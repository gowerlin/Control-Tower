# BMM Supplementary Workflows and Features

## Product Planning Workflows

## v6.10-v6.12 New Feature Routing

| Capability | Status | Route / Skill | Use When |
|------------|--------|---------------|----------|
| Human walkthrough of a change | Renamed in v6.12 | `bmad-walkthrough` (was `bmad-checkpoint-preview`, `CK` -> `WT`) | A person wants to review a commit, branch, PR, or spec in comprehension order |
| Right-sized Build ceremony | Changed in v6.12 | `bmad-build` light path (`route: oneshot`) | A small change with no intent gaps and nothing irreversible should finish in one session |
| Logged review triage | New in v6.12 | `## Review Triage Log` in Build specs; verdict per finding in `bmad-code-review` | You need to see why each finding was patched, deferred, or rejected |
| Adopt handwritten agent instructions | New in v6.12 | `bmad-project-context`, `adopt` intent | A repo already has a handwritten `AGENTS.md` (or similar) without the BMad managed block |
| Opt-in compatibility shims | Changed in v6.12 | Installer `--shims` / `--no-shims` | Old skill IDs must keep resolving on a fresh install |
| Canonical implementation loop | Renamed in v6.11; trigger narrowed in v6.12 | `bmad-build` (was `bmad-quick-dev`) | Delegated features, stories, bug fixes, and meaningful changes — not interactive edits, git bookkeeping, or formatting chores |
| Unattended implementation | Renamed in v6.11 | `bmad-build-auto` (was `bmad-dev-auto`) | One coherent intent can run without human interaction |
| One review skill, many lenses | Consolidated in v6.11 | `bmad-review` | A diff, branch, PRD, spec, story, architecture doc, or any prose document needs review |
| Decision-grade research | Consolidated in v6.11 | `bmad-deep-recon` | An answer should rest on evidence rather than model memory |
| Repo agent instructions | New skill in v6.11 | `bmad-project-context` | AI agents need this repo's verified commands, policy, conventions, and known pitfalls |
| Planning-to-execution contract | New in v6.11 | `stories.yaml` from `bmad-spec` Story Breakdown | A spec needs to be dispatched story by story, autonomously or otherwise |
| Evidence-based epic review | Rebuilt in v6.11 | `bmad-retrospective` | An epic is complete and needs judging against its own artifacts |
| Readiness gate | Folded in during v6.11 | `bmad-sprint-planning` | Planning needs a PASS/CONCERNS/FAIL check before implementation starts |
| Inspectable skill snapshots | New in v6.11 | `_bmad/render/` (automatic) | You need to see exactly what a skill rendered and ran |
| Layered TOML configuration | New in v6.11 | `_bmad/config.toml` chain + `_bmad/custom/{skill}.toml` chain | Config or per-skill behavior needs a persistent override |
| `uv` requirement | Hard requirement in v6.11 | Install `uv` | `bmad-build` and `bmad-build-auto` halt without it — no interpreter fallback |
| Antigravity CLI target | New in v6.11 | Installer picker entry `AGY` | Installing to `.agents/skills` and `~/.gemini/antigravity-cli/skills` |
| Core-only install | New in v6.11 | Module picker | Only the eight core skills are wanted; note `bmad-spec` is no longer core |
| Idea pressure test | Core skill since v6.9 | `bmad-forge-idea` | The idea may not deserve a PRD yet |
| Architecture spine | Preferred since v6.9 | `bmad-architecture` | Requirements or a spec exist and the user is ready to decide how to build |
| Unattended dev-loop orchestrator | Opt-in module since v6.10 | `bmad-loop` + `bmad-loop-setup` | Repeated autonomous iterations need policy, hooks, and review |
| Party rooms and memory | Expanded in v6.9-v6.10 | `bmad-party-mode` | Decisions need multiple perspectives, named rooms, or anti-consensus review |
| Automator | Deprecated | Migrate to `bmad-loop` | Existing Automator users need a migration route |
| Whiteport Design Studio | Deprecated in v6.11 | Features merging into the coming `bmad-ux` package | Existing WDS installs need a migration expectation |

### `bmad-forge-idea`

- **Use when**: An idea needs pressure-testing before PRD, brief, or build commitment.
- **Purpose**: Stress the idea until it hardens, proves out, or dies cheaply.
- **Output**: `{output_folder}/forge` artifacts, including `forge-report.html` every run and `forged-idea.md` when the idea hardens.
- **Next**: `bmad-spec`, `bmad-product-brief`, `bmad-prfaq`, `bmad-prd`, `bmad-build`, or a no-build decision.

### `bmad-product-brief`

- **Use when**: A product idea needs shape before PRD-level rigor.
- **Modes**: Create, Update, Validate.
- **Working styles**: Fast path for a quick draft with assumptions, Coaching path for deeper facilitation.
- **Output**: A brief workspace with `brief.md`, optional `addendum.md`, and decision memory.
- **Next**: `bmad-prd`, `bmad-prfaq`, `bmad-deep-recon`, or `bmad-help`.

