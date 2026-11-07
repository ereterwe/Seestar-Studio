"""Read-only dual stack/RTSP probe; never sends telescope control actions."""
import json
import time
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from seestar_studio.manager import TelescopeManager
from seestar_studio.video import VideoSession


def main():
    app = QApplication([]); manager = TelescopeManager(); videos = {}; records = {}
    started = time.monotonic(); closing = False
    def tick():
        nonlocal closing
        data, _ = manager.latest()
        for sn, (info, tel, frame) in data.items():
            record = records.setdefault(sn, {'model': info.model, 'stack_sequences': [], 'states': [], 'video_sequences': [], 'cameras': []})
            state = [tel.get('view_stage'), tel.get('stacked_frames')]
            if state not in record['states']: record['states'].append(state)
            if frame and frame.sequence not in record['stack_sequences']: record['stack_sequences'].append(frame.sequence)
            if sn not in videos and tel.connected and not closing:
                videos[sn] = VideoSession(); videos[sn].configure(info.ip)
            if sn in videos:
                v = videos[sn].latest(); record['cameras'] = list(v['cameras']); record['video_status'] = v['status']
                if v['frame'] and v['frame'].sequence not in record['video_sequences']: record['video_sequences'].append(v['frame'].sequence)
        if time.monotonic() - started >= 90 and not closing:
            closing = True; manager.stop()
            for v in videos.values(): v.stop()
        if closing and not manager.running and not any(v.running for v in videos.values()):
            report = {'test_type': 'real hardware read-only; no device mode changes', 'duration_s': round(time.monotonic()-started), 'devices': records, 'clean_shutdown': True}
            path = Path('reports/v22-hardware.json'); path.write_text(json.dumps(report, indent=2), encoding='utf-8')
            print(json.dumps(report)); app.quit()
    timer = QTimer(); timer.timeout.connect(tick); timer.start(500); manager.start()
    return app.exec()


if __name__ == '__main__': raise SystemExit(main())
