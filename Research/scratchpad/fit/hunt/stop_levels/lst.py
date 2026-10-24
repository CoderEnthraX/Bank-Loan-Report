import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from dispser import *
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
    g = pfeat(P, i, t['d'], t['entry'], A)
    if g['n_same_sess'] == 0 or g['n_same24'] == 0:
        print(f"{'TIGHT' if t['tight'] else '     '} {t['sym']:6s} {t['arm']} {'L' if t['d']>0 else 'S'} {t['out']:4s} since={P['sinceStart'][i]:3d} nss={g['n_same_sess']} n24={g['n_same24']} n48={g['n_same48']} bs_same={g['bs_same']} bs_opp={g['bs_opp']} nopp_sess={g['n_opp_sess']} nopp24={g['n_opp24']}")
