# 多塔台協調協議

> **範圍**：本文件處理兩種多塔台情境：
> 1. **同專案內多個塔台 session**（如 Feature + Hotfix 平行作業）— 主要原文，見下方「記憶分層」「塔台登記簿」「跨塔台留言板」「決策」段落
> 2. **跨 user 環境的塔台**（不同安裝、共用 `~/.claude/control-tower-data/`）— 由 D62 協議定義，見下方「跨塔台 GP 編號協議（D62）」段落
>
> **跨專案**協調（同一 user 環境，不同專案的塔台之間）請見 [cross-project-coordination.md](cross-project-coordination.md)。

## 記憶分層

| 層級 | 內容 | 機制 |
|------|------|------|
| 共享層 | 工單檔案、sprint-status.yaml、_decision-log.md、`AGENTS.md` 的專案上下文區塊（BMad v6.11+；舊專案為 project-context.md） | 磁碟檔案，天然共享 |
| 協調層 | 塔台登記簿、跨塔台留言板 | 約定檔案 + 啟動掃描 |
| 隔離層 | Context window 對話、當前推理、個人進度快照 | Context window 天然隔離 |

## 塔台登記簿

存放於 `_ct-workorders/_tower-registry.md`，每個塔台啟動時寫入：

```markdown
# 塔台登記簿

| 塔台 ID | 啟動時間 | 範圍 | 分支 | 最後心跳 | 鎖定工單 |
|---------|---------|------|------|---------|---------|
| CT-A | 2026-03-30 20:00 | Story 1.2-1.5 | feature/auth | 2026-03-30 21:30 | T0005 |
| CT-B | 2026-03-30 21:00 | HOTFIX-01 | main | 2026-03-30 21:15 | T0006 |
```

### 規則

- 啟動時寫入登記
- 每次派發/處理工單時更新心跳
- 超過 2 小時無心跳 → 視為離線，鎖定的工單可被接管
- 不同塔台不可鎖定同一工單

## 跨塔台留言板

存放於 `_ct-workorders/_cross-tower-notes.md`：

```markdown
# 跨塔台留言板

---
**CT-B → CT-A** | 2026-03-30 21:20
HOTFIX-01 修了 Redis pool 設定（config/redis.yml max_connections 10→50）。
如果 Story 1.3 涉及 Redis，需要在 feature 分支 merge main。
---
```

### 檢查時機

- 塔台啟動時
- 每次派發新工單前
- 使用者說「sync」時

## 決策：一個塔台還是多個

| 條件 | 建議 |
|------|------|
| 子專案共用 DB、共用 API、經常同步改動 | 🗼 一個塔台 |
| 子專案獨立部署、獨立 DB、很少同時改動 | 🗼🗼 各開塔台 |
| 子專案是跟團隊共用的獨立 repo、隊友不用 CT（v5.14.3+） | 🗼 一個塔台，工單集中在上層的個人塔台 repo（[mono-repo-patterns.md](mono-repo-patterns.md) § 巢狀的獨立 repo）；隊友也用 CT、或需要 worktree 隔離改子 repo → 🗼🗼 各開塔台（同節〈何時改用方案 2〉） |
| 不確定 | 先用一個，太雜再拆 |
| Feature + Hotfix 在不同分支 | 🗼🗼 各開塔台 + Worktree 隔離 |

> 若開了多個塔台且涉及不同專案的協調需求，請參考 [cross-project-coordination.md](cross-project-coordination.md)
> 的 COORDINATED / DELEGATE 工單機制。

---

## 跨塔台 GP 編號協議（D62）

> **協議來源**：D62（2026-04-23 拍板，方案 D — 命名空間前綴）
> **適用範圍**：多個獨立塔台共用同一個 user 環境（`~/.claude/control-tower-data/`）的場景
> **典型情境**：同一台機器跑 project-b + better-agent-terminal + BMad-Guide 三個獨立 repo 的塔台

### 背景

