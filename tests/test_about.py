import json
from pathlib import Path
from PIL import Image
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QDialog, QPlainTextEdit
from seestar_studio.about import AboutDialog
from seestar_studio.metadata import public_versions, REPOSITORY
from seestar_studio.branding import app_icon, icon_path
from seestar_studio import __version__


def test_original_icon_has_windows_sizes_and_transparency(app):
    icon=Image.open(icon_path())
    assert icon.ico.sizes()=={(x,x) for x in (16,24,32,48,64,128,256)}
    for size in icon.ico.sizes():
        image=icon.ico.getimage(size).convert('RGBA')
        assert image.getpixel((0,0))[3]<=3  # Lanczos edge ringing at small sizes
        assert image.getbbox() is not None
    assert not app_icon().isNull()


def test_about_real_versions_links_and_private_repository(app,tmp_path,monkeypatch):
    (tmp_path/'LICENSE').write_text('test license',encoding='utf-8')
    dialog=AboutDialog(root=tmp_path)
    assert dialog.versions['Seestar Studio']==__version__
    assert dialog.versions['Qt'] and dialog.versions['PySide6']
    assert dialog.actions_by_file['LICENSE'].isEnabled()
    assert not dialog.actions_by_file['LICENSING.md'].isEnabled()
    dialog.copy_versions()
    assert json.loads(QApplication.clipboard().text())==public_versions()
    from seestar_studio import about
    opened=[]
    monkeypatch.setattr(about.QDesktopServices,'openUrl',lambda url:opened.append(url) or True)
    dialog.open_repository();assert opened[0].toString()==REPOSITORY
    dialog.open_source();assert opened[1].isLocalFile()
    monkeypatch.setattr(QDialog,'exec',lambda self:0)
    dialog.open_document('LICENSE')
    assert any(w.toPlainText()=='test license' for w in dialog.findChildren(QPlainTextEdit))
    dialog.reject();dialog.deleteLater()
