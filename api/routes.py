"""
API routes for astronomy calculations
"""
from fastapi import APIRouter, HTTPException
from astropy.time import Time
from datetime import datetime
import sys
import os

# Add parent directory to path to import from root modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DayOfTheWeek import jd_to_weekday
from api.models import DateTimeRequest, DayOfWeekResponse

router = APIRouter()

# Day names mapping
DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


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
        # Combine date and time
        datetime_str = f"{request.date} {request.time}"
        
        # Parse the datetime
        dt = datetime.fromisoformat(datetime_str)
        
        # Convert to Julian Date using astropy
        t = Time(dt, format='datetime', scale='utc')
        jd = t.jd
        
        # Calculate day of week
        day_index = jd_to_weekday(jd)
        day_name = DAY_NAMES[day_index]
        
        return DayOfWeekResponse(
            julian_date=jd,
            day_of_week=day_index,
            day_name=day_name,
            input_datetime=datetime_str
        )
        
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
