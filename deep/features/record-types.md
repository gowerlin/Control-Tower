---
title: BUG／PLAN／EXP 與研究型工單
description: 標準工單之外的三種單據各有自己的狀態機，彼此以文字引用串起來；研究型工單允許 Worker 互動，收尾必須交出可決策的結論。
---

# BUG／PLAN／EXP 與研究型工單

<p class="ct-lead">一句話：工單（T####）負責「做一件事」，但 bug 要驗證才能關、想法要等評估才做、實驗的產出是知識而不是功能；所以 CT 另外提供 BUG、PLAN、EXP 三種單據和研究型工單，各自用最適合的狀態機，預設全部關閉。</p>

## 為什麼不只用一種工單 {#why}

標準工單的狀態機是為「執行一個交付物」設計的：`PENDING → IN_PROGRESS → DONE`，中間可能 `PARTIAL`、`BLOCKED`、`FAILED`。可是開發中還有三類事情，硬塞進這個狀態機會失真：

- **bug**：Worker 回報「修好了」只代表實作完成，還沒證明真的修好。若用 `DONE` 表示，修了但沒修好的 bug 就會靜靜地被關掉。
- **想法與規劃**：一個想法可能要很久之後才做，也可能永遠不做；它做的時候通常會拆成好幾張工單。它需要的是「還在想、已規劃、執行中、完成或放棄」這種長週期狀態。
- **實驗**：結果不確定，而且「這條路不通」本身就是有價值的結論。用 `FAILED` 表示一個證明了某方案不可行的實驗，等於把知識記成失敗。

所以 CT 在標準工單之外加了三種單據。它們**預設關閉**，用 `*config` 個別啟用：

| 類型 | 檔名格式 | 用途 | 啟用設定 |
|---|---|---|---|
| 工單 | `T####-description.md` | 標準任務 | 永遠啟用 |
| BUG | `BUG-###-description.md` | Bug 追蹤 | `enable_bug_tracking: true` |
| PLAN | `PLAN-###-description.md` | 規劃與想法 | `enable_plan_tracking: true` |
| EXP | `EXP-[TOPIC]-###-description.md` | 實驗性工作 | `enable_experiments: true` |

BUG 和 PLAN 是三位數流水號；EXP 每個 TOPIC 各自從 001 計數，TOPIC 是 2–10 個大寫英文字母或數字，例如 `EXP-AUTH-001-jwt-vs-session.md`。各類型的計數器都記在 `_tower-state.md`，`*sync` 時會檢查計數器與實際檔案是否一致，修正漂移。這些單據的編號規則和工單 ID 的權威正則是分開的，彼此不套用。

## BUG：修好和關閉是兩件事 {#bug}

```
OPEN → FIXING → FIXED → VERIFY → CLOSED
                  └ 驗證失敗 → FIXING
任何階段 → WONTFIX
```

`FIXED` 和 `CLOSED` 分開，就是為了擋住「修了但沒真的修好」：修復工單回報後只到 `FIXED`，要經過驗證才能 `CLOSED`；驗證失敗就回到 `FIXING`。`WONTFIX` 任何階段都可以標記，但要記錄原因。

建立 BUG 單時，塔台會先做需求對齊，用選項式提問釐清三件事：嚴重度（🔴 阻塞功能或資料損失、🟡 功能異常但有替代方案、🟢 外觀瑕疵）、能不能重現、有沒有 workaround。最少必填的只有標題、嚴重度和「預期 vs 實際」的現象描述。建立後你可以選擇立即派修復工單、先記錄，或標記不修。

修復本身仍然由標準工單執行，工單裡引用 BUG 編號。修復完成後塔台把 BUG 改為 `FIXED`，並詢問要不要派驗證工單；高嚴重度建議用獨立的驗證工單。`*sync` 會掃描所有 BUG 單，重建 `_bug-tracker.md` 索引。

### 結案判準與 `closed_reason`（v5.13.0） {#bug-closing}

未結清單只該放還要做的事。留著已經修好、過時或不打算修的 BUG，會讓人誤判工作量與風險。v5.13.0 寫下一張判準表，平常處理 BUG、逐張核對舊 BUG 都照它決定落在哪個狀態：

