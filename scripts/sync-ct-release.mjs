#!/usr/bin/env node
// CT 發版同步（CT 每次發版都要同步更新 Portal）。零依賴。
//
//   node scripts/sync-ct-release.mjs <版號>        # 例：node scripts/sync-ct-release.mjs 5.12.2
//
// 1. 版號一致性：參數 = CT control-tower/SKILL.md 的版號註解 = Guide SKILL.md 的版號註解，否則報錯停止
// 2. 更新 .vitepress/ct-release.json（CT 版號、Guide 版號、發布日、zip 名稱）
// 3. 從 CT CHANGELOG 重新產生 versions/releases.md：近 10 版全文，更早的連到演進史；只列正式版（預發行段落略過、頁首註明），
//    新主版號線的 CHANGELOG 缺分出後才發的舊線正式版時，從較舊的穩定版目錄補上（見 mergeOlderStable）；
//    先做內部 id 摘要化（通用規則，見 summarizeIds；刪 SHA 後清掉空括號；落點檢查名 C-0～C-4 保留），再套 data/release-rewrites.json 的逐筆改寫
// 4. 對產出的 releases.md 跑去識別掃描（詞表在 site/ 外，含「內部 id」選用類別）；命中就報錯停止，要人工改寫後再跑
//
// 私有詞表與允許清單的路徑由環境變數 PORTAL_DEID_TERMS／PORTAL_DEID_ALLOW 傳入；沒設定就在寫檔前報錯停止。
// 只寫 site/ 內的兩個檔案；不改 CT、Guide 目錄。

import { spawnSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { maskLandingCheckIds, unmaskLandingCheckIds } from './deid-scan.mjs'

const FULL_ENTRIES = 10
const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const REPO = path.resolve(SITE, '..', '..')
const RELEASE_JSON = path.join(SITE, '.vitepress', 'ct-release.json')
const RELEASES_MD = path.join(SITE, 'versions', 'releases.md')
// 去識別改寫表：[{ version, pattern（正則，不寫敏感原值）, replace, reason }]；每筆都必須命中，否則報錯（來源改了要回來更新）
// pattern 裡的 {id} 代表任一個內部 id（ID_SOURCE）、{ref} 代表任一個回函／契約條目（REF_SOURCE），改寫表本身就不必寫出原值
const REWRITES = path.join(SITE, 'data', 'release-rewrites.json')
// 預發行版的逐版說明所在的專章（從 versions/releases.md 連過去）
const PREVIEW_PAGE = '../preview/methodology-adapters'

// 內部 id：工單號、塔台決策號、BUG／PLAN 編號。CHANGELOG 給維護者看，公開站不需要這些出處
const ID_SOURCE = String.raw`\b(?:CT-T[0-9]{3}|T[0-9]{4}|D[0-9]{3}|BUG-[0-9]{3}|PLAN-[0-9]{3})\b`
const ID = new RegExp(ID_SOURCE)
// 回函與契約條目：BAT 驗收回函的 F-n／O-n、BAT 介面契約的 C-n（含 C-1–C-8 範圍），以「、／–」串接。
// 落點檢查名 C-0～C-4 同形，摘要化前先用 deid-scan.mjs 的 maskLandingCheckIds 遮掉，這裡的規則就碰不到
const REF_SOURCE = String.raw`\b[FOC]-[0-9]+\b`
const REF = new RegExp(REF_SOURCE)
const REF_LIST = String.raw`${REF_SOURCE}(?:[、／–]${REF_SOURCE})*`
const isInternal = s => ID.test(s) || REF.test(s)
// 7–40 碼 hex，至少一個數字、一個字母（避免誤中英文單字與純數字）
const SHA_SOURCE = String.raw`\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b`
// BAT repo 內部的文件路徑（可帶「…」節與 commit SHA），以「、」串接；前面要緊接「BAT 」或「BAT 權威：」
const BAT_PATH = String.raw`\x60(?:CLAUDE\.md|(?:docs|electron|src)/[^\x60\n]+)\x60(?:「[^」\n]*」節)?(?:\s*\x60[0-9a-f]{7,40}\x60)?`
const BAT_PATHS = new RegExp(String.raw`BAT( 權威：| )${BAT_PATH}(?:、\s*${BAT_PATH})*`, 'g')

function fail(message) {
  console.error(`[sync-ct-release] 錯誤：${message}`)
  process.exit(1)
}

const rel = p => path.relative(REPO, p).split(path.sep).join('/')

function readVersionComment(file, key) {
  if (!fs.existsSync(file)) fail(`找不到 ${rel(file)}`)
  const m = fs.readFileSync(file, 'utf8').match(new RegExp(`<!--\\s*${key}:\\s*([0-9]+\\.[0-9]+\\.[0-9]+)\\s*-->`))
  if (!m) fail(`${rel(file)} 沒有 <!-- ${key}: x.y.z --> 版號註解`)
  return m[1]
}

// 行內 code span 以外的 < 與 {{ 要跳脫：CHANGELOG 裡的 <name>、<版號> 之類會被當成 HTML／Vue 樣板
function escapeOutsideCode(line) {
  let out = ''
  let i = 0
  while (i < line.length) {
    if (line[i] === '`') {
      let n = 0
      while (line[i + n] === '`') n++
      const fence = '`'.repeat(n)
      const end = line.indexOf(fence, i + n)
      if (end !== -1) {
        out += line.slice(i, end + n)
        i = end + n
        continue
      }
      out += fence
      i += n
      continue
    }
    const ch = line[i]
    out += ch === '<' ? '&lt;' : ch
    i++
  }
  return out.replace(/\{\{/g, '&#123;&#123;').replace(/\}\}/g, '&#125;&#125;')
}

// 非 http(s) 的 Markdown 連結（指向 CT 版本目錄內的相對檔案）在站內會變成死連結，改成純文字
function unlinkRelative(line) {
  return line.replace(/\[([^\]]+)\]\((?!https?:)[^)]+\)/g, '$1')
}

