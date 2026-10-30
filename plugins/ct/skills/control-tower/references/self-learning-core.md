# 自包含學習核心（Level 0）

本協議零相依——只要 AI 能讀寫 .md 檔案就能完整運作。
有 ECC 時自動增強（見 enhancement-integration.md），無 ECC 時本檔即為完整學習系統。

## _learnings.md 格式

存放於 `_ct-workorders/_learnings.md`，塔台啟動時讀取、運作中更新。

### 三區結構（v4.4.0 Phase 3+，新產出強制）

v4.4.0 Phase 3（T0105）起新產出以三區結構分流：

```markdown
# 塔台學習紀錄

> 由塔台自動維護。啟動時讀取，用於改善決策品質。
> 格式為純 markdown，任何 AI Agent 均可讀寫。
> Phase 3（v4.4.0+）起採三區結構，分類規則見 ct-evolve SKILL.md Step 2.6。

## 🧭 Strategic（跨技術棧決策原則）
<!-- 供塔台做架構決策 / 新 skill 設計時查閱 -->
<!-- 判定：5 年後本 repo 換技術棧仍適用 → 歸此區 -->

（新產出累積處）

## 🔧 Tactical（具體技術操作 know-how）
<!-- 供 Worker 遇到具體技術問題時查閱 -->
<!-- 判定：綁定具體語言 / 工具 / 指令 → 歸此區 -->

（新產出累積處）

## 📜 Episodic 事件日誌（未 distill）
<!-- Phase 2 T0104 引入；Step 2.5 未過關的條目暫存 -->

（暫存處）

## 工作流程序列
<!-- 跨技術棧的流程資產，不分 tactical/strategic，一律視為 Strategic 類 -->

（見下方格式）

## 估時校準
<!-- 獨立於三區結構 -->

| BMad 流程 | 樣本 | 平均(min) | 建議預估 |
|-----------|------|-----------|---------|

## 📚 歷史條目（Phase 3 之前，不 retrofit）
<!-- Phase 1-2 累積條目以 <details> 摺疊保留，不自動搬位 -->

<details>
<summary>展開查看</summary>

（舊版傳統格式條目或四欄格式但未分流條目）

</details>
```

### AC-3 不 retrofit 規則

- **禁止**：自動把歷史條目按新分類搬位
- **允許**：使用者在實戰中引用某歷史條目 ≥ 2 次後，**手動**升級移入新區（不自動化）
- 歷史條目保留在 `## 📚 歷史條目` 區以 `<details>` 摺疊，不影響新產出累積

### 跨 consumer 驗證機制（AC-6）

三區結構在實戰中是否好用，需要透過多個 consumer 驗證：

- **Stable consumer**（dogfood verification site #1）：套用新結構後運作 2-4 週，回饋「tactical / strategic 分類是否好判定」
- **Aggressive consumer**（dogfood verification site #2）：同上，並主動產出 ≥ 10 條 strategic 條目作為驗證樣本
- **回饋管道**：各 consumer 在自己的 repo 開對等追蹤 PLAN，定期同步到 CT skill 主 repo
  - 同步方式：走 `_cross-references.md`（若有），或直接 session 對話
  - 同步節奏：建議 1-2 週一次

**驗收指標**：
- 抽查 5 條 tactical 條目，確認「換技術棧就失效」標準一致
- 累積 ≥ 10 條 strategic 條目（跨 consumer 總和）
- 分類準確率 ≥ 80%（人工抽驗時歸屬正確）

> **不強制同步節奏**：各 consumer 自行決定何時套用新結構。本 skill 主 repo 保留新舊結構並存能力（Phase 3 前的 `_learnings.md` 仍可用平面結構）。

## 決策模式格式

### 傳統格式（v4.3.x 及以前；歷史條目保留）

```markdown
### P<編號>: <名稱>
- **觸發**：<什麼情境下應套用此模式>
- **規則**：<具體該怎麼做>
- **來源**：<日期 + 專案 + 事件>
- **驗證次數**：<數字>
- **狀態**：🔵/🟡/🟢/⭐
```

### 四欄格式（v4.4.0+ 新產出強制）

v4.4.0 起由 `*evolve` / `/ct-evolve` 的 Step 2.5 Distillation 檢核把關。每條新模式寫入主區時必須以四欄呈現：

