# Global FIELDGUIDE 層格式定義

> 本文件定義 Global 層 FIELDGUIDE 資料的格式和管理規則。
> 路徑：`~/.claude/control-tower-data/fieldguide/`
> 供 `/ct-fieldguide init` 和 `/ct-fieldguide update` 參考。

## 目錄結構

```
~/.claude/control-tower-data/fieldguide/
├ seed-l1.md              ← 通用 L1 設計哲學（跨專案不變）
├ seed-l2-templates.md    ← 通用 L2 決策樹框架（可複用結構）
├ promoted/               ← 從專案晉升的完整決策樹
│  ├ error-handling.md    ← 含 L1 + L2（L3 省略，因專案特定）
│  └ api-design.md
└ registry.md             ← 跨專案 FIELDGUIDE 索引
```

---

## seed-l1.md — 通用設計哲學種子

**用途**：跨專案不變的 L1 原則。新專案 `init` 時自動注入。

**格式**：

```markdown
# 通用設計哲學種子

> 新專案 init 時自動注入。專案可覆蓋。

## GL1-001: <主題>
<一句話原則>

## GL1-002: <主題>
<一句話原則>
```

**ID 規則**：`GL1-NNN`（Global L1，三位數序號）

**範例**：

```markdown
## GL1-001: 彈出容器選擇
容器越重，切換成本越高——能用輕量容器完成的事，不要用重量容器。

## GL1-002: 錯誤處理
ERROR 類訊息讓使用者自己關閉；INFO 類可以自動消失。失敗路徑的可見度必須 >= 成功路徑。

## GL1-003: 表格設計
將「宣告欄位」和「資料取得」分離——開發者只需描述每欄的性質，框架負責串接。

## GL1-004: 一致性優先
先看專案中有沒有人做過類似的 UI/API，有就照著做。一致性 > 理論最佳。

<!-- GL1-005 ~ GL1-009 保留空號，供未來 coding 類原則晉升使用 -->

## GL1-010: 視覺規範單一來源
視覺一致性由單一權威來源（DESIGN.md）驅動，程式碼中不出現 hardcoded 色碼。

## GL1-011: 設計-程式碼職責分離
設計決策（色彩、字體、間距）在 DESIGN.md 維護；
Coding 決策（元件選擇、資料流）在 FIELDGUIDE 維護。兩者不重複。
```

**編號規則**：
- `GL1-001 ~ GL1-009`：coding 類通用原則（彈出容器、錯誤處理、表格、一致性等）
- `GL1-010 ~ GL1-019`：視覺規範類通用原則（單一來源、職責分離等）
- 各類別之間保留空號，避免未來新增時需要重新編號

**寫入規則**：
- 不含專案特定名稱（如元件名、路徑）
- 新增條目追加到末尾
- 已存在的條目不重複新增（以主題去重）

---

## seed-l2-templates.md — 通用決策樹框架

**用途**：可複用的 L2 決策樹骨架（不含專案特定的具體答案）。新專案 `init` 時作為 L2 起點。

**格式**：

```markdown
# 通用決策樹框架

> 新專案 init 時作為 L2 起點，sub-session 根據實際程式碼填充細節。

## GT2-001: <主題>
<決策樹骨架，使用通用術語>

## GT2-002: <主題>
<決策樹骨架>
```

**ID 規則**：`GT2-NNN`（Global Template L2，三位數序號）

**範例**：

```markdown
## GT2-001: 彈出容器選擇
需要彈出容器？
├─ 內容是完整場景 → 獨立路由頁面
├─ 需要集中注意力的獨立任務 → Dialog 系
├─ CRUD 表單、需對照列表內容 → Drawer 系
└─ 不確定 → 看該模組最相似的頁面用了什麼

## GT2-002: 表格元件選擇
需要表格？
├─ 標準 CRUD 列表（分頁 + 搜尋 + 排序）→ 專案封裝表格元件
├─ 簡單靜態表格（無分頁、資料量少）→ 原生表格元件
├─ 時間序列資料 → Timeline 元件
└─ 不確定 → 用封裝表格元件，它能處理大部分場景
```

**寫入規則**：
- 使用通用術語（如「Dialog 系」而非 `ElDialog`）
- 決策結構完整但不含專案特定細節
- 子分支可省略（由專案 init 時根據程式碼填充）

---

## promoted/ — 晉升的完整決策樹

**用途**：從專案 FIELDGUIDE 晉升的完整 L1+L2 內容（省略 L3）。

**路徑**：`~/.claude/control-tower-data/fieldguide/promoted/<topic>.md`

**格式**：

```markdown
# <主題> — 晉升決策樹

> 晉升自：<專案名稱>
> 晉升日期：<日期>
> 適用技術棧：<技術棧標籤>

## L1 設計哲學

<抽象原則>

## L2 決策樹

<完整決策樹，使用通用術語>

## 晉升來源

- 首次來源：<專案名稱>（<日期>）
- 驗證專案：<專案名稱>（<日期>）
```

**寫入規則**：
- L3 永不晉升（本質是專案特定的）
- 晉升時去除具體元件名稱和路徑（如 `BaseDrawer` → `Drawer 系元件`）
- 記錄來源專案和驗證專案

