# 預覽：BAT ↔ CT 契約 v2——待你決定、待你執行（v6.1.0-pre.1）

> 📌 **本章內容已納入正式版 6.1.0，保留作為預覽期間的參考。** CT v6.1.0（2026-11-25）取代 6.0.2 成為穩定版；本章寫的 BAT ↔ CT 契約 v2 6.1.0 起屬於正式版，規範內容與 6.1.0-pre.1 相同。
> 下面的「預覽版、尚未發布」「穩定版仍是 6.0.2」「BAT 端還沒發佈、還沒在實機跑過」等說法是 **6.1.0 以前**的狀態：6.1.0 的下載在 GitHub Release `ct-v6.1.0`（Latest），CT plugin 6.1.0 上架 marketplace；
> 支援契約 v2 的 BAT（BAT ≥ 0.8.0-pre.3）已發佈，契約 v2 已在它的測試版上實機驗證（驗了什麼、還沒驗什麼見〈已知未驗〉）。本章的檔名與段落錨點不改。
> **正式章節**：簡述在 `bat-integration.md` § BAT ↔ CT 契約 v2：待辦分頁（v6.1.0+）；版本變更見 CT `docs/CHANGELOG.md` `[6.1.0]`、安裝指南 § 2.69。
>
> ⚠️ **預覽版，尚未發布。** 本章寫的是 CT v6.1.0-pre.1 的 BAT ↔ CT 契約 v2。預覽版只打包、不安裝、不建 Release；
> **穩定版仍是 6.0.2**。支援契約 v2 的 Better Agent Terminal（BAT）也還沒發佈，本章提到的 BAT 端行為都還沒在實機跑過（見〈已知未驗〉）。
> 回答時先告訴使用者這一點。
>
> 本章跟其他章一樣是**教科書**：講為什麼這樣設計、實際用起來是什麼樣子。欄位表、型別、上限、觸發點、訊息字樣一律以 CT 權威檔為準，
> 本章只寫檔名與章節名，不重抄規則表。要照著做的確切寫法，指向 `ct-help` § 與 BAT 協作（Working With BAT, v6.1.0+）或下表的權威檔。

| 主題 | CT 權威定義（`BMad-Control-Tower-v6.1.0`；章節與 6.1.0-pre.1 相同） |
|------|------------|
| 契約 v2 的欄位、誰寫誰清、回答格式、`user_inbox: off`、隱私、時區、筆數 | `control-tower/references/memory-protocol.md` § 契約 v2 欄位（v6.1.0+）（**唯一權威**） |
| 開工宣告（`--set-role tower --bat-contract 2`）、`bat-contract:`／`hooks:` 解析、舊 BAT 重送、降級提示 | `control-tower/references/auto-session.md` § 塔台分頁角色宣告 第 3、5 點 |
| 狀態面板的 `BAT 契約` 欄與三種提示行 | `control-tower/references/memory-protocol.md` § 塔台狀態面板 |
| 斷點暫停時寫待決、Worker 提問升級時寫待決 | `control-tower/references/yolo-mode.md` § 斷點判準（〈暫停時寫待決〉）、§ Worker 向塔台提問 › 塔台端 |
| 依賴的工單在等你 → 不派；收單時寫待執行 | `control-tower/references/work-order-system.md` § 派發流程 第 2.6 步、§ 回報處理流程 第 4.5 步 |
| 工單 `waiting_user` | `control-tower/references/work-order-template.md` § `waiting_user` |
| 回覆結尾重列 | `control-tower/SKILL.md` § Output Style |
| `user_inbox` 設定 | `control-tower/references/tower-config.md` § 可用選項 |
| `check-frontmatter.py` 的新檢查 | `control-tower/scripts/check-frontmatter.py` 開頭說明 |
| 版本變更與已知未驗 | CT `docs/CHANGELOG.md` `[6.1.0]`（預覽時 `[6.1.0-pre.1]`）、安裝指南 § 2.69（預覽時 § 2.68） |

---

## 一句話

**塔台要你做的事，從「終端裡的一段話」變成「檔案裡的一筆資料」。** 塔台把要你決定的事（`U-n`）和要你自己執行的事（`A-n`）寫進
`_tower-state.md` 的 frontmatter，BAT 的「待辦」分頁唯讀顯示；不用 BAT 的人也不吃虧——有東西在等你時，塔台每次回覆的最後一行都會重列一次。
**沒有東西在等你時，什麼都不多。**

