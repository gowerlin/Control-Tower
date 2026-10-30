---
title: 觀測與改進：status／insights／fieldguide
description: ct-status 從檔案讀狀態並抓出 drift；決策日誌是 append-only 的選項分析；ct-insights 用工單紀錄算健康度與原則衝突；FIELDGUIDE 與 DESIGN.md 把反覆出現的做法沉澱成規範；Debug 三層防線與品質閘門擋住重蹈覆轍。
---

# 觀測與改進：status／insights／fieldguide

<p class="ct-lead">一句話：既然所有事都寫在檔案裡，檔案本身就是儀表板；CT 提供一組只讀或「讀了再開工單」的工具，從工單、決策日誌與學習紀錄看出現在的狀態、過去的模式，以及值得沉澱成規範的做法。</p>

這一篇的工具有一個共同點：**看的人不動手改**。`ct-status` 預設不改任何檔案；`ct-insights` 只讀紀錄、產出報告；塔台的 `*fieldguide` 只做讀取和分析，需要改檔時一律開工單交給 Worker。觀測與改進是兩件事，分開才不會讓「看一眼」變成「順手改掉」。

## `ct-status` 與 drift 偵測 {#status}

`ct-status` 可以在任何 session 執行，從檔案回報工單狀態：

| 參數 | 行為 |
|---|---|
| `T####` 或路徑 | 顯示一張工單的狀態與主要元資料 |
| 空白或 `all` | 彙整熱區工單 |
| `sync` | 比對工單檔與 `sprint-status.yaml` |
| `active` | 強調還需要塔台或 Worker 處理的項目 |

讀取順序有兩條關鍵規則。第一，**frontmatter 優先**，只有沒有 frontmatter 的舊工單才退回讀正文的元資料表；兩者不一致時回報 `metadata_drift` 並以 frontmatter 為準，不默默修掉。第二，**未知的狀態就是 `UNKNOWN`**，絕不硬轉成 `PENDING`，否則一張狀態寫錯的工單會看起來像還沒開始。

狀態分成三桶：進行中（`PENDING`、`IN_PROGRESS`、`PAUSED`、`URGENT`）、需要塔台判斷（未解決的 `PARTIAL`、`BLOCKED`、`FAILED`、`INTERRUPTED`、`UNKNOWN`）、已結束（`DONE`、`CLOSED`、`WONTFIX` 等）。`INTERRUPTED` 是 session 中斷後塔台已另開接續工單或重派的原工單，塔台確認接續工單接手後就可以結掉；在那之前 `ct-status` 把它列在這一桶，工單有寫接續工單時一併列出編號。`PARTIAL` 只是某個時間點的未完成；卡點已被後續工單或範圍決策解除時，`ct-status` 會把它列為「可補正的已解決 PARTIAL」，建議塔台改成 `DONE`。

`ct-status` 是唯讀的，所以它跑[落點檢查](./landing-check)時從不停下來，而是把 C-0 到 C-3 的結果和狀態一起報告。在錯的 repo 讀到的狀態若看起來一切正常，比報錯更危險，所以結果要攤開來給你看。輸出保持精簡：編號、標題、狀態、時間、必要時的範圍或 commit、卡點或下一步，以及 drift 或同步不一致的警告；大型專案先給摘要，只列出進行中與不一致的項目。

## 決策日誌：append-only 的選項分析 {#decision-log}

`_decision-log.md` 記下每一個值得留下來的決策。格式固定：上方是倒序的索引表（`ID`、日期、決策、相關工單），下方是倒序的詳細紀錄，每條一個 `### D### 日期 — 標題` 區段，必填五個欄位：

- **背景**：當時的情境
- **選項**：至少兩個，以 `[A]`、`[B]` 標記並附簡短說明
- **決定**：選哪一個，以及理由
- **影響**：會動到哪些範圍
- **相關工單**

觸發方式有兩種：你主動說「記錄一個決策」或「我們決定了……」，或塔台在討論中認出重要的架構決策，主動問你要不要記。塔台會先以選項分析的格式整理出預覽，**你確認後才寫入**，同時更新索引與 `_tower-state.md` 的編號追蹤。決策日誌是 **append-only**：塔台不刪除也不修改已有的紀錄。塔台也不會主動建立這個檔，只在環境偵測時提示可以建立。

決策日誌也是其他機制的依據：yolo 下塔台代決 Worker 的提問要記進決策日誌，Workflow 授權要引用你同意的那條決策，`*sync` 會驗證索引與詳細紀錄的數量一致。

v5.13.0 起格式寫得更嚴，因為 BAT 指揮塔的決策頁也讀這個檔：索引表頭是 `ID`（舊寫法是 `#`）、每一列都以 `|` 開頭和結尾、格子裡不放 `|`、熱檔裡的每一筆決策都要有索引列、詳細紀錄的標題固定是 `### D### YYYY-MM-DD — 標題`。人看起來一樣的表格，解析器不一定一樣：少一個列尾的 `|`，BAT 就從那一列截斷，後面的決策全部看不到。`*sync` 的格式驗證會指出要改的地方，但不會自動改。

