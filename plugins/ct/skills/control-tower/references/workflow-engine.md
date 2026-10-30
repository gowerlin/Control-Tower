# Workflow 引擎（v5.10.0+）

> 本檔是 CT 對 Claude Code **Workflow 工具**的**唯一權威定義**：定位、Skill／Playbook／Workflow 三分法、
> 工具型與派工型、設計規則 R1–R5、知識卡格式、成熟度與回測、指標降級、成本與規模、`workflow_integration` 的行為、
> 同意治理、Codex、知識卡的寫入路徑檢查、現況與尚未定案的部分。
> 例外：`workflow_integration` 的有效值與預設只在 [tower-config.md](tower-config.md)；Worker 依授權使用 Workflow 與記錄子代理的規則只在 `ct-exec/SKILL.md`。
> [doctrine.md](doctrine.md)、[playbook-engine.md](playbook-engine.md)、[data-layer-architecture.md](data-layer-architecture.md)、
> [self-learning-core.md](self-learning-core.md)、`ct-evolve/SKILL.md`、`ct-insights/references/analysis-rules.md` 與 `SKILL.md` 只放摘要並引用這裡。
> 「哪些工單適合 Workflow」的偵測規則（S1–S6／X1–X5、WFC 候選格式）的權威在
> `ct-insights/references/analysis-rules.md` § Workflow 適配度；`--workflow` 模式的行為在 `ct-evolve/SKILL.md` § Promotion Modes。
>
> 來源：使用者提案 `_proposal-2026-10-20-ct-workflow-intelligence.md`（§4、§5.2、§5.4，只作背景）；
> T0176 meta-PLAN § 2 事實核對、§ 3 十項結論、回報區「成本基準」；T0177 報告 § 3–§ 6、§ 8、§ 10；
> D075（同意治理）、D076（U1 降級只限 Workflow、U2 v5.10.0 = P1+P2）、D080（工具型／派工型）、D081（G1 通過）、D082（T0178 範圍）；
> v5.11.0：D083（`workflow_integration`）、D085（派發匹配 (C) 腳本守門＋按需提示）、D089（G2 未通過）、D090（P3 精簡版，T0183）。
>
> **v5.11.0 是精簡版 P3。** 新增：設定 `workflow_integration`（§ `workflow_integration` 的行為）、Worker 使用 Workflow 的授權
> 與自發子代理記錄（§ 同意治理；Worker 側權威在 `ct-exec/SKILL.md`）、預篩腳本的排除守門與按需提示（`*insights workflow`）。
> 閘門 G2 未通過（§ 現況：G2 未通過），所以**具名 workflow 的派發與執行**、工單 frontmatter 欄位（`execution`、`workflow_run_id` 等）
> 都**待卡片達 🟡 後再定**，本版沒有這些規格（見 § 尚未定案）。

---

## 定位

**Workflow 是 Worker 在單張工單內的執行方式，不是 CT 的編排層。**

CT 仍然只用檔案驅動的工單來編排工作：派工、跨 session、人工把關，都由工單和 Playbook 負責。
Workflow 只在一張已經派出的工單**之內**，由 Worker 決定子任務怎麼並行、怎麼互相驗證。
所以 [doctrine.md](doctrine.md) 前言「CT 不是 workflow 工具」仍然成立：CT 不編排 Workflow，是工單裡的 Worker 選擇用它執行。

「Workflow」在本檔專指 Claude Code 的 Workflow 工具（以腳本編排多個子 agent 的背景執行）。
`work-order-template.md` 裡的 BMad workflow（`bmad-*` 技能流程）是另一回事，不受本檔規範。

## 三分法：Skill／Playbook／Workflow

| 產物 | 封裝的是 | 作用範圍 | 判斷問句 | 典型證據 |
|---|---|---|---|---|
| **Skill** | 怎麼做（知識、規範） | 單一 agent | 每個執行者都需要這份知識嗎？ | 跨 3 個以上專案重複出現的做法 |
| **Playbook** | 工單序列 | 跨工單、跨 session，中間有人把關 | 這是一連串要依序完成、中途要人確認的工作嗎？ | 同系列工單依序派出（probe 系列）；修復單 → 獨立驗證單 |
| **Workflow** | 單張工單內的編排形狀（扇出、驗證、彙整） | 單張工單之內，Worker 決定 | 這張工單裡有執行前就能列出、彼此獨立的同形子任務嗎？或者這類工作過去常常被推翻，值得加一層獨立驗證嗎？ | 扇出：單張工單逐一處理 N 個獨立模組或文件；驗證：前一張的結論被獨立複核推翻 |

