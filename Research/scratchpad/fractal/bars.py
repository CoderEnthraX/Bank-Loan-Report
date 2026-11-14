"""Fractal grid research: TradingView-aligned bars from the FxPro gold M1 export (gold/data/M1.pkl).
Clock: New York time + 7 h (= FxPro server time outside the US / EU summer-time gap weeks). On TradingView gold (session 17:00 New York)
the daily bar starts at 17:00 NY and the 4 h bars at 17:00 / 21:00 / 01:00 / 05:00 / 09:00 / 13:00 NY, i.e. 00:00 / 04:00 ... on this clock.
M5 / M15 / H1 buckets are the same on any whole-hour clock.
Output bars.npz: M1 arrays (t = clock seconds, ut = UTC seconds, O H L C, SP spread points) and per timeframe TF in M5 M15 H1 H4 D1:
  TF_t (bucket start, clock seconds), TF_O/H/L/C, TF_i0 (first M1 index of the bucket), and M1 -> TF index (TF_k)."""
import pickle, numpy as np, datetime as dt
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
d = pickle.load(open(S + '/gold/data/M1.pkl', 'rb'))
NY = ZoneInfo('America/New_York'); UTC = dt.timezone.utc
ut = np.array([int(x.replace(tzinfo=UTC).timestamp()) for x in d['utc']], dtype=np.int64)
# NY offset changes only at the US switch dates: compute per distinct UTC hour
hrs = np.unique(ut // 3600)
off = {h: int(dt.datetime.fromtimestamp(int(h) * 3600, UTC).astimezone(NY).utcoffset().total_seconds()) for h in hrs}
t = ut + np.array([off[h] for h in ut // 3600], dtype=np.int64) + 7 * 3600
srv = np.array([int(x.replace(tzinfo=UTC).timestamp()) for x in d['srv']], dtype=np.int64)
print('M1 bars', len(t), '| clock - server hours:', sorted(set(((t - srv) // 3600).tolist())))
assert np.all(np.diff(t) > 0), 'clock not increasing'
O, H, L, C = (np.asarray(d[k], dtype=np.float64) for k in 'OHLC')
out = dict(t=t, ut=ut, O=O, H=H, L=L, C=C, SP=np.asarray(d['SP'], dtype=np.int64))
for tf, sec in (('M5', 300), ('M15', 900), ('H1', 3600), ('H4', 14400), ('D1', 86400)):
    b = t // sec
    i0 = np.flatnonzero(np.r_[True, b[1:] != b[:-1]])
    i1 = np.r_[i0[1:], len(t)]
    k = np.repeat(np.arange(len(i0)), i1 - i0)
    out[tf + '_t'] = b[i0] * sec; out[tf + '_i0'] = i0; out[tf + '_k'] = k.astype(np.int32)
    out[tf + '_O'] = O[i0]; out[tf + '_C'] = C[i1 - 1]
    out[tf + '_H'] = np.maximum.reduceat(H, i0); out[tf + '_L'] = np.minimum.reduceat(L, i0)
    print(tf, 'bars', len(i0))
np.savez(S + '/fractal/bars.npz', **out)
# cross-check against the existing server-clock M5 / H1 pickles (same buckets except the summer-time gap weeks)
for tf in ('M5', 'H1'):
    e = pickle.load(open(S + '/gold/data/%s.pkl' % tf, 'rb'))
    print(tf, 'existing', len(e['O']), 'new', len(out[tf + '_O']), '| H equal on common prefix:', np.allclose(np.asarray(e['H'][:1000]), out[tf + '_H'][:1000]))
dd = out['D1_t']
print('first D1', dt.datetime.utcfromtimestamp(int(dd[0])), 'last D1', dt.datetime.utcfromtimestamp(int(dd[-1])), '| weekdays', sorted(set(dt.datetime.utcfromtimestamp(int(x)).weekday() for x in dd)))
