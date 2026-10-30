---
title: 功能總覽
description: CT 由哪 8 個 skill 組成、各在哪種 session 做什麼，塔台內建命令依用途分成哪幾組，四級能力、設定的四層覆蓋，以及每項功能對應的進階篇。指令語法與參數見指令參考大全。
---

<script setup>
const mapRows = [
  ['工單：編號、粒度、模板欄位、重疊檢查', '工單系統'],
  ['派工：四種模式、終端偵測、BAT、降級鏈', '派工：auto-session 與 BAT'],
  ['yolo 與斷點 A–E', 'yolo 與斷點 A–E'],
  ['Worker 在 yolo 下改問塔台', 'Worker 向塔台提問'],
  ['worktree 隔離與合併工單', 'worktree 隔離與三種合併模式'],
  ['Worker 寫入前確認 repo 身分', '落點檢查'],
  ['*pause／*resume、Renew、ct-done', '中斷、Renew 與補救收尾'],
  ['*bug、*plan、*exp、研究型工單', 'BUG／PLAN／EXP 與研究型工單'],
  ['*evolve、ct-evolve、Playbook、Workflow', '自我學習、Playbook 與 Workflow'],
  ['project-prefix、跨專案與多塔台', '跨塔台與跨專案協作'],
  ['ct-status、ct-insights、ct-fieldguide、*fieldguide', '觀測與改進']
]
</script>

# 功能總覽

CT 由 1 個塔台 skill 和 7 個 Worker／輔助 skill 組成，塔台在自己的 session 裡還有 15 個內建命令。這一頁講每個部分**做什麼、在哪裡用**；每個指令的語法、參數、前綴與設定值，只寫在[指令參考大全](/reference/commands)。 {.ct-lead}

## CT 由什麼組成 {#skills}

**塔台**（在你自己開的塔台 session 裡）

- **`control-tower`**：對齊需求、開單、派工、收單、記錄決策與學習；不寫產品程式碼。在 BAT 裡要從你自己開的一般分頁啟動，不能在被派出來的 Worker 分頁裡。

**Worker**（一張工單一個新的 session）

- **`ct-exec`**：主力。執行一張工單的完整生命週期：確認落點、開工、執行、驗證、收尾、通知塔台。
- **`ct-done`**：補救。session 中斷、漏了收尾或要更正狀態時，把回報與收尾補完，不做新的產品工作。
- **`ct-fieldguide`**：產生、更新、稽核專案的 FIELDGUIDE 與 DESIGN.md。

**輔助**（任何 session 都能用）

- **`ct-status`**：唯讀查單張或全部工單的狀態，以及 frontmatter 與 body 的不一致。
- **`ct-evolve`**：從執行紀錄萃取可複用的經驗，晉升成 Playbook，或寫成 skill／Workflow 的 brief。
- **`ct-insights`**：分析工單歷史與使用模式，找出好模式、壞模式與原則衝突。
- **`ct-help`**：操作手冊，回答「現在該輸入什麼」；只解釋，不建立也不修改工單。

**為什麼拆成 8 個？** 塔台 skill 帶著「不准寫程式碼」這類嚴格的硬邊界，但 Worker 必須直接讀寫程式碼。拆成獨立的 skill，Worker session 就不會載入塔台的角色限制。塔台啟動時會檢查其他 skill 有沒有裝，缺了會警告。

