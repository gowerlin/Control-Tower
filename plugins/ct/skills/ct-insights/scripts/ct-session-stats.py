#!/usr/bin/env python3
"""ct-session-stats.py — Claude Code 本機 session 紀錄（JSONL）→ 工單層級用量統計（v6.0.0-beta.10，T0394），
以及工具清單建議（`--tools`，v6.0.0-beta.12+，T0422）。

規則的權威是 ct-insights/references/analysis-rules.md § Session 用量統計（`*insights sessions`）
與 § 工具清單建議（`*insights tools`）；腳本把這兩節寫成程式，兩者不一致時改腳本。
來源：EXP-SESSIONLOG-001（T0391）與 PLAN-004 ⑥；PLAN-006（T0419～T0421）。

和 ct-workflow-prefilter.py 相同的做法：只用 Python 3 標準函式庫、只讀、不呼叫模型、不連網、不自動標記或修改工單。
只有 --snapshot-append、--facts 會寫到命令列指定的檔案。

隱私設計：
- 每筆 JSONL 紀錄讀進來後立刻經 project_record() 投影成只含允許欄位的小 dict，原始物件隨即丟棄。
- 指令原文（input.command）只在投影時正規化成雜湊、規則標記與第一個字；檔案路徑只留副檔名與是否在 repo 內。
- 使用者訊息只比對 ct-exec 工單號與 slash command 名稱（每一則都比對，保留命名空間），其他內容不保留。
- 附件（skill_listing、deferred_tools_delta、mcp_instructions_delta、agent_listing_delta）與 api-request-shape
  只留名稱與長度；清單與 instructions 的文字只在投影時量長度，不保留。
- --tools 讀設定檔時只取鍵名、type、啟用狀態、版號與 hook 事件名；env／headers／args／url／command 的值不讀出。
- 工單只讀 frontmatter 的 id、type、session_ids；塔台狀態只讀「塔台 session `<uuid>`」；決策日誌只讀 D###、時間行、索引表最後一欄。
- 每次輸出（stdout、快照、候選事實）前自動跑隱私自檢，命中就不輸出並 exit 3。

用法（完整說明見 analysis-rules.md）：
  python <ct-insights>/scripts/ct-session-stats.py --workorders-dir _ct-workorders --days 30
  python <ct-insights>/scripts/ct-session-stats.py --workorders-dir _ct-workorders --workorders T0394 \
      --snapshot-append _ct-workorders/_insights/session-stats/2026-11.json
  python <ct-insights>/scripts/ct-session-stats.py --tools --workorders-dir _ct-workorders --days 30
  python <ct-insights>/scripts/ct-session-stats.py --self-check out.json

exit code：0 成功；2 參數錯誤；3 隱私自檢不通過（不輸出）；4 資料不可用（找不到 session 紀錄）。
"""
from __future__ import annotations

import argparse
import bisect
import collections
import datetime as _dt
import glob
import hashlib
import json
import os
import re
import sys

SCRIPT_NAME = "ct-session-stats.py"
GENERATOR_VERSION = "0.2.0"
REPORT_SCHEMA = "ct-session-stats-report/0.1"
SNAPSHOT_SCHEMA = "ct-session-stats-snapshot/0.2"
SNAPSHOT_SCHEMAS_READ = ("ct-session-stats-snapshot/0.1", SNAPSHOT_SCHEMA)
FACT_SCHEMA = "ct-session-fact/0.1"
PRICING_SCHEMA = "ct-session-stats-pricing/0.1"
TOOLS_SCHEMA = "ct-tool-usage/0.1"

EXIT_OK, EXIT_USAGE, EXIT_PRIVACY, EXIT_UNAVAILABLE = 0, 2, 3, 4

STUCK_WINDOW = 10
STUCK_THRESHOLD = 3  # max_failures_in_10_calls >= 3 → 🔵 觀察訊號（E3；門檻未經結果校準）
DECISION_SLACK = _dt.timedelta(seconds=60)  # 決策時間只到分鐘：同一分鐘內的請求仍算在該筆之前

WO_ID = r"(?:[A-Z][A-Z0-9]*-)?T\d{4}"
WO_ID_RE = re.compile(r"^" + WO_ID + r"$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
# ① 第一則使用者訊息：/ct-exec T####、$ct-exec T####；plugin 安裝時 slash command 帶命名空間（例 /ct:ct-exec）
CTEXEC_RE = re.compile(r"^[/$](?:[a-z0-9_-]{1,40}:)?ct-exec\s+(" + WO_ID + r")(?![0-9])")
SLASH_NAME_RE = re.compile(r"^[/$](?:[a-z0-9_-]{1,40}:)?([a-z0-9][a-z0-9_-]{0,40})(?:\s|$)")
# v6.0.0-beta.12：slash command 全名（保留命名空間，例 /codex:rescue → codex:rescue），計入 skills_invoked
SLASH_FULL_RE = re.compile(r"^[/$]((?:[a-z0-9_-]{1,40}:)?[a-z0-9][a-z0-9_-]{0,40})(?:\s|$)")
TITLE_WO_RE = re.compile(r"(?<![A-Za-z0-9])(" + WO_ID + r")(?![0-9])")
CMD_NAME_RE = re.compile(r"<command-name>([^<]{0,80})</command-name>")
CMD_ARGS_RE = re.compile(r"<command-args>([^<]{0,200})</command-args>")
TOWER_SID_RE = re.compile(r"塔台 session\s*`([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})`")
SAFE_EXT_RE = re.compile(r"^\.[a-z0-9]{1,8}$")
ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
RELATED_ID_RE = re.compile(r"(?:[A-Z]+-)?T\d{4}|PLAN-\d{3}|BUG-\d{3,4}|EXP-[A-Z]+-\d{3}")

USAGE_KEYS = (
    ("input", ("input_tokens",)),
    ("output", ("output_tokens",)),
    ("cache_read", ("cache_read_input_tokens",)),
    ("cache_write", ("cache_creation_input_tokens",)),
    ("cache_write_5m", ("cache_creation", "ephemeral_5m_input_tokens")),
    ("cache_write_1h", ("cache_creation", "ephemeral_1h_input_tokens")),
)
TOKEN_FIELDS = tuple(k for k, _ in USAGE_KEYS)
FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Grep", "Glob"}
SHELL_TOOLS = {"Bash", "PowerShell"}
AGENT_TOOLS = {"Agent", "Task"}
ATTACHMENT_TYPES = ("skill_listing", "deferred_tools_delta", "mcp_instructions_delta", "agent_listing_delta")


# ---------------------------------------------------------------------------
# 指令正規化（E4）：原文只在這裡出現，回傳值不含原文
# ---------------------------------------------------------------------------
_NORM_RULES = (
    ("node-alias", re.compile(r'"?\$\{BAT_HELPER_NODE:-node\}"?'), "node"),
    ("quotes", re.compile(r"'"), '"'),
    ("path-sep", re.compile(r"\\\\|\\"), "/"),
    ("drive", re.compile(r'(?<![A-Za-z0-9])/([a-zA-Z])/(?=[^/\s"])'), r"\1:/"),
    ("trailing-redirect", re.compile(r"(\s+2>&1|\s+2>\s*/dev/null|\s+2>\$null)+\s*$"), ""),
    ("trailing-pager", re.compile(r"(\s*\|\s*(head|tail)(\s+-n)?\s+-?\d+\s*)+$"), ""),
    ("whitespace", re.compile(r"\s+"), " "),
)
KNOWN_COMMANDS = frozenset("""
git gh node npm npx pnpm yarn python python3 py pip uv bash sh zsh pwsh powershell cmd wsl
cd ls dir cat head tail grep rg sed awk find echo printf cp mv rm mkdir rmdir touch chmod ln
diff cmp wc sort uniq tr cut tee xargs jq date sleep timeout time test which where env printenv
export set unset source for while if until do case curl wget tar unzip zip gzip sha256sum md5sum
basename dirname realpath cygpath iconv file strings du df ps kill tasklist taskkill winget choco
docker go cargo dotnet java make ffmpeg claude codex true false exit
""".split())
PS_CMDLET_RE = re.compile(
    r"^(?:get|set|new|remove|test|select|write|start|stop|add|invoke|out|copy|move|rename|join|split|"
    r"convert|convertto|convertfrom|import|export|measure|sort|where|foreach|format|clear|resolve|"
    r"expand|compress|read|wait|push|pop|update|register|unregister|enable|disable)-[a-z]{2,40}$")


def _h(s: str, n: int = 12) -> str:
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()[:n]


def _lower_drive(s: str) -> str:
    return re.sub(r"(?<![A-Za-z0-9])([A-Z]):/", lambda m: m.group(1).lower() + ":/", s)


def first_word(tokens) -> str:
    """指令第一個字：只輸出已知指令或 PowerShell cmdlet，其他一律代號（避免洩漏目錄名或檔名）。"""
    for t in tokens:
        if not t or ENV_ASSIGN_RE.match(t):
            continue
        t = t.strip('"').strip("'")
        if re.search(r"[/\\:]", t):
            return "<path>"
        t = t.lower()
        if t.endswith(".exe"):
            t = t[:-4]
        if re.search(r"\.[a-z0-9]{1,8}$", t):
            return "<file>"
        if t in KNOWN_COMMANDS or PS_CMDLET_RE.match(t):
            return t
        return "<other>"
    return "<none>"


def normalize_command(cmd) -> dict:
    raw = cmd if isinstance(cmd, str) else ""
    s = raw.strip()
    tags = []
    for tag, rx, rep in _NORM_RULES:
        s2 = rx.sub(rep, s)
        if tag == "drive":
            s2 = _lower_drive(s2)
        if s2 != s:
            tags.append(tag)
            s = s2
    tokens = s.strip().split(" ")
    return {"raw": _h(raw), "norm": _h(s.strip()), "tags": tuple(tags), "first": first_word(tokens),
            "tokset": frozenset(_h(t, 8) for t in tokens if t)}


def path_facts(path, cwd) -> dict:
    """檔案路徑 → 副檔名、是否在 repo 內、記憶體內雜湊。不回傳路徑本身。"""
    if not isinstance(path, str) or not path:
        return {"ext": "<none>", "in_repo": None, "hash": None}
    p = _lower_drive(re.sub(r"^/([a-zA-Z])/", r"\1:/", path.replace("\\", "/")))
    c = _lower_drive((cwd or "").replace("\\", "/")).rstrip("/")
    absolute = bool(re.match(r"^([a-z]:/|/|~)", p))
    in_repo = (not absolute) or (bool(c) and (p == c or p.startswith(c + "/")))
    base = p.rstrip("/").split("/")[-1]
    ext = os.path.splitext(base)[1].lower() if "." in base else ""
    ext = ext if SAFE_EXT_RE.match(ext or "") else ("<none>" if not ext else "<other>")
    full = p if absolute or not c else c + "/" + p
    return {"ext": ext, "in_repo": in_repo, "hash": _h(full.lower())}


# ---------------------------------------------------------------------------
# 投影：唯一讀原始 JSONL 紀錄的地方
# ---------------------------------------------------------------------------
def _prompt_facts(content):
    if isinstance(content, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in content):
            return None
        txt = "".join(x.get("text", "") for x in content
                      if isinstance(x, dict) and x.get("type") == "text" and isinstance(x.get("text"), str))
    elif isinstance(content, str):
        txt = content
    else:
        return {"kind": "empty", "wo": None, "slash": None, "cmd": None}
    m1 = CMD_NAME_RE.search(txt)
    if m1:  # slash command 展開後：<command-name>/ct-exec</command-name><command-args>T####</command-args>
        m2 = CMD_ARGS_RE.search(txt)
        txt = (m1.group(1).strip() + " " + (m2.group(1).strip() if m2 else "")).strip()
    else:
        txt = txt.strip()
    full = SLASH_FULL_RE.match(txt)
    cmd = full.group(1) if full else None
    m = CTEXEC_RE.match(txt)
    if m:
        return {"kind": "ct-exec", "wo": m.group(1), "slash": "ct-exec", "cmd": cmd}
    s = SLASH_NAME_RE.match(txt)
    if s:
        return {"kind": "slash", "wo": None, "slash": s.group(1), "cmd": cmd}
    return {"kind": "text", "wo": None, "slash": None, "cmd": None}


def _usage(u) -> dict:
    u = u if isinstance(u, dict) else {}
    out = {}
    for name, path in USAGE_KEYS:
        v = u
        for k in path:
            v = v.get(k) if isinstance(v, dict) else None
        out[name] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0
    return out


def _title_facts(title) -> dict:
    if not isinstance(title, str):
        return {"wo": None, "role": None}
    m = TITLE_WO_RE.search(title)
    role = None
    for r in ("Worker", "Tower"):
        if re.search(r"(?<![A-Za-z])" + r + r"(?![A-Za-z])", title):
            role = r.lower()
            break
    return {"wo": m.group(1) if m else None, "role": role}


def _safe_name(v, rx=r"^[A-Za-z0-9:_.-]{1,64}$"):
    if not isinstance(v, str) or not v:
        return None
    return v if re.match(rx, v) else "<other>"


TOOL_NAME_RX = r"^[A-Za-z][A-Za-z0-9_.-]{0,100}$"


def server_key(name):
    """MCP server 名稱 → 工具前綴用的鍵（`claude.ai Claude Docs` → `claude_ai_Claude_Docs`、
    `plugin:presenton:presenton` → `plugin_presenton_presenton`）。"""
    if not isinstance(name, str) or not name:
        return None
    return _safe_name(re.sub(r"[^A-Za-z0-9_-]", "_", name))


def _names(lst, rx=r"^[A-Za-z0-9:_.-]{1,64}$"):
    return [n for n in (_safe_name(x, rx) for x in (lst if isinstance(lst, list) else []) if isinstance(x, str)) if n]


def _listing_facts(a: dict) -> dict:
    """skill_listing：只留名稱、逐筆長度、只剩名稱的筆數、清單總長。說明文字只在這裡量長度，不保留。"""
    raw = [x for x in (a.get("names") if isinstance(a.get("names"), list) else []) if isinstance(x, str)]
    content = a.get("content") if isinstance(a.get("content"), str) else ""
    nset = set(raw)
    entry, bare = {}, set()
    for line in content.split("\n"):
        if not line.startswith("- "):
            continue
        body = line[2:]
        best = body if body in nset else None
        if best is None:
            i = body.find(":")
            while i >= 0:
                if body[:i] in nset and (best is None or i > len(best)):
                    best = body[:i]
                i = body.find(":", i + 1)
        if best is None:
            continue
        key = _safe_name(best) or "<other>"
        entry[key] = max(entry.get(key, 0), len(line) + 1)
        if body == best:
            bare.add(key)
    names = [_safe_name(n) or "<other>" for n in raw]
    return {"names": names, "len": entry, "bare": sorted(bare), "total": len(content),
            "initial": bool(a.get("isInitial"))}


def _attachment_facts(a: dict) -> dict | None:
    at = a.get("type")
    if at == "skill_listing":
        return dict(_listing_facts(a), att=at)
    if at == "deferred_tools_delta":
        def srv(lst):
            out = []
            for x in lst if isinstance(lst, list) else []:
                k = server_key(x.get("name") if isinstance(x, dict) else x)
                if k:
                    out.append(k)
            return out
        return {"att": at, "added": _names(a.get("addedNames"), TOOL_NAME_RX),
                "removed": len(a.get("removedNames") or []) if isinstance(a.get("removedNames"), list) else 0,
                "failed": srv(a.get("failedMcpServers")), "pending": srv(a.get("pendingMcpServers"))}
    if at == "mcp_instructions_delta":
        names = a.get("addedNames") if isinstance(a.get("addedNames"), list) else []
        blocks = a.get("addedBlocks") if isinstance(a.get("addedBlocks"), list) else []
        added = []
        for i, n in enumerate(names):
            k = server_key(n)
            if k:
                b = blocks[i] if i < len(blocks) and isinstance(blocks[i], str) else ""
                added.append((k, len(b)))
        return {"att": at, "added": added,
                "removed": len(a.get("removedNames") or []) if isinstance(a.get("removedNames"), list) else 0}
    if at == "agent_listing_delta":
        return {"att": at, "added": _names(a.get("addedTypes")), "builtin": _names(a.get("builtInTypes")),
                "builtin_plugin": _names(a.get("builtInPluginTypes")),
                "removed": len(a.get("removedTypes") or []) if isinstance(a.get("removedTypes"), list) else 0}
    return None


def _shape_facts(o: dict) -> list:
    """api-request-shape：工具名稱、序列化後的字元數、是否 deferred。schema 內容不保留。"""
    shape = o.get("shape") if isinstance(o.get("shape"), dict) else {}
    out = []
    for t in shape.get("tools") if isinstance(shape.get("tools"), list) else []:
        if not isinstance(t, dict):
            continue
        name = _safe_name(t.get("name"), TOOL_NAME_RX)
        if not name:
            continue
        out.append((name, len(json.dumps(t, ensure_ascii=False, separators=(",", ":"))), bool(t.get("defer_loading"))))
    return out


def project_record(o) -> dict | None:
    if not isinstance(o, dict):
        return None
    t = o.get("type")
    base = {"type": t if isinstance(t, str) else None, "timestamp": o.get("timestamp"),
            "version": _safe_name(o.get("version"), r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.]+)?$"),
            "uuid": o.get("uuid")}
    cwd = o.get("cwd") if isinstance(o.get("cwd"), str) else None  # 只在記憶體內判斷 repo，不輸出
    if t == "attachment":
        a = o.get("attachment") if isinstance(o.get("attachment"), dict) else {}
        f = _attachment_facts(a) if a.get("type") in ATTACHMENT_TYPES else None
        if f is None:
            return {"type": "attachment", "timestamp": o.get("timestamp"), "cwd": cwd}
        base.update(f, cwd=cwd)
        return base
    if t == "api-request-shape":
        base["shape_tools"] = _shape_facts(o)
        return base
    if t == "assistant":
        msg = o.get("message") if isinstance(o.get("message"), dict) else {}
        cwd = o.get("cwd") if isinstance(o.get("cwd"), str) else None
        items = []
        for c in msg.get("content") or []:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            name = c.get("name") if isinstance(c.get("name"), str) else "<unknown>"
            if not re.match(r"^[A-Za-z][A-Za-z0-9_.-]{0,100}$", name):
                name = "<other>"
            inp = c.get("input") if isinstance(c.get("input"), dict) else {}
            item = {"name": name, "id": c.get("id")}
            if name in FILE_TOOLS:
                item["path"] = path_facts(inp.get("file_path") or inp.get("path") or inp.get("notebook_path"), cwd)
            if name in SHELL_TOOLS:
                item["cmd"] = normalize_command(inp.get("command"))
            if name == "Skill":
                item["skill"] = _safe_name(inp.get("skill")) or "<other>"
            if name in AGENT_TOOLS:  # v6.0.0-beta.12：agent 類型；沒給 subagent_type 記 <default>
                st = inp.get("subagent_type")
                item["agent"] = (_safe_name(st) or "<other>") if isinstance(st, str) and st else "<default>"
            items.append(item)
        base.update({"msg_id": msg.get("id"), "requestId": o.get("requestId"),
                     "model": _safe_name(msg.get("model"), r"^[a-z][a-z0-9.-]{0,63}$"),
                     "usage": _usage(msg.get("usage")), "tools": items,
                     "attributionMcpServer": _safe_name(o.get("attributionMcpServer")),
                     "in_repo_cwd": cwd})
        return base
    if t == "user":
        msg = o.get("message") if isinstance(o.get("message"), dict) else {}
        content = msg.get("content")
        results = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    results.append((c.get("tool_use_id"), bool(c.get("is_error"))))
        meta = bool(o.get("isMeta"))
        base.update({"isMeta": meta, "results": results, "cwd": cwd,
                     "prompt": None if results or meta else _prompt_facts(content)})
        return base
    if t in ("custom-title", "agent-name"):
        base["title"] = _title_facts(o.get("customTitle") if t == "custom-title" else o.get("agentName"))
        return base
    return {"type": t if isinstance(t, str) else None}


