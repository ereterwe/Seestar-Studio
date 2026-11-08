import hashlib
from pathlib import Path
import threading
import time
import pytest
from telescope_desk.models import DeviceInfo
from telescope_desk.files.models import RemoteEntry, TransferCancelled, RemoteChangedError
from telescope_desk.files.paths import remote_path, windows_name, destination
from telescope_desk.files.downloads import download_one, DownloadService


INFO = DeviceInfo('test-device', '127.0.0.1', 'Seestar test')


class MemoryClient:
    def __init__(self, data=b'abc' * 200000):
        self.data = data
        self.offsets = []
        self.modified = 1234.0
        self.closed = False
    def stat(self, path):
        return RemoteEntry(path, path.rsplit('/', 1)[-1], False, len(self.data), self.modified)
    def list(self, path):
        return [self.stat(path + '/image.fit')]
    def read(self, path, offset, length):
        self.offsets.append(offset)
        return self.data[offset:offset + length]
    def close(self): self.closed = True


@pytest.mark.parametrize('path', ['../a', 'MyWorks/../a', '/etc/file', 'C:/file', 'a\\b', 'a\x00b', 'a//b', 'a/./b'])
def test_reject_remote_traversal(path):
    with pytest.raises(ValueError): remote_path(path)


def test_windows_paths_and_collision_safety(tmp_path):
    for value in ['CON', 'COM1.fit', 'NGC:7000', 'x.', 'x ', 'a' * 200]:
        result = windows_name(value)
        assert result != value
        assert ':' not in result and len(result) < 130
    assert windows_name('a:b') != windows_name('a?b')
    assert destination(tmp_path, 'Seestar', 'MyWorks/M 31/test.fit').is_relative_to(tmp_path)


def test_complete_duplicate_and_no_overwrite(tmp_path):
    client = MemoryClient()
    entry = client.stat('MyWorks/M31/a.fit')
    target, skipped = download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *args: None, 0)
    assert not skipped and target.read_bytes() == client.data
    previous = len(client.offsets)
    assert download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *a: None, 0)[1]
    assert len(client.offsets) == previous
    target.write_bytes(b'local edit')
    with pytest.raises(FileExistsError):
        download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *a: None, 0)
    assert target.read_bytes() == b'local edit'


def test_cancel_resume_and_partial_integrity(tmp_path):
    client = MemoryClient()
    entry = client.stat('MyWorks/test.fit')
    cancelled = threading.Event()
    def progress(*args): cancelled.set()
    with pytest.raises(TransferCancelled):
        download_one(client, INFO, entry, tmp_path, cancelled, progress, 0)
    partial = next(tmp_path.rglob('data.part'))
    length = partial.stat().st_size
    assert 0 < length < entry.size
    client.offsets.clear()
    target, _ = download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *a: None, 0)
    assert client.offsets[0] == length
    assert target.read_bytes() == client.data
    assert not partial.exists()


def test_corrupt_partial_is_not_appended(tmp_path):
    client = MemoryClient()
    entry = client.stat('MyWorks/test.fit')
    cancel = threading.Event()
    with pytest.raises(TransferCancelled):
        download_one(client, INFO, entry, tmp_path, cancel, lambda *a: cancel.set(), 0)
    partial = next(tmp_path.rglob('data.part'))
    partial.write_bytes(b'bad')
    with pytest.raises(ValueError, match='Teiltransfer'):
        download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *a: None, 0)
    assert partial.read_bytes() == b'bad'


def test_remote_change_short_read_empty_file(tmp_path):
    client = MemoryClient()
    entry = client.stat('MyWorks/test.fit')
    client.modified += 1
    with pytest.raises(RemoteChangedError):
        download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *a: None, 0)
    client = MemoryClient(b'')
    path, skipped = download_one(client, INFO, client.stat('MyWorks/empty'), tmp_path, threading.Event(), lambda *a: None, 0)
    assert path.stat().st_size == 0
    client = MemoryClient()
    client.read = lambda *a: b''
    with pytest.raises(IOError):
        download_one(client, INFO, client.stat('MyWorks/short'), tmp_path, threading.Event(), lambda *a: None, 0)


def test_changed_while_downloading_not_published(tmp_path):
    client = MemoryClient()
    entry = client.stat('MyWorks/change.fit')
    with pytest.raises(RemoteChangedError):
        download_one(client, INFO, entry, tmp_path, threading.Event(), lambda *a: setattr(client, 'modified', 9999), 0)
    assert not destination(tmp_path, f'{INFO.model}_{INFO.serial}', entry.path).exists()


def test_service_multiple_devices_recursive_dedup_shutdown(tmp_path):
    clients = []
    def factory(info):
        client = MemoryClient(b'abc')
        clients.append(client)
        return client
    service = DownloadService(factory)
    folder = RemoteEntry('MyWorks/M31', 'M31', True)
    try:
        service.submit(INFO, [folder, RemoteEntry('MyWorks/M31/image.fit', 'image.fit', False, 3, 1234)], tmp_path, 0)
        service.submit(DeviceInfo('second', '127.0.0.2'), [folder], tmp_path, 0)
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline and not all(s.state == 'Fertig' for s in service.statuses()):
            time.sleep(.02)
        assert len(service.statuses()) == 2
        assert all(s.state == 'Fertig' and s.files_total == 1 for s in service.statuses())
    finally:
        service.stop(); service.join(3)
    assert not service.running and all(c.closed for c in clients)
