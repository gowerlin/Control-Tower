# 治理護欄的設計理由

v5.0.3 ~ v5.0.9 的變更，多半不是新功能，而是**從真實失誤裡長出來的護欄**。
本檔只講每道護欄「為什麼長這樣」——它防的是哪一種失效、為什麼別的寫法不行。
確切的正則、旗標、路徑與檢查步驟不在這裡，需要時看 `ct-help` 或文中指名的 CT reference。

| 護欄 | 防的失效 | CT 權威定義 |
|------|---------|------------|
| Landing Zone Check | Worker 在錯的 repo 執行一張正確的工單 | `ct-exec/SKILL.md` § Landing Zone Check |
| 摘要授權規則 | 照著「看起來完整」的摘要指令派工 | `control-tower/SKILL.md` § BAT And Auto-Session |
| 單一權威定義 | 各處各自自洽、合起來牴觸 | `work-order-system.md` § 工單 ID 格式 等 |
| Layer 1 寫入機制 | 備份「放旁邊」被註冊成現役 skill | `data-layer-architecture.md` § 寫入規則 |
| 版本治理 | 版號散落、安裝後無從驗證 | `version-governance.md` |
| 合併護欄（v5.3.0） | 隔離工單的成果以未經驗證或無從追溯的形式進入 `main` | `merge-workorder.md` § 共同護欄 |
| 棄用條款寫法 | 新規則壓不過 AI 記憶裡的舊慣例 | `skill-writing-conventions.md` |

---

## Landing Zone Check：身分不能用路徑證明

### 它要回答的問題

Worker 開工前要確認的是一個**身分**問題：「我現在所在的 repo，是這張工單寫給的那個 repo 嗎？」
派工端傳錯 `cwd`、使用者在錯的終端分頁輸入指令、兩個專案剛好都有 `T0047`——
工單 ID 跨專案會撞號，所以光看 ID 什麼也分辨不出來。落點檢查不假設派工端傳的參數一定正確，它是寫入前的最後一道防線。

它在工單流程中的位置見 `work-order-lifecycle.md` § Landing Zone Check。
這份檢查只在 `ct-exec` 定義一次，`ct-done` 與 `ct-status` 都引用同一份、不另寫——寫入型的兩者不符即 STOP，唯讀的 `ct-status` 只把結果和狀態一起報告。
三個 skill 共用一份定義，是下文「單一權威定義」的直接應用：若各自複述，遲早會出現三個略有不同的落點檢查。

### 為什麼不能靠「檔案在不在」判斷

最直覺的作法是看工單 `affects_files` 列的路徑在不在當前 repo 裡。問題是：

> 「正確的 repo，但工單要從零建立整棵目錄」與「完全錯的 repo」，
> 在純路徑測試下**結構上無法區分**——兩者都是「那些路徑不存在」。

所以不論怎麼調門檻（看幾層、看比例），路徑存在與否都**答不了身分問題**。
身分需要一個外部訊號：v5.0.5 起，塔台在工單 frontmatter 寫入 `repo`（repo 根目錄的目錄名），
Worker 直接比對 `repo` 與實際 repo 根目錄名——這就是 **C-0 repo identity**，落點檢查中唯一的**承重檢查**，不符即 STOP。

### C-3 為什麼從承重降為輔助：實測，不是猜測

路徑檢查（C-3）原本是承重檢查。v5.0.5 之前，塔台拿另一個 repo 的 **34 張真實工單、65 個 `affects_files` 項目**，
模擬「Worker 誤落到 BMad-Guide repo」重放了一次：

| C-3 判定法 | 擋下的錯誤落點 |
|-----------|--------------|
| 只看直接父目錄（最初規格） | **34／34 — 100%** |
| 上溯到最近的既存祖先目錄（v5.0.4 實際出貨） | **14／34 — 41%** |

失效機制：`docs/api/*.md` 會一路上溯到 `docs/`——兩個 repo 恰好都有這個頂層目錄名；
而 STOP 條件是「**所有**可測項目都不存在」，只要一個項目的名字夠通用，整張工單的 C-3 就失效。

