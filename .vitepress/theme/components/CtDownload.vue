<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import type { ThemeConfig } from '../../config.mjs'
import bmadGuide from '../../../data/bmad-guide.json'

// 取得方式（取代 BAT 的 DownloadLinks）：目前版號、GitHub Release 下載連結與安裝步驟。
// 版號讀 ct-release.json（scripts/sync-ct-release.mjs 產生）與 data/bmad-guide.json（跟 BMad-Method 走，bmad-guide 發版時同步更新）。
// 下載網址用 config.mts 的 releasesUrl 組，不寫死版號：tag 是 ct-v<CT 版號>、bmad-guide-v<bmad-guide 版號>，附件名就是 json 裡的 zip 名。
// CT 單一 skill zip 有 8 個，連到該版 Release 頁。安裝步驟摘要自 CT 安裝與使用指南 § 4.1、§ 4.3，詳細步驟在 /install。
const { theme } = useData<ThemeConfig>()
const release = computed(() => theme.value.ctRelease)
const releasesUrl = computed(() => theme.value.releasesUrl)
const ctTag = computed(() => `ct-v${release.value.ctVersion}`)
const ctAsset = (name: string) => `${releasesUrl.value}download/${ctTag.value}/${name}`
const bmadGuideAsset = computed(() => `${releasesUrl.value}download/bmad-guide-v${bmadGuide.version}/${bmadGuide.zip}`)
</script>

<template>
  <div class="ct-download">
    <p class="cd-status">
      <span><b>目前版本</b> CT v{{ release.ctVersion }} · CT Guide v{{ release.guideVersion }}（{{ release.releasedAt }}）· BMad Guide v{{ bmadGuide.version }}（{{ bmadGuide.releasedAt }}）</span>
      <span><b>取得方式</b> 從 GitHub Releases 下載</span>
    </p>
    <ul class="cd-files" aria-label="發行檔">
      <li v-if="release.zip">
        <a class="download-item" :href="ctAsset(release.zip)">
          <span class="download-label">BMad Control Tower</span>
          <span class="download-note">{{ release.zip }}</span>
        </a>
      </li>
      <li v-if="release.zip">
        <a class="download-item" :href="`${releasesUrl}tag/${ctTag}`" target="_blank" rel="noreferrer">
          <span class="download-label">CT 單一 skill zip（claude.ai 上傳用）</span>
          <span class="download-note">8 個 &lt;skill&gt;-v{{ release.ctVersion }}.zip，在 v{{ release.ctVersion }} 的 Release 頁</span>
        </a>
      </li>
      <li v-if="release.guideZip">
        <a class="download-item" :href="ctAsset(release.guideZip)">
          <span class="download-label">CT Guide Skill</span>
          <span class="download-note">{{ release.guideZip }}</span>
        </a>
      </li>
      <li v-if="bmadGuide.zip">
        <a class="download-item" :href="bmadGuideAsset">
          <span class="download-label">BMad Guide Skill</span>
          <span class="download-note">{{ bmadGuide.zip }}</span>
        </a>
      </li>
    </ul>
    <p class="cd-more">舊版本：所有版本見 <a :href="releasesUrl" target="_blank" rel="noreferrer">GitHub Releases</a></p>
    <p class="cd-steps-title">下載之後</p>
    <ol class="cd-steps">
      <li>zip 解壓縮後，根層直接是 8 個 skill 目錄（不含 <code>docs/</code>）；發行目錄版則是 <code>skills/</code> 底下 8 個 skill 目錄，另附 <code>docs/</code>。</li>
      <li>Claude Code 放到 <code>~/.claude/skills/&lt;skill&gt;/</code>；Codex 放到 <code>~/.codex/skills/&lt;skill&gt;/</code>。塔台與 Worker 用同一批，一起升級。</li>
      <li>BMad Guide 是單一 skill，安裝目錄名是 <code>bmad-guide</code>；它的 zip 最上層是帶版號的資料夾，詳見<a :href="withBase('/install#bmad-guide')">安裝 BMad Guide Skill</a>。</li>
      <li>開一個新的 session，輸入 <code>/control-tower</code>（Codex 用 <code>$control-tower</code>）。新版從下一個 session 才生效。</li>
    </ol>
    <p class="cd-more">升級、備份與回退的完整步驟：<a :href="withBase('/install')">安裝</a></p>
  </div>
</template>
