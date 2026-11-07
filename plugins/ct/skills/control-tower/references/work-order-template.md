# 工單模板

產生新工單時，複製此模板並填入實際值。

```markdown
# 工單 T<編號>-<描述>

## 元資料
- **工單編號**：T<編號>
- **任務名稱**：<任務描述>
- **狀態**：PENDING
- **建立時間**：<當前時間> (UTC+8)
- **開始時間**：（sub-session 開始時填入）
- **完成時間**：（完成時填入）
- **目標子專案**：（mono-repo 時填寫，單一專案可留空；巢狀的獨立 repo 見 `mono-repo-patterns.md` § 巢狀的獨立 repo）
- **intervention_type**：fire-and-forget / context-dependent / decision-requiring（未填時 Worker 視為 fire-and-forget；填寫指引見下方）
- **affects_files**（v4.4.0+，可選；供塔台派發前 overlap check 使用，填寫指引見下方「填寫 `affects_files` 指引」）：
  - `<相對路徑 1>`
  - `<相對路徑 2>`
- **memory_overrides**（v4.4.0+，可選；僅當本工單指示與 Worker 歷史慣例 / 全局記憶衝突時才填寫；填寫指引見下方「填寫 `memory_overrides` 指引」）：
  - ❌ 「<舊慣例 A 描述>」→ 本工單處理：嚴禁。棄用理由：<具體理由>
  - ✅ 「<沿用規則 B 描述>」→ 本工單處理：沿用。理由：<具體理由>

## 工作量預估
- **預估規模**：大 / 中 / 小
- **Context Window 風險**：高（>100 檔案）/ 中 / 低
- **降級策略**：若 Context Window 不足，可先完成 [子範圍]，回報 PARTIAL

## Session 建議
- **建議類型**：🆕 新 Session / 🔄 原 Session
- **原因**：<具體原因>

## 規格層級自問（派發前）

<!-- spec_level_check：塔台在派發工單前自問五項規格層級，降低誤派風險；v4.4.0+ 新增第 5 項「記憶覆蓋」 -->

- [ ] **目標層**：這張工單的目標是**執行**（有明確輸出）/ **設計**（需要先決定方向）/ **研究**（不知道該做什麼）？
- [ ] **決策權歸屬**：Worker 是否有權自行決定 X？（X = 技術方案、檔案位置、命名、介面）
- [ ] **資訊完整度**：Worker 僅讀工單 + 前置條件檔案，是否足以獨立完成？若不足，缺什麼？
- [ ] **回頭成本**：若 Worker 走錯方向，回復成本是（A）改幾行程式 /（B）重做半天 /（C）整個子系統要重設計？
- [ ] **記憶覆蓋**：本工單指示是否與任何已知的 memory / 全局記憶 / 歷史慣例衝突？若有，是否已在 `memory_overrides` 欄位明示覆蓋？

> **自問指引**
> - 若第 1 項選「研究」→ 考慮改用**研究型工單**（`類型: research` + `互動模式: enabled`）
> - 若第 2 項有任一 X 回答「否」→ 該 X 須在工單內明文指定，不能丟給 Worker（亦可考慮標 `intervention_type: decision-requiring`）
> - 若第 3 項回答「不足」→ 補齊前置條件，或拆成兩張工單（先探索後執行）
> - 若第 4 項為 C → 升級為 meta-PLAN 先規劃再執行
> - 若第 5 項回答「是」→ **必填** `memory_overrides` 欄位，明示覆蓋哪些歷史慣例；若 Worker memory 有與本工單衝突的慣例但未明示覆蓋，執行時有違規風險（參見 [skill-writing-conventions.md](skill-writing-conventions.md) § 棄用條款寫法規範）

## 任務指令

### 方法論工作流程
（v6.0.0+。沒有任何層由方法論 adapter 負責時刪除本段；何時要寫、內容是什麼見 `methodology-adapters.md` § 工單欄位，
填法與範例見下方「填寫方法論欄位指引」。frontmatter `methodology` 是 SoT，本段是人讀鏡像）
- <層>：`<adapter>` / `<workflow>`（<adapter `workorder.annotations` 宣告的標注>）
- <層>：`<adapter>` / `<workflow>`

<adapter `workorder.required_when` 指定的段落；例：bmad `bmad-build-auto` → `### Autonomous Contract`，欄位見 `adapters/bmad.yaml`>

### 方法論邊界
（何時寫見 `methodology-adapters.md` § 工單欄位 › 內文段落：`methodology_guard: warn` 時塔台自動加（沒有 `methodology` 的工單也加）、
adapter `required_when` 要求、本單開放方法論子代理寫入、或本單要用 `methodology-adapters.md` § 引入方式 ③ 的本地副本；否則刪除。本段是邊界段範本的**唯一一份**，措辭照 V1 實測版
（`spec/方法論介接/verification/V1-pstack-ct-exec.md` § 7.2），V2b（`verification/V2b-dual-injection.md` § 7.2）改成由各家 adapter 填值並加通用條文。
第一條：本單有層由 adapter 負責 → 【只允許】；注入開著、但不負責本單任何一層的方法論 → 【不使用】，**每一家都列**；兩種都有就兩項都寫，【只允許】在前。
其餘照抄。`<…>` 換成實際值，每家的值取自它的 adapter（`methodology-adapters.md` § 與 hook／session 路由的相處規則 第 2 點）：
`<skill 樣式>` = `session.skill_patterns`、`<入口 skill>` 與 `<注入條件摘要>` = `session.hooks[].entry_skills`、`trigger_summary`、
`<範圍外產物例子>` = 本單相關 adapter `artifacts.writes` 的聯集）
- 【不使用】本單**不使用**下列方法論的任何 skill；它們的 SessionStart 注入要 session 先叫某個 skill 的指示**不適用本單**：
  - `<skill 樣式>`（注入：「<注入條件摘要> → 先叫 <入口 skill>」）
  - （每一家注入開著、且不負責本單的方法論各一行）

  本段就是使用者的明確指示，依注入文字自己寫的「User instructions ... take precedence」優先。
- 【只允許】本單**只允許** `<skill 清單>`（含上列 skill 自己呼叫的子 skill 與它們自帶的唯讀審查子代理，回報照實寫；子 skill 取自 adapter `session.subagents.ct_rule`）；其他 `<skill 樣式>` skill 一律不用（例：`<要停用的 playbook 或 skill>`）。SessionStart 注入的「<注入條件摘要> → 先叫 <入口 skill>」指示只在上述 skill 的範圍內適用：本段就是使用者的明確指示，依注入文字自己寫的「User instructions ... take precedence」優先。
  （§ 引入方式 ③ 的本地副本沒有 adapter：`<skill 清單>` 寫副本路徑，沒有注入就省略注入那一句。例：「本單**只允許** `.claude/skills/mp-tdd/SKILL.md`（mattpocock/skills `tdd` 的本地副本，見 `methodology-adapters.md` § ③ 的做法）；其他 `.claude/skills/mp-*` 副本一律不用。」）
- 方法論 skill 要求先問使用者或等使用者核准（例：設計核准前不准實作的硬閘門、規格釐清提問、建 worktree 前徵求同意）時，不得因此問使用者或停下等待；需要決策時照 ct-exec 的規則處理（`CT_MODE=yolo` 時問塔台）。
- 實作直接由主 Worker 照 ct-exec 流程完成；子代理只能唯讀，不開寫入型子代理，也不另開背景子代理（`methodology.subagent_writes: deny`）。上列 skill 自帶的唯讀審查子代理（含背景，adapter `session.subagents.only_in`、`background`）除外：回報區照實寫子代理數、是否背景、子代理內呼叫的 skill。
  （開放寫入時改成「子代理寫入只限本單〈方法論子代理授權〉表列；表外只能唯讀」，授權段放在 `## 元資料` 之後，見下方「撰寫方法論子代理授權」）
- 不開分支、不建 worktree、不 push、不開 PR、不 `git reset`（交付層 `methodology.delivery: none`）。
  （交付層由使用者授權開放時，改成只列本單允許的交付動作；push 仍要本單明寫使用者授權）
- 不在 `affects_files` 以外產生檔案（例：<範圍外產物例子>）；方法論要留的工作檔放 Worker scratchpad，沒有 scratchpad 時（headless `claude -p`、Codex、一般終端機）放系統暫存目錄（`$TMPDIR`／`%TEMP%`）下的 `ct-<工單號>/`，收尾刪除。收尾時 repo 外不留檔（不寫 repo 上一層或其他目錄）。
- 回報區照本工單模板，用<工單語言>；不套 <方法論的寫作風格規則，例：unslop> 寫法。
- 若仍呼叫了任何方法論 skill，在回報區 `### 方法論執行紀錄` 寫明哪個 skill、在哪一步、做了什麼、跳過什麼。
- compact 或 resume 之後，先重讀本工單（含本段）再繼續。

### 前置條件
需載入的文件清單：
- <文件 1>
- <文件 2>

### 輸入上下文
（由指揮塔整理的精簡上下文，sub-session 不需要回塔台問背景）

<專案描述、技術棧、目前進度、具體任務說明>

### 預期產出
- <產出檔案或交付物 1>
- <產出檔案或交付物 2>

### 相關通過案例（僅 `customer_acceptance_gate: on` 且本單會改程式或資料，v6.0.0-beta.3+）
（不適用就刪除本段。寫法與 Worker 做法見本檔 § 撰寫〈相關通過案例〉）
- 驗收案例表：<位置>
- 改動範圍：<模組／畫面／資料表>
- 相關且結果為通過的案例：<案例編號清單，由塔台初列；Worker 動工前補齊並逐案判定>

### 驗收條件
- [ ] <條件 1>
- [ ] <條件 2>
- [ ] <條件 3>

## Sub-session 執行指示

