<script setup lang="ts">
import { withBase } from 'vitepress'

// CT Guide 的學習路線，依讀者分流。
// 來源：control-tower-guide/SKILL.md § Audience routing、§ Reference file routing。每條路線連到 Portal 進階區對應篇。純 SSR。
interface Route {
  who: string
  signal: string
  files: string[]
  portal: { text: string; link: string }
  start?: boolean
}

const ROUTES: Route[] = [
  {
    who: '新手',
    signal: '問「什麼是」「怎麼用」「第一次」',
    files: ['concepts.md', 'ecosystem.md', 'work-order-lifecycle.md'],
    portal: { text: '一張工單的一生', link: '/lifecycle' },
    start: true
  },
  {
    who: '想懂架構的人',
    signal: '三層、同構、Layer 1、跨專案、除錯、Playbook、決策日誌',
    files: ['three-layer-arch.md', 'advanced-patterns.md', 'work-order-lifecycle.md'],
    portal: { text: '進階：設計理念', link: '/deep/' }
  },
  {
    who: '用 yolo 與自動派工的人',
    signal: 'YOLO、auto-session、斷點、提問通道、Codex、落點檢查、單一權威',
    files: ['runtime-dispatch.md', 'governance.md'],
    portal: { text: 'yolo 與斷點 A–E', link: '/deep/features/yolo' }
  },
  {
    who: '搭配 BAT 的人',
    signal: 'BAT、Worker 分頁、範圍權杖、worktree、BAT MCP、啟動確認',
    files: ['bat-integration.md', 'work-order-lifecycle.md（worktree 隔離與合併工單）'],
    portal: { text: '派工：auto-session 與 BAT', link: '/deep/features/dispatch' }
  },
  {
    who: '整合其他工具的人',
    signal: 'BMad-Method、bmad-guide、方法論轉接、pstack、mem0、*import、*onboard',
    files: ['integration.md', 'preview-methodology.md（方法論轉接）'],
    portal: { text: '功能總覽', link: '/features' }
  },
  {
    who: '在意 Workflow 的人',
    signal: 'Workflow、三分法、知識卡、Workflow 授權、閘門 G2',
    files: ['concepts.md（Workflow：單張工單內的執行方式）', 'advanced-patterns.md'],
    portal: { text: '自我學習、Playbook 與 Workflow', link: '/deep/features/learning-playbook-workflow' }
  }
]
</script>

<template>
  <ul class="learning-path" aria-label="依讀者分流的學習路線">
    <li v-for="r in ROUTES" :key="r.who" class="lp-route" :class="{ 'is-start': r.start }">
      <p class="lp-who">{{ r.who }}</p>
      <p class="lp-signal">會問到：{{ r.signal }}</p>
      <ol class="lp-files" :aria-label="`${r.who}：Guide 教材順序`">
        <li v-for="f in r.files" :key="f"><code>{{ f }}</code></li>
      </ol>
      <p class="lp-portal"><span aria-hidden="true">→ </span>Portal：<a :href="withBase(r.portal.link)">{{ r.portal.text }}</a></p>
    </li>
  </ul>
</template>
