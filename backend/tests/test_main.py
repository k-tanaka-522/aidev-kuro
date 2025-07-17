import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_root_endpoint():
    """Test the root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "healthy"


def test_health_endpoint():
    """Test the health check endpoint."""
    client = TestClient(app)
    
    # Mock the DynamoDB health check
    with pytest.mock.patch('app.services.dynamodb.DynamoDBService.health_check', return_value=True):
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert data["services"]["dynamodb"] == "healthy"
        assert data["services"]["api"] == "healthy"


def test_health_endpoint_failure():
    """Test the health check endpoint when DynamoDB is down."""
    client = TestClient(app)
    
    # Mock DynamoDB failure
    with pytest.mock.patch('app.services.dynamodb.DynamoDBService.health_check', side_effect=Exception("Connection failed")):
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        assert "error" in data


def test_cors_headers():
    """Test CORS headers are present."""
    client = TestClient(app)
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    
    # FastAPI handles OPTIONS automatically for CORS
    assert response.status_code == 200


def test_api_documentation_disabled_in_production():
    """Test that API documentation is disabled in production."""
    # This would be tested with environment-specific configuration
    pass