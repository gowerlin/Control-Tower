# DESIGN.md 擷取流程

> 本文件定義 `/ct-fieldguide design` 從專案程式碼擷取視覺規範的完整流程。
> 供 design 子命令參考。

## 擷取流程總覽

| Step | 名稱 | 說明 | 修正 |
|------|------|------|------|
| 0.5 | 專案結構偵測 | monorepo vs 單專案判斷 | M4 |
| 1 | 偵測設計系統來源 | 按優先級掃描技術棧 | M1 |
| 2 | 擷取色彩系統 | 色碼收集 + 語意角色分類 | M2/M3/M6 |
| 3 | 擷取字體系統 | font-family + size 層級 + weight |  |
| 4 | 擷取間距與佈局 | 間距基數 + 圓角 + 斷點 |  |
| 5 | 擷取元件樣式 | 按鈕/輸入框/卡片/導覽列 | M5 |
| 6 | 偵測暗黑模式 | media query / class toggle / library |  |
| 7 | 擷取 Do's and Don'ts | **P2 占位** — 暫不實作 | M7 |
| 8 | 組裝 DESIGN.md | 九章節標準格式 + 信心度標注 |  |
| 9 | 寫入與收尾 | 備份邏輯 + 寫入 + 完成摘要 |  |

```
流程圖：

Step 0.5 專案結構偵測
    │
    ├─ 單專案 → 產生 1 份 DESIGN.md
    └─ monorepo → 每個子專案各產生 1 份 + 交叉引用
         │
Step 1  偵測設計系統來源（按優先級）
         │
Step 2  擷取色彩系統
         │
Step 3  擷取字體系統
         │
Step 4  擷取間距與佈局
         │
Step 5  擷取元件樣式
         │
Step 6  偵測暗黑模式
         │
Step 7  Do's/Don'ts（P2 占位）
         │
Step 8  組裝 DESIGN.md（九章節）
         │
Step 9  寫入與收尾
```

### 擷取模式

| 模式 | 觸發 | 步驟 | 能力 |
|------|------|------|------|
| 靜態擷取 | `/ct-fieldguide design` 或 `/ct-fieldguide design [path]` | Step 0.5-9 | 色彩、字體、間距、元件、暗黑模式 |
| URL 靜態 | `/ct-fieldguide design [url]`（Chrome MCP 不可用時） | Step U1-U5 | CSS 層定義（custom properties、@font-face、media query） |
| Chrome MCP | `/ct-fieldguide design [url]`（Chrome MCP 可用時） | Step C1-C5 + Step 3.5 + Step 4.5 | 靜態全部 + 佈局結構 + 排版深度 |
| 混合模式 | 有原始碼 + URL | 靜態 Step 1-9 + Chrome Step 3.5/4.5 | 最完整 |

### URL 模式自動路由

當 source 為 URL 格式時：

```
/ct-fieldguide design [url]
├── 偵測 Chrome MCP 可用性
│   ├── 可用 → Chrome MCP 模式（Step C1-C5 + Step 3.5 + Step 4.5）
│   └── 不可用 → URL 靜態分析（Step U1-U5）
└── 顯示模式選擇結果
    ├── ✅ Chrome MCP 連接成功 → 使用 Chrome MCP 模式
    └── ⚠️ Chrome MCP 不可用 → 降級為 URL 靜態分析（信心度 -15~20%）
```

---

## Step 0.5：專案結構偵測（M4）

**觸發條件**：所有 `design` 子命令執行時的第一步。

**輸入**：專案根目錄。

**Glob 指令**：

```
Glob: pattern="**/package.json" → 列出所有 package.json 位置
Glob: pattern="**/pnpm-workspace.yaml"
Glob: pattern="**/lerna.json"
Glob: pattern="**/nx.json"
Glob: pattern="**/turbo.json"
```

**處理邏輯**：

```
偵測到 workspace 設定檔？
├─ 是 → monorepo 模式
│   ├─ 列出所有子專案（含 package.json 的子目錄）
│   ├─ 篩選有前端依賴的子專案（dependencies 含 vue/react/angular）
│   ├─ 檢查子專案間是否共享 theme（共用 styles/ 目錄）
│   └─ 產生子專案清單，標註共享關係
└─ 否 → 單專案模式
    └─ 直接進入 Step 1
```

**輸出**：

```yaml
structure: single | monorepo
subprojects:          # monorepo 才有
  - name: "crm"
    path: "packages/crm"
    shared_theme: "src/styles/"
  - name: "sso"
    path: "packages/sso"
    shared_theme: null   # 獨立 theme
```

**降級行為**：若無 workspace 設定檔，預設為單專案模式。

---

## Step 1：偵測設計系統來源（M1 Tailwind v4 擴充）

**觸發條件**：Step 0.5 完成後。每個子專案（或單專案）各執行一次。

**輸入**：專案根目錄（或子專案目錄）。

**偵測順序表**：

| 優先級 | Glob / Grep 指令 | 設計系統類型 | 擷取策略 |
|--------|-----------------|-------------|---------|
| 1 | `Glob: pattern="DESIGN.md"` | 已有 DESIGN.md | 詢問重建 / 跳過 |
| 2a | `Glob: pattern="tailwind.config.*"` | Tailwind v3 | 解析 `theme.extend` |
| 2b | `Grep: pattern="@theme\|@import \"tailwindcss\"" glob="*.css"` | Tailwind v4 | 解析 `@theme` 區塊 |
| 3 | `Glob: pattern="**/tokens.json"` + `Glob: pattern="style-dictionary.*"` | Design Token | 解析結構化 token |
| 4 | `Grep: pattern="\\$color-\|\\$brand-\|\\$theme-" glob="**/*.scss"` | SCSS 變數 | 解析 `$` 變數 |
| 5 | `Grep: pattern="--[a-z]+-" glob="**/*.css"` 含 `:root` | CSS Custom Properties | 解析 `--*` 變數 |
| 6 | `Grep: pattern="--el-color-\|--el-bg-" glob="**/*.{css,scss}"` | Element Plus 主題覆寫 | 解析 `--el-*` 變數 |
| 7 | 以上皆無 | 無設計系統 | 掃描 inline style + hardcoded 值 |

**Grep/Glob 指令（Tailwind v4 偵測詳細）**：

```bash
# Tailwind v3 — 傳統 config 檔案
Glob: pattern="tailwind.config.*"

# Tailwind v4 — CSS-based configuration（M1）
Grep: pattern="@theme" glob="**/*.css"
Grep: pattern="@import \"tailwindcss\"" glob="**/*.css"
Grep: pattern="@import 'tailwindcss'" glob="**/*.css"
```

**處理邏輯**：

```
偵測結果判斷：
├─ 命中 #1（DESIGN.md 已存在）
│   → 詢問使用者：重建 / 跳過 / 合併
├─ 命中 #2a → Tailwind v3 模式
│   → 讀取 tailwind.config.* → 解析 theme.extend
├─ 命中 #2b → Tailwind v4 模式
│   → 找到含 @theme 的 CSS 檔案 → 解析 @theme 區塊內 --color-* 定義
│   → 同時檢查 :root 和 .dark 的 CSS custom properties
├─ 命中 #3 → Design Token 模式
│   → 解析 tokens.json 結構
├─ 命中 #4 → SCSS 變數模式
│   → Grep 收集所有 $ 變數定義
├─ 命中 #5 → CSS Custom Properties 模式
│   → Grep 收集 :root 中所有 -- 變數
├─ 命中 #6 → Element Plus 覆寫模式（觸發 M6 差異化擷取）
│   → 只記錄覆寫的 --el-* 變數，不擷取 library 預設值
└─ 命中 #7 → 無系統模式
    → 使用頻率統計法

可能同時命中多個（如 Tailwind + CSS var），按優先級合併。
```

**輸出**：

