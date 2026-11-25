# 記憶持久化協議

本協議設計為 **AI-agnostic**——任何能讀寫 .md 檔案的 AI Agent 都能使用。

## _tower-state.md（塔台記憶）

存放於 `_ct-workorders/_tower-state.md`，塔台啟動時讀取、運作中更新。

### 標準區段結構（F-22）

#### 機器可讀摘要（YAML frontmatter）

> v6.0.0 新增。本小節是 `_tower-state.md` 機器可讀摘要的**唯一權威定義**，也是 CT 對外（BAT 等外部讀者）的契約；
> 其他文件提到「塔台狀態摘要」都指這裡。欄位依 BAT 契約 v1（BAT D184 回覆稿），v6.1.0 起依 **BAT ↔ CT 契約 v2**（BAT 與 CT 雙方使用者核定）
> 加上下方 § 契約 v2 欄位；**欄位名、型別與語意不得自行修改**，要改先通知 BAT（見下方相容規則）。

**位置**：`_tower-state.md` 第一行 `---` 起的 YAML frontmatter，以下一行 `---` 結束；其後的 Markdown 本文（下方標準區段）照舊。

**欄位**（前 6 列是契約 v1，全部保留、語意不變；後 6 列是契約 v2，v6.1.0+，細節只寫在下方 § 契約 v2 欄位）：

| 欄位 | 必填 | 型別 | 內容 |
|------|------|------|------|
| `schema_kind` | 必填 | 字串，固定 `tower-state` | 讓讀者辨識這是塔台狀態摘要 |
| `summary_version` | 必填 | 整數（≥ 1），目前 `1` | 摘要格式版號；**不加引號** |
| `updated_at` | 必填 | 字串，ISO 8601 含時區 | 摘要最後更新時間；依使用者全域的時間戳規則以 `date "+%Y-%m-%dT%H:%M:%S%z"` 取系統時間，不得手打 |
| `session` | 選填 | 字串，自由文字 | 目前塔台 session 的說明（例：啟動時間＋CT 版號） |
| `next_ids` | 選填 | 開放 map（鍵 → 字串） | 鍵由 CT 決定，外部讀者照原樣顯示，**檔案中的順序即顯示順序** |
| `todo` | 選填 | 字串陣列 | 待辦；外部讀者只顯示**前 5 則** |
| `bat_contract` | v2 必填 | 整數，目前 `2`；**不加引號** | 契約版本。CT 6.1.0 起每次寫入都寫 |
| `ct_version` | v2 必填 | 字串 | 寫入時的 CT 版號 |
| `awaiting_user` | 選填 | 陣列 | 待你決定 |
| `user_actions` | 選填 | 陣列 | 待你執行 |
| `reminders` | 選填 | 陣列 | 到期提醒 |
| `next_ids.user`／`next_ids.action` | 選填 | 字串 `"U-n"`／`"A-n"` | `next_ids` 裡的兩個鍵：下一個待決／待執行編號 |

**CT 的取值慣例**：

- `next_ids` 寫**下一個可用編號**（本文 § 🔢 編號追蹤 的最大編號 + 1，不是最大編號本身）：`workorder: "T0306"`、`decision: "D341"`；
  專案有啟用 BUG／PLAN 時才加 `bug: "BUG-###"`、`plan: "PLAN-###"`；v6.1.0+ 再加 `user: "U-n"`、`action: "A-n"`（下方 § 契約 v2 欄位 › 編號）。
  順序固定為 `workorder`、`decision`、`bug`、`plan`、`user`、`action`。
- `todo` 取自本文 § 🌅 起手式 › 立即待辦 與 § ⏳ 待處理事項：最重要的放前面，一則一句。可以多於 5 則，但第 6 則起外部讀者看不到。
  v6.1.0+：要使用者決定的事放 `awaiting_user`、要使用者自己執行的事放 `user_actions`，`todo` 不重複列（下方 § 契約 v2 欄位）。
- **進行中工單不放進摘要**：外部讀者從 `_ct-workorders/T*.md` 的 frontmatter `status` 自己算，避免兩份資料不一致。
  `todo` 可以寫「等 T#### 完成後做某事」這類待辦，但不要拿它當進行中清單。

**相容規則**：

- 讀者忽略未知鍵、不顯示缺少的選填欄位；YAML 解析失敗時讀者當作沒有摘要。
- **新增欄位不升版**（`summary_version` 維持 `1`）。只有**改掉既有欄位的名稱、型別或語意**才升 `summary_version`，且必須**先通知 BAT**
  （依 [cross-project-coordination.md](cross-project-coordination.md)），等 BAT 回覆再改。
- 契約 v2（v6.1.0+）的欄位是新增，`summary_version` 不升。`bat_contract` 是專門的契約版本欄位，和 `summary_version`（摘要格式版號）是兩件事；
  契約要升 v3 同樣先通知 BAT、雙方核定後才改。

**YAML 寫法**：

- 字串值一律加引號（含 `updated_at`、`next_ids` 的值、每則 `todo`），避免 `:`、`#`、全形符號或時間格式被誤解析；`summary_version`、`bat_contract` 是整數不加引號。
  不含反斜線時用雙引號；**含反斜線 `\`（例：Windows 路徑）時用單引號或改成正斜線**（v6.0.1+）。
- 寫完必須能被一般 YAML parser 解析，每次寫入後自檢。字串寫法、正反例與自檢方法的唯一權威是下方 § YAML frontmatter 字串寫法與寫入後自檢。

範例：

```yaml
---
schema_kind: tower-state
summary_version: 1
bat_contract: 2
ct_version: "6.1.0"
updated_at: "2026-10-25T19:21:43+0800"
session: "2026-10-25 17:48 塔台 session（CT v6.1.0）"
next_ids:
  workorder: "T0306"
  decision: "D341"
  bug: "BUG-012"
  plan: "PLAN-004"
  user: "U-1"
  action: "A-1"
todo:
  - "T0299 完成後開 I4（Worker 端）"
  - "I6b：打包＋Guide 同版號＋Portal 預覽專章"
  - "等 BAT T0701 回覆：指揮塔總覽顯示塔台狀態"
---
```

（有待決、待執行或提醒項目時的完整範例見下方 § 契約 v2 欄位。）

**維護時機**：

- 塔台**每次寫入** `_tower-state.md` 都同步更新摘要（至少刷新 `updated_at`，其餘欄位有變就改）：啟動、派工、收單、決策、
  `*rescan`、收工（Session 結束前）、`*pause`／`*resume`，以及下方 § 自動更新時機 列的每一項。v6.1.0+ 每次寫入也寫 `bat_contract: 2` 與
  `ct_version`（下方 § 契約 v2 欄位）。
- **Fast Path 恢復**：摘要只供外部顯示，塔台恢復狀態**以本文為準**。摘要與本文不一致（例：`next_ids` 不等於 § 🔢 編號追蹤 的最大編號 + 1、
  `todo` 過時）時以本文為準，並在這次寫入時依本文重寫摘要。
  例外（v6.1.0+）：`awaiting_user`、`user_actions`、`reminders` 三個清單**只存在 frontmatter**（本文不重抄），依本文重寫摘要時原樣保留，不得清掉。
- **Full Scan／`*rescan`**：重建本文時一併依新本文重建摘要（同上，三個清單原樣保留）。
- **舊專案沒有摘要**：不是錯誤，恢復啟動不提示補齊（摘要不屬於下方 7 個必要區段）；塔台下次寫入 `_tower-state.md` 時直接補上。不需要遷移工具。
- **首次啟動**（從標準模板建立 `_tower-state.md`）：同時寫入摘要。

```markdown
---
schema_kind: tower-state
summary_version: 1
bat_contract: 2
ct_version: "<CT 版號>"
updated_at: "<datetime>"
next_ids:
  workorder: "T####"
  decision: "D###"
  user: "U-1"
  action: "A-1"
