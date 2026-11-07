"""Explicit read-only onboarding check; no import, activation or control action."""
import json
from datetime import datetime, timezone
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from seestar_studio.settings import SettingsService
from seestar_studio.setup_service import SetupService, SetupError


def main():
    app = QCoreApplication([])
    app.setApplicationName('Seestar Studio'); app.setOrganizationName('SeestarStudio')
    service = SetupService(SettingsService().path.parent / 'authentication')
    reference = service.configure_runtime()
    from seestar_studio.backend import discover
    results = []
    for info in discover():
        try:
            service.connection_check(info, reference)
            results.append({'model': info.model, 'read_only_identity_check': 'passed'})
        except SetupError:
            results.append({'model': info.model, 'read_only_identity_check': 'failed'})
    report = {'test_type': 'real hardware; read-only authentication/identity',
        'imported_or_activated': False, 'devices': results}
    report['checked_utc'] = datetime.now(timezone.utc).isoformat()
    output = Path('reports') / ('setup-hardware-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
    return 0 if results and all(v['read_only_identity_check'] == 'passed' for v in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
