---
title: 更版紀錄
description: BMad Control Tower 近 10 版的更版紀錄（最新 v5.13.0），更早的版本見演進史。
---

<!-- 本頁由 scripts/sync-ct-release.mjs 從 CT CHANGELOG 產生，請勿手改；要改內容請改來源後重跑。 -->

# 更版紀錄

目前版本 **v5.13.0**（2026-10-29）。這裡列出最近 10 版的完整紀錄，最新的在最上面；更早的 54 版（v2.1.1 ～ v5.11.0）請看[演進史](./evolution)。

::: tip 摘要不具權威
本頁照錄 CT 的 CHANGELOG，只拿掉工單、決策、驗收回函等內部編號與出處註記。規則的權威定義在 CT 各 skill 與 references，兩者有出入時以 CT 本體為準。
:::

::: v-pre

## 5.13.0 <small>2026-10-29</small> {#v5-13-0}


> **MINOR：BUG／工單狀態衛生、BAT 塔台面板讀取契約、`_tower-state.md` 機器可讀摘要契約 v1，新增 3 個設定。**
> 讓 BAT 指揮塔面板（總覽、決策、臭蟲、待辦池、工單）穩定讀得到 CT 寫的檔，並讓未結清單只留真的還要做的事。
> 新設定依 `version-governance.md` § SemVer 慣例屬 MINOR（原規劃為 PATCH，中間沒有另發 PATCH）。
> BAT 介面不變、最低 BAT 版本不變；對照 BAT `0.7.1-pre.8` 的解析器。升級無需遷移（見安裝指南 § 2.54）。

### Added

- `_tower-state.md` 機器可讀摘要契約 v1（`memory-protocol.md` § 機器可讀摘要（YAML frontmatter），唯一權威）：塔台每次寫入 `_tower-state.md` 都同步更新檔頭 frontmatter（`schema_kind`、`summary_version`、`updated_at`、`session`、`next_ids`、`todo`），BAT 指揮塔總覽讀得到待辦與下一個編號。與 v6 同一份契約，欄位與 BAT 逐欄一致；舊專案沒有摘要不算錯，下次寫入時補上。Startup Protocol 與 `*pause`／`*resume` 都指回這一節
- BAT 塔台面板讀取契約（`memory-protocol.md` 新節，唯一權威）：熱檔大小預算 400 KB（409,600 bytes，以磁碟 UTF-8 位元組計）與 BAT 讀檔上限 524,288 bytes、超過時 BAT 各頁的表現、各檔 BAT 依賴的格式、嚴重度／優先級值域對照、frontmatter 與 BOM 共通規則。對照 BAT `0.7.1-pre.8`
- `_bug-tracker.md`／`_backlog.md` 索引格式（`bug-plan-system.md` § 索引格式，唯一權威）：原本指向的「SKILL.md `*sync` 段落」不存在，補上完整格式
- Startup Protocol 與 `*sync` 量熱檔大小，超過預算或上限各印一行提示（不阻擋）
- 決策日誌收斂程序（`decision-log-system.md` § 收斂）：較舊的詳細紀錄原文搬到 `_archive/decisions/_decision-log-D###-D###.md`，熱檔保留涵蓋全部決策的索引表，🔴 危害規則逐字留在熱檔
- BUG 結案判準（`bug-plan-system.md` § 結案判準）：七種情況對應 `FIXED`／`CLOSED`／`WONTFIX`／`OPEN`；不新增狀態值，改用選填欄位 `closed_reason`（`not_a_defect`、`superseded`、`duplicate`、`obsolete`、`external`、`deferred`）；延後的 BUG 列進 `_backlog.md`〈後續待辦（延後的 BUG）〉、留在熱區、可重開
- 未結 BUG 清理提示：`*sync`／`*insights` 在未結張數或久未更新天數超過門檻時印一行，新設定 `bug_review_open_threshold`（預設 `20`）、`bug_review_stale_days`（預設 `30`）
- 客戶驗收不回歸閘（可選）：新設定 `customer_acceptance_gate`（預設 `off`）；`on` 時會改程式或資料的工單多〈相關通過案例〉段，Worker 動工前逐案判定，會改變通過案例就停下交使用者

### Changed

