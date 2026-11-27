#!/usr/bin/env python3
"""check-frontmatter.py — CT 寫的 YAML frontmatter 寫入後自檢（T0549；v6.0.1 起隨 control-tower 發行；v6.1.0 起另檢查契約 v2 欄位，T0557；
v6.2.0 起另檢查 awaiting_user[].recommended 與 inbox_features，T0566；v6.3.0 起另檢查 awaiting_user[].multi 與多個代號的 recommended，T0573）。

規則的權威是 control-tower/references/memory-protocol.md § YAML frontmatter 字串寫法與寫入後自檢。
本腳本只做其中「可機器檢查」的部分，規則有變以權威檔為準，再改這裡。

用法：
  python -X utf8 -I -B <control-tower>/scripts/check-frontmatter.py <路徑> [<路徑> ...]
  python -X utf8 -I -B <control-tower>/scripts/check-frontmatter.py _ct-workorders/            # 檢查目錄裡的 *.md（不含子目錄）
  python -X utf8 -I -B <control-tower>/scripts/check-frontmatter.py -r <目錄>                  # 含子目錄（略過 . 開頭的目錄）

  --recursive, -r  目錄連子目錄一起檢查
  --no-yaml        不用 PyYAML 做完整解析（只做本腳本的檢查；測試用）
  --verbose, -v    通過的檔也列出
  --quiet, -q      只印最後的結論一行

依賴：只用 Python 3.8+ 標準函式庫。環境裡有 PyYAML 時，本腳本自己的檢查都通過後，再用 yaml.safe_load
做一次完整解析（多抓本腳本沒涵蓋的語法錯誤）；沒有 PyYAML 一樣能用。

檢查項（問題代碼）：
  no-frontmatter        直接指定的檔第一行不是 ---（目錄掃描時沒有 frontmatter 的檔只略過、不算問題）
  bom                   檔案以 BOM 開頭（frontmatter 要從第一個位元組開始）
  unclosed-frontmatter  有開頭 --- 但找不到結尾 ---
  bad-escape            雙引號字串裡有 YAML 1.2 合法跳脫以外的 \\X（例：Windows 路徑的 \\U、\\m）
  unclosed-quote        引號字串沒有閉合
  stray-single-quote    單引號字串裡有單獨的 '（要寫成 ''）
  text-after-quote      雙引號字串結束後還有文字（字串裡有未跳脫的 "）
  unclosed-flow         [ ] 或 { } 沒有閉合
  plain-indicator       沒加引號的值以 YAML 指示字元開頭（` @ % * & ! , ] } 或 "- "、"? "）
  colon-in-plain        沒加引號的值裡有 ": "（或以 : 結尾）
  tab-indent            縮排用了 tab
  not-utf8              檔案不是 UTF-8
  yaml-error            （有 PyYAML 時）完整解析失敗；只印 PyYAML 的問題描述，不印原文
  not-mapping           （有 PyYAML 時）frontmatter 頂層不是 mapping

契約 v2 欄位（v6.1.0 起；權威 memory-protocol.md § 契約 v2 欄位）。上面的語法檢查都通過後才做；
只對 schema_kind: tower-state 的檔檢查 v2 欄位（沒有這些欄位的 6.0.x 狀態檔照舊通過），waiting-user 對任何檔都檢查：
  v2-type               bat_contract 不是整數（加了引號也算）；清單或清單項目的形狀不對（例：awaiting_user 不是清單）
  v2-missing            清單項目缺少必填鍵（awaiting_user：id、summary；user_actions：id、title；reminders：id、title、due_at）
  v2-id                 id 格式不符（awaiting_user ^U-\\d+$、user_actions ^A-\\d+$、reminders ^[a-z0-9-]{1,40}$）
  v2-option             options 的項目不是「<代號> <說明>」（代號 ^[A-Za-z0-9]{1,3}$），或同一筆的代號重複（不分大小寫）
  v2-length             summary／title 超過 120 字、command 超過 300 字
  v2-date               reminders 的 due_at（或 last_at）不是可解析的 ISO 日期或日期時間
  v2-next-id            next_ids.user 不是 "U-n"、next_ids.action 不是 "A-n"
  v2-recommended        （v6.2.0 起）awaiting_user 的 recommended 不是字串（沒加引號的數字也算）、對不到同一筆 options 的
                        任何代號（不分大小寫），或 options 是空清單（自由回答）卻寫了 recommended
                        （v6.3.0 起）recommended 有多個代號（以「、」連接）但該筆不是 multi: true，或其中任何一個代號對不到
  v2-features           （v6.2.0 起）inbox_features 不是字串清單（例：不是清單、項目是數字或巢狀清單）；不認得的值不報錯
  v2-multi              （v6.3.0 起）awaiting_user 的 multi 不是布林（只收不加引號的 true／false；加了引號、yes／no 都算錯）
  waiting-user          工單 frontmatter 的 waiting_user 不是 "U-n"
  v2-count（警告）      awaiting_user 超過 20 筆、user_actions 超過 20 筆或 reminders 超過 10 筆；只警告，不影響 exit code
  v2-multi-ignored（警告）（v6.3.0 起）options 少於 2 項（含空清單、沒有 options）卻寫了 multi: true；讀者會忽略它，
                        所以只警告，不影響 exit code
  v2-skipped（警告）    本腳本的小型解析器看不懂這份 frontmatter，契約 v2 欄位沒有檢查（語法檢查照常）

輸出：只印檔名、行號、欄號與問題類型，不印檔案原文。問題印成「- FAIL …」，警告印成「- WARN …」（格式相同）。
exit 0 = 全部通過（可以有警告）；1 = 有問題；2 = 用法錯誤或路徑不存在。

所有輸入只讀，不寫任何檔。
"""
import argparse
import os
import re
import sys

