# RC：方法論轉接（v6.0.0-rc.1）

> 📌 **本章內容已納入正式版 6.0.0，保留作為預發行期間的歷史參考。** CT v6.0.0（2026-11-07）是 v6 系列的第一個正式版，取代 5.15.0 成為穩定版；
> 本章寫的方法論轉接與 beta.1～rc.1 的各項 v6 功能，6.0.0 起都屬於正式版。下面的 Beta／RC 標示，以及「只打包、不取代穩定版」「預發行版不提供 plugin」「沒問題就發正式版」等說法，
> 是 **6.0.0 以前**的狀態：6.0.0 的下載在 GitHub Release `ct-v6.0.0`（Latest），CT plugin 6.0.0 起上架 marketplace（預發行版 beta、rc 仍不提供）。本章的檔名與段落錨點不改。
> **正式章節**：方法論轉接的簡述在 `integration.md` § 方法論轉接（v6.0.0+）；Worker 端在 `work-order-lifecycle.md` § 方法論（v6.0.0+）；設定鍵在 `ecosystem.md` § 設定系統；
> session 用量統計與工具清單建議在 `advanced-patterns.md`（ct-insights）；執行中補充工單在 `work-order-lifecycle.md` § Worker Renew 機制。
> 本章保留各功能的設計理由、實測證據與每個預發行版改了什麼；6.0.0 本身見 § 6.0.0：納入正式版。
>
> 🧪 **RC（正式版候選），與穩定版 5.15.0 並行。** 本章寫的是 CT v6.0.0-rc.1：方法論轉接（methodology adapter）、三種引入方式與各家定位、`_tower-state.md` 機器可讀摘要，
> 以及隔離試用之後的修補。v6 的 Beta 與 RC 都是預發行，RC 一樣**只打包、不安裝**，不取代穩定版：首頁、`/install` 與更版紀錄的下載仍是 5.15.0，
> RC 的下載在 GitHub 預發行 Release `ct-v6.0.0-rc.1`（不是 Latest）。RC 期間功能凍結、只修錯，沒問題就發正式版 6.0.0。回答時先告訴使用者這一點。
>
> beta.1 是 v6.0.0-pre.1（預覽）在隔離環境實測後修補、定稿的版本；beta.2 是「方法論引入的結論版」：哪些方法論值得引入、怎麼引入，
> 不引入的方法論怎麼共存。本章沿用 beta.1 的專章，補上 beta.2 的變更：§ 方法論不是一定要引入、§ 在 CT 專案使用 mattpocock/skills、
> § 實測 P3、§ 引入方式 的實測狀態（③ 已實測）、§ 環境偵測只列名稱 的新寫法。
>
> beta.3 是「狀態衛生與 BAT 塔台面板讀取契約」版，方法論的部分沒有改。**同批規則穩定版 5.13.0 也有**，所以寫在主教材各章，
> 本章只在 § beta.3：狀態衛生與 BAT 塔台面板讀取契約 指向它們。
>
> beta.4 是「通知用完整工單 ID 與 BAT 塔台面板讀取契約（對齊 BAT `0.7.1-pre.9`）」版，方法論的部分也沒有改。**同批規則穩定版 5.13.1 也有**，
> 所以同樣寫在主教材各章，本章只在 § beta.4：通知用完整工單 ID 與 BAT 塔台面板讀取契約 指向它們；〈已知未驗〉當時更新為 15 項。
>
> beta.5 是「plugin 安裝就緒」版，方法論的部分也沒有改。**同批規則穩定版 5.14.0 也有**，所以同樣寫在主教材各章，
> 本章只在 § beta.5：plugin 安裝就緒 指向它們；〈已知未驗〉當時更新為 16 項。
> **beta 沒有 plugin，不要用 marketplace 裝 beta**：marketplace 只上架穩定版，beta 照舊用 zip 手動安裝；在 beta 環境執行 plugin 安裝指令，
> 裝到的是穩定版 5.x，會和手動安裝的 beta 並存。
>
> beta.6 移植穩定版 5.14.1、5.14.2，並讓方法論 adapter 偵測得到 plugin 安裝的方法論 skill。**移植的規則穩定版 5.14.1／5.14.2 也有**，寫在主教材各章；
> 只有 adapter 的部分（probe 怎麼解析 skill 根目錄、`skill_root`、`bmad.yaml` 兩個 plugin probe、已安裝卻讀不到時提示一次）是 v6 才有，
> 寫在 § beta.6：移植 5.14.1／5.14.2、adapter 偵測 plugin；〈已知未驗〉當時更新為 19 項。
> beta 仍沒有 CT plugin，但 **bmad-guide 不跟 CT 版號**：beta 使用者可以從穩定 marketplace 只裝 `bmad-guide`，beta.6 的塔台偵測得到它（plugin probe 當時尚未實機驗證，beta.8 前已驗）。
>
> beta.7 只移植穩定版 5.14.3 的「一個塔台、多個巢狀的獨立 repo」配置文件，方法論的部分沒有改。**這份文件穩定版 5.14.3 也有**，寫在主教材 `advanced-patterns.md`，
> 本章只在 § beta.7：移植 5.14.3（巢狀的獨立 repo） 指向它；〈已知未驗〉當時更新為 20 項。
>
> beta.8 移植穩定版 5.14.4：塔台找方法論 skill 時先找自己這個 runtime 的安裝，另一個 runtime 的只當讀檔來源；Claude plugin 的位置只有一處。
> **移植的規則穩定版 5.14.4 也有**，寫在主教材 `integration.md` § 偵測與降級、`three-layer-arch.md` § plugin 安裝路徑也是 Layer 1；
> 只有 probe 的選填欄位 `runtime` 與 `bmad.yaml`、`ct-adapter-pstack` 的 probe 改法是 v6 才有，寫在 § beta.8：移植 5.14.4、probe 依 runtime；
> 〈已知未驗〉當時更新為 19 項（beta.7 的第 16、17 項已實機驗證、移除，新增第 19 項）。
>
> beta.9 移植穩定版 5.15.0：yolo 模式下 Worker 一次問多題時塔台只被叫醒一次、同一批的重複通知不再重複提醒你，並一併修正兩個原本就有的問題
> （多題時先問的題可能還沒等到答覆就過期、兩則通知黏在一起時誤觸斷點 A）。方法論的部分沒有改。
> **移植的規則穩定版 5.15.0 也有**，寫在主教材 `work-order-lifecycle.md`（〈一批只叫醒塔台一次〉）、`runtime-dispatch.md` § 斷點，
> 本章只在 § beta.9：移植 5.15.0（一批提問只叫醒塔台一次） 指向它們；〈已知未驗〉當時更新為 23 項（新增第 20～23 項）。
>
> beta.10 的改動都是 v6 才有的（穩定版 5.15.0 沒有）：token 用量統計（`*insights sessions`、工單 `session_ids`、塔台記自己的 session id、收單補記與快照），
> 統計產生的候選事實接進既有學習流程（`ct-evolve --facts-from`），以及外部增強外掛治理——ECC Level 1 退場、mem0 Level 3 保留但要在本地規則記錄例外才啟用；
> 另修正 Codex skill 掃描器（已實測會遞迴）、手動安裝 skill 的移除、helper 輸出的前導空白。寫在 § beta.10：session 用量統計（PLAN-004 ⑥）、
> § beta.10：session 證據怎麼進學習流程（PLAN-004 ⑦）、§ beta.10：ECC Level 1 退場；〈已知未驗〉當時更新為 33 項（beta.9 的第 20、22、23 項已實機驗證、移除，
> 第 21 項縮小成新的第 20 項，新增第 21～33 項）。
>
> beta.11 的改動也都只在 v6：塔台能在 Worker 還在跑的時候往工單寫〈塔台補充（執行中 #N）〉，Worker（`ct-exec`，以及 `ct-done` 寫回報前）在三個固定節點看一次段落標題、自己讀到新段落；
> Claude Code 塔台可選用跨 session 訊息提醒自己的 Worker；另補 `ct-help` 的 session 命令說明、BAT 下不放 `--settings` 的第二個理由與 BAT 待送通知。
> 寫在 § beta.11：Worker 執行中接收塔台補充；〈已知未驗〉當時更新為 36 項（第 1～33 項照舊，新增第 34～36 項；隔離工單、yolo 衝突提問、跨 session 提醒、Codex 節點檢查已在安裝後以實際 BAT 派工驗過）。
>
> beta.12 的改動也都只在 v6：新命令 `*insights tools` 用本機 Claude Code session 紀錄找出一直載入、卻很少或從來沒用到的 skill、plugin、MCP server、agent 類型與內建工具，
> 依工單類型分組、各項標層級與設定鍵，**只建議、不改設定**，核心內建工具一律保留；`*insights sessions` 也計 slash command 與 agent 類型（快照 `0.2`）；另加打包檢查（description 不得含角括號）。
> 寫在 § beta.12：工具清單建議；〈已知未驗〉當時更新為 42 項（第 1～36 項照舊，新增第 37～42 項）。
>
> rc.1 是**正式版候選**：beta 回饋期結束，**功能凍結、只修錯**，RC 期間沒有發現要修的問題就發正式版 6.0.0。本版相對 beta.12 只有修正：Worker 讀塔台補充的三個節點寫法一致
> （`ct-exec` 驗證前那一次改成驗證段落的第 1 步、`ct-done` 寫回報前那一次改成先寫）、`ct-insights` 的 JSON 欄位文件補齊、本教材的 pstack adapter 版號改成 0.2.6；沒有新功能、設定或命令。
> 寫在 § rc.1：正式版候選（只修錯）；〈已知未驗〉更新為 41 項（beta.12 的第 22 項已實測、移除，第 21、28 項只留還沒驗的部分）。本章的檔名與段落錨點沿用 Beta 時的名稱。
>
> 本章跟其他章一樣是**教科書**：講概念與「為什麼這樣設計」。欄位、鍵值、範本、訊息格式一律以 CT 權威檔為準，
> 本章只寫檔名與章節名，不複述規則全文。要照著做的確切寫法，指向 `ct-help` § Methodology Adapters (v6.0.0+) 或下表的權威檔。

| 主題 | CT 權威定義 |
|------|------------|
| 方法論轉接契約（adapter 格式、層、抽換、疊加、解析、降級、衝突） | `control-tower/references/methodology-adapters.md`（全檔；本檔自稱唯一權威） |
| 「方法論不是一定要引入」原則與各家定位 | `methodology-adapters.md` § 引入方式（原則段與建議表） |
| 三種引入方式 | `methodology-adapters.md` § 引入方式；pstack 的建議：`ct-adapter-pstack/README.md`〈引入方式建議〉 |
| ③ 部分參考的做法（例：mattpocock/skills） | `methodology-adapters.md` § ③ 的做法 |
| 「方法論 skill」的範圍（含 ③ 的本地副本） | `ct-exec/SKILL.md` § Methodology (v6.0.0-pre.1+) |
| `methodology*` 9 個設定鍵的驗證、檢視、寫入 | `tower-config.md` § 方法論設定鍵（v6.0.0+） |
| 工單裡的方法論段落與範例 | `work-order-template.md` 標準模板的 `### 方法論邊界`、§ 填寫方法論欄位指引（v6.0.0+）、§ 撰寫方法論子代理授權（v6.0.0+） |
| Worker 怎麼帶入方法論 | `ct-exec/SKILL.md` § Methodology (v6.0.0-pre.1+)、§ Startup |
| compact／resume 後重讀工單 | `ct-exec/references/session-guardrails.md` § compact／resume 後重讀工單（v6.0.0-pre.1，所有工單） |
| BUG／PLAN／EXP 預設開啟、啟用即產生索引 | `bug-plan-system.md` § 啟用與索引檔、§ 索引格式；`tower-config.md` § 可用選項 |
| 環境偵測只列名稱 | `auto-session.md` § BAT 內部終端路由 › 偵測條件 |
| `CLAUDE_CONFIG_DIR`／`CODEX_HOME` | `data-layer-architecture.md` § 路徑解析（P-3，T0314） |
| 塔台語言不因注入改變 | `control-tower/SKILL.md` § Role（語言規則）、`methodology-adapters.md` § 衝突與防護 C1、C8 |
| `_tower-state.md` 機器可讀摘要 | `memory-protocol.md` § 機器可讀摘要（YAML frontmatter） |
| beta.3 的狀態衛生與 BAT 塔台面板讀取契約（同批規則穩定版 5.13.0 也有） | 見 § beta.3：狀態衛生與 BAT 塔台面板讀取契約 的對照表 |
| beta.4 的通知用完整工單 ID 與 BAT 塔台面板讀取契約 pre.9（同批規則穩定版 5.13.1 也有） | 見 § beta.4：通知用完整工單 ID 與 BAT 塔台面板讀取契約 的對照表 |
| beta.5 的 plugin 安裝就緒（同批規則穩定版 5.14.0 也有；beta 不提供 plugin） | 見 § beta.5：plugin 安裝就緒 的對照表 |
| beta.6 的移植（同批規則穩定版 5.14.1／5.14.2 也有）與 adapter 偵測 plugin | 見 § beta.6：移植 5.14.1／5.14.2、adapter 偵測 plugin；probe 解析：`methodology-adapters.md` § 描述檔格式 › probe 怎麼解析 skill 根目錄、§ 降級；bmad 的 probe：`adapters/bmad.yaml` `detection.probes` |
| beta.7 的移植（同一份文件穩定版 5.14.3 也有）：巢狀的獨立 repo | 見 § beta.7：移植 5.14.3（巢狀的獨立 repo）；`mono-repo-patterns.md` § 巢狀的獨立 repo（一個塔台、多個共用 repo） |
| beta.8 的移植（同批規則穩定版 5.14.4 也有）與 probe 依 runtime | 見 § beta.8：移植 5.14.4、probe 依 runtime；`methodology-adapters.md` § 描述檔格式 › probe 怎麼解析 skill 根目錄（第 1 點順序、第 3 點 Claude plugin）；`data-layer-architecture.md` § 路徑解析 |
| beta.9 的移植（同批規則穩定版 5.15.0 也有）：一批提問只叫醒塔台一次 | 見 § beta.9：移植 5.15.0（一批提問只叫醒塔台一次）；`yolo-mode.md` § Worker 向塔台提問、§ 斷點 A |
| beta.10（v6 才有）：token 用量統計、session 證據、外部增強外掛治理 | 見 § beta.10：session 用量統計（PLAN-004 ⑥）、§ beta.10：session 證據怎麼進學習流程（PLAN-004 ⑦）、§ beta.10：ECC Level 1 退場；`ct-insights/references/analysis-rules.md` § Session 用量統計、`ct-evolve/SKILL.md` § Session Evidence、`enhancement-integration.md` § 外部增強外掛治理、§ ECC Level 1 退場、§ Level 3 › 啟用條件 |
| beta.11（v6 才有）：執行中補充工單 | 見 § beta.11：Worker 執行中接收塔台補充；`work-order-system.md` § 執行中補充工單、`ct-exec/SKILL.md` § Tower Addenda Check、`cross-project-coordination.md` § 通知自己的 Worker 重讀工單；BAT 補註見 `bat-integration.md` § Worker 執行與通知、〈為什麼不能在 BAT 的 Claude 啟動參數放 `--settings`〉 |
| beta.12（v6 才有）：工具清單建議 | 見 § beta.12：工具清單建議；`ct-insights/references/analysis-rules.md` § 工具清單建議；打包檢查：`version-governance.md` § 發布流程 |
| rc.1（正式版候選）：只修錯 | 見 § rc.1：正式版候選（只修錯）；`ct-exec/SKILL.md` § Phase 3、§ Tower Addenda Check；`ct-done/SKILL.md` 第 6 步；`analysis-rules.md` § 工具清單建議 › 報告格式 |
| 6.0.0（正式版）：納入正式版 | 見 § 6.0.0：納入正式版；`version-governance.md` 版號表 v6.0.0 列 |
| 版本變更與已知未驗 | CT `docs/CHANGELOG.md` `[6.0.0]`（含〈從 5.15.0 升級〉；rc.1 的變更見 `[6.0.0-rc.1]`；beta.12、beta.11、beta.10、beta.9、beta.8、beta.7、beta.6、beta.5、beta.4、beta.3、beta.2、beta.1 的變更見 `[6.0.0-beta.12]`、`[6.0.0-beta.11]`、`[6.0.0-beta.10]`、`[6.0.0-beta.9]`、`[6.0.0-beta.8]`、`[6.0.0-beta.7]`、`[6.0.0-beta.6]`、`[6.0.0-beta.5]`、`[6.0.0-beta.4]`、`[6.0.0-beta.3]`、`[6.0.0-beta.2]`、`[6.0.0-beta.1]`）；安裝與升級步驟見 CT 安裝指南 § 2.65、§ 2.64、§ 2.63、§ 2.62、§ 2.61、§ 2.60、§ 2.59、§ 2.58、§ 2.57、§ 2.56、§ 2.55、§ 2.54、§ 2.53、§ 2.52、§ 4.1 |

---

## 一句話

**CT 管「編排」，方法論管「一張工單裡怎麼做」。** 以前 CT 只認得 BMAD，而且把 BMAD 的路由寫死在 CT 本體；
v6 把這一層換成**方法論中立的轉接介面**：每個方法論用一份 adapter 描述檔告訴塔台它在哪、管哪幾層、每種需求該走哪個流程。
BMAD 是第一個、也是預設的 adapter。**什麼都不設，方法論的行為與 5.12.x 完全相同。**
beta.1 只有一個刻意的預設變更：BUG／PLAN／EXP 改成預設開啟（設定明寫 `false` 的照舊，見 § BUG／PLAN／EXP 預設開啟）；beta.2 沒有設定變更；beta.3 新增三個設定（`bug_review_open_threshold`、`bug_review_stale_days`、`customer_acceptance_gate`），從 beta.2 升級不需要遷移（§ beta.3：狀態衛生與 BAT 塔台面板讀取契約）；beta.4 沒有新命令、新設定，從 beta.3 升級只換 skill 檔案（§ beta.4：通知用完整工單 ID 與 BAT 塔台面板讀取契約）；beta.5 也沒有新命令、新設定，從 beta.4 升級只換 skill 檔案（§ beta.5：plugin 安裝就緒）。

**能接方法論，不代表每一家都該接。** beta.2 的結論是：只有在 CT 下實測或研究證明有效益的方法論，CT 才給 adapter、範例或引入建議；
其他的只保留「機器上已經裝了它時怎麼共存」的防護（§ 方法論不是一定要引入）。

---

## 為什麼要方法論轉接

### 分工：編排永遠屬於 CT

| 誰 | 負責 | 不負責 |
|---|---|---|
| CT 核心 | 工單生命週期、落點檢查、`affects_files`、回報區、commit／push 規則、yolo 提問、BAT 通知、三振、學習萃取 | 工單內「怎麼寫程式、怎麼審查」 |
| adapter（描述檔） | 告訴塔台方法論在哪、什麼版本、管哪幾層、每種需求走哪個流程、結果怎麼對應 CT 狀態、會寫哪些檔、會跟 CT 撞在哪 | 執行任何東西——描述檔是**資料，不是程式** |
| 方法論本身 | 工單內的紀律與步驟 | CT 的生命週期 |

（權威：`methodology-adapters.md` § 分工）

這條界線跟「蜂王模式」是同一個想法（`concepts.md` § 蜂王模式）：塔台不碰程式碼，也就不該管 Worker 用哪一套寫程式的紀律；
反過來，方法論再強，也不能改 CT 的工單生命週期。兩邊撞在一起時，**CT 的規則永遠優先**（下方〈衝突時誰贏〉）。

### 寫死就會落後：一個實際的例子

v5.12.x 的 BMAD 路由寫在 CT 本體，還寫著 `bmad-dev-auto`、`bmad-quick-dev`、`final_revision`；
但 BMad-Method v6.11 起它們已改成 `bmad-build-auto`、`bmad-build`，Build Auto 也沒有 `final_revision` 了。
CT 沒有跟著 BMAD 發版，路由就悄悄過期——這正是把路由搬出 CT 本體、改成 adapter 的直接理由。
v6.0.0-pre.1 一併修正了這些舊名，舊名只留在 `adapters/bmad.yaml` 的 `retired_names`（CHANGELOG `[6.0.0-pre.1]` › Changed）。

### 從 Level 2 到方法論轉接

`integration.md` § Level 2 講的是 v5 的「外部 bmad-guide」：塔台偵測 `bmad-guide`，讀它的 reference 選 workflow。v6（自 pre.1 起）的變化：

| | v5.12.x（Level 2：外部 bmad-guide） | v6（Level 2：方法論轉接） |
|---|---|---|
| 認得的方法論 | 只有 BMAD | 任何有 adapter 的方法論；BMAD 是內建 adapter |
| 路由放在哪 | CT 本體（`enhancement-integration.md` 的表） | adapter 描述檔（BMAD：`control-tower/references/adapters/bmad.yaml`） |
| 工單段落 | `### BMad 工作流程` | frontmatter `methodology` ＋ `### 方法論工作流程`（舊段照讀、不回寫） |
| 回報區 | `### sprint-status.yaml 已更新` | `### 方法論執行紀錄`＋`### 方法論狀態回寫`（舊段照讀） |
| `bmad-guide` 的角色 | 唯一的 BMAD 知識來源 | 仍是 BMAD 名稱與細路由的權威；`bmad.yaml` 是標明 `tested_version` 的快照 |
| 去哪裡找 bmad-guide | 5.14.1 起：手動安裝 → Claude plugin → Codex plugin（`enhancement-integration.md` § Level 2 › 偵測） | beta.6 起：同樣的順序寫成 `bmad.yaml` 的 probe，skill 根目錄依契約解析（§ beta.6）；beta.5 以前只查 `skills/` 底下的手動安裝 |

（權威：`enhancement-integration.md` § Level 2：方法論轉接（methodology adapter）、`methodology-adapters.md` § 舊欄位相容）

**向下相容是硬約束**：`methodology` 缺省 = `auto` = 偵測到 bmad adapter 可用（也就是裝了 bmad-guide）就是 bmad，否則 `none`——
與 5.12.x 的 Level 2 一模一樣。舊工單、舊設定檔都不用改，塔台也不會自己把新鍵補寫進設定檔。

---

## 5 層與需求類型

一個方法論不一定什麼都管。契約把「一張工單裡的事」切成 5 層：

| 層 | 鍵名 | 範圍 |
|---|---|---|
| 規劃 | `planning` | 需求、PRD、架構、UX、拆工作項、研究調查 |
| 執行 | `execution` | 實作、重構、修 bug、TDD |
| 審查 | `review` | code review、對抗式審查 |
| 驗證 | `verification` | 測試策略、驗收、在實物上驗證 |
| 交付 | `delivery` | 開 PR、merge、release、deploy——**預設 `none`，CT 不讓方法論做交付，除非使用者授權** |

- **「編排」不是第六層**：它永遠屬於 CT，不能指定給 adapter。
- **這裡的「層」不是三層架構的 Layer，也不是能力等級的 Level**。CT 的「Level」已經有三種意思，所以方法論一律稱「層」（`methodology-adapters.md` § 層次）。
  畫圖時不要把 5 層和 Layer 1/2/3 畫在同一軸（`diagrams.md` § 繪圖禁忌）。

塔台選 workflow 的鍵是**需求類型**：`feature`、`bugfix`、`refactor`、`research`、`review`、`test`、`small-change`，選填 `delivery`。
adapter 對每種需求類型的每一層寫入口；寫 `{}` 表示「本方法論明確不處理這類需求」（`methodology-adapters.md` § 需求類型（routing 的鍵））。

---

## 抽換 vs 分層疊加

兩種用法，差在「換掉整套」還是「每層各選」。

### 抽換：換主方法論

`methodology` 是主方法論：`auto`（預設）／`none`／某個 adapter id。換成 `pstack`，沒另外指定的層就全部跟著 pstack。

### 分層疊加：不同層用不同方法論

`methodology_planning`、`_execution`、`_review`、`_verification` 各自可以是 `inherit`（預設，跟主方法論）、`none` 或某個 adapter id；
`methodology_delivery` 只有 `none`（預設）或 adapter id，沒有 `inherit`。例：主方法論 bmad、執行層 pstack——規劃用 BMAD 拆出工作項規格，實作改用 pstack 的 playbook。

