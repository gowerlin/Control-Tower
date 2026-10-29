<script setup lang="ts">
// 演進史的八個世代：飛行進程條造型——左格是呼號（世代與版號範圍），右格是這一代的動作。
// 版數合計 60，等於 CHANGELOG 的條目數；v1 未編號、不在 CHANGELOG 內。
// 演進史只維護在 Portal（原 EVO 文件已刪除）：之後的版本照 CT CHANGELOG 補進最後一代或新世代（CT 每次發版都要同步更新 Portal）。
// 要改內容可傳 eras 覆蓋預設值。
interface Era {
  callsign: string
  range: string
  dates: string
  count: string
  theme: string
  what: string
}

const ERAS: Era[] = [
  {
    callsign: 'v1',
    range: '未編號',
    dates: '2026-03-27 → 03-28',
    count: '未列入 CHANGELOG',
    theme: '1 個斜線指令',
    what: '塔台在對話裡產生「工作指引包」，使用者自己複製到新 session 執行，做完再把摘要貼回塔台。'
  },
  {
    callsign: 'v2',
    range: '2.1.1',
    dates: '2026-03-28',
    count: '1 版',
    theme: '檔案驅動的工單',
    what: '工作指引改寫進 .md 工單檔；/ct-exec 跑完整生命週期，/ct-done 補救收尾，/ct-status 查狀態。Debug 三層防線與 Context 衛生在這時寫下。'
  },
  {
    callsign: 'v3',
    range: '3.0.0–3.6.1',
    dates: '03-30 → 04-10',
    count: '8 版',
    theme: 'Skill 化 · 會學習',
    what: '改成 SKILL.md 加按需載入的 references；加入四級能力、自我學習、跨 session 的塔台記憶，定出三層資料與跨專案協調。'
  },
  {
    callsign: 'v4',
    range: '4.0.0–4.4.1',
    dates: '04-15 → 04-25',
    count: '11 版',
    theme: '流程平台 · BAT · YOLO',
    what: 'BUG／PLAN／EXP 單據、歸檔、決策日誌、研究型工單與 Renew；4.1 接上 BAT，4.2 加入 yolo，4.3 讓 Worker 改讀塔台傳來的 CT_MODE。'
  },
  {
    callsign: 'v5.0',
    range: '5.0.0–5.0.9',
    dates: '04-28 → 10-04',
    count: '10 版',
    theme: 'Metadata 改版 · 治理收斂',
    what: '唯一一次主版號升級：工單 metadata 改以 YAML frontmatter 為事實來源。5.0.3 把 SKILL.md 改成路由器並相容 Codex，之後把散落的規則收斂成一處權威定義。'
  },
  {
    callsign: 'v5.1–5.2',
    range: '5.1.0–5.2.3',
    dates: '10-15 → 10-16',
    count: '5 版',
    theme: '分頁生命週期',
    what: '塔台開始管理 BAT 分頁本身：收單後回收 Worker 分頁、啟動時宣告自己是塔台。'
  },
  {
    callsign: 'v5.2.4–5.9',
    range: '5.2.4–5.9.0',
    dates: '10-17 → 10-18',
    count: '17 版',
    theme: 'BAT 0.7 委派 · 隔離、觀測、對話',
    what: 'BAT 先定介面、再委派 CT 寫規則：範圍權杖、worktree 隔離與合併工單、yolo Worker 改問塔台、斷點 D、Worker 啟動確認、跨 session 認出對方的塔台。'
  },
  {
    callsign: 'v5.10–5.13',
    range: '5.10.0–5.13.0',
    dates: '10-20 → 10-29',
    count: '12 版',
    theme: 'Workflow 規則層 · 重派前回收 · 狀態衛生',
    what: '替 Workflow 工具在工單裡定位置：它是單張工單內的執行方式，要明文授權才能用；閘門 G2 沒過，範圍縮小。5.12 在重派前先回收舊 Worker 分頁。5.13 讓 BAT 指揮塔面板穩定讀得到 CT 寫的檔，並讓未結清單只留真的還要做的事。'
  }
]

const props = defineProps<{ eras?: Era[] }>()
const list = props.eras ?? ERAS
</script>

<template>
  <ol class="tour-generations era-timeline" aria-label="CT 的世代">
    <li v-for="(era, i) in list" :key="era.callsign" :class="{ 'is-current': i === list.length - 1 }">
      <p class="tour-gen-name">
        {{ era.callsign }}<span v-if="i === list.length - 1" class="era-tag">目前</span>
        <small>{{ era.range }} · {{ era.dates }} · {{ era.count }}</small>
      </p>
      <p class="tour-gen-line"><b>主題</b><span>{{ era.theme }}</span></p>
      <p class="tour-gen-line"><b>動作</b><span>{{ era.what }}</span></p>
    </li>
  </ol>
</template>