```yaml
source_type: "tailwind-v4" | "tailwind-v3" | "design-token" | "scss" | "css-var" | "element-plus" | "none"
source_files:
  - "src/index.css"       # 含 @theme 定義
  - "src/app.css"         # 含 :root 變數
library_detected: null | "element-plus" | "ant-design" | "vuetify"
library_version: null | "2.x"
extraction_mode: "full" | "differential"   # M6
```

**降級行為**：全部偵測失敗 → 進入 #7 無系統模式，頻率統計。

---

## Step 2：擷取色彩系統（M2 OKLch + M3 Runtime + M6 差異化）

**觸發條件**：Step 1 完成，已知 source_type。

**輸入**：Step 1 偵測到的來源檔案。

### 2a. 收集色彩定義

**按 source_type 分支執行**：

**Tailwind v4 模式**：
```bash
# 在 @theme 區塊中搜尋色彩定義
Grep: pattern="--color-" glob="**/*.css"
Grep: pattern="--[a-z]+" glob="**/*.css" -B 1 -A 1
# 搜尋 :root 中的所有 custom properties
Grep: pattern=":root\s*\{" glob="**/*.css" -A 50
# 搜尋 .dark 區塊
Grep: pattern="\.dark\s*\{" glob="**/*.css" -A 50
```

**Tailwind v3 模式**：
```bash
# 讀取 config 檔案
Read: tailwind.config.* → 解析 theme.colors / theme.extend.colors
```

**SCSS 模式**：
```bash
Grep: pattern="\\$color-" glob="**/*.scss"
Grep: pattern="\\$brand-" glob="**/*.scss"
Grep: pattern="\\$theme-" glob="**/*.scss"
```

**CSS Custom Properties 模式**：
```bash
Grep: pattern="--color-" glob="**/*.css"
Grep: pattern="--[a-z]+-color" glob="**/*.css"
```

**Element Plus 差異化模式（M6）**：
```bash
# 只搜尋覆寫的變數（非 library 預設值）
Grep: pattern="--el-color-primary" glob="**/*.{css,scss}"
Grep: pattern="--el-color-success|--el-color-warning|--el-color-danger|--el-color-info" glob="**/*.{css,scss}"
# 搜尋品牌色 SCSS 變數
Grep: pattern="\\$brand-" glob="**/*.scss"
```

**Runtime theme 偵測（M3）**：
```bash
# JavaScript 動態設定主題色
Grep: pattern="setProperty" glob="**/*.{ts,js,vue}"
Grep: pattern="style\.setProperty" glob="**/*.{ts,js,vue}"
# Vue composable / hook 形式
Grep: pattern="useTheme|useDark" glob="**/*.{ts,js,vue}"
```

**無系統模式（頻率統計）**：
```bash
# 收集所有 hardcoded 色碼
Grep: pattern="#[0-9a-fA-F]{3,8}" glob="**/*.{vue,tsx,jsx,css,scss}"
Grep: pattern="rgb\(|rgba\(" glob="**/*.{vue,tsx,jsx,css,scss}"
Grep: pattern="hsl\(|hsla\(" glob="**/*.{vue,tsx,jsx,css,scss}"
Grep: pattern="oklch\(" glob="**/*.{vue,tsx,jsx,css,scss}"
```

### 2b. 語意角色分類

```
分類邏輯：
├─ 有語意命名（primary/success/warning/error/danger/info）
│   → 直接映射（信心度：高）
├─ 有 Element Plus 命名（--el-color-primary 等）
│   → 映射到標準角色（信心度：高）
├─ 有 shadcn/ui 命名（--background/--foreground/--primary 等）
│   → 映射到標準角色（信心度：高）
└─ 無語意命名
    → 從使用場景推斷（信心度：中/低）：
        ├─ 按鈕背景色 + 最高頻 → primary
        ├─ .error / .danger 類中使用 → error/danger
        ├─ .success 類中使用 → success
        └─ 其餘按頻率標記 accent-1、accent-2、neutral-*
```

### 2c. 色碼格式解析（M2）

所有收集到的色碼需統一解析。支援格式見本文末「色碼格式支援」章節。

**輸出**：

```yaml
colors:
  - role: "primary"
    value: "oklch(0.205 0 0)"
    source_var: "--primary"
    source_file: "src/index.css"
    confidence: "高"    # 直接映射
  - role: "success"
    value: "#67C23A"
    source_var: null     # Element Plus 預設值，未覆寫
    source_file: null
    confidence: "中"    # 推測使用預設
runtime_themes:
  - hook: "useTheme()"
    file: "src/composables/useTheme.ts"
    mechanism: "setProperty"
```

**降級行為**：
- 無任何色彩定義 → 報告「色彩系統：未偵測到」，信心度標為低。
- runtime theme 未偵測到 → 略過 runtime 段落，僅記錄靜態色彩。

---

## Step 3：擷取字體系統

**觸發條件**：Step 2 完成。

**輸入**：CSS/SCSS/Tailwind 設定檔。

### 3a. font-family

```bash
# CSS/SCSS 定義
Grep: pattern="font-family:" glob="**/*.{css,scss}"
# @font-face 宣告
Grep: pattern="@font-face" glob="**/*.{css,scss}" -A 5
# Google Fonts import
Grep: pattern="fonts\.googleapis\.com" glob="**/*.{css,scss,html}"
# Tailwind v4 字體定義
Grep: pattern="--font-" glob="**/*.css"
```

**處理邏輯**：

```
區分字體用途：
├─ 主字體（body / sans）→ 出現在 body 或 :root 或 --font-sans
├─ 等寬字體（code / mono）→ 出現在 code 或 pre 或 --font-mono
├─ 裝飾字體 → @font-face 載入的非系統字體
└─ UI Library 預設 → 若未覆寫，標註「使用 <library> 預設值」
```

### 3b. font-size 層級

```bash
# Tailwind v4
Grep: pattern="--text-" glob="**/*.css"
# CSS/SCSS 定義
Grep: pattern="font-size:" glob="**/*.{css,scss}"
# Element Plus 覆寫
Grep: pattern="--el-font-size" glob="**/*.{css,scss}"
```

**處理邏輯**：

```
收集所有尺寸值後歸納層級：
├─ 有明確命名（text-xs / text-sm / text-base / text-lg / text-xl）
│   → 直接使用命名層級
├─ 僅有 px 值
│   → 從 HTML 標籤用途推斷：h1 > h2 > h3 > body > caption > label
└─ 產出完整字體層級表
```

### 3c. font-weight 與 line-height

```bash
Grep: pattern="font-weight:" glob="**/*.{css,scss}"
Grep: pattern="--font-weight" glob="**/*.css"
Grep: pattern="line-height:" glob="**/*.{css,scss}"
```

**輸出**：

```yaml
typography:
  families:
    - name: "Inter"
      role: "sans"          # sans / mono / display
      source: "@font-face in src/index.css"
      weights: [400, 500, 600, 700]
  sizes:
    - name: "text-xs"
      value: "10px"
      usage: "label, caption"
    - name: "text-sm"
      value: "12px"
      usage: "body small"
  line_heights:
    - context: "body"
      value: "1.5"
```

**降級行為**：
- 無字體定義 → 報告「字體系統：使用瀏覽器/library 預設」。
- 僅有部分資訊 → 填入已知部分，其餘標註「未偵測」。

---

## Step 3.5：排版風格深度擷取（Chrome MCP 專用）

> 此步驟僅在 Chrome MCP 模式下執行。靜態模式跳過此步驟。
> 擷取 heading 視覺層級、表格排版、表單排版的 computed styles。

**觸發條件**：Step 3 完成，且為 Chrome MCP 或混合模式。

**輸入**：已載入的網頁（Chrome MCP 連線中）。

### 3.5a. 標題視覺層級

```javascript
// 擷取 h1-h6 computed styles
const headings = {};
['h1','h2','h3','h4','h5','h6'].forEach(tag => {
  const el = document.querySelector(tag);
  if (el) {
    const s = getComputedStyle(el);
    headings[tag] = {
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      lineHeight: s.lineHeight,
      marginTop: s.marginTop,
      marginBottom: s.marginBottom,
      color: s.color
    };
  }
});
JSON.stringify(headings, null, 2);
```

