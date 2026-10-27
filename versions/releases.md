---
title: 更版紀錄
description: BMad Control Tower 近 10 版的更版紀錄（最新 v5.12.7），更早的版本見演進史。
---

<!-- 本頁由 scripts/sync-ct-release.mjs 從 CT CHANGELOG 產生，請勿手改；要改內容請改來源後重跑。 -->

# 更版紀錄

目前版本 **v5.12.7**（2026-10-27）。這裡列出最近 10 版的完整紀錄，最新的在最上面；更早的 52 版（v2.1.1 ～ v5.9.0）請看[演進史](./evolution)。

::: tip 摘要不具權威
本頁照錄 CT 的 CHANGELOG，只拿掉工單、決策、驗收回函等內部編號與出處註記。規則的權威定義在 CT 各 skill 與 references，兩者有出入時以 CT 本體為準。
:::

::: v-pre

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

## 5.11.0 <small>2026-10-20</small> {#v5-11-0}


> **MINOR：Workflow 精簡版——閘門 G2（至少一個具名 workflow 回測達標、升到 🟡）未通過後只做不花 workflow token 的部分。** 新設定 `workflow_integration`
> （`off`／`ask`／`on`，預設 `on`）；Worker 只有在工單明文授權時才呼叫 Workflow 工具、自發子代理要在回報區記錄（`ct-exec`）；
> 預篩腳本隨 `ct-insights` 發行、修三處偵測缺漏，只做排除守門與按需提示（`*insights workflow`）；另修補幾項先前驗收記下的小問題。
> **不做**：具名 workflow 的派發與執行、`execution`／`workflow_run_id`／`workflow_stats` 等工單欄位（待卡片達 🟡 後再定）。
> BAT 無最低版本需求。派工命令、`--set-role`、斷點、提問通道、隔離派工、合併流程、`worker_auto_close` 與 `ct-exec` 其他執行流程不變。

### Added

- `tower-config.md` § 可用選項：`workflow_integration`（`off` / `ask` / `on`，預設 `on`；有效值與預設的唯一權威），持久化範例補一行。
- `workflow-engine.md` § `workflow_integration` 的行為：三個值對塔台寫 Workflow 授權與工具型 workflow 的影響；`off` 時規則分析、預篩腳本、
  `--workflow` brief 照常；Worker 不讀設定，塔台在工單裡決定；只管 Workflow 工具，不管 Worker 的一般子代理。
- `ct-exec/SKILL.md` § Workflow And Sub-Agents（唯一權威）：工單有「Workflow 使用授權」段落才可以呼叫 Workflow，只做列出的執行，
  重跑、加資料、超過 agent 上限先問塔台；token 超過事後上限 → 記錄、不重跑、下一次授權執行前先問塔台；每次執行記 `runId`／agent／tokens／耗時／`dropped`；
  沒有 Workflow 工具（Codex）不模擬。自發的唯讀子代理不需授權，但回報區 `### 子代理與 Workflow 使用` 要記數量、用途、唯讀與保證方式、約略 tokens（或估算方式）。
  § Phase 4 第 3 步與 Reference Routing 補引用。
- `work-order-template.md` § 撰寫 Workflow 使用授權：塔台的授權段落範本，`workflow_integration: off` 時不得寫、只派 Claude Code Worker。
- `ct-insights/scripts/ct-workflow-prefilter.py`（新檔，Python 3 標準函式庫）：既有的預篩腳本隨 skill 發行並修正三處偵測缺漏——X2 加來源
  ④ `intervention_type: decision-requiring`（frontmatter 頂層或 `interaction:` 底下、內文元資料鏡像行）與 ⑤「DP 裁定紀錄」；S1 的 cue 也看 `title`；
  X4(a) 補「逐一＋複製／雜湊／計數」；新增 `--ids` 逐張輸出守門結論與證據位置、摘要加排除守門統計。
- `ct-insights/references/analysis-rules.md` § 預篩腳本：排除守門與按需提示（唯一權威）：只用 X2、X3、X5 守門（X5 提示 Playbook）、X1／X4 只標需人工；
  按需提示只在塔台主動呼叫時列候選與證據位置、不自動標記或修改工單；塔台入口 `*insights workflow [T#### …]`；沒有 Python 3 時改人工判定。
