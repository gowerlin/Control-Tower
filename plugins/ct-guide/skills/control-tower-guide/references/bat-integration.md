# BAT 整合協作

本檔是教材中 BAT（Better Agent Terminal）相關內容的**集中處**：BAT 是什麼、CT 與 BAT 怎麼分工、兩座塔台怎麼協作、
一張 Worker 分頁從開到關經過哪些步驟，以及每一步背後的設計理由。其他章節講到 BAT 時只放一兩句概念並連到這裡。

與終端無關的派工概念——auto-session 四階、Worker 無狀態、YOLO 與斷點、Agent 中立、成功判讀、降級鏈——在 `runtime-dispatch.md`。
確切的旗標、環境變數、exit code 與 helper 路徑以 CT 的 `auto-session.md`、`work-order-system.md`、`merge-workorder.md` 為準，速查用 `ct-help`。

---

## BAT 是什麼、CT 為什麼要整合它

CT 的工單流程本身不需要任何終端工具：塔台寫工單，使用者自己開一個新 session 輸入 `/ct-exec T0001`（Codex 是 `$ct-exec T0001`），
Worker 做完顯示 `T0001 完成`，使用者再把這行帶回塔台。v4 時代就是這樣跑的——可行，但每張工單都要人做三件機械事：
**開 session、貼指令、帶回報**。

BAT 是一個能同時開多個 agent 終端分頁的桌面終端（Electron）。它內建一個 RemoteServer，並提供兩支零依賴的 Node.js helper：
`bat-terminal.mjs`（開分頁、回收分頁、宣告分頁、查詢）與 `bat-notify.mjs`（把訊息送到指定分頁）。
CT 整合它之後，那三件機械事都交給機器：

| 人工做法（無 BAT） | BAT 內 |
|------------------|-------|
| 使用者自己開新 session、貼上 `/ct-exec T0001` | 塔台呼叫 helper，BAT 開出 Worker 分頁並帶入指令 |
| Worker 顯示 `T0001 完成`，使用者複製後貼回塔台 | Worker 用 `bat-notify` 把訊息預填到塔台分頁（yolo 時自動送出） |
| 收單後使用者自己關掉 Worker 分頁 | 塔台收單後請 BAT 回收該單的分頁（`worker_auto_close`） |
| 重派同一張工單前，使用者自己關掉舊 Worker 分頁 | 塔台重派前先請 BAT 回收舊分頁（v5.12.0） |

BAT 不可用時，CT 沿降級鏈退回新終端分頁、剪貼簿、文字提示（`runtime-dispatch.md` § 降級鏈）——**BAT 是加速器，不是前提**。

---

## 分工原則：BAT 定介面，CT 照契約呼叫

CT 與 BAT 之間的每一個功能，都照同一個分工：

| | BAT | CT |
|---|---|---|
| 負責 | 提供能力：開／關分頁、注入環境變數、組 `/` 或 `$`、設分頁標題、權限判定、worktree 建立與狀態查詢 | 決定**何時**呼叫、帶什麼參數，以及結果怎麼影響工單流程 |
| 介面 | **定契約**：參數名、值域、exit code 語意、env 名、JSON 欄位、MCP tool 名 | **照契約寫**，不得更改；契約不清楚就回問 BAT，不自行補完 |
| 判斷依據 | — | **只看 exit code**（MCP 只看 `isError`）；stdout、stderr 這類給人看的輸出不參與判斷 |

為什麼只看 exit code：給人看的文字會隨版本改字、改格式，它從來沒有承諾過語意（實例見 `runtime-dispatch.md` § 成功判讀）。
stderr 只在少數地方被用來**挑選提示文字**（例如 `Forbidden`），從不決定流程。

為什麼介面由 BAT 定：分頁、權杖、worktree 都是 BAT 的 runtime 物件，持有它的一方回答最準。CT 若自己記一份
「哪個分頁是誰派的」或「這台 BAT 是哪一版」，就多了一份可能與實際脫節的狀態——這和 `concepts.md` § Worker 無狀態、塔台有狀態
是同一種分工：塔台持有進度與決策，終端是 BAT 的事。

---

## 兩座塔台怎麼協作

BAT 本身也是一個用 CT 管理的專案，有自己的塔台。CT 的 BAT 相關功能，幾乎都是兩座塔台跨專案協作的產物：

```
BAT 塔台：發現 CT 需要配合的新能力 → 寫 CT-T### 委派單（DELEGATE）
    ↓
BMad-Guide 塔台（CT 的家）：受理 → 開本地工單 → Worker 改 CT 規格
    ↓
CT 發版 → 回覆 BAT 塔台：已落地什麼、與規格的差異、疑問
    ↓
BAT 發佈對應版本後 → 另開工單做 runtime 驗收
```

幾條固定的規矩：

- **介面權威在 BAT repo 的 `CLAUDE.md`**（委派單的規格若與 `CLAUDE.md` 不一致，以 `CLAUDE.md` 為準，差異寫進回覆）
- **CT 不寫 BAT repo**：BMad-Guide 塔台只唯讀參考 BAT 的文件與 helper，修改永遠由 BAT 塔台自己做
- **CT 可以先發**：CT 常在 BAT 新版發佈前就發版，因為新功能都設計成「舊 BAT 失敗即降級」（見下方〈版本對照表〉）；
  所以 runtime 驗收要等 BAT 發佈後**另開工單**，不混在 CT 發版工單裡
- 回覆裡可以提出疑問或異議——這正是跨專案協調的「回覆稿異議段落」（`advanced-patterns.md` § 回覆稿的異議段落）

本 repo 的實例：

| BAT 委派單 | 內容 | 本地工單 | CT 版本 | 需要的 BAT |
|-----------|------|---------|--------|-----------|
| CT-T011 | 收單後回收 Worker 分頁（`--close-worker`、`worker_auto_close`） | T0134 | v5.1.0 | `>= 0.6.1-pre.4` |
| CT-T013 | 塔台分頁角色宣告（`--set-role tower`） | T0139 | v5.2.0 | `>= 0.6.1-pre.6` |
| CT-T014 | 每分頁範圍權杖（文件與失敗提示） | T0149 | v5.2.4 | `>= 0.7.0-pre.1` |
| CT-T015 | worktree 隔離派工、BAT MCP 唯讀 tool | T0155 | v5.3.0 | `>= 0.7.0-pre.2` |
| CT-T016 | 合併工單 | T0155 | v5.3.0 | `>= 0.7.0-pre.2` |
| CT-T017 | § 一 `--worktree-status` 分頁關閉後可查（`source`）；§ 二 斷點 D（Worker `blocked`） | T0161（§ 一）、T0163（§ 二） | v5.4.0、v5.5.0 | `>= 0.7.0-pre.4` |
| CT-T018 | Worker 啟動確認（`--wait-started`、exit `8`、MCP `agentStarted`） | T0165 | v5.6.0 | `>= 0.7.0-pre.6` |
| CT-T019 | Worker 問塔台的結構化通道（`--ask`、`bat_wait_question`、`bat_list_questions`、`--answer`、`blockedReason: tower`） | T0169 | v5.7.0 | `>= 0.7.0-pre.7` |
| CT-T020 | codex 分頁的 OSC 7501（斷點 D 接受 `blockedDetection: osc`／`blockedReason: input`、codex 的 `--wait-started`／`agentStarted`） | T0172 | v5.8.0 | `>= 0.7.0-pre.9` |
| CT-T021 | Claude session 識別：跨 session 選收件人、MCP `claudeSessionName`／`claudeSessionId`、`scope: towers`、面板提示 | T0174 | v5.9.0 | `>= 0.7.1-pre.1` |
| CT-T022 | 重派前回收舊 Worker 分頁（BAT BUG-170；沿用 `--close-worker`，BAT 不改程式） | T0184 | v5.12.0 | 不變（`--close-worker` 自 v5.1.0） |

CT-T015 與 CT-T016 由同一張本地工單一起處理，因為兩者是同一個功能的前後兩半：隔離派工產生分支，合併工單把分支收回 `main`。
CT-T017 則反過來，一張委派單拆成兩張本地工單、兩個 CT 版本：§ 一 沒有爭議，先出 v5.4.0；§ 二 的斷點 D，使用者把方向改成
「yolo 下 Worker 有問題先問塔台」，於是和 yolo 提問通道一起出 v5.5.0。CT-T019 的實機驗收由 BAT 端統一跑，驗收找到的提問通道問題在 v5.7.1 補上
（見 `work-order-lifecycle.md` 〈yolo 提問通道〉）。
CT-T021 方向反過來：需求由 CT 塔台先提給 BAT（D067，CT 不向 Claude Code 提需求），BAT 實作後再以委派單請 CT 接上。
跨專案協調的五種類型與流程見 `advanced-patterns.md` § 跨專案協調。

---

## 一張分頁的生命週期

把上面的功能按時間排起來，就是一張 Worker 分頁從開到關的完整路徑：

