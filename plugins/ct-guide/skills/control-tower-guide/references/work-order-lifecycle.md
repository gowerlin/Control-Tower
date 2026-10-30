# 工單生命週期

## 工單是什麼

工單是塔台與 Worker session 之間的通訊橋樑。每張工單是一個 `.md` 檔案，包含：

- **任務指令**：要做什麼、怎麼做、明文排除什麼
- **驗收條件**：做到什麼程度算完成
- **回報區**：執行結果、遭遇問題、互動紀錄

存放在專案的 `_ct-workorders/` 目錄。工單之所以是「檔案」而不是對話裡的一段話，是因為磁碟上的 artifact 是跨 session 唯一可靠的共享介面（見 `concepts.md` § 第一原則）。

### 四種單據命名格式

| 單據類型 | 編號格式 | 位數 | 檔名範例 |
|---------|---------|------|---------|
| 工單 | `T####` | 4 位 | `T0045-user-auth.md` |
| BUG | `BUG-###` | 3 位 | `BUG-012-login-crash.md` |
| PLAN | `PLAN-###` | 3 位 | `PLAN-003-api-redesign.md` |
| EXP | `EXP-[TOPIC]-###` | 3 位（每個 TOPIC 獨立計數） | `EXP-CACHE-001-redis-ttl.md` |

工單 ID 可以帶一個**可選**的 2–4 位大寫前綴，例如 `CP-T0113`（跨塔台交辦）或 `LC-T0001`（設定了 `project-prefix`）。
所以「沒設 project-prefix 就不會看到前綴 ID」並不成立——收到別的塔台交辦的工單時就會出現。
Worker 回報與通知時也要原樣送出含前綴的完整 ID（v5.13.1），見下方 § 回報與通知用完整工單 ID。
ID 格式在 CT 中只有**一處權威定義**（`work-order-system.md` § 工單 ID 格式），其他地方一律交叉引用；
為何要收斂成單一定義，詳見 `governance.md`。

BUG／PLAN／EXP 預設關閉，由 `enable_bug_tracking`／`enable_plan_tracking`／`enable_experiments` 開啟（見 `ecosystem.md` § 設定系統）。

---

## 工單的兩層 metadata：frontmatter 與 body table

v5 的工單檔有**兩份** metadata，各司其職：

```markdown
---
schema_version: 1          ← 機器讀這裡（SoT）
schema_kind: workorder
id: T0045
status: IN_PROGRESS
...
---
# 工單 T0045-user-auth

## 元資料                  ← 人類看這裡（鏡像）
- **狀態**：IN_PROGRESS
...
```

| | YAML frontmatter | body 元資料表 |
|---|---|---|
| 角色 | **機器 SoT** | 人類鏡像，供速查 |
| 誰讀 | `*sync`、`ct-status`、BAT、腳本 | 使用者、Worker 閱讀時 |
| 兩者不一致時 | 以 frontmatter 為準 | `*sync` 輸出 drift warning，**不自動覆寫** body |

**為什麼不讓 body table 當唯一來源？** 人類寫的 markdown 表格格式漂移是常態（欄名改字、多一個空格、emoji 前綴），
機器解析它就得容忍各種寫法；把機器要讀的值搬進固定格式的 YAML，解析就變成確定性的。
**為什麼 drift 時不覆寫 body？** body 可能有人類特意寫的註記，機器自動覆寫等於抹掉人的判斷；只警告、交給人處理才安全。

缺 frontmatter 的舊工單仍可被讀取（legacy 表格 fallback），只會被警告，不會立即失效。

### frontmatter 欄位地圖

| 欄位 | 用途 | 設計理由 |
|------|------|---------|
| `schema_version` / `schema_kind` | 固定 `1` / `workorder` | 讓解析器知道自己在讀什麼；index 檔等其他種類有各自的 `schema_kind` |
| `id` / `title` | `T####` 與不含狀態 emoji 的標題 | ID 不含檔名描述，比對才不會因描述改字而失準 |
| `type` | `research`／`impl`／`fix`／`test`／`docs`／`refactor`／`audit`／`spike`／`chore` | `research` 會改變 Worker 的互動行為（見下方研究型工單） |
| `status` | 狀態 enum（見下節） | 顯式狀態讓塔台只讀前幾十行就能分類，不必全文判讀 |
| `repo` | repo 根目錄的**目錄名** | 落點檢查的身分依據；與 `project`（子專案／PLAN／BUG 名）語意不同、不得混用。工單集中在上層、改的是巢狀的獨立 repo 時填**上層**的目錄名（v5.14.3，見 `advanced-patterns.md` § 巢狀的獨立 repo） |
| `project` | mono-repo 子專案或記錄編號 | 由人命名，不參與落點檢查 |
| `created_at` / `started_at` / `updated_at` / `completed_at` | 帶時區的 ISO 8601 時間 | 時間一律由系統指令取得，不由 AI 推估 |
| `depends_on` / `followups` | 前置與後續工單 | 工單鏈的明文依賴 |
| `affects_files` | 這張工單會動到的檔案 | 派發前做 **static overlap check**：兩張進行中工單的集合有交集就警告、要求序列化 |
| `interaction.mode_hint` | 派發時的意圖紀錄 | **只是文件**，不是 Worker 的 runtime mode 來源 |
| `interaction.interactive` | 是否允許 Worker 主動提問 | 研究型工單的預設依據；runtime 的 `CT_INTERACTIVE` 優先；yolo 下不適用（一律改問塔台，v5.5.0） |
| `interaction.intervention_type` | `fire-and-forget`／`context-dependent`／`decision-requiring` | 依「對塔台的介入成本」分類：決定能否平行、要不要預告使用者等下得做決策 |
| `renew_count` | Renew 次數 | 塔台據此判斷是否該改開新工單 |
| `landing_check.expect_missing` | 本工單自己會建立目標樹 | 落點檢查的逃生閥，**只有塔台能設** |
| `isolation`（v5.3.0，選用） | 唯一的值 `worktree`：派工時讓 BAT 建獨立 worktree | **預設不隔離**，沒有這個欄位時一切與 v5.2.6 相同；見下方〈worktree 隔離與合併工單〉 |

另外兩個 body 區段也屬工單 metadata：`memory_overrides`（明列「AI 記憶中某個舊作法本工單不採用」及理由）與
「規格層級自問」（派發前確認 spec 停在架構邊界層，不太淺讓 Worker 亂猜、也不太深奪走 Worker 的實作選擇）。

合併工單（v5.3.0）沿用同一套 frontmatter、同一個 `T####` 編號序列，只多幾個固定欄位：`kind: merge`、`merges`、`merge_mode`、
`integration_worktree`、`base_main_sha`、`merge_target`——它**不是新的單據類型**，而是一張任務內容固定為「合併」的一般工單。

> 欄位的完整寫法與值域以 CT 的 `work-order-template.md` 為準；本節只講每個欄位為什麼存在。

---

## 核心迴圈

迴圈骨架不變：**塔台產生工單 → Worker 執行 → 回報 → 塔台更新狀態、記錄學習、派下一張**。
v5 的差別在「派工」與「回報」兩端可以由 BAT 自動化，依 `auto-session` 設定分成三種形態：

