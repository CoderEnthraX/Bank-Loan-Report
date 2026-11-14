"""M1 candidates ranked by their edge over random entries with the same exits (exact engine, M1): the top N settings by high-first
train R / DD that pass the filters (every year positive under both paths, SL >= 0.15, BE off or >= 0.10, right <= RMAX), each with the
random baseline (20 seeds, per year). Usage: m1_edge.py RMAX N PART NPARTS"""
import sys, os, json, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import ana1, engine as EN, fast as FA
from cand import rand_base, B
for _k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + _k] = B[_k]
RMAX, N, PART, NP = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
os.environ['STAGE'] = 'M1'; a = ana1.load('M1'); os.environ['STAGE'] = 'M1h'; b = ana1.load('M1')
p = a['prm']
ok = ((a['trN'] >= 150) & (a['teN'] >= 100) & (a['yR'] > 0).all(1) & (b['yR'] > 0).all(1) & (p[:, 4] >= 0.15 - 1e-9) & ((p[:, 5] == 0) | (p[:, 5] >= 0.10 - 1e-9)) & (p[:, 0] <= RMAX))
obj = np.where(ok, b['trR'] / np.maximum(b['trDD'], 2.0), -np.inf)
idx = []; seen = set()
for i in np.argsort(-obj):
    if not np.isfinite(obj[i]) or len(idx) >= N: break
    key = (tuple(p[i, :6]), round(a['R'][i], 6))
    if key in seen: continue
    seen.add(key); idx.append(i)
t1 = B['t']; out = []
for q, i in enumerate(idx):
    if q % NP != PART: continue
    r, l, off, tp, sl, be, sv = p[i, :7]; r = int(r); l = int(l)
    tr = EN.run(B, 'M1', 'M1', r, l, off, sl, tp, be, sv); st = EN.stats(tr, sl)
    yrs = [EN.stats(tr, sl, t=t1, y0=y, y1=y)['R'] for y in range(2021, 2027)]
    kk = np.arange(len(t1), dtype=np.int64); ev = FA.events(B['O'], B['H'], B['L'], B['C'], kk, EN.pivots(B['H'], l, r), off)[0]
    mR, mY, _ = rand_base(len(ev), tp, sl, be, sv, 0.23)
    edge = st['R'] - mR; edge_tr = sum(yrs[:3]) - sum(mY[:3])
    out.append(dict(prm=[r, l, float(off), float(tp), float(sl), float(be), float(sv)], R=st['R'], dd=st['ddR'], pf=st['pf'], n=st['n'], win=st['win'], rand=mR, edge=edge, edge_tr=edge_tr,
                    hf=float(b['R'][i]), hfdd=float(b['dd'][i]), years=yrs, ryears=list(mY)))
    print('R%2d L%3d off %+.2f TP %.2f SL %.2f BE %.2f SV %.2f | %4d tr PF %.2f | %+6.1fR DD %4.1f | high-first %+6.1fR | random %+6.1fR | edge %+6.1fR (train %+5.1fR) | edge/DD %.1f' % (
        r, l, off, tp, sl, be, sv, st['n'], st['pf'], st['R'], st['ddR'], b['R'][i], mR, edge, edge_tr, edge / max(st['ddR'], 1)), flush=True)
json.dump(out, open('m1_edge_%d_%d.json' % (RMAX, PART), 'w'), default=float)
