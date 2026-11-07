#!/usr/bin/env python3
"""validate-adapter.py — 方法論 adapter 描述檔檢查（T0303；v6.0.0-pre.1 預覽起隨 control-tower 發行）。

檢查規則的權威是 control-tower/references/methodology-adapters.md § 描述檔格式（欄位表、routing 入口欄位、
§ 新 adapter 的最小檢查）。本腳本只做其中「可機器檢查」的部分，規則有變以權威檔為準，再改這裡。

用法：
  uv run --no-project --with pyyaml python <control-tower>/scripts/validate-adapter.py <路徑> [<路徑> ...]
  python <control-tower>/scripts/validate-adapter.py <路徑> ...      # 環境已有 PyYAML 時

  <路徑> 可以是描述檔（內建 adapters/<id>.yaml、外部或專案本地的 adapter.yaml），
  或含 adapter.yaml 的目錄（例：ct-adapter-pstack/）。

  --source auto|builtin|external-skill|project-local
                 判斷 id 對應規則用的來源（預設 auto：依路徑判斷，見下）
  --quiet        只印每個檔的總結論

依賴：Python 3.8+ 與 PyYAML（只用 yaml.safe_load）。沒有 PyYAML 時印出取得方式並以 exit 2 結束；
不自帶簡化版 YAML 解析器，因為描述檔用到 flow mapping、多層巢狀與註解，簡化解析會誤判。

來源判斷（auto，對應權威檔 § 描述檔格式 的來源表）：
  <dir>/ct-adapter-<x>/adapter.yaml        → 外部 skill，id 應為 <x>
  <dir>/_adapters/<x>/adapter.yaml         → 專案本地，id 應為 <x>
  <dir>/<x>.yaml（檔名不是 adapter.yaml）  → CT 內建，id 應為 <x>
  其他                                     → 無法判斷，id 對應項 FAIL（可用 --source 指定）
  methodology_adapters_path 指到的目錄與 _adapters/ 同結構（<path>/<x>/adapter.yaml），目錄名不是 _adapters
  時 auto 認不得，用 --source project-local 檢查（權威檔 § 散布與搜尋順序）

輸出：每個檔逐項 PASS／WARN／FAIL，最後一行總結論。全部檔案沒有 FAIL → exit 0；任一 FAIL → exit 1；
用法錯誤、檔案不存在或缺 PyYAML → exit 2。WARN 不影響 exit code。

可機器檢查、本腳本會查的：
  M1  YAML 能解析，頂層是 mapping
  M2  schema = ct-methodology-adapter/v1
  M3  22 個頂層欄位都在，沒有欄位表以外的頂層欄位
  M4  id 格式 [a-z0-9-] 且符合來源表；不是保留字 auto／none／inherit；maintainer.kind 與來源一致
  M5  adapter_status、maintainer 子欄位
  M6  upstream 有 name、url（http/https）、license、version_range、tested_version、version_source；
      tested_version 落在 version_range（只認得 >=、>、<=、<、= 組合；認不得就 WARN）
  M7  runtimes 非空且只含 claude-code／codex；worker.invoke 對每個 runtime 都有寫法
  M8  detection：strategy、probes（每個有 id、kind ∈ skill/plugin/file、非空 search）、min_version、
      on_below_min、on_missing；skill_root 只用於 kind: plugin，是非空相對路徑、不含 ..；kind: plugin 寫了
      required_files 就要有 skill_root；選填 runtime（v6.0.0-beta.8+）是一個 runtime 名（claude-code／codex）且在 runtimes 內；
      session.hooks 非空時必須有 detection.hook_probe（mapping）；hook_probe 有 runtime 名
      （claude-code／codex）的鍵 = 依 runtime 分開：鍵要在 runtimes 內、值是 mapping，每個有 hook 的 runtime
      （session.hooks[].runtime，沒寫 = runtimes 全部）都要有鍵
  M9  capabilities 剛好 5 層，值 ∈ full/partial/none
  M10 routing：7 種必填需求類型都在（值可為 {} = 明確缺席）；需求類型與層名合法；每個入口有 workflow；
      入口欄位只用 routing 入口欄位表的鍵；入口指向 capabilities: none 的層 → WARN
  M11 workorder、worker 子欄位；worker.lifecycle_owner = ct-exec、run_mode = inline；
      asks_user、ct_overrides 是清單（可空），ct_overrides 每項有 behavior、ct_rule
  M12 status_mapping：rules 涵蓋 DONE／PARTIAL／BLOCKED／FAILED，ct_status 值合法；required_report 非空；
      至少一條 DONE 規則或 status_mapping 說明提到工單閘門（啟發式，沒有 → WARN）
  M13 artifacts.writes、handoff（produces／consumes 的 layer 合法、有 kind；writeback 有 target、by）、
      tracker、retired_names（每項有 replacement、since、kind；允許一個字串 note）、degradation 子欄位
  M14 session：hooks（每項有 event、matcher、effect、measured、off_switch、ct_guard；選填 runtime ⊂ runtimes、
      entry_skills 是非空字串清單、trigger_summary 非空字串）、name_collisions、subagents.writes 是布林、
      subagents.ct_rule、always_on_tokens（整數或 unknown）、選填 skill_patterns 是非空字串清單；vocabulary、links 是 mapping。
      邊界段範本要用的值缺了 → WARN：沒有 skill_patterns；有 hook 但沒有 entry_skills 或 trigger_summary
  M15 外部 skill 目錄有 SKILL.md、README.md；專案本地目錄有 README.md（缺 → WARN：描述檔本身仍可讀）

不可機器檢查、要人看的（權威檔 § 新 adapter 的最小檢查 其餘部分）：
  - 描述檔與 README 沒有第三方 skill 原文（腳本無從比對上游全文；人工抽查上游 SKILL.md 特徵句）
  - detection 的 probe 在真實機器上真的能判斷「有／沒有」（腳本只查欄位齊全）
  - status_mapping 確實寫明「方法論 done ≠ 工單 DONE」（M12 只做關鍵字啟發）
  - session.hooks、子代理、asks_user、git 副作用、artifacts.writes 宣告得「完整」（腳本只查欄位存在）
  - 有 hook 的方法論附隔離試裝紀錄（注入內容、開關、主環境前後比對）
  - routing 的 workflow 名稱在上游真的存在、retired_names 的替代名正確

所有輸入只讀，不寫任何檔。
"""
import argparse
import os
import re
import sys

