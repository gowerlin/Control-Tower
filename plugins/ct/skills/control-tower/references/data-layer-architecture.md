# 三層資料架構（Data Layer Architecture）

> Control Tower v3.3+ 的資料分層設計。
> 解決「塔台自我學習寫入 skill 原始檔，導致升級覆蓋衝突」的根本問題。

## 架構總覽

```
Layer 1: Core Skills（唯讀，升級時整份覆蓋）
  ~/.claude/skills/control-tower/
  ~/.claude/skills/ct-exec/
  ~/.claude/skills/ct-done/
  ~/.claude/skills/ct-status/
  ~/.claude/skills/ct-evolve/
  ~/.claude/skills/ct-fieldguide/
  ~/.claude/skills/ct-help/
  ~/.claude/skills/ct-insights/
  ~/.codex/skills/<同上 8 個 skill>/   ← Codex 端安裝位置
  ~/.claude/plugins/、$CODEX_HOME/plugins/ …  ← plugin 安裝位置（v5.14.0+；完整清單見 § 寫入規則）

Layer 2: Global Learning（使用者級，跨專案，升級不碰）
  ~/.claude/control-tower-data/
  ├ learnings/
  │  ├ patterns.md         ← 跨專案通用模式
  │  └ anti-patterns.md    ← 跨專案踩過的坑
  ├ playbooks/             ← 全局 playbook（從專案晉升）
  ├ workflows/             ← 全局 workflow 知識卡（v5.10.0+，見 workflow-engine.md）
  ├ extensions/            ← 使用者自訂擴展規則
  ├ project-registry.md    ← 跨專案索引（專案名 → 路徑對照）
  └ config.yaml            ← 全局設定

Layer 3: Project Learning（專案級，現有機制，不變動）
  <project-root>/_ct-workorders/
  ├ _learnings.md          ← 專案學習紀錄
  ├ _playbooks/            ← 專案 playbook
  ├ _workflows/            ← 專案 workflow 知識卡（v5.10.0+，見 workflow-engine.md）
  ├ _local-rules.md        ← 專案特有規則
  ├ _cross-references.md   ← 跨專案參照
  ├ _tower-config.yaml     ← 專案設定
  ├ _tower-state.md        ← 塔台記憶
  └ _decision-log.md       ← 決策日誌
```

## 核心原則

### 載入順序

Core (Layer 1) → Global (Layer 2) → Project (Layer 3)

### 覆蓋優先級

Project (Layer 3) > Global (Layer 2) > Core (Layer 1)

### 寫入規則

> 🔴 **本節是「什麼可以／不可以寫進 Layer 1 skill 安裝路徑」的唯一權威定義。**
> Layer 1 skill 安裝路徑（下稱「Layer 1 路徑」）=
> - **手動安裝**（zip）：**`~/.claude/skills/` 與 `~/.codex/skills/`** 兩處
> - **plugin 安裝**（v5.14.0+）：**`~/.claude/plugins/`**（整個目錄，含 `cache/`、`marketplaces/`；有設定 `CLAUDE_CODE_PLUGIN_CACHE_DIR`
>   時，cache 在它指的目錄，該目錄同樣算 Layer 1 路徑）、**`$CODEX_HOME/plugins/`**、**`$CODEX_HOME/.tmp/marketplaces/`**
>   （`CODEX_HOME` 未設定時是 `~/.codex`）
>
> Q1 ~ Q4 對上列每一處**同樣適用**，差異只在各題明列之處（Q2 機制實證與 plugin 機制、Q3 plugin 的安裝方式、Q4 備份落點與 plugin 不備份）。
> CT 全庫其餘各處一律**交叉引用本節**，不得複述判斷條件或範圍。
> 若他處敘述與本節牴觸，以本節為準。