BS = chr(92)  # 反斜線；原始碼裡不直接寫反斜線字面，避免編輯工具改寫
# YAML 1.2 雙引號字串的合法跳脫（反斜線後一個字元）；x／u／U 另外要求 2／4／8 個十六進位數字
SIMPLE_ESCAPES = set('0abtnvfre "/N_LP' + '\t' + BS)
HEX_ESCAPES = {'x': 2, 'u': 4, 'U': 8}
HEXDIGITS = set('0123456789abcdefABCDEF')
PLAIN_BAD_FIRST = {
    '`': '以 ` 開頭（YAML 保留字元）',
    '@': '以 @ 開頭（YAML 保留字元）',
    '%': '以 % 開頭（YAML 指示字元）',
    '*': '以 * 開頭（會被當成別名）',
    '&': '以 & 開頭（會被當成錨點）',
    '!': '以 ! 開頭（會被當成標籤）',
    ',': '以 , 開頭（YAML 指示字元）',
    ']': '以 ] 開頭（YAML 指示字元）',
    '}': '以 } 開頭（YAML 指示字元）',
}
BLOCK_SCALAR_RE = re.compile(r'^[|>][0-9+-]*[ \t]*(#.*)?$')
PROBLEM_TEXT = {
    'no-frontmatter': '第一行不是 ---（沒有 frontmatter）',
    'bom': '檔案以 BOM 開頭；frontmatter 要從第一個位元組開始',
    'unclosed-frontmatter': '有開頭 --- 但找不到結尾 ---',
    'unclosed-quote': '引號字串沒有閉合',
    'stray-single-quote': "單引號字串裡有單獨的 '（字串內的 ' 要寫成 ''）",
    'text-after-quote': '雙引號字串結束後還有文字（字串內有未跳脫的 "）；含反斜線或雙引號的值改用單引號',
    'unclosed-flow': '[ ] 或 { } 沒有閉合',
    'colon-in-plain': '沒加引號的值裡有「: 」或以 : 結尾；整個值要加引號',
    'tab-indent': '縮排用了 tab；YAML 縮排只能用空白',
    'not-utf8': '檔案不是 UTF-8',
    'not-mapping': 'frontmatter 頂層不是 mapping（鍵: 值）',
}


class FileReport:
    def __init__(self, path):
        self.path = path
        self.items = []  # (line, col, code, message)；line／col 從 1 起算，0 表示不適用
        self.warnings = []  # 同上格式；只警告，不影響 exit code（v6.1.0+）

    def add(self, line, col, code, msg=None):
        self.items.append((line, col, code, msg or PROBLEM_TEXT.get(code, code)))

    def warn(self, line, col, code, msg):
        self.warnings.append((line, col, code, msg))


# ---------------------------------------------------------------- 掃描器

