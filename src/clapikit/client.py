
import requests
from typing import Dict, Any, Optional
from .parser import OpenAPISpec

class APIClient:
    """Client for making API requests based on OpenAPI specifications."""
    
    def __init__(self, spec: OpenAPISpec):
        """Initialize the client with an OpenAPI specification."""
        self.spec = spec
        self.base_url = spec.server_url
    
    def request(self, path: str, method: str, **kwargs) -> requests.Response:
        """Make an API request based on the specification."""
        url = self._build_url(path)
        return requests.request(method.upper(), url, **kwargs)
    
    def _build_url(self, path: str) -> str:
        """Build the full URL for a request."""
        base = self.base_url.rstrip('/')
        
        path = path.lstrip('/')
        
        return f"{base}/{path}"