def iter_projected(path: str, mutate=None):
    """逐行讀 JSONL → 投影。mutate 只給測試用（未知欄位注入）。"""
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if mutate is not None:
                o = mutate(o)
            r = project_record(o)
            if r is not None:
                yield r


# ---------------------------------------------------------------------------
# 單一 transcript 的累計
# ---------------------------------------------------------------------------
def parse_ts(s):
    if not isinstance(s, str) or not s:
        return None
    try:
        t = _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.astimezone()


def iso(t):
    return t.astimezone(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if t else None


class Acc:
    def __init__(self):
        self.versions = set()
        self.req = {}  # (message.id, requestId) → {"usage", "model", "ts"}（E1 去重）
        self.tool_seq = []
        self.tool_ids = set()
        self.results = {}
        self.result_order = []
        self.prompts = []
        self.titles = []
        self.mcp_attr = collections.Counter()
        self.ts_min = self.ts_max = None
        self.records = 0
        self.cwd = None
        self.slash = []  # (全名, ts)：每一則使用者訊息的 slash command（v6.0.0-beta.12）
        # 載入清單（附件；v6.0.0-beta.12，--tools 與 slash 計數用）
        self.listing = {"has": False, "initial_total": 0, "any_total": 0, "initial": set(), "all": set(),
                        "len": {}, "bare": set(), "has_initial": False}
        self.mcp = {"has": False, "names": collections.defaultdict(set), "instr": {}, "failed": set(),
                    "pending": set(), "removed": 0}
        self.agents = {"has": False, "types": set(), "builtin": set()}
        self.shape = {"has": False, "tools": {}, "mcp": set()}

    def add(self, r: dict):
        t = r.get("type")
        self.records += 1
        ts = parse_ts(r.get("timestamp"))
        if ts is not None and t in ("assistant", "user"):
            self.ts_min = ts if self.ts_min is None or ts < self.ts_min else self.ts_min
            self.ts_max = ts if self.ts_max is None or ts > self.ts_max else self.ts_max
        if self.cwd is None and r.get("cwd"):
            self.cwd = r["cwd"]
        if t == "attachment" and "att" in r:
            self._add_attachment(r)
        elif t == "api-request-shape":
            sh = self.shape
            sh["has"] = True
            for name, n, deferred in r.get("shape_tools") or ():
                if name.startswith("mcp__"):
                    parts = name.split("__")
                    if len(parts) > 2 and parts[1]:
                        sh["mcp"].add(parts[1])
                    continue
                if not deferred:
                    sh["tools"][name] = max(sh["tools"].get(name, 0), n)
        if t == "assistant":
            if r.get("in_repo_cwd") and self.cwd is None:
                self.cwd = r["in_repo_cwd"]
            if r.get("version") and r["version"] != "<other>":
                self.versions.add(r["version"])
            key = (r.get("msg_id"), r.get("requestId"))
            if key == (None, None):
                key = ("uuid", r.get("uuid"))
            if key not in self.req:
                self.req[key] = {"usage": r["usage"], "model": r.get("model"), "ts": ts}
                if r.get("attributionMcpServer"):
                    self.mcp_attr[r["attributionMcpServer"]] += 1
            for c in r["tools"]:
                tid = c.get("id") or ("anon", len(self.tool_seq))
                if tid in self.tool_ids:
                    continue
                self.tool_ids.add(tid)
                self.tool_seq.append(dict(c, ts=ts))
        elif t == "user":
            for tid, err in r["results"]:
                self.results[tid] = err
                self.result_order.append(err)
            if r.get("prompt") is not None:
                self.prompts.append(r["prompt"])
                if r["prompt"].get("cmd"):
                    self.slash.append((r["prompt"]["cmd"], ts))
        elif t in ("custom-title", "agent-name"):
            self.titles.append(r["title"])

    def _add_attachment(self, r: dict):
        at = r["att"]
        if at == "skill_listing":
            li = self.listing
            li["has"] = True
            li["any_total"] = max(li["any_total"], r["total"])
            names = set(r["names"])
            li["all"] |= names
            for k, v in r["len"].items():
                li["len"][k] = max(li["len"].get(k, 0), v)
            # 基準清單：最長的一份 isInitial 清單；都沒有 isInitial 時用第一份
            if r["initial"] and (not li["has_initial"] or r["total"] >= li["initial_total"]):
                li.update(initial_total=r["total"], initial=names, bare=set(r["bare"]), has_initial=True)
            elif not li["has_initial"] and not li["initial"]:
                li.update(initial_total=r["total"], initial=names, bare=set(r["bare"]))
        elif at == "deferred_tools_delta":
            m = self.mcp
            m["has"] = True
            m["removed"] += r["removed"]
            for name in r["added"]:
                if name.startswith("mcp__"):
                    parts = name.split("__")
                    if len(parts) > 2 and parts[1]:
                        m["names"][parts[1]].add(name)
            m["failed"].update(r["failed"])
            m["pending"].update(r["pending"])
        elif at == "mcp_instructions_delta":
            m = self.mcp
            m["removed"] += r["removed"]
            for k, n in r["added"]:
                m["instr"][k] = max(m["instr"].get(k, 0), n)
        elif at == "agent_listing_delta":
            ag = self.agents
            ag["has"] = True
            ag["types"].update(r["added"])
            ag["builtin"].update(r["builtin"])

    def slash_counts(self) -> collections.Counter:
        """slash command 只在名稱出現在這個 session 的 skill 清單時才算（內建 CLI 命令 /clear 等不算）。"""
        listed = self.listing["all"]
        return collections.Counter(n for n, _ in self.slash if n in listed)

    def tokens(self) -> dict:
        tot = collections.Counter()
        for q in self.req.values():
            tot.update(q["usage"])
        return {k: int(tot.get(k, 0)) for k in TOKEN_FIELDS}

    def tokens_by_model(self) -> dict:
        out = collections.defaultdict(collections.Counter)
        for q in self.req.values():
            out[q["model"] or "<unknown>"].update(q["usage"])
        return {m: {k: int(c.get(k, 0)) for k in TOKEN_FIELDS} for m, c in out.items()}

    def tool_metrics(self) -> dict:
        by_tool, by_mcp, skills, fail_by_tool, agents = (collections.Counter() for _ in range(5))
        read_hits, norm_fail = collections.Counter(), collections.Counter()
        near = 0
        prev = None
        for c in self.tool_seq:
            name = c["name"]
            err = bool(self.results.get(c.get("id")))
            by_tool[name] += 1
            if name.startswith("mcp__"):
                parts = name.split("__")
                by_mcp[parts[1] if len(parts) > 2 and parts[1] else "<unknown>"] += 1
            if "skill" in c:
                skills[c["skill"]] += 1
            if "agent" in c:
                agents[c["agent"]] += 1
            if err:
                fail_by_tool[name] += 1
            if "path" in c and name == "Read" and c["path"]["hash"]:
                read_hits[c["path"]["hash"]] += 1
            if "cmd" in c:
                if err:
                    norm_fail[(name, c["cmd"]["norm"])] += 1
                    if prev is not None and prev[1] and prev[0]["name"] == name \
                            and prev[0]["cmd"]["first"] == c["cmd"]["first"]:
                        a, b = prev[0]["cmd"]["tokset"], c["cmd"]["tokset"]
                        near += (len(a & b) / len(a | b) if (a | b) else 1.0) >= 0.5
                prev = (c, err)
        skills.update(self.slash_counts())  # v6.0.0-beta.12：skills_invoked = Skill 工具 + slash command
        return {"by_tool": by_tool, "by_mcp_server": by_mcp, "skills_invoked": skills, "agents_invoked": agents,
                "failures_by_tool": fail_by_tool,
                "tool_calls": len(self.tool_seq), "failures": sum(fail_by_tool.values()),
                "same_file_read_ge3": sum(1 for v in read_hits.values() if v >= 3),
                "repeat_fail_groups_norm": sum(1 for v in norm_fail.values() if v >= 2),
                "near_repeat_fail_pairs_j50": int(near)}

    def stuck_metrics(self) -> dict:
        errs = self.result_order
        streak = best = 0
        for e in errs:
            streak = streak + 1 if e else 0
            best = max(best, streak)
        win = max((sum(errs[i:i + STUCK_WINDOW]) for i in range(max(1, len(errs) - STUCK_WINDOW + 1))), default=0)
        return {"max_failures_in_10_calls": int(win), "max_consecutive_failures": best}


def _feed(acc: Acc, path: str, until, mutate=None):
    for r in iter_projected(path, mutate):
        if until is not None:
            ts = parse_ts(r.get("timestamp"))
            if ts is not None and ts > until:
                continue  # 紀錄層級截止（E8）：執行中的 session 重跑才會一致
        acc.add(r)


def analyse_session(main_path: str, until=None, include_subagents=True, mutate=None) -> dict:
    sid = os.path.basename(main_path)[:-len(".jsonl")]
    main = Acc()
    _feed(main, main_path, until, mutate)
    subs = []
    sub_dir = os.path.join(os.path.dirname(main_path), sid, "subagents")  # E6；<sid>/workflows/ 不讀
    if include_subagents and os.path.isdir(sub_dir):
        for sp in sorted(glob.glob(os.path.join(sub_dir, "*.jsonl"))):
            a = Acc()
            _feed(a, sp, until, mutate)
            if a.records:
                subs.append(a)
    return {"sid": sid, "main": main, "subs": subs,
            "first": main.prompts[0] if main.prompts else None,
            "title_wo": next((t["wo"] for t in main.titles if t["wo"]), None),
            "title_role": next((t["role"] for t in main.titles if t["role"]), None)}


# ---------------------------------------------------------------------------
# 外部來源：工單 frontmatter、塔台狀態、決策日誌、BAT log（皆只讀限定欄位）
# ---------------------------------------------------------------------------
def _read_frontmatter(path: str, limit=32768) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(limit)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    return head[3:end] if end > 0 else None


def load_workorders(wo_dir: str) -> dict:
    """只讀 frontmatter 的 id、type、session_ids → {"types": {wo: type}, "sid_map": {sid: {wo,…}}}。"""
    types, sid_map = {}, collections.defaultdict(set)
    if not wo_dir or not os.path.isdir(wo_dir):
        return {"types": types, "sid_map": {}}
    for p in sorted(glob.glob(os.path.join(wo_dir, "**", "*.md"), recursive=True)):
        if os.sep + "_insights" + os.sep in p:
            continue
        fm = _read_frontmatter(p)
        if fm is None:
            continue
        mid = re.search(r"^id:\s*[\"']?(" + WO_ID + r")[\"']?\s*$", fm, re.M)
        if not mid:
            continue
        wo = mid.group(1)
        mty = re.search(r"^type:\s*[\"']?([a-z][a-z_-]{0,30})[\"']?\s*$", fm, re.M)
        types[wo] = mty.group(1) if mty else None
        ms = re.search(r"^session_ids:[ \t]*(.*)$((?:\n[ \t]+-.*$)*)", fm, re.M)
        if ms:
            vals = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", ms.group(1) + ms.group(2))
            for v in vals:
                sid_map[v].add(wo)
    return {"types": types, "sid_map": dict(sid_map)}


def load_tower_sessions(wo_dir: str, extra=()) -> set:
    """`_tower-state.md`（與歸檔的塔台狀態）開工條目的「塔台 session `<uuid>`」。"""
    paths = list(extra or ())
    if wo_dir and os.path.isdir(wo_dir):
        paths.append(os.path.join(wo_dir, "_tower-state.md"))
        paths += sorted(glob.glob(os.path.join(wo_dir, "_archive", "**", "*tower-state*.md"), recursive=True))
    out = set()
    for p in paths:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    out.update(TOWER_SID_RE.findall(line))
        except OSError:
            continue
    return out


def load_decisions(paths) -> list:
    """決策日誌（檔案或目錄，可多個）：只讀索引表 `| D### | 日期 | … | 相關 |` 的最後一欄、
    `## D###` 標題、其後第一個 `> YYYY-MM-DD HH:MM (UTC±N)` 時間行。回傳 [(時間, D###, [相關 ID])]（依時間排序）。"""
    files = []
    for p in paths or ():
        files += sorted(glob.glob(os.path.join(p, "*.md"))) if os.path.isdir(p) else [p]
    related, times = {}, {}
    for fp in files:
        cur = None
        try:
            f = open(fp, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with f:
            for line in f:
                m = re.match(r"^\|\s*(D\d{3,4})\s*\|\s*\d{4}-\d{2}-\d{2}\s*\|", line)
                if m:
                    last = line.rstrip().rstrip("|").split("|")[-1]
                    related[m.group(1)] = sorted(set(RELATED_ID_RE.findall(last)))
                    continue
                h = re.match(r"^#{2,4}\s*(D\d{3,4})\b", line)
                if h:
                    cur = h.group(1)
                    continue
                t = re.match(r"^>\s*(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})\s*\(UTC([+-]\d{1,2})\)", line)
                if t and cur and cur not in times:
                    tz = _dt.timezone(_dt.timedelta(hours=int(t.group(6))))
                    times[cur] = _dt.datetime(*(int(t.group(i)) for i in range(1, 6)), tzinfo=tz)
    return sorted((ts, did, related.get(did, [])) for did, ts in times.items())


def load_bat_log(path: str):
    """選填。只讀 event、terminalId、workorder、session；讀不到回傳 None（不影響其他結果，D517）。"""
    dispatch, hooks = {}, collections.defaultdict(set)
    try:
        f = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return None
    with f:
        for line in f:
            i = line.find("{")
            if i < 0:
                continue
            try:
                o = json.loads(line[i:])
            except ValueError:
                continue
            if not isinstance(o, dict):
                continue
            ev, tid = o.get("event"), o.get("terminalId")
            if ev == "invoke-create-with-command" and tid and isinstance(o.get("workorder"), str):
                dispatch[tid] = o["workorder"]
            elif ev == "report-hook" and tid and isinstance(o.get("session"), str) \
                    and re.match(r"^[0-9a-f]{8}$", o["session"]):
                hooks[o["session"]].add(tid)
    return {"dispatch": dispatch, "hooks": hooks}


def bat_workorder(sid: str, bat):
    if not bat:
        return None
    wos = {bat["dispatch"][t] for t in bat["hooks"].get(sid[:8], ()) if t in bat["dispatch"]}
    wos = {w for w in wos if WO_ID_RE.match(w)}
    return wos.pop() if len(wos) == 1 else None


def load_pricing(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, ValueError):
        return None
    return p if isinstance(p, dict) and p.get("schema") == PRICING_SCHEMA and isinstance(p.get("models"), dict) else None


# ---------------------------------------------------------------------------
# 歸屬（E2）：⓪ 工單 frontmatter session_ids → ① 第一則訊息 → ② 分頁標題 → ③ BAT 前綴（可選）
# ---------------------------------------------------------------------------
def resolve(s: dict, wo_info: dict, tower_sids: set, bat) -> dict:
    sid = s["sid"]
    fm_wos = sorted(wo_info.get("sid_map", {}).get(sid, ()))
    fm = fm_wos[0] if len(fm_wos) == 1 else None
    first = s["first"]
    ct = first["wo"] if first and first["kind"] == "ct-exec" else None
    tw = s["title_wo"]
    bw = bat_workorder(sid, bat)
    cands = [w for w in (fm, ct, tw, bw) if w]
    conflict = len(set(cands)) > 1 or len(fm_wos) > 1 or bool(fm_wos and sid in tower_sids)
    wo = fm or ct or tw or bw
    if fm:
        role = "worker"
    elif sid in tower_sids:
        role, wo = "tower", None
    elif first and first["kind"] == "slash" and first["slash"] == "control-tower":
        role, wo = "tower", None
    elif s["title_role"] == "tower" and not ct:
        role, wo = "tower", None
    elif wo:
        role = "worker"
    else:
        role = "other"
    if role == "tower":
        source = "tower-state" if sid in tower_sids else ("first-prompt" if first and first["kind"] == "slash" else "title")
    else:
        source = "frontmatter" if fm else "ct-exec" if ct else "title" if tw else "bat" if bw else None
    return {"workorder": wo if role == "worker" else None, "role": role, "source": source, "conflict": conflict}


# ---------------------------------------------------------------------------
# 成本（估算，等價 API 成本；E9）
# ---------------------------------------------------------------------------
def est_cost(by_model: dict, pricing):
    if not pricing:
        return None, None
    usd, unpriced = 0.0, 0
    for m in sorted(by_model):
        t = by_model[m]
        p = pricing["models"].get(m)
        if not isinstance(p, dict):
            unpriced += sum(t.values()) - t.get("cache_write_5m", 0) - t.get("cache_write_1h", 0)
            continue
        w5, w1 = t.get("cache_write_5m", 0), t.get("cache_write_1h", 0)
        rest = max(0, t.get("cache_write", 0) - w5 - w1)
        usd += (t.get("input", 0) * p["input"] + t.get("output", 0) * p["output"]
                + t.get("cache_read", 0) * p["cache_read"]
                + (w5 + rest) * p["cache_write_5m"] + w1 * p["cache_write_1h"]) / 1e6
    return round(usd, 4), int(unpriced)


def _merge_models(dicts):
    out = collections.defaultdict(collections.Counter)
    for d in dicts:
        for m, t in d.items():
            out[m].update(t)
    return {m: {k: int(c.get(k, 0)) for k in TOKEN_FIELDS} for m, c in out.items()}


def _tok(c) -> dict:
    return {k: int(c.get(k, 0)) for k in TOKEN_FIELDS}


# ---------------------------------------------------------------------------
# 組裝
# ---------------------------------------------------------------------------
def session_row(s: dict, att: dict, pricing, with_sid: bool) -> dict:
    m = s["main"]
    sub_tok, sub_tools = collections.Counter(), 0
    for a in s["subs"]:
        sub_tok.update(a.tokens())
        sub_tools += len(a.tool_seq)
    by_model = _merge_models([m.tokens_by_model()] + [a.tokens_by_model() for a in s["subs"]])
    usd, unpriced = est_cost(by_model, pricing)
    row = {"workorder": att["workorder"], "role": att["role"], "attribution": {"source": att["source"],
                                                                                "conflict": att["conflict"]},
           "versions": sorted(m.versions), "start": iso(m.ts_min), "end": iso(m.ts_max),
           "tokens": m.tokens(), "subagent_tokens": _tok(sub_tok), "est_usd": usd, "unpriced_tokens": unpriced,
           "api_requests": len(m.req), "tools": m.tool_metrics(), "stuck": m.stuck_metrics(),
           "subagent_files": len(s["subs"]), "subagent_tool_calls": sub_tools,
           "_sid": s["sid"], "_reqs": sorted(((q["ts"], q["usage"]) for q in
                                              list(m.req.values()) + [q for a in s["subs"] for q in a.req.values()]
                                              if q["ts"] is not None), key=lambda x: x[0]),
           "_ts": (m.ts_min, m.ts_max)}
    if with_sid:
        row["session_id"] = s["sid"]
    return row


def aggregate_workorders(rows, types: dict, with_sid: bool) -> list:
    by = collections.defaultdict(list)
    for r in rows:
        if r["role"] == "worker" and r["workorder"]:
            by[r["workorder"]].append(r)
    out = []
    for wo in sorted(by):
        rs = by[wo]
        tok, sub_tok = collections.Counter(), collections.Counter()
        tools, mcp, skills, fails, agents = (collections.Counter() for _ in range(5))
        counts = collections.Counter()
        stuck = collections.Counter()
        sources = collections.Counter()
        usd, unpriced, priced = 0.0, 0, True
        for r in rs:
            tok.update(r["tokens"])
            sub_tok.update(r["subagent_tokens"])
            t = r["tools"]
            tools.update(t["by_tool"])
            mcp.update(t["by_mcp_server"])
            skills.update(t["skills_invoked"])
            agents.update(t["agents_invoked"])
            fails.update(t["failures_by_tool"])
            for k in ("tool_calls", "failures", "same_file_read_ge3"):
                counts[k] += t[k]
            counts["api_requests"] += r["api_requests"]
            counts["subagent_files"] += r["subagent_files"]
            stuck["near_repeat_fail_pairs_j50"] += t["near_repeat_fail_pairs_j50"]
            stuck["repeat_fail_groups_norm"] += t["repeat_fail_groups_norm"]
            for k in ("max_failures_in_10_calls", "max_consecutive_failures"):
                stuck[k] = max(stuck[k], r["stuck"][k])
            sources[r["attribution"]["source"] or "<none>"] += 1
            if r["est_usd"] is None:
                priced = False
            else:
                usd += r["est_usd"]
                unpriced += r["unpriced_tokens"]
        entry = {
            "workorder": wo, "type": types.get(wo), "sessions": len(rs), "renews": len(rs) - 1,
            "versions": sorted({v for r in rs for v in r["versions"]}),
            "start": min((r["start"] for r in rs if r["start"]), default=None),
            "end": max((r["end"] for r in rs if r["end"]), default=None),
            "attribution": {"source": sorted(sources.items(), key=lambda x: (-x[1], x[0]))[0][0],
                            "sources": dict(sorted(sources.items())),
                            "conflict": any(r["attribution"]["conflict"] for r in rs)},
            "tokens": _tok(tok), "subagent_tokens": _tok(sub_tok),
            "est_usd": round(usd, 4) if priced else None, "unpriced_tokens": unpriced if priced else None,
            "counts": dict(sorted(counts.items())),
            "stuck": dict(sorted(stuck.items())),
            "stuck_signal": stuck["max_failures_in_10_calls"] >= STUCK_THRESHOLD,
            "top_tools": [[n, c] for n, c in sorted(tools.items(), key=lambda x: (-x[1], x[0]))[:5]],
            "by_tool": dict(sorted(tools.items())),
            "failures_by_tool": dict(sorted(fails.items())),
            "by_mcp_server": dict(sorted(mcp.items())),
            "skills_invoked": dict(sorted(skills.items())),
            "agents_invoked": dict(sorted(agents.items())),
        }
        if with_sid:
            entry["session_ids"] = sorted(r["_sid"] for r in rs)
        out.append(entry)
    return out


def tower_by_decision(rows, decisions) -> dict | None:
    """「估」：塔台每個 API 請求歸給「上一筆～這筆」的那筆決策（決策前；T0391 推論塔台先做事後寫決策）。
    該筆決策要在同一個塔台 session 結束（加 60 秒）之前；之後沒有決策的歸 after_last。未經結果驗證。"""
    if not decisions:
        return None
    keys = [d[0] + DECISION_SLACK for d in decisions]
    related = collections.defaultdict(collections.Counter)
    general, after_last, total = collections.Counter(), collections.Counter(), collections.Counter()
    for r in rows:
        if r["role"] != "tower":
            continue
        s_end = r["_ts"][1]
        for ts, usage in r["_reqs"]:
            total.update(usage)
            j = bisect.bisect_right(keys, ts)
            if j >= len(decisions) or (s_end is not None and decisions[j][0] > s_end + DECISION_SLACK):
                after_last.update(usage)
                continue
            ids = decisions[j][2]
            if not ids:
                general.update(usage)
                continue
            for i in ids:
                for k, v in usage.items():
                    related[i][k] += v / len(ids)
    rel = {i: {k: int(round(c.get(k, 0))) for k in TOKEN_FIELDS} for i, c in sorted(related.items())}
    covered = sum(v["output"] for v in rel.values())
    return {"estimate": True, "validated": False, "direction": "previous-to-this",
            "decisions": len(decisions), "related": rel, "general": _tok(general), "after_last": _tok(after_last),
            "share_output_related": round(covered / total["output"], 3) if total.get("output") else 0.0}


def _usage_block(rows, role, pricing) -> dict:
    tok, sub, n = collections.Counter(), collections.Counter(), 0
    usd, priced = 0.0, True
    for r in rows:
        if r["role"] != role:
            continue
        n += 1
        tok.update(r["tokens"])
        sub.update(r["subagent_tokens"])
        if r["est_usd"] is None:
            priced = False
        else:
            usd += r["est_usd"]
    return {"sessions": n, "tokens": _tok(tok), "subagent_tokens": _tok(sub),
            "est_usd": round(usd, 4) if priced and pricing else None}


def tower_daily(rows) -> dict:
    out = collections.defaultdict(collections.Counter)
    for r in rows:
        if r["role"] != "tower":
            continue
        for ts, usage in r["_reqs"]:
            d = ts.astimezone(_dt.timezone.utc).date().isoformat()
            out[d].update(usage)
            out[d]["api_requests"] += 1
    return {d: {k: int(c.get(k, 0)) for k in TOKEN_FIELDS + ("api_requests",)} for d, c in sorted(out.items())}


def _date_bound(s, end=False):
    if not s:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        d = _dt.datetime.fromisoformat(s).astimezone()  # 只給日期：本機時區的當天起訖
        return d + _dt.timedelta(days=1, microseconds=-1) if end else d
    t = parse_ts(s)
    if t is None:
        raise ValueError(s)
    return t


def encode_project(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9-]", "-", path)


class Unavailable(Exception):
    pass


def build_report(args, mutate=None) -> dict:
    projects = args.project if isinstance(args.project, list) else [args.project]
    dirs = [os.path.join(os.path.expanduser(args.projects_dir), p) for p in projects]
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        raise Unavailable("project-dir-not-found")
    seen, files = set(), []
    for d in dirs:  # 可給多個 --project（例：隔離工單的 worktree 路徑）；同一個 session id 只算一次
        for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
            if os.path.basename(f) not in seen:
                seen.add(os.path.basename(f))
                files.append(f)
    files.sort(key=lambda f: (os.path.basename(f), f))
    if not files:
        raise Unavailable("no-session-files")
    since = _date_bound(args.since)
    until = _date_bound(args.until, end=True)
    if args.days and not since:
        since = (_dt.datetime.now().astimezone() - _dt.timedelta(days=args.days)).replace(
            hour=0, minute=0, second=0, microsecond=0)
    wo_info = load_workorders(args.workorders_dir)
    tower_sids = load_tower_sessions(args.workorders_dir, args.tower_state)
    bat = load_bat_log(args.bat_log) if args.bat_log else None
    pricing = load_pricing(args.pricing)
    decisions = load_decisions(args.decision_log) if args.decision_log else None
    wanted = {w.strip() for w in args.workorders.split(",") if w.strip()} if args.workorders else None
    rows = []
    for mp in files:
        s = analyse_session(mp, until=until, include_subagents=not args.no_subagents, mutate=mutate)
        m = s["main"]
        if m.ts_min is None or (since and m.ts_min < since) or (until and m.ts_min > until):
            continue
        att = resolve(s, wo_info, tower_sids, bat)
        if wanted is not None and att["role"] != "tower" and att["workorder"] not in wanted:
            continue
        rows.append(session_row(s, att, pricing, args.with_session_ids))
    if wanted is not None:  # 只留和這些工單時間重疊的塔台 session
        ws = [r for r in rows if r["role"] == "worker"]
        lo = min((r["_ts"][0] for r in ws), default=None)
        hi = max((r["_ts"][1] for r in ws), default=None)
        rows = [r for r in rows if r["role"] != "tower" or (lo and hi and r["_ts"][1] >= lo and r["_ts"][0] <= hi)]
    rows.sort(key=lambda r: (r["start"] or "", r["workorder"] or "", r["role"], r["_sid"]))
    n_all = len(rows)
    n_worker = sum(1 for r in rows if r["role"] == "worker")
    srcs = collections.Counter(r["attribution"]["source"] or "<none>" for r in rows if r["role"] == "worker")
    rep = {
        "schema": REPORT_SCHEMA,
        "generator": {"script": SCRIPT_NAME, "version": GENERATOR_VERSION},
        "source": {"agent": "claude-code", "claude_code_versions": sorted({v for r in rows for v in r["versions"]}),
                   "workorders_dir": bool(args.workorders_dir), "tower_state_ids": len(tower_sids),
                   "frontmatter_session_ids": len(wo_info["sid_map"]), "bat_log": bat is not None,
                   "decision_log": decisions is not None, "subagents": not args.no_subagents,
                   "pricing_as_of": pricing.get("as_of") if pricing else None},
        "filter": {"workorders": sorted(wanted) if wanted else None,
                   "since": iso(since), "until": iso(until)},
        "totals": {"sessions": n_all, "worker_sessions": n_worker,
                   "tower_sessions": sum(1 for r in rows if r["role"] == "tower"),
                   "other_sessions": sum(1 for r in rows if r["role"] == "other"),
                   "workorders": len({r["workorder"] for r in rows if r["role"] == "worker"})},
        "coverage": {"attributed_worker_sessions": n_worker,
                     "share_of_sessions": round(n_worker / n_all, 3) if n_all else 0.0,
                     "worker_sources": dict(sorted(srcs.items())),
                     "conflicts": sum(1 for r in rows if r["attribution"]["conflict"])},
        "workorders": aggregate_workorders(rows, wo_info["types"], args.with_session_ids),
        "tower_usage": dict(_usage_block(rows, "tower", pricing), allocated=False),
        "other_usage": _usage_block(rows, "other", pricing),
        "stuck_signals": [],
        "tower_daily": tower_daily(rows),
    }
    rep["stuck_signals"] = [w["workorder"] for w in rep["workorders"] if w["stuck_signal"]]
    tbd = tower_by_decision(rows, decisions)
    if tbd is not None:
        rep["tower_by_decision"] = tbd
    if args.sessions:
        rep["sessions"] = [_public_row(r) for r in rows]
    return rep


def _public_row(r: dict) -> dict:
    d = {k: v for k, v in r.items() if not k.startswith("_")}
    t = dict(d["tools"])
    for k in ("by_tool", "by_mcp_server", "skills_invoked", "agents_invoked", "failures_by_tool"):
        t[k] = dict(sorted(t[k].items()))
    d["tools"] = t
    return d


# ---------------------------------------------------------------------------
# 快照（E7）與候選事實（給 ⑦）
# ---------------------------------------------------------------------------
SNAPSHOT_ENTRY_KEYS = ("workorder", "type", "sessions", "renews", "versions", "start", "end", "attribution", "tokens",
                       "subagent_tokens", "est_usd", "unpriced_tokens", "counts", "stuck", "stuck_signal", "top_tools",
                       "by_tool", "failures_by_tool", "by_mcp_server", "skills_invoked", "agents_invoked",
                       "session_ids")


def _load_snapshot(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and d.get("schema") in SNAPSHOT_SCHEMAS_READ else None


def snapshot_append(rep: dict, path: str, now: str):
    """把報表的工單條目併入快照檔。規則：
    - 已在同目錄其他月份快照裡的工單不重複寫；
    - 同一檔已有的工單：新結果的 sessions 不少於舊的才取代（原始紀錄被清掉時不會蓋掉舊數字）；
    - tower_daily 逐日取 output 較大的那份。回傳 (快照 dict, 新增, 取代, 保留)。"""
    d = os.path.dirname(os.path.abspath(path))
    elsewhere = set()
    for p in sorted(glob.glob(os.path.join(d, "*.json"))):
        if os.path.abspath(p) == os.path.abspath(path):
            continue
        o = _load_snapshot(p)
        if o:
            elsewhere.update(w.get("workorder") for w in o.get("workorders", []))
    old = _load_snapshot(path) if os.path.exists(path) else None
    entries = {w["workorder"]: w for w in (old or {}).get("workorders", []) if isinstance(w, dict)}
    added = replaced = kept = 0
    for w in rep["workorders"]:
        e = {k: w[k] for k in SNAPSHOT_ENTRY_KEYS if k in w}
        wo = e["workorder"]
        if wo in elsewhere:
            kept += 1
            continue
        if wo in entries:
            if e["sessions"] >= entries[wo].get("sessions", 0):
                replaced += entries[wo] != e
                entries[wo] = e
            else:
                kept += 1
        else:
            entries[wo] = e
            added += 1
    daily = dict((old or {}).get("tower_daily", {}))
    for day, v in rep.get("tower_daily", {}).items():
        if day not in daily or v.get("output", 0) >= daily[day].get("output", 0):
            daily[day] = v
    snap = {"schema": SNAPSHOT_SCHEMA, "generated_at": now, "generator": rep["generator"],
            "source": {"agent": "claude-code",
                       "claude_code_versions": sorted(set((old or {}).get("source", {}).get("claude_code_versions", []))
                                                      | set(rep["source"]["claude_code_versions"])),
                       "pricing_as_of": rep["source"]["pricing_as_of"]},
            "workorders": [entries[k] for k in sorted(entries)],
            "tower_daily": dict(sorted(daily.items()))}
    return snap, added, replaced, kept


def _day(s):
    return s[:10] if isinstance(s, str) and len(s) >= 10 else None


def build_facts(entries: list) -> list:
    """候選事實（ct-session-fact/0.1）：由快照條目產生，不讀 JSONL，同一份快照一定得到同一份結果。
    規則 stuck.window10_fail_ge3：工單的 max_failures_in_10_calls >= 3，主體是該單失敗最多的工具。"""
    entries = sorted((e for e in entries if isinstance(e, dict) and e.get("workorder")), key=lambda e: e["workorder"])
    if not entries:
        return []
    days_all = sorted(d for e in entries for d in (_day(e.get("start")), _day(e.get("end"))) if d)
    src = f"ct-session-stats {GENERATOR_VERSION} {days_all[0]}..{days_all[-1]}" if days_all else None
    groups = collections.defaultdict(list)
    for e in entries:
        st = e.get("stuck") or {}
        if st.get("max_failures_in_10_calls", 0) < STUCK_THRESHOLD:
            continue
        fb = e.get("failures_by_tool") or {}
        subj = sorted(fb.items(), key=lambda x: (-x[1], x[0]))[0][0] if fb else "<unknown>"
        groups[subj].append(e)
    facts = []
    for subj in sorted(groups):
        es = sorted(groups[subj], key=lambda e: e["workorder"])
        wos = [e["workorder"] for e in es]
        days = sorted({_day(e.get("end")) for e in es if _day(e.get("end"))})
        last = days[-1] if days else None
        counter = sorted(e["workorder"] for e in entries
                         if e["workorder"] not in wos and last and (_day(e.get("end")) or "") > last
                         and (e.get("by_tool") or {}).get(subj, 0) >= STUCK_WINDOW
                         and (e.get("stuck") or {}).get("max_failures_in_10_calls", 0) < STUCK_THRESHOLD)
        facts.append({
            "schema": FACT_SCHEMA, "fact_id": f"stuck.window10:{subj}", "rule": "stuck.window10_fail_ge3",
            "subject": {"kind": "tool", "name": subj}, "workorders": wos, "days": days,
            "evidence": {"metric": "max_failures_in_10_calls",
                         "values": [e["stuck"]["max_failures_in_10_calls"] for e in es]},
            "counter_evidence": {"workorders": counter}, "source": src,
            "confidence": "🟡" if len(wos) >= 2 and len(days) >= 2 else "🔵",
            "state": "withdrawn-candidate" if len(counter) >= 2 else "candidate",
        })
    return facts


# ---------------------------------------------------------------------------
# 隱私自檢：所有字串與鍵都要符合允許樣式；全文不得有路徑、指令片段、信箱、權杖值
# ---------------------------------------------------------------------------
ALLOWED_STRING_RES = [re.compile(x) for x in (
    r"^" + WO_ID + r"$",
    r"^(?:PLAN-\d{3}|BUG-\d{3,4}|EXP-[A-Z]+-\d{3}|D\d{3,4})$",
    r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.]+)?$",
    r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$",
    r"^mcp__[A-Za-z0-9_.-]{1,100}$",
    r"^[A-Za-z][A-Za-z0-9_:.-]{0,63}$",
    r"^\.[a-z0-9]{1,8}$",
    r"^<(?:none|other|unknown|path|file|default|current)>$",
    r"^[a-z0-9][a-z0-9._+-]{0,30}$",
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    r"^ct-session-(?:stats-(?:snapshot|report|pricing)|fact)/\d+\.\d+$",
    r"^ct-tool-usage/\d+\.\d+$",
    r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}@[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$",  # plugin id（例 codex@openai-codex）
    r"^ct-session-stats\.py$",
    r"^ct-session-stats \d+\.\d+\.\d+ \d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}$",
    r"^(?:🔵|🟡)$",
)]
FORBIDDEN_RES = [re.compile(x) for x in (
    r"[A-Za-z]:[\\/]", r"(^|[\s\"'])/(?:c|d|home|Users|tmp|mnt)/", r"\\\\|\\Users|/Users/|\.claude/|AppData",
    r"\s&&\s|\s\|\s", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}",
)]
SECRET_ENV = ("BAT_REMOTE_TOKEN",)
TEXT_LINE_RE = re.compile(r"^[\w .,:;=()%/<>+\-\[\]#|—→·×*~'\"$🔵🟡「」（）、，：]*$")


