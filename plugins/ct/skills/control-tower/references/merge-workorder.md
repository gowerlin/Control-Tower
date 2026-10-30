# 合併工單（v5.3.0+）

> 本檔是「把隔離工單的分支 `ct/T####` 合併回 `main`」的**唯一權威定義**：三種模式、共同護欄、塔台直接合併判準、
> `--worktree-status` 的指令與欄位、收單 SHA 比對五步、合併完成後清理。
> [work-order-template.md](work-order-template.md) § 合併工單模板、[yolo-mode.md](yolo-mode.md) § 斷點 E、
> [auto-session.md](auto-session.md)、[work-order-system.md](work-order-system.md) 與 `SKILL.md` 只放摘要並引用這裡。
>
> 來源：BAT CT-T016（D150：合併由塔台派合併工單執行，BAT 不做合併引擎，只提供唯讀信號）、BAT T0585（`--worktree-status`）、
> D031（判準第 1 條採放寬版；合併一律整合 worktree `--no-ff` 再對 main `--ff-only`）、
> BAT CT-T017 § 一／T0589（v5.4.0+：分頁關閉後仍可查，`source`；D035）。
> BAT 介面（參數、exit code、JSON 欄位名）以 BAT 為準，CT 不得更改。

## 適用範圍

- 只適用於以 `--isolation worktree` 派出、且派工紀錄不是 `isolation: not-applied` 的工單（隔離工單，見
  [auto-session.md](auto-session.md) § worktree 隔離派工）。
- **不用隔離、不派合併單的專案：所有既有流程不受影響。** 非隔離工單的 commit 直接在主 checkout，沒有東西要合併。
- 需 BAT **`>= 0.7.0-pre.2`**（`--worktree-status`）；BAT 太舊時資料來源改用 git，見 § 合併判準資料來源。
  BAT **`>= 0.7.0-pre.4`**（v5.4.0+）起 Worker 分頁回收後也查得到（回傳帶 `source`），見 § 合併判準資料來源 › 查詢時機與資料來源。

## 流程總覽

隔離工單的 Worker 回報 `DONE` 後，塔台在收單流程中：

1. 讀回報區，含「隔離分支證據」（`branch` / `base_sha` / `validated_sha` / `head_sha`，Worker 規則見 `ct-exec/SKILL.md` § Worktree Isolation）。
2. 查 `--worktree-status`，見 § 合併判準資料來源。舊 BAT（`< 0.7.0-pre.4`）要**在回收 Worker 分頁之前**查（分頁關閉後查不到，
   只能改用 git）；BAT `>= 0.7.0-pre.4` 回收前後都可查（v5.4.0+）。怎麼判定是哪一種，見 § 合併判準資料來源 › 查詢時機與資料來源。
3. 依 [work-order-system.md](work-order-system.md) § 收單後回收 Worker 分頁 以 `--worktree keep` 回收（worktree 與分支留著）。
4. § 塔台直接合併判準 五條全部成立 → 模式 ①，塔台依 § 直接合併的做法 自己做，不派單。
   任一條不成立或無法判斷 → 塔台決定模式 ② 或 ③，依 [work-order-template.md](work-order-template.md) § 合併工單模板 派合併工單。
5. 合併工單回報後，塔台做 § 收單 SHA 比對五步。
6. `--ff-only` 之前一律經 [yolo-mode.md](yolo-mode.md) § 斷點 E（非 yolo 一律暫停確認；yolo 依下方各模式規則）。
7. 合併完成後清理，見 § 合併完成後清理。

## 三種模式

模式由**塔台**決定，寫在合併工單 `merge_mode`。Worker 不得自行改模式。

### ① 機械合併（`mechanical`）

- **條件**：§ 塔台直接合併判準 五條全部成立。
- **誰做**：塔台直接做，**不派合併工單**。做法見 § 直接合併的做法。
- **回報**：塔台在決策日誌記一筆：被合併工單、`base_main_sha`、merge commit、parent1 / parent2、ff 後的 `main`。
- **yolo**：五條判準在 ff 前再確認一次仍成立 → 自動 `--ff-only`；任一條不再成立 → 改派合併工單，不自動 ff。
  非 yolo：ff 前暫停確認（斷點 E）。
- 直接合併途中 `git merge --no-ff` 出現衝突 → `git merge --abort`，放棄直接合併，改派模式 ②。

### ② 衝突解決（`conflict`）

