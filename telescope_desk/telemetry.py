import math
from .models import Telemetry


class TelemetryService:
    """Normalize the reference dashboard snapshot, preserving unknown values."""

    @staticmethod
    def normalize(snapshot: dict, paused=False) -> Telemetry:
        values = dict(snapshot)
        for key, value in values.items():
            if isinstance(value, float) and not math.isfinite(value):
                values[key] = None
        # This quantity in SeestarPy is derived from count × current exposure.
        values["integration_estimated"] = values.get("stack_time_s") is not None
        return Telemetry(
            serial=str(values.get("sn", "")),
            connected=bool(values.get("connected")) and not paused,
            paused=paused, values=values,
            error=values.get("error"), image_error=values.get("image_error"),
        )


def number(value, suffix="", digits=0):
    if value is None:
        return "—"
    try:
        from .i18n import locale
        return locale().toString(float(value), 'f', digits) + suffix
    except (ValueError, TypeError):
        return "—"


def duration(seconds):
    if seconds is None:
        return "—"
    seconds = max(0, int(seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
