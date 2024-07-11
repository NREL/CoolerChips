#!/bin/bash

# Check if requirements.txt exists and install dependencies
if [ -f /app/requirements.txt ]; then
    pip install --no-cache-dir -r /app/requirements.txt
fi

# Install the application itself if needed
pip install /app/

# Execute the passed command
exec "$@"
