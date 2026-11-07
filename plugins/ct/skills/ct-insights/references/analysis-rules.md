# 互動模式分析規則

> 從工單的「互動紀錄」和決策日誌中偵測使用模式。
> 每個模式有明確的偵測信號和說明。
> v5.10.0+：另有「Workflow 適配度」規則組（S1–S6／X1–X5），從工單內文偵測適合以 Workflow 執行的候選。
> v6.0.0-beta.10+：另有「Session 用量統計」（`*insights sessions`），從 Claude Code 本機 session 紀錄算工單層級用量。

---

## 好的模式 ✅

| # | 模式 | 偵測信號 | 說明 |
|---|------|---------|------|
| G1 | **排除法驅動** | 工單含有「排除 A → 確認 B」的記錄 | 系統性除錯，不是猜測驅動 |
| G2 | **對照驗證** | 工單含有成功/失敗案例比較 | 找到成功案例來對照差異 |
| G3 | **契約驅動** | 跨專案工單引用 contracts/ | 不是「照抄」，而是引用共用規格 |
| G4 | **結構化回報** | 回報區有完整的「已完成/未解決/建議」 | sub-session 正確收尾 |
| G5 | **漸進式拆分** | 一個大工單被拆成 2-3 個子工單 | 遇到洋蔥問題時正確拆層 |

### 偵測細節

**G1 排除法驅動**：
- 掃描工單回報區和互動紀錄
- 尋找「排除」「確認」「不是 X 而是 Y」等措辭
- 判斷是否為系統性的假設-驗證-排除流程

**G2 對照驗證**：
- 掃描工單中是否包含成功/失敗案例的比較
- 尋找「對比」「成功案例」「與 X 不同的是」等模式

**G3 契約驅動**：
- 偵測工單任務指令或回報區是否引用 `contracts/` 路徑
- 跨專案工單中是否有共用規格引用

**G4 結構化回報**：
- 檢查回報區的「產出摘要」是否有結構化內容（非空、非僅「完成」二字）
- 檢查是否包含「已完成」「未解決」「建議」等區分

**G5 漸進式拆分**：
- 偵測是否有 PARTIAL 狀態的工單後續被拆成多張新工單
- 偵測洋蔥偵測觸發後的正確收尾和新工單建立

---

## 壞的模式 ❌

| # | 模式 | 偵測信號 | 說明 |
|---|------|---------|------|
| B1 | **恐慌驅動** | 同一時段有多張 IN_PROGRESS 工單 | 同時追多條線而不是逐一解決 |
| B2 | **塔台越權** | 決策日誌記錄「塔台直接讀取/修改檔案」 | Tower 違憲行為 |
| B3 | **模糊回報** | 回報區只有「完成」二字，無結構化內容 | sub-session 沒有正確收尾 |
| B4 | **工單膨脹** | 單張工單耗時超過 60 分鐘 | 工單拆分不夠細 |
| B5 | **跳過品質閘門** | 審查工單 DONE 後沒有修正工單 | 審查發現問題但被忽略 |
| B6 | **學習汙染** | `_learnings.md` 中有 ❌ 廢棄模式 | 壞習慣曾被寫入學習記憶庫 |

### 偵測細節

**B1 恐慌驅動**：
- 掃描工單的開始時間和完成時間
- 偵測同一 30 分鐘時段內是否有 3+ 張工單同時處於 IN_PROGRESS
- 排除：PAUSED 狀態的工單不算

**B2 塔台越權**：
- 掃描 `_decision-log.md` 中是否有 Tower 直接操作檔案的記錄
- 掃描 `_tower-state.md` 中是否有違憲標記

**B3 模糊回報**：
- 檢查所有 DONE 工單的回報區
- 「產出摘要」為空或僅含簡短文字（<20 字）判定為模糊

**B4 工單膨脹**：
- 計算每張工單的實際耗時（完成時間 - 開始時間）
- 超過 60 分鐘的工單標記為膨脹

**B5 跳過品質閘門**：
- 偵測審查類工單（任務名稱含「審查」「review」「code review」）
- 審查工單 DONE 後，檢查後續是否有對應的修正工單

**B6 學習汙染**：
- 掃描 `_learnings.md` 中的模式和反模式
- 統計帶 ❌ 廢棄標記的數量

---

## Workflow 適配度 🔀（v5.10.0+）

> 本節是「哪些工單適合以 Claude Code Workflow 執行」的**唯一權威偵測規則**：訊號 S1–S6、排除 X1–X5、判定流程、分級、WFC 候選輸出格式。
> Workflow 的定位、三分法、設計規則、知識卡與成熟度，見 `../../control-tower/references/workflow-engine.md`（唯一權威）。
> 來源：T0177 報告 § 3、§ 4、§ 6、§ 8、§ 10（使用者抽驗 30／30 認同，D081）。
> 本節只產出**候選**；把候選寫成 brief 與知識卡是 `ct-evolve --workflow` 的事，本版不派發、不執行 Workflow。
> v5.11.0+：預篩腳本的角色（排除守門＋按需提示）與塔台入口 `*insights workflow` 見 § 預篩腳本：排除守門與按需提示（本節唯一權威）。

### 判定流程

```
任一 X1–X4 成立 ─────────────────────────────▶ 排除（記錄是哪一條）
X5 成立（序列重複但單張不扇出）───────────────▶ 改列 Playbook／範本候選
否則：
  扇出軌  S1（嚴格）且 S6 ──────────────────────▶ pipeline／loop-until-dry 候選
  驗證軌  同形族 S3 事件 ≥ 2，或 S4 有 ≥ 3 個可獨立評估的方案 ─▶ adversarial-verify／judge-panel 候選
  兩軌都成立 ───────────────────────────────▶ pipeline＋adversarial-verify
  兩軌都不成立 ─────────────────────────────▶ 一般執行
附註（不排除，只記錄）：X1-延後、X2-弱、規模小（單一 agent ≤ 15 分）、S5、自發扇出
```

**兩條軌道**：扇出軌（S1＋S6）找「單張內可以平行做的同形子任務」；驗證軌（S3 事件）找「過去常被推翻、值得加一層獨立複核的工作」。
X1–X4 對兩軌都適用；X5 不算 Workflow 訊號，把工單轉去 Playbook／範本。

### 訊號

| # | 模式 | 偵測信號 | 說明 |
|---|------|---------|------|
| S1 | **可扇出（嚴格）** | 任務指令或執行步驟出現「對每個…」「逐一…」後接清單；清單項目屬同一類；`affects_files` 每項對應一個子項（輔助） | 工單**明文給定** N ≥ 3 個同類項目，逐一做同一套處理；項目可獨立執行、不寫同一個檔，而且**執行前就能列出**（可寫成 `args`） |
| S2 | **重複** | 同一族內，經複核確認同形、且每張 S1 成立的成員數 ≥ 3 | 「同形」依**形狀三元組**判定：子任務來源 × 階段結構 × 驗收方式（不依主題） |
| S3 | **誤報或重工**（驗證軌主訊號） | `status` 曾是 PARTIAL 後被改判、`renew_count > 0`、內文出現「改判」「推翻」「與…不符」，或後續工單引用本單並更正 | 結論被推翻、塔台改判、事後補漏，或後續工單證明本單錯誤；以族為單位累計 |
| S4 | **N 選一研究**（低權重） | 「方案 A/B/C」「Route A/B/C」並列，各方案的評估不依賴同一份盤點 | 比較 ≥ 3 個**可以獨立評估**的方案；只是驗證軌的形狀提示 |
| S5 | **單一 context 裝不下**（輔助註記，不計分） | 「Context Window 風險：高」「context 不足 → PARTIAL」、拆單紀錄 | 只用來在設計階段估分批大小 |
| S6 | **子項獨立、可結構化驗收**（扇出軌必要條件） | 驗收條件寫「每項…」並給固定欄位；**沒有**「基於 Step N 結論」「同一個 runtime」「describe.serial」這類串行字樣 | 子項之間不共用狀態、不依賴前一步結論；每個子項有固定欄位或 PASS/FAIL，能映射到報告區段。**反條件**：共用狀態或串行依賴 → S6 不成立，只擋扇出軌，不排除整張（驗證層仍可能有效） |

### 排除條件

| # | 模式 | 偵測信號 | 說明 |
|---|------|---------|------|
| X1 | **單內人工 runtime 驗證** | 驗收條件寫「使用者目視」「實機」「安裝版」；標題含「實機驗收」「探針」並有安裝版步驟 | 單內需要 GUI 或硬體的人工驗證。延後到下游工單的人工驗收**不排除**，記為 **X1-延後** |
| X2 | **執行中需要人即時回答** | 三個來源任一處有內容即成立（見偵測細節） | **X2-弱**（只記錄、不排除）：決策放在單後的待決清單；執行中被追加範圍 |
| X3 | **跨 session、跨天** | `started_at` 與 `completed_at` 不同天；出現 `## 塔台補充（Renew #N）`；`renew_count > 0`；回報區寫「接續上一個 session」 | — |
| X4 | **機械批次** | 執行步驟是單一指令；`affects_files` 只有 1 個檔；回報區寫「純盤點無阻礙」且沒有判斷紀錄 | 符合任一即成立：(a) 一支腳本或一條指令可跑完；(b) 同一個編輯套用 N 次，或修改集中在同一個檔、彼此耦合；(c) 全程不需要判斷 |
| X5 | **序列重複但單張不扇出** | S2 的同形成立，而單張 S1 不成立；`depends_on` 指向同系列的前一張；同一個 PLAN 依序派出 | 改列 **Playbook／範本候選**，不算 Workflow 訊號 |

