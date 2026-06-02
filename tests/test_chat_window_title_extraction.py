#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OPENCHRONICLE_DB = REPO_ROOT / "openchronicle.db"
DEFAULT_OUTPUT_DB = Path(__file__).resolve().parent / "chat_window_title_extraction_results.db"


def import_cleaner_module():
    sys.path.insert(0, str(REPO_ROOT))
    try:
        import yaml  # noqa: F401
    except ModuleNotFoundError:
        stub = types.ModuleType("src.config_loader")
        stub.get_config = lambda: {}
        sys.modules["src.config_loader"] = stub

    from src import cleaner

    return cleaner


def ensure_result_schema(conn, reset=True):
    cursor = conn.cursor()
    if reset:
        cursor.execute("DROP TABLE IF EXISTS chat_window_title_extraction_results")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_window_title_extraction_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_capture_id TEXT,
            timestamp TEXT,
            app_name TEXT,
            original_window_title TEXT,
            extracted_window_title TEXT,
            original_visible_text TEXT,
            context_json TEXT,
            extraction_status TEXT
        );
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chat_title_results_app
        ON chat_window_title_extraction_results(app_name);
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chat_title_results_extracted
        ON chat_window_title_extraction_results(extracted_window_title);
        """
    )
    conn.commit()


def iter_chat_captures(openchronicle_db):
    conn = sqlite3.connect(openchronicle_db)
    conn.row_factory = sqlite3.Row
    try:
        yield from conn.execute(
            """
            SELECT id, timestamp, app_name, bundle_id, window_title,
                   focused_role, focused_value, visible_text, url
            FROM captures
            WHERE app_name IN ('Feishu', 'WeChat')
               OR app_name LIKE '%飞书%'
               OR app_name LIKE '%微信%'
               OR lower(app_name) LIKE '%feishu%'
               OR lower(app_name) LIKE '%wechat%'
               OR lower(bundle_id) LIKE '%lark%'
               OR lower(bundle_id) LIKE '%wechat%'
               OR lower(bundle_id) LIKE '%xinwechat%'
            ORDER BY timestamp ASC, id ASC
            """
        )
    finally:
        conn.close()


def is_feishu_capture(cleaner, row):
    return cleaner.is_feishu_app(row["app_name"], row["bundle_id"], None)


def is_wechat_capture(cleaner, row):
    return cleaner.is_wechat_app(row["app_name"], row["bundle_id"], None)


def extract_chat_window_title(cleaner, row):
    visible_text = row["visible_text"] or ""
    context = None
    if is_feishu_capture(cleaner, row):
        context = cleaner.extract_feishu_messenger_chat_context(visible_text)
    elif is_wechat_capture(cleaner, row):
        context = cleaner.extract_wechat_chat_context(visible_text)

    extracted_title = cleaner.app_context_title(context)
    status = "ok" if extracted_title else "missing_title"
    return extracted_title, context, status


def write_results(openchronicle_db, output_db, reset=True, limit=None):
    cleaner = import_cleaner_module()
    output_db.parent.mkdir(parents=True, exist_ok=True)
    output_conn = sqlite3.connect(output_db)
    ensure_result_schema(output_conn, reset=reset)
    cursor = output_conn.cursor()

    total = 0
    extracted = 0
    app_counts = {}
    status_counts = {}
    for row in iter_chat_captures(openchronicle_db):
        if limit is not None and total >= limit:
            break
        total += 1
        row = dict(row)
        extracted_title, context, status = extract_chat_window_title(cleaner, row)
        if extracted_title:
            extracted += 1
        app_name = row.get("app_name") or ""
        app_counts[app_name] = app_counts.get(app_name, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
        cursor.execute(
            """
            INSERT INTO chat_window_title_extraction_results
            (source_capture_id, timestamp, app_name, original_window_title,
             extracted_window_title, original_visible_text, context_json, extraction_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(row.get("id") or ""),
                row.get("timestamp") or "",
                app_name,
                row.get("window_title") or "",
                extracted_title,
                row.get("visible_text") or "",
                json.dumps(context or {}, ensure_ascii=False),
                status,
            ),
        )

    output_conn.commit()
    output_conn.close()
    return {
        "openchronicle_db": str(openchronicle_db),
        "output_db": str(output_db),
        "table": "chat_window_title_extraction_results",
        "total_events": total,
        "extracted_titles": extracted,
        "missing_titles": total - extracted,
        "app_counts": app_counts,
        "status_counts": status_counts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract Feishu/WeChat chat window titles from OpenChronicle AXTree captures."
    )
    parser.add_argument("--openchronicle-db", default=str(DEFAULT_OPENCHRONICLE_DB))
    parser.add_argument("--output-db", default=str(DEFAULT_OUTPUT_DB))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--append", action="store_true", help="Append to existing result table instead of rebuilding it.")
    args = parser.parse_args()

    openchronicle_db = Path(os.path.expanduser(args.openchronicle_db)).resolve()
    output_db = Path(os.path.expanduser(args.output_db)).resolve()
    if not openchronicle_db.exists():
        raise FileNotFoundError(f"OpenChronicle database not found: {openchronicle_db}")

    stats = write_results(
        openchronicle_db=openchronicle_db,
        output_db=output_db,
        reset=not args.append,
        limit=args.limit,
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
