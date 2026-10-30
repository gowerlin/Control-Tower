# Brownfield / Established Project Workflows

> "Brownfield" means an existing codebase. BMad docs now say "existing codebase"; since v6.12.0 the upstream home of this topic is `docs/existing-codebases/` (`start-in-an-existing-codebase.md`, `set-and-maintain-project-context.md`, `theory-of-project-context.md`, `getting-deeper.md`). The v6.11.0 pages `docs/how-to/established-projects.md`, `docs/how-to/project-context.md`, `docs/how-to/quick-fixes.md`, `docs/explanation/project-context.md`, `docs/explanation/project-context-theory.md`, and `docs/explanation/established-projects-faq.md` no longer exist.

## Overview

Existing projects need context capture before planning or coding. The goal is to stop agents from inventing architecture, naming, tests, or workflows that conflict with what the project already does.

**What changed in v6.11.0 — read this before answering any brownfield question.** The v6.10-era route was "scan the repo, generate a `project-context.md`, then feed that document to every downstream workflow." v6.11.0 reverses that premise. Generated documentation is no longer the deliverable, and `project-context.md` is no longer produced. The replacement is `bmad-project-context`: a conversation that writes **one small verified block inside the repository's `AGENTS.md`**. If a user describes the old route, say plainly that it is retired and route them here.

**What v6.12.0 adds on top:**

- **Nothing auto-loads `project-context.md` any more.** `persistent_facts` ships empty (`persistent_facts = []`) in every shipped agent and workflow `customize.toml`. In v6.11.0, 31 of them — the five agents (e.g. `bmad-agent-dev/customize.toml:38`) plus workflows such as `bmad-prd`, `bmad-architecture`, `bmad-build`, `bmad-spec`, and `bmad-party-mode` — still listed `file:{project-root}/**/project-context.md`. CHANGELOG v6.12.0 (Breaking): "Re-add `project-context.md` to your override if you relied on the auto-load." The shipped comments now say repo-wide context belongs in `AGENTS.md`, which every skill already sees.
- **`bmad-project-context` gains an `adopt` intent**, so a handwritten `AGENTS.md` / `CLAUDE.md` is kept and improved instead of rewritten (CHANGELOG v6.12.0 Also; `bmad-project-context/SKILL.md:12,25,87-91`).
- **The admission test is reframed** from "can an agent derive this?" to "what does it cost when it doesn't?" (`references/best-practices.md:5-9`). See below.

## The On-Ramp

```text
npx bmad-method install
        │
        ▼
bmad-project-context          ← the brownfield on-ramp (optional; see "Prepare or skip")
        │  setup or adopt → the <!-- bmad:context --> block in AGENTS.md
        ▼
bmad-help                     ← "what should I run next?"
        │
        ├── one-session change ─────────► bmad-build
        │
        ├── several sessions ──► bmad-spec ──► bmad-build per piece ──► bmad-retrospective (optional)
        │
        └── project-sized ──► PRD / UX / architecture / epics /
                              bmad-sprint-planning ──► bmad-build
```

All implementation goes through `bmad-build`. Scope does not change the implementation skill; it only changes how much context you prepare first (`docs/existing-codebases/start-in-an-existing-codebase.md:19-22`).

Upstream's framing for existing codebases: most of the knowledge is already in the source, and agents read code well. Textual descriptions of what they can already read add contradiction, ambiguity, and context bloat — and that includes the original greenfield planning documents (PRD and the rest). Keep those archived for the few sessions that need them, out of reach of an ordinary change (`start-in-an-existing-codebase.md:8-17`).

### Step 1: Install or update BMad

```bash
npx bmad-method install
```

Old skill IDs (`bmad-document-project`, `bmad-generate-project-context`, and the rest) are compatibility shims. Since v6.12.0 a **fresh** install leaves them out unless you pass `--shims`; an existing install keeps them if it already had them. See `references/workflow-map.md` § Retired Or Deprecated Names.

### Step 2: Clean up completed planning artifacts

If earlier BMad cycles finished their epics and stories, archive or delete those files before onboarding. Stale outputs pollute new planning. Check `docs/`, `_bmad-output/planning-artifacts/`, and `_bmad-output/implementation-artifacts/`. Git history is the archive; the working tree is not. v6.12.0 states the reason more sharply: an agent doing a small request should not even be able to find the old greenfield context by accident.

### Step 3: Prepare project context, or skip it

```text
bmad-project-context
```

