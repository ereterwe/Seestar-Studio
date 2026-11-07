"""Bounded asynchronous, local SQLite observation history (no images or sites)."""
from .i18n import source as ui_text, tr
from dataclasses import dataclass
import math
from pathlib import Path
import queue
import sqlite3
import threading
import time
import uuid

def finite(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None

@dataclass(frozen=True)
class Sample:
    serial: str
    model: str
    timestamp: float
    connected: bool
    target: str | None
    stage: str | None
    exposure: float | None
    accepted: float | None
    dropped: float | None
    integration: float | None
    battery: float | None
    temperature: float | None

def sample_from(info, tel, timestamp):
    fresh = tel.connected and (not tel.paused) and (tel.get('age_s') is not None) and (tel.get('age_s') <= 20)
    value = lambda key: finite(tel.get(key)) if fresh else None
    return Sample(info.serial, info.model, timestamp, fresh, str(tel.get('target'))[:200] if fresh and tel.get('target') else None, str(tel.get('view_stage'))[:80] if fresh and tel.get('view_stage') else None, value('exp_s'), value('stacked_frames'), value('dropped_frames'), value('stack_time_s'), value('battery'), value('temp_c'))

class HistoryStore:
    """Owned by the writer thread; deterministic ingestion for tests."""

    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=3)
        if self.db.execute('PRAGMA user_version').fetchone()[0] not in (0, 1):
            self.db.close()
            raise ValueError('Unsupported history schema')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('\n            CREATE TABLE IF NOT EXISTS sessions (\n                id TEXT PRIMARY KEY, serial TEXT NOT NULL, model TEXT, target TEXT,\n                observed_start REAL NOT NULL, observed_end REAL, end_reason TEXT,\n                disconnects INTEGER NOT NULL DEFAULT 0);\n            CREATE TABLE IF NOT EXISTS samples (\n                id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),\n                ts REAL NOT NULL, connected INTEGER NOT NULL, stage TEXT, exposure REAL,\n                accepted REAL, dropped REAL, integration_est REAL, battery REAL, temperature REAL);\n            CREATE INDEX IF NOT EXISTS samples_session_time ON samples(session_id, ts);\n            CREATE INDEX IF NOT EXISTS sessions_time ON sessions(observed_start DESC);\n            PRAGMA user_version=1;\n        ')
        self.db.execute("UPDATE sessions SET observed_end=COALESCE((SELECT MAX(ts) FROM samples WHERE session_id=sessions.id),observed_start), end_reason='monitor_interrupted' WHERE observed_end IS NULL")
        self.db.commit()
        self.active = {}

    def _end(self, serial, reason):
        state = self.active.pop(serial)
        self.db.execute('UPDATE sessions SET observed_end=?, end_reason=? WHERE id=?', (state['last'].timestamp, reason, state['id']))

    def ingest(self, sample):
        state = self.active.get(sample.serial)
        if state and sample.timestamp <= state['last'].timestamp:
            return
        if state and (not sample.connected) and (sample.timestamp - state['last_connected'].timestamp > 300):
            self._end(sample.serial, 'observation_gap')
            state = None
        if state and sample.connected:
            old = state['last_connected']
            reason = None
            if sample.timestamp - old.timestamp > 300:
                reason = 'observation_gap'
            elif sample.stage is not None and sample.stage != 'Stack':
                reason = 'stack_ended'
            elif sample.target is not None and sample.target != state['target']:
                reason = 'target_changed'
            elif sample.accepted is not None and old.accepted is not None and (sample.accepted < old.accepted):
                reason = 'counter_reset'
            if reason:
                self._end(sample.serial, reason)
                state = None
        if state is None:
            if not sample.connected or sample.stage != 'Stack':
                self.db.commit()
                return
            ident = uuid.uuid4().hex
            self.db.execute('INSERT INTO sessions(id,serial,model,target,observed_start) VALUES (?,?,?,?,?)', (ident, sample.serial, sample.model, sample.target, sample.timestamp))
            state = {'id': ident, 'target': sample.target, 'last': sample, 'last_connected': sample}
            self.active[sample.serial] = state
        if not sample.connected and state['last'].connected:
            self.db.execute('UPDATE sessions SET disconnects=disconnects+1 WHERE id=?', (state['id'],))
        self.db.execute('INSERT INTO samples(session_id,ts,connected,stage,exposure,accepted,dropped,integration_est,battery,temperature) VALUES (?,?,?,?,?,?,?,?,?,?)', (state['id'], sample.timestamp, int(sample.connected), sample.stage, sample.exposure, sample.accepted, sample.dropped, sample.integration, sample.battery, sample.temperature))
        state['last'] = sample
        if sample.connected:
            state['last_connected'] = sample
        self.db.commit()

    def close(self):
        for serial in list(self.active):
            self._end(serial, 'monitor_closed')
        self.db.commit()
        self.db.close()

