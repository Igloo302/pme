"""Flask API routes for Screen Memory GUI."""

import os
import re
import sqlite3
import subprocess
import time
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict

import requests as req
from flask import jsonify, request

from smgui.config import (
    SCREENPIPE_API,
    OPENCHRONICLE_BIN,
    SCREENPIPE_DATA,
    OPENCHRONICLE_DATA,
    SCREENPIPE_DB,
    OPENCHRONICLE_DB,
    SCREENPIPE_PIPES_DIR,
    CONFIG_PATH,
    OUTPUT_DB,
)


def register_routes(app):
    """Register all Flask routes on the given app instance."""

    # ── Screenpipe routes ──────────────────────────────────────────

    @app.route("/")
    def index():
        from smgui.template import HTML_TEMPLATE
        from flask import render_template_string
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/screenpipe/status")
    def screenpipe_status():
        try:
            response = req.get(f"{SCREENPIPE_API}/health", timeout=2)
            return jsonify({"running": response.status_code == 200})
        except Exception:
            return jsonify({"running": False})

    @app.route("/api/screenpipe/start", methods=["POST"])
    def screenpipe_start():
        try:
            err_log_path = "/tmp/screenpipe_start.err"
            if os.path.exists(err_log_path):
                try:
                    os.remove(err_log_path)
                except Exception:
                    pass

            cfg = get_pme_config()
            sp_cfg = cfg.get("screenpipe", {})
            bin_path = os.path.expanduser(sp_cfg.get("bin_path") or "/opt/homebrew/bin/screenpipe")
            use_audio = sp_cfg.get("use_audio", True)

            cmd = [bin_path, "record"]
            if not use_audio:
                cmd.append("--disable-audio")

            with open(err_log_path, "w") as err_file:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=err_file,
                )
            
            # Wait for 1.5 seconds to check if it crashes immediately (e.g. TCC)
            time.sleep(1.5)
            if proc.poll() is not None:
                err_content = ""
                try:
                    with open(err_log_path, "r") as f:
                        err_content = f.read().strip()
                except Exception:
                    pass
                
                if "TCC" in err_content or "permission" in err_content.lower() or "拒绝" in err_content:
                    # Automatically open macOS Screen Recording settings
                    subprocess.Popen([
                        "open", 
                        "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
                    ])
                    return jsonify({
                        "message": (
                            "Error: macOS blocked Screenpipe (TCC permission denied).\n\n"
                            "We have automatically opened System Settings -> Screen Recording for you.\n\n"
                            "Please enable the permission for 'Antigravity' (or your terminal application), "
                            "restart it, and try starting Screenpipe again."
                        )
                    })
                else:
                    return jsonify({
                        "message": f"Error: Screenpipe failed to start.\nDetails: {err_content[:200]}"
                    })

            return jsonify({"message": "Screenpipe started successfully!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/screenpipe/stop", methods=["POST"])
    def screenpipe_stop():
        try:
            subprocess.run(["pkill", "-f", "screenpipe"], capture_output=True)
            subprocess.run(["pkill", "-f", "ffmpeg"], capture_output=True)
            time.sleep(1)
            
            err_log_path = "/tmp/screenpipe_stop.err"
            if os.path.exists(err_log_path):
                try:
                    os.remove(err_log_path)
                except Exception:
                    pass

            cfg = get_pme_config()
            sp_cfg = cfg.get("screenpipe", {})
            bin_path = os.path.expanduser(sp_cfg.get("bin_path") or "/opt/homebrew/bin/screenpipe")

            with open(err_log_path, "w") as err_file:
                proc = subprocess.Popen(
                    [bin_path, "record", "--disable-audio", "--fps", "0"],
                    stdout=subprocess.DEVNULL,
                    stderr=err_file,
                )
            
            time.sleep(1.5)
            if proc.poll() is not None:
                err_content = ""
                try:
                    with open(err_log_path, "r") as f:
                        err_content = f.read().strip()
                except Exception:
                    pass
                
                if "TCC" in err_content or "permission" in err_content.lower() or "拒绝" in err_content:
                    subprocess.Popen([
                        "open", 
                        "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
                    ])
                    return jsonify({
                        "message": (
                            "Recording stopped, but the database server failed to start (TCC permission denied).\n\n"
                            "We have automatically opened System Settings -> Screen Recording for you.\n\n"
                            "Please enable the permission for 'Antigravity' (or your terminal application), "
                            "restart it, and try starting Screenpipe again."
                        )
                    })
                else:
                    return jsonify({
                        "message": f"Recording stopped, but database server failed to start.\nDetails: {err_content[:200]}"
                    })

            return jsonify({"message": "Recording stopped! Search still available."})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/screenpipe/shutdown", methods=["POST"])
    def screenpipe_shutdown():
        try:
            subprocess.run(["pkill", "-9", "-f", "screenpipe"], capture_output=True)
            subprocess.run(["pkill", "-9", "-f", "ffmpeg"], capture_output=True)
            time.sleep(1)
            return jsonify({"message": "Screenpipe completely shutdown."})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/screenpipe/search")
    def screenpipe_search():
        query = request.args.get("q", "")
        content_type = request.args.get("content_type", "all")
        try:
            params = {"q": query, "content_type": content_type, "limit": 20}
            response = req.get(
                f"{SCREENPIPE_API}/search", params=params, timeout=10
            )
            if response.status_code == 200:
                return jsonify(response.json())
            return jsonify([])
        except Exception:
            return jsonify([])

    @app.route("/api/screenpipe/open-folder", methods=["POST"])
    def screenpipe_open_folder():
        try:
            import platform
            if not os.path.exists(SCREENPIPE_DATA):
                return jsonify({"error": "Data folder does not exist"})
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", SCREENPIPE_DATA])
            elif system == "Windows":
                subprocess.run(["explorer", SCREENPIPE_DATA])
            else:
                subprocess.run(["xdg-open", SCREENPIPE_DATA])
            return jsonify({})
        except Exception as e:
            return jsonify({"error": str(e)})

    # ── OpenChronicle routes ───────────────────────────────────────

    @app.route("/api/openchronicle/status")
    def openchronicle_status():
        try:
            result = subprocess.run(
                [OPENCHRONICLE_BIN, "status"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if "Daemon" in result.stdout and "running" in result.stdout:
                pid_match = re.search(r"running pid (\d+)", result.stdout)
                files_match = re.search(r"Buffer\s+(\d+) files", result.stdout)
                return jsonify({
                    "running": True,
                    "pid": pid_match.group(1) if pid_match else None,
                    "buffer_files": int(files_match.group(1)) if files_match else 0,
                })
            return jsonify({"running": False})
        except subprocess.TimeoutExpired:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "openchronicle start"],
                    capture_output=True, text=True, timeout=2,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return jsonify({"running": True, "pid": result.stdout.strip()})
                return jsonify({"running": False})
            except Exception:
                return jsonify({"running": False})
        except Exception:
            return jsonify({"running": False})

    @app.route("/api/openchronicle/start", methods=["POST"])
    def openchronicle_start():
        try:
            subprocess.Popen(
                [OPENCHRONICLE_BIN, "start"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            return jsonify({"message": "OpenChronicle started!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/openchronicle/stop", methods=["POST"])
    def openchronicle_stop():
        try:
            subprocess.run([OPENCHRONICLE_BIN, "stop"], capture_output=True)
            time.sleep(1)
            return jsonify({"message": "OpenChronicle stopped!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/openchronicle/pause", methods=["POST"])
    def openchronicle_pause():
        try:
            subprocess.run([OPENCHRONICLE_BIN, "pause"], capture_output=True)
            return jsonify({"message": "OpenChronicle paused!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/openchronicle/resume", methods=["POST"])
    def openchronicle_resume():
        try:
            subprocess.run([OPENCHRONICLE_BIN, "resume"], capture_output=True)
            return jsonify({"message": "OpenChronicle resumed!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/pme/search")
    def pme_search():
        query = request.args.get("q", "")
        content_type = request.args.get("content_type", "all")
        if not query:
            return jsonify({"data": []})
        try:
            cfg = get_pme_config()
            db_cfg = cfg.get("database", {})
            db_path = os.path.expanduser(db_cfg.get("cleaned_db", "smgui/memory.db"))
            if not os.path.exists(db_path):
                return jsonify({"data": []})

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            results = []

            # We can use FTS MATCH, and fallback to LIKE if query has syntax errors
            try:
                cursor.execute(
                    """
                    SELECT r.timestamp, f.app_name, f.window_title, f.ocr_text, f.cleaned_text
                    FROM records_fts f
                    JOIN records r ON f.id = r.id
                    WHERE records_fts MATCH ?
                    LIMIT 20
                    """,
                    (query,),
                )
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                cursor.execute(
                    """
                    SELECT timestamp, app_name, window_title, ocr_text, cleaned_text
                    FROM records
                    WHERE app_name LIKE ? OR window_title LIKE ? OR ocr_text LIKE ? OR cleaned_text LIKE ?
                    LIMIT 20
                    """,
                    (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"),
                )
                rows = cursor.fetchall()

            for row in rows:
                timestamp, app_name, window_title, ocr_text, cleaned_text = row
                text = cleaned_text or ocr_text or ""
                results.append({
                    "type": "PME Record",
                    "content": {
                        "timestamp": timestamp,
                        "app_name": app_name or "Unknown",
                        "app": app_name or "Unknown",
                        "window_name": window_title or "",
                        "text": text[:500],
                        "content": text[:500]
                    }
                })

            conn.close()
            return jsonify({"data": results})
        except Exception as e:
            return jsonify({"data": [], "error": str(e)})

    @app.route("/api/openchronicle/search")
    def openchronicle_search():
        query = request.args.get("q", "")
        content_type = request.args.get("content_type", "all")
        try:
            cfg = get_pme_config()
            db_cfg = cfg.get("database", {})
            db_path = os.path.expanduser(db_cfg.get("openchronicle_db", "~/.openchronicle/index.db"))
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            results = []

            if content_type in ("captures", "all"):
                cursor.execute(
                    """
                    SELECT rowid, app_name, window_title,
                           focused_value, visible_text, url
                    FROM captures_fts
                    WHERE captures_fts MATCH ?
                    LIMIT 20
                    """,
                    (query,),
                )
                for row in cursor.fetchall():
                    cursor2 = conn.cursor()
                    cursor2.execute(
                        "SELECT timestamp FROM captures WHERE rowid = ?", (row[0],)
                    )
                    ts_row = cursor2.fetchone()
                    timestamp = ts_row[0] if ts_row else "Unknown"
                    text = row[3] or row[4] or ""
                    results.append({
                        "type": "Capture",
                        "content": {
                            "timestamp": timestamp,
                            "app_name": row[1] or "Unknown",
                            "app": row[1] or "Unknown",
                            "window_name": row[2] or "",
                            "text": text[:500],
                            "content": text[:500],
                            "url": row[5] or "",
                        },
                    })

            if content_type in ("entries", "all"):
                cursor.execute(
                    """
                    SELECT id, prefix, timestamp, tags, content
                    FROM entries
                    WHERE entries MATCH ?
                    LIMIT 20
                    """,
                    (query,),
                )
                for row in cursor.fetchall():
                    results.append({
                        "type": "Event",
                        "content": {
                            "timestamp": row[2],
                            "app_name": row[1] or "Unknown",
                            "app": row[1] or "Unknown",
                            "text": (row[4] or "")[:500],
                            "content": (row[4] or "")[:500],
                            "tags": row[3] or "",
                        },
                    })

            conn.close()
            return jsonify({"data": results})
        except Exception as e:
            return jsonify({"data": [], "error": str(e)})

    @app.route("/api/openchronicle/open-folder", methods=["POST"])
    def openchronicle_open_folder():
        try:
            import platform
            if not os.path.exists(OPENCHRONICLE_DATA):
                return jsonify({"error": "Data folder does not exist"})
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", OPENCHRONICLE_DATA])
            elif system == "Windows":
                subprocess.run(["explorer", OPENCHRONICLE_DATA])
            else:
                subprocess.run(["xdg-open", OPENCHRONICLE_DATA])
            return jsonify({})
        except Exception as e:
            return jsonify({"error": str(e)})

    # ── Activity heatmap ───────────────────────────────────────────

    @app.route("/api/activity/heatmap")
    def activity_heatmap():
        try:
            backend = request.args.get("backend", "").lower()
            if not backend:
                backend = "pme"

            use_pme = False
            use_screenpipe = False

            cfg = get_pme_config()
            db_cfg = cfg.get("database", {})
            if backend == "pme":
                db_path = os.path.expanduser(db_cfg.get("cleaned_db", "smgui/memory.db"))
                use_pme = True
            elif backend == "screenpipe":
                db_path = os.path.expanduser(db_cfg.get("screenpipe_db", "~/.screenpipe/db.sqlite"))
                use_screenpipe = True
            else:  # openchronicle
                db_path = os.path.expanduser(db_cfg.get("openchronicle_db", "~/.openchronicle/index.db"))

            if not os.path.exists(db_path):
                return jsonify([])

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            days = 30
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Uniform SQLite date filter formatting
            date_filter = start_date.strftime("%Y-%m-%d")

            if use_pme:
                cursor.execute(
                    """
                    SELECT timestamp as ts, app_name FROM records
                    WHERE date(timestamp) >= ? ORDER BY timestamp
                    """,
                    (date_filter,),
                )
            elif use_screenpipe:
                cursor.execute(
                    """
                    SELECT f.timestamp as ts, COALESCE(o.app_name, 'Unknown') as app_name
                    FROM frames f
                    LEFT JOIN ocr_text o ON o.frame_id = f.id
                    WHERE date(f.timestamp) >= ?
                    GROUP BY f.id
                    ORDER BY f.timestamp
                    """,
                    (date_filter,),
                )
            else:
                cursor.execute(
                    """
                    SELECT timestamp as ts, app_name FROM captures
                    WHERE date(timestamp) >= ? ORDER BY timestamp
                    """,
                    (date_filter,),
                )

            rows = cursor.fetchall()
            conn.close()

            day_hour_data = defaultdict(
                lambda: defaultdict(lambda: {"count": 0, "apps": defaultdict(int)})
            )
            for ts_str, app_name in rows:
                try:
                    # Parse timezone-aware ISO string, then convert to local timezone
                    ts = datetime.fromisoformat(ts_str).astimezone()
                    day_key = ts.strftime("%Y-%m-%d")
                    hour = ts.hour
                    day_hour_data[day_key][hour]["count"] += 1
                    if app_name:
                        day_hour_data[day_key][hour]["apps"][app_name] += 1
                except Exception as e:
                    continue

            result = []
            for i in range(days - 1, -1, -1):
                date = end_date - timedelta(days=i)
                day_key = date.strftime("%Y-%m-%d")
                day_data = day_hour_data.get(day_key, {})
                hours = []
                for hour in range(24):
                    hour_data = day_data.get(hour, {"count": 0, "apps": {}})
                    sorted_apps = sorted(
                        hour_data["apps"].items(), key=lambda x: -x[1]
                    )
                    top_apps = [app for app, _ in sorted_apps[:5]]
                    hours.append({
                        "hour": hour,
                        "count": hour_data["count"],
                        "apps": top_apps,
                    })
                result.append({
                    "date": day_key,
                    "day_name": date.strftime("%a"),
                    "hours": hours,
                })
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ── Screenpipe Pipes ───────────────────────────────────────────

    @app.route("/api/screenpipe/pipes")
    def screenpipe_pipes():
        pipes = []
        pipes_dir = SCREENPIPE_PIPES_DIR
        if not os.path.isdir(pipes_dir):
            return jsonify([])
        for name in sorted(os.listdir(pipes_dir)):
            pipe_path = os.path.join(pipes_dir, name)
            if not os.path.isdir(pipe_path):
                continue
            pipe_md = os.path.join(pipe_path, "pipe.md")
            info = {"name": name, "enabled": True, "description": "", "schedule": ""}
            # Check if disabled (symlink or existence of .disabled)
            if os.path.exists(os.path.join(pipe_path, ".disabled")):
                info["enabled"] = False
            if os.path.isfile(pipe_md):
                try:
                    with open(pipe_md, "r") as f:
                        content = f.read(2048)
                    # Simple frontmatter parsing
                    if content.startswith("---"):
                        end = content.find("---", 3)
                        if end != -1:
                            fm = content[3:end]
                            for line in fm.split("\n"):
                                line = line.strip()
                                if line.startswith("description:"):
                                    info["description"] = line.split(":", 1)[1].strip().strip('"').strip("'")
                                elif line.startswith("schedule:"):
                                    info["schedule"] = line.split(":", 1)[1].strip().strip('"').strip("'")
                except Exception:
                    pass
            pipes.append(info)
        return jsonify(pipes)

    @app.route("/api/screenpipe/pipes/<name>/enable", methods=["POST"])
    def screenpipe_pipe_enable(name):
        pipe_path = os.path.join(SCREENPIPE_PIPES_DIR, name)
        disabled_flag = os.path.join(pipe_path, ".disabled")
        if os.path.exists(disabled_flag):
            os.remove(disabled_flag)
        return jsonify({"message": f"Pipe '{name}' enabled"})

    @app.route("/api/screenpipe/pipes/<name>/disable", methods=["POST"])
    def screenpipe_pipe_disable(name):
        pipe_path = os.path.join(SCREENPIPE_PIPES_DIR, name)
        if os.path.isdir(pipe_path):
            disabled_flag = os.path.join(pipe_path, ".disabled")
            with open(disabled_flag, "w") as f:
                f.write("")
            return jsonify({"message": f"Pipe '{name}' disabled"})
        return jsonify({"error": "Pipe not found"}), 404

    # ── Stats ──────────────────────────────────────────────────────

    def query_db_stats(db_path, db_type):
        stats = {
            "exists": False,
            "total_captures": 0,
            "daily_captures": 0,
            "weekly_captures": 0,
            "storage_mb": 0.0
        }
        if not db_path or not os.path.exists(db_path):
            return stats
        
        stats["exists"] = True
        try:
            db_size = os.path.getsize(db_path)
            stats["storage_mb"] = round(db_size / (1024 * 1024), 2)
        except Exception:
            pass
            
        table_name = "frames" if db_type == "screenpipe" else ("captures" if db_type == "openchronicle" else "records")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Total captures
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                stats["total_captures"] = cursor.fetchone()[0]
            except Exception:
                pass
                
            # Daily captures (today)
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE date(timestamp) = ?",
                    (today,),
                )
                stats["daily_captures"] = cursor.fetchone()[0]
            except Exception:
                pass
                
            # Weekly captures (past 7 days)
            try:
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE timestamp >= ?",
                    (week_ago,),
                )
                stats["weekly_captures"] = cursor.fetchone()[0]
            except Exception:
                pass
                
            conn.close()
        except Exception:
            pass
            
        return stats

    @app.route("/api/stats/summary")
    def stats_summary():
        cfg = get_pme_config()
        db_cfg = cfg.get("database", {})
        screenpipe_path = os.path.expanduser(db_cfg.get("screenpipe_db", "~/.screenpipe/db.sqlite"))
        openchronicle_path = os.path.expanduser(db_cfg.get("openchronicle_db", "~/.openchronicle/index.db"))
        cleaned_path = os.path.expanduser(db_cfg.get("cleaned_db", "smgui/memory.db"))

        return jsonify({
            "screenpipe": query_db_stats(screenpipe_path, "screenpipe"),
            "openchronicle": query_db_stats(openchronicle_path, "openchronicle"),
            "pme": query_db_stats(cleaned_path, "pme")
        })

    # ── Timeline ───────────────────────────────────────────────────

    @app.route("/api/timeline")
    def timeline():
        date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
        limit = int(request.args.get("limit", "50"))
        events = []

        db_path = OUTPUT_DB
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                # First try to fetch from screen_facts (LLM-cleaned facts)
                cursor.execute(
                    """
                    SELECT replace(substr(start_timestamp, 1, 19), 'T', ' ') as ts,
                           app_name, window_title, fact_text as text
                    FROM screen_facts
                    WHERE date(start_timestamp) = ?
                    ORDER BY start_timestamp DESC
                    LIMIT ?
                    """,
                    (date, limit),
                )
                rows = cursor.fetchall()

                # Fall back to records table if no facts exist yet for this date
                if not rows:
                    cursor.execute(
                        """
                        SELECT replace(substr(timestamp, 1, 19), 'T', ' ') as ts,
                               app_name, window_title, COALESCE(cleaned_text, ocr_text, '') as text
                        FROM records
                        WHERE date(timestamp) = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                        """,
                        (date, limit),
                    )
                    rows = cursor.fetchall()

                for row in rows:
                    events.append({
                        "time": row[0],
                        "app_name": row[1] or "Unknown",
                        "type": "capture",
                        "text": (row[3] or "")[:300],
                        "window_title": row[2] or "",
                    })
                conn.close()
            except Exception as e:
                return jsonify({"error": str(e), "events": []}), 500

        return jsonify({"date": date, "events": events})

    # ── PME Cleaner routes ──────────────────────────────────────────

    @app.route("/api/pme/clean", methods=["POST"])
    def pme_clean():
        global pme_cleaner_state
        phase = request.json.get("phase") if (request.is_json and request.json) else request.form.get("phase")
        start_time_str = request.json.get("start_time") if (request.is_json and request.json) else request.form.get("start_time")
        end_time_str = request.json.get("end_time") if (request.is_json and request.json) else request.form.get("end_time")
        if not phase:
            phase = request.args.get("phase")
        if phase == "all" or phase == "":
            phase = None

        with pme_lock:
            if pme_cleaner_state["running"]:
                return jsonify({"status": "busy", "message": "Cleaner is already running"})
            pme_cleaner_state["running"] = True
            pme_cleaner_state["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pme_cleaner_state["last_run_phase"] = phase or "all"
            pme_cleaner_state["last_run_status"] = "running"
            pme_cleaner_state["last_run_error"] = None
        
        # Start background job
        t = threading.Thread(
            target=run_pme_cleaner_job,
            kwargs={
                "phase": phase,
                "start_time_str": start_time_str,
                "end_time_str": end_time_str
            }
        )
        t.daemon = True
        t.start()
        
        return jsonify({"status": "started", "message": "PME cleaning process started in background"})

    @app.route("/api/pme/status")
    def pme_status():
        with pme_lock:
            state_copy = pme_cleaner_state.copy()
        state_copy["schedule_state"] = get_schedule_state()
        state_copy["enabled"] = get_pme_config().get("screen_memory", {}).get("enabled", True)
        return jsonify(state_copy)

    @app.route("/api/pme/start", methods=["POST"])
    def pme_start_route():
        success = save_pme_config({"screen_memory": {"enabled": True}})
        return jsonify({"success": success})

    @app.route("/api/pme/stop", methods=["POST"])
    def pme_stop_route():
        success = save_pme_config({"screen_memory": {"enabled": False}})
        return jsonify({"success": success})

    @app.route("/api/pme/config", methods=["GET", "POST"])
    def pme_config_route():
        if request.method == "POST":
            new_config = request.json
            if not isinstance(new_config, dict):
                return jsonify({"error": "Invalid JSON configuration payload"}), 400
            
            # Check LLM connection if model section is in new_config
            model_cfg = new_config.get("model")
            if model_cfg and isinstance(model_cfg, dict):
                if model_cfg.get("api_key") or model_cfg.get("model"):
                    ok, err = test_llm_connection(model_cfg)
                    if not ok:
                        return jsonify({"success": False, "error": f"LLM API verification failed: {err}"})

            success = save_pme_config(new_config)
            return jsonify({"success": success})
        else:
            config = get_pme_config()
            return jsonify(config)

    # Start the background auto-cleaning scheduler loop
    def run_auto_cleaner_loop():
        # Wait for Flask to initialize
        time.sleep(5)
        while True:
            try:
                from smgui.service import run_screen_memory_due_work
                cfg = get_pme_config()
                is_enabled = cfg.get("screen_memory", {}).get("enabled", True)
                if is_enabled:
                    run_screen_memory_due_work()
            except Exception as e:
                print(f"Error in background scheduler: {e}")
            time.sleep(30)

    scheduler_thread = threading.Thread(target=run_auto_cleaner_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()


# ── PME Helper Functions & State (Module Level) ───────────────────

pme_cleaner_state = {
    "running": False,
    "last_run_time": None,
    "last_run_status": None,
    "last_run_phase": None,
    "last_run_error": None,
    "last_run_stats": None
}
pme_lock = threading.Lock()

def run_pme_cleaner_job(phase=None, start_time_str=None, end_time_str=None):
    global pme_cleaner_state
    try:
        from smgui.service import run_screen_memory_due_work
        custom_start = None
        custom_end = None
        if start_time_str:
            try:
                dt = datetime.fromisoformat(start_time_str)
                if dt.tzinfo is None:
                    dt = dt.astimezone()
                    dt = dt.astimezone(timezone.utc)
                custom_start = dt
            except Exception:
                pass
        if end_time_str:
            try:
                dt = datetime.fromisoformat(end_time_str)
                if dt.tzinfo is None:
                    dt = dt.astimezone()
                    dt = dt.astimezone(timezone.utc)
                custom_end = dt
            except Exception:
                pass

        result = run_screen_memory_due_work(
            force_phase=phase,
            custom_start_time=custom_start,
            custom_end_time=custom_end
        )
        
        with pme_lock:
            pme_cleaner_state["running"] = False
            pme_cleaner_state["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pme_cleaner_state["last_run_phase"] = phase or "all"
            if result.get("status") == "ok":
                pme_cleaner_state["last_run_status"] = "success"
                pme_cleaner_state["last_run_stats"] = result
            elif result.get("status") == "busy":
                pme_cleaner_state["last_run_status"] = "error"
                pme_cleaner_state["last_run_error"] = result.get("message", "Pipeline lock is held")
            else:
                pme_cleaner_state["last_run_status"] = "error"
                pme_cleaner_state["last_run_error"] = result.get("message", "Unknown error")
    except Exception as e:
        with pme_lock:
            pme_cleaner_state["running"] = False
            pme_cleaner_state["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pme_cleaner_state["last_run_phase"] = phase or "all"
            pme_cleaner_state["last_run_status"] = "error"
            pme_cleaner_state["last_run_error"] = str(e)

def get_pme_config():
    import yaml
    config_path = CONFIG_PATH
    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            pass

    # Standard defaults matching the requirements
    database = data.get("database", {})
    if not database:
        database = {
            "screenpipe_db": "~/.screenpipe/db.sqlite",
            "openchronicle_db": "~/.openchronicle/index.db",
            "cleaned_db": OUTPUT_DB
        }
        
    screenpipe = data.get("screenpipe", {})
    if not screenpipe:
        screenpipe = {
            "bin_path": "/opt/homebrew/bin/screenpipe",
            "api_url": "http://localhost:3030",
            "api_token": "",
            "use_audio": True
        }
    elif "use_audio" not in screenpipe:
        screenpipe["use_audio"] = True
        
    openchronicle = data.get("openchronicle", {})
    if not openchronicle:
        openchronicle = {
            "bin_path": "/Users/jyshen/.local/bin/openchronicle"
        }
        
    screen_memory = data.get("screen_memory", {})
    if not screen_memory:
        screen_memory = {
            "ingest_interval_minutes": 30,
            "fact_clustering_interval_hours": 2,
            "observation_interval_hours": 24,
            "enabled": True
        }
        
    model = data.get("model", {})
    if not model:
        model = {
            "provider": "openai-codex",
            "model": "gpt-5.5",
            "base_url": "https://chatgpt.com/backend-api/codex",
            "api_key": "",
            "temperature": 0.2
        }

    embedding = data.get("embedding", {})
    if not embedding:
        embedding = {
            "enabled": False,
            "provider": "openai",
            "model": "text-embedding-3-small",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": "",
            "api_key_env": "EMBEDDING_API_KEY",
            "dimensions": 1536,
            "normalize": True
        }

    return {
        "database": database,
        "screenpipe": screenpipe,
        "openchronicle": openchronicle,
        "screen_memory": screen_memory,
        "model": model,
        "embedding": embedding
    }

def test_llm_connection(model_cfg):
    from openai import OpenAI
    import os
    
    provider = model_cfg.get("provider", "openai-codex")
    model = model_cfg.get("model", "")
    base_url = model_cfg.get("base_url", "")
    api_key = model_cfg.get("api_key", "")
    
    if not api_key and not model:
        return True, None
        
    if not api_key:
        is_local = base_url and any(x in base_url for x in ["localhost", "127.0.0.1", "::1"])
        if is_local:
            api_key = "dummy"
        else:
            api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                return False, "API key is missing"
                
    if not base_url:
        if provider == "openai-codex":
            base_url = "https://chatgpt.com/backend-api/codex"
        else:
            base_url = "https://api.openai.com/v1"
            
    if not model:
        return False, "Model name is missing"
        
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=2,
            timeout=5.0
        )
        return True, None
    except Exception as e:
        return False, str(e)

def save_pme_config(new_config):
    import yaml
    config_path = CONFIG_PATH
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        # Merge key sections
        for section in ["database", "screenpipe", "openchronicle", "screen_memory", "model", "embedding"]:
            if section in new_config and isinstance(new_config[section], dict):
                if section not in data or not isinstance(data[section], dict):
                    data[section] = {}
                for k, v in new_config[section].items():
                    data[section][k] = v

        with open(config_path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception:
        return False

def get_schedule_state():
    from smgui.config import SCHEDULE_STATE_PATH
    if os.path.exists(SCHEDULE_STATE_PATH):
        try:
            with open(SCHEDULE_STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

