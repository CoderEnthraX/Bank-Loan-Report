"""v6.0 grid file: names declared at the slot loop's top level must not be used after the loop; no history references / ta.* calls of
user series inside the loop (only high / low / close / open / time of the chart). Usage: loop_audit.py FILE.pine"""
import re, sys
L = open(sys.argv[1]).read().split('\n')
a = next(i for i, l in enumerate(L) if l.startswith('for slot = 0 to'))
b = next(i for i in range(a + 1, len(L)) if L[i].strip() and not L[i].startswith(' ') and not L[i].startswith('//'))
DECL = re.compile(r'^ {12}(?:(?:float|int|bool|string|color|line|box|label|array<[^>]+>)\s+)?([A-Za-z_]\w*)\s*=(?!=)')
TUP = re.compile(r'^ {12}\[([^\]]+)\]\s*=')
names = set()
for l in L[a:b]:
    m = DECL.match(l)
    if m: names.add(m.group(1))
    m = TUP.match(l)
    if m: names.update(x.strip() for x in m.group(1).split(','))
post = '\n'.join(re.sub(r'//.*', '', x) for x in L[b:])
used = sorted(n for n in names if re.search(r'(?<![\w.])' + n + r'\b', post))
body = re.sub(r'//.*', '', '\n'.join(L[a:b]))
hist = sorted(set(x for x in re.findall(r'\b(\w+)\[(?:\d+|j)\]', body) if x not in ('high', 'low', 'close', 'open', 'time')))
print('loop lines %d-%d, top-level names %d, used after the loop: %s, user history refs: %s, ta.* calls: %s' % (a + 1, b, len(names), used or 'none', hist or 'none', re.findall(r'\bta\.\w+', body) or 'none'))
