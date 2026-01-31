#!/bin/bash
# Render deployment script - no virtual environment needed on Render

echo "🚀 Starting Price Tracker Bot on Render..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH and run the bot
export PYTHONPATH="$SCRIPT_DIR"
cd "$SCRIPT_DIR"

echo "🤖 Starting bot (tables will be auto-created)..."
python -m src.price_tracker_bot.main
