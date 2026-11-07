"""Central DE/EN resources and live Qt presentation translation.

Domain messages use stable source text; protocol values and persisted data are
never translated. The presentation layer can change language without rebuilding
windows, stopping workers or invalidating control confirmations.
"""
from functools import lru_cache
import json
from pathlib import Path
import re
from PySide6.QtCore import QObject, QTimer, QEvent, QLocale, QTranslator, QLibraryInfo, Signal
from PySide6.QtWidgets import (QApplication, QLabel, QAbstractButton, QComboBox, QPushButton,
    QLineEdit, QTableWidget, QTreeWidget, QTabWidget, QGroupBox, QSpinBox,
    QDoubleSpinBox, QDateTimeEdit, QWizardPage, QMessageBox as QtMessageBox,
    QFileDialog as QtFileDialog)

RESOURCES = json.loads((Path(__file__).parent / 'translations' / 'messages.json').read_text(encoding='utf-8'))
LANGUAGE = 'de'
_exact = {}; _patterns = []
for key, entry in RESOURCES.items():
    for variant in set(entry.values()):
        _exact[variant] = key
        if '{p' in variant:
            names = re.findall(r'\{(p\d+)\}', variant)
            parts = re.split(r'\{p\d+\}', variant)
            if len(set(names)) == len(names):
                pattern = ''.join(re.escape(part) + (f'(?P<{names[i]}>.*?)' if i < len(names) else '') for i, part in enumerate(parts))
                _patterns.append((re.compile('^'+pattern+'$', re.DOTALL), key))

# Specific composed messages must win over generic description templates whose
# final placeholder could otherwise swallow the rest of a multi-line panel.
_patterns.sort(key=lambda item: len(item[0].pattern)-16*item[0].pattern.count('(?P<'),reverse=True)
_prefixes=sorted((text for text in _exact if '{p' not in text and len(text)>20
                 and (text.endswith('.') or text.endswith(' '))),key=len,reverse=True)


def source(key):
    return RESOURCES.get(key, {}).get('source', key)


def language_for(choice, system=None):
    if choice in ('de', 'en'): return choice
    return 'de' if (system or QLocale.system().name()).lower().startswith('de') else 'en'


@lru_cache(maxsize=8192)
def translate(value, language, depth=0):
    if not isinstance(value, str) or not value: return value
    key = _exact.get(value)
    if key: return RESOURCES[key].get(language) or RESOURCES[key]['source']
    if depth > 8: return value
    if value.endswith(' …'):return translate(value[:-2],language,depth+1)+' …'
    for pattern, key in _patterns:
        match = pattern.fullmatch(value)
        if match:
            fields = {k: translate(v, language, depth+1) for k,v in match.groupdict().items()}
            try: return RESOURCES[key][language].format(**fields)
            except (KeyError,ValueError): return value
    for prefix in _prefixes:
        if value.startswith(prefix) and value!=prefix:
            return translate(prefix,language,depth+1)+translate(value[len(prefix):],language,depth+1)
    # Composed status/tooltip lines retain unknown protocol data verbatim.
    for separator in ('\n', ' · ', '; '):
        if separator in value:
            return separator.join(translate(part,language,depth+1) for part in value.split(separator))
    for prefix in ('VERALTET · ', 'Gespeichert: ', 'Gefunden: ', 'Dateizugriff fehlgeschlagen: '):
        if value.startswith(prefix): return translate(prefix,language,depth+1)+value[len(prefix):]
    return value


def tr(value): return translate(value, LANGUAGE)
def locale(): return QLocale('de_DE' if LANGUAGE == 'de' else 'en_US')


class Label(QLabel):
    def __init__(self, text='', parent=None):
        super().__init__(tr(text),parent)
    def setText(self,text): super().setText(tr(text))


class Button(QPushButton):
    def __init__(self,text='',parent=None):super().__init__(tr(text),parent)
    def setText(self,text):super().setText(tr(text))


class QMessageBox(QtMessageBox):
    @staticmethod
    def information(parent,title,text,*args,**kwargs): return QtMessageBox.information(parent,tr(title),tr(text),*args,**kwargs)
    @staticmethod
    def warning(parent,title,text,*args,**kwargs): return QtMessageBox.warning(parent,tr(title),tr(text),*args,**kwargs)
    @staticmethod
    def question(parent,title,text,*args,**kwargs): return QtMessageBox.question(parent,tr(title),tr(text),*args,**kwargs)
    @staticmethod
    def critical(parent,title,text,*args,**kwargs): return QtMessageBox.critical(parent,tr(title),tr(text),*args,**kwargs)


