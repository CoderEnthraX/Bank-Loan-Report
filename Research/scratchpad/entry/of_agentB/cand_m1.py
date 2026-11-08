import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, cand
tf = 'M1'
for m in (15, 30, 60):
    x, i, d = cand.c2_sig(tf, 'cvd_cl', m, gap=60)
    for st in ('struct', 'atr'): cand.go(tf, x, i, d, 'C2 div cl m%d stp %s' % (m, st), 'stp', st)
for pct in (90, 95):
    x, i, d, k = cand.c1_sig(tf, pct, gap=60)
    cand.go(tf, x, i, d, 'C1 dPOC p%d(k%.1f) mkt atr' % (pct, k), 'mkt', 'atr')
