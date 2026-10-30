# Control Tower 圖表樣板

本檔只定義**圖表規格**：什麼圖、什麼節點、什麼連線、點擊節點後 drill-down 到哪個 reference。
圖的內容一律以各 reference 的正文為準；本檔與正文不一致時，以正文為準並修正本檔。

## 顏色規範

| 元素 | Class | 用途 |
|------|-------|------|
| Tower（塔台/指揮） | `c-gold` | control-tower、塔台端動作（派工、讀回報、決定下一張） |
| Worker（執行） | `c-blue` | ct-exec、ct-done、Worker 端動作 |
| 工單/狀態 | `c-teal` | 工單流轉、狀態機、工單檔案 |
| 學習/萃取 | `c-purple` | ct-evolve、ct-insights、ct-fieldguide、PLAN 狀態 |
| 查詢/輔助 | `c-gray` | ct-status、ct-help、不阻斷的記錄／資訊節點 |
| BMad 整合 | `c-coral` | BMad-Method 相關、BUG 狀態 |
| 進階模式 | `c-amber` | 跨專案、中斷、多塔台、決策菱形、斷點 |
| 三層架構 | `c-green` | Layer 1/2/3、通過／歸檔等正向結果 |

不新增 class：v5 新概念沿用既有色——BAT 派工沿用 Tower／Worker 兩色（依動作發生在哪一端），
治理護欄的判定菱形用 `c-amber`、STOP 結果用 `c-coral`、WARN／記錄用 `c-gray`、PASS 用 `c-green`。同一張圖若借用顏色，須附圖例。

## SVG Setup（所有圖表通用）

```svg
<svg width="100%" viewBox="0 0 680 [H]">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
```

## Clickable Node 模式

```svg
<g class="node c-[color]" onclick="sendPrompt('介紹 [topic] 的詳細說明')">
  <rect x="X" y="Y" width="W" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="CX" y="CY-8" text-anchor="middle" dominant-baseline="central">標題</text>
  <text class="ts" x="CX" y="CY+10" text-anchor="middle" dominant-baseline="central">→ 副標</text>
</g>
```

每張圖的 **Drill-down** 列出：點哪個節點 → `sendPrompt()` 文字 → 回答時要讀的 reference 與章節。

## 繪圖禁忌：四組「L／Layer 編號」不可畫在同一軸

| 編號 | 指什麼 | 方向 | 出處 |
|------|-------|------|------|
| Layer 1/2/3 | 資料歸屬：Core／Global／Project | 1 = 最底層的 skill 本體 | `three-layer-arch.md` 上半部 |
| L1/L2/L3（知識存取） | FIELDGUIDE／learnings／工單 | **與上列相反**：L1 = 最小最熱 | `three-layer-arch.md` § 三層與 Memory Hierarchy 同構 |
| L1/L2/L3（FIELDGUIDE 內部） | 設計哲學／決策樹／專案快照 | 文件內部分段 | `advanced-patterns.md` § FIELDGUIDE 教戰手冊 |
| L0–L3（知識成熟度管線） | 觀察／驗證／Playbook／Skill | 晉升順序 | `concepts.md` § 知識成熟度管線 |

需要同時呈現兩組時，畫成**並列的獨立面板**，各自有軸與標題，面板之間不畫「Layer N ↔ LN」的對應線。

## 17 種圖表類型

### 1. 生態系總覽圖
**When**：「Control Tower 有哪些元件」「整體架構」「`/` 和 `$` 差在哪」
**節點**：中央 `control-tower`（`c-gold`，副標 `*` 內建命令）；環繞七個輔助 skill——`ct-exec`、`ct-done`（`c-blue`）、`ct-status`、`ct-help`（`c-gray`）、`ct-evolve`、`ct-insights`、`ct-fieldguide`（`c-purple`）。每個節點副標寫 `/name`／`$name`
**連線**：塔台 → `ct-exec`「工單」；`ct-exec` → 塔台「回報」；`ct-done`、`ct-status` → `ct-exec` 虛線「引用落點檢查」；`ct-evolve` → `ct-fieldguide`「[FG-CANDIDATE]」
**Drill-down**：任一 skill → `sendPrompt('介紹 [skill] 的角色')` → `ecosystem.md` § 角色定位；`/`／`$` 標籤 → `ecosystem.md` § 三軌前綴

