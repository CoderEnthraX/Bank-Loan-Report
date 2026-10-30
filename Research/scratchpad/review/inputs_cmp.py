"""Compare every input.*() call of two Pine files, ignoring the title: prints inputs added/removed and every non-title change."""
import re, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/pinecheck')
from inline_lint import calls, split_args
def inputs(path):
    src = open(path, encoding='utf8').read(); out = {}
    for off, a in calls(src):
        ls = src.rfind('\n', 0, off) + 1; m = re.match(r'\s*(?:var\s+)?(?:\w+\s+)?(\w+)\s*=\s*$', src[ls:off])
        name = m.group(1) if m else 'line%d' % (src.count('\n', 0, off) + 1)
        fn = re.match(r'input\.\w+', src[off:]).group(0)
        args = split_args(a); kw = {}; pos = []
        for x in args:
            mm = re.match(r'^(\w+)\s*=(?!=)\s*(.*)$', x, re.S)
            if mm: kw[mm.group(1)] = mm.group(2).strip()
            else: pos.append(x)
        title = kw.pop('title', pos[1] if len(pos) > 1 else None)
        if len(pos) > 1: pos = pos[:1] + pos[2:]
        out[name] = dict(fn=fn, pos=pos, kw=kw, title=title)
    return out
a, b = inputs(sys.argv[1]), inputs(sys.argv[2])
print('inputs old %d new %d' % (len(a), len(b)))
print('removed:', sorted(set(a) - set(b))); print('added:', sorted(set(b) - set(a)))
nt = 0
for k in sorted(set(a) & set(b)):
    x, y = a[k], b[k]
    if x['title'] != y['title']: nt += 1
    d = []
    if x['fn'] != y['fn']: d.append('fn %s -> %s' % (x['fn'], y['fn']))
    if x['pos'] != y['pos']: d.append('default/pos %s -> %s' % (x['pos'], y['pos']))
    for kk in sorted(set(x['kw']) | set(y['kw'])):
        if x['kw'].get(kk) != y['kw'].get(kk):
            d.append('%s: %s -> %s' % (kk, (x['kw'].get(kk) or '-')[:70], (y['kw'].get(kk) or '-')[:70]))
    if d: print('  %-12s' % k, ' | '.join(d))
print('titles changed:', nt)
