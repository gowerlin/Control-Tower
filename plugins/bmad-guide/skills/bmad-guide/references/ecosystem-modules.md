# BMad Ecosystem Modules

> Source basis: `bmad-method` v6.12.0 tag, dereferenced commit `05bfbd46d00766ec88eb9b42e76be2c575d64d7b` — `bmad-modules.yaml` (identical to v6.11.0), `docs/start/install-bmad.md`, `docs/customize/add-modules.md`, `docs/customize/customize-bmad.md`, `docs/customize/use-web-bundles.md`, `web-bundles/` (identical to v6.11.0), `README.md`, `src/scripts/render_skill.py`, `tools/installer/commands/install.js`, `tools/installer/ide/platform-codes.yaml`. v6.12.1–v6.12.4 changes re-checked against the `v6.12.4` tag, dereferenced commit `bab9082c3e884e0d72c759bcd1a6d90bcc01be84` — `CHANGELOG.md`, `bmad-modules.yaml`, `tools/installer/modules/channel-plan.js`, `tools/installer/ui.js`, `tools/installer/install-messages.yaml`, `tools/installer/core/installer.js`, `docs/customize/customize-bmad.md`. External module repos (TEA, BMB, CIS, GDS, `bmad-loop`, WDS) are **not** in the snapshot; descriptions of them below come from the main repo's own pages, and anything beyond that is marked unverified.

BMad is modular. BMM (BMad Method) is the core development method; other skills, modules, web bundles, and customization layers extend it.

**v6.12.0 changed none of the module registry or the Web Bundles.** What changed at this layer: deprecated shims are opt-in on fresh installs (`--shims`), three installer targets were added, and the docs moved (`docs/how-to/*` -> `docs/start/`, `docs/customize/`).

**v6.12.1–v6.12.4 do change this layer** (Web Bundles still unchanged): every skill now reads one merged config (v6.12.1), the registry **pins** TEA and CIS to their last v6 releases (v6.12.2), the channel picker drops `next` (v6.12.3–v6.12.4), and the installer advertises the v7 preview (v6.12.2). Details below.

## Installation Prerequisites

**Node.js 20.12+** — the installer requires it.
**`uv`** — a hard requirement for rendered skills.
**Git** — only when installing external or custom modules from Git.
**An AI tool** — Claude Code, Cursor, and others. Run `npx bmad-method install --list-tools` for the full list.

### Do not tell users to install Python

**Python is not a user prerequisite since v6.11.0, and v6.12.0 did not change that.** Every script is invoked through `uv run`, and `uv` provisions an interpreter from each script's own `requires-python` declaration. The user installs `uv`; `uv` handles Python.

Upstream contradicts itself on this point, so answer from the source code rather than from any single page:

