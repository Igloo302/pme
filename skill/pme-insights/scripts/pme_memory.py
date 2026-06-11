#!/usr/bin/env python3
"""Locate a PME database and extract bounded, traceable work evidence."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


REQUIRED_COLUMNS = {
    "records": {"id", "timestamp"},
    "screen_facts": {"id", "fact_text", "evidence_record_ids_json"},
    "screen_observations": {
        "id",
        "summary_text",
        "progress_text",
        "evidence_record_ids_json",
    },
}
SUPPORTING_TABLES = {"window_workstream", "segments", "views"}
DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.json"
JSON_FIELDS = {
    "blockers_json",
    "next_actions_json",
    "key_points_json",
    "decisions_json",
    "entities_json",
    "artifacts_json",
    "evidence_record_ids_json",
    "evidence_view_ids_json",
    "evidence_window_workstream_ids_json",
    "evidence_ids_json",
    "topics_json",
    "app_names_json",
    "window_titles_json",
}


class PmeError(RuntimeError):
    pass


def _connect_readonly(path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(path.resolve()))}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    quoted = table.replace('"', '""')
    return {
        row["name"]
        for row in connection.execute(f'PRAGMA table_info("{quoted}")')
    }


def _database_times(connection: sqlite3.Connection) -> tuple[str | None, str | None]:
    row = connection.execute(
        "SELECT MIN(timestamp) AS first_at, MAX(timestamp) AS last_at FROM records"
    ).fetchone()
    return row["first_at"], row["last_at"]


def validate_database(path: Path | str) -> dict[str, Any]:
    candidate = Path(path).expanduser()
    result: dict[str, Any] = {
        "path": str(candidate.resolve(strict=False)),
        "valid": False,
        "missing_tables": [],
        "missing_columns": {},
    }
    if not candidate.is_file():
        result["error"] = "file_not_found"
        return result

    try:
        with _connect_readonly(candidate) as connection:
            integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
            if integrity != "ok":
                result["error"] = f"sqlite_quick_check:{integrity}"
                return result
            tables = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            missing_tables = sorted(set(REQUIRED_COLUMNS) - tables)
            missing_columns: dict[str, list[str]] = {}
            for table, required in REQUIRED_COLUMNS.items():
                if table not in tables:
                    continue
                absent = sorted(required - _table_columns(connection, table))
                if absent:
                    missing_columns[table] = absent
            result["missing_tables"] = missing_tables
            result["missing_columns"] = missing_columns
            if missing_tables or missing_columns:
                result["error"] = "schema_mismatch"
                return result

            first_at, last_at = _database_times(connection)
            result.update(
                {
                    "valid": True,
                    "first_record_at": first_at,
                    "last_record_at": last_at,
                    "record_count": connection.execute(
                        "SELECT COUNT(*) FROM records"
                    ).fetchone()[0],
                    "available_tables": sorted(
                        (set(REQUIRED_COLUMNS) | SUPPORTING_TABLES) & tables
                    ),
                    "size_bytes": candidate.stat().st_size,
                    "modified_at": datetime.fromtimestamp(
                        candidate.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                }
            )
            return result
    except (sqlite3.Error, OSError) as exc:
        result["error"] = f"{type(exc).__name__}:{exc}"
        return result


def _load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PmeError(f"Invalid config {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PmeError(f"Invalid config {config_path}: expected a JSON object")
    return data


def _write_config(
    config_path: Path, database: dict[str, Any]
) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "database_path": database["path"],
        "last_verified_at": datetime.now(timezone.utc).isoformat(),
        "database_identity": {
            "required_tables": sorted(REQUIRED_COLUMNS),
            "first_record_at": database.get("first_record_at"),
            "last_record_at": database.get("last_record_at"),
            "record_count": database.get("record_count"),
        },
    }
    temporary = config_path.with_suffix(config_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(config_path)


def resolve_database(
    explicit_db: Path | str | None = None,
    config_path: Path | str | None = None,
) -> dict[str, Any]:
    config_file = Path(
        os.environ.get("PME_INSIGHTS_CONFIG")
        or config_path
        or DEFAULT_CONFIG
    ).expanduser()
    config = _load_config(config_file)

    override = explicit_db or os.environ.get("PME_MEMORY_DB")
    requested = override or config.get("database_path")
    if requested:
        validation = validate_database(Path(requested))
        if validation["valid"]:
            _write_config(config_file, validation)
            return {
                "status": "ok",
                "database_path": validation["path"],
                "config_path": str(config_file.resolve(strict=False)),
                "config_updated": config.get("database_path") != validation["path"],
                "validation": validation,
            }
        if override:
            return {
                "status": "invalid",
                "requested_path": str(Path(requested).expanduser()),
                "config_path": str(config_file.resolve(strict=False)),
                "validation": validation,
            }
        return {
            "status": "missing",
            "configured_path": str(Path(requested).expanduser()),
            "config_path": str(config_file.resolve(strict=False)),
            "validation": validation,
            "action": "Ask the user for the new PME memory.db path, then run configure --db PATH.",
        }
    return {
        "status": "unconfigured",
        "config_path": str(config_file.resolve(strict=False)),
        "action": "Ask the user for the PME memory.db path, then run configure --db PATH.",
    }


def _decode_json_fields(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    for field in JSON_FIELDS & item.keys():
        value = item[field]
        if not value:
            item[field] = []
            continue
        try:
            item[field] = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            item[field] = value
    return item


def _select_existing(
    connection: sqlite3.Connection,
    table: str,
    desired_columns: list[str],
    where: str,
    parameters: tuple[Any, ...],
    limit: int,
) -> list[dict[str, Any]]:
    columns = _table_columns(connection, table)
    selected = [column for column in desired_columns if column in columns]
    if not selected:
        return []
    quoted = ", ".join(f'"{column}"' for column in selected)
    rows = connection.execute(
        f'SELECT {quoted} FROM "{table}" WHERE {where} '
        f"ORDER BY 1 DESC LIMIT ?",
        (*parameters, limit),
    )
    return [_decode_json_fields(row) for row in rows]


def _time_overlap_expression(
    columns: set[str],
    pairs: list[tuple[str, str]],
    fallbacks: list[str] | None = None,
) -> str:
    for start_column, end_column in pairs:
        if start_column in columns and end_column in columns:
            return (
                f'COALESCE("{end_column}", "{start_column}") >= ? '
                f'AND COALESCE("{start_column}", "{end_column}") < ?'
            )
    for column in fallbacks or []:
        if column in columns:
            return f'"{column}" >= ? AND "{column}" < ?'
    raise PmeError("PME table has no supported time columns")


def _count_values(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counter = Counter(
        str(item[key])
        for item in items
        if item.get(key) not in (None, "", "unknown", "general")
    )
    return dict(counter.most_common())


def _annotate_fact_attribution(fact: dict[str, Any]) -> dict[str, Any]:
    app = str(fact.get("app_name") or "").lower()
    window = str(fact.get("window_title") or "").lower()
    browser_source = any(
        marker in app
        for marker in ("edge", "chrome", "safari", "firefox", "浏览器")
    )
    external_content = any(
        marker in window
        for marker in (
            "github",
            "release",
            "amazon",
            "京东",
            "search",
            "搜索",
            "news",
        )
    )
    action_like = fact.get("fact_kind") in {"action", "result", "decision"}
    implementation_like = fact.get("work_type") in {
        "implementation",
        "debugging",
        "configuration",
        "documentation",
    }
    risk = browser_source and (external_content or action_like or implementation_like)
    fact["attribution_risk"] = risk
    if risk:
        fact["attribution_risk_reason"] = (
            "Action-like fact was derived from browser content. Verify that it "
            "describes the user's work rather than a viewed page or changelog."
        )
    return fact


def extract_evidence(
    database_path: Path | str,
    start: str,
    end: str,
    limit: int = 500,
) -> dict[str, Any]:
    database = Path(database_path).expanduser()
    validation = validate_database(database)
    if not validation["valid"]:
        raise PmeError(f"Not a valid PME database: {validation}")

    with _connect_readonly(database) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        observation_columns = _table_columns(connection, "screen_observations")
        observations = _select_existing(
            connection,
            "screen_observations",
            [
                "id",
                "period_start",
                "period_end",
                "title",
                "summary_text",
                "progress_text",
                "project_key",
                "objective_key",
                "work_type",
                "category",
                "key_points_json",
                "decisions_json",
                "blockers_json",
                "next_actions_json",
                "evidence_view_ids_json",
                "evidence_record_ids_json",
                "evidence_window_workstream_ids_json",
                "confidence",
            ],
            _time_overlap_expression(
                observation_columns,
                [("period_start", "period_end")],
                ["created_at", "updated_at"],
            ),
            (start, end),
            limit,
        )
        fact_columns = _table_columns(connection, "screen_facts")
        facts = _select_existing(
            connection,
            "screen_facts",
            [
                "id",
                "fact_text",
                "fact_type",
                "fact_kind",
                "work_type",
                "project_key",
                "objective_key",
                "start_timestamp",
                "end_timestamp",
                "app_name",
                "window_title",
                "evidence_record_ids_json",
                "confidence",
            ],
            _time_overlap_expression(
                fact_columns,
                [("start_timestamp", "end_timestamp")],
                ["created_at", "updated_at"],
            ),
            (start, end),
            limit,
        )
        facts = [_annotate_fact_attribution(fact) for fact in facts]
        workstreams = (
            _select_existing(
                connection,
                "window_workstream",
                [
                    "id",
                    "title",
                    "summary",
                    "category",
                    "start_timestamp",
                    "end_timestamp",
                    "view_count",
                    "segment_count",
                    "confidence",
                ],
                "end_timestamp >= ? AND start_timestamp < ?",
                (start, end),
                limit,
            )
            if "window_workstream" in tables
            else []
        )
        segments = (
            _select_existing(
                connection,
                "segments",
                [
                    "id",
                    "start_timestamp",
                    "end_timestamp",
                    "duration_seconds",
                    "activity_type",
                    "project_hint",
                    "summary",
                    "actions_json",
                    "artifacts_json",
                    "evidence_ids_json",
                    "confidence",
                ],
                "end_timestamp >= ? AND start_timestamp < ?",
                (start, end),
                limit,
            )
            if "segments" in tables
            else []
        )
        views = (
            _select_existing(
                connection,
                "views",
                [
                    "id",
                    "start_timestamp",
                    "end_timestamp",
                    "app_name",
                    "window_title",
                    "content_kind",
                    "representative_text",
                    "evidence_ids_json",
                    "confidence",
                ],
                "end_timestamp >= ? AND start_timestamp < ?",
                (start, end),
                limit,
            )
            if "views" in tables
            else []
        )
        record_columns = _table_columns(connection, "records")
        group_columns = [
            column
            for column in ("app_name", "content_kind")
            if column in record_columns
        ]
        if group_columns:
            group_sql = ", ".join(f'"{column}"' for column in group_columns)
            record_stats = [
                dict(row)
                for row in connection.execute(
                    f"""
                    SELECT {group_sql}, COUNT(*) AS record_count,
                           MIN(timestamp) AS first_at, MAX(timestamp) AS last_at
                    FROM records
                    WHERE timestamp >= ? AND timestamp < ?
                    GROUP BY {group_sql}
                    ORDER BY record_count DESC
                    LIMIT 100
                    """,
                    (start, end),
                )
            ]
        else:
            record_stats = []

    if observations:
        primary_source = "screen_observations"
    elif facts:
        primary_source = "screen_facts"
    elif workstreams:
        primary_source = "window_workstream"
    elif segments:
        primary_source = "segments"
    elif views:
        primary_source = "views"
    else:
        primary_source = "none"

    duration_by_activity: Counter[str] = Counter()
    duration_by_project: Counter[str] = Counter()
    for segment in segments:
        duration = int(segment.get("duration_seconds") or 0)
        if segment.get("activity_type"):
            duration_by_activity[str(segment["activity_type"])] += duration
        if segment.get("project_hint") not in (None, "", "unknown", "general"):
            duration_by_project[str(segment["project_hint"])] += duration

    return {
        "database": validation,
        "period": {"start": start, "end": end},
        "primary_source": primary_source,
        "source_counts": {
            "observations": len(observations),
            "facts": len(facts),
            "workstreams": len(workstreams),
            "segments": len(segments),
            "views": len(views),
        },
        "attention_summary": {
            "segment_seconds_by_activity": dict(duration_by_activity.most_common()),
            "segment_seconds_by_project": dict(duration_by_project.most_common()),
            "observation_projects": _count_values(observations, "project_key"),
            "observation_work_types": _count_values(observations, "work_type"),
            "fact_projects": _count_values(facts, "project_key"),
            "fact_work_types": _count_values(facts, "work_type"),
            "record_groups": record_stats,
        },
        "observations": observations,
        "facts": facts,
        "workstreams": workstreams,
        "segments": segments,
        "views": views,
        "warnings": (
            []
            if observations
            else [
                "screen_observations has no rows in this period; "
                f"using {primary_source} as the highest available evidence layer."
            ]
        ),
    }


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def _default_period(days: int) -> tuple[str, str]:
    end = datetime.now().astimezone()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Locate a PME memory.db and extract traceable evidence."
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Config path (default: skill/config.json or PME_INSIGHTS_CONFIG).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    configure = subparsers.add_parser("configure")
    configure.add_argument("--db", type=Path, required=True)

    status = subparsers.add_parser("status")
    status.add_argument("--db", type=Path)

    extract = subparsers.add_parser("extract")
    extract.add_argument("--db", type=Path)
    extract.add_argument("--start")
    extract.add_argument("--end")
    extract.add_argument("--days", type=int, default=7)
    extract.add_argument("--limit", type=int, default=500)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = args.config or DEFAULT_CONFIG
    try:
        result = resolve_database(
            explicit_db=getattr(args, "db", None),
            config_path=config_path,
        )
        if args.command in {"configure", "status"}:
            _print_json(result)
            return 0 if result["status"] == "ok" else 2
        if result["status"] != "ok":
            _print_json(result)
            return 2

        if args.start or args.end:
            if not (args.start and args.end):
                raise PmeError("--start and --end must be supplied together")
            start = _parse_time(args.start).isoformat()
            end = _parse_time(args.end).isoformat()
        else:
            start, end = _default_period(args.days)
        payload = extract_evidence(
            result["database_path"],
            start=start,
            end=end,
            limit=args.limit,
        )
        payload["resolution"] = result
        _print_json(payload)
        return 0
    except PmeError as exc:
        _print_json({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
