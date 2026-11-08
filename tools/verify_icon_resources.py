"""Check actual executable PE icons against the original multi-size ICO."""
import hashlib
import json
from pathlib import Path
import struct
import pefile
from telescope_desk import __version__


def main():
    root = Path(__file__).resolve().parents[1]
    ico = (root / 'telescope_desk/assets/TelescopeDesk.ico').read_bytes()
    count = struct.unpack_from('<H', ico, 4)[0]
    expected = {}
    for index in range(count):
        w, h, _, _, _, _, size, offset = struct.unpack_from('<BBBBHHII', ico, 6 + index * 16)
        expected[(w or 256, h or 256)] = hashlib.sha256(ico[offset:offset + size]).hexdigest()
    results = []
    for path in [root / 'dist' / __version__ / 'TelescopeDesk/TelescopeDesk.exe',
                 root / 'release' / f'TelescopeDesk-{__version__}-setup-win64.exe']:
        with pefile.PE(str(path)) as pe:
            icons, groups = {}, []
            for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                if kind.id not in (3, 14):
                    continue
                for entry in kind.directory.entries:
                    data = entry.directory.entries[0].data.struct
                    payload = pe.get_data(data.OffsetToData, data.Size)
                    if kind.id == 3:
                        icons[entry.id] = hashlib.sha256(payload).hexdigest()
                    else:
                        groups.append(payload)
            matched = set()
            for group in groups:
                for index in range(struct.unpack_from('<H', group, 4)[0]):
                    w, h, _, _, _, _, _, resource = struct.unpack_from('<BBBBHHIH', group, 6 + index * 14)
                    dimensions = (w or 256, h or 256)
                    if icons.get(resource) == expected.get(dimensions):
                        matched.add(dimensions)
            assert matched == set(expected), f'Original icon sizes missing in {path.name}'
            results.append({'file':path.relative_to(root).as_posix(),
                            'original_icon_sizes':sorted(w for w, _ in matched),
                            'all_icon_payloads_match':True})
    report = {'version':__version__, 'results':results,
              'scope':'PE resources only; not a visual Windows shell/cache inspection'}
    (root / 'reports/beta-icon-resources.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
