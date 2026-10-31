# Runtime 派工機制

工單寫好之後，還有兩段路要走：**把 Worker 開起來**（派工），以及**把結果送回塔台**（回報）。
v4 時這兩段都靠使用者手動；v4.1 之後，BAT（Better Agent Terminal）讓兩段都能自動化，YOLO 再進一步讓塔台自主決定下一張。

本檔講這套機制中**與終端無關**的分工與設計理由；BAT 這一端怎麼配合（環境變數、分頁角色、隔離派工、回收、查詢）見 `bat-integration.md`。
核心迴圈的三種形態（手動／BAT／YOLO）見 `work-order-lifecycle.md` § 核心迴圈；
確切的旗標、環境變數與 helper 路徑以 CT 的 `auto-session.md`、`yolo-mode.md` 為準，速查用 `ct-help`。

---

## auto-session 四階：人與機器各做哪一段

`auto-session` 設定決定派工後誰做什麼（預設 `ask`）：

| 值 | 開 Worker | Worker 回報 | 決定下一張 | 適合 |
|----|----------|------------|-----------|------|
| `off` | 塔台只顯示指令文字，使用者自己開 | 使用者帶回 | 使用者 | 不想讓塔台動終端、或環境無法自動化 |
| `ask` | 每次詢問：開新分頁／複製到剪貼簿／我自己來 | Worker 顯示固定訊息（剪貼簿／手動），由使用者帶回塔台 | 使用者 | 預設；每次派工都想看一眼 |
| `on` | 靜默開新分頁並帶入指令 | 預填，使用者按送出 | 使用者 | 已信任派工流程，只想省掉開分頁 |
| `yolo` | 同 `on` | **自動送出** | **塔台自主決定** | 一個已拆好單的 PLAN，想讓它自己跑完 |

`yolo` 是 `on` 的超集，多出三件事：Worker 自動送出、塔台自主派下一張、**斷點安全閘**（A／B／C；v5.3.0 加上合併前的 E，v5.5.0 加上 Worker 等待使用者的 D）。
v5.5.0 起 yolo Worker 有問題也不再問使用者，改問塔台（見下方〈yolo 下 Worker 改問塔台〉）。
啟用期間塔台狀態面板**下方**會一直顯示 `⚠️ YOLO MODE ACTIVE`，直到使用者改回設定。

每往下一階，就把一段「人的確認」交給機器。所以四階不是「越自動越好」的排序，而是**在哪裡保留人的判斷**的選擇——
`yolo` 拿掉了最後一個人工確認點，因此必須用斷點把判斷權在必要時交還給人。

---

## BAT：把派工與回報接到終端

在 BAT（Better Agent Terminal）裡，塔台用 helper 直接開出 Worker 分頁並帶入工單，Worker 收尾時把固定訊息送回塔台分頁，
收單後還能請 BAT 回收分頁；工單帶 `isolation: worktree` 時，BAT 會讓 Worker 在獨立的 git worktree 裡工作。
本檔其餘各節講派工的通用原則（BAT 的成功判讀與降級也在其中）；BAT 這一端的分工、兩組環境變數、`--workspace` 與 `--cwd`、塔台分頁角色宣告、範圍權杖與分頁角色、
worktree 隔離派工、收單後回收 Worker 分頁、查詢通道與 BAT 版本對照，集中在 `bat-integration.md`。

---

## Worker 無狀態：mode 怎麼送到 Worker

「Worker 不讀設定檔決定模式」的原則與同構理由見 `concepts.md` § Worker 無狀態、塔台有狀態。這裡講它的**傳遞路徑**：

```
塔台設定（auto-session）＋ 啟動詢問的結果
  → 派工參數 --mode <yolo|ask|off|on>、--interactive／--no-interactive（yolo 一律 --no-interactive，v5.5.0）
  → BAT 注入 Worker 環境 CT_MODE、CT_INTERACTIVE
  → Worker 收尾時依 CT_MODE 決定：on 只預填；yolo 預填並送出；
    ask／off（含缺值）顯示手動訊息，由使用者帶回
```

v4.3.0 把 `CT_MODE` 從設定檔搬到派工參數，本質是**把 runtime context 從磁碟搬到 process 參數**——
同一張工單、同一組參數，在哪個 session 執行行為都相同。

兩個邊界情況：

- `CT_MODE` 未設或不合法（例如舊版塔台派工）→ Worker 退回 `ask` 並顯示升級提示，不中斷
- `CT_INTERACTIVE` 未設 → Worker 依工單 frontmatter 的互動設定（見 `work-order-lifecycle.md` § 研究型工單）

