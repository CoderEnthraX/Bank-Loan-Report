import sys, time
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0,S+'/entry')
import numpy as np, kit, signals, data
t=time.time()
for tf in ('M15','M5'):
    b=data.load(tf); s=signals.raw(tf); print(tf, len(s['i']), 'signals', time.time()-t)
    kit.evaluate(tf, s['i'], s['d'], s['entry'], s['stop_h'], mode=0, window=5, name='baseline limit')
    i=s['i']; d=s['d']; A=b['atr'][i]
    kit.evaluate(tf, i, d, b['C'][i], b['C'][i]-d*1.8*A, mode=1, name='market all')
    print(time.time()-t)
