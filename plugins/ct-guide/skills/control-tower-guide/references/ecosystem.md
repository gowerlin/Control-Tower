# Control Tower 生態系全覽

## 八個 Skill 元件

Control Tower 由一個塔台 skill 和七個輔助 skill 組成。每個 skill 都能從 Claude Code（`/`）或 Codex（`$`）呼叫：

| Skill | Claude Code | Codex | 角色 | 使用場景 |
|-------|-------------|-------|------|---------|
| `control-tower` | `/control-tower` | `$control-tower` | 指揮官（Orchestrator） | 塔台 session |
| `ct-exec` | `/ct-exec T0001` | `$ct-exec T0001` | 工單執行（Worker） | Worker session |
| `ct-done` | `/ct-done T0001` | `$ct-done T0001` | 補救收尾 | Worker session（中斷恢復） |
| `ct-status` | `/ct-status` | `$ct-status` | 狀態查詢（唯讀） | 任意 session |
| `ct-evolve` | `/ct-evolve` | `$ct-evolve` | 學習萃取 | 任意 session |
| `ct-insights` | `/ct-insights` | `$ct-insights` | 使用模式分析 | 任意 session |
| `ct-fieldguide` | `/ct-fieldguide` | `$ct-fieldguide` | FIELDGUIDE／DESIGN.md 自動化 | Worker session |
| `ct-help` | `/ct-help` | `$ct-help` | 操作手冊 + 概念速答 | 任意 session |

**Codex 相容的代價與做法**：每個 skill 的 frontmatter 只保留 `name` 與 `description`（Codex 的 skill 驗證把未知欄位視為錯誤），
另附一個 `agents/openai.yaml` 提供 Codex 端的顯示名稱與預設提示。所以版本號不在 frontmatter，而是 body 第一行的註解
`<!-- control-tower-version: X.Y.Z -->`。版本治理的完整設計見 `governance.md`。

### 角色定位

```
control-tower（指揮官）
  ├── 啟動 → 讀狀態與設定 → BAT 內宣告塔台分頁（v5.2.0）→ 狀態面板
  ├── 討論需求 → 對齊認知 → 產生工單（frontmatter + affects_files + 驗收閘門）
  ├── 派工（手動／BAT／YOLO）→ 讀回報 → 驗證證據 → 更新狀態（隔離工單另有合併，v5.3.0）
  └── 決策紀錄 → 學習萃取 → 決定下一張

ct-exec（主力工蜂）
  └── 讀工單 → 落點檢查 → 開工 → 執行 → 驗證 → 反序收尾 → 通知塔台

ct-done（救援工蜂）
  └── 落點檢查 → 補寫回報 → 更新狀態 → 通知塔台

ct-status（雷達）
  └── 單張或全部工單狀態、狀態分桶、frontmatter／body drift；也跑落點檢查，但只報告不阻斷

ct-evolve（學習引擎）
  └── 從經驗萃取可複用模式（「我學到了什麼？」）；分 Tactical／Strategic／Episodic，標記 [FG-CANDIDATE] 交給 ct-fieldguide

ct-insights（健檢儀）
  └── 分析工單歷史與使用模式的好壞（「我做得怎麼樣？」）

ct-fieldguide（教戰手冊工具）
  └── init／update／audit（含 --debt 找競爭實作）／extract／merge／promote；design 從程式碼或 URL 產出或稽核 DESIGN.md

ct-help（操作手冊）
  └── 指令速查、設定參考、BAT／YOLO 概念速答；只解釋，不建立或修改工單
```

在 BAT 裡，塔台要在使用者自己開的一般分頁啟動，不能在被派出來的 Worker 分頁裡（v5.2.4）。原因見 `bat-integration.md` § 範圍權杖與分頁角色。

落點檢查（Landing Zone Check）由 `ct-exec` 定義，`ct-done` 與 `ct-status` 引用同一份定義：
寫入型的兩者在不符時 STOP，唯讀的 `ct-status` 只把結果和狀態一起報告。設計理由見 `governance.md`。

## 三軌前綴：`*`、`/`、`$`