todo:
  - "<最緊急事項>"
---
# 塔台狀態快照 _tower-state.md

## 🌅 起手式（Quick Recovery）
> 最後更新：<datetime>

### 立即待辦
1. <最緊急事項>

### 近期完成摘要
- <關鍵成果>

### 快速連結
- Bug Tracker → [_bug-tracker.md]
- Backlog → [_backlog.md]
- Decision Log → [_decision-log.md]
- Learnings → [_learnings.md]

---

## 📦 基本資訊

| 欄位 | 內容 |
|------|------|
| **專案** | <name> |
| **目前里程碑** | <milestone> |
| **塔台版本** | Control Tower vX.Y.Z |

---

## 🔢 編號追蹤

| 類型 | 最大編號 |
|------|---------|
| 工單 | T#### |
| BUG | BUG-### |
| PLAN | PLAN-### |
| 決策 | D### |
| 待你決定 | U-n（還沒用過寫「—」） |
| 待你執行 | A-n（還沒用過寫「—」） |

---

## 📊 進度快照
<當前 sprint/milestone 狀態>

---

## 📝 本 Session 決策日誌
- D###：<摘要>

---

## ⏳ 待處理事項
- <未結事項>

---

## 🔍 環境快照
> 最後掃描：<datetime>

<Full Scan 結果；`*rescan` 時刷新>
```

#### 契約 v2 欄位（v6.1.0+）

> v6.1.0 新增（6.1.0-pre.1 預覽時加入，6.1.0 納入正式版）。本小節是 **BAT ↔ CT 契約 v2** 在 CT 端的**唯一權威定義**：上方 § 機器可讀摘要 的 v2 欄位、誰寫誰清、回答格式、
> 隱私、時區與筆數。[auto-session.md](auto-session.md)（開工宣告）、[yolo-mode.md](yolo-mode.md)（斷點與提問）、
> [work-order-system.md](work-order-system.md)（派工與收單）、[work-order-template.md](work-order-template.md)（工單 `waiting_user`）、
> [tower-config.md](tower-config.md)（`user_inbox`）與 `SKILL.md`（回覆結尾重列）只寫自己那一步並引用這裡，不重抄規則。
> 依據：BAT 與 CT 雙方使用者核定的契約 v2（BAT GitHub #24）；BAT 待辦分頁怎麼讀、怎麼顯示以 BAT 文件為準。
> 契約 v1 的欄位全部保留、語意不變；`summary_version` 不升。

**用途**：塔台需要使用者決定或執行的事寫進 frontmatter，Better Agent Terminal（BAT）的「待辦」分頁唯讀顯示，
使用者不必在終端往回捲找塔台的提問。塔台開工時也向 BAT 宣告契約版本（[auto-session.md](auto-session.md) § 塔台分頁角色宣告），
兩邊都是 v2 時 BAT 的新功能才啟用。在舊 BAT 或 BAT 以外的終端照樣寫這些欄位，待決事項另外列在每次回覆的結尾（`SKILL.md` § Output Style）。

**頂層欄位**

| 欄位 | 型別 | 寫法 |
|---|---|---|
| `bat_contract` | 整數 `2`，**不加引號** | CT 6.1.0 起**每次**寫 `_tower-state.md` 都寫；`user_inbox: off`、非 BAT 終端也寫（契約版本和要不要寫清單是兩件事） |
| `ct_version` | 字串 | 每次寫入都寫，值取自已安裝的 `control-tower/SKILL.md` 版本註解 `<!-- control-tower-version: X -->` 的 `X`（例 `"6.1.0"`）；BAT 只顯示、不比較 |
| `next_ids.user`／`next_ids.action` | 字串 `"U-n"`／`"A-n"` | 下一個可用編號（見下方〈編號〉） |
| `awaiting_user` | 陣列，≤ 20 筆 | 待你決定；沒有項目時不寫這個鍵 |
| `user_actions` | 陣列，≤ 20 筆 | 待你執行；沒有項目時不寫這個鍵 |
| `reminders` | 陣列，≤ 10 筆 | 到期提醒；沒有項目時不寫這個鍵 |

**`awaiting_user[]` 每筆**

| 鍵 | 型別 | 內容 |
|---|---|---|
| `id` | 字串，`^U-\d+$` | 待決編號 |
| `workorder` | 字串 | 相關工單完整 ID（含前綴）；沒有工單時空字串 `""` |
| `kind` | 字串 | 目前只有 `"decision"` |
| `source` | 字串 | `breakpoint-A`／`breakpoint-B-1`／`breakpoint-B-2`／`breakpoint-C`／`breakpoint-E`／`worker-question`／`tower-question`（觸發點見下方〈誰寫、誰清〉） |
| `summary` | 字串，≤ 120 字 | 一句話說要決定什麼 |
| `options` | 字串陣列，≤ 6 項 | 每項 `<代號> <說明>`；代號 `^[A-Za-z0-9]{1,3}$`、同一筆內不重複（不分大小寫也不重複）。要自由回答時空陣列 `[]`；「其他」不列成選項（使用者本來就可以回自由文字） |
| `created_at` | 字串 | 寫入時間（見下方〈時區〉） |

**`user_actions[]` 每筆**

| 鍵 | 型別 | 內容 |
|---|---|---|
| `id` | 字串，`^A-\d+$` | 待執行編號 |
| `title` | 字串，≤ 120 字 | 要使用者做什麼 |
| `ref` | 字串 | 來源（工單完整 ID、決策 D###、BUG／PLAN 編號）；沒有時空字串 |
| `kind` | 字串 | `verify`（實機驗收）／`run`（要使用者自己跑的指令）／`manual`（手動操作或設定） |
| `command` | 字串，≤ 300 字 | 選填：使用者要執行的指令。含反斜線時用單引號或改正斜線（下方 § YAML frontmatter 字串寫法與寫入後自檢）；不放權杖、祕密 |
| `created_at` | 字串 | 寫入時間 |

**`reminders[]` 每筆**

| 鍵 | 型別 | 內容 |
|---|---|---|
| `id` | 字串，`^[a-z0-9-]{1,40}$` | 必填；例 `"weekly-log-review"` |
| `title` | 字串，≤ 120 字 | 必填 |
| `due_at` | 字串，ISO 日期或日期時間 | 必填；下一次到期，例 `"2026-12-02"` |
| `last_at` | 字串，ISO 日期或日期時間 | 選填；上次做完的時間 |
| `ref` | 字串 | 選填；來源（本地規則編號、PLAN 編號等） |

**編號**

- `U-n`、`A-n` 在專案內遞增、**不重用**（已移除的編號也不再發）。本文 § 🔢 編號追蹤 記最大編號，`next_ids.user`／`next_ids.action` = 最大編號 + 1，
  和其他 `next_ids` 的慣例相同；還沒用過時是 `"U-1"`／`"A-1"`（第一次寫入 v2 欄位時就寫）。

**誰寫、誰清**

- **`awaiting_user`**：塔台停下來要使用者決定時，在**同一次寫入**加一筆；那件事有工單時，工單 frontmatter 同時加 `waiting_user: "U-n"`
  （[work-order-template.md](work-order-template.md) § `waiting_user`）。觸發點：
  - yolo 斷點 A／B-1／B-2／C 暫停、斷點 E（含非 yolo 的 `⏸ 合併前確認`）——`source` 對應 `breakpoint-<斷點>`（[yolo-mode.md](yolo-mode.md) § 斷點判準）；
  - Worker 提問升級給使用者（`⏸ YOLO PAUSED — 提問需要你決定`）——`worker-question`（[yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › 塔台端）；
  - 塔台自己停下來等使用者決定、而且不是同一輪對話就接著做的事（例：收單後要使用者選下一步、跨專案文件要使用者核定）——`tower-question`。
    需求對齊時一來一往的提問不寫。
  - 不寫：斷點 D（不暫停，使用者到 Worker 分頁處理）、使用者中斷。
  - 對使用者顯示的暫停訊息帶上同一個 `U-n`。
  - **移除**：使用者回答後，在同一次寫入移除該筆、清掉工單的 `waiting_user`、決策日誌記一筆（含 `U-n`）。工單取消、重開或那件事不再需要決定時，
    同樣一併移除，決策日誌記原因。
- **`user_actions`**：收單時，回報區列出的「待實機／待使用者執行」項目各寫一筆（[work-order-system.md](work-order-system.md) § 回報處理流程）；
  塔台自己發現要使用者執行的事也可以寫。使用者回 `A-n：完成` → 移除＋決策日誌；回 `A-n：失敗 <說明>` → 移除＋決策日誌，
  塔台依內容開 BUG 或重開工單。原本會寫進 `todo` 的同類項目改寫這裡，`todo` 不重複列。
- **`reminders`**：專案的定期事項（例：每週日誌清查、到某日重跑掃描）。塔台做完時更新 `last_at`／`due_at`；不再需要時移除。
- **不自動遷移**：升級到 6.1.0 時不批次改寫既有的 `todo`；塔台下次處理到該項時再搬到對應清單。
- 三個清單只在 frontmatter（本文不重抄；依本文重寫摘要時原樣保留，見上方 § 機器可讀摘要 › 維護時機）。
- **BAT 只讀**：BAT 不改 CT 的任何檔（包含已回答的項目）；清單裡的項目消失就是已結。

**回答格式與解析**

- 使用者回答的格式：`U-n：<代號或自由文字>`、`A-n：完成`、`A-n：失敗 <說明>`。全形 `：` 與半形 `:` 都接受，冒號前後的空白忽略。
  一則訊息有好幾行回答時逐行處理。
- 回答可能是使用者手打，也可能是 BAT 面板送進塔台分頁的同一行文字，CT 不區分。
- `U-n` 的代號比對：冒號後的文字（去掉前後空白）與該筆某個選項的代號相同（不分大小寫），而且**只命中一個**才算選了該選項；
  否則整段當自由回答。
- 使用者沒寫 `U-n`、但明顯在回答剛顯示的暫停（例：未決只有一筆時直接回 `B`）→ 照那一筆處理，確認行寫出 `U-n`；對不到唯一一筆就問是哪一筆。
- 編號不存在或已結 → 不猜，回一行說明並列出目前未決的編號。
- 塔台處理後回一行確認，例：`U-3 已收到：B → 恢復 T0123`、`A-2 已收到：完成`。使用者之後更正，照新的回答處理並記決策日誌。

**`user_inbox: off`**（[tower-config.md](tower-config.md) § 可用選項）：不寫 `awaiting_user`、`user_actions`，退回 6.0.x 寫法（待決只在終端輸出、
待使用者執行的項目照舊放 `todo`）。`bat_contract`、`ct_version`、`reminders`、`next_ids.user`／`action`、工單 `waiting_user` 照寫，
回覆結尾的重列也照印（只是資料只在終端，BAT 待辦分頁看不到）。

**隱私**：`summary`、`title`、`options`、`command` 不寫祕密、權杖、客戶資料、真實個人資料；需要細節時寫「見 T#### 回報區」。
內容和 CT 原本就寫進 `_tower-state.md`、決策日誌的同一類，`_ct-workorders/` 公開的專案要不要寫由 `user_inbox` 決定。

**時區**：契約 v2 新欄位的日期時間一律寫成 `+08:00` 這種帶冒號的時區：`date "+%Y-%m-%dT%H:%M:%S%:z"`（Git Bash 的 GNU date 支援 `%:z`）；
PowerShell `Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"`。`reminders` 的 `due_at`／`last_at` 可以只寫日期。既有欄位（`updated_at` 等）維持 `+0800`，不改。
同樣取自系統時間，不得手打。