// 只收正式版條目。預發行版（`## [6.0.0-rc.1]` 這類帶 - 的版號）的段落整段略過：預發行版不更新更版紀錄，
// 內容放在「實驗功能」專章；不略過的話，這些段落會被併進上一個正式版條目的內文
function parseChangelog(text) {
  const entries = []
  const skipped = []
  let current = null
  let inFence = false
  for (const raw of text.split(/\r?\n/)) {
    if (/^```/.test(raw)) inFence = !inFence
    const head = !inFence && raw.match(/^## \[([0-9]+\.[0-9]+\.[0-9]+)(-[0-9A-Za-z.]+)?\]\s*[—-]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})/)
    if (head) {
      if (head[2]) {
        skipped.push(`${head[1]}${head[2]}`)
        current = null
        continue
      }
      current = { version: head[1], date: head[3], lines: [] }
      entries.push(current)
      continue
    }
    if (current) current.lines.push(raw)
  }
  entries.skipped = skipped
  return entries
}

const semverCmp = (a, b) => {
  const pa = a.split('.').map(Number)
  const pb = b.split('.').map(Number)
  for (let i = 0; i < 3; i++) if (pa[i] !== pb[i]) return pa[i] - pb[i]
  return 0
}

// 新的主版號線（例 v6）從較舊的穩定版分出來時，它的 CHANGELOG 不含分出後才發的舊線正式版（例 5.12.7～5.15.0）。
// 從比本版舊的穩定版目錄（BMad-Control-Tower-v<x.y.z>，不含帶後綴的目錄）補上缺的條目；同一版號以較新目錄的內容為準
function mergeOlderStable(entries, version) {
  const base = path.join(REPO, 'BMad-Control-Tower')
  const dirs = fs
    .readdirSync(base, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name.match(/^BMad-Control-Tower-v([0-9]+\.[0-9]+\.[0-9]+)$/)?.[1])
    .filter(v => v && semverCmp(v, version) < 0)
    .sort((a, b) => semverCmp(b, a))
  const have = new Set(entries.map(e => e.version))
  const added = []
  for (const v of dirs) {
    const file = path.join(base, `BMad-Control-Tower-v${v}`, 'docs', 'CHANGELOG.md')
    if (!fs.existsSync(file)) continue
    for (const entry of parseChangelog(fs.readFileSync(file, 'utf8'))) {
      if (have.has(entry.version) || semverCmp(entry.version, version) >= 0) continue
      have.add(entry.version)
      added.push({ entry, from: v })
    }
  }
  const merged = [...entries, ...added.map(a => a.entry)].sort((a, b) => semverCmp(b.version, a.version))
  merged.skipped = entries.skipped
  return { merged, added }
}

function renderEntry(entry) {
  const anchor = `v${entry.version.replace(/\./g, '-')}`
  const body = []
  let inFence = false
  for (const raw of entry.lines) {
    if (/^```/.test(raw)) {
      inFence = !inFence
      body.push(raw)
      continue
    }
    body.push(inFence ? raw : escapeOutsideCode(unlinkRelative(raw)))
  }
  while (body.length && body[body.length - 1].trim() === '') body.pop()
  return [`## ${entry.version} <small>${entry.date}</small> {#${anchor}}`, '', ...body].join('\n')
}

