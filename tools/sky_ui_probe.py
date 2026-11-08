"""Native QA with a clearly synthetic site; never writes it to user settings."""
import json
from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from telescope_desk.manager import TelescopeManager
from telescope_desk.settings import SettingsService
from telescope_desk.window import DashboardWindow
from telescope_desk.theme import STYLE
from telescope_desk.sky.astronomy import Site


def main():
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Telescope Desk'); app.setOrganizationName('TelescopeDesk')
    app.setStyle('Fusion'); app.setStyleSheet(STYLE)
    manager = TelescopeManager()
    settings = SettingsService(Path('reports/sky-test-settings.json'))
    window = DashboardWindow(manager, settings)
    window.resize(1920, 1080); window.show(); manager.start()
    report = {'site': 'synthetic test fixture, not user observing location'}
    def prepare():
        window.tabs.setCurrentWidget(window.sky)
        window.sky.site = Site(52, 13, 40, 'Europe/Berlin')
        window.sky.search.setText('M31')
        window.sky.request_calculation()
    def capture():
        window.grab().save('reports/sky-explorer.png')
        report['catalog_count'] = len(window.sky.catalog.targets) if window.sky.catalog else 0
        report['night_calculated'] = window.sky.night is not None
        data, _ = manager.latest()
        report['devices'] = {sn: {'connected': tel.connected, 'target': tel.get('target'),
            'stage': tel.get('view_stage'), 'frame_seq': frame.sequence if frame else None} for sn, (_, tel, frame) in data.items()}
        window.tabs.setCurrentIndex(0)
        QTimer.singleShot(1000, lambda: window.grab().save('reports/phase2-dashboard.png'))
    QTimer.singleShot(3000, prepare)
    QTimer.singleShot(45000, capture)
    QTimer.singleShot(50000, window.close)
    result = app.exec()
    manager.stop(); manager.join(30)
    report['clean_shutdown'] = not manager.running and not window.sky.running and not window.file_manager.running
    Path('reports/sky-ui.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
