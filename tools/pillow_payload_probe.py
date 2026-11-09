"""Exercise retained Pillow extension bytes and actual image pipeline offline.

Python helper files come from the matching installed Pillow. The application's
frozen archive is inspected separately to establish excluded module absence.
"""
import argparse
import hashlib
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile


def child(folder):
    sys.path.insert(0, str(folder))
    sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
    import io
    import socket
    from unittest.mock import patch
    import numpy as np
    from PIL import Image, _imaging
    assert Path(_imaging.__file__).resolve().is_relative_to(folder)
    with patch.object(socket.socket, 'sendto', side_effect=OSError('offline test')), \
         patch.object(socket.socket, 'recvfrom', side_effect=OSError('offline test')), \
         patch.object(socket, 'gethostbyname', side_effect=socket.gaierror('offline test')):
        from telescope_desk.imaging import ImagePipeline
        from seestarpy.dashboard.monitor import _fit_and_encode
    pipeline = ImagePipeline()
    cases = []
    for size in [(32, 24), (101, 67), (1920, 1080)]:
        image = Image.new('RGB', size, (73, 117, 191))
        for progressive in (False, True):
            output = io.BytesIO()
            image.save(output, format='JPEG', progressive=progressive)
            decoded = pipeline.decode({'width': 0, 'height': 0}, output.getvalue())
            assert (decoded.width(), decoded.height()) == size
            assert abs(decoded.pixelColor(0, 0).red() - 73) < 4
            path = folder / 'export.png'
            assert decoded.save(str(path))
            with Image.open(path) as exported:
                assert exported.size == size
            cases.append({'size': size, 'progressive': progressive})
    raw = np.arange(32 * 24 * 3, dtype=np.uint16).reshape(24, 32, 3)
    decoded = pipeline.decode({'width': 32, 'height': 24}, raw.tobytes())
    assert (decoded.width(), decoded.height()) == (32, 24)
    reduced = pipeline.decode({'width': 32, 'height': 24}, raw[:, :, 0].copy().tobytes())
    assert (reduced.width(), reduced.height()) == (16, 12)
    encoded = _fit_and_encode(Image.new('RGB', (120, 80)), 60, 85)
    assert encoded[:2] == b'\xff\xd8'
    try:
        pipeline.decode({'width': 0, 'height': 0}, b'\xff\xd8\xffbroken')
    except Exception:
        pass
    else:
        raise AssertionError('Corrupt JPEG accepted')
    result = {'jpeg_cases': cases, 'png_roundtrip': True, 'raw_rgb': True,
              'raw_bayer': True, 'dashboard_jpeg_encode': True, 'corrupt_jpeg_rejected': True,
              'core_reported_versions': {name: getattr(_imaging, name, None) for name in
                  ('jpeglib_version', 'libjpeg_turbo_version', 'libtiff_version',
                   'jp2klib_version', 'zlib_version', 'zlib_ng_version')}}
    (folder / 'result.json').write_text(json.dumps(result), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--child', type=Path)
    args = parser.parse_args()
    if args.child:
        child(args.child.resolve())
        return
    from PyInstaller.archive.readers import CArchiveReader
    reader = CArchiveReader(str(args.target / 'TelescopeDesk.exe'))
    pyz = reader.open_embedded_archive(next(n for n, d in reader.toc.items() if d[-1] == 'z'))
    excluded = ['PIL.ImageTk', 'PIL._imagingtk', 'PIL.ImageCms', 'PIL._imagingcms',
                'PIL.WebPImagePlugin', 'PIL._webp', 'PIL.AvifImagePlugin', 'PIL._avif']
    assert not set(excluded) & set(pyz.toc)
    binaries = list((args.target / '_internal/PIL').glob('*.pyd'))
    assert [p.name.split('.')[0] for p in binaries] == ['_imaging']
    from PIL import __file__ as installed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pillow-probe-', dir=args.output.parent) as temporary:
        folder = Path(temporary)
        shutil.copytree(Path(installed).parent, folder / 'PIL',
                        ignore=lambda directory, names: [n for n in names if n.endswith(('.pyd', '.pyc')) or n == '__pycache__'])
        for binary in binaries:
            shutil.copyfile(binary, folder / 'PIL' / binary.name)
        process = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(folder)],
                                 capture_output=True, timeout=45)
        args.output.with_suffix('.stderr.txt').write_bytes(process.stderr)
        if process.returncode:
            raise RuntimeError('Offline payload probe failed; see local stderr report')
        report = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
    report.update({'excluded_frozen_modules': excluded, 'hardware_test': False,
        'pillow_binary_sha256': hashlib.sha256(binaries[0].read_bytes()).hexdigest(),
        'scope': 'Actual packaged Pillow extension, matching installed Python helpers, current application pipeline; Qt/NumPy from development environment'})
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Pillow payload probe passed')


if __name__ == '__main__':
    main()
