#!/usr/bin/env python3
"""mq5check.py - offline MQL5 compile checker: .mq5 -> C++ (line-preserving) -> clang++ -fsyntax-only against mql5shim.h.

Usage: python3 -I mq5check.py [--keep] [--cpp OUT.cpp] [--raw] file.mq5
Prints diagnostics and a final line "RESULT: N errors, M warnings". Exit code 1 if N > 0.
"""
import calendar
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SHIM = os.path.join(HERE, "mql5rt.h")
MAIN_FILE = [None]
INPUTS = []   # (type, name) of every `input` global, in order

CLANG_FLAGS = [
    "-std=c++17", "-fsyntax-only", "-fno-caret-diagnostics", "-fno-color-diagnostics", "-fmessage-length=0",
    "-ferror-limit=0", "-fshow-column",
    "-Wall", "-Wextra", "-Wshadow", "-Wfloat-conversion", "-Wshorten-64-to-32", "-Wimplicit-int-conversion",
    "-Wsign-compare", "-Wuninitialized", "-Wsometimes-uninitialized", "-Wconditional-uninitialized", "-Wreturn-type",
    # MetaEditor does not warn about these:
    "-Wno-unused-parameter", "-Wno-unused-variable", "-Wno-unused-but-set-variable", "-Wno-unused-function",
    "-Wno-unused-const-variable", "-Wno-unused-local-typedef", "-Wno-parentheses", "-Wno-logical-op-parentheses",
    "-Wno-switch", "-Wno-missing-field-initializers", "-Wno-implicit-fallthrough", "-Wno-deprecated-copy",
    "-Wno-unused-lambda-capture", "-Wno-dangling-else", "-Wno-pragma-once-outside-header",
    "-Wno-implicit-int-float-conversion",   # long->double: MetaEditor does not report it (unverified, see README)
    "-Wno-extra-semi", "-Wno-c++20-designator",
]

# identifiers that are C++ keywords (or clash with the C++ language) but are legal MQL5 names: renamed consistently
RENAME = {"long": "mql_long", "__FILE__": "MQ_FILE__", "__DATE__": "MQ_DATE__", "__DATETIME__": "MQ_DATETIME__", "__PATH__": "MQ_PATH__"}
CXX_KEYWORDS = ["alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor", "char16_t", "char32_t", "compl", "concept",
                "constexpr", "decltype", "export", "friend", "mutable", "namespace", "noexcept", "not", "not_eq", "nullptr", "or", "or_eq",
                "register", "requires", "static_assert", "thread_local", "typeid", "typename", "using", "wchar_t", "xor", "xor_eq",
                "inline", "explicit", "constinit", "consteval", "co_await", "co_return", "co_yield", "restrict_unused"]
for _k in CXX_KEYWORDS:
    if _k not in ("typename", "inline", "explicit", "static_assert"):  # MQL5 itself has typename/inline/explicit
        RENAME.setdefault(_k, _k + "__mq")

TOKEN_RE = re.compile(r"""
 (?P<bc>/\*.*?\*/) |
 (?P<lc>//[^\n]*) |
 (?P<dt>[Dd]'[^'\n]*') |
 (?P<col>[Cc]'[^'\n]*') |
 (?P<str>"(?:\\.|[^"\\\n])*") |
 (?P<chr>'(?:\\.|[^'\\\n])*') |
 (?P<id>[A-Za-z_][A-Za-z_0-9]*) |
 (?P<num>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?[A-Za-z0-9_]*) |
 (?P<nl>\n) |
 (?P<ws>[ \t\r\f\v]+) |
 (?P<p>.)
""", re.X | re.S)

NOWRAP_DIRECTIVES = {"property", "include", "import", "pragma", "error", "warning", "resource", "undef"}
KNOWN_INCLUDES = {"Trade/Trade.mqh", "Trade\\Trade.mqh", "Trade/SymbolInfo.mqh", "Trade/PositionInfo.mqh", "Trade/DealInfo.mqh",
                  "Trade/OrderInfo.mqh", "Trade/AccountInfo.mqh"}

notes = []   # preprocessor-level warnings (printed as warnings)
preproc_errors = []