| 層 | 路徑 | 可寫入 | 範圍 |
|----|------|--------|------|
| Layer 1 | `~/.claude/skills/` | ❌ 永遠不可寫入（唯一例外見 Q3） | **整個路徑**，不限於 skill 定義檔 |
| Layer 1 | `~/.codex/skills/` | ❌ 永遠不可寫入（唯一例外見 Q3） | **整個路徑**，不限於 skill 定義檔 |
| Layer 1 | `~/.claude/plugins/`（含 `cache/`、`marketplaces/`）；`CLAUDE_CODE_PLUGIN_CACHE_DIR`（有設定時） | ❌ 永遠不可寫入（唯一例外見 Q3：只能透過 plugin 指令） | **整個路徑**，不限於 skill 定義檔（v5.14.0+） |
| Layer 1 | `$CODEX_HOME/plugins/`、`$CODEX_HOME/.tmp/marketplaces/`（`CODEX_HOME` 預設 `~/.codex`） | ❌ 永遠不可寫入（唯一例外見 Q3：只能透過 plugin 指令） | **整個路徑**，不限於 skill 定義檔（v5.14.0+） |
| Layer 2 | `~/.claude/control-tower-data/` | ✅ 學習萃取、設定修改 | — |
| Layer 3 | `<project>/_ct-workorders/` | ✅ 工單執行、學習記錄 | — |

#### Q1 — 什麼絕對不能寫進 Layer 1 路徑？

**任何不是 skill 定義檔的東西，一律不得寫入 `~/.claude/skills/` 或 `~/.codex/skills/` 之下。無例外。**
plugin 安裝路徑（v5.14.0+，見本節開頭）也一樣，而且更嚴：連 skill 定義檔本身都只能由 plugin 指令寫入（Q3）。

包含但不限於：

- 安裝／升級前的備份目錄（`_backup-*`）
- 暫存檔、工作副本、實驗性副本
- 封存（archive）的舊版 skill
- `.bak` / `.old` / `.orig` 等任何備份後綴的檔案或目錄
- 任何「順手放在旁邊」的附帶目錄

「它不是 skill 定義檔，所以唯讀保護管不到」是**錯的**。
本規則的範圍是**整個 `~/.claude/skills/` 與整個 `~/.codex/skills/` 路徑**（以及本節開頭列的整個 plugin 安裝路徑），不是路徑下的某個檔案類別。

#### Q2 — 為什麼？（機制，不是誡命）

`~/.claude/skills/` **第一層的每一個子目錄都會被 skill 掃描器當成一個 skill 註冊**，
名稱即目錄名。掃描器只看第一層：子目錄根層若有 `SKILL.md`，它就是一個現役 skill。

因此一份根層帶 `SKILL.md` 的備份會**以舊版的 description 進入路由候選**。
備份的 description 與現役版本高度重疊，**路由時可能命中舊版**，
答出已被新版反轉的內容 —— 而且不會有任何錯誤訊息，是靜默答錯。

**實證（D006，2026-09-02）**：T0118 把安裝前備份放到
`~/.claude/skills/_backup-bmad-guide-v6.10.0-20260902-143708/`，
該目錄根層有 `SKILL.md`，隨即被註冊為現役 skill 並出現在可用 skill 清單中，
description 仍是 v6.10.0 那份。

**「上次這樣做沒事」不構成反證。** 同期的 T0115 備份的是 8 個 skill 的**父目錄**，
根層沒有 `SKILL.md`，掃描器只看第一層因而略過 —— 那是**結構僥倖，不是規則有效**。
單一 skill 的備份必然踩到。

**Codex 端（`~/.codex/skills/`）：比照辦理。** 上述實證來自 **Claude Code** 的掃描器（D006）。
Codex 的 skill 掃描器是否同樣「第一層子目錄即註冊」**未經實測**；保守起見**視為相同**，
規則（Q1、Q4）照樣適用。此段不是已證實的事實，在取得 Codex 端實測前不得改寫為「已證實」。

**plugin 安裝路徑（v5.14.0+）：機制不同，結論相同。** plugin 路徑由 plugin manager 管理：安裝、更新、移除時，
cache 裡那個 plugin 版本的目錄由它整份建立或重建（Claude 依 `plugin.json` 的 `version` 判斷新版；Codex 的 git marketplace
每次啟動都會自動升級，依 commit 判斷；T0348）。所以：

- **手改的內容會在下次更新時被蓋掉**，蓋掉之前則和發行版靜默地不一致 —— 和 D006 一樣沒有錯誤訊息
- 放進 cache 或 marketplace 副本的備份、暫存目錄，plugin manager 不認得，可能殘留，也可能在更新時被刪掉
- 要改 CT 的行為，改專案 Layer 3 或全域 Layer 2，不改 plugin 安裝路徑