| 比較 | `*` 前綴 | `/` 前綴 | `$` 前綴 |
|------|---------|---------|---------|
| 是什麼 | 塔台內建命令 | Claude Code 載入獨立 skill | Codex 載入獨立 skill |
| 在哪用 | **僅限**進行中的塔台 session | 任意 Claude Code session | 任意 Codex session |
| 角色切換 | 不切換，繼續塔台流程 | 載入該 skill 的角色 | 同 `/` |
| 範例 | `*evolve` | `/ct-evolve` | `$ct-evolve` |

`/` 與 `$` 是**同一個 skill 的兩個入口**，差別只在宿主工具。BAT 派工時由 BAT 依 Worker 使用的 agent 決定送出 `/ct-exec` 還是 `$ct-exec`，塔台不寫死。

v5.14.0 起 CT 也能用 plugin 安裝（plugin `ct`）。Claude Code 寫法不變（`/ct-exec`，完整寫法 `/ct:ct-exec`）；Codex 用 plugin 安裝時要寫 `$ct:ct-exec`；BAT 派工要 BAT `>= 0.7.2-pre.1` 才會依安裝方式送這個寫法（v5.14.2），更舊的 BAT 叫不到，所以 Codex 搭配舊 BAT 仍用 zip 手動安裝。為什麼、以及兩種安裝並存時誰生效，見 `governance.md` § plugin marketplace：另一種安裝方式；寫法權威是 CT `auto-session.md` § 依安裝方式的 skill 呼叫字串。

`*` 命令與對應的獨立 skill（例如 `*evolve` 與 `ct-evolve`）的差別不在「精簡版 vs 完整版」，而在**在哪個角色裡執行**：
`*` 命令在塔台角色裡就地處理，獨立 skill 則在自己的 session 以自己的角色執行。

### 塔台內建命令一覽

| 命令 | 用途 |
|------|------|
| `*rescan` | 執行 Full Scan，重建 `_tower-state.md` 的環境快照 |
| `*config` | 檢視或調整塔台設定（見下方設定全表） |
| `*help` | 塔台內查詢使用說明；完整用法交給 `ct-help` |
| `*sync` | 以工單檔案為準，校準塔台記憶／工單／`sprint-status.yaml`，重建 BUG／PLAN 索引，報告 drift |
| `*pause` / `*resume` | 凍結進行中工單以處理緊急任務，之後恢復 |
| `*bug` / `*plan` / `*exp` | 建立 BUG／PLAN／EXP 單據（需先在設定中啟用） |
| `*archive` | 熱區 → 冷區歸檔（可預覽、強制指定、搜尋冷區、取回熱區） |
| `*evolve` | 學習萃取；子命令見下 |
| `*insights` | 依 session 與工單歷史做有證據的使用模式分析；v5.11.0 起 `*insights workflow [T#### …]` 跑預篩腳本，只做排除守門與按需提示、不改工單 |
| `*fieldguide` | FIELDGUIDE 管理 |
| `*import` | 安全匯入規則或 playbook：讀取現有 → 衝突分析 → 確認 → 寫入 |
| `*onboard` | 互動式探索 5 個主題（Git 習慣、哪些小事免開工單、Worker 收尾的 Git 行為、遇到不清楚的問題、塔台與 Worker 邊界），產出個人化 `_local-rules.md` |

旗標的確切拼法以 `ct-help` 或 CT reference 為準。

### `*evolve` 子命令

| 子命令 | 用途 |
|--------|------|
| `*evolve --playbook` | 把成熟的驗證規則寫成 playbook（L1→L2） |
| `*evolve --skill` | **只產出 skill brief**（觸發條件、核心流程、所需資源、驗證計畫）；要寫成已安裝的 skill，使用者須明確呼叫 `skill-creator` |
| `*evolve --status` | 查看各級數量、過時或重複的 learning、建議的下一步晉升 |

`--skill` 停在 brief，是因為 Layer 1 寫入規則：已安裝的 skill 不是塔台能自行寫入的地方（見 `three-layer-arch.md`）。

