# 工單系統

## 工單編號規則

> 🔴 **下方「工單 ID 格式（權威定義）」小節是全庫工單 ID 格式的唯一事實來源。**
> 其他 reference（`auto-session.md`、`cross-project-coordination.md`、`archive-system.md` 等）
> 與各 Worker skill 一律**交叉引用**本節，**不得自行複述格式正則**。
>
> 這條規則有代價換來的理由：v5.0.6 之前，CT 內部對「工單 ID 可否帶前綴」有五處敘述、
> 兩種相反立場（`auto-session.md` 說只能 `T` + 數字，`cross-project-coordination.md` 說跨專案強制帶前綴）。
> 各處自己都自洽，合起來牴觸。逐處改寫只會讓下次再度發散——**收斂成一處定義才是修法**。

### 工單 ID 格式（權威定義）

**權威正則**：

```
^(?:[A-Z]{2,4}-)?T\d+$
```

即：**可選**的 2–4 位大寫英文前綴 + 連字號，後接 `T` + 純數字流水號。
工單**檔名**在此 ID 後再接 `-<簡短描述>.md`。

| | 值 | 說明 |
|---|---|---|
| ✅ 合法 | `T0115` | 無前綴，單專案標準形式 |
| ✅ 合法 | `CP-T0113` | 跨塔台交辦慣例前綴 |
| ✅ 合法 | `LC-T0001` | `project-prefix: LC` 自動加上 |
| ✅ 合法 | `ME-T0015` | 同上 |
| ❌ 非法 | `cp-T0113` | 前綴必須大寫 |
| ❌ 非法 | `PROJ-T0001` | 前綴超過 4 字元 |
| ❌ 非法 | `C-T0001` | 前綴少於 2 字元 |
| ❌ 非法 | `T0115 完成` | 含空白 |
| ❌ 非法 | `T0115; rm -rf /` | 含 shell 元字元 |
| ❌ 非法 | `T-0115`、`TASK0115` | 主體不是 `T` + 純數字 |

**前綴的來源有二，兩者都會產生合法的前綴 ID**：

1. **`project-prefix` 設定**（見 [tower-config.md](tower-config.md)）——一旦設定，塔台派發工單時
   **無條件**自動加前綴，不分是否為跨專案工單。
2. **跨塔台交辦的既有慣例**（如 `CP-`）——由他方塔台或人工建立的 COORDINATED / DELEGATE 工單，
   **不經 `project-prefix` 產生**（見 [cross-project-coordination.md](cross-project-coordination.md)）。

> 🔴 **未設定 `project-prefix` 的專案，一樣可能出現前綴 ID。**
> 這是 2026-09-02 這次規則牴觸的實際引信，任何「本專案沒設 `project-prefix`，所以只會看到無前綴 ID」
> 的假設都是錯的。實例：BMad-Guide repo 的 `_tower-config.yaml` 是 `project-prefix: ""`，
> 熱區卻有 8 張 `CP-T####` 工單；2026-09-01 派發 CP-T0113 時，即因下游驗證器只認無前綴 ID 而被擋，
> 塔台被迫改走 `--prompt` 繞道。

**本正則的適用範圍**（凡是判定「這是不是一個合法工單 ID」的地方，都用它，不另立規則）：

- 工單檔名前段與 frontmatter `id` 欄位的合法值
- BAT `--workorder` 參數的合法值，以及該參數的**防注入白名單**
  （見 [auto-session.md](auto-session.md) § 安全邊界）
- BAT `--close-worker` 參數的合法值（v5.1.0+，見本檔 § 回報處理流程與
  [auto-session.md](auto-session.md) § 安全邊界）
- `*sync` / `*archive` 掃描時辨識工單檔案的依據（見 [archive-system.md](archive-system.md)）
- 跨專案參照表 `_cross-references.md` 的工單欄位

本正則仍是**嚴格白名單**：相對於「僅 `T` + 數字」，只多放行 2–4 位大寫字母加一個連字號，
不含空白、引號、路徑分隔字元或任何 shell 元字元，注入面未放寬。

### 在其他正則中引用本定義

其他文件若需把工單 ID **組合**進更大的正則（例如比對 Worker 回報字串），
一律使用具名片段 **`<WORKORDER_ID>`**，代表本正則的**無錨點主體**：

```
<WORKORDER_ID>  ≡  (?:[A-Z]{2,4}-)?T\d+
```