#### Q3 — 那 skill 定義檔本身呢？

Tower 與 Worker **預設一律禁止寫入** Layer 1 路徑（`~/.claude/skills/`、`~/.codex/skills/`）下的 skill 定義檔。

**唯一例外**：使用者明文授權的安裝／升級。三個條件全部滿足才成立 ——

1. 授權**寫在工單內**（執行範圍或明文授權節）。Worker **不得自行認定**已取得授權
2. 授權指名**具體版本、具體 skill 與目標路徑**（`~/.claude/skills/` 或 `~/.codex/skills/`），
   不是概括性的「可以裝 skill」。只指名其中一處的授權**不及於另一處**
3. 執行時遵循 [version-governance.md](version-governance.md) § 安裝／升級流程
   （備份 → 安裝 → 逐檔複驗 → 回報回退方式）

**plugin 安裝（v5.14.0+）**：同樣需要上面三個條件；條件 2 的「目標路徑」改為指名 **agent（Claude Code 或 Codex）、
plugin 與 marketplace**（例 `ct@control-tower`），只指名其中一個 agent 的授權不及於另一個。條件 3 的流程改為
[version-governance.md](version-governance.md) § plugin 安裝／升級。🔴 即使有授權，也**只能透過 plugin 指令**
（`claude plugin …`、`codex plugin …`）安裝、更新或移除；不得直接在 plugin 安裝路徑下複製、修改或刪除檔案。

與既有規則**不衝突**：

- 「塔台模式不得寫入已安裝的 skill 定義檔」→ **仍然成立**。塔台模式本身沒有這個例外；
  安裝一律另開工單，由 Worker 在工單明文授權下執行
- 「Layer 1 唯讀，由人工升級流程覆寫」→ **仍然成立**。工單內的明文授權**就是**
  人工升級流程中「使用者授權」的那一步，不是繞過它的旁路

例外的範圍僅止於**安裝／升級行為本身**，**不擴及 Q1**：
安裝授權不允許把備份、暫存或任何非 skill 定義檔寫進 Layer 1 路徑。

#### Q4 — 備份要放哪？

| 安裝路徑 | 備份落點 |
|---|---|
| `~/.claude/skills/` | **`~/.claude/skill-backups/`** —— `~/.claude/skills/` 的**同層兄弟目錄**，不在其下 |
| `~/.codex/skills/` | **`~/.codex/skill-backups/`** —— `~/.codex/skills/` 的**同層兄弟目錄**，不在其下 |

命名：`_backup-<skill 或版本標識>-<yyyyMMdd-HHmmss>`

timestamp **必須以系統指令取得**，不得憑印象手打：

```bash
date "+%Y%m%d-%H%M%S"
```

```powershell
Get-Date -Format "yyyyMMdd-HHmmss"
```

🔴 **不得放在 `~/.claude/skills/` 或 `~/.codex/skills/` 之下** —— 包含以底線開頭、以點開頭，
或任何自認為「掃描器應該會略過」的命名。掃描器的行為不是本規則的前提，
路徑位置才是。

**plugin 安裝（v5.14.0+）：不適用。** 不在 plugin 安裝路徑旁做備份；回退方式是用 plugin 指令移除
（`claude plugin uninstall`、`codex plugin remove`）後重裝，或改回 zip 手動安裝。從手動安裝遷移到 plugin 時，
備份的是**手動安裝**那份，落點照上表。

完整的安裝／升級程序見 [version-governance.md](version-governance.md) § 安裝／升級流程。

#### Layer 3 附屬：專案 workflow 腳本（v5.10.0+）

`<project>/.claude/workflows/*.js`（Claude Code Workflow 工具的專案腳本）**不屬於 Layer 1**，也不在上方 Q1～Q4 的範圍內；
它是 Layer 3 的附屬：屬於專案、跟著專案走。Workflow 在 CT 的定位與規則見 [workflow-engine.md](workflow-engine.md)（唯一權威）。

