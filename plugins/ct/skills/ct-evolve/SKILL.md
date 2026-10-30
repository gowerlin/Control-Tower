---
name: ct-evolve
description: "Control Tower learning extraction skill for distilling work order experience into reusable patterns, anti-patterns, playbooks, or skill candidates. Use when the user invokes $ct-evolve or /ct-evolve, asks what was learned, wants to promote learnings with --playbook, --skill, --workflow, or --status, or needs FIELDGUIDE candidate tagging from repeated execution evidence."
---
<!-- ct-evolve-version: 5.14.3 -->

# ct-evolve

Distill Control Tower execution history into reusable knowledge without polluting long-term memory with raw event logs.

Arguments: `$ARGUMENTS`

## Modes

| Argument | Mode | Behavior |
|---|---|---|
| empty or topic | learning extraction | scan records and propose distilled patterns |
| `--playbook [name]` | playbook promotion | promote validated patterns into reusable playbook material |
| `--skill [name]` | skill candidate | draft a skill-promotion plan, then use `$skill-creator` in a separate authoring turn |
| `--workflow [name]` | workflow brief (v5.10.0+) | draft a Workflow brief and write it as a 🔵 knowledge card; never writes `.claude/workflows/` |
| `--status` | pipeline status | show maturity counts and stale candidates |

## Write Boundaries

- Do not write Layer 1 installed skill definitions (manual-install and plugin-install locations). Path list, scope, and the single exception: see `control-tower/references/data-layer-architecture.md` § 寫入規則 (authoritative definition).
- Project learnings live under `_ct-workorders/`.
- Global learnings live under `~/.claude/control-tower-data/`.
- Workflow knowledge cards (v5.10.0+) live under `_ct-workorders/_workflows/` (project) or `~/.claude/control-tower-data/workflows/` (global, only when Layer 2 exists). Path check: `control-tower/references/workflow-engine.md` § 寫入路徑檢查（知識卡）.
- Never write project workflow scripts (`.claude/workflows/*.js`) or `~/.claude/workflows/`. Scripts are written only by a Worker under a later work order whose `affects_files` lists them, after the user confirms the brief; see `control-tower/references/data-layer-architecture.md` § Layer 3 附屬：專案 workflow 腳本.
- When the user asks to actually edit a skill, switch to the appropriate skill-authoring workflow rather than doing it as `ct-evolve`.

## Extraction Flow

1. Read `_ct-workorders/_learnings.md`, decision log, current Tower state, and relevant completed work orders.
2. Identify candidate patterns, anti-patterns, recurring sequences, estimation misses (actual vs estimate off by more than 50%), review findings, and user corrections.
3. Distill each candidate before writing it.
4. Classify scope: project-only, global, or uncertain.
5. Write only accepted distilled knowledge, preserving existing sections.
6. Report what was added, skipped, or left for review.

If a recurring sequence is complete and 🟢 or above, suggest `--playbook`; never write a playbook from the extraction mode itself.

## Distillation Gate

Every new candidate must answer:

- What happened?
- Why did it happen?
- Under what trigger does it recur?
- What general pattern does it represent?
- What concrete action should future agents take?

Reject or archive candidates that require the original incident to understand. A valid learning should work as an if-then rule in another task.

Preferred format:

```markdown
### P###: <name>
- **Learning**: <one-sentence rule>
- **Trigger**: <condition>
- **Pattern**: <general mechanism>
- **Action**: <repeatable action>
- **Example**: <one concrete anchor>
- **Source**: <date + project + work order>
- **Status**: 🔵/🟡/🟢/⭐
```

## Classification

- Tactical: tool, language, shell, framework, or repo-specific operational know-how.
- Strategic: cross-stack decision pattern likely to remain useful after technology changes.
- Episodic: raw event that is not yet generalizable.

If uncertain, default to Tactical or Episodic rather than overstating generality.

## FIELDGUIDE Bridge

If a distilled candidate concerns coding standards, UI conventions, naming, API format, validation, error handling, typography, colors, spacing, responsive behavior, or design tokens, add a `[FG-CANDIDATE]` tag with a short topic. `ct-fieldguide` can later promote it into FIELDGUIDE or DESIGN.md.

## Workflow Bridge (v5.10.0+)

If a candidate is a work shape that meets the 🔵 candidate grade of `ct-insights/references/analysis-rules.md` § Workflow 適配度 (conditions live only there), add a `[WF-CANDIDATE]` tag with the WFC id or shape name. Repetition *between* work orders is a Playbook candidate (X5), not `[WF-CANDIDATE]`. `--workflow` can later turn the tagged candidate into a brief.

## Promotion Modes

For `--playbook`:

1. Select mature validated learnings.
2. Confirm trigger, steps, inputs, outputs, and failure modes.
3. Write to project or global playbook location only after scope is clear.

For `--skill`:

1. Identify skill-worthy repeated workflow.
2. Produce a concise skill brief: triggers, core workflow, references/assets/scripts needed, validation plan.
3. Do not edit installed skill files unless the user explicitly invokes `$skill-creator`.

For `--workflow` (v5.10.0+; what Workflow is in CT, rules R1–R5, card format and maturity: `../control-tower/references/workflow-engine.md`, the single authority):

1. Pick the source: a `[WF-CANDIDATE]`, a `WFC###` from `ct-insights`, or the named shape `[name]`. Record its evidence work orders.
2. Produce a brief only: subtask source (and whether it can be listed as `args` before execution), stages, the schema of each stage (R1: maps to report sections), verification strategy, whether a worktree is needed (R3: none through v5.11.0; read-only or analysis shapes only), agent / subtask caps and cost estimate (per-agent overhead ~31k; within the session's workflow size guideline), use (工具型 or 派工型), and how it meets R1–R5.
3. Write it as a 🔵 knowledge card in the card format, after the scope question (project or global, as for playbooks; global only when Layer 2 exists) and the card path check.
4. Do not write `.claude/workflows/`, do not write a script, and do not run Workflow, a backtest, or a trial run. The script is written by a separate work order after the user confirms the brief (like `--skill`); any backtest or trial run first lists its estimated size for the user's approval.

For `--status`:

- Count candidate, validated, playbook, and skill-ready items, plus `[WF-CANDIDATE]` tags and Workflow knowledge cards by maturity (v5.10.0+).
- Show stale or duplicate learnings.
- Recommend the next promotion action.

## Reference Routing

Load only when needed:

- `../control-tower/references/self-learning-core.md`
- `../control-tower/references/playbook-engine.md`
- `../control-tower/references/workflow-engine.md` (for `--workflow` and `[WF-CANDIDATE]`)
- `../ct-insights/references/analysis-rules.md` § Workflow 適配度 (for `[WF-CANDIDATE]` conditions)
- `../control-tower/references/skill-writing-conventions.md`
- `../control-tower/references/fieldguide-commands.md`
- `../control-tower/references/enhancement-integration.md` § /ct-evolve Level 1 增強 (only when ECC is present)

## Error Handling

- Missing `_ct-workorders/`: explain that there is no project CT history.
- No completed work orders: report insufficient evidence.
- Ambiguous scope: write nothing and ask for project/global choice.
- Candidate fails distillation: put it in Episodic or report it as skipped.
