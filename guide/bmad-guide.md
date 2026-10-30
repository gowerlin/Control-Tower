---
title: BMad Guide Skill
description: BMad-Method 的互動式學習指南 bmad-guide：它是什麼、和 CT 的關係、什麼時候問它、啟動版本檢查與 *update、怎麼安裝（zip 或 plugin marketplace），以及版號為什麼跟 BMad-Method 走。
---

<script setup>
import { useData } from 'vitepress'
import bmadGuide from '../data/bmad-guide.json'

const { theme } = useData()
const mkt = theme.value.marketplaceRepo

const modeRows = [
  ['Learning（概念理解）', '「X 是什麼」「這怎麼運作」「解釋 X」', '先簡短講概念，再說它在生命週期的哪個位置，最後補常見陷阱與什麼時候不該用'],
  ['Practical（實戰查詢）', '「下一步做什麼」「該用哪個指令」「怎麼跑 X」', '先給確切的 bmad-* skill ID 或 workflow，列出輸入 → 產出，並註明是 IDE／本機流程還是 Web Bundle 流程']
]

const renameRows = [
  ['bmad-quick-dev', '改名', 'bmad-build'],
  ['bmad-dev-auto', '改名', 'bmad-build-auto'],
  ['bmad-checkpoint-preview', 'v6.12.0 改名', 'bmad-walkthrough'],
  ['bmad-create-prd／bmad-edit-prd／bmad-validate-prd', '改名', 'bmad-prd（create／update／validate）'],
  ['bmad-market-research 等三種 research', '合併', 'bmad-deep-recon（type = market／domain／technical）'],
  ['bmad-document-project', '合併', 'bmad-project-context（setup）'],
  ['bmad-create-story、bmad-dev-story', '棄用但完整保留', '不在預設流程；建議改用 bmad-build'],
  ['bmad-create-ux-design', '退役', 'bmad-ux'],
  ['bmad-investigate', '退役（v6.10.0）', '一般調查、bmad-help、研究型工單，或意圖清楚後用 bmad-build']
]

const refRows = [
  ['workflow-map.md', 'BMM 各階段、四種規劃路徑、Agent 與選單代碼、主流程順序、產出物、bmad-build／bmad-build-auto 的位置、改名與退役對照表、各版重點變更'],
  ['v6-11-migration.md', '你說出 v6.10／v6.11 時代的 skill ID、產出物或選單代碼時，查現行的替代者；shim 行為；客製化 TOML 改名'],
  ['supplementary-workflows.md', 'PRD 變體、product brief、PRFAQ、bmad-spec、bmad-forge-idea、Build、review 分流、bmad-review 視角、bmad-walkthrough、bmad-deep-recon、bmad-project-context、Party Mode、Advanced Elicitation、Web Bundles'],
  ['tea-module.md', '測試、QA 自動化、TEA 整合、風險導向的測試策略'],
  ['ecosystem-modules.md', 'Web Bundles、bmad-customize、BMad Loop、BMad Builder、Game Dev、Creative Intelligence、外部模組、安裝前提、分層 TOML 設定'],
  ['brownfield.md', '既有程式碼的專案、bmad-project-context 與 AGENTS.md 區塊、已退役的 project-context.md 與 bmad-investigate 路由'],
  ['diagrams.md', '畫任何 SVG 圖之前'],
  ['update-protocol.md', '你輸入 *update、要求更新知識庫，或啟動版本檢查發現版本不同']
]
</script>

# BMad Guide Skill

<p class="ct-lead">BMad Guide Skill（skill 名稱 <code>bmad-guide</code>）是 BMad-Method 的互動式學習指南：用繁體中文回答 BMad-Method 的流程、角色與 skill 該怎麼用，把你帶到該跑的 <code>bmad-*</code> skill，並可畫出能點擊、一路往下追問的 SVG 流程圖。</p>

本站內容以 **bmad-guide v{{ bmadGuide.version }}**（BMad-Method v{{ bmadGuide.bmadMethodVersion }}）為準。它和 [CT Guide](./ct-guide) 是兩個不同的 skill，分工見[專區首頁](./)。

## 它是什麼 {#what}

- **回答 BMad-Method 的問題**：生命週期各階段、workflow、產出物、Agent 角色、指令路由。回答用繁體中文，skill ID、檔案路徑、指令名稱保留原文。
- **帶路，不代跑**：它告訴你該用哪個 `bmad-*` skill、需要什麼前置條件、輸入什麼、會產出什麼；真正執行流程的是那個 skill 本身。
- **圖可以點**：需要一張流程圖時，它依 `references/diagrams.md` 現場畫 SVG，節點點下去就等於再問一句「介紹 ……」，一層一層往下展開。圖上的配色有固定意義，例如 Phase 1～4 依序是青綠、藍、紫、珊瑚色，開發迴圈用琥珀色，所有標籤都是繁體中文。

