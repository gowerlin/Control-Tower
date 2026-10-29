---
title: 一張工單的一生
description: 從對齊需求、開單、派發前檢查、派工、Worker 執行與反序收尾，到塔台收單、狀態機與決策日誌，一張工單會經過哪些步驟、每一步留下哪個檔案。
---

<script setup>
const dispatchRows = [
  ['off', '顯示要在新 session 執行的指令（例如 /ct-exec T0042）', '自己開 session、貼指令；做完把「T0042 完成」帶回塔台'],
  ['ask（預設）', '每次先問：開新分頁執行、複製到剪貼簿，還是你自己來', '逐張選擇'],
  ['on', '直接開 Worker 分頁並預載指令；開不了就降級', 'Worker 把回報預填到塔台輸入列，你看一眼再送出'],
  ['yolo', '同 on，並把模式 yolo 傳給 Worker', 'Worker 自動送出回報，塔台自己決定下一張；遇到斷點才停下等你']
]
const reportRows = [
  ['DONE、FIXED', 'T0042 完成'],
  ['PARTIAL', 'T0042 部分完成'],
  ['BLOCKED、FAILED', 'T0042 需要協助'],
  ['仍是 IN_PROGRESS，有問題等塔台答覆（只在 yolo）', 'T0042 提問']
]
const bucketRows = [
  ['還在流程中', 'PENDING、IN_PROGRESS、PAUSED、URGENT', '照常推進'],
  ['需要塔台判斷', '未解決的 PARTIAL、BLOCKED、FAILED，已有接續工單或重派的 INTERRUPTED，以及無法辨識的 UNKNOWN', '塔台決定 Renew、拆單、改策略或問你；INTERRUPTED 在確認接續工單接手後結掉'],
  ['已結束', 'DONE、FIXED（驗證政策允許後）、CLOSED、WONTFIX、DROPPED、CONCLUDED、ABANDONED', '可以歸檔']
]
</script>

# 一張工單的一生

一張工單從你說「我想要……」開始，到塔台把決定寫進日誌結束。這一頁照順序走一遍：每一步誰在做、你要做什麼、留下哪個檔案。 {.ct-lead}

<TicketLife />

BAT 站也有一段從執行環境角度看的同一個流程，附短片：<BatLink path="control-tower#lifecycle">BAT 站：一張工單的一生</BatLink>。

## 1. 對齊需求，然後開單 {#align}

你不用一次把需求說清楚。塔台會先**複述目標、找出還不知道的事**，再用有範圍的選項式問題問你，你可以回答「不確定」。範圍具體到可以執行了，塔台才開單。最少問幾輪由 `alignment-rounds` 控制（預設 3，`0` = 不強制提問）。

開出來的工單是 `_ct-workorders/T####-<簡述>.md`，最上方是 YAML frontmatter（給機器讀的事實來源），下面是給人看的元資料表、任務指令與回報區。一張工單應該是**一個交付物**，可以中斷、可以接著做。工單裡會寫清楚：

- **目標與範圍**，以及明確的**不准碰的東西**
- **`affects_files`**：這張工單會動到哪些檔案（派工前的重疊檢查靠它）
- **驗收條件**：怎樣才算完成，要附什麼證據
- **收尾要求**：要不要 commit、回報區要填什麼

狀態是 `PENDING`。

## 2. 派發前檢查 {#pre-dispatch}

派工前塔台做兩件事：

1. **查學習紀錄**（安靜進行）：讀 `_learnings.md`，看有沒有符合這次情境的經驗；有相符的 Playbook 會建議套用。
2. **檔案重疊檢查**：比對這張工單的 `affects_files` 和目前所有 `IN_PROGRESS` 工單的 `affects_files`。

| 判定 | 什麼情況 | 塔台怎麼做 |
|---|---|---|
| 🚨 BLOCK | 和進行中的工單有完全相同的檔案路徑 | 列出衝突，要你輸入「確認接受衝突」才繼續，否則取消派工 |
| ⚠️ WARN | 任一方用萬用字元 `*`、沒有宣告 `affects_files`，或同目錄不同檔 | 提醒，問你要不要繼續 |
| ✅ PASS | 沒有交集 | 正常派工 |

