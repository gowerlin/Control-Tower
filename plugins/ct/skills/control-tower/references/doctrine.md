# CT 設計依據（Doctrine）

> **目的**：給已讀過 `SKILL.md` 但不知道「為什麼 CT 這麼設計」的新 consumer / 新 skill 設計者閱讀。本文件聚合並重構 CT 背後的思維模型，不重複 `SKILL.md` 的指令用法、不重複 `CHANGELOG.md` 的版本紀錄，只回答**設計依據**這一個問題。
>
> **寫作立場**：客觀描述設計決策與其成因，不代任何個人觀點發言。所有論述均可回溯到本 repo 既有 artifacts（工單、skill 檔、決策日誌、`*evolve` 產出）。

---

## 前言：為什麼需要這份文件？

閱讀 `SKILL.md` 可以學會「怎麼用 CT」，但無法回答以下這類問題：

- 為什麼 CT 選擇 `.md` 檔案當工單載體，而不是某種 in-memory orchestrator？
- 為什麼要維護 `_tower-state.md`，直接掃 git log 不行嗎？
- 為什麼工單要切成三層資料結構（`_ct-workorders/` / `_learnings.md` / `fieldguide/`），不能用單一資料夾？
- 為什麼 `*evolve` 的輸出要拆成 tactical 和 strategic 兩類歸檔？
- 為什麼要給工單 metadata 加 `intervention_type`、`affects_files`、`spec_level_check` 這些欄位？

這些問題的答案散落在各個 skill 檔的「背景」段、`_decision-log.md` 的歷史決議、以及 `*evolve` 累積的 strategic learnings。新加入的 consumer 若要從頭拼湊，成本很高。

本文件把那些散落的論述**聚合**起來，用**一個統一的思維模型**解釋 CT 為什麼長這個樣子。核心論點只有一句：**CT 不是 workflow 工具，是一套小型的認知作業系統（Cognitive OS）**。

> **與 Claude Code Workflow 的關係（v5.10.0+）**：Workflow 是 **Worker 在單張工單內的執行方式，不是 CT 的編排層**。
> CT 仍然只用檔案驅動的工單編排工作（派工、跨 session、人工把關由工單和 Playbook 負責）；
> Workflow 只在一張已派出的工單之內，由 Worker 決定子任務怎麼並行、怎麼互相驗證。所以上一句仍然成立。
> 三分法、規則與成熟度見 [workflow-engine.md](workflow-engine.md)（唯一權威）。

---

## 第一原則：Memory Hierarchy 同構

CT 全部設計依據可以從一個同構關係推導出來：

| 傳統作業系統 | CT 對應物 |
|-------------|----------|
| Disk | Filesystem（工單檔案、learnings、fieldguide） |
| RAM | Context window |
| Stateless process | 每次 LLM call |
| IPC pipe | Worker 之間透過 artifact 檔案傳遞資料 |
| Memory hierarchy（L1/L2/L3 cache） | CT 三層資料結構 |

這不是比喻，是**同構（isomorphism）**。兩邊遵循相同的結構約束：

1. **容量有限 × 速度有限的權衡**：Context window 有上限，RAM 也有上限。存在 context 裡的資料拿得快，存在 disk 上的拿得慢。
2. **Stateless 執行單元 + 外部持久化**：每次 LLM call 是獨立 process；必須靠 disk 上的 artifact 維持跨 session 狀態。
3. **Shared resource 的協調成本**：多個 process 競爭同一個 shared resource 時會產生 lock／conflict；多個 Worker 同時讀寫同一區檔案也會。

從這個第一原則出發，CT 的幾個關鍵決策就不是「偶然的直覺」，而是**同構約束下幾乎必然的選擇**。

### 設計決策對應表

