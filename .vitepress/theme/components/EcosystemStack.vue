<script setup lang="ts">
// 五塊積木：BMad-Method、CT、BAT 與兩個 Guide skill 怎麼疊在一起。
// 原圖：design/ecosystem-stack-source.html（使用者的 artifact 快照）。積木結構、配色與點選互動照原圖；
// 版號讀 ct-release.json 與 data/bmad-guide.json，說法對齊 /features、/guide/、/deep/features/dispatch。
// SSR 輸出就可讀：積木說明先以清單列在圖下方，有 client JS 時才換成點選面板。
import { computed, onMounted, ref } from 'vue'
import { useData } from 'vitepress'
import type { ThemeConfig } from '../../config.mjs'
import bmadGuide from '../../../data/bmad-guide.json'

type Key = 'user' | 'bmad' | 'bmadguide' | 'ct' | 'ctguide' | 'bat' | 'repo'

interface Info {
  key: Key
  accent: string
  title: string
  desc: string
}

interface Tile {
  x: number
  name: string
  note: string
  face: string
  shade: string
}

const { theme } = useData<ThemeConfig>()
const release = computed(() => theme.value.ctRelease)

// 由上往下的順序，也是靜態清單的順序
const INFO = computed<Info[]>(() => [
  {
    key: 'user',
    accent: '#FFC400',
    title: '你（開發者）',
    desc: '在塔台 session 下達需求、審核結果；即使全自動，該你決定的事也會回到你手上。需要概念或流程時，隨時問兩個 Guide skill。'
  },
  {
    key: 'bmad',
    accent: '#7B3FF2',
    title: 'BMad-Method',
    desc: 'AI 輔助開發的工作流方法論。把工作拆成分析、規劃、方案設計與實作幾個階段，由不同角色的 Agent（Mary、John、Winston、Amelia……）與 bmad-* skill 承接。'
  },
  {
    key: 'bmadguide',
    accent: '#B79BF2',
    title: 'BMad Guide（bmad-guide）',
    desc: `BMad-Method 的互動式學習指南，回答「現在在哪個階段、下一步該跑哪個 bmad-* skill」，也認得已經改名或退役的 skill。它是 CT 的外部依賴：塔台偵測到它才拿來查 BMad 流程，沒裝也照常運作。版號跟 BMad-Method 走，目前 v${bmadGuide.version}（BMad-Method v${bmadGuide.bmadMethodVersion}）。`
  },
  {
    key: 'ct',
    accent: '#0B7A62',
    title: 'BMad Control Tower（CT）',
    desc: `用檔案式工單管理多 Agent 工作，由 1 個塔台 skill 和 7 個 Worker／輔助 skill 組成。塔台對齊需求、開單、派工、收單，不寫產品程式碼；Worker 在自己的 session 用 ct-exec 執行一張工單並回報。CT 不內嵌 BMad-Method 內容，偵測到 bmad-guide 才讀它；沒有它時，工作流程欄位改由你手動指定。目前 v${release.value.ctVersion}。`
  },
  {
    key: 'ctguide',
    accent: '#8ED7B8',
    title: 'CT Guide（control-tower-guide）',
    desc: `CT 的教科書，講塔台與 Worker、工單、派工、治理為什麼這樣設計，另有 bat-integration 專章說明 CT 與 BAT 怎麼分工。它獨立安裝，不是 CT 的 8 個 skill 之一；要確切的指令語法，問 ct-help。版號與 CT 相同，目前 v${release.value.guideVersion}。`
  },
  {
    key: 'bat',
    accent: '#1D5FD6',
    title: 'BAT（Better Agent Terminal）',
    desc: '多終端工作區，BAT 定義介面，CT 負責呼叫。塔台用 bat-terminal.mjs 請 BAT 開 Worker 分頁（Claude Code 或 Codex，由 BAT 依設定決定），也用它宣告塔台角色、要求 worktree 隔離；Worker 完成後用 bat-notify 回報塔台；BAT MCP 提供唯讀查詢。BAT 是可選的：沒有它，塔台改給你一行可以手動照做的指令。'
  },
  {
    key: 'repo',
    accent: '#1F7A45',
    title: '專案 repo 與檔案系統',
    desc: '工單、報告、決策日誌與程式碼都是 repo 裡的檔案，塔台與 Worker 以這些檔案為共同依據。CT 的核心只靠這些檔案就能運作。'
  }
])

