"""Pine warns 'Shadowing variable x which exists in parent scope' when a block declares a name that a global (or an enclosing block)
already declares. Lists every indented declaration (and function / method parameter) whose name is declared at column 0."""
import re, sys
src = open(sys.argv[1], encoding='utf8').read().split('\n')
TYPES = r'(?:var\s+|varip\s+)?(?:(?:int|float|bool|string|color|line|label|table|box|array<\w+>|Strat)\s+)?'
glob = set()
for l in src:
    m = re.match(r'^' + TYPES + r'(\w+)\s*=[^=>]', l)
    if m: glob.add(m.group(1))
    m = re.match(r'^\[([\w\s,]+)\]\s*=', l)
    if m: glob.update(x.strip() for x in m.group(1).split(','))
    m = re.match(r'^(?:method\s+)?(\w+)\(', l)
    if m: glob.add(m.group(1))
bad = []
for n, l in enumerate(src, 1):
    if l.startswith((' ', '\t')) and not l.strip().startswith('//'):
        m = re.match(r'^\s+' + TYPES + r'(\w+)\s*=[^=>]', l)
        if m and m.group(1) in glob: bad.append((n, m.group(1), l.strip()[:80]))
        m = re.match(r'^\s+\[([\w\s,]+)\]\s*=', l)
        if m:
            for x in m.group(1).split(','):
                if x.strip() in glob: bad.append((n, x.strip(), l.strip()[:80]))
        m = re.match(r'^\s+for\s+(?:\[(\w+),\s*(\w+)\]|(\w+))\s', l)
        if m:
            for x in m.groups():
                if x and x in glob: bad.append((n, x, l.strip()[:80]))
    m = re.match(r'^(?:method\s+)?\w+\((.*)\)\s*=>', l)
    if m:
        for a in m.group(1).split(','):
            w = a.strip().split()
            if w and w[-1] in glob: bad.append((n, w[-1], 'parameter: ' + l[:80]))
print('%s: %d possible shadowing warnings' % (sys.argv[1].split('/')[-1], len(bad)))
for b in bad: print('   line %d: %s | %s' % b)
