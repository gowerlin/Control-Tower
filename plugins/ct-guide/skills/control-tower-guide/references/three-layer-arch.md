# 三層架構設計原理

## 為什麼需要三層分離？

早期的塔台把學習紀錄直接寫進 skill 原始檔。這導致一個問題：**升級 skill 時會覆蓋學習紀錄**。

三層資料架構把「隨版本更替的程式」與「隨使用累積的資料」拆開，徹底解決這個衝突：

```
Layer 1: Core（唯讀，升級時整份覆蓋）
  ~/.claude/skills/            ← 整個路徑都受保護，不只 control-tower 一個目錄
  ├ control-tower/
  ├ ct-exec/  ct-done/  ct-status/
  ├ ct-evolve/  ct-help/  ct-insights/  ct-fieldguide/
  └ （Codex 端對應 ~/.codex/skills/）
  ~/.claude/plugins/、$CODEX_HOME/plugins/ …  ← plugin 安裝位置（v5.14.0+），同樣是 Layer 1

Layer 2: Global（使用者級，跨專案，升級不碰）
  ~/.claude/control-tower-data/
  ├ config.yaml            ← 全局設定
  ├ learnings/             ← 跨專案通用模式（patterns.md）& 反模式（anti-patterns.md）
  ├ playbooks/             ← 全局 playbook（從專案晉升）
  ├ workflows/             ← 全局 workflow 知識卡（v5.10.0+）
  ├ extensions/            ← 使用者自訂擴展規則
  └ project-registry.md    ← 跨專案索引

Layer 3: Project（專案級，每個專案各一份）
  <project-root>/_ct-workorders/
  ├ T####-*.md / BUG-* / PLAN-* / EXP-*   ← 熱區單據
  ├ _tower-config.yaml     ← 專案設定
  ├ _tower-state.md        ← 塔台跨 session 狀態
  ├ _learnings.md          ← 專案級學習
  ├ _playbooks/            ← 專案級 playbook
  ├ _workflows/            ← 專案級 workflow 知識卡（v5.10.0+）
  ├ _local-rules.md        ← 專案級規則
  ├ _cross-references.md   ← 跨專案參照
  ├ _decision-log.md       ← 決策日誌
  ├ _bug-tracker.md        ← BUG 索引（*sync 自動重建）
  ├ _backlog.md            ← PLAN 索引（*sync 自動重建）
  └ _archive/              ← 冷區
     ├ workorders/  bugs/  plans/
```

## 三層的角色

| 層級 | 生命週期 | 寫入者 | 升級影響 |
|------|---------|--------|---------|
| **Layer 1 Core** | 隨 skill 版本 | **無人可在日常運作中寫入**；唯一例外是工單明文授權的安裝／升級 | 會被覆蓋 |
| **Layer 2 Global** | 跨專案永久 | 塔台／`ct-evolve`（學習萃取、設定修改） | 不受影響 |
| **Layer 3 Project** | 專案級永久 | 塔台／Worker（工單執行、學習紀錄） | 不受影響 |

## Layer 1 寫入規則

Layer 1 的規則只有一句話：**Layer 1 安裝路徑（zip 手動安裝的 `~/.claude/skills/` 與 `~/.codex/skills/`，以及 v5.14.0 起 plugin 安裝的目錄）底下，除了被明文授權安裝的 skill 定義檔，什麼都不准寫。**

### plugin 安裝路徑也是 Layer 1（v5.14.0）

v5.14.0 起 CT 也能用 plugin 安裝（見 `governance.md` § plugin marketplace：另一種安裝方式），skill 就不在 `skills/` 底下，而在 plugin 目錄：

| Agent | plugin 安裝路徑 |
|---|---|
| Claude Code | `~/.claude/plugins/`（含 `cache/`、`marketplaces/`；設了 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 時，cache 在它指的目錄） |
| Codex | `$CODEX_HOME/plugins/`、`$CODEX_HOME/.tmp/marketplaces/`（`CODEX_HOME` 預設 `~/.codex`） |

這些路徑和 `skills/` 一樣受保護，而且更嚴：連 skill 定義檔本身都只能由 plugin 指令寫入。plugin 目錄由 plugin manager 管理，
手改的檔案在下一次更新就被蓋掉，而且沒有人會知道它曾經被改過。完整路徑清單以 CT `data-layer-architecture.md` § 寫入規則為準。