| 形態 | 派工 | Worker 收尾後的回報 | 誰按下送出 |
|------|------|-------------------|-----------|
| **手動** | 塔台顯示 Worker 指令，使用者自己開新 session 輸入 `/ct-exec T0001`（或 Codex 的 `$ct-exec T0001`） | Worker 顯示固定訊息（如 `T0001 完成`），使用者帶回塔台 | 使用者 |
| **BAT** | 塔台透過 BAT 直接開出 Worker 終端並帶入工單 | Worker 把訊息**預填**到塔台終端的輸入列（`on`；`ask` 由使用者帶回） | 使用者（確認後送出） |
| **YOLO** | 同 BAT | Worker 預填**並自動送出**，塔台讀回報後自主決定下一張 | 自動；遇斷點才停下等人 |

剪貼簿只是 BAT 不可用時的 fallback，不再是主要回報管道。
派工機制與 YOLO 斷點的設計見 `runtime-dispatch.md`。

在 BAT 內，迴圈前後還多了幾個附帶步驟：塔台啟動時宣告自己的分頁（v5.2.0）、收單後可請 BAT 回收 Worker 分頁（v5.1.0，預設關閉）、同一張工單重派前先回收舊 Worker 分頁（v5.12.0）；
塔台也必須在使用者自己開的一般分頁啟動，不能在 Worker 分頁裡（v5.2.4）。這些步驟失敗都不影響迴圈本身。
一張分頁從宣告、派工、通知到回收的完整路徑與設計理由，見 `bat-integration.md` § 一張分頁的生命週期。

v5.3.0 起，帶 `isolation: worktree` 的工單在迴圈尾端多一段**合併**：Worker 的成果在分支 `ct/T####` 上，要合併回 `main` 才算進了主線。
見下方〈worktree 隔離與合併工單〉。

固定回報訊息依最終狀態對應：`DONE`／`FIXED` → `T#### 完成`；`PARTIAL` → `T#### 部分完成`；`FAILED`／`BLOCKED` → `T#### 需要協助`。
v5.5.0 起 yolo 另有一個**不是收尾**的訊息 `T#### 提問`：工單仍是 `IN_PROGRESS`，Worker 有問題在等塔台答覆（見下方〈yolo 提問通道〉）。

---

## 狀態機

### 工單 status enum

```
PENDING / IN_PROGRESS / DONE / FIXED / FAILED / BLOCKED / PARTIAL / INTERRUPTED / URGENT
```

### 正常流程

```
📋 PENDING → 🔄 IN_PROGRESS → ✅ DONE
```

工單沒有「待審」這種中間態。驗收是塔台讀回報時做的事，不是工單的一個狀態；
需要獨立審查時，塔台會派一張**審查工單**，而不是讓原工單停在某個狀態等人。

### 其他路徑

| 路徑 | 說明 |
|------|------|
| `IN_PROGRESS → 🔧 FIXED` | 修 bug 的實作完成，等待驗證 |
| `IN_PROGRESS → ⚡ PARTIAL` | 部分驗收閘門通過、至少一項未完成；須寫明卡在哪個閘門。段落分給 Worker 與塔台的工單，Worker 只就自己的段落判定，塔台段落還沒證據不算 `PARTIAL`（v5.6.1；CT `work-order-template.md` § 撰寫 verification 工單的驗收步驟） |
| `IN_PROGRESS → ❌ FAILED` | 嘗試的作法沒有達成目標，需塔台判斷 |
| `IN_PROGRESS → ⛔ BLOCKED` | 需要使用者輸入或外部狀態（權限、環境、廠商）；須點名缺什麼 |
| `IN_PROGRESS → ⏸ PAUSED → IN_PROGRESS` | `*pause` 凍結以處理緊急任務，`*resume` 恢復 |
| `IN_PROGRESS → INTERRUPTED` | session 中斷且由塔台決定改派或開接續工單時，原工單標記中斷 |
| `直接 → 🔥 URGENT` | 中斷協議產生的緊急工單，**不經過 PENDING** |
| `→ ABANDONED`／superseded | 工單因範圍決策被刻意退役，與「完成」區分 |

### 狀態分桶

`ct-status` 與塔台把狀態分成三桶，回答的是「這張工單現在需要誰」：

| 桶 | 狀態 | 意義 |
|----|------|------|
| **Active** | `PENDING`、`IN_PROGRESS`、`PAUSED`、`URGENT` | 還在流程中 |
| **Needs Tower judgment** | 未解決的 `PARTIAL`、`BLOCKED`、`FAILED`、`INTERRUPTED`（v5.12.5+）、`UNKNOWN` | 需要塔台做決定；`INTERRUPTED` 是塔台已開接續工單或重派的原工單，塔台確認接續工單接手後才結掉 |
| **Final** | `DONE`、`FIXED`（驗證政策允許後）、`CLOSED`、`WONTFIX`、`DROPPED`、`CONCLUDED`、`ABANDONED` | 已結束 |

### resolved PARTIAL → DONE

`PARTIAL` 是**時間點**狀態，不該永遠代表「還有未完成工作」。
若之後的工單、範圍決策或最終驗收已解除原本的 blocker，塔台把原工單補正為 `DONE`：
保留原回報區與證據、加一段事後註記說明由哪張工單／哪個決策解決，並同步各處追蹤。
若 blocker 是因設計方向被淘汰而消失，則用 `ABANDONED`／superseded 類終態，而非 `DONE`。

**v5.13.0：一裁示就收尾。** 以前補正的時點落在歸檔前覆核，結果常是塔台早就決定「剩下的交給另一張單」，
原工單卻在看板上掛著 `PARTIAL` 好幾天，看起來像沒做完。現在的規則是：Worker 依停止條件回 `PARTIAL` 是對的，收尾是塔台的事——
塔台**一裁示**剩餘部分怎麼處理（另開接手單、或判定不需再做），就**當下**在原工單文末補〈塔台收尾補記〉並改 `DONE`，
接手單完成後再回頭確認；剩餘部分被設計方向淘汰的改 `ABANDONED`。只有真的在等外部條件（廠商、客戶、環境、使用者還沒給的輸入）
才保留 `PARTIAL` 或改 `BLOCKED`。歸檔前覆核仍在，但只是最後防線。權威：CT `work-order-system.md` § PARTIAL 當下收尾。

### 事實來源優先級

SoT 分兩段：

> **跨來源**：工單檔案 > `sprint-status.yaml` > 塔台記憶
>
> **工單檔案內**：YAML frontmatter > body 元資料表

不一致時以左邊為準，使用 `*sync` 修正差異。

---

## ct-exec 的執行流程

Worker 在新 session 執行 `/ct-exec T0001`（或 `$ct-exec T0001`）後，依序經過：

```
Startup → Landing Zone Check → Phase 1 Start → Phase 2 Execute
        → Phase 3 Verify → Phase 4 Report And Commit → BAT Notify
```

### Startup

定位工單檔（多張符合就停下來問）、先讀專案規則（`AGENTS.md`、`_ct-workorders/_local-rules.md`、`CLAUDE.md`），
再完整讀工單：frontmatter、body 元資料、執行步驟、驗收閘門、明文排除、回報模板。開工前取得真實系統時間。
環境有 `CT_HOME` 時（v5.3.0 隔離派工），工單到 `$CT_HOME/_ct-workorders/` 找，見下方〈worktree 隔離與合併工單〉。

**Worker 的模式由塔台在派工時傳入**（`CT_MODE`、`CT_INTERACTIVE` 環境變數），Worker **不讀設定檔來決定模式**；
frontmatter 的 `mode_hint` 也只是參考。設定檔只能用來讀重試上限、commit 政策這類調諧參數。
這就是「Worker 無狀態」原則（見 `concepts.md`）。

### Landing Zone Check（落點檢查）

