"""v6.0 true grid: wrap the EA (globals + functions + event handlers) into class CLeg, so two legs run side by side with their own state.
wrap(text) -> text. Globals become members (their initial values go to the constructor), functions become methods (prototype in the
class, the definition outside as CLeg::name with the default values removed), #define / enum / struct stay global (before the class).
The event handlers become Init / Deinit / ChartEvt / Tick; new OnInit / OnDeinit / OnChartEvent / OnTick drive leg 0 (and leg 1 in the grid)."""
import re

HANDLERS = [('int OnInit()', 'int Init()'), ('void OnDeinit(const int reason)', 'void Deinit(const int reason)'),
            ('void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)',
             'void ChartEvt(const int id, const long &lparam, const double &dparam, const string &sparam)'),
            ('void OnTick()', 'void Tick()')]


def scan_items(t):
    """top-level items: (lead, kind, text). kind: pp, func, type (enum / struct), decl, proto"""
    i, n, out = 0, len(t), []
    while i < n:
        j = i
        while j < n:                                   # lead: blank space and comments
            if t[j].isspace(): j += 1
            elif t.startswith('//', j): j = t.find('\n', j); j = n if j < 0 else j + 1
            elif t.startswith('/*', j): j = t.index('*/', j) + 2
            else: break
        lead = t[i:j]
        if j >= n: out.append((lead, 'tail', '')); break
        if t[j] == '#':
            k = t.find('\n', j); k = n if k < 0 else k
            out.append((lead, 'pp', t[j:k])); i = k; continue
        k, dp, db, dk, eq, seen_paren, kind = j, 0, 0, 0, False, False, None
        head = re.match(r'\s*(enum|struct|class)\b', t[j:j + 20])
        while k < n:
            ch = t[k]
            if t.startswith('//', k): k = t.find('\n', k); continue
            if t.startswith('/*', k): k = t.index('*/', k) + 2; continue
            if ch == '"':
                k += 1
                while t[k] != '"': k += 2 if t[k] == '\\' else 1
                k += 1; continue
            if ch == "'":
                k += 1
                while t[k] != "'": k += 2 if t[k] == '\\' else 1
                k += 1; continue
            if ch == '(': dp += 1; seen_paren = True
            elif ch == ')': dp -= 1
            elif ch == '[': dk += 1
            elif ch == ']': dk -= 1
            elif ch == '=' and dp == 0 and db == 0 and dk == 0 and t[k + 1] != '=' and t[k - 1] not in '=!<>': eq = True
            elif ch == '{':
                if db == 0 and dp == 0 and not eq and (head or seen_paren):
                    # a body: function or type
                    d = 1; m = k + 1
                    while d:
                        if t.startswith('//', m): m = t.find('\n', m); continue
                        if t.startswith('/*', m): m = t.index('*/', m) + 2; continue
                        c = t[m]
                        if c == '"':
                            m += 1
                            while t[m] != '"': m += 2 if t[m] == '\\' else 1
                        elif c == "'":
                            m += 1
                            while t[m] != "'": m += 2 if t[m] == '\\' else 1
                        elif c == '{': d += 1
                        elif c == '}': d -= 1
                        m += 1
                    if head:
                        m = t.index(';', m) + 1; kind = 'type'
                    else: kind = 'func'
                    k = m; break
                db += 1
            elif ch == '}': db -= 1
            elif ch == ';' and dp == 0 and db == 0:
                k += 1
                kind = 'decl' if not (seen_paren and not eq and re.match(r'[^=(]*\w\s*\(', t[j:k], re.S)) else 'proto'
                break
            k += 1
        out.append((lead, kind, t[j:k])); i = k
    return out


def split_top(s, sep=','):
    parts, d, cur, i = [], 0, '', 0
    while i < len(s):
        c = s[i]
        if c == '"':
            j = i + 1
            while s[j] != '"': j += 2 if s[j] == '\\' else 1
            cur += s[i:j + 1]; i = j + 1; continue
        if c in '([{': d += 1
        elif c in ')]}': d -= 1
        if c == sep and d == 0: parts.append(cur); cur = ''
        else: cur += c
        i += 1
    parts.append(cur)
    return parts


def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    return re.sub(r'//[^\n]*', ' ', s)


def no_default(p):
    q = split_top(p, '=')
    return q[0].rstrip()


