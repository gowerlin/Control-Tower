# FIELDGUIDE 三層結構格式規範

> 本文件定義 FIELDGUIDE.md 的完整格式，供 `/ct-fieldguide` 所有子命令參考。
> 所有寫入 FIELDGUIDE.md 的操作必須遵循本規範。

## 核心概念

FIELDGUIDE（教戰手冊）是專案級的 coding 標準文件，採用三層結構：

| 層級 | 名稱 | 性質 | 說明 |
|------|------|------|------|
| L1 | 設計哲學 | 抽象原則 | 不隨具體技術改變的通用原則（「為什麼」） |
| L2 | 決策樹 | 情境分支 | 遇到特定情境時的 if-then 判斷邏輯（「怎麼選」） |
| L3 | 專案快照 | 具體答案 | 本專案的實際做法、路徑、元件名稱（「具體怎麼做」） |

**三層關係**：L1 抽象出 L2 的「為什麼」，L2 的每個分支由 L3 提供具體答案。

---

## FIELDGUIDE.md 整體結構

```markdown
# FIELDGUIDE — <專案名稱> 教戰手冊

> 最後更新：<日期>
> 技術棧：<主要技術棧摘要>
> 章節數：<N>

## 目錄

- [1. <章節名稱>](#1-章節名稱)
- [2. <章節名稱>](#2-章節名稱)
- ...

---

## 1. <章節名稱>

### L1 設計哲學

<本章節的抽象原則>

### L2 決策樹

<情境分支邏輯>

### L3 專案快照

<具體做法和路徑>

---

## 2. <章節名稱>

（同上結構）
```

---

## L1 設計哲學撰寫指引

**定位**：跨專案可能複用的通用原則，不含專案特定名稱。

**格式**：

```markdown
### L1 設計哲學

容器越重，切換成本越高——能用輕量容器完成的事，不要用重量容器。
```

**撰寫規則**：
1. **一句話概括**：用一句話表達核心原則，不超過兩句
2. **不含專案特定名稱**：不出現 `BaseDrawer`、`ElSelect` 等具體元件名
3. **可驗證**：原則必須能在程式碼中找到對應的實踐
4. **從 L2 反推**：先有決策樹，再從中抽象出原則

**常見 L1 類型**：
- 容器/佈局選擇原則
- 錯誤處理哲學
- 一致性 vs 最佳實踐的權衡
- 資料流設計原則
- UI 互動設計原則

**反面範例**（不要這樣寫）：
```markdown
❌ 使用 Element Plus 的 ElDialog 而不是 ElDrawer
    （這是 L3，不是 L1）

❌ 元件設計是軟體工程的重要議題
    （太空泛，無法指導決策）
```

---

## L2 決策樹撰寫指引

**定位**：遇到特定情境時的判斷邏輯，用樹狀分支表達。

**格式**：

```markdown
### L2 決策樹

需要彈出容器？
├─ 內容是完整場景（獨立流程） → 獨立路由頁面
├─ 需要集中注意力的獨立任務 → Dialog 系
│   ├─ 簡單確認/提示 → MessageBox
│   └─ 複雜表單/多步驟 → Dialog
├─ CRUD 表單、需對照列表內容 → Drawer 系
│   ├─ 標準新增/編輯 → 封裝 Drawer 元件
│   └─ 需要大面積操作 → 全寬 Drawer
└─ 不確定 → 看該模組最相似的頁面用了什麼
```

**撰寫規則**：
1. **以問題開頭**：「需要 X？」或「遇到 Y 情境？」
2. **樹狀分支**：使用 `├─`、`└─` 表達分支（Unicode box drawing）
3. **每個分支有結論**：`→` 後接具體選擇
4. **兜底分支**：最後一條 `└─` 提供不確定時的預設建議
5. **可嵌套**：複雜決策可多層嵌套
6. **可含專案特定名稱**：L2 可出現元件名稱，但決策結構本身應可複用

**分支符號規範**：
- `├─`：中間分支
- `└─`：最後分支
- `│`：垂直連接線
- `→`：分支結論
- 嵌套時縮進 4 格或使用 `│   ├─` 格式

**反面範例**：
```markdown
❌ 用 Dialog。
    （無決策邏輯，直接跳到結論）

❌ Dialog 比 Drawer 好用。
    （主觀判斷，不是情境分支）
```

---

## L3 專案快照撰寫指引

