# 版號治理（Version Governance）

Control Tower skill 版號必須同時滿足兩件事：

1. Codex skill validation 可通過。
2. Tower 面板、文件與 Worker 相容性仍能追蹤版本。

## 版號事實來源

Skill YAML frontmatter 僅放 runtime 需要的欄位，至少包含 `name` 與 `description`。不要把 `version:` 放在 frontmatter；Codex skill validation 會把未知欄位視為錯誤。

版本事實來源改用 body 內第一個註解：

```markdown
<!-- control-tower-version: 6.0.0 -->
```

同步點：

| 位置 | 格式 |
|------|------|
| Body 註解 | `<!-- control-tower-version: X.Y.Z -->` |
| H1 或面板 title | `BMad Control Tower vX.Y.Z` |
| `_tower-state.md` metadata | `Control Tower vX.Y.Z` |
| Worker 相容性文件 | 需要時在相關 reference 標明最低版本 |

`*sync` 或版本檢查若需要讀版本，優先讀 body 註解，再讀 title 作為 fallback。不得要求 frontmatter `version:` 存在。

## SemVer 慣例

採 Semantic Versioning：`MAJOR.MINOR.PATCH`。

| 觸發條件 | 版號變動 |
|---------|---------|
| 不相容的工作流程或 metadata schema 變更 | MAJOR |
| 新命令、新設定、新向下相容能力 | MINOR |
| 文件補完、BAT 規則修正、trigger 描述調整 | PATCH |

## 發布流程

1. 更新 body 版本註解與可見 title。
2. 更新受影響 references。
3. 驗證 `SKILL.md` frontmatter 只包含允許欄位且 description 不超過 validation 限制。打包前另檢查每個要發行的 `SKILL.md`（各 skill、外部 adapter skill、教學 skill）frontmatter 的 `description` 不得含 `<` 或 `>`：claude.ai 上傳會拒絕（v6.0.0-beta.12+，BUG-003）。有就先改寫再打包，例如 `methodology_<layer>` 改成 `per-layer methodology_*`；已發行的版本目錄不就地改。
4. 驗證 `agents/openai.yaml` 的 UI metadata 仍符合 skill 功能。
5. Commit / tag / sync installed skill 的時機由使用者或正式 release 流程決定；Tower / Worker 不主動 push。

## 安裝／升級流程

把某個版本安裝到 `~/.claude/skills/` 或 `~/.codex/skills/` 是**寫入 Layer 1**。
可否寫入、範圍與唯一例外，見
[data-layer-architecture.md](data-layer-architecture.md) § 寫入規則（唯一權威定義）。
本節只規範**取得授權之後怎麼做**。

以下指令與路徑以 Claude 端（`~/.claude/skills/`）為例。Codex 端（`~/.codex/skills/`）步驟相同，
授權條件見權威定義 Q3、備份落點見 Q4，依其對應替換路徑。

用 plugin marketplace 安裝（v6.0.0-beta.5+ 條文）是另一條流程，見本節 § plugin 安裝／升級；下面 Step 1～4 是 zip 手動安裝。
**預發行版（beta、rc）不提供 plugin**：v6 的 beta 與 RC 只用 zip 手動安裝；v6 正式版 6.0.0 起上架 plugin（見 § plugin 安裝／升級 開頭）。

### 前置：授權

安裝必須有工單內的明文授權，成立條件見權威定義 § 寫入規則 Q3。Worker 不得自行認定已取得授權。
無授權 → 停止並回報，不要「順手裝一下」。

### Step 1：備份現行安裝品

落點與命名以權威定義 § 寫入規則 Q4 為準。Claude 端例：備份放
`~/.claude/skill-backups/`，**不在 `~/.claude/skills/` 之下**。

```bash
TS=$(date "+%Y%m%d-%H%M%S")          # timestamp 必須取自系統，不得手打
BK=~/.claude/skill-backups/_backup-ct-v<舊版號>-$TS
mkdir -p "$BK"
cp -r ~/.claude/skills/<skill>/ "$BK"/
```

```powershell
$TS = Get-Date -Format "yyyyMMdd-HHmmss"
$BK = "$env:USERPROFILE\.claude\skill-backups\_backup-ct-v<舊版號>-$TS"
New-Item -ItemType Directory -Path $BK -Force
```

- **備份失敗即停**（v5.3.0+）：逐一備份要安裝的每個 skill，任一 skill 備份失敗就停止，不處理後面的 skill、**不得進入 Step 2**。
  全部備份完成後、進 Step 2 之前，逐檔複驗每個備份與現行安裝品相同（例 `diff -r ~/.claude/skills/<skill> "$BK/<skill>"`）；
  任一不同就停止，不得進入 Step 2。此時已安裝目錄完全沒有變動。尚未安裝的 skill（首次安裝）沒有東西要備份，略過即可。
  理由：Step 4 的回退依賴這份備份；備份不完整就替換，失敗時無法復原。

### Step 2：安裝

把新版本目錄下的 skill 安裝到 `~/.claude/skills/`。
只替換授權指名的 skill，不動其他 skill。

- **不得先刪除已安裝的 skill 目錄再複製**（v5.2.6+）。先把新版複製到 `skills/` **之外**的暫存目錄
  （例 `~/.claude/skill-backups/_staging-ct-v<新版號>-<timestamp>/`；落點同權威定義 § 寫入規則 Q1、Q4，
  不得在 `skills/` 之下），對來源逐檔複驗全部 IDENTICAL 後，才逐一替換已安裝目錄。
  替換時先把舊目錄移到暫存目錄，再把已複驗的新目錄移入，不先刪除。
- 任一步驟失敗就**停止**，不繼續處理後面的 skill。複製或暫存複驗階段失敗時，已安裝目錄保持原狀；
  替換階段中途失敗時，以 Step 4 的回退方式從 Step 1 備份復原。
- Windows／Git Bash：傳給原生 Windows 程式（例 Windows Python）的路徑，要用它讀得到的形式
  （`cygpath -w` 轉換或相對路徑）；不要假設 `/d/...`、`/c/...` 這類 POSIX 形式可用。
- 暫存目錄在 Step 3 全部 IDENTICAL 後才刪除。

理由：先刪後複製時，只要複製失敗，已安裝的 skill 就會消失。T0151 實際發生過：Windows Python 讀不到
`/d/...` 形式的來源路徑，兩端 8 個 skill 目錄已被刪除，複製卻全部失敗。

### Step 3：逐檔複驗（要求全部 IDENTICAL）

安裝後必須以 **逐檔 diff 或 SHA256 比對** 確認來源與安裝品一致，
**要求全部 IDENTICAL**。任一檔不一致 → 視為安裝失敗，回退並回報，不得宣稱安裝完成。

```bash
diff -r <版本目錄>/<skill>/ ~/.claude/skills/<skill>/ && echo IDENTICAL
```

```powershell
Get-ChildItem -Recurse -File <版本目錄>\<skill> |
  ForEach-Object { (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
```

### Step 4：回報

回報必須包含：

| 項目 | 內容 |
|------|------|
| 備份路徑 | 完整路徑，且須看得出在權威定義 Q4 指定的備份落點之下（Claude 端為 `~/.claude/skill-backups/`） |
| 複驗結果 | 逐 skill 列出，全部 IDENTICAL 才算 PASS |
| 回退方式 | 具體指令：用 Step 2 同一套流程把 Step 1 的備份目錄裝回（先複製到暫存並複驗，再替換），不先刪除已安裝目錄 |
| 生效時機 | 覆寫當前 session 正在使用的 skill 時，變更於**下一個 session** 生效 |

### 反面案例（D006，2026-09-02）

把備份放進 `~/.claude/skills/` 之下，會被 skill 掃描器註冊成現役 skill。
機制與實證見權威定義 § 寫入規則 Q2。

### plugin 安裝／升級（v6.0.0-beta.5+）

> 🔴 本小節是 **plugin 安裝、升級、從手動安裝遷移**的唯一權威流程；安裝指南與其他文件引用本小節，不複述指令與條件。
> 上面 Step 1～4 是 **zip 手動安裝**的流程，兩種方式並行，zip 手動安裝照舊支援。
>
> ⚠️ **預發行版（beta、rc）不提供 plugin**：marketplace `control-tower` 只上架穩定版（帶 `-` 的版號不上架），`6.0.0-beta.N`、`6.0.0-rc.N` 照舊只用 zip 手動安裝。
> 本小節自 v6 正式版 6.0.0 起適用於 v6，條文與穩定版 5.x 相同；在 beta 或 RC 環境執行下面的指令，裝到的是**穩定版**（6.0.0 起是 v6 正式版），不是預發行版。

plugin 安裝也是**寫入 Layer 1**：路徑清單見權威定義 § 寫入規則開頭，授權條件見 Q3（plugin 安裝），不備份見 Q4。

| 項目 | 值 |
|---|---|
| marketplace | `control-tower`（放在 `gowerlin/Control-Tower` 的根目錄） |
| CT plugin | `ct`：8 個 CT skill 放在同一個 plugin（`../` 相對連結依賴它們是兄弟目錄，不得拆成多個 plugin） |
| Guide plugin | `ct-guide`（`control-tower-guide`，可不裝） |
| BMad Guide plugin | `bmad-guide`（skill `bmad-guide`，可不裝；Level 2 用，塔台怎麼找到它（手動安裝優先、再 Claude／Codex plugin）只定義在 [adapters/bmad.yaml](adapters/bmad.yaml) `detection.probes`，v6.0.0-beta.6+）。bmad-guide 不跟 CT 版號，**beta、RC 使用者也可以從穩定 marketplace 只裝這一個**（CT 本身仍用 zip） |
| 預發行版（beta、rc） | 不上架；`-beta.N`、`-rc.N` 照舊用 zip 手動安裝 |
| 版號 | `plugin.json` 的 `version` = CT 版號（Guide plugin = Guide 版號；BMad Guide plugin = bmad-guide 版號，跟 BMad-Method 走、不跟 CT，例 `6.12.4`） |

#### 前置：授權

同手動安裝：工單內明文授權，指名 agent（Claude Code 或 Codex）、plugin 與 marketplace（例 `ct@control-tower`），
成立條件見權威定義 § 寫入規則 Q3。無授權 → 停止並回報。🔴 只用下面的 plugin 指令；不得直接在 plugin 安裝路徑下複製或修改檔案。

#### 安裝

Claude Code：

```bash
claude plugin marketplace add gowerlin/Control-Tower
claude plugin install ct@control-tower
claude plugin install ct-guide@control-tower      # 可選
claude plugin install bmad-guide@control-tower    # 可選（Level 2）
```

Codex：

