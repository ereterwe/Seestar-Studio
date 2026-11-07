from .i18n import QMessageBox, QFileDialog
from .i18n import source as ui_text, tr
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo, available_timezones
import uuid
import re
from PySide6.QtCore import Qt, QTimer, QDate, QDateTime, QTime, QTimeZone
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSpinBox, QDialog, QFormLayout, QComboBox, QDialogButtonBox, QScrollArea, QDateEdit, QDateTimeEdit, QCheckBox, QPlainTextEdit
from .card import label, button
from .planner import PlanEntry, instant, schedule, next_slot, materialize, save_document, load_document
from .timezones import system_timezone, resolve_local, local_text
from .timeline import Timeline
from .solar import SolarService
from .telemetry import number

SOLAR_NOTES = {'solar.polar_day': ui_text('solar.polar_day'), 'solar.polar_night': ui_text('solar.polar_night'),
               'solar.no_dark': ui_text('solar.no_dark'), 'missing': ui_text('solar.missing'),
               'loading': ui_text('solar.loading'), 'off': ui_text('solar.off'), 'error': ui_text('solar.error')}

class EntryDialog(QDialog):

    def __init__(self, target, devices, entry=None, parent=None, zone='UTC', suggestion=None, selected=''):
        super().__init__(parent)
        self.setWindowTitle(ui_text('m0133'))
        self.target = target
        self.zone = zone
        self.resize(640, 330)
        layout = QFormLayout(self)
        layout.addRow(label(target.title, 'target'))
        self.device = QComboBox()
        self.device.setEditable(True)
        for key, name in devices.items():
            self.device.addItem(name, key)
        if selected:
            self.device.setCurrentIndex(self.device.findData(selected))
        self.minutes = QSpinBox()
        self.minutes.setRange(1, 720)
        self.minutes.setValue(entry.minutes if entry else 60)
        self.local = QDateTimeEdit()
        # This editor holds wall-clock components. Resolve DST ourselves in the
        # selected planning zone; Qt must not silently normalize a Windows gap.
        self.local.setTimeZone(QTimeZone.utc())
        self.local.setCalendarPopup(True)
        self.local.setDisplayFormat('dd.MM.yyyy HH:mm')
        at = instant(entry.fixed_start) if entry and entry.fixed_start else suggestion or datetime.now(timezone.utc)
        wall = at.astimezone(ZoneInfo(zone))
        self.local.setDateTime(QDateTime(QDate(wall.date()), QTime(wall.hour, wall.minute, wall.second), QTimeZone.utc()))
        self.occurrence = QComboBox()
        self.occurrence.addItem(ui_text('m0134'), None)
        self.occurrence.addItem(ui_text('m0135'), 0)
        self.occurrence.addItem(ui_text('m0136'), 1)
        if entry:
            index = self.device.findData(entry.telescope)
            if index >= 0:
                self.device.setCurrentIndex(index)
            else:
                self.device.setEditText(entry.telescope)
            self.occurrence.setCurrentIndex(1 + at.astimezone(ZoneInfo(zone)).fold)
        self.offset = label('', 'muted')
        self.local.dateTimeChanged.connect(self.preview)
        self.occurrence.currentIndexChanged.connect(self.preview)
        layout.addRow(ui_text('m0137'), self.device)
        layout.addRow(ui_text('m0138'), self.minutes)
        layout.addRow(ui_text('m0139'), self.local)
        layout.addRow(zone, self.occurrence)
        layout.addRow(self.offset)
        boxes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        boxes.accepted.connect(self.validate)
        boxes.rejected.connect(self.reject)
        layout.addRow(boxes)
        self.entry_id = entry.id if entry else uuid.uuid4().hex
        self.preview()

    def timestamp(self):
        return resolve_local(self.local.dateTime().toPython(), self.zone, self.occurrence.currentData())

    def preview(self):
        try:
            self.offset.setText(local_text(self.timestamp(), self.zone))
        except ValueError as exc:
            self.offset.setText(str(exc))

    def validate(self):
        try:
            index = self.device.currentIndex()
            device = self.device.currentData() if index >= 0 and self.device.currentText() == self.device.itemText(index) else self.device.currentText().strip()
            self.entry = PlanEntry(self.entry_id, device or self.device.currentText().strip(), self.target.id, self.minutes.value(), self.timestamp().isoformat())
        except ValueError as exc:
            QMessageBox.warning(self, ui_text('extra.3'), str(exc))
            return
        self.accept()