### 3.5b. 表格排版

```javascript
// 擷取 Element Plus 表格排版
const tableTypo = {};
const thCell = document.querySelector('.el-table__header-wrapper th .cell');
if (thCell) {
  const s = getComputedStyle(thCell);
  const th = getComputedStyle(thCell.closest('th'));
  tableTypo.header = {
    fontSize: s.fontSize, fontWeight: s.fontWeight,
    height: th.height, backgroundColor: th.backgroundColor,
    borderBottom: th.borderBottomWidth + ' ' + th.borderBottomStyle + ' ' + th.borderBottomColor
  };
}
const tdCell = document.querySelector('.el-table__body-wrapper td .cell');
if (tdCell) {
  const s = getComputedStyle(tdCell);
  const td = getComputedStyle(tdCell.closest('td'));
  tableTypo.body = {
    fontSize: s.fontSize, fontWeight: s.fontWeight,
    height: td.height, backgroundColor: td.backgroundColor,
    borderBottom: td.borderBottomWidth + ' ' + td.borderBottomStyle + ' ' + td.borderBottomColor
  };
}
// 斑馬紋偵測
const rows = document.querySelectorAll('.el-table__body-wrapper tr');
if (rows.length >= 2) {
  const bg0 = getComputedStyle(rows[0]).backgroundColor;
  const bg1 = getComputedStyle(rows[1]).backgroundColor;
  tableTypo.striped = bg0 !== bg1;
  if (tableTypo.striped) tableTypo.stripeColor = bg1;
}
JSON.stringify(tableTypo, null, 2);
```

**降級行為**：頁面上找不到 `.el-table` → 跳過表格排版，在 DESIGN.md 標注「表格排版：當前頁面無表格元素」。

### 3.5c. 表單排版

```javascript
// 擷取 Element Plus 表單排版
const formTypo = {};
const label = document.querySelector('.el-form-item__label');
if (label) {
  const s = getComputedStyle(label);
  formTypo.label = {
    fontSize: s.fontSize, fontWeight: s.fontWeight,
    lineHeight: s.lineHeight, color: s.color,
    width: s.width
  };
}
const input = document.querySelector('.el-input__inner');
if (input) {
  const s = getComputedStyle(input);
  formTypo.input = {
    fontSize: s.fontSize, fontWeight: s.fontWeight,
    height: s.height, color: s.color,
    borderRadius: s.borderRadius
  };
}
const formItem = document.querySelector('.el-form-item');
if (formItem) {
  const s = getComputedStyle(formItem);
  formTypo.itemSpacing = { marginBottom: s.marginBottom };
}
JSON.stringify(formTypo, null, 2);
```

**降級行為**：頁面上找不到 `.el-form-item` → 跳過表單排版，在 DESIGN.md 標注「表單排版：當前頁面無表單元素」。

### DESIGN.md 輸出格式

擷取結果寫入 Chapter 3 Typography Rules 的子章節：

```markdown
### Heading Visual Hierarchy（Chrome MCP 擷取）

| Level | Size | Weight | Line Height | Margin | Color | 用途 |
|-------|------|--------|-------------|--------|-------|------|
| h1 | 28px | 700 | normal | 0 / 12px | #fff | 主標題（hero 區） |
| h2 | — | — | — | — | — | 未使用 |

### Table Typography（Chrome MCP 擷取，若適用）

| 部位 | Font Size | Weight | Height | Background | Border |
|------|-----------|--------|--------|-----------|--------|
| Header | 15px | 700 | 45px | #f5f7fa | 1px solid #ebeef5 |
| Body | 14px | 400 | 45px | #fff | 1px solid #ebeef5 |
| Striped | — | — | — | — (無斑馬紋) | — |

### Form Typography（Chrome MCP 擷取，若適用）

| 元素 | Font Size | Weight | Height | Color |
|------|-----------|--------|--------|-------|
| Label | 14px | 400 | 32px lh | #606266 |
| Input | 14px | — | 30px | #606266 |
| Item spacing | — | — | mb: 18px | — |
```

**輸出**：Step 3.5 擷取的 JSON 結果，供 Step 8 組裝使用。

---

## Step 4：擷取間距與佈局

**觸發條件**：Step 3 完成。

**輸入**：CSS/SCSS/Tailwind 設定檔。

### 4a. 間距系統

```bash
# Tailwind
Grep: pattern="--spacing" glob="**/*.css"
# CSS Custom Properties
Grep: pattern="--gap-|--space-" glob="**/*.css"
# SCSS 變數
Grep: pattern="\\$spacing-|\\$gap-" glob="**/*.scss"
# 頻率統計（無系統模式）
Grep: pattern="margin:|padding:" glob="**/*.{css,scss,vue}" -A 0
```

**處理邏輯**：

```
歸納間距基數：
├─ 有明確 scale（如 Tailwind 的 4px 基數）→ 直接使用
├─ 有 CSS var 定義（--spacing-1: 4px 等）→ 解析 scale
└─ 無系統 → 統計 margin/padding 值頻率
    → 找出最小公約值作為基數（常見：4px / 8px）
```

### 4b. 圓角系統

```bash
Grep: pattern="border-radius:" glob="**/*.{css,scss}"
Grep: pattern="--radius" glob="**/*.css"
Grep: pattern="rounded-" glob="**/*.{vue,tsx,jsx}"
```

**處理邏輯**：

```
歸納常用值：
├─ sm = 常見最小值（如 4px / 0.25rem）
├─ md = 常見中等值（如 8px / 0.5rem）
├─ lg = 常見最大值（如 12px / 0.75rem）
├─ xl = 16px 或以上
└─ full = 9999px / 50%（圓形）
```

### 4c. 容器與網格

```bash
Grep: pattern="max-width:" glob="**/*.{css,scss}"
Grep: pattern="container" glob="**/*.{css,scss}"
# 響應式斷點
Grep: pattern="@media.*min-width|@media.*max-width" glob="**/*.{css,scss}"
# Tailwind 斷點
Grep: pattern="--breakpoint-" glob="**/*.css"
Grep: pattern="screens:" glob="tailwind.config.*"
```

**輸出**：

```yaml
spacing:
  base: "4px"
  scale: [0, 1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64]
border_radius:
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
breakpoints:
  sm: "640px"
  md: "768px"
  lg: "1024px"
  xl: "1280px"
container:
  max_width: "1280px"
```

**降級行為**：
- 無間距系統 → 統計前 10 常用 margin/padding 值，歸納基數。
- 無斷點 → 檢查是否為桌面應用（Electron 等），標註「響應式：不適用」。

---

## Step 4.5：擷取佈局結構（Chrome MCP 專用）

> 此步驟僅在 Chrome MCP 模式下執行。靜態模式跳過此步驟。
> 偵測頁面骨架（header/sidebar/footer）、容器佈局模式、導航結構。

**觸發條件**：Step 4 完成，且為 Chrome MCP 或混合模式。

**輸入**：已載入的網頁（Chrome MCP 連線中）。

### 4.5a. 頁面骨架偵測

```javascript
// 偵測主要佈局區域並測量尺寸
const layout = { regions: {} };

// Header
const header = document.querySelector('.el-header, header, [class*="header"], [class*="navbar"]');
if (header) {
  const s = getComputedStyle(header);
  layout.regions.header = {
    exists: true, height: s.height, width: s.width,
    position: s.position, backgroundColor: s.backgroundColor
  };
}

// Sidebar
const sidebar = document.querySelector('.el-aside, aside, [class*="sidebar"], [class*="side-menu"]');
if (sidebar) {
  const s = getComputedStyle(sidebar);
  layout.regions.sidebar = {
    exists: true, width: s.width, height: s.height,
    position: s.position, backgroundColor: s.backgroundColor
  };
}

// Footer
const footer = document.querySelector('.el-footer, footer, [class*="footer"]');
if (footer) {
  const s = getComputedStyle(footer);
  layout.regions.footer = {
    exists: true, height: s.height,
    position: s.position, backgroundColor: s.backgroundColor
  };
}

// Main content
const main = document.querySelector('.el-main, main, [class*="main-content"], [class*="app-main"]');
if (main) {
  const s = getComputedStyle(main);
  layout.regions.main = {
    exists: true, flex: s.flex, overflow: s.overflow,
    padding: s.padding, backgroundColor: s.backgroundColor
  };
}

JSON.stringify(layout, null, 2);
```

