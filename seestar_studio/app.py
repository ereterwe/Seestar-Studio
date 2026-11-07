from .i18n import QMessageBox
from .i18n import source as ui_text, tr
from .i18n import TranslationController
import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
import uuid
from PySide6.QtCore import QStandardPaths, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from .manager import TelescopeManager
from .settings import SettingsService
from .theme import STYLE
from .window import DashboardWindow
from .setup_service import SetupService
from .instance import InstanceLock

def main():
    parser = argparse.ArgumentParser(description='Seestar Studio — local observatory, read-only by default')
    parser.add_argument('--smoke-seconds', type=int, default=0, help='Close automatically after this many seconds')
    parser.add_argument('--capture', help='Save an application-rendered QA screenshot (PNG)')
    parser.add_argument('--capture-after', type=int, default=45)
    parser.add_argument('--window-size', help='Initial QA window size, e.g. 1920x1080')
    parser.add_argument('--qa-sky', action='store_true', help='QA only: synthetic site in memory, never stored')
    parser.add_argument('--capture-all-tabs', action='store_true', help='QA: capture each native tab alongside the main screenshot')
    args = parser.parse_args()
    from .branding import set_windows_identity, app_icon
    set_windows_identity()
    app = QApplication(sys.argv[:1])
    app.setWindowIcon(app_icon())
    app.setApplicationName('Seestar Studio')
    app.setOrganizationName('SeestarStudio')
    app.setFont(QFont('Segoe UI', 10))
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    instance_lock = InstanceLock('Local\\SeestarStudio.QA.'+uuid.uuid4().hex) if args.qa_sky and args.smoke_seconds else InstanceLock()
    if instance_lock.already_running:
        QMessageBox.information(None, 'Seestar Studio', ui_text('m0000'))
        instance_lock.close()
        return 0
    log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)) / 'logs'
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(log_dir / 'studio.log', maxBytes=1000000, backupCount=3, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logging.getLogger('seestar_studio').addHandler(handler)
        logging.getLogger('seestar_studio').setLevel(logging.INFO)
    except OSError:
        pass
    manager = TelescopeManager()
    qa_settings = Path('reports') / ('exe-qa-profile-'+uuid.uuid4().hex[:8]) / 'settings.json' if args.qa_sky else None
    settings = SettingsService(qa_settings)
    app.translations = TranslationController(app, settings.values['language'])
    setup = SetupService(settings.path.parent / 'authentication')
    reference = setup.configure_runtime()
    window = DashboardWindow(manager, settings, setup_service=setup)
    if args.window_size:
        try:
            width, height = map(int, args.window_size.lower().split('x'))
        except ValueError:
            parser.error('--window-size expects WIDTHxHEIGHT')
        window.resize(max(900, min(width, 7680)), max(650, min(height, 4320)))
    window.show()
    manager.start()
    if reference is None and (not settings.values['setup_seen']):
        QTimer.singleShot(800, window.open_setup)
    if args.qa_sky:
        from .sky.astronomy import Site

        def prepare_sky():
            window.tabs.setCurrentWidget(window.sky)
            window.sky.site = Site(52, 13, 40, 'Europe/Berlin')
            window.sky.search.setText('M31')
            window.sky.request_calculation()
        QTimer.singleShot(3000, prepare_sky)
    if args.capture:

        def capture():
            path = Path(args.capture)
            path.parent.mkdir(parents=True, exist_ok=True)
            window.grab().save(str(path))
            values, _ = manager.latest()
            report = {'frozen_executable': bool(getattr(sys, 'frozen', False)), 'window_size': [window.width(), window.height()], 'devices': {}}
            report['catalog_count'] = len(window.sky.catalog.targets) if window.sky.catalog else None
            report['sky_calculated'] = window.sky.night is not None
            report['synthetic_site_qa'] = args.qa_sky
            report['tabs'] = [window.tabs.tabText(i) for i in range(window.tabs.count())]
            report['control_enabled'] = window.control.service.enabled
            report['solar_background_ready'] = window.planner.timeline.solar is not None
            report['solar_event_count'] = len(window.planner.timeline.solar.events) if window.planner.timeline.solar else 0
            from .metadata import public_versions, local_references
            report['versions'] = public_versions()
            report['icon_available'] = not app.windowIcon().isNull()
            report['local_reference_names'] = list(local_references())
            try:
                from winrt.windows.devices.geolocation import Geolocator
                import winrt.windows.foundation
                report['windows_location_module_available'] = True
            except ImportError:
                report['windows_location_module_available'] = False
            report['windows_location_requested'] = False
            for sn, (info, telemetry, frame) in values.items():
                report['devices'][sn] = {'model': info.model, 'telemetry': telemetry.values, 'frame': None if frame is None else {'kind': frame.kind, 'format': frame.source_format, 'sequence': frame.sequence, 'size': [frame.image.width(), frame.image.height()]}}
            path.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            if args.capture_all_tabs:
                original = window.tabs.currentIndex()
                for index in range(window.tabs.count()):
                    window.tabs.setCurrentIndex(index)
                    app.processEvents()
                    window.grab().save(str(path.with_name(f'{path.stem}-tab{index}.png')))
                window.tabs.setCurrentIndex(original)
                if args.qa_sky:
                    from .about import AboutDialog
                    from .sky.site import SiteDialog
                    for dialog in (AboutDialog(window), SiteDialog({},window)):
                        if isinstance(dialog, SiteDialog):
                            # Deliberately simulated failure; no Windows query.
                            dialog.show_windows_error('denied')
                            from PySide6.QtGui import QDesktopServices
                            original_open = QDesktopServices.openUrl
                            dispatched = []
                            try:
                                QDesktopServices.openUrl = lambda url: dispatched.append(url.toString()) or True
                                dialog.location_settings.click()
                            finally:
                                QDesktopServices.openUrl = original_open
                            report['location_settings_simulated_uri'] = dispatched
                        dialog.show();app.translations.refresh();app.processEvents()
                        dialog.grab().save(str(path.with_name(f'{path.stem}-{type(dialog).__name__}.png')))
                        dialog.reject();dialog.deleteLater()
                path.with_suffix('.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        QTimer.singleShot(args.capture_after * 1000, capture)
    if args.smoke_seconds:
        QTimer.singleShot(args.smoke_seconds * 1000, window.close)
    result = app.exec()
    manager.stop()
    manager.join(40)
    if args.capture:
        report_path = Path(args.capture).with_suffix('.json')
        try:
            report = json.loads(report_path.read_text(encoding='utf-8'))
            report['clean_shutdown'] = not window.workers_running()
            report['application_exit_code'] = result
            report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        except (OSError, ValueError):
            pass
    instance_lock.close()
    return result
