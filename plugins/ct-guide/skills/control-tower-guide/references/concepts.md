# Control Tower 核心哲學

## 第一原則：Memory Hierarchy 同構

CT 的設計可以從一個同構關係推導出來——它不是 workflow 工具，而是一套小型的**認知作業系統**：

| 傳統作業系統 | CT 對應物 |
|-------------|----------|
| Disk | Filesystem（工單檔案、learnings、fieldguide） |
| RAM | Context window |
| Stateless process | 每次 LLM call |
| IPC pipe | Worker 之間透過 artifact 檔案傳遞資料 |
| Memory hierarchy（L1/L2/L3 cache） | CT 三層資料結構 |

這不是比喻，是**同構**：兩邊遵循相同的結構約束——

1. **容量 × 速度的權衡**：context window 有上限，RAM 也有上限
2. **無狀態執行單元 + 外部持久化**：每次 LLM call 都是獨立 process，跨 session 的狀態只能靠磁碟上的 artifact
3. **共享資源的協調成本**：多個 Worker 同時讀寫同一區檔案，和多個 process 搶同一個資源一樣會衝突

從這裡出發，CT 的幾個關鍵決策就不是直覺，而是同構約束下幾乎必然的選擇：

| CT 設計 | 同構解讀 |
|---------|---------|
| Worker 無狀態、塔台有狀態 | stateless process + persistent orchestrator 的分工 |
| 工單用 `.md` 檔案而非對話 | 磁碟上的 artifact 是跨 process 唯一可靠的共享介面 |
| `_tower-state.md` 持久化 | episodic memory 必須外部化，否則 RAM 清空即遺失 |
| 塔台不寫程式、只派工 | kernel 不做 user-space 的事，只做排程與資源配置 |
| Worker 回塔台只帶結構化摘要 | syscall 回傳 result code，不回傳整個 process 的 memory dump |

本檔其餘各節，都是這張表的展開。CT 自帶的 `doctrine.md` 是這套論述的上游原文。

## Orchestrator/Worker 分離模式

CT 的骨架是 Orchestrator/Worker 模式：一個中心節點負責協調和決策，多個工作節點負責執行。落到 AI 輔助開發：

- **Orchestrator = 塔台**：一個只負責決策與協調的 AI session
- **Worker**：在獨立 AI session 執行具體工作——可以是 Claude Code，也可以是 Codex
- **通訊橋樑 = 工單（.md 檔案）**：解決 AI 的失憶問題

### Worker 無狀態、塔台有狀態

這是同構原則最直接的落地：

| | 塔台 | Worker |
|---|---|---|
| 持有什麼 | 進度、決策、編號、派工紀錄（`_tower-state.md` 等私有狀態檔） | 只有手上這張工單 |
| 模式從哪來 | 自己的設定（session > project > global > default） | **派工時由塔台傳入**（`CT_MODE`、`CT_INTERACTIVE`） |
| 讀設定檔 | 可以 | 只能讀調諧參數（重試上限、commit 政策），**不得**用來決定 runtime 模式 |

為什麼 Worker 不能自己讀設定檔決定模式？因為設定檔是磁碟上的共享狀態：塔台改了設定、或 Worker 落在另一個專案目錄，
Worker 讀到的就不是塔台派工時的意圖。把模式從「磁碟上的設定」搬到「派工參數」，Worker 才真正無狀態——
同一張工單、同一組參數，在哪個 session 執行都得到相同行為。這條原則在 CT 決策日誌中編號 D062。

## 蜂王模式（Queen Bee Model）

一個直覺的比喻：

| 角色 | 對應 | 職責 |
|------|------|------|
| 蜂王（Queen） | 塔台 Tower | 決策、規劃、協調、派工 |
| 工蜂（Worker） | Worker session | 寫程式、測試、debug、讀檔 |
| 花蜜傳遞 | 工單 .md 檔案 | 雙向溝通橋樑 |

**蜂王不會自己去採花蜜——如果她去了，她就看不到整個蜂巢的全貌了。**

## Hard Boundaries（塔台硬邊界）

塔台的行為邊界在 CT 中稱為 **Hard Boundaries**。社群常把違反它叫「違憲」，這個標籤好記，但內容以 Hard Boundaries 為準：

