# `*fieldguide` 子命令完整行為規格

> 塔台內建命令，不離開塔台角色。
> 所有命令執行後繼續塔台流程。
> 所有需要修改檔案的操作都透過工單交給 `/ct-fieldguide` sub-session。

---

## `*fieldguide scan [N]` — 事後萃取

**用途**：從工單回報區自動提取新發現的 coding 標準，評估是否需要更新 FIELDGUIDE。

**語法**：`*fieldguide scan [N]`（N：掃描最近 N 張已完成工單，預設 5）

**行為**：
1. Glob 列出 `_ct-workorders/T*.md`，篩選狀態為 DONE 的工單
2. 讀取最近 N 張工單的回報區，重點搜尋：
   - 「發現與建議」區段（`[FG]`、`[FG-DEBT]`、`[FG-PROMOTE]` 標記）
   - 「遭遇問題」區段中暗示 coding 標準的描述
   - 「互動紀錄」中使用者確認的技術決策
   - `_learnings.md` 中的 `[FG-CANDIDATE]` 標記（由 `*evolve` 橋接）
   **雙模式提取**：
   - **標記模式**（精確）：有 `[FG]` / `[FG-DEBT]` / `[FG-PROMOTE]` 標記的內容直接提取
   - **語義模式**（補充）：無標記時，分析「遭遇問題」和「互動紀錄」中的技術決策描述，識別暗含的 coding 標準（如「發現 XX 必須 YY」「改用 ZZ 方式」等模式）
   語義模式產生的候選項目在呈現時標注 `（語義推斷）`，提示使用者需額外確認。
3. 提取候選項目，每項標注：
   - 來源工單編號
   - 對應的 FIELDGUIDE 層級（L1 設計哲學 / L2 決策樹 / L3 專案快照）
   - 對應的 FIELDGUIDE 章節（若能匹配現有章節）
   - 是否為新章節（無法匹配現有章節時）
4. 以互動式列表呈現候選項目：
   ```
   📋 *fieldguide scan 結果（最近 N 張工單）

   找到 N 個候選更新項目：

   [1] T0208 → 搜尋陷阱：ElSelect remote 搜尋需 filterable + remote 雙開
       層級：L2 決策樹 + L3 快照
       章節：元件使用規範 → 搜尋元件選擇（新增子節點）

   [2] T0210 → PIM 不移植聲明
       層級：L1 設計哲學 + L3 快照
       章節：跨層聲明與技術債（新章節）

   要處理哪些？
   [A] 全部 → 產生一張 /ct-fieldguide update 工單
   [B] 選擇 → 輸入編號（如 1,3）
   [C] 稍後 → 記錄到待辦，下次 scan 時提醒
   ```
5. 使用者確認後：
   - 產生工單，任務指令包含確認的候選項目清單
   - 工單的「輸入上下文」包含提取出的具體內容和來源工單引用

**產出**：工單檔案（交由 `/ct-fieldguide update` 在 sub-session 執行）

**不產出工單的情況**：掃描結果為空 → 顯示「近期工單無新的 coding 標準發現」

---

## `*fieldguide add [topic]` — 日常維護

**用途**：互動式新增一條決策樹（或更新現有決策樹），由使用者口述、塔台結構化。

**語法**：`*fieldguide add [topic]`（topic 可選，指定主題）

**行為**：
1. 若有 `topic` → 讀取現有 FIELDGUIDE.md，找到對應章節
2. 若無 `topic` → 詢問使用者要新增/更新的主題
3. 進入互動式提問（遵循需求對齊協議的選項式提問）：
   ```
   🌳 *fieldguide add — 新增決策樹

   主題：<topic>

   Q1: 這個情境通常在什麼時候遇到？
   [A] 建立新頁面/元件時
   [B] 修改既有功能時
   [C] 處理錯誤/例外時
   [D] 其他：________

   Q2: 你目前的判斷依據是什麼？
   （請描述你的 if-then 邏輯）

   Q3: 本專案有沒有參考範例？
   [A] 有，路徑是：________
   [B] 沒有，這是第一次遇到
   [C] 有多種做法（技術債）
   ```
4. 根據回答，塔台草擬三層結構：
   - L1：從使用者描述的「為什麼」抽象出設計哲學
   - L2：從使用者描述的 if-then 邏輯整理為決策樹
   - L3：使用者提供的具體檔案路徑和做法
