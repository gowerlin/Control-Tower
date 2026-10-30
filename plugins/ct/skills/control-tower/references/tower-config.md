# 塔台設定系統

> 塔台內建命令（`*` 前綴）的完整規格。
>
> ## 內建命令總覽
>
> | 命令 | 語法 | 用途 |
> |------|------|------|
> | `*config` | `*config [option] [value] [--save scope]` | 調整塔台行為設定 |
> | `*help` | `*help [topic]` | 查詢使用指南 |
> | `*sync` | `*sync` | 進度同步，掃描工單比對差異 |
> | `*pause` | `*pause [原因]` | 暫停當前工單，處理緊急任務 |
> | `*resume` | `*resume [工單編號]` | 恢復被暫停的工單 |
> | `*evolve` | `*evolve [topic]` | 學習萃取（精簡版） |

## `*config` 命令

### 語法

```
*config                              # 列出所有設定及來源
*config <option>                     # 查看單項設定
*config <option> <value>             # 修改設定（僅本次 session）
*config <option> <value> --save project   # 寫入專案設定檔
*config <option> <value> --save global    # 寫入全局設定檔
*config reset                        # 重設所有設定為預設值（僅 session）
*config reset <option>               # 重設單項設定為預設值（僅 session）
```

### 可用選項

| 選項 | 有效值 | 預設 | 說明 |
|------|--------|------|------|
| `alignment-rounds` | `0` - `5` | `3` | 需求對齊最少提問輪數。`0` = 關閉強制提問，直接產生工單 |
| `interactive-prompts` | `on` / `off` | `on` | 選項式提問開關。`off` 時退回純文字提問 |
| `experience-level` | `beginner` / `standard` / `expert` | `standard` | 影響提示詳細度和引導程度 |
| `verbose` | `on` / `off` | `on` | 工單派發摘要的詳細程度。`off` 時精簡輸出 |
| `auto-session` | `on` / `ask` / `off` / `yolo` | `ask` | 工單派發後自動開新 session 行為。`on` = 靜默開新分頁；`ask` = 詢問使用者；`off` = 僅文字提示；`yolo` = `on` 的超集，Worker 自動送出 + 塔台自主決策下一張工單（詳見 [yolo-mode.md](yolo-mode.md)） |
| `yolo_max_retries` | `0` - `10` | `3` | YOLO 模式斷點 B 閾值（Renew ≥N 次或連續 N 張 FAILED 觸發暫停）。`0` = 停用斷點 B。詳見 [yolo-mode.md](yolo-mode.md) |
| `worker_question_timeout` | `0` - `120`（分鐘，整數） | `30` | v5.5.0+。yolo Worker 向塔台提問後原地等待答覆的上限；逾時改以 `BLOCKED` 收尾、由塔台以 Renew 答覆。`0` = 不等，提問後直接走備援。只影響 yolo。塔台 yolo 派工時把生效值寫進工單 frontmatter，Worker 的取值順序見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › `worker_question_timeout` 的取值。走 BAT 通道（v5.7.0+）時同一個值也是 `--ask --expires-min` 的值（見同節 § BAT 通道 › 限制、§ Worker 端 3-A） |
| `project-prefix` | `2-4 字元大寫英文` / 空 | 空 | 專案前綴，用於跨專案協調時的工單編號。設定後工單格式變為 `<前綴>-T<編號>-<描述>`。詳見 [cross-project-coordination.md](cross-project-coordination.md) |
| `enable_bug_tracking` | `true` / `false` | `false` | 啟用 BUG 單據追蹤。啟用後可使用 `*bug` 命令建立 BUG 單，`*sync` 掃描 BUG 檔案。詳見 [bug-plan-system.md](bug-plan-system.md) |
| `enable_plan_tracking` | `true` / `false` | `false` | 啟用 PLAN 單據追蹤。啟用後可使用 `*plan` 命令建立 PLAN 單，`*sync` 掃描 PLAN 檔案。詳見 [bug-plan-system.md](bug-plan-system.md) |
| `enable_experiments` | `true` / `false` | `false` | 啟用 EXP 實驗追蹤。啟用後可使用 `*exp` 命令建立 EXP 單，支援 worktree 隔離實驗。詳見 [bug-plan-system.md](bug-plan-system.md) |
| `archive_days` | `0` - `365` | `7` | 歸檔天數門檻。最終態單據超過此天數成為歸檔候選。`0` = 最終態立即可歸檔。詳見 [archive-system.md](archive-system.md) |
| `auto_archive_prompt` | `on` / `off` | `off` | `*sync` 結束後是否提示歸檔候選數量。`on` 時在同步摘要末尾顯示候選提示。詳見 [archive-system.md](archive-system.md) |
| `bug_review_open_threshold` | `0` - `500` | `20` | v5.13.0+。熱區未結 BUG 多於這個張數時，`*sync`／`*insights` 印一行提示建議逐張核對。`0` = 停用這個條件。條件與提示見 [bug-plan-system.md](bug-plan-system.md) § BUG 單據 › 未結 BUG 清理提示 |
| `bug_review_stale_days` | `0` - `365`（天） | `30` | v5.13.0+。有未結 BUG 超過這個天數沒更新時，同上提示。`0` = 停用這個條件。詳見同上 |
| `customer_acceptance_gate` | `on` / `off` | `off` | v5.13.0+。客戶驗收不回歸閘（可選規則）。`on` 時會改程式或資料的工單多一段〈相關通過案例〉，動工前逐案判定、會改變通過案例就停下交使用者。只在專案已進入客戶驗收、有驗收案例表時開。規則與為何預設 `off` 見 [work-order-template.md](work-order-template.md) § 撰寫〈相關通過案例〉 |
| `research_interaction` | `true` / `false` | `true` | 研究型工單是否允許 Worker 互動。塔台派工時據此決定傳 `--interactive`／`--no-interactive`（v5.5.0+ yolo 不適用：一律 `--no-interactive`，Worker 改問塔台，見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問）；Worker 不讀此值決定互動（runtime `CT_INTERACTIVE` 優先，見 [auto-session.md](auto-session.md) § Mode 與互動旗標協定）。詳見 [research-workorder.md](research-workorder.md) |
| `research_max_questions` | `1` - `5` | `3` | 研究型工單 Worker 每次提問的上限數量。詳見 [research-workorder.md](research-workorder.md) |
| `auto_commit` | `on` / `ask` / `off` | `ask` | 塔台直接處理小變動後的 commit 行為。`on` = 靜默自主 commit；`ask` = 完成修改後詢問使用者；`off` = 不 commit，僅回報修改內容。僅對粒度判斷為「小」且無邏輯變動的修改生效。硬限制（邏輯變動、多模組、使用者禁止）不受此設定影響 |
| `auto_commit_format` | 字串模板 | `"chore: {description} ({scope})"` | 自主 commit 訊息格式。可用變數：`{description}`（描述動作）、`{scope}`（影響範圍）。範例：`chore: fix typos in README (documentation)` |
| `worker_max_retries` | `1` - `10` | `3` | Worker 熔斷計數器最大嘗試輪數。同一問題連續失敗達此次數觸發三振出局。詳見 [session-guardrails.md](../../ct-exec/references/session-guardrails.md) |
| `worker_strikeout_action` | `block` / `warn` | `block` | 三振出局觸發後行為。`block` = 禁止繼續嘗試，強制收尾回報；`warn` = 警告但允許使用者決定（`CT_MODE=yolo` 時照 `block` 處理，v5.5.1+）。詳見 [session-guardrails.md](../../ct-exec/references/session-guardrails.md) |
| `worker_commit` | `required` / `recommended` / `off` | `required` | Worker 收尾時 commit 行為。`required` = 必須 commit（失敗仍完成收尾）；`recommended` = 建議 commit，不阻斷；`off` = 不要求。ct-done 補救收尾時也依此檢查 |
| `worker_auto_close` | `off` / `done` | `off` | `done` = 工單 `DONE` 且不 Renew、輸出收單確認後，呼叫 BAT 回收該工單的 Worker 分頁。`PARTIAL` / `FAILED` / `BLOCKED` 與需要 Renew 的單一律不回收。僅在 BAT 環境（`BAT_SESSION=1`）且該工單是由本塔台以 `bat-terminal.mjs` 派出時生效。`off` = 收單流程不變。觸發條件、指令與 exit code 處理見 [work-order-system.md](work-order-system.md) § 回報處理流程。不影響重派前回收（v5.12.0+，`off` 時也回收；見 [work-order-system.md](work-order-system.md) § 重派前回收舊 Worker 分頁） |
| `worker_close_delay` | `0` - `300`（秒） | `10` | 回收前的延遲，以 `--delay-ms` 傳給 BAT。延遲期間 Worker 分頁的輸出**不**取消回收；只有排程後使用者在該 Worker 分頁的輸入會取消（終端自動回應，例如切換分頁時送出的 focus report，不算輸入）。延遲到期後 BAT 等分頁連續安靜 5 s 才關，從到期起最多再等 60 s，屆時仍在輸出就放棄、分頁保留（helper 已 exit `0`，塔台不會得知）。以上依 BAT T0545／D145（BAT `CLAUDE.md`「Worker 分頁回收」節、`docs/agent-guide/worker-tab-recycle.md`）。僅在 `worker_auto_close: done` 時有作用。詳見 [work-order-system.md](work-order-system.md) § 回報處理流程 |
| `workflow_integration` | `off` / `ask` / `on` | `on` | v5.11.0+。Claude Code Workflow 工具的整合強度（token 焦慮時可臨時關閉）。`off` = 塔台不建議、不授權 Worker 用 Workflow，不跑工具型 workflow；`ask` = 每次要授權 Worker 用 Workflow 都先問使用者，⭐ 也一樣；`on` = 知識卡到 ⭐ 之前先問使用者，⭐ 之後塔台在 yolo 下可自決。三個值下，規則分析、預篩腳本與 `--workflow` brief 都照常（不花 workflow token）。只約束塔台；Worker 不讀此值，依工單裡的授權段落行事。行為細節見 [workflow-engine.md](workflow-engine.md) § `workflow_integration` 的行為 |