### 偵測細節

**S1 可扇出（嚴格）**：
- 只看指令區：`## 任務指令`、`### Step N`、驗收條件裡的清單或表格；**不看回報區**
- 不成立的典型：N 項全改在同一檔；一條指令跑完 N 個 spec；N 只是表格列數；N 要執行中才知道（不能寫成 `args`）

**S2 重複**：
- 先把紀錄正規化成工單層級（同一張工單的多份報告只算一次）
- 依形狀三元組分群，不依主題或標題；族名和證據不符、或族過大時重新聚類

**S3 誤報或重工**：
- 來源：frontmatter `status`／`renew_count`、`## 塔台收單`、`## 塔台補充（Renew #N）`、決策日誌、學習紀錄、後續工單內文
- 塔台複驗全部 PASS、沒有改判 → 不算

**S4 N 選一研究**：
- 只有 2 個方案，或各方案共用同一份盤點 → 不算

**S6 子項獨立**：
- 讀驗收條件、報告模板與執行步驟的依賴字樣
- 共用同一個父元件、同一份盤點、同一個 runtime 狀態 → 不成立

**X1 人工 runtime 驗證**：
- 讀驗收條件、標題、`type`，以及回報區的證據分道（runtime／installed）
- 明文禁止啟動 app、runtime 驗證留給後續工單 → X1-延後，不排除

**X2 執行中需要人回答**（三個來源，去掉 fenced code block 後判斷）：
1. `### 待塔台決策` 下有 `#### Q-n`
2. 以 `- **塔台答覆 Q-n**` 開頭的行
3. `### 互動紀錄`（或 `**互動紀錄**`）下的 Q/A 條目：清單 `[HH:MM] Q…→ A…`，或表格 `| Q1 |`
- 內容是「無」「（無）」不算；只開了互動模式、沒有提問也不算
- BAT 塔台提問只存在記憶體、不落檔，**不能**用 BAT 的提問紀錄偵測

**X3 跨 session**：讀 frontmatter、Renew 段、回報區

**X4 機械批次**：
- 讀執行步驟、`affects_files`、回報區的修改檔清單
- **名稱含 batch ≠ 適合 workflow**：標題關鍵字（`batch`、`audit`、`probe`、「批次」）不當訊號用；例：20 個 BUG 套用同一個編輯的「batch」工單是 X4
- 「單一 agent 15 分鐘內完成」**不是**排除條件，只記為「規模小」（用時間排除會把驗證軌的正例全部排掉）
- 每個子項都要判斷（例：逐個套件判斷 breaking change）→ 不是 X4

**X5 序列重複**：讀標題與模板相似度、`depends_on`、PLAN 的子單列表；兩張依序、但單張內各有可扇出的子項 → 不是 X5，看 S1

**輔助訊號：Worker 自發扇出**（不單獨成立）：
- 回報區出現「子代理」「sub-agent」「Explore」「平行盤點」，且 Worker 實際以多個唯讀子代理分工、主 agent 再抽查
- 只用來**支持**某族的扇出軌或驗證軌判定（例：補強 S1／S3 的證據），不能單獨讓工單成為候選；記在附註

### 分級（不用 0–100 分數）

| 等級 | 扇出軌 | 驗證軌 |
|---|---|---|
| 🔵 候選 | 無 X1–X5；複核確認的同形成員 ≥ 3，**而且**每張都 S1（嚴格）且 S6 | 無 X1–X5；同形成員 ≥ 2，而且族內 S3 事件 ≥ 2 |
| 邊界 | 只有 1–2 張同形；或 S6 部分成立（例如共用一個前置步驟） | S3 事件只有 1 次，或只有 S4 |
| 排除 | 任一 X1–X4，或 X5 | 同左 |

- 附註（X1-延後、X2-弱、規模小、S5、自發扇出）只記錄，不影響等級
- 正式列為 🔵 候選之前，要回到證據工單內文**複核**，寫出複核結論
- 若之後要排序，分數只排序**同一等級內**的候選，不跨等級比較、不拿絕對值當門檻

### 輸出格式

每個候選一段，格式固定：

```markdown
### WFC###: <候選名稱（依形狀命名，不依主題）>
- **軌道／形狀**：扇出軌 pipeline｜loop-until-dry；驗證軌 adversarial-verify｜judge-panel；或兩軌組合
- **形狀三元組**：子任務來源 × 階段結構 × 驗收方式
- **證據工單**：T####、T####（同形成員 N 張，其中複核確認 M 張；每張附命中的 S）
- **子任務來源**：<工單內清單／檔案 glob／git log／args>；**args 可行性**：執行前可列｜執行中才產生
- **S3 事件**：<工單：推翻、改判或補漏的一句描述>（驗證軌必填）
- **排除檢查**：X1–X5 的結果，以及附註（X1-延後、X2-弱、規模小、自發扇出）
- **基準**：單一 agent 實際耗時 <分>；預估規模 N 個子任務 × ~k tokens ＋ 每個 agent 固定開銷 ~31k
- **等級**：🔵 候選｜邊界｜排除
- **複核結論**：成立｜weakened｜refuted，附一句理由與複核日期
- **狀態**：🔵 候選
```

另外兩份清單，格式固定：

- **Playbook／範本候選（X5）**：系列名｜工單範圍｜共同模板｜建議落點（`_playbooks/` 或派工範本）
- **邊界案例**：工單｜疑義點（一句）｜需要誰判斷（使用者或塔台）

🔵 候選可由 `ct-evolve` 加 `[WF-CANDIDATE]` 標記；寫成 brief 與知識卡用 `ct-evolve --workflow`（見 `ct-evolve/SKILL.md`）。

### 預篩腳本：排除守門與按需提示（v5.11.0+）

> 來源：D085 選項 (C)（T0179 報告 § 5）；腳本由 T0179 撰寫，T0183 修 E4–E6 後隨本 skill 發行。

**腳本**：`ct-insights/scripts/ct-workflow-prefilter.py`。只用 Python 3 標準函式庫，不呼叫 LLM、不花 workflow token；
所有輸入只讀，除非給 `--jsonl`，否則不寫任何檔。它把本節的規則寫成 regex 與門檻，**判定以本節條文為準**，兩者不一致時改腳本。

腳本只有兩個角色：

1. **排除守門**：命中 **X2、X3、X5** 的工單，塔台**不考慮 Workflow**；其中 X5 改提示 **Playbook／範本**（列進 Playbook／範本候選清單）。
   只用這三條，是因為腳本對它們最可靠：BAT 校準時 X2 召回 74%、只多抓 2 張，和 T0177 人工定案相同；X3、X5 中等。
   X1、X4 在腳本裡是啟發式（BAT 校準召回 25%、15%），**不拿來守門**，只在輸出標「需人工」。
2. **按需提示**：**只在塔台主動呼叫時**（收單、規劃、使用者問「這張適不適合 Workflow」）列出候選與證據位置（檔案與行號）。
   🔴 **不自動標記工單**：不在派工流程裡自動跑、不改工單、不寫 `WFC###`、不加 `[WF-CANDIDATE]`。
   提示只是「去看這幾行」——候選要升成 🔵 或寫授權，仍要回到工單內文依上方規則人工複核（S1 嚴格的「同一套處理」、S6 一定要人工判）。

**塔台入口**（`control-tower/SKILL.md` 命令表只放摘要，指回這裡）：

| 命令 | 執行 | 輸出 |
|---|---|---|
| `*insights workflow` | `python "<ct-insights>/scripts/ct-workflow-prefilter.py" _ct-workorders` | 規則命中率、分軌、**排除守門統計**、前 N 名候選（`--top N`，預設 10）與證據位置 |
| `*insights workflow T#### [T#### …]` | 同上，加 `--ids T####,T####` | 逐張：守門結論（`不考慮 Workflow`／`不考慮 Workflow；提示 Playbook`／`未擋下`）、守門命中與證據、主判定（全部 X 套用）、需人工的項目、證據位置 |

- `<ct-insights>` 是**已載入的 `ct-insights` skill 所在目錄**（放它 `SKILL.md` 的那一層，v6.0.0-beta.5+）；塔台只載入 `control-tower` 時，用和 `control-tower`
  skill 目錄同一層的 `ct-insights` 目錄。8 個 CT skill 不論手動安裝或 plugin 安裝都是兄弟目錄，所以兩種安裝方式都成立；不要寫死
  `~/.claude/skills`、`~/.codex/skills`（plugin 安裝時不在那裡）。腳本本身不依賴安裝位置（只讀命令列給的路徑）。
  X5 要看整個目錄才判得出系列，所以給 `--ids` 時仍掃整個 `_ct-workorders/`，只輸出指定的工單。
- 直譯器名稱依平台（Windows 多半是 `python`，macOS／Linux 多半是 `python3`）。Windows 上從 Git Bash 呼叫時，Windows 版 Python 讀不到
  `/c/...` 形式的路徑，腳本路徑先轉成 Windows 形式（`cygpath -w`）；`_ct-workorders` 這類相對路徑不受影響。找不到 Python 3：說明原因，改依本節條文人工判定那幾張；不安裝套件、不改用其他腳本。
- 三個 `workflow_integration` 值下都可以跑（0 workflow token）；值的定義在 `control-tower/references/tower-config.md` § 可用選項。
- 守門擋的是 **Workflow 工具**。Worker 自己用一般 Agent 工具開唯讀子代理平行讀取，不受 X2 守門限制（例：專案 A T0081
  同時有即時問答與 5 個唯讀子代理），但要依 `ct-exec/SKILL.md` § Workflow And Sub-Agents 記在回報區。