**三者可以疊加**：Playbook 裡的某一張工單用 Workflow 執行；Workflow 的每個子 agent 載入 Skill。

**分界的三條提醒**

1. **重複發生在工單「之間」，就是 Playbook，不是 Workflow**（規則組的 X5）。
2. **單張工單小（約 15 分鐘內），扇出的收益就很低**。這時只有驗證軌（獨立複核、多視角審查）值得考慮。
   「規模小」只記錄，不是排除條件。
3. **工作量大，不代表適合 Workflow**。一支腳本或一條指令能跑完的是 X4；`batch` 這個字不是訊號。

偵測與分級的條文在 `ct-insights/references/analysis-rules.md` § Workflow 適配度，本節不複述。
v5.11.0+ 的預篩腳本（`ct-insights/scripts/ct-workflow-prefilter.py`）只做**排除守門**與**按需提示**，不自動標記工單；
角色與塔台入口 `*insights workflow [T#### …]` 見同檔 § 預篩腳本：排除守門與按需提示。

## 兩種用途：工具型與派工型（D080）

| 用途 | 誰用 | 形狀 | 例子 | 本版狀態 |
|---|---|---|---|---|
| **工具型** | 分析作業（`ct-insights`、`ct-evolve` 這類讀工單歷史的作業） | 讀大量語料、分批結構化、彙整 | 語料挖掘：分批全讀工單 → 結構化分類 → 確定性分群 → 對抗式複核 → 彙整 | 可以寫知識卡與 brief；要實際執行，卡片須到 🟡 以上，且每次執行前依 § 成熟度與回測 列規模、經使用者同意 |
| **派工型** | 一般工單，由 Worker 以 workflow 執行 | 單張工單內的扇出或驗證 | 多來源唯讀核對：每個來源一個唯讀子 agent 對照程式碼，主 agent 抽查關鍵點後統一寫入 | 可以寫知識卡與 brief；**具名 workflow 的派發與執行待卡片達 🟡 後再定**（D090）。Worker 只有在工單明文授權時才可以呼叫 Workflow 工具（§ 同意治理） |

知識卡的「用途」欄必填其中之一（§ 知識卡格式）。工具型的卡片**不參與**日後的派發匹配。

## 設計規則 R1–R5

所有 CT 的 workflow（brief、腳本、知識卡）都要符合以下規則。brief 逐條寫出怎麼符合；不符合的就不寫成腳本。

| # | 規則 | 為什麼 |
|---|---|---|
| **R1** | 回傳 schema 必須能**直接映射工單報告的區段**（發現、修改、驗證結果、遺漏）。 | Worker 用結果直接填回報區，不另做轉換；轉換容易漏項 |
| **R2** | 有界覆蓋（top-N、取樣、不重試）時，一律用 `log()` 記下被略過的項目，**禁止靜默截斷**。遺漏數寫進報告（遺漏率的分子）。 | 沒有被記下的遺漏，看起來就像「全部看過」 |
| **R3** | **不使用 Workflow 內建的 `isolation: 'worktree'`**。P2～P3（v5.10.0～v5.11.0）的 workflow **只做唯讀或分析形狀**：子 agent 不改檔，只回結構化結果，由 Worker 統一寫入。平行改檔的形狀不在本版範圍，日後另案設計。 | BAT 偵測不到 Workflow 自建的 worktree，CT 的合併流程（[merge-workorder.md](merge-workorder.md)）也沒有對接 |
| **R4** | 子 agent 只能使用**唯讀** tool；bat MCP 也只用唯讀 tool（`mcp__bat__*` 目前本來就全部唯讀）。 | 與 R3 同理；寫入集中在 Worker，才對得上工單的 `affects_files` 與 commit |

> **R4 的殘餘風險（v5.11.0 加註，T0180 表外 3）**：Explore 型 agent 只拿掉 Edit／Write／NotebookEdit，**仍然有 Bash／PowerShell**，
> 所以「只用唯讀 tool」不能只靠 agent 型別保證。唯讀要靠 prompt 明文禁止寫入（含 shell 的重導向、`git` 寫入指令），
> 再由 Worker 收尾時用 `git status --porcelain` 確認沒有意外改動。這是已知的殘餘風險，沒有技術上的強制手段。
| **R5** | 腳本不得使用 `Date.now()`／`Math.random()`；時間戳由呼叫端以 `args` 傳入（取值方式依全域規則：以系統指令取得，不憑印象）。 | 這兩個值會破壞 `resumeFromRunId` 的續跑；時間戳也必須可追溯 |

## 知識卡格式

