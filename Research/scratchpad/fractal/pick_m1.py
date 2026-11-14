"""Final pick for strategies 10 (M5) and 11 (M15). Stages 1 + 2, each under the indicator's path rule (PM 0) and always-high-first
candles (PM 2). Filters: every year 2021-2026 positive under both; >= 150 trades in 2021-23 and >= 100 in 2024-26; SL >= 0.15 %;
BE off or >= 0.10 %; right <= RMAX. Rank: PM 2 train (2021-23) R / DD. For the best K (distinct settings) the exact engine adds:
random entries with the same exits (20 seeds), the share of entries within 1 hour of an entry of strategies 1-9, and the test years."""
import sys, os, json, numpy as np, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import ana1, engine as EN
from run9 import T9
from cand import rand_base, B
for _k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + _k] = B[_k]
tf = sys.argv[1]; RMAX = int(sys.argv[2]); K = int(sys.argv[3]) if len(sys.argv) > 3 else 12
rows = []
for stg in (('M1',) if tf == 'M1' else ('1', '2')):
    os.environ['STAGE'] = stg; a = ana1.load(tf)
    os.environ['STAGE'] = stg + 'h'; b = ana1.load(tf)
    p = a['prm']
    ok = ((a['trN'] >= 150) & (a['teN'] >= 100) & (a['yR'] > 0).all(1) & (b['yR'] > 0).all(1) & (p[:, 4] >= 0.15 - 1e-9)
          & ((p[:, 5] == 0) | (p[:, 5] >= 0.10 - 1e-9)) & (p[:, 0] <= RMAX))
    for i in np.flatnonzero(ok):
        rows.append((b['trR'][i] / max(b['trDD'][i], 2.0), tuple(p[i, :7]), a['R'][i], a['dd'][i], b['R'][i], b['dd'][i], a['pf'][i], a['n'][i], a['win'][i]))
print('%s: %d settings pass the filters (right <= %d)' % (tf, len(rows), RMAX))
rows.sort(key=lambda x: -x[0])
t1 = EN.chart(B, 'M1')[0]
ent9 = np.sort(np.concatenate([t1[EN.run(B, 'M1', *q)[:, 0].astype(int)] for q in T9]))
seen = set(); out = []
for obj, prm, R0, dd0, R2, dd2, pf, n, win in rows:
    key = (prm[:6], round(R0, 6))
    if key in seen: continue
    seen.add(key)
    r, l, off, tp, sl, be, sv = prm; r = int(r); l = int(l)
    tr = EN.run(B, 'M1', tf, r, l, off, sl, tp, be, sv); st = EN.stats(tr, sl)
    et = t1[tr[:, 0].astype(int)]
    j = np.searchsorted(ent9, et); near = np.zeros(len(et), bool)
    for d in (-1, 0):
        jj = np.clip(j + d, 0, len(ent9) - 1); near |= np.abs(ent9[jj] - et) <= 3600
    kk = (np.searchsorted(B[tf + '_t'], t1, side='right') - 1).astype(np.int64)
    import fast as FA
    ev = FA.events(B['O'], B['H'], B['L'], B['C'], kk, EN.pivots(B[tf + '_H'], l, r), off)[0]
    mR, mY, _ = rand_base(len(ev), tp, sl, be, sv, 0.23)
    yrs = [EN.stats(tr, sl, t=t1, y0=y, y1=y)['R'] for y in range(2021, 2027)]
    out.append(dict(prm=[tf, r, l, off, sl, tp, be, sv], obj=obj, R=st['R'], dd=st['ddR'], pct=st['pct'], R2=R2, dd2=dd2, pf=st['pf'], n=st['n'], win=st['win'],
                    streak=st['streak'], rand=mR, overlap=float(near.mean()), years=yrs))
    print('R%2d L%3d off %+.2f TP %.2f SL %.2f BE %.2f SV %.2f | %4d trades win %4.1f%% PF %4.2f | %+6.1fR (%+6.1f%%) DD %4.1f | high-first %+6.1fR DD %4.1f | random %+6.1fR | near S1-9 %3.0f%% | years %s' % (
        r, l, off, tp, sl, be, sv, st['n'], st['win'], st['pf'], st['R'], st['pct'], st['ddR'], R2, dd2, mR, 100 * near.mean(), ' '.join('%+.0f' % x for x in yrs)), flush=True)
    if len(out) >= K: break
json.dump(out, open('pick_%s_r%d.json' % (tf, RMAX), 'w'), indent=1, default=float)