```
① 塔台分頁宣告角色      塔台啟動時 --set-role tower --mode <m>（模式改了再宣告）
        ↓
② 派工建立 Worker 分頁   --workspace／--cwd／--mode／--[no-]interactive（yolo 一律 --no-interactive）／--agent default
                         --skill ct-exec --workorder T####［--isolation worktree］［--wait-started 30000］
                         BAT 注入 BAT_TOWER_TERMINAL_ID、CT_MODE、CT_INTERACTIVE（隔離時另加 CT_HOME 等）
                         helper 等 Worker 的 claude 啟動（v5.6.0）：started 已啟動／unknown 無法判定／exit 8 不重派
        ↓
③ Worker 執行與通知      ct-exec 收尾後 bat-notify：on 預填、yolo 自動送出（--submit）
                         yolo 執行中有問題：送 T#### 提問，在工單裡等塔台答覆（v5.5.0）
                         BAT >= 0.7.0-pre.7：題目照樣寫工單，再以 --ask 問、bat_wait_question 等（v5.7.0）
        ↓
④ 收單回收              worker_auto_close: done 時 --close-worker（隔離工單加 --worktree keep）
                         同一張工單要重派時，先 --close-worker … --delay-ms 0 回收舊分頁再回到 ②（v5.12.0）
        ↓
⑤（隔離工單）合併後清理  合併完成後 --worktree remove、整合 worktree detach；分支保留到使用者同意
```

下面各節依序講每一步的設計理由。圖見 `diagrams.md` § 16。

---

## 兩組環境變數，兩個角色

BAT 會在它開出的每個終端注入環境變數。CT 把它們分成兩組，各自只服務一個方向（D004）：

| 方向 | 誰需要 | 必要變數 |
|------|-------|---------|
| **Tower dispatch**（塔台開 Worker） | 塔台 session | `BAT_SESSION`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`、`BAT_TERMINAL_ID`、`BAT_WORKSPACE_ID` |
| **Worker notify**（Worker 回報塔台） | Worker session | `BAT_TOWER_TERMINAL_ID`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN` |

關鍵在 `BAT_TOWER_TERMINAL_ID`：它不是塔台本來就有的值，而是**派工時才產生**的——
塔台把自己的 `BAT_TERMINAL_ID` 傳給派工 helper，BAT 再把它注入 Worker 的環境，Worker 收尾時就知道要通知哪個終端。

**為什麼要拆開？** 如果把兩組混成一份「BAT 必要變數」清單，塔台會因為自己沒有 `BAT_TOWER_TERMINAL_ID` 而誤判「不是 BAT 環境」，
退回剪貼簿派工。拆開之後，每一方只檢查自己那個方向需要的變數。

v5.2.0 起塔台還會用一次 helper 宣告自己的分頁（見下方〈塔台分頁角色宣告〉）。這次呼叫只需要 `BAT_SESSION`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`、`BAT_TERMINAL_ID`，
**不需要** `BAT_WORKSPACE_ID`——它不開新分頁、只設定自己，用不到「分頁要落在哪個 workspace」。道理和上面相同：每一次呼叫只檢查它那個方向真正需要的變數。

兩組表裡都有的 `BAT_REMOTE_TOKEN`，自 BAT `>= 0.7.0-pre.1` 起是**每個分頁專屬**的範圍權杖，不再是一把全權的 server token；
`BAT_TOWER_TERMINAL_ID` 也因此多了一層意義——有它的分頁就是 Worker 分頁。兩者的設計理由見下方〈範圍權杖與分頁角色〉。

另一個相關的假陰性：某些 helper shell（Git Bash、MSYS、壓縮 shell）看不到 BAT 注入的變數。
CT 規定在 Windows 上要用 native PowerShell 再查一次（v5.12.7 起只列變數名稱、不輸出值，`BAT_REMOTE_TOKEN` 只記「已設定」）；PowerShell 看得到就視為 BAT 可用，記為 `shell env visibility mismatch`，不得因此降級。

---

## 塔台分頁角色宣告（v5.2.0）

Worker 分頁是 BAT 開的，BAT 從一開始就知道它是誰：標題是 `<Agent> · Worker · T####`，環境裡有派工時注入的 `CT_MODE`。
塔台不同——它跑在**使用者自己開的分頁**裡，BAT 既不知道這個分頁是塔台，也不知道塔台現在是什麼模式。
v5.2.0 起，塔台啟動時用一次 helper（`--set-role tower`）向 BAT 宣告自己，補上這兩項資訊。宣告之後 BAT 才能：

1. 把分頁標題設成 `<Agent 顯示名> · Tower`，與 Worker 分頁對應（使用者自己改過名就保留，不覆蓋）
2. 知道塔台是不是 `yolo`——BAT 端的用量限制自動繼續只套用在 yolo 分頁；塔台不宣告模式，就落不進這個判斷

**標題由 BAT 組，CT 只負責呼叫。** 這與下方〈誰負責 `/` 還是 `$`〉、`runtime-dispatch.md` § Agent 中立 是同一種分工：
跟終端分頁、agent 有關的呈現由持有它的 BAT 決定，塔台 skill 不必知道標題長什麼樣。

**每次啟動都宣告，模式變了再宣告。** 時機是塔台啟動、狀態面板顯示之前呼叫一次；BAT 端冪等，同一分頁重複啟動也照常呼叫，塔台不必記「宣告過沒有」。
session 中以 `*config auto-session <m>` 改了生效值，就帶新的 `--mode` 再呼叫一次。每次都要帶 `--mode`：不帶時 BAT **不會清除**已記錄的模式，
少帶一次，BAT 就會一直以為塔台還是舊模式。v5.5.0 之前 YOLO 的啟動詢問只問 Worker 互動旗標、不改模式，所以不會觸發再宣告（v5.5.0 起 yolo 已不再有這個詢問）。

**只看 exit code，非 0 一律當「不支援」。** 不重試、不改用其他方式、不影響塔台啟動；狀態面板的 `分頁標題` 欄只記三種結果：
`已設定`／`不支援（BAT 太舊）`／`略過（非 BAT）`。這延續 `runtime-dispatch.md` § 成功判讀 的「信機器語意」，也和下方〈收單後回收 Worker 分頁〉一樣是**可接受的失敗**：
分頁標題是便利，不是塔台運作的前提，沒有理由讓它擋住啟動。

**Worker 不宣告。** `ct-exec` 等 Worker 與工具 skill 不得呼叫——Worker 分頁的標題在 BAT 建立分頁時就已決定；
若在 Worker 分頁誤呼叫，反而會把 Worker 標成 Tower。BAT `>= 0.7.0-pre.1` 起 BAT 端也會拒絕這種呼叫（exit `1`，見下方〈範圍權杖與分頁角色〉）；
Worker skill 本身不變，仍然不呼叫。

**CT 可以先發。** 這個功能需要 BAT `>= 0.6.1-pre.6`（CT v5.2.0 發佈時該版尚未發佈，以實際發佈版號為準）。依 CT 本體規格，舊版 helper 不認得這個參數，
會在建立任何分頁之前就以 exit `1` 結束，正好落進上面「非 0 即不支援」的降級路徑——所以 CT 不必等 BAT 發版，也不必判斷 BAT 版本
（理由同 `runtime-dispatch.md` § 降級鏈 的「先送、失敗才降級」）。

**分頁標題不是 session 名稱（v5.9.0）。** 標題 `Claude CLI · Tower` 是給人在 BAT UI 上看的；Claude Code 的 ListAgents 看的是另一個名字——
BAT `>= 0.7.1-pre.1` 啟動 claude 分頁時用 `--name` 給的名稱（例 `BMad-Guide · Tower`、`BMad-Guide · Worker · T0174`）。
從一般分頁開的塔台，宣告之後標題會變成 `· Tower`，session 名稱卻已在啟動時定為 `<工作區> · <短 ID>`，事後改不了。
所以 v5.9.0 的狀態面板在這種情況多一行提示：改用 BAT「以塔台開啟 Claude」開塔台，別的專案塔台就能直接在 ListAgents 找到你。
這只是提示：不擋啟動、不替使用者改名；舊 BAT、MCP 不可用時直接不顯示。「以塔台開啟 Claude」也**只負責命名**，塔台照樣要靠這裡的 `--set-role tower` 宣告。

> 呼叫條件、指令參數、PowerShell 寫法、exit code 對照與防注入規則以 CT 的 `auto-session.md` § 塔台分頁角色宣告、§ 安全邊界 為準；
> 面板欄位定義見 CT 的 `memory-protocol.md` § 塔台狀態面板。本節只講設計理由。

---

## 派工：建立 Worker 分頁

### `--workspace` 與 `--cwd`：修的是兩件不同的事

派工時兩個參數都要傳，而且不能互相取代：

| 參數 | 決定什麼 | 不傳會怎樣 |
|------|---------|-----------|
| `--cwd` | Worker 在**哪個目錄**執行 | 繼承呼叫端的 cwd；多數時候正確，但塔台 session 的 cwd 可能早已漂移，而且派工當下看不出來 |
| `--workspace` | 終端分頁落在 **BAT 的哪個 workspace** | 新分頁落在使用者**當下正在看**的 workspace——這是 BAT 的刻意設計，不是 bug |

實際發生過的現象是「**cwd 正確，分頁卻落錯 workspace**」：同時開著好幾個專案時，Worker 跑在對的目錄，
卻出現在另一個專案的分頁列裡。這正是只傳 `--cwd`、沒傳 `--workspace` 的結果，而且非常容易漏看。

即使派工參數都對，Worker 開工時仍會跑落點檢查（見 `governance.md`）——派工端與執行端各自防守，不互相假設。

