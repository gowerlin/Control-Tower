---
name: control-tower-guide
description: "Interactive learning guide for BMad Control Tower v5.14.2, the file-driven work order orchestrator (Tower/Worker on Claude Code or Codex). Use for concepts, design rationale, or architecture: Orchestrator/Worker, work order lifecycle, three-layer architecture, cross-project coordination, runtime dispatch, governance guardrails, or why a ct-* command works the way it does. Triggers: 塔台學習, 塔台教學, CT 入門, ct-guide, 工單流程, 蜂王模式, 同構, context 衛生, 三層架構, Layer 1 寫入規則, frontmatter, 證據分道, affects_files, intervention_type, BAT, YOLO, 工單前綴, 完整工單 ID, 斷點 D, 塔台代決, auto-session, worker_auto_close, --set-role, 分頁標題, 範圍權杖, worktree, 合併工單, Codex, $ct-exec, plugin, marketplace, auto-update, ct@control-tower, Level 2, 落點檢查, Landing Zone, 跨專案協調, HANDOVER, ADVISORY, 除錯防線, 品質閘門, 三振出局, 範圍守護, BUG, PLAN, EXP, 研究型工單, Renew, 反序寫入, 歸檔, 遷移引擎, 知識管線, Playbook, 三區學習, FIELDGUIDE, *import, *onboard, 決策日誌, 機器可讀摘要, 塔台面板, 收斂, 結案判準, 不回歸閘. Explains with clickable SVG diagrams. Distinct from ct-help (operations manual) and the Tower's beginner mode."
---
<!-- control-tower-guide-version: 5.14.2 -->

# BMad Control Tower Interactive Learning Guide

An interactive visual guide to the Control Tower ecosystem, written against **BMad Control Tower v5.14.2**.
Generates clickable SVG workflow diagrams for drill-down exploration via `sendPrompt()`.

## Positioning

This skill is the **textbook**: it explains *why* Control Tower is designed the way it is. It does not run commands or create work orders.

| Resource | Form | Analogy | Purpose |
|----------|------|---------|---------|
| **control-tower-guide** (this) | Standalone skill | 教科書 | Concepts, design rationale, architecture, the v4 → v5 worldview change |
| `ct-help` | CT skill (`/ct-help`, `$ct-help`) | 操作手冊 + 概念速答 | Short, executable answers: command syntax, settings, prefixes, BAT/YOLO in brief |
| beginner-tutorial | **Tower built-in mode**, not a skill — enabled when `experience-level=beginner` | 駕訓班教練 | In-session coaching inside a live Tower: lesson gates, violation detection, graduation |

**Who to ask when**: to *do* something now (exact flag, setting value, which command) → `ct-help`;
to *understand* why it works that way, or how the pieces fit → this guide;
to be coached while actually running a Tower → set `experience-level` to `beginner` in that Tower.
For exact rules (regexes, flags, paths), this guide points to `ct-help` or the CT reference instead of restating them.

## Command prefixes

CT skills have two entry points for the same skill: `/` in Claude Code and `$` in Codex (e.g. `/ct-exec T0001` and `$ct-exec T0001`).
v5.14.0+: CT can also be installed as the plugin `ct` from the `control-tower` marketplace. Claude Code keeps `/ct-exec` (full form `/ct:ct-exec`);
Codex with the plugin must use `$ct:ct-exec` (`$ct-exec` does not reach a plugin skill). BAT dispatch to Codex works with both installs on
BAT `>= 0.7.2-pre.1` (BAT sends `$ct-exec` or `$ct:ct-exec` depending on how CT is installed on the Codex side; v5.14.2), and only with the
zip manual install on older BAT.
Mention this whenever the user brings up plugin, marketplace or Codex; the rule lives in CT `auto-session.md` § 依安裝方式的 skill 呼叫字串.
`*` commands (e.g. `*evolve`) are built into a running Tower session. When explaining a command, show both `/` and `$` forms.
This guide itself is packaged as a standalone skill (zip) and, from v5.14.0, also as the plugin `ct-guide`; its frontmatter `name` stays `control-tower-guide`.

## When to use

