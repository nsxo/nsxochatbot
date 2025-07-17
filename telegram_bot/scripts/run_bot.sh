#!/bin/bash

# Change to project root directory  
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

# Run the bot using the main entry point
python run.py 