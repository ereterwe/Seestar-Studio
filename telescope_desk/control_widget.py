from .i18n import QMessageBox
from .i18n import source as ui_text, tr
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QCheckBox, QSpinBox, QScrollArea
from .card import label, button
from .control import ControlService, ACTIONS, unavailable_reason

class ControlWidget(QWidget):
    mode_changed = Signal(bool)

    def __init__(self, service=None):
        super().__init__()
        self.service = service or ControlService()
        self.target = None
        root = QVBoxLayout(self)
        self.mode = QCheckBox(ui_text('m0064'))
        root.addWidget(self.mode)
        notice = label(ui_text('m0065'), 'muted')
        notice.setWordWrap(True)
        root.addWidget(notice)
        self.devices = QComboBox()
        root.addWidget(self.devices)
        self.target_label = label(ui_text('m0066'), 'target')
        self.target_label.setWordWrap(True)
        root.addWidget(self.target_label)
        self.state = label(ui_text('m0067'), 'muted')
        self.state.setWordWrap(True)
        root.addWidget(self.state)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        form = QFormLayout(body)
        self.exposure = QComboBox()
        for seconds in (2, 5, 10, 20, 30, 60):
            self.exposure.addItem(ui_text('m0073').format(p0=f'{seconds}'), seconds)
        self.exposure.setCurrentIndex(2)
        self.gain = QSpinBox()
        self.gain.setRange(0, 1000)
        self.gain.setValue(80)
        self.filter = QComboBox()
        self.filter.addItem(ui_text('ctl_keep_filter'), None)
        self.filter.addItem('Open / IR-Cut (1)', 1)
        self.filter.addItem('LP / Narrow (2)', 2)
        self.filter.addItem(ui_text('m0069'), 0)
        form.addRow(ui_text('m0070'), self.exposure)
        form.addRow(ui_text('m0071'), self.gain)
        form.addRow(ui_text('m0072'), self.filter)
        self.buttons = {}
        for action, name in ACTIONS.items():
            if action == 'observe': name = ui_text('ctl_observe_button')
            b = button(name + ' …', lambda checked=False, a=action: self.confirm(a))
            self.buttons[action] = b
            form.addRow(b)
        self.cancel_button = button(ui_text('ctl_cancel'), self.cancel_sequence)
        form.addRow(self.cancel_button)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)
        self.result = label('', 'muted')
        self.result.setWordWrap(True)
        root.addWidget(self.result)
        self.steps = label('', 'muted')
        self.steps.setWordWrap(True)
        root.addWidget(self.steps)
        self.mode.toggled.connect(self.set_mode)
        self.devices.currentIndexChanged.connect(self.refresh)
        self.filter.currentIndexChanged.connect(self.refresh)
        self.refresh()

    def set_mode(self, enabled):
        self.service.set_enabled(enabled)
        self.mode_changed.emit(enabled)
        self.refresh()

    def set_target(self, target):
        self.target = target
        self.target_label.setText(f'GoTo: {target.title} · RA {target.ra:.5f}° / Dec {target.dec:.5f}°')
        self.refresh()

    def sync_devices(self, data):
        self.service.update_devices(data)
        current = self.devices.currentData()
        keys = tuple(((sn, info.model) for sn, (info, _, _) in data.items()))
        if keys != getattr(self, '_keys', None):
            self._keys = keys
            self.devices.blockSignals(True)
            self.devices.clear()
            self.devices.addItem(ui_text('m0074'), None)
            for sn, model in keys:
                self.devices.addItem(f'{model} · {sn}', sn)
            self.devices.setCurrentIndex(max(0, self.devices.findData(current)))
            self.devices.blockSignals(False)
        self.service.poll()
        self.refresh()

    def refresh(self):
        serial = self.devices.currentData()
        data = self.service.devices.get(serial)
        if data:
            _, tel, _ = data
            self.state.setText(ui_text('m0075').format(p0=ui_text('ctl_connected') if tel.connected else ui_text('ctl_disconnected'), p1=f"{tel.get('target') or '—'}", p2=f"{tel.get('view_mode') or '—'} / {tel.get('view_stage') or '—'} / {tel.get('view_state') or '—'}"))
        else:
            self.state.setText(ui_text('m0067'))
        for action, b in self.buttons.items():
            reason = ''
            if not self.service.enabled: reason = ui_text('m0049')
            elif data is None: reason = ui_text('m0050')
            else:
                try: self.service._check(serial)
                except (ValueError, PermissionError) as exc: reason = str(exc)
                if not reason and self.service.busy(serial): reason = ui_text('ctl_operation_busy')
                if not reason: reason = unavailable_reason(action, data[1].values)
            if not reason and action in ('goto', 'observe') and self.target is None:
                reason = ui_text('ctl_target_required')
            if not reason and action == 'filter' and self.filter.currentData() is None:
                reason = ui_text('ctl_filter_required')
            if not reason and action == 'preview' and self.filter.currentData() == 0:
                reason = ui_text('m0044')
            b.setEnabled(not reason)
            b.setToolTip(tr(reason or (ui_text('ctl_full_help') if action == 'observe' else
                                      ui_text('ctl_preview_help') if action == 'preview' else
                                      ui_text('ctl_stack_help') if action == 'stack' else ACTIONS[action])))
        self.cancel_button.setEnabled(self.service.enabled and self.service.busy(serial))
        result = self.service.results.get(serial, '')
        self.result.setText(ui_text('ctl_last_result').format(p0=result) if result else '')
        self.steps.setText(' · '.join(self.service.histories.get(serial, [])[-5:]))

    def confirm(self, action):
        params = {}
        if action in ('goto', 'observe') and self.target:
            params = {'target': self.target.title, 'ra': self.target.ra, 'dec': self.target.dec}
        elif action == 'exposure':
            params = {'seconds': self.exposure.currentData()}
        elif action == 'gain':
            params = {'gain': self.gain.value()}
        elif action == 'filter':
            params = {'position': self.filter.currentData()}
        elif action == 'preview':
            params = {'filter': self.filter.currentData()}
        try:
            intent = self.service.prepare(self.devices.currentData(), action, params)
            answer = QMessageBox.question(self, ui_text('m0076'), intent.description, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.service.execute(intent)
        except (ValueError, PermissionError) as exc:
            QMessageBox.warning(self, ui_text('m0077'), str(exc))
        self.refresh()

    def cancel_sequence(self):
        serial = self.devices.currentData()
        if QMessageBox.question(self, ui_text('ctl_cancel'), ui_text('ctl_cancel_confirm'),
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            try: self.service.cancel(serial)
            except (ValueError, PermissionError) as exc:
                QMessageBox.warning(self, ui_text('m0077'), str(exc))
        self.refresh()

    @property
    def running(self):
        return self.service.running

    def stop(self):
        self.service.stop()
