from dataclasses import dataclass, field
from typing import Any
import time


@dataclass(frozen=True)
class DeviceInfo:
    serial: str
    ip: str
    model: str = "Seestar"
    device_id: str = ""


@dataclass(frozen=True)
class ImageFrame:
    image: Any  # owned QImage, produced off the GUI thread
    sequence: int
    received_at: float
    kind: str
    source_format: str
    frame_id: Any = None


@dataclass(frozen=True)
class Telemetry:
    serial: str
    connected: bool
    paused: bool = False
    values: dict = field(default_factory=dict)
    error: str | None = None
    image_error: str | None = None
    observed_at: float = field(default_factory=time.time)

    def get(self, key, default=None):
        return self.values.get(key, default)