這是**靜態比對**：只比工單上宣告的路徑，不追蹤 Worker 執行時實際動了哪些檔案。所以 `affects_files` 寫得越準，檢查越有用。需要真的平行改同一區時，工單可以要求在獨立的 git worktree 裡做（見 [worktree 隔離與合併](/deep/features/worktree-merge)）。

## 3. 派工 {#dispatch}

派工的方式由 `*config auto-session` 決定：

<CardTable caption="auto-session 的四種模式" :columns="['模式', '塔台怎麼派', '你要做什麼']" :rows="dispatchRows" />

`on` 與 `yolo` 會依環境往下降級，降級過程不打擾你：

1. **BAT 內部終端**（在 BAT 裡時）：BAT 在同一個工作區開 Worker 分頁，帶上這張工單與模式。
2. **開新終端分頁**（不在 BAT 裡，且認得你的終端）。
3. **寫入剪貼簿**。
4. **文字提示**：一行 `/ct-exec T0042`，**永遠顯示**，即使前面成功開了分頁。

塔台不會把模式寫進設定檔讓 Worker 去讀，而是在派工時用環境變數 `CT_MODE` 傳給 Worker。Worker 因此是無狀態的：同一張工單、同一組參數，在哪裡跑都一樣。

## 4. Worker 執行 {#worker}

Worker 是一個全新的 session，輸入 `/ct-exec T0042`（Codex：`$ct-exec T0042`）開工。它只帶這一張工單的脈絡，依序做這幾件事：

1. **讀工單與專案規則**：先讀 `AGENTS.md`、本地規則與 `CLAUDE.md` 這類專案指引，再讀完整張工單，並記下系統時間。
2. **落點檢查**：在**任何寫入之前**確認自己在對的 repo。工單的 `repo` 欄位和目前 repo 根目錄的名稱不同就**停下來**，不猜、不改欄位讓檢查通過。這一步存在，是因為「路徑存在」證明不了「這是對的 repo」（見[落點檢查](/deep/features/landing-check)）。
3. **開工**：把 `status` 改成 `IN_PROGRESS`，寫入 `started_at`。如果原本就是 `IN_PROGRESS`，保留原本的開工紀錄，記成接續執行。
4. **執行**：只在 `affects_files`、執行步驟與排除事項的範圍內動手，不碰和工單無關的未提交變更。做到一半發現需要擴大範圍時，停下來問（yolo 下改問塔台），不自己擴大。
5. **驗證**：跑工單寫的驗收。跑不了的要寫出確切原因，不能暗示通過。證據分道記錄：原始碼與文件、建置與測試、實際執行、部署、發行包、外部驗收各寫各的，每一道各自標 `PASS`、`PARTIAL`、`BLOCKED` 或 `FAILED`。

### 反序收尾：先寫報告，再改狀態 {#closeout}

收尾的順序是刻意倒過來的：

1. 需要 commit 時，**先 commit 產品改動**，好讓報告能寫上 commit。
2. **填回報區**：結果摘要、改了哪些檔、驗收證據、commit、偏差、阻礙與後續建議。
3. **最後才改狀態**（`DONE`、`PARTIAL`……）與完成時間，並自我檢查回報區沒有留下範本字樣。
4. **commit 工單檔本身**。
5. **通知塔台**。

為什麼要倒過來？塔台或其他工具可能在監看工單的狀態。如果先改狀態再寫報告，外面就可能讀到一張「狀態是 `DONE`、回報區卻是空的」工單。反序寫入保證：**任何人看到 `DONE` 的那一刻，報告已經完整、而且已經 commit**。

通知塔台的訊息是固定的一行，不是一段說明：

<CardTable caption="回報字串" :columns="['工單狀態', '送回塔台的字串']" :rows="reportRows" />

細節都在工單的回報區裡，回到塔台的只是一行指標，讓塔台自己去讀檔。不要把 200 行錯誤 log 貼進塔台，那會污染塔台的 context。

## 5. 塔台收單與獨立複驗 {#review}

收到「T0042 完成」，塔台不會直接採信：