知識卡記錄一個 workflow 的設計與驗證狀態，比照 [playbook-engine.md](playbook-engine.md) § Playbook 標準格式。
**腳本不寫在卡片裡**；腳本的落點與寫入條件見 [data-layer-architecture.md](data-layer-architecture.md) § 寫入規則 › Layer 3 附屬：專案 workflow 腳本。

| 範圍 | 路徑 |
|---|---|
| 專案 | `_ct-workorders/_workflows/<name>.md`（Layer 3） |
| 全局 | `~/.claude/control-tower-data/workflows/<name>.md`（Layer 2）；Layer 2 不存在時**只做專案級**，不代為建立 |

```markdown
# Workflow: <名稱（依形狀命名，不依主題）>

> 用途：工具型 / 派工型
> 成熟度：🔵 brief / 🟡 回測達標 / 🟢 實戰可靠 / ⭐ 預設建議（降級時附 ↓ 與日期）
> 範圍：project / global
> 首次記錄：<日期>
> 來源：WFC### / T####（候選與證據工單）
> 腳本：<`.claude/workflows/<name>.js`，尚未撰寫則寫「未撰寫」>

## 適用場景
- <觸發條件；引用規則組的軌道與 S 訊號>

## 不適用場景
- <排除條件；引用 X1–X5>

## args schema
| 參數 | 型別 | 說明 | 執行前可列？ |
|---|---|---|---|

## 階段與 schema
| 階段 | 做什麼 | 子 agent 數 | 回傳 schema（R1：對應報告哪一區段） |
|---|---|---|---|

## 驗證策略
<單票／對抗式複核／多視角；主 agent 抽查哪些點>

## 規模上限與成本
- agent 數上限：<N>（不超過 session 的 workflow 規模準則，放寬要使用者同意）
- 子任務數上限：<N>
- token 事後上限：<N>（整次執行；執行中讀不到用量，只能事後對照）
- 單位成本上限：<N> tokens／子任務（§ 指標降級 的比較基準）
- 預估：<子任務數> × ~<k> tokens ＋ 每個 agent 固定開銷 ~31k

## R1–R5 符合情形
- R1：… / R2：… / R3：… / R4：… / R5：…

## 驗證歷史
| 次 | 種類（回測／實戰） | 工單 | 召回 | 誤報 | 採納率 | 推翻率 | tokens | 遺漏 | 日期 |
|---|---|---|---|---|---|---|---|---|---|

## 降級紀錄
| 日期 | 從 → 到 | 觸發條件 | 證據 |
|---|---|---|---|
```

## 成熟度與回測

| 等級 | 條件 | 可做什麼 |
|---|---|---|
| 🔵 brief | `ct-evolve --workflow` 產出 brief 與卡片 | 只供討論；使用者確認 brief 後，可另開工單撰寫腳本 |
| 🟡 回測達標 | **有已知發現**的稽核或審查型：回測**召回 ≥ 80%、誤報 ≤ 20%**。**沒有已知發現的研究型不能用回測升 🟡**，改為「1 次實戰＋使用者認可結論」 | 工具型可經使用者同意執行；派工型的具名派發在第一張卡達 🟡 後再定（§ 尚未定案） |
| 🟢 實戰可靠 | 2+ 次實戰執行，採納率 ≥ 80% | 同上 |
| ⭐ 預設建議 | 3+ 次驗證＋使用者認可 | 同上；⭐ 才解除「每次先問使用者」（§ 同意治理） |

**回測做法**：選 2–3 張**已結案**、形狀相同的工單（工具型可改用已有標準答案的語料子集），用 workflow 重跑，
對照當時 Worker 的實際產出，記錄召回率、誤報數、token 成本、耗時，寫進卡片「驗證歷史」。

🔴 **每次回測或試跑之前，都要先列出預估規模（agent 數、子任務數、預估 tokens），經使用者同意才跑。**
這條不因成熟度、不因 yolo 而免除；回測與試跑另開工單執行，不在寫 brief 的同一輪做。

**指標**（寫進卡片的驗證歷史）：

| 指標 | 計算 | 用途 |
|---|---|---|
| 採納率 | 被塔台接受的發現數 ÷ 回報發現數 | 升級條件 |
| 推翻率 | 塔台退回或推翻的發現數 ÷ 回報發現數 | 降級觸發 |
| 單位成本 | tokens ÷ 子任務數 | 降級觸發、成本控管 |
| 遺漏率 | `dropped`（R2 記下的略過項）÷ 子任務總數 | 覆蓋完整度 |

## 指標降級（只限 Workflow，D076 U1 = a）

