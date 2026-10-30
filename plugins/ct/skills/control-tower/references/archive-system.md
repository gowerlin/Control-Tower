# 歸檔子系統（Archive System）

> Control Tower v4 擴展：熱區（active）/ 冷區（`_archive/`）分離機制。
> 完成的單據定期歸檔到冷區，減少 `*sync` 掃描範圍，降低 token 消耗。

## 設計背景

- BAT 實驗：84 張文件歸檔後，目錄從 ~150 降到 ~80
- 專案 B 實驗：200 張封存 vs 107 張 active
- 學員需求 FR-01：避免 `*sync` 重複掃描封存檔浪費 token

**核心原則**：`*sync` 專注熱區（零 token 掃描冷區），冷區按需查詢。

---

## 歸檔目錄結構

```
_ct-workorders/
├── _archive/
│   ├── workorders/    # T####-*.md（已完成工單）
│   ├── bugs/          # BUG-###-*.md（已關閉 BUG）
│   ├── plans/         # PLAN-###-*.md（已完成/放棄 PLAN）
│   └── decisions/     # _decision-log-D###-D###.md（決策日誌收斂搬出的詳細紀錄，見 decision-log-system.md § 收斂；不經 *archive）
├── T0080-active.md    # 熱區（active）
├── BUG-005-active.md
├── PLAN-003-active.md
└── ...
```

> EXP 單據歸檔到 `_archive/workorders/`（與工單共用），因 EXP 無獨立子目錄需求。

**目錄初始化**：首次執行 `*archive` 時，若 `_archive/` 不存在，自動建立含三個子目錄。

---

## 歸檔資格判定（決策樹）

```
單據是否為最終態？
├─ 否 → 不歸檔
└─ 是 → 超過 archive_days 天？
         ├─ 否 → 不歸檔
         └─ 是 → 被 active 單據引用？
                  ├─ 是 → 豁免（不歸檔）
                  └─ 否 → ✅ 歸檔候選
```

### 最終態定義

各類單據的最終態與日期欄位來源，以下方 § 最終態與日期欄位來源（v5.0.0 frontmatter-first 版）為唯一權威定義，
本節不複述。

### 天數計算

以單據完成時間（完成時間 / 關閉時間 / 結論時間）為基準，計算至今日的天數差。
若完成時間欄位為空，以建立時間為降級基準。

### 豁免規則

以下情況即使滿足歸檔條件，仍**不會被列為候選**：

1. **活躍引用豁免**：被 active 單據（非最終態）的「相關單據」或內文引用
   - 檢查方式：Grep 熱區所有非最終態單據，搜尋該編號
   - 範例：T0080 (IN_PROGRESS) 內文提到「參考 T0045」→ T0045 豁免
2. **塔台標記保留**：`_tower-state.md` 的 `pinned_items` 列表中的單據
3. **起手式引用**：`_tower-state.md` 的待處理事項或進度快照中直接提及的單據
4. **CP 工單歸檔豁免（F-23）**：跨專案 COORDINATED/DELEGATE 工單，本地完成但對方尚未完成
   - COORDINATED：`affected-projects` 中有尚未完成的 DELEGATE → 豁免
   - DELEGATE：對應 COORDINATED 工單尚未 DONE → 豁免
   - 檢查方式：讀取工單 `coordination` 元資料，確認對方工單狀態
   - 雙方皆為最終態 → 正常歸檔流程
5. **延後的 BUG**：`closed_reason: deferred` 的 BUG 留在熱區，讓 `_backlog.md`〈後續待辦〉完整（[bug-plan-system.md](bug-plan-system.md) § BUG 單據 › 結案判準）

> 強制歸檔（`*archive T0001`）跳過天數和引用檢查，但會顯示警告。

### 參考文件排除（F-24）

以下文件類型**完全不在歸檔範圍內**，`*archive` 掃描時直接跳過：

