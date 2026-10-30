---
title: 落點檢查（Landing Zone Check）
description: Worker 動手前確認自己在對的 repo：身分不能用路徑證明，所以由 C-0 的 repo 欄位承重，C-1、C-3、C-2 各自只做輔助。
---

# 落點檢查（Landing Zone Check）

<p class="ct-lead">一句話：「我是不是在這張工單寫給的那個 repo？」是一個身分問題，而路徑存在與否答不了身分問題；所以 CT 讓工單帶一個 repo 欄位當外部訊號，由 C-0 承重，其他檢查只負責輔助與留證據。</p>

## 它要回答的問題 {#question}

Worker 在任何寫入動作之前，包括改工單、碰產品檔、commit，都要先跑落點檢查。它要回答的是：「我現在所在的 repo，是這張工單寫給的那個 repo 嗎？」

會出錯的情境並不罕見：派工端傳錯 `cwd`、使用者在錯的終端分頁輸入指令、兩個專案剛好都有一張 `T0047`。工單 ID 跨專案會撞號，所以光看 ID 什麼也分辨不出來。落點檢查**不假設派工端傳的參數一定正確**，它是「把一張正確的工單執行在錯的 repo」之前的最後一道防線。

這份檢查只在 `ct-exec` 定義一次。`ct-done` 與 `ct-status` 都引用同一份：寫入型的 `ct-done` 不符就停，唯讀的 `ct-status` 只把結果和狀態一起報告。三個 skill 共用一份定義，是「單一權威定義」原則的直接應用，各自複述的話，遲早會出現三個略有不同的落點檢查。

## 為什麼身分不能用路徑證明 {#why-not-paths}

最直覺的作法是看工單 `affects_files` 列的路徑在不在目前的 repo 裡。問題在於：

> 「正確的 repo，但工單要從零建立整棵目錄」和「完全錯的 repo」，在純路徑測試下**結構上無法區分**，兩者都是「那些路徑不存在」。

所以不論怎麼調門檻，看幾層目錄、看多少比例，路徑存在與否都答不了身分問題。身分需要一個**外部訊號**。v5.0.5 起，塔台寫工單時在 frontmatter 填 `repo`，值是 repo 根目錄的目錄名，Worker 直接拿它和實際 repo 根目錄的名稱比對。

## 四個檢查與它們的份量 {#checks}

<LandingCheck />

| 檢查 | 份量 | 失敗時停不停 |
|---|---|---|
| **C-0** repo 身分 | 承重 | 停：`WRONG_REPO_CONFIRMED` |
| C-1 工單位置 | 便宜的健全檢查 | 停，但很少觸發 |
| C-3 `affects_files` 抽查 | 輔助、啟發式 | 只有工單**沒有** `repo` 欄位時才停 |
| C-2 分支比對 | 只提醒 | 不停 |

### C-0：repo 身分 {#c0}

`repo` 和 `basename(REPO_ROOT)` 不相等，就停下來回報 `WRONG_REPO_CONFIRMED`，列出兩個值與解析出的 repo 根目錄，不猜、不繼續。**不准修改工單的 `repo` 欄位讓檢查通過**。相等就通過，之後的 C-3 只記錄、不再單獨叫停。

工單沒有 `repo` 欄位時，記一個「repo identity unavailable」警告，改由 C-3 加 C-1 判斷。缺欄位本身**從不叫停**，因為舊工單和別的塔台寫的工單本來就可能沒有這個欄位。

`repo` 是目錄名，不是路徑也不是顯示名稱，也不要拿它和 `project` 比。`project` 指的是 mono-repo 裡的子專案或 PLAN、BUG 紀錄，和 repo 是刻意分開的兩個欄位。在 BAT worktree 裡（有 `CT_HOME` 時），比對對象換成 `CT_HOME` 的目錄名，因為 worktree 的根目錄叫 `T####`；換的是比對對象，語意不變，仍是承重、仍然不符就停。