- User asks "what is Control Tower", "how does CT work", "why Orchestrator/Worker", "why is the Worker stateless"
- User asks about the work order lifecycle, status buckets, frontmatter vs body table, or evidence lanes
- User asks about the three-layer architecture, Layer 1 write rules, or the memory hierarchy isomorphism
- User asks how dispatch works: auto-session, YOLO breakpoints (incl. breakpoint D), the yolo Tower-question channel (Worker asks the Tower, Tower decides within scope), Claude Code vs Codex Workers
- User asks about BAT: what it is, how CT and BAT split the work, how the two Towers collaborate, a Worker tab's lifecycle, scoped tokens, query channels, which BAT version a feature needs
- User asks about worktree isolation (`isolation: worktree`), merge work orders, the three merge modes, breakpoint E, or the isolated-branch SHA evidence
- User asks why a guardrail exists: Landing Zone Check, summary authority rule, single authoritative definition, versioning
- User asks about cross-project coordination (five types incl. HANDOVER/ADVISORY), mono-repo, or multi-tower
- User asks about CT's relationship with BMad-Method (external bmad-guide), ECC, or mem0, or how the Tower finds bmad-guide (zip or plugin install, v5.14.1)
- User asks about BUG/PLAN/EXP, archive, migration, knowledge pipeline, Playbooks, or `*evolve`
- User asks how Claude Code Workflow fits CT (Skill / Playbook / Workflow split, `ct-evolve --workflow`, why there is no dispatch matching yet, the `workflow_integration` switch, Worker authorization, `*insights workflow`)
- User asks about Worker safety (scope guard, three-strikes, onion detector, duration alert, reverse-order closeout)
- User asks how to install CT: zip manual install vs the plugin marketplace (v5.14.0), migrating between them, which copy wins when both exist, auto-update, Codex + BAT
- User is upgrading from v4 and wants to know what changed

## How to respond

1. **Identify the topic category** and read the appropriate reference file(s) — only the ones needed
2. **Answer in Traditional Chinese (zh-TW)**
3. **Accompany with an interactive SVG diagram** using the Visualizer tool; read `references/diagrams.md` first
4. **Make nodes clickable** with `sendPrompt('介紹 [topic]')` for drill-down

## Response modes

### Learning mode (概念理解)
When user asks "what is X", "why does X work this way", "explain X":
- Lead with clear prose explanation of the concept and design rationale
- Follow with contextual diagram showing where X fits in the CT ecosystem
- Add tips, common misconceptions, and design trade-offs

### Practical mode (實戰查詢)
When user asks "how to get started", "what should I do next", "how to set up":
- Lead with concrete steps and command examples (`/` and `$` forms)
- Show quick-reference: prerequisites → actions → expected outcomes
- Follow with a focused diagram highlighting the relevant workflow
- For exact flags or setting syntax, point to `ct-help`

### Comparison mode (比較釐清)
When user asks "difference between X and Y", "when to use X vs Y":
- Lead with side-by-side comparison table
- Explain the design reasoning behind the distinction
- Show positioning diagram with clear boundaries

## Audience routing

### Beginner indicators
Keywords: 入門, 開始, 新手, 第一次, 什麼是, 怎麼用, 基礎
→ Start with `concepts.md` + `ecosystem.md`, progress to `work-order-lifecycle.md`

### Advanced indicators
Keywords: 三層, 同構, Layer 1, 跨專案, HANDOVER, mono-repo, 除錯, 品質閘門, 中斷, 學習萃取, 三區學習, insights, FIELDGUIDE, 三振, 範圍守護, 洋蔥, 歸檔, 遷移, auto_commit, BUG/PLAN/EXP 生命週期, Playbook, 知識管線, Renew, 反序寫入, 決策日誌, Tower State, 機器可讀摘要, `summary_version`, 決策日誌收斂, 結案判準, `closed_reason`, 未結 BUG 清理, PARTIAL 當下收尾, 塔台收尾補記, 不回歸閘, `customer_acceptance_gate`
→ Route to `three-layer-arch.md`, `advanced-patterns.md`, or `work-order-lifecycle.md`

### Workflow indicators
Keywords: Workflow, 三分法, `--workflow`, `[WF-CANDIDATE]`, `_workflows/`, 知識卡, 適配度, WFC, 工具型, 派工型, `.claude/workflows/`, `workflow_integration`, token 焦慮, Workflow 授權, 子代理記錄, `*insights workflow`, 預篩, 排除守門, G2
→ Route to `concepts.md` § Workflow：單張工單內的執行方式 (v5.11.0: § v5.11.0：回測沒過之後，先做便宜的部分); rules in `advanced-patterns.md` (ct-insights / ct-evolve); script location in `three-layer-arch.md`