| 排除對象 | 原因 |
|---------|------|
| `_spec-*.md` | 技術規格，長期參考 |
| `_report-*.md` | 研究報告，長期參考 |
| `_spike-*.md` | 技術 spike，長期參考 |
| `_question-*.md` | 技術問題，長期參考 |
| `_roadmap-*.md` | 路線圖，長期參考 |
| `reports/` 子目錄 | 大型研究報告，長期參考 |

這些文件為非工單類型的參考文件，不適用歸檔生命週期（排除清單以本節上表為準）。

---

## `*archive` 命令

### 語法

| 語法 | 行為 |
|------|------|
| `*archive` | 掃描熱區 → 列出候選 → 確認 → 批次 `git mv` |
| `*archive --dry-run` | 只列出候選，不執行 |
| `*archive T0001` | 強制歸檔指定單據（跳過天數和引用檢查） |
| `*archive --search <keyword>` | 從冷區搜尋已歸檔單據（Grep `_archive/`） |
| `*archive --restore T0001` | 從冷區取回到熱區（`git mv` 反向） |

### 執行流程（無參數 / --dry-run）

```
1. 掃描 _ct-workorders/*.md（排除 _archive/ 和 _ 開頭系統文件）
2. 篩選最終態 + 超過 archive_days 天的單據
3. 檢查引用豁免（Grep 活躍單據是否引用候選編號）
4. 顯示候選列表：
   📦 歸檔候選（共 N 張）：
   - T0045-user-auth.md (DONE, 完成於 2026-04-01, 13 天前)
   - BUG-003-login-crash.md (CLOSED, 關閉於 2026-04-02, 12 天前)
   - PLAN-002-refactor.md (DROPPED, 放棄於 2026-03-28, 17 天前)

   豁免（N 張）：
   - T0048-xxx.md — 被 T0080 引用

   --dry-run 模式到此結束。
   非 dry-run 繼續：
5. 確認歸檔？[Y/n]
6. 確認後依類型 git mv 到對應子目錄：
   - T####-*.md → _archive/workorders/
   - BUG-###-*.md → _archive/bugs/
   - PLAN-###-*.md → _archive/plans/
   - EXP-*-*.md → _archive/workorders/
7. 自動觸發 *sync 重建索引
8. 顯示歸檔摘要
```

### 歸檔摘要格式

```
✅ 歸檔完成
───────────────────
📦 已歸檔 N 張：
  → workorders/: T0045, T0046
  → bugs/: BUG-003
  → plans/: PLAN-002

🔄 *sync 已自動執行，索引已更新。
💡 如需取回，使用 *archive --restore <編號>
```

### 強制歸檔（`*archive T0001`）

1. 定位指定單據（Glob `_ct-workorders/T0001-*.md`）
2. 顯示單據當前狀態
3. 若非最終態 → 警告「⚠️ T0001 狀態為 IN_PROGRESS，強制歸檔可能遺失進行中的工作。確認？[y/N]」
4. 若為最終態但被引用 → 警告「⚠️ T0001 被 T0080 引用，歸檔後引用將指向冷區。確認？[Y/n]」
5. 確認後 `git mv` 到對應子目錄
6. 自動觸發 `*sync`

### 搜尋冷區（`*archive --search <keyword>`）

1. Grep `_ct-workorders/_archive/` 目錄，搜尋 keyword
2. 搜尋範圍：檔名 + 文件內容
3. 顯示匹配結果：

```
🔍 冷區搜尋「auth」（共 N 筆）：
  📁 workorders/T0045-user-auth.md (DONE)
  📁 bugs/BUG-003-login-auth-crash.md (CLOSED)

💡 使用 *archive --restore T0045 取回到熱區
```

### 取回到熱區（`*archive --restore T0001`）

1. 搜尋 `_archive/` 下所有子目錄，找到匹配的單據
2. 顯示單據摘要（狀態、歸檔時間）
3. `git mv` 回 `_ct-workorders/`（熱區根目錄）
4. 自動觸發 `*sync` 重建索引
5. 顯示取回摘要：