def check_text(text: str) -> list:
    problems = []
    for name in SECRET_ENV:
        v = os.environ.get(name)
        if v and len(v) >= 8 and v in text:
            problems.append(f"secret value of {name} found")
    for rx in FORBIDDEN_RES:
        if rx.search(text):
            problems.append(f"forbidden pattern {rx.pattern!r} matched")
    data, docs = None, []
    try:
        data = json.loads(text)
        docs = [data]
    except ValueError:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        try:  # NDJSON（--facts）
            docs = [json.loads(ln) for ln in lines]
        except ValueError:
            docs = []
            for ln in lines:
                if not TEXT_LINE_RE.match(ln):
                    problems.append("non-allowlisted text line")
                    break

    def walk(x, where):
        if isinstance(x, dict):
            for k, v in x.items():
                if not any(r.match(k) for r in ALLOWED_STRING_RES):
                    problems.append(f"key not allowlisted at {where}")
                walk(v, where + "." + (k if len(k) < 40 else "?"))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{where}[{i}]")
        elif isinstance(x, str) and not any(r.match(x) for r in ALLOWED_STRING_RES):
            problems.append(f"string not allowlisted at {where}")

    for i, d in enumerate(docs):
        walk(d, "$" if len(docs) == 1 else f"$[{i}]")
    return problems


