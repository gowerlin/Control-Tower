---
title: 檔案即真相來源
description: 為什麼不靠對話記憶：工單、決策日誌與狀態檔各記什麼，frontmatter 為什麼是機器的事實來源，以及收尾為什麼要反序寫入。
---

# 檔案即真相來源

<p class="ct-lead">記憶會錯，檔案才算數。CT 把工作狀態寫進專案裡的檔案：工單、決策日誌、塔台狀態檔。任何新的 session 讀檔就能接手；檔案和記憶不一致時，以檔案為準。</p>

## 為什麼不靠對話記憶

用 AI 寫程式的人，大多遇過這幾種狀況：對話太長，AI 忘了前面講好的約定；session 一關，進度全部歸零；換一個 session，又得從頭解釋一次背景。

原因很簡單：對話記憶存在 context window 裡，而 context window 就像 RAM，有上限，也會被清空（見 [認知作業系統](/deep/principles/cognitive-os)）。要讓狀態撐過 session，只能把它寫到「磁碟」上。

CT 的做法是把專案內的檔案當成事實來源。這帶來幾個好處：

- **任何新的 AI session 讀檔就能接手**，不必從頭解釋。
- **git 會記錄所有變更**，誰在什麼時候改了什麼，查得到。
- **人可以直接讀、直接改**，不需要特殊工具。
- **不綁定特定 AI**：同一張工單，Claude Code 用 `/ct-exec`、Codex 用 `$ct-exec`（用 plugin 安裝時是 `$ct:ct-exec`）都能執行。

事實來源有兩段優先順序：

> **跨來源**：工單檔案 ＞ `sprint-status.yaml` ＞ 塔台記憶
>
> **單一檔案內**：YAML frontmatter ＞ body 元資料表

第一段處理 AI 失憶：記憶和檔案說法不同時，相信檔案。第二段處理「機器和人讀同一份檔案」的衝突，下面會談。

## 工單、決策日誌、狀態檔各記什麼

所有檔案都放在專案根目錄的 `_ct-workorders/` 底下：

| 檔案 | 記什麼 | 誰寫 |
|---|---|---|
| `T####-描述.md` | 一張工單：任務指令、驗收條件，以及 Worker 填的回報區 | 塔台建立，Worker 回報 |
| `_tower-state.md` | 塔台的跨 session 記憶：立即待辦、編號追蹤、進度快照、待處理事項等 | 塔台 |
| `_decision-log.md` | 非自明的決策與理由，倒序、只追加不改寫 | 塔台 |
| `_learnings.md` | 從工單中萃取的模式、反模式與事件 | 塔台、`ct-evolve` |
| `_tower-config.yaml` | 專案層的塔台設定 | 塔台（例如 `*config … --save project`） |

決策日誌值得多說一句。它不記「PRD 之後做架構」這種自明的決定，也不記「幫我建工單」這種明確指令；它記的是使用者的問題與塔台的判斷、流程順序的取捨、跳過或新增某個步驟的理由。價值最高的一類是**使用者糾正**：原本怎麼決定、後來改成什麼。三個月後有人問「當初為什麼這樣做」，答案就在這裡。

這些狀態檔是**塔台私有**的。Worker 只有在工單明文授權時才能改，否則一張工單的執行可能悄悄改掉整個專案的記憶。

## frontmatter 是機器的事實來源，body 表格是給人看的鏡像

v5.0.0 之前，工單狀態寫在內文的元資料表裡，`*sync`、`ct-status`、歸檔各自去解析那張表。問題是人寫的 Markdown 表格格式一定會漂移：欄名改了一個字、多一個空格、加了 emoji 前綴，機器就得容忍各種寫法。

v5.0.0 改成在檔頭放 YAML frontmatter，所有讀取端都先讀它：

| | YAML frontmatter | body 元資料表 |
|---|---|---|
| 角色 | **機器的事實來源** | 人看的鏡像，方便速查 |
| 誰讀 | `*sync`、`ct-status`、BAT、腳本 | 使用者、Worker 閱讀時 |
| 兩邊不一致時 | 以 frontmatter 為準 | `*sync` 發出 drift 警告，**不自動覆寫** |

為什麼 drift 時不直接覆寫 body？因為 body 裡可能有人特意寫的註記，機器自動覆寫，等於抹掉人的判斷。只警告、交給人處理，比較安全。

這是 CT 唯一一次升主版號。原因不是功能變多，而是**事實來源換了位置**。這個改動先在 BAT 專案試跑了 5 個 sprint，才回寫到 CT。沒有 frontmatter 的舊工單仍然讀得到，會改走舊的表格解析並發出警告，不會直接失效。

Worker 端的規則也一樣：frontmatter 是機器的事實來源，清單欄位用 YAML block list，時間戳一律帶時區、加引號，未知的狀態值不得默默當成 `PENDING`。權威定義：`ct-exec/SKILL.md` § Frontmatter Rules。

