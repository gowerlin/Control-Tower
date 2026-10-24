import fs from 'node:fs'
import { defineConfigWithTheme, type DefaultTheme, type HeadConfig } from 'vitepress'

// 🔴 寫頁面內容時不改本檔：nav、sidebar、元件、設定值有需要時以 yolo 提問請塔台裁示。

export interface CtRelease {
  ctVersion: string
  guideVersion: string
  releasedAt: string
  zip: string | null
  guideZip: string | null
  changelogEntries: number
}

export interface ThemeConfig extends DefaultTheme.Config {
  /** scripts/sync-ct-release.mjs 產生的版本資料 */
  ctRelease: CtRelease
  /** BAT 站網址（結尾有 /）；Portal → BAT 的連結一律用它組，內文不手寫網址 */
  batSiteUrl: string
  /** 推廣影片第二季簡報的 GitHub Release 下載網址（結尾有 /）；/podcast 的下載連結一律用它組，內文不手寫網址 */
  podcastReleaseUrl: string
  /** CT、CT Guide、BMad Guide 發行 zip 的 GitHub Releases 網址（結尾有 /）；CtDownload 的下載連結一律用它組，內文不手寫網址 */
  releasesUrl: string
  /** Artifact 預覽建置：沒有 client JS，元件只剩 SSR 的樣子 */
  artifact: boolean
}

// ---------- 設定值 ----------

// BAT 站網址常數：只能寫在 .vitepress/ 的設定裡，由 site/ 外的允許清單豁免去識別掃描
const DEFAULT_BAT_SITE_URL = 'https://gowerlin.github.io/better-agent-terminal/'
// 推廣影片第二季簡報 PDF 的 Release 附件網址：同上，只能寫在設定裡，允許清單只放行到 podcast-s2/ 這一層
const PODCAST_RELEASE_URL = 'https://github.com/gowerlin/Control-Tower/releases/download/podcast-s2/'
// 發行 zip 的 Releases 網址：同上，只能寫在設定裡；tag 規則 ct-v<CT 版號>、bmad-guide-v<bmad-guide 版號>，由 CtDownload 組
const CT_RELEASES_URL = 'https://github.com/gowerlin/Control-Tower/releases/'
// Artifact 預覽用的哨兵 base：build 完由 scripts/build-artifact.mjs 改寫成相對路徑
const ARTIFACT_BASE = '/__ct__/'

const TARGET = process.env.PORTAL_TARGET === 'artifact' ? 'artifact' : 'web'
const IS_ARTIFACT = TARGET === 'artifact'
const BASE = IS_ARTIFACT ? ARTIFACT_BASE : withSlashes(process.env.PORTAL_BASE || '/')
const SITE_URL = IS_ARTIFACT ? '' : withTrailingSlash(process.env.PORTAL_SITE_URL || '')
const BAT_SITE_URL = withTrailingSlash(process.env.BAT_SITE_URL || DEFAULT_BAT_SITE_URL)
// 元件展示頁（_showcase/）只在 PORTAL_SHOWCASE=1 時建置，供 B0 驗收元件；不屬於 36 頁
const SHOWCASE = process.env.PORTAL_SHOWCASE === '1'

const SITE_TITLE = 'BMad Control Tower'
const SITE_DESCRIPTION =
  '一個塔台，指揮整隊 Agent；每個決定都留在檔案裡。BMad Control Tower 是檔案驅動的工單編排 skill 組，在 Claude Code 或 Codex 上運作。'

// 404 頁的說明：VitePress 內建的是英文 Not Found
const NOT_FOUND_DESCRIPTION = '找不到這個頁面，網址可能已經移除或改名。請回 Control Tower Portal 首頁，或從上方選單找你要的內容。'

function withSlashes(value: string): string {
  let v = value.trim()
  if (!v.startsWith('/')) v = '/' + v
  if (!v.endsWith('/')) v += '/'
  return v
}

function withTrailingSlash(value: string): string {
  const v = value.trim()
  if (!v) return ''
  return v.endsWith('/') ? v : v + '/'
}

function readCtRelease(): CtRelease {
  const file = new URL('./ct-release.json', import.meta.url)
  if (!fs.existsSync(file)) {
    throw new Error('[config] 找不到 .vitepress/ct-release.json；先執行 node scripts/sync-ct-release.mjs <版號>')
  }
  return JSON.parse(fs.readFileSync(file, 'utf8')) as CtRelease
}

// cleanUrls：why.md → why、guide/index.md → guide/、index.md → 首頁
function pageUrl(relativePath: string): string {
  return SITE_URL + relativePath.replace(/(^|\/)index\.md$/, '$1').replace(/\.md$/, '')
}

if (!IS_ARTIFACT && !SITE_URL) {
  console.warn('\n[config] WARNING: 沒有設定 PORTAL_SITE_URL；不輸出 sitemap、og:url 與 og:image 的絕對網址\n')
}

// ---------- nav 與 sidebar（不含 /contribute：回報與協助測試頁尚未提供） ----------