| CT 設計 | 同構解讀 |
|---------|---------|
| Worker 無狀態、塔台有狀態 | 對應「stateless process + persistent orchestrator」的分工 |
| 工單用 `.md` 檔案而非 inline 對話 | 對應「disk 上的 artifact 是跨 process 唯一可靠的共享介面」 |
| `_tower-state.md` 持久化 | 對應「episodic memory 必須外部化，否則 RAM 清空即遺失」 |
| 塔台不直接改程式碼、只派工 | 對應「kernel 不做 user-space 的事，只做排程與資源配置」 |
| Worker 回塔台只帶結構化摘要，不帶推理全文 | 對應「syscall 回傳 result code，不回傳整個 process 的 memory dump」 |

**CT 實例錨點**：v4.3.0 的 `BUG-041` 閉環把 `CT_MODE` 從 config 檔改為透過 `--mode` flag 顯式傳遞——這一改動的本質就是**把 runtime mode context 從 disk（config file）搬到 argv（process 參數）**，確保 Worker 完全無狀態、完全不讀 config。D062「Worker 無狀態原則」即為此同構關係的正式化。

---

## CT 三層資料結構的設計依據

CT 的資料層分三層，對應 cache hierarchy 的容量 × 速度權衡：

| 層級 | 實體位置 | 類比 | 特性 |
|------|---------|------|------|
| L3 | `_ct-workorders/` | 硬碟 | 容量大、全量保存、讀取成本高 |
| L2 | `_learnings.md`（distilled） | L2 cache | 中等容量、去蕪存菁、供塔台查閱 |
| L1 | `fieldguide/` | L1 cache / 熱區 | 容量小、高頻命中、塔台啟動即讀 |

### 為什麼不能只有一層？

若只保留 `_ct-workorders/`：塔台每次啟動都要掃所有工單才能回答「最近解過什麼類似問題」，context window 會被原始事件紀錄塞爆，留給判斷的 germane load 被壓縮到幾乎為零。

若只保留 `fieldguide/`：熱區容量太小，無法保存完整脈絡；一旦某個決策的細節被問到「當初為什麼這麼決定」，找不到原始證據。

### 三層的流動方向

```
L3 （工單事件）─ *evolve distillation ─▶ L2 （learnings）─ promotion ─▶ L1 （fieldguide）
```

**CT 實例錨點**：
- L3→L2：`T0104` 強化 `*evolve` prompt 的 distillation 步驟，確保從事件紀錄萃取出「因果」而非「時間軸」。
- L2→L1：`T0105` 把 `*evolve` 輸出拆成 tactical / strategic 兩類，前者留在 L2 當參考、後者在累積到一定成熟度後晉升 L1 fieldguide。
- L3 本身：`_ct-workorders/` 底下每張工單都有完整的「任務指令 → 回報區」結構，對應 disk 上的 block storage。

### 與「塔台不直接看 git log」的關聯

Git log 記錄的是「code change 的時間軸」，屬於 episodic、粒度偏低、沒有因果萃取。若塔台直接看 git log 代替 `_tower-state.md`，等於放棄 L1/L2 只靠 L3 原始資料——違反 memory hierarchy 的基本原則。

`_tower-state.md` 存在的理由是：把跨 session 的**決策狀態**（哪些工單開著、哪些卡住、哪些等驗收）壓縮到一份可在塔台啟動瞬間掃完的摘要。這是 L1 熱區的一種形式。

---

## 工單狀態機的設計依據

每張工單有 `status` 欄位（如 `PENDING` / `IN_PROGRESS` / `DONE` / `BLOCKED`；完整允許值以 [work-order-template.md](work-order-template.md) § `status` 為唯一權威定義），配合 `開始時間` / `完成時間` 時戳。這個設計不是為了「好看」或「排版」。

### 為什麼要顯式狀態欄位？

塔台的核心職責之一是 `*sync`（任何 session 查狀態則用 `/ct-status`）——在 session 啟動時快速判斷「全局進度到哪裡」。若狀態只能從工單全文推斷（看有沒有填完成時間、看回報區有沒有內容），塔台必須**全文讀取每張工單**才能判斷，掃描成本從 `O(1) per work order` 膨脹到 `O(n) per work order`，在工單數量增加後會壓垮 context budget。

顯式狀態欄位把這個判斷變成 **O(1)**：塔台只需讀元資料區前 20 行即可分類，省下的 context budget 留給真正需要推理的工單。

