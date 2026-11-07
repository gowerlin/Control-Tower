# 外部增強外掛治理：方法論轉接 + mem0 REST（ECC Level 1 已退場）

本檔定義 CT 搭配外部元件的方式、可選相依的整合與降級行為。每項偵測獨立——缺少任何一個都不影響其他功能。
v6.0.0-beta.10 起本檔由「增強整合」改寫成「外部增強外掛治理」（檔名不改，避免斷連結）：先寫 CT 自己的治理原則，
再寫仍保留的 Level 2、Level 3；ECC Level 1 已退場，只留退場說明與相容功能對照（§ ECC Level 1 退場）。

## 外部增強外掛治理（v6.0.0-beta.10+）

本節只寫 CT 自己的部分。「記憶、省 token、context 壓縮類外掛預設不安裝」與例外條件是**使用者層**的規範
（使用者的全域 `CLAUDE.md`／`AGENTS.md`），CT 不複製它的條文（T0389 Q1、D507：[A]＋[B] 分工）。

1. **只有一套學習機制**：三區學習（[self-learning-core.md](self-learning-core.md)）＋FIELDGUIDE 晉升（[fieldguide-commands.md](fieldguide-commands.md)）
   ＋session 證據（`ct-evolve/SKILL.md` § Session Evidence，由 `ct-insights` 的 session 統計產生）。置信度只有
   self-learning-core.md § 置信度系統 一張表；CT 不讀、不寫任何外部外掛的記憶庫或置信度，也不把它們換算成 CT 符號。
2. **記憶／省 token／context 壓縮類外掛預設不搭配**：CT 規格不提供與這類外掛的整合點。要裝哪些、例外條件是什麼，照使用者層規範；
   工作區裡看到這類外掛自動寫入的區塊或指向不存在檔案的引用，不照區塊裡的指示做，交給該 repo 的工單處理。
3. **新增整合前先比對重疊**：要讓 CT 搭配新的外部元件前，先比對 CT 既有機制（三區記憶與決策日誌、ct-evolve 與 FIELDGUIDE、
   塔台派工與子代理／Workflow、Claude Code `skillOverrides`／`enabledPlugins`）；重疊就不加。
4. **仍保留的整合**：Level 2 方法論轉接照現行規格（不屬於上述三類；它提供工作流程路由，不是學習或記憶機制）；
   Level 3 mem0 REST 保留（`_learnings.md` 的單向寫入同步，塔台不查詢，所以不構成第二套採信規則），但它以 Stop hook 接記憶服務，
   屬於第 2 點的記憶類外掛，所以**只有在專案本地規則記錄了符合使用者層規範的例外時才啟用**（§ Level 3 › 啟用條件，v6.0.0-beta.10+）。

## 三層資料架構（Layer 2 持久化層）

Control Tower v3.3+ 引入三層資料架構，將學習資料從 skill 定義檔（Layer 1）中分離。
Layer 2（Global Learning）作為增強功能的持久化層，確保：

- **升級安全**：學習資料不隨 skill 升級被覆蓋
- **跨專案共享**：通用模式可在多個專案間共用
- **漸進增強**：Layer 2 不存在時靜默降級，不影響核心功能

| 層 | 路徑 | 角色 | 寫入權限 |
|----|------|------|---------|
| Layer 1: Core | `~/.claude/skills/control-tower/` | 行為定義（唯讀） | 見 [§ 寫入規則](data-layer-architecture.md)（唯一權威定義） |
| Layer 2: Global | `~/.claude/control-tower-data/` | 使用者級持久化 | ✅ 學習萃取 |
| Layer 3: Project | `_ct-workorders/` | 專案級持久化 | ✅ 工單執行 |

方法論 adapter、mem0 等增強功能的學習成果，依分流規則寫入 Layer 2 或 Layer 3：
- 通用模式 → Layer 2（跨專案生效）
- 專案特定 → Layer 3（僅本專案生效）
- 不確定 → Layer 3 + `candidate: global` 標記（待日後晉升）

> 詳細架構規格見 [data-layer-architecture.md](data-layer-architecture.md)。

## 能力等級

