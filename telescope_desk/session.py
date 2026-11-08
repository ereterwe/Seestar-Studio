from .i18n import source as ui_text, tr
import threading
from .telemetry import TelemetryService

class TelescopeSession:
    """One independently pausable session; never restarts a stopped monitor."""

    def __init__(self, info, factory):
        self.info, self.factory = (info, factory)
        self.monitor = factory(info)
        self.paused = False
        self.last_frame = None
        self.lock = threading.RLock()

    def start(self):
        with self.lock:
            self.monitor.start()

    def pause(self):
        with self.lock:
            self.paused = True
            self.monitor.stop()

    def resume(self):
        with self.lock:
            if not self.paused:
                return
            self.monitor = self.factory(self.info)
            self.monitor.start()
            self.paused = False

    def relocate(self, info):
        with self.lock:
            if info.ip == self.info.ip:
                return
            self.info = info
            self.monitor.stop()
            self.monitor = self.factory(info)
            if not self.paused:
                self.monitor.start()

    def snapshot(self):
        with self.lock:
            snapshot = self.monitor.snapshot()
            if self.last_frame is not None and self.monitor.native_frame() is None:
                snapshot['image_error'] = ui_text('m0171')
            return TelemetryService.normalize(snapshot, self.paused)

    def frame(self):
        with self.lock:
            frame = self.monitor.native_frame()
            if frame is not None:
                self.last_frame = frame
            return self.last_frame

    def stop(self):
        with self.lock:
            self.monitor.stop()