> `_tower-config.yaml` 另有 `gp-prefix`（Playbook 的 GP 編號前綴）：它不是 `*config` 選項，所以不列在上表。定義、設定位置與未設定時的 fallback 見 [multi-tower-protocol.md](multi-tower-protocol.md) § `gp-prefix` 設定（唯一權威定義）。

### experience-level 行為差異

| 行為 | beginner | standard | expert |
|------|----------|----------|--------|
| 首次啟動提示 | 顯示 | 顯示 | 隱藏 |
| 工單模板說明 | 詳細 | 標準 | 精簡 |
| 工作流程建議 | 主動提供 | 被動提供 | 僅被問時 |
| 術語解釋 | 自動附加 | 不附加 | 不附加 |
| 對齊提問輪數建議 | 4-5 輪 | 3 輪 | 1-2 輪 |

### 輸出格式

```
*config 不帶參數的輸出範例：

⚙️ 塔台設定
┌──────────────────┬──────────┬──────────┐
│ 選項             │ 目前值   │ 來源     │
├──────────────────┼──────────┼──────────┤
│ alignment-rounds │ 3        │ 預設     │
│ interactive-prompts │ on    │ global   │
│ experience-level │ expert   │ project  │
│ verbose          │ off      │ session  │
└──────────────────┴──────────┴──────────┘

💡 使用 *config <option> <value> 修改（預設僅 session）
   加 --save project 或 --save global 持久化
```

