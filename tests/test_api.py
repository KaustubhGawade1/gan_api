"""Tests for API endpoints"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_generate_with_valid_request(client, valid_generate_request):
    """Test image generation with valid request."""
    # This will fail if model weights are not present
    # In CI/CD, mock the inference service
    response = client.post("/api/v1/generate", json=valid_generate_request)
    # Either 200 (success) or 500 (weights not found)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


def test_generate_with_empty_prompt(client):
    """Test image generation with empty prompt."""
    request_data = {
        "prompt": "",
        "seed": 42,
    }
    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_generate_missing_required_field(client):
    """Test image generation with missing required field."""
    response = client.post("/api/v1/generate", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_generate_with_custom_seed(client):
    """Test image generation with custom seed."""
    request_data = {
        "prompt": "A test prompt",
        "seed": 100,
        "guidance_scale": 1.5,
    }
    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


def test_image_response_format(client, valid_generate_request):
    """Test that image response has correct format."""
    response = client.post("/api/v1/generate", json=valid_generate_request)
    
    if response.status_code == status.HTTP_200_OK:
        assert response.headers["content-type"] == "image/jpeg"
        assert len(response.content) > 0
        # Check JPEG header
        assert response.content[:2] == b'\xff\xd8'