疊加的四條設計原則（`methodology-adapters.md` § 分層疊加（不同層用不同方法論））：

1. **每層一個負責者（排他）**。同一層不能有兩個 adapter——兩套紀律同時指揮一個 Worker，只會互相打架。
2. **跨層交接靠產物**：上一層產出的東西（例：`story-spec`）要對得上下一層吃的東西；對不上，塔台警告並退回「把路徑當一般文件交給下一層」。
3. **回寫由產生產物的 adapter 決定**：BMAD 規劃出來的工作項，由 pstack 實作完之後，狀態要寫回 BMAD 的格式——這一步寫在執行工單裡，塔台收單時複查。
4. **換執行層會失去原方法論內建的審查**（例：`bmad-build` 內建的 Review Triage），派工摘要會提示這個取捨；要審查也換，就另外設 `methodology_review`。

### 設定疊加順序與「這張用 X 做」

9 個鍵沿用既有的「session ＞ project ＞ global ＞ 預設」欄位級覆蓋（`three-layer-arch.md` § 設定的四層覆蓋），上面再加一層**工單覆寫**：
使用者對單張工單指定方法論，塔台寫進該工單、不改設定檔。

| 使用者說 | 範圍 |
|---|---|
| 「這張用 X 做」（整張覆寫） | 規劃、執行、審查、驗證**四層全部**用 X，蓋過設定檔明寫的層設定 |
| 「這張 <層> 用 X」（指定層覆寫） | 只有那一層 |

兩種可以並用（「這張用 X 做，審查用 Y」）：先套整張、再套指定層。**交付層不在整張覆寫內**——要開放必須明說「這張交付層用 X」。
理由很簡單：交付是對外、不可逆的動作，不能因為一句「用 X 做」就順帶開放（`methodology-adapters.md` § 抽換（專案選主方法論））。

工單 frontmatter 的 `methodology.resolved_from` 每層各記來源（`workorder`／`session`／`project`／`global`／`default`），
所以事後看工單就知道「這一層為什麼是 pstack」。設定的檢視指令與解析例在 `tower-config.md` § 方法論設定鍵（v6.0.0+）。

### 什麼時候解析

- 塔台**寫工單時**解析一次，寫進 frontmatter。
- 還沒派出的 `PENDING` 工單，**派工前再解析一次**（工單覆寫照留），有差異就在派工摘要列出、以新值為準。
- **已派出的工單不變**：`IN_PROGRESS` 以後（含 Renew、重派）不重新解析。設定變更只影響之後派出的工單——Worker 正在照工單做事，不能讓它腳下的規則換掉。

（權威：`methodology-adapters.md` § 解析步驟（塔台派工時））

Worker 不讀設定檔決定方法論，這與 `CT_MODE` 由塔台傳入是同一個原則（`runtime-dispatch.md` § Worker 無狀態：mode 怎麼送到 Worker）：
塔台已經把結果寫進工單，Worker 只照工單做。

---

## adapter 是什麼

### 一份描述檔＋一份 README

一個方法論 = 一份 YAML 描述檔（機器讀，`schema: ct-methodology-adapter/v1`，固定 22 個頂層欄位）＋一份 README（人讀）。
描述檔只放名稱、對照、連結與 CT 自己的規則，**不放第三方 skill 原文**——授權乾淨，也不會跟上游內容一起過期。
22 個欄位涵蓋：在哪、什麼版本、怎麼偵測、5 層各自能力、需求 → 流程路由、工單要加什麼段落、Worker 怎麼呼叫、結果怎麼對應 CT 狀態、
會寫哪些檔、跨層交接、退役名、降級、hook 與子代理、撞詞對照（`methodology-adapters.md` § 描述檔格式）。

**方法論說 done ≠ 工單 DONE**：方法論自己的終態是成功，**而且**工單驗證閘門通過，才能 DONE（`methodology-adapters.md` § 狀態對應總則）。
這延續了 CT 一貫的「證據分道」：方法論的自評是一條證據，不是驗收本身（`concepts.md` § 證據分道）。

### 三種來源

| 來源 | 位置 | 例子 |
|---|---|---|
| CT 內建 | `control-tower/references/adapters/<id>.yaml` | 目前只有 `bmad` |
| 外部 skill | `ct-adapter-<id>/`，裝在 skills 目錄 | CT 官方的 `ct-adapter-pstack`（**選用**：已在用 pstack 才裝；Beta 隨預發行 Release 提供 zip；`adapter_version` 0.2.6、`tested_version` 0.9.103） |
| 專案本地 | `_ct-workorders/_adapters/<id>/` | 團隊自己的流程 |

搜尋順序：`methodology_adapters_path` ＞ 專案本地 ＞ 外部 skill ＞ CT 內建；同 `id` 取第一個找到的，所以專案可以用同 `id` 覆寫內建 bmad
（`methodology-adapters.md` § 散布與搜尋順序）。新 adapter 的可機器檢查部分交給 `control-tower/scripts/validate-adapter.py`；
上游名稱是否真的存在、有沒有第三方原文，仍要人看（`methodology-adapters.md` § 新 adapter 的最小檢查）。

### 什麼時候要另外配一個 guide skill

BMAD 除了 adapter，還有一個 `bmad-guide`（教學、細路由、名稱與版本對照）。新方法論要不要也配一個？符合下列**任一**才配：

1. 沒有自帶路由，或自帶的路由不認版本
2. 多階段，而且要依產物狀態選下一步
3. skill 改名、退役頻繁，需要一個地方持續維護對照
4. 需要在地化教學

都不符合，就把 CT 需要的資訊全部放進 `ct-adapter-<id>`，不另做 guide。BMAD 四條都符合，所以有 `bmad-guide`；
pstack 自帶 `poteto-mode` 路由與 playbook、改版快，是**不配 guide 的反例**（`methodology-adapters.md` § 未來介接（新方法論要不要配 guide skill））。
有 guide 的方法論，**名稱與細路由以 guide 為準**，adapter 只是快照——這仍是「單一權威定義」（`governance.md` § 單一權威定義）。

### 找不到、壞掉、能力不足：一律降級，不阻塞

方法論沒裝、描述檔壞了、workflow 名稱不存在、該層能力是 `none`——都退回主方法論或自由文字，派工摘要提示，**不阻塞塔台，也不替方法論編造行為**
（`methodology-adapters.md` § 降級）。這跟 v5 Level 2「查詢失敗一律靜默退回手動指定」是同一種降級哲學（`integration.md` § 偵測與降級）。
beta.6 起有一種情況不再靜默：probe 全部失敗、agent 的可用 skill 清單裡卻有該方法論的 skill——裝了、只是塔台讀不到——本 session 提示一次再降級（同一節的新列；穩定版 5.14.1 對 bmad-guide 也這樣做）。

---

## 方法論不是一定要引入：各家定位

（beta.2 新增；權威：`methodology-adapters.md` § 引入方式 的原則段與建議表。）

### 原則

v6 讓 CT 能接任何方法論，但「能接」不等於「該接」。beta.2 把這件事寫成原則：
**只有實測或研究證明對 CT 使用者有效益時，CT 才給它 adapter、範例或引入建議；沒有效益的，CT 只保留「機器上已經裝了它時怎麼共存」的防護（C1、C5、C10），不推薦、不做範例。**

### 為什麼要先給結論，而不是把每一家都列成選項

- **建議會被讀成背書。** 教材、Portal 或 `*onboard` 把一家方法論寫成「建議用 ② 或 ③ 引入」，讀者自然理解成「CT 推薦它」。
  beta.1 的各家表把 Superpowers 寫成「② 或 ③」就是這樣：當時只問了「怎麼裝才不干擾 CT」，沒有先問「裝了有沒有用」。
- **每多接一家，成本是確定的，效益不一定。** 常駐注入的 token、搶路由的風險、跟著上游改版、Release 多一個附件——這些一定會發生；
  效益如果沒有證據，就是拿確定的成本去換不確定的好處。
- **共存防護和推薦是兩回事。** 使用者機器上可能本來就裝了某個方法論，CT 不能假裝它不存在，所以防護（邊界段、雙注入偵測、HARD-GATE 的處理）照樣保留；
  只是不再鼓勵別人為了 CT 去裝它。

所以 beta.2 打包前先過一道**結論閘門**：塔台依 P1／P1b（§ 隔離試用）、P3（§ 實測 P3）與 mattpocock/skills 的研究，逐家列出效益、成本與建議，
使用者確認後才寫進 CT。

### 四家定位

| 方法論 | 定位 | 效益（證據） | 成本（證據） |
|---|---|---|---|
| BMAD（內建 adapter） | **引入**：① 內建、預設 | CT 原生的方法論與課程基準；P1 實測與 5.12.x 行為一致（只差 tracker 段，beta.1 已修，P-1） | `bmad.yaml` 要跟著 bmad-guide 的更名走（已有同步流程） |
| pstack（`ct-adapter-pstack`） | **選用**：已在用 pstack 才裝；CT 不預設、不主動推薦 | 已在用 pstack 的人可以抽換或分層（P1、P1b 照權威檔走完整流程）；也是 adapter 契約唯一的外部參考實作 | 沒有邊界段時注入會搶路由（V1 1/2、V2a 2/2）；常駐注入 998 bytes（C14）；背景子代理要額外記帳（Q-1）；要跟上游版本 |
| Superpowers（沒有 adapter） | **不建議引入**；已裝的機器照共存防護 | 在 CT 下**沒有實測效益**：有邊界段時 0 次叫用（V2b、P1b、P3）；沒有邊界段時 Worker 依 `ct-exec` 優先序第 ④ 項也不採用；HARD-GATE 0/3 | 每個 session 常駐注入 3.4～7.9 KB（V2b 3,417 bytes、P1b 3,616 bytes、P3 7,906 bytes）；沒有官方的關注入開關（C10、C14） |
| mattpocock/skills（沒有 adapter；工具型 skill 集） | ③ 部分參考的**可選做法範例，品質效益未實證**；不建議標準 plugin 安裝 | ③ 的機制實測有效（P3：本地副本 0 次被模型自動叫用、工單指名才用、Worker 3/3 記入回報區）；提供 TDD、除錯、審查的具體做法 | 只有文件層；用它和不用它的品質差異沒有比較過 |

讀這張表的方式：

- **Superpowers 不是「不好」，是「在 CT 下用不到」。** 它的設計是讓模型自己判斷何時進 brainstorming、TDD 這類流程；
  可是 CT 工單已經寫定「做什麼、怎麼驗收」，Worker 依 `ct-exec` 的優先序不採用不負責本單的注入——三輪實測它都沒被叫到。
  剩下的只有成本：每個 session 好幾 KB 的注入，而且上游沒有只關注入的開關。
- **pstack 有用，但只對「已經在用 pstack 的人」有用。** 效益是讓 pstack 使用者把熟悉的流程接進 CT；
  沒在用的人裝了，只多出注入搶路由與常駐 token。所以是「選用」，不是「推薦」——CT 的預設仍是 BMAD。
- **mattpocock/skills 證明的是「③ 這個做法行得通」，不是「它讓品質變好」。** P3 驗的是機制：副本不會被模型自己叫到、Worker 照工單指名讀檔照做、用了有記錄。
  用與不用的成果差多少沒有做 A/B。塔台評估過補做：8 張樣本太小、合成工單會干擾判讀（P3 的 M4 就是例子），而且結果不會改 CT 的設計，
  所以 beta.2 不補做；想在自己的專案用，建議在真實專案開 EXP 單、只測一支（例：`diagnosing-bugs` 或 `tdd`）。
- 這張表是**給 CT 使用者的建議**，不是塔台的派工規則。塔台派工照實際偵測（`hook_probe`）：機器上裝了什麼，塔台就照什麼防護（§ 引入方式 › 塔台不替你選）。

### 已經裝了 Superpowers 怎麼辦

不必為了 CT 移除，但 CT 也不會去用它。塔台照共存防護處理（`methodology-adapters.md` § 衝突與防護 C1、C5、C10）：

- 注入開著時，`methodology_guard: warn` 在工單自動加 `### 方法論邊界`，把 Superpowers 以「無 adapter」列進【不使用】；和 pstack 同時開著就標「雙注入」（§ 雙注入）。
- 派工摘要的常駐 token 寫「`always_on_tokens` 未量測」，不填估值（Q-4，§ 隔離試用）。
- HARD-GATE（設計核准前不准實作）：沒有指名 Superpowers 的工單，Worker 在 headless／yolo 下不會被它擋住（P3 2/2，§ 實測 P3）。
- 想省掉常駐注入，只能在 CT 管理的機器上停用它（上游沒有只關注入的開關）。這是使用者的安裝選擇，塔台只提示、不代做。

---

## 引入方式：完整安裝、只引用 skill、部分參考

（beta.1 新增，beta.2 補實測結果；權威：`methodology-adapters.md` § 引入方式。上一節回答「要不要引入」；本節回答「要引入的話，裝到什麼程度」。
下一節〈注入防護〉講的是「已經裝了、注入開著」時怎麼防；本節往前一步：**要不要讓注入開著**。）

### 為什麼不能只有「全裝」一種

pre.1 時，方法論只有兩種狀態：完整安裝（plugin＋hook＋skill），或不用；衝突表 C1 的建議也只有一句「關掉注入」。
可是 hook 正是方法論跟 CT 撞在一起的地方：

| 衝突 | hook 造成什麼 | 實測 |
|---|---|---|
| C1 注入搶路由 | Worker 分頁一開就被導向方法論入口 | V1：沒有邊界段 2 次中 1 次進 `pstack:poteto-mode` |
| C10 多家注入疊加 | 兩家都裝，兩段注入同時進 context | V2b、P1b：兩段都送達 |
| C14 常駐 token | 每個 session 都付一次 | pstack 998 bytes；Superpowers 3,417 bytes（V2b）、3,616 bytes（P1b） |
| 沒有關注入的開關 | 上游沒提供官方開關（Superpowers） | 只能靠邊界段壓 |

只想借一個 skill 的人，被迫為了它承擔整套常駐注入。所以 beta.1 把「裝到什麼程度」列成正式選項，由重到輕三種。

### 三種方式

| 方式 | 裝什麼 | 常駐注入 | 塔台怎麼看 | 工單怎麼寫 |
|---|---|---|---|---|
| ① **完整安裝** | 上游的標準安裝：plugin、hook、skill 全裝 | 有 | adapter 的 `hook_probe` 判斷注入開著 → `methodology_guard: warn` 自動加邊界段；兩家以上標「雙注入」 | 照解析步驟；注入開著時有 `### 方法論邊界` |
| ② **只引用 skill** | 不裝會常駐注入的 hook／plugin，只裝需要的 skill（例：上游的 skills-only 安裝），或以路徑讀 skill 檔 | 無 | `hook_probe` 判斷為關：這家不觸發【不使用】項，也不會有「雙注入」提示；adapter 要有認得這種安裝的 probe（pstack：`skills-only`） | 用到時在邊界段的【只允許】**指名** skill（以路徑讀就寫路徑） |
| ③ **部分參考** | 精選 skill 的**本地副本**（鎖版、名稱加前綴、frontmatter `disable-model-invocation: true`），或只借鏡做法，寫進工單步驟或專案準則（FIELDGUIDE、`_local-rules.md`） | 無 | 不偵測，guard 不觸發；要讓塔台路由到本地副本，就寫專案本地 adapter 指向加了前綴的名稱 | 【只允許】或工單步驟指名副本路徑，或直接寫做法；沒有 adapter 時屬自由文字，不為副本寫 `methodology` 層，其他層照解析步驟（例：執行層用副本、審查層照 `auto` 仍由 bmad 負責）；用了照樣記入 `### 方法論執行紀錄` |

③ 的三個動作各有用意：

- **名稱加前綴**：副本不跟上游同名 skill 撞名，回報區一看就知道用的是副本、不是上游。
- **`disable-model-invocation: true`**：模型不會因為「描述看起來符合」就自己叫用它，只有工單明寫才用——正是 CT 要的「用了什麼由工單決定」。
- **鎖版**：上游改版不會悄悄改變副本的行為；代價是副本要自己維護，跟〈寫死就會落後〉是同一個取捨的另一面。

### 各家建議

先看上一節的定位：**要引入**的才談引入方式；不建議引入的（Superpowers）沒有引入方式的建議，只有共存防護。

| 方法論 | 定位 | 引入方式建議 | 為什麼 |
|---|---|---|---|
| bmad（內建） | 引入 | ① | 核心不裝 harness hook（`bmad.yaml` 的 `session.hooks` 是空的，推論）；選配模組 `bmad-loop` 有自己的 hook，裝了另外評估 |
| pstack（`ct-adapter-pstack`） | 選用 | 已在用 pstack 時：當主方法論或固定負責某一層用 ①；只在個別工單借某個 skill（例 `thermos` 審查）用 ② | ① 有官方的關注入開關，邊界段實測有效；② 用上游 skills-only 安裝，沒有常駐注入、不觸發「雙注入」 |
| mattpocock/skills（沒有 adapter） | 可選做法範例，品質效益未實證 | ③；不做標準 plugin 安裝 | 沒有 hook，標準安裝後模型可依描述自動叫用、塔台偵測不到（C1 ⑤）；③ 的機制已實測有效。做法見 § 在 CT 專案使用 mattpocock/skills |
| Superpowers（沒有 adapter） | 不建議引入 | —（已裝的機器照共存防護） | 在 CT 下沒有實測效益、常駐注入且沒有官方的關注入開關；見 § 方法論不是一定要引入 › 已經裝了 Superpowers 怎麼辦 |

**何時才建議 ② 或 ③**（權威檔的條件）：方法論**對 CT 使用者有效益、值得引入**，但它的 hook 會影響 CT（注入搶路由、多家注入疊加、常駐 token），
或上游沒有官方的關注入開關；或方法論沒有 hook、靠 skill 描述讓模型自動叫用。沒有效益的方法論不給 ②／③ 的建議。

pstack 的完整建議（含選用定位，以及「已經 ① 裝好、但大多數工單不用 pstack」時寫 `session hook: off` 或改成 ②）在 `ct-adapter-pstack/README.md`〈引入方式建議〉。

### 塔台不替你選

- 引入方式是**使用者機器上的安裝選擇**，塔台不改安裝；派工依實際偵測（`hook_probe`）判斷，不依「建議」判斷。
  這跟〈hook 信任〉同一種精神：碰到使用者層級的決定，塔台只提示、不代做。
- adapter 描述檔**沒有**「建議的引入方式」欄位，是評估過後刻意不加：塔台派工看的是實際偵測，不是建議；`*onboard` 主題 5 只列 adapter 的 id 與名稱、不讀說明欄位；
  建議依情境而定（pstack 當主 → ①、借一個 skill → ②），一個值表達不了；需要建議的 mattpocock/skills 也根本沒有 adapter。所以建議寫在 adapter README 與權威檔的各家表，契約仍是 `ct-methodology-adapter/v1`。
- `*onboard` 問主方法論時，選的方法論有 hook，會補一句「也可以只引用 skill 或只參考做法」；偵測到沒有 adapter 的注入（例：Superpowers）時，改說「方法論不是一定要引入」，
  指向建議表，並說明已經裝了的話塔台派工時照共存防護處理——beta.1 在這裡也提 ②／③，等於在推薦它，beta.2 拆成兩句（`onboarding.md` § 主題 5：主方法論（v6.0.0+））。

### 實測狀態：③ 已實測、② 未實測

- **① 完整安裝**：邊界段實測有效（V1 3/3、V2a 2/2、V2b 2/2，P1b 雙注入再 1/1），見下一節〈注入防護〉。
- **③ 部分參考：已實測**（P3，beta.2）。mattpocock/skills 的 3 支本地副本（`mp-diagnosing-bugs`、`mp-tdd`、`mp-code-review`，加 `disable-model-invocation: true`）
  在塔台與 Worker 共 4 個 session 裡 **0 次**被模型自動叫用；塔台照權威檔把副本路徑寫進【只允許】；Worker **3/3** 以路徑讀並照做、**3/3** 記入 `### 方法論執行紀錄`。
  同一份上游以標準 plugin 安裝（①）時，塔台開 bugfix 單 0/1 自動叫用——n=1，只能說「這次沒發生」，不代表不會發生（C1 ⑤）。細節見 § 實測 P3。
- **② 只引用 skill：仍未實測**。上表 ② 的塔台行為是依規則推得。
- 還沒驗的 ③ 周邊：Codex 端的 `policy.allow_implicit_invocation: false`、副本「先問使用者」的步驟在 yolo 下改問塔台、副本在 BAT worktree 隔離派工下的可見性（§ 已知未驗 第 3、5 項）。

### 圖：三種引入方式

規格見 `diagrams.md` § 19（beta.2 改圖：各家列改成定位，Superpowers 不再指向任何方式；實測列改成 ③ 已實測）。