const nav: DefaultTheme.NavItem[] = [
  {
    text: '開始',
    items: [
      { text: '為什麼需要 CT', link: '/why' },
      { text: '一張工單的一生', link: '/lifecycle' }
    ]
  },
  { text: '安裝', link: '/install' },
  { text: '功能', link: '/features' },
  { text: 'Guide Skill', link: '/guide/', activeMatch: '^/guide/' },
  {
    text: '進階',
    activeMatch: '^/deep/',
    items: [
      { text: '設計理念總覽', link: '/deep/#principles' },
      { text: '功能深入總覽', link: '/deep/#features' }
    ]
  },
  {
    text: '版本',
    activeMatch: '^/versions/',
    items: [
      { text: '版本總覽', link: '/versions/' },
      { text: '相容版本', link: '/versions/compatibility' },
      { text: '更版紀錄', link: '/versions/releases' },
      { text: '演進史', link: '/versions/evolution' }
    ]
  },
  {
    text: '案例與課程',
    items: [
      { text: '實戰案例', link: '/cases' },
      { text: '課程', link: '/course' },
      { text: '推廣影片（S2）', link: '/podcast' }
    ]
  },
  {
    text: '參考',
    items: [
      { text: '指令參考大全', link: '/reference/commands' },
      { text: '常見問題', link: '/faq' },
      { text: 'BAT 站', link: BAT_SITE_URL, target: '_blank', rel: 'noreferrer' }
    ]
  }
]

const sidebar: DefaultTheme.SidebarItem[] = [
  {
    text: '開始使用',
    items: [
      { text: '為什麼需要 CT', link: '/why' },
      { text: '安裝', link: '/install' },
      { text: '一張工單的一生', link: '/lifecycle' },
      { text: '功能總覽', link: '/features' }
    ]
  },
  {
    text: 'Guide Skill',
    items: [
      { text: '專區首頁', link: '/guide/' },
      { text: 'CT Guide', link: '/guide/ct-guide' },
      { text: 'CT Guide 學習路線', link: '/guide/learning-path' },
      { text: 'BMad Guide', link: '/guide/bmad-guide' }
    ]
  },
  {
    text: '進階：設計理念',
    items: [
      { text: '總覽', link: '/deep/#principles' },
      { text: '認知作業系統', link: '/deep/principles/cognitive-os' },
      { text: '檔案即真相來源', link: '/deep/principles/files-as-truth' },
      { text: '塔台不讀程式碼', link: '/deep/principles/tower-and-workers' },
      { text: '三層資料與記憶', link: '/deep/principles/data-layers' },
      { text: '可逆與不可逆的界線', link: '/deep/principles/boundaries' },
      { text: '治理：單一權威', link: '/deep/principles/governance' },
      { text: '會學習的系統', link: '/deep/principles/learning' }
    ]
  },
  {
    text: '進階：功能深入',
    items: [
      { text: '總覽', link: '/deep/#features' },
      { text: '工單系統', link: '/deep/features/work-orders' },
      { text: '派工：auto-session 與 BAT', link: '/deep/features/dispatch' },
      { text: 'yolo 與斷點 A–E', link: '/deep/features/yolo' },
      { text: 'Worker 向塔台提問', link: '/deep/features/worker-questions' },
      { text: 'worktree 隔離與合併', link: '/deep/features/worktree-merge' },
      { text: '落點檢查', link: '/deep/features/landing-check' },
      { text: '中斷、Renew 與補救收尾', link: '/deep/features/recovery' },
      { text: 'BUG／PLAN／EXP 與研究型工單', link: '/deep/features/record-types' },
      { text: '自我學習、Playbook 與 Workflow', link: '/deep/features/learning-playbook-workflow' },
      { text: '跨塔台與跨專案協作', link: '/deep/features/multi-tower' },
      { text: '觀測與改進', link: '/deep/features/observability' }
    ]
  },
  {
    text: '版本與相容性',
    items: [
      { text: '版本總覽', link: '/versions/' },
      { text: '相容版本對照', link: '/versions/compatibility' },
      { text: '更版紀錄', link: '/versions/releases' },
      { text: '演進史', link: '/versions/evolution' }
    ]
  },
  {
    text: '案例與課程',
    items: [
      { text: '實戰案例', link: '/cases' },
      { text: '課程入口', link: '/course' },
      { text: '推廣影片（S2）', link: '/podcast' }
    ]
  },
  {
    text: '參考',
    items: [
      { text: '指令參考大全', link: '/reference/commands' },
      { text: '常見問題', link: '/faq' }
    ]
  }
]

