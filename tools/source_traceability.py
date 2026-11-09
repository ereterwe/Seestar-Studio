"""Bind actual native files and scoped embedded Pillow components to source evidence."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
from tools.release_compliance import owner_index, source_candidates
from tools.resolve_native_sources import pillow_components, recipe


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_openjpeg_patch(root, supplier, sources):
    """Check the original supplier patch against the preserved upstream source."""
    component = next(c for c in supplier['components'] if c['name'] == 'OpenJPEG')
    patch = base64.b64decode(component['pedigree']['patches'][0]['diff']['text']['content'], validate=True)
    source = next(s for s in sources if s['component'].lower() == 'openjpeg')
    relative = 'src/lib/openjp2/j2k.c'
    # Never trust patch or tar paths to select filesystem destinations.
    headers = [line for line in patch.decode('utf-8').splitlines() if line.startswith(('--- ', '+++ '))]
    if headers != ['--- ' + relative, '+++ ' + relative]:
        raise ValueError('Unexpected OpenJPEG patch paths')
    with tarfile.open(root / 'third_party_sources' / source['file']) as archive:
        member = next(m for m in archive.getmembers() if m.isfile() and m.name.endswith('/' + relative))
        original = archive.extractfile(member).read()
    with tempfile.TemporaryDirectory(prefix='telescope-openjpeg-source-') as directory:
        folder = Path(directory)
        target = folder / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(original)
        patchfile = folder / 'supplier.patch'
        patchfile.write_bytes(patch)
        subprocess.run(['git', 'apply', '-p0', '--check', str(patchfile)], cwd=folder, check=True, capture_output=True)
        subprocess.run(['git', 'apply', '-p0', str(patchfile)], cwd=folder, check=True, capture_output=True)
        updated = target.read_bytes()
    return {'status': 'PASS', 'source_archive': source['file'], 'source_member': member.name,
            'patch_sha256': hashlib.sha256(patch).hexdigest(),
            'original_sha256': hashlib.sha256(original).hexdigest(),
            'patched_sha256': hashlib.sha256(updated).hexdigest(),
            'scope': 'Patch applies to upstream source; not a rebuild or proof of binary linkage.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = json.loads((root / 'docs/DEPENDENCY_SOURCES.json').read_text(encoding='utf-8'))['sources']
    sources = [s for s in sources if s.get('status') == 'downloaded']
    for source in sources:
        assert Path(source['file']).name == source['file']
        assert sha(root / 'third_party_sources' / source['file']) == source['sha256']
    owners, packages = owner_index()
    records = []
    for path in sorted(args.target.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.dll', '.pyd', '.exe'}:
            continue
        relative = path.relative_to(args.target).as_posix()
        digest = sha(path)
        origin = owners.get(digest, [])
        candidates = source_candidates(origin, sources, relative if '/plugins/' in relative else path.name)
        status = 'source_candidates_identified' if candidates else 'OPEN'
        if path.name == 'TelescopeDesk.exe':
            status = 'own_application_and_pyinstaller_bootloader'
            candidates = [s for s in sources if s['component'].lower() == 'pyinstaller']
        if path.name.lower().startswith(('msvcp', 'vcruntime', 'concrt')):
            status = 'proprietary_runtime_redistribution_terms_review'
            candidates = []
        records.append({'file': relative, 'sha256': digest, 'origin_matches': origin,
            'source_status': status, 'sources': candidates,
            'publisher_build_correspondence': 'OPEN unless individually established in accompanying evidence',
            'license_metadata': {o['package']: packages[o['package']]['license'] for o in origin if o['package'] in packages}})
    supplier = json.loads((root / 'docs/provenance/Pillow/pillow-13.0.0.cdx.json').read_text(encoding='utf-8'))
    extensions = {'PIL.' + p.name.split('.')[0] for p in (args.target / '_internal/PIL').glob('*.pyd')}
    scoped = pillow_components(supplier, extensions, ['pkg:generic/libimagequant', 'pkg:generic/libxcb'])
    aliases = {'libjpeg / libjpeg-turbo': 'libjpeg-turbo', 'libtiff': 'libtiff',
               'OpenJPEG': 'openjpeg', 'zlib': 'zlib-ng', 'PIL._imaging': 'Pillow-build-repository'}
    embedded = []
    for component in scoped:
        name = aliases.get(component['name'], component['name'])
        matched = [s for s in sources if s['component'].lower() == name.lower()]
        # Some source records use upstream shorthand names.
        if not matched and component['name'] == 'libtiff':
            matched = [s for s in sources if s['file'].startswith('tiff-')]
        patches = []
        for patch in component.get('pedigree', {}).get('patches', []):
            data = patch.get('diff', {}).get('text', {})
            if data.get('encoding') == 'base64':
                content = base64.b64decode(data['content'], validate=True)
                patches.append({'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content),
                                'location': 'Original supplier SBOM pedigree.patches.diff.text'})
        embedded.append({'name': component['name'], 'version': component.get('version'),
            'sources': matched, 'patches': patches, 'licenses': component.get('licenses', []),
            'evidence': 'Supplier-declared dependency closure of retained extension; feature/link details still require build evidence'})
    report = {'target': args.target.name, 'native_files': records, 'pillow_extensions': sorted(extensions),
        'pillow_embedded': embedded, 'verified_source_archives': len(sources),
        'pillow_build_recipes': [recipe('Pillow-git-13.0.0.tar.gz', suffix) for suffix in
                                 ('/winbuild/build_prepare.py', '/.github/dependencies.json')],
        'openjpeg_patch_check': verify_openjpeg_patch(root, supplier, sources),
        'review_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'limitations': ['Candidate source mapping is distinct from exact producing-build proof.',
            'Original OpenJPEG SBOM ancestor has a libtiff name typo; OpenJPEG purl/version/patch identify the intended source. Original SBOM is preserved.',
            'Remaining embedded dependency/link closure, Qt/Mesa patches and Microsoft rights remain explicitly OPEN.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print({'native_files': len(records), 'pillow_components': len(embedded),
           'unmapped_native_files': [r['file'] for r in records if r['source_status'] == 'OPEN'],
           'unmapped_pillow_components': [r['name'] for r in embedded if not r['sources']]})


if __name__ == '__main__':
    main()
