"""
API routes for astronomy calculations
"""
from fastapi import APIRouter, HTTPException
from api.models import DateTimeRequest, DayOfWeekResponse
from api.services.dates import calculate_day_of_week

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
