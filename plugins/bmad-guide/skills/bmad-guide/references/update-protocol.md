# BMad-Guide Update Protocol

This file defines how the `bmad-guide` knowledge base checks the official BMad-Method version and refreshes its reference files.

## Passive Version Detection

1. Read `current_version` in `SKILL.md`.
2. Resolve the official latest version through this fallback chain:

| Priority | Method | Query / URL |
|----------|--------|-------------|
| 1 | GitHub release/tag | `https://github.com/bmad-code-org/bmad-method/releases/latest` or tag lookup |
| 2 | npm registry | `https://registry.npmjs.org/bmad-method/latest` |
| 3 | Web search | `bmad-method latest version bmad-code-org` |

3. Compare:
   - Same version: continue silently.
   - Different version: show a one-time update hint.
   - Detection failure: continue silently.

The guide must never block normal help because version detection failed.

## Manual Update Command

Triggered by `*update` or `*update --force`.

### Phase 1: Version Resolution

1. Detect `--force`.
2. Resolve latest version through the fallback chain. Use npm `latest`, never the npm `next` dist-tag: `next` is a 6.x prerelease (for example `6.12.3-next.1`), not the v7 line, and must not be read as evidence of v7 either way.
3. If detection fails and not force mode, stop with a clear network/version-resolution error.
4. If the version matches and not force mode, say the guide is current.
5. Stop and report instead of regenerating when **either** signal says the target is the v7 line:
   - the resolved version is a new **major** (v7 or later); **or**
   - the snapshot at the resolved ref has no `package.json` and ships a top-level `skills/` with `skills/bmod-*/bmod.toml` module records.

   **The v7 line does not announce itself through its version number.** Through the v7 preview its module records read `version = "6.13.0-next"` (`skills/bmod-method/bmod.toml`), a string that is never published to npm and never tagged, so the tag and npm chain above never resolves to it. This guide's file layout and every source path below assume the v6 repository structure (see Phase 2).
6. Otherwise continue.

### Phase 2: Source Snapshot

**Read the release tag, never `main`.** Since v6.12, upstream `main` and `dev` carry the next major line, not the 6.x code: the `main` tree has no `package.json` and no `web-bundles/`, and ships a top-level `skills/` with per-skill `bmod.toml` files. The 6.x line is maintained on the `V6.12` branch and published as `v{version}` tags. Anything read from `main` describes v7 work in progress, not the installed product — do not write it into the guide as v6 behavior.

Since 2026-09-20 (`35d39c3e`, "replace per-skill module metadata with bmod module records"), the v7 line's version marker is the `[bmod] version` of each `skills/bmod-*/bmod.toml`; `pyproject.toml` says so and itself holds `version = "0"`. It reads `6.13.0-next` throughout the preview. `main` is not only work in progress: it is what `npx skills add bmad-code-org/BMAD-METHOD` installs, and since v6.12.2 the v6 installer itself points users there (`tools/installer/install-messages.yaml`). A user can therefore be running v7 while this protocol correctly resolves `6.12.x` — that case is caught by the local check in `SKILL.md` (Startup Version Check, step 0), not here. v6.12.0 is the fork point: `git merge-base main V6.12` is its commit.

Prefer a deterministic tag snapshot. Clone to a temporary directory **outside** this repository.

```bash
git clone --depth 1 --branch v{version} https://github.com/bmad-code-org/bmad-method.git <temp-dir>
```

The repo is also reachable as `BMAD-METHOD.git`; GitHub resolves repository names case-insensitively, so either spelling works.

Record:
- Resolved tag.
- Dereferenced commit SHA.
- `package.json` version.
- The `CHANGELOG.md` section for the version.
- Release notes URL.

Use these exact commands — **`git rev-parse v{version}` alone is not the commit SHA.** A `--depth 1 --branch <tag>` clone brings back only that tag, and the tag is an *annotated tag object*, so a bare `rev-parse` returns the tag object's own SHA, not the commit it points at:

```bash
git rev-parse "v{version}^{commit}"     # dereferenced commit SHA — record this one
git rev-parse "v{version}"              # annotated tag object SHA (different value; not the commit)
git rev-parse HEAD                      # equals the dereferenced commit SHA in a tag clone
git log -1 --format="%H|%ci|%s"
```