- 決策日誌索引表頭 `#` 改 `ID`；寫明每列 `|` 開頭與結尾、格子內不得有 `|`、索引涵蓋熱檔每一筆、標題固定 `### D### YYYY-MM-DD — 標題`、熱檔不放其他含 `ID` 欄的表格；`*sync` 格式驗證加 BAT 可讀性與大小
- `_bug-tracker.md` 索引：未結區段時間欄改 `報修時間`、CLOSED／WONTFIX 為 `關閉時間`，加 `相關工單` 欄；嚴重度／優先級格子一律 `🔴 High`／`🟡 Medium`／`🟢 Low`（`critical` 寫 `🔴 High（critical）`），不再只寫 emoji；寫明狀態只由區段標題決定
- `_backlog.md` 索引：`## Dropped` 表頭改 `| ID | 標題 | 原因 | 連結 |`（原刪除線表頭讓整區讀不到）
- `PARTIAL` 收尾時點提前到塔台裁示當下（`work-order-system.md` § PARTIAL 當下收尾）：補〈塔台收尾補記〉並改 `DONE`，接手單完成後回頭確認；歸檔前覆核改為最後防線
- 改了 BUG／PLAN 狀態要同一批重建 `_bug-tracker.md`／`_backlog.md`
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.54，§ 4.1 版號範例同步（`OLD=5.12.8`、`VER=5.13.0`、發行物檔名），§ 13 Config 速查表加 3 個新設定

### Unchanged

- BAT 介面、CT 最低 BAT 版本、派工與通知的指令、旗標、exit code 不變。
- BUG 狀態值不變（`OPEN／FIXING／FIXED／VERIFY／CLOSED／WONTFIX`，與 BAT 一對一）；工單狀態值不變。
- 既有設定的值域與預設不變；三個新設定不設就用預設，行為與 5.12.8 相同（清理提示只多印一行）。
- 歷史段落（本檔舊段落、版號表舊列、安裝指南舊章節）不改；安裝指南 § 2.13 只加一行 📌 註。

## 5.12.8 <small>2026-10-27</small> {#v5-12-8}


> **PATCH：BMAD 路由與工單規則裡 BMad-Method v6.11 前的舊名改成現行名稱，並修正「`bmad-create-story` 內建 Review」的說法。**
> BMad-Method v6.12 起新安裝預設不裝舊名的 shim（要 `--shims` 才裝），照舊名開出的工單可能叫不到 skill。名稱以 BMad-Method v6.12.4（`bmad-guide` v6.12.4）為準。

### Fixed

- 路由與規則直接用舊名的地方換成現行名稱：
  - `control-tower/references/enhancement-integration.md`:52（ECC 觀察範例 `bmad-create-prd` → `bmad-prd`）、:114（`bmad-quick-dev` → `bmad-build`）、:115、:133、:148（`bmad-dev-auto` → `bmad-build-auto`）、:129（補 context 改用 `bmad-project-context`（setup intent），取代 `bmad-document-project`／`bmad-generate-project-context`）、:152（`bmad-dev-auto-result-*.md` → `bmad-build-auto-result-*.md`）、:133、:154（`final_revision` → commit 範圍 `baseline_revision..HEAD`；多個 story 用 `baseline_revision..下一個 story 的 baseline_revision`）
  - `control-tower/references/work-order-system.md`:132（`dev-story` 工單 → 開發（`bmad-build`）工單）、:147（派發摘要範例 `bmad-generate-project-context` → `bmad-project-context`（setup intent））、:172（`bmad-dev-auto` → `bmad-build-auto`、`final_revision` → commit 範圍）
  - `control-tower/references/work-order-template.md`:62、:63、:65（`bmad-dev-auto` → `bmad-build-auto`、結果檔名、`final_revision` → commit 範圍）
  - `control-tower/references/debug-strategies.md`:12（`dev-story` → 開發（`bmad-build`））
- `work-order-system.md`:120 的審查說法：原本寫「使用 `bmad-create-story` 時 Story 內建 Review、不需額外工單」，已不成立。改成：`bmad-create-story` 是保留的 shim；Story 拆分走 `bmad-spec` Story Breakdown，審查在 `bmad-build` 的 Review Triage，不能因為用了 story 就省略審查；用 `bmad-build` 時看 spec 的 `## Review Triage Log` 有沒有跑，沒跑就照同一表的其他條件另派審查工單。
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.53，§ 4.1 版號範例同步（`OLD=5.12.7`、`VER=5.12.8`、發行物檔名）。

### Unchanged

