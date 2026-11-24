#!/usr/bin/env python3
"""check-frontmatter.py — CT 寫的 YAML frontmatter 寫入後自檢（T0549；v6.0.1 起隨 control-tower 發行）。

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

輸出：只印檔名、行號、欄號與問題類型，不印檔案原文。
exit 0 = 全部通過；1 = 有問題；2 = 用法錯誤或路徑不存在。

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

    def add(self, line, col, code, msg=None):
        self.items.append((line, col, code, msg or PROBLEM_TEXT.get(code, code)))


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

    n_checked = n_skipped = n_bad_files = n_items = 0
    yaml_used = False
    for path, explicit in files:
        rep, has_fm = check_file(path, explicit, not args.no_yaml)
        if not has_fm:
            n_skipped += 1
            continue
        n_checked += 1
        if rep.items:
            n_bad_files += 1
            n_items += len(rep.items)
            if not args.quiet:
                print('## ' + path)
                for line, col, code, msg in rep.items:
                    where = '第 %d 行第 %d 欄' % (line, col) if line else '（整檔）'
                    print('- FAIL %s %s：%s' % (code, where, msg))
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
    if n_bad_files:
        print('結論：FAIL（%d 檔有問題、共 %d 處；檢查 %d 檔、略過沒有 frontmatter 的 %d 檔；%s）'
              % (n_bad_files, n_items, n_checked, n_skipped, how))
        return 1
    print('結論：PASS（檢查 %d 檔、略過沒有 frontmatter 的 %d 檔；%s）' % (n_checked, n_skipped, how))
    return 0


if __name__ == '__main__':
    sys.exit(main())
