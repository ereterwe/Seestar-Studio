"""Compare frozen native bytes to publisher-hash-verified original PyPI wheels.

Explicit developer tool. Downloads reference wheels but never installs/imports
or executes them. No telescope discovery or authentication files are involved.
"""
from importlib import metadata
import hashlib
import json
from pathlib import Path
import zipfile

from tools.collect_release_provenance import get, download

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/compliance-followup'


def main():
    inventory = json.loads((ROOT / 'docs/compliance/B3_BINARY_SOURCE_MAP.json').read_text(encoding='utf-8'))
    packages = {o['package'] for row in inventory['native_files'] for o in row['origin_matches']
                if o['package'] != 'CPython distribution'}
    records = []
    for name in sorted(packages):
        dist = metadata.distribution(name)
        tag_lines = [line.removeprefix('Tag: ').strip() for line in (dist.read_text('WHEEL') or '').splitlines()
                     if line.startswith('Tag: ')]
        row = {'package': name, 'version': dist.version, 'wheel_tags': tag_lines, 'status': 'OPEN'}
        try:
            release = json.loads(get(f'https://pypi.org/pypi/{name}/{dist.version}/json'))
            matches = [f for f in release['urls'] if f['packagetype'] == 'bdist_wheel'
                       and any(f['filename'].endswith('-' + tag + '.whl') for tag in tag_lines)]
            if len(matches) != 1:
                row['reason'] = 'Exact wheel identity is ambiguous or absent'
            else:
                wheel = matches[0]
                record = download(name, dist.version, wheel['url'], wheel['filename'], wheel['digests']['sha256'], kind='binary-reference')
                row['reference'] = record
                if record['status'] == 'downloaded':
                    with zipfile.ZipFile(OUT / record['file']) as archive:
                        checks = []
                        for native in inventory['native_files']:
                            origins = [o for o in native['origin_matches'] if o['package'] == name]
                            for origin in origins:
                                member = origin['record_path']
                                if member not in archive.namelist():
                                    checks.append({'file': native['file'], 'member': member, 'status': 'OPEN'})
                                else:
                                    valid = hashlib.sha256(archive.read(member)).hexdigest() == native['sha256']
                                    checks.append({'file': native['file'], 'member': member, 'status': 'PASS' if valid else 'BLOCKER'})
                        row['native_files'] = checks
                        sbom_checks = []
                        for file in dist.files or []:
                            member = str(file).replace('\\', '/')
                            if '.dist-info/sboms/' not in member:
                                continue
                            if member not in archive.namelist():
                                sbom_checks.append({'file': member, 'status': 'OPEN'})
                            else:
                                installed = Path(dist.locate_file(file)).read_bytes()
                                sbom_checks.append({'file': member, 'sha256': hashlib.sha256(installed).hexdigest(),
                                                    'status': 'PASS' if archive.read(member) == installed else 'BLOCKER'})
                        row['supplier_sboms'] = sbom_checks
                        row['status'] = 'PASS' if checks and all(c['status'] == 'PASS' for c in checks) else 'BLOCKER' if any(c['status'] == 'BLOCKER' for c in checks) else 'OPEN'
                        if any(c['status'] != 'PASS' for c in sbom_checks):
                            row['status'] = 'BLOCKER' if any(c['status'] == 'BLOCKER' for c in sbom_checks) else 'OPEN'
        except Exception as exc:
            row['error_type'] = type(exc).__name__
        records.append(row)
        (OUT / 'publisher-wheel-verification.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
        print(name + ': ' + row['status'], flush=True)
    print(json.dumps({'packages': len(records), 'pass': sum(r['status'] == 'PASS' for r in records),
                      'scope': 'Publisher binary identity, not proof of unpublished patches or full native rebuild'}))


if __name__ == '__main__':
    main()