| 項目 | 規則 |
|---|---|
| 版控 | **必須進 git**。CT 隔離 worktree 從 commit 建出，未入版控的腳本在 worktree 裡不存在 |
| 誰寫 | **只由 Worker 依工單 `affects_files` 寫入**。工單沒列該腳本路徑 → 不得寫；塔台模式、`ct-evolve`、`ct-insights` 都不寫 |
| 何時寫 | brief 先經使用者確認（`ct-evolve --workflow` 只產 brief，比照 `--skill`），再另開工單撰寫腳本 |
| 知識卡 | 專案卡在 `_ct-workorders/_workflows/<name>.md`（Layer 3）；全局卡在 Layer 2 `~/.claude/control-tower-data/workflows/`。Layer 2 不存在時只做專案級 |
| 不用的路徑 | 🔴 不使用 `~/.claude/workflows/`（使用者層，不跟著專案、不進專案版控） |
| 跨專案 | **不自動同步**到其他專案；要搬到另一個專案，在該專案開工單 |
| 語法檢查（v5.11.0+） | 寫好或改過腳本後，**不執行 Workflow** 也能做的靜態檢查，見下方 |

**語法檢查做法（v5.11.0+，T0181 表外 4）**：Workflow 腳本有 `export const meta = {...}` 與頂層 `return`，
直接 `node --check` 一定失敗。把腳本轉成暫存檔再檢查，暫存檔放 scratchpad，不進 repo：

1. `export const meta` 改成 `const meta`
2. 其餘整段包進 `async function __wf__() { … }`（頂層的 `await`、`return` 才合法）
3. `node --check <暫存檔>`；exit `0` 才算通過

```bash
{ sed 's/^export const meta/const meta/' .claude/workflows/<name>.js | sed '1s/^/async function __wf__() {\n/'; echo '}'; } > "$SCRATCH/<name>.check.js"
node --check "$SCRATCH/<name>.check.js"
```

這只驗語法，不驗 `agent()`、`args` 等執行期行為；那部分要用不呼叫 Workflow 工具的 mock harness（例：T0182 Step 1b），或交給回測工單。

學習系統與 Playbook 的寫入路徑檢查不涵蓋腳本（腳本寫入不是學習寫入）；
知識卡的路徑檢查見 [workflow-engine.md](workflow-engine.md) § 寫入路徑檢查（知識卡）。

## Layer 2 詳細規格

### 目錄建立

塔台啟動時偵測 `~/.claude/control-tower-data/` 是否存在：

- 存在 → 讀取內容
- 不存在 → 首次使用，提示建立（不強制——Level 0 仍可正常運作）

建立指令（由塔台引導）：

```bash
# Unix/macOS
mkdir -p ~/.claude/control-tower-data/{learnings,playbooks,extensions}

# Windows PowerShell
$base = "$env:USERPROFILE\.claude\control-tower-data"
'learnings','playbooks','extensions' | ForEach-Object { New-Item -ItemType Directory -Path "$base\$_" -Force }
```

### 各檔案格式

#### learnings/patterns.md

```markdown
# 全局決策模式

> 從多個專案萃取的通用模式。由 /ct-evolve 的全局規則評估（Step 6）晉升而來。

## 決策模式

### GP<編號>: <名稱>
- **觸發**：<情境>
- **規則**：<具體做法>
- **來源專案**：<專案1, 專案2, ...>
- **驗證次數**：<跨專案總計>
- **狀態**：🟢/⭐
```

#### learnings/anti-patterns.md

```markdown
# 全局反模式

> 跨專案共通的錯誤做法紀錄。

## 反模式

### GA<編號>: <名稱>
- **描述**：<錯誤做法>
- **正確做法**：<應該怎麼做>
- **來源專案**：<專案1, 專案2, ...>
```

#### playbooks/\<name\>.md

與 Layer 3 的 playbook 格式相同，但標記為 `scope: global`。
晉升來源記錄在 playbook 頂部的 metadata 中。

#### extensions/

使用者自訂的塔台擴展規則。格式自由，塔台啟動時讀取。

用途範例：
- 自訂工單模板
- 團隊特定的品質檢查規則
- 自訂狀態流轉規則
- 額外的 Reference routing 規則

#### project-registry.md

