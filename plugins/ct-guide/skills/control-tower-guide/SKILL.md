---
name: control-tower-guide
description: "Learning guide for BMad Control Tower v6.0.0 stable (replaces 5.15.0), the file-driven work order orchestrator. For concepts, rationale, architecture: Orchestrator/Worker, work order lifecycle, three-layer architecture, cross-project coordination, runtime dispatch, governance guardrails, why ct-* commands work as they do, or v6 methodology adapters. Triggers: 塔台學習, 正式版, CT 入門, ct-guide, 工單流程, 蜂王模式, 同構, context 衛生, 三層架構, Layer 1 寫入規則, frontmatter, 證據分道, affects_files, intervention_type, BAT, YOLO, 工單前綴, 完整工單 ID, 斷點 D, 塔台代決, auto-session, worker_auto_close, --set-role, 分頁標題, 範圍權杖, worktree, 合併工單, Codex, $ct-exec, plugin, marketplace, auto-update, ct@control-tower, 落點檢查, Landing Zone, 跨專案協調, HANDOVER, ADVISORY, 除錯防線, 品質閘門, 三振出局, 範圍守護, BUG, PLAN, EXP, 研究型工單, Renew, 反序寫入, 歸檔, 遷移引擎, 知識管線, Playbook, 三區學習, FIELDGUIDE, *import, *onboard, 決策日誌, 機器可讀摘要, 塔台面板, 收斂, 結案判準, 不回歸閘, 方法論轉接, pstack, 疊加, 引入方式, 不必引入, 選用, 共存, mattpocock, 預設開啟. Clickable SVG diagrams. Not ct-help or beginner mode."
---
<!-- control-tower-guide-version: 6.0.0 -->

# BMad Control Tower Interactive Learning Guide