v5.3.0 的隔離派工沿用同一條路徑：「這個 Worker 在 worktree 裡」也是派工時注入的變數（`CT_HOME` 等），Worker 不自己推測。
見 `bat-integration.md` § worktree 隔離派工。

---

## YOLO 與斷點：自主推進的邊界

### 塔台怎麼決定下一張

YOLO 下，塔台收到 Worker 的完成訊息後，從當前 PLAN 對應研究工單的**拆單建議表**機械式地挑出下一張。
資訊不足（找不到拆單表、格式不符、下一列只是占位符）就不猜，直接暫停。

### 斷點

斷點是「把判斷權交還給人」的時機。觸發時塔台暫停 YOLO，並提供選項讓使用者決定（斷點 D 例外，見表後說明）：

| 斷點 | 觸發條件 | 為什麼要停 |
|------|---------|-----------|
| **A** 非預期回報 | Worker 的回報訊息不精確符合固定格式（`T#### 完成`／`部分完成`／`需要協助`；v5.5.0 加 `提問`） | 機器無法確定 Worker 的真實狀態；可能是 Worker 版本舊或語氣出格 |
| **B-1** Renew 過多 | 工單 Renew 次數 ≥ N | 同一張工單反覆迭代，代表方向需要重新對齊，該拆新工單 |
| **B-2** 連續失敗 | 連續 N 張 `FAILED`／`BLOCKED`（`DONE`／`FIXED`／`PARTIAL` 會歸零） | 可能是 PLAN 或研究結論本身有問題，繼續派只會累積失敗 |
| **C** 跨出 PLAN | Worker 建議另開工單，或提到不在當前拆單表裡的編號 | 擴大範圍是人的決定，不是塔台能自主做的 |
| **D** Worker 等待使用者（v5.5.0） | 塔台順手查到 Worker 分頁 `blocked`（BAT MCP），原因是等使用者的那幾種：hook 的三種，v5.8.0 起加 codex 的 `input`（`blockedReason: tower` 不算，v5.7.0） | Worker 停在等人回答，使用者不一定看得到那個分頁；它**不暫停**流程，只告知（見下方） |
| **E** 合併前確認（v5.3.0） | 塔台要以 `--ff-only` 把隔離工單的合併結果推進 `main` 之前 | `main` 是所有工單共用的主線；機器判準沒能完全擔保合併品質時（驗收未全綠、有範圍外檔案、等價移植），要人看過才推進 |

N 是 `yolo_max_retries`（預設 `3`；`0` 停用斷點 B）。斷點 A 的比對同樣接受帶前綴的工單 ID，
因為它引用的是 ID 格式的單一權威定義，而不是自己另寫一份。
v5.15.0 起斷點 A 看的是通知字串的**結尾**：取最後一則 `<工單 ID> <關鍵字>`，前面只能是其他完整的通知。原因是 BAT 預填塔台輸入框後 Enter 沒送出時，
字串會留在輸入框，下一則直接接在後面（`T0715 提問T0715 提問`）；以前要求整個字串只有一則，就會誤停。原本合法的字串仍合法，其他原本會停的仍會停；
有幾題也不看字串，一律看 BAT 題目列表與工單標記（CT `yolo-mode.md` § 斷點 A）。
v5.13.1 補上另一個方向：工單是 `LB-T0184`，Worker 卻送來 `T0184 完成`。字串本身符合格式，所以**不是**斷點 A；塔台照缺前綴容錯對工單——熱區恰好一張 `LB-T0184` 就當作那一張並記錄，同號有多張或找不到才是斷點 A 的非預期狀態（`work-order-lifecycle.md` § 回報與通知用完整工單 ID）。

斷點 E 和其他斷點不同的地方：它**不只在 yolo 下生效**。非 yolo 模式下，每次 `--ff-only` 前一律暫停確認；
yolo 下則依合併模式決定能不能自動通過（機械合併判準仍成立、或衝突解決驗收全綠且無範圍外檔案 → 自動；等價移植 → 一律暫停）。
理由是「推進 `main`」的回頭成本比「派下一張工單」高得多。斷點 E 不計入斷點 B 的連續失敗計數。
合併流程本身見 `work-order-lifecycle.md` § worktree 隔離與合併工單；斷點 E 的確切規則以 CT 的 `yolo-mode.md` § 斷點 E 為準。