class Scanner:
    """逐字掃描 frontmatter 的行（不含開頭與結尾的 ---）。line_base = 第一行在檔案中的行號。"""

    def __init__(self, lines, line_base, rep):
        self.lines = lines
        self.base = line_base
        self.rep = rep

    def report(self, i, j, code, msg=None):
        self.rep.add(self.base + i, j + 1, code, msg)

    # 雙引號字串：(i, j) 指在開頭的 "；回傳 (i2, j2, ok)，(i2, j2) 指在結尾 " 之後
    def scan_double(self, i, j):
        start = (i, j)
        line = self.lines[i]
        k = j + 1
        bad = []
        while True:
            if k >= len(line):
                i += 1
                if i >= len(self.lines):
                    return start, None, bad
                line = self.lines[i]
                k = 0
                continue
            c = line[k]
            if c == '"':
                return start, (i, k + 1), bad
            if c == BS:
                if k + 1 >= len(line):  # 行尾的反斜線 = 跳脫換行（合法）
                    k += 1
                    continue
                e = line[k + 1]
                if e in HEX_ESCAPES:
                    n = HEX_ESCAPES[e]
                    digits = line[k + 2:k + 2 + n]
                    if len(digits) != n or not all(d in HEXDIGITS for d in digits):
                        bad.append((i, k, '雙引號內的 ' + BS + e + ' 後面要接 %d 個十六進位數字（Windows 路徑請改用單引號或正斜線）' % n))
                        k += 2
                        continue
                    k += 2 + n
                    continue
                if e not in SIMPLE_ESCAPES:
                    shown = BS + e if ' ' < e < chr(127) else '反斜線＋U+%04X' % ord(e)  # 非 ASCII 只印碼位
                    bad.append((i, k, '雙引號內的 ' + shown + ' 不是合法跳脫（含反斜線的值改用單引號或正斜線）'))
                k += 2
                continue
            k += 1

    # 單引號字串：'' 是一個 '；單獨的 ' 結束字串
    def scan_single(self, i, j):
        start = (i, j)
        line = self.lines[i]
        k = j + 1
        while True:
            if k >= len(line):
                i += 1
                if i >= len(self.lines):
                    return start, None
                line = self.lines[i]
                k = 0
                continue
            if line[k] == "'":
                if k + 1 < len(line) and line[k + 1] == "'":
                    k += 2
                    continue
                return start, (i, k + 1)
            k += 1

    def rest_is_empty(self, i, j):
        rest = self.lines[i][j:]
        s = rest.lstrip(' \t')
        return s == '' or (s.startswith('#') and (len(rest) > len(s) or j == 0))

    def quoted(self, i, j, as_key_allowed):
        """掃描 (i, j) 開始的引號字串。回傳 (下一個要看的行號, 是否為鍵, 鍵之後的欄)。"""
        q = self.lines[i][j]
        if q == '"':
            start, end, bad = self.scan_double(i, j)
        else:
            start, end = self.scan_single(i, j)
            bad = []
        for (bi, bj, msg) in bad:
            self.report(bi, bj, 'bad-escape', msg)
        if end is None:
            self.report(start[0], start[1], 'unclosed-quote')
            return start[0] + 1, False, None
        ei, ej = end
        rest = self.lines[ei][ej:]
        stripped = rest.lstrip(' \t')
        if as_key_allowed and ei == start[0] and stripped.startswith(':') and (len(stripped) == 1 or stripped[1] in ' \t'):
            return ei, True, ej + (len(rest) - len(stripped)) + 1
        if self.rest_is_empty(ei, ej):
            return ei + 1, False, None
        if ei != start[0]:
            # 跨行後才閉合又接著文字：多半是開頭那行少了結尾引號
            self.report(start[0], start[1], 'unclosed-quote')
            return start[0] + 1, False, None
        if q == "'":
            self.report(ei, ej - 1, 'stray-single-quote')
        else:
            self.report(ei, ej - 1, 'text-after-quote')
        return ei + 1, False, None

    def flow(self, i, j):
        """[ ] 或 { }：檢查裡面的引號字串與括號閉合。回傳下一個要看的行號。"""
        start = (i, j)
        depth = 0
        k = j
        while True:
            if i >= len(self.lines):
                self.report(start[0], start[1], 'unclosed-flow')
                return start[0] + 1
            line = self.lines[i]
            if k >= len(line):
                i += 1
                k = 0
                continue
            c = line[k]
            if c in '[{':
                depth += 1
            elif c in ']}':
                depth -= 1
                if depth == 0:
                    if self.rest_is_empty(i, k + 1):
                        return i + 1
                    self.report(i, k + 1, 'unclosed-flow', '[ ] 或 { } 結束後還有文字')
                    return i + 1
            elif c == '"':
                _, end, bad = self.scan_double(i, k)
                for (bi, bj, msg) in bad:
                    self.report(bi, bj, 'bad-escape', msg)
                if end is None:
                    self.report(i, k, 'unclosed-quote')
                    return start[0] + 1
                i, k = end
                continue
            elif c == "'":
                _, end = self.scan_single(i, k)
                if end is None:
                    self.report(i, k, 'unclosed-quote')
                    return start[0] + 1
                i, k = end
                continue
            elif c == '#' and (k == 0 or line[k - 1] in ' \t'):
                i += 1
                k = 0
                continue
            k += 1

    def value(self, i, j, parent_indent):
        """檢查從 (i, j) 開始的值。回傳 (下一個要看的行號, 區塊字串的父縮排或 None)。"""
        line = self.lines[i]
        v = line[j:]
        if v.strip() == '' or v.lstrip().startswith('#'):
            return i + 1, None
        c = v[0]
        if c in '"\'':
            ni, is_key, kj = self.quoted(i, j, as_key_allowed=False)
            return ni, None
        if c in '[{':
            return self.flow(i, j), None
        if c in '|>' and BLOCK_SCALAR_RE.match(v):
            return i + 1, parent_indent
        self.plain(i, j)
        return i + 1, None

    def plain(self, i, j):
        v = self.lines[i][j:]
        m = re.search(r'[ \t]#', v)
        body = v[:m.start()] if m else v
        body = body.rstrip(' \t')
        if not body:
            return
        c = body[0]
        if c in PLAIN_BAD_FIRST:
            self.report(i, j, 'plain-indicator', '沒加引號的值' + PLAIN_BAD_FIRST[c] + '；整個值要加引號')
            return
        if c in '-?' and (len(body) == 1 or body[1] in ' \t'):
            self.report(i, j, 'plain-indicator', '沒加引號的值以「' + c + ' 」開頭；整個值要加引號')
            return
        for k in range(len(body)):
            if body[k] == ':' and (k + 1 == len(body) or body[k + 1] in ' \t'):
                self.report(i, j + k, 'colon-in-plain')
                return

    def run(self):
        block_indent = None
        i = 0
        n = len(self.lines)
        while i < n:
            line = self.lines[i]
            if block_indent is not None:
                ind = len(line) - len(line.lstrip(' '))
                if line.strip() == '' or ind > block_indent:
                    i += 1
                    continue
                block_indent = None
            stripped = line.lstrip(' \t')
            if stripped == '' or stripped.startswith('#'):
                i += 1
                continue
            lead = line[:len(line) - len(stripped)]
            if '\t' in lead:
                self.report(i, lead.index('\t'), 'tab-indent')
            j = len(lead)
            # 清單項目「- 」（可連續）
            is_item = False
            while j < len(line) and line[j] == '-' and (j + 1 == len(line) or line[j + 1] in ' \t'):
                is_item = True
                j += 1
                while j < len(line) and line[j] in ' \t':
                    j += 1
            if j >= len(line):
                i += 1
                continue
            key_col = j
            c = line[j]
            if c in '"\'':
                ni, is_key, kj = self.quoted(i, j, as_key_allowed=True)
                if not is_key:
                    i = ni
                    continue
                while kj < len(line) and line[kj] in ' \t':
                    kj += 1
                i, block_indent = self.value(i, kj, key_col)
                continue
            if c in '[{':
                i = self.flow(i, j)
                continue
            if c == '?' and (j + 1 == len(line) or line[j + 1] in ' \t'):
                i += 1
                continue
            # 找鍵的「:」：第一個後面接空白或在行尾的 :（在註解之前）
            m = re.search(r'[ \t]#', line[j:])
            seg_end = j + m.start() if m else len(line)
            colon = None
            for k in range(j, seg_end):
                if line[k] == ':' and (k + 1 == len(line) or line[k + 1] in ' \t'):
                    colon = k
                    break
            if colon is not None and line[j] not in PLAIN_BAD_FIRST:
                vj = colon + 1
                while vj < len(line) and line[vj] in ' \t':
                    vj += 1
                i, block_indent = self.value(i, vj, key_col)
                continue
            if is_item:
                if c in '|>' and BLOCK_SCALAR_RE.match(line[j:]):
                    block_indent = key_col - 2 if key_col >= 2 else 0
                    i += 1
                    continue
                self.plain(i, j)
            # 不是鍵也不是清單項目：多行純量的續行，不檢查
            i += 1


