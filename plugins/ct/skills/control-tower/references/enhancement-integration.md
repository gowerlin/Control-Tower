# 增強整合：ECC + bmad-guide + mem0 REST

本檔定義三個可選相依的整合方式與降級行為。
每項偵測獨立——缺少任何一個都不影響其他功能。

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

ECC、bmad-guide、mem0 等增強功能的學習成果，依分流規則寫入 Layer 2 或 Layer 3：
- 通用模式 → Layer 2（跨專案生效）
- 專案特定 → Layer 3（僅本專案生效）
- 不確定 → Layer 3 + `candidate: global` 標記（待日後晉升）

> 詳細架構規格見 [data-layer-architecture.md](data-layer-architecture.md)。

## 能力等級

| Level | 條件 | 能力 |
|-------|------|------|
| 0 | 零相依 | 完整核心：工單、進度、Debug、學習（_learnings.md） |
| 1 | +ECC | hook 觀察 + instinct 置信度 + /evolve 進化 |
| 2 | +bmad-guide | 自動 BMad workflow routing + Agent 標注 |
| 3 | +mem0 REST | 寫入同步跨裝置/跨專案經驗（單向，memsync CLI 橋接） |

等級可任意組合：Level 0+2（有 bmad-guide 無 ECC）完全合法。

## Level 1：ECC continuous-learning-v2

### 偵測

檢查 `~/.claude/homunculus/` 目錄是否存在。

### CT → ECC 觀察寫入

工單回報處理時，**除了寫 _learnings.md（Level 0 保底）**，額外寫入 ECC observations.jsonl：

```jsonl
{"timestamp":"...","event":"ct_workorder_complete","tool":"ControlTower",
 "project_id":"...","project_name":"...",
 "input":{"workorder_id":"T0002","bmad_workflow":"bmad-prd","estimated_size":"大"},
 "output":{"result":"DONE","actual_minutes":46,"output_files":21}}

{"timestamp":"...","event":"ct_user_correction","tool":"ControlTower",
 "input":{"tower_planned":"skip to handover","user_said":"審查問題不修正嗎？"},
 "output":{"tower_corrected_to":"insert fix workorder","pattern_category":"quality-gate"}}

{"timestamp":"...","event":"ct_decision","tool":"ControlTower",
 "input":{"question":"不選技術能做 Stories 嗎？"},
 "output":{"decision":"yes","rationale":"Story 格式天然技術無關"}}
```

ECC observer 自動從 `ct_*` 事件中產生 `domain: "orchestration"` 的 instincts。

### ECC → CT instinct 讀取

啟動時掃描 ECC instincts 中 `domain: "orchestration"` 的條目，按 confidence 排序載入。

### confidence 映射

| ECC 數值 | CT 符號 |
|---------|--------|
| 0.3 | 🔵 |
| 0.5 | 🟡 |
| 0.7 | 🟢 |
| 0.85+ | ⭐ |

### /ct-evolve Level 1 增強

Level 0 全部 + ：
- 讀取 ECC instincts (domain: orchestration)
- 將 _learnings.md 新模式同步為 ECC instinct YAML
- 調用 ECC /evolve 做 instinct 聚類
- 顯示 /promote 候選（project → global）

### 雙寫保障

**永遠同時寫 _learnings.md 和 ECC observations**。即使 ECC 被移除，_learnings.md 仍保有完整學習紀錄——不因解除相依而丟失知識。

## Level 2：外部 bmad-guide

Control Tower 不內嵌 `BMad-Guide-Skill` 或 `BMad-Method` 內容。Level 2 的唯一責任是偵測外部已安裝的 `bmad-guide` skill，並在需要 BMad workflow routing 時讀取它的 references。

### 偵測

檢查 `bmad-guide` skill 是否可用：

1. 優先讀取已安裝 skill 的 `bmad-guide/SKILL.md`。
2. 讀取 `current_version` marker；若低於任務所需版本，顯示升級提示但不阻塞 Tower。
3. 嘗試讀取 `references/workflow-map.md`；成功即視為 Level 2 可用。
4. 查詢失敗或未安裝時，靜默 fallback 為手動 workflow 欄位。

版本化發行包中可參考 `BMad-Guide-Skill/bmad-guide-v<版號>/`（例 `bmad-guide-v6.12.4/`），但安裝後的 runtime source of truth 是實際可用的 `bmad-guide` skill。

### Workflow Routing

派發工單時查詢 bmad-guide references：

| 時機 | 查詢 | 取什麼 |
|------|------|--------|
| 選工作流程 | workflow-map.md | Phase→Workflow→Agent 映射、retired/deprecated 名稱替代 |
| 棕地專案 | brownfield.md | Phase 0 步驟、context/docs、research workorder 判斷 |
| 小修改 | supplementary-workflows.md | Spec / Build（舊稱 Quick Flow）：`bmad-spec`／`bmad-build` 適用條件 |
| 無人值守單次迭代 | supplementary-workflows.md | `bmad-build-auto` prerequisites、spec status contract、blocked handling |
| 自動化循環 | ecosystem-modules.md | `bmad-loop` 安裝、`bmad-loop-setup`、Automator migration |
| 新功能或模組詢問 | ecosystem-modules.md | 官方 opt-in modules registry、Web Bundles、BMad Builder、TEA、Game Dev、Creative、WDS |
| 需要測試 | tea-module.md | TEA 整合時機 |
| 需要審查 | supplementary-workflows.md | Adversarial Review 規則 |

