---
name: ct-exec
description: "Control Tower Worker skill for executing a work order end to end from any sub-session. Use when the user invokes $ct-exec or /ct-exec with a T#### work order, asks a worker to start or resume scoped execution, or needs the full lifecycle of reading the work order, marking IN_PROGRESS, implementing only the listed scope, validating, writing the report, committing when required, and notifying Tower or providing a fallback completion message."
---
<!-- ct-exec-version: 5.15.0 -->

# ct-exec

Execute exactly one Control Tower work order in a Worker session.

Arguments: `$ARGUMENTS`

## Role

Act as Worker, not Tower. The work order file is authoritative. Read it fully, execute its explicit steps, update its report and metadata, and stop at scope boundaries.

Use Traditional Chinese for user-facing discussion unless the work order or user requests another language. Preserve exact paths, commands, IDs, commit hashes, enum values, API names, and error text.

## Startup

1. Parse `$ARGUMENTS` for a work order id or path.
2. Locate the file under `_ct-workorders/` (under `$CT_HOME/_ct-workorders/` when `CT_HOME` is set; see § Worktree Isolation); if multiple match, stop and ask for the exact target.
3. Read project instructions first when present: `AGENTS.md`, `_ct-workorders/_local-rules.md`, and product guidance such as `CLAUDE.md`.
4. Read the complete work order, including frontmatter, body metadata table, execution steps, validation gates, exclusions, and report template.
5. Record the real current time with timezone before editing.

## Mode And Environment

Runtime mode is passed by Tower. Worker must not read Tower config to decide dispatch mode.

- `CT_MODE`: legal values are `yolo`, `ask`, `off`, `on`.
- `CT_INTERACTIVE`: `1` allows research interaction; `0` forbids it; missing means follow work order metadata.
  With `CT_MODE=yolo` (v5.5.0+) the Worker never asks the user, whatever `CT_INTERACTIVE` says; it asks Tower instead (§ Questions For Tower).
- `interaction.mode_hint` in work order frontmatter is informational only.
- Reading `_tower-config.yaml` or `~/.claude/control-tower-data/config.yaml` is allowed only for worker tuning values such as retry limits or commit policy, not for runtime mode.

BAT detection rules:

- Check the real owning shell. If a bash-backed helper cannot see `BAT_*`, verify on Windows with native PowerShell, listing names only: `Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object`. Detection lists variable names only and never prints values; `BAT_REMOTE_TOKEN` is recorded only as "set" (single authoritative rule: `control-tower/references/auto-session.md` § 偵測條件).
- Treat PowerShell-visible but helper-shell-empty BAT vars as `shell env visibility mismatch`, not as non-BAT.
- Worker notify requires `BAT_TOWER_TERMINAL_ID`, `BAT_REMOTE_PORT`, and `BAT_REMOTE_TOKEN`.
- Use helper path order: `BAT_HELPER_DIR\bat-notify.mjs`, then `C:\Program Files\BetterAgentTerminal\resources\scripts\bat-notify.mjs`.
- `--submit` is valid only when `CT_MODE=yolo`.

## Worktree Isolation (`CT_HOME`, v5.3.0+)

This section is the single authoritative definition of Worker behavior inside a BAT worktree.
`ct-done` applies it to its own closeout by reference and does not restate it. Dispatch-side rules
(`--isolation worktree`, exit `7`) live in `../control-tower/references/auto-session.md` § worktree 隔離派工;
merging the branch back is Tower work, defined in `../control-tower/references/merge-workorder.md`.

**Detection.** The Worker is in a worktree exactly when `CT_HOME` is set. BAT `>= 0.7.0-pre.2` injects it,
together with `CT_WORKTREE` (worktree path, contains the cwd), `CT_WORKTREE_BRANCH` (`ct/T####`) and
`CT_WORKTREE_BASE` (40-char base SHA), only into tabs dispatched with `--isolation worktree`. Apply the same
shell-visibility rule as for `BAT_*`: if a bash-backed helper sees nothing, check native PowerShell
(`Get-ChildItem Env:CT_* | Select-Object -ExpandProperty Name | Sort-Object`, names only) before concluding it is absent.

**`CT_HOME` not set → this section does not apply, and every other section of this file behaves exactly as in
v5.2.6.** All rules below are conditional on `CT_HOME`.

When `CT_HOME` is set:

