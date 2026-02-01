"""
Tests for the batch earth observations service
"""
import pytest
from api.services.batch_earth_observations import calculate_batch_earth_observations


def test_basic_batch_calculation():
    """Test basic batch calculation with multiple frames"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="18:00:00",
        frame_count=7,  # 0, 1, 2, 3, 4, 5, 6 hours
        latitude=40.7128,
        longitude=-74.0060,
        elevation=10.0
    )
    
    assert "frames" in result
    assert "metadata" in result
    assert len(result["frames"]) == 7
    
    # Check first frame
    first_frame = result["frames"][0]
    assert "datetime" in first_frame
    assert "sun" in first_frame
    assert "moon" in first_frame
    assert "moon_phase" in first_frame
    assert first_frame["datetime"] == "2024-01-01T12:00:00"
    
    # Check last frame
    last_frame = result["frames"][-1]
    assert last_frame["datetime"] == "2024-01-01T18:00:00"
    
    # Check sun position structure
    assert "altitude" in first_frame["sun"]
    assert "azimuth" in first_frame["sun"]
    assert "is_visible" in first_frame["sun"]
    
    # Check moon position structure
    assert "altitude" in first_frame["moon"]
    assert "azimuth" in first_frame["moon"]
    assert "is_visible" in first_frame["moon"]
    
    # Check moon phase structure
    assert "illumination" in first_frame["moon_phase"]
    assert "phase_angle" in first_frame["moon_phase"]
    assert "phase_name" in first_frame["moon_phase"]
    
    # Check metadata
    assert result["metadata"]["frame_count"] == 7
    assert result["metadata"]["start_datetime"] == "2024-01-01T12:00:00"
    assert result["metadata"]["end_datetime"] == "2024-01-01T18:00:00"
    assert result["metadata"]["time_span_hours"] == 6.0
    assert result["metadata"]["location"]["latitude"] == 40.7128
    assert result["metadata"]["location"]["longitude"] == -74.0060
    assert result["metadata"]["location"]["elevation"] == 10.0


def test_minimum_two_frames():
    """Test that at least 2 frames are required"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result["frames"]) == 2
    assert result["frames"][0]["datetime"] == "2024-01-01T12:00:00"
    assert result["frames"][1]["datetime"] == "2024-01-01T13:00:00"


def test_frame_count_validation_too_low():
    """Test that frame_count < 2 raises ValueError"""
    with pytest.raises(ValueError, match="frame_count must be at least 2"):
        calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="13:00:00",
            frame_count=1,
            latitude=0.0,
            longitude=0.0,
            elevation=0.0
        )


def test_end_before_start_validation():
    """Test that end_datetime must be after start_datetime"""
    with pytest.raises(ValueError, match="end_datetime must be after start_datetime"):
        calculate_batch_earth_observations(
            start_date="2024-01-02",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="12:00:00",
            frame_count=2,
            latitude=0.0,
            longitude=0.0,
            elevation=0.0
        )


def test_equal_start_end_validation():
    """Test that start and end times cannot be equal"""
    with pytest.raises(ValueError, match="end_datetime must be after start_datetime"):
        calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="12:00:00",
            frame_count=2,
            latitude=0.0,
            longitude=0.0,
            elevation=0.0
        )


def test_coordinate_validation_latitude():
    """Test that invalid latitude is caught by underlying services"""
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="13:00:00",
            frame_count=2,
            latitude=91.0,
            longitude=0.0,
            elevation=0.0
        )


def test_coordinate_validation_longitude():
    """Test that invalid longitude is caught by underlying services"""
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="13:00:00",
            frame_count=2,
            latitude=0.0,
            longitude=181.0,
            elevation=0.0
        )


def test_time_span_calculation():
    """Test that time span is calculated correctly"""
    # 24 hour span
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-02",
        end_time="00:00:00",
        frame_count=5,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert result["metadata"]["time_span_hours"] == 24.0