An interactive visual guide to the Control Tower ecosystem, written against **BMad Control Tower v6.0.0（正式版，取代 5.15.0 成為穩定版）**.
6.0.0 is the first stable release of the v6 line and replaces 5.15.0 as the stable line (downloads in the GitHub Release `ct-v6.0.0`, Latest; 5.15.0 stays downloadable as the previous stable). Everything listed below from pre.1 through rc.1 shipped first as a pre-release (packaged only, alongside the stable line of the time); since 6.0.0 it is all part of the stable line.
v6.0.0 keeps the 5.x behavior when no `methodology*` setting is used, with one deliberate exception (since beta.1): BUG／PLAN／EXP are now on by default
(a setting that explicitly says `false` stays off). The chapters carried over from the stable guide (5.15.0) still hold; the three places that state the old default are updated.
beta.2 is the "which methodologies to adopt" release: a methodology is not something CT must adopt — BMAD is adopted (built in, default), pstack is optional,
Superpowers is not recommended (coexistence safeguards only), mattpocock/skills is an optional option-③ example with unproven quality benefit.
beta.3 is the status-hygiene and BAT Tower panel read contract release (BUG closeout criteria and `closed_reason`, closing a `PARTIAL` at the Tower's ruling,
the open-BUG review prompt, the optional customer-acceptance no-regression gate, decision-log format and condensation, the 400 KB hot-file budget);
the same batch of rules is in stable 5.13.0, so it is taught in the main chapters, and the Beta chapter only points to them.
beta.4 is the full-work-order-ID and BAT panel read contract (BAT `0.7.1-pre.9`) release (Workers send the full work order ID, prefix included, in notify, `--ask` and `--source`,
and check it against the frontmatter `id` before sending; the Tower tolerates a missing prefix; the panel contract follows pre.9's "cannot read" message and `critical` handling);
the same batch of rules is in stable 5.13.1, so it is also taught in the main chapters, and the Beta chapter only points to them.
beta.5 is the plugin-install-readiness release (the plugin marketplace text, plugin install paths as Layer 1, the call string per install method, Codex + BAT staying on the zip, which beta.6 changes to "by BAT version");
the same batch of rules is in stable 5.14.0, so it is taught in the main chapters, and the Beta chapter only points to them.
Pre-releases (beta, rc) ship **no plugin**: the marketplace lists stable releases only, so a beta or RC is installed from the zip, and plugin commands run in such a setup install the stable release next to it; 6.0.0 is on the marketplace.
The one v6-only difference was that § 路徑解析 counted both `~/.claude/plugins/` and `${CLAUDE_CONFIG_DIR}/plugins/` as Layer 1 (unverified); since beta.8 it is one path, as in stable 5.14.4.
beta.6 ports stable 5.14.1 and 5.14.2 (Tower-side templates use `<工單 ID>`, the marketplace also offers `bmad-guide`, Codex + BAT by BAT version,
the `AGENTS.md` project-context wording, the plugin-cache note); those rules are in stable 5.14.1／5.14.2, so they are taught in the main chapters.
It also lets methodology adapters find a methodology skill installed as a plugin (a probe resolves a skill root, a plugin probe may set `skill_root`,
the built-in `bmad.yaml` adds two plugin probes after the manual one, a one-time notice when a methodology is installed but unreadable): that part is v6-only
and is in the Beta chapter's § beta.6. The plugin probes were verified on a real machine before beta.8. The Beta still ships no CT plugin, but a beta user may install
just `bmad-guide` from the stable marketplace (it does not follow the CT version), and beta.6 finds it.
beta.7 ports stable 5.14.3: one Tower for several nested independent repos (work orders in the parent repo, the Worker runs there, sub-repos commit with `git -C`, no worktree isolation).
It is documentation only and the same text is in stable 5.14.3, so it is taught in `advanced-patterns.md` § 巢狀的獨立 repo; the Beta chapter only points to it.
beta.8 ports stable 5.14.4: the Tower looks for a methodology skill in its own runtime first (manual install, then plugin) and reads the other runtime's install only as a file source,
noting it once; the Claude plugin root is one path. Those rules are taught in `integration.md` § 偵測與降級 and `three-layer-arch.md`. The optional probe field `runtime`
and the reworked `bmad.yaml` (0.2.1) and `ct-adapter-pstack` (0.2.6) probes are v6-only and are in the Beta chapter's § beta.8.
beta.9 ports stable 5.15.0: a yolo Worker that asks several questions wakes the Tower once per batch (questions 1 … N-1 with `--ask --no-pty-write`, the last with `--submit`),
the Tower answers repeated notifications with a minimal check and never reminds the user twice, each question's 120 s lease counts on its own, and breakpoint A reads a notification by its tail.
Those rules are the same as stable 5.15.0, so they are taught in `work-order-lifecycle.md` (the yolo Tower-question channel) and `runtime-dispatch.md`; the Beta chapter's § beta.9 only points to them.
beta.10 is v6-only (stable 5.15.0 does not have it): session usage statistics (`*insights sessions` in `ct-insights`, the Worker's `session_ids`, the Tower's own session id,
the closeout backfill and snapshot; Tower usage is listed apart and never allocated), session evidence entering the learning flow (`ct-evolve --facts-from`, the existing confidence table, withdrawal),
and external enhancement governance (one learning mechanism; ECC Level 1 retired; mem0 Level 3 kept but enabled only when the project's local rules record an exception under the user-level plugin rule),
plus spec fixes (the Codex skill scanner recursion is verified, removing manually installed skills, leading spaces in helper output). Those are taught in the Beta chapter's § beta.10 sections
and in the main chapters that point to them (`advanced-patterns.md`, `work-order-lifecycle.md`, `integration.md`, `three-layer-arch.md`, `bat-integration.md`).
beta.11 is v6-only too: mid-flight addenda — while a Worker is still `IN_PROGRESS` the Tower writes `## 塔台補充（執行中 #N）` (not a Renew), and the Worker (`ct-exec`, and `ct-done` before its report)
checks the section headings at three fixed points (before validation, before the product commit, before the report) and reads only new sections; an optional cross-session nudge to the Tower's own Worker;
plus small items (`ct-help` explains `*insights sessions` and `--facts-from`, a second reason not to put `--settings` in BAT launch arguments, BAT `>= 0.7.3-pre.8` holding Worker notifications).
Those are taught in the Beta chapter's § beta.11：Worker 執行中接收塔台補充 and in `work-order-lifecycle.md`, `advanced-patterns.md`, `bat-integration.md`.
beta.12 is v6-only as well: the tool-list suggestion `*insights tools` (in `ct-insights`) reads the local Claude Code session logs and lists the skills, plugins, MCP servers, agent types and built-in tools
that are always loaded but rarely or never used, grouped by work order type, each with the layer to change it at (project, user, claude.ai account) and the key or interface;
it only suggests and never edits a setting, and core built-in tools (`Skill`, `Bash`, `Read`, …) are always kept. `*insights sessions` also counts slash commands and agent types now (snapshot `0.2`),
and packaging checks that no `SKILL.md` description contains angle brackets. Those are taught in the Beta chapter's § beta.12：工具清單建議 and in `advanced-patterns.md` (ct-insights).
rc.1 is the release candidate: the beta feedback period is over, features are frozen and only fixes land (no new feature, setting or command); if nothing needs fixing it becomes 6.0.0.
It fixes the wording of the Worker's addenda check points (`ct-exec` runs node 1 as the first step of Phase 3, `ct-done` states its check first), completes the `*insights tools` JSON field list
in `analysis-rules.md`, and corrects this guide's `ct-adapter-pstack` version to 0.2.6. Taught in the Beta chapter's § rc.1：正式版候選（只修錯）.
6.0.0 is the stable release: no feature or rule change from rc.1, only the version and labels (RC → stable); the CT plugin `ct` and this guide's plugin `ct-guide` are on the marketplace at 6.0.0. Taught in § 6.0.0：納入正式版.
What v6 adds (methodology adapters, the three adoption modes and per-methodology positioning, the `_tower-state.md` summary, the fixes from isolated trials P1／P1b／P3) was taught during the pre-release in one Beta chapter,
`references/preview-methodology.md`; since 6.0.0 that chapter is kept as the pre-release history (design rationale, test evidence, what each pre-release changed; file name and section anchors unchanged), and the main chapters carry the short version with links: methodology adapters in `integration.md` § 方法論轉接（v6.0.0+）, the Worker side in `work-order-lifecycle.md` § 方法論（v6.0.0+）.
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
v5.14.0+ (v6: the same text since v6.0.0-beta.5; on the marketplace since 6.0.0, pre-releases ship no plugin — zip only): CT can also be installed as the plugin `ct` from the `control-tower` marketplace. Claude Code keeps `/ct-exec` (full form `/ct:ct-exec`);
Codex with the plugin must use `$ct:ct-exec` (`$ct-exec` does not reach a plugin skill). BAT dispatch to Codex works with both installs on
BAT `>= 0.7.2-pre.1` (BAT sends `$ct-exec` or `$ct:ct-exec` depending on how CT is installed on the Codex side; v5.14.2, v6 since v6.0.0-beta.6), and only with the
zip manual install on older BAT.
Mention this whenever the user brings up plugin, marketplace or Codex; the rule lives in CT `auto-session.md` § 依安裝方式的 skill 呼叫字串.
`*` commands (e.g. `*evolve`) are built into a running Tower session. When explaining a command, show both `/` and `$` forms.
This guide itself is packaged as a standalone skill (zip) and, from v5.14.0 (stable only, 6.0.0 included; pre-release guides ship as a zip only), also as the plugin `ct-guide`; its frontmatter `name` stays `control-tower-guide`.

## When to use

- User asks "what is Control Tower", "how does CT work", "why Orchestrator/Worker", "why is the Worker stateless"
- User asks about the work order lifecycle, status buckets, frontmatter vs body table, or evidence lanes
- User asks about the three-layer architecture, Layer 1 write rules, or the memory hierarchy isomorphism
- User asks how dispatch works: auto-session, YOLO breakpoints (incl. breakpoint D), the yolo Tower-question channel (Worker asks the Tower, Tower decides within scope), Claude Code vs Codex Workers
- User asks about BAT: what it is, how CT and BAT split the work, how the two Towers collaborate, a Worker tab's lifecycle, scoped tokens, query channels, which BAT version a feature needs
- User asks about worktree isolation (`isolation: worktree`), merge work orders, the three merge modes, breakpoint E, or the isolated-branch SHA evidence
- User asks why a guardrail exists: Landing Zone Check, summary authority rule, single authoritative definition, versioning
- User asks about cross-project coordination (five types incl. HANDOVER/ADVISORY), mono-repo, nested independent repos under one Tower (v5.14.3; v6 since v6.0.0-beta.7), or multi-tower
- User asks about CT's relationship with BMad-Method (external bmad-guide), ECC (Level 1 retired in v6.0.0-beta.10), or mem0 (Level 3; v6.0.0-beta.10 needs a local-rules exception), or about external enhancement plugin governance (one learning mechanism), or how the Tower finds bmad-guide (zip or plugin install; v5.14.1, v6 through adapter probes since v6.0.0-beta.6)
- User asks about BUG/PLAN/EXP, archive, migration, knowledge pipeline, Playbooks, or `*evolve`
- User asks how Claude Code Workflow fits CT (Skill / Playbook / Workflow split, `ct-evolve --workflow`, why there is no dispatch matching yet, the `workflow_integration` switch, Worker authorization, `*insights workflow`)
- User asks about Worker safety (scope guard, three-strikes, onion detector, duration alert, reverse-order closeout)
- User asks how to install CT: zip manual install vs the plugin marketplace (v5.14.0; v6 since 6.0.0; pre-releases ship no plugin), migrating between them, which copy wins when both exist, auto-update, Codex + BAT
- User is upgrading from v4 and wants to know what changed
- User asks about v6 (6.0.0, stable; formerly the beta／RC pre-releases): methodology adapters (BMAD, pstack, …), whether a methodology must be adopted at all and each one's positioning (BMAD adopted, pstack optional, Superpowers not recommended／coexistence only, mattpocock/skills as an option-③ example), using mattpocock/skills in a CT project, swapping or layering methodologies, the three adoption modes (full install／skills only／partial reference) and which are tested (③ tested in P3, ② not), the `methodology*` settings, the `### 方法論邊界` section, SessionStart injection, Codex hook trust, dual injection, the `_tower-state.md` machine-readable summary, BUG／PLAN／EXP on by default, env detection listing names only (bash `compgen -e`, one variable per command), `CLAUDE_CONFIG_DIR`／`CODEX_HOME`, what the isolated trials (P1／P1b／P3) changed, what beta.3 changed (status hygiene and the BAT panel read contract — the same rules as stable 5.13.0, taught in the main chapters), what beta.4 changed (the full work order ID in reports and the BAT panel contract for `0.7.1-pre.9` — the same rules as stable 5.13.1, taught in the main chapters), what beta.5 changed (plugin-install readiness — the same rules as stable 5.14.0, taught in the main chapters; the Beta itself ships no plugin), or what beta.6 changed (the ported 5.14.1／5.14.2 rules, taught in the main chapters; adapter plugin probes and `skill_root`, v6-only), or what beta.7 changed (the ported 5.14.3 nested-independent-repos layout, taught in `advanced-patterns.md`), or what beta.8 changed (the ported 5.14.4 per-runtime search order and single Claude plugin root, taught in `integration.md`; the probe field `runtime`, v6-only), or what beta.9 changed (the ported 5.15.0 question batching, minimal check for repeated notifications, per-question lease and tail reading of notifications, taught in `work-order-lifecycle.md` and `runtime-dispatch.md`), or what beta.10 changed (v6-only: session usage statistics, session evidence via `ct-evolve --facts-from`, ECC Level 1 retired, mem0 Level 3 only with a local-rules exception, the Codex scanner and skill-removal fixes), or what beta.11 changed (v6-only: mid-flight addenda `## 塔台補充（執行中 #N）` and the Worker's three check points, `ct-done` checking before its report, the optional nudge to the Tower's own Worker, the BAT notes), or what beta.12 changed (v6-only: the tool-list suggestion `*insights tools` — suggest only, each item with its layer, core built-in tools kept; `skills_invoked` counting slash commands, `agents_invoked`, snapshot `0.2`; the angle-bracket packaging check), or what rc.1 is (the release candidate: features frozen, fixes only; what it fixed), or what 6.0.0 changed (the stable release; no change from rc.1 beyond version and labels, the plugin on the marketplace) — say that since 6.0.0 these are part of the stable line (which replaces 5.15.0), and that the Beta／RC labels in the Beta chapter describe the pre-release period

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
Keywords: 三層, 同構, Layer 1, 跨專案, HANDOVER, mono-repo, 巢狀 repo, 多 repo 塔台, `git -C`, 除錯, 品質閘門, 中斷, 學習萃取, 三區學習, insights, FIELDGUIDE, 三振, 範圍守護, 洋蔥, 歸檔, 遷移, auto_commit, BUG/PLAN/EXP 生命週期, Playbook, 知識管線, Renew, 反序寫入, 決策日誌, Tower State, 機器可讀摘要, `summary_version`, 決策日誌收斂, 結案判準, `closed_reason`, 未結 BUG 清理, PARTIAL 當下收尾, 塔台收尾補記, 不回歸閘, `customer_acceptance_gate`
→ Route to `three-layer-arch.md`, `advanced-patterns.md`, or `work-order-lifecycle.md`

### Workflow indicators
Keywords: Workflow, 三分法, `--workflow`, `[WF-CANDIDATE]`, `_workflows/`, 知識卡, 適配度, WFC, 工具型, 派工型, `.claude/workflows/`, `workflow_integration`, token 焦慮, Workflow 授權, 子代理記錄, `*insights workflow`, 預篩, 排除守門, G2
→ Route to `concepts.md` § Workflow：單張工單內的執行方式 (v5.11.0: § v5.11.0：回測沒過之後，先做便宜的部分); rules in `advanced-patterns.md` (ct-insights / ct-evolve); script location in `three-layer-arch.md`

### Runtime & governance indicators
Keywords: YOLO, auto-session, 斷點, 斷點 D, 塔台代決, 提問通道, `T#### 提問`, 一批提問只叫醒一次, `--no-pty-write`, 重複通知, 回報 ID 缺前綴, 送出前比對, `worker_question_timeout`, CT_MODE, Codex, `$ct-exec`, `$ct:ct-exec`, 降級鏈, 成功判讀, 落點檢查, Landing Zone, repo identity, expect_missing, 摘要授權, 單一權威, 版本治理, 棄用條款, 合併護欄
→ Route to `runtime-dispatch.md` or `governance.md`

### Install indicators
Keywords: 安裝, 升級, plugin, marketplace, `ct@control-tower`, `ct-guide`, auto-update, 自動更新, `claude plugin`, `codex plugin`, zip 手動安裝, 遷移, 並存, `/ct:ct-exec`, `$ct:ct-exec`, `skill-backups`
→ Route to `governance.md` § plugin marketplace：另一種安裝方式（v5.14.0／v6.0.0-beta.5 條文；v6 自 6.0.0 起上架） and § 安裝流程（zip 手動安裝）; Layer 1 paths in `three-layer-arch.md`; the Codex + BAT rule (by BAT version, v5.14.2／v6.0.0-beta.6) in `bat-integration.md` § 誰負責 `/` 還是 `$`. For a v6 beta or RC user (pre-release), say first that pre-releases ship no CT plugin and must not be installed from the marketplace (installing only `bmad-guide` from it is fine); a 6.0.0 user may use the marketplace

### BAT indicators
Keywords: BAT, Better Agent Terminal, BAT 塔台, CT-T###, worker_auto_close, Worker 回收, `--set-role`, 分頁標題, 範圍權杖, Worker 分頁, `Forbidden`, `RECOVERY_PENDING`, `--isolation`, `CT_HOME`, `--worktree-status`, BAT MCP, `mcp__bat__*`, `blocked`, `blockedDetection`, `--wait-started`, `agentStarted`, Worker 啟動確認, exit `8`, `--ask`, `bat_wait_question`, `bat_list_questions`, `--answer`, `blockedReason: tower`, `blockedReason: input`, `blockedDetection: osc`, OSC 7501, codex 在等使用者, BAT 問答通道, BAT 版本, BAT 塔台面板, 面板讀取契約, 頁面空了, 大小預算, 400 KB, 512 KiB, `File too large`, 無法讀取, `critical`, 工單前綴, 完整工單 ID, `--source`, 標 Done, 一次關掉 Worker 分頁
→ Route to `bat-integration.md`

### Isolation & merge indicators
Keywords: worktree, `isolation`, 隔離派工, `ct/T####`, 合併工單, `merge_mode`, 機械合併, 衝突解決, 等價移植, 直接合併判準, 斷點 E, `validated_sha`, `head_sha`
→ Route to `work-order-lifecycle.md` § worktree 隔離與合併工單; BAT-side details to `bat-integration.md`; guardrail rationale to `governance.md` § 合併護欄

### v6 indicators (v6.0.0 stable; the Beta chapter keeps the pre-release history)
Keywords: v6, 6.0.0, 正式版, Beta, RC, rc.1, 正式版候選, 功能凍結, beta.1, beta.2, beta.3, beta.4, beta.5, beta.6, beta.7, beta.8, beta.9, beta.10, beta.11, beta.12, 工具清單建議, `*insights tools`, 載入但沒用到, `skillOverrides`, `enabledPlugins`, `TOOLS_CORE_BUILTIN`, 核心內建工具, `agents_invoked`, 執行中補充, 塔台補充（執行中, Tower Addenda Check, 節點檢查, 重讀工單, 檔案已變更, 待送通知, session 用量, token 用量, `*insights sessions`, `session_ids`, `CLAUDE_CODE_SESSION_ID`, 塔台 session id, 收單快照, `_insights/`, `ct-session-stats.py`, 塔台用量不攤分, 候選事實, session 證據, `--facts-from`, `ct-session-fact`, 撤回候選, ECC Level 1 退場, 外部增強外掛治理, `--settings`, beta 沒有 plugin, `skill_root`, plugin probe, adapter 偵測 plugin, probe `runtime`, 依 runtime, 只當讀檔來源, 預覽, 狀態衛生, 同批規則, 方法論不是一定要引入, 不必引入, 要不要引入, 各家定位, 引入, 選用, 不建議引入, 共存, 共存防護, 結論閘門, 效益未實證, mattpocock, mattpocock/skills, `mp-`, `VENDOR.md`, `policy.allow_implicit_invocation`, ③ 已實測, P3, T0327, `compgen -e`, 一個變數一個指令, 方法論轉接, methodology adapter, adapter, 主方法論, 抽換, 分層疊加, 疊加, 5 層, `methodology`, `methodology_<layer>`, `inherit`, 這張用 X 做, 工單覆寫, `resolved_from`, pstack, `ct-adapter-pstack`, `ct-adapter-<id>`, `adapter_version`, `tested_version`, `bmad.yaml`, `_adapters/`, guide skill, 引入方式, 完整安裝, 只引用 skill, skills-only, 部分參考, 本地副本, `disable-model-invocation`, 方法論邊界, 邊界段, 【只允許】, 【不使用】, `methodology_guard`, SessionStart 注入, `methodology_ambient`, 方法論執行紀錄, compact 後重讀, hook 信任, Hooks need review, 雙注入, Superpowers, HARD-GATE, `always_on_tokens`, 未量測, `subagent_writes`, 背景子代理, 子 skill, 交付層, scratchpad 退路, 暫存目錄, 塔台語言, 預設開啟, `enable_bug_tracking`, `_bug-tracker.md`, `_backlog.md`, 待辦池, 臭蟲分頁, 只列名稱, 環境偵測, `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, 隔離設定目錄, 隔離試用, P1, P1b, T0314, T0315, V1, V2a, V2b, 已知未驗, 機器可讀摘要, `summary_version`, BAT 總覽, 預發行 Release
→ For what a v6 feature is and how it is used, start from the main chapter (`integration.md` § 方法論轉接（v6.0.0+）, `work-order-lifecycle.md` § 方法論（v6.0.0+）, `advanced-patterns.md`), then `preview-methodology.md` for the design rationale, test evidence and pre-release history; say that since 6.0.0 these are part of the stable line (6.0.0 replaces 5.15.0), and that the chapter's Beta／RC labels describe the pre-release period.
beta.3's status-hygiene and BAT-panel rules are the same as stable 5.13.0: teach them from the main chapters (`work-order-lifecycle.md`, `three-layer-arch.md`, `bat-integration.md` § BAT 塔台面板讀取契約, `ecosystem.md` § 設定系統); the Beta chapter's § beta.3：狀態衛生與 BAT 塔台面板讀取契約 only maps them and adds the Beta-only notes.
beta.4's full-work-order-ID and BAT-panel (pre.9) rules are the same as stable 5.13.1: teach them from the main chapters (`work-order-lifecycle.md` § 回報與通知用完整工單 ID, `runtime-dispatch.md` § 斷點, `bat-integration.md` § Worker 執行與通知 and § BAT 塔台面板讀取契約, `three-layer-arch.md` § `_bug-tracker.md` 和 `_backlog.md`); the Beta chapter's § beta.4：通知用完整工單 ID 與 BAT 塔台面板讀取契約 only maps them and adds the Beta-only notes.
beta.5's plugin-install-readiness rules are the same as stable 5.14.0: teach them from the main chapters (`governance.md` § plugin marketplace：另一種安裝方式, `three-layer-arch.md` § plugin 安裝路徑也是 Layer 1, `bat-integration.md` § 誰負責 `/` 還是 `$`, `ecosystem.md` § 三軌前綴：`*`、`/`、`$`); the Beta chapter's § beta.5：plugin 安裝就緒 only maps them and adds the Beta-only notes (no plugin for the Beta, both plugin paths count).
beta.6's ported rules are the same as stable 5.14.1／5.14.2: teach them from the main chapters (`work-order-lifecycle.md` § 回報與通知用完整工單 ID, `bat-integration.md` § 誰負責 `/` 還是 `$`, `governance.md` § plugin marketplace：另一種安裝方式, `integration.md` § 偵測與降級); the adapter plugin probes and `skill_root` are v6-only and live in the Beta chapter's § beta.6：移植 5.14.1／5.14.2、adapter 偵測 plugin, which also maps the ported rules.
beta.7's nested-independent-repos layout is the same text as stable 5.14.3: teach it from `advanced-patterns.md` § 巢狀的獨立 repo (and `work-order-lifecycle.md` for `repo`); the Beta chapter's § beta.7：移植 5.14.3（巢狀的獨立 repo） only points to it.
beta.8's ported search order and single Claude plugin root are the same rules as stable 5.14.4: teach them from `integration.md` § 偵測與降級 and `three-layer-arch.md` § plugin 安裝路徑也是 Layer 1; the probe field `runtime` and the `bmad.yaml`／`ct-adapter-pstack` probe changes are v6-only and live in the Beta chapter's § beta.8：移植 5.14.4、probe 依 runtime.
beta.9's ported question-batching rules are the same as stable 5.15.0: teach them from `work-order-lifecycle.md` (〈一批只叫醒塔台一次〉 and the BAT channel), `runtime-dispatch.md` § 斷點 and `bat-integration.md`; the Beta chapter's § beta.9：移植 5.15.0（一批提問只叫醒塔台一次） only points to them.
beta.10 is v6-only: teach session usage from § beta.10：session 用量統計（PLAN-004 ⑥）, session evidence from § beta.10：session 證據怎麼進學習流程（PLAN-004 ⑦）, and ECC Level 1 retirement plus the mem0 Level 3 condition from § beta.10：ECC Level 1 退場 and `integration.md` § Level 3 › 啟用條件; the main chapters (`advanced-patterns.md`, `work-order-lifecycle.md`, `three-layer-arch.md`, `governance.md`) carry the short versions.
beta.11 is v6-only: teach mid-flight addenda from § beta.11：Worker 執行中接收塔台補充 (what was verified with isolated `claude -p` and what waits for real dispatch); the main chapters (`work-order-lifecycle.md` § Worker Renew 機制 and the `ct-done` paragraph, `advanced-patterns.md` § 跨 session 通知對方塔台, `bat-integration.md` § Worker 執行與通知 and the `--settings` paragraph) carry the short versions.
beta.12 is v6-only: teach the tool-list suggestion from § beta.12：工具清單建議 (what it reads, suggest only, each item's layer, why core built-in tools are kept, which levers were measured and which are not); `advanced-patterns.md` (ct-insights) carries the short version.
rc.1 is the release candidate: teach what an RC means and what it fixed from § rc.1：正式版候選（只修錯）; the fixes change wording only (the three check points and their meaning are unchanged).
6.0.0 is the stable release: teach it from § 6.0.0：納入正式版 (no change from rc.1 beyond version and labels; upgrading from 5.15.0: CT `CHANGELOG.md` [6.0.0] and install guide § 2.65).
Which methodologies to adopt (and why Superpowers is not recommended) → § 方法論不是一定要引入：各家定位; mattpocock/skills → § 在 CT 專案使用 mattpocock/skills; P3 findings → § 實測 P3. Never present a methodology as recommended beyond its positioning there.
For the old Level 2 (external bmad-guide) still read `integration.md` § Level 2, then the Beta chapter's § 從 Level 2 到方法論轉接.
For env detection also read `bat-integration.md` § 兩組環境變數，兩個角色 (listing names only is the same as in 5.12.7+; the bash `compgen -e` form and one-variable-per-command are v6-only, not in 5.x).

### Integration indicators
Keywords: BMad-Method, bmad-guide, ECC, ECC 退場, 外部增強外掛治理, mem0, Level, 整合, 增強, Playbook 引擎, *import, *onboard, 安全匯入, 研究文件, Level 2 偵測, plugin 版 bmad-guide, `bmad-guide@control-tower`, 偵測不到 bmad-guide, 讀到另一個 runtime 的 bmad-guide, `CLAUDE_CONFIG_DIR`
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
| `references/ecosystem.md` | 8 skills with `/` and `$` entry points (v5.14.0／v6.0.0-beta.5 text: Codex plugin install uses `$ct:`; on the marketplace since 6.0.0, pre-releases ship no plugin), `*`/`/`/`$` prefixes, Tower commands, SKILL.md-as-router, CT reference catalogue, data flow, capability levels, full settings table, v4 → v5 worldview change table |
| `references/work-order-lifecycle.md` | Work order file and frontmatter field map (incl. `isolation`, merge work order fields), core loop (manual/BAT/YOLO), status enum and buckets, ct-exec flow (Landing Zone Check, 4 phases, BAT notify, reporting with the full work order ID incl. prefix and the three-layer fix: templates, Worker pre-send check, Tower prefix tolerance; v5.13.1／v6.0.0-beta.4; v5.14.1／v6.0.0-beta.6: the Tower-side dispatch and close templates use `<工單 ID>` too), commit policy, worktree isolation and merge work orders (why isolate, Worker in a worktree, SHA evidence, three merge modes, direct-merge criteria, breakpoint E), BUG/PLAN/EXP state machines, BUG closeout criteria and `closed_reason` and the open-BUG review prompt (v5.13.0／v6.0.0-beta.3), closing a `PARTIAL` at the Tower's ruling (v5.13.0／v6.0.0-beta.3), the optional customer-acceptance no-regression gate (v5.13.0／v6.0.0-beta.3), research work orders, the yolo Tower-question channel (v5.15.0／v6.0.0-beta.9: a batch of questions wakes the Tower once; repeated notifications get a minimal check and no second reminder to the user), Renew |
| `references/three-layer-arch.md` | Core/Global/Project layers, Layer 1 write rules (v5.14.0／v6.0.0-beta.5 text: plugin install paths are Layer 1 too; v5.14.4／v6.0.0-beta.8: the Claude plugin root is one path, verified; beta.5～beta.7 counted two), merge rules, four-level config override, learning routing, two kinds of "three layers", Tower private state files, `_decision-log.md` (v5.13.0／v6.0.0-beta.3: format rules BAT relies on, condensation), `_archive/`, BUG/PLAN index format, Tower State sections and its machine-readable summary frontmatter (v5.13.0; v6 since 6.0.0-pre.1) |
| `references/advanced-patterns.md` | Five cross-project coordination types, ID prefixes, multi-tower and GP namespaces, `*pause`/`*resume`, mono-repo, nested independent repos (v5.14.3; v6 since v6.0.0-beta.7: why work orders end up in a sub-repo — the Worker's cwd, not C-0/C-1; one Tower vs one per repo; limits), debug tiers, quality gates, Worker's four safeguards, beginner mode, ct-insights, ct-evolve, FIELDGUIDE, archive operations, migration, Tower auto-commit |
| `references/integration.md` | Methodology adapters in brief (v6.0.0+: 5 layers, swap vs layering, adapter sources, positioning, adoption modes, injection guard; links to the Beta chapter), Level 1 ECC (v6.0.0-beta.10: retired, why, and where each feature went), Level 2 external bmad-guide (v5.14.1: where the Tower looks — manual install first, then the Claude and Codex plugin installs; read-only; a one-time notice when it is installed but unreadable; v6.0.0-beta.6: the same order as adapter probes with `skill_root`; v5.14.4／v6.0.0-beta.8: per runtime — this runtime's manual install, then its plugin, then the other runtime's installs as a read-only source; one Claude plugin root), Level 3 mem0 REST (v6.0.0-beta.10: enabled only with a local-rules exception under the user-level plugin rule), Codex integration, Playbook engine, research/spec files, `*import`, `*onboard`, environment detection |
| `references/runtime-dispatch.md` | Terminal-independent dispatch: auto-session's four levels, how `CT_MODE` reaches the Worker, YOLO breakpoints (A/B/C/D/E; v5.13.1／v6.0.0-beta.4: a report ID missing its prefix is not breakpoint A unless ambiguous), the yolo Tower-question channel in brief, agent neutrality, success signals, fallback chain, Worker-side notify fallback |
| `references/bat-integration.md` | Everything BAT: what BAT is and why CT integrates it, the BAT-defines/CT-calls split, how the BAT Tower and the CT Tower collaborate (CT-T011/T013/T014/T015/T016), a Worker tab's lifecycle, the two env-var groups, `--workspace` vs `--cwd`, who builds `/` or `$` (v5.14.0: a Codex plugin install could not take BAT dispatch; v5.14.1／v6.0.0-beta.6: dispatch templates take `<工單 ID>`; v5.14.2／v6.0.0-beta.6: on BAT `>= 0.7.2-pre.1` BAT picks `$ct-exec` or `$ct:ct-exec`, so it can, and why BAT decides rather than the Tower; pre-releases ship no plugin, 6.0.0 is on the marketplace), 塔台分頁角色宣告 (`--set-role`), worktree isolated dispatch (`--isolation worktree`, `CT_HOME`, exit `7`), `BAT_HELPER_NODE`, scoped token and tab roles (`Forbidden`／`RECOVERY_PENDING`, naming tabs by title), Worker notify (v5.13.1／v6.0.0-beta.4: why `--source` must be the full work order ID — BAT matches the Worker tab by it), closing the Worker tab (worker_auto_close, `--worktree keep`; v5.12.0: closing the old tab before a re-dispatch), query channels (`--worktree-status`, BAT MCP), breakpoint D (`blocked`), the BAT Tower panel read contract (why a page goes empty, the 400 KB budget, how to measure; v5.13.0／v6.0.0-beta.3; v5.13.1／v6.0.0-beta.4: BAT `>= 0.7.1-pre.9` shows "cannot read" and counts `critical` as High, and why the budget stays), CT ↔ BAT version table |
| `references/governance.md` | Design rationale of the guardrails: Landing Zone Check (identity ≠ path; C-0 inside a worktree), summary authority rule, single authoritative definition, Layer 1 write mechanism and install flow, the plugin marketplace as a second install method (v5.14.0／v6.0.0-beta.5 text; v6 on the marketplace since 6.0.0, pre-releases ship no plugin: what it is, relation to the zip, which copy wins when both exist, auto-update, Codex + BAT (v5.14.2／v6.0.0-beta.6: by BAT version); v5.14.1: the same marketplace also offers `bmad-guide`, which a Beta user may install alone), versioning, merge guardrails, deprecation clauses |
| `references/diagrams.md` | Before generating any SVG visualization (20 diagram types, incl. v6.0.0-beta.10 session usage data flow, incl. BAT/YOLO dispatch loop, Landing Zone Check decision tree, frontmatter SoT/drift, EXP state machine, BAT tab relationship and lifecycle, isolated work order merge, Beta: 5 layers × adapters, three adoption modes) |
| `references/preview-methodology.md` | **v6 pre-release history (pre.1～rc.1; included in the stable 6.0.0; chapter keeps its Beta name and anchors)**: Beta status and where to download, why methodology adapters, a methodology is not something CT must adopt (principle, per-methodology positioning with evidence, living with an installed Superpowers), using mattpocock/skills in a CT project (option ③ steps, P3 results, `.gitignore`／worktree caveat), swap vs layering (5 layers, `methodology` and `methodology_<layer>`, per-work-order override, delivery stays closed), what an adapter is (built-in bmad, external optional `ct-adapter-pstack` 0.2.6, project-local; when a guide skill is needed), the three adoption modes (full install／skills only／partial reference; ③ tested, ② not) with a clickable SVG, injection guard (`### 方法論邊界`, `methodology_guard: warn`, recording methodology use, re-read after compact／resume) with the V1／V2a／V2b numbers, Codex hook trust, dual injection, what the isolated trials P1／P1b (T0314／T0315) found and how beta.1 fixed it (P-2／P-4／P-5／Q-1／Q-3／Q-4), what P3 (T0327) found and how beta.2 fixed it (P3-1～P3-6, HARD-GATE 2/2 not triggered), BUG／PLAN／EXP on by default and the upgrade impact, env detection listing names only (bash `compgen -e`, one variable per command), `CLAUDE_CONFIG_DIR`／`CODEX_HOME`, the `_tower-state.md` machine-readable summary (BAT overview), a map of beta.3's status-hygiene and BAT-panel rules to the main chapters (same rules as stable 5.13.0), a map of beta.4's full-work-order-ID and BAT-panel (pre.9) rules to the main chapters (same rules as stable 5.13.1), a map of beta.5's plugin-install-readiness rules to the main chapters (same rules as stable 5.14.0; the Beta ships no plugin, do not install it from the marketplace), beta.6: a map of the ported 5.14.1／5.14.2 rules to the main chapters and the v6-only adapter plugin probes (how a probe resolves a skill root, `skill_root`, the two `bmad.yaml` plugin probes, the one-time notice; a beta user may install only `bmad-guide` from the stable marketplace), beta.7: a pointer to the ported 5.14.3 nested-independent-repos layout, beta.8: a map of the ported 5.14.4 rules and the v6-only probe field `runtime` (how probes are tried per runtime, the split `bmad.yaml` 0.2.1 and `ct-adapter-pstack` 0.2.6 probes), beta.9: a pointer to the ported 5.15.0 question batching, the 41 known-unverified items (as of 6.0.0, same as rc.1), and a ready clickable SVG of 5 layers × adapters; beta.10 (v6 only): session usage statistics (`*insights sessions`, Worker `session_ids`, the Tower session id, closeout backup and snapshot, Tower usage never allocated, estimates) with a clickable data-flow SVG; beta.10: how session evidence enters the learning flow (`ct-evolve --facts-from`, no new threshold, withdrawal) and ECC Level 1 retired (compatibility table, one learning mechanism, mem0 Level 3 only with a local-rules exception, BAT launch arguments without `--settings`); beta.11 (v6 only): mid-flight addenda (`## 塔台補充（執行中 #N）`, the Worker's three check points, `ct-done` before its report, the optional nudge to the Tower's own Worker, what isolated `claude -p` verified and the file-change notice); beta.12 (v6 only): the tool-list suggestion `*insights tools` (what counts as loaded and used, grouped by work order type, suggest only, layers and keys, core built-in tools kept, measured vs unverified levers); rc.1: the release candidate (features frozen, fixes only, what it fixed); 6.0.0: included in the stable release |