class Tok:
    __slots__ = ("k", "t")

    def __init__(self, k, t):
        self.k, self.t = k, t


def read_src(path):
    """MetaEditor files may be UTF-16 (BOM) or UTF-8 (with/without BOM)."""
    data = open(path, "rb").read()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace").replace("\r\n", "\n")
    return data.decode("utf-8-sig", errors="replace")


def lex(src):
    toks = []
    for m in TOKEN_RE.finditer(src):
        toks.append(Tok(m.lastgroup, m.group()))
    return toks


def dt_to_cpp(lit, where):
    body = lit[2:-1].strip()
    m = re.match(r"^(\d{4})\.(\d{1,2})\.(\d{1,2})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$", body)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        hh, mi, ss = int(m.group(4) or 0), int(m.group(5) or 0), int(m.group(6) or 0)
        return "((datetime)%dLL)" % (calendar.timegm((y, mo, d, hh, mi, ss)))
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", body)
    if m:
        return "((datetime)%dLL)" % (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3) or 0))
    if body == "":
        return "((datetime)0)"
    preproc_errors.append((where[0], where[1], "invalid datetime literal %s" % lit))
    return "((datetime)0)"


def col_to_cpp(lit, where):
    body = lit[2:-1].strip()
    named = re.match(r"^[A-Za-z]\w*$", body)
    parts = [p.strip() for p in body.split(",")]
    try:
        if len(parts) == 3:
            r, g, b = [int(p, 0) for p in parts]
            return "((color)%d)" % (r | (g << 8) | (b << 16))
        if len(parts) == 1 and parts[0] and not named:
            return "((color)%d)" % int(parts[0], 0)
    except ValueError:
        pass
    preproc_errors.append((where[0], where[1], "invalid color literal %s" % lit))
    return "((color)0)"


def find_include(name, cur_dir, main_dir):
    for base in (cur_dir, main_dir):
        p = os.path.normpath(os.path.join(base, name))
        if os.path.isfile(p):
            return p
    return None


