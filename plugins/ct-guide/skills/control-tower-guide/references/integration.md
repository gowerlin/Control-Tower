# 生態系整合

## Control Tower 的獨立性

CT 在 Level 0 零相依：只要能讀寫 `.md` 檔案的 AI 工具就能運作，落地為 Claude Code 與 Codex 都能當塔台或 Worker。
它不依附於特定的開發方法論或平台；與其他工具整合時，能力逐級遞增，但**每項偵測各自獨立**，缺少任何一個都靜默降級。

能力等級總表（Level 0–3 各需要什麼、提供什麼）見 `ecosystem.md` § 能力等級。本檔講每一級**怎麼整合、降級時剩下什麼**。

---

## Level 1：ECC continuous-learning-v2

ECC（Everything Claude Code）的 continuous-learning-v2 以 hook 觀察工具使用，自動形成 instinct。CT 以 `~/.claude/homunculus/` 是否存在判定它可用。

| 方向 | 作法 |
|------|------|
| CT → ECC | 處理工單回報時，除了寫 `_learnings.md`，另寫入 ECC observations：工單完成、使用者糾正、塔台決策三類事件 |
| ECC → CT | 塔台啟動時讀取 `domain: "orchestration"` 的 instinct，依置信度排序載入 |
| 置信度對應 | ECC 的數值置信度對應 CT 的 🔵／🟡／🟢／⭐ |

**雙寫保障**：永遠同時寫 `_learnings.md` 與 ECC observations。即使之後移除 ECC，`_learnings.md` 仍保有完整學習紀錄——**不因解除相依而丟失知識**。

兩者是互補而非重疊：ECC 學的是工具使用層面的模式，CT 的 `*evolve`／`ct-evolve` 學的是專案協調層面的模式。

---

## Level 2：外部 bmad-guide

### 三者的關係

```
BMad-Method（方法論）
  ↕ 定義開發階段、Agent 角色、工作流程
bmad-guide（外部 skill，導航）
  ↕ 告訴塔台「這件事該走哪個 workflow」
Control Tower（執行）
  → 用工單管理實際執行
```

### CT 不內嵌 BMad 內容

v5.0.3 起，CT **不附帶**任何 BMad-Method 或 bmad-guide 的內容。Level 2 的唯一責任，是偵測使用者另外安裝的 `bmad-guide` skill，
需要 BMad workflow routing 時去讀它的 reference。

**為什麼要拆出去？** BMad-Method 有自己的版本節奏：workflow 會改名、退役、被取代。把它的內容內嵌在 CT 裡，
CT 就得跟著 BMad 每一次改版重新發行，而且內嵌的那份必然落後。讓 CT 只負責「偵測並讀取外部導航」，
BMad 的知識就只有一個事實來源——外部 `bmad-guide`。這與 `governance.md` 的單一權威定義是同一個原則。

### 偵測與降級

塔台依序檢查：外部 `bmad-guide` 的 SKILL.md 是否可讀、它的版本是否滿足任務需要（太舊只提示升級、不阻斷）、
它的 workflow 對照表是否讀得到。讀得到就是 Level 2 可用。

**去哪裡找 SKILL.md（v5.14.1）。** bmad-guide 有兩種裝法：zip 手動安裝放在 `skills/bmad-guide/`，plugin 安裝
（同一個 marketplace 的 `bmad-guide@control-tower`，見 `governance.md` § plugin marketplace：另一種安裝方式）則放在 plugin 管理的目錄。
5.14.0 只寫「讀取已安裝 skill」，塔台習慣去 `skills/` 找；用 plugin 裝的 bmad-guide 找不到，又不說一聲，就默默改成手動欄位——
使用者明明裝了，卻以為 Level 2 沒作用。5.14.1 把搜尋順序寫成一張表：

| 順序 | 安裝方式 | 塔台去哪裡讀 |
|---|---|---|
| 1 | 手動安裝（zip） | 各 agent 的 `skills/bmad-guide/SKILL.md` |
| 2 | Claude Code plugin | plugin 安裝清單裡 `bmad-guide@<任一 marketplace>` 指的安裝目錄 |
| 3 | Codex plugin | Codex 設定裡啟用的 `bmad-guide@<任一 marketplace>`，到 plugin cache 取該版本 |

幾個設計上的選擇：

