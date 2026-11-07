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
| ✅ 合法 | `PROJ-T0001` | 前綴 4 字元（上限） |
| ❌ 非法 | `cp-T0113` | 前綴必須大寫 |
| ❌ 非法 | `PROJX-T0001` | 前綴超過 4 字元 |
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

### 回報與通知用的工單 ID（完整 ID，v6.0.0-beta.4+）

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
├── _bmad-output/                 ← 方法論產物（例：bmad；實際位置依 adapter `artifacts.writes`，若使用）
├── src/
└── ...
```

## 工單粒度原則

每張工單 = 一層的一個方法論工作流程（或一個明確交付物）：
- 單一職責：不合併多個工作流程到同一工單；層與方法論工作流程的定義見 [methodology-adapters.md](methodology-adapters.md) § 層次
- 沒有方法論 adapter（`methodology: none` 或未安裝）時，以「一個明確交付物」切分
- 完整可交付：sub-session 完成後有明確產出
- 可中斷可恢復：PARTIAL 時可基於已完成部分產生接續工單
- 已驗證有效：6 工單 / 90 分鐘 / 44 檔產出（Keenbest 逆向工程實測）

## 規劃產物 → 執行之間的品質檢查點

規劃層的產物（例：bmad 的 story spec）交給執行層之前，塔台根據以下條件決定是否插入獨立審查。
跨層交接的規則（`handoff.produces`／`consumes`、回寫）見 [methodology-adapters.md](methodology-adapters.md) § 分層疊加。

| 條件 | 塔台動作 |
|------|---------|
| 執行層的方法論工作流程內建審查（例：bmad `bmad-build` 的 Review Triage，story 由 `bmad-spec` 拆出） | 審查已內建，**不需額外工單** |
| 執行層換成另一個方法論（分層疊加），審查層 `inherit` 主方法論 | 派工摘要提示「原方法論內建在執行流程裡的審查不會跑」（`methodology-adapters.md` § 分層疊加 第 5 點）；依審查層 adapter 的 `routing.<需求類型>.review` 決定要不要派審查工單 |
| 高風險工作項（涉及安全、金流、資料遷移） | 派發**獨立審查工單**（Adversarial Review），用不同 session 交叉驗證 |
| 工作項跨多個子專案或影響共用模組 | 派發**獨立審查工單**，確認跨專案影響已涵蓋 |
| 沒有方法論 adapter 的自訂流程 | 塔台**主動提議** review 步驟：「規劃產物已產生，建議先審查再實作，要派審查工單嗎？」 |
| 使用者明確跳過 | 記錄到 `_decision-log.md`，標注「使用者選擇跳過規劃產物審查」 |

### 審查工單的 Session 原則

獨立審查工單必須在**不同 session** 執行（避免確認偏誤）。工單 Session 建議自動設為 🆕 新 Session。

### 搭配品質閘門

若獨立審查回報包含 CRITICAL/HIGH 發現 → 強制派發修正工單，修正完成後才派發執行層工單。（同「審查→修正→交付」三步驟規則）

## 派發流程

每次派發任務時，塔台：

1. **學習查詢**（靜默）：讀取 `_learnings.md`，比對決策模式的觸發條件
2. **方法論工作流程選擇**：依 [methodology-adapters.md](methodology-adapters.md) § 解析步驟，解析本單每一層由哪個 adapter 負責，再查該 adapter 的 `routing.<需求類型>.<層>` 取得 workflow（bmad 的 `routing.*.reference` 指向 `bmad-guide` 的 reference 檔，相對於偵測到的 skill 根目錄；去哪裡找 `bmad-guide` 只定義在 [adapters/bmad.yaml](adapters/bmad.yaml) `detection.probes`）；找不到 adapter、未安裝或沒有入口 → 照該檔 § 降級（通常是使用者手動指定或自由文字）。結果寫進工單 frontmatter `methodology` 與 `### 方法論工作流程` 段（[work-order-template.md](work-order-template.md) § 填寫方法論欄位指引）。
   已建立、尚未派出（`PENDING`）的工單要派出時，先照 [methodology-adapters.md](methodology-adapters.md) § 解析步驟 › 何時解析 重新解析一次：工單覆寫保留，其他層依當下設定重算；
   與 frontmatter 不同 → 以新值為準、更新工單，並在派工摘要列出差異（見下方範例）。已派出的工單不重算。