```svg
<svg width="100%" viewBox="0 0 680 660">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>

<text class="ts" x="40" y="22" dominant-baseline="central">由重到輕 →（裝到什麼程度是使用者的選擇；塔台依實際偵測派工）</text>

<!-- 三種方式 -->
<g class="node c-teal" onclick="sendPrompt('介紹方法論引入方式 ① 完整安裝')">
  <rect x="40" y="40" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="128" y="58" text-anchor="middle" dominant-baseline="central">① 完整安裝</text>
  <text class="ts" x="128" y="76" text-anchor="middle" dominant-baseline="central">plugin＋hook＋skill</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹方法論引入方式 ② 只引用 skill')">
  <rect x="252" y="40" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="58" text-anchor="middle" dominant-baseline="central">② 只引用 skill</text>
  <text class="ts" x="340" y="76" text-anchor="middle" dominant-baseline="central">skills-only・不裝 hook</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹方法論引入方式 ③ 部分參考')">
  <rect x="464" y="40" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="552" y="58" text-anchor="middle" dominant-baseline="central">③ 部分參考</text>
  <text class="ts" x="552" y="76" text-anchor="middle" dominant-baseline="central">本地副本・借鏡做法</text>
</g>
<line x1="128" y1="92" x2="128" y2="118" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="92" x2="340" y2="118" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="552" y1="92" x2="552" y2="118" stroke-width="1" marker-end="url(#arrow)"/>

<!-- 常駐注入 -->
<g class="node c-amber" onclick="sendPrompt('介紹 SessionStart 注入為什麼要邊界段')">
  <rect x="40" y="120" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="128" y="138" text-anchor="middle" dominant-baseline="central">常駐注入：有</text>
  <text class="ts" x="128" y="156" text-anchor="middle" dominant-baseline="central">SessionStart hook</text>
</g>
<g class="node c-green" onclick="sendPrompt('介紹不裝 hook 為什麼就沒有常駐注入')">
  <rect x="252" y="120" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="138" text-anchor="middle" dominant-baseline="central">常駐注入：無</text>
  <text class="ts" x="340" y="156" text-anchor="middle" dominant-baseline="central">只有 skill 檔</text>
</g>
<g class="node c-green" onclick="sendPrompt('介紹本地副本的前綴與 disable-model-invocation')">
  <rect x="464" y="120" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="552" y="138" text-anchor="middle" dominant-baseline="central">常駐注入：無</text>
  <text class="ts" x="552" y="156" text-anchor="middle" dominant-baseline="central">副本不會自己被叫用</text>
</g>
<line x1="128" y1="172" x2="128" y2="198" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="172" x2="340" y2="198" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="552" y1="172" x2="552" y2="198" stroke-width="1" marker-end="url(#arrow)"/>

<!-- 塔台 -->
<g class="node c-gold" onclick="sendPrompt('介紹方法論邊界段與 methodology_guard')">
  <rect x="40" y="200" width="176" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="128" y="220" text-anchor="middle" dominant-baseline="central">塔台：warn</text>
  <text class="ts" x="128" y="240" text-anchor="middle" dominant-baseline="central">自動加邊界段・雙注入提示</text>
</g>
<g class="node c-gold" onclick="sendPrompt('介紹塔台怎麼用 hook_probe 判斷注入')">
  <rect x="252" y="200" width="176" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="220" text-anchor="middle" dominant-baseline="central">塔台：探測為關</text>
  <text class="ts" x="340" y="240" text-anchor="middle" dominant-baseline="central">不觸發【不使用】</text>
</g>
<g class="node c-gold" onclick="sendPrompt('介紹塔台怎麼用 hook_probe 判斷注入')">
  <rect x="464" y="200" width="176" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="552" y="220" text-anchor="middle" dominant-baseline="central">塔台：不偵測</text>
  <text class="ts" x="552" y="240" text-anchor="middle" dominant-baseline="central">guard 不觸發</text>
</g>
<line x1="128" y1="256" x2="128" y2="282" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="256" x2="340" y2="282" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="552" y1="256" x2="552" y2="282" stroke-width="1" marker-end="url(#arrow)"/>

<!-- 工單 -->
<g class="node c-teal" onclick="sendPrompt('介紹邊界段的【只允許】與【不使用】')">
  <rect x="40" y="284" width="176" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="128" y="304" text-anchor="middle" dominant-baseline="central">工單：邊界段</text>
  <text class="ts" x="128" y="324" text-anchor="middle" dominant-baseline="central">【只允許】＋【不使用】</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹邊界段的【只允許】與【不使用】')">
  <rect x="252" y="284" width="176" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="304" text-anchor="middle" dominant-baseline="central">工單：【只允許】</text>
  <text class="ts" x="340" y="324" text-anchor="middle" dominant-baseline="central">指名 skill 或路徑</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹方法論引入方式 ③ 部分參考')">
  <rect x="464" y="284" width="176" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="552" y="304" text-anchor="middle" dominant-baseline="central">工單步驟指名副本</text>
  <text class="ts" x="552" y="324" text-anchor="middle" dominant-baseline="central">或直接寫進步驟</text>
</g>

<!-- 各家建議 -->
<text class="ts" x="40" y="366" dominant-baseline="central">各家定位與建議的方式（虛線指向建議的方式；只有值得引入的才有）</text>
<path d="M128 384 L128 344" fill="none" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<path d="M330 384 L140 344" fill="none" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<path d="M330 384 L330 344" fill="none" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<path d="M552 384 L552 344" fill="none" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<g class="node c-coral" onclick="sendPrompt('介紹內建 bmad adapter 與 bmad-guide 的關係')">
  <rect x="40" y="386" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="128" y="404" text-anchor="middle" dominant-baseline="central">bmad 引入 → ①</text>
  <text class="ts" x="128" y="422" text-anchor="middle" dominant-baseline="central">內建・預設</text>
</g>
<g class="node c-amber" onclick="sendPrompt('介紹 ct-adapter-pstack 的引入方式建議')">
  <rect x="252" y="386" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="404" text-anchor="middle" dominant-baseline="central">pstack 選用 → ①／②</text>
  <text class="ts" x="340" y="422" text-anchor="middle" dominant-baseline="central">已在用 pstack 才裝</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹在 CT 專案使用 mattpocock/skills')">
  <rect x="464" y="386" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="552" y="404" text-anchor="middle" dominant-baseline="central">mattpocock → ③</text>
  <text class="ts" x="552" y="422" text-anchor="middle" dominant-baseline="central">做法範例・效益未實證</text>
</g>

<!-- 不建議引入（不連到任何方式） -->
<g class="node c-gray" onclick="sendPrompt('介紹 Superpowers 為什麼不建議引入、已經裝了怎麼共存')">
  <rect x="40" y="458" width="600" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="476" text-anchor="middle" dominant-baseline="central">Superpowers：不建議引入（在 CT 下沒有實測效益）</text>
  <text class="ts" x="340" y="494" text-anchor="middle" dominant-baseline="central">已裝的機器只留共存防護：邊界段【不使用】・雙注入提示・C1／C5／C10</text>
</g>

<!-- 實測狀態 -->
<g class="node c-gray" onclick="sendPrompt('介紹引入方式哪些已實測、哪些未實測')">
  <rect x="40" y="526" width="600" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="544" text-anchor="middle" dominant-baseline="central">實測：① 邊界段有效（V1・V2a・V2b・P1b）；③ 已實測（P3：0 次自動叫用、3/3 記錄）</text>
  <text class="ts" x="340" y="562" text-anchor="middle" dominant-baseline="central">② 未實測：塔台行為依規則推得</text>
</g>

<!-- 圖例 -->
<text class="ts" x="40" y="602" dominant-baseline="central">圖例：青綠＝方式與工單　琥珀＝有常駐注入／外部 adapter　綠＝無注入</text>
<text class="ts" x="40" y="622" dominant-baseline="central">　　　金＝塔台　珊瑚＝BMAD　灰＝無 adapter／不引入／記錄</text>
<text class="ts" x="40" y="642" dominant-baseline="central">引入方式 ≠ 方法論的 5 層：前者是「裝多少」，後者是「誰負責哪一層」</text>
</svg>
```

**Drill-down**：

| 點哪裡 | `sendPrompt()` | 回答時讀 |
|---|---|---|
| ①／②／③ 方式 | 介紹方法論引入方式 ① 完整安裝（② 只引用 skill、③ 部分參考） | 本章 § 引入方式 › 三種方式 |
| 常駐注入：有 | 介紹 SessionStart 注入為什麼要邊界段 | 本章 § 注入防護 › 問題 |
| 常駐注入：無（②） | 介紹不裝 hook 為什麼就沒有常駐注入 | 本章 § 引入方式 › 為什麼不能只有「全裝」一種 |
| 常駐注入：無（③） | 介紹本地副本的前綴與 disable-model-invocation | 本章 § 引入方式 › 三種方式（③ 的三個動作） |
| 塔台：warn | 介紹方法論邊界段與 methodology_guard | 本章 § 注入防護 › 四道防線 |
| 塔台：探測為關／不偵測 | 介紹塔台怎麼用 hook_probe 判斷注入 | 本章 § 引入方式 › 塔台不替你選；§ 注入防護 |
| 工單節點 | 介紹邊界段的【只允許】與【不使用】 | 本章 § 注入防護 › 四道防線 |
| bmad | 介紹內建 bmad adapter 與 bmad-guide 的關係 | 本章 § adapter 是什麼 › 什麼時候要另外配一個 guide skill；§ 方法論不是一定要引入 › 四家定位 |
| pstack | 介紹 ct-adapter-pstack 的引入方式建議 | 本章 § 方法論不是一定要引入 › 四家定位；§ 引入方式 › 各家建議；§ 隔離試用 › `ct-adapter-pstack` 0.2.3（beta.2 為 0.2.4） |
| mattpocock | 介紹在 CT 專案使用 mattpocock/skills | 本章 § 在 CT 專案使用 mattpocock/skills |
| Superpowers | 介紹 Superpowers 為什麼不建議引入、已經裝了怎麼共存 | 本章 § 方法論不是一定要引入（四家定位、已經裝了 Superpowers 怎麼辦）；§ 雙注入 |
| 實測 | 介紹引入方式哪些已實測、哪些未實測 | 本章 § 引入方式 › 實測狀態：③ 已實測、② 未實測；§ 實測 P3；§ 已知未驗 |

---

## 在 CT 專案使用 mattpocock/skills

（beta.2 新增；權威：`methodology-adapters.md` § 引入方式、§ ③ 的做法、§ 衝突與防護 C1；`ct-exec/SKILL.md` § Methodology (v6.0.0-pre.1+)。
這是 ③ 的一個**可選做法範例，品質效益未實證**——不是 CT 的推薦，也不是必要步驟。）

### 它是什麼、為什麼不能直接裝

mattpocock/skills（<https://github.com/mattpocock/skills>，MIT）是一組**工具型 skill 集**：TDD、除錯、code review 之類的單支做法。
它**不是方法論**——沒有編排、沒有狀態，也沒有 hook。CT 沒有它的 adapter，也不散布它的任何檔案或原文；下面都是使用者在自己專案裡做的事。

**不要在 CT 管理的機器上裝標準 plugin**，原因有兩個：

- **沒有 hook，反而更難防。** 標準安裝後，模型可依 skill 描述自動叫用它（例：描述寫著「遇到 bug 時用」）。塔台與 Worker 都可能被叫到，
  而 CT 的守衛 `hook_probe` 看的是 hook——沒有 hook 就偵測不到、guard 不觸發、`methodology_ambient` 也看不到（C1 ⑤）。
  P3 的標準安裝那一輪塔台 0/1 被叫用，n=1 不能證明風險不存在。
- **plugin 會自動更新**：跑的版本和工單記的對不上，出了問題無從比對。

### 怎麼做（③）

| 步驟 | 做什麼 | 為什麼 |
|---|---|---|
| 本地副本、鎖版 | 從上游一個固定的 commit 把要用的 skill 複製到專案的 skill 目錄 | 上游改版不會悄悄改變副本行為 |
| 名稱加前綴 | 副本 `name` 加前綴（例：`mp-`） | 上游不為避開 harness 內建指令改名（例：`code-review` 與 Claude Code 內建指令同名），不加前綴可能叫到內建的那一個 |
| 關掉自動叫用 | Claude Code：frontmatter `disable-model-invocation: true`；Codex 也要用時，副本的 `agents/openai.yaml` 另寫 `policy.allow_implicit_invocation: false` | 兩個 runtime 各看各的設定，只改一邊，另一邊仍會依描述自動叫用 |
| 改寫外部前提 | 叫其他上游 skill 的句子改成副本路徑或刪掉；以外部 issue tracker 為規格來源的前提改成「規格 = 本工單檔」 | 副本在 CT 工單裡跑，事實來源是工單 |
| 工單指名才用 | 工單 `### 方法論邊界` 的【只允許】或執行步驟寫副本路徑；副本要問使用者或等核准的步驟，在邊界段逐條寫成 CT 的處理（寫進回報區不停下、改問塔台、回 `BLOCKED`） | 用了什麼由工單決定；P3 的塔台自己就把副本裡兩處「問使用者」逐條對照成 CT 規則，Worker 照做沒有停下 |
| 用了照樣記錄 | Worker 用了副本，記入 `### 方法論執行紀錄`（beta.2 起是規則：「方法論 skill」的範圍含工單指名的 skill 與 ③ 的本地副本）；副本在 Claude Code 也只能以路徑讀，讀了照做算一次呼叫 | 防線 ②「用了必記」不因為沒有 adapter 就失效 |
| 記版本 | 副本旁放一份紀錄（例：`VENDOR.md`：上游網址、commit、複製日期、本地改了什麼）；上游更新另開工單比對 | 鎖版的代價是要自己維護，紀錄讓比對有依據 |

**不放進 Worker 工單的 skill**：自建 worktree 或整合分支的（`implement-spec`）、以外部 issue tracker 為事實來源的（`to-spec`、`to-tickets`、`triage`、`wayfinder`、`implement`）、
開寫入型背景子代理的（`research`）、整支都在問使用者的（`domain-modeling`）。它們分別撞上 CT 的「隔離走 BAT worktree」「事實來源是工單」「寫入集中在主 Worker」「yolo 不問使用者」（C4～C7、C15）。

### P3 實測：機制有效，效益未實證

| 看什麼 | 結果 |
|---|---|
| 副本會不會被模型自己叫到 | 3 支副本（`mp-diagnosing-bugs`、`mp-tdd`、`mp-code-review`）在塔台與 Worker 共 4 個 session 裡 **0 次** |
| 塔台怎麼開單 | 照 § ③ 的做法把副本路徑寫進【只允許】，不為副本寫 `methodology` 層，審查層照 `auto` 仍由 bmad 負責 |
| Worker 怎麼用 | **3/3** 以路徑讀 `SKILL.md` 照做；副本自帶的審查子代理是前景、唯讀，照規則記帳 |
| 有沒有記錄 | **3/3** 記入 `### 方法論執行紀錄`（寫明副本路徑、在哪一步、做了什麼、跳過什麼） |
| 品質有沒有變好 | **沒有比較過**（A/B 未做，理由見 § 方法論不是一定要引入 › 四家定位） |

### 注意：副本放在被 `.gitignore` 排除的目錄時（推論）

副本常放在 `.claude/skills/` 之類的目錄，而很多專案的 `.gitignore` 排除整個 `.claude/`。BAT 的 worktree 隔離派工（`isolation: worktree`）
從 git 建出工作樹，**沒進 git 的副本不會出現在 worktree 裡**，Worker 就讀不到工單指名的路徑。要在隔離派工裡用副本，就讓副本進 git（在 `.gitignore` 放行那個目錄）。
這一點是 P3 的試用塔台讀規則時指出的，P3 沒有派 worktree 驗證，所以是**推論**，列在〈已知未驗〉第 3 項。

---

## 注入防護：為什麼要「邊界段」

### 問題：Worker 分頁一開，就被叫去用別的方法論

有些方法論裝的是**外掛＋SessionStart hook**：每個新 session 一開，hook 就往 context 塞一段路由指示。
pstack 的注入是 998 bytes，開頭是「You have pstack.」，意思大致是「多檔、設計選擇、原因未知的 bug → 先叫 `pstack:poteto-mode`」。
它在 `startup`、`resume`、`clear`、`compact` 都會注入。

對 CT 來說，這是「工單之外的另一個指揮者」：Worker 照工單做事做到一半，被注入導進另一套流程——
委派子代理、開 worktree、開 PR，都可能跟 CT 的「寫入集中在主 Worker」「不切分支、不 push」撞在一起（`methodology-adapters.md` § 衝突與防護 C1、C4、C6）。

### 四道防線

| 防線 | 做什麼 | 誰做 |
|---|---|---|
| ① `### 方法論邊界` | 在工單裡明寫「本單用／不用哪些方法論 skill」、子代理只能唯讀、不開分支不 push、範圍外不產檔、compact／resume 後重讀 | 塔台：`methodology_guard: warn`（預設）時**自動加**，沒有任何層由 adapter 負責的工單也加 |
| ② 方法論使用必記 | 呼叫了任何方法論 skill（不論工單有沒有宣告）都寫進回報區 `### 方法論執行紀錄` | Worker |
| ③ 注入自查 | 開工時看 context 有沒有注入標記，寫成 `methodology_ambient` 行（有 `methodology` 或邊界段的工單**必填**，沒看到寫 `none`；不阻塞） | Worker |
| ④ compact／resume 後重讀工單 | 不靠 compact 摘要記得邊界，先重讀整張工單（含邊界段）再繼續 | Worker，所有工單 |

邊界段有兩種變體：本單有層由某方法論負責 → 【只允許】那幾個 skill；注入開著、但不負責本單任何一層 → 【不使用】，**每一家都列**。
兩種都有就兩項都寫。範本的唯一一份在 `work-order-template.md` 標準模板的 `### 方法論邊界`；每家的值取自它的 adapter
（`methodology-adapters.md` § 與 hook／session 路由的相處規則 第 2 點）。

邊界段為什麼有效？注入文字自己寫著「使用者指示（直接要求）優先」，這是方法論**文件化的覆寫管道**；邊界段就是那個使用者指示。
CT 不跟方法論硬碰，而是走它自己留的門。

### 為什麼預設 `warn` 而不是 `block`：實測依據

這不是猜的。CT 在預覽期間跑了三輪真實 session 驗證（權威檔 § 與 hook／session 路由的相處規則 第 3 點、§ 衝突與防護 C1／C9／C10 記錄結論）：

| 驗證 | 環境 | 沒有邊界段 | 有邊界段 |
|---|---|---|---|
| **V1** | Claude Code＋pstack | 2 次中 **1 次**進 `pstack:poteto-mode`（在落點檢查之後、標 `IN_PROGRESS` 之前），而且**回報區完全沒寫** | **3/3** 沒呼叫任何 pstack skill，回報區主動聲明遵守 |
| **V2a** | Codex＋pstack（hook 已信任） | **2/2** 進 poteto-mode，其中 1 次回報區沒寫 | **2/2** 擋住 |
| **V2b** | Claude Code＋pstack＋Superpowers（雙注入） | **0/3** 呼叫任何 skill；4 個沒有邊界段的 session 回報區**都沒提到**注入存在 | 兩家都列的邊界段 **2/2** 有效，並主動寫 `### 方法論執行紀錄` |

讀這張表的方式：

- **邊界段每次都有效**（7/7），所以值得每張工單都加——而且要塔台自動加，不能靠開單的人記得。這就是 `warn` 的意思：**自動加邊界段＋派工摘要提示**，不是只提示。
- **沒有邊界段時有風險、但不是每次**，所以不必用 `block` 擋掉整個派工。`block` 留給完全不想讓方法論碰 CT 工單的專案自選；`off` 不檢查。
- **最危險的不是「進了方法論」，而是「進了卻沒寫」**：V1、V2a 都出現塔台只看工單完全不知道的情況。所以防線 ② 是硬規則，Codex 沒有 Skill 工具，讀了方法論的 `SKILL.md` 照著做也算呼叫。
- **compact 後的邊界不能靠運氣**：V1 的 compact 測試邊界仍有效（n=1），但 Worker 沒有先重讀工單，是 compact 摘要剛好保留了邊界資訊。摘要內容由模型決定、不保證，所以有了防線 ④。
- 樣本都小，只能說「邊界段有效、無邊界有風險」，不能給機率。

beta.1 前的隔離試用（§ 隔離試用）又跑了幾輪有邊界段的工單：P1b 的雙注入工單，邊界段讓 Worker 只叫允許的 2 個 pstack skill、0 次 `superpowers:*`（1/1）；
雙注入＋疊加也照邊界段走（n=1）。結論不變，`warn` 維持預設。但 P1b 也找到邊界段**沒寫到**的一個縫：被允許的 skill 自己開的子代理（Q-1，見 § 隔離試用）。

### 衝突時誰贏

① CT 核心規則 ＞ ② 工單的 `### 方法論邊界` ＞ ③ 該層負責 adapter 的流程 ＞ ④ 其他已安裝方法論的常駐注入（對它不負責的層一律不採用）。
方法論的某一步跟 ①～③ 衝突，Worker 跳過並在回報區寫原因——**不是停下工單的理由**（`ct-exec/SKILL.md` § Methodology (v6.0.0-pre.1+)）。

兩個常被問的預設：方法論自己開的寫入型子代理預設 `deny`（要開放得在工單加〈方法論子代理授權〉段，`work-order-template.md` § 撰寫方法論子代理授權（v6.0.0+））；
交付層預設 `none`，方法論想開 PR、release 的步驟一律跳過。方法論想問使用者的題目照 ct-exec 規則走，yolo 下改問塔台（`work-order-lifecycle.md` § yolo 提問通道）。

---

## hook 信任：塔台不替使用者決定

Codex 的外掛 hook 要使用者**信任**之後才會執行；V2a 實測，`codex exec` 遇到未信任的 hook 是靜默略過，不卡住也不提示。

**塔台不替使用者信任 hook**：不寫 Codex 設定檔的信任值、不透過其他程式代為寫入、不用略過信任的旗標。
理由：Codex 寫明信任後的 hook 可以在 sandbox 外執行——信任等於核准在 sandbox 外執行程式，這是使用者的決定，不在塔台權限內
（`methodology-adapters.md` § 與 hook／session 路由的相處規則 第 5 點）。這跟 Layer 1 寫入規則同一種精神：碰到使用者層級的授權，塔台只提示、不代簽（`governance.md` § Layer 1 寫入機制）。

派 codex Worker 前，塔台依 adapter 的 `hook_probe.codex` 看 hook 狀態：

| hook 狀態 | 會發生什麼 | 塔台怎麼做 |
|---|---|---|
| `trusted` | 注入會到 | 照 `methodology_guard`（`warn` = 自動加邊界段；V2a：Codex 邊界段 2/2 有效） |
| `untrusted`／`modified` | hook 不執行，但 BAT 派出的互動 TUI 會在開工前停在「Hooks need review」畫面 | 派工摘要提示使用者先在自己的終端機開一次 `codex` 處理 review，或照 adapter 的開關關掉注入；邊界段照樣加（使用者可能選信任） |
| 外掛停用 | 不注入 | 不用處理 |

「Hooks need review」停住時，BAT 派工表現為 exit `8`（分頁在、啟動未確認），**不是斷點 D**——那個畫面不送 BAT 看得懂的序列。
處理照 `auto-session.md` § Worker 啟動確認（`--wait-started`，v5.6.0+）：不重派（`bat-integration.md` § 斷點 D 的「還看不到的情況」）。
`modified` 的意思是：方法論升版後，之前信任過的 hook 會再要求 review 一次——所以「信任過」不是一勞永逸（推論）。

---

## 雙注入：兩家方法論同時開著

一台機器可能同時裝了兩個會注入的方法論（V2b 測的是 pstack＋Superpowers）。規則：**兩家以上注入開著，一律至少 `warn`**——
邊界段每一家都列，派工摘要另標一行「雙注入」（`methodology-adapters.md` § 衝突與防護 C10）。

V2b 的發現：兩段注入都送達、也都進了 Worker 的 context（Superpowers 的注入 3,417 bytes，是 pstack 的 3.4 倍，文字也強硬得多），
但沒有邊界段時 0/3 呼叫任何 skill；兩家都列的邊界段 2/2 有效。所以**維持「至少 `warn`」、不升 `block`**；
建議（不強制）一台機器只開一家注入。

beta.2 起這一節是**共存防護**，不是引入建議：Superpowers 定位為不建議引入（§ 方法論不是一定要引入），
權威檔 C10 原本「其他家改用 ②／③」的建議，對 Superpowers 改成「在 CT 下沒有實測效益，已裝的機器照 C1、C5、C10 共存」。雙注入的偵測與邊界段規則本身不變。

順帶一個量測教訓：`claude plugin details` 對 hook 寫「no model context cost」，但 hook 每個 session 實際注入好幾 KB。
adapter 的 `always_on_tokens`（常駐 token 成本，列在派工摘要）**要含 hook 實測注入量**，只抄 `plugin details` 會低估（C14）。
沒有 adapter 的方法論（例 Superpowers）沒有這個值可讀：beta.1 起派工摘要寫「`always_on_tokens` 未量測」，不填估值（Q-4，見 § 隔離試用）。

P1b 再跑一次雙注入，補了三件事：

- **雙注入＋疊加已驗（n=1）**：主方法論 bmad、執行層 pstack，Superpowers 注入開著列為【不使用】。Worker 依層先叫 `pstack:poteto-mode`、再叫 `bmad-code-review`，0 次 `superpowers:*`，pstack 沒有越出執行層。
- **Superpowers 的 SessionStart matcher 沒有 `resume`**：塔台用 `--resume` 接續時，塔台 session 只收到 pstack 的注入。
  但塔台仍從安裝檔偵測到 Superpowers——所以 C10 的判斷**不依賴塔台自己有沒有收到注入**，這是刻意的：偵測靠檔案，比靠「我有沒有被注入」穩定。
- 這次量到的 Superpowers 注入是 3,616 bytes（V2b 3,417 bytes）；兩次數字不同（原因未查，推論是上游版本不同），所以 `always_on_tokens` 要實測、不能抄舊值。
  beta.2 前的 P3 又量到 7,906 bytes（`SessionStart:startup`）；P3 記錄的 Superpowers 版本與 V2b／P1b 相同（7.0.1），所以「上游版本不同」這個推論站不住，
  差異原因仍未查——再一次說明這個值只能實測。

---

## 隔離試用：P1／P1b 找到什麼、beta.1 怎麼修

### 為什麼先試用再出 Beta

beta.1 不是把 pre.1 的版號改掉就好。pre.1 的 V1／V2a／V2b 驗的是「注入會不會搶路由」，沒有把 v6 塔台**從頭到尾**跑一遍。
所以出 Beta 前先做了兩輪隔離試用：把 `CLAUDE_CONFIG_DIR` 指向一個暫時的設定目錄、在裡面裝 v6.0.0-pre.1，拿一個真實專案的複本，跑真實的塔台與 Worker session——
**不碰使用者主環境**，試完前後比對主環境沒有變動。

| 輪 | 範圍 | 結果 |
|---|---|---|
| **P1**（T0314） | v6 塔台在舊 5.x 狀態檔上啟動；BMAD 預設的小任務；疊加（主方法論 bmad、執行層 pstack） | 舊專案正常啟動，第一次寫入就補上機器可讀摘要；小任務不加方法論段落、跑到 DONE，回報區與 5.12.x 同構；一般疊加（pstack 執行＋bmad 審查）已驗 n=1；找到 P-1～P-5 |
| **P1b**（T0315） | 整張抽換成 pstack；pstack＋Superpowers 雙注入；嘗試觸發 Superpowers HARD-GATE；雙注入＋疊加 | 抽換走完整流程；雙注入照規則；HARD-GATE 0/1 未觸發；雙注入＋疊加已驗 n=1；找到 Q-1～Q-4，P-5 重現 4/4 |

