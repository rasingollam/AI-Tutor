#!/bin/bash

# Activate virtual environment
source /home/rasi/Documents/Work/Sentinel_Systems/AI-Tutor/venv/bin/activate

# Run the FastAPI server with host set to 0.0.0.0
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
