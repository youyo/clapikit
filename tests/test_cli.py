"""Tests for the CLI module."""

import pytest
import json
import os
import click
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from clapikit.cli import cli, dynamic_cli, DynamicCLI

class TestCLI:
    """Test the CLI functionality."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create a Click CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_openapi_spec(self):
        """Create a mock OpenAPI specification."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "http://example.com/api"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "listUsers",
                        "summary": "List users"
                    }
                },
                "/users/{id}": {
                    "get": {
                        "operationId": "getUser",
                        "summary": "Get user by ID"
                    }
                }
            }
        }
    
    @pytest.fixture
    def mock_spec_object(self, mock_openapi_spec):
        """Create a mock OpenAPISpec object."""
        mock_spec = MagicMock()
        mock_spec.openapi = mock_openapi_spec["openapi"]
        mock_spec.info = mock_openapi_spec["info"]
        mock_spec.servers = mock_openapi_spec["servers"]
        mock_spec.paths = mock_openapi_spec["paths"]
        mock_spec.server_url = mock_openapi_spec["servers"][0]["url"]
        return mock_spec
    
    def test_list_commands(self, cli_runner, mock_spec_object):
        """Test listing available commands."""
        with cli_runner.isolated_filesystem():
            with open("test.yaml", "w") as f:
                f.write("dummy: content")
            
            with patch("clapikit.parser.OpenAPIParser.parse", return_value=mock_spec_object):
                dynamic_cli.spec = None
                dynamic_cli.client = None
                dynamic_cli.commands = {}
                
                result = cli_runner.invoke(cli, ["--spec", "test.yaml"])
                
                assert result.exit_code == 0
                assert "listUsers" in result.output
                assert "getUser" in result.output
    
    def test_debug_flag(self, cli_runner, mock_spec_object):
        """Test the debug flag."""
        with cli_runner.isolated_filesystem():
            with open("test.yaml", "w") as f:
                f.write("dummy: content")
            
            with patch("clapikit.parser.OpenAPIParser.parse", return_value=mock_spec_object):
                dynamic_cli.spec = None
                dynamic_cli.client = None
                dynamic_cli.commands = {}
                
                result_no_debug = cli_runner.invoke(cli, ["--spec", "test.yaml"])
                
                result_debug = cli_runner.invoke(cli, ["--spec", "test.yaml", "--debug"])
                
                assert "Using server:" not in result_no_debug.output
                assert "Using server:" in result_debug.output
    
    def test_execute_command(self, cli_runner, mock_spec_object):
        """Test executing a command."""
        with cli_runner.isolated_filesystem():
            with open("test.yaml", "w") as f:
                f.write("dummy: content")
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"users": [{"id": 1, "name": "Test User"}]}
            mock_response.headers = {"content-type": "application/json"}
            
            test_cli = DynamicCLI()
            test_cli.spec = mock_spec_object
            test_cli.client = MagicMock()
            test_cli.client.request.return_value = mock_response
            
            test_cli.commands = {
                "listUsers": {
                    "path": "/users",
                    "method": "get",
                    "summary": "List users",
                    "details": {}
                }
            }
            
            with patch("clapikit.parser.OpenAPIParser.parse", return_value=mock_spec_object):
                with patch("clapikit.client.APIClient.request", return_value=mock_response):
                    with patch("clapikit.cli.dynamic_cli", test_cli):
                        result = cli_runner.invoke(cli, ["--spec", "test.yaml", "listUsers"])
                        
                        assert result.exit_code == 0
                        assert "200" in result.output
