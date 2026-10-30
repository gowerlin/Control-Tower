# v6.11.0 And v6.12.0 Migration And Rename Map

> Source basis (v6.12.0 delta): `bmad-method` v6.12.0 tag, dereferenced commit `05bfbd46d00766ec88eb9b42e76be2c575d64d7b`, `package.json`, `src/bmm-skills/v6-shims/README.md`, `src/core-skills/v6-shims/README.md`, `src/bmm-skills/v6-shims/bmad-checkpoint-preview/SKILL.md`, `src/bmm-skills/ship/bmad-walkthrough/SKILL.md`, `src/bmm-skills/plan/bmad-generate-project-context/SKILL.md`, `tools/installer/core/shim-policy.js`, `tools/installer/commands/install.js`, `src/bmm-skills/module-help.csv`, `src/bmm-skills/agents/*/customize.toml`, `src/bmm-skills/ship/bmad-build/` and `bmad-build-auto/` (`spec-template.md`, `step-04-review.md`), `src/bmm-skills/ship/bmad-code-review/steps/step-03-triage.md`, `src/core-skills/bmad-review/SKILL.md`, `src/bmm-skills/plan/bmad-project-context/references/best-practices.md`, `removals.txt`, `docs/reference/skills-and-agents.md`, and the `CHANGELOG.md` v6.12.0 section.
>
> Source basis (v6.11.0 sections A–J): `bmad-method` v6.11.0 tag, dereferenced commit `9ce3c397c9b238de96f7365da8019f6f66b059da`, `package.json`, `src/bmm-skills/v6-shims/README.md`, `src/core-skills/v6-shims/README.md`, `src/core-skills/bmad-review/customize.toml`, `src/bmm-skills/module-help.csv`, `src/core-skills/module-help.csv`, `src/bmm-skills/agents/*/customize.toml`, `docs/reference/workflow-map.md`, `docs/reference/agents.md`, `docs/reference/build-auto.md`, `removals.txt`, `bmad-modules.yaml`, and the `CHANGELOG.md` v6.11.0 section. Rows changed by v6.12.0 are marked in place.
>
> The filename keeps `v6-11` so that existing pointers keep resolving; it now covers both releases.

This file answers one question: **"I used to run X. What do I run now?"**

v6.11.0 is the largest rename/merge release in the v6 line. Core drops from fourteen skills to eight, the three research skills become one, the five review/editorial skills become lenses on one skill, and Quick Dev becomes Build. Users still have old installs, old notes, old scripts, and old customization files that name the old IDs, so the guide must recognize every retired name and route it.

v6.12.0 is a much smaller rename release — one skill renamed (`bmad-checkpoint-preview` -> `bmad-walkthrough`) — but it changes **whether old IDs exist at all**: deprecated shims are no longer installed on a fresh install unless asked for.

## How To Use This File

1. User upgrading from v6.11.x -> read **Upgrading From v6.11.x** first.
2. User names an old skill ID, artifact, or menu code -> find it in the tables below.
3. Answer with: current status, the replacement, and **how the replacement is triggered** (intent, lens code, research type, or menu code).
4. Since v6.12.0, also say whether the old ID resolves on their install — see the Shim Policy.
5. If the user has customization TOML files, check section H — **overrides do not follow renames automatically**.
6. If the item is in section J, say so explicitly instead of asserting it as fact.

## Shim Policy (read this first)

- Retired v6 IDs live in `src/core-skills/v6-shims/` and `src/bmm-skills/v6-shims/`. The folder is **grouping only**: the installer discovers skills recursively and installs each under its own `name`, so nesting does not change any installed path or skill ID.
- **Since v6.12.0, shims are opt-in on fresh installs.** The installer treats every skill whose frontmatter has `metadata.lifecycle: shim` as a shim (`tools/installer/core/shim-policy.js:19-21`, `isShimSkill()`), and `inferShimPreference()` (`:92-99`) decides whether to install them:

  | Install | Shims installed? |
  |---------|------------------|
  | Fresh install, no flag | **No** — old IDs do not resolve |
  | `--shims` / `--no-shims` passed (`tools/installer/commands/install.js:37-38`) | As requested |
  | Existing install, no flag | The saved preference if one exists; otherwise **yes** only if the old skill manifest shows a shim was installed |

  So "calling the old ID still works" is true only where shims are installed. In v6.11.0 they shipped by default and calling the old ID always worked.
