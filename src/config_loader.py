import os
import sqlite3
import subprocess
import yaml

def load_yaml_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    return config

def get_config():
    config = load_yaml_config()
    
    # 1. Expand all database paths (e.g. ~/ -> /Users/username/)
    db_cfg = config.get("database", {})
    for key in ["screenpipe_db", "openchronicle_db", "cleaned_db"]:
        if key in db_cfg and db_cfg[key]:
            db_cfg[key] = os.path.expanduser(db_cfg[key])
            
    # Expand openchronicle binary path
    oc_cfg = config.get("openchronicle", {})
    if "bin_path" in oc_cfg and oc_cfg["bin_path"]:
        oc_cfg["bin_path"] = os.path.expanduser(oc_cfg["bin_path"])
        
    # Expand screenpipe binary path
    sp_cfg = config.get("screenpipe", {})
    if "bin_path" in sp_cfg and sp_cfg["bin_path"]:
        sp_cfg["bin_path"] = os.path.expanduser(sp_cfg["bin_path"])
        
    # 2. Automatically retrieve Screenpipe Token if not configured in yaml
    if not sp_cfg.get("api_token"):
        # Let's try running screenpipe auth token
        bin_path = sp_cfg.get("bin_path", "/opt/homebrew/bin/screenpipe")
        if os.path.exists(bin_path):
            try:
                result = subprocess.run([bin_path, "auth", "token"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    sp_cfg["api_token"] = result.stdout.strip()
            except Exception:
                pass
                
        # Last resort: Try loading from secrets table in screenpipe db
        if not sp_cfg.get("api_token") and os.path.exists(db_cfg.get("screenpipe_db", "")):
            try:
                conn = sqlite3.connect(db_cfg["screenpipe_db"])
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM secrets WHERE key = 'api_auth_key' LIMIT 1")
                row = cursor.fetchone()
                conn.close()
                if row and row[0]:
                    import base64
                    val = row[0]
                    # Check if base64 or plaintext
                    if val.startswith("sp-"):
                        sp_cfg["api_token"] = val
                    else:
                        try:
                            decoded = base64.b64decode(val).decode("utf-8")
                            if decoded.startswith("sp-"):
                                sp_cfg["api_token"] = decoded
                        except Exception:
                            pass
            except Exception:
                pass
                
    return config