## 反序收尾：外部看到終態時，回報一定已經寫完

工單檔就是塔台和 Worker 之間的 IPC 通道。塔台、BAT 或其他工具會監看工單狀態；一旦看到 `DONE`，就會去讀回報區。

如果 Worker 先把狀態改成 `DONE`、再填回報，外面的人就可能讀到一張「狀態是 DONE、回報區卻是空的」的工單。這不是假設，v4.0 時真的發生過這種 file watch 競態。解法是**反序寫入**：讓 `DONE` 成為最後一個動作，像並行程式裡的 memory barrier 一樣。外部看到終態的那一刻，回報區保證已經完整。這就是「把檔案當 IPC」時的 happens-before 保證。

目前的收尾順序是（權威定義：`ct-exec/SKILL.md` § Phase 4: Report And Commit）：

1. 依政策先 commit 產品變更，回報區才記得到 commit hash。
2. 填回報區：結果、變更檔案、驗收證據、commit 狀態、偏差、阻礙、後續建議。
3. 回報完整之後，才更新狀態與完成時間。
4. 依政策 commit 工單檔。
5. 最後才通知塔台。

::: info 這個順序改過一次
v4.4.0 的順序是「回報區 → commit → 狀態」。v5.7.0 發現它和「通知之前工單已經 commit」的規則對不上，`ct-exec` 改成上面的順序：狀態寫完、工單 commit 之後才通知。「先寫回報、最後才讓外部看到終態」的原則沒變，變的是 commit 和通知的位置。v5.12.3 之前，`doctrine.md` § 為什麼要反序寫入？ 仍寫著 v4.4.0 的舊順序；v5.12.3 起它也改成上面的順序並引用 `ct-exec/SKILL.md` § Phase 4: Report And Commit，兩處一致。以 `ct-exec/SKILL.md` 為準。
:::

## 顯式狀態欄位：判斷成本從 O(n) 降到 O(1)

工單的 `status` 欄位不是為了好看。塔台啟動時要回答「全局進度到哪了」，如果狀態只能從內容推斷（有沒有填完成時間？回報區有沒有字？），塔台就得讀完每一張工單全文，工單一多，context 很快就被吃光。

有了顯式欄位，塔台只要讀每張工單開頭幾十行就能分類，省下的 context 留給真正需要推理的工單。這也是 frontmatter 放在檔頭的原因之一。

狀態值本身也照「這張工單現在需要誰」分成三桶：仍在流程中的（`PENDING`、`IN_PROGRESS`…）、需要塔台判斷的（未解決的 `PARTIAL`、`BLOCKED`、`FAILED`，以及已有接續工單、等塔台確認後結掉的 `INTERRUPTED`），以及已經結束的。工單也沒有「待審」這種中間態：驗收是塔台讀回報時做的事，需要獨立審查就另派一張審查工單。完整的狀態值以 `work-order-template.md` § `status` 為準，見 [工單系統](/deep/features/work-orders)。

## 證據分道：說清楚是哪一種「做完了」

「做完了」需要說清楚是**哪一種**做完。CT 把驗收證據分成獨立的通道，不混為一談：

```
source／docs │ build／test │ runtime │ deploy │ release／安裝包 │ 外部 SIT／客戶確認
```

單元測試過了，不代表 runtime 能動；部署成功，不代表客戶確認過。每條通道各自用 `PASS`／`PARTIAL`／`BLOCKED`／`FAILED` 加上具體證據回報。某個閘門跑不了，就寫出確切的阻礙，不能暗示它通過了。

這樣塔台看到 `DONE` 時，知道它涵蓋到哪一層，不會把「測試綠了」誤讀成「已經上線」。這也是「檔案即真相」的延伸：寫進回報區的不是一句「改好了」，而是可以逐條查核的證據。

## 延伸閱讀

- `control-tower-guide/references/concepts.md` § 檔案驅動設計、§ 證據分道
- `control-tower-guide/references/work-order-lifecycle.md` § 工單的兩層 metadata：frontmatter 與 body table、§ 狀態機
- `control-tower/references/doctrine.md` § 工單狀態機的設計依據、§ 為什麼要反序寫入？
- `control-tower/references/work-order-template.md` § Sprint 2 transition — YAML frontmatter SoT (v5.0.0+)
- `control-tower/references/memory-protocol.md` § _decision-log.md（決策日誌）
- `ct-exec/SKILL.md` § Frontmatter Rules、§ Phase 3: Verify、§ Phase 4: Report And Commit
- 演進史 § 5.0.0：metadata 改用 frontmatter（見 [演進史](/versions/evolution)）

<p class="ct-note">Portal 是摘要，不具權威。內容與 CT reference 有出入時，以 reference 為準。</p>
