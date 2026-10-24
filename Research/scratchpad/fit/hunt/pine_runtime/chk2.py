import sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/pine_runtime')
from rt import run
def trig(p, mt, up):
    q = p / mt
    return (math.ceil(q - 1e-7) if up else math.floor(q + 1e-7)) * mt
for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    tr, ev, P = run(sym); mt = P['mt']; R = P['rows']
    off = sum(1 for r in R for x in (r['h'], r['l']) if abs(x / mt - round(x / mt)) > 1e-6)
    bad = 0; badfill = 0
    for t in tr:
        d = t['dir']
        # long: limit/stop reached from above (floor), target from below (ceil); short reversed
        for lvl, up in ((t['entry'], d < 0), (t['stop'], d < 0), (t['t4'], d > 0)):
            s = trig(lvl, mt, up)
            # check equivalence on every bar's on-grid extremes: low <= lvl  <=> low <= s ; high >= lvl <=> high >= s
            for r in R[t['fill']: (t['exit'] or t['fill']) + 1]:
                if up: bad += ((r['h'] >= lvl) != (r['h'] >= s - 1e-9))
                else: bad += ((r['l'] <= lvl) != (r['l'] <= s + 1e-9))
    lines = 4 * len(tr); boxes = 2 * len(tr)
    print(f"{sym:7s} offgrid extremes={off} trigTick mismatches={bad} trades={len(tr)} lines={lines} boxes={boxes} trades losing TP/entry lines={max(0,len(tr)-125)} losing boxes={max(0,len(tr)-250)}")
