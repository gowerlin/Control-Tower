---
title: 三層資料與記憶
description: Core Skills、Global、Project 三層資料怎麼載入、誰覆蓋誰；學習紀錄怎麼分流與晉升；塔台記憶怎麼存、換 Agent 時怎麼恢復。
---

# 三層資料與記憶

<p class="ct-lead">CT 把「隨版本更替的程式」和「隨使用累積的資料」分開放：skill 本體唯讀，跨專案的經驗放在使用者層，本專案的狀態跟著專案走。這樣升級 CT 時，學到的東西不會被覆蓋。</p>

## 三層：Core Skills、Global、Project

早期的塔台把學習紀錄直接寫回 skill 原始檔，結果每次升級 skill，學到的規則就被新版整份蓋掉。v3.3 把資料拆成三層，從結構上解決這個衝突：

<LayerStack />

| 層 | 路徑 | 生命週期 | 誰可以寫 |
|---|---|---|---|
| Layer 1 Core | `~/.claude/skills/`、`~/.codex/skills/`；plugin 安裝的 `~/.claude/plugins/`、`~/.codex/plugins/` 等（v5.14.0 起） | 隨 skill 版本，升級時整份覆蓋 | 日常運作中**沒有人**；唯一例外是工單明文授權的安裝或升級，plugin 安裝只能用 plugin 指令 |
| Layer 2 Global | `~/.claude/control-tower-data/` | 跨專案永久保存，升級不碰 | 塔台、`ct-evolve`（學習萃取、設定修改） |
| Layer 3 Project | `<專案根目錄>/_ct-workorders/` | 專案層永久保存，跟著專案進版控 | 塔台、Worker（工單執行、學習紀錄） |

設計理由有四點：

- **Core 唯讀**：升級安全，skill 定義不會在執行中被改掉。範圍是整個 skills 路徑，不只 skill 定義檔，理由見 [可逆與不可逆的界線](/deep/principles/boundaries)。
- **Global 跨專案**：通用的知識只學一次，所有專案共用。
- **Project 隔離**：某個專案特有的經驗，不會污染其他專案。
- **靜默降級**：Layer 2 不存在也能用，詳見下文。

::: tip 和「知識存取的三層」不同
這裡的三層回答「誰擁有、升級時會不會被覆蓋」。[認知作業系統](/deep/principles/cognitive-os) 提到的工單／learnings／FIELDGUIDE，是另一組依「容量和讀取成本」分的三層。
:::

## 載入順序與覆蓋優先級

塔台啟動時依序載入 **Core → Global → Project**；覆蓋時反過來，**Project ＞ Global ＞ Core**。不同種類的資料，合併方式不一樣：

| 類型 | 合併策略 |
|---|---|
| 設定值 | 欄位級覆蓋：Project ＞ Global ＞ 預設值。Project 只需寫出和 Global 不同的項目 |
| 擴展規則 | 附加，不覆蓋：Global 的 `extensions/` 和 Project 的 `_local-rules.md` 同時生效 |
| 學習紀錄 | 並列合併；同一個觸發條件下 Project 優先。編號分開：Global 用 `GP`／`GA`／`GSEQ`，Project 用 `P`／`A`／`SEQ` |
| Playbook | 同名時 Project 優先，不同名的兩層同時生效 |

設定值其實有四個來源，最上面還有一層 **session**：用 `*config` 即時修改，session 結束就消失。這四層只服務**塔台**。Worker 不讀設定檔來決定執行模式，模式由塔台派工時傳入（見 [塔台不讀程式碼](/deep/principles/tower-and-workers)）。

## 學習紀錄怎麼分流：Episodic、Tactical、Strategic

記憶可以分成好幾類，CT 對 semantic（`SKILL.md`）、episodic（工單歸檔）、procedural（skill 指令）都有現成的載體。比較難的是第四類 **strategic memory**：

| | Episodic（事件） | Strategic（策略） |
|---|---|---|
| 內容 | 事件紀錄 | 因果萃取 |
| 例子 | 「某次部署後流量尖峰，觸發了 thundering herd」 | 「固定間隔重試遇到流量尖峰會 thundering herd，改用指數退避加隨機抖動」 |
| 價值 | 可追溯 | 可重用 |

Strategic memory 是**蒸餾過的** episodic memory。很多團隊的事後檢討文件看了沒用，就是因為停在事件層，沒做蒸餾。

即使蒸餾過，學到的東西粒度也不同。CT 再把它拆成兩類：**Tactical** 是工具、語言、框架或某個 repo 特有的操作經驗，換技術棧就失效；**Strategic** 是技術更替後仍然成立的決策模式。不拆的話，少數高價值的 strategic 心得，會被大量 tactical 小技巧淹沒，塔台讀每一條都要付一樣的 context 成本。還不能泛化的原始事件，就先留在 Episodic。不確定時，寧可歸到 Tactical 或 Episodic，不誇大通用性。

