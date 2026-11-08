"""Shared original icon and stable Windows desktop identity."""
from pathlib import Path
import sys
from PySide6.QtGui import QIcon


def icon_path():
    return Path(__file__).parent / 'assets' / 'TelescopeDesk.ico'


def app_icon():
    return QIcon(str(icon_path()))


def set_windows_identity():
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('TelescopeDesk.Desktop')