🔴 **不得就地展開**成字面正則。展開就是複製一份定義，下次改動必然漏改一處
——`yolo-mode.md` 斷點 A 的回報字串比對曾寫死無前綴形式，帶前綴工單（`CP-T0113 完成`）
因此無法匹配，正是這種漏改的實例。

> BUG / PLAN / EXP 單據不適用本正則，其編號規則見 [bug-plan-system.md](bug-plan-system.md)。

### 回報與通知用的工單 ID（完整 ID，v5.13.1+）

> 🔴 本節是「Worker 回報、通知、提問時工單 ID 怎麼寫」與「送出前比對」的**唯一權威**。
> `ct-exec`、`ct-done`、[auto-session.md](auto-session.md)、[yolo-mode.md](yolo-mode.md) 與安裝指南的通知範本一律引用本節，不複述。

**規則**：Worker 送給 BAT 或塔台的工單 ID 一律是**工單完整 ID**——`/ct-exec`（`/ct-done`）收到什麼 ID 就照原樣用，
它等於工單 frontmatter `id`，**含前綴，不得截短**成 `T` 加數字。適用於：

- `bat-notify.mjs` 的 `--source` 與訊息字串（`完成`／`部分完成`／`需要協助`／`提問`／`失敗`）
- `bat-notify.mjs --ask --source` 與它的訊息字串
- 手動備援訊息（剪貼簿、畫面上「回塔台回報時輸入」的文字）

範本一律寫 `<工單 ID>`，不寫 `T####`：

| 工單 frontmatter `id` | `--source` | 通知訊息 |
|---|---|---|
| `T0341`（無前綴） | `--source "T0341"` | `T0341 完成` |
| `LB-T0184`（有前綴） | `--source "LB-T0184"` | `LB-T0184 完成` |
| `LB-T0184` | ❌ `--source "T0184"` | ❌ `T0184 完成` |

> 為什麼（D422）：範本原本寫 `T####`，Worker 會照「T 加四位數字」的形狀從 `LB-T0184` 截出 `T0184`。
> BAT 用 `--source` 比對 Worker 分頁登記的工單，對不上就無法把分頁標成 Done、無法一次關掉已完成的 Worker 分頁。
> 某個設了前綴的專案實測：回報 87 次帶前綴、43 次沒帶，隨機發生。

**送出前比對（Worker）**：每次送通知、`--ask` 或顯示手動備援訊息之前，把要用的 ID 和工單 frontmatter `id` 比對：

1. 取期望值：frontmatter `id`；舊單沒有 `id` 時，取檔名開頭到第一個 `T\d+` 為止的那段（例 `LB-T0184-fix-auth.md` → `LB-T0184`）。
2. 一致 → 照送。
3. 不一致 → 改用期望值再送，並在工單回報區記一行「通知 ID 已更正：`<原值>` → `<期望值>`」。
   收尾通知通常在工單 commit 之後才送，這一行記在下一次寫工單時，或在畫面上告訴使用者；不為了這一行另外 commit。

塔台端收到缺前綴的 ID 時怎麼處理，見下方 § 回報處理流程 › 回報 ID 對不上時。

### 編號配置規則

- 流水號從 `0001` 開始，單調遞增
- 描述使用小寫英文，單字以 `-` 分隔
- 範例：`T0001-create-project-context`、`T0015-fix-auth-bug`
- 前綴範例：`LC-T0001-create-project-context`、`ME-T0015-fix-auth-bug`
- 塔台維護當前最大編號，每次產生新工單自動遞增
- 前綴是否強制、由誰產生，見上方權威定義節；跨專案協調（COORDINATED / DELEGATE）規範見
  [cross-project-coordination.md](cross-project-coordination.md)

## 工單目錄結構

```
your-project/
├── _ct-workorders/
│   ├── T0001-create-project-context.md
│   ├── T0002-create-prd.md
│   ├── _tower-state.md           ← 塔台記憶
│   ├── _decision-log.md          ← 決策日誌
│   ├── _learnings.md             ← 學習紀錄
│   ├── _cross-references.md      ← 跨專案參照
│   ├── _playbooks/               ← 自動生成的操作範本
│   └── _tower-config.yaml        ← 專案設定
├── _bmad-output/                 ← BMad 產出（若使用）
├── src/
└── ...
```

## 工單粒度原則