### Runtime & governance indicators
Keywords: YOLO, auto-session, 斷點, 斷點 D, 塔台代決, 提問通道, `T#### 提問`, 回報 ID 缺前綴, 送出前比對, `worker_question_timeout`, CT_MODE, Codex, `$ct-exec`, `$ct:ct-exec`, 降級鏈, 成功判讀, 落點檢查, Landing Zone, repo identity, expect_missing, 摘要授權, 單一權威, 版本治理, 棄用條款, 合併護欄
→ Route to `runtime-dispatch.md` or `governance.md`

### Install indicators
Keywords: 安裝, 升級, plugin, marketplace, `ct@control-tower`, `ct-guide`, auto-update, 自動更新, `claude plugin`, `codex plugin`, zip 手動安裝, 遷移, 並存, `/ct:ct-exec`, `$ct:ct-exec`, `skill-backups`
→ Route to `governance.md` § plugin marketplace：另一種安裝方式（v5.14.0） and § 安裝流程（zip 手動安裝）; Layer 1 paths in `three-layer-arch.md`; the Codex + BAT rule (by BAT version, v5.14.2) in `bat-integration.md` § 誰負責 `/` 還是 `$`

### BAT indicators
Keywords: BAT, Better Agent Terminal, BAT 塔台, CT-T###, worker_auto_close, Worker 回收, `--set-role`, 分頁標題, 範圍權杖, Worker 分頁, `Forbidden`, `RECOVERY_PENDING`, `--isolation`, `CT_HOME`, `--worktree-status`, BAT MCP, `mcp__bat__*`, `blocked`, `blockedDetection`, `--wait-started`, `agentStarted`, Worker 啟動確認, exit `8`, `--ask`, `bat_wait_question`, `bat_list_questions`, `--answer`, `blockedReason: tower`, `blockedReason: input`, `blockedDetection: osc`, OSC 7501, codex 在等使用者, BAT 問答通道, BAT 版本, BAT 塔台面板, 面板讀取契約, 頁面空了, 大小預算, 400 KB, 512 KiB, `File too large`, 無法讀取, `critical`, 工單前綴, 完整工單 ID, `--source`, 標 Done, 一次關掉 Worker 分頁
→ Route to `bat-integration.md`

### Isolation & merge indicators
Keywords: worktree, `isolation`, 隔離派工, `ct/T####`, 合併工單, `merge_mode`, 機械合併, 衝突解決, 等價移植, 直接合併判準, 斷點 E, `validated_sha`, `head_sha`
→ Route to `work-order-lifecycle.md` § worktree 隔離與合併工單; BAT-side details to `bat-integration.md`; guardrail rationale to `governance.md` § 合併護欄

### Integration indicators
Keywords: BMad-Method, bmad-guide, ECC, mem0, Level, 整合, 增強, Playbook 引擎, *import, *onboard, 安全匯入, 研究文件, Level 2 偵測, plugin 版 bmad-guide, `bmad-guide@control-tower`, 偵測不到 bmad-guide
→ Route to `integration.md`

## Diagram conventions

- Tower/Orchestrator = `c-gold`, Worker/Execution = `c-blue`
- Work orders/Status = `c-teal`, Learning/Extract = `c-purple`
- Query/Utility = `c-gray`, BMad integration = `c-coral`
- Advanced patterns = `c-amber`, Three-layer = `c-green`
- All labels in Traditional Chinese (zh-TW); status enums, commands and file names stay verbatim
- Never draw the different "L1/L2/L3" numberings on one axis (see `diagrams.md`)
- Clickable nodes: `onclick="sendPrompt('介紹 ...')"`

## Reference file routing

