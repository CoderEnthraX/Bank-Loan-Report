import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
import r3
from engine2 import prepare
o = json.loads(sys.argv[1]); base = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
tot = 0; ch = 0
for sym in ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']:
    T = prepare(sym)['T']
    a = {(x['dir'], x['fill']): x for x in r3.shown(sym, base)}; b = {(x['dir'], x['fill']): x for x in r3.shown(sym, dict(base, **o))}
    tot += len(a)
    for k in sorted(set(a) | set(b), key=lambda z: z[1]):
        x, y = a.get(k), b.get(k)
        if x and y and abs(x['stop'] - y['stop']) < 1e-9 and x['exit'] == y['exit']: continue
        ch += 1
        f = lambda z: 'none' if z is None else f"stop {z['stop']:.2f} {'H' if z['half'] else 'n'} exit {T[z['exit']] if z['exit'] is not None else None} res {z['res']}"
        print(sym, T[k[1]], 'L' if k[0] > 0 else 'S', '| old', f(x), '| new', f(y))
print('changed', ch, 'of', tot)
