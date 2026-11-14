"""Settings that hold under the indicator's path rule (PM 0) AND always-high-first candles (PM 2): rows of search<stg>_<TF> and
search<stg>h_<TF> are the same settings. Filters: PM 0 every year positive, >= 150 / 100 train / test trades; PM 2 every year positive.
Objective: PM 2 train R / DD (the worst case), ties by PM 0."""
import numpy as np, sys, os
import ana1
tf = sys.argv[1]; stg = sys.argv[2]; k = int(sys.argv[3]) if len(sys.argv) > 3 else 15
rmax = int(sys.argv[4]) if len(sys.argv) > 4 else 999; lmax = int(sys.argv[5]) if len(sys.argv) > 5 else 999
os.environ['STAGE'] = stg; a = ana1.load(tf)
os.environ['STAGE'] = stg + 'h'; b = ana1.load(tf)
assert np.array_equal(a['prm'][:, :7], b['prm'][:, :7])
p = a['prm']
ok = ((a['trN'] >= 150) & (a['teN'] >= 100) & (a['yR'] > 0).all(1) & (b['yR'] > 0).all(1) & (p[:, 0] <= rmax) & (p[:, 1] <= lmax))
print('%s stage %s: %d settings, %d pass (PM 0 and PM 2 every year positive, right <= %d, left <= %d)' % (tf, stg, len(p), ok.sum(), rmax, lmax))
obj = np.where(ok, b['trR'] / np.maximum(b['trDD'], 2.0), -np.inf)
print('   R   L   off    TP    SL    BE    SV | trades win%   PF | PM0: train R  DD | test R  DD | all R  DD || PM2: trades  PF | train R  DD | test R  DD | all R  DD | PM2 years')
idx = []; seen = set()
for i in np.argsort(-obj):
    if not np.isfinite(obj[i]) or len(idx) >= k: break
    key = (tuple(p[i, :6]), round(a['R'][i], 6), round(b['R'][i], 6))
    if key in seen: continue
    seen.add(key); idx.append(i)
    print('%4d %3d %5.2f %5.2f %5.2f %5.2f %5.2f | %5d %4.1f %4.2f | %7.1f %4.1f | %6.1f %4.1f | %6.1f %4.1f || %5d %4.2f | %7.1f %4.1f | %6.1f %4.1f | %6.1f %4.1f | %s' % (
        p[i, 0], p[i, 1], p[i, 2], p[i, 3], p[i, 4], p[i, 5], p[i, 6], a['n'][i], 100 * a['win'][i], a['pf'][i], a['trR'][i], a['trDD'][i], a['teR'][i], a['teDD'][i], a['R'][i], a['dd'][i],
        b['n'][i], b['pf'][i], b['trR'][i], b['trDD'][i], b['teR'][i], b['teDD'][i], b['R'][i], b['dd'][i], ' '.join('%+.0f' % x for x in b['yR'][i])))
