"""Application-internal native UI QA with real read-only hardware."""
import json
from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from telescope_desk.manager import TelescopeManager
from telescope_desk.settings import SettingsService
from telescope_desk.window import DashboardWindow
from telescope_desk.theme import STYLE


def main():
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Telescope Desk'); app.setOrganizationName('TelescopeDesk')
    app.setStyle('Fusion'); app.setStyleSheet(STYLE)
    manager = TelescopeManager()
    window = DashboardWindow(manager, SettingsService())
    window.resize(1920, 1080)
    window.show()
    manager.start()
    report = {}
    def prepare():
        data, _ = manager.latest()
        if data:
            serial = sorted(data)[0]
            window.tabs.setCurrentIndex(1)
            window.file_manager.show_path(serial, 'MyWorks')
    def capture():
        window.grab().save('reports/file-manager.png')
        report['file_rows'] = window.file_manager.files.topLevelItemCount()
        report['devices'] = list(window.file_manager.devices)
        report['file_message'] = window.file_manager.message.text()
        window.tabs.setCurrentIndex(0)
        QTimer.singleShot(1000, lambda: window.grab().save('reports/phase1-dashboard.png'))
    QTimer.singleShot(15000, prepare)
    QTimer.singleShot(45000, capture)
    QTimer.singleShot(55000, window.close)
    result = app.exec()
    manager.stop(); manager.join(30)
    report['clean_shutdown'] = not manager.running and not window.file_manager.running
    Path('reports/file-ui.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