```bash
codex plugin marketplace add gowerlin/Control-Tower
codex plugin add ct@control-tower
codex plugin add ct-guide@control-tower           # 可選
codex plugin add bmad-guide@control-tower         # 可選（Level 2）
```

#### 升級

- **Claude Code**：`claude plugin marketplace update control-tower`（session 內 `/plugin marketplace update control-tower`），
  再 `claude plugin update ct@control-tower`（其他 plugin 同理，例 `bmad-guide@control-tower`）；下一個 session 生效。Claude 依 `plugin.json` 的 `version` 判斷有沒有新版
  （`version` 沒變就不會更新）。自動更新在 `/plugin` → Marketplaces 對 `control-tower` 開啟；第三方 marketplace **預設關閉**。
- **Codex**：`codex plugin marketplace upgrade control-tower`。Codex 每次啟動也會自動升級所有 git marketplace（依 commit 判斷）。

#### 從 zip 手動安裝遷移到 plugin

同一個 agent 上，手動安裝和 plugin 安裝**只留一種**。

1. 依上面 Step 1 把手動安裝的 8 個 CT skill 備份到 `skill-backups/`，逐檔複驗（Guide 的 `control-tower-guide`、BMad Guide 的 `bmad-guide` 同理：
   要改用 plugin 的那個就要先移除它的手動安裝）。
2. 複驗全部 IDENTICAL 後，把這些 skill 從 `~/.claude/skills/`（Codex：`~/.codex/skills/`）移走（移到備份落點，不直接刪除）。
   🔴 **不移除時 plugin 版靜默不生效**：同名的一般 skill 存在時，Claude 的 `/ct-exec`、Codex 的 `$ct-exec` 都會用手動安裝那份
   （T0349 實測），而且看不出差別。
3. 依上面〈安裝〉裝 plugin。
4. 開新 session 確認：
   - 版號（見下方〈版號確認〉）
   - Claude：`/ct:ct-exec` 一定叫到 plugin 版；不帶前綴的 `/ct-exec` 載入的 skill 目錄應在 plugin 安裝路徑下，不在 `~/.claude/skills/`
   - Codex：用 `$ct:ct-exec`（plugin 安裝下 `$ct-exec` 叫不到 CT，T0349）
   - `bmad-guide`：Claude `/bmad-guide`（完整寫法 `/bmad-guide:bmad-guide`），Codex `$bmad-guide:bmad-guide`（T0357 實測）
5. claude.ai 同步下來的 `anthropic-skills:*` 副本（例 `anthropic-skills:ct-exec`）不在本機 `skills/` 目錄，不會被上面的步驟移除，會繼續並存。
   版本不同時兩份 description 都參與自動路由，可能選到舊版；手動呼叫時用完整名稱 `/ct:ct-exec` 確認。

#### Codex 搭配 BAT 派工：依 BAT 版本

BAT 對 Codex 派工送哪個呼叫字串由 BAT 決定，CT 的派工命令不變（v6.0.0-beta.6+）：

- BAT `>= 0.7.2-pre.1`：BAT 依 Codex 端實際的安裝方式送 `$ct-exec`（手動安裝）或 `$ct:ct-exec`（plugin），zip 手動安裝與 plugin 都能接受 BAT 派工；
  兩種都裝時用手動安裝那份（所以改用 plugin 時仍要先移除手動安裝，見上方〈從 zip 手動安裝遷移到 plugin〉）
- 更舊的 BAT：一律送 `$ct-exec`，只裝 plugin 時叫不到 CT skill（plugin skill 在 Codex 一定帶前綴 `$ct:ct-exec`，T0349）；
  Codex 要接受 BAT 派工就繼續用 zip 手動安裝，或先把 BAT 升到 `0.7.2-pre.1` 以上
- Codex＋BAT＋plugin 的端到端派工尚未實機驗證（D453）

判斷順序與各情況的呼叫寫法只定義在 [auto-session.md](auto-session.md) § 依安裝方式的 skill 呼叫字串（唯一權威）；
最低 BAT 版本另列在同檔 § 依賴的 BAT 基礎設施。

#### 版號確認

```bash
claude plugin list --json        # ct@control-tower 的 version
codex plugin list --json         # ct@control-tower 的 version
```

`version` 應等於 CT 版號，也和已載入的 `SKILL.md` 版號註解（本檔 § 版號事實來源）一致。
`bmad-guide@control-tower` 的 `version` 應等於 bmad-guide `SKILL.md` 的 `current_version`（去掉 `v`）。

#### 回退

用 plugin 指令移除（`claude plugin uninstall ct@control-tower`、`codex plugin remove ct@control-tower`），
再依上面 Step 2 的流程把遷移前的備份裝回 `skills/`（先複製到暫存並複驗，再放入）。

#### 回報

| 項目 | 內容 |
|------|------|
| 遷移備份 | 從手動安裝遷移時：備份路徑（在權威定義 Q4 的備份落點之下）與複驗結果；手動安裝已從 `skills/` 移走的證據 |
| 安裝結果 | 執行的 plugin 指令與結束碼；`plugin list --json` 的 `version` |
| 呼叫確認 | 新 session 中載入的 skill 目錄（不在 `skills/` 之下） |
| 回退方式 | 上面〈回退〉的具體指令 |
| 生效時機 | 下一個 session |

## 歷史版號表