### 誰負責 `/` 還是 `$`

塔台派工時只送一組**與 agent 無關的 payload**：要執行哪個 skill、哪張工單。
Worker 該收到 `/ct-exec T0001`（Claude Code）還是 `$ct-exec T0001`（Codex），由 BAT 依實際啟動的 agent 組出來。
這讓塔台 skill 不必知道對面是哪個 AI 工具。agent 的選擇見 `runtime-dispatch.md` § Agent 中立。

**用 plugin 安裝的 Codex 接不到 BAT 派工（v5.14.0）。** BAT 組出來的只有 `/ct-exec`、`$ct-exec` 兩種，不帶 plugin 前綴。Claude Code 的 plugin skill 不帶前綴也叫得到，所以 Claude 端不論手動或 plugin 安裝都能接派工；Codex 的 plugin skill 只能用 `$ct:ct-exec` 叫，`$ct-exec` 不會載入它——只裝 plugin 的 Codex Worker 收到指令，卻沒有 CT skill 可用。CT 沒有請 BAT 為此改介面，而是寫明 **Codex 搭配 BAT 派工繼續用 zip 手動安裝**：BAT 不必知道 Worker 怎麼裝 CT，塔台也照舊只送 `--skill`。各情況的寫法以 CT `auto-session.md` § 依安裝方式的 skill 呼叫字串為準；plugin 是什麼、並存時誰生效見 `governance.md` § plugin marketplace：另一種安裝方式。

> 派工指令的完整參數表以 `auto-session.md` § BAT 內部終端路由為準；SKILL.md 裡的範例是摘要，不能拿來直接派工（見 `governance.md` § 摘要授權規則）。

### worktree 隔離派工（v5.3.0）

工單 frontmatter 有 `isolation: worktree` 時，塔台在派工命令最後加 `--isolation worktree`，BAT 就不讓 Worker 直接在主 checkout 工作，
而是先建一個獨立的 git worktree 與分支 `ct/T####`（base = 主 checkout 當下的 `HEAD`），讓 Worker 在裡面執行。
**沒有這個欄位就不加**——預設不隔離，派工命令與 v5.2.6 逐字相同。為什麼要隔離、Worker 在裡面怎麼工作、之後怎麼合併，
屬於工單流程，見 `work-order-lifecycle.md` § worktree 隔離與合併工單。這裡只講 BAT 這一端：

**BAT 多注入四個變數。** 隔離派出的 Worker 分頁才有：

| 變數 | 內容 | Worker 拿來做什麼 |
|------|------|-----------------|
| `CT_HOME` | 主 checkout 路徑 | **有它就代表在 worktree 裡**；工單一律讀寫 `$CT_HOME/_ct-workorders/` |
| `CT_WORKTREE` | worktree 路徑 | 確認自己的 worktree 收工前已全部 commit |
| `CT_WORKTREE_BRANCH` | `ct/T####` | 回報的 `branch` |
| `CT_WORKTREE_BASE` | base SHA | 回報的 `base_sha` |

這延續〈兩組環境變數，兩個角色〉的做法：**角色由派工時注入的變數決定**，Worker 不必自己推測「我是不是在 worktree 裡」。

**成功仍只看 exit `0`。** 成功時 stdout 多印 `worktree:`／`branch:`／`base:` 三行，塔台只把它們當證據記下（合併時對照），不參與判斷。
「有沒有真的隔離」是另一個問題，依序看：exit `0` → `bat-scripts.log` 該次派工紀錄的 `worktree` 欄位（字串＝已隔離、`null`＝未隔離）→ 讀不到紀錄才看 stdout 那三行。
這個 log 的位置照 BAT helper 的解析順序找：有 `BAT_HELPER_LOG_DIR`（headless 用；須為絕對路徑，相對路徑會被忽略，v5.3.2 補記）就在那裡，否則在 `BAT_USER_DATA` 底下的 `Logs\`；兩個變數都沒有時 CT 不猜位置，當作讀不到 log（v5.3.1，以 CT `auto-session.md` § BAT 派發成功判讀規則 第 2 點為準）。
會判成未隔離的情況是新版 helper 搭配不認得隔離的舊 BAT 主程式：分頁照常建好，但**實際沒有隔離**（正常安裝 helper 與主程式同版出貨，這是防禦性規則；細節見 CT `auto-session.md` § worktree 隔離派工 第 2 點）。
塔台照實告訴使用者「未隔離」，之後把這張單當非隔離工單處理，不假裝它有分支可合併。

**exit `7`（`WORKTREE_FAILED`）：不重試、不建分頁、不自動改成非隔離。** worktree 建不起來（不是 git repo、位置被佔用、分支已在別處 checkout）時，
BAT 不建分頁、以 exit `7` 結束。塔台把原因告訴使用者，由使用者決定排除原因後重派，或明確同意改非隔離派工；yolo 下同樣暫停等人。

**為什麼不自動退回非隔離？** 這和 `runtime-dispatch.md` § 降級鏈 的「環境降級靜默進行」剛好相反，理由是降級的代價不同：
一般工單降級成剪貼簿，Worker 還是在同一個主 checkout 做同一件事，只是多一步人工；隔離工單降級成非隔離，
Worker 會**直接改主 checkout**——使用者選擇隔離，往往正是因為有別的工單同時在跑。這不是「換一條路做同一件事」，而是換了一件事，所以要人決定。
同理，舊 BAT 不認得 `--isolation`（exit `1`）時，隔離工單也**不走**降級鏈（`--prompt` 改送、新終端、剪貼簿都會讓 Worker 落在主 checkout），停下來等使用者。

> 派工命令、stdout 證據行、exit `7` 與舊 BAT 的處理以 CT 的 `auto-session.md` § worktree 隔離派工 為準；
> Worker 端規則以 `ct-exec/SKILL.md` § Worktree Isolation 為準。本節只講設計理由。

### 等 Worker 真的起來：`--wait-started`（v5.6.0）

helper 建好 PTY 就回 exit `0`，啟動指令約半秒後才寫進分頁——所以 exit `0` 只代表「分頁在」，不代表 Worker 起來了（BAT BUG-151）。
BAT `>= 0.7.0-pre.6` 讓 claude 的 `SessionStart` hook 回報「已啟動」，CT v5.6.0 據此在派工命令最後加 `--wait-started 30000`：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" \
  --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
  --cwd "<專案根目錄>" --mode <yolo|ask|off|on> [--interactive|--no-interactive] \
  --agent default --skill ct-exec --workorder T#### [--isolation worktree] --wait-started 30000
```

（示意；完整參數表與條件以 CT `auto-session.md` 為準，不得照抄派工。）

- **值固定、不開設定**：`30000` 是 BAT 的建議值，只影響派工那一次 helper 等多久，所以 CT 不為它新增 config。
- **一定帶 `--notify-id`**：BAT 只讓塔台查自己派出的 Worker，`--wait-started` 少了它就是用法錯誤——這和〈範圍權杖與分頁角色〉是同一套最小權限。
- **只用在派工**：`--close-worker`、`--set-role`、`--worktree-status` 不帶；降級成 `--prompt` 派工時也不帶。
- **不帶時完全不變**：BAT 契約保證不帶參數時輸出與 exit code 都和以前一樣，所以舊 BAT 降級後的路徑就是 v5.5.1 的路徑。

四種結果怎麼讀、exit `8` 為什麼不能重派、舊 BAT 怎麼自動退回，見 `runtime-dispatch.md` § Worker 啟動確認。

> 參數、四種結果、`started:` 行解析與舊 BAT 降級以 CT 的 `auto-session.md` § Worker 啟動確認 為唯一權威；
> BAT 端契約以 BAT `docs/agent-guide/worker-launch-confirmation.md` 為準。本節只講設計理由。

### Helper 用哪個 node：`BAT_HELPER_NODE`（v5.2.1）

v5.2.1 起，所有 BAT helper 呼叫（派工、Worker notify、回收分頁、角色宣告）都以 `"${BAT_HELPER_NODE:-node}"` 執行。
本機沒有這個變數就用 `node`，行為與先前相同；遠端分頁（WSL／SSH／Docker）則由 BAT 注入它自帶的 bundle node 路徑——
因為遠端的 login shell 可能重設 PATH、找不到 `node`，helper 還沒開始就失敗。
安全面上，執行檔只能是這個變數的值或字面 `node`，不得換成其他執行檔（規則見 CT 的 `auto-session.md` § 執行方式「Node 解析」、§ 安全邊界）。

---

## 權限與分頁角色

### 範圍權杖與分頁角色（v5.2.4；v5.2.5 補面板與分頁描述）

BAT `>= 0.7.0-pre.1` 把本機分頁的 `BAT_REMOTE_TOKEN` 換成**分頁專屬**的範圍權杖（遠端分頁早就是如此）。變數名、helper 的讀法、CT 的呼叫方式都沒變，
變的是「這把權杖能做什麼」：BAT 依分頁角色決定 helper 權限。CT v5.2.4 只改文件與失敗提示，正常流程不變。

**角色只看一個變數。** 分頁環境裡**有沒有** `BAT_TOWER_TERMINAL_ID` 就決定了它是什麼：

