"""Offline tests. Coordinates below are synthetic, never a saved user location."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import threading
import time
import pytest
from PySide6.QtWidgets import QScrollArea
from telescope_desk.solar import calculate_solar, sun_altitudes, solar_colors, SolarService
from telescope_desk.sky.astronomy import Site
from telescope_desk.planner import PlanEntry, schedule, instant
from telescope_desk.timeline import Timeline

UTC = timezone.utc


@pytest.mark.parametrize('lat,lon,expected', [
    (52,13, {'sunrise':'05:11','sunset':'17:21','civil_dawn':'04:37','civil_dusk':'17:55'}),
    (-33,151, {'sunrise':'20:00','sunset':'08:08','civil_dawn':'19:35','civil_dusk':'08:32'}),
    (0,0, {'sunrise':'06:04','sunset':'18:11','civil_dawn':'05:44','civil_dusk':'18:31'}),
])
def test_solar_events_against_usno_reference(lat, lon, expected, monkeypatch):
    # USNO API v4, retrieved 2026-11-07; minute-rounded UTC on 2026-03-20.
    # https://aa.usno.navy.mil/api/rstt/oneday?date=2026-03-20&coords=52,13&tz=0
    # Same endpoint queried separately with coords=-33,151 and coords=0,0.
    # Fixed public test data; no service request during tests/application use.
    import socket
    monkeypatch.setattr(socket.socket, 'connect', lambda *a: pytest.fail('Solar calculation tried network access'))
    start = datetime(2026,3,20,tzinfo=UTC)
    site = Site(lat,lon,0,'UTC')
    profile = calculate_solar(site,start,start+timedelta(days=1))
    for kind, stamp in expected.items():
        event = next(e for e in profile.events if e.kind == kind)
        reference = datetime.fromisoformat('2026-03-20T'+stamp+':00+00:00')
        assert abs((event.time-reference).total_seconds()) < 90
    assert len(profile.events)==8
    # All four independent thresholds, both directions, at each root.
    for event in profile.events:
        before,at,after = sun_altitudes(site,[event.time-timedelta(seconds=30),event.time,event.time+timedelta(seconds=30)])
        assert abs(at-event.altitude)<.003
        assert (before-event.altitude)*(after-event.altitude)<0
    assert profile.dark_seconds > 0


@pytest.mark.parametrize('lat,month,condition,dark', [
    (80,6,'solar.polar_day',False), (70,12,'solar.polar_night',True),
    (52,6,'solar.no_dark',False), (-80,12,'solar.polar_day',False),
])
def test_polar_and_incomplete_nights(lat,month,condition,dark):
    start=datetime(2026,month,21,tzinfo=UTC)
    p=calculate_solar(Site(lat,0,0,'UTC'),start,start+timedelta(days=1))
    assert condition in p.conditions
    assert (p.dark_seconds>0)==dark
    if condition=='solar.polar_day': assert min(p.altitudes)>0 and not p.events
    if condition=='solar.polar_night':
        assert max(p.altitudes)<-.8333 and max(p.altitudes)>-18
        assert 0 < p.dark_seconds < 86400  # polar night != all-day astronomical dark
        assert not any(e.kind in ('sunrise','sunset') for e in p.events)
    if not dark:
        assert min(p.altitudes)>-18
        assert solar_colors([min(p.altitudes)]) != solar_colors([-18])


@pytest.mark.parametrize('stamp,hours', [('2026-03-28T20:00:00+01:00',23),('2026-10-24T20:00:00+02:00',25)])
def test_dst_absolute_times_and_multiday_background(app,stamp,hours):
    timeline=Timeline()
    timeline.set_rows([],{'a':'a'},'Europe/Berlin',instant(stamp),5)
    assert (timeline.end-timeline.base).total_seconds()==hours*3600
    profile=calculate_solar(Site(52,13,0,'Europe/Berlin'),timeline.base,timeline.end)
    assert profile.times[-1]==timeline.end and profile.times[0]==timeline.base
    assert all(a<b for a,b in zip(profile.times,profile.times[1:]))
    timeline.set_solar(profile)
    event=next(e for e in profile.events if e.kind=='night_start')
    offset=timeline.x(event.time)-180
    timeline.zoom(2)
    assert timeline.x(event.time)-180==pytest.approx(offset*2)
    assert timeline.solar is profile
    timeline.deleteLater()


def test_multiday_uses_new_solar_positions_and_site(app):
    start=instant('2026-03-20T12:00:00Z')
    entries=[PlanEntry('a','a','M31',60,start.isoformat()),
             PlanEntry('b','a','M31',120,(start+timedelta(days=3,hours=9)).isoformat())]
    rows=schedule(entries,start.isoformat(),5,SimpleNamespace(by_id={}))
    t=Timeline();t.set_rows(rows,{'a':'a'},'UTC',start,5)
    assert t.end>=rows[-1].end and (t.end-t.base).days==4
    p=calculate_solar(Site(52,13,0,'UTC'),t.base,t.end)
    sunsets=[e.time for e in p.events if e.kind=='sunset']
    assert len(sunsets)==4
    assert abs((sunsets[1]-sunsets[0]).total_seconds()-86400)>20
    other=calculate_solar(Site(-33,151,0,'UTC'),t.base,t.end)
    assert other.colors!=p.colors and other.events!=p.events
    t.deleteLater()


def test_render_alignment_scroll_zoom_and_opaque_bars(app):
    start=instant('2026-03-20T12:00:00Z')
    rows=schedule([PlanEntry('a','A','M31',120,'2026-03-20T15:00:00Z'),
                   PlanEntry('b','B','M31',120,'2026-03-20T15:00:00Z')],start.isoformat(),5,SimpleNamespace(by_id={}))
    t=Timeline();scroll=QScrollArea();scroll.setWidget(t);scroll.resize(900,450);scroll.show()
    t.set_rows(rows,{'A':'A','B':'B'},'UTC',start,5);t.resize(t.minimumSize())
    p=calculate_solar(Site(52,13,0,'UTC'),t.base,t.end)
    app.processEvents();neutral=t.grab().toImage()
    t.set_solar(p);app.processEvents();colored=t.grab().toImage()
    rect=t.rectangle(rows[0]);x,y=int(rect.left()+3),int(rect.bottom()-5)
    assert colored.pixelColor(x,y)==neutral.pixelColor(x,y)  # block remains opaque
    assert colored.pixelColor(200,120)==colored.pixelColor(200,220)  # same sun for all devices
    assert colored.pixelColor(200,120)!=neutral.pixelColor(200,120)
    for x,title in t.event_rects:
        assert any(x==pytest.approx(t.x(e.time)) for e in p.events)
        assert title
    scroll.horizontalScrollBar().setValue(300);app.processEvents()
    assert t.solar is p and t.x(rows[0].start)==rect.left()
    assert t.grab().toImage().pixelColor(200,120)==colored.pixelColor(200,120)
    t.zoom(2);app.processEvents()
    assert t.rectangle(rows[0]).width()==pytest.approx(rect.width()*2)
    t.set_solar(None);app.processEvents()
    assert t.grab().toImage().pixelColor(200,120)==neutral.pixelColor(200,120)
    scroll.close();scroll.deleteLater()


def test_continuous_color_interpolation():
    for boundary in (-18,-12,-6,0,12):
        a=solar_colors([boundary-.001]);b=solar_colors([boundary+.001])
        assert max(abs(x-y) for x,y in zip(a,b))<=1


def test_service_latest_only_cache_failure_and_shutdown():
    started=threading.Event();release=threading.Event();calls=[]
    def calculate(site,start,end,stopped):
        calls.append(site);started.set();release.wait(3)
        if site.longitude==99: raise ValueError('fixture error')
        return site
    s=SolarService(calculate);start=instant('2026-03-20T00:00:00Z');end=start+timedelta(days=1)
    first,second=Site(0,0,0,'UTC'),Site(10,20,0,'UTC')
    try:
        s.request(first,start,end,True);assert started.wait(1)
        s.request(second,start,end,True);assert s.profile is None and len(calls)==1
        release.set()
        deadline=time.monotonic()+3
        while s.profile is not second and time.monotonic()<deadline:s.poll();time.sleep(.01)
        assert s.profile is second and calls==[first,second]
        s.request(first,start,end,True);assert s.profile is first and len(calls)==2
        s.request(None,start,end,True);assert s.profile is None and s.state=='missing'
        s.request(first,start,end,False);assert s.profile is None and s.state=='off'
        s.request(Site(0,99,0,'UTC'),start,end,True)
        deadline=time.monotonic()+3
        while s.state!='error' and time.monotonic()<deadline:s.poll();time.sleep(.01)
        assert s.state=='error'
        for _ in range(10):s.poll()
        assert len(calls)==3
    finally: release.set();s.stop()


def test_background_preference_and_confirmed_location_only(app,tmp_path):
    from telescope_desk.settings import SettingsService
    from telescope_desk.planner_widget import PlannerWidget
    sky=SimpleNamespace(catalog=SimpleNamespace(by_id={}),site=None,target=None)
    settings=SettingsService(tmp_path/'settings.json')
    widget=PlannerWidget(sky,settings)
    try:
        assert widget.day_night.isChecked() and widget.solar.state=='missing'
        assert widget.solar.future is None
        widget.day_night.setChecked(False)
        assert SettingsService(settings.path).values['planner_day_night'] is False
        sky.site=Site(52,13,0,'UTC');widget.refresh_solar()
        assert widget.solar.future is None and widget.timeline.solar is None
        widget.day_night.setChecked(True)
        assert widget.solar.desired[0]==sky.site
        sky.site=None;widget.refresh_solar()
        assert widget.timeline.solar is None and widget.solar.state=='missing'
    finally:widget.stop();widget.close();widget.deleteLater()