- **Upstream contradiction:** both `v6-shims/README.md` files still say the shims "ship by default" and that "a future install option will let users include or exclude this folder". The shipped installer and the `CHANGELOG.md` v6.12.0 Breaking list ("Deprecated shims are opt-in on fresh installs. Pass `--shims` to keep them.") say otherwise. This guide follows `shim-policy.js`.
- There are **two different kinds of shim**, and conflating them is the most common mistake:
  - **Forwarding shim** — holds no logic; forwards to the replacement with a stated intent, type, or lens pre-set.
  - **Retained in full** — the whole original workflow is still there and still runs when invoked by name. It has only left the default routing (agent menu, `bmad-help` recommendations, workflow map). `bmad-create-story` and `bmad-dev-story` are this kind. Both carry `lifecycle: shim`, so on a fresh v6.12.0 install without `--shims` they are absent too.
- Both `v6-shims/README.md` files state: "Removal rides the v7 cut — never a 6.x minor." No specific version number or date is published (see section J).
- A **deprecated skill is not always in `v6-shims/`**. Judge deprecation by the skill's own `SKILL.md` frontmatter, not by which directory it sits in — `bmad-generate-project-context` is deprecated and forwarding while still living in `src/bmm-skills/plan/`. v6.12.0 added `metadata.lifecycle: shim` to its frontmatter (`plan/bmad-generate-project-context/SKILL.md:4-5`; v6.11.0 had no such field), so it is now opt-in on fresh installs like the rest.

## Upgrading From v6.11.x (v6.12.0 Delta)

Breaking items come from the `CHANGELOG.md` v6.12.0 section and were each confirmed in source; the rest were found by diffing the v6.11.0 and v6.12.0 trees.

### `bmad-checkpoint-preview` -> `bmad-walkthrough`

| Old | New | Evidence |
|-----|-----|----------|
| Skill `bmad-checkpoint-preview` | `bmad-walkthrough` (`src/bmm-skills/ship/bmad-walkthrough/`) | `module-help.csv` line 17 |
| Menu code `CK` | `WT` | `module-help.csv` line 17 (v6.11.0 same line: `CK`) |
| Customization `_bmad/custom/bmad-checkpoint-preview.toml` / `.user.toml` | `_bmad/custom/bmad-walkthrough.toml` / `.user.toml` | `v6-shims/bmad-checkpoint-preview/SKILL.md:12-18` |

`bmad-walkthrough` is **not** on any agent menu: `WT` exists only in `module-help.csv`, and the Developer (Amelia) menu stays `BD`, `QA`, `CR`, `SP`, `ER`. Invoke it directly or by saying "walkthrough", "walk me through this change", or "human review".

The old ID is a forwarding shim (`lifecycle: shim`), so it exists only where shims are installed. When it does run, its On Activation flow (`v6-shims/bmad-checkpoint-preview/SKILL.md:10-21`) is:

1. Check for `_bmad/custom/bmad-checkpoint-preview.toml` and `_bmad/custom/bmad-checkpoint-preview.user.toml`.
2. Neither exists -> print the deprecation notice and invoke `bmad-walkthrough` once with the user's input verbatim.
3. A legacy file exists and the matching `bmad-walkthrough*.toml` does **not** -> offer to rename it; rename only after explicit approval. Declined, unavailable, or failed -> **HALT, invoke nothing**.
4. A legacy file exists and the matching new file **also** exists -> never overwrite. Read both, explain the differences, propose the merged content, and save it only after explicit approval; then verify the new file and delete the legacy one. Declined, unavailable, or failed -> **HALT, invoke nothing**.
5. Only after every legacy file is migrated -> print the notice and forward.