| 分頁 | 判定 | 能做的事 |
|------|------|---------|
| 塔台分頁（含使用者自己開的一般分頁） | 沒有 `BAT_TOWER_TERMINAL_ID` | 派工、`--close-worker`（只關自己派出的）、`--set-role`（只設自己） |
| Worker 分頁 | 有 `BAT_TOWER_TERMINAL_ID` | 只能 `bat-notify` 給綁定的那個塔台 |

這個變數本來就是派工時才注入、只給 Worker 用來知道「要通知誰」（見上方〈兩組環境變數，兩個角色〉），所以它天然就是「這個分頁是被派出來的」的標記。
BAT 拿它做最小權限：Worker 的工作只需要回報自己的塔台，其他能力本來就不該有。CT 的正常流程全在表內——塔台只在自己分頁派工、回收、宣告，
Worker 只回報自己的塔台——所以 CT 不需要改任何呼叫。

**塔台要在一般分頁啟動。** 在 Worker 分頁裡啟動塔台，派工、`--set-role`、`--close-worker` 都會 exit `1`。
塔台不會因為看到這個變數就拒絕啟動，也不預先跳過呼叫——照常呼叫，失敗走既有規則。理由同 `runtime-dispatch.md` § 降級鏈 的「先送、失敗才降級」：
權限是 BAT 的事實，由 BAT 回答最準，塔台不另寫一份可能與 BAT 脫節的判斷。

**`Forbidden`／`RECOVERY_PENDING` 只用來挑提示。** 判斷仍然只看 exit code：派工走降級鏈、`--set-role` 記為不支援、`--close-worker` 照它的 exit code 表；
不重試、不改用其他方式，`RECOVERY_PENDING`（BAT 重開後 Recovery 提示還沒回答時派工被拒，BAT 保證沒有建出分頁）也**不自動重派**。
stderr 含這兩個字時，只是降級訊息**多一句原因提示**，告訴使用者該去哪裡處理（換到一般分頁啟動塔台；先在 BAT 視窗回答 Recovery 提示再派工）。
這與 `runtime-dispatch.md` § 成功判讀 的「信機器語意」不衝突：stderr 字串**不參與判斷**，只決定給人看的那一句話；
它也是降級鏈「靜默降級」的例外，道理和「BAT 版本舊必須明示」相同——這是使用者能修的狀況，靜默帶過等於把它藏起來。
不自動重派是因為 Recovery 提示要使用者做選擇，答完之前重派只會再被拒一次；答完之後要不要派，也是使用者的決定。

**權杖的值不外流。** 權杖現在代表的是**某一個分頁**的權限，不是大家共用的 server token，也不能假設它是。所以它的值不得在分頁間複製，
也不得寫進日誌、工單、回報區、剪貼簿或決策日誌；需要記錄時只寫「已設定」。helper 自己從環境變數讀取，CT 從來不需要經手它的值。
Worker 在回報區記錄 BAT 證據時同樣只寫「已設定」；Worker 分頁的權杖本來就只允許 `bat-notify` 給綁定的塔台，
這正是 Worker 收尾唯一需要的能力，所以 `ct-exec`／`ct-done` 的通知呼叫不必改。

**面板與對使用者的稱呼（v5.2.5）。** 在 Worker 分頁啟動的塔台，狀態面板 BAT 欄位直接顯示 `不可派發（Worker 分頁）`；
v5.2.4 的寫法是「可派發」後面加註「無法派工」，字面自相矛盾，v5.2.5 改成單一值。判定一樣只看 env，不為了填欄位另跑掃描。
同一輪也規定：塔台對使用者提到某個分頁時，用使用者在 BAT 上看得到的**分頁標題**（`<Agent 顯示名> · Tower`、`<Agent 顯示名> · Worker · T####`，使用者改過名就以使用者看到的為準），
不用 terminal ID——UUID 是給機器對帳用的（日誌、狀態檔、證據欄位、helper 參數），使用者在畫面上找不到它。

**舊 BAT 不受影響。** BAT `< 0.7.0-pre.1` 沒有分頁角色限制，不會出現 `Forbidden` 或 `RECOVERY_PENDING`，行為與 v5.2.3 相同。

> 權杖、角色、`Forbidden` 與 `RECOVERY_PENDING` 的確切規則與提示文字以 CT 的 `auto-session.md` § BAT 內部終端路由 › 範圍權杖與分頁角色 為準；
> 分頁怎麼稱呼見同檔 § 對使用者描述分頁；面板 BAT 欄位見 `memory-protocol.md` § 塔台狀態面板。本節只講設計理由。

---

## Worker 執行與通知

Worker 收尾的順序是**先寫最終狀態與回報區、commit 工單，最後才 notify**（`work-order-lifecycle.md` § Phase 4、§ BAT Notify；v5.7.0 起隔離與非隔離工單同一個順序，`ct-done` 也在 notify 前 commit 工單檔）。
通知走 `bat-notify.mjs`，目標是派工時注入的 `BAT_TOWER_TERMINAL_ID`；訊息是固定格式（`T#### 完成`／`部分完成`／`需要協助`；yolo 另有執行中的 `T#### 提問`，v5.5.0，見 `work-order-lifecycle.md` § yolo 提問通道）。
`CT_MODE=on` 只預填到塔台輸入列，`yolo` 預填並自動送出（`--submit`）；`ask`／`off`（含缺值）不加 `--submit`，顯示要手動帶回塔台的確切訊息。

**訊息與 `--source` 一律用工單完整 ID（v5.13.1）**：上面的 `T####` 是訊息種類的名稱。BAT 用 `--source` 比對 Worker 分頁登記的工單——
塔台派 `--workorder LB-T0184`，分頁登記的就是 `LB-T0184`；Worker 若送 `--source T0184`，BAT 對不上，那個分頁標不了 Done，
使用者一次關掉已完成的 Worker 分頁時也就漏了它。CT 判定這是自己範本的缺陷（範本原本只寫 `T####`），修在 CT 這邊，不請 BAT 另加備援比對。
三層修法（範本、Worker 送出前比對、塔台缺前綴容錯）與塔台容錯為什麼保不住 BAT 標 Done，見 `work-order-lifecycle.md` § 回報與通知用完整工單 ID。

通知只是「叫塔台來讀檔」：回報內容一律在工單檔裡，訊息本身不帶細節。所以 notify 失敗時工單已是最終狀態，
使用者把 Worker 顯示的固定訊息帶回塔台即可收單（`runtime-dispatch.md` § Worker 端的回報降級）。

---

## 收單後回收 Worker 分頁（v5.1.0；v5.3.0 補隔離工單）

BAT 派工讓開 Worker 不再費力，代價是分頁會一直累積：一個 PLAN 跑完，分頁列上留著一排早已收單的 Worker。
v5.1.0 新增 `worker_auto_close`，讓塔台在收單之後請 BAT 收掉該單的 Worker 分頁。本節只講設計理由；
選項值域見 CT 的 `tower-config.md` § 可用選項，指令、完整 exit code 表與參數防注入規則見 `work-order-system.md` § 回報處理流程、`auto-session.md` § 安全邊界。

**預設關閉。** `worker_auto_close` 預設 `off`，使用者明確設成 `done` 才生效；`off` 時收單流程與 v5.0.9 完全相同。
關分頁會讓裡面的輸出從畫面上消失，這種動作該由使用者選擇開啟，而不是預設替他決定。

**只回收沒有東西要看的單。** 下列條件全部成立才回收：`worker_auto_close: done`、工單 `DONE`、本次不 Renew、`BAT_SESSION=1`。
`PARTIAL`／`BLOCKED`／`FAILED` 一律不回收——這些單的分頁裡還有使用者或塔台要回頭看的東西：錯誤輸出、卡住的位置、Worker 留下的說明。
需要 Renew 的單也不回收，因為還有下一輪要接著做。只有乾淨結束的 `DONE`，分頁才真的用完了。

**收單之後才動手，並留一段延遲。** 回收發生在塔台輸出「已確認完成」**之後**，是收單的附帶動作，不是收單本身。
`worker_close_delay`（`0`–`300` 秒，預設 `10`）讓分頁在消失前多留一段時間。延遲期間 Worker 還在輸出**不會**取消回收——agent 回報之後常再印幾秒收尾，拿輸出當取消條件，回收常會被這段收尾輸出取消掉；只有使用者在那個分頁輸入才取消，因為那代表人還在用它（切換分頁時終端自動送出的回應不算輸入）。延遲到期後 BAT 再等分頁連續安靜 5 秒才關，最多再等 60 秒，仍在輸出就放棄、留下分頁。（v5.12.1 對齊 BAT T0545；定義以 CT 的 `tower-config.md` § 可用選項 為準。）

**歸屬由 BAT 判定。** 「這張單的 Worker 是不是本塔台派的」由 BAT 回答（找不到／不是你的），塔台不追蹤 terminal ID。
這延續 `concepts.md` § Worker 無狀態、塔台有狀態 的分工：塔台持有的是進度與決策，終端分頁是 BAT 的 runtime 物件，
由持有它的一方回答最準確；塔台若自己記一份 terminal ID，就多了一份可能與實際分頁脫節的狀態。

**只看 exit code。** 延續 `runtime-dispatch.md` § 成功判讀 的原則——信機器語意，不信給人看的文字。exit code 只需分成三類：

