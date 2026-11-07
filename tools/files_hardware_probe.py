"""Real, read-only SMB + download/resume probe alongside both live viewers."""
import json
from pathlib import Path
import threading
import time
from seestar_studio.manager import TelescopeManager
from seestar_studio.files.smb import SeestarFileClient
from seestar_studio.files.downloads import download_one, sha256_file
from seestar_studio.files.models import TransferCancelled


def main():
    root = Path('reports/downloads/phase1').resolve()
    root.mkdir(parents=True, exist_ok=True)
    manager = TelescopeManager()
    manager.start()
    report = {'type': 'real hardware, read-only', 'devices': {}}
    try:
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            data, _ = manager.latest()
            if len(data) >= 2 and all(t.connected for _, t, _ in data.values()):
                break
            time.sleep(.5)
        data, _ = manager.latest()
        for serial, (info, telemetry, frame) in data.items():
            record = report['devices'][serial] = {'model': info.model, 'stack_before': telemetry.get('stacked_frames')}
            client = None
            try:
                client = SeestarFileClient(info)
                roots = client.list('')
                record['root_directories'] = [e.name for e in roots if e.is_dir]
                folders = client.list('MyWorks')
                record['observation_directories'] = len([e for e in folders if e.is_dir])
                chosen = []
                for folder in [e for e in folders if e.is_dir][:12]:
                    entries = client.list(folder.path)
                    record.setdefault('types_seen', []).extend(sorted({e.kind for e in entries if not e.is_dir}))
                    images = [e for e in entries if not e.is_dir and e.name.lower().endswith(('.jpg', '.png')) and 100_000 < e.size < 8_000_000]
                    if images:
                        chosen = sorted(images, key=lambda e: e.size)[:1]
                        break
                record['types_seen'] = sorted(set(record.get('types_seen', [])))
                if chosen:
                    entry = chosen[0]
                    cancel = threading.Event()
                    try:
                        download_one(client, info, entry, root, cancel, lambda *args: cancel.set(), 1024 * 1024)
                    except TransferCancelled:
                        record['cancel_confirmed'] = True
                    target, skipped = download_one(client, info, entry, root, threading.Event(), lambda *args: None, 1024 * 1024)
                    record['download'] = {'name': entry.name, 'remote_size': entry.size, 'local_size': target.stat().st_size,
                                          'sha256': sha256_file(target), 'resumed_or_completed': True}
                    record['duplicate_skipped'] = download_one(client, info, entry, root, threading.Event(), lambda *args: None, 1024 * 1024)[1]
                else:
                    record['download_pending'] = 'No suitable bounded JPEG/PNG sample found'
                print(serial, 'SMB folders:', record['observation_directories'], 'download:', bool(chosen), flush=True)
            except Exception as exc:
                record['error_type'] = type(exc).__name__
                print(serial, type(exc).__name__, flush=True)
            finally:
                if client:
                    client.close()
        end = time.monotonic() + 40
        while time.monotonic() < end:
            time.sleep(1)
        data, _ = manager.latest()
        for serial, (info, telemetry, frame) in data.items():
            report['devices'].setdefault(serial, {})['after'] = {
                'connected': telemetry.connected, 'stacked_frames': telemetry.get('stacked_frames'),
                'frame_sequence': frame.sequence if frame else 0, 'image_error': telemetry.image_error,
                'target': telemetry.get('target'), 'stage': telemetry.get('view_stage')}
    finally:
        manager.stop()
        manager.join(40)
    report['clean_shutdown'] = not manager.running
    Path('reports/files-hardware.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Report: reports/files-hardware.json; clean shutdown:', not manager.running)


if __name__ == '__main__':
    main()