Consequence: an unattended run that names `bmad-checkpoint-preview` in a project with an un-renamed override **refuses to start**. Rename the file before the upgrade (section H).

### Everything else that changed

| Change | What to do | Evidence (v6.12.0 tree) |
|--------|------------|-------------------------|
| **Shims opt-in on fresh installs** | Pass `--shims` if scripts, notes, or external modules still call old IDs; otherwise switch them to the current IDs | `tools/installer/core/shim-policy.js:92-99`; `commands/install.js:37-38`; see Shim Policy |
| **`persistent_facts` ships empty** | `project-context.md` is no longer auto-loaded. Re-add it to `persistent_facts` in your override if you relied on it, or let `bmad-project-context` absorb it into `AGENTS.md`. Scope: in v6.11.0, 31 shipped `customize.toml` files listed it (the five agents plus workflows such as `bmad-prd`, `bmad-build`, `bmad-spec`, `bmad-party-mode`); in v6.12.0 all 34 files with the key ship `persistent_facts = []` | e.g. `agents/bmad-agent-dev/customize.toml:38`; `CHANGELOG.md` v6.12.0 Breaking |
| **`{diff_output}` -> `{diff_file}`** | Update custom review-layer overrides. `{diff_file}` is a path to a unified diff file, not the diff text; `{claims_file}` is substituted the same way | `ship/bmad-build/customize.toml:78-79`; `bmad-build/step-04-review.md`; `bmad-code-review/steps/step-01-gather-context.md`, `step-02-review.md` |
| **Build Auto `followup_review_recommended` formula** | Orchestrators that read the flag see a stricter rule. v6.11.0: `true` if any patched finding was `high`, or `3 × medium + 1 × low >= 5`. v6.12.0: first pass `true` if any patched entry was `high` or two or more `medium` were patched; follow-up pass `true` only if a `high` was patched; a `true` must name the unverified risk, otherwise it is `false` | `ship/bmad-build-auto/step-04-review.md:103` (v6.11.0 same file `:83`) |
| **Spec tiers trimmed** | Custom spec templates or overrides that fill these tiers need updating. Build spec: "Ask First" tier removed (Boundaries is Always / Never); human-gated choices move to a new `## Open Questions` section, and the spec cannot leave `draft` while an entry remains. Build Auto spec: "Block If" tier removed | `ship/bmad-build/spec-template.md:26-33,46-54`; `ship/bmad-build-auto/spec-template.md:28-34` (v6.11.0: `bmad-build/spec-template.md:31`, `bmad-build-auto/spec-template.md:34`) |
| **Build triggers more narrowly** | Do not expect Build to volunteer for interactive edits, git bookkeeping, or formatting / configuration-hygiene chores; explicit BMAD requests still qualify | `ship/bmad-build/SKILL.md:3` |
| **Build sizes the ceremony after investigating** | Small clean changes take the `oneshot` light path with a two-section spec; the route is stored in spec frontmatter `route` | `ship/bmad-build/spec-template.md:6`; `CHANGELOG.md` v6.12.0 |
| **`bmad-review` triggers only when asked** | It runs only when the user actually says "review" (or another skill issues an explicit `skill:bmad-review` directive), never uninvited; acting on earlier review feedback is a change, not a review. New optional `claims` input goes to the edge-case lens alone | `core-skills/bmad-review/SKILL.md:3,17` |
| **`bmad-code-review` triage order** | Each finding gets one verdict (`high` / `medium` / `low` / `false` / `maybe-false`) with evidence **before** grouping; survivors are then grouped only by shared root cause. Reviewer-assigned severity is ignored | `bmad-code-review/steps/step-03-triage.md:19-41` |
| **Project-context admission test reversed** | Do not quote the v6.11.0 rule "leave out what an agent can derive from the repo". v6.12.0 asks what it costs when the agent does **not** derive it; a derivable line that stops repeated rediscovery now earns its place | `plan/bmad-project-context/references/best-practices.md:5-9` |
| **`bmad-project-context` `adopt` intent** | A handwritten `AGENTS.md` is kept as the baseline instead of being rewritten | `plan/bmad-project-context/SKILL.md:12,87-91` |
| **`llms.txt` / `llms-full.txt` no longer published** | Point tools at the docs site instead | `CHANGELOG.md` v6.12.0 Breaking; `module-help.csv` `_meta` rows |
| **Docs reorganized by task** | Old `docs/reference/*`, `docs/explanation/*`, `docs/how-to/*` links are dead; see `update-protocol.md` § Sources that no longer exist | `docs/{start,plan,build,customize,existing-codebases}/` |