### 為什麼要反序寫入？

Worker 在 `ct-exec` 收尾時嚴格遵守以下順序（唯一權威是 `ct-exec/SKILL.md` § Phase 4；本節只說明為什麼）：

1. 先 commit 產品變更（依 commit 政策），回報區才能記下 commit hash
2. 填回報區（完成狀態文字、產出摘要、互動紀錄、commit hash）
3. 回報區完成**之後**，才修改最終狀態（如 `DONE`）與完成時間
4. commit 工單檔（依 commit 政策）
5. 最後才通知塔台

> 演進：本節在 v4.4.0 寫成時的順序是「回報區 → commit → 最後改狀態」；v5.7.0 起統一成上面的順序（隔離工單本來就是這樣）。
> 變的是 commit 的位置與「通知前先 commit 工單」，「回報區完成後才改狀態」這一點沒有變。

原因是**避免 file watch race condition**：若塔台或其他工具監聽工單狀態變化，先改狀態再填回報區會讓外部讀到一張「狀態 DONE 但回報區空白」的殘缺工單。反序寫入保證「外部看到 DONE 的那一刻，回報區已完整」——這是 filesystem-as-IPC 情境下的 happens-before guarantee。

**CT 實例錨點**：`ct-exec/SKILL.md` § Phase 4（Report And Commit）明文規定寫入順序與收尾自檢，commit 規則（含 `worker_commit` 政策分流）在同節 › Commit rules。這不是 Worker 的個人風格，是 CT filesystem-as-IPC 模型下的協定要求。

---

## Episodic vs Strategic vs Tactical 的分流

Memory 可以分四類（Semantic / Episodic / Procedural / Strategic），CT 對前三類都有成熟載體（`SKILL.md` / 工單歸檔 / skill command 檔）。關鍵分歧在**第四類 Strategic Memory 的正確形態**。

### Strategic Memory ≠ Episodic Memory

| | Episodic | Strategic |
|---|---------|-----------|
| 內容 | 事件紀錄 | 因果萃取 |
| 舉例（事件） | 「T0038 部署後流量尖峰觸發 thundering herd」 | 「fixed interval retry 在流量尖峰會 thundering herd → 改用 exp backoff + jitter」 |
| 價值 | 可追溯 | 可重用 |
| 時間耦合 | 強耦合（日期、人、場景） | 去耦合（只保留因果結構） |

Strategic Memory 是**蒸餾過的** episodic memory。很多團隊的「事後檢討文件」看了沒用，因為它們停在 episodic 層級，沒做到 distillation。

### 為什麼要再拆 Tactical vs Strategic？

即使做到了 distillation，萃取出來的 learning 也有粒度差：

| 類型 | 範疇 | 跨技術棧 robustness | 用途 |
|------|------|----------------------|------|
| Tactical | 下次執行這類工單怎麼改進 | 低（換技術棧就失效） | 短期 workflow 微調 |
| Strategic | CT 設計在這類場景暴露的假設是什麼 | 高（跨技術棧都有效） | 長期架構演化 |

若不拆分，高價值的 strategic insights 會被大量 tactical tips 淹沒。塔台在 `*evolve` 之後讀 `_learnings.md` 時，每條 learning 要花同等 context 成本，但產出價值天差地別——這就是 extraneous cognitive load 的典型形態。

**CT 實例錨點**：
- `T0100`：audit `*evolve` 最近輸出的 episodic/strategic 比例，量化當前 distillation 品質。
- `T0104`：強化 `*evolve` prompt 的 distillation 步驟，把「時間軸描述」推向「因果萃取」。
- `T0105`：把 `*evolve` 輸出拆成 tactical / strategic 兩類分別歸檔，讓兩者的讀取成本與使用情境解耦。

---

## Double-loop Learning 在 CT 的體現

組織學習區分兩種 loop：

| | Single-loop | Double-loop |
|---|------------|-------------|
| 修正對象 | 行動 | 目標 / 假設本身 |
| 問題範例 | 「spec 寫太模糊，下次寫清楚」 | 「對 agent 分工的假設錯了，task boundary 要重定義」 |

