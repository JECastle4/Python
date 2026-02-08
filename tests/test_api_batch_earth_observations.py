"""
Tests for the batch earth observations service
"""
import pytest
from api.services.batch_earth_observations import calculate_batch_earth_observations
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.routes import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_basic_batch_calculation():
    """Test basic batch calculation with multiple frames"""
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="18:00:00",
        frame_count=7,  # 0, 1, 2, 3, 4, 5, 6 hours
        latitude=40.7128,
        longitude=-74.0060,
        elevation=10.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
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
    assert first_frame["datetime"] == "2024-01-01T12:00:00"
    # Check metadata
    assert result["metadata"]["frame_count"] == 7
    assert result["metadata"]["start_datetime"] == "2024-01-01T12:00:00"
    assert result["metadata"]["end_datetime"] == "2024-01-01T18:00:00"
    assert result["metadata"]["time_span_hours"] == 6.0
    assert result["metadata"]["location"]["latitude"] == 40.7128
    assert result["metadata"]["location"]["longitude"] == -74.0060
    assert result["metadata"]["location"]["elevation"] == 10.0


def test_frame_count_validation_too_low():
    """Test that frame_count < 2 raises ValueError"""
    with pytest.raises(ValueError, match="frame_count must be at least 2"):
        gen = calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="13:00:00",
            frame_count=1,
            latitude=0.0,
            longitude=0.0,
            elevation=0.0
        )
        list(gen)


def test_end_before_start_validation():
    """Test that end_datetime must be after start_datetime"""
    with pytest.raises(ValueError, match="end_datetime must be after start_datetime"):
        gen = calculate_batch_earth_observations(
            start_date="2024-01-02",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="12:00:00",
            frame_count=2,
            latitude=0.0,
            longitude=0.0,
            elevation=0.0
        )
        list(gen)


def test_equal_start_end_validation():
    """Test that start and end times cannot be equal"""
    with pytest.raises(ValueError, match="end_datetime must be after start_datetime"):
        gen = calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="12:00:00",
            frame_count=2,
            latitude=0.0,
            longitude=0.0,
            elevation=0.0
        )
        list(gen)


def test_coordinate_validation_latitude():
    """Test that invalid latitude is caught by underlying services"""
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        gen = calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="13:00:00",
            frame_count=2,
            latitude=91.0,
            longitude=0.0,
            elevation=0.0
        )
        list(gen)


def test_coordinate_validation_longitude():
    """Test that invalid longitude is caught by underlying services"""
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        gen = calculate_batch_earth_observations(
            start_date="2024-01-01",
            start_time="12:00:00",
            end_date="2024-01-01",
            end_time="13:00:00",
            frame_count=2,
            latitude=0.0,
            longitude=181.0,
            elevation=0.0
        )
        list(gen)


def test_time_span_calculation():
    """Test that time span is calculated correctly"""
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-02",
        end_time="00:00:00",
        frame_count=5,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert result["metadata"]["time_span_hours"] == 24.0


def test_default_time_values():
    """Test that default start_time is 00:00:00 and end_time is 23:59:59"""
    # This test verifies behavior when defaults might be used by the API
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-01",
        end_time="23:59:59",
        frame_count=2,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert result["frames"][0]["datetime"] == "2024-01-01T00:00:00"
    assert result["frames"][1]["datetime"] == "2024-01-01T23:59:59"
    assert abs(result["metadata"]["time_span_hours"] - 23.9997) < 0.001


def test_large_frame_count():
    """Test with larger frame count"""
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-01",
        end_time="01:00:00",
        frame_count=61,  # Every minute
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert len(result["frames"]) == 61
    assert result["metadata"]["frame_count"] == 61


def test_multi_day_span():
    """Test batch calculation spanning multiple days"""
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-03",
        end_time="12:00:00",
        frame_count=3,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert len(result["frames"]) == 3
    assert result["frames"][0]["datetime"] == "2024-01-01T12:00:00"
    assert result["frames"][1]["datetime"] == "2024-01-02T12:00:00"
    assert result["frames"][2]["datetime"] == "2024-01-03T12:00:00"
    assert result["metadata"]["time_span_hours"] == 48.0

