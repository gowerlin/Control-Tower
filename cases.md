---
title: 實戰案例
description: CT 開發過程中真實發生的九件事：斷電續作、衝突合併、用證據擋下升級、量測推翻直覺、收尾前被關、跨塔台交辦、版本同步規則、塔台不採信 Worker 的 PASS、先實機再寫文件。
---

# 實戰案例

規則讀起來都很合理，真正的考驗是事情沒照計劃走的時候。這一頁收的是 CT 自己開發過程中真實發生的事：每張卡寫情境、CT 怎麼處理、示範了哪個機制，最後連到講那個機制的進階篇。 {.ct-intro}

案例取自兩個地方：CT 本身的開發紀錄，以及課程示範 repo（用 CT 帶著 BMad 與 BAT 開發一個 Go SMS 平台）的實錄。改寫時保留機制與因果，不寫工單編號、決策編號與 commit 識別碼，時間只寫到日期，數字都能在紀錄裡查到。

## 中斷與恢復 {#recovery}

工作做到一半停下來，是最常見的混亂。CT 的做法是先看檔案裡留下什麼，再決定怎麼接。 {.ct-lead}

<CaseCard id="power-loss" title="斷電之後，從半成品接著做" tag="斷電續作" facet="both" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', '盤點現場、寫補充說明、Renew 重派'], ['BAT', '重派前先回收舊分頁']]">
<template #before>2026-10-23，一個 Worker 正在做課程某一章的素材，主機突然斷電重開，Worker 的 session 跟著結束。重開後的現場是：一部分成果已經 commit 並打好本機 tag，另外還有一大批沒 commit 的半成品（49 個修改、12 個刪除、11 個新檔），工單回報區一片空白，狀態還停在 IN_PROGRESS。</template>
<template #after>塔台沒有直接重派，先自己盤點現場：改過與新增的檔案沒有空檔、沒有壞字元，<code>git fsck</code> 也沒有錯，所以半成品保留、不還原。工作還沒做完，不適合用只補收尾的 <code>ct-done</code>，於是在工單加一段「塔台補充：斷電續作」：不要丟掉半成品、已經做完的步驟不重跑、示範 repo 若有中斷的 merge 就先停下回報、tag 照規格移到最終 commit。重派前先回收舊分頁（BAT 重開後舊分頁已不在，回 exit <code>3</code>，照規則仍然派工），再以 yolo 重派 <code>ct-exec</code>，並確認 Worker 已啟動。</template>
<template #result>續作的 Worker 約 23 分鐘後回報 DONE，沒有重做已完成的部分。示範的機制：Renew（塔台補充 → 重派）、<code>ct-done</code> 與 <code>ct-exec</code> 的分界、重派前回收舊分頁、塔台獨立盤點現場。→ <a href="./deep/features/recovery">中斷、Renew 與補救收尾</a></template>
</CaseCard>

<CaseCard id="closed-before-closeout" title="產品做完了，收尾卻沒做" tag="收尾前被關" facet="ct" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', '判斷缺什麼、只重派收尾']]">
<template #before>2026-10-18，一張 CT 發版工單的 Worker 分頁在收尾前被關掉了。產品其實已經完成：commit 在、兩個發行 zip 在、兩端安裝逐檔比對 16/16 IDENTICAL、備份也在；但回報區是空的、frontmatter 還是 IN_PROGRESS、工單沒有 commit。使用者問塔台：直接算 DONE，還是重派？</template>
<template #after>塔台判定<strong>不能直接 DONE</strong>：這張工單的驗收條件要求附檔案行號與搜尋證據，有幾條規則也還沒有人自檢過，這些都不在檔案裡。它也不用 <code>ct-done</code>，因為 <code>ct-done</code> 只補收尾欄位、不跑驗收。塔台在工單加一段重派說明：不重做前五步，從回報區接著做，驗收不合才修。然後重派 <code>ct-exec</code>。</template>
<template #result>重派的 Worker 約 6 分鐘後回報 DONE，全部驗收通過，沒有任何產品改動。和上一張對照：兩次都重派 <code>ct-exec</code>，差別在補充說明要 Worker 接著做的是「未完成的工作」還是「缺少的證據」。→ <a href="./deep/features/recovery">中斷、Renew 與補救收尾</a></template>
</CaseCard>

## 用證據做決定 {#evidence}

CT 不靠「看起來沒問題」做決定。下面四件事，都是一個量測、一次複驗或一次實機實驗改變或補足了原本的判斷。 {.ct-lead}

