"""Native UI screenshots with synthetic telemetry; never opens a socket."""
import json
from pathlib import Path
from dataclasses import replace
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from telescope_desk.control_widget import ControlWidget
from telescope_desk.control import ControlService
from telescope_desk.i18n import TranslationController
from telescope_desk.sky.catalog import Catalog
from telescope_desk.theme import STYLE
from tests.test_control import fleet


def main():
    app = QApplication([]); app.setStyle('Fusion'); app.setStyleSheet(STYLE)
    translation = TranslationController(app, 'de')
    def no_transport(ip): raise AssertionError('UI probe cannot access hardware')
    w = ControlWidget(ControlService(no_transport)); w.resize(1200, 1000)
    w.setWindowTitle('SIMULATION — control UI verification')
    data = fleet(); w.sync_devices(data); w.mode.setChecked(True)
    w.devices.setCurrentIndex(w.devices.findData('1')); w.set_target(Catalog().search('M81')[0])
    root = Path('reports/control-ui'); root.mkdir(exist_ok=True)
    results = {}
    def capture():
        for language in ('de', 'en'):
            translation.set_language(language); w.refresh(); app.processEvents()
            w.grab().save(str(root/f'{language}.png'))
            results[language] = {a: {'enabled': b.isEnabled(), 'text': b.text(), 'reason': b.toolTip()} for a,b in w.buttons.items()}
        (root/'result.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
        w.stop(); w.close(); app.quit()
    w.show(); QTimer.singleShot(500,capture); app.exec()


if __name__ == '__main__': main()