| # | 邊界 | 為什麼 |
|---|------|--------|
| 1 | 不直接實作產品程式碼、不 debug 原始碼、不讀 raw log、不做大範圍程式碼分析——改派工單 | 保住塔台的 context 給全局判斷 |
| 2 | **不以通用的 agent／task 委派取代工單** | 塔台協調必須是檔案驅動、使用者看得見的；背景委派不留工單、不留回報 |
| 3 | 不寫已安裝的 skill 定義檔（`~/.claude/skills/**`、`~/.codex/skills/**`、plugin cache） | 範圍與唯一例外見 `three-layer-arch.md` § Layer 1 |
| 4 | 未經工單或使用者明文授權，不 push、不 force-push、不 reset hard、不刪分支、不還原使用者的修改 | 不可逆或對外的動作需要明確授權 |
| 5 | 保留無關的未提交變更；塔台自己 commit 小修改時只納入目標檔案 | 不誤帶別人的工作 |
| 6 | `_tower-state.md`、`_decision-log.md`、`_learnings.md`、`_tower-config.yaml`、`_bug-tracker.md`、`_backlog.md`、`_cross-references.md` 是**塔台私有狀態** | Worker 只有在工單明文授權時才能改 |

**唯一的直接處理例外**：單一模組內、**不涉邏輯**的小變動（例如修錯字），塔台可在安全時直接處理，commit 行為依 `auto_commit`。
涉及邏輯、跨模組、或使用者禁止時，一律派工單。

### 為什麼這麼嚴格？

AI 的 context window 是有限的寶貴資源。塔台讀了 500 行程式碼，這 500 行就會持續佔據記憶空間；
工單一多，被程式碼佔據的空間會讓塔台「忘記」更重要的全局資訊——專案目標、進度、已做的決策。

### 常見越界情境

| 情境 | 正確做法 |
|------|---------|
| 使用者貼程式碼進塔台 | 派分析工單，Worker 處理 |
| 塔台回覆出現程式碼片段 | 喊停，塔台已越權 |
| 使用者在塔台問技術細節 | 開獨立 session 或派研究型工單 |
| 塔台想「順手」用背景 agent 查一下 | 不行——開工單，讓使用者看得見 |

AI 天生想「表現得有用」：當你問「這段程式碼什麼意思？」，它會很貼心地去讀——這正是越界。
正確做法是告訴塔台「我需要理解某個模組」，讓塔台派工單。

## Context 衛生原則

塔台的記憶空間必須保留給：

- 全局進度與狀態追蹤
- 決策紀錄與歷史脈絡
- 跨工單的協調資訊
- 學習紀錄與模式辨識

**不應進入塔台的內容**：原始程式碼、完整 log、技術細節、debug 過程。

Worker 端同理：全新任務、改 A 壞 B、AI 在繞圈、同一問題修 3 次以上、審查類工單，都該開新 session 換一個乾淨的 context。

## 檔案驅動設計

CT 用專案內的檔案作為事實來源：

```
_ct-workorders/
├── T0001-任務描述.md      ← 工單（任務指令 + 回報）
├── _tower-state.md         ← 塔台跨 session 記憶
├── _decision-log.md        ← 決策日誌（倒序、append-only）
├── _learnings.md           ← 學習紀錄
├── _tower-config.yaml      ← 專案設定
├── _playbooks/             ← 晉升後的操作範本
└── _archive/               ← 冷區（見下方熱區／冷區）

sprint-status.yaml          ← 進度追蹤（BMad 專案）
```

### 事實來源：兩段式

> **跨來源**：檔案 > 記憶（工單檔案 > `sprint-status.yaml` > 塔台記憶）
>
> **檔案內**：YAML frontmatter（機器 SoT）> body 元資料表（人類鏡像）

第一段解決 AI 失憶：記憶會錯，檔案才算數。第二段解決機器與人類讀同一份檔案的衝突：
機器讀固定格式的 frontmatter，人類讀表格；兩者不一致時以 frontmatter 為準，`*sync` 只警告、不覆寫人寫的表格。
（欄位細節見 `work-order-lifecycle.md`。）

