import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/extras')
from lib import *
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
P, tr = mine(sym, cfg())
T = P['T']; A = P[('atr', 14)]
print('MINE:')
for m in tr:
    if a <= T[m['fill']] <= b:
        print(' ', 'L' if m['dir'] > 0 else 'S', 'arm', T[m['arm']], 'fill', T[m['fill']], 'exit', T[m['exit']] if m['exit'] is not None else None, m['res'], 'e %.6g s %.6g R/A %.2f' % (m['entry'], m['stop'], m['dir']*(m['entry']-m['stop'])/A[m['arm']]))
print('GT:')
for g in gt(sym):
    if a <= g['fill'] <= b: print(' ', 'L' if g['d'] > 0 else 'S', 'fill', g['fill'], 'exit', g['exit'], g['out'], 'e', g['entry'], 's', g['stop'])
print('RAW SIGNALS:')
for i, t in enumerate(T):
    if a <= t <= b:
        s = sig(P, i)
        if s: print('  ', t, 'L' if s > 0 else 'S', 'daystart' if P['daystart'][i] else '')
print('WINDOWS:', [(w['a'], w['b']) for w in WIN if w['sym'] == sym])
