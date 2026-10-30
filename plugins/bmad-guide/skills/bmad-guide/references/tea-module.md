# TEA — Test Architect Enterprise Module

> Source basis: `bmad-method` v6.12.0 tag, dereferenced commit `05bfbd46d00766ec88eb9b42e76be2c575d64d7b` — `docs/build/test-completed-work.md`, `docs/customize/add-modules.md` (§ Test Architect (TEA)), `bmad-modules.yaml` (`tea` entry), `src/bmm-skills/ship/bmad-qa-generate-e2e-tests/SKILL.md`. The v6.11.0 source `docs/reference/testing.md` no longer exists. The v6.12.2 registry pin was re-checked against the `v6.12.4` tag, dereferenced commit `bab9082c3e884e0d72c759bcd1a6d90bcc01be84` (`bmad-modules.yaml`, `CHANGELOG.md`, `tools/installer/ui.js`).
>
> TEA is a **separate repository**. The main-repo snapshot describes it but does not contain its skills. Anything below marked ⚠️ comes from TEA's own documentation or from earlier guide revisions and is **not verified against the v6.12.0 main repo**.

TEA is a separate testing architecture module. Install it through the BMad installer when test strategy needs to go beyond BMM's built-in QA generation.

**Status in v6.12.4: not deprecated, but pinned to TEA v1.27.2.** In v6.12.0 its `bmad-modules.yaml` entry was identical to v6.11.0 — `code: tea`, `name: "BMad Test Architect"`, `default_channel: stable`, `defaultSelected: false`, no `deprecated` flag. v6.12.2 added **`pin: v1.27.2`** (`bmad-modules.yaml:75`): "CIS and TEA install at their last v6 releases (v0.3.2 and v1.27.2); newer releases target v7" (CHANGELOG v6.12.2). Since v6.12.4 the installer shows no channel picker for TEA and prints `tea is pinned to v1.27.2. Newer versions need the v7 installer: npx skills add …` instead; `--pin tea=TAG` still overrides the pin (CHANGELOG v6.12.4; `tools/installer/ui.js:2016-2025`). A user asking for a newer TEA is asking about the v7 line, which this guide does not cover.

## Overview

Per `docs/customize/add-modules.md:71-86`, TEA provides test strategy, automation guidance, and release-gate decisions through an agent, **Murat** (Master Test Architect and Quality Advisor), and nine workflows. Compared with the built-in QA skill it adds risk-based prioritization (P0-P3) and requirements traceability, with optional Playwright Utils and MCP integrations. BMM does not mandate TEA; it is selected when the project needs stronger testing governance.

- Documentation: `https://bmad-code-org.github.io/bmad-method-test-architecture-enterprise/` — upstream points here for TEA's "current workflows, commands, and setup" (`docs/build/test-completed-work.md:102-103`)
- Install: `npx bmad-method install` and select the TEA module
- npm: `bmad-method-test-architecture-enterprise`

## Valid Usage Modes ⚠️

