from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - dependency is declared in requirements.txt
    yaml = None


PORT = 5555

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SMGUI_DATA_DIR = str(PROJECT_ROOT / "smgui")
Path(SMGUI_DATA_DIR).mkdir(parents=True, exist_ok=True)

CONFIG_PATH = os.path.join(SMGUI_DATA_DIR, "config.yaml")
OUTPUT_DB = os.path.join(SMGUI_DATA_DIR, "memory.db")
SCHEDULE_STATE_PATH = os.path.join(SMGUI_DATA_DIR, "schedule_state.json")
PIPELINE_LOCK_FILE = os.path.join(SMGUI_DATA_DIR, ".pipeline.lock")


SCREEN_MEMORY_DEFAULTS: Dict[str, Any] = {
    "enabled": True,
    "output_db": "",
    "fact_extraction_interval_minutes": 30,
    "observation_interval_hours": 2,
    "task_interval_hours": 4,
    "initial_lookback_minutes": 30,
    "openchronicle": {
        "record_link_window_seconds": 6,
        "max_events_per_record": 3,
    },
    "cleaning_policy": {
        "active_interval": 2,
        "bg_interval": 30,
        "ax_trigger_interval": 10,
        "min_quality": 0.18,
        "ignored_apps": [
            "控制中心",
            "通知中心",
            "程序坞",
            "Control Center",
            "Notification Center",
            "Dock",
        ],
        "system_apps_keep_if_focused": ["系统设置", "System Settings"],
        "min_useful_chars": 8,
    },
    "view_generation": {
        "gap_minutes": 8,
        "max_minutes": 30,
    },
    "screen_fact_generation": {
        "enabled": True,
        "enable_LLM": True,
        "fallback_fact_when_llm_fails": False,
        "fact_llm_budget": 400,
        "llm_timeout": 120,
    },
    "window_workstream_generation": {
        "enabled": True,
        "enable_LLM_summary": False,
        "min_relevance": 0.35,
        "title_similarity_threshold": 0.82,
        "max_member_views_for_matching": 12,
        "max_views_for_summary": 24,
        "pair_min_score": 0.45,
        "min_support_ratio": 0.5,
        "top_k": 3,
        "min_top_k_avg": 0.55,
        "cluster_seed_min_score": 0.65,
        "cluster_merge_passes": 1,
        "cluster_merge_support_ratio": 0.5,
        "cluster_merge_min_score": 0.35,
        "max_time_gap_days": 30,
        "primary_match_since": "current_week",
        "historical_min_entity_overlap": 2,
        "llm_budget": 0,
        "llm_timeout": 120,
    },
    "screen_observation_generation": {
        "enabled": True,
        "enable_LLM_observation_generation": True,
        "fallback_observation_when_llm_fails": True,
        "fact_cluster_min_score": 0.42,
        "observation_min_fact_count": 1,
        "observation_merge_fact_min_score": 0.42,
        "observation_merge_min_score": 0.48,
        "observation_merge_support_ratio": 0.5,
        "observation_llm_budget": 200,
        "llm_timeout": 120,
    },
    "task_workstream_generation": {
        "enabled": True,
        "enable_LLM_observation_matching": True,
        "enable_LLM_task_profile_update": True,
        "observation_match_llm_budget": 50,
        "task_profile_llm_budget": 50,
        "observation_match_candidate_top_k": 8,
        "observation_match_min_score": 0.58,
        "observation_match_low_confidence_floor": 0.5,
        "min_observations_to_create_task": 2,
        "max_observations_per_run": 200,
        "llm_timeout": 120,
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _load_embedding_config(config: Dict[str, Any]) -> Dict[str, Any]:
    raw = config.get("embedding", {})
    if not isinstance(raw, dict):
        return {"enabled": False, "api_key_env": "EMBEDDING_API_KEY"}

    embedding = copy.deepcopy(raw)
    if "enabled" not in embedding:
        embedding["enabled"] = bool(
            embedding.get("model") and embedding.get("base_url")
        )
    embedding.setdefault("api_key_env", "EMBEDDING_API_KEY")
    return embedding


def resolve_api_key(config: Dict[str, Any], *, default_env: str = "") -> str:
    api_key = str(config.get("api_key") or "").strip()
    if api_key:
        return api_key

    env_name = str(config.get("api_key_env") or default_env or "").strip()
    if env_name:
        return os.environ.get(env_name, "").strip()
    return ""


def _parse_simple_yaml_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"''", '""'}:
        return ""
    if (value[0], value[-1]) in {("'", "'"), ('"', '"')}:
        return value[1:-1]
    lower_value = value.lower()
    if lower_value == "true":
        return True
    if lower_value == "false":
        return False
    if lower_value in {"null", "~"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _load_simple_yaml(path: str) -> Dict[str, Any]:
    """Small fallback for the flat, two-level GUI config used by smgui."""
    root: Dict[str, Any] = {}
    current_section: Dict[str, Any] | None = None
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if indent == 0:
                if value:
                    root[key] = _parse_simple_yaml_scalar(value)
                    current_section = None
                else:
                    section: Dict[str, Any] = {}
                    root[key] = section
                    current_section = section
            elif current_section is not None:
                current_section[key] = _parse_simple_yaml_scalar(value)
    return root


def load_gui_config() -> Dict[str, Any]:
    try:
        if yaml is None:
            return _load_simple_yaml(CONFIG_PATH)
        with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except OSError:
        data = {}
    except Exception:
        data = {}
    return data if isinstance(data, dict) else {}


def load_screen_memory_config(config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if config is None:
        config = load_gui_config()
    config = config if isinstance(config, dict) else {}
    raw = copy.deepcopy(config.get("screen_memory", {}))
    database = config.get("database", {})
    if isinstance(database, dict):
        if "screenpipe_db" in database:
            raw["screenpipe_db"] = database["screenpipe_db"]
        if "openchronicle_db" in database:
            raw["openchronicle_db"] = database["openchronicle_db"]
        if "cleaned_db" in database:
            raw["output_db"] = database["cleaned_db"]

    if "ingest_interval_minutes" in raw and "fact_extraction_interval_minutes" not in raw:
        raw["fact_extraction_interval_minutes"] = raw["ingest_interval_minutes"]
    if "fact_clustering_interval_hours" in raw and "observation_interval_hours" not in raw:
        raw["observation_interval_hours"] = raw["fact_clustering_interval_hours"]

    settings = _deep_merge(SCREEN_MEMORY_DEFAULTS, raw)
    settings.setdefault("screenpipe_db", "")
    settings.setdefault("openchronicle_db", "")
    output_db = settings.get("output_db")
    if not output_db:
        output_db = OUTPUT_DB
    else:
        output_db = Path(output_db).expanduser()
        if not output_db.is_absolute():
            output_db = PROJECT_ROOT / output_db
    settings["screenpipe_db"] = os.path.expanduser(str(settings.get("screenpipe_db") or ""))
    settings["openchronicle_db"] = os.path.expanduser(str(settings.get("openchronicle_db") or ""))
    settings["output_db"] = str(Path(output_db).expanduser())

    # Preserve the PME cleaner's original section names internally.
    return {
        "enabled": bool(settings.get("enabled")),
        "schedule": {
            "fact_extraction_interval_minutes": settings["fact_extraction_interval_minutes"],
            "observation_interval_hours": settings["observation_interval_hours"],
            "task_interval_hours": settings["task_interval_hours"],
            "initial_lookback_minutes": settings["initial_lookback_minutes"],
        },
        "database": {
            "screenpipe_db": settings["screenpipe_db"],
            "openchronicle_db": settings["openchronicle_db"],
            "cleaned_db": settings["output_db"],
        },
        "openchronicle": settings["openchronicle"],
        "cleaning_policy": settings["cleaning_policy"],
        "view_generation": settings["view_generation"],
        "window_workstream_generation": settings["window_workstream_generation"],
        "task_workstream_generation": settings["task_workstream_generation"],
        "screen_fact_generation": settings["screen_fact_generation"],
        "screen_observation_generation": settings["screen_observation_generation"],
        "embedding": _load_embedding_config(config),
    }
