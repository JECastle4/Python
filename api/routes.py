"""
API routes for astronomy calculations
"""
from fastapi import APIRouter, HTTPException
from api.models import (
    DateTimeRequest,
    DayOfWeekResponse,
    SunPositionRequest,
    SunPositionResponse,
    MoonPositionRequest,
    MoonPositionResponse,
    MoonPhaseRequest,
    MoonPhaseResponse,
)
from api.services.dates import calculate_day_of_week
from api.services.sun import calculate_sun_position
from api.services.moon import calculate_moon_position
from api.services.moon_phase import calculate_moon_phase

router = APIRouter()


@router.post("/day-of-week", response_model=DayOfWeekResponse)
async def get_day_of_week(request: DateTimeRequest):
    """
    Calculate the day of the week from a given date and time.
    
    Converts the input date/time to Julian Date (JD) using astropy,
    then calculates which day of the week it falls on.
    
    - **date**: Date in ISO format (YYYY-MM-DD)
    - **time**: Optional time in HH:MM:SS format (defaults to 00:00:00)
    
    Returns:
    - **julian_date**: The JD as a float
    - **day_of_week**: Integer 0-6 (0=Sunday)
    - **day_name**: Name of the day
    - **input_datetime**: The processed input
    """
    try:
        result = calculate_day_of_week(request.date, request.time)
        return DayOfWeekResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date/time format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating day of week: {str(e)}"
        )


@router.post("/sun-position", response_model=SunPositionResponse)
async def get_sun_position(request: SunPositionRequest):
    """
    Calculate the sun's position at a given time and location.
    
    Returns altitude (angle above horizon) and azimuth (compass direction),
    along with visibility status.
    
    - **date**: Date in ISO format (YYYY-MM-DD)
    - **time**: Time in HH:MM:SS format
    - **latitude**: Latitude in degrees (-90 to 90)
    - **longitude**: Longitude in degrees (-180 to 180)
    - **elevation**: Elevation above sea level in meters (optional)
    
    Returns:
    - **altitude**: Sun's altitude in degrees (negative = below horizon)
    - **azimuth**: Sun's azimuth in degrees (0=North, 90=East)
    - **is_visible**: True if sun is above horizon
    - **julian_date**: JD for this calculation
    - **input_datetime**: The processed input
    - **location**: The location used for calculation
    """
    try:
        result = calculate_sun_position(
            request.date,
            request.time,
            request.latitude,
            request.longitude,
            request.elevation
        )
        return SunPositionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating sun position: {str(e)}"
        )


@router.post("/moon-position", response_model=MoonPositionResponse)
async def get_moon_position(request: MoonPositionRequest):
    """
    Calculate the moon's position at a given time and location.
    
    Returns altitude (angle above horizon) and azimuth (compass direction),
    along with visibility status.
    
    - **date**: Date in ISO format (YYYY-MM-DD)
    - **time**: Time in HH:MM:SS format
    - **latitude**: Latitude in degrees (-90 to 90)
    - **longitude**: Longitude in degrees (-180 to 180)
    - **elevation**: Elevation above sea level in meters (optional)
    
    Returns:
    - **altitude**: Moon's altitude in degrees (negative = below horizon)
    - **azimuth**: Moon's azimuth in degrees (0=North, 90=East)
    - **is_visible**: True if moon is above horizon
    - **julian_date**: JD for this calculation
    - **input_datetime**: The processed input
    - **location**: The location used for calculation
    """
    try:
        result = calculate_moon_position(
            request.date,
            request.time,
            request.latitude,
            request.longitude,
            request.elevation
        )
        return MoonPositionResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating moon position: {str(e)}"
        )


@router.post("/moon-phase", response_model=MoonPhaseResponse)
async def get_moon_phase(request: MoonPhaseRequest):
    """
    Calculate the moon's phase information at a given time and location.
    
    Returns illumination fraction (0=new, 1=full), phase angle in ecliptic
    longitude (0-180°=waxing, 180-360°=waning), and textual phase name.
    
    Note: Phase calculation requires both sun and moon positions to determine
    the angular separation and ecliptic longitude difference.
    
    - **date**: Date in ISO format (YYYY-MM-DD)
    - **time**: Time in HH:MM:SS format
    - **latitude**: Latitude in degrees (-90 to 90)
    - **longitude**: Longitude in degrees (-180 to 180)
    - **elevation**: Elevation above sea level in meters (optional)
    
    Returns:
    - **illumination**: Fraction illuminated (0.0 to 1.0)
    - **phase_angle**: Angle in ecliptic (0-360°)
    - **phase_name**: E.g., "Waxing Crescent", "Full Moon"
    - **julian_date**: JD for this calculation
    - **input_datetime**: The processed input
    - **location**: The location used for calculation
    """
    try:
        result = calculate_moon_phase(
            request.date,
            request.time,
            request.latitude,
            request.longitude,
            request.elevation
        )
        return MoonPhaseResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating moon phase: {str(e)}"
        )
