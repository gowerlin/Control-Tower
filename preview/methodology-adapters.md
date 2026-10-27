---
title: Beta：方法論轉接（v6.0.0-beta.2）
description: CT v6.0.0-beta.2 Beta 的方法論轉接：把「只認 BMad」換成可以抽換、分層疊加的 adapter，用實測決定怎麼防住其他方法論的 SessionStart 注入，並逐家說清楚哪些方法論值得引入、哪些只要共存。Beta 在 GitHub 預發行 Release 提供下載，與穩定版並行、不取代。
---

<script setup>
import { useData } from 'vitepress'

const { theme } = useData()
const stableVersion = theme.value.ctRelease.ctVersion
// Beta 的預發行 Release：tag 與附件名固定，網址用 releasesUrl 組，內文不手寫網址
const betaVersion = '6.0.0-beta.2'
const betaTag = `ct-v${betaVersion}`
const betaPage = `${theme.value.releasesUrl}tag/${betaTag}`
const betaAsset = (name) => `${theme.value.releasesUrl}download/${betaTag}/${name}`
const betaFiles = [
  { name: `BMad-Control-Tower-v${betaVersion}.zip`, size: '406 KB', note: '全量：根層直接是 8 個 skill 目錄' },
  { name: `control-tower-guide-v${betaVersion}.zip`, size: '163 KB', note: 'CT Guide（教學 skill），Beta 內容在「Beta：方法論轉接」一章' },
  { name: `ct-adapter-pstack-v${betaVersion}.zip`, size: '17 KB', note: 'pstack 的 adapter（adapter_version 0.2.4）；選用，已經在用 pstack 才需要' },
  { name: `control-tower-v${betaVersion}.zip`, size: '305 KB', note: '單一 skill（claude.ai 上傳用，下同）' },
  { name: `ct-exec-v${betaVersion}.zip`, size: '23 KB', note: '' },
  { name: `ct-done-v${betaVersion}.zip`, size: '4 KB', note: '' },
  { name: `ct-status-v${betaVersion}.zip`, size: '3 KB', note: '' },
  { name: `ct-evolve-v${betaVersion}.zip`, size: '4 KB', note: '' },
  { name: `ct-fieldguide-v${betaVersion}.zip`, size: '32 KB', note: '' },
  { name: `ct-help-v${betaVersion}.zip`, size: '4 KB', note: '' },
  { name: `ct-insights-v${betaVersion}.zip`, size: '32 KB', note: '' }
]
</script>

# Beta：方法論轉接（v6.0.0-beta.2）