## 作用域與持久化

### 三層設定架構

```
session（記憶體，最高優先）
  ↑ 覆蓋
project — Layer 3（_ct-workorders/_tower-config.yaml）
  ↑ 覆蓋
global — Layer 2（~/.claude/control-tower-data/config.yaml）
  ↑ 覆蓋
預設值（tower-config.md § 可用選項的「預設」欄 — Layer 1）
```

> **遷移注意**：全局設定從 `~/.claude/control-tower-config.yaml` 遷入
> `~/.claude/control-tower-data/config.yaml`（Layer 2）。過渡期兩個路徑均可讀取，
> 新路徑優先。詳見 [data-layer-architecture.md](data-layer-architecture.md) 遷移指南。

### 持久化檔案格式

```yaml
# _ct-workorders/_tower-config.yaml（Layer 3）或 ~/.claude/control-tower-data/config.yaml（Layer 2）
control-tower:
  alignment-rounds: 3
  interactive-prompts: on
  experience-level: standard
  verbose: on
  # v4 多單據類型（預設關閉，按需啟用）
  enable_bug_tracking: false
  enable_plan_tracking: false
  enable_experiments: false
  # v4 歸檔系統
  archive_days: 7
  auto_archive_prompt: off
  # v5.13.0+ 未結 BUG 清理提示門檻（0 = 停用該條件）
  bug_review_open_threshold: 20
  bug_review_stale_days: 30
  # v5.13.0+ 客戶驗收不回歸閘（可選；專案進入客戶驗收才開）
  customer_acceptance_gate: off
  # v4 研究型工單
  research_interaction: true
  research_max_questions: 3
  # v4 粒度決策 + 自主 commit
  auto_commit: ask
  auto_commit_format: "chore: {description} ({scope})"
  # v4 Worker 安全護欄
  worker_max_retries: 3
  worker_strikeout_action: block
  worker_commit: required
  # v4.2+ YOLO 模式
  yolo_max_retries: 3
  # v5.5+ yolo Worker 向塔台提問的等待上限（分鐘；0 = 不等）
  worker_question_timeout: 30
  # v5.1+ 收單後回收 Worker 分頁（需 BAT 支援 --close-worker）
  worker_auto_close: off
  worker_close_delay: 10
  # v5.11+ Claude Code Workflow 整合強度（off / ask / on）
  workflow_integration: on
```