它先判斷你在問哪一類問題，只讀對應的那幾份 reference，再依問法選一種回應模式：

<CardTable
  :columns="['模式', '什麼時候', '回答的樣子']"
  :rows="modeRows"
  caption="BMad Guide 的兩種回應模式"
/>

## 和 CT 的關係 {#ct}

CT 不內嵌任何 BMad-Method 內容。你另外裝了 `bmad-guide`，塔台才會依專案階段查出該走哪一套 BMad 流程；沒有它，工作流程欄位改由你手動指定，塔台照常運作，也不會自己編造 BMad 的行為。這是 CT 能力等級裡的 Level 2，偵測不到就安靜降級，不會報錯。

這組規則已經寫在其他頁，本頁不另寫一份：

- 能力等級與「bmad-guide 是外部依賴」：[功能總覽 › 四級能力](/features#levels)
- 塔台讀不到它、或它的版本太舊時怎麼辦：[相容版本對照 › bmad-guide](/versions/compatibility#bmad-guide)
- 它升級了，CT 要不要跟著改：[常見問題](/faq#deps)
- 不用 BMad-Method 也能用 CT：[常見問題](/faq#bmad)

所以 `bmad-guide` 有兩種用法：塔台在開單時讀它（你不用做任何事），以及你自己直接問它。兩者讀的是同一份 skill。

## 什麼時候問它 {#when}

下面這些情況，它會接手（摘自 `SKILL.md` § When To Use）：

- 問 BMad-Method 的概念、階段、workflow、產出物、Agent 或指令路由。
- 問下一步該用哪個 `bmad-*` skill，例如 `bmad-prd`、`bmad-ux`、`bmad-spec`、`bmad-architecture`、`bmad-build`、`bmad-code-review`、`bmad-walkthrough`、`bmad-retrospective`。
- 提到 Mary、John、Winston、Amelia、Sally 這些角色。Paige（Tech Writer）在 v6.11.0 退役，它認得這個名字，會改帶你到 `bmad-project-context` 或 Analyst 的 `PC`。
- 問既有程式碼的專案（brownfield）、`AGENTS.md` 的 project-context 區塊、`stories.yaml`、`bmad-review` 的各種視角、`bmad-deep-recon` 的研究類型、客製化 TOML、`persistent_facts`、`uv`、Web Bundles、TEA 測試、BMad Loop、BMad Builder、Game Dev、Creative Intelligence、Party Mode、Advanced Elicitation。
- 問 `project-context.md` 或文件分片（sharding）。這兩項都已退役，它會說明被什麼取代，而不是帶你去用。

### 說出舊的 skill 名稱時 {#retired}

你說出一個舊的 skill ID，例如 v6.10 時代的 `bmad-quick-dev`、`bmad-create-story`，或 v6.11 的 `bmad-checkpoint-preview`，它會直接說這是舊名，給你現行的 ID 與觸發方式，並查你的客製化檔要不要跟著改名（客製化檔不會跟著 skill 改名）。

v6.12.0 起，舊 ID 只在**有安裝 shim** 的環境還能用：新安裝預設不裝，除非安裝時帶 `--shims`；既有安裝沿用原本的設定。所以「舊名稱還能叫得動」不一定成立，它會把這點講清楚。幾個常見的例子：

<CardTable
  :columns="['舊名稱', '狀態', '改用']"
  :rows="renameRows"
  caption="常見的改名與退役 skill（節錄）"
/>

完整對照表在 `references/workflow-map.md` § Retired Or Deprecated Names，逐項遷移說明在 `references/v6-11-migration.md`。

### 偵測 v7 skills line {#v7}

回答前，它會先看你裝的是不是 BMad 的 **v7 skills line**：已安裝的 skill 裡有 `bmod-method` 或 `bmod-core-tools`，或某個 BMad skill 資料夾裡有 `bmod.toml`，就是 v7（用 `npx skills add bmad-code-org/BMAD-METHOD` 裝的）。版號字串不可靠：v7 preview 的 `bmod.toml` 寫的是 `6.13.0-next`，看起來像 6.x，其實不是。

判斷只靠「看」：查 agent 拿到的可用 skill 清單，或列出 skill 目錄裡有沒有 `bmod-*`，不連網、不寫檔；這些都查不到時就靜默略過。確定是 v7 時，它會先講清楚三件事再回答：

- 這份指南教的是 v6.12，v7 preview 在安裝方式、產出物與 skill 名稱上都不同；
- 安裝、狀態、更新、遷移與「下一步」這類問題，改問已安裝的 `bmad` skill；
- 不推薦 `bmod-*/retired.toml` 列在 `removed` 底下的 skill（例如 `bmad-create-epics-and-stories`、`bmad-sprint-planning`），也不用這份指南描述 v7 的流程。

要注意的是，v6.12.2 起 v6 安裝程式的開頭與結尾訊息會宣傳 v7 preview 的安裝指令。照著那行指令裝的是 v7，不是 v6.12。

## 啟動版本檢查與 `*update` {#update}

**每次啟動先比對版本**：讀 `SKILL.md` 裡的 `current_version`，再查 BMad-Method 官方最新版，先查 GitHub release／tag，查不到改查 npm registry 的 `latest`（`references/update-protocol.md` 另列網頁搜尋為第三順位）。

- 版本相同：不出聲，直接回答。
- 版本不同：提示一次「bmad-guide 知識庫版本 v{local}，官方最新 v{remote}。輸入 \*update 可更新知識庫。」
- 查不到：不出聲，照常回答。

版本檢查**絕不擋住回答**。

**`*update`** 是 bmad-guide 自己的指令（不是 CT 塔台的 `*` 命令）：照 `references/update-protocol.md` 把知識庫更新到 BMad-Method 最新版，依序是版本解析、取得上游原始碼快照、重新產生 references、合併、驗證、輸出摘要。`*update --force` 則是版本號已經相同也重新讀一次上游、重新產生 references。幾條安全規則：

- 只用 npm 的 `latest`，不用 `next`（`next` 是 6.x 的預覽版，不代表 v7）。
- 目標是新的 major（v7 以後），或上游快照已經是 v7 的 skills 結構時，停下來回報，不重新產生。
- 在已安裝的 skill 裡只寫 `bmad-guide` 自己的目錄；覆寫前先備份，而且備份放在 skill 目錄**之外**（例如 `~/.claude/skill-backups/`）。放在 `~/.claude/skills/` 底下、根層帶 `SKILL.md` 的備份會被當成一個 skill 註冊，可能用舊內容搶走路由。
- 打包與安裝都排除 `.` 開頭的路徑（例如編輯器或掃描工具的快取目錄）。
- 查不到上游版本時，保持既有檔案不動，不編造版本。

## 安裝 {#install}

發行檔是 <code>{{ bmadGuide.zip }}</code>，裡面只有一個 skill：

```
bmad-guide-v<版號>/
├── SKILL.md
└── references/      ← 8 份：workflow-map、v6-11-migration、supplementary-workflows、
                        tea-module、ecosystem-modules、brownfield、diagrams、update-protocol
```

注意 zip 的最上層是帶版號的資料夾 `bmad-guide-v<版號>/`。CT Guide 的 zip（v5.12.4 起）最上層也是一個資料夾，但名稱是不帶版號的 `control-tower-guide/`；這裡的資料夾名帶版號，和 skill 名稱 `bmad-guide` 不同。安裝目錄要用 skill 名稱 `bmad-guide`，所以解壓後把那個資料夾的**內容**放進：

| Agent | 安裝路徑 |
|---|---|
| Claude Code | `~/.claude/skills/bmad-guide/` |
| Codex | `~/.codex/skills/bmad-guide/` |

升級時照 CT 的做法：先備份到 `skills/` 之外、複驗後再替換，最後逐檔比對（見[安裝 › 升級](/install#upgrade)）。兩端是各自獨立的安裝，升級其中一端不會更新另一端。

### 用 plugin 安裝 {#install-plugin}

bmad-guide 也放在 CT 的 plugin marketplace `control-tower`（本站的公開 repo <code>{{ mkt }}</code>），plugin 名稱是 `bmad-guide`。plugin 裡的 skill 和發行 zip 的內容相同，另附 BMad-Method 的授權聲明（`THIRD-PARTY-NOTICES.md`）；版號一樣跟 BMad-Method 走。

<div class="language-bash"><span class="lang">bash</span><pre><code># Claude Code
claude plugin marketplace add {{ mkt }}
claude plugin install bmad-guide@control-tower
# Codex
codex plugin marketplace add {{ mkt }}
codex plugin add bmad-guide@control-tower</code></pre></div>

- **zip 與 plugin 擇一**：兩種並存時，`skills/bmad-guide/` 裡手動安裝的那份會生效，plugin 版不生效，而且看不出差別。改用 plugin 前，先把手動安裝備份到 `skills/` 之外再移走，做法同[安裝 › 從 zip 手動安裝改用 plugin](/install#plugin)。
- **呼叫寫法**：Claude Code 照常用 `/bmad-guide`（完整寫法 `/bmad-guide:bmad-guide`）；Codex 一律帶前綴 `$bmad-guide:bmad-guide`，從 shell 帶參數時用單引號包住。
- **更新交給 plugin 指令**：`claude plugin marketplace update control-tower` 再 `claude plugin update bmad-guide@control-tower`；Codex 啟動時自動升級 marketplace。plugin 版**不要用 `*update`**：`*update` 會改寫已安裝 skill 的目錄，而 plugin 的安裝目錄由 Agent CLI 管理，改了會在下次 plugin 更新時被蓋掉，內容也會和 plugin 的版號對不上。等新版 bmad-guide 發布後，用 plugin 指令更新。
- **CT 塔台的 Level 2**：CT 偵測 bmad-guide 的條文目前以 `skills/` 目錄裡的安裝為準（6.0.0 beta 的方法論 adapter 只查 `skills/bmad-guide/`），用 plugin 安裝時塔台可能找不到它，安靜地改成手動填寫工作流程欄位。要讓塔台用到 bmad-guide，目前建議用 zip 手動安裝，待 CT 後續版本支援 plugin 的偵測。
- 其他指令（確認版號、移除）和 CT 的 plugin 相同，見[安裝 › 用 plugin marketplace 安裝](/install#plugin)。

**在 claude.ai 使用**：claude.ai 一次只接受一個 skill 的 zip，而且 zip 的最上層必須是和 `SKILL.md` 的 `name` 同名的資料夾（見[安裝 › 打包](/install#claude-ai-zip)）。發行 zip 的最上層是 `bmad-guide-v<版號>/`，名稱不符，所以要先把資料夾改名為 `bmad-guide/` 再壓一次：

```
bmad-guide.zip
└── bmad-guide/
    ├── SKILL.md
    └── references/
```

壓完用 `unzip -l bmad-guide.zip` 檢查，每一行都應該以 `bmad-guide/` 開頭。上傳步驟和 CT Guide 相同，見[安裝 › 上傳](/install#claude-ai-upload)。

## 版本 {#version}

| 項目 | 值 |
|---|---|
| bmad-guide 版本 | v{{ bmadGuide.version }} |
| 對應的 BMad-Method 版本 | v{{ bmadGuide.bmadMethodVersion }} |
| 發布日 | {{ bmadGuide.releasedAt }} |
| 發行檔 | <code>{{ bmadGuide.zip }}</code> |

- **版號跟 BMad-Method 走，不跟 CT。** bmad-guide 的版號就是它所教的 BMad-Method 版號；CT 發版時它不會跟著出新版，BMad-Method 發版後才用 `*update` 更新。這和 CT Guide 永遠與 CT 同號正好相反。
- 版號寫在 `SKILL.md` 正文的 `current_version` 標記，skill 的說明與標題也帶著同一個版號；啟動版本檢查比對的就是這個標記。
- bmad-guide 每發一版，本頁的版本資料同一輪更新。plugin `bmad-guide@control-tower` 的版號由同一份版本資料產生，公開站重推時跟著更新。
- CT 需要哪一版 bmad-guide、版本太舊時塔台怎麼做，見[相容版本對照 › bmad-guide](/versions/compatibility#bmad-guide)。

## 延伸閱讀 {#further}

- bmad-guide `SKILL.md` § When To Use、§ Startup Version Check、§ Response Flow、§ Response Modes、§ Diagram Conventions、§ Reference File Routing、§ Built-In Commands
- `references/workflow-map.md` § Retired Or Deprecated Names、§ v6.12.0 Key Changes、§ v6.12.1–v6.12.4 Key Changes
- `references/v6-11-migration.md` § Shim Policy (read this first)、§ H. Customization File Rename Guide
- `references/update-protocol.md` § Passive Version Detection、§ Manual Update Command、§ Safety Rules
- `references/ecosystem-modules.md` § Installation Prerequisites、§ Layered Configuration
- `references/brownfield.md` § `bmad-project-context` In Detail、§ Retired Brownfield Routes
- `references/diagrams.md` § Color Conventions、§ Clickable Node Pattern
- CT `enhancement-integration.md` § Level 2：外部 bmad-guide

bmad-guide 的 8 份 references 各管什麼（摘自 `SKILL.md` § Reference File Routing）：

<CardTable
  :columns="['檔案', '什麼時候讀']"
  :rows="refRows"
  caption="bmad-guide 的 references"
/>

摘要不具權威；與 bmad-guide `SKILL.md`／references 有出入時，以 skill 為準。
