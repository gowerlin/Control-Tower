---
title: 可逆與不可逆的界線
description: 可逆的事放手，不可逆的事要明文授權或經過斷點：塔台的指令白名單、push 與安裝規則、Layer 1 保護、合併斷點，以及 Workflow 與匯入的硬限制。
---

# 可逆與不可逆的界線

<p class="ct-lead">可逆的事放手讓 AI 做；不可逆或對外的事，要有寫在工單裡的明文授權，或停在一個斷點等人確認。CT 的各種安全規則，幾乎都是這一條原則的展開。</p>

## 原則：先問「做錯了能不能退回來」

AI 做錯事的代價差很多。改錯一個檔案，`git` 就能還原；工單寫錯，重派一張就好。但 push 到遠端、刪掉分支、覆寫已安裝的 skill、把未經驗證的結果推進 `main`，做了就很難收回，或者別人已經看到了。

CT 不試圖讓 AI 「永遠不犯錯」，而是把動作分成兩類：

- **可逆的**：在工單範圍內放手做，事後靠回報區的證據檢查。
- **不可逆或對外的**：必須有**寫在工單裡的明文授權**，或經過一個**斷點**，由人確認後才做。

塔台的 Hard Boundaries 第 4 條把這件事寫得很直接：沒有工單或使用者的明文授權，不 push、不 force-push、不 reset hard、不刪分支、不還原使用者的修改（`control-tower/SKILL.md` § Hard Boundaries）。下面各節是這條原則在不同地方的樣子。

## 塔台的指令白名單

塔台原則上不跑任何 shell 指令。唯一的例外是一份**白名單**，裡面只有派工需要的動作：開新的終端分頁或 CLI session、把派工指令寫進剪貼簿、透過 BAT 開 Worker 分頁、回收 Worker 分頁、查詢隔離 Worker 的狀態、答覆 Worker 的提問、宣告塔台分頁的角色，以及合併判準全部成立時的直接合併。白名單以外的操作一律禁止。

白名單還附帶防注入規則：

- 指令參數只能是工單指令，例如 `/ct-exec T####`。
- 工單編號必須符合唯一的權威正則，不符合就**直接拒絕**，不正規化、不截斷、不修補。
- `--mode` 只收 `yolo`／`ask`／`off`／`on`；每個旗標的值域與不得同時使用的組合都有明文規定。
- BAT 的範圍權杖不得輸出、記錄，也不得放進參數；需要記錄時只寫「已設定」。

權威定義：`auto-session.md` § 安全邊界。白名單的作用不只是擋掉危險指令，也讓「塔台做了什麼」可以預期：看白名單就知道塔台最多能做到哪裡。

## 不主動 push、不主動 tag

發版流程的最後一步寫得很清楚：commit、tag、同步已安裝 skill 的時機，由使用者或正式的 release 流程決定，**塔台和 Worker 都不主動 push**（`version-governance.md` § 發布流程）。

Worker 端的規則一樣：除非工單明文寫出使用者授權 push，否則不 push；commit 時只納入本工單的檔案，不誤帶別人的未提交變更。push 是把東西送到別人看得到的地方，可能已經被快取或被別人拉走，就算之後刪掉也收不回來。

## 安裝與升級：要授權、先備份、先複製驗證再替換

把 skill 裝進 `~/.claude/skills/` 或 `~/.codex/skills/`，是改動所有 session 都會載入的東西。CT 把它當成最需要小心的動作：

1. **授權寫在工單裡**，而且指名具體版本、具體 skill 與目標路徑。只寫「可以裝 skill」不算；只指名一處路徑的授權，也不及於另一處。Worker 不得自行認定已取得授權。
2. **先備份**現行安裝品，放在 skills 目錄**之外**；任何一個 skill 備份失敗或複驗不一致就停，不進入安裝。
3. **不先刪除**。先把新版複製到暫存目錄、逐檔複驗，全部一致之後才逐一替換；替換時先把舊目錄移走，不是刪掉。
4. **逐檔複驗**安裝結果，要求全部 IDENTICAL，任何一檔不一致就視為失敗並回退。
5. **回報**備份路徑、逐 skill 的複驗結果、具體的回退指令，以及「下一個 session 才生效」。

v5.14.0 起用 plugin marketplace 安裝也算寫入 Layer 1，一樣要工單授權，指名 Agent、plugin 與 marketplace（例如 `ct@control-tower`）。差別在做法：只能用 `claude plugin …`、`codex plugin …` 指令安裝、更新或移除，不在 plugin 的安裝目錄裡複製或改檔，也不在旁邊做備份；回退是用 plugin 指令移除，或改回 zip 手動安裝。

「禁止先刪除」是踩過坑才加的：曾經有一次安裝先刪掉了已安裝的 skill 目錄，接著複製因為路徑格式問題全部失敗，結果兩端的 8 個 skill 都不見了。先複製、驗證、再替換，任何一步失敗，已安裝的版本都還在。權威定義：`version-governance.md` § 安裝／升級流程。

## Layer 1 整個路徑都不能寫，連備份也不行

Layer 1 的保護範圍是**整個** `~/.claude/skills/` 與 `~/.codex/skills/` 路徑，不只是 skill 定義檔；v5.14.0 起也包括 plugin 的安裝路徑（`~/.claude/plugins/`、`~/.codex/plugins/` 等），而且更嚴，連 skill 定義檔都只能由 plugin 指令寫入。備份、暫存檔、封存的舊版、`.bak` 檔，或任何「順手放在旁邊」的目錄，都不得放在這底下。

