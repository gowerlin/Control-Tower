---
title: 更版紀錄
description: BMad Control Tower 近 10 版的更版紀錄（最新 v5.14.1），更早的版本見演進史。
---

<!-- 本頁由 scripts/sync-ct-release.mjs 從 CT CHANGELOG 產生，請勿手改；要改內容請改來源後重跑。 -->

# 更版紀錄

目前版本 **v5.14.1**（2026-10-30）。這裡列出最近 10 版的完整紀錄，最新的在最上面；更早的 57 版（v2.1.1 ～ v5.12.2）請看[演進史](./evolution)。

::: tip 摘要不具權威
本頁照錄 CT 的 CHANGELOG，只拿掉工單、決策、驗收回函等內部編號與出處註記。規則的權威定義在 CT 各 skill 與 references，兩者有出入時以 CT 本體為準。
:::

::: v-pre

## 5.14.1 <small>2026-10-30</small> {#v5-14-1}


> **PATCH：塔台偵測得到 plugin 安裝的 bmad-guide（Level 2）、安裝說明補同一個 marketplace 的 `bmad-guide`、塔台端派工範本改用完整工單 ID。**
> 5.14.0 只寫「讀取已安裝 skill」，塔台找慣用的 `skills/` 目錄；用 plugin 裝的 bmad-guide 找不到，也不說一聲就改用手動 workflow 欄位。
> 沒有新命令、新設定；BAT 介面、派工命令的參數與順序、斷點 A 正則、exit code 不變。升級只換 skill 檔案（見安裝指南 § 2.57）。

### Fixed

- **塔台偵測得到 plugin 安裝的 bmad-guide（Level 2）**：`enhancement-integration.md` § Level 2 › 偵測 改成明列搜尋順序（唯一權威）——手動安裝 `skills/bmad-guide/SKILL.md`（`~/.claude`、`~/.codex`、`~/.agents`）→ Claude plugin（`${CLAUDE_CODE_PLUGIN_CACHE_DIR:-~/.claude/plugins}/installed_plugins.json` 的 `bmad-guide@*` → `installPath`）→ Codex plugin（`config.toml` 啟用的 `bmad-guide@*` → `plugins/cache/<marketplace>/bmad-guide/<version>/`）；並存時手動優先；`references/` 相對於找到的 `SKILL.md`；plugin 路徑只讀
- **不再靜默降級**：可用 skill 清單有 `bmad-guide`／`bmad-guide:bmad-guide` 但讀不到檔案時，提示使用者一次，再改手動欄位；清單裡也沒有才照舊靜默

### Changed

- `version-governance.md` § plugin 安裝／升級 與安裝指南 § 4.1：同一個 marketplace 另有 `bmad-guide`（`bmad-guide@control-tower`，可選，版號跟 BMad-Method 走、不跟 CT）——名稱表、安裝、升級、遷移（要改用 plugin 先移除手動安裝）、呼叫寫法、版號確認
- 塔台端指令範本 `--workorder`、`--close-worker`、`--worktree-status` 由 `T####` 改成 `<工單 ID>`（含前綴、不截短；與 5.13.1 的 Worker 端相同），`auto-session.md` § 執行方式 加一點說明；`/ct-exec T####` 等呼叫字串樣板的 `T####` 同樣代表完整 ID
- `mono-repo-patterns.md`、`multi-tower-protocol.md`：`project-context.md` → `AGENTS.md` 的專案上下文區塊（BMad v6.11+，以 bmad-guide v6.12.4 為準）
- `enhancement-integration.md` § Playbook → bmad-guide 回饋：bmad-guide 為 plugin 安裝時不改已安裝檔案，改提議修改原始碼、隨下一版發布
- `data-layer-architecture.md` § 寫入規則：補記設了 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 時，`installed_plugins.json`、`known_marketplaces.json` 也一起改到它指的目錄（Layer 1 範圍不變）
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.57，§ 1〈目前版本一覽〉、§ 4.1 版號範例與發行物檔名同步（`OLD=5.14.0`、`VER=5.14.1`）

### Unchanged