---

## 為什麼：提問被後面的回合淹沒

yolo 下塔台同時看好幾個 Worker。一個 Worker 碰到斷點、塔台停下來問你「A／B／C 選哪個」，下一秒另一個 Worker 回報 `完成`，塔台收單、派下一張，
又是一大段輸出。等你回到塔台分頁，那個問題已經被捲到好幾個畫面之外；更糟的是，塔台後面的回覆看起來一切正常，
你不會知道上面還有一題沒答，而那張工單（以及依賴它的工單）就一直停著。

以前的補救都是「把話說得更醒目」：⏸ 標記、粗體、重複一次。問題不在醒不醒目，而在**它是一段會被捲走的文字**。所以契約 v2 換了做法：

1. **要你做的事變成資料**：寫進 `_tower-state.md` 的 frontmatter，有編號、有選項、有建立時間。文字會被捲走，檔案裡的一筆不會。
2. **BAT 把資料放在固定位置**：BAT 右側欄新增「待辦」分頁，讀這份 frontmatter，列出待你決定、待你執行、到期提醒，以及哪些工單在等你。
3. **不靠 BAT 的那一半也一起做**：塔台每次回覆的最後一行固定重列還沒結的項目。終端、Claude 面板、舊 BAT 都看得到。

**分工照舊：CT 寫，BAT 讀。** 這和 v1（BAT 塔台面板讀取契約，見 `bat-integration.md` § BAT 塔台面板讀取契約）是同一個方向——檔是 CT 寫的，
所以欄位定義寫在 CT 這邊；BAT 只讀、**不改 CT 的任何檔**，連「已回答」也不由 BAT 標記。清單裡的項目消失，就是已經結了。
這樣兩邊各只有一個寫入者，不會出現「BAT 標了已回答、塔台卻沒收到」這種兩份狀態對不上的情況。

**兩邊都是 v2 才啟用。** 塔台開工時向 BAT 宣告自己說契約 v2（下方〈開工宣告〉）；BAT 只對宣告了 v2 的塔台分頁打開新功能。
任一邊比較舊，就各自照舊運作，不會半套。

---

## 欄位一覽：記住名字就好，寫法看權威節

| 欄位 | 在哪 | 一句話 |
|------|------|--------|
| `bat_contract: 2` | `_tower-state.md` frontmatter | 這份狀態檔照契約 v2 寫；**整數、不加引號**；6.1.0 起每次寫入都寫 |
| `ct_version` | 同上 | 寫入這份檔的 CT 版號（取自已安裝 `control-tower/SKILL.md` 的版本註解）；BAT 只顯示 |
| `awaiting_user[]` | 同上 | **待你決定**，每筆 `U-n`：哪張工單、什麼來源（哪個斷點或提問）、一句摘要、選項 |
| `user_actions[]` | 同上 | **待你執行**，每筆 `A-n`：實機驗收（`verify`）、要你跑的指令（`run`）、手動操作（`manual`） |
| `reminders[]` | 同上 | 專案的定期事項與到期日 |
| `next_ids.user`／`next_ids.action` | 同上 | 下一個 `U-n`／`A-n`；專案內遞增、不重用 |
| `waiting_user: "U-n"` | **工單** frontmatter | 這張工單在等你決定哪一題 |

確切的鍵、型別、長度與筆數上限只寫在 CT `memory-protocol.md` § 契約 v2 欄位，本章不重抄。

### 兩種版號：`summary_version` 不升，另外多一個 `bat_contract`

契約 v1 的機器可讀摘要有 `summary_version: 1`（`three-layer-arch.md` § Tower State）。這次加了一堆新欄位，為什麼不升成 2？

- `summary_version` 的規則從 v5.13.0 起就寫明：**新增欄位不升版；改既有欄位的名稱、型別或語意才升**。契約 v2 一個舊欄位都沒動，
  只讀 v1 的 BAT 照樣讀得懂，升版反而會讓它誤以為格式變了。