def translate(path, included, stack=()):
    """Return translated text for one source file (same number of lines as the source)."""
    src = read_src(path)
    toks = lex(src)
    n = len(toks)
    out_dirs = {}     # token index -> replacement text (whole-directive handling)
    cur_dir = os.path.dirname(os.path.abspath(path))
    line_no = 1
    lines_of = []     # line number of each token start
    for t in toks:
        lines_of.append(line_no)
        line_no += t.t.count("\n")

    # ---- directives (#property / #include / #import ...) ----
    at_line_start = True
    i = 0
    import_open = False
    while i < n:
        t = toks[i]
        if t.k == "nl":
            at_line_start = True
        elif t.k in ("ws", "bc"):
            if t.k == "bc" and "\n" in t.t:
                at_line_start = at_line_start
        elif t.k == "p" and t.t == "#" and at_line_start:
            j = i + 1
            while j < n and toks[j].k in ("ws",):
                j += 1
            name = toks[j].t if j < n and toks[j].k == "id" else ""
            # end of directive line
            e = j
            while e < n and toks[e].k != "nl" and not (toks[e].k == "bc" and "\n" in toks[e].t):
                e += 1
            if name in NOWRAP_DIRECTIVES:
                body = "".join(x.t for x in toks[j + 1:e]).strip()
                repl = ""
                if name == "include":
                    m = re.match(r'^<(.+)>', body)
                    m2 = re.match(r'^"(.+)"', body)
                    if m:
                        inc = m.group(1)
                        if inc not in KNOWN_INCLUDES:
                            notes.append((path, lines_of[i], "include <%s> is not covered by the shim: its symbols will be reported as undeclared" % inc))
                    elif m2:
                        p = find_include(m2.group(1), cur_dir, os.path.dirname(MAIN_FILE[0] or os.path.abspath(sys.argv[-1])))
                        if p is None:
                            preproc_errors.append((path, lines_of[i], "cannot open include file '%s'" % m2.group(1)))
                        elif p not in stack:
                            sub = translate(p, included, stack + (path,))
                            repl = '\n#line 1 "%s"\n%s\n#line %d "%s"\n' % (p, sub, lines_of[i], os.path.abspath(path))
                            # compress: the include directive line itself must keep its newline count (0 extra lines here)
                elif name == "import":
                    import_open = not import_open
                    notes.append((path, lines_of[i], "#import is not supported by the checker (imported functions are undeclared)"))
                elif name == "property":
                    pass
                for x in range(i, e):
                    toks[x].t = ""
                    toks[x].k = "ws"
                toks[i].t = repl
            else:
                # keep the directive; mark its tokens so strings are not wrapped only for the NOWRAP set
                pass
            i = e
            continue
        else:
            at_line_start = False
        i += 1

    # ---- `input group "..."` ----
    sig = [k for k in range(n) if toks[k].k not in ("ws", "nl", "bc", "lc")]
    sidx = {k: p for p, k in enumerate(sig)}

    def nxt(k, step=1):
        p = sidx.get(k)
        if p is None:
            return None
        p += step
        return sig[p] if 0 <= p < len(sig) else None

    for k in sig:
        t = toks[k]
        if t.k == "id" and t.t == "input":
            a = nxt(k)
            if a is not None and toks[a].k == "id" and toks[a].t == "group":
                b = nxt(a)
                t.t = ""
                toks[a].t = ""
                if b is not None and toks[b].k == "str":
                    toks[b].t = ""
                    toks[b].k = "ws"
    # ---- inputs -> plain (NON-const) globals, remembered for SetInput ----
    for p, k in enumerate(sig):
        t = toks[k]
        if t.k == "id" and t.t in ("input", "sinput"):
            q = p + 1
            while q < len(sig) and toks[sig[q]].t not in ("=", ";"):
                q += 1
            if q < len(sig) and q - 2 > p:
                INPUTS.append((toks[sig[q - 2]].t, toks[sig[q - 1]].t))
            t.t = ""
    # ---- (string) cast: explicit casts must not trigger the implicit-number->string warning ----
    for p, k in enumerate(sig):
        if toks[k].t == "(" and p + 2 < len(sig) and toks[sig[p + 1]].t == "string" and toks[sig[p + 2]].t == ")":
            toks[sig[p + 1]].t = "mq_strcast"
    # ---- literals and renames ----
    for k in sig:
        t = toks[k]
        if t.k == "id":
            if t.t in RENAME:
                t.t = RENAME[t.t]
        elif t.k == "str":
            t.t = t.t + "_mq"
        elif t.k == "dt":
            t.t = dt_to_cpp(t.t, (path, lines_of[k]))
        elif t.k == "col":
            t.t = col_to_cpp(t.t, (path, lines_of[k]))
    # strings in preprocessor lines that are kept (#define etc.) were wrapped above too; that is intended.

    # ---- dynamic arrays: T a[]  /  T &a[] ----
    sig = [k for k in range(n) if toks[k].k not in ("ws", "nl", "bc", "lc") and toks[k].t != ""]
    last_type = None
    for p, k in enumerate(sig):
        t = toks[k]
        if t.t in (";", "{", "}"):
            last_type = None
        if not (t.t == "[" and p + 3 < len(sig) and toks[sig[p + 1]].t == "]" and toks[sig[p - 1]].k == "id"):
            continue
        after = toks[sig[p + 2]].t
        if after not in (";", ",", ")"):
            continue
        name_k = sig[p - 1]
        q = p - 2
        amp = False
        if toks[sig[q]].t == "&":
            amp = True
            amp_k = sig[q]
            q -= 1
        type_k = None
        if toks[sig[q]].k == "id" and toks[sig[q]].t not in ("const", "static", "return"):
            type_k = sig[q]
            last_type = toks[type_k].t
        elif toks[sig[q]].t == "," and last_type and not amp:
            type_k = None
        else:
            continue
        ttxt = toks[type_k].t if type_k is not None else last_type
        wrapper = "ArrayView" if amp else "MqlArr"
        if type_k is not None:
            toks[type_k].t = "%s<%s>" % (wrapper, ttxt)
        # (second declarator of `T a[], b[];`: the first one already carries the MqlArr<T> type, only [] is dropped)
        if amp:
            toks[amp_k].t = ""
        toks[sig[p]].t = ""
        toks[sig[p + 1]].t = ""

    # ---- `.` on object pointers (MQL5 has no ->): obj.m  ->  mq_dot(obj).m ----
    sig = [k for k in range(n) if toks[k].k not in ("ws", "nl", "bc", "lc") and toks[k].t != ""]
    NOT_CALL = {"if", "while", "for", "switch", "return", "sizeof", "else", "do", "case"}

    O = {k: toks[k].t for k in sig}   # snapshot: the pass below prefixes token texts

    def chain_start(p):
        while True:
            t = O[sig[p]]
            if t in (")", "]"):
                close, open_ = t, "(" if t == ")" else "["
                depth = 0
                q = p
                while q >= 0:
                    tt = O[sig[q]]
                    if tt == close:
                        depth += 1
                    elif tt == open_:
                        depth -= 1
                        if depth == 0:
                            break
                    q -= 1
                if q < 0:
                    return None
                if q - 1 >= 0 and toks[sig[q - 1]].k == "id" and O[sig[q - 1]] not in NOT_CALL and open_ == "(":
                    p = q - 1
                elif open_ == "[" and q - 1 >= 0 and (toks[sig[q - 1]].k == "id" or O[sig[q - 1]] in (")", "]")):
                    p = q - 1
                    continue
                else:
                    return q
            elif toks[sig[p]].k == "id":
                pass
            else:
                return None
            if p - 2 >= 0 and O[sig[p - 1]] in (".", "->", "::"):
                p -= 2
                continue
            return p

    for p, k in enumerate(sig):
        if O[k] == "." and p > 0 and p + 1 < len(sig) and toks[sig[p + 1]].k == "id":
            st = chain_start(p - 1)
            if st is None:
                continue
            toks[sig[st]].t = "mq_dot(" + toks[sig[st]].t
            toks[k].t = ")."
    return "".join(t.t for t in toks)