- BAT 介面、派工命令的參數與順序、斷點 A 正則、exit code、設定、工單欄位、狀態值不變
- zip 手動安裝流程、發行物版面（全量 zip、8 個單一 skill zip、Guide zip）、plugin 名稱與內容組成不變
- 歷史段落（本檔舊段落、版號表舊列、安裝指南舊章節）不改

## 5.14.0 <small>2026-10-30</small> {#v5-14-0}


> **MINOR：CT 另提供 plugin marketplace 安裝（Claude Code、Codex）；zip 手動安裝照舊。**
> marketplace `control-tower` 放在本站的公開 repo 根目錄（指令見安裝頁）；CT plugin `ct`（8 個 skill）、教學 plugin `ct-guide`；beta 不上架。
> BAT 介面不變、最低 BAT 版本不變。**Codex 搭配 BAT 派工請繼續用 zip 手動安裝**（BAT 對 Codex 送 `$ct-exec`，plugin 版在 Codex 只能用 `$ct:ct-exec` 呼叫）。升級只換 skill 檔案（見安裝指南 § 2.56）。

### Added

- `version-governance.md` § 安裝／升級流程 › plugin 安裝／升級（唯一權威）：安裝（`claude plugin marketplace add`（加本站的公開 repo，指令見安裝頁）→ `claude plugin install ct@control-tower`；`codex plugin marketplace add` → `codex plugin add ct@control-tower`）、升級、從 zip 手動安裝遷移（**先備份並移除**手動安裝，否則 `/ct-exec`、`$ct-exec` 會用手動那份，plugin 版靜默不生效）、版號確認（`plugin list --json`）、回退
- `auto-session.md` § 依安裝方式的 skill 呼叫字串（唯一權威）：Claude 手動／plugin 都用 `/ct-exec T####`（完整寫法 `/ct:ct-exec`）；Codex 手動 `$ct-exec T####`、plugin `$ct:ct-exec T####`；BAT 派工對 Codex 只支援手動安裝；Codex 寫法一律單引號
- 安裝指南 § 4.1〈用 plugin marketplace 安裝／升級〉、§ 2.56

### Changed

- `data-layer-architecture.md` § 寫入規則：Layer 1 路徑加上 plugin 安裝路徑（`~/.claude/plugins/`、`CLAUDE_CODE_PLUGIN_CACHE_DIR`、`$CODEX_HOME/plugins/`、`$CODEX_HOME/.tmp/marketplaces/`）；Q2 補 plugin 機制、Q3 補 plugin 安裝的授權（只能用 plugin 指令）、Q4 註明 plugin 不備份。`control-tower/SKILL.md`、`ct-evolve/SKILL.md` 改為只引用權威，不再列路徑
- `ct-insights` 預篩腳本的路徑改用「已載入的 `ct-insights` skill 所在目錄」，不再寫死 `~/.claude/skills`／`~/.codex/skills`（plugin 安裝時 `*insights workflow` 才找得到腳本）
- `ct-help`、8 個 `agents/openai.yaml` 的 `default_prompt`、安裝指南 § 4.2／§ 4.3／§ 14：呼叫寫法補 plugin 安裝（Codex 用 `$ct:<skill>`）；非 BAT 開分頁／剪貼簿的 `<agent-cli>` 為 `codex` 時改用 Codex 寫法
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.56，§ 1〈目前版本一覽〉、§ 4.1 版號範例與發行物檔名同步（`OLD=5.13.1`、`VER=5.14.0`）

### Fixed

- `auto-session.md` § Worker 側讀取規則寫死 `~/.claude/skills/ct-exec/SKILL.md`（plugin 安裝與 Codex 下都錯），改相對連結；原文指向的兩個小節名稱已不存在，改指 `ct-exec/SKILL.md` § Mode And Environment
- `tower-config.md` `worker_max_retries`、`worker_strikeout_action` 兩列的 `session-guardrails.md` 連結層級錯（`../` → `../../`）；`enhancement-integration.md` 指向 `data-layer-architecture.md` 的連結層級錯

### Unchanged

- zip 手動安裝流程、發行物版面（全量 zip、8 個單一 skill zip、Guide zip）不變；claude.ai 仍上傳單一 skill zip
- BAT 介面、派工命令（`--skill`／`--workorder`）、斷點 A 正則、設定、工單欄位、狀態值不變
- 8 個 skill 一律放在同一個 plugin（`../` 相對連結依賴它們是兄弟目錄）
- 歷史段落（本檔舊段落、版號表舊列、安裝指南舊章節）不改

