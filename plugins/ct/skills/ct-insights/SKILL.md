---
name: ct-insights
description: "Control Tower insights skill for analyzing work order history, decision logs, learning records, and usage patterns. Use when the user invokes $ct-insights or /ct-insights, requests project or global workflow health, asks what patterns are good or bad, wants conflicts or improvement suggestions, or wants an evidence-based report from Control Tower records."
---
<!-- ct-insights-version: 6.0.0 -->

# ct-insights

Analyze Control Tower usage. Read records, compute health signals, and report evidence-backed findings.

Arguments: `$ARGUMENTS`

## Scope

| Invocation | Scope | Data |
|---|---|---|
| `ct-insights` | current project | `_ct-workorders/`, state, decisions, learnings, main methodology tracker (bmad: sprint status) |
| `ct-insights global` | global | Layer 2 registry and registered project summaries |
| `*insights` | Tower session | handled by `control-tower`, not this skill |
| `*insights workflow [T#### …]` | Tower session (v5.11.0+) | `control-tower` runs this skill's `scripts/ct-workflow-prefilter.py` (path relative to this skill's directory, manual or plugin install); see `references/analysis-rules.md` § 預篩腳本：排除守門與按需提示 |
| `*insights sessions [T#### …] [--since … --until …]` | Tower session (v6.0.0-beta.10+) | `control-tower` runs this skill's `scripts/ct-session-stats.py` on the local Claude Code session JSONL (Claude Code only); see `references/analysis-rules.md` § Session 用量統計（`*insights sessions`，v6.0.0-beta.10+） |
| `*insights tools [--all-projects] [--keep …] [--since … --until …]` | Tower session (v6.0.0-beta.12+) | `control-tower` runs the same script with `--tools`: loaded tool lists × actual use → a suggestion report (Claude Code only); see `references/analysis-rules.md` § 工具清單建議（`*insights tools`，v6.0.0-beta.12+） |

If invoked outside a Control Tower project, explain which files are missing and stop.

## Analysis Flow

1. Collect work order records, including T/BUG/PLAN/EXP when enabled.
2. Prefer frontmatter metadata; report drift rather than hiding it.
3. Collect `_tower-state.md`, `_decision-log.md` (or `_decisions.md`, the legacy decision-log file name, when an older project still uses it), `_learnings.md`, and the main methodology's tracker when present (adapter `tracker`, found the same way as `../ct-status/SKILL.md` § Read Order; bmad: `sprint-status.yaml`).
   v6.0.0-pre.1+: when work orders carry frontmatter `methodology`, metrics may be grouped by adapter (`methodology.layers.<layer>.adapter`; a legacy `### BMad 工作流程` section counts as `bmad`; neither → `none`), and `### 方法論執行紀錄` adds evidence (methodology skills used without being declared, `methodology_ambient`). Say when groups are too small to compare.
4. Calculate status distribution, cycle time, blocked/partial rate, retry or strikeout signals, and stale active items. v6.0.0-beta.3+: for open BUGs, use the review conditions in `../control-tower/references/bug-plan-system.md` § BUG 單據 › 未結 BUG 清理提示.
5. Detect good and bad patterns using `references/analysis-rules.md`. v5.10.0+: when the user asks which work fits Claude Code Workflow, apply its § Workflow 適配度 rule group (S1–S6 / X1–X5, two tracks, 🔵 / 邊界 / 排除 grading) and output `WFC###` candidates in that section's format. Candidates only: do not write briefs, `.claude/workflows/`, or run Workflow here. v5.11.0+: the bundled prefilter script `scripts/ct-workflow-prefilter.py` (Python 3 standard library, read-only, 0 workflow tokens) may be run first for exclusion gating (X2 / X3 / X5 → do not consider Workflow; X5 → suggest a Playbook) and for on-demand hints with evidence locations; it never marks or edits work orders, and its hints still need the manual review that section requires.
5a. v6.0.0-beta.10+: for token and tool usage per work order, run the bundled `scripts/ct-session-stats.py` (Python 3 standard library, read-only, no model calls, no network). Attribution order, allowed fields, privacy rules, degradation, output reading, snapshot and candidate-fact formats live only in `references/analysis-rules.md` § Session 用量統計. Key points: Tower usage is listed separately and never allocated to work orders; `est_usd` and `tower_by_decision` are estimates (「估」); `max_failures_in_10_calls >= 3` is a 🔵 observation, never a verdict; every output passes the built-in privacy self-check first (exit `3` = nothing written); no session data → exit `4`, report 「資料不可用」 and continue the rest of the report.
   v6.0.0-beta.12+: `skills_invoked` also counts slash commands (full namespaced name, only when the name is in that session's skill listing) and a new `agents_invoked` counts agent types (`subagent_type`); snapshots are `ct-session-stats-snapshot/0.2` (`--facts-from` still reads `0.1`).
5b. v6.0.0-beta.12+: for "which skills, plugins, MCP servers, agent types and built-in tools are always loaded but rarely used", run the same script with `--tools` (`*insights tools`). It only suggests, never edits any setting; each suggestion names its layer (project, user, claude.ai account) and the key or interface, and takes effect in a new session. Criteria, levers, report format and privacy checks live only in `references/analysis-rules.md` § 工具清單建議. It writes no snapshot and no candidate facts.
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
- `scripts/ct-workflow-prefilter.py` (v5.11.0+): the prefilter script; run it, do not load it into context. Resolve it from this skill's own directory, never from a fixed `~/.claude/skills` or `~/.codex/skills` path (v6.0.0-beta.5+; see `references/analysis-rules.md` § 預篩腳本：排除守門與按需提示).
- `scripts/ct-session-stats.py` (v6.0.0-beta.10+): the session usage script, with `scripts/pricing.json` and tests in `scripts/tests/`; run it, do not load it into context. Resolve it like the prefilter script. v6.0.0-beta.12+: `--tools` is the tool-list suggestion mode; its rules are `references/analysis-rules.md` § 工具清單建議（`*insights tools`，v6.0.0-beta.12+）.
- `../control-tower/references/workflow-engine.md`: what Workflow is in CT (positioning, Skill / Playbook / Workflow split); load only when explaining a WFC candidate.
- `references/conflict-rules.md`: principle conflict detection.
- `references/report-template.md`: output sections, metrics, and health panel.

## Error Handling

- Missing `_ct-workorders/`: no project-level CT data.
- Missing decision or learning files: skip those dimensions and mark evidence unavailable.
- Missing Claude Code session records (script exit `4`), or no Python 3: mark the session usage section 「資料不可用」 and continue.
- Broken project registry in global mode: report invalid entries and continue with valid projects.
- Huge history: sample active/recent items first, then ask before building a long report.