**v5.11.0 的修正（T0179 報告 § 4 的 E4–E6）**：

| 代號 | 修正 | 腳本實作 |
|---|---|---|
| E5 | X2 加兩個來源：④ `intervention_type: decision-requiring`、⑤「DP 裁定紀錄」 | ④ frontmatter 頂層或 `interaction:` 底下，或內文元資料的鏡像行；⑤ 標題或粗體含「DP 裁定紀錄」，且段落有表格資料列或清單項（「無」不算） |
| E6 | S1 的 cue 也看 `title` | 標題當一個 cue 來源；標題沒有清單可數，只取 cue 子句的數量，執行前可列與否照「cue 行只寫數量」的規則（指向具體來源才算） |
| E4 | X4(a) 補「逐一＋複製／雜湊／計數」 | 指令區同一行「逐一／逐檔…」前後 30 字內有複製、雜湊（SHA、MD5、hash）、計數（count、`wc -l`） |

其他已知限制（E1–E3、E7、E8：背景句數量、異質清單、同一檔彙整、子代理關鍵字誤觸、串行依賴）腳本修不了，靠人工複核。

---

## Session 用量統計（`*insights sessions`，v6.0.0-beta.10+）

> 來源：EXP-SESSIONLOG-001（T0391）〈給 PLAN-004 ⑥ 的規格建議〉、PLAN-004〈⑥ 規格追加〉、D511／D512／D517／D520；腳本由 T0394 撰寫。
> 本節是 session 用量統計（腳本角色、歸屬、隱私、降級、輸出解讀、快照與候選事實格式）的**唯一權威**；同一支腳本的工具清單建議（`--tools`）見下一節〈工具清單建議〉；
> 塔台何時寫快照、何時補記 session id 見 `control-tower/references/work-order-system.md` § 收單補記 session id、§ 收單快照。

**用途**：回答「每張工單、每個塔台 session 花了多少 token」。以 Claude Code 本機 session 紀錄
（Claude Code 專案紀錄目錄下、以專案路徑編碼命名的子目錄裡的 `<session id>.jsonl`）算出每張工單的 token、工具與 MCP 使用、失敗與失敗密度、
估算成本；塔台用量另列；結果可寫成只有數字的快照，並由快照產生給 ct-evolve 的候選事實（接法見 `ct-evolve/SKILL.md` § Session Evidence）。

**腳本**：`ct-insights/scripts/ct-session-stats.py`（價目表 `pricing.json` 在同目錄；測試 `scripts/tests/test_ct_session_stats.py`）。
和預篩腳本相同的做法：只用 Python 3 標準函式庫、只讀、不呼叫模型、不連網、🔴 **不自動標記或修改工單**。
只有 `--snapshot-append`、`--facts` 會寫到命令列指定的檔案。規則以本節為準，兩者不一致時改腳本。

**範圍**：只做 Claude Code（D507 Q5＝[A]）；Codex、Copilot 不做；`<session id>/workflows/` 目錄不讀（Workflow 代理沒有併入）。

### 塔台入口

`control-tower/SKILL.md` 命令表只放摘要，指回這裡。在 repo 根目錄執行（`--project` 省略時由目前目錄推算）：

| 命令 | 執行 | 輸出 |
|---|---|---|
| `*insights sessions` | `python "<ct-insights>/scripts/ct-session-stats.py" --workorders-dir _ct-workorders --days 30 --decision-log _ct-workorders/_decision-log.md --decision-log _ct-workorders/_archive/decisions --snapshot-append _ct-workorders/_insights/session-stats/<YYYY-MM>.json` | 摘要表（每張工單一列）、覆蓋率、塔台另列、卡住訊號、依決策切的「估」欄；同時把還沒有快照的工單補進快照 |
| `*insights sessions T#### [T#### …]` | 同上，加 `--workorders T####,T####`（`--days` 可省略） | 只列這些工單；塔台 session 只取和它們時間重疊的 |
| `*insights sessions … --since … --until …` | 同上，改用 `--since`／`--until`（取代 `--days`） | 指定期間 |

- `<ct-insights>` 的解析、直譯器名稱、Git Bash 路徑轉換，與 § 預篩腳本 相同。`<YYYY-MM>` 是寫入當下的月份（本機時間）。
- 要給使用者看 JSON 時加 `--json`；要附逐 session 明細加 `--sessions`；要附 session id 加 `--with-session-ids`（預設不附）。
- 找不到 Python 3：說明原因並寫「資料不可用」，不安裝套件、不改用其他腳本。

| 參數 | 說明 |
|---|---|
| `--projects-dir` | 預設 `~/.claude/projects` |
| `--project` | 編碼後的專案目錄名（路徑中英數與 `-` 以外的字元都換成 `-`），可給多次（例：隔離工單的 worktree 路徑另有自己的目錄；同一個 session id 只算一次）；省略時由目前目錄推算 |
| `--workorders-dir` | `_ct-workorders`：讀工單 frontmatter 的 `id`、`type`、`session_ids`，以及 `_tower-state.md`（含 `_archive/` 下的塔台狀態）的塔台 session id |
| `--workorders T####,…` | 只算這些工單 |
| `--since` / `--until` | `YYYY-MM-DD`（本機時區當天起訖）或 ISO 8601；依 session 開始時間篩選。`--until` 同時截掉時間晚於它的**紀錄**（紀錄層級，E8：執行中的 session 重跑才會一致） |
| `--days N` | 沒給 `--since` 時取最近 N 天 |
| `--decision-log` | 決策日誌檔或目錄，可給多次（含 `_archive/decisions/`）；給了才輸出 `tower_by_decision` |
| `--bat-log` | 選填：BAT `bat-scripts.log`。讀得到才交叉驗證歸屬；讀不到、沒給都不影響其他結果（🔴 不得依賴它，D517） |
| `--pricing` | 預設同目錄的 `pricing.json` |
| `--json` / `--sessions` / `--with-session-ids` / `--no-subagents` | JSON 輸出／逐 session 明細／附 session id／不併入子代理 |
| `--snapshot-append FILE` | 把工單條目併入快照（見下方〈快照〉） |
| `--facts OUT` | 另寫候選事實 NDJSON（見下方〈候選事實〉） |
| `--facts-from SNAPSHOT` | 只從既有快照（檔或目錄，可多次）產生候選事實，不讀 JSONL；搭配 `--facts` |
| `--self-check FILE` | 只做隱私自檢 |

exit code：`0` 成功；`2` 參數錯誤；`3` 隱私自檢不通過（什麼都不輸出、不寫檔）；`4` 資料不可用（找不到 session 紀錄目錄或沒有 `.jsonl`；`--json` 時輸出 `{"available": false, "reason": …}`）。

### 資料來源與允許欄位

腳本只讀下列欄位，其他一律忽略（新版 Claude Code 加的欄位不影響結果，E8）。每筆 JSONL 紀錄讀進來後立刻投影成只含這些欄位的小 dict。

| 來源 | 讀的欄位 | 用法 |
|---|---|---|
| JSONL 所有紀錄 | `type`、`timestamp`、`version`、`uuid` | 分類、時間、版本 |
| JSONL assistant | `requestId`、`message.id`、`message.model`、`message.usage.*`、`attributionMcpServer`、`cwd` | 去重、token、成本、MCP；`cwd` 只用來判斷檔案是否在 repo 內 |
| JSONL assistant tool_use | `name`、`id`；`input.file_path`／`path`／`notebook_path`；Bash／PowerShell 的 `input.command`；Skill 的 `input.skill`；`Agent`／`Task` 的 `input.subagent_type`（v6.0.0-beta.12+） | 工具次數；路徑只算副檔名、是否在 repo 內、記憶體內雜湊；指令只在記憶體內正規化成雜湊與第一個字；`subagent_type` 只取名稱，沒給記 `<default>` |
| JSONL user | `tool_result.tool_use_id`、`is_error`、`isMeta`、**每一則**真正的使用者訊息（v6.0.0-beta.12+；之前只看第一則）、`cwd` | 失敗；`isMeta` 只用來跳過注入的 meta 紀錄；訊息只比對 ct-exec 工單號與 slash command 名稱（`<command-name>` 或開頭的 `/x`、`$x`，保留命名空間全名）；歸屬 ① 仍只看第一則；`cwd` 只在記憶體內判斷 repo（`--tools`） |
| JSONL `attachment`（v6.0.0-beta.12+） | `skill_listing`、`deferred_tools_delta`、`mcp_instructions_delta`、`agent_listing_delta` 的名稱與長度（欄位見〈工具清單建議〉§ 清單來源） | slash command 只在名稱出現在該 session 的 `skill_listing.names` 時才計；`--tools` 的載入清單。清單與 instructions 的文字只在投影時量長度，不保留 |
| JSONL `api-request-shape`（v6.0.0-beta.12+） | `shape.tools[].name`、`defer_loading`、每個元素序列化後的長度 | 只給 `--tools`：內建工具的每輪 schema 字元 |
| JSONL `custom-title`／`agent-name` | `customTitle`、`agentName` | 只取工單號與 `Worker`／`Tower` |
| 子代理 | `<session id>/subagents/*.jsonl`（同上欄位） | 併入父 session，token 另列 `subagent_tokens`（E6） |
| 工單 frontmatter | `id`、`type`、`session_ids` | ⓪ 歸屬、工單類型 |
| `_tower-state.md` | 「塔台 session」後接反引號包住的 uuid | 塔台角色 ⓪ |
| 決策日誌 | 索引表 `\| D### \| 日期 \| … \|` 的最後一欄、`## D###` 標題、其後第一個 `> YYYY-MM-DD HH:MM (UTC±N)` | `tower_by_decision` |
| BAT log（選填） | `event`、`terminalId`、`workorder`、`session` | ③ 交叉驗證 |
| `pricing.json` | `models.<模型>.{input, output, cache_read, cache_write_5m, cache_write_1h}`（USD／百萬 token）、`as_of` | `est_usd` |

