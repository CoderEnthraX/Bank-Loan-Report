"""Gold intraday seasonality, drift-neutral: per year, D(hour) - mean D of that year (D = (long edge - short edge) / 2, avg pts over
TP1-TP4, market entries at every bar, stop 1.8 ATR). Hours in New York local time (DST aware). Years 2021-2024 + 2025H1 (no test data)."""
import sys, pickle, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import ev, data
def edge(m):
    return np.mean([(np.mean(m >= r - 1e-9) - b) * 100 for r, b in zip(ev.TPR, ev.BASE)]) if len(m) else np.nan
NY = ZoneInfo('America/New_York')
def ny_hour(utc):
    s = pd.to_datetime(utc, unit='s', utc=True).tz_convert(NY)
    return s.hour.to_numpy(), s.minute.to_numpy()
tf = sys.argv[1] if len(sys.argv) > 1 else 'M15'
f = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb')); b = data.load(tf)
f = f[f.split != 'test'].copy()
f['nyh'], _ = ny_hour(b['utc'][f.i.to_numpy()])
f['yr'] = np.where(f.year == 2025, '25H1', f.year.astype(str))
yrs = ['2021', '2022', '2023', '2024', '25H1']
print('%s: D(NY hour) minus the year mean, avg pts over TP1-TP4 (+ = longs better than shorts at that hour)' % tf)
print('NYh  ' + ' '.join('%6s' % y for y in yrs) + '   all   n/yr')
tab = {}
for y in yrs:
    g = f[f.yr == y]; base = (edge(g.mfeL.values) - edge(g.mfeS.values)) / 2
    for h in range(24):
        m = g[g.nyh == h]
        tab[(y, h)] = ((edge(m.mfeL.values) - edge(m.mfeS.values)) / 2 - base, len(m))
for h in range(24):
    vals = [tab[(y, h)][0] for y in yrs]
    pos = sum(v > 0 for v in vals if not np.isnan(v))
    print('%02d   ' % h + ' '.join('%+6.1f' % v for v in vals) + '  %+5.1f  %5d  %d/5 positive' % (np.nanmean(vals), np.mean([tab[(y, h)][1] for y in yrs]), pos))
