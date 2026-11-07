<script setup lang="ts">
// 四級能力（沿用 BAT，文案對齊 control-tower-guide/references/ecosystem.md § 能力等級）：第 0 級是只靠檔案的核心，其餘三級是可選的增強，可以任意組合。
// 桌面：三個增強並排，坐在第 0 級上（可任意組合，不是階梯）；窄螢幕照 DOM 順序 0 → 3。
// 虛線框 = 可選；實線 = 核心。
interface Level {
  name: string
  what: string
  fit: string
  core?: boolean
}

const LEVELS: Level[] = [
  {
    name: '自包含核心',
    what: '零相依，只靠 repo 裡的檔案。工單、進度追蹤、Debug、中斷處理、多塔台協調與自我學習（_learnings.md），都在這一級。',
    fit: '任何專案的起點；不裝任何東西也能用。',
    core: true
  },
  {
    name: '加上 ECC hook 觀察',
    what: '裝了 ECC continuous-learning-v2 後，塔台多一份以 hook 記錄的觀察來源，經驗的置信度更有依據。6.0.0 起退場：CT 不再寫 observation、不讀置信度，編號保留。',
    fit: '只在 5.x；6.0.0 起不需要。'
  },
  {
    name: '加上 bmad-guide',
    what: '偵測到另外安裝的 bmad-guide skill 時，塔台依專案階段查出該走哪一套 BMad-Method 流程，並在工單上標出 Agent 角色。CT 本身不內嵌 BMad 內容。6.0.0 起這一級改稱「方法論轉接」，由內建的 bmad adapter 承接，行為相同。',
    fit: '已經在用 BMad-Method 的團隊。'
  },
  {
    name: '加上 mem0 跨裝置記憶',
    what: '把已確立的經驗同步到 mem0，換電腦也帶得走。目前只單向寫出，不會反過來查詢。6.0.0 起要在專案的本地規則記錄例外才啟用。',
    fit: '在好幾台機器上工作。'
  }
]
</script>

<template>
  <ol class="cap-levels" aria-label="四級能力">
    <li v-for="(level, i) in LEVELS" :key="level.name" class="cap-level" :class="{ 'is-core': level.core }">
      <p class="cap-head">
        <span class="cap-num">第 {{ i }} 級</span>
        <span class="cap-kind">{{ level.core ? '核心' : '可選' }}</span>
      </p>
      <p class="cap-name">{{ level.name }}</p>
      <p class="cap-what">{{ level.what }}</p>
      <p class="cap-fit"><b>適合</b>{{ level.fit }}</p>
    </li>
  </ol>
</template>
