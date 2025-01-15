#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if filename is provided
if [ -z "$1" ]; then
    echo "Please provide a filename for the job data"
    exit 1
fi

# Create the job data file
echo "Paste the job data JSON and press Ctrl+D when done:"
cat > "job_data/parsed_jobs/$1.json"

# Run the Python script
python job_tracker.py "job_data/parsed_jobs/$1.json"