HANDLERS = {
    "OnTick": "void (*)()", "OnTimer": "void (*)()", "OnTrade": "void (*)()", "OnDeinit": "void (*)(const int)",
    "OnChartEvent": "void (*)(const int, const mql_long&, const double&, const string&)",
    "OnTradeTransaction": "void (*)(const MqlTradeTransaction&, const MqlTradeRequest&, const MqlTradeResult&)",
    "OnTester": "double (*)()",
}


def build_cpp(path):
    orig = read_src(path)
    body = translate(path, set())
    extra = []
    for name, sig in HANDLERS.items():
        m = re.search(r"^[ \t]*(?:void|int|double|bool)[ \t]+%s[ \t]*\(" % name, orig, re.M)
        if m:
            ln = orig.count("\n", 0, m.start()) + 1
            extra.append('#line %d "%s"\ntypedef %s;\nstatic mq_t_%s mq_chk_%s = &%s;' % (ln, os.path.abspath(path), sig.replace("(*)", "(*mq_t_%s)" % name), name, name, name))
    head = '#include "%s"\n#line 1 "%s"\n' % (SHIM, os.path.abspath(path))
    return head + body + "\n" + "\n".join(extra) + "\n" + rt_wrapper(), orig


def rt_wrapper():
    """Plain-C entry points for the driver (generated, appended to the translated EA)."""
    L = ['#line 1 "<rt-wrapper>"', 'extern "C" int rt_SetInput(const char* name, double v)', "{"]
    for ty, nm in INPUTS:
        if ty == "string":
            continue
        if ty in ("bool",):
            cast = "(v != 0)"
        elif ty in ("int", "uint", "long", "ulong", "datetime", "color", "double", "float", "short", "ushort", "char", "uchar"):
            cast = "(%s)v" % ("mql_long" if ty == "long" else ty)
        else:
            cast = "(%s)(int)v" % ty          # enum
        L.append('   if(__builtin_strcmp(name, "%s") == 0) { %s = %s; return 1; }' % (nm, nm, cast))
    L += ["   return 0;", "}"]
    L.append("struct RtEv { int fill, fillL, exit, win; long long bi, armBar; double lim, stp, stp0, res; };")
    L.append('extern "C" void rt_reset() { ResetEngine(); }')
    L.append('extern "C" int rt_look() { return (int)MathMax(MathMax(InpStructLen, InpBrkLen + 1), MathMax(InpMomLen + 1, InpStopLen)) + 2; }')
    L.append('extern "C" void rt_step(int s, RtEv* e) { ProcessBar(s); e->fill = evFill; e->fillL = evFillL; e->exit = evExit; e->win = evWin; e->bi = bi; '
             'e->armBar = armBar; e->lim = lim; e->stp = stp; e->stp0 = stp0; e->res = evRes; }')
    L.append('extern "C" void rt_stats(double* o) { o[0] = totW; o[1] = totL; o[2] = totR; o[3] = tpHitN[0]; o[4] = tpHitN[1]; o[5] = tpHitN[2]; o[6] = tpHitN[3]; '
             'o[7] = beN; o[8] = lkN; o[9] = ghW; o[10] = ghL; o[11] = ghR; }')
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- diagnostics
DIAG_RE = re.compile(r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+): (?P<sev>warning|error|fatal error|note): (?P<msg>.*?)(?: \[(?P<flag>-W[\w+-]+)\])?$")

