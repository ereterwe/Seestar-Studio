from ..i18n import source as ui_text, tr
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Protocol

@dataclass(frozen=True)
class RemoteEntry:
    path: str
    name: str
    is_dir: bool
    size: int = 0
    modified: float | None = None

    @property
    def kind(self) -> str:
        if self.is_dir:
            return ui_text('m0290')
        suffix = PurePosixPath(self.name).suffix.lower()
        if suffix in {'.fit', '.fits', '.fts'}:
            return 'FITS-Subframe' if '_sub/' in self.path.lower() or self.name.lower().startswith('light_') else 'FITS'
        return {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.raw': 'RAW-Subframe', '.dng': 'RAW-Subframe'}.get(suffix, suffix.upper().lstrip('.') or ui_text('extra.5'))

class FileClient(Protocol):

    def list(self, path: str) -> list[RemoteEntry]:
        ...

    def stat(self, path: str) -> RemoteEntry:
        ...

    def read(self, path: str, offset: int, length: int) -> bytes:
        ...

    def close(self) -> None:
        ...

class TransferCancelled(Exception):
    pass

class RemoteChangedError(Exception):
    pass