<CaseCard id="measure-landing" title="量測推翻直覺：身分不能用路徑證明" tag="量測推翻直覺" facet="ct" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', '模擬量測、改設計、推翻自己先前的判斷']]">
<template #before>2026-09-01，一個 Worker 在實作落點檢查時改了規則：C-3 原本檢查「檔案或它的直接父目錄存在」，Worker 改成「往上找到最近存在的祖先目錄」。理由是它這張工單本身要建立一整棵新版本目錄，照原規則會被誤判成「可能落錯 repo」。Worker 說這樣改「鑑別力沒有減少」。</template>
<template #after>塔台沒有直接接受，而是做了一次<strong>模擬量測</strong>：拿另一個專案的 34 張真實工單（共 65 條 <code>affects_files</code>），假裝 Worker 誤落在這個 repo，看規則攔不攔得下。直接父目錄的規則攔下 34/34（100%），祖先上溯的規則只攔下 14/34（41%）。漏掉的 20 張，主因是像 <code>docs/api/*.md</code> 這種路徑會上溯到兩個 repo 都有的 <code>docs/</code>，而且只要一條命中，整張工單的 C-3 就失效。</template>
<template #result>結論是純路徑法根本解不了這個問題：「在對的 repo 建新目錄」和「落在錯的 repo」用路徑看是同一種形狀。於是保留祖先上溯（避免假警報），把 C-3 降為輔助，另在工單加 <code>repo</code> 欄位，用 repo 身分（C-0）當承重檢查；塔台先前「這個欄位太重、本輪不做」的判斷也一併推翻。注意：這是模擬量測，紀錄裡沒有「真的攔下錯 repo」的實例。→ <a href="./deep/features/landing-check">落點檢查</a></template>
</CaseCard>

<CaseCard id="evidence-gate" title="回測沒過閘門，就縮小範圍" tag="用證據擋下升級" facet="ct" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', '回測、對照門檻、維持 🔵、只做便宜的部分']]">
<template #before>2026-10-20，CT 在評估要不要讓 Claude Code 的 Workflow 工具成為派工的一部分：把兩支具名 workflow（一支挖掘語料、一支多來源唯讀查核）寫成知識卡，通過閘門 G2 就讓塔台在派工時自動建議使用。G2 的條件是用三組真實資料回測，看召回率與誤報率是否達到門檻。</template>
<template #after>三組回測的結果：第一組召回 60%、誤報 25%；第二組召回 88.1%、誤報 1.5%，但漏掉了一個單一 Worker 先前就找到、而且推翻原結論的重點，用量還超出核准上限約兩成；第三組召回 61.1%。兩張知識卡都沒到門檻，置信度維持 🔵，G2 不通過。使用者選擇的路線是：具名 workflow 停在 🔵、不參與派工，原本的下一階段縮成精簡版，只做便宜的部分。</template>
<template #result>結果就是 v5.11.0：新增 <code>workflow_integration</code> 設定，Worker 只有在工單明文授權時才能呼叫 Workflow，自己開的子代理要在回報區記錄。之後兩支具名 workflow 也移出「可直接呼叫」的清單，避免誤觸一次就耗掉大量用量。→ <a href="./deep/principles/learning">會學習的系統</a>、<a href="./deep/features/learning-playbook-workflow">自我學習、Playbook 與 Workflow</a></template>
</CaseCard>

<CaseCard id="independent-check" title="塔台不採信 Worker 的 PASS" tag="獨立複驗" facet="ct" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', '收單前在自己的環境重跑一次']]">
<template #before>2026-10-22，一張課程工具的工單回報 DONE，所有驗收都 PASS，其中包括一支逐字稿工具的 23 項自動測試。Worker 是在自己的 shell 環境跑的，結果全綠。</template>
<template #after>塔台收單前在自己的 Git Bash 重跑同一組測試，結果 1/23 FAIL：一個以 <code>/control-tower</code> 開頭的參數，被 Git Bash 的路徑轉換改寫成一個 Windows 路徑。設定 <code>MSYS_NO_PATHCONV=1</code> 之後 23 項全過。塔台接著推論影響範圍：<code>claude</code> 是原生程式，工具送出的 <code>/ct-exec</code> 這類提示也會被改壞，下一階段開始前一定要修。</template>
<template #result>原工單照驗收收單，另開一張範圍很小的工單修這個缺陷，並要求用一次真實呼叫證明提示原樣送達。示範的機制：Worker 的 PASS 是證據之一，不是結論；塔台收單時在不同環境獨立複驗，問題就在交出去之前被抓到。→ <a href="./lifecycle">一張工單的一生</a></template>
</CaseCard>