工單集中在上層、改的是巢狀的獨立 repo 時（v5.14.3 起寫明的配置，見[一個塔台管多個共用 repo](/deep/features/multi-tower#nested-repos)），`repo` 填**上層**的目錄名，Worker 也在上層執行。C-0 因此只驗上層，不驗子 repo 是不是對的 clone，這一步要寫進工單步驟（例如 `git -C <子 repo> rev-parse --show-toplevel`）。上層一定要是 git repo，不是的話 C-0、C-1、C-3 都會跳過。

### C-1：工單位置 {#c1}

確認找到的工單檔確實在 repo 根目錄底下。不在就停。它便宜，但很少觸發：Worker 是在自己的 cwd 底下找工單，cwd 錯了通常是根本找不到工單；只有 ID 撞號才會誤中，而那種情況 C-0 會直接抓到。所以 C-1 要保留，但不能依賴它。

### C-3：`affects_files` 抽查 {#c3}

取 `affects_files` 的前 5 項，排除含萬用字元的項目與工單目錄本身，對每一項往上找**最近存在的上層目錄**：路徑本身存在，或有一層祖先存在，都算「存在」；整條路徑上只有 repo 根目錄存在，才算「不存在」。工單本來就可能建立新檔，所以檔案本身不在是允許的；在正確的 repo 裡，幾乎總有某一層祖先已經存在。

| 結果 | C-0 已通過，或工單宣告 `expect_missing` | 工單沒有 `repo` 欄位 |
|---|---|---|
| 全部不存在 | 記警告，繼續 | **停**：`WRONG_REPO_SUSPECTED`，列出檢查過的每個路徑 |
| 部分存在 | 記錄，繼續 | 記錄，繼續 |
| 沒有可測項目 | 記「不適用」，繼續 | 記「不適用」，繼續 |

停下來時不准為了讓檢查通過而去建立缺少的目錄。

### C-2：分支比對 {#c2}

工單有 `branch` 欄位時，和目前分支比對。不一樣只提醒；不能互動時記警告後繼續。刻意切換分支是很常見的正常理由，所以它從不硬停。

## 量測：從 100% 掉到 41% {#measurement}

C-3 原本是承重檢查。它被降級，靠的是量測而不是猜測。塔台拿另一個 repo 的 **34 張真實工單、65 個 `affects_files` 項目**，模擬「Worker 誤落到另一個 repo」重放了一次：

| C-3 判定法 | 擋下的錯誤落點 |
|---|---|
| 只看直接父目錄（最初的規格） | **34／34，100%** |
| 往上找最近存在的祖先（v5.0.4 實際出貨的規則） | **14／34，41%** |

失效的機制很單純：`docs/api/*.md` 會一路往上找到 `docs/`，而兩個 repo 剛好都有這個頂層目錄。STOP 的條件是「**所有**可測項目都不存在」，只要有一個項目名字夠通用，整張工單的 C-3 就失效。

那為什麼不退回「只看直接父目錄」？因為「建立一個新版本目錄並在裡面工作」這種很普通的工單，在**正確**的 repo 裡，所有項目和它們的直接父目錄也都不存在，會被誤判成錯 repo。**會亂叫的警報終究會被忽略**，這個代價比它換來的保護更持久。所以 CT 的做法是保留祖先上溯（低誤報），另外加上 C-0 承擔身分判斷。C-3 不再需要高偵測率，只在 C-0 無法使用時才恢復叫停的權力。

需要說明的是，這是一次**模擬量測**，不是真的攔下過錯誤落點的實例。它的價值在於推翻了一個直覺：「路徑檢查應該夠用」聽起來很合理，量下去才知道它在常見的目錄命名下會大量失效。

## `expect_missing`：例外通道，不是靜音開關 {#expect-missing}

工單 frontmatter 可以宣告：

```yaml
landing_check:
  expect_missing: true
```

意思是「這張工單的執行步驟自己會建立 `affects_files` 指向的目錄樹，開工時找不到是預期的」。它只把 C-3 的「全部不存在」從停止降為警告，**C-0 不受影響**，照樣不符就停。

- **只有塔台能設**，而且只在工單真的會建立自己的目標樹時才設。
- **Worker 絕不能為了讓檢查通過而加上它**。遇到落點停止，正確的反應是回報塔台，而不是改工單改到它不再叫。
- 它不涵蓋「檔案應該存在但我找不到」，那正是 C-3 要抓的訊號。

沒寫就是 `false`。C-0 不符時改工單的 `repo` 也是同一回事：所有「改工單讓護欄閉嘴」的動作，本質上都是拆掉護欄。

## 為什麼不做 C-4 {#no-c4}

曾經有人提議加一個 C-4：檢查 BAT 的 workspace ID 是否等於「這個專案平常用的 workspace」。這個提議被**刻意否決**，記在規則裡以免再被提起：

1. 沒有這樣的欄位，要做就得在專案設定新增一個鍵。
2. **workspace ID 不穩定**。同一個 repo 的 workspace ID 在兩次快照之間就變過一次，把它釘在設定裡只會不斷誤報，而誤報的護欄會被忽略。

替代做法是**只記錄、不比對**：Worker 把觀察到的 `BAT_WORKSPACE_ID` 寫進回報當證據，它從不拿來比較，也從不擋下任何事。這樣保留了事後追查的價值，又沒有誤報。

## 怎麼留紀錄 {#recording}

落點檢查的結果寫進工單回報區：`PASS`、`WARN` 或 `STOP`，並點名哪些檢查不是 PASS。C-0 的比對要明確寫出兩個值，也就是工單的 `repo`（或「沒有」）和觀察到的 repo 根目錄名，讓事後能重建當時的判斷。

::: tip 命令範例
本頁的判定表是摘要，各檢查的精確條件以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `ct-exec/SKILL.md` § Landing Zone Check（C-0 — Repo identity (load-bearing)、C-1 — Work order belongs to this repo、C-3 — `affects_files` spot check (secondary / heuristic)、`landing_check.expect_missing` — the escape valve、C-2 — Branch comparison、Recording、C-4 (workspace consistency) is deliberately not implemented）
- `control-tower-guide/references/governance.md` § Landing Zone Check：身分不能用路徑證明
- `control-tower/references/mono-repo-patterns.md` § 巢狀的獨立 repo › 限制（v5.14.3+）
- `control-tower/references/work-order-template.md` § `repo`（v5.0.5+，落點檢查 C-0 承重欄位）、§ `landing_check`（v5.0.5+，落點檢查逃生閥）
- CT 安裝與使用指南 § 2.15、§ 2.16

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
