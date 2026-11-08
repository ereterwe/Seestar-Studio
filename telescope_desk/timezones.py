"""Windows timezone and explicit local-time resolution, independent of site."""
from .i18n import source as ui_text, tr
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from tzlocal import get_localzone_name

def system_timezone():
    try:
        name = get_localzone_name()
        ZoneInfo(name)
        return name
    except Exception:
        return 'UTC'

def local_candidates(value, zone):
    naive = value.replace(tzinfo=None)
    tz = ZoneInfo(zone)
    found = {}
    for fold in (0, 1):
        candidate = naive.replace(tzinfo=tz, fold=fold).astimezone(timezone.utc)
        if candidate.astimezone(tz).replace(tzinfo=None) == naive:
            found[candidate] = candidate
    return sorted(found)

def resolve_local(value, zone, occurrence=None):
    candidates = local_candidates(value, zone)
    if not candidates:
        raise ValueError(ui_text('m0245'))
    if len(candidates) > 1 and occurrence not in (0, 1):
        raise ValueError(ui_text('m0246'))
    return candidates[0] if len(candidates)==1 else candidates[occurrence]

def local_text(value, zone, seconds=False):
    from PySide6.QtCore import QDate, QTime, QLocale
    from .i18n import locale, LANGUAGE
    local = value.astimezone(ZoneInfo(zone))
    date = locale().toString(QDate(local.year,local.month,local.day), 'dd.MM.yyyy' if LANGUAGE=='de' else 'MMM d, yyyy')
    fmt = 'HH:mm' if LANGUAGE=='de' else QLocale.system().timeFormat(QLocale.FormatType.ShortFormat)
    if seconds:fmt='HH:mm:ss'
    return date+' '+locale().toString(QTime(local.hour,local.minute,local.second),fmt)+' '+local.strftime('%z')