> **重要**：請在開始工作前，將「開始時間」填入當前時間。
> 完成後請填寫「回報區」。無論成功、失敗或需要後續指示，都必須填寫。

### 執行步驟
1. 讀取本工單全部內容
2. 更新「開始時間」欄位
3. 載入前置條件中的文件
4. 依照任務指令執行
5. 完成後填寫回報區
6. 更新「狀態」（DONE / FAILED / BLOCKED / PARTIAL）
7. 更新「完成時間」
8. 若工單有 `methodology.writeback`，或主方法論有 tracker（bmad 時為 `sprint-status.yaml`），依 adapter 規則回寫，結果寫進回報區 `### 方法論狀態回寫`

---

## 回報區

> 以下由 sub-session 填寫，請勿在指揮塔 session 中編輯（唯一例外：`### 待塔台決策` 的 `塔台答覆 Q-n` 行由塔台新增）

### 待塔台決策（僅 yolo Worker 有問題時，v5.5.0+）
（沒有提問就刪除本段；研究型工單同樣適用。格式、等待與備援以 `yolo-mode.md` § Worker 向塔台提問 為準）
#### Q-1：<一句話問題>
- 提問時間：<取自系統，取值方式見 `yolo-mode.md` § Worker 端 第 2 點>
- 選項：[A] … / [B] … / [C] 其他：________
- Worker 建議：
- 影響範圍：
- 阻塞：是 / 否
（`塔台答覆 Q-1` 行由塔台新增，Worker 不預寫；改等工單答覆的題，Worker 在題目最後加一行 `- **通道**：工單`：`--ask` 失敗的題 v5.7.1 起、`--ask` 成功後才退回的題 v5.7.2 起，見 `yolo-mode.md` § Worker 端 3-A 第 2、6 步）

### 完成狀態
（DONE / FAILED / BLOCKED / PARTIAL）
- **session_id**：<本 session 的 `CLAUDE_CODE_SESSION_ID`，或 `unavailable`>（v6.0.0-beta.10+；frontmatter `session_ids` 的鏡像，見 `ct-exec/SKILL.md` § Phase 4 › Session id）

### 產出摘要
（列出產生的檔案、修改的檔案、關鍵變更）

### 互動紀錄
（記錄執行過程中與使用者的重要互動，包括：
  - 需要使用者確認的決策及結果
  - 使用者提供的額外資訊或偏好
  - 執行過程中的方向調整
  格式：[時間] 問題 → 使用者回覆 → 採取行動）

### Renew 歷程
（若有 Renew 則記錄每次 Renew 的摘要，無則填「無」）

### 遭遇問題
（若有問題或需要指揮塔介入的事項，在此描述）

### 相關通過案例判定（僅工單有〈相關通過案例〉段時）
| 案例 | 判定（不受影響／受影響但預期不變／會改變） | 理由 |
|---|---|---|

### 方法論執行紀錄
（有任何層由方法論 adapter 負責、本 session 呼叫了任何方法論 skill、或看到方法論注入時填；都沒有就刪除本段。
內容與格式見 `methodology-adapters.md` § 工單欄位 › `### 方法論執行紀錄` 的內容：`methodology_ambient` 行、方法論 skill 使用表、
adapter `status_mapping.required_report` 逐項與狀態對應）
- **methodology_ambient**：<none／<adapter id>（<事件>；標記「<一句原文>」）>

### 方法論狀態回寫
（有 `methodology.writeback` 或主方法論有 tracker 時填：回寫了什麼、寫在哪（bmad 時為 `sprint-status.yaml`、story spec `status`）；
都沒有就填「不適用」。舊工單的 `### sprint-status.yaml 已更新` 段照讀，等同本段）

### 隔離分支證據（僅 `isolation: worktree` 工單，v5.3.0+）
（非隔離工單刪除本段。欄位定義與取值方式以 `ct-exec/SKILL.md` § Worktree Isolation 第 7 點為準）
- branch：`ct/T<編號>`
- base_sha：
- validated_sha：
- head_sha：
- validated_sha ≠ head_sha 的說明：（相同則填「相同」）

### 回報時間
（填入當前時間）
```

> **Renew 支援**：一般工單也可由塔台 Renew。塔台在回報區 `---` 之前插入 `## 塔台補充（Renew #N）` 區段,
> 並更新元資料加入 `Renew 次數` 欄位。Worker 偵測觸發詞後增量讀取新指示。
> 完整 Renew 格式見 [research-workorder.md](research-workorder.md) § Renew 機制。
> Worker 還在 `IN_PROGRESS` 時要補充或修正指示，不用 Renew，改寫 `## 塔台補充（執行中 #N）`（v6.0.0-beta.11+，不加 `Renew 次數`）；
> 寫法只定義在 [work-order-system.md](work-order-system.md) § 執行中補充工單。Worker 讀到後記在 `### 互動紀錄`，回報區不新增段落。

### 填寫 `intervention_type` 指引

`intervention_type` 在工單元資料明文標註 Worker 的互動行為策略,讓使用者心理預期明確,也讓 Worker 行為有依據。三種值:

| 值 | 定義 | Worker 行為 |
|----|------|------------|
| `fire-and-forget` | Worker 全程自動,不打斷使用者 | 遇到卡點先嘗試三次(熔斷),三振才回報 |
| `context-dependent` | Worker 需讀取特定 context(使用者的 session 歷史 / 其他工單 / 環境設定)才能判斷 | 若 context 不足可主動提問一次,之後自動完成 |
| `decision-requiring` | Worker 執行到特定節點必須等使用者決策 | 達到 decision point 明確停下,選項式提問,等回覆才繼續 |

**何時選哪一個**:

- **預設 `fire-and-forget`**:無狀態工單、純執行型(模板套用、檔案重構、明確 bug 修復)
- **選 `context-dependent`**:工單需要 Worker 理解使用者**未寫在工單內的偏好或歷史**(例:命名風格、慣用元件、過往決策)。context 缺失時允許主動提問**一次**釐清,之後自動完成
- **選 `decision-requiring`**:工單包含**分叉點**,不同選擇導致不同後果(例:A 方案 vs B 方案,影響整個架構)。達到 decision point 必須停下等使用者
- **與規格層級自問的關係**(T0101):若「決策權歸屬」有 X 回答「否」→ 考慮標 `decision-requiring`

**與 `類型` 欄位(research)的關係**:

| `類型` | 常見 `intervention_type` | 說明 |
|--------|--------------------------|------|
| `execution` / `documentation` / 其他 | 通常 `fire-and-forget` | 現有行為不變 |
| `research` | 通常 `context-dependent` 或 `decision-requiring` | 研究型工單本來就允許互動(由「互動模式」開關控制),`intervention_type` 是**更細的行為描述**——指出互動是「補 context」還是「等決策」 |

兩套機制不衝突:`類型: research` + `互動模式: enabled` 決定是否允許互動,`intervention_type` 決定互動的**觸發時機與目的**。

**向下相容**:

- 未含 `intervention_type` 的舊工單,Worker 視為 `fire-and-forget`
- Phase 2 不強制填寫,Phase 3 審視是否升級為強制欄位

### 填寫 `affects_files` 指引

`affects_files` 在工單元資料明文標註 Worker 預期會「寫入 / 修改 / 刪除」的檔案清單，讓塔台在派發前能做 **static overlap check**，及早攔截平行工單互相覆蓋或產生 merge conflict 的高風險組合。完整派發邏輯見 [work-order-system.md](work-order-system.md) § 派發前 overlap check。

**填寫原則**：

- **只列寫入目標**：Worker 會對哪些檔案做 **寫入 / 修改 / 刪除**。單純讀取的檔案（前置條件載入）**不算**，不要列入。
- **使用相對路徑**：以專案根目錄為基準（例：`control-tower/SKILL.md`、`_ct-workorders/_tower-state.md`）。
- **不含專案前綴**：mono-repo 中的子專案路徑已由 `目標子專案` 欄位補足，`affects_files` 維持相對於工單所在專案根的路徑。
- **巢狀的獨立 repo**（v6.0.0-beta.7+；子專案各有自己的 `.git`，工單集中在上層）：一樣從上層（工單所在專案根）寫起，包含子 repo 的目錄（例 `src/app-frontend/src/login.ts`）；Worker 在子 repo commit 時要去掉子 repo 前綴，見 [mono-repo-patterns.md](mono-repo-patterns.md) § 巢狀的獨立 repo。

**標註粒度**：

| 粒度 | 寫法 | 使用時機 |
|------|------|---------|
| 檔案層（預設） | `path/to/file.md` | Worker 明確知道會改哪些檔 |
| 目錄層 | `_ct-workorders/*` | Worker 會在目錄下建立多張新檔但名稱未定（例：批次生成工單） |
| 全專案 | `*` | 極少數：全局重構、rename 專案範圍內所有檔 |

**無法預測時**：

- 寫「待 Worker 執行期間確認」作為單一項目，塔台派發時視為 `*`（保守 WARN）
- Worker 在回報區「產出摘要」補上實際動過的檔案清單，供 \*evolve 事後歸納

**`_tower-state.md` 特殊註記**：

- 塔台自身會自動更新 `_tower-state.md`，**Worker 工單通常不列入** `affects_files`
- 例外：若工單目標本身就是改塔台狀態快照格式（如本工單 T0103 的 AC-6），才明文列入並在工單註解說明

**範例**：

```markdown
- **affects_files**:
  - `control-tower/SKILL.md`
  - `control-tower/references/work-order-template.md`
  - `control-tower/references/work-order-system.md`
```

研究型工單建議寫法：

```markdown
- **affects_files**:
  - `無寫入`                              # 純調查，不產出檔案
  # 或
  - `_ct-workorders/T####-research-report.md`  # 若產出獨立報告檔
