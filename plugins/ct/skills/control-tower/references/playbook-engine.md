# 知識成熟度管線（Playbook Engine）

> 將零散觀察逐步成熟為可複用 playbook，最終晉升為永久 skill。
> 讓 Control Tower 的學習成果從「紀錄」進化為「可執行知識」。

## 管線總覽

```
Level 0: 觀察（_learnings.md 中的觀察紀錄）
  ↓ *evolve 萃取 + 使用者確認
Level 1: 驗證規則（_learnings.md 中標記 validated / 🟢）
  ↓ *evolve --playbook 晉升
Level 2: Playbook（_playbooks/*.md）
  ↓ /skill-creator 永久化
Level 3: Skill（~/.claude/skills/）
```

**Workflow 分支（v5.10.0+）**：形狀落在「單張工單之內」的候選（ct-evolve `[WF-CANDIDATE]`）不走上面的 Playbook 晉升，
改走 `/ct-evolve --workflow` → `_workflows/` 知識卡（🔵 brief → 🟡 回測 → 🟢 → ⭐，且有指標降級）。
重複發生在工單「之間」的仍是 Playbook。三分法、知識卡格式、成熟度與降級見 [workflow-engine.md](workflow-engine.md)（唯一權威）。

### 晉升標準

| 晉升 | 條件 | 觸發者 |
|------|------|--------|
| L0→L1（觀察→驗證） | 同一模式在 2+ 工單中重複出現（即專案層 🟢；條件以 [self-learning-core.md](self-learning-core.md) § 置信度系統 為準） | `*evolve` 自動標記 |
| L1→L2（驗證→Playbook） | validated（🟢 reliable）+ 使用者確認 | `*evolve --playbook` |
| L2→L3（Playbook→Skill） | playbook 在 3+ 專案使用 + 使用者決定 | `*evolve --skill` → `/skill-creator` |

### 與現有置信度系統對應

各級條件的唯一權威是 [self-learning-core.md](self-learning-core.md) § 置信度系統（分專案層／全域層）；本表只把管線等級對到置信度符號。

| 管線等級 | 置信度符號 | 說明 |
|---------|----------|------|
| L0 觀察 | 🔵 new | 首次記錄，靜默觀察 |
| L0→L1 過渡 | 🟡 validating | 1 次驗證，遇匹配時建議 |
| L1 驗證 | 🟢 reliable | 專案層 2+ 工單重複出現（全域層要 2+ 專案驗證），主動應用 |
| L1→L2 候選 | 🟢 reliable + 完整序列 | 可升級為 Playbook |
| L2 Playbook | ⭐ proven（playbook 內） | 3+ 驗證的成熟 playbook |
| L2→L3 候選 | ⭐ proven + 跨 3+ 專案 | 可升級為永久 Skill |

## 目錄結構

```
_ct-workorders/
├── _playbooks/
│   ├── feature-story-standard.md
│   ├── research-workorder-pattern.md
│   ├── bug-fix-standard.md
│   └── ...
├── _learnings.md
└── ...

~/.claude/control-tower-data/
├── playbooks/           ← 全局 playbook（從專案晉升）
│   ├── brownfield-reverse-eng.md
│   └── ...
└── ...
```

## Playbook 標準格式

```markdown
# Playbook: <名稱>

> 驗證次數：N（最近：T####）
> 置信度：🟢 可靠 / 🟡 實驗中 / 🔴 未驗證
> 首次記錄：<日期>
> 範圍：project / global
> 來源 Pattern：P### / SEQ###（from _learnings.md）
> Skill 候選：是 / 否（達 ⭐ 時標記）

## 適用場景
- <觸發條件 1>
- <觸發條件 2>

## 不適用場景
- <排除條件 1>

## 序列定義

### 工單 1：<名稱>（預估 ~N min）
- 命名：`T{N}-<pattern>`
- Session 建議：🆕 新 Session
- 包含：<預期內容>

### 工單 2：<名稱>（預估 ~N min）
...

## 品質關卡
- <條件> → 觸發 <動作>

## 工單模板
<各步驟的工單模板片段>

## 注意事項
<執行要點、常見陷阱>

## 驗證歷史
| 執行 | 專案 | 工單 | 結果 | 時間 |
|------|------|------|------|------|

## Skill 晉升紀錄
（達到 ⭐ proven 且跨 3+ 專案時，記錄 /skill-creator 產出路徑）
```

## `*evolve` 擴展子命令

