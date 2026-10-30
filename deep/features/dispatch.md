---
title: 派工：auto-session 與 BAT
description: 四種派工模式、終端偵測與 17 種開分頁方式、mode 怎麼傳到 Worker、BAT 派工的成功判讀與啟動確認，以及永遠留著文字提示的降級鏈。
---

# 派工：auto-session 與 BAT

<p class="ct-lead">一句話：派工是「把一張工單交到一個新 Worker 手上」。CT 會盡量自動開分頁，但成功與否只認 exit code，模式用參數明確傳給 Worker，任何一步失敗都往下降級，最後一定留著一行可以手動照做的文字。</p>

塔台寫好工單之後，還要有人開一個新 session、輸入 `/ct-exec T####`。這一步看起來瑣碎，卻是多 session 工作最容易出錯的地方：開錯目錄、開錯 workspace、忘了帶模式、以為分頁開了其實沒開。`auto-session` 這組規則就是把這一步標準化，讓它在各種終端裡行為一致、失敗時看得出來。

## 四種模式：在哪裡保留人的判斷 {#modes}

`auto-session` 設定決定派工之後誰做什麼，預設是 `ask`：

| 值 | 開 Worker | Worker 回報 | 決定下一張 |
|---|---|---|---|
| `off` | 塔台只顯示指令文字，你自己開 | 你帶回塔台 | 你 |
| `ask` | 每次問：開新分頁／複製到剪貼簿／我自己來 | Worker 顯示固定訊息，你帶回 | 你 |
| `on` | 靜默開新分頁並帶入指令 | 預填在塔台輸入列，你按送出 | 你 |
| `yolo` | 同 `on` | **自動送出** | **塔台自主決定** |

每往下一階，就把一段「人的確認」交給機器。所以這四階不是「越自動越好」的排序，而是**選擇在哪裡保留人的判斷**。`yolo` 拿掉了最後一個人工確認點，因此必須用斷點把判斷權在必要時交還給人，細節見 [yolo 與斷點 A–E](./yolo)。

## 終端偵測與 17 種開分頁方式 {#terminal}

要「自動開新分頁」，塔台得先知道自己在哪種終端裡。偵測依一棵由特定到寬鬆的決策樹，靠環境變數判斷：最先看 `BAT_SESSION=1`（在 BAT 內部就直接走 BAT 路由），接著是 Codespaces、devcontainer、SSH、tmux、screen、WSL、Windows Terminal，然後依 `TERM_PROGRAM` 分辨 VS Code、macOS Terminal、iTerm2、Warp、WezTerm，再認 Linux 桌面終端（kitty、Alacritty、GNOME Terminal、Konsole），最後才是 mintty 或未知。

順序本身就是設計。例如 BAT 會設 `TERM_PROGRAM`，不先短路就會被誤判成別的終端，甚至遞迴派工；tmux 裡的「開新分頁」使用者預期的是 `tmux new-window`，所以 tmux 優先於外層終端；WSL 裡 `WT_SESSION` 可能穿透進來，但剪貼簿要走 `clip.exe`、開分頁要 `wt.exe` 加 `wsl.exe` 兩層，順序顛倒就會選錯指令。

偵測結果對應到一張 17 列的開分頁指令矩陣。其中幾種環境根本沒有可靠的開分頁方式（WSL 的 conhost 外層、devcontainer、Warp、SSH），矩陣直接標「無方案」，交給剪貼簿層處理，不硬做。

## Worker 不讀設定：mode 怎麼送到 Worker {#mode-flags}

Worker 是無狀態的：它**不讀**塔台的設定檔來決定自己用什麼模式。模式由塔台在派工時用參數明確傳過去：

```
塔台設定（auto-session）＋ 啟動詢問的結果
  → 派工參數 --mode <yolo|ask|off|on>、--interactive／--no-interactive
  → BAT 注入 Worker 環境 CT_MODE、CT_INTERACTIVE
  → Worker 收尾時依 CT_MODE 決定怎麼通知塔台
```

這等於把執行期的上下文從「磁碟上的設定檔」搬到「行程參數」：同一張工單、同一組參數，不管在哪個 session 執行，行為都相同。`CT_MODE` 沒設或不合法時（例如舊版塔台派工），Worker 退回 `ask` 並顯示升級提示，不會中斷。`CT_MODE=yolo` 時 Worker 一律不問使用者，不管 `CT_INTERACTIVE` 是什麼，有問題就改問塔台（見 [Worker 向塔台提問](./worker-questions)）。

## BAT 派工：helper、範圍權杖與分頁角色 {#bat}