### 歸屬（E2）

同一則 assistant 訊息會拆成約 2 筆紀錄，以 (`message.id`, `requestId`) 去重、只取 `type: assistant`（E1；不去重 token 會灌大一倍多）。

Worker session 的工單歸屬優先序：

1. ⓪ 工單 frontmatter `session_ids` 含這個 session id（ct-exec 收尾寫、塔台收單補記；JSONL 被清掉後仍可對快照）
2. ① 第一則使用者訊息 `^[/$]ct-exec T####`（slash command 展開後的 `<command-name>`＋`<command-args>` 先還原；plugin 安裝的命名空間形式 `/<plugin>:ct-exec` 也算）
3. ② 分頁標題（`custom-title`／`agent-name`）裡的工單號
4. ③ BAT `report-hook.session` 前 8 碼 → `terminalId` → 派工的 `workorder`（**可選**，只交叉驗證）

任兩個來源給出不同工單，或同一個 session id 出現在兩張工單的 `session_ids`，記 `attribution.conflict: true`，照優先序取用；衝突數當健康指標。
`session_ids` 的值不是 UUID（例 `unavailable`）就不算 ⓪。

角色：⓪ 命中 → Worker；session id 在 `_tower-state.md` 的塔台 session 清單 → 塔台；第一則訊息是 `/control-tower` → 塔台；
標題含 `Tower`（且第一則不是 ct-exec）→ 塔台；有工單號 → Worker；其餘 → other。

### 隱私規則

- 輸出、快照、候選事實、回報都**不得**含：對話內容、指令原文、完整檔案路徑、信箱、權杖。
- 指令只輸出第一個字，而且只輸出已知指令或 PowerShell cmdlet；路徑形式的執行檔、檔名、其他字一律代號（`<path>`、`<file>`、`<other>`）。
- 檔案路徑只輸出副檔名與是否在 repo 內；雜湊只在記憶體內計數，不輸出。編碼後的專案目錄名（它就是完整路徑）不輸出。
- session id 不是秘密，但預設不輸出；`--with-session-ids` 才附。
- **自動自檢**：每次輸出（stdout、快照、候選事實）前都先檢查——所有 JSON 字串與鍵符合允許樣式（工單號、版本、時間、工具名、副檔名、session id…），
  全文沒有磁碟路徑、`/Users/`、`.claude/`、`AppData`、` && `、` | `、信箱；環境變數 `BAT_REMOTE_TOKEN` 有值時確認它的值不在輸出裡（只回報有沒有，不印值）。
  命中就不輸出、不寫檔，exit `3`。`--self-check FILE` 可對任何檔案單獨跑同一套檢查。
- 測試只用合成 JSONL；不把真實 session 檔、輸出或快照以外的中間檔放進 repo。

### 降級（不增設定、不阻擋其他流程）

| 情況 | 行為 |
|---|---|
| 找不到 session 紀錄（新機器、被清掉、非 Claude Code） | exit `4`；報告該節寫「資料不可用」；收單快照跳過並在收單訊息註一句 |
| 沒給 `--workorders-dir` | 沒有 ⓪、工單 `type`、塔台 session id；其餘照算 |
| BAT log 沒給或讀不到 | 沒有 ③；結果不變（`source.bat_log: false`） |
| `pricing.json` 讀不到或格式不符 | `est_usd: null` |
| 模型不在價目表 | 該模型的 token 記在 `unpriced_tokens`，不計價 |
| 沒給決策日誌 | 不輸出 `tower_by_decision` |

### 輸出解讀

| 群組 | 欄位 | 解讀 |
|---|---|---|
| 識別 | `workorder`、`type`、`sessions`、`renews`（= sessions − 1）、`versions`、`start`、`end`、`attribution{source, sources, conflict}` | `start`／`end` 是 UTC |
| token | `tokens{input, output, cache_read, cache_write, cache_write_5m, cache_write_1h}`、`subagent_tokens{…}` | 去重後；子代理另列，不和主 session 相加 |
| 成本 | `est_usd`、`unpriced_tokens`、`source.pricing_as_of` | 🔵 **估算（等價 API 成本）**：主 session＋子代理依 `message.model` 與 `pricing.json` 換算。比 `cost-state` 低約 10%（E9），只看趨勢與工單之間比較，不當帳單；訂閱方案不按 token 計費 |
| 工具 | `counts{api_requests, tool_calls, failures, same_file_read_ge3, subagent_files}`、`top_tools`（前 5）、`by_tool`、`failures_by_tool`、`by_mcp_server`、`skills_invoked`、`agents_invoked`（v6.0.0-beta.12+） | v6.0.0-beta.12+：`skills_invoked` = Skill 工具＋使用者 slash command（每一則訊息、保留命名空間全名，例 `/codex:rescue` → `codex:rescue`；名稱不在該 session 的 skill 清單就不計，所以 `/clear`、`/compact` 等內建 CLI 命令與沒有清單紀錄的舊 session 都不計）；`agents_invoked` = `Agent`／`Task` 的 `subagent_type` 次數（`tool_use.id` 去重，沒給記 `<default>`）。兩者都只算主 session，子代理的工具呼叫不併入（子代理只另列 token 與 `subagent_tool_calls`） |
| 卡住 | `stuck{max_failures_in_10_calls, max_consecutive_failures, near_repeat_fail_pairs_j50, repeat_fail_groups_norm}`、`stuck_signal`、整體 `stuck_signals` | 主訊號 `max_failures_in_10_calls >= 3`（任意連續 10 次工具結果裡的失敗數），只是 🔵 **觀察**，不判定工單、不自動標記；門檻未經結果校準（E3）。重複失敗是弱訊號（Worker 很少原樣重跑失敗指令，E4） |
| 整體 | `totals`、`coverage{attributed_worker_sessions, share_of_sessions, worker_sources, conflicts}` | `share_of_sessions` = 歸到工單的 Worker session ÷ 全部 session（T0391：0.863） |
| 塔台另列 | `tower_usage{sessions, tokens, subagent_tokens, est_usd, allocated: false}`、`tower_daily{日期: …}` | **預設，不攤分**（見下） |
| 塔台對照（估） | `tower_by_decision{estimate: true, validated: false, direction: previous-to-this, decisions, related{<工單或 PLAN>: tokens}, general, after_last, share_output_related}` | 只是對照欄（見下） |
| 其他 | `other_usage` | 不是 Worker 也不是塔台的 session |

**不輸出**：turn 數、每 turn 工具數（Worker 九成只有 1 個 turn，沒有分辨力，E3）、塔台攤分到工單的數字。

**塔台用量為什麼不攤分（E5）**：塔台約三分之二的用量發生在沒有任何 Worker 執行的時候（規劃、收單、派工之間）；能攤的三分之一裡又有三成是多張工單同時進行，
攤分結果主要反映並行度，不是工單成本。所以 `tower_usage` 另列、`allocated: false`，工單的數字只含它自己的 Worker session。

**`tower_by_decision`（標「估」）**：PLAN-004 ⑥ 第 2 點要的「依決策時間切」。每個塔台 API 請求歸給**「上一筆～這筆」**的那筆決策
（`direction: previous-to-this`，決策前；〔推論〕塔台通常先做事、後寫決策，收單、開單都是），再平均分給該筆決策索引表最後一欄的相關工單／PLAN；
決策沒有相關 ID → `general`；同一個塔台 session 結束後（加 60 秒）才出現的決策不算，之後沒有決策 → `after_last`。決策時間只到分鐘，所以每筆加 60 秒寬限。
🔴 **未經結果驗證**（`validated: false`）：T0391 量到切法方向一換，超過一半的用量換了歸屬，沒有實際標記能判斷哪個方向對。
只當對照，不當預設、不加進工單成本。**PLAN 用量** = 該 PLAN 關聯工單的 Worker 用量 ＋ 這欄切給該 PLAN 的部分（腳本不推算 PLAN 與工單的關聯，報告時依 PLAN 的工單清單相加，並標「估」）。

### 快照（`ct-session-stats-snapshot/0.2`，E7；v6.0.0-beta.12 起 `0.2`）

Claude Code 預設只保留 session 紀錄 30 天（`cleanupPeriodDays`），換機、手動清理也會讓原始紀錄消失，所以要留只有數字的快照。

- **位置**：`_ct-workorders/_insights/session-stats/<YYYY-MM>.json`（跟著 repo、只有數字；歸屬見 `control-tower/references/data-layer-architecture.md`）。
- **何時寫**：塔台收單時對該工單寫一筆（`control-tower/references/work-order-system.md` § 收單快照）；`*insights sessions` 執行時補寫還沒有快照的工單。不設排程。
- **格式**：

  ```text
  schema, generated_at, generator{script, version}, source{agent, claude_code_versions, pricing_as_of},
  workorders[]{workorder, type, sessions, renews, versions, start, end, attribution{source, sources, conflict},
               tokens{6}, subagent_tokens{6}, est_usd, unpriced_tokens,
               counts{api_requests, tool_calls, failures, same_file_read_ge3, subagent_files},
               stuck{max_failures_in_10_calls, max_consecutive_failures, near_repeat_fail_pairs_j50, repeat_fail_groups_norm},
               stuck_signal, top_tools[[name, count]×≤5], by_tool{}, failures_by_tool{}, by_mcp_server{}, skills_invoked{},
               agents_invoked{}（0.2 起）, session_ids[]（只有 --with-session-ids 時）},
  tower_daily{YYYY-MM-DD（UTC）: {6 個 token 欄位, api_requests}}（塔台 session，含子代理）
  ```