::: warning Beta，與穩定版並行、不取代
本頁介紹的是 **CT v6.0.0-beta.2（Beta）**。Beta 放在 GitHub 的**預發行 Release**，不是最新正式版；規則在正式版 6.0.0 前還可能調整。
目前的穩定版仍是 **v{{ stableVersion }}**，首頁、安裝說明與下載連結都以穩定版為準。Beta 只提供 zip，不會取代你已經裝好的穩定版；想試用，建議裝在隔離的設定目錄（見[下載與試用](#download)）。
:::

<p class="ct-lead">一句話：CT 原本只認得 BMad-Method 這一種開發方法論；v6 把它換成一層「方法論轉接」，BMad 變成第一個、也是預設的 adapter，其他方法論只要寫一份描述檔就能接上，而且每一層（規劃、執行、審查、驗證、交付）可以各用不同的方法論。但「能接」不等於「該接」：beta.2 逐家說清楚哪些方法論值得引入、哪些只要在機器上共存就好。v6.0.0-pre.1 預覽版定下設計，兩輪隔離試用修補後成為 beta.1，再一輪試用與逐家定位後成為 beta.2。</p>

## 下載與試用 {#download}

Beta 的發行檔都在預發行 Release <a :href="betaPage" target="_blank" rel="noreferrer">{{ betaTag }}</a>，共 11 個 zip；每個檔的 SHA-256 寫在 Release 說明裡。

<table>
  <thead><tr><th>檔案</th><th>大小</th><th>內容</th></tr></thead>
  <tbody>
    <tr v-for="f in betaFiles" :key="f.name">
      <td><a :href="betaAsset(f.name)">{{ f.name }}</a></td>
      <td>{{ f.size }}</td>
      <td>{{ f.note }}</td>
    </tr>
  </tbody>
</table>

試用前先知道幾件事：

- **只打包，不自動安裝。** Beta 和穩定版 v{{ stableVersion }} 並行：本站的首頁、[安裝](../install)與更版紀錄都還是穩定版，下載 Beta 不會影響已經裝好的穩定版。
- **建議裝在隔離的設定目錄。** 設 `CLAUDE_CONFIG_DIR`（Codex 是 `CODEX_HOME`）指向另一個目錄，把 Beta 裝在那裡，主環境照舊用穩定版。beta.1 修好了全域路徑（見[全域路徑](#config-dir)），隔離試用才真正隔離。
- **塔台與 Worker 用同一批。** 和穩定版一樣，同一個設定目錄裡的 8 個 skill 要一起換版。
- **安裝方式和穩定版相同**（見[安裝](../install)）：解開全量 zip，把 8 個 skill 目錄放進隔離設定目錄的 `skills/`；已經在用 pstack 才另外放 `ct-adapter-pstack`。從穩定版的專案改用 Beta，先看 [BUG／PLAN／EXP 預設開啟](#bug-plan-exp)的升級影響。
- **從 beta.1 升到 beta.2 沒有設定變更**：契約仍是 `ct-methodology-adapter/v1`，設定鍵與預設值都和 beta.1 相同，8 個 skill 照樣一起換即可。

## 方法論不是一定要引入：各家定位 {#adopt-or-not}

v6 讓 CT 能接任何方法論，但接一家的成本是確定的：每個 session 常駐的注入、搶走 Worker 的風險、跟著上游改版、Release 多一個附件；效益卻不一定。beta.1 的建議只回答了「怎麼裝才不干擾 CT」，沒有先問「裝了有沒有用」，結果把一家在 CT 下用不到的方法論也寫成了可引入的選項，讀起來就像 CT 在推薦它。

所以 beta.2 打包前，先依三輪隔離試用與研究結果逐家寫出效益、成本與建議，確認後才寫進 CT。原則是：

::: tip 原則
**只有實測或研究證明對 CT 使用者有效益時，CT 才給它 adapter、範例或引入建議；沒有效益的，CT 只保留「機器上已經裝了它時怎麼共存」的防護，不推薦、不做範例。**
:::

| 方法論 | 定位 | 效益 | 成本 |
|---|---|---|---|
| BMad-Method（內建 adapter） | **引入**：完整安裝，內建、預設 | CT 原生的方法論與課程基準；隔離試用時行為與 5.12.x 一致 | adapter 要跟著 bmad-guide 的更名走（已有同步流程） |
| pstack（`ct-adapter-pstack`） | **選用**：已經在用 pstack 才裝；CT 不預設、不主動推薦 | 已在用 pstack 的人能把熟悉的流程抽換或分層接進 CT（隔離試用照規則走完整流程）；也是 adapter 契約唯一的外部參考實作 | 沒有邊界段時注入會搶走 Worker；常駐注入約 1 KB；背景子代理要額外記帳；要跟上游版本 |
| Superpowers（沒有 adapter） | **不建議引入**；已經裝了的機器照共存防護 | 在 CT 下**沒有實測效益**：有邊界段時 0 次被叫用（三輪試用都是），沒有邊界段時 Worker 也不採用不負責本單的注入，「先問使用者」的硬閘門三次都沒觸發 | 每個 session 常駐注入 3.4～7.9 KB；上游沒有只關注入的開關 |
| mattpocock/skills（沒有 adapter，工具型 skill 集） | [部分參考](#adoption)的**可選做法範例，品質效益未實證**；不建議標準 plugin 安裝 | 「部分參考」的機制實測有效：本地副本不會被模型自己叫到、工單指名才用、用了 3/3 都有記錄；提供 TDD、除錯、審查的具體做法 | 只有文件層；用它和不用它的品質差異沒有比較過 |

讀這張表的方式：

- **Superpowers 不是「不好」，是「在 CT 下用不到」。** 它的設計是讓模型自己判斷何時進 brainstorming、TDD 這類流程；CT 工單已經寫定「做什麼、怎麼驗收」，Worker 依 `ct-exec` 的優先序不採用不負責本單的注入，所以三輪試用它都沒被叫到，剩下的只有成本。
- **pstack 有用，但只對「已經在用 pstack 的人」有用。** 沒在用的人裝了，只會多出搶路由的注入與常駐 token。所以是「選用」，不是「推薦」；CT 的預設仍是 BMad。
- **mattpocock/skills 證明的是「部分參考這個做法行得通」，不是「它讓品質變好」。** 品質比較（A/B）評估後不做：樣本太小、合成的試驗工單會干擾判讀，而且結果不會改變 CT 的設計。想在自己的專案用，建議在真實專案開一張 EXP 單、只測一支。
- 這張表是**給使用者的建議**，不是塔台的派工規則。塔台派工照實際偵測：機器上裝了什麼，塔台就照什麼防護，不替你改安裝。

### 已經裝了 Superpowers 怎麼辦 {#superpowers-coexist}

不必為了 CT 移除，但 CT 也不會去用它。塔台照共存防護處理（`methodology-adapters.md` § 衝突與防護）：

- 注入開著時，預設的 `methodology_guard: warn` 在工單自動加「方法論邊界」段，把 Superpowers 列進「不使用」；和 pstack 同時開著時，派工摘要另外標「雙注入」（見[防住別家方法論的注入](#guard)）。
- 派工摘要的常駐 token 寫「未量測」，不填估值。
- 「設計核准前不准實作」的硬閘門：沒有指名 Superpowers 的工單，Worker 在無人值守（yolo）下不會被它擋住（試用 2/2）。
- 想省掉常駐注入，只能在 CT 管理的機器上停用它（上游沒有只關注入的開關）。這是使用者的安裝選擇，塔台只提示、不代做。

## beta.2 改了什麼 {#beta2}

beta.1 留下兩個「依規則推得、沒有實測」的大項：引入方式的[部分參考](#adoption)（mattpocock/skills 的副本做法是新寫的），以及 Superpowers 的「先問使用者」硬閘門會不會擋住 Worker。這兩項直接決定 beta.2 怎麼寫，所以照前兩輪的方式再做一輪**隔離試用**：暫時的設定目錄、真實專案的複本、試完比對主環境沒有變動。

| 看什麼 | 結果 | beta.2 怎麼改 |
|---|---|---|
| 部分參考：mattpocock/skills 3 支本地副本 | 塔台與 Worker 共 4 個 session 裡 **0 次**被模型自動叫用；塔台照規則把副本路徑寫進工單的「只允許」；Worker 3/3 以路徑讀並照做、3/3 記入回報區 | 部分參考寫成**已實測**；只引用 skill 仍未實測 |
| Superpowers 硬閘門 | 守衛關掉、工單也沒指定方法論時，注入送達，2/2 仍沒觸發、沒停下、沒提問 | 觸發條件改成與實測一致：沒有指名 Superpowers 的工單不會被它擋住 |
| 沒有 hook、靠描述觸發的 skill | 標準 plugin 安裝時，塔台 0/1 被自動叫用 | 「塔台一樣會被叫到」改成「也可能被叫到」並附樣本數：一次沒發生不代表風險不存在 |
| 環境偵測的寫法 | bash 的舊寫法要放行 `env` 才跑得動；一次讀多個變數時混進了不在例外清單的變數 | 見下方[環境偵測：`compgen -e`、一個變數一個指令](#env-compgen) |

這輪試用沒有找到擋住 beta.2 的問題，全部只改文件。其他變更：

- **[各家定位](#adopt-or-not)與「方法論不是一定要引入」原則**寫進權威檔；Superpowers 在 CT 文件、`*onboard` 與 Guide 裡一律改成共存說法。
- **部分參考的做法補兩點**：部分層用本地副本時，不為副本寫方法論層，其他層照原本的解析；副本裡要問使用者或等核准的步驟，在邊界段逐條寫成 CT 的處理（寫進回報區不停下、改問塔台、回 `BLOCKED`）。
- **「方法論 skill」的範圍**擴到工單邊界段或執行步驟指名的 skill（含本地副本）：用了一樣記入回報區的方法論執行紀錄；副本在 Claude Code 也只能以路徑讀，讀了照做算一次呼叫。
- **`ct-adapter-pstack` 0.2.4**：README 加「選用」定位與部分參考的實測結果，描述檔的欄位與值不變。工單範本與派工摘要範例的 pstack 版本同步改成 `upstream 0.9.103 / adapter 0.2.4`。

### 在 CT 專案使用 mattpocock/skills {#mattpocock}

[mattpocock/skills](https://github.com/mattpocock/skills)（MIT）是一組**工具型 skill 集**：TDD、除錯、code review 之類的單支做法。它不是方法論，沒有編排、沒有狀態，也沒有 hook。CT 沒有它的 adapter，**也不散布它的任何檔案或原文**；下面都是使用者在自己專案裡做的事，是部分參考的一個可選範例，**品質效益未實證**，不是 CT 的推薦。

**不要在 CT 管理的機器上裝標準 plugin。** 沒有 hook 反而更難防：標準安裝後，模型會依 skill 描述自己決定叫用，塔台與 Worker 都可能被叫到，而 CT 偵測注入看的是 hook，偵測不到這種叫用。plugin 也會自動更新，實際跑的版本和工單記的對不上。改用部分參考：

1. **本地副本、鎖版**：從上游一個固定的 commit 把要用的 skill 複製到專案的 skill 目錄。
2. **名稱加前綴**（例：`mp-`）：上游有和 Claude Code 內建指令同名的 skill（`code-review`），不加前綴可能叫到內建的那一個。
3. **關掉自動叫用**：Claude Code 在副本 frontmatter 加 `disable-model-invocation: true`；Codex 也要用時，另寫 `policy.allow_implicit_invocation: false`。兩個 runtime 各看各的設定。
4. **改寫外部前提**：叫其他上游 skill 的句子改成副本路徑或刪掉；以外部 issue tracker 為規格來源的前提改成「規格就是本工單」。
5. **工單指名才用**：在工單的方法論邊界段或執行步驟寫副本路徑；Worker 用了照樣記入回報區。
6. **記版本**：副本旁放一份紀錄（例：`VENDOR.md`：上游網址、commit、複製日期、本地改了什麼），上游更新時另開工單比對，不自動同步。

有些 skill 不適合放進 Worker 工單：自建 worktree 或整合分支的、以外部 issue tracker 為事實來源的、開會寫檔的背景子代理的、整支都在問使用者的。它們分別撞上 CT 的「隔離走 BAT worktree」「事實來源是工單」「寫入集中在主 Worker」「無人值守時不問使用者」。完整清單見 `methodology-adapters.md` § ③ 的做法。

::: info 副本放在被 `.gitignore` 排除的目錄時（推論）
副本常放在 `.claude/skills/` 這類目錄，而不少專案的 `.gitignore` 排除整個 `.claude/`。BAT 的 worktree 隔離派工從 git 建出工作樹，**沒進 git 的副本不會出現在 worktree 裡**，Worker 就讀不到工單指名的路徑；要在隔離派工裡用副本，就讓副本進 git。這一點是讀規則推得的，還沒有派 worktree 實測。
:::

### 環境偵測：`compgen -e`、一個變數一個指令 {#env-compgen}

beta.1 起偵測環境變數只列名稱（見[環境偵測只列名稱](#env-names)），但試用發現規則本身的寫法會走樣：bash 的 `env | cut …` 在有指令白名單的環境要放行 `env` 才跑得動，而放行 `env` 等於放行「印出整組變數與值」；一個 `printenv` 一次讀多個名稱時，清單外的變數很容易跟著被讀出來。beta.2 改成：

- **bash 列名稱用 `compgen -e`**（bash 內建，只輸出名稱、不碰值）：`compgen -e | grep -E '^(BAT|CT)_' | sort`。PowerShell 寫法不變：`Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object`。
- **明列的例外一個變數一個指令讀**（例：`printenv CT_MODE`，再另一個指令讀下一個），不把多個名稱放進同一個指令，也不和列名稱的指令串成一行。看指令就知道讀了什麼，白名單也能逐個放行。

試用中沒有任何一次嘗試印出權杖的值；改的是「照規則做也會走樣」的寫法。

## beta.1 改了什麼 {#beta1}

v6.0.0-pre.1 驗的是「其他方法論的注入會不會搶走 Worker」，還沒有把 v6 塔台從頭到尾跑過一遍。所以出 beta.1 前先做了兩輪**隔離試用**：在暫時的設定目錄裝 pre.1，拿真實專案的複本跑真實的塔台與 Worker session，不碰主環境。

| 輪 | 範圍 | 結果 |
|---|---|---|
| 第一輪 | v6 塔台在舊 5.x 狀態檔上啟動；BMad 預設的小任務；疊加（主方法論 bmad、執行層 pstack） | 舊專案正常啟動，第一次寫入就補上機器可讀摘要；小任務跑到完成，回報區和 5.12.x 同構；一般疊加驗過一次 |
| 第二輪 | 整張工單抽換成 pstack；pstack＋Superpowers 雙注入；試著觸發 Superpowers 的硬閘門；雙注入＋疊加 | 抽換走完整流程；雙注入照規則處理；硬閘門沒有觸發；雙注入＋疊加驗過一次 |

兩輪都**沒有擋住 Beta 的問題**：找到的都是規則措辭或 adapter 的宣告，契約仍是 `ct-methodology-adapter/v1`，沒有新增欄位。beta.1 的變更如下。

### 引入方式：完整安裝、只引用 skill、部分參考 {#adoption}

pre.1 時，方法論只有「完整安裝」和「不用」兩種狀態。可是方法論和 CT 衝突的地方大多來自它的 SessionStart hook：只想借一個 skill 的人，也得承擔整套每個 session 都會注入的指示。beta.1 把「裝到什麼程度」列成正式選項：

| 方式 | 裝什麼 | 常駐注入 | 塔台怎麼看 |
|---|---|---|---|
| ① **完整安裝** | 上游的標準安裝：plugin、hook、skill 全裝 | 有 | 偵測到注入開著，照 `methodology_guard: warn` 自動加邊界段；兩家以上標「雙注入」 |
| ② **只引用 skill** | 不裝會常駐注入的 hook／plugin，只裝需要的 skill（例如上游的 skills-only 安裝），或以路徑讀 skill 檔 | 無 | 偵測為關，不加這家的邊界段；用到時在工單的邊界段指名 skill |
| ③ **部分參考** | 精選 skill 的本地副本（鎖版、名稱加前綴、設成不讓模型自己叫用），或只借鏡做法，寫進工單步驟或專案準則 | 無 | 不偵測；工單邊界段或執行步驟指名副本路徑，用了照樣記入回報區；要讓塔台路由到副本，就寫一個專案本地 adapter |

各家怎麼引入（beta.2 依[各家定位](#adopt-or-not)改寫）：bmad 用 ①；pstack 是選用，已經在用的人當主方法論或固定負責某一層用 ①，只在個別工單借某個 skill 用 ②；mattpocock/skills 這類工具型 skill 集用 ③（做法見[上面](#mattpocock)）。Superpowers **不建議引入**，所以沒有引入方式的建議；機器上已經裝了，就照[共存防護](#superpowers-coexist)處理。

引入方式是使用者機器上的安裝選擇，**塔台不替你選、也不改安裝**，派工只看實際偵測到的狀態。③ 在 beta.2 已實測（見 [beta.2 改了什麼](#beta2)）；② 還沒有實測，上表的塔台行為是依規則推得。

### BUG／PLAN／EXP 預設開啟 {#bug-plan-exp}

`enable_bug_tracking`、`enable_plan_tracking`、`enable_experiments` 的預設由 `false` 改成 `true`。啟用時（含預設啟用）塔台**立即**產生空的 `_bug-tracker.md`、`_backlog.md`，不等第一次 `*sync`：BAT 指揮塔面板的「待辦池」與「臭蟲」讀的就是這兩個檔，以前檔案還沒產生時面板是空的，使用者看不出是還沒同步。

這是 v6 唯一一個「什麼都不設也會不同」的變化：

| 你的設定 | 升到 Beta 之後 |
|---|---|
| 明寫 `true` | 不變 |
| 明寫 `false` | 不變，照舊關閉 |
| **沒寫這三個鍵** | **會啟用**，塔台下次啟動產生兩個空索引 |

不要就在專案或全域設定明寫 `false`（例如 `*config enable_bug_tracking false`）。檔案已存在就不動；改回 `false` 不刪檔。

### 環境偵測只列名稱 {#env-names}

偵測 BAT 與 CT 的環境變數時**只判斷有無、只列變數名稱**，不用會列出整組變數的指令；`BAT_REMOTE_TOKEN` 任何時候只記「已設定」。舊寫法會連值一起印出，包括權杖；工具輸出會留在對話紀錄裡，也可能被分享出去。判讀邏輯不變。這和穩定版 v5.12.7 是同一個修正；beta.2 再把 bash 寫法改成 `compgen -e`（見[上面](#env-compgen)）。

### 全域路徑：`CLAUDE_CONFIG_DIR`／`CODEX_HOME` {#config-dir}

CT 文件寫的 `~/.claude/…` 一律解讀為 `${CLAUDE_CONFIG_DIR:-~/.claude}/…`，`~/.codex/…` 解讀為 `${CODEX_HOME:-~/.codex}/…`；塔台讀全域設定、偵測 adapter 都照這個規則，變數沒設時和 5.12.x 相同。隔離試用時，塔台仍到家目錄找全域設定，等於讀到主環境的設定，這正是隔離想避免的事。

### 其他修補 {#other-fixes}

- **塔台的對話語言不因方法論注入改變**：試用時，pstack 注入開著的塔台有幾次改用英文回覆。原本的防護都寫給 Worker，忘了塔台也是一個 session、也會收到注入。
- **沒有 scratchpad 時的暫存目錄**：邊界段寫明退路是系統暫存目錄下的 `ct-<工單號>/`，收尾刪除，repo 外不留檔。試用時有 Worker 把工作檔寫到 repo 的上一層。
- **方法論自帶的子代理**：工單允許某個方法論 skill 時，也涵蓋它自己呼叫的子 skill 與自帶的唯讀審查子代理（含背景執行的）；回報區要寫子代理數、是否背景、子代理裡叫了哪些 skill。真正的風險是「用了沒寫」，所以改成允許＋照實回報。
- **紀錄格式附範例**：Worker 記錄注入狀態（`methodology_ambient`）的格式常寫錯，規則改成直接附正反範例。
- **沒有 adapter 的注入方法論**：常駐 token 寫「未量測」，不填估值，並附上量法。
- **方法論狀態回寫段**：主方法論有 tracker（bmad 的 `sprint-status.yaml`）時，回報區保留這一段，和 5.12.x 的回報區形狀一致。
- **`ct-adapter-pstack` 0.2.3**：宣告哪些 pstack 流程會開子代理、是否背景執行；實測版本 0.9.103；偵測路徑照上面的全域路徑規則；README 加引入方式建議。

## 為什麼要做 {#why}

CT 管的是**編排**：哪張工單、誰來做、做完沒有、怎麼回報。一張工單**裡面**怎麼寫程式、怎麼審查，向來交給方法論。穩定版的做法是「能力等級 Level 2」：偵測到 `bmad-guide` 就用 BMad 的 workflow 路由，沒有就退回自由文字。

這個做法有兩個問題：

- **路由寫死在 CT 本體，就會落後。** 設計 v6 時發現，穩定版的 BMad 路由還寫著 BMad-Method v6.11 前的舊名（`bmad-build-auto`、`bmad-build` 的前身）；v5.12.8 起穩定版也已改用現行名稱。方法論改版的速度和 CT 不同步，名稱與路由應該放在一個能單獨更新的地方。
- **只認一家。** 社群裡還有其他把「一張工作怎麼做完」講得很細的方法論，例如 pstack。想用的人在穩定版只能自己在工單裡手寫；機器上裝了別家方法論（例如 Superpowers）時，CT 也不知道它會帶來什麼副作用。

所以 v6 把 Level 2 換成方法論中立的一層，並把分工講清楚：

| 誰 | 負責 | 不負責 |
|---|---|---|
| **CT 核心** | 工單生命週期、落點檢查、`affects_files`、回報區格式、commit／push 規則、yolo 提問、通知、三振、學習萃取 | 工單內「怎麼寫程式、怎麼審查」 |
| **adapter**（描述檔） | 告訴 CT：這個方法論在哪、什麼版本、管哪幾層、每種需求走哪個流程、結果怎麼對應 CT 狀態、會寫哪些檔、會和 CT 撞在哪 | 執行任何東西：描述檔是資料，不是程式 |
| **方法論本身** | 工單內的紀律與步驟 | CT 的生命週期 |

衝突時 **CT 的生命週期規則永遠優先**。方法論說「做完了」，但工單的驗證閘門沒過，工單就不能是 `DONE`。

## 五層與抽換 {#layers}

方法論的範圍切成五層。「編排」不是第六層，它永遠屬於 CT。

| 層 | 範圍 | 對應的 CT 工單 |
|---|---|---|
| 規劃 | 需求、PRD、架構、UX、拆工作項、研究調查 | 研究型工單、設計工單 |
| 執行 | 實作、重構、修 bug、TDD | 一般實作工單 |
| 審查 | code review、對抗式審查、一致性分析 | 審查工單、品質閘門插入的審查 |
| 驗證 | 測試策略、驗收、在實物上驗證 | 驗證工單、驗證閘門 |
| 交付 | 開 PR、merge、release、deploy | 發版工單；**預設不交給方法論** |

**抽換**：專案設定新增主方法論 `methodology`，預設 `auto`。`auto` 的意思是「偵測到 bmad-guide 就用 bmad，否則不用方法論」，**和穩定版的行為完全相同**，所以不改設定就不會有任何差別。

**分層疊加**：每一層另有一個設定鍵（`methodology_planning`、`methodology_execution`、`methodology_review`、`methodology_verification`、`methodology_delivery`），值是 adapter 名、`none`，或 `inherit`（跟主方法論）。例如「規劃用 BMad、實作用 pstack」：

```yaml
methodology: bmad
methodology_execution: pstack
```

疊加有幾條固定的規則，理由都是「讓塔台在派工時就能說清楚誰負責什麼」：

- **每層只有一個負責者。** 同一張工單、同一層不能有兩個方法論，免得 Worker 收到兩套互相矛盾的步驟。
- **層與層之間靠產物交接。** 上一層產出的規格檔（例如 BMad 的 story spec）要對得上下一層能吃的格式；對不上時，塔台警告，把產物路徑當一般文件交給下一層。
- **審查層預設跟主方法論。** 換掉執行層會失去原方法論內建在執行流程裡的審查（例如 BMad Build 內建的 Review Triage），派工摘要會提醒這個取捨。
- **交付層預設 `none`。** 開 PR、push、發版是對外、不可逆的動作，CT 不讓方法論代做，除非使用者明說。
- **單張工單可以覆寫。** 說「這張用 X 做」，規劃到驗證四層都用 X（交付層除外）；說「這張審查用 Y」，只換那一層。覆寫寫進工單本身，不改設定檔。

解析結果由塔台寫進工單 frontmatter 的 `methodology` 欄位，Worker 照工單做，**不自己讀設定檔**，這和 CT 一貫的「執行期的值由塔台傳入」相同。

## adapter 是什麼 {#adapter}

一個方法論 = 一份 YAML 描述檔（給機器讀）＋一份 README（給人讀）。描述檔固定 22 個頂層欄位：識別與版本、偵測方式、五層的能力、每種需求的路由、工單要加哪些段落、Worker 怎麼呼叫、結果怎麼對應 CT 狀態、會寫哪些檔、會裝哪些 hook、和 CT 撞名的詞。描述檔**只放名稱、對照、連結與 CT 自己的規則，不放第三方方法論的原文**。

adapter 有三種來源，搜尋時由近到遠，同名取第一個找到的：

| 來源 | 位置 | 例子 |
|---|---|---|
| 專案本地 | 專案的 `_ct-workorders/_adapters/<id>/` | 團隊自己的開發規範 |
| 外部 skill | 裝在 skills 目錄的 `ct-adapter-<id>/` | CT 官方的 `ct-adapter-pstack`（選用） |
| CT 內建 | CT 自帶 | `bmad`（目前唯一一個） |

專案可以用同名的本地 adapter 覆寫內建的 `bmad`。v6 另附一支唯讀的檢查腳本 `validate-adapter.py`，檢查描述檔裡能機器判斷的部分（欄位齊不齊、路由結構、狀態對應四態等）；上游名稱是否真的存在、有沒有夾帶原文，仍要人看。

### 內建 bmad

穩定版散在 CT 文件裡的 BMad 路由、替代名稱表、Autonomous Contract，v6 全部搬進內建的 `bmad` adapter，舊名只留在它的「退役名稱」對照裡。這次也順便修正了上面提到的舊名漂移。

### `ct-adapter-pstack`

CT 官方的第一個外部 adapter，讓塔台能把執行、審查、驗證層交給 [pstack-claude](https://github.com/michael-denyer/pstack-claude)（pstack 給 Claude Code 與 Codex 的移植版）。它只是描述檔：不執行 pstack，也不取代 pstack 的安裝；與 CT 衝突的地方（例如 pstack 的 playbook 結尾預設開 PR、預設開會寫程式的背景子代理）寫成 CT 優先的規則。定位是**選用**：已經在用 pstack 的人才需要，CT 不預設、不主動推薦。Beta 把它打包成獨立的 zip（`adapter_version` 0.2.4，見[下載與試用](#download)），不在 `control-tower` 裡。

### 何時另外配一個 guide skill

BMad 除了 adapter，還有一個獨立的 `bmad-guide`（教學、細路由、名稱與版本對照）。新方法論要不要也配一個？v6 的準則是**符合下列任一才配**：

1. 沒有自帶路由，或自帶的路由不認版本
2. 多階段，而且要依產物狀態決定下一步
3. skill 改名、退役頻繁，需要一個地方持續維護對照
4. 需要在地化教學

BMad 四項都符合，所以有 guide；有 guide 時名稱與細路由以 guide 為準，adapter 只是標明測試版本的快照。pstack 是反例：它自帶入口與 playbook、改版快，CT 需要的資訊全部放在 adapter 裡就夠了。

## 防住別家方法論的注入 {#guard}

機器上裝了其他方法論時，最實際的問題不是「怎麼叫它」，而是**它會不會自己跑進來**。pstack 與 Superpowers 都會裝 SessionStart hook：每個 session（包括 Worker 分頁）一開，就在 context 裡注入一段「遇到某類工作先用我的入口」的指示，compact 之後還會再注入一次。Worker 開始執行工單時，可能被這段指示導進方法論自己的流程，而那套流程可能想開子代理、開分支、開 PR，和 CT 的規則衝突。這些防護不論 CT 建不建議那一家都照樣保留，也是[共存防護](#superpowers-coexist)的內容。

不想讓注入開著，可以改用[只引用 skill 或部分參考](#adoption)；注入開著時，v6 的處置是派工前的檢查 `methodology_guard`：

| 值 | 行為 |
|---|---|
| `warn`（預設） | 塔台偵測到有方法論的注入開著、而它不負責本單任何一層時，**自動**在工單加一段「方法論邊界」：本單不使用哪些方法論 skill、子代理只能唯讀、不開分支、不 push、方法論要求先問使用者時不因此停下、compact 或 resume 後先重讀工單。派工摘要同時提示哪幾家注入開著、每個 session 多花多少 token |
| `block` | 不派工，請使用者先關掉注入或改設定。留給完全不想讓方法論碰 CT 工單的專案自選 |
| `off` | 不檢查，不加邊界段 |

同時開著兩家以上的注入時，至少照 `warn` 處理，邊界段每一家都列，派工摘要另外標「雙注入」。Worker 這一側也加了兩條硬規則：在回報區記下自己在 context 看到哪些注入（沒看到也要寫「沒有」），以及**用了任何方法論 skill 都要寫進回報區**，不論工單有沒有宣告。

### 為什麼是 `warn`，不是 `block` {#evidence}

這不是憑感覺決定的。v6.0.0-pre.1 設計時，在隔離的設定目錄裡用真的 session 跑了三輪驗證：

| 驗證 | 環境 | 沒有邊界段 | 有邊界段 |
|---|---|---|---|
| V1 | Claude Code＋pstack | 2 次中 1 次在動手前進了 pstack 的入口，而且**回報區沒寫** | 3 次都沒呼叫方法論 skill，回報區主動聲明遵守邊界 |
| V2a | Codex＋pstack（hook 已信任） | 2 次都進了 pstack 的入口，其中 1 次回報區沒寫 | 2 次都擋住 |
| V2b | Claude Code＋pstack＋Superpowers 雙注入 | 3 次都沒呼叫方法論 skill，但回報區**都沒提到**注入存在 | 兩家都列的邊界段 2 次都有效，回報區主動寫出方法論紀錄 |

從這張表可以讀出三件事：

- **注入是真的會改變 Worker 的行為**，而且發生時塔台只看工單完全不會知道。所以「什麼都不做」不行，Worker 用了方法論一定要記。
- **一段寫清楚的邊界就壓得住**，在三種環境下都有效。所以不需要預設 `block` 把整個方法論擋在外面，自動加邊界段的成本低得多。
- 進了方法論流程的那幾次，Worker 都靠工單明寫的「不開分支、不 push」跳過了衝突步驟；工單沒寫這些時會不會照做，沒有測。所以邊界段把這些寫成明文，不依賴工單剛好有寫。

樣本都很小，只能說「邊界段有效、沒有邊界段有風險」，不能當成機率。出 beta.1 前的第二輪隔離試用又驗了一次雙注入＋疊加，邊界段同樣有效。另一個附帶發現：Superpowers 的外掛資訊寫 hook「沒有 context 成本」，實測每個 session 注入 3.4～7.9 KB，所以常駐 token 數一定要以實測的注入量為準。

### Codex 的 hook 信任 {#codex-hook-trust}

Codex 的 hook 要使用者**信任**之後才會執行；沒信任時，`codex exec` 會靜默略過，不注入、也不提示。信任狀態寫在使用者的 Codex 設定檔裡，技術上塔台可以替使用者寫進去，但 v6 明定：**塔台不替使用者信任 hook**。Codex 自己寫明信任後的 hook 可以在 sandbox 外執行，信任等於核准在 sandbox 外執行程式，這是使用者的決定，不在塔台的權限內。

塔台改做的是派工前看 hook 的狀態：

- **已信任**：注入會到，照 `warn` 自動加邊界段（V2a 實測邊界段有效）。
- **未信任或信任後被改過**：hook 不執行，但 BAT 派出的互動 Codex 分頁會在開工前停在「Hooks need review」畫面等人。派工摘要提示使用者先在自己的終端機開一次 `codex` 處理，或照 adapter 寫的開關關掉注入。方法論升版後，之前信任過的 hook 可能要再 review 一次。
- **外掛停用**：不注入，不用處理。

## 塔台狀態摘要（給 BAT 總覽） {#tower-state-summary}

v6 另外替塔台狀態檔 `_tower-state.md` 加了一段機器可讀的摘要（檔頭的 YAML frontmatter），讓 BAT 的指揮塔總覽不必解析整份 Markdown，就能顯示塔台現在的狀況：

| 欄位 | 內容 |
|---|---|
| `updated_at` | 摘要最後更新時間（取自系統時間） |
| `session` | 目前塔台 session 的說明 |
| `next_ids` | 下一個可用的工單、決策編號（有用 BUG／PLAN 時也列） |
| `todo` | 待辦，BAT 只顯示前 5 則 |

塔台每次寫入狀態檔都順手更新摘要。**進行中的工單刻意不放進摘要**：BAT 直接從工單檔的 `status` 自己算，避免兩份資料不一致。舊專案沒有摘要不是錯誤，塔台下次寫入時補上（第一輪隔離試用實測如此）。摘要只給外部顯示用，塔台自己恢復狀態仍以本文為準。

BAT 端在 `0.7.1-pre.7`（預覽版）加上這個總覽：沒有摘要的專案也能看到最後更新時間與進行中工單；「下一個編號」與「待辦」要 CT v6 寫出摘要後才有。版本需求見[相容版本對照的 Beta 一節](../versions/compatibility#preview)。

## 向下相容 {#compat}

- 不設定 `methodology` 就是 `auto`，方法論的行為與穩定版 v{{ stableVersion }} 相同。
- **例外：BUG／PLAN／EXP 預設開啟。** 設定沒寫這三個鍵的專案，升級後會啟用並產生兩個空索引；不要就明寫 `false`（見[上面](#bug-plan-exp)）。
- 舊工單的 `### BMad 工作流程` 段照讀，CT 從裡面寫的 workflow 名稱推出它屬於哪一層；**不回寫舊工單**。
- 工單沒有 `methodology` 欄位時，Worker 的執行方式和穩定版相同。
- BAT 介面與 CT 要求的最低 BAT 版本沒有因為方法論轉接而改變。
- beta.1 升 beta.2 沒有設定變更，契約與設定鍵都相同。

## 還沒驗證的事 {#unverified}

beta.2 把下列 9 項明確標成「已知未驗」，正式版前可能因實測結果調整：

1. Codex 互動分頁的「Hooks need review」畫面，以及 Codex 設定裡 hook 的啟用狀態（`hooks.state.<key>.enabled`）：目前是依程式內字串與既有文件推論。
2. Codex 在 resume、compact 後是否重新注入。
3. 引入方式：③ 部分參考**已實測**（mattpocock/skills 3 支本地副本：0 次被模型自動叫用、塔台照規則寫「只允許」、Worker 以路徑讀並 3/3 記入回報區）。還沒測的是：Codex 端的 `policy.allow_implicit_invocation: false`、② 只引用 skill、副本在 BAT worktree 隔離派工下讀不讀得到（副本放在被 `.gitignore` 排除的目錄時讀不到，是推論）。沒有 hook 的描述觸發：標準安裝時塔台 0/1 被叫用，風險未排除。
4. Superpowers 的「先問使用者」硬閘門：守衛關掉、工單也沒指定方法論時，無人值守下 2/2 沒觸發；工單明確指名 Superpowers 的 brainstorming 時會怎樣，還沒實測。
5. 副本裡「先問使用者」的步驟，在無人值守下改問塔台：試用工單事先回答了，這條路徑沒有出現。
6. 無人值守的提問備援（沒有可用的等待工具時直接回 `BLOCKED`）：試用中 Worker 都判斷沒有要問塔台的事，沒有觀察到。
7. 方法論疊加：一般疊加與雙注入＋疊加各驗過一次；跨層的 story spec 交接與狀態回寫還沒驗。
8. 工單沒寫「不開分支、不 push」時，pstack 的 poteto-mode 會不會委派子代理或開 PR：沒有邊界段、但工單 frontmatter 寫明交付層 `none`、子代理不得寫入時，poteto-mode 仍跳過了開 PR 與委派（驗過一次）；frontmatter 也沒寫的情況還沒驗。
9. 啟用即產生空索引、塔台語言規則、暫存目錄退路、子代理回報要求，以及 beta.2 的環境偵測新寫法，都是文件規則，還沒有實機跑過。

## 出處與名稱 {#notices}

本頁提到的第三方方法論與 skill 集只引用名稱與連結，不附上游內容：

- [pstack-claude](https://github.com/michael-denyer/pstack-claude)：pstack 給 Claude Code、Codex 的移植版（MIT，授權全文見上游 repo）；原作 pstack 在 [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)。`ct-adapter-pstack` 的出處與上游授權見它 zip 內的 `NOTICE.md`，本站 repo 的 `THIRD-PARTY-NOTICES.md` 也有一節摘要。
- [Superpowers](https://github.com/obra/superpowers)：CT 沒有為它做 adapter，也不建議引入；本頁只在實測與共存防護的說明裡提到它。
- [mattpocock/skills](https://github.com/mattpocock/skills)（MIT）：CT 沒有為它做 adapter，也不散布它的任何檔案或原文；本頁只把它當部分參考的做法範例。

「pstack」「poteto-mode」「Superpowers」「mattpocock/skills」是上游專案使用的名稱；CT 使用這些名稱只為了指出對應的上游功能，不代表上游作者認可或參與。

## 延伸閱讀 {#further-reading}

以下檔案都在 [Beta 的 zip](#download) 裡：

- `control-tower/references/methodology-adapters.md`：方法論轉接契約的唯一權威定義（描述檔格式、層次、解析、降級、衝突與防護）；§ 引入方式 有「方法論不是一定要引入」原則與各家建議，§ ③ 的做法 是 mattpocock/skills 的完整步驟
- `control-tower/references/adapters/bmad.yaml`：內建 bmad adapter
- `control-tower/references/bug-plan-system.md` § 啟用與索引檔、§ 索引格式：BUG／PLAN／EXP 預設開啟與空索引
- `control-tower/references/data-layer-architecture.md` § 路徑解析：`CLAUDE_CONFIG_DIR`／`CODEX_HOME`
- `control-tower/references/auto-session.md` § BAT 內部終端路由 › 偵測條件：環境偵測只列名稱、`compgen -e` 與一個變數一個指令
- `ct-adapter-pstack/`：`README.md`（選用定位、引入方式建議、限制與實測摘要）、`NOTICE.md`（出處與授權）
- `control-tower/references/memory-protocol.md` § 機器可讀摘要（YAML frontmatter）
- `ct-exec/SKILL.md` § Methodology：Worker 端的帶入、注入自查與紀錄規則（含「方法論 skill」的範圍）
- CT Guide `references/preview-methodology.md`「Beta：方法論轉接」：§ 方法論不是一定要引入：各家定位、§ 在 CT 專案使用 mattpocock/skills、§ 實測（③ 部分參考與 HARD-GATE，beta.2）、§ 引入方式（附三種引入方式的圖）、§ 隔離試用、§ BUG／PLAN／EXP 預設開啟、§ 環境偵測只列名稱、§ 全域路徑、§ 已知未驗

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。本頁介紹的是 Beta，正式版的規則以正式發布的 CT 為準。
:::