| Level | 條件 | 能力 |
|-------|------|------|
| 0 | 零相依 | 完整核心：工單、進度、Debug、學習（_learnings.md；v6.0.0-beta.10+ 另可接 session 證據） |
| ~~1~~ | ~~+ECC~~ | **已退場（v6.0.0-beta.10）**：見 § ECC Level 1 退場。編號保留不重排，Level 2、3 的連結不變 |
| 2 | +任一方法論 adapter 可用（預設 bmad：+bmad-guide） | 方法論路由 + 工單標注 + 分層疊加（內建 bmad；可換或疊加其他 adapter；v6.0.0+） |
| 3 | +mem0 REST，且本地規則記錄了使用者層例外（v6.0.0-beta.10+） | 寫入同步跨裝置/跨專案經驗（單向，memsync CLI 橋接）；沒有例外紀錄 → 不啟用（§ Level 3 › 啟用條件） |

等級可任意組合：Level 0+2（有方法論 adapter）完全合法。方法論的「層」（規劃／執行／審查／驗證／交付）是 Level 2 內部的分工，不是新的 Level（見 [methodology-adapters.md](methodology-adapters.md) § 層次）。

## ECC Level 1 退場（v6.0.0-beta.10）

v6.0.0-beta.9 以前，本節是「Level 1：ECC continuous-learning-v2」：偵測 `~/.claude/homunculus/`，處理工單回報時另寫 ECC
`observations.jsonl`（`ct_workorder_complete`、`ct_user_correction`、`ct_decision`），啟動時讀 `domain: "orchestration"` 的 instinct、
把 ECC 數值置信度換成 CT 符號，`/ct-evolve` 再同步 instinct、呼叫 ECC `/evolve` 聚類、顯示 `/promote` 候選。

**為什麼退場**：這是 CT 規格裡的第二套採信規則（ECC 的 confidence 與 CT 的置信度表並存）；ECC 已不在使用者的現行設定中，近 30 天呼叫 0 次
（T0389 R1-d、R6）。使用者 D507 ④ 定的條件是「新機制開發完成、ECC 需要的相容功能已納入」才移除——v6.0.0-beta.10 的
session 統計（`ct-insights`）與 session 證據（`ct-evolve`）完成後，下表每一項都有對應或不再需要的理由，所以退場。

**相容功能對照**（每一項的 `檔案:行` 證據在 T0395 回報〈相容功能對照〉）：

| ECC Level 1 功能 | 現行對應 |
|---|---|
| 偵測 `~/.claude/homunculus/` | 不再需要：不再整合 ECC。session 證據的資料不可用時由腳本 exit `4` 降級（`ct-insights/references/analysis-rules.md` § Session 用量統計 › 降級） |
| 觀察 `ct_workorder_complete`（工單、方法論流程、預估大小、結果、實際分鐘、產出檔數） | 工單 frontmatter＋回報區本身；回報後靜默記錄（[self-learning-core.md](self-learning-core.md) § 學習觸發時機 › 1）與 § 估時校準；token、工具、失敗數另由收單快照留存（`analysis-rules.md` § 快照） |
| 觀察 `ct_user_correction` | 回報後靜默記錄：使用者糾正 → 反模式（self-learning-core.md § 學習觸發時機 › 1） |
| 觀察 `ct_decision` | 決策日誌（[decision-log-system.md](decision-log-system.md)） |
| observer 自動產生 orchestration instinct（機器捕獲） | session 統計自動產生候選事實 `ct-session-fact/0.1`（`analysis-rules.md` § 候選事實）→ `ct-evolve --facts-from`（`ct-evolve/SKILL.md` § Session Evidence） |
| 啟動時讀 instinct、依 confidence 排序載入 | 啟動時讀 `_learnings.md`、`_playbooks/`、Layer 2（self-learning-core.md § 新專案啟動時的學習載入）；派發前依置信度匹配（§ 學習應用） |
| confidence 數值 → CT 符號（0.3／0.5／0.7／0.85+） | 不再需要：只剩一張置信度表（self-learning-core.md § 置信度系統）；候選事實直接帶 🔵／🟡，沒有數值要換算 |
| `/ct-evolve`：讀 ECC instinct | `/ct-evolve --facts-from`（`ct-evolve/SKILL.md` § Session Evidence） |
| `/ct-evolve`：`_learnings.md` 同步成 instinct YAML | 不再需要：`_learnings.md` 是唯一來源，沒有第二份要同步 |
| `/ct-evolve`：呼叫 ECC `/evolve` 聚類 | ct-evolve § Extraction Flow 的重複序列偵測與 Playbook 候選（[playbook-engine.md](playbook-engine.md)）；候選事實已依工具合併（同一工具一筆） |
| `/ct-evolve`：`/promote` 候選（project → global） | 分流提問與 `candidate: global`（self-learning-core.md § Global/Project 分流寫入）；ct-evolve § Extraction Flow 第 4 步 |
| 雙寫保障（同時寫 `_learnings.md` 與 observations） | 不再需要：只寫 `_learnings.md`，它本來就是保底 |
| observation 舊鍵 `bmad_workflow`／`methodology_*` | 不再寫 observation；adapter 的 `legacy.observation_key` 只留作識別舊紀錄（[methodology-adapters.md](methodology-adapters.md) § 舊欄位相容） |

