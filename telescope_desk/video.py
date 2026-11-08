"""Read-only RTSP reception, with one Qt decoder thread and latest-frame mailbox.

No telescope command adapter is imported. RTSP DESCRIBE/SETUP/PLAY are media
subscription messages, never firmware mode/start-view/record commands.
"""
from .i18n import source as ui_text, tr
import socket
import threading
import time
from urllib.parse import urlsplit
from PySide6.QtCore import QObject, QThread, QTimer, QUrl, Signal, Slot
from .models import ImageFrame

def probe_rtsp(url, timeout=2):
    """Bounded SDP inspection. A port being open alone is not a camera capability."""
    parsed = urlsplit(url)
    if parsed.scheme != 'rtsp' or not parsed.hostname or parsed.username:
        return False
    deadline = time.monotonic() + timeout
    try:
        with socket.create_connection((parsed.hostname, parsed.port or 554), timeout) as sock:
            request = f'DESCRIBE {url} RTSP/1.0\r\nCSeq: 1\r\nAccept: application/sdp\r\nUser-Agent: TelescopeDesk\r\n\r\n'
            sock.sendall(request.encode('ascii'))
            data = b''
            while len(data) < 65536 and time.monotonic() < deadline:
                sock.settimeout(max(0.05, deadline - time.monotonic()))
                block = sock.recv(min(4096, 65536 - len(data)))
                if not block:
                    break
                data += block
                if b'\r\n\r\n' in data:
                    head, body = data.split(b'\r\n\r\n', 1)
                    if not head.startswith(b'RTSP/1.0 200 '):
                        return False
                    lengths = [line.split(b':', 1)[1].strip() for line in head.split(b'\r\n') if line.lower().startswith(b'content-length:')]
                    if lengths and len(body) >= int(lengths[0]):
                        return b'm=video ' in body
            return False
    except (OSError, ValueError, UnicodeError):
        return False

