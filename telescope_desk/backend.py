"""Version-pinned adapter around SeestarPy 0.8.0 ScopeMonitor.

Imported only by the backend thread: SeestarPy discovers on import.
Protocol framing, authentication, event polling and pacing stay upstream.
"""
from .i18n import source as ui_text, tr
import hashlib
import json
import logging
import socket
import threading
import time
from importlib.metadata import version
from seestarpy import auth, connection, stream
from seestarpy.dashboard.monitor import ScopeMonitor, RECONNECT_DELAY
from .imaging import ImagePipeline
from .models import ImageFrame
LOG = logging.getLogger(__name__)
READ_METHODS = frozenset(ScopeMonitor._HEARTBEAT_CYCLE) | {'get_verify_str', 'verify_client', 'pi_is_verified', 'test_connection', 'get_stacked_img', 'get_current_img'}

class ReadOnlySocket:
    """Reject every outgoing RPC outside the audited viewer allowlist."""

    def __init__(self, sock, stop):
        self.sock, self.stop = (sock, stop)
        self.deadline = None
        self.remaining_bytes = None

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def sendall(self, data):
        message = json.loads(data.decode('utf-8').strip())
        if message.get('method') not in READ_METHODS:
            raise PermissionError('Command is not allowed in viewer mode')
        self.sock.sendall(data)

    def recv(self, size):
        if self.stop.is_set():
            raise ConnectionAbortedError('Session stopped')
        if self.deadline is not None and time.monotonic() > self.deadline:
            raise TimeoutError('Frame transfer deadline exceeded')
        if self.remaining_bytes is not None and self.remaining_bytes <= 0:
            raise ValueError('Receive budget exceeded')
        data = self.sock.recv(size if self.remaining_bytes is None else min(size, self.remaining_bytes))
        if self.remaining_bytes is not None:
            self.remaining_bytes -= len(data)
        return data

