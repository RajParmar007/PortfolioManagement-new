#!/usr/bin/env python3
"""
Simple script to start the FastAPI backend server
"""

import subprocess
import sys
import os

def main():
    # Check if we're in the right directory
    if not os.path.exists('fastapi_backend.py'):
        print("Error: fastapi_backend.py not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Check if required packages are installed
    try:
        import fastapi
        import uvicorn
        print("✓ FastAPI dependencies found")
    except ImportError as e:
        print(f"Error: Missing dependencies. Please install: pip install -r fastapi_requirements.txt")
        print(f"Missing: {e}")
        sys.exit(1)
    
    # Start the server
    print("Starting FastAPI backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "fastapi_backend.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