大多數團隊做到 single-loop 就停了。Double-loop 難在它要質疑**系統本身的設計假設**，而不只是「我這次做得好不好」。

### `*evolve` 作為正式觸發器

CT 透過 `*evolve` 命令把 double-loop 從「偶然的反省」升級為**定期的正式流程**：

```
執行工單 ──▶ *evolve 萃取模式 ──▶ 更新 template / skill ──▶ 下次執行更好
       ▲                                                         │
       └─────────────────────────────────────────────────────────┘
```

這個 loop 本身是 single-loop（改 template 還在「怎麼做得更好」層級）。要進入 double-loop，`*evolve` 的輸出必須回答更深的問題：

- 「Tower / Worker 分工方式，對某類專案（例如純文件專案）是不是不適用？」
- 「某些 brownfield 專案是不是根本不適合工單制？」
- 「`_tower-state.md` 的檔案格式，對高頻更新場景（一天數十次狀態變化）是不是不夠好？」

這些問題會質疑 CT **自身的設計假設**。前述 tactical / strategic 分流（T0105）正是為了讓這類深層問題有獨立歸檔位置，不會被日常 workflow 微調覆蓋。

**CT 實例錨點**：
- `T0098`（本系列 meta-PLAN）本身就是一次 double-loop——質疑「工單 metadata 是否足夠支持平行派發與架構決策預警」這個假設。
- `T0099`（audit `_tower-state.md` 資訊密度）是對「state file 長期累積是否擠壓 germane load」的設計假設再驗證。

---

## `intervention_type` / `affects_files` / `spec_level_check` 的設計依據

v4.4.x 系列工單 metadata 加了三個欄位。每一個都對應一個具體的 cognitive load 或協調風險問題，不是裝飾。

### `intervention_type`：降低 cognitive load

三種值對應三種介入成本：

| 類別 | 介入時機 | 對應 cognitive load |
|------|---------|---------------------|
| `fire-and-forget` | 0 次 | 幾乎不佔 working memory |
| `context-dependent` | 1 次（讀前序產出） | 少量 germane load |
| `decision-requiring` | 中途 N 次 | 大量 germane load |

**軸線翻轉的意義**：傳統 agent 分類看「agent 內部構造」（有無記憶、有無目標）；CT 的分類看「對協調者的介入成本」。這個視角才是 orchestrator 視角——**agent 是什麼不重要，重要的是 agent 對塔台是什麼成本**。

加入這個欄位後塔台可以做三件新事：

1. **平行化策略**：`fire-and-forget` 類別可多工單併發，`decision-requiring` 必須序列。
2. **Standby 預告**：發現工單鏈裡有 `decision-requiring`，提前通知使用者「等下要做架構決策」。
3. **Sprint 資源估算**：`decision-requiring` 佔比高的 sprint，實際產出速度會被使用者 availability 卡住，不是被 AI 卡住。

**CT 實例錨點**：`T0102`（Phase 2 落地該欄位到工單模板）。

### `affects_files`：避免平行派發規格錯配

平行工單之間若有 file overlap，可能導致互相覆蓋或 merge conflict。多 agent 系統中此成本會被乘法放大，符合「模糊規格在平行執行時會被乘法放大」的普遍規律。

`affects_files` 讓塔台在派工前做 **static overlap check**（純機械比對 glob pattern，不需要 LLM 介入）：

- 兩張工單的 `affects_files` 集合有交集 → 警告並要求序列化或拆單。
- 完全不交集 → 可安全平行。

**為什麼是 static 而非 dynamic？** Dynamic watcher（runtime 監聽檔案變化）會引入額外的 orchestration 成本，且 false positive 比例高（touch 檔案不等於 logic conflict）。Static pre-check 用 glob pattern 的集合交集判斷即可涵蓋 95% 情境，剩 5% 的 semantic conflict 本來就需要人工標記。

**CT 實例錨點**：`T0103`（Phase 2 落地 `affects_files` metadata 和塔台 static overlap check）。