1. **讀回報區與 metadata**。
2. **核對**：狀態、commit、變更的檔案、每一項驗收條件的證據、寫出來的阻礙。來源與測試的證據，和實際執行、部署、發行、客戶確認的證據分開看，不把「測試綠了」讀成「已經上線」。需要時，塔台會自己再跑一次檢查，或開一張審查工單。
3. **同步進度**：更新塔台狀態，有 `sprint-status.yaml` 時一起同步；審查類工單回報了嚴重問題，就強制開修正工單。
4. **決定下一步**：
   - `DONE`：派下一張，或宣布這一段完成。
   - `PARTIAL`：先看卡住的那一項還在不在；塔台一決定剩下的部分怎麼處理（拆接手單，或判定不需再做），當下就補一段收尾補記、改成 `DONE`；只有在等外部條件時才繼續掛著。
   - `BLOCKED`：記下卡點，看有沒有其他可以並行的工單。
   - `FAILED`：換個角度，啟動除錯策略。

需要再派同一張工單時，塔台在工單裡加一段「塔台補充（Renew #N）」再重派；在 BAT 裡，重派前會先回收舊的 Worker 分頁。

## 6. 狀態機 {#states}

<TicketStates />

- **沒有「待審」狀態**。驗收是塔台讀回報時做的事，不是工單停著等人的一個狀態；需要獨立審查就另開一張工單。
- **`PARTIAL` 是時間點上的狀態**。塔台一裁示剩下的部分怎麼處理，就當下補正為 `DONE`（v5.13.0 起，不等到歸檔），不要讓它永遠掛在「進行中」的追蹤裡。
- 其他狀態：`*pause` 會把工單標成 `PAUSED`，`*resume` 恢復；session 中斷、塔台決定改派或開接續工單時，原工單標成 `INTERRUPTED`；中斷協議產生的緊急工單是 `URGENT`，不經過 `PENDING`。

`ct-status` 與塔台把狀態分成三桶，回答「這張工單現在需要誰」：

<CardTable caption="狀態分桶" :columns="['桶', '狀態', '接下來']" :rows="bucketRows" />

一張工單裡，**frontmatter 是事實來源**，body 的元資料表只是給人看的鏡像；兩者不一致時以 frontmatter 為準，並把不一致報出來。跨來源時，**工單檔 > `sprint-status.yaml` > 塔台記憶**。

## 7. 記下來：決策日誌與學習紀錄 {#record}

收單之後，塔台把這次的決定寫進 `_ct-workorders/_decision-log.md`（倒序、只追加），把值得記住的做法安靜地追加到 `_learnings.md`。下一張工單派發前，第 2 步會再讀到這些經驗。

學到的東西不會一次就變成規則：它從「觀察到一次」開始，被反覆驗證才升級，最後可能長成一份 Playbook。這個過程見[會學習的系統](/deep/principles/learning)。

## 中斷了怎麼辦 {#interrupted}

- **Worker session 被關掉、工作其實做完了，只是沒收好尾**：在新的 session 跑 `/ct-done T0042`，它一樣先做落點檢查，再補完回報與收尾。
- **工作還沒做完**：塔台看回報區。有部分結果就開一張接續工單；空的就重派原工單，或換個策略開新工單。原工單標成 `INTERRUPTED`。
- **塔台 session 斷了**：重新輸入 `/control-tower`，塔台會讀 `_tower-state.md` 從上次的地方接著走。

細節見[中斷、Renew 與補救收尾](/deep/features/recovery)。

## 延伸閱讀 {#further}

- CT Guide `references/work-order-lifecycle.md` § 核心迴圈、§ 狀態機、§ ct-exec 的執行流程、§ 回報規範、§ 需求對齊協議、§ Session 中斷善後
- `control-tower/references/work-order-system.md` § 派發流程、§ 派發前 overlap check（v4.4.0+）、§ 回報處理流程、§ 中斷復原
- `ct-exec/SKILL.md` § Landing Zone Check、§ Phase 1: Start ～ § Phase 4: Report And Commit、§ BAT Notify And Fallback
- `control-tower/references/doctrine.md` § 工單狀態機的設計依據
- `control-tower/references/auto-session.md` § 派發後行為（依 `auto-session` 設定）、§ 降級鏈、§ Mode 與互動旗標協定（v4.3.0+）
- CT 安裝與使用指南 § 6. 基本操作流程

Portal 是摘要，不具權威；與 reference 有出入時，以 reference 為準。
