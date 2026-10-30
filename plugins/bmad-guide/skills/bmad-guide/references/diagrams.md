# BMad-Method Diagram Templates

> Diagram rules for BMad-Method v6.12.4 (no diagram-relevant change since v6.12.0). This file has no upstream source of its own: names, chains, and artifacts follow `workflow-map.md` and `supplementary-workflows.md`, and must be re-checked on every update (`update-protocol.md`, Phase 3).

## Color Conventions

| Element | Class | Usage |
|---------|-------|-------|
| Phase 1 Analysis | `c-teal` | Brainstorming, forge idea, deep recon, brief, PRFAQ |
| Phase 2 Planning | `c-blue` | PRD, UX, spec |
| Phase 3 Solutioning | `c-purple` | Architecture, epics, sprint planning + readiness gate |
| Phase 4 Implementation | `c-coral` | Build, code review, retrospective |
| Dev loop | `c-amber` | Sprint planning, build, code review, build auto |
| Auxiliary | `c-gray` | Help, customize, correct course, walkthrough |
| Spec / Build (formerly "Quick Flow") | `c-green` | `bmad-spec`, `bmad-build`, `bmad-build-auto` |
| Review lenses | `c-slate` | `bmad-review` and its lens set |
| TEA | `c-pink` | Test architecture workflows |
| Web Bundles | `c-indigo` | Gemini Gems / ChatGPT Custom GPT planning bundles |
| Ecosystem modules | `c-green` | BMad Loop, Builder, Game Dev, Creative |
| Retired / shim | `c-gray` at opacity 0.5, `stroke-dasharray="4 3"` | Old IDs shown only for recognition |

Two conventions changed in v6.11.0:

- The old "Spec / Quick Flow" class is now **"Spec / Build"**. Keep "(formerly Quick Flow)" in the legend while users still say the old name.
- Retired names never get a live phase color. Draw them dashed, dimmed, and labeled with the arrow form described under Common Node Labels.

One convention changed in v6.12.0:

- `bmad-checkpoint-preview` is now `bmad-walkthrough` (`CK` -> `WT`). Draw `bmad-walkthrough` as the live node; the old ID appears only as a retired label. Do not attach it to the Developer (Amelia) card — `WT` is not on any agent menu.

## SVG Setup

```svg
<svg width="100%" viewBox="0 0 680 [H]">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

## Diagram Types

### 1. Full Workflow Map

Use for lifecycle overview. Show `bmad-forge-idea` / brief / PRFAQ as optional entry shapes, then `bmad-spec` / PRD -> UX -> architecture -> epics -> `bmad-sprint-planning` -> `bmad-build`.

### 2. Phase Detail

Use when drilling into one phase. Include workflow IDs, agent labels, inputs, outputs, and sequence arrows.

### 3. Planning Shape Comparison

Use when comparing `bmad-spec`, product brief, PRFAQ, PRD, and UX. Show what each artifact owns and what downstream workflow consumes it.

### 4. Dev Loop

Use for Phase 4. The chain is a single line (set in v6.11.0, unchanged in v6.12.0; `module-help.csv` gives `bmad-build` `preceded-by=bmad-sprint-planning`, `followed-by=bmad-code-review`):

```text
bmad-sprint-planning ──► bmad-build ──► bmad-code-review ──┬──► next story
                                                            └──► bmad-retrospective
