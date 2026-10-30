---
title: 安裝
description: 在 Claude Code 或 Codex 安裝與升級 CT 的 8 個 skill：zip 手動安裝（備份、暫存複驗、替換、逐檔比對）與 plugin marketplace 安裝、回退方式，以及在 claude.ai 能用到什麼程度。
---

<script setup>
import { useData } from 'vitepress'
import bmadGuide from './data/bmad-guide.json'

const { theme } = useData()
const mkt = theme.value.marketplaceRepo
</script>

# 安裝

CT 是 8 個 skill，裝在你電腦上 Agent CLI 的 skill 目錄裡：可以下載 zip 手動安裝，v5.14.0 起也可以用 plugin marketplace 安裝。目前版本 <VersionBadge />。 {.ct-lead}

## 你需要什麼 {#requirements}

- **一個 Agent CLI**：Claude Code 或 Codex，擇一或兩個都裝。塔台和 Worker 可以用同一種，也可以不同。
- **一個 git repo**：工單、塔台狀態與決策日誌都寫在專案的 `_ct-workorders/` 底下，和程式碼一起進版控。
- **可選：BAT**。有 <BatLink>Better Agent Terminal</BatLink> 時，塔台可以直接開 Worker 分頁、Worker 做完自動通知塔台；沒有也能用，塔台改給你剪貼簿或一行指令。
- **可選：BMad Guide Skill**。`bmad-guide` 是 BMad-Method 的互動式學習指南，有兩種用法：當 CT 的外部依賴，塔台偵測到它就啟用 Level 2，依專案階段查出該走哪一套 BMad 流程；也可以單獨裝，當作學 BMad-Method 的指南。見 [BMad Guide Skill](/guide/bmad-guide)。
- **可選：其他增強**。ECC、mem0，偵測到才啟用，見[功能總覽的能力等級](/features#levels)。

## 兩種安裝方式 {#methods}

| | zip 手動安裝 | plugin marketplace（v5.14.0 起） |
|---|---|---|
| 適用 | Claude Code、Codex；**Codex 搭配 BAT 派工只能用這種** | Claude Code；不用 BAT 派工的 Codex |
| 怎麼裝 | 下載下面的 zip，照[第一次安裝](#first-install) | 一行 `marketplace add` 再裝 plugin，見[用 plugin marketplace 安裝](#plugin) |
| 怎麼更新 | 每次照[升級：四步](#upgrade)手動替換 | 交給 Agent CLI（Claude Code 要先開 auto-update；Codex 啟動時自動升級） |
| 呼叫寫法 | Claude Code `/ct-exec`；Codex `$ct-exec` | Claude Code `/ct-exec`（完整寫法 `/ct:ct-exec`）；Codex `$ct:ct-exec` |
| beta | 可以 | 不上架 |

同一個 Agent 上只留一種：兩種並存時手動安裝那份會蓋過 plugin 版，而且看不出差別。

<CtDownload />

## 發行物長什麼樣子 {#layout}

| 發行物 | 內容 |
|---|---|
| `BMad-Control-Tower-v<版號>/` | `skills/` 底下 8 個 skill 目錄，加上 `docs/`（安裝與使用指南、`CHANGELOG.md` 等） |
| `BMad-Control-Tower-v<版號>.zip` | 根層直接是 8 個 skill 目錄，不含 `docs/` |
| `BMad-Control-Tower-v<版號>-skills/`（v5.12.4 起） | 8 個單一 skill zip `<skill>-v<版號>.zip`，每個 zip 根層只有一個資料夾 `<skill>/`。給 claude.ai 上傳用（見 [claude.ai](#claude-ai-zip)），不用來安裝到 `~/.claude/skills/` |
| `bmad-guide-v<版號>.zip` | BMad Guide Skill，只有一個 skill。最上層是帶版號的資料夾 `bmad-guide-v<版號>/`，裡面是 `SKILL.md` 和 `references/`。版號跟 BMad-Method 走，不跟 CT |

8 個 skill 是 `control-tower`、`ct-exec`、`ct-done`、`ct-status`、`ct-evolve`、`ct-help`、`ct-insights`、`ct-fieldguide`。**全部都要裝，而且塔台與 Worker 必須同一批升級**：塔台與 Worker 之間的協定會隨版本調整，混用新舊版時兩邊對不上。例如 v4.3 起模式由塔台在派工時以旗標傳給 Worker，舊塔台配新 Worker 時 yolo 就會失效、退回 ask。

## 安裝位置 {#paths}

| Agent | 安裝路徑 | 備份放哪裡 | 指令前綴 |
|---|---|---|---|
| Claude Code（zip 手動安裝） | `~/.claude/skills/<skill>/` | `~/.claude/skill-backups/` | `/`（例：`/ct-exec T0001`） |
| Codex（zip 手動安裝） | `~/.codex/skills/<skill>/` | `~/.codex/skill-backups/` | `$`（例：`$ct-exec T0001`） |
| Claude Code（plugin） | `~/.claude/plugins/` 底下（設了 `CLAUDE_CONFIG_DIR` 或 `CLAUDE_CODE_PLUGIN_CACHE_DIR` 時跟著搬，只算一處），由 Claude Code 管理 | 不備份 | `/`（例：`/ct-exec T0001`，完整寫法 `/ct:ct-exec T0001`） |
| Codex（plugin） | `~/.codex/plugins/` 底下，由 Codex 管理 | 不備份 | `$ct:`（例：`$ct:ct-exec T0001`） |

兩端是**各自獨立的安裝**：升級其中一端不會更新另一端，請分別確認版號。plugin 的安裝目錄只能用 plugin 指令安裝、更新或移除，不要手動複製或修改裡面的檔案。

BMad Guide 裝在同一層：Claude Code 是 `~/.claude/skills/bmad-guide/`，Codex 是 `~/.codex/skills/bmad-guide/`，見[安裝 BMad Guide Skill](#bmad-guide)。

::: warning 備份不要放在 skills/ 底下
`~/.claude/skills/` 第一層的每個子目錄都會被 skill 掃描器當成一個 skill 註冊。一份根層帶 `SKILL.md` 的備份會以舊版的說明進入路由候選，之後可能**靜默地**載入舊版、答出已經被新版推翻的內容。所以備份、暫存目錄、`.bak` 這類東西一律放在 `skills/` 之外。Codex 端的掃描器行為未經實測，規則比照辦理。
:::

## 第一次安裝（zip 手動安裝） {#first-install}

用 plugin 安裝的，見[用 plugin marketplace 安裝](#plugin)。

1. 取得發行物並解壓縮。
2. 把 8 個 skill 目錄複製到上表的安裝路徑，每個 skill 一個目錄（例如 `~/.claude/skills/control-tower/`）。不要帶 `.` 開頭的隱藏目錄。
3. 確認版號（見下一節），8 個都要是同一版。
4. **開一個新的 session**，在專案目錄輸入 `/control-tower`（Codex：`$control-tower`）。塔台會先顯示狀態面板，第一次使用時會建立 `_ct-workorders/`。

第一次安裝沒有東西要備份，下面升級流程的 Step 1 會自動略過還沒安裝的 skill；照升級流程跑一遍也可以。

## 確認現行版號 {#check-version}

版號寫在每個 `SKILL.md` 正文的第一個註解（例如 `<!-- control-tower-version: 5.14.4 -->`），frontmatter 不放版號。下面是 zip 手動安裝的查法；用 plugin 安裝的看 `plugin list --json`，見[確認 plugin 版號](#plugin-version)。

::: code-group

```bash [Claude Code]
grep -h -o "[a-z-]*-version: [0-9.]*" ~/.claude/skills/{control-tower,ct-*}/SKILL.md
```

```bash [Codex]
grep -h -o "[a-z-]*-version: [0-9.]*" ~/.codex/skills/{control-tower,ct-*}/SKILL.md
```

:::

8 行的版號應該一致。v5.0.2 以前的舊版把版號放在 frontmatter 的 `version:`。

## 升級：四步（zip 手動安裝） {#upgrade}

升級的原則是**任何一步失敗都不會讓你少掉一個能用的 skill**：先備份並確認備份完整，再把新版複製到暫存區驗證，驗證過了才替換，替換後逐檔比對。

1. **查版號**：用上一節的指令記下目前的版號，後面命名備份目錄要用。
2. **備份**：把目前的 8 個 skill 複製到 `skill-backups/`（**不放在 `skills/` 底下**），時間戳一律取自系統、不要手打。任何一個 skill 備份失敗就停；全部備份完，逐檔確認備份和現行安裝品相同，不同也停。這時已安裝的目錄完全沒動。
3. **先複製到暫存區驗證，再替換**：把新版複製到 `skills/` 之外的暫存目錄，逐檔確認和來源一致後，才一個一個替換。替換時先把舊目錄**移**到暫存目錄，再把新目錄移進來，**不先刪除**已安裝的目錄。
4. **逐檔比對 IDENTICAL**：替換完，用 `diff -r` 或 SHA-256 比對來源和安裝品，8 個都要 IDENTICAL 才算完成；任何一個不一致就視為安裝失敗，照下方回退。最後確認 `skills/` 底下沒有 `_backup-*`、`_staging-*` 或隱藏目錄。

::: tip 新版從下一個 session 才生效
正在跑的 session 已經載入舊版的 skill。升級完要開新的 session，新版才會生效。
:::

::: details 完整指令（bash，以 Claude Code 為例；摘自 CT 安裝與使用指南 § 4.1）

```bash
NEW=BMad-Control-Tower-v<新版號>/skills # 或 zip 解壓後的根目錄
OLD=<目前的版號>                         # 第 1 步查得
VER=<新版號>                             # 暫存目錄命名用
SKILLS="control-tower ct-done ct-evolve ct-exec ct-fieldguide ct-help ct-insights ct-status"

# Step 1：備份現行安裝品（timestamp 必須取自系統，不得手打）
#   任一 skill 備份失敗就停止；全部備份完成後逐檔複驗備份與現行安裝品相同，不通過也停止 —— 兩者都不得進 Step 2
TS=$(date "+%Y%m%d-%H%M%S")
BK=~/.claude/skill-backups/_backup-ct-v$OLD-$TS
ct_backup() (   # 用法：ct_backup <備份目錄>；在子 shell 執行，失敗時印 STOP 並回傳非 0
  bk=$1
  mkdir -p "$bk" || { echo "STOP: 備份目錄建立失敗，已安裝目錄未變動"; exit 1; }
  for s in $SKILLS; do   # (1) 逐一備份；尚未安裝的 skill（首次安裝）略過
    [ -e ~/.claude/skills/$s ] || { echo "$s 尚未安裝，略過備份"; continue; }
    cp -r ~/.claude/skills/$s "$bk/$s" || { echo "STOP: $s 備份失敗，已安裝目錄未變動"; exit 1; }
  done
  for s in $SKILLS; do   # (2) 進 Step 2 前逐檔複驗：每個備份都必須與現行安裝品相同
    [ -e ~/.claude/skills/$s ] || continue
    diff -r ~/.claude/skills/$s "$bk/$s" >/dev/null || { echo "STOP: $s 備份與現行安裝品不同，已安裝目錄未變動"; exit 1; }
  done
)
if ct_backup "$BK"; then STEP1=OK; echo "Step 1 OK"; else STEP1=STOP; echo "Step 1 STOP —— 不進 Step 2，依訊息處理"; fi

# Step 2：安裝 —— 先複製到 skills/ 之外的暫存目錄、複驗全部 IDENTICAL 後才逐一替換；任一步失敗就停止
#   不先刪除已安裝目錄（舊目錄移到暫存目錄，不刪除）；不帶 . 開頭的隱藏目錄
#   Windows／Git Bash：Windows Python 讀不到 POSIX 形式的磁碟路徑，傳給它的路徑先經 wp（cygpath -w）轉換
wp() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s\n' "$1"; fi; }
ct_swap() (   # 用法：ct_swap <來源根目錄> <暫存目錄>；在子 shell 執行，失敗時印 STOP 並回傳非 0
  src=$1; st=$2
  mkdir -p "$st/new" "$st/old" || exit 1
  for s in $SKILLS; do   # (1) 全部複製到暫存並複驗 —— 這一階段完全不碰已安裝目錄
    python -c "import shutil,sys; shutil.copytree(sys.argv[1], sys.argv[2], ignore=shutil.ignore_patterns('.*'))" "$(wp "$src/$s")" "$(wp "$st/new/$s")" &&
      diff -r -x '.*' "$src/$s" "$st/new/$s" >/dev/null ||
      { echo "STOP: $s 複製或暫存複驗失敗，已安裝目錄未變動"; exit 1; }
  done
  for s in $SKILLS; do   # (2) 逐一替換 —— 舊目錄移到暫存目錄，再移入已複驗的新目錄
    if [ -e ~/.claude/skills/$s ]; then
      mv ~/.claude/skills/$s "$st/old/$s" || { echo "STOP: $s 舊目錄移出失敗"; exit 1; }
    fi
    mv "$st/new/$s" ~/.claude/skills/$s ||
      { mv "$st/old/$s" ~/.claude/skills/$s; echo "STOP: $s 移入失敗，已放回舊目錄；先前已替換的 skill 依「回退」復原"; exit 1; }
  done
)
ST=~/.claude/skill-backups/_staging-ct-v$VER-$TS     # 與備份同層，不在 skills/ 之下
if [ "$STEP1" = OK ]; then
  if ct_swap "$NEW" "$ST"; then STEP2=OK; echo "Step 2 OK"; else STEP2=STOP; echo "Step 2 STOP —— 依訊息處理，不要往下執行"; fi
else
  STEP2=SKIP; echo "Step 2 未執行：Step 1 未通過"
fi

# Step 3：逐檔複驗 —— 必須全部 IDENTICAL，任一不一致即視為安裝失敗、回退
#   Step 1 未通過時沒有替換任何東西，不做複驗也不回退
if [ "$STEP2" != SKIP ]; then
  OK=1
  for s in $SKILLS; do
    diff -r -x '.*' "$NEW/$s" ~/.claude/skills/$s >/dev/null && echo "$s IDENTICAL" || { echo "$s MISMATCH"; OK=0; }
  done
  [ $OK = 1 ] && rm -rf "$ST"    # 全部 IDENTICAL 才刪暫存目錄（裡面只剩移出的舊目錄，Step 1 已有備份）
fi

# 附帶檢查：skills/ 下不得出現備份、暫存或隱藏目錄
ls ~/.claude/skills | grep -E '^_(backup|staging)'   # 須無輸出
find ~/.claude/skills -name '.sonar'                 # 須無輸出
```

PowerShell 取時間戳與建立備份目錄：

```powershell
$TS = Get-Date -Format "yyyyMMdd-HHmmss"
$BK = "$env:USERPROFILE\.claude\skill-backups\_backup-ct-v<目前的版號>-$TS"
New-Item -ItemType Directory -Path $BK -Force
```

Codex 端把 `~/.claude/skills` 換成 `~/.codex/skills`、`~/.claude/skill-backups` 換成 `~/.codex/skill-backups` 即可。
:::

升級完記下四件事：備份的完整路徑、每個 skill 的比對結果、回退方式、從下一個 session 生效。

## 回退 {#rollback}

用同一套「暫存驗證再替換」的流程，把備份裝回去，一樣不先刪除已安裝的目錄。沿用上面同一個 shell 裡的 `SKILLS`、`BK`、`wp`、`ct_swap`：

```bash
RB=~/.claude/skill-backups/_staging-rollback-$(date "+%Y%m%d-%H%M%S")
ct_swap "$BK" "$RB" && echo "回退 OK" || echo "回退 STOP —— 依訊息處理"
OK=1
for s in $SKILLS; do
  diff -r -x '.*' "$BK/$s" ~/.claude/skills/$s >/dev/null && echo "$s IDENTICAL" || { echo "$s MISMATCH"; OK=0; }
done
[ $OK = 1 ] && rm -rf "$RB"
```

## 用 plugin marketplace 安裝（v5.14.0 起） {#plugin}

v5.14.0 起，CT 也可以用 Claude Code 與 Codex 的 plugin marketplace 安裝，之後的更新交給 Agent CLI。zip 手動安裝照舊支援，同一個 Agent 上兩種擇一。

| 項目 | 內容 |
|---|---|
| marketplace | `control-tower`，放在本站的公開 repo <code>{{ mkt }}</code> |
| plugin | `ct`：CT 的 8 個 skill，一定一起裝；`ct-guide`：CT Guide，可不裝；`bmad-guide`：[BMad Guide Skill](/guide/bmad-guide)，可不裝 |
| 版號 | `ct` 的版號 = CT 版號，`ct-guide` 的版號 = CT Guide 版號；`bmad-guide` 的版號跟 BMad-Method 走（例如 6.12.4），不跟 CT |
| beta | 不上架，beta 照舊用 zip 手動安裝 |

::: warning 從 zip 手動安裝改用 plugin：先移除手動安裝
同名的手動安裝還留在 `skills/` 裡時，`/ct-exec`、`$ct-exec` 都會用手動那份，plugin 版不生效，而且看不出差別。所以先照[升級：四步](#upgrade)的 Step 1 把 8 個 skill（有裝 CT Guide、BMad Guide 的話加上 `control-tower-guide`、`bmad-guide`）備份到 `skill-backups/`、逐檔確認備份完整，再把它們從 `~/.claude/skills/`（Codex：`~/.codex/skills/`）**移**到備份目錄，不要直接刪除。之後才裝 plugin。
:::

::: warning Codex 搭配 BAT 派工：看 BAT 版本
BAT `0.7.2-pre.1` 起會看 Codex 那一端怎麼裝：有手動安裝就送 `$ct-exec T####`，只裝 plugin 就送 `$ct:ct-exec T####`，所以 zip 和 plugin 都能接 BAT 派工（CT v5.14.2 起；這條路徑的端到端派工還沒實機驗證過）。兩種都裝時 BAT 送手動那份，所以從 zip 改用 plugin 照樣要先移除手動安裝。更舊的 BAT 一律送 `$ct-exec`，plugin 版在 Codex 一定帶前綴、叫不到，接這種 BAT 派工的 Codex 就繼續用 zip 手動安裝，或先把 BAT 升級。Claude Code 不受影響：plugin 版用不帶前綴的 `/ct-exec` 也叫得到。
:::

### Claude Code {#plugin-claude}

<div class="language-bash"><span class="lang">bash</span><pre><code>claude plugin marketplace add {{ mkt }}
claude plugin install ct@control-tower
claude plugin install ct-guide@control-tower      # 可選：CT Guide
claude plugin install bmad-guide@control-tower    # 可選：BMad Guide</code></pre></div>

- 開新 session 後照常用 `/control-tower`、`/ct-exec T0001`、`/bmad-guide`。要確定叫到的是 plugin 版，用完整寫法 `/ct:ct-exec T0001`、`/bmad-guide:bmad-guide`。
- **自動更新**：第三方 marketplace 預設關閉。在 session 裡輸入 `/plugin`，到 Marketplaces 對 `control-tower` 開啟 auto-update。
- **手動更新**：`claude plugin marketplace update control-tower`，再 `claude plugin update ct@control-tower`（有裝 CT Guide、BMad Guide 再 `claude plugin update ct-guide@control-tower`、`claude plugin update bmad-guide@control-tower`）。Claude Code 看 plugin 的版號判斷有沒有新版。
- 新版從下一個 session 生效。

### Codex {#plugin-codex}

<div class="language-bash"><span class="lang">bash</span><pre><code>codex plugin marketplace add {{ mkt }}
codex plugin add ct@control-tower
codex plugin add ct-guide@control-tower           # 可選：CT Guide
codex plugin add bmad-guide@control-tower         # 可選：BMad Guide</code></pre></div>

- 呼叫一律帶前綴：`$ct:control-tower`、`$ct:ct-exec T0001`、`$ct-guide:control-tower-guide`、`$bmad-guide:bmad-guide`。不帶前綴的 `$ct-exec` 叫不到 plugin 版。
- 從 shell 帶參數啟動 Codex 時，用單引號包住（例如 `codex '$ct:ct-exec T0001'`），否則 bash 和 PowerShell 會把 `$ct` 當成變數。
- **自動更新**：Codex 每次啟動會自動升級 git 型的 marketplace。手動升級：`codex plugin marketplace upgrade control-tower`。
- 新版從下一個 session 生效。

### 確認 plugin 版號 {#plugin-version}

```bash
claude plugin list --json        # ct@control-tower 的 version
codex plugin list --json         # ct@control-tower 的 version
```

`version` 應該等於 CT 版號（目前 <VersionBadge />）。`ct-guide@control-tower` 等於 CT Guide 版號；`bmad-guide@control-tower` 等於 bmad-guide 的版號，也就是它所教的 BMad-Method 版號（目前 v{{ bmadGuide.version }}）。

### 移除與回退 {#plugin-rollback}

plugin 安裝不另做備份，回退就是用 plugin 指令移除：`claude plugin uninstall ct@control-tower`、`codex plugin remove ct@control-tower`（`ct-guide`、`bmad-guide` 同樣寫法）。要回到 zip 手動安裝，照[回退](#rollback)把遷移前的備份裝回 `skills/`。plugin 的安裝目錄由 Agent CLI 管理，不要手動複製、修改或刪除裡面的檔案。

## 讓 CT Worker 代為安裝 {#worker-install}

塔台與 Worker 預設**不得**寫入 `~/.claude/skills/` 或 `~/.codex/skills/`。要讓 Worker 替你安裝，必須在**工單裡明文授權**，指名具體版本、具體 skill 與目標路徑；只指名 `~/.claude/skills/` 的工單不能拿來寫 `~/.codex/skills/`。Worker 不會自己認定已經取得授權，沒有授權就停下來回報。

plugin 安裝也一樣要授權，工單要指名 Agent（Claude Code 或 Codex）、plugin 與 marketplace（例如 `ct@control-tower`）；有授權也只能用 plugin 指令安裝，不會直接動 plugin 的安裝目錄。

## 用 Codex 當 Worker 或塔台 {#codex}

- zip 手動安裝時 skill 裝在 `~/.codex/skills/<skill>/`，指令前綴是 `$`：`$control-tower`、`$ct-exec T0001`。用 plugin 安裝時一律帶前綴：`$ct:control-tower`、`$ct:ct-exec T0001`（見 [plugin 安裝的 Codex 段](#plugin-codex)）。
- 在 BAT 裡，塔台派工用 `--agent default`，由 BAT 依你在 BAT 設定的預設 Agent 決定開 Claude Code 還是 Codex，也由 BAT 決定送 `/ct-exec`、`$ct-exec` 還是 `$ct:ct-exec`。想讓 Worker 用 Codex，改 BAT 的預設 Agent，不要把 `codex` 寫死在工單裡。BAT `>= 0.7.2-pre.1` 依 Codex 端的安裝方式送 `$ct-exec` 或 `$ct:ct-exec`，zip 和 plugin 都能接 BAT 派工；更舊的 BAT 只送不帶前綴的 `$ct-exec`，接它派工的 Codex 要用 zip 手動安裝（見[用 plugin marketplace 安裝](#plugin)）。
- 不在 BAT 裡時，用環境變數 `CT_AGENT_CMD=claude` 或 `CT_AGENT_CMD=codex` 指定；兩者都裝了又沒指定時，塔台不猜，改給你剪貼簿或文字提示。

如果你想在 `~/.codex/AGENTS.md` 放一段給 Codex 看的 BAT 派工說明，可以參考下面這段。它**是範例，不是權威定義**：派工指令以 `control-tower/references/auto-session.md` 為準，兩者不一致時照 reference 改這段，不要反過來。

````markdown
## BAT (BetterAgentTerminal) — Control Tower 派工（範例；權威為 control-tower/references/auto-session.md）

**塔台派發 Worker**（helper 優先用 `BAT_HELPER_DIR`）：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" \
  --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
  --cwd "<專案根目錄>" \
  --mode <yolo|ask|off|on> [--interactive|--no-interactive] \
  --agent default --skill <ct-exec|ct-done> --workorder <工單 ID> \
  [--wait-started 30000]
```

**Worker 通知塔台**（`--submit` 僅限 `CT_MODE=yolo`；`on` 不加，僅預填）：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-notify.mjs" \
  --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" [--submit] "<工單 ID> 完成"
```

- `<工單 ID>` 是完整工單 ID，等於工單 frontmatter 的 `id`：設了前綴就含前綴（例 `--workorder CP-T0113`、`CP-T0113 完成`），不能截成 `T` 加數字，否則 BAT 對不上 Worker 分頁、無法標成 Done（Worker 回報 v5.13.1 起；塔台派工範本 v5.14.1 起）
- 路徑用 Windows 形式；不要改成 POSIX 形式，Node 會誤判為相對路徑
- 塔台派工必要的環境變數：`BAT_SESSION=1`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`、`BAT_TERMINAL_ID`、`BAT_WORKSPACE_ID`
- `--workspace` 與 `--cwd` 都要傳，兩者修的是不同的事，不能互相取代
- bash 看不到 `BAT_*` 時，Windows 上用 PowerShell `Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object` 複查（只列名稱、不輸出值；`BAT_REMOTE_TOKEN` 只記「已設定」），不得直接判定為非 BAT
````

## 在 claude.ai 使用 {#claude-ai}

claude.ai 可以上傳自訂 skill，但 CT 的核心工作（讀寫工單檔、派工給 Worker、改程式碼、commit）都發生在你電腦上的專案 repo 裡。claude.ai 的程式碼執行環境是與你的電腦隔開的沙箱，碰不到你的 repo，所以能做的事不一樣：

| Skill | 在 claude.ai 對話中 | 建議 |
|---|---|---|
| CT Guide（`control-tower-guide`） | 可以用：概念教學、設計理由、比較說明。網頁版與桌面版會畫出可點擊的流程圖，手機 app 不會顯示圖表 | 推薦上傳 |
| `ct-help` | 可以用：指令與概念說明 | 可上傳 |
| `control-tower` 與其他 `ct-*` | 只能當諮詢：可以討論規則、草擬一張工單讓你下載。塔台狀態、工單目錄、派工、Worker 執行都無法運作 | 正式使用請裝到 Claude Code 或 Codex |

::: warning 未實測的兩件事
- **塔台在 claude.ai 遇到「沒有 repo」時會怎麼反應**：可能說明它需要本機 repo、無法運作，也可能在沙箱裡自己建一個 `_ct-workorders/`。**未實測**。
- **檔案會不會跨對話保留**：官方文件沒有說沙箱裡寫的檔案會保留到下一個對話，預期不會。**未實測**。就算塔台在某次對話裡建了工單檔，也不要當成它記得。
:::

### 事前準備 {#claude-ai-prepare}

1. **開啟程式碼執行**：skill 需要程式碼執行環境。個人帳號在設定的「Capabilities」裡開啟「Code execution and file creation」；組織帳號由管理員在組織設定開啟 skill 與程式碼執行。
2. **取得 skill 檔案**：見本頁上方的「取得方式」。目前版本：<VersionBadge />。

### 打包：一個 zip 只能放一個 skill {#claude-ai-zip}

claude.ai 一次只接受一個 skill 的 zip，而且 zip 的最上層必須是 skill 資料夾本身，資料夾名稱要和 `SKILL.md` 裡的 `name` 相同：

```
control-tower-guide.zip
└── control-tower-guide/
    ├── SKILL.md
    └── references/
```

- **v5.12.4 起直接用現成的單一 skill zip**：發行物另附 `BMad-Control-Tower-v<版號>-skills/`，裡面是 8 個 `<skill>-v<版號>.zip`，每個 zip 的根層是唯一資料夾 `<skill>/`，可以直接上傳。CT Guide 的 `control-tower-guide-v<版號>.zip` 根層也是唯一資料夾 `control-tower-guide/`，同樣可以直接上傳。
- **CT 的全量 zip（`BMad-Control-Tower-v<版號>.zip`）一次包含 8 個 skill，不能直接上傳**，會被拒絕。要自己打包的話，解壓後對每個 skill 資料夾各壓一個 zip（壓「資料夾本身」，不是資料夾裡的檔案）。
- 不論現成或自己壓，都可以用 `unzip -l <檔名>.zip` 檢查：每一行都應該以 `<skill 名稱>/` 開頭。

### 上傳 {#claude-ai-upload}

1. 開啟 claude.ai 的 **Customize › Skills**。
2. 按「+」→「Create skill」→「Upload a skill」，選擇 zip。
3. 上傳後確認該 skill 已開啟。
4. 更新版本時，上傳同名 skill 即可取代舊版。

介面名稱與路徑以 claude.ai 當下為準；這個功能還在 beta，畫面可能調整。

### 確認可以用 {#claude-ai-verify}

開新對話，輸入「用 Control Tower Guide 說明一張工單從建立到收單的流程，並畫一張圖」。回覆應該引用 Guide 的內容，網頁版會出現可點擊的流程圖。

### 同時使用 Claude Code 時：擇一安裝來源 {#claude-ai-sync}

claude.ai 上開啟的 skill 會自動同步到以同一帳號登入的 Claude Code，名稱會帶 `anthropic-skills:` 前綴。如果你也照本頁的步驟在本機裝了 CT，Claude Code 就會同時看到兩份；本機用 plugin 安裝、`~/.claude/skills/` 又留著手動安裝的話，會是三份。版號不同時可能載入舊的那份。**建議擇一**：

- **以本機安裝為主**（建議）：本機只留 zip 手動安裝或 plugin 其中一種；claude.ai 只上傳 Guide，或在 Claude Code 設定裡把 `syncClaudeAiSkills` 設為 `false`。用 plugin 安裝時，`/ct:ct-exec` 這種完整寫法一定叫到 plugin 版。
- **以 claude.ai 為主**：不要在本機另裝同名 skill，並且每次 CT 更版都重新上傳全部 9 個 zip（CT 8 個加 Guide）。

## 安裝 CT Guide Skill {#guide}

CT Guide 是 CT 的互動式教科書，用問的，它會解釋設計理由並畫可點擊的圖。它和 CT 同版號發行，安裝方式與 CT 相同：zip 手動安裝的目錄名是 `control-tower-guide`；用 plugin 安裝時裝 `ct-guide@control-tower`（見[用 plugin marketplace 安裝](#plugin)）。怎麼安裝、怎麼問，見 [CT Guide Skill](/guide/ct-guide)。

## 安裝 BMad Guide Skill {#bmad-guide}

BMad Guide（`bmad-guide`）是 BMad-Method 的互動式學習指南，也是 CT 的可選搭配：裝了它，塔台會依專案階段查出該走哪一套 BMad 流程（Level 2）；不用 CT 也可以單獨裝，當作學 BMad-Method 的指南。

- **版號跟 BMad-Method 走，不跟 CT**：bmad-guide 的版號就是它所教的 BMad-Method 版號（例如 v6.12.4）。CT 發版時它不會跟著出新版，所以兩者不必同一批升級。
- **zip 的版面**：發行檔是 `bmad-guide-v<版號>.zip`，裡面只有一個 skill。最上層是帶版號的資料夾 `bmad-guide-v<版號>/`（裡面是 `SKILL.md` 和 `references/`）。CT Guide 的 zip（v5.12.4 起）最上層也是一個資料夾，但名稱是不帶版號的 `control-tower-guide/`；bmad-guide 的資料夾名帶版號，和 skill 名稱 `bmad-guide` 不同。
- **安裝路徑**：目錄名用 skill 名稱 `bmad-guide`，解壓後把 `bmad-guide-v<版號>/` 的**內容**放進 Claude Code 的 `~/.claude/skills/bmad-guide/` 或 Codex 的 `~/.codex/skills/bmad-guide/`。不要把帶版號的資料夾原封不動放進 `skills/`。兩端是各自獨立的安裝。
- **升級**：沿用 CT 的同一套流程：先備份到 `skills/` 之外、複製到暫存區複驗後才替換、替換時不先刪除舊目錄，最後逐檔比對 IDENTICAL（見[升級：四步](#upgrade)、[回退](#rollback)）。套用上面那份完整指令時，`SKILLS` 只放 `bmad-guide`；指令是以 skill 名稱找來源目錄，所以先把解壓出來的 `bmad-guide-v<版號>/` 改名為 `bmad-guide/`，`NEW` 指向它的上一層。現行版號看 `SKILL.md` 裡的 `current_version`。
- **新版從下一個 session 才生效**：和 CT 一樣，正在跑的 session 已經載入舊版。
- **也可以用 plugin 安裝**：`bmad-guide@control-tower`，和 CT 放在同一個 marketplace（見[用 plugin marketplace 安裝](#plugin)）。zip 與 plugin 擇一；Codex 用 plugin 時呼叫寫法是 `$bmad-guide:bmad-guide`。CT 5.14.1 起塔台的 Level 2 偵測得到 plugin 版，5.14.4 起先找塔台所在 agent 自己的安裝；搭配 CT 5.14.0 或 6.0.0-beta.5 以前的 beta 時仍建議用 zip 手動安裝（beta.6 起 adapter 也偵測得到，beta.7 實機驗證過），見 [BMad Guide Skill › 用 plugin 安裝](/guide/bmad-guide#install-plugin)。

詳細步驟、claude.ai 的打包方式與 `*update` 怎麼用，見 [BMad Guide Skill](/guide/bmad-guide#install)。

## 搭配 BAT {#bat}

CT 不預先判斷你的 BAT 是哪一版：照常呼叫，失敗時依結束碼降級。各項功能需要的 BAT 最低版本見[相容版本對照](/versions/compatibility)；BAT 本身的安裝與版本見 <BatLink path="install">BAT 站：安裝</BatLink>、<BatLink path="compatibility">BAT 站：版本對照</BatLink>。

## 延伸閱讀 {#further}

- CT 安裝與使用指南 § 4. 安裝（4.1 安裝／升級（現行流程，含〈用 plugin marketplace 安裝／升級〉）、4.2 Agent CLI 選擇、4.3 Skill 架構（v5.14.4））、§ 2.56、§ 2.57、§ 2.58
- `control-tower/references/version-governance.md` § 安裝／升級流程（含 plugin 安裝／升級）、§ 版號事實來源
- `control-tower/references/data-layer-architecture.md` § 寫入規則（Q1～Q4：Layer 1 路徑（含 plugin 安裝路徑）、備份落點、唯一例外）
- `control-tower/references/auto-session.md` § BAT 內部終端路由（Better Agent Terminal），派工指令的權威；§ 依安裝方式的 skill 呼叫字串
- claude.ai 段：CT 開發紀錄中的 claude.ai 安裝調查（官方 Help Center〈Use skills in Claude〉、〈Create custom skills〉，2026-10-23 擷取）

Portal 是摘要，不具權威；與 reference 有出入時，以 reference 為準。
