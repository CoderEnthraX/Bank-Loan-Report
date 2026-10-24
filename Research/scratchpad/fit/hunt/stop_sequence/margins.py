import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare
from nearsig import conds
from daily2 import daily2, dayidx2
CASES = [('CRUDE','2026-10-08 10:45',1,'N'),('NASDAQ','2026-10-12 06:15',-1,'N'),('NIFTY','2026-10-12 09:50',-1,'N'),('US30','2026-10-07 05:10',-1,'N'),
         ('CRUDE','2026-10-09 10:25',-1,'T'),('EURUSD','2026-10-09 15:25',-1,'T'),('GC','2026-10-07 05:55',-1,'T'),('GC','2026-10-08 04:45',1,'T'),('GC','2026-10-09 18:20',-1,'T'),
         ('NASDAQ','2026-10-09 06:00',1,'T'),('NIFTY','2026-10-05 09:25',1,'T'),('NIFTY','2026-10-09 10:05',1,'T')]
for s, ta, d, lab in CASES:
    P = prepare(s); i = P['T'].index(ta); ds = daily2(P)[dayidx2(P, i)]['a']
    O, H, L, C, V = P['O'], P['H'], P['L'], P['C'], P['V']; A = P[('atr', 14)]
    out = []
    for j in range(ds, i):
        r = conds(P, j, d)
        if not r or not r['dir']: continue
        a = A[j]; rng = H[j] - L[j]
        m = dict(rng=rng / a, body=abs(C[j] - O[j]) / rng, clos=((H[j] - C[j]) if d > 0 else (C[j] - L[j])) / rng,
                 brk=d * (C[j] - (max(H[j-10:j]) if d > 0 else min(L[j-10:j]))) / a, vw=d * (C[j] - V[j]) / a, mom=d * (C[j] - C[j-10]) / a)
        fails = [k for k in ('rng', 'body', 'clos', 'brk', 'vw', 'mom', 'vsl') if not r[k]]
        if len(fails) <= 2:
            out.append(f"{P['T'][j][11:]} fail={'/'.join(fails)} rng={m['rng']:.2f} body={m['body']:.2f} clos={m['clos']:.2f} brk={m['brk']:+.2f} vw={m['vw']:+.2f} mom={m['mom']:+.2f}")
    print(f"== {s} {ta} {'L' if d>0 else 'S'} {lab}")
    for o in out: print('    ', o)
