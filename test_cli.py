
import sys
import os
import subprocess

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

OPENAPI_URL = "https://learn.openapis.org/examples/v3.0/api-with-examples.yaml"

if __name__ == "__main__":
    print("=== Testing with default server ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "run", OPENAPI_URL])
    
    print("\n=== Testing with server override ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "run", OPENAPI_URL, "--server", "http://127.0.0.1:4010"])
