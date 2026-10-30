# Auto-Session 自動開新 Session

> 工單派發後自動在新終端分頁開啟 sub-session，減少使用者手動操作。

## 終端環境偵測

啟動時偵測（環境偵測 Step 0 第 8 項），結果快取供後續使用。偵測回傳標準 struct（見下方「偵測結果 struct」），供 B 面（開新分頁，T0226）/ C 面（剪貼簿，T0227）/ D 面（四模式映射）共同消費。

> 規格來源：PLAN-025 研究工單 T0224（commit `013175a`）A/B/C/D 四面矩陣。本節規格化偵測層；B 面具體開分頁指令與 C 面剪貼簿寫入實作分別由 T0226 / T0227 落實。

### 偵測結果 struct（T0226 / T0227 消費介面）

```typescript
interface TerminalDetection {
  /** 識別到的主要終端類型（見 TerminalType） */
  type: TerminalType;

  /** 觸發此分類的主要環境變數名稱（debug log 用） */
  primary_var: string;

  /** 其他共存的偵測信號（如 tmux-in-iTerm2 → additional_vars 含 TERM_PROGRAM） */
  additional_vars: string[];

  /** 外層包裹層陣列（由內到外），空陣列代表無包裹
   *  tmux-in-iTerm2-on-macOS  → ["tmux", "iterm2"]
   *  devcontainer-in-VSCode   → ["devcontainer", "vscode"]
   *  WSL-in-WindowsTerminal   → ["wsl", "windows-terminal"]
   */
  wrapping_layers: string[];

  /** 平台族群（供降級鏈選擇剪貼簿工具） */
  platform: "windows" | "macos" | "linux" | "wsl" | "container" | "ssh" | "unknown";

  /** 是否為 BAT 內部終端（短路旗標；true 時直接略過 auto-session 新分頁流程） */
  is_bat_internal: boolean;
}

type TerminalType =
  | "bat-internal"          // Step 0
  | "codespaces"            // Step 1
  | "devcontainer"          // Step 2
  | "ssh"                   // Step 3
  | "tmux"                  // Step 4
  | "screen"                // Step 5
  | "wsl"                   // Step 6
  | "windows-terminal"      // Step 7
  | "vscode"                // Step 8 (TERM_PROGRAM=vscode, non-devcontainer)
  | "cursor"                // Step 8 fork 細分（偵測到 CURSOR_* 時）
  | "macos-terminal"        // Step 8 (Apple_Terminal)
  | "iterm2"                // Step 8 (iTerm.app)
  | "warp"                  // Step 8 (WarpTerminal)
  | "wezterm"               // Step 8 (WezTerm)
  | "kitty"                 // Step 9
  | "alacritty"             // Step 9
  | "gnome-terminal"        // Step 9
  | "konsole"               // Step 9
  | "mintty"                // Step 10 (MSYSTEM=MINGW64，無 WT_SESSION)
  | "unknown";              // Fallback
```

### A.1 偵測變數完整表（20 條）

| # | 環境 | 主要偵測變數 | 輔助變數 | 值範例 | 來源 | 優先度 | 互斥/共存 |
|---|------|-------------|---------|--------|------|-------|----------|
| 1 | BAT 內部終端 | `BAT_SESSION=1` | `TERM_PROGRAM=better-agent-terminal`, `BAT_TERMINAL_ID`, `BAT_REMOTE_PORT` | `BAT_SESSION=1` | 專案 spec + 實測 | Step 0（最優先） | 最特定，最優先短路 |
| 2 | GitHub Codespaces | `CODESPACES=true` | `CODESPACE_NAME`, `GITHUB_CODESPACE_TOKEN` | `CODESPACES=true` | GitHub 官方 | Step 1 | 獨佔；視同 devcontainer 處理 |
| 3 | VS Code Remote Containers | `REMOTE_CONTAINERS=true` | `REMOTE_CONTAINERS_IPC`, `REMOTE_CONTAINERS_SOCKETS` | `REMOTE_CONTAINERS=true` | VS Code docs/remote/containers | Step 2 | 和 host `TERM_PROGRAM` 共存；VS Code 1.79+ OSC 52 穿透 |
| 4 | SSH | `SSH_CONNECTION` | `SSH_TTY`, `SSH_CLIENT` | `SSH_CONNECTION=192.168.1.1 42 ...` | OpenSSH sshd(8) | Step 3 | 和外層 term 共存 |
| 5 | tmux | `TMUX` | `TMUX_PANE` | `TMUX=/tmp/tmux-1000/default,1234,0` | tmux(1) | Step 4 | 和外層共存；行為優先於外層 |
| 6 | GNU screen | `STY` | `WINDOW` | `STY=1234.pts-0.hostname` | screen(1) | Step 5 | 和外層共存；同 tmux 邏輯 |
| 7 | WSL | `WSL_DISTRO_NAME` | `WSL_INTEROP`, `WSLENV` | `WSL_DISTRO_NAME=Ubuntu` | learn.microsoft.com/wsl | Step 6 | 獨佔內層；外層可能為 WT |
| 8 | Windows Terminal | `WT_SESSION` | `WT_PROFILE_ID` | `WT_SESSION=<UUID>` | WT 官方 | Step 7 | 可和 WSL 共存為外層 |
| 9 | VS Code（non-devcontainer） | `TERM_PROGRAM=vscode` | `VSCODE_INJECTION=1`, `VSCODE_GIT_IPC_HANDLE` | `TERM_PROGRAM=vscode` | VS Code 官方 | Step 8 | 和 macOS term 互斥 |
| 10 | Cursor（VS Code fork） | `TERM_PROGRAM=vscode` | 部分 fork 另設 `CURSOR_*`（需實作階段驗證） | 同 9 | 推測 | Step 8（VSCode 分支內細分） | 同 9 |
| 11 | macOS Terminal.app | `TERM_PROGRAM=Apple_Terminal` | `TERM_SESSION_ID` | - | Apple 官方 | Step 8 | TERM_PROGRAM 分支互斥 |
| 12 | iTerm2 | `TERM_PROGRAM=iTerm.app` | `ITERM_PROFILE`, `ITERM_SESSION_ID` | - | iTerm2 docs | Step 8 | 同上 |
| 13 | Warp | `TERM_PROGRAM=WarpTerminal` | - | - | Warp 官方 | Step 8 | 同上 |
| 14 | WezTerm | `TERM_PROGRAM=WezTerm` | `WEZTERM_EXECUTABLE`, `WEZTERM_PANE` | - | WezTerm 官方 | Step 8 | 同上 |
| 15 | Kitty | `KITTY_WINDOW_ID` | `KITTY_PID`, `TERM=xterm-kitty` | `KITTY_WINDOW_ID=1` | Kitty docs | Step 9 | 不設 TERM_PROGRAM，獨立 |
| 16 | Alacritty | `ALACRITTY_LOG` / `ALACRITTY_SOCKET` | `TERM=alacritty` | - | Alacritty docs | Step 9 | 獨立 |
| 17 | GNOME Terminal | `GNOME_TERMINAL_SERVICE` / `GNOME_TERMINAL_SCREEN` | `COLORTERM=gnome-terminal` | - | GNOME 文件 | Step 9 | 獨立 |
| 18 | Konsole | `KONSOLE_VERSION` | `KONSOLE_DBUS_SESSION` | - | KDE docs | Step 9 | 獨立 |
| 19 | MSYS2 / Git Bash | `MSYSTEM=MINGW64` | `OSTYPE=msys` | `MSYSTEM=MINGW64` | MSYS2 官方 + 實測 | Step 10 | Windows 專屬；可和 WT_SESSION 共存為外層 |
| 20 | 通用色彩（輔助） | `COLORTERM=truecolor` | `TERM=xterm-256color` | - | - | 僅供色彩判斷，**不作終端識別** |

### A.2 決策樹（由特定到寬鬆）

```
Step 0. BAT_SESSION == "1" in the owning shell
        → type: "bat-internal", is_bat_internal: true
        → 短路：已在 BAT 內部，走 BAT 內部終端路由（見下方「BAT 內部終端路由」章節）
          避免 auto-session 遞迴派發。
        → 若 helper shell 看不到 BAT_*，Windows 上先用 native PowerShell 只列 Env:BAT* 的名稱複查（不輸出值）；
          PowerShell 可見時仍視為 BAT，標記 shell env visibility mismatch。

Step 1. CODESPACES == "true"
        → type: "codespaces", platform: "container"
        → 視同 devcontainer 處理（OSC 52 穿透 VS Code 1.79+）

Step 2. REMOTE_CONTAINERS == "true"
        → type: "devcontainer", platform: "container"
        → wrapping_layers 視 TERM_PROGRAM 疊加（通常含 "vscode"）
        → 子決策（容器內 VS Code 版本）：
           - VS Code 1.79+   → OSC 52 穿透 → C 面 OSC 52 剪貼簿
           - VS Code < 1.79  → 文字提示（不依賴剪貼簿，避免誤判）

Step 3. SSH_CONNECTION 存在
        → type: "ssh", platform: "ssh"
        → wrapping_layers 含外層（依 TERM_PROGRAM / WT_SESSION 疊加）
        → 子決策（依外層 terminal OSC 52 支援度）：
           - 外層為 iTerm2 / WT / VSCode / Kitty / WezTerm → OSC 52 剪貼簿
           - 外層為 macOS Terminal                         → 文字提示（OSC 52 缺）

Step 4. TMUX 存在
        → type: "tmux", wrapping_layers 前插 "tmux"
        → 優先於外層：tmux 內「開新分頁」= tmux new-window
        → 繼續評估外層（Step 7+）以決定剪貼簿穿透路徑

Step 5. STY 存在
        → type: "screen", wrapping_layers 前插 "screen"
        → 同 tmux 邏輯：screen -X screen 為新分頁，繼續評估外層

Step 6. WSL_DISTRO_NAME 存在
        → type: "wsl", platform: "wsl"
        → 子決策（外層判斷）：
           - WT_SESSION 也存在 → 走 wt.exe + wsl.exe 雙層（B 面）
           - 否則（conhost 外層）→ 剪貼簿 via clip.exe（C 面），B 面不可用

Step 7. WT_SESSION 存在（且 Step 6 未命中）
        → type: "windows-terminal", platform: "windows"
        → 純 Windows Terminal（非 WSL）

Step 8. TERM_PROGRAM 有值（依值分支；前段 Step 已吃掉 devcontainer / ssh）
        - "vscode"          → type: "vscode"
        - "Apple_Terminal"  → type: "macos-terminal", platform: "macos"
        - "iTerm.app"       → type: "iterm2",         platform: "macos"
        - "WarpTerminal"    → type: "warp"
        - "WezTerm"         → type: "wezterm"
        - 其他值             → 保留原值於 primary_var，type: "unknown"

Step 9. Linux 桌面終端識別（TERM_PROGRAM 未設 / 不識別時）
        - KITTY_WINDOW_ID        → type: "kitty"
        - ALACRITTY_LOG          → type: "alacritty"
        - GNOME_TERMINAL_SERVICE → type: "gnome-terminal"
        - KONSOLE_VERSION        → type: "konsole"
        - 均為 platform: "linux"

Step 10. 降級識別
        - MSYSTEM=MINGW64（無 WT_SESSION） → type: "mintty", platform: "windows"
        - TERM=xterm-kitty / alacritty / ... → 補識別（輔助信號）
        - 其餘 → type: "unknown", platform: "unknown"

Fallback:
  type == "unknown" → 剪貼簿層（若可用）→ 文字提示
```

### 短路規則（由強至弱，5 條）

1. **BAT_SESSION 最優先**：避免 BAT 內部遞迴派發（對應風險 R1）。BAT 設了 `TERM_PROGRAM=better-agent-terminal`，若不先短路會被 Step 8 誤判。
2. **容器類（CODESPACES / REMOTE_CONTAINERS）優先於 SSH 與外層 TERM_PROGRAM**：容器內的開分頁能力由 VS Code 提供，不是容器內 shell。
3. **tmux / screen 優先於外層 term**：使用者在 tmux 內的「開新分頁」預期 = tmux new-window，而非外層 terminal 的分頁。
4. **WSL 優先於 WT_SESSION**（對應風險 R2）：WSL 內 `WT_SESSION` 可能穿透（Win11 22H2+），但剪貼簿必須走 `clip.exe`、開分頁需 `wt.exe wsl.exe -e` 雙層；顛倒順序會選錯指令。
5. **REMOTE_CONTAINERS 優先於 TERM_PROGRAM**：容器內 `TERM_PROGRAM=vscode` 會穿透，但實際無法靠 VS Code 自動開新分頁（VS Code Remote 的終端由 shell 提供）。

### 偵測邏輯（虛擬碼）

```
function detect_terminal() -> TerminalDetection:
  wrapping_layers = []

  # Step 0：BAT 內部短路；Windows helper shell empty 時需 native PowerShell 只列 Env:BAT* 名稱複查（不輸出值）
  if env.BAT_SESSION == "1" or native_powershell_has_bat_env():
    return build("bat-internal", "BAT_SESSION", infer_platform(),
                 is_bat_internal = true)

  # Step 1–2：容器類
  if env.CODESPACES == "true":
    return build("codespaces", "CODESPACES", "container")
  if env.REMOTE_CONTAINERS == "true":
    wrap = ["vscode"] if env.TERM_PROGRAM == "vscode" else []
    return build("devcontainer", "REMOTE_CONTAINERS", "container", wrap)

  # Step 3：SSH
  if env.SSH_CONNECTION:
    return build("ssh", "SSH_CONNECTION", "ssh",
                 wrapping = outer_term_layers())

  # Step 4–5：包裹層（tmux / screen）— 前插並繼續
  if env.TMUX: wrapping_layers.insert(0, "tmux")
  if env.STY:  wrapping_layers.insert(0, "screen")

  # Step 6：WSL
  if env.WSL_DISTRO_NAME:
    outer = "windows-terminal" if env.WT_SESSION else "conhost"
    return build("wsl", "WSL_DISTRO_NAME", "wsl",
                 wrapping = wrapping_layers + [outer])

  # Step 7：純 Windows Terminal
  if env.WT_SESSION:
    return build(first_wrapper_or("windows-terminal"),
                 "WT_SESSION", "windows",
                 wrapping = wrapping_layers + ["windows-terminal"] if wrapping_layers else [])

  # Step 8：TERM_PROGRAM 分支
  match env.TERM_PROGRAM:
    "vscode"         → return build("vscode",         "TERM_PROGRAM", infer_platform(), wrapping_layers)
    "Apple_Terminal" → return build("macos-terminal", "TERM_PROGRAM", "macos",          wrapping_layers)
    "iTerm.app"      → return build("iterm2",         "TERM_PROGRAM", "macos",          wrapping_layers)
    "WarpTerminal"   → return build("warp",           "TERM_PROGRAM", infer_platform(), wrapping_layers)
    "WezTerm"        → return build("wezterm",        "TERM_PROGRAM", infer_platform(), wrapping_layers)

  # Step 9：Linux 桌面
  if env.KITTY_WINDOW_ID:         return build("kitty",          "KITTY_WINDOW_ID",         "linux", wrapping_layers)
  if env.ALACRITTY_LOG:           return build("alacritty",      "ALACRITTY_LOG",           "linux", wrapping_layers)
  if env.GNOME_TERMINAL_SERVICE:  return build("gnome-terminal", "GNOME_TERMINAL_SERVICE",  "linux", wrapping_layers)
  if env.KONSOLE_VERSION:         return build("konsole",        "KONSOLE_VERSION",         "linux", wrapping_layers)

  # Step 10：降級識別
  if env.MSYSTEM == "MINGW64":    return build("mintty", "MSYSTEM", "windows", wrapping_layers)

  # Fallback
  return build("unknown", "-", "unknown", wrapping_layers)

function detect_clipboard():
  # 完整規格見 §「C 面：剪貼簿層」（T0227 落實）
  # 呼叫端改用 copy_to_clipboard_with_fallback(text, detection)（B.4 介面）
  # 該函式依 C.1 平台優先順序 → C.2 OSC 52 allowlist → C.4 文字提示降級
  return copy_to_clipboard_with_fallback
```

### 測試者主場景（devcontainer）預期偵測結果

```json
{
  "type": "devcontainer",
  "primary_var": "REMOTE_CONTAINERS",
  "additional_vars": ["TERM_PROGRAM=vscode", "TERM=xterm-256color"],
  "wrapping_layers": ["vscode"],
  "platform": "container",
  "is_bat_internal": false
}
```

驗證轉 T0228 實機跑 `env | cut -d= -f1 | grep -iE "REMOTE|CODESPACES|TERM|SSH"`（只列名稱；要判斷值時只讀單一非祕密變數，規則見 § BAT 內部終端路由 › 偵測條件）。備案信號（若 `REMOTE_CONTAINERS` 未設）：`test -f /.dockerenv` 或檢查 `/proc/1/cgroup` 是否含 `docker` / `containerd`。

### VS Code（non-devcontainer）備註：R4 待 T0228 驗證

> T0224 研究階段將「VS Code 自動開分頁行為」列為 🔴 高風險（Q7 R4）——VS Code 官方無「自動分頁」CLI 說明；現行實作（Step 8 分支 type=`vscode` 時送 `<agent-cli> "/ct-exec T####"` 字面指令）依賴的行為**實測可疑**。
>
> **R4 驗證不在本工單（T0225）範圍內**（Worker 於 Windows BAT 內部執行，無 VS Code 實測環境；使用者目前也在 BAT，兩者皆無法實測）。**移交 T0228**（測試者於 macOS VS Code + devcontainer 實機驗證時一併處理）。
>
> 在 T0228 驗證完成前，VS Code（non-devcontainer）路徑**維持現行行為不變**，T0226 開新分頁指令表應沿用現行 `<agent-cli> "/ct-exec T####"` 字面指令。驗證結論出爐後若需降級，另派補丁工單修改 VS Code 段落。

