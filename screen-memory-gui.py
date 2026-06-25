#!/usr/bin/env python3
"""
Screen Memory GUI - Unified interface for Screenpipe and OpenChronicle
"""

import sys
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))
print()
from flask import Flask
import webbrowser

from screen_memory.config import PORT

app = Flask(__name__)

from routes import register_routes  # noqa: E402
register_routes(app)

if __name__ == '__main__':
    print("Launching Screen Memory GUI...")
    print(f"Open http://localhost:{PORT} in your browser")
    webbrowser.open(f'http://localhost:{PORT}')
    app.run(port=PORT, debug=False)