任一等級，符合以下任一條件就**降一級**，寫進卡片「降級紀錄」：

- **連續 2 次**推翻率 > 30%
- 單位成本（tokens ÷ 子任務數）**超過卡片單位成本上限的 50%**（即實際 > 上限 × 1.5）

現有的 ❌ 廢棄（使用者說不適用）與休眠（連續 3 個專案未觸發），對知識卡照舊適用。

🔴 **本規則只適用於 Workflow 知識卡**，不改變 [self-learning-core.md](self-learning-core.md) § 置信度系統對 pattern、playbook 的規則。
**待決**：累積 ≥ 5 次 workflow 執行後，再評估是否把指標降級推廣到整個置信度系統（由使用者決定；本版不改）。

## 成本與規模

- **沒有 token 預算參數**：Workflow 的輸入沒有 token 預算欄位，執行中也讀不到 token 用量。
  所以預算**只能靠腳本限制 agent 數與子任務數**，token 只能**事後記帳**；超支由 § 指標降級 處理，不是「超過就中止」。
- **成本基準**（BAT EXP-WFMINE-001／T0673 實測，2026-10-20；寫進卡片的預估時引用）：
  - 中文為主的工單語料約 **1.9 bytes/token**
  - 每個 reader agent **固定開銷約 31k tokens**
  - 全量挖掘（718 檔、39 個 agent、約 20.5 分鐘）共 7.35M tokens，超出使用者核准上限約 5%——執行中讀不到用量，只能事後確認
  - `resumeFromRunId` 續跑**可能沒有命中快取**（實測多花約 185k，原因未查證）；預估時不要假設續跑便宜
  - 回測 R2、R3（T0182）的 reader 實際每組 **100–180k tokens**，是卡片預估（40–60k）的 2–3 倍；預估多來源核對時以這個區間為準（§ 現況：G2 未通過）
- **規模準則**：尊重 session 設定的 workflow 規模準則（例：small = 少於 5 個 agent）。brief 與卡片的上限不得超過它；
  要放寬，回測或試跑前的規模預估就要寫明，由使用者同意。

## `workflow_integration` 的行為（v5.11.0+，D083）

有效值、預設與持久化的權威在 [tower-config.md](tower-config.md) § 可用選項；本節只寫各值對塔台行為的影響。
三層設定照舊：`*config workflow_integration off` 只影響當前 session（token 焦慮時臨時關閉），加 `--save project`／`--save global` 才持久。

| 值 | 塔台寫 Workflow 授權（§ 同意治理） | 工具型 workflow（`ct-insights`、`ct-evolve` 這類分析作業） | 不受影響、照常做的事 |
|---|---|---|---|
| `off` | **不建議、不寫授權**。已寫好授權但還沒派出的工單，派工前刪掉授權段落並在工單註記「Workflow 未授權（`workflow_integration: off`）」 | 不開執行工單、不跑 | 規則分析（S1–S6／X1–X5）、預篩腳本（`*insights workflow`）、`ct-evolve --workflow` 產 brief 與 🔵 卡片——這些都不花 workflow token |
| `ask` | **每次**寫授權前都先問使用者，知識卡到 ⭐ 也一樣 | 每次執行前列規模、經使用者同意（本來就如此） | 同上 |
| `on` | D075：知識卡到 ⭐ 之前先問使用者；⭐ 之後塔台在 yolo 下可以在卡片規模上限內自決。**本版沒有 ⭐ 卡，實際行為等同「每次都問」** | 同 `ask` | 同上 |

- **Worker 不讀這個設定**（D062）：塔台在派工時就把結果寫進工單——有授權段落才可以用，沒有就不可以。
  工單派出後才改設定，不會影響已派出的工單；要收回授權，塔台改工單（Worker 執行中則以 Renew 或提問答覆告知）。
- 只管 **Workflow 工具**。Worker 用一般 Agent 工具開的唯讀子代理不是 Workflow，不受這個設定管；但它的用量要記在回報區
  （Worker 側的權威在 `ct-exec/SKILL.md` § Workflow And Sub-Agents），塔台收單時就看得到。
- BAT 不需要為這個設定改動。

## 同意治理（D075；v5.11.0 起落到工單授權）

- 工具型：每次執行前列規模、經使用者同意（§ 成熟度與回測）。
- 派工型：Worker 在一張工單內呼叫 Workflow，**必須有塔台寫在工單裡的授權段落**。Worker 怎麼依授權執行、超出時怎麼停，
  權威在 `ct-exec/SKILL.md` § Workflow And Sub-Agents；授權段落的範本在 [work-order-template.md](work-order-template.md) § 撰寫 Workflow 使用授權。
