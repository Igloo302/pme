# PME Insights Playbooks

## Daily report

Use the user's local calendar day.

```markdown
# 工作日报（YYYY-MM-DD）

## 今日进展
- [state] Work movement and result.
  证据：`table: ids`

## 阻塞与未决
- Observed blocker or uncertainty.
  证据：`table: ids`

## 后续跟进
- Observed next action.
  证据：`table: ids`

## 简短判断
- One clearly labeled inference, only when useful.
```

Do not create a follow-up section when no observed next action exists.

## Weekly report

Use an explicit seven-day or calendar-week range.

```markdown
# 工作周报（YYYY-MM-DD 至 YYYY-MM-DD）

## 核心进展
### Project or objective
- Consolidated progress and state.
  证据：`table: ids`

## 已完成
## 进行中
## 阻塞与风险
## 已明确的后续动作
```

Omit empty sections. Keep project boundaries conservative.

## Read me

Answer “最近我在关注什么 / 我的工作模式是什么” using a recent 14-30 day window unless the user specifies one.

Cover:

- Recurring work themes
- Typical activity modes: implementation, research, communication, debugging
- Switching or concentration patterns supported by time evidence
- Stable patterns versus one-off events
- Confidence and coverage limits

Do not diagnose personality, motivation, health, or private traits from screen behavior.

## Attention insight

Use `segment_seconds_by_*` for time claims. Use observation/fact counts only for topic frequency.

Cover:

- Main time allocations
- High-attention projects or objectives
- Research-to-execution balance
- Fragmentation or repeated return patterns
- Important work receiving little observed time, only when a goal is explicitly known

Say “capture coverage suggests” when duration coverage is incomplete.

## Plan

Separate observed commitments from recommendations:

```markdown
## Current state
## Observed open loops
## Recommended priorities
1. Priority and why now.
## Suggested next actions
```

Rank by explicit urgency, blocker removal, dependency order, unfinished momentum, and stable goals. Do not invent deadlines.

## Solve a problem

Identify bottlenecks as hypotheses unless explicitly observed.

```markdown
## Problem signal
## Most likely bottleneck
## Evidence
## Uncertainty
## Next diagnostic or action
## Success signal
```

Prefer the smallest action that can disprove the bottleneck hypothesis or unblock the next dependency.

## Progress brief

Keep it concise:

```markdown
## Recently advanced
## Still open
## Next follow-ups
## Risks
```

Use the latest state when repeated observations describe the same item, while retaining IDs from all merged evidence.