### 範圍是「整個路徑」，不是「skill 定義檔」

不只是不能改 `SKILL.md`。安裝前的備份目錄、暫存檔、工作副本、封存的舊版、`.bak`／`.old` 檔、
任何「順手放在旁邊」的目錄——全部不得出現在 Layer 1 安裝路徑之下。
「它不是 skill 定義檔，所以唯讀保護管不到」是錯的想法。

### 為什麼範圍這麼大：掃描器的機制

這不是誡命，是機制推出來的結論：

> **`~/.claude/skills/` 第一層的每一個子目錄，都會被 skill 掃描器註冊成一個 skill。**
> 子目錄根層有 `SKILL.md`，它就是一個現役 skill。

所以一份放在旁邊的備份，會帶著**舊版的 description** 進入路由候選。
舊 description 與現役版本高度重疊，路由時可能命中舊版，答出已被新版推翻的內容——而且沒有任何錯誤訊息，是靜默答錯。

以上是 Claude Code 掃描器的機制。Codex 端（`~/.codex/skills/`）比照辦理；Codex 掃描器是否同樣第一層即註冊**未經實測**，CT 保守視為相同。

### 唯一例外與備份落點

- **唯一例外**：使用者在**工單內**明文授權、指名具體版本、具體 skill **與目標路徑**的安裝／升級；只指名其中一處的授權不及於另一處。塔台模式本身沒有這個例外，安裝一律另開工單由 Worker 執行；Worker 也不得自行認定已取得授權
- **例外不擴及備份**：即使有安裝授權，備份也不能放進 `~/.claude/skills/` 或 `~/.codex/skills/`
- **備份落點**（皆為對應 `skills/` 的**同層兄弟目錄**，不在其下）：
  - `~/.claude/skills/` → `~/.claude/skill-backups/`
  - `~/.codex/skills/` → `~/.codex/skill-backups/`
- **plugin 安裝不備份**（v5.14.0）：回退方式是用 plugin 指令移除，再把 zip 手動安裝裝回來

這條規則在 CT 中只有一處權威定義（`data-layer-architecture.md` § 寫入規則），其他文件一律交叉引用。
規則的實證案例（一份備份被註冊成現役 skill）、安裝流程（備份 → 安裝 → 逐檔複驗 → 回報回退方式），以及「為什麼要單一權威定義」，詳見 `governance.md`。

## 合併規則

啟動時依序載入 Core → Global → Project，合併策略如下：

| 類型 | 策略 | 說明 |
|------|------|------|
| **設定值** | 覆蓋：Project > Global > 預設值 | 欄位級合併（非整檔替換），Project 只需列出與 Global 不同的項目 |
| **擴展規則** | 附加：不覆蓋 | Global `extensions/` + Project `_local-rules.md` 同時生效 |
| **學習紀錄** | 並列合併，同觸發條件 Project 優先 | ID 命名空間分開：Global 用 `GP`／`GA`／`GSEQ`，Project 用 `P`／`A`／`SEQ` |
| **Playbook** | 同名覆蓋：Project 優先 | 不同名的 Global 和 Project 同時生效 |

## 設定的四層覆蓋

設定值有四個來源，優先級由高到低：

1. **Session**：`*config` 即時修改，session 結束即消失
2. **Project**：`_ct-workorders/_tower-config.yaml`
3. **Global**：`~/.claude/control-tower-data/config.yaml`
4. **Default**：CT 內建預設值

這四層只服務**塔台**。Worker 不讀設定檔來決定 runtime 模式——模式由塔台派工時傳入（見 `concepts.md` § Worker 無狀態）。

## 學習紀錄的分流

`*evolve` 萃取學習時沿兩條軸分流：

**寫到哪一層**——

```
[A] 通用（全部專案）→ 寫入 Layer 2
[B] 本專案 → 寫入 Layer 3
[C] 不確定 → 寫入 Layer 3，待累積驗證後再晉升
```

**屬於哪一類**——

| 類別 | 內容 | 跨技術棧 |
|------|------|---------|
| **Tactical** | 工具、語言、shell、框架或 repo 特定的操作經驗 | 換技術棧就失效 |
| **Strategic** | 技術更替後仍成立的決策模式 | 跨技術棧有效 |
| **Episodic** | 尚未能泛化的原始事件 | — |

