---
name: ct-done
description: "Control Tower Worker recovery-close skill for remedially closing a work order after interruption, missed closeout, manual status correction, or Tower recovery. Use when the user invokes $ct-done or /ct-done with a T#### work order and optionally a final status such as DONE, FIXED, PARTIAL, BLOCKED, or FAILED."
---
<!-- ct-done-version: 5.14.0 -->

# ct-done

Close or repair the closeout of one existing Control Tower work order. Use this only for recovery; normal execution should close through `ct-exec`.

Arguments: `$ARGUMENTS`

## Role

Act as a Worker doing closeout repair. Do not implement new product work unless the user explicitly changes scope. Preserve existing report evidence and add missing closeout data.

## Workflow

1. Parse work order id/path and optional requested status.
2. Locate and read the complete work order.
3. Read project instructions if needed for closeout rules.
4. Determine the final status from explicit argument, existing report evidence, or user confirmation.
5. Collect current evidence: `git status`, relevant `git diff --name-only`, recent commits, validation notes, and existing report content.
6. Fill missing report fields first.
7. Update metadata only after the report is complete.
8. Commit the work order file itself before any notify (v5.7.0+): `git commit --only <work order file> -m "<message with the work order id>"`
   (add it first if untracked; with `CT_HOME` set, commit it in `$CT_HOME` as § Worktree Isolation says). Commit only that file —
   product changes are never committed for the user here; § Commit Check still reports them.
9. Notify Tower or show exact manual fallback message.

## Landing Zone Check

Run the Landing Zone Check before any write action, exactly as defined in
`../ct-exec/SKILL.md` § `Landing Zone Check` — C-0 (repo identity, load-bearing,
`WRONG_REPO_CONFIRMED` on mismatch), C-1 (work order belongs to this repo), C-3
(`affects_files` spot check, secondary/heuristic; `WRONG_REPO_SUSPECTED` only when the work
order has no `repo` field), and C-2 (branch comparison), plus recording the observed
`BAT_WORKSPACE_ID`.

That section is the single authoritative definition. Do not restate the rules here; load it
and follow it. `ct-done` writes final status into a work order, so a wrong-repo run corrupts the record of a work order that was never executed here — run the check before the first edit, not after.

## Worktree Isolation

When `CT_HOME` is set (BAT worktree, v5.3.0+), apply `../ct-exec/SKILL.md` § Worktree Isolation to this
closeout: read and write the work order only under `$CT_HOME/_ct-workorders/` and commit it there with
`git -C "$CT_HOME" commit --only`, never stage the worktree's `_ct-workorders/` copy, collect evidence and look
for the work order's commits on the worktree branch `ct/T####`, leave no uncommitted changes in the worktree,
and add the `branch` / `base_sha` / `validated_sha` / `head_sha` report fields. That section is the single
authoritative definition; do not restate it here. With `CT_HOME` unset, this skill behaves exactly as in v5.2.6.

## Status Selection

Use exact statuses:

- `DONE`: scoped objective is complete.
- `FIXED`: bug-fix work is implemented and awaits verification.
- `PARTIAL`: some gates passed but scoped work remains incomplete.
- `BLOCKED`: completion needs external input, auth, environment, vendor state, or Tower decision.
- `FAILED`: attempted path did not satisfy the objective.
- `ABANDONED` or superseded final-state: only when a scope decision retires the work.

If the current status is `PARTIAL`, check whether the blocker has since been resolved by a later work order, scope decision, or final acceptance. If resolved, add a post-resolution note and correct status to `DONE`; do not keep resolved partials in active tracking.

## Report Repair

Preserve existing content. Add only missing closeout evidence:

- result summary
- final status and rationale
- files changed or relevant artifacts
- validation evidence and skipped gates
- commit SHA or reason no commit exists
- deviations, blockers, and follow-up recommendations
- post-resolution note for resolved partials

If the work order's own steps require syncing `sprint-status.yaml` and that step was missed, do it as part of the repair (Tower re-checks it at intake: `../control-tower/references/work-order-system.md` § sprint-status.yaml 同步).

For frontmatter work orders, frontmatter is metadata SoT and body table is a human mirror. Use quoted ISO 8601 timestamps with offset.

## Commit Check

This check is about the work order's product commits. The work order file itself is committed by § Workflow step 8 (v5.7.0+).

If worker policy requires or recommends a commit:

1. Check recent commits for the work order id.
2. If the product changes are missing, tell the user they appear uncommitted (do not commit them yourself).
3. Do not invent a commit SHA.
4. Do not commit unrelated dirty files.
5. Never push unless explicitly authorized.

`ct-done` may finish without a product commit only when policy allows or the user confirms the recovery closeout should proceed.
If the work order file commit in step 8 fails, record why and still show the manual Tower message; do not claim it was committed.

## BAT Notify

Use `CT_MODE` for notify behavior. Do not read Tower config to decide mode.

Message mapping (`<工單 ID>` = the full work order id exactly as `/ct-done` received it, i.e. the frontmatter `id`, prefix included,
never cut down to `T` plus digits: `LB-T0184 完成`, not `T0184 完成`; without a prefix: `T0341 完成`. The same id goes into
`--source`. Single authority: `../control-tower/references/work-order-system.md` § 回報與通知用的工單 ID):

- `DONE` / `FIXED`: `<工單 ID> 完成`
- `PARTIAL`: `<工單 ID> 部分完成`
- `FAILED` / `BLOCKED`: `<工單 ID> 需要協助`

`<工單 ID> 提問` (v5.5.0+) is also a legal Tower string, but only `ct-exec` sends it, mid-execution under `CT_MODE=yolo`
(`ct-exec/SKILL.md` § Questions For Tower). `ct-done` is a closeout and never sends it. When recovering a work order whose
frontmatter still has `tower_question: open`, close it with the status the evidence supports (usually `BLOCKED`) and keep the questions.
`ct-done` never uses the BAT question channel (`ct-exec` § Questions For Tower, v5.7.0+) either.

Helper path order:

1. `BAT_HELPER_DIR\bat-notify.mjs`
2. `C:\Program Files\BetterAgentTerminal\resources\scripts\bat-notify.mjs`

Rules:

- `CT_MODE=on`: notify without `--submit`.
- `CT_MODE=yolo`: notify with `--submit`.
- `CT_MODE=ask` / `off` / missing: show manual or clipboard fallback.
- Before notifying or showing the manual message, compare the id you are about to use with the frontmatter `id`; if they differ,
  use the frontmatter value (v5.13.1; steps and the report line in the authority above).
- If a bash-backed helper cannot see `BAT_*`, verify with native PowerShell on Windows before declaring BAT unavailable. List variable names only, never values (`../control-tower/references/auto-session.md` § 偵測條件).
- If notify fails, record the exact failure and show the exact manual Tower message.

## Error Handling

- Work order not found: list candidates and stop.
- Multiple matches: ask for exact path.
- Work order still `PENDING`: it was never started. Say so, suggest `ct-exec`, and stop without editing it.
- Already final: do not rewrite unless user confirms repair.
- No evidence for final status: ask the user for the intended status.
- Frontmatter/body drift: use frontmatter and record drift; avoid broad rewrites.