- **併入規則**（`--snapshot-append`）：已在同目錄其他月份快照的工單不重複寫；同一檔已有的工單，新結果的 `sessions` 不少於舊的才取代
  （原始紀錄被清掉時不會蓋掉舊數字）；`tower_daily` 逐日保留 output 較大的那份。同一範圍重跑，除了 `generated_at` 之外結果相同。
- 寫入前同樣過隱私自檢；不通過就不寫。
- **`0.2` 與 `0.1` 的差別**（v6.0.0-beta.12）：加 `agents_invoked`；`skills_invoked` 改為 Skill 工具＋slash command（定義見〈輸出解讀〉）；`generator.version` `0.2.0`。
  `--facts-from`、`--snapshot-append` 的「其他月份已有」判斷照常讀 `0.1` 與 `0.2`；同一個月份檔原本是 `0.1` 時，追加後整檔標 `0.2`，舊條目保留原本的定義（沒有 `agents_invoked`）。
  候選事實 `ct-session-fact/0.1` 不變（只用 `stuck`、`failures_by_tool`）。

### 候選事實（`ct-session-fact/0.1`，給 ⑦）

由快照條目產生（`--facts`；或 `--facts-from` 只讀快照），**不直接讀 JSONL**，所以原始紀錄清掉後仍可重算；NDJSON、一行一筆、鍵排序固定，
同一份快照一定得到同一份事實。本版只產出格式與一條規則；ct-evolve 怎麼讀、怎麼晉升（置信度對應、撤回、去向、觸發）見
`ct-evolve/SKILL.md` § Session Evidence（`/ct-evolve --facts-from <快照或事實檔>`，唯一權威）。

```json
{"schema":"ct-session-fact/0.1","fact_id":"stuck.window10:Bash","rule":"stuck.window10_fail_ge3",
 "subject":{"kind":"tool","name":"Bash"},"workorders":["T0380","T0385"],"days":["2026-10-28","2026-10-30"],
 "evidence":{"metric":"max_failures_in_10_calls","values":[3,4]},
 "counter_evidence":{"workorders":[]},"source":"ct-session-stats 0.1.0 2026-10-02..2026-11-01",
 "confidence":"🔵","state":"candidate"}
```

（工單號與數值是示範用的假資料。）

| 欄位 | 規則 |
|---|---|
| `rule` `stuck.window10_fail_ge3` | 工單的 `max_failures_in_10_calls >= 3`；`subject` 是該單 `failures_by_tool` 最多的工具（同數取名稱排序第一個）；同一工具的工單合成一筆 |
| `days` | 這些工單 `end` 的日期（UTC） |
| `counter_evidence.workorders` | 結束日晚於最後一筆證據、該工具呼叫 ≥ 10 次、而且沒有卡住訊號的工單 |
| `confidence` | 只能是 🔵（進場）或 🟡（`workorders` ≥ 2 張且 `days` ≥ 2 天）；🟢 以上要過 ct-evolve 的 Distillation Gate，⭐ 要使用者認可 |
| `state` | `candidate`；反證 ≥ 2 張 → `withdrawn-candidate`（可恢復）。`❌ 廢棄` 只由使用者決定 |
| `source` | 腳本版本與快照涵蓋的日期範圍 |

計數單位是工單，不是 session。

### 已知限制

- 估算成本比 `cost-state` 低約 10%（E9，原因未證實）；價目要人工更新（`pricing.json` 的 `source`、`as_of`；列入 CT 發版檢查）。
- 卡住門檻、`tower_by_decision` 的方向都未經結果驗證（樣本裡的工單全是 `DONE`）。
- 第一則訊息不是 ct-exec（例：先 `/clear`）、又沒有 ⓪ 與標題的 session 歸不到工單。
- `/clear` 後同一分頁換了新 session id；BAT 只記最後一個（D517），所以 ct-exec 收尾寫的 `session_ids` 是主要來源，收單補記是備援。
- Workflow 代理（`<session id>/workflows/`）、Codex、Copilot 沒有納入。

---

## 工具清單建議（`*insights tools`，v6.0.0-beta.12+）

> 來源：PLAN-006（S0 盤點 T0419、套用手段研究 T0420、S1 規格 T0421、S2 實作 T0422）；D577、D578、D579。
> 本節是工具清單建議（入口、清單來源、計算、判準、套用手段、報告格式、隱私與自檢）的**唯一權威**；設計理由與 S2 修訂見
> PLAN-006 S1 規格（專案內部文件，不隨 skill 發佈）。腳本與 〈Session 用量統計〉 同一支（`ct-session-stats.py --tools`），兩者不一致時改腳本。

**用途**：用本機 Claude Code session 紀錄回答「哪些 skill／plugin／MCP server／agent 類型／內建工具一直載入、卻很少或從來沒用到；要關的話到哪一層、改哪個設定」，
產出一份**建議報告**。每一項都追溯得到同一次統計的數字（PLAN-006 規則 4）。

| 做 | 不做 |
|---|---|
| 列出已載入項目、實際使用次數、依工單類型分組、每輪成本估算 | 🔴 **自動改任何設定**。報告只寫「到哪一層、哪個鍵或介面」，使用者自己改 |
| 各層都建議並標層級：專案、使用者、claude.ai 帳號 | 在 BAT 的 Claude 啟動參數放 `--settings`，或建議用 CLI 旗標套用（D517） |
| 另列「不是移除建議」的問題：同名重複 skill、連線失敗的 MCP、skill 清單被截 | Codex、Copilot |
| 每項附「改完開新 session 生效」 | 閒置偵測、等 session 閒置再套用（期間內清單「移除」事件 0 次，沒有資料能證明中途移除的影響） |
| | 快照與候選事實：`--tools` 不寫快照、不產生 `ct-session-fact`（工具清單是「現在的設定 × 最近的用量」，設定一改就過時） |

### 入口

`control-tower/SKILL.md` 命令表只放摘要，指回這裡。在 repo 根目錄執行；`<ct-insights>` 的解析、直譯器、Git Bash 路徑轉換與 § 預篩腳本 相同。

| 命令 | 執行 | 輸出 |
|---|---|---|
| `*insights tools` | `python "<ct-insights>/scripts/ct-session-stats.py" --tools --workorders-dir _ct-workorders --days 30` | 本 repo 的建議報告（Markdown，stdout） |
| `*insights tools --since … --until …` | 同上，改用 `--since`／`--until` | 指定期間 |
| `*insights tools --all-projects` | 同上，加 `--all-projects` | 跨 repo：掃 Claude Code 專案紀錄目錄下全部專案；其他 repo 一律代號 |
| `*insights tools --keep <名稱>` | 同上，加 `--keep <名稱>`（可多次） | 指定的 skill／plugin／MCP／agent 一律不建議（例：本 repo 的產品 `bmad-guide`） |

| 參數 | 說明 |
|---|---|
| `--json` | 改輸出 `ct-tool-usage/0.1` JSON（見〈報告格式〉） |
| `--out FILE` | 寫檔而不是 stdout；寫前過自檢 |
| `--codes-map FILE` | 跨 repo 代號對照。FILE **已存在就沿用其中的代號、不改寫**（同名 repo 依表中順序對應；表裡沒有的 repo 另編新代號，stderr 只報數量）；不存在才寫。FILE 在任何被掃的 git repo 底下 → exit `2`。對照檔不進任何 repo |
| `--claude-home DIR`、`--claude-json FILE` | 設定來源位置（預設 `~/.claude`、`~/.claude.json`；測試用） |
| `--projects-dir`、`--project`、`--workorders-dir`、`--since`、`--until`、`--days`、`--pricing` | 與〈Session 用量統計〉相同。省略 `--project` 時，本 repo 模式取「編碼後名稱是目前 repo 或其子目錄」的專案目錄，再以 session 的 `cwd` 往上找到的 git 根目錄確認屬於目前 repo |

- `--tools` 不接受 `--snapshot-append`、`--facts`、`--facts-from`、`--with-session-ids`、`--sessions`、`--workorders`、`--decision-log` → exit `2`；`--all-projects`、`--keep`、`--out`、`--codes-map` 沒有 `--tools` → exit `2`。
- exit code：`0` 成功、`2` 參數錯誤、`3` 隱私自檢不通過（不輸出、不寫檔）、`4` 資料不可用（`--json` 時輸出 `{"available": false, "reason": …}`）。
- 找不到 Python 3：說明原因並寫「資料不可用」，不安裝套件、不改用其他腳本。

### 清單來源

**「已載入」以 session 紀錄（JSONL）的附件為準**；設定檔只用來判定層級，不用來推算載入清單。附件記的是實際送進上下文的清單（含執行環境注入的
`bat`、`claude-artifacts`，以及被清單上限截掉說明的 skill），帶字元長度，也記得連不上的 MCP server。只讀主 session 的附件。