class NativeMonitor(ScopeMonitor):

    def __init__(self, info):
        if version('seestarpy') != '0.8.0':
            raise RuntimeError('Telescope Desk requires seestarpy 0.8.0')
        super().__init__(info.serial, info.ip, info.model, info.device_id)
        self.pipeline = ImagePipeline()
        self._sockets = set()
        self._socket_lock = threading.Lock()
        self._native_frame = None
        self._digest = None
        self._last_received = 0.0
        self._last_fetch_duration = 0.0

    def _open(self, port):
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wrapped = ReadOnlySocket(raw, self._stop)
        with self._socket_lock:
            if self._stop.is_set():
                raw.close()
                raise ConnectionAbortedError()
            self._sockets.add(wrapped)
        try:
            wrapped.settimeout(10)
            wrapped.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            wrapped.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            wrapped.connect((self.ip, port))
            return wrapped
        except Exception:
            self._close(wrapped)
            raise

    def _close(self, sock):
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()
        with self._socket_lock:
            self._sockets.discard(sock)

    def _connect_command(self):
        sock = self._open(connection.DEFAULT_PORT)
        try:
            sock.deadline = time.monotonic() + 30
            if auth.KEY_PATH is not None:
                auth.authenticate(sock)
            sock.deadline = None
            sock.settimeout(1)
            return sock
        except Exception:
            self._close(sock)
            raise

    def _command_loop(self):
        while not self._stop.is_set():
            sock = None
            try:
                sock = self._connect_command()
                self._set_connected(True)
                self._read_events(sock)
            except Exception as exc:
                self._set_connected(False, type(exc).__name__)
            finally:
                if sock is not None:
                    self._close(sock)
            self._stop.wait(RECONNECT_DELAY)
        self._set_connected(False)

    def _handle_message(self, line):
        try:
            data = json.loads(line)
        except (ValueError, TypeError):
            return
        if not isinstance(data, dict):
            return
        if 'error' in data and 'result' not in data and 'Event' not in data:
            with self._lock:
                self._error = ui_text('m0001')
            return
        if 'result' in data and (not isinstance(data['result'], (dict, list, int, float, type(None)))):
            return
        if data.get('method') in {'get_device_state', 'iscope_get_app_state'} and (not isinstance(data.get('result'), dict)):
            return
        with self._lock:
            method = data.get('method')
            if method == 'iscope_get_app_state' and isinstance(data.get('result'), dict):
                self._events.pop('View', None)
                self._events.pop('Stack', None)
            if method == 'get_device_state' and isinstance(data.get('result'), dict):
                self._events.pop('PiStatus', None)
            if 'result' in data:
                self._error = None
        if data.get('Event') and data['Event'] not in {'View', 'Stack', 'PiStatus', 'ScopeGoto', 'AutoGoto', 'PlateSolve', 'AutoFocus', 'ContinuousExposure', 'ScopeHome', 'ScopeMoveToHorizon'}:
            return
        super()._handle_message(line)

    def _image_loop(self):
        while not self._stop.is_set():
            sock = None
            try:
                sock = self._open(self.image_port)
                sock.settimeout(45)
                self._poll_frames(sock)
            except Exception as exc:
                with self._lock:
                    self._image_error = type(exc).__name__
            finally:
                if sock is not None:
                    self._close(sock)
            self._stop.wait(RECONNECT_DELAY)

    def _request_frame(self, sock, method):
        if method not in {'get_stacked_img', 'get_current_img'}:
            raise PermissionError('Not an image read')
        started = time.monotonic()
        sock.deadline = started + 120
        sock.remaining_bytes = 256 * 1024 * 1024
        stream._send_json(sock, method)
        for _ in range(10):
            if self._stop.is_set():
                return False
            header, payload = stream._read_frame(sock)
            if not stream.is_image_frame(header):
                continue
            kind = 'stacked' if stream.is_stacked_frame(header) else 'preview'
            hasher = hashlib.blake2b(payload, digest_size=16)
            hasher.update(f"{kind}:{header.get('width')}:{header.get('height')}".encode())
            digest = hasher.digest()
            now = time.time()
            if digest != self._digest or (self._native_frame and self._native_frame.kind != kind):
                image = self.pipeline.decode(header, payload)
                with self._lock:
                    self._frame_seq += 1
                    self._native_frame = ImageFrame(image, self._frame_seq, now, kind, 'JPEG' if payload[:3] == b'\xff\xd8\xff' else 'RAW 16-bit', header.get('image_id'))
                    self._digest = digest
                    self._frame_time = now
                    self._frame_meta = {'kind': kind, 'width': image.width(), 'height': image.height()}
            with self._lock:
                self._last_received = now
                self._last_fetch_duration = time.monotonic() - started
                self._image_error = None
            return True
        return False

    def native_frame(self):
        with self._lock:
            return self._native_frame

    def snapshot(self):
        result = super().snapshot()
        with self._lock:
            result['received_age_s'] = time.time() - self._last_received if self._last_received else None
            result['stale_after_s'] = max(90, self._last_fetch_duration * 4 + 30)
            device = self._rpc.get('get_device_state') or {}
            result['transfer_mode'] = ((device.get('setting') or {}).get('preview') or {}).get('image_transfer_mode')
            result['capabilities'] = {k: v for k, v in (device.get('device') or {}).items() if k.startswith('can_') and type(v) is bool}
            result['has_focuser'] = True if isinstance(device.get('focuser'), dict) and device['focuser'] else None
            result['camera_ready'] = True if isinstance(device.get('camera'), dict) and device['camera'] else None
            result['move_type'] = (device.get('mount') or {}).get('move_type')
            result['focuser_state'] = (device.get('focuser') or {}).get('state')
            for key in ('auto_af', 'stack_after_goto'):
                value = (device.get('setting') or {}).get(key)
                result[key] = value if type(value) is bool else None
        return result

    def stop(self):
        self._stop.set()
        with self._socket_lock:
            sockets = list(self._sockets)
        for sock in sockets:
            self._close(sock)
        for thread in self._threads:
            thread.join(timeout=15)
        if any((thread.is_alive() for thread in self._threads)):
            raise RuntimeError('Worker did not terminate')
        self._threads = []

def discover():
    connection.discover(quiet=True)
    from .models import DeviceInfo
    return [DeviceInfo(sn, rec['ip'], rec.get('model', 'Seestar'), rec.get('dev_id', sn)) for sn, rec in list(connection.DISCOVERED.items())]
