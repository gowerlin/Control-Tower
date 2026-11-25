---
title: 進階：總覽
description: 進階區的地圖：設計理念 7 篇講 CT 為什麼這樣設計，功能深入 12 篇講每個機制怎麼運作，附建議閱讀順序。
---

# 進階：總覽

<p class="ct-lead">進階區給已經會用 CT、想知道「為什麼這樣設計」的人。設計理念 7 篇講背後的原則，功能深入 12 篇講每個機制的規則；每篇都同時回答「規則是什麼」和「為什麼這樣定」。</p>

如果你還沒用過 CT，建議先讀 [為什麼需要 CT](/why) 和 [一張工單的一生](/lifecycle)，再回到這裡。

## 設計理念 {#principles}

這 7 篇講的是 CT 背後的原則。它們不教指令，而是解釋為什麼塔台不讀程式碼、為什麼工單要寫成檔案、為什麼有些動作一定要人點頭。讀完之後，遇到規則沒寫到的情況，你大概也推得出 CT 會怎麼做。

<FeatureGrid set="principles" />

## 功能深入 {#features}

這 12 篇逐一拆解 CT 的機制：工單、派工、待辦分頁、yolo 與斷點、Worker 提問、worktree 隔離與合併、落點檢查、中斷與 Renew、多種單據、學習與 Workflow、跨塔台協作、觀測工具。每篇都會連回對應的設計理念。

<FeatureGrid set="features" />

## 建議閱讀順序

**第一次讀進階區**，先讀設計理念的前三篇，它們是其他所有規則的根：

1. [認知作業系統](/deep/principles/cognitive-os)：CT 的第一原則。之後每一篇幾乎都能從這裡推出來。
2. [檔案即真相來源](/deep/principles/files-as-truth)：為什麼一切都寫進檔案，以及收尾為什麼要反序。
3. [塔台不讀程式碼](/deep/principles/tower-and-workers)：塔台和 Worker 怎麼分工。

接著依你的需要挑：

- **要開始用 yolo 或 BAT 自動派工**：[可逆與不可逆的界線](/deep/principles/boundaries) → [派工](/deep/features/dispatch) → [yolo 與斷點](/deep/features/yolo) → [Worker 向塔台提問](/deep/features/worker-questions) → [待辦分頁](/deep/features/bat-todo)。
- **要用 worktree 隔離並行開發**：[可逆與不可逆的界線](/deep/principles/boundaries) → [worktree 隔離與合併](/deep/features/worktree-merge) → [落點檢查](/deep/features/landing-check)。
- **要讓 CT 累積經驗、跨專案共用**：[三層資料與記憶](/deep/principles/data-layers) → [會學習的系統](/deep/principles/learning) → [自我學習、Playbook 與 Workflow](/deep/features/learning-playbook-workflow)。
- **要維護規則、寫 skill，或想知道 CT 怎麼管自己的文件**：[治理](/deep/principles/governance)。

## 怎麼讀「延伸閱讀」

每篇最後都有「延伸閱讀」，列出權威出處的檔案與章節，寫法是「檔案 § 章節名」。路徑以 CT 安裝後的 skill 目錄為起點，例如 `control-tower/references/doctrine.md`、`ct-exec/SKILL.md`；CT Guide 的檔案以 `control-tower-guide/` 為起點；`docs/` 開頭的是 CT 版本目錄裡的實戰補充文件（不在安裝用的 zip 裡）；標「文章」「規劃文件」的是 CT 專案的背景文件，不是規則的權威來源。

## 延伸閱讀 {#further-reading}

- `control-tower/SKILL.md` § Reference Routing：每份 reference 管哪一塊
- `control-tower/references/doctrine.md` § 第一原則：Memory Hierarchy 同構、§ CT 三層資料結構的設計依據、§ 工單狀態機的設計依據
- `control-tower-guide/references/concepts.md` § Orchestrator/Worker 分離模式、§ Hard Boundaries（塔台硬邊界）

::: warning 摘要不具權威
Portal 是摘要，不具權威。CT 的每條規則只在一份 reference 裡完整定義，Portal 只是幫你讀懂它。內容與 CT reference 有出入時，以 reference 為準。為什麼要這樣寫，見 [治理：單一權威與「摘要不具權威」](/deep/principles/governance)。
:::
