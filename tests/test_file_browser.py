from concurrent.futures import Future
import io
from pathlib import Path
from PIL import Image
from seestar_studio.files.browser import FileBrowserService
from seestar_studio.files.models import RemoteEntry
from seestar_studio.files.widget import FileManagerWidget
from seestar_studio.files.downloads import DownloadService
from seestar_studio.models import DeviceInfo, Telemetry
from seestar_studio.settings import SettingsService
from tests.test_files import MemoryClient


def test_thumbnail_cache_and_no_raw_download(app, tmp_path):
    stream = io.BytesIO()
    Image.new('RGB', (100, 200), 'red').save(stream, format='JPEG')
    client = MemoryClient(stream.getvalue())
    service = FileBrowserService(tmp_path, lambda info: client)
    info = DeviceInfo('test', '127.0.0.1')
    entry = client.stat('MyWorks/test.jpg')
    try:
        image = service.thumbnail(info, entry).result(3)
        assert not image.isNull()
        count = len(client.offsets)
        assert not service.thumbnail(info, entry).result(3).isNull()
        assert len(client.offsets) == count
        import pytest
        with pytest.raises(ValueError):
            service.thumbnail(info, client.stat('MyWorks/test.fit')).result(3)
        assert len(client.offsets) == count
    finally:
        service.stop()


def test_native_file_manager_device_and_directory_list(app, tmp_path):
    class Browser:
        running = False
        def list(self, info, path):
            result = Future()
            result.set_result([RemoteEntry('MyWorks/M31', 'M31', True)] if not path else [RemoteEntry(path + '/test.fit', 'test.fit', False, 5000, 1234)])
            return result
        def stop(self): pass
    service = DownloadService(lambda info: MemoryClient())
    widget = FileManagerWidget(SettingsService(tmp_path / 'settings.json'), Browser(), service)
    info = DeviceInfo('test', '127.0.0.1', 'Mock telescope')
    widget.sync_devices({'test': (info, Telemetry('test', True), None)})
    assert widget.tree.topLevelItemCount() == 1
    assert widget.tree.topLevelItem(0).child(0).text(0) == 'M31'
    widget.show_path('test', 'MyWorks/M31')
    widget.poll()
    assert widget.files.topLevelItemCount() == 1, widget.message.text()
    assert widget.files.topLevelItem(0).text(0) == 'test.fit'
    widget.search.setText('jpg')
    assert widget.files.topLevelItem(0).isHidden()
    widget.stop(); service.join(2)
