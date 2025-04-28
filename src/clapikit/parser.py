
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

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
    """Parser for OpenAPI specification files."""
    
    def __init__(self, spec_path: Union[str, Path]):
        """Initialize the parser with a path to the spec file."""
        self.spec_path = Path(spec_path)
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")
    
    def parse(self) -> OpenAPISpec:
        """Parse the OpenAPI specification file."""
        content = self._read_file()
        return OpenAPISpec(**content)
    
    def _read_file(self) -> Dict[str, Any]:
        """Read and parse the specification file based on its extension."""
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