那為什麼不退回「只看直接父目錄」？因為「建立一個新版本目錄並在裡面工作」這種很普通的工單，
在**正確**的 repo 裡所有項目與直接父目錄也都不存在，會被誤判成錯 repo。
**會亂叫的警報終究會被忽略**，它的代價比它換來的保護更久。所以 CT 保留祖先上溯（低誤報）、
另外加上 C-0 承擔身分判斷——C-3 不再需要高偵測率，只在 C-0 無法使用時（舊工單、其他塔台寫的工單沒有 `repo` 欄位）才恢復 STOP 的權力。

### `expect_missing` 是逃生閥，不是靜音開關

工單 frontmatter 可宣告 `landing_check.expect_missing: true`，意思是「本工單自己會建立 `affects_files` 指向的目錄樹，開工時找不到是預期的」。
它只把 C-3 的「全部不存在」從 STOP 降為警告，**C-0 不受影響**。

- **只有塔台能設**，而且只在工單真的會建立自己的目標樹時才設
- **Worker 絕不能為了讓檢查通過而加上它**——遇到落點 STOP，正確反應是回報塔台，而不是改工單直到它不再叫
- 它不涵蓋「檔案應該存在但我找不到」；那正是 C-3 要抓的訊號

同理，C-0 不符時 Worker 也不得修改工單的 `repo` 欄位。所有「改工單讓護欄閉嘴」的動作，本質都是拆掉護欄。

### C-4 workspace 一致性：為何刻意不做

曾有提案：比對 BAT 的 `BAT_WORKSPACE_ID` 與「這個專案平常用的 workspace」。評估後**明確不做**：

1. 根本沒有「平常用的 workspace」這個欄位，得新增設定項
2. **workspace ID 不穩定**：同一個 BMad-Guide repo 的 workspace ID 在兩次快照中就不同了；把 ID 釘進設定只會帶來持續的假警報

替代作法是只把觀察到的 `BAT_WORKSPACE_ID` **記錄**進回報區作為鑑識證據，從不比對、從不阻斷。
這個「不做」被寫進 CT 本體，就是為了不讓同一個提案再被提一次。

### 在 worktree 裡：換比對對象，不換語意（v5.3.0）

隔離派工的 Worker 在 BAT 建的 worktree 裡執行，而 worktree 的根目錄名是工單編號 `T####`，不是 repo 名。
若照舊比對 `basename(repo 根目錄)`，每一張隔離工單都會在 C-0 誤判 `WRONG_REPO_CONFIRMED`。
所以環境有 `CT_HOME`（主 checkout 路徑）時，C-0 改比 `CT_HOME` 的目錄名；C-1 改確認工單在 `CT_HOME` 底下；C-3 照常對 worktree 檢查。
**C-0 的承重地位與 STOP 語意不變**——改的只是「身分要拿什麼來比」，身分問題本身沒變。
`CT_HOME` 不存在時，落點檢查與 v5.2.6 完全相同。

> 檢查順序、各檢查的權重與 STOP 條件，以 `ct-exec/SKILL.md` § Landing Zone Check 為唯一定義；worktree 中的比對對象見同檔 § Worktree Isolation。

---

## 摘要授權規則：「看起來完整」本身就是失效模式

v5 的 SKILL.md 是路由器（見 `ecosystem.md` § SKILL.md 是路由器），裡面的指令範例是**為了路由而寫的有損摘要**。
規則是：**SKILL.md 的指令範例絕不能是派工指令的唯一來源**；要執行就載入它旁邊指名的 reference，照那裡的指令表逐字使用。

這條規則來自一次真實失誤：塔台 SKILL.md 的派工指令行讀起來像完整的旗標清單，實際上靜默漏了 `--workspace` 與 `--notify-id`，
塔台就照著它逐字派工。

值得記住的是 CT 對這次失誤的診斷：

> 補上漏掉的那個旗標，只會把失誤移到下一個旗標。
> 缺陷不在某個特定旗標，而在於摘要**看起來是完整的**。