5. 呈現草擬結果，使用者確認/修改
6. 確認後產生工單，交由 `/ct-fieldguide update` 寫入 FIELDGUIDE.md

**特殊情境**：
- 使用者說「有多種做法」→ 自動觸發 `*fieldguide debt` 的分析邏輯
- 使用者提供的內容僅涉及 L3（具體做法）→ 塔台嘗試匹配現有 L2 決策樹，若匹配成功則工單僅更新 L3

**產出**：工單檔案（含草擬的三層結構內容）

---

## `*fieldguide audit [module]` — 主動盤點

**用途**：對指定模組做 coding 標準掃描，找出 FIELDGUIDE 與實際程式碼的不一致。

**語法**：`*fieldguide audit [module]`（module 可選，指定模組路徑或名稱）

**行為**：
1. 若有 `module` → 確認路徑存在
2. 若無 `module` → 列出專案主要模組供選擇
3. 檢查現有 FIELDGUIDE.md：
   - 存在 → 比對模式（audit against existing）
   - 不存在 → 建議改用 `*fieldguide init`
4. 產生盤點工單，任務指令包含：
   - 盤點範圍（指定模組）
   - 盤點焦點：比對 FIELDGUIDE L3 快照 vs 實際程式碼
   - 預期發現：過時的路徑、新增的慣例、不一致的做法
5. 工單交由 `/ct-fieldguide audit` 在 sub-session 執行

**與 `*fieldguide scan` 的區別**：
- `scan`：被動，從已完成工單的回報中提取
- `audit`：主動，掃描程式碼比對 FIELDGUIDE

**產出**：盤點工單檔案

---

## `*fieldguide init` — 從零建立

**用途**：新專案啟動時，產生初版 FIELDGUIDE.md。

**語法**：`*fieldguide init`

**行為**：
1. 檢查現有 FIELDGUIDE.md：
   - 存在 → 提示「已有 FIELDGUIDE，要重建嗎？」（高風險操作，預設不重建）
   - 不存在 → 繼續
2. 檢查 Global 層種子（`~/.claude/control-tower-data/fieldguide/`）：
   - 存在 → 讀取種子清單
   - 不存在 → 從空白開始
3. 互動式確認：
   ```
   🌱 *fieldguide init — 產生初版 FIELDGUIDE

   偵測到 Global 種子：
   ✅ 通用設計哲學（N 條 L1 原則）
   ✅ 通用決策樹框架（N 個 L2 模板）
   （或 ❌ 無 Global 種子，將從空白開始）

   專案技術棧：
   [A] Vue 3 + Element Plus（自動匹配前端模板）
   [B] React + Ant Design
   [C] .NET + Razor Pages
   [D] 其他：________

   FIELDGUIDE 放置路徑：
   [A] 專案根目錄 FIELDGUIDE.md（推薦）
   [B] src/<subproject>/FIELDGUIDE.md（mono-repo）
   [C] 自訂：________
   ```
4. 產生工單，任務指令包含：
   - Global 種子內容（L1 + L2 框架）
   - 需掃描的核心目錄（根據技術棧推測）
   - 代表頁面選擇指引
5. 工單交由 `/ct-fieldguide init` 在 sub-session 執行

**產出**：工單檔案

---

## `*fieldguide debt [topic]` — 技術債盤點

**用途**：盤點同一議題存在多種作法的情況，產生技術債清單。

**語法**：`*fieldguide debt [topic]`（topic 可選，指定盤點主題）

**行為**：
1. 若有 `topic` → 針對該主題分析
2. 若無 `topic` → 從現有 FIELDGUIDE 的 L3 快照中識別潛在衝突點：
   - 同一決策樹節點有多個不同做法
   - L3 快照標記「無統一慣例，建議建立」的項目
3. 互動式確認要深入盤點的主題
4. 產生盤點工單，任務指令聚焦於：
   - 列出同一議題的所有不同實作方式
   - 標注每種方式的使用頻率和優缺點
   - 建議統一方案
5. 工單交由 `/ct-fieldguide audit`（以 debt 模式）在 sub-session 執行

**與 `audit` 的區別**：
- `audit`：FIELDGUIDE vs 程式碼的一致性
- `debt`：程式碼內部的一致性（同議題多種做法）

