# 微應用 / Mono-repo 模式

## 單一塔台管多子專案

啟動時告知結構：

```
/control-tower
我的專案是 mono-repo：
- app-a/：[功能簡述]，有獨立 .git
- app-b/：[功能簡述]，有獨立 .git
- shared/：[共用模組]
```

塔台額外職責：

1. **工單標記子專案**：元資料中標注「目標子專案：app-a」
2. **跨專案影響偵測**：改 shared/ 時提醒兩邊測試
3. **文件歸屬建議**：共用文件放 parent/docs/，子專案特有的放各自目錄

## 目錄結構建議

```
parent-dir/
├── AGENTS.md                ← 專案上下文（BMad v6.11+：bmad-project-context 寫的區塊）
├── _ct-workorders/          ← 工單統一管理
├── docs/                    ← BMad 共用文件
│   ├── prd.md
│   └── sprint-status.yaml
├── app-a/
│   ├── .git/
│   └── docs/                ← app-a 專屬文件
└── app-b/
    ├── .git/
    └── docs/                ← app-b 專屬文件
```

> BMad v6.11+ 不再產出 `project-context.md`，專案上下文改寫在 repo 根目錄 `AGENTS.md` 的區塊；子專案（含巢狀 repo）可以有自己的
> `AGENTS.md`（條件見下述 reference），由上層列指標。舊專案留下的 `project-context.md` 不會自動載入。以已安裝 `bmad-guide` 的 `references/brownfield.md` 為準（v5.14.1+）。

> 子專案各有自己的 `.git`（巢狀的獨立 repo）時，上層要不要是 git repo、`repo` 填什麼、Worker 在哪裡執行、子 repo 怎麼 commit，
> 見下方 § 巢狀的獨立 repo（v5.14.3+）。

## 巢狀的獨立 repo（一個塔台、多個共用 repo）

> **本節是這個配置的唯一權威定義**（v5.14.3+）。判斷表（[multi-tower-protocol.md](multi-tower-protocol.md) § 決策：一個塔台還是多個）、
> 工單模板（[work-order-template.md](work-order-template.md)）與安裝指南都只引用本節，不複述。
> 這是**寫法與配置**，不是新規則：CT 的落點檢查、commit 規則、派工命令都沒有改，CT 5.14.2 起就能這樣用（實機結果見本節最後）。

### 適用情況

上層目錄底下有兩個以上**各自獨立的 git repo**（各有自己的 `.git` 與 remote，通常是跟團隊共用、隊友不一定用 CT 的 repo），
而你想用**一個塔台**管全部的工單，也不想把執行紀錄寫進團隊共用的 repo。

子專案都在**同一個** git repo 裡的一般 mono-repo，用本檔前面幾節就好，不需要本節的 `git -C`。

### 為什麼工單會跑進子 repo

沒有照本節設定時，常見的結果是工單被寫進各子 repo 自己的 `_ct-workorders/`，BAT 面板只讀 workspace 那一層，看不到，編號也各自從頭算。
原因**不是**落點檢查 C-0／C-1 要求工單放在子 repo，而是三條規則合在一起：

1. Worker 在**自己 cwd 底下**的 `_ct-workorders/` 找工單（`ct-exec/SKILL.md` § Startup）。
2. `repo` 是「這張工單在哪個 git repo 執行」，值是 Worker cwd 的 git toplevel 目錄名（[work-order-template.md](work-order-template.md) § `repo`）。
3. 塔台派工的 `--cwd` 是塔台自己的專案根目錄（[auto-session.md](auto-session.md) § 執行方式）。

所以讓 Worker 在子 repo 執行，工單就只能放在子 repo。反過來，讓 **Worker 在上層執行**，C-0、C-1 一樣會過，這就是本節的配置。

### 目錄

```
project-a/                 ← 個人的塔台 git repo（不推，或推到個人 remote）；BAT workspace 指向這裡
├── .git/
├── .gitignore             ← 列出 src/app-frontend/、src/app-backend/（子 repo 不進上層版控）
├── _ct-workorders/        ← 全部工單、塔台狀態、決策日誌、BUG（只有這一份）
└── src/
    ├── app-frontend/      ← 獨立 repo（團隊共用），沒有 _ct-workorders/
    │   └── .git/
    └── app-backend/       ← 獨立 repo（團隊共用），沒有 _ct-workorders/
        └── .git/
```

### 設定上層

1. 上層 `git init`。🔴 **上層一定要是 git repo**：不是的話，ct-exec 落點檢查的 C-0、C-1、C-3 全部跳過、只記 WARN，等於沒有落點保護。
2. 上層 `.gitignore` 逐一列出子 repo 目錄（例：`src/app-frontend/`、`src/app-backend/`），子 repo 的檔案不進上層版控。
   設定後在上層跑 `git status`，應該看不到子 repo 的任何檔案。
3. BAT workspace 指向上層。
4. 上層的 remote：不設，或推到個人的 remote（見下一小節）。

