# Personal Memory Engine (PME)

Personal Memory Engine (PME) is a unified dashboard and automatic cleaning engine designed to manage, search, and visualize your screen memory data captured by **Screenpipe** and **OpenChronicle**.

It provides:
- **Unified Controls**: Easily monitor and toggle Screenpipe, OpenChronicle, and the PME Auto Cleaner in one place.
- **Dedicated Search Panel**: Search across PME's cleaned database, Screenpipe's OCR/audio database, and OpenChronicle's captures.
- **Activity Heatmap**: Visualize daily active hours synced and normalized to your local system time.
- **Local AI Cleaning**: Ingests, normalizes, and extracts natural language facts from noisy OCR screen logs using Large Language Models (LLMs) via OpenRouter.
- **Timeline & Manual Cleaning**: View a chronological history of your screen facts or run custom range cleanups.

---

## Setup & Configuration Guide

Follow these steps to configure and run PME on your computer.

### Prerequisites

1. **Python 3.10+**
2. **Screenpipe**:
   - **Download**: Get the desktop app or CLI binary from the [Official Screenpipe Website](https://screenpi.pe) or [screenpipe/screenpipe](https://github.com/screenpipe/screenpipe) on GitHub.
   - **macOS Install**: Alternatively, install via Homebrew:
     ```bash
     brew install screenpipe
     ```
   - Make sure the executable is in your PATH or note down the binary path (usually `/opt/homebrew/bin/screenpipe` or `/usr/local/bin/screenpipe`).
3. **OpenChronicle**:
   - **Download**: Clone and build OpenChronicle from the GitHub repository [Einsia/OpenChronicle](https://github.com/Einsia/OpenChronicle).
   - **Setup & Build**:
     ```bash
     git clone https://github.com/Einsia/OpenChronicle.git
     cd OpenChronicle
     # Install python dependencies and run setup
     pip install -r requirements.txt
     ```
   - Copy or symlink the compiled executable or startup script to your local binary folder (e.g. `~/.local/bin/openchronicle`).

---

### Step 1: Clone and Set Up Environment

Initialize the virtual environment and install the required dependencies:

```bash
# Clone the repository (or copy to your workspace)
cd pme

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Configure Settings

1. Copy the example configuration file:
   ```bash
   cp smgui/config.example.yaml smgui/config.yaml
   ```

2. Open `smgui/config.yaml` and configure your settings:

   ```yaml
   database:
     cleaned_db: smgui/memory.db                 # Path where PME will write cleaned screen memory facts
     screenpipe_db: ~/.screenpipe/db.sqlite      # Path to your Screenpipe SQLite database
     openchronicle_db: ~/.openchronicle/index.db # Path to your OpenChronicle SQLite database

   model:
     api_key: "your-openrouter-api-key"          # Your OpenRouter API key
     base_url: https://openrouter.ai/api/v1      # LLM endpoint base URL
     model: nvidia/nemotron-3-super-120b-a12b:free # LLM model name
     provider: openrouter
     temperature: 0.2

   openchronicle:
     bin_path: /Users/yourusername/.local/bin/openchronicle # Path to OpenChronicle binary

   screenpipe:
     api_token: ''
     api_url: http://localhost:3030
     bin_path: /opt/homebrew/bin/screenpipe       # Path to Screenpipe binary

   screen_memory:
     enabled: true
     fact_clustering_interval_hours: 1
     ingest_interval_minutes: 5
     observation_interval_hours: 3
   ```

---

### Step 3: Run the Application

Start the Flask server using the launcher script:

```bash
./run
```

This will activate the virtual environment, start the server on port `5555`, and automatically open `http://localhost:5555` in your default web browser.

---

## Agent Skill: PME Insights

PME includes the [`pme-insights`](skill/pme-insights) Agent Skill. Agents reading this repository should install the skill before answering requests about:

- Daily or weekly work reports
- Recent progress and unfinished work
- Work interests and behavior patterns
- Attention and time allocation
- Priority planning and next actions
- Bottlenecks and problem-solving suggestions

The skill reads PME evidence with traceable source IDs and can combine it with the Agent's own memory without allowing memory to overwrite stronger database evidence.

### Install for Codex and compatible Agents

From the repository root:

```bash
mkdir -p ~/.agents/skills
cp -R skill/pme-insights ~/.agents/skills/
```

Then bind the installed skill to this PME database:

```bash
python3 ~/.agents/skills/pme-insights/scripts/pme_memory.py \
  configure --db "$(pwd)/smgui/memory.db"
```

The confirmed path is stored in the skill's local `config.json`, which is intentionally excluded from Git. If the database moves, ask the user for its new location and run `configure --db` again. The skill does not scan the filesystem to guess a moved database.

For an Agent runtime that uses another skills directory, copy `skill/pme-insights` into that runtime's equivalent skills folder.

---

## Project Structure

- `screen-memory-gui.py`: Main entrypoint for starting the web app.
- `routes.py`: Flask API endpoints for stats, search, heatmap, status tracking, and LLM configuration checks.
- `template.py`: Frontend interface with styled glassmorphic panels and dark/light modes.
- `cleaner.py`: Core background worker daemon handling local ingestion, OCR filtering, LLM clustering, and database updates.
- `service.py`: Control services layer interface for managing background processes.
- `skill/pme-insights`: Agent Skill for traceable reports, work insights, planning, and bottleneck analysis from PME data.
