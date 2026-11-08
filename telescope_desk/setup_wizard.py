from .i18n import QFileDialog, QMessageBox
from .i18n import source as ui_text, tr
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QCheckBox, QComboBox
from .card import label, button
from .setup_service import SetupService, SetupError

class ImportPage(QWizardPage):

    def isComplete(self):
        wizard = self.wizard()
        if wizard is None or not hasattr(wizard, 'keep'):
            return False
        return wizard.keep.isChecked() and wizard.original is not None or bool(wizard.candidates)

class SetupWizard(QWizard):
    """Local, explicit onboarding; existing files are never overwritten."""

    def __init__(self, profile, devices, parent=None, service=None):
        super().__init__(parent)
        self.service = service or SetupService(profile)
        self.devices_provider = devices
        self.original = self.service.active()
        self.candidates = []
        self.verified_path = None
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-setup')
        self._future = None
        self._closing = False
        self._disposed = False
        self.setWindowTitle(ui_text('m0203'))
        self.setMinimumSize(780, 560)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setButtonText(QWizard.WizardButton.NextButton, ui_text('m0204'))
        self.setButtonText(QWizard.WizardButton.BackButton, ui_text('m0205'))
        self.setButtonText(QWizard.WizardButton.FinishButton, ui_text('m0206'))
        self.setButtonText(QWizard.WizardButton.CancelButton, ui_text('m0207'))
        intro = QWizardPage()
        intro.setTitle(ui_text('m0208'))
        layout = QVBoxLayout(intro)
        layout.addWidget(label(ui_text('m0226'), 'muted'))
        description = ui_text('m0237') + self.original.origin + '\n' + str(self.original.path) if self.original else ui_text('m0209')
        self.existing = label(description, 'device')
        self.existing.setWordWrap(True)
        layout.addWidget(self.existing)
        layout.addWidget(label(ui_text('m0227'), 'muted'))
        self.keep = QCheckBox(ui_text('m0210'))
        self.keep.setChecked(self.original is not None)
        self.keep.setEnabled(self.original is not None)
        layout.addWidget(self.keep)
        layout.addStretch()
        self.addPage(intro)
        self.import_page = ImportPage()
        self.import_page.setTitle(ui_text('m0211'))
        layout = QVBoxLayout(self.import_page)
        note = label(ui_text('m0212'), 'muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        self.rights = QCheckBox(ui_text('m0213'))
        layout.addWidget(self.rights)
        self.import_button = button(ui_text('m0214'), self.choose_import)
        layout.addWidget(self.import_button)
        self.candidate_combo = QComboBox()
        layout.addWidget(self.candidate_combo)
        self.import_status = label(ui_text('m0215'), 'muted')
        self.import_status.setWordWrap(True)
        layout.addWidget(self.import_status)
        layout.addStretch()
        self.addPage(self.import_page)
        check = QWizardPage()
        check.setTitle(ui_text('m0216'))
        layout = QVBoxLayout(check)
        text = label(ui_text('m0217'), 'muted')
        text.setWordWrap(True)
        layout.addWidget(text)
        self.devices = QComboBox()
        layout.addWidget(self.devices)
        self.check_button = button(ui_text('m0218'), self.check_connection)
        layout.addWidget(self.check_button)
        self.check_status = label(ui_text('m0219'), 'muted')
        self.check_status.setWordWrap(True)
        layout.addWidget(self.check_status)
        layout.addStretch()
        self.addPage(check)
        self.keep.toggled.connect(self.selection_changed)
        self.candidate_combo.currentIndexChanged.connect(self.selection_changed)
        self.currentIdChanged.connect(self.page_changed)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(150)
        self.device_timer = QTimer(self)
        self.device_timer.timeout.connect(self.sync_devices)
        self.device_timer.start(1000)
        self.sync_devices()
        self.selection_changed()

    @property
    def running(self):
        return self._future is not None

    def selected_reference(self):
        if self.keep.isChecked():
            return self.original
        index = self.candidate_combo.currentIndex()
        return self.candidates[index] if 0 <= index < len(self.candidates) else None

    def selection_changed(self):
        self.verified_path = None
        self.import_button.setEnabled(not self.keep.isChecked() and (not self.running))
        self.candidate_combo.setEnabled(not self.keep.isChecked())
        self.import_page.completeChanged.emit()
        self.check_status.setText(ui_text('m0220'))

    def page_changed(self):
        self.sync_devices()

    def sync_devices(self):
        data = self.devices_provider()
        current = self.devices.currentData()
        keys = tuple(((sn, info.model) for sn, (info, _, _) in data.items()))
        if keys != getattr(self, '_device_keys', None):
            self._device_keys = keys
            self.devices.clear()
            self.devices.addItem(ui_text('m0228'), None)
            for sn, model in keys:
                self.devices.addItem(f'{model} · {sn}', sn)
            self.devices.setCurrentIndex(max(0, self.devices.findData(current)))
        self.check_button.setEnabled(bool(data) and self.selected_reference() is not None and (not self.running))

    def choose_import(self):
        if self.running:
            return
        path, _ = QFileDialog.getOpenFileName(self, ui_text('m0221'), '', ui_text('m0222'))
        if not path:
            return
        if path.lower().endswith(('.apk', '.xapk')) and (not self.rights.isChecked()):
            QMessageBox.information(self, ui_text('m0229'), ui_text('m0230'))
            return
        self.import_button.setEnabled(False)
        self.import_status.setText(ui_text('m0223'))
        self._future = ('import', self._pool.submit(self.service.import_file, path))
        self.set_busy(True)
        self.button(QWizard.WizardButton.NextButton).setEnabled(False)

    def check_connection(self):
        if self.running:
            return
        data = self.devices_provider()
        serial = self.devices.currentData()
        reference = self.selected_reference()
        if serial not in data or reference is None:
            self.check_status.setText(ui_text('m0231'))
            return
        self._checking_reference = reference
        self.check_status.setText(ui_text('m0224'))
        self._future = ('check', self._pool.submit(self.service.connection_check, data[serial][0], reference))
        self.set_busy(True)
        self.check_button.setEnabled(False)
        self.button(QWizard.WizardButton.FinishButton).setEnabled(False)

    def set_busy(self, busy):
        self.keep.setEnabled(not busy and self.original is not None)
        self.candidate_combo.setEnabled(not busy and (not self.keep.isChecked()))
        self.import_button.setEnabled(not busy and (not self.keep.isChecked()))
        self.devices.setEnabled(not busy)
        self.button(QWizard.WizardButton.BackButton).setEnabled(not busy and self.currentId() > 0)

    def poll(self):
        if not self._future or not self._future[1].done():
            return
        kind, future = self._future
        self._future = None
        self.set_busy(False)
        try:
            result = future.result()
            if kind == 'import':
                self.service.discard(self.candidates)
                self.candidates = result
                self.candidate_combo.clear()
                for reference in result:
                    self.candidate_combo.addItem(ui_text('m0238').format(p0=f'{reference.bits}', p1=f'{reference.fingerprint[:20]}'))
                self.import_status.setText(ui_text('m0234').format(p0=f'{len(result)}'))
                self.import_page.completeChanged.emit()
            else:
                self.verified_path = self._checking_reference.path
                self.check_status.setText(result)
        except SetupError as exc:
            (self.import_status if kind == 'import' else self.check_status).setText(str(exc))
        except Exception:
            (self.import_status if kind == 'import' else self.check_status).setText(ui_text('m0235'))
        self.import_button.setEnabled(not self.keep.isChecked())
        self.button(QWizard.WizardButton.FinishButton).setEnabled(True)
        self.import_page.completeChanged.emit()
        self.sync_devices()
        if self._closing:
            self.dispose()

    def accept(self):
        if self.running:
            return
        reference = self.selected_reference()
        if reference is None:
            return
        if not self.keep.isChecked():
            text = ui_text('m0225').format(p0=f'{reference.bits}', p1=f'{reference.fingerprint[:20]}')
            if self.verified_path != reference.path:
                text += ui_text('m0232')
            if self.original:
                text += ui_text('m0233')
            if QMessageBox.question(self, ui_text('m0236'), text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            try:
                self.service.activate(reference, confirmed=True)
            except SetupError as exc:
                QMessageBox.warning(self, ui_text('m0239'), str(exc))
                return
        self.dispose()
        super().accept()

    def reject(self):
        self._closing = True
        self.service.stopped.set()
        if not self.running:
            self.dispose()
        super().reject()

    def dispose(self):
        if self._disposed:
            return
        self._disposed = True
        self.currentIdChanged.disconnect(self.page_changed)
        self.keep.toggled.disconnect(self.selection_changed)
        self.candidate_combo.currentIndexChanged.disconnect(self.selection_changed)
        self.service.discard(self.candidates)
        self.timer.stop()
        self.device_timer.stop()
        self._pool.shutdown(wait=False, cancel_futures=True)