append-only 的檔總會越長越大。超過大小預算時塔台會提示**收斂**，何時做由你決定：較舊的詳細紀錄**原文**搬到 `_archive/decisions/` 的封存檔，熱檔保留涵蓋全部決策的索引表，標了 🔴 的危害規則整段留在熱檔。搬的是位置、不是內容，所以和 append-only 不衝突。

## BAT 塔台面板為什麼會空 {#bat-panel}

BAT 視窗裡的指揮塔面板（總覽、決策、臭蟲、待辦池、工單）直接讀 CT 寫的檔。v5.13.0 把 BAT 依賴的部分寫成一份讀取契約（v5.13.1 對照到 BAT `0.7.1-pre.9`），最常碰到的是檔案大小：

- **BAT 的讀檔上限是 524,288 bytes（512 KiB）**，超過就整檔不讀。各頁的表現看 BAT 版本：
  - BAT `0.7.1-pre.9`（預覽版）起，決策、臭蟲、待辦池、Epics、Sprint 頁讀不到時顯示「無法讀取」和檔名，太大時附上 KB 數；太大的工單仍列在清單裡，狀態是 UNKNOWN。
  - 更舊的 BAT 多數頁**不報錯**：決策頁顯示「沒有找到決策」，臭蟲與待辦池是空清單，太大的工單直接從清單消失。
  - 總覽在兩種版本都會說檔案太大；檔案不存在時各頁照舊是空的，不算錯誤。

  所以面板空了或說無法讀取，都先量檔案大小。
- **CT 的預算是 400 KB（409,600 bytes）**，比上限低一截，留空間給「已經提示、還沒收斂」的那幾個 session。BAT 會報錯之後預算仍然保留：塔台不知道你裝的是哪一版 BAT，舊版超過上限照樣靜默變空；而且「無法讀取」只讓問題看得見，那一頁照樣沒有內容。
- **量位元組，不數字元**：中文一個字佔 3 bytes。bash 用 `stat -c %s <檔>`，PowerShell 用 `(Get-Item <檔>).Length`。塔台啟動和 `*sync` 會量 `_tower-state.md`、`_decision-log.md`、`_bug-tracker.md`、`_backlog.md` 等熱檔（`*sync` 另量熱區單據），超過時印一行提示並指出收斂方式：決策日誌照上一節收斂，BUG 與待辦索引靠 `*archive` 歸檔後重建，單張工單把長篇證據移到另一個檔。提示不阻擋，塔台也不自動收斂。

大小之外，契約也列出各檔 BAT 依賴的格式。例如 BUG 索引的狀態只看那一列所在的區段標題；嚴重度格子要寫 `🔴 High`，只寫 emoji 時 BAT 顯示 Unknown，按等級篩選就會漏掉。BAT `0.7.1-pre.9` 起只寫 `critical` 也算 High，但更舊的 BAT 會顯示 Unknown，所以 critical 的 BUG 在索引裡照舊寫 `🔴 High（critical）`。CT 不為了面板去改單據本身的值，只照契約寫索引。

## `ct-insights`：從紀錄看健康度 {#insights}

`ct-insights` 分析 CT 的使用狀況，有三個作用域：

| 作用域 | 誰執行 | 看什麼 |
|---|---|---|
| `/ct-insights`（專案層） | 獨立 skill，任何 session | 本專案 `_ct-workorders/` 的工單、塔台狀態、決策日誌、學習紀錄、`sprint-status.yaml` |
| `/ct-insights global`（全局層） | 獨立 skill，任何 session | 全局層加上專案索引登記的每個專案，比較跨專案模式、全局學習品質、Playbook 使用率與成長曲線 |
| `*insights`（session 層） | 塔台內建指令 | 只看這一輪塔台 session：派了幾張、被糾正幾次、有沒有越權、context 還剩多少 |

專案與全局報告以數據面板開頭（分析期間、工單總數、完成率、平均耗時），接著是**工單健康度**五項指標：

| 指標 | 計算 | 健康基準 |
|---|---|---|
| 完成率 | DONE ÷ 總數 | ≥ 80% |
| 熔斷率 | BLOCKED ÷ 總數 | ≤ 20% |
| 估時偏差 | \|實際 − 預估\| ÷ 預估 | ≤ 50% |
| 首次完成率 | 從未 PARTIAL 或 FAILED 的 DONE ÷ 總數 | ≥ 60% |
| 回報品質 | 回報區有結構化內容的比例 | ≥ 80% |

再往下是「做得好的地方」「需要改善的地方」「原則衝突」「趨勢分析」「改善建議」與「學習記憶庫健康度」。好的模式例如排除法驅動的除錯、跨專案引用契約、結構化回報、遇到洋蔥問題時拆層；壞的模式例如同時追好幾條線、回報區只寫「完成」兩個字、單張工單拖超過一小時、審查發現問題卻沒有修正工單。原則衝突則對照 CT 的核心原則，例如塔台出現分析程式碼的痕跡、工單檔與 `sprint-status.yaml` 不一致、審查有 CRITICAL 卻沒有後續修正。

