# YOLO 模式規格

> `auto-session: yolo` 的完整行為規格。
>
> **核心概念**：`on` 超集 = Worker 自動送出 + 塔台自主決策下一張 + 斷點安全閘（A / B / C；v5.3.0+ 加 E 合併前確認；v5.5.0+ 加 D Worker 等待使用者）。
> v5.5.0+ yolo Worker 有問題時向塔台提問、由塔台代決，見 § Worker 向塔台提問。
>
> **前置**：需 BAT ≥ PLAN-020 W1（`bat-notify.mjs --submit` 支援）、Worker skill `ct-exec` / `ct-done` ≥ v4.2.0（本 release）。
>
> **姊妹文件**：[auto-session.md](auto-session.md) § `auto-session = yolo`、`ct-exec/SKILL.md` § BAT Notify And Fallback、`ct-done/SKILL.md` § BAT Notify。

## BAT env 分工（D004）

Tower dispatch required env：

- `BAT_SESSION=1`
- `BAT_REMOTE_PORT`
- `BAT_REMOTE_TOKEN`
- `BAT_TERMINAL_ID`
- `BAT_WORKSPACE_ID`

Worker notify required env：

- `BAT_TOWER_TERMINAL_ID`
- `BAT_REMOTE_PORT`
- `BAT_REMOTE_TOKEN`

Tower session 不需要預先具備 `BAT_TOWER_TERMINAL_ID`。Tower 派發時必須把自己的 `BAT_TERMINAL_ID` 傳給 `bat-terminal.mjs --notify-id`；BAT 會把該值注入 Worker 的 `BAT_TOWER_TERMINAL_ID`，Worker 完成後再用 `bat-notify.mjs --target "$BAT_TOWER_TERMINAL_ID"` 回報 Tower。

環境有 `BAT_TOWER_TERMINAL_ID` 就是 Worker 分頁；在 Worker 分頁不能當塔台派工。判定與失敗處理見 [auto-session.md](auto-session.md) § BAT 內部終端路由 › 範圍權杖與分頁角色。

BAT helper 路徑優先使用 `BAT_HELPER_DIR`：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" --cwd "<專案根目錄>" --mode yolo --agent default --skill ct-exec --workorder T####
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-notify.mjs" --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" --submit "<工單 ID> 完成"
```

`--workorder` 與 `--source` 都用工單完整 ID；Worker 端 `<工單 ID>` 的寫法與送出前比對見 [work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID。

v5.6.0+ 派工另在最後加 `--wait-started 30000`（本塔台 session 未判定不支援時）；exit `8` 不重派、`started: unknown` 不是失敗，規則見 [auto-session.md](auto-session.md) § Worker 啟動確認。exit `8` 不是 yolo 斷點。

若 `BAT_HELPER_DIR` 未設定，fallback 到 `C:\Program Files\BetterAgentTerminal\resources\scripts\*.mjs`。Windows 路徑不可改成 `/c/...` POSIX 形式。`"${BAT_HELPER_NODE:-node}"` 的解析規則（含 PowerShell 寫法）見 [auto-session.md](auto-session.md) § 執行方式 的「Node 解析」。

若目前 shell 看不到 `BAT_*`，Windows 上需用 native PowerShell 複查（只列名稱）`Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object`；偵測只判斷有無、不輸出值，`BAT_REMOTE_TOKEN` 只記「已設定」（唯一權威：[auto-session.md](auto-session.md) § 偵測條件）。PowerShell 可見但 helper shell 不可見時，標記為 `shell env visibility mismatch`，不得誤判為非 BAT。

## 啟動識別

塔台啟動時（Step 0 環境偵測完成後），讀取 `auto-session` 設定：

- 值為 `yolo` → 進入 yolo 模式
- 其他值 → 走現有 on/ask/off 流程

在 BAT 內，塔台啟動與 `*config auto-session <m>` 改變生效值時都要以 `--set-role tower --mode <m>` 宣告（v5.2.0+；BAT 據此判斷塔台分頁是否為 yolo 分頁），見 [auto-session.md](auto-session.md) § 塔台分頁角色宣告。

### 啟動面板警語

yolo 模式開啟時，塔台主面板（[memory-protocol.md](memory-protocol.md) § 塔台狀態面板）**下方必須**顯示：

```
╠═══════════════════════════════════════════════════════╣
║ ⚠️  YOLO MODE ACTIVE — 塔台將自主決策                  ║
║  斷點條件：A 非預期狀態 / B Renew≥N 或 N 連續 FAILED / C 跨 PLAN / D Worker 等待使用者 / E 合併前確認  ║
║  Worker 提問：問塔台（等待上限 <M> 分鐘）              ║
║  關閉：*config auto-session on                        ║
╠═══════════════════════════════════════════════════════╣
```

其中 `N` 為 `yolo_max_retries` config 值（有效值與預設見 [tower-config.md](tower-config.md) § 可用選項）。

若 `yolo_max_retries = 0` → 啟動面板警語中斷點 B 行改為「B 已停用」。

`Worker 提問` 欄位（v5.5.0+）：yolo Worker 一律向塔台提問，不向使用者提問（見 § Worker 向塔台提問）；`<M>` 為 `worker_question_timeout` config 值（有效值與預設見 [tower-config.md](tower-config.md) § 可用選項），`0` 時改為「問塔台（不等待，直接 BLOCKED）」。

斷點列的 `E 合併前確認`（v5.3.0+）一律顯示；不使用 worktree 隔離的專案不會觸發它，見下方 § 斷點 E。
斷點列的 `D Worker 等待使用者`（v5.5.0+）一律顯示；BAT MCP 不可用或 BAT 太舊時不會觸發它，見下方 § 斷點 D。

**使用者中斷快捷**：yolo 啟用期間，使用者**隨時**輸入 `停` / `stop` / `abort`（獨立詞，regex `^(停|stop|abort)$` case-insensitive）可觸發**使用者中斷**（獨立於斷點 A/B/C/D/E，不佔用 `yolo_max_retries` 配額）。詳見下方「使用者中斷（非斷點）」小節。

### 啟動詢問（G3 互動旗標）

> v5.5.0 起 yolo **不再詢問** G3。v4.3.0 起到 v5.5.0 之前，G3 只在 yolo 啟動時問「是否允許 Worker 在研究型工單中向你提問」；
> v5.5.0 起 yolo 下研究型工單的提問也一律走 § Worker 向塔台提問（問塔台，不問使用者），這個問題已無選項可選。

- yolo 派工一律帶 `--no-interactive`（對應 `CT_INTERACTIVE=0`：Worker 不得向使用者提問）。塔台 session 記憶體變數 `session.allow_worker_interactive` 停用。
- yolo 派工**不得**帶 `--interactive`。使用者在 yolo 下要求允許 Worker 向自己提問時，告知做法：改 `*config auto-session on`（或 `ask` / `off`）後派工，
  非 yolo 的互動旗標照 [auto-session.md](auto-session.md) § Mode 與互動旗標協定 與 config `research_interaction` 決定。
- 舊塔台（`< v5.5.0`）派出、帶 `--interactive` 的 yolo Worker：Worker 端仍以 `CT_MODE=yolo` 為準走提問通道（見 `ct-exec/SKILL.md` § Mode And Environment）。
- 非 yolo（`on` / `ask` / `off`）的派工與 Worker 互動行為不變。

### Banner 設計（Worker 端顯示，AC-NEW-4）

Worker skill `/ct-exec` 啟動時若偵測到 `CT_MODE=yolo`（塔台派發時注入），在任何流程開始前顯示醒目 banner：

```
╔══════════════════════════════════════════════════════════════╗
║  🚨  YOLO MODE ACTIVE  🚨                                    ║
║                                                              ║
║  Worker 將自動送出完成訊息給塔台；塔台將自動決策下一張工單。 ║
║  使用者可隨時輸入「停」中斷自動派發。                        ║
╚══════════════════════════════════════════════════════════════╝
```

Banner 特徵：
- 🚨 雙側警示 emoji（頭尾各一）
- 標題「YOLO MODE ACTIVE」置中
- 雙行文案說明：(1) Worker 自動送出 + 塔台自主決策 (2) 使用者中斷快捷
- 雙線框線（`╔══...══╗`）作為視覺分隔

**與降級提示互斥**：
- `CT_MODE=yolo` → 顯示此 banner
- `CT_MODE` 未設 / 不合法 → 顯示「⚠️ 塔台未傳 `--mode` flag，降級為 ask 模式」提示
- 兩者**不同時出現**

詳細 Worker 側讀取規則見 `ct-exec/SKILL.md` § 讀取 CT_MODE env。

### 派發下一張時的回報面板

塔台自動派發下一張工單前，顯示：

```
🤖 YOLO: T0xxx DONE → 自動派發下一張 T0xxy
   依據：<研究工單 T0xxx-R 的 D 區段第 N 列>
   斷點計數：Renew 0 / FAILED 0 / N
   模式：--mode yolo | 互動：問塔台（--no-interactive）
   [Ctrl+C 中斷 / *pause 手動介入]
```

**派發面板新增欄位**（v4.3.0+，AC-NEW-5）：
- `模式`：顯示當前派發指令會帶的 `--mode` 值（yolo/ask/off/on），讓使用者 session 內即時看到將傳給 Worker 的模式
- `互動`：v5.5.0+ yolo 固定為「問塔台（`--no-interactive`）」（見上方 § 啟動詢問（G3 互動旗標））；v5.5.0 之前反映 G3 結果

**1-2 秒視覺緩衝**：塔台顯示上述面板後，強制等待 1-2 秒再執行實際派發動作，給使用者中斷時機（Ctrl+C 或 `*pause`）。

---

## 下一張工單判定邏輯（Q2.A 分支）

### 資訊來源

1. **當前活躍 PLAN**：從 `_tower-state.md` 讀取「本 Session 焦點」或「進度快照」段落
2. **該 PLAN 對應的研究工單**：工單元資料 `關聯 PLAN: PLAN-0XX` + `關聯研究: T0XXX`，或從 PLAN 檔案反查
3. **研究工單回報區 D 區段**：結構化 markdown 表格（拆單建議）
4. **現有熱區工單狀態**：Glob `_ct-workorders/T*.md` + parse 元資料的「狀態」欄位

### D 區段 parse 規則

塔台從研究工單回報區尋找以下 section heading 之一（優先序）：

1. `### 拆單建議摘要` 或 `### 拆單總表`
2. `### D. 拆單建議` 或 `### D 區段` 等 D 前綴章節
3. `## D. 實作工單拆單建議` 等 H2 D 前綴章節

在該 section 下，尋找**第一個符合格式的 markdown 表格**，預期格式：

```markdown
| # | 標題 | 專案 | 依賴 | 工時 | 🚦 |
|---|------|------|------|------|-----|
| 1 | BAT code: xxx | 本專案 | — | 1h | 🟢 |
| 2 | 本地草稿: yyy | 本專案 | 工單 1 | 1.5h | 🟢 |
| ... |
```

**關鍵欄位必須存在**（缺任一即視為格式不符）：
- `#`（編號欄，接受 `工單` 前綴，如「工單 1」）
- `標題`
- `依賴`（`—` / `-` / 空字串表示無依賴）

### 判定邏輯（機械化，偽碼）

```
on_worker_report_done(T_done):
  1. workorder = read_file(T_done)
  2. plan = parse_metadata(workorder, "關聯 PLAN")
  3. research = parse_metadata(workorder, "關聯研究")
  4. if plan is None or research is None:
        → 斷點 A（無 PLAN/research 綁定，無法自主決策）
  5. d_section = extract_d_section(read_file(research))
  6. if d_section is None:
        → 斷點 A（研究工單無 D 區段）
  7. table = parse_markdown_table(d_section)
  8. if table is None or not has_required_columns(table):
        → 斷點 A（表格格式不符）
  9. for row in table:
       if dependencies_all_done(row.依賴) and not dispatched(row.標題):
         if has_concrete_T_number(row.標題):
           → 派發該工單
         else:
           → 斷點 A（占位符，需使用者補 T####）
  10. 若所有列都完成或已派發 → 顯示「PLAN 完成」+ 結束 yolo
```

### Fallback 路徑（觸發斷點 A）