```markdown
### P<編號>: <名稱>
- **Learning**: <一句話總結；等同傳統 `規則` 欄>
- **Trigger**: <觸發條件；if-then 的 if 部分。必須脫離單一工單描述>
- **Pattern**: <通用模式 / 歸屬類別；if-then 的 then 部分 + 類別掛點>
- **Action**: <建議對策；必須是可執行動作>
- **Example**: <一個具體案例作錨點，**僅一條**，避免退化回事件日誌>
- **來源**：<日期 + 專案 + 工單編號>
- **驗證次數**：<數字>
- **狀態**：🔵/🟡/🟢/⭐
```

**向下相容**：既有 TL001-TL### 等傳統格式條目不 retrofit。僅新產出強制四欄。

**Trigger/Pattern 語意層檢核**（Template bias 防線，T0100 audit 成果）：

只檢查「四欄是否填滿」會產生 Template bias——欄位完整但內容仍 episodic。Step 2.5 額外要求語意自問：

- **條件脫離性**：Trigger 若套在別的工單/專案/時間，是否還能用同樣措辭判斷？
- **if-then 結構**：Pattern 是否真有「當 X 成立 → 採取 Y」結構？
- **反覆驗證性**：寫成 checklist 交給沒看過事件的人，能否據此辨識下次同類情境？

三問任一為「否」→ 候選歸 Episodic 區，不進主區。詳見 `ct-evolve/SKILL.md` Step 2.5。

## 反模式格式

```markdown
### A<編號>: <名稱>
- **描述**：<錯誤做法>
- **正確做法**：<應該怎麼做>
- **來源**：<日期 + 專案 + 事件>
```

## 工作流程序列格式

```markdown
### SEQ<編號>: <名稱>
- **序列**：<step1 → step2 → step3>
- **工單數**：<N>
- **總耗時**：<~Nmin>
- **成功率**：<N%>
- **驗證次數**：<N>
- **適用場景**：<描述>
```

## Episodic 事件日誌（v4.4.0+）

### 用途

暫存已記錄但**未通過 Step 2.5 Distillation 檢核**的事件條目。避免 episodic raw 直接膨脹 `_learnings.md` 主區（T0100 audit 暴露的主因之一）。

### 區段位置

- **專案層**：`_ct-workorders/_learnings.md` 底部新增 `## Episodic 事件日誌（未 distill）` 區
- **全局層**：`~/.claude/control-tower-data/learnings/patterns.md` 底部同名區段（按需建立）

### Episodic 條目格式

```markdown
### E<編號>: <一句話描述事件>
- **發生時間**：<日期>
- **工單**：<T#### 或多個>
- **事件**：<原始敘述，可含專有名詞、具體檔名>
- **嘗試 distill 結果**：<說明哪一條未通過（Trigger 寫不出 / Pattern 無 if-then / 自問失敗）>
- **Review tag**：<empty / 待 review / 已 distill 移至 P###>
```

### Review 節奏

- **每季**（或使用者主動觸發 `*evolve --review-episodic`）檢視 Episodic 區：
  - 若累積多次類似事件 → 有機會抽出新 Trigger/Pattern，移到主區（標註來源 E###）
  - 若單次事件長期無同類 → 標記「歸檔」或刪除
- **禁止**：直接把 Episodic 條目複製到主區而不重做 Step 2.5 檢核

### 與 Step 2.5 的契約

1. `*evolve` / `/ct-evolve` 在 Step 2.5.4 判定為 Episodic 的候選 → 寫入本區
2. 本區條目**不**計入置信度系統（🔵/🟡/🟢/⭐）
3. 本區條目**不**觸發分流提問（一律專案層，除非 review 時升級）
4. 本區條目**不**被 `學習應用（派發前匹配）` 流程讀取——僅主區條目會影響塔台決策

## 置信度系統

本節是置信度各級條件的**唯一權威定義**（v5.12.3 起分兩層）；[playbook-engine.md](playbook-engine.md) § 晉升標準、
§ 與現有置信度系統對應 與安裝指南 § 8 只放摘要並引用本節。

- **專案層**：本專案 Layer 3 的 `_learnings.md`
- **全域層**：晉升到 Layer 2（`~/.claude/control-tower-data/`）的全域 learnings 與全域規則

| 符號 | 狀態 | 專案層條件 | 全域層條件 | 行為 |
|------|------|-----------|-----------|------|
| 🔵 | 觀察 | 首次記錄 | 同專案層 | 靜默記錄，不主動推薦 |
| 🟡 | 初步 | 1 次驗證 或 使用者確認 | 同專案層 | 遇匹配時建議 |
| 🟢 | 可靠 | 同一模式在 2+ 工單重複出現（= 知識成熟度管線 L1 `validated`） | 2+ 專案驗證 | 主動應用到決策 |
| ⭐ | 規則 | 3+ 驗證 + 使用者認可 | 同專案層 | 塔台預設行為 |

