from .i18n import source as ui_text, tr
import json
from pathlib import Path
from PySide6.QtCore import QStandardPaths, QSaveFile, QIODevice

class SettingsService:

    def __init__(self, path=None):
        self.path = Path(path) if path else profile_directory() / 'settings.json'
        self.values = {'order': [], 'details': {}, 'size': [1600, 960], 'download_dir': '', 'site': {}, 'setup_seen': False, 'view_modes': {}, 'known_devices': {}, 'language': 'auto', 'planner_timezone': '', 'last_plan_id': ''}
        self.values['planner_day_night'] = True
        try:
            loaded = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(loaded, dict):
                for key in self.values:
                    if isinstance(loaded.get(key), type(self.values[key])):
                        self.values[key] = loaded[key]
        except (OSError, ValueError):
            pass

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        target = QSaveFile(str(self.path))
        if not target.open(QIODevice.OpenModeFlag.WriteOnly):
            raise OSError(ui_text('m0172'))
        target.write(json.dumps(self.values, ensure_ascii=False).encode('utf-8'))
        if not target.commit():
            raise OSError(ui_text('m0173'))


def profile_directory(current=None):
    """Reuse an existing legacy profile in place; never duplicate authentication keys.

    An existing new profile takes precedence. Old and new applications share the
    same process mutex, protecting plans/history from concurrent writers.
    """
    current = Path(current) if current else Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation))
    legacy = current.parent.parent / 'SeestarStudio' / 'Seestar Studio'
    if not current.exists() and legacy.is_dir() and not legacy.is_symlink():
        return legacy
    return current
