import sys, struct; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import run, tr_series, day_starts, MINTICK
from arp_data import load
from decimal import Decimal
def f32(x): return struct.unpack('f', struct.pack('f', x))[0]
modes = {'none': lambda x, mt: x, 'mul': lambda x, mt: round(x/mt)*mt, 'f32': lambda x, mt: f32(x),
         'mulinv': lambda x, mt: round(x/mt)*(1/round(1/mt)) }
for sym in sys.argv[2:]:
  for m in sys.argv[1].split(','):
    rows = load(sym); mt = MINTICK[sym]; fn = modes[m]
    for r in rows:
        for k in ('o','h','l','c'): r[k] = fn(r[k], mt)
    P = dict(sym=sym, rows=rows, mt=mt, tr=tr_series(rows), daystart=day_starts(rows))
    tr = run(P); mine = {(t['fill'], t['dir']) for t in tr}
    csv = {(r['i'], 1 if r['lf'] else -1) for r in rows if r['lf'] or r['sf']}
    a = {x for x in mine if x[0] >= 1500}; b = {x for x in csv if x[0] >= 1500}
    print(m, sym, 'both', len(a & b), 'only_port', len(a - b), 'only_csv', len(b - a), sorted(a ^ b)[:6])
