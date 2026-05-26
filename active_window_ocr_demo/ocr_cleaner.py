import os
import sys
import sqlite3
import argparse
from datetime import datetime, timezone, timedelta

def parse_args():
    parser = argparse.ArgumentParser(description="PME-OCR Data Cleaning and Database Generation Tool")
    parser.add_argument(
        "--screenpipe-db",
        default=os.path.expanduser("~/.screenpipe/db.sqlite"),
        help="Path to the Screenpipe SQLite database"
    )
    parser.add_argument(
        "--openchronicle-db",
        default=os.path.expanduser("~/.openchronicle/index.db"),
        help="Path to the OpenChronicle SQLite database"
    )
    parser.add_argument(
        "--output",
        default=os.path.expanduser("~/Documents/antigravity/wonderful-nobel/active_window_ocr_demo/pme_cleaned_memories.db"),
        help="Path to the output cleaned SQLite database"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Number of past days of data to clean and process"
    )
    return parser.parse_args()

def init_output_db(db_path):
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Overwrite if exists, or connect
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create main table
    cursor.execute("""
    CREATE TABLE cleaned_memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        app_name TEXT,
        window_title TEXT,
        focused INTEGER,
        ocr_text TEXT,
        trigger_reason TEXT,
        raw_frame_id INTEGER
    );
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_memories_timestamp ON cleaned_memories(timestamp);")
    cursor.execute("CREATE INDEX idx_memories_app ON cleaned_memories(app_name);")
    
    # Create FTS5 virtual table
    cursor.execute("""
    CREATE VIRTUAL TABLE cleaned_memories_fts USING fts5(
        id UNINDEXED,
        app_name,
        window_title,
        ocr_text,
        tokenize = 'unicode61 remove_diacritics 2'
    );
    """)
    
    # Create triggers
    cursor.execute("""
    CREATE TRIGGER cleaned_memories_ai AFTER INSERT ON cleaned_memories BEGIN
        INSERT INTO cleaned_memories_fts(id, app_name, window_title, ocr_text)
        VALUES (new.id, new.app_name, new.window_title, new.ocr_text);
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER cleaned_memories_ad AFTER DELETE ON cleaned_memories BEGIN
        DELETE FROM cleaned_memories_fts WHERE id = old.id;
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER cleaned_memories_au AFTER UPDATE ON cleaned_memories BEGIN
        DELETE FROM cleaned_memories_fts WHERE id = old.id;
        INSERT INTO cleaned_memories_fts(id, app_name, window_title, ocr_text)
        VALUES (new.id, new.app_name, new.window_title, new.ocr_text);
    END;
    """)
    
    conn.commit()
    return conn

def load_screenpipe_data(db_path, start_time):
    print(f"Connecting to Screenpipe database at: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query ocr_text and frames
    # Screenpipe timestamps are UTC strings, e.g. 2026-05-26T04:04:38.169845+00:00
    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Loading frames since UTC {start_str}...")
    
    query = """
    SELECT f.timestamp, o.app_name, o.window_name, o.focused, o.text, f.id
    FROM frames f
    JOIN ocr_text o ON o.frame_id = f.id
    WHERE f.timestamp >= ?
    ORDER BY f.timestamp ASC
    """
    
    cursor.execute(query, (start_str,))
    rows = cursor.fetchall()
    print(f"Fetched {len(rows)} raw OCR window records from Screenpipe.")
    conn.close()
    return rows

def load_openchronicle_events(db_path, start_time):
    if not os.path.exists(db_path):
        print(f"OpenChronicle index.db not found at {db_path}. Skipping AXTree event integration.")
        return set()
        
    print(f"Connecting to OpenChronicle database at: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # OpenChronicle timestamps are local time strings with offset, e.g. 2026-05-26T12:08:26+08:00
    # Let's select all captures in the range
    query = "SELECT timestamp, app_name, window_title FROM captures ORDER BY timestamp ASC"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # Parse and convert to rounded UTC seconds
    oc_events = set()
    for row in rows:
        ts_str, app_name, title = row
        try:
            # Parse ISO8601 timestamp (with offset)
            dt = datetime.fromisoformat(ts_str)
            if dt.timestamp() >= start_time.timestamp():
                dt_utc_sec = dt.astimezone(timezone.utc).replace(microsecond=0)
                if app_name:
                    oc_events.add((dt_utc_sec, app_name.strip().lower()))
        except Exception as e:
            # Skip invalid timestamp formats
            continue
            
    print(f"Loaded {len(oc_events)} unique AXTree activity events from OpenChronicle.")
    return oc_events

def run_cleaning_and_sync(sp_rows, oc_events, output_conn):
    print("Initializing PME-OCR scheduling simulation and data cleaning...")
    
    # Group Screenpipe records by rounded UTC second
    timeline = {}
    for row in sp_rows:
        ts_str, app_name, window_name, focused, text, frame_id = row
        try:
            dt = datetime.fromisoformat(ts_str)
            dt_sec = dt.replace(microsecond=0)
            if dt_sec not in timeline:
                timeline[dt_sec] = []
            timeline[dt_sec].append({
                "app": app_name,
                "window": window_name,
                "focused": int(focused),
                "text": text,
                "frame_id": frame_id
            })
        except Exception as e:
            continue
            
    sorted_seconds = sorted(timeline.keys())
    if not sorted_seconds:
        print("No valid timeline records found to clean.")
        return
        
    print(f"Aligned timeline covers {len(sorted_seconds)} active seconds of user activity.")
    
    # Tracking variables for scheduling
    last_ocr_time = {} # dict of dict: last_ocr_time[app][window] = dt
    last_text = {}     # dict of dict: last_text[app][window] = text
    prev_active_windows = set()
    
    # Statistics
    stats = {
        "raw_records": len(sp_rows),
        "cleaned_records": 0,
        "active_high_freq": 0,
        "focus_switch": 0,
        "periodic_bg": 0,
        "dynamic_ax_change": 0,
        "initial": 0,
        "deduplicated": 0
    }
    
    cursor = output_conn.cursor()
    
    for t in sorted_seconds:
        second_records = timeline[t]
        
        # 1. Determine active windows at this second
        current_active = set()
        for r in second_records:
            if r["focused"] == 1:
                current_active.add((r["app"], r["window"]))
                
        # 2. Check if focus switched
        focus_changed = False
        if current_active != prev_active_windows:
            focus_changed = True
            
        # 3. Apply Multi-Frequency scheduling logic to each visible window
        for r in second_records:
            app, window, focused, text, frame_id = r["app"], r["window"], r["focused"], r["text"], r["frame_id"]
            
            # Setup nested tracking structures
            if app not in last_ocr_time:
                last_ocr_time[app] = {}
                last_text[app] = {}
                
            last_t = last_ocr_time[app].get(window)
            prev_txt = last_text[app].get(window)
            
            trigger = None
            
            # Scheduling checks
            if last_t is None:
                trigger = "initial"
            elif focused == 1:
                # Active window high frequency (every 2s)
                if (t - last_t).total_seconds() >= 2:
                    trigger = "active_high_freq"
            else:
                # Focus changed: capture final/initial state
                if focus_changed:
                    trigger = "focus_switch"
                # Dynamic AX change in background (every 10s)
                elif (t, app.lower()) in oc_events and (t - last_t).total_seconds() >= 10:
                    trigger = "dynamic_ax_change"
                # Periodic background update (every 30s)
                elif (t - last_t).total_seconds() >= 30:
                    trigger = "periodic_bg"
                    
            if trigger:
                # Perform deduplication: if text hasn't changed since last recorded snapshot, skip writing
                # But keep the last_ocr_time updated so the scheduling timer progresses
                last_ocr_time[app][window] = t
                
                # Check for actual content changes
                if text == prev_txt:
                    stats["deduplicated"] += 1
                    continue
                    
                # Update text tracking
                last_text[app][window] = text
                
                # Write to the new database
                cursor.execute(
                    """
                    INSERT INTO cleaned_memories 
                    (timestamp, app_name, window_title, focused, ocr_text, trigger_reason, raw_frame_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (t.isoformat(), app, window, focused, text, trigger, frame_id)
                )
                
                stats["cleaned_records"] += 1
                stats[trigger] += 1
                
        prev_active_windows = current_active
        
    output_conn.commit()
    
    print("\n" + "="*50)
    print("DATA CLEANING & RECONSTRUCTION COMPLETE")
    print("="*50)
    print(f"Raw Database OCR entries processed: {stats['raw_records']}")
    print(f"Cleaned Database entries generated: {stats['cleaned_records']}")
    print(f"Deduplicated entries (no content change): {stats['deduplicated']}")
    print(f"Storage compression ratio: {stats['raw_records'] / max(1, stats['cleaned_records']):.2f}x")
    print("\nTrigger Statistics:")
    print(f"  - Initial App Load:            {stats['initial']}")
    print(f"  - Active Window High-Freq:     {stats['active_high_freq']}")
    print(f"  - Focus Switch Immediate:      {stats['focus_switch']}")
    print(f"  - Dynamic Background AX Event: {stats['dynamic_ax_change']}")
    print(f"  - Periodic Background Poll:    {stats['periodic_bg']}")
    print("="*50 + "\n")
    
    return stats

def test_query_capabilities(db_path):
    print("Verifying cleaned database query capabilities...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Total row count
    cursor.execute("SELECT count(*) FROM cleaned_memories")
    count = cursor.fetchone()[0]
    print(f"Verification: Total rows in 'cleaned_memories' table: {count}")
    
    # 2. Get top apps
    cursor.execute("SELECT app_name, count(*) FROM cleaned_memories GROUP BY app_name ORDER BY count(*) DESC LIMIT 5")
    print("Top 5 apps in cleaned database:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} entries")
        
    # 3. Test FTS5 Search
    print("\nTesting FTS5 Full-Text Search:")
    test_keywords = ["Aura", "Antigravity", "Feishu", "项目", "代码", "WeChat"]
    for kw in test_keywords:
        cursor.execute("""
        SELECT cleaned_memories.app_name, cleaned_memories.window_title, snippet(cleaned_memories_fts, 2, '【', '】', '...', 10) 
        FROM cleaned_memories_fts 
        JOIN cleaned_memories ON cleaned_memories.id = cleaned_memories_fts.id 
        WHERE cleaned_memories_fts MATCH ? 
        LIMIT 2
        """, (kw,))
        results = cursor.fetchall()
        print(f"  Keyword '{kw}' matches: {len(results)} rows")
        for r in results:
            print(f"    * App: {r[0]} | Title: {r[1]} | Snippet: {r[2]}")
            
    conn.close()

def main():
    args = parse_args()
    
    # Compute start time
    start_time = datetime.now(timezone.utc) - timedelta(days=args.days)
    
    # Initialize output database
    output_conn = init_output_db(args.output)
    
    # Load inputs
    try:
        sp_rows = load_screenpipe_data(args.screenpipe_db, start_time)
    except Exception as e:
        print(f"Error loading Screenpipe data: {e}")
        sys.exit(1)
        
    try:
        oc_events = load_openchronicle_events(args.openchronicle_db, start_time)
    except Exception as e:
        print(f"Error loading OpenChronicle data: {e}")
        oc_events = set()
        
    # Process
    run_cleaning_and_sync(sp_rows, oc_events, output_conn)
    output_conn.close()
    
    # Verify
    test_query_capabilities(args.output)
    print(f"\nSUCCESS! Cleaned database saved at: {args.output}")

if __name__ == "__main__":
    main()