v5.10.0 起獨立 skill `ct-evolve` 多一個 `--workflow [name]`：只產 Workflow brief 與 🔵 知識卡，同樣停在 brief（腳本另開工單、使用者確認後才寫）。
v5.11.0 起塔台的 `*evolve --workflow [name]` 直接轉交 `/ct-evolve --workflow`，不另做一套（權威 CT `playbook-engine.md` § `*evolve` 擴展子命令）。概念見 `concepts.md` § Workflow：單張工單內的執行方式。

## SKILL.md 是路由器，reference 才是權威

v5 的 SKILL.md 不再承載完整規格。每個 SKILL.md 只寫三件事：**角色、硬邊界、路由表**；細節放在 `references/`，**按需載入**，不整批讀入。

| | SKILL.md | reference |
|---|---|---|
| 內容 | 角色、Hard Boundaries、何時載入哪份 reference | 完整規格、命令表、流程 |
| 權威性 | **摘要**——裡面的指令範例可能省略必要旗標 | 它負責的那個動作的**事實來源** |
| 載入時機 | skill 啟動時 | 當前動作需要時才讀 |

這帶來一條重要的使用規則：**SKILL.md 裡的指令範例不得當成實際執行指令的唯一來源**，要執行就去讀它旁邊指名的 reference。
這條「摘要授權規則」是從真實派工失誤得出的，詳見 `governance.md`。

為什麼要瘦身成路由器？SKILL.md 在每次觸發時整份進入 context。v5.0.2 時 8 個 SKILL.md 合計 4,938 行，v5.0.3 瘦身為 865 行——
規格放在 SKILL.md，等於每個 session 一開始就先燒掉大量 context，而且大部分內容與當下的動作無關。路由器化之後，context 只花在當前動作需要的那份 reference 上——這正是 `concepts.md` 第一原則的應用。

### `control-tower` 的 reference 目錄（31 份，九組）

| 分組 | Reference |
|------|-----------|
| 工單生命週期 | `work-order-system.md`、`work-order-template.md`、`research-workorder.md`、`merge-workorder.md`（v5.3.0） |
| Runtime 派工 | `auto-session.md`、`yolo-mode.md` |
| 狀態與記憶 | `memory-protocol.md`、`context-hygiene.md`、`data-layer-architecture.md` |
| 設定與說明 | `tower-config.md`、`beginner-tutorial.md` |
| Debug 與中斷 | `debug-strategies.md`、`interrupt-protocol.md` |
| 知識與演化 | `self-learning-core.md`、`playbook-engine.md`、`skill-writing-conventions.md`、`workflow-engine.md`（v5.10.0；v5.11.0 加 `workflow_integration` 的行為、授權治理與 G2 現況） |
| 多專案與 repo 形態 | `multi-tower-protocol.md`、`cross-project-coordination.md`、`mono-repo-patterns.md` |
| 命令與紀錄 | `bug-plan-system.md`、`decision-log-system.md`、`archive-system.md`、`fieldguide-commands.md`、`safe-import.md`、`onboarding.md` |
| 治理與設計依據 | `version-governance.md`、`doctrine.md`、`enhancement-integration.md`、`migration-engine.md` |

v5.2.1 起，塔台狀態面板的唯一定義在 `memory-protocol.md` § 塔台狀態面板（最小欄位與範本；欄位沒有資料就寫「未知」）。

其餘 1 份不在路由分組中：`interactive-prompts.md`（選項式提問規範）。
v5.12.4 起 `control-tower/references/ct-exec.md` 退役（內容與 `ct-exec/SKILL.md` 不一致、沒有任何檔案引用它），Worker 執行規則只看 `ct-exec/SKILL.md`。
v5.12.5 起其餘三份 Worker 命令長版說明（`ct-done`、`ct-status`、`ct-evolve`）也退役：仍有效的規則補進各自的 `SKILL.md`，塔台主動提議 `/ct-evolve` 的時機搬進 `self-learning-core.md`，各 Worker 命令的規則只看自己的 `SKILL.md`。

其他 skill 也各有自己的 reference：`ct-exec` 1 份（`session-guardrails.md`：重試、範圍守衛、洋蔥偵測、超時提醒）、
`ct-fieldguide` 4 份、`ct-insights` 3 份；`ct-done`、`ct-status`、`ct-evolve`、`ct-help` 沒有自己的 reference，
需要時引用其他 skill 的定義（例如 `ct-done`／`ct-status` 引用 `ct-exec` 的落點檢查，`ct-help` 引用 `control-tower` 的 reference）。