- **靜默**：回收已排定，或找不到分頁（必要時提示一次手動關閉）
- **一行回報、不重試**：分頁不是本塔台派的、對象不唯一、或分頁正忙
- **BAT 不支援或連線失敗**：一行警告，同一 session 不再重試

🔴 **回收失敗不影響收單。** 不論 exit code 為何，都不回寫工單、不改變下一步的判斷；YOLO 下也不計入斷點 B、不觸發任何斷點。
工單已經 `DONE` 是事實，不會因為一個分頁沒關掉而改變；讓附帶動作的失敗反過來影響收單或 YOLO 的健康判定，就是因果倒置。

**舊版 BAT 是可接受的失敗。** BAT 不支援 `--close-worker` 時，一行警告後照常收單，塔台不預先判斷 BAT 版本。
理由與 `runtime-dispatch.md` § 降級鏈 的「先送、失敗才降級」相同：直接送出、看 exit code，就完全不需要判版。

**隔離工單：分頁先關，worktree 留著（v5.3.0）。** 隔離工單回收時多帶 `--worktree keep`：只關分頁，worktree 與分支 `ct/T####` 留給合併。
等合併完成，才用 `--worktree remove` 清掉 worktree（不強制刪除；worktree 裡有未提交變更就不刪、告知使用者），分支保留到使用者同意刪除。
把「關分頁」與「刪 worktree」拆成兩個時間點，是因為兩者的前提不同：分頁在工單 `DONE` 時就用完了，worktree 卻要等成果進了 `main` 才真的沒用。
還有第三個值 `--worktree archive`，會把分支改名為 `ct-archive/T####`——**合併前不得使用**，否則合併要找的分支就不見了。
非隔離工單**不帶** `--worktree`，指令與行為和 v5.2.6 完全相同。

> 隔離工單的回收指令以 CT 的 `work-order-system.md` § 收單後回收 Worker 分頁 為準；合併後清理以 `merge-workorder.md` § 合併完成後清理 為準（v5.3.1 補：ff 之後整合 worktree `switch --detach`，不再佔著 `ct-merge/T####`——分支被某個 worktree checkout 時 `git branch -d` 會被拒，使用者同意刪分支時才刪得掉）。

### 重派前回收舊 Worker 分頁（v5.12.0）

收單回收處理的是「單做完了」；還有一種分頁會留下來：同一張工單**再派一次**的時候。yolo 提問逾時走備援、`BLOCKED`／`FAILED` 之後 Renew、
使用者停掉首派的 Worker 要求重來——這些情況塔台都是派一個**新的** Worker（不對舊分頁送按鍵），舊分頁就還開著。

**問題在收尾才浮現（BAT BUG-170）。** 同一個塔台、同一張工單有兩個 Worker 分頁時，新 Worker `DONE` 後的收單回收找到兩個候選，
BAT 拒絕猜，回 exit `5`（`AMBIGUOUS`）——兩個分頁都得使用者手動關。BAT 的「已回報」標示也以「同塔台、同工單」比對，舊分頁跟著標成 `✓`，看起來像剛完成。
與其在收尾時處理「不知道該關哪個」，不如在源頭就不讓兩個並存：**重派之前先關舊的。**

**用的是同一支 `--close-worker`，BAT 不用改。** 差別只在時機與延遲：派工之前呼叫、`--delay-ms 0`，隔離工單照樣加 `--worktree keep`
（worktree 與分支 `ct/T####` 留給新 Worker 沿用）。不會關錯分頁，是因為 BAT 在**呼叫當下**就鎖定唯一的候選分頁，之後新派的 Worker 分頁不在其中；
`--delay-ms 0` 也不是立刻殺掉——BAT 仍等舊分頁連續安靜 5 秒（最多再等 60 秒），這段時間使用者在舊分頁打字就會取消。

**不論結果都照常派工。** 回收是重派的前置清理，不是重派的前提：

- exit `0`（已排程）、`3`（找不到——使用者已經關了，或 BAT 重開沒還原）→ 直接派工
- exit `5`（對象不唯一）→ 一行提示使用者用分頁標題找到舊分頁手動關，照常派工
- exit `4`／`1`／其他 → 一行提示，照常派工；`1`（BAT 不支援或連線失敗）之後，這個塔台 session 的重派前回收與收單回收都不再嘗試——兩者共用同一個旗標

讓清理失敗擋住重派，就是讓附帶動作反過來決定主流程，和上一節「回收失敗不影響收單」是同一個道理。

**與 `worker_auto_close` 無關。** 設定是 `off` 也照樣回收（D094）。`worker_auto_close` 管的是「單做完要不要收分頁」這個偏好；
重派前回收管的是「同一張單不要同時有兩個 Worker」這個正確性問題，兩件事不能共用一個開關。

**三種情況刻意不回收**，各有理由：

- **`/ct-done` 補救派工**：補救的對象往往就是舊分頁停下來的現場，輸出可能正是要看的東西，所以保留（D094 由使用者決定）。
  代價是收單回收可能回 exit `5`，照收單回收的規則一行提示使用者手動關
- **研究單在原分頁「重讀工單」**：Renew 沒有派新 Worker，原分頁就是要繼續的那個 Worker
- **舊 BAT 不認得 `--wait-started` 時的去參數重派**：前一次根本沒建出分頁

> 適用條件、指令與 exit code 表以 CT 的 `work-order-system.md` § 回報處理流程 › 重派前回收舊 Worker 分頁 為唯一權威；BAT 端的介面以 BAT `CLAUDE.md`「Worker 分頁回收」節為準。

---

## 查詢通道：`--worktree-status` 與 BAT MCP（v5.3.0）

v5.3.0 之前，塔台想知道 Worker 的狀況只有一條路：讀工單回報區（以及事後查 `bat-scripts.log`）。BAT `>= 0.7.0-pre.2` 多了兩條**唯讀**的查詢通道：

| 通道 | 是什麼 | CT 用在哪 |
|------|-------|----------|
| `bat-terminal.mjs --worktree-status T####` | helper 指令；回傳隔離 Worker 的 worktree 狀態（一行 JSON：分支、ahead／behind、變更檔、範圍外檔案、預測衝突、髒檔…） | 合併前判斷「塔台能不能直接合併」的資料來源 |
| BAT MCP（`mcp__bat__*`） | BAT 啟動的 claude／codex 分頁裡的一組 MCP tool：自己是誰、列分頁、分頁狀態、讀輸出、等狀態改變、worktree 狀態；BAT `>= 0.7.0-pre.7` 另有 `bat_wait_question`（Worker 等答覆）與 `bat_list_questions`（塔台讀題）（CT v5.7.0） | 選用；目前沒有規則必須用 |

**唯讀是刻意的。** BAT 不 checkout、不 merge、不 commit——它只提供信號，合併由塔台決定、由合併工單執行
（理由見 `work-order-lifecycle.md` § worktree 隔離與合併工單）。

**`--worktree-status` 什麼時候查，看 BAT 版本。** 舊 BAT（`< 0.7.0-pre.4`）只查**執行中**的 Worker 分頁；隔離工單收單時以 `--worktree keep` 關掉分頁之後，BAT 就查不到了，
所以要先查、再回收。BAT `>= 0.7.0-pre.4`（CT v5.4.0+）回收後也查得到，不必搶在回收前查。新版的回傳多一個 `source` 欄位，標明資料從哪裡來：
`live` 是分頁還在執行；`exited` 是分頁已關，BAT 還留著它的結束紀錄（有時間與筆數上限，且只在記憶體裡，BAT 重開就沒了）；
`git` 是連結束紀錄都沒有，BAT 從塔台分頁開啟時所在的 repo 依分支 `ct/T####` 找回來。
塔台照樣不預先判斷 BAT 版本：成功回傳**有** `source` 才當新版，這個 session 還沒看過帶 `source` 的回傳就照舊版處理——先查、再回收。
不管哪一版，查不到（舊 BAT 分頁已關、不是本塔台派的、分支已改名或刪除、BAT 太舊）就改用 git 在主 checkout 直接算同樣的欄位，
**查不到的欄位一律視為該條判準不通過**——資料缺漏時偏向派合併工單，而不是偏向直接合併。
（v5.4.0；查詢時機與 `source` 的規則以 CT `merge-workorder.md` § 合併判準資料來源 › 查詢時機與資料來源 為準。）

**「回收後也查得到」不等於「合併後也查得到」（v5.6.1）。** `source: git` 的 `base` 是分支與 `main` 的 merge-base；
分支一旦合併，merge-base 就是分支自己的 `head`，於是 `ahead 0`、`changedFiles []`——原始派工 base 與變更清單都看不到了（T0166 實測）。
所以五條判準一定要在合併**之前**取；合併後再查，只能確認分支已經併入（CT `merge-workorder.md` § 查詢時機與資料來源）。

