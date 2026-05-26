# PME — Personal Memory Engine

> **An exploratory post-processor that fuses screen recording data from two open-source tools to build a high-signal, low-noise personal memory database.**

---

## The Problem

Most "screen recorder" tools either:

- **Record too much** — every frame, every pixel change, hundreds of millions of tokens of raw OCR noise. You can't feed that to an LLM.
- **Record too little** — event-driven snapshots miss what's happening in background windows entirely.

When you want to answer a question like *"What exactly was I working on between 10 AM and noon last Tuesday?"*, neither approach gives you a usable answer.

---

## What This Project Explores

PME is **not** a finished product. It's a research spike exploring one hypothesis:

> **The combination of screen-level OCR (Screenpipe) + accessibility-tree events (OpenChronicle) contains enough signal to reconstruct a high-fidelity personal work log — if you apply the right post-processing filter.**

The key insight is that these two data sources are complementary:

| Source | Strengths | Weaknesses |
|--------|-----------|------------|
| **Screenpipe** | Captures text on every window (OCR), even background | Periodic — 2 s per frame, massive redundancy |
| **OpenChronicle** | Event-driven AX tree — fires *only* when something changes | Misses windows it can't inspect via accessibility |

PME fuses them with a **multi-frequency state machine**:

```
Active window focused  →  sample every 2s  (high-freq OCR)
Focus switch detected  →  sample immediately  (transition capture)
Background AX change   →  sample within 10s  (dynamic bg capture)
Silent background      →  sample every 30s  (low-freq heartbeat)
Content unchanged      →  skip entirely  (deduplication)
No OC data in window   →  discard bucket  (incomplete data filter)
```

**Result in testing (2-hour session):**

| Metric | Raw Screenpipe | PME Cleaned |
|--------|---------------|-------------|
| Total characters | ~3,950,000 (token overflow) | ~610,000 |
| Background coverage | Partial | Complete |
| Compression ratio | 1× | **~9×** |
| LLM-ready? | ❌ Too large | ✅ Yes |

The cleaned output is a SQLite database with FTS5 full-text search, ready to use as a RAG context for any LLM.

---

## Architecture

```
wonderful-nobel/
├── pme_cli.py            # CLI entry point: clean / ask / status / gui
├── config.yaml           # All paths and policy settings live here
├── setup.sh              # One-command environment setup
├── requirements.txt      # Python dependencies
│
├── src/
│   ├── cleaner.py        # Core engine: state machine, dedup, bucket filter
│   ├── qa_engine.py      # FTS5 retrieval + LLM prompt builder (litellm)
│   └── config_loader.py  # YAML config loader with ~ expansion + token auto-read
│
└── gui/
    ├── routes.py         # Flask API routes (control panel + search + auto-cleaner)
    └── template.py       # Single-page Web UI (dark/light mode, i18n)
```

The Web UI gives you:
- **Dashboard** — one-click start/stop for both recording tools, 30-day activity heatmap, auto-cleaner status
- **Search** — search across Screenpipe raw OCR, OpenChronicle captures, and PME cleaned memories
- **Timeline** — browse events by day
- **Statistics** — database sizes and record counts
- **PME Engine** — trigger full cleans, download the output DB
- **Settings** — edit all config fields without touching YAML

---

## Prerequisites

PME sits **on top of** two existing tools. You need both running to collect data.

### 1. Screenpipe

Screenpipe records your screen continuously and stores OCR text in a local SQLite database.

> **Note:** The Screenpipe repo has moved from `mediar-ai/screenpipe` to its own org.  
> See: https://github.com/screenpipe-org/screenpipe

**Option A — Desktop App (easiest):**

