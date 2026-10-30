# 記憶持久化協議

本協議設計為 **AI-agnostic**——任何能讀寫 .md 檔案的 AI Agent 都能使用。

## _tower-state.md（塔台記憶）

存放於 `_ct-workorders/_tower-state.md`，塔台啟動時讀取、運作中更新。

### 標準區段結構（F-22）

#### 機器可讀摘要（YAML frontmatter）

> v5.13.0 新增。本小節是 `_tower-state.md` 機器可讀摘要的**唯一權威定義**，也是 CT 對外（BAT 等外部讀者）的契約；
> 其他文件提到「塔台狀態摘要」都指這裡。欄位依 BAT 契約 v1（BAT D184 回覆稿），**欄位名、型別與語意不得自行修改**，
> 要改先通知 BAT（見下方相容規則）。

**位置**：`_tower-state.md` 第一行 `---` 起的 YAML frontmatter，以下一行 `---` 結束；其後的 Markdown 本文（下方標準區段）照舊。

**欄位**：

| 欄位 | 必填 | 型別 | 內容 |
|------|------|------|------|
| `schema_kind` | 必填 | 字串，固定 `tower-state` | 讓讀者辨識這是塔台狀態摘要 |
| `summary_version` | 必填 | 整數（≥ 1），目前 `1` | 摘要格式版號；**不加引號** |
| `updated_at` | 必填 | 字串，ISO 8601 含時區 | 摘要最後更新時間；依使用者全域的時間戳規則以 `date "+%Y-%m-%dT%H:%M:%S%z"` 取系統時間，不得手打 |
| `session` | 選填 | 字串，自由文字 | 目前塔台 session 的說明（例：啟動時間＋CT 版號） |
| `next_ids` | 選填 | 開放 map（鍵 → 字串） | 鍵由 CT 決定，外部讀者照原樣顯示，**檔案中的順序即顯示順序** |
| `todo` | 選填 | 字串陣列 | 待辦；外部讀者只顯示**前 5 則** |

**CT 的取值慣例**：

- `next_ids` 寫**下一個可用編號**（本文 § 🔢 編號追蹤 的最大編號 + 1，不是最大編號本身）：`workorder: "T0306"`、`decision: "D341"`；
  專案有啟用 BUG／PLAN 時才加 `bug: "BUG-###"`、`plan: "PLAN-###"`。順序固定為 `workorder`、`decision`、`bug`、`plan`。
- `todo` 取自本文 § 🌅 起手式 › 立即待辦 與 § ⏳ 待處理事項：最重要的放前面，一則一句。可以多於 5 則，但第 6 則起外部讀者看不到。
- **進行中工單不放進摘要**：外部讀者從 `_ct-workorders/T*.md` 的 frontmatter `status` 自己算，避免兩份資料不一致。
  `todo` 可以寫「等 T#### 完成後做某事」這類待辦，但不要拿它當進行中清單。

**相容規則**：

- 讀者忽略未知鍵、不顯示缺少的選填欄位；YAML 解析失敗時讀者當作沒有摘要。
- **新增欄位不升版**（`summary_version` 維持 `1`）。只有**改掉既有欄位的名稱、型別或語意**才升 `summary_version`，且必須**先通知 BAT**
  （依 [cross-project-coordination.md](cross-project-coordination.md)），等 BAT 回覆再改。

**YAML 寫法**：

- 字串值一律加雙引號（含 `updated_at`、`next_ids` 的值、每則 `todo`），避免 `:`、`#`、全形符號或時間格式被誤解析；`summary_version` 是整數不加引號。
- 寫完必須能被一般 YAML parser 解析（例：`uv run --no-project --with pyyaml python -c "…yaml.safe_load(…)"`）。

範例：

```yaml
---
schema_kind: tower-state
summary_version: 1
updated_at: "2026-10-25T19:21:43+0800"
session: "2026-10-25 17:48 塔台 session（CT v5.13.0）"
next_ids:
  workorder: "T0306"
  decision: "D341"
  bug: "BUG-012"
  plan: "PLAN-004"
todo:
  - "T0299 完成後開 I4（Worker 端）"
  - "I6b：打包＋Guide 同版號＋Portal 預覽專章"
  - "等 BAT T0701 回覆：指揮塔總覽顯示塔台狀態"
---
```

**維護時機**：

- 塔台**每次寫入** `_tower-state.md` 都同步更新摘要（至少刷新 `updated_at`，其餘欄位有變就改）：啟動、派工、收單、決策、
  `*rescan`、收工（Session 結束前）、`*pause`／`*resume`，以及下方 § 自動更新時機 列的每一項。
- **Fast Path 恢復**：摘要只供外部顯示，塔台恢復狀態**以本文為準**。摘要與本文不一致（例：`next_ids` 不等於 § 🔢 編號追蹤 的最大編號 + 1、
  `todo` 過時）時以本文為準，並在這次寫入時依本文重寫摘要。
