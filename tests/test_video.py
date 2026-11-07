import time
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import QVideoFrame
from seestar_studio.video import Mailbox, VideoWorker, VideoSession, probe_rtsp
from seestar_studio.models import DeviceInfo, Telemetry, ImageFrame


def test_video_frame_mailbox_format_and_decoder_errors(app):
    box = Mailbox(); worker = VideoWorker(box)
    worker.ip = '192.0.2.1'
    frame = QVideoFrame(QImage(320, 240, QImage.Format.Format_RGB32))
    worker.receive(frame)
    assert box.snapshot()['frame'].image.width() == 320
    assert box.snapshot()['frame'].kind == 'video'
    worker.receive(QVideoFrame())
    assert box.snapshot()['frame'].sequence == 1
    worker.decode_error()
    assert box.snapshot()['fps'] is None and worker.retry_at > time.monotonic()
    assert box.snapshot()['frame'] is not None  # stale image retained


def test_unavailable_camera_reconnect_bounded_and_release(app):
    calls = []
    worker = VideoWorker(Mailbox(), probe=lambda url: calls.append(url) or False)
    worker.configure('192.0.2.1', 'wide')
    assert len(calls) == 2 and worker.mailbox.snapshot()['cameras'] == ()
    worker.tick(); assert len(calls) == 2
    worker.retry_at = 0; worker.tick(); assert len(calls) == 4
    worker.configure('', 'main'); worker.tick(); assert len(calls) == 4
    worker.timer.stop(); worker.deleteLater()


def test_two_cards_modes_preserve_stack_and_stop_workers(app, monkeypatch):
    from seestar_studio import video
    from seestar_studio.card import TelescopeCard
    monkeypatch.setattr(video, 'VideoSession', lambda parent: VideoSession(parent,
        worker_factory=lambda box: VideoWorker(box, probe=lambda url: False)))
    cards = [TelescopeCard(DeviceInfo(str(i), '192.0.2.1')) for i in range(2)]
    stack = ImageFrame(QImage(80, 100, QImage.Format.Format_RGB32), 1, time.time(), 'stacked', 'RAW')
    for card in cards: card.update_data(card.info, Telemetry(card.info.serial, True), stack)
    cards[0].source.setCurrentIndex(1)
    assert cards[1].source.currentData() == 'stack' and cards[1].current_frame() is stack
    cards[0].source.setCurrentIndex(0)
    assert cards[0].current_frame() is stack
    for card in cards: card.stop_video()
    deadline = time.monotonic() + 5
    while any(c.video and c.video.running for c in cards) and time.monotonic() < deadline:
        app.processEvents(); time.sleep(.01)
    assert not cards[0].video.running
    for card in cards: card.deleteLater()


def test_rtsp_probe_requires_video_sdp(monkeypatch):
    import socket
    class Socket:
        def __init__(self, response): self.response = response
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def settimeout(self, n): pass
        def sendall(self, data): assert data.startswith(b'DESCRIBE ') and b'start_view' not in data
        def recv(self, n): data, self.response = self.response, b''; return data
    body = b'v=0\r\nm=video 0 RTP/AVP 96\r\n'
    monkeypatch.setattr(socket, 'create_connection', lambda *a: Socket(b'RTSP/1.0 200 OK\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body))
    assert probe_rtsp('rtsp://192.0.2.1:4554/stream')
    monkeypatch.setattr(socket, 'create_connection', lambda *a: Socket(b'RTSP/1.0 404 Not Found\r\n\r\n'))
    assert not probe_rtsp('rtsp://192.0.2.1:4554/stream')


def test_real_qt_decoder_with_synthetic_local_video(app,tmp_path,monkeypatch):
    from PIL import Image
    from seestarpy import stream
    frames=[Image.new('RGB',(96,64),(i*10,40,100)) for i in range(20)]
    path=tmp_path/'synthetic.gif';frames[0].save(path,save_all=True,append_images=frames[1:],duration=80,loop=0)
    monkeypatch.setattr(stream,'build_rtsp_url',lambda *args:path.as_uri())
    session=VideoSession(worker_factory=lambda box:VideoWorker(box,probe=lambda url:True))
    session.configure('synthetic')
    try:
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            app.processEvents();time.sleep(.02)
            frame=session.latest()['frame']
            if frame and frame.sequence>=5:break
        frame=session.latest()['frame']
        assert frame is not None and frame.sequence>=5
        assert frame.image.width()==96
    finally:
        session.stop();deadline=time.monotonic()+8
        while session.running and time.monotonic()<deadline:app.processEvents();time.sleep(.02)
        assert not session.running
        session.deleteLater()
