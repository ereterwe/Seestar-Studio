from ..i18n import QMessageBox
from ..i18n import source as ui_text, tr
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from PySide6.QtCore import Qt, QTimer, QDate, QRectF, Signal
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox, QDateEdit, QScrollArea
from ..card import label, button
from ..plots import LinePlot
from ..telemetry import number
from .catalog import Catalog, TYPES
from .astronomy import Site, CAMERAS, calculate

class FieldOfView(QWidget):

    def __init__(self):
        super().__init__()
        self.target, self.camera = (None, CAMERAS[0])
        self.setMinimumHeight(200)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.camera.fov
        target_w = (self.target.minor or self.target.major or 0) / 60 if self.target else 0
        target_h = (self.target.major or 0) / 60 if self.target else 0
        scale = min((self.width() - 40) / max(w, target_w, 0.1), (self.height() - 40) / max(h, target_h, 0.1))
        cx, cy = (self.width() / 2, self.height() / 2)
        p.setPen(QPen(QColor('#5cd6a3'), 2))
        p.drawRect(QRectF(cx - w * scale / 2, cy - h * scale / 2, w * scale, h * scale))
        if target_w and target_h:
            p.setPen(QPen(QColor('#e6ad63'), 2))
            p.setBrush(QColor(230, 173, 99, 28))
            p.drawEllipse(QRectF(cx - target_w * scale / 2, cy - target_h * scale / 2, target_w * scale, target_h * scale))

from .site import SiteDialog