每張工單 = 一個 BMad 工作流程（或一個明確交付物）：
- 單一職責：不合併多個工作流程到同一工單
- 完整可交付：sub-session 完成後有明確產出
- 可中斷可恢復：PARTIAL 時可基於已完成部分產生接續工單
- 已驗證有效：6 工單 / 90 分鐘 / 44 檔產出（Keenbest 逆向工程實測）

## Story → Dev 之間的品質檢查點

Story 產生後、Dev 實作前，塔台根據以下條件決定是否插入獨立審查：

| 條件 | 塔台動作 |
|------|---------|
| 使用 BMad `bmad-create-story` 或 `bmad-build` | `bmad-create-story` 是保留的 shim；Story 拆分走 `bmad-spec` Story Breakdown，審查在 `bmad-build` 的 Review Triage——**不能因為用了 story 就省略審查**。用 `bmad-build` 時看 Review Triage 是否有跑（spec 的 `## Review Triage Log`），沒跑就照下列條件另派審查工單 |
| 高風險 Story（涉及安全、金流、資料遷移） | 派發**獨立審查工單**（Adversarial Review），用不同 session 交叉驗證 |
| Story 跨多個子專案或影響共用模組 | 派發**獨立審查工單**，確認跨專案影響已涵蓋 |
| 無 BMad 的自訂流程 | 塔台**主動提議** review 步驟：「Story 已產生，建議先審查再開發，要派審查工單嗎？」 |
| 使用者明確跳過 | 記錄到 `_decision-log.md`，標注「使用者選擇跳過 Story Review」 |

### 審查工單的 Session 原則

獨立審查工單必須在**不同 session** 執行（避免確認偏誤）。工單 Session 建議自動設為 🆕 新 Session。

### 搭配品質閘門

若獨立審查回報包含 CRITICAL/HIGH 發現 → 強制派發修正工單，修正完成後才派發開發（`bmad-build`）工單。（同「審查→修正→交付」三步驟規則）

## 派發流程

每次派發任務時，塔台：

1. **學習查詢**（靜默）：讀取 `_learnings.md`，比對決策模式的觸發條件
2. **工作流程選擇**：若有外部 `bmad-guide` skill（去哪裡找見 [enhancement-integration.md](enhancement-integration.md) § Level 2 › 偵測）→ 自動查 `workflow-map.md` / `supplementary-workflows.md` / `ecosystem-modules.md`；無 → 使用者手動指定
2.5. **派發前 overlap check**（v4.4.0+）：比對本次工單的 `affects_files` 與目前 IN_PROGRESS 工單的 `affects_files`，依交集嚴重度決定 BLOCK / WARN / 放行（見下方「派發前 overlap check」）
3. **產生工單檔案**：寫入 `_ct-workorders/T<編號>-<描述>.md`（見 work-order-template.md）
4. **畫面顯示摘要**：

```
📋 工單已建立：T0001-create-project-context
   任務：建立專案上下文
   工作流程：bmad-project-context（setup intent）
   預期產出：`AGENTS.md` 的專案上下文區塊
   工單路徑：_ct-workorders/T0001-create-project-context.md

👉 建議開 🆕 新 Session

🚀 開新 Session 執行：
/ct-exec T0001

📋 回塔台回報時輸入：T0001 完成
```

**派發後行為**（依 `auto-session` 設定，詳見 [auto-session.md](auto-session.md)）：
- `on`：靜默開新分頁 + 同時顯示文字提示
- `ask`：互動式提問（開新分頁 / 複製到剪貼簿 / 自己來）
- `off`：僅顯示文字複製提示（傳統行為）

5. **更新進度表**
6. **更新 _tower-state.md**（最大工單編號、進度快照）

### BMad v6.10+ workflow 派發注意

| Workflow | Tower 派發規則 |
|----------|----------------|
| `bmad-architecture` | 新工單使用此名稱；`bmad-create-architecture` 僅視為舊名 / compatibility shim |
| `bmad-build-auto` | 視為 autonomous single-iteration；工單必須要求 durable artifact、spec frontmatter terminal status、`baseline_revision`、commit 範圍 `baseline_revision..HEAD`（多個 story：`baseline_revision..下一個 story 的 baseline_revision`） |
| `bmad-loop` | 不直接當一般工單 workflow；先確認 opt-in module 已安裝且 `bmad-loop-setup` 已完成 |
| `bmad-investigate` | 不派發；v6.10.0 retired，改開 CT research workorder 或一般調查 |
| `bmad-automator` | 不建議新工單；deprecated，提示遷移到 `bmad-loop`（循環）或 `bmad-build-auto`（無人值守單次迭代） |

