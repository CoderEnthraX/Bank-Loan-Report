"""v5.0 reference regression: with sizeBy='risk' and the v4.9 rules, gold/recovery.py and gold/crooks_tp1.py must equal their v4.9 copies
exactly (every trade's $ risk and every result field), on the parity sequences (every rule, caps, splits, over N wins, ladder levels,
base modes usd / pct / lot)."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as N, recovery_v49 as O, crooks, crooks_tp1 as TN, crooks_tp1_v49 as TO
bad = runs = 0
srcs = [(tf, d) for tf in crooks.TFS for d in crooks.sources(tf) if d['name'] in ('Default settings', 'Most profit', 'Shortest losing streak')]
for tf, d in srcs:
    seq = crooks.sequence(d['trades'], d['cfg'])[:3000]; xr = crooks.exit_r(d['cfg'])
    sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]
    trs = [(res, c, parts, None, None, sd * (1.0 + c), 0.6 * sd * (1.0 + c)) for (_, res, c, parts), sd in zip(seq, sds)]
    for mode in O.MODES:
        kws = [{}]
        if mode in O.LADFAM: kws += [dict(lad=lv, ladT=T) for lv in O.LADDER for T in (500.0, 1000.0)]
        for kw in kws:
            for cn in ((1, 2, 3) if mode in O.CFAM else (1,)):
                for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                    for bm in ('usd', 'pct', 'lot'):
                        a, b = [], []
                        ra = O.simulate(trs, mode, cap=cap, capAction=act, exitR=xr, trace=a, cN=cn, baseMode=bm, **kw)
                        rb = N.simulate(trs, mode, cap=cap, capAction=act, exitR=xr, trace=b, cN=cn, baseMode=bm, **kw)
                        runs += 1
                        if a != b or ra != rb: bad += 1; print('DIFF', tf, d['name'], mode, kw, cn, cap, act, bm)
print('recovery.py: runs %d, differences %d' % (runs, bad))
D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb')); bad2 = runs2 = 0
for (tf, name), d in D.items():
    tr = [dict(x, m=1.0, rmin=x['R1'] + x['spx']) for x in d['trades']]
    for mode in ('Off', 'Crooks A', 'Crooks B', 'Crooks C', 'Crooks D', 'Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J'):
        for lad in ((None, 'Medium', 'Max') if mode in O.LADFAM else (None,)):
            for cap, act in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                for cn in ((1, 2) if mode in TO.CFAM else (1,)):
                    a, b = [], []
                    ra = TO.simulate(tr, mode, cap=cap, capAction=act, cSplit=3, exitR=d['tp1R'], trace=a, cN=cn, lad=lad)
                    rb = TN.simulate(tr, mode, cap=cap, capAction=act, cSplit=3, exitR=d['tp1R'], trace=b, cN=cn, lad=lad)
                    runs2 += 1
                    if [(id(x), r, p, s) for x, r, p, s in a] != [(id(x), r, p, s) for x, r, p, s in b] or ra != rb: bad2 += 1; print('TP1 DIFF', tf, name, mode, lad, cap, act, cn)
print('crooks_tp1.py: runs %d, differences %d' % (runs2, bad2))