- 但 BAT 還是需要知道「這份檔有沒有 v2 的內容」，才能決定待辦分頁要不要啟用——這是**功能協商**，不是格式相容。所以另開一個欄位 `bat_contract`。

兩個號碼回答的是兩個不同的問題：`summary_version` 是「我讀得懂這份摘要嗎」，`bat_contract` 是「這個塔台和我說同一版的協作規則嗎」。

---

## 生命週期：什麼時候寫、什麼時候清

**寫待你決定（`U-n`）**——塔台停下來要你決定時，在顯示暫停訊息的**同一次**寫入加一筆；有工單時工單同時加 `waiting_user`：

- yolo 斷點 A、B-1、B-2、C 暫停，斷點 E（含非 yolo 的 `⏸ 合併前確認`）
- Worker 的提問超出塔台能代決的範圍、升級給你（`⏸ YOLO PAUSED — 提問需要你決定`，見 `work-order-lifecycle.md` § 塔台代決的邊界）
- 塔台自己停下來等你決定、而且不是同一輪對話就接著做的事（例：收單後要你選下一步）

**不寫**：斷點 D（它本來就不暫停，你要去 Worker 分頁處理）、你自己中斷 yolo、需求對齊時一來一往的提問。原則是「會停在那裡等你的才寫」——
清單的價值在於裡面每一筆都真的在等你，混進會自己過去的事，清單就沒人信了。

暫停訊息本身也帶上同一個編號：

```
⏸ YOLO PAUSED — 斷點 A 觸發
  ...
  待決編號：U-3
  ...
  請回覆 U-3：A／B／C
```

**寫待你執行（`A-n`）**——收單時，Worker 回報區列的「待實機／待使用者執行」項目各寫一筆，收單確認裡列出新的 `A-n`。
以前這類項目寫在 `todo`，跟塔台自己的待辦混在一起；現在改寫這裡，`todo` 不再重複列。

**清掉**——你回答後，塔台在同一次寫入移除那一筆、清掉工單的 `waiting_user`、在決策日誌記一筆（含 `U-n`）。
工單取消、重開或那件事不再需要決定時也一併移除並記原因。`A-n` 回「完成」就移除；回「失敗」也移除，塔台依內容開 BUG 或重開工單——
失敗的後續由新的單據承接，不讓同一筆一直掛著。

**依賴的工單在等你 → 先不派。** 派工前塔台看 `depends_on`：依賴的工單有 `waiting_user`，這張就先不派，印一行說明在等哪一題；**其他工單照常派**。
只暫停真正受影響的那條線，yolo 的其他進度不必陪著停。

**不自動遷移。** 升到 6.1.0 時，舊 `todo` 裡「等你決定」「等你實機驗收」的項目不會被批次改寫；塔台下次處理到那一項時再搬。
批次改寫狀態檔的風險（改錯、改漏、一次大 diff）比「舊項目晚一點搬」大得多。

---

## 回答：一行就好

| 你要做的 | 回覆 |
|----------|------|
| 選一個選項 | `U-3：B` |
| 不在選項裡的答案 | `U-3：<你自己的話>` |
| 做完了 | `A-2：完成` |
| 做了但失敗 | `A-2：失敗 <哪裡不對>` |

- 全形 `：` 與半形 `:` 都可以，冒號前後的空白不管；一則訊息可以有好幾行，逐行處理。
- 代號不分大小寫，而且要**只命中一個選項**才算選了它，否則整段當自由回答——寧可當成你寫的一句話，也不要猜錯成某個選項。
- 只有一題在等、你直接回 `B`：塔台照那一題處理，確認行會寫出 `U-n`。對不到唯一一題就會問你是哪一題。
- 塔台回一行確認，例：`U-3 已收到：B → 恢復 T0123`、`A-2 已收到：完成`。
- 你可以在塔台分頁自己打，也可以用 BAT 待辦分頁的回答框——它送進塔台分頁的就是同一行字，CT 不區分。

### 回覆結尾重列：任何終端都有

有東西在等你時，塔台**每次回覆的最後一行**固定是這一行（沒有項目的那半段不印，兩者都沒有就整行不印）：

```
⏸ 待你決定：U-3（T0123）、U-5（—）；🙋 待你執行：A-2（安裝新版後做一次完整重裝驗收）——回覆「U-n：選項」或「A-n：完成」
```