兩輪的結論都是**沒有阻擋 beta.1 的問題**：找到的都是規則措辭或 adapter 宣告層級，契約仍是 `ct-methodology-adapter/v1`、沒有新增欄位。
這就是為什麼 beta.1 的 CHANGELOG 只有 Fixed 與 Changed，沒有契約變更。

### 找到什麼、怎麼修

| 代號 | 試用時看到什麼 | beta.1 改成什麼 | 為什麼這樣修 |
|---|---|---|---|
| **P-1** | 沒有任何層由 adapter 負責的工單，回報區少了 tracker 段；兩份權威檔說法互相矛盾 | 主方法論有 `tracker`（bmad 的 `sprint-status.yaml`）時，保留 `### 方法論狀態回寫` | 與 5.12.x 的 `### sprint-status.yaml 已更新` 一致：升級不該改變回報區的形狀 |
| **P-2** | pstack 注入開著時，塔台回覆改用英文（P1 2 次；P1b 5 輪都是中文，合計 n=2／7） | 塔台語言規則加一句：方法論注入不改變對話語言；C1／C8 註明塔台 session 也會收到注入 | 原本的防護（邊界段、回報區照模板）都寫給 Worker，忘了塔台也是 session、也會被注入。成因是注入還是 session 狀態仍是推論，所以只補規則、不加機制 |
| **P-3** | 隔離目錄下，塔台找全域設定仍去家目錄的 `.claude/`（P1、P1b 都出現） | 見 § 全域路徑 | — |
| **P-4** | 沒有 scratchpad 的 Worker 把審查工作檔寫到 **repo 的上一層**（P1 1 次；P1b 0 次） | 邊界段寫明退路：系統暫存目錄（`$TMPDIR`／`%TEMP%`）下的 `ct-<工單號>/`，收尾刪除，repo 外不留檔 | 「放 scratchpad」對 headless `claude -p`、Codex、一般終端機等於沒寫；repo 的上一層在真實環境常是別的 repo 或共用目錄 |
| **P-5** | `methodology_ambient` 的事件寫成「SessionStart hook 注入」之類，不照權威格式（P1 1 次、P1b 4/4） | `ct-exec` § Methodology 直接附三行範例；權威檔加「❌ 不要寫／✅ 要寫」對照 | 重現率這麼高，代表規則的**寫法**有問題，不是 Worker 粗心；給範例比多加一段說明有效（推論） |
| **Q-1** | 【只允許】擋不住被允許 skill 自己開的子代理：`pstack:thermos` 開了 2 個**背景**審查子代理，子代理內又各叫一個清單外的 pstack skill；Worker 回報「其他 pstack 都沒用」，塔台收單也沒發現（子代理確實唯讀） | 【只允許】涵蓋上列 skill 自己呼叫的子 skill 與自帶的唯讀審查子代理（含背景）；回報區要寫子代理數、是否背景、子代理內叫了哪些 skill；pstack adapter 宣告 `only_in`、`background` | 這些子代理是 workflow 本身的一部分，禁止它等於不能用這個 skill。真正的風險跟防線 ② 一樣是「**用了沒寫**」，所以改成允許＋照實回報 |
| **Q-2** | 環境變數檢查的規則文字本身會印出值 | 見 § 環境偵測只列名稱 | — |
| **Q-3** | 想觸發 Superpowers HARD-GATE 卻沒觸發（0/1）：工單有 `methodology.layers` 時，Worker 依優先序第 ④ 項不採用不負責本單的注入，拿掉邊界段也一樣 | C5 補上實測證據與觸發條件：要 `methodology_guard: off`＋工單沒有 `methodology` 才可能出現 | 「未驗」要寫出**為什麼沒驗到**，否則下一個人只會以為沒人去測。這次的結論是 v6 正常流程下幾乎遇不到（推論）。beta.2 前的 P3 照這個條件再測 2/2 仍未觸發，觸發條件改寫（§ 實測 P3） |
| **Q-4** | 沒有 adapter 的注入方法論（Superpowers）沒有 `always_on_tokens` 可讀，塔台只寫「沒量到」 | 派工摘要寫「`always_on_tokens` 未量測」、不填估值；附量法：在隔離設定目錄跑 `claude -p --output-format stream-json --verbose`，看 `hook_response` 的注入長度，量到的數字寫進專案本地 adapter | 估值一旦寫進派工摘要就會被當成事實；寧可明寫未量測，並把量法寫下來讓需要的人補 |

P-2、P-4、Q-1 的新規則與「啟用即產生空索引」一樣，是**文件規則、尚未實機跑過**（beta.2 的〈已知未驗〉第 9 項）。

### `ct-adapter-pstack` 0.2.3

外部 adapter 跟著試用結果升了一版（`adapter_version` 0.2.2 → 0.2.3）：

- `session.subagents` 宣告 `only_in`（只有 `poteto-mode`、`thermos`、`interrogate` 會開子代理）與 `background`（Q-1）
- `tested_version` 0.9.103：P1、P1b 兩輪實測的 pstack 版本；`version_range` 不變，`pinned_ref` 仍指 0.9.102 的 commit
- 偵測路徑照 `${CLAUDE_CONFIG_DIR:-~/.claude}`／`${CODEX_HOME:-~/.codex}`（P-3）
- README 加〈引入方式建議〉，〈還沒驗證的〉改寫 poteto-mode 委派／開 PR 那一項（〈已知未驗〉第 5 項）

Beta 的發行物裡 `ct-adapter-pstack` 是獨立的 zip，不在 `control-tower` 裡；不用 pstack 就不必裝。

beta.2 再升 0.2.4，**只改 README 與一句說明**：〈引入方式建議〉加「選用」定位（已在用 pstack 才裝，CT 不預設、不主動推薦）與「③ 已在 P3 實測有效、pstack 的 ②／③ 未實測」，
`SKILL.md` 加一句選用說明；描述檔的欄位與值不變（`tested_version` 仍 0.9.103）。

---

## 實測 P3：③ 部分參考與 HARD-GATE（beta.2）

（權威：`methodology-adapters.md` § 引入方式 表下第 1 點、§ 衝突與防護 C1、C5；`auto-session.md` § BAT 內部終端路由 › 偵測條件）

### 為什麼還要再測一輪

beta.1 留下兩個「依規則推得、沒有實測」的大項：引入方式 ③（mattpocock/skills 的副本做法是新寫的），以及 Superpowers HARD-GATE（P1b 0/1 沒觸發，C5 只寫了推測的觸發條件）。
這兩項直接決定 beta.2 要怎麼寫：③ 有沒有效，決定 mattpocock 能不能當範例；HARD-GATE 會不會擋住 Worker，決定 Superpowers 的共存防護夠不夠。
所以 beta.2 前照 P1／P1b 的方式再做一輪隔離試用（P3，9 次 `claude -p`）：`CLAUDE_CONFIG_DIR` 指向暫時目錄、真實專案的複本、試完比對主環境沒有變動。

### 找到什麼、beta.2 怎麼修

| 代號 | 試用時看到什麼 | beta.2 改成什麼 | 為什麼這樣修 |
|---|---|---|---|
| ③ 實測 | 副本 0 次被自動叫用（4 個 session）；塔台照規則寫【只允許】；Worker 3/3 照做、3/3 記錄 | 權威檔 ③ 寫成**已實測**，② 仍未實測 | 有實測才能把 mattpocock 當範例；② 沒測就照實寫未測 |
| **P3-1** | `methodology_guard: off`＋工單沒有 `methodology`、yolo 下，Superpowers 注入送達，**2/2** 仍 0 次叫 `superpowers:brainstorming`、沒停下、沒提問（連同 P1b 共 0/3） | C5 的觸發條件改寫：Worker 依 `ct-exec` 優先序第 ④ 項不採用不負責任何層的注入；沒有指名 Superpowers 的工單不會被它擋住（n=2） | beta.1 寫的「這種條件下 Worker 才會採用注入」跟實測不符；文件寫錯的條件，比沒寫更會誤導 |
| **P3-2** | 權威的 bash 寫法 `env \| cut -d= -f1` 要放行 `env` 才跑得動（白名單下 9 次全擋）；Worker 3 次用 `printenv` 一次讀多個名稱，含不在例外清單的變數 | 見 § 環境偵測只列名稱 › beta.2 的新寫法 | 規則寫的指令自己要放行危險的 `env`，等於逼人開大門；一次讀多個名稱，例外清單就守不住 |
| **P3-3** | 標準 plugin 安裝時塔台 0/1 被叫用 | C1 ⑤「塔台 session 一樣會被叫到」改成「也可能被叫到」並附次數（n=1） | 「一樣會」說得比證據強；「不會」也說不出口，所以寫「也可能」加樣本數 |
| **P3-4** | 副本有 `disable-model-invocation: true`，Worker 只能以路徑讀 | `ct-exec` 寫明 ③ 副本在 Claude Code 也只能以路徑讀，讀了照做算一次呼叫 | 和 Codex「讀 `SKILL.md` 照做也算呼叫」同一個道理，免得 Worker 以為沒走 Skill 工具就不必記 |
| **P3-5** | 部分層用 ③ 時，塔台不知道其他層怎麼辦 | 權威表 ③ 列補「不為副本寫 `methodology` 層；其他層照解析步驟」 | P3 的塔台自己做對了（審查層仍給 bmad），把它寫成規則 |
| **P3-6** | 副本裡「先問使用者」的步驟，塔台逐條在邊界段對照成 CT 的處理，Worker 照做沒停 | § ③ 的做法 補一點：副本要問使用者或等核准的步驟，在邊界段逐條寫成 CT 的處理 | 通用條文（不得因方法論要問使用者而停下）有效，但逐條對照更明確 |

P3 的結論是**沒有阻擋 beta.2 的問題**；全部只改文件，契約仍 `ct-methodology-adapter/v1`、沒有新增欄位，所以 beta.2 從 beta.1 升級沒有設定變更。
也有 P3 沒驗到的：工單**明確指名** `superpowers:brainstorming` 時的 HARD-GATE、副本「先問使用者」在 yolo 下改問塔台（試用工單預先回答了，這條路徑沒出現）、
headless 提問備援、Codex 端 `allow_implicit_invocation`、②、副本在 BAT worktree 下的可見性——都列進〈已知未驗〉。

---

## BUG／PLAN／EXP 預設開啟

（權威：`bug-plan-system.md` § 啟用與索引檔、§ 索引格式；`tower-config.md` § 可用選項）

### 改了什麼

- `enable_bug_tracking`、`enable_plan_tracking`、`enable_experiments` 預設由 `false` 改成 `true`。
- 啟用時（含預設啟用）**立即**產生空的 `_bug-tracker.md`、`_backlog.md`——塔台啟動時，或 `*config` 改成 `true` 的當下——不等第一次 `*sync`。
  檔案已存在就不動；EXP 沒有索引檔；改回 `false` 不刪檔。兩個索引屬塔台私有狀態，Worker 不產生、不修改。
- 索引格式原本指向一個不存在的段落（文件漂移），beta.1 補成 `bug-plan-system.md` § 索引格式，作為唯一權威定義。

### 為什麼

- **BAT 面板讀這兩個檔**：BAT 指揮塔面板的「待辦池」讀 `_backlog.md`、「臭蟲」讀 `_bug-tracker.md`。以前要等第一次 `*sync` 才產生，
  檔案不存在時面板是空的——使用者看到一個空面板，卻不知道是因為還沒同步。這件事實際發生過，才把「啟用即產生」寫成規則。
- **預設開啟是使用者的決定**：BUG／PLAN 先改，EXP 隨後一併納入。EXP 開著沒用時成本近乎 0：啟動與 `*sync` 只多一次 `EXP-*.md` 檔名比對，
  `*exp` 的規格用到才載入（推算，未實測）。
- 這是 v6 唯一一個「**什麼都不設也會不同**」的變化，所以用「設定明寫 `false` 的照舊」守住相容：不要的人寫一行就回到原狀。

### 升級影響

| 你的設定 | 從 5.12.x 升到 v6 Beta（beta.1 起）之後 |
|---|---|
| 明寫 `true` | 不變 |
| 明寫 `false` | 不變，照舊關閉 |
| **沒寫這三個鍵** | **會啟用**，塔台下次啟動產生兩個空索引 |

不要就在專案或全域設定明寫 `false`（例：`*config enable_bug_tracking false`）。本 Guide 沿用章寫到舊預設的三處
（`concepts.md` § 多單據類型哲學、`work-order-lifecycle.md` 開頭、`ecosystem.md` § 設定系統）已一併改寫。

---

## 環境偵測只列名稱

（權威：`auto-session.md` § BAT 內部終端路由 › 偵測條件；「只列名稱」與穩定版 5.12.7 起是**同一個修正**，沿用章 `bat-integration.md` § 兩組環境變數，兩個角色 也已更新；
beta.2 再改 bash 寫法與「一個變數一個指令」，目前只在 v6 Beta）

### 改了什麼

環境偵測與檢查**只判斷有無、只列變數名稱**，不用會列出整組變數的指令：PowerShell 加 `Select-Object -ExpandProperty Name`，
bash 用 `compgen -e | grep -E '^(BAT|CT)_' | sort`（beta.1 是 `env | cut -d= -f1`，見下方 › beta.2 的新寫法）。`BAT_REMOTE_TOKEN` 任何時候只記「已設定」。
判讀邏輯（`shell env visibility mismatch`、塔台派工的五個變數、Worker 通知的三個變數）完全不變。

### 為什麼

- **規則文字本身就教了會外洩的指令**：舊寫法 `Get-ChildItem Env:BAT* | Sort-Object Name` 會把值一起印出來，包含 `BAT_REMOTE_TOKEN`。
- **P1b 實測**：塔台與 Worker 照規則判斷 BAT 時，多次嘗試會輸出變數值的指令。試用環境有白名單，全部被擋下；一般 BAT 分頁沒有白名單，就會直接進對話紀錄。
- **「先印再遮」不行**：用 `sed` 之類遮罩，只遮得到名稱含 `TOKEN` 的變數，別的祕密照樣出去。
- 權杖雖然是分頁專屬的範圍權杖（`bat-integration.md` § 權限與分頁角色），仍是憑證；工具輸出會留在對話紀錄裡，也可能被分享。

**明列例外**（刻意只讀**單一**非祕密變數，照舊）：判斷模式的 `CT_MODE`、`CT_INTERACTIVE`；落點檢查記錄的 `BAT_WORKSPACE_ID`；
worktree 的 `CT_HOME`、`CT_WORKTREE*` 證據。**一次讀一個變數、一個指令**（beta.2 寫明，見下方）。

### beta.2 的新寫法：`compgen -e`、一個變數一個指令

P3 照 beta.1 的規則跑，發現規則本身的寫法會走樣（§ 實測 P3 › P3-2）：

| 寫法 | P3 看到什麼 | 問題 |
|---|---|---|
| bash `env \| cut -d= -f1 \| …` | 有指令白名單的環境 9 次全被擋 | 要讓它跑，就得放行 `env`；而放行 `env` 等於放行「印出整組變數與值」——規則為了只列名稱，反而逼人打開最危險的那扇門 |
| `printenv A B C` 一次讀多個 | Worker 3 次這樣讀，其中混進不在例外清單的變數 | 例外清單是「刻意只讀單一非祕密變數」；一個指令塞多個名稱，清單外的變數很容易跟著被讀出來 |

所以 beta.2 改成：

- **bash 列名稱用 `compgen -e`**：它是 bash 內建，只輸出變數名稱、不碰值，也不需要放行 `env`；後面接 `grep -E '^(BAT|CT)_'` 篩出要看的。
  PowerShell 寫法不變（`Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object`）。
- **明列例外一個變數一個指令**：例 `printenv CT_MODE`，再另一個指令 `printenv CT_INTERACTIVE`；不把多個名稱放進同一個 `printenv`，
  也不把讀值的指令和列名稱的指令串成同一行。一個指令只讀一個名稱，看指令就知道讀了什麼，白名單也能逐個放行。

這次沒有任何一次嘗試印出權杖的值（P3 裡提到 `BAT_REMOTE_TOKEN` 的指令都是判斷有無）；改的是「照規則做也會走樣」的寫法。
`ct-exec`、`control-tower`、`ct-done`、`ct-help`、`yolo-mode.md`、工單模板、安裝指南都同步引用這段權威。

---

## 全域路徑：`CLAUDE_CONFIG_DIR`／`CODEX_HOME`

（權威：`data-layer-architecture.md` § 路徑解析（P-3，T0314））

### 改了什麼

CT 文件寫的 `~/.claude/…` 一律解讀為 `${CLAUDE_CONFIG_DIR:-~/.claude}/…`，`~/.codex/…` 解讀為 `${CODEX_HOME:-~/.codex}/…`。
塔台讀全域設定、偵測 adapter 都照這張對照；變數沒設時與 5.12.x 相同。Codex 端的 CT 資料層仍在 `${CLAUDE_CONFIG_DIR:-~/.claude}/control-tower-data/`（CT 資料層不分 runtime）。
權威檔只改了這張對照與會被機器讀的偵測路徑；其他文件仍寫 `~/.claude/control-tower-data/`，一律照對照解讀。

beta.5 在這張對照加了**一個例外**：plugin 目錄不照上面的規則只取一處，`~/.claude/plugins/` 與設了 `CLAUDE_CONFIG_DIR` 時的 `${CLAUDE_CONFIG_DIR}/plugins/` **兩處都算** Layer 1——當時 `CLAUDE_CONFIG_DIR` 會不會連 plugin 目錄一起搬走還沒有驗證。
之後實測確認會搬，beta.8 照穩定版 5.14.4 改成只有一處：`${CLAUDE_CODE_PLUGIN_CACHE_DIR:-${CLAUDE_CONFIG_DIR:-~/.claude}/plugins}`，例外刪除，v6 跟穩定版在這裡不再有結構差異。為什麼當初寧可多算一處、後來又為什麼改回一處，見主教材 `three-layer-arch.md` § plugin 安裝路徑也是 Layer 1（v5.14.0／v6.0.0-beta.5 條文）。

### 為什麼

P1 在隔離目錄試用時，塔台找全域設定直接去家目錄的 `.claude/control-tower-data/`，沒有照 `CLAUDE_CONFIG_DIR`；P1b 再次出現。
那兩次主環境剛好沒有那個檔，沒有造成影響；但隔離試用、或同時用好幾個設定目錄的人，會**讀到主環境的設定**——正是隔離想避免的事。
`bmad.yaml` 的偵測路徑也寫死 `~/.claude`，同一個問題。

### 試用 Beta 的建議

Beta 與穩定版並行，建議裝在**隔離設定目錄**試：設 `CLAUDE_CONFIG_DIR`（Codex：`CODEX_HOME`）指向另一個目錄，把 Beta 裝在那裡，主環境的 5.15.0 不受影響。
P1／P1b／P3 就是這樣跑的，beta.1 修了路徑之後，隔離試用才真正隔離。安裝與升級步驟見 CT 安裝指南 § 2.59、§ 2.58、§ 2.57、§ 2.56、§ 2.55、§ 2.54、§ 2.53、§ 2.52、§ 4.1。
隔離目錄裡也一樣只用 zip 裝 Beta，**不要用 marketplace 裝 CT**：beta 沒有 CT plugin，plugin 安裝指令裝到的是穩定版 5.x（§ beta.5：plugin 安裝就緒）；只裝 `bmad-guide` 不受這條限制（§ beta.6）。

有一個例外要知道（推論）：P3 的隔離塔台回覆裡出現了使用者家目錄全域指示檔裡的字串，隔離目錄與試用專案都沒有這個字串——
設了 `CLAUDE_CONFIG_DIR` 時，使用者層級的指示可能仍從原本的位置載入或由帳號同步帶入。所以「隔離設定目錄」隔離的是 CT 的安裝與設定，不等於「沒有使用者指示」。

---

## `_tower-state.md` 機器可讀摘要

v6（自 pre.1 起）另一個新東西跟方法論無關：`_tower-state.md` 開頭加一段 **YAML frontmatter 摘要**，給 BAT 的總覽讀。
穩定版 5.13.0 也補進了同一份契約 v1，設計理由已寫進主教材 `three-layer-arch.md` § Tower State（`_tower-state.md`）；v6 這邊 beta.3、beta.4、beta.5 都沒有改。

| 欄位 | 內容 |
|---|---|
| `schema_kind` | 固定 `tower-state` |
| `summary_version` | 摘要格式版號，目前 `1` |
| `updated_at` | 最後更新時間，取系統時間 |
| `session`（選填） | 目前塔台 session 的說明 |
| `next_ids`（選填） | **下一個可用編號**（不是最大編號），例：`workorder`、`decision` |
| `todo`（選填） | 待辦；外部讀者只顯示前 5 則 |

設計重點（`memory-protocol.md` § 機器可讀摘要（YAML frontmatter））：

- **它是 CT 對外的契約**：欄位依 BAT 契約 v1，名稱、型別、語意不得自行修改。新增欄位不升版；改既有欄位才升 `summary_version`，而且要先通知 BAT、等回覆（`advanced-patterns.md` § 五種協調類型）。
- **進行中工單刻意不放**：BAT 自己從 `_ct-workorders/T*.md` 的 frontmatter `status` 算，避免兩份資料不一致——這是「事實來源只有一個」的又一次應用（`concepts.md` § 事實來源：兩段式）。
- **摘要只供外部顯示，塔台恢復狀態以本文為準**：兩者不一致時以本文重寫摘要。舊專案沒有摘要不是錯誤，塔台下次寫入時直接補上，不需要遷移工具。
- 塔台每次寫 `_tower-state.md` 都同步刷新摘要（至少 `updated_at`）。

BAT 端：總覽讀這份摘要需要 BAT **`>= 0.7.1-pre.7`**（預覽版）；「下一個編號」與「待辦」要 CT 寫入摘要才看得到（v6 `>= v6.0.0-pre.1`；穩定版 `>= v5.13.0`）。
跟其他 BAT 功能一樣，CT 不預先判斷 BAT 版本（`bat-integration.md` § 版本對照表）。

---

## beta.3：狀態衛生與 BAT 塔台面板讀取契約

**同批規則穩定版 5.13.0 也有**（CT `docs/CHANGELOG.md` `[6.0.0-beta.3]`），所以本章不重講，下表只指向主教材已寫好的章節：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| BAT 塔台面板讀取契約（為什麼頁面會空、400 KB 預算、怎麼量） | `bat-integration.md` § BAT 塔台面板讀取契約 | `memory-protocol.md` § BAT 塔台面板讀取契約 |
| 決策日誌的格式與收斂 | `three-layer-arch.md` § `_decision-log.md` | `decision-log-system.md` § 格式規則、§ 收斂 |
| BUG／PLAN 索引格式（`🔴 High`、改狀態同一批重建索引） | `three-layer-arch.md` § `_bug-tracker.md` 和 `_backlog.md` | `bug-plan-system.md` § 索引格式 |
| BUG 結案判準與 `closed_reason`、未結 BUG 清理提示 | `work-order-lifecycle.md` § BUG 生命週期 › 結案判準與 `closed_reason` | `bug-plan-system.md` § 結案判準、§ 未結 BUG 清理提示 |
| `PARTIAL` 當下收尾 | `work-order-lifecycle.md` § resolved PARTIAL → DONE | `work-order-system.md` § PARTIAL 當下收尾（含 resolved `PARTIAL` 補正） |
| 客戶驗收不回歸閘（可選） | `work-order-lifecycle.md` § 客戶驗收不回歸閘 | `work-order-template.md` § 撰寫〈相關通過案例〉；`ct-exec/SKILL.md` § Phase 2 |
| 三個新設定（`bug_review_open_threshold`、`bug_review_stale_days`、`customer_acceptance_gate`） | `ecosystem.md` § 設定系統 | `tower-config.md` § 可用選項 |

只跟 Beta 有關的三點：

- **從 beta.2 升級不需要遷移**：三個新設定不設就用預設（`customer_acceptance_gate` 預設 `off`）；舊的 `_bug-tracker.md`／`_backlog.md` 在下一次 `*sync` 照新格式重建。
  方法論契約仍 `ct-methodology-adapter/v1`，`ct-adapter-pstack` 內容沒改、仍 0.2.4