`beginner-tutorial.md` 不是獨立 skill，而是塔台在 `experience-level` 為 `beginner` 時啟用的教學模式。
`doctrine.md` 是 CT 的設計依據文件，回答「為什麼這樣設計」——本教材的概念章節以它為上游。

## 資料流向

```
使用者描述需求
    ↓
🗼 塔台 session（/control-tower 或 $control-tower）
    ├── 對齊 → 產生工單 .md（frontmatter = SoT）
    ├── 派發前：affects_files 重疊檢查
    ├── 派工
    │     ├─ 手動：顯示 Worker 指令，使用者自己開 session
    │     └─ BAT／YOLO：BAT 開出 Worker 終端並帶入工單與 CT_MODE（`isolation: worktree` 的工單在獨立 worktree，v5.3.0）
    │             ↓
    │   🔧 Worker session（/ct-exec 或 $ct-exec T0001）
    │       ├── 落點檢查 → 開工 → 執行 → 驗證（證據分道）
    │       ├── 反序收尾：產品 commit → 回報區 → 狀態 → 工單 commit（commit 依政策；v5.7.0）
    │       └── 回報塔台
    │             ├─ 手動：顯示「T0001 完成」，使用者帶回塔台
    │             ├─ BAT：預填到塔台輸入列，使用者確認送出（`on`；`ask` 由使用者帶回）
    │             └─ YOLO：預填並自動送出
    │             ↓
    ├── 讀工單回報區 → 驗證狀態、commit、變更檔、證據
    ├── 隔離工單：合併回 main（塔台直接合併或派合併工單，v5.3.0）
    ├── 更新塔台狀態 → 記錄決策與學習
    └── 決定下一步：下一張、Renew、結案、驗證，或升級求助（YOLO 遇斷點才停下）
```

三種形態的差別只在「誰開 Worker」與「誰按下送出」；工單檔案作為唯一通道這點不變。派工機制詳見 `runtime-dispatch.md`。

## 能力等級（Level 0-3）

CT 的功能隨可選元件遞增，每項偵測獨立，可任意組合（例如 Level 0+2 完全合法）：

| Level | 條件 | 能力 |
|-------|------|------|
| **Level 0** | 零相依 | 完整核心：工單、進度、Debug、學習（`_learnings.md`） |
| **Level 1** | + ECC continuous-learning-v2 | hook 觀察、instinct 置信度、`/evolve` 進化 |
| **Level 2** | + **外部** `bmad-guide` skill | 自動 BMad workflow routing 與 Agent 標注 |
| **Level 3** | + mem0 REST | 寫入同步跨裝置／跨專案經驗（單向，透過 memsync CLI 橋接） |

**重要**：Level 0 已經完全可用。增強元件是錦上添花，不是必要條件；缺少任何一個都靜默降級。

**Level 2 的邊界**：CT 不內嵌任何 BMad-Method 內容，只偵測使用者另外安裝的 `bmad-guide` 並讀它的 reference。
`bmad-guide` 不可用時，塔台照常運作，BMad 工作流程欄位改為手動指定，且不自行編造 BMad 行為。
v5.14.1 起 zip 手動安裝與 plugin 安裝的 bmad-guide 都偵測得到（手動優先；v5.14.4 起先找本 runtime 的安裝，另一個 runtime 的只當讀檔來源）；可用 skill 清單有它卻讀不到檔案時，塔台提示一次而不是靜默降級，見 `integration.md` § 偵測與降級。

## 設定系統

透過 `*config` 調整。下表為 CT 全部設定項、值域與預設值：

