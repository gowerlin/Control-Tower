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
  ${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}/、$CODEX_HOME/plugins/ …  ← plugin 安裝位置（v6.0.0-beta.5+；完整清單見 § 寫入規則）

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
  ├ _insights/             ← 統計快照（v6.0.0-beta.10+；session-stats/<YYYY-MM>.json，見下方 § `_ct-workorders/_insights/`）
  ├ _local-rules.md        ← 專案特有規則
  ├ _cross-references.md   ← 跨專案參照
  ├ _tower-config.yaml     ← 專案設定
  ├ _tower-state.md        ← 塔台記憶
  └ _decision-log.md       ← 決策日誌
```

### 路徑解析（P-3，T0314）

本節是 CT 全域路徑的**唯一權威定義**；CT 各檔寫的 `~/.claude/…`、`~/.codex/…` 一律照下表解讀，不另寫死家目錄：

| 文件寫法 | 實際位置 | 說明 |
|---|---|---|
| `~/.claude/…`（含 Layer 2 `~/.claude/control-tower-data/`、Layer 1 `~/.claude/skills/`） | `${CLAUDE_CONFIG_DIR:-~/.claude}/…` | 設了 `CLAUDE_CONFIG_DIR`（例：隔離試用、多設定目錄）就在它底下 |
| `~/.codex/…`（Layer 1 Codex 端 `~/.codex/skills/`） | `${CODEX_HOME:-~/.codex}/…` | 設了 `CODEX_HOME` 就在它底下 |
| `~/.claude/plugins/`（Layer 1 plugin 安裝路徑，v6.0.0-beta.5+） | `${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}/`，**只有這一處** | `installed_plugins.json`、`known_marketplaces.json`、`cache/`、`marketplaces/` 都在這一處：設了 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 就是它指的目錄，只設 `CLAUDE_CONFIG_DIR` 就是 `${CLAUDE_CONFIG_DIR}/plugins/`，都沒設是 `~/.claude/plugins/`（T0357、T0374 實測）。設了其中任一個時，`~/.claude/plugins/` 屬於另一份設定，不是本 session 載入的 plugin（v6.0.0-beta.8 起改成單一路徑；之前兩處都算） |

- 塔台讀全域設定、偵測 adapter（`adapters/*.yaml` 的 `detection.probes[].search`）都照這張表；只讀這兩個變數的**有無與路徑**，不列出整組環境變數（[auto-session.md](auto-session.md) § BAT 內部終端路由 › 偵測條件）。
- 變數沒設 → 與 v5.12.6 相同（`~/.claude`、`~/.codex`）。
- Codex 端的 CT Layer 2 仍在 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/`（CT 資料層不分 runtime）。

## 核心原則

### 載入順序

Core (Layer 1) → Global (Layer 2) → Project (Layer 3)

### 覆蓋優先級

Project (Layer 3) > Global (Layer 2) > Core (Layer 1)

### 寫入規則

> 🔴 **本節是「什麼可以／不可以寫進 Layer 1 skill 安裝路徑」的唯一權威定義。**
> Layer 1 skill 安裝路徑（下稱「Layer 1 路徑」）=
> - **手動安裝**（zip）：**`~/.claude/skills/` 與 `~/.codex/skills/`** 兩處
> - **plugin 安裝**（v6.0.0-beta.5+）：**`${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}/`**（整個目錄，含 `installed_plugins.json`、`known_marketplaces.json`、
>   `cache/`、`marketplaces/`；只有這一處：設了 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 就是它指的目錄，只設 `CLAUDE_CONFIG_DIR` 就是
>   `${CLAUDE_CONFIG_DIR}/plugins/`，都沒設是 `~/.claude/plugins/`，見 § 路徑解析；v6.0.0-beta.8 改寫，T0357、T0374 實測）、**`$CODEX_HOME/plugins/`**、**`$CODEX_HOME/.tmp/marketplaces/`**
>   （`CODEX_HOME` 未設定時是 `~/.codex`）。預發行版（beta、rc）不上架 plugin（[version-governance.md](version-governance.md) § plugin 安裝／升級），
>   但同一台機器可能裝了穩定版的 plugin，本規則照樣適用
>
> Q1 ~ Q4 對上列每一處**同樣適用**，差異只在各題明列之處（Q2 機制實證與 plugin 機制、Q3 plugin 的安裝方式、Q4 備份落點與 plugin 不備份）。
> CT 全庫其餘各處一律**交叉引用本節**，不得複述判斷條件或範圍。
> 若他處敘述與本節牴觸，以本節為準。

| 層 | 路徑 | 可寫入 | 範圍 |
|----|------|--------|------|
| Layer 1 | `~/.claude/skills/` | ❌ 永遠不可寫入（唯一例外見 Q3：授權下的安裝／升級、使用者逐項決定的移除） | **整個路徑**，不限於 skill 定義檔 |
| Layer 1 | `~/.codex/skills/` | ❌ 永遠不可寫入（唯一例外見 Q3：授權下的安裝／升級、使用者逐項決定的移除） | **整個路徑**，不限於 skill 定義檔 |
| Layer 1 | `${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}/`（含 `cache/`、`marketplaces/`；見 § 路徑解析） | ❌ 永遠不可寫入（唯一例外見 Q3：只能透過 plugin 指令） | **整個路徑**，不限於 skill 定義檔（v6.0.0-beta.5+） |
| Layer 1 | `$CODEX_HOME/plugins/`、`$CODEX_HOME/.tmp/marketplaces/`（`CODEX_HOME` 預設 `~/.codex`） | ❌ 永遠不可寫入（唯一例外見 Q3：只能透過 plugin 指令） | **整個路徑**，不限於 skill 定義檔（v6.0.0-beta.5+） |
| Layer 2 | `~/.claude/control-tower-data/` | ✅ 學習萃取、設定修改 | — |
| Layer 3 | `<project>/_ct-workorders/` | ✅ 工單執行、學習記錄 | — |

#### Q1 — 什麼絕對不能寫進 Layer 1 路徑？

**任何不是 skill 定義檔的東西，一律不得寫入 `~/.claude/skills/` 或 `~/.codex/skills/` 之下。無例外。**
plugin 安裝路徑（v6.0.0-beta.5+，見本節開頭）也一樣，而且更嚴：連 skill 定義檔本身都只能由 plugin 指令寫入（Q3）。

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

**Codex 端（`~/.codex/skills/`）：已證實，而且比 Claude Code 更嚴（v6.0.0-beta.10+）。** Codex 的 skill 掃描器
**會往下遞迴**，不只看第一層：任何深度的子目錄只要有 `SKILL.md` 就會被註冊，目錄名以底線開頭也一樣。
所以 Claude Code 端靠結構僥倖逃過的情況，在 Codex 端逃不過 —— 像 T0115 那樣把備份放成**父目錄**、根層沒有 `SKILL.md`，
Codex 照樣會往下找到裡面每個 skill 的 `SKILL.md` 並註冊。

**實證（Codex 0.166.0，2026-11-01，T0389 R3）**：用暫存的 `CODEX_HOME`（不碰真實設定），以 `codex debug prompt-input`
列出模型會看到的 skill 清單（不呼叫模型）。`CODEX_HOME/skills/_backup-zz-root/SKILL.md`（第一層、底線開頭）與
`CODEX_HOME/skills/_backup-zz-nested/zz-inner/SKILL.md`（第二層）**兩個都被註冊**。

結論：Codex 端的備份一律放在 `~/.codex/skills/` 以外（落點見 Q4：`~/.codex/skill-backups/`），**不得放在 `~/.codex/skills/`
之下任何深度**；Claude Code 端同樣一律放 `~/.claude/skill-backups/`。Q1、Q4 的規則兩端照樣適用。

**plugin 安裝路徑（v6.0.0-beta.5+）：機制不同，結論相同。** plugin 路徑由 plugin manager 管理：安裝、更新、移除時，
cache 裡那個 plugin 版本的目錄由它整份建立或重建（Claude 依 `plugin.json` 的 `version` 判斷新版；Codex 的 git marketplace
每次啟動都會自動升級，依 commit 判斷；T0348）。所以：

- **手改的內容會在下次更新時被蓋掉**，蓋掉之前則和發行版靜默地不一致 —— 和 D006 一樣沒有錯誤訊息
- 放進 cache 或 marketplace 副本的備份、暫存目錄，plugin manager 不認得，可能殘留，也可能在更新時被刪掉
- 要改 CT 的行為，改專案 Layer 3 或全域 Layer 2，不改 plugin 安裝路徑

#### Q3 — 那 skill 定義檔本身呢？

Tower 與 Worker **預設一律禁止寫入** Layer 1 路徑（`~/.claude/skills/`、`~/.codex/skills/`）下的 skill 定義檔。

**唯一例外**：使用者明文授權的安裝／升級，以及使用者逐項決定的手動安裝 skill 移除（v6.0.0-beta.10+，見下方〈手動安裝 skill 的移除〉）。
安裝／升級要三個條件全部滿足才成立 ——

1. 授權**寫在工單內**（執行範圍或明文授權節）。Worker **不得自行認定**已取得授權
2. 授權指名**具體版本、具體 skill 與目標路徑**（`~/.claude/skills/` 或 `~/.codex/skills/`），
   不是概括性的「可以裝 skill」。只指名其中一處的授權**不及於另一處**
3. 執行時遵循 [version-governance.md](version-governance.md) § 安裝／升級流程
   （備份 → 安裝 → 逐檔複驗 → 回報回退方式）

**手動安裝 skill 的移除（v6.0.0-beta.10+）：出建議 → 使用者逐項決定 → 依決定自動執行。** 適用 `~/.claude/skills/`、`~/.codex/skills/`
下手動安裝的 skill；授權的形式和安裝不同，由使用者逐項的決定構成：

1. **出建議**：要移除手動安裝的 skill 時，塔台（或依工單執行的 Worker）先產出**建議清單**，每一項列：agent（Claude Code／Codex）、
   skill 名稱、路徑、目前版本、建議處置與理由。處置三選一，**預設建議 `移出`**：
   - `移出`：把整個 skill 目錄搬到備份落點下的 `_removed-<skill>-<版號>-<yyyyMMdd-HHmmss>/`（Claude Code 是 `~/.claude/skill-backups/`，
     Codex 是 `~/.codex/skill-backups/`，落點同 Q4；時間戳以系統指令取得）
   - `刪除`：直接刪除，不可復原
   - `保留`：不動
2. **使用者逐項決定**：清單交給使用者，**每一項分別**選處置；使用者沒回答的項目**一律不動**。使用者逐項的決定寫進工單，
   就是那一項的執行授權 —— 不需要另外的明文授權句，但只及於清單上、使用者選過的那幾項，以及清單上寫的那個 agent 的路徑
   （例 Claude Code 那一項的決定不及於 Codex 端的同名 skill）。
3. **依決定自動執行**：Worker 照使用者逐項的決定執行，不再逐項確認，執行結果逐項寫進工單回報區：
   - `移出` → 整個目錄搬走（移動，不是複製），搬完確認**原路徑已不存在**、該 agent 的 skill 清單**不再註冊**這個 skill，
     並寫明搬到哪裡（回退方式就是搬回原路徑）
   - `刪除` → 直接刪除；🔴 只在使用者選了 `刪除` 的項目上做
   - `保留` → 不動
4. **yolo**：Worker 不直接問使用者，清單照 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 交給塔台；塔台**不代決任何一項**
   （刪除不可逆，一律升級給使用者；`移出`、`保留` 也是使用者逐項決定的範圍），轉給使用者後把逐項的決定答回。
5. plugin 的移除不在此列：照下方〈plugin 安裝〉，仍只能用 plugin 指令。

| 動作 | 手動安裝（`~/.claude/skills/`、`~/.codex/skills/`） | plugin 安裝 |
|---|---|---|
| 安裝／升級 | Worker，工單授權指名版本、skill、路徑；照 § 安裝／升級流程 | Worker，工單授權指名 agent、plugin、marketplace；只能用 plugin 指令 |
| 移除 | 塔台或 Worker 出建議清單（預設 `移出`）→ 使用者逐項選 `移出`／`刪除`／`保留`（沒回答的不動）→ Worker 依決定執行（v6.0.0-beta.10+） | Worker，工單授權指名 agent、plugin、marketplace；只能用 plugin 指令（`claude plugin uninstall`、`codex plugin remove`） |

**plugin 安裝（v6.0.0-beta.5+）**：同樣需要上面三個條件；條件 2 的「目標路徑」改為指名 **agent（Claude Code 或 Codex）、
plugin 與 marketplace**（例 `ct@control-tower`），只指名其中一個 agent 的授權不及於另一個。條件 3 的流程改為
[version-governance.md](version-governance.md) § plugin 安裝／升級。🔴 即使有授權，也**只能透過 plugin 指令**
（`claude plugin …`、`codex plugin …`）安裝、更新或移除；不得直接在 plugin 安裝路徑下複製、修改或刪除檔案。

與既有規則**不衝突**：

- 「塔台模式不得寫入已安裝的 skill 定義檔」→ **仍然成立**。塔台模式本身沒有這個例外；
  安裝一律另開工單，由 Worker 在工單明文授權下執行
- 「Layer 1 唯讀，由人工升級流程覆寫」→ **仍然成立**。工單內的明文授權**就是**
  人工升級流程中「使用者授權」的那一步，不是繞過它的旁路

例外的範圍僅止於**安裝／升級與移除行為本身**，**不擴及 Q1**：
安裝授權或使用者的移除決定，都不允許把備份、暫存或任何非 skill 定義檔寫進 Layer 1 路徑。

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

**plugin 安裝（v6.0.0-beta.5+）：不適用。** 不在 plugin 安裝路徑旁做備份；回退方式是用 plugin 指令移除
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

#### `_ct-workorders/_insights/`（v6.0.0-beta.10+）

ct-insights 統計的專案級產出，屬於 **Layer 3**：跟著專案、進版控、只有數字。目前只有一種內容：

| 項目 | 規則 |
|---|---|
| 內容 | `session-stats/<YYYY-MM>.json`：session 用量快照（`ct-session-stats-snapshot/0.2`，v6.0.0-beta.12+；`0.1` 的舊檔照常讀）；格式、併入規則與隱私自檢的唯一權威是 `ct-insights/references/analysis-rules.md` § Session 用量統計 › 快照 |
| 誰寫 | **只由塔台**：收單時（[work-order-system.md](work-order-system.md) § 收單快照）與 `*insights sessions` 補寫；都經 `ct-insights/scripts/ct-session-stats.py --snapshot-append` 寫，不手動編輯。Worker、`ct-evolve` 不寫；寫實作或規格的工單也不建實際資料檔 |
| 誰讀 | `*insights sessions`、`ct-session-stats.py --facts-from`（候選事實，給 ct-evolve；接法見 ⑦） |
| 掃描 | 🔴 `*sync`、`*archive` **不掃描**這個目錄（不是單據，沒有狀態）；BAT 塔台面板也不讀（[memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 › 各檔要求） |
| 不放的東西 | 對話內容、指令原文、完整路徑、權杖、真實 session 紀錄檔（`.jsonl`） |
| 不用的路徑 | 不放 `~/.claude/**`（不跟著專案；原始紀錄本來就在那裡、會被清掉） |

## Layer 2 詳細規格

### 目錄建立

塔台啟動時偵測 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/` 是否存在（§ 路徑解析）：

- 存在 → 讀取內容
- 不存在 → 首次使用，提示建立（不強制——Level 0 仍可正常運作）

建立指令（由塔台引導）：

```bash
# Unix/macOS
mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/control-tower-data/"{learnings,playbooks,extensions}

# Windows PowerShell
$cfg = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { "$env:USERPROFILE\.claude" }
$base = "$cfg\control-tower-data"
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