### 2. 工單生命週期圖
**When**：「工單怎麼流轉」「狀態機」「PARTIAL 之後呢」
**節點**：三個背景容器即狀態分桶——**Active**（`PENDING`、`IN_PROGRESS`、`PAUSED`、`URGENT`）、**Needs Tower judgment**（`PARTIAL`、`BLOCKED`、`FAILED`、`INTERRUPTED`、`UNKNOWN`）、**Final**（`DONE`、`FIXED`（驗證政策允許後）、`ABANDONED`／superseded）。狀態節點 `c-teal`
**連線**：主線 `PENDING → IN_PROGRESS → DONE`（實線）；`IN_PROGRESS` → `FIXED`／`PARTIAL`／`FAILED`／`BLOCKED`／`INTERRUPTED`；`IN_PROGRESS ⇄ PAUSED`（`*pause`／`*resume`）；`URGENT` 從圖外直接進入、**不經 PENDING**；`PARTIAL → DONE` 虛線「resolved PARTIAL 補正」；`→ ABANDONED` 虛線「範圍決策退役」
**不得出現**：任何「待審」中間態——審查是另一張工單
**Drill-down**：`PARTIAL` → `sendPrompt('介紹 resolved PARTIAL 補正')` → `work-order-lifecycle.md` § resolved PARTIAL → DONE；分桶容器 → `work-order-lifecycle.md` § 狀態分桶

### 3. 三層架構圖（資料歸屬）
**When**：「三層是什麼」「設定覆蓋」「為什麼不能在 skills 目錄放備份」
**節點**：三個水平容器由下到上——Layer 1 Core `~/.claude/skills/`（整個路徑，附註 Codex 端 `~/.codex/skills/`；v5.14.0 起再附註 plugin 安裝路徑 `~/.claude/plugins/`、`$CODEX_HOME/plugins/`，同屬 Layer 1）、Layer 2 Global `~/.claude/control-tower-data/`、Layer 3 Project `_ct-workorders/`（`c-green`）。Layer 1 容器**外側**畫兄弟節點 `~/.claude/skill-backups/`（`c-gray`，附註 Codex 端 `~/.codex/skill-backups/`），與 `skills/` 同層、不在其內
**連線**：設定覆蓋箭頭 Default → Global → Project → Session（右側直排）；Layer 1 容器邊框標註「日常不寫入；唯一例外 = 工單明文授權的安裝（plugin 只能用 plugin 指令）」
**變體（同構對照）**：被問到「三層與 memory hierarchy」時，改畫兩個並列面板（資料歸屬 vs 知識存取），遵守上方繪圖禁忌
**Drill-down**：Layer 1 → `sendPrompt('介紹 Layer 1 寫入規則')` → `three-layer-arch.md` § Layer 1 寫入規則；`skill-backups` → `governance.md` § Layer 1 寫入機制；覆蓋箭頭 → `three-layer-arch.md` § 設定的四層覆蓋

### 4. 塔台核心迴圈圖
**When**：「塔台怎麼運作」「基本流程」
**節點**：環形——需求對齊 → 產生工單（frontmatter） → 派工 → Worker 執行（`ct-exec`） → 回報（固定訊息） → 塔台讀回報區驗證證據 → 更新狀態、決策、學習 → 下一張
**連線**：「派工」與「回報」兩段各標三條細分支：手動／BAT／YOLO；「下一張」可分出 Renew、結案、升級求助
**Drill-down**：派工或回報 → `sendPrompt('介紹手動、BAT、YOLO 三種形態')` → `work-order-lifecycle.md` § 核心迴圈；BAT 細節 → `bat-integration.md`（圖見 16）

### 5. 蜂王模式圖
**When**：「為什麼塔台不碰程式碼」「角色分離」
**節點**：左欄 Tower（蜂王，`c-gold`）列 Hard Boundaries 六條的短標；右欄 Worker（工蜂，`c-blue`）列寫程式、測試、debug、讀檔；中間工單檔（`c-teal`）
**連線**：Tower → 工單 → Worker 雙向；Tower 欄底部附一個小節點「唯一直接處理例外：單模組、不涉邏輯」
**Drill-down**：Hard Boundaries → `sendPrompt('介紹塔台 Hard Boundaries')` → `concepts.md` § Hard Boundaries；工單 → `concepts.md` § Worker 無狀態、塔台有狀態