For v6.12.4 these resolve to commit `bab9082c3e884e0d72c759bcd1a6d90bcc01be84` (also the `V6.12` branch head as of 2026-10-15) and tag object `eecafe9d4bcad92166bee08623e0526009d862c4`. For v6.12.0 they were commit `05bfbd46d00766ec88eb9b42e76be2c575d64d7b` and tag object `b28fef564f2c48ac20d969bcccaf2fc08d503afb`.

Prefer `CHANGELOG.md` over GitHub release notes as the primary narrative source: it lives inside the repo, it is pinned by the tag, and it can be existence-checked like any other path.

> Environment note: on Windows, sandboxed shells have been observed to report `exit 0` on a clone while writing nothing to disk. Verify the snapshot directory is non-empty before trusting it, and prefer native PowerShell for the clone and for filesystem writes.

### Phase 3: Reference Regeneration

Update each guide file from the source snapshot. All paths below are relative to the snapshot root and were existence-checked against the v6.12.0 tag, then re-checked unchanged against the v6.12.4 tag. Glob rows were checked to match at least one file. The one exception is `_bmad/render/`: it is a runtime path inside an installed project, not a snapshot path, so it never exists in a tag snapshot — do not report it as missing.

| Guide File | Upstream Sources |
|------------|------------------|
| `SKILL.md` | `package.json` (`current_version`), `src/bmm-skills/module-help.csv`, `src/core-skills/module-help.csv` (the skill IDs named in `description`), `docs/reference/skills-and-agents.md` (persona roster), `src/bmm-skills/agents/*/customize.toml` |
| `workflow-map.md` | `package.json`, `src/bmm-skills/module-help.csv`, `src/core-skills/module-help.csv`, `src/bmm-skills/agents/*/customize.toml` (authoritative menu codes), `src/bmm-skills/plan/*/SKILL.md`, `src/bmm-skills/ship/*/SKILL.md`, `src/bmm-skills/ship/bmad-build/spec-template.md`, `src/bmm-skills/ship/bmad-build-auto/spec-template.md`, `src/bmm-skills/ship/bmad-build-auto/step-04-review.md` (terminal contract), `docs/reference/skills-and-agents.md`, `docs/plan/choose-a-planning-path.md`, `docs/build/build-a-change.md`, `docs/build/walk-through-a-change.md`, `docs/build/autonomous-development-loops.md`, `src/bmm-skills/v6-shims/README.md`, `tools/installer/core/shim-policy.js`, `removals.txt`, `CHANGELOG.md` (version section) |
| `v6-11-migration.md` | `src/bmm-skills/v6-shims/README.md`, `src/core-skills/v6-shims/README.md`, `src/bmm-skills/v6-shims/*/SKILL.md` and `src/core-skills/v6-shims/*/SKILL.md` (frontmatter `metadata.lifecycle`, On Activation steps), `src/bmm-skills/plan/bmad-generate-project-context/SKILL.md`, `src/core-skills/bmad-review/customize.toml` (authoritative lens codes), `src/bmm-skills/agents/*/customize.toml` (authoritative menu codes), `tools/installer/core/shim-policy.js`, `tools/installer/commands/install.js` (`--shims` / `--no-shims`), `removals.txt`, `docs/reference/skills-and-agents.md`, `CHANGELOG.md` (version section) |
| `supplementary-workflows.md` | `src/core-skills/module-help.csv`, `src/bmm-skills/module-help.csv`, `src/core-skills/bmad-*/SKILL.md`, `src/core-skills/bmad-review/customize.toml`, `src/bmm-skills/plan/bmad-spec/assets/stories-schema.md`, `src/bmm-skills/ship/bmad-code-review/customize.toml` (review layers), `src/bmm-skills/ship/bmad-build/references/claims-check.md`, `docs/build/*.md`, `docs/plan/*.md`, `docs/customize/run-multi-agent-discussions.md`, `docs/customize/use-web-bundles.md`, `web-bundles/README.md`, `src/core-skills/v6-shims/README.md` |
| `tea-module.md` | `docs/build/test-completed-work.md` (**the only main-repo page that names TEA workflow IDs**), `docs/customize/add-modules.md` (TEA section), `bmad-modules.yaml` (`tea` entry), and TEA's own external documentation at `https://bmad-code-org.github.io/bmad-method-test-architecture-enterprise/` — **outside the main-repo snapshot, so anything sourced only from it must be marked unverified** |
| `ecosystem-modules.md` | `bmad-modules.yaml` (**single source of truth for the module list**), `web-bundles/README.md`, `web-bundles/bundles.json`, `docs/customize/add-modules.md`, `docs/start/install-bmad.md` (prerequisites), `docs/customize/customize-bmad.md` (layered TOML), `docs/customize/use-web-bundles.md`, `README.md` (prerequisites; see the contradiction note in `ecosystem-modules.md`), `src/scripts/render_skill.py` (the `_bmad/render/` contract; `_bmad/render/` itself is a post-install runtime path, not a snapshot path) |
| `brownfield.md` | `docs/existing-codebases/*.md`, `src/bmm-skills/plan/bmad-project-context/SKILL.md`, `src/bmm-skills/plan/bmad-project-context/references/best-practices.md` (admission test), `src/bmm-skills/plan/bmad-generate-project-context/SKILL.md`, `docs/build/test-completed-work.md` (TEA for brownfield) |
| `diagrams.md` | Internal guide diagram rules. Follows the names and artifacts settled by `workflow-map.md` and `supplementary-workflows.md`; it has no independent upstream source, but it **must** be re-checked on every update — a diagram that still draws a retired chain as live is a routing defect like any other. |
| `update-protocol.md` | This protocol itself, updated when upstream repo structure or release practice changes. v6.11.0 reissued the table after a structural reorganization; v6.12.0 reissued it again because upstream reorganized `docs/` by task. |