| File | Read when |
|------|-----------|
| `references/concepts.md` | Core philosophy: memory hierarchy isomorphism, Orchestrator/Worker, stateless Worker, Queen Bee, Hard Boundaries, context hygiene, two-stage SoT, evidence lanes, multi-document types, hot/cold zones, knowledge pipeline, Workflow inside one work order (v5.10.0; v5.11.0 integration switch, Worker authorization, G2 status), granularity |
| `references/ecosystem.md` | 8 skills with `/` and `$` entry points (v5.14.0: Codex plugin install uses `$ct:`), `*`/`/`/`$` prefixes, Tower commands, SKILL.md-as-router, CT reference catalogue, data flow, capability levels, full settings table, v4 → v5 worldview change table |
| `references/work-order-lifecycle.md` | Work order file and frontmatter field map (incl. `isolation`, merge work order fields), core loop (manual/BAT/YOLO), status enum and buckets, ct-exec flow (Landing Zone Check, 4 phases, BAT notify, reporting with the full work order ID incl. prefix and the three-layer fix: templates, Worker pre-send check, Tower prefix tolerance; v5.13.1; v5.14.1: the Tower-side dispatch and close templates use `<工單 ID>` too), commit policy, worktree isolation and merge work orders (why isolate, Worker in a worktree, SHA evidence, three merge modes, direct-merge criteria, breakpoint E), BUG/PLAN/EXP state machines, BUG closeout criteria and `closed_reason` and the open-BUG review prompt (v5.13.0), closing a `PARTIAL` at the Tower's ruling (v5.13.0), the optional customer-acceptance no-regression gate (v5.13.0), research work orders, the yolo Tower-question channel, Renew |
| `references/three-layer-arch.md` | Core/Global/Project layers, Layer 1 write rules (v5.14.0: plugin install paths are Layer 1 too), merge rules, four-level config override, learning routing, two kinds of "three layers", Tower private state files, `_decision-log.md` (v5.13.0: format rules BAT relies on, condensation), `_archive/`, BUG/PLAN index format, Tower State sections and its machine-readable summary frontmatter (v5.13.0) |
| `references/advanced-patterns.md` | Five cross-project coordination types, ID prefixes, multi-tower and GP namespaces, `*pause`/`*resume`, mono-repo, debug tiers, quality gates, Worker's four safeguards, beginner mode, ct-insights, ct-evolve, FIELDGUIDE, archive operations, migration, Tower auto-commit |
| `references/integration.md` | Level 1 ECC, Level 2 external bmad-guide (v5.14.1: where the Tower looks — manual install first, then the Claude and Codex plugin installs; read-only; a one-time notice when it is installed but unreadable), Level 3 mem0 REST, Codex integration, Playbook engine, research/spec files, `*import`, `*onboard`, environment detection |
| `references/runtime-dispatch.md` | Terminal-independent dispatch: auto-session's four levels, how `CT_MODE` reaches the Worker, YOLO breakpoints (A/B/C/D/E; v5.13.1: a report ID missing its prefix is not breakpoint A unless ambiguous), the yolo Tower-question channel in brief, agent neutrality, success signals, fallback chain, Worker-side notify fallback |
| `references/bat-integration.md` | Everything BAT: what BAT is and why CT integrates it, the BAT-defines/CT-calls split, how the BAT Tower and the CT Tower collaborate (CT-T011/T013/T014/T015/T016), a Worker tab's lifecycle, the two env-var groups, `--workspace` vs `--cwd`, who builds `/` or `$` (v5.14.0: a Codex plugin install could not take BAT dispatch; v5.14.1: dispatch templates take `<工單 ID>`; v5.14.2: on BAT `>= 0.7.2-pre.1` BAT picks `$ct-exec` or `$ct:ct-exec`, so it can, and why BAT decides rather than the Tower), 塔台分頁角色宣告 (`--set-role`), worktree isolated dispatch (`--isolation worktree`, `CT_HOME`, exit `7`), `BAT_HELPER_NODE`, scoped token and tab roles (`Forbidden`／`RECOVERY_PENDING`, naming tabs by title), Worker notify (v5.13.1: why `--source` must be the full work order ID — BAT matches the Worker tab by it), closing the Worker tab (worker_auto_close, `--worktree keep`; v5.12.0: closing the old tab before a re-dispatch), query channels (`--worktree-status`, BAT MCP), breakpoint D (`blocked`), the BAT Tower panel read contract (why a page goes empty, the 400 KB budget, how to measure; v5.13.0; v5.13.1: BAT `>= 0.7.1-pre.9` shows "cannot read" and counts `critical` as High, and why the budget stays), CT ↔ BAT version table |
| `references/governance.md` | Design rationale of the guardrails: Landing Zone Check (identity ≠ path; C-0 inside a worktree), summary authority rule, single authoritative definition, Layer 1 write mechanism and install flow, the plugin marketplace as a second install method (v5.14.0: what it is, relation to the zip, which copy wins when both exist, auto-update, Codex + BAT (v5.14.2: by BAT version); v5.14.1: the same marketplace also offers `bmad-guide`), versioning, merge guardrails, deprecation clauses |
| `references/diagrams.md` | Before generating any SVG visualization (17 diagram types, incl. BAT/YOLO dispatch loop, Landing Zone Check decision tree, frontmatter SoT/drift, EXP state machine, BAT tab relationship and lifecycle, isolated work order merge) |
