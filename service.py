from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from smgui.cleaner import ScreenMemoryCleaner, load_screen_memory_config
from smgui.config import OUTPUT_DB, SCHEDULE_STATE_PATH, CONFIG_PATH, PIPELINE_LOCK_FILE

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_PIPELINE_LOCK_FILE = PIPELINE_LOCK_FILE


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_state_time(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_state() -> Dict[str, Any]:
    path = Path(SCHEDULE_STATE_PATH)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(state: Dict[str, Any]) -> None:
    path = Path(SCHEDULE_STATE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _is_due(last_run: Any, now: datetime, interval: timedelta) -> bool:
    previous = _parse_state_time(last_run)
    return previous is None or now - previous >= interval


def resolve_llm_client() -> Optional[Any]:
    import os
    import yaml
    from openai import OpenAI
    
    config_path = CONFIG_PATH
    
    provider = "openai-codex"
    base_url = "https://chatgpt.com/backend-api/codex"
    api_key = ""
    
    # Load config to see if there's custom provider
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                cfg = yaml.safe_load(f) or {}
                model_sec = cfg.get('model', {})
                if model_sec.get('provider'):
                    provider = model_sec.get('provider')
                if model_sec.get('base_url'):
                    base_url = model_sec.get('base_url')
                if model_sec.get('api_key'):
                    api_key = model_sec.get('api_key')
        except Exception:
            pass
            
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or "dummy"
            
    try:
        return OpenAI(base_url=base_url, api_key=api_key)
    except Exception as exc:
        logger.warning("Could not create local PME LLM client: %s", exc)
        return None


def _run_ingest(
    cleaner: ScreenMemoryCleaner,
    state: Dict[str, Any],
    now: datetime,
    custom_start_time: Optional[datetime] = None,
    custom_end_time: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    schedule = cleaner.config.get("schedule", {})
    if custom_start_time:
        previous = custom_start_time
    else:
        previous = _parse_state_time(state.get("last_ingest_at"))
        if previous is None:
            previous = now - timedelta(
                minutes=max(1, int(schedule.get("initial_lookback_minutes", 30)))
            )
            
    end = custom_end_time if custom_end_time else now
    
    stats = cleaner.clean(
        start_time_str=previous.isoformat(),
        end_time_str=end.isoformat(),
        incremental=True,
        generate_screen_facts=True,
        update_window_workstreams=True,
    )
    if stats is not None and not custom_start_time:
        state["last_ingest_at"] = now.isoformat()
        state["last_ingest_stats"] = stats
    return stats


def _run_fact_clustering(
    cleaner: ScreenMemoryCleaner,
    state: Dict[str, Any],
    now: datetime,
) -> Dict[str, Any]:
    connection = cleaner.ensure_cleaned_db()
    try:
        stats = cleaner.update_screen_fact_cluster_tables(connection)
    finally:
        connection.close()
    state["last_fact_clustering_at"] = now.isoformat()
    state["last_fact_clustering_stats"] = stats
    return stats


def _run_observations(
    cleaner: ScreenMemoryCleaner,
    state: Dict[str, Any],
    now: datetime,
) -> Dict[str, Any]:
    connection = cleaner.ensure_cleaned_db()
    try:
        cluster_stats = cleaner.update_screen_fact_cluster_tables(connection)
        observation_stats = cleaner.update_screen_observation_tables(connection, None)
    finally:
        connection.close()
    stats = {
        "fact_clustering": cluster_stats,
        "observations": observation_stats,
    }
    state["last_observation_at"] = now.isoformat()
    state["last_observation_stats"] = stats
    return stats


def run_screen_memory_due_work(
    *,
    now: Optional[datetime] = None,
    force_phase: Optional[str] = None,
    custom_start_time: Optional[datetime] = None,
    custom_end_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    cleaner_config = load_screen_memory_config()
    if not cleaner_config.get("enabled") and not custom_start_time:
        return {"status": "disabled"}

    # Acquire lock using a file lock
    lock_dir = Path(_PIPELINE_LOCK_FILE).parent
    lock_dir.mkdir(parents=True, exist_ok=True)
    
    if not _LOCK.acquire(blocking=False):
        return {"status": "busy", "message": "Pipeline lock is held by another thread"}
        
    lock_handle = open(_PIPELINE_LOCK_FILE, "a+")
    try:
        try:
            import fcntl
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                _LOCK.release()
                return {"status": "busy", "message": "Pipeline lock is held by another process"}
        except (ImportError, OSError):
            # Fallback or busy check
            pass

        state = _load_state()
        current = (now or _utc_now()).astimezone(timezone.utc)
        schedule = cleaner_config.get("schedule", {})

        ingest_due = custom_start_time is not None or force_phase == "ingest" or (
            force_phase is None
            and _is_due(
                state.get("last_ingest_at"),
                current,
                timedelta(minutes=max(1, int(schedule["ingest_interval_minutes"]))),
            )
        )
        cluster_due = force_phase == "cluster" or (
            force_phase is None
            and _is_due(
                state.get("last_fact_clustering_at"),
                current,
                timedelta(hours=max(1, int(schedule["fact_clustering_interval_hours"]))),
            )
        )
        observation_due = force_phase == "observation" or (
            force_phase is None
            and _is_due(
                state.get("last_observation_at"),
                current,
                timedelta(hours=max(1, int(schedule["observation_interval_hours"]))),
            )
        )
        
        if not any((ingest_due, cluster_due, observation_due)):
            return {
                "status": "ok",
                "phases": {},
                "output_db": cleaner_config["database"]["cleaned_db"],
            }

        llm_client = resolve_llm_client()
        cleaner = ScreenMemoryCleaner(
            cleaner_config,
            llm_client=llm_client,
            quiet=True,
        )
        
        phases: Dict[str, Any] = {}
        if ingest_due:
            phases["ingest"] = _run_ingest(
                cleaner, 
                state, 
                current,
                custom_start_time=custom_start_time,
                custom_end_time=custom_end_time
            )
            if not custom_start_time:
                _save_state(state)
        if cluster_due:
            phases["fact_clustering"] = _run_fact_clustering(
                cleaner,
                state,
                current,
            )
            _save_state(state)
        if observation_due:
            phases["observations"] = _run_observations(cleaner, state, current)
            _save_state(state)

        return {
            "status": "ok",
            "phases": phases,
            "output_db": cleaner.cleaned_db,
        }
    except Exception as e:
        logger.exception("Screen memory pipeline failed: %s", e)
        return {"status": "error", "message": str(e)}
    finally:
        lock_handle.close()
        try:
            _LOCK.release()
        except RuntimeError:
            pass