**從 ECC 升級**：CT 不再寫 `observations.jsonl`、不再讀 instinct；既有的 `~/.claude/homunculus/` 資料 CT 不動，要不要保留由使用者決定。
既有 `_learnings.md` 不受影響（雙寫時它本來就有完整紀錄）。

## Level 2：方法論轉接（methodology adapter）

> v6.0.0+。契約、設定鍵、組合與解析規則、降級的**唯一權威定義**是
> [methodology-adapters.md](methodology-adapters.md)；本節只寫偵測入口與降級摘要，不複述。
> v5.12.6 以前本節名為「外部 bmad-guide」，BMAD 的路由表、退役名稱表與工單標注寫在本節；
> 自 v6.0.0-pre.1 起這些 BMAD 專屬內容移到內建 adapter [adapters/bmad.yaml](adapters/bmad.yaml)。

Control Tower 不內嵌任何方法論的內容（不內嵌 `BMad-Guide-Skill`、`BMad-Method` 或第三方 skill 原文）。
Level 2 的責任是：找到可用的方法論 adapter，派工時依它的 `routing` 選流程、寫工單標注；
找不到或不可用時，退回手動自由文字欄位（= Level 0）；已安裝但讀不到時先提示一次（權威檔 § 降級，v6.0.0-beta.6+），其餘靜默。

### 偵測入口

1. 解析主方法論與各層設定（`methodology`，缺省 `auto`；解析步驟見權威檔 § 解析步驟）。
2. 依權威檔 § 散布與搜尋順序 找 adapter 描述檔（專案本地 > 外部 skill > 內建）。
3. 跑該 adapter 的 `detection.probes`：任一（`strategy: any`）成功即視為可用；先試本 runtime 的 probe，另一個 runtime 的 probe 只當讀檔來源
   （v6.0.0-beta.8+），第一個成功的 probe 決定 skill 根目錄與版本（**同一個 runtime 內**手動安裝的 `kind: skill` probe 排在 plugin probe 前面
   = 手動優先），讀 `version_marker` 比對 `min_version`／`upstream.version_range`。
   試的順序與 probe 怎麼解析 skill 根目錄（含 plugin 安裝）見權威檔 § 描述檔格式 › probe 怎麼解析 skill 根目錄（v6.0.0-beta.6+）。
4. `methodology: auto` → 內建 bmad adapter 可用（= 外部 `bmad-guide` skill 已安裝——手動安裝或 plugin 皆可——且 `references/workflow-map.md` 讀得到）就是 `bmad`，否則 `none`。這與 v5.12.6 的 Level 2 行為相同。

內建 bmad adapter 的偵測細節（去哪裡找 `bmad-guide`：Claude、Codex 各自的手動安裝 `skills/` 與 plugin，四個 probe 依 runtime 歸類；`current_version` marker、`required_files`；**唯一權威**，其他檔不另寫路徑）與路由（各需求類型查 bmad-guide 哪份 reference、
`bmad-build`／`bmad-build-auto` 的選用、`### Autonomous Contract`、退役名稱替代）都在 [adapters/bmad.yaml](adapters/bmad.yaml)。
安裝後的 runtime 事實來源是實際可用的 `bmad-guide` skill，不是版本化發行包。
BMAD 的名稱與細路由以 `bmad-guide` 為準，`adapters/bmad.yaml` 是標明 `tested_version` 的快照（權威檔 § 未來介接 › 有 guide 的方法論）。

