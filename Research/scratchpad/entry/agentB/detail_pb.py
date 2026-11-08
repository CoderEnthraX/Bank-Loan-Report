"""detail of the best continuation-type entry (C3): pb (1st counter bar within 5 bars closes beyond the retest lvl) + with 5-day trend"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, lib, data, signals
from pb import pb_bars
from detail import show
for tf in sys.argv[1:]:
    b = data.load(tf); c = lib.ctx(tf); C, A = b['C'], b['atr']; s = signals.raw(tf)
    J = pb_bars(b, s, 5, 'lvl'); m = J >= 0; j = J[m]; d = s['d'][m].astype(np.int64); k = d * c['trend_d5'][j] > 0
    show(tf, j[k], d[k], C[j[k]], C[j[k]] - d[k] * 1.8 * A[j[k]], 1, 'C3 pb + 5d trend')
