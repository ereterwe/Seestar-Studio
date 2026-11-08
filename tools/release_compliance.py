"""Read-only evidence audit of an explicitly selected onedir distribution.

Does not start the application, import SeestarPy, download, publish, or read user
authentication directories. PASS applies only to the named technical check,
never to legal clearance. Exit codes: 0 PASS, 1 OPEN, 2 BLOCKER.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NATIVE = {'.dll', '.pyd', '.exe'}
PRIVATE = {'.pem', '.key', '.apk', '.xapk', '.p12', '.pfx', '.sqlite', '.sqlite3', '.db', '.log'}
PATTERNS = {
    'private_key_material': re.compile(rb'-----BEGIN (?:RSA |EC |ENCRYPTED |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{200,}'),
    'github_token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})\b'),
    'aws_access_id': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
}
REVIEW_PATTERNS = {
    'personal_path': re.compile(rb'(?i)C:[\\/]+Users[\\/]+(?!Public\b|Default\b|runneradmin\b|<|\{)[a-z][a-z0-9_-]+[\\/]'),
    'device_identifier': re.compile(rb'\bs(?:30|50)(?:pro)?_[0-9a-f]{8}\b'),
    'credential_assignment': re.compile(rb'''(?i)(?:password|api_key|access_token)\s*[=:]\s*["'][^"'\r\n]{8,}["']'''),
}
REQUIRED_DOCS = ['README.md', 'LICENSE', 'LICENSING.md', 'THIRD_PARTY_NOTICES.md',
                 'BUILDING.md', 'INSTALLATION.md', 'COMPATIBILITY.md', 'CHANGELOG.md',
                 'BETA_RELEASE_CHECKLIST.md', 'docs/DEPENDENCIES.md']


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def normalize(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()


def scan_bytes(data: bytes) -> dict:
    # Report categories only, never secret contents or matched context.
    return {'blockers': [k for k, p in PATTERNS.items() if p.search(data)],
            'review': [k for k, p in REVIEW_PATTERNS.items() if p.search(data)]}


def private_name(name: str) -> bool:
    name = name.replace('\\', '/')
    return (PurePosixPath(name).suffix.lower() in PRIVATE
            and not (name == 'certifi/cacert.pem' or name.endswith('/certifi/cacert.pem')))


def scan_zip(data: bytes, depth=0) -> dict:
    """Inspect archive members in memory, never extract arbitrary paths."""
    result = {'members': 0, 'findings': [], 'incomplete': []}
    if depth > 3:
        result['incomplete'].append('nested archive depth limit')
        return result
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) > 30000 or sum(i.file_size for i in infos) > 1024**3:
            result['incomplete'].append('archive inspection size limit')
            return result
        seen = set()
        for item in infos:
            if item.is_dir():
                continue
            name = item.filename.replace('\\', '/')
            result['members'] += 1
            issues = []
            if name in seen or '..' in PurePosixPath(name).parts or name.startswith('/') or ':' in name:
                issues.append('unsafe_or_duplicate_archive_path')
            seen.add(name)
            if private_name(name):
                issues.append('private_file_type')
            if item.file_size > 128 * 1024**2 or item.flag_bits & 1:
                result['incomplete'].append({'member': name, 'reason': 'size limit or encrypted'})
                continue
            content = archive.read(item)  # Includes CRC verification.
            found = scan_bytes(content)
            if issues or found['blockers'] or found['review']:
                result['findings'].append({'member': name, 'blockers': issues + found['blockers'], 'review': found['review']})
            if name.lower().endswith('.zip'):
                nested = scan_zip(content, depth + 1)
                result['members'] += nested['members']
                result['findings'].extend({'container': name, **f} for f in nested['findings'])
                result['incomplete'].extend(nested['incomplete'])
    return result


def owner_index():
    """Use installed wheel RECORD hashes; no package code is imported."""
    by_hash = defaultdict(list)
    packages = {}
    for dist in metadata.distributions():
        name = dist.metadata['Name']
        licenses = []
        for file in dist.files or []:
            rel = str(file).replace('\\', '/')
            if '.dist-info/' in rel and any(k in rel.lower() for k in ('license', 'copying', 'notice')):
                licenses.append(rel)
            if file.hash and file.hash.mode == 'sha256':
                try:
                    digest = base64.urlsafe_b64decode(file.hash.value + '===').hex()
                except (ValueError, TypeError):
                    continue
                by_hash[digest].append({'package': name, 'version': dist.version, 'record_path': rel,
                                        'evidence': 'binary bytes match installed RECORD SHA256'})
        packages[name] = {'version': dist.version,
                         'license': dist.metadata.get('License-Expression') or dist.metadata.get('License') or 'UNKNOWN',
                         'project_urls': dist.metadata.get_all('Project-URL', []),
                         'license_files': licenses}
    # CPython installer files do not have wheel RECORD metadata.
    base = Path(sys.base_prefix)
    for folder in (base, base / 'DLLs'):
        for file in folder.glob('*'):
            if file.is_file() and file.suffix.lower() in NATIVE:
                by_hash[sha(file)].append({'package': 'CPython distribution', 'version': sys.version.split()[0],
                                           'record_path': file.relative_to(base).as_posix(),
                                           'evidence': 'bytes match local base Python; publisher chain OPEN'})
    return by_hash, packages


def inspect_pe(path: Path) -> dict:
    import pefile
    with pefile.PE(str(path), fast_load=True) as pe:
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY[k] for k in (
            'IMAGE_DIRECTORY_ENTRY_IMPORT', 'IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT', 'IMAGE_DIRECTORY_ENTRY_RESOURCE')])
        imports = sorted({i.dll.decode('ascii', 'replace') for attr in ('DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT')
                          for i in getattr(pe, attr, [])})
        strings = {}
        for group in getattr(pe, 'FileInfo', []):
            for info in group:
                for table in getattr(info, 'StringTable', []):
                    for key, value in table.entries.items():
                        if key in (b'FileVersion', b'ProductVersion', b'CompanyName', b'LegalCopyright'):
                            strings[key.decode()] = value.decode('utf-8', 'replace')
        return {'imports': imports, 'version_resource': strings}


def source_candidates(owners, sources, name):
    names = {normalize(o['package']) for o in owners}
    if 'cpython distribution' in names:
        names.add('cpython')
    if 'cryptography' in names:
        names.add('cryptography-build-repository')
        names.update(normalize(s['component']) for s in sources if s['component'].startswith('Rust/'))
    if 'pillow' in names:
        names.add('pillow-build-repository')
    low = name.lower().replace('\\', '/')
    if low.startswith(('avcodec-', 'avformat-', 'avutil-', 'swresample-', 'swscale-')):
        names = {'ffmpeg', 'ffmpeg-official-release'}
    elif 'openblas' in low:
        names = {'openblas', 'scipy-openblas-build'}
    elif low == 'opengl32sw.dll':
        names = {'mesa', 'llvm'}
    elif low.startswith(('pyside', 'shiboken')):
        names = {'pyside-setup'}
    elif low.endswith(('qt6pdf.dll', '/qpdf.dll')):
        names = {'qtwebengine'}  # Separate PDF wheel; not qtbase's source version.
    elif 'virtualkeyboard' in low:
        names = {'qtvirtualkeyboard'}
    elif low.startswith(('qt6qml', 'qt6quick')):
        names = {'qtdeclarative'}
    elif 'multimedia' in low:
        names = {'qtmultimedia'}
    elif 'svg' in low:
        names = {'qtsvg'}
    elif '/imageformats/' in low and low.rsplit('/', 1)[1] in {'qicns.dll', 'qtga.dll', 'qtiff.dll', 'qwbmp.dll', 'qwebp.dll'}:
        names = {'qtimageformats'}
    elif low.startswith('qt6') or '/plugins/' in low:
        names = {'qtbase'}
    return [s for s in sources if normalize(s['component']) in names and s.get('file')]


def git_history(root: Path) -> dict:
    """Scan every reachable blob, commit and annotated tag; no rewrites."""
    objects = subprocess.run(['git', 'rev-list', '--objects', '--all'], cwd=root,
                             check=True, capture_output=True).stdout.splitlines()
    ids = sorted({line.split(b' ', 1)[0] for line in objects})
    stream = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    findings = []
    counts = Counter()
    try:
        for oid in ids:
            stream.stdin.write(oid + b'\n')
            stream.stdin.flush()
            header = stream.stdout.readline().split()
            if len(header) != 3:
                raise ValueError('Unable to read Git object')
            kind, size = header[1].decode(), int(header[2])
            data = stream.stdout.read(size)
            if len(data) != size or stream.stdout.read(1) != b'\n':
                raise ValueError('Truncated Git object')
            counts[kind] += 1
            if kind in ('blob', 'commit', 'tag'):
                found = scan_bytes(data)
                if found['blockers'] or found['review']:
                    findings.append({'object': oid.decode(), 'type': kind, **found})
        forbidden = [hashlib.sha256(line).hexdigest() for line in objects if b' ' in line
                     and private_name(line.split(b' ', 1)[1].decode('utf-8', 'replace'))]
    finally:
        stream.stdin.close()
        stream.stdout.close()
        stream.wait(timeout=10)
    return {'counts': dict(counts), 'findings': findings, 'forbidden_path_fingerprints': forbidden,
            'scope': 'All locally reachable refs, including fetched tags; unreachable objects, remote PR refs and Git LFS payloads not covered.'}


def check_sources(manifest: Path, directory: Path):
    entries = json.loads(manifest.read_text(encoding='utf-8'))['sources']
    checked = []
    for record in entries:
        row = dict(record)
        file = record.get('file')
        if not file:
            row['archive_check'] = 'OPEN'
        elif Path(file).name != file:
            row['archive_check'] = 'BLOCKER'
        elif not (directory / file).is_file():
            row['archive_check'] = 'OPEN'
        else:
            row['archive_check'] = 'PASS' if sha(directory / file) == record.get('sha256') else 'BLOCKER'
        row['binary_correspondence'] = 'OPEN'
        checked.append(row)
    return checked


def current_source_scan(root):
    names = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                           cwd=root, capture_output=True, check=True).stdout.split(b'\0')
    findings, skipped, count = [], [], 0
    for raw in sorted(set(names)):
        if not raw:
            continue
        rel = raw.decode('utf-8', 'replace')
        path = root / rel
        if not path.is_file():
            continue
        if path.is_symlink() or path.stat().st_size > 128 * 1024**2:
            skipped.append(rel)
            continue
        if private_name(rel):
            findings.append({'file': rel, 'blockers': ['private_file_type'], 'review': []})
            continue
        count += 1
        result = scan_bytes(path.read_bytes())
        if result['blockers'] or result['review']:
            findings.append({'file': rel, **result})
    return {'files_scanned': count, 'findings': findings, 'skipped': skipped,
            'scope': 'Tracked and nonignored working files. Ignored personal files and reports are not publication inputs.'}


def audit(target: Path, expected: str, root: Path = ROOT) -> dict:
    checks = []
    def check(name, status, evidence):
        checks.append({'check': name, 'status': status, 'evidence': evidence})
    build = json.loads((target / 'build-info.json').read_text(encoding='utf-8'))
    check('selected_release_version', 'PASS' if build['version'] == expected else 'BLOCKER',
          {'expected': expected, 'actual': build['version']})
    sources = check_sources(root / 'docs/DEPENDENCY_SOURCES.json', root / 'third_party_sources')
    bad = [s['component'] for s in sources if s['archive_check'] == 'BLOCKER']
    verified_sources = sum(s['archive_check'] == 'PASS' for s in sources)
    check('available_source_archive_hashes', 'BLOCKER' if bad else 'PASS' if verified_sources else 'OPEN',
          {'verified': sum(s['archive_check'] == 'PASS' for s in sources), 'mismatches': bad,
           'note': 'Missing archives and binary correspondence are separate OPEN checks.'})
    by_hash, packages = owner_index()
    files, natives, found, zip_reports, skipped_raw = [], [], [], [], []
    runtime_owners = set()
    for path in sorted(target.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(target).as_posix()
        if private_name(rel) or path.is_symlink():
            files.append({'file': rel, 'bytes': path.stat().st_size, 'sha256': None, 'inspection': 'not opened'})
            found.append({'file': rel, 'blockers': ['private_file_type_or_symlink'], 'review': []})
            continue
        digest = sha(path)
        row = {'file': rel, 'bytes': path.stat().st_size, 'sha256': digest}
        matches = by_hash.get(digest, [])
        if matches:
            row['origin_matches'] = matches
        files.append(row)
        if path.stat().st_size <= 128 * 1024**2:
            result = scan_bytes(path.read_bytes())
            if result['blockers'] or result['review']:
                found.append({'file': rel, **result})
        else:
            skipped_raw.append(rel)
        if path.suffix.lower() == '.zip':
            zip_reports.append({'file': rel, **scan_zip(path.read_bytes())})
        if path.suffix.lower() not in NATIVE:
            continue
        owners = by_hash.get(digest, [])
        runtime_owners.update(o['package'] for o in owners)
        info = inspect_pe(path)
        candidates = source_candidates(owners, sources, path.name if '/plugins/' not in rel else rel)
        is_ms = path.name.lower().startswith(('msvcp', 'vcruntime', 'concrt'))
        natives.append({**row, **info, 'origin_matches': owners,
                        'origin_status': 'PASS' if owners else 'OPEN',
                        'source_candidates': candidates,
                        'source_status': 'OPEN',
                        'package_declared_license': [packages[o['package']]['license'] for o in owners if o['package'] in packages],
                        'license': 'Microsoft redistribution terms: review required' if is_ms else
                            'LGPL-2.1-or-later (FFmpeg runtime exports); embedded dependencies separately OPEN' if path.name.lower().startswith(('avcodec-', 'avformat-', 'avutil-', 'swresample-', 'swscale-')) else
                            'GPL-3.0 option; NOT LGPL (Qt Virtual Keyboard)' if 'virtualkeyboard' in rel.lower() else
                            'Per-component license review OPEN; package_declared_license is the owner package metadata, not a license grant for all embedded libraries',
                        'copyright': info['version_resource'].get('LegalCopyright', 'See original package notices; per-file attribution OPEN'),
                        'modifications': 'No byte changes relative to origin match' if owners else 'Not established',
                        'build_information': 'Installed wheel/CPython bytes; upstream compiler, patches and static libraries not thereby proved',
                        'obligations': 'Preserve notices; evaluate exact source/build delivery and library replacement. Microsoft files require separate redistribution authority.',
                        'classification': 'bundled Microsoft runtime (not automatically a System Library)' if is_ms else 'bundled application or third-party native code'})
    check('payload_inventory', 'PASS', {'files': len(files), 'native_files': len(natives), 'hash': 'SHA256 of actual file bytes'})
    unknown = [n['file'] for n in natives if n['origin_status'] != 'PASS']
    check('native_binary_origin', 'OPEN' if unknown else 'PASS', {'unmatched': unknown,
          'limitation': 'RECORD correspondence is local installation provenance, not proof of publisher signing or source build.'})
    check('native_corresponding_source', 'BLOCKER', 'Native source/patch/build/static dependency chain has not been independently reconstructed; source archives alone are insufficient.')
    missing = [p for p in REQUIRED_DOCS if not (target / p).is_file()]
    check('mandatory_document_presence', 'BLOCKER' if missing else 'PASS', missing)
    check('license_and_copyright_coverage', 'OPEN', 'Presence of collected license texts does not establish all embedded component attribution.')
    provenance = target / '_internal/seestar_studio/catalog_data/provenance.json'
    if provenance.is_file():
        catalog = json.loads(provenance.read_text(encoding='utf-8'))
        changed = [name for name, record in catalog['files'].items()
                   if not (provenance.parent / name).is_file() or sha(provenance.parent / name) != record['sha256']]
        check('catalog_snapshot_integrity', 'BLOCKER' if changed else 'PASS', {'changed_or_missing': changed, 'revision': catalog['revision'], 'license': catalog['license']})
    else:
        check('catalog_snapshot_integrity', 'OPEN', 'No catalog provenance manifest found')
    # PYZ compressed entries are scanned after decompression; no modules execute.
    modules = []
    ambiguous_owners = set()
    from PyInstaller.archive.readers import CArchiveReader
    exe = CArchiveReader(str(target / 'SeestarStudio.exe'))
    module_owners = defaultdict(list)
    for dist in metadata.distributions():
        for file in dist.files or []:
            name = str(file).replace('\\', '/')
            if name.endswith('.py') and not name.startswith('../'):
                module = name[:-3].replace('/', '.')
                if module.endswith('.__init__'):
                    module = module[:-9]
                module_owners[module].append(dist.metadata['Name'])
    for entry, desc in exe.toc.items():
        if desc[-1] == 'z':
            pyz = exe.open_embedded_archive(entry)
            for name in sorted(pyz.toc):
                data = pyz.extract(name, raw=True) or b''
                owners = module_owners.get(name, [])
                if len(owners) == 1:
                    runtime_owners.update(owners)
                else:
                    ambiguous_owners.update(owners)
                modules.append({'module': name, 'bytecode_sha256': hashlib.sha256(data).hexdigest(),
                                'candidate_packages': owners, 'source_correspondence': 'OPEN'})
                result = scan_bytes(data)
                if result['blockers'] or result['review']:
                    found.append({'file': 'PYZ:' + name, **result})
        else:
            result = scan_bytes(exe.extract(entry))
            if result['blockers'] or result['review']:
                found.append({'file': 'CArchive:' + entry, **result})
    for name, package in packages.items():
        package['scope'] = ('runtime presence evidenced by native hash or uniquely owned embedded module name' if name in runtime_owners
                            else 'ambiguous shared module ownership; runtime presence not established' if name in ambiguous_owners
                            else 'installed only; runtime presence not established, not automatically a development-only package')
    license_dirs = {normalize(p.name) for p in (target / 'licenses').iterdir() if p.is_dir()}
    absent = [name for name in sorted(runtime_owners) if name in packages
              and packages[name]['license_files'] and normalize(name) not in license_dirs]
    check('runtime_package_notice_directories', 'BLOCKER' if absent else 'PASS',
          {'missing': absent, 'scope': 'Expected package notice directories for packages declaring license files; content and static-library coverage remain separate OPEN checks.'})
    for report in zip_reports:
        found.extend({'container': report['file'], **f} for f in report['findings'])
    check('payload_secret_patterns', 'BLOCKER' if any(f['blockers'] for f in found) else 'OPEN' if found or skipped_raw else 'PASS',
          {'findings': found, 'skipped_raw_files': skipped_raw, 'scope': 'File names, raw bytes, ZIPs and decompressed CArchive/PYZ entries; heuristic, not a complete secret guarantee.'})
    check('archive_scan_completeness', 'OPEN' if any(r['incomplete'] for r in zip_reports) else 'PASS',
          [{'file': r['file'], 'members': r['members'], 'incomplete': r['incomplete']} for r in zip_reports])
    history = git_history(root)
    check('reachable_git_secret_patterns', 'BLOCKER' if history['forbidden_path_fingerprints'] or any(f['blockers'] for f in history['findings'])
          else 'OPEN' if history['findings'] else 'PASS', history)
    current = current_source_scan(root)
    check('current_source_secret_patterns', 'BLOCKER' if any(f['blockers'] for f in current['findings'])
          else 'OPEN' if current['findings'] or current['skipped'] else 'PASS', current)
    check('source_zip_application_hash', *source_hash_check(target, build))
    check('public_release_identity', 'OPEN', 'This offline check does not establish remote release visibility, asset hashes, tester copies or authorization.')
    check('installer_payload', 'OPEN', 'An onedir audit does not prove identity of an installer payload; retain separate extraction/install evidence.')
    check('legal_review', 'OPEN', 'ZWO interoperability, Microsoft redistribution, applicable codec patents and source obligations need documented review.')
    severity = max({'PASS': 0, 'OPEN': 1, 'BLOCKER': 2}[c['status']] for c in checks)
    return {'schema': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(),
            'expected_version': expected, 'artifact_version': build['version'], 'build_info': build,
            'status': ['PASS', 'OPEN', 'BLOCKER'][severity], 'public_distribution_cleared': False,
            'checks': checks, 'files': files, 'native_files': natives, 'python_modules': modules,
            'installed_packages': packages, 'source_archives': sources}


def source_hash_check(target, build):
    archive_path = target / 'SeestarStudio-source.zip'
    if not archive_path.is_file():
        return 'BLOCKER', 'Missing application source archive'
    with zipfile.ZipFile(archive_path) as archive:
        # Match build_metadata's platform Path ordering (including Windows case
        # folding), not lexicographic archive strings. Existing build hashes use it.
        names = [p.as_posix() for p in sorted(Path(n) for n in archive.namelist()
                 if n.startswith('seestar_studio/') and not n.endswith('/')
                 and n != 'seestar_studio/build_info.json')]
        digest = hashlib.sha256()
        for name in names:
            digest.update(name.encode())
            digest.update(archive.read(name))
        info = json.loads(archive.read('seestar_studio/build_info.json'))
        valid = bool(names) and digest.hexdigest() == build.get('source_sha256') == info.get('source_sha256') and info['version'] == build['version']
        return ('PASS' if valid else 'BLOCKER'), {'files': len(names), 'computed_source_sha256': digest.hexdigest(),
                                                'scope': 'Application source vs embedded build metadata; not a native-library rebuild proof.'}


def write_report(report, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'compliance.json').write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding='utf-8')
    lines = [f"# Release evidence — {report['artifact_version']}", '',
             f"Requested audit: **{report['expected_version']}**. Result: **{report['status']}**.",
             'Technical evidence only; no legal clearance or publication authorization.', '',
             '| Check | Status |', '|---|---|']
    lines += [f"| {c['check']} | {c['status']} |" for c in report['checks']]
    lines += ['', 'Exact evidence, hashes, native mapping, embedded Python modules and source candidates: `compliance.json`.',
              'OPEN means unknown or incomplete. BLOCKER prevents treating this evidence as release clearance.']
    (output / 'COMPLIANCE.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--expected-version', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    target, output = args.target.resolve(), args.output.resolve()
    if output == target or target in output.parents:
        parser.error('Reports must be outside the audited artifact')
    try:
        report = audit(target, args.expected_version)
    except Exception as exc:
        # Exception text can include sensitive paths/values; only expose type.
        report = {'status': 'BLOCKER', 'artifact_version': 'UNKNOWN', 'expected_version': args.expected_version,
                  'public_distribution_cleared': False, 'checks': [{'check': 'audit_completed', 'status': 'BLOCKER',
                                                                  'evidence': type(exc).__name__}]}
    write_report(report, output)
    print(json.dumps({'status': report['status'], 'checks': len(report['checks'])}))
    return {'PASS': 0, 'OPEN': 1, 'BLOCKER': 2}[report['status']]


if __name__ == '__main__':
    raise SystemExit(main())