class SkyExplorerWidget(QWidget):
    observe_requested = Signal(object)
    plan_requested = Signal(object)

    def __init__(self, settings, devices=None):
        super().__init__()
        self.settings = settings
        self.devices = devices or (lambda: {})
        self._site_dialog = None
        self.catalog, self.target, self.night, self.site = (None, None, None, None)
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-sky')
        self._catalog_future = self._pool.submit(Catalog)
        self._calculation = None
        self._generation = 0
        self._pending = False
        self._stopped = False
        try:
            self.site = Site(**settings.values.get('site', {}))
        except (TypeError, ValueError, ZoneInfoNotFoundError):
            pass
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(ui_text('m0358'))
        self.collection = QComboBox()
        self.collection.addItems([ui_text('m0346'), 'Messier', 'Caldwell'])
        bar.addWidget(self.search, 1)
        bar.addWidget(self.collection)
        bar.addWidget(button(ui_text('m0372'), self.configure_site))
        bar.addWidget(button(ui_text('m0373'), self.clear_site))
        local_date = datetime.now(ZoneInfo(self.site.timezone)).date() if self.site else datetime.now().date()
        self.date = QDateEdit(QDate(local_date.year, local_date.month, local_date.day))
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat('dd.MM.yyyy')
        bar.addWidget(self.date)
        bar.addWidget(button(ui_text('m0374'), self.request_calculation))
        layout.addLayout(bar)
        self.status = label(ui_text('m0359'), 'muted')
        layout.addWidget(self.status)
        split = QSplitter()
        self.results = QTableWidget(0, 3)
        self.results.setHorizontalHeaderLabels([ui_text('m0375'), ui_text('m0314'), ui_text('m0376')])
        self.results.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results.verticalHeader().hide()
        split.addWidget(self.results)
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail = QWidget()
        right = QVBoxLayout(detail)
        self.title = label(ui_text('m0360'), 'brand')
        self.details = label('', 'muted')
        self.details.setWordWrap(True)
        self.visibility = label(ui_text('m0361'), 'muted')
        self.visibility.setWordWrap(True)
        right.addWidget(self.title)
        right.addWidget(self.details)
        self.camera = QComboBox()
        self.camera.addItems([c.name for c in CAMERAS])
        right.addWidget(self.camera)
        self.fov = FieldOfView()
        right.addWidget(self.fov)
        self.fov_text = label('', 'muted')
        self.fov_text.setWordWrap(True)
        right.addWidget(self.fov_text)
        right.addWidget(self.visibility)
        right.addWidget(label(ui_text('m0377'), 'eyebrow'))
        self.plot = LinePlot()
        right.addWidget(self.plot)
        actions = QHBoxLayout()
        self.observe = button(ui_text('m0362'), self.request_observe)
        self.plan = button(ui_text('m0363'), lambda: self.plan_requested.emit(self.target))
        self.observe.setEnabled(False)
        self.plan.setEnabled(False)
        actions.addWidget(self.observe)
        actions.addWidget(self.plan)
        right.addLayout(actions)
        detail_scroll.setWidget(detail)
        split.addWidget(detail_scroll)
        split.setSizes([550, 850])
        layout.addWidget(split, 1)
        layout.addWidget(label(ui_text('m0378'), 'muted'))
        self.search.textChanged.connect(self.update_results)
        self.collection.currentTextChanged.connect(self.update_results)
        self.results.itemSelectionChanged.connect(self.select_target)
        self.camera.currentIndexChanged.connect(self.update_fov)
        self.date.dateChanged.connect(self.request_calculation)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(150)
        self.update_fov()

    @property
    def running(self):
        return (self._catalog_future is not None and (not self._catalog_future.done())
                or (self._calculation is not None and (not self._calculation[1].done()))
                or bool(self._site_dialog and self._site_dialog.running))

    def stop(self):
        self._stopped = True
        self._pending = False
        if self._site_dialog:
            self._site_dialog.reject()
        self._pool.shutdown(wait=False, cancel_futures=True)

    def update_results(self):
        if self.catalog is None:
            return
        self.matches = self.catalog.search(self.search.text(), self.collection.currentText())
        self.results.setRowCount(0)
        for row, target in enumerate(self.matches):
            self.results.insertRow(row)
            for col, value in enumerate((target.title, TYPES.get(target.kind, target.kind), target.constellation)):
                self.results.setItem(row, col, QTableWidgetItem(value))
        self.status.setText(ui_text('m0364').format(p0=number(len(self.catalog.targets)), p1=f'{len(self.matches)}'))
        if self.matches:
            self.results.selectRow(0)

    def select_target(self):
        row = self.results.currentRow()
        if not 0 <= row < len(getattr(self, 'matches', [])):
            return
        self.target = self.matches[row]
        t = self.target
        self.title.setText(t.title)
        self.details.setText(ui_text('m0365').format(p0=f'{t.description}', p1=f"{number(t.ra, '°', 5)}", p2=f"{number(t.dec, '°', 5)}", p3=f"{number(t.major, '′', 1)}", p4=f"{number(t.minor, '′', 1)}", p5=f"{number(t.magnitude, ' mag', 2)}", p6=f'{t.band}', p7=f'{t.suitability}', p8=f"{', '.join(t.aliases)}"))
        self.observe.setEnabled(t.valid)
        self.plan.setEnabled(t.valid)
        self.update_fov()
        self.request_calculation()

    def update_fov(self):
        self.fov.camera = CAMERAS[self.camera.currentIndex()]
        self.fov.target = self.target
        self.fov.update()
        w, h = self.fov.camera.fov
        self.fov_text.setText(ui_text('m0366').format(p0=number(w,digits=2), p1=number(h,digits=2)))

    def configure_site(self):
        dialog = SiteDialog(asdict(self.site) if self.site else {}, self, devices=self.devices)
        self._site_dialog = dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.site = dialog.site
            self.settings.values['site'] = asdict(self.site)
            self.save_site()
            local = datetime.now(ZoneInfo(self.site.timezone))
            self.date.setDate(QDate(local.year, local.month, local.day))
            self.request_calculation()

    def clear_site(self):
        self.site = None
        self.settings.values['site'] = {}
        self.save_site()
        self.request_calculation()

    def save_site(self):
        try:
            self.settings.save()
        except OSError:
            QMessageBox.warning(self, ui_text('m0417'), ui_text('m0383'))

    def request_calculation(self):
        self._generation += 1
        self.night = None
        self.plot.set_series([])
        self._pending = bool(self.site and self.target and self.target.valid)
        self.visibility.setText(ui_text('m0379') if self._pending else ui_text('m0380'))

    def request_observe(self):
        if self.target and self.target.valid:
            self.observe_requested.emit(self.target)

    def poll(self):
        if self._stopped:
            return
        if self._catalog_future is not None and self._catalog_future.done():
            try:
                self.catalog = self._catalog_future.result()
                self.update_results()
            except Exception:
                self.status.setText(ui_text('m0384'))
            self._catalog_future = None
        if self._calculation and self._calculation[1].done():
            generation, future = self._calculation
            self._calculation = None
            if generation == self._generation:
                try:
                    self.night = future.result()
                    self.show_night()
                except Exception:
                    self.visibility.setText(ui_text('m0385'))
        if self._pending and self._calculation is None:
            self._pending = False
            self._calculation = (self._generation, self._pool.submit(calculate, self.target, self.site, self.date.date().toPython()))

    def show_night(self):
        n, tz = (self.night, ZoneInfo(self.site.timezone))
        from ..timezones import local_text
        stamp = lambda t: local_text(t, self.site.timezone)
        ranges = lambda pairs: '; '.join((f'{stamp(a)} – {stamp(b)}' for a, b in pairs)) or ui_text('m0381')
        self.visibility.setText(ui_text('m0367').format(p0=number(n.current_alt,digits=1), p1=number(n.current_az,digits=1), p2=number(n.current_moon,digits=1), p3=f"{', '.join(map(stamp, n.rise)) or ui_text('sky.no_crossing')}", p4=f"{', '.join(map(stamp, n.setting)) or ui_text('sky.no_crossing')}", p5=f'{stamp(n.transit)}', p6=f'{ranges(n.dark_windows)}', p7=f'{ranges(n.windows)}', p8=f'{n.warning}'))
        self.plot.set_series([(n.altitude, '#5cd6a3'), (n.sun_altitude, '#e6ad63')], (stamp(n.times[0]), stamp(n.times[-1])))
