"""Explicit one-shot location proposals. Never persists or logs coordinates."""
from dataclasses import dataclass
from datetime import timedelta
import math
import socket
import threading
import time
from PySide6.QtCore import QObject, QTimer, Signal
from .i18n import source as ui_text


@dataclass(frozen=True)
class LocationProposal:
    latitude: float
    longitude: float
    accuracy: float | None = None
    elevation: float | None = None
    source: str = 'windows'

    def __post_init__(self):
        if (not all(type(v) in (float, int) and math.isfinite(v) for v in (self.latitude, self.longitude))
                or not -90 <= self.latitude <= 90 or not -180 <= self.longitude <= 180):
            raise ValueError('Invalid location')
        if self.accuracy is not None and (not math.isfinite(self.accuracy) or self.accuracy < 0):
            raise ValueError('Invalid accuracy')
        if self.elevation is not None and (not math.isfinite(self.elevation) or not -500 <= self.elevation <= 10000):
            raise ValueError('Invalid elevation')


def windows_proposal(position):
    coordinate = position.coordinate
    point = coordinate.point
    basic = point.position
    elevation = None
    # Astronomy expects sea-level elevation, not an ellipsoid/terrain height.
    # GEOID == 3 in the audited Windows API. Accept only a bounded reported error.
    error = coordinate.altitude_accuracy
    if (int(point.altitude_reference_system) == 3 and error is not None
            and math.isfinite(error) and 0 <= error <= 100
            and math.isfinite(basic.altitude) and -500 <= basic.altitude <= 10000):
        elevation = basic.altitude
    return LocationProposal(basic.latitude, basic.longitude, coordinate.accuracy, elevation)


class WindowsLocationRequest(QObject):
    proposal = Signal(object)
    failed = Signal(str)

    def __init__(self, parent=None, api=None):
        super().__init__(parent)
        self.api = api
        self.operation = None
        self.locator = None
        self.phase = None
        self._apartment = False
        self.error_code = None
        self.deadline = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)

    def start(self):
        """Called only after explicit consent on the foreground GUI thread."""
        self.cancel()
        self.error_code = None
        try:
            if self.api is None:
                from winrt.windows.devices.geolocation import Geolocator
                self.api = Geolocator
            if getattr(self.api, '__module__', '').startswith('winrt'):
                import winrt.windows.foundation
                import winrt.windows.foundation.collections
                from winrt.runtime import init_apartment, ApartmentType
                init_apartment(ApartmentType.SINGLE_THREADED)
                self._apartment = True
            self.phase = 'permission'
            self.operation = self.api.request_access_async()
            self.deadline = time.monotonic() + 60
            self.timer.start(100)
        except (ImportError, AttributeError):
            self.fail('unsupported')
        except Exception as exc:
            self.fail(self.classify_error(exc))

    def location_status(self):
        try: return int(self.locator.location_status)
        except (AttributeError, TypeError, ValueError, OSError): return None

    def classify_error(self, exc):
        status = self.location_status()
        if status == 3: return 'disabled'
        if isinstance(exc, TimeoutError): return 'timeout'
        code = getattr(exc, 'winerror', None) or getattr(exc, 'hresult', None)
        if code is not None:
            code = int(code) & 0xffffffff
            if code in (5, 0x80070005): return 'denied'
            if code in (1460, 0x800705b4, 0x80070102): return 'timeout'
            if code in (50, 0x80070032, 0x80040154, 0x80004001): return 'unsupported'
        if status == 5: return 'unsupported'
        if status == 2: return 'no_data'
        return 'failed'

    def fail(self, code):
        self.error_code = code
        self.cancel()
        self.failed.emit(code)

    def poll(self):
        if self.operation is None:
            return
        try:
            if time.monotonic() > self.deadline:
                raise TimeoutError()
            # IAsyncOperation status: Started=0, Completed=1, Canceled=2, Error=3.
            status = int(self.operation.status)
            if status == 0:
                if self.location_status() in (3, 5):
                    self.fail('disabled' if self.location_status() == 3 else 'unsupported')
                return
            result = self.operation.get_results()  # completed operation; never waits
            self.operation.close()
            self.operation = None
            if self.phase == 'permission':
                if int(result) != 1:  # Allowed=1, Denied=2, Unspecified=0
                    if int(result) == 2:
                        try: self.locator = self.api()  # status only; no position request
                        except Exception: pass
                        self.fail('disabled' if self.location_status() == 3 else 'denied')
                    else:
                        self.fail('failed')
                    return
                self.locator = self.api()
                if self.location_status() in (3, 5):
                    self.fail('disabled' if self.location_status() == 3 else 'unsupported')
                    return
                self.phase = 'position'
                self.operation = self.locator.get_geoposition_async_with_age_and_timeout(
                    timedelta(seconds=30), timedelta(seconds=25))
                self.deadline = time.monotonic() + 30
            else:
                value = windows_proposal(result)
                self.cancel()
                self.proposal.emit(value)
        except Exception as exc:
            self.fail(self.classify_error(exc))

    def cancel(self):
        self.timer.stop()
        if self.operation is not None:
            try:
                self.operation.cancel()
                self.operation.close()
            except Exception:
                pass
        self.operation = self.locator = None
        self.phase = None
        if self._apartment:
            from winrt.runtime import uninit_apartment
            uninit_apartment()
            self._apartment = False


def read_seestar_location(info, stopped=None):
    """Existing authenticated read API; identity and location in one response.

    SeestarPy 0.8.0 raw.get_device_state documents location_lon_lat as [lon,lat].
    No model assumptions, coordinate writes, persistent connection or retry.
    """
    from seestarpy import auth, connection
    from .backend import ReadOnlySocket
    stopped = stopped or threading.Event()
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = ReadOnlySocket(raw, stopped)
    sock.deadline = time.monotonic() + 25
    sock.remaining_bytes = 2 * 1024 * 1024
    try:
        sock.settimeout(5)
        sock.connect((info.ip, connection.DEFAULT_PORT))
        if auth.KEY_PATH is not None:
            auth.authenticate(sock)
        reply = auth._send_recv(sock, {'id': 1501, 'method': 'get_device_state',
            'params': {'keys': ['device', 'location_lon_lat']}})
        result = reply.get('result') or {}
        if reply.get('code') != 0 or str((result.get('device') or {}).get('sn', '')).casefold() != info.serial.casefold():
            raise ValueError('Device identity not confirmed')
        pair = result.get('location_lon_lat')
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError('Location not supplied')
        return LocationProposal(pair[1], pair[0], source='seestar')
    except Exception:
        raise ValueError(ui_text('location.scope_failed')) from None
    finally:
        raw.close()
