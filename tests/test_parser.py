
import os
import unittest
from pathlib import Path
from clapikit.parser import OpenAPIParser, OpenAPISpec

class TestOpenAPIParser(unittest.TestCase):
    def setUp(self):
        self.fixture_path = Path(__file__).parent / "fixtures" / "api-with-examples.yaml"
    
    def test_parse_yaml(self):
        parser = OpenAPIParser(self.fixture_path)
        spec = parser.parse()
        
        self.assertIsInstance(spec, OpenAPISpec)
        self.assertEqual(spec.openapi, "3.0.0")
        self.assertEqual(spec.info["title"], "Simple API overview")
        self.assertEqual(spec.info["version"], "2.0.0")
        self.assertIn("/", spec.paths)
        self.assertIn("/v2", spec.paths)
    
    def test_server_url_override(self):
        parser = OpenAPIParser(self.fixture_path)
        spec = parser.parse()
        
        default_url = spec.server_url
        
        new_url = "http://custom-server:8080"
        spec.server_url = new_url
        
        self.assertEqual(spec.server_url, new_url)
        self.assertEqual(spec.servers[0]["url"], new_url)

if __name__ == "__main__":
    unittest.main()
