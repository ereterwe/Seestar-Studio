from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QApplication
from .i18n import source as ui_text, TranslationController
from .card import label, button

class PreferencesDialog(QDialog):

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle(ui_text('settings.title'))
        self.resize(600, 200)
        layout = QFormLayout(self)
        self.language = QComboBox()
        for key, name in [('auto', ui_text('settings.auto')), ('de', 'Deutsch'), ('en', 'English')]:
            self.language.addItem(name, key)
        self.language.setCurrentIndex(max(0, self.language.findData(settings.values['language'])))
        layout.addRow(ui_text('settings.language'), self.language)
        note = label(ui_text('settings.note'), 'muted')
        note.setWordWrap(True)
        layout.addRow(note)
        layout.addRow(button(ui_text('settings.close'), self.accept))

        def change():
            settings.values['language'] = self.language.currentData()
            app = QApplication.instance()
            if not hasattr(app, 'translations'):
                app.translations = TranslationController(app)
            app.translations.set_language(settings.values['language'])
            try:
                settings.save()
            except OSError:
                note.setText(ui_text('settings.save_error'))
            if parent:
                if parent.sky.target:
                    parent.sky.select_target()
                if parent.sky.night and parent.sky.site:
                    parent.sky.show_night()
                parent.history.refresh()
                parent.planner.redraw()
        self.language.currentIndexChanged.connect(change)
