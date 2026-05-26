import os
import sqlite3
from datetime import datetime, timezone

def get_db_paths():
    return {
        "screenpipe": os.path.expanduser("~/.screenpipe/db.sqlite"),
        "openchronicle": os.path.expanduser("~/.openchronicle/index.db"),
        "cleaned": os.path.expanduser("~/Documents/antigravity/wonderful-nobel/active_window_ocr_demo/pme_cleaned_memories.db")
    }

def analyze_screenpipe(db_path, start_utc, end_utc):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query all frames & OCR in the time range
    query = """
    SELECT f.timestamp, o.app_name, o.window_name, o.focused, o.text
    FROM frames f
    JOIN ocr_text o ON o.frame_id = f.id
    WHERE f.timestamp >= ? AND f.timestamp <= ?
    ORDER BY f.timestamp ASC
    """
    cursor.execute(query, (start_utc, end_utc))
    rows = cursor.fetchall()
    conn.close()
    
    # Analyze
    total_records = len(rows)
    apps = set()
    total_chars = 0
    focused_records = 0
    unique_texts = set()
    
    text_timeline = []
    for r in rows:
        ts, app, window, focused, text = r
        apps.add(app)
        total_chars += len(text)
        if focused:
            focused_records += 1
        if text.strip():
            unique_texts.add(text.strip())
            
        clean_text_short = "  ".join([line.strip() for line in text.split("\n") if line.strip()][:5])
        if len(text.split("\n")) > 5:
            clean_text_short += "..."
        text_timeline.append(f"[{ts}] App: {app} | Title: {window} | Focused: {focused}\n内容: {clean_text_short}")
        
    return {
        "total_records": total_records,
        "apps": sorted(list(apps)),
        "total_chars": total_chars,
        "focused_records": focused_records,
        "unique_texts_count": len(unique_texts),
        "timeline": text_timeline
    }

def analyze_openchronicle(db_path, start_local, end_local):
    if not os.path.exists(db_path):
        return {"total_records": 0, "apps": [], "total_chars": 0, "timeline": []}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT timestamp, app_name, window_title, visible_text
    FROM captures
    WHERE timestamp >= ? AND timestamp <= ?
    ORDER BY timestamp ASC
    """
    cursor.execute(query, (start_local, end_local))
    rows = cursor.fetchall()
    conn.close()
    
    total_records = len(rows)
    apps = set()
    total_chars = 0
    text_timeline = []
    for r in rows:
        ts, app, title, text = r
        if app:
            apps.add(app)
        if text:
            total_chars += len(text)
            
        clean_text_short = "  ".join([line.strip() for line in (text or "").split("\n") if line.strip()][:5])
        if text and len(text.split("\n")) > 5:
            clean_text_short += "..."
        text_timeline.append(f"[{ts}] App: {app} | Title: {title}\n内容: {clean_text_short}")
        
    return {
        "total_records": total_records,
        "apps": sorted(list(apps)),
        "total_chars": total_chars,
        "timeline": text_timeline
    }

def analyze_cleaned(db_path, start_utc, end_utc):
    if not os.path.exists(db_path):
        return {"total_records": 0, "apps": [], "total_chars": 0, "timeline": []}
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT timestamp, app_name, window_title, focused, ocr_text, trigger_reason
    FROM cleaned_memories
    WHERE timestamp >= ? AND timestamp <= ?
    ORDER BY timestamp ASC
    """
    cursor.execute(query, (start_utc, end_utc))
    rows = cursor.fetchall()
    conn.close()
    
    total_records = len(rows)
    apps = set()
    total_chars = 0
    text_timeline = []
    for r in rows:
        ts, app, title, focused, text, reason = r
        apps.add(app)
        total_chars += len(text)
        
        clean_text_short = "  ".join([line.strip() for line in text.split("\n") if line.strip()][:5])
        if len(text.split("\n")) > 5:
            clean_text_short += "..."
        text_timeline.append(f"[{ts}] App: {app} | Title: {title} | Focused: {focused} | Trigger: {reason}\n内容: {clean_text_short}")
        
    return {
        "total_records": total_records,
        "apps": sorted(list(apps)),
        "total_chars": total_chars,
        "timeline": text_timeline
    }

def main():
    paths = get_db_paths()
    
    # 5/20 10:00 - 12:00 in UTC+8
    # Local timestamp format: 2026-05-20T10:00:00+08:00
    # UTC timestamp format: 2026-05-20T02:00:00
    start_utc = "2026-05-20T02:00:00"
    end_utc = "2026-05-20T04:00:00"
    
    start_local = "2026-05-20T10:00:00+08:00"
    end_local = "2026-05-20T12:00:00+08:00"
    
    print("="*60)
    print("DATABASE ANALYSIS FOR 2026-05-20 10:00 - 12:00 (UTC+8)")
    print("="*60)
    
    sp_res = analyze_screenpipe(paths["screenpipe"], start_utc, end_utc)
    print("\n[1] Screenpipe Raw Database:")
    print(f"  - Total OCR records: {sp_res['total_records']}")
    print(f"  - Focused (active) window records: {sp_res['focused_records']}")
    print(f"  - Total text characters: {sp_res['total_chars']}")
    print(f"  - Unique texts count (deduped): {sp_res['unique_texts_count']}")
    print(f"  - Active Apps ({len(sp_res['apps'])}): {', '.join(sp_res['apps'])}")
    
    oc_res = analyze_openchronicle(paths["openchronicle"], start_local, end_local)
    print("\n[2] OpenChronicle Database:")
    print(f"  - Total capture events: {oc_res['total_records']}")
    print(f"  - Total text characters: {oc_res['total_chars']}")
    print(f"  - Active Apps ({len(oc_res['apps'])}): {', '.join(oc_res['apps'])}")
    
    cl_res = analyze_cleaned(paths["cleaned"], start_utc, end_utc)
    print("\n[3] PME Cleaned Database (Our Cleaner):")
    print(f"  - Total stored records: {cl_res['total_records']}")
    print(f"  - Total text characters: {cl_res['total_chars']}")
    print(f"  - Active Apps ({len(cl_res['apps'])}): {', '.join(cl_res['apps'])}")
    print(f"  - Compression Ratio vs Raw: {sp_res['total_records'] / max(1, cl_res['total_records']):.2f}x (records), {sp_res['total_chars'] / max(1, cl_res['total_chars']):.2f}x (chars)")
    
    print("\n" + "="*60)
    print("TIMELINE SAMPLES FOR PROMPT COMPARISON")
    print("="*60)
    
    print("\n--- [Screenpipe Prompt Sample (Top 5 items)] ---")
    for item in sp_res["timeline"][:5]:
        print(item)
        print("-" * 30)
    if len(sp_res["timeline"]) > 5:
        print(f"... and {len(sp_res['timeline']) - 5} more records")
        
    print("\n--- [OpenChronicle Prompt Sample (Top 5 items)] ---")
    for item in oc_res["timeline"][:5]:
        print(item)
        print("-" * 30)
    if len(oc_res["timeline"]) > 5:
        print(f"... and {len(oc_res['timeline']) - 5} more records")
        
    print("\n--- [Cleaned Memories Prompt Sample (Top 5 items)] ---")
    for item in cl_res["timeline"][:5]:
        print(item)
        print("-" * 30)
    if len(cl_res["timeline"]) > 5:
        print(f"... and {len(cl_res['timeline']) - 5} more records")

if __name__ == "__main__":
    main()
