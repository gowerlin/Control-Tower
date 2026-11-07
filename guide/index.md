---
title: Guide Skill 專區
description: 兩個互動式學習指南 skill：教 CT 的 CT Guide 與教 BMad-Method 的 BMad Guide。各教什麼、版號跟誰走、什麼時候問哪一個，以及和 ct-help、新手村的分工。
# 不顯示右側本頁目錄，讓內容欄變寬、五塊積木圖放大
aside: false
---

<script setup>
import { useData } from 'vitepress'
import bmadGuide from '../data/bmad-guide.json'

const { theme } = useData()
const ctGuideVersion = theme.value.ctRelease.guideVersion

const compareRows = [
  ['skill 名稱', 'control-tower-guide', 'bmad-guide'],
  ['教什麼', 'CT：塔台與 Worker、工單、派工、治理為什麼這樣設計，各部分怎麼接在一起', 'BMad-Method：生命週期各階段、Agent 角色、下一步該用哪個 bmad-* skill、哪些 skill 已經改名或退役'],
  ['版號跟誰走', '跟 CT：CT 每發一版（含 patch），同一輪出一版同號的 CT Guide', '跟 BMad-Method：BMad-Method 發版後才更新，不跟 CT'],
  ['目前版本', `v${ctGuideVersion}`, `v${bmadGuide.version}（BMad-Method v${bmadGuide.bmadMethodVersion}）`],
  ['回答方式', '繁體中文；三種回應模式（概念理解、實戰查詢、比較釐清）；附可點擊的 SVG 圖', '繁體中文；兩種回應模式（概念理解、實戰查詢）；需要時附可點擊的 SVG 圖'],
  ['和 CT 的關係', 'CT 的配套教材；獨立安裝，不是 CT 的 8 個 skill 之一', 'CT 的外部依賴：塔台偵測到它才拿來查 BMad 流程；沒裝也照常運作']
]

const roleRows = [
  ['control-tower-guide', '獨立的 skill', '教科書（CT）', '理解 CT 的概念、設計理由與架構'],
  ['bmad-guide', '獨立的 skill', '教科書（BMad-Method）', '理解 BMad-Method 的流程，找出下一步該用的 bmad-* skill'],
  ['ct-help', 'CT 的 skill（/ct-help、$ct-help）', '操作手冊', '馬上要做一件事：確切的 CT 指令、設定、前綴'],
  ['新手村（beginner-tutorial）', '塔台內建模式，不是 skill', '駕訓班教練', '在進行中的塔台裡陪練：課程關卡、違規偵測、結業']
]
</script>

# Guide Skill 專區

<p class="ct-lead">這裡收兩個互動式學習指南 skill：教 CT 的 CT Guide，和教 BMad-Method 的 BMad Guide。兩者都是「教科書」，用問的，用繁體中文回答，並畫可以點擊、一路往下追問的圖；它們只負責講解和帶路，不替你執行工作。</p>

## 五塊積木：兩個 Guide 貼在哪一層 {#stack}

BMad-Method、CT、BAT 由上往下疊成一套：方法、編排、執行環境，最底下是專案 repo。兩個 Guide 不是其中一層，而是貼在各自講解的那一層旁邊：BMad Guide 貼在 BMad-Method 右側，CT Guide 貼在 CT 左側。

<EcosystemStack />

塔台偵測到 BMad Guide 才會讀它，查出該走的 BMad 流程；CT Guide 則只講解 CT，其中 `bat-integration` 專章說明 CT 與 BAT 怎麼分工。

## 兩個 skill 對照 {#compare}

<CardTable
  :columns="['', 'CT Guide', 'BMad Guide']"
  :rows="compareRows"
  caption="CT Guide 與 BMad Guide 對照"
/>

- [CT Guide Skill](./ct-guide)：是什麼、安裝、三種回應模式、怎麼問、17 種圖表
- [CT Guide 學習路線](./learning-path)：CT Guide 十一份教材依讀者分流的閱讀順序
- [BMad Guide Skill](./bmad-guide)：是什麼、和 CT 的關係、什麼時候問它、版本檢查與 `*update`、安裝

兩個 skill 的版號各走各的：CT Guide 永遠和 CT 同號，BMad Guide 和 BMad-Method 同號。所以裝 CT v{{ theme.ctRelease.ctVersion }} 時，CT Guide 是 v{{ ctGuideVersion }}，BMad Guide 則看你用的 BMad-Method 版本，本站內容以 BMad Guide v{{ bmadGuide.version }} 為準。

## 什麼時候問哪一個 {#which}

兩個 skill 的觸發話題不同：一個講 CT 與塔台，一個講 BMad-Method 與 `bmad-*` skill。可以兩個都裝。

- **問 CT 為什麼這樣設計**：塔台為什麼不讀程式碼、工單為什麼是檔案、yolo 的斷點、落點檢查、三層資料……問 **CT Guide**。
- **問 BMad 的流程**：現在在哪個階段、下一步該跑哪個 `bmad-*` skill、某個角色（Mary、John、Winston……）管什麼、舊的 skill 名稱現在改成什麼……問 **BMad Guide**。
- **在塔台裡開工單時要配哪個 BMad 流程**：不用自己問。塔台偵測到 `bmad-guide` 就會去讀它，依專案階段查出流程；沒裝的話，工作流程欄位由你手動指定（見 [BMad Guide › 和 CT 的關係](./bmad-guide#ct)）。
- **要確切的 CT 指令或設定值**：問 `ct-help`，或查[指令參考大全](/reference/commands)。

## 和 ct-help、新手村的分工 {#roles}

<CardTable
  :columns="['資源', '形式', '比喻', '用途']"
  :rows="roleRows"
  :highlight="[0, 1]"
  caption="兩個 Guide、ct-help 與新手村的分工"
/>

兩個 Guide 講到確切的規則時，都不會自己再寫一份：CT Guide 指回 `ct-help` 或 CT 的 reference，BMad Guide 依自己的 references 回答，並帶你到對的 `bmad-*` skill。這和 Portal 的立場相同：摘要只負責帶路，權威定義只有一處。

## 延伸閱讀 {#further}

- CT Guide `SKILL.md` § Positioning、§ When to use、§ Response modes
- bmad-guide `SKILL.md` § When To Use、§ Response Modes、§ Built-In Commands
- CT `enhancement-integration.md` § Level 2：方法論轉接（methodology adapter）

Portal 是摘要，不具權威；與各 skill 的 `SKILL.md`／references 有出入時，以 skill 為準。