所以修法不是「把摘要補齊」——任何摘要都會再次過時——而是**改變摘要的地位**：在它旁邊標明「非權威」，
並規定 reference 才是那個動作的事實來源。這也解釋了為什麼 CT 不禁止 SKILL.md 寫指令範例：範例對路由有用，問題只在把它當權威。

---

## 單一權威定義＋交叉引用

### 失效：各處各自自洽，合起來牴觸

v5.0.6 之前，CT 內部對「工單 ID 可不可以帶前綴」有五處敘述、兩種相反立場：
一處說只能是 `T` 加數字，另一處說跨專案強制帶前綴。**每一處單獨讀都說得通，放在一起就互相矛盾。**

這個矛盾有實際代價：BMad-Guide repo 沒設 `project-prefix`，熱區卻有多張 `CP-T####` 跨塔台工單；
派發其中一張時，下游驗證器只認無前綴 ID，派工被擋，塔台被迫繞道。

### 修法：定義一次，其他處只引用

CT 的結論是「逐處改寫只會讓下次再度發散——**收斂成一處定義才是修法**」：

- 規則只在一個地方完整定義，並標明「本節是唯一事實來源」
- 其他地方只寫交叉引用，**不複述判斷條件**
- 需要把規則組合進更大的規則時，用具名片段指稱它，而不是就地展開成字面值

最後一條也有實例：YOLO 斷點 A 比對 Worker 回報字串的正則曾經就地寫死無前綴形式，
帶前綴的 `CP-T0113 完成` 因此被誤判成非預期回報。**展開就是複製一份定義，下次改動必然漏改一處。**

v5.0.6 把工單 ID 格式收斂到 `work-order-system.md`；v5.0.7 以同樣作法收斂 `~/.claude/skills/` 寫入規則，把 6 處複述改為交叉引用；v5.0.9 再把 `~/.codex/skills/` 納入同一權威定義；v5.14.0 把 plugin 安裝路徑也收進同一份定義。
本教材自己也照這個原則寫：同一主題只在一個檔案展開，其他檔案只引用。

---

## Layer 1 寫入機制：為什麼「放旁邊」也危險

規則本身（範圍是整個 `~/.claude/skills/` 與整個 `~/.codex/skills/`，v5.14.0 起再加上 plugin 安裝路徑；唯一例外的三個條件、備份落點）已在 `three-layer-arch.md` § Layer 1 寫入規則說明。
這裡補的是規則背後的**實證與推理**。

### 實證（D006）

一次 bmad-guide 升級前，備份被放在 `~/.claude/skills/_backup-bmad-guide-v6.10.0-<時間戳>/`。
該目錄根層有 `SKILL.md`，隨即被註冊為現役 skill、出現在可用 skill 清單中，description 還是舊版那份。
舊 description 與新版高度重疊，路由時可能命中舊版，答出已被新版推翻的內容——沒有任何錯誤訊息。
這是 Claude Code 端的實證；Codex 端未實測。

### 「上次這樣做沒事」不構成反證

同期另一次升級也把備份放在 `skills/` 底下，卻沒出事。原因是那次備份的是 8 個 skill 的**父目錄**，
根層沒有 `SKILL.md`，而掃描器只看第一層，於是略過——**那是結構僥倖，不是規則有效**。換成備份單一 skill，必然踩到。

這是護欄設計中常見的陷阱：一次沒出事的經驗，很容易被當成「這樣做是安全的」證據。
CT 的寫法是把**機制**寫出來（掃描器註冊第一層子目錄），讓讀者自己推得出「下一次會不會出事」，而不是只給一句「禁止」。

也因此，「以底線或點開頭命名，掃描器應該會略過吧」同樣不被接受：**掃描器的行為不是規則的前提，路徑位置才是。**

### 安裝流程（zip 手動安裝）

取得工單明文授權後，安裝依序是：

