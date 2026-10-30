---
name: bmad-guide
description: "Interactive learning guide for BMad-Method v6.12.4 development workflow. Use when the user asks about BMad-Method, BMAD, BMM workflows, lifecycle phases, agents, web bundles, established/brownfield projects, renamed or retired bmad-* skills, or which bmad-* skill to run next. Covers bmad-prd, bmad-ux, bmad-spec, bmad-product-brief, bmad-prfaq, bmad-forge-idea, bmad-build, bmad-build-auto, bmad-walkthrough, bmad-project-context, bmad-deep-recon, bmad-review, bmad-loop, bmad-customize, bmad-help, Party Mode, Advanced Elicitation, TEA testing module, and ecosystem modules."
---

# BMad-Method v6.12.4 Interactive Learning Guide

> **current_version: v6.12.4**

An interactive visual guide covering the BMad-Method ecosystem. It answers in Traditional Chinese, routes users to the right `bmad-*` skill, and can produce clickable SVG workflow maps for drill-down exploration via `sendPrompt()`.

## When To Use

- User asks about BMad-Method concepts, phases, workflows, artifacts, agents, or command routing.
- User asks which `bmad-*` skill to use next.
- User mentions Mary, John, Winston, Amelia, Sally, or a BMad persona role. Paige (Tech Writer) is retired in v6.11.0 — recognize the name and route to `bmad-project-context` or the Analyst `PC` trigger.
- User asks about `bmad-product-brief`, `bmad-prfaq`, `bmad-prd`, `bmad-ux`, `bmad-spec`, `bmad-forge-idea`, `bmad-architecture`, `bmad-create-epics-and-stories`, `bmad-sprint-planning`, `bmad-build`, `bmad-build-auto`, `bmad-code-review`, `bmad-walkthrough`, `bmad-retrospective`, `bmad-correct-course`, `bmad-project-context`, `bmad-deep-recon`, `bmad-review`, `bmad-customize`, or any other `bmad-*` skill.
- User names an older skill ID — v6.10-era `bmad-quick-dev`, `bmad-dev-auto`, `bmad-create-story`, `bmad-dev-story`, `bmad-market-research`, `bmad-document-project`, `bmad-sprint-status`, `bmad-check-implementation-readiness`, or v6.11-era `bmad-checkpoint-preview` (renamed to `bmad-walkthrough` in v6.12.0) — and needs to know what replaced it. These are old names; see `references/v6-11-migration.md` and the retired-name table in `references/workflow-map.md`.
- User asks about established/brownfield projects, the `AGENTS.md` project-context block, `stories.yaml`, `bmad-review` lenses, `bmad-deep-recon` research types, `v6-shims` and the opt-in shim install (`--shims`), customization TOML renames, `persistent_facts`, `uv`, Web Bundles, TEA testing, BMad Loop, BMad Builder, Game Dev, Creative Intelligence, Party Mode, Advanced Elicitation, retired/deprecated workflows, or `*update`.
- User asks about `project-context.md` or document sharding — both are retired capabilities; explain what replaced them rather than routing to them.

## Startup Version Check

0. **Check for the v7 skills line first.** If the user's installed skills include `bmod-method` or `bmod-core-tools`, or any BMad skill folder carries a `bmod.toml`, the user is on the **v7 skills line** (installed with `npx skills add bmad-code-org/BMAD-METHOD`), whatever its version string says — through the v7 preview, `bmod-*/bmod.toml` reads `version = "6.13.0-next"`, which is not a 6.x release. Detect it by looking, never by fetching or writing: check the list of available skills the agent was given for `bmod-method` or `bmod-core-tools`, or list the skills directories the agent loads (for example `~/.claude/skills/`, `.claude/skills/`, `~/.agents/skills/`) for `bmod-*` entries, or check a BMad skill folder for `bmod.toml`. A v6.12 install has no `bmod.toml` anywhere. If the line is v7, say so before answering:
   - this guide covers v6.12, and the v7 preview differs from it in installation, artifacts, and skill names;
   - route setup, status, update, migration, and next-step questions to the installed `bmad` skill;
   - do not recommend any skill that the user's `bmod-*/retired.toml` lists under `removed` (for example `bmad-create-epics-and-stories` and `bmad-sprint-planning`), and do not describe v7 workflows from this guide.
   If none of these signals can be checked, skip this step silently.
1. Read the local `current_version` marker in this file.
2. Try to detect the official latest BMad-Method version:
   - Preferred: GitHub release or tag lookup for `bmad-code-org/bmad-method`.
   - Fallback: `https://registry.npmjs.org/bmad-method/latest`, reading the JSON `version` field.
3. Compare:
   - Same version: continue silently.
   - Different version: show once: `bmad-guide 知識庫版本 v{local}，官方最新 v{remote}。輸入 *update 可更新知識庫。`
   - Detection failure: degrade silently and continue.

