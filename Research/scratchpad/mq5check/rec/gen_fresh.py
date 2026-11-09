"""gen_fresh.py EA.mq5 -> C++ rec_fresh(): every global of the EA's '//--- globals' block back to its declared initial value (or 0 / false /
"" / empty array), i.e. what a fresh program load gives. Used by the restart-memory test (rec_restart)."""
import sys, re
src = open(sys.argv[1], encoding='utf8').read().split('\n')
a = next(i for i, l in enumerate(src) if l.startswith('//--- globals')); b = next(i for i in range(a + 1, len(src)) if src[i].startswith('//--- helpers'))
TYPES = ('double', 'int', 'bool', 'long', 'ulong', 'datetime', 'string', 'color', 'uint')
DEF = {'bool': 'false', 'string': '""'}
out = ['extern "C" void rec_fresh()', '{']; names = []
for line in src[a + 1:b]:
    code = line.split('//')[0].strip()
    if not code or not code.split()[0] in TYPES: continue
    for stmt in code.split(';'):
        stmt = stmt.strip()
        if not stmt: continue
        m = re.match(r'(%s)\s+(.*)$' % '|'.join(TYPES), stmt)
        assert m, stmt
        ty, rest = m.group(1), m.group(2)
        for d in rest.split(','):
            d = d.strip(); init = None
            if '=' in d: d, init = [x.strip() for x in d.split('=', 1)]
            am = re.match(r'(\w+)\s*\[\s*(\w*)\s*\]$', d)
            if am:
                nm, sz = am.group(1), am.group(2)
                if sz: out.append('   for(int q_ = 0; q_ < %s; q_++) %s[q_] = %s;' % (sz, nm, DEF.get(ty, '0')))
                else: out.append('   ArrayResize(%s, 0);' % nm)
            else:
                nm = d; assert re.match(r'^\w+$', nm), d
                out.append('   %s = %s;' % (nm, init if init is not None else DEF.get(ty, '0')))
            names.append(nm)
out.append('}')
print('\n'.join(out))
sys.stderr.write('rec_fresh: %d globals\n' % len(names))
