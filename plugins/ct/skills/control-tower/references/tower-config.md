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
| `enable_bug_tracking` | `true` / `false` | `true` | 啟用 BUG 單據追蹤。啟用後可使用 `*bug` 命令建立 BUG 單，`*sync` 掃描 BUG 檔案；啟用時（含預設）立即產生空的 `_bug-tracker.md`（[bug-plan-system.md](bug-plan-system.md) § 啟用與索引檔）。v6 起預設 `true`（D363），設定明寫 `false` 的照舊 |
| `enable_plan_tracking` | `true` / `false` | `true` | 啟用 PLAN 單據追蹤。啟用後可使用 `*plan` 命令建立 PLAN 單，`*sync` 掃描 PLAN 檔案；啟用時（含預設）立即產生空的 `_backlog.md`（[bug-plan-system.md](bug-plan-system.md) § 啟用與索引檔）。v6 起預設 `true`（D363），設定明寫 `false` 的照舊 |
| `enable_experiments` | `true` / `false` | `true` | 啟用 EXP 實驗追蹤。啟用後可使用 `*exp` 命令建立 EXP 單，支援 worktree 隔離實驗；EXP 沒有索引檔。詳見 [bug-plan-system.md](bug-plan-system.md)。v6 起預設 `true`（D368），設定明寫 `false` 的照舊 |
| `archive_days` | `0` - `365` | `7` | 歸檔天數門檻。最終態單據超過此天數成為歸檔候選。`0` = 最終態立即可歸檔。詳見 [archive-system.md](archive-system.md) |
| `auto_archive_prompt` | `on` / `off` | `off` | `*sync` 結束後是否提示歸檔候選數量。`on` 時在同步摘要末尾顯示候選提示。詳見 [archive-system.md](archive-system.md) |
| `bug_review_open_threshold` | `0` - `500` | `20` | v6.0.0-beta.3+。熱區未結 BUG 多於這個張數時，`*sync`／`*insights` 印一行提示建議逐張核對。`0` = 停用這個條件。條件與提示見 [bug-plan-system.md](bug-plan-system.md) § BUG 單據 › 未結 BUG 清理提示 |
| `bug_review_stale_days` | `0` - `365`（天） | `30` | v6.0.0-beta.3+。有未結 BUG 超過這個天數沒更新時，同上提示。`0` = 停用這個條件。詳見同上 |
| `customer_acceptance_gate` | `on` / `off` | `off` | v6.0.0-beta.3+。客戶驗收不回歸閘（可選規則）。`on` 時會改程式或資料的工單多一段〈相關通過案例〉，動工前逐案判定、會改變通過案例就停下交使用者。只在專案已進入客戶驗收、有驗收案例表時開。規則與為何預設 `off` 見 [work-order-template.md](work-order-template.md) § 撰寫〈相關通過案例〉 |
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
| `methodology` | `auto` / `none` / `<adapter id>` | `auto` | v6.0.0+。主方法論（沒有個別指定的層都跟它）。語意見 [methodology-adapters.md](methodology-adapters.md) § 抽換 |
| `methodology_planning` | `inherit` / `none` / `<adapter id>` | `inherit` | v6.0.0+。規劃層的負責 adapter。語意見 [methodology-adapters.md](methodology-adapters.md) § 抽換、§ 層次 |
| `methodology_execution` | `inherit` / `none` / `<adapter id>` | `inherit` | v6.0.0+。執行層的負責 adapter。語意同上 |
| `methodology_review` | `inherit` / `none` / `<adapter id>` | `inherit` | v6.0.0+。審查層的負責 adapter。語意同上；換層時的能力落差見 [methodology-adapters.md](methodology-adapters.md) § 分層疊加 |
| `methodology_verification` | `inherit` / `none` / `<adapter id>` | `inherit` | v6.0.0+。驗證層的負責 adapter。語意同上 |
| `methodology_delivery` | `none` / `<adapter id>` | `none` | v6.0.0+。交付層的負責 adapter（不接受 `inherit`）。語意同上 |
| `methodology_subagent_writes` | `deny` / `per-workorder` | `deny` | v6.0.0+。方法論寫入型子代理的處置。語意見 [methodology-adapters.md](methodology-adapters.md) § 衝突與防護 C4 |
| `methodology_guard` | `warn` / `block` / `off` | `warn` | v6.0.0+。派工前的方法論注入／衝突檢查。語意見 [methodology-adapters.md](methodology-adapters.md) § 與 hook／session 路由的相處規則 |
| `methodology_adapters_path` | 路徑 / 空 | 空 | v6.0.0+。額外的 adapter 搜尋路徑。語意見 [methodology-adapters.md](methodology-adapters.md) § 散布與搜尋順序 |