不確定時，預設歸 Tactical 或 Episodic，不誇大通用性。拆開兩類的理由：高價值的 strategic insight 不該被大量 tactical 小技巧淹沒。

**晉升到 Layer 2**：模式在 3 個以上專案驗證、經使用者認可後，`ct-evolve` 提議晉升；確認後複製到 Layer 2、改用 `GP`／`GA`／`GSEQ` 編號並記錄來源專案，Layer 3 原始紀錄保留。

## Layer 2 的建立

塔台啟動時偵測 `~/.claude/control-tower-data/` 是否存在：

- 存在 → 讀取內容
- 不存在 → **提示建立，不強制**——沒有 Layer 2 時塔台照常運作（僅 Layer 1 + Layer 3）

## 設計哲學

- **Core 唯讀**：確保升級安全，skill 定義不被運行時修改；範圍涵蓋整個 skills 路徑，因為掃描器看的是路徑
- **Global 跨專案**：通用知識只學一次，所有專案共享
- **Project 隔離**：專案特有的學習不污染其他專案
- **靜默降級**：Layer 2 目錄或部分檔案不存在時跳過、不報錯；檔案格式錯誤才警告

## 三層與 Memory Hierarchy 同構

CT 有兩種「三層」，看的是不同的軸，不要混為一談：

| 視角 | 三層 | 分層依據 |
|------|------|---------|
| **資料歸屬**（本檔上半部） | Core／Global／Project | 誰擁有、生命週期多長、升級時會不會被覆蓋 |
| **知識存取**（`concepts.md` 第一原則的延伸） | 工單／learnings／FIELDGUIDE | 容量 × 讀取成本，對應 cache hierarchy |

知識存取的三層：

| 層級 | 實體 | 類比 | 特性 |
|------|------|------|------|
| L3 | `_ct-workorders/` 工單 | 硬碟 | 容量大、全量保存、讀取成本高 |
| L2 | `_learnings.md`（蒸餾後） | L2 cache | 中等容量、去蕪存菁，供塔台查閱 |
| L1 | FIELDGUIDE（`ct-fieldguide` 管理） | L1 cache／熱區 | 容量小、高頻命中 |

```
L3 工單事件 ─ *evolve 蒸餾 ─▶ L2 learnings ─ 晉升 ─▶ L1 FIELDGUIDE
```

**為什麼不能只有一層？** 只留工單：塔台每次都得掃全部工單才能回答「最近解過什麼類似問題」，context 被原始事件塞爆。
只留 FIELDGUIDE：容量太小，被問到「當初為什麼這樣決定」時找不到原始證據。

這也是塔台**不直接看 git log** 的理由：git log 是低粒度、沒有因果萃取的事件時間軸，拿它代替 `_tower-state.md` 等於放棄快取、只讀硬碟。

## Layer 3 元件

### 塔台私有狀態檔

以下檔案屬於**塔台私有狀態**，Worker 只有在工單明文授權時才能編輯：

```
_tower-state.md  _decision-log.md  _learnings.md  _tower-config.yaml
_bug-tracker.md  _backlog.md  _cross-references.md
```

理由：這些檔案是塔台的「記憶」。Worker 若可以隨手改，塔台下次啟動讀到的就不再是自己的決策紀錄。

### `_playbooks/` 目錄

知識成熟度管線的 L2 產出。每個 playbook 是一個獨立 `.md` 檔，記錄標準化操作程序：

```
_playbooks/
├── feature-story-standard.md
├── research-workorder-pattern.md
└── bug-fix-standard.md
```

由 `*evolve --playbook` 從已驗證的觀察提煉。Global 層的 `playbooks/` 存放跨專案通用的程序。

### `_workflows/` 與專案 workflow 腳本（v5.10.0+）

`_workflows/` 放 Workflow **知識卡**：`ct-evolve --workflow` 產出的 brief、成熟度、驗證歷史與降級紀錄。卡片不是腳本。

真正的腳本是 `<project>/.claude/workflows/*.js`（Claude Code Workflow 工具的專案腳本），它落在哪一層？
它**不是 Layer 1**——不在 skill 安裝路徑，也不跟著 CT 升級——而是 **Layer 3 的附屬**：屬於專案、跟著專案走。規則有四條：