Not verified against the v6.12.0 main repo (no main-repo page describes these modes; they come from TEA's own documentation).

| Mode | Description |
|------|-------------|
| Skip TEA | Existing test process is sufficient |
| TEA Lite | Use Automate / Test Review selectively |
| TEA with BMad | Integrate TEA across planning, architecture, and implementation |
| TEA standalone | Use TEA on a non-BMad project |
| TEA learning | Use TEA as a structured testing learning companion |

## TEA Workflows

The main repo names nine workflows (`docs/customize/add-modules.md:72,84-85`) but gives skill IDs for only three of them.

| Workflow | Skill ID | ID verified in v6.12.0 main repo? | What the main repo says |
|----------|----------|-----------------------------------|-------------------------|
| Automate | `bmad-testarch-automate` | ✅ `docs/build/test-completed-work.md:10` | The heavier generate: fixtures, more test levels, knowledge-base patterns; generates from existing code and can run standalone |
| Test Design | `bmad-testarch-test-design` | ✅ `docs/build/test-completed-work.md:92` | Optional before Automate; improves the run, not a prerequisite |
| Traceability | `bmad-testarch-trace` | ✅ `docs/build/test-completed-work.md:95` | Optional after generation, to check coverage; not part of generate |
| ATDD | ⚠️ not verified | — | For features that do not exist yet (`:98`) |
| Test Review | ⚠️ not verified | — | Available when needed, not required to generate tests (`:98-100`) |
| NFR Assessment | ⚠️ not verified | — | Same (`:98-100`) |
| Release Gate | ⚠️ not verified | — | "release gates are available when you need them" (`:98-99`) |
| CI Setup | ⚠️ not verified | — | Listed under "Provides" (`docs/customize/add-modules.md:85`) |
| Framework Scaffolding | ⚠️ not verified | — | Same (`:85`) |

> ⚠️ **Only the three ✅ IDs are confirmed.** The three verified IDs share the `bmad-testarch-` prefix, but do not extrapolate other IDs from that pattern — check TEA's own docs before scripting against any of them. Earlier revisions of this guide listed bare lowercase labels (`test-design`, `atdd`, `automate`, `test-review`, `trace`, `nfr-assess`, `ci`, `framework`); the three verified IDs show those were not the skill IDs, so do not offer them as commands.

## Integration Points

What the v6.12.0 main repo establishes (`docs/build/test-completed-work.md`):

- **Before generation (optional):** `bmad-testarch-test-design`.
- **Generation of finished work:** `bmad-qa-generate-e2e-tests` (built in) or `bmad-testarch-automate` (TEA).
- **After generation (optional):** `bmad-testarch-trace` to check coverage.
- **Features that do not exist yet:** ATDD.
- **When needed, never required for generation:** test review, NFR assessment, release gates.

⚠️ Phase-by-phase placement (NFR Assessment in Planning; system-level Test Design, Framework Scaffolding, and CI Setup in Solutioning; epic-level Test Design, ATDD, Automate, Test Review, and Traceability in Implementation; Release Gate before release; Traceability early on brownfield systems) is carried from earlier guide revisions and is **not verified against the v6.12.0 main repo**. Present it as a reasonable default, not as upstream's prescription. If testability affects architecture, running system-level test design before the `bmad-sprint-planning` readiness gate remains sensible guidance.

## When Testing Runs In The Loop

**Upstream reversed its timing advice in v6.12.0.** v6.11.0 (`docs/reference/testing.md:98`) said the QA Automate workflow "is designed to run **after a full epic is complete**". v6.12.0 says the opposite (`docs/build/test-completed-work.md:113-114`):

> You can run built-in QA after one change. You do not have to wait for an epic to finish.

The typical v6.12.0 sequence:

1. Implement with `bmad-build` (Developer menu `BD`). If a suite already exists, Build aims to leave it passing.
2. Optionally walk through the result with `bmad-walkthrough`.
3. Generate coverage with `bmad-qa-generate-e2e-tests` (Developer menu `QA`) or `bmad-testarch-automate`.
4. After a whole epic, `bmad-retrospective` is a **different** check — it judges the epic against its spec, not the test suite.

Do not tell users that generating tests per change is a mistake; that was v6.11.0 advice.

## Built-In QA — What It Actually Does

`bmad-qa-generate-e2e-tests` (trigger `QA` via the Developer agent) is part of BMM and needs no installation. It works from the code that exists, using whatever test framework the project already has. Open a fresh chat and name the skill; say what to test before, with, or after the command — a feature, a directory, or "discover what is untested."

Six steps (`docs/build/test-completed-work.md:55-64`):

1. **Detect the test framework** — scans dependencies and existing tests (Playwright, Jest, Vitest, Cypress, and similar). If none exists, looks at the stack and suggests one.
2. **Identify features** — asks what to test, or auto-discovers features in the codebase.
3. **Generate API tests** when there are endpoints — status codes, response shape, happy path, and one or two error cases.
4. **Generate E2E tests** when there is a UI — user workflows with semantic locators (roles, labels, text) and visible-outcome assertions.
5. **Run the tests** and fix failures immediately.
6. **Write a summary** of what was generated and what is still uncovered.

Output: test files under the project's `tests/` directory, and a summary at `{implementation_artifacts}/tests/test-summary.md` (`bmad-qa-generate-e2e-tests/SKILL.md:65`).

Generated tests stay simple on purpose:

- Standard framework APIs only.
- Semantic locators for UI tests (roles, labels, text — not CSS selectors).
- Independent tests with no order dependencies.
- No hardcoded waits or sleeps.
- Clear descriptions that read as feature documentation.

Scope boundary: the QA skill **generates tests only**. Happy path plus a few critical errors is the ceiling, and it does not compose complex fixtures. Review is `bmad-build` during the run, or `bmad-code-review` (`CR`) for another pass.

## TEA vs BMM Built-In QA

| Aspect | BMM QA (`bmad-qa-generate-e2e-tests`) | TEA |
|--------|---------------------------------------|-----|
| Best for | Simple coverage of implemented features | Heavier coverage of the same kind of work; test strategy, quality gates, traceability |
| Setup | Included with BMM | Install the TEA module |
| Approach | Generate from the code that exists | Same for Automate (standalone); optional test design improves the run |
| What it covers | API and E2E; happy path plus a few errors | API, E2E, fixtures, more patterns; optional component tests |
| Strategy | Happy path + critical edge cases | Risk-based prioritization (P0-P3) |
| Workflows | One skill | Nine workflows (three IDs verified, see above) |
| Agent | Amelia / DEV (`QA`) | **Murat** — Master Test Architect and Quality Advisor |

Rows 1-4 follow `docs/build/test-completed-work.md:20-25`; rows 5-7 follow `docs/customize/add-modules.md:71-86`.

Upstream's own recommendation (`docs/build/test-completed-work.md:27-31`): **most projects should start with built-in QA.** Use `bmad-testarch-automate` when you want the heavier generate; install TEA later, alongside it, if test strategy, quality gates, or requirements traceability become necessary.

## Routing Rule

- "Generate tests for this implemented feature / this change" -> `bmad-qa-generate-e2e-tests`.
- "Heavier coverage with fixtures and more test levels" -> `bmad-testarch-automate` (TEA).
- "What should our test strategy be", "what are the risks", "is this covered", "how do we set up CI/test architecture", "can we ship this" -> TEA.
- "Walk me through this change before testing" -> `bmad-walkthrough` (manual observations, not generated coverage).
- Cause of failure unknown -> investigate first. `bmad-deep-recon` (technical type) replaced the retired research trio, and `bmad-investigate` has been retired since v6.10.0. In Control Tower contexts, open a research workorder before deciding whether TEA or implementation work is needed.
