# PME Schema and Evidence

## Evidence hierarchy

Use the highest populated layer for the requested period:

| Priority | Table | Meaning | Appropriate use |
|---|---|---|---|
| 1 | `screen_observations` | Work-level progress, event clusters, status changes, results, blockers, task signals | Primary reporting evidence |
| 2 | `screen_facts` | Atomic episodic or semantic facts linked to raw records | Fill gaps and verify claims |
| 3 | `window_workstream` | Cross-time activity grouped around a window/content stream | Project/context clues |
| 4 | `segments` | Time-bounded activity summaries | Time allocation and fallback |
| 5 | `views` | Deduplicated application/window views | Context and weak fallback |
| 6 | `records` | Raw OCR/AX captures | Verification only |

`screen_observations` is not user-authored text and is not an Agent-level conclusion. It is a derived work signal built from screen facts.

## Important fields

### `screen_observations`

- `progress_text`: strongest description of work movement.
- `summary_text`: background and context.
- `project_key`, `objective_key`: grouping hints, not guaranteed truth.
- `work_type`, `category`: activity classification.
- `blockers_json`: observed blockers.
- `next_actions_json`: observed follow-ups, not automatically current commitments.
- `evidence_*_ids_json`: traceability.
- `confidence`: calibration signal.

### `screen_facts`

- `fact_text`: atomic claim.
- `fact_type`: episodic or semantic.
- `fact_kind`: action, result, context, decision, blocker, and similar.
- `work_type`: implementation, debugging, research, communication, and similar.
- `evidence_record_ids_json`: raw evidence links.
- `attribution_risk`: extractor warning that an action-like fact came from browser content and may describe the viewed page rather than the user.

Facts derived from repositories, release notes, shopping pages, documentation, or search results are content observations first. A sentence such as “fixed OAuth login” on a GitHub page is not evidence that the user made that fix. Require corroborating observation, direct editing/execution context, or recast it as research.

### Time-allocation sources

Prefer `segments.duration_seconds` grouped by meaningful project/activity. Record counts are capture density, not time spent. Never equate record count with duration.

## Status interpretation

- **Completed:** explicit result, delivery, merge, send, publish, fix, or completion signal.
- **In progress:** implementation or production activity without a completion signal.
- **Blocked:** explicit error, dependency, unresolved decision, waiting state, or failed attempt.
- **Research/discussion:** reading, comparing, browsing, investigating, discussing, or drafting without implementation evidence.
- **Uncertain:** conflicting, low-confidence, or insufficient evidence.

## Database compatibility

The extractor validates required PME identity tables and dynamically tolerates optional fields. If `screen_observations` is empty, it returns a warning and chooses the highest populated fallback layer.

The database is always opened read-only. The skill may update only its own `config.json`, and only from a user-supplied path or explicit environment override. It does not search the filesystem for moved databases.