**MCP 範圍跟著分頁權杖走。** Worker 只能查自己（另可讀綁定塔台的 metadata，不能讀塔台輸出），塔台可查自己與自己派出的 Worker；
不在範圍內回錯誤，不是空結果。這和〈範圍權杖與分頁角色〉是同一套最小權限。判斷只看 tool 結果的 `isError`，摘要文字不參與——
與 helper 只看 exit code 同一個原則。有些 client（例 Claude Code）只把錯誤文字（例 `NOT_OWNER`）顯示給 agent、看不到 `structuredContent`；
這不影響判斷——看的仍是「是不是錯誤結果」，code 只用來挑給使用者的提示文字（v5.3.1 補記）。
連 code 都取不到（錯誤文字裡也認不出已知的 code）時，改走同功能的 helper CLI，以 helper 的結果為準——真的是範圍或權限錯誤，
helper 也會以非 0 的 exit code 拒絕；同一個 tool 不重試（v5.3.2，以 CT `auto-session.md` § BAT MCP 唯讀 tool 的降級鏈為準）。

**降級鏈：MCP → helper CLI → 檔案。** MCP tool 不存在或回 `UNSUPPORTED`／`CONNECT_FAILED`，就改用同功能的 helper；
沒有對應 helper 的查詢，就回到讀檔案（工單回報區、`bat-scripts.log`）。**目前沒有任何 CT 規則必須用 MCP**——
所有流程都能只靠 helper 與檔案完成，MCP 只是較省事的通道。所以舊 BAT 或在 Settings 關掉 BAT MCP 的使用者，行為與 v5.2.6 相同。
斷點 D（v5.5.0）是唯一只能用 MCP 的項目，但它不是必要流程：MCP 不可用時它不啟用，其他流程照常（見下一節）。

**`agentStarted`（v5.6.0，BAT `>= 0.7.0-pre.6`）。** `bat_get_state`／`bat_wait`／`bat_list_terminals` 的回傳多一個 `agentStarted`：
`true` 是該分頁的 claude 已執行 `SessionStart`（get-state／wait 另回 `agentStartedAt`）；`false` 是 BAT 注入了 hooks、但還沒收到；
`null` 是**無法判定**（codex、自訂 CLI、hooks 被關閉……），**不得當成啟動失敗**。`bat_wait` 也多了 `until: 'agent-started'`。
v5.8.0 起（BAT `>= 0.7.0-pre.9`），codex `>= 0.163.0` 的分頁也有信號：codex 自己送的第一個 OSC 7501 → `true`，之前 `false`；
`null` 只剩較舊或版本確認不到的 codex、自訂 CLI 等（見下一節〈codex 也看得到了〉）。
它是 Worker 啟動確認的選用查詢通道：派工當下的判讀看 helper 的 `--wait-started` 結果，MCP 不可用就不查——
所以「沒有 CT 規則必須用 MCP」仍然成立。

**問答的兩個 tool（v5.7.0，BAT `>= 0.7.0-pre.7`）。** `bat_wait_question` 讓 Worker 長輪詢自己問的題目，不能用時有 helper `--wait-answer`；`bat_list_questions` 讓塔台讀題，不能用時塔台改讀工單 `### 待塔台決策`。問答的**寫入**（提問、取消、答覆）沒有 MCP tool，只走 helper——BAT MCP 全部唯讀的原則不變。所以這兩個 tool 也不是必要條件（`work-order-lifecycle.md` § BAT 結構化通道）。狀態回傳另多一個 `pendingQuestions`（該 Worker 的待答題數），沒有這個欄位就代表 BAT 太舊。

**session 名稱與塔台清單（v5.9.0，BAT `>= 0.7.1-pre.1`）。** `bat_whoami`／`bat_list_terminals`／`bat_get_state` 多兩個鍵：
`claudeSessionName`（ListAgents 上的名稱）與 `claudeSessionId`。兩條讀法要記住：**鍵不存在 = 舊 BAT**，不要當成 `null`；
`claudeSessionId: null` **不代表沒有 session**（可能只是 hook 還沒回報）。這和 `pendingQuestions`「沒有欄位就代表 BAT 太舊」是同一種判讀。
`bat_list_terminals` 的 `scope` 也多了 `towers`：已宣告的塔台可以列出同一個 BAT 裡**所有工作區**的塔台。這是 BAT 特意放寬的範圍，
所以收得很緊——只給已宣告的塔台、每列只有識別用的欄位（工作區名稱、session 名稱、狀態），讀不到對方的輸出或狀態細節（仍是 `NOT_OWNER`）。
它只有一個用途：跨 session 選收件人的第 2 步（`advanced-patterns.md` § 跨 session 通知對方塔台）。舊 BAT 回 `INVALID_ARGS`，跳過即可；
helper 沒有對應的查詢，所以這一步只能用 MCP——它也不是必要流程，找不到就回到「請使用者轉交」，「沒有 CT 規則必須用 MCP」仍然成立。

> tool 清單、錯誤碼與範圍以 CT 的 `auto-session.md` § BAT MCP 唯讀 tool 為準（問答兩個 tool 的參數與欄位在 CT `yolo-mode.md` § Worker 向塔台提問 › BAT 通道）；`--worktree-status` 的指令、exit code 與 JSON 欄位以
> `merge-workorder.md` § 合併判準資料來源 為準。本節只講設計理由。

---

## 斷點 D：塔台看得到 Worker 在等人（v5.5.0；v5.5.1 補 BAT 版號；v5.6.0 更新已知限制；v5.7.0 補 `tower`；v5.8.0 補 codex 的 `input`）

Worker 停在等人回答——權限確認、AskUserQuestion、MCP 表單（elicitation）——從外面看，和「還在工作」或「已經閒置」很難分。
BAT `0.7.0-pre.4` 起用 claude 的 hooks 回報這個狀態：MCP 查到的分頁 `state` 多一個 `blocked`，另帶 `blockedReason`（`permission`／`question`／`elicitation`）
與 `blockedSince`；每個回傳也都帶 `blockedDetection`，說明這個分頁有沒有在回報。CT v5.5.0 用它定義斷點 D。

**它做什麼。** 塔台查到 Worker 分頁 `blocked`，就用分頁標題告訴使用者「`<分頁標題>` 在等你回答（原因：`<blockedReason>`）」，請使用者自己到那個分頁處理。
yolo 下這是**異常偵測**：yolo Worker 有問題應該問塔台（`work-order-lifecycle.md` § yolo 提問通道），停在等使用者，代表它用了提問工具、
碰上 MCP 表單或權限提示；塔台記入 YOLO 歷程，但**不暫停**其他流程。非 yolo 下只是告知。

**它刻意不做什麼。**

- **不代答、不送按鍵**：對 Worker 分頁寫入輸入，等於替使用者回答；答案只能由使用者自己給。
- **不當成失敗**：不重派、不 Renew、不計入斷點 B；同一次等待（同一個 `blockedSince`）只告知一次，不重複催促。
- **不輪詢**：不開背景監看，只在塔台本來就在看這個 Worker 時（使用者問進度、等回報、Renew 或重派前）順手看一眼。
- **只走 MCP**：沒有對應的 helper CLI。MCP 不可用、或回傳沒有 `blockedDetection`（舊 BAT）→ 斷點 D 不啟用，其他流程照常。
  所以它是唯一只能用 MCP 的項目，卻不違反上一節「沒有 CT 規則必須用 MCP」——它不是必要流程。

**`blockedDetection: none` 的意思。** 這個分頁沒有在回報 hook 或 OSC 7501（較舊或版本確認不到的 codex Worker、關閉 BAT MCP、自訂參數已含 `--settings`、raw command 派工等），
永遠不會回 hook 的三種原因（`permission`／`question`／`elicitation`），也不會回 codex 的 `input`。所以它的 `idle` **不能**解讀成「沒有在等人」——只是看不到而已。
v5.6.1 以前這裡寫成「永遠不會回 `blocked`」；BAT `0.7.0-pre.7` 多了下面的 `tower`，它不靠 hook，所以 v5.7.0 改成現在的說法；v5.8.0 再補上 `input`。

**codex 也看得到了（v5.8.0，BAT `>= 0.7.0-pre.9`）。** codex `>= 0.163.0` 會自己在終端送一段 OSC 7501（`state=idle|working|blocked`），
BAT 只讀、不改輸出，據此把分頁記成 `blockedDetection: osc`；`state=blocked` 就回 `blocked`、`blockedReason: input`、`source: 'osc'`。
CT 把 `input` 和 hook 的三種原因並列為「等使用者的原因」，處理完全相同：只以分頁標題告知、不代答、不送按鍵、不暫停流程、同一次等待只告知一次。
三個設計重點：

- **為什麼只有一個 `input`，不分權限或提問**：codex 的 OSC 7501 本身不分種類（核准提示、Plan mode 提問、elicitation 都是 `blocked`）。
  CT 本來就規定原因照原值顯示、不據此斷定是哪一種，所以多一個不分種類的值不必改邏輯。
- **為什麼使用者打字不會清掉 `input`**：hook 的原因是 BAT 從 claude 的事件推出來的，使用者輸入是很好的「已處理」信號；
  codex 則會在處理完後自己送下一個狀態，BAT 以 codex 的說法為準，避免在使用者打字但還沒答完時就誤清。代價是使用者答完、codex 還沒送轉換前，
  塔台可能再讀到同一次 `input`——「同一個 `blockedSince` 只告知一次」剛好吸收這個情況，不會重複催促。
- **優先序**：`exited` > hook 的原因／`input` > `tower` > `working`／`idle`。codex Worker 同時在等使用者和等塔台時，先回 `input`（使用者看得到的才需要告知），
  `input` 清除後塔台才會讀到 `tower`、去讀題答覆。`hook` 分頁不會因為輸出裡出現 OSC 7501 而變成 `osc`，兩種原因不會同時出現。

