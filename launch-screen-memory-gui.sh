#!/bin/bash
# Screen Memory GUI Launcher

echo "🚀 Launching Screen Memory GUI..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 screen-memory-gui.py
