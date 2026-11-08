from .i18n import QFileDialog, QMessageBox
'Explicit local diagnostic export, with a small privacy-preserving schema.'
from .i18n import source as ui_text, tr
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import re
from PySide6.QtCore import QSaveFile, QIODevice
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QComboBox
from .card import label, button
from . import __version__

def diagnostic_snapshot(data, key_configured, history_error=None, feature="general"):
    from .metadata import public_versions
    feature = feature if feature in {"general","live_stack","live_view","telemetry","files","sky","planner","history","setup","location","about"} else "general"
    packages = {}
    for name in ('seestarpy', 'PySide6', 'numpy', 'Pillow', 'astropy', 'pysmb'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = 'not available'
    devices = []
    for index, (_, (info, telemetry, frame)) in enumerate(data.items(), 1):
        devices.append({'device': index, 'model': info.model if re.fullmatch(r'Seestar S[0-9]+(?: Pro)?',str(info.model)) else 'unknown', 'firmware': telemetry.get('firmware') if re.fullmatch(r'[vV]?[0-9]+(?:[.\-][0-9]+){0,6}',str(telemetry.get('firmware'))) else None, 'connected': telemetry.connected, 'paused': telemetry.paused, 'status_age_seconds': telemetry.get('age_s'), 'frame_sequence': frame.sequence if frame else None, 'frame_kind': frame.kind if frame else None, 'frame_size': [frame.image.width(), frame.image.height()] if frame else None, 'status_error_present': bool(telemetry.error), 'image_error_present': bool(telemetry.image_error), 'capabilities': {k: v for k, v in (telemetry.get('capabilities') or {}).items() if isinstance(k, str) and k.startswith('can_') and (type(v) is bool)}})
    return {'schema': 2, 'versions': public_versions(), 'affected_feature': feature, 'error_categories': (["history_write_failed"] if history_error else []) + (["status_read_failed"] if any(t.error for _,t,_ in data.values()) else []) + (["image_receive_failed"] if any(t.image_error for _,t,_ in data.values()) else []), 'application_version': __version__, 'created_utc': datetime.now(timezone.utc).isoformat(), 'platform': {'system': platform.system(), 'release': platform.release(), 'machine': platform.machine()}, 'packages': packages, 'local_authentication_configured': bool(key_configured), 'history_error_present': bool(history_error), 'devices': devices, 'privacy': 'No serials, IPs, paths, keys, targets, locations, images or raw RPC bodies. Local export only.'}

class DiagnosticsDialog(QDialog):

    def __init__(self, snapshot, parent=None):
        super().__init__(parent)
        self.setWindowTitle(ui_text('m0078'))
        self.resize(800, 650)
        self.text = json.dumps(snapshot, indent=2, ensure_ascii=False)
        self.snapshot = dict(snapshot)
        layout = QVBoxLayout(self)
        note = label(ui_text('diagnostics.privacy'), 'muted')
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addWidget(label(ui_text('diagnostics.feature')))
        self.feature = QComboBox()
        for key, title in [('general','Telescope Desk'),('live_stack',ui_text('m0432')),('live_view','Live View'),
                           ('files',ui_text('m0433')),('sky',ui_text('m0434')),('planner',ui_text('m0435')),
                           ('history',ui_text('m0397')),('setup',ui_text('m0239')),('location',ui_text('m0355')),('about',ui_text('about.title'))]:
            self.feature.addItem(title,key)
        self.feature.setCurrentIndex(max(0,self.feature.findData(snapshot.get('affected_feature','general'))))
        layout.addWidget(self.feature)
        self.preview = QPlainTextEdit(self.text)
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview, 1)
        self.feature.currentIndexChanged.connect(self.update_feature)
        layout.addWidget(button(ui_text('m0081'), self.save))
        layout.addWidget(button(ui_text('m0082'), self.accept))

    def update_feature(self):
        self.snapshot['affected_feature'] = self.feature.currentData()
        self.text = json.dumps(self.snapshot, indent=2, ensure_ascii=False)
        self.preview.setPlainText(self.text)

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, ui_text('m0080'), 'TelescopeDesk-diagnostics.json', 'JSON (*.json)')
        if not path:
            return
        output = QSaveFile(path)
        if not output.open(QIODevice.OpenModeFlag.WriteOnly):
            QMessageBox.warning(self, ui_text('m0083'), ui_text('m0084'))
            return
        output.write(self.text.encode('utf-8'))
        if not output.commit():
            QMessageBox.warning(self, ui_text('m0083'), ui_text('m0085'))
