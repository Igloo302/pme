"""Configuration constants for Screen Memory GUI."""

import os

SCREENPIPE_API = "http://localhost:3030"
OPENCHRONICLE_BIN = "/Users/jyshen/.local/bin/openchronicle"
SCREENPIPE_DATA = os.path.expanduser("~/.screenpipe")
OPENCHRONICLE_DATA = os.path.expanduser("~/.openchronicle")
SCREENPIPE_DB = os.path.join(SCREENPIPE_DATA, "db.sqlite")
OPENCHRONICLE_DB = os.path.join(OPENCHRONICLE_DATA, "index.db")
SCREENPIPE_PIPES_DIR = os.path.join(SCREENPIPE_DATA, "pipes")
PORT = 5555
# Dedicated independent config & data directory for screen memory gui
SMGUI_DATA_DIR = "smgui"
os.makedirs(SMGUI_DATA_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(SMGUI_DATA_DIR, "config.yaml")
OUTPUT_DB = os.path.join(SMGUI_DATA_DIR, "memory.db")
SCHEDULE_STATE_PATH = os.path.join(SMGUI_DATA_DIR, "schedule_state.json")
PIPELINE_LOCK_FILE = os.path.join(SMGUI_DATA_DIR, ".pipeline.lock")