| 語法 | 行為 |
|------|------|
| `*evolve` | （不變）從最近工單萃取學習，寫入 _learnings.md |
| `*evolve --playbook [name]` | 從 validated 學習晉升為 playbook → 寫入 _playbooks/ |
| `*evolve --skill [name]` | 提示使用者用 /skill-creator 將 playbook 永久化 |
| `*evolve --workflow [name]` | v5.11.0+。**轉交 `/ct-evolve --workflow [name]`**（只產 brief 與 🔵 知識卡；不寫 `.claude/workflows/`、不執行 Workflow）。行為的權威在 `ct-evolve/SKILL.md` § Promotion Modes，塔台不另做一套 |
| `*evolve --status` | 顯示知識成熟度統計面板 |

### `*evolve --playbook [name]`

**行為**：

0. **決定 GP 編號前綴**（D62 協議，見下方「GP 編號規則」）：讀 `_tower-config.yaml` 的 `gp-prefix`；
   設定位置與未設定時的 fallback 鏈（含拒絕晉升）見
   [multi-tower-protocol.md](multi-tower-protocol.md) § `gp-prefix` 設定（唯一權威定義）
1. 掃描 `_learnings.md` 中 🟢 reliable 以上的 pattern 和完整工作流程序列（SEQ）
2. 列出候選清單：
   ```
   📘 Playbook 候選
     [1] P005 + SEQ001 — 棕地逆向工程（驗證 3 次，🟢）
     [2] P008 + P009 — 安全修復標準流程（驗證 4 次，🟢）
   選擇候選（編號），或輸入自訂名稱：
   ```
3. 若帶 `[name]` 參數：直接以該名稱建立，跳過候選選擇
4. 使用者選定後，自動產生 Playbook 草稿（填入 metadata、序列、品質關卡）
5. 顯示草稿預覽，使用者確認後寫入
6. **分流提問**（見下方 Global/Project 分流）：
   - [A] 通用 → `~/.claude/control-tower-data/playbooks/<name>.md`
   - [B] 本專案 → `_ct-workorders/_playbooks/<name>.md`
7. 執行寫入路徑安全檢查後寫入

**無候選時**：
```
📘 目前沒有 🟢 reliable 以上的 pattern 可升級。
   L0 觀察：N 條 / L1 驗證中：M 條
   💡 繼續執行工單，累積驗證次數後再嘗試。
```

### `*evolve --skill [name]`

**行為**：

1. 掃描 `_playbooks/` 中 ⭐ proven 以上且跨 3+ 專案驗證的 playbook
2. 列出候選清單：
   ```
   🎯 Skill 晉升候選
     [1] brownfield-reverse-eng（驗證 5 次，跨 3 專案，⭐）
   選擇候選（編號）：
   ```
3. 若帶 `[name]` 參數：直接定位該 playbook
4. 使用者選定後：
   - 萃取 Playbook 核心邏輯：
     - 適用/不適用場景 → Skill 觸發條件
     - 工單序列 → Skill 執行步驟
     - 品質關卡 → Skill 驗收條件
   - 產生 Skill 草稿摘要
   - 提示使用者：「請在新 session 執行 `/skill-creator`，以下是建議的 skill 規格：」
   - 顯示規格摘要供複製
5. 回寫 Playbook：標記「已晉升為 Skill: `<skill-name>`」

**無候選時**：
```
🎯 目前沒有 ⭐ proven 以上的 Playbook 可晉升為 Skill。
   📋 Playbooks：N 個（最高置信度：🟢）
   💡 在更多專案中使用 Playbook，累積跨專案驗證。
```

### `*evolve --status`

**行為**：統計各 Level 數量，顯示統計面板。

1. 讀取 `_learnings.md`：計算各置信度的 pattern 數量
2. 讀取 `_playbooks/`：計算 playbook 數量和置信度
3. 讀取 Layer 2（若存在）：計算全局 playbook 數量
4. 顯示統計面板

**面板格式**：

```
📚 知識成熟度管線

  Level 0 觀察：N 條（_learnings.md）
  Level 1 驗證：N 條（validated）
  Level 2 Playbook：N 個（_playbooks/）
  Level 3 Skill：N 個（已晉升）

  候選晉升：
  - L005 → Playbook（驗證 4 次，置信度 🟢）
  - L012 → Playbook（驗證 2 次，置信度 🟡）

  ⭐ Skill 候選：
  - brownfield-reverse-eng（跨 3 專案，⭐）
```