```
備份現行安裝品到權威定義指定的備份落點（Claude 端 ~/.claude/skill-backups/、Codex 端 ~/.codex/skill-backups/；時間戳取自系統）
  → 逐檔複驗備份與現行安裝品相同；任一 skill 備份失敗或不同就停止，不進覆寫（v5.3.0）
  → 只覆寫授權指名的 skill 與目標路徑
  → 逐檔 diff 或 SHA256 複驗，要求全部 IDENTICAL
  → 回報：備份路徑、逐 skill 複驗結果、具體回退指令、生效時機
```

備份要先複驗再覆寫，是因為回退依賴這份備份——備份不完整就替換，失敗時無法復原。
任一檔不一致即視為安裝失敗、回退並回報，不得宣稱完成。生效時機要寫明，是因為覆寫當前 session 正在用的 skill，
變更要到**下一個 session** 才生效——不寫的話，使用者會在同一個 session 裡驗證，然後誤以為安裝沒成功。

> 完整步驟與指令見 `version-governance.md` § 安裝／升級流程；可否寫入以 `data-layer-architecture.md` § 寫入規則為準。

### plugin marketplace：另一種安裝方式（v5.14.0）

**是什麼。** marketplace 是一個 git repo，裡面有一份目錄檔，列出可以安裝的 plugin。Claude Code 與 Codex 都能「訂閱」一個 marketplace
（`plugin marketplace add`），之後用 `<plugin>@<marketplace>` 安裝其中的 plugin。CT 的 marketplace 叫 `control-tower`，放在發行 repo
`gowerlin/Control-Tower` 的根目錄，裡面有兩個 plugin：

| plugin | 內容 | 為什麼這樣分 |
|---|---|---|
| `ct` | CT 的 8 個 skill | 8 個 skill 之間用 `../` 相對連結互相引用，必須是兄弟目錄，所以放同一個 plugin，不拆開 |
| `ct-guide` | 本教材 | 和獨立 zip 一樣可裝可不裝 |

beta 版不上架，照舊用 zip。安裝寫法是 `ct@control-tower`。

**和 zip 的關係。** 內容相同，來源是同一個版本目錄；差別在誰用、怎麼更新。

| | zip | plugin marketplace |
|---|---|---|
| 給誰 | 所有 agent：Claude Code、Codex、claude.ai（上傳單一 skill zip），以及任何讀 skill 目錄的工具 | Claude Code 與 Codex |
| 更新 | 每次自己下載、照安裝流程備份、替換、逐檔複驗 | 訂閱後用 plugin 指令更新，或開自動更新 |
| 發行 | 仍是 Release 的附件 | 不是附件；隨發行 repo 一起更新 |

zip 沒有被取代：它是唯一能給每一種 agent 的格式。marketplace 只是讓 Claude 與 Codex 使用者不必每次手動換檔。

**手動與 plugin 並存時誰生效。** CT 實機驗證過兩種 agent：

| 情況 | Claude Code | Codex |
|---|---|---|
| 只裝 plugin | `/ct-exec` 叫得到；`/ct:ct-exec` 也行 | 只有 `$ct:ct-exec` 叫得到；`$ct-exec` **不會**載入 plugin 的 skill |
| 手動與 plugin 都裝 | `/ct-exec` 用**手動那份**；`/ct:ct-exec` 才是 plugin 版 | `$ct-exec` 用**手動那份**；`$ct:ct-exec` 是 plugin 版 |

危險的是第二列：沒有錯誤訊息、看起來一樣，舊的手動安裝卻一直在生效，plugin 更新了也沒用。
所以從 zip 改用 plugin 的第一步是**先備份、再把手動安裝移出 `skills/`**，然後才裝 plugin，開新 session 用完整寫法確認。
claude.ai 同步下來的 `anthropic-skills:*` 副本不在本機 `skills/`，不受這一步影響，會繼續並存。

**Codex 搭配 BAT：繼續用 zip。** BAT 對 Codex 派工送的是 `$ct-exec`，只裝 plugin 的 Codex 收到後叫不到 CT。
CT 沒有請 BAT 改，而是寫明這個組合用 zip 手動安裝（理由見 `bat-integration.md` § 誰負責 `/` 還是 `$`）。