斷點 D 是唯一**不暫停**的斷點：塔台只在本來就在看某個 Worker 時（使用者問進度、等回報、Renew 或重派前）順手看 BAT 回報的分頁狀態，
看到 `blocked` 就用分頁標題告訴使用者「在等你回答」，請使用者自己去處理；塔台不代答、不送按鍵，也不另開輪詢。
yolo 下它是異常偵測（yolo Worker 本該問塔台），非 yolo 下只是告知。v5.7.0 起 BAT 另有 `blockedReason: tower`：Worker 在等的是塔台，
所以那不是斷點 D，塔台直接讀題答覆。v5.8.0 起 codex Worker 也看得到在等使用者（`blockedReason: input`，需 BAT `>= 0.7.0-pre.9` 與 codex `>= 0.163.0`），
處理和 claude 的一樣。設計理由與 BAT 版本條件見 `bat-integration.md` § 斷點 D；
確切規則以 CT 的 `yolo-mode.md` § 斷點 D 為準。

### 使用者中斷 ≠ 斷點

YOLO 期間使用者隨時輸入 `停`／`stop`／`abort` 就會暫停，但這**不是斷點**：

| | 斷點 A／B／C／D／E | 使用者中斷 |
|---|---|---|
| 觸發者 | 塔台／Worker 自動 | 使用者主動 |
| 計數 | 累計，影響 YOLO 健康判定 | 獨立計數，不影響健康判定 |
| 佔用 `yolo_max_retries` | 會（D 與 E 例外：不計入斷點 B） | **不會** |

分開的理由：使用者叫停通常是「我想看一下」，不代表流程出問題。若把它算成斷點，使用者每次喊停都會把 YOLO 推向「不健康」，最後反而不敢喊停。

### 啟動詢問與歷程

v5.5.0 之前，啟用 YOLO 時塔台會先問使用者「本 session 是否允許 Worker 在研究型工單中提問」，答案只存在塔台的 session 記憶中、**不落盤**，
再轉成派工的互動旗標。v5.5.0 起不再問：yolo Worker 有問題一律改問塔台（見下節），派工一律帶 `--no-interactive`；
想讓 Worker 直接問你，就改用非 yolo 模式。YOLO 的派工、斷點與提問紀錄寫在 `_tower-state.md` 的 `## YOLO 歷程` 區段（見 `three-layer-arch.md` § Tower State）。

### yolo 下 Worker 改問塔台（v5.5.0）

yolo 把人從迴圈裡拿掉，所以 Worker 的問題也不能再丟給人。v5.5.0 讓 yolo Worker 把問題寫進工單、送 `T#### 提問`、原地等塔台答覆；
塔台在工單範圍內代決，碰到範圍變更、不可逆操作、對外發布或需要使用者偏好的問題才暫停問使用者；等不到答覆就退回 `BLOCKED` + Renew。
這是 yolo「塔台自主」的延伸，邊界和斷點 C 一致。往返流程、代決邊界與備援見 `work-order-lifecycle.md` § yolo 提問通道。
v5.7.0 起，BAT `>= 0.7.0-pre.7` 時問答改走 BAT 結構化通道，題目仍寫進工單；通道失效就回到工單檔往返（同檔 § BAT 結構化通道）。

---

## Agent 中立：Claude Code 與 Codex

CT 的八個 skill 都能在 Claude Code（`/`）與 Codex（`$`）中執行；每個 skill 附有 `agents/openai.yaml` 提供 Codex 端的顯示名稱與預設提示
（frontmatter 為何只留 `name`／`description`，見 `governance.md` § 版本治理）。

派工時選哪個 agent，CT 刻意**不自己決定**：

| 路由 | agent 怎麼決定 |
|------|--------------|
| BAT 內部 | 派工參數 `--agent default`，由 BAT 依 workspace 預設 → 全域預設 → fallback CLI 解析 |
| 非 BAT | 先看 `CT_AGENT_CMD`（只允許 `claude`／`codex`）；未指定時只在兩者**恰好只有一個可用**時自動採用；否則交給剪貼簿或文字提示 |

`claude` 與 `codex` 都在、又沒有指定時，CT **不得自行偏好其中一個**——避免同一個專案的工單今天由 Claude 跑、明天由 Codex 跑，造成跨工具的行為漂移。
Codex 端的使用面見 `integration.md` § Codex。

---

## 成功判讀：信什麼、不信什麼

