# session-anchored HTF ATR (bucket = session, floor(minutes since session start / m)), as TradingView aligns intraday HTF bars to the session
import sys, pickle
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
def htf_sess(P, m, L, mode, inc):
    key = ('htfs', m, L, mode, inc)
    if key in P: return P[key]
    O, H, Lo, C = P['O'], P['H'], P['L'], P['C']; n = len(O)
    sess = 0; bid = []; prev = None
    for i in range(n):
        if P['daystart'][i] and i: sess += 1
        bid.append((sess, P['sinceStart'][i] * 5 // m))
    fin = []; out = [None] * n; cur = None; cb = None; prevC = None; s = None
    a = 2 / (L + 1)
    for i in range(n):
        if bid[i] != cb:
            if cur is not None:
                tr = cur[1] - cur[2] if prevC is None else max(cur[1] - cur[2], abs(cur[1] - prevC), abs(cur[2] - prevC))
                fin.append(tr); prevC = cur[3]
                if len(fin) >= L:
                    if mode == 'sma': s = sum(fin[-L:]) / L
                    elif s is None: s = sum(fin[-L:]) / L
                    elif mode == 'rma': s = (s * (L - 1) + tr) / L
                    else: s = a * tr + (1 - a) * s
            cur = [O[i], H[i], Lo[i], C[i]]; cb = bid[i]
        else:
            cur[1] = max(cur[1], H[i]); cur[2] = min(cur[2], Lo[i]); cur[3] = C[i]
        if s is None: continue
        if not inc: out[i] = s; continue
        trc = cur[1] - cur[2] if prevC is None else max(cur[1] - cur[2], abs(cur[1] - prevC), abs(cur[2] - prevC))
        if mode == 'rma': out[i] = (s * (L - 1) + trc) / L
        elif mode == 'sma': out[i] = (sum(fin[-(L - 1):]) + trc) / L
        else: out[i] = a * trc + (1 - a) * s
    P[key] = out; return out
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr', 14)][i]; f = {}
    for m in (15, 30, 60, 120, 240):
        for L in (5, 14):
            for mode in ('rma', 'sma', 'ema'):
                for inc in (True, False):
                    v = htf_sess(P, m, L, mode, inc)[i]
                    if v: f[f'hs{m}_{mode}{L}_{"c" if inc else "p"}'] = v / A
    rows.append((t, f))
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat6.pkl', 'wb'))
