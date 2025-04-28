
import os
import yaml
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from urllib.parse import urlparse

class OpenAPISpec(BaseModel):
    """Model representing an OpenAPI specification."""
    openapi: str
    info: Dict[str, Any]
    paths: Dict[str, Dict[str, Any]]
    servers: Optional[List[Dict[str, Any]]] = []
    
    @property
    def server_url(self) -> str:
        """Get the default server URL from the spec."""
        if self.servers and len(self.servers) > 0:
            return self.servers[0].get('url', 'http://localhost')
        return 'http://localhost'
    
    @server_url.setter
    def server_url(self, url: str):
        """Set the server URL, overriding the spec."""
        if not self.servers:
            self.servers = [{'url': url}]
        else:
            self.servers[0]['url'] = url

class OpenAPIParser:
    """Parser for OpenAPI specification files or URLs."""
    
    def __init__(self, spec_path_or_url: Union[str, Path]):
        """Initialize the parser with a path to the spec file or URL."""
        self.spec_path_or_url = str(spec_path_or_url)
        self.is_url = self._is_url(self.spec_path_or_url)
        
        if not self.is_url:
            self.spec_path = Path(spec_path_or_url)
            if not self.spec_path.exists():
                raise FileNotFoundError(f"Specification file not found: {spec_path_or_url}")
    
    def parse(self) -> OpenAPISpec:
        """Parse the OpenAPI specification file or URL."""
        content = self._read_content()
        return OpenAPISpec(**content)
    
    def _is_url(self, path_or_url: str) -> bool:
        """Check if the given string is a URL."""
        parsed = urlparse(path_or_url)
        return parsed.scheme in ('http', 'https')
    
    def _read_content(self) -> Dict[str, Any]:
        """Read and parse the specification from file or URL."""
        if self.is_url:
            return self._fetch_from_url()
        else:
            return self._read_from_file()
    
    def _fetch_from_url(self) -> Dict[str, Any]:
        """Fetch and parse the specification from a URL."""
        try:
            response = requests.get(self.spec_path_or_url)
            response.raise_for_status()
            content = response.text
            
            if self.spec_path_or_url.endswith('.json'):
                return json.loads(content)
            elif self.spec_path_or_url.endswith(('.yaml', '.yml')):
                return yaml.safe_load(content)
            else:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    try:
                        return yaml.safe_load(content)
                    except yaml.YAMLError:
                        raise ValueError(f"Unsupported content format from URL: {self.spec_path_or_url}")
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch specification from URL: {self.spec_path_or_url}. Error: {str(e)}")
    
    def _read_from_file(self) -> Dict[str, Any]:
        """Read and parse the specification from a file."""
        file_ext = self.spec_path.suffix.lower()
        
        with open(self.spec_path, 'r') as f:
            if file_ext in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif file_ext == '.json':
                return json.load(f)
            else:
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    try:
                        return yaml.safe_load(content)
                    except yaml.YAMLError:
                        raise ValueError(f"Unsupported file format: {file_ext}")