- 已經寫明「舊名 → 新名」的退役對照保留：`enhancement-integration.md`:129～:131、`work-order-system.md`:171、:174、:175。
- `control-tower/SKILL.md` 的「退役名要經外部 `bmad-guide` 確認才路由」原則不變；其他規則、旗標、exit code、步驟不變。
- BAT 介面不變、CT 最低 BAT 版本不變；設定的值域與預設、工單 metadata 不變。
- 歷史段落（本檔舊段落、版號表舊列、安裝指南舊章節）不改。

## 5.12.7 <small>2026-10-27</small> {#v5-12-7}


> **PATCH：BAT／CT 環境偵測改成只列變數名稱、不輸出值。**
> 舊的偵測寫法（`Get-ChildItem Env:BAT*`、`Get-ChildItem Env:CT_*` 不接 `Select-Object -ExpandProperty Name`）會把變數值（含 BAT 範圍權杖 `BAT_REMOTE_TOKEN`）印進 session transcript；Worker 依這個思路自組 `env | grep …` 時也一樣。

### Fixed

- 偵測指令改成只列名稱——PowerShell `Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object`（`CT_*` 同理），bash `env | cut -d= -f1 | grep -E '^BAT_' | sort`：
  - `control-tower/references/auto-session.md`:93（決策樹 Step 0 註記）、:171（虛擬碼註解）、:244（`env | grep -iE …` → `env | cut -d= -f1 | grep -iE …`）、:754（§ 偵測條件 PowerShell 範例）
  - `control-tower/references/yolo-mode.md`:43、`control-tower/SKILL.md`:89、`ct-exec/SKILL.md`:39、:56（`Env:CT_*`）、安裝指南 :1774（§ 4.2 Codex 端 `AGENTS.md` 塔台派工段落範例；v5.12.6 為 :1757）
  - 同類敘述（沒有指令、但會讓 Worker 自組列值指令）補一句只列名稱並引用權威：`ct-done/SKILL.md`:121、`ct-help/SKILL.md`:106
- 新增唯一權威規則 `auto-session.md` § BAT 內部終端路由 › 偵測條件（:756～:764）：偵測 `BAT_*`／`CT_*` 只判斷有無、任何 helper 或手動檢查只列名稱；`BAT_REMOTE_TOKEN` 任何時候只記「已設定」（呼應 § 範圍權杖與分頁角色 第 2 點）；例外是規則明定的單一非祕密變數只讀那一個（`CT_MODE`、`CT_INTERACTIVE`、`ct-exec` 落點檢查記錄的 `BAT_WORKSPACE_ID`、worktree 的 `CT_HOME`／`CT_WORKTREE_*` 證據）。其他檔只放一句並引用。
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.52，§ 4.1 版號範例同步（`OLD=5.12.6`、`VER=5.12.7`、發行物檔名）。

### Unchanged

- 判讀邏輯：`shell env visibility mismatch`、塔台派工五個必要變數、Worker notify 三個必要變數、helper exit code、落點檢查（含記錄 `BAT_WORKSPACE_ID`）與 worktree SHA 證據都不變。
- BAT 介面不變、CT 最低 BAT 版本不變；設定的值域與預設、工單 metadata 不變。
- 歷史段落（本檔舊段落、版號表舊列、安裝指南舊章節）不改。

## 5.12.6 <small>2026-10-25</small> {#v5-12-6}


> **PATCH：發行內容去識別（只改說明文字，規則與行為不變）。**
> 範例與由來說明裡可識別的名稱換成中性說法或範例值，以便公開發行；指令、旗標、exit code、步驟順序、檔名、設定的值域與預設、工單 metadata、BAT 介面都不變。

### Changed

- 去識別改寫（只列檔案與類別，不列原文；「由來」類句子保留事件與日期，只換名稱）：
  - 私人專案 repo 名與專案代稱 → 「專案 A／B／C」、`project-a`／`project-b`／`project-c`：`ct-exec/SKILL.md` § Landing Zone Check、`ct-fieldguide/references/global-fieldguide.md`（範例表）、
    `ct-insights/references/analysis-rules.md`，`control-tower/references/` 的 `archive-system.md`、`auto-session.md`、`cross-project-coordination.md`、`multi-tower-protocol.md`、`playbook-engine.md`、`work-order-template.md`；本檔歷史段落
  - 本機絕對路徑 → `~/repos/…`、`~/Projects/…` 占位：`global-fieldguide.md`（範例表）、`work-order-template.md` § `repo`；`docs/Control Tower 自助擴充指南：教塔台學新技能 v4.md`（`*import --from` 範例路徑）
  - 私有詞（人名、帳號、主機名、組織名）→ 中性說法：`auto-session.md`、`cross-project-coordination.md`、`work-order-template.md`、`yolo-mode.md`；本檔歷史段落
  - 內網主機位址 → RFC 5737 範例位址：`enhancement-integration.md`、`self-learning-core.md`
  - 私人規則名 → 中性說法：`yolo-mode.md`；本檔歷史段落
  - 分頁短 id 範例 → 占位：`memory-protocol.md`
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.51，§ 4.1 版號範例同步（`OLD=5.12.5`、`VER=5.12.6`、發行物檔名）。

