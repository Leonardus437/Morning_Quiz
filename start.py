#!/usr/bin/env python3
import os
import sys

# Get PORT from environment, default to 8000
port = os.getenv("PORT", "8000")

# Start uvicorn
os.system(f"uvicorn main:app --host 0.0.0.0 --port {port}")
