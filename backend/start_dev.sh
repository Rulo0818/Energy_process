#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Verify we're using the correct Python
echo "Using Python: $(which python)"
echo "Using uvicorn: $(which uvicorn)"

# Start uvicorn with reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
