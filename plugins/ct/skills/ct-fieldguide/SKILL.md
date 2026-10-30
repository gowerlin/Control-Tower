---
name: ct-fieldguide
description: "Control Tower FIELDGUIDE and DESIGN.md automation skill. Use when the user invokes $ct-fieldguide or /ct-fieldguide, asks to initialize, update, audit, extract, merge, or promote FIELDGUIDE.md guidance, or asks to generate or audit DESIGN.md visual standards from code or a URL."
---
<!-- ct-fieldguide-version: 5.14.3 -->

# ct-fieldguide

Generate, update, audit, and promote project FIELDGUIDE and DESIGN.md knowledge. This is a Worker skill; Tower should create or route work orders when changes are substantial.

Arguments: `$ARGUMENTS`

## Role

Act as a documentation and governance Worker. Read project rules, inspect only the scoped files, and write FIELDGUIDE/DESIGN artifacts when the command requires it. Do not modify product code unless a work order explicitly says so.

## Write Boundaries

- Project FIELDGUIDE files live under the scoped project, often `src/<subproject>/FIELDGUIDE.md`.
- Project visual standards usually live under `docs/design-standards/` or a work-order-specified path.
- Global FIELDGUIDE promotion lives under `~/.claude/control-tower-data/` only when explicitly requested.
- Do not write installed skill definitions.
- Preserve existing sections unless the command asks for a rewrite.

## Command Routing

| Command | Action | Reference |
|---|---|---|
| `init` | Create an initial FIELDGUIDE from CLAUDE.md, repo conventions, and key source patterns. | `references/fieldguide-format.md` |
| `update` | Patch specific FIELDGUIDE sections from recent work order evidence or explicit source findings. | `references/fieldguide-format.md` |
| `audit` | Compare FIELDGUIDE against actual code and report drift, missing rules, stale paths, or debt. | `references/global-fieldguide.md` |
| `audit --debt` | Find multiple competing implementations of the same convention. | `references/extraction-patterns.md` |
| `extract` | Produce a structured inventory without immediately merging. | `references/extraction-patterns.md` |
| `merge` | Merge an extraction result into a target FIELDGUIDE after conflict review. | `references/fieldguide-format.md` |
| `promote` | Evaluate project rules for global promotion. | `references/global-fieldguide.md` |
| `design` | Generate or audit DESIGN.md from code or URL. | `references/design-extraction.md` |

If no command is supplied, infer the safest read-only action from the request. Prefer `audit` over writing when intent is unclear.

## Fieldguide Init

1. Read project guidance such as `CLAUDE.md`, `AGENTS.md`, existing FIELDGUIDE, and local rules.
2. Identify stack, folder ownership, standard components, API patterns, validation patterns, routing, auth, and testing conventions.
3. Sample representative code rather than bulk-reading the repo.
4. Write concise rules with examples and "when to use" context.
5. Mark uncertain findings as candidates rather than rules.

## Update

1. Read the target section before editing.
2. Read only the work order, report, source snippet, or candidate evidence needed.
3. Apply the smallest patch that keeps the guide internally consistent.
4. Avoid duplicating DESIGN.md visual rules inside FIELDGUIDE; link or bridge them.

## Audit

Report findings first:

- stale path or component references
- undocumented but repeated conventions
- conflicting implementations
- FIELDGUIDE rules contradicted by current code
- visual hardcoding that belongs in DESIGN.md

Include evidence paths and recommend whether to update FIELDGUIDE, DESIGN.md, work orders, or code.

## DESIGN.md Extraction

Use `references/design-extraction.md` for detailed code and URL extraction. Keep the output practical:

- design tokens and CSS variables
- typography and spacing scale
- color usage and hardcoded colors
- component states and layout rules
- responsive breakpoints
- accessibility constraints
- framework-specific UI conventions

Do not infer a brand system from one-off values without evidence.

## Promotion

Promote project rules to global only when:

- the rule is repeated across projects or explicitly requested,
- trigger and action are general enough,
- project-specific names are removed or clearly scoped,
- conflicts with existing global guidance are reviewed.

Use `[FG-CANDIDATE]`, `[FG-DEBT]`, and `[FG-PROMOTE]` tags consistently so Tower and `ct-evolve` can track maturity.

## Output

For write commands, report:

- files changed
- sections added or updated
- evidence used
- uncertain candidates
- validation or audit result

For read-only commands, do not edit files and label the result as audit/extraction only.

## Error Handling

- Missing target guide: offer `init`.
- Multiple possible target guides: ask for exact subproject.
- Conflicting section content: show conflict and request direction before overwriting.
- URL extraction blocked: fall back to static analysis if possible and mark screenshots/runtime unavailable.