> `methodology*` 這 9 個鍵的驗證、檢視、持久化與相容規則見下方 § 方法論設定鍵；值的**語意**（層次、`auto`／`inherit` 怎麼解析、降級）
> 只寫在 [methodology-adapters.md](methodology-adapters.md)，本檔不複述。

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

### 方法論設定鍵（v6.0.0+）

本節只管 `methodology*` 9 個鍵的登錄面：驗證、檢視、寫入與相容。值的語意、層次、`auto`／`inherit` 的解析、找不到 adapter 時怎麼退
都以 [methodology-adapters.md](methodology-adapters.md)（§ 抽換、§ 分層疊加、§ 解析步驟、§ 降級）為準。

**舊設定相容**：設定檔（global、project）與 session 都沒有任何 `methodology*` 鍵時，9 個鍵全取 § 可用選項的預設值，
`methodology` 即 `auto`，塔台行為與 v5.12.6 相同。升級到 v6.0.0 不需要改設定檔；塔台也不會自己把這組鍵補寫進既有設定檔，
只有使用者用 `*config … --save` 或 `*onboard`（[onboarding.md](onboarding.md) 主題 5）選了非預設值才寫入。
Worker 不讀這組鍵（[methodology-adapters.md](methodology-adapters.md) § Worker 帶入）；塔台派工時把解析結果寫進工單 frontmatter `methodology`。

#### 值的驗證

| 選項 | 接受 | 報錯（不修改） | 照存但警告 |
|---|---|---|---|
| `methodology` | `auto`、`none`、符合 `[a-z0-9-]+` 的 adapter id | 大寫、空白、底線等不符 id 格式的值；`inherit`（主方法論沒有上一層可跟） | id 格式正確，但照搜尋順序找不到這個 adapter、或描述檔壞掉 |
| `methodology_planning`／`_execution`／`_review`／`_verification` | `inherit`、`none`、adapter id | 不符 id 格式的值；`auto`（只用在主方法論） | 同上 |
| `methodology_delivery` | `none`、adapter id | 不符 id 格式的值；`inherit`、`auto` | 同上 |
| `methodology_subagent_writes` | `deny`、`per-workorder` | 其他值 | — |
| `methodology_guard` | `warn`、`block`、`off` | 其他值 | — |
| `methodology_adapters_path` | 一個路徑字串；空字串 = 清除 | — | 路徑目前不存在（相對路徑的基準見權威檔 § 散布與搜尋順序） |

- `auto`、`none`、`inherit` 是保留字，不會是 adapter id（[methodology-adapters.md](methodology-adapters.md) § 描述檔格式 › 欄位表 `id`）。
- 層只有 [methodology-adapters.md](methodology-adapters.md) § 層次 的 5 個；`methodology_orchestration`、`methodology_testing` 這類鍵名走一般規則
  「選項名稱不存在 → 報錯，列出可用選項」。「編排」永遠屬於 CT，沒有對應的鍵。
- adapter 找不到或壞掉時**照存不擋**：adapter 可能之後才安裝，派工時該層照權威檔 § 降級 處理，不阻塞塔台。`*config` 只負責把問題提早說出來。
- 設定檔裡的 `methodology*` 值不合法（例：手改成 `methodology_delivery: inherit`）→ 啟動時警告，該鍵改用預設值，其他鍵照讀。

錯誤與警告訊息：

```
*config methodology_delivery inherit
❌ methodology_delivery 不接受 `inherit`。有效值：none / <adapter id>（預設 none）。設定未修改。

*config methodology_review PStack
❌ `PStack` 不是有效的 adapter id（只能用小寫英文、數字、-）。methodology_review 有效值：inherit / none / <adapter id>（預設 inherit）。設定未修改。

*config methodology_execution pstack
⚠️ methodology_execution = pstack（session）已設定，但目前找不到 adapter `pstack`
   （搜尋順序見 methodology-adapters.md § 散布與搜尋順序）。
   派工時該層依 methodology-adapters.md § 降級 處理，不阻塞塔台。
```

#### 檢視與寫入

- `*config methodology` 列出 9 個鍵的目前值與來源，並加一欄「解析結果」：`auto` 顯示偵測後的值，`inherit` 顯示跟到的主方法論，
  找不到的 adapter 標 ⚠️。這只是設定層的結果；每張工單實際用到哪幾層、哪個 workflow 要到派工時依 request_kind 決定。

  ```
  *config methodology

  ⚙️ 方法論設定（v6.0.0+）
  選項                         目前值     來源      解析結果
  methodology                  auto       預設      bmad（偵測到 bmad-guide）
  methodology_planning         inherit    預設      bmad
  methodology_execution        pstack     project   pstack
  methodology_review           inherit    預設      bmad
  methodology_verification     inherit    預設      bmad
  methodology_delivery         none       預設      none
  methodology_subagent_writes  deny       預設      deny
  methodology_guard            warn       預設      warn
  methodology_adapters_path    （空）     預設      （空）
  ```

