"""Bundle only hash-verified upstream archives listed in the source manifest."""
import hashlib
import json
from pathlib import Path
import zipfile
from seestar_studio import __version__


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = root / 'docs/DEPENDENCY_SOURCES.json'
    records = json.loads(manifest.read_text(encoding='utf-8'))['sources']
    archives = []
    for record in records:
        if record.get('status') != 'downloaded':
            continue
        name = record['file']
        if Path(name).name != name:
            raise ValueError('Unexpected source archive path')
        path = root / 'third_party_sources' / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Source checksum mismatch: ' + name)
        archives.append(path)
    output = root / 'release' / f'SeestarStudio-{__version__}-upstream-sources.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_STORED) as bundle:
        for path in archives:
            bundle.write(path, 'archives/' + path.name)
        for name in ['docs/DEPENDENCY_SOURCES.json', 'docs/DEPENDENCIES.md',
                     'docs/QT_ATTRIBUTIONS.json', 'LICENSING.md', 'THIRD_PARTY_NOTICES.md',
                     'BUILDING.md', 'tools/fetch_dependency_sources.py',
                     'tools/package_dependency_sources.py']:
            bundle.write(root / name, name)
        for path in (root / 'third_party_licenses').rglob('*'):
            if path.is_file():
                bundle.write(path, path.relative_to(root).as_posix())
        bundle.writestr('README.txt',
            'Local beta review material; not authorized for distribution.\n'
            'These are unmodified upstream sources verified against the manifest.\n'
            'They do NOT prove complete Corresponding Source for all native binaries.\n'
            'Exact binary/build/patch/static dependency mapping remains open.\n'
            'See LICENSING.md before any redistribution.\n')
    with zipfile.ZipFile(output) as bundle:
        assert bundle.testzip() is None
    print(f'Verified upstream archives: {len(archives)}; bundle bytes: {output.stat().st_size}')


if __name__ == '__main__':
    main()
