---
title: worktree 隔離與三種合併模式
description: 隔離工單在獨立 worktree 與分支上工作；合併由塔台決定，判準全過才直接合併，否則派合併工單，推進 main 前一律經過 SHA 比對與斷點 E。
---

# worktree 隔離與三種合併模式

<p class="ct-lead">一句話：隔離讓並行的 Worker 各自擁有一個工作樹，成果是一條從已知 base 開出的分支；合併不交給 BAT，而是由塔台依五條判準決定自己合或派合併工單，推進 main 之前一定要證明「合進去的就是驗收過的那一版」。</p>

## 什麼時候用 `--isolation worktree` {#when}

非隔離的工單直接在主 checkout 工作，一次只跑一張時沒有問題。可是一旦同時派出兩張會動產品檔的工單，兩個 Worker 改的就是**同一個工作樹**：一個在跑測試，另一個改到一半的檔案也在裡面；一個 commit 時，可能把另一個的變更一起帶進去。`affects_files` 的 overlap check 能擋住「改同一個檔」，擋不住「共用一個工作樹」。

工單 frontmatter 寫 `isolation: worktree` 時，塔台派工加 `--isolation worktree`（需要 BAT `>= 0.7.0-pre.2`）。BAT 會在主 checkout 上層的 `.bat-worktrees/<repo 目錄名>/<T####>` 建一個 worktree 與分支 `ct/<T####>`，base 是主 checkout 當下的 `HEAD`。好處有兩個：並行不互相污染，以及合併可追溯，驗收跑在哪個 SHA、合併的是哪個 SHA 都有證據。

**預設不隔離**，因為隔離有成本：多一個 worktree 要裝依賴，多一段合併流程。適合並行、會大量改產品檔、希望驗收後再進 `main` 的工單；不適合只改 `_ct-workorders/` 或文件的小單、研究型工單，以及要在主 checkout 操作執行環境的工單（安裝、部署）。

隔離派工失敗時，塔台**不會自動改成非隔離**重派。BAT 回 exit `7`（`WORKTREE_FAILED`，例如位置被佔用、分支已在別處 checkout），或 BAT 太舊不認得參數，塔台都停下來告訴你原因，由你決定排除原因後重派，或明確同意改成非隔離。非隔離就是讓 Worker 直接改主 checkout，那正是你選擇隔離時想避免的事。yolo 下也一樣暫停。

## Worker 在 worktree 裡的規則 {#worker-rules}

Worker 從環境變數 `CT_HOME` 知道自己在 worktree 裡，這個變數由 BAT 在派工時注入，Worker 不自己推測。同時注入的還有 `CT_WORKTREE`、`CT_WORKTREE_BRANCH` 與 `CT_WORKTREE_BASE`。和平常不同的只有幾件事：

| | 規則 | 為什麼 |
|---|---|---|
| 工單在哪讀寫 | 一律在**主 checkout** 的 `$CT_HOME/_ct-workorders/`；worktree 裡那份是唯讀副本，不改、不 stage | 塔台讀的是主 checkout；寫在 worktree 裡塔台看不到，合併時還會和塔台的記帳衝突 |
| 產品變更 commit 到哪 | worktree 的分支 `ct/T####`；不切分支、不 merge、不 rebase、不 push | 分支就是交付物，合併是塔台的決定 |
| 收工前 | worktree 必須全部 commit，即使 commit 政策本來可以不 commit | 沒 commit 的不在分支上，合併不到；髒的 worktree BAT 也不會清掉 |
| 落點檢查 | C-0 拿工單的 `repo` 和 `CT_HOME` 的目錄名比，不和 worktree 的目錄名比 | worktree 目錄叫 `T####`，不是 repo 名 |
| 回報區 | 多一段隔離分支證據：`branch`、`base_sha`、`validated_sha`、`head_sha` | 見下方 SHA 比對 |

