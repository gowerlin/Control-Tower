---
name: ct-status
description: "Control Tower status skill for checking work order state from any session. Use when the user invokes $ct-status or /ct-status, asks for one T#### status, all active work, a sync-style status check, frontmatter/body drift, or whether PARTIAL, BLOCKED, DONE, BUG, PLAN, or EXP records are still active."
---
<!-- ct-status-version: 5.15.0 -->

# ct-status

Report Control Tower state from files. Do not mutate files unless the user explicitly asks for a repair.

Arguments: `$ARGUMENTS`

## Modes

| Argument | Behavior |
|---|---|
| `T####` or path | Show one work order status and key metadata. |
| empty or `all` | Summarize hot-zone work orders. |
| `sync` | Compare work order files with `sprint-status.yaml` when available. |
| `active` | Emphasize items that still require Tower or Worker action. |

## Read Order

1. Locate `_ct-workorders/`.
2. Read matching work order files.
3. Prefer YAML frontmatter when present.
4. Fallback to legacy body metadata table only when frontmatter is missing.
5. If frontmatter and body drift, report `metadata_drift` and use frontmatter.
6. Unknown statuses remain `UNKNOWN`; never coerce to `PENDING`.

For `sync`, look for `sprint-status.yaml` in the repo root, `_bmad-output/`, and `docs/`.

## Landing Zone Check

Run the Landing Zone Check before any write action, exactly as defined in
`../ct-exec/SKILL.md` § `Landing Zone Check` — C-0 (repo identity, load-bearing,
`WRONG_REPO_CONFIRMED` on mismatch), C-1 (work order belongs to this repo), C-3
(`affects_files` spot check, secondary/heuristic; `WRONG_REPO_SUSPECTED` only when the work
order has no `repo` field), and C-2 (branch comparison), plus recording the observed
`BAT_WORKSPACE_ID`.

That section is the single authoritative definition. Do not restate the rules here; load it
and follow it. `ct-status` is read-only, so it never STOPs on C-0 or C-3: report the C-0 / C-1 / C-2 / C-3 outcome alongside the status output instead, so a wrong-repo read is visible rather than silently reassuring.

## Status Buckets

- Active: `PENDING`, `IN_PROGRESS`, `PAUSED`, `URGENT`.
- Needs Tower judgment: unresolved `PARTIAL`, `BLOCKED`, `FAILED`, `INTERRUPTED`, `UNKNOWN`.
- Final: `DONE`, `FIXED` only after verification policy allows, `CLOSED`, `WONTFIX`, `DROPPED`, `CONCLUDED`, `ABANDONED`.

`INTERRUPTED` (v5.12.5+) marks an original work order whose session was interrupted after Tower had already opened a follow-up work order or re-dispatched it (`../control-tower/references/work-order-system.md` § 中斷復原). Tower can close it once it confirms the follow-up has taken over; until then report it here with the follow-up id when the work order names one.

`PARTIAL` is point-in-time incomplete. If a later work order, scope decision, or final acceptance resolved the blocker, report it as a resolved partial candidate and recommend Tower correction to `DONE` or superseded final-state.

## Output

Keep output compact and evidence-based:

- id, title, status, timestamps
- scope or affected files when useful
- commit SHA when present
- blocker or next action
- drift or sync mismatch warning
- On sync mismatch, end with the next step: hand it to Tower (`*sync`, or tell the Tower `重新同步`); ct-status itself stays read-only.

For large projects, summarize first and list only active or mismatched items unless the user asks for all details.

## Error Handling

- No `_ct-workorders/`: report that Control Tower is not initialized here.
- No matches: list nearby ids if cheap.
- Missing `sprint-status.yaml`: complete file status report and mark yaml comparison unavailable.
- Invalid frontmatter: report the parse/validation issue and fallback only if the body metadata is parseable.
