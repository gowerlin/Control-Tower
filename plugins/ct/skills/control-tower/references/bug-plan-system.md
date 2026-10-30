# 多單據類型系統（BUG / PLAN / EXP）

> Control Tower v4 擴展：在標準工單（T####）之外，新增 BUG、PLAN、EXP 三種專用單據類型。
> 所有新類型**預設關閉**，透過 `*config` 啟用。索引檔（`_bug-tracker.md`、`_backlog.md`）格式的唯一權威定義在 § 索引格式。

## 類型總覽

| 類型 | 檔名格式 | 用途 | 啟用設定 | 預設 |
|------|---------|------|---------|------|
| Work Order | `T####-description.md` | 標準任務（不變） | 永遠啟用 | 是 |
| Bug Report | `BUG-###-description.md` | Bug 追蹤 | `enable_bug_tracking: true` | 否 |
| Plan | `PLAN-###-description.md` | 規劃/想法 | `enable_plan_tracking: true` | 否 |
| Experiment | `EXP-[TOPIC]-###-description.md` | 實驗性工作 | `enable_experiments: true` | 否 |

## 索引格式

> v5.13.0 新增（5.12.8 以前本檔指向「SKILL.md `*sync` 段落」，該段落不存在）。

本節是 `_bug-tracker.md`、`_backlog.md` 格式的**唯一權威定義**（D360；照 CT 開發 repo 現行兩檔的實際格式寫成）。`*sync` 每次整檔重寫
（frontmatter 與 body 一起，§ PLAN-034 Sprint 2 transition 元資料解析規則）；啟用後第一次 `*sync` 產生索引時用同一格式。
BAT 指揮塔面板的「臭蟲」「待辦池」只讀這兩個索引，不讀個別單據（展開詳情時才讀），所以**改了 BUG／PLAN 狀態就要重建索引**（§ BUG 單據 › `*sync` 整合）。
BAT 依賴的部分、值域對照與大小預算以 [memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 為準；改格式前先對照該節。

**frontmatter**（兩檔共通）：

| 欄位 | `_bug-tracker.md` | `_backlog.md` |
|------|-------------------|---------------|
| `schema_version` | `1` | `1` |
| `schema_kind` | `index` | `index` |
| `id` | `_bug-tracker` | `_backlog` |
| `index_kind` | `bugs` | `plans` |
| `generated_at` | 產生時的系統時間，帶引號的 ISO 8601＋時區 | 同左 |
| `generator` | `control-tower-sync` | `control-tower-sync` |
| `source_globs` | `_ct-workorders/BUG-*.md` | `_ct-workorders/PLAN-*.md` |
| `exclude_globs` | `_ct-workorders/_archive/**`、`_ct-workorders/examples/**` | 同左 |
| `total` | 熱區 BUG 單總數 | 熱區 PLAN 單總數 |
| `breakdown` | `OPEN`、`FIXING`、`FIXED`、`VERIFY`、`CLOSED`、`WONTFIX` 各自的張數（0 也要列） | `IDEA`、`PLANNED`、`IN_PROGRESS`、`DONE`、`DROPPED` 各自的張數（0 也要列） |

list 欄位用 YAML block list。

**`_bug-tracker.md` body**（依 § BUG 單據 › `*sync` 整合 的狀態分配）：

```markdown
# Bug Tracker

> ⚠️ 此文件由 `*sync` 自動生成，請勿手動編輯。
> 最後同步：<YYYY-MM-DD HH:MM> (UTC+8) — <這次同步的一句說明>

## 統計
- 🔴 Open: <n> | ⏳ Fixing: <n> | ✅ Fixed: <n> | 🧪 Verify: <n> | 🚫 Closed: <n> | ⛔ Won't Fix: <n> | **Total: <n>**

## 🔴 Open / 處理中

| ID | 標題 | 嚴重度 | 報修時間 | 相關工單 | 連結 |
|----|------|--------|---------|---------|------|
| BUG-007 | 登入後畫面空白 | 🔴 High | 2026-10-20 14:05 | T0123 | [BUG-007](BUG-007-login-blank.md) |

## ⏳ 修復中 (FIXING)

| ID | 標題 | 嚴重度 | 報修時間 | 相關工單 | 連結 |
|----|------|--------|---------|---------|------|
| _（無）_ | | | | | |

## ✅ 已修復

| ID | 標題 | 嚴重度 | 報修時間 | 相關工單 | 連結 |
|----|------|--------|---------|---------|------|
| _（無）_ | | | | | |

## 🧪 驗收中 (VERIFY)

| ID | 標題 | 嚴重度 | 報修時間 | 相關工單 | 連結 |
|----|------|--------|---------|---------|------|
| _（無）_ | | | | | |

## 🚫 已關閉 (CLOSED)

| ID | 標題 | 嚴重度 | 關閉時間 | 相關工單 | 連結 |
|----|------|--------|---------|---------|------|
| BUG-004 | 匯出檔名亂碼 | 🟡 Medium | 2026-10-18 09:30 | T0110 | [BUG-004](BUG-004-export-filename.md) |
| BUG-002 | 舊版設定頁按鈕錯位 | 🟢 Low | 2026-10-15 16:12 | | [BUG-002](BUG-002-legacy-settings-button.md) |

## ⛔ 不修復 (WONTFIX)

| ID | 標題 | 嚴重度 | 關閉時間 | 相關工單 | 連結 |
|----|------|--------|---------|---------|------|
| _（無）_ | | | | | |
```

**`_backlog.md` body**（依 § PLAN 單據 › `*sync` 整合 的狀態分配）：

```markdown
# Backlog

> ⚠️ 此文件由 `*sync` 自動生成，請勿手動編輯。
> 最後同步：<YYYY-MM-DD HH:MM> (UTC+8) — <這次同步的一句說明>

## 統計
- 💡 Ideas: <n> | 📋 Planned: <n> | 🔄 In Progress: <n> | ✅ Done: <n> | 🚫 Dropped: <n>

## Active

| ID | 標題 | 優先級 | 狀態 | 連結 |
|----|------|--------|------|------|
| PLAN-005 | 匯出改成背景工作 | 🟡 Medium | 📋 PLANNED | [PLAN-005](PLAN-005-background-export.md) |
| PLAN-006 | 多語系 | 🔴 High（critical） | 🔄 IN_PROGRESS | [PLAN-006](PLAN-006-i18n.md) |

## Completed

| ID | 標題 | 完成時間 | 連結 |
|----|------|---------|------|
| PLAN-003 | 首頁改版 | 2026-10-12 | [PLAN-003](PLAN-003-home-redesign.md) |

## Dropped

| ID | 標題 | 原因 | 連結 |
|----|------|------|------|
| PLAN-004 | 改用另一套圖表元件 | 授權不合 | [PLAN-004](PLAN-004-chart-lib.md) |

## 後續待辦（延後的 BUG）

| ID | 標題 | 嚴重度 | 延後時間 | 連結 |
|----|------|--------|---------|------|
| BUG-002 | 舊版設定頁按鈕錯位 | 🟢 Low | 2026-10-15 16:12 | [BUG-002](BUG-002-legacy-settings-button.md) |
```

上面兩個範本的資料列是示意；實際每個區段照熱區單據產生，沒有單據時放 `_（無）_` 列。

- **區段標題照範本，不得改字、不得新增其他 `##` 區段**。BAT 讀 `_bug-tracker.md` 時**狀態只看列所在的 `##` 區段標題**，列內的狀態欄不看；
  標題不認得的區段，裡面的 BUG 一律算 OPEN。所以 `_bug-tracker.md` 不放狀態欄，六個區段就是六個狀態。
- **每列**：`ID` 是單號（BAT 只收 `BUG-`／`PLAN-` 開頭）；`連結` 是相對連結 `[BUG-###](BUG-###-description.md)`，已歸檔的指到 `_archive/…`。
- **嚴重度／優先級格子**固定寫 `🔴 High`／`🟡 Medium`／`🟢 Low`；單據 frontmatter 是 `critical` 的寫 `🔴 High（critical）`。
  不得只寫 emoji 或只寫 `critical`（BAT 顯示 Unknown；只寫 `critical` 的格子在 BAT `>= 0.7.1-pre.9` 已算 High，但更舊的 BAT 仍是 Unknown）。單據的值怎麼換成格子，見 [memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 › 值域對照。
- **時間欄**：`_bug-tracker.md` 未結的四個區段（Open、FIXING、已修復、VERIFY）寫 `報修時間`（BUG 的 `created_at`，舊單取元資料的 `建立時間`／`發現時間`），
  CLOSED 與 WONTFIX 寫 `關閉時間`（`closed_at`，沒有就取 `updated_at`）。格式 `YYYY-MM-DD HH:MM`。BAT 只讀這兩個欄名。
- **`相關工單`**：修復或處理這張 BUG 的工單（frontmatter `links.related_workorders`，多張用 `、` 分隔）；沒有就留空。舊索引沒有這一欄不算錯，下次 `*sync` 補上。
- **`_backlog.md`**：Active 列保留 `狀態` 欄，圖示加狀態值（例 `📋 PLANNED`、`💡 IDEA`；BAT 以這欄蓋過區段）；`## Dropped` 表頭用 `ID`、`標題`，不加刪除線（加了 BAT 讀不到整區）。
- **`## 後續待辦（延後的 BUG）`**：列出熱區 `status: CLOSED` 且 `closed_reason: deferred` 的 BUG（§ BUG 單據 › 結案判準），`延後時間` 取 `closed_at`。
  **只放 BUG 列，不放 PLAN 列**：BAT 讀 `_backlog.md` 只收 `PLAN-` 開頭的列，BUG 列會被略過，不會混進待辦池；PLAN 列放在這裡會被當成 IDEA。
  這些 BUG 在 BAT 臭蟲頁照樣出現在 CLOSED 區。
- 區段沒有單據時放一列 `| _（無）_ | | | | |`（欄數照該表）；各區段與欄位標題照上方範本，不增減。
- 表格列與儲存格的共通寫法（每列 `|` 開頭與結尾、格子內不得有 `|`）見 [memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 › 各檔要求。

## 編號管理

### 編號格式

| 類型 | 格式 | 位數 | 起始值 | 範例 |
|------|------|------|--------|------|
| Work Order | `T####` | 4 位 | 0001 | T0072 |
| Bug Report | `BUG-###` | 3 位 | 001 | BUG-001 |
| Plan | `PLAN-###` | 3 位 | 001 | PLAN-001 |
| Experiment | `EXP-[TOPIC]-###` | 3 位（每 TOPIC 獨立） | 001 | EXP-AUTH-001 |

### 編號追蹤

編號追蹤寫入 `_tower-state.md`，與現有 `next_workorder_number` 同層：

```yaml
# _tower-state.md 編號追蹤區段
next_workorder_number: T0073
next_bug_number: BUG-001
next_plan_number: PLAN-001
# EXP 編號按 TOPIC 獨立追蹤
exp_counters:
  AUTH: 1
  PERF: 3
```

### 自動遞增邏輯

1. 塔台產生新單據時，讀取 `_tower-state.md` 中對應類型的計數器
2. 使用當前值作為新單據編號
3. 遞增計數器並寫回 `_tower-state.md`
4. 若 `_tower-state.md` 中無對應計數器（首次啟用），從 001 開始
5. `*sync` 時驗證計數器與實際檔案一致性，修正漂移

---

## BUG 單據

### 生命週期狀態機

```
OPEN → FIXING → FIXED → VERIFY → CLOSED
                              └→ WONTFIX
     └→ WONTFIX（任何階段可直接標記）
     └→ CLOSED（依 § 結案判準 直接結案，帶 closed_reason）
CLOSED（closed_reason: deferred）→ OPEN（要做時重開）
```

| 狀態 | 說明 | 進入條件 | 離開條件 |
|------|------|---------|---------|
| OPEN | 已回報，待處理 | 建立時；延後的 BUG 重開時 | 指派修復 → FIXING |
| FIXING | 修復中 | 從 OPEN 指派 | 修復完成 → FIXED |
| FIXED | 已修復，待驗證 | sub-session 回報修復；或依 § 結案判準 核對時確認現行程式已修好 | 驗證通過 → VERIFY；驗證失敗 → 回到 FIXING |
| VERIFY | 驗證中 | 從 FIXED 進入驗證 | 確認修復 → CLOSED |
| CLOSED | 已關閉 | 驗證通過；或依 § 結案判準 直接結案（帶 `closed_reason`） | 終態（`closed_reason: deferred` 可重開 → OPEN） |
| WONTFIX | 不修復 | 任何階段皆可標記 | 終態 |

**不新增狀態值**：上表六值與 BAT 一對一相同。「不是缺陷」「被取代」「非我方」「延後」都用 `CLOSED` 加結案原因表達（§ 結案判準）。

### 嚴重度

| 等級 | 符號 | 說明 |
|------|------|------|
| High | 🔴 | 阻塞功能或資料損失 |
| Medium | 🟡 | 功能異常但有替代方案 |
| Low | 🟢 | 外觀瑕疵或次要問題 |

### BUG 互動流程

**最少必填欄位**：標題、嚴重度、現象描述（預期 vs 實際行為）

**建立 BUG 單**：

使用者在塔台中回報 bug 時，塔台進行需求對齊：

1. 確認問題描述（重現步驟、預期/實際行為）
2. 選項式提問——釐清問題特性：
   - 嚴重度？ `[A]` 🔴 High（阻塞功能或資料損失） `[B]` 🟡 Medium（功能異常但有替代方案） `[C]` 🟢 Low（外觀瑕疵或次要問題）
   - 可重現？ `[A]` 100%（每次操作都會發生） `[B]` 偶爾（無法穩定重現） `[C]` 只出現一次
   - 有 workaround？ `[A]` 有（請簡述替代方式） `[B]` 沒有
3. 關聯現有工單（是否與進行中的任務相關）
4. 產生 BUG 單檔案，寫入 `_ct-workorders/`
5. 顯示摘要：

```
🐛 BUG 單已建立：BUG-001-login-crash
   嚴重度：🔴 High
   可重現：100%
   Workaround：無
   狀態：OPEN
   路徑：_ct-workorders/BUG-001-login-crash.md

👉 後續處理：
   [A] 立即派發修復工單（BUG 狀態 → FIXING）
   [B] 先記錄，稍後處理（BUG 狀態留 OPEN）
   [C] 標記 WONTFIX（不修復）
```

**修復流程**：

1. 塔台派發修復工單（標準 T#### 工單），工單中引用 BUG 編號
2. Sub-session 完成修復後回報
3. 塔台更新 BUG 狀態：FIXING → FIXED
4. 塔台詢問是否需要驗證工單（高嚴重度建議獨立驗證）
5. 驗證通過 → CLOSED；驗證失敗 → 回到 FIXING

### 結案判準

本節是「BUG 該落哪個狀態、要寫什麼」的**唯一權威定義**。一般的處理與結案、逐張核對未結 BUG（§ 未結 BUG 清理提示）都用它。

| 情況 | 狀態 | 要寫的 |
|---|---|---|
| 現行程式已修好 | `FIXED` | 修正 commit 或 `檔案:行` |
| 前提錯誤、設計如此 | `CLOSED` | `closed_reason: not_a_defect`＋原判（當初為什麼以為是 BUG） |
| 屬實但不修（使用者接受、交付版走不到） | `WONTFIX` | 寫進交付文件的已知限制 |
| 過時：功能退場、程式已刪、被他單取代或重複、規劃已改 | `CLOSED` | `closed_reason: superseded`／`duplicate`／`obsolete`＋被誰取代或為何過時 |
| 非我方責任 | `CLOSED` | `closed_reason: external`＋已告知對方（誰、何時） |
| 仍成立但低優先、短期不做 | `CLOSED` | `closed_reason: deferred`；`*sync` 把它列進 `_backlog.md`〈後續待辦〉（§ 索引格式）；要做時重開成 `OPEN` |
| 仍成立且要做 | `OPEN` | 標「上線前」或「後續」，並重新核定嚴重度 |

- **證據不足就維持 `OPEN`（待查）**，不得猜。
- 逐張以**現行程式碼**與後續工單、決策核對，不只看單內記載；單內有多段更正時以最後一段為準。
- **結案原因**記兩處：frontmatter 選填欄位 `closed_reason`（值：`not_a_defect`、`superseded`、`duplicate`、`obsolete`、`external`、`deferred`），
  以及本文元資料一行 `- **結案原因**：<值>：<說明>`。只有照上表直接結案的 `CLOSED` 才填，一般驗收通過的 `CLOSED` 不填；
  同時把系統時間寫進 `closed_at`。BAT 不讀 `closed_reason`，不影響面板。
- **延後的 BUG 留在熱區**：`closed_reason: deferred` 的 BUG 不列為歸檔候選（[archive-system.md](archive-system.md) § 豁免規則），
  `_backlog.md`〈後續待辦〉才會完整。重開時狀態改回 `OPEN`、刪掉 `closed_reason` 與 `closed_at`，本文補一行重開原因。

### 未結 BUG 清理提示

本節是提示條件與內容的**唯一權威定義**；門檻的有效值與預設在 [tower-config.md](tower-config.md) § 可用選項（`bug_review_open_threshold`、`bug_review_stale_days`）。

- **條件**（`*sync` 計算，任一成立就提示）：熱區未結 BUG（`OPEN`、`FIXING`、`FIXED`、`VERIFY`）多於 `bug_review_open_threshold` 張；
  或有未結 BUG 超過 `bug_review_stale_days` 天沒更新（`updated_at`，沒有就取 `created_at`；舊單取元資料的時間欄）。門檻值 `0` = 該條件停用。
- **提示**（`*sync` 摘要末尾一行，不阻擋）：
  `🧹 未結 BUG <n> 張（門檻 <m>）／<k> 張超過 <d> 天沒更新，建議照 bug-plan-system.md § 結案判準 逐張核對（可分批平行派唯讀工單）`
- 核對工單只讀程式碼與紀錄，回報每張的建議狀態與證據；改不改狀態由塔台依回報決定，改完同一批重建索引（下方 `*sync` 整合）。
- `*insights` 報告也帶這一行（條件相同）。

**`*sync` 整合**：

BUG 單據參與 `*sync` 掃描，自動重建 `_bug-tracker.md` 索引。

**改狀態要同一批重建索引**：塔台改了任何 BUG 或 PLAN 的狀態（含結案、延後、重開、歸檔、取回），同一批次就重建 `_bug-tracker.md`／`_backlog.md`
（跑 `*sync`，或只重建這兩檔），不留到下次。BAT 看板讀的是索引，不重建就顯示舊狀態。大小檢查見 [memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 › 大小預算。

**元資料解析規則**（`*sync` 讀取 BUG 單時提取；有 frontmatter 時以 frontmatter 為準，§ PLAN-034 Sprint 2 transition）：

| 欄位 | 解析方式 | 用途 |
|------|---------|------|
| 編號 | 檔名前綴 `BUG-###` | 索引 ID |
| 標題 | frontmatter `title`；元資料區 `**標題**：` 後的值 | 索引標題欄 |
| 狀態 | frontmatter `status`；元資料區 `**狀態**：` 後的值（OPEN/FIXING/FIXED/VERIFY/CLOSED/WONTFIX） | 分配到對應 section |
| 嚴重度 | frontmatter `severity`；元資料區 `**嚴重度**：` 後的值 | 索引嚴重度欄，換成 `🔴 High` 等（§ 索引格式） |
| 報修時間 | frontmatter `created_at`；元資料區 `**建立時間**：`／`**發現時間**：` 後的值 | 未結區段的 `報修時間` 欄 |
| 關閉時間 | frontmatter `closed_at`（沒有就取 `updated_at`）；元資料區 `**關閉時間**：` 後的值 | CLOSED／WONTFIX 區段的 `關閉時間` 欄 |
| 結案原因 | frontmatter `closed_reason`；元資料區 `**結案原因**：` 後的值 | `deferred` → 列進 `_backlog.md`〈後續待辦〉 |
| 相關工單 | frontmatter `links.related_workorders`；元資料區 `**修復工單**：` 後的值 | 索引相關工單欄 |
| 連結 | `_ct-workorders/BUG-###-description.md` 相對路徑 | 索引連結欄 |

> 依狀態分配到 `_bug-tracker.md` 對應 section，完整格式定義見本檔 § 索引格式。

---

## PLAN 單據

### 生命週期狀態機

```
IDEA → PLANNED → IN_PROGRESS → DONE
                            └→ DROPPED
```

| 狀態 | 說明 | 進入條件 | 離開條件 |
|------|------|---------|---------|
| IDEA | 初步想法 | 建立時 | 評估可行 → PLANNED |
| PLANNED | 已規劃，待實施 | 從 IDEA 評估通過 | 開始實施 → IN_PROGRESS |
| IN_PROGRESS | 實施中 | 關聯工單開始執行 | 完成 → DONE；放棄 → DROPPED |
| DONE | 已完成 | 所有關聯工單完成 | 終態 |
| DROPPED | 已放棄 | 評估後決定不做 | 終態 |

### 優先級

| 等級 | 符號 | 說明 |
|------|------|------|
| High | 🔴 | 近期必須處理 |
| Medium | 🟡 | 中期規劃 |
| Low | 🟢 | 長期想法或低優先 |

### PLAN 互動流程

**最少必填欄位**：標題、動機/背景（一句話）

**建立 PLAN 單**：

使用者在塔台中提出想法/規劃時：

1. 確認想法描述和預期目標
2. 選項式提問——釐清規劃特性：
   - 優先級？ `[A]` 🔴 High（近期必須處理） `[B]` 🟡 Medium（中期規劃） `[C]` 🟢 Low（長期想法或低優先）
   - 類型？ `[A]` 功能想法 `[B]` 技術改善 `[C]` 架構調整 `[D]` 其他
3. 產生 PLAN 單檔案
4. 顯示摘要：

```
💡 PLAN 單已建立：PLAN-001-refactor-auth-module
   優先級：🟡 Medium
   類型：技術改善
   狀態：IDEA
   路徑：_ct-workorders/PLAN-001-refactor-auth-module.md

👉 下一步：
   [A] 立即評估，轉為 PLANNED
   [B] 先記錄，稍後評估（狀態留 IDEA）
```

**從 PLAN 轉為實作**：

1. 使用者決定實施某個 PLAN
2. 塔台將 PLAN 狀態更新為 IN_PROGRESS
3. 從 PLAN 描述拆解出一或多張標準工單（T####）
4. 工單中引用 PLAN 編號
5. 所有關聯工單完成後，PLAN 狀態更新為 DONE

**`*sync` 整合**：

PLAN 單據參與 `*sync` 掃描，自動重建 `_backlog.md` 索引；改了 PLAN 狀態同樣同一批重建（上方 § BUG 單據 › `*sync` 整合）。

**元資料解析規則**（`*sync` 讀取 PLAN 單時提取）：

| 欄位 | 解析方式 | 用途 |
|------|---------|------|
| 編號 | 檔名前綴 `PLAN-###` | 索引 ID |
| 標題 | 元資料區 `**標題**：` 後的值 | 索引標題欄 |
| 狀態 | 元資料區 `**狀態**：` 後的值（IDEA/PLANNED/IN_PROGRESS/DONE/DROPPED） | 分配到對應 section |
| 優先級 | frontmatter `priority`；元資料區 `**優先級**：` 後的值 | 索引優先級欄（Active 區），換成 `🔴 High` 等（§ 索引格式） |
| 建立時間 | 元資料區 `**建立時間**：` 後的值 | 排序依據 |
| 完成時間 | 元資料區 `**完成時間**：` 後的值 | Completed 區時間欄 |
| 連結 | `_ct-workorders/PLAN-###-description.md` 相對路徑 | 索引連結欄 |

> IDEA/PLANNED/IN_PROGRESS → Active 區，DONE → Completed 區，DROPPED → Dropped 區。
> 完整格式定義見本檔 § 索引格式。

---

## EXP 實驗單據

### 前綴規範

- 格式：`EXP-[TOPIC]-###-description.md`
- **TOPIC**：2-10 字元，僅限大寫英文字母和數字
- 每個 TOPIC 獨立計數，從 001 起
- 範例：`EXP-AUTH-001-jwt-vs-session.md`、`EXP-PERF-002-cache-strategy.md`

### TOPIC 命名規則

| 規則 | 說明 | 範例 |
|------|------|------|
| 長度 | 2-10 字元 | `AUTH`、`PERF`、`UI2` |
| 字元集 | 大寫英文 A-Z + 數字 0-9 | `DB`、`API3` |
| 禁止 | 小寫、空格、特殊符號 | ~~`auth`~~、~~`my-exp`~~ |
| 語意 | 代表實驗領域或主題 | `CACHE`、`MIGRATE` |

### 生命週期狀態機

```
EXPLORING → CONCLUDED
         └→ ABANDONED
```

| 狀態 | 說明 | 進入條件 | 離開條件 |
|------|------|---------|---------|
| EXPLORING | 實驗進行中 | 建立時 | 得出結論 → CONCLUDED；放棄 → ABANDONED |
| CONCLUDED | 已得出結論 | 實驗完成，記錄結論 | 終態 |
| ABANDONED | 已放棄 | 實驗無法繼續或無意義 | 終態 |

### Worktree 工作流

EXP 單據搭配 Git worktree 使用，實驗失敗可零污染丟棄：

**Step 1：建立 EXP 單據後，塔台提問執行方式**：
```
👉 執行方式：
   [A] 在 worktree 中實驗（推薦，失敗可零污染丟棄）
   [B] 在當前分支實驗（適合小規模探索）
   [C] 先記錄，稍後實驗
```

**Step 2：選擇 [A] 時，塔台指導建立 worktree**：
```bash
# 塔台提供指令（使用者在終端機執行）
git worktree add ../<repo>-<topic> -b exp/<topic>
# 範例：git worktree add ../my-project-auth -b exp/auth
```

**Step 3：使用者在 worktree 目錄開啟新 sub-session 執行實驗**

EXP 工單會自動出現在 worktree 的 `_ct-workorders/` 中（共用同一 git 歷史）。

**Step 4：實驗結束，依結果走不同路徑**：

- **成功路徑**（CONCLUDED）：
  1. 在 worktree 提交所有變更
  2. 從 `exp/<topic>` 建立 PR 回主分支
  3. PR 合併後清理：
     ```bash
     git worktree remove ../<repo>-<topic>
     git branch -d exp/<topic>
     ```
  4. 塔台更新 EXP 狀態 → CONCLUDED，填寫結論

- **失敗/放棄路徑**（ABANDONED）：
  1. 丟棄 worktree，主線零污染：
     ```bash
     git worktree remove ../<repo>-<topic>
     git branch -D exp/<topic>
     ```
  2. 塔台更新 EXP 狀態 → ABANDONED，記錄放棄原因

**`*sync` 行為**：EXP 工單列在獨立「🧪 實驗分支」區塊，不計入 sprint 進度。

### EXP 互動流程

**最少必填欄位**：TOPIC 名稱、實驗假設（一句話）

**建立 EXP 單**：

1. 使用者描述實驗目的
2. 確認 TOPIC 名稱（塔台建議 2-10 字元大寫英文+數字，使用者確認）
3. 確認實驗假設（一句話描述要驗證的事情）
4. 產生 EXP 單檔案
5. 顯示摘要並引導至 Worktree 工作流（見上方）：

```
🧪 EXP 單已建立：EXP-AUTH-001-jwt-vs-session
   TOPIC：AUTH
   假設：JWT 比 session 更適合分散式環境
   狀態：EXPLORING
   路徑：_ct-workorders/EXP-AUTH-001-jwt-vs-session.md

👉 執行方式：
   [A] 在 worktree 中實驗（推薦，失敗可零污染丟棄）
   [B] 在當前分支實驗（適合小規模探索）
   [C] 先記錄，稍後實驗
```

**`*sync` 整合**：

EXP 單據參與 `*sync` 掃描，在同步摘要中列於獨立的「🧪 實驗分支」區塊（不生成獨立索引文件）。

**元資料解析規則**（`*sync` 讀取 EXP 單時提取）：

| 欄位 | 解析方式 | 用途 |
|------|---------|------|
| 編號 | 檔名前綴 `EXP-[TOPIC]-###` | 統計顯示 |
| 標題 | 元資料區 `**標題**：` 後的值 | 統計顯示 |
| 狀態 | 元資料區 `**狀態**：` 後的值（EXPLORING/CONCLUDED/ABANDONED） | 統計分類 |
| TOPIC | 元資料區 `**TOPIC**：` 後的值 | 計數器驗證 |

> EXP 不計入 Sprint 進度，僅在 `*sync` 摘要中顯示統計。

---

## 跨類型關聯

不同類型單據之間可透過文字引用建立關聯：

| 關聯場景 | 說明 |
|---------|------|
| BUG → T#### | BUG 單的修復工單 |
| PLAN → T#### | PLAN 拆解出的實作工單 |
| EXP → T#### | 實驗成功後的正式實作工單 |
| T#### → BUG | 工單執行中發現的 bug |
| EXP → PLAN | 實驗結論轉為正式規劃 |

關聯方式：在單據的相關欄位中引用編號（如「修復工單：T0073」、「來源 BUG：BUG-001」）。
不使用自動化連結系統，保持簡單的文字引用。

---

## 未啟用時的行為

當對應 config 選項為 `false` 時：

| 情境 | 塔台行為 |
|------|---------|
| 使用者回報 bug | 正常用標準工單（T####）處理，不建立 BUG 單 |
| 使用者提出想法 | 正常用標準工單（T####）處理，不建立 PLAN 單 |
| 使用者想實驗 | 正常用標準工單（T####）處理，不建立 EXP 單 |
| `*sync` 掃描 | 忽略 `BUG-*.md`、`PLAN-*.md`、`EXP-*.md` 檔案 |

> 即使功能未啟用，若 `_ct-workorders/` 中已存在 BUG/PLAN/EXP 檔案（如從其他專案複製），
> `*sync` 會在摘要中提示「偵測到 N 張 BUG/PLAN/EXP 單據但功能未啟用」，建議使用者啟用。

---

## EXP 模板

```markdown
# EXP-[TOPIC]-###-description

## 元資料
- **編號**：EXP-[TOPIC]-###
- **標題**：<實驗主題簡述>
- **狀態**：EXPLORING
- **TOPIC**：<TOPIC 名稱>
- **假設**：<實驗要驗證的假設>
- **建立時間**：<ISO datetime>
- **結論時間**：（CONCLUDED 或 ABANDONED 時填入）

## 實驗設計
<實驗方法、步驟、預期觀察指標>

## 實驗紀錄
<每次實驗的觀察和數據>

## 結論
（CONCLUDED 時填寫：驗證結果、學到什麼、建議下一步）
（ABANDONED 時填寫：放棄原因）
```

---

## PLAN-034 Sprint 2 transition — YAML frontmatter SoT (v5.0.0+)

> v5.0.0 起，BUG / PLAN / EXP 新單據模板輸出 v1 YAML frontmatter，並保留原 body metadata table 作為人類鏡像。
> frontmatter = SoT；body table = 人類鏡像；drift 時 `*sync` warn 不覆寫 body table。

### YAML frontmatter 共通規則

新建 BUG / PLAN / EXP 單據時，檔案第一個 bytes 必須是 v1 YAML frontmatter。
時間欄位使用 quoted ISO 8601 with offset，例如 `"2026-04-28T19:16:49+08:00"`。
list 欄位使用 YAML block list。`_archive/**` 不參與 hot-zone sync migration。

### BUG frontmatter template

```yaml
---
schema_version: 1
schema_kind: bug
id: BUG-###
title: <bug 標題>
status: OPEN
severity: medium
reproducibility: always
created_at: "<ISO 8601 datetime with offset>"
# closed_at: "<ISO 8601 datetime with offset>"   # CLOSED／WONTFIX 時填
# closed_reason: deferred                          # 只在依 § 結案判準 直接結案時填，值見該節
links:
  related_workorders:
    - T####
affects_files:
  - <repo-relative path>
---
```

狀態 enum：`OPEN / FIXING / FIXED / VERIFY / CLOSED / WONTFIX`。
`severity` 建議用 `low / medium / high / critical`；body table 可繼續顯示 emoji。寫進索引時一律換成 `🔴 High` 等（§ 索引格式）。

### PLAN frontmatter template

```yaml
---
schema_version: 1
schema_kind: plan
id: PLAN-###
title: <plan 標題>
status: IDEA
priority: medium
created_at: "<ISO 8601 datetime with offset>"
plan_type:
  - technical-improvement
trigger_bugs:
  - BUG-###
scope:
  - <scope item>
estimated_workorders: 3
---
```

狀態 enum：`IDEA / PLANNED / IN_PROGRESS / DONE / DROPPED`。
`priority` 建議用 `low / medium / high / critical`；body table 可繼續顯示 emoji。寫進索引時一律換成 `🔴 High` 等（§ 索引格式）。

### EXP frontmatter template

```yaml
---
schema_version: 1
schema_kind: experiment
id: EXP-[TOPIC]-###
title: <實驗主題簡述>
status: EXPLORING
topic: <TOPIC 名稱>
created_at: "<ISO 8601 datetime with offset>"
driving_decision: <D### 或工單 ID>
related_plan: PLAN-###
success_criteria:
  - <criteria 1>
  - <criteria 2>
---
```

EXP frontmatter status enum 固定為 `EXPLORING / CONCLUDED / ABANDONED`。
此三值是 PLAN-034 Sprint 2 對齊現行 CT skill 與 EXP-HEADLESS-001 熱區慣例的唯一 EXP enum。

### 元資料解析規則（frontmatter-first）

```text
解析順序：
1. 若檔案有 YAML frontmatter：validate schema_version/schema_kind/id/status，使用 frontmatter 作為 SoT。
2. 若缺 frontmatter：fallback 既有 markdown body metadata table，並在 sync summary 輸出 `missing_frontmatter` warning。
3. 若 frontmatter 與 body table drift：使用 frontmatter，輸出 `metadata_drift` warning，不覆寫 body。
4. Unknown status：標 invalid/unknown，不可 fallback 到 PENDING 或其他預設狀態。
```

> PLAN-034 transition：`*sync` 先讀 frontmatter；無 frontmatter 才 fallback legacy body metadata table 並警告 `missing_frontmatter`。
> Generated `_backlog.md` / `_bug-tracker.md` 可整檔重寫，但 human BUG / PLAN body table 不因 drift 自動覆寫。
> Unknown status 必須標為 invalid/unknown，不可 fallback 成 OPEN 或 PENDING。

### 驗收

- BUG / PLAN / EXP templates 均有 v1 frontmatter block。
- EXP enum 全文使用 `EXPLORING / CONCLUDED / ABANDONED`。
- 三類都保留 legacy body metadata table fallback。
- 三類都明示 frontmatter SoT、body mirror、drift warn 不覆寫。