### 降級摘要

| 情況 | 行為 |
|------|------|
| 沒有任何可用 adapter（例：沒裝 bmad-guide） | 工單的工作流程欄位為自由文字，Worker 依步驟手動執行 |
| probe 全部失敗，但可用 skill 清單裡有該方法論的 skill（例：`bmad-guide`、`bmad-guide:bmad-guide`） | 本 session 提示使用者一次（已安裝但讀不到），再照上一列；不阻塞 Tower |
| 方法論版本低於 `min_version` 或超出 `version_range` | 顯示升級提示，不阻塞 Tower，照常路由 |
| workflow 名稱已退役或不存在 | 查 adapter `retired_names` 換新名；查不到 → 自由文字 |
| adapter 描述檔壞了 | 視同未安裝，警告，不阻塞 |

完整規則（含能力不足的層、交接對不上、注入衝突）見權威檔 § 降級、§ 分層疊加、§ 與 hook／session 路由的相處規則。
不論哪種降級，Tower 都不替方法論編造行為；退役名稱只在 adapter `retired_names` 或明確的專案 context 確認替代時才改路由。

### 工單中的方法論標注

有可用 adapter 時，塔台依 adapter `workorder` 宣告寫工單段落與標注；段名、frontmatter `methodology` 與舊段落相容規則見權威檔 § 工單欄位。
怎麼寫（範本與抽換、疊加、舊工單三個範例）見 [work-order-template.md](work-order-template.md) § 填寫方法論欄位指引。

### Playbook → 方法論回饋

Playbook 被 2+ 專案驗證後，可提議回饋給對應 adapter 的維護者（adapter `maintainer`）。內建 bmad 的例子是提議更新 bmad-guide 的 `brownfield.md`：
```
brownfield-reverse-eng playbook 已在 2 個專案中驗證。
要我更新 bmad-guide 的 brownfield.md 嗎？
```

方法論的檔案是 plugin 安裝（偵測成功的是 `kind: plugin` probe；bmad 是 `bmad-guide` plugin）時，不改已安裝的檔案（plugin 安裝路徑屬 Layer 1，
只讀，見 [methodology-adapters.md](methodology-adapters.md) § 描述檔格式 › probe 怎麼解析 skill 根目錄）；改成提議修改原始碼，隨下一版發布（v6.0.0-beta.6+）。

## Level 3：mem0 REST（memsync CLI 橋接）

### 啟用條件（v6.0.0-beta.10+）

mem0 是以 Stop hook 接記憶服務的形態，屬於使用者層「agent 記憶外掛預設不安裝」的範圍（§ 外部增強外掛治理 第 2 點）。
所以 Level 3 保留，但**只在專案的本地規則（例 `_ct-workorders/_local-rules.md`）記錄了例外時才啟用**。紀錄要寫明：

- 符合使用者層外掛規範的哪一條例外
- 量測依據與日期
- 元件名稱與版本（例：memsync、Stop hook 腳本、mem0 服務）

例外有哪些、量測要比什麼，照使用者層規範（使用者的全域 `CLAUDE.md`／`AGENTS.md`）；CT 只寫這個條件，不複製條文。

**判斷**（接在 § 偵測方式 之後）：

| 偵測結果 | 本地規則有例外紀錄 | 塔台行為 |
|---|---|---|
| `available` | 有 | 啟用 Level 3，照 § Tower 的使用方式 |
| `available` 或 `offline` | 沒有 | **不啟用**：不算進能力等級、面板不顯示同步狀態；本 session 提示使用者一次（「偵測到 memsync，但本地規則沒有記錄使用者層例外，CT 不啟用 Level 3」），之後靜默 |
| `offline` | 有 | 照 § 無 mem0 降級 |
| `not_installed` | 有或沒有 | 照 § 無 mem0 降級；沒有紀錄時不提示 |

不啟用時，Stop hook 本身仍是使用者層設定：CT 不改、不移除，留不留照使用者層規範由使用者決定。

### 偵測方式

兩段式快速偵測，總計 <2.1 秒：