Download the macOS `.dmg` installer from **[screenpi.pe](https://screenpi.pe)**, install it, and follow the on-screen setup.

**Option B — CLI via Homebrew:**
```bash
brew install screenpipe
```

**Option C — CLI quick-install script:**
```bash
curl -fsSL get.screenpi.pe/cli | sh
```

**macOS permissions:**  
On first run, grant **Screen Recording** and **Microphone** access in **System Settings → Privacy & Security**.

**Start recording (CLI):**
```bash
screenpipe record
```

Screenpipe's database is typically at `~/.screenpipe/db.sqlite`.

---

### 2. OpenChronicle

OpenChronicle captures macOS accessibility tree events — when windows change, apps switch, text is typed — and stores them in a local SQLite database.

**Install:**
```bash
# Download the latest binary from GitHub releases
curl -L https://github.com/openchronicle/openchronicle/releases/latest/download/openchronicle-macos -o ~/.local/bin/openchronicle
chmod +x ~/.local/bin/openchronicle
```

Or see: https://github.com/openchronicle/openchronicle

**Grant accessibility permissions:**  
Go to **System Settings → Privacy & Security → Accessibility** and enable OpenChronicle.

**Start recording:**
```bash
openchronicle start
```

OpenChronicle's database is typically at `~/.openchronicle/index.db`.

---

### 3. Python 3.8+

```bash
# Check if you have it
python3 --version

# macOS — install via Homebrew if needed
brew install python
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/pme.git
cd pme

# Run the one-command setup (creates .venv and installs dependencies)
./setup.sh
```

Then edit `config.yaml` to match your local paths:

```yaml
database:
  screenpipe_db: "~/.screenpipe/db.sqlite"      # adjust if different
  openchronicle_db: "~/.openchronicle/index.db" # adjust if different
  cleaned_db: "~/pme_cleaned_memories.db"        # where to write output

screenpipe:
  api_url: "http://localhost:3030"
  bin_path: "/opt/homebrew/bin/screenpipe"       # `which screenpipe`
  api_token: ""                                   # auto-detected if blank

openchronicle:
  bin_path: "~/.local/bin/openchronicle"         # `which openchronicle`
```

---

## Usage

### Start the Web Control Panel

```bash
source .venv/bin/activate
python pme_cli.py gui
```

Open **http://127.0.0.1:5555** in your browser.

From there you can start/stop recording tools, browse the heatmap, search memories, and trigger cleans — all without the terminal.

---

### Run a Manual Clean (CLI)

```bash
source .venv/bin/activate

# Clean the last 3 days (default)
python pme_cli.py clean

# Clean a specific range
python pme_cli.py clean --days 7

# Clean a specific time window
python pme_cli.py clean --start "2024-05-20T10:00:00" --end "2024-05-20T12:00:00"
```

The cleaned database is written to `cleaned_db` in your `config.yaml`.

---

### Query Your Memories

```bash
# Pull up context and print a prompt you can paste into any LLM
python pme_cli.py ask "Aura project"

# Let PME call an LLM directly (needs an API key in your environment)
export OPENAI_API_KEY="sk-..."
# or: export DEEPSEEK_API_KEY="..."

python pme_cli.py ask "What was I working on last Tuesday morning?" --ask
```

---

### Check Database Status

```bash
python pme_cli.py status
```

Shows record counts and file sizes for all three databases.

---

## Auto-Cleaner

When both Screenpipe and OpenChronicle are running, PME's background thread automatically runs an **incremental clean every 5 minutes** — appending new data without ever wiping existing records.

You can watch it live on the Dashboard's **PME Auto-Cleaner** card.

---

## How the Cleaning Works (Technical Detail)

1. **Load** OCR frames from Screenpipe for the target time window.
2. **Load** AX tree events from OpenChronicle for the same window.
3. **Bucket filter** — split time into 10-minute buckets. Discard any Screenpipe bucket that has zero matching OpenChronicle events (likely a recording gap where only one tool was running — incomplete data).
4. **State machine simulation** — iterate through remaining frames second by second, deciding whether to keep each record based on:
   - Is this window currently focused? → high-freq rule (2s)
   - Did focus just switch? → immediate snapshot
   - Did OpenChronicle fire an AX event for this background window? → dynamic rule (10s)
   - Otherwise → low-freq rule (30s)
5. **Content dedup** — if the OCR text hasn't changed since the last stored record for this window, skip it.
6. **Write** kept records to `cleaned_memories` table with FTS5 triggers for fast full-text search.

---

## Limitations & Future Work

- **macOS only** — both Screenpipe and OpenChronicle are macOS-first. Linux support would require alternative sensor tools.
- **Two tools required** — if either tool is offline, a whole time bucket is discarded. This is intentional (incomplete data = unreliable signal), but means gaps in recording are gaps in memory.
- **No audio** — this version focuses on screen text. Screenpipe captures audio transcripts too; wiring those in is a natural next step.
- **No LLM summarization** — the current RAG just retrieves raw OCR text. Summarizing it per-session or per-day would make results much more readable.
- **Refactoring** — this is an exploration. Once the approach is validated, the architecture would be simplified significantly.

---

## Contributing

This is a personal research project. PRs welcome, but expect rough edges.

---

## License

MIT