### `bmad-prfaq`

- **Use when**: The idea needs a Working Backwards pressure test before commitment.
- **Style**: Direct customer-first challenge; weak customer/problem framing gets pushed back.
- **Output**: `prfaq-{project}.md` plus a downstream PRD distillate.
- **Headless option**: `--headless` / `-H` when enough structured context is already supplied.

### `bmad-prd`

- **Use when**: The project needs a requirements contract for downstream UX, architecture, epics, and implementation.
- **Modes**: Create, Update, Validate — three intents in one skill. State the intent on invocation or the skill will ask.
- **Entry points**: Vision + Features for capability-led work; Journey-led for UX-heavy or multi-stakeholder products.
- **Discipline**: Capabilities and requirements in the PRD; mechanism, technical detail, and overflow rationale in `addendum.md`.
- **Output**: Create/Update produce `prd.md`, `addendum.md`, and `.memlog.md`; Validate produces `validation-report.html` + `.md`.
- **Review integration**: Names explicit `bmad-review` lenses in its `doc_standards`, so the editorial lenses run at finalize.
- **Retired IDs**: `bmad-create-prd`, `bmad-edit-prd`, and `bmad-validate-prd` are forwarding shims in `v6-shims/`. Where shims are installed (opt-in on fresh installs since v6.12.0) they still work and pass the corresponding intent through.
- **Next**: `bmad-ux`, `bmad-architecture`, `bmad-create-epics-and-stories`, or `bmad-help`.

### `bmad-ux`

- **Use when**: UI, interaction, accessibility, surface closure, or experience behavior is a meaningful part of the product.
- **Output**: `DESIGN.md` for visual identity and `EXPERIENCE.md` for behavior, flow, IA, states, journeys, and accessibility, plus `.memlog.md`.
- **Retired ID**: `bmad-create-ux-design` is retired outright and listed in `removals.txt`; route to `bmad-ux`.
- **Design handoff**: Can prepare a producer-shaped prompt for tools such as Google Stitch; the spines remain the source of truth.

## Solutioning

### `bmad-architecture`

- **Use when**: Requirements, a spec, or a feature slice exists and the user is ready to decide how to build. Also any time independently-built parts risk diverging.
- **Purpose**: Produce the architecture spine — the invariants that keep features, epics, and stories consistent. Comes before epics and stories.
- **Entry shapes**: Raw idea, large doc, codebase, feature slice, or existing architecture spine. On brownfield it ratifies the existing codebase.
- **Output**: `ARCHITECTURE-SPINE.md` by default, hydrating to richer architecture artifacts when configured.
- **Review integration**: Names explicit `bmad-review` lenses in its `doc_standards`.
- **Retired ID**: `bmad-create-architecture` lives in `v6-shims/` as a forwarding shim (create intent) and is expected to go away at v7.

### `bmad-sprint-planning`

- **Use when**: Planning artifacts exist and implementation is about to start, or sprint status needs a read.
- **Two faces**: the readiness gate (`SP`, PASS / CONCERNS / FAIL, opens the skill) and the status view (`SS`, dispatched with `action=status`).
- **Absorbed skill**: `bmad-check-implementation-readiness` is removed outright and folded in here. The `IR` trigger on the PM and Architect menus dispatches this gate. The gate finds artifacts by content instead of the filename globs that used to miss `SPEC.md` and `DESIGN.md`.
- **Script core**: `scripts/sprint_plan.py` with `generate` / `status` / `validate` subcommands and JSON-only output owns epic parsing, ordering, preserve-never-downgrade status merging, story-file detection, `action_items` carry-over, atomic writes, and drift checks. Judgment stays with the LLM, and the skill falls back to reading the file directly if a script path fails.
- **Repair and validate modes**: "Fix sprint status" rebuilds a broken or drifted file — subagents gather evidence, you confirm the proposed state, then one `generate --fresh --set key=status ...` writes a pristine file. That is the only path allowed to downgrade a status. "Validate sprint status" reports structural problems without writing.
- **Compatibility**: Legacy v6 statuses (`drafted`, `contexted`) are normalized rather than treated as illegal; refresh preserves custom keys, comments, and `project_key` / `tracking_system` / `story_location`. The `sprint-status.yaml` format itself is unchanged.
- **Retired ID**: `bmad-sprint-status` is a forwarding shim. Migrate `_bmad/custom/bmad-sprint-status.toml` to `bmad-sprint-planning.toml`.

## Spec Kernel

### `bmad-spec`