查詢失敗 → 靜默 fallback，使用者手動指定。

### BMad v6.10+ Routing Overrides

當外部 `bmad-guide` 顯示 BMad-Method v6.10.0 或更新時，Tower routing 必須採用下列替代：

| 舊名 / 需求 | Tower 路由 |
|-------------|------------|
| `bmad-investigate` | 已 retired；改開 CT research workorder、一般調查，或先用 `bmad-project-context`（setup intent）補 context |
| `bmad-automator` | 已 deprecated；循環建議 `bmad-loop` + `bmad-loop-setup`，無人值守單次迭代用 `bmad-build-auto` |
| `bmad-create-architecture` | compatibility shim；新工單標 `bmad-architecture` |
| UX 舊流程 | 使用 `bmad-ux`，產出 `DESIGN.md` + `EXPERIENCE.md` |
| 自動化單次執行 | `bmad-build-auto`，工單必須要求 Worker 回報 durable artifact、spec status、`baseline_revision`、commit 範圍 `baseline_revision..HEAD`（多個 story：`baseline_revision..下一個 story 的 baseline_revision`） |

### 工單中的 BMad 標注

有 bmad-guide 時，工單自動包含：
```markdown
### BMad 工作流程
`bmad-prd`
- Agent: PM (John) — `bmad-agent-pm`
- Phase: 2 (Planning)
- Guide: bmad-guide v6.12.4 reference: workflow-map.md
```

無 bmad-guide 時，工單的工作流程欄位為自由文字。

`bmad-build-auto` 工單需額外標註：

```markdown
### Autonomous Contract
- Monitor: `{implementation_artifacts}/spec-*.md` or `bmad-build-auto-result-*.md`
- Terminal status: `done` / `blocked`
- Required report: blocking condition, verification, changed files, `baseline_revision`, commit range `baseline_revision..HEAD` (multiple stories: `baseline_revision..<next story's baseline_revision>`)
```

### Playbook → bmad-guide 回饋

Playbook 被 2+ 專案驗證後，提議更新 bmad-guide 的 brownfield.md：
```
brownfield-reverse-eng playbook 已在 2 個專案中驗證。
要我更新 bmad-guide 的 brownfield.md 嗎？
```

## Level 3：mem0 REST（memsync CLI 橋接）

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
| 偵測 | 塔台啟動 | `memsync status --json`（timeout 2s） |

### 關鍵差異（相較於舊 MCP 架構）

| 項目 | 舊 MCP | 新 REST + memsync |
|------|--------|-------------------|
| 寫入 | 直接 `add_memory()` | `_learnings.md` + Stop hook 自動化 |
| 查詢 | 直接 `search_memory()` | ❌ Tower 無法查詢 |
| 偵測 | 嘗試 MCP 工具 | `memsync status --json` |
| 依賴 | Claude Code MCP 註冊 | memsync CLI + Stop hook + REST server |

### 無 mem0 降級

偵測失敗時塔台仍然正常運作：
- `_learnings.md` 寫入不受影響（Layer 3 本地儲存）
- `*evolve` 流程不受影響
- 僅跨裝置/跨專案的長期記憶同步失效
- 面板顯示 ❌ 或 ⚠️ 提示使用者，但不阻塞操作

### 能力矩陣

| 功能 | L0 | +ECC | +bmad-guide | +mem0 REST |
|------|----|------|-------------|------------|
| 本地學習 | ✅ | ✅ | ✅ | ✅ |
| ECC instinct | ❌ | ✅ | ✅ | ✅ |
| 工作流引導 | ❌ | ❌ | ✅ | ✅ |
| 跨裝置同步（寫入） | ❌ | ❌ | ❌ | ✅ |
| 跨專案查詢 | ❌ | ❌ | ❌ | ⚠️ 不支援 |

## 降級行為速查

| 功能 | L0 | +ECC | +bmad-guide | +mem0 REST |
|------|:--:|:----:|:-----------:|:----------:|
| 工單派發 | ✅ | ✅ | ✅ 自動 routing | ✅ |
| 進度追蹤 | ✅ | ✅ | ✅ | ✅ |
| Debug 策略 | ✅ | ✅ | ✅ +TEA 提示 | ✅ |
| 中斷處理 | ✅ | ✅ | ✅ | ✅ |
| 多塔台 | ✅ | ✅ | ✅ | ✅ |
| 觀察記錄 | ✅ 回報時 | ✅ +hook 100% | ✅ | ✅ |
| 模式萃取 | ✅ 讀工單 | ✅ +observer | ✅ +Agent 標注 | ✅ |
| 置信度 | ✅ 4級emoji | ✅ +數值 | ✅ | ✅ |
| Playbook | ✅ | ✅ +聚類 | ✅ +回饋 | ✅ |
| Workflow 路由 | ❌ 手動 | ❌ 手動 | ✅ 自動 | ✅ |
| 跨專案學習 | ⚠ 手動複製 | ✅ /promote | ✅ | ⚠️ 僅寫入同步，Tower 不可查詢（見 § Tower 的使用方式） |
| 全局經驗 | ⚠ 本機 | ⚠ ECC global | ⚠ | ✅ Qdrant（僅寫入，Tower 不可查詢） |
