"""Local source/recipe/SBOM evidence. No discovery, device RPC or key access."""
from importlib import metadata
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/compliance-followup'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pillow_components(sbom, shipped, disabled=()):
    """Scope generic supplier metadata to actual extension roots and features."""
    components = {c['bom-ref']: c for c in sbom['components']}
    edges = {d['ref']: d.get('dependsOn', []) for d in sbom.get('dependencies', [])}
    todo = [ref for ref, c in components.items() if c.get('name') in shipped]
    disabled = set(disabled)
    seen = set()
    while todo:
        ref = todo.pop()
        if ref in seen or ref in disabled:
            continue
        seen.add(ref)
        todo.extend(edges.get(ref, []))
    return [components[ref] for ref in sorted(seen) if ref in components]


def recipe(archive, suffix):
    path = ROOT / 'third_party_sources' / archive
    with tarfile.open(path) as source:
        member = next(m for m in source.getmembers() if m.isfile() and m.name.endswith(suffix))
        data = source.extractfile(member).read()
        return {'archive': archive, 'member': member.name, 'sha256': digest(data),
                'git_commit': source.pax_headers.get('comment'), 'text': data.decode('utf-8')}


def compare_pe_images(one, two):
    """Separate signed-file identity from code/data section identity."""
    import pefile
    with pefile.PE(data=one) as a, pefile.PE(data=two) as b:
        sections_a = [(s.Name.hex(), digest(s.get_data())) for s in a.sections]
        sections_b = [(s.Name.hex(), digest(s.get_data())) for s in b.sections]
        return {'same_file': one == two, 'same_pe_sections': sections_a == sections_b,
                'one_sha256': digest(one), 'two_sha256': digest(two),
                'section_count': len(sections_a),
                'note': 'Matching sections do not prove identical certificates or publisher source patches.'}


