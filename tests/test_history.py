from dataclasses import replace
import sqlite3
import time
from telescope_desk.history import Sample, HistoryStore, HistoryService, read_history, sample_from, summarize
from telescope_desk.models import DeviceInfo, Telemetry


def sample(ts=1000, serial='SIM-A', target='M31', accepted=100, **kwargs):
    return replace(Sample(serial, 'SIMULATED', ts, True, target, 'Stack', 10, accepted, 10, accepted * 10 if accepted is not None else None, 80, 20), **kwargs)


def test_multi_device_reset_target_and_persistence(tmp_path):
    path = tmp_path / 'history.sqlite3'; store = HistoryStore(path)
    store.ingest(sample()); store.ingest(sample(serial='SIM-B'))
    store.ingest(sample(1015, accepted=102)); store.ingest(sample(1030, accepted=1))
    store.ingest(sample(1045, target='M42', accepted=1)); store.close()
    sessions, _ = read_history(path)
    assert len(sessions) == 4
    assert {s['end_reason'] for s in sessions} >= {'counter_reset', 'target_changed', 'monitor_closed'}
    store = HistoryStore(path); store.ingest(sample(1100)); store.close()
    assert len(read_history(path)[0]) == 5  # application restart never invents continuity


def test_disconnections_unknown_values_and_exposure_changes(tmp_path):
    path = tmp_path / 'history.sqlite3'; store = HistoryStore(path)
    store.ingest(sample(1000, accepted=10)); store.ingest(sample(1015, accepted=12))
    store.ingest(sample(1030, accepted=14, exposure=20))
    store.ingest(sample(1045, connected=False, exposure=None, accepted=None, dropped=None, integration=None, battery=None, temperature=None))
    store.ingest(sample(1060, accepted=17, exposure=20))
    store.close()
    sessions, _ = read_history(path)
    assert sessions[0]['disconnects'] == 1
    _, details = read_history(path, [sessions[0]['id']]); d = details[sessions[0]['id']]
    assert d['estimated_observed_seconds'] == 20
    assert d['unknown_intervals'] == 3
    assert d['latest']['accepted'] == 17
    assert d['points'][3]['battery'] is None


def test_recovery_unclosed_session_and_out_of_order(tmp_path):
    path = tmp_path / 'history.sqlite3'; store = HistoryStore(path)
    store.ingest(sample(1000)); store.ingest(sample(990))
    store.db.close()  # simulate abrupt process loss
    restarted = HistoryStore(path)
    sessions, _ = read_history(path)
    assert sessions[0]['end_reason'] == 'monitor_interrupted'
    assert sessions[0]['observed_end'] == 1000
    restarted.close()


def test_stale_telemetry_never_records_cached_measurements():
    info = DeviceInfo('SIM', '127.0.0.1')
    tel = Telemetry('SIM', True, values={'age_s': 100, 'stacked_frames': 999, 'battery': 70})
    result = sample_from(info, tel, 1000)
    assert not result.connected and result.accepted is None and result.battery is None


def test_async_drain_and_failure_isolation(tmp_path):
    path = tmp_path / 'history.sqlite3'
    service = HistoryService(path)
    info = DeviceInfo('SIM', '127.0.0.1')
    tel = Telemetry('SIM', True, values={'age_s': 1, 'target': 'M31', 'view_stage': 'Stack', 'stacked_frames': 10})
    service.submit({'SIM': (info, tel, None)}, now=1000)
    service.submit({'SIM': (info, tel, None)}, now=1001)  # throttled
    service.stop(); service.join()
    assert not service.running and service.error is None
    sessions, _ = read_history(path)
    _, details = read_history(path, [sessions[0]['id']])
    assert details[sessions[0]['id']]['sample_count'] == 1
    bad = tmp_path / 'not-a-directory'; bad.write_text('x')
    broken = HistoryService(bad / 'history.sqlite3'); broken.join()
    assert broken.error and not broken.running


def test_twelve_hour_plot_is_bounded_without_false_gaps():
    samples = [{'ts': i * 15, 'connected': True, 'accepted': i, 'dropped': 0,
                'exposure': 10, 'integration_est': i * 10, 'battery': 80, 'temperature': 25} for i in range(2881)]
    result = summarize(samples)
    assert len(result['points']) <= 1001
    assert all(p['temperature'] == 25 for p in result['points'])
    assert result['unknown_intervals'] == 0
    samples[500]['connected'] = False
    result = summarize(samples)
    assert any(p['temperature'] is None for p in result['points'])
    assert result['unknown_intervals'] == 2


def test_extended_offline_period_closes_session(tmp_path):
    path = tmp_path / 'history.sqlite3'; store = HistoryStore(path)
    store.ingest(sample(1000)); store.ingest(sample(1015, connected=False))
    store.ingest(sample(1400, connected=False))
    assert not store.active
    store.close()
    sessions, _ = read_history(path)
    assert sessions[0]['end_reason'] == 'observation_gap'