### 4.5b. 容器佈局模式偵測

```javascript
// 偵測 flex/grid 佈局模式
const containers = document.querySelectorAll('.el-container, [class*="layout"], [class*="container"]');
const layoutPatterns = [];

containers.forEach((c, i) => {
  if (i >= 5) return; // 最多偵測 5 個容器
  const s = getComputedStyle(c);
  const pattern = {
    tag: c.tagName.toLowerCase(),
    className: c.className.split(' ').slice(0, 3).join(' '),
    display: s.display,
    flexDirection: s.display === 'flex' ? s.flexDirection : null,
    gridTemplateColumns: s.display === 'grid' ? s.gridTemplateColumns : null,
    children: c.children.length,
    nested: c.querySelector('.el-container') ? true : false
  };
  layoutPatterns.push(pattern);
});

JSON.stringify(layoutPatterns, null, 2);
```

### 4.5c. 導航結構偵測

```javascript
// 偵測導航結構
const navigation = {};

// 主導航（sidebar menu / top menu）
const menus = document.querySelectorAll('.el-menu');
menus.forEach((menu, i) => {
  const s = getComputedStyle(menu);
  const isVertical = menu.classList.contains('el-menu--vertical') ||
                     s.flexDirection === 'column';
  const items = menu.querySelectorAll(':scope > .el-menu-item, :scope > .el-sub-menu');
  const subMenus = menu.querySelectorAll('.el-sub-menu');

  navigation[`menu_${i}`] = {
    direction: isVertical ? 'vertical' : 'horizontal',
    topLevelItems: items.length,
    hasSubMenus: subMenus.length > 0,
    maxDepth: subMenus.length > 0 ? 2 : 1,
    activeColor: s.getPropertyValue('--el-menu-active-color') || null,
    backgroundColor: s.backgroundColor
  };
});

// 麵包屑
const breadcrumb = document.querySelector('.el-breadcrumb');
if (breadcrumb) {
  const items = breadcrumb.querySelectorAll('.el-breadcrumb__item');
  navigation.breadcrumb = { exists: true, levels: items.length };
}

// Tabs 頁籤
const tabs = document.querySelector('.el-tabs');
if (tabs) {
  const tabItems = tabs.querySelectorAll('.el-tabs__item');
  navigation.tabs = { exists: true, count: tabItems.length };
}

JSON.stringify(navigation, null, 2);
```

### DESIGN.md 輸出格式

擷取結果寫入 Chapter 5 Layout Principles 的子章節：

```markdown
### Page Skeleton（Chrome MCP 擷取）

| 區域 | 存在 | 尺寸 | 定位 | 背景色 |
|------|------|------|------|--------|
| Header | ✅ | h: 60px, w: 100% | fixed | #009688 |
| Sidebar | ✅ | w: 211px | static | #ffffff |
| Footer | ✅ | h: 40px | static | transparent |
| Main Content | ✅ | flex: 1 | — | #f0f2f5 |

- Layout Type: sidebar + header + content (flex row)
- Container: el-container (display: flex, direction: row)

### Navigation Structure（Chrome MCP 擷取）

- Primary: Sidebar vertical menu (el-menu--vertical)
  - Menu items: 10 top-level, 深度 2 級
  - Active style: bg `#e6f5f3`, color `#009688`
- Secondary: Breadcrumb (el-breadcrumb)
- Tertiary: Page tabs (el-tabs)
```

**降級行為**：
- 頁面無 `.el-container` 且無語意 HTML 佈局元素 → 跳過佈局偵測，標注「佈局結構：無法偵測」。
- 無 `.el-menu` → 跳過導航偵測，標注「導航結構：未偵測到選單元素」。

**輸出**：Step 4.5 擷取的 JSON 結果，供 Step 8 組裝使用。

---

## Step 5：擷取元件樣式（M5 CVA 偵測）

**觸發條件**：Step 4 完成。

**輸入**：元件目錄、CSS/SCSS 檔案。

### CVA 偵測（M5 — 優先路徑）

```bash
# 搜尋 CVA 函式呼叫
Grep: pattern="cva\(" glob="**/*.{ts,tsx,vue}"
# 搜尋 variants 定義
Grep: pattern="variants:" glob="**/*.{ts,tsx,vue}" -A 20
```

**CVA 處理邏輯**：

```
CVA 偵測結果？
├─ 找到 cva() 呼叫
│   → 解析 variants 物件：
│       ├─ variant（如 default / destructive / outline / ghost）
│       ├─ size（如 default / sm / lg / icon）
│       └─ 每個 variant 的 class 列表
│   → 直接對應到 DESIGN.md Component Stylings 章節
│   → 信心度：高（CVA 是 100% 準確的樣式來源）
└─ 未找到 cva()
    → 進入傳統 CSS class grep 路徑
```

### 5a. 按鈕

```bash
# CVA 路徑（優先）
Grep: pattern="buttonVariants|button.*cva" glob="**/*.{ts,tsx,vue}" -A 30

# CSS class 路徑（降級）
Grep: pattern="\.btn-|\.el-button--" glob="**/*.{css,scss}"
Grep: pattern="\.btn\s*\{" glob="**/*.{css,scss}" -A 10
```

**提取**：default / hover / active / disabled / loading 各狀態的樣式，以及 variant 清單（primary / secondary / outline / ghost / danger）。

### 5b. 輸入框

```bash
Grep: pattern="\.input-|\.el-input" glob="**/*.{css,scss}" -A 5
Grep: pattern="input.*cva" glob="**/*.{ts,tsx,vue}" -A 20
```

**提取**：normal / focus / error / disabled 各狀態樣式。

### 5c. 卡片與容器

```bash
Grep: pattern="\.card-|\.el-card" glob="**/*.{css,scss}" -A 10
Grep: pattern="card.*cva" glob="**/*.{ts,tsx,vue}" -A 20
```

**提取**：padding、border-radius、shadow 值。

### 5d. 導覽列

```bash
Grep: pattern="\.nav-|\.sidebar-|\.header-" glob="**/*.{css,scss}" -A 10
Grep: pattern="--sidebar" glob="**/*.css"
```

**提取**：佈局模式（fixed / sticky）、背景色、寬度。

**輸出**：

```yaml
components:
  button:
    source: "cva"          # 或 "css-class"
    confidence: "高"
    variants:
      - name: "default"
        classes: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90"
      - name: "destructive"
        classes: "bg-destructive text-white shadow-xs hover:bg-destructive/90"
    sizes:
      - name: "default"
        classes: "h-9 px-4 py-2"
      - name: "sm"
        classes: "h-8 rounded-md px-3 text-xs"
  input:
    source: "css-class"
    confidence: "中"
```

**降級行為**：
- 無 CVA 且無 CSS class → 報告「元件樣式：依賴 library 預設，無自訂樣式」。
- 部分元件無資料 → 僅輸出有資料的元件，其餘略過。

---

## Step 6：偵測暗黑模式

**觸發條件**：Step 5 完成。

**輸入**：CSS/SCSS 檔案、JavaScript/TypeScript 檔案。

**Grep 指令**：

```bash
# CSS media query 模式
Grep: pattern="prefers-color-scheme:\s*dark" glob="**/*.{css,scss}"

# Class toggle 模式
Grep: pattern="\.dark\s" glob="**/*.{css,scss}"
Grep: pattern="\[data-theme=.dark.\]" glob="**/*.{css,scss}"
Grep: pattern="html\.dark|:root\.dark" glob="**/*.{css,scss}"