| 情況 | 狀態 | 要寫的 |
|---|---|---|
| 現行程式已經修好 | `FIXED` | 修正的 commit 或 `檔案:行` |
| 前提錯了、設計本來如此 | `CLOSED` | `closed_reason: not_a_defect`，加上當初為什麼以為是 BUG |
| 屬實但不修（你接受、交付版走不到） | `WONTFIX` | 寫進交付文件的已知限制 |
| 過時：功能退場、被別張單取代或重複、規劃改了 | `CLOSED` | `closed_reason: superseded`／`duplicate`／`obsolete`，加上被誰取代或為什麼過時 |
| 不是我方的責任 | `CLOSED` | `closed_reason: external`，加上已經告知誰、何時 |
| 仍然成立，但優先度低、短期不做 | `CLOSED` | `closed_reason: deferred`；列進 `_backlog.md` 的〈後續待辦〉，要做時重開成 `OPEN` |
| 仍然成立，而且要做 | `OPEN` | 標「上線前」或「後續」，重新核定嚴重度 |

- **證據不足就維持 `OPEN`**，不猜。核對時看現行程式碼和後續的工單、決策，不只看單裡寫了什麼。
- **為什麼不新增狀態值**：BUG 的六個狀態和 BAT 一對一，多一個值 BAT 就認不得。結案原因因此放在選填欄位 `closed_reason`（本文也寫一行「結案原因」）；BAT 不讀這個欄位，面板不受影響。一般驗收通過的 `CLOSED` 不必填。
- **延後的 BUG 留在熱區**，不列為歸檔候選，〈後續待辦〉才完整；重開時改回 `OPEN`，拿掉 `closed_reason` 與 `closed_at`。
- **清理提示**：`*sync` 與 `*insights` 在未結 BUG 多於 `bug_review_open_threshold` 張（預設 20），或有 BUG 超過 `bug_review_stale_days` 天（預設 30）沒更新時，印一行提示，建議照上表逐張核對，可以分批派唯讀工單。改不改狀態由塔台依核對結果決定；改了就同一批重建 `_bug-tracker.md`，因為 BAT 看板讀的是索引。

## PLAN：一個想法到多張工單 {#plan}

```
IDEA → PLANNED → IN_PROGRESS → DONE
                            └→ DROPPED
```

PLAN 用來記錄想法、規劃與技術評估。最少必填的是標題和一句話的動機，建立時塔台問優先級（近期必須、中期規劃、長期想法）和類型（功能想法、技術改善、架構調整）。

決定實施時，塔台把 PLAN 改為 `IN_PROGRESS`，從描述拆出一或多張標準工單，每張都引用 PLAN 編號；所有關聯工單完成後，PLAN 才改為 `DONE`。評估後決定不做就 `DROPPED`，並記下原因。`*sync` 會重建 `_backlog.md`，把進行中的、已完成的、已放棄的分區列出。

