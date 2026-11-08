from ..i18n import source as ui_text, tr
import hashlib
from pathlib import Path
import re

def remote_path(value: str) -> str:
    """Accept only relative SMB paths. Never normalize away traversal."""
    if not isinstance(value, str) or '\\' in value or '\x00' in value or (':' in value) or value.startswith('/'):
        raise ValueError(ui_text('m0291'))
    if value == '':
        return ''
    if any((part in {'', '.', '..'} for part in value.split('/'))):
        raise ValueError(ui_text('m0291'))
    return value

def child_path(parent: str, name: str) -> str:
    if '/' in name or '\\' in name or name in {'', '.', '..'}:
        raise ValueError(ui_text('m0292'))
    return remote_path(f'{parent}/{name}' if parent else name)

def windows_name(value: str) -> str:
    cleaned = re.sub('[<>:"/\\\\|?*\\x00-\\x1f]', '_', value).rstrip(' .')
    if not cleaned or cleaned.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(10)), *(f'LPT{i}' for i in range(10))}:
        cleaned = '_' + cleaned
    if cleaned != value or len(cleaned) > 110:
        digest = hashlib.sha256(value.encode()).hexdigest()[:8]
        suffix = Path(cleaned).suffix[:12]
        stem = cleaned[:-len(suffix)] if suffix else cleaned
        cleaned = stem[:90] + '-' + digest + suffix
    return cleaned

def under_root(root: Path, *parts: str) -> Path:
    base = root.expanduser().resolve()
    candidate = base.joinpath(*parts)
    resolved = candidate.resolve()
    if not resolved.is_relative_to(base) or resolved == base:
        raise ValueError(ui_text('m0293'))
    return candidate

def destination(root: Path, device: str, path: str) -> Path:
    path = remote_path(path)
    if not path:
        raise ValueError(ui_text('m0294'))
    return under_root(root, windows_name(device), *(windows_name(p) for p in path.split('/')))
