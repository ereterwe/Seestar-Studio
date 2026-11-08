import time
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QImage
from telescope_desk.viewer import ImageViewer
from telescope_desk.settings import SettingsService
from telescope_desk.window import DashboardWindow
from telescope_desk.models import DeviceInfo, ImageFrame, Telemetry
from telescope_desk.theme import STYLE


def test_zoom_position_and_fit(app):
    viewer = ImageViewer()
    viewer.resize(640, 480)
    viewer.show()
    image = QImage(1000, 1800, QImage.Format.Format_RGB888)
    image.fill(Qt.GlobalColor.darkBlue)
    viewer.set_image(image)
    app.processEvents()
    assert viewer.transform().m11() < .3
    viewer.actual_size()
    viewer.centerOn(QPointF(600, 1000))
    center = viewer.mapToScene(viewer.viewport().rect().center())
    viewer.set_image(image)
    assert viewer.transform().m11() == 1
    after = viewer.mapToScene(viewer.viewport().rect().center())
    assert abs(after.x() - center.x()) < 2 and abs(after.y() - center.y()) < 2
    viewer.close()


class FakeManager:
    running = False
    def __init__(self, count):
        self.data = {}
        for i in range(count):
            sn = str(i)
            info = DeviceInfo(sn, "127.0.0.1", "Simuliertes Teleskop")
            self.data[sn] = (info, Telemetry(sn, True, values={"target": "SIMULATION", "battery": 50}), None)
    def latest(self): return self.data, "SIMULIERTER TEST"
    def request_scan(self): pass
    def set_paused(self, sn, paused): pass
    def stop(self): pass


def test_layout_reorder_maximize_unknowns_and_settings(app, tmp_path):
    from telescope_desk.files.browser import FileBrowserService
    from telescope_desk.files.downloads import DownloadService
    class NoNetworkClient:
        def __init__(self, info): pass
        def list(self, path): return []
        def close(self): pass
    app.setStyleSheet(STYLE)
    settings = SettingsService(tmp_path / "settings.json")
    window = DashboardWindow(FakeManager(3), settings,
        FileBrowserService(tmp_path / 'cache', NoNetworkClient), DownloadService(NoNetworkClient))
    window.resize(1920, 1080)
    window.show()
    window.refresh()
    app.processEvents()
    assert len(window.cards) == 3
    assert window.cards["0"].metrics["filter"].text() == "—"
    window.move_card("0", 1)
    assert window.order[:2] == ["1", "0"]
    window.maximize_card("0")
    assert window.cards["0"].isVisible() and not window.cards["1"].isVisible()
    window.escape()
    assert window.cards["1"].isVisible()
    window.close()
    window.file_manager.downloads.join(2)
    window.refresh()
    assert SettingsService(settings.path).values["order"][:2] == ["1", "0"]


def test_stale_image_is_preserved(app):
    from telescope_desk.card import TelescopeCard
    info = DeviceInfo("test", "127.0.0.1")
    card = TelescopeCard(info)
    image = QImage(100, 100, QImage.Format.Format_RGB888)
    image.fill(Qt.GlobalColor.black)
    frame = ImageFrame(image, 1, time.time(), "stacked", "JPEG")
    card.update_data(info, Telemetry("test", True), frame)
    card.update_data(info, Telemetry("test", False, image_error="ConnectionError"), frame)
    assert card.frame is frame
    assert card.image_status.text().startswith("VERALTET")
    card.close()


def test_export_and_corrupt_settings(app, tmp_path):
    image = QImage(30, 50, QImage.Format.Format_RGB888)
    image.fill(Qt.GlobalColor.darkGreen)
    path = tmp_path / "export.png"
    assert image.save(str(path))
    restored = QImage(str(path))
    assert restored.size() == image.size()
    assert restored.pixelColor(4, 4) == image.pixelColor(4, 4)
    config = tmp_path / "settings.json"
    config.write_text("{broken", encoding="utf-8")
    settings = SettingsService(config)
    assert settings.values["order"] == []
    settings.values["order"] = ["A", "B"]
    settings.save()
    assert SettingsService(config).values["order"] == ["A", "B"]