| JSONL 紀錄 | 讀的欄位（只取名稱與長度） | 用法 |
|---|---|---|
| `attachment.type: skill_listing` | `names[]`、`isInitial`、`content` 的總長與逐筆長度（每筆 `- <name>: <說明>` 一行；只有 `- <name>` 的是「只剩名稱」） | 載入的 skill、每個 skill 的清單字元、只剩名稱的筆數。基準清單是最長的一份 `isInitial` 清單；之後追加的清單只算載入與逐筆長度 |
| `attachment.type: deferred_tools_delta` | `addedNames[]`、`removedNames[]` 筆數、`failedMcpServers[].name`、`pendingMcpServers[]` | `mcp__<server>__…` → 載入的 MCP server 與名稱字元；連線失敗的 server |
| `attachment.type: mcp_instructions_delta` | `addedNames[]`、`addedBlocks[]` 的逐筆長度、`removedNames[]` 筆數 | 每個 MCP server 的 instructions 字元 |
| `attachment.type: agent_listing_delta` | `addedTypes[]`、`builtInTypes[]`、`builtInPluginTypes[]`、`removedTypes[]` 筆數 | 載入的 agent 類型、哪些是內建 |
| `type: api-request-shape` | `shape.tools[].name`、`defer_loading`、每個元素序列化後的長度 | 非 deferred 的內建工具 schema 字元；`mcp__` 開頭的非 deferred 工具也算該 server 載入 |

- MCP server 名稱轉成工具前綴用的鍵：英數、`_`、`-` 以外換成 `_`（`claude.ai Claude Docs` → `claude_ai_Claude_Docs`、`plugin:presenton:presenton` → `plugin_presenton_presenton`）。
  載入 = 出現在工具名稱、instructions、連線失敗或連線中清單任一處。
- 附件以「追加」累積：一個項目在 session 中出現過任一次就算該 session 載入。`removed*` 只記次數（報告的方法與限制列出）。
- 不讀 `prompt_snapshot`、`api-request-blob`、`instructions`、`session_context` 等其他附件。
- **沒有附件紀錄的 session**（較舊的 Claude Code）不算進該類項目的分母；報告列覆蓋率。

**層級判定**（設定檔只取名稱、`type`、啟用狀態、版號；`env`、`headers`、`args`、`url`、`command` 等值一律不讀出）：

| 項目 | 判定順序 | 層級（報告用字） |
|---|---|---|
| skill `anthropic-skills:<n>` | 前綴即判定 | **claude.ai 帳號**（同步 skill） |
| skill `<plugin>:<n>` | `<plugin>` 是已安裝 plugin（`installed_plugins.json`，或 `~/.claude/plugins/synced/` 下的 `plugin.json` 名稱 → id `<name>@synced`） | 依 plugin；不認得的前綴 → 不明 |
| skill `<n>`（無前綴） | ① 目前 repo 的 `.claude/skills/<n>/`（含 session `cwd` 到 repo 根目錄之間各層的 `.claude/skills/`）→ ② `~/.claude/skills/<n>/` → ③ 其他 repo 的專案層（跨 repo 時）→ ④ 都沒有：出現在至少一半有清單紀錄的 session → Claude Code 內建；否則不明 | ① **專案** ② **使用者** ③ 該 repo ④ 內建／不明 |
| plugin | `installed_plugins.json` 的 scope；synced 目錄 | user → **使用者**；project／local → **專案**；`@synced` → **claude.ai 帳號** |
| MCP `claude_ai_<n>` | 前綴即判定 | **claude.ai 帳號**（connector） |
| MCP `plugin_<plugin>_<n>` | 前綴即判定 | 依 plugin |
| MCP 其他 | ① 目前 repo `.mcp.json` → ② 其他 repo 的 `.mcp.json` → ③ `~/.claude.json` 該專案區 `mcpServers` → ④ `~/.claude.json` 頂層 `mcpServers` → ⑤ 都沒有：`claude-in-chrome` 是 Claude Code 內建整合，其他是執行環境注入（例 `bat`、`claude-artifacts`） | ① **專案** ② 該 repo ③ **使用者**（專案區）④ **使用者** ⑤ 內建／注入 |
| agent 類型 `<plugin>:<n>` | 同 plugin skill | 依 plugin |
| agent 類型（無前綴） | `builtInTypes` 或 `<default>` → 內建；目前 repo `.claude/agents/` → 專案；`~/.claude/agents/` → 使用者；其他 repo → 該 repo；都沒有 → 不明 | 同左 |
| 內建工具 | `api-request-shape` 的非 deferred、不以 `mcp__` 開頭 | Claude Code 內建 |

讀的設定：使用者層 `~/.claude/settings.json`（`enabledPlugins`、`skillOverrides`、`syncClaudeAiSkills`、`enableArtifact`、`disableBundledSkills`、`permissions.deny` 中的裸工具名）、
`~/.claude.json`（頂層 `mcpServers` 鍵；`projects` 中與 repo 根目錄相符那一區的 `mcpServers` 鍵與 `disabledMcpServers`；路徑鍵只在記憶體內比對）、
`~/.claude/plugins/installed_plugins.json`（id、scope、version、安裝目錄只在記憶體內用）、plugin 目錄的 `hooks/hooks.json` 與 `.claude-plugin/plugin.json`（**只取 hook 事件名**）、
`~/.claude/skills/*/SKILL.md` 與 `~/.claude/skills/synced/*/<n>/SKILL.md`（只取名稱與版號）；專案層 `.mcp.json`（鍵）、`.claude/settings.json`、`.claude/settings.local.json`、
`.claude/skills/*/SKILL.md`、`.claude/agents/*.md`（名稱）。版號只取 `<!-- <name>-version: X -->` 或 frontmatter `version`／`current_version`，不符版號樣式記 `<unknown>`。
讀不到設定 → 層級記不明，該項不出建議，其他照算。腳本不呼叫 `claude plugin details` 等 CLI（不啟動其他程式、不連網）。

### 計算規則

**使用次數**（與〈Session 用量統計〉的 `skills_invoked`、`by_mcp_server`、`agents_invoked` 同一份程式；只算主 session）：

| 來源 | 計法 | 歸給 |
|---|---|---|
| Skill 工具 | `tool_use.name == "Skill"` 的 `input.skill` | 該 skill |
| 使用者 slash command | 每一則使用者訊息（跳過 `isMeta`、`tool_result`）的 `<command-name>/x</command-name>` 或開頭的 `/x`、`$x`，保留命名空間全名；名稱在該 session 的 skill 清單才計 | 該 skill（plugin command 歸該 plugin） |
| agent 類型 | `Agent`／`Task` 的 `input.subagent_type`，`tool_use.id` 去重，沒給記 `<default>` | 該 agent 類型 |
| MCP | `mcp__<server>__…` 工具前綴 | 該 server |
| 內建工具 | 工具名稱 | 該工具 |

沒計到的使用（列入方法與限制）：直接讀 skill 檔照做（CT 自己的 skill 常這樣用，所以 CT skill 一律不建議）、Workflow 腳本裡的 `agent()`（`<session>/workflows/` 不讀）、子代理內的呼叫、Codex 端。

**日期**：最後使用日 = 期間內最後一次使用的紀錄時間（本機日期）。資料天數 = 報告結束日 − 期間內第一次載入日 + 1。未使用天數：0 次的項目 = 資料天數；有使用的 = 結束日 − 最後使用日。

**依工單類型分組**（規則 3）：塔台 → `tower`；Worker → 工單 frontmatter `type` 原樣（`implementation`、`impl` 各自一組，不正規化；frontmatter 沒有 `type` → `unknown`）；
CT repo 內不是塔台也歸不到工單 → `other(CT repo)`（JSON 鍵 `other_ct_repo`）；沒有 `_ct-workorders/` 的 repo → `non-CT`（`non_ct`）。歸屬用〈Session 用量統計〉的 ⓪～②（不讀 BAT log）。
每個項目每組記 `loaded`、`used`（session 數）。

**每輪成本**：字元量自附件——skill 是清單中該筆的字元；MCP server 是 deferred 工具名稱字元（每個名稱＋1）＋instructions 字元；內建工具是 schema 序列化後的字元。
每項取有載入的 session 的平均。換算 **2.7 字元／token**，區間 2.3～3.5（T0419 兩個獨立校準；T0420 實測 13 個重複 skill −1,280 token 比字元估算高，報告照字元估算並註明）。
「每輪」= 每次 API 請求都重送（多半以 cache read 計）。

**skill 清單上限**：上限 `C` = 期間內觀察到的基準清單最大長度（每次重算）；貼著上限 = 清單長度 ≥ `C` − 1,500。每個 skill 的完整長度 = 它在期間內任一 session 出現過的最長清單字元。
一個 session 關掉一組 skill `R`：`L` = 目前基準清單長度；需求 = `L` ＋ 只剩名稱的各筆補回說明所需字元；`D'` = 需求 − `R` 各筆的完整長度（未截的用目前長度）；
**省下字元 = max(0, `L` − min(`C`, `D'`))**（`R` 中只在追加清單出現的另加目前長度）。`D'` 仍超過 `C` 時省 0，效果是被截的說明補回來：可補回筆數 = `D'` ≤ `C` 時是全部只剩名稱的筆數，
否則用 `R` 騰出的字元依所需字元由小到大估。報告的 skill 省量一律用這個公式按請求數加權平均（同一列多個 skill 時整組一起算），不把單項字元直接相加。

### 判定（`verdict`）

