from dataclasses import replace
from datetime import datetime, timedelta
from types import SimpleNamespace
import json
import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from seestar_studio.planner import PlanEntry, next_slot, schedule, instant, save_plan, save_document, load_document
from seestar_studio.timezones import resolve_local, local_candidates, local_text


def test_native_entry_editor_preserves_wall_time_and_rejects_dst_gap(app):
    from PySide6.QtCore import QDateTime, QDate, QTime, QTimeZone
    from seestar_studio.planner_widget import EntryDialog
    target = SimpleNamespace(id='M31', title='M31')
    dialog = EntryDialog(target, {'A':'A'}, zone='Europe/Berlin',
                         suggestion=instant('2026-11-06T19:00:00Z'))
    try:
        assert dialog.local.time().hour() == 20
        assert dialog.timestamp() == instant('2026-11-06T19:00:00Z')
        dialog.local.setDateTime(QDateTime(QDate(2026,3,29), QTime(2,30), QTimeZone.utc()))
        assert dialog.local.time().hour() == 2
        with pytest.raises(ValueError): dialog.timestamp()
        dialog.local.setDateTime(QDateTime(QDate(2026,10,25), QTime(2,30), QTimeZone.utc()))
        with pytest.raises(ValueError): dialog.timestamp()
        dialog.occurrence.setCurrentIndex(1); first = dialog.timestamp()
        dialog.occurrence.setCurrentIndex(2)
        assert dialog.timestamp() - first == timedelta(hours=1)
    finally:
        dialog.close(); dialog.deleteLater()


def test_required_2205_and_device_independence():
    entries=[PlanEntry('a','S50','M31',120,'2026-11-06T20:00:00+01:00')]
    at=next_slot(entries,'S50','2026-11-06T20:00:00+01:00',60,5)
    assert local_text(at,'Europe/Berlin').startswith('06.11.2026 22:05')
    assert next_slot(entries,'PRO','2026-11-06T20:00:00+01:00',60,5).hour==19


def test_all_occupied_slots_gap_transitions_and_unsorted_conflicts():
    entries=[PlanEntry('late','A','M31',60,'2026-11-06T23:00:00Z'),PlanEntry('early','A','M31',60,'2026-11-06T20:00:00Z')]
    assert next_slot(entries,'A','2026-11-06T20:00:00Z',60,5,True)==instant('2026-11-06T21:05:00Z')
    assert next_slot(entries,'A','2026-11-06T20:00:00Z',60,5).day==7
    rows=schedule(entries,'2026-11-06T20:00:00Z',5,SimpleNamespace(by_id={}))
    assert not any('Zeitkonflikt' in issue for r in rows for issue in r.issues)
    changed=[entries[0],replace(entries[1],fixed_start='2026-11-06T22:30:00Z')]
    rows=schedule(changed,'2026-11-06T20:00:00Z',5,SimpleNamespace(by_id={}))
    assert all(any('Zeitkonflikt' in issue for issue in r.issues) for r in rows)


def test_nonexistent_and_ambiguous_local_times():
    with pytest.raises(ValueError):resolve_local(datetime(2026,3,29,2,30),'Europe/Berlin')
    with pytest.raises(ValueError):resolve_local(datetime(2026,10,25,2,30),'Europe/Berlin')
    early=resolve_local(datetime(2026,10,25,2,30),'Europe/Berlin',0)
    late=resolve_local(datetime(2026,10,25,2,30),'Europe/Berlin',1)
    assert late-early==timedelta(hours=1)
    assert len(local_candidates(datetime(2026,11,6,20),'America/New_York'))==1
    assert resolve_local(datetime(2026,11,6,20),'Europe/Berlin',1)==resolve_local(datetime(2026,11,6,20),'Europe/Berlin',0)


def test_migration_preserves_midnight_and_utc_on_roundtrip(app,tmp_path):
    entries=[PlanEntry('a','A','M31',120),PlanEntry('b','A','M33',60)]
    path=tmp_path/'v1.json';save_plan(path,entries,'2026-11-06T23:00:00+01:00',5)
    migrated,start,setup,zone=load_document(path,'Europe/Berlin')
    assert instant(migrated[1].fixed_start)==instant('2026-11-07T01:05:00+01:00')
    new=tmp_path/'v2.json';save_document(new,migrated,start,setup,'America/New_York')
    again,_,_,zone=load_document(new,'UTC')
    assert again==migrated and zone=='America/New_York'
    assert json.loads(new.read_text())['version']==2


