# 方法論轉接（Methodology Adapters）

> **v6.0.0 正式版（取代 5.15.0 成為穩定版）。** 本檔是 CT 方法論轉接契約的**唯一權威定義**：adapter 描述檔格式、層次與需求類型、
> 工單欄位、狀態對應、降級、抽換／疊加／解析規則、衝突與防護。其他檔（`enhancement-integration.md` § Level 2、
> `SKILL.md` § Methodology Adapters、`adapters/*.yaml`）只引用本檔，不複述。
> 方法論轉接自 `6.0.0-pre.1` 預覽起，經 beta.1～beta.12 與 rc.1 預發行，於 6.0.0 納入正式版。實作進度見 § Beta 實作狀態（章節名沿用預發行期間的名稱以免斷連，內容是現行版本 6.0.0）。
>
> 設計依據：`BMad-Control-Tower/spec/方法論介接/METHODOLOGY-PLAN.md`（T0298）§ 4～§ 6；G0 定案 D332（T0297）。
> 調查證據（各方法論的出處與行號、實測紀錄）留在 PLAN，本檔只寫規則。

## Beta 實作狀態

| 部分 | v6.0.0 | 說明 |
|---|---|---|
| 契約（本檔）、內建 bmad adapter（`adapters/bmad.yaml`） | ✅ | Level 2 的 BMAD 路由改由 `adapters/bmad.yaml` 提供（`enhancement-integration.md` § Level 2） |
| 工單 frontmatter `methodology`、`### 方法論工作流程` 等新段落進工單模板 | ✅ | `work-order-template.md` § 填寫方法論欄位指引（三範例）、`work-order-system.md` § 派發流程 第 2 步、§ 主方法論 tracker 同步（T0301） |
| `methodology*` 設定鍵登錄進 `*config` | ✅ | 登錄、驗證、持久化格式、解析例在 `tower-config.md` § 可用選項、§ 方法論設定鍵；`*onboard` 主題 5、`ct-help` § Methodology Adapters（T0302） |
| Worker 端（`ct-exec` 帶入、注入自查、子代理寫入授權；`ct-status`／`ct-done`／`ct-insights` 讀 `tracker`） | ✅ | Worker 規則在 `ct-exec/SKILL.md` § Methodology（帶入、優先序、注入自查、方法論使用必記、子代理授權、交付層）與 § Startup（compact／resume 後重讀工單）；`ct-status` sync、`ct-done` 補修、`ct-insights` 讀主方法論 `tracker`；V1 實測結果併入 § 與 hook／session 路由的相處規則、§ 衝突與防護 C1、C9（T0306） |
| 外部 adapter（`ct-adapter-<id>` skill）與驗證腳本 | ✅ | CT 官方 `ct-adapter-pstack`（原始碼 `adapters/ct-adapter-pstack/`，隨 CT 發行版另出 zip）；驗證腳本 `scripts/validate-adapter.py`（§ 新 adapter 的最小檢查 的可機器檢查部分）（T0303） |

**向下相容（硬約束，D332）**：`methodology` 缺省 = `auto` = 現行行為；舊工單的 `### BMad 工作流程` 段照讀、不回寫。

## 分工

| 誰 | 負責 | 不負責 |
|---|---|---|
| **CT 核心** | 工單生命週期（PENDING → IN_PROGRESS → 最終態）、落點檢查、`affects_files`、回報區格式、commit／push 規則、yolo 提問、BAT 通知、三振、學習萃取 | 工單內「怎麼寫程式、怎麼審查」 |
| **adapter**（描述檔） | 告訴 CT：這個方法論在哪、什麼版本、管哪幾層、每種需求走哪個流程、Worker 怎麼叫它、它的結果怎麼對應 CT 狀態、它會寫哪些檔、會跟 CT 撞在哪 | 執行任何東西（描述檔是資料，不是程式） |
| **方法論本身** | 工單內的紀律與步驟 | CT 的生命週期 |

CT 的生命週期規則永遠優先（§ 衝突與防護 › 優先序）。

## 層次

| 層 | 鍵名 | 範圍 | CT 對應 |
|---|---|---|---|
| 規劃 | `planning` | 需求、PRD、架構、UX、拆 story／task、研究調查 | 研究型工單、設計工單 |
| 執行 | `execution` | 實作、重構、修 bug、TDD | 一般實作工單 |
| 審查 | `review` | code review、對抗式審查、一致性分析 | 審查工單、品質閘門插入的審查 |
| 驗證 | `verification` | 測試策略、驗收、在實物上驗證 | 驗證工單、Phase 3 驗證閘門 |
| 交付 | `delivery` | 開 PR、merge、release、deploy | 發版工單（**預設 `none`**：CT 不讓方法論做交付，除非使用者授權） |

「編排」不是第六層：它永遠屬於 CT，不可指定給 adapter。

「Level」在 CT 已有三種意思（能力等級、Playbook 成熟度、FIELDGUIDE 分層）；方法論的分層一律稱「層」（layer），不稱 Level。

## 需求類型（routing 的鍵）

`feature`（新功能）・ `bugfix`（修 bug）・ `refactor`（重構）・ `research`（研究）・ `review`（審查）・ `test`（測試）・ `small-change`（小修改）・ `delivery`（交付，選填）。

每個類型下列出各層的入口。某層沒有入口 = 本方法論不處理該層，由其他層的 adapter 或 CT 本身負責。

## 描述檔格式

一個方法論 = 一份 YAML 描述檔（機器讀）＋一份 README（人讀）。描述檔只放名稱、對照、連結與 CT 自己的規則，
**不放第三方 skill 原文**。

| 來源 | 描述檔位置 | `id` 對應 |
|---|---|---|
| CT 內建 | `control-tower/references/adapters/<id>.yaml`（說明寫在檔內註解與本檔） | 檔名 |
| 外部 skill | `ct-adapter-<id>/adapter.yaml`＋`README.md`（skill 目錄另有說明用途的 `SKILL.md`） | 目錄名去掉 `ct-adapter-` |
| 專案本地 | `_ct-workorders/_adapters/<id>/adapter.yaml`＋`README.md` | 目錄名 |

### 欄位表（`schema: ct-methodology-adapter/v1`）

固定 22 個頂層欄位。必填 = 缺了就視同描述檔壞掉（§ 降級）；「可為 `{}`／`[]`」= 欄位要在，內容可空。

| 欄位 | 必填 | 意義 |
|---|---|---|
| `schema` | ✅ | 契約版本，固定 `ct-methodology-adapter/v1` |
| `id` | ✅ | 設定與工單用的識別字，`[a-z0-9-]`，須等於上表的檔名／目錄名。`auto`、`none`、`inherit` 是**保留字**（設定值的關鍵字，§ 抽換），不能當 `id`；設定值是這三個字時一律當關鍵字解讀 |
| `display_name` | ✅ | 顯示名 |
| `adapter_version` | ✅ | adapter 自己的版本（不是上游版本） |
| `adapter_status` | ✅ | `prototype` / `stable` / `deprecated` |
| `maintainer` | ✅ | `kind`（`ct-builtin` / `external-skill` / `project-local`）、`owner`、`sync_rule` |
| `upstream` | ✅ | `name`、`url`、`license`、`version_range`、`tested_version`、`version_source`；選填 `pinned_ref`、`original`、`guide` |
| `runtimes` | ✅ | 支援的 runtime 清單（`claude-code`、`codex`）；不支援的 runtime 不列 |
| `detection` | ✅ | `strategy`（`any` / `all`）、`probes[]`（`id`、`kind`：`skill` / `plugin` / `file`；`search` 路徑；`version_marker`；`required_files`；選填 `skill_root`：只用於 `kind: plugin`，v6.0.0-beta.6+；選填 `runtime`：probe 屬於哪個 runtime，值是 `runtimes` 內的一個 runtime 名（`claude-code`、`codex`），沒寫 = 所有 runtime 適用，v6.0.0-beta.8+；路徑怎麼解析、試的順序見下方 § probe 怎麼解析 skill 根目錄）、`min_version`、`on_below_min`、`on_missing`；**方法論有 hook 時必填** `hook_probe`（判斷注入是否開著、`off_switch` 可寫「無」）。注入條件依 runtime 不同時（例：Codex 的 hook 要信任才執行），`hook_probe` 以 runtime 名（`claude-code`、`codex`）為鍵分開寫：每個有 hook 的 runtime（`session.hooks[].runtime`，沒寫 = `runtimes` 全部）都要有自己的鍵，其他鍵為各 runtime 共用 |
| `capabilities` | ✅ | 5 層各 `full` / `partial` / `none` |
| `routing` | ✅ | `<需求類型>.<層>` → 入口（見下方 routing 入口欄位）。需求類型的值寫 `{}` = **明確缺席**（本方法論不處理這類需求）；缺鍵才算不完整 |
| `workorder` | ✅ | `section_heading`、`annotations`、`required_when[]`（某 workflow 要加哪個段落與欄位）、`legacy`（舊段名、舊 observation 鍵） |
| `worker` | ✅ | `lifecycle_owner`（固定 `ct-exec`）、`run_mode`（`inline`）、`invoke.<runtime>`、`requires`、`asks_user[]`、`ct_overrides[]`（`behavior` → `ct_rule`） |
| `status_mapping` | ✅ | `source`、`rules[]`（`when` → `ct_status`：DONE / PARTIAL / BLOCKED / FAILED）、`required_report[]` |
| `artifacts` | ✅ | `writes[]`（塔台開單要放進 `affects_files` 或指定到 scratchpad）；選填 `user_config`（方法論改寫的使用者層設定，例：在 `CLAUDE.md` 加 include） |
| `handoff` | ✅ | `produces[]`、`consumes[]`（各有 `layer`、`kind`）、`writeback`（`target`、`by`） |
| `tracker` | ✅（可為 `{}`） | 進度追蹤檔（`file`、`search`、`optional`），給 `*sync`／`ct-status sync` |
| `retired_names` | ✅（可為 `{}`） | 舊名 → `{replacement, since, kind}`（各項可另加選填 `note`）；另允許一個值為字串的 `note` 鍵（整組的說明，不是舊名）。CT 文件裡該方法論的舊名只留在這裡 |
| `degradation` | ✅ | `not_installed`、`below_min_version`、`workflow_missing`；選填 `no_subagents` |
| `session` | ✅ | `hooks[]`（`event`、`matcher`、`effect`、`measured`、`off_switch`、`ct_guard`；選填 `runtime`：注入發生在哪些 runtime、`entry_skills`：注入叫 session 先用的 skill 清單、`trigger_summary`：注入條件摘要，一句 CT 自己的話，不貼原文）、`name_collisions[]`、`subagents`（`writes`、`ct_rule`；選填 `only_in`：只有哪些 workflow 會開子代理，不寫 = 不限、`background`：會開背景子代理、`worktree`：子代理會自建 worktree）、`always_on_tokens`（常駐 token 數，**含 hook 注入量**，C14）；選填 `skill_patterns`（本方法論 skill 的名稱樣式，例 `pstack:*`、`bmad-*`）。`entry_skills`、`trigger_summary`、`skill_patterns` 是塔台填邊界段範本用的值（§ 與 hook／session 路由的相處規則 第 2 點）；有 hook 的 adapter 應提供 |
| `vocabulary` | ✅ | 撞詞對照（方法論詞 → 與 CT 詞的區別） |
| `links` | ✅ | 參考連結 |