`*evolve` 萃取時還有第二個問題：**寫到哪一層？** 通用的寫 Layer 2，本專案的寫 Layer 3，不確定的先寫 Layer 3、加上 `candidate: global` 標記，等累積驗證再說。

## 塔台記憶：`_tower-state.md` 與狀態面板

塔台的跨 session 記憶存在 `_ct-workorders/_tower-state.md`，有 7 個必要區段：

1. **起手式**：立即待辦、近期完成、快速連結
2. **基本資訊**：專案名稱、里程碑、塔台版本
3. **編號追蹤**：各類單據的最大編號
4. **進度快照**：目前 sprint 或里程碑的狀態
5. **本 Session 決策日誌**：精簡版，完整版在 `_decision-log.md`
6. **待處理事項**：未結的事
7. **環境快照**：環境掃描結果與掃描時間

塔台恢復啟動時會檢查這 7 個區段，缺少就提示補齊；每次處理完回報、做出決策、派出緊急工單，或使用者說「存檔」時更新。

啟動時，塔台依這份檔案輸出一個**狀態面板**：分支、工作區、進行中的工單、下一個工單編號、BAT 能不能派工、auto-session 的生效值與來源層、立即待辦。面板是格式範本，欄位有資料就顯示，沒有就寫「未知」，**不為了填欄位去跑額外掃描**。面板本身也是在節省 context。

為什麼要另外維護這份檔案，而不是每次掃工單或 git log？因為它把「哪些工單開著、哪些卡住、哪些等驗收」壓縮成一份啟動時一眼就能讀完的摘要，就像熱區快取。

## 晉升（Layer 3 → Layer 2）與降級

**晉升**：某個模式在 3 個以上專案驗證過、使用者也認可時，`ct-evolve` 會提議把它升到 Layer 2。使用者確認後，把它複製到 Layer 2 對應的檔案，改用 `GP`／`GA`／`GSEQ` 編號，並記下來源專案。**Layer 3 的原始紀錄保留，不刪除**，日後要追溯「這條規則從哪來」時還找得到。

**降級**是指 Layer 2 不完整時，塔台怎麼照常運作：

| 情境 | 行為 |
|---|---|
| Layer 2 目錄不存在 | 靜默降級，只用 Layer 1＋Layer 3 |
| Layer 2 部分檔案缺失 | 跳過缺的檔案，不報錯 |
| Layer 2 檔案格式錯誤 | 警告使用者，該檔改用預設值 |

這也是 Layer 2 「提示建立、但不強制」的原因：沒有它，CT 一樣能用，只是少了跨專案的經驗。

## 換 Agent 接手時怎麼恢復

記憶協議的設計目標是 **AI-agnostic**：任何能讀寫 `.md` 檔的 AI agent 都能使用。換一個 agent 接手塔台時，恢復順序是：

1. 讀 `_tower-state.md`，恢復進度
2. 讀 `_decision-log.md`，理解決策脈絡
3. 讀 `_learnings.md`，載入學習經驗
4. 掃描 `_ct-workorders/T*.md`，驗證實際狀態
5. 顯示恢復結果：上次與這次的 agent、決策筆數、學習模式數量

讀資料時，Layer 3 優先（專案狀態），再讀 Layer 2（全域設定和學習），Layer 1 的內建預設值只在前兩層缺資料時才用。

第 4 步是關鍵：塔台記憶只是摘要，工單檔案才是事實（見 [檔案即真相來源](/deep/principles/files-as-truth)）。兩邊說法不同時，以工單檔案為準修正塔台記憶。

## 延伸閱讀

- `control-tower/references/data-layer-architecture.md` § 架構總覽、§ 核心原則、§ 載入合併邏輯、§ 晉升流程（Layer 3 → Layer 2）、§ 降級行為
- `control-tower/references/doctrine.md` § CT 三層資料結構的設計依據、§ Episodic vs Strategic vs Tactical 的分流
- `control-tower/references/memory-protocol.md` § _tower-state.md（塔台記憶）、§ 塔台狀態面板、§ 跨 Agent 狀態恢復
- `control-tower/references/self-learning-core.md` § Global/Project 分流寫入
- `control-tower-guide/references/three-layer-arch.md` § 為什麼需要三層分離？、§ 合併規則、§ 設定的四層覆蓋、§ 學習紀錄的分流、§ 設計哲學

<p class="ct-note">Portal 是摘要，不具權威。內容與 CT reference 有出入時，以 reference 為準。</p>
