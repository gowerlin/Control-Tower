# 程式碼掃描策略

> 本文件定義 `/ct-fieldguide` 掃描程式碼時的策略和模式。
> 供 init、extract、audit 子命令參考。

## 技術棧偵測

### 偵測方式

按優先級檢查以下檔案，確定專案技術棧：

| 偵測檔案 | 技術棧 | 掃描焦點 |
|----------|--------|---------|
| `package.json` | JavaScript/TypeScript 前端 | 依 dependencies 判斷框架 |
| `*.csproj` / `*.sln` | .NET | Web API / Razor / Blazor |
| `requirements.txt` / `pyproject.toml` | Python | Django / FastAPI / Flask |
| `go.mod` | Go | 標準庫 vs 框架 |
| `Cargo.toml` | Rust | — |
| `pom.xml` / `build.gradle` | Java/Kotlin | Spring Boot / Android |

### 前端框架細分

從 `package.json` 的 `dependencies` 進一步判斷：

| 依賴 | 框架 | UI 庫 | 掃描重點 |
|------|------|-------|---------|
| `vue` | Vue 2/3 | — | 元件模式、Composition API vs Options API |
| `element-plus` / `element-ui` | — | Element | 表格/表單/彈窗元件用法 |
| `ant-design-vue` | — | Ant Design | 表格/表單/佈局元件用法 |
| `react` | React | — | Hook 模式、狀態管理 |
| `next` | Next.js | — | 路由模式、SSR 策略 |
| `@angular/core` | Angular | — | 模組/服務/元件架構 |

### 後端框架細分

| 框架 | 掃描重點 |
|------|---------|
| ASP.NET Core | Controller 模式、DI、Middleware |
| Django | View/Template 模式、ORM 用法 |
| FastAPI | Router 模式、Pydantic 用法 |
| Express/Fastify | Middleware 模式、路由組織 |
| Spring Boot | Bean/Service/Repository 模式 |

---

## 核心目錄掃描

### 掃描範圍決策

根據技術棧決定掃描的核心目錄：

**Vue/React 前端專案**：
```
src/
├ components/    ← 封裝元件（重點掃描）
├ views/         ← 頁面元件（代表頁面選擇來源）
├ composables/   ← 組合式函數（Vue 3）
│ hooks/         ← Hook（React）
├ utils/         ← 工具函數
├ api/           ← API 呼叫層
├ stores/        ← 狀態管理
└ router/        ← 路由設定
```

**.NET 後端專案**：
```
src/
├ Controllers/   ← API 端點（重點掃描）
├ Services/      ← 業務邏輯
├ Models/        ← 資料模型
├ Repositories/  ← 資料存取
├ Middleware/     ← 中介軟體
└ Configurations/ ← 設定
```

**Python 後端專案**：
```
app/ 或 src/
├ routes/ 或 views/  ← 端點定義
├ services/          ← 業務邏輯
├ models/            ← 資料模型
├ schemas/           ← 請求/回應結構
└ utils/             ← 工具函數
```

### 掃描深度

- **封裝元件目錄**：全部讀取，識別 props 介面和使用模式
- **頁面/View 目錄**：選 3-5 個代表頁面深入分析
- **API/Service 層**：掃描檔案結構和命名慣例，選 2-3 個深入
- **工具/設定**：概覽結構，不深入

---

## 代表頁面選擇

### 選擇標準

從頁面/View 目錄中選出 3-5 個代表頁面，標準：

1. **功能覆蓋**：涵蓋 CRUD 列表、表單、詳情等主要頁面類型
2. **複雜度梯度**：包含簡單和複雜頁面
3. **近期活躍**：優先選擇最近修改的頁面（`git log` 或修改時間）
4. **元件多樣性**：使用不同 UI 元件的頁面

### 選擇流程

1. 列出所有頁面/View 檔案
2. 按功能分類（列表頁、表單頁、詳情頁、儀表板等）
3. 每類選 1-2 個代表
4. 優先選：
   - 使用封裝元件的頁面（展示元件使用慣例）
   - 含表格的頁面（展示資料展示模式）
   - 含表單的頁面（展示表單驗證模式）
   - 含彈窗/抽屜的頁面（展示容器選擇慣例）

### 範例選擇結果

