"""Evidence failures must not become release clearance."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

from tools.release_compliance import check_sources, git_history, private_name, scan_bytes, scan_zip, source_hash_check, write_report


def archive_bytes(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return stream.getvalue()


def test_nested_archive_private_material_is_detected_without_echoing_it():
    secret = b'-----BEGIN PRIVATE KEY-----\n' + b'A' * 240 + b'\n-----END PRIVATE KEY-----'
    report = scan_zip(archive_bytes({'sources.zip': archive_bytes({'hidden.txt': secret})}))
    assert report['findings'][0]['blockers'] == ['private_key_material']
    assert secret.decode() not in json.dumps(report)
    assert scan_bytes(b"pattern = '-----BEGIN PRIVATE KEY-----'")['blockers'] == []


def test_private_names_and_path_traversal():
    assert private_name('profile/session.sqlite3')
    assert private_name('authentication/import.pem')
    assert not private_name('_internal/certifi/cacert.pem')
    findings = scan_zip(archive_bytes({'../escape.txt': 'safe content'}))['findings']
    assert 'unsafe_or_duplicate_archive_path' in findings[0]['blockers']


def test_source_archive_hash_never_proves_binary_correspondence(tmp_path):
    (tmp_path / 'good.tar.gz').write_bytes(b'example source archive')
    records = [
        {'component': 'good', 'file': 'good.tar.gz', 'sha256': hashlib.sha256(b'example source archive').hexdigest()},
        {'component': 'missing', 'file': 'missing.tar.gz', 'sha256': '0' * 64},
        {'component': 'wrong', 'file': 'good.tar.gz', 'sha256': '0' * 64},
    ]
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'sources': records}))
    result = check_sources(manifest, tmp_path)
    assert [r['archive_check'] for r in result] == ['PASS', 'OPEN', 'BLOCKER']
    assert all(r['binary_correspondence'] == 'OPEN' for r in result)


def test_source_build_hash_order_and_tamper(tmp_path):
    files = {'seestar_studio/assets/Icon.txt': b'icon', 'seestar_studio/assets.py': b'code',
             'seestar_studio/Hello.py': b'upper', 'seestar_studio/alpha.py': b'lower'}
    digest = hashlib.sha256()
    for path in sorted(map(Path, files)):
        digest.update(path.as_posix().encode())
        digest.update(files[path.as_posix()])
    build = {'version': 'test', 'source_sha256': digest.hexdigest()}
    files['seestar_studio/build_info.json'] = json.dumps(build).encode()
    path = tmp_path / 'SeestarStudio-source.zip'
    path.write_bytes(archive_bytes(files))
    assert source_hash_check(tmp_path, build)[0] == 'PASS'
    files['seestar_studio/alpha.py'] = b'modified'
    path.write_bytes(archive_bytes(files))
    assert source_hash_check(tmp_path, build)[0] == 'BLOCKER'


def test_machine_and_human_report_keep_unknown_open(tmp_path):
    report = {'artifact_version': 'old', 'expected_version': 'new', 'status': 'BLOCKER',
              'checks': [{'check': 'version', 'status': 'BLOCKER'}, {'check': 'sources', 'status': 'OPEN'}]}
    write_report(report, tmp_path)
    assert json.loads((tmp_path / 'compliance.json').read_text()) == report
    human = (tmp_path / 'COMPLIANCE.md').read_text()
    assert '| sources | OPEN |' in human
    assert 'legal clearance' in human


def test_history_detects_removed_synthetic_secret_without_echo(tmp_path):
    def git(*args):
        return subprocess.run(['git', '-c', 'user.name=Audit Test', '-c', 'user.email=audit@example.invalid',
                               '-c', 'commit.gpgsign=false', *args], cwd=tmp_path,
                              check=True, capture_output=True)
    git('init')
    synthetic = 'ghp_' + 'A' * 36  # Format fixture, never a real credential.
    path = tmp_path / 'old.txt'
    path.write_text(synthetic)
    git('add', 'old.txt')
    git('commit', '-m', 'Synthetic historical fixture')
    git('tag', '-a', 'fixture', '-m', 'Fixture tag')
    path.write_text('removed from working file')
    git('add', 'old.txt')
    git('commit', '-m', 'Remove fixture from current content')
    report = git_history(tmp_path)
    assert report['counts']['commit'] == 2 and report['counts']['tag'] == 1
    assert any('github_token' in f['blockers'] for f in report['findings'])
    assert synthetic not in json.dumps(report)