```
↩️ 已取回 T0045-user-auth.md 到熱區
   原位置：_archive/workorders/
   目前狀態：DONE

🔄 *sync 已自動執行，索引已更新。
```

---

## Config 選項

`archive_days`、`auto_archive_prompt` 的有效值與預設值以 [tower-config.md](tower-config.md) § 可用選項（權威定義）為準，本節不複述；以下只說明它們在歸檔流程中的用法。

### archive_days

控制最終態單據需等待多少天才會成為歸檔候選。

- `0`：最終態立即成為候選（適合快速迭代專案）
- `7`：完成 7 天後成為候選（兼顧可追溯性）
- `30`：完成 30 天後（適合需要長期參考的專案）
- `365`：近乎不歸檔（僅手動 `*archive T####`）

### auto_archive_prompt

控制 `*sync` 執行後是否自動提示歸檔候選。

- `off`：`*sync` 不提示歸檔（減少雜訊）
- `on`：`*sync` 結束時顯示歸檔候選數量和提示

```
# auto_archive_prompt: on 時的 *sync 末尾提示
📦 歸檔候選：3 張（超過 7 天未活動）
💡 使用 *archive 查看詳情並執行歸檔
```

---

## 與 `*sync` 的協作

### *sync 跳過冷區

`*sync` 掃描 `_ct-workorders/` 時，**嚴格跳過 `_archive/` 子目錄**：

```
_ct-workorders/（*sync 掃描範圍）
├── T####-*.md        ✅ 掃描
├── CP-T####-*.md     ✅ 掃描（跨專案前綴工單，歸入 sprint 同步）
├── BUG-###-*.md      ✅ 掃描（若啟用）
├── PLAN-###-*.md     ✅ 掃描（若啟用）
├── EXP-*-*.md        ✅ 掃描（若啟用）
├── _archive/         ❌ 嚴格跳過（零 token）
├── _spec-*.md 等     ❌ 跳過參考文件（見「參考文件排除」）
├── reports/          ❌ 跳過研究報告子目錄
└── _*.md             ❌ 跳過系統文件
```

### *sync 歸檔候選提示

`*sync` 結束時（步驟 10），統計歸檔候選：

1. 篩選熱區中所有最終態單據
2. 計算超過 `archive_days` 的數量
3. 若 `auto_archive_prompt: on`，顯示提示
4. 若 `auto_archive_prompt: off`，僅在摘要中顯示候選數量

### *archive 觸發 *sync

`*archive` 執行歸檔後，自動觸發 `*sync` 重建索引：
- 歸檔後的單據從索引中移除
- 活躍單據的引用關係可能改變
- 確保 sprint-status.yaml / _bug-tracker.md / _backlog.md 與熱區一致

---

## Git 整合

### git mv 策略

歸檔和取回操作使用 `git mv`（而非檔案複製+刪除）：

- 保留完整的 git 歷史記錄
- 可透過 `git log --follow` 追蹤歸檔前後的修改歷程
- 歸檔操作本身成為可追溯的 commit

### 無 Git 環境

若偵測到不在 git 管理下：

1. 使用檔案移動（mv）替代 `git mv`
2. 顯示提示：「⚠️ 非 Git 環境，使用檔案移動。歸檔操作不可透過 Git 追溯。」

---

## 錯誤處理

| 情境 | 行為 |
|------|------|
| `_archive/` 不存在 | 自動建立（含 workorders/、bugs/、plans/ 子目錄） |
| 指定單據不存在 | 列出熱區所有單據，提示選擇 |
| 指定單據在冷區（搜尋/取回） | 搜尋 `_archive/` 所有子目錄 |
| `--restore` 目標在熱區已有同名檔案 | 報錯，提示手動處理 |
| `git mv` 失敗 | 報錯，提示手動移動，不繼續後續操作 |
| 無歸檔候選 | 顯示「✅ 熱區整潔，無需歸檔」 |

---

## PLAN-034 Sprint 2 transition — frontmatter-first archive (v5.0.0+)

