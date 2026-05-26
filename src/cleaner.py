import os
import sqlite3
from datetime import datetime, timezone, timedelta
from src.config_loader import get_config

class PMECleaner:
    def __init__(self):
        self.config = get_config()
        self.db_cfg = self.config.get("database", {})
        self.policy_cfg = self.config.get("cleaning_policy", {})
        
        self.screenpipe_db = self.db_cfg.get("screenpipe_db")
        self.openchronicle_db = self.db_cfg.get("openchronicle_db")
        self.cleaned_db = self.db_cfg.get("cleaned_db")
        
        # Policy thresholds
        self.active_interval = self.policy_cfg.get("active_interval", 2)
        self.bg_interval = self.policy_cfg.get("bg_interval", 30)
        self.ax_trigger_interval = self.policy_cfg.get("ax_trigger_interval", 10)

    def _create_schema(self, conn):
        """Create tables, indexes, FTS and triggers if they don't exist."""
        cursor = conn.cursor()
        
        # Main table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cleaned_memories (
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
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON cleaned_memories(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_app ON cleaned_memories(app_name);")
        
        # FTS5 Table — check existence first since FTS5 doesn't support IF NOT EXISTS
        fts_exists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cleaned_memories_fts'"
        ).fetchone()
        if not fts_exists:
            cursor.execute("""
            CREATE VIRTUAL TABLE cleaned_memories_fts USING fts5(
                id UNINDEXED,
                app_name,
                window_title,
                ocr_text,
                tokenize = 'unicode61 remove_diacritics 2'
            );
            """)
        
        # Triggers — use IF NOT EXISTS workaround (check sqlite_master)
        trigger_exists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' AND name='cleaned_memories_ai'"
        ).fetchone()
        if not trigger_exists:
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

    def init_cleaned_db(self):
        """Full reset: delete existing DB and create fresh schema. Used by manual clean."""
        os.makedirs(os.path.dirname(self.cleaned_db), exist_ok=True)
        
        if os.path.exists(self.cleaned_db):
            os.remove(self.cleaned_db)
            
        conn = sqlite3.connect(self.cleaned_db)
        self._create_schema(conn)
        return conn

    def ensure_cleaned_db(self):
        """Incremental: create DB/tables only if they don't exist. Used by auto-cleaner."""
        os.makedirs(os.path.dirname(self.cleaned_db), exist_ok=True)
        conn = sqlite3.connect(self.cleaned_db)
        self._create_schema(conn)
        return conn

    def load_screenpipe_data(self, start_time, end_time=None):
        print(f"Connecting to Screenpipe database: {self.screenpipe_db}...")
        conn = sqlite3.connect(self.screenpipe_db)
        cursor = conn.cursor()
        
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        if end_time:
            end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
            print(f"Fetching raw OCR between {start_str} and {end_str} UTC...")
            query = """
            SELECT f.timestamp, o.app_name, o.window_name, o.focused, o.text, f.id
            FROM frames f
            JOIN ocr_text o ON o.frame_id = f.id
            WHERE f.timestamp >= ? AND f.timestamp <= ?
            ORDER BY f.timestamp ASC
            """
            cursor.execute(query, (start_str, end_str))
        else:
            print(f"Fetching raw OCR since {start_str} UTC...")
            query = """
            SELECT f.timestamp, o.app_name, o.window_name, o.focused, o.text, f.id
            FROM frames f
            JOIN ocr_text o ON o.frame_id = f.id
            WHERE f.timestamp >= ?
            ORDER BY f.timestamp ASC
            """
            cursor.execute(query, (start_str,))
            
        rows = cursor.fetchall()
        conn.close()
        print(f"Fetched {len(rows)} raw OCR entries.")
        return rows

    def load_openchronicle_events(self, start_time, end_time=None):
        if not os.path.exists(self.openchronicle_db):
            print(f"OpenChronicle database not found at {self.openchronicle_db}. Skipping AXTree dynamics.")
            return set()
            
        print(f"Connecting to OpenChronicle database: {self.openchronicle_db}...")
        conn = sqlite3.connect(self.openchronicle_db)
        cursor = conn.cursor()
        
        query = "SELECT timestamp, app_name FROM captures ORDER BY timestamp ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        oc_events = set()
        for row in rows:
            ts_str, app_name = row
            try:
                dt = datetime.fromisoformat(ts_str)
                dt_utc = dt.astimezone(timezone.utc)
                if dt_utc.timestamp() >= start_time.timestamp():
                    if end_time is None or dt_utc.timestamp() <= end_time.timestamp():
                        dt_utc_sec = dt_utc.replace(microsecond=0)
                        if app_name:
                            oc_events.add((dt_utc_sec, app_name.strip().lower()))
            except Exception:
                continue
                
        print(f"Loaded {len(oc_events)} OpenChronicle events.")
        return oc_events

    def process_cleaning(self, sp_rows, oc_events, output_conn):
        print("Running scheduling simulation & deduplication...")
        
        # Align timeline
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
            except Exception:
                continue
                
        sorted_seconds = sorted(timeline.keys())
        if not sorted_seconds:
            print("No aligned records to clean.")
            return {}
            
        last_ocr_time = {}
        last_text = {}
        prev_active_windows = set()
        
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
            current_active = set()
            for r in second_records:
                if r["focused"] == 1:
                    current_active.add((r["app"], r["window"]))
                    
            focus_changed = (current_active != prev_active_windows)
            
            for r in second_records:
                app, window, focused, text, frame_id = r["app"], r["window"], r["focused"], r["text"], r["frame_id"]
                
                if app not in last_ocr_time:
                    last_ocr_time[app] = {}
                    last_text[app] = {}
                    
                last_t = last_ocr_time[app].get(window)
                prev_txt = last_text[app].get(window)
                
                trigger = None
                
                if last_t is None:
                    trigger = "initial"
                elif focused == 1:
                    if (t - last_t).total_seconds() >= self.active_interval:
                        trigger = "active_high_freq"
                else:
                    if focus_changed:
                        trigger = "focus_switch"
                    elif (t, app.lower()) in oc_events and (t - last_t).total_seconds() >= self.ax_trigger_interval:
                        trigger = "dynamic_ax_change"
                    elif (t - last_t).total_seconds() >= self.bg_interval:
                        trigger = "periodic_bg"
                        
                if trigger:
                    last_ocr_time[app][window] = t
                    if text == prev_txt:
                        stats["deduplicated"] += 1
                        continue
                        
                    last_text[app][window] = text
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
        return stats

    def filter_incomplete_data(self, sp_rows, oc_events, start_time, end_time, bucket_minutes=10):
        # Create buckets of bucket_minutes (e.g. 10 minutes)
        bucket_size = timedelta(minutes=bucket_minutes)
        
        # OpenChronicle events buckets
        oc_buckets = set()
        for t_utc_sec, app_name in oc_events:
            delta = t_utc_sec - start_time
            bucket_idx = int(delta.total_seconds() // (bucket_minutes * 60))
            oc_buckets.add(bucket_idx)
            
        # Group Screenpipe rows by bucket
        sp_buckets = {}
        for row in sp_rows:
            ts_str = row[0]
            try:
                # Remove Z and parse timezone
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                dt_utc = dt.astimezone(timezone.utc)
                delta = dt_utc - start_time
                bucket_idx = int(delta.total_seconds() // (bucket_minutes * 60))
                if bucket_idx not in sp_buckets:
                    sp_buckets[bucket_idx] = []
                sp_buckets[bucket_idx].append(row)
            except Exception:
                continue
                
        # Rebuild filtered sp_rows
        filtered_sp_rows = []
        discarded_count = 0
        
        # Loop through buckets having Screenpipe data
        for bucket_idx, rows in sorted(sp_buckets.items()):
            if bucket_idx in oc_buckets:
                # Both databases have data in this 10-minute interval
                filtered_sp_rows.extend(rows)
            else:
                # Incomplete data: Screenpipe has data, but OpenChronicle has 0 events
                discarded_count += len(rows)
                
        print(f"Filter incomplete data (10-minute buckets): kept {len(filtered_sp_rows)} rows, discarded {discarded_count} rows.")
        return filtered_sp_rows, discarded_count

    def clean(self, start_time_str=None, end_time_str=None, days=3, incremental=False, output_path=None):
        """
        Clean and merge screen data from Screenpipe and OpenChronicle.
        
        Args:
            incremental: If True, use ensure_cleaned_db() to preserve existing data.
                         If False, use init_cleaned_db() for a full reset.
            output_path: If provided (and not incremental), override self.cleaned_db
                         to write the full-reset DB to a custom location.
        """
        # For full-reset mode with custom output path, temporarily override cleaned_db
        original_cleaned_db = self.cleaned_db
        if output_path and not incremental:
            self.cleaned_db = os.path.expanduser(output_path)

        # Parse start and end times
        if start_time_str:
            dt_start = datetime.fromisoformat(start_time_str)
            if dt_start.tzinfo is None:
                dt_start = dt_start.astimezone(timezone.utc)
            start_time = dt_start
        else:
            start_time = datetime.now(timezone.utc) - timedelta(days=days)
            
        if end_time_str:
            dt_end = datetime.fromisoformat(end_time_str)
            if dt_end.tzinfo is None:
                dt_end = dt_end.astimezone(timezone.utc)
            end_time = dt_end
        else:
            end_time = datetime.now(timezone.utc)
            
        # Create or open output DB
        if incremental:
            output_conn = self.ensure_cleaned_db()
        else:
            output_conn = self.init_cleaned_db()
        
        try:
            sp_rows = self.load_screenpipe_data(start_time, end_time)
        except Exception as e:
            print(f"Error reading Screenpipe: {e}")
            output_conn.close()
            return None
            
        try:
            oc_events = self.load_openchronicle_events(start_time, end_time)
        except Exception as e:
            print(f"Error reading OpenChronicle: {e}")
            oc_events = set()
            
        # Filter out intervals with incomplete data
        sp_rows, discarded_count = self.filter_incomplete_data(sp_rows, oc_events, start_time, end_time)
        
        # Delete existing records in this time range to avoid duplicates
        try:
            cursor = output_conn.cursor()
            cursor.execute(
                "DELETE FROM cleaned_memories WHERE timestamp >= ? AND timestamp <= ?",
                (start_time.isoformat(), end_time.isoformat())
            )
            output_conn.commit()
        except Exception as e:
            print(f"Error removing old records: {e}")
        
        # Clean
        stats = self.process_cleaning(sp_rows, oc_events, output_conn)
        output_conn.close()
        
        # Record the actual output path used
        stats["output_path"] = self.cleaned_db
        
        # Restore original cleaned_db path (in case it was overridden)
        self.cleaned_db = original_cleaned_db
        
        # Add discarded count to stats
        stats["discarded_incomplete_records"] = discarded_count
        
        print("\n" + "="*50)
        mode_label = "INCREMENTAL" if incremental else "FULL RESET"
        print(f"DATA PROCESSOR CLEANING STATS ({mode_label})")
        print("="*50)
        print(f"Output Path: {stats.get('output_path', 'N/A')}")
        print(f"Raw Records: {stats.get('raw_records', 0)}")
        print(f"Discarded Incomplete Records: {stats.get('discarded_incomplete_records', 0)}")
        print(f"Cleaned Records: {stats.get('cleaned_records', 0)}")
        print(f"Deduplicated (Skipped): {stats.get('deduplicated', 0)}")
        print(f"Compression Ratio: {stats.get('raw_records', 0) / max(1, stats.get('cleaned_records', 0)):.2f}x")
        print("="*50)
        return stats

    def incremental_clean(self, minutes=30):
        """Convenience method for the auto-cleaner background thread."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=minutes)
        return self.clean(
            start_time_str=start_time.isoformat(),
            end_time_str=now.isoformat(),
            incremental=True
        )