```

**向下相容**：

- 未含 `affects_files` 的舊工單，塔台派發前視為 `*`（保守假設）→ 任何平行派發都 WARN
- 這個保守預設會**鼓勵**使用者補填新工單的 `affects_files`
- Phase 2 不強制填寫；Phase 3 審視是否升級為強制欄位

**與 static overlap check 的失真容忍**：

- 宣告值與 Worker 實際動的檔案若有落差（Worker 動了更多），**不是本機制責任**；塔台僅以字面內容做比對
- 落差素材由 \*evolve 掃描歷史工單的「回報區 vs `affects_files`」差異，作為歸納的觀察點

### 填寫 `memory_overrides` 指引

`memory_overrides` 用於在工單元資料**明示覆蓋**與 Worker 歷史慣例 / 全局記憶 / `~/.claude/CLAUDE.md` / auto memory 衝突的指令。目的是把「記憶 vs 工單特例」的選擇權從 Worker 隱性判斷拉到工單顯性宣告，降低 Worker 執行時依賴舊慣例而違反當前工單意圖的風險（根因見 [skill-writing-conventions.md](skill-writing-conventions.md) § 棄用條款寫法規範）。

**填寫時機**：

- 本工單指令與 `~/.claude/CLAUDE.md` 或 skill 內既有規則明顯衝突
- 本工單要改變 Worker 已執行過多次的慣例（例：原本全局同步某目錄，本工單只改 dev snapshot）
- Worker memory 中可能殘留舊版 skill 的行為（例：v4.3.x 允許 X，v4.4.x 改為嚴禁 X）

**無衝突可省略**：大多數工單不需填寫此欄位。

**三欄格式（必須同時標註）**：

```markdown
- **memory_overrides**：
  - ❌ 「舊慣例 A 的文字描述」→ 本工單處理：嚴禁。棄用理由：<具體理由>
  - ✅ 「沿用規則 B 的文字描述」→ 本工單處理：沿用。理由：<具體理由>
```

| 欄位 | 說明 |
|------|------|
| 歷史慣例（引號內文字） | Worker 可能從 memory 或舊版 skill 帶入的慣例，用使用者能認出的語氣描述 |
| 本工單處理 | 三擇一：嚴禁 / 沿用 / 變更為…… |
| 棄用理由 / 沿用理由 | 一句話說明為何這樣選；與 `skill-writing-conventions.md` 的棄用條款呼應 |

**與 spec_level_check 第 5 項的連動**：

- 若自問第 5 項回答「是」（有衝突）→ **必填** `memory_overrides`
- 未填則派發前塔台可提醒「疑似記憶衝突但未覆蓋宣告」
- Worker 執行時若發現 memory 帶入的慣例不在 `memory_overrides` 明示清單內，應以工單當前指令為準並在回報區記錄落差（GP078 相關）

**向下相容**：

- 未含 `memory_overrides` 的舊工單，Worker 行為不變（按歷史慣例執行）
- 此欄位**不對既有工單 retrofit**
- Phase 2 為可選欄位，Phase 3 視使用情況再決定是否升級為強制

**範例**：

```markdown
- **memory_overrides**：
  - ❌ 「發 ct-evolve 要同步更新 Layer 1 安裝品」→ 本工單處理：嚴禁。棄用理由：見 `data-layer-architecture.md` § 寫入規則（唯一權威定義）
  - ✅ 「改動後要補 commit」→ 本工單處理：沿用。理由：保留工單 commit 慣例
  - ❌ 「輸出整組環境變數或 `BAT_REMOTE_TOKEN` 的值」→ 本工單處理：嚴禁。棄用理由：偵測照 `auto-session.md` § BAT 內部終端路由 › 偵測條件 只列名稱；該節明列的例外（`CT_MODE`／`CT_INTERACTIVE`／`BAT_WORKSPACE_ID`／`CT_HOME`／`CT_WORKTREE_*`）可單獨讀；唯一可以**寫進工單**的值是 `CLAUDE_CODE_SESSION_ID`（v6.0.0-beta.10+，`ct-exec/SKILL.md` § Phase 4 › Session id）
```

**環境變數的標準寫法**（D385、D388）：要在 `memory_overrides` 提醒 Worker 不外洩環境變數時，照上面範例第三條寫：引用
[auto-session.md](auto-session.md) § BAT 內部終端路由 › 偵測條件（只列名稱），並註明該節的明列例外可單獨讀（一個變數一個指令）。
不要寫「嚴禁輸出任何環境變數的值」：它比權威規則嚴，會和 `ct-exec` 讀 `CT_MODE`／`CT_INTERACTIVE` 判斷模式、落點檢查記錄 `BAT_WORKSPACE_ID` 衝突，Worker 照規則做也會被判違反（T0320、T0323 因此 PARTIAL）。

### 撰寫 verification 工單的驗收步驟

> 本小節是**驗收步驟設計**指引，只管工單怎麼寫。**此為驗收設計，不改變 CT 執行時判斷只看 exit code 的規則**
> （見 [auto-session.md](auto-session.md) § BAT 派發成功判讀規則、§ BAT 內部終端路由 › 範圍權杖與分頁角色 第 5、6 點）。
> 由來：T0150。

1. **「預期被拒」的步驟**：payload 必須先能通過 helper 的本地參數驗證，才測得到 server 端的拒絕。
   helper 本地驗證失敗與權限拒絕都是 exit `1`，只看 exit code 會把「根本沒送出」誤判成「被拒絕」。
   - 例：`bat-terminal.mjs --skill` 只收 `ct-exec`／`ct-done`。要測權限拒絕時，改用 `--prompt "/ct-status T####"` 這類唯讀 payload
     （萬一被誤放行，開出的也只是唯讀的 ct-status）；不要改用 `--skill ct-exec`／`ct-done`，誤放行時會多開一個執行或收尾該工單的 Worker。
   - 驗收紀錄要**同時**寫 exit code 與 stderr 關鍵字（例 `Forbidden: role-not-allowed`），兩者都符合才算通過。
     stderr 在這裡只用來確認驗收打到了目標。
2. **要求使用者在某個分頁操作的步驟**：用分頁標題描述（例「在 `Claude CLI · Worker · T####` 分頁執行 …」），不要用 terminal ID；
   規則見 [auto-session.md](auto-session.md) § 對使用者描述分頁。
3. **驗收「在 Worker 分頁啟動塔台」這類行為之前**：先請使用者在該分頁 `/clear`（或開新 session）。
   帶著工單 context 的 session 已經知道預期結果，跑出來的行為不能當作規格行為的證據。
4. **段落分給 Worker 與塔台的工單**（v5.6.1，T0167）：開單時在工單寫明哪些段落屬塔台、哪些屬 Worker
   （例段落標題寫「段 A —— 塔台：…」「段 B —— Worker：…」，回報區開頭註明「段 B 由 Worker 填寫；段 A、C 由塔台補記」）。
   Worker 的完成狀態**只就 Worker 段落判定**：塔台段落在工單裡還沒有證據，不構成 `PARTIAL`，留給塔台補記
   （Worker 端同一條規則在 `ct-exec/SKILL.md` § Phase 4 › Status rules 之後）。

### 撰寫〈相關通過案例〉（客戶驗收不回歸閘，v6.0.0-beta.3+）

本小節是客戶驗收不回歸閘的**唯一權威定義**；開關 `customer_acceptance_gate` 的有效值與預設在 [tower-config.md](tower-config.md) § 可用選項。

**這是可選規則，預設 `off`**。它只對已經進入客戶驗收、手上有驗收案例表（每個案例有編號與通過／不通過結果）的專案有意義；
其他專案沒有案例表可比對，開了只會多一段空白。專案進入客戶驗收時，由使用者決定開啟（`*config customer_acceptance_gate on --save project`），
並把案例表的位置寫進 `_local-rules.md` 或每張工單的〈相關通過案例〉段。

`on` 時：

1. **塔台開單**：會改程式或資料的工單加〈相關通過案例〉段（上方範本 § 任務指令），寫案例表位置、改動範圍、塔台初列的相關通過案例。
   只改文件、只讀的研究單不加。
2. **Worker 動工前**：從案例表找出與改動範圍相關、結果為**通過**的案例，補齊清單，逐案判定：
   - **不受影響**：改動碰不到這個案例的步驟或資料
   - **受影響但預期不變**：改動碰得到，但案例的預期結果與畫面不變（寫理由）
   - **會改變** ⇒ **停下**，不動工，交使用者裁示（yolo：照 `ct-exec/SKILL.md` § Questions For Tower 問塔台，塔台轉問使用者）
3. **回報區**：必填 `### 相關通過案例判定` 表；沒有相關通過案例也要寫「無」與查找範圍。
4. **部署後走場**：塔台把這些案例列進部署後必跑清單（部署或驗證工單的驗收條件）。
5. **已完成的修正**：開啟時已經完成、還沒部署的修正工單，塔台另開一張唯讀核對單，照第 2 步回溯判定。

### 撰寫 Workflow 使用授權（v5.11.0+）

> 本小節只是**塔台寫授權段落的範本**。Worker 怎麼依授權執行、超出時怎麼停、回報區記什麼，權威在 `ct-exec/SKILL.md` § Workflow And Sub-Agents；
> 塔台什麼時候可以寫、要不要先問使用者，依 `workflow_integration`，見 [workflow-engine.md](workflow-engine.md) § `workflow_integration` 的行為、§ 同意治理。
> 由來：T0182 的寫法（D087），T0183 收進範本。

- 🔴 `workflow_integration` 生效值是 `off` 時**不得寫**這個段落；工單沒有這個段落，Worker 就不會呼叫 Workflow 工具。
- 只派給 Claude Code Worker（`--agent` 不得是 codex；Codex 不支援 Workflow）。
- 每一列都要能事前列出：執行哪個 workflow（或腳本）、用什麼資料、agent 上限、token 事後上限。寫不出上限就不要授權。

