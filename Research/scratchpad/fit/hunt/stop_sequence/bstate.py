"""Bias state machine: B reset at session start to previous session candle dir; updated by each raw displacement (event set E)."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare
from tightdata import TRADES
from bias import daily, dayidx
from nearsig import conds
from sig import raw
def events(P, kind):
    key = ('ev', kind)
    if key in P: return P[key]
    n = len(P['T']); S = raw(P)
    if kind == 'E1': ev = list(S)
    else:
        need = {'E2': ('dir','rng','body','clos','brk','vw','mom','vsl'), 'E3': ('dir','rng','body','clos','brk','vw','vsl')}[kind]
        ev = [0] * n
        for i in range(11, n):
            if P[('atr', 14)][i] is None: continue
            for d in (1, -1):
                r = conds(P, i, d)
                if r and all(r[k] for k in need): ev[i] = d
    P[key] = ev; return ev
def bstate(P, i, kind, reset='pdDir'):
    ev = events(P, kind); D = daily(P); k = dayidx(P, i); pd = D[k - 1]
    if reset == 'pdDir': B = 1 if pd['c'] > pd['o'] else -1
    elif reset == 'pd2': B = 1 if pd['c'] > D[k - 2]['c'] else -1
    elif reset == 'none':
        B = 0
        for j in range(i - 1, -1, -1):
            if ev[j]: B = ev[j]; break
        return B
    for j in range(D[k]['a'], i):
        if ev[j]: B = ev[j]
    return B
if __name__ == '__main__':
    for kind in ('E1', 'E2', 'E3'):
        for reset in ('pdDir', 'pd2', 'none'):
            tp = fp = 0; fps = []; fns = []
            for t in TRADES:
                P = prepare(t['sym']); B = bstate(P, t['arm_i'], kind, reset); pred = (B == -t['d'])
                if pred and t['tight']: tp += 1
                elif pred: fp += 1; fps.append(f"{t['sym']} {t['fill'][5:]}")
                elif t['tight']: fns.append(f"{t['sym']} {t['fill'][5:]}")
            print(kind, reset, 'TP', tp, 'FP', fp, 'FN', fns, 'FPs', fps)
