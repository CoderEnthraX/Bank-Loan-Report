"""Like ana3 with a cap on right / left (time scale) and both stages pooled."""
import numpy as np, sys, os
import ana1
tf = sys.argv[1]; bef = float(sys.argv[2]); slf = float(sys.argv[3]); rmax = int(sys.argv[4]); lmax = int(sys.argv[5]); k = int(sys.argv[6])
best = []
for stg in ('1', '2'):
    os.environ['STAGE'] = stg
    d = ana1.load(tf); p = d['prm']
    ok = ((d['trN'] >= 150) & (d['teN'] >= 100) & (d['yR'] > 0).all(1) & ((p[:, 5] == 0) | (p[:, 5] >= bef - 1e-9)) & (p[:, 4] >= slf - 1e-9)
          & (p[:, 0] <= rmax) & (p[:, 1] <= lmax))
    obj = np.where(ok, d['trR'] / np.maximum(d['trDD'], 2.0), -np.inf)
    print('stage %s: %d qualify' % (stg, ok.sum()))
    idx = []; seen = set()
    for i in np.argsort(-obj):
        if not np.isfinite(obj[i]) or len(idx) >= k: break
        key = (tuple(p[i, :6]), round(d['R'][i], 6))
        if key in seen: continue
        seen.add(key); idx.append(i)
    ana1.show(d, idx, '-- stage %s %s: right <= %d, left <= %d, BE off or >= %.2f, SL >= %.2f, every year positive' % (stg, tf, rmax, lmax, bef, slf))