- **`_tower-state.md` 機器可讀摘要**：5.13.0 補進的是 v6 自 pre.1 起就有的契約 v1，beta.3 沒有改（§ `_tower-state.md` 機器可讀摘要）
- **本版新規則的已知未驗**是〈已知未驗〉第 10～13 項

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.3]`；安裝與升級步驟見 CT 安裝指南 § 2.54）

---

## beta.4：通知用完整工單 ID 與 BAT 塔台面板讀取契約

**同批規則穩定版 5.13.1 也有**（CT `docs/CHANGELOG.md` `[6.0.0-beta.4]`），所以本章不重講，下表只指向主教材已寫好的章節：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| 通知、提問、`--source` 一律用工單完整 ID（含前綴、不截短），以及為什麼範本會教錯 | `work-order-lifecycle.md` § 回報與通知用完整工單 ID | `work-order-system.md` § 回報與通知用的工單 ID |
| Worker 送出前與 frontmatter `id` 比對 | `work-order-lifecycle.md` § 回報與通知用完整工單 ID（三層修法表） | `work-order-system.md` § 回報與通知用的工單 ID；`ct-exec/SKILL.md` § BAT Notify And Fallback、`ct-done/SKILL.md` § BAT Notify |
| 塔台缺前綴容錯（只保住收單；缺前綴不算斷點 A，同號多張或找不到才是） | `work-order-lifecycle.md` § 回報與通知用完整工單 ID、`runtime-dispatch.md` § 斷點 | `work-order-system.md` § 回報處理流程 › 回報 ID 對不上時；`yolo-mode.md` § 斷點 A：Worker 回報非預期狀態 |
| BAT 怎麼用 `--source` 對 Worker 分頁、對不上為什麼標不了 Done | `bat-integration.md` § Worker 執行與通知 | `work-order-system.md` § 回報與通知用的工單 ID |
| BAT 塔台面板讀取契約對齊 BAT `0.7.1-pre.9`（「無法讀取 <檔名>」、`critical` 算 High、400 KB 預算為什麼保留） | `bat-integration.md` § BAT 塔台面板讀取契約 | `memory-protocol.md` § BAT 塔台面板讀取契約 |
| 索引格子照舊寫 `🔴 High（critical）` | `three-layer-arch.md` § `_bug-tracker.md` 和 `_backlog.md` | `bug-plan-system.md` § 索引格式 |

只跟 Beta 有關的三點：

- **從 beta.3 升級只換 skill 檔案**：沒有新命令、新設定，不需改設定或工單；`control-tower`、`ct-exec`、`ct-done` 都有改，8 個 skill 同批換；BAT 不必升級。
  方法論契約仍 `ct-methodology-adapter/v1`，`ct-adapter-pstack` 內容沒改、仍 0.2.4
- **穩定版 5.13.1 另改的 BMad 舊說法**（Quick Flow、`bmad-automator` 替代、`v6.10` 標題、bmad-guide 範例版號），v6 已由 `adapters/bmad.yaml` 承接，beta.4 不需改；
  v6 只把派工摘要與回報確認範例裡 `bmad-project-context` 的產出改成 `AGENTS.md` 的專案上下文區塊（`work-order-system.md`）
- **本版新規則的已知未驗**是〈已知未驗〉第 14、15 項；第 10 項改寫成 BAT `0.7.1-pre.9` 的現況

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.4]`；安裝與升級步驟見 CT 安裝指南 § 2.55）

---

## beta.5：plugin 安裝就緒

**同批規則穩定版 5.14.0 也有**（CT `docs/CHANGELOG.md` `[6.0.0-beta.5]`），所以本章不重講，下表只指向主教材已寫好的章節：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| plugin marketplace 是什麼、和 zip 的關係、手動與 plugin 並存時誰生效、自動更新、從 zip 遷移 | `governance.md` § plugin marketplace：另一種安裝方式 | `version-governance.md` § 安裝／升級流程 › plugin 安裝／升級 |
| plugin 安裝路徑也是 Layer 1（只能用 plugin 指令寫入、不備份） | `three-layer-arch.md` § plugin 安裝路徑也是 Layer 1 | `data-layer-architecture.md` § 寫入規則（開頭 plugin 那一項、Q2～Q4） |
| 依安裝方式的呼叫寫法（Claude `/ct-exec`；Codex 手動 `$ct-exec`、plugin `$ct:ct-exec`） | `ecosystem.md` § 三軌前綴：`*`、`/`、`$`；`integration.md` § Codex 整合 | `auto-session.md` § 依安裝方式的 skill 呼叫字串 |
| Codex 搭配 BAT 派工（beta.5 時寫「繼續用 zip」；beta.6 起依 BAT 版本，見 § beta.6） | `bat-integration.md` § 誰負責 `/` 還是 `$` | `version-governance.md` § plugin 安裝／升級 › Codex 搭配 BAT 派工：依 BAT 版本（beta.6 改名） |
| playbook 不得寫進 plugin 安裝路徑 | `integration.md` § Playbook 引擎 | `data-layer-architecture.md` § 寫入規則 |

只跟 Beta 有關的四點：

- **beta 沒有 plugin，不要用 marketplace 裝 beta**：marketplace `control-tower` 只上架穩定版（腳本拒絕帶 `-` 的版號），`6.0.0-beta.N` 照舊用 zip 手動安裝。
  在 beta 環境執行 `claude plugin install ct@control-tower`（或 Codex 的 `codex plugin add`），裝到的是**穩定版 5.x**，會和手動安裝的 beta 並存；
  不帶前綴的 `/ct-exec`、`$ct-exec` 用的是手動那份，所以看起來沒事，其實機器上同時有兩個版本（`governance.md` § plugin marketplace：另一種安裝方式 › 手動與 plugin 並存時誰生效）。
  v6 的 plugin 條文是**正式版上架後**的規格；上架後的呼叫寫法與穩定版相同：Claude `/ct-exec`、Codex 手動 `$ct-exec`／plugin `$ct:ct-exec`；Codex＋BAT beta.5 時寫的是用 zip，beta.6 起依 BAT 版本（`>= 0.7.2-pre.1` 兩種安裝都支援，見 § beta.6）
- **§ 路徑解析：兩處都算（未驗證；beta.8 起改成一處，見 § beta.8）**：v6 有 § 路徑解析（穩定版沒有），plugin 目錄是它唯一的例外，`~/.claude/plugins/` 與 `${CLAUDE_CONFIG_DIR}/plugins/` 都當 Layer 1；
  beta 本身沒有 plugin，但同一台機器可能裝了穩定版的 plugin，所以照樣適用（§ 全域路徑；理由見 `three-layer-arch.md` § plugin 安裝路徑也是 Layer 1）
- **從 beta.4 升級只換 skill 檔案**：沒有新命令、新設定，不需改設定或工單；規則改在 `control-tower`、`ct-evolve`、`ct-help`、`ct-insights`，8 個 `agents/openai.yaml` 都有改，8 個 skill 同批換；BAT 不必升級。
  方法論契約仍 `ct-methodology-adapter/v1`，`ct-adapter-pstack` 內容沒改、仍 0.2.4
- **本版新規則的已知未驗**是〈已知未驗〉第 16 項（`CLAUDE_CONFIG_DIR` 與 plugin 目錄；beta.8 前已實機驗證、移除）

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.5]`；安裝與升級步驟見 CT 安裝指南 § 2.56）

---

## beta.6：移植 5.14.1／5.14.2、adapter 偵測 plugin

**移植的規則穩定版 5.14.1／5.14.2 也有**（CT `docs/CHANGELOG.md` `[6.0.0-beta.6]`），所以本章不重講，下表只指向主教材已寫好的章節：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| 塔台端派工與回收範本用 `<工單 ID>`（5.14.1） | `work-order-lifecycle.md` § 回報與通知用完整工單 ID；`bat-integration.md` § 一張分頁的生命週期 | `auto-session.md` § 執行方式 |
| marketplace 另有 `bmad-guide`（5.14.1） | `governance.md` § plugin marketplace：另一種安裝方式 | `version-governance.md` § 安裝／升級流程 › plugin 安裝／升級 |
| Codex 搭配 BAT 派工依 BAT 版本（5.14.2） | `bat-integration.md` § 誰負責 `/` 還是 `$`、§ 版本對照表 | `auto-session.md` § 依安裝方式的 skill 呼叫字串、§ 依賴的 BAT 基礎設施；`version-governance.md` › Codex 搭配 BAT 派工：依 BAT 版本 |
| 偵測 plugin 版 bmad-guide 的設計理由（5.14.1：手動優先、marketplace 不寫死、`references/` 相對、只讀、讀不到時提示一次） | `integration.md` § 偵測與降級 | v6：`adapters/bmad.yaml` `detection.probes`；`methodology-adapters.md` § 描述檔格式 › probe 怎麼解析 skill 根目錄、§ 降級 |
| 專案上下文改指 `AGENTS.md` 的區塊（5.14.1） | — | `mono-repo-patterns.md`、`multi-tower-protocol.md` |
| `CLAUDE_CODE_PLUGIN_CACHE_DIR` 時安裝清單也搬過去（5.14.1） | — | `data-layer-architecture.md` § 寫入規則 |

### 只在 v6 的部分：adapter 偵測得到 plugin 安裝的方法論

**為什麼要改。** beta.5 以前，`bmad.yaml` 的 probe 只查 `skills/` 底下的手動安裝。穩定版 5.14.1 已經偵測得到 plugin 版 bmad-guide，
v6 若照舊，同一台機器上用 plugin 裝的 bmad-guide，穩定版塔台找得到、beta 塔台卻找不到。v6 的 Level 2 偵測由 adapter 負責，
所以修法不是在 `enhancement-integration.md` 加一張搜尋表，而是讓 adapter 契約本身懂 plugin 安裝——這樣任何方法論的 adapter 都用得上。

**probe 怎麼解析 skill 根目錄**（權威：`methodology-adapters.md` § 描述檔格式 › probe 怎麼解析 skill 根目錄）：

- **依列出順序，第一個成功的 probe 決定 skill 根目錄與版本**（beta.8 起先分 runtime，見 § beta.8）。同一個 skill 的手動 probe 排在 plugin 前面＝手動優先，和 agent 兩種都裝時實際載入的那份一致
- **`kind: plugin` 先找 plugin 安裝根目錄**：Claude 看安裝清單的 `installPath`，Codex 看設定裡啟用的 plugin、到 cache 取最新版本；`name` 寫 `<plugin>@*`，不寫死 marketplace
- **`skill_root`**：probe 底下的選填欄位，寫 skill 在安裝根目錄底下的相對位置（bmad 是 `skills/bmad-guide`）。為什麼要明寫，而不讓 CT 用 plugin 名稱去推：
  一個 plugin 可能帶好幾個 skill（pstack 就是），plugin 名稱也不一定等於 skill 名稱；明寫比猜可靠，`validate-adapter.py` M8 也檢查得到
  （只能用在 `kind: plugin`、要是相對路徑且不含 `..`；寫了 `required_files` 就要有 `skill_root`）
- **之後的路徑都相對於 skill 根目錄**：`required_files`、相對的 `version_marker.file`、routing 的 `reference`；plugin 路徑只讀
- **契約仍 `ct-methodology-adapter/v1`、頂層 22 欄不變**：`skill_root` 是 probe 的選填子欄位，舊 adapter 不用改

**bmad 的兩個 plugin probe。** 內建 `bmad.yaml` 在手動的 `guide-skill` 之後加 `guide-claude-plugin`、`guide-codex-plugin`——順序就是 5.14.1 那張搜尋順序表
（`integration.md` § 偵測與降級）。版本與手動安裝比對同一個 `min_version`。beta.8 起 `guide-skill` 拆成兩個、四個 probe 標 `runtime`（§ beta.8）。

**已安裝卻讀不到：提示一次，寫成方法論中立。** 5.14.1 是為 bmad-guide 寫的；v6 把它寫成契約 § 降級的一列：probe 全部失敗、可用 skill 清單裡卻有該方法論的 skill，
本 session 提示一次再降級。為什麼要和「沒裝」分開，理由跟 5.14.1 一樣：靜默降級會讓使用者以為裝了沒作用（`integration.md` § 偵測與降級）。

**`ct-adapter-pstack` 0.2.5。** pstack 本來就是 plugin，它的 plugin probe 早就有；這版只讓 Claude probe 也考慮 `CLAUDE_CODE_PLUGIN_CACHE_DIR`，
並把 `pinned_ref` 對齊 `tested_version` 0.9.103（`ct-adapter-pstack` 的 `adapter.yaml`、`NOTICE.md`）。

只跟 Beta 有關的四點：

- **beta 仍沒有 CT plugin，但可以只裝 `bmad-guide`**：bmad-guide 不跟 CT 版號，beta 使用者可以從穩定 marketplace 裝 `bmad-guide@control-tower`，
  beta.6 的塔台偵測得到；手動與 plugin 並存時用手動那份。CT 本身照舊用 zip，不要從 marketplace 裝 `ct`（§ beta.5：plugin 安裝就緒）
- **Codex＋BAT**：beta 本身只有 zip，所以 BAT 版本的條件只有在同機另裝穩定版 CT plugin、又要讓 Codex 用它接派工時才相關
- **從 beta.5 升級只換 skill 檔案**：沒有新命令、新設定，不需改設定或工單；有用 pstack 的換 `ct-adapter-pstack` 0.2.5；BAT 不必升級
- **本版新規則的已知未驗**是〈已知未驗〉第 17～19 項（plugin probe 未實機、提示一次未觸發、Codex＋BAT＋plugin 端到端；beta.8 起 plugin probe 已驗、移除，另兩項改編為第 16、17 項）

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.6]`；安裝與升級步驟見 CT 安裝指南 § 2.57）

---

## beta.7：移植 5.14.3（巢狀的獨立 repo）

beta.7 只移植穩定版 5.14.3 的一份配置文件：**一個塔台、多個巢狀的獨立 repo**（上層目錄底下有好幾個跟團隊共用的獨立 repo 時，工單集中在上層、Worker 在上層執行、子 repo 用 `git -C` commit）。
**這份文件穩定版 5.14.3 也有**，條文相同，方法論的部分沒有改（契約不變、`ct-adapter-pstack` 仍 0.2.5），所以本章不重講，只指向主教材：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| 為什麼工單會跑進子 repo、一個塔台還是每個 repo 一個塔台、限制 | `advanced-patterns.md` § 巢狀的獨立 repo：一個塔台管多個共用 repo | `mono-repo-patterns.md` § 巢狀的獨立 repo（一個塔台、多個共用 repo）；判斷表 `multi-tower-protocol.md` § 決策：一個塔台還是多個 |
| `repo` 填上層目錄名 | `work-order-lifecycle.md` frontmatter 欄位地圖的 `repo` 列 | `work-order-template.md` § `repo` |
| 派工 cwd、不能 worktree | `bat-integration.md` § 版本對照表（v5.14.3、v6.0.0-beta.7 兩列） | `mono-repo-patterns.md` § 巢狀的獨立 repo › 派工與面板、› 限制 |

只跟 Beta 有關的兩點：

- **實機驗證用的是穩定版**：這個配置以穩定版 CT 5.14.2＋BAT 0.7.2-pre.1 實機驗過；它用到的落點檢查、commit 規則與派工命令在 beta 相同，結果照抄，沒有在 beta 上重跑。BAT 面板一鍵派工兩邊都還沒驗（〈已知未驗〉第 20 項，beta.8 起是第 18 項）
- **從 beta.6 升級只換 skill 檔案**：沒有新命令、新設定、新欄位，不需改設定或工單；`ct-adapter-pstack` 內容沒變；BAT 不必升級

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.7]`；安裝與升級步驟見 CT 安裝指南 § 2.58）

---

## beta.8：移植 5.14.4、probe 依 runtime

**移植的規則穩定版 5.14.4 也有**（CT `docs/CHANGELOG.md` `[6.0.0-beta.8]`），所以本章不重講，下表只指向主教材已寫好的章節：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| 找方法論 skill 依 runtime 分開（本 runtime 手動 → 本 runtime plugin → 另一個 runtime 只當讀檔來源；同一個 runtime 內手動優先） | `integration.md` § 偵測與降級（〈5.14.4 改成依 runtime 分開〉） | v6：`methodology-adapters.md` § 描述檔格式 › probe 怎麼解析 skill 根目錄 第 1 點 |
| Claude plugin 的位置只有一處 | `three-layer-arch.md` § plugin 安裝路徑也是 Layer 1 | `data-layer-architecture.md` § 路徑解析、§ 寫入規則；`methodology-adapters.md` 同節 第 3 點 |

### 只在 v6 的部分：probe 的 `runtime`

**為什麼要改。** v6 的 bmad-guide 偵測寫在 adapter 的 probe，beta.7 的 `guide-skill` 把 Claude 與 Codex 的 `skills/` 寫在同一個 probe 裡，
塔台照列出順序試，所以 5.14.4 修掉的那個問題在 v6 一樣存在：Claude 只裝 plugin、Codex 用 zip 時，Claude 塔台會先命中 Codex 那份。
v6 的修法和 beta.6 一樣，不在 `enhancement-integration.md` 加表，而是讓 adapter 契約本身懂 runtime——任何方法論的 adapter 都用得上。

**怎麼試**（權威：`methodology-adapters.md` § 描述檔格式 › probe 怎麼解析 skill 根目錄 第 1 點）：

- **probe 可以標 `runtime`**（選填，值是 `runtimes` 裡的一個 runtime 名）。沒寫 = 所有 runtime 適用，所以舊 adapter 不用改、行為不變；`validate-adapter.py` M8 檢查值域
- **先試本 runtime 的 probe 與沒寫 `runtime` 的 probe，依列出順序；再試另一個 runtime 的。** 不另外照 `kind` 重排，理由是 adapter 本來就要把同一個 runtime 的手動 probe 排在 plugin 前面，
  而名稱不同的 skill（pstack 的 skills-only）本來就允許依 adapter 自己的需要排；塔台再照 `kind` 重排，反而會蓋掉 adapter 的安排
- **另一個 runtime 的只當讀檔來源**：照常用來查 routing，第一次用到時註明一次「不是本 runtime 載入的」，不阻斷——和 5.14.4 同一個理由

**bmad 與 pstack 的改法。** `bmad.yaml` 0.2.1：`guide-skill` 拆成 `guide-skill-claude`、`guide-skill-codex`（`~/.agents/skills/` 歸 Codex），連同兩個 plugin probe 都標 `runtime`，
照新規則試出來的順序就是 5.14.4 那張表。`ct-adapter-pstack` 0.2.6：兩個 plugin probe 標 `runtime`，skills-only 同樣拆成兩個。
兩邊的 Claude plugin probe 都刪掉第 2 個 `search`（`~/.claude/plugins/installed_plugins.json`）：位置只有一處之後，它只會命中本 session 沒載入的 plugin。

只跟 Beta 有關的三點：

- **beta.7 的第 16、17 項已實機驗證**：`CLAUDE_CONFIG_DIR` 會搬 plugin 目錄；adapter 的 plugin probe 在 Claude Code 與 Codex 各一個隔離環境都判斷正確，手動與 plugin 並存時手動優先。兩項從〈已知未驗〉移除
- **從 beta.7 升級只換 skill 檔案**：沒有新命令、新設定，不需改設定或工單；有用 pstack 的換 `ct-adapter-pstack` 0.2.6；自己寫的 adapter 照舊可用；BAT 不必升級
- **本版新規則的已知未驗**是〈已知未驗〉第 19 項（依 runtime 的新順序本身還沒在塔台實際跑過，穩定版 5.14.4 也一樣）

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.8]`；安裝與升級步驟見 CT 安裝指南 § 2.59）

---

## beta.9：移植 5.15.0（一批提問只叫醒塔台一次）

**移植的規則穩定版 5.15.0 也有**（CT `docs/CHANGELOG.md` `[6.0.0-beta.9]`），條文相同、只差版本標記，所以本章不重講，下表只指向主教材已寫好的章節：

| 主題 | 主教材 | CT 權威 |
|---|---|---|
| 一批多題只叫醒塔台一次（前 N-1 題 `--ask --no-pty-write`、第 N 題 `--ask --submit`；最後一題送不上時緊接著補送） | `work-order-lifecycle.md`〈一批只叫醒塔台一次〉 | `yolo-mode.md` § Worker 向塔台提問 › § Worker 端 3-A 第 1、2 步、§ BAT 通道 |
| 塔台收到重複通知的最少檢查、已升級的題不重複提醒 | 同上 | 同節 § 塔台端 第 1、2 點 |
| 多題等待的租約逐題計算（`min(45, floor(90 / K))` 秒、能同時等就同時等） | `work-order-lifecycle.md`（BAT 通道的租約那段） | 同節 § Worker 端 3-A 第 3 步、§ BAT 通道 › 限制 |
| 斷點 A 看通知字串結尾、題數只看列表與工單標記 | `runtime-dispatch.md` § 斷點 | `yolo-mode.md` § 斷點 A |
| BAT 版本對照 | `bat-integration.md` 版本對照表（v5.15.0、v6.0.0-beta.9 列） | `yolo-mode.md` § BAT / Worker 版本相容 |

只跟 Beta 有關的三點：

- **版本說法換成 beta 的**：CT 規範裡的新條文標 `v6.0.0-beta.9`；版本相容表與迴歸情境裡的「舊版」寫成 `v6.0.0-beta.8 以前`（穩定版寫成 `v5.14.4`）。規則本身一字不差
- **從 beta.8 升級只換 skill 檔案**：沒有新命令、新設定、新欄位，不需改設定或工單；Worker（`ct-exec`）與塔台（`control-tower`）要同批換才完全生效；方法論契約、`bmad.yaml`、`ct-adapter-pstack` 內容都沒改；BAT 不必升級
- **本版新規則的已知未驗**是〈已知未驗〉第 20～23 項（Worker 照 skill 實際送出、塔台端的最少檢查與等待條目、多題逐題等待、結尾判讀都還沒在新 session 實機跑過，穩定版 5.15.0 也一樣）

（權威：CT `docs/CHANGELOG.md` `[6.0.0-beta.9]`；安裝與升級步驟見 CT 安裝指南 § 2.60）

---

## beta.10：session 用量統計（PLAN-004 ⑥）

使用者問「每張工單、每個塔台 session 有沒有記 token 用量」——原本沒有。beta.10 用 Claude Code 自己留在本機的 session 紀錄
（Claude Code 專案紀錄目錄下、以專案路徑編碼命名的子目錄裡的 `<session id>.jsonl`）把用量算到工單，**只做 Claude Code**，Codex／Copilot 不做。這一節只在 v6，穩定版 5.15.0 沒有。

### 誰做什麼

| 誰 | 什麼時候 | 做什麼 |
|---|---|---|
| Worker（`ct-exec`） | 收尾 | 把自己的 `CLAUDE_CODE_SESSION_ID` 寫進工單 frontmatter `session_ids`（Renew 追加、不覆蓋），回報區〈完成狀態〉多一行 `session_id`；不是 UUID 或沒設就寫 `unavailable` |
| 塔台 | 啟動 | 在 `_tower-state.md` 的開工條目寫「塔台 session」加反引號包住的 uuid；拿不到寫「session id 未知」，不擋啟動；機器可讀摘要不加欄位 |
| 塔台 | 收單（`--close-worker` 之前） | 用 BAT MCP 讀 Worker 分頁的 `claudeSessionId`，不在 `session_ids` 就追加（備援）；再對這張工單寫一筆**快照**到 `_ct-workorders/_insights/session-stats/<YYYY-MM>.json` |
| 塔台 | `*insights sessions` | 跑 `ct-insights/scripts/ct-session-stats.py` 出報表，並補寫還沒有快照的工單 |

### 為什麼這樣設計

- **只用規則式腳本**：Python 標準函式庫、只讀、不呼叫模型、不連網，和 `*insights workflow` 的預篩腳本同一套做法。同一範圍重跑結果相同。
- **歸屬先看工單自己記的 session id**：⓪ `session_ids` → ① 第一則訊息 `/ct-exec T####` → ② 分頁標題 → ③ BAT log（可選）。
  T0391 的實驗裡 ① 就能把 Worker session 100% 歸到工單，但 session 紀錄 30 天後會被清掉，⓪ 讓快照與工單日後還對得上。
  BAT 的 `bat-scripts.log` 是診斷日誌、會輪替，**不依賴它**（D517）。
