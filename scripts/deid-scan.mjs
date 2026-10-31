#!/usr/bin/env node
// 去識別掃描。零依賴。
//
//   node scripts/deid-scan.mjs [--terms <私有詞表>] [--allow <允許清單>] [--internal-ids] <路徑…>
//
// --internal-ids：選用類別「內部 id」。編號類（工單號、決策號、BUG／PLAN 編號、提問選項號、閘門題號、本地規則代號、
// 規劃文件的引用）對全站生效，
// 頁面上的範例編號只放行 EXAMPLE_IDS 列出的；其他類別只對更版紀錄（versions/releases.md 與建置出的 releases.html）生效：
// commit SHA、BAT 內部文件路徑、BAT 回函與介面契約條目（F-n、O-n、C-n）、內部階段名（「智能 P2」這類）。
// HTML 先去掉標籤再比對（資產檔名的雜湊不算）；建置產物裡 JS、JSON 與內嵌腳本的 Vite 產物雜湊也先遮掉（maskViteHashes）。
// 落點檢查名 C-0～C-4 在落點檢查語境裡不算條目（maskLandingCheckIds，sync-ct-release.mjs 共用）。
//
// 只輸出「檔案:行:類別」與各類計數，不輸出命中的原文（避免把敏感值印進日誌）。命中數 > 0 時 exit 1。
// 詞表與允許清單放在 site/ 外（不進公開 repo），以參數或環境變數 PORTAL_DEID_TERMS／PORTAL_DEID_ALLOW 傳入（參數優先）；
// 兩個都沒有就報錯結束（exit 2），不會略過掃描。檔案格式見各檔開頭的註解。
//
// 掃描範圍：EXTENSIONS 的副檔名（含字幕檔 .srt），以及沒有副檔名的檔案（含 .gitignore 這類點開頭的檔名）；
// 前 8 KB 有 NUL 位元組的檔案視為二進位，跳過。export-public-repo.mjs 用 isScannable 判斷哪些檔案要另外補掃

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const EXTENSIONS = new Set(['.md', '.vue', '.ts', '.mts', '.css', '.json', '.html', '.svg', '.js', '.mjs', '.toml', '.txt', '.srt', '.xml', '.yml', '.yaml'])
// 不掃的目錄：依賴與建置快取。.vitepress/dist 與 dist-artifact 要另外當路徑參數傳入才掃
const SKIP_DIRS = new Set(['node_modules', '.git', 'cache'])
const SKIP_UNLESS_ROOT = new Set(['dist', 'dist-artifact'])
// 不掃的檔案：鎖檔只有套件名稱與雜湊；規劃文件不公開，而且本身就列出這裡的正則
const SKIP_FILES = new Set(['package-lock.json', 'PORTAL-PLAN.md'])

// 類別依編號排列；1、2 另有私有詞表
const PATTERNS = [
  ['1-專案名', /\b20[0-9]{2}_[A-Za-z][A-Za-z0-9_-]+/g],
  ['3-個人路徑', /([A-Z]:[\\/]+|\/[a-z]\/)Users[\\/]/gi],
  ['3-磁碟路徑', /\b[A-Z]:[\\/]+[A-Za-z@]/g],
  ['3-專案目錄編碼', /[A-Za-z]--[A-Za-z0-9-]+--/g],
  ['3-Claude 專案目錄', /\.claude[\\/]projects[\\/]/g],
  ['4-內網位址', /\b(10|192\.168|172\.(1[6-9]|2[0-9]|3[01]))(\.[0-9]{1,3}){2}\b/g],
  ['5-權杖', /(ghp_|gho_|github_pat_|sk-ant-|glpat-|AKIA|xox[bp]-)[A-Za-z0-9_-]{8,}/g],
  ['6-UUID', /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi],
  ['6-32 碼 hex', /\b[0-9a-f]{32}\b/g],
  ['6-提問 id', /\bq-[0-9a-f]{8}-[0-9a-f]{16}\b/g],
  ['6-分頁短 id', /· [0-9a-f]{6,8}\b/g],
  ['7-私人規則名', /R-G0[0-9]{2}/g],
  ['8-Email', /[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[a-z]{2,})/g]
]
const EMAIL_ALLOWED = /(^|\.)example\.(com|org|net)$/

