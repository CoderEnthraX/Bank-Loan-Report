"""Tight iff HTF trend T against d AND no displacement event in d since (a) session start, (b) T turned against d, (c) max(a,b)."""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
import importlib.util
spec = importlib.util.spec_from_file_location('fdp', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/rule_firstday_prevday.py'); fdp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fdp)
from tightdata import TRADES
def trend(P, kind, th):
    key = ('trend', kind, th)
    if key in P: return P[key]
    n = len(P['T']); out = [0] * n
    if kind.startswith('h'):
        m, f = kind[1:].split('_'); S = htf_series(P, int(m))
        for i in range(n):
            s = S[i]
            if s is None: continue
            v = s[f]
            out[i] = 1 if v > th else (-1 if v < -th else 0)
    elif kind == 'pd':
        out_, idx = fdp._daily(P)
        for i in range(n):
            k = idx[i]
            if k == 0: continue
            po, pc = out_[k - 1][2], out_[k - 1][3]; A = P[('atr', 14)][i] or 1
            v = (pc - po) / A; out[i] = 1 if v > th else (-1 if v < -th else 0)
    elif kind.startswith('ema'):
        a, b = map(int, kind[3:].split('_')); ea, eb = ema(P['C'], a), ema(P['C'], b)
        for i in range(n):
            A = P[('atr', 14)][i] or 1; v = (ea[i] - eb[i]) / A; out[i] = 1 if v > th else (-1 if v < -th else 0)
    P[key] = out; return out
def is_tight(P, i, d, kind, th, since):
    T = trend(P, kind, th)
    if T[i] != -d: return False
    out_, idx = fdp._daily(P); a = out_[idx[i]][0]
    b = i
    while b > 0 and T[b - 1] == -d: b -= 1
    start = {'sess': a, 'flip': b, 'both': max(a, b), 'none': i}[since]
    return not any(fdp._event(P, j, d) for j in range(start, i))
if __name__ == '__main__':
    res = []
    kinds = [('pd', [0, 1, 2]), ('h30_e2050', [0, 0.25, 0.5]), ('h60_e2050', [0, 0.25, 0.5]), ('h120_e2050', [0, 0.25, 0.5]), ('h240_e2050', [0, 0.25, 0.5]),
             ('h60_spr', [0, 5, 10]), ('h120_spr', [0, 5, 10]), ('h240_spr', [0, 5, 10]), ('h120_ers', [0, 0.1, 0.2]), ('h240_ers', [0, 0.1]),
             ('ema50_200', [0, 0.5, 1]), ('ema20_50', [0, 0.5, 1]), ('ema100_200', [0, 0.5])]
    for kind, ths in kinds:
        for th in ths:
            for since in ('sess', 'flip', 'both', 'none'):
                tp = fp = 0; fps = []
                for t in TRADES:
                    P = get(t['sym']); pr = is_tight(P, t['arm_i'], t['d'], kind, th, since)
                    if pr and t['tight']: tp += 1
                    elif pr: fp += 1; fps.append(f"{t['sym']} {t['fill'][5:]}")
                res.append((8 - tp + fp, tp, fp, kind, th, since, fps if fp <= 4 else ''))
    res.sort(key=lambda x: x[0])
    for r in res[:30]: print(r)