- **條件**：判準不成立，但塔台判斷以 git merge 解衝突即可完成。
- **Worker 做的事**：在 `integration_worktree` 以 `--no-ff` 合併 `ct/T####`、解衝突、跑**專案完整驗收**。不 ff `main`。
- **回報要求**：
  - 每個衝突檔：雙方意圖（`main` 那邊為什麼這樣改、工單分支為什麼這樣改）、解法、理由；
  - merge commit SHA、parent1 / parent2；
  - 驗收結果與跑驗收時的 SHA（應等於 merge commit；不同要說明）；
  - 範圍外檔案：合併結果相對 `base_main_sha` 的變更中，不在被合併工單 `affects_files` 內的檔案（`_ct-workorders/**` 不算），沒有就寫「無」。
- **yolo**：驗收全綠**且**沒有範圍外檔案 → 塔台自動 `--ff-only`；否則暫停（斷點 E）。非 yolo：一律暫停。
- 🔴 Worker 遇到超出衝突解決的情況（例：分支太舊、程式碼已重構到合併後必須改寫邏輯）→ 回報 `PARTIAL` 並**建議**改模式 ③，
  不自行升級成等價移植。

### ③ 等價移植（`port`）

- **條件**：分支過舊、程式碼已重構、或來源是 EXP／上游成果，git merge 已不適合。
- **Worker 做的事**：以原工單的目標與驗收條件為規格，在整合 worktree 從目前 `main` 重新實作，**不用 git merge 合併該分支**。不 ff `main`。
- **回報要求**：
  - 對照表：「原 commit / hunk → 新位置」；
  - 原工單驗收條件**逐條**重新驗證的結果；
  - 整合分支的 head SHA、跑驗收時的 SHA。
- **yolo 與非 yolo：一律暫停**等使用者確認（斷點 E）。

## 共同護欄

所有模式都適用：

- **只在整合 worktree 工作。** 合併不在主 checkout 做，也不在被合併工單的 worktree 做。
  - 整合 worktree 長期保留（避免每次重裝依賴），路徑寫在合併工單 `integration_worktree`。建議放在主 checkout 上層、
    BAT 的 `.bat-worktrees/` 以外，例 `<主 checkout 上層>/.ct-integration/<repo 目錄名>`。
  - 第一次建立：`git -C "<主 checkout>" worktree add --detach "<integration_worktree>" <merge_target>`，之後依專案規則安裝依賴。
  - 每次合併開工前，整合 worktree 必須乾淨（`git -C "<integration_worktree>" status --porcelain` 為空），
    再從 `base_main_sha` 開一條**新的**合併分支：`git -C "<integration_worktree>" switch -c ct-merge/T#### <base_main_sha>`
    （`T####` 是被合併工單；分支已存在就停下回報，不得覆寫）。`main` 已在主 checkout checkout，整合 worktree 不能也 checkout `main`，所以用合併分支。
- **一律 `--no-ff` 合併**，commit 訊息含被合併工單 ID（例 `merge(ct): T0412 <標題>`）。
- **`main` 只能 `git merge --ff-only`**，在主 checkout 執行，且主 checkout 目前必須在 `merge_target` 分支上：
  `git -C "<主 checkout>" merge --ff-only ct-merge/T####`。
- **不 push**（沿用各專案授權）；不 `--force`、不 `reset --hard`、不 rebase `main`。
- **主 checkout 有與合併檔重疊的髒檔時，`--ff-only` 會被 git 拒絕，這是正常保護**：告訴使用者哪些檔案擋住了，請使用者處理後再 ff；
  不得 stash、不得丟棄使用者的變更。
- Windows 上所有 git 指令加 `-c core.longpaths=true`（長路徑檔在沒有這個旗標時會被看成已刪除，BAT T0583 實測）。

## 塔台直接合併判準

**五條全部成立**才可走模式 ①；任一條不成立、或資料取不到 → 派合併工單。資料來源見下一節。

1. **`main` 沒有前進，或只在 `_ct-workorders/**` 前進**（放寬版，D031）：
   `behind == 0`；**或** `git diff --name-only <base>..<mainHead>` 列出的檔案全部在 `_ct-workorders/**` 底下。
   （塔台的工單記帳 commit 幾乎一定讓 `main` 前進，所以採放寬版。）
2. Worker 回報的 `validated_sha` 等於 `head`（分支目前 SHA）。
3. `outOfScopeFiles` 是**空陣列**（`null` 不算通過：代表讀不到工單或工單沒有 `affects_files`），**且** `touchesCtWorkorders == false`。
4. `conflicts == []`（`null` 不算通過）。
5. `dirty` 是**空陣列**（`worktreeMissing: true` 或 `dirty: null` 不算通過），**且**主 checkout 沒有與 `changedFiles` 重疊的髒檔
   （`git -C "<主 checkout>" status --porcelain` 的路徑與 `changedFiles` 取交集為空）。