**任何寫入動作之前**（改工單狀態、動產品檔、commit），Worker 先確認自己落在對的 repo：
比對工單 frontmatter 的 `repo` 與實際 repo 根目錄名，不符就 STOP 並回報，不猜、不自行修改工單讓檢查通過。

它是最後一道防線：不假設派工端傳的參數一定正確。
為什麼「身分」不能靠檢查路徑是否存在來證明、`expect_missing` 逃生閥為何只有塔台能設，詳見 `governance.md`。
在 worktree 裡（v5.3.0），比對的對象改成 `CT_HOME` 的目錄名，因為 worktree 的根目錄名是 `T####`；STOP 的語意不變。

### Phase 1：Start

1. frontmatter 寫入 `started_at`、`updated_at`，`status` 從 `PENDING` 改為 `IN_PROGRESS`，body 表格同步鏡像
2. 若工單已是 `IN_PROGRESS`，保留原開工證據，註記這是續作
3. 呈現任務摘要：編號、標題、範圍、關鍵檔案、明文排除、驗收閘門

### Phase 2：Execute

- 只在 `affects_files`、執行步驟與明文排除的範圍內工作
- 只載入工單與專案規則要求的文件
- 不動無關的未提交變更，不還原使用者的修改
- 需求變成範圍外時**停下來問**：完成目前範圍、記錄給塔台、或明確擴大範圍
- 執行中有四項防護：範圍守衛、熔斷計數（同一問題連續失敗達 `worker_max_retries` 即三振）、洋蔥偵測、超時提醒（詳見 `advanced-patterns.md`）；
  yolo 下這些防護不問使用者，改為記錄或問塔台（v5.5.1）
- **Claude Code Workflow 只在工單明文授權時才用**（v5.11.0）：工單沒有「Workflow 使用授權」段落就不呼叫；有的話只做列出的執行，超過 agent 或 token 上限、要重跑都先停下問塔台。Worker 自己開的唯讀子代理不需授權，但回報區要記數量、用途、是否唯讀、約略 tokens（權威 CT `ct-exec/SKILL.md` § Workflow And Sub-Agents；為什麼見 `concepts.md` § v5.11.0：回測沒過之後，先做便宜的部分）

### Phase 3：Verify

跑工單指定的驗收閘門；跑不了的閘門要記下確切阻礙，**不得暗示 PASS**。
證據依通道分開回報，不混為一談：

```
source／docs 檢查 │ build 與測試 │ runtime smoke │ 部署 │ release／安裝包驗證 │ 外部 SIT／客戶確認
```

「單元測試過了」不等於「部署上去能動」，更不等於「客戶確認了」。每一道各用 `PASS`／`PARTIAL`／`BLOCKED`／`FAILED` 附具體證據。

### Phase 4：Report And Commit（反序收尾）

```
1. 依政策先 commit 產品變更（回報區才記得到它的 hash）
2. 填回報區（結果、變更檔案、驗證證據、commit 狀態、偏差、阻礙、後續）
3. 更新 status 與完成時間
4. 依政策 commit 工單檔
5. 最後才通知塔台
```

v5.7.0 起這就是唯一的收尾順序：隔離工單（下方〈Worker 在 worktree 裡怎麼工作〉）本來就是這個順序，非隔離工單也對齊了。
v5.6.1 以前非隔離工單寫成「回報區 → commit → 狀態」，T0168 發版時發現它和「通知前工單已 commit」的規則對不上（D047），
所以改成「狀態寫完、工單 commit，才 notify」。權威寫法見 CT `ct-exec/SKILL.md` § Phase 4。

**為什麼要反序？** 工單檔就是塔台與 Worker 之間的 IPC 通道。若先改狀態再填回報，監看狀態變化的塔台或工具
可能讀到一張「狀態 DONE 但回報區空白」的殘缺工單。反序寫入保證「外部看到終態的那一刻，回報區已完整」——
這是 filesystem-as-IPC 情境下的 happens-before 保證。

**commit 依政策，不是一律強制**：

| `worker_commit` | 行為 |
|-----------------|------|
| `required`（預設） | 必須 commit；commit 失敗仍完成收尾並記錄原因 |
| `recommended` | 建議 commit，不阻斷收尾 |
| `off` | 不要求 |

工單本身也可以明文規定（例如「不得 commit，塔台驗收後統一收帳」），以工單為準。
commit 訊息必須帶工單編號；有無關的未提交變更時只 commit 本工單的檔案；**除非工單明文授權，否則不 push**。

`sprint-status.yaml` 只在工單明確要求時由 Worker 更新，塔台每次處理回報時會複查補漏。

### BAT Notify

通知在最終狀態與回報區都寫完**之後**才送，依 `CT_MODE` 處理：`yolo` 預填並自動送出（`--submit`）；`on` 只預填、不送出；
`ask`、`off`，以及 `CT_MODE` 缺值或不合法（Worker 視同 `ask`）一律不加 `--submit`，顯示要帶回塔台的確切訊息作為剪貼簿／手動 fallback。
通知失敗時如實記錄，並顯示要手動帶回塔台的確切訊息——不得宣稱自動送出成功。

Worker 只送通知：不宣告分頁（那是塔台的事）、回報區記錄 BAT 證據時權杖只寫「已設定」、不寫出它的值。
helper 用哪個 node、Worker 分頁的權限範圍與這些規定的理由，見 `bat-integration.md` § Worker 執行與通知、§ 範圍權杖與分頁角色。

### 回報與通知用完整工單 ID（v5.13.1）

上面各處寫的 `T#### 完成`、`T#### 提問` 是**訊息種類的名稱**，實際送出的是**工單完整 ID**：`/ct-exec`（`/ct-done`）收到什麼 ID 就照原樣用，
它等於工單 frontmatter `id`，含前綴、不截短。沒設前綴的專案送 `T0341 完成`；設了前綴（例 `LB-`）的專案送 `LB-T0184 完成`，
`bat-notify.mjs --source` 也是 `LB-T0184`。提問（`--ask --source`）與手動帶回塔台的備援訊息同樣適用。

**為什麼要特別寫出來**：v5.13.0 以前的通知範本寫的是 `--source "T####" … "T#### 完成"`。Worker 照著範本「T 加四位數字」的形狀，
有時會從 `LB-T0184` 截出 `T0184`——一個設了前綴的專案統計，回報 87 次帶前綴、43 次沒帶，隨機發生。
塔台讀得懂這種回報，問題出在 BAT：BAT 用 `--source` 比對 Worker 分頁登記的工單，對不上就無法把那個分頁標成 Done，
使用者也就不能一次關掉所有已完成的 Worker 分頁。CT 的 ID 格式本來就允許前綴，**規格沒錯，錯在範本沒教**，所以修在 CT 這邊。

v5.13.1 分三層修：

| 層 | 做什麼 | 補的是哪個洞 |
|---|---|---|
| 範本 | 所有通知範本改寫 `<工單 ID>` 並指回唯一權威，附有前綴與無前綴的例子 | 根因：不再給 Worker 一個可以照抄的錯誤形狀 |
| Worker 送出前比對 | 送通知、`--ask` 或顯示手動備援訊息之前，拿要用的 ID 和 frontmatter `id` 比（舊單沒有 `id` 就取檔名開頭到第一個 `T` 加數字為止）；不一致就改用 frontmatter 的值，並在回報區記一行 | 防呆：範本之外的失誤，送出前就攔下 |
| 塔台缺前綴容錯 | 收到的 ID 在熱區沒有完全相同的工單、但**恰好一張**是「前綴 + 同號」→ 當作那一張處理並記錄「回報 ID 缺前綴」；同號有多張或找不到 → 不猜，問使用者（yolo 屬斷點 A） | 過渡期：還在跑舊 skill 的 Worker 送來缺前綴的回報，塔台照樣收得了單 |