**優勢**：

- 任何新 AI session 讀檔即可接手，解決失憶問題
- Git 版控追蹤所有變更歷史
- 人類可直接閱讀和編輯
- **AI-agnostic**——落地為 Claude Code 與 Codex 都能當 Worker：同一張工單，`/ct-exec` 或 `$ct-exec` 都能執行

## 證據分道

「做完了」需要說清楚是**哪一種**做完。CT 把驗證證據分成獨立的通道，不混為一談：

```
source／docs │ build／test │ runtime │ deploy │ release／安裝包 │ 外部 SIT／客戶確認
```

單元測試通過，不代表 runtime 能動；部署成功，不代表客戶確認。每條通道各自以 `PASS`／`PARTIAL`／`BLOCKED`／`FAILED` 附具體證據回報。
這讓塔台看到 `DONE` 時知道它涵蓋到哪一層，而不是把「測試綠了」誤讀成「已經上線」。

## Control Tower 解決的四個 AI 協作痛點

| 痛點 | CT 的解法 |
|------|----------|
| **Context 污染** | 塔台不碰程式碼，保持記憶乾淨 |
| **AI 失憶** | 工單 .md 持久化，新 session 讀檔即接手 |
| **協調崩壞** | 顯式狀態機 + 進度追蹤 + 派發前 `affects_files` 重疊檢查，防止偏離、重複與互相覆蓋 |
| **Token 浪費** | 工單寫明所有必要資訊，不需重複解釋背景 |

## 多單據類型哲學

只有一種單據 `T####` 時，所有工作——功能開發、bug 修復、規劃討論——全部塞進同一種格式，會帶來：

- **生命週期不匹配**：bug 需要「驗證」步驟，但一般工單沒有
- **語意模糊**：從編號看不出任務性質
- **狀態機過載**：一個狀態機要服務所有場景，變得臃腫

因此 CT 在工單之外提供三種可選單據，各有專屬生命週期：

| 單據類型 | 格式 | 典型場景 | 特色 |
|---------|------|---------|------|
| **T####**（工單） | `T0001-描述.md` | 功能開發、重構、文件更新 | 經典流程 |
| **BUG-###** | `BUG-001-描述.md` | 缺陷修復 | 6 態，FIXED 之後還有 VERIFY |
| **PLAN-###** | `PLAN-001-描述.md` | 規劃、技術評估 | 5 態，含 DROPPED |
| **EXP-[主題]-###** | `EXP-CACHE-001-描述.md` | 技術實驗 | `EXPLORING → CONCLUDED／ABANDONED` |

BUG／PLAN／EXP 預設關閉，需要時在設定中啟用。

**設計原則**：不同性質的工作，用不同的流程管理。就像醫院不會用同一份表格處理門診和手術。

## 熱區／冷區分離

專案推進後，`_ct-workorders/` 會堆積大量已結束的單據。塔台每次同步都掃描它們，但三個月前關閉的 bug 對當前工作毫無幫助。
冷區就放在 `_ct-workorders/` 底下：

```
_ct-workorders/
├── _archive/              ← 冷區
│   ├── workorders/        ← 已歸檔工單（EXP 也放這裡）
│   ├── bugs/              ← 已歸檔 BUG
│   └── plans/             ← 已歸檔 PLAN
├── T0080-新功能.md         ← 熱區
├── BUG-005-修復.md
└── ...
```

**熱區**是日常工作場所；**冷區**是長期記憶，按需查詢。

**歸檔資格**（三關都過才是候選）：

1. **已是終態**——各類單據不同：工單 `DONE`／`FIXED`／`FAILED`／`PARTIAL`（`PARTIAL` 須先覆核 blocker 是否已解除）；
   BUG `CLOSED`／`WONTFIX`；PLAN `DONE`／`DROPPED`；EXP `CONCLUDED`／`ABANDONED`
2. **超過 `archive_days` 天**（預設 **7** 天；`0` = 終態立即可歸檔）
3. **沒有被引用**——豁免是「引用式」而非旗標：仍被進行中單據引用、被 `_tower-state.md` 釘選或在待處理事項中提及、
   跨專案協調中對方尚未完成的單據，都自動豁免

