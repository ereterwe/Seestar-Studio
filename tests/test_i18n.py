import ast
import re
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox
from seestar_studio import i18n
from seestar_studio.telemetry import number
from seestar_studio.settings import SettingsService


def test_catalog_complete_placeholders_and_code_references():
    for key,value in i18n.RESOURCES.items():
        assert value['de'] and value['en']
        assert set(re.findall(r'\{p\d+\}',value['source']))==set(re.findall(r'\{p\d+\}',value['en']))
        assert set(re.findall(r'\{p\d+\}',value['source']))==set(re.findall(r'\{p\d+\}',value['de']))
    for path in Path('seestar_studio').rglob('*.py'):
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        for n in ast.walk(tree):
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ui_text':
                assert n.args[0].value in i18n.RESOURCES, (path,n.args[0].value)


def test_language_detection_fallback_and_dynamic_templates():
    assert i18n.language_for('auto','de_DE')=='de'
    assert i18n.language_for('auto','fr_FR')=='en'
    assert i18n.language_for('en','de_DE')=='en'
    assert i18n.translate('unknown protocol/value','en')=='unknown protocol/value'
    assert i18n.translate('GoTo zum ausgewählten Ziel …','en')=='GoTo selected target …'
    value='Größe für ein einzelnes Bildfeld prüfen. Heuristik; Himmel, Filter und Flächenhelligkeit sind nicht bewertet.'
    translated=i18n.translate(value,'en')
    assert 'Größe' not in translated and 'Heuristik' not in translated and 'field of view' in translated
    assert i18n.translate('Gespeichert: C:/private/M31.png','en')=='Saved: C:/private/M31.png'
    assert i18n.translate('2 Ziele · 1 mit Hinweis/Konflikt. Keine Ausführung.','en')=='2 targets · 1 with notice/conflict. No execution.'
    assert i18n.translate('2 targets · 1 with notice/conflict. No execution.','de')=='2 Ziele · 1 mit Hinweis/Konflikt. Keine Ausführung.'


def test_live_language_change_keeps_protocol_values_and_selection(app,tmp_path):
    controller=i18n.TranslationController(app,'de')
    dialog=QDialog();layout=QVBoxLayout(dialog)
    text=QLabel('Ziel nicht verfügbar');button=QPushButton('Speichern …')
    combo=QComboBox();combo.addItem('Hauptkamera','main');combo.addItem('Weitwinkelkamera','wide');combo.setCurrentIndex(1)
    for w in (text,button,combo):layout.addWidget(w)
    emitted=[];combo.currentIndexChanged.connect(emitted.append)
    try:
        controller.set_language('en')
        assert text.text()=='Target unavailable' and combo.currentText()=='Wide-angle camera'
        assert combo.currentData()=='wide' and not emitted
        assert number(10.5,' s',1)=='10.5 s'
        controller.set_language('de')
        assert text.text()=='Ziel nicht verfügbar' and number(10.5,' s',1)=='10,5 s'
        settings=SettingsService(tmp_path/'settings.json');settings.values['language']='en';settings.save()
        assert SettingsService(settings.path).values['language']=='en'
    finally:
        controller.set_language('de');controller.timer.stop();app.removeEventFilter(controller);controller.deleteLater();dialog.close();dialog.deleteLater()