第三層刻意寫明**只保住塔台收單**。塔台在自己這邊對到工單，不會讓 BAT 那邊的 `--source` 對上，那個分頁還是標不了 Done；
所以真正的修法是 Worker 端的前兩層，塔台容錯只是不讓流程卡住。容錯也只往一個方向：收到帶前綴的 ID、熱區卻只有無前綴的同號單時不套用，
因為「漏寫前綴」解釋不了這種情況，照樣問使用者。

**塔台端範本也改（v5.14.1）。** v5.13.1 修的是 Worker 端；塔台端的派工與回收範本（`--workorder`、`--close-worker`、`--worktree-status`）
當時還寫 `T####`，給塔台的是同一個可以照抄的錯誤形狀。派工時塔台傳什麼，BAT 就替 Worker 分頁登記什麼，
所以完整 ID 要從派工那一刻就對；5.14.1 把這些範本也改成 `<工單 ID>`（代入 frontmatter `id` 原樣、含前綴）。
`/ct-exec T####` 這類 agent 呼叫字串樣板保留 `T####`：表頭本來就標明是占位，CT 另在派工權威表加一句說明它同樣代表完整 ID。

> 規則以 CT `work-order-system.md` § 回報與通知用的工單 ID（Worker 端，含送出前比對）與 § 回報處理流程 › 回報 ID 對不上時（塔台端）為唯一權威；
> 前綴從哪裡來見 `advanced-patterns.md` § 工單 ID 前綴，BAT 怎麼用 `--source` 見 `bat-integration.md` § Worker 執行與通知。

---

## worktree 隔離與合併工單（v5.3.0）

### 為什麼要隔離

非隔離的工單直接在主 checkout 工作，一次只跑一張單時沒有問題。但 YOLO 或手動同時派出兩張會動產品檔的工單時，
兩個 Worker 改的是**同一個工作樹**：一個 Worker 跑測試時，另一個 Worker 改到一半的檔案也在裡面；一個 Worker commit 時，
可能把另一個的變更一起帶進去。`affects_files` 的重疊檢查能擋住「改同一個檔」，擋不住「共用一個工作樹」。

工單帶 `isolation: worktree` 時，BAT 為它建一個獨立的 git worktree 與分支 `ct/T####`，Worker 在裡面工作。好處有兩個：

- **並行不互污**：每個 Worker 有自己的工作樹，測試、build、commit 都只看到自己的變更
- **可追溯的合併**：成果是一條從已知 base 開出的分支，驗收跑在哪個 SHA、合併的是哪個 SHA，全部有證據可對

**預設不隔離。** 隔離有成本：多一個 worktree 要裝依賴、多一段合併流程。所以它是選用的——適合並行、會大量改產品檔、希望驗收過後再進 `main` 的工單；
只改 `_ct-workorders/` 或文件的小單、研究型工單、需要在主 checkout 操作執行環境的工單（安裝、部署）不適合。
沒有這個欄位時，派工、Worker、收單、回收與 v5.2.6 完全相同。

隔離派工失敗（BAT 回 exit `7`，或 BAT 太舊）時，塔台**不會自動改成非隔離**重派，而是停下來讓使用者決定——
非隔離等於讓 Worker 直接改主 checkout，那正是使用者選擇隔離時想避免的事。BAT 端的細節見 `bat-integration.md` § worktree 隔離派工。

### Worker 在 worktree 裡怎麼工作

Worker 從環境變數 `CT_HOME` 知道自己在 worktree 裡（派工時由 BAT 注入，不靠自己推測）。和平常不同的只有四件事：

| | 規則 | 為什麼 |
|---|---|---|
| 工單在哪裡讀寫 | 一律在**主 checkout** 的 `$CT_HOME/_ct-workorders/`；worktree 裡那份是 base 當下的唯讀副本，不改、不 stage | 塔台讀的是主 checkout；寫在 worktree 裡的回報塔台看不到，合併時還會和塔台的記帳衝突 |
| 產品變更 commit 到哪 | worktree 的分支 `ct/T####`；不切分支、不 merge、不 rebase、不 push | 分支就是交付物；合併是塔台的決定，不是 Worker 的 |
| 收工前 | worktree 必須**全部 commit**（`status --porcelain` 為空），即使 commit 政策本來可以不 commit | 沒 commit 的東西不在分支上，合併不到；髒的 worktree BAT 也不會清掉 |
| 回報區 | 多一段「隔離分支證據」：`branch`、`base_sha`、`validated_sha`、`head_sha` | 見下一小節 |

BAT 不替 worktree 安裝依賴，Worker 要照專案規則自己裝；專案沒寫怎麼裝，就在回報區記下來。
反序收尾的順序不變，只是分成兩個地方：先在 worktree commit 產品變更、記下 SHA，再到主 checkout 填回報、改最終狀態、commit 工單，最後才通知塔台。

### 收單 SHA 回報的用途

| 欄位 | 是什麼 | 拿來做什麼 |
|------|-------|-----------|
| `branch` | `ct/T####` | 合併時要合哪條分支 |
| `base_sha` | 派工當下的 base | 算出 `main` 在這段期間前進了什麼（例如只有塔台的工單記帳 commit） |
| `validated_sha` | 跑驗收閘門那一刻的 `HEAD` | 證明「驗收過的」是哪個版本 |
| `head_sha` | 最後一次產品 commit 後的 `HEAD` | 證明「要合併的」是哪個版本 |

`validated_sha` 與 `head_sha` 相等，才能說「合併進 `main` 的，就是驗收過的那一版」；驗收之後又 commit 了東西，Worker 必須說明那些 commit 為什麼不需要重驗，
或重跑驗收。塔台直接合併的判準之一就是兩者相等。

### 合併：為什麼交給工單，而不是 BAT

BAT 只提供**唯讀信號**（`--worktree-status`：分支 ahead／behind、變更檔、範圍外檔案、預測衝突、髒檔），不 checkout、不 merge、不 commit。
合併由塔台決定、由塔台自己或合併工單執行。理由是合併需要的東西 BAT 都沒有：判斷衝突雙方的意圖、跑專案的完整驗收、
在範圍外檔案出現時停下來問人——這些正是工單流程（Worker 執行、驗收閘門、回報區、塔台收單）本來就有的能力。
讓 BAT 變成合併引擎，等於在工單流程之外另開一條沒有驗收與回報的路。

合併有三種模式，由**塔台**決定、寫在合併工單的 `merge_mode`，Worker 不得自行改：

| 模式 | 什麼時候用 | 誰做 | yolo 下能否自動推進 `main` |
|------|-----------|-----|------------------------|
| ① 機械（`mechanical`） | 塔台直接合併判準五條全部成立 | 塔台自己做，**不派單** | ff 前再確認判準仍成立 → 自動 |
| ② 衝突解決（`conflict`） | 判準不成立，但用 git merge 解衝突就能完成 | 合併工單：Worker 合併、解衝突、跑完整驗收，逐檔寫下雙方意圖與解法 | 驗收全綠且無範圍外檔案 → 自動；否則暫停 |
| ③ 等價移植（`port`） | 分支太舊、程式碼已重構、或來源是 EXP／上游成果，git merge 已不適合 | 合併工單：Worker 以原工單的目標與驗收為規格，從目前 `main` 重新實作，附「原 hunk → 新位置」對照表 | 一律暫停 |

