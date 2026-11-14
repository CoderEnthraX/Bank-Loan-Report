"""Stage 2 with practical limits: BE trigger off or >= a floor, SL >= a floor; every year positive; objective train R / DD."""
import numpy as np, sys, os
os.environ['STAGE'] = '2'
from ana1 import load, show
tf = sys.argv[1]; bef = float(sys.argv[2]); slf = float(sys.argv[3]); k = int(sys.argv[4]) if len(sys.argv) > 4 else 12
d = load(tf); p = d['prm']
ok = (d['trN'] >= 150) & (d['teN'] >= 100) & (d['yR'] > 0).all(1) & ((p[:, 5] == 0) | (p[:, 5] >= bef - 1e-9)) & (p[:, 4] >= slf - 1e-9)
obj = np.where(ok, d['trR'] / np.maximum(d['trDD'], 2.0), -np.inf)
# one row per (R, L, off, TP, SL, BE): salvage variants that give the same result are folded
idx = []; seen = set()
for i in np.argsort(-obj):
    if not np.isfinite(obj[i]) or len(idx) >= k: break
    key = (tuple(p[i, :6]), round(d['R'][i], 6))
    if key in seen: continue
    seen.add(key); idx.append(i)
show(d, idx, '-- %s, BE off or >= %.2f, SL >= %.2f, every year positive: top %d by train R / DD (%d qualify)' % (tf, bef, slf, k, ok.sum()))
