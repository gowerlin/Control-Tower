---
title: 課程道館說明
description: 「多代理規格驅動開發實戰」6 章道館：每章的題目、驗收、自我驗證方式、參考解 tag 內容與常見卡點。參考解在公開程式碼 repo 的 dojo-ch1～dojo-ch6 tag。
---

<script setup>
import { useData } from 'vitepress'

const { theme } = useData()
const codeRepo = theme.value.courseCodeRepoUrl
</script>

# 課程道館說明

<p class="ct-lead">每章最後一個單元是「道館」：用一個可驗證的產出結束這一章。這一頁整理 6 個道館的題目、驗收、怎麼自己驗、參考解裡有什麼，以及常見卡點。</p>

## 開始之前

- **程式碼**：clone 公開 repo <a :href="codeRepo" target="_blank" rel="noreferrer">ct-bat-bmad-go-sms</a>，每章從起點 tag 開分支：`git switch -c my-chN chN-start`。repo 的根就是影片裡的 `sms-platform/`。取得方式與 tag 的意思見[課程：下載與程式碼](/course#downloads)。
- **參考解**：`dojo-chN` tag。做完後 `git diff my-dojo-chN dojo-chN` 對照；路徑不用帶前綴。
- **影片的路徑**：影片與投影片裡的 `courses/ct-bat-bmad-go-sms/sms-platform/…` 一律對應程式碼 repo 的根，見[影片與公開 repo 的對照](/course#video-vs-repo)。
- **編號**：頁面上的工單（`T0001` 這類）與決策（`D001` 這類）都是示範專案自己的編號，在程式碼 repo 的 `_ct-workorders/` 裡找得到。你自己做時照 CT 規則取號，不必和示範專案一樣；練習用的工單用 `T9` 開頭的四碼編號，不占正式編號。
- **真實執行紀錄**：示範畫面用的逐字稿、回答腳本與快照不在程式碼 repo，影片與投影片 PDF 中可見。

**提交方式**（每章相同）：本課是自學課程，沒有收件人，「提交」就是自我驗收＋留下可回溯的證據。

1. 驗收逐項自驗通過。
2. 產品檔與工單各自 commit（commit 訊息含工單編號），在你的 repo 打 tag，例如 `git tag my-dojo-ch1`。
3. 測試輸出、`/ct-status` 結果與決策留在工單回報區與決策日誌。
4. 對照參考解：`git diff my-dojo-chN dojo-chN`。文字不必一樣，要比的是結構與證據。

在討論區求助時，貼 tag 名稱與測試輸出即可；**不要貼權杖、`.env` 或含使用者名稱的完整路徑**。

## CH1：派出第一張最小工單 {#ch1}

單元 1-06｜影片 30 分＋實作 45–60 分鐘｜起點 `ch1-start` → 參考解 `dojo-ch1`

**題目**：寫 `T0001`（可用 1-05 的草稿），在第二個 Claude Code 終端用 `/ct-exec T0001` 執行。這一章還沒裝 BAT，手動派工正是重點。Worker 填完回報區後，塔台收單、`*sync`、記決策 `D001`。

1. **終端 A（塔台）**：在 repo 根啟動 Claude Code，執行 `/control-tower`；下一個工單編號應是 `T0001`。
2. **開單**：`repo` 與 `created_at` 都要跑指令取得（Git Bash `basename "$(git rev-parse --show-toplevel)"`、`date "+%Y-%m-%dT%H:%M:%S%z"`；PowerShell `Split-Path -Leaf (git rev-parse --show-toplevel)`、`Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"`）；驗收條件都要是指令能驗的。
3. **終端 B（Worker）**：同一個資料夾開另一個 Claude Code，`/ct-exec T0001`。Worker 依序做落點檢查、`IN_PROGRESS`、建檔、`go test`、產品 commit、回報區、`DONE`、工單 commit，最後給你一句要貼回塔台的完成訊息。
4. **收單**：把完成訊息貼給塔台。塔台逐條核對驗收證據、`*sync`、把這次的決定記成 `D001`、更新 tower-state。
5. **錄重播**：把驗證步驟寫成 VHS tape，確認任何時候都能重現。

**驗收**：(1) `go.mod` 存在且獨立；(2) `go test ./...` 全綠，含 `TestE2E_Healthz`；(3) `T0001` 是 `DONE`、body 鏡像一致、`*sync` 無 drift；(4) tower-state 列出 `T0001`、`D001` 已寫；(5) 全程可用 VHS tape 重播。

| 項 | 指令或檔案 | 通過時看到 |
|---|---|---|
| (1) | `go list -m all` | `module example.com/sms-platform`、`go 1.27.3`；只有一行 |
| (2) | `go test ./... -v` | `--- PASS: TestE2E_Healthz`，最後沒有 `FAIL` |
| (3) | `/ct-status T0001`；塔台 `*sync` | `DONE`；沒有 drift 警告 |
| (4) | `_ct-workorders/_tower-state.md`、`_decision-log.md` | 有 `T0001`；`D001` 有背景、至少 2 個選項、決定與理由、影響、相關工單 |
| (5) | `vhs <你的>.tape` | 從頭跑完、不需人工輸入、畫面上沒有權杖與個資 |

**參考解 `dojo-ch1`**：Go module 骨架（`go.mod`、`cmd/smsd/`、`internal/httpapi/`、`e2e/healthz_test.go`）、`_ct-workorders/T0001-*.md`（含填好的回報區）、`_ct-workorders/_decision-log.md` 的 `D001`。tag 裡那份 `T0001` 對應 `ch1-start` 已經建好的骨架（產品 commit 訊息因此不含 `T0001`），檔案比較多；影片 1-06 畫面上那份是在獨立示範 repo 真實執行的，只有工單列的五個檔，你做出來的會比較像那一份。

**常見卡點**

- **Go 沒裝或版本不對**：`go version` 要看到 `go1.27.3`。Worker 執行中才發現沒有 Go，應回報 `BLOCKED`；不要讓 Worker 自己下載或換版本，修好環境後由塔台 Renew 再派。
- **路徑含空白**：指令裡一律加雙引號。Git Bash 的 `/c/...` 路徑不要傳給原生 Windows 程式，改用 `cygpath -m`。
- **`repo` 欄填錯，Worker 一開工就被落點檢查 C-0 擋下（`WRONG_REPO_CONFIRMED`）**：在塔台終端跑上面的指令，把輸出照抄回 `repo`。程式碼 repo 的根就是 sms-platform，`repo` 填 clone 下來的目錄名（預設 `ct-bat-bmad-go-sms`）；sms-platform 放在更大的 repo 裡時填外層 repo 名，`affects_files` 也加上前綴（例：`services/sms-platform/go.mod`）。**不要**為了通過檢查加 `landing_check`。
- **`*sync` 說有 drift**：frontmatter 與 body 不一致。`*sync` 以 frontmatter 為準、只警告不覆寫，把 body 改成一致再 `*sync`。
- **Worker 找不到 `T0001`**：兩個終端要在同一個資料夾（同一個 repo）。

## CH2：立案文件齊、story 1 綠燈 {#ch2}

單元 2-10｜影片 30 分＋實作 60–90 分鐘｜起點 `ch2-start`（＝`dojo-ch1`）→ 參考解 `dojo-ch2`

**題目**：用自己的措辭從 forged-idea 跑到 `stories.yaml`＋`epics.md`，用 `bmad-review` 至少跑一個 lens 修正 PRD，用 `bmad-project-context` 建 `AGENTS.md`，最後用 `bmad-build` 完成 story 1。速成路徑可以直接用參考版 PRD 與 SPINE，只跑 spec、epics、build。

七個步驟都**在 repo 根啟動 Claude Code**（BMad-Method v6.12.4 裝在 `_bmad/`，skill 在 `.claude/skills/`，產物落在 `_bmad-output/`）。建議每個 skill 開一個新 session，每完成一步 commit 一次。

| 步驟 | 路徑 | skill | 產出 | 單元 |
|---|---|---|---|---|
| 1 壓力測試點子 | 高手 | `bmad-forge-idea` | `forged-idea.md` | 2-02 |
| 2 brief → PRD | 兩者（速成用參考版） | `bmad-product-brief`、`bmad-prd` | `_bmad-output/planning-artifacts/briefs/…`、`…/prds/…/prd.md` | 2-03 |
| 3 架構不變量 | 高手（速成用參考版） | `bmad-architecture` | `…/ARCHITECTURE-SPINE.md` | 2-04 |
| 4 SPEC＋stories | 兩者 | `bmad-spec` | `_bmad-output/specs/spec-<slug>/SPEC.md`、`stories.yaml` | 2-05 |
| 5 epics＋就緒閘門 | 兩者 | `bmad-create-epics-and-stories`、`bmad-sprint-planning` | `epics.md`、`sprint-status.yaml`（閘門 PASS） | 2-06 |
| 6 review 修 PRD、建手冊 | 兩者 | `bmad-review`、`bmad-project-context` | PRD 修訂 commit；`AGENTS.md`；`CLAUDE.md` 的 `@AGENTS.md` | 2-09、2-07 |
| 7 實作 Story 1.1 | 兩者 | `bmad-build` | `spec-1-1-*.md`、程式碼與 `e2e/` 測試、本機 commit | 2-08 |

本課的 story 規則：`stories.yaml` 每則 story 加自訂欄位 `e2e: TestE2E_<Feature>_<Behavior>`，同一個測試名也寫進標準欄位 `invoke_dev_with`（`bmad-spec` 的 schema 沒有 `e2e`）；`bmad-create-epics-and-stories` 不讀 `stories.yaml`，寫 epics 時在對話裡帶入切法與測試名；一則 story ＝ 一張工單 ＝ 一個 E2E 名。

**驗收**：(1) 六份文件（brief、PRD、ARCHITECTURE-SPINE、SPEC＋`stories.yaml`、`epics.md`、`AGENTS.md`）齊全且互相引用一致；(2) 每則 story 的 `e2e` 是合法的 `TestE2E_*`；(3) 八項功能（REST 發送 API、供應商 adapter、發送佇列與重試、狀態回報 webhook、模板、速率限制、多租戶 API key、E2E／BDD 測試門檻）都有 story，且寫明「不做 Web 主控台」；(4) `bmad-review` 的發現至少回寫一處；(5) `go test ./...` 全綠，含 `TestE2E_SendMessage_Returns202AndQueryable`。

| 項 | 指令或檔案 | 通過時看到 |
|---|---|---|
| (1) | SPEC 每個 `CAP-N` 在 PRD 有出處；或單獨跑就緒閘門 | 閘門 `PASS`，沒有孤兒需求 |
| (2) | `Select-String 'e2e: ' <spec 資料夾>/stories.yaml` | 每則一行，`TestE2E_` 開頭、只有英數與底線 |
| (3) | `Select-String 'Web 主控台' <prd.md>, <SPEC.md>` | 非目標寫明「不做 Web 主控台」 |
| (4) | `git log -p -- <prd.md 路徑>` | 有一次 review 之後的修訂 |
| (5) | `go test ./... -v` | `--- PASS: TestE2E_SendMessage_Returns202AndQueryable`、`--- PASS: TestE2E_Healthz` |

**參考解 `dojo-ch2`**：在拋棄式副本裡真實跑十個 BMad skill 的產物（只做了去識別與格式整理）：`_bmad-output/forge/`、`planning-artifacts/briefs/`、`prds/`（含 validation 報告）、`architecture/`（含三份審查）、`specs/spec-sms-platform/`（`SPEC.md`、`stories.yaml`、`glossary.md`、`state-machines.md`、`error-codes.md`）、`epics.md`、`implementation-artifacts/sprint-status.yaml`（閘門先 CONCERNS，修完 PASS）、`AGENTS.md`；Story 1.1 的 `spec-1-1-send-and-query-message.md` 與程式 `internal/{httpapi,queue,store}/`、`e2e/messages_test.go`。review 用 verification gaps lens 對 PRD 提出 6 筆發現，回寫其中一筆（補 `queue_full`）。

| `stories.yaml` id | `epics.md` | story | 功能 | `e2e` |
|---|---|---|---|---|
| 1 | 1.1 | 送出訊息並可查詢 | REST 發送 API | `TestE2E_SendMessage_Returns202AndQueryable` |
| 2 | 1.2 | mock Provider 故障注入 | 供應商 adapter | `TestE2E_MockAdapter_FaultInjection` |
| 3 | 2.1 | 缺 API key 回 401 | 多租戶 API key | `TestE2E_Auth_MissingKey401` |
| 4 | 2.2 | 跨租戶查詢回 404 | 多租戶 API key | `TestE2E_Tenant_IsolationReturns404` |
| 5 | 1.4 | 模板渲染變數 | 模板 | `TestE2E_Template_RendersVariables` |
| 6 | 2.3 | 超量回 429 與 Retry-After | 速率限制 | `TestE2E_RateLimit_Returns429WithRetryAfter` |
| 7 | 1.3 | 依 status 列表篩選 | REST 發送 API | `TestE2E_ListMessages_FilterByStatus` |
| 8 | 1.5 | 模板缺變數回 422 | 模板 | `TestE2E_Template_MissingVariableReturns422` |
| 9 | 1.6 | 重試後成功 | 佇列與重試 | `TestE2E_Queue_RetriesThenSucceeds` |
| 10 | 1.7 | 重試用盡標記 failed | 佇列與重試 | `TestE2E_Queue_ExhaustsRetriesMarksFailed` |
| 11 | 1.8 | 回呼更新狀態並只通知租戶一次 | 狀態回報 webhook | `TestE2E_Webhook_DeliveredUpdatesStatusAndNotifiesTenantOnce` |
| 12 | 1.9 | 三竹風格 Adapter 契約測試 | 供應商 adapter | `TestE2E_MitakeAdapter_ContractAgainstFakeServer` |

第 8 項功能（E2E 門檻）不另立 story：每則 story 都帶一個 `e2e`，`go test ./... -race` 全綠是收單條件。

**常見卡點**

- **打 `/` 找不到 `bmad-*` skill**：skill 裝在 repo 的 `.claude/skills/`，要從 repo 根啟動 Claude Code；剛裝好的要重開 session。`bmad-build` 一啟動就停：它要 `uv`。確認載入的版本：`_bmad/_config/manifest.yaml` 是 `6.12.4`。
- **產物落點錯**：影片說「跑到課程 repo 根就是錯的」，那是講師的製作 repo。**程式碼 repo 的根就是 sms-platform，產物落在根目錄的 `_bmad-output/` 是正確的**。真的落到別處，通常是在 repo 外啟動、載到另一份使用者層級的 BMad：把檔案搬回、從 repo 根重開、確認 manifest 後再繼續。
- **`e2e` 名不合法**：不能有空白、連字號或中文；Go 測試函式名要以 `Test` 開頭，例 `TestE2E_RateLimit_Returns429WithRetryAfter`。
- **story 粒度太大**：`bmad-build` 做到一半 spec 一直長、要動五六個套件，就回 `bmad-spec` 重切，更新 `stories.yaml` 與 `epics.md`，重跑就緒閘門再 build。
- **就緒閘門 FAIL 或 CONCERNS**：照它點名的 skill 修完再跑；最常見的是 `stories.yaml` 與 `epics.md` 對不上。

## CH3：兩則 story 轉成工單、手動派工、收單並記決策 {#ch3}

單元 3-09｜影片 30 分＋實作 60–90 分鐘｜起點 `ch3-start`（＝`dojo-ch2`）→ 參考解 `dojo-ch3`

**題目**：從 `stories.yaml` 挑「mock Provider 故障注入」（id `"2"`，寫成 `T0002`）與「多租戶 API key」（id `"3"`＋`"4"`，寫成 `T0003`），各寫一張工單：`repo`、`affects_files` 不重疊、`intervention_type: fire-and-forget`、驗收含 `TestE2E_*`。第二終端依序 `/ct-exec`，塔台依證據收單、寫 `D002`（記「API key 放 header 而非 query」）、`*sync`。這一章還不用 BAT，Worker 由你手動開第二個 Claude Code 扮演。

1. **挑 story**：`epics.md` 的編號和 `stories.yaml` 的 id 不同，一律用 `e2e` 測試名對應。還沒有 CH2 產物時，從 `ch3-start` 開始（裡面已有 `stories.yaml`）。
2. **開單**：確認下一號是 `T0002`、下一個決策是 `D002`。兩張的 `affects_files` 沒有交集；共用檔只歸一張（參考解把 `e2e/testutil` 歸 `T0003`，並寫進 `T0002` 的〈不做〉）。驗收貼上 3-07 的品質閘門片段。
3. **執行**：先 `/ct-exec T0002`；收完單再 `/ct-exec T0003`。
4. **收單**：逐條核對 `go test` 輸出、commit hash、改了哪些檔，用 `git diff --name-only <base>..HEAD` 對照 `affects_files`；證據不足判 `PARTIAL`，用 Renew 請 Worker 補，不由塔台代跑。派 `T0002` 前先記下 base commit。
5. **記決策與同步**：塔台預覽 `D002`（背景、至少兩個選項、決定與理由、影響、相關工單，並引用 `T0003` 回報區的證據），確認後寫入決策日誌，最後 `*sync`。

**驗收**：(1) 兩張 `DONE`、無 drift；(2) `TestE2E_MockAdapter_FaultInjection`（fail／timeout／delay）、`TestE2E_Auth_MissingKey401`、`TestE2E_Tenant_IsolationReturns404` 全綠；(3) `affects_files` 與實際 diff 一致；(4) `D002` 引用回報區而非摘要。

| 項 | 指令或檔案 | 通過時看到 |
|---|---|---|
| (1) | `/ct-status T0002`、`/ct-status T0003`；塔台 `*sync` | 兩張 `DONE`；沒有 drift 警告 |
| (2) | `go test ./e2e -run 'TestE2E_(MockAdapter\|Auth\|Tenant)' -v` | 三個測試各有 `--- PASS`（故障注入的三個子測試都有） |
| (3) | `git diff --name-only <base>..HEAD` | 每個檔案都在其中一張的 `affects_files` 裡 |
| (4) | `_ct-workorders/_decision-log.md` | 最上面是 `D002`，引用 `T0003` 回報區的測試輸出或 commit |

高手路徑的練習（故意寫錯 `repo` 觀察落點檢查 C-0、用 `*bug` 走一張 OPEN→CLOSED、對 `T0002` 跑 `*evolve`）用 `T9` 開頭的練習編號，不要占用第四章的 `T0004`。

**參考解 `dojo-ch3`**：`_ct-workorders/T0002-mock-provider-fault-injection.md`、`T0003-auth-and-tenant-isolation.md`（含回報區）；`internal/provider/mock/`（暫時／永久失敗、timeout、delay）；`internal/tenant/tenant.go`（key 只存 SHA-256）與 `internal/httpapi/auth.go` 的 `X-API-Key` 中介層；`e2e/mock_fault_test.go`、`auth_test.go`、`tenant_isolation_test.go`；決策日誌的 `D002`（另有高手路徑的實驗與回寫工單 `EXP-ROUTER-001`）；`_tower-state.md`。

**常見卡點**

- **派 `T0003` 時 overlap check BLOCK**：`T0002` 還沒收單、兩張都列了同一個共用檔，或有一張沒寫 `affects_files`。改工單或等收單；**不要**輸入「確認接受衝突」。
- **落點檢查 C-0 擋下**：照 CH1 的做法把 `repo` 改成實際的目錄名，重新派工；C-0 在動手前就停，沒有檔案被改。
- **Worker 說「全部完成」就收單**：那是摘要不是證據。找 `--- PASS` 的實際輸出、commit hash、改過的檔案，缺一條就判 `PARTIAL`。
- **`*sync` 之後 drift 還在**：`*sync` 只警告不覆寫，改 body 再同步。Worker 中斷、狀態卡在 `IN_PROGRESS`，用 `/ct-done T0002 PARTIAL` 補救結案，不要手改 frontmatter。
- **`-race` 在 Windows 報 cgo 錯誤**：在 dev container 內跑，或在回報區寫明改在容器執行；不得省略後當作通過。
- **timeout／delay 測試時好時壞**：用 `e2e/testutil` 的假時鐘，不要真的等待。

## CH4：yolo 批次派 3 張工單並處理一次 Worker 提問 {#ch4}

單元 4-10｜影片 30 分＋實作 60–90 分鐘（選配另加 30 分鐘）｜起點 `ch4-start`（＝`dojo-ch3`）→ 參考解 `dojo-ch4`

**題目**：從 `stories.yaml` 取 id `"6"`「超量回 429 與 Retry-After」、`"7"`「依 status 列表篩選」、`"8"`「模板缺變數回 422」，寫成 `T0005`（速率限制）、`T0006`（`GET /v1/messages` 列表與 status 篩選）、`T0007`（模板缺變數 422）三張 `affects_files` 不重疊的工單。`T0005` 刻意把「桶容量與補充速率、`Retry-After` 取整方式」留給 Worker 向塔台提問（演算法已由 SPINE AD-12 定為每 API key 一桶的 token bucket）。塔台以 yolo 批次派出三張、回答提問、依證據收單，最後回收三個 Worker 分頁。

**選配（高手）**：`T0007` 改在 4-09 的 Docker 分頁（dev container）裡由塔台派出並收單。容器掛的是 repo 根，容器路徑是 `/workspace/<你的 repo 目錄名>`（clone 成預設名稱時是 `/workspace/ct-bat-bmad-go-sms`）。

0. **前置單（塔台）**：三張都得改 `internal/httpapi/` 的路由組裝與錯誤對應。示範專案先開前置單 `T9003`，把 `internal/httpapi/` 拆成每個功能一個檔、預留 stub，收單後三張的 `affects_files` 才能兩兩不交集。你的切法可以不同，但共用檔要先處理掉。
1. **開單**：`repo`、`created_at` 跑指令取得；三張 `affects_files` 沒有交集；驗收寫 E2E 名並貼上品質閘門（`make test`＝`go test ./... -race` 全綠）。`T0007` 建立在 4-03 的 `T0004`（模板 CRUD＋渲染）之上，`T0004` 要先收單。
2. **yolo 批次派工**：`*config auto-session yolo`。派工前塔台跑 overlap check，完全相同的檔案就 BLOCK，不要硬派。每張都用同一套派工五要件：

   ```bash
   "${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-terminal.mjs" \
     --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
     --cwd "<repo 根目錄>" --mode yolo --no-interactive \
     --agent default --skill ct-exec --workorder T0005 --wait-started 30000
   ```

   只看 exit code：`0` 看 `started:` 行；`8` 分頁在但未確認啟動，不重派；`1` 走降級鏈（stderr 有 `RECOVERY_PENDING` 先回答 BAT 的 Recovery 提示）。
3. **提問**：`T0005` 的 Worker 在回報區最上面寫 `#### Q-1`、frontmatter 加 `tower_question: open`、commit 後以 `bat-notify.mjs --ask` 送出，再用 `bat_wait_question` 原地等。塔台用 MCP `bat_list_questions` 看題目，以 `bat-terminal.mjs --answer <questionId> --choice <n>` 回答，並把決定記成下一個 D 編號，引用 SPINE AD-12 與 `T0005` 的提問。
4. **收單**：逐張核對 `go test` 輸出、commit hash、改過的檔案；用 `git diff --name-only <base>..HEAD` 對照三張的 `affects_files`。
5. **回收**：`--close-worker T0005 --notify-id "$BAT_TERMINAL_ID"`（`T0006`、`T0007` 同），最後 `bat_list_terminals`（`scope=mine`）確認 Worker 都不在了。

**驗收**：(1) 三張 `DONE`，三個 Worker 分頁縮圖到 ✓；(2) 至少一次提問被塔台 `--answer` 回覆並記入決策日誌；(3) `TestE2E_RateLimit_Returns429WithRetryAfter`、`TestE2E_ListMessages_FilterByStatus`、`TestE2E_Template_MissingVariableReturns422` 全綠；(4) `--close-worker` 回收三個分頁；(5) 派工與回收指令可由 VHS 重播（權杖不入鏡）；(6) 選配：`T0007` 回報區的落點檢查記的是容器內路徑 `/workspace/<你的 repo 目錄名>/…`，主機端 `git log` 看得到容器內做的同一個 commit，主機端 `go test ./... -race` 仍全綠。

| 項 | 指令或檔案 | 通過時看到 |
|---|---|---|
| (2) | `T0005` 的 `### 互動紀錄`；決策日誌 | 一行 `[HH:MM] Q-1: … → A（塔台）: … → Action: …`；frontmatter 已無 `tower_question`；決策引用 `T0005` 的 Q-1 與 SPINE AD-12 |
| (3) | `go test ./e2e/... -race -v -run 'TestE2E_(RateLimit\|ListMessages\|Template_Missing)'` | 三個測試各有 `--- PASS`；再跑 `make test` 全綠 |
| (4) | 塔台呼叫 `bat_list_terminals`（`scope=mine`） | 沒有三張的 Worker 分頁 |
| (5) | 你的派工與回收指令 | 只用 `$BAT_TERMINAL_ID`、`$BAT_WORKSPACE_ID`、`$BAT_HELPER_DIR` 等環境變數，沒有寫死權杖或主機路徑 |

高手路徑的延伸：三張改用 `--isolation worktree` 派工、收單後走塔台直接合併；用 `bat_list_terminals`／`bat_wait_question` 從塔台監看 Worker；故意關掉 BAT 再打開，觀察 Recovery 提示與 `RECOVERY_PENDING`，確認塔台沒有自動重派。

**參考解 `dojo-ch4`**：前置單 `_ct-workorders/T9003-httpapi-feature-split.md` 與拆好的 `internal/httpapi/*.go`；`T0005-rate-limit.md`（含 `### 待塔台決策` 的提問與 `### 互動紀錄`）、`T0006-list-messages-filter-status.md`、`T0007-template-missing-variable-422.md`；`internal/ratelimit/`（每 API key 一個 token bucket、可注入 clock）、`internal/httpapi/ratelimit.go`、`messages_list.go`、`errors_templates.go`；`e2e/ratelimit_test.go`、`messages_list_test.go`、`template_missing_variable_test.go`；4-03 的 `T0004-template-crud-and-render.md`；決策日誌（`T0005` 兩題答覆記成兩筆決策）；`compose.yaml`（dev container）。選配的「容器內派工」講師環境沒有錄：容器內只真實跑了 `go test`，`T0007` 是在主機 BAT 派的。

**常見卡點**

- **派第二張時 overlap check BLOCK**：三張都列了 `internal/httpapi/` 的同一個檔。共用檔只歸一張，其他用 `depends_on` 指向它，或改走 `--isolation worktree`。
- **`T0005` 的 Worker 沒有提問**：補練一次提問通道。先在 `T0005` 回報區補寫 `#### Q-1`、加 `tower_question: open` 並 commit，再在 `T0005` 的 Worker 分頁手動送出同一題（題目只走 stdin）：

  ```bash
  # q1.json：{"question":"Q-1：桶容量與補充速率、Retry-After 取整方式？","options":["照 SPINE AD-12","容量與補充速率改用全域預設"],"detail":"Worker 建議：照 SPINE AD-12","blocking":true}
  "${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR/bat-notify.mjs" --ask --source T0005 \
    --target "$BAT_TOWER_TERMINAL_ID" --submit --expires-min 30 "T0005 提問" < q1.json
  ```

  下次開單時在〈不做〉或驗收寫明「這兩項不得自行決定，須向塔台提問」。
- **exit 1 且 stderr 有 `RECOVERY_PENDING`**：BAT 剛重開，先到 BAT 視窗回答 Recovery 提示，再重新派工；回答後不會自動補建分頁，塔台也不會自動重派。
- **exit 8（`started: unconfirmed`）**：分頁已經建立，**不要重派**；用 `bat_get_state` 看分頁。
- **等答覆逾時，Worker 以 `BLOCKED` 收尾**：塔台改在工單的 `## 塔台補充（Renew #N）` 寫 `- **塔台答覆 Q-1**：…` 再重派；重派前先 `--close-worker T0005 --delay-ms 0` 回收舊分頁。
- **三張幾乎同時回報**：塔台一次處理一張，其他排隊不會遺失；回報格式不對（例如「搞定了」）是斷點 A，yolo 也會停下來請你確認。
- **選配：Docker 分頁的 Worker 開在錯的目錄**：分頁起點是 mount 根 `/workspace/<你的 repo 目錄名>`，不是 compose 的 `working_dir`；`--cwd` 一定要寫完整容器路徑。clone 成別的資料夾名時設 `SMS_REPO_NAME`，見程式碼 repo README 的〈dev container〉。

## CH5：一個 epic 的批次派工並合併 {#ch5}

單元 5-10｜影片 30 分＋實作 90–120 分鐘（建議分兩次）｜起點 `ch5-start`（＝`dojo-ch4`）→ 參考解 `dojo-ch5`

**題目**：以 `T0008`、`T0009`（`depends_on: T0008`）、`T0010` 完成 epic 1。`T0008` 與 `T0010` 以 `--isolation worktree` 平行派出並合併，`T0009` 等 `T0008` 合併後再派；每張的收單門檻是對應 E2E 全綠；最後跑 `bmad-retrospective`。

| 工單 | 內容 | story（id） | 收單門檻（E2E） |
|---|---|---|---|
| `T0008` | 佇列與重試：worker pool、指數退避、attempts 與 failed 終態 | 9、10 | `TestE2E_Queue_RetriesThenSucceeds`、`TestE2E_Queue_ExhaustsRetriesMarksFailed` |
| `T0009` | 狀態回報 webhook：供應商回呼、狀態更新、租戶 callback（HMAC 簽章、冪等） | 11 | `TestE2E_Webhook_DeliveredUpdatesStatusAndNotifiesTenantOnce` |
| `T0010` | 三竹風格 HTTP adapter：契約測試、`PROVIDER=mock\|mitake` 切換 | 12 | `TestE2E_MitakeAdapter_ContractAgainstFakeServer` |

> 三竹風格 adapter 免責：本課只模擬公開文件描述的表單風格，不代表三竹實際介面，不連接真實端點，與三竹資訊無合作或背書關係。

1. **確認起點**：三張在 5-02 已建好、`status: PENDING`，紅燈骨架就位；`T0008`、`T0010` 有 `isolation: worktree`。記下 base commit。
2. **第一波派工**：派 `T0008`、`T0010`，派工指令加 `--isolation worktree`；BAT 在主 checkout 上層建 `.bat-worktrees/<repo 目錄名>/T0008`，分支 `ct/T0008`。exit `7`（`WORKTREE_FAILED`）不重試、不改成非隔離。
3. **收單與合併**：依回報區證據收單（含 `branch`／`base_sha`／`validated_sha`／`head_sha`）→ `--close-worker … --worktree keep` → 查 `--worktree-status`，逐條對照五條直接合併判準：五條全成立走模式 ①（塔台直接合併，不開合併工單，記在決策日誌）；任一條不成立就派合併工單（`kind: merge`、`merge_mode: conflict`）。合併後清理 worktree（不加 `--force`）。
4. **第二波派工**：`T0008` 合併回 `main` **之後**才派 `T0009`。
5. **全綠**：主 checkout 的 `main` 上 `go test ./... -race`，含八項功能全部 E2E；`providertest` 契約對 `mock`、`mitake` 各跑一次（`PROVIDER` 只在 `cmd/smsd` 啟動時讀，切換由 `TestNewProvider_*` 驗證）。
6. **回顧**：對 epic 1 跑 `/bmad-retrospective`，確認過的行動項交給塔台轉成 followups 或 PLAN，最後 `*sync`。

速成路徑可以全部序列派工、不用 worktree，或只讓 `T0010` 走 worktree。高手路徑三張都隔離派工，並至少製造一次衝突、完整走一次 `merge_mode: conflict` 合併工單；也可以用 godog 把 E2E 改寫成 Feature。合併模式 ②（conflict）在錄製時實機跑過；③（port）只依 CT v5.12.2 文件設計，錄製時尚未實機驗證，行為和文件不同時以你安裝的 CT 版本為準，並把指令與輸出記進合併工單回報區。

**驗收**：(1) 三張 `DONE` 且 `main` 上 `go test ./... -race` 全綠，`providertest` 對 `mock`／`mitake` 皆綠；(2) 至少一張走 worktree 並留下 SHA 比對五步紀錄，`--worktree-status` 無殘留；(3) webhook E2E 驗證租戶 callback 只收到一次且簽章正確；(4) 三竹風格 adapter 測試不連外網；(5) retrospective 至少兩條行動項轉成 followups 或 PLAN。

| 項 | 指令或檔案 | 通過時看到 |
|---|---|---|
| (1) | `/ct-status` 三張；`PROVIDER=mitake go test ./... -race`（PowerShell：`$env:PROVIDER = 'mitake'; go test ./... -race`） | 三張 `DONE`；兩次都沒有 `FAIL` |
| (2) | 決策日誌（模式 ①）或合併工單回報區（模式 ②）；`git worktree list` | 有 `base_main_sha`、`head_sha`、merge commit 的 parent1／parent2、ff 後的 `main`；`.bat-worktrees/` 沒有已合併工單的 worktree |
| (3) | `go test ./e2e -run Webhook -count=1 -v` | `--- PASS`；測試確實檢查「重送也只通知一次」與 HMAC 簽章 |
| (4) | 讀 adapter 測試；暫時斷網再跑 | 請求位址都來自 `httptest`；斷網照樣 PASS |
| (5) | `epic-1-retro-<日期>.md`；`sprint-status.yaml` 的 `action_items` | 至少兩條行動項，各有對應單號 |

**參考解 `dojo-ch5`**：`T0008-queue-send-worker-and-retry.md`、`T0009-status-webhook.md`、`T0010-mitake-style-adapter.md`（`T0008`、`T0010` 的回報區有 `branch`／`base_sha`／`validated_sha`／`head_sha`）；`T0010` 走模式 ① 直接合併（紀錄在決策日誌），`T0008` 判準不成立、派合併工單 `T0011-merge-T0008.md`（模式 ②）；`internal/queue/`、`internal/webhook/`、`internal/store/store.go`（outbox）、`internal/provider/mitake/`、`internal/provider/providertest/contract.go`、`cmd/smsd/provider.go`；`e2e/queue_retry_test.go`、`webhook_test.go`、`mitake_adapter_test.go`；`features/`（godog）；`_bmad-output/implementation-artifacts/epic-1-retro-2026-10-23.md`（判定 rejected，理由見報告）。

**常見卡點**

- **exit `7`（`WORKTREE_FAILED`）**：塔台不重試、不自動改成非隔離。常見原因是 worktree 位置被占用或分支已在別處 checkout，`git worktree list` 看現況、清掉再重派；Windows 長路徑加 `-c core.longpaths=true`。
- **`git merge --ff-only` 被拒**：主 checkout 有未提交、和這次合併重疊的檔案。先處理你的檔案；**不要** stash、`reset --hard`、`--force`。合併期間 `main` 又前進了，照 SHA 比對五步第 ⑤ 步處理。
- **`T0009` 在 `T0008` 合併前就派出**：DONE 只代表分支上的工作完成。請塔台回收分頁，等合併後重派。
- **webhook 測試偶爾顯示通知兩次**：冪等沒做好，不能收單；改用假時鐘與 `httptest`。
- **adapter 測試斷網就失敗**：測試偷偷連外，位址一律取自 `httptest`。
- **回顧有行動項、塔台沒有對應的單**：只寫在回顧報告裡不算，請塔台開單或建 PLAN，並把單號寫回 followups。

## CH6：結業道館：你的多代理工作流 {#ch6}

單元 6-06｜影片 30 分＋實作 60 分鐘｜起點 `ch6-start`（＝`dojo-ch5`）→ 參考解 `dojo-ch6`

**題目**：彙整 CH1–CH5「改造成你的工作流」段的產出，寫成自己專案適用的工作流文件；用 `*evolve --playbook` 固化至少一項為 L2 playbook；用 `*import --check` 確認一條自寫規則已載入；對課程專案跑 `*insights`。

1. **寫工作流文件**（約 30 分）：例如 `docs/multi-agent-workflow.md`，六個 `##` 區塊：工單模板片段、auto-session 對照表、worktree 準則、收單門檻、決策日誌規範、FIELDGUIDE 一頁。每區塊四行：規則（可用指令驗證的句子）、`參考：`（CT reference 或本課單元）、實例（sms-platform 上真實發生過的一次）、例外。寫完在 `AGENTS.md` 加一行指向它。
2. **固化成 L2 Playbook**（約 10 分）：`_ct-workorders/_tower-config.yaml` 設 `gp-prefix: <2–4 字大寫>` → 塔台 `*evolve`（候選要答完 Distillation Gate 五問）→ `*evolve --playbook <name>` → 確認草稿 → 寫入 `_ct-workorders/_playbooks/GP-<PREFIX>-001-<name>.md`。
3. **寫一條自寫規則並確認**（約 10 分）：塔台 `*import rule` → 確認合併計畫才寫入 `_ct-workorders/_local-rules.md` → `*import --check`，在狀態樹看到你的規則標題。規則寫成「觸發條件＋動作」，例如「驗收條件寫不出測試名就不開單」。
4. **跑 insights**（約 10 分）：`*insights`（或任何 session 的 `/ct-insights`）；分清報告裡的「事實」與「推論」，每條附工單編號的發現都回該工單回報區核對一次。

**驗收**：(1) 文件六個區塊齊全且每區塊引用對應的 reference；(2) `*evolve --playbook` 產出一份 L2 playbook，來源學習通過 Distillation Gate；(3) `*import --check` 列出你的自寫規則；(4) 工單模板片段能貼進 CT 工單格式而不破壞 frontmatter；(5) `*insights` 報告引用 ≥3 張工單證據。

| 項 | 指令或檔案 | 通過時看到 |
|---|---|---|
| (1) | `Select-String '^## \|^參考：' docs/multi-agent-workflow.md` | `##` 標題 6 個、`參考：` 行 6 個 |
| (2) | `_ct-workorders/_playbooks/`；`_learnings.md` | 有 `GP-<PREFIX>-###-<name>.md`，來源 Pattern 有 Learning／Trigger／Pattern／Action／Example 五欄 |
| (3) | 塔台 `*import --check` | `_local-rules.md` 底下列出你的規則標題 |
| (4) | 把片段貼進一張 `T9` 開頭的練習工單，跑 `/ct-status` | 沒有 frontmatter／body drift 警告 |
| (5) | `*insights` 報告 | 至少 3 個不同的工單編號被當作證據引用 |

**參考解 `dojo-ch6`**：講師版 `docs/multi-agent-workflow.md`；L2 Playbook 範例 `_ct-workorders/_playbooks/GP-SMS-001-parallel-worktree-merge.md`（來源學習在 `_learnings.md`、`gp-prefix: SMS` 在 `_tower-config.yaml`）；`FIELDGUIDE.md` 完整版；insights 報告 `_ct-workorders/_reports/insights-2026-10-23.md`；`_local-rules.md`（含一條自寫規則）；示範③把回顧行動項轉成的兩張下一輪工單。對照：`git diff my-dojo-ch6 dojo-ch6 -- docs/multi-agent-workflow.md _ct-workorders/_playbooks`。

**常見卡點**

- **`*evolve --playbook` 被拒（沒有 `gp-prefix` 也沒有 `project-prefix`）**：在 `_tower-config.yaml` 加 `gp-prefix`；先看別的塔台用了哪些前綴，不要重複。不要改設 `project-prefix` 湊數，它是跨專案工單前綴，語意不同。
- **沒有 reliable 以上的候選**：帶名稱 `*evolve --playbook <name>` 直接建立，或繼續累積驗證次數；來源 Pattern 都要指回答完五問的學習。
- **`*import --check` 看不到規則**：多半是用了 `*import playbook`（它寫 `_learnings.md`），改用 `*import rule`；或合併計畫那一步沒有確認。
- **片段貼進工單後 drift**：片段寫死了狀態或日期。body 元資料改成佔位，狀態與時間戳只在 frontmatter 由塔台填。
- **insights 說樣本太小**：工單少於 3 張。在已有 `T0001`～`T0010` 的程式碼 repo 裡再跑。
- **`/ct-fieldguide` 或 `/ct-insights` 找不到**：多半是用 `claude --setting-sources project,local` 啟動，使用者層的 CT skill 不會載入。把同版本的八個 CT skill 複製進 repo 的 `.claude/skills/`，見程式碼 repo README 的〈Control Tower skill 放哪一層〉。
