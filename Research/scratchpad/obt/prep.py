"""M5 volumes (sum of the M1 tick volumes per 5-minute server-time bucket) for the simulator test, and the Python stream's signals on the same bars."""
import sys, numpy as np, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/ob')
d = dict(np.load(S + '/entry/cache_M1.npz'))
a, b = 1780275600, 1790985600
m = (d['srv'] >= a) & (d['srv'] < b)
srv, O, H, L, C, V = d['srv'][m], d['O'][m], d['H'][m], d['L'][m], d['C'][m], d['TV'][m]
bars = []
for s, o, h, l, c, v in zip(srv, O, H, L, C, V):
    k = int(s) // 300 * 300
    if bars and bars[-1][0] == k:
        x = bars[-1]; x[2] = max(x[2], h); x[3] = min(x[3], l); x[4] = c; x[5] += v
    else: bars.append([k, o, h, l, c, float(v)])
with open(S + '/obt/vol_m5.txt', 'w') as f:
    for x in bars: f.write('%d %.1f\n' % (x[0], x[5]))
import importlib.util
sp = importlib.util.spec_from_file_location('obs', S + '/ob/ob_stream.py')
# ob_stream imports ob_test (loads data); only the OB class is needed
src = open(S + '/ob/ob_stream.py').read().replace('import ob_test as T', 'T = None')
ns = {'__file__': S + '/ob/ob_stream.py', '__name__': 'obs'}; exec(compile(src, 'ob_stream', 'exec'), ns)
for stop in ('candle',):
    eng = ns['OB'](5, [15, 30, 60])
    out = open(S + '/obt/py_sig.txt', 'w')
    for x in bars:
        t = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=x[0])
        r = eng.bar(t, x[1], x[2], x[3], x[4], x[5])
        if r: out.write('%d %d %.2f %.2f %s\n' % (x[0], r[0], r[1], r[2], '%.2f' % r[3] if r[3] is not None else '0'))
print(len(bars), 'M5 bars')