| 結果 | 報告區 | 條件（依此順序判定） |
|---|---|---|
| `keep` 不建議 | 不建議區 | CT 自己的 skill（`control-tower`、`control-tower-guide`、`ct-exec`、`ct-done`、`ct-status`、`ct-evolve`、`ct-insights`、`ct-help`、`ct-fieldguide`、`ct-adapter-*`，plugin 形式 `ct:*`、`ct-guide:*`；`anthropic-skills:ct-*` 這類同步副本不算）；`--keep` 指定的名稱或 plugin；**核心內建工具**（腳本常數 `TOOLS_CORE_BUILTIN`：`Skill`、`ToolSearch`、`Agent`、`Task`、`Read`、`Write`、`Edit`、`Bash`、`PowerShell`、`Grep`、`Glob`、`AskUserQuestion`、`SendMessage`、`ListAgents`；關掉後 CT 或 Claude Code 基本操作會壞，一律 `keep`，理由「核心工具：CT／Claude Code 運作必需」，v6.0.0-beta.12 T0423） |
| `other_repo` 由該 repo 處理 | 不建議區（跨 repo） | 其他 repo 的專案層項目 |
| `in_use_by_type` 某類型在用 | 不建議區，標「〈組〉在用」 | 任一組 `used` ≥ 3 |
| `no_lever` 無可用手段 | 不建議區，寫「目前只能在〈層〉處理」 | 層級是內建 skill（只有 `disableBundledSkills` 整批）、內建 agent、執行環境注入、內建整合、不明 |
| `connection_failed` | 另列問題（連線失敗） | MCP：載入 ≥ 5 session 且失敗率 ≥ 50%（不進建議表，避免重複） |
| `duplicate` | 另列問題（重複） | 同名重複 skill 中建議關的那一份 |
| `insufficient_data` 資料不足 | 不建議區 | 資料天數 < 14 或載入 session < 20 |
| `recommend` 建議停用 | 建議表 | 期間內 0 次使用 |
| `consider` 可考慮 | 建議表（標「可考慮」） | 使用 session ≤ 2，且最後使用距結束日 ≥ 14 天 |
| `needs_user_decision` 需使用者裁示 | 需使用者裁示區 | 內建工具：使用率（使用 ÷ 載入 session；分子只計同時在載入分母內的使用 session，沒有工具 schema 紀錄的 session 不計，所以 ≤ 1；使用 session 總數照舊另列）< 5% 且每輪 ≥ 500 token；核心內建工具不適用（判 `keep`） |
| `no_action` | 只在 `--json` 的 `items[]` | 其餘（例：使用 session ≥ 3 而沒有任一組 ≥ 3；常用或每輪不到 500 token 的非核心內建工具） |

- plugin 的 skill、MCP、agent 合成一列 plugin（整個 plugin 一起關）：有元件 `keep` → `keep`；任一組在用 → `in_use_by_type`；全部 0 次且都是 `recommend` → `recommend`；有使用但都在 `consider` 範圍 → `consider`；其餘依元件結果。
- 門檻寫成腳本常數，不加設定鍵；報告的方法與限制印出本次使用的門檻值。理由：資料天數 14 天約為預設保留 30 天的一半（T0419 的 `presenton`、`slideops` 14 天、0 次，判斷清楚）；
  載入 20 session 以下 0 次沒有意義；規則 3 用絕對次數 ≥ 3（比例門檻會漏掉 `workflow-authoring` research 3／152 這類確實在用的）；`consider` 的 1～2 次多半是單次嘗試，最近 14 天內用過的不提。

### 套用手段

**所有建議都附「改完開新 session 生效」。** 驗證：文件＝官方文件明載；實測＝T0420 或 T0422 在 CLI 2.1.316 以 `claude -p` 實測；觀察＝T0419 的使用紀錄；未驗證＝照寫但標「未驗證」。

| 項目來源 | 建議手段（層級：檔案或介面 → 鍵與值） | 驗證 | 🔴 不寫成建議 |
|---|---|---|---|
| claude.ai 同步 skill `anthropic-skills:<n>` | **專案**：`.claude/settings.json` → `skillOverrides` → `"anthropic-skills:<n>": "off"`（要保留名稱用 `"name-only"`）。🔴 鍵一律用**完整前綴名** | 實測（T0420 r2、r5；T0422 v2 再驗：兩個前綴名都移出 `init.skills`）；文件未寫，報告註明 | 裸名 `"<n>"`：先關到使用者層同名 skill（T0420 r4）。專案層 `syncClaudeAiSkills: false`：被忽略 |
| 同上，所有專案都不要 | **使用者**：`~/.claude/settings.json` → `syncClaudeAiSkills: false`；或 **claude.ai 帳號**的 skills 設定逐項關 | 文件 | 放 `.claude/settings.local.json` 的效果未實測，不寫成建議 |
| 使用者層 skill `<n>` | **專案**：`.claude/settings.json` → `skillOverrides` → `"<n>": "off"`（裸名先命中使用者層）；或 **使用者**：移除 `~/.claude/skills/<name>/` | 實測（T0420 r4）＋文件 | — |
| 專案層 skill（目前 repo） | **專案**：`.claude/settings.json` → `skillOverrides`；或移除 `.claude/skills/<name>/` | 文件 | 跨 repo 時其他 repo 的不出鍵值，寫「由〈代號〉處理」 |
| plugin（含其 skill、command、agent、MCP） | **專案**：`.claude/settings.json` → `enabledPlugins` → `"<plugin>@<marketplace>": false`；或 **使用者**：`~/.claude/settings.json` 同鍵。整個 plugin 一起關；**列出該 plugin 的 hook 事件，註明「關 plugin 會一起停掉這些 hook」** | 文件 | `skillOverrides` 關 plugin skill：文件明載不適用 |
| claude.ai 同步 plugin（`@synced`） | **claude.ai 帳號**的 plugin 設定；或 **專案**：`.claude/settings.json` → `enabledPlugins` → `"<plugin>@synced": false` | 帳號：觀察；`enabledPlugins`：**實測**（T0422 v3：`"presenton@synced": false` 讓該 plugin 的 skill 與 MCP server 都移出清單）、文件未寫 | — |
| 使用者層 MCP | **使用者**：`~/.claude.json` 頂層 `mcpServers` 移除（介面 `/mcp` 或 `claude mcp remove <name> -s user`）；只在某專案停用：`~/.claude.json` 該專案區 `disabledMcpServers`（介面 `/mcp`） | 觀察 | — |
| 使用者層 MCP（專案區） | **使用者**：`~/.claude.json` 該專案區 `mcpServers` 移除（介面 `/mcp`） | 觀察 | — |
| 專案層 MCP（目前 repo） | **專案**：`.mcp.json` 移除 | 文件 | 跨 repo 時寫「由〈代號〉處理」 |
| claude.ai connector | **claude.ai 帳號**的 connector 設定 | 觀察 | 專案層停用方式未驗證，不寫成專案建議 |
| 使用者層／專案層 agent 定義 | 移除該 agent 定義檔 | 未驗證 | — |
| Claude Code 內建工具 | 只列在需使用者裁示區（下一小節） | — | scoped 規則 `Tool(...)`：只拒絕呼叫、不省 token（T0420 ②）；`--settings`、CLI `--disallowedTools`（D517） |

JSON 的 `lever.location` 只能是固定集合：`project_settings`、`project_settings_local`、`project_mcp_json`、`project_skills_dir`、`project_agents_dir`、`user_settings`、`user_claude_json`、
`user_claude_json_project`、`user_skills_dir`、`user_agents_dir`、`claude_ai_account`、`none`；`verified` 只能是 `documented`、`measured`、`observed`、`unverified`。

#### 需使用者裁示：內建工具

條件：內建工具、使用率 < 5%、每輪 ≥ 500 token（例：`Artifact` ≈14k token／輪、使用率 4.8%）。核心內建工具（`TOOLS_CORE_BUILTIN`，清單見判定表 `keep` 列）不適用：一律判 `keep`、列在不建議區，不進本區也不進建議表（T0423：`Skill` 使用率 4.7%、≈679 token 曾命中本條件）。`Workflow`、`Artifact`、`ScheduleWakeup`、`ReportFindings`、`SendFeedback` 這類選用功能不算核心工具，照本條件判定。

- 手段：**專案** `.claude/settings.json` → `"enableArtifact": false`（Artifact 專用，首選）或 `permissions.deny: ["<Tool>"]`（**裸工具名**才會移出清單；T0420 以 `Workflow` 實測 −1,948 token）。
- 每項必附：① **單向**：`enableArtifact` 任何設定檔設 `false` 之後沒有檔案能再打開；`permissions.deny` 的單向性未驗證。② **塔台與 Worker 共用**專案設定（`.claude/settings.local.json` 也是同一個 repo 目錄共用），無法只關 Worker。
  ③ 工具專屬的影響：`Artifact` →「關掉後塔台也不能發 Artifact」；`Workflow` →「CT 的 Workflow 授權工單無法執行」；`ScheduleWakeup` →「`/loop` 自訂節奏無法使用」；其他寫「影響未評估」。
  ④「套用後在互動 session 用 `/context` 或下一次 `*insights tools` 確認已移出清單」（`claude -p` 沒有 `Artifact`，只能在互動 session 確認）。

#### 另列問題（不算工具移除建議）

