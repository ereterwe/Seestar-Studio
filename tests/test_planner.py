from datetime import timedelta
from types import SimpleNamespace
import pytest
from telescope_desk.planner import PlanEntry, instant, schedule, save_plan, load_plan
from telescope_desk.sky.astronomy import Site
from telescope_desk.sky.catalog import Catalog


@pytest.fixture(scope='module')
def catalog(): return Catalog()


def test_multidevice_order_gaps_and_conflicts(catalog):
    entries = [PlanEntry('a', 'A', 'NGC0224', 60), PlanEntry('b', 'B', 'NGC0224', 60),
               PlanEntry('c', 'A', 'NGC0700', 30, '2026-11-06T20:30:00Z')]
    rows = schedule(entries, '2026-11-06T20:00:00Z', 5, catalog)
    assert rows[0].start == rows[2].start
    assert any('Zeitkonflikt' in issue for issue in rows[1].issues)
    assert all(any('Standort' in issue for issue in r.issues) for r in rows)


def test_optimized_windows_and_fixed_time_preservation(catalog):
    start = instant('2026-11-06T18:00:00Z')
    def calc(target, site, date):
        return SimpleNamespace(windows=((start, start + timedelta(hours=2 if target.id == 'NGC0224' else 6)),))
    entries = [PlanEntry('a', 'A', 'NGC7000', 60), PlanEntry('b', 'A', 'NGC0224', 60)]
    rows = schedule(entries, start.isoformat(), 5, catalog, Site(52, 13, 40, 'Europe/Berlin'), True, calc)
    assert [r.entry.id for r in rows] == ['b', 'a']
    assert not any(r.issues for r in rows)
    assert rows[1].start == rows[0].end + timedelta(minutes=5)
    fixed = PlanEntry('c', 'A', 'NGC0224', 60, '2026-11-06T19:30:00Z')
    rows = schedule([fixed], start.isoformat(), 0, catalog, Site(52, 13, 40, 'Europe/Berlin'), True, calc)
    assert rows[0].start == instant(fixed.fixed_start)
    assert rows[0].issues  # finishes outside window


def test_save_load_roundtrip_and_invalid_file(app, tmp_path):
    entries = [PlanEntry('a', 'A', 'NGC0224', 60)]
    path = tmp_path / 'plan.json'
    save_plan(path, entries, '2026-11-06T20:00:00+01:00', 5)
    loaded, start, setup = load_plan(path)
    assert loaded == entries and setup == 5 and instant(start).hour == 19
    path.write_text('{"version": 99, "entries": []}', encoding='utf-8')
    with pytest.raises(ValueError): load_plan(path)


def test_offsets_are_explicit_and_dst_repeated_hour_distinct():
    with pytest.raises(ValueError): instant('2026-10-25T02:30:00')
    early = instant('2026-10-25T02:30:00+02:00')
    late = instant('2026-10-25T02:30:00+01:00')
    assert (late - early).total_seconds() == 3600
    with pytest.raises(ValueError): PlanEntry('a', '', 'M31', 60)
    with pytest.raises(ValueError): PlanEntry('a', 'A', 'M31', 0)
