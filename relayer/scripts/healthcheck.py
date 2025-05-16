#!/usr/bin/env python3
"""
Simple health check script for the relayer.
Returns exit code 0 if the relayer is healthy, non-zero otherwise.
"""
import sys
import os
import requests
from urllib.parse import urljoin

def check_health():
    """Check if the relayer API is healthy"""
    host = os.environ.get("HOST", "localhost")
    port = os.environ.get("PORT", "8000")
    
    base_url = f"http://{host}:{port}"
    health_url = urljoin(base_url, "/")
    
    try:
        response = requests.get(health_url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "Relayer is running":
            print("Health check successful")
            return True
        else:
            print(f"Unexpected response: {data}")
            return False
    except requests.RequestException as e:
        print(f"Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1) 