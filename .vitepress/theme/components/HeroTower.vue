<script setup lang="ts">
// 首頁主視覺：「一張工單的一生」——塔台開單、派工，Worker 執行、回報，塔台收單；每一步都寫進檔案。
// 純 CSS：信標依序掃過塔台的步驟（reduced motion 時不動）；SSR 靜態輸出就是完整的流程（Artifact 預覽也看得懂）。
// 塔台的步驟用主色實心信標、Worker 的步驟空心。放在首頁深色 Hero 上（.home-hero-grid 的右欄）。
interface Step {
  who: string
  what: string
  file: string
  tower?: boolean
}

const STEPS: Step[] = [
  { who: '塔台', what: '開單', file: 'T0042-checkout-coupon.md · PENDING', tower: true },
  { who: '塔台', what: '派工', file: '/ct-exec T0042 → 新的 Worker', tower: true },
  { who: 'Worker', what: '執行與驗證', file: 'IN_PROGRESS · 只動 affects_files' },
  { who: 'Worker', what: '回報', file: '先寫回報區，再改狀態 · DONE' },
  { who: '塔台', what: '收單', file: '逐項核對證據 · 寫進決策日誌', tower: true }
]
</script>

<template>
  <figure class="hero-tower" aria-labelledby="hero-tower-caption" data-no-zoom>
    <p class="ht-head">
      <span>一張工單的一生</span>
      <span aria-hidden="true">● 塔台　○ Worker</span>
    </p>
    <ol class="ht-steps">
      <li v-for="(step, i) in STEPS" :key="step.what" class="ht-step" :class="{ 'is-tower': step.tower }">
        <span class="ht-mark" aria-hidden="true">{{ i + 1 }}</span>
        <div>
          <p class="ht-who">{{ step.who }}</p>
          <p class="ht-what">{{ step.what }}</p>
          <p class="ht-file">{{ step.file }}</p>
        </div>
      </li>
    </ol>
    <figcaption id="hero-tower-caption" class="ht-foot">
      每一步都留在 repo 裡的檔案：換一個 session、換一個 Agent，脈絡都還在。
    </figcaption>
  </figure>
</template>
