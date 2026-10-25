---
title: 課程
description: 「多代理規格驅動開發實戰」：用 BMad-Method、Control Tower 與 BAT 以 Go 打造 SMS 通訊平台。6 章、57 單元、影片約 21 小時。
---

<script setup>
import { useData } from 'vitepress'

const { theme } = useData()
const codeRepo = theme.value.courseCodeRepoUrl
const slides = (name) => `${theme.value.releasesUrl}download/${theme.value.courseReleaseTag}/${name}`
const slidesPage = `${theme.value.releasesUrl}tag/${theme.value.courseReleaseTag}`
const ctPublic = (name) => `${theme.value.releasesUrl}download/ct-v5.12.2/${name}`
</script>

# 課程：多代理規格驅動開發實戰

<p class="ct-lead">用 BMad-Method、Control Tower 與 BAT 以 Go 打造 SMS 通訊平台。這門課教已經會用 Claude Code 的開發者，把「一個人、一個 session」的 AI coding，升級成多代理、規格驅動、由工單約束的工作流。</p>

## 課程主張

**只有工單檔與驗收證據能約束多代理。**

一個 agent 可以靠測試約束；好幾個 agent 同時工作時，還需要一份大家都照著走的契約。這門課裡，BMad 的規劃產物綁定 CT 工單的驗收條件，E2E 與 BDD 測試是 Worker 收單的門檻：測試名寫在工單裡，沒有測試名就不開單。

三件套各自的位置：**BMad 想清楚、CT 管得住、BAT 跑得動**。貫穿全課的專案是一個後端 SMS 通訊平台，從一句話的點子做到八項功能齊全。

只想先花四十分鐘知道這三樣工具在做什麼，可以先看 5 支短片：[推廣影片（第二季）](/podcast)。

## 適合誰

- **適合**：會用 Claude Code 完成日常開發任務，但沒碰過 BMad-Method、Control Tower、BAT 的工程師與技術主管。
- **先備**：會用 git、會跑終端指令、看得懂一種靜態語言的程式碼。**不需要 Go 經驗**，Go 語法邊做邊帶，每個單元最多兩三個 Go 要點。需要一台能裝 Claude Code、Node.js、Go 與 BAT 的機器；環境設定範例涵蓋 Windows 11（含 WSL2）、macOS 與 Dev Docker 三組。
- **主線工具**：所有示範、錄影與 Worker 分頁都用 Claude Code。Codex 也能跟練（CT 的 8 個 skill 與 BAT 派工都支援，改用 `$` 前綴），課程用一頁說明差異。

不適合這門課的人：

- 還不會用任何 coding agent 的人（課程不教 agent 的基本操作）
- 想學 Go 語言本身的人
- 只需要前端或 UI 的人（課程不做 Web 主控台）
- 想要「一鍵全自動」、不願意讀工單檔的人

## 章節

全課 **6 章、57 單元，影片合計約 21 小時**。每章第一個單元是「速成 vs 高手學習路徑」，最後一個單元是「道館」：用一個可驗證的產出結束這一章。單元形式分成講解 28 個、示範 22 個、Live Coding 1 個、道館 6 個。

<CardTable
  :columns="['章', '標題', '單元', '影片長度', '道館產出']"
  :rows="[
    ['CH1', '新手村：一個 session 為什麼不夠', '7', '2:28:49', '派出第一張最小工單，建好 Go module 骨架與健康檢查 API'],
    ['CH2', 'BMad-Method v6：從點子到可派工的 story，做出第一支 API', '11', '4:03:48', '立案文件齊全（PRD、架構、SPEC、epics、AGENTS.md），第一則 story 綠燈'],
    ['CH3', 'Control Tower：工單編排、收單與治理', '10', '3:57:21', '把兩則 story 轉成工單、派給手動 Worker、收單並寫決策日誌'],
    ['CH4', 'BAT：多分頁執行環境、遠端 PTY 環境與自動派工', '11', '4:01:44', '以 yolo 批次派 3 張互不相依的工單，並處理一次 Worker 提問'],
    ['CH5', 'Go SMS 平台實戰：用三件套跑完一個 epic', '11', '4:05:47', '一個 epic 批次派工並合併，八項功能全部到位'],
    ['CH6', '進階與治理：讓多代理工作流長期可維護', '7', '2:22:32', '你自己的多代理工作流：工單模板、auto-session 策略、收單門檻與 FIELDGUIDE']
  ]"
  caption="課程章節"
/>

各章的重點：

