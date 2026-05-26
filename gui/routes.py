"""Flask API routes for PME Behavior Monitor GUI."""

import os
import re
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from collections import defaultdict

import requests as req
from flask import jsonify, request

from src.config_loader import get_config

def register_routes(app):
    """Register all Flask routes on the given app instance."""
    
    # Start PME background auto-cleaner thread
    import threading
    from datetime import timezone
    
    # Shared state for auto-cleaner status (thread-safe via GIL for simple appends)
    auto_cleaner_log = []
    auto_cleaner_state = {"running": False, "last_check": None, "total_runs": 0}
    
    def _has_recent_data(db_path, table, minutes=10):
        """Check if a database has records written in the last N minutes."""
        if not db_path or not os.path.exists(os.path.expanduser(db_path)):
            return False
        try:
            conn = sqlite3.connect(os.path.expanduser(db_path))
            cursor = conn.cursor()
            cursor.execute(f"SELECT timestamp FROM {table} ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if not row or not row[0]:
                return False
            ts_str = row[0].replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = now - dt.astimezone(timezone.utc)
            return -60 <= diff.total_seconds() <= minutes * 60
        except Exception as e:
            print(f"Error checking recent data in {db_path} ({table}): {e}")
            return False

    def run_auto_clean_once():
        auto_cleaner_state["last_check"] = datetime.now().isoformat()
        
        # Check for fresh data instead of checking if processes are running
        sp_has_data = _has_recent_data(get_sp_db(), "frames", minutes=10)
        oc_has_data = _has_recent_data(get_oc_db(), "captures", minutes=10)
            
        if sp_has_data and oc_has_data:
            auto_cleaner_state["running"] = True
            print("🔄 Auto-cleaner: Fresh data in both databases. Running incremental PME clean...")
            from src.cleaner import PMECleaner
            cleaner = PMECleaner()
            stats = cleaner.incremental_clean(minutes=30)
            auto_cleaner_state["total_runs"] += 1
            if stats:
                log_entry = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "raw": stats.get("raw_records", 0),
                    "cleaned": stats.get("cleaned_records", 0),
                    "discarded": stats.get("discarded_incomplete_records", 0),
                    "dedup": stats.get("deduplicated", 0),
                    "status": "success"
                }
                auto_cleaner_log.append(log_entry)
                # Keep only last 50 entries
                if len(auto_cleaner_log) > 50:
                    auto_cleaner_log.pop(0)
                print(f"✅ Auto-cleaner success: raw={stats.get('raw_records', 0)}, cleaned={stats.get('cleaned_records', 0)}, discarded={stats.get('discarded_incomplete_records', 0)}")
                return True, stats, None
            return False, None, "No stats returned"
        else:
            auto_cleaner_state["running"] = False
            reason = []
            if not sp_has_data:
                reason.append("No recent Screenpipe data")
            if not oc_has_data:
                reason.append("No recent OpenChronicle data")
            reason_str = ", ".join(reason)
            log_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "status": "skipped",
                "reason": reason_str
            }
            auto_cleaner_log.append(log_entry)
            if len(auto_cleaner_log) > 50:
                auto_cleaner_log.pop(0)
            return False, None, reason_str

    def start_auto_cleaner():
        def worker():
            # Wait for Flask server to launch completely
            time.sleep(10)
            print("🌱 PME Auto-cleaner background thread started.")
            while True:
                try:
                    run_auto_clean_once()
                except Exception as e:
                    print(f"⚠️ Auto-cleaner error: {e}")
                    auto_cleaner_log.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "status": "error",
                        "reason": str(e)[:100]
                    })
                
                # Check status and run every 5 minutes
                time.sleep(300)
                
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    start_auto_cleaner()
    
    # Auto-cleaner status API
    @app.route("/api/pme/auto-cleaner/status")
    def auto_cleaner_status():
        return jsonify({
            "state": auto_cleaner_state,
            "log": auto_cleaner_log[-10:]  # Return last 10 entries
        })

    # Auto-cleaner trigger API
    @app.route("/api/pme/auto-cleaner/trigger", methods=["POST"])
    def auto_cleaner_trigger():
        try:
            success, stats, reason = run_auto_clean_once()
            if success:
                return jsonify({
                    "success": True,
                    "message": "Incremental PME clean completed successfully.",
                    "stats": stats
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Cleaner skipped: {reason}"
                })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error triggering auto-cleaner: {e}"
            }), 500

    # Dynamic configuration getters so Web UI modifications take effect immediately
    def get_sp_api():
        return get_config().get("screenpipe", {}).get("api_url", "http://localhost:3030")
    
    def get_sp_bin():
        return get_config().get("screenpipe", {}).get("bin_path", "/opt/homebrew/bin/screenpipe")
        
    def get_oc_bin():
        return get_config().get("openchronicle", {}).get("bin_path", "/Users/jyshen/.local/bin/openchronicle")
        
    def get_sp_db():
        return get_config().get("database", {}).get("screenpipe_db")
        
    def get_oc_db():
        return get_config().get("database", {}).get("openchronicle_db")
        
    def get_cleaned_db():
        return get_config().get("database", {}).get("cleaned_db")

    def get_auth_headers():
        token = get_config().get("screenpipe", {}).get("api_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    # ── Main template ──────────────────────────────────────────

    @app.route("/")
    def index():
        from gui.template import HTML_TEMPLATE
        from flask import render_template_string
        return render_template_string(HTML_TEMPLATE)

    # ── Screenpipe Control routes ──────────────────────────────────────────

    @app.route("/api/screenpipe/status")
    def screenpipe_status():
        try:
            # Health endpoint does not require auth, but we pass headers just in case
            response = req.get(f"{get_sp_api()}/health", headers=get_auth_headers(), timeout=2)
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

            with open(err_log_path, "w") as err_file:
                # Upgraded screenpipe requires "record" subcommand to start daemon
                proc = subprocess.Popen(
                    [get_sp_bin(), "record"],
                    stdout=subprocess.DEVNULL,
                    stderr=err_file,
                )
            
            # Wait to check for immediate crash (e.g. TCC)
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
                            "Error: macOS blocked Screenpipe (TCC permission denied).\n\n"
                            "We have automatically opened System Settings -> Screen Recording for you.\n\n"
                            "Please enable the permission for the terminal application or 'Antigravity', "
                            "restart and try again."
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
            return jsonify({"message": "Screenpipe recording daemon stopped successfully!"})
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
            # Crucial: inject Bearer Token authentication to prevent 403 Forbidden!
            response = req.get(
                f"{get_sp_api()}/search", 
                params=params, 
                headers=get_auth_headers(), 
                timeout=10
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
            sp_dir = os.path.dirname(get_sp_db())
            if not os.path.exists(sp_dir):
                return jsonify({"error": "Data folder does not exist"})
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", sp_dir])
            elif system == "Windows":
                subprocess.run(["explorer", sp_dir])
            else:
                subprocess.run(["xdg-open", sp_dir])
            return jsonify({})
        except Exception as e:
            return jsonify({"error": str(e)})

    # ── OpenChronicle Control routes ───────────────────────────────────────

    @app.route("/api/openchronicle/status")
    def openchronicle_status():
        try:
            result = subprocess.run(
                [get_oc_bin(), "status"],
                capture_output=True,
                text=True,
                timeout=10,
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
        except Exception:
            try:
                # Fallback check
                result = subprocess.run(
                    ["pgrep", "-f", "openchronicle start"],
                    capture_output=True, text=True, timeout=2,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return jsonify({"running": True, "pid": result.stdout.strip()})
                return jsonify({"running": False})
            except Exception:
                return jsonify({"running": False})

    @app.route("/api/openchronicle/start", methods=["POST"])
    def openchronicle_start():
        try:
            subprocess.Popen(
                [get_oc_bin(), "start"],
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
            subprocess.run([get_oc_bin(), "stop"], capture_output=True)
            time.sleep(1)
            return jsonify({"message": "OpenChronicle stopped!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/openchronicle/pause", methods=["POST"])
    def openchronicle_pause():
        try:
            subprocess.run([get_oc_bin(), "pause"], capture_output=True)
            return jsonify({"message": "OpenChronicle paused!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/openchronicle/resume", methods=["POST"])
    def openchronicle_resume():
        try:
            subprocess.run([get_oc_bin(), "resume"], capture_output=True)
            return jsonify({"message": "OpenChronicle resumed!"})
        except Exception as e:
            return jsonify({"message": f"Error: {str(e)}"})

    @app.route("/api/openchronicle/search")
    def openchronicle_search():
        query = request.args.get("q", "")
        if not os.path.exists(get_oc_db()):
            return jsonify([])
            
        try:
            conn = sqlite3.connect(get_oc_db())
            cursor = conn.cursor()
            results = []

            # Search in FTS table
            cursor.execute(
                """
                SELECT rowid, app_name, window_title, focused_value, visible_text, url
                FROM captures_fts
                WHERE captures_fts MATCH ?
                LIMIT 20
                """,
                (f'"{query}"',),
            )
            for row in cursor.fetchall():
                cursor2 = conn.cursor()
                cursor2.execute(
                    "SELECT timestamp FROM captures WHERE rowid = ?", (row[0],)
                )
                ts_row = cursor2.fetchone()
                timestamp = ts_row[0] if ts_row else "Unknown"
                text = row[4] or ""
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
            conn.close()
            return jsonify(results)
        except Exception:
            return jsonify([])

    # ── PME Cleaned Database Search ───────────────────────────────────────

    @app.route("/api/pme/search")
    def pme_search():
        query = request.args.get("q", "")
        if not query:
            return jsonify([])
        try:
            from src.qa_engine import PMEQueryEngine
            engine = PMEQueryEngine()
            rows = engine.retrieve_context(query, limit=20)
            results = []
            for row in rows:
                ts, app, title, text, reason, focused = row
                status = "Active" if focused else "Background"
                results.append({
                    "type": "Cleaned Memory",
                    "content": {
                        "timestamp": ts,
                        "app_name": app or "Unknown",
                        "app": app or "Unknown",
                        "window_name": title or "",
                        "text": text[:500] if text else "",
                        "content": text[:500] if text else "",
                        "trigger_reason": reason or "",
                        "focused": focused,
                        "status": status
                    }
                })
            return jsonify(results)
        except FileNotFoundError as e:
            return jsonify([{
                "type": "Error",
                "content": {
                    "timestamp": "-",
                    "app_name": "System",
                    "app": "System",
                    "text": "PME Cleaned DB not found. Please clean data first in PME Engine tab.",
                    "content": "PME Cleaned DB not found. Please clean data first in PME Engine tab."
                }
            }])
        except Exception as e:
            return jsonify([{
                "type": "Error",
                "content": {
                    "timestamp": "-",
                    "app_name": "System",
                    "app": "System",
                    "text": f"Search failed: {str(e)}",
                    "content": f"Search failed: {str(e)}"
                }
            }])

    # ── PME Cleaned Database Dashboard & Heatmap ───────────────────────────

    @app.route("/api/activity/heatmap")
    def activity_heatmap():
        try:
            backend = request.args.get("backend", "").lower()
            oc_db = get_oc_db()
            sp_db = get_sp_db()
            
            if not backend:
                db_path = oc_db
                use_screenpipe = False
                if not db_path or not os.path.exists(os.path.expanduser(db_path)):
                    db_path = sp_db
                    use_screenpipe = True
            elif backend == "screenpipe":
                db_path = sp_db
                use_screenpipe = True
            else:  # openchronicle
                db_path = oc_db
                use_screenpipe = False

            if not db_path or not os.path.exists(os.path.expanduser(db_path)):
                return jsonify([])

            conn = sqlite3.connect(os.path.expanduser(db_path))
            cursor = conn.cursor()
            days = 30
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            if use_screenpipe:
                cursor.execute(
                    """
                    SELECT datetime(f.timestamp) as ts, COALESCE(o.app_name, 'Unknown') as app_name
                    FROM frames f
                    LEFT JOIN ocr_text o ON o.frame_id = f.id
                    WHERE f.timestamp >= ?
                    GROUP BY f.id
                    ORDER BY f.timestamp
                    """,
                    (start_date.isoformat(),),
                )
            else:
                cursor.execute(
                    "SELECT datetime(timestamp) as ts, app_name FROM captures "
                    "WHERE timestamp >= ? ORDER BY timestamp",
                    (start_date.isoformat(),),
                )

            rows = cursor.fetchall()
            conn.close()

            day_hour_data = defaultdict(
                lambda: defaultdict(lambda: {"count": 0, "apps": defaultdict(int)})
            )
            for ts_str, app_name in rows:
                try:
                    cleaned_ts = ts_str.split(".")[0].replace("Z", "").replace("T", " ")
                    if "+" in cleaned_ts:
                        cleaned_ts = cleaned_ts.split("+")[0]
                    ts = datetime.strptime(cleaned_ts, "%Y-%m-%d %H:%M:%S")
                    day_key = ts.strftime("%Y-%m-%d")
                    hour = ts.hour
                    day_hour_data[day_key][hour]["count"] += 1
                    if app_name:
                        day_hour_data[day_key][hour]["apps"][app_name] += 1
                except Exception:
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        day_key = ts.strftime("%Y-%m-%d")
                        hour = ts.hour
                        day_hour_data[day_key][hour]["count"] += 1
                        if app_name:
                            day_hour_data[day_key][hour]["apps"][app_name] += 1
                    except Exception:
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
            
    # ── PME Cleaned Database status API ───────────────────────────────────

    @app.route("/api/pme/status")
    def pme_status():
        sp_db_path = get_sp_db()
        oc_db_path = get_oc_db()
        pme_db_path = get_cleaned_db()
        
        sp_size = os.path.getsize(sp_db_path) if os.path.exists(sp_db_path) else 0
        oc_size = os.path.getsize(oc_db_path) if os.path.exists(oc_db_path) else 0
        pme_size = os.path.getsize(pme_db_path) if os.path.exists(pme_db_path) else 0
        
        sp_count = 0
        oc_count = 0
        pme_count = 0
        
        try:
            if sp_size > 0:
                conn = sqlite3.connect(sp_db_path)
                sp_count = conn.cursor().execute("SELECT count(*) FROM ocr_text").fetchone()[0]
                conn.close()
            if oc_size > 0:
                conn = sqlite3.connect(oc_db_path)
                oc_count = conn.cursor().execute("SELECT count(*) FROM captures").fetchone()[0]
                conn.close()
            if pme_size > 0:
                conn = sqlite3.connect(pme_db_path)
                pme_count = conn.cursor().execute("SELECT count(*) FROM cleaned_memories").fetchone()[0]
                conn.close()
        except Exception:
            pass
            
        return jsonify({
            "screenpipe": {"size_mb": round(sp_size / (1024*1024), 2), "records": sp_count},
            "openchronicle": {"size_mb": round(oc_size / (1024*1024), 2), "records": oc_count},
            "pme_cleaned": {"size_mb": round(pme_size / (1024*1024), 2), "records": pme_count}
        })

    # ── PME Config and Cleaning API Endpoints ───────────────────────────

    @app.route("/api/config")
    def get_gui_config():
        try:
            from src.config_loader import load_yaml_config
            return jsonify(load_yaml_config())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/config", methods=["POST"])
    def save_gui_config():
        try:
            import yaml
            from src.config_loader import load_yaml_config
            new_data = request.json or {}
            
            # Read existing to merge and preserve unexposed configurations (like LLM, Token)
            current_config = load_yaml_config()
            
            if "database" in new_data:
                current_config["database"] = current_config.get("database", {})
                current_config["database"].update(new_data["database"])
            if "cleaning_policy" in new_data:
                current_config["cleaning_policy"] = current_config.get("cleaning_policy", {})
                current_config["cleaning_policy"].update(new_data["cleaning_policy"])
            if "screenpipe" in new_data:
                current_config["screenpipe"] = current_config.get("screenpipe", {})
                current_config["screenpipe"].update(new_data["screenpipe"])
            if "openchronicle" in new_data:
                current_config["openchronicle"] = current_config.get("openchronicle", {})
                current_config["openchronicle"].update(new_data["openchronicle"])
            if "llm" in new_data:
                current_config["llm"] = current_config.get("llm", {})
                current_config["llm"].update(new_data["llm"])
                
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(current_config, f, default_flow_style=False, allow_unicode=True)
                
            return jsonify({"message": "Configuration saved successfully!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/pme/clean", methods=["POST"])
    def run_pme_clean():
        try:
            from src.cleaner import PMECleaner
            req_data = request.json or {}
            start_time = req_data.get("start_time")
            end_time = req_data.get("end_time")
            output_path = req_data.get("output_path")  # User-specified save path
            
            if not output_path:
                import tempfile
                fd, temp_path = tempfile.mkstemp(suffix=".db", prefix="pme_temp_cleaned_")
                os.close(fd)
                output_path = temp_path
                
            cleaner = PMECleaner()
            stats = cleaner.clean(
                start_time_str=start_time,
                end_time_str=end_time,
                output_path=output_path
            )
            if stats:
                return jsonify({
                    "success": True,
                    "stats": stats,
                    "output_path": stats.get("output_path", ""),
                    "message": "PME Database cleaned and generated successfully!"
                })
            else:
                return jsonify({"success": False, "message": "Failed to clean database."}), 500
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @app.route("/api/pme/clean/download")
    def download_cleaned_db():
        """Download the last generated cleaned DB file."""
        try:
            file_path = request.args.get("path", "")
            if not file_path:
                file_path = get_cleaned_db()
            file_path = os.path.expanduser(file_path)
            if not os.path.exists(file_path):
                return jsonify({"error": "Cleaned DB file not found"}), 404
            from flask import send_file
            return send_file(
                file_path,
                as_attachment=True,
                download_name="pme_cleaned_memories.db",
                mimetype="application/x-sqlite3"
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/pme/clean/save", methods=["POST"])
    def save_cleaned_db_to():
        """Copy the generated cleaned DB to a user-specified path."""
        try:
            import shutil
            req_data = request.json or {}
            source = req_data.get("source", "")
            destination = req_data.get("destination", "")
            if not source:
                source = get_cleaned_db()
            source = os.path.expanduser(source)
            destination = os.path.expanduser(destination)
            
            if not os.path.exists(source):
                return jsonify({"success": False, "message": "Source DB not found. Please run cleaning first."}), 404
            if not destination:
                return jsonify({"success": False, "message": "No destination path specified."}), 400
                
            # Create parent directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.copy2(source, destination)
            return jsonify({
                "success": True,
                "message": f"Saved to {destination}",
                "path": destination
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    # ── Screenpipe Pipes ───────────────────────────────────────────

    @app.route("/api/screenpipe/pipes")
    def screenpipe_pipes():
        pipes = []
        pipes_dir = os.path.expanduser(os.path.join(os.path.dirname(get_sp_db()), "pipes")) if get_sp_db() else os.path.expanduser("~/.screenpipe/pipes")
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
        pipes_dir = os.path.expanduser(os.path.join(os.path.dirname(get_sp_db()), "pipes")) if get_sp_db() else os.path.expanduser("~/.screenpipe/pipes")
        pipe_path = os.path.join(pipes_dir, name)
        disabled_flag = os.path.join(pipe_path, ".disabled")
        if os.path.exists(disabled_flag):
            os.remove(disabled_flag)
        return jsonify({"message": f"Pipe '{name}' enabled"})

    @app.route("/api/screenpipe/pipes/<name>/disable", methods=["POST"])
    def screenpipe_pipe_disable(name):
        pipes_dir = os.path.expanduser(os.path.join(os.path.dirname(get_sp_db()), "pipes")) if get_sp_db() else os.path.expanduser("~/.screenpipe/pipes")
        pipe_path = os.path.join(pipes_dir, name)
        if os.path.isdir(pipe_path):
            disabled_flag = os.path.join(pipe_path, ".disabled")
            with open(disabled_flag, "w") as f:
                f.write("")
            return jsonify({"message": f"Pipe '{name}' disabled"})
        return jsonify({"error": "Pipe not found"}), 404

    # ── Stats ──────────────────────────────────────────────────────

    @app.route("/api/stats/summary")
    def stats_summary():
        stats = {
            "total_captures": 0,
            "storage_mb": 0,
            "daily_captures": 0,
            "weekly_captures": 0,
            "db_source": "none",
        }
        db_path = None
        oc_db = get_oc_db()
        sp_db = get_sp_db()
        if oc_db and os.path.exists(os.path.expanduser(oc_db)):
            db_path = os.path.expanduser(oc_db)
            stats["db_source"] = "openchronicle"
        elif sp_db and os.path.exists(os.path.expanduser(sp_db)):
            db_path = os.path.expanduser(sp_db)
            stats["db_source"] = "screenpipe"

        if db_path:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Total captures
                try:
                    if stats["db_source"] == "screenpipe":
                        cursor.execute("SELECT COUNT(*) FROM frames")
                    else:
                        cursor.execute("SELECT COUNT(*) FROM captures")
                    stats["total_captures"] = cursor.fetchone()[0]
                except Exception:
                    pass

                # Daily captures (today)
                try:
                    today = datetime.now().strftime("%Y-%m-%d")
                    if stats["db_source"] == "screenpipe":
                        cursor.execute(
                            "SELECT COUNT(*) FROM frames WHERE date(timestamp) = ?",
                            (today,),
                        )
                    else:
                        cursor.execute(
                            "SELECT COUNT(*) FROM captures WHERE date(timestamp) = ?",
                            (today,),
                        )
                    stats["daily_captures"] = cursor.fetchone()[0]
                except Exception:
                    pass

                # Weekly captures
                try:
                    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                    if stats["db_source"] == "screenpipe":
                        cursor.execute(
                            "SELECT COUNT(*) FROM frames WHERE timestamp >= ?",
                            (week_ago,),
                        )
                    else:
                        cursor.execute(
                            "SELECT COUNT(*) FROM captures WHERE timestamp >= ?",
                            (week_ago,),
                        )
                    stats["weekly_captures"] = cursor.fetchone()[0]
                except Exception:
                    pass

                conn.close()

                # Storage size in MB
                db_size = os.path.getsize(db_path)
                stats["storage_mb"] = round(db_size / (1024 * 1024), 2)
            except Exception:
                pass

        return jsonify(stats)

    # ── Timeline ───────────────────────────────────────────────────

    @app.route("/api/timeline")
    def timeline():
        date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
        limit = int(request.args.get("limit", "50"))
        events = []

        db_path = None
        oc_db = get_oc_db()
        sp_db = get_sp_db()
        if oc_db and os.path.exists(os.path.expanduser(oc_db)):
            db_path = os.path.expanduser(oc_db)
        elif sp_db and os.path.exists(os.path.expanduser(sp_db)):
            db_path = os.path.expanduser(sp_db)

        if db_path:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                if "db.sqlite" in db_path or "screenpipe" in db_path:
                    cursor.execute(
                        """
                        SELECT datetime(f.timestamp) as ts,
                               COALESCE(o.app_name, 'Unknown') as app_name,
                               GROUP_CONCAT(o.text, ' ') as ocr_text
                        FROM frames f
                        LEFT JOIN ocr_text o ON o.frame_id = f.id
                        WHERE date(f.timestamp) = ?
                        GROUP BY f.id
                        ORDER BY f.timestamp DESC
                        LIMIT ?
                        """,
                        (date, limit),
                    )
                    for row in cursor.fetchall():
                        events.append({
                            "time": row[0],
                            "app_name": row[1] or "Unknown",
                            "type": "capture",
                            "text": (row[2] or "")[:300],
                        })
                else:
                    cursor.execute(
                        """
                        SELECT datetime(timestamp) as ts, app_name,
                               window_title, visible_text
                        FROM captures
                        WHERE date(timestamp) = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                        """,
                        (date, limit),
                    )
                    for row in cursor.fetchall():
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