### 6. 跨專案協調圖
**When**：「跨專案怎麼做」「COORDINATED 工單」「HANDOVER 是什麼」
**節點**：兩個專案塔台並排（`c-amber`）；五種類型——LOCAL、COORDINATED、DELEGATE 為實線框（工單），HANDOVER、ADVISORY 為虛線框（非工單通道）；接收方的 `_reply-*.md`（含異議段落）
**連線**：COORDINATED 在上方連接兩塔台；DELEGATE 在下方指向各自的 Worker；HANDOVER → `ACKNOWLEDGED`（→ 建立 DELEGATE）或 `DECLINED`；ADVISORY 只指向對方、無後續箭頭
**Drill-down**：HANDOVER／ADVISORY → `sendPrompt('介紹 HANDOVER 與 ADVISORY')` → `advanced-patterns.md` § HANDOVER 與 ADVISORY 怎麼運作；異議段落 → `advanced-patterns.md` § 回覆稿的異議段落；
實例（BAT 塔台以 `CT-T###` 委派 CT 功能）→ `sendPrompt('介紹 BAT 塔台與 CT 塔台怎麼協作')` → `bat-integration.md` § 兩座塔台怎麼協作；
跨 session 通知對方塔台（v5.9.0）→ `sendPrompt('塔台怎麼用跨 session 訊息找到對方塔台')` → `advanced-patterns.md` § 跨 session 通知對方塔台

### 7. BUG 狀態機圖
**When**：「BUG 怎麼流轉」「VERIFY 是什麼」「BUG 生命週期」
**節點**：`OPEN → FIXING → FIXED → VERIFY → CLOSED`，加 `WONTFIX`；共 6 個狀態（`c-coral`，`VERIFY` 用 `c-amber`）
**連線**：主線實線；`FIXED → FIXING` 虛線「驗證失敗」；`WONTFIX` 以一條橫跨的虛線標「任何階段可標記」
**Drill-down**：`FIXED` 或 `VERIFY` → `sendPrompt('介紹 BUG 驗收流程')` → `work-order-lifecycle.md` § BUG 生命週期

### 8. PLAN 狀態機圖
**When**：「PLAN 怎麼流轉」「規劃單據」「PLAN 生命週期」
**節點**：`IDEA → PLANNED → IN_PROGRESS → DONE`，加 `DROPPED`；共 5 個狀態（`c-purple`）
**連線**：`DROPPED` 只從 `IN_PROGRESS` 分出（「放棄，需記錄原因」）
**Drill-down**：`IDEA` → `sendPrompt('介紹 PLAN 單據的使用場景')` → `work-order-lifecycle.md` § PLAN 生命週期、`concepts.md` § 多單據類型哲學

### 9. 歸檔流程圖
**When**：「歸檔怎麼運作」「`*archive`」「熱區冷區」
**節點**：三個決策菱形（`c-amber`）——「已是終態？（依單據類型）」→「超過 `archive_days`？（預設 7）」→「仍被引用？」；結果「歸檔候選」（`c-green`）／「保留」（`c-gray`）
**連線**：任一菱形「否／是被引用」→ 保留；第三個菱形旁列引用式豁免三類：進行中單據引用、塔台釘選或待處理事項提及、跨專案對方未完成。另一條虛線「`*archive T0001` 強制歸檔：跳過天數與引用檢查，顯示警告」
**右側附註**：`_ct-workorders/_archive/{workorders,bugs,plans}/`（EXP 放 `workorders/`）；`*sync` 嚴格跳過冷區
**Drill-down**：歸檔結果 → `sendPrompt('介紹 archive 命令的完整用法')` → `advanced-patterns.md` § 歸檔操作；豁免 → `concepts.md` § 熱區／冷區分離

### 10. 知識成熟度管線圖
**When**：「知識管線」「Playbook」「`*evolve --playbook`」「學習怎麼晉升」
**節點**：L0 觀察（🔵，`c-gray`）→ L1 驗證（`validated`／🟢，`c-teal`）→ L2 Playbook（`_playbooks/`，`c-purple`）→ L3 Skill（`c-gold`）；每節點標存放位置與晉升條件
**連線**：`*evolve`（專案層 2+ 工單重複；全域 🟢 要 2+ 專案，條件見 CT `self-learning-core.md` § 置信度系統）、`*evolve --playbook`（validated + 使用者確認）、`*evolve --skill`（3+ 專案）；最後一段畫成兩截——`*evolve --skill` 只到「skill brief」節點，brief → L3 為虛線「使用者自行呼叫 `skill-creator`」
**Drill-down**：L2 → `sendPrompt('介紹 Playbook 引擎的運作方式')` → `integration.md` § Playbook 引擎；brief 虛線 → `concepts.md` § 知識成熟度管線
**Workflow 分支（v5.10.0+）**：從 L0／L1 另拉一條 `c-purple` 分支「`[WF-CANDIDATE]` → `ct-evolve --workflow` → `_workflows/` 🔵 知識卡（brief）」；卡片 → 腳本為虛線「另開工單、使用者確認 brief 後」；分支旁註「🔵→🟡 回測、可降級」。分支不接到 L2 Playbook
**注意**：這裡的 L0–L3 是晉升順序，不是三層架構（見繪圖禁忌）