**定位**：本專案的具體實作細節，包含路徑、元件名稱、設定值。

**格式**：

```markdown
### L3 專案快照

**封裝元件**：`src/components/BaseDrawer.vue`
- Props：`visible`（Boolean）、`title`（String）、`width`（String, 預設 '600px'）
- 使用方式：`<BaseDrawer :visible.sync="drawerVisible" title="新增">`

**參考頁面**：
- 標準用法：`src/views/member/MemberList.vue:45`（Drawer 新增會員）
- 進階用法：`src/views/order/OrderDetail.vue:120`（Dialog 確認訂單）

**注意事項**：
- ElDrawer 的 `destroy-on-close` 必須設為 true（避免表單狀態殘留）
- Dialog 的 `close-on-click-modal` 設為 false（防止誤關）
```

**撰寫規則**：
1. **路徑必須真實**：所有檔案路徑必須經過 `Glob` 或 `ls` 驗證
2. **含行號**：重要的參考位置附上行號（`file.vue:45`）
3. **含設定值**：關鍵的 props、config、flag 要列出具體值
4. **含注意事項**：容易踩坑的地方明確標注
5. **永不晉升**：L3 是專案特定的，不會被晉升到 Global 層

**L3 可包含的內容類型**：
- 封裝元件的路徑和使用方式
- 參考頁面的路徑和行號
- 設定值和環境變數
- 命名慣例和程式碼風格
- 已知的坑和 workaround

---

## 章節組織原則

**按主題分章**，而非按技術分層。每章包含完整的 L1+L2+L3。

### 章節類型

| 類型 | 用途 | 範例章節名稱 |
|------|------|-------------|
| coding | 程式碼標準 | 錯誤處理、元件使用規範、API 呼叫模式 |
| visual | 視覺規範橋接 | 視覺規範（DESIGN.md 橋接） |

> `visual` 類型章節不重複 DESIGN.md 內容，而是提供 FIELDGUIDE → DESIGN.md 的交叉引用。

**常見章節**：
1. 彈出容器選擇（Dialog / Drawer / 路由頁面）
2. 表格元件設計
3. 表單驗證
4. 錯誤處理與訊息通知
5. API 設計與呼叫慣例
6. 搜尋元件選擇
7. 權限控制
8. 國際化（i18n）
9. 跨層聲明與技術債

**章節新增規則**：
- 新發現的慣例先嘗試歸入現有章節
- 無法歸入時才新增章節
- 新章節至少要有 L2（決策樹），L1 可暫缺（標記「待抽象」）
- L3 可漸進式補充

---

## 目錄維護

目錄必須與章節同步。每次新增/刪除章節後更新目錄。

```markdown
## 目錄

- [1. 彈出容器選擇](#1-彈出容器選擇)
- [2. 表格元件設計](#2-表格元件設計)
- [3. 錯誤處理與訊息通知](#3-錯誤處理與訊息通知)
```

---

## 更新標記

更新 FIELDGUIDE.md 時，在被修改的章節末尾加入更新標記：

```markdown
> 📝 更新於 <日期>，來源：T<工單編號>
```

頭部的「最後更新」日期同步更新。

---

## 技術債章節格式

當同一議題存在多種做法（由 `*fieldguide debt` 識別），使用特殊格式：

```markdown
## N. 表單驗證（⚠️ 技術債）

### L1 設計哲學

表單驗證邏輯應集中管理，而非散落在各元件中。

### L2 決策樹

需要表單驗證？
├─ 簡單必填 → inline validator
├─ 複雜業務邏輯 → rules 物件
└─ ⚠️ 目前兩種做法並存，尚未統一

### L3 專案快照

**做法 A：inline validator**（使用頻率：60%）
- 範例：`src/views/member/MemberForm.vue:30`
- 特徵：驗證邏輯寫在 template 的 `:rules` 屬性中

**做法 B：rules 物件**（使用頻率：40%）
- 範例：`src/views/order/OrderForm.vue:15`
- 特徵：獨立 `rules` 物件在 `<script>` 中定義

**建議統一方案**：rules 物件（理由：可複用、好測試、集中管理）

> 📝 技術債識別於 <日期>，來源：T<工單編號>
```

---

## `[FG]` 標記系統

工單回報區使用的標記格式，供 `*fieldguide scan` 自動提取 coding 標準發現。

### 標記類型