def self_check_file(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return check_text(f.read())


# ---------------------------------------------------------------------------
# 輸出
# ---------------------------------------------------------------------------
def _n(v):
    return "-" if v is None else f"{v:,}"


def render_text(rep: dict) -> str:
    t, c = rep["totals"], rep["coverage"]
    out = [f"ct-session-stats {rep['generator']['version']}  claude-code={','.join(rep['source']['claude_code_versions']) or '-'}",
           f"sessions={t['sessions']} worker={t['worker_sessions']} tower={t['tower_sessions']} "
           f"other={t['other_sessions']} workorders={t['workorders']}",
           f"coverage worker/all={c['share_of_sessions']} conflicts={c['conflicts']} "
           f"sources={' '.join(f'{k}:{v}' for k, v in c['worker_sources'].items()) or '-'}",
           "",
           "workorder  type  sess  input  output  cache_read  cache_write  sub_output  est_usd(估)  tools  fail  "
           "max_fail_10  stuck"]
    for w in rep["workorders"]:
        tk = w["tokens"]
        out.append("  ".join(str(x) for x in (
            w["workorder"], w["type"] or "-", w["sessions"], _n(tk["input"]), _n(tk["output"]), _n(tk["cache_read"]),
            _n(tk["cache_write"]), _n(w["subagent_tokens"]["output"]),
            "-" if w["est_usd"] is None else f"{w['est_usd']:.2f}", w["counts"].get("tool_calls", 0),
            w["counts"].get("failures", 0), w["stuck"].get("max_failures_in_10_calls", 0),
            "🔵" if w["stuck_signal"] else "-")))
    tu = rep["tower_usage"]
    out += ["", f"tower_usage (not allocated): sessions={tu['sessions']} output={_n(tu['tokens']['output'])} "
                f"cache_read={_n(tu['tokens']['cache_read'])} est_usd(估)="
                f"{'-' if tu['est_usd'] is None else format(tu['est_usd'], '.2f')}",
            f"other_usage: sessions={rep['other_usage']['sessions']} output={_n(rep['other_usage']['tokens']['output'])}",
            f"stuck_signals (🔵 max_failures_in_10_calls>={STUCK_THRESHOLD}): {', '.join(rep['stuck_signals']) or '-'}"]
    tbd = rep.get("tower_by_decision")
    if tbd:
        top = sorted(tbd["related"].items(), key=lambda x: (-x[1]["output"], x[0]))[:10]
        out += [f"tower_by_decision (估, direction=previous-to-this, not validated): decisions={tbd['decisions']} "
                f"share_output_related={tbd['share_output_related']} general_output={_n(tbd['general']['output'])} "
                f"after_last_output={_n(tbd['after_last']['output'])}",
                "  top: " + (", ".join(f"{k} {v['output']:,}" for k, v in top) or "-")]
    return "\n".join(out) + "\n"


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def _write_checked(path: str, text: str) -> list:
    probs = check_text(text)
    if probs:
        return probs
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return []


def emit(rep: dict, args, out=None, err=None) -> int:
    out = out or sys.stdout
    err = err or sys.stderr
    text = _dump(rep) if args.json else render_text(rep)
    probs = check_text(_dump(rep)) + ([] if args.json else check_text(text))
    if probs:
        for p in sorted(set(probs)):
            err.write(f"self-check FAIL {p}\n")
        err.write("self-check: FAIL — nothing written\n")
        return EXIT_PRIVACY
    snap_entries = None
    if args.snapshot_append:
        now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
        snap, a, r, k = snapshot_append(rep, args.snapshot_append, now)
        probs = _write_checked(args.snapshot_append, _dump(snap))
        if probs:
            err.write("self-check: FAIL — snapshot not written\n")
            return EXIT_PRIVACY
        err.write(f"snapshot: added={a} replaced={r} kept={k} workorders={len(snap['workorders'])}\n")
        snap_entries = snap["workorders"]
    if args.facts:
        entries = snap_entries if snap_entries is not None else \
            [{k: w[k] for k in SNAPSHOT_ENTRY_KEYS if k in w} for w in rep["workorders"]]
        facts = build_facts(entries)
        probs = _write_checked(args.facts, "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n"
                                                   for x in facts))
        if probs:
            err.write("self-check: FAIL — facts not written\n")
            return EXIT_PRIVACY
        err.write(f"facts: {len(facts)}\n")
    out.write(text)
    return EXIT_OK


def facts_from_snapshots(paths) -> list:
    entries = {}
    for p in paths:
        files = sorted(glob.glob(os.path.join(p, "*.json"))) if os.path.isdir(p) else [p]
        for fp in files:
            o = _load_snapshot(fp)
            for w in (o or {}).get("workorders", []):
                if isinstance(w, dict) and w.get("workorder") and w["workorder"] not in entries:
                    entries[w["workorder"]] = w
    return build_facts(list(entries.values()))


# ---------------------------------------------------------------------------
# 工具清單建議（--tools，v6.0.0-beta.12+，PLAN-006 S2／T0422）
# 規則權威：analysis-rules.md § 工具清單建議（`*insights tools`）。只出建議，🔴 不改任何設定。
# ---------------------------------------------------------------------------
TOOLS_DATA_DAYS_MIN = 14        # 資料天數門檻
TOOLS_LOADED_MIN = 20           # 載入 session 門檻
TOOLS_GROUP_USED_MIN = 3        # 規則 3「某類型在用」：單一組使用 session 數
TOOLS_CONSIDER_MAX_USED = 2     # consider：使用 session 上限
TOOLS_CONSIDER_MIN_IDLE = 14    # consider：最後使用距結束日天數下限
TOOLS_BUILTIN_RATE_MAX = 0.05   # 內建工具：使用率上限
TOOLS_BUILTIN_TOKENS_MIN = 500  # 內建工具：每輪 token 下限
# 核心內建工具：關掉後 CT 或 Claude Code 基本操作會壞，一律 keep（不進需使用者裁示區；T0423／D580）
TOOLS_CORE_BUILTIN = frozenset(("Skill", "ToolSearch", "Agent", "Task", "Read", "Write", "Edit", "Bash", "PowerShell",
                                "Grep", "Glob", "AskUserQuestion", "SendMessage", "ListAgents"))
TOOLS_MCP_FAIL_MIN_LOADED = 5
TOOLS_MCP_FAIL_RATE = 0.5
TOOLS_TRUNCATED_SHARE = 0.5
TOOLS_NEAR_CAP = 1500           # 清單長度 ≥ C − 1,500 算貼著上限
CHARS_PER_TOKEN = {"mid": 2.7, "low": 3.5, "high": 2.3}  # low／high 指 token 數的下／上緣
CT_SKILLS = frozenset(("control-tower", "control-tower-guide", "ct-exec", "ct-done", "ct-status", "ct-evolve",
                       "ct-insights", "ct-help", "ct-fieldguide"))
CT_PLUGINS = frozenset(("ct", "ct-guide"))
BUILTIN_MCP_INTEGRATIONS = frozenset(("claude-in-chrome",))
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.]+)?$")
GROUP_LABELS = {"tower": "tower", "other_ct_repo": "other(CT repo)", "non_ct": "non-CT"}
LEVER_LOCATIONS = ("project_settings", "project_settings_local", "project_mcp_json", "project_skills_dir",
                   "project_agents_dir", "user_settings", "user_claude_json", "user_claude_json_project",
                   "user_skills_dir", "user_agents_dir", "claude_ai_account", "none")
LOCATION_TEXT = {
    "project_settings": "`.claude/settings.json`", "project_settings_local": "`.claude/settings.local.json`",
    "project_mcp_json": "`.mcp.json`", "project_skills_dir": "`.claude/skills/<name>/`",
    "project_agents_dir": "專案的 agent 定義檔", "user_settings": "`~/.claude/settings.json`",
    "user_claude_json": "`~/.claude.json`", "user_claude_json_project": "`~/.claude.json` 該專案區",
    "user_skills_dir": "`~/.claude/skills/<name>/`", "user_agents_dir": "使用者層的 agent 定義檔",
    "claude_ai_account": "claude.ai 帳號設定", "none": "—"}
LAYER_TEXT = {"project": "專案", "user": "使用者", "claude_ai": "claude.ai 帳號", "builtin": "Claude Code 內建",
              "injected": "執行環境注入", "unknown": "不明"}
NOTE_TEXT = {
    "restart_session": "改完開新 session 生效",
    "undocumented_measured": "synced 適用 `skillOverrides` 為實測行為、文件未寫（CLI 2.1.316）",
    "full_prefix_name": "🔴 鍵一律用完整前綴名，裸名會先關到使用者層同名 skill",
    "hooks_stop_together": "關 plugin 會一起停掉 hook",
    "plugin_skill_no_overrides": "plugin skill 不吃 `skillOverrides`",
    "unverified": "未驗證",
    "synced_plugin_measured": "`enabledPlugins` 關 `@synced` plugin 為實測行為（CLI 2.1.316：plugin 的 skill 與 MCP 都移出清單）、文件未寫",
    "one_way": "單向：設了 `false` 之後沒有設定檔能再打開",
    "one_way_unverified": "`permissions.deny` 的單向性未驗證",
    "shared_tower_worker": "塔台與 Worker 共用專案設定，無法只關 Worker",
    "artifact_tower_too": "關掉後塔台也不能發 Artifact",
    "workflow_ct_orders": "CT 的 Workflow 授權工單無法執行",
    "schedule_loop": "`/loop` 自訂節奏無法使用",
    "impact_unassessed": "影響未評估",
    "confirm_after_apply": "套用後在互動 session 用 `/context` 或下一次 `*insights tools` 確認已移出清單",
    "listing_full": "清單滿載，主要效果是補回被截的說明",
    "has_duplicate": "另有同步副本，見另列問題",
    "short_data": "資料天數不足",
    "injected_lever": "目前只能在執行環境（例 BAT）處理",
    "integration_lever": "目前只能在 Claude Code 整合設定處理",
    "bundled_lever": "目前只能在使用者層用 `disableBundledSkills` 整批處理",
    "builtin_agent_lever": "Claude Code 內建 agent 類型，沒有經過驗證的逐項關閉手段",
    "unknown_layer": "層級不明，未出建議",
    "ct_skill": "CT 自己的 skill，直接讀檔使用計不到",
    "keep_arg": "`--keep` 指定",
    "core_tool": "核心工具：CT／Claude Code 運作必需",
    "local_service": "要用時開服務即可，不一定要移除",
}


def _ntok(chars, which="mid"):
    return int(round(chars / CHARS_PER_TOKEN[which])) if chars else 0


def _tok3(chars):
    return {k: _ntok(chars, k) for k in ("mid", "low", "high")}


def _norm_path(p):
    return os.path.normcase(os.path.normpath(os.path.abspath(os.path.expanduser(p)))) if p else None


def git_root(path, cache=None):
    """往上找 `.git`（目錄或 worktree 的檔案）；worktree 指回主 repo。找不到 → (原路徑, False)。不執行 git。"""
    if not path:
        return None, False
    key = _norm_path(path)
    if cache is not None and key in cache:
        return cache[key]
    p = os.path.abspath(os.path.expanduser(path))
    res = (p, False)
    cur = p
    while True:
        g = os.path.join(cur, ".git")
        if os.path.isdir(g):
            res = (cur, True)
            break
        if os.path.isfile(g):
            main = None
            try:
                with open(g, encoding="utf-8", errors="replace") as f:
                    line = f.readline().strip()
                if line.startswith("gitdir:"):
                    gd = line[7:].strip().replace("\\", "/")
                    if "/.git/worktrees/" in gd:
                        main = gd.split("/.git/worktrees/")[0]
            except OSError:
                pass
            res = (os.path.abspath(main) if main else cur, True)
            break
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    if cache is not None:
        cache[key] = res
    return res


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _skill_version(path):
    """SKILL.md 的版號：`<!-- <name>-version: X -->` 或 frontmatter `version`／`current_version`；不符樣式 → <unknown>。"""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(6000)
    except OSError:
        return None
    m = re.search(r"<!--\s*[A-Za-z0-9_.-]+-version:\s*([^\s>]+)", head)
    if not m:
        fm = head.split("\n---", 1)[0] if head.startswith("---") else ""
        m = re.search(r"^[ \t]*(?:current_version|version):\s*[\"']?([^\s\"']+)", fm, re.M)
    if not m:
        return "<unknown>"
    return m.group(1) if VERSION_RE.match(m.group(1)) else "<unknown>"


def _dir_names(path):
    try:
        return sorted(n for n in os.listdir(path) if not n.startswith(".") and os.path.isdir(os.path.join(path, n)))
    except OSError:
        return []


def _hook_events(plugin_dir):
    ev = set()
    for p in (os.path.join(plugin_dir, "hooks", "hooks.json"), os.path.join(plugin_dir, ".claude-plugin", "plugin.json")):
        d = _read_json(p)
        h = d.get("hooks") if isinstance(d, dict) else None
        if isinstance(h, dict):
            ev.update(k for k in h if isinstance(k, str) and re.match(r"^[A-Z][A-Za-z]{1,40}$", k))
    return sorted(ev)


def _settings_keys(path):
    d = _read_json(path)
    if not isinstance(d, dict):
        return None
    perm = d.get("permissions") if isinstance(d.get("permissions"), dict) else {}
    return {"enabledPlugins": {k: v for k, v in (d.get("enabledPlugins") or {}).items()
                               if isinstance(k, str) and isinstance(v, bool)}
            if isinstance(d.get("enabledPlugins"), dict) else {},
            "skillOverrides": {k: v for k, v in (d.get("skillOverrides") or {}).items()
                               if isinstance(k, str) and isinstance(v, str)}
            if isinstance(d.get("skillOverrides"), dict) else {},
            "syncClaudeAiSkills": d.get("syncClaudeAiSkills") if isinstance(d.get("syncClaudeAiSkills"), bool) else None,
            "enableArtifact": d.get("enableArtifact") if isinstance(d.get("enableArtifact"), bool) else None,
            "disableBundledSkills": bool(d.get("disableBundledSkills")),
            "deny_bare": sorted(x for x in (perm.get("deny") or []) if isinstance(x, str) and re.match(TOOL_NAME_RX, x))}


