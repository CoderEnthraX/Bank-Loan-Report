import sys, pickle
rows = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/feat.pkl', 'rb'))
keys = sorted({k for _, f in rows for k in f})
NT = sum(t['tight'] for t, _ in rows)
res = []
def pairval(k):
    a = b = None
    for t, f in rows:
        if t['sym'] == 'NIFTY' and t['fill'] == '2026-10-09 10:10': a = f.get(k)
        if t['sym'] == 'SENSEX' and t['fill'] == '2026-10-09 10:10': b = f.get(k)
    return a, b
for k in keys:
    v = [(f[k], t['tight']) for t, f in rows if k in f]
    if len(v) < len(rows) - 15: continue
    xs = sorted(set(x for x, _ in v))
    best = None
    # one-sided
    for th in xs:
        for side in ('>=', '<='):
            tp = sum(1 for x, tg in v if tg and (x >= th if side == '>=' else x <= th))
            fp = sum(1 for x, tg in v if not tg and (x >= th if side == '>=' else x <= th))
            err = (NT - tp) + fp
            if best is None or err < best[0]: best = (err, tp, fp, side, th)
    # interval
    tv = sorted(x for x, tg in v if tg)
    lo, hi = tv[0], tv[-1]
    fp_all = sum(1 for x, tg in v if not tg and lo <= x <= hi)
    besti = None
    for a in xs:
        for b in xs:
            if b < a: continue
            tp = sum(1 for x, tg in v if tg and a <= x <= b); fp = sum(1 for x, tg in v if not tg and a <= x <= b)
            err = (NT - tp) + fp
            if besti is None or err < besti[0]: besti = (err, tp, fp, a, b)
    res.append((best[0], k, best, fp_all, besti, pairval(k)))
res.sort(key=lambda r: (r[0], r[4][0]))
for r in res[:int(sys.argv[2]) if len(sys.argv) > 2 else 40]:
    e, k, b, fa, bi, pv = r
    print(f"{k:28s} err {e:2d} (tp {b[1]} fp {b[2]} {b[3]} {b[4]:.4g}) | 8-cover fp {fa:2d} | interval err {bi[0]} tp {bi[1]} fp {bi[2]} [{bi[3]:.4g},{bi[4]:.4g}] | NIFTY {pv[0] if pv[0] is None else round(pv[0],3)} SENSEX {pv[1] if pv[1] is None else round(pv[1],3)}")
