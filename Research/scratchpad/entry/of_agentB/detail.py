import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, cand, kit
out = {}
def detail(tf, x, i, d, kind, stop, name):
    e, st, mode = L.orders(x, i, d, kind, stop, struct=np.where(d == 1, x['L'][i], x['H'][i]))
    good = (x['split'][i] != 'test'); i, d, e, st = i[good], d[good], e[good], st[good]
    print('==', name, tf)
    r = kit.evaluate(tf, i, d, e, st, mode=mode, window=3, name=name)
    pl = L.A.placebo(tf, i, d, e, st, mode, 3, K=5, seed=1)
    py = L.A.per_year(tf, i, d, e, st, mode, 3)
    rec = dict(tf=tf)
    for s in ('train', 'valid'):
        for lab in ('long', 'short'):
            q = r[(s, lab)]
            rec['%s_%s' % (s, lab)] = dict(n=q['n'], pm=round(q['per_month'], 1), hit=list(np.round(q['hit'], 1)), ex=list(np.round(q['excess'], 1)),
                                         avgex=round(q['avg_excess'], 2), plex=list(np.round(q['hit'] - pl[(s, lab)], 1)),
                                         avgpl=round(float(np.mean(q['hit'] - pl[(s, lab)])), 2), E=list(np.round(q['E'], 3)), fill=round(q['fill_rate'], 2))
            print('  %s %s placebo-adj %s' % (s, lab, ' '.join('%+5.1f' % v for v in q['hit'] - pl[(s, lab)])), ' E per TP', np.round(q['E'], 3))
    rec['per_year'] = {'%d_%s' % (y, 'L' if dd == 1 else 'S'): v for (y, dd), v in py.items()}
    print('  per year', {k: (v[0], round(v[1], 1)) for k, v in rec['per_year'].items()})
    out[name] = rec

tf = 'M5'
x, i, d, k = cand.c1_sig(tf, 90); detail(tf, x, i, d, 'mkt', 'atr', 'C1 dPOC fade p90 M5 mkt 1.8ATR (k=%.1f)' % k)
x, i, d, k = cand.c1_sig('M15', 90); detail('M15', x, i, d, 'mkt', 'atr', 'C1 dPOC fade p90 M15 mkt 1.8ATR (k=%.1f)' % k)
x, i, d = cand.c2_sig(tf, 'cvd_cl', 6); detail(tf, x, i, d, 'stp', 'struct', 'C2 CVD-CLV div m6 M5 stop-entry struct')
json.dump(out, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB/detail.json', 'w'), indent=1, default=float)
