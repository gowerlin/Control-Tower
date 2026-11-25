<script setup lang="ts">
import { computed } from 'vue'
import { withBase } from 'vitepress'

// 沿用 BAT 的 FeatureGrid，資料集換成 CT 內容。
interface Feature {
  title: string
  body: string
  // 卡片底下的一句註腳
  note?: string
  // 標題連到的頁面（站內路徑，不含 base）
  link?: string
  // 'you'：這一格講的是「你要做的事」，框線用「你 = 藍」
  tone?: 'you'
}

type FeatureSet = 'pains' | 'routes' | 'principles' | 'features'

const props = withDefaults(defineProps<{ set?: FeatureSet }>(), { set: 'pains' })

// 首頁「四個 AI 協作痛點 → CT 怎麼接住」（control-tower-guide/references/concepts.md § Control Tower 解決的四個 AI 協作痛點）
const PAINS: Feature[] = [
  {
    title: 'Context 污染',
    body: '塔台不碰程式碼，只看工單、回報與決定，記憶保持乾淨；實作留給每張工單一個全新的 Worker。',
    link: '/deep/principles/tower-and-workers'
  },
  {
    title: 'AI 失憶',
    body: '工單是 repo 裡的 Markdown 檔。新的 session 讀檔就能接手，不靠對話記憶。',
    link: '/deep/principles/files-as-truth'
  },
  {
    title: '協調崩壞',
    body: '明確的狀態機與進度追蹤；派工前比對每張工單會動到的檔案，防止偏離、重複與互相覆蓋。',
    link: '/deep/features/work-orders'
  },
  {
    title: 'Token 浪費',
    body: '工單寫明目標、範圍、驗收條件與不准碰的東西，Worker 不用重新聽一遍背景。',
    link: '/lifecycle'
  }
]

// 首頁「三條延伸路線」
const ROUTES: Feature[] = [
  {
    title: 'Guide Skill',
    body: '想系統性學 CT 或 BMad-Method：裝上互動式學習指南 CT Guide 與 BMad Guide，用問的，它們會畫可點擊的圖給你看。',
    link: '/guide/'
  },
  {
    title: '進階：設計理念與功能深入',
    body: '想知道規則是什麼、為什麼這樣定：7 篇設計理念、12 篇功能深入。',
    link: '/deep/'
  },
  {
    title: '課程',
    body: '想看一個完整專案怎麼用 BMad、CT、BAT 一路做完。',
    link: '/course'
  }
]

// /deep/ 總覽：設計理念 7 篇
const PRINCIPLES: Feature[] = [
  { title: '認知作業系統', body: 'CT 是 Cognitive OS，不是 workflow 工具：檔案、context window 與無狀態呼叫的對應。', link: '/deep/principles/cognitive-os' },
  { title: '檔案即真相來源', body: '為什麼不靠對話記憶；frontmatter 是機器的事實來源，先寫回報再改狀態。', link: '/deep/principles/files-as-truth' },
  { title: '塔台不讀程式碼', body: '塔台與 Worker 為什麼分開，以及問題該問誰。', link: '/deep/principles/tower-and-workers' },
  { title: '三層資料與記憶', body: 'Core Skills、Global、Project 三層，與塔台記憶的晉升和恢復。', link: '/deep/principles/data-layers' },
  { title: '可逆與不可逆的界線', body: '可逆的事放手，不可逆的事要明文授權或經過斷點。', link: '/deep/principles/boundaries' },
  { title: '治理：單一權威', body: '每條規則只有一個權威定義，其他地方用交叉引用；摘要不具權威。', link: '/deep/principles/governance' },
  { title: '會學習的系統', body: '從觀察到 Playbook 再到 Skill，也讓系統公開質疑自己。', link: '/deep/principles/learning' }
]

// /deep/ 總覽：功能深入 12 篇
const FEATURES: Feature[] = [
  { title: '工單系統', body: '編號、粒度、模板欄位、overlap check 與回報處理。', link: '/deep/features/work-orders' },
  { title: '派工：auto-session 與 BAT', body: '四種派工模式、成功判讀、啟動確認與降級鏈。', link: '/deep/features/dispatch' },
  { title: '待辦分頁（BAT ↔ CT 契約 v2）', body: '塔台把要你決定、要你執行的事寫進檔案，BAT 待辦分頁唯讀顯示，回覆結尾重列。', link: '/deep/features/bat-todo' },
  { title: 'yolo 與斷點 A–E', body: '自主推進，以及五種斷點什麼時候停下來。', link: '/deep/features/yolo' },
  { title: 'Worker 向塔台提問', body: 'yolo 下 Worker 改問塔台：提問通道、工單通道與逾時備援。', link: '/deep/features/worker-questions' },
  { title: 'worktree 隔離與合併', body: '隔離派工時 Worker 的規則、直接合併判準與三種合併模式。', link: '/deep/features/worktree-merge' },
  { title: '落點檢查', body: 'Worker 動手前怎麼確認自己在對的 repo。', link: '/deep/features/landing-check' },
  { title: '中斷、Renew 與補救收尾', body: 'HOTFIX 插隊、Renew，以及 ct-done 和重派 ct-exec 的分界。', link: '/deep/features/recovery' },
  { title: 'BUG／PLAN／EXP 與研究型工單', body: '多種單據的狀態機與跨類型關聯。', link: '/deep/features/record-types' },
  { title: '自我學習、Playbook 與 Workflow', body: '學習紀錄、Playbook 引擎，以及 Skill／Playbook／Workflow 的分工。', link: '/deep/features/learning-playbook-workflow' },
  { title: '跨塔台與跨專案協作', body: '五種協調類型、工單前綴與跨 session 選收件人。', link: '/deep/features/multi-tower' },
  { title: '觀測與改進', body: 'ct-status、決策日誌、ct-insights 與 FIELDGUIDE。', link: '/deep/features/observability' }
]

const SETS: Record<FeatureSet, Feature[]> = { pains: PAINS, routes: ROUTES, principles: PRINCIPLES, features: FEATURES }

const features = computed(() => SETS[props.set])
</script>

<template>
  <ul class="features" :class="`is-${set}`">
    <li v-for="f in features" :key="f.title" class="feature" :class="{ 'is-you': f.tone === 'you' }">
      <h3 class="feature-title">
        <a v-if="f.link" :href="withBase(f.link)">{{ f.title }}</a>
        <template v-else>{{ f.title }}</template>
      </h3>
      <p class="feature-body">{{ f.body }}</p>
      <p v-if="f.note" class="feature-note">{{ f.note }}</p>
    </li>
  </ul>
</template>