模式 ② 的 Worker 發現情況超出解衝突（例如合併後邏輯必須改寫），回報 `PARTIAL` 並**建議**改 ③，不自行升級——
換模式等於換一種工作，那是塔台的決定。

### 塔台直接合併的判準精神

五條判準（以 CT 的 `merge-workorder.md` § 塔台直接合併判準 為準）可以濃縮成一句話：
**合併結果的產品檔，必須和 Worker 驗收過的那一版完全相同，而且沒有任何東西需要人判斷。**
所以它要求驗收版本等於分支現況、沒有範圍外檔案、沒有改到 `_ct-workorders/`、預測沒有衝突、兩邊都沒有會擋路的髒檔。

第 1 條原本是「`main` 沒有前進」，v5.3.0 採**放寬版**：`main` 沒前進，**或只在 `_ct-workorders/**` 前進**也算通過。
原因很實際：塔台每收一張單都會 commit 工單記帳，`main` 幾乎一定會前進；嚴格版會讓直接合併幾乎永遠不成立。
而只動 `_ct-workorders/**` 的前進不碰產品檔，合併後的產品樹仍等於驗收過的那一版，所以不必重跑驗收。

判準的資料取不到（BAT 查不到、git 也算不出來）一律算**不通過**——資料缺漏時寧可派合併工單多跑一次驗收，也不靠猜測直接推進 `main`。

### 共同護欄與斷點 E

三種模式共用一組護欄：只在長期保留的**整合 worktree** 合併、一律 `--no-ff`、`main` 只用 `--ff-only` 推進、不 push、不 `--force`／`reset --hard`／rebase `main`；
主 checkout 有重疊的髒檔時 `--ff-only` 會被拒絕，這是正常保護，不 stash、不丟棄使用者的變更。
即使 `behind == 0`，直接合併也一律走整合 worktree `--no-ff` 再 `--ff-only`，不走「直接 ff 工單分支」的捷徑。
這些護欄為什麼這樣定，見 `governance.md` § 合併護欄。

`--ff-only` 推進 `main` 之前是**斷點 E**：非 yolo 一律暫停確認，yolo 依上表各模式的規則（見 `runtime-dispatch.md` § YOLO 與斷點）。
推進之前，塔台還要做「收單 SHA 比對」：確認 merge commit 的兩個 parent 分別是合併前的 `main` 與 Worker 驗收過的 SHA，
（等價移植沒有這種 merge commit，改以對照表與逐條重驗取代），任一步對不上就不推進。合併完成後才清掉被合併工單的 worktree，分支保留到使用者同意刪除。

### 收單時的順序

```
Worker 回報 DONE（含隔離分支證據）
  → 塔台查 --worktree-status（舊 BAT 必須在回收分頁之前；BAT >= 0.7.0-pre.4 回收後也可查；查不到就改用 git）
  → 回收 Worker 分頁：--close-worker … --worktree keep（worktree 與分支留著）
  → 判準五條全部成立？ ─ 是 → 模式 ①：塔台在整合 worktree 合併
                       └ 否 → 派合併工單（模式 ② 或 ③）
  → 收單 SHA 比對 → 斷點 E → main --ff-only → 清理 worktree
```

> 隔離欄位以 CT 的 `work-order-template.md` § `isolation` 為準；Worker 規則以 `ct-exec/SKILL.md` § Worktree Isolation 為準；
> 合併流程（模式、護欄、判準、`--worktree-status`、SHA 比對、清理）以 `merge-workorder.md` 為準；斷點 E 以 `yolo-mode.md` § 斷點 E 為準。
> BAT 端的派工、回收與查詢見 `bat-integration.md`。本節只講設計理由。

---

## Session 中斷善後

Worker session 意外關閉、AI 沒收尾、或需要手動更正狀態時，用 `ct-done` 補救：

```
/ct-done T0001 PARTIAL
```

`ct-done` 一樣先跑落點檢查，再補完回報與收尾，確保工單不會成為「幽靈工單」（`IN_PROGRESS` 卻沒人在做）。
v5.7.0 起 `ct-done` 在通知塔台前也會 commit **工單檔本身**，和 `ct-exec` 一樣守「通知前工單已 commit」；
產品變更則不替你 commit，只告訴你哪些看起來還沒 commit（權威見 CT `ct-done/SKILL.md` § Workflow）。

塔台面對中斷的工單：回報區有部分結果 → 開**接續工單**（新編號、參照原工單）；回報區為空 → 重派原工單或改策略開新工單；原工單標記 `INTERRUPTED`。在 BAT 內重派原工單前，塔台先回收舊 Worker 分頁（v5.12.0，見 `bat-integration.md` § 重派前回收舊 Worker 分頁）。

## 工單粒度原則

| 原則 | 說明 |
|------|------|
| **單一職責** | 一張工單 = 一個工作流程或一個明確交付物，不合併多個 |
| **可交付** | Worker 完成後有明確產出 |
| **可中斷** | `PARTIAL` 時可基於已完成部分產生接續工單 |
| **已驗證規模** | 實測參考：6 張工單／90 分鐘／44 檔產出 |

## 回報規範

### 正確的回報方式

```
✅ 「T0001 完成」              ← 帶工單編號
✅ 「LB-T0184 完成」           ← 工單有前綴就帶前綴（完整 ID，v5.13.1）
✅ 「T0003 需要協助」           ← 帶編號 + 狀態訊息
✅ 「T0002 遇到問題，API 回傳 403」← 帶編號 + 一句話描述
```

### 錯誤的回報方式

```
❌ 「做完了」               ← 缺少工單編號
❌ 「T0184 完成」（工單是 LB-T0184）← 截掉前綴，BAT 對不上 Worker 分頁
❌ （貼 200 行 error log）  ← 污染塔台 Context
❌ 「幫我看這段 code」      ← 塔台不碰程式碼
```

細節在工單回報區裡；回到塔台的只是一行指標，讓塔台自己去讀檔。

## 需求對齊協議

塔台在產生工單前，先完成需求對齊：

```
使用者描述需求（不用一次說清楚）
    ↓
塔台複述目標、找出未知項
    ↓
塔台提出有範圍的釐清問題（預設選項式）
    ↓
使用者回答（可以說「不確定」）
    ↓
範圍具體到可執行 → 塔台產生工單
```

最少提問輪數由 `alignment-rounds` 控制（預設 3，`0` = 關閉強制提問）。

---

## 客戶驗收不回歸閘（可選，v5.13.0）

專案進入客戶驗收之後，最傷的往往不是新 BUG，而是修 BUG 時把**已經驗收通過**的功能改壞：客戶要重測，信任也受損。
同一輪連開十幾張修正單時，很容易沒有人回頭核對哪些通過案例會被碰到。

這條規則把核對變成工單的固定一段，由設定 `customer_acceptance_gate` 開關，**預設 `off`**：

- **塔台開單**：會改程式或資料的工單加〈相關通過案例〉段，寫案例表位置、改動範圍與初列的相關案例；只改文件或只讀的研究單不加
- **Worker 動工前**：從案例表找出與改動範圍相關、結果為通過的案例，逐案判定「不受影響」「受影響但預期不變」或「會改變」；
  **會改變就停下**，交使用者裁示（yolo 時問塔台，塔台轉問使用者）
- **回報區**：必填〈相關通過案例判定〉表；沒有相關案例也要寫「無」與查找範圍
- **部署後**：塔台把這些案例列進部署後必跑清單