派工成功與否，CT 以 helper process 的 **exit code 為 `0`** 為主規則；`bat-scripts.log`（NDJSON，一行一筆）裡
`"script":"bat-terminal"`、`"event":"terminal-created"`、`"result":"ok"` 這筆 helper 端紀錄，是**事後查證用**
（這個 log 在哪裡，見 `bat-integration.md` § worktree 隔離派工（v5.3.0） 的 log 位置說明；v5.3.2 補引用）。
同名的 `terminal-created` 事件也會出現在 BAT app 端的日誌，但那是 app 端的紀錄，與 helper 的 exit code 不是同一個信號——
CT v5.0.1 ~ v5.0.9 曾把 app 端日誌的寫法當成查證依據，v5.1.0 更正。

| 不可信的訊號 | 為什麼 |
|-------------|--------|
| stdout 的 `Terminal created: ...` 文字 | 這是給人看的 cosmetic 輸出。以 skill＋工單形式派工時，它在舊版 BAT 會印出 `Terminal created: null`，但終端其實已建立成功——據此降級剪貼簿就是誤判 |
| 對 BAT 的 port 打明文 HTTP 健康檢查 | 那個 port 是 TLS／WSS endpoint，明文請求必然得到空回應——那是**協定不匹配**，不是 server 故障 |

共同的原則：**信機器語意的訊號（exit code、結構化日誌），不信給人看的文字**。
給人看的文字會隨版本改字、改格式，而它從來沒有承諾過語意。這條規則來自一次跨專案的翻盤調查，v5.0.1 起納入 CT 本體。

exit `0` 的意思也要讀準：它代表**分頁已建立**，不代表 Worker 已經啟動。BAT `< 0.7.0-pre.5` 有個實例（BAT BUG-151）：派工後約 1 秒內在 BAT 視窗打字，
啟動指令會失敗，helper 仍回 `0`。CT v5.5.1 先補了一句暫時說明（MCP 可用時可查）；v5.6.0 起改用正式機制。

### Worker 啟動確認（v5.6.0；v5.8.0 補 codex）

CT v5.6.0 派工時在參數最後加 `--wait-started 30000`（需 BAT `>= 0.7.0-pre.6`）：helper 建好分頁後最多等 30 秒，
等 Worker 的 claude 執行 `SessionStart` hook，再在 stdout 最後一行寫出結果。**派工成功與否仍看 exit code**；
`started:` 這一行只在帶了參數時才解析——這是「不信給人看的文字」的例外嗎？不是：它是 BAT 介面契約定義的機器輸出，不是 cosmetic 文字。

| 結果 | 意思 | 塔台怎麼做 |
|------|------|-----------|
| exit `0` + `started: <時間>` | Worker 的 claude 已啟動（v5.8.0：codex `>= 0.163.0` 也算，信號是它送的第一個 OSC 7501） | 派工成功，時間留作證據 |
| exit `0` + `started: unknown` | **無法判定**（較舊或版本確認不到的 codex、自訂 CLI、hooks 被關閉……） | 照舊等 Worker 回報 |
| exit `8` + `started: unconfirmed` | 分頁在，30 秒內沒確認啟動 | **不重派**；MCP 可用時看分頁輸出，否則以分頁標題請使用者去看 |
| exit `1` | 派工失敗 | 照舊走降級鏈（舊 BAT 的例外見下） |

兩個最容易讀錯的地方：

- **exit `8` 為什麼不能重派**：分頁沒有被關掉，Worker 可能只是起得慢。重派會讓同一張工單同時有兩個 Worker 在跑——
  這比「晚一點才知道它起來了」糟得多。還有一種誤報：BAT 讀不到的 hooks 關閉方式（例如專案設定）會讓確認信號永遠不來，
  但 Worker 其實正常在跑。所以 exit `8` 交給人看，不交給自動化。使用者看過之後決定重派時，塔台先請 BAT 回收這個分頁再派（v5.12.0，
  見 `bat-integration.md` § 重派前回收舊 Worker 分頁），同一張工單一樣不會留下兩個 Worker。
- **`unknown` 為什麼不是失敗**：它只代表「這個分頁沒有信號可看」（較舊的 codex Worker 沒有 claude 的 hooks、也不送 OSC 7501，hooks 被關閉時也一樣），
  不代表 Worker 沒起來。把它當失敗，等於把所有舊 codex 派工都判成失敗。MCP 的 `agentStarted: null` 是同一個意思。

