"""DE/EN native visual QA, isolated settings and explicitly simulated devices."""
import json
import sys
import time
import uuid
from pathlib import Path
from dataclasses import replace
from PySide6.QtCore import QTimer, QDate
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel, QAbstractButton
import re
from PySide6.QtGui import QImage, QColor
from seestar_studio.i18n import TranslationController
from seestar_studio.window import DashboardWindow
from seestar_studio.settings import SettingsService
from seestar_studio.theme import STYLE
from seestar_studio.files.browser import FileBrowserService
from seestar_studio.files.downloads import DownloadService
from seestar_studio.planner import PlanEntry
from seestar_studio.models import ImageFrame
from seestar_studio.setup_service import SetupService
from seestar_studio.setup_wizard import SetupWizard
from seestar_studio.preferences import PreferencesDialog
from seestar_studio.about import AboutDialog
from seestar_studio.sky.site import SiteDialog
from seestar_studio.sky.astronomy import Site
from seestar_studio.location import LocationProposal
from seestar_studio.branding import app_icon
from seestar_studio.diagnostics import DiagnosticsDialog, diagnostic_snapshot
from tests.test_ui import FakeManager
from tests.test_control import fleet


class NoNetworkClient:
    def __init__(self,*args):raise ConnectionError('SIMULATION: no network')


def main():
    app=QApplication([]);app.setWindowIcon(app_icon());app.setStyle('Fusion');app.setStyleSheet(STYLE)
    app.translations=TranslationController(app,'de')
    root=Path('reports')/('b2-ui-'+uuid.uuid4().hex[:8]);root.mkdir(parents=True)
    manager=FakeManager(0)
    for sn,(info,tel,_) in fleet().items():
        img=QImage(300,500,QImage.Format.Format_RGB32);img.fill(QColor('#25374d'))
        manager.data[sn]=(replace(info,model='SIMULATION / '+info.model),tel,ImageFrame(img,1,time.time(),'stacked','SIMULATION'))
    settings=SettingsService(root/'settings.json')
    window=DashboardWindow(manager,settings,FileBrowserService(root/'cache',NoNetworkClient),DownloadService(NoNetworkClient))
    window.resize(1920,1080);window.show();window.refresh()
    def prepare():
        keys=list(manager.data)
        window.sky.site=Site(52,13,0,'Europe/Berlin')
        window.planner.date.setDate(QDate(2026,11,6))
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
            PreferencesDialog(settings),DiagnosticsDialog(diagnostic_snapshot(manager.data,False)), AboutDialog(), SiteDialog({}, devices=lambda:manager.data)]
        for dialog in dialogs:
            if isinstance(dialog,SiteDialog):dialog.show_windows_error('denied')
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
    def capture_en():
        capture('en')
        QTimer.singleShot(500,window.close)
    def capture_de():
        capture('de')
        QTimer.singleShot(500,capture_en)
    QTimer.singleShot(5000,capture_de)
    code=app.exec()
    Path('reports/b2-ui-latest.json').write_text(json.dumps({'directory':str(root.resolve()),'exit_code':code,'synthetic':True,'solar_ready':window.planner.timeline.solar is not None,'solar_events':len(window.planner.timeline.solar.events) if window.planner.timeline.solar else 0,'clean_shutdown':not window.workers_running()},indent=2),encoding='utf-8')
    return code


if __name__=='__main__':raise SystemExit(main())
