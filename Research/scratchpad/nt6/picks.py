"""Picks per timeframe from res_TF.pkl: best by score (all years) and best picked on 2021-2023 only (its 2024-2026 shown as the honest test);
re-run their trades; money rules on each (whole period from $1,000; every year fresh; every month fresh). -> picks.pkl"""
import sys, os, pickle, collections
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(HERE)
sys.path.insert(0, S + '/nt5'); sys.path.insert(0, S + '/gold'); sys.path.insert(0, HERE)
import recovery as RC
TFS = [t for t in os.environ.get('TFS', 'M1 M5 M15 H1 H4 D1').split() if os.path.exists(HERE + '/res_%s.pkl' % t)]
MINTR = {'M1': 200, 'M5': 150, 'M15': 100, 'H1': 60, 'H4': 30, 'D1': 20}
RULES = [('Fixed $20', 'Off', 'risk', {}), ('% of equity 2%', '% of equity', 'risk', dict(eqPct=2.0)), ('Fibonacci', 'Fibonacci', 'risk', {}),
         ('Step-up', 'Step-up (+$ per loss in a row)', 'risk', {}), ('Recover 50% of losses', 'Recover a % of losses per trade', 'risk', {}),
         ("D'Alembert", "D'Alembert", 'risk', {}), ('Paroli', 'Paroli', 'risk', {}), ('Crooks E over 3', 'Crooks E', 'risk', dict(cN=3)),
         ('Drawdown cut', 'Drawdown cut', 'risk', {}), ('Combo 2', 'C2', 'risk', {}), ('Combo 3', 'C3', 'risk', {}), ('Combo 4', 'C4', 'risk', {})]


def score(r, yrs=None):
    if r is None: return -1e9
    if yrs is None: return r['tot'] - 0.5 * r['dd']
    return sum(v for y, v in r['yr'].items() if y in yrs)


def tup(x, tp):
    d = x['dist']; rmin = d + 0.23
    return (x['net'], 0.0, None, None, 100.0 * (d + 0.23) / x['px'], rmin, None, 2 * rmin, tp * d / (d + 0.23))


def money(tr, tp):
    out = {}
    for lab, mode, sb, kw in RULES:
        allr = RC.simulate([tup(x, tp) for x in tr], mode, base=20.0, exitR=tp, start=1000.0, sizeBy=sb, **kw)
        yrs = {}; mons = {}
        for y in range(2021, 2027):
            ty = [x for x in tr if x['t'].year == y]
            r = RC.simulate([tup(x, tp) for x in ty], mode, base=20.0, exitR=tp, start=1000.0, sizeBy=sb, **kw)
            yrs[y] = dict(net=r['net'], dd=r['maxDDpct'], ruined=r['ruined'])
            for m in sorted({x['t'].month for x in ty}):
                rm = RC.simulate([tup(x, tp) for x in ty if x['t'].month == m], mode, base=20.0, exitR=tp, start=1000.0, sizeBy=sb, **kw)
                mons[(y, m)] = rm['net']
        out[lab] = dict(all=dict(net=allr['net'], dd=allr['maxDDpct'], ruined=allr['ruined']), years=yrs, months=mons)
    return out


if __name__ == '__main__':
    sys.argv = [sys.argv[0], 'M5', '0', '0']
    import edge, importlib.util                          # search.py loaded by path (another module named 'search' is on the gold path)
    sys.argv = [sys.argv[0], 'M5', '0', '0']
    _sp = importlib.util.spec_from_file_location('nt6_search', HERE + '/search.py'); SR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SR)
    P = {}
    for tf in TFS:
        sys.argv = [sys.argv[0], tf, '0', '0']
        R = [x for x in pickle.load(open(HERE + '/res_%s.pkl' % tf, 'rb')) if x[1] and x[1]['n'] >= MINTR[tf]]
        if not R: continue
        best = max(R, key=lambda x: score(x[1])); early = max(R, key=lambda x: score(x[1], (2021, 2022, 2023)))
        P[tf] = dict(n_searched=len(R))
        for tag, (c, r) in (('best', best), ('early', early)):
            on, eng = SR.cfg_eng(c)
            tr = edge.trades_for(tf, c['tp'], on, eng)
            P[tf][tag] = dict(cfg=c, stats=r, trades=[dict(t=x['t'], tx=x['tx'], net=x['net'], dist=x['dist'], px=x['px'], dir=x['dir']) for x in tr],
                              money=money(tr, c['tp']) if tag == 'best' else None)
            print(tf, tag, 'R %.1f dd %.1f n %d' % (r['tot'], r['dd'], r['n']), c, flush=True)
        # hindsight: the best setting of every month (from everything searched)
        hs = {}
        for c, r in R:
            for ym, v in r['mon'].items():
                if ym not in hs or v > hs[ym][0]: hs[ym] = (v, c)
        P[tf]['hindsight'] = hs
    pickle.dump(P, open(HERE + '/picks.pkl', 'wb')); print('saved', list(P))
