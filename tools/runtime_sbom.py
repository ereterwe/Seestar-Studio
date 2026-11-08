"""Build a file-complete CycloneDX inventory from the selected release audit.

Unknown embedded linkage and licence conclusions remain explicit. No network.
"""
import argparse
import hashlib
import json
from pathlib import Path
import uuid


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def create(target, audit):
    components = []
    root = Path(__file__).resolve().parents[1]
    native = {x['file']: x for x in audit['native_files']}
    runtime = {name: data for name, data in audit['installed_packages'].items()
               if data['scope'].startswith(('runtime presence', 'ambiguous'))}
    for name, data in sorted(runtime.items()):
        components.append({'type': 'library', 'bom-ref': 'package:' + name,
            'name': name, 'version': data['version'],
            'properties': [{'name': 'telescope-desk:evidence', 'value': data['scope']},
                {'name': 'telescope-desk:declared-license', 'value': data['license']},
                {'name': 'telescope-desk:legal-clearance', 'value': 'not established'}]})
    # Include supplier-declared embedded Pillow components only for extensions
    # actually shipped. This intentionally excludes the removed AVIF/font roots.
    from tools.resolve_native_sources import pillow_components
    extensions = {'PIL.' + p.name.split('.')[0] for p in (target / '_internal/PIL').glob('*.pyd')}
    if extensions:
        supplier = json.loads((root / 'docs/provenance/Pillow/pillow-13.0.0.cdx.json').read_text(encoding='utf-8'))
        for c in pillow_components(supplier, extensions, ['pkg:generic/libimagequant', 'pkg:generic/libxcb']):
            row = {k: c[k] for k in ('name', 'version', 'licenses', 'purl', 'externalReferences') if k in c}
            row.update({'type': 'library', 'bom-ref': 'embedded:Pillow:' + c['bom-ref'],
                'properties': [{'name': 'telescope-desk:evidence', 'value':
                    'Publisher SBOM dependency closure scoped to shipped extension roots; disabled libimagequant/xcb excluded based on matched publisher binaries. Exact platform-static linkage remains OPEN.'}]})
            components.append(row)
    if any('cryptography' in n and n.endswith('_rust.pyd') for n in native):
        supplier = json.loads((root / 'docs/provenance/cryptography/sbom.json').read_text(encoding='utf-8'))
        for c in supplier['components']:
            row = {k: c[k] for k in ('name', 'version', 'licenses', 'purl', 'externalReferences') if k in c}
            row.update({'type': 'library', 'bom-ref': 'embedded:cryptography:' + c['name'],
                'properties': [{'name': 'telescope-desk:evidence', 'value': 'Publisher OpenSSL SBOM, runtime version corroborated in retained baseline.'}]})
            components.append(row)
    for path in sorted(target.rglob('*')):
        if not path.is_file():
            continue
        name = path.relative_to(target).as_posix()
        props = [{'name': 'telescope-desk:path', 'value': name}]
        if name in native:
            row = native[name]
            props.append({'name': 'telescope-desk:native-evidence', 'value': json.dumps({
                k: row.get(k) for k in ('origin_matches', 'imports', 'version_resource', 'source_candidates')})})
        components.append({'type': 'file', 'bom-ref': 'file:' + name, 'name': name,
            'hashes': [{'alg': 'SHA-256', 'content': digest(path)}], 'properties': props})
    # Publisher SBOMs are retained separately: indiscriminate merging would claim
    # removed AVIF and all-platform Rust optional libraries as active Windows code.
    return {'bomFormat': 'CycloneDX', 'specVersion': '1.6', 'version': 1,
        'serialNumber': 'urn:uuid:' + str(uuid.uuid4()),
        'metadata': {'component': {'type': 'application', 'bom-ref': 'application',
            'name': 'Telescope Desk', 'version': audit['artifact_version'],
            'licenses': [{'license': {'id': 'GPL-3.0-only'}}]},
            'properties': [{'name': 'telescope-desk:build-source', 'value': json.dumps(audit.get('build_info', {}))},
                {'name': 'telescope-desk:scope', 'value':
                'Complete selected payload file inventory; package runtime presence inferred from native hashes and frozen Python ownership. Exact embedded static linkage and ambiguous Python ownership remain OPEN. Supplier evidence is in docs/provenance.'}]},
        'components': components,
        'compositions': [{'aggregate': 'incomplete', 'assemblies': ['application']}],
        'dependencies': [{'ref': 'application', 'dependsOn': ['package:' + n for n in sorted(runtime)]}]}


def verify(target, bom):
    files = {c['name']: c for c in bom['components'] if c['type'] == 'file'}
    actual = {p.relative_to(target).as_posix(): p for p in target.rglob('*') if p.is_file()}
    missing = sorted(actual.keys() - files.keys())
    extra = sorted(files.keys() - actual.keys())
    changed = sorted(n for n in actual.keys() & files.keys()
                     if files[n]['hashes'][0]['content'] != digest(actual[n]))
    build = target / 'build-info.json'
    version_mismatch = (build.is_file() and json.loads(build.read_text(encoding='utf-8'))['version']
                        != bom['metadata']['component']['version'])
    return {'files': len(actual), 'undocumented': missing, 'absent': extra,
            'hash_mismatches': changed, 'version_mismatch': version_mismatch,
            'payload_coverage_pass': not (missing or extra or changed or version_mismatch),
            'embedded_component_completeness': 'OPEN', 'legal_clearance': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    if a.output.resolve().is_relative_to(a.target.resolve()):
        p.error('SBOM must be outside payload to avoid self-hashing')
    if a.verify:
        bom = json.loads(a.output.read_text(encoding='utf-8'))
    else:
        bom = create(a.target, json.loads(a.audit.read_text(encoding='utf-8')))
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(bom, indent=2), encoding='utf-8')
    report = verify(a.target, bom)
    a.output.with_suffix('.verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
    return 0 if report['payload_coverage_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