這一行只是**提醒**，資料在 frontmatter；它不取代問問題的那則暫停訊息。之所以放在最後一行，是因為最後一行是你回到分頁時第一眼看到、
也最不會被後面的輸出蓋掉的位置。它不依賴 BAT，所以舊 BAT、非 BAT 終端、Claude 面板開的塔台都一樣有。

---

## 開工宣告：先寫狀態檔，再告訴 BAT

塔台本來每次啟動就會 `--set-role tower` 向 BAT 宣告分頁角色（`bat-integration.md` § 塔台分頁角色宣告）。6.1.0 在同一個呼叫多帶 `--bat-contract 2`，順序是：

1. `_tower-state.md` 還沒有 `bat_contract: 2`（含第一次開工）→ **先寫入**；
2. 帶 `--bat-contract 2` 呼叫 `--set-role tower`；
3. 讀輸出的 `bat-contract:` 與 `hooks:` 兩行。

**為什麼先寫檔再宣告**：BAT 看到分頁宣告 v2 時會去讀狀態檔；如果順序反過來，BAT 會先讀到一份還不是 v2 的檔。先寫再說，對方讀到的一定是一致的狀態。

**為什麼每次都要帶**：BAT 每次 `--set-role` 都覆寫這個分頁的宣告。模式變更時（`*config auto-session <m>`）塔台會再呼叫一次，那一次若沒帶，
BAT 就會把契約宣告清掉——和 v5.2.0 起「每次都要帶 `--mode`」是同一個道理。

**狀態面板多一欄 `BAT 契約`**，值只有四種：

| `BAT 契約` | 什麼情況 |
|------------|---------|
| `v2` | BAT 回 `bat-contract: 2` |
| `不支援（BAT 太舊）` | BAT 認得參數但不支援 v2，或根本不認得這個參數（下方） |
| `未知（宣告失敗）` | `--set-role` 本身失敗（連線、權杖等），照舊不重試、不擋開工 |
| `略過（非 BAT）` | 不在 BAT 裡，或是 Claude 面板開的塔台 |

**舊 BAT：只重送一次。** 太舊的 helper 不認得 `--bat-contract`，會回 exit `1`＋`Unknown option '--bat-contract'`，而且**沒有**設定角色。
塔台不帶這個參數重送一次，標題與模式照舊可用，本 session 之後都不再帶；開工面板印一行降級提示，說明哪些功能不可用、待決事項仍會列在回覆結尾。
這和 `--wait-started`（v5.6.0）的處理是同一個模式：**先送、失敗才降級、只降一次**（`runtime-dispatch.md` § 降級鏈）。
只重送一次是刻意的：再多試幾次也不會讓舊 BAT 變新，只會把開工拖長、把錯誤訊息洗版。

**`hooks:` 那一行講的是另一件事。** BAT 用自己的 claude hooks 知道塔台的 Claude 在幹嘛（回合結束、停在對話框、回合訊息卡）。
BAT 開的 Claude 分頁會自動加上；但你在 shell 分頁手打 `claude`、在 agent 自訂參數放了 `--settings`、或關了 BAT MCP 時就沒有。
這時 BAT 回 `hooks: none (<原因代號>)`，塔台在開工面板印一行原因與怎麼修（代號對照在 CT `auto-session.md` § 塔台分頁角色宣告 第 5 點）。
`hooks: ok …` 與 Codex 的 `hooks: n/a (codex)` 不印——沒問題的事不佔面板。

兩個容易混淆的點：

- **BAT 的 hooks 不是 CT 的 hooks**：CT 自己的 hooks 是另一件事，不屬契約 v2。
- **CT 不替你安裝 plugin、不改你的 claude 設定**：需要 BAT 的 `bat-hooks` plugin 時，面板只告訴你怎麼做，裝不裝由你。
  會改使用者環境的事，必須由使用者自己決定。

**CT 只看這一次呼叫的輸出。** BAT MCP 雖然也查得到這個分頁的契約版本與 hooks 狀態，CT 不讀那些欄位來判斷——同一件事只有一個判斷依據，
跟「信機器語意、不信旁證」（`runtime-dispatch.md` § 成功判讀）一致。

