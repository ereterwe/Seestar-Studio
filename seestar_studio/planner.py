"""Local planning only. This module has no command/network adapter."""
from .i18n import source as ui_text, tr
from dataclasses import dataclass, asdict, field, replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from PySide6.QtCore import QSaveFile, QIODevice
from .sky.astronomy import calculate

def instant(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(ui_text('m0120'))
    return result.astimezone(timezone.utc)

@dataclass(frozen=True)
class PlanEntry:
    id: str
    telescope: str
    target: str
    minutes: int
    fixed_start: str = ''

    def __post_init__(self):
        if not self.id or len(self.id) > 80 or (not self.telescope.strip()) or (len(self.telescope) > 120):
            raise ValueError(ui_text('m0127'))
        if not self.target or len(self.target) > 120 or type(self.minutes) is not int or (not 1 <= self.minutes <= 720):
            raise ValueError(ui_text('m0128'))
        if self.fixed_start:
            instant(self.fixed_start)

@dataclass(frozen=True)
class Scheduled:
    entry: PlanEntry
    start: datetime
    end: datetime
    issues: tuple[str, ...]
    astronomy: dict = field(default_factory=dict)

def save_plan(path, entries, start, setup_minutes):
    instant(start)
    validate_entries(entries, setup_minutes)
    data = {'version': 1, 'start': start, 'setup_minutes': setup_minutes, 'entries': [asdict(e) for e in entries]}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    file = QSaveFile(str(path))
    if not file.open(QIODevice.OpenModeFlag.WriteOnly):
        raise OSError(ui_text('m0121'))
    file.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    if not file.commit():
        raise OSError(ui_text('m0122'))

def validate_entries(entries, setup_minutes):
    if len(entries) > 100 or len({e.id for e in entries}) != len(entries):
        raise ValueError(ui_text('m0123'))
    if type(setup_minutes) is not int or not 0 <= setup_minutes <= 120:
        raise ValueError(ui_text('m0124'))

def load_plan(path):
    if Path(path).stat().st_size > 1000000:
        raise ValueError(ui_text('m0125'))
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('version') not in (1, 2) or (not isinstance(data.get('entries'), list)):
        raise ValueError(ui_text('m0126'))
    entries = [PlanEntry(**e) for e in data['entries']]
    validate_entries(entries, data['setup_minutes'])
    instant(data['start'])
    return (entries, data['start'], data['setup_minutes'])

def next_slot(entries, telescope, start, minutes, setup_minutes=5, fill_gaps=False, exclude=None):
    """Find a free UTC slot including transitions on both sides, per device."""
    validate_entries(entries, setup_minutes)
    base = instant(start) if isinstance(start, str) else start
    duration = timedelta(minutes=minutes)
    gap = timedelta(minutes=setup_minutes)
    intervals = []
    cursor = base
    for entry in entries:
        if entry.telescope != telescope or entry.id == exclude:
            continue
        at = instant(entry.fixed_start) if entry.fixed_start else cursor
        end = at + timedelta(minutes=entry.minutes)
        intervals.append((at, end))
        cursor = max(cursor, end + gap)
    if not fill_gaps:
        return max([base] + [b + gap for a, b in intervals])
    candidate = base
    for a, b in sorted(intervals):
        if candidate + duration + gap <= a:
            return candidate
        if candidate < b + gap:
            candidate = b + gap
    return candidate

def materialize(entries, start, setup):
    """V1 implicit sequencing becomes explicit, with exactly the old instants."""
    cursors = {}
    result = []
    for entry in entries:
        cursor = cursors.get(entry.telescope, instant(start))
        at = instant(entry.fixed_start) if entry.fixed_start else cursor
        result.append(replace(entry, fixed_start=at.isoformat()))
        cursors[entry.telescope] = max(cursor, at + timedelta(minutes=entry.minutes + setup))
    return result

def save_document(path, entries, start, setup, zone, name='', rows=()):
    ZoneInfo(zone)
    instant(start)
    validate_entries(entries, setup)
    entries = materialize(entries, start, setup)
    data = {'version': 2, 'timezone': zone, 'name': name, 'start': instant(start).isoformat(), 'planning_date': instant(start).astimezone(ZoneInfo(zone)).date().isoformat(), 'setup_minutes': setup, 'entries': [asdict(e) for e in entries], 'checks': [{'id': r.entry.id, 'start': r.start.isoformat(), 'end': r.end.isoformat(), 'issues': list(r.issues), 'astronomy': r.astronomy} for r in rows]}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    file = QSaveFile(str(path))
    if not file.open(QIODevice.OpenModeFlag.WriteOnly):
        raise OSError(ui_text('m0121'))
    file.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    if not file.commit():
        raise OSError(ui_text('m0122'))

def load_document(path, fallback_zone):
    entries, start, setup = load_plan(path)
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    zone = data.get('timezone', fallback_zone)
    ZoneInfo(zone)
    return (materialize(entries, start, setup), start, setup, zone)

def schedule(entries, start, setup_minutes, catalog, site=None, optimize=False, calculator=calculate):
    validate_entries(entries, setup_minutes)
    base = instant(start)
    windows = {}
    if site:
        local = base.astimezone(ZoneInfo(site.timezone))
        night_date = (local - timedelta(days=1)).date() if local.hour < 12 else local.date()
        for target_id in dict.fromkeys((e.target for e in entries)):
            target = catalog.by_id.get(target_id)
            if target and target.valid:
                windows[target_id] = calculator(target, site, night_date).windows
    result = []
    for telescope in dict.fromkeys((e.telescope for e in entries)):
        tasks = [e for e in entries if e.telescope == telescope]
        if optimize and site:
            if not any((e.fixed_start for e in tasks)):
                tasks.sort(key=lambda e: min((b for a, b in windows.get(e.target, ()) if b >= base), default=datetime.max.replace(tzinfo=timezone.utc)))
        cursor = base
        for entry in tasks:
            issues = []
            duration = timedelta(minutes=entry.minutes)
            start_time = instant(entry.fixed_start) if entry.fixed_start else cursor
            if optimize and site and (not entry.fixed_start):
                possible = [max(cursor, a) for a, b in windows.get(entry.target, ()) if max(cursor, a) + duration <= b]
                if possible:
                    start_time = min(possible)
            end = start_time + duration
            details = {}
            if entry.target not in catalog.by_id or not catalog.by_id[entry.target].valid:
                issues.append(ui_text('m0129'))
            elif site is None:
                issues.append(ui_text('m0130'))
            elif not any((a <= start_time and end <= b for a, b in windows.get(entry.target, ()))):
                issues.append(ui_text('m0131'))
            if site and entry.target in catalog.by_id and catalog.by_id[entry.target].valid:
                if calculator is calculate:
                    local = start_time.astimezone(ZoneInfo(site.timezone))
                    date = (local - timedelta(days=1)).date() if local.hour < 12 else local.date()
                    night = calculator(catalog.by_id[entry.target], site, date, now=start_time)
                    issues=[issue for issue in issues if issue!=ui_text('m0131')]
                    if not any(a<=start_time and end<=b for a,b in night.windows):issues.append(ui_text('m0131'))
                    details = {'altitude': night.current_alt, 'azimuth': night.current_az, 'rise': [t.isoformat() for t in night.rise], 'set': [t.isoformat() for t in night.setting], 'darkness': [[a.isoformat(), b.isoformat()] for a, b in night.dark_windows], 'windows': [[a.isoformat(), b.isoformat()] for a, b in night.windows]}
            result.append(Scheduled(entry, start_time, end, tuple(issues), details))
            cursor = max(cursor, end + timedelta(minutes=setup_minutes))
    conflicting = set()
    for i, a in enumerate(result):
        for b in result[i + 1:]:
            if a.entry.telescope != b.entry.telescope:
                continue
            earlier, later = sorted((a, b), key=lambda r: r.start)
            if earlier.end + timedelta(minutes=setup_minutes) > later.start:
                conflicting.update((a.entry.id, b.entry.id))
    return [replace(r, issues=r.issues + (ui_text('m0132'),)) if r.entry.id in conflicting else r for r in result]