**筆數與大小**：`awaiting_user` ≤ 20、`user_actions` ≤ 20、`reminders` ≤ 10；單筆約 0.5 KB 以內。超過時塔台狀態面板多一行提示
（下方 § 塔台狀態面板），不擋流程；先處理或移除過時的項目。整份 `_tower-state.md`（含 frontmatter）受下方 § BAT 塔台面板讀取契約 › 大小預算 約束。

**寫入後自檢**：照下方 § YAML frontmatter 字串寫法與寫入後自檢。`check-frontmatter.py` v6.1.0 起對 `schema_kind: tower-state` 的檔另檢查本節的
型別、格式與上限（只回報，問題代碼見腳本開頭說明）；寫入前塔台自己先確認選項代號符合格式、不重複，不符就改寫，不交給 BAT 退回自由回答。

完整範例：

```yaml
---
schema_kind: tower-state
summary_version: 1
bat_contract: 2
ct_version: "6.1.0"
updated_at: "2026-11-25T03:10:23+0800"
next_ids:
  workorder: "T0130"
  decision: "D045"
  user: "U-6"
  action: "A-3"
todo:
  - "T0124 完成後派 T0125"
awaiting_user:
  - id: "U-3"
    workorder: "T0123"
    kind: "decision"
    source: "breakpoint-A"
    summary: "T0123 回報字串不符規格，要怎麼收單"
    options: ["A 接受為 DONE，續派下一張", "B 接受為 FAILED", "C 退回 ask 模式"]
    created_at: "2026-11-25T03:10:23+08:00"
user_actions:
  - id: "A-2"
    title: "安裝 0.8.0-pre.2 後做一次完整重裝驗收"
    ref: "T0120"
    kind: "verify"
    command: 'pwsh -NoProfile -File e2e\manual\reinstall-acceptance.ps1'
    created_at: "2026-11-25T03:02:00+08:00"
reminders:
  - id: "weekly-log-review"
    title: "每週日誌清查"
    ref: "PLAN-012"
    last_at: "2026-11-18"
    due_at: "2026-12-02"
---
```

### 必要區段（7 個）

恢復啟動時塔台驗證以下 7 個區段的完整性，缺少的區段提示補齊：