# ---------------------------------------------------------------- 契約 v2 欄位（v6.1.0+）
#
# 權威：memory-protocol.md § 契約 v2 欄位。只在上面的語法檢查全部通過後才跑，所以這裡的小型解析器
# 只需要看懂 CT 會寫的 YAML 子集（區塊 mapping／清單、引號字串、單層 [ ] 清單）；看不懂的寫法跳過不判斷。

V2_LISTS = ('awaiting_user', 'user_actions', 'reminders')
V2_LIMITS = {'awaiting_user': 20, 'user_actions': 20, 'reminders': 10}
V2_ID_RE = {
    'awaiting_user': (re.compile(r'^U-[0-9]+$'), 'U-<數字>'),
    'user_actions': (re.compile(r'^A-[0-9]+$'), 'A-<數字>'),
    'reminders': (re.compile(r'^[a-z0-9-]{1,40}$'), '1～40 個小寫英數字或 -'),
}
V2_REQUIRED = {
    'awaiting_user': ('id', 'summary'),
    'user_actions': ('id', 'title'),
    'reminders': ('id', 'title', 'due_at'),
}
V2_LEN_LIMITS = {'summary': 120, 'title': 120, 'command': 300}
V2_OPTION_RE = re.compile(r'^([A-Za-z0-9]{1,3})[ \t]+[^ \t]')
V2_INT_RE = re.compile(r'^[-+]?[0-9]+$')
# 沒加引號時 YAML 不會讀成字串的純量（數字、布林、null；v6.2.0+ 的 recommended／inbox_features 用來判斷型別）
V2_NON_STR_PLAIN_RE = re.compile(r'^(?:[-+]?(?:[0-9][0-9_]*(?:\.[0-9_]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?'
                                 r'|0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN)'
                                 r'|true|True|TRUE|false|False|FALSE|yes|Yes|YES|no|No|NO|on|On|ON|off|Off|OFF'
                                 r'|null|Null|NULL|~)$')
# v6.3.0+：awaiting_user[].multi 只接受 YAML 1.2 core 的布林（yes／no／on／off 在 YAML 1.2 是字串，不收）
V2_BOOL_RE = re.compile(r'^(?:true|True|TRUE|false|False|FALSE)$')
IDEO_COMMA = chr(0x3001)  # 「、」；v6.3.0+ 多個推薦代號的分隔
V2_DATE_RE = re.compile(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})'
                        r'(?:[Tt ]([0-9]{2}):([0-9]{2})(?::([0-9]{2})(?:[.,][0-9]+)?)?'
                        r'(?:[Zz]|[+-]([0-9]{2})(?::?([0-9]{2}))?)?)?$')
KEY_RE = re.compile(r'^([A-Za-z0-9_][A-Za-z0-9_. -]*?)[ \t]*:(?:[ \t]+|$)')


class Node:
    """kind：'map'（value = {鍵: (節點, 鍵的行, 鍵的欄)}）／'seq'（value = [節點]）／'scalar'。
    scalar 的 style：'plain'／'double'／'single'／'block'／'other'（看不懂的寫法，value 為 None）。line／col 從 0 起算。"""
    __slots__ = ('kind', 'value', 'style', 'line', 'col')

    def __init__(self, kind, value, line, col, style=None):
        self.kind = kind
        self.value = value
        self.style = style
        self.line = line
        self.col = col


def _indent(s):
    return len(s) - len(s.lstrip(' '))


def _meaningful(s):
    t = s.strip()
    return t != '' and not t.startswith('#')