### 11. 研究型工單流程圖
**When**：「研究型工單」「Worker 可以提問嗎」「Renew」「yolo Worker 有問題怎麼辦」「塔台代決」
**節點**：四列——塔台（`c-gold`）／工單檔（`c-teal`）／使用者（`c-gray`）／Worker（`c-blue`）
**連線**：塔台派單（`type: research`，`CT_INTERACTIVE`）→ Worker 執行 → Worker 向**使用者**選項式提問（上限 `research_max_questions`）→ 使用者回答 → Worker 繼續；需要塔台補充時：塔台在工單寫入「塔台補充（Renew #N）」、`renew_count` +1 → 使用者對 Worker 說「重讀工單」→ Worker 只讀最新 Renew 區段 → 繼續 → 收尾（可決策結論 + Renew 歷程）。Renew 循環用虛線（可多次）
**yolo 變體（v5.5.0）**：Worker 向使用者提問那一段換成提問往返——Worker → 工單檔 `### 待塔台決策` `Q-n`（`c-teal`）→ `T#### 提問` → 塔台代決（`c-gold`；範圍變更／不可逆／對外發布／需要偏好 → 虛線轉問使用者）→ 工單檔新增 `塔台答覆 Q-n` → Worker 重讀工單後繼續；逾時虛線 → `BLOCKED` → Renew 區段答覆 → 重新派工。兩種模式畫成兩條泳道並標明「非 yolo」／「yolo」。v5.7.0 的 BAT 結構化通道是同一個往返換了傳輸方式（題目照樣先寫進工單檔），畫在圖 12；本圖不另畫
**不得畫成**：非 yolo 泳道裡 Worker 直接向塔台提問；yolo 泳道裡 Worker 向使用者提問；塔台對 Worker 分頁送按鍵代答；Worker 自己發起 Renew
**Drill-down**：Renew → `sendPrompt('介紹 Worker Renew 機制')` → `work-order-lifecycle.md` § Worker Renew 機制；提問 → `work-order-lifecycle.md` § 互動由誰決定；yolo 提問往返 → `sendPrompt('介紹 yolo 提問通道')` → `work-order-lifecycle.md` § yolo 提問通道