## 派發前 overlap check（v4.4.0+）

多張工單平行執行時（不同 sub-session / worktree），若兩張工單修改相同檔案會導致 merge conflict 或互相覆蓋。塔台在派發前依工單元資料的 `affects_files` 做 **static overlap check**，在派發瞬間攔截高風險組合。`affects_files` 的填寫規則見 [work-order-template.md](work-order-template.md) §「填寫 `affects_files` 指引」。

### 判斷邏輯（偽碼）

```
input:
  new_wo.affects_files   # 本次要派發的工單
  in_progress_wos        # _tower-state.md 中狀態為 IN_PROGRESS 的工單清單

# 向下相容：未宣告 affects_files 的工單視為 `*`
if new_wo.affects_files is empty:
    new_wo.affects_files = ['*']
for wo in in_progress_wos:
    if wo.affects_files is empty:
        wo.affects_files = ['*']

# 比對每一張 IN_PROGRESS 工單
for wo in in_progress_wos:
    sev = compare(new_wo.affects_files, wo.affects_files)
    if sev == "exact":        # 交集包含完全相同的檔案路徑
        action = 🚨 BLOCK
    elif sev == "wildcard":   # 任一方標 `*`（全專案）
        action = ⚠️ WARN
    elif sev == "same_dir":   # 同目錄不同檔案（例：同 _ct-workorders/ 下的不同工單檔）
        action = ⚠️ WARN
    else:
        action = ✅ PASS
    collect(wo, action)

# 顯示最嚴重的判定給使用者
if any BLOCK:
    show_block_prompt()   # 列出衝突工單 + 衝突檔案清單，要求明確確認
elif any WARN:
    show_warn_prompt()    # 列出潛在衝突，允許 [Y] 繼續 / [N] 取消
else:
    proceed_to_dispatch()
```

### 判定行為

| 判定 | 觸發條件 | 塔台動作 |
|------|---------|---------|
| 🚨 **BLOCK** | 與任一 IN_PROGRESS 工單有完全相同檔案路徑 | 顯示衝突清單，要求使用者輸入 `確認接受衝突` 才繼續；否則取消派發 |
| ⚠️ **WARN（wildcard）** | 任一方 `affects_files` 為 `*`（或未宣告→保守視為 `*`） | 顯示警告，`[Y/N]` 提示是否繼續 |
| ⚠️ **WARN（same_dir）** | 同目錄但不同檔案（僅目錄層標註時觸發） | 同上 |
| ✅ **PASS** | 無交集 | 正常派發 |

### Static 性質（不做 runtime watch）

- **只做字面比對**：以工單元資料的 `affects_files` 為準，**不追蹤** Worker 執行期間實際動了哪些檔案
- **失真容忍**：若 Worker 實際動的檔案超出宣告範圍，不是本機制責任；落差素材由 \*evolve 歸納
- **理由**：runtime file watcher 複雜度高（需要長駐程序 + IPC），在 Phase 2 不納入範圍；static check 已能攔截大多數典型衝突

### 向下相容

- 未含 `affects_files` 的舊工單 → 保守視為 `*` → 任何平行派發都 WARN
- 保守預設鼓勵使用者補填新工單，同時不 break 既有流程
- 單人單 session 工作（無 IN_PROGRESS 工單時）→ 此 check 永遠 PASS，無感知成本

### 顯示範例

**BLOCK 範例**：

```
🚨 派發 overlap check 失敗：T0105 與 T0103 衝突

T0103（IN_PROGRESS）affects_files：
  - control-tower/references/work-order-template.md
  - control-tower/references/work-order-system.md

T0105（即將派發）affects_files：
  - control-tower/references/work-order-template.md  ← 衝突
  - control-tower/SKILL.md

繼續派發會有 merge conflict 風險。
[A] 取消派發 T0105
[B] 先等 T0103 完成再派 T0105（建議）
[C] 確認接受衝突（需明確輸入「確認接受衝突」）
```

**WARN 範例**：

```
⚠️ 派發 overlap check 警告：T0106 與 T0104 同目錄

T0104（IN_PROGRESS）affects_files：
  - _ct-workorders/*

T0106（即將派發）affects_files：
  - _ct-workorders/_tower-state.md

[Y] 繼續派發
[N] 取消，等 T0104 完成
```