<CaseCard id="nested-repos" title="先查前提、先實機，再寫文件" tag="前提更正" facet="both" before-label="情境" after-label="CT 怎麼處理" :roles="[['BAT 塔台', '轉來使用者的問題'], ['CT', '查證前提、拋棄式目錄實機驗證、補文件']]">
<template #before>2026-10-30，BAT 塔台轉來一位使用者的問題：上層目錄底下有好幾個跟團隊共用的獨立 repo，工單被寫進各子 repo，BAT 指揮塔面板只讀 workspace 那一層、看不到，編號也各自從頭算。BAT 塔台的理解是落點檢查 C-0、C-1 要求工單放在子 repo，並提了幾個方向，其中一個是放寬落點檢查。</template>
<template #after>CT 塔台先查前提：C-0、C-1 是 v5.0.4、v5.0.5 為了攔下「對的工單在錯的 repo 執行」加的，並沒有規定工單放哪裡；真正讓工單跑進子 repo 的，是 Worker 在子 repo 執行（Worker 在自己 cwd 底下找工單，<code>repo</code> 又是 cwd 所在 repo 的名字）。放寬落點檢查等於拆掉 C-0 要攔的那道防線，所以不採用；改推薦讓 Worker 在上層執行：上層 <code>git init</code> 當個人的塔台 repo、工單全放上層、子 repo 用 <code>git -C</code> commit，BAT 不需要改程式。這個方案當時只是照規則推得，塔台沒有直接寫進文件，而是先建一個拋棄式目錄（上層加兩個子 repo），派 Worker 實機跑一張同時改兩個子 repo 的工單。</template>
<template #result>C-0、C-1、C-3 都通過，兩個子 repo 各自 commit 成功，上層看不到子 repo 的檔案。實驗另外找到三件推論時沒想到的事：<code>affects_files</code> 從上層寫、<code>git -C</code> 時要去掉子 repo 前綴；C-0 只驗上層、不驗子 repo；新目錄第一次派工會先跳出資料夾信任確認，<code>--wait-started</code> 回 exit <code>8</code>（塔台沒有重派，請使用者在分頁回答）。這三點都寫進 v5.14.3 的限制，沒驗到的面板一鍵派工也照實標成未驗。示範的機制：先更正前提再談方案、推論先實機再寫成文件、護欄不為方便而放寬。→ <a href="./deep/features/multi-tower#nested-repos">一個塔台管多個共用 repo</a></template>
</CaseCard>

## 並行與合併 {#parallel}

這一張來自課程示範 repo 的實錄：兩張會改到同一個檔案的工單並行，最後怎麼安全地合回 `main`。 {.ct-lead}

<CaseCard id="conflict-merge" title="兩張工單改到同一個檔案" tag="衝突合併工單" facet="both" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', 'overlap 檢查、判斷合併模式、SHA 比對、斷點 E'], ['BAT', 'worktree 隔離派工、提問通道、查 worktree 狀態']]">
<template #before>2026-10-23，示範 repo 要同時做 SMS 平台的兩項功能：發送佇列與重試、真實供應商的 adapter。兩張工單都會動到 <code>cmd/smsd/main.go</code>，派工前的 overlap 檢查回 BLOCK。其中一個 Worker 執行中透過 BAT 通道問了塔台五題，有一題沒有被輪詢到、過期了。</template>
<template #after>塔台照 BLOCK 的提示接受風險，兩張都用 <code>--isolation worktree</code> 派到各自的分支。過期的那題，Worker 依 yolo 備援把工單回報成 BLOCKED，塔台在 Renew 區段答覆後重派，第二次就 DONE；這張先完成，直接合併（模式 ①）。另一張完成時，<code>main</code> 已經往前走了 10 個 commit，而且 <code>main.go</code> 有衝突，直接合併的五個判準有兩個不成立，於是另開合併工單（模式 ②，conflict）：解掉 1 個檔案的衝突、寫明雙方意圖與解法，驗收跑在合併後的 commit 上。收單時走 SHA 比對五步，塔台自己用 <code>git rev-parse</code> 確認兩個 parent；第 5 步觸發（<code>main</code> 因合併工單的回報 commit 又前進了一步，差異只有那份工單檔），再合一次，經過斷點 E 後以 <code>--ff-only</code> 推進 <code>main</code>，最後清理 worktree 與分支。</template>
<template #result>合併後塔台在 <code>main</code> 上重跑 <code>go test ./... -race</code>，10 個套件全部通過。示範的機制：worktree 隔離、overlap BLOCK、合併模式 ① 與 ②、SHA 比對五步、提問逾時 → BLOCKED → Renew。這次實錄也留下四條回饋給 CT 下一版。→ <a href="./deep/features/worktree-merge">worktree 隔離與三種合併模式</a></template>
</CaseCard>