Not changed in v6.12.0: the five agent menus (code by code), the review lens codes, `bmad-modules.yaml`, and Web Bundles (`web-bundles/` is file-for-file identical to v6.11.0). See section I.

## A. Renamed — Forwarding Shims

All rows are forwarding shims with `lifecycle: shim` in v6.12.0; each resolves only where shims are installed.

| Old ID | Status (v6.12.0) | Route to | How to trigger the replacement |
|--------|------------------|----------|-------------------------------|
| `bmad-checkpoint-preview` | Forwarding shim (**renamed in v6.12.0**) | `bmad-walkthrough` | Invoke `bmad-walkthrough` directly (`WT` is not on any agent menu). Rename customization files first — see section H |
| `bmad-quick-dev` | Forwarding shim | `bmad-build` | Invoke `bmad-build` directly, or Dev agent menu code `BD` |
| `bmad-dev-auto` | Forwarding shim | `bmad-build-auto` | Invoke `bmad-build-auto` directly (orchestrator surface) |
| `bmad-create-prd` | Forwarding shim | `bmad-prd` | `create` intent |
| `bmad-edit-prd` | Forwarding shim | `bmad-prd` | `update` intent |
| `bmad-validate-prd` | Forwarding shim | `bmad-prd` | `validate` intent |
| `bmad-create-architecture` | Forwarding shim | `bmad-architecture` | `create` intent, or Architect menu code `CA` |
| `bmad-sprint-status` | Forwarding shim | `bmad-sprint-planning` | Status view — menu code `SS` dispatches it with `action=status` |

`bmad-sprint-status`'s unused data and validate modes had zero callers and are gone; the status view survives.

## B. Merged — One Skill Absorbed Several

### Review and editorial -> `bmad-review` (lenses)

Five skills became **lenses** on a single `bmad-review`. A lens is a pass over the content with its own method, keyed by `code` in `[[workflow.lenses]]`.

| Old ID | Route to | Lens `code` | Lens applies to |
|--------|----------|-------------|-----------------|
| `bmad-review-adversarial-general` | `bmad-review` | `adversarial` | any |
| `bmad-review-edge-case-hunter` | `bmad-review` | `edge-case-hunter` | any (content with behavior to trace) |
| `bmad-review-verification-gap` | `bmad-review` | `verification-gap` | code, inside a repo where tests can be read |
| `bmad-editorial-review-structure` | `bmad-review` | `structure` | docs |
| `bmad-editorial-review-prose` | `bmad-review` | `prose` | docs, runs `after = "structure"` |
| `bmad-editorial-review` | `bmad-review` | `structure` + `prose` together | docs |

The lens `code` values above are read from `src/core-skills/bmad-review/customize.toml`, which is the authoritative source. Note that `src/core-skills/v6-shims/README.md` writes the second one informally as "edge-case lens"; the actual code is `edge-case-hunter`. Unchanged in v6.12.0.

`bmad-editorial-review` keeps its own `customize.toml` so existing team and user overrides still resolve, and the shim forwards those resolved values to `bmad-review`.

### Research trio -> `bmad-deep-recon` (types)

