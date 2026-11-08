"""Read actual bundled FFmpeg format/protocol registries without network traffic."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path


class Format(ctypes.Structure):
    _fields_ = [('name', ctypes.c_char_p), ('long_name', ctypes.c_char_p)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    folder = a.target.resolve() / '_internal/PySide6'
    path = next(folder.glob('avformat-*.dll'))
    directory = os.add_dll_directory(str(folder))
    lib = ctypes.CDLL(str(path))
    result = {'file': path.relative_to(a.target.resolve()).as_posix(),
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'scope': 'Registered compiled capabilities, not tested device formats'}
    for key, symbol in [('demuxers', 'av_demuxer_iterate'), ('muxers', 'av_muxer_iterate')]:
        fn = getattr(lib, symbol)
        fn.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        fn.restype = ctypes.POINTER(Format)
        opaque = ctypes.c_void_p()
        names = []
        while True:
            entry = fn(ctypes.byref(opaque))
            if not entry:break
            names.append(entry.contents.name.decode('ascii'))
            if len(names) > 4096:raise ValueError('Registry bound exceeded')
        result[key] = sorted(names)
    lib.avio_enum_protocols.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
    lib.avio_enum_protocols.restype = ctypes.c_char_p
    for output in (0, 1):
        opaque = ctypes.c_void_p();names = []
        while True:
            name = lib.avio_enum_protocols(ctypes.byref(opaque), output)
            if not name:break
            names.append(name.decode('ascii'))
            if len(names) > 4096:raise ValueError('Registry bound exceeded')
        result['output_protocols' if output else 'input_protocols'] = sorted(names)
    lib.avformat_configuration.restype = ctypes.c_char_p
    result['configuration'] = lib.avformat_configuration().decode('utf-8')
    result['standalone_avfilter_files'] = [x.name for x in folder.glob('avfilter*')]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    directory.close()
    print({k: len(result[k]) for k in ('demuxers','muxers','input_protocols','output_protocols')})


if __name__ == '__main__':main()
