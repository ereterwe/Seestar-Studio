"""Local authentication onboarding, never reading existing keys for discovery."""
from .i18n import source as ui_text, tr
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time
import uuid
import zipfile
from PySide6.QtCore import QSaveFile, QIODevice
from .secure_storage import private_directory, write_new_private

class SetupError(ValueError):
    """Safe, user-readable error. Never contains a key or extraction output."""

@dataclass(frozen=True)
class KeyReference:
    path: Path
    origin: str
    fingerprint: str = ''
    bits: int = 0

def existing_reference(environ=None, cwd=None, home=None):
    environ = os.environ if environ is None else environ
    candidates = [(environ.get('SEESTAR_KEY_PATH'), ui_text('m0174')), (Path(cwd or Path.cwd()) / 'seestar.pem', ui_text('m0175')), (Path(home or Path.home()) / '.seestarpy' / 'seestar.pem', ui_text('m0176'))]
    for path, origin in candidates:
        if path and Path(path).is_file():
            return KeyReference(Path(path).resolve(), origin)
    return None

def validate_pem(content):
    if not 100 <= len(content) <= 32768:
        raise SetupError(ui_text('m0177'))
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    try:
        key = serialization.load_pem_private_key(content, password=None)
    except Exception:
        raise SetupError(ui_text('m0180')) from None
    if not isinstance(key, RSAPrivateKey) or key.key_size < 1024:
        raise SetupError(ui_text('m0178'))
    public = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    return (hashlib.sha256(public).hexdigest(), key.key_size)

def apk_keys(path):
    from seestarpy import extract_pem
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > 20000:
            raise SetupError(ui_text('m0181'))
        relevant = [i for i in infos if i.filename in extract_pem.SO_PATHS]
        if len({i.filename for i in relevant}) != len(relevant):
            raise SetupError(ui_text('m0182'))
        if any((i.file_size > 32 * 1024 * 1024 or i.flag_bits & 1 for i in relevant)):
            raise SetupError(ui_text('m0183'))
    return extract_pem.extract_pem_from_apk(path, progress=lambda message: None)