### `spec_level_check`：避免平行派發前 spec 錯配

工單是否「spec 寫得夠具體」決定 Worker 能否獨立完成。Spec 有三層：

| 層級 | 範例 | 誰寫 |
|------|------|------|
| 產品意圖 | 「付款失敗要自動重試」 | 規劃者 |
| 架構邊界 | 「retry 放 client wrapper、exp backoff、max 3、超過發 event」 | 塔台或架構者 |
| 實作細節 | retry library 選擇、error code mapping、timeout 數值 | Worker |

**Spec 應該停在架構邊界層**。再往下寫是浪費（奪走 Worker 的決定空間），再往上停是危險（Worker 必須猜）。

`spec_level_check` 的自問清單強制工單作者確認：

```markdown
- [ ] 是否定義了 interface contract？
- [ ] 是否定義了 error handling strategy？
- [ ] 是否定義了 boundary condition？
- [ ] 是否留下了實作選擇空間（沒有過度規範）？
```

前三項沒勾 = spec 太淺（Worker 會亂猜）；第四項沒勾 = spec 太深（浪費 Worker）。這個檢查的成本很低（勾四個框），但能攔下多數「工單下去後才發現 spec 不對稱」的情境。

**CT 實例錨點**：`T0101`（Phase 1 落地 `spec_level_check` 欄位）。

---

## 開放問題

以下議題在當前版本尚未有定論，保留給未來的 double-loop 思考：

1. **`_tower-state.md` 的檔案格式會不會在高頻更新場景扛不住？**
   若某個 consumer 的工作節奏達到一天數十次狀態變化，純文字 diff 的成本可能超過 SQLite 這類結構化儲存。是否要保留單一格式，還是允許塔台在不同場景選擇不同後端？目前尚無定論，等累積足夠使用案例再決議。

2. **Fire-and-forget 類工單真的需要塔台介入嗎？**
   若整串工單都是 `fire-and-forget`，塔台的存在價值僅剩「派發與彙總」。此時是否應允許工單直接 trigger 下一張、繞過塔台？yolo 模式已朝此方向演化，但尚未完全放棄塔台中轉。

3. **某些 brownfield 專案是否根本不適合工單制？**
   高度耦合的 legacy code、或需要跨多個模組反覆探索的逆向工程場景，強制走工單制反而會增加 extraneous load。CT 目前沒有「退出工單制、改用自由對話」的正式協定。

4. **Semantic dependency 的自動化上限在哪？**
   `affects_files` 只能涵蓋 syntactic dependency。Semantic dependency（例如 API contract 的設計影響 frontend flow）目前完全靠人工標記。這條線未來是否能部分自動化，仍是開放問題。

---

## 延伸閱讀

本文件只勾勒設計依據的骨架。以下 artifacts 提供更深入的脈絡：

- **CLT × CT 對照分析文件**：本 repo 規劃資料夾中，由獨立分析者撰寫的完整六步拆解，包含 Cognitive Load Theory / Extended Mind Thesis / Double-loop Learning 三套理論框架的原始引述。
- **本次改良 meta-PLAN**：`_ct-workorders/T0098-ct-v44-clt-alignment-meta-plan.md`，把六項改良拆成四個 Phase 的完整規劃。
- **Phase 1-4 各階段工單**：`T0099`（`_tower-state.md` audit）、`T0100`（`*evolve` episodic/strategic audit）、`T0101`（`spec_level_check`）、`T0102`（`intervention_type`）、`T0103`（`affects_files`）、`T0104`（`*evolve` distillation）、`T0105`（tactical/strategic split）、`T0106`（本文件）。
- **塔台決策日誌**：`_decision-log.md`，保留關鍵設計決議的原始動機與替代方案比較。
- **Skill 檔「背景」段**：各 skill（`ct-exec/SKILL.md` / `ct-done/SKILL.md` / `ct-evolve/SKILL.md` / 等）的開頭段落，記錄該命令誕生的具體場景。

---

**版本**：v4.4.0
**最後更新**：2026-04-22
**維護者**：CT skill 主 repo
