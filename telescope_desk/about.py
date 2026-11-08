"""Scrollable credits, actual versions and verified local licensing references."""
import json
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QScrollArea, QPlainTextEdit, QApplication
from .i18n import source as ui_text, tr, QMessageBox
from .card import label, button
from .branding import app_icon
from .metadata import public_versions, local_references, resource_root, REPOSITORY


class AboutDialog(QDialog):
    def __init__(self, parent=None, root=None):
        super().__init__(parent)
        self.setWindowTitle(ui_text('about.title'))
        self.setWindowIcon(app_icon())
        self.resize(800, 700)
        self.root = root or resource_root()
        self.references = local_references(self.root)
        self.versions = public_versions()
        outer = QVBoxLayout(self)
        header = QHBoxLayout()
        icon = label('');icon.setPixmap(app_icon().pixmap(64,64));header.addWidget(icon)
        heading = QVBoxLayout();heading.addWidget(label('TELESCOPE DESK','brand'))
        heading.addWidget(label(self.versions['Telescope Desk'],'eyebrow'))
        header.addLayout(heading);header.addStretch();outer.addLayout(header)
        scroll = QScrollArea();scroll.setWidgetResizable(True)
        content = QWidget();body = QVBoxLayout(content)
        paragraphs = [ui_text('about.description'),ui_text('about.project'),ui_text('about.mark'),
            ui_text('about.codex'),ui_text('about.origin'),ui_text('about.licenses'),
            ui_text('about.license_text'),ui_text('about.independent'),ui_text('about.private'),
            REPOSITORY,ui_text('about.private_note'),ui_text('about.local')]
        for text in paragraphs:
            item=label(text,'muted');item.setTextFormat(Qt.TextFormat.PlainText);item.setWordWrap(True)
            item.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            body.addWidget(item)
        body.addWidget(label('\n'.join(self.references), 'muted'))
        body.addStretch();scroll.setWidget(content);outer.addWidget(scroll,1)
        versions = QPlainTextEdit(self.version_text());versions.setReadOnly(True);versions.setMaximumHeight(130)
        outer.addWidget(versions)
        actions = QGridLayout()
        self.actions_by_file = {}
        for i,(name,title) in enumerate([('LICENSE',ui_text('about.license')),('THIRD_PARTY_NOTICES.md',ui_text('about.notices')),('LICENSING.md',ui_text('about.review'))]):
            action=button(title,lambda checked=False,n=name:self.open_document(n))
            action.setEnabled(name in self.references);actions.addWidget(action,0,i)
            self.actions_by_file[name]=action
        source=button(ui_text('about.source'),self.open_source)
        source.setEnabled('TelescopeDesk-source.zip' in self.references or (self.root/'telescope_desk').is_dir())
        actions.addWidget(source,1,0)
        actions.addWidget(button(ui_text('about.repository'),self.open_repository),1,1)
        actions.addWidget(button(ui_text('about.copy'),self.copy_versions),1,2)
        outer.addLayout(actions)
        self.status=label('','muted');outer.addWidget(self.status)
        outer.addWidget(button(ui_text('m0082'),self.accept))

    def version_text(self):
        return json.dumps(self.versions,ensure_ascii=False,indent=2)

    def copy_versions(self):
        QApplication.clipboard().setText(self.version_text())
        self.status.setText(ui_text('about.copied'))

    def open_url(self,url):
        if not QDesktopServices.openUrl(url):self.status.setText(ui_text('about.open_failed'))

    def open_repository(self):
        self.open_url(QUrl(REPOSITORY))

    def open_source(self):
        self.open_url(QUrl.fromLocalFile(str(self.root)))

    def open_document(self,name):
        path=self.references.get(name)
        if path is None or not path.is_file():
            self.status.setText(ui_text('about.open_failed'));return
        # Built-in viewer also works on a fresh PC without a Markdown association.
        dialog=QDialog(self);dialog.setWindowTitle(name);dialog.resize(850,650)
        layout=QVBoxLayout(dialog)
        try:text=path.read_text(encoding='utf-8')
        except (OSError,UnicodeError):
            self.status.setText(ui_text('about.open_failed'));return
        viewer=QPlainTextEdit(text);viewer.setReadOnly(True);layout.addWidget(viewer)
        layout.addWidget(button(ui_text('m0082'),dialog.accept));dialog.exec()