### Unchanged

- 規則與行為：指令、旗標、exit code、步驟順序、檔名、設定的值域與預設、工單 metadata 不變；BAT 介面不變、CT 最低 BAT 版本不變。
- 保留的公開值：BAT 預設安裝路徑（`Program Files` 下的 `BetterAgentTerminal`）、`auto-session.md` § A.1 偵測變數完整表 SSH 列的文件範例位址。
- 歷史段落只換可識別的名稱，記載的事件、日期與版本內容不改。

## 5.12.5 <small>2026-10-23</small> {#v5-12-5}


> **PATCH：退役 `control-tower/references/` 其餘三份 Worker 命令長版說明，仍有效的規則補進 SKILL／reference；`ct-status` 的 `INTERRUPTED` 歸 Needs Tower judgment（文件補完，行為不變）。**
> 塔台與 Worker 行為以現行 SKILL 為準、不變；設定的值域與預設、工單 metadata、BAT 介面都不變。

### Removed

- **`control-tower/references/ct-done.md`**（57 行）、**`ct-status.md`**（80 行）、**`ct-evolve.md`**（135 行）：ct-* 斜線指令時期的長版說明。
  原因：三份都不在 `control-tower/SKILL.md` 的 Reference Routing，`control-tower` 與 `ct-*` 的關係由 `control-tower/SKILL.md` 建立；內容又有幾處和現行 SKILL 衝突——
  `ct-done.md` 先改狀態再填回報區（現行為反序收尾）、收尾後一律回報「完成」（現行依狀態分 `完成`／`部分完成`／`需要協助`）；`ct-status.md` 只讀前 15 行（現行以 frontmatter 為準）；
  `ct-evolve.md` 偵測到就寫入、結案時「強制生成 playbook（不需確認）」、Playbook 門檻「3+ 工單、100% 成功率」與指錯檔的格式連結（現行為蒸餾＋分流、🟢＋完整序列＋使用者確認）。
  `ct-evolve.md` 又被 `self-learning-core.md` 連成「完整規範」，照連結讀過去的塔台或 Worker 會拿到錯的規則。仍有效的內容先搬走（見 Changed）再刪。
  升級後已安裝的這三個檔案不再存在（安裝指南 § 4.1 為整個 skill 目錄替換，舊檔隨舊目錄移走；見 § 2.50）。

### Changed

- `ct-done/SKILL.md`：§ Error Handling 加「工單還是 `PENDING`：說明尚未開工、建議 `ct-exec`、不改工單並停止」；§ Report Repair 加「工單本身要求同步 `sprint-status.yaml` 而漏做時，補救時一併補上」
  （塔台收單時仍會複查，`work-order-system.md` § sprint-status.yaml 同步）。來源 `ct-done.md` 錯誤處理與 Step 6。
- `ct-status/SKILL.md` § Output：sync 有落差時，最後一句交給塔台（`*sync` 或說「重新同步」），`ct-status` 本身維持唯讀。來源 `ct-status.md` § sync 差異報告。
- `ct-evolve/SKILL.md`：§ Extraction Flow 第 2 步估時偏差寫明「actual vs estimate off by more than 50%」；第 6 步後加「完整且 🟢 以上的 recurring sequence 只建議 `--playbook`，萃取模式不自己寫 playbook」；
  § Reference Routing 加 `enhancement-integration.md` § /ct-evolve Level 1 增強（有 ECC 時；原本只能經 `self-learning-core.md` 間接到達）。
- `self-learning-core.md` § 學習觸發時機 › `### 3. /ct-evolve`：「完整規範」連結改到 `ct-evolve/SKILL.md`；塔台主動提議的時機搬進來——「Sprint 結束」「Epic 完成」「回顧」、
  累積 ≥10 筆觀察紀錄且尚未萃取，以及提議格式；結案（「結案」「專案完成」）改成提議對 🟢 以上候選跑 `--playbook`、照 `playbook-engine.md` 確認與分流提問後寫入，
  外加 ⭐ 候選提議全局化與專案學習總結。「強制生成 playbook（不需確認）」**不搬**（已廢棄的 v4.0 做法）。