## 規則怎麼長出來 {#rules}

CT 的規則多半不是事先設計好的，而是某件事發生之後才補上，而且補的時候要寫清楚由誰檢查。 {.ct-lead}

<CaseCard id="cross-tower" title="另一座塔台交來規格，由對方實機驗收" tag="跨塔台交辦" facet="both" before-label="情境" after-label="CT 怎麼處理" :roles="[['BAT 塔台', '寫規格、實機驗收'], ['CT', '照規格寫規則、發版']]">
<template #before>2026-10-22，BAT 塔台透過跨 session 訊息交來一份規格：同一張工單重派時，舊的 Worker 分頁還開著，等新 Worker DONE、塔台收單回收時，會因為找到兩個分頁而回 exit <code>5</code>（<code>AMBIGUOUS</code>），兩個分頁都得手動關，BAT 還會把兩個分頁都標成完成。規格請 CT 在重派前先回收舊分頁。</template>
<template #after>CT 塔台把規格裡要決定的四題交給使用者，使用者都選了建議項：例如 <code>ct-done</code> 的補救派工<strong>不回收</strong>，因為舊分頁的輸出可能正是要看的現場；<code>worker_auto_close</code> 關閉時<strong>仍然回收</strong>，因為這是為了避免同一張工單有兩個分頁，不是收單回收。CT 開單、發 v5.12.0（新增塔台行為，屬 MINOR；BAT 介面不變），Guide 同版號。</template>
<template #result>驗收由 BAT 塔台在 BAT 安裝版上做：情境一是 yolo 備援 → Renew → 重派前回收 exit <code>0</code> → 新 Worker DONE 後收單回收 exit <code>0</code>，不再 <code>AMBIGUOUS</code>；情境二是舊分頁已手動關 → 回收回 exit <code>3</code> → 照常派工。兩個情境都 PASS，同一天結案。示範的機制：BAT 定介面、CT 照契約寫規則，交辦方自己驗收。→ <a href="./deep/features/multi-tower">跨塔台與跨專案協作</a></template>
</CaseCard>

<CaseCard id="version-sync" title="版本同步規則的誕生" tag="同步規則" facet="ct" before-label="情境" after-label="CT 怎麼處理" :roles="[['CT', '把一次疏漏寫成收單時必查的規則']]">
<template #before>2026-10-17，使用者發現 CT 發了 v5.2.4，CT Guide Skill 卻還停在 v5.2.3，沒有跟著更版。教材和工具的版號對不上，讀 Guide 的人會以為自己裝的是另一版。</template>
<template #after>使用者當天就訂下專案規則：CT 每次發版（含 patch），同一輪必須出一版同號的 Guide；內容不受影響時至少更新版號，內容受影響時一併對齊教材。發版工單的驗收要包含 Guide 同步，塔台收單時檢查兩邊版號，不一致就不算收完。已經漏掉的那一版，使用者選擇一次性的例外：Guide 跳過 v5.2.4，直接和 CT 一起出 v5.2.5，內容對齊兩版。</template>
<template #result>從 v5.2.5 起照規則走，之後只有一次同樣的例外（兩版間隔很短時 Guide 跳過前一版、直接對齊下一版）。後來 Portal 也加進同一條同步鏈，收一輪發版要對三處版號。示範的機制：版本治理；規則寫進專案本地規則，由塔台在收單時檢查。→ <a href="./versions/">版本總覽</a></template>
</CaseCard>

## 更多案例

BAT 站另有一頁案例，包括虛構專案 demo-shop 的三個情境，以及 BAT 自己的開發紀錄：<BatLink path="cases">BAT 站：實戰案例</BatLink>。

## 延伸閱讀

- CT 開發紀錄（決策日誌、專案本地規則）
- CT `research-workorder.md` § Renew 機制；`ct-done/SKILL.md`
- CT `ct-exec/SKILL.md` § Landing Zone Check
- CT `mono-repo-patterns.md` § 巢狀的獨立 repo（一個塔台、多個共用 repo）
- CT `workflow-engine.md` § 現況：G2 未通過（v5.11.0）
- CT `merge-workorder.md` § 三種模式、§ 收單 SHA 比對五步、§ 斷點 E
- CT `work-order-system.md` § 重派前回收舊 Worker 分頁（v5.12.0+）
- CT 實戰補充（四）〈當現實比計劃更混亂時〉

Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。