**routing 入口欄位**：`workflow`（必填；`none` = 不走方法論、直接改）、`alternatives`、`detail`（一層多步序列或 playbook 名，v1 以文字描述）、`agent`、`reference`（方法論 skill 內的檔名，相對於偵測成功的 probe 解析出的 skill 根目錄，見 § probe 怎麼解析 skill 根目錄；adapter 可在註解指定子目錄，例 bmad 的 `references/`）、`note`、`unattended`（無人值守時改用的 workflow）、`fallback`（`workflow: none` 不適用時的退路）、`requires_module`（需要的 opt-in 模組）、`ct_policy`（CT 對這個入口的額外規則）。

**`kind` 的建議值（非封閉）**：下列是內建 bmad 與 `ct-adapter-pstack` 已用的值，新 adapter 優先沿用；意思不同時可以自訂新值，
但跨層交接只在兩邊 `kind` 字串相同時才對得上（§ 分層疊加 第 3 點）。

| 欄位 | 建議值 |
|---|---|
| `retired_names.<舊名>.kind` | `retired`（已移除，沒有直接替代）、`deprecated`（還在但不建議用）、`forwarding-shim`（舊名轉呼叫新名）、`retained-shim`（舊名保留但行為已變）、`renamed-artifact`（產物檔名改了）、`removed-field`（產物欄位移除） |
| `handoff.produces[]`／`consumes[]` 的 `kind` | `story-spec`（單一工作項的規格檔）、`epic-spec`（一組工作項的規格與清單）、`goal-text`（一句話目標或一般文件路徑；交接對不上時的退路） |
| `maintainer.kind` | 封閉：`ct-builtin` / `external-skill` / `project-local`（上方欄位表） |
| `detection.probes[].kind` | 封閉：`skill` / `plugin` / `file`（上方欄位表） |

### probe 怎麼解析 skill 根目錄

（v6.0.0-beta.6+；本小節是 probe 路徑解析的唯一權威，各 adapter 的 `detection.probes` 只寫自己的路徑與順序。）

1. **順序**（v6.0.0-beta.8 起依 runtime 分開）：塔台先認定自己跑在哪個 runtime（Claude Code 或 Codex，即塔台所在的 agent），再依下表試
   `detection.probes`；`strategy: any` 時第一個成功的 probe 決定 **skill 根目錄**（方法論 skill 的 `SKILL.md` 所在目錄）與偵測到的版本。

   | 順序 | 試哪些 probe | 命中時 |
   |---|---|---|
   | ① | `runtime` 是本 runtime 的 probe，以及沒寫 `runtime` 的 probe，依列出的順序 | 照常使用 |
   | ② | `runtime` 是另一個 runtime 的 probe，依列出的順序 | **只當讀檔來源**（見下方） |

   - **同一個 runtime 內手動優先**：同一個 skill 有手動安裝與 plugin 兩種 probe 時，本 runtime 的 agent 實際載入的是手動安裝那份
     （[auto-session.md](auto-session.md) § 依安裝方式的 skill 呼叫字串），所以 adapter 要把同一個 runtime 的 `kind: skill` probe 排在 `kind: plugin` 前面。
     這個理由只在同一個 runtime 內成立：Claude Code 不載入 `~/.codex/skills/`、`~/.agents/skills/`，Codex 也不載入 Claude 的 `skills/`，
     所以另一個 runtime 的手動安裝排在本 runtime 的 plugin 之後（②）。內建 bmad adapter 照這個規則試出來的順序是：本 runtime 手動 →
     本 runtime plugin → 另一個 runtime 手動 → 另一個 runtime plugin，和穩定版 5.14.4 `enhancement-integration.md` § Level 2 › 偵測 第 1 步的 ①②③ 相同。
     skill 名稱不同的 probe（例：`ct-adapter-pstack` 的 skills-only 安裝）在同一個 runtime 內依 adapter 自己的需要排，不受此限。
   - **② 只當讀檔來源**：本 runtime 的 agent 沒有載入這一份，版本與 `references/` 可能和使用者在本 runtime 呼叫得到的不同（① 都沒有命中時，
     使用者在本 runtime 根本叫不到這個方法論的 skill）。照常用它的 skill 根目錄解析 `routing` 的 `reference` 與版本，並在第一次用到時
     （派工摘要的備註或回覆裡）註明一次「〈方法論〉讀自 〈另一個 runtime〉 的安裝，不是本 runtime 載入的」，不阻塞 Tower；`on_below_min` 的版本提示照常。
   - **沒寫 `runtime`** 的 probe 對每個 runtime 都排在 ①、依列出的順序：probe 都沒寫 `runtime` 的 adapter（v6.0.0-beta.7 以前的格式）
     照列出順序試，行為不變。只對某個 runtime 有意義的路徑（該 runtime 的 `skills/`、plugin 清單）應寫 `runtime`，
     免得另一個 runtime 的塔台把它當成本 runtime 載入的那份。
2. **各 `kind` 的 skill 根目錄**：

   | `kind` | `search` 命中的是 | skill 根目錄 |
   |---|---|---|
   | `skill` | `<skills 目錄>/<skill>/SKILL.md` | 命中檔所在目錄 |
   | `file` | 任意檔案 | 命中檔所在目錄 |
   | `plugin` | plugin 清單：Claude `installed_plugins.json`、Codex `config.toml`（依檔名判斷是哪個 runtime） | `<plugin 安裝根目錄>/<skill_root>`；沒寫 `skill_root` → 沒有 skill 根目錄（只判斷有沒有裝、讀版本） |

3. **plugin 安裝根目錄**：probe 的 `name` 寫 `<plugin>@<marketplace>`，`<marketplace>` 寫 `*` = 任一 marketplace（不寫死 marketplace 名稱；
   有多筆符合時用第一筆，派工摘要列出全部）。
   - Claude：清單中 key 符合 `name` 的項目的 `installPath`。清單位置寫成
     `${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}/installed_plugins.json`，**只有這一處**：設了 `CLAUDE_CODE_PLUGIN_CACHE_DIR`
     時清單與 `cache/` 都在它指的目錄（T0357 實測）；只設 `CLAUDE_CONFIG_DIR` 時在 `${CLAUDE_CONFIG_DIR}/plugins/`（T0374 實測）。
     設了其中任一個時，`~/.claude/plugins/` 屬於另一份設定，不是本 session 載入的 plugin，不列進 `search`
     （[data-layer-architecture.md](data-layer-architecture.md) § 路徑解析；v6.0.0-beta.8 起，之前兩處都算）。
   - Codex：`${CODEX_HOME:-~/.codex}/config.toml` 有 `[plugins."<plugin>@<marketplace>"]` 且 `enabled = true` →
     `${CODEX_HOME:-~/.codex}/plugins/cache/<marketplace>/<plugin>/<version>/`（有多個 `<version>` 目錄時取最新版號）。
4. **`skill_root`**（選填，只用於 `kind: plugin`）：skill 目錄相對於 plugin 安裝根目錄的路徑，例 `skills/bmad-guide`；不得是絕對路徑、不得含 `..`。
   plugin 可以帶多個 skill，plugin 名稱也不一定等於 skill 名稱，所以由 adapter 明寫，CT 不推測。
5. **相對路徑相對於誰**：`required_files`、相對路徑的 `version_marker.file`、該 adapter `routing` 的 `reference`，一律相對於第 1 點那個 skill 根目錄，
   不另外假設 `~/.claude/skills/`。沒有 skill 根目錄的 plugin probe 不得寫 `required_files`；它的相對 `version_marker.file` 相對於 `search`
   命中檔所在目錄（例：`ct-adapter-pstack` 的 `installed_plugins.json`）。路徑裡的 `<marketplace>`、`<version>` 代入第 3 點解析出的值。
6. 🔴 **只讀**：probe 解析出的路徑都只讀不寫；plugin 安裝路徑屬 Layer 1（[data-layer-architecture.md](data-layer-architecture.md) § 寫入規則）。
   方法論檔案是 plugin 安裝時要回饋改動，改提議修改原始碼（[enhancement-integration.md](enhancement-integration.md) § Playbook → 方法論回饋）。

### 新 adapter 的最小檢查

