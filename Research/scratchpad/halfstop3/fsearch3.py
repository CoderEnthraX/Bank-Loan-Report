"""Single-feature rule search on the labeled table. Positives HALF, negatives norm. Trigger = model half flag (halfCap on)."""
import sys, io, contextlib, os
os.environ['INP'] = '{"halfCap": true}'
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
import r3
from engine import rma
IM = {}
def imps(sym):
    if sym not in IM:
        r3.IMPS = []; r3.run(sym, tab3.inp); IM[sym] = list(r3.IMPS); r3.IMPS = None
    return IM[sym]
rows = []
for r in tab3.rows:
    if r['m'] is None or r['lab'] not in ('HALF', 'norm'): continue
    F = r['F']; d = r['d']; P = r['P']; j = r['j']; A = r['A']; e = r['e']; C, O, H, L, V = P['C'], P['O'], P['H'], P['L'], P['V']
    s0 = j - F['vwBars']; tr = P['tr']
    if ('a100',) not in P: P[('a100',)] = rma(tr, 100)
    seq = [s for i, s, *_ in imps(P['sym']) if s0 <= i < j]
    f = dict(k=F['vwBars'], hour=int(P['T'][j][11:13]) + int(P['T'][j][14:16]) / 60, rngA=(H[j] - L[j]) / A, cVW=d * (C[j] - V[j]) / A, eVW=d * (e - V[j]) / A,
             gap=d * (O[s0] - C[s0 - 1]) / A, oVW=d * (O[s0] - V[s0 - 1]) / A, AA0=A / rma(tr, 14)[s0], A100=A / P[('a100',)][j], trA=tr[j] / A,
             sigLow=d * (e - (L[j] if d > 0 else H[j])) / A, sw10=d * (e - (min(L[j-9:j+1]) if d > 0 else max(H[j-9:j+1]))) / A,
             sesExt=d * (e - (min(L[s0:j+1]) if d > 0 else max(H[s0:j+1]))) / A, prevNet=d * (F['prevNet'] or 0),
             curNet=d * sum(seq), sameN=sum(1 for s in seq if s == d), oppN=sum(1 for s in seq if s == -d), maxTR10=max(tr[j-9:j+1]) / A)
    y = r['lab'] == 'HALF'; m = r['m']['half']
    rows.append((r['src'] + ' ' + P['sym'][:6] + ' ' + r['ft'], y, m, f))
base = [x for x in rows if x[1] != x[2]]
print('base errors', len(base), [x[0] for x in base])
res = []
for fn in rows[0][3]:
    vals = sorted(set(x[3][fn] for x in rows))
    for t in vals:
        for op in ('>=', '<='):
            ok = (lambda v: v >= t) if op == '>=' else (lambda v: v <= t)
            for mode in ('AND', 'OR'):
                err = [x[0] for x in rows if ((x[2] and ok(x[3][fn])) if mode == 'AND' else (x[2] or ok(x[3][fn]))) != x[1]]
                res.append((len(err), fn, op, round(t, 3), mode, err))
res.sort(key=lambda z: z[0])
for z in res[:25]: print(z[0], z[1], z[2], z[3], z[4], z[5] if z[0] <= 4 else '')
if len(sys.argv) > 1:
    for nm, y, m, f in rows:
        if m or y: print(f"{nm:34s} y{'H' if y else 'n'} m{'H' if m else 'n'} " + ' '.join(f"{k} {f[k]:+.2f}" for k in ('k', 'gap', 'maxTR10', 'trA', 'AA0', 'A100', 'prevNet', 'oppN', 'sigLow', 'eVW')))
