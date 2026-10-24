"""stop = clamp(dist to level + buf, 0.9, 1.8) for every level feature (level on stop side), match |pred-actual|<0.12 over 80"""
import sys, pickle; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels/feat2.pkl','rb'))
import vp; from lv import prepare
from malv import mafeat
for t, x in rows:
    P = prepare(t['sym']); A = P[('atr',14)][t['arm_i']]
    x.update(vp.vpfeat(P, t['arm_i'], t['d'], t['entry'], A)); x.update(mafeat(P, t['arm_i'], t['d'], t['entry'], A))
skip = ('since','srange','adr','datr','rv','vshare','vwapjump','n_','bs_','rngA','bodyA','bodyP','brkA','momA','ent_mid')
keys = sorted({k for _, x in rows for k in x if not k.startswith(skip)})
res = []
for k in keys:
    for buf in (0.0, 0.05, 0.1, 0.2, 0.3):
        for mode in ('stopside', 'abs'):
            ok = 0; tok = 0
            for t, x in rows:
                v = x.get(k)
                if v is None: pr = 1.8
                elif mode == 'stopside': pr = min(max(-v + buf, 0.9), 1.8) if v < 0 else 1.8
                else: pr = min(max(abs(v) + buf, 0.9), 1.8)
                m = abs(pr - t['stopR']) < 0.12; ok += m; tok += m and t['tight']
            res.append((ok, tok, k, buf, mode))
res.sort(reverse=True)
for r in res[:12]: print(r)
print('max tight matched by any clamp rule with >=72 total:', max([r[1] for r in res if r[0] >= 72] or [0]))
