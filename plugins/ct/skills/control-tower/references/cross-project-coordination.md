# 跨專案協調（Cross-Project Coordination）

> 定義 Control Tower 跨專案協調的五種類型（三種工單 + 兩種非工單通道）、流程、統籌權規則。
> 搭配 [multi-tower-protocol.md](multi-tower-protocol.md) 使用——
> 本文件處理**跨專案**協調（不同 `_ct-workorders/`），multi-tower 處理**同專案多塔台**。

## 五種協調類型

前三種是**工單**，後兩種是**非工單的跨塔台通道**。

| 類型 | 工單？ | 說明 | 使用情境 |
|------|-------|------|---------|
| **LOCAL** | ✅ | 預設，單專案工單 | 一般任務，省略協調區段 |
| **COORDINATED** | ✅ | 統籌工單，追蹤跨專案整體進度 | 需求影響多個專案時，由主專案建立 |
| **DELEGATE** | ✅ | 受派工單，參照統籌工單或 HANDOVER 執行 | 接收專案依據子任務描述建立 |
| **HANDOVER** | ❌ | 受理**前**的發現＋提案，尚未成為工單 | 跨塔台發現對方負責的問題，但修法待對方判斷；對方受理後才轉 DELEGATE |
| **ADVISORY** | ❌ | 純意見，**不期待對方動作** | 對他方的可選強化提供評估，明確不主張必改 |