BAT 不替 worktree 安裝依賴，Worker 要照專案文件自己裝；專案沒寫就在回報區記下來。收尾仍是反序，只是分在兩個地方：先在 worktree commit 產品變更、記下 SHA，再到主 checkout 填回報、改最終狀態、commit 工單，最後才通知塔台。

`validated_sha`（跑驗收那一刻的 `HEAD`）和 `head_sha`（最後一次產品 commit 後的 `HEAD`）必須相等，才能說「合併進 `main` 的就是驗收過的那一版」。驗收後又 commit 了東西，Worker 要說明為什麼不需要重驗，或重跑驗收。

## 為什麼合併交給工單，不交給 BAT {#why-workorder}

BAT 只提供**唯讀信號**：`--worktree-status` 回報分支的 ahead／behind、變更檔、範圍外檔案、預測衝突與髒檔，但不 checkout、不 merge、不 commit。合併需要的東西 BAT 都沒有：判斷衝突雙方的意圖、跑專案的完整驗收、遇到範圍外檔案時停下來問人。這些正是工單流程本來就有的能力。讓 BAT 變成合併引擎，等於在工單流程之外另開一條沒有驗收也沒有回報的路。

## 直接合併的五條判準與三種模式 {#modes}

<MergeModes />

五條判準可以濃縮成一句話：**合併結果的產品檔必須和 Worker 驗收過的那一版完全相同，而且沒有任何東西需要人判斷。**

第 1 條採放寬版：`main` 沒有前進，**或只在 `_ct-workorders/**` 底下前進**也算通過。原因很實際，塔台每收一張單都會 commit 工單記帳，`main` 幾乎一定會前進；嚴格版會讓直接合併幾乎永遠不成立。而只動工單目錄的前進不碰產品檔，合併後的產品樹仍等於驗收過的那一版，不必重跑驗收。

判準的資料取不到（BAT 查不到、git 也算不出來），或欄位是 `null`，一律算**不通過**。資料缺漏時寧可派合併工單多跑一次驗收，也不靠猜測推進 `main`。沒填 `affects_files` 的隔離工單，範圍外檔案無從計算，所以一律走合併工單。

模式由**塔台**決定，寫在合併工單的 `merge_mode`，Worker 不得自己改：

- **① 機械合併**：五條全部成立，塔台自己做，不派單。途中 `--no-ff` 出現衝突就 `merge --abort`，改派模式 ②。
- **② 衝突解決**：Worker 在整合 worktree 以 `--no-ff` 合併、解衝突、跑完整驗收，逐檔寫下 `main` 那邊與工單分支各自為什麼這樣改、怎麼解、為什麼。發現情況超出解衝突（例如合併後邏輯必須改寫），回報 `PARTIAL` 並**建議**改 ③，不自行升級，因為換模式等於換一種工作。
- **③ 等價移植**：分支太舊、程式碼已重構，或來源是 EXP／上游成果時，Worker 以原工單的目標與驗收條件為規格，從目前的 `main` 重新實作，附「原改動 → 新位置」對照表，並逐條重驗原工單的驗收條件。

## 共同護欄 {#guardrails}

三種模式共用一組護欄：

- **只在整合 worktree 合併**。不在主 checkout 做，也不在被合併工單的 worktree 做。整合 worktree 長期保留（避免每次重裝依賴），每次合併前必須乾淨，再從 `base_main_sha` 開一條新的合併分支 `ct-merge/T####`；分支已存在就停下回報，不得覆寫。
- **一律 `--no-ff`**，commit 訊息含被合併工單的 ID。即使 `main` 完全沒前進，也不走「直接 ff 工單分支」的捷徑。
- **`main` 只用 `--ff-only` 推進**，在主 checkout 執行。
- 不 push、不 `--force`、不 `reset --hard`、不 rebase `main`。
- 主 checkout 有與合併檔重疊的未提交變更時，`--ff-only` 會被 git 拒絕，這是正常保護：告訴你哪些檔案擋住了，請你處理後再 ff，不 stash、不丟棄你的變更。
- Windows 上的 git 指令加 `-c core.longpaths=true`，否則長路徑檔可能被看成已刪除。