| 情境 | 訊息 |
|------|------|
| 找不到研究工單 | `⏸ YOLO PAUSED — 工單 T#### 無關聯研究工單` |
| 研究工單無 D 區段 | `⏸ YOLO PAUSED — T####-R 無 D 區段` |
| D 區段無表格或格式不符 | `⏸ YOLO PAUSED — D 區段表格格式不符` |
| 列中無具體 T#### | `⏸ YOLO PAUSED — 下一列為占位符，需補 T####` |
| 所有列都完成 | `✅ PLAN-0XX 所有工單完成 → yolo 流程結束` |

---

## 斷點判準（A / B / C / D / E）

> v4.2.0 起為 A / B / C 三個斷點；v5.3.0 加入斷點 E（合併前確認）；v5.5.0 加入斷點 D（Worker 等待使用者）。

### 斷點 A：Worker 回報非預期狀態

**判準（機械化 regex）**：

Worker 收尾訊息必須**精準匹配**以下 regex：

```regex
^<WORKORDER_ID>\s+(完成|部分完成|需要協助|提問|失敗)\s*$
```

`<WORKORDER_ID>` 是 [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義）
所定義的具名片段，**套用時展開為該處的值，本節不複述**。
⚠️ 它涵蓋帶前綴的工單 ID：`CP-T0113 完成` 是合法回報，不得判為斷點 A。

對應的合法字串（與 `ct-exec` § BAT Notify And Fallback、`ct-done` § BAT Notify 鎖定一致）（`<工單 ID>` = 工單完整 ID，含前綴、不得截短，規則見 [work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID）：

| Worker 狀態 | 通知字串 |
|------------|---------|
| `DONE` / `FIXED` | `<工單 ID> 完成` |
| `PARTIAL` | `<工單 ID> 部分完成` |
| `FAILED` | `<工單 ID> 需要協助` |
| `BLOCKED` | `<工單 ID> 需要協助` |
| `IN_PROGRESS`，有待塔台決策的問題（v5.5.0+，只有 `ct-exec`） | `<工單 ID> 提問` |

例：`LB-T0184 完成`、`T0341 部分完成`。收到缺前綴的 ID（`T0184 完成`，熱區只有 `LB-T0184`）時符合本 regex，不是斷點 A；
對工單照 [work-order-system.md](work-order-system.md) § 回報處理流程 › 回報 ID 對不上時（多張同號或找不到才屬斷點 A）。

**注意**：`失敗` 也列入合法字串以容錯，但實際 Worker skill 鎖定收尾映射為「完成/部分完成/需要協助」（`失敗` 與 `需要協助` 語意皆為需介入）。

`T#### 提問`（v5.5.0+）不是收尾訊息：工單仍在執行，塔台**不收單**，改照 § Worker 向塔台提問 › 塔台端 處理。
`ct-done` 是補救收尾，不會送 `提問`。

不匹配 → 斷點 A 觸發。

**觸發後塔台動作**：

```
⏸ YOLO PAUSED — 斷點 A 觸發
  Worker 回報：<原文（保留引號）>
  可能原因：Worker skill 版本舊 / 字串未遵循規格 / 非預期語氣
  選項：
    [A] 接受為 DONE（語意清楚，續派下一張）
    [B] 接受為 FAILED（計入斷點 B 計數）
    [C] 退回 yolo → ask 模式，手動接手
  請輸入 A/B/C：
```

---

### 斷點 B：Renew ≥N 或連續 N FAILED

N = `yolo_max_retries` config 值（有效值與預設見 [tower-config.md](tower-config.md) § 可用選項）。

#### B-1：Renew 過多

**判準**：讀取被回報工單元資料的 `Renew 次數` 欄位，若 ≥N → 斷點 B-1。

**觸發訊息**：

```
⏸ YOLO PAUSED — 斷點 B-1
  工單 T#### Renew 次數：N 次（超過閾值 N）
  建議：拆成新工單，避免同工單反覆迭代
  選項：
    [A] 接受此工單為 DONE 並繼續 yolo
    [B] 塔台協助拆新工單（暫停 yolo，進入對齊）
    [C] 退回 yolo → ask 模式
  請輸入 A/B/C：
```

#### B-2：連續 N FAILED

**判準**：塔台 session 級計數器（記在 `_tower-state.md` 的 `## YOLO 歷程` › `### 計數器`，格式見下方 § YOLO 計數器），規則：

- Worker 回報 `FAILED` / `BLOCKED` → 計數器 +1
- Worker 回報 `DONE` / `FIXED` / `PARTIAL` → 計數器歸零
- 計數器達 N → 斷點 B-2

##### YOLO 計數器

斷點 B-2 用的連續 FAILED 計數器，計數規則就是上方 B-2 的判準。記在 `_tower-state.md` 的 `## YOLO 歷程` › `### 計數器`（v5.12.4 起統一為這個位置，
沒有獨立的 `## YOLO 計數器` 區段；同一段其他列的格式見下方 § `_tower-state.md` 新增 `## YOLO 歷程` 區段），格式：

```markdown
## YOLO 歷程

### 計數器

- 連續 FAILED: 2 / 3
- 最近 FAILED 工單: T####, T####
- 最後更新：2026-04-18 14:23
```

**觸發訊息**：

```
⏸ YOLO PAUSED — 斷點 B-2
  連續 FAILED 計數：N / N（達上限）
  最近失敗工單：T####, T####, T####
  建議：yolo 自動暫停，檢查是否需調整 PLAN 或研究結論
  選項：
    [A] 重置計數器並續跑（risky）
    [B] 暫停 yolo，手動診斷
    [C] 退回 yolo → ask 模式
  請輸入 A/B/C：
```

---

### 斷點 C：Worker 建議跨出 PLAN 範圍

**判準**：Worker 回報區（「Worker 筆記」或「下一步建議」段落）若出現**跨出當前 PLAN 拆單表**的建議。

**偵測 regex**（二擇一觸發）：

```regex
(?:另開|新開|建議.*派|建議.*開)\s*(?:工單|研究|PLAN|BUG)
```

```regex
\b(<WORKORDER_ID>|PLAN-\d{3}|BUG-\d{3}|EXP-[A-Z]+-\d{3})\b
```

（第二條用於偵測 Worker 提到新編號；塔台比對是否為當前 PLAN 拆單表中的工單。
`<WORKORDER_ID>` 同上，展開自 [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義），
因此帶前綴的新編號同樣會被偵測到）

**觸發後塔台動作**：

```
⏸ YOLO PAUSED — 斷點 C 觸發
  Worker 建議（引用原文）：
  > <引用 Worker 筆記中匹配 regex 的段落>

  這個建議在當前 PLAN-0XX 拆單表外。
  選項：
    [A] 擴大當前 PLAN（將新發現納入 D 區段表格）
    [B] 開新 PLAN 處理此發現
    [C] 忽略此建議，繼續 yolo 流程（依原 D 區段派下一張）
  請輸入 A/B/C：
```

---

### 斷點 D：Worker 等待使用者（v5.5.0+）

> 本小節是斷點 D 的**唯一權威定義**。MCP tool 與回傳欄位見 [auto-session.md](auto-session.md) § BAT MCP 唯讀 tool；
> BAT 端契約以 BAT `CLAUDE.md`「blocked 狀態偵測（PLAN-047 M1b / T0590）」節與 `docs/agent-guide/blocked-state.md` 為準（CT-T017 § 二），
> codex 分頁（`blockedDetection: osc`，v5.8.0+）另以 BAT T0621「介面契約」C-1–C-8 與 `blocked-state.md`「codex（OSC 7501）」節為準（CT-T020），
> CT 不得更改欄位名或列舉值。

**判準**：塔台查到某個 Worker 分頁 `state == blocked`（MCP `bat_get_state` / `bat_list_terminals` / `bat_wait`，BAT `>= 0.7.0-pre.4`），
且 `blockedReason` 是下列**等使用者的 reason** 之一：

- hook 的三種 reason（`permission` / `question` / `elicitation`；`source: 'hook'`，`blockedDetection: hook` 的 claude-cli Worker）；
- `input`（v5.8.0+；`source: 'osc'`，`blockedDetection: osc` 的 codex Worker；BAT 需 `>= 0.7.0-pre.9`）：
  codex 在等使用者——核准提示、Plan mode 提問等，OSC 7501 不分種類。處理與 hook 的三種 reason 相同（見下方 **處理**、**共同**）。

**`blockedReason: tower` 不是斷點 D**（v5.7.0+，BAT `>= 0.7.0-pre.7`）：Worker 在等**塔台**答覆它經 BAT 通道問的題目，不是在等使用者。
不告知使用者「在等你回答」、不寫 `[斷點 D]`；改照 § Worker 向塔台提問 › 塔台端 讀題並答覆（沒收到 `提問` 通知也一樣）。
它由 BAT 自己的問答紀錄判斷、不靠 hook，與 `blockedDetection` 無關（codex Worker 也會回）。
BAT 的優先序是 `exited` > hook 的三種 reason／`input` > `tower` > `working` / `idle`（`input` 與 hook 的 reason 不會同時出現在同一分頁）：
Worker 同時在等使用者時會回等使用者的 reason，照本節處理。

**啟用條件**（以下只對等使用者的 reason）：

- 只走 MCP，沒有對應的 helper CLI。MCP tool 不存在或不可用、或回傳**沒有** `blockedDetection` 欄位（舊 BAT）→ 斷點 D 不啟用，
  維持現行判斷（工單回報區、Worker 輸出、等待時間）。
- `blockedDetection: none`（codex 低於 `0.163.0` 或 BAT 確認不到版本的 codex Worker、舊 BAT 上的 codex Worker（見已知限制第 1 點）、
  Settings 關閉 BAT MCP、自訂參數已含 `--settings`、raw command 派工…）→ 這個分頁永遠不會回 hook 的三種 reason，也不會回 `input`
  （BAT `>= 0.7.0-pre.7` 仍可能回 `blocked` / `tower`，照上一段處理），維持現行判斷；**不得把 `idle` 解讀為沒有在等人**。
  （v5.5.0～v5.6.1 寫作「永遠不會回 `blocked`」，BAT T0607 起改為不會回 hook 的三種 reason；v5.8.0 依 BAT T0621 C-1 補上 `input`。）
- `blockedDetection: hook` → hook 的三種 reason 可信，照本節處理。
- `blockedDetection: osc`（v5.8.0+）→ `input` 可信，照本節處理。

**何時查**：不新增輪詢、不開背景監看。只在塔台本來就在看某個 Worker 時順便看 `state`：

- 使用者問進度；
- 等 Worker 回報等到要判斷它是否卡住；
- Renew 或重派之前。

`bat_wait` 的 `until: 'idle'` 以「不是 `working`」判斷，`blocked` 也會返回：返回後看 `state` 與 `blockedReason`，等使用者的 reason 照本節處理、
`tower` 照上方，不得當成 Worker 已閒置或已完成。

**處理**：

- **yolo**：異常偵測。yolo Worker 有問題應向塔台提問（§ Worker 向塔台提問），不應停在等使用者；仍是 `blocked`，
  代表它違規使用了提問工具（例 AskUserQuestion）、遇到 MCP 表單（elicitation）或權限提示；codex Worker 的 `input` 代表遇到核准提示或提問
  （以 `--yolo` 啟動的 codex 回合中幾乎不會出現，BAT T0619）。塔台用分頁標題告訴使用者（訊息見下），
  並寫 YOLO 歷程 `[斷點 D]`；**不暫停**其他流程（其他工單照常派發、收單），那張單本來就在等它的 Worker 回報。
- **非 yolo（`on` / `ask` / `off`）**：告知型。同樣告訴使用者，不另加異常判斷。

**共同**：

- 🔴 塔台**不代答、不送按鍵、不對 Worker 分頁寫入任何輸入**；請使用者自己到該分頁處理。
- `blocked` 不算卡住或失敗：不重派、不 Renew、不計入 `yolo_max_retries`（斷點 B-1 / B-2）與連續 FAILED。
- 同一次 `blocked`（同一個 `blockedSince`）只告知一次，不重複催促；`blockedSince` 改變（新的一次等待）才再告知。

**訊息**（`<分頁標題>` 依 [auto-session.md](auto-session.md) § 對使用者描述分頁；`blockedSince` 是 ms，換成本地時間顯示）：

```
⚠️ YOLO 斷點 D（不暫停）— <分頁標題> 在等你回答（原因：<blockedReason>，從 HH:MM 起）
   工單：T####　請到該分頁處理；塔台不會代答。
   yolo Worker 不應等使用者（應向塔台提問），已記入 YOLO 歷程；其他流程照常進行。
```

非 yolo 為 `ℹ️ 斷點 D — <分頁標題> 在等你回答（原因：<blockedReason>，從 HH:MM 起）`，第二行相同，沒有第三行。

- 措辭一律中性：`<blockedReason>` 照原值顯示，**不得**依它斷定「是權限確認」或「是提問」。

**`blockedReason` 的值**（BAT 權威）：`permission`（權限確認）/ `question`（AskUserQuestion）/ `elicitation`（MCP 表單）；
BAT `>= 0.7.0-pre.7` 另有 `tower`（`source: 'question'`，不是斷點 D，見上方）；
BAT `>= 0.7.0-pre.9` 另有 `input`（v5.8.0+，`source: 'osc'`，codex `>= 0.163.0`；核准提示、Plan mode 提問、elicitation 都是 `input`，
不分種類，所以訊息照原值顯示 `input`，同樣不得斷定是哪一種）。

- BAT `0.7.0-pre.4`（BUG-150 修正前）：claude-cli 的 AskUserQuestion 一律回報 `permission`（任何權限模式，含 `--dangerously-skip-permissions`）；
  `question` 只維持約 90 ms，塔台實際讀不到。
- BAT `>= 0.7.0-pre.5`（BUG-150 修正後）：AskUserQuestion 回報 `question`；契約欄位與列舉值不變。
- 修正前後都照原值顯示、措辭都中性，塔台邏輯不變。

**清除**（BAT 權威）：hook 的三種 reason 在使用者送出下一則 prompt、回合結束（`Stop`）、使用者在該分頁鍵盤輸入、分頁結束時清除；AskUserQuestion 回答完成只清 `question`。

- BAT `0.7.0-pre.4`（BUG-150 修正前）：AskUserQuestion 以滑鼠回答後**不會**清除，`blocked` 維持到該回合 `Stop`。
- BAT `>= 0.7.0-pre.5`（BUG-150 修正後）：AskUserQuestion 以滑鼠或鍵盤回答後由 `PostToolUse` 立即清除，不必等 `Stop`。
- 修正前後都一樣：權限對話框以滑鼠允許／拒絕、elicitation 以滑鼠回答或逾時關閉 → `blocked` 維持到該回合 `Stop`（或使用者鍵盤輸入）。
- 所以使用者回答後到該回合結束前，仍可能讀到同一個 `blockedSince` 的 `blocked`：照上方「只告知一次」，不重複催促。
- `tower`（BAT `>= 0.7.0-pre.7`）：答覆、取消、過期、Worker 或塔台分頁結束、Terminal Server recovery 時清除；使用者在 Worker 分頁輸入**不清除**。
- `input`（v5.8.0+，BAT T0621 C-2）：codex 自己送轉換（OSC 7501 `state=working` / `idle` / `clear`）、PTY 結束（exit / kill / restart）、
  Terminal Server recovery 時清除；🔴 使用者在該分頁的輸入**不清除**（與 hook 的三種 reason 不同，由 codex 自己送轉換）。
  所以使用者已在分頁處理、但 codex 還沒送轉換時，塔台仍可能讀到同一個 `blockedSince` 的 `input`：照上方「只告知一次」，不重複催促，
  也不據此判定 Worker 卡住或使用者沒處理；`blockedSince` 改變才是新的一次等待。

**已知限制**（CT-T017 § 二，第 3 點依 BAT T0596 / T0597 改寫；第 5 點 v5.5.1 依 BAT `docs/agent-guide/blocked-state.md` 補；第 4 點 v5.6.0 依 BAT T0600 改寫；
第 1 點 v5.8.0 依 BAT T0621 改寫、第 5 點補 codex、第 6 點 v5.8.0 依 BAT T0621 補）：

1. hook 的三種 reason 只有 claude-cli Worker 支援（`blockedDetection: hook`）。codex Worker（v5.8.0+）依 codex 與 BAT 版本而定：
   - codex `>= 0.163.0`，且 BAT `>= 0.7.0-pre.9` → `blockedDetection: osc`，可能回 `input`（照本節處理）；
   - codex 低於 `0.163.0`、BAT 確認不到版本（例如 Windows 上 PATH 第一個是 npm shim `codex.cmd`）、或舊 BAT（≤ `0.7.0-pre.8`）
     → `blockedDetection: none`，照上方 `none` 的規則（現行降級不變，與 v5.7.2 相同）。BAT 觀察到 OSC 7501 後會把 `none` 改為 `osc`，
     所以同一分頁可能由 `none` 變 `osc`：每次照當下回傳的 `blockedDetection` 判斷。
   - `hook` 分頁不會因輸出出現 OSC 7501 而變成 `osc`。`tower` 不在此限（與 `blockedDetection` 無關）。
2. 權限對話框以滑鼠允許／拒絕、elicitation 以滑鼠回答或逾時關閉：`blocked` 維持到該回合 `Stop` 或使用者鍵盤輸入。
3. 以 `--dangerously-skip-permissions` 啟動的 Worker（本機 CT yolo Worker 的自訂參數）沒有一般工具的權限提示，
   但「不會出現 `permission`」在 BUG-150 修正前**不成立**：AskUserQuestion 仍回報 `permission`。BAT `>= 0.7.0-pre.5` 起 AskUserQuestion 回報 `question`；
   bypass 下的 `permission` 仍可能來自其他需要使用者互動的工具（例 ExitPlanMode；BAT 依二進位推論、未實測）。
4. claude 設定關閉 hooks（`disableAllHooks: true`，或 managed settings 的 `allowManagedHooksOnly`）時 BAT hooks 不執行：
   - BAT `>= 0.7.0-pre.6`：BAT 啟動 Worker 時讀 claude 的 managed 設定檔與使用者設定檔（`$CLAUDE_CONFIG_DIR/settings.json`，否則 `~/.claude/settings.json`），
     managed 有 `allowManagedHooksOnly: true`，或第一個設了 `disableAllHooks` 的檔案（managed 優先）為 `true` → 回 `blockedDetection: none`，
     斷點 D 照上方 `none` 的規則處理（維持現行判斷，不把 `idle` 解讀為沒有在等人）。讀不到的層級（專案設定 `<cwd>/.claude/settings[.local].json`、MDM／server-managed policy 等）
     仍是 `hook`，但不會有事件，等於偵測不到。
   - BAT `< 0.7.0-pre.6`：`blockedDetection` 仍是 `hook`，但不會有事件，等於偵測不到。
5. BAT 重開或 headless server 重啟後，重開前的 `blocked` / `blockedDetection` 會遺失（BAT 重開時分頁還原會以當下設定重新記錄
   `blockedDetection`；headless server 重啟則全部遺失），所以重開前那一次等待可能漏報；細節以 BAT 權威為準。
   codex 分頁（`osc`，v5.8.0+）在 BAT 重開、Terminal Server 存活時，BAT 由重播內容補掃最後一個 OSC 7501 恢復 `osc` 與 `input`（BAT T0621 C-7）。
6. codex 的 `input`（v5.8.0+）不分核准提示／Plan mode 提問／elicitation；codex 卡在啟動前畫面（「Trust this folder?」「Hooks need review」）時
   完全不送 OSC 7501 → 不是 `blocked`，只表現為未啟動（`--wait-started` exit `8`，見 [auto-session.md](auto-session.md) § Worker 啟動確認）；
   OSC 7501 未公開，codex 改格式時 BAT 偵測會失效；遠端（WSL / SSH / Docker）的 codex 未實測。細節以 BAT 權威為準。

---

### 斷點 E：合併前確認（v5.3.0+）

> 本小節是斷點 E 的**唯一權威定義**。合併流程、三種模式與各模式的 yolo 規則見 [merge-workorder.md](merge-workorder.md)，本節不複述。

**判準**：塔台要對 `main`（或合併工單的 `merge_target`）執行 `git merge --ff-only`，把隔離工單的合併結果推進 `main` 之前。

- **非 yolo 模式（`on` / `ask` / `off`）**：**一律暫停**，等使用者確認後才 ff。
- **yolo 模式**：依 [merge-workorder.md](merge-workorder.md) § 三種模式 該模式的規則：
  - ① 機械合併：ff 前再確認直接合併五條判準仍成立 → 自動 ff，不暫停（資料來源見 [merge-workorder.md](merge-workorder.md) § 合併判準資料來源 › 查詢時機與資料來源）；
  - ② 衝突解決：驗收全綠**且**無範圍外檔案 → 自動 ff；否則暫停；
  - ③ 等價移植：一律暫停。
- 收單 SHA 比對任一步不成立 → 不進 ff，直接暫停並說明哪一步不成立（不論模式）。
- 不使用 worktree 隔離、不合併的流程不會觸發斷點 E。

**觸發後塔台動作**（yolo 標題為 `⏸ YOLO PAUSED — 斷點 E（合併前確認）`，非 yolo 為 `⏸ 合併前確認`）：

```
⏸ YOLO PAUSED — 斷點 E（合併前確認）
  合併：T#### → main（模式 <① 機械 / ② 衝突解決 / ③ 等價移植>）
  merge commit：<SHA>（parent1 <SHA> / parent2 <SHA>）
  驗收：<全綠 / 未全綠：…>　範圍外檔案：<無 / 清單>
  暫停原因：<非 yolo / 驗收未全綠 / 有範圍外檔案 / 模式 ③ / SHA 比對第 N 步不成立>
  選項：
    [A] 執行 git merge --ff-only
    [B] 暫不合併（分支與整合 worktree 保留）
    [C] 退回 yolo → ask 模式，手動接手
  請輸入 A/B/C：
```

- 斷點 E 不計入斷點 B 的連續 FAILED 計數；`[斷點 E]` 照常寫入 YOLO 歷程。
- `--ff-only` 被 git 拒絕（主 checkout 有重疊的髒檔）屬正常保護，不是失敗：告知使用者擋住的檔案，等使用者處理後再 ff。

---

### 使用者中斷（非斷點）

**判準**：使用者在塔台 session 直接輸入 `停` / `stop` / `abort`（regex `^(停|stop|abort)$`，case-insensitive）。

**觸發後塔台動作**：

```
🛑 YOLO PAUSED — 使用者中斷
  偵測字串：「<原文>」
  擱置動作：<下一張派發 / 當前派發中 buffer>
  Bash 執行：❌ 未送出
  yolo 狀態：PAUSED (等使用者指令)
```

**和 A/B/C/D/E 的差異**：

- A/B/C/D/E 為塔台/Worker 自動觸發，計數器累計、影響 yolo health 判定（D 只計觸發次數，不計入斷點 B，見上方 § 斷點 D）
- 使用者中斷為使用者主動觸發，獨立計數，不影響 yolo health 判定
- 使用者中斷**不佔用** `yolo_max_retries` 配額（B 斷點計數器不增）

---

## Worker 向塔台提問（v5.5.0+）

> 本節是 yolo「Worker 向塔台提問、塔台代決」的**唯一權威定義**（D036 / D037），Worker 端與塔台端都在這裡。
> `ct-exec/SKILL.md` 只放 Worker 必要步驟摘要＋引用本節；工單區段範本見 [work-order-template.md](work-order-template.md) § 回報區。
> 基本通道是工單檔往返（工單檔＋既有 `bat-notify.mjs` 一般通知），任何 BAT 版本都能用。v5.7.0 起 BAT `>= 0.7.0-pre.7` 另有結構化的
> BAT 問答通道（§ BAT 通道）；題目仍先寫進工單（雙寫，D048），BAT 通道不可用或中途失效時回到工單檔往返或 § 備援。
> BAT 通道的 helper 參數、exit code、MCP tool 欄位與版本判定在 CT 內**只寫在本節**（§ BAT 通道、§ Worker 端 第 3 點、§ 塔台端 第 1、3 點），其他檔只引用。

### 適用範圍

- 只適用 `CT_MODE=yolo` 的 Worker（`ct-exec`）。
- 非 yolo（`CT_MODE` 為 `on` / `ask` / `off`，或未設、不合法而降級為 `ask`）：本節**完全不適用**，Worker 與塔台行為不變
  （研究型工單照 [research-workorder.md](research-workorder.md) 向使用者提問）。
- yolo Worker **不得**使用 AskUserQuestion 或任何向使用者提問的工具（研究型工單、`CT_INTERACTIVE=1` 也一樣）。
  違規時塔台可能經 § 斷點 D 發現。

### BAT 通道（v5.7.0+）

> BAT 介面權威：BAT `docs/agent-guide/tower-questions.md`、`docs/agent-guide/blocked-state.md` 與 BAT `CLAUDE.md`「Worker 問塔台（PLAN-048 / T0607）」節
> （CT-T019；v5.7.0 依 BAT `c271e852` / `00bdcaeb` 撰寫）。CT 不得更改參數名、值域、exit code 語意或輸出格式；與本節不一致時以 BAT 權威為準。

BAT `>= 0.7.0-pre.7` 提供 Worker 問塔台的結構化通道：問題只存在 BAT 主行程記憶體（不寫檔、BAT 日誌不記內容），
Worker 以 helper 提問、以唯讀 MCP 長輪詢等答覆；塔台以唯讀 MCP 讀題、以 helper 答覆。BAT 不對 Worker 分頁寫入任何東西。

- **雙寫**（D048）：Worker 一律先照 § Worker 端 第 2 點把題目寫進工單、加 `tower_question: open`、commit，**之後**才走 BAT 通道。
  工單的問答紀錄（`### 待塔台決策`、`### 互動紀錄`）屬 CT，BAT 不保存；BAT 通道成功時塔台不在工單寫答覆行，由 Worker 寫互動紀錄。
- `worker_question_timeout = 0` → 不用 BAT 通道（照 § Worker 端 第 3 點）。
- 🔴 **內容只走 stdin**：問題、選項、`detail`、答覆文字只從 stdin 傳給 helper（UTF-8、≤ 64 KiB），不得放進命令列參數
  （helper 會把命令列原樣寫進 `bat-scripts.log`，命令列也會出現在程序列表與 agent 的工具紀錄）。Windows 用 pwsh 7 或 Git Bash heredoc；
  Windows PowerShell 5.1 的管線預設不是 UTF-8，會弄壞中文，不得使用。
- 權杖：題目與答覆裡不得寫出任何權杖值（[auto-session.md](auto-session.md) § 範圍權杖與分頁角色 第 2 點）；BAT 收件時的遮罩不改變這條規則。
- 不需要事先判斷 BAT 版本：直接送，依下方「版本判定與降級」表的結果降級。

**MCP tool**（唯讀；問答的寫入沒有 MCP tool，只走 helper）。錯誤判讀與降級照 [auto-session.md](auto-session.md) § BAT MCP 唯讀 tool 的判斷依據與降級鏈：

| tool | 誰用 | 參數 | CT 用到的回傳欄位 |
|---|---|---|---|
| `bat_wait_question` | Worker | `questionId`（必填）、`timeoutMs?`（≤ 45 000，預設 45 000） | `changed`、`status`（`pending` / `answered` / `cancelled` / `expired` / `lost`）、`endReason?`、`answer?`（`{ choice?, text }`；`choice` 1 起算）。`changed: false` + `status: pending` = 這次逾時，再呼叫 |
| `bat_list_questions` | 塔台 | `terminalId?`（Worker 的 terminal id；省略 = 送給本塔台的全部）、`status?`（`pending` / `all`，預設 `pending`） | `questions[]`：`questionId`、`workerTerminalId`、`workorder?`、`question`、`options`、`allowFreeText`、`detail?`、`blocking`、`status`、`expiresAt` |

BAT `>= 0.7.0-pre.7` 的狀態回傳（`bat_get_state` / `bat_wait` / `bat_list_terminals` 每列）另帶 `pendingQuestions`（該 Worker 的待答題數）；
Worker 有 `blocking` 的待答題時 `state: blocked`、`blockedReason: tower`、`source: 'question'`，不是斷點 D（見 § 斷點 D）。

**限制**（BAT 常數，CT 不另訂）：

- `--expires-min` 只收 `1`～`120`（分鐘）。CT 固定用生效的 `worker_question_timeout`（`0` 不用本通道，所以落在範圍內）。
- 🔴 `blocking` 題目超過 120 s 沒有提問的 Worker 呼叫等待 → `expired` / `not-polled`；單次等待最多 45 s。
- 每個 Worker 同時最多 8 題待答（超過 → `--ask` exit `10`）。題目 ≤ 4 000 字、`detail` ≤ 8 000 字、選項最多 10 個（每個 ≤ 500 字）、答覆 ≤ 8 000 字。
- 題目只在記憶體：BAT 重開或 headless server 重啟後舊 id 回 `lost`；Terminal Server recovery → `cancelled`；Worker 或塔台分頁結束 → `cancelled`。
- 使用者在 Worker 分頁輸入**不影響**題目（不取消、不清除 `blocked` / `tower`）。

**版本判定與降級**（CT 內唯一的權威表，依 BAT CT-T019「版本判定」；其他檔引用本表）：

| 端 | 判定為「BAT 通道不可用」 | 降級 |
|---|---|---|
| Worker 提問 | `--ask` exit ≠ `0`：舊 helper（stderr `Unknown option '--ask'`）、新 helper 舊 host（`ask: UNSUPPORTED`），以及 exit `3` / `10` 與其他 `1` | 該題加 `- **通道**：工單` 標記、commit 後改送一般 `T#### 提問` 通知（多題只送一次，v5.7.1，§ Worker 端 3-A 第 2 步），照 § Worker 端 3-B 等工單答覆行（題目已在工單；helper 失敗時已取消該題，不留下塔台看不到的題目） |
| Worker 等待 | MCP `bat_wait_question` 不存在、回 `UNSUPPORTED` / `CONNECT_FAILED` 或取不到 code 的錯誤；`--wait-answer` exit ≠ `0`；回傳 `status` 為 `lost` / `cancelled` / `expired` | MCP 不能用 → 改用 `--wait-answer`；`--wait-answer` 也失敗 → 取消該題（§ Worker 端 3-A 第 5 步）、剩餘時間照 3-B；`lost` / `cancelled` → 剩餘時間照 3-B；`expired` → § 備援。改走 3-B 的題都先照 § Worker 端 3-A 第 6 步加 `通道` 標記、commit、送一次一般 `T#### 提問`（v5.7.2） |
| 塔台讀取 | `bat_list_questions` 不存在 / `UNSUPPORTED`、狀態回傳沒有 `pendingQuestions` 欄位 | 讀工單 `### 待塔台決策`，照 § 塔台端 第 3 點的工單答覆寫答覆行。列表能用但裡面找不到該題 → 不屬本列，照 § 塔台端 第 1 點的表（有 `通道` 標記 → 工單答覆；沒有 → 先不答，v5.7.1） |
| 塔台答覆 | `--answer` exit `3`（含 `answer: LOST`）或 `1`（含 `Unknown option '--answer'`、`answer: UNSUPPORTED`） | 照 § 塔台端 第 3 點的工單答覆寫答覆行（exit `9` / `4` 也見該點） |

判斷只看 exit code、MCP 是否為錯誤結果與回傳的 `status`；stderr 只用來挑給使用者的提示文字（同 [auto-session.md](auto-session.md) § BAT MCP 唯讀 tool 的判斷依據）。
每一種降級最後都落到 v5.6.1 的工單檔往返或 § 備援，所以 BAT 通道不可用時行為與 v5.6.1 相同（v5.7.1 起 `--ask` 失敗的題多一行 `通道` 標記與一次 commit，見 § Worker 端 3-A 第 2 步；v5.7.2 起 `--ask` 成功後才改走工單的題也一樣，見同節第 6 步）。

**已知限制**：

- `--ask` 本身逾時（BAT 3 s 沒回應，exit `1`）時 helper 拿不到 id、無法取消；BAT 若已登記該題，塔台可能在 `bat_list_questions` 看到並以 BAT 答覆，
  Worker（已改等工單答覆行）收不到。這題由 BAT 租約在 120 s 內 `expired`；若塔台已答，Worker 最後逾時走 § 備援，塔台在 Renew 區段再答一次。
  v5.7.1 起 Worker 對這題加 `- **通道**：工單` 標記，塔台看到標記就改工單答覆（§ 塔台端 第 1 點），所以只剩「塔台在標記寫入前就處理了別題的通知、
  並以 BAT 答了這題」時才會發生。
- Worker 等待中 BAT 失效且 `--cancel-question` 也失敗時同上：最後由 § 備援 收尾。v5.7.2 起 Worker 改走工單時一樣加 `通道` 標記並送一般 `提問`
  （§ Worker 端 3-A 第 6 步），所以只剩「塔台在標記寫入前就以 BAT 答了這題」時才會發生。
- **BAT 已結束題目的保留規則**（BAT 常數，CT 不另訂；出處 BAT `electron/tower-questions.ts` `QUESTION_ENDED_RETENTION_MS` / `QUESTION_ENDED_MAX`
  與 sweep 的清除迴圈，檔案 commit `fbf641dc`；`docs/agent-guide/tower-questions.md` § 問題與 id，commit `5b58c748`）：
  - 已結束（`answered` / `cancelled` / `expired`）的題目保留 10 分鐘，從結束時間算；過期是在每次存取時才清，所以實際保留 ≥ 10 分鐘。
  - 全 BAT 合計最多保留 64 筆已結束題目，超過丟最舊的。與分頁關閉無關。
  - BAT 重開（headless server 重啟）全清，舊 id 回 `lost`。
  - `lost` 只出現在單題回傳（`--answer` exit `3`、`bat_wait_question` / `--wait-answer`），**不會**出現在 `bat_list_questions` 的列表裡。
  - 影響範圍（v5.7.2，D054 / D055）：CT 的正確性**不依賴**這個保留期——`--ask` 成功後才改走工單的題，Worker 都會加 `通道` 標記並送一般 `提問`
    （§ Worker 端 3-A 第 6 步），塔台看標記就走工單答覆。保留期只影響「塔台能不能在 Worker 寫標記**前**就在列表看到 `cancelled`」
    （§ 塔台端 第 1 點）；看不到時該則通知落「列表沒有、也沒有標記」先不答，等 Worker 寫標記後送來的 `提問`。

### Worker 端

> 本節與 § 塔台端 寫的 `T#### 提問`／`T#### 需要協助` 是訊息種類的名稱。Worker 實際送出的 ID（訊息字串與 `--source`）是工單完整 ID，含前綴、不得截短，
> 送出前與 frontmatter `id` 比對（v5.13.1+，[work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID）。

**1. 何時提問**：遇到工單範圍內無法自行決定、且猜錯會造成返工的選擇。

- 能依工單、決策日誌、專案慣例（`CLAUDE.md` / `AGENTS.md` / FIELDGUIDE 等）自行決定的，不提問：自己決定，並在回報區記下理由。
- 範圍外的事項：能記為候選、收尾回報的就記（`ct-exec` 範圍守護）；必須現在決定是否擴大範圍才能繼續的，用本通道提問
  （屬「範圍變更」，塔台會轉問使用者，見 § 塔台端）。Worker 不得自行擴大範圍。
- 研究型工單每一輪最多 `research_max_questions` 題（有效值見 [tower-config.md](tower-config.md) § 可用選項）。

**2. 寫問題**：在工單 `## 回報區` 最上方（`### 完成狀態` 之前）新增 `### 待塔台決策`（已有就接在後面）。
每題一個 `#### Q-n`，`n` 在同一張工單內遞增、不重用；一次可問多題：

```markdown
### 待塔台決策

#### Q-1：<一句話問題>
- 提問時間：<ISO 8601，取自系統：bash `date "+%Y-%m-%dT%H:%M:%S%z"`／PowerShell `Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"` 的輸出>
- 選項：[A] … / [B] … / [C] 其他：________
- Worker 建議：[A]，因為 …
- 影響範圍：<哪些檔案／步驟／驗收條件>
- 阻塞：是（Step N 起要等答覆）/ 否（先做不受影響的步驟）
```

- 「提問時間」（v5.8.1，D064；同使用者全域的時間戳規則）：**先執行**範本中的指令，再把輸出原樣貼上；不得自行推估、依前一個時間遞推或補成整數秒。
- Worker **不得**預寫答覆行或佔位文字（例「塔台答覆 Q-1：（待填）」）：答覆行由塔台新增，Worker 以它是否出現判斷是否已答。
- frontmatter 加 `tower_question: open`（表示有待答問題）。這是送 `T#### 提問` **前**的必要步驟，不論接下來是原地等待，
  還是 `worker_question_timeout = 0` 直接走 § 備援（v5.6.1，T0167）。
- **先 commit 後 notify**（v5.6.1，T0167）：送 `T#### 提問` 前，工單檔（含 `### 待塔台決策` 與 `tower_question: open`）必須已 commit；
  已完成、依 commit 政策要 commit 的產品變更也一樣。commit 寫法照 `ct-exec/SKILL.md` § Phase 4 › Commit rules
  （隔離工單照同檔 § Worktree Isolation 第 2、3 點：工單 commit 到 `$CT_HOME`、產品 commit 在 worktree）。
- 然後照第 3 點通知塔台：BAT 通道的 `--ask`，或一般的 **`T#### 提問`** 通知（yolo 照常 `--submit`），**二擇一，同一題不重複通知**。
  上面三步（寫題目、`tower_question: open`、commit）走不走 BAT 通道都一樣（v5.7.0，雙寫）。

**3. 送出與原地等待**：

先選通道（v5.7.0+）：

- `worker_question_timeout = 0` → 不用 BAT 通道：依 `ct-exec/SKILL.md` § BAT Notify And Fallback 送一般 `T#### 提問`，接著直接走第 4 點 § 備援。
- 其他情況 → 先走 **3-A BAT 通道**；不可用或中途失效時改 **3-B 工單檔等待**（判定見 § BAT 通道 › 版本判定與降級）。
- 總等待上限 = `worker_question_timeout` 分鐘，從第一次通知塔台起算（取值見 § `worker_question_timeout` 的取值）；從 3-A 改 3-B 時只剩剩餘時間。
- `阻塞：否` 的題目，Worker 可以先做不受影響的步驟；但填完成狀態之前，必須等到所有答覆或走備援。

**3-A BAT 通道**（BAT `>= 0.7.0-pre.7`）：

1. 每題送一次 `--ask`（一題一個問題 id，多題就依序送）。helper 路徑與 node 照 `ct-exec/SKILL.md` § BAT Notify And Fallback；題目內容只走 stdin：

   ```bash
   "${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-notify.mjs" --ask --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" \
     --submit --expires-min <worker_question_timeout> "<工單 ID> 提問" <<'JSON'
   {"question":"Q-n：<一句話問題>","options":["<選項 A>","<選項 B>"],"detail":"Worker 建議：…\n影響範圍：…\n阻塞：…","blocking":true}
   JSON
   ```

   - `<工單 ID>` 是工單完整 ID，含前綴、不得截短；送出前與 frontmatter `id` 比對（[work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID）。
   - `question` 以工單題號 `Q-n：` 開頭，內容與工單的題目相同（塔台據此對應工單題目）；`options` 照工單題目的選項，不列「其他」
     （BAT 預設允許自由文字）；`detail` 放 Worker 建議、影響範圍、阻塞；`blocking` 固定 `true`。
   - `--expires-min` = 生效的 `worker_question_timeout`；`--submit` 照 yolo 規則。PowerShell 用 pwsh 7 的 here-string 管線
     （`@'…'@ | & $n $h --ask …`），不用 Windows PowerShell 5.1。
   - `--ask` 自己就會通知塔台 `T#### 提問`：成功後**不要再另送一般通知**。
   - 一次問多題時，**先把所有題的 `--ask` 送完**（含第 2 步的標記、commit 與一般通知），才進入第 3 步的等待（v5.7.1，T0170）。
     從第一題 `--ask` 成功到開始等待，不得超過 120 s（§ BAT 通道 › 限制）。
2. exit `0` → 從 stdout 的 `question: <id>` 行取得問題 id。exit ≠ `0`（任何值）→ 這題改 3-B，在工單該題 `#### Q-n` 的最後加一行
   `- **通道**：工單`（v5.7.1；表示「這題改等工單答覆」，不是答覆行，第 3-B 的比對不會把它當成答覆）。所有題都送完後：
   - 有任何一題加了標記 → **commit 工單**（只多了標記行；commit 寫法同第 2 點）→ **最後**送**一次**一般 `T#### 提問` 通知
     （不論幾題退回都只送一次）→ 之後才進入等待，退回的題照 3-B 等工單答覆行。
   - 沒有任何題退回 → 不加標記、不送一般 `提問`（每題的 `--ask` 已各送一則通知）。
   - 這個順序的目的（F-1）：標記在最後那則 `提問` 送出前已 commit，塔台處理那則通知時一定看得到；工單裡沒有標記、BAT 列表裡也還沒有的題，
     一定還有後續通知（它自己的 `--ask`，或最後那則 `提問`），所以塔台可以照 § 塔台端 第 1 點先不答它。
   - 第 3 步起才改 3-B 的題（`--ask` 已成功；`lost`、`cancelled`，含 Worker 自己取消）也加同一行標記並送一般 `提問`，見第 6 步
     （v5.7.2，D055；推翻 v5.7.1「標記只在這一步加、晚退回不加標記也不另送通知」）。
3. 等答覆：迴圈呼叫 MCP `bat_wait_question`（`questionId` = 該 id，每次 ≤ 45 s）。MCP 不能用時（見 § BAT 通道 › 版本判定與降級）改用

   ```bash
   "${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-notify.mjs" --wait-answer <id>
   ```

   stdout 一行 JSON，欄位同 `bat_wait_question` 的回傳；任何 `status`（含 `pending`、`lost`）都是 exit `0`，exit ≠ `0` 是錯誤。
   - `changed: false` + `status: pending` = 這次逾時 → 再呼叫。
   - 🔴 兩次呼叫的間隔不得超過 120 s（`blocking` 題目沒人等會 `expired` / `not-polled`）。先做 `阻塞：否` 的不受影響步驟時也一樣；
     做不到就不要在等待期間做其他步驟。
   - `--wait-answer` 也 exit ≠ `0` → 照第 5 步取消這題，剩餘時間改 3-B（先照第 6 步）。
   - BAT 通道的等待本身就是等待工具：沒有 Monitor 之類工具的平台（例 codex）也能走 3-A。
4. 看回傳的 `status`：
   - `answered` → 依 `answer` 繼續（`choice` = 選了第幾個選項，1 起算；`text` = 塔台的答覆文字）。記入 `### 互動紀錄`（格式同 3-B），
     A 的部分寫 `A（塔台，BAT 通道，choice <n>）`（沒有 `choice` 就不寫這段）。BAT 不保存問答，互動紀錄是唯一的紀錄。
   - `lost`（BAT 重開過）或 `cancelled`（任何 `endReason`）→ 照第 6 步加標記、commit、送一般 `提問`，剩餘時間改 3-B 等工單答覆行
     （塔台看到標記就寫工單答覆行，見 § 塔台端 第 1、3 點）。
   - `expired`（`timeout` / `not-polled`）→ 第 4 點 § 備援。
5. 中途放棄 BAT 等待（等待工具都不能用、要改 3-B；或要結束 Worker）→ 取消該題：

   ```bash
   "${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-notify.mjs" --cancel-question <id>
   ```

   🔴 exit `0` 不代表這次取消了，看 stdout 的 `status:` 行：`cancelled worker` 才是這次取消；`answered` → 答覆已到，
   再呼叫一次 wait 取得答覆後照第 4 步；其他（`expired …`、`cancelled <其他原因>`、`lost`）→ 照原本要走的路徑，如下。
   要改 3-B 時（v5.7.2）：`cancelled worker`、`cancelled <其他原因>`、`lost`，或 `--cancel-question` 本身失敗（exit ≠ `0`、沒有 `status:` 行）
   → 照第 6 步再改 3-B；`answered` → 照上面取得答覆，**不加標記**；`expired …` → § 備援，**不加標記**。
   要結束 Worker 時的順序見第 4 點 § 備援（那時不加標記，塔台照「收到備援」在 Renew 區段答）。
6. **晚退回的標記**（v5.7.2，D055）：`--ask` 已成功（有問題 id）的題，在第 3 步起因第 4 步的 `lost` / `cancelled`、或第 5 步列出的情況
   （含等待工具都不能用、`--wait-answer` exit ≠ `0`）而改走 3-B 時：
   1. 在工單該題 `#### Q-n` 的最後加一行 `- **通道**：工單`（與第 2 步同一行；只加這一行，不改題目或其他內容）。
   2. **commit 工單**（只多了標記行；commit 寫法同第 2 點）。
   3. 送**一次**一般 `T#### 提問` 通知（依 `ct-exec/SKILL.md` § BAT Notify And Fallback，yolo 照常 `--submit`）。送不出去 → 第 4 點 § 備援。
   4. 這題剩餘時間照 3-B 等工單答覆行。

   - 同一時間有幾題一起退回（例：BAT 重開，所有在等的題一起 `lost`）→ 標記都加完、**commit 一次**、只送**一則**一般 `提問`。之後又有別題退回，再照本步做一次。
   - 不適用：`--cancel-question` 的 `status:` 行是 `answered`（照第 4 步 `answered`）或 `expired …`（§ 備援）；第 4 步的 `expired`（§ 備援）。都不加標記。
   - 目的（D054 / D055）：標記在那則 `提問` 送出前已 commit，塔台處理時一定看得到，照 § 塔台端 第 1 點表第一列走工單答覆；
     塔台因此不依賴 BAT 列表的 `cancelled` 狀態，也就不依賴 BAT 已結束題目的保留期（§ BAT 通道 › 已知限制）。
   - 塔台若在標記寫入前已經依列表 `cancelled` 或 `--answer` exit `9` 寫了這題的工單答覆行，標記與這則 `提問` 不會造成重複答覆：
     塔台收到時該題已有答覆，照 § 塔台端 第 1 點「沒有任何未答的題 → 不動作」。
   - 這是 3-B「等待期間對工單檔只讀不寫」的唯一例外，範圍只限：標記行、這一次 commit、一則一般 `提問`。
     做完再回到其他題的 BAT 等待，兩次呼叫的間隔仍不得超過 120 s（第 3 步）。

**3-B 工單檔等待**（v5.6.1 原第 3 點；BAT 通道沒用或已降級時）：

- 用 agent 平台提供的等待／監看工具（例 Claude Code 的 Monitor、背景 shell 迴圈）重讀**自己的工單檔**
  （隔離工單讀 `$CT_HOME/_ct-workorders/<file>`，見 `ct-exec/SKILL.md` § Worktree Isolation），直到每一題都出現 `塔台答覆 Q-n` 行。
- **怎麼判斷「出現答覆行」**（v5.6.1，T0166）：只認固定格式的答覆行——行首 `- **塔台答覆 Q-n**`（格式見 § 塔台端 第 3 點），
  而且只在 `### 待塔台決策` 區段或 `## 塔台補充（Renew #N）` 區段內找。工單本文（執行步驟、驗收條件等）出現同樣字樣**不算答覆**；
  只搜整份檔案的 `塔台答覆 Q-n` 字樣，會在塔台還沒答時就誤判已答。`` ``` `` 圍起來的 fenced code block 裡的標題行與答覆行也**不算**
  （v5.7.1；例如工單本文貼了範本）。可直接用的比對（`Q-1` 換成題號；題號後緊接的 `[*][*]` 擋住 `Q-10` 這類前綴誤命中；
  用 `[*]`、`` [`] `` 而不用 `\*`、`` \` ``，避開 awk 字串跳脫的差異；行首可有空白的 `` ``` `` 行切換「在程式碼區塊內」）：

  ```bash
  # exit 0 = 已答；exit 1 = 還沒答
  awk -v q='Q-1' '
    /^[ \t]*[`][`][`]/ { in_f = !in_f; next }
    in_f { next }
    /^##[#]? / { in_s = ($0 ~ /^### 待塔台決策/ || $0 ~ /^## 塔台補充（Renew #[0-9]+）/) }
    in_s && $0 ~ ("^- [*][*]塔台答覆 " q "[*][*]") { found = 1 }
    END { exit !found }' "$f"
  ```

  3-A 第 2、6 步的 `- **通道**：工單` 標記不是答覆行，這個比對不會命中它。

  只需要單行判斷時，答覆行本身的 regex 是 `^- \*\*塔台答覆 Q-1\*\*`（例 `grep -qE '^- \*\*塔台答覆 Q-1\*\*' "$f"`）；
  它不限區段，所以以上面限定區段的比對為準。
- 間隔 ≥ 30 秒；總等待上限見上方「先選通道」。
- 讀到答覆 → 依答覆繼續。每題記入回報區 `### 互動紀錄`（研究型工單格式，見 [research-workorder.md](research-workorder.md) § 互動紀錄格式）：
  `[HH:MM] Q-n: <問題摘要> → A（塔台）: <答覆> → Action: <採取的行動>`。
- 等待期間對工單檔只讀不寫；已寫的題目不改，要補充就開新題（重新照第 2、3 點送出）。3-A 第 2 步的 `通道` 標記在開始等待前加，不屬等待期間。
  唯一的例外是 3-A 第 6 步的晚退回標記（v5.7.2）：只限標記行、一次 commit、一則一般 `提問`。
  這些 commit 以工單檔為單位，塔台已寫、未 commit 的答覆行會一併帶入，屬預期行為（v5.8.1，見 § 塔台端 第 3 點 **工單答覆**）。

全部題目都答完（不論經 3-A 還是 3-B）→ 刪除 frontmatter `tower_question`。

**4. 備援**（以下任一成立 → 不再等）：

- 等到上限仍有題目沒答；
- `worker_question_timeout = 0`；
- 3-A 回傳 `expired`（`timeout` / `not-polled`）；
- 要走 3-B，但平台沒有可用的等待工具（例 codex；Worker 自行判斷，並在回報區 `### 遭遇問題` 說明）；
- `T#### 提問` 通知送不出去（`--ask` 失敗後改送的一般通知、或 3-A 第 6 步晚退回後的一般通知也失敗，塔台不會知道有問題）。

做法：照常完成回報區（`### 待塔台決策` 原樣保留、frontmatter `tower_question: open` 保留；第 2 點送 `提問` 前就該加上，
沒有就在這時補上）→ 工單 `BLOCKED` → **commit 工單（含 `BLOCKED` 狀態）與產品變更**（`ct-exec/SKILL.md` § Phase 4 › Commit rules；
隔離工單照同檔 § Worktree Isolation 第 8 點的收尾順序：工單 commit 之後才 notify）→
還有 BAT 題目在等（3-A 的 id、還沒收到結束狀態）就照 3-A 第 5 步取消（v5.7.0+）→
依 `ct-exec/SKILL.md` § BAT Notify And Fallback 送 `T#### 需要協助`（通知失敗照該節顯示手動訊息）。

### 塔台端

**收到 `T#### 提問`**（斷點 A regex 的合法字串，但不是收尾，不收單）：

0. **先看 Worker 會不會等**（v5.6.1，T0167）：工單 frontmatter `worker_question_timeout: 0`，或工單狀態已是 `BLOCKED` →
   Worker 不會等答覆、會走 § 備援。這時**不在題目下寫答覆**，等 `T#### 需要協助` 後照下方「收到備援」只在 Renew 區段答，
   避免同一題有兩個答覆。代決邊界照第 2 點先判斷（需要使用者決定的照樣先問）。
1. **讀題**：讀工單 `### 待塔台決策` 中還沒有 `塔台答覆` 的題目（題目全文、Worker 建議、阻塞以工單為準）。
   接著（v5.7.0+）呼叫 MCP `bat_list_questions`（`status: all`；`terminalId` = 該 Worker 的 terminal id，不知道時省略，再以 `workorder` 篩選）。
   列表中「該題」= 屬於這張工單（`workorder` = 該工單編號；沒有 `workorder` 時看 `workerTerminalId` 是否為該 Worker）、且 `question` 以該題號
   `Q-n：` 開頭的題。對每一題未答的 Q-n 依序判斷（v5.7.1，T0170；第一個符合的那列生效）：

   | Q-n 的狀況 | 這一則通知怎麼處理 |
   |---|---|
   | 工單裡該題下有 `- **通道**：工單` 標記（§ Worker 端 3-A 第 2、6 步） | 第 3 點走 **工單答覆**（Worker 在等工單；列表即使有這題也不用 BAT 答） |
   | 列表有、`pending` | 第 3 點走 **BAT 答覆** |
   | 列表有、`answered` | 不動作（已經以 BAT 答覆；BAT 答覆的題在工單裡本來就沒有答覆行） |
   | 列表有、`cancelled` | 第 3 點走 **工單答覆**（Worker 已改等工單答覆行，§ Worker 端 3-A 第 4、5 步；標記還沒寫入） |
   | 列表有、`expired` | 不在題目下答；等 `T#### 需要協助`，照下方「收到備援」 |
   | 列表沒有、也沒有標記 | **這一則通知先不答**，等同一 Worker 的下一則通知再判斷（題目還在 `--ask` 的路上） |

   - `bat_list_questions` 不能用、狀態回傳沒有 `pendingQuestions` 欄位（§ BAT 通道 › 版本判定與降級）→ 不用上表，全部未答的題照 v5.6.1
     走 **工單答覆**。
   - 🔴 判斷只看「列表狀態＋工單標記」，**不得**用「列表目前沒有 `pending` 題」推論 Worker 已送完：塔台剛答完一題時，`pending` 列表會暫時是空的，
     後面幾題可能還沒登記到 BAT（F-1，T0616 實測的競態）。
   - Worker 在最後一則通知之前，每一題不是已登記到 BAT、就是已加標記（§ Worker 端 3-A 第 2 步），所以處理到同一 Worker 的最後一則通知時，
     還沒有結果的題不會落在「列表沒有、也沒有標記」那列。一直沒有後續通知時（例如 Worker 是 v5.7.0 以前的 `ct-exec`，見 § BAT / Worker 版本相容），
     Worker 逾時走 § 備援，塔台在 `需要協助` 後照「收到備援」答覆：不會有題目永遠等不到答覆，最壞是等到逾時。
   - `lost` 不在上表：它只出現在單題回傳（`--answer` exit `3`、`bat_wait_question`），**不會**出現在 `bat_list_questions` 的列表
     （§ BAT 通道 › 已知限制）。BAT 重開後舊題從列表消失，落「有標記」或「列表沒有、也沒有標記」列。
   - **「`--ask` 成功後才改走工單」**時（O-1，T0616 Q-3；v5.7.2，D055）：Worker 照 § Worker 端 3-A 第 6 步加 `通道` 標記、commit、
     再送一則一般 `提問`，塔台處理那則通知時看到標記 → 上表第一列。所以塔台**不依賴 BAT 已結束題目的保留期**（10 分鐘／64 筆，§ BAT 通道 › 已知限制）：
     超過保留期、列表已沒有這題也一樣有標記可看。
     列表 `cancelled` 列與第 3 點 exit `9` 的 `cancelled` 規則保留，處理的是「標記還沒寫入前，塔台就先處理到該題原本 `--ask` 的那則 `提問`」：
     那時列表已是 `cancelled` → 上表 `cancelled` 列；還是 `pending`、`--answer` 才回 exit `9` `status: cancelled worker` → 第 3 點 exit `9` 的
     `cancelled` 規則。兩者都改寫工單答覆行。v5.7.1 以前的 Worker 不寫晚退回標記，也只能走這兩條（受保留期限制，見 § BAT / Worker 版本相容）。
   - 🔴 這時同一題不會兩個通道都答：塔台依列表 `cancelled` 或 exit `9` 寫了工單答覆行之後，才收到 Worker 第 6 步送來的一般 `提問` →
     該題已有答覆行、不再是「未答的題」，照下方「沒有任何未答的題 → 不動作」，不 `--answer`、不再寫第二行。
     反過來，`--answer` 先成功（exit `0`）的題，Worker 在等待中收到 `answered`，不會走第 6 步。
   - 🔴 同一題只能有一個生效的答覆：`--answer` exit `0` 之後不得再寫工單答覆行，寫了工單答覆行之後不得再 `--answer`。
     `--answer` 失敗（exit `3` / `1`，或 `9` 的 `cancelled`）後改寫工單答覆行不算重複。
   - 沒有任何未答的題（例如同一批題目的第二個 `提問` 通知）→ 不動作。
2. 每題依**代決邊界**判斷：
   - **工單範圍內的技術／實作選擇** → 塔台決定。
   - **範圍變更、刪除／不可逆操作、對外發布、需要使用者偏好的選擇** → 先問使用者（格式見下），使用者回答後再答覆。
3. 依第 1 點的結果答覆：
   - **BAT 答覆**（v5.7.0+）：答覆文字只走 stdin（同 § BAT 通道 的 stdin 規則）：

     ```bash
     "${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-terminal.mjs" --answer <questionId> --notify-id "$BAT_TERMINAL_ID" [--choice <n>] <<'TXT'
     <決策>——<一句理由>（塔台代決 / 使用者決定）
     TXT
     ```

     `--choice` = 選第幾個選項（1 起算）；答「其他」不帶 `--choice`，只寫文字。結果只看 exit code：
     - `0` → 完成，**不在工單寫答覆行**（Worker 從 BAT 收到、自己寫互動紀錄）。
     - `3`（含 `answer: LOST`）或 `1`（含 `UNSUPPORTED`、`Unknown option '--answer'`）→ 改 **工單答覆**。
     - `9` CLOSED → 不重答，看 stdout 的 `status:` 行：`answered` → 已有答覆生效，不再動作；`expired …` → 等 `T#### 需要協助`，照下方「收到備援」；
       `cancelled …` → 重讀工單：已 `BLOCKED` → 同 `expired`；否則改 **工單答覆**（Worker 取消 BAT 題目後就在等工單答覆行）。
     - `4` NOT_OWNER → 斷點 A（題目不是送給這個塔台的）。
   - **工單答覆**：在該題最後新增**一行**（只新增這一行；不改 Worker 寫的任何內容、不改工單其他區段）：
     `- **塔台答覆 Q-n**：<決策>——<一句理由>（<時間，取自系統>；塔台代決 / 使用者決定）`
     塔台寫完答覆行**不另 commit**（v5.8.1，D064）：Worker 之後以工單檔為單位 commit 時會一併帶入這行，屬預期行為。
     Worker 不得改動答覆行，可在回報區註明該次 commit 帶入了塔台答覆行。
4. 每題記入決策日誌（[decision-log-system.md](decision-log-system.md)），並寫 YOLO 歷程 `[提問]` 條目（兩種答覆都一樣）。
5. 不另外通知 Worker、不對 Worker 分頁送任何按鍵或輸入：Worker 自己讀工單檔或從 BAT 等到答覆。

🔴 塔台**不背景輪詢** `bat_list_questions`：只在收到 `T#### 提問`，或查狀態時看到某個 Worker `blocked` / `tower`（§ 斷點 D）時查。
看到 `blocked` / `tower` 但沒收到 `提問`（例如通知遺失）→ 照本節第 0 點起處理。

回報區原則上只由 Worker 填寫；`塔台答覆 Q-n` 行是唯一的例外。

**升級給使用者的暫停格式**（比照斷點 A 的選項式）：

```
⏸ YOLO PAUSED — 提問需要你決定
  工單：T####（<分頁標題>）Q-n：<問題>
  Worker 建議：<建議與理由>
  需要你決定的原因：<範圍變更 / 刪除或不可逆 / 對外發布 / 需要你的偏好>
  選項：
    [A] <選項 A>
    [B] <選項 B>
    [C] 其他：________
  請輸入：
```

使用者回答前 Worker 可能已逾時走備援：照下方「收到備援」處理，答覆改寫在 Renew 區段。
走 BAT 答覆的題目升級給使用者時仍是 `pending`，但會在 `expiresAt` 過期（v5.7.0+）：使用者回答後照第 3 點答覆，
過期了（`--answer` exit `9`、`status: expired …`）就照下方「收到備援」。

**收到備援的 `T#### 需要協助`**（工單 `BLOCKED`、frontmatter `tower_question: open`）：

- 依同一代決邊界決定答覆，寫在 `## 塔台補充（Renew #N）`（格式見 [research-workorder.md](research-workorder.md) § Renew 機制），每題一行 `塔台答覆 Q-n`
  （行首格式與上方第 3 點相同：`- **塔台答覆 Q-n**：…`，不放進引用區塊；Worker 以這個格式判斷已答，見 § Worker 端 第 3 點）；
  `renew_count` +1、狀態改回 `PENDING`，然後重新派工（派新的 Worker；不對舊分頁送按鍵）。派新 Worker 前先照
  [work-order-system.md](work-order-system.md) § 回報處理流程 › 重派前回收舊 Worker 分頁（v5.12.0+）回收舊分頁。
- Worker 讀到 Renew 區段的 `塔台答覆 Q-n`，等同讀到答覆：記入互動紀錄、刪除 `tower_question`、繼續執行。

### 計數

- 提問本身不計入 `yolo_max_retries`、不算 Renew、不算 FAILED，也不是斷點。
- 走備援時就是一次一般的 `BLOCKED` + Renew：照既有規則計入斷點 B-1（Renew 次數）與 B-2（連續 FAILED / BLOCKED）。
- YOLO 歷程每題追加：`[提問] <時間> — T#### Q-n <問題摘要> → <答覆摘要>（塔台代決 / 使用者決定 / 逾時走備援）`。

### `worker_question_timeout` 的取值

有效值與預設以 [tower-config.md](tower-config.md) § 可用選項 為準。塔台 session 的 `*config` 只在塔台記憶體裡，Worker 看不到，所以：

- **塔台**：yolo 派工前，把生效值（session > project > global > 預設）寫進工單 frontmatter `worker_question_timeout: <分鐘>`。
- **Worker** 依序取第一個存在的值：工單 frontmatter `worker_question_timeout` → `_ct-workorders/_tower-config.yaml` →
  `~/.claude/control-tower-data/config.yaml` → 預設值。讀 config 屬 `ct-exec` 允許的 Worker 調校值讀取，不是讀 runtime mode。
- 取到的值不是 `0`～`120` 的整數 → 改用預設值，並在回報區記 WARN。Worker 不自行使用其他數字。

---

## `_tower-state.md` 新增 `## YOLO 歷程` 區段

yolo 模式啟動時，塔台在 `_tower-state.md` **必要區段清單**之外追加此區段（位置：`## 🔍 環境快照` 之後、檔尾之前）。

### 格式規格

```markdown
## YOLO 歷程

### 當前 Session（2026-04-18 13:00）

- [啟動] 2026-04-18 13:00 — PLAN-020 啟動 yolo，資訊來源：T0167 研究工單 D 區段
- [派發] 2026-04-18 13:02 — T0168 → T0169（依拆單表第 2 列）
- [完成] 2026-04-18 13:45 — T0168 DONE（正常）
- [派發] 2026-04-18 13:46 — T0169 → T0170（依拆單表第 3 列）
- [完成] 2026-04-18 14:30 — T0169 DONE（正常）
- [派發] 2026-04-18 14:31 — T0170 → T0171（依拆單表第 4 列）
- [斷點 A] 2026-04-18 15:00 — T0170 回報「執行時遇到問題」，不匹配四字串 → 暫停
- [恢復] 2026-04-18 15:02 — 使用者選 [C] 退回 ask 模式

### 計數器

- 連續 FAILED: 0 / 3
- 本 session yolo 派發工單數: 3
- 本 session 斷點觸發: A×1, B×0, C×0, D×0, E×0, 使用者中斷×0
- 本 session 提問: 0

### 歷史 Session（摘要）

- 2026-04-15 yolo session：派發 4 張，全 DONE，無斷點
- 2026-04-16 yolo session：派發 2 張，斷點 B-2 觸發後暫停
```

### 寫入時機

| 事件 | 寫入欄位 |
|------|---------|
| yolo 模式首次啟動（本 session） | 新增 `### 當前 Session` 標題 + `[啟動]` 條目 |
| 塔台派發下一張工單 | 追加 `[派發]` 條目 |
| Worker 回報完成 | 追加 `[完成]` 條目 |
| 斷點 A/B/C/D/E 觸發 | 追加 `[斷點 X]` 條目 + 更新計數器（D 同一個 `blockedSince` 只記一次） |
| 收到 `T#### 提問`（v5.5.0+） | 每題追加 `[提問]` 條目 + 更新「本 session 提問」（格式見 § Worker 向塔台提問 › 計數） |
| 使用者輸入「停」/「stop」/「abort」 | 追加 `[使用者中斷]` 條目 + 不更新 A/B/C/D/E 計數器 |
| 使用者恢復流程 | 追加 `[恢復]` 條目 |
| yolo 模式關閉 | `### 當前 Session` 移至 `### 歷史 Session` 摘要 |

### 必要區段清單更新

`_tower-state.md` 原必要區段清單為 7 項。yolo 啟用時**條件追加**第 8 項：

> 8. YOLO 歷程（僅當 `auto-session: yolo` 曾啟用）

非 yolo 模式下此區段不存在，**不視為區段缺失**。

---

## 使用者可見訊息（規格化彙整）

### 啟動階段

| 情境 | 訊息 |
|------|------|
| yolo 模式首次啟動 | 主面板（[memory-protocol.md](memory-protocol.md) § 塔台狀態面板）下方顯示 `⚠️ YOLO MODE ACTIVE` 警語（見上方格式） |
| `yolo_max_retries = 0` | 啟動面板警語中斷點 B 行改為「B 已停用」 |

### 派發階段

| 情境 | 訊息 |
|------|------|
| 下一張派發前 | `🤖 YOLO: T0xxx DONE → 自動派發下一張 T0xxy`（含依據、計數器、中斷提示） |
| 1-2s 緩衝期 | 同上面板保持顯示（不額外訊息） |
| 派發完成 | 沿用現有 `on` 模式派發訊息，但頭部加 `🤖 YOLO` 前綴 |

### 斷點觸發

| 斷點 | 訊息 |
|------|------|
| A | `⏸ YOLO PAUSED — 斷點 A 觸發` |
| B-1 | `⏸ YOLO PAUSED — 斷點 B-1` |
| B-2 | `⏸ YOLO PAUSED — 斷點 B-2` |
| C | `⏸ YOLO PAUSED — 斷點 C 觸發` |
| D（v5.5.0+） | `⚠️ YOLO 斷點 D（不暫停）— <分頁標題> 在等你回答（原因：<blockedReason>，從 HH:MM 起）`；非 yolo 為 `ℹ️ 斷點 D — <分頁標題> 在等你回答（原因：<blockedReason>，從 HH:MM 起）` |
| E（v5.3.0+） | `⏸ YOLO PAUSED — 斷點 E（合併前確認）`；非 yolo 為 `⏸ 合併前確認` |
| 提問需要使用者決定（v5.5.0+，非斷點） | `⏸ YOLO PAUSED — 提問需要你決定`（塔台代決的題目不顯示暫停，見 § Worker 向塔台提問 › 塔台端） |
| 使用者中斷（非斷點） | `🛑 YOLO PAUSED — 使用者中斷` |

### PLAN 完成

| 情境 | 訊息 |
|------|------|
| D 區段所有列完成 | `✅ PLAN-0XX 所有工單完成 → yolo 流程結束。是否結案 PLAN？[A] 是，*plan close / [B] 否，保留` |

---

## 收單後回收 Worker 分頁（v5.1.0+）

yolo 自主收單同樣適用 [work-order-system.md](work-order-system.md) § 回報處理流程 › 收單後回收 Worker 分頁（`worker_auto_close`）；
條件、指令與 exit code 處理以該節為準，本節不複述。

回收是收單確認之後的附帶動作，**斷點 A / B / C / D 的判斷不受回收結果影響**：任何 exit code 都不計入斷點 B 計數、
不觸發斷點，也不改變「下一張工單判定邏輯」的結果。

---

## 失敗硬鉤子語意對齊

> 📌 v5.1.0 更正：v4.2.0 ~ v5.0.9 此處寫「notify 失敗 → 工單狀態保持 `IN_PROGRESS`」，並引用 `ct-exec` Step 8.5 / `ct-done` Step 6.5。
> 現行 Worker skill 沒有這兩個步驟編號，收尾順序是**先寫最終狀態、commit 工單，最後才 notify**：
> `ct-exec/SKILL.md` § Phase 4（產品 commit → 填回報區（記產品 commit hash）→ 最終狀態與完成時間 → 工單 commit；v5.7.0 起非隔離工單也與
> 同檔 § Worktree Isolation 第 8 點同序）之後才是 § BAT Notify And Fallback（"After metadata/report closeout"）；
> `ct-done/SKILL.md` § Workflow 第 7 步更新 metadata、第 8 步 commit 工單檔（v5.7.0+）、第 9 步才 notify。

yolo 下 Worker `bat-notify` 失敗時：

- 工單**已是最終狀態**（`DONE` / `PARTIAL` / `BLOCKED` / `FAILED` 等），回報區已完整、工單已 commit（依 commit 政策）——只是塔台沒收到通知
- 塔台 session 在 yolo 下**不會收到**該工單的完成訊息
- 塔台無訊息可 parse → **不觸發**斷點 A/B/C（因為沒有 Worker 回報；斷點 D 看 BAT 狀態、不看訊息，不受影響）
- `T#### 提問` 送不出去時（v5.7.0+：`--ask` 失敗後改送的一般通知也失敗），Worker 不等答覆，直接走 § Worker 向塔台提問 › 備援
- Worker 會照自己的手動 fallback 顯示應回報的固定訊息（`ct-exec/SKILL.md` § BAT Notify And Fallback、`ct-done/SKILL.md` § BAT Notify）；
  使用者把該訊息帶回塔台 → 塔台照 [work-order-system.md](work-order-system.md) § 回報處理流程收單，判定依工單檔案的最終狀態與回報區

此設計避免塔台誤判「Worker 失敗」為「Worker 無回應」觸發錯誤斷點。

---

## 相容性

### auto-session 向下相容

| 現有設定 | 升級後行為 |
|---------|-----------|
| `auto-session: off` | 完全不變，yolo 新機制不影響 |
| `auto-session: ask` | 完全不變 |
| `auto-session: on` | 完全不變 |
| 未設定（套用 [tower-config.md](tower-config.md) § 可用選項 的預設值） | 完全不變 |

yolo 為**新增**第四階，啟用前需使用者明確下 `*config auto-session yolo`，**無自動升級**。

### 舊工單相容

| 情境 | 行為 |
|------|------|
| 工單無 `關聯 PLAN` / `關聯研究` 元資料 | yolo 下該工單完成後 → 斷點 A（無法決策下一張），退回使用者手動 |
| 研究工單無 D 區段 | 同上，斷點 A |
| D 區段表格欄位不全 | 同上，斷點 A |
| `_tower-state.md` 無 `## YOLO 歷程` 區段 | yolo 啟用時自動建立；非 yolo 模式下此區段不存在不視為缺失 |

### BAT / Worker 版本相容

| 組件 | 最低版本 | yolo 行為 |
|------|---------|-----------|
| BAT `bat-notify.mjs` | PLAN-020 W1（含 `--submit`） | Worker 自動送出可生效 |
| Worker skill（ct-exec/ct-done） | v4.2.0（本 release） | 硬鉤子邏輯 + 四字串規格生效 |
| control-tower skill | v4.2.0（本 release） | 塔台自主決策 + 3 斷點生效 |
| BAT `bat-terminal.mjs`（帶前綴 `--workorder`，如 `CP-T0113`） | `v0.5.9-pre.1`（BAT 的 fork 版）——upstream 原始 repo 截至 2026-09-02 尚未含此修復 | 帶前綴工單可走結構化派工；舊版走 `--prompt` 降級（見 [auto-session.md](auto-session.md) § 舊版 BAT 降級規則） |
| BAT MCP `state == blocked`（斷點 D） | `0.7.0-pre.4`（回傳有 `blockedDetection` 欄位） | 斷點 D 生效；更舊或 MCP 不可用 → 斷點 D 不啟用（見 § 斷點 D） |
| BAT `blockedReason` 的 AskUserQuestion 修正（BUG-150） | `0.7.0-pre.5` | AskUserQuestion 回報 `question`、回答後立即清除；`0.7.0-pre.4` 回報 `permission`。塔台邏輯相同（見 § 斷點 D） |
| Worker skill `ct-exec`（提問通道） | v5.5.0 | yolo Worker 送 `T#### 提問` 並原地等待；舊 Worker 不會提問，行為不變 |
| BAT 問答通道（`bat-notify.mjs --ask` / `--wait-answer` / `--cancel-question`、`bat-terminal.mjs --answer`、MCP `bat_list_questions` / `bat_wait_question`、`blockedReason: tower`、`pendingQuestions`） | `0.7.0-pre.7` | yolo 提問走 BAT 通道（題目仍寫工單，雙寫）；更舊的 BAT 或任一端不可用 → 工單檔往返，行為同 v5.6.1（判定見 § Worker 向塔台提問 › BAT 通道 › 版本判定與降級）；`tower` 不是斷點 D |
| Worker skill `ct-exec`（BAT 通道） | v5.7.0 | v5.5.0～v5.6.1 的 Worker 只送一般 `T#### 提問`：塔台 v5.7.0 在 `bat_list_questions` 找不到題目 → 工單答覆，行為同 v5.6.1（塔台 v5.7.1 起見下一列） |
| Worker skill `ct-exec`（多題等齊，`通道` 標記） | v5.7.1 | 塔台 v5.7.1 對「列表沒有、也沒有標記」的題先不答（§ 塔台端 第 1 點）。v5.7.0 以前的 Worker 不加標記：它們改走工單的題（v5.5.0～v5.6.1 的全部題目、v5.7.0 `--ask` 失敗的題）要等 Worker 逾時走 § 備援、塔台在 Renew 區段答覆。CT 兩端與 Worker 同版安裝即不受影響 |
| Worker skill `ct-exec`（晚退回也加 `通道` 標記） | v5.7.2 | `--ask` 成功後才改走工單的題也加標記並送一般 `提問`（§ Worker 端 3-A 第 6 步），塔台不依賴 BAT 保留期。v5.7.1 的 Worker 不加：塔台只能靠列表 `cancelled` 列或 `--answer` exit `9`（§ 塔台端 第 1、3 點），超過 BAT 保留期（10 分鐘／64 筆）或 BAT 重開就落「列表沒有、也沒有標記」，要等 Worker 逾時走 § 備援。不會答錯，只會慢 |
| BAT `bat-terminal.mjs --wait-started`（Worker 啟動確認）、`disableAllHooks` → `blockedDetection: none` | `0.7.0-pre.6` | 派工帶 `--wait-started 30000`，exit `8` 不重派、不是斷點；更舊的 BAT 去掉參數重派一次（見 [auto-session.md](auto-session.md) § Worker 啟動確認）。斷點 D 已知限制第 4 點依版本不同（見 § 斷點 D） |
| BAT codex OSC 7501（`blockedDetection: osc`、`blockedReason: input`、codex `agentStarted`；BAT T0621，另需 codex `>= 0.163.0`） | `>= 0.7.0-pre.9` | v5.8.0+：codex Worker 的 `input` 走斷點 D（§ 斷點 D）、`--wait-started` 對 codex 回 `started: <時間>` 或 exit `8`（[auto-session.md](auto-session.md) § Worker 啟動確認）。舊 BAT（≤ `0.7.0-pre.8`）或較舊 codex → `blockedDetection: none`、`agentStarted: null`、`started: unknown`，行為同 v5.7.2 |

**漸進式啟用**：任一組件版本不足時：
- BAT 舊版本 → Worker yolo 降級為 on（Worker skill 已規格化）
- BAT < `v0.5.9-pre.1` + 帶前綴工單 → 塔台單次降級為 `--prompt` 派工並明示原因；
  **不得以錯誤訊息字串存在性判版**（見 [auto-session.md](auto-session.md) § 舊版 BAT 降級規則）
- Worker skill 舊版 + BAT 新版 → 塔台讀到舊版字串 → 斷點 A 觸發（安全）

---

## 迴歸測試場景

### T1：`auto-session: off` 行為不變

- 觸發：`*config auto-session off` → 派發工單
- 預期：
  - 無 `⚠️ YOLO MODE ACTIVE` 警語
  - Worker 收尾後塔台不自動派發下一張
  - 無 `## YOLO 歷程` 區段寫入
  - `yolo_max_retries` config 存在但無影響

### T2：`auto-session: ask` 行為不變

- 同 T1，預期行為完全一致。

### T3：`auto-session: on` 行為不變

- 同 T1，但開新分頁 + 預載指令正常運作；Worker 回報需使用者按 Enter。

### T4：`auto-session: yolo` 正常路徑

- 觸發：`*config auto-session yolo` → 派發 T0001（有 `關聯 PLAN`、研究工單 D 區段完整）
- 預期：
  - 主面板（[memory-protocol.md](memory-protocol.md) § 塔台狀態面板）顯示 `⚠️ YOLO MODE ACTIVE`
  - Worker 完成後自動回報 `T0001 完成`
  - 塔台 regex 驗證通過 → 讀取 D 區段 → 派發 T0002
  - 顯示派發面板 + 1-2s 緩衝
  - `_tower-state.md` 追加 `[派發]` / `[完成]` 條目

### T5：斷點 A 觸發（Worker 回報異字串）

- 觸發：T4 場景下 Worker 回報 `T0001 執行時遇到問題`（不匹配 regex）
- 預期：
  - 塔台顯示 `⏸ YOLO PAUSED — 斷點 A 觸發` + A/B/C 選項
  - 不派發下一張，等使用者選擇
  - 選 [C] 後 → 退回 ask，`## YOLO 歷程` 追加 `[恢復]`

### T6：斷點 B-1 觸發（Renew ≥N）

- 觸發：T0002 工單 Renew 3 次（設 `yolo_max_retries: 3`），Worker 回報 `T0002 完成`
- 預期：
  - 塔台讀取元資料發現 Renew 次數 ≥3 → 觸發 B-1
  - 顯示 `⏸ YOLO PAUSED — 斷點 B-1` + A/B/C
  - `_tower-state.md` 追加 `[斷點 B-1]`

### T7：斷點 B-2 觸發（連續 N FAILED）

- 觸發：T0003、T0004、T0005 連續回報 `T#### 需要協助`（FAILED），`yolo_max_retries: 3`
- 預期：
  - 第 3 次回報後計數器達 3 → 觸發 B-2
  - `## YOLO 歷程` › `### 計數器` 顯示 `連續 FAILED: 3 / 3`
  - 顯示 `⏸ YOLO PAUSED — 斷點 B-2`

### T8：斷點 C 觸發（Worker 建議跨 PLAN）

- 觸發：T4 場景下 Worker 回報區「Worker 筆記」含 `建議另開 BUG 單處理 XXX 問題`
- 預期：
  - 塔台 regex 匹配 `建議.*開.*BUG` → 觸發 C
  - 顯示 `⏸ YOLO PAUSED — 斷點 C 觸發` + 引用原文
  - A/B/C 選項齊全

### T9：Worker 向塔台提問（v5.5.0+）

- 觸發：T4 場景下 Worker 遇到範圍內的選擇，寫 `### 待塔台決策` Q-1、frontmatter `tower_question: open`，送 `T0001 提問`
- 預期：
  - 塔台 regex 驗證通過，不收單；範圍內 → 寫 `塔台答覆 Q-1` + 決策日誌 + `[提問]` 條目，不暫停
  - Worker 讀到答覆 → 互動紀錄一筆、刪除 `tower_question`、繼續執行
  - 逾時或 `worker_question_timeout: 0` → Worker `BLOCKED` + `T0001 需要協助`，塔台在 Renew 區段答覆後重派（v5.12.0+：派工前先 `--close-worker T0001 … --delay-ms 0` 回收舊分頁）
- BAT 通道（v5.7.0+，BAT `>= 0.7.0-pre.7`）：Worker 寫完並 commit 題目後送 `--ask`（不另送一般通知）→ 塔台 `bat_list_questions` 看到 Q-1 →
  `--answer` exit `0`、工單不寫答覆行 → Worker `bat_wait_question` 收到 `answered` → 互動紀錄註明 BAT 通道、刪除 `tower_question`
- 降級：舊 BAT（`--ask` exit ≠ `0`）→ Worker 在 Q-1 下加 `- **通道**：工單`、commit 後改送一般 `T0001 提問`、塔台看到標記 → 工單答覆，結果同第一個情境；
  等待中 `lost` / `cancelled` → Worker 在 Q-1 下加 `通道` 標記、commit、送一般 `T0001 提問`（v5.7.2）→ 塔台看到標記 → 工單答覆、Worker 剩餘時間讀工單
  （標記寫入前塔台先處理到原本那則通知：列表 `cancelled` 或 `--answer` exit `9`（`cancelled`）→ 同樣工單答覆，之後那則 `提問` 不動作）；`expired` → 同逾時
- 多題（v5.7.1）：Q-1、Q-2 `--ask` 成功、Q-3 失敗 → Worker 三題都送完、Q-3 加 `通道` 標記、commit、最後送一則一般 `T0001 提問` → 塔台每則通知只答
  列表 `pending` 的題（BAT）與有標記的題（工單），列表沒有又沒標記的題先不答 → 每題只有一個通道的答覆

### T10：斷點 D（v5.5.0+）

- 觸發：使用者問進度，塔台 `bat_get_state` 讀到 Worker `blocked`、`blockedDetection: hook`
- 預期：
  - 以分頁標題告知，原因照 `blockedReason` 原值；yolo 寫 `[斷點 D]`，不暫停其他流程
  - 塔台不代答、不送按鍵；不重派、不計入斷點 B
  - 同一個 `blockedSince` 再查到不再告知；`blockedDetection: none` 或沒有該欄位 → 不觸發
  - `blockedReason: tower`（v5.7.0+，codex 分頁也會回）→ 不觸發、不告知使用者；塔台照 § Worker 向塔台提問 › 塔台端 讀題答覆
- 情境 2（v5.8.0+）：codex Worker 讀到 `blocked`、`blockedReason: input`、`source: 'osc'`、`blockedDetection: osc`
  - 與 hook 的 reason 相同：以分頁標題告知（原因顯示 `input`）、不代答、不送按鍵、不暫停其他流程
  - 使用者處理後 codex 還沒送轉換、再讀到同一個 `blockedSince` 的 `input` → 不再告知（使用者輸入不清除 `input`）
  - 同一 codex Worker 也有待答題時，BAT 依優先序回 `input`（不是 `tower`）；`input` 清除後才會讀到 `tower`，那時照 § 塔台端 讀題答覆
  - 舊 BAT 或較舊 codex（`blockedDetection: none`）→ 只可能讀到 `tower`，斷點 D 不觸發（同 v5.7.2）

---

## 引用

- **ct-exec SKILL.md § BAT Notify And Fallback** — Worker skill 端硬鉤子規格（同 v4.2.0 新增）
- **ct-done SKILL.md § BAT Notify** — Worker skill 補救路徑硬鉤子（同 v4.2.0 新增）
- **auto-session.md** — 三階現有行為與 yolo 新增章節
- **BAT `bat-notify.mjs --submit`** — PLAN-020 W1（commit `c4b2a19`，Worker 自動送出機制）
- **BAT CT-T017 § 二 / T0596 / T0597** — `blocked` 狀態與斷點 D（v5.5.0；BAT 權威為 BAT `CLAUDE.md`「blocked 狀態偵測」節與 `docs/agent-guide/blocked-state.md`）
- **BAT CT-T019 / T0607 / T0608 / T0611** — Worker 問塔台的 BAT 通道與 `blockedReason: tower`（v5.7.0；BAT 權威為 BAT `CLAUDE.md`「Worker 問塔台（PLAN-048 / T0607）」節與 `docs/agent-guide/tower-questions.md`）
- **BAT CT-T020 / T0621** — codex 分頁的 OSC 7501：`blockedDetection: osc`、`blockedReason: input`、codex `agentStarted`（v5.8.0；BAT 權威為 T0621「介面契約」C-1–C-8、BAT `CLAUDE.md`「blocked 狀態偵測」「Worker 啟動確認」兩節、`docs/agent-guide/blocked-state.md` 與 `docs/agent-guide/worker-launch-confirmation.md` 的 codex 節）