**非 BAT 終端**：不呼叫 `--set-role`（照舊），但 v2 欄位照寫、回覆結尾照印。契約版本和「在不在 BAT 裡」是兩件事：
狀態檔今天在終端寫、明天在 BAT 裡讀，內容應該一樣。

---

## `user_inbox: off`、隱私、時區、筆數與自檢

**不想把這些寫進檔案：`*config user_inbox off`**（加 `--save project` 保存）。塔台就不寫 `awaiting_user`、`user_actions`，退回 6.0.x 的做法
（待決只在終端、待執行照舊放 `todo`）；`bat_contract`、`ct_version`、`reminders`、工單 `waiting_user` 照寫，**回覆結尾照印**。
典型情境是 `_ct-workorders/` 會公開的專案。注意它關的是「寫清單」，不是「契約 v2」：開工宣告照常、`bat_contract` 照寫，
因為契約版本描述的是這個塔台怎麼寫檔，不是這次寫了哪些內容。

**隱私**：摘要、標題、選項、指令不寫祕密、權杖、客戶資料、真實個人資料；需要細節就寫「見 T#### 回報區」。
這些欄位會顯示在 BAT 面板上，也跟著 repo 走，寫法和決策日誌是同一類標準。

**時區**：契約 v2 新欄位的時間寫成 `+08:00` 這種**帶冒號**的時區（`date "+%Y-%m-%dT%H:%M:%S%:z"`），既有欄位（`updated_at` 等）維持 `+0800` 不改。
新欄位的寫法是 BAT 與 CT 核定契約 v2 時的約定；舊欄位不改，是因為改了就動到契約 v1 已有欄位的寫法。兩者一樣都要取自系統時間，不得手打。

**筆數上限**：待決、待執行各 20 筆，提醒 10 筆。超過時開工面板多一行提示，**不擋流程**——上限是讓你注意清單已經失去「一眼看完」的用途，
該先處理或移除過時的項目；整份 `_tower-state.md`（含 frontmatter）仍受 400 KB 預算約束（`bat-integration.md` § 400 KB 預算）。

**寫完自檢多了 v2 的檢查。** 6.0.1 的寫入後自檢（`three-layer-arch.md` § Tower State）照舊跑 `check-frontmatter.py`；6.1.0 的腳本對狀態檔另檢查
v2 欄位的型別、編號格式、選項代號、字數與日期，對工單檢查 `waiting_user`。第一次出現**警告層級**（`- WARN`），只用在筆數超過上限：
它不影響 exit code，因為超過上限不會讓檔讀不到，只是該整理了；其他問題仍是 FAIL、不得 commit。沒有 v2 欄位的 6.0.x 狀態檔照舊通過，輸出逐字相同。
選項代號格式不對時，塔台在**寫入前**自己改，不留給 BAT 退回成自由回答。

---

## 版本需求：舊 BAT、非 BAT 也能用

| 組合 | 會看到什麼 |
|------|-----------|
| CT 6.1.0（本預覽 6.1.0-pre.1）＋支援契約 v2 的 BAT（**BAT ≥ 0.8.0-pre.3**） | 待辦分頁、通知保護、回合訊息卡；`BAT 契約：v2` |
| CT 6.1.0＋舊 BAT | 沒有待辦分頁；開工面板一行降級提示；標題、模式、派工、回收照舊；回覆結尾照樣重列 |
| CT 6.1.0＋非 BAT 終端或 Claude 面板 | 不宣告；v2 欄位照寫、回覆結尾照印 |
| CT 6.0.x＋新 BAT | 塔台不宣告 v2，BAT 的待辦分頁說明需要哪一版、保持關閉；其他照舊 |

BAT 端的對應版本與 CT 6.1.0 同日發佈；上表第一列的最低版號（BAT ≥ 0.8.0-pre.3）與 CT `auto-session.md` § 塔台分頁角色宣告 第 5 點的降級提示相同。
這也是 CT 一貫的「CT 可以先發」（`bat-integration.md` § 版本對照表）：新功能設計成舊 BAT 失敗即降級，所以 CT 不必判斷 BAT 版本。

既有的「塔台停在權限或提問對話框時，BAT 延後送出 Worker 通知」（`bat-integration.md` § Worker 執行與通知〈塔台在等你時，通知會先排隊〉）**不綁契約版本**，照舊運作。