- `*config methodology_<layer> <值>`、`--save project`／`--save global`、`*config reset <option>` 與其他選項相同（§ 寫入行為）：
  不帶 `--save` 只改 session；`--save` 只合併被改的那一個鍵（欄位級覆蓋），不會把其他 `methodology*` 鍵一起寫進去。
- 設定變更不影響**已派出**的工單。已建立但**尚未派出**（`PENDING`）的工單，派工前會依當下設定重新解析一次，有差異就在派工摘要列出、以新值為準
  （[methodology-adapters.md](methodology-adapters.md) § 解析步驟 › 何時解析）。

#### 解析例：三層疊加＋工單覆寫

規則照 [methodology-adapters.md](methodology-adapters.md) § 抽換（疊加層級、工單覆寫）、§ 解析步驟 第 2～4 步與 § 工單欄位（`resolved_from` 每層各記）：
每個鍵各自取最高優先層的值（session ＞ project ＞ global ＞ 預設），再套工單覆寫，全部疊完之後才把 `inherit` 換成主方法論、把 `auto` 換成偵測結果。
例中的 `team-x` 是假設的專案本地 adapter。

**設定層**（還沒套工單覆寫）：

| 鍵 | 預設 | global | project | session | 生效值（來源） |
|---|---|---|---|---|---|
| `methodology` | `auto` | `bmad` | `pstack` | `team-x`（`*config methodology team-x`） | `team-x`（session） |
| `methodology_planning` | `inherit` | — | `bmad` | — | `bmad`（project） |
| `methodology_execution` | `inherit` | — | — | — | `inherit` → `team-x`（session） |
| `methodology_review` | `inherit` | — | — | — | `inherit` → `team-x`（session） |
| `methodology_verification` | `inherit` | — | — | — | `inherit` → `team-x`（session） |
| `methodology_delivery` | `none` | — | — | — | `none`（預設） |
| `methodology_subagent_writes` | `deny` | — | — | — | `deny`（預設） |
| `methodology_guard` | `warn` | `block` | — | — | `block`（global） |
| `methodology_adapters_path` | 空 | — | — | — | 空（預設） |

- **沒有工單覆寫的工單**：規劃層 `bmad`（project 明寫），其餘層 `team-x`（session）。
- **下一個 session**：session 值沒存檔，主方法論回到 `pstack`（project），`inherit` 的層跟著變成 `pstack`；規劃層仍是 `bmad`。

**工單覆寫**（同一份設定下的三張工單）：

| 工單 | 使用者說 | 本單用到的層 → 生效 adapter（`resolved_from`） |
|---|---|---|
| T0123 feature | 「T0123 這張用 pstack 做」（整張覆寫） | planning → `pstack`（workorder）、execution → `pstack`（workorder）、review → `pstack`（workorder） |
| T0124 bugfix | 「T0124 審查用 bmad」（指定層覆寫） | execution → `team-x`（session）、review → `bmad`（workorder） |
| T0125 bugfix | 「T0125 用 pstack 做，審查用 bmad」（兩種並用） | execution → `pstack`（workorder）、review → `bmad`（workorder） |

- **整張覆寫蓋過層設定**：T0123 的規劃層是 `pstack`，不是 project 明寫的 `bmad`。交付層不在整張覆寫內，仍是 `none`。
- **混合來源每層各記**：T0124 的兩層來源不同，frontmatter 寫成：

  ```yaml
  methodology:
    request_kind: bugfix
    resolved_from:
      execution: session
      review: workorder
    layers:
      execution:
        adapter: team-x
        workflow: <team-x adapter 的 routing.bugfix.execution>
      review:
        adapter: bmad
        workflow: bmad-code-review
  ```

- **派工前重新解析**：T0124 建好還沒派，使用者改了 `*config methodology_execution pstack` → 派工前重算，執行層 `team-x` → `pstack`（來源 session），
  派工摘要列出這個差異；審查層是工單覆寫，保留 `bmad`。T0124 派出之後再改設定，就不再影響它。
- 三張都不改設定檔。

## 作用域與持久化

### 三層設定架構

```
session（記憶體，最高優先）
  ↑ 覆蓋
project — Layer 3（_ct-workorders/_tower-config.yaml）
  ↑ 覆蓋
global — Layer 2（${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/config.yaml）
  ↑ 覆蓋
預設值（tower-config.md § 可用選項的「預設」欄 — Layer 1）
```