- **第一個讀得到的就用，手動優先。** 兩種都裝時，agent 實際載入的是手動那份（`governance.md` 的並存表），塔台讀同一份，才不會路由和 agent 用的版本對不上
- **marketplace 名稱不寫死。** 只比對 `bmad-guide@*`，從別的 marketplace 裝也找得到
- **`references/` 相對於找到的 SKILL.md。** plugin 版的 reference 不在 `skills/` 底下，所以不另外假設路徑
- **只讀。** plugin 目錄也是 Layer 1（`three-layer-arch.md` § plugin 安裝路徑也是 Layer 1），偵測只讀不寫

**已安裝卻讀不到：提示一次（v5.14.1）。** 可用 skill 清單裡有 `bmad-guide`（或 plugin 寫法 `bmad-guide:bmad-guide`），三處卻都讀不到檔案時，
表示裝了但塔台找不到——這和「沒裝」不一樣，靜默降級會讓使用者誤會。所以塔台在本 session 提示一次（建議告訴塔台 SKILL.md 的位置或改用 zip），
再照常改手動欄位、不阻斷。清單裡也沒有，才是真的沒裝，照舊靜默。

**不可用時**：塔台照常運作，工單的 BMad 工作流程欄位改為**手動指定**的自由文字，
且**不自行編造** BMad 行為；已退役或改名的 workflow，也只在外部 guide 或專案明確確認替代者時才改路由。

> 搜尋順序、路徑與提示條件以 CT `enhancement-integration.md` § Level 2 › 偵測為唯一權威；本節只講為什麼。

### 有 bmad-guide 時增加什麼

| 時機 | 塔台向 bmad-guide 取什麼 |
|------|------------------------|
| 選工作流程 | Phase → Workflow → Agent 對照，以及退役／改名的替代 |
| 棕地專案 | Phase 0 步驟、是否先開研究型工單 |
| 小修改 | `bmad-build`（舊稱 Quick Flow）的適用條件 |
| 自動化執行 | 單次自動執行與循環自動化的前置條件 |
| 測試、審查 | TEA 整合時機、對抗式審查規則 |

工單會自動帶上 BMad 標注（workflow、Agent、Phase、所參照的 guide 版本）。查詢失敗一律靜默退回手動指定。

### 版本感知的路由覆寫

外部 guide 顯示 BMad-Method 為 v6.10 或更新時，塔台必須套用替代路由——例如已退役的 workflow 改走 CT 研究型工單或補 context 的 workflow、
已棄用的自動化工具改用其後繼者、UX 舊流程改用新的 UX workflow。
替代清單由 CT 的 `enhancement-integration.md` 定義；**哪個名字在你的 BMad 版本裡還有效，以外部 bmad-guide 為準**。

`sprint-status.yaml` 是 BMad 專案的進度檔，在 CT 的事實來源優先級中排在工單檔案之後（見 `work-order-lifecycle.md` § 事實來源優先級）。

---

## Level 3：mem0 REST

Level 3 是**跨裝置、跨專案的寫入同步**，以 mem0 的 REST 服務為後端，透過 memsync CLI 橋接：

```
_learnings.md（塔台寫入）
    ↓
Stop hook
    ↓
memsync CLI
    ↓
mem0 REST API → 向量儲存
```

| 操作 | 方式 |
|------|------|
| 寫入 | 塔台不直接呼叫；`*evolve` 寫入 `_learnings.md` 後，由 Stop hook 自動同步 |
| 查詢 | **不支援**——memsync 只做同步，塔台無法從 mem0 查詢 |
| 偵測 | 先看 memsync 執行檔是否存在，再以有 2 秒硬性 timeout 的健康檢查確認 |

**單向**是這一級最需要記住的事：mem0 在 CT 中是「把學習送出去」的管道，不是塔台的記憶來源。
塔台的記憶仍然是磁碟上的 `_tower-state.md`、`_learnings.md` 與工單——這延續了 `concepts.md` 第一原則：跨 session 的狀態只能靠專案內的 artifact。

偵測用硬性 timeout，是因為它在塔台啟動時執行：遠端服務掛掉不該拖慢塔台啟動。

**無 mem0 時**：`_learnings.md` 寫入與 `*evolve` 流程完全不受影響，只有跨裝置／跨專案的長期記憶同步失效；面板會提示，但不阻斷任何操作。