### 12. BAT／YOLO 派工迴圈圖（v5 新增；v5.2.0 補塔台分頁宣告、收單後回收；v5.2.4 補 Worker 分頁 → `Forbidden` 分支；v5.3.0 加隔離工單註記；v5.5.0 補提問往返與斷點 D；v5.6.0 補 Worker 啟動確認；v5.7.0 補 BAT 問答通道分支；v5.8.0 補 codex 信號註記）
**When**：「BAT 怎麼派工」「YOLO 怎麼跑」「Worker 怎麼通知塔台」「塔台分頁標題」「Worker 分頁會自己關嗎」「在 Worker 分頁開塔台會怎樣」「`Forbidden`」「斷點 D」「Worker 在等我回答」「Worker 有沒有真的起來」「exit `8`」「`--wait-started`」
**節點**：塔台啟動 → 分頁角色宣告（`c-gold`，標 `--set-role tower --mode <m>`；結果節點 `c-gray`：`已設定`／`不支援（BAT 太舊）`／`略過（非 BAT）`，三者都往下走）→ 塔台（`auto-session`）→ 派工 helper（標 `--cwd`、`--workspace`、`--mode`、`--[no-]interactive`；yolo 一律 `--no-interactive`）→ BAT 開 Worker 終端（注入 `CT_MODE`、`CT_INTERACTIVE`、`BAT_TOWER_TERMINAL_ID`；由 BAT 組 `/` 或 `$`）→ Worker `ct-exec` → 收尾通知 → 塔台讀回報 → 回收 Worker 分頁（`c-gray`，註「`worker_auto_close: done`、`DONE`、不 Renew 才做；失敗不影響收單」）→ 斷點檢查菱形（`c-amber`：A／B-1／B-2／C）→ 挑下一張（拆單建議表）。
提問往返（v5.5.0，只有 yolo）：Worker `ct-exec` 拉一條虛線小迴圈「`T#### 提問`」→ 塔台代決（`c-gold`）→ 工單檔「`塔台答覆 Q-n`」（`c-teal`）→ 回到 Worker，不經過讀回報、回收與斷點菱形（不是收尾）。BAT 通道（v5.7.0，BAT `>= 0.7.0-pre.7`）：同一個小迴圈旁並排一條實線分支——Worker「題目寫進工單檔並 commit」（`c-teal`）→「`--ask`」→ 塔台「`bat_list_questions` → `--answer`」（`c-gold`）→ Worker「`bat_wait_question` 收到答覆」，註「工單不寫答覆行；Worker 記互動紀錄」；分支上拉一條虛線「失效（BAT 太舊／`lost`／取消／答覆失敗）→ 回到工單檔往返」接到原本那條迴圈，另一條虛線「`expired` → `BLOCKED` + Renew」。斷點 D（v5.5.0）：塔台旁一個 `c-gray` 節點「查到 `blocked`（MCP）→ 以分頁標題告知使用者」，註「不暫停、不代答；只在本來就在看 Worker 時查」（v5.8.0 起註記加「hook 的三種原因或 codex 的 `input`」），畫在斷點菱形之外；v5.7.0 起這個節點旁加一條虛線「`blockedReason: tower` → 不是斷點 D，去讀題答覆」接到 BAT 通道分支的塔台節點。
Worker 啟動確認（v5.6.0）：派工 helper 旁加註 `［--wait-started 30000］`；「BAT 開 Worker 終端」與「Worker `ct-exec`」之間插一個「等待啟動確認」菱形（`c-amber`，註「helper 最多等 30 秒」），分三條往下：`started: <時間>`（exit `0`，已啟動）與 `started: unknown`（exit `0`，無法判定、照現行流程）都接到 Worker `ct-exec`；exit `8`（`started: unconfirmed`）拉到一個 `c-gray` 節點「分頁在、未確認啟動 → MCP 看輸出或以分頁標題提醒使用者」，註「不重派」，再以虛線接回塔台等回報。派工 helper 另拉一條虛線「exit `1` + `Unknown option '--wait-started'`（舊 BAT，不建分頁）→ 去掉參數重派一次」回到派工 helper，註「本 session 不再帶」。v5.8.0：菱形註記加「codex `>= 0.163.0` 也有信號（BAT `>= 0.7.0-pre.9`）；較舊 codex 走 `unknown`」，exit `8` 節點註記加「codex 常見原因：Trust this folder? 啟動畫面」；不新增節點。
隔離工單（v5.3.0）只在派工 helper 旁加註 `［--isolation worktree］`、回收節點加註 `--worktree keep`，並從讀回報拉一條虛線「合併（見圖 17，斷點 E）」；隔離與合併的細節不畫進本圖
**連線**：通知分三條——`on`「預填，使用者送出」、YOLO「自動送出」、`ask`／`off`「手動帶回」；斷點命中或使用者喊停 → 「暫停，交還使用者」（使用者中斷另標「≠ 斷點」）；無斷點 → 回到「塔台（`auto-session`）」，形成迴圈；`*config auto-session <m>` 改模式 → 虛線回到分頁角色宣告（帶新 `--mode` 再宣告一次）；分頁角色宣告與派工 helper 各拉一條虛線分支「Worker 分頁（有 `BAT_TOWER_TERMINAL_ID`，BAT `>= 0.7.0-pre.1`）→ exit `1`」（`c-gray`，註「stderr 含 `Forbidden` 只多一句提示：請在一般分頁啟動塔台」）——宣告這條併入 `不支援（BAT 太舊）` 照常往下走，派工這條接到側欄降級鏈；派工另可標 `RECOVERY_PENDING`（BAT Recovery 提示未回答，不自動重派）
**不得畫成**：迴圈每輪都回到分頁角色宣告（只在啟動與改模式時宣告）；宣告失敗擋住塔台啟動；Worker 呼叫 `--set-role`；回收失敗導致工單狀態改變或觸發斷點；`Forbidden`／`RECOVERY_PENDING` 分支觸發重試或自動重派、或由 stderr 決定是否降級；塔台因有 `BAT_TOWER_TERMINAL_ID` 而拒絕啟動或預先跳過呼叫；`T#### 提問` 畫成收單；BAT 通道分支跳過「題目寫進工單檔」；`blockedReason: tower` 畫成告知使用者；斷點 D 暫停迴圈；塔台對 Worker 分頁送按鍵代答或背景輪詢 `blocked`；exit `8` 接到降級鏈或重派；`started: unknown` 畫成失敗；舊 BAT 的去參數重派畫成迴圈（只一次）
**側欄**：降級鏈 BAT → 新分頁 → 剪貼簿 → 文字提示；成功判讀以 exit code 為主規則，`bat-scripts.log` 只供事後查證；helper 一律以 `${BAT_HELPER_NODE:-node}` 執行；圖中提到分頁一律用分頁標題（`<Agent 顯示名> · Tower`／`· Worker · T####`），不畫 terminal ID（v5.2.5）
**Drill-down**：分頁角色宣告 → `sendPrompt('介紹塔台分頁角色宣告')` → `bat-integration.md` § 塔台分頁角色宣告（v5.2.0）；BAT 終端 → `sendPrompt('介紹 BAT 兩組環境變數')` → `bat-integration.md` § 兩組環境變數，兩個角色；回收 → `sendPrompt('介紹收單後回收 Worker 分頁')` → `bat-integration.md` § 收單後回收 Worker 分頁；斷點 → `runtime-dispatch.md` § YOLO 與斷點；`CT_MODE` → `runtime-dispatch.md` § Worker 無狀態；`Forbidden` 分支 → `sendPrompt('介紹 BAT 範圍權杖與分頁角色')` → `bat-integration.md` § 範圍權杖與分頁角色；提問往返 → `sendPrompt('介紹 yolo 提問通道')` → `work-order-lifecycle.md` § yolo 提問通道；斷點 D → `sendPrompt('介紹斷點 D')` → `bat-integration.md` § 斷點 D；等待啟動確認 → `sendPrompt('介紹 Worker 啟動確認')` → `runtime-dispatch.md` § Worker 啟動確認