較舊的 codex、BAT 確認不到版本（例如 Windows 上 PATH 第一個是 npm 的 `codex.cmd`）、或舊 BAT（≤ `0.7.0-pre.8`）→ 仍是 `none`，CT 的行為和 v5.7.2 一模一樣——
這就是 v5.8.0 能在 BAT 發版前先改規則的原因：舊環境的「降級」就是現行行為。

**`blockedReason: tower` 不是斷點 D（v5.7.0，BAT `>= 0.7.0-pre.7`）。** Worker 經 BAT 結構化通道問了塔台、正在等答覆時，BAT 也回 `blocked`，原因是 `tower`。
它等的是**塔台**，不是使用者，所以塔台不告知使用者「在等你回答」，而是直接去讀題、答覆（`work-order-lifecycle.md` § BAT 結構化通道）——
就算漏收了 `提問` 通知，看到 `tower` 也照提問處理。它由 BAT 自己的問答紀錄判斷、和 `blockedDetection` 無關，codex Worker 也會出現。
Worker 同時在等使用者時，BAT 優先回 hook 的原因，那就照斷點 D 處理。使用者在 Worker 分頁打字不會清掉 `tower`；答覆、取消、過期或分頁結束才會。

**為什麼 `blockedReason` 要到 BAT `0.7.0-pre.5` 才準。** claude 對 AskUserQuestion 也會送出權限請求，BAT `0.7.0-pre.4` 因此把原因報成 `permission`，
滑鼠回答後也要等到該回合結束才清除（BAT BUG-150）。`0.7.0-pre.5` 起提問一律回報 `question`，用滑鼠或鍵盤回答後立即清除。
CT 的做法不因版本而變：原因照原值顯示、措辭中性、不據此斷定「是權限還是提問」。v5.5.0 寫規則時 BUG-150 的修正還沒發版，
這樣寫讓修正前後都不必改邏輯；v5.5.1 只補上版號。

**還看不到的情況。** 權限對話框以滑鼠允許或拒絕、elicitation 以滑鼠回答或逾時關閉，`blocked` 會維持到該回合結束；
claude 設定停用 hooks（`disableAllHooks: true`，或 managed 設定的 `allowManagedHooksOnly`）時：BAT `>= 0.7.0-pre.6` 會讀 claude 的 managed 與使用者設定檔，
讀得到就回 `blockedDetection: none`，塔台照 `none` 處理（`idle` 不代表沒有在等人）；專案設定等讀不到的層級，以及 `< 0.7.0-pre.6` 的 BAT，
仍回 `hook` 但沒有事件，等於偵測不到（v5.6.0 依 BAT pre.6 更新）。hook 的原因只支援 claude-cli Worker，codex 走上面的 `input`（v5.8.0）；
codex 卡在啟動前畫面（「Trust this folder?」「Hooks need review」）時不送任何序列，所以看起來是「沒起來」而不是 `blocked`；
BAT 重開或 headless server 重啟後，之前的 `blocked` 狀態會遺失，可能漏報一次（v5.5.1 補記；codex 分頁在 BAT 重開時會由重播內容補回，v5.8.0）。

> 觸發、處理、訊息格式與已知限制以 CT 的 `yolo-mode.md` § 斷點 D 為唯一權威；MCP tool 與回傳欄位見 CT `auto-session.md` § BAT MCP 唯讀 tool；
> BAT 端契約以 BAT `docs/agent-guide/blocked-state.md` 為準（codex 的部分另以 BAT T0621「介面契約」C-1–C-8 為準）。

---

## BAT 塔台面板讀取契約（v5.13.0；v5.13.1 對齊 BAT `0.7.1-pre.9`）

BAT 視窗裡的指揮塔面板（總覽、決策、臭蟲、待辦池、工單各頁）直接讀 CT 寫的檔：`_tower-state.md`、`_decision-log.md`、
`_bug-tracker.md`、`_backlog.md`、每張工單。這是分工原則的另一個方向——前面各節是 CT 呼叫 BAT 的介面，由 BAT 定；
這裡是 BAT 讀 CT 的檔案格式，檔是 CT 寫的，所以契約寫在 CT 這邊，並註明對照的是 BAT 哪一版的解析器。

### 為什麼頁面會空

最常見的原因不是格式錯，是**檔太大**。BAT 讀這些檔共用同一個讀檔函式，上限 512 KiB（524,288 bytes），超過就整檔不讀。
BAT `0.7.1-pre.9` 以前，麻煩在於大部分頁面**不報錯**；pre.9 起改成明說讀不到（v5.13.1 把契約對齊這一版）：

| BAT 頁 | 檔超過上限時：BAT `>= 0.7.1-pre.9` | 更舊的 BAT |
|---|---|---|
| 總覽 | 顯示讀不到塔台狀態檔（File too large） | 同左 |
| 決策、臭蟲、待辦池 | 顯示「無法讀取 <檔名>」，附 KB 數與 512 KB 上限 | 不報錯，清單是空的 |
| 工單 | 那一張仍列在清單，狀態 UNKNOWN | 那一張從清單消失，不提示 |

在更舊的 BAT 上，「沒有決策」和「決策日誌太大」在畫面上長得一樣，所以**頁面空了先量檔案大小**；pre.9 起畫面會直接說是哪個檔。
檔案不存在仍顯示空（那不是錯誤），512 KiB 上限也沒變。append-only 的決策日誌是最容易長大的一個。

### 400 KB 預算：比上限早一步提醒

CT 自己訂的預算是 400 KB（409,600 bytes），比 BAT 的上限低約 100 KB。差的這段是緩衝：塔台提示之後，
到使用者真的去收斂之前，通常還會再跑幾個 session、再寫幾筆決策，不該一提示就已經讀不到。

- **量位元組，不數字元**：中文一個字在 UTF-8 是 3 bytes，用字數估會低估將近三倍。bash `stat -c %s <檔>`；PowerShell `(Get-Item <檔>).Length`
- **何時量**：塔台啟動與 `*sync` 只量大小、不為此讀內容；超過預算印一行 ⚠️，超過上限印一行 🔴，都不阻擋
- **怎麼縮**：決策日誌照 CT `decision-log-system.md` § 收斂（設計理由見 `three-layer-arch.md` § `_decision-log.md`）；
  BUG／PLAN 索引靠 `*archive` 把終態單據移出熱區，下次 `*sync` 重建就變小；單張工單把長篇證據移到另一個檔、工單裡留連結。
  塔台不自動收斂——搬什麼、何時搬由使用者決定

**BAT 會報錯了，預算為什麼還留著（v5.13.1）**：兩個理由。第一，塔台不知道使用者裝的是哪一版 BAT，更舊的 BAT 超過上限仍會靜默變空，
提示不能只靠 BAT 那邊。第二，pre.9 的「無法讀取」只是讓問題**看得見**，那一頁照樣沒有內容；400 KB 預算的用處是在走到那一步之前先提醒。
所以檢查時機與輸出不分 BAT 版本照做，數字也沒動。

### 格式：人看起來一樣，解析器不一樣

契約其餘部分是各檔 BAT 依賴的寫法。共同的道理是：BAT 逐列讀 Markdown 表格，一行不是以 `|` 開頭又以 `|` 結尾，表格就在那裡結束；
格子裡的 `|` 會讓欄位錯位。嚴重度與優先級只認含 `High`／`Medium`／`Low` 的字串，只寫 🔴 的格子在 BAT 是 Unknown；`critical` 在 BAT `>= 0.7.1-pre.9` 的任何讀取路徑都算 High，更舊的 BAT 只在讀封存單據的 frontmatter 時這樣做。
`_tower-state.md` 則靠開頭的機器可讀摘要（見 `three-layer-arch.md` § Tower State）。這些寫法對人幾乎沒差，對面板是讀得到與讀不到的差別。

契約也規定 CT **不為了面板改單據的值**：BUG 狀態不新增值（CT 與 BAT 的 BUG 狀態一對一相同），單據 frontmatter 照舊可以寫 `critical`，
只有索引格子寫成 `🔴 High（critical）`。面板要多顯示什麼，是寫法的事，不是改資料的事。

> 大小預算、各頁表現、各檔 BAT 依賴的格式與值域對照，以 CT `memory-protocol.md` § BAT 塔台面板讀取契約 為唯一權威（對照 BAT `0.7.1-pre.9`：解析器仍以 pre.8 對照，pre.9 改的讀檔失敗提示與 `critical` 讀法依 BAT 通知）；
> 各檔的完整格式在該節列出的權威段。BAT 改了解析規則，以 BAT 的通知為準再改 CT。

---

## 版本對照表

CT 從不預先判斷 BAT 版本：一律先照常呼叫，失敗才依 exit code 降級（`runtime-dispatch.md` § 降級鏈）。
所以下表不是「要先確認的條件」，而是「舊 BAT 上會看到什麼」：