const BMAD_TILES: Tile[] = [
  { x: 194, name: '分析', note: 'Mary 分析師', face: '#FF5C8A', shade: '#CC3F70' },
  { x: 320, name: '規劃', note: 'John 產品經理', face: '#FFB400', shade: '#C98A00' },
  { x: 446, name: '方案設計', note: 'Winston 架構師', face: '#22C3E6', shade: '#1895B5' },
  { x: 572, name: '實作', note: 'Amelia 開發', face: '#8BD34A', shade: '#5E9B26' }
]

// 塔台 skill 加 7 個 Worker／輔助 skill（/features#skills），兩列各四塊
const CT_TILES: Tile[][] = [
  [
    { x: 194, name: 'control-tower', note: '塔台', face: '#FFD43B', shade: '#C9A100' },
    { x: 320, name: 'ct-exec', note: '執行工單', face: '#FF8A3D', shade: '#C65A12' },
    { x: 446, name: 'ct-done', note: '補救收尾', face: '#FF6B9A', shade: '#CC3F70' },
    { x: 572, name: 'ct-fieldguide', note: 'FIELDGUIDE', face: '#8BD34A', shade: '#5E9B26' }
  ],
  [
    { x: 194, name: 'ct-status', note: '查看狀態', face: '#5CC8FF', shade: '#2A94C8' },
    { x: 320, name: 'ct-evolve', note: '萃取學習', face: '#B18CFF', shade: '#7C58CC' },
    { x: 446, name: 'ct-insights', note: '分析洞察', face: '#E9EDF5', shade: '#AEB6C8' },
    { x: 572, name: 'ct-help', note: '操作手冊', face: '#FFB400', shade: '#C98A00' }
  ]
]

const BAT_TILES: Tile[] = [
  { x: 194, name: '塔台分頁', note: '宣告塔台角色', face: '#FFD43B', shade: '#C79A00' },
  { x: 320, name: 'Worker 分頁', note: 'Claude Code', face: '#FF6B9A', shade: '#CC3F70' },
  { x: 446, name: 'Worker 分頁', note: 'Codex', face: '#8BD34A', shade: '#5E9B26' },
  { x: 572, name: 'BAT MCP', note: '唯讀查詢', face: '#5CC8FF', shade: '#2A94C8' }
]

// 積木上緣的凸點（原圖用 JS 產生，這裡在 SSR 就算好）
function studs(x: number, w: number): number[] {
  const n = Math.floor((w - 24 + 18) / 46)
  const start = x + (w - (n * 28 + (n - 1) * 18)) / 2
  return Array.from({ length: n }, (_, i) => start + i * 46)
}

const live = ref(false)
const selected = ref<Key | null>(null)
const current = computed(() => INFO.value.find(i => i.key === selected.value) ?? null)

onMounted(() => {
  live.value = true
})

function pick(key: Key) {
  selected.value = key
}

function onKey(e: KeyboardEvent, key: Key) {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    pick(key)
  }
}

// 只有 client JS 在時，積木才是按鈕
function brickAttrs(key: Key, label: string) {
  if (!live.value) return {}
  return {
    role: 'button',
    tabindex: 0,
    'aria-label': label,
    'aria-pressed': selected.value === key ? 'true' : 'false'
  }
}
</script>

