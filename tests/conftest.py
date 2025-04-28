"""Pytest configuration file for clapikit tests."""

import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

@pytest.fixture
def sample_openapi_url():
    """Return a URL to a sample OpenAPI specification."""
    return "https://learn.openapis.org/examples/v3.0/api-with-examples.yaml"

@pytest.fixture
def mock_server_url():
    """Return a URL to a mock server."""
    return "http://127.0.0.1:4010"