- YAML 能解析、`schema` 正確、22 個頂層欄位都在、`id` 符合來源表
- `upstream` 有 URL、授權、`tested_version`；描述檔與 README 沒有第三方 skill 原文
- `detection` 至少一個 probe 能判斷「有／沒有」；有 hook 就有 `hook_probe`；`kind: plugin` 寫了 `required_files` 就要有 `skill_root`；只對某個 runtime 有意義的 probe 寫 `runtime`（值在 `runtimes` 內）；同一個 runtime 內，同一個 skill 的手動安裝 probe 排在 plugin probe 前面（§ probe 怎麼解析 skill 根目錄）
- `capabilities` 5 層都有值；`routing` 對 7 種必填需求類型都有明確入口或明確缺席（值 `{}`）
- `status_mapping` 涵蓋 DONE／PARTIAL／BLOCKED／FAILED，且寫明「方法論 done ≠ 工單 DONE」
- `session.hooks`、`subagents`、`worker.asks_user`、git 副作用（`ct_overrides`）、`artifacts.writes` 都有宣告（沒有就寫空）
- 有 hook 的方法論：附隔離試裝紀錄（注入內容、開關、主環境前後比對）
- `invoke` 對 `runtimes` 列出的每個 runtime 都有寫法

可機器檢查的部分（解析、22 欄位、`id`、routing 結構與明確缺席、probe 欄位（含 `runtime` 的值域）、`status_mapping` 四態等）用
`scripts/validate-adapter.py <描述檔或 adapter 目錄>` 執行檢查；腳本只做本清單裡能機器判斷的項目，規則以本檔為準。
上游名稱是否真的存在、有沒有第三方原文、probe 在真實機器上能不能判斷、隔離試裝紀錄仍要人工看。

## 工單欄位

### frontmatter（機器 SoT，塔台派工時寫入）

```yaml
methodology:
  request_kind: feature            # § 需求類型
  resolved_from:                   # 每層各記來源（鍵同 layers）：workorder / session / project / global / default
    execution: workorder
    review: project
  layers:                          # 本單用到的層；每層一個 adapter
    execution:
      adapter: <id>
      workflow: <adapter routing 的 workflow>
      detail: <選填>
    review:
      adapter: <id>
      workflow: <workflow>
  inputs:                          # 跨層交接（選填）
    - kind: story-spec
      from_adapter: <id>
      path: <產物路徑>
  writeback:                       # 選填；上游 adapter 要求回寫時
    adapter: <id>
    target: <回寫目標>
  versions:
    <id>: "upstream <偵測值> / adapter <adapter_version>"
  subagent_writes: deny            # deny / authorized（authorized 時另附授權段，§ 衝突與防護 C4）
  delivery: none
```

**`resolved_from` 每層各記**：值是該層生效 adapter 來自哪一層設定（§ 抽換 › 疊加層級）。

- 該層由工單覆寫決定（整張或指定層，§ 抽換 › 工單覆寫）→ `workorder`。
- 該層的鍵在某層設定明寫了 adapter id 或 `none` → 那一層（`session`／`project`／`global`）。
- 該層是 `inherit` → 記主方法論 `methodology` 鍵的來源；主方法論是 `auto` 的偵測結果時，記 `auto` 那個值的來源（沒人設過就是 `default`）。
- 鍵只列 `layers` 裡有的層。例：上方範例 = 使用者說「這張執行層用 <id>」（`execution: workorder`），審查層 `inherit` 跟 project 設定的主方法論（`review: project`）。
- 預覽版早期寫成單一值（`resolved_from: project`）的工單照讀，視為每層都是這個來源；不回寫。

### 內文段落

| 段落 | 何時 | 內容 |
|---|---|---|
| `### 方法論工作流程` | 有任何層由 adapter 負責 | 人讀鏡像：每層的 adapter／workflow，加 adapter `workorder.annotations` 宣告的標注 |
| adapter `workorder.required_when` 指定的段落 | 該 workflow 被選用 | 例：bmad `bmad-build-auto` → `### Autonomous Contract` |
| `### 方法論邊界` | `methodology_guard: warn` 時塔台自動加（§ 與 hook／session 路由的相處規則 第 2 點；**沒有任何層由 adapter 負責的工單也加**）、adapter `required_when` 要求、本單開放方法論子代理寫入、或本單要用 § 引入方式 ③ 的本地副本（也可只在執行步驟指名，不加本段） | 本單使用／不使用哪些方法論 skill、子代理是否可寫、不開分支／不 push、交付層是否開放、用了要記、compact／resume 後重讀。範本只寫在 `work-order-template.md` 標準模板的 `### 方法論邊界`（兩種變體），本檔不複述 |
| 回報區 `### 方法論執行紀錄` | 有任何層由 adapter 負責、本 session 呼叫了任何方法論 skill、或 Worker 看到注入標記 | 下方「`### 方法論執行紀錄` 的內容」 |
| 回報區 `### 方法論狀態回寫` | 有 `writeback` 或主方法論有 `tracker`（**沒有任何層由 adapter 負責的工單也保留**，與 v5.12.6 一律有的 `### sprint-status.yaml 已更新` 一致；P-1，T0314） | 回寫了什麼、在哪；用不到時填「不適用」 |

#### `### 方法論執行紀錄` 的內容

依序三部分；沒有的部分整段省略（`methodology_ambient` 行除外，見下）。

1. **`methodology_ambient` 行**（V1 後改必填，仍不阻塞；D342）：Worker 在 context 看到的方法論注入。

   ```markdown
   - **methodology_ambient**：none
   - **methodology_ambient**：pstack（SessionStart:startup、compact；標記「You have pstack.」）
   - **methodology_ambient**：pstack（SessionStart:startup；標記「You have pstack.」）、unknown（SessionStart:startup；標記「<注入文字第一句>」）
   ```

   - 值：`none`（沒看到）或逐家列出 `<adapter id>（<事件>；標記「<一句原文>」）`，多家以 `、` 分隔。認不出是哪個 adapter → `unknown`。
     事件寫看得到的 `SessionStart:<startup|resume|clear|compact>`；看不出事件寫 `事件不明`。compact／resume 後再看到同一家，把事件補在同一項。
     事件一律是 `SessionStart:` 加冒號加子事件，多個子事件以 `、` 分隔（P-5：P1、P1b 共 5 次寫成下列錯誤寫法）：

     | ❌ 不要寫 | ✅ 要寫 |
     |---|---|
     | `pstack（SessionStart hook 注入）` | `pstack（SessionStart:startup；標記「You have pstack.」）` |
     | `pstack（SessionStart startup）`、`pstack（SessionStart；…）` | `pstack（SessionStart:startup；標記「You have pstack.」）`；看不出子事件 → `pstack（事件不明；標記「You have pstack.」）` |
   - 必填的範圍：工單有 frontmatter `methodology` 或有 `### 方法論邊界` → **一律寫**（沒看到就寫 `none`）；都沒有 → 只在看到注入時寫
     （沒寫 = 沒看到，所以這類工單在沒有注入時與 v5.12.6 相同）。
   - 標記只記一句原文，不貼整段注入文字（第三方原文，§ 描述檔格式）。
2. **方法論 skill 使用**：本 session 呼叫的每個方法論 skill（不論工單有沒有宣告；V1 B2 實測「用了沒寫」會發生）。

   ```markdown
   | skill | 在哪一步 | 做了什麼 | 跳過什麼與原因 | 工單有宣告 |
   |---|---|---|---|---|
   | `pstack:poteto-mode` | Phase 2 開始前 | 讀 Feature playbook，列待辦 | 子代理委派、開 PR：工單不開分支、不 push（CT 優先） | 否 |
   ```

   一個都沒呼叫且工單有 `### 方法論邊界` → 寫一行「依本單方法論邊界，未呼叫方法論 skill」。
   方法論 skill 開的子代理在子代理內呼叫的方法論 skill 也各列一列：`在哪一步` 寫 `<上層 skill> 的子代理內（背景／前景）`；
   子代理本身（數量、是否背景、唯讀與否）記在 `### 子代理與 Workflow 使用`（Q-1，T0315：P1b 兩次只寫數量，沒寫背景與子代理內的 skill）。
   「方法論 skill」的範圍只定義在 `ct-exec/SKILL.md` § Methodology（Record every methodology skill call；G2 起含工單指名的 skill），本檔不複述。
3. **adapter `required_report`**：每層負責 adapter 的 `status_mapping.required_report` 逐項，並寫方法論結果怎麼對應到完成狀態（§ 狀態對應總則）。

### 舊欄位相容

| 舊 | 新 | 處理 |
|---|---|---|
| 內文 `### BMad 工作流程` | `### 方法論工作流程` + frontmatter `methodology` | 舊工單沒有 `methodology` frontmatter → 照讀舊段，視為 `layers.<由 workflow 推得的層>.adapter = bmad`；**不回寫舊工單** |
| ECC observation `bmad_workflow` | `methodology_workflow` + `methodology_adapter` | v6.0.0-beta.10 起 ECC Level 1 退場，CT 不再寫 observation（新舊鍵都不寫）；adapter `legacy.observation_key` 只留作識別舊紀錄（`enhancement-integration.md` § ECC Level 1 退場）。v6.0.0-pre.1～beta.9 是過渡期雙寫 |
| 回報區 `### sprint-status.yaml 已更新` | `### 方法論狀態回寫` | 主方法論是 bmad 時內容一樣；舊工單照讀 |

**由 workflow 推得的層**（上表第 1 列）：

1. 在 `adapters/bmad.yaml` 的 `routing` 找舊段寫的 workflow 名稱：它出現在哪一層（`routing.<需求類型>.<層>` 入口的 `workflow`、`alternatives` 或 `unattended`），就是那一層。
   出現在不只一層時，取工單類型對應的層（§ 層次 的「CT 對應」欄：研究、設計工單 → `planning`，一般實作 → `execution`，以此類推）。
2. 名稱在 `routing` 找不到 → 先查 `retired_names`：是舊名就換成 `replacement` 再回到第 1 步。
3. 都查不到 → 不推層，該段當自由文字（§ 降級）。

只用來讀舊工單；不因此改寫舊工單（不補 frontmatter、不改段名，重派或 Renew 時也一樣）。範例見 `work-order-template.md` § 填寫方法論欄位指引 › 範例 C。

