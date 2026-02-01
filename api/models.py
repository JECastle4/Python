"""
Pydantic models for API request and response validation
"""
from pydantic import BaseModel, Field
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


class LocationModel(BaseModel):
    """Model for geographic location"""
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in degrees (-90 to 90, negative=South)"
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in degrees (-180 to 180, negative=West)"
    )
    elevation: float = Field(
        default=0.0,
        description="Elevation above sea level in meters"
    )


class SunPositionRequest(BaseModel):
    """Request model for sun position calculation"""
    date: str = Field(
        ..., 
        description="Date in ISO format (YYYY-MM-DD)",
        examples=["2026-02-01"]
    )
    time: str = Field(
        ...,
        description="Time in HH:MM:SS format",
        examples=["12:30:45"]
    )
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in degrees (-90 to 90, negative=South)",
        examples=[40.7128]
    )
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in degrees (-180 to 180, negative=West)",
        examples=[-74.0060]
    )
    elevation: float = Field(
        default=0.0,
        description="Elevation above sea level in meters",
        examples=[10.0]
    )


class SunPositionResponse(BaseModel):
    """Response model for sun position calculation"""
    altitude: float = Field(
        ...,
        description="Sun's altitude in degrees (negative = below horizon)"
    )
    azimuth: float = Field(
        ...,
        description="Sun's azimuth in degrees (0=North, 90=East, 180=South, 270=West)"
    )
    is_visible: bool = Field(
        ...,
        description="Whether the sun is above the horizon"
    )
    julian_date: float = Field(
        ...,
        description="Julian Date (JD) for this calculation"
    )
    input_datetime: str = Field(
        ...,
        description="The input date and time that was processed"
    )
    location: LocationModel = Field(
        ...,
        description="The location used for the calculation"
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