1. **Work order lives in the main checkout.** Read and write the work order only at
   `$CT_HOME/_ct-workorders/<file>`. The worktree's own `_ct-workorders/` is a read-only copy taken at base —
   never edit it and never stage anything under it in the worktree.
2. **Work order commits go to the main checkout**, touching only that file:
   `git -C "$CT_HOME" commit --only _ct-workorders/<file> -m "<message with work order id>"`.
   (If the file is untracked there, `git -C "$CT_HOME" add -- _ct-workorders/<file>` first.)
3. **Product changes stay in the worktree.** Edit and commit product files only in the worktree, on its current
   branch `ct/T####`. Never edit product files under `$CT_HOME`, never switch branches, merge, rebase, or push.
4. **Landing check C-0** compares the work order `repo` with `basename "$CT_HOME"` instead of
   `basename(REPO_ROOT)`, because the worktree's toplevel directory is named `T####`
   (PowerShell: `Split-Path -Leaf $env:CT_HOME`). C-0 keeps its meaning: load-bearing, `WRONG_REPO_CONFIRMED`
   STOP on mismatch. C-1 checks that the work order sits under `$CT_HOME`. C-3 runs against the worktree
   (`REPO_ROOT`) as usual. Record `CT_HOME` and `CT_WORKTREE_BRANCH` in the landing evidence.
