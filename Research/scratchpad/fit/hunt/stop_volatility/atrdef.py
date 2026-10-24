import sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility')
from vlib import *
from tightdata import TRADES
defs = {}
def get(P, name):
    mode, Ln, lag = name
    fn = dict(rma=rma, sma=sma, ema=ema, wma=wma)[mode]
    return series(P, ('atrv', mode, Ln), lambda: fn(P['tr'], Ln))
res = []
for mode in ('rma', 'sma', 'ema', 'wma'):
    for Ln in (5, 7, 10, 12, 13, 14, 15, 16, 20, 21, 50):
        for lag in (0, 1):
            nr = []; tt = []
            for t in TRADES:
                P = prepare(t['sym']); s = get(P, (mode, Ln, lag)); i = t['arm_i'] - lag
                if s[i] is None: continue
                r = t['d'] * (t['entry'] - t['stop']) / s[i]
                (tt if t['tight'] else nr).append(r)
            m = sum(nr) / len(nr); sd = math.sqrt(sum((x - m) ** 2 for x in nr) / len(nr))
            mad = sorted(abs(x - 1.8) for x in nr)[len(nr) // 2]
            res.append((sd, mode, Ln, lag, m, mad, [round(x, 3) for x in tt]))
res.sort()
for r in res[:15]: print(f"{r[1]}{r[2]} lag{r[3]} normal mean {r[4]:.4f} sd {r[0]:.4f} medAbsDev(1.8) {r[5]:.4f} tight {r[6]}")