- `playbook-engine.md` § 與 `/ct-evolve` 的整合：首句與表頭的「`/ct-evolve` Step 4」改成「`/ct-evolve`（學習萃取模式）」，「候選來源」改成 `ct-evolve/SKILL.md` § Extraction Flow 找到的 recurring sequences、再由使用者決定是否 `--playbook`。

### Fixed

- **`ct-status` 的 `INTERRUPTED` 沒有 bucket**：它是合法狀態（`work-order-system.md` § 中斷復原、`work-order-template.md`），但 § Status Buckets 三組都沒列。
  現在歸 **Needs Tower judgment**，並寫明依據：session 中斷後塔台已另開接續工單或重派的原工單，塔台確認接續工單接手後可結掉。
- 安裝指南新增 § 2.50；§ 4.1 版號範例同步（`OLD=5.12.4`、`VER=5.12.5`、發行物檔名）。

### Unchanged

- 歷史段落（本檔舊版段，含 [5.12.4]「其他三份……保留」、[5.11.0] `ct-evolve.md` 補 `--workflow`、mem0 REST 改寫、[4.0] `ct-evolve.md` 獨立 reference 等條目；
  `version-governance.md` 版號表舊列；安裝指南 § 2.4x 等舊章節）不改。
- 塔台 `*evolve`、`*sync`、補救收尾的流程不讀這三份說明，行為不變；`ct-status` 長版的狀態符號表是顯示慣例，不搬。

## 5.12.4 <small>2026-10-23</small> {#v5-12-4}


> **PATCH：退役 `control-tower/references/ct-exec.md`、YOLO 連續 FAILED 計數器位置統一、發行打包調整（文件與發行物，行為不變）。**
> 塔台與 Worker 行為、計數規則、設定的值域與預設、工單 metadata、BAT 介面都不變。

### Removed

- **`control-tower/references/ct-exec.md`**（100 行的 Worker 命令長版說明）。原因：內容與 `ct-exec/SKILL.md` 不一致（例：落點檢查寫成 C-3 承重、
  收尾寫成 Step 8 一次性修改；現行為 C-0 承重、§ Phase 4 反序收尾），而且沒有任何 SKILL 或 reference 連到它。Worker 執行規則的權威改為只有 `ct-exec/SKILL.md`。
  `doctrine.md` § 延伸閱讀的泛稱「各 skill（`ct-exec.md` / `ct-done.md` / `ct-evolve.md` / 等）」改成實際檔名（`ct-exec/SKILL.md` / `ct-done/SKILL.md` / `ct-evolve/SKILL.md` / 等）。
  升級後已安裝的 `control-tower/references/ct-exec.md` 不再存在（安裝指南 § 4.1 為整個 skill 目錄替換，舊檔隨舊目錄移走；見 § 2.49）。

### Fixed

- **YOLO 連續 FAILED 計數器的位置**：`yolo-mode.md` 原本兩種說法——§ 斷點 B-2、§ YOLO 計數器小節與驗收範例 T7 寫 `_tower-state.md` 的 `## YOLO 計數器` 段，
  § `_tower-state.md` 新增 `## YOLO 歷程` 區段 寫 `## YOLO 歷程` › `### 計數器`。統一為 **`## YOLO 歷程` › `### 計數器`**（塔台實際寫入的位置）；
  `##### YOLO 計數器` 小節保留（可引用），內文與格式範例改成新位置。計數規則（B-2 判準）、重設時機、斷點 B 語意不變；其他 reference 沒有寫計數器位置。
- 安裝指南新增 § 2.49；§ 4.1 發行物版面補單一 skill zip 目錄與教學 skill zip 新版面。

### Changed（打包）

- 發行物另出 **`BMad-Control-Tower-v5.12.4-skills/`**：8 個單一 skill zip `<skill>-v5.12.4.zip`，每個 zip 根層是唯一資料夾 `<skill>/`（claude.ai 一個 zip 只收一個 skill）。
  全量 `BMad-Control-Tower-v5.12.4.zip` 版面不變（根層 8 個 skill 目錄、不含 `docs/`）。