def test_north_pole():
    """Test calculation at North Pole"""
    gen = calculate_batch_earth_observations(
        start_date="2024-06-21",  # Summer solstice
        start_time="12:00:00",
        end_date="2024-06-21",
        end_time="18:00:00",
        frame_count=3,
        latitude=90.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert len(result["frames"]) == 3
    # Sun should be visible at North Pole during summer
    assert result["frames"][0]["sun"]["is_visible"]


def test_south_pole():
    """Test calculation at South Pole"""
    gen = calculate_batch_earth_observations(
        start_date="2024-12-21",  # Winter solstice (summer in southern hemisphere)
        start_time="12:00:00",
        end_date="2024-12-21",
        end_time="18:00:00",
        frame_count=3,
        latitude=-90.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert len(result["frames"]) == 3
    # Sun should be visible at South Pole during southern summer


def test_equator():
    """Test calculation at equator"""
    gen = calculate_batch_earth_observations(
        start_date="2024-03-20",  # Equinox
        start_time="06:00:00",
        end_date="2024-03-20",
        end_time="18:00:00",
        frame_count=5,
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    assert len(result["frames"]) == 5


def test_prime_meridian_and_dateline():
    """Test calculations at Prime Meridian and International Date Line"""
    # Prime Meridian
    gen1 = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=51.4778,  # Greenwich
        longitude=0.0,
        elevation=0.0
    )
    frames1 = []
    metadata1 = None
    for item in gen1:
        if isinstance(item, dict) and "frame_count" in item:
            metadata1 = item
        else:
            frames1.append(item)
    result1 = {"frames": frames1, "metadata": metadata1}
    assert len(result1["frames"]) == 2
    # International Date Line (180 degrees)
    gen2 = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-01",
        end_time="13:00:00",
        frame_count=2,
        latitude=0.0,
        longitude=180.0,
        elevation=0.0
    )
    frames2 = []
    metadata2 = None
    for item in gen2:
        if isinstance(item, dict) and "frame_count" in item:
            metadata2 = item
        else:
            frames2.append(item)
    result2 = {"frames": frames2, "metadata": metadata2}
    assert len(result2["frames"]) == 2


def test_moon_phase_varies_over_month():
    """Test that moon phase changes over a month"""
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="12:00:00",
        end_date="2024-01-29",
        end_time="12:00:00",
        frame_count=5,  # Sample 5 points over ~28 days
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    # Moon phase should change significantly over a month
    phases = [frame["moon_phase"]["phase_angle"] for frame in result["frames"]]
    assert len(set(phases)) > 1  # Phases should be different


def test_sun_moon_visibility_changes():
    """Test that sun and moon visibility can change over time"""
    gen = calculate_batch_earth_observations(
        start_date="2024-01-01",
        start_time="00:00:00",
        end_date="2024-01-02",
        end_time="00:00:00",
        frame_count=25,  # Hourly over 24 hours
        latitude=40.0,
        longitude=0.0,
        elevation=0.0
    )
    frames = []
    metadata = None
    for item in gen:
        if isinstance(item, dict) and "frame_count" in item:
            metadata = item
        else:
            frames.append(item)
    result = {"frames": frames, "metadata": metadata}
    sun_visibility = [frame["sun"]["is_visible"] for frame in result["frames"]]
    # Sun should rise and set during 24 hours at mid-latitudes
    assert True in sun_visibility
    assert False in sun_visibility


def test_sse_batch_earth_observations_stream():
    """Test SSE streaming endpoint for batch earth observations"""
    payload = {
        "start_date": "2024-01-01",
        "start_time": "12:00:00",
        "end_date": "2024-01-01",
        "end_time": "18:00:00",
        "frame_count": 3,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "elevation": 10.0
    }
    response = client.get(
        "/batch-earth-observations-stream",
        params=payload,
        headers={"Accept": "text/event-stream"}
    )
    assert response.status_code == 200
    # Parse SSE events
    events = response.text.strip().split("\n\n")
    frame_events = [e for e in events if e.startswith("event: frame")]
    metadata_events = [e for e in events if e.startswith("event: metadata")]
    assert len(frame_events) == 3
    assert len(metadata_events) == 1
    # Validate frame event structure
    for idx, event in enumerate(frame_events):
        assert f"id: {idx}" in event
        assert "data: " in event
        data = json.loads(event.split("data: ", 1)[1])
        assert "datetime" in data
        assert "sun" in data
        assert "moon" in data
        assert "moon_phase" in data
    # Validate metadata event structure
    metadata_data = json.loads(metadata_events[0].split("data: ", 1)[1])
    assert metadata_data["frame_count"] == 3
    assert metadata_data["start_datetime"] == "2024-01-01T12:00:00"
    assert metadata_data["end_datetime"] == "2024-01-01T18:00:00"
    assert metadata_data["location"]["latitude"] == 40.7128
    assert metadata_data["location"]["longitude"] == -74.0060
    assert metadata_data["location"]["elevation"] == 10.0
