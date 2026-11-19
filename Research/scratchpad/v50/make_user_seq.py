"""v5.0 parity sources from the user's M5 settings (Tue-Thu, 06-23 IST, kill zones Asia / London / NY) with the final exit at TP1 = 0.1R and
0.3R: the engine's trades as (time, R, cost in R, parts=None) + the stop distance, like crooks.sequence (cost 0.23 per oz / stop distance)."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/conf')
import confirm as Q
out = {}
for tp in (0.1, 0.3):
    cfg = dict(Q.USER_ENG, exitAt=1, tp1R=tp, **Q.USER_ON)
    P, p, tr = Q.engine(dict(key='user', tf='M5', cfg=cfg)); T = P['T']
    seq = []; sds = []
    for x in tr:
        d = x['dir'] * (x['entry'] - x['stop'])
        seq.append((T[x['fill']], x['res'], 0.23 / d, None)); sds.append(d)
    out[tp] = dict(seq=seq, sds=sds, xr=tp)
    print(tp, len(seq), 'trades, wins', sum(1 for s in seq if s[1] > 0))
pickle.dump(out, open(S + '/v50/user_seq.pkl', 'wb'))
