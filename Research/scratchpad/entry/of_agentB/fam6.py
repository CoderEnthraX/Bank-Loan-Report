"""F6: the indicator's raw signals filtered by order-flow conditions (agree / disagree), and the opposite trade on disagreement."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, signals
TFS = sys.argv[1:] or ['M15', 'M5']
def orders3(tf, x, i, d, ent, stp, name):
    L.run(tf, i, d, ent, stp, mode=0, window=5, name=name + ' lim own', family='F6 combo')
    for k in ('mkt', 'stp'):
        e, st, mode = L.orders(x, i, d, k, 'atr')
        L.run(tf, i, d, e, st, mode=mode, window=3, name=name + ' %s atr' % k, family='F6 combo')
for tf in TFS:
    x = L.ctx(tf); a = x['atr']; C = x['C']
    s = signals.raw(tf); i = s['i'].astype(np.int64); d = s['d'].astype(np.int64)
    keep = L.base_ok(x, 0)[i] & ~s['both'] & ~np.isnan(x['dvah'][i]) & ~np.isnan(x['pvah'][i])
    i, d, ent, stp = i[keep], d[keep], s['entry'][keep], s['stop_h'][keep]
    print(tf, 'signals', len(i))
    orders3(tf, x, i, d, ent, stp, 'F6 sig ALL')
    _, mn, mx, mean = L.comp_rvp(tf, i, C[i], C[i] + d * 2.0 * a[i])
    conds = {
        'bar delta agrees': x['dtk'][i] * d > 0,
        'sess CVD agrees': x['cvd_tk'][i] * d > 0,
        'close beyond devVA': np.where(d == 1, C[i] > x['dvah'][i], C[i] < x['dval'][i]),
        'devPOC ahead': d * (x['dpoc'][i] - C[i]) > 0,
        'LVN path ahead': mean < 0.5,
        'beyond priorVA': np.where(d == 1, C[i] > x['pvah'][i], C[i] < x['pval'][i]),
    }
    for lab, m in conds.items():
        print('  %s: %.0f%% of signals' % (lab, 100 * m.mean()))
        orders3(tf, x, i[m], d[m], ent[m], stp[m], 'F6 sig +%s' % lab)
        orders3(tf, x, i[~m], d[~m], ent[~m], stp[~m], 'F6 sig NOT %s' % lab)
        e, st, mode = L.orders(x, i[~m], -d[~m], 'mkt', 'atr')
        L.run(tf, i[~m], -d[~m], e, st, mode=1, name='F6 OPP sig NOT %s mkt' % lab, family='F6 combo')
