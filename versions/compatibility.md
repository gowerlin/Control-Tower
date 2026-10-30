---
title: 相容版本對照
description: 每個 CT 功能從哪一版開始、需要哪一版 BAT 與 codex、BAT 太舊時會怎樣，以及 CT 和 bmad-guide 的版本關係。
---

# 相容版本對照

<p class="ct-lead">CT 不會先檢查 BAT 版本才決定要不要用某個功能。它一律照常呼叫，失敗時才依 exit code 降級，所以下表不是「用之前要先確認的條件」，而是「BAT 太舊時你會看到什麼」。</p>

## 原則

- **照常呼叫，失敗才降級**。BAT 太舊時，新參數通常會讓 helper 回 exit `1`；CT 依各功能的規則降級（例如去掉參數重派一次、改走工單檔往返、改用 git 計算），不會因此擋住整個流程。
- **不以錯誤訊息的字串判斷版本**。版本判斷只看 exit code 與回傳欄位有沒有出現。
- **任一邊較舊，就是那個功能不啟用**，其餘流程照舊。
- **塔台和 Worker 要同批升級**。新版塔台派工給舊版 Worker 時，應該看到明確的 `PARTIAL`／`BLOCKED` 或升級提示，不能當成 YOLO 自動回報已經生效。

## 每個功能需要的版本

「CT 起始版本」是這個功能在 CT 出現的版本；「BAT 最低版本」與「codex」是功能完整生效需要的版本。BAT 的最低門檻從 `0.5.9-pre.1` 一路提高到 `0.7.1-pre.1`；v5.10 到 v5.13 沒有再提高門檻。

<VersionMatrix />

## codex

只有一項功能另外需要 codex 的版本：v5.8.0 起，BAT 用 OSC 7501 判斷 codex 分頁「在等人回答」與「已啟動」，需要 codex `>= 0.163.0`（加上 BAT `>= 0.7.0-pre.9`）。版本不夠時，codex Worker 的狀態一律是「無法判斷」：斷點 D 不會因為 codex 在等人而觸發，啟動確認回 `started: unknown`。其他功能在 Claude Code 與 Codex 上的行為相同，差別只在指令前綴（`/` 與 `$`）。

## bmad-guide

CT 不內嵌 BMad-Method 的內容。需要 BMad 的 workflow 路由時，塔台去讀**另外安裝**的 `bmad-guide` skill；沒裝或讀不到，就靜默改用工單裡手動填的 workflow 欄位，不擋住塔台。

