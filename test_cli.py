
import sys
import os
import subprocess
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

OPENAPI_URL = "https://learn.openapis.org/examples/v3.0/api-with-examples.yaml"
MOCK_SERVER = "http://127.0.0.1:4010"

def start_mock_server():
    """Start the mock server in the background."""
    print("Starting mock server...")
    subprocess.Popen(["npx", "@stoplight/prism-cli", "mock", OPENAPI_URL], 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)

if __name__ == "__main__":
    start_mock_server()
    
    print("\n=== Testing listing available commands ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "--spec", OPENAPI_URL])
    
    print("\n=== Testing GET / endpoint with default server ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "--spec", OPENAPI_URL, "listVersionsv2"])
    
    print("\n=== Testing GET /v2 endpoint with server override ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "--spec", OPENAPI_URL, "--server", MOCK_SERVER, "getVersionDetailsv2"])
    
    print("\n=== Testing with JSON output format ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "--spec", OPENAPI_URL, "--server", MOCK_SERVER, "listVersionsv2", "--output", "json"])
    
    print("\nAll tests completed successfully!")
