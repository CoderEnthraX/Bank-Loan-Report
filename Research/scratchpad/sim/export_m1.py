"""Exports FxPro gold M1 bars (server time, UTC offset, OHLC, spread) for the broker simulator: export_m1.py FROM TO OUT.csv (dates YYYY-MM-DD, server time)."""
import sys, datetime
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
d = dict(np.load(S + '/entry/cache_M1.npz'))
ep = datetime.datetime(1970, 1, 1)
a = int((datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d') - ep).total_seconds())
b = int((datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d') - ep).total_seconds())
m = (d['srv'] >= a) & (d['srv'] < b)
with open(sys.argv[3], 'w') as f:
    for s, u, o, h, l, c, sp in zip(d['srv'][m], d['utc'][m], d['O'][m], d['H'][m], d['L'][m], d['C'][m], d['SP'][m]):
        f.write('%d,%d,%.2f,%.2f,%.2f,%.2f,%.3f\n' % (s, s - u, o, h, l, c, sp))
print(m.sum(), 'M1 bars', sys.argv[1], '->', sys.argv[2])