def _is_item(content):
    return content[:1] == '-' and (len(content) == 1 or content[1] in ' \t')


def _quote_end(text, k):
    """text[k] 是引號；回傳結尾引號之後的位置，沒閉合回傳 None。"""
    q = text[k]
    m = k + 1
    while m < len(text):
        c = text[m]
        if q == '"' and c == BS:
            m += 2
            continue
        if c == q:
            if q == "'" and m + 1 < len(text) and text[m + 1] == "'":
                m += 2
                continue
            return m + 1
        m += 1
    return None


def _decode_double(body):
    out = []
    k = 0
    while k < len(body):
        c = body[k]
        if c == BS and k + 1 < len(body):
            e = body[k + 1]
            if e in HEX_ESCAPES:
                n = HEX_ESCAPES[e]
                try:
                    out.append(chr(int(body[k + 2:k + 2 + n], 16)))
                    k += 2 + n
                    continue
                except ValueError:
                    pass
            out.append({'n': chr(10), 't': chr(9), '0': chr(0)}.get(e, e))
            k += 2
            continue
        out.append(c)
        k += 1
    return ''.join(out)


def _scalar(text, line, col):
    t = text.strip()
    if t[:1] in ('"', "'"):
        end = _quote_end(t, 0)
        if end is None:
            return Node('scalar', None, line, col, 'other')
        body = t[1:end - 1]
        if t[0] == '"':
            return Node('scalar', _decode_double(body), line, col, 'double')
        return Node('scalar', body.replace("''", "'"), line, col, 'single')
    m = re.search(r'[ \t]#', t)
    if m:
        t = t[:m.start()]
    t = t.strip()
    return Node('scalar', t if t else None, line, col, 'plain')


def _split_flow(text):
    """text 以 [ 或 { 開頭；回傳 (頂層項目的原文清單, 結尾之後的文字)，沒閉合回傳 None。"""
    items, cur, k, depth = [], [], 1, 1
    while k < len(text):
        c = text[k]
        if c in ('"', "'"):
            end = _quote_end(text, k)
            if end is None:
                return None
            cur.append(text[k:end])
            k = end
            continue
        if c in '[{':
            depth += 1
        elif c in ']}':
            depth -= 1
            if depth == 0:
                items.append(''.join(cur))
                return [x.strip() for x in items if x.strip()], text[k + 1:]
        elif c == ',' and depth == 1:
            items.append(''.join(cur))
            cur = []
            k += 1
            continue
        cur.append(c)
        k += 1
    return None


class MiniYaml:
    def __init__(self, lines):
        self.lines = list(lines)
        self.n = len(self.lines)

    def next_meaningful(self, i):
        while i < self.n and not _meaningful(self.lines[i]):
            i += 1
        return i

    def parse_node(self, i, min_indent):
        i = self.next_meaningful(i)
        if i >= self.n:
            return None, i
        ind = _indent(self.lines[i])
        if ind < min_indent:
            return None, i
        if _is_item(self.lines[i][ind:]):
            return self.parse_seq(i, ind)
        return self.parse_map(i, ind)

    def parse_map(self, i, ind):
        node = Node('map', {}, i, ind)
        while True:
            i = self.next_meaningful(i)
            if i >= self.n:
                break
            line = self.lines[i]
            li = _indent(line)
            if li < ind:
                break
            if li > ind:
                i += 1  # 看不懂的縮排：跳過
                continue
            content = line[ind:]
            if _is_item(content):
                break
            m = KEY_RE.match(content)
            if not m:
                i += 1
                continue
            key = m.group(1).strip()
            key_line = i
            vj = ind + m.end()
            if not _meaningful(line[vj:]):
                j = self.next_meaningful(i + 1)
                if j < self.n and _indent(self.lines[j]) == ind and _is_item(self.lines[j][ind:]):
                    val, i = self.parse_seq(j, ind)
                elif j < self.n and _indent(self.lines[j]) > ind:
                    val, i = self.parse_node(j, ind + 1)
                else:
                    val, i = Node('scalar', None, i, vj, 'plain'), i + 1
            else:
                val, i = self.inline(i, vj, ind)
            node.value[key] = (val, key_line, ind)
        return node, i

    def parse_seq(self, i, ind):
        node = Node('seq', [], i, ind)
        while True:
            i = self.next_meaningful(i)
            if i >= self.n:
                break
            line = self.lines[i]
            li = _indent(line)
            if li != ind or not _is_item(line[ind:]):
                if li > ind:
                    i += 1
                    continue
                break
            k = ind + 1
            while k < len(line) and line[k] in ' \t':
                k += 1
            rest = line[k:]
            item_line = i
            if not _meaningful(rest):
                val, i = self.parse_node(i + 1, ind + 1)
                if val is None:
                    val = Node('scalar', None, item_line, k, 'plain')
            elif rest[:1] not in ('"', "'", '[', '{') and KEY_RE.match(rest):
                self.lines[i] = ' ' * k + rest  # 「- 鍵: 值」：把「- 」當成縮排，往下當 mapping 讀
                val, i = self.parse_map(i, k)
            elif _is_item(rest):
                self.lines[i] = ' ' * k + rest
                val, i = self.parse_seq(i, k)
            else:
                val, i = self.inline(i, k, ind)
            val.line, val.col = item_line, k
            node.value.append(val)
        return node, i

    def _join_until(self, i, t, done):
        """從第 i 行的 t 開始，必要時接下一行，直到 done(text) 不是 None。回傳 (text, 最後一行)。"""
        text, j = t, i
        while done(text) is None and j + 1 < self.n:
            j += 1
            text += ' ' + self.lines[j].strip()
        return text, j

    def inline(self, i, vj, ind):
        line = self.lines[i]
        t = line[vj:].lstrip(' \t')
        col = len(line) - len(t)
        if t[:1] in '|>' and BLOCK_SCALAR_RE.match(t):
            j = i + 1
            while j < self.n and (not self.lines[j].strip() or _indent(self.lines[j]) > ind):
                j += 1
            text = ' '.join(self.lines[x].strip() for x in range(i + 1, j))
            return Node('scalar', text, i, col, 'block'), j
        if t[:1] in '[{':
            text, j = self._join_until(i, t, _split_flow)
            got = _split_flow(text)
            if got is None or t[0] == '{':
                return Node('scalar', None, i, col, 'other'), j + 1
            return Node('seq', [_scalar(x, i, col) for x in got[0]], i, col), j + 1
        if t[:1] in ('"', "'"):
            text, j = self._join_until(i, t, lambda s: _quote_end(s, 0))
            return _scalar(text, i, col), j + 1
        j = i + 1
        while j < self.n and self.lines[j].strip() and _indent(self.lines[j]) > ind:
            j += 1  # 多行純量的續行
        return _scalar(t, i, col), j