- **Use when**: The input is messy, mixed, too large, or not yet shaped into a PRD/brief.
- **Purpose**: Distill intent into a canonical machine contract. Locks the WHAT before the HOW.
- **Kernel fields**: Why, Capabilities, Constraints, Non-goals, Success signal.
- **Output**: `{output_folder}/specs/spec-{slug}/SPEC.md` plus companion files for catalogs, diagrams, glossary, conventions, state machines, or adopted upstream artifacts.
- **Location change**: Moved from core into bmm in v6.11.0 (`src/bmm-skills/plan/bmad-spec/`) and is presented as a Phase 2 Planning workflow. **Core-only installs no longer get it.**
- **Sole writer**: It is the only writer of `SPEC.md`; other skills invoke it headless when they need to express or update intent.
- **Scope**: Works for software, game design, research, editorial, policy, business — anything intent-bearing. Validation mode is also available.
- **Not a coaching workflow**: If the input is too thin, use `bmad-forge-idea`, `bmad-product-brief`, `bmad-prd`, or `bmad-brainstorming` first.

### Story Breakdown and `stories.yaml`

An optional `bmad-spec` step emits `stories.yaml` beside `SPEC.md`: a top-level YAML list, one entry per story, in execution order. List order **is** execution order. It is discovered by its fixed filename, never listed in `companions:`, never referenced from frontmatter.

| Field | Required | Meaning |
|-------|----------|---------|
| `id` | yes | Unique quoted string, letters/digits/dashes only. Used for equality and as a filename prefix. Prefix-free: `"3"` and `"3-2"` cannot coexist. No zero-padding. |
| `title` | yes | One line; becomes the story's heading downstream |
| `description` | yes | What this story covers, pointing into `SPEC.md`; keep it to two sentences |
| `spec_checkpoint` | no (`false`) | Caller-only. When true, a human reviews the story spec between planning and implementation |
| `done_checkpoint` | no (`false`) | Caller-only. When true, dispatch pauses after this story completes |
| `invoke_dev_with` | no (`""`) | Free text appended verbatim to the dispatch prompt; only the implementing dev skill reads it |

**There is deliberately no `status` field, ever.** Status lives in the story spec file under `<spec-folder>/stories/<story-id>-<slug>.md`.

An id is pinned once its story spec file exists; pinned ids survive edits, retired ids are never reassigned, and stories with no spec file yet may be renumbered freely on re-derive. Updates go through Story Breakdown: append the change to `.memlog.md`, then re-derive.

## Build And Autonomous Dev

### `bmad-build`

- **Agent**: DEV (Amelia) / `bmad-agent-dev`, menu code `BD`.
- **Use when**: The user delegates a feature, story, bug fix, or meaningful change; a bare story or issue link counts, and an explicit BMAD request always qualifies. This is the one official way BMad implements code.
- **Do not volunteer it (v6.12.0)**: for user-directed interactive edits, version-control operations that only record existing work, or obvious low-risk mechanical maintenance (small ignore-file, typo-only, formatting-only, configuration-hygiene edits) (`bmad-build/SKILL.md:3`). For a trivial edit the user will review themselves, skip BMad entirely (`docs/build/build-a-change.md:23-25`).
- **Accepts**: A couple of phrases, a bug tracker link, plan-mode output, text from a chat session, an intent file, a spec, or a fully planned story from epics and sprint artifacts.
- **Design**: Compress intent into one coherent goal, investigate the codebase and planning artifacts before asking anything, route to the smallest safe path, run longer with less supervision against the approved spec, and diagnose failure at the layer it entered — intent, spec generation, or local implementation. Only truly local problems get patched locally.
- **Light path (v6.12.0)**: After investigating, Build records intent gaps, irreversibles, and footprint. All clean and small -> `route: oneshot`: a two-section spec (`## Intent` + `## Implementation Notes`), implemented, reviewed, and presented in the same session. Anything flagged -> `route: dispatch`: a full spec with one `## Open Questions` entry per intent gap, answered before approval. In v6.11.0 the one-shot call was made in step 1, before investigation. See `references/workflow-map.md` § How Build Sizes A Change.
- **Human checkpoints**: Answering open questions and approving the plan (dispatch route only), and final review. The light path has no plan checkpoint. Nothing else is a recurring checkpoint.
- **Story handling**: When a planned story enters Build, the story stays the upstream product and acceptance context; Build creates its own execution record for the run.
- **Output**: `spec-*.md` + code.
- **Configurable keys**: `[workflow] implementation_handoff` holds the literal recipe passed to the coding subagent, so implementation can be routed to a different model or an external CLI without forking the skill — the parent is barred from restating goals, listing files, or injecting acceptance criteria into the dispatch. `[workflow] open_spec` replaces the hard-coded VS Code launch at completion; set it to an empty string to disable the launch without affecting spec generation (examples ship for VS Code, Cursor, Windsurf, Zed, IntelliJ IDEA, Vim, and Emacs).
- **Review layers**: `[[workflow.review_layers]]` lets you add, replace, or disable a reviewer, including swapping in an external tool over bash and therefore a different model. An empty `instruction` disables a layer, a new `id` appends one, and the defaults reproduce the previous prompts exactly. Since v6.12.0 the diff reaches layers as a file: the placeholder is `{diff_file}` (absolute path to a unified diff), replacing `{diff_output}` — **update custom layers that used `{diff_output}`**. `{claims_file}` is substituted the same way.
- **Review triage (v6.12.0)**: Every reviewer finding gets one row in the spec's `## Review Triage Log` — verdict (`high` / `medium` / `low` / `false` / `maybe-false`) plus evidence. Nothing is dropped or merged silently, and re-reviews carry settled rows forward instead of re-verifying them. Severity assigned by a reviewer subagent is disregarded. Patch-worthy findings are fixed; unrelated pre-existing ones are appended to `{implementation_artifacts}/deferred-work.md`.
- **Matrix audit**: When a spec carries an I/O and Edge-Case Matrix, implementation checks every row has a covering test that actually executed and passed. A test that exists but was never registered, filtered in, or enabled counts as missing; Build halts and asks.
- **Prerequisite**: `uv`. Build is a rendered skill with no interpreter fallback and halts if `uv` is unavailable.
- **Retired ID**: `bmad-quick-dev` is a forwarding shim.