def main():
    OUT.mkdir(exist_ok=True, parents=True)
    manifest = json.loads((ROOT / 'docs/DEPENDENCY_SOURCES.json').read_text(encoding='utf-8'))
    sources = []
    for record in manifest['sources']:
        if record.get('status') != 'downloaded':
            continue
        path = ROOT / 'third_party_sources' / record['file']
        if Path(record['file']).name != record['file'] or not path.is_file():
            raise ValueError('Missing/unsafe source archive')
        if digest(path.read_bytes()) != record['sha256']:
            raise ValueError('Source archive hash mismatch')
        sources.append({k: record[k] for k in ('component', 'version', 'file', 'sha256', 'url')})
    recipes = [recipe(*args) for args in [
        ('qt-supermodule-6.12.0.tar.gz', '/coin/provisioning/common/windows/install-ffmpeg.ps1'),
        ('qt-supermodule-6.12.0.tar.gz', '/coin/provisioning/common/windows/mesa_llvmpipe.ps1'),
        ('qt-supermodule-6.12.0.tar.gz', '/coin/provisioning/common/windows/zlib-helpers.ps1'),
        ('qt-supermodule-6.12.0.tar.gz', '/coin/provisioning/common/windows/zlib.ps1'),
        ('qt-supermodule-6.12.0.tar.gz', '/coin/provisioning/common/shared/ffmpeg_config_options.txt'),
        ('openblas-libs-0.3.34.106.0.tar.gz', '/openblas_commit.txt'),
        ('openblas-libs-0.3.34.106.0.tar.gz', '/tools/build_steps_windows.sh'),
        ('openblas-libs-0.3.34.106.0.tar.gz', '/patches-windows/openblas-make-libs.patch'),
        ('Pillow-git-13.0.0.tar.gz', '/winbuild/build_prepare.py'),
        ('Pillow-git-13.0.0.tar.gz', '/.github/dependencies.json'),
        ('Python-3.12.10.tar.xz', '/PCbuild/python.props'),
        ('Python-3.12.10.tar.xz', '/PCbuild/get_externals.bat'),
        ('cryptography-git-50.0.2.tar.gz', '/.github/actions/windows-wheel/action.yml'),
    ]]
    recipe_dir = OUT / 'recipes'
    recipe_dir.mkdir(exist_ok=True)
    for row in recipes:
        name = re.sub('[^a-zA-Z0-9._-]', '_', row['member'])
        (recipe_dir / name).write_text(row['text'], encoding='utf-8')
        row['local_evidence'] = 'recipes/' + name
        del row['text']
    # These are supplier metadata and are explicitly kept distinct from link proof.
    summaries = []
    for name in ('cryptography', 'Pillow'):
        dist = metadata.distribution(name)
        for file in dist.files or []:
            relative = str(file).replace('\\', '/')
            if '.dist-info/sboms/' not in relative:
                continue
            data = Path(dist.locate_file(file)).read_bytes()
            bom = json.loads(data)
            summaries.append({'package': name, 'version': dist.version,
                              'file': relative, 'sha256': digest(data),
                              'components': [{k: c.get(k) for k in ('name', 'version', 'purl', 'licenses', 'externalReferences')}
                                             for c in bom.get('components', [])],
                              'scope': 'Supplier SBOM; may include build/optional/all-target components'})
    payload = ROOT / 'dist/2.3.0b3/TelescopeDesk'
    extensions = {'PIL.' + p.name.split('.')[0] for p in (payload / '_internal/PIL').glob('*.pyd')}
    from PIL import _avif, features
    disabled = []
    if not features.check_feature('libimagequant'):
        disabled.append('pkg:generic/libimagequant')
    if not features.check_feature('xcb'):
        disabled.append('pkg:generic/libxcb')
    dist = metadata.distribution('Pillow')
    bom = json.loads((Path(dist.locate_file('pillow-13.0.0.dist-info/sboms/pillow-13.0.0.cdx.json'))).read_text(encoding='utf-8'))
    pillow = {'shipped_extensions': sorted(extensions), 'disabled_feature_dependencies': disabled,
              'scoped_supplier_components': pillow_components(bom, extensions, disabled),
              'avif_codecs': _avif.codec_versions(),
              'note': 'Runtime feature probes use installed extensions already hash-matched to b3. Generic SBOM edges are not exact per-platform linkage proof.'}
    mesa_archive = OUT / 'qt-mesa-11.2.2-x64.7z'
    seven_zip = shutil.which('7z') or str(Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / '7-Zip/7z.exe')
    if Path(seven_zip).is_file():
        command = [seven_zip, 'x', '-so', str(mesa_archive), 'opengl32sw.dll']
    else:
        command = ['tar', '-xOf', str(mesa_archive), 'opengl32sw.dll']
    extracted = subprocess.run(command, capture_output=True, check=True).stdout
    mesa = compare_pe_images(extracted, (payload / '_internal/PySide6/opengl32sw.dll').read_bytes())
    mesa.update({'reference_archive': mesa_archive.name,
                 'qt_recipe_sha1_matches': hashlib.sha1(mesa_archive.read_bytes()).hexdigest() == '58f948746696b17a594b2f542e87b0e831b28dc3',
                 'identified_sources': ['Mesa 11.2.2', 'LLVM 3.6.2'],
                 'source_patch_correspondence': 'OPEN; do not infer exact Qt patches from matching version/sections'})
    # Qt's recipe supplies this digest for its release source input.
    ffmpeg = next((r for r in manifest['sources'] if r['component'] == 'FFmpeg-official-release' and r.get('status') == 'downloaded'), None)
    ffmpeg_proof = {'release': '9.0.1', 'recipe_located': True, 'qt_source_sha1_matches': False}
    if ffmpeg:
        ffmpeg_proof['qt_source_sha1_matches'] = hashlib.sha1((ROOT / 'third_party_sources' / ffmpeg['file']).read_bytes()).hexdigest() == '89c318905212e6b67e10e42ab10ab8007e0aefda'
        ffmpeg_proof['source_record'] = ffmpeg
    result = {'scope': 'Unmodified b3 binaries and local supplementary sources; no release approval',
              'verified_source_archive_count': len(sources), 'source_archives': sources,
              'recipes': recipes, 'supplier_sboms': summaries, 'pillow': pillow,
              'mesa': mesa, 'ffmpeg': ffmpeg_proof,
              'complete_native_source_build_correspondence': False,
              'open_items': ['Exact Qt wheel build/patch confirmation', 'Mesa/LLVM publisher patch/build correspondence',
                             'Native rebuild verification and static compiler-runtime closure',
                             'Microsoft redistribution conditions and applicable legal patent/ZWO review']}
    (OUT / 'native-resolution.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'sources': len(sources), 'recipes': len(recipes), 'sboms': len(summaries),
                      'mesa_same_sections': mesa['same_pe_sections'], 'mesa_same_file': mesa['same_file'],
                      'ffmpeg_recipe_source_digest_matches': ffmpeg_proof['qt_source_sha1_matches']}))


if __name__ == '__main__':
    main()
