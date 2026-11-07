# Native onedir build: Qt DLLs remain replaceable; no key/data-folder bundling.
from PyInstaller.utils.hooks import copy_metadata
import os
import sys
from pathlib import Path

# The host PATH may contain unrelated imaging-tool runtimes (e.g. Poppler's
# ICU). Qt uses the Windows ICU ABI; bundling a foreign icuuc.dll breaks startup.
# Resolve dependencies only against this Python/Qt environment and Windows.
site_packages = Path(sys.prefix) / 'Lib' / 'site-packages'
windows = Path(os.environ.get('SystemRoot', r'C:\Windows'))
os.environ['PATH'] = os.pathsep.join(map(str, [
    Path(sys.base_prefix), Path(sys.base_prefix) / 'DLLs',
    Path(sys.prefix) / 'Scripts', site_packages / 'PySide6',
    site_packages / 'shiboken6', windows / 'System32', windows,
]))

a = Analysis(
    ['launcher.py'], pathex=[], binaries=[],
    datas=copy_metadata('seestarpy') + [('LICENSE', '.'), ('THIRD_PARTY_NOTICES.md', '.'), ('seestar_studio/assets', 'seestar_studio/assets'), ('seestar_studio/build_info.json', 'seestar_studio'), ('seestar_studio/catalog_data', 'seestar_studio/catalog_data'), ('seestar_studio/translations', 'seestar_studio/translations'), (str(site_packages / 'PySide6' / 'translations' / 'qtbase_de.qm'), 'PySide6/translations')],
    hiddenimports=['seestar_studio.backend', 'PIL.JpegImagePlugin', 'PIL.PngImagePlugin', 'winrt.windows.foundation', 'winrt.windows.foundation.collections', 'winrt.windows.devices.geolocation'],
    hookspath=['tools/hooks'], hooksconfig={}, runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
              'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtPdf', 'pytest',
              'astropy.visualization', 'astropy.conftest', 'astropy.samp'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='SeestarStudio',
          icon='seestar_studio/assets/SeestarStudio.ico', version='build/version_info.txt',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='SeestarStudio')