1. **🌅 起手式**：立即待辦 + 近期完成 + 快速連結
2. **📦 基本資訊**：專案名稱 + 里程碑 + 塔台版本
3. **🔢 編號追蹤**：各類型最大編號
4. **📊 進度快照**：當前 sprint/milestone 狀態
5. **📝 本 Session 決策日誌**：精簡版決策紀錄
6. **⏳ 待處理事項**：未結事項列表
7. **🔍 環境快照**：Full Scan 結果與掃描時間。何時走 Fast Path、何時重跑 Full Scan，
   以 [../SKILL.md](../SKILL.md) § Startup Protocol 為準，本節不複述

> `## YOLO 歷程` **不是**必要區段：只在 YOLO 模式下追加的條件區段，
> 位置與格式見 [yolo-mode.md](yolo-mode.md) § `_tower-state.md` 新增 `## YOLO 歷程` 區段。

### 塔台行為

| 情境 | 行為 |
|------|------|
| 首次啟動（無 `_tower-state.md`） | 從標準模板建立，填入專案名稱和初始編號，並寫入機器可讀摘要 |
| 恢復啟動（有 `_tower-state.md`） | 讀取並驗證 7 個必要區段完整性，缺少的區段提示補齊；狀態以本文為準，沒有摘要不提示（下次寫入時補上） |
| 啟動後第一次寫入（首次或恢復都算，v6.0.0-beta.10+） | 在 § 🌅 起手式 寫本 session 的開工條目（時間、CT 版號），條目內記塔台 session id，見下方 § 塔台 session id |
| Session 結束前 | 更新「起手式」（立即待辦 + 近期完成）和「進度快照」，並同步摘要 |

### 塔台 session id（v6.0.0-beta.10+）

> 本小節是塔台記錄自己 session id 的**唯一權威定義**（PLAN-004 ⑥ 第 1 點，D511／D520；之前各專案以本地規則過渡）。
> Worker 端的寫法是 `ct-exec/SKILL.md` § Phase 4 › Session id；讀它的統計是 `ct-insights/references/analysis-rules.md` § Session 用量統計。

塔台 session 沒有工單號，事後統計 token 用量時要靠 session id 找到它的 session 紀錄，並把它認成塔台（歸屬 ⓪）。

- **何時寫**：塔台啟動後第一次寫 `_tower-state.md` 的開工條目時（上方 § 塔台行為）。之後同一個 session 不必重寫。
- **取值**：只讀 `CLAUDE_CODE_SESSION_ID` 這一個變數（bash `printf '%s' "$CLAUDE_CODE_SESSION_ID"`；PowerShell `$env:CLAUDE_CODE_SESSION_ID`），
  或 BAT MCP `bat_whoami` 的 `claudeSessionId`（BAT `>= 0.7.1-pre.1`；兩者相同）。寫入前以
  `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$` 驗證。這是「環境變數只列名稱」唯一允許寫值的例外
  （[auto-session.md](auto-session.md) § BAT 內部終端路由 › 偵測條件）；不得順帶列出其他變數，權杖一律不寫。
- **格式**：開工條目文字裡寫「塔台 session」後接以反引號包住的 uuid，例：`` 塔台 session `<uuid>` ``（`<uuid>` 換成實際的 session id）。
  統計腳本只認這個寫法（「塔台 session」、空白、反引號、uuid、反引號）。
- **拿不到**（變數沒設、不是 UUID、Codex 或其他執行環境、MCP 不可用）：寫「session id 未知」，**不阻擋啟動**。
- **不加進機器可讀摘要**：frontmatter 沒有這個欄位（契約 v1、v2 都沒有）；`session` 欄位照舊是自由文字，不放 session id。
- 開工條目日後被收斂或 `*rescan` 移除時，session id 跟著消失：不必另外保存。統計會退回用第一則訊息 `/control-tower` 與分頁標題判斷塔台；
  已寫好的收單快照（只有數字）不受影響。

### 自動更新時機

以下每一項寫入本文時，都同步更新機器可讀摘要（見上方 § 機器可讀摘要（YAML frontmatter）› 維護時機）。

- 每次處理工單回報後
- 每次做出決策後
- 派發緊急工單後
- 使用者說「存檔」時
- Session 即將結束時（若可偵測）

`_tower-state.md` 也受下方 § BAT 塔台面板讀取契約 › 大小預算 約束；超過預算時照上方 § 標準區段結構 收斂，本文只留必要區段與條件區段的現況。

## BAT 塔台面板讀取契約

> v6.0.0-beta.3 新增。本節是「CT 寫、BAT 指揮塔面板讀」的檔案格式的**唯一權威定義**：大小預算、各檔 BAT 依賴的格式、值域對照、共通規則。
> 各檔的完整格式仍在各自的權威段（下方 § 各檔要求 列出位置），本節只寫 BAT 依賴的部分；其他文件提到「BAT 讀得到」「大小預算」都引用這裡。
> 對照版本：BAT `0.7.1-pre.9`（讀檔、塔台狀態、決策日誌、臭蟲索引與待辦池解析器以 `0.7.1-pre.8` 對照；pre.9 改的讀檔失敗提示與 `critical` 讀法依 BAT 通知，D420／D421）。BAT 改了解析規則，以 BAT 的通知為準再改本節。
> 這裡的「BAT 塔台面板」是 BAT 視窗裡的指揮塔面板（總覽、決策、臭蟲、待辦池、工單各頁），不是上方 § 塔台狀態面板（塔台啟動時自己輸出的面板）。
> **契約 v2**（v6.1.0+）：`_tower-state.md` frontmatter 多了上方 § 契約 v2 欄位，BAT 的「待辦」分頁讀它們；BAT 以狀態檔的 `bat_contract`
> 與塔台分頁的宣告（[auto-session.md](auto-session.md) § 塔台分頁角色宣告）判斷雙方是否都是 v2。契約 v1 的讀法（本節以下各段）不變。

### 大小預算

- **BAT 讀檔上限 524,288 bytes**（512 KiB）。超過就整檔不讀。
- **CT 預算 409,600 bytes（400 KB）**。預算到上限之間的空間，留給提示後到收斂前的幾個 session。
- 以**整個檔**計，`_tower-state.md` 的 frontmatter（含契約 v2 的三個清單）也算在內。`_tower-state.md` 超過預算時先整理 `todo` 的長文
  （一則一句），再照下方 `<收斂方式>` 收斂本文。
- 一律以**磁碟上的 UTF-8 位元組**計，不用字元數估算（中文一字 3 bytes）。量法：bash `stat -c %s <file>`；PowerShell `(Get-Item <file>).Length`。
- **適用檔案**：`_tower-state.md`、`_decision-log.md`、`_bug-tracker.md`、`_backlog.md`、`_tower-config.yaml`，以及熱區每一張 `T*.md`、`BUG-*.md`、`PLAN-*.md`
  （BAT 讀這些檔都走同一個讀檔函式，上限相同）。
- 超過上限時 BAT 各頁的表現（頁面空了或顯示「無法讀取」，都先量檔案大小）：