# Element Plus dark mode
Grep: pattern="--el-bg-color-dark|--el-fill-color-dark" glob="**/*.{css,scss}"
Grep: pattern="useDark|isDark|toggleDark" glob="**/*.{ts,js,vue}"

# Tailwind dark mode
Grep: pattern="dark:" glob="**/*.{vue,tsx,jsx}" -c
```

**處理邏輯**：

```
暗黑模式偵測結果？
├─ 偵測到 prefers-color-scheme → media query 模式
│   → 提取 dark 色彩映射
├─ 偵測到 .dark class → class toggle 模式
│   → 提取 .dark 區塊內的色彩覆寫
│   → 檢查切換機制（useDark / localStorage / system）
├─ 偵測到 Element Plus dark → library dark 模式
│   → 記錄 --el-*-dark 變數覆寫
├─ 偵測到 dark: prefix → Tailwind dark 模式
│   → 統計 dark: utility 使用數量
└─ 未偵測到
    → 標記「暗黑模式：未實作」
```

**輸出**：

```yaml
dark_mode:
  detected: true | false
  mechanism: "class-toggle" | "media-query" | "library" | "tailwind-dark" | null
  toggle_method: "useDark() hook" | "localStorage" | null
  color_overrides:
    - role: "background"
      light: "oklch(1 0 0)"
      dark: "oklch(0.145 0 0)"
```

**降級行為**：未偵測到 → 在 DESIGN.md 第 8 章標註「暗黑模式：未實作」。

---

## Step 7：擷取 Do's and Don'ts（P2 占位 — M7）

**觸發條件**：Step 6 完成。

**狀態**：**P2（暫不實作）**。T0051 實測顯示從程式碼自動推斷 Do's/Don'ts 效果有限，手動撰寫更有價值。

**目前行為**：

```
產生占位內容：
├─ Do's → 「（待手動補充：根據專案慣例和設計決策填寫）」
├─ Don'ts → 「（待手動補充：根據常見錯誤和反模式填寫）」
└─ 信心度 → 標為「低（自動擷取）」或「無（占位）」
```

**未來計畫**（P2 實作時）：
- 從 FIELDGUIDE.md 的相關章節提取（L2 決策樹 → Do's）
- 從 .eslintrc / stylelint 設定提取禁用規則
- 從 CSS 註解提取 TODO / FIXME / HACK

---

## Step 8：組裝 DESIGN.md

**觸發條件**：Step 7 完成（所有擷取步驟結束）。

**輸入**：Step 2-7 的所有中間結果。

**處理邏輯**：

1. 計算整體信心度：各 Step 信心度加權平均
   - 色彩系統 × 0.30
   - 字體系統 × 0.15
   - 元件樣式 × 0.25
   - 間距佈局 × 0.15
   - 暗黑模式 × 0.10
   - Do's/Don'ts × 0.05

2. 填入九章節模板（見下方「DESIGN.md 標準格式」）

3. 每個章節末尾標註信心度

**信心度計算規則**：

| 等級 | 標準 | 說明 |
|------|------|------|
| 高 | 直接映射 | 色碼/樣式有明確語意命名，可直接對應角色 |
| 中 | 推斷 | 從使用場景、class 名稱、檔案位置推斷用途 |
| 低 | 頻率統計 | 僅從出現頻率推測重要性，無語意佐證 |

**輸出**：完整 DESIGN.md 文件內容（字串）。

### Chrome MCP 結果整合

若有 Chrome MCP 擷取結果（Step 3.5 / Step 4.5）：

1. **Chapter 3 Typography Rules**：合併靜態字體定義 + Chrome MCP 排版深度
   - 靜態 Font Family / Size / Weight 為基礎
   - Chrome MCP 的 Heading Visual Hierarchy、Table Typography、Form Typography 作為子章節追加
   - 若靜態和 Chrome MCP 有衝突值 → 以 Chrome MCP（computed）為準，標注「runtime 驗證值」

2. **Chapter 5 Layout Principles**：合併靜態間距 token + Chrome MCP 佈局結構
   - 靜態 Spacing / Radius / Breakpoints 為基礎
   - Chrome MCP 的 Page Skeleton、Navigation Structure 作為子章節追加

3. **metadata**：標注 `擷取模式：混合（靜態 + Chrome MCP）` 或 `擷取模式：Chrome MCP`

4. **信心度**：Chrome MCP 擷取的子章節信心度額外加 10%（runtime computed = 高準確度）
   - 靜態擷取為「中」的排版項目 → Chrome MCP 驗證後提升為「高」
   - Chrome MCP 獨有章節（Page Skeleton / Navigation Structure）→ 直接標為「高」

---

## Step 9：寫入與收尾

**觸發條件**：Step 8 組裝完成。

**輸入**：Step 8 的 DESIGN.md 文件內容、寫入目標路徑。

**處理邏輯**：

```
1. 寫入前檢查
   ├─ DESIGN.md 已存在？
   │   ├─ 存在 → 備份為 DESIGN.md.bak，詢問覆蓋/合併/取消
   │   └─ 不存在 → 直接寫入
   └─ monorepo 模式 → 確認每個子專案的寫入路徑

2. 寫入 DESIGN.md
   ├─ 單專案 → 寫入專案根目錄
   └─ monorepo → 每個子專案目錄各寫一份

3. 顯示完成摘要
   ✅ DESIGN.md 已產生
      路徑：<路徑>
      擷取來源：<source_type>
      色彩角色：<N> 個（直接映射 <N>、推斷 <N>、頻率 <N>）
      字體層級：<N> 級
      元件樣式：<N> 個（CVA: <N>、CSS: <N>）
      暗黑模式：<偵測結果>
      整體信心度：<N%>
```

**降級行為**：
- 備份失敗 → 警告使用者，詢問是否繼續覆蓋。
- 寫入失敗 → 將內容輸出到終端，讓使用者手動貼上。

---

## DESIGN.md 標準格式

九章節模板定義，遵循 Google Stitch 格式：

```markdown
# DESIGN.md — <專案名稱> 設計系統

> 擷取方式：專案程式碼掃描
> 擷取日期：<今日日期>
> 來源類型：<Tailwind v4 / Tailwind v3 / CSS var / SCSS / Element Plus / 推斷>
> 信心度：<N%>（語意角色直接映射比例）
> 技術棧：<偵測到的前端技術棧>

## 1. Visual Theme & Atmosphere

<整體設計哲學描述>
- 從元件密度、留白比例、色彩傾向推斷
- 標註「專業/現代/溫暖/極簡」等風格關鍵詞
- 若使用 UI library，標註框架風格基底

**信心度**：<高/中/低>（<推斷依據>）

## 2. Color Palette & Roles

### <模式名稱>（如 Light Mode / :root）

| 角色 | 色碼 | 來源變數 | 信心度 |
|------|------|---------|--------|
| primary | <色碼> | <--var-name> | <高/中/低> |
| ...

### Dark Mode（若有）

| 角色 | 色碼 | 備註 |
|------|------|------|
| ...

**信心度**：<高/中/低>（<說明>）

## 3. Typography Rules

### Font Family

| 用途 | 字體 | 來源 |
|------|------|------|
| 主字體 | <字體名> | <來源> |
| 等寬字體 | <字體名> | <來源> |

### Font Size Hierarchy

| 層級 | 值 | 用途 |
|------|-----|------|
| ...

### Font Weight

| 數值 | 語意 | 使用場景 |
|------|------|---------|
| ...

**信心度**：<高/中/低>（<說明>）

### Heading Visual Hierarchy（Chrome MCP 擷取時填入）

| Level | Size | Weight | Line Height | Margin | Color | 用途 |
|-------|------|--------|-------------|--------|-------|------|
| h1 | — | — | — | — | — | — |
| h2 | — | — | — | — | — | — |
| h3 | — | — | — | — | — | — |

> 此子章節由 Step 3.5 Chrome MCP 擷取填入。靜態模式不產生此表格。