| 設定項 | 值域 | 預設值 | 說明 |
|--------|------|--------|------|
| `alignment-rounds` | `0` - `5` | `3` | 需求對齊最少提問輪數；`0` = 關閉強制提問 |
| `interactive-prompts` | `on` / `off` | `on` | 選項式提問開關 |
| `experience-level` | `beginner` / `standard` / `expert` | `standard` | 提示詳細度與引導程度；`beginner` 啟用教學模式 |
| `verbose` | `on` / `off` | `on` | 工單派發摘要的詳細程度 |
| `auto-session` | `on` / `ask` / `off` / `yolo` | `ask` | 派工後開 Worker 的行為：`on` 靜默開新分頁；`ask` 詢問；`off` 僅文字提示；`yolo` = `on` 的超集，Worker 自動送出 + 塔台自主決定下一張 |
| `yolo_max_retries` | `0` - `10` | `3` | YOLO 斷點 B 閾值（Renew ≥N 次或連續 N 張 FAILED 即暫停）；`0` = 停用斷點 B |
| `project-prefix` | `2-4 字元大寫英文` / 空 | 空 | 跨專案協調用的工單 ID 前綴 |
| `enable_bug_tracking` | `true` / `false` | `false` | 啟用 BUG 單據 |
| `enable_plan_tracking` | `true` / `false` | `false` | 啟用 PLAN 單據 |
| `enable_experiments` | `true` / `false` | `false` | 啟用 EXP 實驗單據 |
| `archive_days` | `0` - `365` | `7` | 終態單據超過此天數成為歸檔候選；`0` = 立即可歸檔 |
| `auto_archive_prompt` | `on` / `off` | `off` | `*sync` 結束後是否提示歸檔候選數量 |
| `research_interaction` | `true` / `false` | `true` | 研究型工單是否允許 Worker 互動；yolo 下不適用（Worker 一律改問塔台，v5.5.0） |
| `research_max_questions` | `1` - `5` | `3` | 研究型工單 Worker 每次提問的上限 |
| `auto_commit` | `on` / `ask` / `off` | `ask` | 塔台直接處理小變動後的 commit 行為；只對「小且無邏輯變動」的修改生效 |
| `auto_commit_format` | 字串模板 | `"chore: {description} ({scope})"` | 塔台自主 commit 的訊息模板 |
| `worker_max_retries` | `1` - `10` | `3` | Worker 熔斷計數上限，同一問題連續失敗達此次數即三振 |
| `worker_strikeout_action` | `block` / `warn` | `block` | 三振後：`block` 禁止再試、強制收尾回報；`warn` 警告但由使用者決定；yolo 下 `warn` 照 `block` 處理（v5.5.1） |
| `worker_commit` | `required` / `recommended` / `off` | `required` | Worker 收尾的 commit 政策（`ct-done` 也依此檢查） |
| `worker_auto_close` | `off` / `done` | `off` | `done` = 工單 `DONE` 且不 Renew、輸出收單確認之後，請 BAT 回收該單的 Worker 分頁；`off` = 收單流程不變。不影響 v5.12.0 的重派前回收（`off` 也回收） |
| `worker_close_delay` | `0` - `300`（秒） | `10` | 回收前的延遲；期間 Worker 分頁的輸出不取消回收，只有使用者在該分頁輸入才取消（終端自動回應不算）；到期後 BAT 等連續安靜 5 秒才關，最多再等 60 秒。只在 `worker_auto_close: done` 時有作用（v5.12.1 對齊 BAT T0545，定義見 CT `tower-config.md`） |
| `worker_question_timeout` | `0` - `120`（分鐘） | `30` | v5.5.0。yolo Worker 向塔台提問後等答覆的上限；`0` = 不等，直接 `BLOCKED`。塔台 yolo 派工時把生效值寫進工單 frontmatter；只影響 yolo |
| `workflow_integration` | `off` / `ask` / `on` | `on` | v5.11.0。Claude Code Workflow 的整合強度：`off` 不建議、不授權；`ask` 每次授權前問使用者；`on` 知識卡到 ⭐ 前問使用者。token 焦慮時可用 `*config workflow_integration off` 只關這個 session（見 `concepts.md` § v5.11.0：回測沒過之後，先做便宜的部分） |
| `bug_review_open_threshold` | `0` - `500` | `20` | v5.13.0。熱區未結 BUG 多於這個張數時，`*sync`／`*insights` 印一行清理提示；`0` = 停用這個條件 |
| `bug_review_stale_days` | `0` - `365`（天） | `30` | v5.13.0。有未結 BUG 超過這個天數沒更新時，同上提示；`0` = 停用這個條件 |
| `customer_acceptance_gate` | `on` / `off` | `off` | v5.13.0。客戶驗收不回歸閘（可選）；只在專案進入客戶驗收、有驗收案例表時開（見 `work-order-lifecycle.md` § 客戶驗收不回歸閘） |

