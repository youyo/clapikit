
import sys
import os
import subprocess

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("=== Testing with default server ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "run", "tests/fixtures/api-with-examples.yaml"])
    
    print("\n=== Testing with server override ===")
    subprocess.run(["python", "-m", "src.clapikit.cli", "run", "tests/fixtures/api-with-examples.yaml", "--server", "http://127.0.0.1:4010"])