## B 面：開新分頁指令矩陣（17 終端）

> 規格來源：PLAN-025 研究工單 T0224（commit `aea9373`）B 面矩陣 + Q5 失敗偵測 + Q7 風險緩解。
> 本節由 T0226 落實 A.2 決策樹產出的 `TerminalDetection` → 對應開新分頁指令的映射。剪貼簿降級（C 面）不在本節範圍，僅定義 fallback 呼叫介面給 T0227 消費。

### B.0 映射介面（`TerminalDetection` → command）

```typescript
// 呼叫鏈：detect_terminal() → resolve_new_tab_command(detection) → exec_or_fallback_to_clipboard()
function resolve_new_tab_command(d: TerminalDetection): NewTabCommandSpec | null {
  // 回傳 null 代表「此 type 不走 B 面」— 直接交棒 C 面剪貼簿（T0227）
  // 依 d.type 查 B.1 表；若 d.wrapping_layers 含 "tmux" / "screen" / "wsl"，需雙層包裹（見 B.1 第 2、14、15 列）
}

interface NewTabCommandSpec {
  /** 實際要 spawn 的 argv（已處理 quoting） */
  argv: string[];

  /** 需要預檢的 binary / 設定（如 `allow_remote_control yes` / socket / --tab 支援度） */
  preflight: PreflightCheck[];

  /** 失敗偵測規則（exit code + stderr 字樣） */
  failure_signatures: {
    nonzero_exit: boolean;                       // true = exit code 非 0 即失敗
    stderr_patterns: string[];                   // stderr 含任一字樣 → 失敗
  };

  /** 失敗時的 fallback 策略 */
  fallback: "clipboard" | "text-prompt" | "none";
}

interface PreflightCheck {
  kind: "command_exists" | "config_key" | "socket_alive" | "version_gte";
  target: string;
  reason: string;
}
```

### B.0.1 Agent CLI 解析

`<agent-cli>` 是 B 面非 BAT 路由的 placeholder，支援 Claude 與 Codex，但不得寫死任一工具：

1. BAT 內部路由已在 A.2 Step 0 短路：使用 `bat-terminal.mjs --agent default --skill ct-exec --workorder T####`，由 BAT Default Agent 設定解析，B 面不參與。
2. 非 BAT 路由解析順序：`CT_AGENT_CMD`（只允許 `claude` / `codex`）→ 安全自動偵測（只在兩者唯一可用時採用）→ C 面剪貼簿/文字提示。
3. 若 `claude` 與 `codex` 同時存在且 `CT_AGENT_CMD` 未指定，不得自行偏好其中一個，避免跨工具行為漂移。
4. 實際 spawn 前必須將 `<agent-cli>` 替換為解析後的 allowlist literal；失敗則回傳 `null` 交 C 面。
5. 本節與 B.1、C 面寫的 `"/ct-exec T####"` 是 Claude 寫法的樣板；解析為 `codex` 時依 § BAT 內部終端路由 › 依安裝方式的 skill 呼叫字串（v5.14.0+）替換成 Codex 寫法並改用單引號（v5.14.0+）。

**映射原則**：
- `d.is_bat_internal === true` → **不走 B 面**（BAT 路由已在 A.2 Step 0 短路處理，見「BAT 內部終端路由」章節）
- `d.wrapping_layers` 含 `"tmux"` → 優先走 `tmux new-window`（第 14 列），外層 terminal 不參與
- `d.wrapping_layers` 含 `"screen"` → 優先走 `screen -X screen`（第 15 列）
- `d.type === "wsl"` + `d.wrapping_layers` 含 `"windows-terminal"` → 走第 2 列（雙層 wt.exe + wsl.exe）
- `d.type === "wsl"` + `d.wrapping_layers` 含 `"conhost"` → **B 面無方案**，回傳 `null` → C 面剪貼簿（T0227）
- `d.type === "devcontainer"` / `"codespaces"` / `"ssh"` / `"warp"` → **B 面無方案**，回傳 `null` → C 面（T0227 OSC 52）
- `d.type === "vscode"`（non-devcontainer）→ 沿用現行 `<agent-cli> "/ct-exec T####"` 字面指令（R4 待 T0228 驗證，見 §247）
- 其餘 type → 查 B.1 表

### B.1 指令矩陣（17 條目）

| # | `d.type` | 平台 | 開新分頁指令（樣板，`$PWD` / `T####` 為 placeholder） | 預檢 | 可行性 | Quoting 要點 |
|---|---------|------|--------------------------------------------------|------|-------|-------------|
| 1 | `windows-terminal` | Windows | `wt -w 0 nt -d "$PWD" <agent-cli> "/ct-exec T####"` | `command -v wt` | ✅ 高（**現行實作、回歸保護**） | WT 不支援嵌套 quote；多個 subcommand 以 `\;` 分隔 |
| 2 | `wsl`（wrap 含 `windows-terminal`） | WSL | `wt.exe -w 0 nt wsl.exe -e bash -lc 'cd "$PWD" && <agent-cli> "/ct-exec T####"'` | `command -v wt.exe` + `command -v wsl.exe` | ✅ 高 | 雙層 shell；`-lc` 載入 login profile；若需 Win path 轉譯用 `wslpath` |
| 3 | `wsl`（wrap 含 `conhost`） | WSL | **B 面無方案** → 交 T0227（`clip.exe` 剪貼簿 + 文字提示） | — | ❌ | — |
| 4 | `vscode`（non-devcontainer） | 跨平台 | `<agent-cli> "/ct-exec T####"`（沿用現行；R4 待 T0228 驗證） | `command -v <agent-cli>` | ⚠️ 中 | — |
| 5 | `devcontainer` / `codespaces` | Container | **B 面無方案** → 交 T0227（VS Code 1.79+ OSC 52 穿透） | — | ❌ | — |
| 6 | `macos-terminal` | macOS | `osascript -e 'tell application "Terminal" to do script "cd " & quoted form of "$PWD" & " && <agent-cli> /ct-exec T####"'` | `command -v osascript` + TCC Automation 授權 | ✅ 高（首次需授權） | AppleScript 雙層 escape；建議走暫存 `.scpt` 檔避開字串逃逸；`quoted form of` 處理含空白/Unicode 的 `$PWD` |
| 7 | `iterm2` | macOS | `osascript -e 'tell application "iTerm" to tell current window to create tab with default profile command "<agent-cli> /ct-exec T####"'` | `command -v osascript` + TCC Automation 授權 | ✅ 高（首次需授權） | 同 6；`create tab` 不走 cwd，需在 command 中 `cd` 或改用 iTerm2 Python API |
| 8 | `warp` | macOS | **B 面無方案**（Warp 公開 API 不含 tab 控制） → 交 T0227（OSC 52 剪貼簿） | — | ❌ | — |
| 9 | `wezterm` | 跨平台 | `wezterm cli spawn --cwd "$PWD" -- <agent-cli> "/ct-exec T####"` | `command -v wezterm` | ✅ 高 | `--` 後直接傳 argv，無需 bash wrap；`--cwd` 原生支援空白路徑 |
| 10 | `gnome-terminal` | Linux | `gnome-terminal --tab --working-directory="$PWD" -- bash -lc '<agent-cli> "/ct-exec T####"; exec bash'` | `command -v gnome-terminal` + `--tab` 支援（≥ 3.0） | ✅ 高 | `--` 後單引號包裹；`exec bash` 保留視窗以便觀察輸出 |
| 11 | `konsole` | Linux | `konsole --new-tab --workdir "$PWD" -e bash -lc '<agent-cli> "/ct-exec T####"; exec bash'` | `command -v konsole` | ✅ 高 | 同 10 |
| 12 | `kitty` | Linux | `kitty @ launch --type=tab --cwd "$PWD" bash -lc '<agent-cli> "/ct-exec T####"; exec bash'` | `command -v kitty` + `allow_remote_control yes` + `listen_on` 設定 | ✅ 中 | 預檢失敗 → 交 T0227 |
| 13 | `alacritty` | Linux | `alacritty msg create-window --working-directory "$PWD" -e bash -lc '<agent-cli> "/ct-exec T####"'` | `command -v alacritty` + daemon/socket 已啟動 | ✅ 中 | 預檢失敗 → 交 T0227 |
| 14 | `tmux`（`wrapping_layers` 含 `tmux`，本身 session 內） | 跨平台 | `tmux new-window -d -c "$PWD" '<agent-cli> "/ct-exec T####"'` | `command -v tmux` + `TMUX` env 存在 | ✅ 高 | 單引號包裹 tmux command；`-c` 指定 cwd；`-d` 不切換焦點 |
| 15 | `screen`（`wrapping_layers` 含 `screen`） | 跨平台 | `screen -X screen -t 'ct' bash -lc '<agent-cli> "/ct-exec T####"'` | `STY` env 存在 | ✅ 中 | `-t` 設分頁名；`-X` 發送指令給當前 screen session |
| 16 | `ssh` | 跨平台 | **B 面無方案**（SSH 不能控制宿主開分頁） → 交 T0227（OSC 52） | — | ❌ | — |
| 17 | `mintty`（MSYS2 / Git Bash，無 `WT_SESSION`） | Windows | `mintty -e bash -lc 'cd "$PWD" && <agent-cli> "/ct-exec T####"'` | `command -v mintty` | ⚠️ 中（開新視窗，非分頁） | Windows 路徑含反斜線時需 `'` 包裹；`-e` 後全部視為 argv |

> **實機預檢結果（T0226 Worker 環境）**：
> - WT 回歸（現行實作未動）→ 指令與 §431 白名單一致，路徑保護 ✅
> - `mintty -e` dry-run → mintty 1.x+ 支援 `-e`（verified via `mintty --help`），指令 parse 通過 ✅
> - tmux → Worker 機器未裝（`command -v tmux` 無輸出），文件推測 → 交 T0228 測試者 devcontainer 驗證

### B.2 Quoting 通用注意（T0224 B 面通用注意）

