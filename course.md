---
title: 課程
description: 「多代理規格驅動開發實戰」：用 BMad-Method、Control Tower 與 BAT 以 Go 打造 SMS 通訊平台。6 章、57 單元、影片約 21 小時。
---

# 課程：多代理規格驅動開發實戰

<p class="ct-lead">用 BMad-Method、Control Tower 與 BAT 以 Go 打造 SMS 通訊平台。這門課教已經會用 Claude Code 的開發者，把「一個人、一個 session」的 AI coding，升級成多代理、規格驅動、由工單約束的工作流。</p>

## 課程主張

**只有工單檔與驗收證據能約束多代理。**

一個 agent 可以靠測試約束；好幾個 agent 同時工作時，還需要一份大家都照著走的契約。這門課裡，BMad 的規劃產物綁定 CT 工單的驗收條件，E2E 與 BDD 測試是 Worker 收單的門檻：測試名寫在工單裡，沒有測試名就不開單。

三件套各自的位置：**BMad 想清楚、CT 管得住、BAT 跑得動**。貫穿全課的專案是一個後端 SMS 通訊平台，從一句話的點子做到八項功能齊全。

只想先花四十分鐘知道這三樣工具在做什麼，可以先看 5 支短片：[推廣影片（第二季）](/podcast)。

## 適合誰

- **適合**：會用 Claude Code 完成日常開發任務，但沒碰過 BMad-Method、Control Tower、BAT 的工程師與技術主管。
- **先備**：會用 git、會跑終端指令、看得懂一種靜態語言的程式碼。**不需要 Go 經驗**，Go 語法邊做邊帶，每個單元最多兩三個 Go 要點。需要一台能裝 Claude Code、Node.js、Go 與 BAT 的機器；環境設定範例涵蓋 Windows 11（含 WSL2）、macOS 與 Dev Docker 三組。
- **主線工具**：所有示範、錄影與 Worker 分頁都用 Claude Code。Codex 也能跟練（CT 的 8 個 skill 與 BAT 派工都支援，改用 `$` 前綴），課程用一頁說明差異。

不適合這門課的人：

- 還不會用任何 coding agent 的人（課程不教 agent 的基本操作）
- 想學 Go 語言本身的人
- 只需要前端或 UI 的人（課程不做 Web 主控台）
- 想要「一鍵全自動」、不願意讀工單檔的人

## 章節

全課 **6 章、57 單元，影片合計約 21 小時**。每章第一個單元是「速成 vs 高手學習路徑」，最後一個單元是「道館」：用一個可驗證的產出結束這一章。單元形式分成講解 28 個、示範 22 個、Live Coding 1 個、道館 6 個。

<CardTable
  :columns="['章', '標題', '單元', '影片長度', '道館產出']"
  :rows="[
    ['CH1', '新手村：一個 session 為什麼不夠', '7', '2:28:49', '派出第一張最小工單，建好 Go module 骨架與健康檢查 API'],
    ['CH2', 'BMad-Method v6：從點子到可派工的 story，做出第一支 API', '11', '4:03:48', '立案文件齊全（PRD、架構、SPEC、epics、AGENTS.md），第一則 story 綠燈'],
    ['CH3', 'Control Tower：工單編排、收單與治理', '10', '3:57:21', '把兩則 story 轉成工單、派給手動 Worker、收單並寫決策日誌'],
    ['CH4', 'BAT：多分頁執行環境、遠端 PTY 環境與自動派工', '11', '4:01:44', '以 yolo 批次派 3 張互不相依的工單，並處理一次 Worker 提問'],
    ['CH5', 'Go SMS 平台實戰：用三件套跑完一個 epic', '11', '4:05:47', '一個 epic 批次派工並合併，八項功能全部到位'],
    ['CH6', '進階與治理：讓多代理工作流長期可維護', '7', '2:22:32', '你自己的多代理工作流：工單模板、auto-session 策略、收單門檻與 FIELDGUIDE']
  ]"
  caption="課程章節"
/>

各章的重點：

- **CH1** 從 context 預算、塔台與 Worker 分離、Hard Boundaries、證據分道四個概念，說明一個 session 為什麼不夠，接著裝好三件套、跑第一次 `/control-tower`。
- **CH2** 走一遍 BMad-Method v6 的規劃：壓力測試點子、PRD、架構、SPEC 與 stories、epics，以及讓每個 Worker 拿到同一本手冊的 `AGENTS.md`，最後用標準實作迴圈做出第一支 API。
- **CH3** 深讀工單模板與 frontmatter，講派工與收單、落點檢查、反序寫入、回報判讀、三層架構與塔台記憶、BUG／PLAN／EXP、Worker 的防護與知識管線。對應 Portal 的[一張工單的一生](/lifecycle)與[進階區](/deep/)。
- **CH4** 接上 BAT：分頁角色、auto-session 四階、範圍權杖、yolo 與斷點、Worker 向塔台提問、回收與重派、worktree 隔離與合併工單，以及把 Worker 派進遠端與容器環境。
- **CH5** 用三件套把剩下的功能一次派完：測試策略與收單門檻、工單粒度與 `affects_files` 重疊、平行工單與三種合併模式、code review 與回顧。[實戰案例](/cases#conflict-merge)裡的衝突合併就是這一章的實錄。
- **CH6** 從一個專案走到一套制度：跨專案與多塔台、版本治理、FIELDGUIDE、Workflow 在單張工單內的用法，以及 BMad 下一代（V7）的遷移看點。

## 錄製時版本

課程內一律標示「本課錄製時版本」。

| 工具 | 版本 |
|---|---|
| BMad-Method | v6.12.4（示範專案自己安裝一份） |
| bmad-guide（教材對照） | v6.12.4 |
| Control Tower | v5.12.2 |
| CT Guide Skill | v5.12.2 |
| Better Agent Terminal | 0.7.1-pre.6 |
| Claude Code | 錄製時 `claude --version` 的輸出 |
| Go | 開工時的最新穩定版，鎖在示範專案的 `go.mod` |

CT 之後發新版時，課程仍以上表為基準；各功能需要的版本見[相容版本對照](/versions/compatibility)。

## 取得方式

課程以 6 支整章影片發布在 YouTube 播放清單：[多代理規格驅動開發實戰（YouTube 播放清單）](https://www.youtube.com/playlist?list=PLM1w-3eL8kgI)。播放清單公開後即可觀看。

| 章 | 標題 | 長度 |
|---|---|---|
| CH1 | 新手村：一個 session 為什麼不夠 | 2:28:49 |
| CH2 | BMad-Method v6：從點子到可派工的 story，做出第一支 API | 4:03:48 |
| CH3 | Control Tower：工單編排、收單與治理 | 3:57:21 |
| CH4 | BAT：多分頁執行環境、遠端 PTY 環境與自動派工 | 4:01:44 |
| CH5 | Go SMS 平台實戰：用三件套跑完一個 epic | 4:05:47 |
| CH6 | 進階與治理：讓多代理工作流長期可維護 | 2:22:32 |

每支影片的說明欄都列出各單元的時間碼，點一下就能跳到該單元。

## 延伸閱讀

- 課程規劃（`COURSE-PLAN.md`）§ 1 課程定位、§ 3 課程總表、§ 6.1 錄製時版本

Portal 是摘要，不具權威；課程內容以課程本身為準。
