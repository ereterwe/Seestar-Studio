"""Async read-only directory/thumbnail service, independent of Qt widgets."""
from ..i18n import source as ui_text, tr
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import threading
from .smb import SeestarFileClient
from .models import RemoteEntry, TransferCancelled

class FileBrowserService:

    def __init__(self, cache_root: Path, factory=SeestarFileClient):
        self.cache_root, self.factory = (cache_root, factory)
        self._pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='studio-file-browser')
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._futures = set()

    def _submit(self, function, *args):
        future = self._pool.submit(function, *args)
        with self._lock:
            self._futures.add(future)
        future.add_done_callback(self._finished)
        return future

    def _finished(self, future):
        with self._lock:
            self._futures.discard(future)

    def list(self, info, path: str):
        return self._submit(self._list, info, path)

    def _list(self, info, path):
        if self._stop.is_set():
            raise TransferCancelled()
        client = self.factory(info)
        try:
            return client.list(path)
        finally:
            client.close()

    def thumbnail(self, info, entry: RemoteEntry):
        return self._submit(self._thumbnail, info, entry)

    def _thumbnail(self, info, entry):
        from PySide6.QtGui import QImage
        from PySide6.QtCore import Qt
        if Path(entry.name).suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
            raise ValueError(ui_text('m0273'))
        if entry.size > 8 * 1024 * 1024:
            raise ValueError(ui_text('m0274'))
        key = hashlib.sha256(f'{info.serial}:{entry.path}:{entry.size}:{entry.modified}'.encode()).hexdigest()
        self.cache_root.mkdir(parents=True, exist_ok=True)
        path = self.cache_root / (key + '.png')
        if path.is_file():
            image = QImage(str(path))
            if not image.isNull():
                return image
        client = self.factory(info)
        try:
            chunks, offset = ([], 0)
            while offset < entry.size:
                if self._stop.is_set():
                    raise TransferCancelled()
                data = client.read(entry.path, offset, min(256 * 1024, entry.size - offset))
                if not data:
                    raise IOError(ui_text('m0276'))
                chunks.append(data)
                offset += len(data)
                if self._stop.wait(len(data) / (1024 * 1024)):
                    raise TransferCancelled()
            image = QImage.fromData(b''.join(chunks))
            if image.isNull():
                raise ValueError(ui_text('m0275'))
            image = image.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image.save(str(path))
            files = sorted(self.cache_root.glob('*.png'), key=lambda p: p.stat().st_mtime, reverse=True)
            for obsolete in files[150:]:
                if len(obsolete.stem) == 64 and all((c in '0123456789abcdef' for c in obsolete.stem)):
                    obsolete.unlink(missing_ok=True)
            return image
        finally:
            client.close()

    def stop(self):
        self._stop.set()
        self._pool.shutdown(wait=False, cancel_futures=True)

    @property
    def running(self):
        with self._lock:
            return bool(self._futures)
