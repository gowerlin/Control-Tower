---
name: ct-help
description: "Control Tower help skill for explaining the Tower and Worker ecosystem, commands, prefixes, workflow, BAT and YOLO concepts, methodology adapters, state files, onboarding, and common confusion. Use when the user invokes $ct-help or /ct-help, is new to Control Tower, asks how to use ct-exec, ct-done, ct-status, ct-evolve, ct-fieldguide, or asks what a Tower command means."
---
<!-- ct-help-version: 6.4.0 -->

# ct-help

Explain Control Tower usage clearly without switching into Tower orchestration or Worker execution.

Arguments: `$ARGUMENTS`

## Response Style

- Use Traditional Chinese by default, including the short progress lines between tool calls.
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

## 與 BAT 協作（Working With BAT, v6.1.0+）

Summaries only; the CT rules live in `../control-tower/references/memory-protocol.md` § 契約 v2 欄位 (fields, answers) and
`../control-tower/references/auto-session.md` § 塔台分頁角色宣告 (startup declaration, `hooks:` hints). BAT's own install steps are in BAT's docs.

- **What contract v2 is**: an agreement between Better Agent Terminal (BAT) and CT. CT writes whatever needs the user into the frontmatter of
  `_ct-workorders/_tower-state.md`; BAT shows it read-only in its right-side 「待辦」 (inbox) tab, so a question from the Tower is not lost
  when later turns scroll it away. At startup the Tower tells BAT it speaks contract v2 (`--set-role tower --bat-contract 2`); BAT turns its new
  features on for that Tower tab only when both sides are v2.
- **What the inbox tab shows**: 「待你決定」 (decisions the Tower stopped for, numbered `U-n`, with their options), 「待你執行」 (things only you
  can do, such as an on-device check or a command to run, numbered `A-n`), reminders that are due, and the work orders marked ⏸ while they
  wait for you. BAT never edits CT files; an item that disappears is done.
