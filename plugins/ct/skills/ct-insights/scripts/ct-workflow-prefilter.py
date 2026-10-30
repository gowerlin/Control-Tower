#!/usr/bin/env python3
"""ct-workflow-prefilter.py — Workflow 適配度純腳本預篩（T0179；v5.11.0 起隨 ct-insights 發行，T0183）。

規則的權威是 ct-insights/references/analysis-rules.md § Workflow 適配度（S1–S6／X1–X5）；
腳本的角色（排除守門＋按需提示）見同節 § 預篩腳本。規則由 T0177 報告 § 3 定案，T0179 寫成腳本，
T0183 修 E4–E6。只用 Python 標準函式庫，不呼叫任何 LLM。

用法：
  python <ct-insights>/scripts/ct-workflow-prefilter.py [選項] <_ct-workorders 路徑> [<路徑> ...]

  --ids T####[,T####]  只列這些工單的守門結果與證據位置（可重複；X5 仍以整個目錄判定系列）
  --label NAME       專案名稱（可重複，依序對應路徑；預設取路徑上一層目錄名）
  --jsonl PATH       逐張判定輸出成 JSON Lines（不給就不輸出）
  --top N            每個專案列出前 N 名候選（預設 10）
  --calibrate JSONL  對 BAT 試點逐張判定 jsonl 做校準（評估 jsonl 列出的同一批檔案；開發用）

所有輸入只讀，只有 --jsonl 會寫到指定路徑。摘要以 Markdown 印到 stdout。
"""
import argparse
import collections
import datetime
import json
import os
import re
import sys

# ---------------------------------------------------------------- 工單判定

WO_NAME = re.compile(r'^(?:CP-|CT-)?T\d{3,4}[a-z]?(?:\.\d+)?(?:-.*)?\.md$')
WO_ID = re.compile(r'^((?:CP-|CT-)?T\d{3,4}[a-z]?(?:\.\d+)?)')
SKIP_DIRS = {'reports', '_templates', '_staging', 'examples', '_playbooks'}
WO_KINDS = {'workorder', 'implementation'}
MARKERS = re.compile(r'^#{1,3}\s*.*(?:回報區|工單回報)|工單編號|^## 任務指令|^# 工單', re.M)


def is_workorder(rel, fm, text):
    """回傳 (是否工單, 理由)。判定方式寫進報告 § 1。"""
    parts = rel.split('/')
    if any(p in SKIP_DIRS for p in parts[:-1]):
        return False, 'dir:' + next(p for p in parts[:-1] if p in SKIP_DIRS)
    kind = fm.get('schema_kind')
    if kind:
        return (kind in WO_KINDS), 'schema_kind:' + kind
    fid = fm.get('id', '')
    if isinstance(fid, str) and WO_ID.match(fid):
        return True, 'fm-id'
    if MARKERS.search(text):
        return True, 'marker'
    return False, 'no-marker'


# ---------------------------------------------------------------- 解析

def parse_frontmatter(text):
    if not text.startswith('---'):
        return {}, 0
    lines = text.split('\n')
    fm, key = {}, None
    for i in range(1, len(lines)):
        ln = lines[i].rstrip('\r')
        if ln.strip() == '---':
            return fm, i + 1
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', ln)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('[') and val.endswith(']'):
                fm[key] = [v.strip().strip('"\'') for v in val[1:-1].split(',') if v.strip()]
            elif val == '':
                fm[key] = []
            else:
                fm[key] = val.strip('"\'')
            continue
        m = re.match(r'^\s+-\s+(.*)$', ln)
        if m and key and isinstance(fm.get(key), list):
            fm[key].append(m.group(1).strip().strip('"\''))
    return {}, 0


def strip_fences(lines):
    """fenced code block 內的行換成空字串，保留行號。"""
    out, inside = [], False
    for ln in lines:
        if re.match(r'^\s*(```|~~~)', ln):
            inside = not inside
            out.append('')
            continue
        out.append('' if inside else ln)
    return out


HEADING = re.compile(r'^(#{1,6})\s+(.*)$')
REPORT_H2 = re.compile(r'^##\s+(?![^\n]*(?:要求|格式|規則|模板|範本))[^\n]*(?:回報|報告區|執行報告|工作報告|Report\b|Closeout)', re.I)
TOWER_H2 = re.compile(r'^##\s+.*塔台')


def split_areas(lines, body_start):
    """回傳 (指令區行號範圍, 回報區行號範圍, 塔台段行號清單)。行號 0 起算。"""
    rep = None
    for i in range(body_start, len(lines)):
        if REPORT_H2.match(lines[i]):
            rep = i
            break
    instr = range(body_start, rep if rep is not None else len(lines))
    report = range(rep, len(lines)) if rep is not None else range(0)
    tower, cur = [], False
    for i in range(body_start, len(lines)):
        m = HEADING.match(lines[i])
        if m and len(m.group(1)) <= 2:
            cur = bool(TOWER_H2.match(lines[i]))
        if cur:
            tower.append(i)
    return instr, report, tower


def section(lines, start):
    """從標題行 start 起到下一個同級或更高級標題前的行號。"""
    m = HEADING.match(lines[start])
    lvl = len(m.group(1)) if m else 7
    end = len(lines)
    for j in range(start + 1, len(lines)):
        h = HEADING.match(lines[j])
        if h and len(h.group(1)) <= lvl:
            end = j
            break
        if not m and re.match(r'^\*\*[^*]+\*\*\s*$', lines[j]):
            end = j
            break
    return range(start + 1, end)


def parse_ts(s):
    if not s or not isinstance(s, str):
        return None
    s = s.strip().strip('"\'').replace(' ', 'T', 1)
    s = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', s)
    try:
        return datetime.datetime.fromisoformat(s)
    except ValueError:
        return None


def snip(s, n=48):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:n] + '…'


# ---------------------------------------------------------------- 規則

# S1 的「逐項」語氣（只在指令區找）
S1_CUE = re.compile(
    r'對每(?:個|一|份|張|項|支|條|筆|檔)|逐(?:一|個|項|張|份|檔|條|筆|頁)|每(?:個|一個|份|項|支|條|張|筆)[^，。\n]{0,12}(?:都|各|分別|做|跑|讀|檢查|核對|比對|判定)'
    r'|分別(?:對|讀|檢查|核對|比對|跑|驗證)|各(?:自)?(?:對|讀|跑|檢查|核對|比對)一次'
    r'|\bfor each\b|\beach of the\b|\bper (?:file|module|item|ticket|commit)\b', re.I)