| CT 版本 | 功能 | 需要的 BAT | 舊 BAT 上的行為 |
|--------|------|-----------|---------------|
| v5.0.6 | 帶前綴的工單 ID 走結構化派工（`--workorder CP-T0113`） | `v0.5.9-pre.1`（BAT 的 fork 版） | 單次降級為 `--prompt` 派工，並**明示**「已降級」與原因 |
| v5.1.0 | 收單後回收 Worker 分頁（`--close-worker`） | `>= 0.6.1-pre.4`（pre.3 已有這個指令，但分頁剛有輸出會回 exit `6` BUSY、延遲期間有輸出就取消；等安靜自 pre.4 起；v5.12.3 更正） | exit `1`：一行警告，照常收單；`worker_auto_close` 預設 `off` 不受影響 |
| v5.2.0 | 塔台分頁角色宣告（`--set-role tower`） | `>= 0.6.1-pre.6` | exit `1`：面板記「不支援（BAT 太舊）」，塔台照常啟動 |
| v5.2.4 | 每分頁範圍權杖、分頁角色權限 | `>= 0.7.0-pre.1` | 沒有角色限制，行為與 v5.2.3 相同 |
| v5.3.0 | worktree 隔離派工（`--isolation worktree`、`CT_*` 變數） | `>= 0.7.0-pre.2` | 隔離工單 exit `1`：**停下等使用者**，不自動改非隔離；非隔離工單不受影響 |
| v5.3.0 | 隔離工單回收（`--worktree keep`／`remove`）、`--worktree-status` | `>= 0.7.0-pre.2` | `--worktree-status` 失敗 → 改用 git 算合併判準 |
| v5.3.0 | BAT MCP 唯讀 tool | `>= 0.7.0-pre.2` | 沒有這組 tool → 直接走 helper／檔案 |
| v5.4.0 | 隔離 Worker 分頁回收後仍可查 `--worktree-status`（回傳帶 `source`） | `>= 0.7.0-pre.4` | 成功回傳沒有 `source` → 照舊在回收分頁之前查；回收後查不到（exit `3`）→ 改用 git |
| v5.5.0 | yolo 提問通道（`T#### 提問`、工單往返） | 無新門檻（只用工單檔與 `bat-notify.mjs`） | — |
| v5.5.0 | 斷點 D（MCP 查到 Worker `blocked`） | `>= 0.7.0-pre.4` | 回傳沒有 `blockedDetection` 或 MCP 不可用 → 斷點 D 不啟用，流程照常 |
| v5.5.1 | `blockedReason` 準確（AskUserQuestion 回報 `question`、回答後立即清除） | `>= 0.7.0-pre.5` | `0.7.0-pre.4` 把提問報成 `permission`；CT 照原值顯示、措辭中性，邏輯相同 |
| v5.6.0 | Worker 啟動確認（`--wait-started`、exit `8`、MCP `agentStarted`） | `>= 0.7.0-pre.6` | exit `1` + `Unknown option '--wait-started'`（不建分頁）→ 去掉參數重派一次，本 session 不再帶，之後同 v5.5.1 |
| v5.6.0 | 斷點 D：claude 設定的 `disableAllHooks` → `blockedDetection: none` | `>= 0.7.0-pre.6` | 仍回 `hook` 但沒有事件（偵測不到）；斷點 D 邏輯相同 |
| v5.7.0 | yolo 提問走 BAT 結構化通道（`--ask`、`bat_wait_question`、`bat_list_questions`、`--answer`、`blockedReason: tower`） | `>= 0.7.0-pre.7` | `--ask` 失敗、tool 不存在或沒有 `pendingQuestions` → 回到工單檔往返，行為同 v5.6.1 |
| v5.8.0 | codex 分頁的 OSC 7501：斷點 D 接受 `input`、codex 的 `--wait-started`／`agentStarted`（另需 codex `>= 0.163.0`） | `>= 0.7.0-pre.9` | 舊 BAT（≤ `0.7.0-pre.8`）或較舊 codex → `blockedDetection: none`、`agentStarted: null`、`started: unknown`，行為同 v5.7.2 |
| v5.8.1 | v5.8.0 的 BAT 版本占位字串換成確切版號；yolo 提問「提問時間」取自系統、自檢不改已送出題目、塔台答覆行由 Worker commit 帶入（皆不涉 BAT 介面） | 無新門檻（v5.8.0 功能仍需 `>= 0.7.0-pre.9`） | — |
| v5.9.0 | 跨 session 選收件人（ListAgents `<工作區> · Tower` → `bat_list_terminals scope=towers` → 請使用者轉交）、MCP `claudeSessionName`／`claudeSessionId`、塔台面板 session 名稱提示 | `>= 0.7.1-pre.1` | ListAgents 沒有這些名稱、MCP 沒有這兩個鍵、`scope: towers` 回 `INVALID_ARGS` → 回覆稿請使用者轉交、面板不提示，行為同 v5.8.1 |
| v5.12.0 | 重派前回收舊 Worker 分頁（沿用 `--close-worker`，`--delay-ms 0`） | 無新門檻（與 v5.1.0 相同，`>= 0.6.1-pre.4`） | exit `1`：一行提示，照常派工，本 session 之後不再嘗試（收單回收也是） |
| v5.12.1 | `worker_close_delay` 的取消條件說明對齊 BAT T0545（延遲期間輸出不取消、只有使用者輸入取消、到期後等安靜 5 秒、最多再等 60 秒；不涉 BAT 介面） | 無新門檻 | — |
| v5.12.2 | 收單回收 exit `0` 的提示改成「Worker 分頁約 N 秒後回收」：到期時仍在輸出就等安靜、最多再等 60 秒，仍在輸出就放棄、保留分頁，塔台不會得知，所以不寫成確定時間（不涉 BAT 介面） | 無新門檻 | — |
| v5.12.3 | 文件更正：`--close-worker` 的最低 BAT 改成 `>= 0.6.1-pre.4`（上方 v5.1.0、v5.12.0 兩列；BAT 介面與 CT 行為不變），另收斂幾處文件說法不一 | 無新門檻 | — |
| v5.12.4 | 退役 `control-tower/references/ct-exec.md`（Worker 規則只看 `ct-exec/SKILL.md`）、YOLO 連續 FAILED 計數器位置統一為 `_tower-state.md` 的 `## YOLO 歷程` › `### 計數器`、發行打包調整（不涉 BAT 介面） | 無新門檻 | — |
| v5.12.5 | 退役 `control-tower/references/` 其餘三份 Worker 命令長版說明（`ct-done`、`ct-status`、`ct-evolve`；仍有效的規則補進各自 `SKILL.md` 與 `self-learning-core.md`）、`ct-status` 的 `INTERRUPTED` 歸 Needs Tower judgment（不涉 BAT 介面） | 無新門檻 | — |
| v5.12.6 | 發行內容去識別：範例與由來說明裡可識別的名稱換成中性說法或範例值（只改說明文字，規則與行為不變；不涉 BAT 介面） | 無新門檻 | — |
| v5.12.7 | 環境偵測改成只列變數名稱、不輸出值（BUG-001；`BAT_REMOTE_TOKEN` 只記「已設定」，判讀邏輯不變；不涉 BAT 介面） | 無新門檻 | — |
| v5.12.8 | BMAD 路由與工單規則的 BMad 舊名改成現行名稱、修正「`bmad-create-story` 內建 Review」說法（BUG-002；不涉 BAT 介面） | 無新門檻 | — |
| v5.13.0 | BAT 塔台面板讀取契約（熱檔預算 400 KB、BAT 讀檔上限 512 KiB、各檔 BAT 依賴的格式）、`_tower-state.md` 機器可讀摘要 v1；另有 BUG／工單狀態衛生與 3 個新設定（不涉 BAT 介面） | 無新門檻（格式對照 BAT `0.7.1-pre.8` 的解析器） | — |
| v5.13.1 | Worker 通知與提問用完整工單 ID（`--source` 含前綴，BAT 才對得到 Worker 分頁、標得了 Done）；面板讀取契約改寫成 BAT `0.7.1-pre.9` 的表現（讀不到時顯示「無法讀取」、`critical` 在任何讀取路徑都算 High；400 KB 預算保留） | 無新門檻（BAT 介面不變；「無法讀取」提示與 `critical` 讀法是 BAT `>= 0.7.1-pre.9` 的行為） | 更舊的 BAT：面板讀不到時照舊靜默變空、只寫 `critical` 的索引格子是 Unknown；CT 的寫法與預算不分版本照做 |
| v5.14.0 | plugin marketplace 安裝方式（plugin `ct`、`ct-guide`）；BAT 對 Codex 送 `$ct-exec`，plugin 版在 Codex 只能用 `$ct:ct-exec` 叫，所以 Codex 搭配 BAT 派工用 zip 手動安裝（不涉 BAT 介面） | 無新門檻 | 與 BAT 版本無關：只裝 plugin 的 Codex Worker 叫不到 CT skill；Claude Code 不受影響 |

`BAT_HELPER_NODE`（v5.2.1）沒有版本門檻：本機沒有這個變數就用 `node`，只有遠端分頁會由 BAT 注入。
版號以 CT 的 `version-governance.md` § 歷史版號表 與 `auto-session.md` § 依賴的 BAT 基礎設施 為準；v5.1.0 的 BAT 版本出自 CT `CHANGELOG.md` [5.12.3]：[5.1.0] 原寫 `0.6.1-pre.3`，v5.12.3 依 BAT 塔台回覆更正為 `>= 0.6.1-pre.4`（歷史段落不改）。