2.4. **方法論注入檢查**（v6.0.0-pre.1，V1 後 D342）：照 [methodology-adapters.md](methodology-adapters.md) § 與 hook／session 路由的相處規則 第 2 點 套 `methodology_guard`。
   `warn`（預設）偵測到注入開著 → 工單**自動加** `### 方法論邊界`（範本：[work-order-template.md](work-order-template.md) 標準模板的 `### 方法論邊界`；
   注入的方法論不負責本單任何一層用【不使用】變體，負責某層用【只允許】變體），沒有 `methodology` 的工單也加；`block` → 不派；`off` → 略過。
2.5. **派發前 overlap check**（v4.4.0+）：比對本次工單的 `affects_files` 與目前 IN_PROGRESS 工單的 `affects_files`，依交集嚴重度決定 BLOCK / WARN / 放行（見下方「派發前 overlap check」）
3. **產生工單檔案**：寫入 `_ct-workorders/T<編號>-<描述>.md`（見 work-order-template.md）
4. **畫面顯示摘要**：

```
📋 工單已建立：T0001-create-project-context
   任務：建立專案上下文
   方法論：planning → bmad/bmad-project-context（bmad-guide v6.12.4 / adapter 0.2.0，來源：內建）
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

**派工摘要的方法論行**（格式依 `methodology-adapters.md` § 解析步驟 第 7 步）：每層一行，
`方法論：<層> → <adapter>/<workflow>（<upstream 版本> / adapter <adapter_version>，來源：<內建／外部 skill／專案本地>）`；
只用到一層就只有一行。降級、能力落差、常駐注入（`methodology_guard`、`always_on_tokens`）在同一區塊多一行提示。
工單沒有任何層由 adapter 負責時，不顯示方法論行；但第 2.4 步自動加了邊界段時，仍顯示那一行提示
（例：`⚠️ pstack SessionStart 注入開著（~4328 tokens）：已加方法論邊界（不使用 pstack:*）`）。多層範例：

```
   方法論：execution → pstack/pstack:poteto-mode（Feature playbook；pstack 0.9.103 / adapter 0.2.5，來源：外部 skill）
   方法論：review    → bmad/bmad-code-review（bmad-guide v6.12.4 / adapter 0.2.0，來源：內建）
   ⚠️ 執行層不是 bmad：bmad-build 內建的 Review Triage 不會跑；pstack SessionStart 注入開著（~4328 tokens），工單已寫方法論邊界
```

PENDING 工單派工前重新解析、結果與工單不同時，方法論行用新值，另加 🔄 行列出差異（改變的層、舊值 → 新值、原因）：

```
   方法論：execution → pstack/pstack:poteto-mode（pstack 0.9.103 / adapter 0.2.5，來源：外部 skill）
   方法論：review    → bmad/bmad-code-review（bmad-guide v6.12.4 / adapter 0.2.0，來源：內建）
   🔄 重新解析：execution team-x → pstack（建單後 session 改了 methodology_execution）；review 為工單覆寫，保留