每個 skill 在 Claude Code 與 Codex 裡都能用，行為相同；兩種 CLI 的寫法與每個 skill 的參數見[指令參考大全 › skill 指令](/reference/commands#skills)。

另外有一個獨立發行、與 CT 同版號的 [CT Guide Skill](/guide/ct-guide)（`control-tower-guide`），它是解釋設計理由的教科書，不是 CT 的 8 個 skill 之一。

## 塔台內建命令 {#tower}

這 15 個命令只在進行中的塔台 session 裡有意義，在塔台角色裡就地處理，處理完繼續塔台的工作。依用途分成五組：

- **掃描與設定**（`*rescan`、`*config`、`*help`）：刷新塔台對環境的快照、調整塔台行為、不離開塔台查使用說明。
- **同步與中斷**（`*sync`、`*pause`、`*resume`）：以工單檔為準校準塔台記憶與進度；緊急任務插進來時凍結手上的工單，處理完再接回來。
- **單據與歸檔**（`*bug`、`*plan`、`*exp`、`*archive`）：登記 BUG、規劃與實驗單（各自需先啟用），把結案的單據移到冷區、需要時再找回來。
- **學習與分析**（`*evolve`、`*insights`、`*fieldguide`）：在塔台裡萃取學習、分析使用模式、盤點 FIELDGUIDE 與 DESIGN.md；要改檔的一律開成工單交給 Worker。
- **匯入與引導**（`*import`、`*onboard`）：安全匯入規則、Playbook 與其他專案的設定；用問答探索你的工作習慣，產出個人化的本地規則。

有幾個命令和獨立 skill 同名（例如 `*evolve` 與 `ct-evolve`），差別不在功能多寡，而在**在哪個角色裡執行**：塔台命令在塔台角色裡處理，獨立 skill 在自己的 session 以自己的角色執行。

每個命令的參數、子命令與起始版本，以及已經不存在的舊命令，見[指令參考大全 › 塔台內建命令](/reference/commands#tower)。

## 四級能力 {#levels}

CT 的功能隨可選元件遞增。每項偵測各自獨立，可以任意組合（例如只有第 0 級加 bmad-guide 也完全合法）；缺了任何一個都安靜降級，不會報錯。

<CapabilityLevels />

- **第 0 級已經完全可用**。工單、進度、Debug、中斷處理、多塔台與自我學習都只靠檔案。
- **bmad-guide 是外部依賴**。CT 不內嵌 BMad-Method 內容；沒有它時，工作流程欄位改由你手動指定。
- **mem0 目前只單向寫出**。經驗會同步出去，塔台不會反過來查詢它。

## 設定 {#config}

設定屬於塔台，決定派工後要不要自動開 Worker、提示有多詳細、開單前問幾輪、啟用哪些單據類型、Worker 收尾的 commit 政策等。在塔台裡用 `*config` 查看與修改。

設定分四層，上面的蓋過下面的：**session（在塔台裡即時修改）> 專案（`_ct-workorders/_tower-config.yaml`）> 全域（`~/.claude/control-tower-data/config.yaml`）> 預設值**。只想試一下就只改 session；要讓這個專案或所有專案都這樣，再寫進對應的那一層。

全部選項、值域、預設值與寫入方式見[指令參考大全 › `*config`](/reference/commands#config)。

::: tip Worker 不讀設定檔決定模式
塔台派工時把模式透過環境變數 `CT_MODE`、`CT_INTERACTIVE` 傳給 Worker；Worker 只從設定讀重試上限、commit 政策這類調諧參數，不用設定檔決定要不要自動回報。這樣同一張工單、同一組參數，在哪個 session 執行都會得到相同的行為。
:::

## 每項功能在進階區的哪一篇 {#deep-map}

<CardTable caption="功能與進階篇對照" :columns="['功能', '進階篇']" :rows="mapRows" />

進階篇的入口在[進階：功能深入](/deep/#features)；為什麼這樣設計，見[設計理念](/deep/#principles)。

## 延伸閱讀 {#further}

- `control-tower/SKILL.md` § Built-In Commands、§ Hard Boundaries
- `ct-help/SKILL.md` § Command Families
- CT 安裝與使用指南 § 4.3 Skill 架構（v5.13.1）、§ 5. 四級能力等級、§ 13. Config 速查表（v5.13.1）、§ 14. 命令速查表（v5.13.1）
- CT Guide `references/ecosystem.md` § 八個 Skill 元件、§ 三軌前綴：`*`、`/`、`$`、§ 能力等級（Level 0-3）
- `control-tower/references/tower-config.md` § `*config` 命令、§ 可用選項、§ 作用域與持久化

Portal 是摘要，不具權威；與 reference 有出入時，以 reference 為準。
