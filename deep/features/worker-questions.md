---
title: Worker 向塔台提問
description: yolo 下 Worker 不問你，改把題目寫進工單問塔台；BAT 結構化通道和工單通道擇一，等不到答覆就退回 BLOCKED，由塔台在 Renew 區段答覆後重派。
---

# Worker 向塔台提問

<p class="ct-lead">一句話：yolo 下沒有人在 Worker 分頁旁邊，所以 Worker 的問題改寄給塔台。題目一律先寫進工單並 commit，再從 BAT 通道或工單通道擇一送出；塔台在範圍內代決，範圍外的事轉問你，等不到答覆就退回 BLOCKED 交給 Renew。</p>

## 為什麼要改問塔台 {#why}

yolo 的前提是「人不在旁邊」：Worker 自動送出、塔台自主派下一張。這時 Worker 若用 AskUserQuestion 這類工具問使用者，整條流程就停在一個沒人看的分頁上。v5.5.0 的做法是把問題的收件人從使用者換成塔台：塔台本來就在讀工單檔，也握有決策日誌與 PLAN 的全局視角。

這條規則只適用 `CT_MODE=yolo` 的 `ct-exec` Worker。非 yolo（`on`、`ask`、`off`，或 `CT_MODE` 缺值而降級為 `ask`）完全不適用，研究型工單照常向使用者提問。反過來說，yolo Worker **不得**使用任何向使用者提問的工具，研究型工單、`CT_INTERACTIVE=1` 也一樣；違規時塔台可能經 [斷點 D](./yolo#d) 發現。

<QuestionFlow />

## 什麼值得問 {#what-to-ask}

只問一種事：**工單範圍內、自己定不了、猜錯會返工**的選擇。

- 能依工單、決策日誌或專案慣例（`CLAUDE.md`、`AGENTS.md`、FIELDGUIDE 等）自己決定的，不問：自己決定，在回報區寫下理由。
- 範圍外的事能記成候選、收尾時回報的，就記下來；非得現在決定要不要擴大範圍才能繼續的，才用提問通道問。這屬於「範圍變更」，塔台會轉問你。Worker 不得自行擴大範圍。
- 研究型工單每一輪的題數上限是 `research_max_questions`。

## 題目寫進工單 {#write}

Worker 在工單 `## 回報區` 最上方新增 `### 待塔台決策`，每題一個 `#### Q-n`，題號在同一張工單內遞增、不重用：

```markdown
### 待塔台決策

#### Q-1：<一句話問題>
- 提問時間：<取自系統時間的輸出>
- 選項：[A] … / [B] … / [C] 其他：________
- Worker 建議：[A]，因為 …
- 影響範圍：<哪些檔案／步驟／驗收條件>
- 阻塞：是（Step N 起要等答覆）/ 否（先做不受影響的步驟）
```

接著有兩個必要步驟，順序不能顛倒：

1. frontmatter 加 `tower_question: open`，表示這張工單有待答問題。不論接下來是原地等，還是設定成不等、直接走備援，都要先加。
2. **先 commit，後通知**。工單（含題目與 `tower_question: open`）要先 commit，依政策要 commit 的產品變更也一樣，然後才通知塔台。塔台收到通知時讀到的工單，必須是已經落地的那一版。

Worker 不得預寫答覆行或任何佔位文字（例如「塔台答覆 Q-1：（待填）」），因為它正是靠答覆行出現與否來判斷答了沒有。「提問時間」也要先執行取系統時間的指令再貼上，不得自行推估或依前一筆遞推。

## 兩個通道，只能擇一 {#channels}

題目寫進工單之後，Worker 從下面兩個通道**擇一**通知塔台，同一題不重複通知：

| 通道 | 條件 | Worker 怎麼送、怎麼等 |
|---|---|---|
| **BAT 結構化通道**（v5.7.0+） | BAT `>= 0.7.0-pre.7`，且 `worker_question_timeout` 不是 `0` | 每題送一次 `bat-notify.mjs --ask`（它自己就會通知塔台 `<工單 ID> 提問`），再反覆呼叫 `bat_wait_question` 等答覆 |
| **工單通道** | 任何 BAT 版本都能用 | 送一般的 `<工單 ID> 提問` 通知，然後每 30 秒以上重讀自己的工單檔，直到每題都出現答覆行 |

兩個通道的 `<工單 ID>` 都是工單的完整 ID，等於 frontmatter 的 `id`：設了前綴就含前綴（例 `CP-T0113 提問`），不能截成 `T` 加數字；Worker 送出前會和 `id` 比對一次（v5.13.1 起）。

BAT 通道的題目只存在 BAT 主行程的記憶體裡，不寫檔、日誌也不記內容；所以題目**一律先寫進工單**（雙寫），工單的問答紀錄是唯一留下來的紀錄。這也代表 BAT 通道任何時候失效，都能退回工單通道，不會留下塔台看不到的題目。

BAT 通道有幾條必須遵守的規則：

- 題目、選項、說明與答覆文字**只走 stdin**，不得放進命令列參數。命令列會被原樣寫進 BAT 的 script 日誌，也會出現在程序列表與工具紀錄裡。
- `question` 以工單題號 `Q-n：` 開頭，內容和工單相同，塔台靠題號把兩邊對起來。
- 等待時兩次呼叫的間隔不得超過 120 秒，否則 BAT 會把這題判為沒人在等而過期。
- 不必事先判斷 BAT 版本：直接送，失敗了照降級表處理。

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-notify.mjs" --ask --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" \
  --submit --expires-min <worker_question_timeout> "<工單 ID> 提問" <<'JSON'
{"question":"Q-n：<一句話問題>","options":["<選項 A>","<選項 B>"],"detail":"Worker 建議：…","blocking":true}
JSON
```

塔台那一側，先讀工單的 `### 待塔台決策`，再用 `bat_list_questions` 對照 BAT 裡的題目狀態，決定每一題要用 BAT 答覆（`bat-terminal.mjs --answer`，答覆文字同樣只走 stdin）還是在工單裡寫答覆行。無論哪一種，**同一題只能有一個生效的答覆**。

## 多題、晚退回與備援 {#edge-cases}

**多題**：一次問好幾題時，Worker 先把所有題的 `--ask` 送完，才開始等。某題 `--ask` 失敗，就在該題最後加一行 `- **通道**：工單`，表示這題改等工單答覆；全部送完後，有任何一題加了標記，就 commit 工單，再送**一次**一般的 `<工單 ID> 提問`。這個順序保證塔台處理通知時一定看得到標記：工單裡沒有標記、BAT 列表裡也還沒有的題，一定還有後續通知，塔台可以先不答。

**晚退回**：`--ask` 成功、等到一半才失效的題（BAT 重開讓題目 `lost`，或被取消），一樣加 `通道` 標記、commit 一次、送一則一般 `提問`，剩下的時間改等工單答覆行。這是工單通道「等待期間對工單只讀不寫」的唯一例外，範圍只限標記行、一次 commit、一則通知。

**備援**：以下任一成立，Worker 就不再等：

- 等到上限 `worker_question_timeout`（預設 30 分鐘；`0` 代表不等）還有題目沒答
- BAT 通道回報題目過期
- 要走工單通道，但平台沒有可用的等待工具
- 提問通知送不出去

這時 Worker 照常完成回報區，題目與 `tower_question: open` 原樣保留，把工單收成 `BLOCKED`，commit 之後才送 `<工單 ID> 需要協助`。塔台在 `## 塔台補充（Renew #N）` 區段逐題寫答覆、把狀態改回 `PENDING`，再派一個新 Worker；在 BAT 內會先回收舊分頁，不對舊分頁送任何按鍵。走到這一步，它就是一次普通的 `BLOCKED` 與 Renew，照常計入斷點 B。

`worker_question_timeout` 是塔台的設定，只存在塔台的記憶裡，Worker 看不到。所以塔台在 yolo 派工前把生效值寫進工單 frontmatter，Worker 先讀工單、再讀專案與全域設定、最後用預設值。值是 `0` 或工單已經 `BLOCKED` 時，塔台不在題目下答，只在 Renew 區段答，避免同一題出現兩個答案。

## 答覆只認區段內的答覆行 {#answer-line}

塔台用工單通道答覆時，在該題最後新增**一行**，不改 Worker 寫的任何內容：

```markdown
- **塔台答覆 Q-n**：<決策>——<一句理由>（<時間>；塔台代決 / 使用者決定）
```

Worker 判斷「答了沒有」只認這種行：行首是 `- **塔台答覆 Q-n**`，而且位在 `### 待塔台決策` 或 `## 塔台補充（Renew #N）` 區段內；程式碼區塊裡的同樣字樣也不算。這條限制來自實機驗收：某張工單的執行步驟本身就寫著「塔台答覆 Q-1」幾個字，Worker 搜整份檔案，第一次檢查就誤判已答。工單檔就是通道，通道裡的訊號必須有一眼可辨的固定格式與位置。

`塔台答覆 Q-n` 行也是「回報區只由 Worker 填寫」的唯一例外。塔台寫完不另外 commit，Worker 之後 commit 工單時會一併帶入。

## 塔台代決的邊界 {#boundary}

| 問題的性質 | 誰決定 |
|---|---|
| 工單範圍內的技術或實作選擇 | 塔台代決，記進決策日誌 |
| 範圍變更、刪除或不可逆操作、對外發布、需要你偏好的選擇 | 塔台暫停並問你（`⏸ YOLO PAUSED — 提問需要你決定`），你回答後再答覆 |

這條線和斷點 C「擴大範圍是人的決定」是同一個道理：塔台能自主的，只有「在既定範圍內怎麼做」。每一題不論怎麼答，都記進決策日誌與 YOLO 歷程。提問本身不是斷點，不算 Renew，也不計入 `yolo_max_retries`。塔台也不背景輪詢題目，只在收到 `T#### 提問`，或查狀態時看到某個 Worker 在等塔台時才去讀。

BAT 這一端的提問介面，見 <BatLink path="control-tower#questions">BAT 站：Worker 問塔台</BatLink>。

::: tip 命令範例
本頁的命令與格式都是摘要，exit code、MCP 欄位與版本降級全表以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `control-tower/references/yolo-mode.md` § Worker 向塔台提問（v5.5.0+）（含 § 適用範圍、§ BAT 通道（v5.7.0+）、§ Worker 端、§ 塔台端、§ 計數、§ `worker_question_timeout` 的取值）
- `ct-exec/SKILL.md` § Questions For Tower (`CT_MODE=yolo`, v5.5.0+)
- `control-tower-guide/references/work-order-lifecycle.md` § yolo 提問通道：Worker 改問塔台（v5.5.0）
- CT 安裝與使用指南 § 2.33、§ 2.37、§ 2.38

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
