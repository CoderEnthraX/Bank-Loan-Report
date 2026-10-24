import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pdlib import *
from engine2 import prepare
from tightdata import TRADES
def pdirs(P, i, d):
    Dd = daily(P); k = dayidx(P, i); pd = Dd[k - 1]; p2 = Dd[k - 2]; A = P[('atr', 14)][i]
    out = {}
    out['body'] = d * (pd['c'] - pd['o']) / A
    out['pd2'] = d * (pd['c'] - p2['c']) / A
    out['vw'] = d * (pd['c'] - pd['vw']) / A
    out['pos'] = (((pd['c'] - pd['l']) if d > 0 else (pd['h'] - pd['c'])) / (pd['h'] - pd['l'])) - 0.5
    for kind in ('E1', 'E2'):
        ev = events(P, kind); last = [ev[j] for j in range(pd['a'], pd['b']) if ev[j]]
        out[f'last{kind}'] = d * last[-1] if last else 0
        out[f'maj{kind}'] = d * sum(last)
    out['mid'] = d * (pd['c'] - (pd['h'] + pd['l']) / 2) / A
    out['o2'] = d * (pd['c'] - p2['o']) / A   # 2-day candle
    out['hl'] = d * ((pd['h'] + pd['l']) - (p2['h'] + p2['l'])) / 2 / A  # midpoint migration
    return out
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']
    rows.append((t, {k: first_e(P, i, d, k) for k in ('E1', 'E2', 'E3')}, pdirs(P, i, d)))
for fk in ('E1', 'E2', 'E3'):
    for pk in rows[0][2]:
        for th in (0, -0.5, -1, -2, -3):
            pred = [(f[fk] and p[pk] < th) for t, f, p in rows]
            tp = sum(1 for x, (t, _, _) in zip(pred, rows) if x and t['tight']); fp = sum(1 for x, (t, _, _) in zip(pred, rows) if x and not t['tight'])
            if tp >= 7: print(fk, pk, '<', th, 'TP', tp, 'FP', fp, [f"{t['sym']} {t['fill'][5:]}" for x, (t, _, _) in zip(pred, rows) if x and not t['tight']], 'FN', [f"{t['sym']} {t['fill'][5:]}" for x, (t, _, _) in zip(pred, rows) if not x and t['tight']])
