import sys, math, pickle, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/gold')
import engine as EN, pine_twin2 as TW, recovery as RC
from final11 import ALL
d = pickle.load(open('dbg_case.pkl', 'rb')); kw = d['kw']; k = d['k']; m = d['m']
B = EN.load(); p = TW.P(**kw); prm = ALL[k]; tr = EN.run(B, 'M1', *prm); sl, tp = prm[4], prm[5]
s = TW.Strat(p, 0, prm[3], sl, tp, prm[6], prm[7]); oscP = 0.0; oscU = 1; base = p.baseR; xr = tp / sl
for j, x in enumerate(tr[:412]):
    F, X = x[1], x[3]; sd = F * sl / 100.0; c = p.costIn / sd; res = (X - F) / sd
    s.mmOpen(F); r_tw = s.risk
    need_r = (base - oscP) / (base * xr); r_ref = base * min(oscU, int(max(1, math.ceil(need_r))))
    if j >= 406:
        print(j, 'twin oscP %.17g oscU %d need %.17g r %.4f || ref oscP %.17g oscU %d need %.17g r %.4f' % (s.oscP, s.oscU, (base - s.oscP) / (base * xr), r_tw, oscP, oscU, need_r, r_ref))
    s.mmBook(s.units * (X - F - p.costIn))
    pnl = r_ref * (res - c) / (1.0 + c); oscP += pnl
    if oscP >= base: oscU = 1; oscP = 0.0
    elif pnl > 0: oscU += 1