## 直接合併的做法

**不論 `behind == 0` 或第 1 條的放寬情況，一律在整合 worktree `--no-ff` 合併後，再對 `main` `--ff-only`（D031）。**
不使用「`behind == 0` 時直接對 `main` `git merge --ff-only ct/T####`」的線性做法。

1. 記下 `base_main_sha` = 目前 `merge_target` 的 SHA。
2. 整合 worktree 乾淨 → `git -C "<integration_worktree>" switch -c ct-merge/T#### <base_main_sha>`。
3. `git -C "<integration_worktree>" merge --no-ff -m "merge(ct): T#### <標題>" ct/T####`。
4. 衝突 → `git -C "<integration_worktree>" merge --abort`，改派模式 ② 合併工單。
5. 不重跑驗收：第 1 條成立時，合併結果的產品檔與 `head`（= `validated_sha`）相同，`main` 多出的只有 `_ct-workorders/**`。
6. 做 § 收單 SHA 比對五步 的 ①～③、⑤。
7. 斷點 E（[yolo-mode.md](yolo-mode.md)）→ `git -C "<主 checkout>" merge --ff-only ct-merge/T####` → 第 ④ 步。
8. § 合併完成後清理。

塔台做模式 ① 用到的 git 指令就是本節與 § 共同護欄、§ 收單 SHA 比對五步、§ 合併完成後清理 列出的這些；其他 git 寫入操作不屬於模式 ①。

## 合併判準資料來源

### `--worktree-status`（BAT T0585）

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --worktree-status T#### --notify-id "$BAT_TERMINAL_ID"
```

或 MCP `bat_worktree_status`（參數 `workorder: "T####"`，見 [auto-session.md](auto-session.md) § BAT MCP 唯讀 tool；
MCP 失敗就改用上面的 helper，再失敗就改用 git）。helper 路徑、`"${BAT_HELPER_NODE:-node}"` 與防注入規則同
[auto-session.md](auto-session.md) § 執行方式、§ 安全邊界。

- 唯讀：BAT 不 checkout、不 merge、不 commit。

#### 查詢時機與資料來源（`source`，v5.4.0+）

- **舊 BAT（`< 0.7.0-pre.4`）**：只查**執行中**的 Worker 分頁，所以要在 `--close-worker` 之前查；BAT 重開後由已存分頁仍可找到。
  分頁關閉後回 exit `3`，改用 git。
- **BAT `>= 0.7.0-pre.4`**：Worker 分頁回收後也可查（`--close-worker --worktree keep|remove` 之後照樣 `--worktree-status T####`），
  不必搶在回收前查，也不必自己用 git 重算。
- **判定是哪一種**：成功回傳（exit `0`）**有** `source` 欄位 = BAT `>= 0.7.0-pre.4`；沒有 = 舊 BAT。
  本 session 還沒有任何一次帶 `source` 的成功回傳時，照舊 BAT 處理（回收前查）。

BAT `>= 0.7.0-pre.4` 依序找、第一個找到的就用，以 `source` 標明（規則以 BAT `docs/agent-guide/worktree-status.md` 為準）：

| `source` | 何時 | 備註 |
|---|---|---|
| `live` | Worker 分頁還在執行（含 BAT 重開後的已存分頁） | T0585 原行為 |
| `exited` | 分頁已結束，且在 BAT 的結束紀錄內（**10 分鐘、最多 32 筆**） | 另帶 `exited: true`、`exitedAt`；`terminalId` = 已結束的 id。紀錄只在 BAT 記憶體，BAT 重開即消失 |
| `git` | 以上都沒有，且**以工單號查詢 + 塔台權杖 + 塔台分頁仍在執行** | BAT 從塔台分頁**建立時的 cwd** 所在 repo，依 `.bat-worktrees/<repo>/<T####>`、分支 `ct/<T####>` 找回；`terminalId: null`。塔台分頁在別的 repo 開的就找不到 |

- worktree 仍登記（以 `--worktree keep` 關閉）→ `dirty` 照常讀。已 `--worktree remove`（只剩分支）→ `dirty: null`、`dirtyCount: null`、
  `worktreeMissing: true`，其餘欄位照算（`source: git` 與 `exited` 都可能出現）。判準第 5 條照舊不算通過，見 § 塔台直接合併判準。
