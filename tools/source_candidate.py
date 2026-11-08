"""Assemble known corresponding-source candidates; unresolved inputs stay OPEN."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    sources = json.loads((root / 'docs/DEPENDENCY_SOURCES.json').read_text(encoding='utf-8'))['sources']
    inputs = {row['file']: row for row in sources if row.get('status') == 'downloaded'}
    for name, row in inputs.items():
        if Path(name).name != name:
            raise ValueError('Unsafe archive name')
        with (root / 'third_party_sources' / name).open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != row['sha256']:
                raise ValueError('Source archive mismatch')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.output, 'x', zipfile.ZIP_STORED) as archive:
        archive.write(a.target / 'TelescopeDesk-source.zip', 'TelescopeDesk-source.zip')
        archive.write(a.target / 'build-info.json', 'build-info.json')
        archive.write(root / 'docs/DEPENDENCY_SOURCES.json', 'DEPENDENCY_SOURCES.json')
        for name in sorted(inputs):
            archive.write(root / 'third_party_sources' / name, 'upstream/' + name)
        archive.writestr('READ-ME-FIRST.txt',
            'LOCAL SOURCE CANDIDATE, NOT A CLEARED PUBLIC RELEASE.\n'
            'Application sources match the selected build; original source archives are hash-checked.\n'
            'Exact native patches/static linkage and legal adequacy remain OPEN; see LICENSING.md\n'
            'inside the application source archive. This filename is not a completeness certification.\n'
            'Some sources are broader than the reduced payload. Original public upstream test key\n'
            'fixtures may be included in unchanged upstream archives; no user or ZWO key/APK is supplied.\n')
    with zipfile.ZipFile(a.output) as archive:
        assert archive.testzip() is None
    print('Source candidate archives:', len(inputs), 'completeness: OPEN')


if __name__ == '__main__':
    main()