5. **Dependencies.** BAT does not install dependencies, so the worktree may lack `node_modules` and similar.
   Install them the way the project documents (check the project's `CLAUDE.md` / `AGENTS.md`) before running
   validation gates that need them. If the project documents nothing, record that in the report.
6. **Commit everything before closeout.** `git -C "$CT_WORKTREE" status --porcelain` must be empty when the report
   is written: commit product changes on `ct/T####`, and remove or commit anything else that shows up (report which).
   A dirty worktree is not removed by BAT's `--worktree remove` cleanup. This applies even when the commit policy
   would otherwise skip the commit, because the branch is the deliverable.
7. **SHA evidence in the report** (add these fields; the template mirror is in
   `../control-tower/references/work-order-template.md` § 回報區):
   - `branch`: `$CT_WORKTREE_BRANCH`
   - `base_sha`: `$CT_WORKTREE_BASE`
   - `validated_sha`: `git -C "$CT_WORKTREE" rev-parse HEAD` at the moment the validation gates ran
   - `head_sha`: `git -C "$CT_WORKTREE" rev-parse HEAD` after the last product commit
   If `validated_sha` differs from `head_sha`, explain why (which commits came after validation and why they do not
   need re-validation), or re-run validation. Tower's direct-merge rule requires them to be equal.
8. **Closeout order** stays reverse-order (§ Phase 4): product commit in the worktree → record the SHAs → fill the
   report in `$CT_HOME` → final metadata → work order commit in `$CT_HOME` → notify.

## Landing Zone Check

Run this before **any** write action: before editing the work order, before touching product
files, before committing. It is the last line of defense against executing a correct work order
against the wrong repository, and it does not assume the dispatcher passed correct parameters.

```
0. REPO_ROOT = git rev-parse --show-toplevel
   Not a git repo -> record WARN, skip C-0, C-1 and C-3, continue.
```

Check order and weight:

| Check | Weight | STOP on failure? |
|---|---|---|
| **C-0** repo identity | 🔴 **load-bearing** | Yes — `WRONG_REPO_CONFIRMED` |
| C-1 work order path | cheap sanity | Yes, but rarely fires (see below) |
| C-3 `affects_files` spot check | secondary / heuristic | Only when the work order has **no** `repo` field |
| C-2 branch comparison | advisory | No |

### C-0 — Repo identity (load-bearing)

```
When the work order frontmatter has a `repo` field:
    expected = repo
    actual   = basename(REPO_ROOT)
    expected != actual
        -> 🔴 STOP. Report WRONG_REPO_CONFIRMED, listing BOTH values
           (expected repo, actual basename) and the resolved REPO_ROOT.
           Do not guess. Do not continue.
           🔴 Do not edit the work order's `repo` field to make the check pass.
    expected == actual
        -> ✅ PASS. C-3 is then informational: still run it and still record the
           result, but it no longer STOPs on its own.

When the work order frontmatter has NO `repo` field:
    -> ⚠️ Record WARN "repo identity unavailable".
       Fall back to the C-3 + C-1 verdict for the landing decision.
       Missing field is NEVER by itself a STOP — old work orders and work orders
       created by other Towers legitimately lack it.
```

`repo` is the repo root's **directory name**, not a path and not a display name:

```bash
basename "$(git rev-parse --show-toplevel)"   # -> BMad-Guide
```

In a BAT worktree (`CT_HOME` set, v5.3.0+), `actual` is `basename "$CT_HOME"` instead; see
§ Worktree Isolation item 4. With `CT_HOME` unset the comparison above is unchanged.

Do not compare against `project`. That field names a mono-repo sub-project or a PLAN/BUG
record, not a repository; the two are deliberately separate fields with different meanings.
See `../control-tower/references/work-order-template.md` § `repo`.

**Why C-0 is the load-bearing check.** Landing failure is a question of *identity* — "am I in
the repo this work order was written for?" — and identity needs an external signal. Path
existence cannot supply one: "correct repo, work order creates the whole tree" and "wrong repo
entirely" are **structurally identical** under pure path tests, so no depth threshold, ratio, or
other path-only metric separates them. C-0 answers the identity question directly, at the cost
of one field the Tower fills in when it writes the work order.

### C-1 — Work order belongs to this repo

Confirm the located work order file path sits under `REPO_ROOT` (under `$CT_HOME` when `CT_HOME`
is set; see § Worktree Isolation item 4).
Mismatch -> 🔴 STOP and report. Do not guess.

C-1 is cheap but **not** the load-bearing check: a Worker looks for the work order under its own
cwd, so a wrong cwd usually means the id is simply not found. Only an id collision produces a
false hit here — and C-0 catches that case outright. Keep C-1, never lean on it.

### C-3 — `affects_files` spot check (secondary / heuristic)

Take the first 5 entries of frontmatter `affects_files`, excluding:

- entries containing a wildcard (`*`, `?`, `[`)
- entries under `_ct-workorders/` (the work order itself — no discriminating power)

For each remaining entry, resolve its **nearest existing ancestor** under `REPO_ROOT`:
test the path itself, then its parent, then that parent's parent, and so on.

- The path exists -> **testable, present**.
- The path does not exist but an ancestor above `REPO_ROOT` does -> **testable, present**.
  A work order may legitimately create new files, so the file itself is allowed to be missing;
  in the right repo some ancestor of it almost always exists already.
- Only `REPO_ROOT` itself exists on the whole chain -> **testable, absent**. Nothing of the
  expected tree is here, which is the signature of a wrong repo.

Verdict — what "all testable entries absent" costs depends on C-0 and on
`landing_check.expect_missing`:

| Result | C-0 PASSed, or `expect_missing: true` | C-0 unavailable (no `repo` field) |
|---|---|---|
| All testable entries absent | ⚠️ Record WARN, continue. C-0 already answered the identity question, or the work order declared that it builds this tree itself. | 🔴 **STOP**. Report `WRONG_REPO_SUSPECTED` with every path checked and the resolved `REPO_ROOT`. Do not guess, do not continue, do not create the missing directories to make the check pass. |
| Some present, some absent | ⚠️ Record in the report, continue. | ⚠️ Record in the report, continue. |
| No testable entries | ℹ️ Record `C-3 not applicable`, continue. | ℹ️ Record `C-3 not applicable`, continue. |

### `landing_check.expect_missing` — the escape valve

A work order may declare in its frontmatter:

```yaml
landing_check:
  expect_missing: true
```

It means: *the execution steps of this work order create the tree that `affects_files` points
at, so those paths are expected to be absent at start.* With it set, a C-3 `absent` verdict
records WARN instead of STOP. **C-0 is unaffected and still STOPs.**

This is **not** a general-purpose mute switch:

- Only the Tower sets it, and only when the work order genuinely creates its own target tree.
- 🔴 **A Worker must never add this field to make a failing check pass.** The correct response
  to a landing STOP is to report it to the Tower — not to edit the work order until it goes
  quiet. A Worker adding this field is disabling the guard.
- It does not cover "the file should exist but I cannot find it". That is exactly the signal
  C-3 exists to catch.

Absent from frontmatter, it defaults to `false`.

**Why C-3 was demoted from load-bearing to secondary (v5.0.5).** C-3 was measured, not
guessed. The Tower replayed **34 real work orders / 65 `affects_files` entries** from the
repo of another project (project A) as if a Worker had landed in `BMad-Guide` by mistake:

| C-3 rule | Wrong-repo landings stopped |
|---|---|
| immediate parent only (the rule as originally specified) | **34 / 34 — 100%** |
| nearest existing ancestor (the rule as shipped in v5.0.4) | **14 / 34 — 41%** |

The failure mechanism: `docs/api/*.md` walks up to `docs/` — a top-level directory name both
repos happen to have. And because STOP requires **every** testable entry to be absent, a single
generically-named entry disarms C-3 for the whole work order.

Reverting to the immediate parent is not the fix — see the ancestor-walk note below; it would
restore detection at the price of false STOPs on every "create a new version tree" work order.
The real conclusion is that **path existence cannot decide repo identity at all**, so C-3 is now
a heuristic that supports the identity check rather than substituting for it.

**C-3 still earns its place** in the case C-0 cannot cover: a work order with **no `repo`
field** — an old work order, or one written by another Tower. There, C-3 + C-1 remain the only
landing signal available, and C-3 keeps its original STOP power.

Work order ids collide across projects — one project's `T0047` is another project's `T0047` —
so the id alone discriminates nothing, which is why the landing check needs `affects_files` or
`repo` rather than the id.

**Why the ancestor walk, and not just the immediate parent.** A work order whose scope is
"create a new version directory and work inside it" has every `affects_files` entry missing
*and* every immediate parent missing, in the correct repo. Stopping at the immediate parent
turns that ordinary work order into a false `WRONG_REPO_SUSPECTED`, and a guard that cries wolf
gets ignored — which costs more than the check earns. Walking up to the nearest existing
ancestor keeps the false-positive rate low: the STOP condition is still "none of the expected
tree is present here", just stated precisely.

The measurement above shows what the ancestor walk costs — 100% → 41% detection — which is why
🔴 **the ancestor walk is kept and C-0 is added on top, rather than the walk being reverted.**
A guard that cries wolf gets ignored, and that cost outlives the protection it buys. With C-0
carrying the identity decision, C-3 no longer needs the detection rate the immediate-parent rule
had.

### C-2 — Branch comparison

When frontmatter or the body metadata table carries a `branch` field, compare it with
`git rev-parse --abbrev-ref HEAD`.
Mismatch -> ⚠️ warn and ask. With `CT_INTERACTIVE=0`, record WARN and continue: a deliberate
branch switch is a normal reason for the mismatch, so this is never a hard stop.

### Recording

Write the outcome (`PASS` / `WARN` / `STOP`) into the work order report section, naming the
checks that produced anything other than PASS.

Record the C-0 comparison explicitly — the `repo` value from frontmatter (or `absent`) and the
observed `basename(REPO_ROOT)` — so the landing decision is reconstructable from the report.

Also record the observed `BAT_WORKSPACE_ID` value in the report when the variable is present.
This is **evidence only** — it is never compared against anything and never blocks.

### 🔴 C-4 (workspace consistency) is deliberately not implemented

A rejected proposal, recorded so it is not raised again: checking `BAT_WORKSPACE_ID` against
"the workspace this project normally uses" was evaluated and declined.

1. No such field exists. It would require a new `_tower-config.yaml` key.
2. **Workspace IDs are not stable.** The BMad-Guide repo's own workspace id was `c70bda35` in a
   2026-06-05 snapshot and `bc439ad7` on 2026-09-01. Pinning an id in config would produce
   steady false alarms, and a guard that fires wrongly is a guard that gets ignored.

Recording the observed value (above) is the accepted substitute: it preserves the forensic
value without the false positives.

## Phase 1: Start

Update the work order before doing product work:

1. Add or update `started_at` and `updated_at` using quoted ISO 8601 with offset.
2. Change `status` from `PENDING` to `IN_PROGRESS`.
3. Keep frontmatter as metadata SoT when present; body table is the human mirror.
4. If already `IN_PROGRESS`, keep the existing start evidence and note that this is a resume.

Show a short task summary: id, title, current status, scope, key files, explicit exclusions, and validation gates.

## Phase 2: Execute

Follow the work order literally:

- Stay within `affects_files`, execution steps, and exclusions.
- Load only the documents required by the work order and project guidance.
- For frontend/UI work in this repo family, read the relevant FIELDGUIDE and design standards before editing.
- Preserve unrelated dirty files; never revert user changes.
- When the work order has a `### 相關通過案例` section (v5.13.0+, customer acceptance gate), judge each passed case before editing, stop on any case that would change, and fill `### 相關通過案例判定` in the report; the rule lives only in `../control-tower/references/work-order-template.md` § 撰寫〈相關通過案例〉.
- Use existing repo patterns before inventing new abstractions.
- If user input redirects the work, record it in the report and obey the newest instruction unless it makes the work order impossible.
- If the request becomes out of scope, stop and ask whether to finish current scope, record for Tower, or explicitly expand scope.
  With `CT_MODE=yolo`, that question goes to Tower (§ Questions For Tower), not to the user.

For research work:

- Use `CT_INTERACTIVE` first, then work order metadata. With `CT_MODE=yolo`, research questions go to Tower (§ Questions For Tower).
- Ask only task-relevant questions and record Q/A in the report.
- End with a decision-ready conclusion: root cause or findings, options, recommendation, residual risk, and suggested next work order if needed.
- See `../control-tower/references/research-workorder.md` when the work order is research-heavy.

For retry, scope, timeout, and escalation behavior, read `references/session-guardrails.md` only when needed.

### Questions For Tower (`CT_MODE=yolo`, v5.5.0+)

Applies only when `CT_MODE=yolo`. With any other `CT_MODE` (or none) this subsection does not apply and nothing above changes.
The single authoritative definition is `../control-tower/references/yolo-mode.md` § Worker 向塔台提問; this is the Worker summary.

- Never use AskUserQuestion or any other tool that asks the user. Ask only about an in-scope choice you cannot settle from the
  work order, decision log or project conventions, where a wrong guess means rework.
- Write each question as `#### Q-n` under `### 待塔台決策` at the top of `## 回報區` (question, options incl. 「其他」, your
  recommendation and reason, impact, whether it blocks later steps). Do not pre-write any answer line.
- Before sending `<工單 ID> 提問`, check (v5.6.1):
  - frontmatter has `tower_question: open` — required on both paths, waiting in place or going straight to the fallback
    (`worker_question_timeout = 0`);
  - the work order (with the questions and `tower_question: open`) is committed, and so are product changes the commit policy says
    to commit. Commit before notify, here and for every other notify; commit rules are § Phase 4 › Commit rules, and in a worktree
    § Worktree Isolation items 2, 3 and 8;
  - every `#### Q-n：` heading carries the question text and is followed by its 「提問時間」 line (v5.7.1, same as § Phase 4 self-check (a));
    take its value as `../control-tower/references/yolo-mode.md` § Worker 端 第 2 點 says (v5.8.1).
- The three steps above (write the questions, add `tower_question: open`, commit) are the same whether or not the BAT channel is used
  (v5.7.0, written to both places). Then send each question once, by exactly one of the two ways below; never both.
- BAT channel (v5.7.0+, BAT `>= 0.7.0-pre.7`; authority § Worker 端 3-A, with the commands, exit codes, result fields and the
  version/fallback table in § BAT 通道): unless `worker_question_timeout = 0`, send each question with `bat-notify.mjs --ask`, question
  text on stdin only (never in argv), then keep calling `bat_wait_question` (fallback `--wait-answer --timeout-ms`) until it ends.
  The 120 s lease counts per question (v5.15.0): every question needs its own first wait within 120 s of its `--ask`, and no gap over
  120 s between two of its waits; waiting on one question never renews another. Each wait's timeout is `min(45, floor(90 / K))` s for
  K questions still waiting; wait on all of them each round, at the same time when the platform can (at most 8), otherwise in turn,
  doing nothing else in between. `answered` → log it in `### 互動紀錄` and continue. Any failure of the channel (`--ask` fails, `lost`, `cancelled`, the wait
  tools fail) drops that question to the work order wait below; `expired` goes to the fallback. `--ask` carries the notification itself:
  never send a plain one for a question whose `--ask` succeeded.
- Several questions (v5.15.0, authority § Worker 端 3-A steps 1–2): only the last notification of a batch of N wakes Tower.
  a. Send questions 1 … N-1 with `--ask --no-pty-write` (no `--submit`; the two flags are mutually exclusive: both → exit `1`,
     `ask: USAGE`, nothing registered). Each one that fails gets a line `- **通道**：工單` at the end of its `#### Q-n`.
  b. If any got the marker, commit the work order.
  c. Send question N with `--ask --submit`. Success → no plain `提問`.
  d. Question N fails → mark it, commit, then send one plain `<工單 ID> 提問` — right after each other, nothing in between (v5.15.0):
     questions 1 … N-1 are still pending in BAT and Tower is not awake yet. BAT `>= 0.7.2-pre.4` also prints `ask: NOTIFY_STEP <step>`; optional,
     record it if you like, but never let it change the flow (older BAT does not print it).
  Then start waiting at once (every question within 120 s of its own `--ask`). One question: just `--ask --submit`, as before.
- Late drop (v5.7.2, authority § Worker 端 3-A step 6): a question whose `--ask` succeeded but that drops to the work order wait later
  (`lost`, `cancelled` including your own cancel with `status: cancelled worker`, or no usable wait tool) also gets the marker line;
  commit the work order, send one plain `<工單 ID> 提問` (one for all questions dropping at the same time), then wait for its answer line.
  This is the only write allowed while waiting. A `--cancel-question` that reports `answered` (handle as answered) or `expired`
  (fallback) gets no marker.
- Otherwise notify `<工單 ID> 提問` the same way as § BAT Notify And Fallback (yolo: `--submit`) and wait in place (authority § Worker 端 3-B):
  re-read your own work order with the platform's wait/monitor tool, interval ≥ 30 s, until every question has a
  `塔台答覆 Q-n` line; limit = `worker_question_timeout` minutes, resolved as defined in the authority (frontmatter → project config →
  global config → default). Then log each answer in `### 互動紀錄` as `[HH:MM] Q-n: … → A（塔台）: … → Action: …`, continue.
- Delete `tower_question` once every question is answered, by either channel.
- An answer counts only as a line starting with `- **塔台答覆 Q-n**` inside `### 待塔台決策` or a `## 塔台補充（Renew #N）` section
  (v5.6.1). The same words elsewhere in the work order body are not an answer, so never decide by grepping the whole file for
  `塔台答覆 Q-n`. Lines inside fenced code blocks do not count either (v5.7.1). The section-scoped `awk` check, which skips fenced
  code blocks, is in the authority, § Worker 端 3-B.
- Fallback — timeout, `worker_question_timeout = 0`, BAT `expired`, no usable wait tool for the work order wait (say so in the report),
  or the `提問` notify failed: finish the report with the questions kept and `tower_question: open`, set `BLOCKED`, commit the work order
  (with `BLOCKED`) and product changes, cancel any question still waiting on the BAT channel (v5.7.0+), then notify `<工單 ID> 需要協助`.
  Tower answers in `## 塔台補充（Renew #N）` and re-dispatches.

### Workflow And Sub-Agents (v5.11.0+)

This subsection is the single authoritative definition of when a Worker may call the Claude Code **Workflow** tool and how it records
the sub-agents it starts itself. Tower-side governance (the `workflow_integration` setting, when Tower may write an authorization) lives
in `../control-tower/references/workflow-engine.md` § 同意治理; the authorization template lives in
`../control-tower/references/work-order-template.md` § 撰寫 Workflow 使用授權. The Worker never reads config to decide this (D062).

**Workflow tool: only with an explicit authorization in the work order.**

- Call the Workflow tool only when the work order carries a `Workflow 使用授權` block that names each authorized run (workflow name
  or script, data, purpose) and the cap of each run: agent count and a post-hoc token cap. No such block → never call it, under any
  `CT_MODE`, however well the work seems to fit; write the idea under follow-ups for Tower instead.
- Do only the listed runs. Anything else — a re-run, another data set, more agents than the cap, a raised cap — is out of scope:
  stop before it and ask Tower (yolo: § Questions For Tower; otherwise as for any scope question).
- Token use cannot be read while a run is going; compare it with the cap after each run. A run over its token cap: record it,
  do not re-run it, and ask Tower before starting the next authorized run, unless the block itself says to finish the remaining runs.
- Record each run in the report: authorization row, `runId`, agents, tokens (tool-reported), duration, skipped items (`dropped`).
- No Workflow tool in this session (for example a Codex Worker): do not emulate it under the authorization's name with other tools.
  Do the work without Workflow if the work order allows that, otherwise ask Tower; record which.
- The design rules R1–R5 in `../control-tower/references/workflow-engine.md` still apply (read-only shapes, no `isolation: 'worktree'`).

**Sub-agents the Worker starts itself (general Agent tool, not Workflow).**

- No authorization is needed for read-only sub-agents that read in parallel within the work order's scope; writes stay with the main
  Worker and within `affects_files`, as for any other work.
- When any were used, the report must say so under `### 子代理與 Workflow 使用`: how many, what for, whether read-only and how that was
  enforced (agent type plus an explicit no-write prompt; an Explore agent still has a shell, see R4), approximate tokens (the tool-reported
  total when shown; otherwise state how it was estimated, e.g. "~31k fixed per agent + bytes read ÷ 1.9"), and what the main Worker
  spot-checked. Neither used → leave the section out.

```markdown
### 子代理與 Workflow 使用
| 種類 | 數量 | 用途 | 唯讀（怎麼保證） | tokens | 備註 |
|---|---|---|---|---|---|
| 子代理（Agent 工具） | 3 | 平行讀 3 份來源 | 是（Explore＋prompt 禁止寫入） | ~210k（工具回報） | 主 agent 抽查 2 項 |
| Workflow | 1 | 授權表 #1 | 是 | 548k（事後上限 450k，超出） | `runId` wf_…；dropped 70 |
```

## Phase 3: Verify

Run the validation gates named in the work order. If a gate cannot run, record the exact blocker and do not imply PASS.

Separate evidence lanes:

- source or docs checks
- build and tests
- runtime smoke
- deployment
- release or installed-bundle verification
- external SIT or customer confirmation

Use `PASS`, `PARTIAL`, `BLOCKED`, or `FAILED` with concrete evidence.

## Phase 4: Report And Commit

Use reverse-order closeout to avoid watchers seeing terminal status before the report exists. Since v5.7.0 this is the same order as
§ Worktree Isolation item 8 (which still governs in a worktree):

1. Commit the product changes first, when the work order or worker policy requires a commit, so the report can record their hashes.
2. Fill the report section: result summary, files changed, validation evidence, commit status (the product commit hashes), deviations,
   blockers, and follow-ups.
3. Include interaction history and Renew history when present, and sub-agent / Workflow use when any (v5.11.0+, § Workflow And Sub-Agents).
4. Only after the report is complete, update final metadata status and completion timestamps.
   Then self-check the work order before step 5 (v5.7.1; checks only, the formats themselves are unchanged):
   (a) every `#### Q-n：` heading under `### 待塔台決策` carries the question text and is followed by its 「提問時間」 line;
   (b) the report section has no template placeholder text left, such as 「（Worker 填寫）」;
   (c) there is exactly one `### 互動紀錄` section.
   (b) or (c) fails: fix it, then continue. (a) fails (v5.8.1): do not edit a question already sent, since Tower may have answered it
   as written; record under `### 遭遇問題` which question and what is missing, then continue.
5. Commit the work order file (report and final metadata), when a commit is required, before any notify.
6. Then notify Tower (§ BAT Notify And Fallback).

With no commit required, skip steps 1 and 5 and say so in the report.

Status rules:

- `DONE`: scoped acceptance criteria passed.
- `FIXED`: bug-fix implementation completed and awaits verification.
- `PARTIAL`: some scoped gates passed but at least one remains incomplete.
- `BLOCKED`: needs external input, auth, environment, vendor state, or Tower decision.
- `FAILED`: attempted approach did not satisfy the objective.
- `ABANDONED` or superseded final-state: use only when the work order is intentionally retired by scope decision.

When the work order splits its steps between Worker and Tower (v5.6.1), judge the status on the Worker steps only. Missing evidence
for Tower steps is not a reason for `PARTIAL`; Tower fills those in. Tower marks which steps are its own when it writes the work order
(`../control-tower/references/work-order-template.md` § 撰寫 verification 工單的驗收步驟).

Commit rules:

- Commit only when the work order or policy requires or recommends it.
- Commit message must include the work order id.
- Use `git commit --only` or precise staging when unrelated dirty files exist.
- Never push unless the work order explicitly says the user authorized push.
- If commit cannot be made, record why and continue closeout only when policy allows.

## BAT Notify And Fallback

After metadata/report closeout:

`<工單 ID>` below is the full work order id exactly as `/ct-exec` received it — the frontmatter `id`, prefix included, never
cut down to `T` plus digits (`LB-T0184 完成`, not `T0184 完成`; without a prefix: `T0341 完成`). The single authority is
`../control-tower/references/work-order-system.md` § 回報與通知用的工單 ID; it covers `--source`, the message, `--ask` and the
manual fallback message.

1. Map status to fixed Tower message:
   - `DONE` / `FIXED`: `<工單 ID> 完成`
   - `PARTIAL`: `<工單 ID> 部分完成`
   - `FAILED` / `BLOCKED`: `<工單 ID> 需要協助`
   - Still `IN_PROGRESS` with open questions for Tower (`CT_MODE=yolo` only, v5.5.0+): `<工單 ID> 提問` — sent mid-execution by
     § Questions For Tower, not at closeout. The Tower-side regex is `../control-tower/references/yolo-mode.md` § 斷點 A.
     On the BAT channel (v5.7.0+) the same message is sent by `bat-notify.mjs --ask` itself; do not send it again. Within a batch only the
     last `--ask` (the one with `--submit`) wakes Tower; the earlier ones use `--no-pty-write` (v5.15.0, § Questions For Tower).
   Before every send — closeout notify, `--ask`, or the manual fallback message — compare the id you are about to use with the
   frontmatter `id` and use the frontmatter value if they differ (v5.13.1; steps and the report line in the authority above).
2. If `CT_MODE=on`, run `bat-notify.mjs` without `--submit`.
3. If `CT_MODE=yolo`, run `bat-notify.mjs --submit`.
4. If `CT_MODE=ask` or `off` — or `CT_MODE` is missing or invalid, which the Worker treats as `ask` (`../control-tower/references/auto-session.md` § Mode 與互動旗標協定 › Worker 側讀取規則) — never add `--submit` (`--submit` is yolo-only, see § Mode And Environment); show the exact manual Tower message as the clipboard/manual fallback. This is the same rule as `ct-done` § BAT Notify.
5. If notify fails in `on`, record failure and show clipboard/manual fallback.
6. If notify fails in `yolo`, do not claim auto-submit succeeded. Mark the closeout evidence honestly and tell the user the exact manual Tower message.

Notify command pattern:

```bash
"${BAT_HELPER_NODE:-node}" "<helper>\\bat-notify.mjs" --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" [--submit] "<工單 ID> 完成"
```

`"${BAT_HELPER_NODE:-node}"`: unset locally → `node`; remote PTYs (WSL / SSH / Docker) get BAT's bundled node. The authoritative rule, including the PowerShell form, is `../control-tower/references/auto-session.md` § 執行方式 › Node 解析.

If BAT notify is unavailable, show the exact manual message for Tower. Use clipboard only when the platform supports it reliably; on Windows prefer PowerShell `Set-Clipboard` for Unicode.

## Frontmatter Rules

For v1 work orders:

- Frontmatter is machine SoT.
- Body metadata table is a human mirror.
- Write list fields as YAML block lists.
- Write timestamps as quoted ISO 8601 with offset.
- Do not silently fallback unknown statuses to `PENDING`.
- If frontmatter/body drift exists, use frontmatter and record the drift rather than rewriting unrelated content.

## Error Handling

- Missing work order: list likely matches and stop.
- Work order already final: ask before reopening or changing.
- Work order has contradictory scope: stop and report the contradiction.
- Validation blocker: record as `PARTIAL` or `BLOCKED` with the exact gate.
- Repeated same failure: stop after the configured retry threshold and write a structured blocker report.

## Reference Routing

- `references/session-guardrails.md`: retries, scope guard, strikeout, timeout, onion-problem handling.
- `../control-tower/references/research-workorder.md`: research work order interaction and Renew rules.
- `../control-tower/references/work-order-template.md`: metadata/report shape.
- `../control-tower/references/merge-workorder.md`: only for a merge work order (frontmatter `kind: merge`, v5.3.0+) — Worker scope, guardrails, and report requirements per merge mode.
- `../control-tower/references/auto-session.md` and `../control-tower/references/yolo-mode.md`: BAT and YOLO dispatch contracts.
- `../control-tower/references/workflow-engine.md`: only when the work order authorizes the Workflow tool (v5.11.0+) — rules R1–R5 and the Tower-side governance; the Worker rule itself is § Workflow And Sub-Agents in this file.
- `## Landing Zone Check` in this file is the single authoritative definition of the landing-zone rules; `ct-done` and `ct-status` reference it rather than restating it. Change it here only.
