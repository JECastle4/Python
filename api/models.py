"""
Pydantic models for API request and response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DateTimeRequest(BaseModel):
    """Request model for date/time input"""
    date: str = Field(
        ..., 
        description="Date in ISO format (YYYY-MM-DD)",
        examples=["2026-02-01"]
    )
    time: Optional[str] = Field(
        default="00:00:00",
        description="Time in HH:MM:SS format (optional, defaults to midnight)",
        examples=["12:30:45"]
    )


class DayOfWeekResponse(BaseModel):
    """Response model for day of week calculation"""
    julian_date: float = Field(
        ...,
        description="Julian Date (JD) as a floating point number"
    )
    day_of_week: int = Field(
        ...,
        description="Day of week as integer (0=Sunday, 1=Monday, ..., 6=Saturday)"
    )
    day_name: str = Field(
        ...,
        description="Name of the day"
    )
    input_datetime: str = Field(
        ...,
        description="The input date and time that was processed"
    )