// 選用類別「內部 id」（--internal-ids）的編號類，對全站生效。
// 決策號另收兩碼（早期的決策號也出現在 CT reference 的章節名括號裡）；提問選項號是決策紀錄的「Q＋題號＋.＋選項字母」
const INTERNAL_NUMBER_PATTERNS = [
  ['內部 id-工單號', /\b(?:CT-T[0-9]{3}|T[0-9]{4})\b/g],
  ['內部 id-決策號', /\bD[0-9]{2,3}\b/g],
  ['內部 id-BUG／PLAN', /\b(?:BUG|PLAN)-[0-9]{3}\b/g],
  ['內部 id-提問選項', /\bQ[0-9]+\.[A-Z]\b/g],
  // 閘門題號「G＋閘門號＋空白＋Q＋題號」；CT 公開概念的閘門名（單獨的 G2）不算
  ['內部 id-閘門題號', /\bG[0-9] Q[0-9]+/g],
  // 本地規則代號「LR-＋三碼」
  ['內部 id-本地規則', /\bLR-[0-9]{3}\b/g],
  // 規劃文件的引用（章節號、文字敘述）。後面接 .md 的是排除清單裡的檔名（不建置、不掃、不匯出），功能性的，放行。
  // 正則寫成 [-] 才不會命中這一行自己
  ['內部 id-規劃文件', /PORTAL[-]PLAN(?!\.md)/g]
]

