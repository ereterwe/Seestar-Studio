from dataclasses import replace
from datetime import date, datetime, timezone
import pytest
from telescope_desk.sky.catalog import Catalog, normalized
from telescope_desk.sky.astronomy import Site, calculate, CAMERAS


@pytest.fixture(scope='module')
def catalog():
    return Catalog()


def test_catalog_aliases_and_complete_lists(catalog):
    assert len(catalog.targets) > 13000
    for a, b in [('M31', 'Andromeda'), ('NGC7000', 'North America'), ('M45', 'Pleiades')]:
        assert catalog.search(a)[0].id == catalog.search(b)[0].id
    assert len(catalog.search('', 'Messier')) == 110
    assert len(catalog.search('', 'Caldwell')) == 109
    assert 'umstritten' in catalog.search('M102')[0].note
    assert normalized('NGC 000224') == normalized('ngc224')


def test_camera_fov_is_physical():
    assert CAMERAS[0].fov == pytest.approx((.7178, 1.2761), abs=.001)
    assert CAMERAS[1].fov == pytest.approx((1.3803, 2.4536), abs=.002)
    assert CAMERAS[2].fov[0] > 30


def test_site_validation():
    with pytest.raises(ValueError):
        Site(91, 0, 0, 'UTC')
    with pytest.raises(ValueError):
        Site(float('nan'), 0, 0, 'UTC')


def test_offline_night_dst_and_polar_cases(catalog, monkeypatch):
    import socket
    monkeypatch.setattr(socket.socket, 'connect', lambda *a: pytest.fail('Astronomy attempted network access'))
    site = Site(52, 13, 40, 'Europe/Berlin')  # synthetic test site, never user configuration
    target = catalog.search('M31')[0]
    n = calculate(target, site, date(2026, 10, 24), datetime(2026, 10, 24, 22, tzinfo=timezone.utc))
    assert (n.times[-1] - n.times[0]).total_seconds() == 25 * 3600
    assert 0 <= n.current_az < 360 and -90 <= n.current_alt <= 90
    assert 0 <= n.current_moon <= 180
    assert n.dark_windows
    for start, end in n.windows:
        assert end > start
        for t, alt, sun in zip(n.times, n.altitude, n.sun_altitude):
            if start <= t <= end:
                assert alt >= 30 and sun <= -18
    polar = calculate(replace(target, dec=89), Site(80, 0, 0, 'UTC'), date(2026, 6, 20))
    assert not polar.windows and not polar.dark_windows and not polar.rise and not polar.setting


def test_equator_celestial_pole_stays_on_horizon(catalog):
    n = calculate(replace(catalog.search('M31')[0], dec=90), Site(0, 0, 0, 'UTC'), date(2026, 11, 6))
    assert max(abs(a) for a in n.altitude) < .3  # includes precession since J2000


def test_native_sky_load_and_unconfigured_site(app, tmp_path):
    import time
    from telescope_desk.settings import SettingsService
    from telescope_desk.sky.widget import SkyExplorerWidget
    w = SkyExplorerWidget(SettingsService(tmp_path / 'settings.json'))
    try:
        deadline = time.monotonic() + 5
        while w.catalog is None and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.02)
        assert w.catalog is not None
        w.search.setText('M31')
        assert w.target.id == 'NGC0224'
        assert w.site is None and w.night is None
    finally:
        w.stop()
        w.close()