### 13. Landing Zone Check 決策樹（v5 新增）
**When**：「落點檢查」「WRONG_REPO」「`expect_missing` 是什麼」
**節點**：起點「任何寫入之前」→ C-0「frontmatter 有 `repo`？」→「`repo` == repo 根目錄名？」→ C-1「工單在 REPO_ROOT 下？」→ C-3「`affects_files` 抽查：全部不存在？」→ C-2「branch 相符？」→ 記錄結果（`PASS`／`WARN`／`STOP`，附 `BAT_WORKSPACE_ID` 證據）
**連線**：
- C-0 不符 → STOP `WRONG_REPO_CONFIRMED`（`c-coral`，註「不得改 `repo`」）；相符 → C-3 只記錄、不 STOP；無 `repo` 欄位 → WARN，C-3 保有 STOP 權
- C-1 否 → STOP
- C-3 全部不存在：C-0 已通過或 `expect_missing: true` → WARN 繼續；無 `repo` 欄位 → STOP `WRONG_REPO_SUSPECTED`
- C-2 不符 → 只警告或詢問，**永不 STOP**
- 不是 git repo → WARN，跳過 C-0／C-1／C-3
**側欄**：C-4 workspace 一致性灰色虛線節點「刻意不做」；`expect_missing` 標「只有塔台能設」；C-0 旁加註「有 `CT_HOME`（worktree，v5.3.0）時改比 `CT_HOME` 的目錄名，STOP 語意不變」
**Drill-down**：C-0 → `sendPrompt('介紹為什麼身分不能用路徑證明')` → `governance.md` § Landing Zone Check；`CT_HOME` 加註 → `governance.md` § 在 worktree 裡：換比對對象，不換語意；C-3 → `governance.md` § C-3 為什麼從承重降為輔助；在工單流程中的位置 → `work-order-lifecycle.md` § Landing Zone Check

### 14. frontmatter SoT／body mirror／drift 圖（v5 新增）
**When**：「frontmatter 和表格哪個算數」「drift 怎麼處理」「SoT」
**節點**：一個工單檔容器（`c-teal`）切上下兩格——上「YAML frontmatter：機器 SoT」、下「body 元資料表：人類鏡像」；左側讀者 `*sync`／`ct-status`／BAT／腳本；右側讀者「人類」；`*sync` drift 檢查菱形（`c-amber`）
**連線**：機器讀者 → frontmatter；人類 → body；Worker 寫入時兩格都寫（frontmatter 為準、body 同步鏡像）；drift → 「warning」（`c-gray`），另畫一條打叉虛線「不自動覆寫 body」；缺 frontmatter → 「legacy 表格 fallback + 警告」
**對照小節點**：`_bug-tracker.md`／`_backlog.md`（`schema_kind: index`，生成物，可整檔重寫）
**頁尾**：跨來源優先級 工單檔案 > `sprint-status.yaml` > 塔台記憶
**Drill-down**：frontmatter → `sendPrompt('介紹工單 frontmatter 欄位地圖')` → `work-order-lifecycle.md` § frontmatter 欄位地圖；兩段式 → `concepts.md` § 事實來源：兩段式

### 15. EXP 狀態機圖（v5 新增）
**When**：「EXP 怎麼流轉」「實驗單據」「實驗失敗怎麼記」
**節點**：`EXPLORING`（建立即進入）→ `CONCLUDED`／`ABANDONED`；共 3 個狀態（`c-teal`）
**連線**：`EXPLORING → CONCLUDED`「得出結論（『這條路不通』也是結論）」；`EXPLORING → ABANDONED`「無法繼續或已無意義」
**側欄**：git worktree 零污染丟棄；歸檔進 `_archive/workorders/`
**不得出現**：`PENDING`、`DONE`、`FAILED` 等工單狀態
**Drill-down**：`CONCLUDED` → `sendPrompt('介紹 EXP 單據為何沒有失敗狀態')` → `work-order-lifecycle.md` § EXP 生命週期