def load_user_config(claude_home, claude_json):
    """使用者層設定：只取鍵名、type、啟用狀態、版號、hook 事件名。"""
    home = os.path.expanduser(claude_home)
    cfg = {"readable": os.path.isdir(home), "settings": _settings_keys(os.path.join(home, "settings.json")),
           "user_skills": {}, "synced_skills": {}, "plugins": {}, "user_agents": set(),
           "user_mcp": set(), "projects_area": {}}
    sk = os.path.join(home, "skills")
    for n in _dir_names(sk):
        if n in ("synced",):
            continue
        cfg["user_skills"][n] = _skill_version(os.path.join(sk, n, "SKILL.md"))
    for bucket in _dir_names(os.path.join(sk, "synced")):
        for n in _dir_names(os.path.join(sk, "synced", bucket)):
            cfg["synced_skills"][n] = _skill_version(os.path.join(sk, "synced", bucket, n, "SKILL.md"))
    try:
        cfg["user_agents"] = {os.path.splitext(n)[0] for n in os.listdir(os.path.join(home, "agents")) if n.endswith(".md")}
    except OSError:
        pass
    ip = _read_json(os.path.join(home, "plugins", "installed_plugins.json"))
    for pid, insts in ((ip or {}).get("plugins") or {}).items() if isinstance(ip, dict) else ():
        if not isinstance(pid, str) or "@" not in pid or not isinstance(insts, list):
            continue
        name = pid.split("@", 1)[0]
        for inst in insts:
            if not isinstance(inst, dict):
                continue
            scope = inst.get("scope") if inst.get("scope") in ("user", "project", "local") else "user"
            ver = inst.get("version") if isinstance(inst.get("version"), str) and VERSION_RE.match(inst["version"]) else "<unknown>"
            pdir = inst.get("installPath") if isinstance(inst.get("installPath"), str) else ""
            cfg["plugins"].setdefault(name, {"id": pid, "layer": "project" if scope in ("project", "local") else "user",
                                             "synced": False, "version": ver,
                                             "hooks": _hook_events(pdir) if pdir else []})
    syn = os.path.join(home, "plugins", "synced")
    for bucket in _dir_names(syn):
        for d in _dir_names(os.path.join(syn, bucket)):
            pj = _read_json(os.path.join(syn, bucket, d, ".claude-plugin", "plugin.json"))
            if not isinstance(pj, dict) or not isinstance(pj.get("name"), str):
                continue
            name = pj["name"]
            if not re.match(r"^[A-Za-z0-9_.-]{1,64}$", name):
                continue
            ver = pj.get("version") if isinstance(pj.get("version"), str) and VERSION_RE.match(pj["version"]) else "<unknown>"
            cfg["plugins"].setdefault(name, {"id": name + "@synced", "layer": "claude_ai", "synced": True,
                                             "version": ver, "hooks": _hook_events(os.path.join(syn, bucket, d))})
    cj = _read_json(os.path.expanduser(claude_json))
    if isinstance(cj, dict):
        top = cj.get("mcpServers") if isinstance(cj.get("mcpServers"), dict) else {}
        cfg["user_mcp"] = {server_key(k) for k in top if server_key(k)}
        for path, area in (cj.get("projects") or {}).items() if isinstance(cj.get("projects"), dict) else ():
            if not isinstance(path, str) or not isinstance(area, dict):
                continue
            ms = area.get("mcpServers") if isinstance(area.get("mcpServers"), dict) else {}
            dis = area.get("disabledMcpServers") if isinstance(area.get("disabledMcpServers"), list) else []
            cfg["projects_area"][_norm_path(path)] = {"mcp": {server_key(k) for k in ms if server_key(k)},
                                                      "disabled": {server_key(k) for k in dis if server_key(k)}}
    cfg["claude_json_readable"] = isinstance(cj, dict)
    return cfg


def add_nested_skills(cfg, root, cwd, seen):
    """session 在 repo 的子目錄執行時，cwd 到 repo 根目錄之間各層的 `.claude/skills/` 也算這個 repo 的專案層。"""
    if not cwd:
        return
    key = _norm_path(cwd)
    if key in seen:
        return
    seen.add(key)
    rk = _norm_path(root)
    cur = os.path.abspath(cwd)
    for _ in range(12):
        ck = _norm_path(cur)
        if ck == rk or not ck.startswith(rk + os.sep):
            break
        sk = os.path.join(cur, ".claude", "skills")
        for n in _dir_names(sk):
            cfg["skills"].setdefault(n, _skill_version(os.path.join(sk, n, "SKILL.md")))
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent


def load_repo_config(root):
    """專案層：.mcp.json 鍵、.claude/settings*.json 的鍵、.claude/skills/*、.claude/agents/*（只取名稱與版號）。"""
    out = {"mcp": set(), "skills": {}, "agents": set(), "settings": None, "settings_local": None,
           "ct": os.path.isdir(os.path.join(root, "_ct-workorders"))}
    mj = _read_json(os.path.join(root, ".mcp.json"))
    if isinstance(mj, dict):
        ms = mj.get("mcpServers") if isinstance(mj.get("mcpServers"), dict) else {}
        out["mcp"] = {server_key(k) for k in ms if server_key(k)}
    sk = os.path.join(root, ".claude", "skills")
    for n in _dir_names(sk):
        out["skills"][n] = _skill_version(os.path.join(sk, n, "SKILL.md"))
    try:
        out["agents"] = {os.path.splitext(n)[0] for n in os.listdir(os.path.join(root, ".claude", "agents"))
                         if n.endswith(".md")}
    except OSError:
        pass
    out["settings"] = _settings_keys(os.path.join(root, ".claude", "settings.json"))
    out["settings_local"] = _settings_keys(os.path.join(root, ".claude", "settings.local.json"))
    return out


def read_codes_map(path):
    """既有代號對照（Markdown 表 `| P01 | <repo 目錄名> | …`）→ {目錄名小寫: [代號…]}（同名 repo 依表中順序）。只在記憶體內使用。"""
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^\|\s*(P\d{2,3})\s*\|\s*([^|]+?)\s*\|", line)
                if m:
                    name = m.group(2).strip().strip("`")
                    name = re.sub(r"^\(非\s*git\)\s*", "", name).strip().strip("`")
                    out.setdefault(name.lower(), []).append(m.group(1))
    except OSError:
        return None
    return out


def _local_date(t):
    return t.astimezone().date() if t else None


def _word_re(name):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", re.I)


class ToolsUsage:
    """跨 session 累計：每個項目（skill、mcp、agent、builtin_tool）的載入、使用、分組、字元。"""

    def __init__(self):
        self.items = {}       # (kind, name) → dict
        self.sessions = []    # 每個 session 的小 dict（清單公式用）
        self.cover = collections.Counter()
        self.by_group = collections.Counter()
        self.by_repo = collections.Counter()
        self.removed = 0
        self.ctx_tokens = 0
        self.ctx_requests = 0

    def item(self, kind, name):
        k = (kind, name)
        if k not in self.items:
            self.items[k] = {"kind": kind, "name": name, "loaded": 0, "failed": 0, "used": 0, "used_loaded": 0, "first_loaded": None,
                             "last_used": None, "calls": collections.Counter(), "by_group": {}, "chars": [],
                             "repos": set(), "loaded_repos": set(), "builtin_flag": False}
        return self.items[k]

    def _mark(self, it, group, start_date, repo, loaded=False, used=False):
        g = it["by_group"].setdefault(group, {"loaded": 0, "used": 0})
        if loaded:
            it["loaded"] += 1
            g["loaded"] += 1
            it["loaded_repos"].add(repo)
            if start_date and (it["first_loaded"] is None or start_date < it["first_loaded"]):
                it["first_loaded"] = start_date
        if used:
            it["used"] += 1
            g["used"] += 1
            it["repos"].add(repo)

    def add_session(self, m: Acc, group: str, repo: str):
        start_date = _local_date(m.ts_min)
        reqs = len(m.req)
        self.by_group[group] += 1
        self.by_repo[repo] += 1
        tk = m.tokens()
        self.ctx_tokens += tk["input"] + tk["cache_read"] + tk["cache_write"]
        self.ctx_requests += reqs
        li, mc, ag, sh = m.listing, m.mcp, m.agents, m.shape
        self.cover["sessions"] += 1
        self.cover["skill_listing"] += li["has"]
        self.cover["mcp_listing"] += mc["has"]
        self.cover["agent_listing"] += ag["has"]
        self.cover["tool_shape"] += sh["has"]
        self.removed += mc["removed"]
        # 使用（主 session；子代理不併，與 *insights sessions 的 skills_invoked 同一份程式）
        use = collections.defaultdict(lambda: [collections.Counter(), None])

        def touch(kind, name, how, ts):
            u = use[(kind, name)]
            u[0][how] += 1
            d = _local_date(ts)
            if d and (u[1] is None or d > u[1]):
                u[1] = d
        for c in m.tool_seq:
            ts = c.get("ts")
            name = c["name"]
            touch("builtin_tool", name, "tool", ts)
            if name.startswith("mcp__"):
                parts = name.split("__")
                touch("mcp", parts[1] if len(parts) > 2 and parts[1] else "<unknown>", "mcp", ts)
            if "skill" in c:
                touch("skill", c["skill"], "skill_tool", ts)
            if "agent" in c:
                touch("agent", c["agent"], "agent", ts)
        for n, ts in m.slash:
            if n in li["all"]:
                touch("skill", n, "slash", ts)
        # 載入
        loaded = set()
        if li["has"]:
            for n in li["all"]:
                loaded.add(("skill", n))
                self.item("skill", n)["chars"].append(li["len"].get(n, 0))
        mcp_loaded = set(mc["names"]) | set(mc["instr"]) | mc["failed"] | mc["pending"] | sh["mcp"]
        for s in mcp_loaded:
            loaded.add(("mcp", s))
            it = self.item("mcp", s)
            chars = sum(len(x) + 1 for x in mc["names"].get(s, ())) + mc["instr"].get(s, 0)
            it["chars"].append(chars)
            if s in mc["failed"]:
                it["failed"] += 1
        for a in ag["types"]:
            loaded.add(("agent", a))
            it = self.item("agent", a)
            if a in ag["builtin"]:
                it["builtin_flag"] = True
        for t, n in sh["tools"].items():
            loaded.add(("builtin_tool", t))
            self.item("builtin_tool", t)["chars"].append(n)
        for k in loaded:
            self._mark(self.item(*k), group, start_date, repo, loaded=True)
        for k, (cnt, last) in use.items():
            if k[0] == "builtin_tool" and k[1].startswith("mcp__"):
                continue
            it = self.item(*k)
            it["calls"].update(cnt)
            self._mark(it, group, start_date, repo, used=True)
            if k in loaded:
                it["used_loaded"] += 1  # 同一 session 也在載入分母內（內建工具 use_rate 的分子）
            if last and (it["last_used"] is None or last > it["last_used"]):
                it["last_used"] = last
        if li["has"]:
            self.sessions.append({"reqs": reqs, "L": li["initial_total"], "initial": set(li["initial"]),
                                  "len": dict(li["len"]), "bare": set(li["bare"]),
                                  "extra": set(li["all"]) - set(li["initial"]), "repo": repo})


def listing_saving(sessions, R, full_len, C):
    """§ 4.4：關掉一組 skill R 的每輪省下字元（依請求數加權平均）、最大值、可補回說明的筆數（平均）。"""
    w = tot = mx = 0
    restored = []
    for s in sessions:
        hit = R & (s["initial"] | s["extra"])
        if not hit:
            continue
        L = s["L"]
        cur = s["len"]
        expand = sum(max(0, full_len.get(n, 0) - cur.get(n, 0)) for n in s["bare"])
        demand = L + expand
        rm_init = R & s["initial"]
        removed_full = sum(cur.get(n, 0) if n not in s["bare"] else max(cur.get(n, 0), full_len.get(n, 0))
                           for n in rm_init)
        d2 = demand - removed_full
        save = max(0, L - min(C, d2)) if C else 0
        save += sum(cur.get(n, 0) for n in R & s["extra"])
        if d2 <= C:
            rest = len(s["bare"] - R)
        else:
            avail = sum(cur.get(n, 0) for n in rm_init)
            rest = 0
            for extra in sorted(max(0, full_len.get(n, 0) - cur.get(n, 0)) for n in s["bare"] - R):
                if extra > avail:
                    break
                avail -= extra
                rest += 1
        restored.append(rest)
        w += s["reqs"]
        tot += s["reqs"] * save
        mx = max(mx, save)
    avg = tot / w if w else 0.0
    return avg, mx, (int(round(sum(restored) / len(restored))) if restored else 0)


