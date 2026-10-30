---
title: 指令參考大全
description: CT 指令的唯一完整清單：8 個 skill 與 CT Guide 的 slash／$ 指令、塔台的 15 個 * 內建命令（含子命令、旗標與 *config 全部設定鍵），以及 yolo 中斷詞、Renew 觸發詞等對話慣用語。
---

<script setup>
const twoCliRows = [
  ['啟動塔台', '/control-tower', '$control-tower'],
  ['執行一張工單', '/ct-exec T0001', '$ct-exec T0001'],
  ['補救收尾', '/ct-done T0001 PARTIAL', '$ct-done T0001 PARTIAL'],
  ['查狀態', '/ct-status', '$ct-status'],
  ['萃取經驗', '/ct-evolve --status', '$ct-evolve --status'],
  ['使用模式分析', '/ct-insights', '$ct-insights'],
  ['FIELDGUIDE', '/ct-fieldguide audit', '$ct-fieldguide audit'],
  ['使用說明', '/ct-help', '$ct-help'],
  ['塔台內建命令', '*sync（不分 CLI，只在塔台 session 裡）', '*sync']
]
const towerRows = [
  ['*rescan', '完整掃描，刷新塔台狀態檔的環境快照', '—', 'v4.0.1'],
  ['*config', '檢視或修改塔台設定', '[選項] [值] [--save project|global]、reset [選項]', 'v3.2.0'],
  ['*help', '不離開塔台查使用說明', '[主題]：commands、workflow、config、workorder、status、tips', 'v3.2.0'],
  ['*sync', '以工單檔為事實來源，校準塔台記憶、工單與 sprint-status.yaml', '—', 'v3.2.0'],
  ['*pause', '凍結進行中的工單，處理緊急任務', '[原因]', 'v3.2.0'],
  ['*resume', '恢復被暫停的工單', '[工單編號]', 'v3.2.0'],
  ['*bug', '登記 BUG 單（需先啟用）', '[標題]', 'v4.0.0'],
  ['*plan', '登記 PLAN 單（需先啟用）', '[標題]', 'v4.0.0'],
  ['*exp', '登記 EXP 實驗單（需先啟用）', '[描述]', 'v4.0.0'],
  ['*archive', '把最終態的單據從熱區移到冷區', '--dry-run、T####、--search <關鍵字>、--restore T####', 'v4.0.0'],
  ['*evolve', '在塔台裡萃取學習', '[主題]、--playbook [名稱]、--skill [名稱]、--status、--workflow [名稱]', 'v3.2.0（--workflow：v5.11.0）'],
  ['*insights', '在塔台裡做使用模式分析', 'workflow [T#### …]', 'v3.4.0（workflow：v5.11.0）'],
  ['*fieldguide', 'FIELDGUIDE 與 DESIGN.md 管理（只讀與分析，寫入一律開工單）', 'scan [N]、add [主題]、audit [模組]、init、debt [主題]、design [generate|check]', 'v3.5.0（design：v3.6.0）'],
  ['*import', '安全匯入規則、Playbook 或其他專案的設定', 'rule、playbook、--from <檔案>、--check、--fix', 'v4.0.0'],
  ['*onboard', '互動式探索你的工作習慣，產出個人化的本地規則', '—', 'v4.0.0']
]
</script>

# 指令參考大全

這是 CT 指令的唯一完整清單；CT 由什麼組成、每個功能在哪篇講，見[功能總覽](/features)。這一頁列出 CT 的每一個指令：語法、參數與旗標、在哪種 session 用、做什麼、權威出處與起始版本。**Portal 是摘要，不具權威**；旗標的確切拼法與完整行為，以各列標出的 reference 為準，兩者有出入時以 reference 為準。 {.ct-lead}

**目錄**

