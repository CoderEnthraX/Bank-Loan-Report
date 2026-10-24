import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/extras')
from lib import *
from tightdata import TRADES
n = {'mid':0,'wick':0,'both':0,'none':0}
for t in TRADES:
    P = prepare(t['sym']); O,H,L,C = P['O'],P['H'],P['L'],P['C']; i = t['arm_i']; d = t['d']; A = P[('atr',14)][i]
    mid = (O[i]+C[i])/2
    wk = max(H[i-6:i]) if d>0 else min(L[i-6:i])
    cl = max(C[i-6:i]) if d>0 else min(C[i-6:i])
    bd = max(max(O[j],C[j]) for j in range(i-6,i)) if d>0 else min(min(O[j],C[j]) for j in range(i-6,i))
    e = t['entry']
    tag = []
    for nm, v in (('mid',mid),('wick',wk),('close',cl),('body',bd)):
        if abs(v-e) <= 0.02*A: tag.append(nm)
    used = 'mid' if d*(mid-wk) >= 0 else 'wick'
    br10w = d*(C[i] - (max(H[i-10:i]) if d>0 else min(L[i-10:i])))/A
    br10c = d*(C[i] - (max(C[i-10:i]) if d>0 else min(C[i-10:i])))/A
    print(t['sym'], t['arm'], d, 'model:', used, 'matches:', tag, 'brk10wick %.2f brk10close %.2f' % (br10w, br10c))
