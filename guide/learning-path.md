---
title: CT Guide 學習路線
description: 依讀者分流的 CT Guide 教材閱讀順序：新手先讀哪三份，想懂架構、用 yolo、搭配 BAT 或整合其他工具的人各讀哪幾份。
---

# CT Guide 學習路線

<p class="ct-lead">Guide 有十份教材，不必從頭讀到尾。Guide 會從你的用詞判斷你是哪一類讀者，只讀那幾份；你自己讀的時候，也可以照同一套分流挑起點。</p>

這是 [CT Guide](./ct-guide)（`control-tower-guide`）的學習路線，教的是 CT。要學 BMad-Method，問另一個 skill [BMad Guide](./bmad-guide)。

## 依讀者分流

Guide 回答前會先看問題裡的關鍵詞。像「入門、開始、新手、第一次、什麼是、怎麼用」這類詞，表示你是新手，它會從 `concepts.md` 和 `ecosystem.md` 開始講，再帶到 `work-order-lifecycle.md`。問到「三層、同構、Layer 1、跨專案、除錯、Playbook、決策日誌」，就改走架構那幾份；問到 YOLO、斷點、落點檢查、單一權威，走派工與治理；問到 BAT、Worker 分頁、範圍權杖，走 BAT 整合。

下面每條路線列出 Guide 的教材順序，以及 Portal 裡對應的入口頁。

<LearningPath />

## 新手路線：先讀這三份

1. **`concepts.md`**：CT 的核心哲學。為什麼把塔台和 Worker 分開、Worker 為什麼不帶狀態、塔台有哪些不能碰的硬邊界、為什麼一切以檔案為準。
2. **`ecosystem.md`**：CT 有哪些零件。8 個 skill 各自的 `/` 與 `$` 入口、`*`／`/`／`$` 三軌前綴、塔台指令、四級能力與完整設定表。
3. **`work-order-lifecycle.md`**：一張工單從開單到收單的完整過程，包括狀態機、Worker 執行的四個階段、回報規範與 commit 規則。

讀完這三份，再到 Portal 看[一張工單的一生](/lifecycle)，就能把概念對到實際的操作。

比起讀文件更想先看影片，可以從[推廣影片（第二季）](/podcast)的 S2-01、S2-03 開始。

## 進階路線：依主題挑

新手路線之外的六份教材彼此獨立，依你遇到的問題挑著讀即可。

- **`three-layer-arch.md`**：Core、Global、Project 三層資料各放什麼、誰能寫哪一層、設定的四層覆蓋、學習紀錄的分流，以及塔台自己的狀態檔與決策日誌。→ Portal：[三層資料與記憶](/deep/principles/data-layers)
- **`runtime-dispatch.md`**：派工怎麼和終端無關地運作。auto-session 四階、`CT_MODE` 怎麼送到 Worker、YOLO 的斷點 A–E、Claude Code 與 Codex 的中立性、成功判讀與降級鏈。→ Portal：[派工：auto-session 與 BAT](/deep/features/dispatch)、[yolo 與斷點 A–E](/deep/features/yolo)
- **`bat-integration.md`**：和 BAT 有關的一切。BAT 定介面、CT 照契約呼叫的分工，兩座塔台怎麼協作，一張 Worker 分頁的生命週期，範圍權杖、隔離派工、查詢通道、斷點 D，以及 CT 與 BAT 的版本對照。→ Portal：[派工：auto-session 與 BAT](/deep/features/dispatch)、[相容版本對照](/versions/compatibility)
- **`governance.md`**：各道護欄的設計理由。落點檢查為什麼「身分不能用路徑證明」、摘要授權規則、單一權威定義、Layer 1 寫入機制、版本治理、合併護欄與棄用條款。→ Portal：[治理：單一權威與「摘要不具權威」](/deep/principles/governance)、[落點檢查](/deep/features/landing-check)
- **`advanced-patterns.md`**：五種跨專案協調類型、多塔台、中斷與恢復、mono-repo（含 v5.14.3 起一個塔台管多個巢狀的獨立 repo）、除錯防線、品質閘門、Worker 的四項防護、新手村、`ct-insights`、`ct-evolve`、FIELDGUIDE、歸檔與遷移。→ Portal：[跨塔台與跨專案協作](/deep/features/multi-tower)、[觀測與改進](/deep/features/observability)
- **`integration.md`**：CT 怎麼接其他工具。Level 1 ECC、Level 2 外部 bmad-guide、Level 3 mem0，Codex 整合、Playbook 引擎、`*import` 與 `*onboard`。→ Portal：[功能總覽](/features)

第十份 `diagrams.md` 是圖表規格，給 Guide 自己畫圖時用，讀者不需要讀；它定義了哪些圖、節點代表什麼、點下去要展開哪一章（見 [CT Guide Skill](./ct-guide) 的「圖是現場畫的，而且可以點」一節）。

## 在意 Workflow 的人

如果你想知道 Claude Code 的 Workflow 工具在 CT 裡的位置，先讀 `concepts.md` 的「Workflow：單張工單內的執行方式」一節，再看 `advanced-patterns.md` 裡 `ct-insights` 與 `ct-evolve` 的規則。Portal 的對應篇是[自我學習、Playbook 與 Workflow](/deep/features/learning-playbook-workflow)。

## Portal 和 Guide 的分工

Portal 不重寫 Guide 的教材，這一頁只放摘要和導讀。想深入時，裝好 Guide 直接問它，或讀 Guide 的 `references/` 原文；教材本身以 Guide skill 為準。

## 延伸閱讀

- Guide `SKILL.md` § Audience routing、§ Reference file routing
- Guide `references/concepts.md`、`ecosystem.md`、`work-order-lifecycle.md`、`three-layer-arch.md`、`runtime-dispatch.md`、`bat-integration.md`、`governance.md`、`advanced-patterns.md`、`integration.md`、`diagrams.md`（各檔 H1 與 H2）

Portal 是摘要，不具權威；與 Guide 或 CT reference 有出入時，以 reference 為準。