**關鍵設計**：`*sync` 嚴格跳過 `_archive/`，塔台的同步成本不隨歷史單據數量成長。

## 知識成熟度管線

從工單執行中學到的經驗，不該永遠停在零散筆記。CT 定義四級成長：

```
L0 觀察 → L1 驗證 → L2 Playbook → L3 Skill
```

| 等級 | 名稱 | 形式 | 晉升條件 |
|------|------|------|---------|
| **L0** | 觀察 | `_learnings.md` 的觀察紀錄（🔵 new） | 工單執行中發現模式 |
| **L1** | 驗證 | `_learnings.md` 中標記 `validated`／🟢 reliable | 同一模式在 2 張以上工單重複出現，`*evolve` 標記（這是專案層的 🟢；晉升到全域的 🟢 要 2 個以上專案驗證，以 CT `self-learning-core.md` § 置信度系統 為準） |
| **L2** | Playbook | `_playbooks/*.md` 標準操作程序 | validated + 使用者確認，`*evolve --playbook` |
| **L3** | Skill | 永久 skill | playbook 在 3 個以上專案使用 + 使用者決定 |

**管線運作**：

- `*evolve`：萃取觀察，並分類為 Tactical（工具／技術棧相關）、Strategic（跨技術棧仍成立的決策模式）、Episodic（尚未能泛化的原始事件）
- `*evolve --playbook`：把成熟的驗證規則寫成 playbook
- `*evolve --skill`：**只產出 skill brief**（觸發條件、核心流程、所需資源、驗證計畫）；要真正寫成已安裝的 skill，須由使用者明確呼叫 `$skill-creator`／`/skill-creator`
- `*evolve --status`：查看各級數量、過時或重複的 learning、建議的下一步晉升

**設計理念**：知識不該一步到位。觀察先沉澱、驗證，再逐步提煉為正式形式；過早 formalize 只會產生僵化的規範。
L3 停在 brief 而不自動安裝，是因為已安裝的 skill 會被所有 session 載入——那是使用者的決定，不是塔台的。

**Workflow 分支（v5.10.0+）**：有些經驗的形狀不是「一串工單」，而是「一張工單裡的扇出或複核」。這種候選不走 L2 Playbook，
改走 `/ct-evolve --workflow` 寫成 `_workflows/` 知識卡，成熟度同樣分 🔵 → 🟡 → 🟢 → ⭐，但多了「依指標降級」。
怎麼分辨見下一節；權威見 CT `control-tower/references/playbook-engine.md` § 管線總覽 與 `workflow-engine.md`。

## Workflow：單張工單內的執行方式（v5.10.0+）

Claude Code 有一個 **Workflow** 工具：用一支腳本同時派出多個子 agent，平行讀、平行查，最後彙整。
它看起來像是「編排工作」——而 CT 自己就是編排工作的系統。兩者會不會打架？

### 定位：Worker 的工具，不是塔台的編排層

CT v5.10.0 的回答是：**Workflow 是 Worker 在單張工單內的執行方式，不是 CT 的編排層。**

派工、跨 session、人工把關，仍然由檔案驅動的工單和 Playbook 負責；Workflow 只活在一張**已經派出**的工單之內，
由 Worker 決定子任務怎麼並行、怎麼互相驗證。所以本章開頭那句「CT 不是 workflow 工具」仍然成立：
塔台不編排 Workflow，是工單裡的 Worker 選擇用它執行。這和同構的分工一致——塔台管跨 session 的狀態，Worker 管一次執行之內的事。

### 三分法：Skill、Playbook、Workflow

| 產物 | 封裝的是 | 作用範圍 | 判斷問句 |
|---|---|---|---|
| **Skill** | 怎麼做（知識、規範） | 單一 agent | 每個執行者都需要這份知識嗎？ |
| **Playbook** | 工單序列 | 跨工單、跨 session，中間有人把關 | 這是一連串要依序完成、中途要人確認的工作嗎？ |
| **Workflow** | 單張工單內的編排形狀（扇出、驗證、彙整） | 單張工單之內 | 工單裡有執行前就能列出、彼此獨立的同形子任務嗎？或這類工作常被推翻，值得加一層獨立複核嗎？ |