```markdown
# 專案索引

| 專案名稱 | 前綴 | 工單目錄路徑 | 塔台版本 | 最後活動 | 工單數 |
|---------|------|------------|---------|---------|--------|
| my-app  | MA | /path/to/my-app/_ct-workorders/ | v3.3 | 2026-03-31 | 15 |
```

> 前綴欄位對應 `_tower-config.yaml` 的 `project-prefix` 設定。
> 跨專案協調規範見 [cross-project-coordination.md](cross-project-coordination.md)。

#### config.yaml

格式同 Layer 3 的 `_tower-config.yaml`，作用域為全局：

```yaml
control-tower:
  alignment-rounds: 3
  interactive-prompts: on
  experience-level: standard
  verbose: on
  auto-session: ask
```

## 載入合併邏輯

### 設定檔合併（config）

```
1. 載入預設值（[tower-config.md](tower-config.md) § 可用選項的「預設」欄）
2. 載入 Layer 2: ~/.claude/control-tower-data/config.yaml    ← 覆蓋預設
3. 載入 Layer 3: _ct-workorders/_tower-config.yaml           ← 覆蓋 Layer 2
4. Session 即時修改（*config）                                ← 最高優先
```

合併策略：**欄位級覆蓋**（非整檔替換）。Layer 3 只需列出與 Layer 2 不同的設定項。

### 學習紀錄合併（learnings）

```
1. 載入 Layer 2: ~/.claude/control-tower-data/learnings/patterns.md
2. 載入 Layer 3: _ct-workorders/_learnings.md
3. 合併後的模式池用於派發前匹配
```

合併策略：

- **並列合併**：Layer 2 和 Layer 3 的模式同時生效
- **ID 命名空間獨立**：Layer 2 使用 GP/GA/GSEQ 前綴，Layer 3 使用 P/A/SEQ 前綴，不衝突
- **同觸發條件覆蓋**：同一觸發條件下，Layer 3 的模式優先於 Layer 2

### Playbook 合併

```
1. 列出 Layer 2: ~/.claude/control-tower-data/playbooks/*.md
2. 列出 Layer 3: _ct-workorders/_playbooks/*.md
3. 同名 playbook → Layer 3 優先
```

## 晉升流程（Layer 3 → Layer 2）

當 /ct-evolve 偵測到模式置信度達 ⭐（3+ 專案驗證 + 使用者認可）：

1. 提議晉升：「此模式已在 3 個專案驗證通過，要晉升為全局模式嗎？」
2. 使用者確認後：
   - 複製到 Layer 2 對應檔案（`patterns.md` / `anti-patterns.md` / `playbooks/`）
   - 編號改為 GP/GA/GSEQ 前綴
   - 記錄來源專案列表
3. Layer 3 原始記錄保留（不刪除）

## 降級行為

| 情境 | 行為 |
|------|------|
| Layer 2 目錄不存在 | 靜默降級，等同 v3.2 行為（僅 Layer 1 + Layer 3） |
| Layer 2 部分檔案缺失 | 跳過缺失檔案，不報錯 |
| Layer 2 檔案格式錯誤 | 警告使用者，該檔使用預設值 |

## 遷移指南（v3.2 → v3.3）

### 全局設定遷移

| 項目 | 舊路徑 | 新路徑 |
|------|--------|--------|
| 全局設定 | `~/.claude/control-tower-config.yaml` | `~/.claude/control-tower-data/config.yaml` |
| 全局模式 | `~/.claude/ct-global-patterns/` | `~/.claude/control-tower-data/learnings/` |

遷移步驟：

1. 建立 Layer 2 目錄結構（見上方建立指令）
2. 移動全局設定：
   ```bash
   mv ~/.claude/control-tower-config.yaml ~/.claude/control-tower-data/config.yaml
   ```
3. 若有全局模式，合併到 `learnings/patterns.md`
4. 確認後刪除舊目錄

### 相容性

過渡期塔台**同時相容新舊路徑**：

```
設定檔讀取順序：
1. ~/.claude/control-tower-data/config.yaml  ← 新路徑（優先）
2. ~/.claude/control-tower-config.yaml       ← 舊路徑（降級相容）
3. 預設值
```

當偵測到舊路徑仍存在時，提示使用者遷移。