SCHEMA = 'ct-methodology-adapter/v1'

TOP_FIELDS = [
    'schema', 'id', 'display_name', 'adapter_version', 'adapter_status', 'maintainer', 'upstream',
    'runtimes', 'detection', 'capabilities', 'routing', 'workorder', 'worker', 'status_mapping',
    'artifacts', 'handoff', 'tracker', 'retired_names', 'degradation', 'session', 'vocabulary', 'links',
]
LAYERS = ['planning', 'execution', 'review', 'verification', 'delivery']
REQUEST_KINDS_REQUIRED = ['feature', 'bugfix', 'refactor', 'research', 'review', 'test', 'small-change']
REQUEST_KINDS = REQUEST_KINDS_REQUIRED + ['delivery']
ENTRY_FIELDS = {'workflow', 'alternatives', 'detail', 'agent', 'reference', 'note', 'unattended',
                'fallback', 'requires_module', 'ct_policy'}
CT_STATUSES = ['DONE', 'PARTIAL', 'BLOCKED', 'FAILED']
ADAPTER_STATUSES = {'prototype', 'stable', 'deprecated'}
MAINTAINER_KINDS = {'ct-builtin', 'external-skill', 'project-local'}
CAPABILITY_VALUES = {'full', 'partial', 'none'}
RUNTIMES = {'claude-code', 'codex'}
PROBE_KINDS = {'skill', 'plugin', 'file'}
ID_RE = re.compile(r'^[a-z0-9-]+$')
RESERVED_IDS = {'auto', 'none', 'inherit'}     # 設定值的關鍵字（權威檔 § 描述檔格式 › 欄位表 id、§ 抽換）
SOURCE_KIND = {'builtin': 'ct-builtin', 'external-skill': 'external-skill', 'project-local': 'project-local'}


class Report:
    def __init__(self, path):
        self.path = path
        self.items = []  # (level, code, message)

    def add(self, level, code, msg):
        self.items.append((level, code, msg))

    def ok(self, code, msg):
        self.add('PASS', code, msg)

    def warn(self, code, msg):
        self.add('WARN', code, msg)

    def fail(self, code, msg):
        self.add('FAIL', code, msg)

    @property
    def failed(self):
        return any(lv == 'FAIL' for lv, _, _ in self.items)

    @property
    def warned(self):
        return any(lv == 'WARN' for lv, _, _ in self.items)


# ---------------------------------------------------------------- 小工具

def nonempty_str(v):
    return isinstance(v, (str, int, float)) and not isinstance(v, bool) and str(v).strip() != ''