PLAN 也是 yolo 的單位：塔台在 yolo 下派「下一張」，依據的就是當前 PLAN 對應研究工單的拆單表（見 [yolo 與斷點](./yolo#next)）；Worker 建議跨出 PLAN 範圍時會觸發斷點 C。

## EXP：產出是知識 {#exp}

```
EXPLORING → CONCLUDED
         └→ ABANDONED
```

EXP 沒有「失敗」狀態。實驗的產出是**知識**而不是功能，證明某個方案不可行，同樣是 `CONCLUDED`；只有實驗無法繼續或已失去意義時才是 `ABANDONED`。建立 EXP 時要確認 TOPIC 名稱和一句話的實驗假設。

EXP 建議搭配 git worktree，讓失敗的實驗可以零污染丟棄。塔台會問執行方式：在 worktree 中實驗（推薦）、在目前分支做小規模探索，或先記錄。選 worktree 時，塔台提供 `git worktree add ../<repo>-<topic> -b exp/<topic>` 這類指令由你執行。實驗成功就提交、開 PR 回主分支、合併後清理；放棄就直接移除 worktree 並刪掉分支，主線完全不受影響。EXP 不計入 sprint 進度，在 `*sync` 摘要裡單獨列成「🧪 實驗分支」區塊。

## 跨類型關聯 {#relations}

單據之間的關聯用**文字引用**，不另做自動連結系統，保持簡單：

| 關聯 | 說明 |
|---|---|
| BUG → T#### | BUG 的修復工單 |
| PLAN → T#### | PLAN 拆出的實作工單 |
| EXP → T#### | 實驗成功後的正式實作工單 |
| T#### → BUG | 工單執行中發現的 bug |
| EXP → PLAN | 實驗結論轉成正式規劃 |

寫法就是在相關欄位引用編號，例如「修復工單：T0073」「來源 BUG：BUG-001」。不做自動連結的理由是成本：引用寫在單據本文裡，任何 AI 或人打開檔案都看得懂，不需要額外的索引或同步機制；要追一條關聯鏈時，順著編號一張一張讀下去就好。真正需要整體視圖的地方，例如 BUG 清單與待辦清單，由 `*sync` 從單據重建索引，索引壞了也能隨時重建。

## 研究型工單：雙向、而且要能決策 {#research}

研究型工單（`type: research`）不是另一種單據，而是標準工單的一種類型，用來處理「還不知道該做什麼」的任務。塔台在這幾種情況會主動建議開研究單：根因不明、需要多輪互動確認方向、技術方向待定、問題描述還太模糊。

| | 傳統工單 | 研究型工單 |
|---|---|---|
| 指令方向 | 塔台 → Worker（單向） | 塔台 ↔ Worker（雙向） |
| Worker 能否主動提問 | 不行，只執行 | 可以，漸進收窄範圍 |
| 收尾內容 | 產出摘要＋遭遇問題 | 加上互動紀錄、調查結論、建議方向 |
| 結論要求 | 完成／未完成 | 必須**可決策** |

**互動由誰決定**依序看：`CT_MODE=yolo` 時一律不問使用者，改問塔台；否則看派工時傳入的 `CT_INTERACTIVE`（`1` 允許、`0` 禁止）；沒有這個變數時才看工單元資料的互動設定。Worker 不讀設定檔決定要不要互動，這是派工時決定的 runtime 參數。

提問遵循「漸進收窄」：第一輪確認大方向（範圍、模組、預期），第二輪問技術細節（限制、效能、相容性），之後才提出候選方案請你確認。每輪最多 `research_max_questions` 題，選項式並以「其他：________」兜底，所有問答都以 `[HH:MM] Q: … → A: … → Action: …` 的格式記進互動紀錄。

**結論必須可決策**。「我查了一些程式碼，發現了一些可能的問題，需要進一步研究」不合格；合格的結論要寫出根因或發現、幾個選項各自的代價、推薦哪一個和理由、殘餘風險，以及建議的下一張工單。

塔台收到研究單回報後：結論清楚而且問題已解決，就標 `DONE` 並把結論記進決策日誌；結論清楚但還要動手，就派實作工單，並在「輸入上下文」引用「基於某研究工單結論，方案 X」；結論不清楚，就 Renew 同一張研究單，補充新的調查方向（見 [中斷、Renew 與補救收尾](./recovery#renew)）。

## 沒啟用時會怎樣 {#disabled}

對應的設定是 `false` 時，回報 bug、提出想法、想做實驗都照常用標準工單處理，不建立 BUG、PLAN、EXP 單；`*sync` 也忽略這些檔案。但如果 `_ct-workorders/` 裡已經有這類檔案（例如從別的專案複製過來），`*sync` 會在摘要裡提示「偵測到 N 張單據但功能未啟用」，建議你啟用。不啟用不會讓既有流程有任何改變。

::: tip 命令範例
本頁的狀態機與指令都是摘要，完整參數以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `control-tower/references/bug-plan-system.md` § 類型總覽、§ 索引格式、§ 編號管理、§ BUG 單據（§ 結案判準、§ 未結 BUG 清理提示）、§ PLAN 單據、§ EXP 實驗單據、§ 跨類型關聯、§ 未啟用時的行為
- `control-tower/references/research-workorder.md` § 觸發條件、§ Worker 行為規格（research 類型專屬）、§ 塔台決策流程
- `control-tower-guide/references/work-order-lifecycle.md` § BUG 生命週期、§ PLAN 生命週期、§ EXP 生命週期、§ 研究型工單
- `control-tower/references/work-order-template.md` § BUG 單模板、§ PLAN 單模板、§ EXP 實驗單模板、§ 研究型工單模板

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
