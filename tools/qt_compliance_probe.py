"""Isolated Qt payload/replacement probe; no application or telescope code.

Creates a disposable evidence directory but never changes the input build.
Appends a harmless overlay to a copied QtCore DLL to demonstrate that changed
DLL bytes load. This is NOT an independently rebuilt Qt or complete app test.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def child(root):
    sys.path.insert(0, str(root))
    handles = [os.add_dll_directory(str(root / name)) for name in ('PySide6', 'shiboken6')]
    os.environ['QT_PLUGIN_PATH'] = str(root / 'PySide6/plugins')
    os.environ['QT_QPA_PLATFORM'] = 'windows'
    os.environ['QT_MEDIA_BACKEND'] = 'ffmpeg'
    from PySide6.QtCore import QTimer, QUrl, qVersion
    from PySide6.QtGui import QImageReader
    from PySide6.QtWidgets import QApplication, QLabel
    from PySide6.QtMultimedia import QMediaPlayer, QVideoSink
    from PIL import Image
    app = QApplication([])
    widget = QLabel('Isolated Qt compliance probe')
    widget.resize(480, 120)
    rendered = widget.grab()
    assert not rendered.isNull()
    # Synthetic animation exercises the real bundled FFmpeg video decoder.
    images = [Image.new('RGB', (96, 64), (i * 10, 40, 100)) for i in range(20)]
    movie = root / 'synthetic.gif'
    images[0].save(movie, save_all=True, append_images=images[1:], duration=80, loop=0)
    player, sink = QMediaPlayer(), QVideoSink()
    frames = []
    sink.videoFrameChanged.connect(lambda frame: frames.append([frame.width(), frame.height()]) if frame.isValid() else None)
    player.setVideoSink(sink)
    player.setSource(QUrl.fromLocalFile(str(movie)))
    player.play()
    QTimer.singleShot(4000, app.quit)
    app.exec()
    player.stop()
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
    kernel.GetModuleHandleW.restype = ctypes.c_void_p
    kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
    kernel.GetModuleFileNameW.restype = ctypes.c_uint
    loaded = []
    for name in ('Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll', 'Qt6Multimedia.dll', 'avcodec-63.dll'):
        handle = kernel.GetModuleHandleW(name)
        assert handle, name
        buffer = ctypes.create_unicode_buffer(32768)
        assert kernel.GetModuleFileNameW(handle, buffer, len(buffer)), name
        path = Path(buffer.value).resolve()
        assert path.is_relative_to(root), 'DLL loaded outside isolated payload'
        loaded.append({'file': path.relative_to(root).as_posix(), 'sha256': digest(path)})
    result = {'qt_version': qVersion(), 'widget_rendered': True, 'video_frames': len(frames),
              'video_size': frames[-1] if frames else None,
              'image_formats': sorted(bytes(f).decode() for f in QImageReader.supportedImageFormats()),
              'loaded_dlls': loaded, 'network_or_telescope_code_used': False}
    (root / 'probe-result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    assert len(frames) >= 3, 'Local decoder did not deliver frames'
    assert {'jpeg', 'png', 'svg'} <= set(result['image_formats'])
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--child', type=Path)
    args = parser.parse_args()
    if args.child:
        return child(args.child.resolve())
    if not args.target or not args.output:
        parser.error('--target and --output required')
    from tools.qt_packaging import excluded, filter_binaries
    target = args.target.resolve()
    output = args.output.resolve()
    if output == target or target in output.parents:
        parser.error('Output must be outside original payload')
    root = output / ('qt-probe-' + uuid.uuid4().hex[:10])
    root.mkdir(parents=True)
    entries = [(p.relative_to(target).as_posix(), str(p), 'BINARY') for p in target.rglob('*')
               if p.is_file() and p.suffix.lower() in {'.dll', '.pyd', '.exe'}]
    kept = filter_binaries(entries)
    removed = [e[0] for e in entries if excluded(e[0])]
    for package in ('PySide6', 'shiboken6'):
        shutil.copytree(target / '_internal' / package, root / package,
                        ignore=lambda directory, names: [n for n in names if excluded(n)])
        # Frozen packages keep Python helpers in PYZ. For this isolated interpreter
        # probe use matching installed helper scripts, and record this limitation.
        installed = Path(sys.prefix) / 'Lib/site-packages' / package
        for path in installed.rglob('*.py'):
            destination = root / package / path.relative_to(installed)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
    core = root / 'PySide6/Qt6Core.dll'
    before = digest(core)
    with core.open('ab') as stream:
        stream.write(b'\nSeestar Studio isolated DLL replacement probe; code unchanged.\n')
    after = digest(core)
    assert before != after
    process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(root)],
                             capture_output=True, timeout=30)
    # Keep stderr local; only report bounded error categories publicly.
    (root / 'decoder-output.txt').write_bytes(process.stderr)
    report = {'status': 'PASS' if process.returncode == 0 else 'BLOCKER',
              'scope': 'Packaged Qt/FFmpeg DLLs with matching installed Python helpers; no Seestar application executed',
              'removed': removed, 'retained_native_count': len(kept),
              'replacement': {'original_sha256': before, 'modified_sha256': after,
                              'method': 'Appended overlay, executable code unchanged; not an independent Qt rebuild'},
              'exit_code': process.returncode}
    if (root / 'probe-result.json').is_file():
        report['probe'] = json.loads((root / 'probe-result.json').read_text())
    (output / 'qt-payload-probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'status': report['status'], 'removed_unused_files': len(removed)}))
    return 0 if process.returncode == 0 else 2


if __name__ == '__main__':
    raise SystemExit(main())