MSG_MAP = [
    (re.compile(r"use of undeclared identifier '(\w+)'"), lambda m: "'%s' - undeclared identifier" % m.group(1)),
    (re.compile(r"no member named '(\w+)' in '([^']+)'.*"), lambda m: "'%s' - undeclared identifier (no such member in %s)" % (m.group(1), clean_types(m.group(2)))),
    (re.compile(r"implicit conversion from '(\w+)' to '(\w+)' changes value.*"), lambda m: "possible loss of data due to type conversion ('%s' to '%s')" % (m.group(1), m.group(2))),
    (re.compile(r"expected ';'.*"), lambda m: "';' - semicolon expected"),
    (re.compile(r"cannot assign to variable '(\w+)' with const-qualified type.*"), lambda m: "'%s' - constant cannot be modified (inputs are read-only)" % m.group(1)),
    (re.compile(r"cannot assign to (?:non-static data member|return value|variable) .*const.*"), lambda m: "constant cannot be modified"),
    (re.compile(r"no matching function for call to '(\w+)'"), lambda m: "'%s' - wrong parameters count or parameter types" % m.group(1)),
    (re.compile(r"too (few|many) arguments to function call, expected (\d+), have (\d+).*"), lambda m: "wrong parameters count (expected %s, have %s)" % (m.group(2), m.group(3))),
    (re.compile(r"implicit conversion (?:turns floating-point number into integer|loses integer precision|loses floating-point precision|changes .*|from .* may lose.*): '(.+?)'(?: \(aka '.*?'\))? to '(.+?)'(?: \(aka '.*?'\))?"), lambda m: "possible loss of data due to type conversion ('%s' to '%s')" % (m.group(1), m.group(2))),
    (re.compile(r".*is deprecated: implicit conversion from 'number' to 'string'"), lambda m: "implicit conversion from 'number' to 'string'"),
    (re.compile(r"variable '(\w+)' is (?:used )?uninitialized.*"), lambda m: "variable '%s' not initialized" % m.group(1)),
    (re.compile(r"variable '(\w+)' may be uninitialized.*"), lambda m: "variable '%s' not initialized" % m.group(1)),
    (re.compile(r"comparison of integers of different signs: '(.+)' and '(.+)'"), lambda m: "signed/unsigned mismatch in comparison ('%s' vs '%s')" % (m.group(1), m.group(2))),
    (re.compile(r"non-void function does not return a value.*"), lambda m: "not all control paths return a value"),
    (re.compile(r"control may reach end of non-void function"), lambda m: "not all control paths return a value"),
    (re.compile(r"array index (-?\d+) is (?:past the end|before the beginning) of the array.*"), lambda m: "array out of range (index %s)" % m.group(1)),
    (re.compile(r"(?:remainder|division) by zero.*"), lambda m: "zero divide"),
    (re.compile(r"(?:if|while|for) statement has empty body"), lambda m: "empty controlled statement found"),
    (re.compile(r".*'mq_t_(\w+)'.*"), lambda m: "wrong signature of event handler %s" % m.group(1)),
    (re.compile(r"redefinition of '(\w+)'"), lambda m: "'%s' - variable already defined" % m.group(1)),
    (re.compile(r"cannot initialize .* with an (?:rvalue|lvalue) of type '(.+)'"), None),
]
ENUM_HINT = re.compile(r"'(?:int|uint|long long|unsigned int|mql_long)'.*'(ENUM_\w+|\w*enum\w*)'|'(ENUM_\w+)'.*'(?:int|uint|long long)'|from 'int' to '(ENUM_\w+)'|no viable conversion from '(?:int|unsigned int|long long)' to '(ENUM_\w+)'")