Run it when the repo's agent instructions are missing, stale, or of unknown quality. **Skip it** when the repo already has an `AGENTS.md`, `CLAUDE.md`, or editor rules someone keeps current, or when agents already have another discovery tool to build on. Skipping does not fail a Build; the cost is the same mistake every session until someone writes it down. You can run it later, including a refresh or audit partway through a project (`start-in-an-existing-codebase.md:35-49`).

It reads what the repo already has and tells you how it measures up, asks which rules you want followed, then verifies the rest — every path a line names, and every claim about what a command does, against the target or script that runs it (`bmad-project-context/SKILL.md:49`). The result is a small verified block in `AGENTS.md`, not a documentation set.

The skill fires only when you name it. It does not route on inferred intent, and it has no unattended mode: every write is shown to you first, and it **never commits** — changes stay in your working tree (`docs/existing-codebases/set-and-maintain-project-context.md:73`). It also runs standalone, with no BMad install present.

## `bmad-project-context` In Detail

### The admission test

This is the core of the doctrine, and the part most likely to be asked about. **v6.12.0 reframed the governing question** (`references/best-practices.md:5-9`):

> **Not *could an agent derive this*, but *what does it cost when it doesn't*?**

Weigh how much exploration finding it takes, how likely the agent is to search the right place in time rather than guess, whether the fact is available at the point of use or only after the mistake, what a retrieval failure costs (a wasted search, or corrupt data), and whether it is a rule that must hold or a detail the code already shows. A line that stops the same rediscovery every session earns its place, **derivable or not**. A stored copy of what the agent reads more accurately first-hand still does not — it rots and is charged every session.

v6.11.0 asked "Can this fact be derived by reading the repository? If yes, it never enters." Do not quote that rule as current.

Excluded by design: repo overviews, directory trees, tech-stack lists, things included for being interesting, style rules a formatter or check should enforce, platitudes, transcribed command lists whose obvious invocation is already right, pasted code or changelog content, aspirational state, and edit history.

What earns a line (`references/best-practices.md:11-20`):

| Admitted | Example |
|----------|---------|
| **Policy** the code cannot express | Frozen and protected paths, generated files, branch rules, secrets, security and compliance — stated by a human or read off an enforcing config, never inferred |
| **What a config file cannot say about running the project** | `pnpm test` is already in `package.json` and stays out; "the suite takes eleven minutes" or "a service must be up first" goes in, and so does the right command when the obvious one is wrong |
| **Conventions that differ from ecosystem defaults** | An agent follows the norm unless told otherwise, so only the deviation is worth storing. A required wrapper or prefix on a command counts, with no observed mistake needed |
| **Known pitfalls**, admitted only from observed failure | A recorded lesson, the maintainer's recollection, a mistake fixed repeatedly in git history, or one the writing session made and caught |
| **Runtime behavior invisible from the repo** | Replaying webhooks, lying health endpoints, environment quirks — once a human confirms it |
| **Cross-component rules** (new in v6.12.0) | What must stay true across parts of the system the agent cannot see from the file it is editing: who owns what, how data must flow, pipeline order |
| **Required tool and runtime versions** (new in v6.12.0) | Read from the project files that declare them, never from the session's environment |
| **Entry points and pointers** | Where work lands; nested or linked files worth reading first |

Note the evidence bar on pitfalls: a trap-looking fact found by scanning becomes **a question**, never a line. The skill's full rule set ships at `references/best-practices.md` inside the skill; it assesses your repo against that file and explains its reasoning back to you at the end.

### Five intents

| Intent | What it does |
|--------|--------------|
| `setup` | No instruction file in the target carries meaningful content (scaffolding, empty headings, a comment, or a lone import line do not count). Assess what exists, ask what you bring, verify the rest, show you the block, then write it. |
| `adopt` | **New in v6.12.0.** An instruction file has content but no managed block — whoever wrote it. That file becomes the baseline, and every instruction in it enters a ledger. When unsure between setup and adopt, the skill adopts. |
| `refresh` | A managed block exists: re-verify caveats and paths, diff deletions and renames since the recorded commit, update what moved, never re-ask what a prior run settled. Proposed removals are ledger entries too. |
| `record` | Capture one observed agent mistake at the moment it happens. A recurring or costly one earns a line. |
| `audit` | Re-verify and prune. The block ends **smaller or equal, never larger**. A removal needs one of the four deletion grounds. |

Source: `bmad-project-context/SKILL.md:12,25`; `docs/existing-codebases/set-and-maintain-project-context.md:121-129`. A supplied intent that contradicts what detection finds — say `setup` against a file with content — is surfaced and confirmed, never silently obeyed.

