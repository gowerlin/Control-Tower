# BMad-Method v6.12.4 Core Workflow Map

> Source basis: `bmad-method` v6.12.0 tag, dereferenced commit `05bfbd46d00766ec88eb9b42e76be2c575d64d7b`, `package.json`, `src/bmm-skills/module-help.csv`, `src/core-skills/module-help.csv`, `src/bmm-skills/agents/*/customize.toml`, `src/bmm-skills/ship/bmad-build/` (`SKILL.md`, `step-01-clarify-and-route.md`, `step-02-plan.md`, `step-oneshot.md`, `spec-template.md`), `src/bmm-skills/ship/bmad-build-auto/` (`spec-template.md`, `step-04-review.md`, `workflow.md`), `docs/plan/choose-a-planning-path.md`, `docs/build/build-a-change.md`, `docs/build/walk-through-a-change.md`, `docs/build/autonomous-development-loops.md`, `docs/reference/skills-and-agents.md`, `src/bmm-skills/v6-shims/README.md`, `src/core-skills/v6-shims/README.md`, `tools/installer/core/shim-policy.js`, `removals.txt`, and the `CHANGELOG.md` v6.12.0 section.
>
> The v6.11.0 sources `docs/reference/workflow-map.md`, `docs/reference/agents.md`, `docs/reference/build-auto.md`, `docs/reference/core-tools.md`, `docs/explanation/build.md`, and `docs/explanation/sprint-planning.md` no longer exist in v6.12.0; upstream reorganized the docs by task (`docs/start/`, `docs/plan/`, `docs/build/`, `docs/customize/`, `docs/existing-codebases/`).

For old-to-new name lookups, see `references/v6-11-migration.md`.

## Core Philosophy

BMad builds project context progressively. Early workflows clarify the problem and intent; planning workflows create durable contracts; solutioning translates those contracts into architecture, epics, and a validated sprint plan; implementation executes one unit of work at a time with review and feedback loops.

Fresh chat/session boundaries still matter. Large planning workflows should run in clean sessions with explicit inputs; unattended loops need an orchestrator that reads durable status artifacts instead of trusting chat output.

Since v6.11.0, **every implementation path converges on `bmad-build`.** Upstream planning is optional and variable. A clear change can enter Build directly; a large initiative can arrive with a PRD, UX design, architecture, epics, stories, readiness results, and a sprint plan. Those artifacts strengthen the implementation context; they do not select a different implementation workflow.