| Old ID | Route to | Pre-set `type` |
|--------|----------|----------------|
| `bmad-market-research` | `bmad-deep-recon` | `market` |
| `bmad-domain-research` | `bmad-deep-recon` | `domain` |
| `bmad-technical-research` | `bmad-deep-recon` | `technical` |

Existing overrides on the old IDs are honored by the shims. `bmad-deep-recon` adds three more type packs the old trio never had: `competitive`, `user-voice`, `academic-lit`.

### Project documentation -> `bmad-project-context`

| Old ID | Status (v6.12.0) | Route to | Trigger |
|--------|------------------|----------|---------|
| `bmad-document-project` | Forwarding shim | `bmad-project-context` | `setup` intent |
| `bmad-generate-project-context` | Deprecated forwarder, **still located in `src/bmm-skills/plan/`**; `lifecycle: shim` since v6.12.0 | `bmad-project-context` | `setup` intent |

The deliverable changes shape, not just name: no generated overview, source-tree, or deep-dive pages, and **no `project-context.md`** — just one verified block in the repository's `AGENTS.md`. An existing `project-context.md` is offered up for absorption at `setup`. In v6.11.0 it also auto-loaded through `persistent_facts`; since v6.12.0 it does not (see the delta table above).

### Readiness gate -> `bmad-sprint-planning`

| Old ID | Status | Route to | Trigger |
|--------|--------|----------|---------|
| `bmad-check-implementation-readiness` | Removed outright (v6.11.0), capability folded in | `bmad-sprint-planning` | Opens with the readiness gate (PASS / CONCERNS / FAIL); PM and Architect menu code `IR` forwards there |

The new gate finds artifacts **by content** instead of the filename globs that used to miss `SPEC.md` and `DESIGN.md`. This ID is listed in `removals.txt`, so existing installs clean it up.

## C. Removed — No Replacement

| Old ID / concept | Route instead |
|------------------|---------------|
| `bmad-index-docs` | Nothing. Retired outright, listed in `removals.txt`. |
| `bmad-shard-doc` | Nothing. Retired outright; the "shard large documents" how-to is gone from all five locales. |
| `bmad-agent-tech-writer` (Paige) | No direct replacement. Project context lives on through the Analyst (Mary) menu code `PC`, or invoke `bmad-project-context` directly. For talk of a successor agent, see section J. |
| `bmad-investigate` | Plain investigation, `bmad-help`, a research workorder, or `bmad-build` once the intent is concrete. Retired since v6.10.0, still listed in `removals.txt`. |
| `bmad-create-ux-design` | `bmad-ux`. Retired before v6.10.0, still listed in `removals.txt`. |

## D. Deprecated But Retained In Full

These are **not** forwarding shims. The complete workflow is still present and still runs.

| Old ID | What actually changed |
|--------|----------------------|
| `bmad-create-story` | Moved into `v6-shims/` in v6.11.0, marked **"Retained in full"**. Dev agent menu drops `CS`; the skill leaves `bmad-help` recommendations and the workflow map. Invoking it by name still executes the full original workflow. Removal rides the v7 cut. |
| `bmad-dev-story` | Same treatment; Dev agent menu drops `DS`. |

Do not tell a user these forward to `bmad-build`. They do not. The correct statement is: deprecated, off the default Phase 4 chain, still fully executable when named **and installed**, removal expected at v7. Since v6.12.0 they carry `lifecycle: shim`, so a fresh install without `--shims` does not include them.

## E. Same ID, New Location Or Phase (v6.11.0)