放在 `## 元資料` 之後：

```markdown
- **Workflow 使用授權**：🟢 本單授權 Worker 呼叫 Workflow 工具，**僅限**下表的執行，規模為使用者 <時間> 核准的上限（D###）。
  超出任何一項上限，或要做下表以外的執行（含重跑），**先停，向塔台提問**。只派 Claude Code Worker。

## 核准的執行（上限）

| # | workflow | 資料 | agent 上限 | token 事後上限 |
|---|---|---|---|---|
| 1 | <name 或 `.claude/workflows/<name>.js`> | <args 摘要> | <N> | <N> |
```

Worker 回報區的 `### 子代理與 Workflow 使用` 由 Worker 依 `ct-exec` 填寫；不必預先放進模板。

### 填寫方法論欄位指引（v6.0.0+）

> 本小節只是**塔台寫方法論欄位的範本與範例**。欄位與段落的定義、何時要寫、狀態怎麼對應、怎麼降級，唯一權威在
> [methodology-adapters.md](methodology-adapters.md)（§ 工單欄位、§ 舊欄位相容、§ 狀態對應總則、§ 降級、§ 衝突與防護）；
> 每層由誰負責依該檔 § 解析步驟 算出，派工流程見 [work-order-system.md](work-order-system.md) § 派發流程 第 2 步。由來：T0301（I2，D333）。

- frontmatter `methodology` 是機器 SoT；內文 `### 方法論工作流程` 是人讀鏡像，兩者要一致（drift 時照 § Body metadata mirror 注意事項，以 frontmatter 為準）。
- 解析結果**沒有任何層由 adapter 負責**（`methodology: none`、adapter 都沒安裝，或全部降級成自由文字；或主方法論對本單需求的入口是 `workflow: none`）→ 不寫 `methodology`、
  不寫 `### 方法論工作流程`，工單與 v5.12.6 相同。兩個例外：
  - 主方法論有 `tracker`（bmad：`sprint-status.yaml`）→ 回報區**保留** `### 方法論狀態回寫`（等同 v5.12.6 一律有的 `### sprint-status.yaml 已更新`；用不到時 Worker 填「不適用」），
    與 `methodology-adapters.md` § 工單欄位 › 內文段落 的「有 `writeback` 或主方法論有 `tracker`」一致（P-1，T0314）。`methodology: none` 沒有主方法論，不保留。
  - `methodology_guard: warn` 偵測到注入時照樣加 `### 方法論邊界`（【不使用】變體；`methodology-adapters.md` § 與 hook／session 路由的相處規則 第 2 點）。
- adapter `artifacts.writes` 會寫到的檔放進 `affects_files`，或在 `### 方法論邊界` 指定放 Worker scratchpad（§ 衝突與防護 C7）；有 `writeback` 時，回寫目標也要在 `affects_files`。
- 段名用「方法論工作流程」；Workflow 工具的授權段維持「Workflow 使用授權」，兩者不要混用（§ 衝突與防護 C13）。

#### 範例 A：抽換（專案主方法論改用 pstack）

專案設定 `methodology: pstack`（其他層 `inherit`）；需求「登入失敗時錯誤訊息沒顯示」，`request_kind: bugfix`。
pstack 的欄位值取自它的 adapter（CT 官方外部 skill `ct-adapter-pstack`，原始碼在 `adapters/ct-adapter-pstack/adapter.yaml`）。

```yaml
methodology:
  request_kind: bugfix
  resolved_from:                   # 每層各記來源（methodology-adapters.md § 工單欄位）
    execution: project             # inherit → 主方法論 pstack，來自 project
    review: project
  layers:
    execution:
      adapter: pstack
      workflow: pstack:poteto-mode
      detail: Bug fix playbook
    review:
      adapter: pstack
      workflow: pstack:thermos
  versions:
    pstack: "upstream 0.9.103 / adapter 0.2.5"
  subagent_writes: deny
  delivery: none
```

```markdown
### 方法論工作流程
- execution：`pstack` / `pstack:poteto-mode`（playbook：Bug fix）
- review：`pstack` / `pstack:thermos`

### 方法論邊界
- 本單**只允許** `pstack:poteto-mode`（Bug fix playbook）、`pstack:thermos`（含 `pstack:thermos` 自己呼叫的子 skill 與它自帶的唯讀審查子代理，回報照實寫）；其他 `pstack:*` skill 一律不用（例：Opening a PR、Babysit、Shipping、Autopilot-*、Orchestrate playbook）。SessionStart 注入的「多檔、設計選擇、原因未知的 bug → 先叫 `pstack:poteto-mode`」指示只在上述 skill 的範圍內適用：本段就是使用者的明確指示，依注入文字自己寫的「User instructions ... take precedence」優先。
- 方法論 skill 要求先問使用者或等使用者核准（例：設計核准前不准實作的硬閘門、規格釐清提問、建 worktree 前徵求同意）時，不得因此問使用者或停下等待；需要決策時照 ct-exec 的規則處理（`CT_MODE=yolo` 時問塔台）。
- 實作直接由主 Worker 照 ct-exec 流程完成；子代理只能唯讀，不開寫入型子代理，也不另開背景子代理（`methodology.subagent_writes: deny`）。上列 skill 自帶的唯讀審查子代理（含背景，adapter `session.subagents.only_in`、`background`）除外：回報區照實寫子代理數、是否背景、子代理內呼叫的 skill。
- 不開分支、不建 worktree、不 push、不開 PR、不 `git reset`（交付層 `methodology.delivery: none`）。
- 不在 `affects_files` 以外產生檔案（例：`todo.md`、`.audit/`、`decisions.tsv`）；方法論要留的工作檔放 Worker scratchpad，沒有 scratchpad 時（headless `claude -p`、Codex、一般終端機）放系統暫存目錄（`$TMPDIR`／`%TEMP%`）下的 `ct-<工單號>/`，收尾刪除。收尾時 repo 外不留檔（不寫 repo 上一層或其他目錄）。
- 回報區照本工單模板，用繁體中文；不套 unslop 寫法。
- 若仍呼叫了任何方法論 skill，在回報區 `### 方法論執行紀錄` 寫明哪個 skill、在哪一步、做了什麼、跳過什麼。
- compact 或 resume 之後，先重讀本工單（含本段）再繼續。
```

`### 方法論邊界` 在這裡是必寫的：pstack 的 `workorder.required_when` 對 `pstack:poteto-mode` 要求它，而且 pstack 有 SessionStart 注入（C1）；pstack 是本單負責者，所以用【只允許】變體。
`pstack:*`、入口 skill 與注入條件摘要取自 pstack adapter 的 `session.skill_patterns`、`session.hooks[].entry_skills`、`trigger_summary`；範圍外產物例子取自它的 `artifacts.writes`。
另有不負責本單的方法論注入開著時，照範本在第一條之後加【不使用】項（`methodology-adapters.md` § 與 hook／session 路由的相處規則 第 2 點）。
回報區 `### 方法論執行紀錄` 填 `methodology_ambient` 行（本單有 `methodology`，一律寫）、方法論 skill 使用表與 pstack `status_mapping.required_report` 的項目；pstack 沒有 `tracker`、本單沒有 `writeback`，`### 方法論狀態回寫` 填「不適用」。

#### 範例 B：疊加（規劃 bmad、執行 pstack）

專案設定 `methodology: bmad`、`methodology_execution: pstack`（`methodology_review: inherit` → bmad）；需求「會員可以用 Passkey 登入」，`request_kind: feature`。
先派一張規劃工單（`layers.planning: {adapter: bmad, workflow: bmad-spec}`，產出 `<spec-folder>/SPEC.md`、`stories.yaml` 與 story spec），
每個 story 再派一張執行工單，下面是其中一張：

```yaml
methodology:
  request_kind: feature
  resolved_from:
    execution: project             # methodology_execution: pstack，project 明寫
    review: project                # inherit → 主方法論 bmad，來自 project
  layers:
    execution:
      adapter: pstack
      workflow: pstack:poteto-mode
      detail: Feature playbook
    review:
      adapter: bmad
      workflow: bmad-code-review
  inputs:
    - kind: story-spec
      from_adapter: bmad
      path: <spec-folder>/stories/2-passkey-register.md
  writeback:
    adapter: bmad
    target: <spec-folder>/stories/2-passkey-register.md frontmatter status、sprint-status.yaml（有用時）
  versions:
    bmad: "upstream 6.12.4 / adapter 0.2.0"
    pstack: "upstream 0.9.103 / adapter 0.2.5"
  subagent_writes: deny
  delivery: none
```

```markdown
### 方法論工作流程
- execution：`pstack` / `pstack:poteto-mode`（playbook：Feature；目標 = 實作 `<spec-folder>/stories/2-passkey-register.md`）
- review：`bmad` / `bmad-code-review`（Reference：bmad-guide v6.12.4 `workflow-map.md` § Review Triage）
- 輸入：bmad story spec `<spec-folder>/stories/2-passkey-register.md`
- 回寫：完成後把該 story 的 frontmatter `status` 改成 `done`（失敗改 `blocked` 並寫原因）；有用 `sprint-status.yaml` 時一併更新

### 方法論邊界
（同範例 A，第一條的清單改成 `pstack:poteto-mode`（Feature playbook）與 `bmad-code-review`；其他 `pstack:*`、`bmad-*` skill 一律不用）
```