## 回報處理流程

使用者回塔台說「T0001 完成」時：

> 收到 `T#### 提問`（yolo，v5.5.0+）不是回報：工單仍在執行，不走本流程，改照 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › 塔台端。

0. **對工單**：用回報的 ID 找熱區工單；找不到完全相同的，照下方 § 回報 ID 對不上時
1. **讀取工單檔案**回報區：完成狀態、產出摘要、遭遇問題
2. **複查 sprint-status.yaml**：未更新則塔台補更新
3. **品質閘門檢查**：若為審查類工單且回報包含 CRITICAL/HIGH 發現 → 強制派發修正工單
4. **更新進度表**
5. **學習記錄**（靜默）：追加觀察到 `_learnings.md`
6. **決策下一步**：
   - `DONE` → 派發下一張或宣布階段完成
   - `FAILED` → 啟動 Debug 策略（見 debug-strategies.md）；Renew 重派同一張工單時，派工前先照下方 § 重派前回收舊 Worker 分頁
   - `BLOCKED` → 記錄卡點，評估可並行的工單；frontmatter 有 `tower_question: open`（yolo 提問逾時的備援，v5.5.0+）→ 在 Renew 區段答覆後重派，見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › 塔台端。不論是否為備援，`BLOCKED` 後 Renew 重派同一張工單時，派工前先照下方 § 重派前回收舊 Worker 分頁
   - `PARTIAL` → 先判斷 blocker 是否仍存在，再照下方 § PARTIAL 當下收尾：塔台一裁示剩餘部分怎麼處理（另開接手單、或判定不需再做），**當下**補〈塔台收尾補記〉並改 `DONE`；
     只有真的在等外部條件的才保留 `PARTIAL`／`BLOCKED`；裁示之前先評估拆分或補充指引

回報確認格式：
```
✅ T0001 已確認完成
   產出：`AGENTS.md` 專案上下文區塊已建立
   sprint-status.yaml：已同步
   學習：已記錄（工作量/結果）
   下一步：準備派發 T0002-create-prd
```

### 回報 ID 對不上時（v5.13.1+）