1. **工單編號格式**依 [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義）——本節不複述該正則。該格式為嚴格白名單，不含空白、引號或 shell 元字元 → 指令端注入風險低；但 `$PWD` 含空白/Unicode 時各層 shell 仍需正確 escape
2. **最穩妥做法**：把完整指令寫成暫存 `.sh` / `.scpt` 檔案，再呼叫該檔，避開多層 escape（尤其 osascript + bash 雙層）
3. **WT 嵌套 quote 限制**：WT `nt` subcommand 不支援嵌套雙引號；若需傳遞含空白的參數，用 `\"` escape 或走暫存檔方案
4. **osascript 雙層 escape**：AppleScript 本身的字串 + shell 字串 = 兩層；建議：
   - 優先使用 `quoted form of "..."`（AppleScript 原生）處理動態路徑
   - 複雜指令走暫存 `.scpt` + `osascript /tmp/ct-####.scpt`
5. **`$PWD` Unicode**：macOS Terminal.app 與 iTerm2 osascript 直傳 Unicode path 需確認 terminal 的輸入編碼為 UTF-8（預設已是）；Windows Terminal 與 mintty `-e` 亦 UTF-8 預設，無額外處理

### B.3 失敗偵測策略（依 T0224 Q5）

統一策略：**每次 spawn 後檢查 exit code → 非 0 或 stderr 含已知錯誤字樣 → 進入下一級（C 面剪貼簿 或 文字提示）**

| 指令層 | 偵測方式 | stderr 錯誤字樣（部分清單） | 限制 |
|-------|---------|-------------------------|------|
| `wt -w 0 nt` | exit code + `%ERRORLEVEL%` | — | WT 非同步啟動，exit 0 不保證分頁出現；需 PATH 預檢 |
| `wt.exe -w 0 nt wsl.exe -e` | 同上 | — | 雙層；外層 wt.exe exit code + 內層 wsl.exe 失敗可能只在 stderr 回報 |
| `osascript` | exit code + stderr 掃描 | `not authorized`, `execution error`, `-1743`（TCC 拒絕）| 首次彈窗可能等使用者很久（> yolo 超時）→ 觸發 R6 緩解（降級剪貼簿） |
| `gnome-terminal --tab` | exit code + `--version` 預檢 | `Unknown option '--tab'` | Ubuntu 18.04 舊版不支援 `--tab` |
| `konsole --new-tab` | exit code | — | 相容性佳 |
| `tmux new-window` | exit code + `tmux list-windows` 差分 | `no server running`, `can't find session` | TMUX socket 無效（容器 mount 問題）會明確回錯 |
| `kitty @ launch` | exit code + stderr 掃描 | `Remote control is disabled`, `No permission` | 需預檢 `allow_remote_control yes` |
| `alacritty msg create-window` | exit code + stderr 掃描 | `No such file or directory`（socket 未啟動） | 需預檢 daemon/socket |
| `wezterm cli spawn` | exit code | — | 相容性佳 |
| `screen -X screen` | exit code | `No screen session found` | 需 `STY` env |
| `mintty -e` | exit code | — | 相容性佳 |

### B.4 降級鏈呼叫介面（交 T0227）

B 面失敗 → 呼叫 C 面剪貼簿層。具體剪貼簿寫入實作**不在本節範圍**（T0227 落實），本節僅定義介面合約：

```typescript
// B 面呼叫 C 面的介面（T0227 需提供此 API）
function copy_to_clipboard_with_fallback(
  text: string,                       // 要寫入的文字（如 "/ct-exec T####"）
  detection: TerminalDetection,       // 供 C 面選擇 OSC 52 / pbcopy / clip 等工具
): ClipboardResult;

interface ClipboardResult {
  method: "pwsh" | "clip" | "pbcopy" | "xclip" | "xsel" | "wl-copy" | "clip.exe" | "osc52" | "tmux-buffer" | "none";
  success: boolean;                   // OSC 52 永遠回 true（不可偵測）
  unicode_safe: boolean;              // clip 為 false、其餘 true
}
```

**B 面降級流程**：

```
1. resolve_new_tab_command(detection)
   → 回傳 null？     → 直接呼叫 copy_to_clipboard_with_fallback(text, detection) + 永遠顯示文字提示
   → 回傳 spec？     → 進入 2.

2. 跑 spec.preflight（每條檢查）
   → 任一失敗？      → 呼叫 copy_to_clipboard_with_fallback(...) + 文字提示
   → 全通過？        → 進入 3.

3. spawn(spec.argv)
   → exit code 非 0？       → 呼叫 copy_to_clipboard_with_fallback(...) + 文字提示
   → stderr 含失敗字樣？    → 同上
   → 成功？                → 仍顯示文字提示（使用者可能切換 session）
```

**原則**：文字提示永遠顯示（即使 B 面成功），使用者才能在不同環境回看；C 面 OSC 52 層**無法偵測**成功失敗，必然保留文字提示（R7 緩解）。

### B.5 R6 osascript 首次授權備註（macOS only）

macOS Terminal.app / iTerm2 的 `osascript` 指令首次執行時，系統會彈出 **TCC（Transparency, Consent, and Control）授權對話框**，要求使用者授予當前執行 `osascript` 的行程（通常為所選 Agent CLI（Claude 或 Codex）或其 host terminal）對 Terminal.app / iTerm.app 的自動化控制權。

**行為細節**：
- 首次彈窗若使用者**未即時授權**，`osascript` 會阻塞等待（可能數秒到無限）→ 破壞 yolo 模式的「靜默派發」預期
- 授權狀態儲存在 `~/Library/Application Support/com.apple.TCC/TCC.db`，一旦授權後續不再彈窗
- 使用者可於 **System Settings → Privacy & Security → Automation** 檢視 / 撤銷授權

**T0226 緩解（R6）**：
- `on` / `yolo` 模式首次在 macOS 執行 osascript 失敗（stderr 含 `not authorized` 或 exit 非 0）→ **立即降級** C 面剪貼簿 + 顯示強化提示：
  ```
  ⚠️ macOS 自動開分頁需授權
     首次使用需於 System Settings → Privacy & Security → Automation
     勾選所選 Agent CLI → Terminal.app（或 iTerm.app）
     已自動把指令複製到剪貼簿，請貼上執行：/ct-exec T####
  ```
- 第二次起若仍失敗 → 視為使用者已明確拒絕授權，永久降級剪貼簿（同本 session 不再嘗試）

## C 面：剪貼簿層（傳統工具 + OSC 52）

> 規格來源：PLAN-025 研究工單 T0224（commit `aea9373`）C 面矩陣 + Q7 R7 緩解。
> 本節落實 A.2 決策樹產出的 `TerminalDetection` → 剪貼簿寫入策略，以及 OSC 52 作為跨環境（SSH / devcontainer / tmux 穿透）備援。呼叫介面 `copy_to_clipboard_with_fallback` 已於 B.4 定義，本節補完內部實作規格。

### C.0 核心原則

1. **文字提示永遠顯示**：OSC 52 無法從程式端偵測成功失敗（終端回應不標準化，TCC 授權、使用者關閉、剪貼簿被第三方覆蓋等情境都不會產生 exit code），因此**即使看似成功，文字提示永遠顯示**（R7 緩解）。
2. **平台優先傳統工具**：傳統工具（pbcopy / xclip / pwsh Set-Clipboard 等）exit code 可偵測，優先使用；失敗或不存在時再嘗試 OSC 52。
3. **macOS Terminal.app 不走 OSC 52**：預設關閉 `allowClipboardAccess`，GUI 無開關可啟用 → 直接走 pbcopy + 文字提示（避免誤判為成功）。
4. **tmux 穿透需外層支援**：OSC 52 在 tmux 內需設 `set -g set-clipboard on` 且外層終端支援 OSC 52 才會穿透；偵測到 `wrapping_layers` 含 `"tmux"` 時，先查**最外層** terminal 是否在支援清單內再決定。

### C.1 傳統剪貼簿寫入指令矩陣（9 條目）

| # | 場景（`d.type` / `d.platform`） | 指令（樣板） | 預檢 | 失敗偵測 | Unicode 安全 | 備註 |
|---|---------------------------------|-------------|------|---------|-------------|------|
| 1 | Windows pwsh（**優先**） | `pwsh -NoProfile -Command "Set-Clipboard -Value '<text>'"` | `command -v pwsh` | exit code 非 0 | ✅ | 原生 Unicode 支援；Git Bash / WT / mintty / cmd 都可跑 |
| 2 | Windows Git Bash 降級 | `printf '%s' '<text_ascii>' \| clip` | `command -v clip`（**且** pwsh 不可用） | exit code 非 0 | ❌ | MSYS2 UTF-8 → Windows 原生 ANSI 轉換丟失 → 僅傳 ASCII；訊息降級為英文（如 `T#### done`） |
| 3 | macOS | `printf '%s' '<text>' \| pbcopy` | `command -v pbcopy` | exit code 非 0 | ✅ | macOS 內建 |
| 4 | Linux X11（xclip） | `printf '%s' '<text>' \| xclip -selection clipboard` | `command -v xclip` + `$DISPLAY` 有值 | exit code 非 0 或 stderr 含 `Can't open display` | ✅ | 無 `$DISPLAY` 時直接跳第 7 列（OSC 52）或第 5 列 |
| 5 | Linux X11（xsel 備援） | `printf '%s' '<text>' \| xsel --clipboard --input` | `command -v xsel` + `$DISPLAY` | exit code 非 0 | ✅ | xclip 不存在時的備援 |
| 6 | Linux Wayland | `printf '%s' '<text>' \| wl-copy` | `command -v wl-copy` + `$WAYLAND_DISPLAY` 有值 | exit code 非 0 | ✅ | `wl-clipboard` 套件；GNOME 40+ / KDE Plasma 5.25+ Wayland 預設 |
| 7 | WSL → Windows 宿主 | `printf '%s' '<text>' \| clip.exe` | `command -v clip.exe` | exit code 非 0 | ⚠️ 需 `chcp 65001`（UTF-8 code page） | `clip.exe` 預設用 Windows ANSI；未設 code page 時中文會亂碼。替代：`powershell.exe -NoProfile -Command "Set-Clipboard -Value '<text>'"`（原生 UTF-8） |
| 8 | WSL → Windows 宿主（pwsh 路徑） | `powershell.exe -NoProfile -Command "Set-Clipboard -Value '<text>'"` | `command -v powershell.exe` | exit code 非 0 | ✅ | 第 7 列的 Unicode 友善替代；略慢（`powershell.exe` 啟動約 500ms） |
| 9 | tmux（內層緩衝） | `tmux load-buffer -` (stdin 餵入 text) + `tmux show-buffer` 驗證 | `command -v tmux` + `$TMUX` 存在 | exit code 非 0 | ✅ | 寫入 tmux buffer；若 `set -g set-clipboard on` 已設，tmux 會自動發 OSC 52 給外層終端；未設則 buffer 僅限 tmux 內 `prefix + ]` 貼上 |

**平台優先順序（偵測結果 struct → 試用順序）**：

| `d.platform` / `d.type` | 優先順序（從上到下嘗試） |
|-------------------------|------------------------|
| `windows`（`windows-terminal` / `mintty` / `vscode` on Windows） | 1 (pwsh) → 2 (clip ASCII 降級) → OSC 52 |
| `wsl` | 8 (powershell.exe UTF-8) → 7 (clip.exe ASCII 降級) → OSC 52 |
| `macos`（`iterm2` / `warp` / `wezterm` on macOS / `vscode` on macOS） | 3 (pbcopy) → OSC 52 |
| `macos-terminal` | 3 (pbcopy) → **文字提示**（**不走 OSC 52**，見 C.0 第 3 條） |
| `linux`（`gnome-terminal` / `konsole` / `kitty` / `alacritty` / `wezterm` on Linux） | 6 (wl-copy, 若 `$WAYLAND_DISPLAY`) → 4 (xclip) → 5 (xsel) → OSC 52 |
| `container`（`devcontainer` / `codespaces`） | OSC 52（容器內傳統工具通常不可用；VS Code 1.79+ 穿透） |
| `ssh` | OSC 52（依外層終端；詳見 C.2 表） |
| `unknown` | OSC 52 → 文字提示 |

**wrapping_layers 影響**：
- 含 `"tmux"` → 先試第 9 列（tmux buffer 兼 OSC 52 觸發），失敗或未設 `set-clipboard on` 時再試外層平台優先列
- 含 `"screen"` → screen 無官方 OSC 52 穿透機制（4.99.0 起 `:osc52` 選項需手動開啟）→ 直接走外層平台優先列

### C.2 OSC 52 Escape Sequence

OSC 52（Operating System Command 52）是 xterm 定義的終端控制序列，讓應用程式請求終端寫入系統剪貼簿。由終端實作決定是否採納（無強制回應協定）。

#### C.2.1 格式規格

```
ESC ] 5 2 ; c ; <base64(UTF-8 text)> BEL
= \033]52;c;<base64>\007
```

欄位說明：

| 段 | 值 | 說明 |
|----|----|------|
| `ESC` | `\033`（`0x1B`） | Introducer |
| `]` | `]`（`0x5D`） | OSC command prefix |
| `52` | 固定字串 `52` | OSC command code |
| `;` | 分隔符 | — |
| `c` | selection target | `c` = clipboard（系統剪貼簿）；`p` = primary（X11 primary selection） |
| `;` | 分隔符 | — |
| `<base64>` | payload | **UTF-8 編碼後再 base64**；不可含換行（RFC 4648 標準 base64 即可） |
| `BEL` | `\007`（`0x07`） | Terminator（另一選項為 `ST`=`\033\\`；實務上 `BEL` 相容性最好） |

**OSC 52 常見錯誤**：

1. **直接傳明文 base64**：忘記先轉 UTF-8 bytes，中文會爛成 Latin-1 亂碼
2. **base64 含換行**：`base64` 指令預設 76 字元換行 → terminator 判定錯誤。用 `base64 -w0`（GNU） / `openssl base64 -A`（BSD）
3. **用 `ST` 終止但寫錯**：`ST` = `ESC \\`（2 bytes），不是單 `\\`
4. **payload 過長**：xterm / iTerm2 預設限制 ~100 KB；超過會靜默失敗。工單完成訊息只有 `"T#### 完成"` 約 10 bytes，無風險

#### C.2.2 寫入函式規格（虛擬碼）

```typescript
function write_osc52(text: string): void {
  // 1. 轉 UTF-8 bytes
  const utf8_bytes: Uint8Array = encode_utf8(text);

  // 2. base64 編碼（無換行）
  const b64: string = base64_encode_nowrap(utf8_bytes);

  // 3. 組 escape sequence
  const seq: string = "\x1b]52;c;" + b64 + "\x07";

  // 4. printf 到 stdout（**不是 stderr**；tmux 穿透要求 stdout）
  process.stdout.write(seq);

  // 5. 不檢查回傳值（終端無標準化回應）
}
```

**各語言範例**：

| 環境 | 實作 |
|------|------|
| Bash（Linux/macOS） | `printf '\033]52;c;%s\007' "$(printf %s "<text>" \| base64 -w0)"` |
| Bash（BSD `base64`） | `printf '\033]52;c;%s\007' "$(printf %s "<text>" \| openssl base64 -A)"` |
| pwsh（Windows） | `[Console]::Out.Write([char]27 + ']52;c;' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('<text>')) + [char]7)` |
| Node.js | `process.stdout.write('\x1b]52;c;' + Buffer.from(text, 'utf8').toString('base64') + '\x07')` |
| Python | `sys.stdout.write('\x1b]52;c;' + base64.b64encode(text.encode('utf-8')).decode('ascii') + '\x07')` |

#### C.2.3 OSC 52 已知支援清單（lookup table）

> 維護原則：此清單作為「是否嘗試 OSC 52」的 allowlist。未列出者走文字提示，避免誤判為成功。
> 更新時機：新終端驗證支援（或新版本預設啟用 OSC 52）→ append 一列；不在此清單的終端 worker 不嘗試 OSC 52。

| # | 終端 | `d.type` | 預設狀態 | 備註 |
|---|------|---------|---------|------|
| 1 | iTerm2 | `iterm2` | ⚠️ GUI 需手動開啟 | Settings → Profiles → Terminal → **Applications in terminal may access clipboard** 需勾選 |
| 2 | Kitty | `kitty` | ✅ 預設 on | 需設 `clipboard_control write-clipboard`（預設已含）；MacOS 13+ 會要求系統權限 |
| 3 | Alacritty | `alacritty` | ✅ 預設 on | 0.8.0+ 支援 |
| 4 | WezTerm | `wezterm` | ✅ 預設 on | 2020-07-22 起 |
| 5 | Warp | `warp` | ✅ 預設 on | 2023-06+ |
| 6 | Windows Terminal | `windows-terminal` | ✅ 預設 on | 1.18+ 完整支援（`copyFormatting`, `clipboard` 設定已預設） |
| 7 | GNOME Terminal | `gnome-terminal` | ✅ 預設 on | 3.36+（2020-03）起 |
| 8 | Konsole | `konsole` | ✅ 預設 on | 22.04+（2022-04）起 |
| 9 | VS Code integrated terminal | `vscode` | ✅ 預設 on | 1.79+（2023-05）；**含 Remote-SSH / Remote-Containers / Codespaces 穿透** |
| 10 | Cursor（VS Code fork） | `cursor` | ✅ 預設 on | 承襲 VS Code 1.79+ 行為 |
| 11 | mintty（MSYS2 / Git Bash） | `mintty` | ✅ 預設 on | 3.5.0+（2021-05）；`AllowSetSelection=yes` 設定項，預設 yes |
| 12 | tmux（外層在上述支援者） | `tmux` wrapping | 條件 | 需 `set -g set-clipboard on` + 外層終端支援；見 C.2.4 |
| **❌ 不支援** | macOS Terminal.app | `macos-terminal` | ❌ 預設 off | `allowClipboardAccess` plist key 僅 `defaults write` 可改，無 GUI 開關；**永遠走 pbcopy + 文字提示** |
| **❌ 不支援** | Warp（舊版 < 2023-06） | — | — | 已淘汰，現行 Warp 預設 on（上表第 5 列） |

**清單外的終端**（如 `unknown` / 其他 Linux 桌面終端 / 未列出的 SSH client）→ **不嘗試 OSC 52，直接文字提示**（保守策略，避免「沉默失敗」讓使用者以為有複製到但實際沒有）。

#### C.2.4 tmux 穿透

tmux 內的 OSC 52 行為：

```
Worker → stdout (OSC 52)
  ↓
tmux（攔截 OSC 52）
  ├─ set-clipboard off（預設）        → 丟棄，不穿透
  ├─ set-clipboard on                 → 寫入 tmux buffer + 轉發給外層終端
  └─ set-clipboard external（4.2+）   → 僅轉發外層，不寫 tmux buffer
```

**設定建議**（使用者 `~/.tmux.conf`）：

```tmux
set -g set-clipboard on
```

**Worker 端判斷**（虛擬碼）：

```
if "tmux" in detection.wrapping_layers:
  outer = detection.wrapping_layers[-1]  # 最外層
  if outer in OSC52_ALLOWLIST:
    # tmux buffer + 嘗試穿透（pre-check 不可行 → 樂觀嘗試）
    write_osc52(text)
    # 同時文字提示（保險）
  else:
    # 外層不支援 → 只寫 tmux buffer（使用者仍可 prefix + ]）
    tmux_load_buffer(text)
    # 文字提示
```

**偵測 `set-clipboard` 是否開啟**（若需精確判斷）：

```bash
tmux show-options -gv set-clipboard 2>/dev/null
# 回 "on" / "external" / "off"
```

Worker 可選擇**不預檢**（樂觀發送 + 永遠配文字提示），降低複雜度。

### C.3 降級鏈（`copy_to_clipboard_with_fallback` 完整流程）

```
Input: text (e.g. "T0227 完成"), detection (TerminalDetection)

1. 短路：detection.is_bat_internal → return { method: "none", success: true, unicode_safe: true }
   （BAT 內部走 bat-notify.mjs，不走剪貼簿層；見 `ct-exec/SKILL.md` § BAT Notify And Fallback、`ct-done/SKILL.md` § BAT Notify）

2. 依 C.1 表「平台優先順序」逐條嘗試：
   for each command in ordered_commands(detection.platform, detection.type):
     2.1. 跑預檢（command_exists / $DISPLAY / $WAYLAND_DISPLAY 等）
          → 失敗：continue 下一條
     2.2. spawn 指令 + 餵入 text
          → exit code 0：return { method: command.name, success: true, unicode_safe: command.unicode_safe }
          → 失敗：記 log，continue 下一條

3. 傳統工具全數失敗 / 平台無對應工具 → 嘗試 OSC 52：
   3.1. 查 detection.type（或 wrapping_layers 最外層）是否在 C.2.3 allowlist
        → 不在：skip 到 4
        → 在：
            write_osc52(text)
            return { method: "osc52", success: true, unicode_safe: true }
            （注意：OSC 52 永遠回 success=true，由呼叫端決定是否搭配文字提示；C.0 原則已規定「永遠搭配」）

4. OSC 52 也不可用 → return { method: "none", success: false, unicode_safe: false }
   → 呼叫端改顯示文字提示（不複製）

（呼叫端統一規則：無論 2/3/4 哪條成功，都加顯「📋 回塔台回報時輸入：<工單 ID> 完成」文字提示）
```

**範例降級鏈**：

| 偵測結果 | 嘗試順序 | 最終方法 |
|---------|---------|---------|
| `{ type: "windows-terminal", platform: "windows" }`（pwsh 可用） | pwsh ✅ | `pwsh` |
| `{ type: "mintty", platform: "windows" }`（pwsh 不存在） | pwsh ❌ → clip ✅（ASCII） | `clip`（unicode_safe=false） |
| `{ type: "macos-terminal" }` | pbcopy ✅ | `pbcopy`（**不試 OSC 52**） |
| `{ type: "iterm2", platform: "macos" }` | pbcopy ✅ | `pbcopy`（OSC 52 備援用不到） |
| `{ type: "devcontainer", platform: "container", wrapping_layers: ["vscode"] }` | pbcopy/xclip ❌ → OSC 52 ✅（vscode 1.79+ 穿透） | `osc52` |
| `{ type: "ssh", wrapping_layers: ["iterm2"] }` | pbcopy ❌（SSH 端無） → OSC 52 ✅（iterm2 允許） | `osc52` |
| `{ type: "ssh", wrapping_layers: ["macos-terminal"] }` | pbcopy ❌ → OSC 52 **不試**（Terminal.app 不在 allowlist） → 文字提示 | `none`（僅文字提示） |
| `{ type: "tmux", wrapping_layers: ["tmux", "windows-terminal"] }` | tmux load-buffer ✅ + OSC 52 ✅（穿透到 WT） | `tmux-buffer` 或 `osc52`（兩者可疊） |
| `{ type: "unknown" }` | — → OSC 52 不試（不在 allowlist） → 文字提示 | `none` |

### C.4 文字提示模板（`none` / 搭配訊息）

無論 C.3 結果如何，呼叫端**永遠顯示**文字提示（`<工單 ID>` = 工單完整 ID，含前綴、不得截短，規則見 [work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID）：

| 狀態 | 文字提示 |
|------|---------|
| 複製成功（pwsh / pbcopy / xclip 等 Unicode-safe） | `📋 已複製「<工單 ID> 完成」到剪貼簿，切回塔台貼上即可回報。` |
| 複製成功（clip 降級 ASCII） | `📋 已複製「<工單 ID> done」到剪貼簿（中文不支援，降級英文）。` |
| OSC 52 發送（無法確認） | `📋 已嘗試複製「<工單 ID> 完成」（OSC 52），若貼上無內容請手動輸入：<工單 ID> 完成` |
| 全部失敗 | `📋 回塔台回報時輸入：<工單 ID> 完成` |

---

## 派發後行為（依 `auto-session` 設定）

### `auto-session = on`

1. 顯示工單摘要
2. 靜默執行：開新分頁 + 預載指令（或剪貼簿降級）
3. 同時顯示文字提示（備用）
4. 顯示回報快捷：`📋 回塔台回報時輸入：<工單 ID> 完成`

### `auto-session = ask`

1. 顯示工單摘要
2. 互動式提問：
   ```
   🚀 要我幫你開新 Session 嗎？
   [A] 開新分頁執行 /ct-exec T####
   [B] 複製指令到剪貼簿
   [C] 不用，我自己來
   ```
3. 使用者選擇後執行對應動作
4. 顯示回報快捷

### `auto-session = off`

1. 顯示工單摘要
2. 文字提示：
   ```
   🚀 開新 Session 執行：
   /ct-exec T####
   ```
3. 顯示回報快捷

### `auto-session = yolo`

> `on` 的超集：Worker 自動送出完成訊息（依 `bat-notify.mjs --submit` 機制）+ 塔台自主決策下一張工單 + 斷點安全閘（A / B / C；v5.3.0+ 加 E 合併前確認；v5.5.0+ 加 D Worker 等待使用者）。
> v5.5.0+ yolo Worker 有問題時向塔台提問、由塔台代決，見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問。

1. 顯示工單摘要（同 `on`）
2. 靜默執行：開新分頁 + 預載指令（同 `on`）
3. 預載指令改用 `bat-terminal.mjs --notify-id $BAT_TERMINAL_ID --workspace "$BAT_WORKSPACE_ID" --cwd "<專案根目錄>" --mode yolo --no-interactive`（`--workspace` 指定目標 workspace 防錯派；`--cwd` 顯式指定專案根目錄，防呼叫端 cwd 漂移；`--mode yolo` flag 告知 Worker skill 以 yolo 模式收尾，觸發 `bat-notify.mjs --submit`；v5.5.0+ yolo 一律 `--no-interactive`、不帶 `--interactive`，Worker 的問題改問塔台，見 [yolo-mode.md](yolo-mode.md) § 啟動詢問（G3 互動旗標）。派工前把 `worker_question_timeout` 生效值寫進工單 frontmatter，見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › `worker_question_timeout` 的取值）
4. Worker 完成後自動回報塔台 → 塔台執行「yolo 自主決策」流程（見 [yolo-mode.md](yolo-mode.md) § 判定邏輯）
5. 塔台狀態面板**下方**顯示 `⚠️ YOLO MODE ACTIVE` 警語（直到使用者改 config）；位置與內容以 [yolo-mode.md](yolo-mode.md) § 啟動面板警語 為準，面板本身見 [memory-protocol.md](memory-protocol.md) § 塔台狀態面板

**差異點對比**：

| 行為 | `on` | `yolo` |
|------|------|--------|
| 開新分頁 | ✅ | ✅ |
| Worker 回報 | 預填（使用者按 Enter） | 自動送出（`\r`） |
| 下一張工單派發 | 使用者手動 | 塔台自主決策 |
| 啟動面板警語 | 無 | ⚠️ YOLO MODE ACTIVE |
| 斷點機制 | 無（v5.3.0+ 合併前一律確認，見 [yolo-mode.md](yolo-mode.md) § 斷點 E；v5.5.0+ 斷點 D 只告知，見 [yolo-mode.md](yolo-mode.md) § 斷點 D） | A/B/C + D（v5.5.0+，Worker 等待使用者）+ E（v5.3.0+，合併前確認） |
| Worker 有問題 | 研究型工單依互動旗標問使用者 | 問塔台、塔台代決（v5.5.0+；v5.7.0+ BAT `>= 0.7.0-pre.7` 另走 BAT 問答通道、題目仍寫工單；見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問） |
| `_tower-state.md` 區段 | 不影響 | 新增 `## YOLO 歷程` |

詳細規格見 [yolo-mode.md](yolo-mode.md)。

## Mode 與互動旗標協定（v4.3.0+）

塔台派發工單時透過指令 flag + env 顯式傳遞 runtime mode，Worker 不讀 config（D062 無狀態原則落實）。

### Flag 規格

| Flag | 合法值 | 作用 |
|------|-------|------|
| `--mode <value>` | `yolo` / `ask` / `off` / `on` | 指定派發模式，覆蓋 Worker 預設行為 |
| `--interactive` | （無參數） | 允許研究型工單 Worker 互動（v5.5.0+ yolo 派工不使用，見 [yolo-mode.md](yolo-mode.md) § 啟動詢問（G3 互動旗標）） |
| `--no-interactive` | （無參數） | 禁止研究型工單 Worker 互動 |

### 環境變數對照

| Env | 來源 | Worker 讀取 |
|-----|------|------------|
| `CT_MODE` | `--mode <value>` | `ct-exec` § BAT Notify And Fallback / `ct-done` § BAT Notify 分流 |
| `CT_INTERACTIVE` | `--interactive` → `1`; `--no-interactive` → `0` | `ct-exec` 研究模式偵測 |

### Worker 側讀取規則

見 [`ct-exec/SKILL.md`](../../ct-exec/SKILL.md) § Mode And Environment（含 D062：Worker 不讀塔台設定判斷派發模式）。
簡言之：
- `CT_MODE` 未設或不合法 → Worker fallback `ask` + 顯示升級提示
- `CT_INTERACTIVE` 未設 → Worker 尊重工單元資料的 `類型: research` + 工單內互動規則
- `CT_MODE=yolo`（v5.5.0+）→ 不論 `CT_INTERACTIVE`，Worker 都不向使用者提問，改走 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問

### 向下相容

舊塔台派發（無 `--mode` flag）時 Worker 顯示升級提示，但不 break。建議使用者同步升級塔台 + Worker skill 至 v4.3.0+。

## BAT 內部終端路由（Better Agent Terminal）

### 偵測條件

塔台偵測到以下 Tower dispatch 環境變數**全部存在**時，啟用 BAT 路由：
- `BAT_SESSION=1`（BAT 內部終端標記）
- `BAT_REMOTE_PORT`（RemoteServer WebSocket 端口）
- `BAT_REMOTE_TOKEN`（RemoteServer 認證權杖；BAT `>= 0.7.0-pre.1` 起為分頁專屬，見下方 § 範圍權杖與分頁角色）
- `BAT_TERMINAL_ID`（Tower 當前終端 PTY ID）
- `BAT_WORKSPACE_ID`（Tower 當前 workspace UUID）

Tower session **不需要、也不得被要求預先具備** `BAT_TOWER_TERMINAL_ID`。該值是 Worker notify 專用，由 Tower 派發時把自己的 `BAT_TERMINAL_ID` 傳給 `bat-terminal.mjs --notify-id` 後，BAT 注入到 Worker 環境。反過來說，**有**這個變數的分頁就是 Worker 分頁，不能當塔台用（BAT `>= 0.7.0-pre.1` 會拒絕派工），見下方 § 範圍權杖與分頁角色 第 4 點。

不可只用單一 shell 的 `$BAT_SESSION` / `$BAT_*` 判定「非 BAT 環境」。`lean-ctx`、壓縮 shell、Git Bash、MSYS 等 helper 可能看不到 PowerShell/BAT 啟動時注入的 env，造成假陰性。若 BAT 偵測為空，Windows 上必須用 native PowerShell 再查一次：

```powershell
Get-ChildItem Env:BAT* | Select-Object -ExpandProperty Name | Sort-Object
```

bash 的同義寫法：`env | cut -d= -f1 | grep -E '^BAT_' | sort`。

**偵測只判斷有無、不輸出值**（v5.12.7，BUG-001）：本段是 CT 環境偵測輸出規則的**唯一權威定義**，其他檔只放一句並引用這裡。

- 偵測 `BAT_*`／`CT_*` 只判斷「有沒有設定」：任何 helper 或手動檢查都只列變數名稱（上面兩種寫法），不得用會連值一起輸出的指令（例：不接 `Select-Object -ExpandProperty Name` 的 `Get-ChildItem Env:…`、`env | grep …`、`printenv`、`set`、`export -p`）。
- `BAT_REMOTE_TOKEN` 任何時候都不得輸出，需要記錄時只寫「已設定」（或「未設定」），同下方 § 範圍權杖與分頁角色 第 2 點。
- 例外：規則明定要用到的**單一非祕密變數**，只讀那一個變數、不列整組：`CT_MODE`、`CT_INTERACTIVE`（§ Mode 與互動旗標協定）、`ct-exec` 落點檢查記錄的 `BAT_WORKSPACE_ID`、worktree 隔離的 `CT_HOME`／`CT_WORKTREE_*` 證據（`ct-exec/SKILL.md` § Worktree Isolation）。
- 判讀邏輯不變：下一段的 `shell env visibility mismatch` 與上面的必要變數清單照舊。

若 PowerShell 可見上述 Tower dispatch 必要 env，視為 BAT 可派發，並回報為 `shell env visibility mismatch`，不得降級成剪貼簿或文字派發。

### 範圍權杖與分頁角色（BAT `>= 0.7.0-pre.1`，v5.2.4+）

> 本小節是 BAT 範圍權杖、分頁角色、`Forbidden` 與 `RECOVERY_PENDING` 處理的**唯一權威定義**。`SKILL.md`、
> [work-order-system.md](work-order-system.md)、[memory-protocol.md](memory-protocol.md) 與本檔其他小節
> 只放摘要並引用這裡，不複述規則。
> 權杖、角色與 `Forbidden` 的語意以 BAT 為準（CT-T014；BAT T0575 / T0576 / T0579），CT 不得更改參數名、值域或 exit code 語意。

**1. 權杖是分頁專屬的**

BAT `>= 0.7.0-pre.1` 起，本機分頁的 `BAT_REMOTE_TOKEN` 不再是全權的 server token，而是**該分頁專屬**的範圍權杖
（`batcap.` 開頭）；遠端分頁（WSL／SSH／Docker）早已如此。變數名與 helper 讀法都不變，CT 的呼叫方式也不變。

**2. 權杖的值不得外流**

- 不得在分頁之間複製。
- 不得寫入日誌、工單、回報區、剪貼簿、決策日誌、commit message 或任何輸出。
- 不得假設它是 server token。
- 需要記錄時只寫「已設定」（或「未設定」）。

**3. 分頁角色決定 helper 權限**

判定依據只有一個：分頁環境裡**有沒有** `BAT_TOWER_TERMINAL_ID`。本機與遠端同一張表：

| 分頁角色 | 判定 | 可用的 helper |
|---|---|---|
| tower | **沒有** `BAT_TOWER_TERMINAL_ID`（使用者自己開的分頁、塔台分頁） | `bat-terminal.mjs` 派工（agent 模式 `--skill` / `--prompt` 與 raw command 模式）、`--close-worker`（只能關自己派出的 Worker）、`--set-role`（只能設自己） |
| worker | **有** `BAT_TOWER_TERMINAL_ID`（被塔台派出的分頁） | `bat-notify.mjs`：只能通知／預填／`--submit` 給**綁定的那個塔台**；預填只收可列印文字 |

表外的操作一律被拒：helper exit `1`，stderr 為 `Error: Forbidden: <原因>`（`role-not-allowed` / `channel-not-allowed` / `target-not-bound`）。
CT 的正常流程都在表內（塔台只在自己分頁派工、回收、`--set-role`；`ct-exec` / `ct-done` 只以
`bat-notify --target "$BAT_TOWER_TERMINAL_ID"` 回報自己的塔台），行為不需要改。

**4. 塔台必須在非 Worker 分頁啟動**

在有 `BAT_TOWER_TERMINAL_ID` 的分頁（Worker 分頁）執行 `/control-tower`／`$control-tower`，派工、`--close-worker`、
`--set-role` 都會 exit `1`。請在一般分頁（使用者自己開的分頁）啟動塔台。塔台不因這個變數拒絕啟動、也不預先跳過呼叫；
照常呼叫，失敗依第 5 點處理。狀態面板 BAT 欄位在 Worker 分頁的值見 [memory-protocol.md](memory-protocol.md) § 塔台狀態面板。

**5. `Forbidden` 的處理**

派工、`--set-role`、`--close-worker` 的 helper exit 非 `0` 時：

- **判斷只看 exit code**：照各自既有的規則處理，不重試、不改用其他方式 —— 派工依 § BAT 派發成功判讀規則 走 § 降級鏈；
  `--set-role` 依 § 塔台分頁角色宣告 第 5 點；`--close-worker` 依 [work-order-system.md](work-order-system.md) § 回報處理流程 的 exit code 表（收單回收與 v5.12.0+ 重派前回收各一張）。
- **stderr 只用來挑提示文字**：若 stderr 含 `Forbidden`，該次的降級訊息／警告**多一句**原因提示：
  `此分頁是 Worker 分頁（BAT 範圍權杖），請在一般分頁啟動塔台`
- stderr 是否含 `Forbidden`，**不得**用來決定是否降級、是否重試，也**不得**用來判斷 BAT 版本（同 § 舊版 BAT 降級規則 的明文禁止）。
  stderr 不含 `Forbidden` 時，訊息與 v5.2.3 相同。
- 這句提示是 § 降級鏈「靜默降級」的例外：在 Worker 分頁啟動了塔台是使用者要處理的狀況，必須讓使用者看到。

**6. `RECOVERY_PENDING`（只適用於派工）**

BAT 重開且 Terminal Server 存活時，畫面會出現 Recovery 提示。使用者回答之前，從存活的塔台分頁派工，BAT 最多等 2 秒，
還沒回答就讓 helper exit `1`，stderr 為 `Failed to create terminal (RECOVERY_PENDING): …`。BAT 保證這次**沒有**建立分頁，之後也不會補建。

- 規則同第 5 點：**判斷只看 exit code**，照 § BAT 派發成功判讀規則 走 § 降級鏈；**不自動重派**、不重試。
- stderr 只用來挑提示文字：若 stderr 含 `RECOVERY_PENDING`，降級訊息**多一句**：
  `BAT 的 Recovery 提示尚未回答，請先在 BAT 視窗選擇保留或重新開始，再重新派工`
- 同樣是 § 降級鏈「靜默降級」的例外。

**7. 升級與 BAT 重開**

升級當下仍存活的舊分頁（env 是舊的全權 token）在重開前照常可用；退出 BAT 時選「保留」、重開後，存活分頁的權杖照常有效。

**8. 舊 BAT（`< 0.7.0-pre.1`）**

行為與 v5.2.3 完全相同：沒有分頁角色限制，不會出現 `Forbidden` 或 `RECOVERY_PENDING`，第 5、6 點的提示不會觸發。

### 執行方式

塔台使用 BAT 的 `bat-terminal.mjs` CLI helper 透過 WebSocket 在 BAT 內部建立新終端分頁。Helper 路徑優先使用 `BAT_HELPER_DIR`，未設定時才 fallback 到 BAT 安裝目錄：

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" \
  --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
  --cwd "<專案根目錄>" \
  --mode <yolo|ask|off|on> [--interactive|--no-interactive] \
  --agent default --skill ct-exec --workorder T####
```

Fallback：

```bash
"${BAT_HELPER_NODE:-node}" "C:\\Program Files\\BetterAgentTerminal\\resources\\scripts\\bat-terminal.mjs" \
  --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
  --cwd "<專案根目錄>" \
  --mode <yolo|ask|off|on> [--interactive|--no-interactive] \
  --agent default --skill ct-exec --workorder T####
```

路徑必須使用 Windows 形式。不要把 `C:\...` 改成 `/c/...`，Node 會把 POSIX 形式誤判成相對路徑。

**Node 解析（v5.2.1+）**：本段是 BAT helper 執行檔解析的**唯一權威規則**，適用於所有 `bat-terminal.mjs`／`bat-notify.mjs` 呼叫（派工、Worker notify、`--close-worker`、`--set-role`）。其他小節與文件的指令範例都依此書寫，不另行定義。

- bash：`"${BAT_HELPER_NODE:-node}" "<helper>\\bat-terminal.mjs" …`
- PowerShell（不支援 `${VAR:-default}`）：

  ```powershell
  $n = if ($env:BAT_HELPER_NODE) { $env:BAT_HELPER_NODE } else { 'node' }
  & $n "<helper>\bat-terminal.mjs" …
  ```

- 本機沒有 `BAT_HELPER_NODE` → `node`，行為與 v5.2.0 相同。
- 遠端 PTY（WSL／SSH／Docker）由 BAT 注入 bundle node 路徑，避免遠端 PATH 沒有 `node` 而失敗。
- 只允許上述兩種形式（`BAT_HELPER_NODE` 的值或字面 `node`），不得改成其他執行檔；見下方 § 安全邊界。

- `--notify-id`：必須傳入 Tower 當前 `BAT_TERMINAL_ID`；BAT 會把此值注入 Worker 的 `BAT_TOWER_TERMINAL_ID`
- `--workspace`：傳入 Tower 當前 workspace UUID（來自 `BAT_WORKSPACE_ID` 環境變數），確保新 PTY 建立在正確 workspace，避開 renderer `activeWorkspaceId` fallback 導致的錯派（BUG-040 Phase 1.2）
- `--cwd`：傳入目標專案根目錄的絕對路徑（Windows 形式）。省略時 `bat-terminal.mjs` 讓新 PTY 繼承呼叫端 process 的 cwd —— 多數情況正確，但塔台 session 的 cwd 可能因先前操作漂移，且該漂移在派工當下不可見；顯式指定是零成本的防護。
  > `--cwd` 與 `--workspace` 修的是**兩件不同的事**：`--cwd` 決定 Worker 在哪個目錄執行，`--workspace` 決定終端分頁落在哪個 workspace。兩者可各自出錯——**cwd 正確而分頁落錯**正是 BUG-031 / T0137 的實際現象，也就是只傳 `--cwd` 不傳 `--workspace` 的結果。兩個都要傳，不可互相取代。
- `--mode`：v4.3.0+ 顯式傳遞 runtime mode 給 Worker（注入 `CT_MODE` env），Worker 不讀 config（D062 無狀態原則）
- `--interactive` / `--no-interactive`：研究型工單 Worker 互動旗標（注入 `CT_INTERACTIVE` env），由塔台啟動詢問決定（見 [yolo-mode.md](yolo-mode.md) § 啟動詢問）
- `--agent default` 由 BAT 解析為 workspace defaultAgent → global defaultAgent → fallback CLI；Skill 不硬編碼 `codex` / `claude`
- `--skill` + `--workorder` 是 agent-neutral payload；Tower skill 不寫 `/` 或 `$` prefix（也不寫 `ct:`），由 BAT app `terminal:create-agent-command` 依 resolved agent 組出 `/ct-exec T####`（Claude）或 `$ct-exec T####`（Codex）；Codex 只裝 CT plugin 時叫不到，各 agent／安裝方式的寫法見下方 § 依安裝方式的 skill 呼叫字串（v5.14.0+）
- `--workorder` 的合法值依 [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義），**含帶前綴的 ID**
  > ⚠️ **BAT 最低版本**：帶前綴的 `--workorder`（如 `CP-T0113`）需 BAT
  > **`v0.5.9-pre.1`+（BAT 的 fork 版）**。
  > upstream 原始 repo 截至 2026-09-02 **尚未含此修復**。
  > 無前綴的 `T####` 不受此版本邊界限制。
  > 舊版 BAT 的處置見下方 § 舊版 BAT 降級規則。
- `--isolation worktree`（v5.3.0+，選用）：只在工單 frontmatter 有 `isolation: worktree` 時加在上方參數之後；沒有就不加。規則見下方 § worktree 隔離派工
- `--wait-started 30000`（v5.6.0+，BAT `>= 0.7.0-pre.6`）：本塔台 session 未判定「不支援 `--wait-started`」時，加在上方所有參數（含 `--isolation worktree`）的最後；
  已判定不支援就不加，命令與 v5.5.1 逐字相同。四種結果、舊 BAT 降級與 `started:` 行解析見 § Worker 啟動確認
- 新終端自動出現在 BAT UI 終端縮圖列
- xterm.js 自動綁定 PTY output，使用者可即時互動
- 終端標題顯示 `Remote: <command>` 方便辨識

### 依安裝方式的 skill 呼叫字串（v5.14.0+）

> 🔴 本小節是「CT skill 在各 agent、各安裝方式下怎麼呼叫」的**唯一權威定義**。本檔其他各處（B 面矩陣、C 面剪貼簿、
> 派發後行為的文字提示、§ 安全邊界）、`ct-help`、`ct-exec/agents/openai.yaml` 與安裝指南一律引用本小節，不另寫規則。
> 依據：T0349 實機驗證（D435）；BAT 不為此修改（D434 B4）。plugin 名稱 `ct`、marketplace `control-tower`，安裝流程見
> [version-governance.md](version-governance.md) § plugin 安裝／升級。

| Agent | 安裝方式 | 呼叫字串（以 `ct-exec` 為例） | BAT 派工（`--skill ct-exec`） |
|---|---|---|---|
| Claude Code | zip 手動安裝 | `/ct-exec T####` | ✅ |
| Claude Code | plugin `ct` | `/ct-exec T####`；完整寫法 `/ct:ct-exec T####` 也可以 | ✅（BAT 送 `/ct-exec T####`，不用改） |
| Claude Code | 兩者並存（不建議） | `/ct-exec` 用**手動安裝**那份；`/ct:ct-exec` 一定用 plugin 版 | ✅，但用的是手動安裝那份 |
| Codex | zip 手動安裝 | `$ct-exec T####` | ✅ |
| Codex | plugin `ct` | **`$ct:ct-exec T####`**（`$ct-exec` 叫不到：不會注入 plugin 的 `SKILL.md`） | ❌ **不支援**：BAT 送 `$ct-exec`。Codex 要接受 BAT 派工就用 zip 手動安裝 |
| Codex | 兩者並存（不建議） | `$ct-exec` 用**手動安裝**那份；`$ct:ct-exec` 用 plugin 版 | ✅，但用的是手動安裝那份 |

規則：

1. **其他 CT skill 同規則**：把 `ct-exec` 換成 skill 名稱（例 Claude `/ct-done T####`、`/control-tower`；Codex plugin `$ct:ct-done T####`、`$ct:control-tower`）。
2. **BAT 派工**：塔台只傳 `--skill` + `--workorder`，不寫 `/`、`$` 或 `ct:` 前綴（§ 執行方式）。BAT 依 resolved agent 組出
   `/ct-exec T####`（Claude）或 `$ct-exec T####`（Codex），所以 Codex 端只有手動安裝能接受 BAT 派工。
3. **非 BAT 路徑**（B 面開新分頁、C 面剪貼簿、`auto-session = ask`／`off` 的文字提示、§ 安全邊界 白名單）：本檔寫的 `/ct-exec T####`
   是樣板（Claude 寫法）。`<agent-cli>` 解析為 `codex` 時改用 Codex 寫法：預設寫手動安裝的 `$ct-exec T####`，並在文字提示加一行
   「只裝 CT plugin 時改輸入 `$ct:ct-exec T####`」。塔台不偵測 Worker 端的安裝方式（判斷依據不足，T0348 B2）。
4. **引號**：Codex 寫法的 `$` 在 bash 與 PowerShell 的雙引號裡都會被當成變數展開（`$ct`），一律用**單引號**包住
   （例 `codex '$ct:ct-exec T####'`、`Set-Clipboard -Value '$ct-exec T####'`）。
5. **並存時的確認**：要確定用到 plugin 版，用完整寫法（Claude `/ct:ct-exec`、Codex `$ct:ct-exec`）。從手動安裝改用 plugin 時要先移除手動安裝，
   步驟見 [version-governance.md](version-governance.md) § plugin 安裝／升級 › 從 zip 手動安裝遷移到 plugin。

### worktree 隔離派工（`--isolation worktree`，v5.3.0+）

> 本小節是隔離派工（派工命令、成功／失敗判讀、降級）的**唯一權威定義**。`SKILL.md`、
> [work-order-template.md](work-order-template.md)（`isolation` 欄位）、[work-order-system.md](work-order-system.md)
> 與 [merge-workorder.md](merge-workorder.md) 只放摘要並引用這裡。
> 介面契約以 BAT T0583 為準（CT-T015 / D150 / D152），CT 不得更改參數名、值域、exit code 語意或 env 名。

**1. 何時加**

- 工單 frontmatter 有 `isolation: worktree`（欄位定義見 [work-order-template.md](work-order-template.md) § `isolation`）→
  派工命令在上方 § 執行方式 的既有參數**之後**加 `--isolation worktree`。
- 沒有這個欄位 → **不加**。預設不隔離（D152），派工命令與 v5.2.6 逐字相同。
- 只用於 agent skill 模式（`--skill ct-exec|ct-done` + `--workorder`）。降級成 `--prompt`（§ 舊版 BAT 降級規則）或 raw command
  時 BAT 不接受 `--isolation`（exit `1`），所以隔離工單**不走** `--prompt` 降級，見第 4 點。

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" \
  --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" \
  --cwd "<專案根目錄>" \
  --mode <yolo|ask|off|on> [--interactive|--no-interactive] \
  --agent default --skill ct-exec --workorder T#### --isolation worktree
```

BAT 以 `--cwd` 的 git toplevel 為主 checkout，建立 `<主 checkout 上層>/.bat-worktrees/<repo 目錄名>/<T####>`、分支 `ct/<T####>`，
base 為主 checkout 當下的 `HEAD`；同工單重派（Renew）沿用既有 worktree 與分支（v5.12.0+：重派前回收舊分頁時帶 `--worktree keep`，見 [work-order-system.md](work-order-system.md) § 回報處理流程 › 重派前回收舊 Worker 分頁）。Worker 分頁的 env 多四個變數：

| 變數 | 值 |
|---|---|
| `CT_HOME` | 主 checkout 絕對路徑（Windows 為反斜線） |
| `CT_WORKTREE` | worktree 路徑（Worker 的 cwd 在其中） |
| `CT_WORKTREE_BRANCH` | `ct/<T####>` |
| `CT_WORKTREE_BASE` | base SHA（40 字元） |

Worker 在 worktree 中的行為（工單寫回主 checkout、C-0、commit、SHA 回報）見 `ct-exec/SKILL.md` § Worktree Isolation。
BAT **不安裝依賴**（D152），由 Worker 依專案規則安裝。

**2. 成功判讀**

- **派工成功與否**仍只看 exit code：`0` = 已派出，規則同下方 § BAT 派發成功判讀規則。下面的判定順序只回答「有沒有隔離」，
  不改變派工成功的判讀。
- 成功時 stdout 在既有行之後多 `  worktree: <path>`（沿用時加 ` (reused)`）、`  branch: ct/T####`、`  base: <40 字元 SHA>`。
  這三行**只當證據記錄**（寫進派工紀錄，供合併時對照），不參與成功判斷。
- **是否真的隔離**，依序判定：
  1. exit code：`0` 才往下判定；非 `0` 依第 3、4 點處理。
  2. `bat-scripts.log` 該次派工的 `"script":"bat-terminal"`、`"event":"terminal-created"`、`"result":"ok"` 紀錄（格式與檔案位置見
     § BAT 派發成功判讀規則 第 2 點）：隔離派工的這筆紀錄帶 `isolation:"worktree"`，其 `worktree`／`branch`／`base` 欄位為
     **字串 = 已隔離**、為 **`null` = 未隔離**。
  3. 讀不到第 2 步（找不到該筆紀錄，或紀錄沒有 `worktree` 欄位）才看 stdout：有上述三行 = 已隔離，沒有 = 未隔離。

  Worker 端以「沒有 `CT_HOME`」判定未隔離，與上述「未隔離」同義（見 `ct-exec/SKILL.md` § Worktree Isolation）。
- 判定為**未隔離**（新 helper 搭配不認得 `isolation` 的舊 BAT 主程式時：exit `0`、分頁照建但非隔離、stdout 沒有上述三行、
  stderr 一行 `[bat-terminal] --isolation worktree: this BAT did not report a worktree …; the Worker is not isolated.`）：
  派工仍算成功，但**這張工單實際沒有隔離**。塔台必須告訴使用者一行「T#### 未隔離（BAT 太舊），Worker 會直接改主 checkout」，
  派工紀錄記 `isolation: not-applied`；之後依非隔離工單處理（Worker 沒有 `CT_HOME`，行為與 v5.2.6 相同；收單不帶 `--worktree`）。
  stderr 這一行不參與判斷。
- helper 隨 BAT 安裝檔／server bundle 一起出貨，正常安裝不會出現新 helper + 舊主程式；未隔離判定是防禦性規則。
- helper 的等待上限是 40 秒（建 worktree 可能較久），一般派工仍是 3 秒。

**3. exit `7`（`WORKTREE_FAILED`）**

stderr 為 `create: WORKTREE_FAILED`（前一行是原因，例：不是 git repo、位置被佔用、`ct/T####` 已在別處 checkout）。BAT **沒有建立分頁**。

- 不重試、不建分頁、**不自動改成非隔離派工**。
- 告知使用者：工單編號、stderr 的原因行（不得含任何權杖值），以及可選的處置（排除原因後重派、或使用者明確同意後改非隔離派工）。
- 由使用者決定；使用者未明確同意前，不得自行拿掉 `--isolation worktree` 重派。yolo 模式同樣暫停等使用者，不算自動決策。

**4. 舊 BAT 與降級**

- 舊 helper（BAT `< 0.7.0-pre.2`）對 `--isolation` 印 `Unknown option`、exit `1`，**在建立分頁之前結束**。照 § BAT 派發成功判讀規則
  的 exit 非 `0` 處理，走 § 降級鏈。
- 隔離工單的降級**不得**退成非隔離派工：§ 舊版 BAT 降級規則 的 `--prompt` 改送、Windows Terminal、剪貼簿、文字提示都會讓 Worker
  在主 checkout 執行，等於非隔離。所以隔離工單 exit 非 `0` 時：
  - 顯示一行原因（BAT 不支援隔離派工或連線失敗，需 BAT `>= 0.7.0-pre.2`），**停在這裡**，不自動送出任何降級派工；
  - 使用者明確同意「改非隔離」後，才照一般工單的降級鏈處理，並在派工紀錄記 `isolation: declined-by-user`。
- 判斷只看 exit code；stderr 只用來挑提示文字（同 § 範圍權杖與分頁角色 第 5 點），不得用來判斷 BAT 版本。

**5. 回收與合併**

隔離工單收單時 `--close-worker` 帶 `--worktree keep`，合併完成後才 `--worktree remove`：見 [work-order-system.md](work-order-system.md)
§ 收單後回收 Worker 分頁。合併流程與直接合併判準見 [merge-workorder.md](merge-workorder.md)。

### BAT MCP 唯讀 tool（選用通道，v5.3.0+）

> 本小節是 CT 使用 BAT MCP 的**唯一權威定義**。介面以 BAT T0582 / T0584 / T0585 為準（CT-T015），CT 不得更改 tool 名、參數或錯誤碼語意。

BAT `>= 0.7.0-pre.2` 啟動的 claude／codex 分頁（Settings「BAT MCP」預設開）有一組 `mcp__bat__*` 唯讀 tool：

| tool | 用途 | 對應 helper CLI |
|---|---|---|
| `bat_whoami` | 自己的分頁身分：`role`（`tower` / `worker` / `shell`）、`towerTerminalId`、`workorder`、`yolo`；BAT `>= 0.7.1-pre.1` 多 `claudeSessionName` / `claudeSessionId`，見表下說明 | 無 |
| `bat_list_terminals` | 列出範圍內的分頁（`scope: mine \| workspace`；BAT `>= 0.7.1-pre.1` 多 `towers`，見表下說明）；BAT `>= 0.7.0-pre.6` 每列多 `agentStarted`（`true` / `false` / `null`，不含 `agentStartedAt`）；BAT `>= 0.7.0-pre.7` 每列多 `pendingQuestions`；BAT `>= 0.7.1-pre.1` `mine` / `workspace` 每列多 `claudeSessionName` / `claudeSessionId` | 無 |
| `bat_get_state` | 分頁狀態：`working` / `idle` / `exited`；BAT `>= 0.7.0-pre.4` 多 `blocked`（另回 `blockedReason` / `blockedSince`），每個回傳都帶 `blockedDetection`（`hook` / `none`；BAT `>= 0.7.0-pre.9` 多 `osc`），用於斷點 D；BAT `>= 0.7.0-pre.6` 多 `agentStarted`（`true` 時另回 `agentStartedAt`，ms epoch），見表下說明；BAT `>= 0.7.0-pre.7` `blockedReason` 多 `tower`（Worker 等塔台答覆，不是斷點 D）、每個回傳多 `pendingQuestions`，見表下說明；BAT `>= 0.7.0-pre.9` `blockedReason` 多 `input`（codex 等使用者，`source: 'osc'`，用於斷點 D）、`osc` 分頁的 `agentStarted` 有值，見表下說明；BAT `>= 0.7.1-pre.1` 每個回傳多 `claudeSessionName` / `claudeSessionId` | 無 |
| `bat_read_output` | 讀分頁輸出（去 ANSI、權杖類字串已遮罩、`cursor` 增量） | 無 |
| `bat_wait` | 等狀態改變／結束／安靜（最多 45 秒）；BAT `>= 0.7.0-pre.4` 進入／離開 `blocked` 也會返回（`until: 'idle'` 在 `blocked` 也成立）；BAT `>= 0.7.0-pre.6` 回傳同 `bat_get_state` 多 `agentStarted` / `agentStartedAt`，`until` 多 `'agent-started'`（`agentStarted` 不是 `false` 或分頁 `exited` 時返回）；BAT `>= 0.7.0-pre.7` 回傳同 `bat_get_state` 多 `pendingQuestions`，進入／離開 `blocked` / `tower` 也會返回；BAT `>= 0.7.0-pre.9` 進入／離開 `input` 也會返回，`osc` 分頁 `until: 'agent-started'` 生效 | 無 |
| `bat_worktree_status` | 隔離 Worker 的 worktree 狀態（同 `--worktree-status` 的 JSON）；Worker 分頁關閉後也可查（v5.4.0+，BAT `>= 0.7.0-pre.4`） | `bat-terminal.mjs --worktree-status`，見 [merge-workorder.md](merge-workorder.md) § 合併判準資料來源 |
| `bat_wait_question` | Worker 等自己經 BAT 通道問的題目的答覆（v5.7.0+，BAT `>= 0.7.0-pre.7`）。參數、回傳欄位與用法只寫在 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › BAT 通道 | `bat-notify.mjs --wait-answer`（同上節） |
| `bat_list_questions` | 塔台列出送給自己的待答題目（v5.7.0+，BAT `>= 0.7.0-pre.7`）。參數、回傳欄位與用法只寫在 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › BAT 通道 | 無（改讀工單 `### 待塔台決策`，同上節的版本判定與降級） |

- **範圍**由分頁權杖決定：Worker 只能查自己（另可讀綁定塔台的 metadata，不能讀塔台輸出）；塔台可查自己與自己派出的 Worker。
  不在範圍內 → 錯誤，不是空結果。
- **`agentStarted`**（v5.6.0+，BAT `>= 0.7.0-pre.6`；語意以 BAT T0600 為準，codex 以 BAT T0621 C-3 為準）：`true` = 該分頁的 claude 已執行 `SessionStart` hook，
  或（v5.8.0+）`osc` 分頁的 codex 已送第一個 OSC 7501；`false` = 已注入 BAT hooks（`blockedDetection: hook`）但還沒收到 `SessionStart`，
  或（v5.8.0+）`blockedDetection: osc` 但還沒收到 OSC 7501；`null` = 無法判定（`blockedDetection: none`：codex 低於 `0.163.0`、BAT 確認不到
  codex 版本、舊 BAT 上的 codex、自訂 CLI、hooks 未注入或被 claude 設定關閉等），**不得當成啟動失敗**。它是 § Worker 啟動確認 的選用查詢通道：派工當下的判讀以 helper 的
  `--wait-started` 結果為準，`bat-terminal.mjs` 沒有對應的事後查詢 CLI，MCP 不可用時就不查。不代表 ct-exec 已讀工單或開工。
- **`blockedReason: tower` / `pendingQuestions`**（v5.7.0+，BAT `>= 0.7.0-pre.7`；語意以 BAT T0607 為準）：Worker 有 `blocking` 的待答題目時
  `state: blocked`、`blockedReason: tower`、`source: 'question'`，與 `blockedDetection` 無關（codex 分頁也會回）；`pendingQuestions` = 該 Worker 的待答題數。
  `tower` **不是**斷點 D，處理見 [yolo-mode.md](yolo-mode.md) § 斷點 D 與 § Worker 向塔台提問 › 塔台端；回傳沒有 `pendingQuestions` 欄位 = BAT 太舊，
  照 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › BAT 通道 › 版本判定與降級。`blockedDetection: none` 的意思是「永遠不會回 hook 的三種 reason，也不會回 `input`」（v5.8.0 補 `input`，BAT T0621 C-1），不是「永遠不會 `blocked`」。
- **`blockedDetection: osc` / `blockedReason: input`**（v5.8.0+，BAT `>= 0.7.0-pre.9`；語意以 BAT T0621 C-1、C-2 為準）：`osc` = 這個分頁出現過 codex 的
  OSC 7501（BAT 派工時確認 codex `>= 0.163.0` 則啟動即記 `osc`；`hook` 分頁不會變 `osc`）。`input` = codex 在等使用者（核准提示、Plan mode 提問等，
  不分種類），`state: blocked`、`source: 'osc'`、`blockedSince`（ms）；使用者輸入不清除。優先序 `exited` > hook 的三種 reason／`input` > `tower` >
  `working` / `idle`。`input` 是斷點 D，判準、處理與清除只寫在 [yolo-mode.md](yolo-mode.md) § 斷點 D。
- **`claudeSessionName` / `claudeSessionId`**（v5.9.0+，BAT `>= 0.7.1-pre.1`；語意以 BAT T0643 回報區「PLAN-050 介面契約總表」C-4 為準）：
  `bat_whoami`、`bat_list_terminals`（`scope: mine` / `workspace` 每列）、`bat_get_state` 的每個回傳都有這兩個鍵，型別 `string | null`；`bat_wait` 不加。
  `claudeSessionName` = BAT 啟動該 claude-cli 分頁時注入的 `--name`（即 ListAgents 顯示的名稱），`null` = 沒注入（非 claude-cli、使用者自訂參數已命名、
  system claude 太舊或讀不到版本等）。`claudeSessionId` = 最後一次 `SessionStart` hook 回報的 session id（`/clear` 等會換新值）。
  🔴 **鍵不存在 = 舊 BAT（不支援）**，不要當成 `null`。🔴 `claudeSessionId: null` **不代表沒有 session**（還沒回報、沒有 hooks、hooks 被關、headless 重開）。
  名稱格式與用途只寫在 [cross-project-coordination.md](cross-project-coordination.md) § 跨 session 選收件人；面板提示見
  [memory-protocol.md](memory-protocol.md) § 塔台狀態面板。
- **`scope: towers`**（v5.9.0+，BAT `>= 0.7.1-pre.1`；語意以同一總表 C-6 為準）：只給已 `--set-role tower` 宣告的塔台（未宣告、Worker → `NOT_OWNER`，
  與 `scope: workspace` 同一條規則）。回傳同一個 BAT host 上**所有工作區**中執行中、已宣告的塔台（含自己），每列**只有** `id`、
  `workspaceId`（`string | null`）、`workspaceName`（`string | null`，工作區 alias 或名稱；headless 一律 `null`）、`title`（可省略，只有本機）、
  `claudeSessionName`（`string | null`；codex 塔台、手動打 `claude` 的塔台為 `null`）、`state`（`working` / `idle` / `blocked`）、`alive: true`、`self`（boolean）。
  不回 `claudeSessionId`、cwd、輸出、`workorder`。對這些分頁的 `bat_get_state` / `bat_read_output` / `bat_wait` 範圍**不變**（別工作區、非自己 Worker 的塔台仍 `NOT_OWNER`）。
  舊 BAT 回 `INVALID_ARGS`（錯誤文字 `INVALID_ARGS: scope`），MCP client 也可能依舊 BAT 的 schema 先擋下 → 一律視為不支援，不重試、不改用其他 scope。
  BAT 重開後還原的塔台分頁要重新 `--set-role tower` 才會被列出（角色不持久化；CT 每次啟動本來就會宣告，§ 塔台分頁角色宣告 第 3 點）。
  唯一用途見 [cross-project-coordination.md](cross-project-coordination.md) § 跨 session 選收件人 第 2 步。
- **錯誤**：tool 結果 `isError: true` + `structuredContent.code`（`NOT_OWNER` / `NOT_FOUND` / `AMBIGUOUS` / `INVALID_ARGS` /
  `UNSUPPORTED`（BAT 太舊）/ `CONNECT_FAILED` / `AUTH_FAILED` / `FORBIDDEN` / `TIMEOUT` …）。
- **判斷依據**：只看 `isError`（MCP）或 exit code（helper CLI）。`content` 的摘要文字與 stdout 的格式不參與判斷。
  有些 client（例 Claude Code，T0158 實測）只把錯誤文字（例 `NOT_OWNER`）顯示給 agent，看不到 `structuredContent`（v5.3.1+ 補記）：
  判斷仍只看這是不是錯誤結果；code 改從錯誤文字取得，只用來挑給使用者的提示文字，取不到 code 也不影響「是否為錯誤」的判斷。
- **降級鏈**：MCP → helper CLI → 檔案（工單回報區、`bat-scripts.log`，位置見 § BAT 派發成功判讀規則 第 2 點）。MCP tool 不存在、`isError` 為 `UNSUPPORTED` / `CONNECT_FAILED`，
  就改用同功能的 helper CLI；沒有對應 helper 的查詢，就回到讀檔案（CT 現行做法）。降級不重試同一個 tool。
  錯誤結果（`isError: true`）**取不到 code**（`structuredContent` 看不到，錯誤文字裡也辨識不出已知 code）時，**視同可降級**（v5.3.2+）：
  同樣改用同功能的 helper CLI，沒有對應 helper 的查詢就回到讀檔案；結果以 helper 的 exit code 為準（真的是範圍／權限錯誤時，
  helper 也會以非 `0` 拒絕）。仍然不重試同一個 tool。取得到 code 時照上一句判斷，不變。
- **目前沒有任何 CT 規則必須使用 MCP**。所有 CT 流程都能只靠 helper CLI 與檔案完成；MCP 只是較省事的查詢通道。
  斷點 D（v5.5.0+，Worker 等待使用者）是唯一只能用 MCP 查的項目，它是告知／異常偵測、不是必要流程：MCP 不可用時斷點 D 不啟用、流程照常；
  定義、啟用條件與 `blocked` 欄位的使用見 [yolo-mode.md](yolo-mode.md) § 斷點 D，本節不複述。
  BAT 問答通道（v5.7.0+）的 `bat_wait_question` 有 helper `--wait-answer` 可降級，`bat_list_questions` 不能用時塔台改讀工單：
  兩者都不是必要條件（[yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › BAT 通道）。
  跨 session 選收件人（v5.9.0+）第 2 步的 `scope: towers` 只能用 MCP 查（helper 沒有 list 參數），不可用時跳過第 2 步、照該節往下走；
  面板的塔台 session 名稱提示同樣只在 MCP 可用時顯示。兩者都不是必要條件（[cross-project-coordination.md](cross-project-coordination.md)
  § 跨 session 選收件人、[memory-protocol.md](memory-protocol.md) § 塔台狀態面板）。
- **權杖**：`bat_read_output` 已遮罩權杖類字串，但遮罩是樣式比對、不是窮舉；不論來源，任何權杖值都不得寫進工單、回報區、日誌或
  commit message（同 § 範圍權杖與分頁角色 第 2 點）。
- 舊 BAT（`< 0.7.0-pre.2`）或 Settings 關閉 BAT MCP：分頁沒有這組 tool，直接走 helper CLI／檔案，行為與 v5.2.6 相同。

### 舊版 BAT 降級規則（帶前綴 `--workorder`）

塔台**不預先偵測 BAT 版本**，一律先照常送結構化派工，失敗才降級：

1. **照常送**：`--agent default --skill ct-exec --workorder <ID>`（其餘參數不變）
2. **判定舊版**：helper **exit code 非 0**，**且** stderr 指向 `--workorder` 值不合法
   （兩個條件都要成立）
3. **降級**：改送 `--prompt "/ct-exec <ID>"`，其餘參數（`--notify-id` / `--workspace` /
   `--cwd` / `--mode` / `--interactive`）一律不變
4. **明示**：塔台輸出必須寫出「已降級為 `--prompt` 派工」與降級原因（舊版 BAT 不接受前綴 ID），
   不得靜默降級——使用者要能看出這台機器的 BAT 該升級了
5. **單次 fallback**：降級只做一次。降級後仍失敗 → 走既有降級鏈（剪貼簿 / 手動指令），
   **不得靜默重試迴圈**

> 🔴 **明文禁止的偵測法：不得以「grep BAT 錯誤訊息字串是否存在」判定 BAT 版本。**
> BAT 塔台 §7 實證：修復後的錯誤訊息**仍含**原字串（`expected T followed by digits`），
> 只是後接 `, with an optional 2-4 char uppercase prefix, e.g. T0001 or CP-T0113` 被擴寫。
> 塔台本次亦複驗本機 `bat-terminal.mjs:235` 確認該字串仍在。
> 以「字串存在性」判版，在訊息被擴寫時會**反向誤判**（把已修復版判成舊版）。
> 要判版就 diff 或雜湊比對；本規則採「先送、失敗才降級」正是為了完全不必判版。

### 塔台分頁角色宣告（`--set-role tower`，v5.2.0+）

> 本小節是 `--set-role` 的**唯一權威定義**。`SKILL.md`、[tower-config.md](tower-config.md)、
> [yolo-mode.md](yolo-mode.md) 只放一句摘要並引用這裡，不複述規則。
> 介面契約以 BAT T0562 + T0565 為準（CT-T013 / D147 / D148），CT 不得更改參數名、值域或 exit code 語意。

Tower 啟動時向 BAT 宣告「這個分頁是塔台」以及目前生效的 auto-session 模式。BAT 據此把分頁標題設為
`<Agent 顯示名> · Tower`（例 `Claude CLI · Tower`，與 Worker 分頁 `Claude CLI · Worker · T####` 對應；
使用者改過名就保留），並以 `--mode` 判斷塔台分頁是否為 yolo 分頁。標題由 BAT 組出並套用，CT 只負責呼叫。

**1. 呼叫條件**

- 只在 **Tower session** 呼叫。
- `BAT_SESSION=1`，且 `BAT_REMOTE_PORT`、`BAT_REMOTE_TOKEN`、`BAT_TERMINAL_ID` 都存在。
- **不需要** `BAT_WORKSPACE_ID`，也**不需要** `BAT_TOWER_TERMINAL_ID`（與派工條件不同：本呼叫不建立分頁，只設定自己）。
- env 不齊或非 BAT 環境 → **略過，不嘗試**。
- env 判讀沿用上方 § 偵測條件 的 PowerShell 複查與 `shell env visibility mismatch` 規則，不另立判讀方式。

**2. 指令**

```bash
"${BAT_HELPER_NODE:-node}" "<helper>\\bat-terminal.mjs" --set-role tower --mode <yolo|ask|off|on> --agent <claude|codex>
```

PowerShell（不支援 `${VAR:-default}` 時的等價寫法，參數完全相同）：

```powershell
$n = if ($env:BAT_HELPER_NODE) { $env:BAT_HELPER_NODE } else { 'node' }
& $n "<helper>\bat-terminal.mjs" --set-role tower --mode <yolo|ask|off|on> --agent <claude|codex>
```

- `<helper>`：解析方式同上方 § 執行方式（`BAT_HELPER_DIR` 優先，未設定才 fallback 到 BAT 安裝目錄；Windows 路徑，不轉 POSIX）。
- `"${BAT_HELPER_NODE:-node}"` 與 PowerShell 的 `$n`：解析規則見上方 § 執行方式 的「Node 解析」（所有 helper 呼叫共用）。
- `--mode`：session > project > global > defaults 解析後**生效的** `auto-session` 值（見 [tower-config.md](tower-config.md) § 三層設定架構），只能是 `yolo` / `ask` / `off` / `on`。
- `--agent`：Claude Code 塔台 → `claude`；Codex 塔台 → `codex`。只是顯示名提示，分頁本身有 agent 設定時 BAT 以分頁為準。
- **不傳** `--terminal-id`（BAT 預設取 `BAT_TERMINAL_ID`，即塔台自己的分頁）。

**3. 時機**

Startup Protocol 完成 BAT 偵測與設定載入之後、顯示狀態面板之前呼叫一次。每次 `/control-tower`
／`$control-tower` 啟動都呼叫（同一分頁重複啟動也照常呼叫，BAT 端冪等）。

**4. 模式變更時再呼叫**

session 中 auto-session 的生效值改變時（`*config auto-session <m>`，含 `--save`；或任何改變生效值的流程），
用新的 `--mode` 再呼叫一次。不帶 `--mode` **不會清除** BAT 記錄的模式，所以每次呼叫都要帶 `--mode`。

**5. exit code**

| exit code | 意義 | 塔台處理 |
|---|---|---|
| `0` | 已處理（標題已套用，或因使用者命名而保留） | 面板記「已設定」 |
| 任何非 `0`（含 `3` NOT_FOUND、`1` 用法錯誤／連線失敗／權杖不允許／BAT 太舊） | 不支援 / 未設定 | 面板記「不支援（BAT 太舊）」；**不重試、不改用其他方式、不影響 Tower 啟動**；stderr 含 `Forbidden` 時多一句原因提示（見 § BAT 內部終端路由 › 範圍權杖與分頁角色 第 5 點） |

判斷**只看 exit code**，stdout / stderr 不參與判斷；唯一例外是 stderr 含 `Forbidden` 時用來挑選提示文字（不改變上表的處理），見 § BAT 內部終端路由 › 範圍權杖與分頁角色 第 5 點。成功時 stdout 的 `✓ Tower role set: <id>`、`  mode: <m>` 與
stderr 的 `set-role: <CODE>` 只當診斷參考。

**6. 狀態面板**

面板的 `分頁標題` 欄位（格式與值域）定義在 [memory-protocol.md](memory-protocol.md) § 塔台狀態面板。取值規則在本小節：
第 5 點的 exit code 決定 `已設定` / `不支援（BAT 太舊）`；依第 1 點 env 不齊或非 BAT 而未呼叫 → `略過（非 BAT）`。

**7. 禁止**

`ct-exec`、`ct-done`、`ct-status`、`ct-evolve`、`ct-insights`、`ct-fieldguide`、`ct-help` **不得呼叫**
`--set-role`。Worker 分頁的標題由 BAT 建立分頁時決定。

**8. 版本需求**

需要 BAT **`>= 0.6.1-pre.6`**（T0562 + T0565 同版；以實際發佈版號為準）。舊 BAT 的行為：

- 舊 helper：對 `--set-role` 印 `Unknown option`，exit `1`，**在建立分頁之前就結束**（不會誤開分頁）。
- 新 helper + 舊 BAT app：印 `set-role: UNSUPPORTED`，exit `1`。

兩者都依第 5 點視為不支援。安全白名單與防注入規則見下方 § 安全邊界。

### 對使用者描述分頁（v5.2.5+）

> 本小節是「塔台對使用者提到某個分頁時用什麼名稱」的**唯一權威定義**。[memory-protocol.md](memory-protocol.md)
> § 塔台狀態面板、[work-order-template.md](work-order-template.md) § 撰寫 verification 工單的驗收步驟 只引用這裡，不複述規則。

塔台在面板、提示、工單步驟或任何輸出中對使用者提到某個 BAT 分頁時，用使用者在 BAT UI 上看得到的**分頁標題**：

- 塔台分頁：`<Agent 顯示名> · Tower`（例 `Claude CLI · Tower`）。
- Worker 分頁：`<Agent 顯示名> · Worker · T####`（例 `Claude CLI · Worker · T0150`）。
- 使用者改過名的分頁：以使用者看到的名稱為準（BAT 會保留使用者命名，見上方 § 塔台分頁角色宣告）。
- 還沒有 CT 標題的分頁（例如使用者自己開、尚未啟動塔台的分頁）：用描述，例「一般分頁（使用者自己開的分頁）」。

terminal ID（`BAT_TERMINAL_ID`、`BAT_TOWER_TERMINAL_ID`、`--notify-id` 的值等 UUID）只用在日誌、狀態檔、證據欄位與 helper 參數；
使用者在 BAT UI 看不到 UUID，不得只用 UUID 指稱分頁。同一處需要留證據時，標題在前、ID 放括號，例
`Claude CLI · Worker · T0150`（`abc7b17b…`）。本規則只管對使用者的描述，不改變任何 helper 呼叫或參數。

分頁標題不是 Claude Code ListAgents 上的 session 名稱（v5.9.0+）：BAT `>= 0.7.1-pre.1` 派出的 claude Worker 在 ListAgents 上叫
`<工作區> · Worker · T####`（BAT 啟動時以 `--name` 加上，CT 派工命令不變、不用做任何事）；塔台與其他分頁的名稱、以及跨 session 傳訊怎麼選收件人，
只寫在 [cross-project-coordination.md](cross-project-coordination.md) § 跨 session 選收件人。

### Worker 完成自動通知

Worker（ct-exec / ct-done）收尾時，若偵測到下列 Worker notify 環境變數，自動執行通知：

- `BAT_TOWER_TERMINAL_ID`（由 Tower dispatch 的 `--notify-id "$BAT_TERMINAL_ID"` 注入）
- `BAT_REMOTE_PORT`
- `BAT_REMOTE_TOKEN`

```bash
"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-notify.mjs" \
  --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" [--submit] "<工單 ID> 完成"
```

`<工單 ID>` 是工單完整 ID（例 `LB-T0184`、`T0341`），含前綴、不得截短；送出前與 frontmatter `id` 比對。規則只寫在
[work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID。

若 `BAT_HELPER_DIR` 未設定，fallback：

```bash
"${BAT_HELPER_NODE:-node}" "C:\\Program Files\\BetterAgentTerminal\\resources\\scripts\\bat-notify.mjs" \
  --source "<工單 ID>" --target "$BAT_TOWER_TERMINAL_ID" [--submit] "<工單 ID> 完成"
```

`--submit` 僅限 YOLO 自動送出。各模式（`on` / `yolo` / `ask` / `off` / 缺值）是否預填、是否送出，以 `ct-exec/SKILL.md` § BAT Notify And Fallback 為準（D017），此處不複述。

通知管道：
1. **PTY write**：Tower 終端輸入行預填完成訊息（不帶 `\r`，不自動送出）
2. **Toast**：BAT UI 右上角彈窗通知
3. **Badge 冒泡**：終端縮圖 badge → Workspace 頁籤 badge（跨 workspace 可見）

### 路由優先級

BAT 路由插入現有降級鏈的**最高優先位置**：

```
1. BAT_SESSION=1 → bat-terminal.mjs（BAT 內部終端）    ← 新增
2. $WT_SESSION 存在 → wt -w 0 nt（Windows Terminal）
3. $TERM_PROGRAM = vscode → 剪貼簿
4. 其他 → 文字提示
```

### 依賴的 BAT 基礎設施

| 元件 | 說明 |
|------|------|
| `BAT_REMOTE_PORT` / `BAT_REMOTE_TOKEN` | RemoteServer WebSocket 連線資訊（pty-manager 自動注入）；`BAT_REMOTE_TOKEN` 自 BAT `>= 0.7.0-pre.1` 起為分頁專屬範圍權杖，見 § 範圍權杖與分頁角色 |
| `BAT_TERMINAL_ID` | 每個 PTY 的 UUID（pty-manager 自動注入） |
| `BAT_WORKSPACE_ID` | Tower 當前 workspace UUID，派發時傳給 `--workspace` |
| （無對應 env var） | `--cwd` 的值不是 BAT 注入的，取自塔台自己的專案根目錄（`git rev-parse --show-toplevel`） |
| `BAT_TOWER_TERMINAL_ID` | Worker notify 目標 Tower PTY ID，由 `--notify-id "$BAT_TERMINAL_ID"` 注入 Worker |
| `BAT_HELPER_DIR` | BAT 安裝目錄下的 `scripts` 子目錄；helper 路徑優先來源 |
| `scripts/bat-terminal.mjs` | 零依賴 Node.js CLI，WebSocket invoke 建立終端 |
| `scripts/bat-notify.mjs` | 零依賴 Node.js CLI，雙管道通知（PTY write + terminal:notify） |
| `bat-terminal.mjs --set-role tower --mode <m>` | v5.2.0+ 塔台分頁角色宣告；需 BAT **`>= 0.6.1-pre.6`**（T0562 + T0565），更舊的 BAT 回 exit `1` 視為不支援。見 § 塔台分頁角色宣告 |
| `BAT_HELPER_NODE` | 遠端分頁的 bundle node 路徑（本機無此變數 → `node`）；所有 helper 呼叫都用，規則見 § 執行方式 的「Node 解析」 |
| `CT_HOME` / `CT_WORKTREE` / `CT_WORKTREE_BRANCH` / `CT_WORKTREE_BASE` | v5.3.0+ 隔離派出的 Worker 分頁才有；需 BAT **`>= 0.7.0-pre.2`**。見 § worktree 隔離派工 |
| `bat-terminal.mjs --worktree-status` / `mcp__bat__*` | v5.3.0+ 唯讀查詢；需 BAT **`>= 0.7.0-pre.2`**；分頁關閉後仍可查 `--worktree-status`（`source`）需 BAT **`>= 0.7.0-pre.4`**（v5.4.0+）。見 § BAT MCP 唯讀 tool 與 [merge-workorder.md](merge-workorder.md) |
| `bat-terminal.mjs … --wait-started <ms>` / MCP `agentStarted` | v5.6.0+ Worker 啟動確認；需 BAT **`>= 0.7.0-pre.6`**（T0600）。更舊的 helper 回 exit `1` + `Unknown option '--wait-started'`，依 § Worker 啟動確認 第 5 點降級。見 § Worker 啟動確認 |
| codex 分頁的 OSC 7501：`blockedDetection: osc`、`blockedReason: input`、codex 的 `--wait-started` / `agentStarted` | v5.8.0+；需 **BAT `>= 0.7.0-pre.9`**（T0621）且 codex `>= 0.163.0`。舊 BAT（≤ `0.7.0-pre.8`）或較舊 codex → `none` / `null` / `started: unknown`，行為同 v5.7.2。見 § Worker 啟動確認 與 [yolo-mode.md](yolo-mode.md) § 斷點 D |
| `bat-notify.mjs --ask` / `--wait-answer` / `--cancel-question`、`bat-terminal.mjs --answer`、MCP `bat_wait_question` / `bat_list_questions`、`blockedReason: tower` / `pendingQuestions` | v5.7.0+ yolo Worker 問塔台的 BAT 通道；需 BAT **`>= 0.7.0-pre.7`**（CT-T019／T0607／T0608／T0611）。更舊的 BAT 降級回工單檔往返。參數、exit code、欄位與版本判定見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › BAT 通道 |
| ListAgents 上的 claude 分頁名稱（`--name`）、MCP `claudeSessionName` / `claudeSessionId`、`bat_list_terminals` `scope: towers`、「以塔台開啟 Claude」 | v5.9.0+ 跨 session 選收件人與面板提示；需 BAT **`>= 0.7.1-pre.1`**（CT-T021／PLAN-050／T0641–T0644）。舊 BAT（≤ `0.7.0-pre.9`）沒有名稱、沒有這兩個鍵、`scope: towers` 回 `INVALID_ARGS`，行為同 v5.8.1。見 § BAT MCP 唯讀 tool 與 [cross-project-coordination.md](cross-project-coordination.md) § 跨 session 選收件人 |
| RemoteServer | BAT 啟動後自動運行的 WebSocket server |
| `terminal:created-externally` | 外部建立的終端 → UI 同步（縮圖 + xterm） |
| `terminal:notify` | 通知事件 → Toast + Badge 冒泡 |

### 向下相容

- 非 BAT 環境：所有 BAT env vars 不存在 → 跳過 BAT 路由 → 走現有降級鏈
- BAT RemoteServer 未啟動：`bat-terminal.mjs` 連線失敗 → timeout 3 秒 → fallback 到下一級
- `--prompt "/ct-exec T####"` 這條路徑仍受支援：BAT app 在 resolved agent 為 Codex 系列時會把它 normalize 為 `$ct-exec T####`。**兩個方向都靠它**——舊版 Tower skill 一直送 `--prompt`（BAT 據此保護未升級的塔台），而現行塔台在§ 舊版 BAT 降級規則觸發時也會主動改送 `--prompt`。
  ⚠️ 因此本條**不是**「不該用 `--prompt`」的意思。結構化的 `--skill` + `--workorder` 是**首選**，`--prompt` 是**受支援的降級路徑**，不是 deprecated pattern。

## BAT 派發成功判讀規則（唯一信號源）

塔台用 `bat-terminal.mjs` 派發 sub-session 時，唯一可信的「派發成功」信號為以下兩者之一：

✅ **信任**（以 1 為主規則；2 是事後查證用）：
1. helper 程序（`bat-terminal.mjs`）exit code 為 `0`
2. `bat-scripts.log`（NDJSON，一行一筆）出現 helper 端的成功紀錄：
   `"script":"bat-terminal"`、`"event":"terminal-created"`、`"result":"ok"`
   （寫入處：BAT `scripts/bat-terminal.mjs` 成功分支；失敗分支同一事件的 `result` 為 `"error"` / `"refused"` / `"false"`，且 exit code 為 `1`）

   **檔案位置**（v5.3.1+；本段是 CT 內 `bat-scripts.log` 位置的唯一權威，其他提到這個 log 的地方只引用這裡）。
   解析順序與 BAT helper 相同（BAT repo `CLAUDE.md` § Helper scripts 的 userData，T0481）：
   1. `BAT_HELPER_LOG_DIR` 有值**且為絕對路徑** → `<BAT_HELPER_LOG_DIR>\bat-scripts.log`（headless bat-server 的設定；本機 PTY 不注入）。
      相對路徑忽略，往下走第 2 步（與 `BAT_USER_DATA` 的規則對稱）。v5.3.2+ 補記：BAT `CLAUDE.md` § Helper scripts 目前只對
      `BAT_USER_DATA` 寫了絕對路徑要求，這一點以 BAT 原始碼為準（`scripts/_bat-logger.mjs` `resolveLogPath()`：
      `if (overrideDir && isAbsolute(overrideDir))`，T0160 實測 `:83`）
   2. 否則看 `BAT_USER_DATA`（須為絕對路徑；相對路徑忽略）→ `<BAT_USER_DATA>\Logs\bat-scripts.log`
   3. 兩者都沒有可用的值（未設定或不是絕對路徑）→ 那是 BAT 舊版（T0481 前）或在 BAT 外執行，BAT helper 才會退回自己推測的位置。CT 不自行推測，
      視為「讀不到 log」，依各處既有規則退回 exit code／stdout。

   實測（T0158，BAT 0.7.0-pre.2 本機分頁）：`BAT_HELPER_LOG_DIR` 未設定，log 在 `$BAT_USER_DATA\Logs\bat-scripts.log`。
   CT 對這個 log 只讀：不得寫入、截斷或刪除。

> 📌 v5.1.0 更正：v5.0.1 ~ v5.0.9 此處寫的是 key=value 形式（`terminal-created` 後接 `result` 等於 `true`），不是 `bat-scripts.log` 的寫法。
> 該形式出自 BAT app 主行程日誌（`Logs/debug-*.log` 的 `[remote][terminal] terminal-created id=<id> result=<boolean> …` 行）；
> `bat-scripts.log` 另有一筆由 app 端鏡像的同名事件（`"script":"remote-server"`，`"result":true` 為布林）。
> 兩者都是 app 端紀錄，與 helper 的 exit code 不是同一個信號；判讀以上方 1、2 為準。

❌ **不解析**：stdout 的 `Terminal created: ...` 訊息(此為 cosmetic 輸出，無語意)

> 📌 exit `0` 只代表分頁已建立，不代表 Worker 已啟動。v5.6.0 起派工帶 `--wait-started`，「Worker 是否已啟動」改由 § Worker 啟動確認
> 判斷（取代 v5.5.1 在此處的暫時補充）。上方判讀規則不變：派工是否成功仍以 exit code 為主，`started:` 行只在帶參數時解析，
> `bat-scripts.log` 的判讀不變。

**派發失敗（exit 非 `0`）**：走 § 降級鏈，不自動重派。stderr 含 `Forbidden` 或 `RECOVERY_PENDING` 時降級訊息多一句原因提示；規則見 § BAT 內部終端路由 › 範圍權杖與分頁角色 第 5、6 點，此處不複述。
隔離工單（`--isolation worktree`，v5.3.0+）的 exit `7` 與 exit 非 `0` 不走降級鏈，改依 § BAT 內部終端路由 › worktree 隔離派工 第 3、4 點。
帶 `--wait-started` 的派工（v5.6.0+）有兩個例外，都依 § Worker 啟動確認：exit `8` **不是**派發失敗（分頁已建立），不走降級鏈、不重派；
exit `1` 且 stderr 含 `Unknown option '--wait-started'`（沒有建立分頁）時去掉該參數重派一次。

### 反 anti-pattern

- ❌ **看到 `Terminal created: null` 就降級剪貼簿（誤判）**
  舊版 BAT 在 `--skill --workorder` 模式下 stdout 印的是 `${command}`，該模式 command=null 屬正常輸出格式，**terminal 實際已建立成功**（看 exit code + log 即可確認）。BAT 自 `v0.5.1`（commit `abdd1cf1`，BUG-020 / T0110）起改印 `✓ Terminal created: <terminalId>`，但更早的版本仍有此行為。
- ❌ **用 `curl http://127.0.0.1:9876/health` 判定 BAT 健康**
  該 port 為 **TLS/WSS** endpoint，plaintext HTTP probe 必然回 Empty reply。**不是 server 故障，是 protocol 不匹配**。

### 替代健康檢查（若需要）

- 若 BAT 升級後提供 HTTPS `/health` 或 `bat-health.mjs` helper → 屆時改寫此規則
- 在那之前，依靠 process check（`tasklist | grep BetterAgent`、Linux/macOS `pgrep`）+ `bat-scripts.log` 內容

### 來源

BUG-020 翻盤事件（專案 B 2026-05-07，T0729 翻盤調查 / T0731 _local-rules.md Layer 3 落地 / CP-T0733 系統層升級）。CT v5.0.1 patch release 將此規則納入系統層。

## Worker 啟動確認（`--wait-started`，v5.6.0+）

> 本節是派工參數 `--wait-started`（何時帶、四種結果、`started:` 行解析、舊 BAT 降級）的**唯一權威定義**。`SKILL.md`、
> [yolo-mode.md](yolo-mode.md) 與本檔其他小節只放摘要並引用這裡，不複述規則。
> 介面契約以 BAT T0600 為準（CT-T018 / D039 / D040；BAT `CLAUDE.md`「Worker 啟動確認（T0600，D154）」節與
> `docs/agent-guide/worker-launch-confirmation.md`），CT 不得更改參數名、值域、輸出格式或 exit code 語意。需 BAT **`>= 0.7.0-pre.6`**。
> codex Worker 的啟動信號（v5.8.0+）以 BAT T0621「介面契約」C-3、C-5、C-6 與 `worker-launch-confirmation.md`「codex（OSC 7501，T0621）」節為準（CT-T020），
> 需 **BAT `>= 0.7.0-pre.9`** 且 codex `>= 0.163.0`。

**1. 為什麼**

helper 在建立 PTY 後就回 exit `0`，啟動指令約 500 ms 後才寫入，所以 exit `0` 不代表 Worker 已啟動（BAT BUG-151）。
BAT `>= 0.7.0-pre.6` 讓 claude 的 `SessionStart` hook 回報「已啟動」，helper 帶 `--wait-started <ms>` 時會等這個信號再結束。
v5.8.0+：BAT `>= 0.7.0-pre.9` 對 codex `>= 0.163.0` 的 Worker 以 codex 自己送的第一個 OSC 7501 當同一個信號（BAT T0621），
helper 的輸出格式與 exit code 語意不變。

**2. 何時帶**

- 派工（`--skill ct-exec|ct-done` + `--workorder`，含 `--isolation worktree`）在 § BAT 內部終端路由 › 執行方式 的既有參數**最後**加
  `--wait-started 30000`，條件只有一個：**本塔台 session 尚未判定「不支援 `--wait-started`」**（第 5 點）。
- 值固定 `30000`（BAT 建議值）。不設 config（D040）：它只影響派工那一次 helper 等多久。
- 不帶的情況：本 session 已判定不支援；§ 舊版 BAT 降級規則 的 `--prompt` 改送；`--close-worker`、`--set-role`、`--worktree-status`
  （BAT 對後三者併用回用法錯誤 exit `1`）。不帶時的命令、輸出與 exit code 和 v5.5.1 完全相同（BAT 契約：不帶參數時輸出與 exit code 完全不變）。
- `--notify-id` 照 § 執行方式 傳塔台自己的 `$BAT_TERMINAL_ID`；BAT 規定帶 `--wait-started` 時必須有它（塔台只能查自己派出的 Worker）。
- codex Worker 照同一條件帶（v5.8.0+ 起對 codex 也可能回 `started: <時間>` 或 exit `8`，見第 3、4 點）。
  BAT `>= 0.7.0-pre.9` 派 codex Worker 時會自己加 `-c check_for_update_on_startup=false`（避免更新提示擋住 Worker，BAT T0621 C-6）：
  由 BAT 加、CT 不用加，CT 的派工命令不變。

**3. 判讀**

派工是否成功仍以 exit code 為主（§ BAT 派發成功判讀規則）。帶參數時，helper 在既有輸出（`✓ Terminal created: <id>` 等）之後，
stdout **最後**多一行 `started:`；塔台取 stdout 中最後一個符合 `/^\s*started: (\S+)\s*$/m` 的行：

| exit | `started:` 行 | 意義（BAT 權威） | 塔台處理 |
|---|---|---|---|
| `0` | `started: <ISO 8601 UTC>` | claude 已執行 `SessionStart`，或（v5.8.0+）codex 已送第一個 OSC 7501（時間 = BAT 收到回報的時間） | 派工成功、Worker 已啟動。時間記進派工紀錄當證據 |
| `0` | `started: unknown` | **無法判定**：codex 低於 `0.163.0` 或版本確認不到（含 Windows 上 PATH 第一個是 npm shim `codex.cmd`、舊 BAT 上的 codex）、raw command、自訂 CLI、hooks 未注入或被 claude 設定關閉、BAT 無法回答等；BAT 依契約對這些 codex 絕不回 `unconfirmed`。stderr 另有一行 `wait-started: <CODE>` | 派工成功，照現行流程：以 Worker 回報判斷。**不是失敗**：不重派、不提示異常。`<CODE>` 只當診斷記錄，不參與判斷 |
| `8` | `started: unconfirmed` | 分頁**已建立**，但 `<ms>` 內未確認啟動，或分頁先結束；stderr `create: LAUNCH_UNCONFIRMED`；**分頁不關閉** | 見第 4 點。**不重派** |
| `1` | — | 派工失敗或用法錯誤 | 照 § BAT 派發成功判讀規則 的 exit 非 `0` 處理；只有第 5 點的情形例外 |

- 其他既有 exit code（`3` / `4` / `5` / `6` / `7`）語意不變，照各自既有規則；`8` 只在帶 `--wait-started` 時出現。
- exit `0` 但 stdout 找不到 `started:` 行 → 視同 `unknown`（照現行流程）。exit `8` 的處理不看 `started:` 行是否存在。
- `started: <時間>` 只代表 claude 已執行 `SessionStart`（codex：已送第一個 OSC 7501），不代表第一個 prompt 已送出或 ct-exec 已讀工單；工單是否開工仍以 Worker 寫的
  `started_at` / `status` 為準。

**4. exit `8`：分頁在、未確認啟動**

- **不重派、不走 § 降級鏈**。分頁沒有關閉，重派會讓同一張工單出現兩個 Worker。
- 派工仍算已派出（分頁存在），派工紀錄記 `started: unconfirmed`，塔台照常等 Worker 回報。
- MCP 可用（§ BAT MCP 唯讀 tool）→ 用 `bat_read_output` 看該 Worker 分頁的輸出，把看到的狀況（例：claude 已在執行、啟動指令報錯、codex 停在啟動畫面）
  一行告訴使用者。MCP 不可用 → 以分頁標題提醒使用者去看，例：
  `T#### 的 Worker 分頁已建立，但 30 秒內未確認啟動，請到「Claude CLI · Worker · T####」分頁查看`（標題寫法見 § 對使用者描述分頁）。
- 要不要重派由使用者決定；塔台不自動重派，也不替使用者在該分頁輸入任何東西。使用者決定重派時，派工前先照
  [work-order-system.md](work-order-system.md) § 回報處理流程 › 重派前回收舊 Worker 分頁（v5.12.0+）回收這個分頁。
- 可能是誤報：專案設定（`<cwd>/.claude/settings[.local].json`）、MDM／server-managed policy 等 BAT 讀不到的 hooks 關閉，會讓
  `agentStarted` 永遠 `false`、期限到時 exit `8`，但 Worker 其實正常執行（BAT 已知限制）。這正是 exit `8` 不能重派的另一個原因。
- codex Worker（v5.8.0+）最常見的 exit `8` 原因是 codex 卡在啟動前畫面：未信任的 git repo 的「Trust this folder?」、「Hooks need review」，
  或可能的更新提示（BAT 權威）；這些畫面不送 OSC 7501，所以也不會變成 `blocked`／斷點 D。處理照上方：不重派，有 MCP 看 `bat_read_output`，
  否則請使用者看分頁標題對應的分頁。另一個誤報來源：BAT 以主行程的 PATH 判定 codex 版本，分頁 shell 實際跑到較舊的 codex 時也可能 exit `8`
  （BAT 已知限制），同樣不重派。
- 斷點 D 不受影響：exit `8` 不是 yolo 的斷點，不暫停 yolo 流程。

**5. 舊 BAT 降級（`Unknown option '--wait-started'`）**

- **條件**（兩個都要成立）：exit `1`，**且** stderr 含 `Unknown option '--wait-started'`。這是 BAT `< 0.7.0-pre.6` 的 helper 對未知選項的既有規則，
  此時**沒有建立分頁**。
- **處理**：去掉 `--wait-started 30000`、其餘參數（含 `--isolation worktree`）一律不變，**重派一次**；本塔台 session 記為「不支援 `--wait-started`」，
  之後的派工不再帶。重派的結果照 § BAT 派發成功判讀規則 判讀（與 v5.5.1 相同）；重派仍 exit 非 `0` → 照該次的既有規則
  （一般工單走 § 降級鏈，隔離工單依 § worktree 隔離派工 第 3、4 點），不再重試。
- 這次重派不是「降級成非隔離」：`--isolation worktree` 保留，所以不受 § worktree 隔離派工 第 4 點「不自動送出降級派工」限制。
  去掉參數後若改由 `--isolation` 或 `--workorder` 的未知／不合法值失敗，就照那兩條既有規則處理；各條降級各自最多一次。
- 「不支援」**只記在塔台 session 記憶**：不寫 config、不寫 `_tower-state.md`、狀態面板 BAT 列不新增欄位或值
  （[memory-protocol.md](memory-protocol.md) § 塔台狀態面板）。BAT 可能在兩個 session 之間升級；新 session 從帶參數開始，
  舊 BAT 最多多一次不建立分頁的 exit `1`。
- 塔台可在派工訊息附一句「BAT 不支援 Worker 啟動確認（需 `>= 0.7.0-pre.6`），本 session 之後不帶 `--wait-started`」，不算錯誤提示。
- 新 helper 對上不支援的 BAT 主程式（helper 與主程式版本不一致）→ exit `0` + `started: unknown`（`wait-started: UNSUPPORTED`），照第 3 點的 `unknown` 處理，
  不記「不支援」。

**6. stderr 的使用範圍**

- 判斷仍以 exit code 為主：exit code 決定「分頁有沒有建立、算不算派工失敗」，stderr 不改變這個判斷。
- stderr 只用在兩處，都不決定成敗：第 5 點用 `Unknown option '--wait-started'` **選擇降級路徑**（去參數重派一次，還是照既有規則）；
  `wait-started: <CODE>` 只當診斷記錄。`create: LAUNCH_UNCONFIRMED` 不參與判斷（exit `8` 已經足夠）。
- 與既有原則的關係：比照 § BAT 內部終端路由 › 範圍權杖與分頁角色 第 5 點的 `Forbidden`（stderr 只挑提示文字）與 § 舊版 BAT 降級規則
  （exit 非 `0` **且** stderr 指向 `--workorder` 才降級），這是 CT 少數允許看 stderr 的情形之一，範圍只到「選哪條降級路徑」。
- 不違反 § 舊版 BAT 降級規則 的「不得以錯誤訊息字串判版」：那條禁止的是同一字串新舊版都會出現、會反向誤判的情況；認得
  `--wait-started` 的 helper 不會印這個 Unknown option 訊息。萬一誤判，代價只是本 session 不帶參數，行為回到 v5.5.1。

**7. 已知限制**（BAT 權威，細節以 BAT 為準）

- 有信號的是 claude-cli Worker（hooks）與（v5.8.0+）codex `>= 0.163.0` 的 Worker（OSC 7501，需 BAT `>= 0.7.0-pre.9`）；
  codex 低於 `0.163.0`、BAT 確認不到 codex 版本、舊 BAT（≤ `0.7.0-pre.8`）上的 codex、自訂 CLI、raw command → `unknown`（MCP `agentStarted: null`），
  與 v5.7.2 相同。
- 時間是 BAT 收到回報的時間，不是 claude／codex 程序啟動時間。
- MCP 的 `agentStarted` 以 PTY 為單位、只記第一次 `SessionStart`（codex：第一個 OSC 7501）；BAT 重開（Terminal Server 存活）後重開前的值會遺失、回 `false`；
  codex 分頁則由重播內容補掃，有 OSC 7501 就恢復為 `true`（時間 = 掃描時間，BAT T0621 C-7）。
  `--wait-started` 只在派工當下使用，不受影響。

## 降級鏈

```
BAT 內部終端（BAT_SESSION=1）
  ↓ 跳過（非 BAT 環境）
開新終端分頁
  ↓ 失敗（終端環境未知）
寫入剪貼簿
  ↓ 失敗（剪貼簿工具不可用）
文字複製提示（永遠顯示）
```

**靜默降級**：降級過程不顯示錯誤訊息，不打擾使用者。**例外**：BAT helper exit 非 `0` 且 stderr 含 `Forbidden`（在 Worker 分頁啟動了塔台）或 `RECOVERY_PENDING`（BAT 的 Recovery 提示尚未回答，僅派工）時，要顯示一行原因提示；降級本身照常、不重試、不自動重派，判斷仍只看 exit code，見 § BAT 內部終端路由 › 範圍權杖與分頁角色 第 5、6 點。

**文字提示永遠顯示**：即使 `auto-session=on` 且成功開新分頁，文字提示仍然顯示（使用者可能在不同環境重新查看）。

## 安全邊界

### Bash 白名單

塔台「嚴格禁止」的**唯一例外**——僅允許以下白名單指令：

| 用途 | 指令 | 平台 |
|------|------|------|
| 開新終端分頁 | `wt -w 0 nt <agent-cli> "/ct-exec T####"` | Windows Terminal |
| 開新 CLI session | `<agent-cli> "/ct-exec T####"` | 跨平台 |
| 寫入剪貼簿 | `pwsh -Command "Set-Clipboard -Value '/ct-exec T####'"` | Windows（優先） |
| 寫入剪貼簿 | `echo /ct-exec T#### \| clip` | Windows（降級，僅英文） |
| 寫入剪貼簿 | `echo "/ct-exec T####" \| pbcopy` | macOS |
| 寫入剪貼簿 | `echo "/ct-exec T####" \| xclip -selection clipboard` | Linux |
| BAT 內部終端 | `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" --cwd "<專案根目錄>" --mode <yolo\|ask\|off\|on> [--interactive\|--no-interactive] --agent default --skill ct-exec --workorder T####` | BAT（Tower dispatch；使用 BAT 預設 Agent；未設 `BAT_HELPER_DIR` 時 fallback 到 `C:\\Program Files\\BetterAgentTerminal\\resources\\scripts\\bat-terminal.mjs`） |
| BAT 內部終端 | `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --notify-id "$BAT_TERMINAL_ID" --workspace "$BAT_WORKSPACE_ID" --cwd "<專案根目錄>" --mode <yolo\|ask\|off\|on> [--interactive\|--no-interactive] --agent default --skill ct-done --workorder T####` | BAT（Tower dispatch；使用 BAT 預設 Agent；未設 `BAT_HELPER_DIR` 時 fallback 到 `C:\\Program Files\\BetterAgentTerminal\\resources\\scripts\\bat-terminal.mjs`） |
| BAT 隔離派工 | 上兩列的指令尾端加 `--isolation worktree` | BAT（v5.3.0+，僅工單有 `isolation: worktree` 時；見 § BAT 內部終端路由 › worktree 隔離派工） |
| BAT 派工啟動確認 | 上三列的指令最尾端加 `--wait-started 30000` | BAT（v5.6.0+，BAT `>= 0.7.0-pre.6`；本塔台 session 未判定「不支援 `--wait-started`」時一律加，已判定就不加、指令與上三列相同；見 § Worker 啟動確認） |
| 回收 Worker 分頁 | `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --close-worker T#### --notify-id "$BAT_TERMINAL_ID" --delay-ms <worker_close_delay × 1000>` | BAT（v5.1.0+，收單後；僅 `worker_auto_close: done` 時，條件與 exit code 處理見 [work-order-system.md](work-order-system.md) § 回報處理流程；helper 路徑 fallback 同上）。v5.12.0+ 也用於重派前（`--delay-ms 0`，不受 `worker_auto_close` 影響；見 [work-order-system.md](work-order-system.md) § 重派前回收舊 Worker 分頁） |
| 回收隔離 Worker 分頁 | 上一列的指令尾端加 `--worktree keep`（收單時）或 `--worktree remove`（合併完成後） | BAT（v5.3.0+，僅隔離工單；見 [work-order-system.md](work-order-system.md) § 收單後回收 Worker 分頁 與 [merge-workorder.md](merge-workorder.md) § 合併完成後清理） |
| 查詢隔離 Worker 狀態 | `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --worktree-status T#### --notify-id "$BAT_TERMINAL_ID"` | BAT（v5.3.0+，唯讀；見 [merge-workorder.md](merge-workorder.md) § 合併判準資料來源） |
| 塔台直接合併（模式 ①） | [merge-workorder.md](merge-workorder.md) § 直接合併的做法 列出的 git 指令（整合 worktree `--no-ff`、`main` 只 `--ff-only`） | git（v5.3.0+，僅直接合併五條判準全部成立時；其他 git 寫入操作不在此列） |
| 答覆 Worker 的 BAT 題目 | `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --answer <questionId> --notify-id "$BAT_TERMINAL_ID" [--choice <n>]`，答覆文字只從 stdin 傳入 | BAT（v5.7.0+，BAT `>= 0.7.0-pre.7`，僅 yolo 塔台收到 `T#### 提問` 時；用法與 exit code 見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › 塔台端 第 3 點；helper 路徑 fallback 同上） |
| 宣告塔台分頁角色 | `"${BAT_HELPER_NODE:-node}" "$BAT_HELPER_DIR\\bat-terminal.mjs" --set-role tower --mode <yolo\|ask\|off\|on> --agent <claude\|codex>` | BAT（v5.2.0+，僅 Tower session；啟動時與 auto-session 生效值改變時；條件、PowerShell 寫法與 exit code 處理見 § 塔台分頁角色宣告；helper 路徑 fallback 同上） |

### 安全規則

- **僅限白名單指令**：不得執行任何其他 Bash 操作
- **`BAT_REMOTE_TOKEN` 的值**（v5.2.4+）：不得輸出、記錄或作為參數傳遞（helper 自行從環境變數讀取）；需要記錄時只寫「已設定」。見 § BAT 內部終端路由 › 範圍權杖與分頁角色 第 2 點
- **helper 執行檔**（v5.2.1+）：BAT helper 列的開頭只允許 `"${BAT_HELPER_NODE:-node}"`（或 PowerShell 等價的 `$n`），即 `BAT_HELPER_NODE` 的值或字面 `node`，規則見 § 執行方式 的「Node 解析」；不得以其他執行檔或使用者輸入取代
- **僅限工單指令內容**：指令參數僅包含 `/ct-exec T####` 或 `/ct-done T####`，或依 § BAT 內部終端路由 › 依安裝方式的 skill 呼叫字串（v5.14.0+）替換後的 Codex 寫法（`$ct-exec T####`、`$ct:ct-exec T####`，`ct-done` 同理，一律單引號）；BAT 內部終端僅傳 `--skill ct-exec|ct-done --workorder T####`（另可依下方規則加 `--isolation worktree`、`--wait-started 30000`）；回收 Worker 分頁僅傳 `--close-worker T####`（v5.1.0+）
- **防注入**：不得傳入任意使用者輸入作為參數。工單編號**僅允許符合 [work-order-system.md](work-order-system.md) § 工單 ID 格式（權威定義）之權威正則的值，其餘一律拒絕**——不正規化、不截斷、不修補，直接拒絕派工並回報。本處不複述該正則，以免與權威定義漂移（v5.0.6 收斂前正是複述導致全庫立場牴觸）。⚠️ 合法值**包含帶前綴的 ID**（如 `CP-T0113`），拒絕帶前綴 ID 是錯誤實作
- `--mode` 參數值僅允許 `yolo` / `ask` / `off` / `on`（正則 `^(yolo|ask|off|on)$`），防注入
- `--interactive` / `--no-interactive` 為 flag（無參數），僅用於研究型工單互動旗標；v5.5.0+ yolo 派工固定 `--no-interactive`、不帶 `--interactive`（見 [yolo-mode.md](yolo-mode.md) § 啟動詢問（G3 互動旗標））
- `--close-worker`（v5.1.0+）：工單編號同樣只接受上方「防注入」所指的權威正則，不另立規則；`--delay-ms` 只允許 `0`–`300000` 的整數（非整數或超出範圍 → 不呼叫）；`--notify-id` 只傳塔台自己的 `$BAT_TERMINAL_ID`；**不得與建立分頁的參數（`--prompt` / `--skill` / 位置參數等）同時使用**（BAT PLAN-041 介面契約原文）
- `--isolation`（v5.3.0+）：值只收 `worktree`；只能搭配 `--skill` + `--workorder`（不得與 `--prompt`、位置參數或 `--close-worker` 同時使用）（BAT T0583 介面契約）
- `--wait-started`（v5.6.0+）：值只收 `0`–`120000` 的整數，CT 固定用 `30000`（非整數或超出範圍 → 不呼叫）；必須搭配 `--notify-id`（只傳塔台自己的 `$BAT_TERMINAL_ID`）；
  只能用在派工（`--skill ct-exec|ct-done` + `--workorder`，可與 `--isolation worktree` 併用）；**不得與 `--close-worker` / `--set-role` / `--worktree-status` 同時使用**
  （BAT T0600 介面契約：併用或缺 `--notify-id` 為用法錯誤 exit `1`）。BAT 另接受 `--prompt` 與 raw command 模式，CT 不使用（§ 舊版 BAT 降級規則 的 `--prompt` 改送不帶此參數）
- `--worktree`（v5.3.0+）：值只收 `keep` / `remove` / `archive`，且只在 `--close-worker` 模式使用；CT 規則只用 `keep` 與 `remove`（`archive` 會把分支改名，合併前不得用）
- `--worktree-status`（v5.3.0+）：工單編號同樣只接受上方「防注入」所指的權威正則；帶工單編號時 `--notify-id` 只傳塔台自己的 `$BAT_TERMINAL_ID`；不得與建立分頁的參數、`--close-worker`、`--delay-ms`、`--worktree`、`--set-role` 同時使用（BAT T0585 介面契約）
- `--set-role`（v5.2.0+）：值只收 `tower`；`--mode` 只收 `yolo` / `ask` / `off` / `on`（同上方正則）；`--agent` 只收 `claude` / `codex`；**不得與建立分頁的參數（`--prompt` / `--skill` / `--workorder` / `--cwd` / `--workspace` / `--notify-id` / `--interactive` / 位置參數等）或 `--close-worker` / `--delay-ms` 同時使用**（BAT T0562 / T0565 介面契約）
- `--answer`（v5.7.0+）：`<questionId>` 只收 `bat_list_questions` 回傳的 id（BAT 格式 `^q-[0-9a-f]{8}-[0-9a-f]{16}$`，不符 → 不呼叫）；`--notify-id` 只傳塔台自己的 `$BAT_TERMINAL_ID`；
  `--choice` 只收 `1` 起算、不超過該題選項數的整數；🔴 答覆文字只走 stdin，不得放進命令列參數；不得與建立分頁的參數、`--close-worker`、`--set-role`、`--worktree-status` 同時使用（BAT T0608 介面契約）。
  Worker 端的 `bat-notify.mjs --ask` / `--wait-answer` / `--cancel-question` 屬 `ct-exec`，**不在**塔台白名單內，塔台不得執行
  （用法見 [yolo-mode.md](yolo-mode.md) § Worker 向塔台提問 › Worker 端 第 3 點）
- **白名單以外的 Bash 操作仍然嚴格禁止**

## 回報快捷

### 塔台端（派發時）

工單派發時同時顯示（`<工單 ID>` 寫工單完整 ID，含前綴）：
```
📋 回塔台回報時輸入：<工單 ID> 完成
```

### ct-exec 端（收尾時）

ct-exec 工單收尾後自動將回報文字寫入剪貼簿（見 ct-exec SKILL.md）（`<工單 ID>` = 工單完整 ID，含前綴、不得截短，規則見 [work-order-system.md](work-order-system.md) § 回報與通知用的工單 ID）：
- `DONE` → 剪貼簿寫入「<工單 ID> 完成」
- `PARTIAL` → 剪貼簿寫入「<工單 ID> 部分完成」
- `FAILED` → 剪貼簿寫入「<工單 ID> 需要協助」
- `BLOCKED` → 剪貼簿寫入「<工單 ID> 需要協助」