- 交接：bmad `handoff.produces` 的 `story-spec` 對上 pstack `handoff.consumes` 的 `story-spec`；回寫由產生產物的 bmad 的 `handoff.writeback` 決定（`by: worker-step`），所以執行步驟要有回寫這一步，塔台收單時複查（`work-order-system.md` § 主方法論 tracker 同步）。
- 取捨：執行層不是 bmad，`bmad-build` 內建的 Review Triage 不會跑；派工摘要要提示（`methodology-adapters.md` § 分層疊加 第 5 點）。審查也要用 pstack 就設 `methodology_review: pstack`。
- `affects_files` 要含 story spec 與 `sprint-status.yaml`（回寫目標）。回報區 `### 方法論執行紀錄` 填 pstack 與 bmad 各自的 `required_report`，`### 方法論狀態回寫` 寫 story `status` 與 tracker 改了什麼。

#### 範例 C：只有舊 `### BMad 工作流程` 段的舊工單（照讀）

v6.0.0-pre.1 之前開的工單沒有 `methodology` frontmatter，只有：

```markdown
### BMad 工作流程
bmad-build（若未安裝 BMad-Method，依下方步驟手動執行）

可選標注（若外部 `bmad-guide` 可用）：
- Agent: bmad-agent-dev
```

- 照 `methodology-adapters.md` § 舊欄位相容 讀：視為 `layers.<層>.adapter = bmad`，層照該節「由 workflow 推得的層」的規則推（本例 `bmad-build` → `execution`；
  退役名 `bmad-dev-auto` 先經 `retired_names` 換成 `bmad-build-auto` 再推；都查不到 → 當自由文字）。
- **不回寫舊工單**：不補 `methodology` frontmatter、不把段名改成 `### 方法論工作流程`。重派或 Renew 時也一樣，只有新開的工單用新段落。
- Worker 對沒有 `methodology` 欄位的工單，行為與 v5.12.6 完全相同。
- 舊回報區的 `### sprint-status.yaml 已更新` 等同 `### 方法論狀態回寫`，`*sync` 與收單照讀。

### 撰寫方法論子代理授權（v6.0.0+）

> 規則在 [methodology-adapters.md](methodology-adapters.md) § 衝突與防護 C4：預設 `deny`，工單寫「子代理只能唯讀」；要開放寫入才加本段。
> 本小節只是段落位置與骨架。這不是 Workflow 工具的授權（上方「撰寫 Workflow 使用授權」），兩段各自獨立。

- 只有專案設定 `methodology_subagent_writes: per-workorder` 時才可以寫；生效值是 `deny` 時**不得寫**。`per-workorder` 時沒寫本段的工單，
  frontmatter 照預設寫 `subagent_writes: deny`（`methodology-adapters.md` § 抽換、§ 衝突與防護 C4）。
- 寫了本段，frontmatter 改 `methodology.subagent_writes: authorized`，`### 方法論邊界` 的子代理一行改成「見本單〈方法論子代理授權〉」。
- Worker 照本段執行、超出時停下並向塔台提問、回報區記什麼：`ct-exec/SKILL.md` § Methodology › 方法論子代理。

放在 `## 元資料` 之後（有 `Workflow 使用授權` 時接在它後面）：

```markdown
- **方法論子代理授權**：🟢 本單授權下表的方法論子代理寫入，**僅限**下表，規模為使用者 <時間> 核准的上限（D###）。
  超出上限或要做下表以外的寫入，**先停，向塔台提問**。worktree 一律走 BAT `--isolation worktree`，不用方法論自建的 worktree。

| # | adapter / workflow | 用途 | 子代理上限 | 寫入範圍（須在 `affects_files` 內） | 可否 commit |
|---|---|---|---|---|---|
| 1 | <id> / <workflow> | <用途> | <N> | <路徑> | 否 |
```

## 研究型工單模板

當問題根因不明、需要多輪互動釐清、或方向不確定時，使用此模板。
Worker 進入研究模式，允許主動提問。完整規格見 [research-workorder.md](research-workorder.md)。

```markdown
# 工單 T<編號>-research-<description>

## 元資料
- **工單編號**：T<編號>
- **任務名稱**：研究：<問題描述>
- **狀態**：PENDING
- **類型**：research
- **互動模式**：enabled
- **intervention_type**：context-dependent / decision-requiring（研究型工單通常二擇一；詳見「填寫 intervention_type 指引」）
- **affects_files**（v4.4.0+，可選；研究工單通常只讀不寫，可填 `無寫入`；若會產出建議清單或報告檔則列出）：
  - `<相對路徑或「無寫入」>`
- **Renew 次數**：0
- **建立時間**：<當前時間> (UTC+8)
- **開始時間**：（sub-session 開始時填入）
- **完成時間**：（完成時填入）

## 研究目標
<塔台整理的問題描述——要釐清什麼問題 / 要調查什麼方向>

## 已知資訊
<目前掌握的線索、症狀、相關文件>

## 調查範圍
<建議調查的檔案、模組、技術方向>

## 研究指引
<建議的調查方向、可參考的文件、評估維度>

## 互動規則
- Worker 可主動向使用者提問以縮小範圍
- 每次提問不超過 research_max_questions 個問題（塔台 config 值；有效值與預設見 control-tower `references/tower-config.md` § 可用選項）
- 每個問題提供選項 + 「其他：________」兜底
- 互動紀錄寫入回報區

## 塔台補充（Renew #1）

**時間**：<datetime> (UTC+8)
**補充內容**：
> <塔台整理的新資訊或方向調整>

**新指示**：
> <具體的新執行指示>

（Renew 時由塔台新增此區段，格式見 research-workorder.md § Renew 機制；Worker 還在執行中時改寫 `## 塔台補充（執行中 #N）`，見 work-order-system.md § 執行中補充工單，v6.0.0-beta.11+）

---

## 回報區

> 以下由 sub-session 填寫，請勿在指揮塔 session 中編輯（唯一例外：`### 待塔台決策` 的 `塔台答覆 Q-n` 行由塔台新增）

### 待塔台決策（僅 yolo Worker 有問題時，v5.5.0+）
（沒有提問就刪除本段；`Q-n` 範本同上方標準模板 § 回報區 › 待塔台決策，格式、等待與備援以 `yolo-mode.md` § Worker 向塔台提問 為準）

### 完成狀態
（DONE / PARTIAL / BLOCKED）
- **session_id**：<本 session 的 `CLAUDE_CODE_SESSION_ID`，或 `unavailable`>（v6.0.0-beta.10+；frontmatter `session_ids` 的鏡像，見 `ct-exec/SKILL.md` § Phase 4 › Session id）

### 互動紀錄
> [HH:MM] Q: <問題摘要> → A: <使用者回覆> → Action: <採取的行動>

### 調查結論
<根因分析或技術方案評估結果——必須是「可決策的」>

### 建議方向
- [A] <方案 A>：<優缺點>
- [B] <方案 B>：<優缺點>
- [C] <方案 C>：<優缺點>
- **推薦**：<推薦方案及理由>

### 建議下一步
- [ ] 開實作工單（建議方案：...）
- [ ] 繼續研究（Renew，新方向：...）
- [ ] 放棄（原因：...）

### Renew 歷程
（若有 Renew 則記錄每次 Renew 的摘要，無則填「無」）

### 遭遇問題
（若有問題或需要指揮塔介入的事項，在此描述）

### 方法論狀態回寫
（有 `methodology.writeback` 或主方法論有 tracker 時填回寫了什麼、寫在哪；都沒有就填「不適用」。另加 `### 方法論執行紀錄` 的條件與內容同上方標準模板）

### 回報時間
（填入當前時間）
```

---

## 緊急工單差異

緊急工單（🔥 URGENT）與一般工單格式相同，但：
- **狀態**：直接標記 `URGENT`（不經過 PENDING）
- **Session 建議**：幾乎一定是 🆕 新 Session（可能在不同 worktree）
- **輸入上下文**：額外包含「中斷的原任務摘要」

## 跨專案協調區段（可選）

當工單為 COORDINATED 或 DELEGATE 類型時，在元資料區段後加入以下區段。
LOCAL 工單（預設）省略此區段。詳見 [cross-project-coordination.md](cross-project-coordination.md)。

### COORDINATED（統籌工單）模板追加

```markdown
## 跨專案協調
- **協調類型**：COORDINATED
- **受影響專案**：
  | 專案 | 前綴 | 子任務 | 對應 DELEGATE 工單 | 狀態 |
  |------|------|--------|-------------------|------|
  | <project-b> | <PB> | <子任務描述> | <PB-T####> | PENDING |
  | <project-c> | <PC> | <子任務描述> | <PC-T####> | PENDING |
- **統籌狀態**：PENDING（全部子任務完成 → DONE）
```

### DELEGATE（受派工單）模板追加

```markdown
## 跨專案協調
- **協調類型**：DELEGATE
- **來源統籌工單**：<PA-T####-description>
- **來源專案**：<project-a>（前綴：<PA>）
- **對應子任務**：<子任務描述>
```

## 盤點工單（教戰手冊格式）

當盤點工單的目標是「萃取 Coding/UI 標準」或「建立技術規範」時，使用此模板 variant。
產出格式為三層教戰手冊，引導 AI 做情境判斷，而非產生僵化的固定條文清單。

**適用時機**：
- 盤點專案的 Coding 標準、UI 元件使用慣例、架構模式
- 需要產出可跨專案複用的技術指引
- 希望 AI 在新專案中能依情境判斷，而非死背條文

**不適用**：一般功能開發、Bug 修復、部署作業等工單（使用一般工單模板）。

### 三層結構定義

| 層級 | 名稱 | 性質 | 跨專案複用性 |
|------|------|------|-------------|
| L1 | 設計哲學 | 引導思維，不規定動作 | 高（跨專案不變） |
| L2 | 決策樹 | 情境 → 判斷依據 → 建議 | 中（架構可複用，細節需調整） |
| L3 | 專案快照 | 本專案的具體答案 + 檔案路徑 | 低（每專案不同） |

### 模板

```markdown
# 工單 T<編號>-<描述>