> v5.12.3 之前本表只有一欄，🟢 寫「2+ 專案驗證」，而 playbook-engine.md 的 L0→L1 寫「2+ 工單重複出現」；兩者分屬上面兩層，這裡把它們並列。

升級：專案層每次在新工單中再次驗證、全域層每次在新專案中成功應用 → 依上表條件升級
降級：使用者說「這個不適用」→ 標記 ❌ 廢棄（保留歷史）
衰減：連續 3 個專案未觸發 → 標記「休眠」

> v5.10.0+：Workflow 知識卡另有依指標的降級（只限 Workflow，不適用本表），見 [workflow-engine.md](workflow-engine.md) § 指標降級。

## 寫入路徑安全檢查

所有學習系統的寫入操作**必須**通過以下路徑檢查：

```
寫入目標路徑檢查流程：
1. if path 落在 Layer 1 路徑（範圍見權威定義）→ 依權威定義判定（學習系統寫入一律 ❌ 拒絕）
2. if path starts with ~/.claude/control-tower-data/ → ✅ Layer 2（全局學習）
3. if path starts with _ct-workorders/ → ✅ Layer 3（專案學習）
4. else → ❌ 拒絕（不明路徑）
```

> 第 1 步的判定範圍與唯一例外，見
> [data-layer-architecture.md](data-layer-architecture.md) § 寫入規則（唯一權威定義）。

**違反時行為**：
- 記錄違規嘗試到工單回報區「遭遇問題」
- 不執行寫入
- 提示正確的目標路徑

> 此檢查適用於所有觸發時機（工單回報後靜默記錄、*evolve、/ct-evolve）。
>
> v5.10.0+：Workflow 知識卡的 `_ct-workorders/_workflows/` 落在第 3 步、`~/.claude/control-tower-data/workflows/` 落在第 2 步，都不是不明路徑
> （卡片的專屬檢查見 [workflow-engine.md](workflow-engine.md) § 寫入路徑檢查（知識卡））。
> 專案 workflow 腳本 `.claude/workflows/*.js` 不是學習寫入，在本檢查落到第 4 步拒絕；它只能由 Worker 依工單 `affects_files` 寫入，
> 見 [data-layer-architecture.md](data-layer-architecture.md) § Layer 3 附屬：專案 workflow 腳本。

## Global/Project 分流寫入

學習萃取（`*evolve` 和 `/ct-evolve`）在模式偵測完成後，**必須**詢問使用者每個新模式的儲存範圍。

### 分流提問

使用者確認萃取出的模式/反模式後，逐一或批次詢問：

```
📦 儲存範圍選擇
   模式：P003 — 大型分析工單需預估工作量

   這個模式適用範圍是？
   [A] 通用（適用全部專案）→ 存入全局 Layer 2
   [B] 本專案 → 存入專案 Layer 3
   [C] 不確定 → 先放專案，日後 review 再決定
```

> 工單回報後的靜默記錄（觸發時機 1）**不觸發分流提問**，一律寫入 Layer 3（維持現有行為）。
> 分流提問僅在使用者主動觸發的 `*evolve` 和 `/ct-evolve` 流程中出現。

### 寫入路徑對照

| 使用者選擇 | learnings 寫入目標 | playbooks 寫入目標 |
|-----------|-------------------|-------------------|
| [A] 通用 | `~/.claude/control-tower-data/learnings/patterns.md` | `~/.claude/control-tower-data/playbooks/` |
| [B] 本專案 | `_ct-workorders/_learnings.md` | `_ct-workorders/_playbooks/` |
| [C] 不確定 | `_ct-workorders/_learnings.md`（加 `candidate: global` 標記） | `_ct-workorders/_playbooks/`（加 `candidate: global` 標記） |

### candidate: global 標記格式

在模式/反模式的 metadata 中加入標記行：

```markdown
### P003: 大型分析工單需預估工作量
- **觸發**：工單涉及 >100 檔案
- **規則**：預估工作量並寫入工單
- **來源**：2026-03-31 / my-app / T0002
- **驗證次數**：1
- **狀態**：🔵
- **candidate**：global ← 待 review 是否晉升全局
```

日後執行 `/ct-evolve` 時，掃描帶 `candidate: global` 標記的模式，主動提議晉升。

### Layer 2 自動初始化

首次選擇 [A] 通用時，若 Layer 2 目錄不存在：