### 16. BAT 分頁關係與生命週期圖（v5.3.0 新增）
**When**：「BAT 和 CT 怎麼分工」「一張 Worker 分頁從開到關」「worktree 隔離派工」「`CT_HOME` 是什麼」「BAT MCP」「`--worktree-status`」「`agentStarted`」
**節點**：三欄——左「塔台分頁」（`c-gold`，標題寫 `<Agent 顯示名> · Tower`）；中「BAT」容器（`c-gray`，借用輔助色，須附圖例），內含 helper（`bat-terminal.mjs`／`bat-notify.mjs`）與 RemoteServer 兩個節點；
右「Worker 分頁」（`c-blue`，標題寫 `<Agent> · Worker · T####`），其下方一個**虛線**容器「worktree `ct/T####`（可選，`isolation: worktree`）」（`c-blue`，Worker 端）。
底部橫跨一個「主 checkout `_ct-workorders/`」節點（`c-teal`）
**連線**（依時間編號 ①–⑤，由上而下）：
- ① 塔台 → helper：`--set-role tower --mode <m>`（啟動與改模式時）
- ② 塔台 → helper → RemoteServer → 建 Worker 分頁：標 `--workspace`、`--cwd`、`--mode`、`--[no-]interactive`、`--agent default`、`--skill`＋`--workorder`、`［--isolation worktree］`、`［--wait-started 30000］`（v5.6.0：helper 等 Worker 的 claude 啟動後才回，exit `8` = 分頁在、未確認，不重派）；
  建立分頁的箭頭旁註「注入 `BAT_TOWER_TERMINAL_ID`、`CT_MODE`、`CT_INTERACTIVE`；隔離另加 `CT_HOME`／`CT_WORKTREE`／`CT_WORKTREE_BRANCH`／`CT_WORKTREE_BASE`」
- ③ Worker → `bat-notify` → 塔台分頁：「`on` 預填／yolo 自動送出」；Worker → 主 checkout `_ct-workorders/`「寫回報」——**隔離時也從 worktree 容器指向主 checkout**，不指向 worktree 裡的副本
- ④ 塔台 → helper：`--close-worker`（`worker_auto_close: done`；隔離工單加 `--worktree keep`），Worker 分頁變灰；
  v5.12.0 另一條虛線「重派前：`--close-worker … --delay-ms 0`」從塔台指向舊 Worker 分頁、再回到 ②（不受 `worker_auto_close` 影響）
- ⑤ 塔台 → helper：`--worktree remove`（只有隔離工單，**合併完成後**），worktree 容器變灰；分支節點保留，註「保留到使用者同意刪除」
- 塔台 ⇢ BAT 一條雙向虛線「唯讀查詢：`--worktree-status`／`mcp__bat__*`」（`c-gray`），註「舊 BAT：④ 之前查；BAT `>= 0.7.0-pre.4`：④ 之後也可查」
**頂部分工帶**：「BAT：提供能力、定介面契約」｜「CT：依契約呼叫、只看 exit code」
**不得畫成**：BAT 執行 merge 或 commit；Worker 呼叫 `--set-role`、派工或 `--close-worker`；Worker 把工單寫進 worktree 裡的 `_ct-workorders/`；
隔離派工失敗後自動改成非隔離派工（失敗只畫一條到「暫停，使用者決定」的虛線）；MCP 畫成必經路徑；分頁上標 terminal ID（一律用分頁標題）
**側欄**：BAT 版本對照（v5.1.0 `>= 0.6.1-pre.4`、v5.2.0 `>= 0.6.1-pre.6`、v5.2.4 `>= 0.7.0-pre.1`、v5.3.0 `>= 0.7.0-pre.2`、v5.4.0 `>= 0.7.0-pre.4`、v5.5.0 斷點 D `>= 0.7.0-pre.4`、v5.5.1 `blockedReason` 準確 `>= 0.7.0-pre.5`、v5.6.0 Worker 啟動確認 `>= 0.7.0-pre.6`、v5.7.0 Worker 問塔台 BAT 通道 `>= 0.7.0-pre.7`、v5.8.0 codex OSC 7501 `>= 0.7.0-pre.9`）；查詢降級鏈 MCP → helper → 檔案（MCP 錯誤取不到 code 時也改走 helper，v5.3.2）
**與圖 12 的分工**：圖 12 畫時間上的派工迴圈與斷點，本圖畫三方的關係與單張分頁的一生；不合併成一張
**Drill-down**：分工帶 → `sendPrompt('介紹 BAT 與 CT 的分工原則')` → `bat-integration.md` § 分工原則；① → `bat-integration.md` § 塔台分頁角色宣告；
② → `sendPrompt('介紹 worktree 隔離派工')` → `bat-integration.md` § worktree 隔離派工；③ → `bat-integration.md` § Worker 執行與通知；
④⑤ → `bat-integration.md` § 收單後回收 Worker 分頁（重派前那條虛線 → § 重派前回收舊 Worker 分頁）；唯讀查詢 → `sendPrompt('介紹 BAT 查詢通道')` → `bat-integration.md` § 查詢通道；
版本側欄 → `bat-integration.md` § 版本對照表；worktree 容器 → `work-order-lifecycle.md` § worktree 隔離與合併工單