**為什麼預設關閉**：它只對手上有驗收案例表（每個案例有編號與通過／不通過結果）的專案有意義；沒有案例表的專案開了，
每張工單只會多一段空白。專案真的進入客戶驗收時，由使用者以 `*config customer_acceptance_gate on --save project` 開啟。

> 權威：CT `work-order-template.md` § 撰寫〈相關通過案例〉；Worker 端的規則在 `ct-exec/SKILL.md` § Phase 2。

## BUG 生命週期

BUG 單據有專屬的 6 態狀態機，包含驗證（VERIFY）中間態：

```
🔴 OPEN → 🔧 FIXING → ✅ FIXED → 👀 VERIFY → 🟢 CLOSED
                         │
                         └─ 驗證失敗 → 🔧 FIXING（重新修復）

任何階段 → ⛔ WONTFIX（不修復，需記錄原因）
```

| 狀態 | 說明 | 離開條件 |
|------|------|---------|
| **OPEN** | 已回報，待處理 | 指派修復 → FIXING |
| **FIXING** | 修復中 | 修復完成 → FIXED |
| **FIXED** | 已修復，待驗證 | 驗證通過 → VERIFY；驗證失敗 → 回到 FIXING |
| **VERIFY** | 驗證中 | 確認修復 → CLOSED |
| **CLOSED** | 已關閉 | 終態 |
| **WONTFIX** | 不修復 | 終態，任何階段皆可標記 |

FIXED 與 CLOSED 分開，是為了防止「修了但沒真的修好」：Worker 回報 FIXED 只代表實作完成，要經過驗證才能關閉。

### 結案判準與 `closed_reason`（v5.13.0）

狀態機回答「可以怎麼走」，沒有回答「這張該落在哪」。實際專案裡，未結清單常累積一批早就修好、過時、被取代或其實不是 BUG 的單——
留著會讓人誤判工作量與風險。v5.13.0 補上結案判準，把常見情況對到既有狀態：

| 情況 | 狀態 |
|---|---|
| 現行程式已修好 | `FIXED` |
| 前提錯誤、設計如此 | `CLOSED`（`closed_reason: not_a_defect`） |
| 屬實但不修 | `WONTFIX`（寫進交付文件的已知限制） |
| 過時、被取代、重複 | `CLOSED`（`superseded`／`duplicate`／`obsolete`） |
| 非我方責任 | `CLOSED`（`external`，註明已告知對方） |
| 仍成立但短期不做 | `CLOSED`（`deferred`；列進 `_backlog.md`〈後續待辦〉，要做時重開成 `OPEN`） |
| 仍成立且要做 | 維持 `OPEN`，重新核定嚴重度 |

**為什麼不新增狀態值，而是加一個選填欄位？** BUG 狀態是 CT 與 BAT 共用的契約（兩邊一對一相同），多一個狀態值，BAT 的看板就得跟著改；
把原因寫進 `closed_reason`，看板照舊，人仍看得到為什麼結。另外兩條紀律：**證據不足就維持 `OPEN`，不得猜**；
逐張以**現行程式碼**與後續工單、決策核對，不只看單內記載。

**未結 BUG 清理提示**：未結張數超過 `bug_review_open_threshold`（預設 `20`），或有單超過 `bug_review_stale_days`（預設 `30` 天）沒更新時，
`*sync`／`*insights` 多印一行，建議照判準逐張核對（可以分批派唯讀核對工單）。這只是提示，改不改狀態由塔台依核對結果決定；
改了就同一批重建索引（見 `three-layer-arch.md` § `_bug-tracker.md` 和 `_backlog.md`）。

> 判準、`closed_reason` 的值與提示條件以 CT `bug-plan-system.md` § 結案判準、§ 未結 BUG 清理提示 為準；兩個門檻的值域在 `tower-config.md` § 可用選項。

## PLAN 生命週期

PLAN 單據用於規劃與技術評估：

```
💡 IDEA → 📋 PLANNED → 🔄 IN_PROGRESS → ✅ DONE
                             │
                             └→ ⛔ DROPPED
```

| 狀態 | 說明 | 離開條件 |
|------|------|---------|
| **IDEA** | 初步想法 | 評估可行 → PLANNED |
| **PLANNED** | 已規劃，待實施 | 開始實施 → IN_PROGRESS |
| **IN_PROGRESS** | 實施中（關聯工單執行中） | 完成 → DONE；放棄 → DROPPED |
| **DONE** | 所有關聯工單完成 | 終態 |
| **DROPPED** | 評估後決定不做，需記錄原因 | 終態 |

## EXP 生命週期

EXP（實驗）單據用於結果不確定的技術探索：

```
🧪 EXPLORING → ✅ CONCLUDED
             └→ ⛔ ABANDONED
```

| 狀態 | 說明 |
|------|------|
| **EXPLORING** | 實驗進行中（建立即進入） |
| **CONCLUDED** | 已得出結論並記錄——「這條路不通」也是結論 |
| **ABANDONED** | 實驗無法繼續或已無意義 |

EXP 沒有「失敗」狀態，因為實驗的產出是**知識**而不是功能：證明某方案不可行，同樣是 `CONCLUDED`。
EXP 搭配 git worktree 使用，實驗失敗可零污染丟棄，不影響主線。

## 研究型工單

`type: research` 的工單打破傳統工單「單向指令」的限制。

### 傳統工單 vs 研究型工單

| 比較 | 傳統工單 | 研究型工單 |
|------|---------|-----------|
| 指令方向 | 塔台→Worker（單向） | 塔台↔Worker（雙向） |
| Worker 行為 | 嚴格按指令執行，不主動提問 | 可主動提問、漸進收窄範圍 |
| 收尾內容 | 產出摘要 + 遭遇問題 | + 互動紀錄 + 調查結論 + 建議方向 |
| 結論要求 | 完成／未完成 | 必須「可決策」：發現、選項、推薦、殘餘風險、建議的下一張工單 |
| 適用場景 | 目標明確的開發任務 | 需要調查才能確定方向的任務 |

### 互動由誰決定

Worker 能不能主動提問，依序看：

```
0. CT_MODE=yolo（v5.5.0）：一律不問使用者，改問塔台（見下方〈yolo 提問通道〉），不看以下兩條
1. runtime 的 CT_INTERACTIVE（塔台派工時傳入）：1 = 允許，0 = 禁止
2. 沒有 CT_INTERACTIVE 時，才看工單 frontmatter 的 interaction.interactive
```

`CT_INTERACTIVE` 由塔台派工時以旗標注入（v5.5.0 之前 YOLO 啟動時由塔台先詢問使用者；v5.5.0 起 yolo 不再詢問，一律 `--no-interactive`）。設定檔中的 `research_interaction`（預設 `true`）
屬塔台設定；Worker 不以讀設定檔的方式決定要不要互動——互動與否是 runtime 參數，不是 Worker 自己的狀態。
`research_max_questions` 是每次提問的上限，值域 `1`–`5`，預設 `3`。提問用選項式加「其他」兜底，所有問答都記入回報區。

## yolo 提問通道：Worker 改問塔台（v5.5.0）

yolo 的前提是「人不在旁邊」：Worker 自動送出、塔台自主派下一張。這時 Worker 若用 AskUserQuestion 之類的工具問使用者，
整條流程就停在一個沒人看的分頁上。v5.5.0 的做法是把問題的收件人從使用者換成塔台——塔台本來就在讀工單檔，也握有決策日誌與 PLAN 的全局視角。

### 一次往返

