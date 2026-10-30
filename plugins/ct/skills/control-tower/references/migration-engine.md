# v3→v4 遷移引擎

> Step 0 環境偵測擴展：偵測 v3.6 專案的 v4 功能啟用狀態，
> 顯示升級面板，讓使用者逐項選擇啟用。

## 設計原則

- **建議非強制**：全部可 skip，不影響任何現有功能
- **漸進式升級**：可分次執行，每次啟動只處理想啟用的功能
- **已啟用隱藏**：面板僅顯示尚未啟用的功能，全部啟用後面板消失
- **Git 備份**：每項遷移操作後 `git add`，建立 staging 備份點
- **零破壞**：所有遷移操作僅新增，不修改或刪除現有檔案內容

---

## 偵測項目

| # | 偵測項 | 偵測方法 | v3.6 特徵 | v4.0 目標 | 遷移動作 |
|---|--------|---------|-----------|-----------|----------|
| 1 | Archive 目錄 | `test -d _ct-workorders/_archive/` | 不存在 | `_archive/{workorders,bugs,plans}/` | 建立三層子目錄 |
| 2 | 決策日誌 | `test -f _ct-workorders/_decision-log.md` | 不存在 | 獨立日誌 | 建立空模板（含索引表頭） |
| 3 | Playbook 目錄 | `test -d _ct-workorders/_playbooks/` | 不存在 | Playbook 引擎 | 建立空目錄 |
| 4 | Config 新選項 | 比對 config 已有選項 vs v4 可用選項 | 缺少 v4 選項 | 12+ 選項 | 新增缺失選項（帶預設值），保留現有值 |
| 5 | 舊索引文件 | `test -f _ct-workorders/_workorder-index.md` | 可能存在 | 廢除（*sync 自動重建） | `git mv` 到 `_archive/workorders/` |
| 6 | BUG 追蹤 | config `enable_bug_tracking` 為 `false` 或缺失 | 未啟用 | `true` | 設定 config + 確認 `_archive/` 可用 |
| 7 | PLAN 追蹤 | config `enable_plan_tracking` 為 `false` 或缺失 | 未啟用 | `true` | 設定 config |
| 8 | EXP 實驗追蹤 | config `enable_experiments` 為 `false` 或缺失 | 未啟用 | `true` | 設定 config |

---

## 觸發條件

遷移偵測在 Step 0 **主面板顯示後**執行：

1. 依序檢查上表 8 個偵測項
2. 收集所有「未啟用」的項目
3. 若有至少 1 項未啟用 → 顯示遷移面板
4. 若全部已啟用 → 靜默跳過（不顯示任何面板）

**與主面板的關係**：
- 主面板（塔台狀態面板，定義見 [memory-protocol.md](memory-protocol.md) § 塔台狀態面板）顯示**當前狀態**（只讀資訊）
- 遷移面板顯示**可執行的升級動作**（互動式選擇）
- 兩個面板獨立，遷移面板不修改主面板內容

---

## 面板格式

動態生成，僅列出「可升級」項目（已啟用的不顯示）：

```
═══ 🆕 v4.0 可升級功能（N 項）═══
  [1] 建立 _archive/ 目錄結構    → 啟用 *archive 命令
  [2] 建立 _decision-log.md      → 獨立決策追溯
  [3] 建立 _playbooks/ 目錄      → Playbook 引擎（Phase 5）
  [4] 補齊 config 新選項          → 更細緻的行為控制
  [5] 歸檔舊 _workorder-index.md → 改用 *sync 自動重建
  [6] 啟用 BUG 追蹤              → BUG-### 單據 + *bug 命令
  [7] 啟用 PLAN 追蹤             → PLAN-### 單據 + *plan 命令
  [8] 啟用 EXP 實驗追蹤          → EXP 單據 + worktree 隔離
═══════════════════════════════════
  輸入編號啟用（可多選，如 1,2,4），「all」全部，「skip」跳過。
```