def clean_types(msg):
    msg = re.sub(r" \(aka '[^']*'\)", "", msg)
    msg = re.sub(r"\bmql_long\b", "long", msg)
    msg = re.sub(r"\bmqlstring\b", "string", msg)
    msg = re.sub(r"\bMqlArr<(.+?)>", r"\1[]", msg)
    return msg


def map_msg(sev, msg, flag, srcline, col):
    msg = clean_types(msg)
    orig = msg
    if flag == "-Wshadow":
        name = ""
        m = re.match(r"[A-Za-z_]\w*", srcline[col - 1:]) if srcline and 0 < col <= len(srcline) else None
        if m:
            name = m.group(0)
        what = "local declaration" if "local" in msg else ("class member" if "member" in msg else "global declaration")
        return "declaration of '%s' hides %s" % (name or "?", what), orig
    for rx, fn in MSG_MAP:
        m = rx.match(msg)
        if m and fn:
            return fn(m), orig
    return msg, orig


def run_clang(cpp_path):
    cmd = ["clang++"] + CLANG_FLAGS + [cpp_path]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stderr


INT_TO_ENUM = re.compile(r"(?:with an? (?:rvalue|lvalue) of type|from) '(?:int|unsigned int|long long|uint|long|ulong|unsigned long long|mql_long)'.*?(?:to )?'(ENUM_\w+)'|no known conversion from '(?:int|unsigned int|long long|uint|long|ulong|mql_long)'(?: \(aka [^)]*\))? to '(ENUM_\w+)'|cannot initialize .* of type '(ENUM_\w+)' with an? (?:rvalue|lvalue) of type '(?:int|unsigned int|long long|double)'|assigning to '(ENUM_\w+)' from incompatible type '(?:int|unsigned int|long long)'")


def is_int_to_enum(d):
    """MQL5 (unlike C++) accepts an implicit integer -> enum conversion; report these as a warning to verify, not an error."""
    texts = [d["msg"]] + [n["msg"] for n in d["notes"]]
    if not any(INT_TO_ENUM.search(t) for t in texts):
        return False
    # arg-count / undeclared problems in the same diagnostic keep it an error
    if any(re.search(r"requires (?:at least )?\d+ arguments?|too (?:few|many)", t) for t in texts):
        return False
    return True


def parse_and_report(stderr, cpp_text, raw=False):
    cpp_lines = cpp_text.split("\n")
    diags = []   # dict(file,line,col,sev,msg,flag,notes)
    cur = None
    for ln in stderr.splitlines():
        m = DIAG_RE.match(ln)
        if not m:
            continue
        d = m.groupdict()
        d["line"], d["col"] = int(d["line"]), int(d["col"])
        if d["sev"] == "note":
            if cur is not None and len(cur["notes"]) < 12:
                cur["notes"].append(d)
            continue
        d["notes"] = []
        cur = d
        diags.append(d)
    seen = set()
    out = []
    n_err = n_warn = 0
    for d in diags:
        key = (d["file"], d["line"], d["col"], d["sev"], d["msg"])
        if key in seen:
            continue
        seen.add(key)
        sev = "error" if d["sev"] in ("error", "fatal error") else "warning"
        if d["flag"] in ("-Warray-bounds", "-Wdivision-by-zero") and sev == "warning":
            sev = "error"     # MetaEditor reports a constant out-of-range index / zero divide as an error
        if sev == "error" and is_int_to_enum(d):
            sev = "warning"
            d["enum_hint"] = True
        if sev == "error":
            n_err += 1
        else:
            n_warn += 1
        out.append((sev, d))
    return out, n_err, n_warn