- **必須進 git**：CT 的隔離 worktree 從 commit 建出，沒進版控的腳本在 worktree 裡根本不存在
- **只由 Worker 依工單 `affects_files` 寫入**：塔台、`ct-evolve`、`ct-insights` 都不寫；工單沒列這個路徑就不得寫
- **brief 先經使用者確認**：`--workflow` 只產 brief，腳本另開工單
- **不用 `~/.claude/workflows/`、不自動同步到其他專案**：使用者層的腳本不跟著專案走，也進不了專案版控；要搬到另一個專案就在那邊開工單

寫好腳本後，不執行 Workflow 也能做語法檢查（v5.11.0）：腳本有 `export const meta` 與頂層 `return`，直接 `node --check` 一定失敗；先把 `export const meta` 改成 `const meta`、整段包進一個 async function，存成 scratchpad 暫存檔再 `node --check`。這只驗語法，執行期行為要靠不呼叫 Workflow 的 mock 或回測工單。

另外別把 CT 自己的腳本和專案腳本搞混：v5.11.0 起 `ct-insights` skill 裡附了一支預篩腳本（`scripts/ct-workflow-prefilter.py`），它是 Layer 1 的一部分、隨 CT 安裝與升級，和專案的 `.claude/workflows/*.js` 無關。

權威見 CT `data-layer-architecture.md` § 寫入規則 › Layer 3 附屬：專案 workflow 腳本。

### `_decision-log.md`

獨立的決策日誌，讓重要決策有完整紀錄，不散落在 `_learnings.md` 或工單裡。使用 `D###` 編號：

```markdown
# Decision Log

## 索引
| ID | 日期 | 決策 | 相關工單 |
|----|------|------|---------|
| D002 | 2026-04-03 | API 改用 REST 而非 GraphQL | T0012 |
| D001 | 2026-04-01 | 選擇 React 而非 Vue | T0005 |

---

## 詳細紀錄（倒序）

### D002 2026-04-03 — API 改用 REST 而非 GraphQL
- **背景**：⋯⋯
- **選項**：[A] ⋯⋯ [B] ⋯⋯
- **決定**：⋯⋯
```

**倒序**（最新在最前）且 **append-only**：塔台不刪除、不修改已有紀錄。每筆必填背景、至少兩個選項、決定與理由、影響、相關工單；
`*sync` 會驗證索引表與詳細紀錄的筆數一致。塔台不主動建立此檔，偵測到不存在時只提示可建立。

**格式為什麼要嚴格（v5.13.0）**：BAT 指揮塔的「決策」頁直接解析這個檔，所以索引表頭是 `ID`、每列以 `|` 開頭與結尾、格子裡不放 `|`、
詳細紀錄標題固定 `### D### YYYY-MM-DD — 標題`。這些寫法對人來說差不多，對解析器卻是讀得到與讀不到的差別——
少一個列尾 `|`，表格就在那一列結束，後面的決策全部看不到。`*sync` 的格式驗證會指出這類問題（見 `bat-integration.md` § BAT 塔台面板讀取契約）。

**收斂（v5.13.0）**：append-only 的檔只會變大。超過 400 KB 預算時塔台只提示、不自動動手，由使用者決定時機，
把最舊的一段詳細紀錄**原文**搬到 `_archive/decisions/_decision-log-D###-D###.md`（不摘要、不改字）。兩個設計重點：

- **索引表不搬**：熱檔的索引表仍涵蓋全部決策，BAT 的決策清單才完整；搬走的只是詳情
- **🔴 危害規則逐字留在熱檔**：會造成資料遺失、誤刪、外洩、誤送的操作與對應禁令，塔台每次啟動都得讀到，所以不搬；拿不準就留

這和 append-only 不衝突：紀錄沒有被刪除或改寫，只是換了存放位置，索引仍指得到它。
格式與步驟以 CT `decision-log-system.md` § 格式規則、§ 收斂 為準。

### `_archive/` 冷區

位於 `_ct-workorders/_archive/`，由 `*archive` 管理，首次歸檔時自動建立三個子目錄（EXP 與工單共用 `workorders/`）。
`*sync` 嚴格跳過冷區；需要時再搜尋或取回。歸檔資格見 `concepts.md` § 熱區／冷區分離。

