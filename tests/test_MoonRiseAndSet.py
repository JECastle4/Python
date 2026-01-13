# tests/test_MoonRiseAndSet.py
from MoonRiseAndSet import moonrise, moonset
from astropy.coordinates import EarthLocation
import astropy.units as u
from astropy.time import Time


def test_moonrise_equator_apr28_2025():
    """Test moonrise at equator on April 28, 2025 - should return a valid time."""
    location = EarthLocation(lat=0*u.deg, lon=0*u.deg, height=0*u.m)
    jd = Time('2025-04-28', format='iso', scale='utc').jd
    result = moonrise(location, jd)
    assert result is not None, "Moonrise should occur at the equator"
    assert isinstance(result, Time), "Result should be an astropy Time object"


def test_moonset_equator_apr28_2025():
    """Test moonset at equator on April 28, 2025 - should return a valid time."""
    location = EarthLocation(lat=0*u.deg, lon=0*u.deg, height=0*u.m)
    jd = Time('2025-04-28', format='iso', scale='utc').jd
    result = moonset(location, jd)
    assert result is not None, "Moonset should occur at the equator"
    assert isinstance(result, Time), "Result should be an astropy Time object"


def test_moonrise_different_latitudes_apr28_2025():
    """Test that moonrise occurs at different times at different latitudes on the same day."""
    jd = Time('2025-04-28', format='iso', scale='utc').jd
    
    # Equator
    location_equator = EarthLocation(lat=0*u.deg, lon=0*u.deg, height=0*u.m)
    moonrise_equator = moonrise(location_equator, jd)
    
    # London (mid-latitude)
    location_london = EarthLocation(lat=51.5*u.deg, lon=-0.127*u.deg, height=0*u.m)
    moonrise_london = moonrise(location_london, jd)
    
    assert moonrise_equator is not None, "Moonrise should occur at equator"
    assert moonrise_london is not None, "Moonrise should occur in London"
    
    # Moonrise times should be different at different latitudes
    time_diff = abs((moonrise_london - moonrise_equator).to(u.hour).value)
    assert time_diff > 0.1, f"Moonrise times should differ significantly between latitudes, got {time_diff:.2f} hours"
    
    print(f"Moonrise at equator: {moonrise_equator.iso}")
    print(f"Moonrise in London: {moonrise_london.iso}")
    print(f"Time difference: {time_diff:.2f} hours")


def test_moonrise_different_latitudes_apr28_2025():
    """Test that moonrise occurs at different times at different latitudes on the same day."""
    jd = Time('2025-04-28', format='iso', scale='utc').jd
    
    # Equator
    location_equator = EarthLocation(lat=0*u.deg, lon=0*u.deg, height=0*u.m)
    moonrise_equator = moonrise(location_equator, jd)
    
    # London (mid-latitude)
    location_london = EarthLocation(lat=51.5*u.deg, lon=-0.127*u.deg, height=0*u.m)
    moonrise_london = moonrise(location_london, jd)
    
    assert moonrise_equator is not None, "Moonrise should occur at equator"
    assert moonrise_london is not None, "Moonrise should occur in London"
    
    # Moonrise times should be different at different latitudes
    time_diff = abs((moonrise_london - moonrise_equator).to(u.hour).value)
    assert time_diff > 0.1, f"Moonrise times should differ significantly between latitudes, got {time_diff:.2f} hours"
    
    print(f"Moonrise at equator: {moonrise_equator.iso}")
    print(f"Moonrise in London: {moonrise_london.iso}")
    print(f"Time difference: {time_diff:.2f} hours")


def test_moonrise_consecutive_days_london():
    """Test that moonrise times are different on consecutive days."""
    location = EarthLocation(lat=51.5*u.deg, lon=-0.127*u.deg, height=0*u.m)
    
    # Test three consecutive days
    jd_apr28 = Time('2025-04-28', format='iso', scale='utc').jd
    jd_apr29 = Time('2025-04-29', format='iso', scale='utc').jd
    jd_apr30 = Time('2025-04-30', format='iso', scale='utc').jd
    
    moonrise_apr28 = moonrise(location, jd_apr28)
    moonrise_apr29 = moonrise(location, jd_apr29)
    moonrise_apr30 = moonrise(location, jd_apr30)
    
    assert moonrise_apr28 is not None, "Moonrise should occur on Apr 28"
    assert moonrise_apr29 is not None, "Moonrise should occur on Apr 29"
    assert moonrise_apr30 is not None, "Moonrise should occur on Apr 30"
    
    # Times should be different day-to-day
    assert moonrise_apr28 != moonrise_apr29, "Moonrise times should differ between consecutive days"
    assert moonrise_apr29 != moonrise_apr30, "Moonrise times should differ between consecutive days"
    
    print(f"\nLondon moonrise times:")
    print(f"Apr 28: {moonrise_apr28.iso}")
    print(f"Apr 29: {moonrise_apr29.iso}")
    print(f"Apr 30: {moonrise_apr30.iso}")


def test_moonset_consecutive_days_london():
    """Test that moonset times are different on consecutive days."""
    location = EarthLocation(lat=51.5*u.deg, lon=-0.127*u.deg, height=0*u.m)
    
    jd_apr28 = Time('2025-04-28', format='iso', scale='utc').jd
    jd_apr29 = Time('2025-04-29', format='iso', scale='utc').jd
    
    moonset_apr28 = moonset(location, jd_apr28)
    moonset_apr29 = moonset(location, jd_apr29)
    
    assert moonset_apr28 is not None, "Moonset should occur on Apr 28"
    assert moonset_apr29 is not None, "Moonset should occur on Apr 29"
    
    # Times should be different day-to-day
    assert moonset_apr28 != moonset_apr29, "Moonset times should differ between consecutive days"
    
    print(f"\nLondon moonset times:")
    print(f"Apr 28: {moonset_apr28.iso}")
    print(f"Apr 29: {moonset_apr29.iso}")