## 元資料
- **工單編號**：T<編號>
- **任務名稱**：盤點 <主題>（教戰手冊格式）
- **狀態**：PENDING
- **建立時間**：<當前時間> (UTC+8)
- **開始時間**：（sub-session 開始時填入）
- **完成時間**：（完成時填入）
- **目標子專案**：（mono-repo 時填寫，單一專案可留空；巢狀的獨立 repo 見 `mono-repo-patterns.md` § 巢狀的獨立 repo）

## 工作量預估
- **預估規模**：大 / 中 / 小
- **Context Window 風險**：高（>100 檔案）/ 中 / 低
- **降級策略**：若 Context Window 不足，可先完成 Level 1-2，Level 3 交後續工單

## Session 建議
- **建議類型**：🆕 新 Session / 🔄 原 Session
- **原因**：<具體原因>

## 任務指令

### 前置條件
需載入的文件清單：
- <盤點目標的核心原始碼目錄>
- <專案既有的規範文件（若有）>

### 盤點範圍
- **盤點主題**：<例：前端 UI 元件使用標準 / 後端 API 設計慣例 / 錯誤處理模式>
- **掃描範圍**：<例：src/components/, src/views/>
- **代表頁面**：<列出 2-3 個最具代表性的頁面/模組，作為 Level 3 萃取依據>

### 輸入上下文
（由指揮塔整理的精簡上下文）

<專案描述、技術棧、已知慣例、盤點動機>

### 產出格式要求

**必須**以教戰手冊三層結構產出，**禁止**產出固定條文清單。

每個盤點主題按以下結構撰寫：

#### Level 1：設計哲學（跨專案通用）
用「引導思維」描述，讓 AI 理解**為什麼**這樣做：
- 以「先看…再決定…」「如果…就…」的句式撰寫
- 不出現具體元件名稱或檔案路徑
- 目標：換到任何專案都適用

#### Level 2：決策樹（情境判斷）
用 if-then 樹狀結構呈現決策路徑：
- 每個分支列出「情境 → 判斷依據 → 建議方向」
- 可以用 ASCII 樹狀圖、表格或條件列表
- 末端分支提供明確的行動建議
- 包含「不確定時」的 fallback 路徑

#### Level 3：專案快照（本專案具體答案）
為每個決策樹節點填入本專案的實際答案：
- **必須**附帶參考檔案路徑（相對路徑）
- 列出本專案使用的具體元件/模式/工具
- 標註版本或最後確認時間
- 若某節點本專案尚無慣例，標記「待建立」

### 預期產出
- <產出檔案路徑，例：_ct-workorders/fieldguide-<主題>.md>

### 驗收條件
- [ ] 產出為教戰手冊三層結構（非固定條文清單）
- [ ] Level 1 不含專案特定名稱，可跨專案複用
- [ ] Level 2 為 if-then 決策樹，覆蓋主要情境
- [ ] Level 2 包含「不確定時」的 fallback 路徑
- [ ] Level 3 每個答案附帶參考檔案路徑
- [ ] 至少覆蓋 <N> 個盤點子主題
- [ ] <其他專案特定驗收條件>

## Sub-session 執行指示

> **重要**：請在開始工作前，將「開始時間」填入當前時間。
> 完成後請填寫「回報區」。無論成功、失敗或需要後續指示，都必須填寫。

### 執行步驟
1. 讀取本工單全部內容
2. 更新「開始時間」欄位
3. 載入前置條件中的文件
4. 掃描盤點範圍內的原始碼，識別慣例和模式
5. 從代表頁面中萃取具體做法
6. **先寫 Level 2 決策樹**（從實際程式碼歸納情境分支）
7. **再抽象出 Level 1 設計哲學**（從決策樹反推通用原則）
8. **最後填入 Level 3 專案快照**（從掃描結果填入具體答案和路徑）
9. 自我檢查：每個 Level 2 分支是否都有 Level 3 對應答案
10. 填寫回報區
11. 更新「狀態」和「完成時間」

### 執行注意事項
- **情境萃取，不是條列條文**：觀察程式碼中「為什麼這樣選擇」，而非只列出「用了什麼」
- **決策樹優先**：先畫出決策分支，再填答案。避免先列答案再硬套結構
- **不確定就標記**：遇到專案中沒有統一慣例的地方，在 Level 3 標記「無統一慣例，建議建立」
- **路徑必須可驗證**：Level 3 的檔案路徑必須是實際存在的檔案

---

## 回報區

> 以下由 sub-session 填寫，請勿在指揮塔 session 中編輯（唯一例外：`### 待塔台決策` 的 `塔台答覆 Q-n` 行由塔台新增）

### 待塔台決策（僅 yolo Worker 有問題時，v5.5.0+）
（沒有提問就刪除本段；`Q-n` 範本同上方標準模板 § 回報區 › 待塔台決策，格式、等待與備援以 `yolo-mode.md` § Worker 向塔台提問 為準）

### 完成狀態
（DONE / FAILED / BLOCKED / PARTIAL）
- **session_id**：<本 session 的 `CLAUDE_CODE_SESSION_ID`，或 `unavailable`>（v6.0.0-beta.10+；frontmatter `session_ids` 的鏡像，見 `ct-exec/SKILL.md` § Phase 4 › Session id）

### 產出摘要
（列出產生的檔案、修改的檔案、關鍵變更）

### 互動紀錄
（記錄執行過程中與使用者的重要互動）

### 遭遇問題
（若有問題或需要指揮塔介入的事項，在此描述）

### 方法論狀態回寫
（有 `methodology.writeback` 或主方法論有 tracker 時填回寫了什麼、寫在哪；都沒有就填「不適用」。另加 `### 方法論執行紀錄` 的條件與內容同上方標準模板）

### 回報時間
（填入當前時間）
```

### 完整範例

以下是使用教戰手冊模板的盤點工單範例（以「前端彈出容器選擇」為主題）：

```markdown
# 工單 T0200-ui-popup-container-fieldguide

## 元資料
- **工單編號**：T0200
- **任務名稱**：盤點前端彈出容器選擇標準（教戰手冊格式）
- **狀態**：DONE
- **建立時間**：2026-04-01 10:00 (UTC+8)
- **開始時間**：2026-04-01 10:05 (UTC+8)
- **完成時間**：2026-04-01 11:30 (UTC+8)

## 任務指令

### 盤點範圍
- **盤點主題**：前端彈出容器（Dialog / Drawer / Message）選擇標準
- **掃描範圍**：src/components/, src/views/
- **代表頁面**：員工管理 (views/system-management/employee-management/), 訂單編輯 (views/order/edit/)

### 產出格式要求
以教戰手冊三層結構產出。

---

## 產出：彈出容器選擇教戰手冊

### Level 1：設計哲學

- 先看專案中有沒有人做過類似的彈出 UI，有就照著做，保持一致性
- 表單複雜度和「是否需要同時看背景資料」是選擇容器的核心判斷依據
- ERROR 類訊息讓使用者自己關閉，INFO 類可以自動消失
- 能用專案已封裝的基底元件就不要自己寫原生的

### Level 2：決策樹

需要彈出 UI？
├─ 表單/編輯場景
│  ├─ 欄位 ≤ 5 且不需同時看列表 → Dialog 系
│  ├─ 欄位 > 5 或需同時看背景列表 → Drawer 系
│  └─ 不確定 → 找專案中最相似的頁面，照著做
├─ 確認/警告場景
│  └─ 需要使用者明確選擇（確認/取消） → MessageBox
├─ 通知/提示場景
│  ├─ ERROR / WARNING → 不自動消失，使用者手動關閉
│  └─ INFO / SUCCESS → 自動消失（3-5 秒）
└─ 不確定屬於哪種場景
   └─ 回頭看「這個操作失敗了使用者會不會漏掉？」
      ├─ 會漏掉 → 用 MessageBox 或持久通知
      └─ 不會漏掉 → 用自動消失的 Message

### Level 3：本專案快照

- **Dialog** → `BaseDialog` (path: `src/components/BaseDialog.vue`)
  - 支援最大化、Resize、標題自訂
  - 範例用法：員工資料編輯 (`views/system-management/employee-management/EditDialog.vue`)
- **Drawer** → `BaseDrawer` (path: `src/components/BaseDrawer.vue`)
  - 支援髒資料檢查、放棄提醒
  - 範例用法：訂單明細編輯 (`views/order/edit/OrderDrawer.vue`)
- **MessageBox** → 直接使用 Element Plus `ElMessageBox.confirm()`
- **Message** → 直接使用 Element Plus `ElMessage`
  - ERROR: `duration: 0`（不自動關閉）
  - SUCCESS/INFO: `duration: 3000`

最後確認時間：2026-04-01
```

---

## BUG 單模板

> 需啟用 `enable_bug_tracking: true`。詳細規格見 [bug-plan-system.md](bug-plan-system.md)。

```markdown
# BUG-###-description

## 元資料
- **編號**：BUG-###
- **標題**：<簡述>
- **狀態**：OPEN
- **嚴重度**：🔴 High / 🟡 Medium / 🟢 Low
- **發現時間**：<ISO datetime>
- **關閉時間**：（關閉時填入）
- **結案原因**：（只在依 `bug-plan-system.md` § 結案判準 直接結案時填：`<closed_reason>：<說明>`）

## 問題描述
<重現步驟、預期行為、實際行為>

## 修復紀錄
<每次修復嘗試的紀錄，含關聯的修復工單編號>

## 關閉原因
（CLOSED 或 WONTFIX 時填寫）
```

### BUG 狀態流轉

```
OPEN → FIXING → FIXED → VERIFY → CLOSED
                              └→ WONTFIX
     └→ WONTFIX（任何階段可直接標記）
     └→ CLOSED（依結案判準直接結案，見 bug-plan-system.md § 結案判準）