class VideoWorker(QObject):

    def __init__(self, mailbox, probe=probe_rtsp, player_factory=None):
        super().__init__()
        self.mailbox, self.probe, self.player_factory = (mailbox, probe, player_factory)
        self.player = self.sink = self.timer = None
        self.ip = None
        self.camera = 'main'
        self.urls = {}
        self.closed = False
        self.last_frame = self.started = self.last_publish = 0
        self.sequence = 0
        self.frames = 0
        self.fps_start = time.monotonic()
        self.retry_at = 0
        self.backoff = 5

    @Slot(str, str)
    def configure(self, ip, camera):
        desired=self.mailbox.snapshot().get('desired')
        if desired is not None and desired!=(ip,camera):return
        self.release()
        self.ip, self.camera = (ip, camera)
        self.urls = {}
        self.backoff = 5
        self.retry_at = 0
        self.mailbox.update(frame=None, cameras=(), fps=None, status=ui_text('m0249'))
        if not ip:
            self.mailbox.update(status=ui_text('m0254'))
            return
        if self.timer is None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.tick)
            self.timer.start(500)
        self.connect_stream()

    def connect_stream(self):
        if not self.ip or self.closed:
            return
        from seestarpy.stream import build_rtsp_url, RTSP_PORT, RTSP_PORT_WIDE
        candidates = {'main': build_rtsp_url(self.ip, RTSP_PORT), 'wide': build_rtsp_url(self.ip, RTSP_PORT_WIDE)}
        self.urls = {key: url for key, url in candidates.items() if self.probe(url)}
        desired=self.mailbox.snapshot().get('desired')
        if desired is not None and desired!=(self.ip,self.camera):return
        self.mailbox.update(cameras=tuple(self.urls))
        if not self.urls:
            self.fail(ui_text('m0250'))
            return
        camera = self.camera if self.camera in self.urls else next(iter(self.urls))
        from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QPlaybackOptions
        self.player = self.player_factory(self) if self.player_factory else QMediaPlayer(self)
        self.sink = QVideoSink(self)
        options = QPlaybackOptions()
        if QUrl(self.urls[camera]).scheme() == 'rtsp':
            options.setPlaybackIntent(QPlaybackOptions.PlaybackIntent.LowLatencyStreaming)
        options.setNetworkTimeout(5000)
        options.setProbeSize(256 * 1024)
        self.player.setPlaybackOptions(options)
        self.player.setVideoSink(self.sink)
        self.sink.videoFrameChanged.connect(self.receive)
        self.player.errorOccurred.connect(self.decode_error)
        self.started = self.last_frame = time.monotonic()
        self.fps_start = self.started
        self.frames = 0
        self.mailbox.update(status=ui_text('m0251'), camera=camera, fps=None)
        self.player.setSource(QUrl(self.urls[camera]))
        self.player.play()

    @Slot()
    def decode_error(self, *unused):
        self.fail(ui_text('m0247'))

    def receive(self, frame):
        if self.closed or not self.ip or (not frame.isValid()):
            return
        now = time.monotonic()
        self.last_frame = now
        if now - self.last_publish < 1 / 30:
            return
        self.last_publish = now
        if frame.width() * frame.height() > 32000000:
            self.fail(ui_text('m0252'))
            return
        image = frame.toImage()
        if image.isNull():
            self.fail(ui_text('m0247'))
            return
        self.sequence += 1
        self.frames += 1
        self.backoff = 5
        elapsed = now - self.fps_start
        self.mailbox.update(frame=ImageFrame(image.copy(), self.sequence, time.time(), 'video', 'RTSP'), status=ui_text('m0438'), fps=self.frames / elapsed if elapsed >= 1 else None)
        if elapsed >= 3:
            self.frames = 0
            self.fps_start = now

    def fail(self, message):
        self.release()
        self.retry_at = time.monotonic() + self.backoff
        self.backoff = min(30, self.backoff * 2)
        self.mailbox.update(status=message, fps=None)

    def tick(self):
        if not self.ip or self.closed:
            return
        if self.player is not None and time.monotonic() - self.last_frame > 12:
            self.fail(ui_text('m0253'))
        elif self.player is None and time.monotonic() >= self.retry_at:
            self.connect_stream()

    def release(self):
        player, sink = (self.player, self.sink)
        self.player = self.sink = None
        if player:
            player.errorOccurred.disconnect(self.decode_error)
            if sink:
                sink.videoFrameChanged.disconnect(self.receive)
            player.stop()
            player.setSource(QUrl())
            player.setVideoSink(None)
            player.deleteLater()
        if sink:
            sink.deleteLater()

    @Slot()
    def shutdown(self):
        self.closed = True
        self.ip = None
        if self.timer:
            self.timer.stop()
        self.release()
        QThread.currentThread().quit()

class Mailbox:

    def __init__(self):
        self.lock = threading.Lock()
        self.data = {'frame': None, 'cameras': (), 'camera': 'main', 'fps': None, 'status': ui_text('m0248')}

    def update(self, **values):
        with self.lock:
            self.data.update(values)

    def snapshot(self):
        with self.lock:
            return dict(self.data)

class VideoSession(QObject):
    configure_requested = Signal(str, str)
    stop_requested = Signal()

    def __init__(self, parent=None, worker_factory=VideoWorker):
        super().__init__(parent)
        self.mailbox = Mailbox()
        self.thread = QThread(self)
        self.worker = worker_factory(self.mailbox)
        self.worker.moveToThread(self.thread)
        self.configure_requested.connect(self.worker.configure)
        self.stop_requested.connect(self.worker.shutdown)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.start()
        self.selection = None

    def configure(self, ip='', camera='main'):
        selection = (ip, camera)
        if selection != self.selection:
            self.selection = selection
            self.mailbox.update(desired=selection)
            self.configure_requested.emit(ip, camera)

    def latest(self):
        return self.mailbox.snapshot()

    @property
    def running(self):
        return self.thread.isRunning()

    def stop(self):
        self.mailbox.update(desired=('', ''))
        self.stop_requested.emit()