## 5.13.1 <small>2026-10-30</small> {#v5-13-1}


> **PATCH：通知用工單完整 ID、BAT 塔台面板讀取契約對齊 BAT `0.7.1-pre.9`、BMad 舊說法 4 項。**
> 設了工單前綴的專案，Worker 收尾通知有時漏掉前綴，BAT 用 `--source` 對不上 Worker 分頁，無法標成 Done、也無法一次關掉已完成的 Worker 分頁。
> 沒有新命令、新設定；BAT 介面、派工命令、斷點 A 正則不變。升級只換 skill 檔案（見安裝指南 § 2.55）。

### Fixed

- **通知用工單完整 ID**：ct-exec、ct-done、`auto-session.md`、`yolo-mode.md`、安裝指南的通知範本由 `T####` 改成 `<工單 ID>`——`/ct-exec` 收到什麼 ID 就照原樣用（等於 frontmatter `id`，含前綴，不得截短）。原範本讓 Worker 把帶前綴的 ID 截掉前綴，BAT 用 `--source` 對不上 Worker 分頁、無法標 Done。適用 `--source`、訊息字串、`--ask --source` 與手動備援訊息。唯一權威：`work-order-system.md` § 回報與通知用的工單 ID。
- **Worker 送出前比對**：收尾通知、`--ask`、手動備援訊息送出前與 frontmatter `id` 比對（舊單沒有 `id` 時取檔名），不一致就改用 frontmatter 的值並在回報區記一行。
- **塔台端容錯**：回報 ID 在熱區沒有完全相同的工單、但恰好一張是「前綴 + 同號」時，當作那一張處理並記錄「回報 ID 缺前綴」；多張同號或找不到就問使用者（yolo 屬斷點 A）。這只保住塔台收單，BAT 標 Done 仍靠 Worker 送對 `--source`。權威：`work-order-system.md` § 回報處理流程 › 回報 ID 對不上時。

### Changed

- `memory-protocol.md` § BAT 塔台面板讀取契約：BAT `>= 0.7.1-pre.9` 讀不到決策、臭蟲、待辦池、Epics、Sprint 的檔時顯示「無法讀取 &lt;檔名>」（太大時附 KB 數與 512 KB 上限），讀不到的工單仍列在清單（UNKNOWN）；`critical` 在任何讀取路徑都算 High。更舊的 BAT 照舊靜默變空，所以 **400 KB 預算保留**；512 KiB 上限不變。`bug-plan-system.md` 同步一句。
- BMad 舊說法（以 bmad-guide v6.12.4 為準）：派發摘要範例的產出改為 `AGENTS.md` 的專案上下文區塊；「Quick Flow」改稱 Spec / Build；`bmad-automator` 的替代補 `bmad-build-auto`；「BMad v6.10」標題改 `v6.10+`；bmad-guide 範例版號更新。
- 版號：8 個 `SKILL.md` 版本註解、`control-tower/SKILL.md` H1、`version-governance.md` 範例與版號表；安裝指南新增 § 2.55，§ 4.1 版號範例同步（`OLD=5.13.0`、`VER=5.13.1`、發行物檔名），§ 13 `project-prefix` 列與 § 14 `/ct-exec`、`/ct-done` 列補完整 ID 一句。

### Unchanged

- BAT 介面、CT 最低 BAT 版本、派工命令（`--workorder`、`--close-worker`）、旗標、exit code 不變；斷點 A 正則本來就涵蓋前綴，不改。
- 沒設工單前綴的專案行為不變（完整 ID 就是 `T` 加數字）。
- 設定、工單欄位、狀態值不變；400 KB 預算與 512 KiB 上限的數字不變。
- 歷史段落（本檔舊段落、版號表舊列、安裝指南舊章節）不改。

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

:::

## 延伸閱讀 {#further-reading}

- CT `CHANGELOG.md`（共 67 個版本；本頁列最近 10 版）
- CT `version-governance.md` § 歷史版號表
- [演進史](./evolution)：更早的 57 版與八個世代

Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
