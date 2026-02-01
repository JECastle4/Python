"""
Integration tests for api/routes.py
"""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestDayOfWeekEndpoint:
    """Test cases for /api/v1/day-of-week endpoint"""
    
    def test_valid_request_date_only(self):
        """Test valid request with date only"""
        response = client.post(
            "/api/v1/day-of-week",
            json={"date": "2026-02-01"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["day_of_week"] == 0
        assert data["day_name"] == "Sunday"
        assert "julian_date" in data
        assert isinstance(data["julian_date"], float)
        assert data["input_datetime"] == "2026-02-01 00:00:00"
    
    def test_valid_request_with_time(self):
        """Test valid request with both date and time"""
        response = client.post(
            "/api/v1/day-of-week",
            json={"date": "2026-02-01", "time": "14:30:45"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["day_of_week"] == 0
        assert data["day_name"] == "Sunday"
        assert data["input_datetime"] == "2026-02-01 14:30:45"
    
    def test_different_days_of_week(self):
        """Test multiple dates to verify different days"""
        test_cases = [
            ("2026-02-01", "Sunday", 0),
            ("2026-02-02", "Monday", 1),
            ("2026-02-03", "Tuesday", 2),
        ]
        
        for date, expected_name, expected_index in test_cases:
            response = client.post(
                "/api/v1/day-of-week",
                json={"date": date}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["day_name"] == expected_name
            assert data["day_of_week"] == expected_index
    
    def test_missing_date_field(self):
        """Test request without required date field"""
        response = client.post(
            "/api/v1/day-of-week",
            json={"time": "12:00:00"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_date_format(self):
        """Test with invalid date format"""
        response = client.post(
            "/api/v1/day-of-week",
            json={"date": "not-a-date"}
        )
        
        assert response.status_code == 400
        assert "Invalid date/time format" in response.json()["detail"]
    
    def test_invalid_time_format(self):
        """Test with invalid time format"""
        response = client.post(
            "/api/v1/day-of-week",
            json={"date": "2026-02-01", "time": "not-a-time"}
        )
        
        assert response.status_code == 400
        assert "Invalid date/time format" in response.json()["detail"]
    
    def test_malformed_json(self):
        """Test with malformed JSON"""
        response = client.post(
            "/api/v1/day-of-week",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_empty_request_body(self):
        """Test with empty request body"""
        response = client.post(
            "/api/v1/day-of-week",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_response_structure(self):
        """Test that response contains all required fields"""
        response = client.post(
            "/api/v1/day-of-week",
            json={"date": "2026-02-01", "time": "12:00:00"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields are present
        assert "julian_date" in data
        assert "day_of_week" in data
        assert "day_name" in data
        assert "input_datetime" in data
        
        # Verify types
        assert isinstance(data["julian_date"], float)
        assert isinstance(data["day_of_week"], int)
        assert isinstance(data["day_name"], str)
        assert isinstance(data["input_datetime"], str)
    
    def test_julian_date_increases_with_time(self):
        """Test that JD increases as time progresses through the day"""
        response1 = client.post(
            "/api/v1/day-of-week",
            json={"date": "2026-02-01", "time": "00:00:00"}
        )
        response2 = client.post(
            "/api/v1/day-of-week",
            json={"date": "2026-02-01", "time": "12:00:00"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        jd1 = response1.json()["julian_date"]
        jd2 = response2.json()["julian_date"]
        
        # JD at noon should be greater than JD at midnight
        assert jd2 > jd1
        # Should be approximately 0.5 days apart
        assert abs((jd2 - jd1) - 0.5) < 0.01


class TestHealthEndpoints:
    """Test health check and root endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert data["health"] == "ok"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"


class TestSunPositionEndpoint:
    """Test cases for /api/v1/sun-position endpoint"""
    
    def test_valid_request(self):
        """Test valid sun position request"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-02-01",
                "time": "12:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "elevation": 10.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "altitude" in data
        assert "azimuth" in data
        assert "is_visible" in data
        assert "julian_date" in data
        assert "input_datetime" in data
        assert "location" in data
        
        assert isinstance(data["altitude"], float)
        assert isinstance(data["azimuth"], float)
        assert isinstance(data["is_visible"], bool)
        assert -90 <= data["altitude"] <= 90
        assert 0 <= data["azimuth"] < 360
    
    def test_request_without_elevation(self):
        """Test request with default elevation"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-02-01",
                "time": "12:00:00",
                "latitude": 0.0,
                "longitude": 0.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["location"]["elevation"] == 0.0
    
    def test_invalid_latitude(self):
        """Test with invalid latitude"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-02-01",
                "time": "12:00:00",
                "latitude": 91.0,
                "longitude": 0.0
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_longitude(self):
        """Test with invalid longitude"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-02-01",
                "time": "12:00:00",
                "latitude": 0.0,
                "longitude": 181.0
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self):
        """Test with missing required fields"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-02-01",
                "time": "12:00:00"
                # Missing latitude and longitude
            }
        )
        
        assert response.status_code == 422
    
    def test_invalid_date_format(self):
        """Test with invalid date format"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "not-a-date",
                "time": "12:00:00",
                "latitude": 0.0,
                "longitude": 0.0
            }
        )
        
        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]
    
    def test_sun_visible_at_noon(self):
        """Test that sun is visible at noon"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-06-21",
                "time": "12:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_visible"] is True
        assert data["altitude"] > 0
    
    def test_sun_not_visible_at_midnight(self):
        """Test that sun is not visible at midnight"""
        response = client.post(
            "/api/v1/sun-position",
            json={
                "date": "2026-02-01",
                "time": "00:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_visible"] is False
        assert data["altitude"] < 0


class TestMoonPositionEndpoint:
    """Test cases for /api/v1/moon-position endpoint"""
    
    def test_moon_position_basic(self):
        """Test basic moon position request"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "20:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "elevation": 10.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "altitude" in data
        assert "azimuth" in data
        assert "is_visible" in data
        assert "julian_date" in data
        assert "location" in data
        assert "input_datetime" in data
        
        assert isinstance(data["altitude"], float)
        assert isinstance(data["azimuth"], float)
        assert isinstance(data["is_visible"], bool)
        
        assert -90 <= data["altitude"] <= 90
        assert 0 <= data["azimuth"] <= 360
    
    def test_moon_position_default_elevation(self):
        """Test moon position with default elevation"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "12:00:00",
                "latitude": 0.0,
                "longitude": 0.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["location"]["elevation"] == 0.0
    
    def test_moon_position_southern_hemisphere(self):
        """Test moon position for southern hemisphere"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "12:00:00",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "elevation": 0.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["location"]["latitude"] == -33.8688
        assert data["location"]["longitude"] == 151.2093
    
    def test_moon_position_visibility(self):
        """Test that moon visibility matches altitude"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "12:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "elevation": 0.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if data["altitude"] > 0:
            assert data["is_visible"] is True
        else:
            assert data["is_visible"] is False
    
    def test_moon_position_invalid_date(self):
        """Test moon position with invalid date"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "invalid-date",
                "time": "12:00:00",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "elevation": 0.0
            }
        )
        
        assert response.status_code == 400
    
    def test_moon_position_invalid_latitude(self):
        """Test moon position with invalid latitude"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "12:00:00",
                "latitude": 100.0,
                "longitude": -74.0060,
                "elevation": 0.0
            }
        )
        
        assert response.status_code == 422
    
    def test_moon_position_invalid_longitude(self):
        """Test moon position with invalid longitude"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "12:00:00",
                "latitude": 40.7128,
                "longitude": 200.0,
                "elevation": 0.0
            }
        )
        
        assert response.status_code == 422
    
    def test_moon_position_extreme_elevation(self):
        """Test moon position with Mt. Everest elevation"""
        response = client.post(
            "/api/v1/moon-position",
            json={
                "date": "2025-01-15",
                "time": "12:00:00",
                "latitude": 27.9881,
                "longitude": 86.9250,
                "elevation": 8848.86
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["location"]["elevation"] == 8848.86