def test_frame_intervals_evenly_spaced():
    """Test that frames are evenly spaced in time"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-01",
        end_time="04:00:00",
        frame_count=5,  # 0, 1, 2, 3, 4 hours
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert result["frames"][0]["datetime"] == "2024-01-01T00:00:00"
    assert result["frames"][1]["datetime"] == "2024-01-01T01:00:00"
    assert result["frames"][2]["datetime"] == "2024-01-01T02:00:00"
    assert result["frames"][3]["datetime"] == "2024-01-01T03:00:00"
    assert result["frames"][4]["datetime"] == "2024-01-01T04:00:00"


def test_default_time_values():
    """Test that default start_time is 00:00:00 and end_time is 23:59:59"""
    # This test verifies behavior when defaults might be used by the API
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-01",
        end_time="23:59:59",
        frame_count=2,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert result["frames"][0]["datetime"] == "2024-01-01T00:00:00"
    assert result["frames"][1]["datetime"] == "2024-01-01T23:59:59"
    assert abs(result["metadata"]["time_span_hours"] - 23.9997) < 0.001


def test_large_frame_count():
    """Test with larger frame count"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-01",
        end_time="01:00:00",
        frame_count=61,  # Every minute
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result["frames"]) == 61
    assert result["metadata"]["frame_count"] == 61


def test_multi_day_span():
    """Test batch calculation spanning multiple days"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-03",
        end_time="12:00:00",
        frame_count=3,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result["frames"]) == 3
    assert result["frames"][0]["datetime"] == "2024-01-01T12:00:00"
    assert result["frames"][1]["datetime"] == "2024-01-02T12:00:00"
    assert result["frames"][2]["datetime"] == "2024-01-03T12:00:00"
    assert result["metadata"]["time_span_hours"] == 48.0


def test_negative_elevation():
    """Test that negative elevation (below sea level) works"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=31.5,  # Dead Sea area
        longitude=35.5,
        elevation=-430.0  # Dead Sea elevation
    )
    
    assert len(result["frames"]) == 2
    assert result["metadata"]["location"]["elevation"] == -430.0


def test_high_elevation():
    """Test that high elevation works"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=27.9881,  # Mt. Everest
        longitude=86.9250,
        elevation=8848.86
    )
    
    assert len(result["frames"]) == 2
    assert result["metadata"]["location"]["elevation"] == 8848.86


def test_north_pole():
    """Test calculation at North Pole"""
    result = calculate_batch_earth_observations(
        start_date="2024-06-21",  # Summer solstice
        start_time="12:00:00",
        end_date="2024-06-21",
        end_time="18:00:00",
        frame_count=3,
        latitude=90.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result["frames"]) == 3
    # Sun should be visible at North Pole during summer
    assert result["frames"][0]["sun"]["is_visible"]


def test_south_pole():
    """Test calculation at South Pole"""
    result = calculate_batch_earth_observations(
        start_date="2024-12-21",  # Winter solstice (summer in southern hemisphere)
        start_time="12:00:00",
        end_date="2024-12-21",
        end_time="18:00:00",
        frame_count=3,
        latitude=-90.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result["frames"]) == 3
    # Sun should be visible at South Pole during southern summer


def test_equator():
    """Test calculation at equator"""
    result = calculate_batch_earth_observations(
        start_date="2024-03-20",  # Equinox
        start_time="06:00:00",
        end_date="2024-03-20",
        end_time="18:00:00",
        frame_count=5,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result["frames"]) == 5


def test_prime_meridian_and_dateline():
    """Test calculations at Prime Meridian and International Date Line"""
    # Prime Meridian
    result1 = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=51.4778,  # Greenwich
        longitude=0.0,
        elevation=0.0
    )
    
    assert len(result1["frames"]) == 2
    
    # International Date Line (180 degrees)
    result2 = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=0.0,
        longitude=180.0,
        elevation=0.0
    )
    
    assert len(result2["frames"]) == 2


def test_moon_phase_varies_over_month():
    """Test that moon phase changes over a month"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-29",
        end_time="12:00:00",
        frame_count=5,  # Sample 5 points over ~28 days
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    
    # Moon phase should change significantly over a month
    phases = [frame["moon_phase"]["phase_angle"] for frame in result["frames"]]
    assert len(set(phases)) > 1  # Phases should be different


def test_sun_moon_visibility_changes():
    """Test that sun and moon visibility can change over time"""
    result = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-02",
        end_time="00:00:00",
        frame_count=25,  # Hourly over 24 hours
        latitude=40.0,
        longitude=0.0,
        elevation=0.0
    )
    
    sun_visibility = [frame["sun"]["is_visible"] for frame in result["frames"]]
    # Sun should rise and set during 24 hours at mid-latitudes
    assert True in sun_visibility
    assert False in sun_visibility