三者可以疊加：Playbook 的某一張工單用 Workflow 執行，Workflow 的每個子 agent 再載入 Skill。

最容易混淆的三件事：

1. **重複發生在工單「之間」，是 Playbook，不是 Workflow。** 一系列探針工單逐張派出、彼此依序，每張自己並不扇出——這是範本化的題目。
2. **工單很小時，扇出沒什麼好處。** 15 分鐘內做得完的工單，平行化省不了多少時間；這時 Workflow 唯一的價值是**驗證**：派獨立的子 agent 複核、從不同角度審查。
3. **工作量大，不代表適合 Workflow。** 一支腳本或一條指令就能跑完的批次，用不著多個 agent；標題寫了 `batch` 也不是訊號。

### 兩種用途

| 用途 | 誰用 | 例子 |
|---|---|---|
| **工具型** | 分析作業（例如 `ct-insights` 讀大量工單歷史） | 語料挖掘：分批全讀 → 結構化分類 → 分群 → 對抗式複核 → 彙整 |
| **派工型** | 一般工單 | 多來源唯讀核對：每個來源一個唯讀子 agent 對照程式碼，Worker 抽查關鍵點後統一寫入 |

兩種都先寫成 brief 與知識卡。派工型怎麼派、Worker 怎麼執行，原本預計 v5.11.0 定案；回測沒過，具名 workflow 的派發延到卡片達 🟡 之後（見下方 § v5.11.0：回測沒過之後，先做便宜的部分）。

### 為什麼 v5.10.0 不做派發匹配

直覺的做法是讓塔台派工前自動判斷「這張該用 Workflow」。v5.10.0 刻意不做，理由來自證據，不是保守：

- **乾淨的扇出比想像中少。** 挖掘 718 張工單、複核 30 張證據工單後發現，單張工單內「彼此獨立、執行前就能列出」的子任務很少見；
  Workflow 的實際價值多半出在**驗證品質**（抓出被推翻的結論、補上漏掉的項目），不在速度。派發匹配的預期因此被下修。
- **還沒有一個 workflow 證明過自己。** 知識卡要先回測（對照已結案工單的已知發現，召回 ≥ 80%、誤報 ≤ 20%）才升 🟡；
  在任何卡片達標之前就自動派發，等於讓未驗證的規則決定花費。
- **成本無法原生控制。** Workflow 沒有 token 預算參數，執行中也讀不到用量（每個子 agent 光固定開銷就約 31k tokens），
  只能限制 agent 數、事後記帳。所以每次回測或試跑之前都要**先列規模、經使用者同意**；派工型在卡片到 ⭐ 之前也一律先問使用者。

於是 v5.10.0 只做規則層：`ct-insights` 找候選、`ct-evolve --workflow` 只產 brief、設計規則 R1–R5（例如子 agent 只用唯讀 tool、
不用 Workflow 內建的 worktree、略過的項目一律記錄）、知識卡與成熟度、只限 Workflow 的指標降級。
腳本由另一張工單在使用者確認 brief 後才寫，且必須進專案 git（見 `three-layer-arch.md`）。

權威：CT `control-tower/references/workflow-engine.md`（定位、三分法、R1–R5、知識卡、成熟度與降級、成本）、
`ct-insights/references/analysis-rules.md` § Workflow 適配度（偵測規則）。

### v5.11.0：回測沒過之後，先做便宜的部分

v5.10.0 寫好規則後，CT 真的拿兩張卡（語料挖掘、多來源唯讀核對）去回測，花了約 1.8M tokens，**兩張都沒有達到 🟡**（閘門 G2 未通過）。
回測留下三個教訓：

- **對抗式複核不是保險。** 有一次 reader 沿用了前一張工單的錯誤結論，負責唱反調的 refuter 只沿著讀取點追、沒追到值的寫入點，也判「確認」；
  最後是 Worker 回到程式碼快照親自查證才推翻。多一層 agent，不等於多一層正確。
- **成本被低估 2–3 倍。** 多來源核對的 reader 每組實際用了 100–180k tokens，卡片原本估 40–60k；其中一次超過事後上限約 22%。
  執行中讀不到用量，上限只能事後對照——這正是前面說「成本無法原生控制」的實際樣子。
