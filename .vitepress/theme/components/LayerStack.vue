<script setup lang="ts">
// 三層資料：Core Skills／Global／Project。
// 來源：control-tower/references/data-layer-architecture.md § 架構總覽、§ 核心原則（載入順序、覆蓋優先級、寫入規則）。純 SSR。
interface Layer {
  id: string
  name: string
  kind: string
  what: string
  path: string
  rule: string
  tone: 'core' | 'global' | 'project'
}

const LAYERS: Layer[] = [
  {
    id: 'Layer 3',
    name: 'Project',
    kind: '專案級',
    what: '這個專案的工單、學習紀錄、Playbook、本地規則、設定、塔台記憶與決策日誌。跟程式碼一起進版控。',
    path: '<專案根目錄>/_ct-workorders/',
    rule: '覆蓋優先級最高',
    tone: 'project'
  },
  {
    id: 'Layer 2',
    name: 'Global',
    kind: '使用者級，跨專案',
    what: '跨專案通用的模式與踩過的坑、從專案晉升的 Playbook、全域設定與跨專案索引。升級 CT 不會碰。',
    path: '~/.claude/control-tower-data/',
    rule: '專案沒有設定時套用',
    tone: 'global'
  },
  {
    id: 'Layer 1',
    name: 'Core Skills',
    kind: '唯讀',
    what: '8 個 skill 本體。升級時整份覆蓋；不是 skill 定義檔的東西一律不得寫進這個路徑，連備份也不行。plugin 安裝的只能用 plugin 指令寫入。',
    path: '~/.claude/skills/<skill>/、~/.codex/skills/<skill>/；plugin 安裝：~/.claude/plugins/（設了 CLAUDE_CONFIG_DIR 或 CLAUDE_CODE_PLUGIN_CACHE_DIR 時跟著搬）、~/.codex/plugins/',
    rule: '預設值',
    tone: 'core'
  }
]
</script>

<template>
  <figure class="layer-stack" aria-label="CT 的三層資料">
    <ol class="ls-layers">
      <li v-for="layer in LAYERS" :key="layer.id" class="ls-layer" :class="`is-${layer.tone}`">
        <p class="ls-name"><small>{{ layer.id }}</small>{{ layer.name }}<small>{{ layer.kind }}</small></p>
        <p class="ls-what">{{ layer.what }}</p>
        <p class="ls-path">{{ layer.path }}</p>
        <p class="ls-rule"><b>覆蓋</b> {{ layer.rule }}</p>
      </li>
    </ol>
    <div class="ls-order">
      <p><b>載入順序</b>　Core → Global → Project</p>
      <p><b>覆蓋優先級</b>　Project ＞ Global ＞ Core</p>
    </div>
  </figure>
</template>