設定的四層覆蓋：**Session > Project > Global > Default**（見 `three-layer-arch.md`）。

`auto-session` 的生效值一改（例如 `*config auto-session yolo`），塔台在 BAT 內會帶新的 `--mode` 再宣告一次自己的分頁（v5.2.0），
BAT 才知道塔台目前是不是 yolo；設計理由見 `bat-integration.md` § 塔台分頁角色宣告。

這些設定屬於**塔台**。Worker 不讀設定檔決定 runtime 模式，只能從設定讀取重試上限、commit 政策這類調諧參數。

---

## v4 → v5 世界觀變更對照表

給從 v4 教材升級的讀者：以下是 v5 世界觀與 v4 敘述不同的地方。本教材正文一律以右欄為準。

| # | v4 的理解 | v5 的現況 |
|---|----------|----------|
| S-1 | 工單 metadata 只有一份，檔案即唯一來源 | YAML frontmatter = 機器 SoT，body 表格 = 人類鏡像；drift 只警告不覆寫 |
| S-2 | SKILL.md 承載完整規格；`*` 命令是精簡版、`/` skill 是完整版 | SKILL.md 是路由器，reference 按需載入且為權威；SKILL.md 指令範例是有損摘要 |
| S-3 | Worker 收尾 = 複製剪貼簿，使用者手動回塔台報告 | 手動／BAT 預填／YOLO 自動送出三態；剪貼簿只是 fallback |
| S-4 | Worker 依設定檔決定互動與 session 行為 | Worker 無狀態：模式由 `CT_MODE`／`CT_INTERACTIVE` 在派工時傳入 |
| S-5 | Worker 一律強制 commit | 依工單指示與 `worker_commit`（`required`／`recommended`／`off`） |
| S-6 | 工單正常路徑含 `REVIEW` 待審狀態 | status enum 無此狀態；審查以另一張工單進行 |
| S-7 | Worker 開工即信任派工端，直接改狀態 | 任何寫入前先跑 Landing Zone Check，repo 身分不符即 STOP |
| S-8 | Layer 1 禁寫 = `control-tower` skill 目錄，升級只靠人工 | 範圍 = 整個 `~/.claude/skills/`（掃描器機制），v5.14.0 起含 plugin 安裝路徑；唯一例外 = 工單明文授權的安裝；備份放 `~/.claude/skill-backups/`（plugin 不備份） |
| S-9 | 跨專案協調只有 3 種，ID 前綴只來自 `project-prefix` | 5 種（含非工單通道 HANDOVER／ADVISORY）；ID 格式單一權威定義，前綴可來自跨塔台交辦 |
| S-10 | Level 3 = claude-mem 持久記憶 | Level 3 = mem0 REST（memsync CLI 單向同步） |
| S-11 | BMad 工作流程路由由 CT 附帶 | CT 不內嵌 BMad 內容，Level 2 只偵測外部 `bmad-guide` |
| S-12 | Tower State = 當前 Sprint／進行中工單／已知問題／決策摘要／學習重點／下一步 | 起手式／基本資訊／編號追蹤／進度快照／本 Session 決策日誌／待處理事項 + 環境快照 + YOLO 歷程 |
| S-13 | EXP 走 PENDING → IN_PROGRESS → DONE／FAILED／ABANDONED | `EXPLORING → CONCLUDED／ABANDONED` |
| S-14 | 塔台輸出粒度分析卡；`*help roles` 職責速查卡 | 兩者皆已移除；粒度原則保留在請求分類與工單粒度原則中 |
| S-15 | CT 指令只有 Claude 的 `/` 形式 | `/`／`$` 雙前綴，Worker 可以是 Claude Code 或 Codex |
