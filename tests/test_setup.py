import io
import os
from pathlib import Path
import subprocess
import zipfile
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from telescope_desk.setup_service import SetupService, SetupError, existing_reference, validate_pem
from telescope_desk.secure_storage import write_new_private


@pytest.fixture(scope='module')
def synthetic_pem():
    # Ephemeral test key generated at runtime; never a ZWO key or source asset.
    return rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())


def test_existing_discovery_preserves_precedence_without_reading(tmp_path, monkeypatch):
    home = tmp_path / 'home'; (home / '.seestarpy').mkdir(parents=True)
    original = home / '.seestarpy' / 'seestar.pem'; original.write_text('not opened during discovery')
    env_key = tmp_path / 'environment.pem'; env_key.write_text('also not opened')
    monkeypatch.setattr(Path, 'read_bytes', lambda *a: pytest.fail('Existing key read'))
    assert existing_reference({}, tmp_path, home).path == original.resolve()
    assert existing_reference({'SEESTAR_KEY_PATH': str(env_key)}, tmp_path, home).path == env_key.resolve()


def test_secure_import_confirmation_activation_and_no_overwrite(app, tmp_path, synthetic_pem, monkeypatch):
    source = tmp_path / 'input.pem'; source.write_bytes(synthetic_pem)
    existing = existing_reference({'SEESTAR_KEY_PATH': str(source)}, tmp_path, tmp_path)
    service = SetupService(tmp_path / 'profile', detector=lambda: existing)
    refs = service.import_file(source)
    assert len(refs) == 1 and refs[0].bits == 2048
    assert service.active() == existing
    with pytest.raises(SetupError): service.activate(refs[0])
    monkeypatch.setattr(service, 'configure_runtime', lambda: None)
    service.activate(refs[0], confirmed=True)
    assert service.active().path == refs[0].path
    assert source.read_bytes() == synthetic_pem
    assert service.config.read_text().find('PRIVATE KEY') == -1
    service.discard(refs)
    assert refs[0].path.exists()  # active file is never discarded
    with pytest.raises(FileExistsError): write_new_private(refs[0].path, b'overwrite')
    assert refs[0].path.read_bytes() == synthetic_pem


def make_apk(content):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('lib/arm64-v8a/libopenssllib.so', b'\x00binary\x00' + content + b'\x00')
    return out.getvalue()


def test_apk_xapk_local_extractor_cleanup(tmp_path, synthetic_pem):
    service = SetupService(tmp_path / 'profile', detector=lambda: None)
    apk = tmp_path / 'input.apk'; apk.write_bytes(make_apk(synthetic_pem))
    refs = service.import_file(apk)
    assert len(refs) == 1
    service.discard(refs); assert not refs[0].path.exists()
    xapk = tmp_path / 'input.xapk'
    with zipfile.ZipFile(xapk, 'w') as archive:
        archive.writestr('../../outside.apk', apk.read_bytes())
    refs = service.import_file(xapk)
    assert len(refs) == 1 and not (tmp_path / 'outside.apk').exists()
    assert not list((service.profile / 'staging').iterdir())
    service.discard(refs)


def test_invalid_inputs_never_activate(tmp_path):
    service = SetupService(tmp_path / 'profile', detector=lambda: None)
    pem = tmp_path / 'bad.pem'; pem.write_text('not a key')
    with pytest.raises(SetupError): service.import_file(pem)
    apk = tmp_path / 'bad.apk'; apk.write_text('not a zip')
    with pytest.raises(SetupError): service.import_file(apk)
    assert service.active() is None and not service.config.exists()


@pytest.mark.skipif(os.name != 'nt', reason='Windows DACL verification')
def test_windows_private_acl_is_protected_and_has_two_entries(tmp_path):
    target = write_new_private(tmp_path / 'private' / 'test.bin', b'synthetic test data')
    acl_file = tmp_path / 'acl.txt'
    result = subprocess.run([str(Path(os.environ['SystemRoot']) / 'System32' / 'icacls.exe'), str(target), '/save', str(acl_file), '/q'],
        capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode == 0
    text = acl_file.read_text(encoding='utf-16-le').lstrip('\ufeff')
    assert 'D:P' in text and text.count('(A;') == 2
    assert ';;;SY)' in text and ';;;WD)' not in text and ';;;BU)' not in text


def test_wizard_existing_config_never_imports_or_activates(app, tmp_path, monkeypatch):
    from telescope_desk.setup_wizard import SetupWizard
    key = tmp_path / 'existing.pem'; key.write_text('unread')
    ref = existing_reference({'SEESTAR_KEY_PATH': str(key)}, tmp_path, tmp_path)
    service = SetupService(tmp_path / 'profile', detector=lambda: ref)
    monkeypatch.setattr(service, 'activate', lambda *a, **k: pytest.fail('Existing config changed'))
    wizard = SetupWizard(service.profile, lambda: {}, service=service)
    assert wizard.keep.isChecked()
    assert wizard.selected_reference() == ref
    wizard.accept()
    assert not wizard.running and not service.config.exists()


def test_connection_check_reads_identity_with_explicit_key_only(tmp_path, monkeypatch):
    import socket
    from seestarpy import auth
    from telescope_desk.models import DeviceInfo
    from telescope_desk.setup_service import KeyReference
    from telescope_desk import backend
    calls = []
    class FakeSocket:
        def settimeout(self, value): pass
        def connect(self, address): calls.append(('connect', address))
        def shutdown(self, how): pass
        def close(self): calls.append(('close',))
    monkeypatch.setattr(socket, 'socket', lambda *a: FakeSocket())
    monkeypatch.setattr(backend, 'ReadOnlySocket', lambda raw, stopped: raw)
    monkeypatch.setattr(auth, 'authenticate', lambda sock, key_path: calls.append(('auth', key_path)))
    def reply(sock, payload):
        calls.append(('rpc', payload))
        return {'code': 0, 'result': {'device': {'sn': 'test-device'}}}
    monkeypatch.setattr(auth, '_send_recv', reply)
    monkeypatch.setattr(auth, 'set_key_path', lambda *a: pytest.fail('Global authentication changed'))
    service = SetupService(tmp_path / 'profile', detector=lambda: None)
    reference = KeyReference(tmp_path / 'synthetic.pem', 'test')
    assert 'erfolgreich' in service.connection_check(DeviceInfo('test-device', '192.0.2.1'), reference)
    assert [v[1]['method'] for v in calls if v[0] == 'rpc'] == ['get_device_state']
    assert ('auth', str(reference.path)) in calls and calls[-1] == ('close',)
    with pytest.raises(SetupError):
        service.connection_check(DeviceInfo('different-device', '192.0.2.1'), reference)


def test_cancelled_wizard_consumes_pending_import_and_cleans_candidates(app, tmp_path, synthetic_pem):
    from concurrent.futures import Future
    from telescope_desk.setup_wizard import SetupWizard
    source = tmp_path / 'synthetic.pem'; source.write_bytes(synthetic_pem)
    service = SetupService(tmp_path / 'profile', detector=lambda: None)
    wizard = SetupWizard(service.profile, lambda: {}, service=service)
    refs = service.import_file(source)
    future = Future()
    wizard._future = ('import', future)
    wizard.reject()
    assert wizard.running and not wizard._disposed
    future.set_result(refs); wizard.poll()
    assert wizard._disposed and not wizard.running
    assert all(not ref.path.exists() for ref in refs)
    assert not service.config.exists()