**codex 也有啟動信號了（v5.8.0，BAT `>= 0.7.0-pre.9`）。** codex `>= 0.163.0` 就緒後會自己送 OSC 7501，BAT 把第一個當成「已啟動」，
所以 codex Worker 也會回 `started: <時間>` 或 exit `8`，判讀規則和 claude 完全一樣。BAT 派工時先跑 `codex --version`：確認不到版本就維持 `unknown`，
**絕不回 `unconfirmed`**——寧可說「不知道」，也不讓塔台把一個正常的 Worker 當成沒起來。codex 的 exit `8` 最常見的原因是卡在啟動畫面
（未信任資料夾的「Trust this folder?」、「Hooks need review」），這些畫面不送任何序列，所以同樣交給人看、不重派。
BAT 還會替派出的 codex Worker 加 `-c check_for_update_on_startup=false`，避免更新提示擋住啟動；這是 BAT 的事，CT 的派工命令一個字都不用改。

**舊 BAT 的降級**：不認得 `--wait-started` 的 helper 會 exit `1`、stderr 寫 `Unknown option '--wait-started'`，而且**不建立分頁**。
塔台看到這個組合就去掉參數重派一次，並在這個塔台 session 記住「不支援」，之後不再帶——所以舊 BAT 最多多一次沒有副作用的失敗，
接著行為就和 v5.5.1 一樣。這是 CT 少數允許看 stderr 的地方，而且只用來**選降級路徑**，不用來判斷成敗：
認得參數的新 helper 根本不會印這句話，所以不會出現 `--workorder` 前綴那種「新舊版訊息都含同一字串」的反向誤判。
完整規則以 CT `auto-session.md` § Worker 啟動確認 為準。

---

## 降級鏈

派工的路由由特定到通用：

```
BAT 內部終端（偵測到 BAT 的 dispatch 變數）
  ↓ 不是 BAT 環境
開新終端分頁（依偵測到的終端類型）
  ↓ 終端未知或無法開分頁
寫入剪貼簿
  ↓ 剪貼簿工具不可用
文字提示（永遠顯示）
```

- **環境降級是靜默的**：不顯示錯誤、不打擾使用者——環境本來就不支援，報錯沒有意義
  （v5.2.4 例外：stderr 含 `Forbidden` 或 `RECOVERY_PENDING` 時多一行原因提示，降級本身照常，見 `bat-integration.md` § 範圍權杖與分頁角色）
- **文字提示永遠顯示**：即使成功開了分頁也顯示，使用者換個環境還能照著做
- **隔離工單不走這條鏈**（v5.3.0）：鏈上每一級都會讓 Worker 落在主 checkout，等於悄悄改成非隔離；所以隔離派工失敗就停下，由使用者決定（見 `bat-integration.md` § worktree 隔離派工）

但有一種降級**必須明示**：舊版 BAT 不接受帶前綴的工單 ID。塔台**不預先偵測 BAT 版本**，一律先照常派工；
只有在 helper 失敗、且錯誤指向工單參數不合法時，才改用相容的指令形式重送一次，並**明白寫出「已降級」與原因**——
使用者要能看出這台機器的 BAT 該升級了（各功能需要的 BAT 版本見 `bat-integration.md` § 版本對照表）。降級**只做一次**，再失敗就走上面的降級鏈，不得靜默重試迴圈。

兩種降級待遇不同，理由也不同：環境不支援是常態，說了也無從改善；BAT 版本舊是**可修的問題**，靜默帶過等於把它藏起來。
至於為什麼不先判斷版本——用錯誤訊息字串判版曾經反向誤判（新版的錯誤訊息仍含舊字串），「先送、失敗才降級」就完全不需要判版。

### Worker 端的回報降級

Worker 收尾通知失敗時同樣如實處理：非 YOLO 模式記錄失敗並顯示剪貼簿或手動訊息；YOLO 模式**不得宣稱已自動送出**，
要明白寫出應手動帶回塔台的確切訊息。新版塔台派工給不支援自動回報的舊版 Worker 時，也以明確的 `PARTIAL`／`BLOCKED` 或升級提示回報。

v5.1.0 更正：Worker 的收尾順序是**先寫最終狀態與回報區、再 notify**（v5.7.0 起 notify 前一律先 commit 工單，`ct-done` 也一樣）。所以 YOLO 下 notify 失敗時，工單**已是最終狀態**，
只是塔台沒收到通知（沒有回報可讀，也就不觸發斷點）；使用者把 Worker 顯示的固定訊息帶回塔台，塔台依工單檔案的最終狀態與回報區收單。
CT v4.2.0 ~ v5.0.9 寫的「notify 失敗時工單維持執行中」不成立。
