---
title: Beta：方法論轉接（v6.0.0-beta.1）
description: CT v6.0.0-beta.1 Beta 的方法論轉接：把「只認 BMad」換成可以抽換、分層疊加的 adapter，並用實測決定怎麼防住其他方法論的 SessionStart 注入。Beta 在 GitHub 預發行 Release 提供下載，與穩定版並行、不取代。
---

<script setup>
import { useData } from 'vitepress'

const { theme } = useData()
const stableVersion = theme.value.ctRelease.ctVersion
// Beta 的預發行 Release：tag 與附件名固定，網址用 releasesUrl 組，內文不手寫網址
const betaVersion = '6.0.0-beta.1'
const betaTag = `ct-v${betaVersion}`
const betaPage = `${theme.value.releasesUrl}tag/${betaTag}`
const betaAsset = (name) => `${theme.value.releasesUrl}download/${betaTag}/${name}`
const betaFiles = [
  { name: `BMad-Control-Tower-v${betaVersion}.zip`, size: '402 KB', note: '全量：根層直接是 8 個 skill 目錄' },
  { name: `control-tower-guide-v${betaVersion}.zip`, size: '153 KB', note: 'CT Guide（教學 skill），Beta 內容在「Beta：方法論轉接」一章' },
  { name: `ct-adapter-pstack-v${betaVersion}.zip`, size: '17 KB', note: 'pstack 的 adapter（adapter_version 0.2.3）；不用 pstack 就不必裝' },
  { name: `control-tower-v${betaVersion}.zip`, size: '301 KB', note: '單一 skill（claude.ai 上傳用，下同）' },
  { name: `ct-exec-v${betaVersion}.zip`, size: '23 KB', note: '' },
  { name: `ct-done-v${betaVersion}.zip`, size: '4 KB', note: '' },
  { name: `ct-status-v${betaVersion}.zip`, size: '3 KB', note: '' },
  { name: `ct-evolve-v${betaVersion}.zip`, size: '4 KB', note: '' },
  { name: `ct-fieldguide-v${betaVersion}.zip`, size: '32 KB', note: '' },
  { name: `ct-help-v${betaVersion}.zip`, size: '4 KB', note: '' },
  { name: `ct-insights-v${betaVersion}.zip`, size: '32 KB', note: '' }
]
</script>

# Beta：方法論轉接（v6.0.0-beta.1）