| Item | What changed |
|------|--------------|
| `bmad-spec` | Moved from core into bmm (`src/bmm-skills/plan/bmad-spec/`) and is now presented as a **Phase 2 Planning** workflow. Core-only installs no longer get it. |
| `bmad-sprint-planning` | Moved from Phase 4 into **Phase 3 Solutioning**, and absorbed the readiness gate. Lives in `src/bmm-skills/plan/`, not `ship/`. |
| `bmad-brainstorming` | Output is now a `brainstorm.html` keepsake plus an optional `brainstorm-intent.md`. |
| bmm skill tree | Reorganized into verb-named folders: `src/bmm-skills/{agents,plan,ship,v6-shims}/`. |
| Phase 4 chain | Converged to `bmad-sprint-planning -> bmad-build -> bmad-code-review`. |
| Phase 4 reviewers | `bmad-code-review`, `bmad-build`, and `bmad-build-auto` now own local `review-prompts/*.md` copies instead of routing through `bmad-review` lenses, which had changed their semantics and output guarantees. |

v6.12.0 moved `bmad-checkpoint-preview` into `src/bmm-skills/v6-shims/` and added `bmad-walkthrough` under `src/bmm-skills/ship/`; no other skill changed location.

## F. Artifact And Frontmatter Field Changes

### v6.11.0

| Old artifact / field | v6.11.0 replacement |
|----------------------|---------------------|
| `{output_folder}/project-context.md` | The `<!-- bmad:context -->` ... `<!-- /bmad:context -->` managed block inside the repo root `AGENTS.md`. Existing files are offered for absorption. |
| `deferred-work.md` (**Build Auto only**) | The Build Auto spec frontmatter `deferred:` list. Each item carries `summary`, `evidence`, optional `location`, optional `severity`. Interactive `bmad-build` **still writes** `deferred-work.md` (v6.11.0 `step-01-clarify-and-route.md:86`; v6.12.0 same file `:87`) — an earlier revision of this guide wrongly listed it as retired for Build as well. |
| `final_revision` (frontmatter) | Gone. Compute a story's commit range as `baseline_revision..<next story's baseline_revision>`, or `baseline_revision..HEAD` at exit. |
| `bmad-dev-auto-result-<slug-or-timestamp>.md` | `bmad-build-auto-result-<slug-or-timestamp>.md` |
| Review triage labels `blind` / `edge` / `vgap` / `auditor` | Findings are tagged by review-layer `id` instead. |
| Build Auto's two separate intent-gap halt strings | Unified to the single string `intent gap`. |
| `docs/reference/dev-auto.md` (upstream source) | `docs/reference/build-auto.md` (itself gone in v6.12.0) |

New artifacts that did not exist in v6.10.0: `stories.yaml` (optional `bmad-spec` Story Breakdown output, sibling of `SPEC.md`), `<spec-folder>/stories/<story-id>-<slug>.md`, `{spec-folder}/RETROSPECTIVE.md`, and the `_bmad/render/` content-addressed snapshot tree.

### v6.12.0

| Old artifact / field | v6.12.0 replacement |
|----------------------|---------------------|
| Review placeholder `{diff_output}` (diff text) | `{diff_file}` (path to a unified diff file); `{claims_file}` added |
| Build spec "Ask First" tier | Removed; `## Open Questions` section, which blocks leaving `draft` |
| Build Auto spec "Block If" tier | Removed |
| — | Build spec frontmatter `route` (`oneshot` \| `dispatch`) |
| — | `## Review Triage Log` section in the Build and Build Auto specs |
| `persistent_facts` entries pointing at `project-context.md` | `persistent_facts = []` in every shipped `customize.toml` |
| `llms.txt`, `llms-full.txt` | No longer published |

## G. Menu Code Changes