def need_keys(rep, code, obj, where, keys):
    """obj 必須是 mapping 且含 keys；回傳缺少的鍵。"""
    if not isinstance(obj, dict):
        rep.fail(code, f'{where} 應為 mapping，實際是 {type(obj).__name__}')
        return list(keys)
    missing = [k for k in keys if k not in obj]
    if missing:
        rep.fail(code, f'{where} 缺 {", ".join(missing)}')
    return missing


def str_list(v):
    return isinstance(v, list) and len(v) > 0 and all(nonempty_str(x) for x in v)


def is_list(rep, code, obj, where, nonempty=False):
    if not isinstance(obj, list):
        rep.fail(code, f'{where} 應為清單，實際是 {type(obj).__name__}')
        return False
    if nonempty and not obj:
        rep.fail(code, f'{where} 不可為空清單')
        return False
    return True


def parse_version(s):
    parts = str(s).strip().lstrip('v').split('-')[0].split('.')
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None


def in_range(version, spec):
    """回傳 True／False；認不得 spec 或版本時回傳 None。"""
    v = parse_version(version)
    if v is None:
        return None
    width = max(len(v), 3)
    pad = lambda t: t + (0,) * (width - len(t))
    ops = re.findall(r'(>=|<=|>|<|=)\s*([0-9][0-9A-Za-z.\-]*)', str(spec))
    if not ops or re.sub(r'(>=|<=|>|<|=)\s*[0-9][0-9A-Za-z.\-]*|\s', '', str(spec)):
        return None
    for op, raw in ops:
        b = parse_version(raw)
        if b is None:
            return None
        a, b = pad(v), pad(b)
        if not {'>=': a >= b, '<=': a <= b, '>': a > b, '<': a < b, '=': a == b}[op]:
            return False
    return True


# ---------------------------------------------------------------- 來源與 id

def resolve_target(path):
    """目錄 → 目錄內的 adapter.yaml。回傳 (檔案路徑, 錯誤訊息)。"""
    if os.path.isdir(path):
        cand = os.path.join(path, 'adapter.yaml')
        if os.path.isfile(cand):
            return os.path.normpath(cand), None
        return None, f'目錄內沒有 adapter.yaml：{path}'
    if os.path.isfile(path):
        return os.path.normpath(path), None
    return None, f'找不到檔案：{path}'


def detect_source(fpath):
    """回傳 (source, expected_id)；認不得時 (None, None)。"""
    full = os.path.abspath(fpath)
    base = os.path.basename(full)
    parent = os.path.basename(os.path.dirname(full))
    grand = os.path.basename(os.path.dirname(os.path.dirname(full)))
    if base == 'adapter.yaml':
        if parent.startswith('ct-adapter-') and len(parent) > len('ct-adapter-'):
            return 'external-skill', parent[len('ct-adapter-'):]
        if grand == '_adapters':
            return 'project-local', parent
        return None, None
    stem, ext = os.path.splitext(base)
    if ext in ('.yaml', '.yml'):
        return 'builtin', stem
    return None, None


def expected_id_for(fpath, source):
    full = os.path.abspath(fpath)
    base = os.path.basename(full)
    parent = os.path.basename(os.path.dirname(full))
    if source == 'builtin':
        return os.path.splitext(base)[0]
    if source == 'external-skill':
        return parent[len('ct-adapter-'):] if parent.startswith('ct-adapter-') else None
    if source == 'project-local':
        return parent
    return None


# ---------------------------------------------------------------- 檢查

