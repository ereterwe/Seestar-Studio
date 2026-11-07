from .i18n import source as ui_text, tr
from .i18n import Label, Button
import time
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QWidget, QComboBox, QStackedWidget
from .viewer import ImageViewer
from .telemetry import number, duration

def label(text='', name=None):
    widget = Label(text)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    if name:
        widget.setObjectName(name)
    return widget

def button(text, callback, tooltip=''):
    widget = Button(text)
    widget.clicked.connect(callback)
    widget.setToolTip(tr(tooltip))
    return widget

class TelescopeCard(QFrame):
    maximize_requested = Signal(str)
    move_requested = Signal(str, int)
    pause_requested = Signal(str, bool)
    save_requested = Signal(str)
    details_changed = Signal(str, bool)
    source_changed = Signal(str, str)

    def __init__(self, info, details_open=False):
        super().__init__()
        self.info, self.frame, self.telemetry = (info, None, None)
        self.video = None
        self.video_frame = None
        self._video_selection = None
        self.setObjectName('card')
        self.setMinimumWidth(410)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 12)
        outer.setSpacing(10)
        top = QHBoxLayout()
        self.name = label(info.model, 'device')
        top.addWidget(self.name, 1)
        self.badge = label(ui_text('m0002'), 'badge')
        top.addWidget(self.badge)
        outer.addLayout(top)
        identity = QHBoxLayout()
        self.identity = label(info.device_id or info.serial, 'muted')
        identity.addWidget(self.identity, 1)
        identity.addWidget(button('←', lambda: self.move_requested.emit(info.serial, -1), ui_text('m0016')))
        identity.addWidget(button('→', lambda: self.move_requested.emit(info.serial, 1), ui_text('m0017')))
        self.pause_button = button(ui_text('m0003'), self._toggle_connection, ui_text('m0004'))
        identity.addWidget(self.pause_button)
        outer.addLayout(identity)
        self.target = label(ui_text('m0005'), 'target')
        outer.addWidget(self.target)
        self.viewer = ImageViewer()
        self.viewer.maximize_requested.connect(lambda: self.maximize_requested.emit(info.serial))
        source_bar = QHBoxLayout()
        self.source = QComboBox()
        self.source.addItem(ui_text('m0428'), 'stack')
        self.source.addItem(ui_text('m0429'), 'video')
        self.source.setToolTip(ui_text('m0006'))
        source_bar.addWidget(self.source)
        self.camera = QComboBox()
        self.camera.hide()
        source_bar.addWidget(self.camera)
        source_bar.addStretch()
        outer.addLayout(source_bar)
        self.video_viewer = ImageViewer()
        self.video_viewer.maximize_requested.connect(lambda: self.maximize_requested.emit(info.serial))
        self.views = QStackedWidget()
        self.views.addWidget(self.viewer)
        self.views.addWidget(self.video_viewer)
        outer.addWidget(self.views, 1)
        self.source.currentIndexChanged.connect(self.change_source)
        self.camera.activated.connect(self.change_camera)
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.poll_video)
        self.video_timer.start(50)
        image_line = QHBoxLayout()
        self.image_status = label(ui_text('m0007'), 'muted')
        self.image_status.setWordWrap(True)
        image_line.addWidget(self.image_status, 1)
        self.zoom = label(ui_text('m0008'), 'muted')
        self.viewer.zoom_changed.connect(self.zoom.setText)
        self.video_viewer.zoom_changed.connect(self.zoom.setText)
        image_line.addWidget(self.zoom)
        outer.addLayout(image_line)
        tools = QHBoxLayout()
        tools.addWidget(button(ui_text('m0008'), lambda: self.views.currentWidget().fit_image()))
        tools.addWidget(button('100 %', lambda: self.views.currentWidget().actual_size()))
        self.save_button = button(ui_text('m0009'), lambda: self.save_requested.emit(info.serial))
        self.save_button.setEnabled(False)
        tools.addWidget(self.save_button)
        tools.addStretch()
        self.max_button = button(ui_text('m0010'), lambda: self.maximize_requested.emit(info.serial))
        tools.addWidget(self.max_button)
        outer.addLayout(tools)
        metrics_widget = QWidget()
        metrics_widget.setObjectName('metrics')
        metrics = QGridLayout(metrics_widget)
        metrics.setContentsMargins(0, 6, 0, 2)
        metrics.setHorizontalSpacing(18)
        metrics.setVerticalSpacing(12)
        self.metrics = {}
        for index, (key, title) in enumerate([('integration', 'INTEGRATION ≈'), ('exposure', ui_text('m0386')), ('frames', ui_text('m0387')), ('rejected', ui_text('m0388')), ('filter', 'FILTER'), ('battery', ui_text('m0389')), ('mode', ui_text('m0390')), ('stage', ui_text('m0391'))]):
            cell = QVBoxLayout()
            cell.setSpacing(3)
            cell.addWidget(label(title, 'metricLabel'))
            value = label('—', 'metricValue')
            self.metrics[key] = value
            cell.addWidget(value)
            metrics.addLayout(cell, index // 4, index % 4)
            metrics.setColumnStretch(index % 4, 1)
        self.metrics['integration'].setToolTip(ui_text('m0011'))
        outer.addWidget(metrics_widget)
        self.details_button = button(ui_text('m0012'), self._toggle_details)
        outer.addWidget(self.details_button)
        self.details = label('', 'muted')
        self.details.setWordWrap(True)
        outer.addWidget(self.details)
        self.details.setVisible(details_open)
        self.details_button.setText(ui_text('m0018') if details_open else ui_text('m0012'))

    def change_source(self):
        is_video = self.source.currentData() == 'video'
        self.views.setCurrentIndex(1 if is_video else 0)
        if is_video and self.video is None:
            from .video import VideoSession
            self.video = VideoSession(self)
        self.sync_video()
        self.source_changed.emit(self.info.serial, self.source.currentData())
        self.save_button.setEnabled(self.current_frame() is not None)
        if not is_video:
            self.update_age()

    def change_camera(self):
        if self.video:
            self.video_frame = None
            from PySide6.QtGui import QPixmap
            self.video_viewer.item.setPixmap(QPixmap())
            self.video.configure(self.info.ip, self.camera.currentData() or 'main')

    def sync_video(self):
        if self.video:
            active = self.source.currentData() == 'video' and self.telemetry and self.telemetry.connected and (not self.telemetry.paused)
            self.video.configure(self.info.ip if active else '', self.camera.currentData() or 'main')
        self.camera.setVisible(self.source.currentData() == 'video' and self.camera.count() > 1)

    def poll_video(self):
        if not self.video or self.source.currentData() != 'video':
            return
        data = self.video.latest()
        cameras = data['cameras']
        if cameras != getattr(self, '_cameras', None):
            self._cameras = cameras
            self.camera.blockSignals(True)
            self.camera.clear()
            for key in cameras:
                self.camera.addItem(ui_text('m0394') if key == 'main' else ui_text('m0395'), key)
            self.camera.setCurrentIndex(max(0, self.camera.findData(data['camera'])))
            self.camera.blockSignals(False)
            self.camera.setVisible(len(cameras) > 1)
        frame = data['frame']
        if frame and frame is not self.video_frame:
            self.video_frame = frame
            self.video_viewer.set_image(frame.image)
        text = data['status']
        if data['fps'] is not None:
            text += " · " + number(data["fps"], " FPS", 1)
        if self.video_frame and (frame is None or time.time() - self.video_frame.received_at > 5 or data['status'] != ui_text('m0438')):
            text = ui_text('m0019') + text
        self.image_status.setText(text)
        self.save_button.setEnabled(self.video_frame is not None)

    def current_frame(self):
        return self.video_frame if self.source.currentData() == 'video' else self.frame

    def stop_video(self):
        self.video_timer.stop()
        if self.video:
            self.video.stop()

    def _toggle_details(self):
        visible = not self.details.isVisible()
        self.details.setVisible(visible)
        self.details_button.setText(ui_text('m0018') if visible else ui_text('m0012'))
        self.details_changed.emit(self.info.serial, visible)

    def _toggle_connection(self):
        paused = not self.telemetry.paused if self.telemetry else True
        self.pause_requested.emit(self.info.serial, paused)
        self.pause_button.setEnabled(False)
        self.pause_button.setText(ui_text('m0013'))

    def update_data(self, info, telemetry, frame):
        self.info, self.telemetry = (info, telemetry)
        t = telemetry.get
        self.name.setText(str(t('model') or info.model))
        self.identity.setText(f'{info.device_id or info.serial}   ·   {info.ip}')
        self.target.setText(str(t('target') or ui_text('m0005')))
        status = ui_text('m0393') if telemetry.paused else ui_text('m0392') if telemetry.connected else ui_text('m0020')
        color, background = ('#7fe0b5', '#17372d') if telemetry.connected else ('#ffb966', '#3c2d1e') if telemetry.paused else ('#ff8c91', '#3b222b')
        if telemetry.error:
            status, color, background = (ui_text('m0021'), '#ffb966', '#3c2d1e')
        self.badge.setText(status)
        self.badge.setStyleSheet(f'color:{color}; background:{background};')
        self.badge.setToolTip(telemetry.error or ui_text('m0022'))
        self.pause_button.setText(ui_text('m0023') if telemetry.paused else ui_text('m0003'))
        self.pause_button.setEnabled(True)
        values = {'integration': duration(t('stack_time_s')), 'exposure': number(t('exp_s'), ' s', 1), 'frames': number(t('stacked_frames')), 'rejected': number(t('dropped_pct'), ' %', 1), 'filter': t('filter') or '—', 'battery': number(t('battery'), ' %'), 'mode': t('view_mode') or '—', 'stage': t('view_stage') or t('view_state') or '—'}
        for key, value in values.items():
            self.metrics[key].setText(str(value))
        self.metrics['rejected'].setToolTip(ui_text('m0014').format(p0=f"{number(t('dropped_frames'))}"))
        self.metrics['rejected'].setStyleSheet('color:#ffb966' if t('dropped_pct') is not None and t('dropped_pct') > 10 else '')
        self.metrics['battery'].setStyleSheet('color:#ffb966' if t('battery') is not None and t('battery') < 30 else '')
        mount = '—' if t('equ_mode') is None else 'EQ' if t('equ_mode') else 'Alt-Az'
        tracking = '—' if t('tracking') is None else ui_text('m0024') if t('tracking') else ui_text('m0025')
        self.details.setText(ui_text('m0015').format(p0=f"{number(t('gain'))}", p1=f"{t('dither') or '—'}", p2=f"{number(t('dropped_frames'))}", p3=f"{t('view_state') or '—'}", p4=f"{number(t('ra'), ' h', 4)}", p5=f"{number(t('dec'), '°', 4)}", p6=f"{number(t('alt'), '°', 1)}", p7=f"{number(t('az'), '°', 1)}", p8=f'{mount}', p9=f'{tracking}', p10=f"{number(t('temp_c'), ' °C', 1)}", p11=f"{number(t('free_gb'), ' GB', 1)}", p12=f"{t('firmware') or '—'}", p13=f"{t('transfer_mode') or '—'}"))
        if frame is not None and frame is not self.frame:
            self.frame = frame
            self.viewer.set_image(frame.image)
            self.save_button.setEnabled(True)
        self.update_age()
        self.sync_video()

    def update_age(self):
        if self.source.currentData() == 'video':
            return
        if self.frame is None:
            self.image_status.setText(ui_text('m0007') + (ui_text('m0026') if self.telemetry and self.telemetry.image_error else ''))
            return
        t = self.telemetry
        age = max(0, time.time() - self.frame.received_at)
        stale = t is None or not t.connected or t.error or t.image_error or ((t.get('received_age_s') or 0) + max(0, time.time() - t.observed_at) > (t.get('stale_after_s') or 90))
        kind = ui_text('m0430') if self.frame.kind == 'stacked' else ui_text('m0431')
        text = ui_text('card.frame_age').format(p0=kind,p1=self.frame.source_format,p2=self.frame.image.width(),p3=self.frame.image.height(),p4=duration(age))
        if stale:
            text = ui_text('m0019') + text
        self.image_status.setText(text)
        self.image_status.setStyleSheet('color:#ffb966' if stale else 'color:#8b9aae')
        self.image_status.setToolTip(t.image_error or '' if t else '')
