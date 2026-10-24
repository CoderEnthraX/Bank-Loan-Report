"""Search REGIME formula families consistent with the table snapshots (realtime frames: allow any bar of the candidate set)."""
import sys, itertools; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
SN = [('CRUDE', ['2026-10-09 13:40'], 'X'), ('EURUSD', ['2026-10-12 12:50', '2026-10-12 12:55'], 'X'),
      ('GC', ['2026-10-12 12:45', '2026-10-12 12:50', '2026-10-12 12:55'], 'X'), ('GC', ['2026-10-12 12:45', '2026-10-12 12:50', '2026-10-12 12:55'], 'R'),
      ('NASDAQ', ['2026-10-12 12:50'], 'R'), ('NASDAQ', ['2026-10-09 13:40'], 'R'), ('NIFTY', ['2026-10-12 12:40'], 'T'),
      ('NIFTY', ['2026-10-12 12:05', '2026-10-12 12:30'], 'T'), ('SENSEX', ['2026-10-12 12:40'], 'X'), ('US30', ['2026-10-12 12:50'], 'R')]
def F(P, i):
    f = feats(P, i); A = P[('atr', 14)][i]; tr = P['tr']
    f['atr_r50'] = A / (sum(tr[i - 49:i + 1]) / 50); f['atr_r100'] = A / (sum(tr[i - 99:i + 1]) / 100)
    f['abs_spr'] = abs(f['spr']); f['abs_cv'] = abs(f['cv']); f['abs_cvs'] = abs(f['cvs']); f['abs_vsl10'] = abs(f['vsl10'])
    f['abs_e2050'] = abs(f['e2050']); f['abs_ce20'] = abs(f['ce20']); f['abs_lr20'] = abs(f['lr20']); f['abs_lr50'] = abs(f['lr50'])
    f['er50'] = er(P['C'], i, 50); f['chop50'] = chop(P, i, 50)
    for m in (15, 30, 60, 240):
        p, q, a, rows = htf_dmi_at(P, m, i); f[f'h{m}adx'] = a; f[f'h{m}absspr'] = abs(p - q)
    return f
data = []
for s, ts, lab in SN:
    P = get(s); data.append((s, lab, [F(P, P['T'].index(t)) for t in ts]))
keys = list(data[0][2][0].keys())
def cls(f, k1, c1, s1, t, k2, c2, s2):
    if s1 * (f[k1] - c1) >= 0: return 'R'
    if f['adx'] >= t and (k2 is None or s2 * (f[k2] - c2) >= 0): return 'T'
    return 'X'
def cands(k):
    v = sorted(set(round(f[k], 3) for _, _, fs in data for f in fs))
    return [(a + b) / 2 for a, b in zip(v, v[1:])]
best = []
use = [d for d in data if d[0] != 'US30']
for k1 in keys:
    for c1 in cands(k1):
        for s1 in (1, -1):
            # first check RANGING consistency quickly
            ok = 0
            for s, lab, fs in use:
                if any((s1 * (f[k1] - c1) >= 0) == (lab == 'R') for f in fs): ok += 1
            if ok < len(use): continue
            for t in (20, 22, 25, 28, 30, 32, 35):
                for k2 in [None] + keys:
                    for c2 in ([0] if k2 is None else cands(k2)):
                        for s2 in ((1,) if k2 is None else (1, -1)):
                            n = sum(1 for s, lab, fs in use if any(cls(f, k1, c1, s1, t, k2, c2, s2) == lab for f in fs))
                            if n == len(use):
                                us = data[-1]; u = cls(us[2][0], k1, c1, s1, t, k2, c2, s2)
                                best.append((k1, round(c1, 2), s1, t, k2, round(c2, 2) if k2 else None, s2, 'US30=' + u))
print(len(best), 'consistent formulas (9 frames excl US30)')
from collections import Counter
print(Counter(b[0] for b in best).most_common(20))
print(Counter((b[0], b[4]) for b in best).most_common(40))
for b in best[:10]: print(b)
for k in ('chop14', 'er10', 'abs_cvs'):
    cs = sorted(set((b[1], b[2]) for b in best if b[0] == k)); print(k, cs)
print('h240adx variants:', sorted(set((b[3], b[5], b[6], b[7]) for b in best if b[0] == 'chop14' and b[4] == 'h240adx')))
print('er50 variants:', sorted(set((b[3], b[5], b[6], b[7]) for b in best if b[0] == 'chop14' and b[4] == 'er50')))
print('no-k2 variants:', [b for b in best if b[4] is None])
for s, lab, fs in data:
    print(s, lab, [(round(f['chop14'],1), round(f['er10'],2), round(f['adx'],1), round(f['er50'],2), round(f['h240adx'],1)) for f in fs])