// 行內 code span 換成佔位符（\u0000n\u0000），處理完再換回；括號比對時不會碰到 code span 裡的內容
function codeSpanGuard() {
  const spans = []
  const guard = s => s.replace(/(`+)[^`\n]*?\1/g, m => `\u0000${spans.push(m) - 1}\u0000`)
  const restore = s => s.replace(/\u0000(\d+)\u0000/g, (_, i) => spans[Number(i)])
  return { guard, restore }
}

// 整個括號刪掉後的接縫。lead 是括號前的空白，會和括號一起換掉：
// 括號前有空白時，後面是空白、標點或行尾就連空白一起刪（「foo (x) bar」→「foo bar」、「foo (x)。」→「foo。」），
// 後面緊接文字就留一個空格；行首的空白（縮排）原樣留下。
// 括號前沒有空白時，英數（或 code span）緊接中文補一個空格（「O-3（…）與」→「O-3 與」），其他情況直接刪
function removedNoteGap(lead, prev = '', next = '') {
  if (lead) {
    if (prev === '' || prev === '\n') return lead
    return /[A-Za-z0-9`\u0000一-鿿]/.test(next) ? ' ' : ''
  }
  return /[A-Za-z0-9`\u0000]/.test(prev) && /[一-鿿]/.test(next) ? ' ' : ''
}

// 括號註記：內容依「，；、／」與「 / 」切段，含內部 id 或回函／契約條目的段刪掉；全部刪光就連括號一起刪。
// 開頭是「條目：說明」的只拿掉「條目：」。行內 code span 先換成佔位符，切段時不會被拆開
function stripIdNotes(text, stats) {
  const { guard, restore } = codeSpanGuard()
  let out = guard(text)
  const note = (open, close) => new RegExp(`([ \\t]*)${open}([^${open}${close}]*)${close}`, 'g')
  for (const [open, close, re] of [['（', '）', note('（', '）')], ['(', ')', note('\\(', '\\)')]]) {
    let before
    do {
      before = out
      out = out.replace(re, (whole, lead, inner, offset, str) => {
        const plain = restore(inner)
        if (!isInternal(plain) || /https?:/.test(plain)) return whole
        const label = inner.match(new RegExp(`^${REF_LIST}：`))
        if (label) {
          stats.refs++
          inner = inner.slice(label[0].length)
        }
        const parts = inner.split(/(\s\/\s|[，；、／])/)
        const kept = []
        for (let i = 0; i < parts.length; i += 2) {
          const part = restore(parts[i])
          if (ID.test(part)) stats.notes++
          else if (REF.test(part)) stats.refs++
          else kept.push(kept.length ? parts[i - 1] : '', parts[i])
        }
        if (kept.length) return `${lead}${open}${kept.join('')}${close}`
        return removedNoteGap(lead, str[offset - 1], str[offset + whole.length])
      })
    } while (out !== before)
  }
  return restore(out)
}

// 刪 SHA 後只剩空白的括號（「pre.3（`f26b7641`）已有」→「pre.3 已有」）整個刪掉，空格規則同 stripIdNotes。
// 行內 code span 裡的 () 不動（`fn()`）
function stripEmptyNotes(text, stats) {
  const { guard, restore } = codeSpanGuard()
  const out = guard(text).replace(/([ \t]*)(?:（\s*）|\(\s*\))/g, (whole, lead, offset, str) => {
    stats.emptyNotes++
    return removedNoteGap(lead, str[offset - 1], str[offset + whole.length])
  })
  return restore(out)
}

// 內部 id 摘要化（通用規則）。只處理 fenced code block 以外的文字；回傳各類處數
function summarizeIds(entries) {
  const stats = { tails: 0, notes: 0, batPaths: 0, shas: 0, refs: 0, stages: 0, emptyNotes: 0 }
  for (const entry of entries) {
    const chunks = []
    let current = []
    for (const line of entry.lines) {
      if (/^```/.test(line)) {
        chunks.push({ code: false, lines: current }, { code: true, lines: [line] })
        current = []
      } else current.push(line)
    }
    chunks.push({ code: false, lines: current })
    let inFence = false
    entry.lines = chunks.flatMap(chunk => {
      if (chunk.code) {
        inFence = !inFence
        return chunk.lines
      }
      if (inFence) return chunk.lines
      // ⓪ 落點檢查語境的 C-0～C-4 不是契約條目：先遮掉，處理完再換回（判斷與 deid-scan.mjs 共用）
      let text = maskLandingCheckIds(chunk.lines.join('\n'))
      // ① 出處尾註「範圍 D###；T####。」
      text = text.replace(new RegExp(`[ \\t]*範圍 (?=[^。\\n]*${ID_SOURCE})[^。\\n]*。`, 'g'), () => {
        stats.tails++
        return ''
      })
      // ② BAT 內部文件路徑 → 「BAT 文件」（含跟在路徑後面的 SHA）
      text = text.replace(BAT_PATHS, (_, prefix) => {
        stats.batPaths++
        return prefix === ' 權威：' ? '權威見 BAT 文件' : 'BAT 文件'
      })
      // ③ 括號註記裡的內部 id 與回函／契約條目
      text = stripIdNotes(text, stats)
      // ③-2 夾在中文之間的回函／契約條目（「回函 F-2、O-3 與」「」C-1–C-8 為準」）；其他位置的交給改寫表的 {ref}
      text = text.replace(new RegExp(`(?<=[一-鿿」])[ \\t]*${REF_LIST}[ \\t]*(?=[一-鿿])`, 'g'), () => {
        stats.refs++
        return ''
      })
      // ③-3 內部階段名（「Workflow 智能 P3 精簡版」→「Workflow 精簡版」）
      text = text.replace(/ 智能 P[0-9]+(?= )/g, () => {
        stats.stages++
        return ''
      })
      // ④ 其餘的 commit SHA（code span 或裸字）
      text = text.replace(new RegExp(`[ \\t]?(\`${SHA_SOURCE}\`|${SHA_SOURCE})`, 'g'), () => {
        stats.shas++
        return ''
      })
      // ④-2 刪 SHA 後留下的空括號
      text = stripEmptyNotes(text, stats)
      return unmaskLandingCheckIds(text).split('\n')
    })
  }
  return stats
}

