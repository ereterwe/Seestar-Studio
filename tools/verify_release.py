"""Local artifact audit; reports counts/paths, never secret contents."""
import io
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile
from telescope_desk import __version__


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portable',type=Path,default=Path('release') / f'TelescopeDesk-{__version__}-win64.zip')
    parser.add_argument('--output',type=Path,default=Path('reports/release-audit.json'))
    args=parser.parse_args(argv)
    path = args.portable
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        assert archive.testzip() is None, 'Damaged release ZIP'
        forbidden = [name for name in names if name.lower().endswith(('.key', '.apk', '.xapk', '.pfx', '.p12', '.sqlite3', '.sqlite', '.db', '.log'))
                     or name.lower().endswith('.pem') and not name.replace('\\', '/').endswith('/certifi/cacert.pem')]
        assert not forbidden, 'Forbidden runtime data present: ' + ', '.join(forbidden)
        assert any(n.endswith('/TelescopeDesk.exe') for n in names)
        assert any(n.endswith('/catalog_data/NGC.csv') for n in names)
        assert any(n.endswith('/catalog_data/CC-BY-SA-4.0.txt') for n in names)
        assert any(n.endswith('/translations/messages.json') for n in names)
        assert any(n.endswith('/ffmpegmediaplugin.dll') for n in names)
        assert any(n.endswith('/avcodec-63.dll') for n in names)
        assert any(n.endswith('/TelescopeDesk.ico') for n in names)
        assert any('winrt/_winrt_windows_devices_geolocation' in n.replace('\\','/') and n.endswith('.pyd') for n in names)
        assert any(n.endswith('/build-info.json') for n in names)
        source_name = next(n for n in names if n.endswith('/TelescopeDesk-source.zip'))
        with zipfile.ZipFile(io.BytesIO(archive.read(source_name))) as sources:
            source_names = sources.namelist()
            assert sources.testzip() is None
            assert 'telescope_desk/catalog_data/provenance.json' in source_names
            assert 'telescope_desk/translations/messages.json' in source_names
            assert not any('/reports/' in n or n.startswith(('reports/', 'backups/', '.venv/')) for n in source_names)
            assert not any(n.lower().endswith(('.pem', '.key', '.apk', '.xapk', '.sqlite3', '.db', '.png', '.jpg'))
                           and n != 'telescope_desk/assets/TelescopeDesk.png' for n in source_names)
            assert 'telescope_desk/assets/TelescopeDesk.svg' in source_names
            assert 'telescope_desk/build_info.json' in source_names
            build_info=json.loads(sources.read('telescope_desk/build_info.json'))
            assert build_info['version']==__version__
            digest=hashlib.sha256()
            application_names=sorted((Path(n) for n in source_names if n.startswith('telescope_desk/') and not n.endswith('/build_info.json')))
            for name in application_names:
                digest.update(name.as_posix().encode());digest.update(sources.read(name.as_posix()))
            assert digest.hexdigest()==build_info['source_sha256'], 'Source archive differs from compiled build input'
            # Catch an actual multiline private key, not extraction source code
            # that merely contains a BEGIN marker as a quoted literal.
            pattern = re.compile(rb'-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{200,}')
            for name in source_names:
                assert not pattern.search(sources.read(name)), 'Private key material in ' + name
        report = {'version': __version__, 'zip_bytes': path.stat().st_size,
                  'runtime_files': len(names), 'source_files': len(source_names),
                  'license_files': sum('/licenses/' in n for n in names),
                  'forbidden_files': len(forbidden), 'zip_integrity': 'passed',
                  'scope': 'current local artifacts only; not a full legal/security/history audit'}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
