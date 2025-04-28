
"""Tests for the parser module."""

import pytest
import requests
import yaml
import json
from pathlib import Path
from clapikit.parser import OpenAPIParser, OpenAPISpec

class TestOpenAPIParser:
    """Test the OpenAPIParser class."""
    
    def test_parse_yaml_from_url(self, sample_openapi_url):
        """Test parsing a YAML file from a URL."""
        parser = OpenAPIParser(sample_openapi_url)
        spec = parser.parse()
        
        assert isinstance(spec, OpenAPISpec)
        assert spec.openapi == "3.0.0"
        assert spec.info["title"] == "Simple API overview"
        assert spec.info["version"] == "2.0.0"
        assert "/" in spec.paths
        assert "/v2" in spec.paths
    
    def test_server_url_override(self, sample_openapi_url, mock_server_url):
        """Test overriding the server URL."""
        parser = OpenAPIParser(sample_openapi_url)
        spec = parser.parse()
        
        default_url = spec.server_url
        
        spec.server_url = mock_server_url
        
        assert spec.server_url == mock_server_url
        assert spec.servers[0]["url"] == mock_server_url
    
    def test_invalid_url(self):
        """Test parsing an invalid URL."""
        with pytest.raises(ValueError):
            parser = OpenAPIParser("https://invalid-url-that-does-not-exist.example.com/openapi.yaml")
            parser.parse()
    
    def test_unsupported_format(self, monkeypatch):
        """Test parsing an unsupported format."""
        def mock_get(*args, **kwargs):
            response = requests.Response()
            response.status_code = 200
            response._content = b"This is not JSON or YAML"
            return response
        
        def mock_yaml_load(*args, **kwargs):
            raise yaml.YAMLError("Invalid YAML")
        
        def mock_json_loads(*args, **kwargs):
            raise json.JSONDecodeError("Invalid JSON", "", 0)
        
        monkeypatch.setattr(requests, "get", mock_get)
        monkeypatch.setattr(yaml, "safe_load", mock_yaml_load)
        monkeypatch.setattr(json, "loads", mock_json_loads)
        
        with pytest.raises(ValueError):
            parser = OpenAPIParser("https://example.com/invalid-format")
            parser.parse()