```
Worker 遇到範圍內、自己定不了、猜錯會返工的選擇
  → 在工單回報區最上方寫 ### 待塔台決策（Q-n：問題、含「其他」的選項、建議與理由、影響、是否阻塞）
  → frontmatter 標 tower_question: open，commit 工單，送 T#### 提問
  → 原地等：每 ≥ 30 秒重讀自己的工單檔，直到每一題都出現「塔台答覆 Q-n」行
    （只認 ### 待塔台決策／Renew 區段內、行首 - **塔台答覆 Q-n** 的那一行）
塔台收到 T#### 提問（不是收尾，不收單）
  → 逐題依代決邊界決定 → 在題目下新增一行「塔台答覆 Q-n」→ 記決策日誌與 YOLO 歷程
Worker 讀到答覆 → 記入互動紀錄、刪除 tower_question → 繼續
```

能從工單、決策日誌或專案慣例自己決定的，Worker 不問，自己決定並在回報區寫下理由；提問是留給「猜錯就要返工」的選擇。

這條基本通道只用兩樣既有的東西：**工單檔**與 `bat-notify.mjs`，任何 BAT 版本都能用（v5.7.0 另有 BAT 結構化通道，見下方）。答覆寫在工單裡、由 Worker 自己來讀，
塔台不對 Worker 分頁送任何按鍵——和〈BAT Notify〉「通知只是叫對方來讀檔」是同一個原則。
`塔台答覆 Q-n` 行也是「回報區只由 Worker 填」的唯一例外；Worker 不能預寫空的答覆行，因為它正是靠這一行出現與否判斷答了沒有。

**「出現答覆行」要看格式與位置，不是看字樣（v5.6.1）。** 實機驗收時（T0166），工單的執行步驟本身就寫著「塔台答覆 Q-1」這幾個字，
Worker 用整份檔案搜字樣，第一次檢查就「命中」——不管塔台答了沒有。所以 CT 把判斷收緊成：只認 `### 待塔台決策` 或
`## 塔台補充（Renew #N）` 區段內、行首 `- **塔台答覆 Q-n**` 的那一行；塔台寫答覆也固定用這個格式，Renew 區段也一樣。
這和「通知只是叫對方來讀檔」是同一套思路：工單檔是通道，通道裡的訊號就得有一眼可辨的固定格式。
v5.7.1 再補一個角落：工單本文若用程式碼區塊（fenced code block）貼了範本，區塊裡的 `### 待塔台決策` 標題與答覆行也不算，
CT 給的 `awk` 比對會跳過程式碼區塊。

**送 `提問` 之前，工單要先 commit（v5.6.1）。** 收尾時通知一律排在 commit 之後（上方〈Phase 4〉→〈BAT Notify〉的順序；
隔離工單在〈Worker 在 worktree 裡怎麼工作〉寫成「commit 工單，最後才通知塔台」），v5.6.1 把同一條順序明寫到提問通道：
塔台收到通知時讀到的工單，必須是已經落地的那一版。實機驗收（T0167）抓到的正是備援的 `需要協助` 比工單 commit 早送出，所以兩條路都要守。
權威寫法見 CT `yolo-mode.md` § Worker 向塔台提問 › Worker 端 第 2、4 點與 `ct-exec/SKILL.md` § Questions For Tower。

### BAT 結構化通道（v5.7.0，BAT `>= 0.7.0-pre.7`）

工單檔往返可靠，但慢：Worker 每 30 秒重讀一次檔，codex 這類沒有監看工具的平台甚至只能直接走備援。
BAT `0.7.0-pre.7` 起提供一條結構化的問答通道，v5.7.0 接上它：

```
Worker 照舊寫 ### 待塔台決策 Q-n、標 tower_question: open、commit 工單      ← 這三步不變（雙寫）
  → bat-notify.mjs --ask 提問（題目只經 stdin 傳入；它自己會通知塔台 T#### 提問，不再另送）
  → MCP bat_wait_question 長輪詢等答覆（不能用就改 --wait-answer）
塔台收到 T#### 提問 → MCP bat_list_questions 看到這一題
  → 代決邊界照舊 → bat-terminal.mjs --answer 答覆（工單裡不寫答覆行）→ 記決策日誌與 YOLO 歷程
Worker 收到 answered → 記入互動紀錄、刪除 tower_question → 繼續
```

**為什麼題目還要寫進工單（雙寫）？** BAT 只把題目放在記憶體裡，不寫檔、日誌也不記內容；BAT 重開就沒了。
工單檔是 CT 的紀錄，也是通道失效時的退路：題目已經在檔裡，任何一步失效都能直接回到上面那條工單檔往返，不用重問。
問答的結果一律由 Worker 寫進互動紀錄——BAT 通道成功時，工單裡唯一的答案就在那裡。

**失效時回到工單檔。** 判斷只看 exit code 與回傳狀態，不先去查 BAT 版本：

- BAT 太舊（`--ask` 失敗）→ Worker 在這題下加一行 `- **通道**：工單`、commit 工單，再送一般的 `T#### 提問`，照工單檔往返等（標記是 v5.7.1 加的）；
- BAT 重開過（`lost`）或題目被取消 → Worker 同樣在這題下加 `通道` 標記、commit 工單、送一般的 `T#### 提問`，剩下的時間改等工單答覆行；
  塔台看到標記就在工單寫答覆行（晚退回也加標記是 v5.7.2 加的，理由見下方〈晚退回的題也要加標記〉）；
- 題目過期（`expired`）→ 照下方〈等不到答覆〉走 `BLOCKED` + Renew；
- 塔台這邊 `bat_list_questions` 不能用、題目有 `通道` 標記，或 `--answer` 失敗 → 寫工單答覆行。

所以 BAT 低於 `0.7.0-pre.7` 時，結果和 v5.6.1 一樣（v5.7.1 起只多一行標記與一次 commit）。`worker_question_timeout: 0` 也不用這條通道。

**一次問好幾題時，塔台要等齊（v5.7.1）。** v5.7.0 實機驗收（BAT T0616）發現一個時序問題：Worker 依序送三題 `--ask`，
第一題的通知到塔台時，後面的題還沒登記到 BAT。照 v5.7.0「列表裡看不到就寫工單答覆行」，塔台會在那題送上 BAT 之前就先在工單答掉它，
同一題變成兩個通道都有答覆。使用者選的改法是「塔台等齊，只改 CT」：

- Worker 先把所有題的 `--ask` 送完；送失敗的題加上 `通道` 標記、commit，最後才送一則一般的 `提問`。
- 塔台每收到一則通知，逐題看「BAT 列表裡這題的狀態」加上「工單裡有沒有標記」：有標記 → 工單答覆；列表是 `pending` → BAT 答覆；
  列表裡沒有、也沒有標記 → 這題還在路上，這一則先不答，等同一個 Worker 的下一則通知。

關鍵是**不能拿「列表現在沒有待答題」當作 Worker 已經送完**：塔台剛答完一題時，待答列表本來就會暫時是空的。
Worker 的送出順序保證了每一題在最後一則通知之前，不是已經在 BAT 列表裡、就是已經有標記；萬一一直等不到後續通知，
Worker 逾時走備援、塔台在 Renew 區段答，最壞是慢，不會有題目永遠沒人答。

