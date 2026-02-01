"""Moon position calculation service."""

from astropy.time import Time
from astropy.coordinates import get_body, AltAz, EarthLocation
import astropy.units as u


def calculate_moon_position(
    date_str: str,
    time_str: str,
    latitude: float,
    longitude: float,
    elevation: float = 0.0,
) -> dict:
    """
    Calculate the moon's position (altitude and azimuth) from a given location on Earth.

    Args:
        date_str: Date in ISO format (YYYY-MM-DD)
        time_str: Time in ISO format (HH:MM:SS)
        latitude: Latitude in degrees (-90 to 90)
        longitude: Longitude in degrees (-180 to 180)
        elevation: Elevation in meters (default: 0.0)

    Returns:
        dict: Dictionary containing:
            - altitude: Moon's altitude in degrees (-90 to 90)
            - azimuth: Moon's azimuth in degrees (0 to 360)
            - is_visible: Boolean indicating if moon is above horizon
            - julian_date: Julian Date of the observation
            - location: Dict with latitude, longitude, elevation
            - input_datetime: Original input datetime string
    """
    # Combine date and time
    datetime_str = f"{date_str}T{time_str}"

    # Convert to astropy Time (assumes UTC)
    time = Time(datetime_str, format="isot", scale="utc")

    # Create location
    location = EarthLocation(
        lat=latitude * u.deg, lon=longitude * u.deg, height=elevation * u.m
    )

    # Get moon position
    moon = get_body("moon", time, location)

    # Convert to AltAz frame for the given location and time
    altaz_frame = AltAz(obstime=time, location=location)
    moon_altaz = moon.transform_to(altaz_frame)

    # Extract altitude and azimuth
    altitude = float(moon_altaz.alt.deg)
    azimuth = float(moon_altaz.az.deg)

    # Determine visibility (above horizon means altitude > 0)
    is_visible = bool(altitude > 0)

    return {
        "altitude": altitude,
        "azimuth": azimuth,
        "is_visible": is_visible,
        "julian_date": float(time.jd),
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation,
        },
        "input_datetime": datetime_str,
    }