- 教學 skill `control-tower-guide-v5.12.4.zip` 改成根層唯一資料夾 `control-tower-guide/`（官方規則：zip 頂層是 skill 資料夾、資料夾名稱等於 `name`；v5.12.3 以前根層是 `SKILL.md`）。
- repo 工具 `tools/Publish-ClaudeAiSkills.ps1`（不在發行物內）：上傳步驟改「claude.ai → Customize → Skills」（實際位置以當下 UI 為準）；`$Catalog` 新增 `ZipRoot = 'Name'`
  （資料夾名取 `SKILL.md` frontmatter `name`），Guide 列改用它；`$SettingsUrl` 與其他邏輯不改。

### Unchanged

- 歷史段落（本檔舊版段，含 [5.12.3] 提到 `ct-exec.md` Step 8 與「YOLO 計數器」補小節的兩條；`version-governance.md` 版號表舊列；安裝指南 § 2.48 等舊章節）不改。
- `control-tower/references/` 其他三份 Worker 命令長版說明（`ct-done.md`、`ct-status.md`、`ct-evolve.md`）不在本版範圍，保留。

## 5.12.3 <small>2026-10-23</small> {#v5-12-3}


> **PATCH：`--close-worker` 最低 BAT 版本更正為 `>= 0.6.1-pre.4`，並收斂累積的文件說法不一（文件修正，行為不變）。**
> 塔台與 Worker 行為、設定的值域與預設、工單 metadata、BAT 介面都不變。

### Fixed

- **`--close-worker` 的最低 BAT 版本**：[5.1.0] 寫的「實機回收需 BAT `0.6.1-pre.3`」不準，更正為 **`>= 0.6.1-pre.4`**（收單後回收與 v5.12.0+ 重派前回收都適用）。
  pre.3 已有這個指令，但分頁 5 秒內有輸出就回 exit `6` BUSY、延遲期間有輸出也會取消排程；等輸出安靜再關自 pre.4 起。
  pre.5 之前，延遲期間的終端自動回應（focus report）會被當成使用者輸入而取消回收（分頁保留、塔台只看到 exit `0`），不影響最低版本。
  出處：BAT 塔台的回覆；BAT `README.md` 相容表「收單後自動回收 Worker 分頁」「重派同一張工單前回收舊 Worker 分頁」兩列。
  本檔 [5.1.0]、[5.12.0] 段與安裝指南 § 2.21 不改；安裝指南 § 13 `worker_auto_close` 列改寫成 `>= 0.6.1-pre.4`。
- 安裝指南 § 4.5、§ 12：`ct-insights` 的作用域改照 `ct-insights/SKILL.md` § Scope（專案、`global`；塔台內用 `*insights`），拿掉不存在的 `/ct-insights session`。
- `doctrine.md` § 為什麼要顯式狀態欄位？：`*status`（不是塔台命令）改成 `*sync`，查狀態用 `/ct-status`。
- `doctrine.md` § 為什麼要反序寫入？：順序改照 `ct-exec/SKILL.md` § Phase 4（產品 commit → 回報區 → 最終狀態 → 工單 commit → 通知），保留 v4.4.0 → v5.7.0 的演進說明；
  「CT 實例錨點」改指 § Phase 4（原本指向的 `ct-exec.md` Step 8 已沒有反序與 commit 的規定）。
- `tower-config.md` § 可用選項：表下註明 `gp-prefix` 寫在 `_tower-config.yaml`、但不是 `*config` 選項，引用 `multi-tower-protocol.md` § `gp-prefix` 設定（唯一權威；v5.0.8 起不列入 `*config` 表）。
- `yolo-mode.md` § 斷點 B-2：原本只出現在範例區塊裡的「YOLO 計數器」補成 `##### YOLO 計數器` 小節，B-2 判準引用它；計數規則與格式不變。
- 實戰補充（一-B）與 `beginner-tutorial.md`：中斷改用 `*pause`／`*resume`（v3.2.0 起的內建命令；「⚡ 插件：」是更早的自由文字說法），
  狀態圖改用 status enum（`PENDING`、`IN_PROGRESS`，沒有 `REVIEW`），註明以 reference 為準。
- 安裝指南 § 4.1 發行物版面：註明本指南、`CHANGELOG.md`、`Control Tower 實戰補充/` 只在發行目錄版，zip 不含 `docs/`（打包版面不變）。
- 安裝指南新增 § 2.48。

### Changed

