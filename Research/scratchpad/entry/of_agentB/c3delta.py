import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, c3
tf = 'M5'
x, i, d, k = c3.c3_sig(tf, 80, gap=12)        # d = trade direction (opposite of the signal)
eff = -d * x['dcl'][i] / np.maximum(x['vol'][i], 1)   # delta efficiency of the signal bar in the signal's direction
cv = -d * x['cvd_cl'][i]                               # session CVD in the signal's direction
med = np.median(eff[x['split'][i] == 'train'])
for lab, m in (('C3 x strong bar delta', eff >= med), ('C3 x weak bar delta', eff < med),
               ('C3 x CVD with move', cv > 0), ('C3 x CVD against move (diverg)', cv <= 0)):
    print(lab, m.sum()); c3.go(tf, x, i[m], d[m], lab)
