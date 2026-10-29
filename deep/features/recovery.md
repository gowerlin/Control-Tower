---
title: 中斷、Renew 與補救收尾
description: 進度存在檔案裡，所以塔台可以被打斷：*pause／*resume 與 HOTFIX 插隊、中斷工單的接續或重派、Renew 補充指示，以及 ct-done 和重派 ct-exec 的分界。
---

# 中斷、Renew 與補救收尾

<p class="ct-lead">一句話：進度存在檔案裡，不在對話裡，所以中斷不會讓工作消失；CT 為三種中斷各準備了一條路：被插隊時用 *pause／*resume，Worker 需要新指示時用 Renew，收尾沒做完時用 ct-done 補救。</p>

開發中被插隊是常態，Worker 分頁也可能在任何時候被關掉、斷電或用完 context。CT 不試圖讓中斷不發生，而是讓每一種中斷都有固定的接續方式。這一切的前提是同一件事：塔台的進度在 `_tower-state.md` 與工單檔裡，Worker 的進度在工單的狀態欄位與回報區裡，都不只存在某個 context window。

## 中斷協議：`*pause` 與任務佇列 {#pause}

塔台正在規劃或派工時，突然有緊急任務插進來，不要跳出去自己處理，也不必擔心打斷塔台會弄丟進度。直接告訴塔台：

```
*pause 上線版本 v2.1 的登入 API 回 500，客戶在催
```

塔台收到 `*pause` 之後：

1. **凍結當前任務**：進行中的工單改為 ⏸ `PAUSED`，把暫停原因和時間記進工單檔。
2. **記錄暫停狀態**：更新 `_tower-state.md` 的暫停欄位（哪張工單、原因、時間）。v5.13.0 起，塔台每次寫 `_tower-state.md`（包括這裡和 `*resume`）都在同一次寫入更新檔頭的機器可讀摘要（下一個編號、待辦），BAT 指揮塔總覽讀的就是它。
3. **評估緊急任務**：判斷範圍、影響、要不要用不同分支，以選項式提問和你確認。
4. **派發緊急工單**：標記 🔥 `URGENT`，附分支策略建議。
5. **排入回歸佇列**：確保緊急任務結束後原任務接得回來。

任務佇列會同時顯示被暫停的工單和正在處理的緊急工單，讓你一眼看出「哪張被誰打斷、等什麼」。這個動作的命令是 `*pause`（v3.2.0 起的內建命令）。更早的版本用自由文字「⚡ 插件：」觸發；實戰補充與新手教學在 v5.12.3 之前還沿用這個說法，現在也都改成 `*pause`。

## HOTFIX 插隊與 `*resume` {#resume}

緊急工單做完之後，用 `*resume` 接回原本的工作：

```
*resume          # 自動找最近一張 PAUSED 工單
*resume T0005    # 恢復指定工單
```

`*resume` 會把 HOTFIX 工單標成 ✅ `DONE`，顯示暫停當時的上下文摘要（原因、時間、已完成的部分），把暫停的工單改回 `IN_PROGRESS`，清掉 `_tower-state.md` 的暫停紀錄。接著它還會做兩件容易被忽略的事：評估 HOTFIX 的修改會不會影響暫停中任務的設計，以及提醒你 feature 分支是不是需要 merge `main`。

緊急任務在不同分支時，建議用 git worktree 做物理隔離，兩個目錄各自開 session，互不干擾。Hotfix 很小（半小時以內）就由同一個塔台管理，在工單裡指定 worktree 路徑；複雜或時間不定時，乾脆開第二個塔台，做完再關。

## IN_PROGRESS 中斷：接續工單或重派 {#interrupted}

比起被插隊，更麻煩的是 Worker 自己中斷了：分頁被關、session 當掉、context 用完。這時工單停在 `IN_PROGRESS`，有開始時間、沒有完成時間。塔台依回報區的狀況決定：

- **回報區有部分結果**：開一張**接續工單**，新編號、參照原工單，從已完成的部分往下做。
- **回報區是空的**：給你兩個選項。一是重派原工單，把狀態重設為 `PENDING`；二是開新工單，可能調整策略或拆分。
- 原工單標記為 `INTERRUPTED`。

這就是工單粒度原則裡「可中斷可恢復」的實際用途：一張工單只交一個交付物，中斷時才有乾淨的接續點。

## Renew：不重開 session 補充指示 {#renew}

傳統流程中，塔台要補充資訊，就得讓 Worker 結束 session、修改工單、再開一個新 session。Renew 打破這個限制：

1. 塔台判斷這次要 Renew，而不是開新工單，就在工單回報區之前插入 `## 塔台補充（Renew #N）` 區段，寫明補充內容和新指示，並把 Renew 次數加一。
2. 塔台告訴你：「工單已更新，請回 Worker 分頁說**重讀工單**。」
3. 你對 Worker 說觸發詞：「重讀工單」、「renew」、「塔台有新指示」或「工單已更新」。
4. Worker 不退出 session，只讀編號最大的那個 Renew 區段，向你確認摘要後繼續，**不重置已完成的工作**。
5. 收尾時在回報區的「Renew 歷程」逐次記下每次 Renew 的摘要。

觸發者是**使用者**，Worker 不會自己「請求 Renew」。它需要更多資訊時，是回報 `BLOCKED`，或在研究型工單裡提問（yolo 下改問塔台）。Renew 主要用於研究型工單，但一般工單也能用。好處是省掉重啟 session 的成本，也保留了 Worker 已經讀過的程式碼與已經做過的分析。