> `methodology*` 鍵在 session 之上還有一層「工單覆寫」：使用者只對單張工單指定方法論（整張或指定層），塔台寫進該工單、不改任何設定檔
> （[methodology-adapters.md](methodology-adapters.md) § 抽換；例見 § 方法論設定鍵 › 解析例）。其他選項沒有這一層。

> **路徑**：Layer 2 一律是 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/`（設了 `CLAUDE_CONFIG_DIR` 就在它底下，否則 `~/.claude`；P-3，T0314）。
> 本檔與其他 CT 檔寫 `~/.claude/control-tower-data/` 時都照這條解讀；權威見 [data-layer-architecture.md](data-layer-architecture.md) § 架構總覽 › 路徑解析。

> **遷移注意**：全局設定從 `~/.claude/control-tower-config.yaml` 遷入
> `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/config.yaml`（Layer 2）。過渡期兩個路徑均可讀取，
> 新路徑優先。詳見 [data-layer-architecture.md](data-layer-architecture.md) 遷移指南。

### 持久化檔案格式

```yaml
# _ct-workorders/_tower-config.yaml（Layer 3）或 ${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/config.yaml（Layer 2）
control-tower:
  alignment-rounds: 3
  interactive-prompts: on
  experience-level: standard
  verbose: on
  # v4 多單據類型（v6 起預設開啟；不想用時寫 false）
  enable_bug_tracking: true
  enable_plan_tracking: true
  enable_experiments: true
  # v4 歸檔系統
  archive_days: 7
  auto_archive_prompt: off
  # v6.0.0-beta.3+ 未結 BUG 清理提示門檻（0 = 停用該條件）
  bug_review_open_threshold: 20
  bug_review_stale_days: 30
  # v6.0.0-beta.3+ 客戶驗收不回歸閘（可選；專案進入客戶驗收才開）
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
  # v6.0.0+：方法論轉接（語意見 methodology-adapters.md § 抽換）
  # 不設定 = auto = 現行行為（與 v5.12.6 相同）；整組可以不寫，只寫與上一層不同的鍵
  methodology: auto                  # auto / none / <adapter id>
  methodology_planning: inherit      # inherit / none / <adapter id>
  methodology_execution: inherit
  methodology_review: inherit
  methodology_verification: inherit
  methodology_delivery: none         # none / <adapter id>
  methodology_subagent_writes: deny  # deny / per-workorder
  methodology_guard: warn            # warn / block / off
  methodology_adapters_path: ""      # 空 = 不加額外搜尋路徑
```

### 啟動時載入流程

1. 讀取預設值（本檔 § 可用選項的「預設」欄 — Layer 1）
2. 讀取 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/config.yaml`（global — Layer 2），覆蓋預設
   - 若不存在，降級讀取 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-config.yaml`（舊路徑，過渡期相容）
3. 讀取 `_ct-workorders/_tower-config.yaml`（project — Layer 3），覆蓋 global
4. Session 設定（`*config` 即時修改）覆蓋一切

### 寫入行為

- `--save project`：讀取現有 `_ct-workorders/_tower-config.yaml`，合併修改項，寫回
- `--save global`：讀取現有 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/config.yaml`（Layer 2），合併修改項，寫回
- 不帶 `--save`：僅修改 session 記憶體，session 結束即失效
- `auto-session`（v5.2.0+）：修改後若生效值改變且在 BAT 內，要用新的 `--mode` 再宣告一次塔台分頁角色，見 [auto-session.md](auto-session.md) § 塔台分頁角色宣告

### 驗證規則

- 值不在有效範圍內 → 報錯，不修改
- 選項名稱不存在 → 報錯，列出可用選項
- 設定檔語法錯誤 → 警告，使用預設值
- `methodology*` 9 個鍵另有逐鍵規則（關鍵字、adapter id 格式、找不到 adapter 照存但警告），見 § 方法論設定鍵 › 值的驗證

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
| `workflow` | ct-help 工作流程速查 | 日常開發、中斷恢復、迭代結束 |
| `config` | 本檔案 *config 段落 | 設定選項和持久化 |
| `workorder` | work-order-system.md 摘要 | 工單生命週期和狀態流轉 |
| `status` | ct-help 紀錄保存位置 | 紀錄在哪裡、持久性 |
| `tips` | ct-help 溝通技巧 | 如何表達需求、確認理解 |
| `methodology` | ct-help § Methodology Adapters | v6.0.0+：adapter 是什麼、怎麼看與改方法論設定 |

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

   可用主題：commands · workflow · config · workorder · status · tips · methodology
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