## Worker 帶入（契約對 Worker 的要求）

Worker 怎麼帶入方法論（讀 `methodology`、依 `worker.invoke` 呼叫、優先序、注入自查、方法論使用必記、子代理授權、交付層、狀態對應與回寫）
只定義在 `ct-exec/SKILL.md` § Methodology，本檔不複述。Worker 不讀 `_tower-config.yaml` 決定方法論（塔台已解析好寫進工單）；
工單沒有 `methodology` 欄位時，Worker 的執行與 v5.12.6 相同。

## 狀態對應總則

| CT 狀態 | 方法論結果 |
|---|---|
| DONE | 方法論自己的終態為成功，**且**工單驗證閘門通過 |
| PARTIAL | 方法論停在中間狀態、或工單要求的獨立審查沒跑成 |
| BLOCKED | 需要人才能決定（intent gap、產品問題）、或環境不足（沒子代理、缺工具、tree 不乾淨） |
| FAILED | 方法論自己的修復迴圈用完仍驗證失敗，或 CT 三振 |

方法論說「done」但工單閘門沒過 → **以工單閘門為準**（不能 DONE）。各 adapter 的細則寫在自己的 `status_mapping`，不能放寬本表。

## 降級

| 情況 | 行為 |
|---|---|
| adapter 指的方法論沒安裝 | 該層退回 `degradation.not_installed`（通常是自由文字 = Level 0）；派工摘要提示 |
| probe 全部失敗，但 agent 的可用 skill 清單裡有該方法論的 skill（`kind: skill` probe 的 `name`，或 plugin 形式 `<plugin>:<skill>`，例 `bmad-guide:bmad-guide`）——已安裝、只是塔台讀不到 | 本 session **提示使用者一次**（一句話＋建議：告訴塔台 `SKILL.md` 的位置，或改用手動安裝），再照上一列；之後不再提示（v6.0.0-beta.6+）。清單裡也沒有 → 照上一列，不另提示 |
| 版本低於 `min_version` 或超出 `version_range` | 警告，照常路由；工單 `methodology.versions` 記實際偵測值 |
| workflow 名稱不存在 | 先查 `retired_names`；查不到 → 同層主方法論；再不行 → 自由文字 |
| adapter 描述檔本身壞了（解析失敗、缺必填、`id` 不符） | 視同未安裝，警告；不阻塞塔台 |
| 負責 adapter 該層 `capabilities: none` | 塔台警告並退回主方法論；主方法論也 `none` → 該層由 CT 本身（自由文字）處理 |

任何降級都不阻塞塔台，也不得替方法論編造行為：沒有 adapter 依據的 workflow 名稱，一律當自由文字處理。

## 與 hook／session 路由的相處規則

1. **adapter 必須宣告自己的 hook**（`session.hooks`），並提供 `detection.hook_probe` 讓塔台判斷注入是否開著；注入條件依 runtime 不同時，`hook_probe` 依 runtime 分開寫（§ 描述檔格式 › 欄位表 `detection`）。
2. 塔台派工前比對（`methodology_guard` 的行為**只定義在這一點**；V1 後定案，D342）：已安裝且注入開著的方法論（adapter `hook_probe` 判斷，
   或塔台偵測到注入）——
   - **不是**本單任何一層的負責者 → 依 `methodology_guard`：
     - `warn`（預設）：塔台**自動**在工單加 `### 方法論邊界`（範本的「不使用」變體），**列出所有**注入開著、且不負責本單任何一層的方法論（每家一項；V2b），
       派工摘要加一行提示（哪幾家、注入開著、已加邊界段、`always_on_tokens`）。沒有任何層由 adapter 負責、因此不寫 `methodology` 的工單也照加。不是只提示。
     - `block`：不派，請使用者關 hook 或改設定（給完全不想讓方法論碰 CT 工單的專案自選）。
     - `off`：不檢查、不自動加邊界段。
   - 是本單某一層的負責者 → 邊界段用範本的「只允許」變體（只列該層 workflow 用到的 skill）；adapter `required_when` 另有要求時一併寫。
     同時還有不負責本單的注入 → 「只允許」與「不使用」兩項都寫。
   - 兩家以上同時注入開著（雙注入）→ 至少照 `warn`（C10）：邊界段每一家都列，派工摘要另標一行「雙注入」（列出哪幾家）。
   - 邊界段範本只寫在 `work-order-template.md` 標準模板的 `### 方法論邊界`；塔台照抄，每家的值取自它的 adapter：方法論 skill 樣式 = `session.skill_patterns`、
     入口 skill 與注入條件摘要 = `session.hooks[].entry_skills`、`trigger_summary`、範圍外產物的例子 = 相關 adapter `artifacts.writes` 的聯集。
     注入開著但找不到 adapter 的方法論照樣列，值由塔台依偵測到的注入自行摘要（不貼原文），派工摘要標「無 adapter」。
     這類方法論沒有 `always_on_tokens` 可讀：派工摘要寫「`always_on_tokens` 未量測」，不填估值（Q-4，T0315）。要量時：在隔離設定目錄跑一次
     `claude -p --output-format stream-json --verbose`，看 `hook_response` 事件的注入內容長度（Codex：開工前的 developer 訊息），skill 描述另看
     `claude plugin details`；量到的數字寫進專案本地 adapter（§ 描述檔格式）再用。
3. 工單 `### 方法論邊界` 明寫「本單使用／不使用哪些方法論 skill」；有注入的方法論多半在注入文字裡寫「使用者指示（直接要求）優先」，這是它們文件化的覆寫管道。
   **V1 實測**（T0299，`spec/方法論介接/verification/V1-pstack-ct-exec.md`）：沒有邊界段時 2 次中 1 次在 Startup 與 Phase 1 之間進 `pstack:poteto-mode`，
   且回報區沒寫；有邊界段 3/3 沒呼叫，回報區主動聲明遵守。所以 `block` 不是預設，但邊界段要由塔台自動加、Worker 用了方法論一定要記。
   **V2a 實測**（T0307，Codex，`verification/V2a-pstack-codex-hooks.md`）：hook 信任後，沒有邊界段 2/2 進 poteto-mode（1 次回報區沒寫），有邊界段 2/2 擋住。
   **V2b 實測**（T0308，pstack＋Superpowers 雙注入，`verification/V2b-dual-injection.md`）：沒有邊界段 0/3 呼叫方法論 skill，兩家都列的邊界段 2/2 有效，
   並讓回報區主動寫 `### 方法論執行紀錄`。兩次都維持 `warn`、不升 `block`。
4. Worker 啟動時自查 context 是否有注入標記，記到回報區 `### 方法論執行紀錄` 的 `methodology_ambient` 行（V1 後改**必填**，仍不阻塞；格式與必填範圍見 § 工單欄位 ›
   `### 方法論執行紀錄` 的內容；Worker 規則見 `ct-exec/SKILL.md` § Methodology）。
5. **Codex 的 hook 信任**（V2a 後；hook 信任規則**只定義在這一點**）：
   - **塔台不替使用者信任 hook**：不寫 `config.toml` 的 `hooks.state`（`trusted_hash`）、不透過 `codex app-server` 代為寫入、不使用 `--dangerously-bypass-hook-trust`。
     理由：Codex 寫明信任後的 hook 可以在 sandbox 外執行；信任等於核准在 sandbox 外執行程式，屬於使用者的決定，不在塔台權限內。
   - codex Worker 派工前，依該 adapter 的 `hook_probe.codex` 判斷 hook 狀態：
     - `trusted`（且外掛啟用、注入沒有被 `off_switch` 關掉）→ 注入會到，照第 2 點的 `methodology_guard`（`warn` = 自動加邊界段；V2a：Codex 邊界段 2/2 有效）。
     - `untrusted`／`modified` → hook 不執行，但互動 TUI 會在開工前停在「Hooks need review」（BAT 派工表現為 exit `8`，處理照
       `auto-session.md` § Worker 啟動確認 第 4 點，不重派）。派工摘要提示使用者：先在自己的終端機開一次 `codex` 處理 review（信任，或選不信任繼續），
       或照 adapter `off_switch` 關掉注入（pstack：`pstack-models.md` 寫 `session hook: off`）。`modified` 要特別說明：方法論升版後，之前信任過的 hook
       會再要求 review 一次（推論）。使用者可能在 review 畫面選信任，所以邊界段照 `trusted` 一樣依第 2 點加。
     - 外掛停用 → 不注入，不用處理。
   - Codex 的注入在 context 裡是一則 developer 訊息（位置在使用者 prompt 之前），標記字串與 Claude Code 相同；Worker 自查照第 4 點。

## 引入方式

本節是方法論「引入方式」的**唯一權威定義**（D369）；C1、C10、adapter README 只引用本節。由重到輕三種：

| 方式 | 裝什麼 | adapter | 工單 | 塔台 `hook_probe`／`methodology_guard` |
|---|---|---|---|---|
| ① **完整安裝** | plugin／hook／skill 全裝（上游的標準安裝） | 完整宣告 `session.hooks`、`detection.hook_probe` | 照 § 解析步驟；注入開著時有邊界段 | `hook_probe` 判斷注入開著 → 照 § 與 hook／session 路由的相處規則 第 2 點（`warn` 自動加邊界段；兩家以上標「雙注入」） |
| ② **只引用 skill** | 不裝會常駐注入的 hook／plugin；只裝需要的 skill（例：上游的 skills-only 安裝），或以路徑讀 skill 檔 | 照常（`detection.probes` 要有 `kind: skill` 的 probe 認得這種安裝；例：pstack 的 `skills-only` probe，`hook_probe.install_without_hook: skills-only` 指出它代表沒有 hook） | 用到時在 `### 方法論邊界` 的【只允許】**指名** skill（以路徑讀時寫路徑） | 沒有注入 → `hook_probe` 判斷為關；這家不觸發【不使用】項與「雙注入」提示。負責本單某層時，邊界段照 adapter `required_when` 寫 |
| ③ **部分參考** | 精選 skill 的**本地副本**（鎖版、名稱加前綴、frontmatter `disable-model-invocation: true`，模型不會自己叫用），或只借鏡做法寫進工單步驟／專案準則（FIELDGUIDE、`_local-rules.md`） | 不需要；要讓塔台路由到本地副本時，寫專案本地 adapter（§ 描述檔格式）指到加了前綴的名稱 | 工單 `### 方法論邊界` 的【只允許】或執行步驟指名副本路徑（或直接寫做法）；沒有 adapter 時屬自由文字，不為副本寫 `methodology` 層；其他層照 § 解析步驟（例：執行層用副本、審查層照 `auto` 仍由 bmad 負責）。指名的副本用了照樣記入 `### 方法論執行紀錄`（G2；範圍見 `ct-exec/SKILL.md` § Methodology 的「方法論 skill」定義） | 沒有注入、塔台不偵測；guard 不觸發 |