**自動更新（auto-update）。**

- Claude Code：第三方 marketplace 的自動更新**預設關閉**，要在 `/plugin` → Marketplaces 對 `control-tower` 打開；不開就手動跑更新指令。
  Claude 用 `plugin.json` 的 `version` 判斷有沒有新版——`version` 沒變就不會更新，所以 CT 每次發版都要讓它等於新版號
- Codex：每次啟動都會自動升級已訂閱的 git marketplace（看 commit，不看 `version`）
- 兩邊都一樣：更新的 skill 在**下一個 session** 生效

**還是 Layer 1。** plugin 目錄同樣不准塔台或 Worker 寫入（`three-layer-arch.md` § plugin 安裝路徑也是 Layer 1）。
要讓 Worker 代為安裝，工單要明文授權並指名 agent、plugin 與 marketplace，而且只能用 plugin 指令；plugin 不備份，回退是移除 plugin、改回 zip。

> 指令、步驟與條件以 CT `version-governance.md` § 安裝／升級流程 › plugin 安裝／升級為準；呼叫寫法以 `auto-session.md` § 依安裝方式的 skill 呼叫字串為準；
> 可否寫入以 `data-layer-architecture.md` § 寫入規則為準。本節只講為什麼。

---

## 版本治理

### 版號為什麼搬到 body 註解

Codex 的 skill 驗證把 frontmatter 裡的未知欄位視為錯誤，所以 frontmatter 只能放 `name` 與 `description`。
版號的事實來源因此改為 body 第一個註解 `<!-- control-tower-version: X.Y.Z -->`，H1 標題、塔台面板與 `_tower-state.md` 是同步點；
需要讀版本時先讀註解、再以標題為 fallback，**不得要求 frontmatter 有 `version:`**。

這是「單一權威定義」在版號上的應用：一個事實來源，其他位置是它的鏡像。

### 版本目錄是安裝與複驗的基準

發行樹不再附 CHANGELOG，版本史記在 `version-governance.md` 的歷史版號表。
安裝流程的逐檔複驗，比對的是「版本目錄裡的 skill」與「安裝後的 skill」——
版本目錄就是那個版本的參照基準，安裝品要跟它逐位元組一致。

版號採 SemVer：不相容的工作流程或 metadata schema 變更升 MAJOR，新命令／設定升 MINOR，文件補完與規則修正升 PATCH。
**commit、tag、同步已安裝 skill 的時機由使用者或正式 release 流程決定**，塔台與 Worker 不主動 push。

升級時另有一條相容性提醒：Worker skill 的版本可以獨立於塔台，但新版塔台派工給舊版 Worker 時，
應以明確的 `PARTIAL`／`BLOCKED` 或升級提示回報，**不得宣稱 YOLO 自動回報已生效**（見 `runtime-dispatch.md`）。

---

## 合併護欄：推進 `main` 的每一步都要能對帳（v5.3.0）

隔離工單的成果在分支 `ct/T####` 上，合併回 `main` 是整條隔離流程唯一會動到共用主線的一步。
合併的模式與流程見 `work-order-lifecycle.md` § worktree 隔離與合併工單；這裡講三種模式共用的護欄各自防什麼。