**編號為動態遞增**：若項目 1 和 3 已啟用，面板只顯示 `[1]`~`[6]` 對應剩餘 6 項。
面板標題中的 `N` 反映實際可升級項目數量。

---

## 使用者互動

### 輸入格式

| 輸入 | 行為 |
|------|------|
| `skip` | 跳過全部，繼續正常啟動流程 |
| `all` | 啟用全部項目 |
| `1` | 啟用編號 1 的項目 |
| `1,3,5` | 啟用編號 1、3、5 的項目 |
| `1-4` | 啟用編號 1 到 4 的項目 |
| 其他 | 提示格式錯誤，重新顯示面板 |

### 互動流程

```
遷移面板顯示
  → 使用者輸入選擇
  → 驗證輸入格式
  → 逐項執行遷移（按偵測項原始順序）
  → 顯示遷移結果摘要
  → 繼續 Step 0 後續流程（Beginner 偵測等）
```

---

## 逐項遷移動作

### [1] 建立 Archive 目錄

```
操作：
  mkdir -p _ct-workorders/_archive/workorders
  mkdir -p _ct-workorders/_archive/bugs
  mkdir -p _ct-workorders/_archive/plans
  git add _ct-workorders/_archive/

結果：✅ _archive/ 目錄結構已建立（3 個子目錄）
```

### [2] 建立決策日誌

```
操作：
  建立 _ct-workorders/_decision-log.md（空模板）
  git add _ct-workorders/_decision-log.md

模板內容：
  # 決策日誌

  | 編號 | 日期 | 決策摘要 | 工單 | 標籤 |
  |------|------|---------|------|------|

結果：✅ _decision-log.md 已建立（空模板）
```

### [3] 建立 Playbook 目錄

```
操作：
  mkdir -p _ct-workorders/_playbooks
  git add _ct-workorders/_playbooks/

結果：✅ _playbooks/ 目錄已建立
```

> 注意：Git 不追蹤空目錄。建立後在目錄中放置 `.gitkeep` 或等待首個 playbook 寫入。

### [4] 補齊 Config 新選項

```
操作：
  1. 讀取現有 _ct-workorders/_tower-config.yaml
  2. 比對 v4 完整選項列表，找出缺失項：
     - enable_bug_tracking: false
     - enable_plan_tracking: false
     - enable_experiments: false
     - archive_days: 7
     - auto_archive_prompt: off
  3. 僅新增缺失的選項（帶預設值），保留所有現有值不變
  4. 寫回 _tower-config.yaml
  5. git add _ct-workorders/_tower-config.yaml

結果：✅ 已新增 N 個 config 選項（現有設定不變）
      列出新增的選項名稱和預設值
```

### [5] 歸檔舊索引文件

```
前提：_ct-workorders/_workorder-index.md 存在
操作：
  1. 確保 _archive/workorders/ 存在（若不存在先建立）
  2. git mv _ct-workorders/_workorder-index.md \
           _ct-workorders/_archive/workorders/_workorder-index.md

結果：✅ 舊索引已歸檔到 _archive/workorders/
      💡 使用 *sync 可自動重建索引
```

### [6] 啟用 BUG 追蹤

```
操作：
  1. 設定 enable_bug_tracking: true
  2. 寫入 _tower-config.yaml（project scope）
  3. git add _ct-workorders/_tower-config.yaml

結果：✅ BUG 追蹤已啟用
      💡 使用 *bug 建立第一張 BUG 單
```

### [7] 啟用 PLAN 追蹤

```
操作：
  1. 設定 enable_plan_tracking: true
  2. 寫入 _tower-config.yaml（project scope）
  3. git add _ct-workorders/_tower-config.yaml

結果：✅ PLAN 追蹤已啟用
      💡 使用 *plan 建立第一張 PLAN 單
```

### [8] 啟用 EXP 實驗追蹤

