<script setup lang="ts">
// yolo 斷點 A–E 落在流程的哪一步。
// 來源：control-tower/references/yolo-mode.md § 斷點判準（A / B / C / D / E）、§ 使用者中斷；control-tower/references/auto-session.md § 派發後行為 › auto-session = yolo。
// 純 SSR：每一步列出會在這裡觸發的斷點（符號 + 文字）。
interface Point {
  key: string
  when: string
  then: string
}

interface Stage {
  name: string
  who: string
  points: Point[]
}

const STAGES: Stage[] = [
  { name: '派工', who: '塔台', points: [] },
  {
    name: '執行',
    who: 'Worker',
    points: [
      {
        key: 'D',
        when: 'Worker 在等使用者（權限確認、提問）',
        then: '塔台從 BAT 查到分頁在等人，告訴你去哪個分頁回答；Worker 等的是塔台時不算。'
      }
    ]
  },
  {
    name: '回報',
    who: 'Worker → 塔台',
    points: [
      { key: 'A', when: '回報字串不合規格', then: '不是「T#### 完成／部分完成／需要協助」這類固定字串，塔台停下來請你判讀。漏了前綴的 ID 不算：熱區恰好一張同號的就照收，同號多張或找不到才停。' },
      { key: 'C', when: 'Worker 建議跨出 PLAN 範圍', then: '回報裡建議另開工單、提到拆單表以外的新編號，塔台停下來讓你決定。' }
    ]
  },
  {
    name: '收單與下一張',
    who: '塔台',
    points: [
      { key: 'B', when: 'Renew 太多次，或連續失敗', then: '同一張工單 Renew 次數達到 yolo_max_retries，或連續失敗達到 yolo_max_retries（跨工單的 session 計數：FAILED、BLOCKED 加一，DONE、FIXED、PARTIAL 歸零），塔台停下來，建議拆單或退回 ask。' }
    ]
  },
  {
    name: '合併',
    who: '塔台',
    points: [
      { key: 'E', when: '把隔離工單的結果推進 main 之前', then: '直接合併在 yolo 下判準仍成立就自動 ff；衝突解決有範圍外檔案或驗收沒全綠、等價移植一律停下來等你確認。' }
    ]
  }
]
</script>

<template>
  <figure class="bp-map" aria-label="yolo 斷點落在流程的哪一步">
    <ol class="bp-flow">
      <li v-for="stage in STAGES" :key="stage.name" class="bp-stage">
        <p class="bp-stage-name">{{ stage.name }}<small>{{ stage.who }}</small></p>
        <ul v-if="stage.points.length" class="bp-points">
          <li v-for="p in stage.points" :key="p.key" class="bp-point">
            <span class="bp-key"><span class="sr-only">斷點 </span>{{ p.key }}</span>
            <div>
              <p class="bp-when">{{ p.when }}</p>
              <p class="bp-then">{{ p.then }}</p>
            </div>
          </li>
        </ul>
        <p v-else class="bp-none">— 這一步沒有斷點，yolo 照常推進</p>
      </li>
    </ol>
    <p class="bp-note">任何時候在塔台輸入 <code>停</code>、<code>stop</code> 或 <code>abort</code>，yolo 都會停下來。斷點暫停時，塔台會列出選項等你選，不會自己猜。</p>
  </figure>
</template>