def wrap(txt, region_start, region_end_marker='int OnInit()'):
    a = txt.index(region_start)
    for x, y in HANDLERS:
        assert txt.count(x) == 1, x
        txt = txt.replace(x, y)
    pre, reg = txt[:a], txt[a:]
    items = scan_items(reg)
    glob, members, ctor, protos, defs = [], [], [], [], []
    # a comment on the same line after a declaration belongs to it (it is the next item's lead up to the first line end)
    items = [list(x) for x in items]
    trail = [''] * len(items)
    for q in range(len(items) - 1):
        if items[q][1] == 'decl':
            ld = items[q + 1][0]; e = ld.find('\n')
            if e > 0 and '//' in ld[:e] and not ld[:e].strip().startswith('/*'):
                trail[q] = ld[:e].strip(); items[q + 1][0] = ld[e:]
    for qi, (lead, kind, s) in enumerate(items):
        if kind == 'tail': defs.append(lead); continue
        assert kind is not None, s[:200]
        if kind in ('pp', 'type'):
            if lead.strip(): defs.append(lead)
            glob.append(s + '\n'); continue
        if kind == 'proto': continue
        if kind == 'decl':
            body = strip_comments(s.rstrip().rstrip(';'))
            assert not re.match(r'\s*(const|static|input|sinput)\b', body), s
            parts = split_top(body)
            typ = None
            for pi, part in enumerate(parts):
                q = split_top(part, '=')
                lhs, init = q[0].strip(), ('='.join(q[1:]).strip() if len(q) > 1 else None)
                m = re.match(r'(.*?)\b(\w+)\s*((?:\[[^\]]*\]\s*)*)$', lhs, re.S)
                assert m, part
                if pi == 0: typ = m.group(1).strip(); assert typ, part
                else: assert not m.group(1).strip(), part
                name, dims = m.group(2), m.group(3).strip()
                assert not (dims and init), part
                members.append('   %s %s%s;' % (typ, name, dims))
                if init is not None: ctor.append('   %s = %s;' % (name, init))
            if lead.strip():
                members[-len(parts):-len(parts)] = ['   ' + ln.strip() for ln in lead.strip('\n').split('\n') if ln.strip()]
            if trail[qi]: members[-1] += "   " + trail[qi]
            continue
        # function
        d = 0; k = 0
        while True:
            if s.startswith('//', k): k = s.find('\n', k); continue
            if s[k] == '"':
                k += 1
                while s[k] != '"': k += 2 if s[k] == '\\' else 1
            elif s[k] == '(': d += 1
            elif s[k] == ')':
                d -= 1
                if d == 0: break
            k += 1
        p0 = s.index('(')
        hd = strip_comments(s[:p0]).strip()
        m = re.match(r'(.*?)\b(\w+)$', hd, re.S)
        assert m, hd
        ret, name = m.group(1).strip(), m.group(2)
        params = strip_comments(s[p0 + 1:k])
        rest = s[k + 1:]
        b = rest.index('{')
        between = rest[:b]
        cq = 'const' if re.search(r'\bconst\b', strip_comments(between)) else ''
        protos.append('   %s %s(%s)%s;' % (ret, name, ' '.join(params.split()), ' ' + cq if cq else ''))
        pdef = ', '.join(no_default(p).strip() for p in split_top(params)) if params.strip() else ''
        defs.append(lead + '%s CLeg::%s(%s)%s' % (ret, name, ' '.join(pdef.split()), between) + rest[b:])
    cls = ['//=== v6.0 TRUE GRID: the whole EA is one class; a leg = one copy (the grid runs leg 0 = VWAP and leg 1 = order block) ===',
           'class CLeg', '{', 'public:', '   long   gMagic;                // this leg\'s magic number (InpMagic + leg)', '   string gPfx;                  // this leg\'s chart object prefix']
    cls += members
    cls += ['   CLeg();'] + protos + ['};', '', 'CLeg::CLeg()', '{', '   gMagic = InpMagic; gPfx = "ARM_";'] + ctor + ['}', '']
    body = ''.join(defs)
    out = pre + ''.join(glob) + '\n' + '\n'.join(cls) + body
    return out


TAIL = r'''
//=== v6.0 the event handlers: leg 0 always; with the true grid also leg 1 (the order block setup, magic + 1) ===
CLeg gEA0;
CLeg gEA1;
bool gGridOn = false;

int OnInit()
{
   gGridOn = InpSetups == SET_GRID;
   gEA0.gLeg = 0; gEA1.gLeg = 1;
   if(gGridOn && AccountInfoInteger(ACCOUNT_LOGIN) != 0 && (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
   {
      string m = "True grid: this account is not a hedging account, so the VWAP leg and the order block leg cannot hold their own trades. Use a hedging account, or choose 'Both: one trade at a time'.";
      Print(m); Alert(m);
      return INIT_PARAMETERS_INCORRECT;
   }
   int r = gEA0.Init();
   if(r != INIT_SUCCEEDED || !gGridOn) return r;
   r = gEA1.Init();
   if(r != INIT_SUCCEEDED) { gEA0.Deinit(REASON_INITFAILED); return r; }
   Print("True grid: the VWAP leg trades with magic ", IntegerToString(gEA0.gMagic), ", the order block leg with magic ", IntegerToString(gEA1.gMagic), ".");
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   gEA0.Deinit(reason);
   if(gGridOn) gEA1.Deinit(reason);
}

void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   gEA0.ChartEvt(id, lparam, dparam, sparam);
   if(gGridOn) gEA1.ChartEvt(id, lparam, dparam, sparam);
}

void OnTick()
{
   gEA0.Tick();
   if(gGridOn) gEA1.Tick();
}
//+------------------------------------------------------------------+
'''


def leg_text(s):
    """inside the class: the magic number and the chart object names are the leg's"""
    s = re.sub(r'\bInpMagic\b', 'gMagic', s)
    s = re.sub(r'"ARM_([^"]*)"', lambda m: 'gPfx' if m.group(1) == '' else '(gPfx + "%s")' % m.group(1), s)
    return s