在 BAT 裡，塔台用 BAT 提供的 helper `bat-terminal.mjs` 建立 Worker 分頁：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" \
  --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
  --cwd "<專案根目錄>" \
  --mode <yolo|ask|off|on> [--interactive|--no-interactive] \
  --agent default --skill ct-exec --workorder <工單 ID>
```

幾個參數各有理由：

- `--notify-id` 傳塔台自己的 `BAT_TERMINAL_ID`。BAT 會把它注入 Worker 環境成 `BAT_TOWER_TERMINAL_ID`，Worker 收尾時才知道要通知哪個塔台。
- `--workspace` 和 `--cwd` 修的是**兩件不同的事**：`--cwd` 決定 Worker 在哪個目錄執行，`--workspace` 決定分頁落在哪個 workspace。實際發生過「目錄對了、分頁落錯 workspace」的情況，所以兩個都要傳，不能互相取代。
- `--agent default` 交給 BAT 依 workspace 預設、全域預設解析要開 Claude Code 還是 Codex；`--skill` 加 `--workorder` 是不帶前綴的中立寫法，由 BAT 依 agent 組出 `/ct-exec T####` 或 `$ct-exec T####`。Codex 用 plugin 安裝時 skill 名稱一定帶前綴（`$ct:ct-exec`），叫不到 BAT 送的 `$ct-exec`，所以接 BAT 派工的 Codex 用 zip 手動安裝（v5.14.0 起，見[安裝](/install#plugin)）；Claude Code 用 plugin 安裝不受影響。CT 刻意不自己偏好任何一個 agent，避免同一個專案的工單今天由一個工具跑、明天換另一個，造成行為漂移。
- `<工單 ID>` 是工單 frontmatter 的 `id` 原樣，設了前綴就含前綴、不截短（例 `--workorder CP-T0113`）。塔台傳什麼，BAT 就用什麼登記 Worker 分頁，之後的回報、回收都靠它對上分頁；v5.14.1 起塔台端的派工、回收範本都這樣寫，和 Worker 端的回報（v5.13.1 起）一致。

環境變數分成兩組，各自只服務一個方向。塔台派工要 `BAT_SESSION`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`、`BAT_TERMINAL_ID`、`BAT_WORKSPACE_ID`；Worker 通知要 `BAT_TOWER_TERMINAL_ID`、`BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`。拆開的原因很實際：混成一份清單的話，塔台會因為自己沒有 `BAT_TOWER_TERMINAL_ID` 而誤判「不在 BAT 裡」，退回剪貼簿派工。另外，Git Bash、MSYS 這類 helper shell 可能看不到 BAT 注入的變數，所以在 Windows 上要用原生 PowerShell 再查一次；PowerShell 看得到就照常走 BAT，記為 `shell env visibility mismatch`，不得因此降級。

BAT `>= 0.7.0-pre.1` 起，`BAT_REMOTE_TOKEN` 是**每個分頁專屬的範圍權杖**。有 `BAT_TOWER_TERMINAL_ID` 的分頁就是 Worker 分頁，只能通知自己綁定的塔台；沒有的才是塔台分頁，能派工、回收自己派出的 Worker、宣告角色。權杖的值不得寫進日誌、工單、回報或任何輸出，需要記錄時只寫「已設定」。在 Worker 分頁裡啟動塔台，派工會被拒絕（`Forbidden`），這時降級訊息會多一句提示，請你到一般分頁啟動塔台。

塔台啟動時還會用 `--set-role tower --mode <m>` 向 BAT 宣告「這個分頁是塔台」，BAT 據此把分頁標題設成 `<Agent 顯示名> · Tower`，和 Worker 分頁的 `… · Worker · T####` 對應。分頁的權限模型與標題在 BAT 這一端怎麼呈現，見 <BatLink path="control-tower#permissions">BAT 站：權限模型</BatLink> 與 <BatLink path="control-tower#visibility">BAT 站：看得見每個 Agent</BatLink>。

## 成功判讀：只認兩個信號 {#success}

派工成不成功，CT 只信兩件事：

1. helper 的 **exit code 為 `0`**（主規則）
2. BAT 的 `bat-scripts.log` 有 helper 寫的 `terminal-created` 成功紀錄（事後查證用）

stdout 印的 `Terminal created: …` **不解析**，那是給人看的輸出。這條規則有一段教訓：舊版 BAT 在 `--skill --workorder` 模式下會印出 `Terminal created: null`，看起來像失敗，分頁其實已經建好；若據此降級成剪貼簿，就會多派一次。另一個常見誤判是拿 `curl` 打 BAT 的本機 port 檢查健康，那是 TLS/WSS 端點，純 HTTP 探測必然回空，不代表 BAT 壞了。

## 啟動確認：`--wait-started`，exit 8 不重派 {#wait-started}