- 塔台寫授權之前，依 `workflow_integration`（§ `workflow_integration` 的行為）決定：`off` 不寫；`ask` 每次問使用者；
  `on` 在知識卡到 ⭐ 之前先問使用者，⭐ 之後塔台才可以在規模上限內自行決定。yolo 也一樣。
- 問使用者時要列出規模（執行次數、每次 agent 上限、token 事後上限），使用者的答覆寫進決策日誌，授權段落引用那條決策。

## Codex

Workflow 是 Claude Code 的能力，**Codex 不支援**。本版不研究 Codex 的等價機制。
有 Workflow 授權的工單只能派給 Claude Code Worker（`--agent` 不得是 codex）；授權段落要寫明這一點。
Codex Worker 遇到授權段落，依 `ct-exec/SKILL.md` § Workflow And Sub-Agents 處理（不模擬、不呼叫）。

## 寫入路徑檢查（知識卡）

```
知識卡寫入目標路徑檢查流程：
1. if path 落在 Layer 1 路徑（範圍見權威定義）→ ❌ 拒絕
2. if path starts with ~/.claude/control-tower-data/workflows/ → ✅ Layer 2（全局卡）
3. if path starts with _ct-workorders/_workflows/ → ✅ Layer 3（專案卡）
4. else → ❌ 拒絕（不明路徑）
```

> 第 1 步的範圍與唯一例外，見 [data-layer-architecture.md](data-layer-architecture.md) § 寫入規則（唯一權威定義）。
> 專案 workflow **腳本**（`.claude/workflows/*.js`）不是知識卡，也不是學習寫入，不走本檢查；
> 只能由 Worker 依工單 `affects_files` 寫入，條件見 data-layer-architecture.md § Layer 3 附屬：專案 workflow 腳本。
> 🔴 不使用 `~/.claude/workflows/`。

## 現況：G2 未通過（v5.11.0，D089）

閘門 G2（至少一個具名 workflow 回測達標升 🟡）**沒有通過**。BMad-Guide 專案的兩張卡片
`corpus-mining`（工具型）與 `multi-source-readonly-check`（派工型）都停在 🔵（T0182，三次回測共約 1.8M tokens、11 個 agent）。

| 教訓 | 證據（T0182 報告 § 4–§ 7） | 對之後設計的意思 |
|---|---|---|
| **refuter 會確認錯誤的發現** | R2 的 reader 沿用前單的錯誤結論，refuter 只沿著讀取點追、沒追到寫入點，也判 `confirmed`；是 Worker 回到快照查證才推翻 | 對抗式複核不是保險。主 agent 的抽查不能只抽「推翻前單」的發現，和前單一致的高嚴重度結論也要抽 |
| **reader 成本被低估 2–3 倍** | 多來源核對的 reader 實際每組 100–180k tokens，卡片預估 40–60k；R2 超過事後上限約 22% | 預估改用實測區間（§ 成本與規模）；執行中讀不到用量，上限只能事後對照 |
| **真正成立的扇出，多半是 Worker 自發** | T0177、T0179 確認的 🔵 案例都是 Worker 自己決定開唯讀子代理；R2 還漏掉了單一 Worker 在 T0653 找到的推翻 | 沒有證據顯示具名 workflow 比單一 Worker 划算。v5.11.0 改為記錄 Worker 自發的子代理用量（`ct-exec/SKILL.md` § Workflow And Sub-Agents），累積證據 |

T0182 報告 § 7 的 11 條修正建議（corpus-mining 6 條、multi-source 5 條）留到日後重測時處理，本版不改卡片與腳本。

## 尚未定案（待卡片達 🟡 後再定，D090）

- **具名 workflow 的派發與執行**：塔台派工前比對 `_workflows/`（[playbook-engine.md](playbook-engine.md) § 塔台自動建議 本版仍不掃描 `_workflows/`）、
  以具名 workflow 派工、`ct-exec` 的具名 workflow 執行路徑、中斷續跑、結果映射回報區
- 工單 frontmatter 欄位（`execution`、`workflow`、`workflow_args`、`workflow_budget`、`workflow_run_id`、`workflow_stats` 等），
  以及交給 BAT 的欄位介面契約（BAT PLAN-054 的 B6 一併延後）
- 預篩提示升級成自動建議（D085：提示清單抽驗準確率 ≥ 70% 之後再評估）
- 撰寫或執行任何 workflow 腳本仍照舊：腳本由另一張工單在使用者確認 brief 後撰寫；回測或試跑再另開工單，跑前列規模經使用者同意