### Adoption and the ledger (v6.12.0)

Existing instructions are the baseline being improved, never raw material to discard (`SKILL.md:35`). Every instruction a human wrote is presumed intentional. The skill opens a **ledger**: one entry per existing section and per independently meaningful instruction, each settling as `retain`, `rewrite`, `relocate`, `automate`, or `delete`, with its reason, evidence, the risk if it goes, and an approval flag.

**Deletion needs one of four grounds** (`references/best-practices.md`, "Judging an existing file"):

1. **Stale or incorrect** — the referent is gone, or the instruction was never true; the evidence is named.
2. **Mechanically enforced** — a hook, linter, formatter, or CI check already fails the violation.
3. **Harmful or contradictory** — it points agents at the wrong thing, or loses a reconciliation with another live instruction.
4. **The user approved this deletion** — asked as a line item, never implied by approving a replacement block.

The proposal shows the settled ledger alongside the new block: replacement text alone hides what the user loses. A rewrite that weakens or drops part of a rule is listed as a deletion. A relocation must land somewhere that is actually loaded, or it counts as a deletion. Adoption commonly ends with `CLAUDE.md` reduced to `@AGENTS.md` once that import is verified for every harness in use, so no instruction lives in two loaded files. "Keep it small" disciplines what the skill writes, never what the maintainer already wrote: an over-budget file the user chose beats a gutted one they didn't.

### Output location and ownership

The output is `AGENTS.md` at the repo root — the file every major coding harness already reads. BMad owns **only** the region between:

```text
<!-- bmad:context -->
...
<!-- /bmad:context -->
```

The splice itself touches nothing outside the markers. Since v6.12.0, text outside them changes only through a settled ledger entry or a fix the user has seen and approved — never as a side effect (`SKILL.md:68`). For a tool that reads a different file, such as Claude Code's `CLAUDE.md`, the skill proposes and verifies a one-line `@AGENTS.md` import (`set-and-maintain-project-context.md:68-71`).

Monorepo components and nested repositories get their own file under the same rules, listed as pointers in the parent. A nested `AGENTS.md` for one directory is now allowed only when its rules are subtree-exclusive and substantial, the split materially reduces the root block, the user approves, and **loading is verified for every harness in use**; otherwise the rules stay in the root block as path-qualified lines (`references/best-practices.md:53`; `set-and-maintain-project-context.md:133-137`).

### Repo or home directory

What this skill writes belongs committed to the repository: shared by the team, consistent across machines, versioned with the code it constrains. If the same rules repeat across every project, or they are personal preferences rather than the team's, they belong in the agent's global configuration in the home directory instead.

### Migrating an existing `project-context.md`

An existing `project-context.md` is **not** absorbed automatically, and since v6.12.0 nothing loads it on its own either. `bmad-project-context` reads one from the retired skills (commonly under `{output_folder}`) in step 1 and offers to absorb its content; it does not delete the file without agreement (`SKILL.md:99`). Until it is absorbed — or re-added to `persistent_facts` in an override — agents simply do not see it. A bloated `docs/` folder is likewise treated as a source to verify against code, not as material to add to.

### Boundary with `bmad-architecture`

Design decisions are *born* in `bmad-architecture`. If a genuinely contested decision surfaces during context work — real tradeoffs, multiple viable shapes — the skill says it deserves `bmad-architecture` rather than quietly making the call.

## Choosing Planning Depth

| Scope | Recommended preparation |
|-------|-------------------------|
| Trivial edit you will review yourself | No BMad; ask the agent directly (`docs/build/build-a-change.md:23-25`) |
| Bug fix, small refactor, config or dependency change | Enter `bmad-build` directly with the request, issue URL, or intent file. See "Quick Fixes" below. |
| Clear update or addition | Enter `bmad-build` directly with the request, issue, or an existing spec. |
| Needs several coding sessions, or messy intent | `bmad-spec` first, then one `bmad-build` per piece, optionally `bmad-retrospective` |
| Product feature with meaningful planning | `bmad-product-brief` -> `bmad-prd` -> ... -> `bmad-build` |
| UI/experience-heavy feature | `bmad-prd` -> `bmad-ux` -> ... -> `bmad-build` |
| Major technical change | PRD / UX if needed -> `bmad-architecture` -> `bmad-create-epics-and-stories` -> `bmad-sprint-planning` -> `bmad-build` |
| Unknown cause / unfamiliar area | `bmad-deep-recon` (technical type) or a Control Tower research workorder first |