- **How to answer** (type it in the Tower tab, or use BAT's answer box, which sends the same line): `U-3：B` (an option code) or
  `U-3：<your own words>`; `A-2：完成`; `A-2：失敗 <what went wrong>`. Full-width `：` and `:` both work. The Tower replies with one
  confirmation line per answer, for example 「U-3 已收到：B → 恢復 T0123」 (CT 6.3.0+: in the same reply; when that reply opens a new
  menu, the confirmations start the menu's first question, after 「剛才的回答：」).
- **Recommended option** (CT 6.2.0+): when the Tower has a recommendation it lists that option first and ends its text with 「（推薦）」,
  in the terminal and in the file; BAT 0.8.0-pre.4 or later also shows a marker and selects it by default. No recommendation, no mark.
- **Dropping items** (CT 6.2.0+): `U-3：放棄` drops a decision, `A-2：略過` drops a to-do; words after it are the reason
  (`U-3：放棄 規格還沒定`). Several at once: `U-1、U-3：放棄 <reason>`. The Tower applies no option, removes the items, keeps the
  work order paused, and logs one decision; it waits for your next instruction instead of asking again.
  CT 6.3.0+: the words after 「放棄」 are **only a reason** — the Tower logs them and does not act on them, even when they read like an
  instruction (it says so in its confirmation line). To give a new direction, answer in your own words instead: `U-3：改做 X` (BAT's
  「其他」 box, the menu's "Other", or typing in the terminal). CT 6.2.x still acted on those words. 「略過」 is not
  「失敗」: no BUG is opened and the check is logged as not verified. Wildcards and ranges (`U-*`, `U-1～U-5`) are not accepted.
  BAT 0.8.0-pre.4 or later adds buttons for this, batch ticks and 「全部放棄」.
- **Pauses as a menu** (CT 6.2.0+): when the Tower stops for your decision (a breakpoint, the merge check, a Worker question passed to you,
  or its own question) it first writes the `U-n` item and then opens Claude Code's own option menu, recommended option first. When the
  question has 1 to 3 options the menu always ends with 「放棄（停下等新方向）」; with 4 options there is no room, so type 「放棄」 in "Other".
  "Other" takes free text, and text starting with 「放棄」 drops the item. A free-answer question (no options) is asked as text, because
  the menu needs at least 2 choices. Pressing Esc closes the menu and ends the Tower's turn: the item stays open, and the Tower's next
  reply reminds you which menus were closed; the next pause still opens a menu.
  The item is still in the inbox and `U-n：…` typed in the terminal or sent from BAT still counts. The same setting as requirement
  questions controls it: `*config interactive-prompts off` gives the plain text pause of 6.1.x. The Tower falls back to text by itself
  on Codex (no menu) and in a BAT tab whose startup check did not report contract v2, because only such a BAT holds a Worker's Enter
  while the menu is open (otherwise that Enter could pick an option for you).
- **Multi-choice** (CT 6.3.0+): when several options can all be true at once, the Tower may mark a question it or a Worker asked as
  multi-choice; breakpoint pauses are always single-choice. Answer with several codes: `U-3：A、C` (`、`, `,`, `，` or a space between
  them; repeats are ignored; the Tower lists them back in the options' order, recommended first). One code is a single choice; anything that is not all codes counts as your own words. Several options may be
  marked 「（推薦）」. The menu lets you tick several and has no drop choice: type 「放棄」 in "Other" to drop it (the ticks are then not
  applied); other words in "Other" make the whole answer free text, recorded together with the ticks. As text, the pause adds the line
  「可複選：回 `U-n：A、C`」. BAT 0.8.0-pre.8 or later draws ticks in the inbox tab.
- **Answering in the inbox tab while a menu is open** (CT 6.4.0+, with BAT 0.8.1-pre.4 or later): you can answer in BAT's inbox tab
  even while the Tower's menu is open. BAT closes the menu and then sends your answer. The other questions in that closed menu are not
  asked again in a menu: they stay open, and you answer them in the inbox tab or the terminal. A new pending item still gets its own menu,
  with only the new questions. Say 「重問 U-n」 if you want the closed questions back in a menu. Before opening a menu the Tower writes
  `menu_open` (which `U-n` are in it) so BAT knows the answer belongs to that menu.
- **Mixing versions**: CT 6.2.0 with an older BAT (0.8.0-pre.3) still shows the inbox tab; there is no marker or drop button, but the
  recommended option is first with 「（推薦）」 and typing `U-n：放棄` in the free-answer box works. A newer BAT with CT 6.1.x shows neither
  feature; everything else works as before. The contract stays v2 (`bat_contract: 2`); CT 6.2.0 adds `inbox_features` to tell BAT.
  CT 6.3.0 adds `multi` to `inbox_features`: with a BAT older than 0.8.0-pre.8 the question shows as single-choice, and typing
  `U-n：A、C` in the free-answer box still works; BAT 0.8.0-pre.8 or later with CT 6.2.x shows no ticks.
  CT 6.4.0 adds `menu` to `inbox_features` and writes `menu_open`: an older BAT ignores both and keeps working as before; BAT
  0.8.1-pre.4 or later with CT 6.3.x or older falls back to its own default for answering while a menu is open.
  **A new BAT (0.8.1-pre.4 or later) with a CT 6.3.x Tower**: the questions left unanswered in a closed menu may be reopened by the 6.3.x
  Tower as a new menu, so when you answer them one by one from the inbox tab, each one costs one more Esc that BAT presses for you;
  CT 6.4.0 does not reopen them.
  **A new BAT with a CT 6.2.x Tower**: the 6.2.x Tower may decide on its own to open its native menu as multi-choice, but it does not write
  `multi` into the file, so BAT shows the question as single-choice, and 6.2.x reads a multi-choice answer as your own words (it never
  applies the wrong option; it just takes one more round to agree). To use multi-choice, upgrade the Tower to CT 6.3.0.
- **Any terminal**: while something waits for you, every Tower reply ends with one line such as
  `⏸ 待你決定：U-3（T0123）；🙋 待你執行：A-2（…）`. This works without BAT and with an old BAT. If that line feels noisy,
  `*config pending_reminder on-change` (CT 6.2.0+, add `--save project` to keep it) prints it only in the first reply of a session, when
  a new item is added, when you ask what is pending, and after you close a pause menu with Esc.
- **Not writing the lists**: `*config user_inbox off` (add `--save project` to keep it) stops CT from writing the decision and to-do lists into
  the file; the reply-end line still appears.
- **Two kinds of hooks, not the same thing**:
  - BAT's hooks report to BAT what the Tower's Claude is doing (turn ended, waiting on a dialog, the last message for the turn cards).
    BAT adds them by itself to the Claude tabs it opens. You need BAT's optional `bat-hooks` plugin only when you start `claude` by hand in a
    shell tab, put `--settings` in the agent's custom arguments, or turned off BAT MCP in BAT's Settings. At startup the Tower prints one line
    when BAT reports `hooks: none (<reason>)`, with what to do.
  - CT's own hooks are a separate matter and not part of contract v2.
  - CT never installs a plugin for you and never changes your claude settings.
- **Versions**: both sides must be new enough — BAT 0.8.0-pre.3 or later and CT 6.1.0 or later. If either side is
  older, BAT's inbox tab says which version is needed and stays off; an old BAT simply has no inbox tab, and the Tower prints one fallback
  line at startup and keeps working. The recommended marker and the drop controls need BAT 0.8.0-pre.4 or later and CT 6.2.0 or later.
  Multi-choice ticks need BAT 0.8.0-pre.8 or later and CT 6.3.0 or later; "drop words are only a reason" is CT 6.3.0 or later.
  Answering in the inbox tab while a menu is open, with the menu's other questions not reopened, needs CT 6.4.0 or later and BAT
  0.8.1-pre.4 or later.

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