### 執行紀錄放哪裡（建議，不是規則）

隊友不用 CT 時，塔台狀態、決策日誌、Worker 回報（可能含本機路徑與個人判斷）是個人的工作紀錄，CT 建議**不要預設推到團隊共用的 remote**。
要不要共用由團隊決定；本節的配置讓它們留在上層的個人塔台 repo，子 repo 只收到產品 commit。

不建議改用「工單留在子 repo，再用子 repo 的 `.gitignore` 或 `.git/info/exclude` 藏起 `_ct-workorders/`」：
Worker 照 commit 規則 commit 工單時會失敗，worktree 隔離也讀不到工單。

### 工單 frontmatter

| 欄位 | 填什麼 | 例 |
|---|---|---|
| `repo` | **上層**的目錄名（在上層跑 `basename "$(git rev-parse --show-toplevel)"`） | `project-a` |
| `project` | 要改的子 repo（給人看，不參與落點檢查） | `app-frontend` |
| `affects_files` | **從上層寫起**，包含子 repo 的目錄 | `src/app-frontend/src/login.ts` |
| `isolation` | 不寫（這種工單不能隔離，見〈限制〉第 1 點） | — |

一張工單同時改兩個子 repo 也可以：`project` 寫主要的那個（或兩個都寫在標題），`affects_files` 照樣從上層列。

工單之間的關聯：同一個塔台底下用 `depends_on`／`related`。`parent_workorder` **不是 CT 欄位**，CT 不讀它；跨塔台用
[cross-project-coordination.md](cross-project-coordination.md) 的 COORDINATED／DELEGATE。

### 工單步驟寫法

ct-exec 照工單明列的步驟執行，它本身不知道「產品檔在另一個 repo」，所以下面這些要**寫進工單步驟**：

1. **前置條件**：先讀子 repo 的 `AGENTS.md`／`CLAUDE.md`。Worker 的 cwd 在上層，runtime 不會自動載入子 repo 的這些檔。
2. **確認子 repo 身分**（建議）：`git -C src/app-frontend rev-parse --show-toplevel` 要指向該子 repo；需要時再看 `remote -v` 與目前分支。
   落點檢查不會替你做這一步（〈限制〉第 2 點）。
3. **產品 commit 在子 repo，用 `git -C`，路徑去掉子 repo 前綴**：

   ```bash
   # affects_files：src/app-frontend/src/login.ts → 在子 repo 裡是 src/login.ts
   git -C src/app-frontend add -- src/login.ts          # 新檔才需要
   git -C src/app-frontend commit --only src/login.ts -m "T0012: <說明>"
   ```

   改到兩個子 repo 就各自 commit。跨 repo 的 commit 做不到原子，照 ct-exec 的反序收尾：
   各子 repo 的產品 commit → 回報區記 SHA → 最後才 commit 工單。
4. **回報區**：每個子 repo 各記一筆（子 repo 路徑、分支、commit SHA）。
5. **工單本身在上層 commit**：`git commit --only _ct-workorders/T0012-<描述>.md`。
6. **push**：子 repo 照一般規則，工單沒寫使用者授權就不 push。

ct-exec § Commit rules 的「`git commit --only` 或精準 staging」在每個 repo 各自成立，不需要另訂規則。

### 派工與面板

- **派工照舊**：`--cwd` 是上層（塔台的專案根）。面板一鍵派工的 cwd 是 BAT workspace 根，也就是上層，兩者一致。
- 面板讀 workspace 根的 `_ct-workorders/`，全部工單都看得到，編號連續。
- **新目錄第一次派工**：Claude Code 會先跳出「要不要信任這個資料夾」的確認，Worker 還沒開始，`--wait-started` 因此可能回 exit `8`。
  這不是派發失敗：請使用者在 Worker 分頁回答信任，之後就會正常開始；塔台不重派、不代按（[auto-session.md](auto-session.md) § Worker 啟動確認）。
  事先在上層開過一次 Claude Code 並回答信任，就不會遇到。

### 限制

1. **不能 `isolation: worktree`**：BAT 以 `--cwd` 的 git toplevel（上層）建 worktree，而子 repo 被上層 `.gitignore` 排除，worktree 裡沒有子 repo。
   要隔離地改子 repo，在子 repo 用它自己的分支（工單步驟寫明 `git -C <子 repo> switch -c …`），或改用方案 2。
2. **C-0 只驗上層**：`repo` 證明 Worker 站在塔台 repo，不證明子 repo 是對的 clone。C-3 看的是檔案系統，子 repo 的路徑會判為存在，
   但看不出檔案屬於哪個 repo。目前靠工單步驟第 2 點自行確認；ct-exec 沒有對應的檢查項。
3. **`affects_files` 與 `git -C` 的路徑基準不同**：`affects_files` 從上層寫，`git -C` 要去掉子 repo 前綴。檔案多或路徑深時容易出錯，
   工單可以在步驟裡直接列出每個子 repo 要 commit 的路徑。
