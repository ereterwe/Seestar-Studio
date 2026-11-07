"""Offline geometric sky calculations. No site inference or IERS download."""
from ..i18n import source as ui_text, tr
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import math
import warnings
from zoneinfo import ZoneInfo
import numpy as np
from astropy import units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, get_body, get_sun
from astropy.time import Time
from astropy.utils import iers
iers.conf.auto_download = False
iers.conf.auto_max_age = None
iers.conf.iers_degraded_accuracy = 'warn'

@dataclass(frozen=True)
class Site:
    latitude: float
    longitude: float
    elevation: float
    timezone: str

    def __post_init__(self):
        if not all((math.isfinite(v) for v in (self.latitude, self.longitude, self.elevation))):
            raise ValueError(ui_text('m0338'))
        if not -90 <= self.latitude <= 90 or not -180 <= self.longitude <= 180 or (not -500 <= self.elevation <= 10000):
            raise ValueError(ui_text('m0339'))
        ZoneInfo(self.timezone)

@dataclass(frozen=True)
class Night:
    times: tuple[datetime, ...]
    altitude: tuple[float, ...]
    sun_altitude: tuple[float, ...]
    moon_separation: tuple[float, ...]
    windows: tuple[tuple[datetime, datetime], ...]
    dark_windows: tuple[tuple[datetime, datetime], ...]
    rise: tuple[datetime, ...]
    setting: tuple[datetime, ...]
    transit: datetime
    current_alt: float
    current_az: float
    current_moon: float
    warning: str

def intervals(times, mask):
    """Conservative complete sample intervals: no extrapolated availability."""
    result = []
    start = None
    for i, ok in enumerate(mask):
        if ok and start is None:
            start = i
        if start is not None and (not ok or i == len(mask) - 1):
            end = i if ok else i - 1
            if end > start:
                result.append((times[start], times[end]))
            start = None
    return tuple(result)

def crossings(times, values, rising):
    result = []
    for i in range(len(values) - 1):
        a, b = values[i:i + 2]
        if a <= 0 < b if rising else a >= 0 > b:
            fraction = -a / (b - a)
            result.append(times[i] + (times[i + 1] - times[i]) * fraction)
    return tuple(result)

def calculate(target, site: Site, night_date: date, now=None, minimum_altitude=30):
    if not target.valid:
        raise ValueError(ui_text('m0335'))
    if not 0 <= minimum_altitude <= 90:
        raise ValueError(ui_text('m0336'))
    tz = ZoneInfo(site.timezone)
    start = datetime.combine(night_date, datetime.min.time(), tz).replace(hour=12).astimezone(timezone.utc)
    end = datetime.combine(night_date + timedelta(days=1), datetime.min.time(), tz).replace(hour=12).astimezone(timezone.utc)
    times = tuple((start + timedelta(minutes=i * 5) for i in range(int((end - start).total_seconds() // 300) + 1)))
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError(ui_text('m0337'))
    location = EarthLocation.from_geodetic(site.longitude * u.deg, site.latitude * u.deg, site.elevation * u.m)
    coord = SkyCoord(ra=target.ra * u.deg, dec=target.dec * u.deg, frame='icrs')
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        instants = Time([*times, now])
        frame = AltAz(obstime=instants, location=location, pressure=0 * u.hPa)
        position = coord.transform_to(frame)
        sun = get_sun(instants).transform_to(frame)
        moon = get_body('moon', instants, location=location, ephemeris='builtin').transform_to(frame)
        separation = position.separation(moon).deg
    alt, solar = (position.alt.deg[:-1], sun.alt.deg[:-1])
    dark = solar <= -18
    warning = ui_text('m0330')
    if caught:
        warning += ui_text('m0331')
    return Night(times, tuple(alt), tuple(solar), tuple(separation[:-1]), intervals(times, dark & (alt >= minimum_altitude)), intervals(times, dark), crossings(times, alt, True), crossings(times, alt, False), times[int(np.argmax(alt))], float(position.alt.deg[-1]), float(position.az.deg[-1]), float(separation[-1]), warning)

@dataclass(frozen=True)
class Camera:
    name: str
    width: int
    height: int
    pixel_um: float
    focal_mm: float

    @property
    def fov(self):
        return tuple((math.degrees(2 * math.atan(pixels * self.pixel_um / 1000 / (2 * self.focal_mm))) for pixels in (self.width, self.height)))
CAMERAS = (Camera(ui_text('m0332'), 1080, 1920, 2.9, 250), Camera(ui_text('m0333'), 2160, 3840, 2.9, 260), Camera(ui_text('m0334'), 2160, 3840, 1.6, 6))