| BAT 頁 | 讀的檔 | BAT `>= 0.7.1-pre.9` | 更舊的 BAT |
|---|---|---|---|
| 總覽 | `_tower-state.md` | 顯示「無法讀取塔台狀態檔（File too large）」 | 同左 |
| 決策 | `_decision-log.md` | 顯示「無法讀取 <檔名>」，附 KB 數與 512 KB 上限 | **不報錯**，顯示「沒有找到決策」 |
| 臭蟲 | `_bug-tracker.md` | 顯示「無法讀取 <檔名>」，附 KB 數與 512 KB 上限 | **不報錯**，清單是空的 |
| 待辦池 | `_backlog.md` | 顯示「無法讀取 <檔名>」，附 KB 數與 512 KB 上限 | **不報錯**，清單是空的 |
| 工單 | 每張 `T*.md` | 那一張仍列在清單，狀態 UNKNOWN | 那一張從清單消失，不提示 |
| BUG／PLAN 詳情 | 單據檔 | 展開時顯示讀取錯誤 | 同左 |

  BAT `>= 0.7.1-pre.9` 的 Epics、Sprint 頁讀不到時同樣顯示「無法讀取 <檔名>」；檔案不存在照舊顯示空（不是錯誤）。512 KiB 上限沒變（BAT BUG-172）。
- **400 KB 預算保留**：更舊的 BAT 超過上限仍會靜默變空，而塔台不知道使用者裝的 BAT 版本，所以下方的檢查時機與輸出不分 BAT 版本照做（D421）。

**檢查時機**：Startup Protocol（[../SKILL.md](../SKILL.md)）與 `*sync`（[work-order-system.md](work-order-system.md) § 主方法論 tracker 同步 › 同步流程）
量上列的 `_` 開頭熱檔；`*sync` 另量熱區單據檔。只量大小（`stat`），不為此讀內容。結果：

| 大小 | 輸出（一檔一行） |
|---|---|
| ≤ 409,600 | 不輸出 |
| 409,601～524,288 | `⚠️ <檔名> <bytes> bytes，超過 400 KB 預算，建議收斂（<收斂方式>）` |
| > 524,288 | `🔴 <檔名> <bytes> bytes，超過 512 KiB，BAT 塔台面板已讀不到這個檔（<收斂方式>）` |

`<收斂方式>`：`_decision-log.md` → [decision-log-system.md](decision-log-system.md) § 收斂；`_tower-state.md` → 上方 § 自動更新時機 末段；
`_bug-tracker.md`／`_backlog.md` → `*archive`（索引只列熱區單據，歸檔後 `*sync` 重建就會變小）；單張工單或單據 → 把附錄或長篇證據移到另外的檔，工單裡留連結。
提示不阻擋啟動或 `*sync`，塔台不自動收斂。

### 各檔要求

| 檔 | BAT 依賴的格式（摘要） | 完整格式的權威段 |
|---|---|---|
| `_tower-state.md` | frontmatter 摘要：契約 v1 欄位＋契約 v2 欄位（v6.1.0+，`bat_contract: 2`） | 上方 § 機器可讀摘要（YAML frontmatter）、§ 契約 v2 欄位 |
| `_decision-log.md` | 索引表表頭 `ID`；每列 `\|` 開頭與結尾；儲存格內沒有 `\|`；索引表涵蓋熱檔每一筆決策；詳細紀錄標題 `### D### YYYY-MM-DD — 標題`；熱檔沒有其他含 `ID` 欄的表格 | [decision-log-system.md](decision-log-system.md) § 格式規則 |
| `_bug-tracker.md` | 狀態只看 `##` 區段標題；`ID` 以 `BUG-` 開頭；嚴重度格子含英文等級；時間欄 `報修時間`／`關閉時間`；`相關工單` 欄 | [bug-plan-system.md](bug-plan-system.md) § 索引格式 |
| `_backlog.md` | `ID` 以 `PLAN-` 開頭；優先級格子含英文等級；Active 列的 `狀態` 欄蓋過區段；`## Dropped` 表頭 `ID`；只放 BUG 列的區段 BAT 會略過 | [bug-plan-system.md](bug-plan-system.md) § 索引格式 |
| `T*.md`、`BUG-*.md`、`PLAN-*.md` | frontmatter `schema_version: 1`（整數）、`schema_kind`、`status`；沒有 frontmatter 才讀本文元資料。v6.1.0+ 工單的 `waiting_user: "U-n"`（契約 v2，BAT 顯示 ⏸） | [work-order-template.md](work-order-template.md) § PLAN-034 Sprint 2 transition、[bug-plan-system.md](bug-plan-system.md) § PLAN-034 Sprint 2 transition |
| `tower-config.md` § 可用選項 | 表格標題 `### 可用選項` 與欄序 `選項 \| 有效值 \| 預設 \| 說明`（BAT 總覽的預設層讀它）。**可以新增列，不得改標題或欄序** | [tower-config.md](tower-config.md) § 可用選項 |

`_ct-workorders/_insights/`（v6.0.0-beta.10+，例：`_insights/session-stats/<YYYY-MM>.json` 統計快照）**不在** BAT 塔台面板讀取範圍，也不受上方大小預算約束；
它的歸屬見 [data-layer-architecture.md](data-layer-architecture.md) § `_ct-workorders/_insights/`。

表格的共通讀法：BAT 逐列讀表格，trim 後**不是以 `|` 開頭且以 `|` 結尾**的一行就讓表格結束（之後的列被當成新表頭）；儲存格以 `|` 切開，
所以格子裡的 `|`（含 `\|` 與行內 code 裡的 `|`）都會讓欄位錯位，一律改寫成 `／`。

### 值域對照（嚴重度／優先級）

BAT 從索引格子與 PLAN 本文讀等級時，認含 `HIGH`／`MEDIUM`／`LOW` 的字串（不分大小寫）；BAT `>= 0.7.1-pre.9` 起在任何讀取路徑都另把 `critical`（不分大小寫）當 High，
更舊的 BAT 只在讀封存單據的 frontmatter 時這樣做（BAT BUG-173；不新增 Critical 等級）。
CT 的索引格子一律寫 **`🔴 High`／`🟡 Medium`／`🟢 Low`**（emoji 加英文等級），新舊 BAT 都讀得對；單據 frontmatter 照舊可以用 `critical`：

| CT 單據的值（frontmatter `severity`／`priority`，或本文元資料） | 索引格子寫成 | BAT 讀索引／本文 | BAT 讀封存檔 frontmatter |
|---|---|---|---|
| `critical` | `🔴 High（critical）` | High | High |
| `high`、`High`、`🔴`、`🔴 High` | `🔴 High` | High | High |
| `medium`、`Medium`、`🟡`、`🟡 Medium` | `🟡 Medium` | Medium | Medium |
| `low`、`Low`、`🟢`、`🟢 Low` | `🟢 Low` | Low | Low |
| 只寫 `🔴`／`🟡`／`🟢` 的**索引格子**（舊寫法） | —（不再這樣寫） | **Unknown** | 不適用 |
| 只寫 `critical` 的**索引格子** | —（不再這樣寫） | BAT `>= 0.7.1-pre.9`：High；更舊：**Unknown** | 不適用 |

BAT 的 Unknown 只在「全部」篩選看得到，按等級篩選時會漏掉。單據的值不在上表（例：空白、`P0`、`高`）→ 索引格子留空，`*sync` 摘要提示該單缺等級；不得猜。

`_backlog.md` 的 Completed、Dropped 沒有優先級欄：BAT 改讀該 PLAN 檔，取檔內第一個 `priority:`／`優先級：` 的值。
frontmatter 是 `critical` 的 PLAN：BAT `>= 0.7.1-pre.9` 起任何讀取路徑都算 High；更舊的 BAT 在 Completed／Dropped、PLAN 檔補值仍是 Unknown
（Active 區有優先級欄，不受影響）。這是舊版 BAT 讀法的已知差異，CT 端不為它改單據的值。