```
代表頁面（Vue 3 + Element Plus 專案）：
1. src/views/member/MemberList.vue       — 標準 CRUD 列表（表格 + 搜尋 + Drawer）
2. src/views/order/OrderCreate.vue       — 複雜表單（多步驟 + 驗證）
3. src/views/dashboard/Dashboard.vue     — 儀表板（圖表 + 卡片佈局）
4. src/views/system/RoleManagement.vue   — 權限管理（樹狀結構 + Dialog）
5. src/views/report/SalesReport.vue      — 報表頁（日期範圍 + 匯出）
```

---

## 慣例識別模式

### 掃描時要識別的慣例類型

| 類型 | 掃描方式 | L2 對應 |
|------|---------|---------|
| 元件使用慣例 | Grep 搜尋 `<El*`、`<Base*`、`<App*` 等前綴 | 元件選擇決策樹 |
| 容器選擇 | Grep 搜尋 Dialog/Drawer/Modal 使用 | 彈出容器決策樹 |
| 錯誤處理 | Grep 搜尋 try/catch、ElMessage、notification | 錯誤處理決策樹 |
| 表單驗證 | Grep 搜尋 rules、validator、validate | 表單驗證決策樹 |
| API 呼叫 | Grep 搜尋 axios、fetch、api 目錄 | API 設計決策樹 |
| 狀態管理 | Grep 搜尋 store、useState、useStore | 狀態管理決策樹 |
| 路由模式 | 讀取 router 設定檔 | 導航決策樹 |
| 命名慣例 | 統計檔名和變數命名風格 | 命名規範 |

### 具體 Grep 模式

**元件使用**：
```bash
# Vue 封裝元件
Grep: pattern="<Base[A-Z]" glob="*.vue"
Grep: pattern="<App[A-Z]" glob="*.vue"

# Element Plus 元件
Grep: pattern="<El[A-Z]" glob="*.vue"

# React 封裝元件
Grep: pattern="import.*from.*components/" glob="*.tsx"
```

**錯誤處理**：
```bash
# 前端
Grep: pattern="ElMessage\.(error|warning|success|info)" glob="*.vue"
Grep: pattern="ElNotification" glob="*.vue"
Grep: pattern="catch\s*\(" glob="*.{vue,ts,js}"

# 後端
Grep: pattern="throw new" glob="*.cs"
Grep: pattern="raise " glob="*.py"
```

**表單驗證**：
```bash
Grep: pattern=":rules=" glob="*.vue"
Grep: pattern="validator:" glob="*.{vue,ts,js}"
Grep: pattern="\[Required\]" glob="*.cs"
```

### 頻率統計

對每種慣例，統計使用頻率來判斷「主流做法」vs「例外做法」：

```
搜尋結果：
  ElDialog: 15 處
  ElDrawer: 8 處
  BaseDrawer: 6 處（全部在 Drawer 場景中）
  ElMessageBox: 12 處

分析：
  → Dialog 系使用頻率高於 Drawer 系
  → Drawer 場景已統一使用 BaseDrawer 封裝
  → MessageBox 主要用於確認操作
```

---

## 萃取順序

### 建議的萃取步驟（init 流程）

1. **技術棧偵測**：確定框架和 UI 庫
2. **目錄結構掃描**：了解專案組織方式
3. **封裝元件盤點**：識別專案封裝了哪些元件
4. **代表頁面深入分析**：逐一分析 3-5 個代表頁面
5. **慣例頻率統計**：對關鍵慣例做 Grep 頻率統計
6. **先寫 L2**：從實際做法歸納決策分支
7. **再抽象 L1**：從 L2 反推通用原則
8. **最後填 L3**：從掃描結果填入具體路徑和做法

### 為什麼 L2 先於 L1？

- L1 是從 L2 抽象出來的，直接寫 L1 容易空泛
- L2 有具體的 if-then 分支可驗證
- 先有具體再抽象，品質更高

---

## audit 模式的掃描策略

### 一般 audit

1. 讀取 FIELDGUIDE.md 的所有 L3 章節
2. 提取所有檔案路徑
3. 用 `Glob` 驗證路徑是否存在
4. 對仍存在的路徑，讀取對應程式碼，比對 L3 描述是否一致
5. 對掃描範圍，搜尋 FIELDGUIDE 未覆蓋的新慣例

### debt 模式

1. 根據工單指定的主題，確定搜尋模式（如「錯誤處理」→ 搜尋 catch/Message/Notification）
2. 收集所有符合的程式碼片段
3. 按模組分組
4. 識別不同做法並統計頻率
5. 產出技術債報告