// 範例編號：頁面上示範格式或指令用的工單號，不指向本 repo 真的工單。只在更版紀錄以外放行（更版紀錄照錄 CHANGELOG，
// 出現的編號都是真的）。新增範例要先加在這裡並寫出處頁；不要用萬用規則放行
const EXAMPLE_IDS = new Map([
  ['T0001', '指令與格式範例：install、faq、reference/commands、guide/ct-guide、versions/evolution、deep/features/work-orders、multi-tower、recovery；課程示範專案的工單：course-dojo'],
  ['T0005', '*resume 範例：reference/commands、deep/features/recovery'],
  ['T0015', '工單檔名範例：deep/features/work-orders'],
  ['T0042', '派工與回報範例：index、faq、lifecycle、HeroTower.vue'],
  ['T0047', '跨專案撞號情境：deep/features/landing-check'],
  ['T0073', '引用欄位範例：deep/features/record-types'],
  ['T0113', '前綴格式範例（CP-T0113、cp-T0113）：deep/features/work-orders、yolo'],
  ['T0115', '單專案標準形式範例：deep/features/work-orders'],
  ['T0123', '*insights workflow 語法範例：reference/commands'],
  ['T0124', '*insights workflow 語法範例：reference/commands'],
  ['T0002', '課程示範專案的工單（CH3 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0003', '課程示範專案的工單（CH3 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0004', '課程示範專案的工單（CH4 道館，4-03 的前置工單；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0005', '課程示範專案的工單（CH4 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0006', '課程示範專案的工單（CH4 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0007', '課程示範專案的工單（CH4 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0008', '課程示範專案的工單（CH5 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0009', '課程示範專案的工單（CH5 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0010', '課程示範專案的工單（CH5 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T0011', '課程示範專案的工單（CH5 道館的合併工單；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['T9003', '課程示範專案的工單（CH4 道館的前置單；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['D001', '課程示範專案的決策（CH1 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['D002', '課程示範專案的決策（CH3 道館；公開程式碼 repo 的 _ct-workorders/）：course-dojo'],
  ['BUG-001', '引用欄位範例：deep/features/record-types']
])

// 其他類別只對更版紀錄生效；規則與 sync-ct-release.mjs 的摘要化一致
const INTERNAL_RELEASE_PATTERNS = [
  ['內部 id-commit SHA', /\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b/g],
  ['內部 id-BAT 文件路徑', /\b(?:docs\/agent-guide|electron)\/[\w./-]+/g],
  ['內部 id-回函／契約條目', /\b[FOC]-[0-9]+\b/g],
  ['內部 id-內部階段名', /智能 P[0-9]+/g]
]

// 落點檢查名：CT 的落點檢查（ct-exec/SKILL.md § Landing Zone Check）叫 C-0～C-4，和 BAT 介面契約條目 C-n 同形。
// 落點檢查語境裡的不算內部條目。sync-ct-release.mjs 摘要化前也用這裡的判斷，兩支腳本才不會一邊留一邊擋。
// 語境：同一句（以「。！？」、空行、下一個清單項目、標題或 HTML 區塊標籤為界，可跨行）有 LANDING_CHECK_CONTEXT 的字樣，而且
//   - 串在一起的條目（以「、／–～」相接）全都是 C-0～C-4（「C-1–C-8」「F-1、C-2」照舊算條目）；
//   - 前面同一段沒有緊接「契約」「回函」（「BAT 契約 C-1」照舊算條目）
export const LANDING_CHECK_CONTEXT = /落點|Landing Zone/i // 「落點」含「落點檢查」
const REF_CHAIN = /\b[FOC]-[0-9]+\b(?:[ \t]*[、／–～~][ \t]*[FOC]-[0-9]+\b)*/g
const SENTENCE_BOUNDARY = /[。！？\u2029]|\n[ \t]*\n|\n(?=[ \t]*(?:[-*+]|[0-9]+\.)[ \t]|[ \t]*#)/g
// 判定為落點檢查名的 C-n 換成「C」＋mask＋數字（長度不變，不再符合 [FOC]-n）；unmaskLandingCheckIds 換回
export const LANDING_CHECK_MASK = '\uE000'

function sentenceAround(text, start, end) {
  let from = 0
  let to = text.length
  for (const m of text.matchAll(SENTENCE_BOUNDARY)) {
    if (m.index + m[0].length <= start) from = m.index + m[0].length
    else if (m.index >= end) {
      to = m.index
      break
    }
  }
  return text.slice(from, to)
}

export function maskLandingCheckIds(text) {
  return text.replace(REF_CHAIN, (chain, offset) => {
    if (!chain.match(/[FOC]-[0-9]+/g).every(id => /^C-[0-4]$/.test(id))) return chain
    if (/(?:契約|回函)[^，；、。！？\n]{0,6}$/.test(text.slice(Math.max(0, offset - 12), offset))) return chain
    if (!LANDING_CHECK_CONTEXT.test(sentenceAround(text, offset, offset + chain.length))) return chain
    return chain.replace(/C-/g, `C${LANDING_CHECK_MASK}`)
  })
}

export const unmaskLandingCheckIds = text => text.replaceAll(`C${LANDING_CHECK_MASK}`, 'C-')

// HTML 去標籤：區塊標籤當句界（給 maskLandingCheckIds），其他標籤換成空白；不跨行，行號不變
const stripTags = text => text.replace(/<\/?(?:p|li|ul|ol|h[1-6]|div|blockquote|table|tr|td|th)\b[^>\n]*>/g, '\u2029').replace(/<[^>\n]*>/g, ' ')

// HTML 註解只拿掉 <!-- 與 -->、內文照樣比對（原始檔的註解會跟著匯出），要在 stripTags 之前做
const uncomment = text => text.replace(/<!--|-->/g, ' ')

// Vite 產物雜湊：建置產物的檔名「<名稱>.<8 碼雜湊>.js」（另有 .lean.js、.mjs、.css）被其他 JS 的 import 引用，
// 頁面雜湊表（HTML 內嵌的 __VP_HASH_MAP__ 與 hashmap.json）另外寫成「"<頁>.md":"<8 碼雜湊>"」（內嵌時引號帶反斜線）。
// 雜湊是 base64url 字元、隨內容變，可能剛好是「.」接「D＋兩、三位數字」再接「-」的形狀而命中決策號，每次發版都要人工判定。
// 比對內部 id 前把這兩種位置的雜湊段換成同長度的底線（行內位置不變）：只遮雜湊段，名稱與頁面內容裡的編號照舊比對，
// 決策號規則本身不放寬；只對建置產物（isBuildOutput）做，原始檔照舊
const VITE_HASHED_NAME = /(\.)[A-Za-z0-9_-]{8}(?=\.(?:lean\.)?(?:js|mjs|css)\b)/g
const VP_HASH_MAP_ENTRY = /(\.md\\?":\\?")[A-Za-z0-9_-]{8}(?=\\?")/g
const maskHash = (match, prefix) => prefix + '_'.repeat(match.length - prefix.length)
const maskViteHashes = text => text.replace(VITE_HASHED_NAME, maskHash).replace(VP_HASH_MAP_ENTRY, maskHash)

const isReleases = file =>/(^|\/)versions\/releases\.(md|html)$/.test(file.split(path.sep).join('/'))

function usage(message) {
  if (message) console.error(`deid-scan: ${message}`)
  console.error('用法：node scripts/deid-scan.mjs [--terms <私有詞表>] [--allow <允許清單>] [--internal-ids] <路徑…>')
  console.error('      沒給 --terms／--allow 時讀環境變數 PORTAL_DEID_TERMS／PORTAL_DEID_ALLOW')
  process.exit(2)
}

function parseArgs(argv) {
  const env = name => process.env[name] || null
  const out = { terms: env('PORTAL_DEID_TERMS'), allow: env('PORTAL_DEID_ALLOW'), internalIds: false, paths: [] }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--terms') out.terms = argv[++i]
    else if (a === '--allow') out.allow = argv[++i]
    else if (a === '--internal-ids') out.internalIds = true
    else if (a.startsWith('--')) usage(`不認得的參數 ${a}`)
    else out.paths.push(a)
  }
  if (!out.terms) usage('沒有私有詞表：請給 --terms 或設定 PORTAL_DEID_TERMS（不帶詞表不掃描）')
  if (!out.allow) usage('沒有允許清單：請給 --allow 或設定 PORTAL_DEID_ALLOW（不帶清單不掃描）')
  if (!out.paths.length) usage('至少給一個要掃的路徑')
  return out
}

function readList(file) {
  if (!fs.existsSync(file)) usage(`找不到 ${file}`)
  return fs
    .readFileSync(file, 'utf8')
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#'))
}

function loadTerms(file) {
  return readList(file).map(line => {
    const [first, second] = line.split('\t')
    const term = second === undefined ? first : second
    const category = second === undefined ? '1' : first.trim()
    const escaped = term.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    return { category: `${category}-私有詞表`, re: new RegExp(escaped, 'gi') }
  })
}

// 只看檔名：EXTENSIONS 的副檔名，或沒有副檔名（path.extname('.gitignore') 是 ''）。
// SKIP_FILES 是刻意不掃的檔案，不算「漏掃」，所以不在這裡排除（collect 另外排除），補掃端也不會撿回去
export function isScannable(file) {
  const ext = path.extname(file)
  return ext === '' || EXTENSIONS.has(ext)
}

function isBinary(file) {
  const fd = fs.openSync(file, 'r')
  try {
    const buf = Buffer.alloc(8192)
    return buf.subarray(0, fs.readSync(fd, buf, 0, buf.length, 0)).includes(0)
  } finally {
    fs.closeSync(fd)
  }
}

function collect(target, isRoot, out) {
  const stat = fs.statSync(target)
  if (stat.isFile()) {
    if (isScannable(target) && !SKIP_FILES.has(path.basename(target)) && !isBinary(target)) out.push(target)
    return
  }
  const name = path.basename(target)
  if (!isRoot && (SKIP_DIRS.has(name) || SKIP_UNLESS_ROOT.has(name))) return
  for (const entry of fs.readdirSync(target)) collect(path.join(target, entry), false, out)
}

// 建置產出（dist、dist-artifact）裡的網址常數是設定值組出來的連結，允許出現；
// 原始檔只允許寫在 .vitepress/ 的設定裡（內文不得手寫這些網址）
function isBuildOutput(file) {
  const p = file.split(path.sep).join('/')
  return /(^|\/)(\.vitepress\/dist|dist-artifact)\//.test(p)
}

function isConfig(file) {
  const p = file.split(path.sep).join('/')
  return /(^|\/)\.vitepress\/[^/]+\.(mts|ts|json)$/.test(p)
}

// 例外：站點根目錄的 README.md 是公開 repo 的首頁，要放 Portal 自己的公開網址；
// LICENSE 與 THIRD-PARTY-NOTICES.md 是公開 repo 的授權檔，著作權行要寫著作權人的帳號名（允許清單另列那一整行）。
// 「站點根目錄」= 旁邊有 .vitepress/config.mts 的目錄，所以 site/ 與匯出後公開 repo 根的這三個檔都成立；
// 子目錄的同名檔與其他 .md 照舊不放行
const SITE_ROOT_FILES = new Set(['README.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md'])

function isSiteRootFile(file) {
  return SITE_ROOT_FILES.has(path.basename(file)) && fs.existsSync(path.join(path.dirname(file), '.vitepress', 'config.mts'))
}

// 例外：CT 發行物（skills 原始檔、解開的 zip）有兩處要寫允許清單上的公開資訊：
// adapter 描述檔（references/adapters/ 下的 .yaml）的 guide.url 是方法論指南的公開 repo 網址；
// ct-adapter-* 目錄的 LICENSE 是外部 adapter 的授權檔，著作權行要寫著作權人的帳號名（同站點根的 LICENSE）。
// 只放行「允許清單網址寫在設定以外」這一類：同一行的私有詞表、路徑、信箱等類別照舊比對；
// adapters/ 子目錄的檔、其他 .yaml、其他目錄的 LICENSE 照舊不放行。路徑先轉絕對路徑，在這些目錄裡直接掃也成立
function isReleaseAllowedFile(file) {
  const abs = path.resolve(file)
  if (/(^|\/)references\/adapters\/[^/]+\.yaml$/.test(abs.split(path.sep).join('/'))) return true
  return path.basename(abs) === 'LICENSE' && path.basename(path.dirname(abs)).startsWith('ct-adapter-')
}

// 例外：plugin marketplace 的 repo 名稱。CT 從 v5.14.0 起在權威段寫 marketplace add 指令，指令一定要帶 repo 名稱，
// 所以 CT 發行物裡出現這個名稱不算「允許清單網址寫在設定以外」。範圍（isCtReleaseFile）：
//   - CT 與 Guide 的 skill 檔（原始檔、解開的 zip、plugin 目錄）：往上找最近一個有 SKILL.md 的目錄，它的 name 是 CT_SKILL_NAMES 之一；
//     遇到站點根目錄（有 .vitepress/config.mts）就停：Portal 頁面不靠這個例外，安裝頁的指令由設定常數組出
//   - CT 的 CHANGELOG：<版本目錄>/docs/CHANGELOG.md，而且同一個版本目錄有 skills/control-tower/SKILL.md
// 只放行允許清單上剛好等於這個名稱、或等於 https://github.com/<名稱> 的項目；含它的較長項目（例如 Releases 網址）照舊報。
// 同一行的私有詞表、路徑、信箱等類別照舊比對。名稱不寫在這裡（這支腳本也會被掃描），從 .vitepress/config.mts 的
// CT_MARKETPLACE_REPO 讀；讀不到就不放行
const CT_SKILL_NAMES = new Set(['control-tower', 'ct-done', 'ct-evolve', 'ct-exec', 'ct-fieldguide', 'ct-help', 'ct-insights', 'ct-status', 'control-tower-guide'])
const SITE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function marketplaceAllowEntries() {
  const config = path.join(SITE_DIR, '.vitepress', 'config.mts')
  const m = fs.existsSync(config) ? fs.readFileSync(config, 'utf8').match(/^const CT_MARKETPLACE_REPO = '([^'\r\n]+)'/m) : null
  return new Set(m ? [m[1], `https://github.com/${m[1]}`] : [])
}

// 目錄裡 SKILL.md 的 frontmatter name；沒有 SKILL.md 是 null，沒有 name 是空字串
const skillNames = new Map()
function skillName(dir) {
  if (!skillNames.has(dir)) {
    const file = path.join(dir, 'SKILL.md')
    let name = null
    if (fs.existsSync(file)) {
      const front = fs.readFileSync(file, 'utf8').match(/^---\r?\n([\s\S]*?)\r?\n---/)
      name = front?.[1].match(/^name:[ \t]*(\S+)/m)?.[1] ?? ''
    }
    skillNames.set(dir, name)
  }
  return skillNames.get(dir)
}

function isCtReleaseFile(file) {
  const abs = path.resolve(file)
  if (path.basename(abs) === 'CHANGELOG.md' && path.basename(path.dirname(abs)) === 'docs') {
    return skillName(path.join(path.dirname(path.dirname(abs)), 'skills', 'control-tower')) === 'control-tower'
  }
  for (let dir = path.dirname(abs); ; dir = path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, '.vitepress', 'config.mts'))) return false
    const name = skillName(dir)
    if (name !== null) return CT_SKILL_NAMES.has(name)
    if (path.dirname(dir) === dir) return false
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2))
  const terms = loadTerms(args.terms)
  // 長的項目先比對：較短的項目先從這一行拿掉的話，含它的較長項目就比對不到（marketplace repo 名稱的例外會漏報 Releases 網址）
  const allow = readList(args.allow).sort((a, b) => b.length - a.length)
  const marketplaceEntries = marketplaceAllowEntries()
  let marketplaceAllowed = 0
  const files = []
  for (const p of args.paths) {
    if (!fs.existsSync(p)) usage(`找不到 ${p}`)
    collect(p, true, files)
  }

  const counts = new Map()
  const hits = []
  const add = (file, line, category) => {
    hits.push(`${file.split(path.sep).join('/')}:${line}:${category}`)
    counts.set(category, (counts.get(category) || 0) + 1)
  }

  let releaseFiles = 0
  for (const file of files) {
    const releases = isReleases(file)
    if (args.internalIds && releases) releaseFiles++
    const internalPatterns = releases ? [...INTERNAL_NUMBER_PATTERNS, ...INTERNAL_RELEASE_PATTERNS] : INTERNAL_NUMBER_PATTERNS
    const content = fs.readFileSync(file, 'utf8')
    const lines = content.split(/\r?\n/)
    // 內部 id 類別比對的文字：HTML 先去標籤（資產檔名的雜湊不算，註解內文留著），建置產物再遮掉 Vite 產物雜湊，
    // 最後把落點檢查名遮掉（整份一起判斷，句子可跨行）
    let internalText = ''
    if (args.internalIds) {
      internalText = file.endsWith('.html') ? stripTags(uncomment(content)) : content
      if (isBuildOutput(file)) internalText = maskViteHashes(internalText)
    }
    const internalLines = args.internalIds ? maskLandingCheckIds(internalText).split(/\r?\n/) : []
    lines.forEach((raw, i) => {
      let line = raw
      for (const entry of allow) {
        if (!line.includes(entry)) continue
        if (!isBuildOutput(file) && !isConfig(file) && !isSiteRootFile(file) && !isReleaseAllowedFile(file)) {
          if (marketplaceEntries.has(entry) && isCtReleaseFile(file)) marketplaceAllowed++
          else add(file, i + 1, '允許清單網址寫在設定以外')
        }
        line = line.split(entry).join(' ')
      }
      for (const [category, re] of PATTERNS) {
        for (const m of line.matchAll(re)) {
          if (category === '8-Email' && EMAIL_ALLOWED.test(m[1])) continue
          add(file, i + 1, category)
        }
      }
      for (const { category, re } of terms) {
        for (const _ of line.matchAll(re)) add(file, i + 1, category)
      }
      if (args.internalIds) {
        for (const [category, re] of internalPatterns) {
          for (const m of internalLines[i].matchAll(re)) {
            if (!releases && EXAMPLE_IDS.has(m[0])) continue
            add(file, i + 1, category)
          }
        }
      }
    })
  }

  for (const h of hits) console.log(h)
  const internalNote = args.internalIds ? `（內部 id：編號類套用全部 ${files.length} 個檔案，其他類別套用 ${releaseFiles} 個更版紀錄檔）` : ''
  console.log(`deid-scan：掃描 ${files.length} 個檔案，命中 ${hits.length}${internalNote}`)
  for (const [category, n] of [...counts].sort()) console.log(`  ${category}: ${n}`)
  if (marketplaceAllowed) console.log(`  （CT 發行物裡的 marketplace repo 名稱放行 ${marketplaceAllowed} 處，不算命中）`)
  process.exit(hits.length ? 1 : 0)
}

// export-public-repo.mjs import isScannable 時不執行
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main()