Too little planning costs one Build run — Build reads the code first and stops to ask when it cannot settle the intent. Too much planning costs documents nobody reads (`start-in-an-existing-codebase.md:24-29`).

### Quick Fixes

Bug fixes, small refactorings, minor tweaks, and dependency updates enter `bmad-build` directly with little or no upstream planning — the same implementation loop planned stories use. The v6.11.0 `docs/how-to/quick-fixes.md` page is gone; the guidance now lives in `docs/build/build-a-change.md`:

- Start a **fresh chat session**; reusing a session from a previous workflow causes context conflicts.
- Build accepts free-form intent before, with, or after the invocation: plain text, file paths, GitHub issue URLs, or bug-tracker links.
- Build investigates the code and planning artifacts first. A small change with no intent gaps and nothing irreversible takes the **light path** (v6.12.0): a two-section spec, implemented and reviewed in the same session with no plan checkpoint. Otherwise it writes a full plan whose open questions you answer before approving.
- Build implements, reviews its own work, patches issues, and commits locally, then offers to push and open a PR.
- If a pushed change misbehaves, `git revert HEAD` and run Build again in a fresh chat.

Build keeps each run focused on one goal. Independent secondary goals, and pre-existing issues the review surfaces, are appended to `deferred-work.md` in the implementation artifacts directory rather than tackled in the same run — treat that file as the backlog and feed items back into later Build runs (`docs/build/build-a-change.md:139-147`).

> Do not generalize the v6.11.0 note that "`deferred-work.md` is gone" to Build. That change is scoped to the **Build Auto** contract, where deferred findings moved into the spec frontmatter `deferred:` list. `bmad-build` still keeps its own `deferred-work.md` ledger.

### Ask `bmad-help`

```text
bmad-help I have an existing app and want to add a feature. What should I run next?
bmad-help How much planning does this change need before implementation?
```

`bmad-help` inspects installed modules and current artifacts, then recommends the next workflow. It also runs automatically at the end of every workflow.

## Brownfield-Specific Considerations

### During PRD creation

- Make the agent find and read the existing project documentation and the `AGENTS.md` context block before it writes requirements. If the PRD cites nothing the repository already does, expect to rework the design once Build meets the real code.
- Requirements must explain integration with the existing system.
- Existing terminology should win over newly invented names.
- Technical mechanisms belong in the addendum or architecture, not in FRs.

### During UX planning

- UX work is optional. Run it when this change adds or alters screens, flows, or patterns; skip it for simple updates to screens you are happy with. Skipping it when new patterns are needed produces inconsistent screens, one story at a time.
- Existing design systems should be named in the UX Foundation.
- `DESIGN.md` should reference or extend existing visual tokens.
- `EXPERIENCE.md` should specify behavioral deltas rather than restating existing UI basics.

### During architecture

- The architect should use the documented architecture files and scan the existing codebase.
- ADRs should explain why a change follows or intentionally diverges from existing patterns.
- Avoid introducing new infrastructure when the current system already has a viable pattern.
- Pay close attention here — if the proposed decisions do not name what the code already does, expect a reinvented component or a conflicting choice, found during implementation.

### During implementation

- **Build follows what it finds — it does not ask.** `bmad-build` investigates the repository, writes down what to reuse and what not to change, and follows that. It does not stop to ask whether to match the current codebase (`start-in-an-existing-codebase.md:70-74`).
- To break a pattern, say so in the request and write why in the spec, so later sessions follow the new rule. If you dislike a pattern but have no plan to change it, say nothing — Build will match the code. Changing one file and leaving the rest leaves two standards with no record of which one wins.
- `bmad-code-review` should check compatibility with existing architecture, not only story ACs.
- If the evidence is weak, route back to `bmad-deep-recon` or a research workorder before implementing.

> The v6.11.0 guide said Build "asks: 'Should I follow these existing conventions?'". That came from the v6.11.0 `docs/explanation/established-projects-faq.md`; no `bmad-build` step file in v6.11.0 or v6.12.0 contains such a prompt, and the v6.12.0 docs now state the opposite. Do not repeat it.

## Existing-Codebase FAQ

The v6.11.0 `docs/explanation/established-projects-faq.md` no longer exists. Its questions are answered by `docs/existing-codebases/start-in-an-existing-codebase.md`:

**Do I have to run project context first?**
No. Run it when agent instructions are missing, stale, or of unknown quality; skip it when the repo already has maintained instructions or agents have another discovery tool. If you already wrote an `AGENTS.md` or `CLAUDE.md`, run it with `adopt` to keep and improve it.