def _str_value(node):
    if node is None or node.kind != 'scalar' or node.style in ('other', 'block') or node.value is None:
        return None
    return node.value


def _is_yaml_string(node):
    """節點是 YAML 會讀成字串的純量：引號字串，或沒加引號但不是數字／布林／null、也不以 [ { 開頭的純量（v6.2.0+）。"""
    v = _str_value(node)
    if v is None:
        return False
    if node.style in ('double', 'single'):
        return True
    return not V2_NON_STR_PLAIN_RE.match(v) and v[:1] not in ('[', '{')


def _valid_date(s):
    m = V2_DATE_RE.match(s)
    if not m:
        return False
    import datetime
    try:
        datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    hh, mm, ss, tzh, tzm = m.group(4), m.group(5), m.group(6), m.group(7), m.group(8)
    if hh is not None and (int(hh) > 23 or int(mm) > 59 or (ss is not None and int(ss) > 59)):
        return False
    if tzh is not None and (int(tzh) > 23 or (tzm is not None and int(tzm) > 59)):
        return False
    return True


def check_contract_v2(fm_lines, base, rep):
    tree, _ = MiniYaml(fm_lines).parse_node(0, 0)
    if tree is None or tree.kind != 'map':
        return
    top = tree.value

    def at(line, col):
        return base + line, col + 1

    # 工單（或任何檔）的 waiting_user
    if 'waiting_user' in top:
        node, kl, kc = top['waiting_user']
        v = _str_value(node)
        if v is None or not V2_ID_RE['awaiting_user'][0].match(v):
            rep.add(*at(kl, kc), 'waiting-user', 'waiting_user 要寫成 "U-<數字>"')

    kind = top.get('schema_kind')
    if kind is None or _str_value(kind[0]) != 'tower-state':
        return

    if 'bat_contract' in top:
        node, kl, kc = top['bat_contract']
        if node.kind != 'scalar' or node.style != 'plain' or node.value is None or not V2_INT_RE.match(node.value):
            rep.add(*at(kl, kc), 'v2-type', 'bat_contract 要是整數（不加引號）')

    if 'inbox_features' in top:  # v6.2.0+：字串清單；不認得的值不報錯
        node, kl, kc = top['inbox_features']
        if node.kind != 'seq':
            rep.add(*at(kl, kc), 'v2-features', 'inbox_features 要是字串清單（例：["recommended", "dismiss"]）')
        else:
            for item in node.value:
                if not _is_yaml_string(item):
                    rep.add(*at(item.line, item.col), 'v2-features', 'inbox_features 的項目要是字串')

    if 'next_ids' in top:
        node = top['next_ids'][0]
        if node.kind == 'map':
            for key, (rx, shown) in (('user', V2_ID_RE['awaiting_user']), ('action', V2_ID_RE['user_actions'])):
                if key in node.value:
                    sub, kl, kc = node.value[key]
                    v = _str_value(sub)
                    if v is None or not rx.match(v):
                        rep.add(*at(kl, kc), 'v2-next-id', 'next_ids.%s 要寫成 "%s"' % (key, shown))

    for name in V2_LISTS:
        if name not in top:
            continue
        node, kl, kc = top[name]
        if node.kind == 'scalar' and node.value is None and node.style == 'plain':
            continue  # 空值 = 沒有項目
        if node.kind != 'seq':
            rep.add(*at(kl, kc), 'v2-type', name + ' 要是清單')
            continue
        if len(node.value) > V2_LIMITS[name]:
            rep.warn(*at(kl, kc), 'v2-count', '%s 有 %d 筆，超過上限 %d（只警告；請先處理或移除過時項目）'
                     % (name, len(node.value), V2_LIMITS[name]))
        for item in node.value:
            if item.kind != 'map':
                rep.add(*at(item.line, item.col), 'v2-type', name + ' 的項目要是「鍵: 值」的 mapping')
                continue
            fields = item.value
            for req in V2_REQUIRED[name]:
                if req not in fields or _str_value(fields[req][0]) is None:
                    rep.add(*at(item.line, item.col), 'v2-missing', '%s 的項目缺少 %s' % (name, req))
            if 'id' in fields:
                v = _str_value(fields['id'][0])
                rx, shown = V2_ID_RE[name]
                if v is not None and not rx.match(v):
                    rep.add(*at(fields['id'][1], fields['id'][2]), 'v2-id', '%s 的 id 要符合 %s' % (name, shown))
            for key, limit in V2_LEN_LIMITS.items():
                if key not in fields:
                    continue
                sub, sl, sc = fields[key]
                if sub.kind != 'scalar':
                    rep.add(*at(sl, sc), 'v2-type', '%s 的 %s 要是字串' % (name, key))
                    continue
                v = _str_value(sub)
                if v is not None and len(v) > limit:
                    rep.add(*at(sl, sc), 'v2-length', '%s 的 %s 超過 %d 字（目前 %d 字）' % (name, key, limit, len(v)))
            codes = None  # awaiting_user 的選項代號（小寫）；None = options 不是可讀的清單
            n_opts = None  # awaiting_user 的選項項數；None = options 不是可讀的清單（v6.3.0+ 判斷 multi 用）
            if name == 'awaiting_user' and 'options' in fields:
                sub, sl, sc = fields['options']
                if sub.kind == 'scalar' and sub.value is None and sub.style == 'plain':
                    codes = set()
                    n_opts = 0
                elif sub.kind != 'seq':
                    rep.add(*at(sl, sc), 'v2-type', 'awaiting_user 的 options 要是清單（自由回答時寫 []）')
                else:
                    seen = set()
                    codes = seen
                    n_opts = len(sub.value)
                    for opt in sub.value:
                        v = _str_value(opt)
                        m = V2_OPTION_RE.match(v) if v is not None else None
                        if not m:
                            rep.add(*at(opt.line, opt.col), 'v2-option',
                                    '選項要寫成「<代號> <說明>」，代號是 1～3 個英數字')
                            continue
                        code = m.group(1).lower()
                        if code in seen:
                            rep.add(*at(opt.line, opt.col), 'v2-option', '同一筆的選項代號重複（不分大小寫）')
                        seen.add(code)
            if name == 'awaiting_user' and 'options' not in fields:
                codes = set()
                n_opts = 0
            is_multi = False  # v6.3.0+：這一筆是 multi: true
            if name == 'awaiting_user' and 'multi' in fields:  # v6.3.0+：布林（不加引號的 true／false）
                sub, sl, sc = fields['multi']
                mv = _str_value(sub)
                if sub.kind != 'scalar' or sub.style != 'plain' or mv is None or not V2_BOOL_RE.match(mv):
                    rep.add(*at(sl, sc), 'v2-multi', 'awaiting_user 的 multi 要是布林（不加引號的 true；單選題不必寫）')
                else:
                    is_multi = mv.lower() == 'true'
                    if is_multi and n_opts is not None and n_opts < 2:
                        rep.warn(*at(sl, sc), 'v2-multi-ignored',
                                 'options 少於 2 項時 multi: true 沒有意義，讀者會忽略（只提示；請拿掉 multi）')
            if name == 'awaiting_user' and 'recommended' in fields:  # v6.2.0+
                sub, sl, sc = fields['recommended']
                v = _str_value(sub)
                if not _is_yaml_string(sub):
                    rep.add(*at(sl, sc), 'v2-recommended',
                            'awaiting_user 的 recommended 要是字串（選項代號；數字代號也要加引號）')
                else:
                    # v6.3.0+：多個代號以「、」連接（只限 multi: true 的那一筆）
                    parts = v.split(IDEO_COMMA)  # 比對不去空白，同單一代號（v6.2.0）
                    if len(parts) > 1 and not is_multi:
                        rep.add(*at(sl, sc), 'v2-recommended',
                                'recommended 有多個代號時，該筆要寫 multi: true（單選題只放一個代號）')
                    if codes is None:
                        pass  # options 本身寫錯（已回報 v2-type），無從比對
                    elif not codes and n_opts == 0:
                        rep.add(*at(sl, sc), 'v2-recommended',
                                'options 是空清單（自由回答）時不寫 recommended')
                    elif any(p.lower() not in codes for p in parts):
                        rep.add(*at(sl, sc), 'v2-recommended',
                                'awaiting_user 的 recommended 有代號對不到同一筆 options 的代號（不分大小寫）；'
                                '有一個對不到就整個不寫這個鍵')
            if name == 'reminders':
                for key in ('due_at', 'last_at'):
                    if key in fields:
                        v = _str_value(fields[key][0])
                        if v is not None and not _valid_date(v):
                            rep.add(*at(fields[key][1], fields[key][2]), 'v2-date',
                                    'reminders 的 %s 不是可解析的 ISO 日期或日期時間' % key)


