import io
import json
import socket
import threading
import time
from unittest.mock import Mock
import numpy as np
import pytest
from PIL import Image
from seestar_studio.backend import NativeMonitor, ReadOnlySocket, READ_METHODS
from seestar_studio.imaging import ImagePipeline
from seestar_studio.models import DeviceInfo


@pytest.fixture
def monitor():
    return NativeMonitor(DeviceInfo("unit", "127.0.0.1"))


def header(width=16, height=12, kind=5):
    return {"width": width, "height": height, "img_type": kind, "image_id": 1, "length": width * height * 6}


def test_readonly_guard():
    raw = Mock()
    sock = ReadOnlySocket(raw, threading.Event())
    for method in ["iscope_stop_view", "scope_goto", "set_setting", "scope_park", "set_wheel_position", "begin_streaming", "stop_streaming"]:
        with pytest.raises(PermissionError):
            sock.sendall(json.dumps({"method": method}).encode())
    raw.sendall.assert_not_called()
    for method in READ_METHODS:
        sock.sendall(json.dumps({"method": method}).encode())
    assert raw.sendall.call_count == len(READ_METHODS)


def test_jpeg_not_stretched(monkeypatch):
    from seestarpy import stream
    buffer = io.BytesIO()
    Image.new("RGB", (40, 60), (130, 75, 25)).save(buffer, format="JPEG")
    monkeypatch.setattr(stream, "_auto_stretch", Mock(side_effect=AssertionError("JPEG stretched")))
    image = ImagePipeline().decode(header(0, 0, 4), buffer.getvalue())
    assert image.width() == 40 and image.height() == 60
    pixel = image.pixelColor(5, 5)
    assert abs(pixel.red() - 130) < 4


def test_raw_and_corruption():
    arr = np.arange(16 * 12 * 3, dtype=np.uint16).reshape(12, 16, 3)
    image = ImagePipeline().decode(header(), arr.tobytes())
    assert image.width() == 16 and not image.isNull()
    assert image.pixelColor(15, 11).red() > image.pixelColor(0, 0).red()
    with pytest.raises(ValueError):
        ImagePipeline().decode(header(), b"invalid")


def test_preview_bayer_reduction():
    arr = np.arange(16 * 12, dtype=np.uint16)
    image = ImagePipeline().decode(header(kind=1), arr.tobytes())
    assert image.width() == 8 and image.height() == 6
    color = image.pixelColor(4, 3)
    assert color.red() == color.green() == color.blue()


def test_dedup_and_last_good_frame(monitor, monkeypatch):
    from seestarpy import stream
    payload = np.arange(16 * 12 * 3, dtype=np.uint16).tobytes()
    monkeypatch.setattr(stream, "_read_frame", lambda sock: (header(), payload))
    sock = Mock()
    assert monitor._request_frame(sock, "get_stacked_img")
    first = monitor.native_frame()
    assert monitor._request_frame(sock, "get_stacked_img")
    assert monitor.native_frame() is first
    monkeypatch.setattr(stream, "_read_frame", lambda sock: (header(), b"bad"))
    with pytest.raises(ValueError):
        monitor._request_frame(sock, "get_stacked_img")
    assert monitor.native_frame() is first


def test_new_poll_replaces_old_events_and_list_coordinates(monitor):
    monitor._handle_message(json.dumps({"Event": "View", "target_name": "old"}))
    monitor._handle_message(json.dumps({"method": "iscope_get_app_state", "result": {"View": {"target_name": "new"}}}))
    monitor._handle_message(json.dumps({"method": "scope_get_horiz_coord", "result": [42.2, 320.4]}))
    assert monitor.snapshot()["target"] == "new"
    assert monitor.snapshot()["alt"] == 42.2
    assert monitor.snapshot()["az"] == 320.4
    assert monitor.snapshot()["transfer_mode"] is None


def test_operation_failure_is_preserved_not_misreported_as_auth_failure(monitor):
    monitor._handle_message(json.dumps({'Event': 'PlateSolve', 'state': 'fail',
                                       'code': 251, 'error': 'solve failed', 'route': ['View','AutoGoto']}))
    assert monitor._events['PlateSolve']['state'] == 'fail'
    assert not monitor.snapshot()['error']
    monitor._handle_message(json.dumps({'method': 'get_device_state', 'result': {
        'camera': {'name': 'simulation'}, 'focuser': {'state': 'idle'},
        'mount': {'close': False, 'move_type': 'none'},
        'setting': {'auto_af': True, 'stack_after_goto': False}}}))
    snapshot = monitor.snapshot()
    assert snapshot['camera_ready'] is True and snapshot['has_focuser'] is True
    assert snapshot['auto_af'] is True and snapshot['stack_after_goto'] is False


def test_stop_interrupts_blocked_receive(monitor):
    left, right = socket.socketpair()
    wrapped = ReadOnlySocket(left, monitor._stop)
    monitor._sockets.add(wrapped)
    ended = threading.Event()
    def read():
        try:
            wrapped.recv(1)
        except OSError:
            pass
        finally:
            ended.set()
    thread = threading.Thread(target=read)
    monitor._threads.append(thread)
    thread.start()
    monitor.stop()
    right.close()
    assert ended.is_set()
    assert not monitor._sockets


def test_unknown_values_and_zero_reject_rate(monitor):
    assert monitor.snapshot()["battery"] is None
    monitor._handle_message(json.dumps({"Event": "Stack", "stacked_frame": 12, "dropped_frame": 0}))
    assert monitor.snapshot()["dropped_pct"] == 0


def test_command_reconnect_is_automatic(monitor, monkeypatch):
    import seestar_studio.backend as backend
    monkeypatch.setattr(backend, "RECONNECT_DELAY", .01)
    attempts = []
    def connect():
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionError("simulated device loss")
        return Mock()
    monkeypatch.setattr(monitor, "_connect_command", connect)
    monkeypatch.setattr(monitor, "_read_events", lambda sock: monitor._stop.set())
    monitor._command_loop()
    assert len(attempts) == 2
    assert not monitor.snapshot()["connected"]


def test_deadline_and_cancellation_prevent_receive():
    raw, stop = Mock(), threading.Event()
    sock = ReadOnlySocket(raw, stop)
    sock.deadline = time.monotonic() - 1
    with pytest.raises(TimeoutError):
        sock.recv(4096)
    stop.set()
    with pytest.raises(ConnectionAbortedError):
        sock.recv(4096)
    raw.recv.assert_not_called()


def test_receive_budget_bounds_corrupt_frame():
    raw = Mock()
    raw.recv.return_value = b"1234"
    sock = ReadOnlySocket(raw, threading.Event())
    sock.remaining_bytes = 4
    assert sock.recv(100) == b"1234"
    raw.recv.assert_called_once_with(4)
    with pytest.raises(ValueError):
        sock.recv(100)