def source_line(path, ln, cache={}):
    if path not in cache:
        try:
            cache[path] = read_src(path).split("\n")
        except OSError:
            cache[path] = []
    L = cache[path]
    return L[ln - 1] if 0 < ln <= len(L) else ""


def line_map(cpp):
    """(file, line) -> translated text, following the #line directives of the generated C++."""
    m = {}
    cur, ln = None, 1
    for row in cpp.split("\n"):
        d = re.match(r'#line (\d+) "(.*)"$', row)
        if d:
            ln, cur = int(d.group(1)), d.group(2)
            continue
        if cur is not None:
            m[(cur, ln)] = row
        ln += 1
    return m


def main_check(argv):
    keep = "--keep" in argv
    raw = "--raw" in argv
    cpp_out = None
    args = []
    it = iter(argv[1:])
    for a in it:
        if a == "--cpp":
            cpp_out = next(it)
        elif a in ("--keep", "--raw"):
            pass
        else:
            args.append(a)
    if len(args) != 1:
        print(__doc__)
        return 2
    path = os.path.abspath(args[0])
    if not os.path.isfile(path):
        print("cannot open %s" % path)
        return 2
    sys.argv[-1] = path
    cpp, orig = build_cpp(path)
    tmpdir = tempfile.mkdtemp(prefix="mq5check_")
    cpp_path = cpp_out or os.path.join(tmpdir, os.path.basename(path) + ".cpp")
    with open(cpp_path, "w", encoding="utf-8") as f:
        f.write(cpp)
    stderr = run_clang(cpp_path)
    if raw:
        print(stderr)
    out, n_err, n_warn = parse_and_report(stderr, cpp)
    lmap = line_map(cpp)
    # preprocessor-level findings
    for w in notes:
        print("%s(%d,1) : warning: %s" % (w[0], w[1], w[2]))
        n_warn += 1
    for e in preproc_errors:
        print("%s(%d,1) : error: %s" % (e[0], e[1], e[2]))
        n_err += 1
    for sev, d in sorted(out, key=lambda x: (x[1]["file"], x[1]["line"], x[1]["col"])):
        f = d["file"]
        src = source_line(f, d["line"])
        msg, orig_msg = map_msg(d["sev"], d["msg"], d["flag"], lmap.get((f, d["line"]), src), d["col"])
        # column in the translated text can differ from the original; the line is exact
        tag = ""
        if msg != orig_msg or d["flag"]:
            tag = "   [clang: %s%s]" % (orig_msg if msg != orig_msg else "", (" " + d["flag"]) if d["flag"] else "")
            tag = tag.replace("[clang:  ", "[clang: ")
        if f.endswith("mql5shim.h"):
            f = "mql5shim.h"
        if d.get("enum_hint"):
            msg = "implicit integer->enum conversion (MQL5 normally accepts this, C++ does not - verify the value is a valid enum member): " + msg
        print("%s(%d,%d) : %s: %s%s" % (f, d["line"], d["col"], sev, msg, tag))
        if src.strip():
            print("    | " + src.strip()[:160])
        for nt in d["notes"][:3]:
            nf = nt["file"]
            if nf.endswith("mql5shim.h"):
                nf = "mql5shim.h"
            print("    note: %s(%d): %s" % (os.path.basename(nf), nt["line"], nt["msg"][:200]))
    print("RESULT: %d errors, %d warnings" % (n_err, n_warn))
    if not keep and not cpp_out:
        try:
            os.remove(cpp_path)
            os.rmdir(tmpdir)
        except OSError:
            pass
    return 1 if n_err else 0





if __name__ == "__main__":
    # usage: mq5rt.py file.mq5 out.cpp   -> executable-harness C++ (inputs non-const, rt_* entry points appended)
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    inp, outp = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    if outp == inp or outp.lower().endswith((".mq5", ".mqh")):
        print("refusing to write the output over a source file: %s" % outp)
        sys.exit(2)
    MAIN_FILE[0] = inp
    cpp, _ = build_cpp(inp)
    open(outp, "w", encoding="utf-8").write(cpp)
    print("wrote %s (%d inputs)" % (outp, len(INPUTS)))