**何時建議 ② 或 ③**：方法論**對 CT 使用者有效益、值得引入**，但它的 hook 會影響 CT——注入搶路由（C1）、多家注入疊加（C10）、常駐 token 成本（C14）——或上游沒有官方的關注入開關（C10），
或方法論**沒有 hook、靠 skill 描述讓模型自動叫用**（`hook_probe` 偵測不到，C1 ⑤）。這時 adapter README 與 `*onboard` 主題 5 的複述給出 ②／③ 的做法，不只寫「關 hook 或不用」；C1 ④、⑤ 的建議也指向這裡。
沒有效益的方法論不給 ②／③ 的建議，只照下方原則保留共存防護。

**方法論不是一定要引入**（D398）：只有實測或研究證明對 CT 使用者有效益時，CT 才給它 adapter、範例或引入建議；沒有效益的，CT 只保留「機器上已經裝了它時怎麼共存」的防護（C1、C5、C10），
不推薦、不做範例。下表的「建議」依各家在 CT 下的實測效益與成本（G 結論，D399、D400）。

| 方法論 | 建議 | 理由 |
|---|---|---|
| bmad（內建） | **引入**：①（內建、預設） | 核心不裝 harness hook（`adapters/bmad.yaml` `session.hooks: []`，推論）；opt-in 模組 `bmad-loop` 有自己的 hook，裝了另評估 |
| pstack（`ct-adapter-pstack`） | **選用**：已在用 pstack 才裝；CT 不預設、不主動推薦。裝了之後：當主方法論或負責某層用 ①（有官方關注入開關，邊界段實測有效）；只在個別工單借用某個 skill 用 ②（上游 skills-only） | 已在用 pstack 的使用者可抽換或分層（P1、P1b）；成本是沒有邊界段時注入會搶路由（C1）、常駐 token（C14）。見該 adapter README〈引入方式建議〉 |
| Superpowers（沒有 adapter） | **不建議引入**；已裝的機器照 C1、C5、C10 的共存防護 | 在 CT 下沒有實測效益：有邊界段時 0 次叫用（V2b、P1b、P3），沒有邊界段時 Worker 依 `ct-exec` 優先序第 ④ 項也不採用，HARD-GATE 0/3（C5）；成本是每個 session 常駐注入 3.4～7.9 KB、沒有官方的關注入開關（C10、C14）。注入開著時塔台照 § 與 hook／session 路由的相處規則 第 2 點以「無 adapter」列入邊界段 |
| mattpocock/skills（沒有 adapter；工具型 skill 集，MIT，<https://github.com/mattpocock/skills>） | ③，不建議標準 plugin 安裝；**可選用的做法範例，品質效益未實證** | 不是方法論（沒有編排與狀態），也沒有 hook：標準安裝後模型可自動叫用的 skill 靠描述觸發，塔台與 Worker 都可能被叫到，`hook_probe` 偵測不到（C1 ⑤）；③ 的機制已實測有效（見下方），但用它和不用它的品質差異沒有比較過；做法見下方 § ③ 的做法 |

- ③ **已實測**（P3，T0327，`spec/方法論介接/verification/P3-v6-beta2-option3-hardgate.md`）：mattpocock/skills 的 3 支本地副本（`mp-diagnosing-bugs`、`mp-tdd`、`mp-code-review`，加 `disable-model-invocation: true`）在塔台與 Worker 共 4 個 session 裡 0 次被模型自動叫用；塔台照本表把副本路徑寫進【只允許】；Worker 3/3 以路徑讀並照做、3/3 記入 `### 方法論執行紀錄`。同一份上游以標準 plugin 安裝（①）時，塔台開 bugfix 單 0/1 自動叫用（n=1，不代表不會發生）。Codex 端的 `policy.allow_implicit_invocation: false` 未實測。
- ② **未實測**（D369）；上表 ② 列的塔台行為是依規則推得。
- 引入方式是使用者在機器上的安裝選擇，塔台不替使用者改安裝；派工依實際偵測結果（`hook_probe`）判斷，不依「建議」判斷。
- adapter 描述檔不加「建議的引入方式」欄位（T0318 Step 4 評估：塔台派工與 `*onboard` 都不讀這個值）；建議寫在 adapter README。

### ③ 的做法（例：mattpocock/skills）

以 mattpocock/skills 為例寫出 ③ 的步驟（PLAN-002，`spec/方法論介接/PLAN-002-mattpocock-skills-research.md` § 9.3）；其他沒有 adapter 的工具型 skill 集照同一套做。
CT 不散布上游的任何檔案或原文，下列都是使用者在自己專案裡做的事。

1. **本地副本、鎖版**：從上游一個固定的 commit 把要用的 skill 複製到專案的 skill 目錄（例：`.claude/skills/mp-tdd/`），不裝標準 plugin（plugin 會自動更新，跑的版本和工單記的對不上）。
2. **名稱加前綴**：副本 frontmatter 的 `name` 加前綴（例：`mp-`）。上游不為避開 harness 內建指令而改名（例：`code-review` 與 Claude Code 內建指令同名），不加前綴可能叫到內建的那一個。
3. **關掉自動叫用**：副本 frontmatter 加 `disable-model-invocation: true`（Claude Code）；Codex 也要用時，同一個副本的 `agents/openai.yaml` 另寫 `policy.allow_implicit_invocation: false`。兩個 runtime 各看各的設定，只改一邊，另一邊仍會依描述自動叫用。
4. **改寫副本裡的外部前提**：叫其他上游 skill 的句子改成副本路徑或刪掉；以外部 issue tracker 為規格來源的前提改成「規格 = 本工單檔」。
5. **工單指名才用**：工單 `### 方法論邊界` 的【只允許】或執行步驟寫副本路徑（寫法見 `work-order-template.md` § 方法論邊界 的【只允許】例子）；Worker 用了照樣記入 `### 方法論執行紀錄`（G2，見 § 引入方式 表 ③ 列）。
   副本要問使用者或等核准的步驟，在邊界段逐條寫成 CT 的處理（例：寫進回報區不停下、改問塔台、回 `BLOCKED`）；通用條文仍保留。
   副本自己開的子代理照 `ct-exec/SKILL.md` § Workflow And Sub-Agents 記帳，邊界段寫「子代理只能唯讀」（C4）。
6. **記版本**：副本旁放一份紀錄（例：`VENDOR.md`：上游網址、commit、複製日期、本地改了什麼）。上游更新時另開工單比對，不自動同步。
7. **不放進 Worker 工單的 skill**：自建 worktree 或整合分支、自己開 PR（C6、C15）；以外部 issue tracker 為事實來源；開寫入型背景子代理（C4、C7）；整支都在問使用者（C5）。
   mattpocock/skills 對應的例子是 `implement-spec`、`to-spec`、`to-tickets`、`triage`、`wayfinder`、`implement`、`research`、`domain-modeling`（研究報告 § 5、§ 9.3）。

## 抽換（專案選主方法論）

設定鍵（扁平，沿用 `*config <選項> <值>` 的純量模型；G0 Q3）：

| 選項 | 有效值 | 預設 | 說明 |
|---|---|---|---|
| `methodology` | `auto` / `none` / `<adapter id>` | `auto` | 主方法論。`auto` = 偵測到 bmad adapter 可用（= bmad-guide 已安裝）就是 `bmad`，否則 `none`——**與 v5.12.6 Level 2 行為相同** |
| `methodology_planning` | `inherit` / `none` / `<adapter id>` | `inherit` | 規劃層；`inherit` = 跟主方法論 |
| `methodology_execution` | 同上 | `inherit` | 執行層 |
| `methodology_review` | 同上 | `inherit` | 審查層（G0 Q4：預設跟主方法論，疊加時派工摘要提示能力落差） |
| `methodology_verification` | 同上 | `inherit` | 驗證層 |
| `methodology_delivery` | `none` / `<adapter id>` | `none` | 交付層；預設不交給方法論 |
| `methodology_subagent_writes` | `deny` / `per-workorder` | `deny` | 方法論的寫入型子代理（§ 衝突與防護 C4；G0 Q5）。`per-workorder` 時塔台預設仍寫 `subagent_writes: deny`，工單有明確的〈方法論子代理授權〉段才寫 `authorized` |
| `methodology_guard` | `warn` / `block` / `off` | `warn` | 派工前的注入／衝突檢查；三個值的行為見 § 與 hook／session 路由的相處規則 第 2 點（G0 Q6；V1 後 D342） |
| `methodology_adapters_path` | 路徑 / 空 | 空 | 額外的 adapter 搜尋路徑（§ 散布與搜尋順序）。v1 只接受**一個**路徑；相對路徑以 **repo 根目錄**為基準 |

`auto`、`none`、`inherit` 是保留字，不會是 adapter id（§ 描述檔格式 › 欄位表 `id`）。

**疊加層級**：沿用既有的「session > project > global > 預設」與欄位級覆蓋（`tower-config.md`、`data-layer-architecture.md`）。
另加最高一層**工單覆寫**：使用者對單張工單指定方法論，塔台寫進該工單、不改設定檔。

