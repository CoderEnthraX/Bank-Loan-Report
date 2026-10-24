import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
for t in TRADES:
    if not (t['tight'] or (t['sym'] in ('SENSEX',) and t['fill'].startswith('2026-10-09'))): continue
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]; d = t['d']; e = t['entry']
    f = levels(P, i, d, e, A)
    print(t['sym'], t['fill'], 'arm', t['arm'], 'd', d, 'TIGHT' if t['tight'] else 'normal', 'stopR %.2f'%t['stopR'], t['out'], 'A=%.5g'%A, 'entry', e, 'since', P['sinceStart'][i])
    print('   ' + ' '.join('%s=%+.2f' % (k, d*(v-e)/A) for k, v in f.items() if v is not None))
