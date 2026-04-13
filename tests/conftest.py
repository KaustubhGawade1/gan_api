"""Test configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Provide test client for API."""
    return TestClient(app)


@pytest.fixture
def valid_generate_request():
    """Provide valid generate request."""
    return {
        "prompt": "A beautiful sunset over the ocean",
        "seed": 42,
        "guidance_scale": 1.0,
    }


@pytest.fixture
def invalid_generate_request():
    """Provide invalid generate request."""
    return {
        "prompt": "",  # Empty prompt
        "seed": 42,
    }