### 17. 隔離工單合併圖（v5.3.0 新增；v5.3.1 清理節點加整合 worktree detach；v5.4.0 查詢節點註解分 BAT 版本）
**When**：「合併工單」「隔離工單做完之後怎麼辦」「三種合併模式」「斷點 E」「塔台能不能直接合併」
**節點**：Worker 回報 `DONE`（`c-blue`，副標「含隔離分支證據」）→ 查 `--worktree-status`（`c-gray`，註「舊 BAT：回收分頁之前；BAT `>= 0.7.0-pre.4`：回收後也可查（`source`）；查不到改用 git」）→ 回收 `--worktree keep`（`c-gray`）
→ 判準菱形「直接合併五條全部成立？」（`c-amber`）→ 是：模式 ① 塔台直接合併（`c-gold`）；否：塔台選模式菱形（`c-amber`）→ ② 衝突解決／③ 等價移植 合併工單（`c-teal`）→ Worker 執行（`c-blue`）
→ 收單 SHA 比對（`c-gold`）→ 斷點 E 菱形（`c-amber`）→ `main --ff-only`（`c-green`）→ 清理 `--worktree remove`＋整合 worktree `switch --detach`（`c-gray`，註「分支保留到使用者同意」）
**背景容器**：虛線容器「整合 worktree」（`c-gray`）框住模式 ① 的合併與 ②／③ 的 Worker 執行；`main` 節點畫在容器外
**連線**：模式 ① 途中衝突 → 虛線「`merge --abort`，改派 ②」；② 的 Worker 超出解衝突 → `PARTIAL`，虛線「建議改 ③」回到塔台選模式菱形；
SHA 比對任一步不成立 → 「暫停，交還使用者」；斷點 E 旁標「非 yolo 一律暫停；yolo：① 判準仍成立、② 驗收全綠且無範圍外檔案 → 自動；③ 一律暫停」；
`--ff-only` 被重疊髒檔拒絕 → 「告知使用者，不 stash」（`c-gray`）
**不得畫成**：BAT 執行合併；Worker 自己改 `merge_mode` 或自行升級到 ③；`behind == 0` 時直接 `--ff-only ct/T####`（一律經整合 worktree `--no-ff`）；
在主 checkout 或被合併工單的 worktree 合併；合併完成立即刪分支；非隔離工單進入本圖
**頁尾**：取不到的判準資料一律算不通過
**Drill-down**：判準菱形 → `sendPrompt('介紹塔台直接合併的判準')` → `work-order-lifecycle.md` § 塔台直接合併的判準精神；
三種模式 → `sendPrompt('介紹三種合併模式')` → `work-order-lifecycle.md` § 合併：為什麼交給工單，而不是 BAT；
整合 worktree、`--no-ff`、`--ff-only` → `governance.md` § 合併護欄；斷點 E → `runtime-dispatch.md` § YOLO 與斷點；
SHA 比對 → `work-order-lifecycle.md` § 收單 SHA 回報的用途；`--worktree-status` → `bat-integration.md` § 查詢通道

## 排版規則

- ViewBox 寬度固定 680，高度依內容計算 + 40px padding
- 容器寬 600px，x=40，rx=16
- 節點寬 140-200px，高 44-56px，rx=8
- 虛線容器：`stroke-dasharray="4 3"` opacity 0.4-0.5；非工單通道、例外路徑、建議性連線也用虛線
- 標題文字 `class="th"` 14px，副標 `class="ts"` 12px，最多 5 字
- 行距 60px，列距 20px
- 所有文字標籤使用繁體中文（zh-TW）；狀態 enum、指令、檔名保留原文
- 所有 `sendPrompt()` 使用中文
