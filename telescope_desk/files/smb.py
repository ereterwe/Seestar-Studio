"""Explicit per-device binding of SeestarPy's documented guest SMB access.

Only read APIs are exposed. No RPC file-list cursor and no remote mutations.
"""
from ..i18n import source as ui_text, tr
import io
from .models import RemoteEntry
from .paths import remote_path, child_path
SHARE_NAME = 'EMMC Images'

class SeestarFileClient:

    def __init__(self, info):
        from smb.SMBConnection import SMBConnection
        self._connection = SMBConnection('', '', 'TelescopeDesk', 'seestar', use_ntlm_v2=False, is_direct_tcp=True)
        try:
            if not self._connection.connect(info.ip, 445, timeout=8):
                raise ConnectionError(ui_text('m0297'))
        except Exception:
            self.close()
            raise

    @staticmethod
    def _entry(path: str, item) -> RemoteEntry:
        if getattr(item, 'file_attributes', 0) & 1024:
            raise ValueError(ui_text('m0295'))
        return RemoteEntry(path, item.filename or path.rsplit('/', 1)[-1], bool(item.isDirectory), int(item.file_size), float(item.last_write_time) if item.last_write_time else None)

    def list(self, path: str) -> list[RemoteEntry]:
        path = remote_path(path)
        result = []
        for item in self._connection.listPath(SHARE_NAME, path or '/', timeout=8):
            if item.filename in {'.', '..'}:
                continue
            try:
                result.append(self._entry(child_path(path, item.filename), item))
            except ValueError:
                continue
        return sorted(result, key=lambda entry: (not entry.is_dir, entry.name.casefold()))

    def stat(self, path: str) -> RemoteEntry:
        path = remote_path(path)
        return self._entry(path, self._connection.getAttributes(SHARE_NAME, path, timeout=8))

    def read(self, path: str, offset: int, length: int) -> bytes:
        if offset < 0 or not 0 < length <= 256 * 1024:
            raise ValueError(ui_text('m0296'))
        output = io.BytesIO()
        self._connection.retrieveFileFromOffset(SHARE_NAME, remote_path(path), output, offset=offset, max_length=length, timeout=8)
        return output.getvalue()

    def close(self) -> None:
        self._connection.close()