**無數據時**：
```
📚 知識成熟度管線

  Level 0 觀察：0 條
  Level 1 驗證：0 條
  Level 2 Playbook：0 個
  Level 3 Skill：0 個

  💡 開始執行工單後，*evolve 會自動累積觀察。
```

## GP 編號規則（D62）

> 跨塔台共用同一個 user 環境（`~/.claude/control-tower-data/playbooks/`）時，舊規則
> 「全域 max+1」會撞號（已實證 GP071-075 案例，參見 D62 決策日誌）。D62 改採命名空間前綴
> 確保各塔台自治、零同步成本。

### 命名格式

```
GP-<PREFIX>-###
```

- `PREFIX`：2-4 字元大寫英文（由 `gp-prefix` config 決定）
- `###`：3 位數流水號，從 `001` 起，**namespace 內**遞增

**範例**：

| 塔台 | gp-prefix 設定 | 第 1 個新晉升編號 | 第 N 個 |
|------|---------------|-----------------|---------|
| project-b | `COOP` | `GP-COOP-001` | `GP-COOP-N` |
| BAT (Better Agent Terminal) | `BAT` | `GP-BAT-001` | `GP-BAT-N` |
| BMad-Guide | `BMAD` | `GP-BMAD-001` | `GP-BMAD-N` |

### 編號計算範圍

新編號 = **同 namespace** 的 max + 1：

```
max(grep "GP-<PREFIX>-" 在 ~/.claude/control-tower-data/playbooks/)
+ max(grep "GP-<PREFIX>-" 在 _ct-workorders/_playbooks/)
→ 取兩者較大者 + 1
```

**不**跨 namespace 查（其他 namespace 的 playbook 視為「他塔台資產」）。

### 凍結號段（GP001-094）

D62 協議生效前的 playbook（編號 `GP001` 到 `GP094`）**完全凍結**：

- 不改名（保持原 `GP089-xxx.md` 格式）
- 不重新晉升（已存在的繼續引用）
- 引用方式不變（工單寫「依 GP070 流程」依然有效）
- `*evolve --playbook` **不會**產生 `GP095` 或更大的「無前綴」編號

新晉升一律使用 `GP-<PREFIX>-###` 格式。

### Fallback 鏈

`gp-prefix` 未設時的 fallback 鏈與拒絕晉升行為，見
[multi-tower-protocol.md](multi-tower-protocol.md) § `gp-prefix` 設定（唯一權威定義），本節不複述。

### 跨塔台採納流程

D62 協議跨多個 user 環境採納時，每個塔台**獨立**執行以下：

1. 在 `_tower-config.yaml` 設 `gp-prefix: <自定義 PREFIX>`
2. 確認 PREFIX 與其他塔台不衝突（見 `multi-tower-protocol.md` § 命名空間註冊）
3. 之後 `*evolve --playbook` 自動採納

未設定 `gp-prefix` 的塔台，行為依 [multi-tower-protocol.md](multi-tower-protocol.md) § `gp-prefix` 設定的 fallback 鏈；不影響其他已採納塔台。

### 與舊 Pattern 編號（P###）的關係

- `P###`（如 `P017` `P018`）是 _learnings.md 中的 Pattern 編號，**不在** D62 範圍
- D62 僅約束 `GP###` → `GP-<PREFIX>-###`（Playbook 層級）
- Pattern 編號保持原規則（local namespace per project）

---

## Global/Project 分流

沿用現有三層架構（見 [data-layer-architecture.md](data-layer-architecture.md)）。

### 分流提問

Playbook 寫入時，詢問使用者儲存範圍：

```
📦 Playbook 儲存範圍選擇
   Playbook：<名稱>

   這個 Playbook 適用範圍是？
   [A] 通用（適用全部專案）→ 存入全局 Layer 2
   [B] 本專案 → 存入專案 Layer 3
   [C] 不確定 → 先放專案，日後 review 再決定
```

### 寫入路徑對照

| 使用者選擇 | Playbook 寫入目標 |
|-----------|-------------------|
| [A] 通用 | `~/.claude/control-tower-data/playbooks/GP-<PREFIX>-###-<name>.md`（scope: global） |
| [B] 本專案 | `_ct-workorders/_playbooks/GP-<PREFIX>-###-<name>.md` |
| [C] 不確定 | `_ct-workorders/_playbooks/GP-<PREFIX>-###-<name>.md`（加 `candidate: global` 標記） |

> 檔名格式 `GP-<PREFIX>-###-<name>.md` 由 D62 協議定義，`<PREFIX>` 從 `gp-prefix` config 決定。
> 詳見上方「GP 編號規則（D62）」。

