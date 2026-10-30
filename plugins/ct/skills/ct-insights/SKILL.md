---
name: ct-insights
description: "Control Tower insights skill for analyzing work order history, decision logs, learning records, and usage patterns. Use when the user invokes $ct-insights or /ct-insights, requests project or global workflow health, asks what patterns are good or bad, wants conflicts or improvement suggestions, or wants an evidence-based report from Control Tower records."
---
<!-- ct-insights-version: 5.14.4 -->

# ct-insights

Analyze Control Tower usage. Read records, compute health signals, and report evidence-backed findings.

Arguments: `$ARGUMENTS`

## Scope

| Invocation | Scope | Data |
|---|---|---|
| `ct-insights` | current project | `_ct-workorders/`, state, decisions, learnings, sprint status |
| `ct-insights global` | global | Layer 2 registry and registered project summaries |
| `*insights` | Tower session | handled by `control-tower`, not this skill |
| `*insights workflow [T#### …]` | Tower session (v5.11.0+) | `control-tower` runs this skill's `scripts/ct-workflow-prefilter.py` (path relative to this skill's directory, manual or plugin install); see `references/analysis-rules.md` § 預篩腳本：排除守門與按需提示 |

If invoked outside a Control Tower project, explain which files are missing and stop.

## Analysis Flow

1. Collect work order records, including T/BUG/PLAN/EXP when enabled.
2. Prefer frontmatter metadata; report drift rather than hiding it.
3. Collect `_tower-state.md`, `_decision-log.md` (or `_decisions.md`, the legacy decision-log file name, when an older project still uses it), `_learnings.md`, and `sprint-status.yaml` when present.
4. Calculate status distribution, cycle time, blocked/partial rate, retry or strikeout signals, and stale active items. v5.13.0+: for open BUGs, use the review conditions in `../control-tower/references/bug-plan-system.md` § BUG 單據 › 未結 BUG 清理提示.
5. Detect good and bad patterns using `references/analysis-rules.md`. v5.10.0+: when the user asks which work fits Claude Code Workflow, apply its § Workflow 適配度 rule group (S1–S6 / X1–X5, two tracks, 🔵 / 邊界 / 排除 grading) and output `WFC###` candidates in that section's format. Candidates only: do not write briefs, `.claude/workflows/`, or run Workflow here. v5.11.0+: the bundled prefilter script `scripts/ct-workflow-prefilter.py` (Python 3 standard library, read-only, 0 workflow tokens) may be run first for exclusion gating (X2 / X3 / X5 → do not consider Workflow; X5 → suggest a Playbook) and for on-demand hints with evidence locations; it never marks or edits work orders, and its hints still need the manual review that section requires.
6. Detect principle conflicts using `references/conflict-rules.md`.
7. Produce recommendations ranked by impact and effort.
8. Use `references/report-template.md` when a structured report is requested.

## Report Rules

- Findings first, with work order ids or file evidence.
- Separate observed facts from inference.
- Do not overclaim from incomplete records.
- Call out stale or missing data sources.
- Prefer `PASS`, `WARNING`, `PARTIAL`, or `BLOCKED` style status labels.

If there are fewer than three work orders, say the sample is too small for strong trend claims and give only local observations.

## Reference Routing

- `references/analysis-rules.md`: pattern detection, including the Workflow fit rule group (authoritative for S1–S6 / X1–X5 and the WFC format, and, v5.11.0+, for the prefilter script's role and the `*insights workflow` entry).
- `scripts/ct-workflow-prefilter.py` (v5.11.0+): the prefilter script; run it, do not load it into context. Resolve it from this skill's own directory, never from a fixed `~/.claude/skills` or `~/.codex/skills` path (v5.14.0+; see `references/analysis-rules.md` § 預篩腳本：排除守門與按需提示).
- `../control-tower/references/workflow-engine.md`: what Workflow is in CT (positioning, Skill / Playbook / Workflow split); load only when explaining a WFC candidate.
- `references/conflict-rules.md`: principle conflict detection.
- `references/report-template.md`: output sections, metrics, and health panel.

## Error Handling

- Missing `_ct-workorders/`: no project-level CT data.
- Missing decision or learning files: skip those dimensions and mark evidence unavailable.
- Broken project registry in global mode: report invalid entries and continue with valid projects.
- Huge history: sample active/recent items first, then ask before building a long report.