v6.12.0 adds: **Build decides how much ceremony a change needs after investigating it, not before.** A small, clean change gets a two-section spec and finishes in one session; anything flagged gets a full written plan first. See [How Build Sizes A Change](#how-build-sizes-a-change-v6120).

## Four Planning Paths

Upstream frames planning as four nested paths that all reuse the same implementation unit — one `bmad-build` session, about 500 lines of code added or changed (not counting tests) in a small handful of files (`docs/build/build-a-change.md:16-18`). Larger work adds shared context around that unit and repeats it; it does not switch to a separate delivery system (`docs/plan/choose-a-planning-path.md:105-107`).

| Path | Fits When | How |
|------|-----------|-----|
| Edit directly | Trivial, low-risk edit you are willing to review yourself | No BMad; ask the agent to make it. If a bug could escape into production, `bmad-build` is likely worth it |
| One Build | The change fits one implementation session | `bmad-build` with a sentence, an issue, a file, or a planned story |
| Epic | One coherent outcome that needs several Build sessions | `bmad-spec` -> Story Breakdown (`stories.yaml`) -> one `bmad-build` per story -> `bmad-retrospective` with the spec folder |
| Project | Greenfield product, multi-epic initiative, or roughly 20+ implementation sessions | Only the planning the project needs (brief / PRD / UX / architecture), then `bmad-spec` per epic, story tracking, and a retrospective at each epic boundary |

The deciding question is whether the intent is already well defined: if it is, feed it to `bmad-spec`; if not, use the analysis and planning tools until it is (`docs/plan/choose-a-planning-path.md:8-37`). Scope is only one signal — use more planning for high risk, unclear requirements, broad architectural reach, cross-system effects, or coordination between people or teams. A PRD is needed when more than one person must agree on what the product is, or more than one epic must not diverge.

## Planning Shapes

| Shape | Best For | Main Artifacts |
|-------|----------|----------------|
| Forge idea | Early idea pressure test before deciding whether to build | `forge-report.html` every run, `forged-idea.md` when the idea hardens |
| Deep recon | A decision that should rest on evidence rather than model memory | `research.md` + optional HTML briefing |
| Spec kernel | Messy intent, brain dumps, transcripts, mixed source material | `SPEC.md` + companion files, optional `stories.yaml` |
| Product brief | Early product shaping when the idea is real but not yet a PRD | `brief.md` + optional `addendum.md` |
| PRFAQ | Working Backwards pressure test before commitment | `prfaq-{project}.md` + downstream PRD distillate |
| PRD | Requirements contract for product/build planning | `prd.md` + optional `addendum.md` + `.memlog.md` |
| UX spine | Products where UI/flow/experience carries meaningful risk | `DESIGN.md` + `EXPERIENCE.md` |
| Build | Any implementation work, from a one-line intent to a planned story | `spec-*.md` + code |

Build is not a "shape" you choose against the others — it is where all of them land. What varies is how much context exists before it runs.

## Agent Roster

| Name | Persona | Skill ID | Menu Codes | Key Workflows |
|------|---------|----------|------------|---------------|
| Mary | Analyst | `bmad-agent-analyst` | `BP`, `MR`, `DR`, `TR`, `TS`, `CR`, `UV`, `CB`, `WB`, `PC` | Brainstorming, Deep Recon (market / domain / technical / select / competitive / user-voice), product brief, PRFAQ, project context |
| John | PM | `bmad-agent-pm` | `PRD`, `CE`, `IR`, `CC` | PRD create/update/validate, epics and stories, implementation readiness (dispatches the sprint-planning gate), correct course |
| Winston | Architect | `bmad-agent-architect` | `CA`, `IR` | `bmad-architecture`, implementation readiness (dispatches the sprint-planning gate) |
| Amelia | DEV | `bmad-agent-dev` | `BD`, `QA`, `CR`, `SP`, `ER` | Build, QA test generation, code review, sprint planning, epic retrospective |
| Sally | UX Designer | `bmad-agent-ux-designer` | `CU` | `bmad-ux`, DESIGN/EXPERIENCE spines |

Menu codes are read from each agent's `customize.toml`, which is the shipped menu definition; all five menus are code-for-code identical to v6.11.0. The v6.11.0 `docs/reference/agents.md` omitted the Analyst's `TS` / `CR` / `UV`; that page is gone, and its v6.12.0 replacement `docs/reference/skills-and-agents.md:52` lists all ten. `CR` is Code Review on Amelia's menu and Competitive research on Mary's — disambiguate by active agent.

No agent menu carries `WT`. `bmad-walkthrough` is invoked directly (or by saying "walkthrough"); `WT` is its `module-help.csv` code, used by `bmad-help` routing.

The only v6.12.0 change in the five agent `customize.toml` files is `persistent_facts`, which now ships empty — agents no longer auto-load `project-context.md`. The same change landed in every shipped workflow skill as well. See `references/brownfield.md`.

Paige (Tech Writer, `bmad-agent-tech-writer`) is **retired in v6.11.0** and listed in `removals.txt`. Project context moved to Mary's `PC` trigger or a direct `bmad-project-context` call. Upstream describes Paige as "on hiatus" (`removals.txt:78-80`, `docs/reference/skills-and-agents.md:58-59`), but no return version, date, or delivery form is published (see `references/v6-11-migration.md` section J).

Bob, Quinn, and Barry remain folded into Amelia in the v6 line; use `bmad-agent-dev` for SM/dev/QA-style implementation work.

## Anytime Workflows

| Workflow | Purpose | Output |
|----------|---------|--------|
| `bmad-help` | Inspect installed modules and route the next action | Recommendation |
| `bmad-spec` | Distill any input into a five-field SPEC kernel | `{output_folder}/specs/spec-{slug}/SPEC.md` + companions, optional `stories.yaml` |
| `bmad-forge-idea` | Pressure-test an idea until it hardens, proves out, or dies cheaply | `{output_folder}/forge` artifacts |
| `bmad-deep-recon` | Decision-grade research: draft a prompt, process a report, or run it here | `{planning_artifacts}/research` report/summary + optional HTML briefing |
| `bmad-review` | Review a diff, branch, doc, spec, story, or plan through installed lenses | Findings JSON array + markdown report |
| `bmad-project-context` | Set up, adopt, refresh, record, or audit the repo's agent instructions | Managed block in the repo root `AGENTS.md` |
| `bmad-correct-course` | Navigate major change or planning drift | Change proposal / updated plan |
| `bmad-sprint-planning` (status view) | Summarize sprint status, risks, and next action; can also validate or repair the tracking file | Status summary |
| `bmad-customize` | Write sparse TOML overrides for installed BMad skills | `_bmad/custom/*.toml` |
| `bmad-party-mode` | Multi-agent discussion for hard decisions | Agent perspectives |
| `bmad-advanced-elicitation` | Deepen or critique a recent output with selectable methods | Refined section/content |
| `bmad-brainstorming` | Facilitated ideation | `brainstorm.html` + optional `brainstorm-intent.md` |

## Phase 1: Analysis (Optional)

| Workflow | Purpose | Output |
|----------|---------|--------|
| `bmad-brainstorming` | Guided ideation with a brainstorming coach | `brainstorm.html` keepsake, optional `brainstorm-intent.md` |
| `bmad-forge-idea` | Pressure-test one idea before planning investment | `forge-report.html`, `forged-idea.md` when it hardens |
| `bmad-deep-recon` | Research any subject for a decision — six typed packs, verified and cited | Research report or summary + optional HTML briefing |
| `bmad-product-brief` | Capture strategic vision when the concept is already clear | `brief.md` + `addendum.md` |
| `bmad-prfaq` | Working Backwards customer-first stress test | `prfaq-{project}.md` |

These are independent tools, not stages: pick the ones the intent gap calls for, in any order, and hand `bmad-spec` the condensed result rather than the raw pile (`docs/plan/choose-a-planning-path.md:50-52`).

`bmad-market-research`, `bmad-domain-research`, and `bmad-technical-research` are **retired forwarding shims** since v6.11.0. Route to `bmad-deep-recon` with `type` = `market`, `domain`, or `technical`.

The v6.11.0 docs named the same brief file both `brief.md` + `addendum.md` and `product-brief.md`. The v6.12.0 planning page uses `brief.md` + `addendum.md` only (`docs/plan/choose-a-planning-path.md:79`).

## Phase 2: Planning

| Workflow | Agent | Purpose | Output |
|----------|-------|---------|--------|
| `bmad-prd` | PM (John) | Create, update, or validate a PRD — three intents in one skill | Create/Update: `prd.md`, `addendum.md`, `.memlog.md`; Validate: `validation-report.html` + `.md` |
| `bmad-ux` | UX (Sally) | Design the UX spine pair when UX carries risk | `DESIGN.md`, `EXPERIENCE.md`, `.memlog.md` |
| `bmad-spec` | Any | Distill any intent input into a `SPEC.md` contract + companions; locks the WHAT before the HOW | `SPEC.md` + companions under `{output_folder}/specs/spec-{slug}/`, optional `stories.yaml` |

`bmad-spec` moved from core into bmm in v6.11.0 and is presented here as a Phase 2 workflow. Core-only installs do not receive it. It is the only writer of `SPEC.md`; other skills invoke it headless when they need to express or update intent. Keep its input short: it reads everything in one pass, with a practical ceiling of a few tens of thousands of tokens (`docs/plan/choose-a-planning-path.md:25-29`).

`bmad-create-prd`, `bmad-edit-prd`, and `bmad-validate-prd` are retired forwarding shims; route to `bmad-prd` with the `create`, `update`, or `validate` intent. `bmad-create-ux-design` is retired; route UX planning to `bmad-ux`.

## Phase 3: Solutioning

| Workflow | Agent | Purpose | Output |
|----------|-------|---------|--------|
| `bmad-architecture` | Architect (Winston) | Make technical decisions explicit; the invariants that keep features, epics, and stories consistent | `ARCHITECTURE-SPINE.md` by default, hydrating to richer outputs when needed |
| `bmad-create-epics-and-stories` | PM (John) | Break requirements into implementable work | Epic files with stories. Since v6.12.1 `epics.md` carries `status: draft` until final validation passes every check, then `status: final`; a failed check keeps it a draft and withholds `[C]` |
| `bmad-sprint-planning` | DEV (Amelia) | Readiness gate before implementation, then story tracking and the status view | PASS / CONCERNS / FAIL + `sprint-status.yaml` |

`bmad-sprint-planning` moved from Phase 4 into Phase 3 in v6.11.0 and absorbed `bmad-check-implementation-readiness`, which is removed outright and listed in `removals.txt`. The `IR` trigger on the PM and Architect menus dispatches the gate here. The gate finds artifacts **by content** instead of the filename globs that used to miss `SPEC.md` and `DESIGN.md`.

Its deterministic core is `scripts/sprint_plan.py` (`generate` / `status` / `validate`, JSON-only output), which owns epic parsing, ordering, preserve-never-downgrade status merging, story-file detection, `action_items` carry-over, atomic writes, and drift checks. Legacy v6 statuses (`drafted`, `contexted`) are normalized rather than rejected, and refresh preserves custom keys, comments, and `project_key` / `tracking_system` / `story_location`. Judgment stays with the LLM, and the skill falls back to reading the file directly if a script path fails. The `sprint-status.yaml` format itself is unchanged.

`bmad-create-architecture` remains only as a forwarding shim; prefer `bmad-architecture`.

## Phase 4: Implementation

Every implementation path converges on `bmad-build`.

| Workflow | Agent | Purpose | Output |
|----------|-------|---------|--------|
| `bmad-build` | DEV (Amelia) | Turn a delegated feature, story, bug fix, or meaningful change into implemented, reviewed code | `spec-*.md` + code + local commit |
| `bmad-code-review` | DEV (Amelia) | Ad hoc review of any code change; optional extra layer after Build's built-in review | Findings + applied patches |
| `bmad-correct-course` | PM (John) / any | Handle significant mid-sprint changes | Updated plan or re-routing |
| `bmad-retrospective` | DEV (Amelia) | Evidence-based review of a completed epic against its acceptance criteria | Retro document, action items, acceptance verdict |
| `bmad-qa-generate-e2e-tests` | DEV (Amelia) | Generate automated API/E2E tests after implementation | Test suite |
| `bmad-walkthrough` | — (invoke directly; not on any agent menu) | Guided human walkthrough of a commit, branch, PR, or spec — purpose and context first, then details, risk spots, and manual tests | Approve / rework / discuss decision |

`bmad-walkthrough` replaces `bmad-checkpoint-preview` in v6.12.0 (`CK` -> `WT`). It is for **human** review; agentic review happens inside `bmad-build` or through `bmad-code-review` (`docs/build/walk-through-a-change.md:19-23`). After a Build run, say "walkthrough" in the same chat; to review anything else, start a fresh chat with a PR, branch, spec path, or the current git state.

`bmad-build-auto` orchestrates unattended iterations of the same implementation model. It is an automation surface, not a second implementation path.

`bmad-sprint-status`, `bmad-create-story`, and `bmad-dev-story` have left this table. `bmad-sprint-status` is a forwarding shim to the sprint-planning status view. `bmad-create-story` and `bmad-dev-story` are **retained in full** in `v6-shims/` — deprecated and off the default chain, but still executing their complete original workflow when invoked by name **and installed**. Since v6.12.0 every skill marked `lifecycle: shim`, retained-in-full ones included, is opt-in on fresh installs (see [Retired Or Deprecated Names](#retired-or-deprecated-names)).

## Build And Build Auto

| Workflow | Use When | Human Role | Orchestrator Notes |
|----------|----------|------------|--------------------|
| `bmad-build` | A feature, story, bug fix, or meaningful change is delegated for normal interactive execution | Present at intent clarification, plan approval (when the plan is flagged), and final review | The canonical implementation loop; menu code `BD` |
| `bmad-build-auto` | One coherent intent can run unattended | Should not be needed during the iteration | Read spec frontmatter `status`, blocking condition, `baseline_revision`, `deferred`, and `followup_review_recommended` |
| `bmad-loop` | Repeated unattended dev-loop orchestration is desired | Sets policy and handles blocked outcomes | Install as an opt-in module, then run `bmad-loop-setup` before automation |

`bmad-build-auto` requires subagent capability. If subagents are unavailable it halts `blocked` with `no subagents`. Version control is optional but strongly recommended; when present, the working tree must be clean.

Both Build skills are **rendered skills** and have no interpreter fallback: they halt if `uv` is unavailable (`bmad-build/SKILL.md:9-13`).

### When Build Triggers (v6.12.0)

v6.12.0 narrows when an agent should volunteer `bmad-build` (CHANGELOG: "Build no longer auto-triggers on interactive edits, git bookkeeping, or formatting chores"). The shipped description (`bmad-build/SKILL.md:3`) reads:

- **Use** when the user delegates a feature, story, bug fix, or meaningful change; a bare story or issue link counts. Explicit BMAD requests always qualify.
- **Skip** obvious, low-risk mechanical maintenance: small ignore-file, typo-only, formatting-only, or configuration-hygiene edits.
- **Do not volunteer** for user-directed interactive edits, or for version-control operations that only record existing work (committing, tagging, and similar bookkeeping).

The v6.11.0 description triggered on any request to "build, fix, tweak, refactor, add or modify any code". When routing, recommend Build for delegated work, not for every edit.

### How Build Sizes A Change (v6.12.0)

v6.11.0 chose a one-shot route in step 1, before investigating, from "zero blast radius". v6.12.0 investigates first and decides in step 2 (`step-02-plan.md:14-22`). Build writes down three facts about the plan as it stands:

| Fact | Meaning |
|------|---------|
| **Intent gaps** | Things the request does not say, the code cannot settle, and the user would notice in the result. Only the human can answer them; choices the user would not notice are Build's to make and record |
| **Irreversibles** | Things that cannot be undone: migrations, data deletion or mutation, external side effects, deploy or config triggers |
| **Footprint** | How big: files changed, and anything new other code will call or depend on |

| Route | Condition | Spec | Flow |
|-------|-----------|------|------|
| `oneshot` (light path) | No intent gaps, nothing irreversible, and the change is small | Frontmatter + `## Intent` + `## Implementation Notes` only; written at `status: in-progress` | Implement, review, and present in the same session (`step-oneshot.md`) |
| `dispatch` | Anything flagged | Full spec: Boundaries & Constraints, I/O matrix, `## Open Questions` (one per intent gap), Code Map, Tasks & Acceptance | Human answers open questions and approves the plan, then implement -> review -> present |

The choice is recorded in spec frontmatter `route` (`spec-template.md:6`). If a one-shot implementation discovers an unnoticed intent gap, an irreversible step, or growth beyond the plan, it stops, restores Code Map and Open Questions, and returns to planning as `route: dispatch`, `status: draft`.

Other v6.12.0 spec changes: the human-gated "Ask First" tier is gone from the Build spec (Boundaries is two tiers, Always / Never), and its replacement is `## Open Questions` — the spec cannot leave `draft` while any entry remains. The Build Auto spec likewise drops its "Block If" tier.

### Review Triage (v6.12.0)

- Review layers read the diff from a **file**: the runtime placeholder is `{diff_file}` (an absolute path to a unified diff), replacing `{diff_output}`. Diff text is never pasted into layer prompts. **Custom review-layer overrides that reference `{diff_output}` must be updated** (CHANGELOG v6.12.0 Breaking).
- Every reviewer finding gets one row in the spec's `## Review Triage Log` — a verdict (`high` / `medium` / `low` / `false` / `maybe-false`) plus its evidence; nothing is dropped, merged, or skipped silently. Re-reviews carry earlier rows forward instead of re-verifying settled findings (`bmad-build/step-04-review.md:31-43`).
- The Edge Case Hunter ends with a **claims check** (`references/claims-check.md`, new in all three of `bmad-build`, `bmad-build-auto`, and `bmad-code-review`): it treats the spec's Intent and Tasks & Acceptance as testimony and tries to falsify each checkable claim against the code.

Interactive Build still appends deferred goals and unrelated pre-existing findings to `{implementation_artifacts}/deferred-work.md` (`bmad-build/step-01-clarify-and-route.md:87`, `step-04-review.md:76`; `docs/build/build-a-change.md:139-147`). Only Build Auto replaced that file with the `deferred` frontmatter list.

### Build Auto Spec Status

| Status | Meaning | Resume entry point |
|--------|---------|--------------------|
| `draft` | Spec exists but has not passed the ready-for-dev gate | plan |
| `ready-for-dev` | Spec is complete enough to implement | implement |
| `in-progress` | Implementation underway | implement |
| `in-review` | Review/triage underway | review |
| `done` | Completed successfully | review again as a fresh follow-up pass |
| `blocked` | Cannot safely continue unattended | halt immediately |

### Build Auto Terminal Contract

On `done`, the workflow writes an `Auto Run Result` section (summary, files changed, review findings breakdown including every rejected finding with its reason, verification performed, residual risks) plus:

- `followup_review_recommended` — **changed in v6.12.0** (`bmad-build-auto/step-04-review.md:103`). Default `false`; count only this pass's entries triaged `patch`, at entry verdict. On a first pass, `true` if any patched entry was `high`, or if two or more `medium` entries were patched. On a follow-up pass, `true` only if that pass patched a `high` — otherwise the work has converged; patch volume is never grounds. A `true` must name the specific unverified risk under `## Auto Run Result`. (v6.11.0 used the score `3 × medium + 1 × low >= 5`.) A suggestion, not a requirement.
- `baseline_revision` — the full canonical revision before implementation; `NO_VCS` without version control.
- `deferred` — frontmatter list of real findings that are not this story's problem. Each item has `summary`, `evidence`, and optionally `location` and `severity`. This is a machine-readable review output, **not** a backlog; queueing, deduplicating, or escalating is the orchestrator's job.

Build Auto has no `final_revision` and writes no `deferred-work.md`. Compute a story's commit range as `baseline_revision..<next story's baseline_revision>`, or `baseline_revision..HEAD` at exit.

Blocking conditions shipped in v6.12.0 include `unclear intent`, `intent gap`, `no subagents`, `missing spec_file before implementation`, `handoff conflicts with spec`, `implementation verification failed`, `patch verification failed`, `review repair loop exceeded 5 iterations (non-convergence)`, `spec failed ready-for-development standard`, `blocked spec supplied`, `matrix ambiguity`, `matrix test audit failed`, `finalization left repository dirty`, `version-control metadata not writable`, and — under folder+ID dispatch — `no stories.yaml found`, `story id not found in stories.yaml`, `no epic spec found`, `ambiguous story file match`, `unrecognized status in existing story file`, `story already blocked`.

On an `intent gap` halt during review, the attempted change is saved as a patch under `{implementation_artifacts}` and named in the halt output before the tree is reverted. If the reading was actually correct, `git apply` the patch and set the spec to `in-review` to resume review instead of re-running.

### `stories.yaml` And Folder+ID Dispatch

`bmad-spec` gains an optional Story Breakdown step emitting `stories.yaml` beside `SPEC.md` — a top-level YAML list, one entry per story, in execution order (list order **is** execution order). It is discovered by its fixed filename, never listed in `companions:`.

| Field | Required | Meaning |
|-------|----------|---------|
| `id` | yes | Unique string, quoted, letters/digits/dashes only. Used for equality and as a filename prefix. Prefix-free: `"3"` and `"3-2"` cannot coexist. |
| `title` | yes | One line; becomes the story's heading downstream |
| `description` | yes | What the story covers, pointing into `SPEC.md`; two sentences |
| `spec_checkpoint` | no (`false`) | Caller-only: human reviews the story spec between planning and implementation |
| `done_checkpoint` | no (`false`) | Caller-only: dispatch pauses after this story completes |
| `invoke_dev_with` | no (`""`) | Free text appended verbatim to the dispatch prompt |

There is **deliberately no `status` field, ever**. Status lives in the story spec file.

Build and Build Auto can both be dispatched by spec folder plus story id. The workflow reads `<spec-folder>/stories.yaml`, takes only that entry's `title` and `description`, and writes to `<spec-folder>/stories/<story-id>-<slug>.md`. Exactly one entry is dispatched per invocation. A `blocked` story file is permanent: every later dispatch of that id halts with `story already blocked` until the file is deleted.

## Story Lifecycle

`TODO` -> `IN PROGRESS` -> `READY FOR REVIEW` -> `DONE`

Official v6.12.0 story loop:

```text
bmad-sprint-planning
  -> bmad-build
  -> bmad-code-review (optional extra layer)
  -> next story or bmad-retrospective
```

Spec-backed epic (no sprint tracking):

```text
bmad-spec -> Story Breakdown (stories.yaml)
  -> bmad-build per story (folder + id)
  -> bmad-retrospective <spec-folder>   (writes RETROSPECTIVE.md)
```

Autonomous single-iteration loop:

```text
bmad-build-auto
  -> spec status: draft / ready-for-dev / in-progress / in-review
  -> terminal status: done / blocked
  -> orchestrator reads durable artifact
```

The v6.10.0 chain `bmad-sprint-planning -> bmad-create-story -> validate -> bmad-dev-story -> bmad-code-review` is retired. Both story skills still run when named and installed, but they are no longer the recommended route.

## Artifact Map

```text
AGENTS.md                          <- repo root; bmad:context managed block
{output_folder}/
  specs/spec-{slug}/
    SPEC.md
    companion-files.md
    stories.yaml                   <- optional Story Breakdown output
    stories/
      <story-id>-<slug>.md
    RETROSPECTIVE.md               <- spec-folder retrospective
  planning-artifacts/
    forge artifacts
    research/                      <- bmad-deep-recon reports and summaries
    brief workspaces
    prfaq documents
    prd workspaces
    ux workspaces/
      DESIGN.md
      EXPERIENCE.md
    ARCHITECTURE-SPINE.md
    epics/
  implementation-artifacts/
    sprint-status.yaml
    spec-*.md                      <- route, Open Questions, Implementation Notes, Review Triage Log
    deferred-work.md               <- interactive bmad-build only
    bmad-build-auto-result-*.md
    epic-<N>-context.md
    intent-gap patch files
    tests/
_bmad/render/                      <- content-addressed skill snapshots + manifest.json
```

Exact folder names are resolved from the installed `_bmad` config; do not hardcode `_bmad-output` if the project config overrides it.

`project-context.md` is no longer produced. Since v6.12.0 nothing auto-loads it either: in v6.11.0, 31 shipped `customize.toml` files (the five agents plus workflow skills such as `bmad-prd`, `bmad-build`, `bmad-spec`, and `bmad-party-mode`) listed it in `persistent_facts`; in v6.12.0 every one ships `persistent_facts = []`. Re-add it to the relevant overrides if you relied on that, or let `bmad-project-context` absorb it into `AGENTS.md`. `deferred-work.md` is still written by interactive `bmad-build`; only `bmad-build-auto` replaced it with frontmatter `deferred`.

## Retired Or Deprecated Names

Old IDs live in `v6-shims/` (plus `bmad-generate-project-context`, still in `plan/`). The folder is grouping only — installed skill IDs and paths are unchanged. Removal rides the v7 cut; both `v6-shims/README.md` files state it is "never a 6.x minor", with no version or date published.

**Whether an old ID resolves depends on the install (v6.12.0).** The installer treats every skill whose frontmatter has `metadata.lifecycle: shim` as a shim, and `inferShimPreference()` decides (`tools/installer/core/shim-policy.js:19-21,92-99`):

| Install | Shims installed? |
|---------|------------------|
| Fresh install, no flag | **No** — old IDs do not resolve |
| Any install with `--shims` / `--no-shims` | As requested |
| Existing install, no flag | The saved preference if one exists; otherwise **yes** only if the old skill manifest shows a shim was installed |

So "the old ID still forwards" holds only where shims are installed. Both `v6-shims/README.md` files still say the shims "ship by default"; that prose contradicts the shipped installer and the CHANGELOG ("Deprecated shims are opt-in on fresh installs. Pass `--shims` to keep them."). This guide follows `shim-policy.js`. Retained-in-full skills are shims too: on a fresh install without `--shims`, `bmad-create-story` and `bmad-dev-story` are absent.

| Name | Status (v6.12.0) | Route Instead |
|------|------------------|---------------|
| `bmad-checkpoint-preview` | Renamed in v6.12.0, forwarding shim | `bmad-walkthrough` (`CK` -> `WT`). Customization files under the old name must be renamed first — the shim HALTs until they are |
| `bmad-quick-dev` | Renamed, forwarding shim | `bmad-build` |
| `bmad-dev-auto` | Renamed, forwarding shim | `bmad-build-auto` |
| `bmad-create-prd` | Renamed, forwarding shim | `bmad-prd` (create intent) |
| `bmad-edit-prd` | Renamed, forwarding shim | `bmad-prd` (update intent) |
| `bmad-validate-prd` | Renamed, forwarding shim | `bmad-prd` (validate intent) |
| `bmad-create-architecture` | Renamed, forwarding shim | `bmad-architecture` (create intent) |
| `bmad-sprint-status` | Renamed, forwarding shim | `bmad-sprint-planning` (status view, `SS` with `action=status`) |
| `bmad-create-story` | Deprecated, **retained in full** | Off the default chain; still runs when named and installed. Prefer `bmad-build` |
| `bmad-dev-story` | Deprecated, **retained in full** | Off the default chain; still runs when named and installed. Prefer `bmad-build` |
| `bmad-review-adversarial-general` | Merged, forwarding shim | `bmad-review`, lens `adversarial` |
| `bmad-review-edge-case-hunter` | Merged, forwarding shim | `bmad-review`, lens `edge-case-hunter` |
| `bmad-review-verification-gap` | Merged, forwarding shim | `bmad-review`, lens `verification-gap` |
| `bmad-editorial-review-structure` | Merged, forwarding shim | `bmad-review`, lens `structure` |
| `bmad-editorial-review-prose` | Merged, forwarding shim | `bmad-review`, lens `prose` |
| `bmad-editorial-review` | Merged, forwarding shim | `bmad-review`, lenses `structure` + `prose` |
| `bmad-market-research` | Merged, forwarding shim | `bmad-deep-recon`, `type = market` |
| `bmad-domain-research` | Merged, forwarding shim | `bmad-deep-recon`, `type = domain` |
| `bmad-technical-research` | Merged, forwarding shim | `bmad-deep-recon`, `type = technical` |
| `bmad-document-project` | Merged, forwarding shim | `bmad-project-context` (setup intent) |
| `bmad-generate-project-context` | Deprecated forwarder, still in `plan/` | `bmad-project-context` (setup intent) |
| `bmad-check-implementation-readiness` | Removed, folded in | `bmad-sprint-planning` readiness gate; `IR` forwards there |
| `bmad-agent-tech-writer` (Paige) | Retired agent | Analyst (Mary) `PC`, or `bmad-project-context` directly |
| `bmad-index-docs` | Removed outright | No replacement |
| `bmad-shard-doc` | Removed outright | No replacement |
| `bmad-investigate` | Retired (v6.10.0) | Plain investigation, `bmad-help`, research workorder, or `bmad-build` once intent is clear |
| `bmad-create-ux-design` | Retired | `bmad-ux` |
| `bmad-automator` | Deprecated | `bmad-loop` + `bmad-build-auto` |

`bmad-generate-project-context` is the directory anomaly: it never moved into `v6-shims/` and still sits in `src/bmm-skills/plan/`. Judge it by frontmatter, not location. v6.12.0 adds `metadata.lifecycle: shim` to it (`plan/bmad-generate-project-context/SKILL.md:4-5`; v6.11.0 had no such field), so the installer now treats it as a shim — opt-in on fresh installs like the rest.

## v6.12.0 Key Changes

- **Build sizes the ceremony after investigating.** Step 2 records intent gaps, irreversibles, and footprint; a clean, small change takes the `oneshot` light path with a two-section spec in one session, anything flagged gets a full plan with `## Open Questions`. The route is stored in spec frontmatter `route`.
- **Build triggers more narrowly.** It no longer volunteers for interactive edits, git bookkeeping, or formatting/configuration-hygiene chores; it is for delegated features, stories, bug fixes, and meaningful changes.
- **Review triage logs a verdict and evidence for every finding** in `## Review Triage Log`, and a claims check (`references/claims-check.md`) tries to falsify the spec's own claims. Build Auto's `followup_review_recommended` rule changed (see the terminal contract above).
- **`{diff_output}` is now `{diff_file}`** — a path to a unified diff file. Update custom review-layer overrides.
- **`bmad-checkpoint-preview` is now `bmad-walkthrough`** (`CK` -> `WT`). The old ID forwards where shims are installed, after migrating any customization file.
- **Deprecated shims are opt-in on fresh installs** (`--shims` / `--no-shims`); existing installs keep them when the manifest shows they were installed.
- **`persistent_facts` ships empty** in every shipped agent and workflow `customize.toml`; `project-context.md` is no longer auto-loaded. Re-add it in an override if you relied on it.
- **`bmad-project-context` gains an `adopt` intent** that keeps a handwritten `AGENTS.md` as the baseline instead of rewriting it.
- **`llms.txt` and `llms-full.txt` are no longer published**; the `module-help.csv` `_meta` rows point to the docs root.
- **Docs are reorganized by task** (`docs/start/`, `docs/plan/`, `docs/build/`, `docs/customize/`, `docs/existing-codebases/`, `docs/reference/skills-and-agents.md`), with a Korean translation.

## v6.12.1–v6.12.4 Key Changes

Patch releases on the `V6.12` branch. Skill IDs, `removals.txt`, both `module-help.csv` files, the shim policy, and `web-bundles/` are unchanged from v6.12.0 (50 skill IDs in both tags). Source: `CHANGELOG.md` v6.12.1–v6.12.4 sections, `v6.12.4` tag, commit `bab9082c3e884e0d72c759bcd1a6d90bcc01be84`.

- **v6.12.1 — every skill reads the same merged config.** 23 bmm skills, including the v6 shims, stopped reading `_bmad/bmm/config.yaml` and load config through `resolve_config.py`, so `_bmad/custom/config.toml` overrides apply everywhere. `_bmad/config.toml` now carries user-scope defaults, so `bmad-build` / `bmad-build-auto` render on a fresh clone without `config.user.toml` (re-run the installer to pick this up). See `ecosystem-modules.md`, Layered Configuration.
- **v6.12.1 — `bmad-create-epics-and-stories` writes `status: draft`** and sets `status: final` only when every final-validation check passes.
- **v6.12.1 — Party Mode's create-party collision check** now sees aliases and custom-only member codes (`resolve_party.py --list-codes`).
- **v6.12.2 — TEA and CIS are pinned** to their last v6 releases (`pin: v1.27.2`, `pin: v0.3.2` in `bmad-modules.yaml`); newer releases target v7.
- **v6.12.2 — the installer advertises the v7 preview** (`npx skills add bmad-code-org/BMAD-METHOD`, `bmad setup`, `bmad migrate`). That installs v7, not v6.12 — see `ecosystem-modules.md`.
- **v6.12.2 — fixes:** `install --yes` without `--directory` installs into the current directory; helper scripts write UTF-8 on Windows.
- **v6.12.3–v6.12.4 — `next` leaves the channel picker** (still available headless via `--next=CODE`); a choice made in the picker now beats a registry pin; a pinned module shows no picker and prints the pin plus the v7 install command.

## v6.10-v6.11 Key Changes

- **Quick Dev becomes Build.** `bmad-quick-dev` -> `bmad-build`, `bmad-dev-auto` -> `bmad-build-auto`, Dev menu `QD` -> `BD`. Phase 4 collapses to one chain: `bmad-sprint-planning -> bmad-build -> bmad-code-review`.
- **Core drops from fourteen skills to eight.** Five review/editorial skills become lenses on `bmad-review`; three research skills become `bmad-deep-recon`; `bmad-document-project` and `bmad-generate-project-context` become `bmad-project-context`; `bmad-index-docs` and `bmad-shard-doc` are removed outright; `bmad-spec` moves to bmm.
- **`bmad-project-context` replaces generated documentation** with one verified block in the repo root `AGENTS.md`. No more `project-context.md`.
- **`bmad-sprint-planning` absorbs the readiness gate** and moves to Phase 3, backed by a tested `sprint_plan.py` script core.
- **`bmad-retrospective` is evidence-based**: five phases over the epic's real artifacts, a source reference required on every finding, and refusal to close an epic with unfinished stories.
- **`stories.yaml` becomes the planning-to-execution contract**, enabling folder+ID dispatch of Build and Build Auto.
- **Config moves to layered TOML**, and renderers now exit 1 on a missing key or unreadable override instead of silently degrading.
- **`uv` becomes a hard requirement for rendered skills.** `bmad-build` and `bmad-build-auto` halt if `uv` is unavailable — there is no interpreter fallback. Python itself leaves the prerequisites list: every script now runs through `uv run`, which provisions an interpreter from each script's own `requires-python`. You need Node.js 20.12+ and `uv`.
- **`_bmad/render/` publishes immutable content-addressed snapshots** of exactly what ran, each with a `manifest.json` of renderer and source hashes, resolved values, and per-output hashes.
- **Review layers are configurable** via `[[workflow.review_layers]]` in `bmad-code-review`, `bmad-build`, and `bmad-build-auto`, and Build Auto gains a fourth default layer, the Intent Alignment Auditor.
- **The bmm tree takes its verb-named shape**: `src/bmm-skills/{agents,plan,ship,v6-shims}/`.
- **Paige (Tech Writer) is retired**, and Whiteport Design Studio (`wds`) is marked deprecated and hidden from the module picker for new installs.
- **Antigravity CLI (AGY) becomes a separate installer target**, and core-only installs are now possible.
