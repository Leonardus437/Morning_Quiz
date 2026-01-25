#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads/chat
mkdir -p uploads/schedules

# Start the application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}