**晚退回的題也要加標記（v5.7.2）。** v5.7.1 只給 `--ask` 失敗的題加標記；`--ask` 成功之後才被取消或遇到 BAT 重開的題不加，
塔台要靠 BAT 列表裡這題變成 `cancelled` 才知道改在工單答。問題是 BAT 列表不會一直記得已結束的題：只保留 10 分鐘、全 BAT 最多 64 筆、BAT 重開就全清，
而 `lost` 根本不會出現在列表裡。塔台如果晚處理（例如那題先升級給使用者），列表裡已經找不到這題，就只能等 Worker 逾時——不會答錯，但會慢。
v5.7.2 的改法只動 CT：晚退回的題，Worker 也加 `通道` 標記、commit、再送一則一般的 `提問`（同時退回幾題只送一則）。
標記在通知前就已 commit，塔台看工單就知道怎麼答，不必再看 BAT 記不記得。

塔台若在標記寫入前已經照列表的 `cancelled` 在工單答了這題，之後收到 Worker 那則 `提問` 時這題已經有答覆行，就什麼都不做——
同一題仍然只有一個通道的答覆。`--cancel-question` 回報這題其實已經答覆或已過期時，Worker 照已答或備援處理，不加標記。
這一步也是 Worker 等待期間唯一可以寫工單的例外：只加標記行、commit 一次、送一則通知。
不過這次 commit 是以整個工單檔為單位：塔台先前寫進工單、還沒 commit 的答覆行會一起進版控。塔台寫完答覆行本來就不另外 commit，
所以這是預期行為（v5.8.1）——Worker 不動答覆行，可以在回報區註明一句。權威在 CT `yolo-mode.md` § Worker 向塔台提問 › 塔台端 第 3 點。

> 規則的權威在 CT `yolo-mode.md` § Worker 向塔台提問 › Worker 端 3-A 第 6 步、§ 塔台端 第 1 點，BAT 保留規則在同節 § BAT 通道 › 已知限制。

BAT 通道裡，Worker 每次等最多 45 秒，兩次之間不能隔超過 120 秒：這是 BAT 的租約規則，提問的 Worker 超過 120 秒沒來等，
題目就會過期（`expired`），Worker 這時走備援。塔台仍然**不背景輪詢**：只在收到 `提問`，或查狀態看到 Worker
`blocked`／`tower` 時才查 `bat_list_questions`（見 `bat-integration.md` § 斷點 D）。

> 指令、exit code、回傳欄位與「版本判定與降級」表以 CT 的 `yolo-mode.md` § Worker 向塔台提問 › BAT 通道、§ Worker 端 第 3 點、§ 塔台端 為唯一權威；
> BAT 端契約見 BAT `docs/agent-guide/tower-questions.md`。

### 塔台代決的邊界

| 問題的性質 | 誰決定 |
|-----------|-------|
| 工單範圍內的技術／實作選擇 | 塔台代決，記決策日誌 |
| 範圍變更、刪除或不可逆操作、對外發布、需要使用者偏好的選擇 | 塔台先暫停問使用者（`⏸ YOLO PAUSED — 提問需要你決定`），再寫答覆 |

這條線和斷點 C「擴大範圍是人的決定」同一個道理：塔台能自主的只有「在既定範圍內怎麼做」。
提問本身不是斷點，不算 Renew，也不計入 `yolo_max_retries`。

### 等不到答覆：退回 BLOCKED + Renew

等待有上限 `worker_question_timeout`（分鐘；`0` = 不等）。塔台的 `*config` 只在它自己的 session 記憶裡，Worker 看不到，
所以塔台在 yolo 派工前把生效值寫進工單 frontmatter——和 `CT_MODE` 一樣，是「runtime 參數由派工帶進來」（`concepts.md` § Worker 無狀態、塔台有狀態）。

逾時、值為 `0`、BAT 通道回報題目過期（v5.7.0）、要等工單檔卻沒有可用的等待工具（例 codex），或 `提問` 通知送不出去，Worker 就不再等：問題原樣留在工單，
工單收成 `BLOCKED` 並送 `T#### 需要協助`；塔台在 `## 塔台補充（Renew #N）` 區段答覆後重新派工——派的是新 Worker，不對舊分頁送按鍵；
v5.12.0 起在 BAT 內會先請 BAT 回收舊分頁，免得同一張工單有兩個 Worker 分頁（`bat-integration.md` § 重派前回收舊 Worker 分頁）。
走到這一步，它就是一次普通的 `BLOCKED` 與 Renew，照常計入斷點 B。

v5.6.1 依實機驗收（T0167）補了兩個細節，都是為了讓「題目」與「答覆」各只有一份：

- **備援也要標 `tower_question: open`。** 這個欄位是塔台判斷「這張 `BLOCKED` 要在 Renew 區段答題」的依據；
  它是送 `提問` **之前**就要加的，不論 Worker 接下來是原地等，還是因為 `0` 直接走備援。
- **`0` 的時候塔台不在題目下答。** Worker 不會等，塔台若在題目下寫了答覆、之後又在 Renew 區段寫一次，同一題就有兩個答案。
  所以塔台收到 `提問` 時先看：工單是 `worker_question_timeout: 0` 或已經 `BLOCKED`，就等 `需要協助`，只在 Renew 區段答。

### 非 yolo 不變

只有 `CT_MODE=yolo` 走這條通道。`on`／`ask`／`off` 下使用者本來就在場，研究型工單照〈互動由誰決定〉向使用者提問。
v5.5.1 起，Worker 執行期四項防護裡原本要問使用者的地方，yolo 下也改成記錄或問塔台（見 `advanced-patterns.md` § Worker 執行期的四項防護）。

> 格式、等待、備援與代決邊界以 CT 的 `yolo-mode.md` § Worker 向塔台提問 為唯一權威；`worker_question_timeout` 的值域與預設見 CT `tower-config.md`。

## Worker Renew 機制

傳統流程中，塔台要補充資訊必須讓 Worker 結束 session、修改工單、再開新 session。Renew 打破這個限制：

### 運作方式

1. 塔台判斷需要 Renew（而非開新工單），在工單回報區之前新增 `## 塔台補充（Renew #N）` 區段，`renew_count` +1
2. 塔台告訴使用者：「工單已更新，請回 Worker session 說**重讀工單**」
3. **使用者對 Worker 說**觸發詞：「重讀工單」、「renew」、「塔台有新指示」、「工單已更新」
4. Worker **不退出 session**，只讀最新的 Renew 區段，向使用者確認摘要後繼續，不重置已完成的工作
5. 收尾時在回報區「Renew 歷程」逐次記錄

觸發者是**使用者**——Worker 不會自己「請求 Renew」，它需要更多資訊時是回報 `BLOCKED` 或在研究型工單中提問（yolo 下改問塔台，見上方〈yolo 提問通道〉）。

Renew 主要用於研究型工單，但一般工單也可使用。

上面這種「使用者在原分頁說重讀工單」的 Renew 不會回收任何分頁——那個分頁就是要繼續的 Worker。塔台改派**新的** Worker 重跑同一張工單時（例：`BLOCKED`／`FAILED` 之後、yolo 提問備援），v5.12.0 起才會先回收舊分頁，見 `bat-integration.md` § 重派前回收舊 Worker 分頁。

### Renew 還是開新工單

| 情境 | 建議 |
|------|------|
| 方向微調、補充資訊 | Renew 同一張工單 |
| 需要完全不同的調查方向 | 開新工單 |
| Worker context window 接近上限 | 開新工單（帶前一張結論作為輸入） |
| 累計 Renew ≥3 次且無收斂趨勢 | 考慮開新工單重新聚焦 |

### 好處

- 省去 session 重啟的成本
- 保留 Worker 的 context（已讀的程式碼、已做的分析）
- 更流暢的塔台-Worker 協作