**工單覆寫**（D336 G-1）有兩種說法：

| 使用者說 | 覆寫範圍 | 結果 |
|---|---|---|
| 「這張用 X 做」（整張覆寫） | 本單**每一層**（規劃、執行、審查、驗證） | 這四層都用 X，**蓋過** session／project／global 明寫的層設定（例：project 寫了 `methodology_planning: bmad`，這張的規劃層仍是 X） |
| 「這張 <層> 用 X」（指定層覆寫） | 只有該層 | 該層用 X；其他層照設定疊加 |

- 兩種可以並用（「這張用 X 做，審查用 Y」）：先套整張覆寫，再套指定層覆寫，所以指定的層以後者為準。
- **交付層不在整張覆寫內**：交付層預設不交給方法論（§ 層次），要開放必須明說「這張交付層用 X」。
- 被工單覆寫決定的層，`resolved_from.<層>` 記 `workorder`（§ 工單欄位）。
- 工單覆寫不碰 `methodology_subagent_writes`、`methodology_guard`、`methodology_adapters_path`；這三個鍵只從設定讀。

## 分層疊加（不同層用不同方法論）

1. **每層一個負責者（排他）**。同一張工單、同一層不能有兩個 adapter。
2. **同層衝突優先序**：① CT 核心規則 ＞ ② 工單明寫的方法論邊界 ＞ ③ 該層負責 adapter 的流程 ＞ ④ 其他已安裝方法論的常駐注入（對它不負責的層一律不採用）。
3. **跨層交接靠產物**：上一層 adapter 的 `handoff.produces` 要對得上下一層 adapter 的 `handoff.consumes`（`kind` 相同）；對不上 → 塔台派工時警告，退回 `goal-text`（把產物路徑當一般文件交給下一層）。
4. **回寫**：下一層執行完，上一層的狀態由**產生產物的 adapter** 的 `handoff.writeback` 決定（`by: worker-step` → 執行工單加回寫步驟，塔台 `*sync` 複查；沿用 `work-order-system.md` 的雙層保障）。
5. **審查用誰**：`methodology_review: inherit` 跟主方法論；換執行層會失去原方法論內建在執行流程裡的審查（例：bmad 的 Review Triage），派工摘要要提示（G0 Q4 已接受的取捨）。
6. **能力不足的層**：見 § 降級 最後一列。

## 解析步驟（塔台派工時）

```
1. 判斷 request_kind（§ 需求類型）
2. 讀設定：default → global → project → session，每個鍵取最高優先層的值（欄位級覆蓋），記下每個鍵的來源；
   再套工單覆寫（§ 抽換 › 工單覆寫）：整張覆寫 → 規劃～驗證四層都設為 X；指定層覆寫 → 該層設為 X（後套，優先）
3. methodology = auto → 偵測 bmad adapter；可用就是 bmad，否則 none
4. 對本單需要的每一層：
     owner = 該層設定（inherit → 主方法論）
     resolved_from.<層> = 該層值的來源（inherit → 主方法論的來源；工單覆寫 → workorder）
     owner 的 adapter 找不到、壞掉或未安裝 → § 降級
     entry = adapter.routing[request_kind][layer]；沒有 → § 降級（能力不足）
5. 收集所有已安裝 adapter 的 session.hooks + hook_probe → 套 methodology_guard（§ 與 hook／session 路由的相處規則 第 2 點；
   warn → 工單加 ### 方法論邊界，沒有任何層由 adapter 負責時也加）
6. 寫 frontmatter methodology（resolved_from 每層各記）、內文 ### 方法論工作流程、required_when 段落；
   subagent_writes 寫 deny，只有 methodology_subagent_writes = per-workorder 且本單有〈方法論子代理授權〉段時寫 authorized；
   把 adapter.artifacts.writes 放進 affects_files（或指定到 scratchpad）
7. 派工摘要加一行「方法論：<層> → <adapter>/<workflow>（版本、來源）」；有常駐注入時附 always_on_tokens
```

**何時解析**（D336 G-6）：

- 塔台**寫工單時**跑一次上面 1～6 步，結果寫進 frontmatter `methodology`。
- 已建立、**尚未派出**（`status: PENDING`）的工單，**派工前重新解析一次**：工單覆寫照原樣保留（`resolved_from.<層>: workorder` 的層不重算，
  覆寫內容以工單 frontmatter 為準），其他層依當下設定重算。結果與 frontmatter 不同 → 派工摘要列出差異（哪一層、舊值 → 新值、原因），
  以新值為準，同步更新 frontmatter `methodology` 與 `### 方法論工作流程`（`affects_files`、`required_when` 段落跟著新 adapter 調整）。
- **已派出的工單不變**：`IN_PROGRESS` 以後（含 Renew、重派）不重新解析，設定變更只影響之後派出的工單。
- 只有 `### BMad 工作流程` 舊段的舊工單不在此列（§ 舊欄位相容，不回寫）。寫工單時解析結果沒有任何層由 adapter 負責、
  所以沒寫 `methodology` 的 PENDING 工單照樣重新解析；新結果有層由 adapter 負責時補寫，並在派工摘要列出。

## 散布與搜尋順序

| 方式 | 位置 | 誰維護 |
|---|---|---|
| CT 內建 | `control-tower/references/adapters/<id>.yaml` | CT（目前只有 `bmad`） |
| 外部 skill | `ct-adapter-<id>/`，裝在 `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/`、`${CODEX_HOME:-~/.codex}/skills/` | adapter 作者（CT 官方或社群） |
| 專案本地 | `_ct-workorders/_adapters/<id>/` | 專案 |

**搜尋順序**：`methodology_adapters_path` > 專案 `_ct-workorders/_adapters/` > 外部 skill `ct-adapter-*` > CT 內建。
同 `id` 取第一個找到的，派工摘要標出來源；專案可以用同 `id` 覆寫內建 bmad。

**`methodology_adapters_path`**（D336 G-4）：v1 只接受**一個**路徑（不接受清單或分隔符串接的多個路徑）。相對路徑以 **repo 根目錄**
（`git rev-parse --show-toplevel`）為基準，不是 `_ct-workorders/`、也不是設定檔所在目錄；絕對路徑照用。

指到的目錄**與專案本地 `_ct-workorders/_adapters/` 同結構**（T0306）：

```
<methodology_adapters_path>/
└── <id>/
    ├── adapter.yaml       # id = 目錄名
    └── README.md
```

- 不是 `ct-adapter-<id>/` 的 skill 結構：外部 skill 一律裝在 skills 目錄，由「外部 skill」那一層搜尋。
- 描述檔照專案本地處理：`maintainer.kind: project-local`，`id` = 目錄名；`validate-adapter.py` 用 `--source project-local` 檢查
  （目錄名不是 `_adapters` 時，腳本的 `auto` 認不得來源）。

| adapter | 同步規則 |
|---|---|
| bmad（內建） | bmad-guide 更版時同一輪檢查 `adapters/bmad.yaml`（`tested_version`、`retired_names`、`routing`；`maintainer.sync_rule`）；不一致時以 bmad-guide 為準（§ 未來介接 › 有 guide 的方法論） |
| 外部 skill | 上游版本超出 `version_range` 時重驗；不跟 CT 版號綁 |
| 專案本地 | 專案自行決定 |

## 未來介接（新方法論要不要配 guide skill）

新增 adapter 的步驟與檢查見 § 描述檔格式、§ 新 adapter 的最小檢查、§ 散布與搜尋順序。本節只定一件事：除了 adapter，要不要另外配一個
**guide skill**（像 bmad 的 `bmad-guide`：教學、細路由、名稱與版本對照的獨立 skill）。

**何時配 guide skill**（D336）：方法論符合下列**任一**才配；都不符合 → CT 需要的資訊全部放 `ct-adapter-<id>`（描述檔＋README＋說明用的 `SKILL.md`），不另做 guide。

1. 沒有自帶路由，或自帶的路由不認版本（不知道哪個版本有哪些 skill、該叫哪個）
2. 多階段，且要依產物狀態選下一步（例：有沒有 PRD、story 狀態到哪了）
3. skill 改名／退役頻繁，需要一個地方持續維護對照
4. 需要在地化教學（給使用者看的中文說明、學習路徑）

**有 guide 的方法論**：

- **名稱與細路由以 guide 為準**。adapter 描述檔（`upstream.guide` 記 guide skill）是標明 `tested_version` 的**快照**，只放 CT 派工需要的對照。
- 兩者不一致（例：adapter 的 workflow 名在 guide 已改名或退役、guide 的版本已超過 `tested_version`）→ 路由照 guide，派工摘要提示更新 adapter；
  adapter 在下一個 CT 版號跟上（內建 bmad：LR-003 同輪檢查，`maintainer.sync_rule`）。

| 方法論 | guide | 理由 |
|---|---|---|
| bmad | ✅ `bmad-guide` | 符合 1～4：名稱隨 BMad-Method 版本變動、依產物狀態選下一步、退役名多、提供中文教學 |
| pstack | ❌（反例） | 自帶 `poteto-mode` 路由與 playbook，改版快；CT 需要的資訊都在 `ct-adapter-pstack` |

## 衝突與防護

規則面；各方法論的出處與實測證據見 PLAN § 6。