::: warning Beta，與穩定版並行、不取代
本頁介紹的是 **CT v6.0.0-beta.1（Beta）**。Beta 放在 GitHub 的**預發行 Release**，不是最新正式版；規則在正式版 6.0.0 前還可能調整。
目前的穩定版仍是 **v{{ stableVersion }}**，首頁、安裝說明與下載連結都以穩定版為準。Beta 只提供 zip，不會取代你已經裝好的穩定版；想試用，建議裝在隔離的設定目錄（見[下載與試用](#download)）。
:::

<p class="ct-lead">一句話：CT 原本只認得 BMad-Method 這一種開發方法論；v6 把它換成一層「方法論轉接」，BMad 變成第一個、也是預設的 adapter，其他方法論只要寫一份描述檔就能接上，而且每一層（規劃、執行、審查、驗證、交付）可以各用不同的方法論。v6.0.0-pre.1 預覽版定下這個設計，經過兩輪隔離試用修補後，成為 v6.0.0-beta.1。</p>

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
- **安裝方式和穩定版相同**（見[安裝](../install)）：解開全量 zip，把 8 個 skill 目錄放進隔離設定目錄的 `skills/`；用 pstack 才另外放 `ct-adapter-pstack`。從穩定版的專案改用 Beta，先看 [BUG／PLAN／EXP 預設開啟](#bug-plan-exp)的升級影響。

## beta.1 改了什麼 {#beta1}

v6.0.0-pre.1 驗的是「其他方法論的注入會不會搶走 Worker」，還沒有把 v6 塔台從頭到尾跑過一遍。所以出 Beta 前先做了兩輪**隔離試用**：在暫時的設定目錄裝 pre.1，拿真實專案的複本跑真實的塔台與 Worker session，不碰主環境。

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
| ③ **部分參考** | 精選 skill 的本地副本（鎖版、名稱加前綴、設成不讓模型自己叫用），或只借鏡做法，寫進工單步驟或專案準則 | 無 | 不偵測；要讓塔台路由到副本，就寫一個專案本地 adapter |

各家建議：bmad 用 ①；pstack 當主方法論或固定負責某一層用 ①，只在個別工單借某個 skill 用 ②；Superpowers 沒有 adapter、也沒有官方的關注入開關，建議 ② 或 ③。

引入方式是使用者機器上的安裝選擇，**塔台不替你選、也不改安裝**，派工只看實際偵測到的狀態。②、③ 還沒有實測，上表的塔台行為是依規則推得。

### BUG／PLAN／EXP 預設開啟 {#bug-plan-exp}

`enable_bug_tracking`、`enable_plan_tracking`、`enable_experiments` 的預設由 `false` 改成 `true`。啟用時（含預設啟用）塔台**立即**產生空的 `_bug-tracker.md`、`_backlog.md`，不等第一次 `*sync`：BAT 指揮塔面板的「待辦池」與「臭蟲」讀的就是這兩個檔，以前檔案還沒產生時面板是空的，使用者看不出是還沒同步。

這是 v6 唯一一個「什麼都不設也會不同」的變化：

| 你的設定 | 升到 beta.1 之後 |
|---|---|
| 明寫 `true` | 不變 |
| 明寫 `false` | 不變，照舊關閉 |
| **沒寫這三個鍵** | **會啟用**，塔台下次啟動產生兩個空索引 |

不要就在專案或全域設定明寫 `false`（例如 `*config enable_bug_tracking false`）。檔案已存在就不動；改回 `false` 不刪檔。

### 環境偵測只列名稱 {#env-names}

偵測 BAT 與 CT 的環境變數時**只判斷有無、只列變數名稱**，不用會列出整組變數的指令；`BAT_REMOTE_TOKEN` 任何時候只記「已設定」。舊寫法會連值一起印出，包括權杖；工具輸出會留在對話紀錄裡，也可能被分享出去。判讀邏輯不變。這和穩定版 v5.12.7 是同一個修正。

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
- **只認一家。** 社群裡還有其他把「一張工作怎麼做完」講得很細的方法論，例如 pstack、Superpowers。想用它們的人，在穩定版只能自己在工單裡手寫，CT 也不知道它們會帶來什麼副作用。

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
| 外部 skill | 裝在 skills 目錄的 `ct-adapter-<id>/` | CT 官方的 `ct-adapter-pstack` |
| CT 內建 | CT 自帶 | `bmad`（目前唯一一個） |

專案可以用同名的本地 adapter 覆寫內建的 `bmad`。v6 另附一支唯讀的檢查腳本 `validate-adapter.py`，檢查描述檔裡能機器判斷的部分（欄位齊不齊、路由結構、狀態對應四態等）；上游名稱是否真的存在、有沒有夾帶原文，仍要人看。

### 內建 bmad

穩定版散在 CT 文件裡的 BMad 路由、替代名稱表、Autonomous Contract，v6 全部搬進內建的 `bmad` adapter，舊名只留在它的「退役名稱」對照裡。這次也順便修正了上面提到的舊名漂移。

### `ct-adapter-pstack`

CT 官方的第一個外部 adapter，讓塔台能把執行、審查、驗證層交給 [pstack-claude](https://github.com/michael-denyer/pstack-claude)（pstack 給 Claude Code 與 Codex 的移植版）。它只是描述檔：不執行 pstack，也不取代 pstack 的安裝；與 CT 衝突的地方（例如 pstack 的 playbook 結尾預設開 PR、預設開會寫程式的背景子代理）寫成 CT 優先的規則。Beta 把它打包成獨立的 zip（`adapter_version` 0.2.3，見[下載與試用](#download)），不在 `control-tower` 裡，不用 pstack 就不必裝。

### 何時另外配一個 guide skill

BMad 除了 adapter，還有一個獨立的 `bmad-guide`（教學、細路由、名稱與版本對照）。新方法論要不要也配一個？v6 的準則是**符合下列任一才配**：

1. 沒有自帶路由，或自帶的路由不認版本
2. 多階段，而且要依產物狀態決定下一步
3. skill 改名、退役頻繁，需要一個地方持續維護對照
4. 需要在地化教學

BMad 四項都符合，所以有 guide；有 guide 時名稱與細路由以 guide 為準，adapter 只是標明測試版本的快照。pstack 是反例：它自帶入口與 playbook、改版快，CT 需要的資訊全部放在 adapter 裡就夠了。

## 防住別家方法論的注入 {#guard}

接其他方法論時，最實際的問題不是「怎麼叫它」，而是**它會不會自己跑進來**。pstack 與 Superpowers 都會裝 SessionStart hook：每個 session（包括 Worker 分頁）一開，就在 context 裡注入一段「遇到某類工作先用我的入口」的指示，compact 之後還會再注入一次。Worker 開始執行工單時，可能被這段指示導進方法論自己的流程，而那套流程可能想開子代理、開分支、開 PR，和 CT 的規則衝突。

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

樣本都很小，只能說「邊界段有效、沒有邊界段有風險」，不能當成機率。出 Beta 前的第二輪隔離試用又驗了一次雙注入＋疊加，邊界段同樣有效。另一個附帶發現：Superpowers 的外掛資訊寫 hook「沒有 context 成本」，實際每個 session 注入約 3.4 KB，所以 adapter 的常駐 token 數一定要含實測的注入量。

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

## 還沒驗證的事 {#unverified}

beta.1 把下列 7 項明確標成「已知未驗」，正式版前可能因實測結果調整：

1. Codex 互動分頁的「Hooks need review」畫面，以及 Codex 設定裡 hook 的啟用狀態（`hooks.state.<key>.enabled`）：目前是依程式內字串與既有文件推論。
2. Codex 在 resume、compact 後是否重新注入。
3. 方法論要求「先問使用者」的硬閘門（Superpowers 的 brainstorming）：試用時沒有觸發。工單指定了方法論負責哪幾層時，Worker 不採用不負責本單的注入；要 `methodology_guard: off`、工單又沒有 `methodology` 時才可能遇到，這種情況還沒實測。
4. 方法論疊加：一般疊加與雙注入＋疊加各驗過一次；跨層的 story spec 交接與狀態回寫還沒驗。
5. 工單沒寫「不開分支、不 push」時，pstack 的 poteto-mode 會不會委派子代理或開 PR：沒有邊界段、但工單 frontmatter 寫明交付層 `none`、子代理不得寫入時，poteto-mode 仍跳過了開 PR 與委派（驗過一次）；frontmatter 也沒寫的情況還沒驗。
6. 引入方式 ②（只引用 skill）、③（部分參考）還沒實測。
7. 啟用即產生空索引、塔台語言規則、暫存目錄退路、子代理回報要求是本版的文件規則，還沒有實機跑過。

## 出處與名稱 {#notices}

本頁提到的第三方方法論只引用名稱與連結，不附上游內容：

- [pstack-claude](https://github.com/michael-denyer/pstack-claude)：pstack 給 Claude Code、Codex 的移植版（MIT，授權全文見上游 repo）；原作 pstack 在 [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)。`ct-adapter-pstack` 的出處與上游授權見它 zip 內的 `NOTICE.md`，本站 repo 的 `THIRD-PARTY-NOTICES.md` 也有一節摘要。
- [Superpowers](https://github.com/obra/superpowers)：只出現在雙注入的驗證情境，CT 沒有為它做 adapter。

「pstack」「poteto-mode」「Superpowers」是上游專案使用的名稱；CT 使用這些名稱只為了指出對應的上游功能，不代表上游作者認可或參與。

## 延伸閱讀 {#further-reading}

以下檔案都在 [Beta 的 zip](#download) 裡：

- `control-tower/references/methodology-adapters.md`：方法論轉接契約的唯一權威定義（描述檔格式、層次、解析、降級、衝突與防護、引入方式）
- `control-tower/references/adapters/bmad.yaml`：內建 bmad adapter
- `control-tower/references/bug-plan-system.md` § 啟用與索引檔、§ 索引格式：BUG／PLAN／EXP 預設開啟與空索引
- `control-tower/references/data-layer-architecture.md` § 路徑解析：`CLAUDE_CONFIG_DIR`／`CODEX_HOME`
- `ct-adapter-pstack/`：`README.md`（引入方式建議、限制與實測摘要）、`NOTICE.md`（出處與授權）
- `control-tower/references/memory-protocol.md` § 機器可讀摘要（YAML frontmatter）
- `ct-exec/SKILL.md` § Methodology：Worker 端的帶入、注入自查與紀錄規則
- CT Guide `references/preview-methodology.md`「Beta：方法論轉接」：§ 引入方式（附三種引入方式的圖）、§ 隔離試用、§ BUG／PLAN／EXP 預設開啟、§ 環境偵測只列名稱、§ 全域路徑、§ 已知未驗

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。本頁介紹的是 Beta，正式版的規則以正式發布的 CT 為準。
:::