| 護欄 | 防的失效 | 為什麼這樣定 |
|------|---------|-------------|
| 只在**整合 worktree** 合併 | 合併過程碰到使用者在主 checkout 的未提交變更，或改動被合併工單的 worktree | 主 checkout 是使用者與塔台記帳的地方；被合併工單的 worktree 是驗收證據（`validated_sha`）所在，不該被合併過程改寫。整合 worktree 長期保留，免得每次合併都重裝依賴 |
| 一律 `--no-ff` | 合併後歷史上看不出「哪張工單帶進了什麼」 | merge commit 的訊息帶工單 ID，第二個 parent 就是 Worker 驗收過的 SHA——收單 SHA 比對才有東西可比 |
| `main` 只用 `--ff-only` | `main` 上出現一個沒有在整合 worktree 做過、比對過的合併結果 | ff 只能把 `main` 移到已存在的 commit；合併期間 `main` 又前進了，ff 會被 git 拒絕，而不是悄悄再合一次 |
| 即使 `behind == 0` 也走整合 worktree（D031） | 同一件事有兩種做法，證據形狀不一 | 只留一條路徑：每次合併都有 merge commit 與兩個 parent 可比對，不因情況剛好簡單就少一份證據 |
| 不 push、不 `--force`、不 `reset --hard`、不 rebase `main` | 改寫已存在的歷史，讓先前記下的 SHA 失效 | SHA 比對的前提是 SHA 不會變；push 的時機沿用各專案授權，不由合併流程決定 |
| 重疊的髒檔擋住 `--ff-only` 時不 stash、不丟棄 | 為了讓合併完成而動到使用者的變更 | git 拒絕是正常保護；使用者的變更是他自己的判斷，塔台沒有資格替他取捨，告訴他哪些檔擋住了，由他處理 |

判準與資料來源也照同一個方向設計：**取不到資料就算不通過**（`null` 不等於空陣列），寧可派合併工單多跑一次驗收，也不在資料缺漏時直接推進 `main`。
最後一道人工確認是斷點 E：它是唯一在非 yolo 模式下也固定**暫停**的斷點（v5.5.0 的斷點 D 在非 yolo 下也生效，但只告知、不暫停），因為「推進 `main`」的回頭成本比任何一張工單都高（見 `runtime-dispatch.md` § YOLO 與斷點）。

> 共同護欄、直接合併判準與收單 SHA 比對以 CT 的 `merge-workorder.md` 為唯一權威定義；斷點 E 以 `yolo-mode.md` § 斷點 E 為準。

---

## 棄用條款：為什麼要寫明「棄用什麼、理由」

工單的 `memory_overrides`（見 `work-order-lifecycle.md` § frontmatter 欄位地圖）不只寫「本工單禁止 X」，
而是寫「AI 記憶中有 X 這個舊作法 → 本工單不採用 → 理由」。原因在 LLM 的訊號強度：

| 寫法 | 效果 |
|------|------|
| 單點禁令「嚴禁 X」 | 權重低，容易被記憶中累積多次的「曾經 X」蓋過 |
| 對比式棄用條款「舊版允許 X，新版棄用 X，改用 Y」 | 權重高，AI 看到的是**規則演進**，而不是一條沒有脈絡的禁令 |

這不是多寫字，而是在不改變語意的前提下提高訊號強度。CT 用同一個格式寫 skill 本身的規則，
再由工單的 `memory_overrides` 在派工時重申一次——skill 與工單**雙重明示**。

何時**不**該用：首次建立的規則（沒有歷史可對比，硬寫棄用條款等於製造虛假歷史）、極低頻的非核心規則、純新功能的規範。
升級判準：同一條規則在兩次以上工單被違反，就該改寫成棄用條款格式。

> 範本與實例見 `skill-writing-conventions.md` § 棄用條款寫法規範。

---

## 這些護欄的共同點

| 護欄 | 共同的設計選擇 |
|------|--------------|
| Landing Zone Check | 用外部訊號（`repo` 欄位）回答身分問題，不用代理指標（路徑） |
| 摘要授權規則 | 不追求「摘要永遠正確」，而是明定摘要不具權威 |
| 單一權威定義 | 不追求「每處都改對」，而是讓規則只存在一處 |
| Layer 1 寫入機制 | 不只給禁令，而是寫出機制，讓「上次沒事」無法成為反證 |
| C-4 不做 | 不加一道會亂叫的警報；只記錄，不阻斷 |
| 合併護欄 | 不追求「這次合併看起來沒問題」，而是讓每次推進 `main` 都有可比對的 SHA 證據；資料缺漏就不推進 |

共同點是：**每道護欄都先問「這種失效會以什麼形式再次發生」**，再選一個讓它無法以同樣形式再發生的結構，
而不是修補眼前那一個實例。