# ---------------------------------------------------------------- 檔案層

def split_frontmatter(text, rep, explicit):
    """回傳 (frontmatter 行, 第一行的行號) 或 None。"""
    has_bom = text.startswith(chr(0xFEFF))
    if has_bom:
        text = text[1:]
    lines = text.split('\n')
    lines = [ln[:-1] if ln.endswith('\r') else ln for ln in lines]
    if not lines or lines[0].rstrip(' \t') != '---':
        if explicit:
            rep.add(1, 1, 'no-frontmatter')
        return None
    if has_bom:
        rep.add(1, 1, 'bom')
    for idx in range(1, len(lines)):
        if lines[idx].rstrip(' \t') in ('---', '...'):
            return lines[1:idx], 2
    rep.add(1, 1, 'unclosed-frontmatter')
    return None


def yaml_check(fm_lines, line_base, rep):
    try:
        import yaml  # noqa: F401（選用）
    except ImportError:
        return False
    try:
        doc = yaml.safe_load('\n'.join(fm_lines))
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        problem = getattr(e, 'problem', None) or type(e).__name__
        if mark is not None:
            rep.add(line_base + mark.line, mark.column + 1, 'yaml-error', 'PyYAML 解析失敗：' + str(problem))
        else:
            rep.add(0, 0, 'yaml-error', 'PyYAML 解析失敗：' + str(problem))
        return True
    if doc is not None and not isinstance(doc, dict):
        rep.add(line_base, 1, 'not-mapping')
    return True