#### Source-selection rules

Four rules earned from real misreads. Apply them before trusting any single upstream file.

1. **The module list comes from `bmad-modules.yaml`, not the docs.** `docs/customize/add-modules.md` (which replaced `docs/reference/modules.md`) describes `bmb`, `cis`, `gds`, and `tea` but omits `bmad-loop` and `wds`. The YAML registry is authoritative and carries `deprecated`, `default_channel`, `aliases`, `npmPackage`, post-install messages, and since v6.12.2 an optional `pin` (the newest tag the v6 installer can install for that module).
2. **A skill's retirement status comes from its own `SKILL.md` frontmatter, not from its directory.** `bmad-generate-project-context` is a deprecated forwarder while still living in `src/bmm-skills/plan/`. Directory position proves nothing. Since v6.12.0 the installer itself decides shim status this way: any skill whose frontmatter has `metadata.lifecycle: shim` is a shim (`tools/installer/core/shim-policy.js`, `isShimSkill()`), wherever it lives.
3. **Do not derive the phase table from `module-help.csv`'s `phase` column.** It still mixes vocabularies in v6.12.0 — `bmad-prd` and `bmad-ux` read `2-planning` while others read `plan` / `ship` / `anytime`. The v6.11.0 phase source, `docs/reference/workflow-map.md`, no longer exists, and the v6.12.0 docs are organized by task rather than by numbered phase. Keep the guide's existing phase structure and change it only on positive evidence: `preceded-by` / `followed-by` in `module-help.csv`, `docs/plan/choose-a-planning-path.md`, or the skills' own content.
4. **Prefer `CHANGELOG.md` to GitHub release notes.** It is in-repo, tag-pinned, and existence-checkable.

#### Sources that no longer exist

These paths were valid in earlier protocol revisions and are now gone. Their absence is itself the evidence of removal; do not restore them to the table.

**Gone in v6.12.0** (24 paths from the v6.11.0 table; upstream reorganized `docs/` by task into `docs/start/`, `docs/plan/`, `docs/build/`, `docs/customize/`, `docs/existing-codebases/`, plus `docs/reference/skills-and-agents.md`). The replacement column names the nearest v6.12.0 home of the same topic; it is not a redirect upstream declares.