def test_planner_autosave_offline_devices_and_drag(app,tmp_path):
    from seestar_studio.settings import SettingsService
    from seestar_studio.planner_widget import PlannerWidget
    settings=SettingsService(tmp_path/'settings.json');settings.values['known_devices']={'A':'S50','B':'S50 Pro'}
    sky=SimpleNamespace(catalog=SimpleNamespace(by_id={}),site=None,target=None)
    widget=PlannerWidget(sky,settings);widget.resize(1600,800);widget.show()
    widget.start.setText('2026-11-06T20:00:00Z')
    widget.entries=[PlanEntry('a','A','M31',120,'2026-11-06T20:00:00Z'),PlanEntry('b','A','M33',60,'2026-11-06T22:05:00Z')]
    widget.invalidate();app.processEvents()
    timeline=widget.timeline;rect=timeline.rectangle(widget.rows[1]);origin=rect.center().toPoint()
    QTest.mousePress(timeline,Qt.MouseButton.LeftButton,pos=origin)
    destination=origin-QPoint(int(timeline.pixels_hour),0)
    QTest.mouseMove(timeline,destination);QTest.mouseRelease(timeline,Qt.MouseButton.LeftButton,pos=destination)
    assert any('Zeitkonflikt' in issue for r in widget.rows for issue in r.issues)
    assert widget.device.count()==2
    key=widget.plan_id;widget.stop();widget.close()
    restored=PlannerWidget(sky,SettingsService(tmp_path/'settings.json'))
    assert restored.plan_id==key and restored.entries==widget.entries
    assert restored.devices.keys()==widget.devices.keys()
    restored.stop();restored.close()


def test_timeline_dst_span_resize_snap_and_no_move_on_click(app):
    from seestar_studio.timeline import Timeline
    timeline=Timeline()
    for day,hours in [('2026-03-28T20:00:00+01:00',23),('2026-10-24T20:00:00+02:00',25)]:
        timeline.set_rows([],{'A':'Offline S50'},'Europe/Berlin',instant(day),5)
        assert (timeline.end-timeline.base).total_seconds()==hours*3600
    entry=PlanEntry('a','A','M31',61,'2026-11-06T20:03:00Z')
    row=schedule([entry],entry.fixed_start,5,SimpleNamespace(by_id={}))[0]
    timeline.drag=(row,0,False)
    assert timeline.proposed(0)[0]==row.start
    assert timeline.proposed(timeline.pixels_hour/6)[0].minute%5==0
    timeline.drag=(row,0,True)
    assert timeline.proposed(timeline.pixels_hour/6)[1]%5==0
    timeline.deleteLater()


def test_optimization_requires_review_and_preserves_existing_on_cancel(app,tmp_path,monkeypatch):
    import time
    from seestar_studio.planner_widget import PlannerWidget
    from seestar_studio.settings import SettingsService
    sky=SimpleNamespace(catalog=SimpleNamespace(by_id={}),site=None,target=None)
    widget=PlannerWidget(sky,SettingsService(tmp_path/'settings.json'))
    widget.start.setText('2026-11-06T20:00:00Z')
    original=[PlanEntry('a','A','M31',120,'2026-11-06T20:00:00Z'),PlanEntry('b','A','M33',60,'2026-11-06T23:00:00Z')]
    widget.entries=list(original);widget.invalidate();widget.auto_timer.stop()
    before=list(widget.entries)
    monkeypatch.setattr(widget,'review_optimization',lambda rows:False)
    widget.calculate(True)
    deadline=time.monotonic()+3
    while widget._future and time.monotonic()<deadline:app.processEvents();widget.poll();time.sleep(.01)
    assert widget.entries==before
    monkeypatch.setattr(widget,'review_optimization',lambda rows:True)
    widget.calculate(True)
    deadline=time.monotonic()+3
    while widget._future and time.monotonic()<deadline:app.processEvents();widget.poll();time.sleep(.01)
    assert instant(widget.entries[1].fixed_start)==instant('2026-11-06T22:05:00Z')
    widget.stop();widget.close()