```

5. **更新進度表**
6. **更新 _tower-state.md**（最大工單編號、進度快照）

### 方法論的派發規則

各方法論 workflow 的派發限制（退役／改名、必要段落、CT 覆寫規則）不寫在本檔，以該 adapter 描述檔為準。
bmad 見 [adapters/bmad.yaml](adapters/bmad.yaml)：`retired_names`（舊名 → 新名）、`workorder.required_when`
（例：`bmad-build-auto` 要加 `### Autonomous Contract`）、`worker.ct_overrides`（例：`bmad-loop` 不當一般工單 workflow 派發）。
workflow 名稱查不到時的處理見 [methodology-adapters.md](methodology-adapters.md) § 降級。

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
1. **讀取工單檔案**回報區：完成狀態、產出摘要、遭遇問題；有 `### 方法論執行紀錄` 時一併看 `methodology_ambient` 與方法論 skill 使用表（工單沒宣告卻用了方法論 skill → 記入決策日誌，之後同類工單確認有邊界段；格式見 [methodology-adapters.md](methodology-adapters.md) § 工單欄位）
2. **複查主方法論 tracker**（bmad 時為 `sprint-status.yaml`；位置見 adapter `tracker`）與 `### 方法論狀態回寫`：該回寫沒回寫則塔台補更新；主方法論沒有 `tracker` 就跳過（§ 主方法論 tracker 同步）
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
   方法論狀態回寫：已同步（sprint-status.yaml）
   學習：已記錄（工作量/結果）
   下一步：準備派發 T0002-create-prd
```

### 回報 ID 對不上時（v6.0.0-beta.4+）

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

### 收單補記 session id（v6.0.0-beta.10+）

> 本節是塔台收單時補記 Worker session id 的**唯一權威**（PLAN-004 ⑥ 第 6 點，D517；BAT D197）。Worker 自己寫的是主要來源
> （`ct-exec/SKILL.md` § Phase 4 › Session id），本節是備援；統計怎麼用見 `ct-insights/references/analysis-rules.md` § Session 用量統計。

處理 Worker 回報（`完成`／`部分完成`／`需要協助`）時，在輸出確認區塊之後、**任何** `--close-worker`（下方 § 收單後回收 Worker 分頁、
§ 重派前回收舊 Worker 分頁）**之前**做一次。分頁關掉之後就讀不到了。不論 `worker_auto_close` 是什麼都做。

1. **找 Worker 分頁**：BAT MCP `bat_list_terminals`（`scope: mine`）裡 `workorder` 等於這張工單完整 ID 的列；**恰好一列**才繼續，零列或多列就跳過。
2. **讀值**：對那一列的 terminal id 呼叫 `bat_get_state`，取 `claudeSessionId`（BAT `>= 0.7.1-pre.1` 才有這個鍵）。
3. **寫入**：值符合 `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`、而且不在工單 frontmatter `session_ids` 裡 → 追加到清單末尾
   （YAML block list、加引號；清單只有 `unavailable` 時換掉它；沒有這個欄位就新增）。只改 frontmatter，不改回報區（回報區由 Worker 填）；隨塔台本來的收單 commit 一起提交。
4. **跳過**（都不是錯誤、不提示、不重試）：不在 BAT（`BAT_SESSION` 不是 `1`）、MCP 不可用或回錯誤、`claudeSessionId` 鍵不存在（舊 BAT）、
   值是 `null`（🔴 不代表沒有 session：還沒回報、hooks 沒注入或被關、headless 重開）、值不是 UUID。
- 只用 MCP 讀，不用 helper CLI（helper 沒有對應查詢，也不要為此讀 `bat-scripts.log`，它不是契約，D517）。
- `/clear` 後同一分頁換了新 session，BAT 只記最後一個 id；之前的 id 只能靠 Worker 自己寫的 `session_ids`。
- session id 不是秘密，可以寫；權杖一律不寫（[auto-session.md](auto-session.md) § BAT 內部終端路由 › 偵測條件）。

### 收單快照（v6.0.0-beta.10+）

> 本節是塔台收單時寫統計快照的**唯一權威**；快照格式與併入規則見 `ct-insights/references/analysis-rules.md` § Session 用量統計 › 快照，
> 存放位置的歸屬見 [data-layer-architecture.md](data-layer-architecture.md) § `_ct-workorders/_insights/`。

Claude Code 預設只留 session 紀錄 30 天，所以收單當下（紀錄一定還在）就留一份只有數字的快照。在上方 § 收單補記 session id **之後**做
（讓這次補記的 id 也能用來歸屬），處理每一次 Worker 回報都做（同一張工單再寫一次時，腳本依併入規則取代或保留，不會重複）：

```bash
python "<ct-insights>/scripts/ct-session-stats.py" --workorders-dir _ct-workorders --workorders <工單 ID> \
  --snapshot-append _ct-workorders/_insights/session-stats/<YYYY-MM>.json