## 收單 SHA 比對五步 {#sha-check}

合併工單回報後（模式 ① 則是塔台自己合完之後），推進 `main` 之前，塔台依序確認：

1. `base_main_sha` 是派合併工單（或開始直接合併）當下的 `main`。
2. `head_sha` 是原工單 Worker 驗收時的 SHA，而且等於目前的 `ct/T####`。
3. merge commit 的 parent1 是 ff 前的 `main`，parent2 是第 2 步的 SHA。模式 ③ 沒有這種 merge commit，改為確認整合分支是從 `base_main_sha` 開出，並以對照表與逐條重驗取代第 2 步。
4. ff 之後的 `main` 等於 merge commit（模式 ③ 為整合分支的 head）。
5. 合併期間 `main` 又前進了：多出來的只有 `_ct-workorders/**`，就在整合分支再 `--no-ff` 合一次 `main` 後 ff；否則 Renew 合併工單重做（模式 ① 改派模式 ②）。

執行順序是先做 1～3 步，需要時做第 5 步，接著經過斷點 E，然後 `--ff-only`，最後做第 4 步。任一步不成立就不 ff，回報給你。

## 斷點 E 與合併後清理 {#breakpoint-e}

`--ff-only` 之前一律經過 [斷點 E](./yolo#e)：非 yolo 一律暫停確認；yolo 下模式 ① 在 ff 前再確認判準仍成立就自動通過，模式 ② 要驗收全綠且沒有範圍外檔案才自動，模式 ③ 一律暫停。

合併完成後：

- 被合併工單的 worktree 以 `--close-worker <工單 ID> … --worktree remove` 回收；分頁早已關閉時由塔台手動 `git worktree remove`（不加 `--force`）。worktree 有未提交或未追蹤的變更就不刪，告訴你。
- **合併前絕對不用 `--worktree archive`**，它會把分支改名為 `ct-archive/T####`。
- 分支 `ct/T####` 與 `ct-merge/T####` 保留到你同意刪除，刪除用 `git branch -d`（不用 `-D`）。
- 整合 worktree 本身保留，但 ff 成功後要 `switch --detach` 離開合併分支，否則之後你同意刪分支時會因為分支仍被 checkout 而刪不掉。

收單時的完整順序：

```
Worker 回報 DONE（含隔離分支證據）
  → 查 --worktree-status（舊 BAT 要在回收分頁前查；查不到改用 git）
  → 回收 Worker 分頁：--close-worker … --worktree keep
  → 五條判準全部成立？ 是 → 模式 ①：塔台在整合 worktree 合併
                      否 → 派合併工單（模式 ② 或 ③）
  → 收單 SHA 比對 → 斷點 E → main --ff-only → 清理
```

BAT 這一端的 worktree 建立、合併前狀態與回收選項，見 <BatLink path="control-tower#parallel">BAT 站：平行與 worktree 隔離</BatLink>。

::: tip 命令範例
本頁的命令都是摘要，`--worktree-status` 欄位、exit code 與 git 指令細節以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `control-tower/references/merge-workorder.md` § 適用範圍、§ 三種模式、§ 共同護欄、§ 塔台直接合併判準、§ 直接合併的做法、§ 合併判準資料來源、§ 收單 SHA 比對五步、§ 合併完成後清理、§ 斷點 E
- `control-tower/references/auto-session.md` § BAT 內部終端路由（Better Agent Terminal）› worktree 隔離派工（`--isolation worktree`，v5.3.0+）
- `control-tower/references/work-order-template.md` § `isolation`（v5.3.0+，選用）、§ 合併工單模板（v5.3.0+）
- `ct-exec/SKILL.md` § Worktree Isolation (`CT_HOME`, v5.3.0+)
- `control-tower-guide/references/work-order-lifecycle.md` § worktree 隔離與合併工單（v5.3.0）

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