| Agent | Change |
|-------|--------|
| Developer (Amelia) | v6.11.0: `QD` -> `BD` (Build). `CS` and `DS` dropped with `bmad-create-story` / `bmad-dev-story`. Current menu (unchanged in v6.12.0): `BD`, `QA`, `CR`, `SP`, `ER`. |
| Analyst (Mary) | v6.11.0: `DP` -> `PC` (Project Context). Deep Recon adds `TS` (select / choose-between), `CR` (competitive), `UV` (user-voice). Current menu per `bmad-agent-analyst/customize.toml` (unchanged in v6.12.0): `BP`, `MR`, `DR`, `TR`, `TS`, `CR`, `UV`, `CB`, `WB`, `PC`. |
| Product Manager (John) | `IR` now dispatches the `bmad-sprint-planning` readiness gate. Menu: `PRD`, `CE`, `IR`, `CC`. |
| Architect (Winston) | Menu: `CA`, `IR` (same forwarding note). |
| UX Designer (Sally) | Menu: `CU`. Unchanged. |
| — (no agent) | v6.12.0: `module-help.csv` code `CK` -> `WT` for `bmad-checkpoint-preview` -> `bmad-walkthrough`. Neither code was ever on an agent menu. |

`CR` means **Code Review** on the Developer menu and **Competitive research** on the Analyst menu. Disambiguate by which agent is active.

Note a v6.11.0 source discrepancy: `docs/reference/agents.md` listed the Analyst triggers as `BP`, `MR`, `DR`, `TR`, `CB`, `WB`, `PC` and omitted `TS` / `CR` / `UV`, which are present in `bmad-agent-analyst/customize.toml`. The `customize.toml` is the shipped menu definition and wins. (`docs/reference/agents.md` no longer exists in v6.12.0.)

## H. Customization File Rename Guide

**Renames do not carry your overrides with them.** This is the highest-impact manual step in the upgrade.

| Old override file | Rename to | Since |
|-------------------|-----------|-------|
| `_bmad/custom/bmad-checkpoint-preview.toml` / `.user.toml` | `_bmad/custom/bmad-walkthrough.toml` / `.user.toml` | v6.12.0 |
| `_bmad/custom/bmad-quick-dev.toml` / `.user.toml` | `_bmad/custom/bmad-build.toml` / `.user.toml` | v6.11.0 |
| `_bmad/custom/bmad-dev-auto.toml` / `.user.toml` | `_bmad/custom/bmad-build-auto.toml` / `.user.toml` | v6.11.0 |
| `_bmad/custom/bmad-sprint-status.toml` | `_bmad/custom/bmad-sprint-planning.toml` | v6.11.0 |
| `_bmad/custom/bmad-document-project.toml` / `bmad-generate-project-context.toml` | `_bmad/custom/bmad-project-context.toml` | v6.11.0 |

Behavior when you skip this: the shim **offers** the migration but requires explicit approval and never overwrites. If you decline, or the migration is unavailable, **the shim halts instead of forwarding**. An unattended run invoking the old name with a legacy customization file present will therefore refuse to start. The `bmad-checkpoint-preview` shim spells this out step by step, including the case where both the old and new file exist (merge proposed, approved, verified, then the legacy file removed) — see **Upgrading From v6.11.x**.

Since v6.12.0 there is a second reason to rename **before** relying on the shim: on a fresh install without `--shims` the shim is not installed at all, so nothing offers the migration and the old-named file is simply never read.

`bmad-editorial-review` is the exception — it keeps its own `customize.toml` and forwards the resolved values, so those overrides keep resolving without a rename.

Two v6.12.0 override edits that are not renames but break the same way if skipped: replace `{diff_output}` with `{diff_file}` in custom review layers, and re-add `project-context.md` to `persistent_facts` if you depended on the auto-load.

