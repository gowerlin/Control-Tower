---
title: 版本總覽
description: 目前的 CT、CT Guide 與 BMad Guide 版本、SemVer 慣例、版號寫在哪裡、Guide 與 Portal 怎麼跟著 CT 同步，以及怎麼查本機裝的是哪一版。
---

# 版本總覽

<p class="ct-lead">CT 與 CT Guide 永遠同一個版號，Portal 顯示的也是這一組。版號寫在每個 <code>SKILL.md</code> 內文的第一個註解裡，不放在 frontmatter。</p>

## 目前版本

<VersionBadge variant="block" />

這組數字由同步腳本從 CT 的發行目錄讀出：CT 和 Guide 的版號不一致時，腳本會報錯並停止，不會寫出一組對不上的版本。每一版改了什麼見[更版紀錄](./releases)，八個世代的來龍去脈見[演進史](./evolution)，各功能需要的 BAT 與 codex 版本見[相容版本對照](./compatibility)。

BMad Guide Skill 是例外：它的版號跟 BMad-Method 走，不跟 CT，所以不歸同步腳本管，版本資料另外讀 `data/bmad-guide.json`。為什麼這樣定、怎麼更新，見 [BMad Guide Skill › 版本](/guide/bmad-guide#version)。

## SemVer 慣例

CT 採 Semantic Versioning，`MAJOR.MINOR.PATCH`：

<CardTable
  :columns="['觸發條件', '版號變動', '例子']"
  :rows="[
    ['不相容的工作流程或 metadata schema 變更', 'MAJOR', '5.0.0：工單 metadata 的事實來源改成 YAML frontmatter'],
    ['新命令、新設定、新的向下相容能力', 'MINOR', '5.12.0：同一張工單重派前，先回收舊的 Worker 分頁'],
    ['文件補完、BAT 規則修正、trigger 描述調整', 'PATCH', '5.12.2：收單回收的提示文字改寫，行為不變']
  ]"
  caption="CT 的 SemVer 慣例"
/>

到目前為止，CHANGELOG 記錄的 64 個版本裡只有一次 MAJOR，就是 5.0.0。

## 版號寫在哪裡

Skill 的 YAML frontmatter 只放執行時需要的欄位（至少 `name` 和 `description`），**不放 `version:`**。原因是 Codex 的 skill 驗證會把不認得的欄位當成錯誤。版號的事實來源改成內文的第一個註解：

```markdown
<!-- control-tower-version: 5.13.0 -->
```

8 個 CT skill 各自有一行，名稱換成 skill 自己的（例如 `ct-exec-version`），Guide 是 `control-tower-guide-version`。同一個版號還會出現在幾個地方，發版時要一起改：

| 位置 | 格式 |
|---|---|
| 內文註解 | `<!-- control-tower-version: X.Y.Z -->` |
| H1 或面板標題 | `BMad Control Tower vX.Y.Z` |
| 塔台狀態檔 `_tower-state.md` 的 metadata | `Control Tower vX.Y.Z` |
| Worker 相容性文件 | 需要時在相關 reference 標明最低版本 |

`*sync` 或版本檢查要讀版號時，先讀內文註解，讀不到才退回標題；不會要求 frontmatter 有 `version:`。這套做法從 v5.0.3 開始，v5.0.2 以前的版本仍是寫在 frontmatter。

## Guide 跟著 CT 同版號

CT 每次發版（含 patch），同一輪都要出一版同號的 CT Guide Skill。Guide 內容不受影響時，至少要更新版號；內容受影響時，連教材一起對齊。發版時檢查兩邊版號，不一致就不算完成這一輪。

這條規則是在 CT v5.2.4 發版、Guide 卻停在 v5.2.3 之後訂下的（見[實戰案例](/cases#version-sync)）。

## Portal 跟著 CT 同步

Portal 的版本資料也要在同一輪更新：

- **每次發版（含 patch）**：執行同步腳本，更新目前版本、從 CT 的 CHANGELOG 重新產生[更版紀錄](./releases)；相容性有變時，更新[相容版本對照](./compatibility)的資料檔。
- **功能或規則有變時**（MINOR，或改了規則的 PATCH）：一併更新受影響的功能頁、進階頁與[指令參考大全](/reference/commands)，發版時列出受影響的 Portal 頁。
- **進入新世代時**：由塔台判斷，更新[演進史](./evolution)。

收一輪發版時要對三處版號：Portal 的版本資料、CT `SKILL.md` 的版號註解、Guide 的版號。三處一致才算收完。

## 怎麼查本機裝了哪一版

在 Claude Code 的安裝目錄下，把每個 skill 的版號註解列出來：

```bash
grep -h -o "[a-z-]*-version: [0-9.]*" ~/.claude/skills/{control-tower,ct-*}/SKILL.md
```

8 行都應該是同一個版號（塔台和 Worker 必須同批升級）。Codex 端把 `~/.claude/skills` 換成 `~/.codex/skills`。兩端是**各自獨立的安裝**，升級其中一端不會更新另一端，要分別查。v5.0.2 以前的版本請改看 frontmatter 的 `version:`。

升級的步驟（備份、暫存複驗、替換、逐檔比對）見[安裝](/install)。新版從**下一個 session** 才生效，正在跑的 session 仍是舊規則。

## 延伸閱讀

- CT `version-governance.md` § 版號事實來源、§ SemVer 慣例、§ 歷史版號表、§ 相容性注意
- CT 安裝與使用指南 § 4.1 安裝／升級（現行流程）：確認現行版號、Codex 端
- CT `CHANGELOG.md`（64 個版本）

Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