### `candidate: global` 標記

在 Playbook metadata 中加入標記行：

```markdown
> 範圍：project
> candidate：global ← 待 review 是否晉升全局
```

日後執行 `*evolve --status` 或 `/ct-evolve` 時，掃描帶 `candidate: global` 標記的 playbook，主動提議晉升。

### Layer 2 自動初始化

首次選擇 [A] 通用時，若 Layer 2 `playbooks/` 目錄不存在：

1. 提示：「全局 playbook 目錄尚未建立，是否現在建立？」
2. 使用者確認後建立（見 [data-layer-architecture.md](data-layer-architecture.md) 建立指令）
3. 使用者拒絕 → 降級為 Layer 3 寫入，標記 `candidate: global`

## 塔台自動建議（派發匹配）

塔台準備派發工單前，自動掃描 playbook 匹配：

> Workflow 知識卡（`_workflows/`）的派發匹配**待卡片達 🟡 後再定**（v5.11.0 起，D090）；匹配流程只掃 playbook，不掃 `_workflows/`（[workflow-engine.md](workflow-engine.md) § 尚未定案）。
> 塔台想知道某張工單適不適合 Workflow，改用按需的 `*insights workflow [T#### …]`（`ct-insights/references/analysis-rules.md` § 預篩腳本：排除守門與按需提示），它不會自動標記工單。

### 匹配流程

```
1. 讀取 _playbooks/ 和全局 playbooks/（若存在）
2. 對每個 playbook 的「適用場景」比對當前任務描述
3. 匹配命中 → 向使用者建議套用
4. 使用者決定：套用 / 不套用 / 修改後套用
```

### 匹配邏輯

比對維度：
- **工單類型關鍵字**：feature / bug / research / refactor 等
- **技術棧關鍵字**：與 playbook 適用場景中的技術棧比對
- **工作流程模式**：工單是否屬於已知序列的一部分

### 建議格式

```
📘 偵測到匹配 Playbook
   Playbook：feature-story-standard（🟢 可靠，驗證 5 次）
   匹配原因：工單類型 = feature + 標準開發流程

   [A] 套用此 Playbook（按序列產生 N 張工單）
   [B] 不套用（手動規劃）
   [C] 修改後套用（預覽並調整序列）
```

### 套用行為

使用者選擇 [A] 或 [C] 時：
1. 按 Playbook 的「序列定義」逐一產生工單
2. 套用 Playbook 的「品質關卡」到對應工單
3. 工單回報區新增「Playbook 來源」標記：`playbook: <name>`
4. 更新 Playbook 的「驗證歷史」

## 寫入路徑安全檢查

所有 Playbook 寫入操作必須通過路徑檢查（沿用 [self-learning-core.md](self-learning-core.md) 的安全檢查）：

```
寫入目標路徑檢查流程：
1. if path 落在 Layer 1 路徑（範圍見權威定義）→ 依權威定義判定（Playbook 寫入一律 ❌ 拒絕）
2. if path starts with ~/.claude/control-tower-data/playbooks/ → ✅ Layer 2（全局）
3. if path starts with _ct-workorders/_playbooks/ → ✅ Layer 3（專案）
4. else → ❌ 拒絕（不明路徑）
```

> 第 1 步的判定範圍與唯一例外，見
> [data-layer-architecture.md](data-layer-architecture.md) § 寫入規則（唯一權威定義）。
>
> Workflow 知識卡（`_ct-workorders/_workflows/`、`~/.claude/control-tower-data/workflows/`）不是 Playbook 寫入，不走本檢查，
> 改走 [workflow-engine.md](workflow-engine.md) § 寫入路徑檢查（知識卡），不會被判成不明路徑。

## 與 `/ct-evolve` 的整合

`/ct-evolve`（學習萃取模式）會找出 Playbook 候選，但不自己寫 playbook。本引擎擴展如下：

| 特性 | `*evolve --playbook` | `/ct-evolve`（學習萃取模式） |
|------|---------------------|---------------------|
| 執行位置 | 塔台 session 內 | 任意 session（獨立 skill） |
| 候選來源 | 使用者指定或自動掃描 🟢 | `ct-evolve/SKILL.md` § Extraction Flow 找到的 recurring sequences，再由使用者決定是否 `--playbook` |
| 互動深度 | 選擇 + 確認 | 完整流程（含 ECC 同步） |
| 適用情境 | 隨時在塔台快速晉升 | Sprint 結束或專案結案 |
