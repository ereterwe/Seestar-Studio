"""Public version/build metadata only; never user or device information."""
from importlib.metadata import version, PackageNotFoundError
import json
from pathlib import Path
import sys
from PySide6.QtCore import qVersion
import PySide6
from . import __version__

REPOSITORY = 'https://github.com/ereterwe/Seestar-Studio'


def resource_root():
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]


def public_versions():
    try: seestar = version('seestarpy')
    except PackageNotFoundError: seestar = 'unavailable'
    values = {'Telescope Desk': __version__, 'SeestarPy': seestar, 'PySide6': PySide6.__version__, 'Qt': qVersion()}
    path = Path(__file__).parent/'build_info.json'
    if path.is_file():
        try:
            build = json.loads(path.read_text(encoding='utf-8'))
            if build.get('version') == __version__:
                for key in ('build_utc', 'source_sha256'):
                    if isinstance(build.get(key), str): values[key] = build[key]
        except (OSError,ValueError):pass
    return values


def local_references(root=None):
    root = root or resource_root()
    return {name: root/name for name in ('LICENSE','THIRD_PARTY_NOTICES.md','LICENSING.md','TelescopeDesk-source.zip') if (root/name).is_file()}