```

---

## PLAN 單模板

> 需啟用 `enable_plan_tracking: true`。詳細規格見 [bug-plan-system.md](bug-plan-system.md)。

```markdown
# PLAN-###-description

## 元資料
- **編號**：PLAN-###
- **標題**：<簡述>
- **狀態**：IDEA
- **優先級**：🔴 High / 🟡 Medium / 🟢 Low
- **建立時間**：<ISO datetime>
- **完成時間**：（完成時填入）

## 描述
<想法/規劃內容>

## 相關工單
<轉為實作時關聯的 T#### 工單>

## 備註
<評估結果、放棄原因等>
```

### PLAN 狀態流轉

```
IDEA → PLANNED → IN_PROGRESS → DONE
                            └→ DROPPED
```

---

## EXP 實驗單模板

> 需啟用 `enable_experiments: true`。詳細規格見 [bug-plan-system.md](bug-plan-system.md)。

```markdown
# EXP-[TOPIC]-###-description

## 元資料
- **編號**：EXP-[TOPIC]-###
- **標題**：<實驗主題簡述>
- **狀態**：EXPLORING
- **TOPIC**：<TOPIC 名稱>
- **假設**：<實驗要驗證的假設>
- **建立時間**：<ISO datetime>
- **結論時間**：（CONCLUDED 或 ABANDONED 時填入）

## 實驗設計
<實驗方法、步驟、預期觀察指標>

## 實驗紀錄
<每次實驗的觀察和數據>

## 結論
（CONCLUDED 時填寫：驗證結果、學到什麼、建議下一步）
（ABANDONED 時填寫：放棄原因）
```

### EXP 狀態流轉

```
EXPLORING → CONCLUDED
         └→ ABANDONED
```

---

## PLAN-034 Sprint 2 transition — YAML frontmatter SoT (v5.0.0+)

> v5.0.0 起，新工單模板從建立時就**雙寫** v1 YAML frontmatter 與既有 body metadata table。
> Frontmatter = 機器 SoT；body metadata table = 人類鏡像；drift 時 `*sync` warn 不覆寫 body。

### 工單模板（含 frontmatter）

```markdown
---
schema_version: 1
schema_kind: workorder
id: T<編號>
title: <任務描述>
type: impl
status: PENDING
repo: <repo 根目錄的目錄名>          # = basename(git rev-parse --show-toplevel)；落點檢查 C-0 承重欄位
project: <目標子專案或 PLAN/BUG 編號>
created_at: "<ISO 8601 datetime with offset>"
sizing: M
depends_on:
  - <前置工單或文件 ID>
followups:
  - <後續工單或文件 ID>
affects_files:
  - <相對路徑 1>
  - <相對路徑 2>
interaction:
  mode_hint: ask
  interactive: false
  intervention_type: fire-and-forget
renew_count: 0
workdir: main repo
landing_check:                       # 可選；僅塔台可填，Worker 不得自加
  expect_missing: false
# isolation: worktree                # 可選（v5.3.0+）；預設不隔離 = 不寫此行。要隔離才取消註解，見下方 `isolation`
# session_ids:                      # 選填（v6.0.0-beta.10+）；Worker 收尾寫、塔台收單補記，建立工單時不寫，見下方 `session_ids`
#   - "<uuid>"
methodology:                         # 可選（v6.0.0+）；沒有任何層由方法論 adapter 負責時整段不寫，見下方 `methodology`
  request_kind: <需求類型>
  resolved_from:                     # 每層各記（鍵同 layers）
    <層>: <workorder / session / project / global / default>
  layers:
    <層>:
      adapter: <adapter id>
      workflow: <adapter routing 的 workflow>
  versions:
    <adapter id>: "upstream <偵測值> / adapter <adapter_version>"
  subagent_writes: deny
  delivery: none
---
# 工單 T<編號>-<描述>

<!--
frontmatter = SoT；body metadata table = 人類鏡像。
若 frontmatter 與 body table drift，*sync 必須 warn 並使用 frontmatter，
不得自動覆寫人類維護的 body table。
-->

## 元資料
- **工單編號**：T<編號>
- **任務名稱**：<任務描述>
- **狀態**：PENDING
- **建立時間**：<當前時間> (UTC+8)
- **開始時間**：（sub-session 開始時填入）
- **完成時間**：（完成時填入）
- **目標子專案**：（mono-repo 時填寫，單一專案可留空；巢狀的獨立 repo 見 `mono-repo-patterns.md` § 巢狀的獨立 repo）
- **intervention_type**：fire-and-forget / context-dependent / decision-requiring
- **affects_files**：
  - `<相對路徑 1>`
  - `<相對路徑 2>`
```

### 欄位填寫規則

#### `schema_version` / `schema_kind`

固定值：

```yaml
schema_version: 1
schema_kind: workorder
```

#### `id` / `title`

- `id` 使用 `T####`，不含檔名描述。
- `title` 使用不含狀態 emoji 的人類標題。
- body H1 可保留既有格式，供人類掃描。

#### `type`

```yaml
type: impl # research / impl / fix / test / docs / refactor / audit / spike / chore
```

#### `status`

新工單預設 `PENDING`。允許值：

```text
PENDING / IN_PROGRESS / PAUSED / DONE / FIXED / FAILED / BLOCKED / PARTIAL / INTERRUPTED / URGENT
```

`PAUSED` 由 `*pause` 設定、`*resume` 解除（改回 `IN_PROGRESS`），流程見 [interrupt-protocol.md](interrupt-protocol.md)。

`URGENT` 是 interruption protocol 產生的 priority signal-as-status special case；可與 `priority: critical` 同時存在。

#### `repo`（v5.0.5+，落點檢查 C-0 承重欄位）

```yaml
repo: BMad-Guide
```

**值的定義**：repo 根目錄的**目錄名**，即 `basename(git rev-parse --show-toplevel)`。

```bash
basename "$(git rev-parse --show-toplevel)"   # -> BMad-Guide
```

- ✅ 目錄名：`BMad-Guide`、`project-a`
- ❌ 不是路徑：`~/repos/my-org/BMad-Guide`
- ❌ 不是專案顯示名：`BMad 控制塔`、`專案 A 核心系統`
- ❌ 不是 remote URL 或 repo slug：`my-org/BMad-Guide`

**`repo` 與 `project` 語意不同，不得混用**：

| 欄位 | 回答的問題 | 值來自 | 落點檢查用途 |
|---|---|---|---|
| `repo` | 這張工單該在**哪個 git repo** 執行？ | `basename(git rev-parse --show-toplevel)` | ✅ C-0 承重檢查比對此欄位 |
| `project` | 在該 repo 內，這張工單屬於**哪個子專案 / PLAN / BUG**？ | 人工命名的 mono-repo 子專案或記錄編號 | ❌ 不參與落點檢查 |

單一 repo 單一專案時兩者的字面值可能碰巧相同，但語意仍不同：
`repo` 由機器指令取得，`project` 由人命名。**填 `repo` 時必須實際跑一次上面的指令，
不得從 `project` 複製、不得憑印象填。**

**選填**。舊工單、他方塔台建立的工單可能沒有此欄位：

- 缺 `repo` 欄位 → 落點檢查記 WARN「repo identity unavailable」並退回 C-3 + C-1 判定
- **不得因缺欄位而 STOP** —— 缺欄位是舊工單的常態，不是錯誤訊號

塔台建立新工單時**應**填入。

工單集中在上層、改的是巢狀的獨立 repo 時，`repo` 填**上層**的目錄名，不是子 repo 的（v6.0.0-beta.7+，見 [mono-repo-patterns.md](mono-repo-patterns.md) § 巢狀的獨立 repo）。

#### `landing_check`（v5.0.5+，落點檢查逃生閥）

```yaml
landing_check:
  expect_missing: true   # 本工單自身才建立目標樹，affects_files 於開工時必然不存在
```

`expect_missing: true` 時，落點檢查 C-3 的 absent 結果**只記 WARN，不 STOP**。
C-0（repo identity）**不受影響，照常 STOP**。

**這不是萬用消音開關。** 適用條件只有一個：

> 工單的執行步驟**自身會建立** `affects_files` 所指的目標樹
> （例如「複製 v5.0.4/ 為 v5.0.5/ 後就地修改」這類新建版本目錄的工單）。

限制：

- **只有塔台在建立工單時可以填**。
- **Worker 不得自行加上此欄位讓檢查通過** —— 落點檢查 STOP 時，正確反應是回報
  `WRONG_REPO_SUSPECTED` 給塔台，不是修改工單讓它安靜。Worker 自加此欄位等同
  停用護欄，屬違規。
- 不適用於「檔案應該存在但找不到」的情況；那正是 C-3 要攔的訊號。

未宣告時預設 `false`。

#### `isolation`（v5.3.0+，選用）

```yaml
isolation: worktree
```

**本小節是 `isolation` 欄位的唯一權威定義。** 值只有 `worktree`；其他值視為格式錯誤，派工前請塔台更正。

- **預設不隔離**（D152）：沒有這個欄位 = 不隔離，派工、Worker 行為、收單、回收與 v5.2.6 完全相同。
- 有 `isolation: worktree` 時，塔台派工加 `--isolation worktree`，BAT 為這張工單建立獨立的 git worktree 與分支 `ct/T####`；
  派工命令、exit `7` 與降級規則見 [auto-session.md](auto-session.md) § worktree 隔離派工。需 BAT **`>= 0.7.0-pre.2`**。
- **何時適合用**：
  - 同時派出多張會動產品檔的工單（並行），避免互相踩到工作樹；
  - 會大量改動產品檔、希望驗收過後再合併回 `main` 的工單。