- 有結束紀錄但不在本塔台範圍內 → exit `4`（`NOT_OWNER`），BAT 不會再往 git 找。
- 用 `terminalId` 參數、Worker 權杖或 server token 查詢不走 `git` 這一步；塔台照本節指令以工單號查詢即可。
- **五條判準要在合併前取得**（v5.6.1，T0166 段 E）：分支合併進 `<merge_target>` 之後再查到 `source: git` 時，`base` 是
  `merge-base HEAD ct/T####`——分支已合併，所以等於 `head`——而且 `ahead 0`、`changedFiles []`，拿不到原始派工 base 與變更清單。
  所以 § 塔台直接合併判準 的五條判準必須在合併前查；合併後的查詢只能確認分支已併入，不能拿來補判準。

**exit code**（判斷只看 exit code；stderr 另印 `worktree-status: <CODE>`，只當診斷）：

| exit | 意義 | 塔台處理 |
|---|---|---|
| `0` | 成功，stdout 一行 JSON | 讀 JSON；`isolated: false` = 這個 Worker 不是隔離派出，沒有分支要合併 |
| `3` | `NOT_FOUND`。舊 BAT：分頁已關或找不到。BAT `>= 0.7.0-pre.4`：執行中與結束紀錄都沒有，且分支 `ct/T####` 已不在（已 `archive` 改名或刪除）或塔台分頁 cwd 不是 git repo | 改用 git |
| `4` | `NOT_OWNER`（不是本塔台派出的 Worker；含不在範圍內的結束紀錄） | 一行告知使用者，改用 git |
| `5` | `AMBIGUOUS`（同工單多個 Worker，例 Renew 重派） | 一行告知使用者，改用 git |
| `1` | 其他：用法錯誤、連線失敗、`UNSUPPORTED`（BAT 太舊）、`FORBIDDEN`、`TIMEOUT`、`GIT_FAILED`（分支或主 checkout 已不在；例：結束紀錄還在、分支已 `archive`）、`INVALID_ARGS` | 改用 git；同一 session 不重試同一指令 |

**JSON 欄位**（`isolated: true` 時；名稱以 BAT 為準）：

| 欄位 | 意義 |
|---|---|
| `terminalId` / `workorder` | Worker 分頁與工單；`source: git` 時 `terminalId: null` |
| `source` | BAT `>= 0.7.0-pre.4`：`live` / `exited` / `git`（`isolated: false` 時也有）；沒有這個欄位 = 舊 BAT |
| `exited` / `exitedAt` | `source: exited` 時：`exited: true` 與結束時間 |
| `isolated` | `false` 時除 `terminalId`、`source`（與 `exited` / `exitedAt`）外其餘欄位不存在 |
| `branch` / `path` / `mainCheckout` | 分支 `ct/T####`、worktree 路徑、主 checkout 路徑 |
| `base` | 派工 base（沿用時為 `merge-base HEAD ct/T####`） |
| `head` / `mainHead` | 分支目前 SHA、主 checkout 目前 `HEAD` |
| `ahead` / `behind` | 相對 `mainHead` |
| `dirty` / `dirtyCount` | worktree 未提交／未追蹤檔（最多列 100 筆）；目錄已刪（含已 `--worktree remove`）時 `dirty: null`、`dirtyCount: null`、`worktreeMissing: true`；查詢失敗時 `null` + `dirtyError` |
| `changedFiles` / `changedCount` | `mainHead...head` 的實際變更（`--no-renames`，搬移時新舊路徑都列；最多 500 筆） |
| `outOfScopeFiles` / `outOfScopeCount` | 不符工單 `affects_files` 的變更；`null` = 讀不到工單或沒有該欄位（**不代表範圍內**）；`_ct-workorders/**` 不算 |
| `touchesCtWorkorders` | 分支改到 `_ct-workorders/**` |
| `conflicts` / `conflictsError` | `merge-tree` 預測的衝突檔；`[]` 乾淨；`null` + `conflictsError` = 無法判斷；可 fast-forward 時固定 `[]` |
| `workorderFile` | 計算 `outOfScopeFiles` 用的工單檔 |
| `computedAt` / `cached` | 計算時間；`cached: true` = ahead／behind／changedFiles／conflicts 沿用同一組 `head`／`mainHead` 的結果（`head`／`mainHead` 永遠是當下值） |

### git（`--worktree-status` 取不到結果時）

`--worktree-status` 回 exit 非 `0` 時用這一節（例：舊 BAT 分頁已關、分支已改名或刪除、BAT 不支援；見上方 exit code 表）。
在主 checkout（`M`）直接查分支 `ct/T####`；**查不到的欄位一律視為該條判準不通過**：