- `workflow-engine.md` § 現況：G2 未通過（refuter 會確認錯誤發現、reader 實測 100–180k／組、成立的扇出多為 Worker 自發）與 § 尚未定案
  （具名 workflow 的派發與執行、frontmatter 欄位與 BAT 契約、預篩升級為自動建議）。
- `data-layer-architecture.md` § Layer 3 附屬：專案 workflow 腳本 補語法檢查做法（`export const meta` 改 `const`、包進 async function 再 `node --check`）。
- `ct-help/SKILL.md` § Claude Code Workflow：整合開關、授權、`*insights workflow`、G2 現況的摘要。

### Changed

- `workflow-engine.md`：前言改為 v5.11.0 精簡版說明並列出兩個例外權威；派工型的狀態、🟡 等級的「可做什麼」、§ 同意治理（落到工單授權，依 `workflow_integration` 決定問不問）、
  § Codex（有授權的工單只派 Claude Code Worker）改寫；R4 加註 Explore 型仍有 Bash／PowerShell，唯讀靠 prompt 明文禁止；成本基準補 reader 實測區間；
  § 本版不做 改為 § 尚未定案。
- `playbook-engine.md`：§ `*evolve` 擴展子命令 新增 `*evolve --workflow [name]` 轉交 `/ct-evolve --workflow`；§ 塔台自動建議 改為「待卡片達 🟡 後再定」並指向 `*insights workflow`。
- `ct-evolve.md` 長版說明新增 § `--workflow [name]`（權威仍在 `ct-evolve/SKILL.md`）。
- `control-tower/SKILL.md` § Built-In Commands 新增 `*evolve --workflow`、`*insights workflow` 兩列（摘要＋引用）；Reference Routing 的 `workflow-engine.md` 說明更新。
- `ct-insights/SKILL.md`：Scope 表、Analysis Flow 第 5 步、Reference Routing 補預篩腳本。`ct-evolve/SKILL.md` brief 的 R3 說明改為「through v5.11.0」。

### Compatibility

- 新設定預設 `on`；沒有新的工單 frontmatter 欄位。既有工單沒有授權段落，Worker 不會呼叫 Workflow——v5.10.0 也沒有這條路徑，行為相同。
- `*insights workflow` 需要 Python 3（標準函式庫即可）；沒有時改依規則人工判定。`ct-insights` 多一個 `scripts/` 目錄，安裝流程照舊整個目錄複製。
- BAT 面板顯示 `execution` 等欄位的功能延後到知識卡達 🟡。
- 塔台與 Worker 請同版安裝。

## 5.10.0 <small>2026-10-20</small> {#v5-10-0}


> **MINOR：Workflow 規則層——CT 開始定義 Claude Code Workflow 在工單裡的位置。** 新增 reference `workflow-engine.md`（Workflow 的唯一權威）、
> `ct-insights` 的「Workflow 適配度」規則組（S1–S6／X1–X5、WFC 候選格式）、`ct-evolve --workflow`（只產 brief 與 🔵 知識卡）與 `[WF-CANDIDATE]` 標記、
> 資料層「Layer 3 附屬：專案 workflow 腳本」。**只有規則層**：派發匹配、工單 frontmatter 欄位（`execution`、`workflow_run_id` 等）、
> `ct-exec` 的 workflow 執行路徑與 Codex 派工檢查在 v5.11.0。BAT 無最低版本需求。派工命令、`--set-role`、斷點、提問通道、隔離派工、合併流程、
> `worker_auto_close` 與 `ct-exec` 執行流程不變。

### Added