- bmad-guide 顯示 BMad-Method v6.10.0 或更新時，塔台改用 v6.10 起的替代名稱，例如 `bmad-investigate` 已退役、改開 CT 研究型工單或一般調查，`bmad-automator` 改建議 `bmad-loop`。
- 版本低於任務需要時，塔台只顯示升級提示，不阻塞。
- bmad-guide 用 plugin marketplace 安裝（`bmad-guide@control-tower`）時，塔台目前可能偵測不到：偵測條文以 `skills/` 目錄裡的安裝為準，讀不到就照上面的規則靜默改用手動欄位。要讓塔台用到它，目前建議用 zip 手動安裝，見 [BMad Guide Skill › 用 plugin 安裝](/guide/bmad-guide#install-plugin)。
- Portal 的內容以 **bmad-guide v6.12.4** 為準。

## BAT 太舊時會怎樣

大多數情況只是「那個功能不啟用」：

- 回收 Worker 分頁失敗：一行警告，照常收單或派工。
- 啟動確認的參數不被接受：去掉參數重派一次，本 session 之後不再帶。
- BAT 提問通道不可用：回到工單檔往返，題目本來就已經寫在工單裡。
- 查詢通道不可用：改走 helper、讀檔案或用 git 計算。

只有一個例外會**停下來等你**：隔離工單（`--isolation worktree`）在舊 BAT 上回 exit `1` 時，塔台不會自動改成非隔離派工，而是停下等你決定；非隔離的工單不受影響。

`BAT_HELPER_NODE` 沒有版本門檻：本機沒有這個變數就用 `node`，只有遠端分頁才由 BAT 注入。

## 和 BAT 站的對照

BAT 站也有一張相容表，是從 BAT 的角度列（<BatLink path="compatibility">BAT 站：相容版本</BatLink>）。兩張表的最低版本一致。「收單後回收 Worker 分頁」與沿用它的「重派前回收」兩端都是 `>= 0.6.1-pre.4`：CT 原本寫 `0.6.1-pre.3`，v5.12.3 依 BAT 的相容表更正（pre.3 已有這個指令，但分頁剛有輸出會回 `BUSY`；等輸出安靜再關自 pre.4 起，見 CT CHANGELOG [5.12.3]）。

## Beta {#preview}

上面的表格只列**穩定版**。CT v6.0.0-beta.5 是 Beta，放在 GitHub 預發行 Release、與穩定版並行，不列入表格；它的內容與下載見[Beta：方法論轉接](../preview/methodology-adapters)。

BAT 指揮塔總覽讀塔台狀態摘要的版本需求如下；v5.13.0 起穩定版也寫同一份摘要（上表也列了這一項）：

| 功能 | BAT | CT |
|---|---|---|
| 總覽顯示最後更新與進行中工單 | `>= 0.7.1-pre.7`（預覽版） | 不限版本（BAT 直接讀工單檔） |
| 總覽顯示下一個編號與待辦 | `>= 0.7.1-pre.7`（預覽版） | 穩定版 `>= v5.13.0`；v6 預覽版 `>= v6.0.0-pre.1`（含 Beta v6.0.0-beta.1～v6.0.0-beta.5）。塔台寫出 `_tower-state.md` 的機器可讀摘要 |

CT 版本不夠時，總覽只是少了這兩項，其他照常顯示。方法論轉接本身沒有改變 BAT 介面，也沒有提高 CT 要求的最低 BAT 版本；beta.1～beta.5 的 BAT 介面與最低 BAT 版本都和 v6.0.0-pre.1 相同；beta.2 改的環境偵測寫法（bash 用 `compgen -e` 只列名稱）是 CT 這一側的指令寫法，不需要新的 BAT 版本。

beta.3 新增 BAT 塔台面板讀取契約：CT 寫的決策日誌、BUG／PLAN 索引、塔台狀態等檔案要長什麼樣、多大以內，BAT 指揮塔面板才讀得到（見 [BAT 塔台面板為什麼會空](../deep/features/observability#bat-panel)）。契約對照 BAT `0.7.1-pre.8`（預覽版）寫成，規範的是 CT 寫檔的格式與大小，不是新的最低 BAT 版本；穩定版 v5.13.0 起也有同一份契約，v5.13.1 把穩定版契約的對照版本改成 BAT `0.7.1-pre.9`（讀不到時顯示「無法讀取」），一樣沒有提高最低 BAT 版本。

beta.4 的 BAT 介面同 beta.3；面板讀取契約改成對照 BAT `0.7.1-pre.9`（預覽版）：pre.9 起讀不到檔時顯示「無法讀取」、`critical` 在任何讀取路徑都算 High，更舊的 BAT 照舊靜默變空，所以 400 KB 預算保留。這和穩定版 v5.13.1 是同一份契約，同樣不是新的最低 BAT 版本。beta.4 另把通知改成用完整工單 ID（設了前綴就含前綴），這是 CT 這一側的寫法，派工命令與 BAT 介面不變，不需要新的 BAT 版本。

beta.5 的 BAT 介面同 beta.4：移植的是穩定版 v5.14.0 的 plugin 安裝就緒規則，派工命令、斷點 A 的判定格式與最低 BAT 版本都不變，不需要新的 BAT 版本。BAT 對 Codex 派工送的是 `$ct-exec`，plugin 版的 Codex 叫不到，所以接 BAT 派工的 Codex 用 zip 手動安裝；Beta 本來就只提供 zip、沒有 plugin，不受影響。

beta.1 改成 BUG／PLAN／EXP 預設開啟，啟用時立即產生 `_bug-tracker.md`、`_backlog.md`，BAT 指揮塔面板的「臭蟲」與「待辦池」因此不必等第一次 `*sync` 就有檔可讀；這不需要新的 BAT 版本。

## 延伸閱讀

- CT `auto-session.md` § BAT 內部終端路由（Better Agent Terminal）› 依賴的 BAT 基礎設施、§ 舊版 BAT 降級規則（帶前綴 `--workorder`）
- CT `yolo-mode.md` § 相容性 › BAT / Worker 版本相容
- CT `version-governance.md` § 歷史版號表、§ 相容性注意
- CT `enhancement-integration.md` § Level 2：外部 bmad-guide
- Guide `references/bat-integration.md` § 版本對照表

Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
