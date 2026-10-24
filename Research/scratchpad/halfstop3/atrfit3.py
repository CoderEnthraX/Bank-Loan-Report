import sys, io, contextlib
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
from engine import rma
R = [r for r in tab3.rows if r['m'] is not None and r['lab'] in ('norm', 'other') and r['src'] != 'BCR#58' ]
def sma(x, n): return [None if i < n - 1 else sum(x[i-n+1:i+1]) / n for i in range(len(x))]
def ema(x, n):
    a = 2 / (n + 1); o = []; v = None
    for z in x: v = z if v is None else a * z + (1 - a) * v; o.append(v)
    return o
V = {}
def variants(P):
    H, L, tr, ds = P['H'], P['L'], P['tr'], P['daystart']
    hl = [h - l for h, l in zip(H, L)]
    trs = [hl[i] if ds[i] else tr[i] for i in range(len(tr))]  # session-first bar TR -> HL
    out = {'rma14': rma(tr, 14), 'rmaHL14': rma(hl, 14), 'rmaTRs14': rma(trs, 14), 'sma14': sma(tr, 14), 'ema14': ema(tr, 14)}
    for n in (10, 20, 50): out['rma%d' % n] = rma(tr, n)
    return out
res = {}
for r in R:
    P = r['P']
    if P['sym'] not in V: V[P['sym']] = variants(P)
    for k, a in V[P['sym']].items():
        A = a[r['j']]
        if A is None: continue
        sr = r['d'] * (r['e'] - r['logStop']) / A
        ok = abs(sr - 1.8) <= 0.12
        res.setdefault(k, []).append((ok, r['src'], r['sym'][:8], r['ft'], round(sr, 2)))
for k, v in res.items():
    print(k, 'ok', sum(o for o, *_ in v), '/', len(v), ' notOK:', [(s, t, x) for o, s, y, t, x in v if not o][:14])
