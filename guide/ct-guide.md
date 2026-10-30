---
title: CT Guide Skill
description: CT 的互動式學習指南：它是「教科書」，回答 CT 為什麼這樣設計；怎麼安裝、有哪三種回應模式、怎麼問。
---

# CT Guide Skill

<p class="ct-lead">CT Guide Skill（skill 名稱 <code>control-tower-guide</code>）是 CT 的教科書：它不執行指令、不開工單，只回答「CT 為什麼這樣設計、各部分怎麼接在一起」，並附上可以點擊、一路往下追問的圖。</p>

這一頁只講 CT Guide。Guide Skill 專區還有另一個 skill：教 BMad-Method 的 [BMad Guide](./bmad-guide)。兩者怎麼分工、該問哪一個，見[專區首頁](./)。

## 它是三種學習資源的其中一種

CT 生態系裡有三樣東西都在「教」，但用途不同。要**馬上做一件事**（確切的旗標、設定值、該用哪個指令），問 `ct-help`；要**理解**為什麼這樣運作、各部分怎麼配合，問 Guide；要在真的跑塔台時**有人帶**，把那座塔台的 `experience-level` 設成 `beginner`。

<CardTable
  :columns="['資源', '形式', '比喻', '用途']"
  :rows="[
    ['control-tower-guide', '獨立的 skill', '教科書', '概念、設計理由、架構，以及 v4 → v5 的世界觀變化'],
    ['ct-help', 'CT 的 skill（/ct-help、$ct-help）', '操作手冊＋概念速答', '簡短、可以照做的答案：指令語法、設定、前綴、BAT／YOLO 的簡介'],
    ['新手村（beginner-tutorial）', '塔台內建模式，不是 skill；experience-level = beginner 時啟用', '駕訓班教練', '在進行中的塔台裡陪練：課程關卡、違規偵測、結業']
  ]"
  :highlight="[0]"
  caption="三種學習資源的定位"
/>

Guide 講到確切的規則（正則、旗標、路徑）時，不會自己再寫一份，而是指回 `ct-help` 或 CT 的 reference。這和 Portal 的立場相同：摘要只負責帶路，權威定義只有一處。

## 安裝

Guide 和 CT 是**同一個版號**：CT 每發一版（含 patch），同一輪就會出一版同號的 Guide，內容沒受影響時至少更新版號。所以裝 CT v5.14.4 時，搭配的就是 Guide v5.14.4（版本對照見[版本總覽](/versions/)）。

- 發行檔是 `control-tower-guide-v<版號>.zip`，壓縮檔的根層只有一個資料夾 `control-tower-guide/`，裡面是 `SKILL.md` 和 `references/`（v5.12.3 以前根層直接是 `SKILL.md`）。
- zip 手動安裝時，安裝目錄的名稱用 skill 名稱 `control-tower-guide`，例如 Claude Code 是 `~/.claude/skills/control-tower-guide/`。
- v5.14.0 起也可以用 plugin marketplace 安裝：plugin 名稱是 `ct-guide`（`ct-guide@control-tower`），和 CT 的 `ct` 放在同一個 marketplace。Codex 用 plugin 安裝時呼叫寫法是 `$ct-guide:control-tower-guide`。見[安裝 › 用 plugin marketplace 安裝](/install#plugin)。
- zip 手動安裝的安裝與升級做法和 CT 一樣：先備份、先複製到 `skills/` 以外的暫存區複驗、再替換，最後逐檔比對全部 IDENTICAL；新版從下一個 session 才生效。步驟見[安裝](/install)。
- 版號寫在 `SKILL.md` 內文的第一個註解 `<!-- control-tower-guide-version: 5.14.4 -->`，和 CT 一樣不放在 frontmatter。

Guide 本身是以 Claude skill 的形式打包的。它解說 CT 指令時會同時列出 Claude Code 的 `/` 寫法與 Codex 的 `$` 寫法（例如 `/ct-exec T0001` 與 `$ct-exec T0001`），用 plugin 安裝時的寫法（Codex 的 `$ct:ct-exec T0001`）也會說明，塔台內建的 `*` 命令則另外標明。

## 三種回應模式

Guide 先判斷你在問哪一類問題，只讀需要的那幾份教材，再用繁體中文回答，並附一張圖。

<CardTable
  :columns="['模式', '什麼時候', '回答的樣子']"
  :rows="[
    ['Learning（概念理解）', '「X 是什麼」「為什麼 X 這樣運作」「解釋 X」', '先講概念與設計理由，再用圖標出 X 在 CT 生態系裡的位置，最後補提示、常見誤解與取捨'],
    ['Practical（實戰查詢）', '「怎麼開始」「下一步做什麼」「怎麼設定」', '先給具體步驟和指令範例（/ 與 $ 兩種寫法），列出前提 → 動作 → 預期結果，再附聚焦在那段流程的圖；確切旗標指回 ct-help'],
    ['Comparison（比較釐清）', '「X 和 Y 差在哪」「什麼時候用 X、什麼時候用 Y」', '先放並排比較表，再說明為什麼要這樣區分，最後用定位圖畫出邊界']
  ]"
  caption="Guide 的三種回應模式"
