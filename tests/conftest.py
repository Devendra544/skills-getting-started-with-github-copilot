"""Pytest configuration and shared fixtures"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        k: {
            "description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": v["participants"].copy()
        }
        for k, v in activities.items()
    }

    yield

    # Restore original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing"""
    return "teststudent@mergington.edu"


@pytest.fixture
def existing_participant():
    """Provide an email of an existing participant"""
    return "michael@mergington.edu"