class SetupService:

    def __init__(self, profile, detector=existing_reference):
        self.profile = Path(profile)
        self.detector = detector
        self.config = self.profile / 'authentication.json'
        self.stopped = threading.Event()

    def imported_reference(self):
        try:
            data = json.loads(self.config.read_text(encoding='utf-8'))
            filename = data['key_file']
            if not isinstance(filename, str) or not filename.endswith('.pem') or Path(filename).name != filename or ('/' in filename) or ('\\' in filename):
                return None
            path = self.profile / 'keys' / filename
            if path.is_file() and (not path.is_symlink()) and (path.resolve().parent == (self.profile / 'keys').resolve()):
                return KeyReference(path, ui_text('m0190'))
        except (OSError, ValueError, KeyError, TypeError):
            pass
        return None

    def active(self):
        return self.imported_reference() or self.detector()

    def configure_runtime(self):
        reference = self.imported_reference()
        if reference:
            os.environ['SEESTAR_KEY_PATH'] = str(reference.path)
            auth = sys.modules.get('seestarpy.auth')
            if auth is not None:
                auth.set_key_path(reference.path)
        return self.active()

    def import_file(self, path):
        path = Path(path)
        if not path.is_file() or path.stat().st_size > 2 * 1024 ** 3:
            raise SetupError(ui_text('m0184'))
        created = []
        try:
            if path.suffix.lower() == '.pem':
                if path.stat().st_size > 32768:
                    raise SetupError(ui_text('m0198'))
                keys = [path.read_bytes()]
            elif path.suffix.lower() == '.apk':
                keys = [s.encode('ascii') for s in apk_keys(path)]
            elif path.suffix.lower() == '.xapk':
                keys = self._xapk_keys(path)
            else:
                raise SetupError(ui_text('m0201'))
            if self.stopped.is_set():
                raise SetupError(ui_text('m0191'))
            if not keys:
                raise SetupError(ui_text('m0192'))
            if len(keys) > 16:
                raise SetupError(ui_text('m0193'))
            validated = {}
            for content in keys:
                fingerprint, bits = validate_pem(content)
                validated[fingerprint] = (content, bits)
            result = []
            for fingerprint, (content, bits) in validated.items():
                destination = self.profile / 'keys' / f'{uuid.uuid4().hex}.pem'
                write_new_private(destination, content)
                created.append(destination)
                result.append(KeyReference(destination, ui_text('m0185'), fingerprint, bits))
            return result
        except SetupError:
            for item in created:
                item.unlink(missing_ok=True)
            raise
        except Exception:
            for item in created:
                item.unlink(missing_ok=True)
            raise SetupError(ui_text('m0194')) from None

    def discard(self, references):
        active = self.imported_reference()
        for reference in references:
            if active and active.path.resolve() == reference.path.resolve():
                continue
            if reference.origin != ui_text('m0185'):
                continue
            if reference.path.resolve().parent != (self.profile / 'keys').resolve():
                continue
            try:
                reference.path.unlink(missing_ok=True)
            except OSError:
                pass

    def _xapk_keys(self, path):
        staging = private_directory(self.profile / 'staging')
        result = []
        with zipfile.ZipFile(path) as archive, tempfile.TemporaryDirectory(prefix='import-', dir=staging) as temp:
            private_directory(temp)
            apks = [i for i in archive.infolist() if i.filename.lower().endswith('.apk')]
            if not apks or len(apks) > 30 or sum((i.file_size for i in apks)) > 2 * 1024 ** 3:
                raise SetupError(ui_text('m0195'))
            for index, item in enumerate(apks):
                if self.stopped.is_set():
                    raise SetupError(ui_text('m0191'))
                if item.file_size > 512 * 1024 ** 2 or item.flag_bits & 1:
                    raise SetupError(ui_text('m0199'))
                target = Path(temp) / f'{index}.apk'
                with archive.open(item) as source, target.open('xb') as output:
                    remaining = item.file_size
                    while remaining > 0:
                        block = source.read(min(1024 ** 2, remaining))
                        if not block:
                            raise SetupError(ui_text('m0202'))
                        output.write(block)
                        remaining -= len(block)
                result += [s.encode('ascii') for s in apk_keys(target)]
                target.unlink()
                if len(result) > 16:
                    raise SetupError(ui_text('m0200'))
        return result

    def activate(self, reference, confirmed=False):
        current = self.active()
        if current and current.path != reference.path and (not confirmed):
            raise SetupError(ui_text('m0186'))
        expected = (self.profile / 'keys').resolve()
        if reference.path.resolve().parent != expected or not reference.path.is_file():
            raise SetupError(ui_text('m0187'))
        private_directory(self.profile)
        output = QSaveFile(str(self.config))
        if not output.open(QIODevice.OpenModeFlag.WriteOnly):
            raise SetupError(ui_text('m0188'))
        output.write(json.dumps({'version': 1, 'key_file': reference.path.name}).encode('utf-8'))
        if not output.commit():
            raise SetupError(ui_text('m0188'))
        self.configure_runtime()

    def connection_check(self, info, reference):
        import socket
        from seestarpy import auth, connection
        from .backend import ReadOnlySocket
        if reference is None:
            raise SetupError(ui_text('m0189'))
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ReadOnlySocket(raw, self.stopped)
        sock.deadline, sock.remaining_bytes = (time.monotonic() + 30, 2 * 1024 ** 2)
        try:
            sock.settimeout(5)
            sock.connect((info.ip, connection.DEFAULT_PORT))
            auth.authenticate(sock, key_path=str(reference.path))
            reply = auth._send_recv(sock, {'id': 1205, 'method': 'get_device_state', 'params': {'keys': ['device']}})
            device = (reply.get('result') or {}).get('device') or {}
            if reply.get('code') != 0 or str(device.get('sn', '')).casefold() != info.serial.casefold():
                raise SetupError(ui_text('m0196'))
            return ui_text('m0179')
        except SetupError:
            raise
        except Exception:
            raise SetupError(ui_text('m0197')) from None
        finally:
            try:
                raw.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            raw.close()
