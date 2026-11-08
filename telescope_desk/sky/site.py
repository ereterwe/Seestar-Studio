"""Location proposals remain in the dialog until explicit confirmation."""
from concurrent.futures import ThreadPoolExecutor
import threading
from zoneinfo import ZoneInfoNotFoundError
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QLineEdit, QComboBox, QHBoxLayout, QDialogButtonBox
from ..i18n import QMessageBox, source as ui_text
from ..card import label, button
from ..telemetry import number
from ..timezones import system_timezone
from ..location import LocationProposal, WindowsLocationRequest, read_seestar_location
from .astronomy import Site

WINDOWS_ERRORS = {'denied': ui_text('location.denied'), 'disabled': ui_text('location.disabled'),
                 'no_data': ui_text('location.no_data'), 'failed': ui_text('location.failed'),
                 'timeout': ui_text('location.timeout'), 'unsupported': ui_text('location.unsupported')}


class SiteDialog(QDialog):
    def __init__(self, values, parent=None, devices=None, windows_factory=WindowsLocationRequest, scope_reader=read_seestar_location):
        super().__init__(parent)
        self.setWindowTitle(ui_text('m0355'))
        self.resize(720, 480)
        self.source = None
        self._closed = False
        self._stopped = threading.Event()
        self._future = None
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-location')
        self.scope_reader = scope_reader
        self.devices = devices or (lambda: {})
        self.windows = windows_factory(self)
        self.windows.proposal.connect(self.apply_proposal)
        self.windows.failed.connect(self.show_windows_error)
        layout = QVBoxLayout(self)
        note = label(ui_text('location.intro'), 'muted'); note.setWordWrap(True)
        layout.addWidget(note)
        actions = QHBoxLayout()
        self.windows_button = button(ui_text('location.windows'), self.request_windows)
        actions.addWidget(self.windows_button)
        actions.addWidget(button(ui_text('location.manual'), self.manual))
        layout.addLayout(actions)
        sources = QHBoxLayout()
        self.scopes = QComboBox()
        for serial, (info, telemetry, _) in self.devices().items():
            if telemetry.connected and not telemetry.paused:
                self.scopes.addItem(info.model + ' · ' + serial, info)
        sources.addWidget(self.scopes, 1)
        self.scope_button = button(ui_text('location.seestar'), self.request_scope)
        self.scope_button.setEnabled(self.scopes.count() > 0)
        sources.addWidget(self.scope_button)
        layout.addLayout(sources)
        self.status = label(ui_text('location.manual_note'), 'muted')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.location_settings = button(ui_text('location.open_settings'), self.open_location_settings)
        self.location_settings.hide()
        layout.addWidget(self.location_settings)
        form = QFormLayout()
        self.lat, self.lon, self.height = QDoubleSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()
        for widget, low, high, key in ((self.lat,-90,90,'latitude'),(self.lon,-180,180,'longitude'),(self.height,-500,10000,'elevation')):
            widget.setRange(low, high)
            widget.setDecimals(5 if key != 'elevation' else 0)
            widget.setValue(values.get(key, 0))
            widget.valueChanged.connect(self.edited)
        self.zone = QLineEdit(values.get('timezone') or system_timezone())
        for title, widget in ((ui_text('m0369'),self.lat),(ui_text('m0370'),self.lon),(ui_text('m0371'),self.height),(ui_text('m0153'),self.zone)):
            form.addRow(title, widget)
        layout.addLayout(form)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(ui_text('m0357'))
        self.buttons.accepted.connect(self.validate); self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.timer = QTimer(self); self.timer.timeout.connect(self.poll); self.timer.start(100)
        self.finished.connect(self.cleanup)

    @property
    def running(self):
        return self._future is not None and not self._future.done()

    def show_error(self, message):
        if not self._closed:
            self.location_settings.hide()
            self.status.setText(message)
            self.windows_button.setEnabled(True)

    def show_windows_error(self, code):
        if self._closed: return
        if code not in {'denied', 'disabled', 'no_data', 'failed', 'timeout', 'unsupported'}:
            code = 'failed'
        self.show_error(WINDOWS_ERRORS[code])
        self.location_settings.setVisible(code in {'denied', 'disabled'})

    def open_location_settings(self):
        # Only a user button action; never changes permissions or retries a query.
        try:
            opened = QDesktopServices.openUrl(QUrl('ms-settings:privacy-location'))
        except Exception:
            opened = False
        if not opened:
            self.status.setText(ui_text('location.settings_failed'))

    def manual(self):
        self.location_settings.hide()
        self.windows.cancel()
        self.source = None
        # Any in-flight telescope reply becomes ineligible to replace manual edits.
        self._accept_scope = False
        self.windows_button.setEnabled(True)
        self.status.setText(ui_text('location.manual_note'))

    def edited(self):
        if hasattr(self, 'status'):
            self.location_settings.hide()
            self.windows.cancel()
            self._accept_scope = False
            self.windows_button.setEnabled(True)
            self.status.setText(ui_text('location.edited') if self.source else ui_text('location.manual_note'))

    def request_windows(self):
        if QMessageBox.question(self, ui_text('location.consent_title'), ui_text('location.consent'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self._accept_scope = False
        self.location_settings.hide()
        self.windows_button.setEnabled(False)
        self.status.setText(ui_text('location.waiting'))
        self.windows.start()

    def request_scope(self):
        if self.running:
            return
        info = self.scopes.currentData()
        if info is None:
            return
        self.windows.cancel()
        self.location_settings.hide()
        self.windows_button.setEnabled(True)
        self._accept_scope = True
        self.scope_button.setEnabled(False)
        self.status.setText(ui_text('location.waiting'))
        self._future = self._pool.submit(self.scope_reader, info, self._stopped)

    def poll(self):
        if self._closed or self._future is None or not self._future.done():
            return
        future, self._future = self._future, None
        self.scope_button.setEnabled(self.scopes.count() > 0)
        if not self._accept_scope:
            return
        try:
            self.apply_proposal(future.result())
        except Exception:
            self.show_error(ui_text('location.scope_failed'))

    def apply_proposal(self, value):
        if self._closed:
            return
        if not isinstance(value, LocationProposal):
            self.show_error(ui_text('location.invalid')); return
        self.source = value
        self.location_settings.hide()
        for widget, number_value in ((self.lat,value.latitude),(self.lon,value.longitude),(self.height,value.elevation)):
            if number_value is not None:
                widget.blockSignals(True); widget.setValue(number_value); widget.blockSignals(False)
        lines = [ui_text('location.source_scope') if value.source == 'seestar' else ui_text('location.source_windows')]
        if value.accuracy is not None:
            distance = number(value.accuracy/1000,' km',1) if value.accuracy >= 1000 else number(value.accuracy,' m')
            lines.append(ui_text('location.accuracy').format(p0=distance))
            if value.accuracy >= 1000: lines.append(ui_text('location.approximate'))
        else:
            lines.append(ui_text('location.unknown_accuracy'))
        if value.elevation is None: lines.append(ui_text('location.no_height'))
        lines.append(ui_text('location.suggestion'))
        self.status.setText('\n'.join(lines))
        self.windows_button.setEnabled(True)

    def validate(self):
        try:
            self.site = Site(self.lat.value(), self.lon.value(), self.height.value(), self.zone.text().strip())
        except (ValueError, ZoneInfoNotFoundError):
            QMessageBox.warning(self, ui_text('m0417'), ui_text('m0382')); return
        self.accept()

    def cleanup(self, *_):
        self._closed = True
        self.windows.cancel(); self.timer.stop(); self._stopped.set()
        self._pool.shutdown(wait=False, cancel_futures=True)
