---
title: 演進史
description: CT 從一個斜線指令長成 8 個 skill：八個世代、CHANGELOG 記錄的 70 個版本，每一代改了哪個機制、是哪件事逼它改的。
---

# 演進史

<p class="ct-lead">CT 一開始是一個斜線指令，塔台寫出來的工作指引要靠人手複製到別的 session。七個月後，它是 8 個 skill：能在 BAT 裡自己開 Worker 分頁、收回報、關分頁，讓 Worker 在隔離的 worktree 裡改檔，看得出 Worker 是否已啟動、是否在等人，也能回答 Worker 的提問。</p>

| 數字 | 意思 |
|---|---|
| **70** | CHANGELOG 記錄的版本（v2.1.1 到 v5.14.4；v1 沒有編號，不計入） |
| **217 天** | 從 2026-03-27 第一次啟動，到 2026-10-30 發布 v5.14.4 |
| **8** | 目前的 skill 數；v1 時只有 1 個斜線指令 |
| **4,938 → 865** | v5.0.3 把 8 個 `SKILL.md` 改成路由器時，總行數的變化 |

這一頁照八個世代整理。每一版的完整紀錄見[更版紀錄](./releases)（近 10 版）與頁尾的[70 個版本一覽](#all-versions)。

## 八個世代 {#eras}

每一列是一個世代，排版仿航管的飛行進程條：左邊是呼號（世代與版號範圍），右邊是這一代的動作。

<EraTimeline />

八個世代裡有編號的七代，版數合計 1 + 8 + 11 + 10 + 5 + 17 + 18 = **70**，等於 CHANGELOG 的條目數；v1 沒有編號，不在其中。

## v1 → v2：把人從傳輸線上拿掉

v1 的塔台只會說話。它把「工作指引包」印在對話裡，列出任務、BMad 工作流程、要開新 session 還是沿用原 session、需要載入哪些文件；使用者自己複製到另一個 session 執行，做完再整理摘要貼回塔台。

試用一天後，使用者提出的第一批改良就是：工作指引改寫進 `.md` 檔，子 session 只需要拿到工單號碼。實測時又發現子 session 不會自己填開始和完成時間，當天就把執行工單做成專用指令 `/ct-exec`，再補上 `/ct-done` 和 `/ct-status`。

v1 的四條資訊流（顯示指引、複製貼上、整理摘要、貼回摘要）都經過使用者的手；v2 改成都經過工單檔案。使用者只剩兩個動作：在新 session 打 `/ct-exec T0001`，回塔台說「T0001 完成」。交接漏段、排版跑掉、忘了把摘要帶回來，這幾種錯誤從此沒有地方發生。

## 塔台和 Worker 分開跑

v3.0 把所有指令包進同一個 skill，靠觸發詞切換五種模式（塔台、工單執行、補救收尾、狀態查詢、學習萃取）。問題出在子 session：Worker 打 `/ct-exec` 時載入的是整個 `control-tower` skill，連「塔台不得讀寫程式碼」的禁令也一起載入，結果 Worker 改不了程式碼。

同一天發布的 v3.1 把 `ct-exec`、`ct-done`、`ct-status`、`ct-evolve` 拆成獨立 skill，再加上 `ct-help`。從此塔台與 Worker 沒有共用的 context，只靠工單檔案交換。後面的派工、回報、Renew 機制都建立在這條邊界上。

## 派工迴路：一個旗標一個旗標長出來

v3.2 的 auto-session 只能在 Windows Terminal 或 VS Code 開新分頁，開不了就把指令放進剪貼簿。v4.1 接上 BAT 之後，派工和回報變成一個閉合的迴路：塔台用 `bat-terminal.mjs` 開 Worker 分頁，Worker 做完用 `bat-notify.mjs` 把「T#### 完成」送回塔台的輸入列。此後每一版都是替這個迴路補一個參數，而且幾乎每個參數背後都有一次派錯。

| 版本 | 補上的東西 | 逼它補的事 |
|---|---|---|
| 4.2.2 | `--workspace` | 沒指定工作區時，新分頁會落在使用者當下正在看的那個工作區 |
| 4.3.0 | `--mode`、`--interactive`；Worker 改讀 `CT_MODE` | Worker 自己讀設定檔判斷模式，可能和塔台的判斷不一致 |
| 5.0.1 | 派工成功只看 exit code 與 helper 日誌 | 有人把 stdout 的 `Terminal created: null` 當成失敗，也有人對 TLS 埠打明文的健康檢查 |
| 5.0.4 | `--cwd`、Worker 端落點檢查、「`SKILL.md` 的指令範例不得當成唯一來源」 | 另一個專案的塔台照 `SKILL.md` 的摘要派工，漏了 `--workspace` 與 `--notify-id` |
| 5.0.5 | 落點檢查改以 repo 身分（C-0）為主 | 原本靠路徑推斷的 C-3，模擬量測的偵測率從 100% 掉到 41%（見[實戰案例](/cases#measure-landing)） |
| 5.2.4 | 每分頁範圍權杖：塔台必須在非 Worker 分頁啟動 | BAT 0.7.0-pre.1 起把本機分頁的權杖改成分頁專屬，Worker 分頁只能通知綁定的塔台 |
| 5.3.0 | `--isolation worktree`、`--worktree keep｜remove`、`--worktree-status`、合併工單 | 並行、會動產品檔的工單改在各自的 worktree 分支上做，合併另開工單 |
| 5.4.0 | Worker 分頁回收後也能查 `--worktree-status` | 舊 BAT 必須在回收分頁之前就查好合併判準 |
| 5.5.0 | 「T#### 提問」：yolo Worker 改問塔台；斷點 D | BAT 開始回報分頁在等人回答 |
| 5.6.0 | `--wait-started 30000`；exit `8` 不重派 | helper exit `0` 只代表分頁建好了，不代表 Worker 起來了 |
| 5.7.0 | `bat-notify.mjs --ask`、`bat-terminal.mjs --answer`、`bat_wait_question` | 5.5.0 的提問只能靠 Worker 輪詢工單檔等答覆 |
| 5.8.0 | codex 分頁的 OSC 7501 | 之前 codex Worker 的狀態一律無法判斷，斷點 D 與啟動確認只對 Claude 有用 |
| 5.9.0 | 跨 session 選收件人 | 通知另一個專案的塔台時，不能只靠目錄名或忙碌狀態推定誰是塔台 |
| 5.12.0 | 重派前先用 `--close-worker … --delay-ms 0` 回收舊分頁 | 同一張工單派了第二個 Worker，收單回收時回 exit `5`（`AMBIGUOUS`），兩個分頁都得手動關 |
| 5.12.1–5.12.2 | 回收時機的說明改照 BAT 的實際行為 | 舊說明寫「有新輸出就取消」「N 秒後回收」，實際上分頁仍在輸出時 BAT 會等安靜、最多再等 60 秒，仍在輸出就放棄 |
| 5.12.3 | `--close-worker` 的最低 BAT 版本更正為 `>= 0.6.1-pre.4` | 原本寫 `0.6.1-pre.3`；pre.3 已有這個指令，但分頁剛有輸出就回 `BUSY`，等輸出安靜再關是 pre.4 起才有 |

v5.2.4 之後換了一種長法：BAT 先寫好介面契約（參數、exit code、JSON 欄位），以委派單交給 CT；CT 照契約寫規則，每一條都註明需要的最低 BAT 版本，也寫明 BAT 太舊時怎麼降級（見[相容版本對照](./compatibility)）。補上的東西從「派到哪裡」轉到「派出去之後看得見什麼」：Worker 在哪個 worktree、是否已啟動、是否在等人回答、有沒有問題要問塔台。

v5.10、v5.11 沒有碰這個迴路：Workflow 規則只管 Worker 在單張工單內怎麼做事，派工指令一個參數也沒變。

## 三層資料：誰可以寫哪裡

v3.0 的自我學習會把萃取出來的規則寫回 skill 原始檔，下次升級 skill 就被覆蓋掉。v3.3 把資料拆成三層：skill 本體（Layer 1）唯讀，跨專案的學習放 Global 層（Layer 2），本專案的放 Project 層（Layer 3）；啟動時依序載入，設定值後者覆蓋前者。

這條規則後來又收緊兩次。v5.0.7 規定寫入 Layer 1 的唯一例外是「工單明文授權的安裝或升級」，起因是安裝前的備份放在 `~/.claude/skills/` 底下，被 skill 掃描器當成現役 skill 註冊；備份從此改放在 `skills/` 之外。v5.0.9 再把同一套規則套用到 `~/.codex/skills/`。v5.14.0 新增 plugin marketplace 安裝，plugin 的安裝目錄（`~/.claude/plugins/`、`~/.codex/plugins/` 等）也收進同一份規則，而且更嚴：只能用 plugin 指令寫入。學習萃取只能寫進 Layer 2 或 Layer 3。

## 5.0.0：metadata 改用 frontmatter

v4 的工單狀態寫在內文的表格裡，`*sync`、`ct-status`、歸檔各自去解析那張表。5.0.0 改成在檔頭放 YAML frontmatter（`schema_version: 1`、`status`、`affects_files`、`completed_at` 等），所有讀取端都先讀 frontmatter，內文表格降為給人看的鏡像。舊工單沒有 frontmatter 時退回舊的解析方式，並輸出 `missing_frontmatter` 警告。

這是 70 版裡唯一一次主版號升級，因為事實來源換了位置。這個改動先在 BAT 專案試跑了 5 個 sprint，才回寫到 CT。

## 5.0.3：SKILL.md 改成路由器

到 v5.0.2，8 個 `SKILL.md` 合計 4,938 行，每次啟動都要整份讀進 context。5.0.3 把它們改成「角色、Hard Boundaries、路由表」三段，細節全部移到 references、按需載入，總行數降到 865 行。

同一版也拿掉 frontmatter 的 `version:` 欄位（Codex 的 skill 驗證會擋不認得的欄位），改用內文註解記版號（見[版本總覽](./#版號寫在哪裡)），並把 bmad-guide 改成外部依賴，不再內嵌 BMad 的內容。精簡時有 7 項機制被刪除、沒有搬進 reference，例如 `*help roles`、粒度分析卡、JetBrains Gateway Dev Container 偵測；之後的 v5.0.8 確認這些不恢復。

## 5.0.4 之後：一條規則只寫一處

5.0.4 到 5.2.3 的修正大多不是新功能，而是同一個病：一條規則在好幾個檔案各寫一份，改了一處、漏了另一處，Worker 讀到舊的那份就做錯。修法也一樣：選一處當權威定義，其他地方只放一句摘要加連結，並在權威小節開頭寫明「其他文件只引用這裡」。

| 版本 | 收斂成單一權威定義的規則 | 權威所在 |
|---|---|---|
| 5.0.6 | 工單 ID 格式（可選 2–4 位大寫前綴 + `T` + 數字） | `work-order-system.md` |
| 5.0.7 | Layer 1 寫入範圍與唯一例外 | `data-layer-architecture.md` |
| 5.0.8 | 15 項 drift：決策日誌檔名、status 列舉、環境快照區段等 | 各自一處 |
| 5.2.0 | `--set-role` 的呼叫條件、指令與 exit code 意義 | `auto-session.md` |
| 5.2.1 | Node 解析（`BAT_HELPER_NODE`）、塔台狀態面板欄位 | `auto-session.md`、`memory-protocol.md` |
| 5.2.2–5.2.3 | 各 reference 複述的設定預設值改為引用 | `tower-config.md` |

5.2.4 之後的新機制則是一出生就先指定權威小節，其他檔案只放摘要：範圍權杖、worktree 隔離派工、Worker 啟動確認在 `auto-session.md`，合併流程在 `merge-workorder.md`，Worker 向塔台提問、斷點 D、BAT 提問通道在 `yolo-mode.md`，Worker 在 worktree 裡的行為在 `ct-exec/SKILL.md`，跨 session 選收件人在 `cross-project-coordination.md`。v5.10 之後照舊：Workflow 的定位與設計規則在 `workflow-engine.md`，重派前回收舊分頁在 `work-order-system.md`。這套做法的理由見[治理：單一權威與「摘要不具權威」](/deep/principles/governance)。

## 版本密度與發行檔大小

**發版的節奏很不平均。** 以每 7 天為一格、從 2026-03-28 起算：70 版裡有 21 版落在頭五週；5.0.x 的十個版本拖了五個月，6 到 8 月只有兩版；10-17 起的一週發了 25 版，其中 10-17、10-18 兩天就有 17 版（第七世代），10-20 到 10-23 再 8 版（第八世代）；下一週的 10-25、10-27 又發了 v5.12.6、v5.12.7、v5.12.8，10-29 發 v5.13.0，10-30 發 v5.13.1、v5.14.0、v5.14.1、v5.14.2、v5.14.3 與 v5.14.4。

| 期間 | 版數 | 內容 |
|---|---|---|
| 頭五週（03-28 起） | 21 | v2.1.1 ～ v5.0.0：Skill 化、自我學習、流程平台、BAT、YOLO、frontmatter |
| 5 月到 10 月初 | 9 | v5.0.1 ～ v5.0.9：治理收斂 |
| 10-15 → 10-16 | 5 | v5.1.0 ～ v5.2.3：分頁生命週期 |
| 10-17 → 10-30 | 35 | v5.2.4 ～ v5.14.4：BAT 0.7 委派、Workflow 規則層、重派前回收、狀態衛生、plugin marketplace、巢狀獨立 repo 配置、bmad-guide 偵測依 runtime |

**發行 zip 的大小**（v4.3.2 以前沒有 zip）：

| 版本 | 大小（bytes） | 說明 |
|---|---|---|
| v4.3.2 | 352,098 | 第一個有 zip 的版本 |
| v4.4.1 | 435,591 | v5.0.3 之前最大 |
| v5.0.2 → v5.0.3 | 428,530 → 216,120 | 路由器化；同一版也從發行樹移除了 CHANGELOG、安裝指南與 `docs/`，落差不全來自 `SKILL.md` 精簡 |
| v5.2.3 → v5.9.0 | 240,217 → 307,157 | 第七世代共增加 66,940；最大的三次是 v5.3.0（+15,991，新增 `merge-workorder.md`）、v5.5.0（+9,478，提問通道與斷點 D）、v5.7.0（+8,782，BAT 提問通道） |
| v5.9.0 → v5.14.4 | 307,157 → 381,399 | 第八世代共增加 74,242，大部分在兩個 Workflow 版本：v5.11.0 +26,351（隨 `ct-insights` 發行的預篩腳本），v5.10.0 +14,507（新增 `workflow-engine.md` 與適配度規則）；v5.12.4 退役 `references/ct-exec.md`，−1,504；v5.12.5 退役其餘三份 Worker 命令長版說明，−4,720；v5.12.6 改寫範例字句，+37；v5.12.7 偵測寫法改成只列名稱，+1,175；v5.12.8 BMad 舊名改成現行名稱，+607；v5.13.0 狀態衛生與 BAT 塔台面板讀取契約，+14,661；v5.13.1 通知用完整工單 ID 與面板契約對齊新版 BAT，+3,376；v5.14.0 plugin marketplace 安裝方式，+5,236；v5.14.1 塔台偵測 plugin 版 bmad-guide 與塔台端範本用完整工單 ID，+2,614；v5.14.2 Codex 搭配 BAT 派工改成依 BAT 版本與工單 ID 範例更正，+894；v5.14.3 一個塔台管多個巢狀獨立 repo 的配置文件，+5,522；v5.14.4 bmad-guide 偵測依 runtime 分開與 Claude plugin 位置只算一處，+908 |

## 70 個版本一覽 {#all-versions}

年份皆為 2026，日期為月-日。CHANGELOG 沒有 4.3.1 的段落，不計入。最新 10 版的完整內容見[更版紀錄](./releases)。

::: details 第八世代 v5.10–5.14：Workflow 規則層、重派前回收、狀態衛生與 plugin marketplace（18 版）

| 版本 | 日期 | 重點 |
|---|---|---|
| 5.14.4 | 10-30 | 規則修正：塔台找 bmad-guide 時先找自己所在 runtime 的安裝——本 runtime 的手動安裝 → 本 runtime 的 plugin → 另一個 runtime 的安裝（只拿來讀檔，第一次用到時註明一次），修正 Claude Code 與 Codex 裝法不同時讀到另一份的問題；Claude Code 的 plugin 位置只算一處（設了 `CLAUDE_CONFIG_DIR`／`CLAUDE_CODE_PLUGIN_CACHE_DIR` 時跟著搬）。BAT 介面不變，升級只換 skill 檔案 |
| 5.14.3 | 10-30 | 文件：寫明一個塔台管多個巢狀獨立 repo 的配置——工單集中在上層的個人塔台 repo，Worker 在上層執行，子 repo 用 `git -C` commit，不能用 worktree 隔離；附拋棄式目錄的實機驗證結果。落點檢查、派工命令與 BAT 介面不變，升級只換 skill 檔案 |
| 5.14.2 | 10-30 | 文件修正：Codex 搭配 BAT 派工改成依 BAT 版本——BAT 0.7.2-pre.1 起依 Codex 端的安裝方式送 `$ct-exec` 或 `$ct:ct-exec`，zip 與 plugin 都能接 BAT 派工，更舊的 BAT 仍用 zip；工單 ID 格式的範例表更正（前綴 4 字元是上限、合法）。派工命令不變，升級只換 skill 檔案 |
| 5.14.1 | 10-30 | 文件修正：塔台偵測得到 plugin 安裝的 bmad-guide（依序找手動安裝、Claude Code plugin、Codex plugin，並存時用手動那份），已安裝卻讀不到時提示一次；安裝說明補同一個 marketplace 的 `bmad-guide`；塔台端派工與回收範本改用完整工單 ID。BAT 介面不變，升級只換 skill 檔案 |
| 5.14.0 MINOR | 10-30 | 另提供 plugin marketplace 安裝（Claude Code、Codex），zip 手動安裝照舊：marketplace `control-tower`、plugin `ct`（8 個 skill）與 `ct-guide`，beta 不上架；從 zip 改用 plugin 要先移除手動安裝；Codex 搭配 BAT 派工繼續用 zip；plugin 安裝目錄也算 Layer 1。BAT 介面不變，升級只換 skill 檔案 |
| 5.13.1 | 10-30 | 文件修正：Worker 回報、通知與提問一律用含前綴的完整工單 ID，送出前和工單 `id` 比對；塔台收到漏了前綴的回報時能對到唯一一張；BAT 塔台面板讀取契約對齊 BAT 0.7.1-pre.9（讀不到時顯示「無法讀取」），400 KB 預算保留，升級只換 skill 檔案 |
| 5.13.0 MINOR | 10-29 | 狀態衛生與 BAT 塔台面板：BUG 結案判準與 `closed_reason`、`PARTIAL` 在塔台裁示當下收尾、`_tower-state.md` 機器可讀摘要、熱檔 400 KB 大小預算與決策日誌收斂；新增 3 個設定，升級無需遷移 |
| 5.12.8 | 10-27 | 文件修正：BMad 路由與工單規則裡 BMad-Method v6.11 前的舊名改成現行名稱；「用了 `bmad-create-story` 就不必另外審查」的說法改成看 `bmad-build` 的 Review Triage 有沒有跑，升級無需額外動作 |
| 5.12.7 | 10-27 | 文件修正：BAT／CT 環境偵測改成只列變數名稱、不輸出值，避免把範圍權杖印進對話紀錄；判讀邏輯不變，升級無需額外動作 |
| 5.12.6 | 10-25 | 文件修正：說明文字裡的範例名稱與路徑換成中性寫法，規則與行為不變，升級無需額外動作 |
| 5.12.5 | 10-23 | 文件補完：退役 `references/` 其餘三份 Worker 命令長版說明（`ct-done`、`ct-status`、`ct-evolve`），仍有效的規則補進各自的 `SKILL.md` 與 `self-learning-core.md`；`ct-status` 的 `INTERRUPTED` 歸「需要塔台判斷」 |
| 5.12.4 | 10-23 | 文件與發行物：退役 `references/ct-exec.md`（Worker 規則只以 `ct-exec/SKILL.md` 為準）；YOLO 計數器位置統一為 `## YOLO 歷程` › `### 計數器`；另出 8 個單一 skill zip，Guide zip 改成資料夾版面 |
| 5.12.3 | 10-23 | 文件修正：`--close-worker` 的最低 BAT 版本更正為 `>= 0.6.1-pre.4`；學習的置信度條件分成專案層與全域層 |
| 5.12.2 | 10-22 | 文件修正：收單回收的提示改成「約 N 秒後回收」，不寫成確定時間或「已關閉」 |
| 5.12.1 | 10-22 | 文件修正：`worker_close_delay` 的取消條件對齊 BAT，延遲期間的輸出不取消、只有使用者輸入會取消 |
| 5.12.0 MINOR | 10-22 | 重派前回收舊 Worker 分頁（`--close-worker … --delay-ms 0`），不論 exit code 都照常派工 |
| 5.11.0 MINOR | 10-20 | Workflow 精簡版：`workflow_integration` 設定、Worker 只在工單授權時呼叫 Workflow、預篩腳本與 `*insights workflow` |
| 5.10.0 MINOR | 10-20 | Workflow 規則層：`workflow-engine.md`、Workflow 適配度規則組、`ct-evolve --workflow` |

:::

::: details 第七世代 v5.2.4–5.9：BAT 0.7 委派——隔離、觀測、對話（17 版）

| 版本 | 日期 | 重點 |
|---|---|---|
| 5.9.0 MINOR | 10-18 | 跨 session 選收件人；MCP 加 `claudeSessionName`、`scope: towers`（BAT ≥ 0.7.1-pre.1） |
| 5.8.1 | 10-18 | BAT 版本佔位換成 `>= 0.7.0-pre.9`；yolo 提問的「提問時間」取自系統 |
| 5.8.0 MINOR | 10-18 | codex 分頁 OSC 7501：斷點 D 接受 `input`，`--wait-started` 對 codex 生效（BAT ≥ 0.7.0-pre.9） |
| 5.7.2 | 10-18 | 晚退回的題也加「通道」標記，塔台不再依賴 BAT 已結束題目的保留期 |
| 5.7.1 | 10-18 | 提問通道補洞六項：多題逐題判斷、「通道」標記、通知前自檢 |
| 5.7.0 MINOR | 10-18 | Worker 問塔台的 BAT 結構化通道：`--ask`／`--answer`、`bat_wait_question`（BAT ≥ 0.7.0-pre.7） |
| 5.6.1 | 10-18 | 實機驗收表外六項：答覆行比對、先 commit 後通知、分段工單的狀態判定 |
| 5.6.0 MINOR | 10-18 | Worker 啟動確認：`--wait-started`、exit `8` 不重派（BAT ≥ 0.7.0-pre.6） |
| 5.5.1 | 10-18 | 補上 BAT 版號 0.7.0-pre.5；yolo 下 Worker 的防護機制不再向使用者提問 |
| 5.5.0 MINOR | 10-18 | yolo 提問通道（Worker 問塔台、塔台代決）、斷點 D、`worker_question_timeout` |
| 5.4.0 MINOR | 10-18 | Worker 分頁回收後也能查 `--worktree-status`（BAT ≥ 0.7.0-pre.4） |
| 5.3.2 | 10-18 | `BAT_HELPER_LOG_DIR` 必須是絕對路徑；MCP 錯誤取不到 code 時改用 helper |
| 5.3.1 | 10-18 | helper 日誌的檔案位置；合併後整合 worktree 改用 `switch --detach` |
| 5.3.0 MINOR | 10-17 | worktree 隔離派工、合併工單、斷點 E、BAT MCP 唯讀通道（BAT ≥ 0.7.0-pre.2） |
| 5.2.6 | 10-17 | 安裝流程安全化：先暫存、複驗再替換，不先刪除已安裝的 skill |
| 5.2.5 | 10-17 | 對使用者用分頁標題描述分頁；Worker 分頁的面板顯示「不可派發」 |
| 5.2.4 | 10-17 | BAT 每分頁範圍權杖：塔台必須在非 Worker 分頁啟動（BAT ≥ 0.7.0-pre.1） |

:::

::: details 第六世代 v5.1–5.2：分頁生命週期（5 版）

| 版本 | 日期 | 重點 |
|---|---|---|
| 5.2.3 | 10-16 | 文件修正：`SKILL.md` 不再複述 `worker_auto_close` 的預設值 |
| 5.2.2 | 10-16 | 文件修正：路徑分隔符號、設定預設值改引用 `tower-config.md` |
| 5.2.1 | 10-16 | 所有 helper 改用 `BAT_HELPER_NODE`；塔台狀態面板定義 |
| 5.2.0 MINOR | 10-16 | 啟動時以 `--set-role tower` 宣告塔台分頁（BAT ≥ 0.6.1-pre.6） |
| 5.1.0 MINOR | 10-15 | `worker_auto_close`：收單後以 `--close-worker` 回收 Worker 分頁 |

:::

::: details 第五世代 v5.0：metadata 改版與治理收斂（10 版）

| 版本 | 日期 | 重點 |
|---|---|---|
| 5.0.9 | 10-04 | Layer 1 寫入規則擴及 `~/.codex/skills/` |
| 5.0.8 | 10-04 | 修正 15 項 drift，確認 5.0.3 刪除的機制不恢復 |
| 5.0.7 | 09-02 | Layer 1 寫入規則單一權威；安裝流程：備份、逐檔複驗、回退 |
| 5.0.6 | 09-02 | 工單 ID 格式單一權威，放行帶前綴的 ID；舊版 BAT 降級規則 |
| 5.0.5 | 09-01 | 落點檢查以 C-0 repo 身分為主；工單模板加 `repo` |
| 5.0.4 | 09-01 | `--cwd`、落點檢查、HANDOVER／ADVISORY 協調類型 |
| 5.0.3 | 07-04 | `SKILL.md` 路由器化（4,938 → 865 行）、Codex 相容、bmad-guide 外部化、證據分道 |
| 5.0.2 | 06-05 | `PARTIAL` 解除後補正為 `DONE`；派工與通知的環境變數需求拆開 |
| 5.0.1 | 05-07 | BAT 派工成功判讀規則（只信 exit code 與日誌） |
| 5.0.0 MAJOR | 04-28 | YAML frontmatter 成為工單 metadata 的事實來源 |

:::

::: details 第四世代 v4：流程平台、BAT、YOLO（11 版）

| 版本 | 日期 | 重點 |
|---|---|---|
| 4.4.1 | 04-25 | 文件化 Claude／Codex 雙 agent 支援 |
| 4.4.0 | 04-23 | `intervention_type`、`affects_files`、`memory_overrides`；`*evolve` 三區；`doctrine.md` |
| 4.3.3 | 04-22 | JetBrains Gateway Dev Container 偵測 |
| 4.3.2 | 04-20 | 終端偵測擴展：20 個環境變數、17 種開分頁指令、OSC 52 |
| 4.3.0 | 04-18 | Worker 無狀態化：改讀 `CT_MODE`／`CT_INTERACTIVE`；版號治理 |
| 4.2.2 | 04-18 | 派工加 `--workspace` |
| 4.2.1 | 04-18 | 區分 YOLO 斷點 C 與使用者中斷 |
| 4.2.0 | 04-18 | YOLO 自主模式：auto-session 第四階、3 個自動暫停斷點 |
| 4.1.0 | 04-17 | BAT 整合：跨分頁派工與 Worker 自動回報 |
| 4.0.1 | 04-15 | 啟動 Fast Path（約 20 次 → 約 3 次 tool call）、`*rescan` |
| 4.0.0 | 04-15 | 24 項功能：BUG／PLAN／EXP、歸檔、決策日誌、遷移引擎、研究型工單、Renew、Worker 護欄、Playbook |

:::

::: details 第三世代 v3：Skill 化與自我學習（8 版）

| 版本 | 日期 | 重點 |
|---|---|---|
| 3.6.1 | 04-10 | mem0 偵測改走 memsync CLI；Level 3 降為單向寫入同步 |
| 3.6.0 | 04-10 | DESIGN.md 視覺規範擷取（程式碼、URL 靜態、Chrome MCP） |
| 3.5.0 | 04-06 | `ct-fieldguide`：FIELDGUIDE 教戰手冊自動化 |
| 3.4.0 | 04-02 | 新手村教學模式、`ct-insights` 使用模式分析 |
| 3.3.0 | 03-31 | 三層資料架構；跨專案協調 LOCAL／COORDINATED／DELEGATE |
| 3.2.0 | 03-31 | `*config`、`*sync`、`*pause`、auto-session、選項式提問 |
| 3.1.0 | 03-30 | Worker 指令拆成獨立 skill，恢復 session 隔離；新增 `ct-help` |
| 3.0.0 | 03-30 | Skill 2.0 格式、四級能力、自我學習、`_tower-state.md`、多塔台 |

:::

::: details 第二世代 v2：工單指令集（1 版）與 v1

| 版本 | 日期 | 重點 |
|---|---|---|
| 2.1.1 | 03-28 | 檔案驅動工單、`/ct-exec`、`/ct-done`、`/ct-status`、Debug 三層防線 |
| v1（未列入 CHANGELOG） | 03-27 | `/control-tower` 斜線指令，在對話中產生工作指引包；當晚補上 mono-repo 多微應用模式 |

:::

## 延伸閱讀

- CT `CHANGELOG.md`（v2.1.1 至 v5.14.4）
- CT `version-governance.md` § 歷史版號表

資料來源：CT CHANGELOG 與開發紀錄。Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
