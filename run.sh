#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Set PYTHONPATH and run the bot
export PYTHONPATH="$SCRIPT_DIR"
cd "$SCRIPT_DIR"
python -m src.price_tracker_bot.main