def check_file(path, explicit, use_yaml):
    rep = FileReport(path)
    try:
        with open(path, 'rb') as fh:
            raw = fh.read()
    except OSError as e:
        rep.add(0, 0, 'not-utf8', '讀檔失敗：' + type(e).__name__)
        return rep, True
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        rep.add(0, 0, 'not-utf8')
        return rep, True
    got = split_frontmatter(text, rep, explicit)
    if got is None:
        has_fm = bool(rep.items)
        return rep, has_fm
    fm_lines, base = got
    Scanner(fm_lines, base, rep).run()
    if use_yaml and not rep.items:
        yaml_check(fm_lines, base, rep)
    if not rep.items:
        try:
            check_contract_v2(fm_lines, base, rep)
        except Exception as e:  # 小型解析器看不懂時不擋檢查，只記一行警告
            rep.warn(0, 0, 'v2-skipped', '契約 v2 欄位檢查略過（' + type(e).__name__ + '）')
    return rep, True


def collect(paths, recursive):
    """回傳 ([(檔案, 是否直接指定)], [不存在的路徑])。"""
    files, missing = [], []
    for raw in paths:
        if os.path.isfile(raw):
            files.append((raw, True))
        elif os.path.isdir(raw):
            if recursive:
                for root, dirs, names in os.walk(raw):
                    dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
                    for name in sorted(names):
                        if name.lower().endswith('.md'):
                            files.append((os.path.join(root, name), False))
            else:
                for name in sorted(os.listdir(raw)):
                    p = os.path.join(raw, name)
                    if os.path.isfile(p) and name.lower().endswith('.md'):
                        files.append((p, False))
        else:
            missing.append(raw)
    return files, missing


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        description='檢查 CT 寫的 YAML frontmatter（memory-protocol.md § YAML frontmatter 字串寫法與寫入後自檢）')
    ap.add_argument('paths', nargs='+', help='檔案或目錄（目錄檢查其中的 *.md）')
    ap.add_argument('-r', '--recursive', action='store_true', help='目錄連子目錄一起檢查')
    ap.add_argument('--no-yaml', action='store_true', help='不用 PyYAML 做完整解析')
    ap.add_argument('-v', '--verbose', action='store_true', help='通過的檔也列出')
    ap.add_argument('-q', '--quiet', action='store_true', help='只印結論')
    args = ap.parse_args(argv)

    files, missing = collect(args.paths, args.recursive)
    for raw in missing:
        print('ERROR 路徑不存在：' + raw, file=sys.stderr)
    if missing:
        return 2

    n_checked = n_skipped = n_bad_files = n_items = n_warn = 0
    yaml_used = False
    for path, explicit in files:
        rep, has_fm = check_file(path, explicit, not args.no_yaml)
        if not has_fm:
            n_skipped += 1
            continue
        n_checked += 1
        n_warn += len(rep.warnings)
        if rep.items or rep.warnings:
            if rep.items:
                n_bad_files += 1
                n_items += len(rep.items)
            if not args.quiet:
                print('## ' + path)
                for level, entries in (('FAIL', rep.items), ('WARN', rep.warnings)):
                    for line, col, code, msg in entries:
                        where = '第 %d 行第 %d 欄' % (line, col) if line else '（整檔）'
                        print('- %s %s %s：%s' % (level, code, where, msg))
        elif args.verbose and not args.quiet:
            print('## ' + path)
            print('- PASS')
    if not args.no_yaml:
        try:
            import yaml  # noqa: F401
            yaml_used = True
        except ImportError:
            yaml_used = False
    how = '另以 PyYAML 完整解析' if yaml_used else '只用標準函式庫檢查'
    if n_warn:
        how += '；警告 %d 處' % n_warn
    if n_bad_files:
        print('結論：FAIL（%d 檔有問題、共 %d 處；檢查 %d 檔、略過沒有 frontmatter 的 %d 檔；%s）'
              % (n_bad_files, n_items, n_checked, n_skipped, how))
        return 1
    print('結論：PASS（檢查 %d 檔、略過沒有 frontmatter 的 %d 檔；%s）' % (n_checked, n_skipped, how))
    return 0


if __name__ == '__main__':
    sys.exit(main())