exit `0` 只代表分頁建好了，不代表 Worker 已經啟動。v5.6.0 起（需要 BAT `>= 0.7.0-pre.6`），派工命令最後加 `--wait-started 30000`，helper 會等 Worker 回報「已啟動」再結束，stdout 最後多一行 `started:`：

| exit | `started:` | 塔台怎麼做 |
|---|---|---|
| `0` | `<時間>` | Worker 已啟動，時間記進派工紀錄 |
| `0` | `unknown` | 無法判定（例如舊版 codex、自訂 CLI），照常等 Worker 回報，**不是失敗** |
| `8` | `unconfirmed` | 分頁已建立但 30 秒內沒確認啟動：**不重派、不降級**，請你去看那個分頁 |
| `1` | — | 派工失敗，照降級鏈處理 |

exit `8` 不重派是關鍵：分頁還在，重派就會讓同一張工單出現兩個 Worker。而且 exit `8` 可能是誤報，例如專案設定關掉了 BAT 讀不到的 hook，Worker 其實正常在跑。要不要重派由你決定，塔台不會自動做，也不會替你在那個分頁輸入任何東西。

舊版 BAT 不認得這個參數時會 exit `1`，stderr 含 `Unknown option '--wait-started'`，而且沒有建立分頁。這時塔台去掉參數重派一次，並在這個 session 記住「不支援」，之後不再帶。

## 降級鏈：文字提示永遠在 {#fallback}

```
BAT 內部終端（BAT_SESSION=1）
  ↓ 不在 BAT
開新終端分頁
  ↓ 失敗（終端環境未知、預檢不過、指令失敗）
寫入剪貼簿
  ↓ 失敗（沒有可用的剪貼簿工具）
文字複製提示（永遠顯示）
```

降級是**靜默**的，不顯示錯誤、不打擾你。例外只有兩個，都會多顯示一行原因：在 Worker 分頁啟動了塔台（`Forbidden`），以及 BAT 重開後的 Recovery 提示還沒回答（`RECOVERY_PENDING`）。不論哪種情況，塔台都**不自動重派**。

就算分頁成功開了，文字提示也照樣顯示。你可能切到別的環境、想重開一次，或剪貼簿根本無法確認有沒有寫進去（OSC 52 就無法偵測成敗），那一行文字是唯一不依賴任何工具的保底。

## 收單後回收分頁 {#recycle}

`worker_auto_close: done` 時，塔台確認收單（工單 `DONE`、本次不 Renew、在 BAT 內）之後，請 BAT 用 `--close-worker <工單 ID>` 回收 Worker 分頁。BAT 會等分頁連續安靜一段時間才關，所以塔台的提示只寫「約 N 秒後回收」，不寫成「已關閉」。隔離工單加 `--worktree keep`，只關分頁、保留 worktree 給合併。

v5.12.0 起還有另一種回收：要對**同一張工單**重派 Worker 之前，先以 `--delay-ms 0` 回收舊分頁，不受 `worker_auto_close` 影響。不回收的話，同一張單會有兩個 Worker 分頁，新 Worker 完成後的收單回收也會因為找到兩個候選而失敗。`ct-done` 補救派工例外：不回收，保留舊分頁的現場給你看。

兩種回收的失敗都**不影響收單結果、不改變重派決定**，在 yolo 下也不計入斷點。

::: tip 命令範例
本頁的命令都是摘要，參數合法值、防注入規則與 exit code 全表以 reference 為準。
:::

## 延伸閱讀 {#further-reading}

- `control-tower/references/auto-session.md` § 終端環境偵測、§ B 面：開新分頁指令矩陣（17 終端）、§ 派發後行為（依 `auto-session` 設定）、§ Mode 與互動旗標協定（v4.3.0+）、§ BAT 內部終端路由（Better Agent Terminal）、§ BAT 派發成功判讀規則（唯一信號源）、§ Worker 啟動確認（`--wait-started`，v5.6.0+）、§ 降級鏈、§ 安全邊界
- `control-tower/references/work-order-system.md` § 收單後回收 Worker 分頁（`worker_auto_close`，v5.1.0+）、§ 重派前回收舊 Worker 分頁（v5.12.0+）
- `control-tower/references/yolo-mode.md` § 收單後回收 Worker 分頁（v5.1.0+）
- `control-tower-guide/references/runtime-dispatch.md`（全篇）
- `control-tower-guide/references/bat-integration.md` § 一張分頁的生命週期、§ 兩組環境變數，兩個角色
- BAT 站：<BatLink path="control-tower#division">分工：塔台、跑道與雷達</BatLink>

::: warning 摘要不具權威
Portal 是摘要，不具權威，與 reference 有出入時以 reference 為準。
:::
