---
name: ct-help
description: "Control Tower help skill for explaining the Tower and Worker ecosystem, commands, prefixes, workflow, BAT and YOLO concepts, state files, onboarding, and common confusion. Use when the user invokes $ct-help or /ct-help, is new to Control Tower, asks how to use ct-exec, ct-done, ct-status, ct-evolve, ct-fieldguide, or asks what a Tower command means."
---
<!-- ct-help-version: 5.15.0 -->

# ct-help

Explain Control Tower usage clearly without switching into Tower orchestration or Worker execution.

Arguments: `$ARGUMENTS`

## Response Style

- Use Traditional Chinese by default.
- Keep command names, paths, env vars, statuses, and examples exact.
- Answer the user's immediate question first.
- Keep beginner explanations short and operational.
- Do not create or edit work orders; this is a help skill.

## Core Model

Control Tower separates coordination from execution:

- Tower session: understands goals, creates work orders, tracks state, receives reports, decides next work.
- Worker session: executes one work order, edits files, validates, commits when required, reports back.
- Files are the source of truth: work orders, Tower state, decisions, learnings, and generated indexes.

Common records:

- `_ct-workorders/T*.md`: work orders
- `_ct-workorders/_tower-state.md`: Tower recovery state
- `_ct-workorders/_decision-log.md`: decisions
- `_ct-workorders/_learnings.md`: project learnings
- `_ct-workorders/_bug-tracker.md`: generated BUG index
- `_ct-workorders/_backlog.md`: generated PLAN index
- `~/.claude/control-tower-data/`: global Layer 2 knowledge and config

## Command Families

`/` or `$` skill commands load a dedicated skill. The call string depends on the agent and the install method (v5.14.0+):
Claude Code uses `/ct-exec T####` for both the zip and the plugin install; Codex uses `$ct-exec T####` for the zip install and
`$ct:ct-exec T####` for the `ct` plugin install. BAT dispatch to Codex works with both installs on BAT `>= 0.7.2-pre.1` (BAT picks the
call string; v5.14.2+), and only with the zip install on older BAT. The examples below use the
Codex zip-install form. The rule lives only in `../control-tower/references/auto-session.md` § 依安裝方式的 skill 呼叫字串; do not restate it.


- `$control-tower`: start or resume Tower.
- `$ct-exec T####`: execute one work order.
- `$ct-done T####`: remedial closeout.
- `$ct-status`: inspect work order state.
- `$ct-evolve`: distill learnings.
- `$ct-insights`: analyze usage patterns.
- `$ct-fieldguide`: generate or audit FIELDGUIDE/DESIGN guidance.
- `$ct-help`: explain usage.

`*` commands are Tower-internal:

- `*sync`: rebuild/compare Tower indexes and status.
- `*config`: view or change Tower settings.
- `*pause` / `*resume`: handle interruption.
- `*bug`, `*plan`, `*exp`: create structured records.
- `*archive`: move final records to cold storage.
- `*evolve`, `*insights`, `*fieldguide`: Tower-local lightweight operations.
- `*import`, `*onboard`, `*rescan`: setup and maintenance.

Explain that `*` commands only make sense inside an active Tower session.

## Typical Workflow

```text
1. Start Tower: $control-tower
2. Discuss or select work
3. Tower creates or dispatches T####
4. Worker runs: $ct-exec T#### (call string per agent and install method: see Command Families)
5. Worker reports and commits when required
6. Tower receives "T#### 完成" or related status
7. Tower updates state and chooses next action
```

For interrupted work:

```text
1. Run $ct-status to inspect state
2. Use $ct-exec T#### to resume scoped work, or $ct-done T#### to repair closeout (call strings: see Command Families)
3. Return exact completion message to Tower
```

## Status Words

- `DONE`: scoped work complete.
- `FIXED`: bug implementation complete and awaiting verification.
- `PARTIAL`: some gates passed but scoped work remains incomplete.
- `BLOCKED`: needs external input or environment.
- `FAILED`: attempted path did not meet objective.
- `ABANDONED` / `DROPPED` / `WONTFIX`: intentionally retired or rejected.

Emphasize that `PARTIAL` can later be corrected when a blocker is resolved.

## BAT And YOLO

BAT can dispatch Worker terminals and notify Tower automatically.

Key concepts:

- Tower dispatch uses `BAT_TERMINAL_ID` with `bat-terminal.mjs --notify-id`.
- Worker notify receives `BAT_TOWER_TERMINAL_ID` and calls `bat-notify.mjs`.
- `CT_MODE=on` pre-fills Tower; `CT_MODE=yolo` may auto-submit with `--submit`.
- Under `CT_MODE=yolo` (v5.5.0+) a Worker asks Tower, not the user (`T#### 提問`, answered in the work order); breakpoint D tells the user when a Worker tab is `blocked` waiting for them. See `../control-tower/references/yolo-mode.md`.
- `BAT_TOWER_TERMINAL_ID` is not required in Tower before dispatch.
- If helper shells cannot see `BAT_*`, native PowerShell may still see them; avoid false non-BAT conclusions. Checks list variable names only, never values (`../control-tower/references/auto-session.md` § 偵測條件).

## Claude Code Workflow (v5.11.0+)

- Workflow is how a Worker may run one work order with several sub-agents; it is not CT's orchestration layer.
- Worried about tokens? `*config workflow_integration off` stops Tower from suggesting or authorizing Workflow for this session;
  add `--save project` or `--save global` to keep it. Values and default: `../control-tower/references/tower-config.md` § 可用選項.
- A Worker calls the Workflow tool only when its work order authorizes it, and records any sub-agents it starts itself
  (`../ct-exec/SKILL.md` § Workflow And Sub-Agents).
- `*insights workflow [T#### …]` lists exclusion-gate results and hints with evidence locations; it never marks work orders.
- Named workflows stay at 🔵 for now (gate G2 not passed); see `../control-tower/references/workflow-engine.md` § 現況：G2 未通過.

## User Guidance Patterns

If the user asks "what should I type?", give the exact command.

If the user asks "where is the record?", name the file and its role.

If the user asks "is it done?", explain which evidence lane is proven: source, test, runtime, deploy, release, or customer confirmation.

If the user is new, explain only the next two or three actions rather than the whole ecosystem.

## Reference Routing

Use these only when needed:

- `../control-tower/SKILL.md`: current Tower startup and command routing.
- `../control-tower/references/tower-config.md`: settings and help topics.
- `../control-tower/references/work-order-system.md`: work order lifecycle.
- `../control-tower/references/auto-session.md`: terminal/BAT dispatch.
- `../control-tower/references/yolo-mode.md`: YOLO mode.
- `../control-tower/references/archive-system.md`: archive behavior.
- `../control-tower/references/bug-plan-system.md`: BUG/PLAN/EXP records.