- [三軌前綴](#prefixes)
- **skill 指令**：[`/control-tower`](#control-tower)、[`/ct-exec`](#ct-exec)、[`/ct-done`](#ct-done)、[`/ct-status`](#ct-status)、[`/ct-evolve`](#ct-evolve)、[`/ct-insights`](#ct-insights)、[`/ct-fieldguide`](#ct-fieldguide)、[`/ct-help`](#ct-help)、[CT Guide](#control-tower-guide)
- **塔台內建命令**：[`*rescan`](#rescan)、[`*config`](#config)、[`*help`](#help)、[`*sync`](#sync)、[`*pause`](#pause)、[`*resume`](#resume)、[`*bug`](#bug)、[`*plan`](#plan)、[`*exp`](#exp)、[`*archive`](#archive)、[`*evolve`](#evolve)、[`*insights`](#insights)、[`*fieldguide`](#fieldguide)、[`*import`](#import)、[`*onboard`](#onboard)
- **對話慣用語**：[yolo 中斷詞](#yolo-stop)、[Renew 觸發詞](#renew)、[回報字串](#report-strings)
- [不要找：不存在或已刪除的指令](#not-commands)

## 三軌前綴 {#prefixes}

| 前綴 | 是什麼 | 在哪用 | 角色切換 |
|---|---|---|---|
| `/` | Claude Code 載入一個獨立 skill | 任何 Claude Code session | 載入該 skill 的角色 |
| `$` | Codex 載入一個獨立 skill | 任何 Codex session | 同 `/` |
| `*` | 塔台內建命令 | **只在**進行中的塔台 session 裡 | 不切換，處理完繼續塔台流程 |

`/` 與 `$` 是**同一個 skill 的兩個入口**，差別只在宿主工具。在 BAT 裡由 BAT 依 Worker 用的 Agent 決定送哪一種，塔台不寫死。以下各節都用 `/` 示範，Codex 一律把 `/` 換成 `$`：

<CardTable caption="同一個 skill 在兩種 CLI 的寫法" :columns="['用途', 'Claude Code', 'Codex']" :rows="twoCliRows" />

`*` 命令和同名的獨立 skill（例如 `*evolve` 與 `/ct-evolve`）的差別在**在哪個角色裡執行**，不在功能多寡。

出處：CT Guide `references/ecosystem.md` § 三軌前綴：`*`、`/`、`$`；CT 安裝與使用指南 § 4.2 Agent CLI 選擇。

## skill 指令 {#skills}

每個 skill 屬於塔台、Worker 還是輔助，以及為什麼拆成 8 個，見[功能總覽 › CT 由什麼組成](/features#skills)。

### `/control-tower` {#control-tower}

- **語法**：`/control-tower [一句話需求或情境]`（Codex：`$control-tower`）
- **參數**：可選的自由文字，例如 `/control-tower 接手這個專案，前手只留了 README`。
- **在哪用**：塔台 session。在 BAT 裡要從你自己開的一般分頁啟動；在被派出來的 Worker 分頁裡，派工類操作會被 BAT 拒絕。
- **做什麼**：啟動或恢復塔台。依序讀專案規則（`AGENTS.md`、`_ct-workorders/_local-rules.md`、`CLAUDE.md`）→ 讀 `_tower-state.md`，有新鮮的環境快照就走快速恢復 → 讀設定（session > 專案 > 全域 > 預設）→ 計算熱區工單數 → 在 BAT 裡宣告這個分頁是塔台 → 顯示狀態面板。只有狀態檔不存在、快照空白或超過 7 天、或你輸入 `*rescan` 時，才做完整掃描。之後跟你對齊需求、開單、派工、收單；硬邊界是不實作產品程式碼、不讀原始碼與原始 log、不用背景 agent 取代工單、不寫已安裝的 skill、未經授權不 push。
- **起始版本**：CT 本體。現行的「塔台與 Worker 分成獨立 skill」自 v3.1.0。
- **權威出處**：`control-tower/SKILL.md` § Startup Protocol、§ Hard Boundaries、§ Request Routing
- **相關**：[為什麼需要 CT](/why)、[塔台不讀程式碼](/deep/principles/tower-and-workers)

### `/ct-exec T####` {#ct-exec}

- **語法**：`/ct-exec T####`，或工單檔路徑（Codex：`$ct-exec T####`）
- **參數**：一個工單編號或路徑。同一個編號在 `_ct-workorders/` 下找到多張時，Worker 停下來請你指定。
- **執行環境**：由塔台派工時傳入，Worker 不讀設定檔決定模式。`CT_MODE`：`yolo`／`ask`／`off`／`on`（沒有或不合法時當成 `ask`）；`CT_INTERACTIVE`：`1` 允許研究型互動、`0` 禁止；`CT_HOME`：在 BAT 的 worktree 隔離分頁裡才有，指向主 checkout。
- **在哪用**：Worker session（一張工單一個新的 session）。
- **做什麼**：執行一張工單的完整生命週期——讀專案規則與整張工單 → **落點檢查**（任何寫入之前；`repo` 不符就停）→ 標 `IN_PROGRESS` → 只在範圍內執行 → 跑驗收、證據分道記錄 → **反序收尾**（產品 commit → 回報區 → 最終狀態 → 工單 commit）→ 通知塔台。通知與提問用收到的**完整工單 ID**：`/ct-exec CP-T0113` 回的是 `CP-T0113 完成`，不會截成 `T0113`；送出前先和工單 frontmatter 的 `id` 比對，不一致就改用 `id`（v5.13.1 起）。工單原本就是 `IN_PROGRESS` 時記成接續執行。`CT_MODE=yolo` 時不問你，有問題寫進工單問塔台。
- **起始版本**：v2.1.1（獨立 skill：v3.1.0；`$` 入口：v5.0.3；落點檢查：v5.0.4；yolo 向塔台提問：v5.5.0；完整工單 ID 通知：v5.13.1）
- **權威出處**：`ct-exec/SKILL.md`（§ Startup、§ Mode And Environment、§ Landing Zone Check、§ Phase 1～4、§ Questions For Tower (`CT_MODE=yolo`, v5.5.0+)、§ BAT Notify And Fallback）；`control-tower/references/work-order-system.md` § 回報與通知用的工單 ID
- **相關**：[一張工單的一生](/lifecycle#worker)、[落點檢查](/deep/features/landing-check)、[Worker 向塔台提問](/deep/features/worker-questions)

### `/ct-done T#### [狀態]` {#ct-done}

- **語法**：`/ct-done T#### [DONE|FIXED|PARTIAL|BLOCKED|FAILED]`（Codex：`$ct-done …`）
- **參數**：工單編號或路徑；可選的最終狀態。沒給狀態時，依回報區的證據判斷，判斷不了就問你。`ABANDONED` 這類退役狀態只在範圍決定要退役這張工單時使用。
- **在哪用**：Worker session（補救用）。
- **做什麼**：只做收尾的修補，**不做新的產品工作**——落點檢查 → 收集現況證據（`git status`、變更檔、最近的 commit）→ 先補齊回報區缺的欄位 → 再更新狀態 → commit 工單檔本身 → 通知塔台（和 `/ct-exec` 一樣用完整工單 ID）。產品改動不替你 commit，只告訴你哪些看起來還沒 commit。遇到原本是 `PARTIAL`、但卡點已經解除的工單，補一段事後註記並改成 `DONE`。不會送 `T#### 提問`。
- **起始版本**：v2.1.1（獨立 skill：v3.1.0）
- **權威出處**：`ct-done/SKILL.md` § Workflow、§ Status Selection、§ Commit Check、§ BAT Notify；`control-tower/references/work-order-system.md` § 回報與通知用的工單 ID
- **相關**：[常見問題 › 卡在 IN_PROGRESS](/faq#in-progress)、[中斷、Renew 與補救收尾](/deep/features/recovery)

### `/ct-status [參數]` {#ct-status}

- **語法**：`/ct-status`、`/ct-status T####`、`/ct-status all`、`/ct-status sync`、`/ct-status active`（Codex：`$ct-status …`）
- **參數**：

  | 參數 | 行為 |
  |---|---|
  | `T####` 或路徑 | 單張工單的狀態與重要 metadata |
  | 空白或 `all` | 熱區工單摘要 |
  | `sync` | 比對工單檔與 `sprint-status.yaml`（在 repo 根目錄、`_bmad-output/`、`docs/` 找） |
  | `active` | 只強調還需要塔台或 Worker 動作的項目 |

- **在哪用**：任何 session。
- **做什麼**：從檔案讀狀態，**不改任何檔案**（除非你明確要求修復）。優先讀 frontmatter，frontmatter 與 body 不一致時報 `metadata_drift` 並以 frontmatter 為準；無法辨識的狀態維持 `UNKNOWN`，不會被當成 `PENDING`。分桶時，未解決的 `PARTIAL`、`BLOCKED`、`FAILED`，以及已有接續工單或重派的 `INTERRUPTED`（v5.12.5 起），都歸「需要塔台判斷」。`sync` 比對有落差時，最後一句會請你交給塔台處理（`*sync`，或跟塔台說「重新同步」），`ct-status` 本身維持唯讀。也會跑落點檢查，但只報告結果、不會停下來。
- **起始版本**：v2.1.1（獨立 skill：v3.1.0）
- **權威出處**：`ct-status/SKILL.md` § Modes、§ Read Order、§ Status Buckets、§ Output
- **相關**：[狀態機與分桶](/lifecycle#states)、[觀測與改進](/deep/features/observability)

### `/ct-evolve [模式]` {#ct-evolve}

- **語法與模式**：

  | 參數 | 模式 | 行為 |
  |---|---|---|
  | 空白或主題 | 學習萃取 | 掃描紀錄，提出萃取過的模式 |
  | `--playbook [名稱]` | Playbook 晉升 | 把驗證過的模式晉升成可重用的 Playbook |
  | `--skill [名稱]` | skill 候選 | 只產出 skill brief；真的要寫成已安裝的 skill，另外用 `skill-creator` |
  | `--workflow [名稱]` | Workflow brief（v5.10.0+） | 只產出 Workflow brief，寫成 🔵 知識卡；不寫 `.claude/workflows/`、不寫腳本、不執行 Workflow |
  | `--status` | 管線狀態 | 各成熟度的數量、過時或重複的經驗、建議的下一步 |

- **在哪用**：任何 session。
- **做什麼**：讀 `_learnings.md`、決策日誌、塔台狀態與已完成的工單，找出候選的模式、反模式與重複出現的序列。每個候選都要回答「發生了什麼、為什麼、什麼條件下會再發生、代表什麼通則、以後該怎麼做」才寫入；分成 Tactical、Strategic、Episodic 三區，不確定時寧可放 Tactical 或 Episodic。專案與全域的範圍不清楚時什麼都不寫、先問你。涉及程式碼慣例或視覺規範的候選會加 `[FG-CANDIDATE]` 標記，交給 `ct-fieldguide`。
- **起始版本**：v3.0.0（獨立 skill：v3.1.0；`--playbook`／`--skill`／`--status`：v4.0.0；`--workflow`：v5.10.0）
- **權威出處**：`ct-evolve/SKILL.md` § Modes、§ Distillation Gate、§ Promotion Modes
- **相關**：[`*evolve`](#evolve)、[自我學習、Playbook 與 Workflow](/deep/features/learning-playbook-workflow)

### `/ct-insights [global]` {#ct-insights}

- **語法**：`/ct-insights`（本專案）、`/ct-insights global`（跨專案；Codex：`$ct-insights …`）
- **參數**：空白 = 本專案的 `_ct-workorders/`、塔台狀態、決策、學習與 `sprint-status.yaml`；`global` = 全域的專案登記簿與各專案摘要。
- **在哪用**：任何 session。
- **做什麼**：計算狀態分布、週期時間、`BLOCKED`／`PARTIAL` 比例、重試與三振訊號、停滯的工作，偵測好模式、壞模式與原則衝突，依影響與成本排出建議。觀察到的事實與推論分開寫；工單少於三張時說明樣本太小，只給局部觀察。問到「哪些工作適合 Claude Code Workflow」時，只輸出候選，不寫 brief、不執行 Workflow。
- **起始版本**：v3.4.0
- **權威出處**：`ct-insights/SKILL.md` § Scope、§ Analysis Flow、§ Report Rules
- **相關**：[`*insights`](#insights)、[觀測與改進](/deep/features/observability)

### `/ct-fieldguide <子命令>` {#ct-fieldguide}

- **語法與子命令**：

  | 子命令 | 做什麼 |
  |---|---|
  | `init` | 從 `CLAUDE.md`、repo 慣例與代表性的程式碼建立第一版 FIELDGUIDE |
  | `update` | 依最近的工單證據或明確的發現，修補 FIELDGUIDE 的特定章節 |
  | `audit` | 比對 FIELDGUIDE 與實際程式碼，報告不一致、缺漏、過時路徑與技術債 |
  | `audit --debt` | 找出同一個慣例有好幾種互相競爭的實作 |
  | `extract` | 產出結構化的清單，不立刻合併 |
  | `merge` | 把 `extract` 的結果在衝突檢視後合併進目標 FIELDGUIDE |
  | `promote` | 評估專案規則能不能晉升到全域 |
  | `design` | 從程式碼或網址產生、稽核 DESIGN.md |

- **參數**：沒給子命令時，從你的要求推斷最安全的唯讀動作，意圖不清楚時優先 `audit`、不寫入。
- **在哪用**：Worker session。修改量大的情況由塔台開工單交給它。
- **做什麼**：只寫 FIELDGUIDE 與 DESIGN.md，不改產品程式碼（除非工單明說）；寫入型子命令回報改了哪些檔、哪些章節、用了什麼證據，唯讀型的標成「僅稽核／擷取」。
- **起始版本**：v3.5.0（`design`：v3.6.0）
- **權威出處**：`ct-fieldguide/SKILL.md` § Command Routing
- **相關**：[`*fieldguide`](#fieldguide)、[觀測與改進](/deep/features/observability)

### `/ct-help [問題]` {#ct-help}

- **語法**：`/ct-help`、`/ct-help <問題>`（Codex：`$ct-help …`）
- **參數**：可選的自由文字問題，例如「`ct-done` 跟 `ct-exec` 差在哪？」。
- **在哪用**：任何 session。
- **做什麼**：操作手冊——先回答你眼前的問題，給確切的指令、紀錄檔的位置、狀態字的意思；新手只解釋接下來兩三步。**只解釋，不建立也不修改工單**，也不切換成塔台或 Worker。
- **起始版本**：v3.1.0
- **權威出處**：`ct-help/SKILL.md` § Command Families、§ User Guidance Patterns
- **相關**：[`*help`](#help)、[CT Guide](#control-tower-guide)

### CT Guide（`control-tower-guide`） {#control-tower-guide}

- **語法**：沒有子命令。直接用問的，例如「CT 入門」「塔台教學」「為什麼 Worker 是無狀態的」「斷點 D 是什麼」。
- **在哪用**：任何 session；也可以上傳到 claude.ai 使用（見[安裝 › 在 claude.ai 使用](/install#claude-ai)）。
- **做什麼**：CT 的教科書，解釋**為什麼**這樣設計，不執行指令、不開工單。依問法分三種回應：概念理解（Learning）、實戰查詢（Practical）、比較釐清（Comparison），並畫可點擊的 SVG 圖讓你往下追問。要確切的旗標或設定值時，它會指向 `ct-help` 或 CT 的 reference。
- **版本**：與 CT 同版號發行，獨立安裝，不是 CT 的 8 個 skill 之一。
- **權威出處**：`control-tower-guide/SKILL.md` § Positioning、§ Response modes
- **相關**：[CT Guide Skill](/guide/ct-guide)、[CT Guide 學習路線](/guide/learning-path)

## 塔台內建命令 {#tower}

以下命令只在**進行中的塔台 session** 裡有意義。這 15 個命令依用途怎麼分組，見[功能總覽 › 塔台內建命令](/features#tower)。

<CardTable caption="塔台內建命令、常用參數與起始版本" :columns="['命令', '做什麼', '常用參數與子命令', '起始版本']" :rows="towerRows" />

下表的參數只列常用的；確切拼法與每個子命令的行為見下面各節。

### `*rescan` {#rescan}

- **語法**：`*rescan`
- **做什麼**：執行完整掃描，刷新 `_tower-state.md` 的環境快照。塔台啟動時只在狀態檔不存在、快照空白或超過 7 天時才自動做；其他時候想刷新快照，就手動輸入這個命令。
- **權威出處**：`control-tower/SKILL.md` § Startup Protocol 第 7 步、§ Built-In Commands；`control-tower/references/memory-protocol.md`

### `*config` {#config}

- **語法**：

  ```text
  *config                                   列出所有設定及來源
  *config <選項>                             查看單項設定
  *config <選項> <值>                         修改設定（只影響這個 session）
  *config <選項> <值> --save project          寫進 _ct-workorders/_tower-config.yaml
  *config <選項> <值> --save global           寫進 ~/.claude/control-tower-data/config.yaml
  *config reset                             所有設定重設為預設值（只影響 session）
  *config reset <選項>                       單項重設為預設值（只影響 session）
  ```

- **作用域**：session > 專案 > 全域 > 預設，上面的蓋過下面的。值不在範圍內、或選項名稱不存在，會報錯並列出可用選項，不修改。
- **在 BAT 裡**：`auto-session` 的生效值一改，塔台會用新的模式再宣告一次自己的分頁。
- **全部設定鍵**：

  | 選項 | 值 | 預設 | 說明 |
  |---|---|---|---|
  | `alignment-rounds` | `0`–`5` | `3` | 開單前最少問幾輪；`0` = 關閉強制提問 |
  | `interactive-prompts` | `on`／`off` | `on` | 選項式提問；`off` 退回純文字提問 |
  | `experience-level` | `beginner`／`standard`／`expert` | `standard` | 提示詳細度與引導程度；`beginner` 啟用新手村教學 |
  | `verbose` | `on`／`off` | `on` | 派工摘要的詳細程度 |
  | `auto-session` | `on`／`ask`／`off`／`yolo` | `ask` | 派工後的行為：`on` 靜默開新分頁；`ask` 先問；`off` 只給文字提示；`yolo` 是 `on` 的超集，Worker 自動送出、塔台自主決定下一張 |
  | `yolo_max_retries` | `0`–`10` | `3` | 斷點 B 的門檻（Renew 次數或連續 `FAILED` 張數）；`0` = 停用斷點 B |
  | `worker_question_timeout` | `0`–`120`（分鐘） | `30` | yolo Worker 問塔台後最多等多久；逾時以 `BLOCKED` 收尾；`0` = 不等 |
  | `project-prefix` | 2–4 個大寫英文字母，或空 | 空 | 跨專案協調用的工單編號前綴。設了前綴時，Worker 回報、通知、提問一律用含前綴的完整 ID（v5.13.1 起） |
  | `enable_bug_tracking` | `true`／`false` | `false` | 啟用 BUG 單（`*bug`） |
  | `enable_plan_tracking` | `true`／`false` | `false` | 啟用 PLAN 單（`*plan`） |
  | `enable_experiments` | `true`／`false` | `false` | 啟用 EXP 實驗單（`*exp`） |
  | `archive_days` | `0`–`365` | `7` | 最終態超過幾天成為歸檔候選；`0` = 立即可歸檔 |
  | `auto_archive_prompt` | `on`／`off` | `off` | `*sync` 結束後是否提示歸檔候選數量 |
  | `bug_review_open_threshold` | `0`–`500` | `20` | v5.13.0 起。熱區未結 BUG 多於這個張數時，`*sync`／`*insights` 印一行提示，建議逐張核對；`0` = 停用這個條件 |
  | `bug_review_stale_days` | `0`–`365`（天） | `30` | v5.13.0 起。有未結 BUG 超過這個天數沒更新時，同上提示；`0` = 停用這個條件 |
  | `customer_acceptance_gate` | `on`／`off` | `off` | v5.13.0 起。客戶驗收不回歸閘：`on` 時會改程式或資料的工單多一段〈相關通過案例〉，Worker 動工前逐案判定，會改變通過案例就停下交你決定。專案進入客戶驗收、有驗收案例表時才開 |
  | `research_interaction` | `true`／`false` | `true` | 研究型工單是否允許 Worker 互動；yolo 下一律不互動、改問塔台 |
  | `research_max_questions` | `1`–`5` | `3` | 研究型工單 Worker 每次提問的上限 |
  | `auto_commit` | `on`／`ask`／`off` | `ask` | 塔台直接處理小變動後的 commit 行為；只對「小且無邏輯變動」的修改生效 |
  | `auto_commit_format` | 字串模板 | `"chore: {description} ({scope})"` | 塔台自主 commit 的訊息格式 |
  | `worker_max_retries` | `1`–`10` | `3` | Worker 熔斷上限，同一問題連續失敗達此次數即三振 |
  | `worker_strikeout_action` | `block`／`warn` | `block` | 三振後：`block` 強制收尾回報；`warn` 警告、由你決定（yolo 下照 `block`） |
  | `worker_commit` | `required`／`recommended`／`off` | `required` | Worker 收尾的 commit 政策；`ct-done` 也依此檢查 |
  | `worker_auto_close` | `off`／`done` | `off` | `done` = 工單 `DONE` 且不 Renew、收單確認後請 BAT 回收 Worker 分頁 |
  | `worker_close_delay` | `0`–`300`（秒） | `10` | 回收前的延遲；期間只有你在該分頁的輸入會取消回收 |
  | `workflow_integration` | `off`／`ask`／`on` | `on` | Claude Code Workflow 的整合強度：`off` 不建議也不授權；`ask` 每次授權前問你；`on` 知識卡到 ⭐ 之前問你 |

  Worker 只會讀 `worker_max_retries`、`worker_strikeout_action`、`worker_commit` 與 `experience-level` 這類調諧參數；`worker_auto_close`、`worker_close_delay` 雖然以 `worker_` 開頭，卻是塔台收單時讀的。

  `_tower-config.yaml` 另有 `gp-prefix`（Playbook 的 GP 編號前綴），但它不是 `*config` 選項，所以不在上表；定義與未設定時的 fallback 見 `multi-tower-protocol.md` § `gp-prefix` 設定（唯一權威定義）。

- **起始版本**：v3.2.0（各選項的版本見權威出處）
- **權威出處**：`control-tower/references/tower-config.md` § `*config` 命令、§ 可用選項、§ 作用域與持久化
- **相關**：[功能總覽 › 設定](/features#config)（四層覆蓋的概念）

### `*help` {#help}

- **語法**：`*help`、`*help <主題>`
- **主題**：`commands`（所有指令的用途與使用位置）、`workflow`（日常開發、中斷恢復、Sprint 結束）、`config`（設定與持久化）、`workorder`（工單生命週期與狀態流轉）、`status`（紀錄在哪裡）、`tips`（怎麼表達需求、確認理解）。
- **做什麼**：不帶參數時顯示精簡的指令速查；帶主題時在塔台 session 裡回答，**不切換角色**，回答完繼續塔台的工作。完整的使用指南用 [`/ct-help`](#ct-help)。
- **起始版本**：v3.2.0
- **權威出處**：`control-tower/references/tower-config.md` § `*help` 命令

### `*sync` {#sync}

- **語法**：`*sync`
- **做什麼**：列出所有工單，讀每張的 metadata，交叉比對**塔台記憶、工單檔、`sprint-status.yaml`** 三方，以工單檔為唯一事實來源修正差異，顯示同步摘要。啟用了 BUG／PLAN 時一併掃描並重建 `_bug-tracker.md` 與 `_backlog.md`；不掃冷區。`auto_archive_prompt: on` 時，結尾提示歸檔候選數量。
- **v5.13.0 起多做的事**（都只多印一行，不阻擋）：
  - 量熱檔大小（`_tower-state.md`、`_decision-log.md`、`_bug-tracker.md`、`_backlog.md` 等，以及熱區單據檔），超過 400 KB 預算或 BAT 的 512 KiB 讀檔上限時提示，並指出怎麼收斂（見[觀測與改進 › BAT 塔台面板為什麼會空](/deep/features/observability#bat-panel)）。
  - 啟用 BUG 追蹤時，未結 BUG 張數或久未更新的天數超過門檻（`bug_review_open_threshold`、`bug_review_stale_days`），就建議照結案判準逐張核對（見 [BUG 結案判準](/deep/features/record-types#bug-closing)）。
  - 決策日誌的格式驗證多檢查 BAT 讀不讀得到（表頭 `ID`、每列以 `|` 開頭與結尾、標題格式）和檔案大小。
  - 索引格式照新規則重建；舊索引在下一次 `*sync` 時換成新格式。塔台改了 BUG／PLAN 狀態，同一批就重建索引，不等下一次 `*sync`。
- **起始版本**：v3.2.0（多類型掃描：v4.0.0；大小提示、未結 BUG 提示：v5.13.0）
- **權威出處**：`control-tower/references/work-order-system.md` § sprint-status.yaml 同步；`control-tower/references/bug-plan-system.md` § 索引格式、§ 未結 BUG 清理提示；`control-tower/references/decision-log-system.md` § 格式驗證；`control-tower/references/memory-protocol.md` § BAT 塔台面板讀取契約 › 大小預算；`control-tower/references/archive-system.md` § 與 `*sync` 的協作

### `*pause [原因]` {#pause}

- **語法**：`*pause [原因]`，例如 `*pause 正式版的登入 API 回 500`
- **做什麼**：不管塔台正在說什麼，立刻：凍結進行中的工單（狀態改成 `PAUSED`，記下原因與時間）→ 記進 `_tower-state.md` → 評估緊急任務的範圍與要不要另開分支 → 開一張標成 `URGENT` 的緊急工單 → 把原工單排進回歸佇列。在 yolo 派工前的緩衝時間裡輸入，也能手動介入。v5.13.0 起，寫 `_tower-state.md` 時同一次寫入更新檔頭的機器可讀摘要，BAT 指揮塔總覽跟著更新。
- **起始版本**：v3.2.0
- **權威出處**：`control-tower/references/interrupt-protocol.md` § 中斷協議

### `*resume [工單編號]` {#resume}

- **語法**：`*resume`（自動找最近一張 `PAUSED` 工單）、`*resume T0005`（恢復指定工單）
- **做什麼**：把暫停的工單接回來，並顯示當時的上下文摘要。v5.13.0 起，清除 `_tower-state.md` 的暫停紀錄時同一次寫入更新機器可讀摘要。
- **起始版本**：v3.2.0
- **權威出處**：`control-tower/references/interrupt-protocol.md` § HOTFIX 完成後恢復（`*resume`）；`control-tower/references/memory-protocol.md` § 機器可讀摘要（YAML frontmatter）

### `*bug` {#bug}

- **語法**：`*bug [標題]`，例如 `*bug 登入頁面白屏`
- **前提**：`enable_bug_tracking: true`。沒啟用時，回報 bug 照一般工單（`T####`）處理。
- **做什麼**：互動登記 BUG 單 `BUG-###-<描述>.md`。最少要有標題、嚴重度與現象（預期與實際行為）；塔台會用選項問嚴重度、能不能重現、有沒有替代做法，並關聯相關工單。
- **起始版本**：v4.0.0
- **權威出處**：`control-tower/references/bug-plan-system.md` § BUG 單據

### `*plan` {#plan}

- **語法**：`*plan [標題]`，例如 `*plan 重構 API 層`
- **前提**：`enable_plan_tracking: true`。
- **做什麼**：登記規劃或想法 `PLAN-###-<描述>.md`。最少要有標題與一句話的動機；塔台會問優先級與類型（功能想法、技術改善、架構調整、其他）。
- **起始版本**：v4.0.0
- **權威出處**：`control-tower/references/bug-plan-system.md` § PLAN 單據

### `*exp` {#exp}

- **語法**：`*exp [描述]`，例如 `*exp 嘗試 WebSocket`
- **前提**：`enable_experiments: true`。
- **做什麼**：登記實驗單 `EXP-<TOPIC>-###-<描述>.md`（每個 TOPIC 各自編號）。最少要有 TOPIC 名稱與一句話的實驗假設；塔台會引導你在獨立的 git worktree 裡做實驗。實驗的狀態是 `EXPLORING` → `CONCLUDED` 或 `ABANDONED`。
- **起始版本**：v4.0.0
- **權威出處**：`control-tower/references/bug-plan-system.md` § EXP 實驗單據

### `*archive` {#archive}

- **語法**：

  | 語法 | 行為 |
  |---|---|
  | `*archive` | 掃描熱區 → 列出候選 → 確認後批次 `git mv` 到 `_archive/` |
  | `*archive --dry-run` | 只列出候選，不執行 |
  | `*archive T0001` | 強制歸檔指定單據（跳過天數與引用檢查） |
  | `*archive --search <關鍵字>` | 在冷區搜尋已歸檔的單據 |
  | `*archive --restore T0001` | 從冷區取回到熱區 |

- **做什麼**：最終態、而且超過 `archive_days` 天的單據才是候選；還被進行中的單據引用的會被豁免。
- **起始版本**：v4.0.0
- **權威出處**：`control-tower/references/archive-system.md` § `*archive` 命令

### `*evolve` {#evolve}

- **語法**：

  | 語法 | 行為 |
  |---|---|
  | `*evolve [主題]` | 從最近的工單萃取學習，寫入 `_learnings.md` |
  | `*evolve --playbook [名稱]` | 從驗證過（🟢 以上）的學習晉升成 Playbook，寫入 `_playbooks/`；會先問寫到專案還是全域 |
  | `*evolve --skill [名稱]` | 只產出 skill brief，提示你用 `skill-creator` 把 Playbook 永久化 |
  | `*evolve --status` | 顯示知識成熟度統計面板 |

- **起始版本**：v3.2.0（`--playbook`／`--skill`／`--status`：v4.0.0）
- **權威出處**：`control-tower/references/playbook-engine.md` § `*evolve` 擴展子命令；`control-tower/references/self-learning-core.md`

#### `*evolve --workflow [名稱]` {#evolve-workflow}

- **做什麼**：轉交給 [`/ct-evolve --workflow`](#ct-evolve)：只產 Workflow brief 與 🔵 知識卡，不寫 `.claude/workflows/`、不執行 Workflow。塔台不另做一套。
- **起始版本**：v5.11.0
- **權威出處**：`control-tower/references/playbook-engine.md` § `*evolve` 擴展子命令；`ct-evolve/SKILL.md` § Promotion Modes

### `*insights` {#insights}

- **語法**：`*insights`
- **做什麼**：在塔台角色裡，依 session 與工單歷史做有證據的使用模式分析，不離開塔台。完整報告用 [`/ct-insights`](#ct-insights)。v5.13.0 起，未結 BUG 超過門檻時，報告也帶和 `*sync` 同一行的清理提示。
- **起始版本**：v3.4.0
- **權威出處**：`control-tower/SKILL.md` § Built-In Commands；`ct-insights/SKILL.md` § Scope；`control-tower/references/bug-plan-system.md` § 未結 BUG 清理提示

#### `*insights workflow [T#### …]` {#insights-workflow}

- **語法**：`*insights workflow`、`*insights workflow T0123 T0124`
- **做什麼**：執行 `ct-insights` 附帶的預篩腳本，做排除守門（不適合用 Workflow 的直接排除；重複出現在工單之間的序列建議改成 Playbook）與附證據位置的按需提示。**只提示，不標記也不修改工單**；提示仍要人工複核。塔台要把 Workflow 授權寫進工單之前，還要先看 `workflow_integration` 的設定。
- **起始版本**：v5.11.0
- **權威出處**：`ct-insights/references/analysis-rules.md` § 預篩腳本：排除守門與按需提示（v5.11.0+）；`control-tower/references/workflow-engine.md` § `workflow_integration` 的行為（v5.11.0+）

### `*fieldguide` {#fieldguide}

塔台只做**讀取與分析**，不直接寫 FIELDGUIDE.md；需要改檔的都開成工單，交給 `/ct-fieldguide` 在 Worker session 執行。

| 子命令 | 什麼時候 | 塔台做什麼 | 產出 |
|---|---|---|---|
| `scan [N]` | 事後 | 讀最近 N 張（預設 5）已完成工單的回報區，提取 coding 標準候選 | 更新工單 → `/ct-fieldguide update` |
| `add [主題]` | 日常 | 互動式把你的判斷整理成決策樹 | 更新工單 → `/ct-fieldguide update` |
| `audit [模組]` | 主動盤點 | 確認範圍，比對 FIELDGUIDE 與實際程式碼 | 盤點工單 → `/ct-fieldguide audit` |
| `init` | 新專案 | 偵測全域種子與技術棧 | 初始化工單 → `/ct-fieldguide init` |
| `debt [主題]` | 技術債 | 找出同一議題有多種做法的地方 | 盤點工單 → `/ct-fieldguide audit --debt` |
| `design` | 視覺規範 | 檢查 DESIGN.md 狀態，建議下一步 | 狀態報告，或工單 → `/ct-fieldguide design` |
| `design generate` | 視覺規範 | 產生從程式碼擷取 DESIGN.md 的工單 | 擷取工單 → `/ct-fieldguide design` |
| `design check` | 一致性 | 快速比對 DESIGN.md 與程式碼 | 差異報告 |

- **起始版本**：v3.5.0（`design` 系列：v3.6.0）
- **權威出處**：`control-tower/references/fieldguide-commands.md` § 命令總覽

### `*import` {#import}

- **語法**：

  | 語法 | 行為 |
  |---|---|
  | `*import rule` | 互動式新增一條本地規則：讀取現有 → 衝突分析 → 確認 → 寫入 |
  | `*import playbook` | 互動式新增 Playbook，流程同上 |
  | `*import --from <檔案>` | 從指定檔案匯入（草稿，或另一個專案的 `_local-rules.md`） |
  | `*import --check` | 查看目前設定狀態（本地規則與學習紀錄概覽） |
  | `*import --fix` | 修正格式錯誤，保留內容 |

- **做什麼**：安全地合併 local rules、Playbook 與設定；有一組不可覆寫的硬限制。`*import` 管規則與學習紀錄，`*config` 管執行時的設定。
- **起始版本**：v4.0.0
- **權威出處**：`control-tower/references/safe-import.md` § 命令語法、§ 安全原則（硬限制）

### `*onboard` {#onboard}

- **語法**：`*onboard`（可以重複執行）
- **做什麼**：塔台切換成工作流程教練，用問答探索 5 個主題：Git 工作習慣、哪些小事不需要開工單、Worker 工單結束後的 Git 行為、遇到不清楚的問題怎麼辦、塔台與 Worker 的邊界；最後產出個人化的 `_local-rules.md`，透過 `*import` 安全合併。
- **起始版本**：v4.0.0
- **權威出處**：`control-tower/references/onboarding.md`

## 對話慣用語 {#phrases}

這些不是指令，而是 CT 會辨認的固定說法。

### yolo 中斷詞 {#yolo-stop}

- **說法**：在塔台 session 裡單獨輸入 `停`、`stop` 或 `abort`（整則訊息只有這個詞，不分大小寫）。
- **效果**：塔台顯示 `🛑 YOLO PAUSED — 使用者中斷`，擱置下一張派工，等你的指令。這是你主動觸發的，**不算斷點**，也不佔 `yolo_max_retries` 的次數。
- **另外**：yolo 每次派下一張之前，會先顯示派工面板並等 1–2 秒，讓你有時間按 Ctrl+C 或輸入 `*pause` 介入。
- **權威出處**：`control-tower/references/yolo-mode.md` § 使用者中斷（非斷點）、§ 派發下一張時的回報面板

### Renew 觸發詞 {#renew}

- **說法**：塔台在工單裡加了「塔台補充（Renew #N）」之後，回到**原本的 Worker 分頁**說「重讀工單」「renew」「塔台有新指示」或「工單已更新」。
- **效果**：Worker 重讀工單，只讀最新的那一段 Renew，向你確認補充內容與新指示後接著做，不重置已完成的工作，收尾時在回報區記下 Renew 歷程。在原分頁繼續時，塔台不會回收這個分頁。
- **權威出處**：`control-tower/references/research-workorder.md` § Renew 機制（F-07）

### 回報字串 {#report-strings}

Worker 收尾時送回塔台的是固定的一行，前面是工單的**完整 ID**。下表的 `T####` 代表訊息的種類，實際送的是收到的那個 ID，設了前綴就含前綴（例 `CP-T0113 完成`）；v5.13.1 起 Worker 送出前會和工單 frontmatter 的 `id` 比對，不一致就改用 `id`。

| 字串 | 什麼時候 |
|---|---|
| `T#### 完成` | `DONE` 或 `FIXED` |
| `T#### 部分完成` | `PARTIAL` |
| `T#### 需要協助` | `BLOCKED` 或 `FAILED` |
| `T#### 提問` | 只在 yolo：工單仍是 `IN_PROGRESS`，Worker 有問題在等塔台答覆，**不是收尾** |

yolo 下塔台另外也接受 `T#### 失敗`。不是這些格式的訊息，會觸發斷點 A。

漏了前綴的回報（例 `T0113 完成`，熱區只有 `CP-T0113`）格式仍然合法，不算斷點 A：塔台在熱區恰好找到一張「前綴＋同號」的工單時，就當成那一張收單，並記一行「回報 ID 缺前綴」；同號的有好幾張或找不到，才停下來問你。這只保住塔台收單，BAT 能不能把 Worker 分頁標成 Done，仍看 Worker 送的 ID。

- **權威出處**：`ct-exec/SKILL.md` § BAT Notify And Fallback；`control-tower/references/work-order-system.md` § 回報與通知用的工單 ID、§ 回報處理流程 › 回報 ID 對不上時；`control-tower/references/yolo-mode.md` § 斷點 A：Worker 回報非預期狀態

## 不要找：不存在或已刪除的指令 {#not-commands}

| 你可能在找 | 實際情況 |
|---|---|
| `*dispatch` | **不存在**。派工是開單之後的一個步驟，依 `auto-session` 自動派，或塔台給你指令自己開 |
| `*help roles` | 職責速查卡，**已在 v5.0.3 刪除** |
| 粒度分析卡 | 塔台輸出的任務規模分析卡，**已在 v5.0.3 刪除**；粒度原則保留在工單粒度原則裡 |
| `*status` | 不是塔台內建命令。查狀態用 [`/ct-status`](#ct-status)，同步用 [`*sync`](#sync) |
| `*fieldguide design init`、`design url <網址>`、`design refresh` | 舊版子命令，不在現行版本；從網站擷取改用 [`/ct-fieldguide design`](#ct-fieldguide) |
| `REVIEW`、`TODO` 狀態 | 不是現行的工單狀態；需要審查就另開一張審查工單 |

## 延伸閱讀 {#further}

- `control-tower/SKILL.md` § Built-In Commands
- `ct-help/SKILL.md` § Command Families
- 各 skill 的 `SKILL.md`（`ct-exec`、`ct-done`、`ct-status`、`ct-evolve`、`ct-insights`、`ct-fieldguide`、`control-tower-guide`）
- CT 安裝與使用指南 § 13. Config 速查表（v5.13.1）、§ 14. 命令速查表（v5.13.1）
- `control-tower/references/tower-config.md` § `*config` 命令、§ 可用選項（表下註明 `gp-prefix` 不是選項）
- `control-tower/references/multi-tower-protocol.md` § `gp-prefix` 設定（唯一權威定義）
- `control-tower/references/fieldguide-commands.md`
- `control-tower/references/playbook-engine.md` § `*evolve` 擴展子命令
- `control-tower/references/yolo-mode.md` § 使用者中斷（非斷點）
- CT Guide `references/ecosystem.md` § 三軌前綴：`*`、`/`、`$`

Portal 是摘要，不具權威；與 reference 有出入時，以 reference 為準。