| Source | What it says |
|--------|--------------|
| `README.md` | "Node.js 20.12+, Python 3.10+, and uv" |
| `docs/start/install-bmad.md:16-27` Prerequisites (v6.12.0) | Node.js 20.12+, a supported AI tool, **`uv`** ("required by skills that render or run Python through `uv`, including `bmad-build` and `bmad-build-auto`"; if missing, "the installer warns you but still completes"), Git only for external/custom modules. **Python is not mentioned.** |
| `docs/how-to/install-bmad.md` Prerequisites (v6.11.0; file gone in v6.12.0) | Node.js 20.12+, Git, an AI tool. Neither Python nor `uv` was mentioned. |
| `CHANGELOG.md` v6.11.0 breaking changes | "`uv` with Python 3.11+ becomes a hard requirement for rendered skills" |
| `CHANGELOG.md` v6.11.0 fixes (#2704) | "With every script invoked through `uv run`, which provisions an interpreter from each script's own `requires-python`, Python leaves the prerequisites: you need Node and `uv`." |

`README.md:18` still says Python 3.10+ in v6.12.0; the v6.12.0 install page now agrees with the source code. The resolution: the **3.11+** figure is real, but it is the floor `uv` satisfies on the user's behalf, not something the user installs. `src/scripts/render_skill.py` carries `requires-python = ">=3.11"` in its inline script metadata, which is exactly the declaration `uv run` reads. Say "you need Node and `uv`"; mention 3.11+ only to explain what `uv` provisions.

### What happens when `uv` is missing

**`bmad-build` and `bmad-build-auto` halt. There is no interpreter fallback.** Rendered skills do not degrade to a system Python.

Installation itself never blocks on this — core-only and CI installs do not render skills — so a user can install successfully, see a green summary, and only hit the halt on the first `bmad-build`. v6.11.0 fixed the installer to name the skills that will halt and to repeat the warning in the post-install summary, with a `python3` probe running only when `uv` is absent. v6.12.0's `docs/start/install-bmad.md:21-23,46-48` states the same behavior: a missing-`uv` warning does not stop the installation, but skills that require `uv` will not work until it is installed. When a user reports "install worked but Build halts immediately", check `uv` first.

## Core BMM

Core BMM includes the phase workflow skills, agent skills, `bmad-help`, `bmad-forge-idea`, `bmad-review`, `bmad-deep-recon`, elicitation tools, and customization support.

Two v6.11.0 changes to the core boundary:

- **Core drops from fourteen skills to eight.** The review and editorial skills became lenses on `bmad-review`; the research trio became `bmad-deep-recon`; `bmad-index-docs` and `bmad-shard-doc` were removed outright, so document sharding and indexing are no longer core capabilities and have no replacement.
- **`bmad-spec` moved out of core into bmm** (`src/bmm-skills/plan/bmad-spec/`) and is now presented as a Phase 2 Planning workflow. **Core-only installs no longer get it.**

v6.12.0 leaves the core skill set unchanged (the same eight). It does change what an install contains: **deprecated shims — including the six core review/editorial forwarders — are no longer installed on a fresh install unless `--shims` is passed** (`tools/installer/commands/install.js:37-38`; policy in `references/v6-11-migration.md`, Shim Policy). Existing installs keep them when the old manifest shows they were installed.

Install or update BMM through the official installer:

```bash
npx bmad-method install
```

### The installer's v7 preview notice (v6.12.2+)

Since v6.12.2 the installer's start and end messages say "BMad v7 is close, and you can preview and test it now: `npx skills add bmad-code-org/BMAD-METHOD`, then ask your agent for `bmad setup`. After setup, `bmad migrate` tests the v6 to v7 migration (still in beta)" (`tools/installer/install-messages.yaml:15-18,41-44`). Read it as an advertisement, not as a step of the v6 install:

- `npx skills add bmad-code-org/BMAD-METHOD` installs the **v7 preview**, not v6.12. It is a different product line with its own layout, and this guide does not teach it.
- `bmad setup` and `bmad migrate` are v7 commands. They do not exist in a v6.12 install.
- A user who followed the notice is on the v7 skills line; handle them as `SKILL.md` (Startup Version Check, step 0) describes.

### Core-only installs

Core-only installation is now possible. `core` used to be a locked, never-actionable checkbox in the module picker; it is no longer a row at all, and is still force-added and installed first. A core-only install gets `bmad-deep-recon` (which lives in core) but not `bmad-spec`.

### Install targets

**Antigravity CLI (AGY)** is a separate installer target in v6.11.0, distinct from the Antigravity IDE entry, installing to `.agents/skills` and `~/.gemini/antigravity-cli/skills` so the two never collide.

v6.12.0 adds **Polytoken**, **Grok**, and **ZCode** targets (`tools/installer/ide/platform-codes.yaml`: `polytoken` -> `.agents/skills`, `grok` -> global `~/.grok/skills`, `zcode` -> `.zcode/skills`).

Run `npx bmad-method install --list-tools` to see every supported tool ID and its target directory.

### Channels and pinning

| Channel | What installs | Who picks it |
|---------|---------------|--------------|
| `stable` (default) | Highest released semver tag; prereleases excluded | Most users |
| `next` | Main branch HEAD at install time. **Headless only since v6.12.3** (`--next=CODE`, `--all-next`, `--channel=next`) | Contributors, early adopters |
| `pinned` | A specific tag you name | Enterprise installs, CI reproducibility |

Channels are per external module. **`core` and `bmm` have no channel** — they ship bundled inside the installer binary, so `--pin bmm=...` and `--next=bmm` are silently ineffective and the installer warns you. Use `npx bmad-method@next install` for a prerelease core/bmm.

These flags still exist in v6.12.0 (`tools/installer/commands/install.js:41-48`: `--channel`, `--all-stable`, `--all-next`, `--next`, `--pin`), but the v6.12.0 docs no longer have a page describing channels; the table above comes from the v6.11.0 install how-to.

**The interactive picker offers only `stable` and `pin` since v6.12.3** (`tools/installer/ui.js:1987-1993`; CHANGELOG v6.12.3: "`next` is gone from the install picker and the channel review, and `--next=CODE` stays for headless use").

**Registry pins (v6.12.2+).** `bmad-modules.yaml` now carries a `pin` field: CIS `pin: v0.3.2`, TEA `pin: v1.27.2` (`bmad-modules.yaml:63,75`). These are the newest versions the v6 installer can install; newer CIS and TEA releases target v7 (CHANGELOG v6.12.2). Since v6.12.4 a pinned module gets **no channel picker** — the installer prints `<code> is pinned to <tag>. Newer versions need the v7 installer: npx skills add …` instead (`tools/installer/ui.js:1946-1957,2016-2025`). `--pin CODE=TAG` still overrides the registry pin. Do not suggest `--next=tea` or `--all-next` to get a newer TEA: the installer's own comment says offering stable or next for a pinned module "leads to a failed install" (`ui.js:1946-1948`).

Precedence when choices overlap (v6.12.3+, from the header comment of `tools/installer/modules/channel-plan.js:13-14`): `--pin` > an explicit per-module choice (`--next=CODE`, or `stable` picked in the picker) > **the registry `pin`** > `--channel` / `--all-*` > the registry `default_channel` > `stable`. Before v6.12.3 the registry pin silently won over the picker (CHANGELOG v6.12.3). That header comment still says "picker next/stable", but the picker itself no longer offers `next` (`ui.js:1987-1993`); follow the code.

`_bmad/_config/manifest.yaml` records exactly what landed on disk, including a `sha` for git-backed modules. For cross-machine reproducibility, convert the recorded tags into explicit `--pin` flags rather than rerunning the same `--modules` command — stable resolves at install time.

## Layered Configuration

v6.11.0 moves configuration to layered TOML. v6.11.0 and v6.12.0 were migration releases, not the cutover: the per-module `_bmad/bmm/config.yaml` still shipped and 23 bmm skills (including the v6 shims) still read it directly.

**Since v6.12.1 every skill reads the same merged config.** Those 23 skills now load config through `resolve_config.py` (CHANGELOG v6.12.1, #3019); in the v6.12.4 tree no file under `src/` references `bmm/config.yaml`. The installer still writes `_bmad/bmm/config.yaml` (`tools/installer/core/installer.js:1022-1030`), but no skill reads it — so overrides in `_bmad/custom/config.toml` and `_bmad/custom/config.user.toml` now reach every skill, where before v6.12.1 they missed the skills that read `config.yaml`.

**Central config resolves in this order, later winning:**

```text
_bmad/config.toml → _bmad/config.user.toml → _bmad/custom/config.toml → _bmad/custom/config.user.toml
```

**Per-skill customization resolves in this order, later winning:**

```text
{skill}/customize.toml → _bmad/custom/{skill}.toml → _bmad/custom/{skill}.user.toml
```

Two rules users need before they edit anything:

- **`_bmad/config.toml` and `_bmad/config.user.toml` are regenerated on every install** (v6.12.0: `docs/customize/customize-bmad.md:265-266,287`, "installer-owned"). Editing them directly means losing the change at the next install. To make a value stick, either re-run the installer with `--set <module>.<key>=<value>`, or shadow it in `_bmad/custom/config.toml`.
- **`_bmad/config.toml` carries user-scope defaults since v6.12.1.** It "also carries each user-scope key's `module.yaml` default, so a clone without `config.user.toml` still resolves it" (`docs/customize/customize-bmad.md:283-285`). A fresh clone with no `config.user.toml` can therefore render `bmad-build` and `bmad-build-auto` (CHANGELOG v6.12.1, #3016). Existing installs pick this up only after re-running the installer.
- **Renderers now halt instead of guessing.** A `{{.var}}` missing from the merged config used to render as an empty string, and an unparseable `_bmad/custom/<skill>.toml` used to be ignored silently. Both now **exit 1 with a clean halt**. Add the missing key, or fix or delete the override.

`--set <module>.<key>=<value>` is the non-interactive path for any module config option. It is applied as a post-install patch, routes user-scope keys to `config.user.toml` and team-scope keys to `config.toml`, writes values verbatim with no template rendering, and performs no validation. `npx bmad-method install --list-options [module]` prints the available keys.

## `bmad-customize`

`bmad-customize` writes sparse TOML overrides under `_bmad/custom/`.

Use it when:
- You want to change an agent's persistent facts, principles, or behavior.
- You want to adjust a workflow template, output path, activation hook, or exposed workflow field.
- You need team-scoped customization (`*.toml`) or personal customization (`*.user.toml`).

Do not use it for hidden step logic that is not exposed in `customize.toml`; use BMad Builder or a feature request for that.

> **Upgrade warning: overrides do not follow renames.** A v6.11.0 rename leaves your old override file stranded. The shim *offers* the migration, but requires explicit approval and never overwrites — and if you decline or the migration is unavailable, **the shim halts instead of forwarding**. An unattended run on an old name with a legacy customization file will refuse to start. Rename tables are in `references/v6-11-migration.md` section H. v6.12.0 adds one rename (`bmad-checkpoint-preview` -> `bmad-walkthrough`) and two override edits that break the same way if skipped: `{diff_output}` -> `{diff_file}` in custom review layers, and re-adding `project-context.md` to `persistent_facts` (it ships empty) if you relied on the auto-load. On a fresh install without `--shims`, no shim exists to offer the migration at all — rename first.

## Rendered Skill Snapshots (`_bmad/render/`)

Skills are rendered through a shared `_bmad/scripts/render_skill.py`, which publishes immutable, content-addressed snapshots under `_bmad/render/`. Each snapshot carries a `manifest.json` recording the renderer and source hashes, the resolved configuration values, and a hash per output file.

- Publishing is **atomic**.
- An existing generation is **verified and reused** rather than re-rendered.
- A hash collision **raises rather than overwrites**.

The practical value is inspectability: `_bmad/render/` is a copy of exactly what ran, so a user debugging odd skill behavior can read the rendered text and the resolved values instead of guessing at the templates. This is also the machinery that makes `uv` a hard requirement.

## Web Bundles

**Web Bundles are current in v6.12.0.** The six planning bundles for web LLM environments are unchanged since v6.10.0 — the `web-bundles/` tree is file-for-file identical between the v6.11.0 and v6.12.0 tags (`releaseTag: web-bundles-v1.0.0`, `releasedAt: 2026-05-25`) — and `docs/customize/use-web-bundles.md` is a live v6.12.0 page. They are for Gemini Gems and ChatGPT Custom GPTs, not local IDE execution.

Do not tell users Web Bundles were removed. Upstream `main` has no `web-bundles/`, but `main` is the unreleased v7 line, not v6.12 (see `references/update-protocol.md`, Phase 2).

| Bundle | Best For | Notes |
|--------|----------|-------|
| Brainstorming Coach | Wide ideation before BMM artifacts | Useful before `bmad-product-brief` or `bmad-prfaq` |
| Product Brief Coach | Brief creation/update/validation | Pairs naturally with `bmad-product-brief` |
| PRFAQ Coach | Working Backwards challenge | Good before PRD commitment |
| PRD Coach | PRD coaching and validation | Produces planning input for IDE work |
| UX Coach | DESIGN.md + EXPERIENCE.md planning | Supports Stitch-oriented handoff |
| Market & Industry Research | Deep Research synthesis | Best when external landscape is current and important |

Supported path: `https://bmadcode.com/web-bundles/` (`docs/customize/use-web-bundles.md:82`).

## BMad Loop

`bmad-loop` is the successor path for unattended dev-loop orchestration.

| Item | Guidance |
|------|----------|
| Installer code | `bmad-loop` (prior code `bauto` is registered as an alias) |
| Default selection | Not selected by default |
| Channel | `stable` |
| Setup | After installing, run `bmad-loop-setup` |
| Worker skill | `bmad-build-auto` — the old ID `bmad-dev-auto` reaches it through the shim only where shims are installed (opt-in on fresh v6.12.0 installs). ⚠️ See the caveat below. |
| Best for | Repeated unattended development iterations with policy, hooks, adversarial review, and deferred-work sweeps |

> ⚠️ **Not verified against the main repo.** `bmad-loop` lives in a separate repository; the v6.12.0 main-repo snapshot carries only its registry entry (unchanged from v6.11.0), not its skill content. The main repo renamed `bmad-dev-auto` to `bmad-build-auto`, so the worker *should* now be `bmad-build-auto`, but whether bmad-loop itself has updated cannot be determined from this snapshot. State this as unconfirmed rather than as fact.

Important boundaries:

- Installing `bmad-loop` only stages the module files. It is a marketplace-plugin module, so its skills are resolved from `.claude-plugin/marketplace.json`.
- Automation is **not active** until `bmad-loop-setup` completes. The installer prints an acknowledgement-required notice saying so.
- Orchestrators should read durable artifacts and spec frontmatter, not infer outcomes from chat text.
- An existing install recorded under the old `bauto` code migrates forward to `bmad-loop` and the stale `_bmad/bauto/` directory is removed, instead of being orphaned as "no source available".

## Official Opt-In Modules

`bmad-modules.yaml` is the **single source of truth** for this list. Do not build it from the docs: `docs/customize/add-modules.md` (which replaced v6.11.0's `docs/reference/modules.md`) omits `bmad-loop` and `wds`. Availability in a project still depends on what was selected during `npx bmad-method install`.

| Module | Code | npm package | Default | Channel | Notes |
|--------|------|-------------|---------|---------|-------|
| BMad Loop | `bmad-loop` | — (marketplace plugin) | Off | stable | Aliases: `bauto`. Run `bmad-loop-setup` after install |
| BMad Test Architect | `tea` | `bmad-method-test-architecture-enterprise` | Off | stable | Enterprise testing BMM add-on |
| BMad Builder | `bmb` | `bmad-builder` | Off | stable | Skill, workflow, and agent builder |
| Creative Intelligence Suite | `cis` | `bmad-creative-intelligence-suite` | Off | stable | Creative thinking partners |
| Game Dev Studio | `gds` | `bmad-game-dev-studio` | Off | stable | Ideate, design, and build games |
| BMad Automator | `automator` | `bmad-story-automator` | Off | next | **Deprecated** — use `bmad-loop` |
| Whiteport Design Studio | `wds` | `bmad-wds` | Off | stable | **Deprecated in v6.11.0** — see below |

A `deprecated: true` module is **hidden from the installer picker unless it is already installed**, so existing users can still see and manage it while new users are never offered it. Its `deprecation-message` is surfaced in the picker hint.

## Deprecated: Whiteport Design Studio (`wds`)

**New in v6.11.0.** WDS was a plain stable module through v6.10.0; it is now marked `deprecated: true` in `bmad-modules.yaml`.

- Hidden from the picker when not installed.
- Existing installs still see it, still select it, and are **never silently stripped**.
- Upstream deprecation message: "Whiteport Design Studio is no longer receiving updates. Its capabilities are being folded into BMad Method (bmm) as enhanced UX features. Your existing install is kept as-is."
- The CHANGELOG adds that key features will merge into a forthcoming `bmad-ux` package.

For new UX work, route to `bmad-ux` rather than WDS.

## Deprecated: BMad Automator

`bmad-automator` is deprecated and replaced by `bmad-loop`.

- New installs should choose `bmad-loop`.
- Existing installs may still show Automator for compatibility and migration.
- Do not recommend Automator for new work unless the project is explicitly pinned to it.

> v6.11.0 change affecting both deprecated modules: **deprecation warnings now fire on every flow, interactive and CLI alike.** Previously a CLI-driven install could silently skip the warning.

## BMad Builder

Use BMad Builder when the exposed customization surface is insufficient and you need new reusable skills, agents, workflows, or modules.

Typical use cases:
- Domain-specific agents such as compliance reviewer, data engineer, or operational analyst.
- Organization-specific workflow sequences.
- Skill or module scaffolding for reuse across teams.
- Replacing ad hoc prompts with installable BMad-style assets.

## TEA — Test Architect Enterprise

TEA is the testing architecture module. It complements BMM but is installed separately. It is **not** deprecated — no `deprecated` flag, `default_channel: stable` — but since v6.12.2 its registry entry carries **`pin: v1.27.2`** (`bmad-modules.yaml:75`): the v6 installer installs TEA v1.27.2, its last v6 release, and newer TEA releases target v7 (CHANGELOG v6.12.2). In v6.12.0 the entry was still unchanged from v6.11.0.

Use TEA when:
- Test strategy must be risk-based rather than just generated tests.
- You need NFR assessment, traceability, CI/test framework setup, ATDD, release gating, or enterprise-grade test governance.
- Brownfield work needs baseline coverage and risk analysis.

See `references/tea-module.md`.

## Game Dev, Creative, And Design Extensions

What the main repo itself says about these modules (`docs/customize/add-modules.md:36-67`):

| Module | Purpose |
|--------|---------|
| BMad Game Dev Studio | Game development for Unity, Unreal, Godot, and custom engines, from prototype to planned production: a Game Design Document (GDD) workflow, game-aware planning and context that feed the standard **Build** implementation loop, narrative design support, and engine-specific architecture guidance |
| Creative Intelligence Suite | Brainstorming, design thinking, and early problem-solving agents (the page lists Innovation Strategist, Design Thinking Coach, Brainstorming Coach, Problem Solver, Creative Problem Solver, Storyteller, Presentation Master) and ideation frameworks such as SCAMPER and reverse brainstorming |
| Whiteport Design Studio | **Deprecated in v6.11.0.** Formerly a UX design extension beyond core `bmad-ux`; capabilities are folding into bmm |

Since v6.12.2 the Creative Intelligence Suite registry entry is pinned to **`v0.3.2`** (`bmad-modules.yaml:63`), its last v6 release; newer CIS releases target v7 (CHANGELOG v6.12.2). A pinned module gets no channel picker (see Channels and pinning).

⚠️ Anything more specific about BMB, CIS, or GDS — module versions, persona names, workflow or skill IDs, agent counts — lives in those external repositories and is **not verified against the v6.12.0 main repo**; say so if it comes up. Module availability can change by installer channel and external repository state. Use `bmad-help` or the installer to verify what is installed in the current project.

## Ecosystem Map

```text
BMad Method (BMM)
├── Core workflows: forge / brief / PRFAQ / PRD / UX / architecture / epics
├── Cross-cutting: help / customize / party-mode / elicitation
├── Review: bmad-review (one skill, many lenses)
├── Research: bmad-deep-recon (three modes, six type packs)
├── Project context: bmad-project-context -> the AGENTS.md block
├── Implementation: bmad-sprint-planning -> bmad-build -> bmad-code-review
│                   bmad-walkthrough for human review of a change
│                   bmad-build-auto for unattended iteration
├── Compatibility: v6-shims (old IDs; opt-in on fresh installs via --shims)
├── Orchestration module: bmad-loop
├── Testing: TEA module + built-in QA generation
├── Domain modules: Builder / Game Dev / Creative
└── Web Bundles: browser LLM planning packs
```

## Routing Rule

When uncertain:

1. Run or ask through `bmad-help`.
2. If the project is existing/brownfield, run `bmad-project-context` first — it writes the verified block in `AGENTS.md`. See `references/brownfield.md`.
3. If the input is messy, use `bmad-spec` (note: bmm, not core, since v6.11.0).
4. If the idea itself is weak or untested, use `bmad-forge-idea`, brief, or PRFAQ before PRD.
5. If the implementation cause is unclear, run `bmad-deep-recon` or a research workorder first; then use `bmad-build` for the change, or `bmad-build-auto` only when the intent is concrete and an orchestrator can poll durable status.
6. If the user asks for repeated unattended implementation, verify `bmad-loop` is installed **and** `bmad-loop-setup` has completed.
7. If a skill halts immediately on a rendered-skill run, check `uv` before anything else.
