"""Offline solar timeline: Astropy, geometric centre, standard rise/set horizon.

No location discovery, ephemeris downloads, persistence or device commands.
Sunrise/set use -0.8333 degrees (standard refraction + solar semidiameter).
Twilight uses geometric -6/-12/-18 degrees; colour phases use 0/-6/-12/-18.
"""
from concurrent.futures import ThreadPoolExecutor, CancelledError
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
import threading
import warnings
import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, get_sun
from astropy.time import Time
from .sky.astronomy import Site  # also configures offline IERS

SUNRISE_ALTITUDE = -0.8333
COLOR_STOPS = ((-18, (7, 12, 23)), (-12, (18, 32, 57)),
               (-6, (44, 39, 69)), (0, (104, 65, 48)), (12, (132, 105, 55)))


def solar_colors(altitudes):
    """Continuous muted colour interpolation, independent of pixels/timezone."""
    values = np.asarray(altitudes, dtype=float)
    anchors = np.array([p[0] for p in COLOR_STOPS])
    channels = np.array([p[1] for p in COLOR_STOPS])
    rgb = np.column_stack([np.interp(values, anchors, channels[:, i]) for i in range(3)])
    return np.column_stack((np.rint(rgb).astype(np.uint8), np.full(len(values), 255, dtype=np.uint8))).astype(np.uint8).tobytes()


@dataclass(frozen=True)
class SolarEvent:
    time: datetime
    kind: str
    altitude: float


@dataclass(frozen=True)
class SolarProfile:
    start: datetime
    end: datetime
    times: tuple[datetime, ...]
    altitudes: tuple[float, ...]
    events: tuple[SolarEvent, ...]
    colors: bytes
    dark_seconds: float
    warning: bool

    @property
    def conditions(self):
        result = []
        if min(self.altitudes) > 0:
            result.append('solar.polar_day')
        elif max(self.altitudes) < SUNRISE_ALTITUDE:
            result.append('solar.polar_night')
        if min(self.altitudes) > -18:
            result.append('solar.no_dark')
        return result


def sun_altitudes(site, times):
    location = EarthLocation.from_geodetic(site.longitude*u.deg, site.latitude*u.deg, site.elevation*u.m)
    instants = Time(times)
    # Astropy's atmospheric approximation is unreliable below the horizon.
    # Keep geometric altitude and correct the rise/set threshold instead.
    frame = AltAz(obstime=instants, location=location, pressure=0*u.hPa)
    return np.asarray(get_sun(instants).transform_to(frame).alt.deg)


def calculate_solar(site: Site, start: datetime, end: datetime, stopped=None):
    if start.utcoffset() is None or end.utcoffset() is None:
        raise ValueError('Solar times must be timezone-aware')
    start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    duration = (end-start).total_seconds()
    if not 0 < duration <= 366*86400:
        raise ValueError('Solar display range must be within 366 days')
    stopped = stopped or threading.Event()
    if stopped.is_set(): raise CancelledError()
    count = math.ceil(duration/60)
    times = tuple(start + timedelta(seconds=duration*i/count) for i in range(count+1))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        pieces = []
        for offset in range(0, len(times), 1441):
            if stopped.is_set(): raise CancelledError()
            pieces.append(sun_altitudes(site, times[offset:offset+1441]))
        values = np.concatenate(pieces)
        brackets = []
        for threshold, rising, falling in ((SUNRISE_ALTITUDE, 'sunrise', 'sunset'),
                (-6., 'civil_dawn', 'civil_dusk'), (-12., 'nautical_dawn', 'nautical_dusk'),
                (-18., 'night_end', 'night_start')):
            for i in np.flatnonzero((values[:-1] < threshold) != (values[1:] < threshold)):
                brackets.append((times[i], times[i+1], threshold, rising if values[i+1] > values[i] else falling, values[i] < threshold))
        # Refine all crossings together; < 1 second numerical bracket, not a
        # claim of subsecond physical accuracy at the atmospheric horizon.
        for _ in range(7):
            if not brackets: break
            if stopped.is_set(): raise CancelledError()
            middles = [a+(b-a)/2 for a,b,_,_,_ in brackets]
            heights = sun_altitudes(site, middles)
            brackets = [(mid,b,h,k,below) if (v<h)==below else (a,mid,h,k,below)
                        for (a,b,h,k,below),mid,v in zip(brackets,middles,heights)]
        events = tuple(sorted((SolarEvent(a+(b-a)/2, k, h) for a,b,h,k,_ in brackets), key=lambda e:e.time))
    # Integrate actual dark intervals, including clipped multi-day/polar ranges.
    dark = values[0] <= -18
    last, seconds = start, 0.
    for event in events:
        if event.kind not in ('night_start', 'night_end'): continue
        if dark: seconds += (event.time-last).total_seconds()
        dark, last = event.kind == 'night_start', event.time
    if dark: seconds += (end-last).total_seconds()
    return SolarProfile(start, end, times, tuple(float(v) for v in values), events,
                        solar_colors(values), seconds, bool(caught))


class SolarService:
    """One bounded worker, newest request only, four-entry in-memory cache."""
    def __init__(self, calculator=calculate_solar):
        self.calculator = calculator
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-solar')
        self.stopped = threading.Event()
        self.future = None
        self.desired = None
        self.cache = OrderedDict()
        self.profile = None
        self.state = 'missing'

    @property
    def running(self):
        return self.future is not None and not self.future[1].done()

    def request(self, site, start, end, enabled):
        key = (site, start, end) if site is not None and enabled else None
        if key != self.desired:
            self.desired = key
            self.profile = None
        if not enabled: self.state = 'off'
        elif key is None: self.state = 'missing'
        else: self.state = 'ready' if self.profile else 'loading'
        self.poll()

    def poll(self):
        if self.stopped.is_set(): return
        if self.future and self.future[1].done():
            key, future = self.future
            self.future = None
            try: result = future.result()
            except Exception: result = None
            self.cache[key] = result
            self.cache.move_to_end(key)
            while len(self.cache) > 4: self.cache.popitem(last=False)
        if self.desired is None: return
        if self.desired in self.cache:
            self.profile = self.cache[self.desired]
            self.state = 'ready' if self.profile is not None else 'error'
        elif self.future is None:
            self.state = 'loading'
            self.future = (self.desired, self.pool.submit(self.calculator, *self.desired, self.stopped))

    def stop(self):
        self.stopped.set()
        self.desired = self.profile = None
        self.cache.clear()
        self.pool.shutdown(wait=False, cancel_futures=True)