- **塔台用量另列、不攤分**：塔台約三分之二的用量發生在沒有任何 Worker 執行的時候，硬攤到工單只會反映「同時開了幾張」。
  依決策日誌時間切的版本也有，但標「估」、方向（上一筆～這筆）未經結果驗證，只當對照。
- **「卡住」看失敗密度**：Worker 幾乎都是一個 turn 做到底，turn 數沒有意義；改看任意連續 10 次工具結果裡失敗幾次，≥ 3 只是 🔵 觀察。
- **成本是估算**：依模型與 `pricing.json` 換算的等價 API 成本，比 Claude Code 自己的 `cost-state` 低約一成；只看趨勢，不當帳單。
- **快照只有數字**：不含對話、指令原文、完整路徑；每次輸出前腳本自己跑隱私自檢，不過就不寫。快照也是 ⑦（ct-evolve 的候選事實）的來源。

### 圖：session 用量資料流

<svg width="100%" viewBox="0 0 680 400">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<g class="node c-blue" onclick="sendPrompt('介紹 Worker 收尾怎麼寫 session_ids')">
  <rect x="40" y="40" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="130" y="58" text-anchor="middle" dominant-baseline="central">Worker 收尾</text>
  <text class="ts" x="130" y="76" text-anchor="middle" dominant-baseline="central">→ 寫 session_ids</text>
</g>
<g class="node c-gold" onclick="sendPrompt('介紹塔台啟動怎麼記自己的 session id')">
  <rect x="250" y="40" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="58" text-anchor="middle" dominant-baseline="central">塔台啟動</text>
  <text class="ts" x="340" y="76" text-anchor="middle" dominant-baseline="central">→ 開工條目記 id</text>
</g>
<g class="node c-gold" onclick="sendPrompt('介紹塔台收單時補記 session id')">
  <rect x="460" y="40" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="58" text-anchor="middle" dominant-baseline="central">塔台收單</text>
  <text class="ts" x="550" y="76" text-anchor="middle" dominant-baseline="central">→ 補記（備援）</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹 session 統計讀哪些欄位、隱私怎麼保證')">
  <rect x="40" y="150" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="130" y="168" text-anchor="middle" dominant-baseline="central">本機 JSONL</text>
  <text class="ts" x="130" y="186" text-anchor="middle" dominant-baseline="central">→ 30 天後清掉</text>
</g>
<g class="node c-purple" onclick="sendPrompt('介紹 ct-session-stats.py 的歸屬優先序')">
  <rect x="250" y="150" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="168" text-anchor="middle" dominant-baseline="central">統計腳本</text>
  <text class="ts" x="340" y="186" text-anchor="middle" dominant-baseline="central">→ ⓪①②③ 歸屬</text>
</g>
<g class="node c-green" onclick="sendPrompt('介紹 session 統計快照放哪、怎麼併入')">
  <rect x="460" y="150" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="168" text-anchor="middle" dominant-baseline="central">快照</text>
  <text class="ts" x="550" y="186" text-anchor="middle" dominant-baseline="central">→ _insights/ 只數字</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹 *insights sessions 的報表怎麼讀')">
  <rect x="250" y="260" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="278" text-anchor="middle" dominant-baseline="central">報表</text>
  <text class="ts" x="340" y="296" text-anchor="middle" dominant-baseline="central">→ 工單／塔台另列</text>
</g>
<g class="node c-purple" onclick="sendPrompt('介紹 session 候選事實怎麼給 ct-evolve')">
  <rect x="460" y="260" width="180" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="550" y="278" text-anchor="middle" dominant-baseline="central">候選事實</text>
  <text class="ts" x="550" y="296" text-anchor="middle" dominant-baseline="central">→ 🔵 給 ⑦</text>
</g>
<line x1="130" y1="92" x2="310" y2="150" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="92" x2="340" y2="150" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="550" y1="92" x2="370" y2="150" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="220" y1="176" x2="250" y2="176" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="430" y1="176" x2="460" y2="176" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="202" x2="340" y2="260" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="550" y1="202" x2="550" y2="260" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<text class="ts" x="340" y="350" text-anchor="middle">塔台用量另列、不攤分；成本與依決策切的欄位都標「估」</text>
<text class="ts" x="340" y="370" text-anchor="middle">bat-scripts.log 只當可選的交叉驗證，讀不到不影響</text>
</svg>

（上排三個 session id 來源都指向統計腳本的歸屬；原始紀錄會被清掉，所以快照要在收單當下寫。圖的規格見 `diagrams.md` § 20。）

### 升級影響

- **不需要改設定或舊工單**：沒有新設定選項；舊工單沒有 `session_ids` 照常，統計改用第一則訊息與分頁標題。
- **要 Python 3**（和預篩腳本一樣）；找不到時報表寫「資料不可用」，收單快照跳過並註一句，其他流程不受影響。
- 收單補記需要 BAT `>= 0.7.1-pre.1`（`claudeSessionId`）與 BAT MCP；沒有就跳過，Worker 自己寫的 `session_ids` 仍在。
- 本專案過渡用的本地規則（塔台記 session id）併入規格後由塔台移除。

### 本版新規則還沒實機跑過的

- 塔台收單補記與收單快照還沒在實機收單跑過（腳本本身以合成資料測試、對一個專案近 30 天實跑過）
- `tower_by_decision` 的方向（上一筆～這筆）未經結果驗證
- `max_failures_in_10_calls >= 3` 的門檻未校準（樣本裡的工單全是 `DONE`）
- 隔離工單（worktree）的 session 紀錄要另加 `--project`，還沒實機跑過
- 候選事實接進 ct-evolve 的實際一輪（`--facts-from`）還沒跑過，見下一節
- 完整清單見 § 已知未驗 第 21～28 項（session 統計）與第 29～32 項（session 證據與 ECC 退場）

（權威：CT `ct-insights/references/analysis-rules.md` § Session 用量統計；`ct-exec/SKILL.md` § Phase 4 › Session id；
`control-tower/references/memory-protocol.md` § 塔台 session id；`work-order-system.md` § 收單補記 session id、§ 收單快照；
`data-layer-architecture.md` § `_ct-workorders/_insights/`）

## beta.10：session 證據怎麼進學習流程（PLAN-004 ⑦）

上一節的統計會從快照產生**候選事實**（`ct-session-fact/0.1`，一行一筆）。這一節講它們怎麼進到 CT 原本的學習流程。只在 v6，穩定版 5.15.0 沒有。

| 問題 | 答案 |
|---|---|
| 什麼時候讀 | 只有使用者下 `/ct-evolve --facts-from <快照或事實檔>` 時。不背景執行、不自動標記工單 |
| 給快照時 | ct-evolve 跑 `ct-session-stats.py --facts-from <快照> --facts <暫存檔>`：只讀快照，所以原始紀錄清掉後仍可重算 |
| 進場多高 | 🔵；`workorders` ≥ 2 張且 `days` ≥ 2 天才到 🟡（就是既有 🟢「2+ 工單重複出現」的前一階） |
| 怎麼到 🟢、⭐ | 🟢 要過 Distillation Gate（寫得出 Trigger／Action）且符合置信度表的 🟢 條件；⭐ 要使用者認可。統計本身到不了 🟢 |
| 數什麼 | 工單，不是 session：Renew、`/clear` 換了 session id 都不多算 |
| 撤回 | 之後 ≥ 2 張工單出現反證 → `⏸ 撤回候選`，保留歷史、可恢復；`❌ 廢棄` 只由使用者決定 |
| 寫到哪 | 卡住訊號 → Episodic；通過閘門的環境事實 → Tactical（相關主題加 `[FG-CANDIDATE]`）；Strategic 不由統計產生 |
| 怎麼認得 | 條目帶 `[SESSION-EVIDENCE: <fact_id>]`；同一份快照重跑得到同一個 `fact_id`，更新原條目而不是新增 |

**為什麼不另訂門檻**：研究（T0389 R6）發現 CT 規格裡已經有第二套採信規則（ECC Level 1，見下一節）；如果再為機器證據訂「≥ 3 session」之類的門檻，
就變成第三套。所以直接接到 `self-learning-core.md` § 置信度系統 那一張表。**為什麼數工單**：實測 Worker 幾乎是一張工單一個 session，
數 session 只會把 Renew 灌成重複證據。**為什麼最多到 🟡**：統計看得到「發生了」，看不到「為什麼」——🟢 要能寫成 if-then 規則，那一步要人或
Distillation Gate 來做。

（權威：CT `ct-evolve/SKILL.md` § Session Evidence；候選事實格式 `ct-insights/references/analysis-rules.md` § 候選事實；
置信度表 `control-tower/references/self-learning-core.md` § 置信度系統）

## beta.10：ECC Level 1 退場

穩定版 5.15.0 的「能力等級」有 Level 1：ECC continuous-learning-v2（寫 ECC 觀察、讀 instinct、把 ECC 數值置信度換成 CT 符號）。
beta.10 把它移出現行規則，`enhancement-integration.md` 改寫成「**外部增強外掛治理**」（檔名不變，連結不斷）。

- **條件**：使用者定的是「新機制完成、ECC 需要的相容功能都已納入」才移除（D507 ④）。所以退場前先做了**相容功能對照**：ECC Level 1 的
  13 項功能，每一項都找到現行對應（例：observer 自動產生 instinct → session 統計自動產生候選事實；`/promote` 候選 → 分流提問與
  `candidate: global`），或寫明不再需要（數值換算、instinct 同步、雙寫）。有任何一項沒有對應，就只會標「已停用」。對照表在 CT
  `enhancement-integration.md` § ECC Level 1 退場。
- **治理原則（CT 自己的部分）**：CT 只有一套學習機制（三區學習＋FIELDGUIDE 晉升＋session 證據）；記憶、省 token、context 壓縮類外掛
  預設不搭配，要不要裝是使用者層的規範，CT 不複製條文；Level 2 方法論轉接照現行規格保留。
- **Level 3 mem0：保留，但要有例外紀錄才啟用**：mem0 以 Stop hook 接記憶服務，屬於使用者層「agent 記憶外掛預設不安裝」的範圍。
  要啟用的專案須在本地規則（例 `_ct-workorders/_local-rules.md`）寫明符合哪一條例外、量測依據與日期、元件名稱與版本；
  沒有紀錄 → 塔台不啟用，偵測到也只提示一次。穩定版 5.15.0 沒有這個條件（偵測到就啟用）。詳見 `integration.md` § Level 3 › 啟用條件。
- **Level 編號不重排**：Level 1 標「已退場」，Level 2、3 的編號與連結不變。
- **從 ECC 升級的使用者**：不用改設定；CT 不再寫 `observations.jsonl`、不再讀 instinct；`~/.claude/homunculus/` 的資料 CT 不動，留不留由使用者決定；
  `_learnings.md` 本來就有完整紀錄（雙寫時的保底）。
- **同一版的 BAT 注意事項**：在 BAT 下不要在 Claude 啟動參數放 `--settings`——BAT 會因此不注入 hooks，blocked 偵測、`--wait-started`、
  session id 回報都失效；要換 skill 組合用專案 `.claude/settings*.json` 的 `skillOverrides`／`enabledPlugins`（`bat-integration.md`）。

（權威：CT `control-tower/references/enhancement-integration.md` § 外部增強外掛治理、§ ECC Level 1 退場、§ Level 3 › 啟用條件；`auto-session.md` § Claude 啟動參數不得放 `--settings`）

## beta.11：Worker 執行中接收塔台補充（PLAN-005）

> 只在 v6，穩定版 5.15.0 沒有。節點檢查已在發版前用隔離的 `claude -p` 驗過（見下方〈驗過的與還沒實機跑過的〉）；隔離工單、yolo 下的衝突提問、跨 session 提醒、Codex Worker 留待安裝後實際派工驗證。

起因是一次實際卡住：BAT 塔台在 Worker 還在跑的時候往工單加了〈塔台補充（Renew #1）〉，Worker 看不到，只能請使用者到 Worker 分頁打「重讀工單」。
Worker 原本只依開工時讀到的工單執行，中途只有 compact／resume 後才會重讀；塔台又不能寫入 Worker 分頁（BAT 範圍權杖；PTY「文字＋Enter」會替對話框作答）。
CT 這次的做法是**不要求 BAT 開放任何東西**，改成 Worker 自己在固定時間點看一眼工單。

### 誰做什麼

| 誰 | 什麼時候 | 做什麼 |
|---|---|---|
| 塔台 | Worker 還是 `IN_PROGRESS`、要補充或修正指示時 | 在回報區 `---` 之前加 `## 塔台補充（執行中 #N）`：時間、補充內容、新指示、範圍與驗收有沒有改、要不要推翻已完成的部分；範圍或驗收改了，同一次也改 frontmatter 與驗收段。不加 `Renew 次數`、不重派 |
| Worker（`ct-exec`） | 驗證前、產品 commit 前、寫回報前（三個固定節點） | 每個節點 grep 一次工單的段落標題，有開工後才出現的 `## 塔台補充（…）` 才讀那一段並照做；沒有就什麼都不輸出（也不在 `### 互動紀錄` 寫「沒有新段落」之類的行）。讀到的記一行在 `### 互動紀錄` |
| Worker（`ct-done`） | 補救收尾、寫回報前 | 同一個檢查跑一次（當作寫回報前的節點）：回報還沒記為讀過的補充段才讀；補救收尾做不到的照實寫進回報，不自己擴權 |
| 塔台（選用） | 寫完補充段之後 | Claude Code 塔台＋Claude Code Worker 時，可用跨 session 訊息送一行「重讀工單 T#### 該段」給自己的 Worker（見 `advanced-patterns.md` § 跨 session 通知對方塔台 末段）；找不到 Worker 就不送 |
| 塔台 | 收單 | 核對每個執行中補充段在 `### 互動紀錄` 都有讀入紀錄；沒有就當作沒讀到，以 Renew 重派或開接手單。Claude Code Worker 會收到「檔案已變更」的提示，常會讀到過了寫回報前節點才寫的段落，有紀錄就照常認定（Codex Worker 沒有這個提示，只靠節點） |

### 為什麼這樣設計

- **只在三個節點看、只 grep 標題**：這三個點之後的動作（跑驗證、commit、寫回報）是最後一次能便宜改方向的地方；每個點只花一次 grep，沒有新段落時連工單全文都不讀。
  代價是長步驟中途讀不到——急的話靠選用的跨 session 訊息，或請使用者說「重讀工單」。
- **和 Renew 分開**：Renew 是 `BLOCKED`／`FAILED` 之後重派，會加 `Renew 次數`、累積到斷點 B-1；執行中補充只是同一輪裡的補充，混在一起會讓 B-1 誤觸發。
- **commit 不影響可見性**：Worker 讀的是工作目錄裡的檔案，塔台存檔就看得到；commit 照慣例只 commit 該工單檔。隔離（worktree）工單的工單檔本來就只在主 checkout，
  Worker 讀 `$CT_HOME` 那份，所以不需要特別處理。
- **跨 session 訊息只是指引**：訊息裡不放任何要求，要求一律寫在工單；所以訊息沒送到、晚到、被擱著，都不會讓 Worker 做錯事，最壞只是晚一點讀到。
- **衝突不自己擴權**：補充段跟已完成的工作衝突、或要求超出 `affects_files`／禁止事項，Worker 照原本的提問規則問塔台（yolo）或停下，不自己放大範圍。

### 驗過的與還沒實機跑過的

發版前用隔離的 `claude -p` 跑了 7 次（暫存 `CLAUDE_CONFIG_DIR` 放 beta.11 的 skill，`CT_MODE=ask`）：

- **已驗**：三個節點各自讀到開工後新增的段落並照做；開工前就有的 `Renew #1` 算進基準；補充段要求改範圍外的檔案、frontmatter 沒改時，Worker 不改、完成原範圍回報 `PARTIAL`（沒有提問通道的情況）；塔台不 commit 也讀得到；`ct-done` 寫回報前讀到開工後才加的段落
- **觀察到、只補說明**：Claude Code 讀過的檔案在磁碟上被改時，下一個回合會收到「檔案已變更」的提示，所以 Worker 常會讀到過了寫回報前節點才寫的段落（2/2）——收單時有讀入紀錄就照常認定；沒有新段落時 Worker 不讀全文，但 4 次中有 3 次在 `### 互動紀錄` 多寫一行「沒有新段落」，規格加了例子說不要寫
- **安裝後實際 BAT 派工驗過**（beta.11 裝在開發機的 Claude Code 與 Codex，4 張小工單）：隔離工單從主 checkout 讀到補充段、worktree 副本沒動；yolo 下補充段超出範圍時 Worker 經 BAT 提問通道問塔台、不自己擴權；跨 session 訊息的四種情況——權限模式相同時送達；不同時訊息擱在 Worker 分頁，要使用者按 Deliver 才晚到（擱置期間 Worker 照常跑、到節點自己讀到，所以塔台已知模式不同就不送）；Worker 正在跑工具時排到工具結束後才看到、不打斷；Codex Worker 不在 ListAgents，依順序不送——以及 Codex Worker 只靠節點檢查讀到補充段。全部通過
- **還沒實機跑過**：「沒有讀入紀錄」那條路徑（只會在 Worker 最後一個回合之後才寫入時出現）；「不寫『沒有新段落』」加了例子之後，實際派工的 4 張（含 Codex）仍都寫了一行——見 § 已知未驗 第 34～36 項

BAT 的兩項補註（帶 `--settings` 的分頁不出現工作區 ⚠️、BAT `>= 0.7.3-pre.8` 塔台等你時 Worker 通知先排隊）跟執行中補充無關，寫在 `bat-integration.md` § Worker 執行與通知 與〈為什麼不能在 BAT 的 Claude 啟動參數放 `--settings`〉。

（權威：CT `control-tower/references/work-order-system.md` § 執行中補充工單；`ct-exec/SKILL.md` § Tower Addenda Check；
`control-tower/references/cross-project-coordination.md` § 通知自己的 Worker 重讀工單）

---

## beta.12：工具清單建議（PLAN-006）

> 只在 v6，穩定版 5.15.0 沒有。新命令 `*insights tools` **只出建議、不改任何設定**；改完設定要開新 session 才生效。

使用者問「每一輪 context 裡，有哪些 skill、MCP、工具一直被載入，卻從來沒用到？」——原本只能憑感覺。beta.12 讓 `ct-insights` 的同一支 session 統計腳本
（`ct-session-stats.py --tools`）用 Claude Code 自己留在本機的 session 紀錄回答這個問題，**只做 Claude Code**，Codex／Copilot 不做。

### 誰做什麼

| 誰 | 什麼時候 | 做什麼 |
|---|---|---|
| 塔台 | 使用者要看工具清單時 | 跑 `*insights tools`（預設只看目前 repo；`--all-projects` 看本機全部專案，其他 repo 一律以代號呈現；`--keep <名稱>` 指定不建議的項目）；把報告給使用者看，不替使用者改設定 |
| 使用者 | 看完報告 | 自己決定要不要照建議改設定檔或介面；改完開新 session，再跑一次 `*insights tools` 或在互動 session 用 `/context` 確認 |
| Worker | — | 沒有變化（`ct-exec`、`ct-done` 只改版號註解） |

### 報告裡有什麼

- **建議表**：期間內 0 次使用的項目標「建議停用」，使用 1～2 次而且最近 14 天沒用的標「可考慮」；每一項都寫明**在哪一層改**（專案、使用者、claude.ai 帳號）、改哪個檔與鍵（或哪個介面），以及每輪約省多少 token
- **不建議**：CT 自己的 skill、`--keep` 指定的、任一工單類型有 3 個以上 session 在用的、資料不足的（資料少於 14 天或載入不到 20 個 session），以及沒有可用手段的
- **需使用者裁示**：`Artifact`、`Workflow` 這類內建工具不放進建議表，另列一區並附警語（關掉是單向的、塔台與 Worker 共用專案設定、關掉後哪些功能不能用）
- **另列問題**：同名重複的 skill（使用者層與 claude.ai 同步各一份，版號不同時標 ⚠️）、一直連不上的 MCP server、skill 清單被截

### 為什麼這樣設計

- **「已載入」以 session 紀錄為準**：設定檔只說「應該有什麼」，session 紀錄的附件（skill 清單、工具 schema、MCP 說明）才是那一輪真的送給模型的東西；設定檔只拿來判斷項目在哪一層。
- **依工單類型分組**：同一個 skill 在一般實作工單 0 次、在研究工單很常用，合起來看就會被誤判成可以關。任一類型有 3 個以上 session 在用就不建議。
- **只建議、不改設定**：專案層設定是這個 repo 的塔台與 Worker 共用的，關掉就兩邊都關，有些手段（例 `enableArtifact: false`）還關了就打不開；這種決定留給使用者。
- **核心內建工具一律保留**：`Skill`、`ToolSearch`、`Agent`、`Bash`、`Read`、`Edit` 等是 CT 與 Claude Code 運作必需的，使用率再低也不列入裁示（例：`Skill` 使用率 4.7% 曾經命中「少用且每輪 ≥ 500 token」的條件）。
- **使用率不超過 100%**：內建工具的使用率只算同時有工具 schema 紀錄的 session，舊 session 沒有這個紀錄、不進分母，也不進分子。
- **每個手段都標驗證程度**：官方文件寫明的標「文件」；以 `claude -p` 在 CLI 2.1.316 實測的標「實測」（同步 skill 用 `skillOverrides` 寫完整前綴名、`@synced` plugin 用 `enabledPlugins`、內建工具用 `permissions.deny` 寫裸工具名）；沒驗過的照寫但標「未驗證」。
- **不寫快照**：工具清單是「現在的設定 × 最近的用量」，設定一改就過時，所以 `--tools` 不寫快照、不產生候選事實；`*insights sessions` 的快照照舊。

### 同一版的其他改動

- `*insights sessions`：`skills_invoked` 也計使用者打的 slash command（命名空間保留全名、`/clear` 這類 CLI 命令不計），新增 `agents_invoked`；快照升 `ct-session-stats-snapshot/0.2`，`0.1` 照常可讀
- 打包檢查：每個要發行的 `SKILL.md` 的 description 不得含 `<`、`>`（claude.ai 上傳會拒絕；beta.11 的 `ct-adapter-pstack` 曾因此被拒，改寫成不用角括號的說法）

### 驗過的與還沒驗的

- **已驗**：本機跨 repo 實跑（30 天、約 1,450 個 session）與發版前的人工盤點逐項比對在容許誤差內；套用手段在 CLI 2.1.316 以 `claude -p` 讀 `system/init` 的清單實測（見上）
- **還沒驗**：同步 skill／plugin 的關法官方文件沒寫，Claude Code 改版可能失效；`permissions.deny` 能不能再打開；`syncClaudeAiSkills` 放 `.claude/settings.local.json`；claude.ai connector 在專案層的停用；`Artifact` 關掉後只能在互動 session 確認；agent 定義的移除——見 § 已知未驗 第 37～42 項

（權威：CT `ct-insights/references/analysis-rules.md` § 工具清單建議；打包檢查：`control-tower/references/version-governance.md` § 發布流程）

---

## rc.1：正式版候選（只修錯）

> v6 的 Beta 與 RC 都是預發行，只打包、不取代穩定版 5.15.0。RC（release candidate，正式版候選）表示 beta 回饋期結束：**功能凍結、只修錯**；
> RC 期間沒有發現要修的問題就發正式版 6.0.0，有問題就修好再出下一個 RC。

### 為什麼要有 RC

- beta.1～beta.12 一邊加功能一邊收回饋；功能一直在變，就沒辦法判斷「這一版能不能當正式版」。RC 先把功能凍結、只看有沒有要修的錯，正式版的內容在發布前就已經照原樣用過一段時間。
- RC 期間想到的新功能排到下一個 MINOR（6.1.0 以後），不擠進 6.0.0。

### 本版修了什麼