### Table Typography（Chrome MCP 擷取時填入）

| 部位 | Font Size | Weight | Height | Background | Border |
|------|-----------|--------|--------|-----------|--------|
| Header | — | — | — | — | — |
| Body | — | — | — | — | — |
| Striped | — | — | — | — | — |

> 此子章節由 Step 3.5 Chrome MCP 擷取填入。頁面無表格時省略。

### Form Typography（Chrome MCP 擷取時填入）

| 元素 | Font Size | Weight | Height | Color |
|------|-----------|--------|--------|-------|
| Label | — | — | — | — |
| Input | — | — | — | — |
| Item spacing | — | — | — | — |

> 此子章節由 Step 3.5 Chrome MCP 擷取填入。頁面無表單時省略。

## 4. Component Stylings

### <元件名稱>（如 Button / Input / Card）

<CVA variants 表格 或 CSS class 描述>
- 列出所有 variant 和 size
- 各狀態（default / hover / active / disabled）的差異

**信心度**：<高/中/低>（<說明>）

## 5. Layout Principles

### Spacing Scale

| Token | 值 | 用途 |
|-------|-----|------|
| ...

### Border Radius

| Token | 值 |
|-------|-----|
| ...

### Container & Grid

- 最大寬度：<值>
- 網格系統：<描述>

### Responsive Breakpoints

| 名稱 | 值 |
|------|-----|
| ...

**信心度**：<高/中/低>（<說明>）

### Page Skeleton（Chrome MCP 擷取時填入）

| 區域 | 存在 | 尺寸 | 定位 | 背景色 |
|------|------|------|------|--------|
| Header | — | — | — | — |
| Sidebar | — | — | — | — |
| Footer | — | — | — | — |
| Main Content | — | — | — | — |

- Layout Type: （Chrome MCP 偵測填入）
- Container: （Chrome MCP 偵測填入）

> 此子章節由 Step 4.5 Chrome MCP 擷取填入。靜態模式不產生此表格。

### Navigation Structure（Chrome MCP 擷取時填入）

- Primary: （Chrome MCP 偵測填入）
- Secondary: （Chrome MCP 偵測填入）
- Tertiary: （Chrome MCP 偵測填入）

> 此子章節由 Step 4.5 Chrome MCP 擷取填入。靜態模式不產生此區段。

## 6. Depth & Elevation

| 層級 | Shadow 值 | 用途 |
|------|-----------|------|
| ...

**信心度**：<高/中/低>（<說明>）

## 7. Do's and Don'ts

### Do's
- （待手動補充 — P2）

### Don'ts
- （待手動補充 — P2）

**信心度**：低（自動擷取能力有限，建議手動撰寫）

## 8. Responsive Behavior

| 面向 | 規則 |
|------|------|
| 斷點 | <斷點表> |
| 觸控目標 | <最小尺寸> |
| 收合策略 | <sidebar/nav 在小螢幕的行為> |

**信心度**：<高/中/低>（<說明>）

## 9. Agent Prompt Guide

### Quick Color Reference

\```
Primary: <色碼> — <描述>
Secondary: <色碼> — <描述>
Destructive: <色碼> — <描述>
Background: <色碼>（light）/ <色碼>（dark）
\```

### AI Agent Usage

\```
1. <第一條使用指引>
2. <第二條使用指引>
...
\```

### Cross-Reference

- FIELDGUIDE.md：<路徑>（若存在）
- 設計系統來源：<路徑>
```

---

## 差異化擷取模式（M6）

當 Step 1 偵測到 UI library（Element Plus / Ant Design / Vuetify 等），啟動差異化模式。

**核心原則**：只記錄與 library 預設值**不同**的覆寫，避免擷取大量 library 預設值造成噪音。

### 偵測觸發

```bash
# Element Plus
Grep: pattern="element-plus" glob="package.json"
# Ant Design Vue
Grep: pattern="ant-design-vue" glob="package.json"
# Vuetify
Grep: pattern="vuetify" glob="package.json"
```

### 差異化擷取邏輯

```
Library 偵測結果？
├─ Element Plus
│   ├─ 搜尋覆寫的 CSS variables：
│   │   Grep: pattern="--el-" glob="**/*.{css,scss}" → 只取 :root 或 theme 檔案中的
│   ├─ 搜尋 runtime 覆寫：
│   │   Grep: pattern="setProperty.*--el-" glob="**/*.{ts,js,vue}"
│   ├─ 搜尋品牌色 SCSS：
│   │   Grep: pattern="\\$brand-|\\$el-" glob="**/*.scss"
│   └─ 對每個覆寫變數：
│       ├─ 記錄覆寫值和來源
│       └─ 標註與 library 預設值的差異
│
├─ Ant Design Vue
│   ├─ 搜尋 theme config：
│   │   Grep: pattern="theme:" glob="**/*.{ts,js}" -A 10
│   └─ 搜尋 token 覆寫：
│       Grep: pattern="token:" glob="**/*.{ts,js}" -A 10
│
└─ Vuetify
    └─ 搜尋 theme 設定：
        Grep: pattern="themes:" glob="**/*.{ts,js}" -A 20
```

### 差異化輸出格式

在 DESIGN.md 的 Color Palette 章節中：

```markdown
## 2. Color Palette & Roles

> 基底：Element Plus 2.x 預設主題
> 以下僅列出覆寫和擴充的色彩

### 覆寫色彩

| 角色 | 覆寫值 | Element Plus 預設 | 來源 | 信心度 |
|------|--------|------------------|------|--------|
| primary | #009688 | #409EFF | config/index.ts | 高 |

### 未覆寫（使用 Element Plus 預設）

| 角色 | 預設值 | 備註 |
|------|--------|------|
| success | #67C23A | 未覆寫 |
| warning | #E6A23C | 未覆寫 |
| danger  | #F56C6C | 未覆寫 |
| info    | #909399 | 未覆寫 |

### 品牌色擴充

| 角色 | 色碼 | 來源 |
|------|------|------|
| brand-primary | #008E6A | $brand-primary (brand.scss) |
```

---

## 色碼格式支援（M2）

所有色彩擷取步驟支援以下格式的解析：

| 格式 | 正則 Pattern | 範例 |
|------|-------------|------|
| HEX 3 | `#[0-9a-fA-F]{3}` | `#fff` |
| HEX 6 | `#[0-9a-fA-F]{6}` | `#009688` |
| HEX 8 | `#[0-9a-fA-F]{8}` | `#009688FF` |
| RGB | `rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)` | `rgb(0, 150, 136)` |
| RGBA | `rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)` | `rgba(0, 150, 136, 0.5)` |
| RGB (modern) | `rgb\(\s*\d+\s+\d+\s+\d+\s*(/\s*[\d.]+%?\s*)?\)` | `rgb(255 255 255 / 12%)` |
| HSL | `hsl\(\s*\d+\s*,\s*[\d.]+%\s*,\s*[\d.]+%\s*\)` | `hsl(174, 100%, 29%)` |
| HSLA | `hsla\(\s*\d+\s*,\s*[\d.]+%\s*,\s*[\d.]+%\s*,\s*[\d.]+\s*\)` | `hsla(174, 100%, 29%, 0.5)` |
| OKLch | `oklch\(\s*[\d.]+\s+[\d.]+\s+[\d.]+\s*\)` | `oklch(0.205 0 0)` |
| OKLch (alpha) | `oklch\(\s*[\d.]+\s+[\d.]+\s+[\d.]+\s*/\s*[\d.]+%?\s*\)` | `oklch(1 0 0 / 10%)` |

**統一 Grep pattern（收集所有色碼）**：

```bash
# 一次搜尋所有色碼格式
Grep: pattern="#[0-9a-fA-F]{3,8}|rgb\(|rgba\(|hsl\(|hsla\(|oklch\(" glob="**/*.{css,scss,vue,tsx,jsx}"
```