- **CH1** 從 context 預算、塔台與 Worker 分離、Hard Boundaries、證據分道四個概念，說明一個 session 為什麼不夠，接著裝好三件套、跑第一次 `/control-tower`。
- **CH2** 走一遍 BMad-Method v6 的規劃：壓力測試點子、PRD、架構、SPEC 與 stories、epics，以及讓每個 Worker 拿到同一本手冊的 `AGENTS.md`，最後用標準實作迴圈做出第一支 API。
- **CH3** 深讀工單模板與 frontmatter，講派工與收單、落點檢查、反序寫入、回報判讀、三層架構與塔台記憶、BUG／PLAN／EXP、Worker 的防護與知識管線。對應 Portal 的[一張工單的一生](/lifecycle)與[進階區](/deep/)。
- **CH4** 接上 BAT：分頁角色、auto-session 四階、範圍權杖、yolo 與斷點、Worker 向塔台提問、回收與重派、worktree 隔離與合併工單，以及把 Worker 派進遠端與容器環境。
- **CH5** 用三件套把剩下的功能一次派完：測試策略與收單門檻、工單粒度與 `affects_files` 重疊、平行工單與三種合併模式、code review 與回顧。[實戰案例](/cases#conflict-merge)裡的衝突合併就是這一章的實錄。
- **CH6** 從一個專案走到一套制度：跨專案與多塔台、版本治理、FIELDGUIDE、Workflow 在單張工單內的用法，以及 BMad 下一代（V7）的遷移看點。

## 錄製時版本

課程內一律標示「本課錄製時版本」。

| 工具 | 版本 |
|---|---|
| BMad-Method | v6.12.4（示範專案自己安裝一份） |
| bmad-guide（教材對照） | v6.12.4 |
| Control Tower | v5.12.2 |
| CT Guide Skill | v5.12.2 |
| Better Agent Terminal | 0.7.1-pre.6 |
| Claude Code | 錄製時 `claude --version` 的輸出 |
| Go | 開工時的最新穩定版，鎖在示範專案的 `go.mod` |

CT 之後發新版時，課程仍以上表為基準；各功能需要的版本見[相容版本對照](/versions/compatibility)。

## 取得方式

課程以 6 支整章影片發布在 YouTube 播放清單：[多代理規格驅動開發實戰（YouTube 播放清單）](https://www.youtube.com/playlist?list=PLM1w-3eL8kgI)。播放清單公開後即可觀看。

| 章 | 標題 | 長度 |
|---|---|---|
| CH1 | 新手村：一個 session 為什麼不夠 | 2:28:49 |
| CH2 | BMad-Method v6：從點子到可派工的 story，做出第一支 API | 4:03:48 |
| CH3 | Control Tower：工單編排、收單與治理 | 3:57:21 |
| CH4 | BAT：多分頁執行環境、遠端 PTY 環境與自動派工 | 4:01:44 |
| CH5 | Go SMS 平台實戰：用三件套跑完一個 epic | 4:05:47 |
| CH6 | 進階與治理：讓多代理工作流長期可維護 | 2:22:32 |

每支影片的說明欄都列出各單元的時間碼，點一下就能跳到該單元。

## 下載與程式碼 {#downloads}

影片之外，學員拿到兩樣東西：示範專案的**程式碼 repo**（含 12 個道館 tag），以及每章一個 zip 的**投影片 PDF**。各章道館的題目、驗收與參考解對照，見[道館說明](/course-dojo)。

### 程式碼與道館 tag {#code}

示範專案 sms-platform 放在公開 repo <a :href="codeRepo" target="_blank" rel="noreferrer">ct-bat-bmad-go-sms</a>（MIT 授權）。repo 的根就是 sms-platform，Go module 在根目錄。clone 下來之後，每章從那一章的起點 tag 開自己的分支：

<div class="language-bash"><span class="lang">bash</span><pre><code>git clone {{ codeRepo }}.git
cd ct-bat-bmad-go-sms
git tag -l                          # ch1-start … ch6-start、dojo-ch1 … dojo-ch6
git switch -c my-ch1 ch1-start      # 從第一章道館的起點開始做</code></pre></div>

| tag | 指向 | 用法 |
|---|---|---|
| `chN-start` | 第 N 章道館開始時的狀態。`ch1-start` 是 `dojo-ch1` 的上一個 commit（課程骨架：go.mod、`/healthz`、E2E harness、自裝的 BMad-Method v6.12.4）；`ch2-start`～`ch6-start` 就是上一章的 `dojo-ch(N-1)` | `git switch -c my-chN chN-start`，在自己的分支上做這一章的道館 |
| `dojo-chN` | 第 N 章道館的參考解：工單（含填好的回報區）、程式、決策日誌 | 做完後對照：`git diff <你的分支或 tag> dojo-chN` |

- `dojo-ch1`～`dojo-ch6` 依序是祖先關係，所以 `chN-start` 就是「前面各章都做完」的狀態。`main` 是課程完稿（`dojo-ch6` 之後再整理文件），tag 不會跟著 `main` 移動。
- 對照時不用帶路徑：repo 根就是 sms-platform。只想看一部分，加 `-- internal/ e2e/` 這類路徑。
- 自己另開的 repo 沒有這些 tag 時，加一個 remote 取回 tag 再比對：`git remote add course <上面的 repo 網址>.git && git fetch course --tags`。
- repo 裡的工單與決策編號都是示範專案自己的；回報區記下的 commit SHA 屬於錄影時的開發歷史，公開 repo 的 commit 是依 tag 整理過的快照，查不到那些 SHA。

### 投影片 PDF {#slides}

每章一個 zip，內含該章每個單元一份 PDF，檔名就是單元編號與標題。PDF 與影片是同一版。全部放在 GitHub Release <a :href="slidesPage" target="_blank" rel="noreferrer">課程「多代理規格驅動開發實戰」投影片 PDF</a>。

| 章 | 下載 | PDF 數 | 大小 |
|---|---|---|---|
| CH1 | <a :href="slides('ct-bat-bmad-go-sms-CH1-slides.zip')">ct-bat-bmad-go-sms-CH1-slides.zip</a> | 7 | 5.2 MB |
| CH2 | <a :href="slides('ct-bat-bmad-go-sms-CH2-slides.zip')">ct-bat-bmad-go-sms-CH2-slides.zip</a> | 11 | 7.2 MB |
| CH3 | <a :href="slides('ct-bat-bmad-go-sms-CH3-slides.zip')">ct-bat-bmad-go-sms-CH3-slides.zip</a> | 10 | 8.1 MB |
| CH4 | <a :href="slides('ct-bat-bmad-go-sms-CH4-slides.zip')">ct-bat-bmad-go-sms-CH4-slides.zip</a> | 11 | 7.7 MB |
| CH5 | <a :href="slides('ct-bat-bmad-go-sms-CH5-slides.zip')">ct-bat-bmad-go-sms-CH5-slides.zip</a> | 11 | 7.2 MB |
| CH6 | <a :href="slides('ct-bat-bmad-go-sms-CH6-slides.zip')">ct-bat-bmad-go-sms-CH6-slides.zip</a> | 7 | 5.2 MB |

- 校驗：<a :href="slides('SHA256SUMS.txt')">SHA256SUMS.txt</a>，下載到同一個資料夾後執行 `sha256sum -c SHA256SUMS.txt`。
- zip 裡的 PDF 檔名是中文（UTF-8）。解壓縮後檔名變成亂碼時，改用 7-Zip 或 `tar -xf <zip 檔>`。
- **授權**：投影片 PDF 著作權屬課程作者、保留所有權利，可下載供個人學習觀看與列印，不授權改作與轉散布。程式碼 repo 以 MIT 授權，見 repo 的 <a :href="`${codeRepo}/blob/main/LICENSE`" target="_blank" rel="noreferrer">LICENSE</a>。BMad-Method 的授權與商標聲明，見 Control Tower 公開 repo 根目錄的 `THIRD-PARTY-NOTICES.md`。

### 錄製時用的工具版本 {#recording-tools}

想和影片用完全相同的版本跟練，可以下載這兩份：

| 工具 | 版本 | 下載 |
|---|---|---|
| Control Tower（公開版） | v5.12.2 | <a :href="`${theme.releasesUrl}tag/ct-v5.12.2`" target="_blank" rel="noreferrer">Release ct-v5.12.2</a>：<a :href="ctPublic('BMad-Control-Tower-v5.12.2-public.zip')">BMad-Control-Tower-v5.12.2-public.zip</a>（351 KB）、<a :href="ctPublic('control-tower-guide-v5.12.2-public.zip')">control-tower-guide-v5.12.2-public.zip</a>（126 KB） |
| bmad-guide | v6.12.4 | <a :href="`${theme.releasesUrl}tag/bmad-guide-v6.12.4`" target="_blank" rel="noreferrer">Release bmad-guide-v6.12.4</a> |

- CT v5.12.2 公開版與錄製時用的檔案只差在去識別的字句，功能與規則相同。
- BMad-Method 本身不用另外下載：程式碼 repo 已在根目錄自裝一份 v6.12.4（`_bmad/`），clone 後照 repo README 的〈安裝 BMad〉還原 skill 副本即可。
- 新學員也可以直接用最新版，安裝與升級見[安裝](/install)。新版與錄製時的差異見[更版紀錄](/versions/releases)。

## 影片與公開 repo 的對照 {#video-vs-repo}

影片是在講師的**課程製作 repo** 裡錄的：示範專案放在 `courses/ct-bat-bmad-go-sms/sms-platform/`，旁邊還有投影片原始檔、逐字稿與製作工具。學員拿到的是程式碼 repo（＝影片裡的 `sms-platform/`）＋投影片 PDF＋影片。影片裡的說法這樣對照：

- 影片說「**課程 repo**」時，指的是講師的製作 repo；學員手上對應的是 clone 下來的程式碼 repo。
- 影片與投影片裡的路徑 `courses/ct-bat-bmad-go-sms/sms-platform/…`，一律**去掉這段前綴**，對應程式碼 repo 的根。
- 影片提到的單元 `assets/` 範本、逐字稿、回答腳本與 `docs/setup/` 安裝文件不在公開 repo；需要的內容都在影片與投影片 PDF 裡看得到。

| 單元 | 影片的說法 | 對照 |
|---|---|---|
| 1-00 | 課程 repo 裡每個目錄放什麼；整門課放在 `courses/ct-bat-bmad-go-sms/` | 那是講師的製作 repo。學員拿到的是程式碼 repo（＝影片裡的 `sms-platform/`）、投影片 PDF 與影片 |
| 1-04 | BAT 新增工作區，指到課程 repo；工作目錄是課程 repo 的根，路徑都從 `sms-platform` 開始；安裝步驟寫在 `docs/setup/windows-wsl` | 工作區指到 clone 下來的程式碼 repo；路徑去掉 `sms-platform/` 前綴。環境需求與指令見程式碼 repo README 的〈快速開始〉，CT 的安裝見[安裝](/install) |
| 1-06 | 參考解放在課程 repo 的 tag `dojo-ch1`，找不到就 `git fetch --tags` | tag 在程式碼 repo；`git fetch --tags` 照常可用 |
| 2-00 | 課程 repo 根目錄原本那份 BMad 安裝只給課程製作用 | 公開 repo 沒有那份安裝，可以忽略 |
| 2-10 | 課程 repo 用 tag `ch2-start` 標記起點；PRD 等文件跑到課程 repo 根目錄的 `_bmad-output/` 是落點錯誤 | tag 在程式碼 repo。程式碼 repo 的根就是 sms-platform，所以**產物落在根目錄的 `_bmad-output/` 是正確的**，和影片裡的卡點說法相反 |
| 3-01、3-02 | 範本放在課程 repo 這個單元的 `assets/` 底下；課程 repo 自己也有一套工單系統，剛好有同號的工單 | 範本內容在影片與投影片 PDF 裡；課程製作 repo 的工單系統學員看不到，可以忽略 |
| 4-08 | 容器掛課程 repo 根，工作目錄在 sms-platform | 掛自己 clone 的程式碼 repo 根，工作目錄就是根 |
| 4-09 | 主機的課程 repo 根掛到容器的 `/workspace/<製作 repo 名>`，`--cwd` 要寫到 `…/courses/ct-bat-bmad-go-sms/sms-platform`；課程 repo 裡有一個子模組指標記的是 Windows 絕對路徑 | 容器路徑是 `/workspace/<你的 repo 目錄名>`（clone 成預設名稱時是 `/workspace/ct-bat-bmad-go-sms`，`docker compose` 不用改設定；改了資料夾名就設 `SMS_REPO_NAME`），`--cwd` 就是這個路徑。子模組的問題只存在講師的製作 repo。細節見程式碼 repo README 的〈dev container〉 |
| 4-10 | 可以從課程 repo 的 tag `ch4-start` 起步，tag 會在課程發布前補齊 | tag 已在程式碼 repo |
| 6-05 | 本機離開課程 repo 就會載到 V7 | 意思是「離開裝了 BMad-Method v6.12.4 的專案目錄」；在程式碼 repo 裡啟動 Claude Code 即可 |

## 延伸閱讀

- 課程規劃（`COURSE-PLAN.md`）§ 1 課程定位、§ 3 課程總表、§ 6.1 錄製時版本

Portal 是摘要，不具權威；課程內容以課程本身為準。