> v5.0.0 起，歸檔資格判定從 grep body table 升級為 frontmatter-first parser。
> `_archive/**` 永遠排除在 hot-zone sync/migration/archive candidate scan 之外。

### Frontmatter-first 判定

`*archive` 判定單據狀態與日期時使用與 `*sync` 相同的 metadata reader：

1. 若檔案有 YAML frontmatter，frontmatter 是 SoT。
2. 若無 frontmatter，fallback 既有 markdown body metadata table，並輸出 `missing_frontmatter` warning。
3. 若 frontmatter 與 body table drift，使用 frontmatter，輸出 `metadata_drift` warning，不覆寫 body。
4. Unknown status 標為 invalid/unknown，不能 fallback 到 PENDING 或非最終態。

過渡期 legacy markdown table fallback 至少保留 1 個月，直到 PLAN-034 Sprint 5 dogfood criteria 通過。

### 最終態與日期欄位來源

| 單據類型 | 最終態 | frontmatter 日期欄位 | legacy fallback |
|---------|--------|----------------------|-----------------|
| Work Order (T####) | DONE, FIXED, FAILED, PARTIAL（需覆核） | `completed_at` | `完成時間` |
| Bug Report (BUG-###) | CLOSED, WONTFIX | `closed_at` 或 `updated_at` | `關閉時間` / `更新時間` / `建立時間` |
| Plan (PLAN-###) | DONE, DROPPED | `completed_at` 或 `updated_at` | `完成時間` / `更新時間` / `建立時間` |
| Experiment (EXP-*) | CONCLUDED, ABANDONED | `concluded_at` 或 `updated_at` | `結論時間` / `建立時間` |

日期欄位優先使用 quoted ISO 8601 with offset，例如 `"2026-04-28T19:16:49+08:00"`。
若日期缺失，保留既有降級行為：以建立時間為候選天數基準，但摘要中標示 `date_fallback=created_at`。

> Work Order 最終態於 v5.0.0 從 `DONE, FAILED` 擴充為 `DONE, FIXED, FAILED, PARTIAL`。
> v5.0.2 起，`PARTIAL` 歸檔前必須先覆核 blocker 是否已由後續工單、scope decision 或 final acceptance 解除。v5.13.0 起這是**最後防線**：
> 塔台裁示當下就該收尾，做法以 [work-order-system.md](work-order-system.md) § 回報處理流程 › PARTIAL 當下收尾 為準。歸檔時仍掛著 `PARTIAL` 的，照該節補做後再歸檔；
> 只有仍在等外部條件、或被明確接受為部分完成結果的才保留 `PARTIAL`。

### 掃描排除

```text
1. 掃描 `_ct-workorders/*.md` hot-zone 檔案。
   - 永遠排除 `_ct-workorders/_archive/**`。
   - 永遠排除 `_ct-workorders/_spec-*.md`、`_report-*.md`、`_spike-*.md`、`_question-*.md`、`_roadmap-*.md`。
   - frontmatter migration 也不得掃描 `_archive/**`。
```

### Frontmatter transition warnings

```text
[PLAN-034 missing_frontmatter] T0045-user-auth.md
action=legacy_archive_parser_used; fallback_retained_until=2026-05-28

[PLAN-034 metadata_drift] BUG-003-login-crash.md
field=status frontmatter=CLOSED body=VERIFY
action=frontmatter_used; body_not_modified

[PLAN-034 invalid_status] PLAN-002-refactor.md
field=status value=COMPLETE
action=archive_candidate_skipped; reason=unknown_status
```

### 驗收

- 歸檔判定使用 frontmatter status first。
- `completed_at` / `closed_at` / `concluded_at` 等欄位優先於 body table。
- legacy markdown table fallback 明確保留至少 1 個月。
- Unknown status 不會被當成 PENDING 或安全非最終態靜默略過。
- `_archive/**` 在 sync、migration、archive candidate scan 中都明確排除。