### `_bug-tracker.md` 和 `_backlog.md`

這兩個是**生成的索引**，由 `*sync` 掃描 BUG／PLAN 單據後整檔重建，**不應手動編輯**：

- `_bug-tracker.md`：依狀態分區的 BUG 索引
- `_backlog.md`：PLAN 索引

v5 起它們帶有 `schema_kind: index` 的 frontmatter，表明自己是生成物——因此可以整檔重寫；
反過來，人類維護的 BUG／PLAN 單據本身，就算 metadata drift 也不會被自動覆寫。

v5.13.0 起兩個索引的格式有唯一權威（CT `bug-plan-system.md` § 索引格式），其中兩件事最常被問：

- **嚴重度／優先級寫 `🔴 High`，不只寫 `🔴`**：BAT 只認含 `High`／`Medium`／`Low` 的字串，只寫 emoji 的格子會被當成 Unknown，
  按等級篩選時就漏掉。單據本身的 frontmatter 照舊可以寫 `critical`，索引格子寫成 `🔴 High（critical）`（BAT `>= 0.7.1-pre.9` 讀到只寫 `critical` 也算 High，但更舊的 BAT 是 Unknown，所以格子照舊這樣寫，新舊 BAT 都讀得對）
- **改了 BUG／PLAN 狀態，同一批就重建索引**：BAT 看板讀的是索引而不是個別單據。不重建，單據已經結了、看板卻還掛著，看起來像沒做

### Tower State（`_tower-state.md`）

塔台跨 session 的決策狀態摘要，設計目標是**塔台啟動瞬間就能掃完**。標準區段：

```markdown
## 🌅 起手式（Quick Recovery）   ← 立即待辦 + 近期完成 + 快速連結
## 📦 基本資訊                    ← 專案名稱 + 里程碑 + 塔台版本
## 🔢 編號追蹤                    ← 各類單據的下一個編號（EXP 依 TOPIC 分開計數）
## 📊 進度快照                    ← 當前 sprint／milestone 狀態
## 📝 本 Session 決策日誌         ← 精簡版決策紀錄（完整版在 _decision-log.md）
## ⏳ 待處理事項                  ← 未結事項
## 🔍 環境快照                    ← 啟動 Fast Path 用的環境偵測結果
## YOLO 歷程                      ← 僅在 auto-session 曾設為 yolo 時存在
```

**啟動兩條路徑**：`_tower-state.md` 存在且環境快照新鮮 → **Fast Path**，直接恢復；
檔案不存在、環境快照為空或超過 7 天、或使用者執行 `*rescan` → **Full Scan** 重建環境快照。

**首次建立**：新專案首次啟動塔台時，以標準模板建立。
**恢復驗證**：重啟時檢查各必要區段，缺少的提示補齊。YOLO 歷程在非 YOLO 模式下不存在，不算缺失。
**更新時機**：處理工單回報後、做出決策後、派發緊急工單後、使用者說「存檔」時、session 即將結束時。

**機器可讀摘要（v5.13.0）**：`_tower-state.md` 開頭多一段 YAML frontmatter（`schema_kind: tower-state`、`summary_version: 1`、
`updated_at`、`session`、`next_ids`、`todo`），塔台每次寫這個檔都同步更新。本文是寫給塔台自己讀的，格式可以隨專案調整；
摘要是寫給外部讀者（BAT 指揮塔總覽）讀的，所以是一份欄位固定的契約——BAT 總覽靠它顯示待辦與下一個編號，沒有它就只能顯示「沒有機器可讀摘要」。
兩個設計選擇：

- **進行中工單不放進摘要**：外部讀者自己從各工單 frontmatter 的 `status` 算，免得同一件事有兩份資料、兩份對不上
- **新增欄位不升版；改既有欄位的名稱、型別或語意才升 `summary_version`，而且要先通知 BAT**：契約的另一方是別的專案，
  單方面改等於讓對方的面板默默壞掉（跨專案協調見 `advanced-patterns.md` § 跨專案協調）

舊專案沒有摘要不算錯，塔台下次寫入時補上。欄位、取值慣例與 YAML 寫法以 CT `memory-protocol.md` § 機器可讀摘要（YAML frontmatter）為準。
