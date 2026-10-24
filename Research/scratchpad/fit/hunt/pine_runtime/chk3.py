import sys, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/pine_runtime')
from rt import run
def trig(p, mt, up):
    q = p / mt
    return (math.ceil(q - 1e-7) if up else math.floor(q + 1e-7)) * mt
for sym, mt in (('EURUSD', 1e-5), ('ETH', 0.01)):
    tr, ev, P = run(sym); R = P['rows']
    off = sum(1 for r in R for x in (r['h'], r['l']) if abs(x / mt - round(x / mt)) > 1e-6)
    print(sym, 'offgrid at', mt, off)
    for t in tr:
        d = t['dir']
        for nm, lvl, up in (('lim', t['entry'], d < 0), ('stop', t['stop'], d < 0), ('t4', t['t4'], d > 0)):
            s = trig(lvl, mt, up)
            for r in R[t['fill']: (t['exit'] or t['fill']) + 1]:
                a = (r['h'] >= lvl) if up else (r['l'] <= lvl)
                b = (r['h'] >= s - 1e-9 * mt) if up else (r['l'] <= s + 1e-9 * mt)
                if a != b: print(' mismatch', sym, t['t'], nm, repr(lvl), s, r['h'], r['l'])