def check(doc, fpath, source_opt):
    rep = Report(fpath)

    # M1
    if not isinstance(doc, dict):
        rep.fail('M1', f'頂層應為 mapping，實際是 {type(doc).__name__}')
        return rep
    rep.ok('M1', 'YAML 解析通過，頂層是 mapping')

    # M2
    if doc.get('schema') == SCHEMA:
        rep.ok('M2', f'schema = {SCHEMA}')
    else:
        rep.fail('M2', f'schema 應為 {SCHEMA}，實際是 {doc.get("schema")!r}')

    # M3
    missing = [k for k in TOP_FIELDS if k not in doc]
    extra = [k for k in doc if k not in TOP_FIELDS]
    if missing:
        rep.fail('M3', f'缺頂層欄位（{len(missing)}）：{", ".join(missing)}')
    if extra:
        rep.fail('M3', f'欄位表以外的頂層欄位：{", ".join(map(str, extra))}')
    if not missing and not extra:
        rep.ok('M3', f'{len(TOP_FIELDS)} 個頂層欄位齊全，沒有多餘欄位')

    # M4
    if source_opt == 'auto':
        source, expected = detect_source(fpath)
    else:
        source, expected = source_opt, expected_id_for(fpath, source_opt)
    aid = doc.get('id')
    if not isinstance(aid, str) or not ID_RE.match(aid):
        rep.fail('M4', f'id 應為 [a-z0-9-]，實際是 {aid!r}')
    elif aid in RESERVED_IDS:
        rep.fail('M4', f'id {aid!r} 是保留字（auto／none／inherit 是設定值的關鍵字），不能當 adapter id')
    elif source is None or expected is None:
        rep.fail('M4', '無法從路徑判斷來源（內建 <id>.yaml／ct-adapter-<id>/adapter.yaml／_adapters/<id>/adapter.yaml），'
                       '請改放到對應位置或用 --source 指定（methodology_adapters_path 的目錄用 --source project-local）')
    elif aid != expected:
        rep.fail('M4', f'id 與來源表不符：來源 {source} 應為 {expected!r}，實際是 {aid!r}')
    else:
        rep.ok('M4', f'id = {aid!r}，符合來源 {source}')
    mkind = doc.get('maintainer', {}).get('kind') if isinstance(doc.get('maintainer'), dict) else None
    if source in SOURCE_KIND and mkind in MAINTAINER_KINDS and mkind != SOURCE_KIND[source]:
        rep.fail('M4', f'maintainer.kind = {mkind!r} 與來源 {source} 不一致（應為 {SOURCE_KIND[source]!r}）')

    # M5
    errs = len(rep.items)
    for k in ('display_name', 'adapter_version'):
        if k in doc and not nonempty_str(doc[k]):
            rep.fail('M5', f'{k} 不可為空')
    if 'adapter_status' in doc and doc['adapter_status'] not in ADAPTER_STATUSES:
        rep.fail('M5', f'adapter_status 應為 {"/".join(sorted(ADAPTER_STATUSES))}，實際是 {doc["adapter_status"]!r}')
    if 'maintainer' in doc and not need_keys(rep, 'M5', doc['maintainer'], 'maintainer', ['kind', 'owner', 'sync_rule']):
        if doc['maintainer']['kind'] not in MAINTAINER_KINDS:
            rep.fail('M5', f'maintainer.kind 應為 {"/".join(sorted(MAINTAINER_KINDS))}，實際是 {doc["maintainer"]["kind"]!r}')
    if len(rep.items) == errs:
        rep.ok('M5', 'display_name、adapter_version、adapter_status、maintainer 合法')

    # M6
    errs = len(rep.items)
    up = doc.get('upstream')
    if 'upstream' in doc and not need_keys(rep, 'M6', up, 'upstream',
                                           ['name', 'url', 'license', 'version_range', 'tested_version', 'version_source']):
        for k in ('name', 'license', 'version_range', 'tested_version', 'version_source'):
            if not nonempty_str(up[k]):
                rep.fail('M6', f'upstream.{k} 不可為空')
        if not (isinstance(up['url'], str) and re.match(r'^https?://\S+$', up['url'])):
            rep.fail('M6', f'upstream.url 應為 http(s) 網址，實際是 {up["url"]!r}')
        r = in_range(up['tested_version'], up['version_range'])
        if r is False:
            rep.fail('M6', f'tested_version {up["tested_version"]} 不在 version_range {up["version_range"]!r} 內')
        elif r is None:
            rep.warn('M6', f'認不得 version_range {up["version_range"]!r} 或 tested_version，沒有比對範圍')
    if len([i for i in rep.items[errs:] if i[0] == 'FAIL']) == 0 and 'upstream' in doc:
        rep.ok('M6', 'upstream 有 URL、授權、tested_version 等必填子欄位')

    # M7
    errs = len(rep.items)
    runtimes = doc.get('runtimes')
    if 'runtimes' in doc and is_list(rep, 'M7', runtimes, 'runtimes', nonempty=True):
        bad = [r for r in runtimes if r not in RUNTIMES]
        if bad:
            rep.fail('M7', f'runtimes 含未知值：{", ".join(map(str, bad))}（只認 {"/".join(sorted(RUNTIMES))}）')
        invoke = doc.get('worker', {}).get('invoke') if isinstance(doc.get('worker'), dict) else None
        if not isinstance(invoke, dict):
            rep.fail('M7', 'worker.invoke 應為 mapping（每個 runtime 一個寫法）')
        else:
            lack = [r for r in runtimes if r in RUNTIMES and not nonempty_str(invoke.get(r))]
            if lack:
                rep.fail('M7', f'worker.invoke 缺 runtime 寫法：{", ".join(lack)}')
    if len(rep.items) == errs and 'runtimes' in doc:
        rep.ok('M7', f'runtimes {runtimes} 都有 invoke 寫法')

    # M8
    errs = len(rep.items)
    det = doc.get('detection')
    if 'detection' in doc and not need_keys(rep, 'M8', det, 'detection',
                                            ['strategy', 'probes', 'min_version', 'on_below_min', 'on_missing']):
        if det['strategy'] not in ('any', 'all'):
            rep.fail('M8', f'detection.strategy 應為 any/all，實際是 {det["strategy"]!r}')
        if is_list(rep, 'M8', det['probes'], 'detection.probes', nonempty=True):
            for i, p in enumerate(det['probes']):
                where = f'detection.probes[{i}]'
                if need_keys(rep, 'M8', p, where, ['id', 'kind', 'search']):
                    continue
                if p['kind'] not in PROBE_KINDS:
                    rep.fail('M8', f'{where}.kind 應為 {"/".join(sorted(PROBE_KINDS))}，實際是 {p["kind"]!r}')
                is_list(rep, 'M8', p['search'], f'{where}.search', nonempty=True)
                # skill_root（權威檔 § 描述檔格式 › probe 怎麼解析 skill 根目錄，v6.0.0-beta.6+）
                if 'skill_root' in p:
                    sr = p['skill_root']
                    if p['kind'] != 'plugin':
                        rep.fail('M8', f'{where}.skill_root 只用於 kind: plugin，實際 kind 是 {p["kind"]!r}')
                    elif (not isinstance(sr, str) or not sr.strip() or sr.startswith(('/', '\\', '~', '$'))
                          or re.match(r'^[A-Za-z]:', sr) or '..' in re.split(r'[\\/]', sr)):
                        rep.fail('M8', f'{where}.skill_root 應為非空相對路徑、不含 ..，實際是 {sr!r}')
                if p['kind'] == 'plugin' and p.get('required_files') and 'skill_root' not in p:
                    rep.fail('M8', f'{where} 是 kind: plugin 且有 required_files，但沒有 skill_root（required_files 相對於 skill 根目錄）')
                # runtime（選填；權威檔 § 描述檔格式 › probe 怎麼解析 skill 根目錄 第 1 點，v6.0.0-beta.8+）
                if 'runtime' in p:
                    pr = p['runtime']
                    if not isinstance(pr, str) or pr not in RUNTIMES:
                        rep.fail('M8', f'{where}.runtime 應為一個 runtime 名（{"/".join(sorted(RUNTIMES))}），實際是 {pr!r}')
                    elif isinstance(runtimes, list) and pr not in runtimes:
                        rep.fail('M8', f'{where}.runtime：runtime {pr} 不在 runtimes 內')
    sess = doc.get('session')
    hooks = sess.get('hooks') if isinstance(sess, dict) else None
    if isinstance(hooks, list) and hooks and isinstance(det, dict) and 'hook_probe' not in det:
        rep.fail('M8', f'session.hooks 有 {len(hooks)} 個 hook，但 detection 沒有 hook_probe')
    hp = det.get('hook_probe') if isinstance(det, dict) else None
    if isinstance(det, dict) and 'hook_probe' in det:
        if not isinstance(hp, dict):
            rep.fail('M8', f'detection.hook_probe 應為 mapping，實際是 {type(hp).__name__}')
        else:
            rt_keys = [k for k in hp if k in RUNTIMES]
            if rt_keys:   # 依 runtime 分開寫（權威檔欄位表 detection）
                declared = runtimes if isinstance(runtimes, list) else []
                for k in rt_keys:
                    if k not in declared:
                        rep.fail('M8', f'detection.hook_probe.{k}：runtime {k} 不在 runtimes 內')
                    if not isinstance(hp[k], dict):
                        rep.fail('M8', f'detection.hook_probe.{k} 應為 mapping')
                need = set()
                for h in hooks if isinstance(hooks, list) else []:
                    hr = h.get('runtime') if isinstance(h, dict) else None
                    need.update(hr if isinstance(hr, list) else declared)
                lack = sorted(r for r in need if r in RUNTIMES and r not in hp)
                if lack:
                    rep.fail('M8', f'detection.hook_probe 依 runtime 分開寫，但缺有 hook 的 runtime：{", ".join(lack)}')
    if len(rep.items) == errs and 'detection' in doc:
        n = len(det['probes'])
        per_rt = [k for k in hp if k in RUNTIMES] if isinstance(hp, dict) else []
        p_rt = [p['runtime'] for p in det['probes'] if isinstance(p, dict) and 'runtime' in p]
        rep.ok('M8', f'detection 有 {n} 個 probe'
               + (f'（{len(p_rt)} 個標 runtime：' + '、'.join(f'{r} {p_rt.count(r)}' for r in sorted(set(p_rt))) + '）' if p_rt else '')
               + ('，有 hook_probe' if 'hook_probe' in det else '')
               + (f'（依 runtime：{", ".join(per_rt)}）' if per_rt else ''))

    # M9
    errs = len(rep.items)
    caps = doc.get('capabilities')
    if 'capabilities' in doc and not need_keys(rep, 'M9', caps, 'capabilities', LAYERS):
        extra_l = [k for k in caps if k not in LAYERS]
        if extra_l:
            rep.fail('M9', f'capabilities 有不合法的層：{", ".join(map(str, extra_l))}（只有 {"/".join(LAYERS)}；編排屬於 CT）')
        bad = [f'{k}={caps[k]!r}' for k in LAYERS if caps[k] not in CAPABILITY_VALUES]
        if bad:
            rep.fail('M9', f'capabilities 值應為 full/partial/none：{", ".join(bad)}')
    if len(rep.items) == errs and 'capabilities' in doc:
        rep.ok('M9', '5 層都有值：' + ', '.join(f'{k}={caps[k]}' for k in LAYERS))

    # M10
    errs = len(rep.items)
    routing = doc.get('routing')
    if 'routing' in doc:
        if not isinstance(routing, dict):
            rep.fail('M10', 'routing 應為 mapping')
        else:
            miss = [k for k in REQUEST_KINDS_REQUIRED if k not in routing]
            if miss:
                rep.fail('M10', f'routing 缺必填需求類型：{", ".join(miss)}（不處理就寫 {{}} 表示明確缺席）')
            for kind, layers in routing.items():
                if kind not in REQUEST_KINDS:
                    rep.fail('M10', f'routing 有不合法的需求類型：{kind!r}')
                    continue
                if layers is None or layers == {}:
                    continue
                if not isinstance(layers, dict):
                    rep.fail('M10', f'routing.{kind} 應為 mapping（層 → 入口）')
                    continue
                for layer, entry in layers.items():
                    where = f'routing.{kind}.{layer}'
                    if layer not in LAYERS:
                        rep.fail('M10', f'{where}：不合法的層名（只有 {"/".join(LAYERS)}）')
                        continue
                    if not isinstance(entry, dict):
                        rep.fail('M10', f'{where} 應為 mapping')
                        continue
                    if not nonempty_str(entry.get('workflow')):
                        rep.fail('M10', f'{where} 缺 workflow（不走方法論就寫 none）')
                    unk = [k for k in entry if k not in ENTRY_FIELDS]
                    if unk:
                        rep.fail('M10', f'{where} 有 routing 入口欄位表以外的鍵：{", ".join(map(str, unk))}')
                    if isinstance(caps, dict) and caps.get(layer) == 'none':
                        rep.warn('M10', f'{where} 有入口，但 capabilities.{layer} = none')
    if len([i for i in rep.items[errs:] if i[0] == 'FAIL']) == 0 and isinstance(routing, dict):
        rep.ok('M10', f'routing 涵蓋 7 種必填需求類型；共 {len(routing)} 種類型、層名與入口欄位合法')

    # M11
    errs = len(rep.items)
    if 'workorder' in doc:
        need_keys(rep, 'M11', doc['workorder'], 'workorder', ['section_heading', 'annotations', 'required_when', 'legacy'])
        wo = doc['workorder']
        if isinstance(wo, dict) and 'required_when' in wo:
            if is_list(rep, 'M11', wo['required_when'], 'workorder.required_when'):
                for i, rw in enumerate(wo['required_when']):
                    need_keys(rep, 'M11', rw, f'workorder.required_when[{i}]', ['workflow', 'section'])
    if 'worker' in doc:
        w = doc['worker']
        if not need_keys(rep, 'M11', w, 'worker',
                         ['lifecycle_owner', 'run_mode', 'invoke', 'requires', 'asks_user', 'ct_overrides']):
            if w['lifecycle_owner'] != 'ct-exec':
                rep.fail('M11', f'worker.lifecycle_owner 固定 ct-exec，實際是 {w["lifecycle_owner"]!r}')
            if w['run_mode'] != 'inline':
                rep.fail('M11', f'worker.run_mode 應為 inline，實際是 {w["run_mode"]!r}')
            is_list(rep, 'M11', w['asks_user'], 'worker.asks_user')
            if is_list(rep, 'M11', w['ct_overrides'], 'worker.ct_overrides'):
                for i, o in enumerate(w['ct_overrides']):
                    need_keys(rep, 'M11', o, f'worker.ct_overrides[{i}]', ['behavior', 'ct_rule'])
    if len(rep.items) == errs and 'worker' in doc and 'workorder' in doc:
        rep.ok('M11', 'workorder、worker 子欄位齊全；lifecycle_owner = ct-exec、run_mode = inline')

    # M12
    errs = len(rep.items)
    sm = doc.get('status_mapping')
    if 'status_mapping' in doc and not need_keys(rep, 'M12', sm, 'status_mapping', ['source', 'rules', 'required_report']):
        seen = set()
        gate_hint = False
        if is_list(rep, 'M12', sm['rules'], 'status_mapping.rules', nonempty=True):
            for i, r in enumerate(sm['rules']):
                if need_keys(rep, 'M12', r, f'status_mapping.rules[{i}]', ['when', 'ct_status']):
                    continue
                if r['ct_status'] not in CT_STATUSES:
                    rep.fail('M12', f'status_mapping.rules[{i}].ct_status 應為 {"/".join(CT_STATUSES)}，實際是 {r["ct_status"]!r}')
                    continue
                seen.add(r['ct_status'])
                if r['ct_status'] == 'DONE' and re.search(r'閘門|gate', str(r['when']), re.I):
                    gate_hint = True
            lack = [s for s in CT_STATUSES if s not in seen]
            if lack:
                rep.fail('M12', f'status_mapping.rules 沒有涵蓋：{", ".join(lack)}')
        is_list(rep, 'M12', sm['required_report'], 'status_mapping.required_report', nonempty=True)
        if not gate_hint and not re.search(r'閘門|gate', f'{sm.get("source", "")} {sm.get("note", "")}', re.I):
            rep.warn('M12', '找不到「工單閘門」字樣：請人工確認 status_mapping 寫明「方法論 done ≠ 工單 DONE」（啟發式）')
    if len([i for i in rep.items[errs:] if i[0] == 'FAIL']) == 0 and 'status_mapping' in doc:
        rep.ok('M12', 'status_mapping 涵蓋 DONE／PARTIAL／BLOCKED／FAILED，required_report 非空')

    # M13
    errs = len(rep.items)
    if 'artifacts' in doc and not need_keys(rep, 'M13', doc['artifacts'], 'artifacts', ['writes']):
        is_list(rep, 'M13', doc['artifacts']['writes'], 'artifacts.writes')
    ho = doc.get('handoff')
    if 'handoff' in doc and not need_keys(rep, 'M13', ho, 'handoff', ['produces', 'consumes', 'writeback']):
        for side in ('produces', 'consumes'):
            if is_list(rep, 'M13', ho[side], f'handoff.{side}'):
                for i, h in enumerate(ho[side]):
                    if need_keys(rep, 'M13', h, f'handoff.{side}[{i}]', ['layer', 'kind']):
                        continue
                    if h['layer'] not in LAYERS:
                        rep.fail('M13', f'handoff.{side}[{i}].layer 不合法：{h["layer"]!r}')
        need_keys(rep, 'M13', ho['writeback'], 'handoff.writeback', ['target', 'by'])
    if 'tracker' in doc and not isinstance(doc['tracker'], dict):
        rep.fail('M13', 'tracker 應為 mapping（沒有就寫 {}）')
    rn = doc.get('retired_names')
    if 'retired_names' in doc:
        if not isinstance(rn, dict):
            rep.fail('M13', 'retired_names 應為 mapping（沒有就寫 {}）')
        else:
            for name, v in rn.items():
                if name == 'note' and isinstance(v, str):
                    continue
                need_keys(rep, 'M13', v, f'retired_names.{name}', ['replacement', 'since', 'kind'])
    if 'degradation' in doc:
        need_keys(rep, 'M13', doc['degradation'], 'degradation', ['not_installed', 'below_min_version', 'workflow_missing'])
    if len(rep.items) == errs:
        rep.ok('M13', 'artifacts、handoff、tracker、retired_names、degradation 結構合法')

    # M14
    errs = len(rep.items)
    if 'session' in doc and not need_keys(rep, 'M14', sess, 'session',
                                          ['hooks', 'name_collisions', 'subagents', 'always_on_tokens']):
        if is_list(rep, 'M14', sess['hooks'], 'session.hooks'):
            for i, h in enumerate(sess['hooks']):
                where = f'session.hooks[{i}]'
                need_keys(rep, 'M14', h, where, ['event', 'matcher', 'effect', 'measured', 'off_switch', 'ct_guard'])
                if not isinstance(h, dict):
                    continue
                if 'runtime' in h:
                    if not str_list(h['runtime']):
                        rep.fail('M14', f'{where}.runtime 應為非空字串清單')
                    elif isinstance(runtimes, list) and any(r not in runtimes for r in h['runtime']):
                        rep.fail('M14', f'{where}.runtime 含 runtimes 以外的值：{h["runtime"]}')
                if 'entry_skills' in h and not str_list(h['entry_skills']):
                    rep.fail('M14', f'{where}.entry_skills 應為非空字串清單')
                if 'trigger_summary' in h and not nonempty_str(h['trigger_summary']):
                    rep.fail('M14', f'{where}.trigger_summary 不可為空')
                lack = [k for k in ('entry_skills', 'trigger_summary') if k not in h]
                if lack:
                    rep.warn('M14', f'{where} 沒有 {"、".join(lack)}（邊界段範本要用；權威檔欄位表 session）')
        if 'skill_patterns' in sess:
            if not str_list(sess['skill_patterns']):
                rep.fail('M14', 'session.skill_patterns 應為非空字串清單')
        else:
            rep.warn('M14', '沒有 session.skill_patterns（邊界段範本的 <skill 樣式> 要用；權威檔欄位表 session）')
        is_list(rep, 'M14', sess['name_collisions'], 'session.name_collisions')
        if not need_keys(rep, 'M14', sess['subagents'], 'session.subagents', ['writes', 'ct_rule']):
            if not isinstance(sess['subagents']['writes'], bool):
                rep.fail('M14', f'session.subagents.writes 應為 true/false，實際是 {sess["subagents"]["writes"]!r}')
        tok = sess['always_on_tokens']
        if not ((isinstance(tok, int) and not isinstance(tok, bool) and tok >= 0) or tok == 'unknown'):
            rep.fail('M14', f'session.always_on_tokens 應為非負整數或 unknown，實際是 {tok!r}')
    for k in ('vocabulary', 'links'):
        if k in doc and not isinstance(doc[k], dict):
            rep.fail('M14', f'{k} 應為 mapping')
    if len([i for i in rep.items[errs:] if i[0] == 'FAIL']) == 0:
        rep.ok('M14', 'session（hooks、name_collisions、subagents.writes、always_on_tokens）、vocabulary、links 合法')

    # M15
    if source in ('external-skill', 'project-local'):
        d = os.path.dirname(os.path.abspath(fpath))
        want = ['SKILL.md', 'README.md'] if source == 'external-skill' else ['README.md']
        lack = [f for f in want if not os.path.isfile(os.path.join(d, f))]
        if lack:
            rep.warn('M15', f'{source} 目錄缺 {", ".join(lack)}（描述檔本身仍可讀；發行前要補）')
        else:
            rep.ok('M15', f'{source} 目錄有 {", ".join(want)}')

    return rep


