# Agent Memory Reconciliation

## Roles

- **PME:** evidence of what appeared to happen during a bounded time period.
- **Agent memory:** longer-term context about identity, preferences, project names, goals, decisions, and prior outcomes.

Memory improves interpretation; it does not become period evidence.

## Merge rules

1. Use PME timestamps and observed states for the requested period.
2. Use memory to resolve stable aliases, project boundaries, user preferences, and background.
3. Do not add work, results, blockers, or plans found only in memory to a period report.
4. A memory created after the PME event may describe a later state. Present both as a transition with dates.
5. A memory predating PME may be stale. Prefer newer PME evidence for current status.
6. When source dates are absent or ordering is unclear, disclose the conflict and avoid choosing a winner.
7. Never use memory to upgrade research to implementation, an attempt to a fix, or a proposal to a decision.

## Conflict examples

PME says a fix was attempted; memory says the issue was later resolved:

> 在报告时段内完成了排查和修复尝试；Agent 记忆显示该问题之后已解决，但这不是本时段内的 PME 结果。

PME says work is ongoing; older memory says it was completed:

> 当前 PME 仍显示相关工作在推进。较早记忆中的“已完成”可能对应上一阶段或已过期状态，暂不据此判定本阶段完成。

## Citation boundary

PME factual items cite PME IDs. Material memory context should be introduced as “根据 Agent 记忆” and follow the host Agent's memory-citation requirements when available.

## Recommendation reasoning

Recommendations may combine:

- observed unfinished work,
- observed blockers,
- observed concentration of time,
- explicit PME next actions,
- stable user priorities from memory.

Label recommendations as recommendations. State the evidence and the assumption behind each one.