報告規則刻意保守：**先給發現並附上工單編號或檔案證據**、觀察到的事實和推論分開寫、不從不完整的紀錄過度推論。工單少於三張時，只給局部觀察，不談趨勢。v5.11.0 起還有 `*insights workflow [T#### …]`，用預篩腳本判斷哪些工單**不適合** Workflow，並給出附證據位置的提示；它不會自動標記或修改工單（見 [自我學習、Playbook 與 Workflow](./learning-playbook-workflow#three-way)）。

## FIELDGUIDE：把做法沉澱成規範 {#fieldguide}

FIELDGUIDE 是專案的 coding 教戰手冊，分三層：L1 設計哲學、L2 決策樹、L3 本專案的具體快照。塔台的 `*fieldguide` 指令只做讀取和分析，所有寫入都開工單交給 `/ct-fieldguide` 在 Worker session 執行：

| 指令 | 時機 | 塔台做什麼 |
|---|---|---|
| `scan [N]` | 事後 | 讀最近 N 張已完成工單的回報區，找出新的 coding 標準候選 |
| `add [topic]` | 日常 | 互動式整理一個主題，草擬三層內容 |
| `audit [module]` | 主動 | 比對 FIELDGUIDE 與實際程式碼，找出過時或不一致 |
| `init` | 新專案 | 偵測技術棧與既有慣例，產生初版 |
| `debt [topic]` | 技術債 | 找出同一議題的多種做法，建議統一方案 |
| `design` | 視覺規範 | 檢查 DESIGN.md 狀態，必要時產生擷取工單 |

`scan` 有兩種提取方式：有 `[FG]`、`[FG-DEBT]`、`[FG-PROMOTE]` 標記的內容直接提取；沒有標記時，從「遭遇問題」和「互動紀錄」裡的技術決策推斷，這類候選會標「（語義推斷）」提醒你多確認。`*evolve` 也會把學習紀錄裡的 `[FG-CANDIDATE]` 橋接過來。`audit` 和 `debt` 的差別在於比對對象：`audit` 看 FIELDGUIDE 和程式碼一不一致，`debt` 看程式碼內部同一件事有沒有好幾種做法。

專案規則要晉升為全局規範，必須在多個專案重複出現（或你明確要求）、觸發條件和做法夠通用、專案專屬的名稱已經拿掉，並且檢查過和既有全局規範有沒有衝突。

## DESIGN.md：視覺規範擷取 {#design}

視覺規範不寫進 FIELDGUIDE，而是另外放在 DESIGN.md，兩者互相連結、不重複。`/ct-fieldguide design` 從程式碼或網址擷取：design token 與 CSS 變數、字體與間距尺度、顏色用法與寫死的顏色、元件狀態與版面規則、斷點、無障礙限制，以及框架的 UI 慣例。原則是**不從零星的數值推斷出一套品牌系統**，要有證據。`*fieldguide design check` 可以快速比對 DESIGN.md 和程式碼是否一致。

## Debug 三層防線與品質閘門 {#debug}

Worker 遇到問題時，塔台依序建議三層：

1. **TDD／ATDD（預防）**：問題出在缺少測試，就先寫測試定義預期行為，讓開發目標變成「紅轉綠」。
2. **診斷腳本（自動化偵測）**：錯誤難重現或 log 量大時，派一張診斷工單讓 Worker 寫 log parser、狀態檢查這類腳本，由你執行後把結果寫回工單，目標是把一萬行 log 濃縮成二十行結論。
3. **結構化 log 分析（最後手段）**：提供 grep、jq、awk 指令讓你先過濾，過濾後不超過五十行。**絕對不把原始 log 直接貼進任何 AI session**。

品質閘門有兩條。一是「審查 → 修正 → 交付」：審查工單回報有 CRITICAL 或 HIGH 發現時，**強制**先派修正工單，不可直接進下一階段；原始 CRITICAL 很多時，修正後再派覆核。二是交叉驗證：產出文件的 session 和審查它的 session 必須分開，避免確認偏誤。這兩條也是 `ct-insights` 檢查原則衝突時會看的地方。

::: tip 命令範例
本頁的指令與指標都是摘要，完整參數以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `ct-status/SKILL.md`（§ Modes、§ Read Order、§ Landing Zone Check、§ Status Buckets、§ Output）
- `control-tower/references/decision-log-system.md` § 格式規格、§ 塔台操作流程、§ 與 `*sync` 的關係、§ 收斂
- `control-tower/references/memory-protocol.md` § BAT 塔台面板讀取契約（§ 大小預算、§ 各檔要求、§ 值域對照（嚴重度／優先級））
- `ct-insights/SKILL.md`（§ Scope、§ Analysis Flow、§ Report Rules）、`ct-insights/references/report-template.md` § 工單健康度（5 項指標）、§ 完整報告結構（Project / Global）
- `spec/CT設計規格-ct-insights使用模式分析.md` § 三、分析維度、§ 四、三個作用域的詳細行為
- `control-tower/references/fieldguide-commands.md`（§ 命令總覽）、`ct-fieldguide/SKILL.md`
- `control-tower/references/debug-strategies.md` § Debug 三層防線、§ 品質閘門

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