# ---------------------------------------------------------------- 主程式

def main(argv=None):
    ap = argparse.ArgumentParser(description='檢查 CT 方法論 adapter 描述檔（methodology-adapters.md § 新 adapter 的最小檢查）')
    ap.add_argument('paths', nargs='+', help='描述檔或含 adapter.yaml 的目錄')
    ap.add_argument('--source', choices=['auto', 'builtin', 'external-skill', 'project-local'], default='auto')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args(argv)

    try:
        import yaml
    except ImportError:
        print('ERROR 需要 PyYAML。用 `uv run --no-project --with pyyaml python validate-adapter.py <路徑>` 執行，'
              '或先 `pip install pyyaml`。', file=sys.stderr)
        return 2

    any_fail = False
    usage_err = False
    for raw in args.paths:
        fpath, err = resolve_target(raw)
        if err:
            print(f'ERROR {err}', file=sys.stderr)
            usage_err = True
            continue
        try:
            with open(fpath, encoding='utf-8') as fh:
                doc = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            rep = Report(fpath)
            rep.fail('M1', 'YAML 解析失敗：' + str(e).replace('\n', ' '))
        else:
            rep = check(doc, fpath, args.source)
        any_fail = any_fail or rep.failed
        verdict = 'FAIL' if rep.failed else 'PASS'
        print(f'## {fpath}')
        if not args.quiet:
            for level, code, msg in rep.items:
                print(f'- {level} {code} {msg}')
        n_fail = sum(1 for lv, _, _ in rep.items if lv == 'FAIL')
        n_warn = sum(1 for lv, _, _ in rep.items if lv == 'WARN')
        print(f'結論：{verdict}（FAIL {n_fail}、WARN {n_warn}）')
        print()

    if usage_err:
        return 2
    return 1 if any_fail else 0


if __name__ == '__main__':
    sys.exit(main())
