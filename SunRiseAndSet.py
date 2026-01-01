from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun
import astropy.units as u
import numpy as np


def sunrise(location: EarthLocation, julianDate: float, target_altitude: u.Quantity = -0.833 * u.deg, tolerance: u.Quantity = 1 * u.second):
    """Estimate sunrise time (UTC) for a given EarthLocation and Julian date.

    Parameters
    ----------
    location : EarthLocation
        Observer location.
    julianDate : float
        Any Julian date for the desired date (the function uses the date's noon UTC as a reference).
    target_altitude : astropy.units.Quantity, optional
        The geometric altitude to consider "rise" (default -0.833 deg accounts for refraction and Sun radius).
    tolerance : astropy.units.Quantity, optional
        Desired accuracy for the returned time (default 1 second).

    Returns
    -------
    astropy.time.Time or None
        The estimated UTC Time of sunrise, or ``None`` if the Sun does not rise on that date for the location
        (e.g., polar day/night).
    """
    # reference midday UTC for the given julianDate
    midday = Time(julianDate, format='jd', scale='utc') + 0.5 * u.day

    # build a coarse time grid over +/- 12 hours (fine-enough to bracket sunrise)
    hours = np.linspace(-12, 12, 241)  # 0.1 hour steps (~6 minutes)
    times = midday + hours * u.hour

    # vectorized altitude computation
    suncoords = get_sun(times)
    altaz = suncoords.transform_to(AltAz(obstime=times, location=location))
    altitudes = altaz.alt.to(u.deg)

    # target difference
    diffs = (altitudes - target_altitude.to(u.deg))

    # find solar noon (time of maximum altitude)
    noon_idx = int(np.argmax(altitudes.value))

    # find the first index (from start up to noon) where altitude >= target (morning crossing)
    morning_zone = diffs[: noon_idx + 1]
    nonneg = np.where(morning_zone >= 0)[0]
    if nonneg.size == 0:
        # no crossing before noon: sun either always above (polar day) or always below (polar night)
        if np.all(diffs > 0):
            return None
        else:
            return None

    idx = int(nonneg[0])
    if idx == 0:
        left = times[0]
        right = times[1]
    else:
        left = times[idx - 1]
        right = times[idx]


    left_val = alt_at(left, location) - target_altitude.to(u.deg).value
    # right_val = alt_at(right, location) - target_altitude.to(u.deg).value

    # ensure we have a sign change (left <= 0 <= right)
    if left_val > 0:
        # attempt to step left until sign change or exhausted
        j = idx - 1
        while j >= 0 and left_val > 0:
            left = times[j]
            left_val = alt_at(left, location) - target_altitude.to(u.deg).value
            j -= 1
        if left_val > 0:
            return None

    # bisection refinement
    tol_days = tolerance.to(u.s).value / 86400.0
    while (right.jd - left.jd) > tol_days:
        mid_jd = 0.5 * (left.jd + right.jd)
        mid = Time(mid_jd, format='jd', scale='utc')
        mid_val = alt_at(mid, location) - target_altitude.to(u.deg).value
        if mid_val < 0:
            left = mid
        else:
            right = mid

    # return the first time the altitude reaches/exceeds target (right bound)
    return right

def sunset(location: EarthLocation, julianDate: float, target_altitude: u.Quantity = -0.833 * u.deg, tolerance: u.Quantity = 1 * u.second):
    """Estimate sunset time (UTC) for a given EarthLocation and Julian date.

    This searches *after* solar noon for the time the Sun descends through the `target_altitude`.

    Parameters
    ----------
    location : EarthLocation
        Observer location.
    julianDate : float
        Any Julian date for the desired date (the function uses the date's noon UTC as a reference).
    target_altitude : astropy.units.Quantity, optional
        The geometric altitude to consider "set" (default -0.833 deg accounts for refraction and Sun radius).
    tolerance : astropy.units.Quantity, optional
        Desired accuracy for the returned time (default 1 second).

    Returns
    -------
    astropy.time.Time or None
        The estimated UTC Time of sunset, or ``None`` if the Sun does not set on that date for the location
        (e.g., polar day/night).
    """
    # reference midday UTC for the given julianDate
    midday = Time(julianDate, format='jd', scale='utc') + 0.5 * u.day

    # build a coarse time grid over +/- 12 hours (fine-enough to bracket sunset)
    hours = np.linspace(-12, 12, 241)  # 0.1 hour steps (~6 minutes)
    times = midday + hours * u.hour

    # vectorized altitude computation
    suncoords = get_sun(times)
    altaz = suncoords.transform_to(AltAz(obstime=times, location=location))
    altitudes = altaz.alt.to(u.deg)

    # target difference
    diffs = (altitudes - target_altitude.to(u.deg))

    # find solar noon (time of maximum altitude)
    noon_idx = int(np.argmax(altitudes.value))

    # look for the first time after (or at) noon where altitude goes below or equal to target
    evening_zone = diffs[noon_idx:]
    leq = np.where(evening_zone <= 0)[0]
    if leq.size == 0:
        # no crossing after noon: sun either always above (polar day) or always below (polar night)
        if np.all(diffs > 0):
            return None
        else:
            return None

    rel_idx = int(leq[0])
    if rel_idx == 0:
        # already below (or at) target at noon -> no sunset later
        return None

    abs_idx = noon_idx + rel_idx
    left = times[abs_idx - 1]
    right = times[abs_idx]

    left_val = alt_at(left, location) - target_altitude.to(u.deg).value
    right_val = alt_at(right, location) - target_altitude.to(u.deg).value

    # ensure we have a sign change (left >= 0 >= right)
    if left_val < 0:
        # attempt to step left until sign change or exhausted
        j = abs_idx - 2
        while j >= 0 and left_val < 0:
            left = times[j]
            left_val = alt_at(left) - target_altitude.to(u.deg).value
            j -= 1
        if left_val < 0:
            return None

    if right_val > 0:
        # attempt to step right until sign change or exhausted
        j = abs_idx + 1
        while j < len(times) and right_val > 0:
            right = times[j]
            right_val = alt_at(right, location) - target_altitude.to(u.deg).value
            j += 1
        if right_val > 0:
            return None

    # bisection refinement (left positive, right negative)
    tol_days = tolerance.to(u.s).value / 86400.0
    while (right.jd - left.jd) > tol_days:
        mid_jd = 0.5 * (left.jd + right.jd)
        mid = Time(mid_jd, format='jd', scale='utc')
        mid_val = alt_at(mid, location) - target_altitude.to(u.deg).value
        if mid_val > 0:
            left = mid
        else:
            right = mid

    # return the first time the altitude drops to/below target (right bound)
    return right
    
# helper to compute altitude at a scalar Time
def alt_at(t: Time, location) -> float:
    return get_sun(t).transform_to(AltAz(obstime=t, location=location)).alt.to(u.deg).value
