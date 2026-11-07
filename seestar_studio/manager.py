from .i18n import source as ui_text, tr
import logging
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from .session import TelescopeSession
LOG = logging.getLogger(__name__)

class TelescopeManager:
    """Network supervisor and a bounded latest-value mailbox for the UI."""

    def __init__(self, discovery=None, factory=None, rescan_interval=60):
        self.discovery, self.factory = (discovery, factory)
        self.rescan_interval = rescan_interval
        self.sessions = {}
        self._stop = threading.Event()
        self._commands = queue.Queue()
        self._lock = threading.Lock()
        self._latest = {}
        self._message = ui_text('m0112')
        self._thread = None

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, name='studio-manager', daemon=True)
            self._thread.start()

    def request_scan(self):
        self._commands.put(('scan', None))

    def set_paused(self, serial, paused):
        self._commands.put(('pause' if paused else 'resume', serial))

    def latest(self):
        with self._lock:
            return (dict(self._latest), self._message)

    def _status(self, message):
        with self._lock:
            self._message = message

    def stop(self):
        self._stop.set()

    def join(self, timeout=None):
        if self._thread:
            self._thread.join(timeout)

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        try:
            if self.discovery is None or self.factory is None:
                from .backend import discover, NativeMonitor
                self.discovery = self.discovery or discover
                self.factory = self.factory or NativeMonitor
            self._supervise()
        except Exception as exc:
            LOG.error('Backend initialization failed: %s', type(exc).__name__)
            self._status(ui_text('m0113'))

    def _supervise(self):
        pending = {}
        scan = None
        next_scan = 0
        with ThreadPoolExecutor(max_workers=8, thread_name_prefix='studio-lifecycle') as pool:
            try:
                while not self._stop.is_set():
                    while not self._commands.empty():
                        action, sn = self._commands.get_nowait()
                        if action == 'scan':
                            next_scan = 0
                        elif sn in self.sessions and sn not in pending:
                            method = self.sessions[sn].pause if action == 'pause' else self.sessions[sn].resume
                            pending[sn] = pool.submit(method)
                    for sn, future in list(pending.items()):
                        if future.done():
                            try:
                                future.result()
                            except Exception as exc:
                                LOG.warning('Device lifecycle failed: %s', type(exc).__name__)
                                self._status(ui_text('m0118'))
                            del pending[sn]
                    if scan is None and time.monotonic() >= next_scan:
                        self._status(ui_text('m0114'))
                        scan = pool.submit(self.discovery)
                    if scan is not None and scan.done():
                        try:
                            for info in scan.result():
                                if info.serial not in self.sessions:
                                    session = TelescopeSession(info, self.factory)
                                    self.sessions[info.serial] = session
                                    pending[info.serial] = pool.submit(session.start)
                                elif info.serial not in pending and self.sessions[info.serial].info.ip != info.ip:
                                    pending[info.serial] = pool.submit(self.sessions[info.serial].relocate, info)
                            self._status(ui_text('m0115') if self.sessions else ui_text('m0116'))
                        except Exception as exc:
                            LOG.warning('Discovery failed: %s', type(exc).__name__)
                            self._status(ui_text('m0117'))
                        scan = None
                        next_scan = time.monotonic() + self.rescan_interval
                    for sn, session in list(self.sessions.items()):
                        if sn in pending:
                            continue
                        try:
                            telemetry, frame = (session.snapshot(), session.frame())
                            with self._lock:
                                self._latest[sn] = (session.info, telemetry, frame)
                        except Exception as exc:
                            LOG.warning('Telemetry rejected: %s', type(exc).__name__)
                            from .models import Telemetry
                            with self._lock:
                                old = self._latest.get(sn)
                                self._latest[sn] = (session.info, Telemetry(sn, False, error=ui_text('m0119')), old[2] if old else None)
                    self._stop.wait(0.5)
            finally:
                for future in pending.values():
                    try:
                        future.result()
                    except Exception:
                        pass
                futures = [pool.submit(session.stop) for session in self.sessions.values()]
                for future in futures:
                    try:
                        future.result()
                    except Exception as exc:
                        LOG.error('Shutdown failed: %s', type(exc).__name__)
