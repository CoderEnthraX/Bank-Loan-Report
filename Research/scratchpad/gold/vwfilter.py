"""Do trades far from the VWAP lose more? Distance of the signal candle's close from the VWAP at the signal, in ATR, in price ($) and in
VWAP standard deviations (sigma, the 'Don't Chase' measure), for the default settings and every catalogue strategy, every timeframe.
Part 1 (collect): one engine run per setting (filter off), per trade: R after spread, distance. Saved to vwfilter_trades.pkl.
Part 2 (scan): a 'max distance' cut-off keeps a trade only if its distance <= X. Each cut-off is scored on 2021-23 and on 2024-26.
Usage: vwfilter.py collect | scan"""
import sys, os, math, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
TFS = ('M1', 'M5', 'M15', 'H1')
def sources(tf):
    C = pickle.load(open(S + '/gold/catalog_%s.pkl' % tf, 'rb'))
    out = [('Default settings', ['Default settings'], {})]
    for k, s in enumerate(C['strategies']): out.append(('%s-S%d' % (tf, k + 1), [n for n, _ in s['scen']], s['cfg']))
    return out
def collect(arg):
    tf, name, scen, cfg = arg
    import geng, ref_gs, greedy
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    c = dict(cfg); p1 = c.pop('p1', 0.0); d = dict(greedy.defaults()); d.update(c)
    vw = c.pop('vwAnchorG', 'session'); src = c.pop('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    o = dict(c); o['needW'] = True
    out = []
    for x in ref_gs.run(tf, o):
        if x['exit'] is None or x['ghost']: continue
        R1 = x['dir'] * (x['entry'] - x['stop']); res = x['res']
        exitR = (d['tp1R'], d['tp2R'], d['tp3R'], d['tp4R'])[d['exitAt'] - 1]          # TP1 reached: exactly as geng.run / final.full
        win = res is not None and abs(res - exitR) < 1e-9 and x['exit'] > x['fill']
        tp1 = win or (d['exitAt'] > 1 and x['dir'] * (x['best'] - (x['entry'] + x['dir'] * d['tp1R'] * R1)) >= -P['mt'] * 0.001)
        if p1 and d['exitAt'] > 1 and tp1: res = p1 * d['tp1R'] + (1 - p1) * res
        out.append(dict(t=P['T'][x['fill']], r=res - P['SP'][x['fill']] / R1, a=x['vwdA'], p=x['vwd'], z=x['vwz'], dir=x['dir']))
    return tf, name, scen, cfg, out
def streak(rs):
    m = c = 0
    for r in rs:
        c = c + 1 if r < 0 else (0 if r > 0 else c)
        m = max(m, c)
    return m
def score(tr):
    n = len(tr); R = sum(x['r'] for x in tr)
    return dict(n=n, R=R, E=R / n if n else 0.0, t=R / math.sqrt(n) if n else 0.0, win=sum(1 for x in tr if x['r'] > 0) / n if n else 0.0, maxL=streak([x['r'] for x in tr]))
def scan(T):
    out = {}
    for key, d in T.items():
        tr = d['trades']; A = [x for x in tr if x['t'].year <= 2023]; B = [x for x in tr if x['t'].year >= 2024]
        res = {'none': dict(all=score(tr), A=score(A), B=score(B))}
        ps = sorted(x['p'] for x in tr)
        grids = {'atr': [round(0.5 + 0.25 * k, 2) for k in range(23)],
                 'price': sorted({round(ps[int(q * (len(ps) - 1))], 2) for q in [0.3 + 0.025 * k for k in range(28)]}),
                 'sigma': [round(0.5 + 0.25 * k, 2) for k in range(15)]}
        for unit, grid in grids.items():
            f = {'atr': lambda x: x['a'], 'price': lambda x: x['p'], 'sigma': lambda x: x['z'] if x['z'] is not None else -99.0}[unit]
            for X in grid:
                keep = lambda L: [x for x in L if f(x) <= X + 1e-12]
                res[(unit, X)] = dict(all=score(keep(tr)), A=score(keep(A)), B=score(keep(B)))
        # buckets in ATR, for the "where are the losers" view
        edges = (0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 99.0)
        bk = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            q = [x for x in tr if lo <= x['a'] < hi]
            bk.append((lo, hi, score(q)))
        out[key] = dict(res=res, buckets=bk, n=len(tr))
    return out
def pick(res, unit):
    """cut-off chosen on 2021-23 only (most R after spread, at least 60% of the trades kept), then read on 2024-26"""
    base = res['none']
    cands = [(k, v) for k, v in res.items() if k != 'none' and k[0] == unit and v['A']['n'] >= 0.6 * base['A']['n']]
    if not cands: return None
    k, v = max(cands, key=lambda kv: (round(kv[1]['A']['R'], 6), -kv[0][1]))
    return k, v
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'collect'
    fn = S + '/gold/vwfilter_trades.pkl'
    if mode in ('collect', 'collect_tp2'):
        jobs = [(tf, n, sc, c) for tf in TFS for n, sc, c in sources(tf)]
        if mode == 'collect_tp2':          # the same settings with the final exit at TP2 (default, most profit, shortest losing streak)
            fn = S + '/gold/vwfilter_trades_tp2.pkl'
            jobs = [(tf, n + ' exit TP2', sc, dict(c, exitAt=2)) for tf, n, sc, c in jobs if n in ('Default settings', tf + '-S1', tf + '-S2')]
        jobs.sort(key=lambda j: TFS.index(j[0]))      # M1 first: the slow ones
        with mp.Pool(4) as pool: res = pool.map(collect, jobs)
        T = {(tf, n): dict(scen=sc, cfg=c, trades=tr) for tf, n, sc, c, tr in res}
        pickle.dump(T, open(fn, 'wb')); print('saved', len(T), 'settings', sum(len(v['trades']) for v in T.values()), 'trades')
    else:
        T = pickle.load(open(fn, 'rb'))
        if os.path.exists(S + '/gold/vwfilter_trades_tp2.pkl'): T.update(pickle.load(open(S + '/gold/vwfilter_trades_tp2.pkl', 'rb')))
        out = scan(T)
        pickle.dump(out, open(S + '/gold/vwfilter_scan.pkl', 'wb'))
        L = []
        for (tf, n), d in sorted(out.items(), key=lambda kv: (TFS.index(kv[0][0]), kv[0][1] != 'Default settings', kv[0][1])):
            b = d['res']['none']
            L.append('\n%s %s (%s) | %d trades | R/trade after spread %+.3f (21-23 %+.3f, 24-26 %+.3f) | longest losing streak %d' % (
                tf, n, ', '.join(T[(tf, n)]['scen'][:2]), d['n'], b['all']['E'], b['A']['E'], b['B']['E'], b['all']['maxL']))
            L.append('   by distance (ATR): ' + ' | '.join('%.1f-%s: %d tr %+.3f' % (lo, ('%.1f' % hi) if hi < 50 else 'up', s['n'], s['E']) for lo, hi, s in d['buckets'] if s['n']))
            for unit in ('atr', 'sigma', 'price'):
                pk = pick(d['res'], unit)
                if not pk: continue
                (u, X), v = pk
                L.append('   %-5s cut-off chosen on 21-23: <= %-6s keeps %4.0f%% | 21-23 R %+7.1f -> %+7.1f | 24-26 R %+7.1f -> %+7.1f (R/trade %+.3f -> %+.3f) | longest losing streak %d -> %d' % (
                    unit, X, 100 * v['all']['n'] / max(1, b['all']['n']), b['A']['R'], v['A']['R'], b['B']['R'], v['B']['R'], b['B']['E'], v['B']['E'], b['all']['maxL'], v['all']['maxL']))
        open(S + '/gold/vwfilter.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
