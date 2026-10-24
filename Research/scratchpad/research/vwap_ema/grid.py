"""VWAP vs EMA50/100/200 study: every config at a 1R exit (1:1) and a 2R exit (1:2); all configs start at bar 200 (EMA200 defined)."""
import sys, json, random
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); import lib
M = S + '/research/vwap_ema/score_side.py'
W = dict(warmStart=200)
NV = dict(useVwap=False)
SA = dict(entryMode='market', halfStopOn=False)          # standalone strategies: enter at the signal close, plain 1.8 ATR stop
TR50 = dict(emaPos=(200,), stack=((50, 200),))           # uptrend: close > EMA200 and EMA50 > EMA200
C = [
 ('A', 'VWAP side (the model)', {}),
 ('A', 'No side filter', NV),
 ('A', 'EMA50 side (close vs EMA50 + slope)', dict(NV, emaPos=(50,), emaSlope=(50,))),
 ('A', 'EMA100 side (close vs EMA100 + slope)', dict(NV, emaPos=(100,), emaSlope=(100,))),
 ('A', 'EMA200 side (close vs EMA200 + slope)', dict(NV, emaPos=(200,), emaSlope=(200,))),
 ('A', 'EMA50 side, position only', dict(NV, emaPos=(50,))),
 ('A', 'EMA100 side, position only', dict(NV, emaPos=(100,))),
 ('A', 'EMA200 side, position only', dict(NV, emaPos=(200,))),
 ('B', 'EMA50>EMA100, close>EMA50', dict(NV, stack=((50, 100),), emaPos=(50,))),
 ('B', 'EMA100>EMA200, close>EMA100', dict(NV, stack=((100, 200),), emaPos=(100,))),
 ('B', 'EMA50>EMA200, close>EMA50', dict(NV, stack=((50, 200),), emaPos=(50,))),
 ('B', 'EMA50>100>200, close>EMA50', dict(NV, stack=((50, 100), (100, 200)), emaPos=(50,))),
]
for nm, o in (('close>EMA200', dict(emaPos=(200,))), ('close>EMA100', dict(emaPos=(100,))), ('close>EMA50', dict(emaPos=(50,))),
              ('EMA50>EMA200', dict(stack=((50, 200),))), ('EMA50>EMA100', dict(stack=((50, 100),))), ('EMA100>EMA200', dict(stack=((100, 200),)))):
    C.append(('C', 'VWAP + ' + nm, o))
    C.append(('C', 'VWAP + ' + nm + ' (skipped run invisibly)', dict(o, emaGhost=True)))
for nb, k in ((6, 0.0), (12, 0.0), (6, 0.5), (12, 0.5)):
    pl = dict(TR50, pull=(50, nb, k)); lab = 'pullback to EMA50 (%d bars, %.1f ATR) in EMA200 trend' % (nb, k)
    C.append(('D', lab + ', no VWAP', dict(NV, **pl)))
    C.append(('D', lab + ', + VWAP', dict(pl)))
    C.append(('D', lab + ', + VWAP (skipped run invisibly)', dict(pl, emaGhost=True)))
C += [
 ('E', 'EMA50 bounce in EMA200 trend (standalone)', dict(NV, **SA, sigMode='emaBounce', **TR50)),
 ('E', 'EMA50 bounce in EMA200 trend + VWAP side (standalone)', dict(**SA, sigMode='emaBounce', **TR50)),
 ('E', 'EMA50/EMA200 cross (standalone)', dict(NV, **SA, sigMode='emaCross', crossFast=50, crossSlow=200)),
 ('E', 'EMA50/EMA100 cross (standalone)', dict(NV, **SA, sigMode='emaCross', crossFast=50, crossSlow=100)),
 ('E', 'EMA20/EMA50 cross (standalone)', dict(NV, **SA, sigMode='emaCross', crossFast=20, crossSlow=50)),
 ('E', 'EMA20/EMA50 cross + VWAP side (standalone)', dict(**SA, sigMode='emaCross', crossFast=20, crossSlow=50)),
]
def summary(tr):
    n = len(tr)
    if not n: return dict(n=0)
    w = sum(1 for x in tr if x['res'] > 0)
    return dict(n=n, win=w / n, E=sum(x['res'] for x in tr) / n, tot=sum(x['res'] for x in tr))
out = []
for fam, name, o in C:
    row = dict(fam=fam, name=name, opts={k: v for k, v in o.items()})
    for ex, key in ((2, 'r1'), (4, 'r2')):
        tr = lib.run_all(M, dict(o, exitAt=ex, **W)); tn, te = lib.split(tr)
        bysym = {}
        for s in lib.SYMS:
            ts = [x for x in tr if x['sym'] == s]; bysym[s] = summary(ts)
        row[key] = dict(all=summary(tr), train=summary(tn), test=summary(te), sym=bysym,
                        days={'%s|%s' % (x['sym'], x['t'][:10]): [] for x in tr})
        dd = {}
        for x in tr: dd.setdefault('%s|%s' % (x['sym'], x['t'][:10]), []).append(x['res'])
        row[key]['days'] = dd
    out.append(row)
    a1, a2 = row['r1']['all'], row['r2']['all']
    print('%s %-70s 1:1 n %4d win %4.1f%% E %+.3f | 1:2 n %4d win %4.1f%% E %+.3f tot %+5.0f' % (fam, name[:70], a1['n'], 100 * a1.get('win', 0), a1.get('E', 0), a2['n'], 100 * a2.get('win', 0), a2.get('E', 0), a2.get('tot', 0)), flush=True)
json.dump(out, open(S + '/research/vwap_ema/grid.json', 'w'))