The version check must never block the guide response.

## Response Flow

1. Identify the topic category and read the matching reference file(s).
2. Answer in Traditional Chinese, keeping exact skill IDs, file paths, and command names in original form.
3. When a visual map helps, use `references/diagrams.md` and generate an SVG diagram.
4. Make diagram nodes clickable with `sendPrompt('介紹 ...')`.
5. For practical routing questions, lead with the recommended skill, prerequisites, expected input, and output artifact.
6. When the user names a retired or renamed skill, say so plainly, give the current ID and how it is triggered, and check `references/v6-11-migration.md` section H for whether their customization files need renaming. Since v6.12.0, also say that the old ID resolves only where shims are installed (fresh installs omit them unless `--shims` is passed).

## Response Modes

### Learning Mode

For "what is X", "how does this work", or "explain X":
- Start with a concise concept explanation.
- Show where the concept sits in the lifecycle.
- Include common pitfalls and when not to use it.

### Practical Mode

For "what should I do next", "which command", or "how do I run X":
- Lead with the exact `bmad-*` skill ID or workflow.
- Show input -> output.
- Note whether it is an IDE/local workflow or a Web Bundle workflow.

## Prerequisites Pointer

Since v6.11.0, BMad requires Node.js 20.12+ and **`uv`** (unchanged through v6.12.4). `uv` is a hard requirement for rendered skills: `bmad-build` and `bmad-build-auto` halt if it is unavailable, with no interpreter fallback. Python itself is no longer a user prerequisite — scripts run through `uv run`, which provisions its own interpreter. Full installation and module details are in `references/ecosystem-modules.md`.

Since v6.12.2 the v6 installer's start and end messages also advertise the v7 preview: `npx skills add bmad-code-org/BMAD-METHOD`, then `bmad setup` and `bmad migrate` (`tools/installer/install-messages.yaml`). That command installs the **v7 preview, not v6.12** — a different skills layout this guide does not teach. A user who followed it is on the v7 skills line (see Startup Version Check, step 0).

## Diagram Conventions

- Phase 1 = `c-teal`, Phase 2 = `c-blue`, Phase 3 = `c-purple`, Phase 4 = `c-coral`.
- Dev loop = `c-amber`, auxiliary/cross-cutting = `c-gray`, Spec/Build (formerly "Quick Flow") = `c-green`.
- TEA = `c-pink`, Web Bundles = `c-indigo`, ecosystem modules = `c-green`.
- All visible labels in Traditional Chinese.
- Clickable nodes use `onclick="sendPrompt('介紹 ...')"`.

## Reference File Routing

| File | Read when |
|------|-----------|
| `references/workflow-map.md` | Core BMM phases, Four Planning Paths, agents and menu codes, main workflow order, artifact flow, `bmad-build` / `bmad-build-auto` placement, when Build triggers and its light path, Build Auto terminal contract, `stories.yaml` contract, shim install policy and retired-name table, v6.12.0 key changes, v6.12.1–v6.12.4 key changes |
| `references/v6-11-migration.md` | User names any v6.10- or v6.11-era skill ID (including `bmad-checkpoint-preview`), artifact, or menu code and needs the current replacement; shim behavior; customization TOML renames; what is unverified |
| `references/supplementary-workflows.md` | PRD variants, product brief, PRFAQ, `bmad-spec`, `bmad-forge-idea`, Build and Build Auto, review triage and `{diff_file}`, `bmad-review` lenses, `bmad-code-review`, `bmad-walkthrough`, `bmad-deep-recon` types, `bmad-project-context`, `bmad-retrospective`, Party Mode modes, Advanced Elicitation, Web Bundles, retired sharding and tech-writing workflows |
| `references/tea-module.md` | Testing, QA automation, TEA integration, risk-based test strategy |
| `references/ecosystem-modules.md` | Web Bundles, BMad Customize, BMad Loop, BMad Builder, Game Dev, Creative Intelligence, external modules, install prerequisites, layered TOML config |
| `references/brownfield.md` | Existing codebases, established-project onboarding, `bmad-project-context` (five intents incl. `adopt`, admission test, ledger) and the `AGENTS.md` block, `project-context.md` and empty `persistent_facts`, retired `bmad-investigate` routing |
| `references/diagrams.md` | Before generating any SVG visualization |
| `references/update-protocol.md` | User types `*update`, asks to refresh guide knowledge, or version check detects mismatch |

## Built-In Commands

| Command | Description |
|---------|-------------|
| `*update` | Update this guide knowledge base to the latest BMad-Method release using the protocol in `references/update-protocol.md`. |
| `*update --force` | Re-read upstream sources and regenerate guide references even when the version marker already matches. |
