from .i18n import QFileDialog, QMessageBox
from .i18n import source as ui_text, tr
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QTabWidget
from .card import TelescopeCard, label, button
from .files.widget import FileManagerWidget
from .sky.widget import SkyExplorerWidget
from .control_widget import ControlWidget
from .planner_widget import PlannerWidget
from .history import HistoryService
from .history_widget import HistoryWidget
from .setup_service import SetupService
from .setup_wizard import SetupWizard
from .diagnostics import DiagnosticsDialog, diagnostic_snapshot
from . import __version__

class DashboardWindow(QMainWindow):

    def __init__(self, manager, settings, file_browser=None, downloads=None, setup_service=None):
        super().__init__()
        self.manager, self.settings = (manager, settings)
        self.setup_service = setup_service or SetupService(settings.path.parent / 'authentication')
        self._setup_dialogs = []
        self.cards = {}
        self.order = list(settings.values['order'])
        self.maximized_card = None
        self._layout_key = None
        self._closing = False
        self._export_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-export')
        self._exports = []
        self.setWindowTitle('Telescope Desk')
        size = settings.values['size']
        if len(size) != 2 or not all((isinstance(v, int) for v in size)):
            size = [1600, 960]
        self.resize(max(900, min(size[0], 7680)), max(650, min(size[1], 4320)))
        self.setMinimumSize(900, 650)
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(24, 18, 24, 10)
        outer.setSpacing(16)
        header = QHBoxLayout()
        brand = QVBoxLayout()
        brand.setSpacing(3)
        brand.addWidget(label('TELESCOPE DESK', 'brand'))
        brand.addWidget(label(ui_text('m0439'), 'eyebrow'))
        header.addLayout(brand)
        header.addStretch()
        self.fleet_status = label(ui_text('m0256'), 'muted')
        header.addWidget(self.fleet_status)
        scan = button(ui_text('m0257'), manager.request_scan, ui_text('m0258'))
        scan.setObjectName('primary')
        header.addWidget(scan)
        header.addWidget(button(ui_text('m0264'), self.toggle_fullscreen))
        header.addWidget(button('Info', self.show_about))
        header.addWidget(button(ui_text('m0239'), self.open_setup))
        header.addWidget(button(ui_text('m0083'), self.open_diagnostics))
        header.addWidget(button(ui_text('settings.title'), self.open_preferences))
        outer.addLayout(header)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.grid = QGridLayout(self.content)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(16)
        self.scroll.setWidget(self.content)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.scroll, ui_text('m0432'))
        self.file_manager = FileManagerWidget(settings, file_browser, downloads)
        self.tabs.addTab(self.file_manager, ui_text('m0433'))
        self.sky = SkyExplorerWidget(settings, devices=lambda: self.manager.latest()[0])
        self.sky.observe_requested.connect(self.observe_target)
        self.sky.plan_requested.connect(self.plan_target)
        self.tabs.addTab(self.sky, ui_text('m0434'))
        self.control = ControlWidget()
        self.tabs.addTab(self.control, ui_text('m0398'))
        self.planner = PlannerWidget(self.sky, settings)
        self.tabs.addTab(self.planner, ui_text('m0435'))
        self.history_service = HistoryService(settings.path.parent / 'history.sqlite3')
        self.history = HistoryWidget(self.history_service)
        self.tabs.addTab(self.history, ui_text('m0397'))
        outer.addWidget(self.tabs, 1)
        self.empty = label(ui_text('m0259'), 'muted')
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid.addWidget(self.empty, 0, 0)
        self.setCentralWidget(root)
        self.mode_label = label(ui_text('m0260'), 'muted')
        self.statusBar().addPermanentWidget(self.mode_label)
        self.control.mode_changed.connect(lambda enabled: self.mode_label.setText((ui_text('m0272') if enabled else ui_text('m0437')) + ui_text('m0268')))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(500)
        QShortcut(QKeySequence('F11'), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence('Escape'), self, activated=self.escape)
        QShortcut(QKeySequence('Ctrl+R'), self, activated=manager.request_scan)
        from PySide6.QtWidgets import QApplication
        controller=getattr(QApplication.instance(),'translations',None)
        if controller:controller.language_changed.connect(self.retranslate)

    def retranslate(self):
        self.refresh()
        if self.sky.target:self.sky.select_target()
        if self.sky.night and self.sky.site:self.sky.show_night()
        self.planner.refresh_library();self.planner.redraw();self.history.refresh()

    def refresh(self):
        for dialog in list(self._setup_dialogs):
            if dialog._disposed and (not dialog.isVisible()):
                self._setup_dialogs.remove(dialog)
                dialog.deleteLater()
        if self._closing:
            if not self.workers_running() and (not self._exports):
                self.close()
            else:
                self._check_exports()
            return
        data, message = self.manager.latest()
        self.file_manager.sync_devices(data)
        self.control.sync_devices(data)
        self.planner.sync_devices(data)
        self.history_service.submit(data)
        for sn, (info, telemetry, frame) in data.items():
            if sn not in self.cards:
                card = TelescopeCard(info, bool(self.settings.values['details'].get(sn)))
                card.maximize_requested.connect(self.maximize_card)
                card.move_requested.connect(self.move_card)
                card.pause_requested.connect(self.manager.set_paused)
                card.save_requested.connect(self.save_frame)
                card.details_changed.connect(self.details_changed)
                card.source_changed.connect(self.source_changed)
                if self.settings.values['view_modes'].get(sn) == 'video':
                    card.source.setCurrentIndex(1)
                self.cards[sn] = card
                if sn not in self.order:
                    self.order.append(sn)
            self.cards[sn].update_data(info, telemetry, frame)
        connected = sum((1 for _, telemetry, _ in data.values() if telemetry.connected))
        self.fleet_status.setText(ui_text('window.connected').format(p0=connected,p1=len(data)))
        self.statusBar().showMessage(message)
        self.arrange()
        self._check_exports()

    def arrange(self):
        visible = [sn for sn in self.order if sn in self.cards and (not self.maximized_card or sn == self.maximized_card)]
        count = len(visible)
        columns = 1 if count < 2 else min(3, max(1, self.scroll.viewport().width() // 570), math.ceil(math.sqrt(count)))
        key = (tuple(visible), columns)
        if key != self._layout_key:
            while self.grid.count():
                self.grid.takeAt(0)
            self.empty.setVisible(not self.cards)
            for card in self.cards.values():
                card.hide()
            for row in range(self.grid.rowCount()):
                self.grid.setRowStretch(row, 0)
                self.grid.setRowMinimumHeight(row, 0)
            for col in range(self.grid.columnCount()):
                self.grid.setColumnStretch(col, 0)
            if not count:
                self.grid.addWidget(self.empty, 0, 0)
            for index, sn in enumerate(visible):
                card = self.cards[sn]
                self.grid.addWidget(card, index // columns, index % columns)
                card.max_button.setText(ui_text('m0269') if self.maximized_card else ui_text('m0010'))
                card.show()
                self.grid.setColumnStretch(index % columns, 1)
                self.grid.setRowStretch(index // columns, 1)
            self._layout_key = key
        rows = max(1, math.ceil(count / columns))
        height = max(580, (self.scroll.viewport().height() - (rows - 1) * 16) // rows)
        for sn in visible:
            self.cards[sn].setMinimumHeight(height)

    def observe_target(self, target):
        self.control.set_target(target)
        self.tabs.setCurrentWidget(self.control)

    def plan_target(self, target):
        self.tabs.setCurrentWidget(self.planner)
        self.planner.add_target(target)

    def workers_running(self):
        return any((self.manager.running, self.file_manager.running, self.sky.running, self.control.running, self.planner.running, self.history.running, self.history_service.running, any((dialog.running for dialog in self._setup_dialogs)), any((card.video and card.video.running for card in self.cards.values()))))

    def source_changed(self, serial, source):
        self.settings.values['view_modes'][serial] = source
        try:
            self.settings.save()
        except OSError:
            pass

    def open_setup(self):
        for dialog in self._setup_dialogs:
            if dialog.isVisible():
                dialog.raise_()
                dialog.activateWindow()
                return
        dialog = SetupWizard(self.setup_service.profile, lambda: self.manager.latest()[0], self)
        self._setup_dialogs.append(dialog)

        def finished():
            self.settings.values['setup_seen'] = True
            try:
                self.settings.save()
            except OSError:
                pass
        dialog.finished.connect(finished)
        dialog.open()

    def open_diagnostics(self):
        snapshot = diagnostic_snapshot(self.manager.latest()[0], self.setup_service.active() is not None, self.history_service.error)
        dialog = DiagnosticsDialog(snapshot, self)
        dialog.exec()

    def open_preferences(self):
        from .preferences import PreferencesDialog
        PreferencesDialog(self.settings, self).exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'scroll'):
            self.arrange()

    def maximize_card(self, sn):
        self.maximized_card = None if self.maximized_card == sn else sn
        self.arrange()

    def move_card(self, sn, direction):
        index = self.order.index(sn)
        other = index + direction
        if 0 <= other < len(self.order):
            self.order[index], self.order[other] = (self.order[other], self.order[index])
            self.settings.values['order'] = self.order
            self.arrange()

    def details_changed(self, sn, visible):
        self.settings.values['details'][sn] = visible

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def show_about(self):
        from .about import AboutDialog
        AboutDialog(self).exec()

    def escape(self):
        if self.isFullScreen():
            self.showNormal()
        elif self.maximized_card:
            self.maximized_card = None
            self.arrange()

    def save_frame(self, sn):
        frame = self.cards[sn].current_frame()
        if frame is None:
            return
        name = f'Seestar_{sn}_{datetime.now():%Y%m%d_%H%M%S}.png'
        path, _ = QFileDialog.getSaveFileName(self, ui_text('m0263'), str(Path.home() / 'Pictures' / name), 'PNG (*.png);;JPEG (*.jpg)')
        if path:
            if not Path(path).suffix:
                path += '.png'
            image = frame.image
            self._exports.append((self._export_pool.submit(image.save, path), path))

    def _check_exports(self):
        for future, path in list(self._exports):
            if future.done():
                try:
                    ok = future.result()
                except Exception:
                    ok = False
                self._exports.remove((future, path))
                if not ok:
                    QMessageBox.warning(self, ui_text('m0009'), ui_text('m0270'))
                else:
                    self.statusBar().showMessage(ui_text('m0271').format(p0=f'{path}'), 5000)

    def closeEvent(self, event):
        if not self._closing:
            if self.control.service._transports:
                answer = QMessageBox.question(self, ui_text('m0266'), ui_text('m0267'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes:
                    event.ignore()
                    return
            self._closing = True
            if not self.isFullScreen() and (not self.isMaximized()):
                self.settings.values['size'] = [self.width(), self.height()]
            self.settings.values['order'] = self.order
            try:
                self.settings.save()
            except OSError:
                pass
            self.manager.stop()
            self.file_manager.stop()
            self.sky.stop()
            self.control.stop()
            self.planner.stop()
            self.history.stop()
            self.history_service.stop()
            for dialog in self._setup_dialogs:
                dialog.reject()
            for card in self.cards.values():
                card.stop_video()
            self.centralWidget().setEnabled(False)
            self.statusBar().showMessage(ui_text('m0265'))
        if self.workers_running() or self._exports:
            event.ignore()
        else:
            self.timer.stop()
            self._export_pool.shutdown(wait=False)
            event.accept()