---

## 圖：CT 寫、BAT 讀、你回答

<svg width="100%" viewBox="0 0 680 450">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<g class="node c-amber" onclick="sendPrompt('介紹契約 v2 什麼時候寫待你決定')">
  <rect x="40" y="40" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="130" y="58" text-anchor="middle" dominant-baseline="central">斷點／提問升級</text>
  <text class="ts" x="130" y="76" text-anchor="middle" dominant-baseline="central">→ 暫停等你</text>
</g>
<g class="node c-gold" onclick="sendPrompt('介紹收單時怎麼寫待你執行')">
  <rect x="460" y="40" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="58" text-anchor="middle" dominant-baseline="central">塔台收單</text>
  <text class="ts" x="550" y="76" text-anchor="middle" dominant-baseline="central">→ 待實機項目</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹 _tower-state.md 的契約 v2 欄位')">
  <rect x="230" y="140" width="220" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="159" text-anchor="middle" dominant-baseline="central">_tower-state.md</text>
  <text class="ts" x="340" y="178" text-anchor="middle" dominant-baseline="central">U-n／A-n＋waiting_user</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹 BAT 待辦分頁看得到什麼')">
  <rect x="40" y="250" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="130" y="268" text-anchor="middle" dominant-baseline="central">BAT 待辦分頁</text>
  <text class="ts" x="130" y="286" text-anchor="middle" dominant-baseline="central">→ 唯讀顯示</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹塔台回覆結尾的待決重列')">
  <rect x="460" y="250" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="268" text-anchor="middle" dominant-baseline="central">回覆最後一行</text>
  <text class="ts" x="550" y="286" text-anchor="middle" dominant-baseline="central">→ 任何終端</text>
</g>
<g class="node c-blue" onclick="sendPrompt('介紹 U-n 和 A-n 怎麼回答')">
  <rect x="250" y="340" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="358" text-anchor="middle" dominant-baseline="central">你回答</text>
  <text class="ts" x="340" y="376" text-anchor="middle" dominant-baseline="central">→ U-3：B</text>
</g>
<line x1="130" y1="92" x2="290" y2="140" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="550" y1="92" x2="390" y2="140" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="290" y1="196" x2="150" y2="250" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<line x1="390" y1="196" x2="530" y2="250" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="150" y1="302" x2="290" y2="340" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="530" y1="302" x2="390" y2="340" stroke-width="1" marker-end="url(#arrow)"/>
<path d="M340 340 L340 196" fill="none" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="352" y="270" dominant-baseline="central">塔台移除＋記決策</text>
<text class="ts" x="210" y="214" text-anchor="middle" dominant-baseline="central">只讀</text>
<text class="ts" x="340" y="420" text-anchor="middle">圖例：藍色「你回答」借用 Worker 色，表示使用者端的動作</text>
</svg>

（上排兩個寫入點都寫進狀態檔；狀態檔往下分兩條：BAT 待辦分頁只讀（虛線，需要支援契約 v2 的 BAT），回覆最後一行任何終端都有；
你回答後由**塔台**移除那一筆並記決策日誌——BAT 從不改檔。圖的規格見 `diagrams.md` § 21。）

---

## 已知未驗

預覽時（CT `CHANGELOG.md` `[6.1.0-pre.1]` › Known unverified）列的兩項，6.1.0 發佈前都已在 BAT 0.8.0-pre.3 的測試版上實機驗過（CT `CHANGELOG.md` `[6.1.0]` 〈實機驗證〉）：

- **已驗證**：支援契約 v2 的 BAT（BAT ≥ 0.8.0-pre.3）已發佈；`--bat-contract 2` 的實際輸出（`bat-contract:`／`hooks:` 兩行）、舊 BAT（0.8.0-pre.1）的 `Unknown option` 只重送一次與降級提示、待辦分頁顯示都實機跑過
- **已驗證**：塔台先寫 `bat_contract` 等欄位再宣告、之後每次寫入都帶；暫停（斷點 A）與塔台自己的提問寫待決；有項目時每則回覆的最後一行都重列，兩邊都空就不印