| 問題 | 偵測 | 報告內容與處理 |
|---|---|---|
| **同名重複 skill** | 使用者層或目前 repo 專案層的 `<n>`，與 `anthropic-skills:<n>` 都在期間內載入 | 列兩邊版號、各自使用 session、同步副本每輪字元；**版號不同時標 ⚠️**（模型可能挑到舊版）。建議關使用次數少的那份，平手關同步副本；關同步副本用完整前綴名 |
| **連線失敗的 MCP server** | 載入 ≥ 5 session 且失敗率 ≥ 50% | 列失敗率、層級與對應手段；註明「每輪 0 token，省的是啟動時的連線嘗試與失敗通知」「本機服務沒開造成的，要用時開服務即可，不一定要移除」 |
| **skill 清單被截** | 貼著上限的 session ≥ 50% | 列比例、`C`、只剩名稱的 skill 數中位數、最常被截的通用名稱（專案專屬名稱只給數量）；處理指向重複 skill 與建議表的 skill（關掉後說明補回） |

### 報告格式

**Markdown**（預設）：① 標題列（期間、範圍、session 數、產出時間、腳本版本）② 結論摘要（建議停用幾項幾列、每輪約省：MCP 部分與 skill 清單部分、需使用者裁示幾項、另列問題、
「只出建議，不自動改設定；改完開新 session 生效」）③ 建議表（`| # | 項目 | 層級 | 設定鍵／介面 | 30 天用量 | 每輪約省 | 注意 |`；`recommend` 在前、依每輪約省中值由大到小；
同種類、同層級、同判定的合成一列，鍵值用 `<name>`）④ 需使用者裁示 ⑤ 另列問題（三類各一張小表）⑥ 不建議與資料不足（項目、結果、理由）⑦ 方法與限制（期間與範圍、附件覆蓋率、
使用次數的來源與沒計到的、換算比與誤差、`C` 的實際值、門檻值、清單移除事件次數、跨 repo 代號說明）。Markdown 由已通過 JSON 自檢的資料加固定句型產生，不帶入原始紀錄的文字。

**JSON**（`--json`，`ct-tool-usage/0.1`）：

```text
schema, generated_at, generator{script, version}, period{since, until, start_date, end_date, data_days_max},
scope{all_projects, projects[], sessions, by_group{<組>: n}, by_project{<代號>: n}},
coverage{skill_listing, mcp_listing, agent_listing, tool_shape}, thresholds{…, chars_per_token{mid, low, high}, listing_cap_chars, listing_near_cap_chars},
listing{sessions, near_cap_sessions, near_cap_share, names_only_median}, summary{…}, row_savings{<判定>:skill:<層級細項>: …}, removed_entries,
project_specific{skill, mcp, agent, used}, privacy{other_repo_names, exempt_colliding_with_generic},
items[]{kind: skill|mcp|agent|builtin_tool, name, plugin, layer: project|user|claude_ai|builtin|injected|unknown, layer_detail, repo_codes[], version,
        lever{layer, location, key, entry, value, verified[, what]}, lever_alternatives[], loaded_sessions, failed_sessions, used_sessions,
        calls{skill_tool, slash, agent, mcp, tool}, first_loaded, last_used, data_days, unused_days, by_group{<組>: {loaded, used}},
        chars_per_turn, tokens_per_turn{mid, low, high}, saving_per_turn{mid, low, high}, verdict, in_use_groups[], notes[],
        use_rate（只有 builtin_tool）, saving_max_chars, restored_descriptions（只有 skill）, plugin_verdict（只有屬於 plugin 的項目）},
plugins[]{name, id, layer, version, hooks[], components{skill, mcp, agent}, verdict, tokens_per_turn, saving_per_turn, saving_detail, lever, …},
issues[]{kind: duplicate|mcp_failure|listing_truncated, names[], …}
```

`use_rate` = 使用率，定義同〈判定〉表 `needs_user_decision` 列：分子只計同時在載入分母內的使用 session，所以 ≤ 1，四捨五入到小數 4 位；`used_sessions` 照舊是使用 session 總數。
`plugin_verdict` 是該元件所屬 plugin 列的判定（見〈判定〉表下 plugin 合成規則）。

`notes[]` 只放代碼（例 `one_way`、`shared_tower_worker`、`hooks_stop_together`、`undocumented_measured`、`synced_plugin_measured`、`restart_session`），由 Markdown 換成中文句子，
所以 JSON 的每個字串仍能套用允許樣式自檢。

### 隱私與自檢

沿用〈Session 用量統計〉§ 隱私規則，另加：

| 可輸出 | 不可輸出 |
|---|---|
| skill／plugin／MCP server／agent 類型／內建工具的**通用名稱**、層級、版號、次數、日期、字元數、token 估算、hook **事件名** | 對話內容、清單與 instructions 的**文字**、指令原文、完整路徑、編碼目錄名、信箱、權杖 |
| 設定檔的**鍵名**與固定位置名稱 | 設定檔 `env`、`headers`、`args`、`url`、`command` 的值；`~/.claude.json` `projects` 的路徑鍵 |
| 其他 repo 的代號 `P01`… | 其他 repo 的名稱、路徑、專案專屬 skill 名稱 |

- **通用名稱**：Claude Code 內建、使用者層、claude.ai 同步、plugin、connector、`bmad-*`、目前 repo 自己的專案層 skill；設定檔認得的名稱一律可列。
  **專案專屬名稱**（其他 repo 的專案層 skill、含其他 repo 名稱的名稱、不合名稱樣式的名稱）只給數量（D510）。看起來像內建、但只出現在一個其他 repo 的名稱也只給數量（巢狀的專案 skill 會像內建）。
- **跨 repo 代號**：依 session `cwd` 往上找 git 根目錄合併成 repo（worktree 的 `.git` 檔指回主 repo）；找不到 git 根目錄的工作目錄自成一個代號。目前 repo 用本名，其他依 session 數由多到少編 `P01`…（同數依第一次 session 時間）；
  `--codes-map` 已存在時沿用。其他 repo 的工單類型讀該 repo `_ct-workorders/` 的 frontmatter `id`、`type`、`session_ids`，只用於分組。session id 不輸出。
- **自檢**依輸出種類分兩套。不通過：不輸出、不寫檔，exit `3`，只印命中的檢查項編號（不印命中的字串）。

| 輸出 | 檢查 |
|---|---|
| JSON（`--json`） | 既有 `check_text()`：所有鍵與字串符合允許樣式＋禁止樣式＋權杖值；允許樣式加 `ct-tool-usage/0.1`、plugin id（`<name>@<marketplace>`）、`<default>`、`<current>` |
| Markdown（預設輸出、`--out`、`--self-check FILE.md`） | `check_report_text()`：① 權杖值（`BAT_REMOTE_TOKEN` 有值時）② 信箱 ③ 磁碟路徑（`X:\`、`X:/`、`/Users/`、`/home/`、`AppData`、`\\`）④ 編碼目錄名樣式（`X--` 開頭的連字號長字串）⑤ `.claude` 只允許出現在 `~/.claude/settings.json`、`~/.claude.json`、`.claude/settings.json`、`.claude/settings.local.json`、`~/.claude/skills/<name>/`、`.claude/skills/<name>/` ⑥ 其他 repo 名稱（記憶體內取得的 git repo 目錄名，整字比對、不分大小寫）⑦ ` && `。表格的 `\|` 允許 |

- ⑥ 只比對 git repo 的目錄名；和報告裡列出的通用名稱撞名的 repo 名稱（例：在某個 skill 目錄裡開的 session）無法區分，不列入 ⑥，JSON `privacy.exempt_colliding_with_generic` 記數量。
- 塔台在報告外另寫的文字（轉貼進工單、決策日誌）要再跑 `--self-check FILE`：副檔名 `.md` 走 Markdown 檢查；要比對其他 repo 名稱時加 `--all-projects`。

### 已知限制

1. 同步 skill 與同步 plugin 適用 `skillOverrides`／`enabledPlugins` 是實測行為、文件未寫（CLI 2.1.316）；Claude Code 改版可能失效，每次發版前可用 `claude -p … --output-format stream-json --verbose` 的 `system/init` 重驗。
2. 字元估算與實測有差距（13 個重複 skill：字元估算平均 ≈550 token，實測 −1,280，haiku 計）；報告以字元估算為準。
3. 塔台與 Worker 共用專案設定：所有專案層建議都同時影響塔台與 Worker；規則 3 的分組只用來「不要建議移除」，不能分角色套用。
4. 工單類型未正規化；門檻用絕對次數降低影響。
5. 使用次數低估：直接讀 skill 檔、Workflow 代理、子代理內、Codex 端不計；CT skill 一律不建議即為此。
6. claude.ai 帳號層無法用本機紀錄驗證：帳號設定的變更只能從下一次 session 的清單看出。
7. 本 repo 模式只找得到編碼名稱以目前 repo 路徑開頭的專案目錄；放在 repo 外的 worktree 用 `--project` 補，或用 `--all-projects`。
8. plugin marketplace 名稱含 `.` 時，JSON 自檢的信箱樣式可能誤判（exit `3`），屆時改寫允許樣式。

---

## 統計輸出格式

報告中每個偵測到的模式附具體工單編號佐證：

```
## ✅ 做得好的地方

  G4 結構化回報：18/23 張工單有完整回報（78%）
      佐證：T0001, T0003, T0005, ...

  G5 漸進式拆分：3 次正確拆分
      佐證：T0007 → T0008+T0009, T0015 → T0016+T0017

## ❌ 需要改善的地方

  B4 工單膨脹：5 張工單耗時 >60 分鐘
      佐證：T0004(82min), T0009(75min), T0012(68min), T0018(91min), T0021(64min)

  B3 模糊回報：5 張工單回報不完整
      佐證：T0006, T0011, T0014, T0019, T0022
```
