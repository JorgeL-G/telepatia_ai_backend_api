import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_ping_endpoint(self, client: TestClient):
        """Test GET /health/ping returns successful response."""
        response = client.get("/health/ping")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"
        assert "timestamp" in data
    
    @patch('app.database.MongoDBConnection')
    def test_db_connection_endpoint(self, mock_mongodb, client: TestClient):
        """Test GET /health/db_connection returns connection status."""
        # Mock successful connection
        mock_instance = mock_mongodb.return_value
        mock_instance.connect_to_mongo.return_value = None
        
        response = client.get("/health/db_connection")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "database_status" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