LIST_ITEM = re.compile(r'^(\s*)(?:[-*+]|\d+[.)、])\s+(.*)$')
TABLE_ROW = re.compile(r'^\s*\|(.+)\|\s*$')
TABLE_SEP = re.compile(r'^\s*\|?\s*:?-{2,}')
CONCRETE = re.compile(r'`[^`]+`|[\w.-]+/[\w./-]+|\.\w{1,5}\b|(?:CP-|CT-)?T\d{3,4}|BUG-\d+|PLAN-\d+|[A-Z][A-Za-z0-9]{2,}')
RUNTIME_SRC = re.compile(r'(?:掃描|盤點|搜尋|grep|找到|命中|輸出|列出|執行)[^，。\n]{0,6}(?:的|後|結果|中)')
TREAT = re.compile(r'^\s*(?:\*\*)?(?:記錄|紀錄|檢查|確認|列出|說明|判定|評估|標註|標記|比對|核對|讀|跑|執行|產出|寫|填|分類|給出|附|回報|record|check|verify|list)')
COUNT_N = re.compile(r'(\d{1,4}|[三四五六七八九十]{1,3})\s*(?:個|份|張|項|支|條|筆|組|檔|款|頁)')
ZH_NUM = {'三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


def count_n(s):
    best = 0
    for m in COUNT_N.finditer(s):
        g = m.group(1)
        if g.isdigit():
            v = int(g)
        elif len(g) == 1:
            v = ZH_NUM[g]
        elif g[0] == '十':
            v = 10 + ZH_NUM.get(g[1], 0)
        else:
            v = ZH_NUM.get(g[0], 0) * 10 + (ZH_NUM.get(g[2], 0) if len(g) > 2 else 0)
        best = max(best, v)
    return best
SERIAL = re.compile(r'基於\s*Step|依\s*Step\s*\d|根據\s*Step|上一步|前一步(?:的)?結(?:論|果)|同一個\s*runtime|describe\.serial|依序|串行|循序|序列|sequential')


def body_start_of(rng):
    return rng.start if len(rng) else 0


def detect_s1(lines, instr, affects, title=''):
    """S1 嚴格。E6（T0183）：frontmatter／H1 的 title 也當一個 cue 來源（i = -1）；
    標題沒有清單可數，只取 cue 子句寫的數量，執行前可列與否照「cue 行只寫數量」的規則判。"""
    best = None
    for i in [-1] + list(instr):
        ln = title if i < 0 else lines[i]
        cm = S1_CUE.search(ln) if ln else None
        if not cm:
            continue
        n_inline = 0
        tail = ln[cm.end():]
        parts = [p for p in re.split(r'[、/，,；;]|\s和\s', tail) if p.strip()]
        if len(parts) >= 3:
            n_inline = len(parts)
        # 緊接的清單或表格（cue 錨定才算；不在 cue 後的表格不計，避免表格列數灌水）。
        # cue 本身是清單項時只算它的子項，兄弟項是後續步驟不是子項目。
        # cue 指名「某清單」時，改數那個標題或粗體標籤下的清單。
        own = LIST_ITEM.match(ln)
        min_ind = len(own.group(1)) + 1 if own else 0
        start = i + 1 if i >= 0 else len(lines)  # 標題 cue 不數清單
        named = re.search(r'「([^」]{2,20})」', ln) if i >= 0 else None
        if named:
            for k in instr:
                if k != i and (HEADING.match(lines[k]) and named.group(1) in lines[k]
                               or '**%s**' % named.group(1) in lines[k]):
                    lk = LIST_ITEM.match(lines[k])
                    start, min_ind = k + 1, (len(lk.group(1)) + 1 if lk else 0)
                    break
        n_list, items, indent, j, seen, t_rows = 0, [], None, start, 0, 0
        while j < min(len(lines), start + 40) and j in instr:
            t = lines[j]
            if HEADING.match(t):
                break
            if not t.strip():
                if n_list:
                    seen += 1
                    if seen > 1:
                        break
                j += 1
                continue
            lm = LIST_ITEM.match(t)
            tm = TABLE_ROW.match(t)
            if lm:
                ind = len(lm.group(1))
                if ind < min_ind:
                    break
                if indent is None:
                    indent = ind
                if ind == indent:
                    n_list += 1
                    items.append(lm.group(2))
                elif ind < indent:
                    break
            elif tm:
                if not TABLE_SEP.match(t):
                    indent = -1 if indent is None else indent
                    n_list += 1
                    t_rows += 1
                    items.append(tm.group(1))
            elif n_list == 0 and j > start + 1:
                break
            elif n_list and not t.startswith(' '):
                break
            j += 1
        if t_rows:
            n_list -= 1  # 表頭列
            items = items[1:]
        # 「對每個 X：」後面接的若是處理步驟或欄位，清單是做法不是項目；N 改取同段的「N 個」
        treat = items and sum(1 for s in items if TREAT.match(s)) >= max(2, len(items) // 2)
        if treat:
            n_list = count_n(' '.join(lines[max(body_start_of(instr), i - 2):i + 1]))
            items = []
        # cue 行自己寫了數量（「逐項修正四份指南」「114 個 commit」），項目清單在別處
        cs = max(ln.rfind(c, 0, cm.start()) for c in '，。；;：:')
        ce = min([x for x in (ln.find(c, cm.end()) for c in '，。；;') if x >= 0] or [len(ln)])
        n_said = count_n(ln[cs + 1:ce])  # 只看 cue 所在的子句
        n = max(n_inline, n_list, n_said)
        if n < 3:
            continue
        sample = items if n_list >= n_inline else parts
        concrete = sum(1 for s in sample if CONCRETE.search(s))
        if RUNTIME_SRC.search(ln[:cm.start() + 12]):
            args = 'runtime'
        elif n_said == n and n > max(n_inline, n_list):
            # 只有數量：cue 行指向具體來源（檔名、工單、git log）才算執行前可列
            args = 'pre' if CONCRETE.search(ln) or re.search(r'git log|commit', ln) else '?'
        elif treat:
            args = '?'  # 項目沒有列在指令裡（可能要執行中才知道），交人工
        else:
            args = 'pre' if concrete >= max(2, len(sample) // 2) else '?'
        real_aff = [a for a in affects if not re.search(r'[*?\[]', a) and not a.startswith('_ct-workorders/')]
        same_file = 1 <= len(real_aff) <= 2 and n > len(real_aff)
        serial = bool(SERIAL.search(ln))  # cue 同一行就寫了「依序／序列」：S6 反訊號
        strength = 'strict' if args == 'pre' and not same_file and not serial else 'weak'
        cand = dict(hit=True, strength=strength, n=n, args=args, same_file=same_file, serial=serial,
                    line=i + 1, evidence=snip(ln), src='title' if i < 0 else 'instr')
        rank = (strength == 'strict', n)
        if best is None or rank > best[0]:
            best = (rank, cand)
    return best[1] if best else dict(hit=False)


# ③ 互動紀錄的 Q/A 條目：`[HH:MM] Q…→ A…`（清單符號、時間戳可有可無），或表格 `| Q1 |`／`| HH:MM | 問 | 答 |`
QA_Q = re.compile(r'^\s*(?:[-*]\s*)?(?:`?\[\d{1,2}:\d{2}\]`?\s*)?(?:\*\*)?Q-?\d*\s*(?:\*\*)?\s*[:：(（]')
QA_A = re.compile(r'→\s*(?:\*\*)?A|\bA\s*[:：]')
QA_TABLE = re.compile(r'^\s*\|\s*(?:(?:\*\*)?Q-?\d+(?:\*\*)?|\d{1,2}:\d{2})\s*\|\s*[^|\s-][^|]*\|\s*[^|\s-]')


INTERVENTION_DR = re.compile(r'^\s*-\s*\*\*intervention_type\*\*\s*[:：]\s*`?decision-requiring\b')
FM_INTERVENTION_DR = re.compile(r'^\s*intervention_type:\s*["\']?decision-requiring\b')  # 頂層或 interaction: 底下
DP_LOG = re.compile(r'^(?:#{2,5}\s*.*|\*\*[^*\n]*)DP\s*裁定紀錄')
EMPTY_ENTRY = re.compile(r'^\s*(?:[-*]\s*)?[（(]?(?:無|none|n/?a|—|-)[)）]?\s*$', re.I)


def has_entries(lines, rng):
    """段落內有表格資料列（不含表頭與分隔列）或清單項，而且不是「無」。"""
    rows = 0
    for j in rng:
        t = lines[j]
        if TABLE_ROW.match(t):
            if not TABLE_SEP.match(t):
                rows += 1
        elif LIST_ITEM.match(t) and not EMPTY_ENTRY.match(t):
            return True
    return rows >= 2  # 第 1 列是表頭


def detect_x2(lines, body_start):
    """X2 來源（T0177 § 3.3）。③ 的格式比 T0177 定案多收兩種（無清單符號、時間戳表格），差異見 T0179 報告。
    E5（T0183）加兩個來源：④ `intervention_type: decision-requiring`（frontmatter 頂層或 `interaction:` 底下，
    或內文元資料的鏡像行）；⑤「DP 裁定紀錄」段落有內容。"""
    src, first = [], None
    if any(FM_INTERVENTION_DR.match(ln) for ln in lines[:body_start]):
        src.append('④decision-requiring')
    for i in range(body_start, len(lines)):
        ln = lines[i]
        if INTERVENTION_DR.match(ln) and '④decision-requiring' not in src:
            src.append('④decision-requiring')
            first = first if first is not None else i
        if DP_LOG.match(ln) and '⑤DP 裁定紀錄' not in src and has_entries(lines, section(lines, i)):
            src.append('⑤DP 裁定紀錄')
            first = first if first is not None else i
        if re.match(r'^#{2,4}\s*待塔台決策', ln):
            if any(re.match(r'^####\s*Q-\d+', lines[j]) for j in section(lines, i)):
                src.append('①待塔台決策')
                first = first or i
        if re.match(r'^\s*-\s*\*\*塔台答覆 Q-\d+', ln):
            if '②塔台答覆' not in src:
                src.append('②塔台答覆')
            first = first or i
        if re.match(r'^#{2,5}\s*.*互動紀錄', ln) or re.match(r'^\*\*[^*\n]*互動紀錄[^*\n]*\*\*', ln):
            sec = list(section(lines, i))
            for k, j in enumerate(sec):
                t = lines[j]
                nxt = next((lines[x] for x in sec[k + 1:k + 3] if lines[x].strip()), '')
                if (QA_Q.match(t) and (QA_A.search(t) or re.match(r'^\s*(?:→|A\s*[:：])', nxt))) \
                        or QA_TABLE.match(t):
                    if '③互動紀錄' not in src:
                        src.append('③互動紀錄')
                    first = first or j
                    break
    return dict(hit=bool(src), sources=src, line=(first + 1) if first is not None else None,
                evidence=snip(lines[first]) if first is not None else
                ('frontmatter intervention_type: decision-requiring' if src else ''))


X2_WEAK = re.compile(r'交(?:由)?塔台(?:決定|裁定|決策)|待塔台(?:決定|裁定)|待決清單|需要決策的事項|遞交給塔台|請塔台(?:決定|裁定)')
X1_KW = re.compile(r'使用者目視|目視確認|實機(?:驗收|驗證|測試)?|安裝版|人工驗收|手動驗收|真機')
X1_DEFER = re.compile(r'延後|下游|後續工單|另開|留給使用者|不在本單|不在範圍|不啟動|禁止啟動|不做')
AC_HEAD = re.compile(r'驗收|Acceptance|\bAC\b|完成條件|完成標準|驗證|閘|Gate|DoD', re.I)
AC_LINE = re.compile(r'^\s*(?:[-*]\s*)?(?:\[[ x]\]\s*)?\**AC-?\d', re.I)
X4_ONE = re.compile(r'(?:一支|單一)(?:腳本|script)|一條指令|單一指令|single command', re.I)
# E4（T0183）：「逐一」接機械動作（複製、雜湊、計數），同一行的前後順序都算
_EACH = r'逐(?:一|個|檔|項|張|份|筆|支)'
_MECH = r'複製|拷貝|\bcopy\b|\bcp\b|雜湊|\bhash\b|SHA-?\d+|MD5|計數|\bcount\b|wc -l'
X4_MECH = re.compile(_EACH + r'[^。\n]{0,30}?(?:' + _MECH + r')|(?:' + _MECH + r')[^。\n]{0,20}?' + _EACH, re.I)
S3_KW = re.compile(r'推翻|改判|與[^，。\n]{0,20}不符|更正|勘誤|錯判|誤判|判錯|結論有誤')
S3_SELF = re.compile(r'推翻|改判')  # 本單回報區／塔台段；其他字樣只在塔台段與跨單引用時才算
S4_OPT = re.compile(r'(?:方案|Route|路線|選項|Option)\s*[（(]?([A-Da-d1-4])[)）]?')
S5_KW = re.compile(r'Context Window 風險[^\n]{0,6}高|context\s*不足|超過單一 sub-session|context <\s*\d+%', re.I)
# 指令區明說「照某張工單的模式做」：X5 的系列邊
_TID = r'(?:CP-|CT-)?T\d{3,4}(?:\.\d+)?'
TPL_REF = re.compile(
    r'(?:沿用|比照|仿照?|延續|鏡像|mirror)\s*' + _TID + r'(?:\s*[/、,]\s*' + _TID + r')*'
    r'|(?:與|同|對齊)\s*' + _TID + r'(?:\s*[/、,]\s*' + _TID + r')*[^，。\n]{0,8}?(?:模式|pattern|結構|格式|做法|同類|同型|對稱|先例)'
    r'|參考\s*' + _TID + r'[^，。\n]{0,10}?(?:格式|模式|結構|樣式|做法|處理)'
    r'|' + _TID + r'[^，。\n]{0,8}?(?:同類|同型|對稱|先例|既建立的 pattern|pattern)'
    r'|following\s+' + _TID + r'\s+pattern', re.I)
SUBAGENT = re.compile(r'子代理|子 ?agent|sub-?agents?|(?-i:\bExplore\b)|平行代理|並行代理|平行盤點|parallel agents?|Agent 工具', re.I)


def scan_lines(lines, rng, pat):
    for i in rng:
        m = pat.search(lines[i])
        if m:
            return i, m
    return None, None


def evaluate(path, rel, text):
    fm, body_start = parse_frontmatter(text)
    raw = text.split('\n')
    lines = strip_fences([ln.rstrip('\r') for ln in raw])
    instr, report, tower = split_areas(lines, body_start)
    fname = os.path.basename(rel)
    m = WO_ID.match(fname)
    wid = (fm.get('id') if isinstance(fm.get('id'), str) and WO_ID.match(fm.get('id', '')) else None) \
        or (m.group(1) if m else fname[:-3])
    title = fm.get('title') if isinstance(fm.get('title'), str) else ''
    if not title:
        for ln in lines[body_start:]:
            if ln.startswith('# '):
                title = ln[2:].strip()
                break
    affects = fm.get('affects_files') if isinstance(fm.get('affects_files'), list) else []
    deps = []
    for d in (fm.get('depends_on') if isinstance(fm.get('depends_on'), list) else [fm.get('depends_on', '')]):
        deps += re.findall(r'(?:CP-|CT-)?T\d{3,4}[a-z]?(?:\.\d+)?', str(d))
    rec = dict(id=wid, path=rel, title=title, status=fm.get('status', ''), type=fm.get('type', ''),
               bytes=len(text.encode('utf-8')), depends_on=deps, notes=[])
    tail = list(report) + [t for t in tower if t not in report]

    rec['S1'] = detect_s1(lines, instr, affects, title)
    i, _ = scan_lines(lines, instr, SERIAL)
    rec['S6'] = dict(verdict='需人工', serial_hint=(i + 1) if i is not None else None,
                     evidence=snip(lines[i]) if i is not None else '')
    # S3：renew、塔台段或回報區的推翻／改判字樣
    renew = int(fm.get('renew_count', '0')) if str(fm.get('renew_count', '0')).isdigit() else 0
    renew_h = next((k for k in range(body_start, len(lines)) if re.match(r'^##\s*塔台補充.*Renew', lines[k])), None)
    i, m = scan_lines(lines, tail, S3_SELF)
    if i is None:
        i, m = scan_lines(lines, tower, S3_KW)
    s3 = []
    if renew > 0:
        s3.append('renew_count=%d' % renew)
    if renew_h is not None:
        s3.append('Renew 段')
    if i is not None:
        s3.append('「%s」' % m.group(0))
    rec['S3'] = dict(hit=bool(s3), via=s3, line=(i + 1) if i is not None else ((renew_h + 1) if renew_h is not None else None),
                     evidence=snip(lines[i]) if i is not None else '')
    # 本單回報區指出「別張工單」錯了：記下來，之後算到被指的那張（S3 的「後續工單證明本單錯誤」）
    refutes = []
    for k in report:
        if S3_KW.search(lines[k]):
            for t in set(re.findall(r'(?:CP-|CT-)?T\d{3,4}(?:\.\d+)?', lines[k])):
                if t != wid:
                    refutes.append((t, k + 1, snip(lines[k], 40)))
    rec['_refutes'] = refutes
    opts = set()
    for k in instr:
        opts |= {o.upper() for o in S4_OPT.findall(lines[k])}
    rec['S4'] = dict(hit=len(opts) >= 3, n=len(opts))
    i, _ = scan_lines(lines, range(body_start, len(lines)), S5_KW)
    rec['S5'] = dict(hit=i is not None, line=(i + 1) if i is not None else None)

    rec['X2'] = detect_x2(lines, body_start)
    i, _ = scan_lines(lines, tail, X2_WEAK)
    rec['X2_weak'] = dict(hit=i is not None and not rec['X2']['hit'], line=(i + 1) if i is not None else None)
    # X1（啟發式）：指令區提到單內人工 runtime；同一行寫延後就記 X1-延後
    x1, x1d, in_ac = None, None, False
    for k in instr:
        h = HEADING.match(lines[k])
        if h:
            in_ac = bool(AC_HEAD.search(h.group(2)))
        if not (in_ac or AC_LINE.match(lines[k])):
            continue
        if X1_KW.search(lines[k]):
            near = ' '.join(lines[max(0, k - 1):k + 2])
            if X1_DEFER.search(near):
                x1d = x1d if x1d is not None else k
            else:
                x1 = k
                break
    rec['X1'] = dict(hit=x1 is not None, heuristic=True, line=(x1 + 1) if x1 is not None else None,
                     evidence=snip(lines[x1]) if x1 is not None else '')
    rec['X1_defer'] = dict(hit=x1 is None and x1d is not None, line=(x1d + 1) if x1d is not None else None)
    # X3：跨天、Renew、session 接續
    st, ct = parse_ts(fm.get('started_at')), parse_ts(fm.get('completed_at'))
    if not st:
        m = re.search(r'開始時間[^\d\n]{0,8}(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:?\d{2})?)', text)
        st = parse_ts(m.group(1)) if m else None
    if not ct:
        m = re.search(r'完成時間[^\d\n]{0,8}(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:?\d{2})?)', text)
        ct = parse_ts(m.group(1)) if m else None
    x3 = []
    if st and ct and st.date() != ct.date():
        x3.append('跨天')
    if renew > 0 or renew_h is not None:
        x3.append('Renew')
    i, _ = scan_lines(lines, tail, re.compile(r'接續上一個 session|跨 session|上一個 session 中斷'))
    if i is not None:
        x3.append('session 接續')
    rec['X3'] = dict(hit=bool(x3), via=x3)
    # X4（啟發式）：(a) 一支腳本／一條指令；(b) 清單 N ≥ 3 但只改一個檔
    x4 = []
    i, _ = scan_lines(lines, instr, X4_ONE)
    if i is not None:
        x4.append('(a) L%d' % (i + 1))
    i, m = scan_lines(lines, instr, X4_MECH)
    if i is not None:
        x4.append('(a) 逐一＋機械動作 L%d「%s」' % (i + 1, snip(m.group(0), 24)))
    if rec['S1'].get('hit') and rec['S1'].get('same_file'):
        x4.append('(b) 清單 N=%d 但 affects_files 只有 ≤ 2 檔' % rec['S1']['n'])
    commits = sum(1 for k in instr if re.search(r'git commit\b', raw[k]))
    if commits >= 2:
        x4.append('(c) 指令區預先寫好 %d 個 git commit' % commits)
    rec['X4'] = dict(hit=bool(x4), heuristic=True, via=x4)
    # 規模（只記錄，不排除）
    minutes = None
    if st and ct:
        if st.tzinfo is None and ct.tzinfo is not None:
            st = st.replace(tzinfo=ct.tzinfo)
        if ct.tzinfo is None and st.tzinfo is not None:
            ct = ct.replace(tzinfo=st.tzinfo)
        try:
            minutes = round((ct - st).total_seconds() / 60, 1)
        except TypeError:
            minutes = None
    rec['minutes'] = minutes
    rec['small'] = (minutes is not None and 0 <= minutes <= 15)
    if minutes is not None and minutes < 0:
        rec['notes'].append('耗時為負（started_at 晚於 completed_at）')
    i, m = scan_lines(lines, tail, SUBAGENT)
    rec['subagent'] = dict(hit=i is not None, term=m.group(0) if m else '', line=(i + 1) if i is not None else None,
                           evidence=snip(lines[i]) if i is not None else '')
    rec['_norm'] = norm_title(title)
    pm = re.match(r'^(.{2,30}?)\s*[：:—–]', title)
    rec['_prefix'] = norm_title(pm.group(1)) if pm else ''  # 「探針：…」這類標題模板的前綴
    tpl = set()
    for k in instr:
        for m in TPL_REF.finditer(lines[k]):
            tpl |= set(re.findall(r'(?:CP-|CT-)?T\d{3,4}(?:\.\d+)?', m.group(0)))
    tpl.discard(wid)
    rec['_tplrefs'] = sorted(tpl)
    return rec


# ---------------------------------------------------------------- X5：系列重複

def norm_title(t):
    t = t.lower()
    t = re.sub(r'(?:cp-|ct-)?t\d{3,4}[a-z]?(?:\.\d+)?|bug-\d+|plan-\d+|exp-[\w-]+|\bd\d{3}\b|v?\d+(?:\.\d+)+|\d+', ' ', t)
    t = re.sub(r'[\W_]+', '', t)
    return t


def bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def id_num(wid):
    m = re.search(r'T(\d+)', wid)
    return int(m.group(1)) if m else -1


def mark_x5(recs, window=15, sim_neighbor=0.55, sim_dep=0.35):
    """同系列的邊有三種：depends_on 指向標題相似（≥ sim_dep）的工單；編號相距 ≤ window 且標題相似
    （≥ sim_neighbor）；指令區明說沿用／比照某張工單（模板引用）。連通塊 ≥ 3 張即為系列；
    系列成員若 S1 不是嚴格版，記 X5。"""
    by_id = {r['id']: k for k, r in enumerate(recs)}
    grams = [bigrams(r['_norm']) for r in recs]
    parent = list(range(len(recs)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b, why):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
        via[a].add(why)
        via[b].add(why)

    via = [set() for _ in recs]
    order = sorted(range(len(recs)), key=lambda k: id_num(recs[k]['id']))
    for pos, a in enumerate(order):
        na = id_num(recs[a]['id'])
        for b in order[pos + 1:]:
            if id_num(recs[b]['id']) - na > window:
                break
            if jaccard(grams[a], grams[b]) >= sim_neighbor:
                union(a, b, '標題相似')
    for a, r in enumerate(recs):
        for d in r['depends_on']:
            b = by_id.get(d)
            if b is not None and b != a and (jaccard(grams[a], grams[b]) >= sim_dep
                                             or (r['_prefix'] and r['_prefix'] == recs[b]['_prefix'])):
                union(a, b, 'depends_on 串鏈')
        for d in r.get('_tplrefs', []):
            b = by_id.get(d)
            if b is not None and b != a:
                union(a, b, '模板引用')
    groups = collections.defaultdict(list)
    for k in range(len(recs)):
        groups[find(k)].append(k)
    for g in groups.values():
        if len(g) < 3:
            continue
        ids = sorted((recs[k]['id'] for k in g), key=id_num)
        for k in g:
            r = recs[k]
            r['series'] = dict(size=len(g), head=ids[0], tail=ids[-1], via=sorted(via[k]))
    for r in recs:
        s1_strict = r['S1'].get('strength') == 'strict'
        r['X5'] = dict(hit=('series' in r) and not s1_strict, series=r.get('series'))


def mark_cross_s3(recs):
    by_id = {r['id']: r for r in recs}
    for r in recs:
        for t, line, ev in r.get('_refutes', []):
            tgt = by_id.get(t)
            if tgt is None or id_num(t) >= id_num(r['id']):
                continue  # 只算「後續工單」指出前單有誤
            tgt['S3']['hit'] = True
            tag = '後續 %s' % r['id']
            if tag not in tgt['S3']['via']:
                tgt['S3']['via'].append(tag)
                tgt['S3'].setdefault('cross', []).append('%s L%d「%s」' % (r['id'], line, ev))


# ---------------------------------------------------------------- 分軌（T0177 § 3.1）

def classify(r):
    xs = [x for x in ('X1', 'X2', 'X3', 'X4') if r[x]['hit']]
    r['X_hits'] = xs
    r['X_reliable'] = [x for x in xs if x in ('X2', 'X3')]
    fan = r['S1'].get('strength') == 'strict'
    ver = r['S3']['hit']
    if xs:
        track = 'excluded'
    elif r['X5']['hit']:
        track = 'playbook'
    elif fan and ver:
        track = 'both'
    elif fan:
        track = 'fanout'
    elif ver:
        track = 'verify'
    elif r['S4']['hit'] or r['S1'].get('hit'):
        track = 'border'
    else:
        track = 'general'
    r['track'] = track
    # 只套腳本可靠的 X（X2、X3）時的分軌，給「啟發式 X1／X4 太嚴」的對照
    if r['X_reliable']:
        r['track_reliable_x'] = 'excluded'
    elif r['X5']['hit']:
        r['track_reliable_x'] = 'playbook'
    else:
        r['track_reliable_x'] = 'both' if fan and ver else 'fanout' if fan else 'verify' if ver else \
            ('border' if r['S4']['hit'] or r['S1'].get('hit') else 'general')
    r['needs_manual'] = ['S6（子項獨立性）'] + (['X1（啟發式）'] if r['X1']['hit'] else []) + \
        (['X4（啟發式）'] if r['X4']['hit'] else []) + (['S3 族內事件數'] if ver else [])
    return r


TRACK_ZH = dict(both='兩軌', fanout='扇出軌', verify='驗證軌', border='邊界', playbook='X5→Playbook',
                excluded='排除', general='一般執行')


def evidence_of(r):
    out = []
    if r['S1'].get('hit'):
        where = 'title' if r['S1'].get('src') == 'title' else 'L%d' % r['S1']['line']
        out.append('S1(%s,N=%d,args=%s) %s「%s」' % (r['S1']['strength'], r['S1']['n'], r['S1']['args'],
                                                   where, r['S1']['evidence']))
    if r['S3']['hit']:
        out.append('S3 %s%s' % ('/'.join(r['S3']['via']), (' L%d' % r['S3']['line']) if r['S3']['line'] else ''))
    if r['subagent']['hit']:
        out.append('子代理 L%d「%s」' % (r['subagent']['line'], r['subagent']['evidence']))
    return '；'.join(out)


def gate_of(r):
    """排除守門（analysis-rules.md § 預篩腳本）：只用可靠的 X2、X3、X5。回傳 (結論, 命中與證據清單)。"""
    why = []
    if r['X2']['hit']:
        why.append('X2 %s%s' % ('/'.join(r['X2']['sources']), (' L%d' % r['X2']['line']) if r['X2']['line'] else ''))
    if r['X3']['hit']:
        why.append('X3 %s' % '/'.join(r['X3']['via']))
    if r['X5']['hit']:
        s = r['X5']['series']
        why.append('X5 系列 %s–%s（%d 張；%s）' % (s['head'], s['tail'], s['size'], '、'.join(s['via'])))
    if r['X2']['hit'] or r['X3']['hit']:
        return '不考慮 Workflow', why
    if r['X5']['hit']:
        return '不考慮 Workflow；提示 Playbook', why
    return '未擋下', why


def show_ids(label, recs, ids):
    """按需提示（--ids）：逐張列守門結果、主判定與證據位置。只讀，不改工單。"""
    by_id = {r['id']: r for r in recs}
    p = print
    p('\n## %s：守門結果（--ids）\n' % label)
    p('| 工單 | 守門 | 守門命中 | 主判定（全部 X） | 需人工 | 證據位置 |\n|---|---|---|---|---|---|')
    for i in ids:
        r = by_id.get(i)
        if r is None:
            p('| %s | （找不到這張工單） | | | | |' % i)
            continue
        verdict, why = gate_of(r)
        manual = list(r['needs_manual']) if verdict == '未擋下' else []
        p('| %s | %s | %s | %s | %s | `%s`：%s |' % (
            i, verdict, '；'.join(why).replace('|', '\\|') or '—', TRACK_ZH[r['track']],
            '、'.join(manual) or '—', r['path'], evidence_of(r).replace('|', '\\|') or '—'))


# ---------------------------------------------------------------- 掃描與摘要

def load_dir(root):
    recs, skipped = [], collections.Counter()
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for f in sorted(fn):
            if not WO_NAME.match(f):
                continue
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root).replace(os.sep, '/')
            with open(full, encoding='utf-8-sig', errors='replace') as h:
                text = h.read()
            fm, _ = parse_frontmatter(text)
            ok, why = is_workorder(rel, fm, text)
            if not ok:
                skipped[why] += 1
                continue
            recs.append(evaluate(full, rel, text))
    # 同一 id 有多個檔：頂層優先於 _archive，其次取較大的檔
    seen, dups = {}, []
    for r in sorted(recs, key=lambda r: (r['path'].startswith('_archive'), -r['bytes'])):
        if r['id'] in seen:
            dups.append((r['id'], r['path'], seen[r['id']]['path']))
            continue
        seen[r['id']] = r
    uniq = sorted(seen.values(), key=lambda r: (id_num(r['id']), r['id']))
    mark_cross_s3(uniq)
    mark_x5(uniq)
    for r in uniq:
        classify(r)
    return uniq, skipped, dups


def pct(a, b):
    return '%d（%.1f%%）' % (a, 100.0 * a / b) if b else '0'


def summarize(label, recs, skipped, dups, top):
    n = len(recs)
    p = print
    p('\n## %s\n' % label)
    p('- 工單數：**%d**（同 id 重複 %d 檔已去重；檔名相符但判定非工單 %d 檔：%s）'
      % (n, len(dups), sum(skipped.values()), dict(skipped) or '無'))
    p('\n| 規則 | 命中 | 比例 |\n|---|---|---|')
    rows = [
        ('S1 嚴格（cue＋N≥3＋執行前可列＋非單檔）', sum(r['S1'].get('strength') == 'strict' for r in recs)),
        ('S1 弱（cue＋N≥3，但 args 不明／執行中／單檔／同行寫依序）', sum(r['S1'].get('strength') == 'weak' for r in recs)),
        ('S3 訊號（Renew／推翻／改判…）', sum(r['S3']['hit'] for r in recs)),
        ('S4（≥3 個方案）', sum(r['S4']['hit'] for r in recs)),
        ('S5（context 風險高）', sum(r['S5']['hit'] for r in recs)),
        ('S6 串行字樣提示（反訊號，需人工）', sum(r['S6']['serial_hint'] is not None for r in recs)),
        ('X1 啟發式（單內人工 runtime）', sum(r['X1']['hit'] for r in recs)),
        ('X1-延後（只記錄）', sum(r['X1_defer']['hit'] for r in recs)),
        ('X2 三來源', sum(r['X2']['hit'] for r in recs)),
        ('X2-弱（只記錄）', sum(r['X2_weak']['hit'] for r in recs)),
        ('X3（跨天／Renew／接續）', sum(r['X3']['hit'] for r in recs)),
        ('X4 啟發式', sum(r['X4']['hit'] for r in recs)),
        ('X5（系列重複且單張非 S1 嚴格）', sum(r['X5']['hit'] for r in recs)),
        ('子代理輔助訊號', sum(r['subagent']['hit'] for r in recs)),
    ]
    for k, v in rows:
        p('| %s | %d | %.1f%% |' % (k, v, 100.0 * v / n if n else 0))
    for key, cap in (('track', '全部 X 套用（主判定）'), ('track_reliable_x', '只套 X2、X3（對照）')):
        c = collections.Counter(r[key] for r in recs)
        p('\n分軌｜%s：' % cap + '、'.join('%s %s' % (TRACK_ZH[t], pct(c[t], n))
                                      for t in ('both', 'fanout', 'verify', 'border', 'playbook', 'excluded', 'general')))
    xc = collections.Counter(tuple(r['X_hits']) for r in recs if r['X_hits'])
    p('\nX 排除分布（組合）：' + '、'.join('%s %d' % ('+'.join(k), v) for k, v in xc.most_common(8)))
    gc = collections.Counter(gate_of(r)[0] for r in recs)
    p('\n排除守門（X2、X3、X5）：不考慮 Workflow %s（其中提示 Playbook %d）、未擋下 %s'
      % (pct(gc['不考慮 Workflow'] + gc['不考慮 Workflow；提示 Playbook'], n), gc['不考慮 Workflow；提示 Playbook'],
         pct(gc['未擋下'], n)))
    mins = [r['minutes'] for r in recs if r['minutes'] is not None and r['minutes'] >= 0]
    buckets = collections.Counter(
        '≤15' if m <= 15 else '15–60' if m <= 60 else '60–240' if m <= 240 else '>240' for m in mins)
    mins.sort()
    med = mins[len(mins) // 2] if mins else None
    p('\n耗時（可算 %d 張，未知 %d 張；中位數 %s 分）：%s' % (
        len(mins), n - len(mins), med, '、'.join('%s 分 %d' % (k, buckets[k]) for k in ('≤15', '15–60', '60–240', '>240'))))
    order = {'both': 0, 'fanout': 1, 'verify': 2}
    cands = [r for r in recs if r['track'] in order]
    cands.sort(key=lambda r: (order[r['track']], not r['subagent']['hit'], -(r['S1'].get('n') or 0), -len(r['S3']['via'])))
    p('\n前 %d 名候選（共 %d 張）：\n\n| # | 工單 | 軌道 | 命中規則 | 耗時 | 證據位置 |\n|---|---|---|---|---|---|' % (min(top, len(cands)), len(cands)))
    for k, r in enumerate(cands[:top], 1):
        hits = [s for s in ('S1', 'S3', 'S4', 'S5') if r[s].get('hit')] + (['子代理'] if r['subagent']['hit'] else []) \
            + (['X2-弱'] if r['X2_weak']['hit'] else []) + (['X1-延後'] if r['X1_defer']['hit'] else [])
        p('| %d | %s | %s | %s | %s | `%s`：%s |' % (k, r['id'], TRACK_ZH[r['track']], '、'.join(hits),
                                                 '%s 分' % r['minutes'] if r['minutes'] is not None else '未知',
                                                 r['path'], evidence_of(r).replace('|', '\\|')))


# ---------------------------------------------------------------- BAT 校準

# T0177 附錄 A（使用者 30/30 認同，D081）的定案判定：cand／border／general／excl:Xn
T0177_APPENDIX_A = {
    'T0034': 'cand', 'T0208': 'general', 'T0353': 'general', 'T0224': 'general', 'T0313': 'general',
    'T0490': 'border', 'T0671': 'border', 'T0653': 'cand', 'T0260': 'general', 'T0032.5': 'border',
    'T0075': 'excl:X4', 'T0083': 'excl:X4', 'T0602': 'excl:X4', 'T0186': 'excl:X4', 'T0190': 'excl:X4',
    'T0570': 'excl:X4', 'T0474': 'excl:X4', 'T0479': 'general', 'T0080': 'general', 'T0066': 'general',
    'T0121': 'general', 'T0102': 'general', 'T0094': 'excl:X4', 'T0559': 'excl:X5', 'T0561': 'excl:X5',
    'T0627': 'excl:X2+X5', 'T0629': 'excl:X2+X5', 'T0267': 'general', 'T0633': 'border', 'T0298': 'general',
}
T0177_X2_EXTRA = {'T0118', 'T0120'}          # T0177 定案偵測多抓的 2 張
T0177_SUBAGENT = ['T0646', 'T0653', 'T0661', 'T0534', 'T0385', 'T0574']
T0177_R = {'R1': ['T0646', 'T0653', 'T0661', 'T0534'], 'R2': ['T0292', 'T0293'], 'R3': ['T0252', 'T0034']}


def coarse(track):
    return {'both': 'cand', 'fanout': 'cand', 'verify': 'cand', 'border': 'border',
            'playbook': 'excl:X5', 'excluded': 'excl', 'general': 'general'}[track]


def calibrate(jsonl_path, top):
    root = os.path.dirname(os.path.abspath(jsonl_path))  # jsonl 位於 _ct-workorders/
    pilot = [json.loads(l) for l in open(jsonl_path, encoding='utf-8') if l.strip()]
    recs, missing = [], []
    for row in pilot:
        rel = row['path'].split('_ct-workorders/', 1)[-1]
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            missing.append(rel)
            continue
        with open(full, encoding='utf-8-sig', errors='replace') as h:
            text = h.read()
        r = evaluate(full, rel, text)
        r['pilot_id'] = row['id']  # 試點把 T0032.5 記成 T0032，id 以檔名為準
        r['_pilot'] = row
        recs.append(r)
    mark_cross_s3(recs)
    mark_x5(recs)
    for r in recs:
        classify(r)
    n = len(recs)
    p = print
    p('\n## BAT 校準（%s，%d 筆；找不到檔 %d）\n' % (os.path.basename(jsonl_path), n, len(missing)))
    ph = lambda r, k: r['_pilot']['exclusions' if k.startswith('X') else 'signals'][k]['hit']

    def cmp(name, mine, theirs, ref=None):
        tp = [r['id'] for r in recs if mine(r) and theirs(r)]
        fn = [r['id'] for r in recs if theirs(r) and not mine(r)]
        fp = [r['id'] for r in recs if mine(r) and not theirs(r)]
        tot = len(tp) + len(fn)
        p('| %s | %d | %d | %s | %d | %d | %s |' % (name, len(tp) + len(fp), tot, pct(len(tp), tot), len(fn), len(fp),
                                               ref or ''))
        return tp, fn, fp

    p('| 項目 | 腳本命中 | 試點命中 | 召回（腳本∩試點） | 漏抓 | 多抓 | T0177 定案值 |\n|---|---|---|---|---|---|---|')
    _, _, fp2 = cmp('X2 三來源', lambda r: r['X2']['hit'], lambda r: ph(r, 'X2'), '51/73（70%），多抓 2（T0118、T0120）')
    _, _, fp5 = cmp('X5（系列且非 S1 嚴格）', lambda r: r['X5']['hit'],
                    lambda r: ph(r, 'S2') and not ph(r, 'S1'), '109（原 S2 且非 S1）')
    cmp('S1（腳本嚴格 vs 試點 S1）', lambda r: r['S1'].get('strength') == 'strict', lambda r: ph(r, 'S1'),
        '試點 S1 含回報區表格，非嚴格版')
    cmp('X1 啟發式', lambda r: r['X1']['hit'], lambda r: ph(r, 'X1'), '—')
    cmp('X3', lambda r: r['X3']['hit'], lambda r: ph(r, 'X3'), '—')
    cmp('X4 啟發式', lambda r: r['X4']['hit'], lambda r: ph(r, 'X4'), '—')
    cmp('S3 訊號', lambda r: r['S3']['hit'], lambda r: ph(r, 'S3'), '—')
    p('\n- X2 多抓清單：%s（T0177 定案多抓：%s）' % (', '.join(fp2) or '無', ', '.join(sorted(T0177_X2_EXTRA))))
    p('- X5 多抓前 15：%s' % ', '.join(fp5[:15]))
    c = collections.Counter(r['track'] for r in recs)
    cr = collections.Counter(r['track_reliable_x'] for r in recs)
    pos = sum(1 for r in recs if not any(ph(r, x) for x in ('X1', 'X2', 'X3', 'X4')) and ph(r, 'S1'))
    p('- 候選數：腳本 扇出軌 %d、驗證軌 %d、兩軌 %d（只套 X2/X3：%d／%d／%d）；試點「無 X 且 S1」%d；T0177 定案 95'
      % (c['fanout'], c['verify'], c['both'], cr['fanout'], cr['verify'], cr['both'], pos))
    byid = {}
    for r in recs:
        if r['id'] not in byid or 'report' not in r['path']:
            byid.setdefault(r['id'], r)
            if 'report' not in r['path']:
                byid[r['id']] = r
    p('- 子代理訊號：腳本共 %d 張；T0177 已知 6 張命中 %s'
      % (sum(r['subagent']['hit'] for r in recs),
         '、'.join('%s%s' % (i, '✓' if byid.get(i, {}).get('subagent', {}).get('hit') else '✗') for i in T0177_SUBAGENT)))
    p('- T0177 R1–R3 成員：' + '；'.join('%s ' % k + '、'.join('%s=%s' % (i, TRACK_ZH[byid[i]['track']]) for i in v if i in byid)
                                     for k, v in T0177_R.items()))
    p('\n附錄 A 30 張：腳本 vs T0177 定案\n\n| 工單 | 定案 | 腳本（全部 X） | 腳本（只 X2/X3） | 腳本命中 | 一致 |\n|---|---|---|---|---|---|')
    agree = agree_r = 0
    for i, exp in T0177_APPENDIX_A.items():
        r = byid.get(i)
        if not r:
            p('| %s | %s | （找不到） | | | |' % (i, exp))
            continue
        got = coarse(r['track'])
        got_r = coarse(r['track_reliable_x'])
        ok = got.split(':')[0] == exp.split(':')[0]
        ok_r = got_r.split(':')[0] == exp.split(':')[0]
        agree += ok
        agree_r += ok_r
        hits = [s for s in ('S1', 'S3', 'S4') if r[s].get('hit')] + r['X_hits'] + (['X5'] if r['X5']['hit'] else [])
        p('| %s | %s | %s | %s | %s | %s |' % (i, exp, TRACK_ZH[r['track']], TRACK_ZH[r['track_reliable_x']],
                                           '、'.join(hits) or '—', '✓' if ok else '✗'))
    p('\n附錄 A 一致率：全部 X %d/30；只 X2/X3 %d/30（比對粗類：候選／邊界／一般／排除）' % (agree, agree_r))
    pos_exp = {i for i, e in T0177_APPENDIX_A.items() if e in ('cand', 'border')}
    pos_got = {i for i in T0177_APPENDIX_A if i in byid and coarse(byid[i]['track']) in ('cand', 'border')}
    p('附錄 A 正向（候選＋邊界）：定案 %d 張、腳本 %d 張、交集 %d 張（%s）；腳本多出：%s'
      % (len(pos_exp), len(pos_got), len(pos_exp & pos_got), '、'.join(sorted(pos_exp & pos_got)) or '無',
         '、'.join(sorted(pos_got - pos_exp)) or '無'))
    return recs


# ---------------------------------------------------------------- main

def dump(path, recs, label):
    with open(path, 'a', encoding='utf-8') as h:
        for r in recs:
            o = {k: v for k, v in r.items() if not k.startswith('_')}
            o['project'] = label
            h.write(json.dumps(o, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('dirs', nargs='*')
    ap.add_argument('--label', action='append', default=[])
    ap.add_argument('--jsonl')
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--calibrate')
    ap.add_argument('--ids', action='append', default=[])
    a = ap.parse_args()
    ids = [t.strip() for s in a.ids for t in s.split(',') if t.strip()]
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if a.jsonl and os.path.exists(a.jsonl):
        os.remove(a.jsonl)
    print('# ct-workflow-prefilter 摘要（Python %s）' % sys.version.split()[0])
    if a.calibrate:
        recs = calibrate(a.calibrate, a.top)
        if a.jsonl:
            dump(a.jsonl, recs, 'BAT-calibration')
    for k, d in enumerate(a.dirs):
        label = a.label[k] if k < len(a.label) else os.path.basename(os.path.dirname(os.path.abspath(d)))
        recs, skipped, dups = load_dir(d)
        if ids:
            show_ids(label, recs, ids)
        else:
            summarize(label, recs, skipped, dups, a.top)
        if a.jsonl:
            dump(a.jsonl, recs, label)


if __name__ == '__main__':
    main()
