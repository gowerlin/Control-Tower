---
name: ct-help
description: "Control Tower help skill for explaining the Tower and Worker ecosystem, commands, prefixes, workflow, BAT and YOLO concepts, methodology adapters, state files, onboarding, and common confusion. Use when the user invokes $ct-help or /ct-help, is new to Control Tower, asks how to use ct-exec, ct-done, ct-status, ct-evolve, ct-fieldguide, or asks what a Tower command means."
---
<!-- ct-help-version: 6.0.0 -->

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

`/` or `$` skill commands load a dedicated skill. The call string depends on the agent and the install method (v6.0.0-beta.5+):
Claude Code uses `/ct-exec T####` for both the zip and the plugin install; Codex uses `$ct-exec T####` for the zip install and
`$ct:ct-exec T####` for the `ct` plugin install. BAT dispatch to Codex works with both installs on BAT `>= 0.7.2-pre.1` (BAT picks the
call string; v6.0.0-beta.6+), and only with the zip install on older BAT. The examples below use the
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
- `*evolve`, `*insights`, `*fieldguide`: Tower-local lightweight operations (`*insights sessions`: see Session Usage And Evidence).
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
- If helper shells cannot see `BAT_*`, native PowerShell may still see them; avoid false non-BAT conclusions. Check names only (bash: `compgen -e | grep -E '^(BAT|CT)_' | sort`), never print the values, and read each named exception with its own command (`control-tower/references/auto-session.md` § BAT 內部終端路由 › 偵測條件).

## Claude Code Workflow (v5.11.0+)

- Workflow is how a Worker may run one work order with several sub-agents; it is not CT's orchestration layer.
- Worried about tokens? `*config workflow_integration off` stops Tower from suggesting or authorizing Workflow for this session;
  add `--save project` or `--save global` to keep it. Values and default: `../control-tower/references/tower-config.md` § 可用選項.
- A Worker calls the Workflow tool only when its work order authorizes it, and records any sub-agents it starts itself
  (`../ct-exec/SKILL.md` § Workflow And Sub-Agents).
- `*insights workflow [T#### …]` lists exclusion-gate results and hints with evidence locations; it never marks work orders.
- Named workflows stay at 🔵 for now (gate G2 not passed); see `../control-tower/references/workflow-engine.md` § 現況：G2 未通過.

## Session Usage And Evidence (v6.0.0-beta.10+)

Summaries only; answer details from the authority sections named here, not from memory.

- `*insights sessions [T#### …]` (Tower command): how many tokens, tool calls and failures each work order used, read from Claude Code's
  local session logs; with ids it lists only those work orders. Claude Code only (no Codex or Copilot). Tower usage is listed separately and
  never split across work orders. Cost is an estimate (equivalent API price), for trends and comparison, not a bill. No session logs (new
  machine, logs cleaned up, not Claude Code) → it says "資料不可用" and nothing else is blocked. Authority:
  `../ct-insights/references/analysis-rules.md` § Session 用量統計. v6.0.0-beta.12+: skill counts include slash commands, and agent types
  (`subagent_type`) are counted too.
- `*insights tools [--all-projects] [--keep …]` (Tower command, v6.0.0-beta.12+): which skills, plugins, MCP servers, agent types and built-in
  tools are always loaded but rarely used, from the same session logs. It only suggests and never changes a setting: each item says which
  layer to change it at (project, user, claude.ai account) and which key or interface, and a change takes effect in a new session. Items a
  work order type uses are not suggested; built-in tools such as `Artifact` go to a "needs your decision" list. Authority:
  `../ct-insights/references/analysis-rules.md` § 工具清單建議.
- `/ct-evolve --facts-from <snapshot or facts file>`: feeds the candidate facts produced from those numbers into the normal learning flow.
  It only marks candidates (🔵, at most 🟡); promotion still goes through the usual gate and user approval, and it never edits work orders.
  Authority: `../ct-evolve/SKILL.md` § Session Evidence.

## Methodology Adapters (v6.0.0+)

Methodology adapters are part of the stable line since 6.0.0, which replaces 5.15.0 (they were a pre-release from 6.0.0-pre.1 through 6.0.0-rc.1). The contract is defined once in
`../control-tower/references/methodology-adapters.md`; the config keys are registered in `../control-tower/references/tower-config.md`
§ 可用選項 and § 方法論設定鍵. Answer from those files; do not restate values or rules from memory.

- What an adapter is: a YAML description file that tells Tower where a methodology (for example BMAD) lives, which of the five layers
  (`planning`, `execution`, `review`, `verification`, `delivery`) it handles, and which workflow fits each kind of request. It is data, not
  code. Tower still owns the work order lifecycle; the methodology only shapes how a Worker does the work inside one work order. BMAD is the
  built-in adapter.
- Nothing to do by default: with no `methodology*` key anywhere, `methodology` is `auto` and Tower behaves exactly as in v5.12.6.
- See the current setting: `*config methodology` inside a Tower session (value, source, and what `auto`/`inherit` resolve to); `*config`
  lists every option.
- Swap the main methodology: `*config methodology <adapter id>` for this session, plus `--save project` or `--save global` to keep it;
  `none` turns methodology routing off. `*onboard` also asks this (`../control-tower/references/onboarding.md` 主題 5).
- Mix methodologies by layer: `*config methodology_<layer> <adapter id>`; layers left at `inherit` follow the main methodology.
  Swapping the review layer loses review steps built into the other methodology's execution flow, and Tower says so when it dispatches.
- One work order only: tell Tower "use <adapter id> for this one" (every layer except delivery), or "use <adapter id> for <layer> in this
  one" (that layer only); Tower records it in that work order and does not change any config file.
- The delivery layer (PR, release, deploy) is never handed to a methodology by default, not even by "use X for this one": say it
  explicitly, for example "use <adapter id> for delivery in this one".
- Workers do not read these keys; the resolved choice is written into the work order, and the Worker carries it as
  `../ct-exec/SKILL.md` § Methodology says (CT rules first; any methodology skill a Worker calls is recorded in the report).
- A methodology that injects instructions at session start (for example pstack): Tower adds a `### 方法論邊界` section to the work
  order by default (`methodology_guard: warn`); `block` refuses to dispatch instead. See `methodology-adapters.md` § 與 hook／session 路由的相處規則.

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
- `../control-tower/references/methodology-adapters.md`: methodology adapters (v6.0.0+).