1. 提示：「全局學習目錄尚未建立，是否現在建立 `~/.claude/control-tower-data/`？」
2. 使用者確認後自動建立目錄結構（見 [data-layer-architecture.md](data-layer-architecture.md) 建立指令）
3. 建立完成後繼續寫入
4. 使用者拒絕 → 降級為 Layer 3 寫入，標記 `candidate: global`

## 學習觸發時機

### 1. 工單回報後（每次，靜默）

塔台處理工單回報後**自動**執行（不需使用者觸發，不顯示過程）：
- 追加一行到「觀察紀錄」表格
- 若本輪對話中有使用者糾正 → 追加到「反模式」，若可歸納規則 → 追加「決策模式」（🟡）
- 更新「估時校準」

### 2. `*evolve`（塔台內建精簡版）

在塔台 session 內快速萃取學習紀錄，不離開塔台角色。

**語法**：`*evolve [topic]`

**行為**：
1. 不帶參數：從最近完成的工單中萃取學習紀錄
2. 帶參數：針對指定主題萃取（如 `*evolve estimation` 萃取估時模式）
3. 讀取 `_learnings.md`，分析觀察紀錄
4. 提出模式/反模式建議
5. **分流提問**：使用者確認模式後，詢問儲存範圍（見「Global/Project 分流寫入」）：
   - [A] 通用（全部專案）→ 寫入 Layer 2
   - [B] 本專案 → 寫入 Layer 3
   - [C] 不確定 → 寫入 Layer 3 並加 `candidate: global` 標記
6. 執行寫入路徑安全檢查後寫入對應目標

**與 `/ct-evolve` 的差異**：
| 特性 | `*evolve` | `/ct-evolve` |
|------|-----------|-------------|
| 執行位置 | 塔台 session 內 | 任意 session（獨立 skill） |
| 角色切換 | 不切換，保持塔台角色 | 載入完整學習萃取角色 |
| 功能範圍 | 快速萃取，聚焦最近工單 | 完整流程（模式偵測、Playbook、ECC 同步、全局規則） |
| 適用情境 | 塔台工作中順手萃取 | Sprint 結束、專案結案等完整萃取 |

### 3. `/ct-evolve`（完整版，手動觸發）

完整規範見 [ct-evolve/SKILL.md](../../ct-evolve/SKILL.md)（唯一權威）。涵蓋：模式偵測、蒸餾後寫入 _learnings.md、Playbook 候選建議（寫入走 `--playbook`）、ECC 同步、全局規則評估。

也在 Sprint 結束和專案結案時由塔台主動提議執行（v5.12.5 起由已退役的 `/ct-evolve` 長版說明搬入本節）：

**Sprint 結束時的提議**——塔台在以下時機主動提議執行 `/ct-evolve`：
- 使用者說「Sprint 結束」「Epic 完成」「回顧」
- 累積 ≥10 筆觀察紀錄且尚未萃取

提議格式：
```
Sprint 結束。本 Sprint 執行了 N 張工單，累積 N 筆觀察。
要我執行學習萃取嗎？
```

**專案結案時的提議**——使用者說「結案」「專案完成」時，塔台提議執行 `/ct-evolve` 做全量萃取，並：
1. 提議對所有 🟢 以上候選跑 `--playbook`，照 [playbook-engine.md](playbook-engine.md) § `*evolve --playbook [name]` 顯示草稿、使用者確認後再做分流提問；不經確認不寫 playbook
2. 檢查所有 ⭐ 候選並提議全局化
3. 顯示專案學習總結

## 學習應用（派發前匹配）

塔台準備派發工單前，靜默匹配 _learnings.md：
1. 讀取「決策模式」，比對每個模式的「觸發」與當前工單性質
2. 🟢+ 置信度 → 自動應用到工單設計，告知使用者
3. 🟡 置信度 → 在工單摘要中附帶建議
4. 讀取「估時校準」→ 填入工單的工作量預估
5. 讀取「工作流程序列」→ 若匹配場景，主動推薦已驗證的序列

## 新專案啟動時的學習載入

1. 讀取本專案 `_learnings.md`（若存在）
2. 讀取 `_playbooks/`（若存在）
3. 若有 Layer 2（`~/.claude/control-tower-data/learnings/`）→ 載入全局模式
4. 若有 mem0 REST（Level 3）→ ⚠️ Tower 無法直接查詢，跨裝置經驗僅透過 Stop hook 寫入同步（單向）；查詢需透過 OpenMemory UI（192.0.2.10:3100）或 sub-session 直接呼叫 REST API
5. 顯示載入摘要