為什麼連備份都不行？因為 skill 掃描器會把這個路徑**第一層的每個子目錄**當成一個 skill 註冊。一份根層帶 `SKILL.md` 的備份，會以舊版的 description 進入路由候選；它和現役版本高度重疊，路由時可能命中舊版，答出已經被新版推翻的內容，而且沒有任何錯誤訊息。這件事在 Claude Code 端實際發生過；Codex 端未實測，保守起見比照辦理。

更值得記住的是 CT 怎麼看待「上次這樣做沒事」：另一次備份也放在 skills 底下卻沒出事，是因為那次備份的是 8 個 skill 的父目錄，根層沒有 `SKILL.md`。**那是結構僥倖，不是規則有效。** 所以 CT 不只寫禁令，還把掃描器的機制寫出來，讓讀的人自己推得出下一次會不會出事。也因此「用底線或點開頭命名，掃描器應該會略過吧」同樣不被接受：規則的前提是路徑位置，不是掃描器的行為。權威定義：`data-layer-architecture.md` § 寫入規則。

## 合併只在整合 worktree 裡做，推進 `main` 前經過斷點 E

隔離工單的成果在分支 `ct/T####` 上，合併回 `main` 是整條隔離流程**唯一會動到共用主線**的一步，所以護欄最多：

| 護欄 | 防什麼 |
|---|---|
| 只在**整合 worktree** 合併，不在主 checkout、也不在被合併工單的 worktree | 碰到使用者未提交的變更，或改寫 Worker 留下的驗收證據 |
| 一律 `--no-ff` | 歷史上看不出「哪張工單帶進了什麼」 |
| `main` 只用 `--ff-only` | `main` 出現一個沒在整合 worktree 做過、比對過的合併結果 |
| 不 push、不 `--force`、不 `reset --hard`、不 rebase `main` | 改寫歷史，讓先前記下的 SHA 失效 |
| 髒檔擋住 `--ff-only` 時不 stash、不丟棄 | 為了完成合併而動到使用者的變更 |

最後一道人工確認是**斷點 E**：塔台要對 `main` 執行 `--ff-only` 之前。非 yolo 模式一律暫停；yolo 模式下，機械合併在判準仍成立時、衝突解決在驗收全綠且沒有範圍外檔案時才自動推進，等價移植一律暫停。收單 SHA 比對任何一步不成立，不論什麼模式都不推進。

斷點 E 是唯一在非 yolo 模式下也固定暫停的斷點，因為「推進 `main`」的回頭成本，比任何一張工單都高。判準的方向也一致：**取不到資料就算不通過**，寧可多派一張合併工單跑一次驗收，也不在資料缺漏時推進 `main`。詳見 [worktree 隔離與合併](/deep/features/worktree-merge)。

## Workflow 與匯入的硬限制

**Workflow 工具**：Claude Code 的 Workflow 一次可以派出多個子 agent，花費在執行中讀不到，只能事後對帳。所以 Worker 要用它，**工單裡必須有塔台寫的授權段落**，寫明跑幾次、每次最多幾個 agent、token 事後上限；超出就停下來問塔台。塔台寫授權前，會依設定先問使用者並把答覆記進決策日誌。Workflow 裡的子 agent 只能用唯讀工具，也不使用 Workflow 內建的 worktree，所有寫入集中在 Worker，才對得上工單的 `affects_files` 與 commit（`workflow-engine.md` § 同意治理（v5.11.0 起落到工單授權）、§ 設計規則 R1–R5）。

**`*import` 匯入**：把規則或 playbook 合併進專案時，有 6 條不可覆寫的硬限制：

1. 絕不直接覆蓋現有文件，必須先讀再合併
2. 絕不在沒告知使用者的情況下解決衝突
3. 絕不在使用者確認前寫入
4. 寫入前一定先讀現有內容
5. 衝突一定並排顯示差異，等使用者三選一
6. 寫入後回報新增、保留、跳過各幾條

權威定義：`safe-import.md` § 安全原則（硬限制）。

這兩組規則的共同點是：**花費或覆寫在發生之前就被看見、被同意**，而不是等 AI 執行到一半自己決定。

## 延伸閱讀

- `control-tower/SKILL.md` § Hard Boundaries
- `control-tower/references/auto-session.md` § 安全邊界（§ Bash 白名單、§ 安全規則）
- `control-tower/references/version-governance.md` § 發布流程、§ 安裝／升級流程
- `control-tower/references/data-layer-architecture.md` § 核心原則 › 寫入規則（Q1～Q4）
- `control-tower-guide/references/governance.md` § Layer 1 寫入機制：為什麼「放旁邊」也危險、§ 合併護欄：推進 `main` 的每一步都要能對帳（v5.3.0）
- `control-tower/references/merge-workorder.md` § 共同護欄、§ 斷點 E
- `control-tower/references/yolo-mode.md` § 斷點 E：合併前確認（v5.3.0+）（斷點 E 的權威定義）
- `control-tower/references/workflow-engine.md` § 同意治理（v5.11.0 起落到工單授權）、§ 設計規則 R1–R5
- `control-tower/references/safe-import.md` § 安全原則（硬限制）

<p class="ct-note">Portal 是摘要，不具權威。內容與 CT reference 有出入時，以 reference 為準。</p>