```

- 在 repo 根目錄執行。`<ct-insights>` 的解析、直譯器名稱、Git Bash 路徑轉換同 `ct-insights/references/analysis-rules.md` § 預篩腳本；
  `<YYYY-MM>` 是寫入當下的月份（本機時間）；目錄不存在時腳本會建立。stdout 的表格不必貼給使用者，看 stderr 的 `snapshot:` 一行即可。
- **隔離工單**（`isolation: worktree`）：Worker 的 session 紀錄在 worktree 路徑對應的專案目錄下，另加一個 `--project <編碼後的 worktree 路徑>`
  （編碼規則同上述 § Session 用量統計 的 `--project`）。
- exit code（判斷只看 exit code）：

| exit | 處理 |
|---|---|
| `0` | 靜默；確認區塊可加一行「session 快照：已寫」 |
| `4`（資料不可用） | 跳過，確認區塊加一句「session 快照：資料不可用」 |
| `3`（隱私自檢不通過，未寫檔） | 跳過，確認區塊加一句「session 快照：自檢不通過，未寫」；不手動改快照 |
| 其他、找不到 Python 3 | 跳過，確認區塊加一句「session 快照：腳本不可用」 |

🔴 快照失敗不影響收單結果、工單狀態與下一步判斷，也不重試。快照檔隨塔台本來的收單 commit 一起提交（只有數字）。

### 收單後回收 Worker 分頁（`worker_auto_close`，v5.1.0+）

輸出上方 `✅ T#### 已確認完成` **之後**才做這一步（v6.0.0-beta.10+：在 § 收單補記 session id、§ 收單快照 之後）。選項的有效值與預設見
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

本節是塔台處理 `PARTIAL` 工單的**唯一權威定義**（v6.0.0-beta.3 起把收尾時點從歸檔前提前到裁示當下）。
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
4. 同步更新主方法論 tracker（bmad 時為 `sprint-status.yaml`）、`_tower-state.md`、`_decision-log.md`、ct-status active tracking 與 BAT active tracking，避免 resolved partial 繼續顯示為 active work。
5. **接手單完成後回頭確認**：收接手單時，在原工單的〈塔台收尾補記〉追加一行「T#### 已完成（D###）」；接手單沒完成剩餘部分時，在補記寫明剩下的由誰接。

## 執行中補充工單（v6.0.0-beta.11+）

> 🔴 本節是「Worker 還在 `IN_PROGRESS` 時，塔台往工單補充或修正指示」的**唯一權威**（PLAN-005 P2，D545）。
> Worker 端怎麼讀到（三個固定節點各 grep 一次段落標題）只定義在 `ct-exec/SKILL.md` § Tower Addenda Check；
> 塔台用跨 session 訊息提醒自己的 Worker（選用）只定義在 [cross-project-coordination.md](cross-project-coordination.md) § 通知自己的 Worker 重讀工單。
> Renew（`BLOCKED`／`FAILED` 之後重派、研究型工單多輪）仍以 [research-workorder.md](research-workorder.md) § Renew 機制 為準，本節不改它。

**何時用**：工單 `status: IN_PROGRESS`、Worker 還在跑，塔台要補充事實或修正指示。例：BAT 或使用者給了新事實、塔台答覆提問後衍生的範圍調整、
發現工單本文寫錯。以下情況**不用**本節：