### `bmad-build-auto`

- **Use when**: One coherent change should run unattended under an orchestrator.
- **Relationship**: The unattended automation surface for the same Build implementation model. It automates the implementation loop; it does not define a second implementation path.
- **Boundary**: It owns the implementation run and the spec artifact it produces, but **not** your backlog policy. Real findings that are not this story's problem get recorded in `deferred` and left there.
- **Prerequisites**: Subagent capability (otherwise halts `blocked` / `no subagents`); `uv`; a clean working tree when version control is present.
- **Inputs**: A short free-form change request, a ticket/issue/story identifier, an intent file path, an existing spec file path, or a spec folder plus a story id (folder+ID dispatch).
- **State model**: Spec frontmatter `status` — `draft`, `ready-for-dev`, `in-progress`, `in-review`, `done`, `blocked` — doubles as the resume entry point.
- **Output**: `{implementation_artifacts}/spec-<slug>.md`, or `<spec-folder>/stories/<story-id>-<slug>.md` under folder+ID dispatch, or the fallback `{implementation_artifacts}/bmad-build-auto-result-<slug-or-timestamp>.md` when it halts before a valid spec file exists.
- **Orchestrator contract**: Read `status`, blocking condition, `followup_review_recommended`, `baseline_revision`, and the frontmatter `deferred:` list. Do not infer success from chat output. Build Auto writes no `deferred-work.md` and has no `final_revision` (interactive `bmad-build` still writes `deferred-work.md`) — compute a story's range as `baseline_revision..<next story's baseline_revision>`, or `..HEAD` at exit.
- **Follow-up scoring (changed in v6.12.0)**: Counts only this pass's entries triaged `patch`, at entry verdict. First pass: `true` if any patched entry was `high`, or two or more `medium` entries were patched. Follow-up pass: `true` only if that pass patched a `high`. A `true` must name the specific unverified risk; otherwise it is `false` (`bmad-build-auto/step-04-review.md:103`). v6.11.0 used the score `3 × medium + 1 × low >= 5`.
- **Extra review layer**: The Intent Alignment Auditor is a fourth default layer, fed the verbatim invocation intent alongside the diff. Only the intent, never the spec's own scope language, can justify deferring a finding.
- **Blocked handling**: `blocked` is a routing signal. Resolve the condition, then usually start a fresh run or pass an explicit known-good spec path. A `blocked` story file under folder+ID dispatch is permanent — delete it to retry.
- **Retired ID**: `bmad-dev-auto` is a forwarding shim, and its result artifact is now `bmad-build-auto-result-*.md`.

### Quick Dev and Dev Auto (retired names)

Users still say "Quick Dev" and "Dev Auto". Both were **renamed** in v6.11.0 and their old IDs are forwarding shims in `src/bmm-skills/v6-shims/`: `bmad-quick-dev` -> `bmad-build`, `bmad-dev-auto` -> `bmad-build-auto`. Since v6.12.0 a fresh install omits all shims unless installed with `--shims`, so the old names may simply not resolve.

**Customization files must be renamed by hand**: `_bmad/custom/bmad-quick-dev{,.user}.toml` -> `bmad-build{,.user}.toml`, and the same for `bmad-dev-auto` -> `bmad-build-auto`. The shim offers the migration but requires explicit approval and never overwrites. Declined or unavailable, **it halts instead of forwarding** — so an unattended run on the old name with a legacy customization file present will refuse to start.

The old three-way framing of Quick Dev versus Dev Auto versus the full method is also gone. Build and Build Auto are the interactive and unattended faces of one implementation model, not two paths:

| Aspect | `bmad-build` | `bmad-build-auto` | Full BMad Method |
|--------|--------------|-------------------|------------------|
| Scale | Anything from one clear intent to a planned story | One unattended iteration of the same model | Product/platform work feeding into Build |
| Human loop | Open questions and plan approval when the plan is flagged; final review | Mostly absent during the run | At phase boundaries, then into Build |
| Upfront docs | Whatever exists; more context, not a different workflow | Spec frontmatter state | Brief / PRFAQ / PRD / UX / architecture / epics / sprint plan |
| Risk | Bounded by the approved spec | Must be safe for unattended execution | Higher, cross-functional, long-running |
| Best orchestrator | Human | `bmad-loop`, CT-like orchestrator | Team process, then Build |

### Story skills (retired from the default chain)

`bmad-create-story` and `bmad-dev-story` moved into `v6-shims/` but are marked **"Retained in full"** — they are not forwarders. The complete original workflow is still present and still runs when the skill is invoked by name. What changed is routing: the Dev agent menu drops `CS` and `DS`, and both skills left `bmad-help` recommendations and the workflow map. Removal rides the v7 cut.

v6.12.0 tags both with `metadata.lifecycle: shim`, so the installer handles them like every other shim: absent from a fresh install unless `--shims` is passed, kept on an existing install that already had shims. "Still runs when invoked by name" assumes it is installed.

Do not describe them as forwarding to `bmad-build`. They do not.

## Project Context

### `bmad-project-context`

- **Use when**: AI agents need to work well in this repo — verified commands, policy, conventions that differ from ecosystem defaults, and known pitfalls.
- **Replaces**: `bmad-document-project` and `bmad-generate-project-context`, both now forwarding shims to the `setup` intent. Analyst menu `DP` -> `PC`.
- **Five intents (v6.12.0)**: `setup` (no instruction file with meaningful content), `adopt` (new — an instruction file has content but no managed block; it becomes the baseline), `refresh` (a managed block exists), `record` (log a mistake agents keep making), `audit` (re-verify and prune). See `references/brownfield.md` for the adopt ledger.
- **Output**: One small verified block between `<!-- bmad:context -->` and `<!-- /bmad:context -->` in the repository root `AGENTS.md`. No generated overview, source-tree, or deep-dive pages, and **no `project-context.md`**.
- **Admission test**: Anything derivable from source is read live and never stored. `pnpm test` stays out; "the suite takes eleven minutes" goes in.
- **Human in the loop**: Every write is shown first. There is no unattended mode, and the skill fires only when named — it never routes on inferred intent.
- **Standalone**: Runs with no BMad install.
- **Migration**: `bmad-project-context` reads an existing `project-context.md` in step 1 and offers to absorb it rather than leaving it orphaned (`bmad-project-context/SKILL.md:99`). Since v6.12.0 no shipped agent or workflow auto-loads `project-context.md` any more (`persistent_facts = []`), so an unabsorbed file is simply ignored unless an override re-adds it.
- **Not yet covered**: The deeper "explain this system and its rationale" altitude is a separate capability still to come.

## Research

### `bmad-deep-recon`

- **Use when**: A decision should rest on evidence rather than the model's memory. It is a core skill, so it is not tied to software projects.
- **Replaces**: `bmad-market-research`, `bmad-domain-research`, and `bmad-technical-research`, now forwarding shims with `type` pre-set. Existing overrides on the old IDs are honored.
- **Three modes**:
  - **Draft** — composes a research prompt carrying the type pack's craft, tuned to the tool you name, for you to paste into ChatGPT, Gemini, Grok, or Perplexity.
  - **Process** — files a finished report from any source, preserves the original untouched in the run folder, extracts and checks its claims against the pack, flags uncovered dimensions, and writes the standard summary.
  - **Run** — does the research in session: parallel web fan-out, verification, cited synthesis, with approval at one plan gate.
- **Six type packs**: `market`, `domain`, `technical`, `competitive`, `user-voice`, `academic-lit`. A type selects a card of prioritized dimensions, source craft, and freshness rules. Deep Recon infers the type from your ask, or you name it. Custom types can be added through `bmad-customize`.
- **Decision shape**: An independent second choice. **Explore** (default) builds understanding; **select** runs a structured choose-between when picking among candidates. Any type can end in a selection matrix.
- **Output**: Always the same shape — a cited `research.md` with metadata downstream skills read directly, plus an optional HTML briefing. A PRD or product brief consumes the summary without reprocessing the original.
- **Analyst menu**: `MR`, `DR`, `TR` carry over; `TS` (select), `CR` (competitive), and `UV` (user-voice) are new.

## QA and Review

### `bmad-review`

One review skill covering a diff, branch, or uncommitted changes; a PRD, spec, story, or architecture doc; or any prose document. Document review and code review stop competing for the same trigger. Findings come back in one shape: a findings JSON array plus a markdown report.

A **lens** is a pass over the content with its own method, defined by `[[workflow.lenses]]` and keyed by `code`. Five ship by default:

| Lens `code` | Name | Applies to | When it runs |
|-------------|------|------------|--------------|
| `adversarial` | Adversarial | any | Always |
| `edge-case-hunter` | Edge-Case Hunter | any | Content with behavior to trace — code, diffs, specs, requirements, plans, stories. Skipped for prose with no behavioral surface |
| `verification-gap` | Verification Gap | code | Reviewed inside a repo where tests can be searched and read |
| `structure` | Editorial Structure | docs | Documents whose shape is the author's to change (cuts, merges, moves) |
| `prose` | Editorial Prose | docs | Documents being copy-edited; runs `after = "structure"`, on top of its findings |

Run every applicable lens or name the ones you want. Lenses are addable, replaceable, and disablable from `_bmad/custom/bmad-review.toml` — a matching `code` replaces a shipped lens, a new `code` appends one. `bmad-prd`, `bmad-ux`, `bmad-architecture`, and `bmad-product-brief` name explicit lenses in their `doc_standards`, so editorial review fires at finalize.

v6.12.0 changes: the skill now fires **only** when the user actually asks for a review (or another skill issues an explicit `skill:bmad-review` directive) — never uninvited, including on edits just made, and a request to act on earlier review feedback is a change, not a review (`bmad-review/SKILL.md:3`). The content is staged once as a file, and an optional `claims` input (commit messages or a change description) goes to the edge-case lens alone for a claims check.

**Phase 4 reviewers do not go through these lenses.** Routing the ship-path reviewers through `bmad-review` had changed their semantics and output guarantees, so `bmad-code-review`, `bmad-build`, and `bmad-build-auto` now own local `review-prompts/*.md` copies and dispatch reviewers by path to the prompt file.

v6.11.0 review behavior changes worth knowing: the adversarial reviewer dropped its "cynical, jaded reviewer" persona for a method (at least ten concrete findings, plus asking what is missing); verification-gap stopped demanding tests that verify nothing; triage deduplicates only findings with the same claim **and** the same required action (superseded in v6.12.0 by verdict-first triage and root-cause grouping — see `bmad-code-review` below); and review fan-out is atomic, with every reviewer subagent spawned before any output is read.

### Adversarial Review

- **Now**: The `adversarial` lens of `bmad-review`, applying to any content type, always on.
- **Old skill ID**: `bmad-review-adversarial-general`, a forwarding shim in `src/core-skills/v6-shims/`.
- **Behavior**: Looks for issues rather than rubber-stamping. In v6.11.0 the persona framing was replaced by an explicit method after A/B piloting showed the persona made no difference to residual-bug hit rate.
- **Note**: The standalone adversarial-review explanation page was removed upstream in all five locales; the material now lives with the lens.

### Edge Case Hunter

- **Now**: The `edge-case-hunter` lens of `bmad-review`.
- **Old skill ID**: `bmad-review-edge-case-hunter`, a forwarding shim.
- **Strength**: Named-set generalization — useful when a change handles only part of a closed set such as enum members, statuses, sentinels, or flags.
- **Claims check (v6.12.0)**: After its path tracing, the hunter reads the change's own claims — the spec's Intent and Tasks & Acceptance in Build, or the supplied `claims` in `bmad-review` — and tries to falsify each against the traced code (`references/claims-check.md`, shipped in `bmad-build`, `bmad-build-auto`, and `bmad-code-review`). Verified claims produce nothing; falsified ones become findings with `kind: "claim"`.

### Verification Gap

- **Now**: The `verification-gap` lens of `bmad-review`, and a third parallel review layer in the Phase 4 reviewers.
- **Old skill ID**: `bmad-review-verification-gap`, a forwarding shim.
- **Question it asks**: "If this behavior broke, would any test fail?" — it reports untested behavior changes, not bugs.

### Editorial Review

- **Now**: The `structure` and `prose` lenses of `bmad-review`.
- **Old skill IDs**: `bmad-editorial-review` (both lenses), `bmad-editorial-review-structure`, and `bmad-editorial-review-prose`, all forwarding shims in `src/core-skills/v6-shims/`.
- **Override note**: `bmad-editorial-review` keeps its own `customize.toml` so existing team and user overrides still resolve; the shim forwards the resolved values.

### `bmad-code-review`

- **Agent**: DEV (Amelia), menu code `CR`.
- **Use when**: Any code change needs review — an optional extra layer after Build's built-in review.
- **v6.11.0 changes**: Owns local `review-prompts/*.md` copies rather than routing through `bmad-review` lenses; supports configurable `[[workflow.review_layers]]`; and honors an explicit "no spec" declaration instead of prompting for one anyway.
- **Four default layers**: `blind-hunter`, `edge-case-hunter`, `verification-gap`, and `acceptance-auditor` (`bmad-code-review/customize.toml:49,68,84,98`). Build uses the first three; Build Auto adds `intent-alignment`.
- **v6.12.0 triage**: Once every layer has reported, each finding gets exactly one verdict — `high`, `medium`, `low`, `false` (with what disproves it), or `maybe-false` (with what would settle it) — before any grouping, and keeps that verdict and evidence for the summary; none is dropped or merged silently. Reviewer-assigned severity is disregarded. Survivors are then grouped only by shared root cause — same location or same fix is not enough (this replaces v6.11.0's same-claim-and-same-action deduplication). Low findings unlikely to be met in everyday use are rejected when the fix would add complexity (`bmad-code-review/steps/step-03-triage.md`). The summary reports `decision-needed`, `patch`, `defer`, and rejected counts. Layers read the diff from `{diff_file}`.

### `bmad-qa-generate-e2e-tests`

- **Agent**: DEV (Amelia), menu code `QA`.
- **Use after**: Implemented code exists and needs generated automated API/E2E tests. Not for code review or story validation — use `CR` for that.
- **Output**: Test suite artifacts under `implementation_artifacts`.
- **Boundary**: This is BMM's built-in lightweight QA. Use TEA for full test architecture and risk strategy.

### `bmad-retrospective`

- **Agent**: DEV (Amelia), menu code `ER`.
- **Use when**: An epic is complete and needs reviewing against its own acceptance criteria.
- **Rebuilt in v6.11.0** as an evidence-based review: five phases over the epic's real artifacts, with aggregate views no single diff hunk shows — architecture delta, duplication, god-class growth, pattern divergence, spec reconciliation.
- **Discipline**: Every finding needs a source reference. An epic with unfinished stories is **rejected**, not quietly closed.
- **Team discussion**: Now opt-in, delegating to `bmad-party-mode` seeded with real findings.
- **Headless**: `-H` / `--headless`, with `-H <epic>` as the stable orchestrator interface.
- **Spec-folder mode**: Can retro an epic that exists only as a spec folder — the shape unattended Build Auto runs leave behind — writing `{spec-folder}/RETROSPECTIVE.md` without touching sprint status.

### `bmad-walkthrough`

- **Renamed in v6.12.0** from `bmad-checkpoint-preview` (`CK` -> `WT`). `WT` is the `module-help.csv` code for `bmad-help` routing; **no agent menu carries it** — Amelia's menu is `BD`, `QA`, `CR`, `SP`, `ER` (`bmad-agent-dev/customize.toml`). Invoke `bmad-walkthrough` directly, or say "walkthrough" / "walk me through this change".
- **Use when**: A person wants to review a change with their own eyes — after one or more `bmad-build` runs, on a PR with more than a handful of files, when onboarding to a branch they did not write, or at sprint review (stories marked `review`). It is for **human** review; agentic review is `bmad-build`'s built-in review or `bmad-code-review` (`docs/build/walk-through-a-change.md:19-40`).
- **Flow**: Five steps — orientation (intent summary and surface-area stats), walkthrough organized by concern rather than by file with clickable `path:line` stops, detail pass (2–5 highest-risk spots tagged by category), testing (2–5 manual observations), and wrap-up (approve / rework / discuss).
- **Entry**: After a Build run, say "walkthrough" in the same chat; otherwise start a fresh chat with a PR, branch, spec path, or the current git state.
- **Old ID**: `bmad-checkpoint-preview` is a forwarding shim in `v6-shims/` where shims are installed. If `_bmad/custom/bmad-checkpoint-preview.toml` or `.user.toml` exists, the shim offers to rename it to `bmad-walkthrough*.toml`, merges with explicit approval if the new file already exists, and **HALTs instead of forwarding** when approval is declined or unavailable (`v6-shims/bmad-checkpoint-preview/SKILL.md:12-21`).

### Advanced Elicitation

- **Skill**: `bmad-advanced-elicitation`.
- **Use when**: A just-produced draft, section, or plan needs to be pushed past its first version — deeper critique, reframing, risk analysis, or more creative exploration.
- **Method menu**: pre-mortem, first principles, red team, socratic, and more. v6.10.0 added Subtraction and Map Is Not the Territory.
- **Categories include**: advanced, collaboration, competitive, core, creative, framing, learning, philosophical, research, retrospective, risk, and technical.

## Party Mode

- **Skill**: `bmad-party-mode`.
- **Purpose**: Bring multiple agent perspectives into one discussion.
- **Use when**: Decisions benefit from product, engineering, UX, research, or critique perspectives together.
- **v6.10.0 addition**: Anti-consensus room pattern for decisions that need resistance to premature agreement.
- **Four modes** (`bmad-party-mode/SKILL.md:43-50`; default `party_mode = "session"` in `customize.toml:47`; a runtime `--mode <session|auto|subagent|agent-team>` wins, and the older `--subagents` means `subagent`):
  - `session` — one model voices every persona inline; the floor every other mode degrades to.
  - `auto` — inline for ordinary rounds, spawns real agents only when independent thinking changes the outcome.
  - `subagent` — a real agent behind each persona every substantive round; best for reviews and focus groups where voices must stay independent.
  - `agent-team` — personas as a persistent team addressing each other directly; Claude Code only.
- **Fallback when a mode is unavailable**: upstream contradicts itself. `docs/customize/run-multi-agent-discussions.md:74-76` describes a chain `agent-team` -> `subagent` -> `session`; the shipped `SKILL.md:43` says to fall back straight to `session` "without comment". This guide follows the shipped skill: expect `session`.
- **Interactive by default**: The opening prompt is a topic, not a task; the room stays open until the user ends it. `--non-interactive` runs one intent to a natural close and releases spawned agents.
- **v6.11.0 fix**: The shared persona resolver's output is now decoded as UTF-8 on Windows; emoji-bearing persona data used to corrupt under a legacy locale such as cp1252 and break party mode outright. `bmad-forge-idea` shares the resolver and got the same fix.
- **Caution**: Useful for reasoning diversity, but not a replacement for file-producing workflows.

## Investigation

### `bmad-investigate` retired

- **Status**: Retired since v6.10.0, still listed in `removals.txt` so existing installs clean it up.
- **Reason**: Upstream states plain investigation reaches the same conclusions at lower cost.
- **Route instead**:
  - `bmad-help` when unsure which BMad workflow applies.
  - `bmad-project-context` when the repo's agent context is missing.
  - `bmad-deep-recon` when the question is a research question rather than a code question.
  - A Tower research workorder or normal code investigation outside BMad when root cause is unknown.
  - `bmad-build` only after the intent or cause is concrete enough to implement.

## Document Sharding and Indexing (retired)

`bmad-shard-doc` and `bmad-index-docs` were **removed outright** in v6.11.0. There is no replacement, and no shim: they are listed in `removals.txt`, so an install or update deletes them from IDE skill directories. The "shard large documents" how-to was removed from all five upstream locales.

If a user asks how to shard a large document now, the honest answer is that BMad no longer ships that capability. Practical routes: let `bmad-spec` distill the oversized document into a `SPEC.md` contract plus companions, or split it by hand and keep an index of your own.

## Technical Writing Workflows (retired)

Paige (`bmad-agent-tech-writer`) is **retired** in v6.11.0 and listed in `removals.txt`. Upstream's stated reason is that her capabilities were generic LLM defaults. All six former entries — `bmad-document-project`, `bmad-agent-tech-writer:write`, `:update-standards`, `:mermaid`, `:validate`, and `:explain` — are gone as a menu.

What survives:

- `bmad-document-project` is still directly invocable as a forwarding shim to `bmad-project-context` (setup intent), where shims are installed.
- Project context is on the Analyst (Mary) menu as `PC`, or invoke `bmad-project-context` directly.
- Ordinary drafting, Mermaid generation, and concept explanation are plain LLM work with no dedicated skill.

Upstream describes Paige as "on hiatus" and returning "in the future far more capable" (`removals.txt:78-80`; `docs/reference/skills-and-agents.md:58-59`). Only the v6.11.0 `CHANGELOG.md` entry (`CHANGELOG.md:43` in the v6.12.0 tree) adds that a replacement "joins soon as an optional installable agent". No version, date, or delivery form is published anywhere — treat both the return and its form as unconfirmed.

## Web Bundles

**Still shipped in v6.12.0.** The tag carries `web-bundles/` with all six bundles, `README.md`, and a `bundles.json` byte-identical to v6.11.0, and `docs/customize/use-web-bundles.md` is a live v6.12.0 page. The upstream `main` branch now tracks the v7 direction (6.x maintenance moved to the `V6.12` branch), and its tree has no `web-bundles/`; that is a v7 development state, not a v6.12.0 removal — do not tell v6.12.0 users the bundles are gone.

Web Bundles are non-IDE planning packs for Gemini Gems and ChatGPT Custom GPTs. Use them when the planning conversation benefits from a web LLM subscription, Canvas-style interaction, image generation, or Deep Research before moving into the IDE.

| Bundle | Purpose |
|--------|---------|
| Brainstorming Coach | Facilitated ideation across many techniques |
| Product Brief Coach | Create / Update / Validate product briefs |
| PRFAQ Coach | Working Backwards PRFAQ challenge |
| PRD Coach | PRD coaching with validation |
| UX Coach | DESIGN.md + EXPERIENCE.md planning with Stitch-oriented handoff |
| Market & Industry Research | Deep Research-backed market and industry synthesis |

The six bundles are unchanged through v6.12.0 (`releaseTag: web-bundles-v1.0.0`). The supported install path is the BMad web-bundles site, not local `_bmad` installation; plan in the web, then copy the artifact into the repo and continue in the IDE (`docs/customize/use-web-bundles.md`).
