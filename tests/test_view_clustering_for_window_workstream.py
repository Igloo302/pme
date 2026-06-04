#!/usr/bin/env python3
import argparse
import os
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = REPO_ROOT / "pme_memory.db"
DEFAULT_CONFIG = REPO_ROOT / "config.yaml"
DEFAULT_OUTPUT_TXT = Path(__file__).resolve().parent / "view_cluster_results.txt"


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


def load_all_view_signatures(cleaner_instance, db_path):
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        return cleaner_instance.load_view_signatures_for_window_workstream_generation(cursor)
    finally:
        conn.close()


def value_summary(values, limit=4):
    unique_values = []
    seen = set()
    for value in values:
        value = str(value or "").strip()
        if not value or value in seen:
            continue
        unique_values.append(value)
        seen.add(value)
        if len(unique_values) >= limit:
            break
    return ", ".join(unique_values)


def cluster_time_range(views):
    starts = [view.get("start_timestamp") for view in views if view.get("start_timestamp")]
    ends = [view.get("end_timestamp") for view in views if view.get("end_timestamp")]
    return (min(starts) if starts else "", max(ends) if ends else "")


def format_cluster_line(index, cluster):
    views = sorted(
        cluster.get("views") or [],
        key=lambda item: (item.get("start_timestamp") or "", item.get("id") or 0),
    )
    start_time, end_time = cluster_time_range(views)
    view_ids = [str(view.get("id")) for view in views if view.get("id") is not None]
    app_names = value_summary(view.get("app_name") for view in views)
    window_titles = value_summary(view.get("window_title") for view in views)
    topics = value_summary(topic for view in views for topic in (view.get("topics") or []))
    return (
        f"cluster={index}\t"
        f"count={len(views)}\t"
        f"apps={app_names}\t"
        f"windows={window_titles}\t"
        f"view_ids={','.join(view_ids)}"
    )


def write_cluster_result(output_path, clusters):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sorted_clusters = sorted(
        clusters,
        key=lambda cluster: (
            min(
                (view.get("start_timestamp") or "" for view in cluster.get("views") or []),
                default="",
            ),
            min((view.get("id") or 0 for view in cluster.get("views") or []), default=0),
        ),
    )
    with open(output_path, "w", encoding="utf-8") as handle:
        for index, cluster in enumerate(sorted_clusters, start=1):
            handle.write(format_cluster_line(index, cluster))
            handle.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Cluster all views with cluster_current_views_for_window_workstream and save one cluster per line."
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to cleaned PME SQLite database.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to config.yaml.")
    parser.add_argument(
        "--output-txt",
        default=str(DEFAULT_OUTPUT_TXT),
        help="Path to save the cluster text result.",
    )
    args = parser.parse_args()

    db_path = Path(os.path.expanduser(args.db)).resolve()
    config_path = Path(os.path.expanduser(args.config)).resolve()
    output_txt_path = Path(os.path.expanduser(args.output_txt)).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    cleaner_module = import_cleaner_module(config_path)
    cleaner_instance = cleaner_module.PMECleaner()
    view_signatures = load_all_view_signatures(cleaner_instance, db_path)
    clusters = cleaner_instance.cluster_current_views_for_window_workstream(view_signatures)
    write_cluster_result(output_txt_path, clusters)

    print(f"Loaded views: {len(view_signatures)}")
    print(f"Generated clusters: {len(clusters)}")
    print(f"Saved result: {output_txt_path}")


if __name__ == "__main__":
    main()