- **置信度條件分專案層／全域層**（釐清兩處衝突的說法，使用者決定）：原本 `self-learning-core.md` § 置信度系統 的 🟢 是「2+ 專案驗證」，
  `playbook-engine.md` § 晉升標準 的 L0→L1 是「2+ 工單重複出現」，§ 與現有置信度系統對應 又把 L1 對到「🟢，2+ 專案驗證」。
  現在權威只在 `self-learning-core.md` § 置信度系統：**專案層**（本專案 Layer 3 `_learnings.md`）的 🟢／管線 L1 `validated` = 同一模式在 2+ 工單重複出現；
  **全域層**（晉升 Layer 2 的 learnings 與全域規則）的 🟢 = 2+ 專案驗證；🔵／🟡／⭐ 兩層相同；升級說明改成分層寫。`playbook-engine.md` 兩處與安裝指南 § 8 改成摘要＋引用。
  語意：專案層 learning 的 🟢 條件在文字上由「2+ 專案驗證」改為「2+ 工單重複出現」（與 `*evolve` 的 L0→L1 標記一致）；全域層 🟢 不變。

### Unchanged

- `work-order-system.md`、`auto-session.md` 不改：兩處 `--close-worker` 的說明與 § 依賴的 BAT 基礎設施 都沒有列 BAT 版本，不新增。
- 歷史段落（本檔舊版段、`version-governance.md` 版號表舊列、安裝指南 § 2.21 等舊章節）不改。發行物版面不變。

## 5.12.2 <small>2026-10-22</small> {#v5-12-2}


> **PATCH：收單回收 exit `0` 的提示改成「約 N 秒後」（文件修正，行為不變）。** `work-order-system.md` § 收單後回收 Worker 分頁 exit `0` 列原本建議在確認區塊加一行
> 「Worker 分頁將於 N 秒後回收」；照 BAT 現行的回收行為，實際關閉可能比 N 秒晚（延遲到期時仍在輸出就等安靜），也可能被放棄，且塔台不會得知。
> exit `0` 的處理仍是「靜默」；其他 exit code 列、收單回收與重派前回收的條件／指令、`worker_close_delay` 的值域與預設不變；BAT 介面不變。

### Fixed

- `work-order-system.md` § 收單後回收 Worker 分頁 exit `0` 列：提示改成「Worker 分頁約 N 秒後回收」，並補一句——延遲到期時分頁仍在輸出，BAT 會等連續安靜 5 s、
  最多再等 60 s，屆時仍在輸出就放棄、保留分頁；helper 已 exit `0`，塔台不會得知，所以提示不得寫成確定的時間或「已關閉」。條件細節引用
  `tower-config.md` § 可用選項 `worker_close_delay`，不重複定義（權威見 BAT 文件）。
- 安裝指南新增 § 2.47。

### Unchanged

- `tower-config.md`、`auto-session.md`、`yolo-mode.md` 與 `work-order-system.md` 的其他列與段落不改；歷史段落（本檔舊版段、`version-governance.md` 版號表舊列、
  安裝指南 § 2.21／§ 2.46）不改。其他檔案沒有把回收寫成確定時間或確定完成的說明。

## 5.12.1 <small>2026-10-22</small> {#v5-12-1}


> **PATCH：`worker_close_delay` 的取消條件對齊 BAT 現行行為（文件修正，行為不變）。** 舊說明寫「延遲期間 Worker 分頁有新輸出或使用者輸入，BAT 會取消回收」，
> 與 BAT 現況不符：延遲期間的輸出**不**取消；只有排程後使用者在 Worker 分頁的輸入會取消（終端自動回應不算）；延遲到期後 BAT 等分頁連續安靜 5 s 才關、最多再等 60 s。
> `worker_close_delay` 值域與預設、`--delay-ms` 換算、收單回收與重派前回收的條件／指令／exit code 不變；BAT 介面不變。

### Fixed

- `tower-config.md` § 可用選項 `worker_close_delay` 列（CT 內唯一權威）：取消條件改照 BAT 權威（BAT 文件）——延遲期間輸出不取消、只有排程後的使用者輸入取消、終端自動回應不算輸入、到期後等連續安靜 5 s、
  最多再等 60 s，仍在輸出就放棄、分頁保留（helper 已 exit `0`，塔台不會得知）。
- 安裝指南 § 13 Config 速查表 `worker_close_delay` 列同步；新增 § 2.46。

### Unchanged