| Removed source | Nearest v6.12.0 home |
|----------------|----------------------|
| `docs/reference/agents.md` | `docs/reference/skills-and-agents.md`; menus in `src/bmm-skills/agents/*/customize.toml` |
| `docs/reference/workflow-map.md` | `docs/reference/skills-and-agents.md`, `docs/plan/choose-a-planning-path.md` (no phase-sectioned page remains; see rule 3) |
| `docs/reference/build-auto.md` | `docs/build/autonomous-development-loops.md`; contract in `src/bmm-skills/ship/bmad-build-auto/` |
| `docs/explanation/build.md` | `docs/build/build-a-change.md` |
| `docs/explanation/sprint-planning.md` | `docs/plan/break-work-into-stories-and-track-it.md` |
| `docs/reference/core-tools.md` | `docs/reference/skills-and-agents.md` § Core Skills; `src/core-skills/module-help.csv` |
| `docs/explanation/deep-recon.md` | `docs/plan/research-a-decision.md` |
| `docs/explanation/advanced-elicitation.md` | No dedicated page; `docs/reference/skills-and-agents.md` § `bmad-advanced-elicitation` and `src/core-skills/bmad-advanced-elicitation/` |
| `docs/explanation/party-mode.md` | `docs/customize/run-multi-agent-discussions.md` |
| `docs/explanation/retrospective.md` | `docs/build/finish-an-epic.md` |
| `docs/explanation/checkpoint-preview.md` | `docs/build/walk-through-a-change.md` (the skill itself was renamed to `bmad-walkthrough`) |
| `docs/explanation/forge-idea.md` | `docs/plan/explore-and-validate-an-idea.md` |
| `docs/how-to/quick-fixes.md` | `docs/build/build-a-change.md` (light path), `docs/existing-codebases/start-in-an-existing-codebase.md` |
| `docs/reference/testing.md` | `docs/build/test-completed-work.md` |
| `docs/reference/modules.md` | `bmad-modules.yaml` (authoritative), `docs/customize/add-modules.md` |
| `docs/how-to/install-bmad.md` | `docs/start/install-bmad.md` |
| `docs/how-to/customize-bmad.md` | `docs/customize/customize-bmad.md` |
| `docs/how-to/install-custom-modules.md` | `docs/customize/add-modules.md` |
| `docs/explanation/web-bundles.md` | `docs/customize/use-web-bundles.md` |
| `docs/how-to/established-projects.md` | `docs/existing-codebases/start-in-an-existing-codebase.md` |
| `docs/explanation/project-context.md` | `docs/existing-codebases/set-and-maintain-project-context.md` |
| `docs/explanation/project-context-theory.md` | `docs/existing-codebases/theory-of-project-context.md` |
| `docs/explanation/established-projects-faq.md` | `docs/existing-codebases/start-in-an-existing-codebase.md` (FAQ content rebuilt in `brownfield.md`) |
| `docs/how-to/project-context.md` | `docs/existing-codebases/set-and-maintain-project-context.md` |

**Gone before v6.12.0:**

| Removed source | Replacement |
|----------------|-------------|
| `docs/reference/dev-auto.md` | `docs/reference/build-auto.md` (itself gone in v6.12.0, see above) |
| `docs/explanation/adversarial-review.md` | Material moved to the `adversarial` lens itself |
| `src/core-skills/bmad-spec/` | `src/bmm-skills/plan/bmad-spec/` |
| `src/core-skills/bmad-index-docs/`, `src/core-skills/bmad-shard-doc/` | None — removed outright |
| `src/bmm-skills/bmad-agent-tech-writer/` | None — Paige retired |
| `src/bmm-skills/plan/bmad-check-implementation-readiness/` | `src/bmm-skills/plan/bmad-sprint-planning/` |
| `src/bmm-skills/ship/bmad-quick-dev/`, `src/bmm-skills/ship/bmad-dev-auto/` | `src/bmm-skills/ship/bmad-build/`, `src/bmm-skills/ship/bmad-build-auto/` (old IDs live in `src/bmm-skills/v6-shims/`) |
| `docs/how-to/shard-large-documents.md` | None — removed in all five locales |
| `docs/how-to/non-interactive-installation.md` | `docs/how-to/install-bmad.md` (itself gone in v6.12.0; now `docs/start/install-bmad.md`) |
| `tools/installer/external-official-modules.yaml` | `bmad-modules.yaml` at the repo root |

### Phase 4: Merge Policy

- Keep the guide concise and navigational; do not paste full upstream skills.
- Use upstream names exactly for skill IDs, action names, output paths, and artifact filenames.
- Preserve Traditional Chinese explanation style.
- Remove retired workflow names or mark them as retired.
- Include newly added core capabilities and official opt-in modules where users need routing guidance.
- Record deprecated module migrations, especially when the installer keeps existing installs visible.
- Record customization-file renames whenever a skill ID changes; overrides do not follow renames.
- Distinguish a **forwarding shim** from a skill **retained in full**. Both live under `v6-shims/`, but only the first forwards. Getting this wrong tells users their working skill is a stub.
- Say whether an old ID resolves at all. Since v6.12.0, shims are opt-in on fresh installs, so "the old ID still forwards" is true only where shims are installed.
- Add new workflows where users need routing guidance.
- Update `current_version`, title, description, and version-specific key changes.
- When upstream sources contradict each other, say so and name the source you followed. Prefer shipped source (`customize.toml`, `bmad-modules.yaml`, skill frontmatter, installer code) over prose documentation.
- Never upgrade an unverified claim into a stated fact. External modules (TEA, BMB, CIS, GDS, `bmad-loop`) are not in the main-repo snapshot; anything sourced from them alone must carry an explicit "not verified against the main repo" note. The same applies to content read from upstream `main` (Phase 2).