| 修正 | 一句話 | CT 權威 |
|---|---|---|
| Worker 節點 1 | `ct-exec` 驗證前的塔台補充檢查改成 § Phase 3 的第 1 步；原本寫在段落中間，beta.12 期間有 3 張工單的 Worker 到節點 2 才補跑 | `ct-exec/SKILL.md` § Phase 3、§ Tower Addenda Check |
| `ct-done` 節點 3 | 寫回報前的檢查改成先寫、再補回報欄位，讀起來的順序和 `ct-exec` 一致 | `ct-done/SKILL.md` 第 6 步 |
| JSON 欄位文件 | `*insights tools` 的 JSON `items[]` 欄位清單補上腳本本來就會輸出的 `use_rate`、`saving_max_chars`、`plugin_verdict` | `ct-insights/references/analysis-rules.md` § 工具清單建議 › 報告格式 |
| 本教材 | `ct-adapter-pstack` 的版號改成現行的 0.2.6（之前仍寫 0.2.5） | — |

三個節點的語意、檢查指令、「沒有新段落時不讀、不記錄」都沒有改；腳本與輸出也沒有改。

### 升級與標示

- 從 beta.12 升級只換 skill 檔案；沒有新設定、新命令或新的 frontmatter 欄位
- 預發行版（beta、rc）都不提供 CT plugin：marketplace 只上架穩定版，`6.0.0-rc.N` 照舊用 zip 手動安裝
- 各檔現行版本的標示從 Beta 改成 RC；本章的檔名與各段錨點（例 § beta.12：工具清單建議）不改名，避免舊連結失效
- 〈已知未驗〉更新為 41 項（見 § 已知未驗 的「跟 beta.12 的 42 項比」）

（權威：CT `docs/CHANGELOG.md` `[6.0.0-rc.1]`；`control-tower/references/version-governance.md` 版號表 v6.0.0-rc.1 列）

---

## 6.0.0：納入正式版

> CT v6.0.0（2026-11-07）是 v6 系列的第一個**正式版**，取代 5.15.0 成為穩定版；5.15.0 成為上一個穩定版，仍可下載。

### 改了什麼

- 相對 rc.1 **沒有功能或規則變更**：RC 期間沒有回報要修的問題，只改版號與標示（各檔現行版本的 RC 標示改成正式版，方法論段落的版號標記改成 `v6.0.0+`）
- CT plugin 6.0.0 起上架 marketplace（`ct@control-tower`、`ct-guide@control-tower` 6.0.0）；預發行版（beta、rc）不提供 plugin 的規則不變
- 方法論契約仍 `ct-methodology-adapter/v1`；內建 `bmad.yaml` 0.2.1、`ct-adapter-pstack` 0.2.6，`adapter_status` 都維持 `prototype`
- 本章保留作為預發行期間的歷史參考；主教材補上方法論轉接的簡述與連結（`integration.md` § 方法論轉接（v6.0.0+）、`work-order-lifecycle.md` § 方法論（v6.0.0+））

### 升級

- 從 rc.1 升級只換 skill 檔案；沒有新設定、新命令或新的 frontmatter 欄位
- 從 5.15.0 升級要注意的事：BUG／PLAN／EXP 預設改開啟（不想要的專案先明寫 `false`）、9 個 `methodology*` 設定鍵（缺省即 5.x 行為）、新命令 `*insights sessions`／`*insights tools`、塔台與 Worker 同批換（舊版 Worker 讀不到執行中補充段落）
- 〈已知未驗〉RC 期間沒有新驗證到的項目，41 項照列（§ 已知未驗）

（權威：CT `docs/CHANGELOG.md` `[6.0.0]`（含〈從 5.15.0 升級〉）；安裝指南 § 2.65；`control-tower/references/version-governance.md` 版號表 v6.0.0 列）

---

## Worker 端會看到什麼不同

- **工單沒有 frontmatter `methodology`** → 照 5.12.x 執行。只有三條規則對所有工單生效，而且都是事件觸發：看到注入（自查記錄）、呼叫了方法論 skill（必記）、compact／resume（重讀工單）。三件事都沒發生，行為就是 5.12.x。
- **工單有 `methodology`** → Phase 2 先依層序（規劃 → 執行 → 審查 → 驗證）照 adapter 寫的方式在本 session 內呼叫 workflow；工單自己的步驟、排除項與驗收閘門照樣適用。
- 舊工單的 `### BMad 工作流程` 照讀、照做，Worker 不改寫舊段落。

beta.1 在 Worker 端多寫清楚四件事（都來自隔離試用，見 § 隔離試用）：

| 事 | Worker 怎麼做 | 來源 |
|---|---|---|
| `methodology_ambient` 的寫法 | 照 `ct-exec` 附的範例寫事件，例：`SessionStart:startup`；看不出是哪個事件就寫「事件不明」 | P-5 |
| 被允許 skill 自帶的子代理 | 允許（唯讀審查子代理，含背景），但回報子代理數、是否背景、子代理內叫了哪些方法論 skill，每個 skill 一列 | Q-1 |
| 沒有 scratchpad | 方法論工作檔放系統暫存目錄下的 `ct-<工單號>/`，收尾刪除；repo 外不留檔 | P-4 |
| 環境偵測 | 只列變數名稱；`CT_MODE`、`CT_INTERACTIVE` 這類明列例外一次讀一個 | Q-2 |

beta.2 在 Worker 端再補三件事（來自 P3，見 § 實測 P3）：

| 事 | Worker 怎麼做 | 來源 |
|---|---|---|
| 「方法論 skill」的範圍 | 工單 `### 方法論邊界` 或執行步驟指名的 skill（含 ③ 的本地副本）也算；用了一樣記入 `### 方法論執行紀錄`。定義只在 `ct-exec` § Methodology | G2、P3 |
| ③ 副本怎麼用 | 副本有 `disable-model-invocation: true`，Claude Code 也只能以路徑讀 `SKILL.md`；讀了照做算一次呼叫 | P3-4 |
| 環境偵測的寫法 | bash 用 `compgen -e` 列名稱；明列例外一個變數一個指令讀 | P3-2 |

（權威：`ct-exec/SKILL.md` § Methodology (v6.0.0-pre.1+)、§ Startup、§ Mode And Environment）

---

## 已知未驗

6.0.0 為止的實測（RC 期間沒有新驗證到的項目，與 rc.1 相同；V1／V2a／V2b＋P1／P1b＋P3、beta.3 新範本對 BAT `0.7.1-pre.8` 解析器的實測、在 beta.7 上做的 adapter plugin probe 實測、穩定版 5.15.0 發版時在 BAT 上用手動指令驗過的送出順序、beta.10 發版前以 ct-exec 5.15.0＋BAT 0.7.2-pre.6 實機跑過的一批提問，beta.11 發版前以隔離 `claude -p` 跑過的節點檢查、beta.11 安裝後以實際 BAT 派工跑過的 4 張小工單、beta.12 發版前以 `claude -p` 實測的工具清單套用手段，以及 beta.10～beta.12 期間實際塔台 session 與收單的 session id 紀錄）沒有涵蓋下列 41 種情況，正式版 6.0.0 仍未實機驗證（CT `docs/CHANGELOG.md` `[6.0.0]` 的 Known unverified，與 `[6.0.0-rc.1]` 編號、順序相同）：

| # | 項目 | 為什麼還沒驗 |
|---|---|---|
| 1 | Codex 互動 TUI 的「Hooks need review」畫面，以及 `hooks.state.<key>.enabled` | V2a 用 `codex exec`（headless）測；TUI 的表現（exit `8`）是由程式內嵌字串與既有文件推得的；P1／P1b／P3 沒有跑 Codex |
| 2 | Codex 的 `resume`／`compact` 重注入 | V2a 只測了啟動時的注入；Claude Code 端（V1）已實測 resume、compact 都會重注入 |
| 3 | 引入方式 ③ 的周邊與 ②：Codex 端 `policy.allow_implicit_invocation: false`、引入方式 ②、③ 副本在 BAT worktree 隔離派工下的可見性；沒有 hook 的描述觸發（C1 ⑤） | ③ 本身已實測（P3：0 次自動叫用、塔台照規則寫【只允許】、Worker 3/3 以路徑讀並記錄）。P3 不跑 `codex`、② 照 D369 不加驗、試用塔台刻意不用 BAT（副本放在被 `.gitignore` 排除的目錄時 worktree 讀不到，是推論）；C1 ⑤ 標準安裝時塔台 0/1 被叫用，n=1，風險未排除 |
| 4 | Superpowers HARD-GATE：工單**明確指名** `superpowers:brainstorming` 時 | `methodology_guard: off`＋沒有 `methodology`、yolo 下已測 2/2 未觸發（Worker 不採用不負責任何層的注入）；指名的情況 P3 次數用完沒測。Superpowers 不建議引入，正常不會被工單指名 |
| 5 | ③ 副本裡「先問使用者」的步驟在 yolo 下改問塔台 | P3 的試用工單事先寫了答案（介面由 Worker 設計），這條路徑沒有出現；下次測試工單不要預先回答副本的提問 |
| 6 | yolo 的 headless 提問備援（沒有可用的等待工具時直接 `BLOCKED`） | P3 的 Worker 都判斷沒有要問塔台的決策，未觀察到；正式安裝後自然會驗 |
| 7 | 方法論疊加的跨層交接與回寫 | 一般疊加（P1）與雙注入＋疊加（P1b）已驗，各 n=1；但兩次都是塔台先定好介面、沒有用規劃層，所以跨層 `story-spec` 交接與 `writeback` 回寫沒有出現過 |
| 8 | 工單沒寫「不開分支／不 push」時，`poteto-mode` 會不會委派子代理或開 PR | P1b 拿掉整段邊界時，frontmatter 的 `delivery: none`／`subagent_writes: deny` 仍讓 poteto-mode 跳過 PR 與委派（n=1）；連 frontmatter 都沒有的情況沒測——v6 塔台一律會寫，要驗得手改工單 |
| 9 | 啟用即產生空索引、P-2 塔台語言規則、P-4 暫存目錄退路、Q-1 子代理回報要求，以及 beta.2 的環境偵測新寫法 | 都是文件規則，還沒有在實機上跑過（環境偵測新寫法是依 P3 的觀察改的，改後沒有再跑） |
| 10 | BAT 塔台面板讀取契約 | beta.3 的範本只以 BAT `0.7.1-pre.8` 的解析器實測（決策、BUG、待辦含 Dropped 全讀到，索引格子沒有 Unknown），還沒有在 BAT 實機面板逐頁看過；beta.4 寫入的 BAT `0.7.1-pre.9` 表現（「無法讀取 <檔名>」提示、`critical` 在任何讀取路徑都算 High）依 BAT 的通知，CT 端沒有實測，BAT 端的實機驗收也還沒做；已知差異：更舊的 BAT 在 `_backlog.md` Completed／Dropped 讀 PLAN 檔補值時，frontmatter `priority: critical` 仍顯示 Unknown |
| 11 | `customer_acceptance_gate: on` 的整條工單流程（開單初列、Worker 逐案判定、會改變就停下、部署後必跑、已完成修正回溯核對） | 都是文件規則，還沒有在實機上跑過；預設 `off`，只有手上有驗收案例表的專案才會開 |
| 12 | 決策日誌收斂在其他專案的實作 | 只在一個專案實作過（D001～D309 搬出，熱檔 583,571 → 188,989 bytes，BAT 決策頁 408 筆全讀到）；決策數、標題格式不同的專案還沒做過 |
| 13 | 未結 BUG 清理提示、熱檔大小提示、`PARTIAL` 當下收尾、`closed_reason` 與延後 BUG 的重開 | 都是文件規則，還沒有在實機上跑過 |
| 14 | 有前綴專案的實機回報：Worker 是否每次都送完整 ID（收尾通知、`--ask`、手動備援訊息），BAT 是否每次都能用 `--source` 對到 Worker 分頁並標 Done | 新範本與送出前比對都是 beta.4 才寫進去的，還沒有在設了前綴的專案實機觀察過 |
| 15 | 塔台端缺前綴容錯（熱區恰好一張「前綴 + 同號」時當作那一張、多張或找不到時問使用者、yolo 屬斷點 A） | 文件規則，還沒有實際觸發過 |
| 16 | 「已安裝但讀不到 → 本 session 提示一次」（`methodology-adapters.md` § 降級） | 文件規則，還沒有實際觸發過 |
| 17 | Codex 用 plugin 安裝、接 BAT `>= 0.7.2-pre.1` 派工的端到端流程（BAT 依安裝方式送 `$ct:ct-exec`） | BAT 驗證的是四種安裝狀態下的判斷結果；真的派一張工單給只裝 plugin 的 Codex Worker 還沒跑過（穩定版 5.14.2 同樣未驗） |
| 18 | 巢狀的獨立 repo 配置下的 BAT 面板一鍵派工 | 要另開一個指向上層的 BAT workspace；面板派工的 cwd = workspace 根是依 BAT 的行為推得。配置本身以穩定版 CT 5.14.2＋BAT 0.7.2-pre.1 實機驗過（`--skill` 派工），面板這條路還沒跑（穩定版 5.14.3 同樣未驗） |
| 19 | 依 runtime 的新搜尋順序（先試本 runtime 的 probe、另一個 runtime 的只當讀檔來源並註明一次） | 實機看到的是舊順序的問題（Claude 塔台推得會取 Codex 那份）；新順序是依規則推得，`bmad.yaml` 0.2.1、`ct-adapter-pstack` 0.2.6 改過的 probe 也還沒在塔台實際跑過（穩定版 5.14.4 的 bmad-guide 偵測同樣未驗） |
| 20 | 塔台 context 壓縮後仍不重複提醒（已升級給使用者、還在等回答的題） | 重複通知一行結束、`⏸ YOLO PAUSED` 只出現一次、升級後的重複通知不重出 ⏸ 都已實機驗過；要等塔台 context 真的被壓縮才會出現，還沒碰到（穩定版 5.15.0 同樣未驗） |
| 21 | 塔台收單補記 session id：BAT 的 `claudeSessionId` 與工單 `session_ids` 不同時的追加 | 從 BAT MCP 找到 Worker 那一列、讀值、與工單比對、寫收單快照都已在實機收單跑過多次；每次工單都已含該值，「追加」這一步還沒實際觸發 |
| 22 | 塔台對話依決策日誌切到各工單的方向（上一筆到這一筆、+60 秒寬限、限同一個塔台 session） | 未經結果驗證，所以報表標「估」、只當對照 |
| 23 | 卡住訊號門檻（最近 10 次呼叫失敗 ≥ 3 次） | 未校準：樣本工單全是 `DONE` |
| 24 | 隔離工單（worktree）另加 `--project <編碼後的 worktree 路徑>` | 多個 `--project` 只以合成資料測過 |
| 25 | plugin 安裝時 `/<plugin>:ct-exec` 的工單歸屬 | 只以合成資料測過 |
| 26 | 估算成本與 `cost-state` 的差距（約 −10%） | 沿用原型的量測，正式腳本沒有再對帳 |
| 27 | Worker 寫 `session_ids`：Renew 時在新 session 追加、單獨的 `unavailable` 被真實值取代 | 一般收尾寫入已有多張工單、Codex Worker 寫 `unavailable` 已實測；這兩種情況還沒實際觀察到 |
| 28 | `ct-evolve --facts-from` 對真實快照的一輪 | 候選事實寫進 `_learnings.md`、同一個 `fact_id` 重跑時更新原條目、`⏸ 撤回候選` 的恢復都未實測 |
| 29 | 「環境事實 → Tactical」的路徑 | 候選事實目前只有一條規則（卡住訊號），這條路只能經人工整理才會出現，還沒有實例 |
| 30 | `ct-done` 寫 `session_ids` | 還沒在實際補救收尾跑過 |
| 31 | BAT `--settings` 條文的症狀描述（`blockedDetection: none`、`started: unknown`、`claudeSessionId: null` 同時出現） | 來自 BAT 的回覆，CT 端沒有實機重現 |
| 32 | mem0 Level 3 的啟用條件（沒有例外紀錄時不啟用並提示一次、有紀錄時照常啟用） | 文件規則，還沒有實際觸發過（發版時本機沒有安裝 memsync） |
| 33 | 沒有新段落時不在 `### 互動紀錄` 寫「沒有新段落」 | 不讀全文、檢查次數正確已驗；這一行在隔離 `claude -p` 與實際 BAT 派工合計 8 次中有 7 次仍寫（含 Codex），加了例子之後實際派工的 4 張也都寫了；規則不改 |
| 34 | 收單時核對的「沒有讀入紀錄」 | Claude Code Worker 透過檔案變更提示常會讀到晚到的段落（2/2），「沒有讀入紀錄」只會在 Worker 最後一個回合之後才寫入時出現（例：工單已 commit、session 已結束），還沒實機跑過 |
| 35 | BAT `--settings` 的第二個理由與 BAT `>= 0.7.3-pre.8` 的待送通知（「待送通知 N」、8 筆上限） | 依 BAT 的通知寫成，CT 端沒有實機重現 |
| 36 | 同步 skill 用 `skillOverrides`（完整前綴名）、同步 plugin 用 `enabledPlugins`（`<plugin>@synced`）關閉 | CLI 2.1.316 實測有效，但官方文件沒寫，Claude Code 改版可能失效；發版前可用 `claude -p` 的 `system/init` 重驗 |
| 37 | `permissions.deny` 的單向性 | `enableArtifact` 設 `false` 之後沒有檔案能再打開是已知的；裸工具名寫進 `permissions.deny` 之後能不能由其他設定檔再打開，沒驗過 |
| 38 | `syncClaudeAiSkills: false` 放在 `.claude/settings.local.json` | 放在專案 `.claude/settings.json` 會被忽略；放 local 的效果沒實測，所以報告不寫成建議 |
| 39 | claude.ai connector 在專案層的停用 | 停用方式沒驗過，報告只建議在 claude.ai 帳號的 connector 設定處理 |
| 40 | 關掉 `Artifact`（`enableArtifact: false`）之後有沒有移出清單 | `claude -p` 的清單沒有 `Artifact`，只能在互動 session 用 `/context` 或下一次 `*insights tools` 確認，還沒有實際套用確認過 |
| 41 | 使用者層／專案層 agent 定義的移除（刪除 agent 定義檔） | 照寫但沒驗過 |

跟 beta.12 的 42 項比：第 1～20 項照舊；第 21 項（收單補記）只留「BAT 的值與工單不同時的追加」；第 22 項（塔台啟動記 session id）已在實際塔台 session 照規格跑過（`CLAUDE_CODE_SESSION_ID` 與 BAT 的 `claudeSessionId` 相同），移除；第 28 項改寫成第 27 項（只留 Renew 追加與 `unavailable` 被取代）；其餘往前移一號，內容不變。

跟 beta.11 的 36 項比：第 1～36 項照舊；第 37～42 項是 beta.12 的工具清單建議在套用手段上還沒驗到、或官方文件沒寫的部分，都只在 v6。在 CLI 2.1.316 以 `claude -p` 實測過的手段（同步 skill 用完整前綴名的 `skillOverrides`、`@synced` plugin 的 `enabledPlugins`、`permissions.deny` 寫裸工具名會移出清單）不列進清單。

跟 beta.10 的 33 項比：第 1～33 項照舊；第 34～36 項是 beta.11 的執行中補充工單與 BAT 補註還沒驗到的部分，都只在 v6。節點檢查本身（三個節點各自讀到、基準、沒有提問通道時衝突不擴權、不 commit 也讀得到、`ct-done` 寫回報前讀到）已用隔離的 `claude -p` 驗過；隔離工單讀主 checkout、yolo 下衝突改用 `提問`、跨 session 提醒自己的 Worker 的四種情況、Codex Worker 的節點檢查已在安裝後以實際 BAT 派工驗過（6 個情境加 Codex 節點檢查全部通過），都不列進清單。

跟 beta.9 的 23 項比：第 1～19 項照舊；第 20、22、23 項已實機驗證、移除（ct-exec 5.15.0＋BAT 0.7.2-pre.6：一批 4 題只叫醒塔台 1 次；4 題同時等、每次 22 秒共 7 輪，塔台叫醒後約 174 秒才答，4 題都 `answered`、0 題 `expired`；黏在一起的 `T#### 提問T#### 提問` 當成一則）；第 21 項縮小成新的第 20 項（只剩塔台 context 壓縮後仍不重複提醒）；第 21～28 項是 beta.10 的 token 用量統計、第 29～32 項是 session 證據與 ECC 退場、第 33 項是 mem0 Level 3 的啟用條件，都只在 v6。

跟 beta.8 的 19 項比：第 1～19 項照舊；第 20～23 項是 beta.9 移植的 5.15.0 規則還沒在新 session 實機驗到的部分，穩定版 5.15.0 同樣未驗。

跟 beta.7 的 20 項比：第 1～15 項照舊；第 16 項（`CLAUDE_CONFIG_DIR` 與 plugin 目錄）、第 17 項（adapter 的 plugin probe）已實機驗證、移除；原第 18～20 項改編為第 16～18 項；第 19 項是 beta.8 新順序還沒驗到的部分，規則穩定版 5.14.4 也有。

跟 beta.6 的 19 項比：第 1～19 項照舊（第 16 項的「本版的 adapter plugin probe」改稱「beta.6 起的」）；第 20 項是 beta.7 移植的文件還沒驗到的部分，穩定版 5.14.3 也有。

跟 beta.5 的 16 項比：第 1～15 項照舊；第 16 項補一句「adapter 的 plugin probe 也兩處都查」；第 17～19 項是 beta.6 新條文還沒驗到的部分——17、18 只在 v6 的 adapter，19 的規則穩定版 5.14.2 也有。

跟 beta.4 的 15 項比：第 1～15 項照舊；第 16 項是 beta.5 新條文還沒驗到的部分。plugin 的條文穩定版 5.14.0 也有，但第 16 項只出在 v6 的 § 路徑解析（穩定版沒有這一節）。

跟 beta.3 的 13 項比：第 1～9、11～13 項照舊；第 10 項改寫成 BAT `0.7.1-pre.9` 的現況（pre.9 的表現依 BAT 通知、CT 端未實測）；第 14、15 項是 beta.4 新規則還沒驗到的部分，這批規則穩定版 5.13.1 也有。

跟 beta.2 的 9 項比：第 1～9 項照舊（第 9 項的「環境偵測新寫法」指的是 beta.2 的寫法）；第 10～13 項是 beta.3 新規則還沒驗到的部分，這批規則穩定版 5.13.0 也有。

beta.1 的 7 項到 beta.2：「Superpowers HARD-GATE」縮小成「工單明確指名時」（第 4 項）；「②、③」縮小成 ③ 的周邊與 ②（第 3 項，③ 本身已驗）；
第 5、6 項是 P3 新發現沒驗到的；第 9 項加上 beta.2 的環境偵測新寫法。其他（Codex TUI、Codex 重注入、跨層交接、poteto-mode）照舊。

---

## 常見誤解