- 歷史段落（本檔 [5.1.0]、`version-governance.md` 版號表舊列、安裝指南 § 2.21）不改；`work-order-system.md` § 重派前回收舊 Worker 分頁 與安裝指南 § 2.45
  的「等安靜 5 s、最多 60 s、使用者輸入取消」原本就與 BAT 一致，不改。

## 5.12.0 <small>2026-10-22</small> {#v5-12-0}


> **MINOR：重派前回收舊 Worker 分頁。** 塔台對同一張工單再派 Worker 之前，先以 `--close-worker … --delay-ms 0`
> 回收舊 Worker 分頁，避免新 Worker `DONE` 後收單回收回 exit `5`（`AMBIGUOUS`）、兩個分頁都要手動關，以及 BAT 把兩個分頁都標 `✓`。
> 不論 exit code 都照常派工。`--skill ct-done` 補救派工不回收、`worker_auto_close: off` 仍回收（使用者決定）。
> BAT 介面不變，最低 BAT 版本不變（`--close-worker` 自 v5.1.0）；無新設定、無新工單欄位。派工命令、`--set-role`、斷點、提問通道（除「收到備援」加一句引用）、
> 隔離派工、合併流程、`worker_question_timeout`、收單回收的條件與指令不變。

### Added

- `work-order-system.md` § 回報處理流程 › 重派前回收舊 Worker 分頁（唯一權威）：適用條件（BAT 內派工、同一張工單再派 `ct-exec`、曾在 BAT 派過；不確定時照樣呼叫）；
  涵蓋 yolo 提問備援、`BLOCKED`／`FAILED` 後 Renew 重派、使用者停掉首派後重派、派工 exit `8` 後使用者決定重派；
  不適用 `--skill ct-done` 補救派工（保留現場）、研究單使用者在原分頁重讀工單、`Unknown option '--wait-started'` 去參數重派、首派；
  與 `worker_auto_close` 無關；指令 `--close-worker T#### --notify-id "$BAT_TERMINAL_ID" --delay-ms 0`（隔離工單加 `--worktree keep`）；
  exit `0`／`3` 繼續派工、`5` 一行提示手動關舊分頁、`4`／`1`／其他一行提示，全部照常派工；`1` 與收單回收共用同一個「不支援 `--close-worker`」session 旗標；
  為什麼安全（BAT 在呼叫當下鎖定唯一候選分頁、`--delay-ms 0` 仍等安靜 5 s、使用者輸入會取消）與為什麼要做。

### Changed

- `work-order-system.md` § 回報處理流程：`FAILED`、`BLOCKED` 列補「Renew 重派前先照新小節」；收單回收 exit `1` 列註明與新小節共用 session 旗標；§ 中斷復原「重派原工單」補引用。
- `yolo-mode.md` § Worker 向塔台提問 › 塔台端「收到備援的 `T#### 需要協助`」：派新 Worker 前一句引用（仍不對舊分頁送按鍵）；§ 迴歸測試場景 T9 預期補一句。
- `research-workorder.md` § Renew 機制 › 塔台操作流程：使用者在原分頁重讀工單時不回收；塔台改派新 Worker 時引用新小節。
- `auto-session.md`：命令表「回收 Worker 分頁」列補重派前用途；§ 範圍權杖與分頁角色 第 5 點的 exit code 表引用改為兩張表；
  § worktree 隔離派工「同工單重派沿用 worktree」補 `--worktree keep` 引用；§ Worker 啟動確認 第 4 點「要不要重派由使用者決定」後補引用。
  § 安全規則 `--close-worker` 列不改（`--delay-ms` 已允許 `0`–`300000`）。
- `tower-config.md` § 可用選項 `worker_auto_close` 列補「不影響重派前回收」。
- `merge-workorder.md` § 合併判準「Renew 合併工單重做」補引用。
- `control-tower/SKILL.md` § Status Handling 收單回收摘要之後補重派前回收摘要＋引用。

### Compatibility

- BAT 介面不變，CT 最低 BAT 版本不變；舊 BAT（不支援 `--close-worker`，exit `1`）只多一行提示，照常派工，之後同 session 不再嘗試。
- 塔台與 Worker 請同版安裝（Worker 端行為無變化）。

:::

## 延伸閱讀 {#further-reading}

- CT `CHANGELOG.md`（共 64 個版本；本頁列最近 10 版）
- CT `version-governance.md` § 歷史版號表
- [演進史](./evolution)：更早的 54 版與八個世代

Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