// local search 的繁中翻譯（沿用 BAT 站）；Artifact 預覽沒有 client JS，不放搜尋
const search: DefaultTheme.Config['search'] = {
  provider: 'local',
  options: {
    translations: {
      button: {
        buttonText: '搜尋',
        buttonAriaLabel: '搜尋'
      },
      modal: {
        displayDetails: '顯示詳細清單',
        resetButtonTitle: '清除搜尋',
        backButtonTitle: '關閉搜尋',
        noResultsText: '找不到相關結果',
        footer: {
          selectText: '選擇',
          selectKeyAriaLabel: 'Enter',
          navigateText: '切換',
          navigateUpKeyAriaLabel: '向上',
          navigateDownKeyAriaLabel: '向下',
          closeText: '關閉',
          closeKeyAriaLabel: 'Esc'
        }
      }
    }
  }
}

export default () => {
  const ctRelease = readCtRelease()

  const head: HeadConfig[] = [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${BASE}favicon.svg` }],
    ['meta', { name: 'theme-color', content: '#10172e' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    [
      'link',
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Chiron+Hei+HK:wght@900&family=Martian+Mono:wght@300;400;500&family=Noto+Sans+TC:wght@400;500;700;900&display=swap'
      }
    ],
    // 分享卡片：每頁共用的部分；標題、說明、網址在 transformHead 依頁面帶入
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:site_name', content: SITE_TITLE }],
    ['meta', { property: 'og:locale', content: 'zh_TW' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }]
  ]
  if (SITE_URL) {
    head.push(
      ['meta', { property: 'og:image', content: `${SITE_URL}og-card.png` }],
      ['meta', { property: 'og:image:width', content: '1200' }],
      ['meta', { property: 'og:image:height', content: '630' }],
      ['meta', { property: 'og:image:alt', content: 'BMad Control Tower：一個塔台，指揮整隊 Agent' }],
      ['meta', { name: 'twitter:image', content: `${SITE_URL}og-card.png` }]
    )
  }

  return defineConfigWithTheme<ThemeConfig>({
    base: BASE,
    lang: 'zh-TW',
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    cleanUrls: !IS_ARTIFACT,
    // Artifact 預覽：VitePress 實驗性 MPA 模式，頁面之間是一般連結、預設零 JS
    mpa: IS_ARTIFACT,

    srcExclude: [
      'PORTAL-PLAN.md',
      'README.md',
      'design/**',
      'scripts/**',
      'data/**',
      'dist-artifact/**',
      ...(SHOWCASE ? [] : ['_showcase/**'])
    ],

    ...(SITE_URL ? { sitemap: { hostname: SITE_URL } } : {}),

    head,

    // 每頁的分享標題／說明取自頁面 frontmatter（沒寫就用站名與站點說明）
    transformHead({ pageData, title, description }) {
      const pageDescription = pageData.isNotFound ? NOT_FOUND_DESCRIPTION : description
      const tags: HeadConfig[] = [
        ['meta', { property: 'og:title', content: title }],
        ['meta', { property: 'og:description', content: pageDescription }],
        ['meta', { name: 'twitter:title', content: title }],
        ['meta', { name: 'twitter:description', content: pageDescription }]
      ]
      if (pageData.isNotFound) {
        // head 裡有 meta description 時，VitePress 不再輸出內建的那一個
        tags.push(['meta', { name: 'description', content: NOT_FOUND_DESCRIPTION }])
      } else if (SITE_URL) {
        tags.push(['meta', { property: 'og:url', content: pageUrl(pageData.relativePath) }])
      }
      return tags
    },

    themeConfig: {
      ctRelease,
      batSiteUrl: BAT_SITE_URL,
      podcastReleaseUrl: PODCAST_RELEASE_URL,
      releasesUrl: CT_RELEASES_URL,
      artifact: IS_ARTIFACT,

      // logo.svg 的線條是 currentColor；放進 <img> 時跟不到頁面文字色，所以深色模式另給固定淺色線條的版本
      logo: { light: '/logo.svg', dark: '/logo-dark.svg', alt: '' },
      siteTitle: 'Control Tower',

      nav,
      sidebar,

      // 頁尾只在沒有側欄的頁面（首頁）顯示，這是 VitePress 預設主題的行為
      footer: {
        message: `內容基準：BMad Control Tower v${ctRelease.ctVersion}`,
        copyright: `執行環境請看 <a href="${BAT_SITE_URL}" target="_blank" rel="noreferrer">Better Agent Terminal 站</a>`
      },

      ...(IS_ARTIFACT ? {} : { search }),

      outline: {
        level: [2, 3],
        label: '本頁目錄'
      },
      docFooter: {
        prev: '上一頁',
        next: '下一頁'
      },
      lastUpdated: {
        text: '最後更新'
      },
      notFound: {
        title: '找不到頁面',
        quote: '這個網址沒有對應的頁面，可能已經移除或改名。',
        linkLabel: '回首頁',
        linkText: '回首頁'
      },
      darkModeSwitchLabel: '外觀',
      lightModeSwitchTitle: '切換為淺色',
      darkModeSwitchTitle: '切換為深色',
      sidebarMenuLabel: '選單',
      returnToTopLabel: '回到頂端',
      langMenuLabel: '切換語言',
      skipToContentLabel: '跳至內容',
      externalLinkIcon: true
    }
  })
}