| 判準需要 | 指令 |
|---|---|
| `head` / `mainHead` | `git -C M rev-parse refs/heads/ct/T####`、`git -C M rev-parse <merge_target>` |
| `base` | `git -C M merge-base <mainHead> <head>` |
| `behind` / `ahead` | `git -C M rev-list --left-right --count <mainHead>...<head>`（左 = behind、右 = ahead） |
| 第 1 條放寬情況 | `git -C M diff --name-only <base>..<mainHead>` |
| `changedFiles` | `git -C M diff --name-only --no-renames <mainHead>...<head>` |
| `outOfScopeFiles` | `changedFiles` 逐一對照工單 `affects_files`（`_ct-workorders/**` 除外）；無法確定 → 不通過 |
| `touchesCtWorkorders` | `changedFiles` 是否有 `_ct-workorders/` 開頭的路徑 |
| `conflicts` | `ahead > 0` 且 `behind > 0` 時 `git -C M merge-tree --write-tree --name-only --no-messages <mainHead> <head>`：exit `0` → `[]`，exit `1` → 有衝突，其他 → 無法判斷（不通過）；否則 `[]` |
| `dirty` | worktree 目錄存在 → `git -C <worktree> status --porcelain`；目錄不在 → 不通過 |

## 收單 SHA 比對五步

合併工單回報後（模式 ① 由塔台自己做完合併後），塔台依序確認：

1. `base_main_sha` = 派合併工單（或開始直接合併）當下的 `main`。
2. `head_sha` = 被合併工單 Worker 跑驗收時的 SHA（原工單回報的 `validated_sha`，且等於目前 `ct/T####`）。
3. merge commit 的 parent1 = ff 前的 `main`、parent2 = 第 2 步的 SHA：
   `git rev-parse <merge commit>^1 <merge commit>^2`。
   模式 ③ 沒有合併該分支的 merge commit：改為確認整合分支是從 `base_main_sha` 開出（`git merge-base <整合分支> <merge_target>` = `base_main_sha`），並以對照表與逐條重驗取代第 2 步。
4. ff 之後 `main` = merge commit（模式 ③ 為整合分支 head）：`git rev-parse <merge_target>`。
5. 合併期間 `main` 又前進了（`main` ≠ parent1，`--ff-only` 會被拒）：
   - `git diff --name-only <parent1>..<merge_target>` 只有 `_ct-workorders/**` → 在整合分支再 `git merge --no-ff <merge_target>` 一次後 ff
     （產品樹相同，不重跑驗收）；
   - 否則 Renew 合併工單重做（模式 ① 則改派模式 ②）；重派 Worker 前照 [work-order-system.md](work-order-system.md) § 回報處理流程 › 重派前回收舊 Worker 分頁（v5.12.0+）。

執行順序：第 1～3 步在讀完回報後做 → 需要時第 5 步 → 斷點 E → `--ff-only` → 第 4 步。任一步不成立 → 不 ff，回報使用者。

## 合併完成後清理

- 回收被合併工單的 worktree：
  `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --close-worker T#### --notify-id "$BAT_TERMINAL_ID" --worktree remove`
  （分頁已在收單時以 `keep` 關閉而回 exit `3` 時）改由塔台手動 `git -C "<主 checkout>" worktree remove "<worktree 路徑>"`（不加 `--force`）。
  worktree 有未提交或未追蹤變更 → 不刪，告知使用者。
- 🔴 不用 `--worktree archive`：它把分支改名為 `ct-archive/T####`，只在使用者明確要求封存時才用，**合併前絕對不用**。
- 分支 `ct/T####` 與 `ct-merge/T####` **保留到使用者同意刪除**；刪除用 `git branch -d`（不用 `-D`）。
- 整合 worktree 本身保留，供下次合併使用。
- **整合 worktree 離開合併分支**（v5.3.1+）：`--ff-only` 成功且 § 收單 SHA 比對五步 第 ④ 步確認之後，
  `git -c core.longpaths=true -C "<integration_worktree>" switch --detach`（非 Windows 可省略 `-c core.longpaths=true`，同 § 共同護欄），
  讓整合 worktree 不再佔用 `ct-merge/T####`。分支仍被某個 worktree checkout 時 `git branch -d` 會被拒，不 detach 的話，
  使用者同意刪分支時刪不掉（T0158 實測情境）。detach 不刪任何分支；下一次合併仍照 § 共同護欄 從 `base_main_sha` 開新的 `ct-merge/T####`。
  沒有 ff（斷點 E 選 `[B]` 暫不合併、或 ff 被拒）時不 detach，合併分支留給之後的 ff。

## 斷點 E

`--ff-only` 之前的暫停規則與畫面是 [yolo-mode.md](yolo-mode.md) § 斷點 E 的權威定義；各模式在 yolo 下是否自動 ff，以本檔
§ 三種模式 為準。