- **不適合**：只改 `_ct-workorders/` 或文件的小單、研究型工單、需要在主 checkout 操作執行環境的工單（例：安裝、部署）。
- **不能用**（v6.0.0-beta.7+）：工單在上層、產品檔在巢狀的獨立 repo 的工單。BAT 以上層建 worktree，worktree 裡沒有子 repo；見 [mono-repo-patterns.md](mono-repo-patterns.md) § 巢狀的獨立 repo › 限制。
- 🔴 隔離工單的 `_ct-workorders/` 一律在主 checkout 修改；worktree 裡的 `_ct-workorders/` 是 base 當下的唯讀副本，
  不得修改、不得 stage（Worker 規則見 `ct-exec/SKILL.md` § Worktree Isolation）。
- `affects_files` 照常填，而且更重要：BAT 以它計算 `outOfScopeFiles`，塔台直接合併判準要求它為空陣列
  （見 [merge-workorder.md](merge-workorder.md) § 塔台直接合併判準）。沒填 `affects_files` 的隔離工單一律走合併工單。
- 隔離工單的回報區要多填「隔離分支證據」段（`branch` / `base_sha` / `validated_sha` / `head_sha`），格式見本檔開頭的回報區模板。
- 隔離工單完成後的合併見 [merge-workorder.md](merge-workorder.md)。

#### `tower_question` / `worker_question_timeout`（v5.5.0+，yolo 提問通道）

```yaml
tower_question: open          # Worker 寫：有待塔台答覆的問題；全部答完後 Worker 刪除此行
worker_question_timeout: 30   # 塔台寫：yolo 派工時的生效值（分鐘）
```

- 兩個欄位都只用在 `CT_MODE=yolo`；非 yolo 工單不寫。規則的唯一權威見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問，
  `worker_question_timeout` 的有效值與預設見 [tower-config.md](tower-config.md) § 可用選項。
- `tower_question` 只有 `open` 一個值；沒有待答問題 = 沒有這個欄位。走備援（`BLOCKED`）時保留，塔台據此知道要在 Renew 區段答覆。
- `tower_question: open` 是送 `T#### 提問` **前**必加的欄位（v5.6.1 起；原地等待與 `worker_question_timeout = 0` 直接走備援都一樣），
  並與 `### 待塔台決策` 的題目一起 commit 後才送出。走 BAT 通道（v5.7.0+，`--ask`）時一樣要加（雙寫）：BAT 通道成功時塔台不在工單寫答覆行，
  Worker 收到答覆、全部答完後照樣刪除此欄位。
- 塔台不改 `tower_question`；Worker 不改 `worker_question_timeout`。

#### `session_ids`（v6.0.0-beta.10+，選填）

```yaml
session_ids:
  - "<uuid>"   # 範例：換成實際的 session id
```

- 執行這張工單的 Claude Code session id（`CLAUDE_CODE_SESSION_ID`），給 `*insights sessions` 做歸屬（優先序 ⓪，見
  `ct-insights/references/analysis-rules.md` § Session 用量統計）。**建立工單時不寫**；由誰寫：
  - **Worker**：ct-exec 收尾寫自己的 session id（取值、UUID 驗證、`unavailable`、Renew 追加不覆蓋，唯一權威 `ct-exec/SKILL.md` § Phase 4 › Session id），
    回報區〈完成狀態〉加鏡像行 `- **session_id**：<值>`；
  - **塔台**：收單時、`--close-worker` 之前，用 BAT MCP 讀 Worker 分頁的 `claudeSessionId`，不在清單裡就追加（[work-order-system.md](work-order-system.md) § 收單補記 session id）。
- YAML block list、每個值加引號；去重；值只能是 UUID 或 `unavailable`。session id 不是秘密，但這是「環境變數只列名稱」唯一允許寫值的地方，
  不得順帶寫其他變數或任何權杖（[auto-session.md](auto-session.md) § BAT 內部終端路由 › 偵測條件）。
- 沒有這個欄位的工單（含所有舊工單）照常；統計改用第一則訊息與分頁標題歸屬。

#### `methodology`（v6.0.0+，選用）

```yaml
methodology:
  request_kind: feature
  resolved_from:
    execution: project
  layers:
    execution:
      adapter: bmad
      workflow: bmad-build
```

- **結構與每個鍵的意義以 [methodology-adapters.md](methodology-adapters.md) § 工單欄位 為準**（含選填的 `detail`、`inputs`、`writeback`），本檔不複述。
- 塔台派工時依該檔 § 解析步驟 寫入；Worker 不讀 `_tower-config.yaml` 決定方法論，只讀這個欄位。
- 沒有任何層由 adapter 負責 → 不寫這個欄位。沒有這個欄位的工單（含所有舊工單），Worker 行為與 v5.12.6 相同；
  舊工單的 `### BMad 工作流程` 段照讀、不回寫（上方「填寫方法論欄位指引」範例 C）。
- 有這個欄位時，內文要有 `### 方法論工作流程` 鏡像，回報區要有 `### 方法論執行紀錄`、`### 方法論狀態回寫`（本檔開頭的模板）。

#### `affects_files`

使用 YAML block list（**不**使用 JSON array），路徑使用 repo-relative forward slashes：

```yaml
affects_files:
  - _ct-workorders/T0342-*.md
  - src/types/control-tower.ts
```

#### `interaction`

```yaml
interaction:
  mode_hint: yolo
  interactive: false
  intervention_type: fire-and-forget
```

注意：

- `mode_hint` 是文件化意圖，**不是** Worker runtime mode source。
- Worker runtime mode 仍只能由塔台注入的 `CT_MODE` env 決定（D062 嚴格禁令）。
- `intervention_type` 保留三值：`fire-and-forget` / `context-dependent` / `decision-requiring`。

### Body metadata mirror 注意事項

> Frontmatter 是機器 SoT；本段元資料只供人類速查。
> 若兩者不一致，`*sync` 使用 frontmatter 並輸出 drift warning，不自動覆寫本段。
> 過渡期 legacy markdown table fallback parser 仍保留；缺 frontmatter 的舊工單只警告不立即失效。

### 驗收

- 新模板產出的工單第一個 bytes 是 `---`。
- 新模板保留原 body metadata table。
- 模板明示 frontmatter SoT / body mirror / drift warn not overwrite。
- `affects_files`、`depends_on`、`followups` 均使用 YAML block list。
- `interaction.mode_hint` 不被描述為 runtime mode source。
- `repo` 欄位有定義、有取值指令、且明文與 `project` 區分語意。
- `landing_check.expect_missing` 有定義，且明訂非萬用消音、Worker 不得自加。
- `isolation` 欄位有定義，且明訂預設不隔離（v5.3.0+）。
- `methodology` 欄位有範本，結構引用 `methodology-adapters.md` § 工單欄位，且明訂缺省 = v5.12.6 行為、舊段照讀（v6.0.0-pre.1）。

---

## 合併工單模板（v5.3.0+）

> 合併工單沿用一般工單（同一個 `T####` 編號序列、同一套 frontmatter），**不是新的單據類型**；只多下方固定欄位。
> 三種模式、共同護欄、直接合併判準與收單 SHA 比對，以 [merge-workorder.md](merge-workorder.md) 為唯一權威，本模板只引用。

```markdown
---
schema_version: 1
schema_kind: workorder
id: T<編號>
title: 合併 T<被合併工單編號> → main
type: chore
status: PENDING
repo: <repo 根目錄的目錄名>
project: <目標子專案或 PLAN/BUG 編號>
created_at: "<ISO 8601 datetime with offset>"
kind: merge
merges:
  - T<被合併工單編號>
merge_mode: conflict                 # mechanical | conflict | port；由塔台決定
integration_worktree: <整合 worktree 的絕對路徑>
base_main_sha: <派合併工單當下 main 的 40 字元 SHA>
merge_target: main                   # 預設 main；需要 PR 的專案可指定整合分支
affects_files:
  - <被合併工單的 affects_files，逐項列出>
interaction:
  mode_hint: ask
  interactive: false
  intervention_type: decision-requiring
renew_count: 0
---
# 工單 T<編號>-merge-<被合併工單編號>

## 元資料
- **工單編號**：T<編號>
- **任務名稱**：合併 T<被合併工單編號> → <merge_target>
- **狀態**：PENDING
- **合併模式**：<① 機械 / ② 衝突解決 / ③ 等價移植>
- **整合 worktree**：<路徑>
- **base_main_sha**：<SHA>

## 任務指令
依 [merge-workorder.md](merge-workorder.md) 的 <模式> 規則執行；共同護欄見同檔 § 共同護欄。
- 被合併分支：`ct/T<被合併工單編號>`（Worker 回報的 `head_sha`：<SHA>）
- 驗收條件：<被合併工單的驗收條件，或專案完整驗收>

## 回報區
（必填項目依模式不同，見 [merge-workorder.md](merge-workorder.md) § 三種模式 的回報要求）
- merge_commit：
- 合併 commit 的 parent1 / parent2：
- 驗收結果（跑在哪個 SHA）：
- 範圍外檔案：
- 衝突檔逐一說明 / 移植對照表：
```

- `kind: merge`：標示這是合併工單；沒有此欄位的工單一律是一般工單。
- `merges`：被合併的工單編號（YAML block list），通常一張。
- `merge_mode`：`mechanical` / `conflict` / `port`，對應三種模式 ① ② ③；由塔台決定，Worker 不得自行升級。
- `integration_worktree`：長期保留的整合 worktree 路徑（避免每次重裝依賴），建立方式見 [merge-workorder.md](merge-workorder.md) § 共同護欄。
- `base_main_sha`：派合併工單當下 `main`（或 `merge_target`）的 SHA，收單 SHA 比對第 ① 步使用。
- `merge_target`：預設 `main`。