`*evolve --playbook` 晉升的 Global playbook 寫入 Layer 2（`~/.claude/control-tower-data/playbooks/`），此目錄**所有塔台共用**。舊規則「全域 max GP + 1」會撞號：

- 案例：T0362 audit 揭露 GP071-075 在 project-b PLAN-001 批和 better-agent-terminal/BMad-Guide 批之間撞號
- T0363 事後修復為 GP085-089，但屬手工補救

D62 改採「命名空間前綴」前瞻性避免撞號。

### 協議總覽

```
舊：GP###（全域共享，會撞）
新：GP-<PREFIX>-###（namespace 隔離，不撞）
```

| 維度 | 舊 | 新（D62）|
|------|----|---------|
| 命名格式 | `GP089` | `GP-COOP-001` |
| 編號計算範圍 | 全域 max+1 | 同 namespace max+1 |
| 跨塔台同步成本 | 需手工查 max（已實證失敗） | 零成本（各自治）|
| 撞號風險 | 高 | 零(不同 namespace 不會撞) |

### 命名空間前綴對照表

| 塔台 | gp-prefix | 範例編號 |
|------|-----------|---------|
| project-b | `COOP` | `GP-COOP-001`, `GP-COOP-002`, ... |
| better-agent-terminal (BAT) | `BAT` | `GP-BAT-001`, `GP-BAT-002`, ... |
| BMad-Guide | `BMAD` | `GP-BMAD-001`, `GP-BMAD-002`, ... |
| 其他塔台 | 各自定義 2-4 字大寫 | 如 `GP-LC-###`、`GP-ME-###` |

> **註冊原則**：採「先到先得，事後告知」。新塔台採納時應先 grep 一次 `~/.claude/control-tower-data/playbooks/`
> 看現有 `GP-*-###` 前綴清單，避免取重複的。撞前綴時 user 自行協調。

### 衝突避免機制（各塔台自治）

```
塔台 A（PREFIX=COOP）              塔台 B（PREFIX=BAT）
─────────────────────              ─────────────────────
*evolve --playbook                 *evolve --playbook
↓                                  ↓
讀本地 _tower-config.yaml          讀本地 _tower-config.yaml
gp-prefix: COOP                    gp-prefix: BAT
↓                                  ↓
grep "GP-COOP-*" Layer 2 + Layer 3 grep "GP-BAT-*" Layer 2 + Layer 3
↓                                  ↓
max=12 → 新編號 GP-COOP-013        max=4 → 新編號 GP-BAT-005
↓                                  ↓
寫入 GP-COOP-013-xxx.md            寫入 GP-BAT-005-xxx.md
─────────────────────              ─────────────────────
                ╲                                   ╱
                 ╲    Layer 2 共用目錄              ╱
                  ╲   ~/.claude/control-tower-data/playbooks/
                   ╲                              ╱
                    GP-COOP-013-xxx.md  GP-BAT-005-xxx.md
                    （兩檔不撞，各自獨立 namespace）
```

**關鍵保證**：
- 各塔台只查自己的 namespace（`GP-<PREFIX>-*`）
- 寫入前不需鎖、不需同步、不需 central registry
- 兩塔台同時跑 `*evolve --playbook` 也不會產生重號（因 PREFIX 不同）

### 舊 GP001-094 凍結聲明

D62 協議**不溯及既往**。

| 項目 | 規則 |
|------|------|
| 舊 playbook 檔名 | 不改名（保持 `GP070-xxx.md` 等原格式） |
| 舊引用 | 不變（工單寫「依 GP070 流程」依然有效） |
| 凍結範圍 | `GP001` 到 `GP094`（含 T0363 修復後的 `GP085-089`）|
| 新晉升 | **強制**用 `GP-<PREFIX>-###` 格式，**禁止**產生 `GP095` 或更高的「無前綴」編號 |
| 跨號段引用 | 新舊號段可互相引用（如「GP-COOP-001 沿用 GP070 思路」）|