class QFileDialog(QtFileDialog):
    @staticmethod
    def getSaveFileName(parent=None,caption='',directory='',filter='',*args,**kwargs):
        return QtFileDialog.getSaveFileName(parent,tr(caption),directory,tr(filter),*args,**kwargs)
    @staticmethod
    def getOpenFileName(parent=None,caption='',directory='',filter='',*args,**kwargs):
        return QtFileDialog.getOpenFileName(parent,tr(caption),directory,tr(filter),*args,**kwargs)
    @staticmethod
    def getExistingDirectory(parent=None,caption='',directory='',*args,**kwargs):
        return QtFileDialog.getExistingDirectory(parent,tr(caption),directory,*args,**kwargs)


class TranslationController(QObject):
    language_changed = Signal(str)
    def __init__(self, app, choice='auto'):
        super().__init__(app); self.app=app; self.translator=QTranslator(self)
        self._busy=False; self._pending=False
        app.installEventFilter(self)
        self.timer=QTimer(self);self.timer.timeout.connect(self.refresh);self.timer.start(500)
        self.set_language(choice)

    def set_language(self,choice):
        global LANGUAGE
        LANGUAGE=language_for(choice)
        self.app.removeTranslator(self.translator)
        if LANGUAGE=='de':
            directory=QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            if self.translator.load('qtbase_de',directory):self.app.installTranslator(self.translator)
        QLocale.setDefault(locale());self.refresh();self.language_changed.emit(LANGUAGE)

    def eventFilter(self,obj,event):
        if event.type() in (QEvent.Type.Show,QEvent.Type.LanguageChange) and not self._busy:
            if not self._pending:
                self._pending=True;QTimer.singleShot(0,self.refresh)
        return False

    def refresh(self):
        if self._busy:return
        self._busy=True;self._pending=False
        try:
            for widget in self.app.allWidgets(): self.apply(widget)
        finally:self._busy=False

    def field(self,obj,key,getter,setter):
        current=getter()
        previous=obj.property('_i18n_last_'+key)
        original=obj.property('_i18n_source_'+key)
        if current!=previous or original is None:original=current
        translated=tr(original)
        obj.setProperty('_i18n_source_'+key,original);obj.setProperty('_i18n_last_'+key,translated)
        if translated!=current:setter(translated)

    def apply(self,w):
        blocked=w.blockSignals(True)
        try:
            self.field(w,'title',w.windowTitle,w.setWindowTitle)
            self.field(w,'tooltip',w.toolTip,w.setToolTip)
            if isinstance(w,(QLabel,QAbstractButton)):self.field(w,'text',w.text,w.setText)
            if isinstance(w,QLineEdit):self.field(w,'placeholder',w.placeholderText,w.setPlaceholderText)
            if isinstance(w,QGroupBox):self.field(w,'group',w.title,w.setTitle)
            if isinstance(w,QWizardPage):
                self.field(w,'page',w.title,w.setTitle);self.field(w,'subtitle',w.subTitle,w.setSubTitle)
            if isinstance(w,QComboBox):
                for i in range(w.count()):self.field(w,'item'+str(i),lambda i=i:w.itemText(i),lambda text,i=i:w.setItemText(i,text))
            if isinstance(w,QTabWidget):
                for i in range(w.count()):self.field(w,'tab'+str(i),lambda i=i:w.tabText(i),lambda text,i=i:w.setTabText(i,text))
            if isinstance(w,(QSpinBox,QDoubleSpinBox)):
                w.setLocale(locale());self.field(w,'suffix',w.suffix,w.setSuffix);self.field(w,'prefix',w.prefix,w.setPrefix)
            if isinstance(w,QDateTimeEdit):
                w.setLocale(locale())
                if w.displayFormat() in ('dd.MM.yyyy','MMM d, yyyy'):w.setDisplayFormat('dd.MM.yyyy' if LANGUAGE=='de' else 'MMM d, yyyy')
                elif 'HH:mm' in w.displayFormat() or 'h:mm' in w.displayFormat():
                    fmt=('dd.MM.yyyy' if LANGUAGE=='de' else 'MMM d, yyyy')+' '+QLocale.system().timeFormat(QLocale.FormatType.ShortFormat)
                    w.setDisplayFormat(fmt)
            if isinstance(w,QTableWidget):
                for col in range(w.columnCount()):
                    item=w.horizontalHeaderItem(col)
                    if item:item.setText(tr(item.text()))
                for row in range(w.rowCount()):
                    for col in range(w.columnCount()):
                        item=w.item(row,col)
                        if item:item.setText(tr(item.text()))
            if isinstance(w,QTreeWidget):
                for col in range(w.columnCount()):w.headerItem().setText(col,tr(w.headerItem().text(col)))
            for action in w.actions():
                self.field(action,'text',action.text,action.setText)
        finally:w.blockSignals(blocked)
