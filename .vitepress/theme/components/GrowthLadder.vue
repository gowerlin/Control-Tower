<script setup lang="ts">
// 知識成熟度管線（沿用 BAT 的 GrowthLadder，文案對齊 control-tower-guide/references/concepts.md § 知識成熟度管線）：
// L0 觀察 → L1 驗證 → L2 Playbook → L3 Skill。靜態，不做動畫。
// 琥珀只用在「塔台記下」的第一格（塔台的顏色）；「你決定」的兩格用「你要做的事」的藍框。
withDefaults(defineProps<{ detailed?: boolean }>(), { detailed: false })

interface Rung {
  level: string
  name: string
  who: string
  short: string
  long: string
  tower?: boolean
  you?: boolean
}

const RUNGS: Rung[] = [
  {
    level: 'L0',
    name: '觀察',
    who: '塔台記下 · 🔵',
    short: '從做完的工單裡記下一條觀察',
    long: '工單執行中發現的模式，先記成 _learnings.md 裡的一條觀察（🔵 new）。',
    tower: true
  },
  {
    level: 'L1',
    name: '驗證',
    who: '兩張以上工單之後 · 🟢',
    short: '同一個模式一再出現，標成已驗證',
    long: '同一個模式在兩張以上工單重複出現，*evolve 把它標成 validated（專案層的 🟢；全域層的 🟢 要兩個以上專案）；之後派發前比對到類似情境，塔台會主動帶上。'
  },
  {
    level: 'L2',
    name: 'Playbook',
    who: '你決定',
    short: '夠成熟了，寫成標準操作程序',
    long: '已驗證、且你確認之後，用 *evolve --playbook 寫成 _playbooks/ 裡的標準操作程序。',
    you: true
  },
  {
    level: 'L3',
    name: 'Skill',
    who: '你決定',
    short: '做成任何專案都能用的 skill',
    long: 'Playbook 在三個以上專案用過，*evolve --skill 只產出 skill brief；要不要真的安裝成 skill，由你決定。',
    you: true
  }
]
</script>

<template>
  <ol class="growth-ladder" :class="{ 'is-detailed': detailed }" aria-label="知識成熟度管線" data-pl-zoom>
    <li v-for="rung in RUNGS" :key="rung.name" class="gl-rung" :class="{ 'is-tower': rung.tower, 'is-you': rung.you }">
      <span class="gl-node" aria-hidden="true" />
      <p class="gl-name">{{ rung.name }}</p>
      <p class="gl-who">{{ rung.level }} · {{ rung.who }}</p>
      <p class="gl-text">{{ detailed ? rung.long : rung.short }}</p>
    </li>
  </ol>
</template>
