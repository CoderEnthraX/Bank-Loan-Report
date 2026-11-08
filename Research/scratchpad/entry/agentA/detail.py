"""finalist details: per-TP hit / excess (train, valid, long / short), per-year excess, E after spread, OCO (one trade per day) variant"""
import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, kit, numpy as np, candA, candB
from fam_sweep import prev_day_hl
OUT = {}
def report(tag, tf, i, d, e, st, mode, win):
    r = kit.evaluate(tf, i, d, e, st, mode=mode, window=win, name=tag[:30])
    py = lib.per_year(tf, i, d, e, st, mode, win)
    print('  per-year avg excess (n):', ' '.join('%d%s %+.1f(%d)' % (y, 'L' if dd == 1 else 'S', v[1], v[0]) for (y, dd), v in sorted(py.items())))
    o = kit.outcomes_of(tf, i, d, e, st, mode, win); f = o['fill_m1'] >= 0; b = lib.ctx(tf)
    sp = b['split'][i]
    for s_ in ('train', 'valid'):
        m = f & (sp == s_)
        dd = (o['fill_m1'][m] - 0)  # fill minute index
        print('  %s fill delay (bars) median %.1f' % (s_, np.median(o['fill_bar'][m] - i[m])))
    OUT[tag] = dict(tf=tf, res={'%s_%s' % k: {kk: (vv.tolist() if hasattr(vv, 'tolist') else vv) for kk, vv in v.items()} for k, v in r.items()},
                    per_year={'%d_%d' % k: v for k, v in py.items()})
    return o

def oco(tf, i, d, e, st, mode, win):
    """keep, per signal bar, only the first-filled of the two orders (cancel the other)"""
    o = kit.outcomes_of(tf, i, d, e, st, mode, win); f = o['fill_m1'] >= 0
    key = np.where(f, o['fill_m1'], 10**12); keep = np.zeros(len(i), bool)
    order = np.lexsort((key, i)); seen = set()
    for k in order:
        if i[k] in seen or not f[k]: continue
        seen.add(i[k]); keep[k] = True
    return keep

for tf in ('M15', 'M5'):
    b, i, d, e, a, win, H, Lo = candA.sigs(tf)
    st = e - d * 1.8 * a
    print('== A NY open-range (09:30-10:00) stop entries, 1.8 ATR,', tf)
    report('A_%s' % tf, tf, i, d, e, st, 2, win)
    k = oco(tf, i, d, e, st, 2, win)
    print('== A OCO (first fill only)', tf); report('A_OCO_%s' % tf, tf, i[k], d[k], e[k], st[k], 2, win)
for tf in ('M15', 'M5', 'H1'):
    b, i, d = candB.sigs(tf); H, L, C, A = b['H'], b['L'], b['C'], b['atr']; a = A[i]
    ext = np.where(d == 1, L[i], H[i]); e = np.where(d == 1, H[i] + 0.05 * a, L[i] - 0.05 * a)
    st = np.where(d == 1, np.minimum(ext - 0.1 * a, e - 0.5 * a), np.maximum(ext + 0.1 * a, e + 0.5 * a))
    print('== B PDH/PDL sweep + confirmation stop entry,', tf, ' median risk ATR %.2f' % np.median(d * (e - st) / a))
    report('B_%s' % tf, tf, i, d, e, st, 2, 3)
json.dump(OUT, open(lib.A + '/detail.json', 'w'), default=float)
