---
title: yolo 與斷點 A–E
description: yolo 是 on 的超集：Worker 自動送出、塔台照拆單表自主派下一張，五種斷點在機器無法擔保時把判斷權交還給你。
---

# yolo 與斷點 A–E

<p class="ct-lead">一句話：yolo 讓一個已經拆好單的 PLAN 自己跑完，但塔台只照拆單表機械式地往前走；資訊不足、結果不符預期、範圍要擴大或要推進 main 時，五種斷點會把判斷權交還給你。</p>

## yolo 是 `on` 的超集 {#superset}

`auto-session` 的四種模式裡（見 [派工](./dispatch#modes)），`yolo` 在 `on` 之上多做三件事：

1. **Worker 自動送出**：收尾時 `bat-notify.mjs` 帶 `--submit`，完成訊息直接送進塔台，不用你按 Enter。
2. **塔台自主派下一張**：依當前 PLAN 的拆單表決定下一張，不等你指示。
3. **斷點安全閘**：A、B、C 三個斷點從一開始就有；v5.3.0 加上合併前確認 E，v5.5.0 加上 Worker 等待使用者 D。

v5.5.0 起還有第四件事：yolo Worker 有問題時不問你，改問塔台、由塔台代決（見 [Worker 向塔台提問](./worker-questions)）。所以 yolo 派工一律帶 `--no-interactive`；想讓 Worker 直接問你，就改用非 yolo 模式。

yolo 拿掉了最後一個人工確認點。這不是「越自動越好」，而是把人的判斷集中到真正需要的地方。啟用期間，塔台狀態面板下方會一直顯示 `⚠️ YOLO MODE ACTIVE` 警語，列出五種斷點和關閉方式（`*config auto-session on`）；Worker 啟動時也會顯示醒目的 YOLO banner。

## BAT 環境變數的分工 {#bat-env}

yolo 依賴 BAT 把派工與回報接起來，而兩個方向需要的環境變數不同。塔台派工要 `BAT_SESSION=1`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`、`BAT_TERMINAL_ID`、`BAT_WORKSPACE_ID`；Worker 通知要 `BAT_TOWER_TERMINAL_ID`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`。`BAT_TOWER_TERMINAL_ID` 不是塔台本來就有的值，而是塔台派工時把自己的 `BAT_TERMINAL_ID` 交給 `--notify-id`，再由 BAT 注入 Worker。拆成兩組的理由是讓每一方只檢查自己那個方向的變數，否則塔台會因為缺 `BAT_TOWER_TERMINAL_ID` 而誤判不在 BAT 裡。

## 下一張怎麼判定：只照拆單表 {#next}

塔台收到 `T#### 完成` 之後，不靠推理決定下一張，而是走一條機械化的路徑：

1. 讀完成工單的元資料，找出它關聯的 PLAN 與研究工單。
2. 在研究工單回報區找拆單建議段落（例如「拆單建議摘要」「D. 拆單建議」），取第一個格式相符的表格。
3. 表格必須有 `#`、`標題`、`依賴` 三欄。
4. 由上往下找第一列「依賴都已完成、還沒派過」的工單；它有具體的 `T####` 就派，只是佔位符就停。
5. 所有列都完成，就顯示「PLAN 完成」並結束 yolo，問你要不要結案 PLAN。

任何一步資訊不足，例如找不到研究工單、沒有拆單段落、表格格式不符、下一列只是佔位符，塔台都**不猜**，直接觸發斷點 A 停下來。派下一張之前，塔台會先顯示 `🤖 YOLO: T0xxx DONE → 自動派發下一張 T0xxy` 面板，列出依據、斷點計數和模式，並強制等一到兩秒，給你按 Ctrl+C 或 `*pause` 的機會。

## 五種斷點 {#breakpoints}

斷點是「機器無法擔保下一步」的時機。觸發時塔台暫停並給你選項（斷點 D 例外，只告知、不暫停）。下圖標出每個斷點落在流程的哪一步：

<BreakpointMap />

### A：Worker 回報非預期 {#a}

Worker 的收尾訊息必須精準符合固定格式：工單 ID 後接 `完成`、`部分完成`、`需要協助` 或 `提問`（容錯另收 `失敗`）。工單 ID 的部分引用工單編號的唯一權威定義，所以 `CP-T0113 完成` 這種帶前綴的回報同樣合法。不符合就是斷點 A：塔台無法確定 Worker 的真實狀態，可能是 Worker 版本太舊，也可能是措辭出格。你可以選擇接受為 DONE 續派、接受為 FAILED（計入斷點 B），或退回 ask 手動接手。

漏了前綴的回報也不是斷點 A（v5.13.1 起）：收到 `T0113 完成`、熱區只有 `CP-T0113` 時，格式仍然合法，塔台把它當成那一張收單，並記一行「回報 ID 缺前綴」；同號的工單有好幾張，或根本找不到，塔台才不猜、停在斷點 A。這個容錯只保住塔台這一側，BAT 要把 Worker 分頁標成 Done，仍要 Worker 送出完整 ID，所以 Worker 送出前也會先和工單的 `id` 比對。

`T#### 提問` 不是收尾訊息，工單還在執行，塔台不收單，改去讀題答覆。

### B：Renew 太多或連續失敗 {#b}

N 是設定值 `yolo_max_retries`（預設 `3`，設 `0` 停用斷點 B）。

- **B-1 Renew 過多**：被回報工單的 Renew 次數達到 N。同一張單反覆迭代，代表方向需要重新對齊，建議拆新工單。
- **B-2 連續失敗**：塔台 session 層級的計數，跨工單累計。Worker 回報 `FAILED` 或 `BLOCKED` 時計數加一，`DONE`、`FIXED`、`PARTIAL` 歸零，達到 N 就暫停。計數器的格式見 `yolo-mode.md` § YOLO 計數器。可能是 PLAN 或研究結論本身有問題，繼續派只會累積失敗。

### C：跨出 PLAN 範圍 {#c}

Worker 的回報裡建議「另開工單」「建議派研究」，或提到不在當前拆單表裡的工單、PLAN、BUG、EXP 編號，就是斷點 C。擴大範圍是人的決定，不是塔台可以自主做的。選項是擴大當前 PLAN、開新 PLAN，或忽略建議照原表繼續。

### D：Worker 在等使用者 {#d}

斷點 D 是唯一不暫停的斷點。塔台只在本來就在看某個 Worker 時（你問進度、等回報等到要判斷是否卡住、Renew 或重派前）順手查 BAT 回報的分頁狀態。看到分頁 `blocked`、原因是等使用者的那幾種（claude Worker 的權限確認、提問、MCP 表單，或 codex Worker 的 `input`），就用分頁標題告訴你「在等你回答」，請你自己去處理。

在 yolo 下這是**異常偵測**：yolo Worker 本該問塔台，停在等使用者代表它誤用了提問工具，或遇到權限提示。塔台不代答、不送按鍵、不另開輪詢，也不暫停其他工單；`blocked` 不算失敗，不計入斷點 B。原因是 `tower` 時代表 Worker 在等塔台答題，那不是斷點 D，塔台直接讀題答覆。這個斷點需要 BAT MCP 可用，BAT 太舊時不啟用。

### E：合併前確認 {#e}

塔台要以 `git merge --ff-only` 把隔離工單的合併結果推進 `main` 之前，就是斷點 E。它和其他斷點不同，**不只在 yolo 下生效**：非 yolo 模式下每次 ff 前一律暫停。yolo 下依合併模式決定：機械合併在 ff 前再確認判準仍成立就自動通過；衝突解決要驗收全綠而且沒有範圍外檔案才自動通過；等價移植一律暫停。收單時的 SHA 比對任一步不成立，不論模式都直接暫停。

理由是「推進 `main`」的回頭成本比「派下一張工單」高得多。`--ff-only` 被 git 拒絕（主 checkout 有重疊的未提交變更）是正常保護，不是失敗。合併流程見 [worktree 隔離與三種合併模式](./worktree-merge)。

## 使用者中斷不是斷點 {#interrupt}

yolo 期間，你隨時在塔台輸入獨立的 `停`、`stop` 或 `abort`，塔台就暫停，並告訴你擱置了什麼動作、命令還沒送出。這**不是斷點**：它獨立計數，不影響 yolo 的健康判定，也不佔用 `yolo_max_retries` 的額度。分開的理由很簡單：你叫停通常只是「我想看一下」，不代表流程出問題。如果算成斷點，每次喊停都會把 yolo 推向「不健康」，最後反而不敢喊停。

## 計數器與 YOLO 歷程 {#history}

yolo 啟用後，塔台在 `_tower-state.md` 加一個 `## YOLO 歷程` 區段，記下每一次啟動、派發、完成、斷點、提問、使用者中斷與恢復，以及計數器：連續失敗（`FAILED`／`BLOCKED`）次數、本 session 派發張數、各斷點觸發次數、提問數。yolo 關閉時，當前 session 的紀錄濃縮成一行摘要移到歷史區。這個區段只在曾經啟用 yolo 時存在，非 yolo 專案缺少它不算區段缺失。

收單後回收 Worker 分頁也照常進行，但回收結果不影響任何斷點判斷，也不計入斷點 B。

## 你會看到的訊息 {#messages}

| 情境 | 訊息開頭 |
|---|---|
| 啟用中 | `⚠️ YOLO MODE ACTIVE` |
| 派下一張之前 | `🤖 YOLO: T0xxx DONE → 自動派發下一張 T0xxy` |
| 斷點 A／B-1／B-2／C | `⏸ YOLO PAUSED — 斷點 A 觸發`（其餘同格式） |
| 斷點 D | `⚠️ YOLO 斷點 D（不暫停）— <分頁標題> 在等你回答` |
| 斷點 E | `⏸ YOLO PAUSED — 斷點 E（合併前確認）`；非 yolo 為 `⏸ 合併前確認` |
| 提問需要你決定 | `⏸ YOLO PAUSED — 提問需要你決定` |
| 使用者中斷 | `🛑 YOLO PAUSED — 使用者中斷` |
| PLAN 完成 | `✅ PLAN-0XX 所有工單完成 → yolo 流程結束` |

BAT 這一端怎麼呈現自主程度與「一定會停下來問你的時候」，見 <BatLink path="control-tower#autonomy">BAT 站：自主程度與斷點</BatLink>。

::: tip 命令範例
本頁的訊息格式、比對規則與命令都是摘要，完整參數以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `control-tower/references/yolo-mode.md` § BAT env 分工、§ 下一張工單判定邏輯、§ 斷點判準（A / B / C / D / E）（含 § 斷點 B：Renew ≥N 或連續 N FAILED › B-2：連續 N FAILED › YOLO 計數器）、§ 使用者中斷（非斷點）、§ `_tower-state.md` 新增 `## YOLO 歷程` 區段、§ 使用者可見訊息（規格化彙整）
- `control-tower/references/auto-session.md` § 派發後行為（依 `auto-session` 設定）› `auto-session = yolo`
- `control-tower/references/tower-config.md` § 可用選項（`yolo_max_retries`）
- `control-tower-guide/references/runtime-dispatch.md` § YOLO 與斷點：自主推進的邊界

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