| 版號 | 發布日 | 關鍵節點 |
|------|--------|---------|
| v4.0.0 | 2026-04-15 | Tower / Worker 分離架構 |
| v4.1.0 | 2026-04-17 | Step 0 Fast Path / Full Scan |
| v4.2.0 | 2026-04-18 | YOLO 自主模式與 BAT notify |
| v4.2.2 | 2026-04-18 | BAT dispatch 加 `--workspace` |
| v4.3.0 | 2026-04-18 | Worker 無狀態化與 `--mode` flag |
| v5.0.0 | 2026-04-28 | YAML frontmatter metadata SoT for work orders |
| v5.0.2 | 2026-06-05 | resolved `PARTIAL` → `DONE` 補正規則；BAT Tower dispatch 與 Worker notify 的 env requirements 拆分（D004） |
| v5.0.3 | 2026-07-04 | External `bmad-guide` v6.10 reference integration; no embedded guide copy；Codex-compatible skill frontmatter（只留 `name`／`description`，版號改 body 註解）and BAT env visibility hardening；SKILL.md 路由器化。精簡時移除未搬移的機制見註 ¹ |
| v5.0.4 | 2026-09-01 | BAT dispatch 補 --cwd 與 SKILL.md 摘要授權標註；ct-exec/ct-done/ct-status 新增 Landing Zone Check；cross-project-coordination 新增 HANDOVER / ADVISORY |
| v5.0.5 | 2026-09-01 | 落點檢查新增 C-0 repo identity 為承重檢查；C-3 降為輔助（實測偵測率 100%→41%）；新增 landing_check.expect_missing 逃生閥；工單模板新增 repo 欄位 |
| v5.0.6 | 2026-09-02 | 工單 ID 格式收斂為單一權威定義（`work-order-system.md` § 工單 ID 格式），全庫統一為「可選 2–4 位大寫前綴 + `T` + 數字」並放行帶前綴 ID；`auto-session.md` / `cross-project-coordination.md` 四處複述改為交叉引用；新增帶前綴 `--workorder` 的 BAT 最低版本標註與舊版 BAT 單次降級規則 |
| v5.0.7 | 2026-09-02 | `~/.claude/skills/` 寫入規則收斂為單一權威定義（`data-layer-architecture.md` § 寫入規則），明訂「任何非 skill 定義檔一律不得寫入」與掃描器機制（D006 實證）；6 處複述改為交叉引用；新增安裝／升級流程（備份落點 `~/.claude/skill-backups/` + 逐檔複驗 + 回退回報） |
| v5.0.8 | 2026-10-04 | 修正 15 項 drift（T0124／D010），同一規則多處敘述者收斂為一處權威＋交叉引用：決策日誌檔名統一 `_decision-log.md`（`_decisions.md` 僅留 legacy 相容讀取）；`_tower-state.md` 必要區段補 🔍 環境快照（7 項）；status enum 補 `PAUSED`、doctrine 移除 `REVIEW`；Layer 1 列滿 8 skill 與 `~/.codex/skills`；刪除懸空引用（Quick Recovery hygiene、研究/Spec 命名慣例）；研究互動改為 runtime `CT_INTERACTIVE` 優先；`gp-prefix` 收斂至 `multi-tower-protocol.md` 並刪除「`*config` 表已含」不實宣稱；mem0 標為不可查詢；前綴規則與工單最終態改交叉引用；本表 v5.0.2／v5.0.3 列更正並補記 v5.0.3 移除機制 |
| v5.0.9 | 2026-10-04 | Layer 1 寫入規則權威定義（`data-layer-architecture.md` § 寫入規則）範圍擴及 `~/.codex/skills/`：Q1／Q3 同樣適用、授權須指名目標路徑、Codex 端備份落點 `~/.codex/skill-backups/`；Q2 Codex 掃描器機制標為「比照、未實測」（D011／T0125）；`version-governance.md` 安裝流程補 Codex 端交叉引用；`playbook-engine.md`／`self-learning-core.md` 路徑守門改交叉引用；`memory-protocol.md` 模板示範值 `vX.Y.Z`；安裝指南全面更新至 v5.0.9 |
| v5.1.0 | 2026-10-15 | 新增 `*config` 選項 `worker_auto_close`（`off`/`done`）與 `worker_close_delay`（`0`–`300` 秒）：`DONE` 且不 Renew 的收單確認後以 BAT `--close-worker` 回收 Worker 分頁（MINOR：新增設定選項；`work-order-system.md` § 回報處理流程、`auto-session.md` Bash 白名單／安全規則、`yolo-mode.md`；CT-T011／D015／T0134）；BAT 文件落差修正：`bat-scripts.log` 成功紀錄 `"result":"ok"`、`yolo-mode.md` notify 失敗時工單已為最終狀態、`ct-exec` BAT Notify 補明 `ask`／`off`（CT-T012）；安裝指南新增 Codex 端 `AGENTS.md` 派工範例 |
| v5.2.0 | 2026-10-16 | 新增 Tower 啟動行為：在 BAT 內以 `bat-terminal.mjs --set-role tower --mode <m> --agent <claude|codex>` 宣告塔台分頁（BAT 設標題 `<Agent> · Tower`、記錄模式），啟動時與 auto-session 生效值改變時呼叫，非 0 exit 一律視為不支援（MINOR：新增 Tower 啟動行為；需 BAT `>= 0.6.1-pre.6`，舊 BAT 不受影響；權威定義 `auto-session.md` § 塔台分頁角色宣告；CT-T013／D147／D148／T0139）；v5.1.1 候選文件落差修正：`auto-session.md` notify 模式改引用 `ct-exec` § BAT Notify And Fallback（D017）、不存在的 Worker 步驟編號引用改指向實際小節、設定預設值的出處改為 `tower-config.md` § 可用選項、安裝指南斷點 A regex 改 `<WORKORDER_ID>`、`archive-system.md` 設定選項改交叉引用 |
| v5.2.1 | 2026-10-16 | PATCH：所有 BAT helper 呼叫（派工、Worker notify、`--close-worker`、`--set-role`）改用 `"${BAT_HELPER_NODE:-node}"`，權威規則在 `auto-session.md` § 執行方式「Node 解析」，取消 v5.2.0「只用於 `--set-role`」的限制；本機沒有此變數 → `node`，行為不變（D019／T0140）。新增塔台狀態面板最小定義（`memory-protocol.md` § 塔台狀態面板，唯一權威；不在 D010 刪除清單內）；YOLO 警語位置與字樣統一為面板下方 `⚠️ YOLO MODE ACTIVE`；`migration-engine.md` 改指向實際偵測來源；`archive-system.md` 用法子節拿掉「預設」字樣；Bash 白名單 helper 路徑分隔符號統一 |
| v5.2.2 | 2026-10-16 | PATCH：純文件修正，行為不變（D020／T0141）。`work-order-system.md` `--close-worker` 指令 helper 路徑分隔符號改為與 `auto-session.md` § 執行方式一致的 `\\`；`auto-session.md` § BAT 派發成功判讀規則第 1 點的 exit code 主體改稱「helper 程序（`bat-terminal.mjs`）」；`yolo-mode.md`、`work-order-system.md`、`research-workorder.md`、`work-order-template.md` 複述的 config 預設值（`yolo_max_retries`、`auto-session`、`worker_auto_close`、`research_max_questions`）改為引用 `tower-config.md` § 可用選項；`yolo-mode.md` § 啟動面板警語的「主面板」補連結到 `memory-protocol.md` § 塔台狀態面板 |
| v5.2.3 | 2026-10-16 | PATCH：純文件修正，行為不變（D022／T0143）。`control-tower/SKILL.md` 收單後回收 Worker 分頁一句拿掉 `worker_auto_close` 預設值複述，改為引用 `references/tower-config.md` § 可用選項；`yolo-mode.md` § 驗收、§ 迴歸測試的「主面板」補連結到 `memory-protocol.md` § 塔台狀態面板，與 § 啟動面板警語寫法一致 |
| v5.2.4 | 2026-10-17 | PATCH：BAT 規則修正（文件與失敗提示），對應 BAT `>= 0.7.0-pre.1` 的每分頁範圍權杖；舊 BAT 行為不變（CT-T014／T0149）。`auto-session.md` § BAT 內部終端路由 新增 § 範圍權杖與分頁角色（唯一權威）：`BAT_REMOTE_TOKEN` 為分頁專屬、不得複製或記錄；分頁角色依有無 `BAT_TOWER_TERMINAL_ID` 決定 helper 權限；塔台須在非 Worker 分頁啟動；派工／`--set-role`／`--close-worker` 非 0 時判斷仍只看 exit code，stderr 含 `Forbidden` 只多一句原因提示；派工遇 `RECOVERY_PENDING`（BAT Recovery 提示尚未回答）同樣只多一句提示、不自動重派。§ 塔台分頁角色宣告 第 5 點、§ BAT 派發成功判讀規則、§ 降級鏈、§ 安全規則、`work-order-system.md` `--close-worker` exit code 表、`memory-protocol.md` § 塔台狀態面板 BAT 列、`control-tower/SKILL.md` § BAT And Auto-Session 改為摘要＋引用 |
| v5.2.5 | 2026-10-17 | PATCH：文件補完，行為不變（D029／T0151）。`memory-protocol.md` § 塔台狀態面板 BAT 列：Worker 分頁的值改為 `不可派發（Worker 分頁）`，取代 v5.2.4 的加註寫法；`auto-session.md` 新增 § 對使用者描述分頁（唯一權威：對使用者用分頁標題，terminal ID 只用在日誌／證據／參數）；`work-order-template.md` 新增 § 撰寫 verification 工單的驗收步驟（驗收設計，不改變 CT 判斷只看 exit code 的規則）；`yolo-mode.md` 環境變數段補 Worker 分頁判定一句、`control-tower/SKILL.md` Scoped token 摘要補 `RECOVERY_PENDING`（皆為摘要＋引用） |
| v5.2.6 | 2026-10-17 | PATCH：安裝流程安全化 + 文件，行為不變（T0153）。§ 安裝／升級流程 Step 2 明訂不得先刪除已安裝的 skill 目錄再複製：先複製到 `skills/` 之外的暫存目錄，逐檔複驗全部 IDENTICAL 後才逐一替換，任一步失敗就停止；Windows／Git Bash 傳給原生程式的路徑用 `cygpath -w` 或相對路徑；Step 4 回退方式改為用同一套流程裝回備份（消化 T0151 安裝中斷事故）。安裝指南 § 4.1 範例同步改寫 |
| v5.3.0 | 2026-10-17 | MINOR：新增**選用**的 worktree 隔離派工與合併工單；工單不帶 `isolation` 時與 v5.2.6 完全相同；新功能需 BAT `>= 0.7.0-pre.2`，舊 BAT 不受影響（CT-T015／CT-T016／D031／T0155）。工單選用欄位 `isolation: worktree`（`work-order-template.md`）；派工加 `--isolation worktree`、exit `7` 不重試且不自動改非隔離（`auto-session.md` § worktree 隔離派工，唯一權威）；Worker 以 `CT_HOME` 判定在 worktree：工單寫回主 checkout、C-0 改比 `basename "$CT_HOME"`、收工前全部 commit、回報 `branch`／`base_sha`／`validated_sha`／`head_sha`（`ct-exec/SKILL.md` § Worktree Isolation，唯一權威；`ct-done` 引用）；隔離工單回收帶 `--worktree keep`（`work-order-system.md`）；新增 `merge-workorder.md`（唯一權威：三種模式、共同護欄、直接合併五條判準（第 1 條放寬版）、一律整合 worktree `--no-ff` 再 `--ff-only`、`--worktree-status`、收單 SHA 比對五步、清理）；合併工單模板（`kind: merge` 等欄位）；`yolo-mode.md` 新增斷點 E（合併前確認）；`auto-session.md` 新增 § BAT MCP 唯讀 tool（選用通道，MCP → helper CLI → 檔案）。另：§ 安裝／升級流程 Step 1 備份失敗即停、進 Step 2 前逐檔複驗備份（T0153 表外 1／D030）。發版後就地修訂隔離判定順序（`auto-session.md` § worktree 隔離派工 第 2 點；D032 一次性例外，版號不變；T0157） |
| v5.3.1 | 2026-10-18 | PATCH：文件補充，流程行為不變（T0158 表外／T0159）。`auto-session.md` § BAT 派發成功判讀規則 第 2 點新增 `bat-scripts.log` 檔案位置（CT 內唯一權威；解析順序同 BAT helper：`BAT_HELPER_LOG_DIR` → `BAT_USER_DATA` 的 `Logs\` → 都沒有就視為讀不到 log），§ worktree 隔離派工 第 2 點與 § BAT MCP 唯讀 tool 降級鏈改為引用；§ BAT MCP 唯讀 tool 判斷依據補「client 可能只顯示錯誤文字」，判斷仍只看是否為錯誤結果；`merge-workorder.md` § 合併完成後清理 補 `--ff-only` 成功後整合 worktree `switch --detach`，§ 直接合併的做法 的模式 ① git 指令範圍補列 § 合併完成後清理 |
| v5.3.2 | 2026-10-18 | PATCH：文件補充 + 補定義 MCP 降級鏈的未定義分支；BAT 介面不變（T0159 表外／T0160／D034）。`auto-session.md` § BAT 派發成功判讀規則 第 2 點「檔案位置」第 1 步：`BAT_HELPER_LOG_DIR` 須為絕對路徑，相對路徑忽略、往下走第 2 步（與 `BAT_USER_DATA` 對稱；依 BAT `scripts/_bat-logger.mjs`，BAT `CLAUDE.md` 未寫此點），解析順序三步不變；§ BAT MCP 唯讀 tool 降級鏈補「錯誤結果取不到 code（`structuredContent` 看不到、錯誤文字也認不出已知 code）→ 視同可降級，改用同功能 helper CLI、沒有對應 helper 就讀檔案，結果以 helper exit code 為準，不重試同一個 tool」；取得到 code 時的降級條件與「判斷依據：只看 `isError`」不變 |
| v5.4.0 | 2026-10-18 | MINOR：放寬隔離工單的狀態查詢時機——BAT `>= 0.7.0-pre.4` 時 Worker 分頁回收後也可查 `--worktree-status`（回傳 `source`：`live`／`exited`／`git`）；舊 BAT（成功回傳沒有 `source`）仍須回收前查；合併判準五條不變；BAT 介面不變（CT-T017 § 一／T0161／D035／D036）。`merge-workorder.md` § 合併判準資料來源 新增「查詢時機與資料來源」（唯一權威），exit `3`／`4`／`1` 列補新 BAT 下的意義（處理不變），JSON 欄位表補 `source`／`exited`／`exitedAt`／`terminalId: null`；§ 流程總覽 第 2 點「回收前查」改為只對舊 BAT；`auto-session.md` § BAT MCP 唯讀 tool 的 `bat_worktree_status` 列與 BAT 命令表補版本條件。CT-T017 § 二（`blocked`／斷點 D）不在本版（D036） |
| v5.5.0 | 2026-10-18 | MINOR：新增 yolo 提問通道、斷點 D、config `worker_question_timeout`，斷點 A 合法字串新增 `提問`；BAT 介面不變；非 yolo 的 Worker／塔台行為不變（BAT CT-T017 § 二／T0596／T0597；D035～D037／T0163）。`yolo-mode.md` 新增 § Worker 向塔台提問（唯一權威：yolo Worker 不向使用者提問，問題寫工單 `### 待塔台決策` `Q-n`、frontmatter `tower_question: open`、送 `T#### 提問` 後原地輪詢工單檔的 `塔台答覆 Q-n`，間隔 ≥ 30 秒、上限 `worker_question_timeout`；逾時／`0`／沒有等待工具／通知失敗 → `BLOCKED` + `T#### 需要協助`，塔台在 Renew 區段答覆後重派；塔台範圍內代決、範圍變更／不可逆／對外發布／需要偏好才問使用者；不計入 `yolo_max_retries`）與 § 斷點 D（唯一權威：塔台查到 Worker `state == blocked` 時以分頁標題告知，yolo 為異常偵測、非 yolo 為告知；不代答、不送按鍵、不輪詢、不重派、不計入斷點 B；同一 `blockedSince` 只告知一次；`blockedReason` 照原值、不斷定；只走 MCP，沒有 `blockedDetection` 或 `none` 時不啟用；BUG-150 修正前後的差異以「修正版（版號已由 v5.5.1 補為 BAT `>= 0.7.0-pre.5`）」表述）；§ 斷點 A regex 改為 `(完成|部分完成|需要協助|提問|失敗)`；§ 啟動詢問（G3）yolo 不再詢問、一律 `--no-interactive`。`auto-session.md` § BAT MCP 唯讀 tool `bat_get_state`／`bat_wait` 列補 `blocked`，刪除 v5.4.0 以前「斷點 D 等 BAT 提供 `blocked`」的舊說法、改引用 § 斷點 D；`tower-config.md` 新增 `worker_question_timeout`（`0`～`120` 分鐘，預設 `30`）；`ct-exec/SKILL.md` 新增 § Questions For Tower（摘要＋引用）與 `提問` 映射；`ct-done/SKILL.md` § BAT Notify 註明不送 `提問`；`research-workorder.md`、`work-order-template.md`、`work-order-system.md`、`control-tower/SKILL.md`、`ct-help/SKILL.md` 補摘要與引用 |
| v5.5.1 | 2026-10-18 | PATCH：補 BAT 版號與 yolo 防護提醒，BAT 介面不變、非 yolo 行為不變（T0164／D038）。`yolo-mode.md` § 斷點 D：BUG-150 修正版的占位寫法改為 BAT `>= 0.7.0-pre.5`（AskUserQuestion 回報 `question`、以滑鼠或鍵盤回答後由 `PostToolUse` 立即清除；`0.7.0-pre.4` 的修正前說明保留），已知限制新增第 5 點（BAT 重開／headless server 重啟後 `blocked`／`blockedDetection` 遺失、可能漏報一次），§ BAT／Worker 版本相容 新增 `0.7.0-pre.5` 列；`ct-exec/references/session-guardrails.md` 新增 § yolo 下的處理（範圍守衛照 [B]、熔斷 `warn` 照 `block`、洋蔥偵測照 [A]、超時只記錄；需要決定時走 § Worker 向塔台提問；非 yolo 不變），`tower-config.md` `worker_strikeout_action` 列同步一句；`work-order-template.md` 研究型與盤點模板補 `### 待塔台決策`；`auto-session.md` § BAT 派發成功判讀規則 補充 exit `0` 只代表分頁已建立、MCP 可用時可用 `bat_get_state`／`bat_read_output` 確認 Worker 已啟動（BAT BUG-151，判讀規則不變） |
| v5.6.0 | 2026-10-18 | MINOR：新增 Worker 啟動確認——派工帶 `--wait-started 30000`、新 exit `8`；不帶參數時的派工命令、輸出與 exit code 與 v5.5.1 相同；需 BAT `>= 0.7.0-pre.6`，舊 BAT 去掉參數重派一次後行為同 v5.5.1（BAT CT-T018／T0600；D039／D040／T0165）。`auto-session.md` 新增 § Worker 啟動確認（唯一權威：何時帶、四種結果——`started: <時間>` 已啟動／`started: unknown` 無法判定、照現行流程、不是失敗／exit `8` `started: unconfirmed` 分頁在、不重派、MCP 可用看 `bat_read_output` 否則以分頁標題提醒使用者／exit `1` 照既有規則；`started:` 行只在帶參數時解析；舊 BAT exit `1` + stderr `Unknown option '--wait-started'` → 去參數重派一次、本 session 記為不支援（只記 session 記憶）；stderr 只用來選降級路徑）；§ BAT 派發成功判讀規則 v5.5.1 暫時補充改為引用新小節、補 exit `8` 與 Unknown option 兩個例外；§ 執行方式、Bash 白名單、§ 安全規則（`--wait-started` 值域、必須搭配 `--notify-id`、只用在派工）、§ BAT MCP 唯讀 tool（`agentStarted`／`agentStartedAt`／`until: 'agent-started'`；仍沒有任何 CT 規則必須使用 MCP）、§ 依賴的 BAT 基礎設施 補 `0.7.0-pre.6`；`yolo-mode.md` § 斷點 D 已知限制第 4 點依 BAT 版本分寫（`>= 0.7.0-pre.6` 讀得到的 `disableAllHooks`／`allowManagedHooksOnly` → `blockedDetection: none`），§ BAT／Worker 版本相容 新增 `0.7.0-pre.6` 列；`control-tower/SKILL.md` 派工摘要補參數與一行摘要 |
| v5.6.1 | 2026-10-18 | PATCH：T0166／T0167 實機驗收表外六項規則補洞；BAT 介面、派工命令不變，非 yolo 的 Worker／塔台行為不變（T0168／D045／D046）。`yolo-mode.md` § Worker 向塔台提問：Worker 端第 2 點 `tower_question: open` 列為送 `T#### 提問` 前的必要步驟（原地等待與 `worker_question_timeout = 0` 直接走備援都一樣）、送 `提問` 前工單（與依政策要 commit 的產品變更）先 commit；第 3 點「出現答覆行」只認 `### 待塔台決策`／`## 塔台補充（Renew #N）` 區段內行首 `- **塔台答覆 Q-n**` 的答覆行（附區段限定的 `awk` 比對），工單本文同樣字樣不算；第 4 點備援在 notify 前 commit 工單（含 `BLOCKED`）；§ 塔台端「收到 `提問`」新增第 0 點（`worker_question_timeout: 0` 或已 `BLOCKED` → 不在題目下答，等 `需要協助` 後只在 Renew 區段答），「收到備援」的 Renew 答覆行格式與第 3 點相同；`control-tower/SKILL.md` yolo 提問摘要補第 0 點。`ct-exec/SKILL.md` § Questions For Tower 同步（送出前檢查、答覆行判斷、備援 commit），§ Phase 4 Status rules 之後補分段工單只就 Worker 段落判定狀態。`work-order-template.md` § 撰寫 verification 工單的驗收步驟 新增第 4 點（開單寫明段落歸屬；塔台段落沒證據不構成 `PARTIAL`）。`merge-workorder.md` § 查詢時機與資料來源：合併後 `source: git` 的 `base` = merge-base（= `head`）、`ahead 0`、`changedFiles []`，五條判準必須合併前取。版號：8 個 `SKILL.md`、H1、本檔範例 → `5.6.1`；安裝指南新增 § 2.36 |
| v5.7.0 | 2026-10-18 | MINOR：yolo Worker 問塔台新增 BAT 結構化通道（雙寫：題目仍先寫工單並 commit）；BAT 太舊或通道失效時回到 v5.6.1 的工單檔往返或備援；非 yolo 的 Worker／塔台行為、派工命令、`--wait-started`、隔離派工與合併流程不變；需 BAT `>= 0.7.0-pre.7`（BAT CT-T019／T0607／T0608／T0611；D045／D048／T0169）。`yolo-mode.md` § Worker 向塔台提問 新增 § BAT 通道（唯一權威：雙寫、內容只走 stdin、MCP `bat_wait_question`／`bat_list_questions` 欄位、BAT 限制常數、四列「版本判定與降級」表、已知限制）；§ Worker 端 第 3 點分為 3-A BAT 通道（`bat-notify.mjs --ask` → `bat_wait_question` 迴圈、備援 `--wait-answer`、間隔不超過 120 s、`answered`／`lost`／`cancelled`／`expired` 的處理、`--cancel-question` 看 `status:` 行）與 3-B 工單檔等待（v5.6.1 原第 3 點）；§ 塔台端 讀題時呼叫 `bat_list_questions`，BAT 題目以 `bat-terminal.mjs --answer` 答覆、成功時不寫工單答覆行，其餘照舊寫工單；exit `3`／`1` 改寫工單、`9` 看 `status:`、`4` 斷點 A；不背景輪詢；§ 斷點 D：`blockedReason: tower` 不是斷點 D，`blockedDetection: none` 改為「永遠不會回 hook 的三種 reason」；§ BAT／Worker 版本相容 新增 `0.7.0-pre.7` 列；`auto-session.md` § BAT MCP 唯讀 tool、§ 依賴的 BAT 基礎設施、Bash 白名單與安全規則（`--answer`）補新 tool／欄位並引用 `yolo-mode.md`；D047 三項：`ct-exec/SKILL.md` § Phase 4 非隔離收尾改為與 § Worktree Isolation 第 8 點同序（產品 commit → 回報區 → 最終 metadata → 工單 commit → notify）、`work-order-template.md` `tower_question` 說明補「送 `提問` 前必加、BAT 通道也加」、`ct-done/SKILL.md` § Workflow notify 前 commit 工單檔本身（產品變更不代為 commit） |
| v5.7.1 | 2026-10-18 | PATCH：yolo 提問通道補洞六項（CT v5.7.0 實機驗收 F-1／O-1／O-2、T0168 表外 2、D049 表外 1）；BAT 介面不變，BAT 最低版本仍 `>= 0.7.0-pre.7`；非 yolo 的 Worker／塔台行為、派工命令、`--wait-started`、隔離派工與合併流程不變（T0170／D052）。`yolo-mode.md` § Worker 向塔台提問：§ 塔台端 第 1 點改為 `bat_list_questions(status: all)` 加工單 `- **通道**：工單` 標記逐題判斷的表（標記 → 工單答覆；`pending` → BAT 答覆；`answered` 不動作；`cancelled`／`lost` → 工單答覆；`expired` 等備援；列表沒有又沒標記 → 這則先不答），不得以「列表目前沒有 `pending`」推論 Worker 已送完，同一題只能有一個生效答覆，O-1（只有取消後降級）併入同表說明；§ Worker 端 3-A 第 1、2 步：多題先送完所有 `--ask`，退回的題加 `通道` 標記、commit 後最後送一則一般 `提問`，沒有退回就不送；3-B `awk` 區段比對略過 fenced code block；§ BAT 通道 版本判定與降級兩列、已知限制、§ BAT／Worker 版本相容（新增 v5.7.1 列）、T9 對齊；`ct-exec/SKILL.md` § Questions For Tower 摘要同步、送出前檢查補 Q-n 標題，§ Phase 4 第 4 步後 notify 前自檢三項（O-2）；`control-tower/SKILL.md` 摘要同步；`tower-config.md` `worker_question_timeout` 補「也是 `--ask --expires-min` 的值」；`work-order-template.md` 待塔台決策範本補標記說明 |
| v5.7.2 | 2026-10-18 | PATCH：晚退回的題也加 `通道` 標記，塔台不再依賴 BAT 已結束題目的保留期（T0170 表外 2、D054）；BAT 介面不變，BAT 最低版本仍 `>= 0.7.0-pre.7`；非 yolo 的 Worker／塔台行為、派工命令、`--wait-started`、隔離派工、合併流程、`--ask` 失敗流程、`expired` 備援與 `worker_question_timeout = 0` 不變（T0171／D055）。`yolo-mode.md` § Worker 向塔台提問：§ Worker 端 3-A 新增第 6 步——`--ask` 成功後因 `lost`／`cancelled`（含 Worker 自己取消且 `status: cancelled worker`）或等待工具都不能用而改走 3-B 的題，加 `- **通道**：工單` → commit 工單 → 送一次一般 `T#### 提問`（同時多題只 commit 一次、送一則）；`--cancel-question` 回 `answered`／`expired` 不加標記；等待期間只讀不寫的唯一例外；推翻 v5.7.1「晚退回不加標記、不另送通知」；§ 塔台端 第 1 點表「`cancelled` / `lost`」改為「`cancelled`」（`lost` 不在列表），O-1 說明改寫、寫明同一題不會兩個通道都答；§ BAT 通道 已知限制補 BAT 保留規則（10 分鐘／64 筆／重開全清／`lost` 不在列表）與「正確性不依賴保留期」；版本判定與降級表、§ 備援、§ BAT／Worker 版本相容（新增 v5.7.2 列）、T9 對齊；`ct-exec/SKILL.md` § Questions For Tower 摘要同步；`work-order-template.md` 待塔台決策範本的標記說明同步 |
| v5.8.0 | 2026-10-18 | MINOR：接 BAT codex 分頁的 OSC 7501 信號——斷點 D 接受 `blockedDetection: osc`／`blockedReason: input`，codex `>= 0.163.0` 的 `--wait-started`／`agentStarted` 生效；BAT 介面以 BAT T0621 C-1–C-8 為準，需 BAT `>= 0.7.0-pre.9`；舊 BAT（≤ `0.7.0-pre.8`）或較舊 codex → `none`／`null`／`started: unknown`，行為同 v5.7.2；非 yolo 的 Worker／塔台行為、派工命令、隔離派工、合併流程、提問通道與 `worker_question_timeout` 不變（BAT CT-T020／T0621；D058／T0172）。`yolo-mode.md` § 斷點 D：判準加 `input`、`none` 也不回 `input`、優先序、`input` 清除（使用者輸入不清除）、已知限制第 1 點改寫、第 5 點補 codex replay、新增第 6 點；§ BAT／Worker 版本相容新增 codex OSC 7501 列；T10 情境 2。`auto-session.md` § BAT MCP 唯讀 tool：值域加 `osc`／`input`、`agentStarted` 補 `osc` 分頁；§ Worker 啟動確認：codex 信號、`unknown` 改為「codex 低於 0.163.0 或版本確認不到」、codex 常見 exit `8` 原因、C-6 由 BAT 加；§ 依賴的 BAT 基礎設施 新增一列。`control-tower/SKILL.md` 兩處摘要 |
| v5.8.1 | 2026-10-18 | PATCH：BAT `v0.7.0-pre.9` 已發佈，v5.8.0 的 BAT 版本占位字串換成 `>= 0.7.0-pre.9`；BAT 介面不變，非 yolo 的 Worker／塔台行為、派工命令、斷點 D 判準、`--wait-started`、隔離派工、合併流程、提問通道流程與 `worker_question_timeout` 不變（T0173／D064）。`yolo-mode.md` § Worker 向塔台提問：題目範本「提問時間」寫明取值指令（F-2）；§ 塔台端 第 3 點註明塔台答覆行由 Worker 的工單 commit 帶入屬預期行為（O-3）。`ct-exec/SKILL.md` § Phase 4 自檢 (a) 不合格只在 `### 遭遇問題` 記錄、不改已送出的題目（F-2）。`work-order-template.md` 提問範本引用取值權威 |
| v5.9.0 | 2026-10-18 | MINOR：接 BAT CT-T021（Claude session 識別，PLAN-050）——新增跨 session 選收件人規則（① ListAgents `<工作區> · Tower` → ② `bat_list_terminals scope=towers` 以 `workspaceName` 對 `claudeSessionName` → ③ `_reply-*.md` 由使用者轉交；` · Worker · T####` 一律不是塔台）、MCP 欄位 `claudeSessionName`／`claudeSessionId`（鍵不存在 = 舊 BAT）與 `scope: towers`、塔台面板 session 名稱提示行；BAT 介面以 BAT T0643「PLAN-050 介面契約總表」C-1–C-8 為準，需 BAT `>= 0.7.1-pre.1`；舊 BAT（≤ `0.7.0-pre.9`）或非 BAT → 第 ③ 步、無提示，行為同 v5.8.1；派工命令、`--set-role` 流程、斷點 D、提問通道、隔離派工、合併流程與 `worker_question_timeout` 不變（T0174／D069）。`cross-project-coordination.md` 新增 § 跨 session 選收件人；`auto-session.md` § BAT MCP 唯讀 tool、§ 依賴的 BAT 基礎設施、§ 對使用者描述分頁；`memory-protocol.md` § 塔台狀態面板；`control-tower/SKILL.md` 三處摘要 |
| v5.10.0 | 2026-10-20 | MINOR：Workflow 智能 P2 規則層——新 reference `workflow-engine.md`（Claude Code Workflow 的唯一權威：定位為 Worker 在單張工單內的執行方式、不是 CT 編排層；Skill／Playbook／Workflow 三分法；工具型／派工型；設計規則 R1–R5；知識卡 `_ct-workorders/_workflows/`；成熟度與回測，回測或試跑前列規模經使用者同意；只限 Workflow 的指標降級；成本與規模；同意治理原則；Codex 不支援）、新規則組 `ct-insights/references/analysis-rules.md` § Workflow 適配度（S1–S6／X1–X5、兩軌、分級、WFC 格式）、新 `ct-evolve --workflow` 模式（只產 brief 與 🔵 知識卡，不寫 `.claude/workflows/`）與 `[WF-CANDIDATE]`；`data-layer-architecture.md` § 寫入規則 新增「Layer 3 附屬：專案 workflow 腳本」；`doctrine.md`、`playbook-engine.md`、`self-learning-core.md`、`control-tower/SKILL.md`、`ct-insights/SKILL.md` 補摘要與引用。派發匹配、frontmatter 欄位、`ct-exec` 執行路徑、Codex 派工檢查在 v5.11.0；BAT 無最低版本需求；派工命令、`--set-role`、斷點、提問通道、隔離派工、合併流程、`worker_auto_close` 與 `ct-exec` 執行流程不變（T0178／D082） |
| v5.11.0 | 2026-10-20 | MINOR：Workflow 智能 P3 精簡版（G2 未通過後的路線，D089／D090）——新設定 `workflow_integration`（`off`／`ask`／`on`，有效值與預設只在 `tower-config.md` § 可用選項；各值對塔台的影響在 `workflow-engine.md` § `workflow_integration` 的行為；Worker 不讀，D083）；新命令入口塔台 `*insights workflow [T#### …]` 與 `*evolve --workflow`（轉交 `/ct-evolve --workflow`）；預篩腳本 `ct-insights/scripts/ct-workflow-prefilter.py` 隨 skill 發行並修 E4–E6，只做排除守門（X2、X3、X5；X5 提示 Playbook）與按需提示、不自動標記工單（`ct-insights/references/analysis-rules.md` § 預篩腳本：排除守門與按需提示，D085 (C)）；`ct-exec/SKILL.md` 新增 § Workflow And Sub-Agents（唯一權威：只有工單明文授權才呼叫 Workflow、超出上限先問塔台、自發唯讀子代理要在回報區記錄數量／用途／唯讀／約略 tokens）；`work-order-template.md` 新增 § 撰寫 Workflow 使用授權（`off` 時不得寫）；`workflow-engine.md` 新增 § 現況：G2 未通過（refuter 會確認錯誤發現、reader 實測 100–180k／組、成立的扇出多為 Worker 自發）、§ 尚未定案（具名 workflow 的派發與執行、`execution` 等 frontmatter 欄位待卡片達 🟡），R4 加註 Explore 型仍有 shell；`data-layer-architecture.md` § Layer 3 附屬 補 workflow 腳本語法檢查做法；`ct-evolve.md` 長版說明補 `--workflow`；`playbook-engine.md`、`control-tower/SKILL.md`、`ct-insights/SKILL.md`、`ct-help/SKILL.md` 補摘要與引用。BAT 無最低版本需求；派工命令、`--set-role`、斷點、提問通道、隔離派工、合併流程、`worker_auto_close` 與 `ct-exec` 其他執行流程不變（T0183／D090） |
| v5.12.0 | 2026-10-22 | MINOR：接 BAT CT-T022（BUG-170）——新增塔台行為「重派前回收舊 Worker 分頁」：對同一張工單再派 Worker（yolo 提問備援、`BLOCKED`／`FAILED` 後 Renew 重派、使用者停掉首派或派工 exit `8` 後決定重派）之前，先 `--close-worker T#### --notify-id … --delay-ms 0`（隔離工單加 `--worktree keep`）；exit `0`／`3` 繼續派工，`4`／`5`／`1`／其他一行提示後繼續派工（`1` 與收單回收共用「不支援 `--close-worker`」session 旗標），不得擋住重派；`--skill ct-done` 補救派工、研究單使用者在原分頁重讀工單、`Unknown option '--wait-started'` 去參數重派、首派不回收；與 `worker_auto_close` 無關（`off` 也回收）。權威 `work-order-system.md` § 回報處理流程 › 重派前回收舊 Worker 分頁，其他檔只放摘要與引用。BAT 介面不變、CT 最低 BAT 版本不變（`--close-worker` 自 v5.1.0）；無新設定、無新工單欄位（T0184／D094） |
| v5.12.1 | 2026-10-22 | PATCH：文件修正、行為不變——`tower-config.md` § 可用選項 `worker_close_delay` 列的取消條件改成照 BAT T0545／D145：延遲期間的輸出不取消回收；只有排程後使用者在 Worker 分頁的輸入會取消（終端自動回應不算輸入）；延遲到期後 BAT 等分頁連續安靜 5 s 才關，最多再等 60 s，仍在輸出就放棄、分頁保留。安裝指南 § 13 同列對齊、新增 § 2.46。`worker_close_delay` 值域與預設、`--delay-ms` 換算、收單回收與重派前回收的條件／指令／exit code 不變；BAT 介面不變（T0185／D096） |
| v5.12.2 | 2026-10-22 | PATCH：文件修正、行為不變——`work-order-system.md` § 收單後回收 Worker 分頁 exit `0` 列：可加的一行提示由「Worker 分頁將於 N 秒後回收」改成「Worker 分頁約 N 秒後回收」，並補一句：延遲到期時分頁仍在輸出，BAT 會等連續安靜 5 s、最多再等 60 s，屆時仍在輸出就放棄、保留分頁；helper 已 exit `0`，塔台不會得知，所以提示不得寫成確定的時間或「已關閉」（條件細節引用 `tower-config.md` § 可用選項 `worker_close_delay`）。exit `0` 的處理仍是「靜默」；其他 exit code 列、收單回收與重派前回收的條件／指令不變；BAT 介面不變（T0186／D098） |
| v5.12.3 | 2026-10-23 | PATCH：文件修正、行為不變——`--close-worker`（收單後回收、重派前回收）的最低 BAT 更正為 `>= 0.6.1-pre.4`（[5.1.0] 原寫 `0.6.1-pre.3`；BAT 塔台回覆 P3、`2321c719`；歷史段落不改）；D182／D183／D185 累積的文件不一致收斂：安裝指南 `ct-insights` 作用域、`doctrine.md` 反序收尾順序（照 `ct-exec` § Phase 4）與 `*status` 字樣、`tower-config.md` 註明 `gp-prefix` 不是 `*config` 選項、`yolo-mode.md` 補 § YOLO 計數器小節、實戰補充（一-B）改 `*pause`／status enum、置信度條件分專案層（2+ 工單）／全域層（2+ 專案）（權威 `self-learning-core.md` § 置信度系統；T0256 Q-1）、註明 zip 不含 `docs/`。T0256／D221。BAT 介面不變 |
| v5.12.4 | 2026-10-23 | PATCH（依 § SemVer：文件補完／修正與發行物打包，沒有新命令、新設定或不相容變更；刪的檔案沒有任何引用）：退役 `control-tower/references/ct-exec.md`（與 `ct-exec/SKILL.md` 不一致、無引用；權威只剩 `ct-exec/SKILL.md`；`doctrine.md` 泛稱改實際檔名）；`yolo-mode.md` 連續 FAILED 計數器位置統一為 `_tower-state.md` 的 `## YOLO 歷程` › `### 計數器`（計數規則、重設時機、斷點 B 語意不變）；發行物另出 `-skills/` 8 個單一 skill zip、教學 skill zip 改根層唯一資料夾 `control-tower-guide/`、上傳腳本 UI 路徑改 Customize → Skills。T0260／D238。BAT 介面不變 |
| v5.12.5 | 2026-10-23 | PATCH（依 § SemVer：文件補完／修正，沒有新命令、新設定或不相容變更；三份長版說明從來不是權威，SKILL 與 `playbook-engine.md` 一直要求確認，D246）：退役 `control-tower/references/` 其餘三份 Worker 命令長版說明（`ct-done`、`ct-status`、`ct-evolve`），仍有效的規則先補進 `ct-done/SKILL.md`（`PENDING` 防呆、`sprint-status.yaml` 補同步）、`ct-status/SKILL.md`（sync 落差交給塔台）、`ct-evolve/SKILL.md`（估時偏差 >50%、只建議 `--playbook`、路由 `enhancement-integration.md`）、`self-learning-core.md`（`/ct-evolve` 連結改 SKILL；塔台主動提議的觸發詞、≥10 筆門檻、提議格式；結案改確認＋分流）、`playbook-engine.md`（不再引用「Step 4」）；`ct-status` § Status Buckets 補 `INTERRUPTED` → Needs Tower judgment（D248）。T0267／D248。BAT 介面不變 |
| v5.12.6 | 2026-10-25 | PATCH（依 § SemVer：只改說明文字，沒有新命令、新設定或不相容變更）：發行內容去識別——範例與由來說明裡可識別的私人專案名、本機絕對路徑、內網主機位址、私人規則名、分頁短 id、私有詞換成中性說法或範例值，以便公開發行；規則與行為不變（指令、旗標、exit code、步驟順序、檔名不動）。T0293／D309。BAT 介面不變 |
| v6.0.0-pre.1 | 2026-10-25（**預覽，不發布**：只打包、不安裝、不建 Release） | 預覽（版號依 G0 定案 D332，取代原建議的 v5.13.0）：方法論轉接——契約權威檔 `methodology-adapters.md` 與內建 adapter `adapters/bmad.yaml`；`enhancement-integration.md` Level 2 由「外部 bmad-guide」改為「方法論轉接」，BMAD 路由、退役名稱與工單標注移進 `bmad.yaml`；`SKILL.md` 加 `## Methodology Adapters`；BMAD 舊名漂移修正（`bmad-build-auto`、`bmad-build`、`baseline_revision..HEAD`、`bmad-build-auto-result-*.md`、Build 內建 Review Triage）。工單模板與派工：`work-order-template.md` 改成 `### 方法論工作流程`＋`### 方法論邊界`、回報區 `### 方法論執行紀錄`＋`### 方法論狀態回寫`、選用 frontmatter `methodology`；`work-order-system.md` 依各層 adapter `routing` 選 workflow、派工摘要每層一行方法論。設定鍵：`tower-config.md` § 可用選項 9 個 `methodology*` 鍵與 § 方法論設定鍵、`*config methodology`、`*help methodology`；`onboarding.md` 主題 5 主方法論。Worker 端：`ct-exec` § Methodology（依 adapter `worker.invoke` 帶入、CT 規則優先、`methodology_ambient` 自查、`### 方法論執行紀錄`、方法論子代理預設唯讀）；`ct-status`、`ct-done`、`ct-insights` 改讀主方法論 `tracker`。外部 adapter `ct-adapter-pstack`（`adapter_version` 0.2.2，另出 zip）與驗證腳本 `control-tower/scripts/validate-adapter.py`（M1～M15；zip 不含 `scripts/tests/`）。`_tower-state.md` 機器可讀摘要：`memory-protocol.md` YAML frontmatter 契約 v1，`SKILL.md` § Startup Protocol 第 8 步、`interrupt-protocol.md` 指回。V1／V2 實測結果落地：`methodology_guard: warn` 派工自動加 `### 方法論邊界`（D342）、多家注入標「雙注入」、Codex 方法論 hook 由使用者信任、adapter 契約新選填欄位、`auto-session.md` exit `8` 補 codex 成因；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-pre.1]`。向下相容：`methodology` 缺省 = `auto` = v5.12.6 行為，沒有 `methodology` 欄位的工單 Worker 行為不變，舊 `### BMad 工作流程` 段照讀。T0300～T0313（實測 T0299、T0307、T0308）／D332。BAT 介面不變 |
| v6.0.0-beta.1 | 2026-10-27（**Beta**：只打包、不安裝；與穩定版 5.12.7 並行、不取代，D364） | Beta（PLAN-001 P1～P3）：P1／P1b 實測（T0314 隔離目錄試用、T0315 pstack 組合）後的 P2 修補（T0318）與 P3 定稿（T0319）。方法論：新 § 引入方式（完整安裝／只引用 skill／部分參考，D369）、`### 方法論狀態回寫` 在主方法論有 `tracker` 時保留、塔台語言不因注入改變、全域路徑照 `${CLAUDE_CONFIG_DIR:-~/.claude}`／`${CODEX_HOME:-~/.codex}`（`data-layer-architecture.md` § 路徑解析）、沒有 scratchpad 時的暫存目錄退路、`methodology_ambient` 寫法對照、workflow 自帶的唯讀審查子代理要回報、C5 觸發條件、無 adapter 注入的 `always_on_tokens` 寫「未量測」；`ct-adapter-pstack` `adapter_version` 0.2.3（`only_in`／`background`、`tested_version` 0.9.103）。設定：`enable_bug_tracking`／`enable_plan_tracking`／`enable_experiments` 預設 `true`（明寫 `false` 照舊），啟用即產生空索引（`bug-plan-system.md` § 啟用與索引檔、§ 索引格式）。環境偵測只列變數名稱（`auto-session.md` § 偵測條件；同 v5.12.7 的修正）。契約仍 `ct-methodology-adapter/v1`；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.1]`。BAT 介面同 v6.0.0-pre.1 |
| v6.0.0-beta.2 | 2026-10-27（**Beta**：只打包、不安裝；與穩定版 5.12.8 並行、不取代，D364） | Beta（PLAN-002 B1、PLAN-003 B1／G／B2）：方法論引入的結論——「方法論不是一定要引入」原則，BMAD 引入（內建）、pstack 選用（已在用才裝）、Superpowers 不建議引入（只留 C1／C5／C10 共存防護）、mattpocock/skills 為 ③ 的可選做法範例（品質效益未實證）；§ ③ 的做法、C1 ⑤ 沒有 hook 的描述觸發、「方法論 skill」範圍含工單指名的 ③ 本地副本（`ct-exec` § Methodology）；③ 已實測（P3）、C5 依 P3 改寫。環境偵測 bash 寫法改 `compgen -e`、明列例外一個變數一個指令（`auto-session.md` § 偵測條件）。`ct-adapter-pstack` `adapter_version` 0.2.4（只改 README 的選用定位）。契約仍 `ct-methodology-adapter/v1`、設定鍵不變；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.2]`。BAT 介面同 v6.0.0-pre.1 |
| v6.0.0-beta.3 | 2026-10-29（**Beta**：只打包、不安裝；與穩定版 5.13.0 並行、不取代，D364） | Beta（狀態衛生＋BAT 塔台面板讀取契約，T0332／D404～D408；同批規則穩定版 5.13.0 也有，D411）：新 `memory-protocol.md` § BAT 塔台面板讀取契約（熱檔大小預算 409,600 bytes、BAT 讀檔上限 524,288 bytes、各檔 BAT 依賴的格式、嚴重度／優先級值域對照），Startup Protocol 與 `*sync` 量熱檔大小並提示；`decision-log-system.md` 索引表頭 `ID`、標題格式與 § 收斂（舊詳細紀錄搬到 `_archive/decisions/`）；`bug-plan-system.md` § 索引格式（`報修時間`／`關閉時間`、`相關工單`、格子 `🔴 High` 等、Dropped 表頭 `ID`、〈後續待辦（延後的 BUG）〉）、§ 結案判準（不新增狀態值，選填 `closed_reason`）、§ 未結 BUG 清理提示、改狀態同批重建索引；`work-order-system.md` § PARTIAL 當下收尾；`work-order-template.md` 客戶驗收不回歸閘（可選）。新設定 `bug_review_open_threshold`（預設 `20`）、`bug_review_stale_days`（預設 `30`）、`customer_acceptance_gate`（預設 `off`）。從 beta.2 升級不需遷移、設定缺省即舊行為；舊索引下次 `*sync` 重建。方法論契約仍 `ct-methodology-adapter/v1`、`ct-adapter-pstack` 仍 0.2.4；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.3]`。BAT 介面同 v6.0.0-pre.1（讀取契約對照 BAT `0.7.1-pre.8`） |
| v6.0.0-beta.4 | 2026-10-30（**Beta**：只打包、不安裝；與穩定版 5.13.1 並行、不取代，D364） | Beta（通知用工單完整 ID＋BAT 塔台面板讀取契約對齊 BAT `0.7.1-pre.9`，T0342／D422；同批規則穩定版 5.13.1 也有）：新 `work-order-system.md` § 回報與通知用的工單 ID（通知範本由 `T####` 改成 `<工單 ID>`、照 frontmatter `id` 原樣用、不得截短；Worker 送出前與 frontmatter `id` 比對）與 § 回報處理流程 › 回報 ID 對不上時（塔台端缺前綴容錯：熱區恰好一張「前綴＋同號」時當作那一張並記錄，多張或找不到就問使用者）；ct-exec、ct-done、`auto-session.md`、`yolo-mode.md` 的通知與提問範本都指回權威段。`memory-protocol.md` § BAT 塔台面板讀取契約 改寫成 BAT `>= 0.7.1-pre.9` 的表現（讀不到時顯示「無法讀取 <檔名>」、`critical` 在任何讀取路徑都算 High；更舊的 BAT 照舊靜默變空，400 KB 預算保留），`bug-plan-system.md` 同步一句；`work-order-system.md` 派工摘要與回報確認範例的 `bmad-project-context` 產出改 `AGENTS.md` 的專案上下文區塊。沒有新命令或新設定；從 beta.3 升級只換 skill 檔案，不需改設定或工單。方法論契約仍 `ct-methodology-adapter/v1`、`ct-adapter-pstack` 仍 0.2.4；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.4]`。BAT 介面同 v6.0.0-pre.1（讀取契約對照 BAT `0.7.1-pre.9`） |
| v6.0.0-beta.5 | 2026-10-30（**Beta**：只打包、不安裝；與穩定版 5.14.0 並行、不取代，D364） | Beta（plugin 安裝就緒的規範移植，T0354／D443；同批規則穩定版 5.14.0 也有）：三個權威位置——`data-layer-architecture.md` § 寫入規則（Layer 1 加 plugin 安裝路徑；Q2 plugin 由 plugin manager 管理、Q3 plugin 安裝的授權、Q4 plugin 不備份）與 § 路徑解析 的 `~/.claude/plugins/` 例外列（`~/.claude/plugins/` 與設了 `CLAUDE_CONFIG_DIR` 時的 `${CLAUDE_CONFIG_DIR}/plugins/` 兩處都算 Layer 1；`CLAUDE_CONFIG_DIR` 會不會搬移 plugin 目錄未驗證）、本檔 § 安裝／升級流程 › plugin 安裝／升級、`auto-session.md` § 依安裝方式的 skill 呼叫字串。**beta 不提供 plugin**：marketplace 只上架穩定版，`6.0.0-beta.N` 照舊用 zip 手動安裝；plugin 相關條文是 v6 正式版上架後的規格（D443）。另修 plugin 安裝下會壞的讀取路徑（`auto-session.md` 寫死的 `ct-exec/SKILL.md`、ct-insights 預篩腳本）、`tower-config.md` 2 處連結層級；8 個 `agents/openai.yaml` 補 plugin 寫法。沒有新命令或新設定；從 beta.4 升級只換 skill 檔案，不需改設定或工單。方法論契約仍 `ct-methodology-adapter/v1`、`ct-adapter-pstack` 仍 0.2.4；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.5]`。BAT 介面同 v6.0.0-pre.1 |
| v6.0.0-beta.6 | 2026-10-30（**Beta**：只打包、不安裝；與穩定版 5.14.2 並行、不取代，D364） | Beta（移植穩定版 5.14.1、5.14.2，並讓方法論 adapter 偵測得到 plugin 安裝的方法論 skill，T0365／D459；同批移植的規則穩定版 5.14.1／5.14.2 也有）：方法論契約 `methodology-adapters.md` 新 § 描述檔格式 › probe 怎麼解析 skill 根目錄（唯一權威：依列出順序第一個成功的 probe 決定 skill 根目錄與版本、手動優先；`kind: plugin` 的安裝根目錄；probe 新增選填子欄位 `skill_root`；`required_files`／相對 `version_marker.file`／routing `reference` 相對於 skill 根目錄；只讀），§ 降級 新列（probe 全部失敗但可用 skill 清單裡有該方法論的 skill → 本 session 提示一次）；`adapters/bmad.yaml` 加 `guide-claude-plugin`、`guide-codex-plugin` 兩個 probe（排在 `guide-skill` 之後）；`validate-adapter.py` M8 檢查 `skill_root`；`ct-adapter-pstack` `adapter_version` 0.2.5（Claude probe 考慮 `CLAUDE_CODE_PLUGIN_CACHE_DIR`、`pinned_ref` 對齊 0.9.103）。5.14.1／5.14.2 移植：本檔 § plugin 安裝／升級 加 `bmad-guide@control-tower`、〈Codex 搭配 BAT 派工：依 BAT 版本〉；`auto-session.md` § 依安裝方式的 skill 呼叫字串 依 BAT 版本（`>= 0.7.2-pre.1`）、§ 依賴的 BAT 基礎設施 加一列、塔台端範本 `<工單 ID>`；`data-layer-architecture.md` § 寫入規則 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 補記；`mono-repo-patterns.md`、`multi-tower-protocol.md` 專案上下文改 `AGENTS.md` 說法；`work-order-system.md` § 工單 ID 格式 範例更正。**beta 不提供 plugin**（D443）：`6.0.0-beta.N` 照舊用 zip 手動安裝；bmad-guide 不跟 CT 版號，beta 使用者可從穩定 marketplace 只裝 `bmad-guide`。沒有新命令或新設定；從 beta.5 升級只換 skill 檔案，不需改設定或工單。方法論契約仍 `ct-methodology-adapter/v1`（頂層欄位不變）；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.6]`。BAT 介面同 v6.0.0-pre.1；Codex 用 plugin 又要接 BAT 派工需 BAT `>= 0.7.2-pre.1` |
| v6.0.0-beta.7 | 2026-10-30（**Beta**：只打包、不安裝；與穩定版 5.14.3 並行、不取代，D364） | Beta（移植穩定版 5.14.3，T0371／D471；同一份文件穩定版 5.14.3 也有）：「一個塔台、多個巢狀的獨立 repo」配置——`mono-repo-patterns.md` 新增 § 巢狀的獨立 repo（唯一權威）：上層 `git init`＋`.gitignore` 排除子 repo、工單集中在上層、`repo` 填上層目錄名、`project` 填子 repo、`affects_files` 從上層寫、Worker 在上層執行、產品用 `git -C <子 repo> commit --only <去掉前綴的路徑>`、回報區各記子 repo SHA；限制（不能 `isolation: worktree`、C-0 只驗上層、路徑前綴轉換、新目錄第一次派工的資料夾信任確認）、何時改用每個 repo 一個塔台、已寫在子 repo 的舊工單怎麼處理，附實機驗證結果（驗證版本是穩定版 CT 5.14.2＋BAT 0.7.2-pre.1，beta 規則相同）。`multi-tower-protocol.md` 判斷表加一列、`work-order-template.md`（目標子專案、`affects_files`、`repo`、`isolation` 不能用）、`onboarding.md`、`control-tower/SKILL.md` 路由指回新節。方法論契約仍 `ct-methodology-adapter/v1`、**契約不變**；`ct-adapter-pstack` 內容不變（`adapter_version` 0.2.5）。沒有新命令或新設定；從 beta.6 升級只換 skill 檔案。落點檢查、commit 規則、BAT 介面、派工命令不變；面板一鍵派工對巢狀 repo 配置未實機驗證；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.7]`。BAT 介面同 v6.0.0-pre.1 |
| v6.0.0-beta.8 | 2026-10-30（**Beta**：只打包、不安裝；與穩定版 5.14.4 並行、不取代，D364） | Beta（移植穩定版 5.14.4，並讓方法論 adapter 的 probe 依 runtime 分開，T0377／D480；移植的規則穩定版 5.14.4 也有）：方法論契約 `methodology-adapters.md` probe 新增選填子欄位 `runtime`（`claude-code`／`codex`，須在 `runtimes` 內；沒寫 = 所有 runtime 適用），§ 描述檔格式 › probe 怎麼解析 skill 根目錄 第 1 點改成先試本 runtime 的 probe（含沒寫 `runtime` 的，依列出順序）、另一個 runtime 的只當讀檔來源並註明一次，「手動優先」限同一個 runtime 內；第 3 點 Claude plugin 清單只有一處 `${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}`（實機驗證）；`validate-adapter.py` M8 檢查 `runtime` 的值域與是否在 `runtimes` 內，新增測試樣本。`adapters/bmad.yaml` `adapter_version` 0.2.1：`guide-skill` 拆成 `guide-skill-claude`、`guide-skill-codex`（`~/.agents/skills/` 歸 Codex），四個 probe 都標 `runtime`，`guide-claude-plugin` 刪掉第 2 個 search；`ct-adapter-pstack` `adapter_version` 0.2.6（同樣依 runtime 分開、`skills-only` 拆成兩個、刪掉第 2 個 Claude search）。5.14.4 移植：`data-layer-architecture.md` § 路徑解析 與 § 寫入規則 的 Claude plugin 路徑改成單一路徑（原「兩處都算」例外刪除），`enhancement-integration.md` § Level 2 › 偵測入口 第 3 點改成依 runtime。**契約仍 `ct-methodology-adapter/v1`**（新增選填子欄位，頂層欄位不變；沒寫 `runtime` 的舊 adapter 行為不變）。沒有新命令或新設定；從 beta.7 升級只換 skill 檔案（用 pstack 的換 `ct-adapter-pstack`）。新的搜尋順序本身未實機驗證；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.8]`。BAT 介面同 v6.0.0-pre.1 |
| v6.0.0-beta.9 | 2026-11-01（**Beta**：只打包、不安裝；與穩定版 5.15.0 並行、不取代，D364） | Beta（移植穩定版 5.15.0，T0387／D500；移植的規則穩定版 5.15.0 也有，條文相同、只差版本標記）：yolo Worker 一批多題只叫醒塔台一次——`yolo-mode.md` § Worker 向塔台提問（唯一權威）§ Worker 端 3-A 第 1、2 步：N ≥ 2 時第 1～N-1 題 `--ask --no-pty-write`（不帶 `--submit`，兩者互斥）、有退回的題加 `通道` 標記並 commit，最後送第 N 題 `--ask --submit`；第 N 題退回才加標記、commit、送一則一般 `提問`（緊接著做）。§ BAT 通道 寫明依賴「`--ask --no-pty-write` 只做 UI 通知、不寫塔台 PTY」，BAT 已確認，BAT `>= 0.7.2-pre.4` 起列為正式契約（`>= 0.7.0-pre.7` 起就是這個行為），`ask: NOTIFY_STEP` 可選用、不得依賴。既有問題一併修正：3-A 第 3 步多題等待租約逐題計算（每次逾時 `min(45, floor(90 / K))` 秒、優先同時等，最多 8 個）；§ 斷點 A 改以通知字串結尾判讀，題數一律以列表與工單標記為準。§ 塔台端 第 1 點：重複通知以 `bat_list_questions` 一次＋工單 grep 一次判斷，沒有新題就一行結束；第 2 點：已升級給使用者、還在等回答的題在 YOLO 歷程寫等待條目，之後不再重出 `⏸ YOLO PAUSED`。§ BAT / Worker 版本相容 加兩列（版本說法用 beta 的）、§ 迴歸測試 T9 加情境；`ct-exec/SKILL.md` § Questions For Tower 與 `control-tower/SKILL.md` 摘要同步。方法論契約仍 `ct-methodology-adapter/v1`、**契約不變**；`bmad.yaml` 0.2.1、`ct-adapter-pstack` 0.2.6 內容不變。沒有新命令、新設定或新欄位；從 beta.8 升級只換 skill 檔案。新流程在新 session 的實機驗證尚未做；已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.9]`。BAT 介面同 v6.0.0-pre.1 |
| v6.0.0-beta.10 | 2026-11-01（**Beta**：只打包、不安裝；與穩定版 5.15.0 並行、不取代，D364） | Beta（session 用量統計、session 證據、外部增強外掛治理，T0393～T0396／D518、D523；本版改動穩定版 5.15.0 沒有）：ct-insights 新命令 `*insights sessions`（`scripts/ct-session-stats.py`＋`pricing.json`，只讀、標準函式庫；權威 `ct-insights/references/analysis-rules.md` § Session 用量統計）；工單選填欄位 `session_ids`（Worker 收尾寫、`ct-done` 補救時寫、塔台收單補記）、塔台啟動記 session id（`memory-protocol.md`）、收單補記與收單快照 `_ct-workorders/_insights/session-stats/`（`work-order-system.md`、`data-layer-architecture.md`）；`auto-session.md` § 偵測條件 加唯一寫值例外 `CLAUDE_CODE_SESSION_ID`、新 § Claude 啟動參數不得放 `--settings`；`ct-evolve --facts-from` 讀候選事實 `ct-session-fact/0.1` 接既有置信度表（§ Session Evidence）。`enhancement-integration.md` 改寫成「外部增強外掛治理」：ECC Level 1 退場（13 項相容功能對照），mem0 Level 3 保留但須在本地規則記錄使用者層例外才啟用（§ Level 3 › 啟用條件）。`data-layer-architecture.md` § 寫入規則：Codex 掃描器已證實會遞迴（Q2）、手動安裝 skill 的移除由使用者逐項決定（Q3）；`yolo-mode.md` helper 輸出前導空白與 `bat_list_questions` 找回 id。方法論契約仍 `ct-methodology-adapter/v1`、**契約不變**；`bmad.yaml` 只改註解（0.2.1）、`ct-adapter-pstack` 內容不變（0.2.6）。新命令 1、新選填欄位 1，沒有新設定；從 beta.9 升級只換 skill 檔案。已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.10]`。BAT 介面同 v6.0.0-pre.1（收單補記另需 BAT `>= 0.7.1-pre.1`＋BAT MCP，沒有就跳過） |
| v6.0.0-beta.11 | 2026-11-03（**Beta**：只打包、不安裝；與穩定版 5.15.0 並行、不取代，D364） | Beta（執行中補充工單 PLAN-005 S1＋小項，T0405、T0399、T0407、T0409／D545、D546、D551；本版改動穩定版 5.15.0 沒有）：`work-order-system.md` § 執行中補充工單（塔台在 Worker `IN_PROGRESS` 時寫 `## 塔台補充（執行中 #N）`，不是 Renew、不加 `Renew 次數`、可見性不依賴 commit；收單核對讀入紀錄，Claude Code Worker 透過檔案變更提示讀到晚到段落時照常認定）；`ct-exec/SKILL.md` § Tower Addenda Check（驗證前、產品 commit 前、寫回報前三個節點各 grep 一次段落標題，只讀開工後新增的補充段；沒有新段落不輸出、不記錄）；`ct-done` 寫回報前同一檢查；`cross-project-coordination.md` § 通知自己的 Worker 重讀工單（選用，只限 Claude Code，訊息只放指引）；`yolo-mode.md` YOLO 歷程 `[補充]` 類型與 BAT `>= 0.7.3-pre.8` 待送通知補註；`auto-session.md` § Claude 啟動參數不得放 `--settings` 第二個理由；`ct-help` § Session Usage And Evidence。方法論契約仍 `ct-methodology-adapter/v1`、**契約不變**；`bmad.yaml` 只改版號註解（0.2.1）、`ct-adapter-pstack` 內容不變（0.2.6）。沒有新設定、新命令或新的 frontmatter 欄位；從 beta.10 升級只換 skill 檔案。已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.11]`。BAT 介面同 v6.0.0-pre.1，沒有新的最低版本 |
| v6.0.0-beta.12 | 2026-11-05（**Beta**：只打包、不安裝；與穩定版 5.15.0 並行、不取代，D364） | Beta（工具清單建議 PLAN-006，T0419～T0424／D577～D582；本版改動穩定版 5.15.0 沒有）：ct-insights 新命令 `*insights tools`（`ct-session-stats.py --tools`，腳本 0.2.0；只讀、只出建議、不改設定；權威 `ct-insights/references/analysis-rules.md` § 工具清單建議）：依 session 紀錄的附件找出已載入但少用或沒用的 skill、plugin、MCP server、agent 類型與內建工具，依工單類型分組，各項標層級（專案、使用者、claude.ai 帳號）與設定鍵，核心內建工具（`TOOLS_CORE_BUILTIN`）一律 `keep`，內建工具使用率的分子只計同時在載入分母內的 session；`skills_invoked` 計入使用者 slash command、新增 `agents_invoked`、快照 `ct-session-stats-snapshot/0.2`（`0.1` 照常可讀）；`control-tower/SKILL.md` 命令表、`ct-help`、`data-layer-architecture.md` 同步摘要。本檔 § 發布流程 第 3 步加打包檢查：`SKILL.md` 的 `description` 不得含 `<`、`>`（BUG-003）。方法論契約仍 `ct-methodology-adapter/v1`、**契約不變**；`bmad.yaml` 只改版號註解（0.2.1）、`ct-adapter-pstack` 內容不變（0.2.6）。新命令 1，沒有新設定或新的 frontmatter 欄位；從 beta.11 升級只換 skill 檔案。已知未驗見 `docs/CHANGELOG.md` `[6.0.0-beta.12]`。BAT 介面同 v6.0.0-pre.1，沒有新的最低版本 |
| v6.0.0-rc.1 | 2026-11-05（**RC**（正式版候選）：只打包、不安裝；與穩定版 5.15.0 並行、不取代，D586） | RC（正式版候選；beta 回饋期結束，功能凍結、只修錯，T0427、T0428／D586、D587）：`ct-exec/SKILL.md` § Phase 3 的塔台補充檢查（節點 1）改成驗證段落第 1 步、§ Tower Addenda Check 節點清單改指「Phase 3 step 1」；`ct-done/SKILL.md` 第 6 步的節點 3 檢查改成先寫；`ct-insights/references/analysis-rules.md` § 工具清單建議 › 報告格式 的 JSON `items[]` 欄位補 `use_rate`、`saving_max_chars`、`plugin_verdict`（腳本不變）。現行標示 Beta 改 RC；「beta 不提供 plugin」的現行規則句改成「預發行版（beta、rc）不提供 plugin」（本檔、`auto-session.md`、`data-layer-architecture.md`；規則不變）。方法論契約仍 `ct-methodology-adapter/v1`、**契約不變**；`bmad.yaml` 只改註解（0.2.1）、`ct-adapter-pstack` 內容不變（0.2.6）。沒有新命令、新設定或新的 frontmatter 欄位；從 beta.12 升級只換 skill 檔案。已知未驗見 `docs/CHANGELOG.md` `[6.0.0-rc.1]`（41 項）。BAT 介面同 v6.0.0-pre.1，沒有新的最低版本 |
| v6.0.0 | 2026-11-07（**正式版**：取代 5.15.0 成為穩定版，D666） | MAJOR 正式版（v6 系列：方法論轉接、BUG／PLAN／EXP 預設開啟、session 用量統計與 `session_ids`、執行中補充工單、工具清單建議，各版內容見 `[6.0.0-pre.1]`～`[6.0.0-rc.1]`；T0464／D666）：相對 rc.1 沒有功能或規則變更，只改版號與標示（RC → 正式版）；plugin 6.0.0 起上架 marketplace（預發行版仍不提供）；方法論契約仍 `ct-methodology-adapter/v1`，內建 `bmad.yaml` 0.2.1、`ct-adapter-pstack` 0.2.6。BAT 最低版本不變（`>= 0.7.0-pre.7`） |

> v4.x ~ v5.0.2 各列以 `docs/CHANGELOG.md` 對應版本段為準。
>
> ¹ v5.0.3 精簡時**刪除、未搬移**至 reference 的機制（D010 確認刪除，**不恢復**）：
> `*sync` 版號一致性驗證第 11 步、遷移偵測第 9 項、JetBrains Gateway Dev Container 偵測、
> 粒度分析卡、`*help roles`、PLAN-033 State Hygiene、BUG VERIFY 決策流。

## 相容性注意

- 舊版文件若提到 frontmatter `version:`，視為 deprecated pattern。修訂時改為 body 註解。
- Worker skill 版本可獨立於 Tower skill，但 BAT/YOLO 相關變更要確認 `ct-exec`、`ct-done` 仍讀取 `CT_MODE`、`CT_INTERACTIVE` 和 `BAT_TOWER_TERMINAL_ID`。
- 若新版 Tower 派發到舊版 Worker，應以明確 `PARTIAL` / `BLOCKED` 或升級提示回報，不要宣稱 YOLO 自動回報已生效。