**OKLch 特別注意**：
- Tailwind v4 預設輸出 OKLch 格式
- OKLch 的 L（亮度）範圍為 0-1，C（色度）和 H（色相）為正數
- alpha 值以 `/ N%` 格式附加，如 `oklch(1 0 0 / 10%)`

---

## URL 靜態分析流程（Step U1-U5）

> 當 `/ct-fieldguide design [url]` 觸發且 Chrome MCP 不可用時，降級為靜態分析。
> 限制：無法擷取 SPA 渲染內容、CSS-in-JS、需登入的頁面。

### Step U1：抓取 HTML

```bash
curl -sL <url> -o page.html
```

- 解析 `<link rel="stylesheet">` 標籤，收集所有 CSS URL
- 將相對路徑轉為絕對路徑（基於 `<base>` 標籤或原始 URL）
- 解析 `<style>` 標籤中的 inline CSS

### Step U2：抓取 CSS 檔案

- 對每個 CSS URL 執行 `curl -sL`
- 合併為單一 CSS 文本（保留來源註解）
- 附加 inline CSS

### Step U3：解析 CSS

從合併的 CSS 文本中提取：

1. **CSS Custom Properties**：`:root { --* }` 宣告
   - 分類：色彩變數（含 color/bg 關鍵詞）、字體變數、間距變數、其他
2. **@font-face 宣告**：font-family 名稱和來源
3. **Media query 斷點**：`@media (min-width: ...)` 和 `(max-width: ...)`
4. **Class 級別樣式**：
   - 按鈕類（`.btn-*`、`.button-*`、`.el-button`）
   - 輸入框類（`.input-*`、`.el-input`）
   - 卡片類（`.card-*`、`.el-card`）

### Step U4：頻率統計

1. 統計 HTML 中各 class 的使用頻率
2. 統計 CSS 中各色碼的出現頻率
3. 從頻率推斷 primary/secondary 角色：
   - 按鈕背景色最高頻 → primary
   - 第二高頻 → secondary
   - `.error`/`.danger` 類使用 → error
   - `.success` 類使用 → success

### Step U5：組裝 DESIGN.md

- 同 Step 8（本地靜態）格式
- 在檔案頭標注：
  ```
  > 擷取方式：URL 靜態分析（curl + CSS 解析）
  > ⚠️ 靜態分析限制：SPA 渲染內容、CSS-in-JS、動態主題可能遺漏
  ```
- 信心度整體降低 15-20%（因為無法取得 JS 渲染結果）
- 建議標注：「如需更完整的擷取，建議使用 Chrome MCP 版」

### URL 靜態分析限制與降級

| 場景 | 行為 |
|------|------|
| SPA 網站（Vue/React 渲染） | 只能擷取 CSS 層定義，元件呈現可能不同。標注警告 |
| CDN CSS（如 Element Plus 預設） | 可擷取，但無法區分客製覆寫 vs 預設值 |
| 需要登入的頁面 | curl 無法取得內容 → 報錯，建議使用 Chrome MCP 版 |
| CSS-in-JS（styled-components） | 靜態分析無法擷取 → 標注需要 Chrome MCP 版 |

---

## Chrome MCP 擷取流程

> 本章節定義 `/ct-fieldguide design [url]` 的 Chrome MCP 擷取流程。
> 獨立於靜態擷取路徑（Step 0.5-9），但可與靜態結果合併（混合模式）。

### 流程架構

```
/ct-fieldguide design [input]
├─ 偵測輸入類型
│   ├─ 本地路徑 → 靜態擷取（Step 0.5-9）
│   ├─ URL 參數 → Chrome MCP 模式（Step C1-C5）
│   └─ 路徑 + URL → 混合模式（靜態 Step 1-9 + Chrome Step 3.5/4.5）
│
├─ Chrome MCP 模式流程
│   ├─ Step C1：導航 + 登入 + 等待 SPA 載入
│   ├─ Step C2：注入擷取腳本（3 個合併腳本）
│   │   ├─ Script 1：Theme（CSS vars + computed colors + font vars）
│   │   ├─ Script 2：Layout + Typography（佈局骨架 + heading + table/form 排版）
│   │   └─ Script 3：Components（按鈕 + 卡片 + 輸入框 + menu + tag）
│   ├─ Step C3：多頁面巡覽（可選）
│   │   ├─ 點擊 sidebar 第一個子頁面（取 table/form 樣式）
│   │   └─ 返回首頁
│   ├─ Step C4：組裝 DESIGN.md（合併各腳本結果）
│   └─ Step C5：寫入 + 收尾
│
└─ 混合模式
    ├─ 有原始碼 + URL → 靜態為主，Chrome 驗證 + 補充佈局/排版
    └─ 只有 URL → Chrome MCP 為主
```

### 擷取腳本合併策略

為減少 Chrome MCP 互動次數（每次 `javascript_tool` 呼叫消耗 context），將擷取合併為 **3 個腳本**：

| 腳本 | 擷取內容 | 預估 output size |
|------|---------|-----------------|
| Script 1：Theme | CSS vars, computed colors, font vars | ~3KB JSON |
| Script 2：Layout + Typography | 佈局骨架, heading, table/form 排版 | ~2KB JSON |
| Script 3：Components | 按鈕, 卡片, 輸入框, menu, tag | ~2KB JSON |

### Script 1：Theme 擷取

```javascript
// === Script 1: Theme ===
// 收集 CSS custom properties + computed color values
const result = { cssVars: {}, computedColors: {}, fontVars: {} };

// 收集 :root CSS custom properties
const rootStyles = getComputedStyle(document.documentElement);
const sheet = [...document.styleSheets].find(s => {
  try { return [...s.cssRules].some(r => r.selectorText === ':root'); } catch { return false; }
});
if (sheet) {
  [...sheet.cssRules]
    .filter(r => r.selectorText === ':root')
    .forEach(r => {
      for (const prop of r.style) {
        if (prop.startsWith('--')) {
          result.cssVars[prop] = rootStyles.getPropertyValue(prop).trim();
        }
      }
    });
}

// 分類色彩和字體變數
for (const [k, v] of Object.entries(result.cssVars)) {
  if (k.includes('color') || k.includes('bg') || k.includes('fill') || k.includes('border')) {
    result.computedColors[k] = v;
  }
  if (k.includes('font') || k.includes('text') || k.includes('size')) {
    result.fontVars[k] = v;
  }
}

// 取得 body computed 基礎樣式
const bodyS = getComputedStyle(document.body);
result.bodyDefaults = {
  fontFamily: bodyS.fontFamily,
  fontSize: bodyS.fontSize,
  color: bodyS.color,
  backgroundColor: bodyS.backgroundColor
};

JSON.stringify(result, null, 2);
```

### Script 2：Layout + Typography 擷取