**What if I forget?**
Nothing breaks — Build does not depend on it. Run `bmad-project-context` at any time; `refresh` and `audit` keep the context true during and after a project.

**How does implementation work in established projects?**
Run `bmad-build`, exactly as for new development. Enter directly for a one-session change; run `bmad-spec` and a Build per piece for several sessions; plan as a project for anything bigger.

**What if the existing code does not follow best practices?**
Build matches the existing code unless you tell it otherwise. If you want a pattern broken, say so in the request and record why in the spec.

## TEA for Brownfield

For established projects with existing tests:

- Use Traceability to baseline current test confidence.
- Use Test Design to identify risk gaps before implementation.
- Use ATDD or Automate only where they fit the project's strategy.
- Avoid replacing an existing test strategy without evidence.

The main repo names three TEA skill IDs: `bmad-testarch-test-design` (optional before Automate), `bmad-testarch-automate` (heavier test generation than `bmad-qa-generate-e2e-tests`), and `bmad-testarch-trace` (optional, after generation) (`docs/build/test-completed-work.md:10,92,95`). Other TEA workflow IDs come from the external TEA module and are not verified against the v6.12.0 main repo. See `references/tea-module.md`.

## Cleanup Between Cycles

After finishing a planning/implementation cycle:

- Archive or remove stale BMad outputs, including greenfield planning documents an ordinary change should not find.
- Keep the `AGENTS.md` context block true — run `bmad-project-context` with the `refresh` intent after structural change, and `audit` when the block feels stale or bloated. Audit only shrinks.
- Prefer Git history for old artifacts unless they remain active inputs.
- Re-run `bmad-help` before starting the next major change.

## Retired Brownfield Routes

Recognize these names, then redirect. Full old-to-new tables live in `references/v6-11-migration.md` — this section is only the brownfield subset.

Every name marked shim below resolves only where shims are installed: since v6.12.0 a fresh install omits them unless `--shims` is passed (`tools/installer/core/shim-policy.js:92-99`).

| Retired name | Status (v6.12.0) | Route to |
|--------------|------------------|----------|
| `bmad-generate-project-context` | Deprecated forwarder. Note the trap: it is **still located in `src/bmm-skills/plan/`**, not in `v6-shims/`, so directory position proves nothing — judge it by frontmatter. v6.12.0 adds `metadata.lifecycle: shim` to that frontmatter, so the installer now treats it as a shim (opt-in on fresh installs). Never present it as a live route. | `bmad-project-context`, `setup` intent |
| `bmad-document-project` | Forwarding shim. Its "scan the repo into generated documentation" approach is the one the evidence went against. The deeper "explain this system and its rationale" altitude is a separate capability still to come. | `bmad-project-context`, `setup` intent |
| `project-context.md` (artifact) | No longer produced as of v6.11.0, and **no longer auto-loaded as of v6.12.0** (`persistent_facts = []` everywhere). `bmad-project-context` offers to absorb an existing file. | The `<!-- bmad:context -->` block in `AGENTS.md`; or re-add the file to an override's `persistent_facts` |
| `bmad-shard-doc` | Removed outright in v6.11.0. No replacement and no shim; listed in `removals.txt`, so existing installs clean it up. The "shard large documents" how-to is gone from all five locales. | Nothing. Say so plainly. |
| `bmad-index-docs` | Removed outright in v6.11.0. No replacement and no shim; listed in `removals.txt`. | Nothing. Say so plainly. |
| `bmad-agent-tech-writer` (Paige) | Retired in v6.11.0, listed in `removals.txt`. | Analyst (Mary) menu code `PC`, or invoke `bmad-project-context` directly |
| `bmad-investigate` | Retired since v6.10.0, still listed in `removals.txt`. | `bmad-deep-recon` (technical type), plain investigation, or a Control Tower research workorder |
| `bmad-quick-dev` / `bmad-dev-auto` | Renamed; forwarding shims. | `bmad-build` / `bmad-build-auto` |
| `bmad-create-story` / `bmad-dev-story` | Deprecated but **retained in full** — not forwarders. Invoking either by name still executes the complete original workflow when installed; they have only left the default Phase 4 chain, the Dev agent menu, and `bmad-help` recommendations. Being `lifecycle: shim`, they are absent from a fresh install without `--shims`. | `bmad-build` for new work; say the old skills still run if the user insists on them and they are installed |

Older plans may still name any of these. Translate the reference rather than executing it, and check `references/v6-11-migration.md` section H — customization TOML overrides do **not** follow renames automatically.
