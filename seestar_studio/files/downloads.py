from ..i18n import source as ui_text, tr
import hashlib
import json
import os
from pathlib import Path
import queue
import threading
import time
from dataclasses import dataclass, replace
from typing import Callable
from .models import RemoteEntry, TransferCancelled, RemoteChangedError
from .paths import destination, under_root, remote_path
from .smb import SeestarFileClient

def atomic_json(path: Path, data: dict) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def same_remote(left: RemoteEntry, right: RemoteEntry) -> bool:
    return left.size == right.size and left.modified == right.modified and (not right.is_dir)

def download_one(client, info, entry: RemoteEntry, root: Path, cancel: threading.Event, progress: Callable[[int, int, float], None], limit_bps: int=2 * 1024 * 1024) -> tuple[Path, bool]:
    """Offset resume with checkpoint hash, immutable final file and identity check.

    Server offers size/mtime, no checksum. SHA256 verifies local checkpoint and
    later duplicate files; it is never presented as a server-side checksum.
    """
    remote_path(entry.path)
    current = client.stat(entry.path)
    if not same_remote(entry, current):
        raise RemoteChangedError(ui_text('m0277'))
    target = destination(root, f'{info.model}_{info.serial}', entry.path)
    identity = {'serial': info.serial, 'path': entry.path, 'size': entry.size, 'modified': entry.modified}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    staging = under_root(root, '.studio-partials', key)
    staging.mkdir(parents=True, exist_ok=True)
    partial, checkpoint, receipt = (staging / 'data.part', staging / 'checkpoint.json', staging / 'receipt.json')
    if target.exists():
        try:
            proof = json.loads(receipt.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            proof = {}
        if proof.get('identity') == identity and target.is_file() and (target.stat().st_size == entry.size) and (sha256_file(target) == proof.get('sha256')):
            progress(entry.size, entry.size, 0)
            return (target, True)
        raise FileExistsError(ui_text('m0278'))
    offset = 0
    digest = hashlib.sha256()
    if partial.exists() and partial.stat().st_size:
        try:
            saved = json.loads(checkpoint.read_text(encoding='utf-8'))
            offset = partial.stat().st_size
            if saved.get('identity') != identity or saved.get('bytes') != offset or offset > entry.size:
                raise ValueError()
            with partial.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    if cancel.is_set():
                        raise TransferCancelled()
                    digest.update(block)
            if saved.get('sha256') != digest.hexdigest():
                raise ValueError()
        except (OSError, ValueError):
            raise ValueError(ui_text('m0281')) from None
    started, initial = (time.monotonic(), offset)
    target.parent.mkdir(parents=True, exist_ok=True)
    destination(root, f'{info.model}_{info.serial}', entry.path)
    under_root(root, '.studio-partials', key, 'data.part')
    with partial.open('ab' if partial.exists() else 'xb') as output:
        while offset < entry.size:
            if cancel.is_set():
                raise TransferCancelled()
            block = client.read(entry.path, offset, min(256 * 1024, entry.size - offset))
            if not block or len(block) > entry.size - offset:
                raise IOError(ui_text('m0282'))
            output.write(block)
            output.flush()
            os.fsync(output.fileno())
            digest.update(block)
            offset += len(block)
            atomic_json(checkpoint, {'identity': identity, 'bytes': offset, 'sha256': digest.hexdigest()})
            elapsed = max(0.001, time.monotonic() - started)
            progress(offset, entry.size, (offset - initial) / elapsed)
            if limit_bps > 0:
                delay = (offset - initial) / limit_bps - elapsed
                if delay > 0 and cancel.wait(delay):
                    raise TransferCancelled()
    if cancel.is_set():
        raise TransferCancelled()
    if not same_remote(entry, client.stat(entry.path)):
        raise RemoteChangedError(ui_text('m0279'))
    if partial.stat().st_size != entry.size:
        raise IOError(ui_text('m0280'))
    target = destination(root, f'{info.model}_{info.serial}', entry.path)
    try:
        os.link(partial, target)
    except OSError:
        created = False
        try:
            with target.open('xb') as output, partial.open('rb') as source:
                created = True
                for block in iter(lambda: source.read(1024 * 1024), b''):
                    if cancel.is_set():
                        raise TransferCancelled()
                    output.write(block)
                output.flush()
                os.fsync(output.fileno())
        except BaseException:
            if created:
                target.unlink()
            raise
    atomic_json(receipt, {'identity': identity, 'sha256': digest.hexdigest(), 'integrity': 'SMB size+mtime; local SHA256'})
    partial.unlink()
    progress(entry.size, entry.size, (offset - initial) / max(0.001, time.monotonic() - started))
    return (target, False)

@dataclass(frozen=True)
class DownloadStatus:
    job_id: str
    serial: str
    name: str
    state: str = ui_text('extra.4')
    done: int = 0
    total: int = 0
    speed: float = 0
    files_done: int = 0
    files_total: int = 0
    error: str = ''

class DownloadService:
    """One transfer globally; bounded, cancellable directory enumeration."""

    def __init__(self, factory=SeestarFileClient):
        self.factory = factory
        self._queue = queue.Queue(maxsize=100)
        self._lock = threading.Lock()
        self._statuses: dict[str, DownloadStatus] = {}
        self._jobs: dict[str, tuple] = {}
        self._devices = {}
        self._cancel: dict[str, threading.Event] = {}
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name='studio-download', daemon=True)
        self._thread.start()

    def submit(self, info, entries: list[RemoteEntry], root: Path, limit_bps: int) -> str:
        payload = (info.serial, sorted((e.path for e in entries)), str(root.resolve()))
        key = hashlib.sha256(json.dumps(payload).encode()).hexdigest()[:16]
        with self._lock:
            if key in self._statuses and self._statuses[key].state in {ui_text('extra.4'), ui_text('m0285'), ui_text('m0286')}:
                return key
            if self._queue.full():
                raise ValueError(ui_text('m0283'))
            if len(self._statuses) >= 200 and key not in self._statuses:
                for old, status in list(self._statuses.items()):
                    if status.state not in {ui_text('extra.4'), ui_text('m0285'), ui_text('m0286')}:
                        self._statuses.pop(old, None)
                        self._jobs.pop(old, None)
                        self._cancel.pop(old, None)
                        break
            self._jobs[key] = (info, list(entries), root, max(0, limit_bps))
            self._cancel[key] = threading.Event()
            self._statuses[key] = DownloadStatus(key, info.serial, ', '.join((e.name for e in entries)))
            self._queue.put_nowait(key)
        return key

    def statuses(self) -> list[DownloadStatus]:
        with self._lock:
            return list(self._statuses.values())

    def update_devices(self, devices: dict) -> None:
        with self._lock:
            self._devices.update(devices)

    def cancel(self, job_id: str) -> None:
        with self._lock:
            if job_id in self._cancel:
                self._cancel[job_id].set()

    def retry(self, job_id: str) -> None:
        with self._lock:
            args = self._jobs.get(job_id)
        if args:
            self.submit(*args)

    def _update(self, key: str, **fields) -> None:
        with self._lock:
            self._statuses[key] = replace(self._statuses[key], **fields)

    def _walk(self, client, selections: list[RemoteEntry], cancel) -> list[RemoteEntry]:
        pending, files, seen = (list(selections), [], set())
        while pending:
            if cancel.is_set():
                raise TransferCancelled()
            entry = pending.pop()
            if entry.path in seen:
                continue
            seen.add(entry.path)
            if len(seen) > 100000 or len(entry.path.split('/')) > 32:
                raise ValueError(ui_text('m0284'))
            if entry.is_dir:
                pending.extend(client.list(entry.path))
            else:
                files.append(entry)
        return sorted(files, key=lambda entry: entry.path)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                key = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            with self._lock:
                info, entries, root, limit = self._jobs[key]
                info = self._devices.get(info.serial, info)
                cancel = self._cancel[key]
            client = None
            try:
                if cancel.is_set():
                    raise TransferCancelled()
                self._update(key, state=ui_text('m0285'))
                client = self.factory(info)
                files = self._walk(client, entries, cancel)
                total, completed = (sum((e.size for e in files)), 0)
                self._update(key, state=ui_text('m0286'), total=total, files_total=len(files), error='')
                for index, entry in enumerate(files):

                    def progress(done, size, speed):
                        self._update(key, done=completed + done, speed=speed)
                    download_one(client, info, entry, root, cancel, progress, limit)
                    completed += entry.size
                    self._update(key, files_done=index + 1)
                self._update(key, state=ui_text('m0287'), done=total, speed=0)
            except TransferCancelled:
                self._update(key, state=ui_text('m0288'), speed=0)
            except Exception as exc:
                message = str(exc) if isinstance(exc, (FileExistsError, RemoteChangedError, ValueError)) else type(exc).__name__
                self._update(key, state=ui_text('m0289'), error=message, speed=0)
            finally:
                if client is not None:
                    try:
                        client.close()
                    except Exception:
                        pass

    def stop(self) -> None:
        self._stop.set()
        with self._lock:
            for event in self._cancel.values():
                event.set()

    @property
    def running(self) -> bool:
        return self._thread.is_alive()

    def join(self, timeout=None) -> None:
        self._thread.join(timeout)
