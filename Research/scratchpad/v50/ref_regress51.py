"""v5.1 reference regression: without the per-trade D (element [8] / x['pd']) recovery.py and crooks_tp1.py must equal their v5.0 copies
exactly, in Risk AND Profit mode, every rule (incl. K / L variants), caps, over N wins, ladders, base modes."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as N, recovery_v50 as O, crooks, crooks_tp1 as TN, crooks_tp1_v50 as TO
bad = runs = 0
srcs = [(tf, d) for tf in crooks.TFS for d in crooks.sources(tf) if d['name'] in ('Default settings', 'Shortest losing streak')]
for tf, d in srcs:
    seq = crooks.sequence(d['trades'], d['cfg'])[:1500]; xr = crooks.exit_r(d['cfg'])
    sds = [x[5] for x in sorted(d['trades'], key=lambda x: x[0])]
    trs = [(res, c, parts, None, None, sd * (1.0 + c), 0.6 * sd * (1.0 + c), 2.0 * sd * (1.0 + c)) for (_, res, c, parts), sd in zip(seq, sds)]
    for mode in O.MODES:
        kws = [{}]
        if mode in O.LADFAM: kws += [dict(lad='Max', ladT=500.0)]
        if mode == 'Crooks K': kws += [dict(kMode='usd'), dict(kMode='pct')]
        for kw in kws:
            for sb in ('risk', 'profit'):
                for cn in ((1, 2) if mode in O.CFAM else (1,)):
                    for cap, act in ((0.0, 'clamp'), (500.0, 'reset'), (500.0, 'stop')):
                        for bm in ('usd', 'pct', 'lot'):
                            a, b = [], []
                            ra = O.simulate(trs, mode, cap=cap, capAction=act, exitR=xr, trace=a, cN=cn, baseMode=bm, sizeBy=sb, **kw)
                            rb = N.simulate(trs, mode, cap=cap, capAction=act, exitR=xr, trace=b, cN=cn, baseMode=bm, sizeBy=sb, **kw)
                            runs += 1
                            if a != b or ra != rb: bad += 1; print('DIFF', tf, d['name'], mode, kw, sb, cn, cap, act, bm)
print('recovery.py v5.1 vs v5.0 (no D given): runs %d, differences %d' % (runs, bad))
D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb')); bad2 = runs2 = 0
for (tf, name), d in list(D.items())[:8]:
    tr = [dict(x, m=1.0, rmin=x['R1'] + x['spx'], krisk=2 * (x['R1'] + x['spx'])) for x in d['trades']]
    for mode in ('Crooks C', 'Crooks E', 'Crooks J', 'Crooks K', 'Crooks L'):
        for sb in ('risk', 'profit'):
            for cap, act in ((0.0, 'clamp'), (500.0, 'reset')):
                a, b = [], []
                ra = TO.simulate(tr, mode, cap=cap, capAction=act, cSplit=3, exitR=d['tp1R'], trace=a, sizeBy=sb)
                rb = TN.simulate(tr, mode, cap=cap, capAction=act, cSplit=3, exitR=d['tp1R'], trace=b, sizeBy=sb)
                runs2 += 1
                if [(id(x), r, p, s) for x, r, p, s in a] != [(id(x), r, p, s) for x, r, p, s in b] or ra != rb: bad2 += 1; print('TP1 DIFF', tf, name, mode, sb, cap, act)
print('crooks_tp1.py v5.1 vs v5.0 (no D given): runs %d, differences %d' % (runs2, bad2))