<template>
  <figure class="eco-stack" :class="{ 'is-live': live }">
    <p class="eco-hint">圖比畫面寬，可以左右滑動看完整張。</p>
    <div class="eco-scroll">
      <svg
        viewBox="0 0 880 796"
        :role="live ? 'group' : 'img'"
        aria-labelledby="eco-title eco-desc"
      >
        <title id="eco-title">BMad-Method、BMad Control Tower、BAT 與兩個 Guide skill 的積木堆疊圖</title>
        <desc id="eco-desc">由上往下依序為你、BMad-Method、BMad Control Tower、BAT 與專案 repo。BMad Guide 貼在 BMad-Method 右側，CT Guide 貼在 Control Tower 左側。</desc>
        <defs>
          <marker id="eco-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M1 1 L9 5 L1 9 z" class="eco-soft" />
          </marker>
        </defs>

        <!-- 底板 -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'repo' }" v-bind="brickAttrs('repo', '專案 repo 與檔案系統')" @click="pick('repo')" @keydown="onKey($event, 'repo')">
          <g v-for="sx in studs(150, 580)" :key="sx"><rect :x="sx" y="741" width="28" height="11" rx="4" fill="#1F7A45" /><rect :x="sx + 5" y="743" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="150" y="750" width="580" height="38" rx="12" fill="#145A31" />
          <rect class="eco-face" x="150" y="750" width="580" height="32" rx="12" fill="#1F7A45" />
          <text x="440" y="772" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">專案 repo 與檔案系統：工單、報告、程式碼都放這裡</text>
        </g>

        <!-- BAT -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'bat' }" v-bind="brickAttrs('bat', 'BAT')" @click="pick('bat')" @keydown="onKey($event, 'bat')">
          <g v-for="sx in studs(170, 540)" :key="sx"><rect :x="sx" y="541" width="28" height="11" rx="4" fill="#1D5FD6" /><rect :x="sx + 5" y="543" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="170" y="550" width="540" height="200" rx="14" fill="#1446A1" />
          <rect class="eco-face" x="170" y="550" width="540" height="192" rx="14" fill="#1D5FD6" />
          <text x="194" y="590" font-size="22" font-weight="900" fill="#fff">BAT　Better Agent Terminal</text>
          <text x="194" y="612" font-size="13.5" fill="#DCE8FF">多終端工作區，負責開分頁、跑 Agent</text>
          <g font-weight="700" fill="#1B1B1F" text-anchor="middle">
            <g v-for="t in BAT_TILES" :key="t.x">
              <rect :x="t.x" y="631" width="114" height="66" rx="9" :fill="t.shade" />
              <rect :x="t.x" y="628" width="114" height="62" rx="9" :fill="t.face" />
              <text :x="t.x + 57" y="655" font-size="15">{{ t.name }}</text>
              <text :x="t.x + 57" y="676" font-size="12.5" font-weight="500">{{ t.note }}</text>
            </g>
          </g>
          <text x="194" y="723" font-size="13" fill="#DCE8FF">Worker 完成後以 bat-notify 回報塔台</text>
        </g>

        <!-- CT Guide（左側） -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'ctguide' }" v-bind="brickAttrs('ctguide', 'CT Guide')" @click="pick('ctguide')" @keydown="onKey($event, 'ctguide')">
          <g v-for="sx in studs(10, 160)" :key="sx"><rect :x="sx" y="391" width="28" height="11" rx="4" fill="#BDEFD9" /><rect :x="sx + 5" y="393" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="10" y="400" width="160" height="120" rx="14" fill="#8ED7B8" />
          <rect class="eco-face" x="10" y="400" width="160" height="113" rx="14" fill="#BDEFD9" />
          <text x="24" y="432" font-size="17" font-weight="900" fill="#0A3A2D">CT Guide</text>
          <text x="24" y="453" font-size="12.5" fill="#0A3A2D">control-tower-guide</text>
          <text x="24" y="478" font-size="13" font-weight="500" fill="#0A3A2D">概念、設計理由</text>
          <text x="24" y="497" font-size="13" font-weight="500" fill="#0A3A2D">與 BAT 整合</text>
        </g>

        <!-- Control Tower -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'ct' }" v-bind="brickAttrs('ct', 'BMad Control Tower')" @click="pick('ct')" @keydown="onKey($event, 'ct')">
          <g v-for="sx in studs(170, 540)" :key="sx"><rect :x="sx" y="271" width="28" height="11" rx="4" fill="#0B7A62" /><rect :x="sx + 5" y="273" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="170" y="280" width="540" height="270" rx="14" fill="#075A48" />
          <rect class="eco-face" x="170" y="280" width="540" height="262" rx="14" fill="#0B7A62" />
          <text x="194" y="318" font-size="22" font-weight="900" fill="#fff">BMad Control Tower　v{{ release.ctVersion }}</text>
          <text x="194" y="340" font-size="13.5" fill="#D3F5EA">塔台與 Worker 用檔案式工單分工</text>
          <g font-weight="700" fill="#1B1B1F" text-anchor="middle">
            <g v-for="(row, r) in CT_TILES" :key="r">
              <g v-for="t in row" :key="t.name">
                <rect :x="t.x" :y="361 + r * 74" width="114" height="60" rx="9" :fill="t.shade" />
                <rect :x="t.x" :y="358 + r * 74" width="114" height="56" rx="9" :fill="t.face" />
                <text :x="t.x + 57" :y="381 + r * 74" font-size="13.5">{{ t.name }}</text>
                <text :x="t.x + 57" :y="401 + r * 74" font-size="12.5" font-weight="500">{{ t.note }}</text>
              </g>
            </g>
          </g>
          <text x="194" y="524" font-size="13" fill="#D3F5EA">也支援 BUG／PLAN／EXP 單據，以及 BAT 派工與 yolo 模式</text>
        </g>

        <!-- BMad Guide（右側） -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'bmadguide' }" v-bind="brickAttrs('bmadguide', 'BMad Guide')" @click="pick('bmadguide')" @keydown="onKey($event, 'bmadguide')">
          <g v-for="sx in studs(710, 160)" :key="sx"><rect :x="sx" y="151" width="28" height="11" rx="4" fill="#DCCBFF" /><rect :x="sx + 5" y="153" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="710" y="160" width="160" height="120" rx="14" fill="#B79BF2" />
          <rect class="eco-face" x="710" y="160" width="160" height="113" rx="14" fill="#DCCBFF" />
          <text x="748" y="192" font-size="17" font-weight="900" fill="#2A1066">BMad Guide</text>
          <text x="748" y="213" font-size="12.5" fill="#2A1066">bmad-guide</text>
          <text x="748" y="238" font-size="13" font-weight="500" fill="#2A1066">學習導覽與</text>
          <text x="748" y="257" font-size="13" font-weight="500" fill="#2A1066">workflow 路由</text>
        </g>

        <!-- BMad-Method -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'bmad' }" v-bind="brickAttrs('bmad', 'BMad-Method')" @click="pick('bmad')" @keydown="onKey($event, 'bmad')">
          <g v-for="sx in studs(170, 540)" :key="sx"><rect :x="sx" y="91" width="28" height="11" rx="4" fill="#7B3FF2" /><rect :x="sx + 5" y="93" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="170" y="100" width="540" height="180" rx="14" fill="#5424BD" />
          <rect class="eco-face" x="170" y="100" width="540" height="172" rx="14" fill="#7B3FF2" />
          <text x="194" y="134" font-size="22" font-weight="900" fill="#fff">BMad-Method</text>
          <text x="194" y="156" font-size="13.5" fill="#F4EFFF">AI 輔助開發的工作流方法論</text>
          <g font-weight="700" fill="#1B1B1F" text-anchor="middle">
            <g v-for="t in BMAD_TILES" :key="t.x">
              <rect :x="t.x" y="182" width="114" height="70" rx="9" :fill="t.shade" />
              <rect :x="t.x" y="178" width="114" height="66" rx="9" :fill="t.face" />
              <text :x="t.x + 57" y="206" font-size="15">{{ t.name }}</text>
              <text :x="t.x + 57" y="228" font-size="12.5" font-weight="500">{{ t.note }}</text>
            </g>
          </g>
        </g>

        <!-- 你 -->
        <g class="eco-brick" :class="{ 'is-sel': selected === 'user' }" v-bind="brickAttrs('user', '你（開發者）')" @click="pick('user')" @keydown="onKey($event, 'user')">
          <g v-for="sx in studs(340, 200)" :key="sx"><rect :x="sx" y="31" width="28" height="11" rx="4" fill="#FFC400" /><rect :x="sx + 5" y="33" width="18" height="2" rx="1" fill="#fff" opacity=".4" /></g>
          <rect x="340" y="40" width="200" height="60" rx="14" fill="#D99E00" />
          <rect class="eco-face" x="340" y="40" width="200" height="54" rx="14" fill="#FFC400" />
          <text x="440" y="64" text-anchor="middle" font-size="17" font-weight="900" fill="#2B2100">你（開發者）</text>
          <text x="440" y="83" text-anchor="middle" font-size="12.5" fill="#2B2100">在塔台 session 下達需求</text>
        </g>

        <!-- 讀取與參照 -->
        <path class="eco-route" d="M710 420 H770 V286" marker-end="url(#eco-arr)" />
        <text class="eco-ink" x="780" y="350" font-size="13" font-weight="700">塔台讀取</text>
        <text class="eco-ink" x="780" y="369" font-size="13" font-weight="700">bmad-guide</text>

        <path class="eco-route" d="M30 524 V660 H166" marker-end="url(#eco-arr)" />
        <text class="eco-ink" x="40" y="596" font-size="13" font-weight="700">bat-integration</text>
        <text class="eco-ink" x="40" y="615" font-size="13" font-weight="700">章節</text>

        <!-- 接縫標籤 -->
        <g font-size="13" font-weight="700" text-anchor="middle">
          <rect class="eco-pill" x="210" y="266" width="460" height="28" rx="14" />
          <text class="eco-ink" x="440" y="285">▲ 塔台讀取 bmad-guide，依專案階段查出 BMad 流程</text>
          <rect class="eco-pill" x="230" y="536" width="420" height="28" rx="14" />
          <text class="eco-ink" x="440" y="555">▼ 派工 bat-terminal.mjs　▲ 回報 bat-notify</text>
          <rect class="eco-pill" x="682" y="252" width="56" height="22" rx="11" />
          <text class="eco-ink" x="710" y="268" font-size="12.5">解說</text>
          <rect class="eco-pill" x="142" y="494" width="56" height="22" rx="11" />
          <text class="eco-ink" x="170" y="510" font-size="12.5">解說</text>
        </g>
      </svg>
    </div>

    <div v-if="live" class="eco-panel" aria-live="polite" :style="current ? { borderLeftColor: current.accent } : undefined">
      <template v-if="current">
        <p class="eco-panel-title">{{ current.title }}</p>
        <p>{{ current.desc }}</p>
      </template>
      <template v-else>
        <p class="eco-panel-title">點選積木</p>
        <p>每一塊都能點，也能用鍵盤的 Tab 與 Enter 操作。</p>
      </template>
    </div>
    <ul v-else class="eco-list" aria-label="每塊積木的說明">
      <li v-for="i in INFO" :key="i.key" :style="{ borderLeftColor: i.accent }">
        <p class="eco-panel-title">{{ i.title }}</p>
        <p>{{ i.desc }}</p>
      </li>
    </ul>

    <div class="eco-notes">
      <div>
        <p class="eco-notes-title">怎麼讀這張圖</p>
        <ul>
          <li>積木由上往下堆：方法、編排、執行環境，最底下是 repo</li>
          <li>淺色側磚是學習指南（Guide skill）</li>
          <li>虛線是讀取或參照</li>
          <li>彩色小磚是磚內的元件；CT 的小磚是它的 8 個 skill</li>
          <li>{{ live ? '點選積木看詳細說明' : '每塊積木的說明列在圖下方' }}</li>
        </ul>
      </div>
      <div>
        <p class="eco-notes-title">一次派工的流程</p>
        <ol>
          <li>你在塔台下達需求</li>
          <li>塔台建立工單</li>
          <li>塔台用 bat-terminal.mjs 請 BAT 開 Worker 分頁</li>
          <li>Worker 執行 ct-exec（Claude Code 是 <code>/ct-exec</code>，Codex 是 <code>$ct-exec</code>，用 plugin 安裝的 Codex 是 <code>$ct:ct-exec</code>）</li>
          <li>Worker 用 bat-notify 回報塔台</li>
        </ol>
      </div>
    </div>
  </figure>
</template>
