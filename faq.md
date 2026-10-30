---
title: 常見問題
description: CT 的常見問題：新版沒生效、Claude Code 與 Codex 的差異、卡在 IN_PROGRESS 的工單、yolo 會不會失控、一定要用 BAT 嗎、塔台為什麼不改程式碼，以及 BAT 相關問題去哪查。
---

# 常見問題

點開問題看答案。每個答案最後都附權威出處；指令的確切語法見[指令參考大全](/reference/commands)。 {.ct-lead}

## 安裝與升級 {#install}

### 升級完，塔台還是舊的行為？ {#not-effective}

::: details 開一個新的 session
正在跑的 session 在啟動時就已經載入舊版的 skill。覆寫安裝後，新版從**下一個 session** 才生效。

如果開了新 session 還是舊的：

1. 確認 8 個 skill 的版號一致：`grep -h -o "[a-z-]*-version: [0-9.]*" ~/.claude/skills/{control-tower,ct-*}/SKILL.md`（Codex 把路徑換成 `~/.codex/skills`）。用 plugin 安裝的看 `claude plugin list --json`（Codex：`codex plugin list --json`）的 `version`；這時 `skills/` 底下如果還留著手動安裝的同名 skill，會用到手動那份，見[安裝 › 用 plugin marketplace 安裝](/install#plugin)。
2. 確認 `skills/` 底下沒有備份或暫存目錄（`_backup-*`、`_staging-*`）。根層帶 `SKILL.md` 的備份會被當成另一個 skill 註冊，路由時可能載入舊版。
3. 同時在 claude.ai 上傳過 CT 時，Claude Code 會多看到一份 `anthropic-skills:` 開頭的同名 skill。兩份版號不同時可能載入舊的那份，建議擇一，見[安裝 › 同時使用 Claude Code 時](/install#claude-ai-sync)。

出處：`control-tower/references/version-governance.md` § 安裝／升級流程 Step 4；`control-tower/references/data-layer-architecture.md` § 寫入規則 Q2。
:::

### 可以只升級塔台，或只升級 Worker 嗎？ {#partial-upgrade}

::: details 不行，8 個要同一批
塔台與 Worker 之間的協定會隨版本調整。例如 v4.3 起模式由塔台在派工時以旗標傳給 Worker：舊塔台配新 Worker 時 yolo 會失效、退回 `ask`；新塔台配舊 Worker 時，舊 Worker 不認得旗標就忽略。8 個 skill 一起升級，Claude Code 與 Codex 兩端也要分別升級。

出處：CT 安裝與使用指南 § 4.1 安裝／升級（現行流程）› 發行物版面、§ 2.7 v4.3 新功能 — Worker 無狀態化 + 版號治理。
:::

### 一定要用 Claude Code 嗎？ {#claude-only}

::: details 不用
CT 的核心只靠讀寫 Markdown 檔，現行版本支援 Claude Code 與 Codex 兩種 Agent CLI。塔台和 Worker 可以用不同的那一種。

出處：CT 安裝與使用指南 § 11. FAQ、§ 4.2 Agent CLI 選擇。
:::

### 一定要用 BMad-Method 嗎？ {#bmad}

::: details 不用
CT 不內嵌任何 BMad-Method 內容。你另外裝了 `bmad-guide` skill，塔台才會依專案階段建議該走哪一套 BMad 流程；沒有它，工作流程欄位標成手動指定，塔台照常運作，也不會自己編造 BMad 的行為。

出處：`control-tower/SKILL.md` § External BMad Guide Integration；CT 安裝與使用指南 § 11. FAQ。
:::

### 依賴的 skill（bmad-guide 等）升級了，CT 要跟著改嗎？ {#deps}

::: details 通常不用
CT 是在執行時去讀 `bmad-guide` 的 reference，不把它的內容寫死在自己裡面。`bmad-guide` 更新了流程對照表，CT 自動讀到新的。只有對方的檔案格式或目錄結構發生破壞性變更時，CT 才需要配合修改。

出處：CT 安裝與使用指南 § 11. FAQ。
:::

## Claude Code 與 Codex {#agents}

### 兩者用起來差在哪？ {#claude-vs-codex}

::: details 前綴、安裝位置，以及誰決定用哪一個
| | Claude Code | Codex |
|---|---|---|
| 指令前綴 | `/control-tower`、`/ct-exec T0001` | `$control-tower`、`$ct-exec T0001` |
| 安裝位置（zip 手動安裝） | `~/.claude/skills/<skill>/` | `~/.codex/skills/<skill>/` |
| plugin 安裝（v5.14.0 起） | 照常 `/ct-exec T0001`，完整寫法 `/ct:ct-exec T0001` | 一律帶前綴 `$ct:ct-exec T0001`；接 BAT 派工要 BAT `>= 0.7.2-pre.1`，更舊的 BAT 用 zip 手動安裝 |
| 升級 | 各自獨立，升級一端不會更新另一端 | 同左 |

工單格式、回報字串、研究型工單的互動規則與 yolo 協定，兩邊一致。同一張工單 `/ct-exec` 或 `$ct-exec`（Codex 用 plugin 安裝時是 `$ct:ct-exec`）都能執行。

**誰決定 Worker 用哪一個**：在 BAT 裡，塔台派工用 `--agent default`，由 BAT 依你設定的預設 Agent 決定，也由 BAT 決定送 `/` 還是 `$`。不在 BAT 裡時，用 `CT_AGENT_CMD=claude` 或 `CT_AGENT_CMD=codex` 指定；兩個都裝了又沒指定，塔台不猜，改給你剪貼簿或文字提示。

出處：CT 安裝與使用指南 § 4.2 Agent CLI 選擇；CT Guide `references/ecosystem.md` § 三軌前綴：`*`、`/`、`$`。
:::

### `*evolve` 和 `/ct-evolve` 有什麼不同？ {#star-vs-slash}

::: details 差在哪個角色裡執行
`*` 開頭的是塔台內建命令，只在進行中的塔台 session 裡有意義，處理完繼續塔台的工作。`/ct-evolve`（Codex：`$ct-evolve`）是獨立的 skill，在它自己的 session 裡以它自己的角色執行。`*insights` 與 `/ct-insights`、`*fieldguide` 與 `/ct-fieldguide`、`*help` 與 `/ct-help` 也是同樣的關係。

出處：CT Guide `references/ecosystem.md` § 三軌前綴：`*`、`/`、`$`；`control-tower/references/tower-config.md` § 與 `/ct-help` 的差異。
:::

## 工單卡住了 {#stuck}

### 工單一直是 `IN_PROGRESS`，該用 `ct-done` 還是重派 `ct-exec`？ {#in-progress}

::: details 看工作做完了沒有
先跑 `/ct-status T0042` 看狀態與回報區。

| 情況 | 用什麼 |
|---|---|
| 工作做完了，只是 Worker 被關掉、漏了收尾，或要更正狀態 | `/ct-done T0042 [狀態]`：補完回報區與收尾，**不做新的產品工作** |
| 工作還沒做完，要接著做 | 在新的 session 跑 `/ct-exec T0042`：它會保留原本的開工紀錄，記成接續執行 |
| 不確定、或回報區是空的 | 回塔台說明情況，由塔台決定：回報區有部分結果就開接續工單；空的就重派原工單或換策略開新工單，原工單標成 `INTERRUPTED` |

兩者都會先做落點檢查。`ct-done` 會 commit 工單檔本身，但**不替你 commit 產品改動**，只告訴你哪些看起來還沒 commit。在 BAT 裡由塔台重派時，塔台會先回收舊的 Worker 分頁。

出處：`ct-done/SKILL.md` § Workflow、§ Commit Check；`ct-help/SKILL.md` § Typical Workflow；`control-tower/references/work-order-system.md` § 中斷復原。
:::

### `PARTIAL` 會一直掛著嗎？ {#partial}

::: details 不會，塔台一裁示就收尾
`PARTIAL` 是時間點上的狀態。Worker 照停止條件回報 `PARTIAL` 是對的，收尾是塔台的事：v5.13.0 起，塔台一決定剩下的部分怎麼處理（另開接手單，或判定不需再做），**當下**就在原工單文末補〈塔台收尾補記〉並改成 `DONE`，不等到歸檔；接手單完成後再回頭確認。剩下的部分被設計方向淘汰時，改成 `ABANDONED` 這類退役狀態。只有真的在等外部條件（廠商、客戶、環境、還沒給的輸入）才保留 `PARTIAL` 或改 `BLOCKED`。以前漏收的，用 `ct-done` 補救收尾時也會補上註記、改成 `DONE`。

出處：`control-tower/references/work-order-system.md` § PARTIAL 當下收尾（含 resolved `PARTIAL` 補正）；`ct-done/SKILL.md` § Status Selection。
:::

### 塔台 session 斷了怎麼辦？ {#tower-lost}

::: details 重新啟動塔台
重新輸入 `/control-tower`。塔台會先讀 `_ct-workorders/_tower-state.md`，從上次的進度接著走；狀態檔不存在或環境快照太舊時，才做一次完整掃描（也可以手動 `*rescan`）。

出處：`control-tower/SKILL.md` § Startup Protocol；CT 安裝與使用指南 § 11. FAQ。
:::

## 自動化 {#automation}

### `yolo` 會不會失控？ {#yolo}

::: details 有五個斷點，你也能隨時喊停
`yolo` 是 `on` 的超集：Worker 自動送出回報，塔台自己決定下一張。它有五個一定會停下來的斷點：

- **A**：Worker 送回的訊息不是約定的回報字串。
- **B**：同一張工單 Renew 太多次，或連續好幾張 `FAILED`（次數由 `yolo_max_retries` 設定，預設 3）。
- **C**：Worker 建議做的事超出這次規劃的範圍。
- **D**：有 Worker 停在畫面上等你回答（塔台只告訴你是哪個分頁，不替你按鍵）。
- **E**：隔離分支要合併回主線之前。

另外，Worker 在 yolo 下有問題時改問塔台：範圍內的技術選擇由塔台代決，**範圍變更、刪除或不可逆的操作、對外發布、需要你偏好的選擇**，塔台會先問你。你隨時可以在塔台輸入 `停`、`stop` 或 `abort` 中斷自動派工，這不算斷點，也不佔重試次數。

出處：`control-tower/references/yolo-mode.md` § 斷點判準（A / B / C / D / E）、§ 使用者中斷（非斷點）、§ Worker 向塔台提問（v5.5.0+）› 塔台端。
:::

### 一定要用 BAT 嗎？ {#need-bat}

::: details 不用，塔台會一路降級
派工時塔台依環境往下降級：BAT 內部終端 → 開新終端分頁 → 寫入剪貼簿 → 文字提示。文字提示永遠會顯示，最差的情況就是你自己開一個 session、貼上 `/ct-exec T0042`，做完把「T0042 完成」帶回塔台。

少了 BAT，你會少掉的是：自動開 Worker 分頁、Worker 做完自動通知塔台、yolo 的自動送出、Worker 啟動確認、結構化的提問通道、worktree 隔離派工與分頁回收。工單、狀態、決策與學習這些核心功能都不受影響。

出處：`control-tower/references/auto-session.md` § 降級鏈、§ 派發後行為（依 `auto-session` 設定）。
:::

### bash 裡看不到 `BAT_*` 環境變數，是不是不在 BAT 裡？ {#bat-env}

::: details 先用 PowerShell 複查
在 Windows 上，bash 這類輔助 shell 有時看不到 BAT 注入的變數，但原生 PowerShell 看得到。不要直接判定為不在 BAT 裡，先用 `Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object` 複查（只列名稱、不輸出值；`BAT_REMOTE_TOKEN` 只記「已設定」）；PowerShell 看得到、bash 看不到，是 shell 之間的可見性落差，不是非 BAT 環境。

出處：`control-tower/SKILL.md` § BAT And Auto-Session；`ct-help/SKILL.md` § BAT And YOLO。
:::

## 塔台的分工 {#tower}

### 塔台為什麼不幫我改程式碼？ {#no-code}

::: details 因為它要留著腦袋看全局
塔台不是「不看程式碼的笨 AI」，是「派人去看程式碼、只收結論的主管」。原因有三個：

1. **Context window 是有限資源**。塔台讀了 500 行程式碼，這 500 行就一直佔著位置，擠掉專案目標、進度與已經做過的決定。
2. **分開才能做更多輪**。塔台的壽命取決於 context 有多乾淨：分開之後，一個塔台 session 撐得過一整個 Sprint 的工單，每個 Worker 則是一張工單一個乾淨的 session，做完就丟。
3. **結論比原始碼有價值**。塔台需要的是「做了什麼、證據是什麼、卡在哪」，不是程式碼本身。

所以你把程式碼貼進塔台，正確的做法是讓塔台開一張分析工單；塔台的回覆裡出現程式碼片段，就是越界了。唯一的例外是單一模組內、不涉及邏輯的小變動（例如修錯字），塔台可以直接處理，commit 行為依 `auto_commit`。

出處：〈CT 實戰補充（一-A）為什麼塔台不讀程式碼〉§ 為什麼要這樣設計、§ 一句話總結；`control-tower/SKILL.md` § Hard Boundaries。
:::

### 這樣不是更浪費 token 嗎？ {#tokens}

::: details 真正浪費的是另外幾件事
多開一個 Worker session 確實有成本，但它換來的是塔台保持乾淨、每個 Worker 天生就是一次性的。真正浪費 token 的是這三件事：

1. 在被污染的 context 裡反覆修同一個 bug，每一輪都帶著前面的垃圾。
2. 重開 session 後從頭解釋背景，因為沒有工單紀錄。
3. 讓塔台讀了程式碼，context 髒了，後面所有決定的品質都跟著下降。

就像你不會因為打電話要花電話費，就讓總經理親自去每個部門跑腿。

出處：〈CT 實戰補充（一-A）為什麼塔台不讀程式碼〉§「這樣不是更浪費 token 嗎？」。
:::

### 為什麼找不到 `*dispatch`？ {#no-dispatch}

::: details 派工不是一個命令
CT 沒有 `*dispatch`。派工是開單之後的一個步驟：塔台依 `auto-session` 設定自動派，或給你指令讓你自己開。舊版的 `*help roles`（職責速查卡）也已在 v5.0.3 刪除。完整的現行命令見[指令參考大全](/reference/commands)。

出處：`control-tower/SKILL.md` § Built-In Commands；CT 安裝與使用指南 § 14. 命令速查表（v5.14.2）。
:::

## BAT 相關問題 {#bat}

分頁、派工通知、狀態偵測、worktree、遠端開發這些屬於執行環境的問題，請看 BAT 站：

- <BatLink path="faq#control-tower">BAT 站 FAQ：Control Tower</BatLink>
- <BatLink path="remote/#tower">BAT 站：在遠端用塔台與 Worker</BatLink>

## 延伸閱讀 {#further}

- CT 安裝與使用指南 § 11. FAQ
- `ct-help/SKILL.md`（Core Model、Command Families、Typical Workflow、Status Words、BAT And YOLO）
- `control-tower/references/auto-session.md` § 降級鏈
- 〈CT 實戰補充（一-A）為什麼塔台不讀程式碼〉§ 一句話總結
- `control-tower/references/yolo-mode.md` § 斷點判準（A / B / C / D / E）

Portal 是摘要，不具權威；與 reference 有出入時，以 reference 為準。