```

Side nodes: `bmad-correct-course`, `bmad-walkthrough` (optional human review of a finished change), `bmad-qa-generate-e2e-tests` (may run after a single change — v6.12.0 dropped the "wait for the whole epic" advice), and `bmad-build-auto` for unattended iteration.

Note for the diagram's own accuracy: `bmad-sprint-planning` sits in **Phase 3** since v6.11.0 and opens with the readiness gate, so draw it as the handoff node between Phase 3 and Phase 4 rather than inside the loop body. Do not draw `bmad-create-story` or `bmad-dev-story` in this chain — they left it, and since v6.12.0 a fresh install without `--shims` does not even contain them. Do not draw a "Quick Flow" branch through `bmad-quick-dev`; that path is now `bmad-spec` / `bmad-build` (`c-green`), and `bmad-quick-dev` is a retired label.

### 5. Agent Roster

Use for "who does what" questions. Five cards: **Mary** (Analyst), **John** (PM), **Winston** (Architect), **Amelia** (DEV), **Sally** (UX Designer). Group by phase affinity and include menu codes.

Menu codes are unchanged in v6.12.0. `bmad-walkthrough` (`WT`) belongs to no card. Paige (Tech Writer) is retired in v6.11.0. Do not include her among the five. If the diagram needs to show history, add one dimmed dashed card labeled retired, pointing to `bmad-project-context` / Analyst `PC`.

### 6. Deep Recon Three-Mode Map

Replaces the old "Research Architecture" diagram, which showed three separate research skills as three branches. That shape is wrong now — there is one skill.

Show `bmad-deep-recon` at the center with:
- **Three modes**: draft a deep-research prompt for the user's own ChatGPT / Gemini / Grok / Perplexity subscription; process a finished report into a cited summary downstream skills reuse; or run the research inline.
- **Six type packs**: `market`, `domain`, `technical`, `competitive`, `user-voice`, `academic-lit`.
- A **select shape** for choose-between decisions.
- Outputs feeding brief / PRFAQ / PRD / architecture.

### 7. Spec Kernel

Use for `bmad-spec`. Show messy input -> kernel fields -> companions -> downstream consumers. Include the optional Story Breakdown branch emitting `stories.yaml` beside `SPEC.md`.

### 8. UX Two-Spine Map

Use for `bmad-ux`. Show sources -> discovery -> `DESIGN.md` and `EXPERIENCE.md` -> architecture / implementation / design handoff.

### 9. TEA Integration Map

Use for TEA questions. Draw the generation flow the v6.12.0 main repo states (`docs/build/test-completed-work.md`): optional `bmad-testarch-test-design` -> `bmad-qa-generate-e2e-tests` **or** `bmad-testarch-automate` -> optional `bmad-testarch-trace`; ATDD only for features that do not exist yet; test review, NFR assessment, and release gates as on-demand side nodes. Generation may follow a single change — do **not** label Automate "after the whole epic completes" (v6.11.0 advice, reversed in v6.12.0).

Only those three `bmad-testarch-*` IDs are verified; label every other TEA node by its display name, not a guessed ID. If you add a phase-placement overlay (NFR in Phase 2; system test design, framework, CI in Phase 3; the rest in Phase 4; release gate at release), mark it as the guide's suggested default — it is not verified against the v6.12.0 main repo (see `tea-module.md`).

### 10. Ecosystem Overview

Use for modules and web bundles. Show BMM core at center, Web Bundles as the web planning front door, TEA/testing, `bmad-loop`, Builder/customization, and external domain modules as satellites. Draw `wds` and `automator` dimmed and dashed — both are deprecated.

### 11. Review Lens Map

New in v6.11.0. Show content type (diff / code / document) -> the lens set that applies -> one unified findings shape.

Lens codes, read from `src/core-skills/bmad-review/customize.toml`: `adversarial`, `edge-case-hunter`, `verification-gap`, `structure`, `prose`. `prose` runs `after = "structure"`, so draw it downstream rather than in parallel.

### 12. Migration Map (v6.11.0 / v6.12.0)

Show old ID -> shim -> new ID, with the shim kind labeled on the edge. Include the v6.12.0 edge `bmad-checkpoint-preview` -> `bmad-walkthrough`, with a note that it halts until a legacy `_bmad/custom/bmad-checkpoint-preview*.toml` is renamed. Two edge kinds, and conflating them is the most common error:

- **Forwarding shim** — holds no logic, forwards with an intent, type, or lens pre-set.
- **Retained in full** — the whole original workflow is still there and still runs when named. `bmad-create-story` and `bmad-dev-story` are this kind; never draw them as forwarding into `bmad-build`.

Since v6.12.0, every shim edge is **install-dependent**: shims are opt-in on fresh installs (`--shims`). Label the shim column "only where shims are installed" rather than implying the old ID always resolves.

Full tables live in `references/v6-11-migration.md`; the diagram is a visual index into it, not a replacement.

## Clickable Node Pattern

```svg
<g class="node c-[color]" onclick="sendPrompt('介紹 [workflow] 的詳細流程')">
  <rect x="X" y="Y" width="W" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="CX" y="CY-8" text-anchor="middle" dominant-baseline="central">Title</text>
  <text class="ts" x="CX" y="CY+10" text-anchor="middle" dominant-baseline="central">-> output</text>
