"""Native setup UI QA with an isolated profile and an ephemeral synthetic key.

No discovery, no real key access, no connection or global activation.
"""
import json
from pathlib import Path
import tempfile
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from seestar_studio.setup_service import SetupService
from seestar_studio.setup_wizard import SetupWizard
from seestar_studio.theme import STYLE


def main():
    app = QApplication([]); app.setStyle('Fusion'); app.setStyleSheet(STYLE)
    root = Path('reports'); root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='studio-setup-qa-') as temp:
        profile = Path(temp)
        service = SetupService(profile / 'authentication', detector=lambda: None)
        wizard = SetupWizard(service.profile, lambda: {}, service=service)
        wizard.resize(900, 620); wizard.show()
        def exercise():
            wizard.grab().save(str(root / 'setup-empty.png'))
            wizard.next(); app.processEvents()
            wizard.grab().save(str(root / 'setup-import.png'))
            source = profile / 'synthetic.pem'
            source.write_bytes(rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            wizard.candidates = service.import_file(source)
            for ref in wizard.candidates: wizard.candidate_combo.addItem('SYNTHETISCHER TESTSCHLÜSSEL', ref)
            wizard.import_page.completeChanged.emit(); wizard.next(); app.processEvents()
            wizard.grab().save(str(root / 'setup-check.png'))
            refs = list(wizard.candidates); wizard.reject()
            report = {'test_type': 'synthetic native UI; no hardware', 'pages': 3,
                'cancel_removed_candidates': all(not r.path.exists() for r in refs),
                'configuration_unchanged': not service.config.exists(), 'disposed': wizard._disposed}
            (root / 'setup-ui.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            wizard.deleteLater(); QTimer.singleShot(100, app.quit)
        QTimer.singleShot(500, exercise)
        return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
