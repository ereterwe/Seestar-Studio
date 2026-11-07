"""Native UI check with fake devices and no network-capable file/control adapter."""
import sys
import uuid
import time
from pathlib import Path
from PySide6.QtCore import QTimer, QItemSelectionModel
from PySide6.QtWidgets import QApplication
from seestar_studio.window import DashboardWindow
from seestar_studio.settings import SettingsService
from seestar_studio.theme import STYLE
from seestar_studio.files.browser import FileBrowserService
from seestar_studio.files.downloads import DownloadService
from tests.test_ui import FakeManager
from tests.test_control import fleet
from seestar_studio.planner import PlanEntry
from seestar_studio.sky.astronomy import Site
from seestar_studio.history import HistoryStore, Sample


class NoNetworkClient:
    def __init__(self, *args):
        raise ConnectionError('Offline UI fixture')


def main():
    app = QApplication(sys.argv[:1]); app.setStyle('Fusion'); app.setStyleSheet(STYLE)
    manager = FakeManager(0); manager.data = fleet()
    fixture_dir = Path('reports') / ('offline-qa-' + uuid.uuid4().hex[:8])
    store = HistoryStore(fixture_dir / 'history.sqlite3')
    for device, target, base_temp in [('SIM A', 'SIM M31', 25), ('SIM B', 'SIM IC1805', 30)]:
        for i in range(40):
            store.ingest(Sample(device, 'SIMULIERT', time.time() - 3600 + i * 15,
                True, target, 'Stack', 10, 100 + i, i // 5, (100 + i) * 10, 90 - i / 2, base_temp + i / 5))
    store.close()
    window = DashboardWindow(manager, SettingsService(fixture_dir / 'settings.json'),
        FileBrowserService(Path('reports/offline-cache'), NoNetworkClient), DownloadService(NoNetworkClient))
    window.control.service.factory = lambda ip: (_ for _ in ()).throw(AssertionError('No commands in UI QA'))
    window.resize(1920, 1080); window.show(); window.refresh()
    def capture():
        window.tabs.setCurrentWidget(window.control)
        QTimer.singleShot(500, lambda: window.grab().save('reports/control-mode.png'))
    def plan():
        window.sky.site = Site(52, 13, 40, 'Europe/Berlin')
        window.planner.entries = [PlanEntry('a', 'SIM A', 'NGC0224', 60), PlanEntry('b', 'SIM B', 'NGC7000', 90), PlanEntry('c', 'SIM A', 'NGC1976', 120)]
        window.planner.start.setText('2026-11-06T18:00:00Z')
        window.planner.calculate(False)
        window.tabs.setCurrentWidget(window.planner)
    QTimer.singleShot(2000, capture)
    QTimer.singleShot(4000, plan)
    QTimer.singleShot(10000, lambda: window.grab().save('reports/planner.png'))
    def history():
        window.tabs.setCurrentWidget(window.history)
        selection = window.history.table.selectionModel()
        for i, session in enumerate(window.history.sessions):
            if (session['target'] or '').startswith('SIM'):
                selection.select(window.history.table.model().index(i, 0), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        window.history.refresh()
    QTimer.singleShot(11000, history)
    QTimer.singleShot(14000, lambda: window.grab().save('reports/session-analysis.png'))
    QTimer.singleShot(16000, window.close)
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