> 🔴 本節是塔台端「回報 ID 缺前綴」容錯的**唯一權威**；Worker 端的規則見上方 § 回報與通知用的工單 ID。
> 回報可能是 `完成`／`部分完成`／`需要協助`／`失敗`，也可能是 yolo 的 `提問`（[yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › 塔台端）；對工單的方式都照本節。

| 情況 | 處理 |
|---|---|
| 熱區有**完全相同** ID 的工單 | 照舊 |
| 沒有完全相同的，但熱區**恰好一張**是「任一前綴 + 同號」（例：收到 `T0184`，熱區只有 `LB-T0184`） | 當作那一張處理；收單紀錄（確認區塊、`_tower-state.md` 或決策日誌，擇塔台本來就會寫的那處）寫一行「回報 ID 缺前綴：收到 `T0184`，對到 `LB-T0184`」。之後對這張單的 BAT 指令（`--close-worker` 等）一律用完整 ID |
| 同號的有多張（例 `LB-T0184` 與 `CP-T0184`），或完全找不到 | 不猜，問使用者是哪一張。yolo 下屬斷點 A 的非預期狀態（[yolo-mode.md](yolo-mode.md) § 斷點 A） |

- 「同號」= 去掉前綴後的 `T\d+` 完全相同（`T0184` 不對 `T184`）。比對範圍只有熱區，不翻歸檔。
- 收到的 ID 帶前綴、熱區卻只有無前綴的同號單（反方向）→ 不套用本表第二列，照第三列問使用者。
- 🔴 本節只保住**塔台收單**。BAT 能不能把 Worker 分頁標成 Done，仍取決於 Worker 送的 `--source`；
  塔台在這裡對到工單，不會讓 BAT 那邊對上。根本修法是 Worker 端的完整 ID 規則與送出前比對（上方 § 回報與通知用的工單 ID）。

### 收單後回收 Worker 分頁（`worker_auto_close`，v5.1.0+）

輸出上方 `✅ T#### 已確認完成` **之後**才做這一步。選項的有效值與預設見
[tower-config.md](tower-config.md) § 可用選項，本節不複述。

**條件（全部成立才執行；任一不成立，本節整段跳過）**：

- `worker_auto_close == done`
- 工單 `status == DONE`
- 本次不 Renew（Renew 見 [research-workorder.md](research-workorder.md) § Renew 機制）
- `BAT_SESSION=1`

`worker_auto_close: off` 時本節不執行任何動作，收單流程與 v5.0.9 完全相同。

**指令**（逐字依 BAT PLAN-041「介面契約」；參數名、值域、exit code 語意皆不得自行更改）：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --close-worker <工單 ID> --notify-id "$BAT_TERMINAL_ID" --delay-ms <worker_close_delay × 1000>
```

- `BAT_HELPER_DIR` 未設定時，helper 路徑沿用 [auto-session.md](auto-session.md) § BAT 內部終端路由 › 執行方式的安裝目錄 fallback（路徑形式規則同該處）；`"${BAT_HELPER_NODE:-node}"` 的解析規則見同處「Node 解析」。
- 參數合法值與防注入規則見 [auto-session.md](auto-session.md) § 安全邊界。
- 「這張單的 Worker 是否由本塔台派出」由 BAT 判定（exit `3` / `4`），塔台不需自行追蹤。

**隔離工單（v5.3.0+）**：工單以 `--isolation worktree` 派出（見 [auto-session.md](auto-session.md) § worktree 隔離派工）時，
上方指令尾端加 `--worktree keep`：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --close-worker <工單 ID> --notify-id "$BAT_TERMINAL_ID" --delay-ms <worker_close_delay × 1000> --worktree keep
```

- `keep` 只關分頁，worktree 與分支 `ct/T####` 留給合併。合併流程見 [merge-workorder.md](merge-workorder.md)。
- 合併完成後才用 `--worktree remove`（或塔台手動 `git worktree remove`），見 [merge-workorder.md](merge-workorder.md) § 合併完成後清理。
- 🔴 `--worktree archive` 會把分支改名為 `ct-archive/T####`，**合併前不得使用**。
- 清理在分頁實際關閉後才執行，結果只寫 BAT 日誌；exit code 與下表相同，不另外判斷清理成敗。
- 非隔離工單（派工時沒有 `--isolation worktree`，或派工紀錄為 `isolation: not-applied`）**不帶** `--worktree`，指令與行為和 v5.2.6 完全相同。

**exit code 處理**（判斷只看 exit code，stdout / stderr 不參與判斷；唯一例外是 stderr 含 `Forbidden` 時用來挑選提示文字，見 [auto-session.md](auto-session.md) § BAT 內部終端路由 › 範圍權杖與分頁角色 第 5 點）：

| exit | 處理 |
|---|---|
| `0` | 靜默；可在確認區塊加一行「Worker 分頁約 N 秒後回收」。延遲到期時分頁仍在輸出，BAT 會等連續安靜 5 s、最多再等 60 s，屆時仍在輸出就放棄、保留分頁；helper 已 exit `0`，塔台不會得知，所以這行提示不得寫成確定的時間或「已關閉」。條件細節見 [tower-config.md](tower-config.md) § 可用選項 `worker_close_delay` |
| `3`（`NOT_FOUND`） | 靜默；必要時提示一次「找不到 Worker 分頁，請手動關閉」 |
| `4`（`NOT_OWNER`）/ `5`（`AMBIGUOUS`）/ `6`（`BUSY`） | 一行回報使用者，不重試 |
| `1` 或其他 | 一行警告「BAT 不支援 `--close-worker` 或連線失敗」，同一 session 不再重試（與下方 § 重派前回收舊 Worker 分頁 共用同一個 session 旗標）；stderr 含 `Forbidden` 時同一行多一句原因提示（同上） |

🔴 **回收失敗不影響收單結果與工單狀態。** 回收是收單確認之後的附帶動作：不論 exit code 為何，
都不得回寫工單、不得改變上方「決策下一步」的判斷。

### 重派前回收舊 Worker 分頁（v5.12.0+）

本節是「對同一張工單再派 Worker 之前，先回收舊 Worker 分頁」的**唯一權威**；其他檔案只放摘要並引用本節。
來源：BAT CT-T022（BUG-170）、D094。

**為什麼要做**：不回收時，同一塔台、同一張工單會有兩個 Worker 分頁。新 Worker `DONE` 後，上一節的收單回收會因此回 exit `5`
（`AMBIGUOUS`），兩個分頁都要使用者手動關；新 Worker 回報時 BAT 也會把同塔台同工單的分頁都標 `✓`，舊分頁看起來像剛完成（BAT BUG-170）。

**適用（全部成立才執行）**：

- 塔台在 BAT 內，且這次以 BAT 內部終端派工（[auto-session.md](auto-session.md) § BAT 內部終端路由）；本塔台 session 未記為「不支援 `--close-worker`」（見下方 exit code 表）
- 要對**同一張工單**再派一個 Worker（`--skill ct-exec`）
- 該工單本塔台 session 之前派過 Worker，或工單紀錄顯示曾在 BAT 派過。判斷不確定時照樣呼叫：沒有舊分頁只會回 exit `3`

至少涵蓋下列重派：

1. yolo 提問備援：`BLOCKED` ＋ `tower_question: open`，塔台在 Renew 區段答覆後重派（[yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › 塔台端「收到備援的 `T#### 需要協助`」）
2. `BLOCKED`／`FAILED` 後 Renew 重派（[research-workorder.md](research-workorder.md) § Renew 機制）
3. 使用者停掉首派的 Worker 後要求重派
4. 派工 exit `8`（`started: unconfirmed`）後**使用者決定**重派。塔台仍不自動重派，照 [auto-session.md](auto-session.md) § Worker 啟動確認 第 4 點

**不適用（不呼叫）**：

- `--skill ct-done` 補救派工：**不回收，保留現場**（D094，使用者決定；舊分頁的輸出可能是使用者要看的現場）。之後收單回收若回 exit `5`，照上一節 exit code 表一行提示使用者手動關舊分頁
- 研究單的 Renew 由使用者在原分頁「重讀工單」繼續（[research-workorder.md](research-workorder.md) § Renew 機制 › 塔台操作流程）：那個分頁就是要繼續的 Worker
- [auto-session.md](auto-session.md) § Worker 啟動確認 第 5 點：`Unknown option '--wait-started'` 時去掉參數重派一次（前一次沒有建立分頁）
- 首次派工

**與 `worker_auto_close` 無關**：`worker_auto_close: off` 時也照本節回收（D094）。本節是避免同一張工單同時有兩個 Worker 分頁，不是收單回收；
`worker_close_delay` 也不適用，延遲固定 `0`。

**指令**（派工前執行；helper 路徑 fallback 與 `"${BAT_HELPER_NODE:-node}"` 的解析、PowerShell 寫法照 [auto-session.md](auto-session.md)
§ BAT 內部終端路由 › 執行方式「Node 解析」；參數合法值與防注入規則見同檔 § 安全邊界）：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --close-worker <工單 ID> --notify-id "$BAT_TERMINAL_ID" --delay-ms 0
```

- 隔離工單（frontmatter `isolation: worktree`，或派工紀錄顯示以 `--isolation worktree` 派出）尾端加 `--worktree keep`：
  worktree 與分支 `ct/T####` 留給新 Worker 沿用（[auto-session.md](auto-session.md) § worktree 隔離派工），之後照 [merge-workorder.md](merge-workorder.md) 合併。
  🔴 不得用 `remove` / `archive`。
- 呼叫回來就派工（含下表所有 exit code）：不等回收完成、不輪詢、不對舊分頁送按鍵或 `pty:write`。派工命令與 [auto-session.md](auto-session.md) 的派工規則完全相同，本節不改。

**為什麼安全**（BAT 權威：`CLAUDE.md`「Worker 分頁回收」節、`docs/agent-guide/worker-tab-recycle.md`）：`--close-worker` 在呼叫當下以工單找候選、
過濾出本塔台的分頁，只有一個候選時記下它的 terminal id 再排程，所以之後新建的 Worker 分頁不受影響。`--delay-ms 0` 仍會等分頁連續安靜 5 s
（最多再等 60 s）才關；排程後使用者在舊分頁輸入會取消回收。

**exit code 處理**（判斷只看 exit code；🔴 **不論結果都照常派工，不得因此擋住重派**）：

| exit | 處理 |
|---|---|
| `0` | 繼續派工 |
| `3`（`NOT_FOUND`） | 繼續派工（沒有舊分頁：使用者已關、BAT 重開後沒還原等） |
| `5`（`AMBIGUOUS`） | 一行提示使用者手動關舊分頁（照 [auto-session.md](auto-session.md) § 對使用者描述分頁 用分頁標題描述），繼續派工 |
| `4`（`NOT_OWNER`）/ `1` / 其他 | 一行提示，繼續派工。`1` 時本塔台 session 記為「不支援 `--close-worker`」：之後重派前回收與上一節收單回收都不再嘗試（與上一節 exit `1` 的「同一 session 不再重試」是同一個旗標） |

stderr 含 `Forbidden` 時同一行多一句原因提示，規則同上一節 exit code 表。回收結果不寫進工單，也不改變重派的決定。

### PARTIAL 當下收尾（含 resolved `PARTIAL` 補正）

本節是塔台處理 `PARTIAL` 工單的**唯一權威定義**（v5.13.0 起把收尾時點從歸檔前提前到裁示當下）。
[archive-system.md](archive-system.md) § 最終態與日期欄位來源 的歸檔前覆核只是最後防線，照本節做就不會走到那裡。

`PARTIAL` 是 point-in-time incomplete 狀態，不應永久代表仍有未完成工作。Worker 依停止條件回報 `PARTIAL` 是對的；收尾是塔台的事。

**何時收尾**：塔台**一裁示**剩餘部分怎麼處理，就**當下**收尾，不等歸檔、不等接手單完成：

| 塔台裁示 | 原工單 |
|---|---|
| 另開接手單（例 T0412 接手剩餘的 Step 5～6） | 補〈塔台收尾補記〉並改 `DONE` |
| 判定剩餘部分不需再做（scope 排除、已由其他工單或決策完成、final acceptance 已涵蓋） | 補〈塔台收尾補記〉並改 `DONE` |
| 剩餘部分被設計方向淘汰（不是完成） | 補〈塔台收尾補記〉並改 `ABANDONED`／superseded 類 final-state |
| 真的在等外部條件（廠商、客戶、環境、使用者還沒給的輸入） | 保留 `PARTIAL`（或改 `BLOCKED`），寫明在等什麼 |

塔台處理回報、`*sync` 或 active tracking 時，看到還掛著的 `PARTIAL` 也要重新判斷：裁示早已做了、只是沒收尾的，當下補做。

**怎麼收尾**：

1. 保留原始回報區與 evidence，不覆寫歷史結論。
2. 在原工單文末新增 `## 塔台收尾補記`（舊稱 post-resolution note）：時間（取系統時間）、裁示（決策編號）、剩餘部分由誰完成（接手單編號）或為何不需再做。
3. 改 frontmatter `status`（與本文元資料鏡像）；`completed_at` 保留 Worker 的值，`updated_at` 取系統時間。
4. 同步更新 `sprint-status.yaml`、`_tower-state.md`、`_decision-log.md`、ct-status active tracking 與 BAT active tracking，避免 resolved partial 繼續顯示為 active work。
5. **接手單完成後回頭確認**：收接手單時，在原工單的〈塔台收尾補記〉追加一行「T#### 已完成（D###）」；接手單沒完成剩餘部分時，在補記寫明剩下的由誰接。

## 中斷復原

工單處於 `IN_PROGRESS`（有開始時間但無完成時間）時：

1. 若回報區有部分結果 → 產生**接續工單**（新編號，參照原工單）
2. 若回報區為空 → 提供兩個選項：
   - **重派原工單**：重設狀態為 PENDING；派工前先照 § 回報處理流程 › 重派前回收舊 Worker 分頁
   - **產生新工單**：可能調整策略或拆分
3. 原工單標記 `INTERRUPTED`

## sprint-status.yaml 同步

**雙重保障**：
1. Sub-session 主力更新（工單指示中明確要求）
2. 塔台複查補漏（每次回報處理時自動檢查）

**觸發全局同步**：使用 `*sync` 內建命令。

同步流程（`*sync` 執行時）：
1. Glob 列出 `_ct-workorders/T*.md`
2. 讀取每張工單元資料（狀態、開始/完成時間）
3. 交叉比對三方（塔台記憶 / 工單檔案 / sprint-status.yaml）
4. 以工單檔案為 single source of truth 修正差異
5. 量熱檔大小，超過預算時在摘要加提示（[memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 › 大小預算）；
   啟用 BUG 追蹤時，加未結 BUG 清理提示（[bug-plan-system.md](bug-plan-system.md) § BUG 單據 › 未結 BUG 清理提示）
6. 顯示同步結果摘要
