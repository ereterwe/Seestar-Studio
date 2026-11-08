"""Explicit developer-only public evidence collection, never executed by the app.

Downloads sources/recipes only. Never downloads APKs, reads keys, installs tools,
or executes downloaded code. Publisher hashes and source/binary proof stay distinct.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import ssl
import tarfile
import tomllib
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
import certifi

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'third_party_sources'
EVIDENCE = ROOT / 'reports/compliance-followup'
TLS = ssl.create_default_context()
TLS.load_verify_locations(cafile=certifi.where())


def get(url, limit=8 * 1024**2):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'TelescopeDesk-SourceAudit'}), timeout=35, context=TLS) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Evidence download size limit')
        return data


def download(component, version, url, filename, expected=None, kind='source'):
    if Path(filename).name != filename:
        raise ValueError('Unsafe output name')
    directory = DEST if kind == 'source' else EVIDENCE
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    row = {'component': component, 'version': version, 'url': url, 'file': filename, 'kind': kind}
    try:
        if not path.exists():
            part = path.with_suffix(path.suffix + '.part')
            with urllib.request.urlopen(url, timeout=40, context=TLS) as response, part.open('wb') as stream:
                count = 0
                while block := response.read(1024**2):
                    count += len(block)
                    if count > 512 * 1024**2:
                        raise ValueError('Source size limit')
                    stream.write(block)
            part.replace(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        row.update(sha256=digest, bytes=path.stat().st_size,
                   publisher_digest_verified=bool(expected), status='downloaded')
        if expected and expected != digest:
            row['status'] = 'hash mismatch'
        if kind == 'source':
            row['binary_correspondence'] = 'OPEN; source availability does not prove wheel build patches/features'
    except Exception as exc:
        row.update(status='unavailable', error_type=type(exc).__name__)
        if hasattr(exc, 'code'):
            row['http_status'] = exc.code
        reason = getattr(exc, 'reason', None)
        if isinstance(reason, ssl.SSLCertVerificationError):
            row.update(tls_verification_failed=True, tls_verify_code=reason.verify_code)
    return row


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    records = []
    # Official immutable tags/versions. A digest calculated here is not described
    # as publisher-verified unless independently supplied by that publisher.
    tasks = [
        ('CPython', '3.12.10', 'https://www.python.org/ftp/python/3.12.10/Python-3.12.10.tar.xz', 'Python-3.12.10.tar.xz'),
        ('zlib', '1.3.1', 'https://zlib.net/fossils/zlib-1.3.1.tar.gz', 'zlib-1.3.1.tar.gz'),
        ('Mesa', '11.2.2', 'https://archive.mesa3d.org/older-versions/11.x/11.2.2/mesa-11.2.2.tar.xz', 'mesa-11.2.2.tar.xz'),
        ('OpenSSL', '3.0.16', 'https://github.com/openssl/openssl/releases/download/openssl-3.0.16/openssl-3.0.16.tar.gz', 'openssl-3.0.16.tar.gz'),
        ('OpenSSL', '4.0.3', 'https://github.com/openssl/openssl/releases/download/openssl-4.0.3/openssl-4.0.3.tar.gz', 'openssl-4.0.3.tar.gz'),
        ('SQLite', '3.49.1', 'https://www.sqlite.org/2025/sqlite-src-3490100.zip', 'sqlite-src-3490100.zip'),
        ('Qt-supermodule', '6.12.0', 'https://codeload.github.com/qt/qt5/tar.gz/refs/tags/v6.12.0', 'qt-supermodule-6.12.0.tar.gz'),
        ('Pillow-build-repository', '13.0.0', 'https://codeload.github.com/python-pillow/Pillow/tar.gz/refs/tags/13.0.0', 'Pillow-git-13.0.0.tar.gz'),
        ('cryptography-build-repository', '50.0.2', 'https://codeload.github.com/pyca/cryptography/tar.gz/refs/tags/50.0.2', 'cryptography-git-50.0.2.tar.gz'),
        ('scipy-openblas-build', '0.3.34.106.0', 'https://codeload.github.com/MacPython/openblas-libs/tar.gz/refs/tags/v0.3.34.106.0', 'openblas-libs-0.3.34.106.0.tar.gz'),
        ('Inno-Setup', '7.1.1', 'https://codeload.github.com/jrsoftware/issrc/tar.gz/refs/tags/is-7_1_1', 'innosetup-7.1.1-src.tar.gz'),
        ('FFmpeg-official-release', '9.0.1', 'https://ffmpeg.org/releases/ffmpeg-9.0.1.tar.gz', 'ffmpeg-9.0.1-official.tar.gz'),
        ('Mesa', '11.2.2', 'https://archive.mesa3d.org/older-versions/11.x/11.2.2/mesa-11.2.2.tar.gz', 'mesa-11.2.2.tar.gz'),
        ('libjpeg-turbo', '3.2.0', 'https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/3.2.0/libjpeg-turbo-3.2.0.tar.gz', 'libjpeg-turbo-3.2.0.tar.gz'),
        ('zlib-ng', '2.3.3', 'https://codeload.github.com/zlib-ng/zlib-ng/tar.gz/refs/tags/2.3.3', 'zlib-ng-2.3.3.tar.gz'),
        ('libwebp', '1.6.0', 'https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.6.0.tar.gz', 'libwebp-1.6.0.tar.gz'),
        ('libtiff', '4.7.2', 'https://download.osgeo.org/libtiff/tiff-4.7.2.tar.gz', 'tiff-4.7.2.tar.gz'),
        ('Little-CMS', '2.19.1', 'https://codeload.github.com/mm2/Little-CMS/tar.gz/refs/tags/lcms2.19.1', 'lcms2-2.19.1.tar.gz'),
        ('OpenJPEG', '2.5.4', 'https://codeload.github.com/uclouvain/openjpeg/tar.gz/refs/tags/v2.5.4', 'openjpeg-2.5.4.tar.gz'),
        ('libavif', '1.4.2', 'https://codeload.github.com/AOMediaCodec/libavif/tar.gz/refs/tags/v1.4.2', 'libavif-1.4.2.tar.gz'),
        ('FFmpeg-official-release', '9.0.1', 'https://ci-files01-hki.ci.qt.io/input/ffmpeg/ffmpeg-9.0.1.tar.gz', 'ffmpeg-9.0.1-qt-cache.tar.gz'),
    ]
    # CPython's own pinned source branches retain Windows patches/amalgamations.
    for component, release in [('bzip2','1.0.8'), ('xz','5.2.5'), ('libffi','3.4.4'), ('sqlite','3.49.1.0'), ('openssl','3.0.16'), ('zlib','1.3.1')]:
        ref = component + '-' + release
        tasks.append(('CPython-source-deps/' + component, release,
                      'https://codeload.github.com/python/cpython-source-deps/tar.gz/refs/tags/' + ref,
                      'cpython-source-deps-' + ref + '.tar.gz'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        records.extend(pool.map(lambda args: download(*args), tasks))
    # The package publisher supplies the source location for the exact BLAS build.
    try:
        pypi = json.loads(get('https://pypi.org/pypi/scipy-openblas64/0.3.34.106.0/json'))
        (EVIDENCE / 'openblas-pypi.json').write_text(json.dumps(pypi, indent=2), encoding='utf-8')
        for file in pypi['urls']:
            if file['packagetype'] == 'sdist':
                records.append(download('scipy-openblas64', '0.3.34.106.0', file['url'], file['filename'], file['digests']['sha256']))
    except Exception as exc:
        (EVIDENCE / 'openblas-metadata-error.txt').write_text(type(exc).__name__)
    # Vendor the exact registry archives identified by cryptography's Cargo.lock.
    with tarfile.open(DEST / 'cryptography-50.0.2.tar.gz') as archive:
        member = next(m for m in archive.getmembers() if m.name.endswith('/Cargo.lock'))
        packages = tomllib.loads(archive.extractfile(member).read().decode())['package']
    crates = [(f"Rust/{p['name']}", p['version'],
               f"https://static.crates.io/crates/{p['name']}/{p['name']}-{p['version']}.crate",
               f"{p['name']}-{p['version']}.crate", p['checksum'])
              for p in packages if p.get('source', '').startswith('registry+')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        records.extend(pool.map(lambda args: download(*args), crates))
    legal = [
        ('VS-Community-2026-terms', '2026', 'https://visualstudio.microsoft.com/wp-content/uploads/2025/10/Visual_Studio_2026-License-Community_ENU.docx', 'VS-Community-2026.docx'),
        ('VC-Runtime-2022-terms', '2022', 'https://visualstudio.microsoft.com/wp-content/uploads/2021/09/Visual-C-Runtime-2015-2022-License-1.docx', 'VC-Runtime-2022.docx'),
        ('VC-Runtime-2026-terms', '2026', 'https://visualstudio.microsoft.com/wp-content/uploads/2025/10/Visual-C-V14-License-Redistributable_and_Runtime_ENU.docx', 'VC-Runtime-2026.docx'),
    ]
    for args in legal:
        row = download(*args, kind='license-reference')
        records.append(row)
        if row['status'] == 'downloaded':
            with zipfile.ZipFile(EVIDENCE / row['file']) as archive:
                document = ET.fromstring(archive.read('word/document.xml'))
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                lines = [''.join(p.itertext()) for p in document.findall('.//w:p', ns)]
                (EVIDENCE / (Path(row['file']).stem + '.txt')).write_text('\n'.join(lines), encoding='utf-8')
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'records': records,
              'all_native_builds_verified': False, 'note': 'Never equate a successful download with Corresponding Source clearance.'}
    (EVIDENCE / 'download-evidence.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    # Merge source records, retaining all previous evidence and unavailable rows.
    manifest = ROOT / 'docs/DEPENDENCY_SOURCES.json'
    data = json.loads(manifest.read_text(encoding='utf-8'))
    keys = {(r['component'], r['version']) for r in records if r['kind'] == 'source'}
    data['sources'] = [r for r in data['sources'] if (r['component'], r['version']) not in keys]
    # Prefer a successful alternate location over a failed candidate for the same
    # component/version. Keep all attempts in raw download-evidence.json.
    chosen = {}
    for record in records:
        if record['kind'] != 'source':
            continue
        key = (record['component'], record['version'])
        if key not in chosen or record['status'] == 'downloaded':
            chosen[key] = record
    data['sources'] += list(chosen.values())
    manifest.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'downloaded': sum(r['status'] == 'downloaded' for r in records),
                      'unavailable': [r['component'] for r in records if r['status'] != 'downloaded']}))


if __name__ == '__main__':
    main()
