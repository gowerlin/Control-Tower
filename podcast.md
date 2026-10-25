---
title: 推廣影片（第二季）
description: 推廣影片第二季：5 支 6 到 11 分鐘的說明影片，介紹 BMad-Method、Control Tower 與 BAT 的設計初衷、工單流程與實戰邊界。附建議觀看順序、錄製時版本、完整語音版與簡報 PDF 下載。
---

<script setup>
import { useData } from 'vitepress'

const { theme } = useData()
const pdf = (name) => theme.value.podcastReleaseUrl + name
const audio = (name) => theme.value.podcastReleaseUrl + name
</script>

# 推廣影片（第二季）

<p class="ct-lead">5 支說明影片，每支 6 到 11 分鐘，講 BMad-Method、Control Tower（CT）與 Better Agent Terminal（BAT）為什麼這樣設計、一張工單怎麼走完、什麼時候該放手。適合第一次接觸這套工具的人。</p>

這個系列只談觀念與全貌，不帶操作。想一步一步動手做，看正式課程[多代理規格驅動開發實戰](/course)：6 章、57 單元、影片約 21 小時，從零做出一個 Go 專案。兩者可以搭配：先看這 5 支影片知道每個零件在做什麼，再進課程實作。

每集另有比影片更完整的對談式語音版，可以在本頁直接收聽，見[完整語音版](#完整語音版)。

播放清單：[BMad Control Tower 推廣影片第二季（影片＋完整語音版）](https://www.youtube.com/playlist?list=PLCSwJasrDt48)

## 五集

<CardTable
  :columns="['集數', '標題', '給誰', '一句話', '長度']"
  :rows="[
    ['S2-01', '把腦力留給判斷：設計初衷與生態系全景', '所有人（入口集）', '記憶交給檔案，跑腿交給 BAT，判斷留給你', '6:22'],
    ['S2-02', 'BMad-Method 6.12：先想清楚，再讓 AI 動手', '用 BMad 規劃需求的人', '先問「意圖清楚了嗎」，所有實作收斂到 bmad-build', '7:01'],
    ['S2-03', 'Control Tower v5：一張工單的一生', '要當塔台指揮官的人', '開單、派工、回報、收單、學習，每次都一樣的外殼', '7:28'],
    ['S2-04', 'BAT：給塔台跑道、無線電和雷達', '同時管很多 Agent 的人', '不用 CT 也好用；接上 CT 後是塔台的基礎設施', '10:55'],
    ['S2-05', '實戰與邊界：放手，但不是放任', '已經在用或正在評估導入的人', '人只做幾個關鍵決定；放手是交出雜事，不是交出判斷', '7:29']
  ]"
  caption="推廣影片第二季五集"
/>

## 建議觀看順序

- **第一次接觸的人**：S2-01 → S2-03 → S2-04 → S2-05；要用 BMad 規劃需求的，再補 S2-02。
- **用過舊版 CT 或 BMad-Method 的人**：S2-01（看這段時間變了什麼）→ S2-04（BAT）→ S2-03（工單流程的更新）→ S2-02（BMad 的改名與新流程）→ S2-05。
- **技術主管、評估導入的人**：S2-01 → S2-05，需要時再看 S2-03、S2-04。

## 錄製時版本

| 工具 | 版本 |
|---|---|
| Control Tower | v5.11.0 |
| Better Agent Terminal | 0.7.1-pre.4 |
| BMad-Method | v6.12.4 |

影片內容以錄製時的版本為準。之後的改變以 Portal 為準：目前版本見[版本總覽](/versions/)，每一版改了什麼見[更版紀錄](/versions/releases)。

## 完整語音版

比影片更完整的對談式語音節目，每集約 16 到 25 分鐘，適合通勤或做事時聽。音檔（m4a）放在公開 repo 的 GitHub Release，可以直接在本頁播放，也可以下載。

| 集數 | 標題 | 長度 | 收聽 |
|---|---|---|---|
| S2-01 | 把腦力留給判斷：設計初衷與生態系全景 | 16:08 | <span v-if="!theme.artifact"><audio controls preload="none" :src="audio('S2-01-audio.m4a')"></audio><br></span><a :href="audio('S2-01-audio.m4a')">下載 S2-01-audio.m4a</a>（29.7 MB） |
| S2-02 | BMad-Method 6.12：先想清楚，再讓 AI 動手 | 20:36 | <span v-if="!theme.artifact"><audio controls preload="none" :src="audio('S2-02-audio.m4a')"></audio><br></span><a :href="audio('S2-02-audio.m4a')">下載 S2-02-audio.m4a</a>（37.9 MB） |
| S2-03 | Control Tower v5：一張工單的一生 | 21:43 | <span v-if="!theme.artifact"><audio controls preload="none" :src="audio('S2-03-audio.m4a')"></audio><br></span><a :href="audio('S2-03-audio.m4a')">下載 S2-03-audio.m4a</a>（40.0 MB） |
| S2-04 | BAT：給塔台跑道、無線電和雷達 | 20:32 | <span v-if="!theme.artifact"><audio controls preload="none" :src="audio('S2-04-audio.m4a')"></audio><br></span><a :href="audio('S2-04-audio.m4a')">下載 S2-04-audio.m4a</a>（37.8 MB） |
| S2-05 | 實戰與邊界：放手，但不是放任 | 24:31 | <span v-if="!theme.artifact"><audio controls preload="none" :src="audio('S2-05-audio.m4a')"></audio><br></span><a :href="audio('S2-05-audio.m4a')">下載 S2-05-audio.m4a</a>（45.1 MB） |

語音版的授權與簡報相同，見[簡報下載](#簡報下載)最後的說明。

## 簡報下載

五集的投影片 PDF 都放在公開 repo 的 GitHub Release，點連結直接下載。

| 集數 | 標題 | 簡報 PDF |
|---|---|---|
| S2-01 | 把腦力留給判斷：設計初衷與生態系全景 | <a :href="pdf('S2-01-ecosystem.pdf')">S2-01-ecosystem.pdf</a>（13.3 MB） |
| S2-02 | BMad-Method 6.12：先想清楚，再讓 AI 動手 | <a :href="pdf('S2-02-bmad-method.pdf')">S2-02-bmad-method.pdf</a>（12.1 MB） |
| S2-03 | Control Tower v5：一張工單的一生 | <a :href="pdf('S2-03-control-tower.pdf')">S2-03-control-tower.pdf</a>（13.7 MB） |
| S2-04 | BAT：給塔台跑道、無線電和雷達 | <a :href="pdf('S2-04-bat.pdf')">S2-04-bat.pdf</a>（11.7 MB） |
| S2-05 | 實戰與邊界：放手，但不是放任 | <a :href="pdf('S2-05-in-practice.pdf')">S2-05-in-practice.pdf</a>（12.0 MB） |

投影片是整頁圖片，沒有可選取的文字。

**授權**：簡報 PDF 與完整語音版（m4a）以 [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh-hant)（姓名標示—非商業性—禁止改作）授權，著作權屬節目作者。可以原樣轉載、分享，但要標示出處（節目作者與本頁連結）、限非商業用途、不得改作。

Portal 是摘要，不具權威；影片、語音版與簡報內容以錄製時版本為準，現行做法以 Portal 與 CT reference 為準。