BUG 狀態值：CT 的 BUG enum（[bug-plan-system.md](bug-plan-system.md) § BUG 單據）與 BAT 一對一相同（`OPEN／FIXING／FIXED／VERIFY／CLOSED／WONTFIX`），
**不新增狀態值**；BAT 從 `_bug-tracker.md` 的區段標題判斷狀態，標題不認得就算 OPEN。

### 共通規則

- **frontmatter 從檔案第一個位元組開始**（第一行就是 `---`）。檔案開頭不要 BOM：除了 `_tower-state.md`，BAT 遇到 BOM 開頭的檔不認 frontmatter。
- `_tower-state.md` 的摘要欄位（含契約 v2 欄位）、工單的 `waiting_user` 與 `tower-config.md` 的 `### 可用選項` 標題與欄序是 BAT 依賴；要改先依 [cross-project-coordination.md](cross-project-coordination.md) 通知 BAT。
- 本節以外改到上表任一檔的格式時，先對照本節；會影響 BAT 讀法的改動同樣先通知 BAT。
- frontmatter 的字串寫法與寫入後自檢見下方 § YAML frontmatter 字串寫法與寫入後自檢。

## YAML frontmatter 字串寫法與寫入後自檢

> v6.0.1 新增。本節是 CT（塔台與 Worker）寫 YAML frontmatter 時**字串怎麼加引號**與**寫完怎麼自檢**的**唯一權威定義**。
> 工單範本、BUG／PLAN／EXP、跨塔台文件、`ct-exec`、`ct-done` 與其他寫 frontmatter 的地方只引用這裡，不另寫規則。
> 起因：BAT 塔台面板讀某個工作區的 `_tower-state.md` 時連續解析失敗，原因是 frontmatter 的雙引號字串裡寫了 Windows 路徑
> （例 `"…\Users\…"`）。YAML 雙引號字串把 `\U`、`\b`、`\m` 這類組合當跳脫序列，不合法的跳脫是語法錯誤，**整份 frontmatter 都讀不到**
> （外部讀者照 § 機器可讀摘要 › 相容規則 當作沒有摘要）。BAT 塔台面板契約 v1 不因本節改變：單引號字串在 YAML 裡一樣是字串，欄位與型別都不變。

> **棄用條款**（v6.0.1 起）：
> v6.0.0 的 § 機器可讀摘要 › YAML 寫法 只寫「字串值一律加雙引號」，沒有提到反斜線。自 v6.0.1 起，**含反斜線 `\` 的值不得寫在雙引號裡**，
> 改用單引號或把路徑改成正斜線（下方 § 字串寫法），而且每次寫完都要自檢（下方 § 寫入後自檢）。
> 若 memory 中有「字串一律雙引號」的舊慣例，以本節為準；塔台可在工單 `memory_overrides` 欄位再明示一次。

### 適用檔案

CT 寫入或修改 frontmatter 的每一個檔：

| 檔 | 欄位與格式的權威段 |
|---|---|
| `_tower-state.md` | 上方 § 機器可讀摘要（YAML frontmatter） |
| 工單 `T*.md`（含專案前綴，例 `LB-T0184-*.md`） | [work-order-template.md](work-order-template.md) § PLAN-034 Sprint 2 transition |
| `BUG-*.md`、`PLAN-*.md`、`EXP-*.md` | [bug-plan-system.md](bug-plan-system.md) § PLAN-034 Sprint 2 transition |
| `_handover-*.md`、`_reply-*.md`（含 ADVISORY） | [cross-project-coordination.md](cross-project-coordination.md) § frontmatter 欄位 |
| 其他由 CT 寫出的 frontmatter（例：`*evolve --skill` 產生的 skill 候選 `SKILL.md`） | 各自的權威段 |

各檔的欄位、型別與必填仍以右欄為準；本節只管字串值怎麼寫與寫完怎麼檢查。

### 字串寫法

| 值的內容 | 寫法 |
|---|---|
| 含反斜線 `\`（Windows 路徑、跳脫字元、正規表示式等） | **單引號**：`'%USERPROFILE%\Documents\proj'`。單引號內不處理跳脫，只有 `'` 本身要寫成兩個 `''`。是路徑的話也可以把分隔改成正斜線後照常用雙引號：`"%USERPROFILE%/Documents/proj"`。**雙引號字串內不寫反斜線** |
| 含雙引號 `"` | 單引號：`'他說 "好" 了'` |
| 其他自由文字（`title`、`todo`、`session`、`delivered` 這類人寫的句子） | **一律加引號**，不含 `\` 和 `"` 時用雙引號（照現行範本）。不加引號時哪些寫法會被 YAML 當成語法，見表下 |
| 時間戳（`created_at`、`updated_at` 等） | 照舊雙引號：`"2026-11-25T00:44:38+0800"`（不含反斜線，安全）；契約 v2 新欄位寫 `+08:00`（上方 § 契約 v2 欄位 › 時區） |
| 整數（`schema_version`、`summary_version`、`bat_contract`、`renew_count` 等）、範本規定不加引號的列舉值與 ID（`status: IN_PROGRESS`、`id: T0549`） | 照各檔範本，不加引號 |