| ID | 衝突 | 偵測 | 處置 |
|---|---|---|---|
| **C1** | SessionStart 注入搶路由（Worker 分頁一開就被導向某個方法論入口；**塔台 session 也會收到同一段注入**） | 塔台：adapter `hook_probe`；Worker：自查 context 注入標記（`methodology_ambient`） | ① 工單 `### 方法論邊界` 明寫用哪些 skill；② `methodology_guard: warn`（預設）= 塔台派工時**自動加邊界段**＋派工摘要提示，`block` 留給使用者自選（行為見 § 與 hook／session 路由的相處規則 第 2 點）；③ Worker 呼叫任何方法論 skill 都記入 `### 方法論執行紀錄`、`methodology_ambient` 必填（`ct-exec/SKILL.md` § Methodology）；④ 建議使用者在 CT 管理的機器上關掉該方法論的注入，或改用 § 引入方式 的 ②（只引用 skill）／③（部分參考）；⑤ **沒有 hook、靠 skill 描述讓模型自動叫用的第三方 skill**（G1，PLAN-002；例：mattpocock/skills 的標準安裝）也會搶路由，塔台 session 也可能被叫到（P3 M1：標準安裝、塔台開 bugfix 單 0/1，n=1），而且沒有注入可偵測：`hook_probe` 判斷為關、guard 不觸發、`methodology_ambient` 也看不到。這類方法論在 CT 管理的機器上建議用 ②（以路徑讀 skill 檔）或 ③（副本加 `disable-model-invocation: true`），不做會讓模型自動叫用的標準安裝（§ 引入方式）；要不要擴充 guard 偵測已安裝的模型可叫用 skill 留待 6.x（要動契約）。V1（T0299）：無邊界段 1/2 進 `pstack:poteto-mode` 且回報區沒寫、有邊界段 3/3 有效 → 維持 `warn`、不升 `block`（D342）。V2a（T0307，Codex）：未信任的 hook 不執行；信任後無邊界段 2/2 進 poteto-mode、有邊界段 2/2 有效。V2b（T0308）：Superpowers 的注入也送達並進 context；雙注入無邊界段 0/3、只有 Superpowers 0/1 呼叫 skill |
| C2 | 指令撞名（例：`/loop`） | adapter `session.name_collisions` | `vocabulary` 區隔；ct-exec 內不用方法論的自動循環，工單之間的循環由 CT 派工／Renew 取代 |
| C3 | 「playbook」撞詞 | adapter `vocabulary` | CT 文件一律寫「CT Playbook」（工單序列）；方法論的 playbook（工單內步驟）加方法論前綴；`*evolve` 不把方法論的 playbook 目錄當 CT Playbook 晉升 |
| **C4** | 方法論的子代理 vs CT「寫入集中在主 Worker」 | adapter `session.subagents.writes`；工單 `methodology.subagent_writes` | 預設 `deny`：工單寫「子代理只能唯讀」。`methodology_subagent_writes: per-workorder` 時塔台預設仍寫 `deny`，只有工單有明確的〈方法論子代理授權〉段才寫 `authorized`（D336 G-5）。要開放 → 工單加「**方法論子代理授權**」段（比照 `Workflow 使用授權`：列出 adapter、用途、上限、能不能 commit；worktree 一律走 BAT `--isolation worktree`，不用方法論自建的 worktree）。這不是 Workflow 工具，R1–R5 不直接套用，但 R3／R4 的理由（BAT 看不到自建 worktree、寫入要對得上 `affects_files`）同樣成立。Worker 怎麼照授權執行、超出時停、回報什麼：`ct-exec/SKILL.md` § Methodology › 方法論子代理。V1：8 次未出現寫入型子代理 |
| C5 | 方法論要問使用者 vs yolo | adapter `worker.asks_user` | yolo：方法論要問的題改問塔台（ct-exec § Questions For Tower）；有硬閘門的規劃層建議由塔台先對齊再派，或該層不用 yolo。邊界段範本有一條通用條文：方法論 skill 要求先問使用者或等核准時不得因此停下，照 ct-exec 規則處理（V2b 後，預防措施）。V2b：6 次都沒觸發會問使用者的 skill。P1b（T0315，`verification/P1b-v6-pre1-pstack-combos.md` § 5.4）：工單有 `methodology.layers` 時，Worker 依 `ct-exec` 優先序第 ④ 項不採用不負責本單的注入，拿掉邊界段也 0/1 叫 `superpowers:brainstorming` → Superpowers HARD-GATE 在 v6 正常流程下幾乎不會出現（推論）。P3（T0327，`verification/P3-v6-beta2-option3-hardgate.md` § 5.6）：`methodology_guard: off`＋`methodology: none`（工單沒有 `methodology`、沒有邊界段）、`CT_MODE=yolo`、Superpowers 注入送達，2/2 仍 0 次叫 `superpowers:brainstorming`、沒停下、沒提問——Worker 依 `ct-exec` 優先序第 ④ 項不採用不負責任何層的注入，並指出 brainstorming 的核准閘門與 yolo 衝突（其中 1 張是需求只有一句、介面由 Worker 設計的工單）。結論：沒有指名 Superpowers 的工單，Worker 在 headless／yolo 下不會被 HARD-GATE 擋住（n=2）；工單在邊界段或執行步驟**明確指名** `superpowers:brainstorming`（§ 引入方式 ②／③）時的硬閘門表現**仍未實測** |
| C6 | 方法論自己動 git（開分支、worktree、commit、merge、push、PR、`reset --hard`） | adapter `ct_overrides`、`artifacts` | ct-exec 規則不變：不切分支、不 push（除非工單授權）；交付層預設 `none`（Worker 端：`ct-exec/SKILL.md` § Methodology › 交付層）；隔離一律走 BAT worktree；邊界段明寫不開分支、不 push，不依賴工單剛好寫了。V1：8 次未出現；進 poteto-mode 那次因工單明寫不開分支、不 push 而跳過委派與 PR |
| C7 | `affects_files` 外的產物 | adapter `artifacts.writes` | 塔台開單時把 `artifacts.writes` 放進 `affects_files`，或在邊界段指定放 Worker scratchpad（沒有 scratchpad 時用系統暫存目錄下的 `ct-<工單號>/`、收尾刪除，repo 外不留檔；措辭見邊界段範本。P1 實測 1 次寫到 repo 上一層，P-4）；收尾 `git status` 必須乾淨（ct-exec 既有規則） |
| C8 | 回報格式與語言 | — | 回報區照 CT 模板與工單語言；方法論的寫作風格規則只用在產品文字（`ct_overrides`）。V1：unslop 只影響最後的聊天訊息，回報區未受影響。**塔台 session 也會收到注入**：塔台對使用者的對話語言不因注入改變（`control-tower/SKILL.md` 語言規則）。P1（T0314）：pstack 注入開著的塔台輪次 2 次改用英文；P1b（T0315）5 輪都是中文，合計 n=2／7，成因（注入或 session 狀態）是推論 |
| C9 | compact 後重注入 | 同 C1 | V1 實測：compact 與 resume 都重新注入；compact 後邊界仍有效（n=1），但靠的是 compact 摘要，Worker 沒有先重讀工單 → ct-exec 加通用規則「compact／resume 後先重讀工單再繼續」（`ct-exec/SKILL.md` § Startup），邊界段也寫這一條 |
| C10 | 多家注入疊加 | 塔台：多個 `hook_probe` 同時為開 | 兩個以上注入一律至少 `warn`：`warn` = 自動加邊界段，列出所有注入開著、且不負責本單的方法論，派工摘要標「雙注入」（§ 與 hook／session 路由的相處規則 第 2 點）。建議（不強制）一台機器只開一家注入；其他家改用 § 引入方式 的 ②／③（Superpowers 沒有官方的關注入開關，在 CT 下也沒有實測效益：§ 引入方式 不建議引入，已裝的機器照本列與 C1、C5 共存）。V2b（T0308）：兩段注入都送達；雙注入無邊界段 0/3 呼叫 skill、只有 Superpowers 0/1；兩家都列的邊界段 2/2 有效並主動入回報區 → 維持「至少 `warn`」、不升 `block` |
| C11 | ID 撞號（方法論自己的 task ID vs CT `T####`） | — | 文件與回報區把方法論 ID 加前綴（`<id>:<原 ID>`）；`ct-status` 只掃 `_ct-workorders/` |
| C12 | 規則來源重疊（方法論的 constitution／include vs CT FIELDGUIDE） | adapter `artifacts.user_config` | 衝突時以工單／使用者指示為準，列入 followups |
| C13 | 「workflow」一詞多義 | — | 工單段名用「方法論工作流程」；Workflow 工具維持「Workflow 使用授權」（`workflow-engine.md`） |
| C14 | 常駐 token 成本 | adapter `session.always_on_tokens` | 列在派工摘要的方法論行。`always_on_tokens` 要含 hook 實測注入量（直接執行 hook 或看 stream-json 的 `hook_response`）：`claude plugin details` 對 hook 寫「no model context cost」，只抄它會低估（V2b；pstack 注入 Claude Code 998 bytes、Codex 996 bytes）。沒有 adapter 的注入方法論寫「未量測」，不填估值（量法見 § 與 hook／session 路由的相處規則 第 2 點；Q-4） |
| C15 | 方法論自己開 issue／PR 處理缺陷 | — | 範圍守衛照 ct-exec；寫進 followups，由塔台開 BUG／工單 |
| C16 | 方法論的單一 active 指標 vs 平行 Worker | — | adapter `invoke` 要求每單指定獨立的指標（例：每單設定的環境變數） |

## 版本歷史

- v6.0.0-pre.1：本檔建立（T0300；G0 D332）。預覽，未發布。
- v6.0.0-pre.1（T0304，D336、D337）：補工單覆寫的整張／指定層（G-1）、`resolved_from` 每層各記（G-2）、保留字（G-3）、
  `methodology_adapters_path` 基準（G-4）、`per-workorder` 預設 `deny`（G-5）、PENDING 工單派工前重新解析（G-6）、
  由 workflow 推得的層、§ 未來介接（何時配 guide skill）；欄位表補選填欄位、`retired_names.note`、明確缺席 `{}`、`kind` 建議值；
  〈預覽版實作狀態〉工單模板、設定鍵、外部 adapter 與驗證腳本三列 ✅。
