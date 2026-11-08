"""DE/EN native visual QA, isolated settings and explicitly simulated devices."""
import json
import sys
import time
import uuid
from pathlib import Path
from dataclasses import replace
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel, QAbstractButton
import re
from PySide6.QtGui import QImage, QColor
from telescope_desk.i18n import TranslationController
from telescope_desk.window import DashboardWindow
from telescope_desk.settings import SettingsService
from telescope_desk.theme import STYLE
from telescope_desk.files.browser import FileBrowserService
from telescope_desk.files.downloads import DownloadService
from telescope_desk.planner import PlanEntry
from telescope_desk.models import ImageFrame
from telescope_desk.setup_service import SetupService
from telescope_desk.setup_wizard import SetupWizard
from telescope_desk.preferences import PreferencesDialog
from telescope_desk.diagnostics import DiagnosticsDialog, diagnostic_snapshot
from tests.test_ui import FakeManager
from tests.test_control import fleet


class NoNetworkClient:
    def __init__(self,*args):raise ConnectionError('SIMULATION: no network')


def main():
    app=QApplication([]);app.setStyle('Fusion');app.setStyleSheet(STYLE)
    app.translations=TranslationController(app,'de')
    root=Path('reports')/('v22-ui-'+uuid.uuid4().hex[:8]);root.mkdir(parents=True)
    manager=FakeManager(0)
    for sn,(info,tel,_) in fleet().items():
        img=QImage(300,500,QImage.Format.Format_RGB32);img.fill(QColor('#25374d'))
        manager.data[sn]=(replace(info,model='SIMULATION / '+info.model),tel,ImageFrame(img,1,time.time(),'stacked','SIMULATION'))
    settings=SettingsService(root/'settings.json')
    window=DashboardWindow(manager,settings,FileBrowserService(root/'cache',NoNetworkClient),DownloadService(NoNetworkClient))
    window.resize(1920,1080);window.show();window.refresh()
    def prepare():
        keys=list(manager.data)
        window.planner.start.setText('2026-11-06T20:00:00+01:00')
        window.planner.entries=[PlanEntry('one',keys[0],'NGC0224',120,'2026-11-06T20:00:00+01:00'),
            PlanEntry('two',keys[0],'NGC0598',60,'2026-11-06T22:05:00+01:00'),
            PlanEntry('three',keys[1],'NGC7000',90,'2026-11-06T20:00:00+01:00')]
        window.planner.invalidate()
    def capture(language):
        app.translations.set_language(language)
        for index in range(window.tabs.count()):
            window.tabs.setCurrentIndex(index);app.translations.refresh();app.processEvents()
            window.grab().save(str(root/f'{language}-tab{index}.png'))
        dialogs=[SetupWizard(root/'auth',lambda:{},service=SetupService(root/'auth',detector=lambda:None)),
            PreferencesDialog(settings),DiagnosticsDialog(diagnostic_snapshot(manager.data,False))]
        for dialog in dialogs:
            dialog.show();app.translations.refresh();app.processEvents()
            dialog.grab().save(str(root/f'{language}-{type(dialog).__name__}.png'))
            dialog.reject();dialog.deleteLater()
        if language=='en':
            leftovers=[]
            for w in app.allWidgets():
                if isinstance(w,(QLabel,QAbstractButton)):
                    text=w.text()
                    if re.search(r'[äöüÄÖÜß]|\b(Gerät|Ziel|Aufnahme|Speichern|Laden|Einpassen|Montierung|Speicher|Sekunden)\b',text):leftovers.append(text)
            (root/'english-audit.json').write_text(json.dumps(sorted(set(leftovers)),ensure_ascii=False,indent=2),encoding='utf-8')
        print('UI capture',language,root,flush=True)
    QTimer.singleShot(2500,prepare)
    QTimer.singleShot(5000,lambda:capture('de'))
    QTimer.singleShot(7500,lambda:capture('en'))
    QTimer.singleShot(10000,window.close)
    code=app.exec()
    Path('reports/v22-ui-latest.json').write_text(json.dumps({'directory':str(root.resolve()),'exit_code':code,'synthetic':True,'clean_shutdown':not window.workers_running()},indent=2),encoding='utf-8')
    return code


if __name__=='__main__':raise SystemExit(main())