| 情況 | 改用 |
|---|---|
| Worker 已回報 `BLOCKED`／`FAILED`（含 yolo 提問備援），要重派 | Renew：`## 塔台補充（Renew #N）`（[research-workorder.md](research-workorder.md) § Renew 機制） |
| 回答 Worker 的 `#### Q-n` | `### 待塔台決策` 的 `- **塔台答覆 Q-n**` 行（[yolo-mode.md](yolo-mode.md) § 塔台端 第 3 點）；執行中補充段裡的答覆行**不算**答覆 |
| Worker 已回報完成（`DONE`／`PARTIAL` 等） | 收單後開接手單，或依 § PARTIAL 當下收尾 裁示 |
| 方向完全不同 | 開新工單（[research-workorder.md](research-workorder.md) § Renew vs 開新工單的判斷） |

寫之前先看一次工單 `status`：已不是 `IN_PROGRESS` 就不寫本段，照上表。

**段落格式**：在工單回報區 `---` 分隔線**之前**插入（與 Renew 同一位置）；已有 `## 塔台補充（…）` 段時，插在最後一段之後。
編號 `#N` 只數執行中補充（#1、#2…），與 Renew 各自遞增。

```markdown
## 塔台補充（執行中 #N）

**時間**：<系統時間，ISO 8601 含時區>
**補充內容**：
> <新事實或修正，附來源（決策編號、BAT 回覆、使用者原話）>

**新指示**：
> <Worker 要做的事；不改原指示就寫「無，僅供參考」>

**範圍與驗收**：<無變更／列出：`affects_files` 增減、驗收條件改了哪幾條>
**已完成部分**：<不影響／要推翻或重做的部分，逐項寫明>
```

- **時間**取系統時間（`date "+%Y-%m-%dT%H:%M:%S%z"`），不憑印象。
- **改了範圍或驗收**：同一次寫入就改 frontmatter `affects_files` 與工單的驗收段，並在〈範圍與驗收〉列出改了什麼。只寫在補充段、frontmatter 沒改的範圍擴大，
  Worker 會當成範圍外而提問或停下（`ct-exec/SKILL.md` § Tower Addenda Check）。擴大範圍前照派工時的 overlap check（§ 派發前 overlap check）再比一次新增的路徑。
- **已完成部分**：要推翻或重做 Worker 已完成（尤其已 commit）的工作，必須在〈已完成部分〉逐項明寫；不得用補充段默默改掉已完成的工作。
- **不改的東西**：工單 `status` 維持 `IN_PROGRESS`；元資料的 `Renew 次數` **不加**（執行中補充不是 Renew，不觸發斷點 B-1）；不重派、不回收 Worker 分頁。
- **只寫自己的段落**：不改回報區、不改 Worker 已寫的內容。Worker 可能同時在寫回報區，塔台寫完後不要再反覆改同一段；要再補就加下一個 `#N`。

**commit**：Worker 讀的是工作目錄裡的工單檔，**可見性不依賴 commit**——塔台寫完存檔，Worker 下一個檢查節點就看得到，不 commit 也一樣。
塔台照 `auto_commit` 慣例 commit 這張工單檔即可，只 commit 該檔（`git commit --only _ct-workorders/<file>`）。Worker 收尾 commit 同一檔時會一併帶入塔台已寫、
未 commit 的段落，屬預期行為（同 [yolo-mode.md](yolo-mode.md) § Worker 端 3-B 對答覆行的說明）。隔離工單的工單檔本來就只在主 checkout
（`ct-exec/SKILL.md` § Worktree Isolation 第 1 點），塔台照常改主 checkout 的那一份，不碰 worktree 裡的副本。

**Worker 什麼時候讀到**：Worker 在**驗證前、產品 commit 前、寫回報前**三個節點各 grep 一次段落標題，發現開工後新增的 `## 塔台補充（…）` 段才讀
（`ct-exec/SKILL.md` § Tower Addenda Check）。所以補充最晚在 Worker 寫回報前被讀到；三個節點之間的長步驟中途**不會**讀到。要它更早讀到：

