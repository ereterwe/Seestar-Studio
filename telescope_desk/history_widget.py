from .i18n import source as ui_text, tr
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from .card import label, button
from .history import read_history
from .timezones import local_text
from .plots import LinePlot
from .telemetry import number, duration

class HistoryWidget(QWidget):

    def __init__(self, service):
        super().__init__()
        self.service = service
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-history-read')
        self._future, self._stopped = (None, False)
        self.sessions = []
        root = QVBoxLayout(self)
        root.addWidget(label(ui_text('m0396'), 'brand'))
        root.addWidget(label(ui_text('m0092'), 'muted'))
        root.addWidget(button(ui_text('m0093'), self.refresh))
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([ui_text('m0094'), ui_text('m0095'), ui_text('m0096'), ui_text('m0097'), ui_text('m0399'), ui_text('m0400')])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        for column in (0, 1, 2, 3, 5):
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        root.addWidget(self.table, 1)
        self.summary = label(ui_text('m0088'), 'muted')
        self.summary.setWordWrap(True)
        self.summary.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        root.addWidget(self.summary)
        plots = QHBoxLayout()
        for name in (ui_text('m0089'), ui_text('m0090')):
            col = QVBoxLayout()
            col.addWidget(label(name, 'eyebrow'))
            plot = LinePlot()
            col.addWidget(plot)
            plots.addLayout(col)
            if name.startswith(ui_text('m0098')):
                self.temperature = plot
            else:
                self.battery = plot
        root.addLayout(plots, 1)
        self.status = label(ui_text('m0091'), 'muted')
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        self.table.itemSelectionChanged.connect(self.refresh)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(200)
        self.periodic = QTimer(self)
        self.periodic.timeout.connect(self.refresh)
        self.periodic.start(15000)
        self.refresh()

    def selected(self):
        return [self.sessions[i.row()]['id'] for i in self.table.selectionModel().selectedRows() if i.row() < len(self.sessions)][:4]

    def refresh(self):
        if self._stopped or self._future is not None:
            return
        selected = self.selected()
        self._future = self._pool.submit(read_history, self.service.path, selected)
        self._requested_selection = selected

    @property
    def running(self):
        return self._future is not None and (not self._future.done())

    def stop(self):
        self._stopped = True
        self._pool.shutdown(wait=False, cancel_futures=True)

    def poll(self):
        if self._stopped:
            return
        if self._future and self._future.done():
            future, self._future = (self._future, None)
            try:
                sessions, details = future.result()
            except Exception:
                self.status.setText(ui_text('m0109'))
                return
            selection = self.selected()
            self.sessions = sessions
            self.table.blockSignals(True)
            self.table.setRowCount(len(sessions))
            stamp = lambda t: local_text(datetime.fromtimestamp(t, timezone.utc),'UTC',True) if t else ui_text('m0104')
            reasons = {'monitor_closed': ui_text('m0099'), 'monitor_interrupted': ui_text('m0100'), 'counter_reset': ui_text('m0101'), 'target_changed': ui_text('extra.2'), 'stack_ended': ui_text('m0102'), 'observation_gap': ui_text('m0103')}
            for i, session in enumerate(sessions):
                values = [f"{session['model']} · {session['serial']}", session['target'] or '—', stamp(session['observed_start']), stamp(session['observed_end']), reasons.get(session['end_reason'], ui_text('m0110')), str(session['disconnects'])]
                for j, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    self.table.setItem(i, j, item)
                    item.setSelected(session['id'] in selection)
            self.table.blockSignals(False)
            if selection != self._requested_selection:
                self.refresh()
                return
            colors = ['#5cd6a3', '#e6ad63', '#83aaff', '#dd8bd2']
            summaries, temp_series, battery_series = ([], [], [])
            for index, (ident, data) in enumerate(details.items()):
                session = next((s for s in sessions if s['id'] == ident), None)
                if not session:
                    continue
                last = data['latest']
                span = (session['observed_end'] or last.get('ts', session['observed_start'])) - session['observed_start']
                color_name = [ui_text('m0111'), ui_text('m0402'), ui_text('m0403'), ui_text('extra.1')][index]
                summaries.append(ui_text('m0105').format(p0=f'{index + 1}', p1=f'{color_name}', p2=f"{session['target'] or '—'}", p3=f"{session['serial']}", p4=f'{duration(span)}', p5=f"{number(last.get('accepted'))}", p6=f"{number(last.get('dropped'))}", p7=f"{number(data['rejection_percent'], '%', 1)}", p8=f"{duration(last.get('integration_est'))}", p9=f"{duration(data['estimated_observed_seconds'])}", p10=f"{data['unknown_intervals']}", p11=f"{data['sample_count']}"))
                points = data['points']
                total = max(1, points[-1]['ts'] - points[0]['ts']) if points else 1
                positions = [(p['ts'] - points[0]['ts']) / total for p in points]
                temp_series.append(([p['temperature'] for p in points], colors[index], positions))
                battery_series.append(([p['battery'] for p in points], colors[index], positions))
            self.summary.setText('\n'.join(summaries) or ui_text('m0106'))
            self.temperature.set_series(temp_series, (ui_text('extra.0'), ui_text('m0107')), (-20, 80))
            self.battery.set_series(battery_series, (ui_text('extra.0'), ui_text('m0107')), (0, 100))
            self.status.setText(self.service.error or ui_text('m0108').format(p0=f'{len(sessions)}', p1=f'{self.service.skipped_batches}'))