/>

## 怎麼問

不需要特別的指令，直接用自然語言問就好。下面這些說法都會讓 Guide 接手：

- **入門**：「塔台學習」「CT 入門」「什麼是 Control Tower」「為什麼要分塔台和 Worker」「Worker 為什麼是無狀態的」
- **工單**：「工單流程」「frontmatter 和內文表格差在哪」「證據分道是什麼」「反序寫入」「Renew」
- **架構**：「三層架構」「Layer 1 寫入規則」「同構」「蜂王模式」「context 衛生」
- **派工與 BAT**：「auto-session」「YOLO 的斷點」「斷點 D」「塔台代決」「範圍權杖」「某個功能需要哪一版 BAT」
- **隔離與合併**：「worktree 隔離」「合併工單的三種模式」「斷點 E」
- **治理**：「落點檢查」「摘要授權規則」「單一權威定義」「版本治理」
- **學習與工具**：「知識管線」「Playbook」「FIELDGUIDE」「Workflow 和 CT 的關係」
- **升級**：「從 v4 升級，改了什麼」

想要的是確切的指令語法或設定值時，直接問 `ct-help` 會更快。

## 圖是現場畫的，而且可以點

Guide 的每個回答都盡量附一張 SVG 圖。圖不是事先做好的圖片，而是依你的問題現場生成；圖上的節點可以點，點下去就等於再問一句「介紹這個節點」，Guide 會去讀對應的教材章節，一層一層往下展開。

教材裡定義了 **17 種圖表類型**：

1. 生態系總覽圖
2. 工單生命週期圖
3. 三層架構圖（資料歸屬）
4. 塔台核心迴圈圖
5. 蜂王模式圖
6. 跨專案協調圖
7. BUG 狀態機圖
8. PLAN 狀態機圖
9. 歸檔流程圖
10. 知識成熟度管線圖
11. 研究型工單流程圖
12. BAT／YOLO 派工迴圈圖
13. Landing Zone Check 決策樹
14. frontmatter SoT／body mirror／drift 圖
15. EXP 狀態機圖
16. BAT 分頁關係與生命週期圖
17. 隔離工單合併圖

配色有固定意義：塔台用金色、Worker 用藍色、工單與狀態用青綠、學習與萃取用紫色。Portal 的主色「信標琥珀」就是沿用 Guide 用金色代表塔台的慣例。另外有一條繪圖禁忌：CT 裡有四組「L／Layer 編號」（資料歸屬的 Layer 1/2/3、知識存取的 L1/L2/L3、FIELDGUIDE 內部分段、知識成熟度 L0–L3），方向和意思都不同，不能畫在同一條軸上。

## 從哪裡開始讀

依你是誰、想解決什麼，Guide 的十份教材有不同的閱讀順序，見[學習路線](./learning-path)。

## 延伸閱讀

- Guide `SKILL.md` § Positioning、§ Command prefixes、§ When to use、§ Response modes、§ Diagram conventions
- Guide `references/diagrams.md` § 17 種圖表類型、§ 繪圖禁忌：四組「L／Layer 編號」不可畫在同一軸
- CT `version-governance.md` § 版號事實來源、§ 安裝／升級流程

Portal 是摘要，不具權威；與 Guide 或 CT reference 有出入時，以 reference 為準。