class PlannerWidget(QWidget):

    def __init__(self, sky, settings):
        super().__init__()
        self.sky, self.settings = (sky, settings)
        self.entries = []
        self.rows = []
        self.devices = {}
        self._device_key = None
        self._generation = 0
        self._future = None
        self._stopped = False
        self._validated_site = None
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-planner')
        self.solar = SolarService()
        self.store = settings.path.parent / 'plans'
        self.store.mkdir(parents=True, exist_ok=True)
        self.plan_id = ''
        self.zone = settings.values.get('planner_timezone') or system_timezone()
        self.start = QLineEdit(self)
        self.start.hide()
        root = QVBoxLayout(self)
        root.addWidget(label(ui_text('m0436'), 'brand'))
        root.addWidget(label(ui_text('m0146'), 'muted'))
        plans = QHBoxLayout()
        self.library = QComboBox()
        plans.addWidget(self.library, 1)
        plans.addWidget(button(ui_text('m0147'), self.new_plan))
        plans.addWidget(button(ui_text('m0148'), self.duplicate_plan))
        plans.addWidget(button(ui_text('m0149'), self.delete_plan))
        plans.addWidget(button(ui_text('m0150'), self.save))
        plans.addWidget(button(ui_text('m0151'), self.load))
        root.addLayout(plans)
        bar = QHBoxLayout()
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat('dd.MM.yyyy')
        self.timezone = QComboBox()
        self.timezone.setEditable(True)
        self.timezone.addItems(sorted(available_timezones()))
        self.timezone.setCurrentText(self.zone)
        self.device = QComboBox()
        self.device.setMinimumWidth(220)
        self.setup = QSpinBox()
        self.setup.setRange(0, 120)
        self.setup.setValue(5)
        self.setup.setSuffix(' min')
        bar.addWidget(label(ui_text('m0152')))
        bar.addWidget(self.date)
        bar.addWidget(label(ui_text('m0153')))
        bar.addWidget(self.timezone, 1)
        bar.addWidget(label(ui_text('m0154')))
        bar.addWidget(self.device, 1)
        bar.addWidget(label(ui_text('m0155')))
        bar.addWidget(self.setup)
        root.addLayout(bar)
        actions = QHBoxLayout()
        actions.addWidget(button(ui_text('m0156'), lambda: self.add_target(self.sky.target)))
        actions.addWidget(button(ui_text('m0157'), self.edit))
        actions.addWidget(button(ui_text('m0158'), self.resolve_conflict))
        actions.addWidget(button(ui_text('planner.optimize'), lambda: self.calculate(True)))
        self.gaps = QCheckBox(ui_text('m0140'))
        actions.addWidget(self.gaps)
        actions.addWidget(button(ui_text('m0159'), lambda: self.calculate(False)))
        actions.addStretch()
        actions.addWidget(button('−', lambda: self.timeline.zoom(1 / 1.25)))
        actions.addWidget(button('+', lambda: self.timeline.zoom(1.25)))
        root.addLayout(actions)
        solar_bar = QHBoxLayout()
        self.day_night = QCheckBox(ui_text('solar.enabled'))
        self.day_night.setChecked(settings.values.get('planner_day_night', True))
        self.day_night.toggled.connect(self.solar_toggled)
        solar_bar.addWidget(self.day_night)
        self.solar_note = label('', 'muted')
        self.solar_note.setWordWrap(True)
        self.solar_note.setToolTip(ui_text('solar.explanation'))
        solar_bar.addWidget(self.solar_note, 1)
        root.addLayout(solar_bar)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.timeline = Timeline()
        self.scroll.setWidget(self.timeline)
        root.addWidget(self.scroll, 1)
        root.addWidget(label(ui_text('m0160'), 'muted'))
        root.addWidget(label(ui_text('m0161'), 'muted'))
        self.message = label(ui_text('m0141'), 'muted')
        self.message.setWordWrap(True)
        root.addWidget(self.message)
        self.timeline.changed.connect(self.change_block)
        self.timeline.edit_requested.connect(self.edit)
        self.timeline.delete_requested.connect(self.remove)
        self.timeline.duplicate_requested.connect(self.duplicate_entry)
        self.date.dateChanged.connect(self.date_changed)
        self.timezone.currentTextChanged.connect(self.zone_changed)
        self.setup.valueChanged.connect(self.invalidate)
        self.library.activated.connect(self.select_plan)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(250)
        self.auto_timer = QTimer(self)
        self.auto_timer.setSingleShot(True)
        self.auto_timer.timeout.connect(lambda: self.calculate(False))
        self.start.textChanged.connect(self.invalidate)
        self.refresh_library()
        last = settings.values.get('last_plan_id', '')
        if re.fullmatch('[0-9a-f]{32}', last) and (self.store / f'{last}.json').is_file():
            self.open_document(self.store / f'{last}.json', last)
        else:
            self.new_plan()
        self.sync_devices({})

    @property
    def running(self):
        return self.solar.running or (self._future is not None and (not self._future[1].done()))

    def stop(self):
        self._stopped = True
        self.auto_timer.stop()
        self.timer.stop()
        self.solar.stop()
        self._pool.shutdown(wait=False, cancel_futures=True)

    def solar_toggled(self, enabled):
        self.settings.values['planner_day_night'] = enabled
        try: self.settings.save()
        except OSError: self.message.setText(ui_text('m0166'))
        self.refresh_solar()

    def refresh_solar(self):
        self.solar.request(self.sky.site, self.timeline.base, self.timeline.end, self.day_night.isChecked())
        self.timeline.set_solar(self.solar.profile)
        if self.solar.profile:
            profile = self.solar.profile
            text = ui_text('solar.duration').format(p0=number(profile.dark_seconds/3600, ' h', 1))
            text += ''.join(' · '+tr(SOLAR_NOTES[key]) for key in profile.conditions)
            if profile.warning: text += ' · '+tr(ui_text('solar.approximate'))
        else:
            text = SOLAR_NOTES[self.solar.state]
        self.solar_note.setText(text)

    def sync_devices(self, data):
        names = self.settings.values['known_devices']
        connected = []
        for sn, (info, tel, _) in data.items():
            names[sn] = info.model
            if tel.connected:
                connected.append(sn)
        ids = list(dict.fromkeys(connected + list(names) + [e.telescope for e in self.entries]))
        key = tuple(((sn, names.get(sn, sn), sn in connected) for sn in ids))
        self.devices = {sn: names.get(sn, sn) + ' · ' + sn for sn in ids}
        if key != self._device_key:
            current = self.device.currentData()
            self.device.clear()
            for sn, name, online in key:
                self.device.addItem(f'{name} · {sn}' + (' ●' if online else ' (offline)'), sn)
            index = self.device.findData(current)
            self.device.setCurrentIndex(max(0, index))
            self._device_key = key
            self.redraw()

    def base_for_date(self):
        day = self.date.date().toPython()
        return resolve_local(datetime.combine(day, datetime.min.time()).replace(hour=20), self.zone)

    def date_changed(self):
        self.start.setText(self.base_for_date().isoformat())

    def zone_changed(self, name):
        try:
            ZoneInfo(name)
        except (ValueError, KeyError):
            return
        self.zone = name
        self.settings.values['planner_timezone'] = name
        self.invalidate()

    def new_plan(self):
        self.plan_id = uuid.uuid4().hex
        self.entries = []
        self.rows = []
        self.start.setText(self.base_for_date().isoformat())
        self.invalidate()
        self.refresh_library()

    def refresh_library(self):
        self.library.clear()
        for path in sorted(self.store.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                entries, start, setup, zone = load_document(path, self.zone)
                self.library.addItem(local_text(instant(start), zone) + f' · {len(entries)}', path.stem)
            except Exception:
                continue
        self.library.setCurrentIndex(self.library.findData(self.plan_id))

    def persist(self):
        if not self.plan_id:
            return
        try:
            save_document(self.store / f'{self.plan_id}.json', self.entries, self.start.text(), self.setup.value(), self.zone, rows=self.rows)
            self.settings.values['last_plan_id'] = self.plan_id
            self.settings.save()
            index = self.library.findData(self.plan_id)
            if index >= 0:
                self.library.setItemText(index, local_text(instant(self.start.text()), self.zone) + f' · {len(self.entries)}')
        except (OSError, ValueError):
            self.message.setText(ui_text('m0166'))

    def invalidate(self):
        if not self.start.text():
            return
        self._generation += 1
        try:
            self.entries = materialize(self.entries, self.start.text(), self.setup.value())
            self.rows = schedule(self.entries, self.start.text(), self.setup.value(), self.sky.catalog or SimpleNamespace(by_id={}))
        except (ValueError, TypeError):
            self.message.setText(ui_text('m0167'))
            return
        self.redraw()
        self.persist()
        self.auto_timer.start(500)
        self.message.setText(ui_text('m0142'))

    def redraw(self):
        if not self.start.text():
            return
        self.timeline.targets = {e.target: self.sky.catalog.by_id[e.target].title for e in self.entries if self.sky.catalog and e.target in self.sky.catalog.by_id}
        self.timeline.set_rows(self.rows, self.devices, self.zone, instant(self.start.text()), self.setup.value())
        self.refresh_solar()

    def selected_id(self, value=None):
        return value if isinstance(value, str) else self.timeline.selected

    def add_target(self, target):
        if target is None or not target.valid:
            self.message.setText(ui_text('m0162'))
            return
        device = self.device.currentData()
        if not device:
            device = ''
        if len(self.entries) >= 100:
            self.message.setText(ui_text('m0163'))
            return
        suggestion = next_slot(self.entries, device, self.start.text(), 60, self.setup.value(), self.gaps.isChecked())
        dialog = EntryDialog(target, self.devices, parent=self, zone=self.zone, suggestion=suggestion, selected=device)
        dialog.manual_start = False
        dialog.local.dateTimeChanged.connect(lambda: setattr(dialog, 'manual_start', True))

        def resuggest():
            if dialog.manual_start:
                return
            chosen = dialog.device.currentData() or dialog.device.currentText()
            at = next_slot(self.entries, chosen, self.start.text(), dialog.minutes.value(), self.setup.value(), self.gaps.isChecked())
            dialog.local.blockSignals(True)
            wall = at.astimezone(ZoneInfo(self.zone))
            dialog.local.setDateTime(QDateTime(QDate(wall.date()), QTime(wall.hour, wall.minute, wall.second), QTimeZone.utc()))
            dialog.local.blockSignals(False)
            dialog.preview()
        dialog.device.currentIndexChanged.connect(resuggest)
        dialog.minutes.valueChanged.connect(resuggest)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.entries.append(dialog.entry)
            self.invalidate()
            self.refresh_library()

    def edit(self, value=None):
        entry = next((e for e in self.entries if e.id == self.selected_id(value)), None)
        if not entry or not self.sky.catalog:
            return
        target = self.sky.catalog.by_id.get(entry.target)
        if not target:
            return
        dialog = EntryDialog(target, self.devices, entry, self, self.zone)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.entries = [dialog.entry if e.id == entry.id else e for e in self.entries]
            self.invalidate()

    def change_block(self, key, start, minutes):
        self.entries = [replace(e, fixed_start=instant(start).isoformat(), minutes=minutes) if e.id == key else e for e in self.entries]
        self.invalidate()

    def remove(self, value=None):
        key = self.selected_id(value)
        self.entries = [e for e in self.entries if e.id != key]
        self.invalidate()
        self.refresh_library()

    def duplicate_entry(self, key):
        entry = next((e for e in self.entries if e.id == key), None)
        if not entry or len(self.entries) >= 100:
            return
        at = next_slot(self.entries, entry.telescope, self.start.text(), entry.minutes, self.setup.value(), self.gaps.isChecked())
        self.entries.append(replace(entry, id=uuid.uuid4().hex, fixed_start=at.isoformat()))
        self.invalidate()

    def resolve_conflict(self):
        entry = next((e for e in self.entries if e.id == self.timeline.selected), None)
        if not entry:
            self.message.setText(ui_text('m0164'))
            return
        at = next_slot(self.entries, entry.telescope, self.start.text(), entry.minutes, self.setup.value(), self.gaps.isChecked(), entry.id)
        self.change_block(entry.id, at.isoformat(), entry.minutes)

    def calculate(self, optimize=False):
        if self._future is not None and not self._future[1].done():
            self.auto_timer.start(500)
            return
        if not self.sky.catalog:
            self.auto_timer.start(1000)
            return
        try:
            instant(self.start.text())
        except ValueError as exc:
            self.message.setText(str(exc))
            return
        self._generation += 1
        entries = [replace(e, fixed_start='') for e in self.entries] if optimize else list(self.entries)
        self._future = (self._generation, self._pool.submit(schedule, entries, self.start.text(), self.setup.value(), self.sky.catalog, self.sky.site, optimize), self.sky.site, optimize)
        self.message.setText(ui_text('m0143'))

    def poll(self):
        if self._stopped:
            return
        self.refresh_solar()
        if self._future and self._future[1].done():
            generation, future, site, optimized = self._future
            self._future = None
            if generation != self._generation or site != self.sky.site:
                return
            try:
                rows = future.result()
                if optimized:
                    if self.review_optimization(rows):
                        self.entries = [replace(r.entry, fixed_start=r.start.isoformat()) for r in rows]
                        self.invalidate()
                    return
                self.rows = rows
                self.redraw()
                self.persist()
                self._validated_site = site
                self.message.setText(ui_text('m0168').format(p0=f'{len(self.rows)}', p1=f'{sum((bool(r.issues) for r in self.rows))}'))
            except Exception:
                self.message.setText(ui_text('m0170'))
        if self.rows and self._validated_site != self.sky.site:
            self._validated_site = self.sky.site
            self.invalidate()
        self.timeline.update()

    def review_optimization(self, rows):
        dialog = QDialog(self)
        dialog.setWindowTitle(tr(ui_text('planner.review')))
        dialog.resize(900, 600)
        layout = QVBoxLayout(dialog)
        note = label(ui_text('planner.review_note'), 'muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        old = {r.entry.id: r for r in self.rows}
        lines = []
        for row in rows:
            previous = old.get(row.entry.id)
            before = local_text(previous.start, self.zone) if previous else '—'
            lines.append(f'{self.devices.get(row.entry.telescope, row.entry.telescope)} · {row.entry.target}\n{before} → {local_text(row.start, self.zone)} — {local_text(row.end, self.zone)}\n' + tr('; '.join(row.issues) or ui_text('m0242')))
        preview = QPlainTextEdit('\n\n'.join(lines))
        preview.setReadOnly(True)
        layout.addWidget(preview, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        return dialog.exec() == QDialog.DialogCode.Accepted

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, ui_text('m0144'), str(self.settings.path.parent / 'observing-plan.json'), 'JSON (*.json)')
        if path:
            try:
                save_document(path, self.entries, self.start.text(), self.setup.value(), self.zone, rows=self.rows)
            except (OSError, ValueError) as exc:
                self.message.setText(str(exc))

    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, ui_text('m0145'), str(self.settings.path.parent), 'JSON (*.json)')
        if path:
            self.open_document(path, uuid.uuid4().hex)
            self.refresh_library()

    def open_document(self, path, key):
        try:
            entries, start, setup, zone = load_document(path, self.zone)
        except Exception:
            self.message.setText(ui_text('m0169'))
            return
        self.start.blockSignals(True)
        self.setup.blockSignals(True)
        self.timezone.blockSignals(True)
        self.date.blockSignals(True)
        self.plan_id = key
        self.entries = entries
        self.zone = zone
        self.timezone.setCurrentText(zone)
        self.start.setText(start)
        self.setup.setValue(setup)
        self.date.setDate(QDate(instant(start).astimezone(ZoneInfo(zone)).date()))
        for w in (self.start, self.setup, self.timezone, self.date):
            w.blockSignals(False)
        self.sync_devices({})
        self.invalidate()

    def select_plan(self):
        key = self.library.currentData()
        if key:
            self.open_document(self.store / f'{key}.json', key)

    def duplicate_plan(self):
        self.plan_id = uuid.uuid4().hex
        self.invalidate()
        self.refresh_library()

    def delete_plan(self):
        if QMessageBox.question(self, ui_text('m0149'), ui_text('m0165'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        (self.store / f'{self.plan_id}.json').unlink(missing_ok=True)
        self.new_plan()