---

## registry.md — 跨專案 FIELDGUIDE 索引

**用途**：記錄所有專案的 FIELDGUIDE 位置和基本資訊。

**格式**：

```markdown
# FIELDGUIDE 跨專案索引

| 專案 | 路徑 | 章節數 | DESIGN.md | 最後更新 | 技術棧 |
|------|------|-------|-----------|---------|--------|
| <專案名> | <絕對路徑> | <N> | <✅/❌> | <日期> | <技術棧> |
```

**範例**：

```markdown
| CrmApp | ~/repos/project-b/src/crm/FIELDGUIDE.md | 12 | ✅ | 2026-04-06 | Vue 3 + Element Plus |
| AlertSystem | ~/repos/project-c/FIELDGUIDE.md | 8 | ❌ | 2026-03-15 | .NET 8 + Razor |
```

**DESIGN.md 欄位說明**：
- `✅`：該專案已產生 DESIGN.md（視覺規範權威來源）
- `❌`：該專案尚未產生 DESIGN.md
- 值由 `/ct-fieldguide init` 或 `/ct-fieldguide design` 根據偵測結果自動填入

**更新時機**：
- `/ct-fieldguide init` 完成後，新增一行（DESIGN.md 欄位根據偵測結果填入）
- `/ct-fieldguide update` 完成後，更新章節數和最後更新日期
- `/ct-fieldguide design` 完成後，更新 DESIGN.md 欄位（❌ → ✅）

---

## 晉升規則（Project → Global）

### 觸發時機

1. `/ct-fieldguide update` 完成後，自動評估是否有內容可晉升
2. `/ct-evolve` 執行時，同步掃描 FIELDGUIDE 的跨專案複用候選
3. 專案結案時，強制評估所有 L1 和 L2 的晉升候選

### 晉升條件

| 層級 | 條件 | 目標 |
|------|------|------|
| L1 | 在 >= 2 個專案中出現相同或相似原則 | `seed-l1.md` |
| L2 | 在 >= 2 個專案中出現相同結構的決策樹 | `seed-l2-templates.md`（骨架）或 `promoted/`（完整） |
| L3 | **永不晉升** | — |

### 視覺規範的晉升規則（PROPOSAL F9）

視覺規範章節的 L1 和 L2 遵循通用晉升條件，但有以下特殊規則：

| 類型 | 晉升規則 | 原因 |
|------|---------|------|
| 視覺規範 L1（原則） | 可晉升到 `seed-l1.md` | 如 GL1-010/011，跨專案通用 |
| 視覺規範 L2（決策樹） | 可晉升到 `seed-l2-templates.md` | 如「色彩選擇決策樹」骨架 |
| **DESIGN.md 本身** | **不晉升** | 專案特定的視覺定義，不通用 |
| DESIGN.md 擷取腳本 | 可晉升為 Global 工具 | 提取邏輯跨專案可複用 |

**DESIGN.md 不晉升的原因**：
- 每個專案的色彩、字體、間距是設計選擇，沒有通用基準
- 不同專案的品牌風格差異大，強制統一會破壞個性
- DESIGN.md 的價值在於「該專案的權威視覺來源」，跨專案複製會失去權威性

**但擷取邏輯可共享**：
- `design-extraction.md` 中的 Grep pattern、CSS 解析邏輯、頻率統計演算法
- 這些是跨專案通用的工具，屬於 Layer 1（Core Skills）或 Layer 2（Global Tools）
- 不屬於 Layer 3（Project），因此不受「專案特定」限制

### 晉升流程

1. `/ct-fieldguide update` 完成後，比對更新的 L1/L2 與 `seed-l1.md` / `seed-l2-templates.md`
2. 若發現新的通用原則（L1 中不含專案特定名稱）→ 在工單回報區標記 `[FG-PROMOTE]`
3. 塔台 `*fieldguide scan` 讀到 `[FG-PROMOTE]` 標記時，提議晉升
4. 使用者確認後，寫入 Global 層

### 晉升時的格式轉換

- **L1**：直接複製（本身不含專案特定內容）
- **L2**：去除具體元件名稱和路徑，保留決策結構

---

## 引用機制

**Project FIELDGUIDE.md 不直接引用 Global 層。**

設計理由：
- FIELDGUIDE.md 需要自包含（sub-session 讀取時不需額外載入 Global 層）
- Global 層是「種子 + 晉升倉庫」，不是「運行時依賴」
- `init` 時從 Global 層複製種子內容到 Project FIELDGUIDE.md

**資料流**：
```
Global seed → init 時複製到 → Project FIELDGUIDE.md（自包含）
                                    ↓
                              日常使用中演化
                                    ↓
                              L1/L2 晉升回 → Global promoted/
```

---

## Global 層不存在時的行為

若 `~/.claude/control-tower-data/fieldguide/` 不存在：
- `/ct-fieldguide init`：從空白開始，完全靠程式碼掃描產生 FIELDGUIDE
- `/ct-fieldguide update`：正常更新，跳過晉升評估
- 首次產生有價值的 L1/L2 時，提議建立 Global 層