另外也實機驗過：從 6.0.2 換版（既有 `todo` 原樣保留）、待決與待執行的回答與移除（`U-n：A`、`U-n：<文字>`、`A-n：完成`、`A-n：失敗 <說明>`）、通知保護、回合訊息卡、`bat-hooks` plugin 並存、CT guard 照常。

正式版 6.1.0 仍未實機驗證的（CT `CHANGELOG.md` `[6.1.0]` › Known unverified，編號相同）：

1. `hooks: none (<原因>)` 與 `plugin-outdated` 的提示行：實機宣告都回 `hooks: ok`，沒有出現過
2. `bat-contract: 2 (requested <n>: unsupported)` 與「exit 0 但沒有 `bat-contract:` 行」兩種不支援的情況：沒有出現過
3. 不在 BAT 裡的終端，以及 Codex 塔台（`hooks: n/a (codex)`）：實機都是 BAT 內的 Claude Code 塔台
4. 斷點 B-1／B-2／C／E 與 Worker 提問升級（`worker-question`）寫待決：只驗過斷點 A 與塔台自己的提問
5. 工單的 `waiting_user`，以及「依賴的工單在等你決定時先不派」：沒有觀察到
6. 收單時把回報區的「待實機／待使用者執行」項目自動寫成 `A-n`：實機的 `A-n` 是應要求寫入的
7. `user_inbox: off`、`reminders`、筆數超過上限的警告：只有樣本測試

---

## 常見誤解

| 誤解 | 實際 |
|------|------|
| 「沒有 BAT 就用不到契約 v2」 | 欄位照寫、回覆結尾照印；BAT 只是多一個固定位置顯示 |
| 「在 BAT 待辦分頁按了回答，BAT 就把那一筆標成已回答」 | BAT 只把同一行字送進塔台分頁；移除那一筆的永遠是塔台 |
| 「`user_inbox: off` 就是關掉契約 v2」 | 只是不寫兩個清單；`bat_contract`、開工宣告、回覆結尾照舊 |
| 「契約 v2 讓 `summary_version` 變成 2」 | 仍是 `1`；契約版本由新的 `bat_contract` 表示 |
| 「有一張工單在等我，yolo 就全部停了」 | 只有 `depends_on` 指到它的工單先不派，其他照常 |
| 「回 `U-3：b` 不算選 B」 | 代號不分大小寫；只要唯一命中就算 |
| 「BAT 回 `hooks: none` 是 CT 壞了」 | 那是 BAT 的 hooks 沒裝上（例：手打 `claude`），照面板那一行修；CT 不替你裝 plugin |
| 「升級後舊的 `todo` 會被自動搬進新清單」 | 不自動遷移，塔台下次處理到時再搬 |
| 「契約 v2 還是預覽、還沒在實機跑過」 | 6.1.0 起屬正式版，已在 BAT 0.8.0-pre.3 的測試版上實機驗證；還沒驗的路徑見〈已知未驗〉 |

---

## 本章引用的 CT 檔與章節

- `control-tower/references/memory-protocol.md`：§ 契約 v2 欄位（v6.1.0+）、§ 機器可讀摘要（YAML frontmatter）、§ BAT 塔台面板讀取契約、§ 塔台狀態面板、§ YAML frontmatter 字串寫法與寫入後自檢
- `control-tower/references/auto-session.md`：§ 塔台分頁角色宣告（第 1、3、4、5、8 點）
- `control-tower/references/yolo-mode.md`：§ 斷點判準（〈暫停時寫待決〉）、§ Worker 向塔台提問 › 塔台端
- `control-tower/references/work-order-system.md`：§ 派發流程（第 2.6 步）、§ 回報處理流程（第 4.5 步）
- `control-tower/references/work-order-template.md`：§ `waiting_user`
- `control-tower/references/tower-config.md`：§ 可用選項（`user_inbox`）
- `control-tower/SKILL.md`：§ Output Style、Startup Protocol 第 5、6、8 步
- `control-tower/scripts/check-frontmatter.py`：開頭說明（契約 v2 的問題代碼與 WARN 層級）
- `ct-help/SKILL.md`：§ 與 BAT 協作（Working With BAT, v6.1.0+）
- `docs/CHANGELOG.md` `[6.1.0]`、`[6.1.0-pre.1]`；安裝指南 § 2.69、§ 2.68