| 標記 | 含義 | scan 處理方式 | 使用場景 |
|------|------|-------------|---------|
| `[FG]` | coding 標準發現 | 自動提取為 FIELDGUIDE 更新候選 | 發現新慣例、最佳實踐、必須遵守的規則 |
| `[FG-DEBT]` | 技術債發現 | 自動提取為 `*fieldguide debt` 候選 | 同一議題存在多種做法，尚未統一 |
| `[FG-PROMOTE]` | 建議晉升 Global 層 | 自動提取為晉升候選 | L1/L2 具通用性，可跨專案複用 |

### 標記格式

在工單回報區的「發現與建議」區段使用：

```markdown
### 發現與建議
[FG] 搜尋元件：ElSelect 的 remote 搜尋必須同時設定 filterable 和 remote 屬性
[FG] 錯誤處理：console.log 同步寫入造成 UI 卡頓，建議改用 async logging
[FG-DEBT] 表單驗證：A 模組用 inline validator，B 模組用 rules 物件，兩種做法並存
[FG-PROMOTE] 章節「彈出容器選擇」的 L1 具通用性，建議晉升 Global 層
```

### 標記撰寫規則

1. **每行一個標記**：一條 `[FG]` 對應一項發現
2. **冒號分隔主題**：`[FG] <主題>：<描述>` 格式
3. **描述需具體**：避免模糊描述（❌「UI 有問題」→ ✅「ElSelect remote 搜尋需 filterable + remote 雙開」）
4. **可選層級提示**：在描述末尾標注建議層級，如 `（建議 L2 + L3）`

### 向後相容

- `[FG]` 標記是**可選的**，不使用標記的工單仍可被 `*fieldguide scan` 處理（透過語義分析）
- 標記只是提高自動提取的精確度和效率
- 現有工單模板不需修改（標記由 sub-session 在回報區自行添加）

### 與 ct-exec 收尾流程的關係

`/ct-exec` 在收尾時可提示 sub-session：
```
💡 若執行過程中發現 coding 標準或技術債，在回報區用 [FG] 或 [FG-DEBT] 標記。
```

### 與 `*evolve` 的橋接

`*evolve` 萃取的學習項目若屬於 coding 標準，會在 `_learnings.md` 中標記 `[FG-CANDIDATE]`。
`*fieldguide scan` 掃描時也會讀取 `_learnings.md` 的 `[FG-CANDIDATE]` 標記。

---

## 視覺規範章節模板

當 FIELDGUIDE 需橋接 DESIGN.md 時，使用以下模板新增 `visual` 類型章節：

```markdown
## N. 視覺規範（DESIGN.md 橋接）

> 本章節連結 FIELDGUIDE 與 DESIGN.md，確保 coding 標準和視覺規範的一致性。
> 完整視覺規範見：[DESIGN.md](./DESIGN.md)

### L1 設計哲學

- 所有視覺決策以 DESIGN.md 為唯一真相來源
- 色彩、字體、間距使用語意 token，不使用 hardcoded 值
- 元件樣式遵循 DESIGN.md 定義的變體（variants），不自創

### L2 決策樹

需要使用色彩時？
├─ 有語意角色（primary/success/error 等）→ 使用 DESIGN.md Color Roles
├─ 是背景/前景 → 使用 DESIGN.md 的 background/foreground token
├─ 需要新色彩 → 先更新 DESIGN.md，再使用新 token
└─ 臨時/一次性 → 禁止，必須經過 DESIGN.md 流程

需要調整間距/圓角時？
├─ 有對應 token → 使用 DESIGN.md Spacing/Radius token
└─ 無對應 token → 先更新 DESIGN.md

需要新元件變體時？
├─ DESIGN.md 已定義 → 直接使用
└─ 未定義 → 提出 DESIGN.md 更新需求

### L3 專案快照

- **DESIGN.md 路徑**：`./DESIGN.md`
- **擷取日期**：<日期>
- **設計系統來源**：<Tailwind v4 / Element Plus / SCSS / ...>
- **色彩角色數量**：<N>
- **暗黑模式**：<已支援 / 未支援>
```

**使用時機**：
- `/ct-fieldguide init` 偵測到 DESIGN.md 時自動新增
- `/ct-fieldguide design` 完成後由 init 或 update 橋接
- L3 專案快照的欄位值從 DESIGN.md metadata 自動填入
