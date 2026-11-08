"""Archive the newly verified sources/notices without replacing existing b3 ZIPs."""
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'docs/DEPENDENCY_SOURCES.json').read_text(encoding='utf-8'))
    target = root / 'release/SeestarStudio-2.3.0b3-compliance-sources-review.zip'
    if target.exists():
        raise FileExistsError('Review source bundle exists; choose a new name instead of overwriting')
    sources = {}
    for row in manifest['sources']:
        if row.get('status') != 'downloaded':
            continue
        name = row['file']
        if Path(name).name != name:
            raise ValueError('Unsafe source filename')
        path = root / 'third_party_sources' / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row['sha256']:
            raise ValueError('Source hash mismatch')
        sources[name] = path
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_STORED) as archive:
        for name, path in sorted(sources.items()):
            archive.write(path, 'archives/' + name)
        for folder in ('docs', 'third_party_licenses'):
            for path in (root / folder).rglob('*'):
                if path.is_file() and not path.is_symlink() and path.suffix.lower() in {'.md', '.txt', '.json'}:
                    archive.write(path, path.relative_to(root).as_posix())
        for name in ('LICENSING.md', 'THIRD_PARTY_NOTICES.md', 'LICENSE', 'BUILDING.md'):
            archive.write(root / name, name)
        for name in ('collect_release_provenance.py', 'resolve_native_sources.py', 'controlled_zlib_build.py',
                     'verify_publisher_wheels.py', 'collect_package_sboms.py', 'package_source_supplement.py'):
            archive.write(root / 'tools' / name, 'tools/' + name)
        archive.writestr('README.txt',
            'Additional original sources, recipes, supplier SBOMs, notices and legal-review material.\n'
            'Relates to the preserved b3 candidate; this is not a complete independently proven\n'
            'Corresponding Source certification or public binary release approval.\n'
            'Original upstream source archives may contain PUBLIC upstream test keys/certificates;\n'
            'these are not user/ZWO authentication material and are not runtime build inputs.\n'
            'No user APK, private key, profile, photograph, Windows SDK/tool binary or wheel reference is included.\n'
            'General developer tools and system-library issues are documented separately.\n')
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError('Review archive integrity failed')
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    report = {'file': target.name, 'bytes': target.stat().st_size, 'sha256': digest,
              'source_archives': len(sources), 'public_release_authorized': False,
              'complete_corresponding_source_verified': False}
    (root / 'reports/compliance-followup/source-supplement.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