---

## Codex 整合

CT 的 8 個 skill 都能在 Codex 中以 `$` 前綴呼叫（`$control-tower`、`$ct-exec T0001`…），塔台與 Worker 可以各自是 Claude Code 或 Codex。
v5.14.0 起用 plugin 安裝時，Codex 要寫 `$ct:` 前綴（`$ct:control-tower`、`$ct:ct-exec T0001`），而且 BAT 派工只支援 zip 手動安裝（見 `governance.md` § plugin marketplace：另一種安裝方式）。

讓同一套 skill 能在兩邊執行的三件事：

| 項目 | 作法 |
|------|------|
| frontmatter | 只保留 `name` 與 `description`——Codex 的 skill 驗證把未知欄位視為錯誤，所以版號移到 body 註解（見 `governance.md` § 版本治理） |
| `agents/openai.yaml` | 每個 skill 附一份，提供 Codex 端的顯示名稱、簡述與預設提示 |
| 指令前綴 | skill 內文不寫死 `/` 或 `$`；派工時由 BAT 依實際啟動的 agent 組出正確前綴 |

派工時 agent 怎麼選（BAT 的預設 agent、非 BAT 時的 `CT_AGENT_CMD`、兩者都在時不得自行偏好）見 `runtime-dispatch.md` § Agent 中立。

> 本教材本身仍以 Claude Code skill 形式打包；內文的指令同時標示 `/` 與 `$` 兩種形式。

---

## Playbook 引擎

Playbook 是知識成熟度管線的 L2 產出：把已驗證的規則整理成**一段工單序列**的標準作業程序。管線四級與晉升條件見 `concepts.md` § 知識成熟度管線。

### Playbook 長什麼樣

每個 playbook 寫明適用與不適用的場景、工單序列（每張的預估時間）、品質關卡、工單模板、注意事項，以及驗證歷史。
專案級放在 `_ct-workorders/_playbooks/`，全域級放在 `~/.claude/control-tower-data/playbooks/`；跨塔台共用全域目錄時的編號規則見 `advanced-patterns.md` § 跨塔台 GP 命名空間。

### 派工時自動建議

塔台準備派發前，會以工單類型、技術棧與工作流程模式比對專案與全域的 playbook。命中時提出建議：

```
📘 偵測到匹配 Playbook
  [A] 套用（依序列產生 N 張工單）
  [B] 不套用（手動規劃）
  [C] 修改後套用（預覽並調整序列）
```

套用時，工單依序列產生、套上對應的品質關卡、回報區標記 playbook 來源，並更新該 playbook 的驗證歷史——**每次使用都在累積它的晉升證據**。

### L2 → L3：停在 skill brief

Playbook 在 **3 個以上專案**使用並達最高置信度後，`*evolve --skill` 會把它轉成一份 skill 規格摘要：
適用場景 → 觸發條件、工單序列 → 執行步驟、品質關卡 → 驗收條件。

到此為止。要真正寫成已安裝的 skill，使用者須**自己在新 session 呼叫 `skill-creator`**。
已安裝的 skill 屬於 Layer 1，塔台與 `ct-evolve` 都不寫入（見 `three-layer-arch.md` § Layer 1 寫入規則）；playbook 寫入路徑若落在 Layer 1 路徑（`~/.claude/skills/`、`~/.codex/skills/`，v5.14.0 起含 plugin 安裝路徑）之下一律拒絕。

另有一條回饋路徑：某個 playbook 被 2 個以上專案驗證後，塔台會提議更新外部 `bmad-guide` 的對應 reference——是否更新由使用者決定。
bmad-guide 是 plugin 安裝時（v5.14.1），這條路徑不改已安裝的檔案：plugin 目錄是 Layer 1，下次更新也會蓋掉，所以改成提議修改 bmad-guide 的原始碼、隨下一版發布。

---

## 研究／Spec 文件

專案裡常有「不是工單、也不是程式碼」的文件。CT 以**檔名前綴**辨識它們，放在 `_ct-workorders/` 底下：

| 檔名 | 用途 |
|------|------|
| `_spec-*.md` | 技術規格 |
| `_report-*.md` | 研究報告 |
| `_spike-*.md` | 技術 spike 紀錄 |
| `_question-*.md` | 待解決的技術問題 |
| `_roadmap-*.md` | 路線圖 |
| `reports/` 子目錄 | 大型研究報告 |

