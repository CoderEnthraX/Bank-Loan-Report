"""compare the broker deals (time, side, volume, price, profit, reason) of simulator runs, per magic number"""
import re, sys
def deals(f, magic=None):
    out = []
    for l in open(f):
        if not l.startswith('SIM DEAL'): continue
        m = re.search(r'magic=(\d+)', l); mg = int(m.group(1))
        if magic is not None and mg != magic: continue
        x = re.sub(r'tk=\d+ pos=\d+ ', '', l.strip())
        x = re.sub(r' magic=\d+', '', x)
        out.append(x)
    return out
def same(a, b, name):
    print('%-40s %5d vs %5d deals: %s' % (name, len(a), len(b), 'IDENTICAL' if a == b else 'DIFFERENT'))
    if a != b:
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y: print('   first diff', i, '\n   ', x, '\n   ', y); break
same(deals('r_base.log'), deals('r_g0.log'), 'v5.40 EA vs grid EA (VWAP only)')
same(deals('r_ob.log'), deals('r_g1.log'), 'OrderBlockEA vs grid EA (order block only)')
same(deals('r_base.log'), deals('r_g3.log', 240611), 'v5.40 EA vs grid leg 1 (magic 240611)')
same(deals('r_ob.log'), deals('r_g3.log', 240612), 'OrderBlockEA vs grid leg 2 (magic 240612)')
print('grid run magics:', sorted(set(re.search(r'magic=(\d+)', l).group(1) for l in open('r_g3.log') if l.startswith('SIM DEAL'))))
for f in ('r_base.log', 'r_ob.log', 'r_g0.log', 'r_g1.log', 'r_g2.log', 'r_g3.log'):
    t = open(f).read()
    print(f, 'rejects', t.count('SIM REJECT'), 'alerts', t.count('ALERT '), 'deals', t.count('SIM DEAL'))