| 情境 | 建議 |
|---|---|
| 方向微調、補充資訊 | Renew 同一張工單 |
| 需要完全不同的方向 | 開新工單 |
| Worker 的 context 接近上限 | 開新工單，帶前一張的結論當輸入 |
| 累計 Renew 三次以上仍不收斂 | 考慮開新工單重新聚焦 |

在 yolo 下，Renew 次數達到 `yolo_max_retries` 會觸發[斷點 B-1](./yolo#b)，提醒你該拆單了。yolo 提問等不到答覆時，塔台也是在 Renew 區段寫答覆後重派（見 [Worker 向塔台提問](./worker-questions#edge-cases)）。

## `ct-done` 和重派 `ct-exec` 的分界 {#ct-done}

這是最容易混淆的一點。兩者都能讓一張卡住的工單「動起來」，但做的是完全不同的事：

| | `ct-done` | 重派 `ct-exec` |
|---|---|---|
| 用途 | **補救收尾**：工作其實已經做完（或已確定結果），只是收尾沒做完 | **重新執行**：工作還沒做完，要再跑一次 |
| 做什麼 | 補完回報區、判定最終狀態、更新元資料、commit 工單檔、通知塔台 | 從頭走完整流程：落點檢查、執行、驗證、反序收尾 |
| 產品程式碼 | **不做新的產品工作**，除非你明確改變範圍；也不替你 commit 產品變更，只告訴你哪些看起來還沒 commit | 照工單範圍實作並 commit |
| 典型情境 | Worker session 意外關閉、AI 沒收尾、需要手動更正狀態 | `BLOCKED`／`FAILED` 後 Renew 重派、回報區是空的中斷工單 |

```
/ct-done T0001 PARTIAL
```

`ct-done` 的原則是**保留既有內容，只補缺的收尾證據**：結果摘要、最終狀態與理由、變更檔案、驗證證據與跳過的閘門、commit SHA 或沒有 commit 的理由、偏差與後續建議。它不會捏造 commit SHA；證據不足以判定最終狀態時，它會問你要哪個狀態。工單已經是最終狀態時，不經你確認不重寫。它一樣先跑[落點檢查](./landing-check)，因為它會把最終狀態寫進工單，在錯的 repo 執行等於污染一張從沒在這裡執行過的工單的紀錄。它的目的是讓工單不會變成「幽靈工單」：狀態是 `IN_PROGRESS`，卻沒有人在做。

`ct-done` 收尾的工單如果還帶著 `tower_question: open`，就照證據收成適當的狀態（通常是 `BLOCKED`）並保留題目；它不會送 `T#### 提問`，那是 `ct-exec` 執行中才會送的訊息。

## 重派前回收舊分頁 {#recycle}

在 BAT 裡，塔台要對同一張工單派一個**新的** Worker 之前（`BLOCKED`／`FAILED` 後重派、yolo 提問備援、你停掉首派的 Worker 後要求重派、啟動確認逾時後你決定重派），會先請 BAT 以 `--close-worker T#### … --delay-ms 0` 回收舊分頁。不回收的話，同一張工單會同時有兩個 Worker 分頁，新 Worker 完成後的收單回收也會因為找到兩個候選而失敗。

有三種情況**不回收**：

- 用 `ct-done` 補救派工時：保留現場，舊分頁的輸出可能正是你要看的東西。
- 研究單的 Renew 由你在原分頁說「重讀工單」繼續時：那個分頁就是要繼續的 Worker。
- 首次派工。

回收不論成功或失敗都照常派工，不會擋住重派，結果也不寫進工單。隔離工單回收時帶 `--worktree keep`，讓新 Worker 沿用原本的 worktree 與分支。

## 這些做法的共同點 {#common}

三種中斷的處理方式看起來各不相同，背後是同一個判斷：**先看檔案說了什麼，再決定要不要重做**。被插隊時，暫停原因和時間寫進工單與塔台狀態，恢復時讀回來；Worker 中斷時，回報區有沒有內容決定是接續還是重派；收尾沒做完時，`ct-done` 只補缺的證據，不重做已經做完的工作。塔台不靠記憶猜「上次做到哪裡」，也不為了保險起見全部重跑。這樣中斷的成本就只剩「讀一次檔案」，而不是「重新做一遍」。

::: tip 命令範例
本頁的命令都是摘要，完整參數以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `control-tower/references/interrupt-protocol.md` § 中斷協議、§ 任務佇列（含中斷狀態）、§ HOTFIX 完成後恢復（`*resume`）、§ Git Worktree 平行作業
- `control-tower/references/memory-protocol.md` § 機器可讀摘要（YAML frontmatter）
- `control-tower/references/work-order-system.md` § 中斷復原、§ 重派前回收舊 Worker 分頁（v5.12.0+）
- `control-tower/references/research-workorder.md` § Renew 機制（F-07）
- `ct-done/SKILL.md`（§ Workflow、§ Status Selection、§ Report Repair、§ Commit Check、§ BAT Notify）
- `control-tower-guide/references/work-order-lifecycle.md` § Session 中斷善後、§ Worker Renew 機制
- `docs/Control Tower 實戰補充/CT實戰補充（一-B）中斷處理與緊急任務.md`

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