- 不加引號會被 YAML 當成語法的自由文字：含 `: `（冒號加空白）或以冒號結尾、含 ` #`（空白加井號，後面會被當成註解而消失），
  或以 `` ` ``、`*`、`&`、`!`、`[`、`{`、`>`、`|`、`%`、`@`、`'`、`"`、`,`、`- `、`? ` 開頭。
- 同一個值裡同時有 `\`、`"` 和 `'`：用單引號，`'` 寫成 `''`，`\` 和 `"` 照原樣。
- **舊檔不追改**：已經存在、而且仍能正確解析的 frontmatter（例：雙引號內正確寫成 `\\` 的舊值）不必改寫。只有**解析失敗**的才要修；
  修的時機是下一次寫入該檔時（照下方 § 寫入後自檢），不另開全面改寫。

正反例：

| # | ❌ 會解析失敗或讀錯 | 為什麼 | ✅ 正確寫法 |
|---|---|---|---|
| 1 | `- "改 %USERPROFILE%\Documents\proj 的設定"` | `\D` 不是合法跳脫，整份 frontmatter 讀不到（`\U` 開頭的 `\Users\` 也一樣：`\U` 要接 8 個十六進位數字） | `- '改 %USERPROFILE%\Documents\proj 的設定'` 或 `- "改 %USERPROFILE%/Documents/proj 的設定"` |
| 2 | `workdir: "..\repo\my-project"` | `\m` 不是合法跳脫；`\r` 雖然合法，卻被讀成歸位字元（單獨出現時**不報錯但值錯了**） | `workdir: '..\repo\my-project'` 或 `workdir: "../repo/my-project"` |
| 3 | `title: 'Tower's 待辦'` | 單引號在 `Tower` 後就結束，後面多出文字 | `title: 'Tower''s 待辦'` 或 `title: "Tower's 待辦"` |
| 4 | `title: "他說 "好" 了"` | 雙引號在 `他說 ` 後就結束 | `title: '他說 "好" 了'` |
| 5 | `title: 決策: 受理` | 第二個 `: ` 被當成另一層 mapping | `title: "決策: 受理"` |
| 6 | `` - `isolation` 不隔離 `` | `` ` `` 是 YAML 保留字元，不能當值的開頭 | `` - "`isolation` 不隔離" `` |

完整範例（`_tower-state.md` 摘要的 `todo` 寫到路徑時）：

```yaml
---
schema_kind: tower-state
summary_version: 1
updated_at: "2026-11-25T00:44:38+0800"
todo:
  - '確認 %USERPROFILE%\Documents\proj 的安裝路徑'
  - "或改寫成正斜線：%USERPROFILE%/Documents/proj"
  - "T0549 完成後通知 BAT 塔台"
---
```

### 寫入後自檢

**時機**：塔台與 Worker **每次寫入或修改**上述檔案的 frontmatter 之後、commit 之前，對**這次寫的檔**跑一次檢查：
塔台寫 `_tower-state.md`、建立或修改工單、BUG／PLAN／EXP、`_handover`／`_reply`、收單改狀態或補記 `session_ids`；Worker 開工改狀態、
寫 `tower_question`、收尾寫狀態與 `session_ids`（`ct-exec`、`ct-done`）。v6.0.2+ 另有 `*sync` 每次對熱區跑一次、只回報不修
（[work-order-system.md](work-order-system.md) § 主方法論 tracker 同步 › 同步流程 第 6 步）。

**方法**（依序取第一個能用的）：

1. **隨 skill 附的檢查腳本**（只用 Python 標準函式庫，不需要 PyYAML）：

   ```bash
   python -X utf8 -I -B <control-tower>/scripts/check-frontmatter.py _ct-workorders/T0549-example.md   # 一個或多個檔
   python -X utf8 -I -B <control-tower>/scripts/check-frontmatter.py _ct-workorders/                   # 整個目錄的 *.md（不含子目錄）
   ```

   `<control-tower>` 是已安裝的 `control-tower` skill 目錄（例：Claude Code `~/.claude/skills/control-tower`、Codex `~/.codex/skills/control-tower`；
   plugin 安裝則在 plugin 的 `skills/control-tower`）。exit `0` = 全部通過、`1` = 有問題、`2` = 用法錯誤或路徑不存在。
   檢查項目與輸出格式寫在腳本開頭的說明；環境裡有 PyYAML 時，腳本會再做一次完整解析。
2. **腳本不在**（例：Worker 端只裝了 `ct-exec`、找不到 `control-tower`）→ 用環境裡現成的 YAML 解析器（PyYAML、node `yaml`／`js-yaml`），
   只印問題描述與行號。PyYAML 的例子：先用 Write 工具把下面的程式寫到 scratchpad 檔（例 `check_fm.py`；v6.0.2+ 不用 heredoc，
   規則見 `ct-exec/SKILL.md` § Long Content Via Files），再執行 `python -X utf8 -B <scratchpad>/check_fm.py <檔>`
   （不加 `-I`：PyYAML 若裝在使用者層 site-packages，`-I` 會找不到它）：

   ```python
   import sys, yaml
   lines = open(sys.argv[1], encoding='utf-8').read().splitlines()
   end = lines.index('---', 1)
   try:
       yaml.safe_load(chr(10).join(lines[1:end]))
       print('OK')
   except yaml.YAMLError as e:
       mark = getattr(e, 'problem_mark', None)
       print('FAIL', sys.argv[1], 'line', (mark.line + 2) if mark else '?', getattr(e, 'problem', ''))
   ```

   不要直接印例外全文：PyYAML 的例外訊息會附上原文片段。
3. **兩者都沒有** → 至少找出 frontmatter 裡「雙引號內有反斜線」的行，只印檔名與行號，再逐行人工確認（改成單引號或正斜線最省事）：

   ```bash
   awk 'NR==1 && $0 != "---" {exit} NR>1 && $0 == "---" {exit} /"[^"]*\\/ {print FILENAME ":" NR}' <檔>
   ```

**失敗時**：當場照上方 § 字串寫法 修正，再檢查一次，直到通過才繼續；**不得 commit 解析失敗的檔**。工單回報或塔台輸出提到檢查結果時，
同樣只寫檔名、行號與問題類型。

**不阻擋**：自檢只管「這次寫的檔」。塔台啟動時讀到解析失敗的 frontmatter（例：別的 session 寫壞的 `_tower-state.md`）不阻擋啟動：
狀態照舊以本文為準（§ 機器可讀摘要 › 維護時機），下次寫入時整段重寫摘要並自檢。全面盤點（例：對整個 `_ct-workorders/` 跑腳本）找到的舊檔
只回報給塔台，由塔台決定何時修。**檢查失敗的訊息不得印出檔案原文全文**（腳本本身只印檔名、行號、欄號與問題類型）。

## 塔台狀態面板

> v5.2.1 新增。本節是塔台狀態面板的**唯一權威定義**；其他文件寫的「主面板」「啟動面板」「Tower status panel」
> 都指這個面板。`SKILL.md` § Startup Protocol、[auto-session.md](auto-session.md)、[yolo-mode.md](yolo-mode.md)、
> [migration-engine.md](migration-engine.md) 只引用這裡，不另列欄位。

Startup Protocol 顯示面板那一步（[../SKILL.md](../SKILL.md) § Startup Protocol）依本節輸出。

**面板是格式範本**：欄位有資料就顯示，沒有的寫「未知」。**不得為了填欄位去跑額外掃描**；
何時跑 Full Scan 仍只依 `SKILL.md` § Startup Protocol。

### 欄位（最小集合）

| 欄位 | 內容 | 資料來源 |
|------|------|---------|
| 分支／HEAD | 目前分支與 HEAD 短 hash | git |
| 工作區 | 髒檔摘要（修改／未追蹤的數量，或「乾淨」） | `git status --short` |
| 進行中工單 | 非終態工單的 ID + 狀態（例 `T0140 IN_PROGRESS`），沒有寫「無」 | Startup Protocol 的熱區工單計數與各單 frontmatter `status` |
| 下一個工單編號 | 最大工單編號 + 1 | `_tower-state.md` § 🔢 編號追蹤 |
| BAT | `可派發` / `不可派發` / `shell env visibility mismatch` / `不可派發（Worker 分頁）`；環境有 `BAT_TOWER_TERMINAL_ID` 時一律取 `不可派發（Worker 分頁）`（v5.2.5+），不再看前三個值 | 前三個值的判定規則見 [auto-session.md](auto-session.md) § BAT 內部終端路由 › 偵測條件（mismatch 依該處規則仍可派發，標出是為了排查）；Worker 分頁依同檔 § BAT 內部終端路由 › 範圍權杖與分頁角色，只看 env，不另跑掃描 |
| auto-session | 生效值與來源層（`session` / `project` / `global` / `defaults`） | [tower-config.md](tower-config.md) § 三層設定架構 |
| 分頁標題 | `已設定` / `不支援（BAT 太舊）` / `略過（非 BAT）` | 何時取哪個值見 [auto-session.md](auto-session.md) § 塔台分頁角色宣告（第 1 點呼叫條件、第 5 點 exit code），本節不複述 |
| BAT 契約（v6.1.0+） | `v2` / `不支援（BAT 太舊）` / `未知（宣告失敗）` / `略過（非 BAT）` | 同一次宣告的結果；何時取哪個值見 [auto-session.md](auto-session.md) § 塔台分頁角色宣告 第 5 點，本節不複述 |
| 立即待辦 | 待辦清單 | `_tower-state.md` § 🌅 起手式 › 立即待辦 |

**塔台 session 名稱提示**（v5.9.0+，BAT `>= 0.7.1-pre.1`）：不是欄位，是面板最後加的一行提示。

- 顯示條件（全部成立）：在 BAT 內；Startup Protocol 的 `--set-role tower` 那一步已處理（不論 exit code）；MCP `bat_whoami` 可用，
  且回傳**有** `claudeSessionName` 鍵；值不以 ` · Tower` 結尾（含 `null`）。
- 提示內容（一行，措辭可調）：`提示：用 BAT「以塔台開啟 Claude」開塔台，其他專案的塔台就能在跨 session 清單直接找到你`。
- 不顯示、不報錯、不另查：鍵不存在（舊 BAT）、MCP 不可用或回錯誤、非 BAT。這與上方「不得為了填欄位去跑額外掃描」一致：
  `bat_whoami` 只在啟動時查這一次，不為它改跑其他查詢。
- 只在啟動時判斷一次，不重複提示；不阻擋啟動；不替使用者改名、不要求 BAT 改名。
- 判斷「以 ` · Tower` 結尾」而不是「含 `Tower`」：工作區名稱本身可能含 `Tower`（例 `BMad-Control-Tower · <短 id>`）。
  名稱格式見 [cross-project-coordination.md](cross-project-coordination.md) § 跨 session 選收件人，欄位見 [auto-session.md](auto-session.md) § BAT MCP 唯讀 tool。

**契約 v2 提示行**（v6.1.0+）：也不是欄位，是 `分頁標題`、`BAT 契約` 之後、`立即待辦` 之前的提示，各一行、沒有就不印：

- **降級提示**：`BAT 契約` 是 `不支援（BAT 太舊）` 時印一行；文字只定義在 [auto-session.md](auto-session.md) § 塔台分頁角色宣告 第 5 點（含 BAT 最低版號），本節不複述。
- **hooks 提示**：同一次宣告輸出 `hooks: none (<代號>)`（或 BAT 回報 plugin 過舊）時印一行；代號與文字對照只在同處，`hooks: ok …`、`hooks: n/a (codex)` 不印。
- **筆數提示**：`awaiting_user` 超過 20 筆、`user_actions` 超過 20 筆或 `reminders` 超過 10 筆時印一行
  `⚠️ 待辦清單筆數超過上限（<清單> <N> 筆，上限 <M>）：請先處理或移除過時項目`；不擋啟動（上限見上方 § 契約 v2 欄位）。

auto-session 生效值為 `yolo` 時，面板**下方**接 YOLO 警語區塊；位置、字樣與內容以
[yolo-mode.md](yolo-mode.md) § 啟動面板警語 為準，本節不複述。

面板或任何輸出對使用者提到某個分頁時，用分頁標題，不用 terminal ID；規則見 [auto-session.md](auto-session.md) § 對使用者描述分頁，本節不複述。

### 範本

```
═══ 🗼 Control Tower — <專案> ═══
  分支／HEAD：<branch> @ <short-hash>
  工作區：<N 修改 / M 未追蹤 | 乾淨>
  進行中工單：<T#### <status>, … | 無>
  下一個工單編號：T####
  BAT：<可派發 | 不可派發 | shell env visibility mismatch | 不可派發（Worker 分頁）>
  auto-session：<yolo|ask|off|on>（來源：<session|project|global|defaults>）
  分頁標題：<已設定 | 不支援（BAT 太舊）| 略過（非 BAT）>
  BAT 契約：<v2 | 不支援（BAT 太舊）| 未知（宣告失敗）| 略過（非 BAT）>
  [⚠️ <降級提示>]                                   ← 只在 BAT 契約為「不支援（BAT 太舊）」時
  [<hooks 提示>]                                    ← 只在 hooks: none／plugin 過舊時
  [⚠️ 待辦清單筆數超過上限（…）]                     ← 只在超過上限時
  立即待辦：
    1. <取自 _tower-state.md § 起手式>
  [提示：用 BAT「以塔台開啟 Claude」開塔台，其他專案的塔台就能在跨 session 清單直接找到你]   ← 只在上方顯示條件成立時
═══════════════════════════════
```

欄位順序與框線樣式可依 agent 介面調整；欄位不得少於上表。

## _decision-log.md（決策日誌）

存放於 `_ct-workorders/_decision-log.md`，記錄所有非自明的決策及其理由。
檔案位置、格式規格、D### 編號與記錄流程，以 [decision-log-system.md](decision-log-system.md) 為唯一權威定義，
本節不複述；以下只補充「哪些決策值得記錄」的判準。

### 記錄標準

記錄以下類型的決策：
- 使用者提出的問題 + 塔台的判斷
- 流程順序的選擇（先做 A 還是先做 B）
- 技術 / 非技術的邊界判斷
- 跳過或新增步驟的理由
- **使用者糾正**（最高價值——記錄原決策和修正後決策）

### 不記錄

- 自明的決策（「PRD 之後做 Architecture」）
- 使用者明確指令（「幫我建工單」）

## 三層資料持久化

塔台的持久化資料分三層存儲（詳見 [data-layer-architecture.md](data-layer-architecture.md)）：

| 層 | 路徑 | 持久性 | 升級影響 |
|----|------|--------|---------|
| Layer 1 | `~/.claude/skills/control-tower/` | 升級時整份覆寫 | 內容重置為新版 |
| Layer 2 | `~/.claude/control-tower-data/` | 跨專案持久保存 | 不受影響 |
| Layer 3 | `_ct-workorders/` | 專案內持久保存 | 不受影響 |

> 本表只描述**持久性與升級影響**。Layer 1 的寫入權限範圍與唯一例外，
> 見 [data-layer-architecture.md](data-layer-architecture.md) § 寫入規則（唯一權威定義）。

### Layer 2 在記憶協議中的角色

Layer 2（`~/.claude/control-tower-data/`）作為**跨專案持久化儲存層**：

- **全局設定**（`config.yaml`）：跨專案共用的塔台行為設定
- **全局學習**（`learnings/`）：從多個專案晉升的決策模式和反模式
- **全局 Playbook**（`playbooks/`）：跨專案可複用的操作範本
- **專案索引**（`project-registry.md`）：所有使用塔台的專案登記
- **擴展規則**（`extensions/`）：使用者自訂的塔台行為擴展

### 狀態恢復時的資料讀取順序

1. Layer 3：`_tower-state.md`、`_decision-log.md`、`_learnings.md`（專案狀態，最高優先）
2. Layer 2：`config.yaml`、`learnings/`（全局設定和學習）
3. Layer 1：SKILL.md 內建預設值（僅當 Layer 2/3 缺失時）

## 跨 Agent 狀態恢復

不同 AI Agent（Claude → GPT → Gemini）接手塔台時：

1. 讀取 `_tower-state.md` → 恢復進度
2. 讀取 `_decision-log.md` → 理解決策脈絡
3. 讀取 `_learnings.md` → 載入學習經驗
4. 掃描 `_ct-workorders/T*.md` → 驗證事實狀態
5. 顯示：
```
🔄 塔台狀態恢復完成
   上次 Agent：Claude Code Opus 4
   當前 Agent：[本次 AI]
   進度表：已載入
   決策日誌：N 筆決策
   學習紀錄：N 個模式
```