class HistoryService:

    def __init__(self, path):
        self.path = Path(path)
        self.error = None
        self.skipped_batches = 0
        self._queue = queue.Queue(maxsize=128)
        self._stop = threading.Event()
        self._last = {}
        self._thread = threading.Thread(target=self._run, name='studio-history', daemon=True)
        self._thread.start()

    def submit(self, data, now=None):
        if self._stop.is_set() or self.error:
            return
        now = time.time() if now is None else now
        batch = []
        for serial, (info, tel, _) in data.items():
            sample = sample_from(info, tel, now)
            previous = self._last.get(serial)
            changed = previous is None or (sample.connected, sample.target, sample.stage) != (previous.connected, previous.target, previous.stage)
            if changed or now - previous.timestamp >= 15:
                batch.append(sample)
        if batch:
            try:
                self._queue.put_nowait(batch)
                self._last.update({sample.serial: sample for sample in batch})
            except queue.Full:
                self.skipped_batches += 1

    def _run(self):
        store = None
        try:
            store = HistoryStore(self.path)
            while not self._stop.is_set() or not self._queue.empty():
                try:
                    batch = self._queue.get(timeout=0.2)
                except queue.Empty:
                    continue
                try:
                    for sample in batch:
                        store.ingest(sample)
                finally:
                    self._queue.task_done()
        except Exception as exc:
            self.error = ui_text('m0086').format(p0=f'{type(exc).__name__}')
        finally:
            if store:
                try:
                    store.close()
                except Exception:
                    self.error = ui_text('m0087')

    @property
    def running(self):
        return self._thread.is_alive()

    def stop(self):
        self._stop.set()

    def join(self, timeout=5):
        self._thread.join(timeout)

def read_history(path, selected=()):
    """Read-only connection; returns bounded UI data and aggregated metrics."""
    if not Path(path).exists():
        return ([], {})
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True, timeout=2)
    db.row_factory = sqlite3.Row
    try:
        sessions = [dict(row) for row in db.execute('SELECT * FROM sessions ORDER BY observed_start DESC LIMIT 200')]
        details = {}
        for ident in list(selected)[:4]:
            samples = [dict(row) for row in db.execute('SELECT * FROM samples WHERE session_id=? ORDER BY ts', (ident,))]
            details[ident] = summarize(samples)
        return (sessions, details)
    finally:
        db.close()

def summarize(samples):
    good = [s for s in samples if s['connected']]
    latest = good[-1] if good else {}
    estimated, unknown_intervals, observed_frames = (0.0, 0, 0)
    for previous, current in zip(samples, samples[1:]):
        a, b = (previous['accepted'], current['accepted'])
        if not previous['connected'] or not current['connected'] or a is None or (b is None) or (b < a):
            unknown_intervals += 1
            continue
        delta = b - a
        observed_frames += delta
        if current['ts'] - previous['ts'] > 30 or current['exposure'] is None or current['exposure'] != previous['exposure']:
            unknown_intervals += 1
            continue
        estimated += delta * current['exposure']
    accepted, dropped = (latest.get('accepted'), latest.get('dropped'))
    denominator = accepted + dropped if accepted is not None and dropped is not None else 0
    step = max(1, math.ceil(len(samples) / 1000))
    indices = list(range(0, len(samples), step))
    if samples and indices[-1] != len(samples) - 1:
        indices.append(len(samples) - 1)
    points = [samples[i] for i in indices]
    for i in range(1, len(points)):
        segment = samples[indices[i - 1]:indices[i] + 1]
        if any((not s['connected'] for s in segment)) or any((b['ts'] - a['ts'] > 30 for a, b in zip(segment, segment[1:]))):
            points[i] = {**points[i], 'battery': None, 'temperature': None}
    return {'sample_count': len(samples), 'latest': latest, 'estimated_observed_seconds': estimated, 'observed_frame_delta': observed_frames, 'unknown_intervals': unknown_intervals, 'rejection_percent': 100 * dropped / denominator if denominator else None, 'points': points}