- `control-tower/references/workflow-engine.md`（唯一權威）：定位（Workflow 是 Worker 在單張工單內的執行方式，不是 CT 的編排層）；
  Skill／Playbook／Workflow 三分法與分界三提醒；工具型（分析作業用，例：語料挖掘）與派工型（工單用，例：多來源唯讀核對；派發待 v5.11.0）；
  設計規則 R1 回傳 schema 映射報告區段、R2 有界覆蓋一律 `log()` 略過項、R3 不用內建 `isolation: 'worktree'`、只做唯讀或分析形狀、
  R4 子 agent 只用唯讀 tool、R5 不用 `Date.now()`／`Math.random()`；知識卡格式（`_ct-workorders/_workflows/<name>.md`，全局卡在 Layer 2）；
  成熟度 🔵 brief → 🟡 回測（召回 ≥ 80%、誤報 ≤ 20%；無已知發現的研究型改 1 次實戰＋使用者認可）→ 🟢 → ⭐，
  每次回測或試跑前列規模經使用者同意；指標降級（只限 Workflow：連續 2 次推翻率 > 30%，或單位成本超過卡片上限 50% → 降一級；
  累積 ≥ 5 次執行後再評估是否推廣）；成本與規模（沒有 token 預算參數、只能限制 agent／子任務數並事後記帳；1.9 bytes/token、每個 agent 固定開銷約 31k、
  `resumeFromRunId` 可能沒命中快取；尊重 session 規模準則）；同意治理原則（⭐ 前一律先問使用者，機制在 v5.11.0）；Codex 不支援；知識卡寫入路徑檢查。
- `ct-insights/references/analysis-rules.md` 新增 § Workflow 適配度（唯一權威偵測規則）：判定流程（扇出軌 S1＋S6、驗證軌 S3）、
  S1–S6／X1–X5 表與偵測細節（X2 三個來源、X4 不以時間排除、「名稱含 batch ≠ 適合 workflow」、共用狀態是 S6 反條件）、
  輔助訊號「Worker 自發扇出」（不單獨成立）、分級（🔵／邊界／排除，不用 0–100 分數）、WFC 候選輸出格式與 Playbook／邊界清單。
- `ct-evolve/SKILL.md`：`--workflow [name]` 模式（只產 brief 並寫成 🔵 知識卡；不寫 `.claude/workflows/`、不寫腳本、不執行 Workflow；
  腳本由另一張工單在使用者確認 brief 後撰寫，比照 `--skill`）；§ Workflow Bridge `[WF-CANDIDATE]` 標記（比照 `[FG-CANDIDATE]`，條件引用規則組）；
  寫入邊界與 `--status` 同步。
- `data-layer-architecture.md` § 寫入規則 新增「Layer 3 附屬：專案 workflow 腳本」：`<project>/.claude/workflows/*.js` 不屬於 Layer 1、必須進 git、
  只由 Worker 依工單 `affects_files` 寫入、brief 先經使用者確認、不使用 `~/.claude/workflows/`、不自動同步到其他專案；架構總覽補 `workflows/`、`_workflows/`。

### Changed

- `doctrine.md` 前言：在「CT 不是 workflow 工具」之後補一段定位，指向 `workflow-engine.md`。
- `playbook-engine.md`：管線總覽補 Workflow 分支；§ 塔台自動建議 註明 Workflow 匹配在 v5.11.0；§ 寫入路徑安全檢查 註明知識卡改走 `workflow-engine.md` 的檢查。
- `self-learning-core.md`：§ 置信度系統 一句指向 Workflow 指標降級（本表規則不變）；§ 寫入路徑安全檢查 註明 `_workflows/` 不是不明路徑、專案腳本不是學習寫入。
- `control-tower/SKILL.md` Reference Routing、`ct-insights/SKILL.md` Analysis Flow 與 Reference Routing：補摘要與引用。

### Compatibility

- 沒有新的工單欄位、設定或命令參數；舊工單與 v5.9.0 行為相同。BAT 無最低版本需求（Workflow 是 Claude Code 原生能力）。
- `ct-evolve --workflow` 與 `[WF-CANDIDATE]` 只在 v5.10.0 以上的 `ct-evolve` 可用；塔台的 `*evolve` 子命令不變。
- 塔台與 Worker 請同版安裝。

:::

## 延伸閱讀 {#further-reading}

- CT `CHANGELOG.md`（共 62 個版本；本頁列最近 10 版）
- CT `version-governance.md` § 歷史版號表
- [演進史](./evolution)：更早的 52 版與八個世代

Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