### 啟動時載入流程

1. 讀取預設值（本檔 § 可用選項的「預設」欄 — Layer 1）
2. 讀取 `~/.claude/control-tower-data/config.yaml`（global — Layer 2），覆蓋預設
   - 若不存在，降級讀取 `~/.claude/control-tower-config.yaml`（舊路徑，過渡期相容）
3. 讀取 `_ct-workorders/_tower-config.yaml`（project — Layer 3），覆蓋 global
4. Session 設定（`*config` 即時修改）覆蓋一切

### 寫入行為

- `--save project`：讀取現有 `_ct-workorders/_tower-config.yaml`，合併修改項，寫回
- `--save global`：讀取現有 `~/.claude/control-tower-data/config.yaml`（Layer 2），合併修改項，寫回
- 不帶 `--save`：僅修改 session 記憶體，session 結束即失效
- `auto-session`（v5.2.0+）：修改後若生效值改變且在 BAT 內，要用新的 `--mode` 再宣告一次塔台分頁角色，見 [auto-session.md](auto-session.md) § 塔台分頁角色宣告

### 驗證規則

- 值不在有效範圍內 → 報錯，不修改
- 選項名稱不存在 → 報錯，列出可用選項
- 設定檔語法錯誤 → 警告，使用預設值

## 擴展新選項

新增選項時需定義：

```yaml
option_name:
  type: string | number | boolean
  valid_values: [list] | range(min, max)
  default: value
  description: 說明文字
  affects: [哪些行為受影響]
```

在本檔案「可用選項」表新增一列，並在「持久化檔案格式」範例補上預設值。
本檔案是選項的唯一權威定義：`control-tower/SKILL.md` 沒有選項表（`*config` 只指向本檔），
不得在 SKILL.md 新建選項表；其他文件需要提到選項時，引用本檔，不複述有效值與預設。

---

## `*help` 命令

### 語法

```
*help                    # 顯示指令速查表
*help <topic>            # 查看特定主題
```

### 可查詢主題

| 主題 | 對應內容 | 說明 |
|------|---------|------|
| `commands` | ct-help 指令速查表 | 所有指令的用途和使用位置 |
| `workflow` | ct-help 工作流程速查 | 日常開發、中斷恢復、Sprint 結束 |
| `config` | 本檔案 *config 段落 | 設定選項和持久化 |
| `workorder` | work-order-system.md 摘要 | 工單生命週期和狀態流轉 |
| `status` | ct-help 紀錄保存位置 | 紀錄在哪裡、持久性 |
| `tips` | ct-help 溝通技巧 | 如何表達需求、確認理解 |

### 執行行為

1. **不帶參數**：顯示精簡版指令速查表
   ```
   🗼 塔台快速參考
   ─────────────────
   /control-tower    啟動或恢復塔台
   /ct-exec T0001    子 session 執行工單
   /ct-done T0001    補救收尾
   /ct-status        查看所有工單狀態
   /ct-evolve        萃取學習模式
   *config           查看/修改塔台設定
   *help <topic>     查看特定主題說明

   可用主題：commands · workflow · config · workorder · status · tips
   ```

2. **帶參數**：讀取 ct-help skill 或對應 reference 的相關內容，**在塔台 session 內**回答
   - 回答後繼續塔台流程，不切換角色
   - 不載入 ct-help 的完整 skill 定義

### 與 `/ct-help` 的差異

| 特性 | `*help` | `/ct-help` |
|------|---------|-----------|
| 執行位置 | 塔台 session 內 | 任意 session（獨立 skill） |
| 角色切換 | 不切換，保持塔台角色 | 載入使用指南角色 |
| 內容範圍 | 按主題查詢，精簡回答 | 完整使用指南 |
| 後續流程 | 回答後繼續塔台工作 | 獨立結束 |
| 適用情境 | 塔台工作中快速查詢 | 新手完整了解生態系 |