這些都是**長期參考文件**：`*sync` 掃描工單時跳過它們（不會被誤認為工單），`*archive` 也完全不把它們列入歸檔範圍——它們沒有「結束」的生命週期。

---

## 安全匯入（`*import`）

`*import` 讓使用者把規則或 playbook 安全地併入專案，不破壞現有設定：

| 語法 | 行為 |
|------|------|
| `*import rule` | 互動式新增規則，寫入 `_local-rules.md` |
| `*import playbook` | 互動式新增 playbook，寫入 `_learnings.md` |
| `*import --from <檔案>` | 從草稿或其他專案的 `_local-rules.md` 匯入，依內容判斷類型 |
| `*import --check` | **查看**目前的設定狀態（規則、learnings、專案與全域設定檔是否存在） |
| `*import --fix` | **修復格式**（標題層級不一、缺分隔、重複標題、編碼問題），保留所有內容，確認後才修 |

### 安全流程

```
讀取目標檔現有內容 → 接收新內容 → 衝突分析 → 顯示合併計畫 → 使用者確認 → 寫入 → 回報新增／保留／跳過
```

同名區段衝突時並排顯示差異，讓使用者選：[A] 保留舊版、[B] 使用新版、[C] 手動合併。

六條**不可覆寫**的硬限制：絕不直接覆蓋現有檔案、絕不未告知就解決衝突、絕不在確認前寫入；寫入前必讀現有內容、衝突必顯示差異等使用者決定、寫入後必回報結果。
設計重點是**合併而非覆寫**：使用者的規則是他自己的判斷累積，匯入工具沒有資格替他取捨。

---

## 互動探索（`*onboard`）

`*onboard` 透過問答把使用者的工作習慣變成個人化規則。觸發後塔台切換為「工作流程教練」角色：暫停派工，探索完成前不產生任何工單。

### 五個主題

1. **Git 工作習慣**
2. **哪些小事不需要開工單**
3. **Worker 工單結束後的 Git 行為**
4. **遇到不清楚的問題怎麼辦**
5. **塔台與 Worker 的邊界**（快速確認）

提問方式本身就是規則：每題都是選項式並附「其他」兜底、一次最多兩題、每個主題結束後複述理解讓使用者確認、
不催促、不直接說「你應該用 X」。使用者說「不確定」時套用該題的預設值，之後再改也沒關係。

### 產出

1. **`_local-rules.md` 草稿**——完整顯示給使用者確認
2. **研究型工單 playbook 草稿**——只在使用者的回答涉及研究型工單時產生，寫入 `_learnings.md`
3. 確認後透過 `*import` 的安全流程合併寫入；下次啟動塔台時自動載入

### 使用場景

- 第一次在專案啟動塔台，想讓塔台配合自己的習慣
- 重新執行 `*onboard`：已有 `_local-rules.md` 時會先問要重新探索、只改某條規則（導向 `*import rule`），還是看目前設定（導向 `*import --check`）

---

## 環境偵測

塔台啟動時偵測各增強元件，結果顯示在狀態面板中：

| 元件 | 判定可用的依據 |
|------|--------------|
| ECC（Level 1） | `~/.claude/homunculus/` 存在 |
| 外部 bmad-guide（Level 2） | skill 可讀且 workflow 對照表讀得到（手動安裝或 plugin 安裝皆可，v5.14.1） |
| mem0 REST（Level 3） | memsync 存在且健康檢查在 timeout 內通過 |

偵測結果只決定**增強功能**的啟用範圍；缺少任何元件都不影響核心功能，面板只提示、不阻斷。

v5.2.1 起狀態面板有唯一定義（CT 本體 `memory-protocol.md` § 塔台狀態面板），最小欄位含分支／HEAD、工作區、進行中工單、下一個工單編號、BAT、auto-session（含來源層）、分頁標題、立即待辦。
在 Worker 分頁啟動時，BAT 欄位的值與原因見 `bat-integration.md` § 範圍權杖與分頁角色；值域與判定以 CT 本體 `memory-protocol.md` § 塔台狀態面板 為準。
面板是**格式範本**：沒有資料的欄位寫「未知」，不為了填欄位跑額外掃描。