**產出**：盤點工單檔案 + 技術債清單（嵌入工單）

---

## `*fieldguide design` — 視覺規範管理

**用途**：在塔台 session 內分析專案的視覺規範狀態，並產生 `/ct-fieldguide design` 工單。

**語法**：`*fieldguide design [subcommand]`

**子命令**：

| 子命令 | 用途 |
|--------|------|
| （無） | 檢查 DESIGN.md 狀態，建議下一步 |
| `generate` | 產生 `/ct-fieldguide design` 工單，從專案程式碼擷取 |
| `check` | 快速比對 DESIGN.md 與程式碼的一致性 |

### `*fieldguide design`（無子命令）

**行為**：
1. 檢查專案根目錄是否存在 `DESIGN.md`
2. 若存在：
   - 讀取 metadata（擷取日期、來源類型、信心度）
   - 與 FIELDGUIDE.md 的橋接章節比對
   - 報告狀態：
   ```
   📊 DESIGN.md 狀態

     路徑：./DESIGN.md
     擷取日期：<日期>
     來源類型：<Tailwind v4 / Element Plus / ...>
     信心度：<N%>
     FIELDGUIDE 橋接：✅ 已橋接 / ❌ 缺少橋接章節
     最後更新距今：<N> 天

     💡 建議：
     - [建議，如「距上次擷取已超過 30 天，建議重新擷取」]
   ```
3. 若不存在：
   ```
   📊 DESIGN.md 狀態

     ❌ 未偵測到 DESIGN.md
     前端程式碼：✅ 偵測到（<技術棧>）

     建議：
     [A] 產生 /ct-fieldguide design 工單 → 從程式碼擷取
     [B] 稍後再說
   ```

### `*fieldguide design generate`

**行為**：
1. 分析專案前端技術棧（快速偵測，不做完整擷取）
2. 產生 `/ct-fieldguide design` 工單，任務指令引用 `design-extraction.md` 流程
3. 工單包含：
   - 偵測到的技術棧摘要
   - 建議的擷取模式（標準 / 差異化）
   - 預估的擷取品質（基於技術棧）

**產出**：工單檔案

### `*fieldguide design check`

**行為**：
1. 讀取現有 DESIGN.md
2. 快速掃描程式碼中的色碼和變數使用
3. 比對是否有未記錄的新色碼或 token
4. 報告差異（不修改任何檔案）：
   ```
   🔍 DESIGN.md 一致性快速檢查

     新增色碼（未記錄）：N 個
     移除色碼（不再使用）：N 個
     新增 CSS 變數：N 個

     建議：
     [A] 產生 /ct-fieldguide design 工單（重新擷取）
     [B] 差異可接受，不處理
   ```

**注意**：check 只做快速比對，不做完整稽核。完整稽核是 `/ct-fieldguide audit` 擴充的範圍（F5，P1 階段）。

---

## 命令總覽

| 命令 | 觸發 | 塔台做什麼 | 產出 |
|------|------|-----------|------|
| `scan [N]` | 事後 | 讀工單回報區，提取候選 | 更新工單 → `/ct-fieldguide update` |
| `add [topic]` | 日常 | 互動式結構化，草擬三層 | 更新工單 → `/ct-fieldguide update` |
| `audit [module]` | 主動 | 確認範圍，產生盤點工單 | 盤點工單 → `/ct-fieldguide audit` |
| `init` | 新專案 | 偵測種子+技術棧，產生工單 | 初始化工單 → `/ct-fieldguide init` |
| `debt [topic]` | 技術債 | 識別衝突點，產生盤點工單 | 盤點工單 → `/ct-fieldguide audit --debt` |
| `design` | 視覺規範 | 檢查 DESIGN.md 狀態 | 狀態報告 / 工單 → `/ct-fieldguide design` |
| `design generate` | 視覺規範 | 產生擷取工單 | 擷取工單 → `/ct-fieldguide design` |
| `design check` | 一致性 | 快速比對 DESIGN.md vs 程式碼 | 差異報告 |

**共通規則**：
- 塔台只做**讀取和分析**，不直接寫入 FIELDGUIDE.md
- 所有需要修改檔案的操作都**透過工單**交給 sub-session
- 工單產生後按正常塔台流程派發（auto-session 或剪貼簿）