1. Claude Code 塔台＋Claude Code Worker：可選用跨 session 訊息提醒（[cross-project-coordination.md](cross-project-coordination.md) § 通知自己的 Worker 重讀工單）；
   沒送到也沒關係，節點檢查會兜底。
2. 其他情況：請使用者回 Worker 分頁說「重讀工單」（Worker 把它當成一次額外的節點檢查）。塔台不得自己寫入 Worker 分頁（BAT 範圍權杖；BUG-196）。

**記錄**：決策日誌照常記裁示；yolo 時在 `_tower-state.md` 的 `## YOLO 歷程` 寫一筆 `[補充]` 條目（格式與寫入時機見 [yolo-mode.md](yolo-mode.md) § `_tower-state.md` 新增 `## YOLO 歷程` 區段）。

**收單時核對**：收到這張工單的回報時，確認回報區 `### 互動紀錄` 有每個執行中補充段的讀入紀錄（Worker 記一行：哪一段、哪個節點、做了什麼）。
有段落沒有讀入紀錄（例：塔台寫入時 Worker 已過了寫回報前的節點）→ 視為**沒讀到**：照上方表格，以 Renew 重派或開接手單處理，不當作已執行。
Claude Code Worker 讀過的工單在磁碟上被改時，下一個回合會收到「檔案已變更」的提示，所以常會讀到過了寫回報前的節點才寫的段落：**有讀入紀錄就照常認定**，
沒有紀錄的才照上面的規則處理。Codex Worker 沒有這個提示，只靠三個節點。

## 中斷復原

工單處於 `IN_PROGRESS`（有開始時間但無完成時間）時：

1. 若回報區有部分結果 → 產生**接續工單**（新編號，參照原工單）
2. 若回報區為空 → 提供兩個選項：
   - **重派原工單**：重設狀態為 PENDING；派工前先照 § 回報處理流程 › 重派前回收舊 Worker 分頁
   - **產生新工單**：可能調整策略或拆分
3. 原工單標記 `INTERRUPTED`

## 主方法論 tracker 同步（原 § sprint-status.yaml 同步）

主方法論 tracker = 主方法論 adapter 的 `tracker`（`file`、`search`、`optional`；契約見 [methodology-adapters.md](methodology-adapters.md) § 描述檔格式）。
bmad 時為 `sprint-status.yaml`（[adapters/bmad.yaml](adapters/bmad.yaml) `tracker`）。主方法論沒有 `tracker`（`tracker: {}`）或 `methodology: none` → 本節不適用。
分層疊加時，別家 adapter 執行了上游產物（例：bmad 的 story），上游狀態依產生產物的 adapter 的 `handoff.writeback` 回寫，同樣由下面的雙重保障複查。

**雙重保障**：
1. Sub-session 主力更新（工單指示中明確要求，結果寫在回報區 `### 方法論狀態回寫`；舊工單的 `### sprint-status.yaml 已更新` 段照讀）
2. 塔台複查補漏（每次回報處理時自動檢查）

**觸發全局同步**：使用 `*sync` 內建命令。

同步流程（`*sync` 執行時）：
1. Glob 列出 `_ct-workorders/T*.md`
2. 讀取每張工單元資料（狀態、開始/完成時間）
3. 交叉比對三方（塔台記憶 / 工單檔案 / 主方法論 tracker）；tracker 找不到且 `optional: true` → 只比對前兩方
4. 以工單檔案為 single source of truth 修正差異
5. 量熱檔大小，超過預算時在摘要加提示（[memory-protocol.md](memory-protocol.md) § BAT 塔台面板讀取契約 › 大小預算）；
   啟用 BUG 追蹤時，加未結 BUG 清理提示（[bug-plan-system.md](bug-plan-system.md) § BUG 單據 › 未結 BUG 清理提示）
6. 顯示同步結果摘要
