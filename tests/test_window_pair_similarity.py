#!/usr/bin/env python3
import argparse
import csv
import itertools
import json
import os
import sqlite3
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "pme_memory.db"
DEFAULT_CONFIG = REPO_ROOT / "config.yaml"
DEFAULT_OUTPUT_JSON = Path(__file__).resolve().parent / "window_pair_similarity_results.json"


def parse_scalar(value):
    value = value.strip()
    if not value:
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_config(config_path):
    try:
        import yaml
    except ModuleNotFoundError:
        return load_simple_yaml_config(config_path)

    with open(config_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_simple_yaml_config(config_path):
    config = {}
    current_section = None
    with open(config_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("#", 1)[0].rstrip()
            if not line.strip() or ":" not in line:
                continue
            indent = len(line) - len(line.lstrip())
            key, value = line.strip().split(":", 1)
            if indent == 0:
                current_section = key.strip()
                config[current_section] = {} if not value.strip() else parse_scalar(value)
                continue
            if current_section and isinstance(config.get(current_section), dict):
                config[current_section][key.strip()] = parse_scalar(value)
    return config


def import_cleaner_module(config_path):
    sys.path.insert(0, str(REPO_ROOT))
    config = load_config(config_path)
    stub = types.ModuleType("src.config_loader")
    stub.get_config = lambda: config
    sys.modules["src.config_loader"] = stub

    from src import cleaner

    return cleaner


def parse_window_ids(args):
    values = []
    values.extend(args.window_ids or [])
    if args.ids:
        values.extend(part for item in args.ids for part in item.split(","))
    window_ids = []
    seen = set()
    for value in values:
        value = str(value).strip()
        if not value:
            continue
        window_id = int(value)
        if window_id not in seen:
            window_ids.append(window_id)
            seen.add(window_id)
    if len(window_ids) < 2:
        raise ValueError("At least two window_workstream ids are required.")
    return window_ids


def load_window_workstreams(cleaner_instance, db_path, window_ids):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        items = cleaner_instance.load_window_workstream_signatures_for_task_generation(
            cursor,
            window_workstream_ids=window_ids,
        )
    finally:
        conn.close()

    by_id = {item["id"]: item for item in items}
    missing = [window_id for window_id in window_ids if window_id not in by_id]
    if missing:
        raise ValueError(f"Missing window_workstream ids in database: {missing}")
    return by_id


def score_pair(cleaner_module, cleaner_instance, left, right):
    cluster_left_into_right = cleaner_instance.score_window_against_task_cluster(
        left,
        {"window_workstreams": [right]},
    )
    cluster_right_into_left = cleaner_instance.score_window_against_task_cluster(
        right,
        {"window_workstreams": [left]},
    )
    return {
        "left_id": left["id"],
        "right_id": right["id"],
        "left_title": left.get("title") or "",
        "right_title": right.get("title") or "",
        "left_labels": cleaner_instance.task_business_title_labels(left),
        "right_labels": cleaner_instance.task_business_title_labels(right),
        "pair_score": cleaner_instance.score_window_workstream_pair_for_task(left, right),
        "title_score": cleaner_instance.title_similarity_score_for_task(left, right),
        "artifact_score": cleaner_module.list_overlap_score(left["artifact_keys"], right["artifact_keys"]),
        "entity_score": cleaner_module.list_overlap_score(left["entity_keys"], right["entity_keys"]),
        "topic_score": cleaner_module.jaccard_similarity(left["topic_keys"], right["topic_keys"]),
        "text_score": cleaner_module.jaccard_similarity(left["tokens"], right["tokens"]),
        "time_score": cleaner_module.time_proximity_score(
            left["start_timestamp"],
            right["start_timestamp"],
            right["end_timestamp"],
            max_gap_days=cleaner_instance.task_workstream_cfg.get("max_time_gap_days", 30),
        ),
        "left_into_right_cluster_score": cluster_left_into_right[0],
        "left_into_right_cluster_reason": cluster_left_into_right[1],
        "right_into_left_cluster_score": cluster_right_into_left[0],
        "right_into_left_cluster_reason": cluster_right_into_left[1],
        "topic_overlap": sorted(left["topic_keys"] & right["topic_keys"]),
        "entity_overlap": sorted(left["entity_keys"] & right["entity_keys"]),
    }


def format_float(value):
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def print_table(rows):
    headers = [
        "left_id",
        "right_id",
        "pair_score",
        "title_score",
        "artifact_score",
        "entity_score",
        "topic_score",
        "text_score",
        "time_score",
        "left_title",
        "right_title",
        "left_into_right_cluster_reason",
        "right_into_left_cluster_reason",
    ]
    print("\t".join(headers))
    for row in rows:
        print("\t".join(format_float(row.get(header, "")) for header in headers))


def print_csv(rows):
    headers = [
        "left_id",
        "right_id",
        "pair_score",
        "title_score",
        "artifact_score",
        "entity_score",
        "topic_score",
        "text_score",
        "time_score",
        "left_title",
        "right_title",
        "left_labels",
        "right_labels",
        "topic_overlap",
        "entity_overlap",
        "left_into_right_cluster_score",
        "left_into_right_cluster_reason",
        "right_into_left_cluster_score",
        "right_into_left_cluster_reason",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        csv_row = dict(row)
        for key in ["left_labels", "right_labels", "topic_overlap", "entity_overlap"]:
            csv_row[key] = json.dumps(csv_row.get(key) or [], ensure_ascii=False)
        writer.writerow({header: csv_row.get(header, "") for header in headers})


def build_result_payload(db_path, config_path, window_ids, rows):
    return {
        "database": str(db_path),
        "config": str(config_path),
        "window_ids": window_ids,
        "pair_count": len(rows),
        "pairs": rows,
    }


def write_json_result(output_path, payload):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compute pairwise task matching scores for window_workstream ids."
    )
    parser.add_argument("window_ids", nargs="*", help="Window workstream ids, e.g. 29 36 37.")
    parser.add_argument("--ids", nargs="*", help="Comma-separated ids, e.g. --ids 29,36,37.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to cleaned PME SQLite database.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to config.yaml.")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Path to save the unified JSON result file.",
    )
    args = parser.parse_args()

    db_path = Path(os.path.expanduser(args.db)).resolve()
    config_path = Path(os.path.expanduser(args.config)).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    output_json_path = Path(os.path.expanduser(args.output_json)).resolve()

    window_ids = parse_window_ids(args)
    cleaner_module = import_cleaner_module(config_path)
    cleaner_instance = cleaner_module.PMECleaner()
    items_by_id = load_window_workstreams(cleaner_instance, db_path, window_ids)
    rows = [
        score_pair(cleaner_module, cleaner_instance, items_by_id[left_id], items_by_id[right_id])
        for left_id, right_id in itertools.combinations(window_ids, 2)
    ]
    payload = build_result_payload(db_path, config_path, window_ids, rows)
    write_json_result(output_json_path, payload)

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print_csv(rows)
    else:
        print_table(rows)
        print(f"\nSaved JSON result: {output_json_path}")


if __name__ == "__main__":
    main()