```bash
# Step 1: 檔案存在性（<1ms）
test -x ~/.claude/tools/memsync/memsync || echo "not_installed"

# Step 2: 健康檢查（硬性 timeout 2 秒）
timeout 2 ~/.claude/tools/memsync/memsync status --json 2>/dev/null \
  && echo "available" || echo "offline"
```

### 架構

```
_learnings.md (Tower 寫入)
    ↓
Stop hook: mem0-bridge.sh
    ↓
memsync memory bridge (Go CLI)
    ↓
REST API (192.0.2.10:8765, Nginx + API Key 認證)
    ↓
OpenMemory API → Qdrant (向量儲存)
```

### Tower 的使用方式

| 操作 | 觸發 | 實際命令 |
|------|------|---------|
| 寫入 | `*evolve` 萃取後寫入 `_learnings.md` | 無需直接呼叫；Stop hook 自動同步 |
| 查詢 | ⚠️ **不支援** | memsync 為 sync-only，無 query 命令 |
| 偵測 | 塔台啟動 | `memsync status --json`（timeout 2s），再依 § 啟用條件 看本地規則有沒有例外紀錄（v6.0.0-beta.10+） |

### 關鍵差異（相較於舊 MCP 架構）

| 項目 | 舊 MCP | 新 REST + memsync |
|------|--------|-------------------|
| 寫入 | 直接 `add_memory()` | `_learnings.md` + Stop hook 自動化 |
| 查詢 | 直接 `search_memory()` | ❌ Tower 無法查詢 |
| 偵測 | 嘗試 MCP 工具 | `memsync status --json` |
| 依賴 | Claude Code MCP 註冊 | memsync CLI + Stop hook + REST server |

### 無 mem0 降級

偵測失敗、或本地規則沒有例外紀錄而不啟用（§ 啟用條件）時，塔台仍然正常運作：
- `_learnings.md` 寫入不受影響（Layer 3 本地儲存）
- `*evolve` 流程不受影響
- 僅跨裝置/跨專案的長期記憶同步失效
- 面板顯示 ❌ 或 ⚠️ 提示使用者，但不阻塞操作

### 能力矩陣

| 功能 | L0 | +方法論 adapter | +mem0 REST |
|------|----|-----------------|------------|
| 本地學習 | ✅ | ✅ | ✅ |
| session 證據（v6.0.0-beta.10+） | ✅（`ct-evolve --facts-from`） | ✅ | ✅ |
| 工作流引導 | ❌ | ✅ | ✅ |
| 跨裝置同步（寫入） | ❌ | ❌ | ✅ |
| 跨專案查詢 | ❌ | ❌ | ⚠️ 不支援 |

> v6.0.0-beta.9 以前兩張表多一欄「+ECC」；v6.0.0-beta.10 起 ECC Level 1 退場，該欄移除（§ ECC Level 1 退場）。
> 兩張表的「+mem0 REST」欄只適用於本地規則記錄了例外、已啟用 Level 3 的專案（§ 啟用條件，v6.0.0-beta.10+）。

## 降級行為速查

| 功能 | L0 | +方法論 adapter | +mem0 REST |
|------|:--:|:---------------:|:----------:|
| 工單派發 | ✅ | ✅ 方法論路由 | ✅ |
| 進度追蹤 | ✅ | ✅ | ✅ |
| Debug 策略 | ✅ | ✅ +驗證層提示（bmad：TEA） | ✅ |
| 中斷處理 | ✅ | ✅ | ✅ |
| 多塔台 | ✅ | ✅ | ✅ |
| 觀察記錄 | ✅ 回報時；session 統計（只在呼叫時） | ✅ | ✅ |
| 模式萃取 | ✅ 讀工單＋候選事實 | ✅ +方法論標注 | ✅ |
| 置信度 | ✅ 4級emoji | ✅ | ✅ |
| Playbook | ✅ | ✅ +回饋 | ✅ |
| 方法論路由 | ❌ 手動 | ✅ 自動 | ✅ |
| 跨專案學習 | ✅ 分流提問寫入 Layer 2 | ✅ | ⚠️ 僅寫入同步，Tower 不可查詢（見 § Tower 的使用方式） |
| 全局經驗 | ⚠ 本機（Layer 2） | ⚠ | ✅ Qdrant（僅寫入，Tower 不可查詢） |
