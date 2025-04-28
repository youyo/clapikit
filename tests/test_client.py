"""Tests for the client module."""

import pytest
import requests
from unittest.mock import MagicMock, patch
from clapikit.client import APIClient
from clapikit.parser import OpenAPISpec

class TestAPIClient:
    """Test the APIClient class."""
    
    @pytest.fixture
    def mock_spec(self):
        """Create a mock OpenAPI specification."""
        spec = MagicMock(spec=OpenAPISpec)
        spec.server_url = "http://example.com/api"
        return spec
    
    def test_init(self, mock_spec):
        """Test initializing the client."""
        client = APIClient(mock_spec)
        assert client.spec == mock_spec
        assert client.base_url == mock_spec.server_url
    
    def test_build_url(self, mock_spec):
        """Test building a URL."""
        client = APIClient(mock_spec)
        
        client.base_url = "http://example.com/api/"
        assert client._build_url("users") == "http://example.com/api/users"
        
        assert client._build_url("/users") == "http://example.com/api/users"
        
        assert client._build_url("/users/") == "http://example.com/api/users/"
    
    @patch("requests.request")
    def test_request(self, mock_request, mock_spec):
        """Test making a request."""
        client = APIClient(mock_spec)
        
        mock_response = MagicMock()
        mock_request.return_value = mock_response
        
        response = client.request("users", "GET", params={"role": "admin"})
        
        mock_request.assert_called_once_with(
            "GET", 
            "http://example.com/api/users", 
            params={"role": "admin"}
        )
        
        assert response == mock_response