```
操作：
  1. 設定 enable_experiments: true
  2. 寫入 _tower-config.yaml（project scope）
  3. git add _ct-workorders/_tower-config.yaml

結果：✅ EXP 實驗追蹤已啟用
      💡 使用 *exp 建立第一個實驗
```

---

## Git 備份機制

每項遷移操作遵循：

```
1. 執行遷移操作（建立目錄/檔案、修改 config）
2. git add 相關檔案（建立 staging 備份點）
3. 所有選中項目執行完畢後顯示結果摘要
```

> **不自動 commit**。遷移引擎僅 `git add` 建立 staging 備份點，
> commit 時機由使用者或塔台在後續流程中決定。
> 使用者可透過 `git diff --cached` 檢視所有遷移變更。

### 無 Git 環境

若偵測到不在 Git 管理下：
- 跳過所有 `git add` / `git mv` 操作
- 使用普通 `mv` 替代 `git mv`（項目 5 舊索引歸檔）
- 面板下方顯示：「⚠️ 非 Git 環境，遷移操作不含版本控制備份。」

---

## 遷移結果摘要

所有選中項目執行完畢後，顯示結果摘要：

```
═══ 遷移結果 ═══
✅ 已啟用 N 項：
  - _archive/ 目錄結構（3 子目錄）
  - _decision-log.md（空模板）
  - BUG 追蹤（config 已更新）

💡 建議執行 *sync 重建索引
🔒 變更已 git add，確認後可 commit
═══════════════
```

若有項目執行失敗，在摘要中列出：

```
⚠️ 部分項目未成功（1 項）：
  - _playbooks/ 建立失敗：權限不足
```

---

## 向下相容保證

1. **skip 全部**：不修改任何檔案，不影響任何現有功能
2. **部分啟用**：僅修改選中項目相關的檔案，其餘不動
3. **Config 保留**：新增選項帶預設值，現有選項值絕不覆蓋
4. **重複執行安全**：已存在的目錄/檔案不會被覆蓋或重建
5. **無 v3.6 功能退化**：所有 v3.6 功能在 v4.0 核心下正常運作
6. **中斷安全**：遷移過程中斷，已完成的項目保留，下次啟動可繼續剩餘項目

---

## 錯誤處理

| 情境 | 行為 |
|------|------|
| 無 Git 環境 | 跳過 `git add`/`git mv`，使用普通檔案操作，顯示提示 |
| `_tower-config.yaml` 不存在 | 建立新檔案（含選中項目的設定值 + 預設值） |
| `git add` 失敗 | 警告但繼續遷移（已建立的檔案/目錄仍有效） |
| 使用者輸入無效編號 | 提示有效範圍（1~N），重新等待輸入 |
| 遷移過程中斷 | 已完成項目保留，下次啟動面板僅顯示剩餘項目 |
| 目標目錄/檔案已存在 | 跳過該項（視為已啟用），不覆蓋 |
| 項目 5 但 `_archive/` 不存在 | 先自動建立 `_archive/workorders/`，再執行歸檔 |

---

## 與其他系統的關係

| 系統 | 關係 |
|------|------|
| 塔台狀態面板（[memory-protocol.md](memory-protocol.md) § 塔台狀態面板） | 只有時序關係：遷移偵測在面板顯示後執行，但**不消費面板資料**；偵測依據是本檔 § 偵測項目 的 8 項檢查（檔案存在性與 config 值） |
| `*sync` | 遷移完成後建議執行 `*sync` 重建索引 |
| `*config` | 項目 4/6/7/8 修改 config，等同 `*config <option> <value> --save project` |
| `*archive` | 項目 1 建立 `_archive/` 目錄，為 `*archive` 命令提供前提 |
| `_decision-log.md` | 項目 2 建立空模板，為決策日誌系統提供前提 |
| Playbook 引擎 | 項目 3 建立 `_playbooks/` 目錄，Phase 5 Playbook 引擎的前提 |
