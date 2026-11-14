"""Interpretation checks on the 9 table strategies (M1 execution): as read (Right = first number), Right / Left swapped, BE off,
salvage off, both off, and the M5 / M15 chart execution (what TradingView computes on those charts)."""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import engine as EN
from run9 import T9
B = EN.load()
def line(tag, rows):
    tot = sum(r['R'] for r in rows); print('%-22s total %+7.1fR | %s' % (tag, tot, ' '.join('S%d %+6.1fR/%4.1fdd' % (i + 1, r['R'], r['ddR']) for i, r in enumerate(rows))))
var = {'as read': lambda p: p, 'right/left swapped': lambda p: (p[0], p[2], p[1]) + p[3:], 'BE off': lambda p: p[:6] + (0.0, p[7]),
       'salvage off': lambda p: p[:7] + (0.0,), 'BE + salvage off': lambda p: p[:6] + (0.0, 0.0)}
for tag, f in var.items():
    rows = []
    for p in T9:
        q = f(p); rows.append(EN.stats(EN.run(B, 'M1', *q), q[4]))
    line(tag, rows)
for ctf in ('M5', 'M15'):
    rows = [EN.stats(EN.run(B, ctf, *p), p[4]) for p in T9]; line('chart ' + ctf, rows)
