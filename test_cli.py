
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.clapikit.cli import main

if __name__ == "__main__":
    print("=== Testing with default server ===")
    sys.argv = ["clapikit", "run", "tests/fixtures/api-with-examples.yaml"]
    main()
    
    print("\n=== Testing with server override ===")
    sys.argv = ["clapikit", "run", "tests/fixtures/api-with-examples.yaml", "--server", "http://127.0.0.1:4010"]
    main()
