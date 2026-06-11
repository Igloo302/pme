---
name: pme-insights
description: Use when a user asks for a daily report, weekly report, progress brief, recent-work summary, work-interest or behavior-pattern analysis, attention or time-allocation insight, priority planning, bottleneck diagnosis, or next-step advice based on a PME memory.db or personal screen-memory database.
---

# PME Insights

Use PME as traceable evidence of observed work and Agent memory as longitudinal context. Never let memory invent activity or overwrite stronger current evidence.

## Start Here

Set `SKILL_DIR` to this skill's installed directory, then inspect the data source:

```bash
python3 "$SKILL_DIR/scripts/pme_memory.py" status
```

Handle the result:

- `ok`: use the returned database.
- `unconfigured`: ask for the PME `memory.db` location, then run `configure --db PATH`.
- `missing`: the saved path no longer exists or is no longer valid. Ask the user for the new path; do not search the filesystem.
- `invalid`: explain the schema mismatch and request another path.

The script saves the confirmed path in `config.json`. If the file later moves, update the config only after the user provides the new location:

```bash
python3 "$SKILL_DIR/scripts/pme_memory.py" configure --db "/new/path/memory.db"
```

Validate the supplied file by PME schema before updating config. Never scan the user's filesystem to guess the new location.

Explicit overrides:

```bash
PME_MEMORY_DB="/path/to/memory.db" python3 "$SKILL_DIR/scripts/pme_memory.py" status
PME_INSIGHTS_CONFIG="/path/to/config.json" python3 "$SKILL_DIR/scripts/pme_memory.py" status
```

## Extract Evidence

Always use an explicit, timezone-aware half-open range `[start, end)`.

```bash
python3 "$SKILL_DIR/scripts/pme_memory.py" extract \
  --start "2026-06-08T00:00:00+08:00" \
  --end "2026-06-15T00:00:00+08:00"
```

For “today,” “this week,” or similar wording, state the exact dates in the answer. Use the user's local timezone when known.

Read [references/schema-and-evidence.md](references/schema-and-evidence.md) when interpreting source layers or degraded data. Read [references/playbooks.md](references/playbooks.md) for the requested output type. Read [references/memory-reconciliation.md](references/memory-reconciliation.md) before using Agent memory.

## Evidence Rules

Apply these rules to every capability:

1. Use only activity supported by PME evidence inside the requested period.
2. Prefer `progress_text`; use `summary_text` for context.
3. Merge semantically equivalent items and combine their source IDs.
4. Do not group work solely because app names, window titles, or timestamps are close.
5. Treat `unknown` or `general` project keys conservatively; use “Other work” when evidence is insufficient.
6. Distinguish completed, in progress, blocked, and research/discussion.
7. Reading is not implementation. Attempting is not solving. Discussing is not deciding.
8. Use `next_actions` only as an observed plan. Agent recommendations must be labeled separately.
9. Preserve conflicts as dated changes or unresolved uncertainty.
10. Use conservative language for low-confidence evidence; omit noise when it adds no work-level meaning.
11. Do not turn entities, artifacts, apps, or keywords into accomplishments by themselves.
12. Every factual work item must cite one or more PME IDs with the source table.
13. Treat `attribution_risk: true` as unverified. Browser pages, repositories, product pages, and changelogs may describe someone else's actions. Do not report them as the user's work without corroborating observations or direct editing/execution evidence.

## Synthesis Workflow

1. Determine intent and exact time range.
2. Resolve and extract PME evidence.
3. Select the highest available evidence layer; use lower layers only to fill gaps or verify.
4. Group evidence by shared project/objective/content, not by application or time proximity alone.
5. Audit source attribution. Downgrade browser-derived action claims to viewed/researched content unless corroborated.
6. Assign each group a state: `completed`, `in_progress`, `blocked`, `research_or_discussion`, or `uncertain`.
7. Retrieve only relevant Agent memories about project identity, stable preferences, prior decisions, or known goals.
8. Reconcile memory using the rules in `memory-reconciliation.md`.
9. Draft using the matching playbook.
10. Audit every factual sentence for a PME citation and every recommendation for an explicit reasoning basis.

## Traceability Format

Use compact citations:

```markdown
证据：`screen_observations: 12, 18`; `screen_facts: 44`
```

When evidence falls back below observations, disclose it once:

> 本时段没有可用的 `screen_observations`，以下内容基于 `screen_facts` 和较低层级记录整理。

Do not expose raw OCR, chat text, or sensitive screen content unless the user explicitly asks to inspect evidence.

## Recommendation Boundary

Reports describe observed work. Planning and problem-solving may add recommendations, but keep three layers visibly separate:

- **Observed:** directly supported by PME.
- **Remembered context:** supplied by Agent memory and labeled when material.
- **Inferred/recommended:** reasoned from observed state; never presented as something the user already did or decided.

If evidence is too thin, say what is known, what is unknown, and what additional observation would reduce uncertainty.