def _median(v):
    v = sorted(v)
    if not v:
        return 0
    n = len(v)
    return v[n // 2] if n % 2 else int(round((v[n // 2 - 1] + v[n // 2]) / 2))


class ToolsContext:
    """設定與 repo 的層級判定（§ 3.3）。"""

    def __init__(self, user_cfg, repo_cfgs, current, codes, other_names):
        self.u, self.repos, self.current, self.codes = user_cfg, repo_cfgs, current, codes
        self.other_res = [_word_re(n) for n in sorted(other_names) if n]
        self.listing_sessions = 0
        self.loaded_counts = {}

    def code(self, repo):
        return self.codes.get(repo, "<unknown>")

    def plugin_of(self, name):
        if ":" in name and not name.startswith("anthropic-skills:"):
            p = name.split(":", 1)[0]
            return p if p in self.u["plugins"] or p in CT_PLUGINS else ("?" + p)
        return None

    def mcp_plugin(self, s):
        if s.startswith("plugin_"):
            for p in sorted(self.u["plugins"], key=len, reverse=True):
                if s.startswith("plugin_" + p + "_"):
                    return p
            return "?"
        return None

    def skill_layer(self, name, loaded_repos):
        if name.startswith("anthropic-skills:"):
            return "claude_ai", "synced", []
        p = self.plugin_of(name)
        if p:
            if p.startswith("?"):
                return "unknown", "plugin_unknown", []
            pl = self.u["plugins"].get(p)
            return (pl["layer"] if pl else "user"), "plugin", []
        proj = sorted(r for r in loaded_repos if name in self.repos.get(r, {}).get("skills", {}))
        if self.current in proj:
            return "project", "project_current", proj
        if name in self.u["user_skills"]:  # 使用者層優先於其他 repo 的同名專案層（名稱是通用名稱）
            return "user", "user", []
        if proj:
            return "project", "project_other", proj
        if not self.u["readable"]:
            return "unknown", "config_unreadable", []
        if self.listing_sessions and self.loaded_counts.get(name, 0) >= 0.5 * self.listing_sessions:
            return "builtin", "bundled", []
        return "unknown", "unknown", []

    def mcp_layer(self, s, loaded_repos):
        if s.startswith("claude_ai_"):
            return "claude_ai", "connector", []
        p = self.mcp_plugin(s)
        if p:
            if p == "?":
                return "unknown", "plugin_unknown", []
            return self.u["plugins"][p]["layer"], "plugin", []
        proj = sorted(r for r in loaded_repos if s in self.repos.get(r, {}).get("mcp", set()))
        if self.current in proj:
            return "project", "project_current", proj
        if proj:
            return "project", "project_other", proj
        area = sorted(r for r in loaded_repos if s in self.u["projects_area"].get(_norm_path(r), {}).get("mcp", set()))
        if area:
            return "user", "user_project_area", area
        if s in self.u["user_mcp"]:
            return "user", "user", []
        if not self.u.get("claude_json_readable"):
            return "unknown", "config_unreadable", []
        if s in BUILTIN_MCP_INTEGRATIONS:
            return "builtin", "integration", []
        return "injected", "injected", []

    def agent_layer(self, a, it, loaded_repos):
        p = self.plugin_of(a) if ":" in a else None
        if p:
            if p.startswith("?"):
                return "unknown", "plugin_unknown", []
            return self.u["plugins"][p]["layer"] if p in self.u["plugins"] else "user", "plugin", []
        if it["builtin_flag"] or a == "<default>":
            return "builtin", "builtin_agent", []
        proj = sorted(r for r in loaded_repos if a in self.repos.get(r, {}).get("agents", set()))
        if self.current in proj:
            return "project", "project_current", proj
        if a in self.u["user_agents"]:
            return "user", "user", []
        if proj:
            return "project", "project_other", proj
        return "unknown", "unknown", []

    def generic(self, kind, name, it, detail):
        """可列名的通用名稱（§ 7.1）；其他 repo 的專案專屬名稱只給數量。"""
        if name.startswith("<"):
            return name in ("<default>",)
        # 設定檔認得的名稱（使用者層、同步、plugin、connector、目前 repo）一律是通用名稱
        if kind == "builtin_tool" or detail in ("synced", "plugin", "user", "project_current", "connector",
                                                 "user_project_area", "integration", "builtin_agent"):
            return True
        if any(r.search(name) for r in self.other_res):
            return False
        if detail in ("injected", "config_unreadable"):
            return True
        if kind == "mcp" and detail == "project_other":
            return True
        if kind == "skill" and name.startswith("bmad-"):
            return True
        if detail in ("bundled", "unknown", "plugin_unknown"):
            # 內建看起來的名稱：出現在目前 repo 或 ≥ 2 個 repo 的清單才列名（巢狀專案 skill 會像內建）
            return self.current in it["loaded_repos"] or len(it["loaded_repos"]) >= 2
        return False


def _lever(layer, location, key=None, entry=None, value=None, verified="documented", what=None):
    d = {"layer": layer, "location": location, "key": key, "entry": entry, "value": value, "verified": verified}
    if what:
        d["what"] = what
    return d


def lever_for(e, ctx):
    """§ 5.4：每項建議的層級、設定鍵或介面。回傳 (主要手段, 其他手段, notes)。"""
    kind, name, layer, detail = e["kind"], e["name"], e["layer"], e["layer_detail"]
    notes = []
    if e.get("plugin") and e["plugin"] in ctx.u["plugins"]:
        pl = ctx.u["plugins"][e["plugin"]]
        if pl["synced"]:
            prim = _lever("claude_ai", "claude_ai_account", verified="observed", what="plugin")
            alts = [_lever("project", "project_settings", "enabledPlugins", pl["id"], False, "measured")]
            notes.append("synced_plugin_measured")
        else:
            prim = _lever("project", "project_settings", "enabledPlugins", pl["id"], False)
            alts = [_lever("user", "user_settings", "enabledPlugins", pl["id"], False)]
        if pl["hooks"]:
            notes.append("hooks_stop_together")
        notes.append("plugin_skill_no_overrides")
        return prim, alts, notes
    if kind == "skill":
        if detail == "synced":
            return (_lever("project", "project_settings", "skillOverrides", name, "off", "measured"),
                    [_lever("user", "user_settings", "syncClaudeAiSkills", None, False),
                     _lever("claude_ai", "claude_ai_account", what="skills")], ["undocumented_measured", "full_prefix_name"])
        if detail == "user":
            return (_lever("project", "project_settings", "skillOverrides", name, "off", "measured"),
                    [_lever("user", "user_skills_dir", None, name, "remove")], [])
        if detail == "project_current":
            return (_lever("project", "project_settings", "skillOverrides", name, "off"),
                    [_lever("project", "project_skills_dir", None, name, "remove")], [])
    if kind == "mcp":
        if detail == "connector":
            return _lever("claude_ai", "claude_ai_account", verified="observed", what="mcp"), [], []
        if detail == "user":
            return (_lever("user", "user_claude_json", "mcpServers", name, "remove", "observed"),
                    [_lever("user", "user_claude_json_project", "disabledMcpServers", name, "add", "observed")], [])
        if detail == "user_project_area":
            return _lever("user", "user_claude_json_project", "mcpServers", name, "remove", "observed"), [], []
        if detail == "project_current":
            return _lever("project", "project_mcp_json", "mcpServers", name, "remove"), [], []
    if kind == "agent":
        if detail == "user":
            return _lever("user", "user_agents_dir", None, name, "remove", "unverified"), [], ["unverified"]
        if detail == "project_current":
            return _lever("project", "project_agents_dir", None, name, "remove", "unverified"), [], ["unverified"]
    if kind == "builtin_tool":
        if name == "Artifact":
            return (_lever("project", "project_settings", "enableArtifact", None, False),
                    [_lever("project", "project_settings", "permissions.deny", name, "add", "measured")],
                    ["one_way", "shared_tower_worker", "artifact_tower_too", "confirm_after_apply"])
        impact = {"Workflow": "workflow_ct_orders", "ScheduleWakeup": "schedule_loop"}.get(name, "impact_unassessed")
        return (_lever("project", "project_settings", "permissions.deny", name, "add", "measured"), [],
                ["one_way_unverified", "shared_tower_worker", impact, "confirm_after_apply"])
    return _lever(layer, "none", verified="unverified"), [], []


def build_tools_report(args, mutate=None) -> dict:
    """--tools：載入清單 × 使用次數 → 建議（§ 3～§ 6）。只讀、不改設定。"""
    projects_dir = os.path.expanduser(args.projects_dir)
    root_cache = {}
    current_root, _ = git_root(os.getcwd(), root_cache)
    current_key = _norm_path(current_root)
    if args.project:
        dirs = [os.path.join(projects_dir, p) for p in args.project]
    elif args.all_projects:
        dirs = [os.path.join(projects_dir, d) for d in _dir_names(projects_dir)]
    else:
        pre = encode_project(current_root)
        dirs = [os.path.join(projects_dir, d) for d in _dir_names(projects_dir) if d == pre or d.startswith(pre + "-")]
    dirs = [d for d in dirs if os.path.isdir(d)]
    if not dirs:
        raise Unavailable("project-dir-not-found")
    seen, files = set(), []
    for d in sorted(dirs):
        for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
            if os.path.basename(f) not in seen:
                seen.add(os.path.basename(f))
                files.append(f)
    files.sort(key=lambda f: (os.path.basename(f), f))
    if not files:
        raise Unavailable("no-session-files")
    since = _date_bound(args.since)
    until = _date_bound(args.until, end=True)
    if args.days and not since:
        since = (_dt.datetime.now().astimezone() - _dt.timedelta(days=args.days)).replace(
            hour=0, minute=0, second=0, microsecond=0)
    end_date = (until or _dt.datetime.now().astimezone()).astimezone().date()
    explicit = bool(args.project)
    # 一輪：分析 session → 依 cwd 找 repo（只在記憶體內）→ 歸屬 → 分組 → 累計；Acc 用完即丟（記憶體）
    roots, repo_cfgs, wo_cache = {}, {}, {}
    tu = ToolsUsage()
    for mp in files:
        s = analyse_session(mp, until=until, include_subagents=False, mutate=mutate)
        m = s["main"]
        if m.ts_min is None or (since and m.ts_min < since) or (until and m.ts_min > until):
            continue
        root, is_git = git_root(m.cwd, root_cache) if m.cwd else (os.path.dirname(mp), False)
        rkey = _norm_path(root)
        if explicit and not args.all_projects:
            rkey, root = current_key, current_root
        elif not args.all_projects and m.cwd and rkey != current_key:
            continue
        r = roots.setdefault(rkey, {"root": root, "n": 0, "first": None, "cwds": set(), "git": is_git})
        r["n"] += 1
        r["first"] = m.ts_min if r["first"] is None or m.ts_min < r["first"] else r["first"]
        if rkey not in repo_cfgs:
            repo_cfgs[rkey] = load_repo_config(root)
            wdir = args.workorders_dir if (rkey == current_key and args.workorders_dir) else (
                os.path.join(root, "_ct-workorders") if repo_cfgs[rkey]["ct"] else None)
            wo_cache[rkey] = (load_workorders(wdir), load_tower_sessions(wdir)) if wdir else (None, set())
        add_nested_skills(repo_cfgs[rkey], root, m.cwd, r["cwds"])
        wo_info, tower = wo_cache[rkey]
        if wo_info is None:
            group = "non_ct"
        else:
            att = resolve(s, wo_info, tower, None)
            if att["role"] == "tower":
                group = "tower"
            elif att["role"] == "worker":
                group = wo_info["types"].get(att["workorder"]) or "unknown"
            else:
                group = "other_ct_repo"
        tu.add_session(m, group, rkey)
        del s, m
    if not roots:
        raise Unavailable("no-sessions-in-period")
    # 代號（§ 7.2）：目前 repo 用本名，其他依 session 數 → 第一次 session 時間編 P01…；--codes-map 已存在時沿用
    if args.codes_map:
        cm = _norm_path(args.codes_map)
        for rk in [roots[k]["root"] for k in roots if roots[k]["git"]] + [current_root]:
            if cm == _norm_path(rk) or cm.startswith(_norm_path(rk) + os.sep):
                raise UsageError("codes-map-inside-scanned-repo")
    prior = read_codes_map(args.codes_map) if args.codes_map and os.path.exists(args.codes_map) else None
    codes, used_codes = {}, set()
    cur_name = os.path.basename(current_root.rstrip("/\\")) or "<current>"
    cur_label = cur_name if re.match(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$", cur_name) else "<current>"
    codes[current_key] = cur_label
    order = sorted((k for k in roots if k != current_key), key=lambda k: (-roots[k]["n"], roots[k]["first"]))
    for k in order if prior else ():  # 同名 repo：依 session 數順序取表中的代號
        cs = [c for c in prior.get(os.path.basename(roots[k]["root"].rstrip("/\\")).lower(), []) if c not in used_codes]
        if cs:
            codes[k] = cs[0]
            used_codes.add(cs[0])
    nxt = 1
    for k in order:
        if k in codes:
            continue
        while "P%02d" % nxt in used_codes:
            nxt += 1
        codes[k] = "P%02d" % nxt
        used_codes.add(codes[k])
    # 其他 repo 名稱只取 git repo（非 git 的工作目錄仍編代號，但目錄名不當 repo 名稱比對）
    other_names = {os.path.basename(roots[k]["root"].rstrip("/\\")) for k in roots if k != current_key and roots[k]["git"]}
    user_cfg = load_user_config(args.claude_home, args.claude_json)
    if current_key not in repo_cfgs:
        repo_cfgs[current_key] = load_repo_config(current_root)
    ctx = ToolsContext(user_cfg, repo_cfgs, current_key, codes, other_names)
    if args.codes_map and not os.path.exists(args.codes_map):
        write_codes_map(args.codes_map, roots, codes, repo_cfgs, current_key, since, until)
    rep = assemble_tools(tu, ctx, args, since, until, end_date, roots)
    # 其他 repo 名稱（只在記憶體內給 Markdown 自檢 ⑥ 用；輸出前移除）。和列出的通用名稱撞名的（例：在某個 skill 目錄裡
    # 開的非 git session，工作目錄名就是 skill 名）無法和通用名稱區分，不列入 ⑥，只計數
    listed = [e["name"] for e in rep["items"]] + [p["name"] for p in rep["plugins"]]
    exempt = {n for n in other_names if any(_word_re(n).search(x) for x in listed)}
    rep["privacy"] = {"other_repo_names": len(other_names), "exempt_colliding_with_generic": len(exempt)}
    rep["_other_names"] = sorted(other_names - exempt)
    if prior is not None:
        missing = sum(1 for k in order if codes[k] not in {c for v in prior.values() for c in v})
        if missing:
            sys.stderr.write(f"codes-map: {missing} repo(s) not in the existing map got new codes (map not rewritten)\n")
    return rep


class UsageError(Exception):
    pass


def write_codes_map(path, roots, codes, repo_cfgs, current_key, since, until):
    """代號對照：只寫在所有被掃 repo 之外（呼叫前已檢查）；不進任何 repo。"""
    lines = ["# 專案代號對照（repo 外，不得進版控）", "",
             f"> 產生時間：{_dt.datetime.now().astimezone().isoformat(timespec='seconds')}；"
             f"期間 {iso(since) or '-'}～{iso(until) or '-'}；ct-session-stats {GENERATOR_VERSION}", "",
             "| 代號 | repo 目錄名（或工作目錄名） | 有 _ct-workorders | 期間 session 數 |", "|---|---|---|---|"]
    for k in sorted(roots, key=lambda k: (codes[k] != codes.get(current_key), codes[k])):
        lines.append(f"| {codes[k]} | {os.path.basename(roots[k]['root'].rstrip(chr(47) + chr(92)))} | "
                     f"{'是' if repo_cfgs[k]['ct'] else '否'} | {roots[k]['n']} |")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def _is_keep(name, plugin, keep):
    base = name.split(":", 1)[1] if plugin and ":" in name else name
    if plugin in CT_PLUGINS:
        return "ct_skill"
    if not name.startswith("anthropic-skills:") and (name in CT_SKILLS or name.startswith("ct-adapter-")):
        return "ct_skill"
    if name in keep or base in keep or (plugin and plugin in keep):
        return "keep_arg"
    return None


def _no_lever_note(e):
    if e["layer"] == "injected":
        return "injected_lever"
    if e["layer"] == "unknown":
        return "unknown_layer"
    return {"bundled": "bundled_lever", "integration": "integration_lever",
            "builtin_agent": "builtin_agent_lever"}.get(e["layer_detail"], "unknown_layer")


def assemble_tools(tu: ToolsUsage, ctx: ToolsContext, args, since, until, end_date, roots) -> dict:
    keep = set(args.keep or ())
    th = {"data_days": TOOLS_DATA_DAYS_MIN, "loaded_sessions": TOOLS_LOADED_MIN,
          "group_used_sessions": TOOLS_GROUP_USED_MIN, "consider_max_used": TOOLS_CONSIDER_MAX_USED,
          "consider_min_idle_days": TOOLS_CONSIDER_MIN_IDLE, "builtin_rate_max": TOOLS_BUILTIN_RATE_MAX,
          "builtin_tokens_min": TOOLS_BUILTIN_TOKENS_MIN, "chars_per_token": dict(CHARS_PER_TOKEN)}
    C = max((s["L"] for s in tu.sessions), default=0)
    ctx.listing_sessions = len(tu.sessions)
    ctx.loaded_counts = {name: it["loaded"] for (kind, name), it in tu.items.items() if kind == "skill"}
    th["listing_cap_chars"] = C
    th["listing_near_cap_chars"] = max(0, C - TOOLS_NEAR_CAP)
    full_len = collections.Counter()
    for s in tu.sessions:
        for n, v in s["len"].items():
            full_len[n] = max(full_len[n], v)
    near = [s for s in tu.sessions if C and s["L"] >= C - TOOLS_NEAR_CAP]
    items, hidden = [], collections.Counter()
    hidden_used = collections.Counter()
    for (kind, name), it in sorted(tu.items.items()):
        if it["loaded"] == 0 and kind == "builtin_tool":
            continue  # 沒有 schema 紀錄的工具（deferred 或舊 session）：每輪不送 schema，不列
        if kind == "skill":
            layer, detail, prepos = ctx.skill_layer(name, it["loaded_repos"] | it["repos"])
        elif kind == "mcp":
            layer, detail, prepos = ctx.mcp_layer(name, it["loaded_repos"] | it["repos"])
        elif kind == "agent":
            layer, detail, prepos = ctx.agent_layer(name, it, it["loaded_repos"] | it["repos"])
        else:
            layer, detail, prepos = "builtin", "builtin_tool", []
        if not ctx.generic(kind, name, it, detail):
            hidden[kind] += 1
            hidden_used[kind] += 1 if it["used"] else 0
            continue
        plugin = None
        if kind in ("skill", "agent") and detail in ("plugin",):
            plugin = name.split(":", 1)[0]
        if kind == "mcp" and detail == "plugin":
            plugin = ctx.mcp_plugin(name)
        if kind == "skill" and name.split(":", 1)[0] in CT_PLUGINS and ":" in name:
            plugin = name.split(":", 1)[0]
        chars = (sum(it["chars"]) / len(it["chars"])) if it["chars"] else 0.0
        fl = it["first_loaded"]
        data_days = (end_date - fl).days + 1 if fl else 0
        lu = it["last_used"]
        unused = data_days if not it["used"] else ((end_date - lu).days if lu else None)
        e = {"kind": kind, "name": name, "plugin": plugin, "layer": layer, "layer_detail": detail,
             "repo_codes": sorted(ctx.code(r) for r in prepos) if prepos and detail == "project_other" else [],
             "version": None, "loaded_sessions": it["loaded"], "failed_sessions": it["failed"],
             "used_sessions": it["used"],
             "calls": {k: int(it["calls"].get(k, 0)) for k in ("skill_tool", "slash", "agent", "mcp", "tool")},
             "first_loaded": fl.isoformat() if fl else None, "last_used": lu.isoformat() if lu else None,
             "data_days": data_days, "unused_days": unused,
             "by_group": {g: dict(v) for g, v in sorted(it["by_group"].items())},
             "chars_per_turn": int(round(chars)), "tokens_per_turn": _tok3(chars),
             "in_use_groups": sorted(g for g, v in it["by_group"].items() if v["used"] >= TOOLS_GROUP_USED_MIN),
             "notes": []}
        if kind == "skill":
            if detail == "synced":
                e["version"] = ctx.u["synced_skills"].get(name.split(":", 1)[1])
            elif detail == "user":
                e["version"] = ctx.u["user_skills"].get(name)
            elif detail == "project_current":
                e["version"] = ctx.repos[ctx.current]["skills"].get(name)
        if plugin and plugin in ctx.u["plugins"]:
            e["version"] = ctx.u["plugins"][plugin]["version"]
        items.append(e)
    # 重複 skill（§ 5.5）
    by_name = {(e["kind"], e["name"]): e for e in items}
    issues = []
    dup_close = set()
    for e in items:
        if e["kind"] != "skill" or e["layer_detail"] not in ("user", "project_current"):
            continue
        syn = by_name.get(("skill", "anthropic-skills:" + e["name"]))
        if not syn:
            continue
        v_this = e["version"]
        v_syn = syn["version"]
        mism = bool(v_this and v_syn and "<unknown>" not in (v_this, v_syn) and v_this != v_syn)
        close = syn["name"]
        if syn["used_sessions"] > e["used_sessions"] and not _is_keep(e["name"], None, keep):
            close = e["name"]
        dup_close.add(close)
        issues.append({"kind": "duplicate", "names": [e["name"], syn["name"]],
                       "layers": {e["name"]: e["layer"], syn["name"]: "claude_ai"},
                       "versions": {e["name"]: v_this or "<unknown>", syn["name"]: v_syn or "<unknown>"},
                       "version_mismatch": mism,
                       "used_sessions": {e["name"]: e["used_sessions"], syn["name"]: syn["used_sessions"]},
                       "synced_chars_per_turn": syn["chars_per_turn"], "close": close})
        e["notes"].append("has_duplicate")
    # 判定（§ 5.1；優先序：keep → other_repo → in_use_by_type → no_lever → duplicate → insufficient_data → recommend → consider）
    for e in items:
        kind = e["kind"]
        e["lever"], e["lever_alternatives"] = None, []
        if kind == "builtin_tool":
            # 分子只計同時在載入分母內的使用 session（沒有 api-request-shape 附件的 session 不進分子），
            # 所以 use_rate ≤ 1；used_sessions 照舊是使用 session 總數
            rate = tu.items[(kind, e["name"])]["used_loaded"] / e["loaded_sessions"] if e["loaded_sessions"] else 0.0
            e["use_rate"] = round(rate, 4)
            if e["name"] in TOOLS_CORE_BUILTIN:
                e["verdict"] = "keep"
                e["notes"].append("core_tool")
            elif e["loaded_sessions"] and rate < TOOLS_BUILTIN_RATE_MAX and e["tokens_per_turn"]["mid"] >= TOOLS_BUILTIN_TOKENS_MIN:
                e["verdict"] = "needs_user_decision"
                prim, alts, notes = lever_for(e, ctx)
                e["lever"], e["lever_alternatives"] = prim, alts
                e["notes"] += notes + ["restart_session"]
            else:
                e["verdict"] = "no_action"
            e["saving_per_turn"] = dict(e["tokens_per_turn"]) if e["verdict"] == "needs_user_decision" else _tok3(0)
            continue
        k = _is_keep(e["name"], e["plugin"], keep)
        if k:
            e["verdict"] = "keep"
            e["notes"].append(k)
        elif e["layer_detail"] == "project_other":
            e["verdict"] = "other_repo"
        elif e["in_use_groups"]:
            e["verdict"] = "in_use_by_type"
            if e["layer"] in ("injected", "builtin", "unknown"):
                e["notes"].append(_no_lever_note(e))
        elif e["layer"] in ("injected", "builtin", "unknown"):
            e["verdict"] = "no_lever"
            e["notes"].append(_no_lever_note(e))
        elif e["kind"] == "mcp" and e["loaded_sessions"] >= TOOLS_MCP_FAIL_MIN_LOADED and \
                e["failed_sessions"] / e["loaded_sessions"] >= TOOLS_MCP_FAIL_RATE:
            e["verdict"] = "connection_failed"  # 另列問題處理，不進建議表
        elif e["name"] in dup_close:
            e["verdict"] = "duplicate"
        elif e["data_days"] < TOOLS_DATA_DAYS_MIN or e["loaded_sessions"] < TOOLS_LOADED_MIN:
            e["verdict"] = "insufficient_data"
        elif e["used_sessions"] == 0:
            e["verdict"] = "recommend"
        elif e["used_sessions"] <= TOOLS_CONSIDER_MAX_USED and (e["unused_days"] or 0) >= TOOLS_CONSIDER_MIN_IDLE:
            e["verdict"] = "consider"
        else:
            e["verdict"] = "no_action"
        if e["verdict"] in ("recommend", "consider", "duplicate"):
            prim, alts, notes = lever_for(e, ctx)
            e["lever"], e["lever_alternatives"] = prim, alts
            e["notes"] += [n for n in notes if n not in e["notes"]] + ["restart_session"]
        if kind == "skill":
            avg, mx, rest = listing_saving(tu.sessions, {e["name"]}, full_len, C)
            e["saving_per_turn"] = _tok3(avg)
            e["saving_max_chars"] = mx
            e["restored_descriptions"] = rest
        elif kind == "mcp":
            e["saving_per_turn"] = dict(e["tokens_per_turn"])
        else:
            e["saving_per_turn"] = _tok3(0)
    # plugin 彙總（§ 5.4 plugin 列：整個 plugin 一起關）
    plugins = []
    for p in sorted({e["plugin"] for e in items if e["plugin"]}):
        comps = [e for e in items if e["plugin"] == p]
        pl = ctx.u["plugins"].get(p)
        verdicts = {e["verdict"] for e in comps}
        loaded = max((e["loaded_sessions"] for e in comps), default=0)
        used = max((e["used_sessions"] for e in comps), default=0)
        groups = sorted({g for e in comps for g in e["in_use_groups"]})
        if "keep" in verdicts:
            v = "keep"
        elif groups:
            v = "in_use_by_type"
        elif any(e["used_sessions"] for e in comps):
            v = "consider" if verdicts <= {"consider", "recommend"} and "consider" in verdicts else "no_action"
        elif verdicts <= {"recommend"}:
            v = "recommend"
        elif "insufficient_data" in verdicts:
            v = "insufficient_data"
        elif "no_lever" in verdicts:
            v = "no_lever"
        else:
            v = sorted(verdicts)[0]
        sk = {e["name"] for e in comps if e["kind"] == "skill"}
        s_avg, s_max, s_rest = listing_saving(tu.sessions, sk, full_len, C) if sk else (0.0, 0, 0)
        mcp_mid = sum(e["chars_per_turn"] for e in comps if e["kind"] == "mcp")
        pe = {"kind": "plugin", "name": p, "plugin": p, "id": pl["id"] if pl else None,
              "layer": pl["layer"] if pl else "unknown", "layer_detail": "synced_plugin" if pl and pl["synced"] else "plugin",
              "version": pl["version"] if pl else None, "hooks": pl["hooks"] if pl else [],
              "components": {"skill": sorted(sk), "mcp": sorted(e["name"] for e in comps if e["kind"] == "mcp"),
                             "agent": sorted(e["name"] for e in comps if e["kind"] == "agent")},
              "loaded_sessions": loaded, "used_sessions": used,
              "calls": {k: sum(e["calls"][k] for e in comps) for k in ("skill_tool", "slash", "agent", "mcp", "tool")},
              "last_used": max((e["last_used"] for e in comps if e["last_used"]), default=None),
              "data_days": max((e["data_days"] for e in comps), default=0),
              "in_use_groups": groups, "verdict": v,
              "by_group": {g: {"loaded": max(e["by_group"].get(g, {}).get("loaded", 0) for e in comps),
                               "used": max(e["by_group"].get(g, {}).get("used", 0) for e in comps)}
                           for g in sorted({g for e in comps for g in e["by_group"]})},
              "tokens_per_turn": {k: sum(e["tokens_per_turn"][k] for e in comps) for k in ("mid", "low", "high")},
              "saving_per_turn": {k: _ntok(mcp_mid, k) + _ntok(s_avg, k) for k in ("mid", "low", "high")},
              "saving_detail": {"mcp_tokens": _tok3(mcp_mid), "skill_tokens": _tok3(s_avg),
                                "skill_max_tokens": _ntok(s_max), "restored_descriptions": s_rest},
              "notes": [], "lever": None, "lever_alternatives": []}
        if v in ("recommend", "consider") and pl:
            prim, alts, notes = lever_for(dict(pe, kind="skill"), ctx)
            pe["lever"], pe["lever_alternatives"] = prim, alts
            pe["notes"] = notes + ["restart_session"]
        for e in comps:
            e["plugin_verdict"] = v
        plugins.append(pe)
    # 另列問題：連線失敗的 MCP、清單被截
    for e in items:
        if e["kind"] == "mcp" and e["loaded_sessions"] >= TOOLS_MCP_FAIL_MIN_LOADED and \
                e["failed_sessions"] / e["loaded_sessions"] >= TOOLS_MCP_FAIL_RATE:
            prim, alts, _ = lever_for(e, ctx) if e["layer_detail"] in ("user", "user_project_area", "project_current",
                                                                        "connector") else (None, [], [])
            issues.append({"kind": "mcp_failure", "names": [e["name"]], "layer": e["layer"],
                           "layer_detail": e["layer_detail"], "repo_codes": e["repo_codes"],
                           "loaded_sessions": e["loaded_sessions"], "failed_sessions": e["failed_sessions"],
                           "failure_rate": round(e["failed_sessions"] / e["loaded_sessions"], 4),
                           "lever": prim, "lever_alternatives": alts, "notes": ["local_service"]})
    share = len(near) / len(tu.sessions) if tu.sessions else 0.0
    names_only_med = _median([len(s["bare"]) for s in near]) if near else 0
    trunc = collections.Counter(n for s in near for n in s["bare"])
    generic_names = {e["name"] for e in items if e["kind"] == "skill"}
    top_trunc = [[n, c] for n, c in sorted(trunc.items(), key=lambda x: (-x[1], x[0])) if n in generic_names][:8]
    listing = {"sessions": len(tu.sessions), "near_cap_sessions": len(near), "near_cap_share": round(share, 4),
               "names_only_median": names_only_med}
    if tu.sessions and share >= TOOLS_TRUNCATED_SHARE:
        issues.append({"kind": "listing_truncated", "names": [n for n, _ in top_trunc], "near_cap_share": round(share, 4),
                       "near_cap_sessions": len(near), "sessions": len(tu.sessions), "names_only_median": names_only_med,
                       "top_truncated": top_trunc,
                       "project_specific_truncated": len([n for n in trunc if n not in generic_names])})
    # 合計（摘要用）：建議停用的 MCP 每輪 token 相加；skill 用清單公式算整組
    rec_items = [e for e in items if e["verdict"] == "recommend" and not e.get("plugin")]
    rec_plugins = [p for p in plugins if p["verdict"] == "recommend"]
    mcp_chars = sum(e["chars_per_turn"] for e in rec_items if e["kind"] == "mcp") + \
        sum(e["chars_per_turn"] for p in rec_plugins for e in items if e["plugin"] == p["name"] and e["kind"] == "mcp")
    R = {e["name"] for e in rec_items if e["kind"] == "skill"} | \
        {n for p in rec_plugins for n in p["components"]["skill"]}
    s_avg, s_max, s_rest = listing_saving(tu.sessions, R, full_len, C) if R else (0.0, 0, 0)
    summary = {"recommend_items": len(rec_items) + len(rec_plugins),
               "consider_items": len([e for e in items if e["verdict"] == "consider" and not e.get("plugin")]) +
               len([p for p in plugins if p["verdict"] == "consider"]),
               "needs_user_decision": len([e for e in items if e["verdict"] == "needs_user_decision"]),
               "issues": len(issues), "mcp_saving_tokens": _tok3(mcp_chars),
               "skill_saving_tokens": _tok3(s_avg), "skill_saving_max_tokens": _ntok(s_max),
               "skill_restored_descriptions": s_rest,
               "avg_context_tokens": int(round(tu.ctx_tokens / tu.ctx_requests)) if tu.ctx_requests else 0}
    data_days_max = max((e["data_days"] for e in items), default=0)
    row_savings = {}
    for e in items:
        if e["kind"] == "skill" and e["verdict"] in ("recommend", "consider") and not e.get("plugin"):
            row_savings.setdefault(e["verdict"] + ":skill:" + e["layer_detail"], set()).add(e["name"])
    for k, names in list(row_savings.items()):
        avg, mx, rest = listing_saving(tu.sessions, names, full_len, C)
        row_savings[k] = {"tokens": _tok3(avg), "max_tokens": _ntok(mx), "restored_descriptions": rest}
    rep = {
        "schema": TOOLS_SCHEMA,
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": {"script": SCRIPT_NAME, "version": GENERATOR_VERSION},
        "period": {"since": iso(since), "until": iso(until),
                   "start_date": since.astimezone().date().isoformat() if since else None,
                   "end_date": end_date.isoformat(), "data_days_max": data_days_max},
        "row_savings": row_savings,
        "scope": {"all_projects": bool(args.all_projects), "projects": sorted(set(ctx.codes.values())),
                  "sessions": tu.cover["sessions"], "by_group": dict(sorted(tu.by_group.items())),
                  "by_project": {ctx.code(k): v for k, v in sorted(tu.by_repo.items(), key=lambda x: ctx.code(x[0]))}},
        "coverage": {k: tu.cover[k] for k in ("skill_listing", "mcp_listing", "agent_listing", "tool_shape")},
        "thresholds": th,
        "listing": listing,
        "summary": summary,
        "removed_entries": tu.removed,
        "project_specific": {"skill": hidden["skill"], "mcp": hidden["mcp"], "agent": hidden["agent"],
                             "used": sum(hidden_used.values())},
        "items": items,
        "plugins": plugins,
        "issues": issues,
    }
    return rep


# ---------------------------------------------------------------------------
# 工具清單建議：Markdown 輸出（由已通過 JSON 自檢的資料＋固定句型產生）
# ---------------------------------------------------------------------------
def _g(group):
    return GROUP_LABELS.get(group, group)


def _tk(t):
    return f"≈{t['mid']:,}（{t['low']:,}～{t['high']:,}）"


def _lever_text(lv):
    if not lv:
        return "—"
    loc = LOCATION_TEXT.get(lv["location"], lv["location"])
    layer = LAYER_TEXT.get(lv["layer"], lv["layer"])
    if lv["location"] == "claude_ai_account":
        what = {"mcp": "connector", "plugin": "plugin", "skill": "skills"}.get(lv.get("what"), "")
        return f"claude.ai 帳號的 {what} 設定" if what else "claude.ai 帳號設定"
    if lv["location"] in ("user_skills_dir", "project_skills_dir"):
        return f"{layer}：移除 {loc}"
    if lv["location"] in ("user_agents_dir", "project_agents_dir"):
        return f"{layer}：移除{loc}（未驗證）"
    if lv["key"] == "skillOverrides":
        return f"{layer}：{loc} → `skillOverrides` → `\"{lv['entry']}\": \"off\"`（要保留名稱用 `\"name-only\"`）"
    if lv["key"] == "enabledPlugins":
        v = {"unverified": "（未驗證）", "measured": "（實測）"}.get(lv["verified"], "")
        return f"{layer}：{loc} → `enabledPlugins` → `\"{lv['entry']}\": false`{v}"
    if lv["key"] == "syncClaudeAiSkills":
        return f"{layer}（所有專案都不要）：{loc} → `syncClaudeAiSkills: false`"
    if lv["key"] == "enableArtifact":
        return f"{layer}：{loc} → `\"enableArtifact\": false`"
    if lv["key"] == "permissions.deny":
        return f"{layer}：{loc} → `permissions.deny: [\"{lv['entry']}\"]`（裸工具名）"
    if lv["key"] == "mcpServers":
        how = "介面 `/mcp` 或 `claude mcp remove` 使用者範圍" if lv["location"] == "user_claude_json" else "介面 `/mcp`"
        return f"{layer}：{loc} → `mcpServers` 移除 `{lv['entry']}`（{how}）"
    if lv["key"] == "disabledMcpServers":
        return f"{layer}（只在某專案停用）：{loc} → `disabledMcpServers` 加 `{lv['entry']}`（介面 `/mcp`）"
    return f"{layer}：{loc}"


def _notes_text(notes):
    seen, out = set(), []
    for n in notes:
        if n in seen or n == "restart_session":
            continue
        seen.add(n)
        out.append(NOTE_TEXT.get(n, n))
    return "；".join(out)


def _usage_text(e):
    t = f"{e['used_sessions']:,}／{e['loaded_sessions']:,} session"
    calls = sum(e["calls"].values()) if isinstance(e.get("calls"), dict) else 0
    if calls:
        t += f"、{calls:,} 次"
    if e.get("last_used"):
        t += f"、最後 {e['last_used']}"
    if e.get("by_group") and e["used_sessions"]:
        top = sorted(((g, v["used"]) for g, v in e["by_group"].items() if v["used"]),
                     key=lambda x: (-x[1], x[0]))[:3]
        t += "（" + "、".join(f"{_g(g)} {n}" for g, n in top) + "）"
    return t


def _rows(rep):
    """建議表的列：plugin 各一列；其他依（種類、層級、判定）合成一列。"""
    items = [e for e in rep["items"] if e["verdict"] in ("recommend", "consider") and not e.get("plugin")]
    rows = []
    for p in rep["plugins"]:
        if p["verdict"] in ("recommend", "consider"):
            comp = p["components"]
            parts = [f"{k} {len(v)}" for k, v in (("skill", comp["skill"]), ("MCP", comp["mcp"]),
                                                  ("agent", comp["agent"])) if v]
            notes = list(p["notes"])
            if p["data_days"] < 21:
                notes.append(f"資料 {p['data_days']} 天")
            hook = f"：{'、'.join('`' + h + '`' for h in p['hooks'])}" if p["hooks"] else ""
            note_txt = _notes_text(notes).replace(NOTE_TEXT["hooks_stop_together"], NOTE_TEXT["hooks_stop_together"] + hook)
            sd = p["saving_detail"]
            sav = []
            if comp["mcp"]:
                sav.append("MCP " + _tk(sd["mcp_tokens"]))
            if comp["skill"]:
                sav.append(f"skill {_tk(sd['skill_tokens'])}（清單公式）")
            rows.append({"verdict": p["verdict"], "n": 1, "mid": p["saving_per_turn"]["mid"],
                         "item": f"`{p['name']}`（plugin，{'、'.join(parts) or '無元件'}）",
                         "layer": LAYER_TEXT.get(p["layer"], p["layer"]) + ("（`@synced`）" if p["layer_detail"] == "synced_plugin" else ""),
                         "lever": "；或 ".join(_lever_text(x) for x in [p["lever"]] + p["lever_alternatives"] if x),
                         "usage": ("**可考慮**：" if p["verdict"] == "consider" else "") + _usage_text(p),
                         "saving": "＋".join(sav) or "≈0", "notes": note_txt})
    groups = collections.OrderedDict()
    for e in sorted(items, key=lambda e: (e["verdict"], e["kind"], e["layer_detail"], e["name"])):
        key = (e["verdict"], e["kind"], e["layer_detail"])
        groups.setdefault(key, []).append(e)
    for (verdict, kind, _), es in groups.items():
        e0 = es[0]
        names = "、".join(f"`{e['name']}`" for e in es)
        label = {"skill": "skill", "mcp": "MCP", "agent": "agent"}.get(kind, kind)
        if e0["layer_detail"] == "connector":
            label = "connector"
        item = (f"{len(es)} 個 {label}（{names}）" if len(es) > 3 else f"{names}（{label}）")
        rs = rep.get("row_savings", {}).get(f"{verdict}:{kind}:{e0['layer_detail']}")
        if kind == "skill":
            t = rs["tokens"] if rs else e0["saving_per_turn"]
            rest = rs["restored_descriptions"] if rs else e0.get("restored_descriptions", 0)
            mid = t["mid"]
            sav = ("≈0（清單滿載，說明補回約 %d 筆）" % rest) if mid == 0 else \
                _tk(t) + f"（清單公式{'，整組' if len(es) > 1 else ''}；說明補回約 {rest} 筆）"
        else:
            mid = sum(e["saving_per_turn"]["mid"] for e in es)
            sav = _tk({k: sum(e["saving_per_turn"][k] for e in es) for k in ("mid", "low", "high")})
        lv = [e0["lever"]] + e0["lever_alternatives"]
        lever = "；或 ".join(_lever_text(x) for x in lv if x)
        if len(es) > 1:
            lever = lever.replace(f"`{e0['name']}`", "`<name>`").replace(f"\"{e0['name']}\"", "\"<name>\"")
        notes = list(e0["notes"])
        if min(e["data_days"] for e in es) < 21:
            notes.append(f"資料 {min(e['data_days'] for e in es)} 天起")
        usage = (f"0／{max(e['loaded_sessions'] for e in es):,} session" if verdict == "recommend"
                 else "**可考慮**：" + "；".join((f"`{e['name']}` " if len(es) > 1 else "") + _usage_text(e) for e in es))
        rows.append({"verdict": verdict, "n": len(es), "mid": mid, "item": item,
                     "layer": LAYER_TEXT.get(e0["layer"], e0["layer"]), "lever": lever, "usage": usage,
                     "saving": sav, "notes": _notes_text(notes)})
    rows.sort(key=lambda r: (r["verdict"] != "recommend", -r["mid"], r["item"]))
    return rows


def render_tools_md(rep: dict) -> str:
    sc, su, li, th = rep["scope"], rep["summary"], rep["listing"], rep["thresholds"]
    per = rep["period"]
    since = per.get("start_date") or "-"
    scope = (f"跨 repo {len(sc['projects'])} 個代號（本 repo＋其他 {len(sc['projects']) - 1} 個）"
             if sc["all_projects"] else "本 repo")
    out = [f"**工具清單建議**｜期間 {since}～{per['end_date']}｜範圍：{scope}｜{sc['sessions']:,} 個 session｜"
           f"產出 {rep['generated_at']}｜ct-session-stats {rep['generator']['version']}", ""]
    rows = _rows(rep)
    rec = [r for r in rows if r["verdict"] == "recommend"]
    con = [r for r in rows if r["verdict"] == "consider"]
    decide = [e for e in rep["items"] if e["verdict"] == "needs_user_decision"]
    issues = rep["issues"]
    ctx_tok = su["avg_context_tokens"]
    pct = f"，占平均每輪上下文 {ctx_tok:,} token 的約 {su['mcp_saving_tokens']['mid'] / ctx_tok * 100:.1f}%" if ctx_tok else ""
    out += ["**結論摘要**", "",
            f"- 建議停用 {sum(r['n'] for r in rec)} 項（{len(rec)} 列）、可考慮 {sum(r['n'] for r in con)} 項（{len(con)} 列）。"
            f"每輪約省：MCP 部分 {_tk(su['mcp_saving_tokens'])} token{pct}；skill 清單部分 "
            f"{_tk(su['skill_saving_tokens'])}（依清單公式按請求數加權，單一 session 最多 ≈{su['skill_saving_max_tokens']:,}；"
            f"清單滿載時省量變小，改為補回被截的說明，約 {su['skill_restored_descriptions']} 筆）。",
            f"- 需使用者裁示 {len(decide)} 項" + ("：" + "、".join(f"內建 `{e['name']}`（≈{e['tokens_per_turn']['mid']:,} token／輪）"
                                                       for e in decide) if decide else "") + "。",
            f"- 另列問題 {len(issues)} 項：" + ("、".join(
                {"duplicate": "同名重複 skill", "mcp_failure": "MCP 連線失敗", "listing_truncated": "skill 清單被截"}[k] + f" {n}"
                for k, n in sorted(collections.Counter(i["kind"] for i in issues).items())) or "無") + "。",
            "- 只出建議，不自動改設定；改完開新 session 生效。", ""]
    out += ["**建議表**", ""]
    if rows:
        out += ["| # | 項目 | 層級 | 設定鍵／介面 | 30 天用量 | 每輪約省 | 注意 |", "|---|---|---|---|---|---|---|"]
        for i, r in enumerate(rows, 1):
            out.append(f"| {i} | {r['item']} | {r['layer']} | {r['lever']} | {r['usage']} | {r['saving']} | {r['notes'] or '—'} |")
    else:
        out.append("（無）")
    out += ["", "**需使用者裁示**", ""]
    if decide:
        out += ["| 項目 | 設定鍵 | 30 天用量 | 每輪約省 | 必讀 |", "|---|---|---|---|---|"]
        for e in decide:
            lv = "；或 ".join(_lever_text(x) for x in [e["lever"]] + e["lever_alternatives"] if x)
            out.append(f"| `{e['name']}`（內建工具） | {lv} | {e['used_sessions']:,}／{e['loaded_sessions']:,} session"
                       f"（{e['use_rate'] * 100:.1f}%）、{e['calls']['tool']:,} 次 | {_tk(e['tokens_per_turn'])} | {_notes_text(e['notes'])} |")
    else:
        out.append("（無）")
    out += ["", "**另列問題**", ""]
    dups = [i for i in issues if i["kind"] == "duplicate"]
    if dups:
        out += [f"同名重複 skill（{len(dups)} 組；處理：`.claude/settings.json` → `skillOverrides` → "
                "`\"anthropic-skills:<name>\": \"off\"`，🔴 不可用裸名）", "",
                "| 名稱 | 這一層版號 | 同步版號 | 這一層使用 | 同步版使用 | 同步版每輪字元 | 建議關 |", "|---|---|---|---|---|---|---|"]
        for i in dups:
            a, b = i["names"]
            vb = ("⚠️ " if i["version_mismatch"] else "") + i["versions"][b]
            out.append(f"| `{a}`（{LAYER_TEXT.get(i['layers'][a], i['layers'][a])}） | {i['versions'][a]} | {vb} | "
                       f"{i['used_sessions'][a]:,} | {i['used_sessions'][b]:,} | {i['synced_chars_per_turn']:,} | `{i['close']}` |")
        out.append("")
    fails = [i for i in issues if i["kind"] == "mcp_failure"]
    if fails:
        out += ["連線失敗的 MCP server（每輪 0 token，省的是啟動連線與失敗通知；本機服務沒開造成的，要用時開服務即可，不一定要移除）", "",
                "| server | 層級 | 失敗率 | 處理 |", "|---|---|---|---|"]
        for i in fails:
            lay = LAYER_TEXT.get(i["layer"], i["layer"])
            if i["repo_codes"]:
                how = f"由 {'、'.join(i['repo_codes'])} 處理"
                lay += f"（{'、'.join(i['repo_codes'])}）"
            else:
                how = "；或 ".join(_lever_text(x) for x in [i["lever"]] + i["lever_alternatives"] if x) or "—"
            out.append(f"| `{i['names'][0]}` | {lay} | {i['failed_sessions']:,}／{i['loaded_sessions']:,}"
                       f"（{i['failure_rate'] * 100:.0f}%） | {how} |")
        out.append("")
    tr = [i for i in issues if i["kind"] == "listing_truncated"]
    if tr:
        i = tr[0]
        names = "、".join(f"`{n}`" for n, _ in i["top_truncated"][:5]) or "—"
        out += [f"skill 清單被截：{i['near_cap_sessions']:,}／{i['sessions']:,} 個 session（{i['near_cap_share'] * 100:.0f}%）貼著上限"
                f"（`C` = {th['listing_cap_chars']:,} 字元）；只剩名稱的 skill 中位數 {i['names_only_median']} 個；"
                f"最常被截的通用名稱 {names}（另有專案專屬名稱 {i['project_specific_truncated']} 個，不列名）。"
                "先處理同名重複 skill 與建議表的 skill，被截的說明會補回。", ""]
    if not issues:
        out += ["（無）", ""]
    out += ["**不建議與資料不足**", "", "| 項目 | 結果 | 理由 |", "|---|---|---|"]
    vt = {"keep": "不建議", "in_use_by_type": "在用", "insufficient_data": "資料不足", "no_lever": "無可用手段",
          "other_repo": "由該 repo 處理"}
    shown = [e for e in rep["items"] if e["verdict"] in vt and not e.get("plugin")] + \
        [p for p in rep["plugins"] if p["verdict"] in vt]
    bucket = collections.OrderedDict()
    for e in sorted(shown, key=lambda e: (list(vt).index(e["verdict"]), e["kind"], e["name"])):
        if e["verdict"] == "in_use_by_type":
            why = "、".join(f"{_g(g)} {e['by_group'][g]['used'] if 'by_group' in e else ''}".strip()
                           for g in e["in_use_groups"]) + " 個 session"
            res = "、".join(_g(g) for g in e["in_use_groups"]) + " 在用"
            extra = _notes_text([n for n in e["notes"] if n.endswith("_lever")])
            bucket.setdefault((res, why + ("；" + extra if extra else ""), e["name"]), []).append(e)
        elif e["verdict"] == "insufficient_data":
            bucket.setdefault((vt["insufficient_data"], f"資料 {e['data_days']} 天、載入 {e['loaded_sessions']} session", e["name"]),
                              []).append(e)
        elif e["verdict"] == "other_repo":
            bucket.setdefault((vt["other_repo"], "各 repo 自己的安裝", "other_repo"), []).append(e)
        else:
            bucket.setdefault((vt[e["verdict"]], _notes_text(e["notes"]) or "—", e["verdict"] + e["kind"]), []).append(e)
    for (res, why, _), es in bucket.items():
        if len(es) > 6:
            label = f"{len(es)} 個（{'、'.join('`' + e['name'] + '`' for e in es[:4])}…）"
        else:
            label = "、".join(f"`{e['name']}`" for e in es)
        if es[0]["verdict"] == "other_repo":
            codes = sorted({c for e in es for c in e.get("repo_codes", [])})
            why = f"{'、'.join(codes[:6])}{'…' if len(codes) > 6 else ''} 的專案層安裝；{why}"
        out.append(f"| {label} | {res} | {why} |")
    ps = rep["project_specific"]
    if any(ps[k] for k in ("skill", "mcp", "agent")):
        out.append(f"| 不能列名的項目（其他 repo 的專案專屬名稱、不合名稱樣式；skill {ps['skill']}、MCP {ps['mcp']}、agent {ps['agent']}） | 不列名 | "
                   f"依隱私規則只給數量；其中 {ps['used']} 個期間內用過 |")
    cv = rep["coverage"]
    out += ["", f"**方法與限制**：期間依 session 開始時間；範圍 {scope}。附件覆蓋率：skill 清單 {cv['skill_listing']:,}／{sc['sessions']:,}、"
            f"MCP 清單 {cv['mcp_listing']:,}／{sc['sessions']:,}、agent 清單 {cv['agent_listing']:,}／{sc['sessions']:,}、"
            f"內建工具 schema {cv['tool_shape']:,}／{sc['sessions']:,}（沒有附件紀錄的 session 不進該類分母）。"
            "使用次數＝Skill 工具＋slash command（名稱在該 session 的 skill 清單才計）＋agent 類型（`subagent_type`）＋MCP 前綴＋內建工具名，"
            "只算主 session；直接讀 skill 檔照做、Workflow 腳本內的 agent、Codex 端計不到，所以 CT 自己的 skill 一律不建議。"
            f"換算 {th['chars_per_token']['mid']} 字元／token（{th['chars_per_token']['high']}～{th['chars_per_token']['low']}）；"
            "實測可能比字元估算高（T0420：13 個重複 skill 實測 −1,280 token）。"
            f"清單上限 `C` 取本期觀察最大值 {th['listing_cap_chars']:,} 字元，貼著上限＝≥ {th['listing_near_cap_chars']:,}。"
            f"門檻：資料 ≥ {th['data_days']} 天、載入 ≥ {th['loaded_sessions']} session、某類型在用 ≥ {th['group_used_sessions']} session、"
            f"可考慮＝使用 ≤ {th['consider_max_used']} session 且最後使用距結束日 ≥ {th['consider_min_idle_days']} 天；"
            f"內建工具＝使用率 < {th['builtin_rate_max'] * 100:.0f}% 且每輪 ≥ {th['builtin_tokens_min']} token。"
            f"期間內清單移除事件 {rep['removed_entries']} 次。"
            + ("其他 repo 以代號表示，代號對照不在本報告。" if sc["all_projects"] else "")]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Markdown 自檢（§ 7.3）：只印命中的檢查項編號，不印命中的字串
# ---------------------------------------------------------------------------
REPORT_ALLOWED_CLAUDE = ("~/.claude/settings.json", "~/.claude.json", ".claude/settings.local.json",
                         ".claude/settings.json", "~/.claude/skills/<name>/", ".claude/skills/<name>/")
REPORT_CHECKS = (
    ("2", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[a-z]{2,}")),
    ("3", re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/|/home/|AppData|\\\\")),
    ("4", re.compile(r"(?<![A-Za-z0-9-])[A-Za-z]--[A-Za-z0-9][A-Za-z0-9-]{6,}")),
    ("7", re.compile(r"\s&&\s")),
)


def check_report_text(text: str, other_names=()) -> list:
    hits = set()
    for name in SECRET_ENV:
        v = os.environ.get(name)
        if v and len(v) >= 8 and v in text:
            hits.add("1")
    for num, rx in REPORT_CHECKS:
        if rx.search(text):
            hits.add(num)
    rest = text
    for a in REPORT_ALLOWED_CLAUDE:
        rest = rest.replace(a, "")
    if ".claude" in rest:
        hits.add("5")
    for n in other_names or ():
        if n and _word_re(n).search(text):
            hits.add("6")
            break
    return sorted(hits)


def scan_repo_names(projects_dir) -> list:
    """--self-check --all-projects 用：在記憶體內取得各專案的 repo 目錄名（不輸出）。"""
    names, cache = set(), {}
    cur, _ = git_root(os.getcwd(), cache)
    ck = _norm_path(cur)
    for d in _dir_names(os.path.expanduser(projects_dir)):
        for f in sorted(glob.glob(os.path.join(os.path.expanduser(projects_dir), d, "*.jsonl")))[-3:]:
            cwd = None
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh):
                        if i > 200:
                            break
                        if '"cwd"' in line:
                            try:
                                o = json.loads(line)
                            except ValueError:
                                continue
                            if isinstance(o, dict) and isinstance(o.get("cwd"), str):
                                cwd = o["cwd"]
                                break
            except OSError:
                continue
            if cwd:
                root, is_git = git_root(cwd, cache)
                if is_git and _norm_path(root) != ck:
                    names.add(os.path.basename(root.rstrip("/\\")))
                break
    return sorted(names)


def emit_tools(rep: dict, args, out=None, err=None) -> int:
    out = out or sys.stdout
    err = err or sys.stderr
    others = rep.pop("_other_names", [])
    js = _dump(rep)
    probs = check_text(js)
    if probs:
        for p in sorted(set(probs)):
            err.write(f"self-check FAIL {p}\n")
        err.write("self-check: FAIL — nothing written\n")
        return EXIT_PRIVACY
    if args.json:
        text = js
    else:
        text = render_tools_md(rep)
        hits = check_report_text(text, others)
        if hits:
            err.write("self-check: FAIL (report checks " + ",".join(hits) + ") — nothing written\n")
            return EXIT_PRIVACY
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        err.write(f"tools: written ({len(text)} chars)\n")
    else:
        out.write(text)
    return EXIT_OK


def main(argv=None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Claude Code session JSONL → 工單層級用量統計（只讀、只輸出數字）")
    ap.add_argument("--projects-dir", default="~/.claude/projects")
    ap.add_argument("--project", action="append",
                    help="編碼後的專案目錄名，可給多次；省略時由目前目錄推算（請在 repo 根目錄執行）")
    ap.add_argument("--workorders-dir", help="_ct-workorders 目錄：讀工單 frontmatter id／type／session_ids 與塔台 session id")
    ap.add_argument("--workorders", help="T####,T####,…（只算這些工單；塔台取時間重疊的 session）")
    ap.add_argument("--since", help="YYYY-MM-DD（本機時區）或 ISO 8601；依 session 開始時間")
    ap.add_argument("--until", help="YYYY-MM-DD 或 ISO 8601；同時截掉時間晚於它的紀錄（紀錄層級）")
    ap.add_argument("--days", type=int, help="沒給 --since 時，取最近 N 天")
    ap.add_argument("--decision-log", action="append", help="決策日誌檔或目錄（可多次，含 _archive/decisions/）")
    ap.add_argument("--tower-state", action="append", help="另外的塔台狀態檔（預設讀 --workorders-dir 下的）")
    ap.add_argument("--bat-log", help="選填：BAT bat-scripts.log（讀得到才交叉驗證，讀不到不影響）")
    ap.add_argument("--pricing", default=os.path.join(here, "pricing.json"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sessions", action="store_true", help="附逐 session 明細")
    ap.add_argument("--with-session-ids", action="store_true", help="附 session id（預設不附）")
    ap.add_argument("--no-subagents", action="store_true")
    ap.add_argument("--snapshot-append", metavar="FILE", help="把工單條目併入快照（_insights/session-stats/<YYYY-MM>.json）")
    ap.add_argument("--facts", metavar="OUT", help="另寫候選事實 NDJSON（ct-session-fact/0.1，由快照條目產生）")
    ap.add_argument("--facts-from", action="append", metavar="SNAPSHOT",
                    help="只從既有快照（檔或目錄）產生候選事實，不讀 JSONL；搭配 --facts")
    ap.add_argument("--self-check", metavar="FILE",
                    help="只做隱私自檢；.md 走 Markdown 檢查（加 --all-projects 比對其他 repo 名稱）；不通過 exit 3")
    # v6.0.0-beta.12：工具清單建議（*insights tools）
    ap.add_argument("--tools", action="store_true", help="工具清單建議報告（Markdown；--json 改輸出 ct-tool-usage/0.1）")
    ap.add_argument("--all-projects", action="store_true", help="跨 repo：掃專案紀錄目錄下全部專案，其他 repo 一律代號")
    ap.add_argument("--keep", action="append", metavar="NAME", help="這個名稱（skill／plugin／MCP／agent）一律不建議；可多次")
    ap.add_argument("--out", metavar="FILE", help="寫檔而不是 stdout（寫前過自檢）")
    ap.add_argument("--codes-map", metavar="FILE",
                    help="跨 repo 代號對照：檔案已存在就沿用其代號（不改寫），不存在才寫；只准在所有被掃 repo 之外")
    ap.add_argument("--claude-home", default="~/.claude", help="設定來源（測試用）")
    ap.add_argument("--claude-json", default="~/.claude.json", help="設定來源（測試用）")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return EXIT_USAGE if e.code else EXIT_OK
    if args.self_check:
        if args.self_check.lower().endswith(".md"):
            try:
                with open(args.self_check, encoding="utf-8") as f:
                    text = f.read()
            except OSError:
                print("error: cannot read file", file=sys.stderr)
                return EXIT_USAGE
            hits = check_report_text(text, scan_repo_names(args.projects_dir) if args.all_projects else ())
            for h in hits:
                print("FAIL report-check", h)
            print("self-check:", "PASS" if not hits else f"FAIL ({len(hits)})")
            return EXIT_OK if not hits else EXIT_PRIVACY
        probs = self_check_file(args.self_check)
        for p in sorted(set(probs)):
            print("FAIL", p)
        print("self-check:", "PASS" if not probs else f"FAIL ({len(probs)})")
        return EXIT_OK if not probs else EXIT_PRIVACY
    if args.tools:
        if args.snapshot_append or args.facts or args.facts_from or args.with_session_ids or args.sessions \
                or args.workorders or args.decision_log:
            print("error: --tools does not take --snapshot-append/--facts/--facts-from/--with-session-ids/"
                  "--sessions/--workorders/--decision-log", file=sys.stderr)
            return EXIT_USAGE
        try:
            rep_t = build_tools_report(args)
        except ValueError as e:
            print(f"error: bad time value ({str(e)[:40]})", file=sys.stderr)
            return EXIT_USAGE
        except UsageError as e:
            print(f"error: {e}", file=sys.stderr)
            return EXIT_USAGE
        except Unavailable as e:
            if args.json:
                sys.stdout.write(_dump({"schema": TOOLS_SCHEMA, "available": False, "reason": str(e)}))
            else:
                print(f"tools: 資料不可用 ({e})")
            return EXIT_UNAVAILABLE
        return emit_tools(rep_t, args)
    if args.all_projects or args.keep or args.out or args.codes_map:
        print("error: --all-projects/--keep/--out/--codes-map need --tools", file=sys.stderr)
        return EXIT_USAGE
    if args.facts_from:
        if not args.facts:
            print("error: --facts-from needs --facts", file=sys.stderr)
            return EXIT_USAGE
        facts = facts_from_snapshots(args.facts_from)
        probs = _write_checked(args.facts, "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n"
                                                   for x in facts))
        if probs:
            print("self-check: FAIL — facts not written", file=sys.stderr)
            return EXIT_PRIVACY
        print(f"facts: {len(facts)}")
        return EXIT_OK
    if not args.project:
        args.project = [encode_project(os.getcwd())]
    try:
        rep = build_report(args)
    except ValueError as e:
        print(f"error: bad time value ({str(e)[:40]})", file=sys.stderr)
        return EXIT_USAGE
    except Unavailable as e:
        if args.json:
            sys.stdout.write(_dump({"schema": REPORT_SCHEMA, "available": False, "reason": str(e)}))
        else:
            print(f"session-stats: 資料不可用 ({e})")
        return EXIT_UNAVAILABLE
    return emit(rep, args)


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    sys.exit(main())
