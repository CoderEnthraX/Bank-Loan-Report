import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/pine_runtime')
from rt import run
tot = 0; bad = 0; beyond = 0
for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    tr, ev, P = run(sym); R = P['rows']
    for t in tr:
        tot += 1
        beyond += t['dir'] * (t['entry'] - R[t['arm']]['c']) > 0
        if not (R[t['fill']]['l'] <= t['entry'] <= R[t['fill']]['h']): bad += 1; print(sym, t['t'], 'gap fill', t['dir'], t['entry'], R[t['fill']])
print('default: trades', tot, 'limit beyond close', beyond, 'fill price untraded (gap)', bad)