- **真正有效的平行讀取，多半是 Worker 自己決定的。** 回頭看已確認的好例子，幾乎都是 Worker 在工單裡自己開唯讀子代理分頭讀，
  工單本身並沒有寫「要平行」；回測時具名 workflow 甚至漏掉了單一 Worker 當初找到的推翻。

所以 v5.11.0 沒有做「具名 workflow 的派發」，而是先把下面幾件**不花 workflow token** 的事做好：

| 做了什麼 | 為什麼這樣設計 |
|---|---|
| **Worker 要有授權才用 Workflow**：工單裡有「Workflow 使用授權」段落（寫明跑幾次、每次最多幾個 agent、token 事後上限）才可以呼叫，超出就停下問塔台 | Workflow 的花費要在派工時就被看見、被同意；不能等 Worker 執行到一半自己決定 |
| **Worker 自己開的子代理要記帳**：不需要授權，但回報區要寫幾個、做什麼、是否唯讀、約略 tokens | 證據顯示好的扇出多半來自這裡；先記下來，日後才知道值不值得做成具名 workflow |
| **`workflow_integration` 開關**：`off`／`ask`／`on`，預設 `on` | 讓使用者決定 Workflow 的積極程度，見下方 |
| **預篩腳本只守門、不打擾**：`*insights workflow` 只在塔台主動呼叫時跑，命中 X2／X3／X5 就判「不考慮 Workflow」，其他只列證據位置 | 腳本對「該排除的」判得準（X2 的召回與誤判和 T0177 定案結果相同），對「該用的」判不準（抽讀 9 張只有 2 張成立）。把準的部分拿來守門，不準的部分不主動跳出來——會一直誤報的警示，使用者很快就會習慣性略過 |

**token 焦慮時怎麼關。** `workflow_integration` 是塔台設定，和其他設定一樣分 session／project／global 三層：

- 這個 session 先不要碰 Workflow：`*config workflow_integration off`，關掉 session 就恢復
- 這個專案一直不要：加 `--save project`；所有專案都不要：加 `--save global`
- `off` 的意思是塔台**不建議、不授權** Workflow，也不跑工具型 workflow；但規則分析、預篩腳本、`--workflow` 產 brief 照常——它們本來就不花 workflow token
- `ask` 是每次要授權前都先問你；`on`（預設）是知識卡到 ⭐ 之前先問你——目前沒有 ⭐ 卡，所以 `on` 實際上也是每次問

Worker 不讀這個設定。塔台在派工時就把決定寫進工單：有授權段落才能用，沒有就不能用；這和「Worker 是無狀態的」是同一個原則。
注意它只管 **Workflow 工具**；Worker 用一般 Agent 工具開的子代理不受它管，但用量一定會出現在回報區。

權威：CT `workflow-engine.md` § `workflow_integration` 的行為、§ 同意治理、§ 現況：G2 未通過；設定值 `tower-config.md` § 可用選項；
Worker 規則 `ct-exec/SKILL.md` § Workflow And Sub-Agents；預篩 `ct-insights/references/analysis-rules.md` § 預篩腳本：排除守門與按需提示。

## 粒度決策

「這件事要不要開工單？」是最常見的判斷。塔台在建立工作前先分類請求：

| 請求 | 塔台處理 |
|------|---------|
| 新的、不明確的功能／bug／研究／遷移／跨模組任務 | 先做需求對齊，再建立一張或多張工單 |
| 單一模組內、不涉邏輯的小變動 | 安全時塔台可直接處理，commit 依 `auto_commit` |
| 已知工單的完成／部分完成／失敗／求助 | 讀該工單回報區，更新塔台狀態，再決定下一步 |
| `ct-exec`／`ct-done`／`ct-status`／`ct-evolve`／`ct-insights` | 交給對應的獨立 skill，不把塔台角色帶進 Worker session |

工單本身的粒度：一張工單 = 一個工作流程或一個明確交付物，可中斷、可接續。

**設計原則**：粒度判斷是輔助決策，不是硬規則。塔台提供建議，使用者做最終決定。