4. **子 repo 的 `AGENTS.md`／`CLAUDE.md` 不會自動載入**：靠工單步驟第 1 點。
5. **還沒有宣告子 repo 根目錄的欄位**：frontmatter 選填欄位與對應的落點檢查之後另議；在那之前，子 repo 路徑寫在工單步驟裡。

### 何時改用方案 2（每個 repo 一個塔台）

本節的配置稱為方案 1。方案 2 是每個 repo 各開一個 BAT workspace＋一個塔台，跨 repo 的需求走
[cross-project-coordination.md](cross-project-coordination.md) 的 COORDINATED／DELEGATE，用 `project-prefix` 區分編號。

| 情況 | 建議 |
|---|---|
| 隊友不用 CT、不想把執行紀錄放進共用 repo | 方案 1（本節） |
| 經常一次改好幾個 repo | 方案 1 |
| 隊友也用 CT，執行紀錄本來就要進各個 repo | 方案 2 |
| 需要 worktree 隔離改子 repo | 方案 2 |
| 各 repo 很少同時改、各自有節奏 | 方案 2 |

方案 2 的代價：執行紀錄進各個共用 repo；多個塔台要切換；跨 repo 的需求要走統籌單和受派單，多一層手續。

### 已經寫在子 repo 的舊工單

兩種做法都可以，CT 不替使用者決定：

- **搬到上層**：移到上層 `_ct-workorders/`，編號不變；兩個子 repo 有同號工單時，先決定怎麼區分（改前綴或重新編號），對照寫進決策日誌。
  搬完後在子 repo 刪除並 commit（這是共用 repo 的 commit，照該 repo 的規矩）。
- **留在原處當歷史**：不再新增，新工單一律開在上層。

不建議兩邊同時繼續開新工單：面板只看得到上層，編號也會分岔。

### 實機驗證（CT 5.14.2、BAT 0.7.2-pre.1）

在拋棄式目錄照本節配置（上層 `git init`＋兩個沒有 remote 的子 repo，上層 `.gitignore` 排除兩者），塔台用 BAT 派 Worker 在上層執行一張同時改兩個子 repo 的工單：

| 項目 | 結果 |
|---|---|
| C-0 | ✅ PASS（`repo` = 上層目錄名 = Worker 的 git toplevel） |
| C-1 | ✅ PASS（工單在上層 `_ct-workorders/`） |
| C-3 | ✅ PASS（子 repo 裡的檔案在檔案系統上存在，判為 present） |
| C-2／C-4 | 不適用（工單沒有 `branch` 欄位；C-4 本來就不實作） |
| ct-exec | 沒有 STOP、WARN，也沒有向塔台提問 |
| 子 repo commit | 兩個子 repo 各自用 `git -C <子 repo> commit --only <去掉前綴的路徑>` 成功，commit 後兩邊 `git status` 都是乾淨的 |
| 上層 | `git status` 看不到子 repo 的檔案（`.gitignore` 生效）；工單在上層用 `--only` commit |
| 派工 | 新目錄第一次派工遇到資料夾信任確認，`--wait-started` 回 exit `8`；使用者在分頁回答後正常開始 |

〈限制〉第 2、3 點與〈派工與面板〉的資料夾信任確認，都是這次實驗的發現。

**未驗證**：面板一鍵派工（要另開一個指向上層的 BAT workspace；cwd = workspace 根是依 BAT 的行為推得）；子 repo 有 remote 時的 push。
`isolation: worktree` 不能用是依 BAT 建 worktree 的方式推得（〈限制〉第 1 點），沒有另做實驗。

## 文件同步衛生

塔台在以下時機提醒檢查文件與程式碼一致性：
- 每個 Story 完成後：「本次改動是否影響 `AGENTS.md` 的專案上下文區塊（舊專案：`project-context.md`）或 architecture.md？」
- Sprint 結束時：派發「文件同步檢查」工單
- 發現回報的程式碼結構與文件描述不符時：主動標記 ⚠

## 跨子專案重複需求

```
同一需求需要在多個子專案實作？
├─ 邏輯完全相同
│   └─ 抽到 shared/ 作為共用模組
│
├─ 規則相同但實作因技術棧不同
│   └─ 先做一、後參照模式
│      1. 先派 app-a 工單（含 spec + 實作 + 測試）
│      2. 完成後派 app-b 工單，附上：
│         - 參照實作路徑
│         - 一致性要求
│         - 可變範圍
│         - 測試案例（必須覆蓋相同場景）
│
└─ 規則不同
    └─ 各自獨立，分別派發互不相依的工單
```

## 多專案協調

管理多個相關專案（前後端分離、微服務）時：
- 追蹤每個專案的獨立進度
- A 專案影響 B 時，主動提醒同步設計文件
- 派發工單時附上「需參照其他專案的檔案路徑」