> 🔴 **HANDOVER / ADVISORY 不是工單。**
> 不進工單編號序列（不佔 `T####` / `CP-T####`）、不計入熱區統計、不受 `*sync` 狀態掃描管轄。
> 詳見 [§ HANDOVER 與 ADVISORY](#handover-與-advisory非工單跨塔台通道)。

### 為什麼原本的三種不夠

三個實證缺口（2026-09-01，CP-T0113 自身的處理過程即為證據）：

| # | 缺口 | 說明 |
|---|------|------|
| 1 | **無「受理前提案」形狀** | `COORDINATED` 預設統籌塔台已知各專案該做什麼（`affected-projects[].task` 為既定子任務）。但常見情境是「我查到這些、我猜你們該這樣改、你們自己判斷」，發起方**無權也無資訊**替對方定義子任務。三種類型無此位置 → **HANDOVER**。 |
| 2 | **無「純諮詢、不期待動作」通道** | 對他方專案提出可選強化意見時，若為它開 DELEGATE，會把「意見」誤表述成「派工」，逼對方在沒有承諾的事情上背狀態 → **ADVISORY**。 |
| 3 | **無「異議／更正來源塔台前提」欄位** | DELEGATE 的回報區是**完工回報**用，不是**動工前反駁前提**用。來源塔台的根因描述可能有誤，而**接受錯誤的根因會導致錯誤的修法** → 見 [§ 回覆稿的異議段落](#回覆稿的異議段落)。 |

### LOCAL（預設）

一般工單，不涉及跨專案。工單格式不變，**省略跨專案協調區段**。

### COORDINATED（統籌工單）

由「誰先碰到需求或受影響最大」的專案塔台建立。工單元資料新增：

```yaml
coordination:
  type: COORDINATED
  affected-projects:
    - name: project-b
      prefix: PB
      task: "更新共用介面以配合新欄位"
    - name: project-c
      prefix: PC
      task: "同步 API schema 變更"
  status: PENDING  # PENDING → IN_PROGRESS → DONE（全部子任務完成）
```

### DELEGATE（受派工單）

接收專案的塔台建立，參照統籌工單的子任務描述。工單元資料新增：

```yaml
coordination:
  type: DELEGATE
  source:
    project: project-a
    prefix: PA
    workorder: PA-T0012-api-schema-v2  # 統籌工單編號
    task-ref: "同步 API schema 變更"   # 對應的子任務描述
```

## HANDOVER 與 ADVISORY（非工單跨塔台通道）

### 定位

| | HANDOVER | ADVISORY |
|---|---|---|
| 期待對方動作？ | 是，但**修法由對方決定** | 否，明確不主張必改 |
| 進工單序列？ | 否 | 否 |
| 計入熱區統計？ | 否 | 否 |
| 受 `*sync` 掃描？ | 否 | 否 |
| 受 `*archive` 管轄？ | 可比照工單歸檔 | 可比照工單歸檔 |
| 後續 | 對方受理 → 對方建立 DELEGATE 工單 | 無強制後續 |

HANDOVER 被受理時，**接收塔台**建立 DELEGATE 工單，並以
`coordination.source.workorder` 指回該 HANDOVER 檔名。
HANDOVER 本身不改狀態成 `DONE`——它的終點是 `ACKNOWLEDGED` 或 `DECLINED`。

### 命名與落點慣例

- `_handover-<YYYY-MM-DD>-<主題>.md` — **發起方**寫在**自己**的 `_ct-workorders/`
- `_reply-<YYYY-MM-DD>-<主題>.md` — **接收方**寫在**自己**的 `_ct-workorders/`
- `_` 前綴使兩者落在工單編號序列之外，`*sync` 的 `T####` 掃描不會命中

> 🔒 **維持既有唯讀原則**：接收塔台只讀不寫來源專案的檔案。
> 回覆稿一律寫在自己的 repo，由使用者轉交，塔台不得跨 repo 寫入。
> v5.9.0+：Claude Code 塔台可另用跨 session 訊息通知對方塔台，收件人怎麼選見下方 § 跨 session 選收件人；找不到收件人時仍由使用者轉交。

### frontmatter 欄位

```yaml
schema_version: 1
schema_kind: cross-tower-handover      # 回覆稿用 cross-tower-handover-reply
from: project-a                        # 發起方專案
to: BMad-Guide                         # 接收方專案
in_reply_to: _handover-2026-09-01-bat-workspace-allocation   # 僅回覆稿需要
status: DRAFT                          # DRAFT → ACKNOWLEDGED / DECLINED
local_workorder: CP-T0113              # 受理後建立的 DELEGATE 工單編號；未受理留空
created_at: "2026-09-01T20:48:28+0800"
```

`status` 語意：

| 值 | 意義 |
|---|---|
| `DRAFT` | 已寫成，尚未送達或尚未答覆 |
| `ACKNOWLEDGED` | 接收方受理，`local_workorder` 必須填入所建立的 DELEGATE 工單編號 |
| `DECLINED` | 接收方不受理，回覆稿須載明理由 |

ADVISORY 使用同一組檔名與欄位，`schema_kind` 為 `cross-tower-advisory`，
且**不得**填 `local_workorder`——填了就表示它其實是 HANDOVER。

### 範例（本次實例，三份文件）

2026-09-01 專案 A 塔台 → BMad-Guide 塔台的 BAT workspace 錯派議題，產出正是這個形狀：

| 檔案 | 角色 |
|---|---|
| `project-a/_ct-workorders/_handover-2026-09-01-bat-workspace-allocation.md` | HANDOVER — 發起方寫在自己 repo |
| `BMad-Guide/_ct-workorders/_reply-2026-09-01-bat-workspace-allocation.md` | 回覆稿 — 接收方寫在自己 repo，含根因更正與 C-4 不採納理由 |
| `BMad-Guide/_ct-workorders/_handover-2026-09-01-bat-workspace-default-opinion.md` | ADVISORY — 轉給 BAT 專案塔台的 B-1/B-2 意見，明確不主張必改 |

受理結果：BMad-Guide 塔台建立 DELEGATE 工單 `CP-T0113`，
其 `coordination.source.workorder` 指回該 HANDOVER。

### 回覆稿的異議段落

`_reply-*.md` **允許並鼓勵**「更正來源塔台前提」段落。

理由：**接受錯誤的根因描述會導致錯誤的修法。**
本次來源交辦稿診斷為「`--workspace` 未見於 CT skill」，實際查證是該 flag 自 v4.2.2 起即存在，
真正缺陷是 `control-tower/SKILL.md` 的派工行是**有損摘要**，看起來像完整旗標清單。
若照原稿診斷去修，只會補一個 flag，不會處理「摘要看起來像完整清單」這個根本失效模式——
下一個被省略的旗標會原樣重演。

異議段落應包含：來源前提原文、查證結果與證據（檔案:行號）、修正後的根因、以及對修法的影響。
異議不是拒絕受理；受理與更正前提可以同時成立。

### 跨 session 選收件人（v5.9.0+）

> 本小節是「塔台用跨 session 訊息通知另一個專案的塔台時，收件人怎麼選」的**唯一權威定義**。
> `SKILL.md`、[auto-session.md](auto-session.md) 只放摘要並引用這裡。BAT 介面以 BAT T0643 回報區「PLAN-050 介面契約總表」C-1–C-8
> 與 BAT `docs/agent-guide/claude-session-name.md` 為準（BAT CT-T021；D069），CT 不得更改名稱格式、欄位、值域或錯誤碼語意。

**適用**：Claude Code 塔台用 Claude Code 現有的跨 session 訊息（ListAgents 列出 session、SendMessage 送訊息）把 HANDOVER、回覆或通知送給
**另一個專案的塔台**時。Codex 塔台沒有這兩個 tool，不適用，照上方 § 命名與落點慣例 由使用者轉交。

**為什麼**：Claude Code 未命名的 session 在 ListAgents 上叫「工作目錄名＋兩字元」（例 `better-agent-terminal-93`），分不出塔台與 Worker。
2026-10-18 曾把 CT-T020 完成回覆送給 `better-agent-terminal-d1`，對方其實是 BAT T0627 的 Worker；另一次只能靠使用者截圖與 idle／busy 狀態
推定 `-93` 是塔台（D067）。

**名稱格式**（BAT `>= 0.7.1-pre.1` 開的 claude-cli 分頁，BAT 啟動時以 `--name` 命名；完整規則、清理與降級見 BAT 權威 C-1–C-3）：

| 名稱 | 是誰 |
|---|---|
| `<工作區> · Worker · <T####>` | BAT 派出的 claude Worker（helper 派工帶 `--skill` + `--workorder`；工單編號可帶前綴，例 `CT-T021`）。遠端 headless 派工的 `<工作區>` 是 `BAT` |
| `<工作區> · Tower` | 使用者以 BAT「以塔台開啟 Claude」開的分頁。🔴 BAT 只負責命名，不代表該分頁已啟動塔台或已 `--set-role tower` |
| `<工作區> · <短 ID>` | 其他 claude-cli 分頁（含從一般分頁開的塔台）；`<短 ID>` 是 terminal id 去 `-` 的前 6 碼小寫 |

分隔字元是 ` · `（空白、U+00B7、空白）。`<工作區>` 是 BAT 工作區的 alias 或名稱，不一定等於 repo 目錄名。
Worker 的名稱由 BAT 加，CT 派工命令不變、不用做任何事。
下文的「目標工作區」指對方專案在 BAT 的工作區名稱（常與 repo 目錄名相同；不確定時不要猜，靠第 2 步的 `workspaceName` 或走第 3 步）。

**選收件人的順序**（依序，命中就停）：

1. **ListAgents 名稱**：有 `<目標工作區> · Tower` → 送它。同名多列（同一工作區開了兩個「以塔台開啟」分頁，或兩個工作區同名）→ 附該列的 `[ref]`；
   分不出該送哪一列 → 改用第 2 步對照。
2. **BAT 塔台清單**：只在**自己在 BAT 內、且本 session 已宣告塔台**（[auto-session.md](auto-session.md) § 塔台分頁角色宣告 exit `0`，面板 `分頁標題` 為 `已設定`）時做。
   呼叫 MCP `bat_list_terminals`、`scope: towers`（helper CLI 沒有對應的 list 參數），在回傳中找 `workspaceName` 等於目標工作區、`self: false` 的列，
   取它的 `claudeSessionName`，到 ListAgents 找**完全相同**的名稱再送；同名多列仍附 `[ref]`。以下情況都算「找不到」，進第 3 步：
   - 該列 `claudeSessionName: null`：codex 塔台、在 shell 手動打 `claude` 開的塔台、BAT 沒注入名稱（使用者自訂參數已有 `--name`、system claude 太舊等）。
   - 沒有符合的列、`workspaceName` 為 `null`（headless）、或符合的列不只一列而對不出是哪個。
   - ListAgents 沒有同名的 session（例如對方在 session 中 `/rename` 過）。
   - 呼叫回錯誤：`INVALID_ARGS`（`scope` 不支援 = 舊 BAT）、`NOT_OWNER`（自己還沒宣告塔台）、MCP client 依舊 BAT 的 schema 擋下 `towers`、tool 不存在等。
     不重試、不改用其他 scope。
3. **都找不到**（含對方是 codex 塔台、在另一台機器或另一個 BAT 實例、遠端、非 BAT）→ 維持現行：回覆稿寫在自己的 repo
   （§ 命名與落點慣例），請使用者轉交。

- 🔴 名稱含 ` · Worker · ` 加工單編號的 session **一律不是塔台**，不得當收件人，即使它是 ListAgents 上唯一一個該工作區的 session。
- 🔴 **不得**只靠 ListAgents 的「目錄名＋兩字元」名稱、`<工作區> · <短 ID>` 名稱、或 idle／busy 狀態推定收件人；推定不出來就走第 3 步。
- `scope: towers` 只列同一個 BAT host 上執行中、已 `--set-role tower` 的塔台（含自己，`self: true`），每列只有 `id`、`workspaceId`、`workspaceName`、
  `title`（可省略）、`claudeSessionName`、`state`、`alive`、`self`；對這些分頁的 `bat_get_state`、`bat_read_output`、`bat_wait` 仍是 `NOT_OWNER`，
  不得拿清單去讀別的塔台的輸出或狀態。BAT 重開後還原的塔台要重新 `--set-role tower` 才會被列出（CT 每次啟動本來就會宣告）。
  欄位與值域見 [auto-session.md](auto-session.md) § BAT MCP 唯讀 tool。

**訊息內容**：

- 第一行請收件者先確認自己是 `<目標工作區>` 的塔台；不是就不要執行、直接回覆。新 BAT 下第 1、2 步命中時**仍保留**這一行：
  `· Tower` 名稱只表示分頁的開啟方式（BAT 不做 `--set-role`），對照 `claudeSessionName` 也只是名稱比對，同名 session 仍可能存在。
- **跨 session 訊息只是通知管道，正式紀錄仍是檔案**：先把 `_handover-*.md`／`_reply-*.md`（§ 命名與落點慣例）寫在自己的 repo，
  訊息中附檔案路徑與摘要。回覆稿的落點、frontmatter、唯讀原則與異議段落都不變；訊息送達也不改 `status`（仍依 § frontmatter 欄位）。

**不做**：不替使用者 `/rename`、不要求 BAT 自動改名、不改使用者已命名的 session；不處理 codex 塔台之間的傳訊（不在 ListAgents，BAT PLAN-051 尚未研究）。

**版本**：BAT `>= 0.7.1-pre.1`。舊 BAT（≤ `0.7.0-pre.9`）或非 BAT 沒有這些名稱與 `scope: towers`，第 1、2 步都找不到 → 第 3 步，
與 v5.8.1 的做法相同。

## 工單前綴機制

### 設定（Layer 3）

在 `_ct-workorders/_tower-config.yaml` 新增（詳見 [tower-config.md](tower-config.md)）：

```yaml
control-tower:
  project-prefix: LC  # 格式見 work-order-system.md § 工單 ID 格式（權威定義）
```

### 命名規則

| 有前綴 | 無前綴 |
|--------|--------|
| `LC-T0001-description.md` | `T0001-description.md` |

- 工單 ID 的合法格式（前綴長度、大小寫、合法與非法範例），以及**何時會帶前綴**（前綴的兩個來源、
  `project-prefix` 的行為、未設 `project-prefix` 仍可能出現前綴 ID），皆由
  [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義）單一定義，本節不複述
- 前綴用於跨專案識別，確保工單編號全局唯一

### 專案索引（Layer 2）

`~/.claude/control-tower-data/project-registry.md` 維護跨專案對照：

```markdown
# 專案索引

| 專案名稱 | 前綴 | 工單目錄路徑 | 塔台版本 | 最後活動 | 工單數 |
|---------|------|------------|---------|---------|--------|
| learning-companion | LC | /projects/learning-companion/_ct-workorders/ | v3.3 | 2026-03-31 | 15 |
| my-engine | ME | /projects/my-engine/_ct-workorders/ | v3.3 | 2026-03-31 | 8 |
```

> 格式定義已包含在 [data-layer-architecture.md](data-layer-architecture.md)。
> 塔台首次設定 `project-prefix` 時，自動更新此索引。

## _cross-references.md

每個專案的 `_ct-workorders/_cross-references.md`（Layer 3）記錄跨專案工單關聯。

### 格式

```markdown
# 跨專案參照

> 自動維護。COORDINATED 或 DELEGATE 工單建立/完成時追加。

| 主題 | 本地工單 | 對方工單 | 來源專案 | 日期 | 說明 |
|------|---------|---------|---------|------|------|
| API schema v2 | LC-T0012 | ME-T0008 | my-engine | 2026-03-31 | 統籌→受派 |
| Redis 設定同步 | LC-T0015 | ME-T0011 | my-engine | 2026-04-01 | 受派→統籌 |
```

### 更新時機

- COORDINATED 工單建立時 → 追加一行（說明欄標「待派發」）
- HANDOVER 送出／收到時 → 各追加一行（說明欄標「待受理」；受理後更新為所建立的 DELEGATE 工單編號）
- DELEGATE 工單建立時 → 雙方專案各追加一行
- DELEGATE 工單完成時 → 更新說明欄
- 塔台建立新工單前 → 先查此檔案，若發現相關主題則提醒使用者

## 跨專案協調流程

```
Step 1: 統籌塔台建立 COORDINATED 工單（含各專案子任務描述）
           ↓
Step 2: 使用者到接收專案的塔台，告知來源工單
           ↓
Step 3: 接收塔台【唯讀讀取】來源統籌工單，建立 DELEGATE 工單
           ↓
Step 4: Sub-session 執行 DELEGATE 工單
           ↓
Step 5: 使用者回統籌塔台回報，統籌塔台讀取對方工單確認
           ↓
Step 6: 統籌工單狀態更新（全部子任務完成 → DONE）
```

### 詳細步驟

#### Step 1：建立統籌工單

統籌塔台識別到任務影響多個專案時：

1. 列出受影響的專案及各自需要做的事
2. 建立 COORDINATED 工單，`coordination.affected-projects` 列出子任務
3. 更新本專案 `_cross-references.md`

#### Step 2-3：派發 DELEGATE 工單

使用者切到接收專案的塔台，告知：

- 「有來自 `<prefix>-T<number>` 的跨專案任務」
- 接收塔台**唯讀讀取**來源工單（不修改），理解子任務描述
- 建立 DELEGATE 工單，`coordination.source` 記錄來源
- 更新雙方 `_cross-references.md`

> **唯讀原則**：接收塔台只讀不寫來源專案的工單檔案。所有修改只發生在自己專案的 `_ct-workorders/`。

#### Step 4-5：執行與回報

- 執行 DELEGATE 工單（標準 /ct-exec 流程）
- 完成後，使用者回統籌塔台回報
- 統籌塔台讀取 DELEGATE 工單確認完成

#### Step 6：統籌工單收尾

所有 affected-projects 的對應 DELEGATE 工單皆 DONE：

- 統籌工單標記 DONE
- 更新 `_cross-references.md`

## 統籌權規則

| 原則 | 說明 |
|------|------|
| **不固定** | 統籌權不綁定特定專案，隨需求而定 |
| **誰先碰到** | 先發現需求的專案自然成為統籌者 |
| **影響最大** | 受影響最大的專案可主動接手統籌 |
| **共用程式庫** | 共用庫（如 common/shared）不設工單目錄，由受影響最大的服務代理統籌 |

### 統籌權轉移

若原統籌專案發現另一專案更適合統籌：

1. 在統籌工單標記「統籌權轉移」
2. 新統籌專案建立新的 COORDINATED 工單（引用原工單）
3. 原統籌工單改為 DELEGATE

## v4 功能整合

### `*sync` 與 CP 工單

`*sync` 掃描時，CP 前綴工單（如 `CP-T0012-xxx.md`）視為標準工單處理——前綴 ID 的合法性依 [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義）：

- 歸入 sprint-status.yaml 同步
- 狀態追蹤與一般工單一致
- `_cross-references.md` 由 `*sync` 在步驟 8（計數器驗證）後額外掃描 CP-前綴工單，驗證參照表與實際工單狀態一致

### `*sync`、`*archive` 與 HANDOVER / ADVISORY

HANDOVER 與 ADVISORY **不是工單**，因此：

- **不受 `*sync` 狀態掃描管轄**——不進 sprint-status.yaml、不計入工單計數器、不參與 drift 檢查。
  `_` 前綴使 `T####` 掃描自然不會命中，無需額外排除規則。
- **不計入熱區統計**。
- **`*archive` 可比照工單歸檔**：`status` 為 `ACKNOWLEDGED` 或 `DECLINED` 且超過 `archive_days`
  即為歸檔候選。ADVISORY 無受理概念，以 `DRAFT` 起算。
- HANDOVER 已 `ACKNOWLEDGED` 但其 `local_workorder` 指向的 DELEGATE 工單尚未最終態
  → **豁免歸檔**（比照下方 CP 工單豁免規則，理由相同：完成狀態取決於雙方）。

### `*archive` 與 CP 工單

CP 工單歸檔需要特殊處理——跨專案工單的完成狀態取決於雙方：

**CP 工單歸檔豁免規則**：
- COORDINATED 工單：本地標記 DONE，但 `affected-projects` 中有尚未完成的 DELEGATE → **豁免歸檔**
- DELEGATE 工單：本地標記 DONE，但對應 COORDINATED 工單尚未 DONE → **豁免歸檔**
- 雙方皆 DONE → 正常歸檔流程（遵循 `archive_days` 設定）

**檢查方式**：
1. 歸檔候選掃描時，偵測 `coordination.type` 為 COORDINATED 或 DELEGATE
2. COORDINATED：讀取 `affected-projects`，Grep 對方工單狀態
3. DELEGATE：讀取 `coordination.source.workorder`，確認統籌工單狀態
4. 任一對方工單非最終態 → 從歸檔候選中移除，標記「CP 豁免」

### `_cross-references.md` 自動維護

| 觸發事件 | 自動更新動作 |
|---------|------------|
| 建立 COORDINATED 工單 | 追加一行，說明欄標「待派發」 |
| 送出／收到 HANDOVER | 各追加一行，說明欄標「待受理」 |
| HANDOVER 受理 | 更新說明欄為所建立的 DELEGATE 工單編號 |
| HANDOVER 不受理 | 更新說明欄為「DECLINED」＋回覆稿檔名 |
| 建立 DELEGATE 工單 | 雙方專案各追加一行 |
| DELEGATE 工單完成 | 更新說明欄（✅ 完成） |
| COORDINATED 工單完成 | 更新說明欄（✅ 全部完成） |
| `*sync` 執行 | 驗證參照表與實際 CP 工單狀態一致 |

## 降級行為

| 情境 | 行為 |
|------|------|
| 單專案使用 | 完全不涉及本機制，所有工單為 LOCAL |
| 無 `project-prefix` | 跨專案時塔台提示設定前綴 |
| 無 Layer 2 project-registry | 靜默降級，手動告知對方工單路徑 |
| 對方專案路徑不可達 | 使用者手動複製工單內容 |