### 跨塔台採納流程

D62 是「自願採納」協議，各塔台獨立決定何時採納。

**單一塔台採納步驟**：

```
1. 確認本機 control-tower skill 版本 ≥ D62 採納版本
2. 規劃本塔台的 PREFIX（2-4 字大寫，避免與其他塔台撞）
3. 在 _ct-workorders/_tower-config.yaml 設定：
   gp-prefix: COOP   # 或 BAT / BMAD / 自定
4. 之後 *evolve --playbook 自動採納新規則
5. 第 1 個新晉升從 GP-<PREFIX>-001 起
```

**多塔台分階段採納**（典型情境）：

```
2026-04-23  D62 拍板
2026-04-23  T0364 完成 Phase 2a draft
2026-04-2X  Phase 2b: apply skill upgrade（單一 commit batch）
2026-04-2X  Phase 3a: project-b 設 gp-prefix: COOP
2026-04-XX  Phase 3b: BAT 採納（user 切到 BAT repo 塔台執行）
2026-04-XX  Phase 3c: BMad-Guide 採納（user 切到 BMad-Guide repo 塔台執行）
```

### `gp-prefix` 設定（唯一權威定義）

`gp-prefix` 的定義、設定位置與未設定時的行為，以本節為唯一權威定義；
[playbook-engine.md](playbook-engine.md) 只交叉引用，不複述。

- **設定位置**：`_ct-workorders/_tower-config.yaml` 的 `gp-prefix: <PREFIX>`（2-4 字大寫）。
  `gp-prefix` 不列在 [tower-config.md](tower-config.md) 的 `*config` 選項表中。
- **未設定時的 fallback 鏈**（`*evolve --playbook` 決定 GP 編號前綴時）：
  1. 讀 `project-prefix`（同 `_tower-config.yaml`，定義見 [tower-config.md](tower-config.md)）
  2. `project-prefix` 也空 → 警告並**拒絕晉升**，不產生新 playbook：
     ```
     ❌ 無法晉升 Playbook：未設定 `gp-prefix` 也未設定 `project-prefix`
        D62 協議要求新 GP 編號使用命名空間前綴（避免跨塔台撞號）
        請在 _ct-workorders/_tower-config.yaml 設定：gp-prefix: <PREFIX>
     ```

> ⚠️ **fallback 是緊急防呆，不是預期行為**。建議所有採納 D62 的塔台**明確**設定 `gp-prefix`，
> 不要仰賴 fallback。理由：`project-prefix`（如 CP）的語義是「跨專案工單前綴」，與
> `gp-prefix`（GP 命名空間）不同，混用會產生語義汙染。

**未採納的塔台行為**：
- `gp-prefix` 與 `project-prefix` 皆未設定的塔台，執行 `*evolve --playbook` 時依上方 fallback 鏈被拒絕晉升
- 不影響已採納塔台的正常運作
- 不影響舊 GP001-094 引用

### 與 multi-tower 機制的差異

| 維度 | 同專案多塔台（本文上半段）| 跨塔台 GP 協議（D62）|
|------|--------------------------|---------------------|
| 共享範圍 | 同一 `_ct-workorders/` 目錄 | 同一 `~/.claude/control-tower-data/` |
| 衝突場景 | 多塔台搶同一張工單 | 多塔台撞 GP 編號 |
| 解法 | 塔台登記簿 + 心跳 | namespace 前綴 |
| 同步成本 | 需讀寫登記簿 | 零(各自治) |
| 適用情境 | Feature + Hotfix 平行作業 | 同 user 跑多 repo 塔台 |

### Cross-reference

- 行為規格：[playbook-engine.md](playbook-engine.md) § GP 編號規則（D62）
- Config 入口：`_ct-workorders/_tower-config.yaml` 的 `gp-prefix`（本檔 § `gp-prefix` 設定）
- 決策日誌：D62（2026-04-23）
