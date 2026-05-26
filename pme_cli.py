import os
import sys
import argparse
import sqlite3
from flask import Flask

from src.config_loader import get_config
from src.cleaner import PMECleaner
from src.qa_engine import PMEQueryEngine
from gui import register_routes

def print_banner():
    banner = """
======================================================================
  PME (Personal Memory Engine) - Screen Activity Processor & Q&A
======================================================================
    """
    print(banner)

def handle_clean(args):
    print("🚀 Starting PME-OCR Multi-Frequency Data Cleaning...")
    cleaner = PMECleaner()
    cleaner.clean(days=args.days)

def handle_ask(args):
    print(f"🚀 Querying PME Cleaned memories for: '{args.query}'...")
    engine = PMEQueryEngine()
    result = engine.ask(args.query, limit=args.limit, ask_llm=args.ask)
    
    if not result.get("rows"):
        print("No related history captures found in database.")
        return
        
    print(f"\nMatched {len(result['rows'])} related screen frames.")
    print("="*60)
    print("Context Summary:")
    print("="*60)
    for i, row in enumerate(result["rows"]):
        ts, app, title, _, reason, focused = row
        status = "Active" if focused else "Background"
        print(f"  #{i+1} [{ts}] {app} - {title} ({status} | Trigger: {reason})")
    print("="*60)
    
    if not args.ask:
        print("\nGenerated Prompt for LLM (Copy to OpenAI/Claude):")
        print("="*60)
        print(result["prompt"])
        print("="*60)

def handle_status(args):
    config = get_config()
    db_cfg = config.get("database", {})
    
    sp_db = db_cfg.get("screenpipe_db")
    oc_db = db_cfg.get("openchronicle_db")
    pme_db = db_cfg.get("cleaned_db")
    
    print("PME Project Database Status:")
    print("="*60)
    
    for name, path in [("Screenpipe Raw DB", sp_db), ("OpenChronicle DB", oc_db), ("PME Cleaned DB", pme_db)]:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024*1024)
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                if "screenpipe" in path.lower():
                    records = cursor.execute("SELECT count(*) FROM ocr_text").fetchone()[0]
                elif "openchronicle" in path.lower() or "index.db" in path:
                    records = cursor.execute("SELECT count(*) FROM captures").fetchone()[0]
                else:
                    records = cursor.execute("SELECT count(*) FROM cleaned_memories").fetchone()[0]
                conn.close()
            except Exception:
                records = "Unknown"
            print(f"  * {name:20}: {size_mb:8.2f} MB | {records} records")
        else:
            print(f"  * {name:20}: NOT FOUND at {path}")
    print("="*60)

def handle_gui(args):
    print_banner()
    config = get_config()
    gui_cfg = config.get("gui", {})
    host = gui_cfg.get("host", "127.0.0.1")
    port = gui_cfg.get("port", 5555)
    
    print(f"🚀 Starting Screen Memory GUI Console...")
    print(f"Open http://{host}:{port} in your browser to manage recordings.")
    
    app = Flask("screen-memory-gui")
    register_routes(app)
    app.run(host=host, port=port, debug=False)

def main():
    parser = argparse.ArgumentParser(description="PME Behavior Monitor CLI wrapper tool")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")
    
    # 1. Clean command
    parser_clean = subparsers.add_parser("clean", help="Clean and deduplicate Screenpipe data")
    parser_clean.add_argument("--days", type=int, default=3, help="Number of past days to clean (default 3)")
    
    # 2. Ask command
    parser_ask = subparsers.add_parser("ask", help="Query PME memories using FTS5 and LLM RAG")
    parser_ask.add_argument("query", type=str, help="Search query (e.g. 'Aura Project')")
    parser_ask.add_argument("--limit", type=int, default=5, help="Max context entries to retrieve (default 5)")
    parser_ask.add_argument("--ask", action="store_true", help="Submit to LLM and print answer (requires litellm)")
    
    # 3. Status command
    subparsers.add_parser("status", help="Show system database size and records counts")
    
    # 4. GUI command
    subparsers.add_parser("gui", help="Start Web UI administration console")
    
    args = parser.parse_args()
    
    if args.command == "clean":
        handle_clean(args)
    elif args.command == "ask":
        handle_ask(args)
    elif args.command == "status":
        handle_status(args)
    elif args.command == "gui":
        handle_gui(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
