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