- v6.0.0-pre.1（T0306，D342、D339）：V1 結果落地——`methodology_guard: warn` 改成塔台自動加 `### 方法論邊界`（§ 與 hook／session 路由的相處規則 第 2 點）、
  `methodology_ambient` 必填與 `### 方法論執行紀錄` 的內容（§ 工單欄位）、C1／C4／C6／C8／C9 補 V1 結果；§ Worker 帶入 改引用 `ct-exec`；
  `methodology_adapters_path` 指到的目錄結構（§ 散布與搜尋順序）；〈預覽版實作狀態〉Worker 端列 ✅。
- v6.0.0-pre.1（T0309，D345、D346）：V2 結果落地——§ 與 hook／session 路由的相處規則 第 5 點（Codex hook 信任：塔台不替使用者信任、派工前依 hook 狀態提示）、
  第 2 點 `warn` 列出所有注入開著的非負責方法論、「雙注入」提示、邊界段的值取自 adapter；欄位表 `detection.hook_probe` 依 runtime 分開、`session` 選填
  `skill_patterns`、`hooks[].entry_skills`、`hooks[].trigger_summary`；C1／C5／C10／C14 補 V2a、V2b 結果。
- P2 修補（T0318，D376、D377；併入 6.0.0-beta.1，版號由 PLAN-001 P3 改）：新 § 引入方式（D369，C1 ④、C10 改引用）；內文段落 `### 方法論狀態回寫` 在沒有層由 adapter 負責時也保留（P-1）；
  C1／C8 塔台 session 也收到注入（P-2）；`~/.claude`／`~/.codex` 改 `${CLAUDE_CONFIG_DIR:-~/.claude}`／`${CODEX_HOME:-~/.codex}`（P-3）；C7 scratchpad 退路（P-4）；
  `methodology_ambient` 錯誤寫法對照（P-5）；子代理內呼叫的 skill 要列（Q-1）；C5 補 P1b 證據與觸發條件（Q-3）；無 adapter 的 `always_on_tokens` 寫「未量測」（Q-4）。契約仍 `ct-methodology-adapter/v1`、不加欄位。
- v6.0.0-beta.1（T0319，PLAN-001 P3）：版號定稿、預覽標示改 Beta（與穩定版 5.12.7 並行、不取代）；規則不變。
- B1 修補（T0325，PLAN-002 [B]、D392；併入 6.0.0-beta.2，版號由 PLAN-003 B2 改）：§ 引入方式 建議表加 mattpocock/skills（③）、新 § ③ 的做法；C1 ⑤ 沒有 hook、靠描述觸發的 skill（G1）；
  ③ 列與 § 工單欄位 改引用 `ct-exec` 的「方法論 skill」定義，範圍擴到工單指名的 skill（含 ③ 本地副本，G2）。契約仍 `ct-methodology-adapter/v1`、不加欄位。
- v6.0.0-beta.2（T0328，PLAN-003 B2；G 結論 D398～D400）：§ 引入方式 加「方法論不是一定要引入」原則與各家定位（bmad 引入、pstack 選用、Superpowers 不建議引入只留共存防護、mattpocock 可選範例且品質效益未實證）；表下第 1 點改成 ③ 已實測、② 未實測（P3，T0327）；③ 列補「部分層用 ③ 時其他層照解析步驟」；§ ③ 的做法 第 5 點補副本要問使用者的步驟在邊界段逐條對照；C1 ⑤ 改「也可能被叫到」（n=1）；C5 依 P3 改寫；C10 的 Superpowers 改共存說法；版號定稿（與穩定版 5.12.8 並行）。契約仍 `ct-methodology-adapter/v1`、不加欄位。
- v6.0.0-beta.3（T0336；規範修改 T0332）：版號定稿（與穩定版 5.13.0 並行）；本檔與方法論轉接規則不變（本版改動在狀態衛生與 BAT 塔台面板讀取契約）。契約仍 `ct-methodology-adapter/v1`、不加欄位；`ct-adapter-pstack` 內容未改，`adapter_version` 仍 0.2.4。
- v6.0.0-beta.4（T0344；規範修改 T0342）：版號定稿（與穩定版 5.13.1 並行）；本檔與方法論轉接規則不變（本版改動在通知用工單完整 ID 與 BAT 塔台面板讀取契約）。契約仍 `ct-methodology-adapter/v1`、不加欄位；`ct-adapter-pstack` 內容未改，`adapter_version` 仍 0.2.4。
- v6.0.0-beta.5（T0355；規範修改 T0354）：版號定稿（與穩定版 5.14.0 並行）；本檔與方法論轉接規則不變（本版改動在 plugin 安裝就緒：寫入規則、§ 路徑解析、安裝方式與呼叫字串）。契約仍 `ct-methodology-adapter/v1`、不加欄位；`ct-adapter-pstack` 內容未改，`adapter_version` 仍 0.2.4。
- v6.0.0-beta.6（T0366；規範修改 T0365）：版號定稿（與穩定版 5.14.2 並行）；新 § 描述檔格式 › probe 怎麼解析 skill 根目錄（依列出順序第一個成功的 probe 決定 skill 根目錄與版本、手動優先；`kind: plugin` 的安裝根目錄；`<plugin>@*`；只讀），probe 新增選填子欄位 `skill_root`（欄位表 `detection`、routing `reference`、§ 新 adapter 的最小檢查 同步；`validate-adapter.py` M8）；§ 降級 新列「已安裝但讀不到 → 提示一次」；內建 `adapters/bmad.yaml` 加兩個 plugin probe。契約仍 `ct-methodology-adapter/v1`、頂層欄位不變；`ct-adapter-pstack` `adapter_version` 0.2.5（Claude probe 的 `search`、`pinned_ref`）。
- v6.0.0-beta.7（T0371）：版號定稿（與穩定版 5.14.3 並行）；**契約不變**（本檔、`adapters/bmad.yaml` 與方法論轉接規則都沒有改；本版改動是移植穩定版 5.14.3 的〈巢狀的獨立 repo〉配置文件，見 `mono-repo-patterns.md`）。`ct-adapter-pstack` 內容不變，`adapter_version` 仍 0.2.5。
- v6.0.0-beta.8（T0377）：版號定稿（與穩定版 5.14.4 並行）；**契約不變、新增選填 `runtime`**：probe 新增選填子欄位 `runtime`（欄位表 `detection`、§ 新 adapter 的最小檢查 同步；`validate-adapter.py` M8），§ 描述檔格式 › probe 怎麼解析 skill 根目錄 第 1 點改成依 runtime（本 runtime 的 probe 與沒寫 `runtime` 的 probe 依列出順序 → 另一個 runtime 的 probe 只當讀檔來源；手動優先限同一個 runtime 內），第 3 點 Claude plugin 清單只有一處（刪掉「設了 `CLAUDE_CONFIG_DIR` 時兩處都算」）。契約仍 `ct-methodology-adapter/v1`、頂層欄位不變，probe 都沒寫 `runtime` 的 adapter 行為不變；內建 `adapters/bmad.yaml` `adapter_version` 0.2.1（`guide-skill` 拆成兩個、四個 probe 標 `runtime`），`ct-adapter-pstack` `adapter_version` 0.2.6。
- v6.0.0-beta.9（T0387）：版號定稿（與穩定版 5.15.0 並行）；**契約不變**（本檔、`adapters/bmad.yaml` 與方法論轉接規則都沒有改；本版改動是移植穩定版 5.15.0 的 yolo 提問流程，見 `yolo-mode.md` § Worker 向塔台提問、§ 斷點 A）。`bmad.yaml` 只改版號註解（`adapter_version` 仍 0.2.1）；`ct-adapter-pstack` 內容不變，`adapter_version` 仍 0.2.6。
- v6.0.0-beta.10（T0396；規範修改 T0393～T0395）：版號定稿（與穩定版 5.15.0 並行）；**契約不變**（adapter 描述檔格式、層次、解析與降級規則都沒有改）。§ 舊欄位相容 的 ECC observation 列改為「ECC Level 1 退場、CT 不再寫 observation，`legacy.observation_key` 只留作識別舊紀錄」；內建 `adapters/bmad.yaml` 只改該欄位的註解與版號註解（`adapter_version` 仍 0.2.1）；`ct-adapter-pstack` 內容不變，`adapter_version` 仍 0.2.6。
- v6.0.0-beta.11（T0409；規範修改 T0405、T0399）：版號定稿（與穩定版 5.15.0 並行）；**契約不變**（本檔、`adapters/bmad.yaml` 與方法論轉接規則都沒有改；本版改動是執行中補充工單與小項）；內建 `adapters/bmad.yaml` 只改版號註解（`adapter_version` 仍 0.2.1）；`ct-adapter-pstack` 內容不變，`adapter_version` 仍 0.2.6。
- v6.0.0-beta.12（T0424；規範修改 T0422、T0423）：版號定稿（與穩定版 5.15.0 並行）；**契約不變**（本檔、`adapters/bmad.yaml` 與方法論轉接規則都沒有改；本版改動是 ct-insights 的工具清單建議 `*insights tools`）；內建 `adapters/bmad.yaml` 只改版號註解（`adapter_version` 仍 0.2.1）；`ct-adapter-pstack` 內容不變，`adapter_version` 仍 0.2.6。
- v6.0.0-rc.1（T0428；修正 T0427）：版號定稿（RC，正式版候選，與穩定版 5.15.0 並行）；**契約不變**（本檔、`adapters/bmad.yaml` 與方法論轉接規則都沒有改；本版只有修正：Worker 塔台補充檢查的寫法與 `analysis-rules.md` 的 JSON 欄位清單）；檔頭標示改 RC；內建 `adapters/bmad.yaml` 只改註解（`adapter_version` 仍 0.2.1）；`ct-adapter-pstack` 內容不變，`adapter_version` 仍 0.2.6。
- v6.0.0（T0464）：正式版（取代 5.15.0 成為穩定版）；**契約不變**（本檔、`adapters/bmad.yaml` 與方法論轉接規則都沒有改）；檔頭標示改正式版；內建 `adapters/bmad.yaml` 只改註解（`adapter_version` 仍 0.2.1）；`ct-adapter-pstack` 只改版號與標示，`adapter_version` 仍 0.2.6。