function applyRewrites(entries) {
  if (!fs.existsSync(REWRITES)) return 0
  const rules = JSON.parse(fs.readFileSync(REWRITES, 'utf8'))
  let total = 0
  for (const rule of rules) {
    const entry = entries.find(e => e.version === rule.version)
    if (!entry) continue // 已不在近 10 版內
    const re = new RegExp(rule.pattern.replaceAll('{id}', `(?:${ID_SOURCE})`).replaceAll('{ref}', `(?:${REF_SOURCE})`), 'g')
    let hit = 0
    entry.lines = entry.lines.map(line =>
      line.replace(re, () => {
        hit++
        return rule.replace
      })
    )
    if (!hit) fail(`release-rewrites.json：${rule.version} 的改寫沒有命中（${rule.reason}）；CHANGELOG 可能改過，請更新改寫表`)
    console.log(`[sync-ct-release] 改寫 ${rule.version}：${hit} 處（${rule.reason}）`)
    total += hit
  }
  return total
}

function main() {
  const version = process.argv[2]
  if (!version || !/^[0-9]+\.[0-9]+\.[0-9]+$/.test(version)) fail('用法：node scripts/sync-ct-release.mjs <版號，例如 5.12.2>')
  const terms = process.env.PORTAL_DEID_TERMS
  const allow = process.env.PORTAL_DEID_ALLOW
  if (!terms || !allow) fail('沒有設定 PORTAL_DEID_TERMS／PORTAL_DEID_ALLOW（私有詞表與允許清單的路徑）；產出的更版紀錄必須掃描，所以不寫檔')

  const ctDir = path.join(REPO, 'BMad-Control-Tower', `BMad-Control-Tower-v${version}`)
  const guideDir = path.join(REPO, 'Control-Tower-Guide-Skill', `control-tower-guide-v${version}`)
  if (!fs.existsSync(ctDir)) fail(`找不到 CT 版本目錄 ${rel(ctDir)}`)
  if (!fs.existsSync(guideDir)) fail(`找不到 Guide 版本目錄 ${rel(guideDir)}（Guide 要與 CT 同版號發行）`)

  const ctVersion = readVersionComment(path.join(ctDir, 'skills', 'control-tower', 'SKILL.md'), 'control-tower-version')
  const guideVersion = readVersionComment(path.join(guideDir, 'SKILL.md'), 'control-tower-guide-version')
  if (ctVersion !== version || guideVersion !== version) {
    fail(`版號不一致：參數 ${version}、CT SKILL.md ${ctVersion}、Guide SKILL.md ${guideVersion}（Guide 要與 CT 同版號）`)
  }

  const changelogPath = path.join(ctDir, 'docs', 'CHANGELOG.md')
  if (!fs.existsSync(changelogPath)) fail(`找不到 ${rel(changelogPath)}`)
  const own = parseChangelog(fs.readFileSync(changelogPath, 'utf8'))
  if (!own.length) fail('CHANGELOG 沒有 `## [x.y.z] — YYYY-MM-DD` 條目')
  if (own[0].version !== version) fail(`CHANGELOG 最新條目是 ${own[0].version}，不是 ${version}`)
  const { merged: entries, added } = mergeOlderStable(own, version)
  const skipped = own.skipped
  if (skipped.length) console.log(`[sync-ct-release] 略過預發行段落 ${skipped.length} 個（v${skipped.at(-1)} ～ v${skipped[0]}）`)
  if (added.length) {
    const from = [...new Set(added.map(a => a.from))].map(v => `v${v}`).join('、')
    console.log(`[sync-ct-release] 從較舊的穩定版目錄補上 ${added.length} 個正式版條目（v${added.at(-1).entry.version} ～ v${added[0].entry.version}，來源 ${from}）`)
  }

  const zipName = `BMad-Control-Tower-v${version}.zip`
  const guideZipName = `control-tower-guide-v${version}.zip`
  const release = {
    ctVersion,
    guideVersion,
    releasedAt: entries[0].date,
    zip: fs.existsSync(path.join(REPO, 'BMad-Control-Tower', zipName)) ? zipName : null,
    guideZip: fs.existsSync(path.join(REPO, 'Control-Tower-Guide-Skill', guideZipName)) ? guideZipName : null,
    changelogEntries: entries.length
  }
  if (!release.zip) console.warn(`[sync-ct-release] 警告：找不到 ${zipName}，ct-release.json 的 zip 記為 null`)

  const full = entries.slice(0, FULL_ENTRIES)
  const ids = summarizeIds(full)
  const rewritten = applyRewrites(full)
  const idTotal = ids.tails + ids.notes + ids.batPaths + ids.shas + ids.refs + ids.stages
  console.log(
    `[sync-ct-release] 內部 id 摘要化 ${idTotal} 處：出處尾註 ${ids.tails}、括號註記 ${ids.notes}、BAT 文件路徑 ${ids.batPaths}、commit SHA ${ids.shas}、` +
      `回函／契約條目 ${ids.refs}、內部階段名 ${ids.stages}；刪 SHA 後清掉空括號 ${ids.emptyNotes} 處；` +
      `改寫表 ${rewritten} 處`
  )
  const older = entries.slice(FULL_ENTRIES)
  const md = [
    '---',
    'title: 更版紀錄',
    `description: BMad Control Tower 近 ${full.length} 版的更版紀錄（最新 v${version}），更早的版本見演進史。`,
    '---',
    '',
    '<!-- 本頁由 scripts/sync-ct-release.mjs 從 CT CHANGELOG 產生，請勿手改；要改內容請改來源後重跑。 -->',
    '',
    '# 更版紀錄',
    '',
    `目前版本 **v${version}**（${release.releasedAt}）。這裡列出最近 ${full.length} 版的完整紀錄，最新的在最上面；` +
      `更早的 ${older.length} 版（v${older.at(-1)?.version ?? '—'} ～ v${older[0]?.version ?? '—'}）請看[演進史](./evolution)。`,
    '',
    ...(skipped.length
      ? [
          `本頁只列正式版。預發行版 v${skipped.at(-1)} ～ v${skipped[0]}（${skipped.length} 版）的改動已彙整在 v${version} 的段落，` +
            `逐版說明保留在「實驗功能」的[預發行專章](${PREVIEW_PAGE})作為歷史參考。`,
          ''
        ]
      : []),
    '::: tip 摘要不具權威',
    '本頁照錄 CT 的 CHANGELOG，只拿掉工單、決策、驗收回函等內部編號與出處註記。規則的權威定義在 CT 各 skill 與 references，兩者有出入時以 CT 本體為準。',
    ':::',
    '',
    '::: v-pre',
    '',
    full.map(renderEntry).join('\n\n'),
    '',
    ':::',
    '',
    '## 延伸閱讀 {#further-reading}',
    '',
    `- CT \`CHANGELOG.md\`（共 ${entries.length} 個版本；本頁列最近 ${full.length} 版）`,
    '- CT `version-governance.md` § 歷史版號表',
    `- [演進史](./evolution)：更早的 ${older.length} 版與八個世代`,
    '',
    'Portal 是摘要，不具權威；與 CT reference 有出入時，以 reference 為準。',
    ''
  ].join('\n')

  fs.mkdirSync(path.dirname(RELEASES_MD), { recursive: true })
  fs.writeFileSync(RELEASES_MD, md)
  fs.mkdirSync(path.dirname(RELEASE_JSON), { recursive: true })
  fs.writeFileSync(RELEASE_JSON, JSON.stringify(release, null, 2) + '\n')

  console.log(`[sync-ct-release] CT ${ctVersion} = Guide ${guideVersion}（${release.releasedAt}）`)
  console.log(`[sync-ct-release] ${rel(RELEASE_JSON)}`)
  console.log(`[sync-ct-release] ${rel(RELEASES_MD)}：全文 ${full.length} 版，連到演進史 ${older.length} 版（CHANGELOG 共 ${entries.length} 版）`)

  const scan = spawnSync(
    process.execPath,
    [path.join(SITE, 'scripts', 'deid-scan.mjs'), '--terms', path.resolve(terms), '--allow', path.resolve(allow), '--internal-ids', RELEASES_MD],
    { stdio: 'inherit' }
  )
  if (scan.status !== 0) fail('releases.md 去識別掃描有命中：請把命中的條目改寫或摘要化後再跑')
}

main()
