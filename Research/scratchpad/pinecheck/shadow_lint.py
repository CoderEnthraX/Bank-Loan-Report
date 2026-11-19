"""TradingView warns "Shadowing variable 'x' which exists in parent scope" when a local scope (indented block or function body) declares
(with '=', not ':=') a name that a parent scope already declared. This lists every such case: names declared at the top level
(variables, tuple elements, inputs) vs declarations and function parameters inside indented blocks / functions. Comments and strings removed."""
import re, sys
TYPES = r'(?:float|int|bool|string|color|table|line|label|box|linefill|polyline|chart\.point|map<[^>]+>|array<[^>]+>|matrix<[^>]+>)'
DECL = re.compile(r'^(\s*)(?:var\s+|varip\s+)?(?:' + TYPES + r'\s+)?([A-Za-z_]\w*)\s*=(?!=)')
TUP = re.compile(r'^(\s*)\[([^\]]+)\]\s*=(?!=)')
FN = re.compile(r'^([A-Za-z_]\w*)\s*\(([^)]*)\)\s*=>')


def strip(line):
    out, q = [], None
    i = 0
    while i < len(line):
        ch = line[i]
        if q:
            if ch == '\\': i += 2; continue
            if ch == q: q = None
            i += 1; continue
        if ch in '"\'': q = ch; i += 1; continue
        if line.startswith('//', i): break
        out.append(ch); i += 1
    return ''.join(out)


for p in sys.argv[1:]:
    lines = [strip(l.rstrip('\n')) for l in open(p, encoding='utf8')]
    glob = {}
    for n, l in enumerate(lines, 1):
        m = DECL.match(l)
        if m and m.group(1) == '': glob.setdefault(m.group(2), n)
        m = TUP.match(l)
        if m and m.group(1) == '':
            for v in m.group(2).split(','): glob.setdefault(v.strip(), n)
        m = FN.match(l)
        if m: glob.setdefault(m.group(1), n)
    bad = []
    for n, l in enumerate(lines, 1):
        m = FN.match(l)
        if m:
            for prm in m.group(2).split(','):
                w = prm.strip().split()
                if w and w[-1].split('=')[0].strip() in glob: bad.append((n, w[-1], 'parameter'))
        m = DECL.match(l)
        if m and m.group(1) != '' and m.group(2) in glob: bad.append((n, m.group(2), 'local, global at line %d' % glob[m.group(2)]))
        m = TUP.match(l)
        if m and m.group(1) != '':
            for v in m.group(2).split(','):
                if v.strip() in glob: bad.append((n, v.strip(), 'tuple, global at line %d' % glob[v.strip()]))
    print('%s: %d shadowing declarations' % (p.split('/')[-1], len(bad)))
    for b in bad: print('   line %d: %s (%s)' % b)
