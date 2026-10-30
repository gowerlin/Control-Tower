# 中斷處理與緊急任務

開發中被插件是常態。使用 `*pause` 命令告訴塔台，不要跳出去自己處理。

## 中斷協議

不管塔台正在說什麼，使用 `*pause` 命令：

```
*pause 上線版本 v2.1 的登入 API 回 500，客戶在催
```

塔台收到 `*pause` 後：

1. **凍結當前任務**：進行中的工單狀態改為 ⏸ PAUSED，記錄暫停原因和時間到工單檔案
2. **記錄暫停狀態**：更新 `_tower-state.md`（paused_workorder、pause_reason、pause_time），同一次寫入同步更新機器可讀摘要（見 `memory-protocol.md` § 機器可讀摘要（YAML frontmatter））
3. **評估緊急任務**：判斷範圍、影響、是否需要不同分支（使用互動式選項提問）
4. **派發緊急工單**：標記 🔥 URGENT，含分支策略建議
5. **排入回歸佇列**：確保緊急任務結束後原任務能接回

## 任務佇列（含中斷狀態）

```
| Story     | 工單  | 狀態          | 卡點        | 下一步           |
|-----------|-------|--------------|------------|-----------------|
| 1.2       | T0005 | ⏸ PAUSED     | 被 HOTFIX 中斷 | 等緊急任務完成 |
| HOTFIX-01 | T0006 | 🔥 URGENT    | -          | ← 正在處理      |
```

## HOTFIX 完成後恢復（`*resume`）

使用 `*resume` 命令恢復暫停的工單：

```
*resume          # 自動尋找最近一張 PAUSED 工單
*resume T0005    # 恢復指定工單
```

`*resume` 執行流程：

1. HOTFIX 工單標記 ✅ DONE
2. 顯示暫停時的上下文摘要（暫停原因、暫停時間、已完成部分）
3. PAUSED 工單狀態改回 🔄 IN_PROGRESS
4. 更新 `_tower-state.md`（清除 paused 記錄），同一次寫入同步更新機器可讀摘要（見 `memory-protocol.md` § 機器可讀摘要（YAML frontmatter））
5. 評估 HOTFIX 修改是否影響暫停中任務的設計
6. 提醒：feature 分支是否需要 merge main
7. 提示下一步行動

## Git Worktree 平行作業

緊急任務在不同分支時，建議物理隔離：

```bash
git worktree add ../my-project-hotfix main
```

兩個目錄各自開 session 互不干擾：

| 情境 | 建議 |
|------|------|
| Hotfix 很小（< 30 min） | 同塔台管理，工單指定 worktree 路徑 |
| Hotfix 複雜或時間不定 | 開第二個塔台，完成後關閉 |

完成後清理：
```bash
git worktree remove ../my-project-hotfix
```