```javascript
// === Script 2: Layout + Typography ===
const result = { layout: {}, headings: {}, tableTypo: {}, formTypo: {} };

// --- Layout: Page Skeleton ---
const regions = ['header', 'sidebar', 'footer', 'main'];
const selectors = {
  header: '.el-header, header, [class*="header"], [class*="navbar"]',
  sidebar: '.el-aside, aside, [class*="sidebar"], [class*="side-menu"]',
  footer: '.el-footer, footer, [class*="footer"]',
  main: '.el-main, main, [class*="main-content"], [class*="app-main"]'
};

for (const region of regions) {
  const el = document.querySelector(selectors[region]);
  if (el) {
    const s = getComputedStyle(el);
    result.layout[region] = {
      exists: true, width: s.width, height: s.height,
      position: s.position, backgroundColor: s.backgroundColor
    };
  }
}

// --- Layout: Container patterns ---
const containers = document.querySelectorAll('.el-container');
result.layout.containers = [...containers].slice(0, 5).map(c => {
  const s = getComputedStyle(c);
  return { display: s.display, flexDirection: s.flexDirection, children: c.children.length };
});

// --- Layout: Navigation ---
const navMenus = document.querySelectorAll('.el-menu');
result.layout.navigation = [...navMenus].map((menu, i) => {
  const isVertical = menu.classList.contains('el-menu--vertical');
  return {
    direction: isVertical ? 'vertical' : 'horizontal',
    topItems: menu.querySelectorAll(':scope > .el-menu-item, :scope > .el-sub-menu').length,
    hasSubMenus: menu.querySelectorAll('.el-sub-menu').length > 0
  };
});
result.layout.breadcrumb = !!document.querySelector('.el-breadcrumb');
result.layout.tabs = !!document.querySelector('.el-tabs');

// --- Typography: Headings ---
['h1','h2','h3','h4','h5','h6'].forEach(tag => {
  const el = document.querySelector(tag);
  if (el) {
    const s = getComputedStyle(el);
    result.headings[tag] = {
      fontSize: s.fontSize, fontWeight: s.fontWeight,
      lineHeight: s.lineHeight, marginTop: s.marginTop,
      marginBottom: s.marginBottom, color: s.color
    };
  }
});

// --- Typography: Table ---
const thCell = document.querySelector('.el-table__header-wrapper th .cell');
if (thCell) {
  const s = getComputedStyle(thCell);
  const th = getComputedStyle(thCell.closest('th'));
  result.tableTypo.header = {
    fontSize: s.fontSize, fontWeight: s.fontWeight,
    height: th.height, backgroundColor: th.backgroundColor
  };
}
const tdCell = document.querySelector('.el-table__body-wrapper td .cell');
if (tdCell) {
  const s = getComputedStyle(tdCell);
  const td = getComputedStyle(tdCell.closest('td'));
  result.tableTypo.body = {
    fontSize: s.fontSize, fontWeight: s.fontWeight,
    height: td.height, backgroundColor: td.backgroundColor
  };
}

// --- Typography: Form ---
const label = document.querySelector('.el-form-item__label');
if (label) {
  const s = getComputedStyle(label);
  result.formTypo.label = { fontSize: s.fontSize, fontWeight: s.fontWeight, color: s.color };
}
const input = document.querySelector('.el-input__inner');
if (input) {
  const s = getComputedStyle(input);
  result.formTypo.input = { fontSize: s.fontSize, height: s.height, color: s.color };
}

JSON.stringify(result, null, 2);
```

### Script 3：Components 擷取

```javascript
// === Script 3: Components ===
const result = { button: {}, card: {}, input: {}, menu: {}, tag: {} };

// --- Button ---
const btn = document.querySelector('.el-button--primary');
if (btn) {
  const s = getComputedStyle(btn);
  result.button.primary = {
    backgroundColor: s.backgroundColor, color: s.color,
    borderRadius: s.borderRadius, fontSize: s.fontSize,
    height: s.height, padding: s.padding
  };
}
const btnDefault = document.querySelector('.el-button--default');
if (btnDefault) {
  const s = getComputedStyle(btnDefault);
  result.button.default = {
    backgroundColor: s.backgroundColor, color: s.color,
    borderColor: s.borderColor, borderRadius: s.borderRadius
  };
}

// --- Card ---
const card = document.querySelector('.el-card');
if (card) {
  const s = getComputedStyle(card);
  result.card = {
    backgroundColor: s.backgroundColor, borderRadius: s.borderRadius,
    boxShadow: s.boxShadow, padding: s.padding
  };
}

// --- Input ---
const inputEl = document.querySelector('.el-input__wrapper');
if (inputEl) {
  const s = getComputedStyle(inputEl);
  result.input = {
    backgroundColor: s.backgroundColor, borderRadius: s.borderRadius,
    boxShadow: s.boxShadow, height: s.height
  };
}

// --- Menu Item ---
const menuItem = document.querySelector('.el-menu-item');
if (menuItem) {
  const s = getComputedStyle(menuItem);
  result.menu.item = {
    height: s.height, fontSize: s.fontSize,
    color: s.color, backgroundColor: s.backgroundColor
  };
}
const activeItem = document.querySelector('.el-menu-item.is-active');
if (activeItem) {
  const s = getComputedStyle(activeItem);
  result.menu.activeItem = {
    color: s.color, backgroundColor: s.backgroundColor
  };
}

// --- Tag ---
const tag = document.querySelector('.el-tag');
if (tag) {
  const s = getComputedStyle(tag);
  result.tag = {
    backgroundColor: s.backgroundColor, color: s.color,
    borderRadius: s.borderRadius, fontSize: s.fontSize, height: s.height
  };
}

JSON.stringify(result, null, 2);
```

### 多頁面巡覽策略

首頁通常缺少表格和表單元素。建議巡覽策略：

1. **首頁擷取**：Theme + Layout + Components（基礎樣式）
2. **自動導航至列表頁**：點擊 sidebar 第一個有子選單的項目 → 進入列表頁
3. **列表頁擷取**：Table + Form typography（Script 2 的表格/表單部分）
4. **觸發 Dialog/Drawer**（若偵測到觸發按鈕）：取得 modal 樣式

```javascript
// 導航至第一個子頁面（在首頁擷取完成後執行）
const firstSubMenu = document.querySelector('.el-sub-menu');
if (firstSubMenu) {
  // 展開子選單
  const title = firstSubMenu.querySelector('.el-sub-menu__title');
  if (title) title.click();
  // 等待展開動畫
  await new Promise(r => setTimeout(r, 500));
  // 點擊第一個子項目
  const firstItem = firstSubMenu.querySelector('.el-menu-item');
  if (firstItem) firstItem.click();
}
```

### SPA 等待策略

```javascript
// Element Plus SPA 載入完成判斷
const waitForSPAReady = () => new Promise((resolve, reject) => {
  let attempts = 0;
  const maxAttempts = 20; // 最多等待 10 秒
  const check = () => {
    attempts++;
    const hasMenu = document.querySelector('.el-menu');
    const hasContainer = document.querySelector('.el-container');
    const hasContent = document.querySelector('.el-main, [class*="app-main"]');
    if ((hasMenu || hasContainer) && hasContent) {
      resolve({ ready: true, attempts });
    } else if (attempts >= maxAttempts) {
      resolve({ ready: false, attempts, fallback: 'timeout' });
    } else {
      setTimeout(check, 500);
    }
  };
  check();
});
```

### 登入流程處理

| 情境 | 偵測方式 | 處理策略 |
|------|---------|---------|
| SSO 登入 | URL 重導至 SSO 頁面（含 `oauth`/`authorize`/`sso`） | 提示使用者手動完成登入，等待重導回目標頁面 |
| 直接登入 | 頁面含 `.el-form` + password input | 提示使用者手動輸入帳號密碼，等待頁面載入 |
| 無需登入 | 頁面直接顯示 `.el-container` / `.el-menu` | 直接開始擷取 |

```javascript
// 偵測登入狀態
const detectLoginState = () => {
  const url = window.location.href;
  const hasSSO = /oauth|authorize|sso|login|signin/i.test(url);
  const hasLoginForm = document.querySelector('input[type="password"]');
  const hasApp = document.querySelector('.el-container, .el-menu');

  if (hasApp && !hasSSO) return { state: 'logged_in' };
  if (hasSSO) return { state: 'sso_redirect', url };
  if (hasLoginForm) return { state: 'login_form' };
  return { state: 'unknown' };
};
```

### 降級行為

| 情境 | 降級策略 |
|------|---------|
| Chrome MCP 擴充套件未連接 | 回報錯誤，建議使用靜態模式（僅限有原始碼） |
| Chrome MCP 連接但頁面載入失敗 | 重試 1 次，仍失敗則終止並回報 |
| 登入頁面無法通過 | 提示使用者手動登入，提供等待重試選項 |
| SPA 等待逾時 | 以當前 DOM 狀態擷取（部分結果），標注信心度為低 |
| 無表格/表單頁面 | 跳過 Step 3.5 的表格/表單部分，僅擷取 heading 和佈局 |
| 混合模式中 Chrome MCP 失敗 | 降級為純靜態模式，DESIGN.md 中 Chrome MCP 子章節留空 |