Configuration itself also moved to layered TOML in v6.11.0: `_bmad/config.toml` -> `config.user.toml` -> `custom/config.toml` -> `custom/config.user.toml`, and per-skill `{skill}/customize.toml` -> `_bmad/custom/{skill}.toml` -> `.user.toml`. The per-module `_bmad/bmm/config.yaml` still ships and older skills still read it, so v6.11.0 is the migration release, not the cutover. *(Historical note for v6.11.0–v6.12.0. Since v6.12.1 no skill reads `_bmad/bmm/config.yaml` directly: all 23 bmm skills that did, including the v6 shims, load config through `resolve_config.py`, so `_bmad/custom/config.toml` overrides now apply to every skill. The installer still writes the file. CHANGELOG v6.12.1, #3019; see `references/ecosystem-modules.md`, Layered Configuration.)* Renderers now **exit 1 with a clean halt** on a missing config key or an unparseable override, where they previously rendered an empty string or ignored the file.

## I. Unchanged — Verified, Do Not "Migrate" These

Skill IDs that did **not** change in v6.12.0: every skill ID present in v6.11.0 except `bmad-checkpoint-preview`. Comparing the `name:` of every `SKILL.md` under `src/` in both tags, the only difference is the added `bmad-walkthrough` (49 -> 50 IDs; `bmad-checkpoint-preview` remains as a shim). The current, non-shim IDs that users route to are unchanged: `bmad-help`, `bmad-customize`, `bmad-party-mode`, `bmad-advanced-elicitation`, `bmad-brainstorming`, `bmad-forge-idea`, `bmad-deep-recon`, `bmad-review`, `bmad-prd`, `bmad-ux`, `bmad-spec`, `bmad-architecture`, `bmad-create-epics-and-stories`, `bmad-sprint-planning`, `bmad-product-brief`, `bmad-prfaq`, `bmad-project-context`, `bmad-build`, `bmad-build-auto`, `bmad-code-review`, `bmad-correct-course`, `bmad-retrospective`, `bmad-qa-generate-e2e-tests`.

The five agent personas are unchanged: Mary (Analyst), John (PM), Winston (Architect), Amelia (DEV), Sally (UX Designer), with the same menu codes. Web Bundles are unchanged (`releaseTag: web-bundles-v1.0.0`, six bundles; `web-bundles/` is identical between the v6.11.0 and v6.12.0 tags) — upstream `main` has no `web-bundles/`, but `main` is the v7 line, not v6.12. The TEA module is still in the official registry and is **not** deprecated; `bmad-modules.yaml` is unchanged. `sprint-status.yaml` format is unchanged.

## J. Not Verified In Source — Flag These, Do Not Assert Them

When any of the following comes up, say plainly that it could not be confirmed against the v6.12.0 source tree.

| Item | What is actually known |
|------|------------------------|
| Whether the external `bmad-loop` module renamed its worker skill to `bmad-build-auto` | Not verified. `bmad-loop` lives in a separate repo; the v6.12.0 snapshot carries only its registry entry (unchanged from v6.11.0), not its skill content. The main repo's rename means the worker should be `bmad-build-auto` — with `bmad-dev-auto` reachable only where shims are installed — but whether bmad-loop itself has updated cannot be determined from this snapshot. Note that `src/core-skills/v6-shims/README.md` says external module repos (gds, loop, tea, bmb, os-utils) "still invoke" the old review IDs; on a fresh install without `--shims` those calls would not resolve. That interaction is inferred from the two sources, not tested. |
| A successor to Paige | Not verified as a scheduled item, and the sources disagree on its form. `CHANGELOG.md:43` (the v6.11.0 entry, still in the v6.12.0 tree) says "Paige's replacement joins soon as an optional installable agent". `removals.txt:78-80` and `docs/reference/skills-and-agents.md:58-59` say only that Paige is "on hiatus" and will return. No skill, module entry, or version plan exists in the snapshot. Do not state the form or the timing. |
| TEA workflow IDs other than three | Only `bmad-testarch-automate`, `bmad-testarch-test-design`, and `bmad-testarch-trace` are named in the main repo (`docs/build/test-completed-work.md:10,92,95`). Every other TEA ID, command, or menu code comes from TEA's own repo or documentation and was not cross-checked against the main repo. (In v6.11.0 none of the lowercase IDs could be confirmed.) |
| The v7 removal date for the shims | Not verified as a version or date. Both `v6-shims/README.md` files say only "Removal rides the v7 cut — never a 6.x minor." Upstream `main` already carries the v7 structure (`skills/` with `bmod.toml`, no `package.json`), but that is unreleased work, not a release date. |