### Phase 5: Verification

Run at minimum:

```bash
git diff --check -- BMad-Guide-Skill
```

**Retired-name sweep** — run over the whole guide tree, not only the files you edited:

```powershell
Select-String -Path BMad-Guide-Skill/bmad-guide-v{version}/**/*.md -Pattern '{old_version}|bmad-quick-dev|bmad-dev-auto|bmad-create-story|bmad-dev-story|bmad-create-prd|bmad-edit-prd|bmad-validate-prd|bmad-create-architecture|bmad-market-research|bmad-domain-research|bmad-technical-research|bmad-sprint-status|bmad-document-project|bmad-generate-project-context|bmad-editorial-review|bmad-review-adversarial-general|bmad-review-edge-case-hunter|bmad-review-verification-gap|bmad-index-docs|bmad-shard-doc|bmad-check-implementation-readiness|bmad-agent-tech-writer|bmad-investigate|bmad-automator|bmad-create-ux-design|bmad-checkpoint-preview|diff_output|project-context\.md|final_revision|Paige'
```

Retired/deprecated names may appear **only** when explicitly described as retired, deprecated, replaced, or compatibility shims. Judge every hit; a hit in a live routing sentence is a defect, not a false positive.

> The pre-v6.11.0 pattern held only three names (`bmad-investigate`, `bmad-automator`, `bmad-create-architecture`). That is why a rename-heavy release could pass verification with stale routing intact. Grow this list every time a release retires a name.
>
> v6.12.0 changes to the pattern: **added** `bmad-checkpoint-preview` (renamed to `bmad-walkthrough`) and `diff_output` (the review placeholder is now `{diff_file}`). **Removed** `deferred-work.md`: interactive `bmad-build` still writes it in v6.12.0 (`src/bmm-skills/ship/bmad-build/step-01-clarify-and-route.md:87`); only `bmad-build-auto` replaced it with the spec frontmatter `deferred` list. Check `deferred-work.md` by hand instead — it is a defect only when a sentence says Build Auto writes it.

**Positive sweep** — confirm the new names actually landed, rather than the old ones merely being deleted:

```powershell
Select-String -Path BMad-Guide-Skill/bmad-guide-v{version}/**/*.md -Pattern 'bmad-build|bmad-build-auto|bmad-project-context|bmad-deep-recon|bmad-review|bmad-walkthrough|diff_file|--shims|stories\.yaml|AGENTS\.md'
```

**File inventory** — and confirm no dot-paths (editor or linter caches such as `.sonar/`) are about to be packaged or installed:

```powershell
Get-ChildItem BMad-Guide-Skill/bmad-guide-v{version} -Recurse -File
Get-ChildItem BMad-Guide-Skill/bmad-guide-v{version} -Recurse -Force | Where-Object { $_.Name -like '.*' }
```

### Phase 6: Output Summary

Report:
- Version and upstream commit used.
- Files created or updated.
- Verification commands and results, including the retired-name sweep with a per-hit verdict.
- Upstream contradictions found and which source was followed.
- Claims that remain unverified.
- Any intentionally preserved dirty worktree state.

## Safety Rules

- In a versioned repo package, write only under `BMad-Guide-Skill/bmad-guide-v{version}/` unless the user explicitly asks to update an installed skill path.
- In an installed skill, write only under the installed `bmad-guide` directory.
- Do not modify other skills or global skill definitions without explicit authorization.
- Do not delete older versioned guide directories.
- Keep the upstream clone outside this repository.
- Back up an installed skill directory before overwriting it, and verify the install file by file afterwards. Put the backup **outside** the skills directory (for example `~/.claude/skill-backups/`): a backup folder with a `SKILL.md` at its root inside `~/.claude/skills/` is registered as a live skill and can win routing with stale content.
- Exclude dot-paths (`.sonar/` and similar) from packaging and installation.
- If upstream lookup fails, stop or keep the existing files unchanged rather than inventing a version.