| 誤解 | 實際 |
|---|---|
| 「v6 還是 Beta／RC，不能當正式版用」 | 6.0.0 起是正式版，取代 5.15.0 成為穩定版；本章的 Beta／RC 標示是預發行期間的狀態（§ 6.0.0：納入正式版） |
| 「v6 不能用 plugin marketplace 裝」 | 6.0.0 起可以（`ct@control-tower` 6.0.0）；不能用 marketplace 的只有預發行版 beta、rc（下一列是當時的說法） |
| 「Beta 會取代我裝的 5.15.0」 | 不會。Beta 只打包、不安裝，下載在預發行 Release（不是 Latest），首頁與 `/install` 仍是 5.15.0；要試建議用隔離設定目錄（§ 全域路徑） |
| 「Beta 也能用 plugin marketplace 裝」 | 不能。marketplace 只上架穩定版，beta 照舊用 zip；在 beta 環境執行 plugin 安裝指令，裝到的是穩定版 5.x，會和手動安裝的 beta 並存（§ beta.5：plugin 安裝就緒） |
| 「plugin 安裝是 Beta 才有的新功能」 | 正好相反。plugin 安裝是穩定版 5.14.0 的功能，寫在主教材 `governance.md` § plugin marketplace：另一種安裝方式；beta.5 只是把同一批條文移進 v6，beta 本身沒有 plugin |
| 「beta 環境不能用 plugin 版 bmad-guide」 | beta.6 起可以：bmad-guide 不跟 CT 版號，可以從穩定 marketplace 只裝它，adapter 的 plugin probe 偵測得到（已實機驗證）；CT 本身仍用 zip（§ beta.6） |
| 「probe 加了 `runtime`，自己寫的 adapter 要改」 | 不用。`runtime` 是選填，沒寫 = 所有 runtime 適用，照列出順序試、行為和 beta.7 相同；只對某個 runtime 有意義的路徑建議加上（§ beta.8） |
| 「塔台改了工單，Worker 馬上就會照做」 | 不是。Worker 只在驗證前、產品 commit 前、寫回報前看一次段落標題（Claude Code Worker 另會收到「檔案已變更」的提示，常會提早讀到）；長步驟中途讀不到，急的話請使用者在 Worker 分頁說「重讀工單」，或用選用的跨 session 提醒（§ beta.11） |
| 「RC 還會再加功能」 | 不會。RC 期間功能凍結、只修錯，新功能排到下一個 MINOR；RC 沒有發現要修的問題就發正式版 6.0.0（§ rc.1：正式版候選（只修錯）） |
| 「`*insights tools` 會幫我把用不到的工具關掉」 | 不會。它只出建議報告、不改任何設定；要不要改、改哪一層由你決定，改完開新 session 才生效。專案層設定塔台與 Worker 共用，關掉就兩邊都關（§ beta.12：工具清單建議） |
| 「beta.10 起不能用 mem0 了」 | 能用，但要在專案的本地規則寫明符合使用者層規範的哪一條例外、量測依據與日期、元件名稱與版本；沒有紀錄時塔台不啟用 Level 3，偵測到會提示一次（`integration.md` § Level 3 › 啟用條件） |
| 「一次問多題只叫醒塔台一次是 Beta 才有的」 | 不是。同批規則穩定版 5.15.0 也有，寫在主教材 `work-order-lifecycle.md`〈一批只叫醒塔台一次〉；Worker 與塔台都要換成 beta.9（或 5.15.0）才完全生效（§ beta.9） |
| 「Codex 搭配 BAT 一定要用 zip」 | 看 BAT 版本：BAT `>= 0.7.2-pre.1` 兩種安裝都支援（穩定版 5.14.2、beta.6 起）；beta 本身只有 zip，同機另裝穩定版 CT plugin 時才相關（`bat-integration.md` § 誰負責 `/` 還是 `$`） |
| 「一個塔台管多個巢狀的獨立 repo 是 Beta 才有的」 | 不是。這份配置文件穩定版 5.14.3 也有，而且用到的規則 5.14.2 就有；寫在主教材 `advanced-patterns.md` § 巢狀的獨立 repo（§ beta.7） |
| 「狀態衛生、BAT 塔台面板讀取契約是 Beta 才有的」 | 不是。同批規則穩定版 5.13.0 也有，寫在主教材各章（§ beta.3：狀態衛生與 BAT 塔台面板讀取契約） |
| 「通知用完整工單 ID、面板契約對齊 BAT `0.7.1-pre.9` 是 Beta 才有的」 | 不是。同批規則穩定版 5.13.1 也有，寫在主教材各章（§ beta.4：通知用完整工單 ID 與 BAT 塔台面板讀取契約） |
| 「塔台會容忍缺前綴的回報，所以 Worker 截短也沒關係」 | 不是。塔台容錯只保住塔台收單，BAT 仍用 `--source` 對 Worker 分頁，截短了照樣標不了 Done（`work-order-lifecycle.md` § 回報與通知用完整工單 ID） |
| 「升到 v6 就要改設定、改舊工單」 | 不用。沒有任何 `methodology*` 鍵 = `auto` = 5.12.x 行為；舊工單照讀、不回寫。唯一要注意的是 BUG／PLAN／EXP 改成預設開啟，不要就明寫 `false`；從 beta.1 升 beta.2 沒有設定變更；從 beta.2 升 beta.3 不需要遷移，新增的三個設定不設就用預設；從 beta.3 升 beta.4、從 beta.4 升 beta.5、從 beta.5 升 beta.6、從 beta.6 升 beta.7、從 beta.7 升 beta.8、從 beta.8 升 beta.9、從 beta.9 升 beta.10、從 beta.10 升 beta.11、從 beta.11 升 beta.12、從 beta.12 升 rc.1 都只換 skill 檔案 |
| 「CT 能接方法論，所以每家都該裝起來」 | 不是。方法論不是一定要引入：BMAD 引入（預設）、pstack 選用、Superpowers 不建議引入、mattpocock/skills 只是 ③ 的可選範例（§ 方法論不是一定要引入） |
| 「CT 建議用 ② 或 ③ 引入 Superpowers」 | 那是 beta.1 的寫法，beta.2 已改：Superpowers 在 CT 下沒有實測效益，不建議引入；已經裝了的機器，CT 照共存防護處理 |
| 「pstack 是 v6 推薦的第二套方法論」 | 不是。`ct-adapter-pstack` 是選用：已在用 pstack 的人才裝，CT 不預設、不主動推薦 |
| 「用 mattpocock/skills 會讓 Worker 的品質變好」 | 沒有證據。P3 證明的是 ③ 的機制有效（不會被自動叫用、指名才用、有記錄），用與不用的品質差異沒有比較過 |
| 「只想用某個方法論的一個 skill，也得整套裝」 | 不用。② 只引用 skill：只裝 skill、不裝 hook，沒有常駐注入（§ 引入方式）；前提是那家方法論值得引入 |
| 「【只允許】的 skill 開了子代理就是違規」 | 被允許 skill 自帶的唯讀審查子代理（含背景）與它叫的子 skill 是允許的，但要照實回報（Q-1） |
| 「環境偵測要把變數印出來，才看得出設定對不對」 | 只要名稱就夠判斷有無；`BAT_REMOTE_TOKEN` 只記「已設定」（§ 環境偵測只列名稱） |
| 「bash 列名稱用 `env \| cut` 就好」 | beta.2 改用 `compgen -e`：`env` 要被放行才跑得動，而放行 `env` 等於放行整組值；明列例外也要一個變數一個指令讀 |
| 「adapter 會執行方法論」 | 描述檔是資料。真正呼叫 workflow 的是 Worker，在同一個 session 內，照 ct-exec 規則 |
| 「方法論說 done 就能 DONE」 | 還要工單驗證閘門通過；方法論 done 但閘門沒過，以閘門為準 |
| 「這張用 X 做」會連交付也交給 X | 不會。交付層要另外明說 |
| 「`warn` 只是印一行警告」 | `warn` = 塔台**自動在工單加邊界段**＋派工摘要提示 |
| 「hook 沒信任，塔台幫我信任一下就好」 | 塔台不替使用者信任：那等於核准 sandbox 外執行程式 |
| 「方法論的 playbook 就是 CT Playbook」 | 不是。CT Playbook 是工單序列；方法論的 playbook 是工單內步驟，`*evolve` 不晉升它（C3） |
| 「5 層就是 Layer 1～5」 | 不是。方法論的「層」與三層架構的 Layer、能力等級的 Level 都無關 |

---

## 圖：5 層 × adapter 疊加

規格見 `diagrams.md` § 18；下面是可直接使用的 SVG（範例設定：`methodology: bmad`、`methodology_execution: pstack`，其他層 `inherit`，交付層 `none`）。

```svg
<svg width="100%" viewBox="0 0 680 600">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>

<!-- CT 核心：編排 -->
<g class="node c-gold" onclick="sendPrompt('介紹方法論轉接的分工：CT 管編排、方法論管工單內紀律')">
  <rect x="40" y="20" width="600" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="40" text-anchor="middle" dominant-baseline="central">CT 核心：編排（不可交給 adapter）</text>
  <text class="ts" x="340" y="60" text-anchor="middle" dominant-baseline="central">生命週期・落點檢查・回報・commit／push・yolo 提問</text>
</g>
<line x1="340" y1="76" x2="340" y2="124" stroke-width="1" marker-end="url(#arrow)"/>
<text class="ts" x="350" y="102" dominant-baseline="central">派工時解析：每層選一個負責者</text>

<!-- 5 層 -->
<g class="node c-teal" onclick="sendPrompt('介紹方法論的 5 層')">
  <rect x="40" y="130" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="96" y="148" text-anchor="middle" dominant-baseline="central">規劃</text>
  <text class="ts" x="96" y="166" text-anchor="middle" dominant-baseline="central">planning</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹方法論的 5 層')">
  <rect x="162" y="130" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="218" y="148" text-anchor="middle" dominant-baseline="central">執行</text>
  <text class="ts" x="218" y="166" text-anchor="middle" dominant-baseline="central">execution</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹分層疊加時審查層用誰')">
  <rect x="284" y="130" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="148" text-anchor="middle" dominant-baseline="central">審查</text>
  <text class="ts" x="340" y="166" text-anchor="middle" dominant-baseline="central">review</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹方法論的 5 層')">
  <rect x="406" y="130" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="462" y="148" text-anchor="middle" dominant-baseline="central">驗證</text>
  <text class="ts" x="462" y="166" text-anchor="middle" dominant-baseline="central">verification</text>
</g>
<g class="node c-teal" onclick="sendPrompt('介紹為什麼交付層預設不交給方法論')">
  <rect x="528" y="130" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="584" y="148" text-anchor="middle" dominant-baseline="central">交付</text>
  <text class="ts" x="584" y="166" text-anchor="middle" dominant-baseline="central">delivery</text>
</g>

<!-- 設定值 -->
<text class="ts" x="96" y="204" text-anchor="middle" dominant-baseline="central">inherit</text>
<text class="ts" x="218" y="204" text-anchor="middle" dominant-baseline="central">pstack</text>
<text class="ts" x="340" y="204" text-anchor="middle" dominant-baseline="central">inherit</text>
<text class="ts" x="462" y="204" text-anchor="middle" dominant-baseline="central">inherit</text>
<text class="ts" x="584" y="204" text-anchor="middle" dominant-baseline="central">none（預設）</text>
<line x1="96" y1="182" x2="96" y2="226" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="218" y1="182" x2="218" y2="226" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="340" y1="182" x2="340" y2="226" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="462" y1="182" x2="462" y2="226" stroke-width="1" marker-end="url(#arrow)"/>
<line x1="584" y1="182" x2="584" y2="226" stroke-width="1" marker-end="url(#arrow)"/>

<!-- 負責者 -->
<g class="node c-coral" onclick="sendPrompt('介紹內建 bmad adapter 與 bmad-guide 的關係')">
  <rect x="40" y="232" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="96" y="250" text-anchor="middle" dominant-baseline="central">bmad</text>
  <text class="ts" x="96" y="268" text-anchor="middle" dominant-baseline="central">主方法論</text>
</g>
<g class="node c-amber" onclick="sendPrompt('介紹 ct-adapter-pstack')">
  <rect x="162" y="232" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="218" y="250" text-anchor="middle" dominant-baseline="central">pstack</text>
  <text class="ts" x="218" y="268" text-anchor="middle" dominant-baseline="central">層設定</text>
</g>
<g class="node c-coral" onclick="sendPrompt('介紹分層疊加時審查層用誰')">
  <rect x="284" y="232" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="250" text-anchor="middle" dominant-baseline="central">bmad</text>
  <text class="ts" x="340" y="268" text-anchor="middle" dominant-baseline="central">跟主方法論</text>
</g>
<g class="node c-coral" onclick="sendPrompt('介紹抽換與分層疊加的差別')">
  <rect x="406" y="232" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="462" y="250" text-anchor="middle" dominant-baseline="central">bmad</text>
  <text class="ts" x="462" y="268" text-anchor="middle" dominant-baseline="central">跟主方法論</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹為什麼交付層預設不交給方法論')">
  <rect x="528" y="232" width="112" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="584" y="250" text-anchor="middle" dominant-baseline="central">不交給方法論</text>
  <text class="ts" x="584" y="268" text-anchor="middle" dominant-baseline="central">要明說才開</text>
</g>

<!-- 跨層交接 -->
<path d="M96 284 Q157 322 218 288" fill="none" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
<g onclick="sendPrompt('介紹分層疊加的跨層交接與回寫')">
  <text class="ts" x="157" y="326" text-anchor="middle" dominant-baseline="central">交接：story-spec</text>
</g>

<!-- adapter 來源 -->
<rect x="40" y="346" width="600" height="104" rx="16" stroke-width="0.5" stroke-dasharray="4 3" fill="none" opacity="0.5"/>
<text class="ts" x="56" y="364" dominant-baseline="central">adapter 描述檔（資料，不是程式）搜尋順序：adapters_path ＞ 專案本地 ＞ 外部 skill ＞ 內建</text>
<g class="node c-coral" onclick="sendPrompt('介紹內建 bmad adapter 與 bmad-guide 的關係')">
  <rect x="56" y="380" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="144" y="398" text-anchor="middle" dominant-baseline="central">CT 內建</text>
  <text class="ts" x="144" y="416" text-anchor="middle" dominant-baseline="central">adapters/bmad.yaml</text>
</g>
<g class="node c-amber" onclick="sendPrompt('介紹 ct-adapter-pstack')">
  <rect x="252" y="380" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="340" y="398" text-anchor="middle" dominant-baseline="central">外部 skill</text>
  <text class="ts" x="340" y="416" text-anchor="middle" dominant-baseline="central">ct-adapter-pstack</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹專案本地 adapter 與何時要配 guide skill')">
  <rect x="448" y="380" width="176" height="52" rx="8" stroke-width="0.5"/>
  <text class="th" x="536" y="398" text-anchor="middle" dominant-baseline="central">專案本地</text>
  <text class="ts" x="536" y="416" text-anchor="middle" dominant-baseline="central">_ct-workorders/_adapters/</text>
</g>

<!-- 注入防護 -->
<g class="node c-teal" onclick="sendPrompt('介紹方法論邊界段與 methodology_guard')">
  <rect x="40" y="474" width="290" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="185" y="494" text-anchor="middle" dominant-baseline="central">### 方法論邊界（warn 自動加）</text>
  <text class="ts" x="185" y="514" text-anchor="middle" dominant-baseline="central">負責者【只允許】・其他注入【不使用】</text>
</g>
<g class="node c-gray" onclick="sendPrompt('介紹方法論注入防護的 V1、V2a、V2b 實測')">
  <rect x="350" y="474" width="290" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="495" y="494" text-anchor="middle" dominant-baseline="central">實測：邊界段 7/7 有效</text>
  <text class="ts" x="495" y="514" text-anchor="middle" dominant-baseline="central">V1・V2a・V2b → 維持 warn</text>
</g>

<!-- 圖例 -->
<text class="ts" x="40" y="560" dominant-baseline="central">圖例：金＝CT 核心　青綠＝層與工單段落　珊瑚＝BMAD　琥珀＝外部 adapter（借用）　灰＝不交給方法論／記錄</text>
<text class="ts" x="40" y="580" dominant-baseline="central">5 層 ≠ 三層架構的 Layer ≠ 能力等級 Level</text>
</svg>
```

**Drill-down**：

| 點哪裡 | `sendPrompt()` | 回答時讀 |
|---|---|---|
| CT 核心 | 介紹方法論轉接的分工：CT 管編排、方法論管工單內紀律 | 本章 § 為什麼要方法論轉接 |
| 規劃／執行／驗證 | 介紹方法論的 5 層 | 本章 § 5 層與需求類型 |
| 審查、審查下的 bmad | 介紹分層疊加時審查層用誰 | 本章 § 抽換 vs 分層疊加 › 分層疊加 |
| 交付、不交給方法論 | 介紹為什麼交付層預設不交給方法論 | 本章 § 抽換 vs 分層疊加 › 設定疊加順序與「這張用 X 做」、§ 注入防護 › 衝突時誰贏 |
| 驗證下的 bmad | 介紹抽換與分層疊加的差別 | 本章 § 抽換 vs 分層疊加 |
| 交接虛線 | 介紹分層疊加的跨層交接與回寫 | 本章 § 抽換 vs 分層疊加 › 分層疊加 |
| bmad、CT 內建 | 介紹內建 bmad adapter 與 bmad-guide 的關係 | 本章 § 從 Level 2 到方法論轉接、§ adapter 是什麼 › 什麼時候要另外配一個 guide skill |
| pstack、外部 skill | 介紹 ct-adapter-pstack | 本章 § adapter 是什麼 › 三種來源 |
| 專案本地 | 介紹專案本地 adapter 與何時要配 guide skill | 本章 § adapter 是什麼 |
| 邊界段 | 介紹方法論邊界段與 methodology_guard | 本章 § 注入防護 › 四道防線 |
| 實測 | 介紹方法論注入防護的 V1、V2a、V2b 實測 | 本章 § 注入防護 › 為什麼預設 `warn` 而不是 `block` |

---

## 本章引用的 CT 檔與章節

| CT 檔 | 章節 |
|---|---|
| `control-tower/references/methodology-adapters.md` | § 分工、§ 層次、§ 需求類型（routing 的鍵）、§ 描述檔格式（beta.6：› probe 怎麼解析 skill 根目錄）、§ 新 adapter 的最小檢查、§ 舊欄位相容、§ 狀態對應總則、§ 降級、§ 與 hook／session 路由的相處規則、§ 引入方式、§ 抽換（專案選主方法論）、§ 分層疊加（不同層用不同方法論）、§ 解析步驟（塔台派工時）、§ 散布與搜尋順序、§ 未來介接（新方法論要不要配 guide skill）、§ 衝突與防護 |
| `control-tower/references/adapters/bmad.yaml` | `retired_names`；beta.6：`detection.probes`（beta.8：依 runtime 拆開、0.2.1） |
| `control-tower/references/methodology-adapters.md`（beta.2 新增引用） | § 引入方式（原則段、建議表、表下實測點）、§ ③ 的做法（例：mattpocock/skills）、§ 衝突與防護 C1 ⑤、C5、C10 |
| `control-tower/references/tower-config.md` | § 方法論設定鍵（v6.0.0+）、§ 可用選項 |
| `control-tower/references/work-order-template.md` | 標準模板 `### 方法論邊界`、§ 填寫方法論欄位指引（v6.0.0+）、§ 撰寫方法論子代理授權（v6.0.0+）、§ 撰寫〈相關通過案例〉（客戶驗收不回歸閘，v6.0.0-beta.3+） |
| `control-tower/references/bug-plan-system.md` | § 啟用與索引檔、§ 索引格式、§ 結案判準、§ 未結 BUG 清理提示（beta.3） |
| `control-tower/references/decision-log-system.md`（beta.3 新增引用） | § 格式規則、§ 收斂 |
| `control-tower/references/work-order-system.md`（beta.3 新增引用） | § PARTIAL 當下收尾（含 resolved `PARTIAL` 補正）；beta.4：§ 回報與通知用的工單 ID、§ 回報處理流程 › 回報 ID 對不上時；beta.6：§ 工單 ID 格式（權威定義） |
| `control-tower/references/data-layer-architecture.md` | § 路徑解析（P-3，T0314；beta.5：`~/.claude/plugins/` 例外列；beta.8：改成單一路徑）；beta.5：§ 寫入規則（beta.6 補 `CLAUDE_CODE_PLUGIN_CACHE_DIR`） |
| `control-tower/references/version-governance.md`（beta.5 新增引用） | § 安裝／升級流程 › plugin 安裝／升級（v6.0.0-beta.5+）、› 從 zip 手動安裝遷移到 plugin、› Codex 搭配 BAT 派工：依 BAT 版本（beta.6 改名；beta.5 時是〈繼續用 zip 手動安裝〉） |
| `control-tower/SKILL.md` | § Role（語言規則） |
| `control-tower/references/enhancement-integration.md` | § Level 2：方法論轉接（methodology adapter）（beta.6：› 偵測入口、› Playbook → 方法論回饋）；beta.10：§ 外部增強外掛治理、§ ECC Level 1 退場、§ Level 3 › 啟用條件 |
| `control-tower/references/mono-repo-patterns.md`、`multi-tower-protocol.md`（beta.6 新增引用） | 專案上下文（`AGENTS.md` 的區塊）的說法；beta.7：`mono-repo-patterns.md` § 巢狀的獨立 repo（一個塔台、多個共用 repo）、`multi-tower-protocol.md` § 決策：一個塔台還是多個 |
| `control-tower/references/memory-protocol.md` | § 機器可讀摘要（YAML frontmatter）、§ BAT 塔台面板讀取契約（beta.3；beta.4 對齊 BAT `0.7.1-pre.9`） |
| `control-tower/references/yolo-mode.md`（beta.4 新增引用） | § 斷點 A：Worker 回報非預期狀態（beta.9：看通知字串結尾）；beta.9：§ Worker 向塔台提問（§ BAT 通道、§ Worker 端 3-A、§ 塔台端）、§ BAT / Worker 版本相容 |
| `control-tower/references/auto-session.md` | § Worker 啟動確認（`--wait-started`，v5.6.0+）、§ BAT 內部終端路由 › 偵測條件；beta.5：§ 依安裝方式的 skill 呼叫字串（v6.0.0-beta.5+）；beta.6：§ 執行方式、§ 依賴的 BAT 基礎設施；beta.10：§ Claude 啟動參數不得放 `--settings` |
| `control-tower/scripts/validate-adapter.py` | （腳本；beta.6：M8 檢查 `skill_root`；beta.8：M8 檢查 probe `runtime`） |
| `ct-exec/SKILL.md` | § Methodology (v6.0.0-pre.1+)、§ Startup、§ Mode And Environment、§ Phase 2: Execute（beta.3）、§ BAT Notify And Fallback（beta.4）、§ Questions For Tower（beta.9）、§ Phase 4 › Session id（beta.10）、§ Phase 3 第 1 步與 § Tower Addenda Check（rc.1 改寫法） |
| `ct-insights/references/analysis-rules.md`、`ct-insights/scripts/ct-session-stats.py`（beta.10 新增引用） | § Session 用量統計（`*insights sessions`，v6.0.0-beta.10+）（含 § 快照、§ 候選事實）；腳本與 `pricing.json`；beta.12：§ 工具清單建議（`*insights tools`，v6.0.0-beta.12+） |
| `control-tower/references/work-order-system.md`、`memory-protocol.md`、`data-layer-architecture.md`（beta.10 補引用） | § 收單補記 session id、§ 收單快照；§ 塔台 session id；§ `_ct-workorders/_insights/` |
| `ct-done/SKILL.md`（beta.4 新增引用） | § BAT Notify；beta.10：§ Report Repair › Session id；beta.11：§ Workflow 第 6 步（寫回報前的補充段檢查；rc.1 改成先寫） |
| `ct-evolve/SKILL.md`、`control-tower/references/self-learning-core.md`（beta.10 新增引用） | § Session Evidence；§ 置信度系統 |
| `ct-exec/references/session-guardrails.md` | § compact／resume 後重讀工單（v6.0.0-pre.1，所有工單；beta.11 補一句執行中補充） |
| `control-tower/references/work-order-system.md`、`cross-project-coordination.md`、`ct-exec/SKILL.md`（beta.11 新增引用） | § 執行中補充工單；§ 通知自己的 Worker 重讀工單；§ Tower Addenda Check |
| `ct-help/SKILL.md` | § Methodology Adapters (v6.0.0+)；beta.11：§ Session Usage And Evidence (v6.0.0-beta.10+) |
| `ct-adapter-pstack/README.md` | 〈引入方式建議〉；beta.6：`adapter.yaml`（0.2.5）；beta.8：`adapter.yaml`（0.2.6） |
| `docs/CHANGELOG.md` | `[6.0.0]`（含 Known unverified、從 5.15.0 升級）、`[6.0.0-rc.1]`、`[6.0.0-beta.12]`、`[6.0.0-beta.11]`、`[6.0.0-beta.10]`、`[6.0.0-beta.9]`、`[6.0.0-beta.8]`、`[6.0.0-beta.7]`、`[6.0.0-beta.6]`、`[6.0.0-beta.5]`、`[6.0.0-beta.4]`、`[6.0.0-beta.3]`、`[6.0.0-beta.2]`、`[6.0.0-beta.1]`、`[6.0.0-pre.1]` |
| `docs/BMad Control Tower 安裝(升級)與使用指南 v5.md` | § 2.65、§ 2.64、§ 2.63、§ 2.62、§ 2.61、§ 2.60、§ 2.59、§ 2.58、§ 2.57、§ 2.56、§ 2.55、§ 2.54、§ 2.53、§ 2.52、§ 4.1 |

`*onboard` 也會問主方法論，並在需要時提三種引入方式；偵測到沒有 adapter 的注入時改說「方法論不是一定要引入」（CT `onboarding.md` § 主題 5：主方法論（v6.0.0+））。
