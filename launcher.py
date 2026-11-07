"""PyInstaller entry point, with opt-in local startup diagnostics."""
import sys
import json
import traceback
from pathlib import Path

diagnostics = '--startup-diagnostics' in sys.argv
if diagnostics:
    sys.argv.remove('--startup-diagnostics')
try:
    from seestar_studio.app import main
except Exception as exc:
    if diagnostics:
        # Stack locations only: no source lines, values, key material or RPCs.
        Path('reports').mkdir(exist_ok=True)
        Path('reports/startup-error.json').write_text(json.dumps({
            'type': type(exc).__name__,
            'import_name': getattr(exc, 'name', None),
            'stack': [{'file': f.filename, 'line': f.lineno, 'function': f.name}
                      for f in traceback.extract_tb(exc.__traceback__)]}, indent=2), encoding='utf-8')
        raise SystemExit(1)
    raise

if __name__ == "__main__":
    raise SystemExit(main())