- **Full Scan／`*rescan`**：重建本文時一併依新本文重建摘要。
- **舊專案沒有摘要**：不是錯誤，恢復啟動不提示補齊（摘要不屬於下方 7 個必要區段）；塔台下次寫入 `_tower-state.md` 時直接補上。不需要遷移工具。
- **首次啟動**（從標準模板建立 `_tower-state.md`）：同時寫入摘要。

```markdown
---
schema_kind: tower-state
summary_version: 1
updated_at: "<datetime>"
next_ids:
  workorder: "T####"
  decision: "D###"
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
| Session 結束前 | 更新「起手式」（立即待辦 + 近期完成）和「進度快照」，並同步摘要 |

### 自動更新時機

以下每一項寫入本文時，都同步更新機器可讀摘要（見上方 § 機器可讀摘要（YAML frontmatter）› 維護時機）。

- 每次處理工單回報後
- 每次做出決策後
- 派發緊急工單後
- 使用者說「存檔」時
- Session 即將結束時（若可偵測）

`_tower-state.md` 也受下方 § BAT 塔台面板讀取契約 › 大小預算 約束；超過預算時照上方 § 標準區段結構 收斂，本文只留必要區段與條件區段的現況。

## BAT 塔台面板讀取契約

> v5.13.0 新增。本節是「CT 寫、BAT 指揮塔面板讀」的檔案格式的**唯一權威定義**：大小預算、各檔 BAT 依賴的格式、值域對照、共通規則。
> 各檔的完整格式仍在各自的權威段（下方 § 各檔要求 列出位置），本節只寫 BAT 依賴的部分；其他文件提到「BAT 讀得到」「大小預算」都引用這裡。
> 對照版本：BAT `0.7.1-pre.9`（讀檔、塔台狀態、決策日誌、臭蟲索引與待辦池解析器以 `0.7.1-pre.8` 對照；pre.9 改的讀檔失敗提示與 `critical` 讀法依 BAT 通知，D420／D421）。BAT 改了解析規則，以 BAT 的通知為準再改本節。
> 這裡的「BAT 塔台面板」是 BAT 視窗裡的指揮塔面板（總覽、決策、臭蟲、待辦池、工單各頁），不是上方 § 塔台狀態面板（塔台啟動時自己輸出的面板）。

### 大小預算

- **BAT 讀檔上限 524,288 bytes**（512 KiB）。超過就整檔不讀。
- **CT 預算 409,600 bytes（400 KB）**。預算到上限之間的空間，留給提示後到收斂前的幾個 session。
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

**檢查時機**：Startup Protocol（[../SKILL.md](../SKILL.md)）與 `*sync`（[work-order-system.md](work-order-system.md) § sprint-status.yaml 同步 › 同步流程）
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
| `_tower-state.md` | frontmatter 摘要契約 v1 | 上方 § 機器可讀摘要（YAML frontmatter） |
| `_decision-log.md` | 索引表表頭 `ID`；每列 `\|` 開頭與結尾；儲存格內沒有 `\|`；索引表涵蓋熱檔每一筆決策；詳細紀錄標題 `### D### YYYY-MM-DD — 標題`；熱檔沒有其他含 `ID` 欄的表格 | [decision-log-system.md](decision-log-system.md) § 格式規則 |
| `_bug-tracker.md` | 狀態只看 `##` 區段標題；`ID` 以 `BUG-` 開頭；嚴重度格子含英文等級；時間欄 `報修時間`／`關閉時間`；`相關工單` 欄 | [bug-plan-system.md](bug-plan-system.md) § 索引格式 |
| `_backlog.md` | `ID` 以 `PLAN-` 開頭；優先級格子含英文等級；Active 列的 `狀態` 欄蓋過區段；`## Dropped` 表頭 `ID`；只放 BUG 列的區段 BAT 會略過 | [bug-plan-system.md](bug-plan-system.md) § 索引格式 |
| `T*.md`、`BUG-*.md`、`PLAN-*.md` | frontmatter `schema_version: 1`（整數）、`schema_kind`、`status`；沒有 frontmatter 才讀本文元資料 | [work-order-template.md](work-order-template.md) § PLAN-034 Sprint 2 transition、[bug-plan-system.md](bug-plan-system.md) § PLAN-034 Sprint 2 transition |
| `tower-config.md` § 可用選項 | 表格標題 `### 可用選項` 與欄序 `選項 \| 有效值 \| 預設 \| 說明`（BAT 總覽的預設層讀它）。**可以新增列，不得改標題或欄序** | [tower-config.md](tower-config.md) § 可用選項 |

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
- `_tower-state.md` 的摘要欄位與 `tower-config.md` 的 `### 可用選項` 標題與欄序是 BAT 依賴；要改先依 [cross-project-coordination.md](cross-project-coordination.md) 通知 BAT。
- 本節以外改到上表任一檔的格式時，先對照本節；會影響 BAT 讀法的改動同樣先通知 BAT。

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