</g>
```

## Layout Rules

- ViewBox width is 680; height is content height plus about 40px padding.
- Phase containers: 600px wide, x=40, rx=16.
- Workflow nodes: 140-200px wide, 44-56px tall, rx=8.
- Use stable dimensions so labels and hover states cannot resize the layout.
- Dashed grouping containers use `stroke-dasharray="4 3"` and opacity 0.4-0.5.
- Title text class `th`: about 14px. Subtitle text class `ts`: about 12px.
- Keep labels short, preferably five Traditional Chinese words or fewer.
- All `sendPrompt()` calls should be in Traditional Chinese.
- Do not use diagrams to hide uncertainty; if routing depends on project state, show the decision node.

## Common Node Labels

### Current skills

| Skill | Label |
|-------|-------|
| `bmad-spec` | SPEC 精粹 |
| `bmad-forge-idea` | 想法鍛造 |
| `bmad-product-brief` | 產品簡報 |
| `bmad-prfaq` | PRFAQ 壓測 |
| `bmad-prd` | PRD 規格 |
| `bmad-ux` | UX 雙主軸 |
| `bmad-architecture` | 架構脊柱 |
| `bmad-create-epics-and-stories` | Epic/Story |
| `bmad-sprint-planning` | Sprint 規劃 |
| `bmad-build` | 建置實作 |
| `bmad-build-auto` | 自動迭代 |
| `bmad-code-review` | 程式審查 |
| `bmad-retrospective` | 回顧覆盤 |
| `bmad-correct-course` | 航道修正 |
| `bmad-project-context` | 專案脈絡 |
| `bmad-deep-recon` | 深度偵查 |
| `bmad-review` | 多鏡審查 |
| `bmad-qa-generate-e2e-tests` | QA 測試生成 |
| `bmad-walkthrough` | 變更導覽 |
| `bmad-loop` | 自動循環 |
| `bmad-help` | 下一步導航 |

### Retired names, kept for recognition only

Draw these dimmed and dashed. The label carries the arrow so a user reading an old diagram can find the new node.

| Retired skill | Label |
|---------------|-------|
| `bmad-checkpoint-preview` | ◇舊名 → 變更導覽 |
| `bmad-quick-dev` | ◇舊名 → 建置實作 |
| `bmad-dev-auto` | ◇舊名 → 自動迭代 |
| `bmad-create-architecture` | ◇舊名 → 架構脊柱 |
| `bmad-sprint-status` | ◇舊名 → Sprint 規劃（狀態） |
| `bmad-document-project` | ◇舊名 → 專案脈絡 |
| `bmad-generate-project-context` | ◇舊名 → 專案脈絡 |
| `bmad-market-research` / `bmad-domain-research` / `bmad-technical-research` | ◇舊名 → 深度偵查 |
| `bmad-editorial-review` and the three `bmad-review-*` skills | ◇舊名 → 多鏡審查 |
| `bmad-check-implementation-readiness` | ◇已移除 → Sprint 規劃閘門 |
| `bmad-create-story` | ◇已棄用（完整保留） |
| `bmad-dev-story` | ◇已棄用（完整保留） |
| `bmad-index-docs` / `bmad-shard-doc` | ◇已移除，無替代 |
| `bmad-agent-tech-writer` | ◇已退役，無直接替代 |

The last four rows have no destination arrow on purpose. `bmad-create-story` and `bmad-dev-story` are deprecated but still fully executable, so their label says so instead of pointing anywhere; the removed skills have no replacement, and drawing an arrow would invent one.
