"""Signals still sitting on the VWAP (gold 2021-2026, the same 41 settings as vwfilter.py). Three skip rules, measured on the signal candle:
  stop   d x (stop - VWAP) / ATR       skip below the cut-off b   (b = 0: the stop is on the other side of the VWAP)
  touch  candles since the candle range last reached the VWAP (0 = the signal candle itself)   skip below N
  entry  d x (entry - VWAP) / ATR      skip below X               (entry level too close to the VWAP, or beyond it)
collect: one engine run per setting (filters off), per trade: R after spread and the three measures -> vwfilter2_trades.pkl
scan: every cut-off scored on 2021-23 and on 2024-26 -> vwfilter2_scan.pkl + vwfilter2.txt
check: the engine with each rule switched on gives exactly the trades that the scan keeps (skipped setups still run invisibly)."""
import sys, os, math, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import vwfilter as VF
TFS = VF.TFS
GRID = {'stop': [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5],
        'touch': [1, 2, 3, 4, 5, 6, 8, 10, 15, 20],
        'entry': [-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]}
KEY = {'stop': 'vs', 'touch': 'vt', 'entry': 've'}
def run_engine(tf, cfg, extra=None):
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    c = dict(cfg); c.pop('p1', None)
    vw = c.pop('vwAnchorG', 'session'); src = c.pop('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    o = dict(c); o.update(extra or {})
    return P, ref_gs.run(tf, o)
def collect(arg):
    tf, name, scen, cfg = arg
    import greedy
    p1 = cfg.get('p1', 0.0); d = dict(greedy.defaults()); d.update({k: v for k, v in cfg.items() if k != 'p1'})
    P, trs = run_engine(tf, cfg)
    out = []
    for x in trs:
        if x['exit'] is None or x['ghost']: continue
        R1 = x['dir'] * (x['entry'] - x['stop']); res = x['res']
        exitR = (d['tp1R'], d['tp2R'], d['tp3R'], d['tp4R'])[d['exitAt'] - 1]
        win = res is not None and abs(res - exitR) < 1e-9 and x['exit'] > x['fill']
        tp1 = win or (d['exitAt'] > 1 and x['dir'] * (x['best'] - (x['entry'] + x['dir'] * d['tp1R'] * R1)) >= -P['mt'] * 0.001)
        if p1 and d['exitAt'] > 1 and tp1: res = p1 * d['tp1R'] + (1 - p1) * res
        out.append(dict(t=P['T'][x['fill']], arm=x['arm'], r=res - P['SP'][x['fill']] / R1, vs=x['vs'], vt=x['vt'], ve=x['ve'], dir=x['dir']))
    return tf, name, scen, cfg, out
def keep(x, rule, cut): return x[KEY[rule]] >= cut
def scan(T):
    out = {}
    for key, d in T.items():
        tr = d['trades']; A = [x for x in tr if x['t'].year <= 2023]; B = [x for x in tr if x['t'].year >= 2024]
        res = {'none': dict(all=VF.score(tr), A=VF.score(A), B=VF.score(B))}
        for rule, grid in GRID.items():
            for cut in grid:
                k = lambda L: [x for x in L if keep(x, rule, cut)]
                res[(rule, cut)] = dict(all=VF.score(k(tr)), A=VF.score(k(A)), B=VF.score(k(B)))
        bk = {}
        for rule, edges in (('stop', (-99, -1.0, -0.5, 0.0, 0.5, 99)), ('touch', (0, 1, 2, 3, 5, 10, 20, 10 ** 10)), ('entry', (-99, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 99))):
            bk[rule] = [(lo, hi, VF.score([x for x in tr if lo <= x[KEY[rule]] < hi])) for lo, hi in zip(edges[:-1], edges[1:])]
        out[key] = dict(res=res, buckets=bk, n=len(tr))
    return out
def pick(res, rule):
    """cut-off chosen on 2021-23 only (most R after spread, at least 60% of the trades kept), then read on 2024-26"""
    base = res['none']
    c = [(k, v) for k, v in res.items() if k != 'none' and k[0] == rule and v['A']['n'] >= 0.6 * base['A']['n']]
    return max(c, key=lambda kv: (round(kv[1]['A']['R'], 6), -abs(kv[0][1]))) if c else None
def check(arg):
    """engine with the rule on == the trades the scan keeps (arm bars compared)"""
    tf, name, cfg, rule, cut, kept = arg
    opt = {'stop': dict(stopVwOn=True, stopVwBuf=cut), 'touch': dict(touchVwOn=True, touchVwN=cut), 'entry': dict(entVwOn=True, entVwAtr=cut)}[rule]
    P, trs = run_engine(tf, cfg, opt)
    got = sorted(x['arm'] for x in trs if x['exit'] is not None and not x['ghost'])
    return tf, name, rule, cut, got == sorted(kept), len(got), len(kept)
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'collect'
    fn = S + '/gold/vwfilter2_trades.pkl'
    if mode == 'collect':
        jobs = [(tf, n, sc, c) for tf in TFS for n, sc, c in VF.sources(tf)]
        jobs += [(tf, n + ' exit TP2', sc, dict(c, exitAt=2)) for tf, n, sc, c in list(jobs) if n in ('Default settings', tf + '-S1', tf + '-S2')]
        jobs.sort(key=lambda j: TFS.index(j[0]))
        with mp.Pool(4) as pool: res = pool.map(collect, jobs)
        T = {(tf, n): dict(scen=sc, cfg=c, trades=tr) for tf, n, sc, c, tr in res}
        pickle.dump(T, open(fn, 'wb')); print('saved', len(T), 'settings', sum(len(v['trades']) for v in T.values()), 'trades')
    elif mode == 'check':
        T = pickle.load(open(fn, 'rb'))
        jobs = []
        for key in (('M15', 'Default settings'), ('H1', 'H1-S1'), ('M15', 'M15-S1')):
            d = T[key]
            for rule, cut in (('stop', 0.0), ('touch', 3), ('entry', 0.5)):
                jobs.append((key[0], key[1], d['cfg'], rule, cut, [x['arm'] for x in d['trades'] if keep(x, rule, cut)]))
        with mp.Pool(4) as pool:
            for r in pool.map(check, jobs): print('%s %s %s %s: engine == scan %s (%d / %d trades)' % r)
    else:
        T = pickle.load(open(fn, 'rb'))
        out = scan(T); pickle.dump(out, open(S + '/gold/vwfilter2_scan.pkl', 'wb'))
        L = []
        for (tf, n), d in sorted(out.items(), key=lambda kv: (TFS.index(kv[0][0]), kv[0][1] != 'Default settings', kv[0][1])):
            b = d['res']['none']; anc = T[(tf, n)]['cfg'].get('vwAnchorG', 'session')
            L.append('\n%s %s (%s, VWAP %s) | %d trades | R/trade %+.3f (21-23 %+.3f, 24-26 %+.3f)' % (tf, n, ', '.join(T[(tf, n)]['scen'][:2]), anc, d['n'], b['all']['E'], b['A']['E'], b['B']['E']))
            for rule in GRID:
                L.append('   %-5s by bucket: ' % rule + ' | '.join('%s-%s: %d tr %+.3f' % (lo, hi if hi < 99 else 'up', s['n'], s['E']) for lo, hi, s in d['buckets'][rule] if s['n']))
                pk = pick(d['res'], rule)
                if pk:
                    (u, X), v = pk
                    L.append('   %-5s chosen on 21-23: >= %-5s keeps %3.0f%% | 21-23 R %+7.1f -> %+7.1f | 24-26 R %+7.1f -> %+7.1f (R/trade %+.3f -> %+.3f)' % (
                        rule, X, 100 * v['all']['n'] / max(1, b['all']['n']), b['A']['R'], v['A']['R'], b['B']['R'], v['B']['R'], b['B']['E'], v['B']['E']))
        open(S + '/gold/vwfilter2.txt', 'w').write('\n'.join(L) + '\n'); print('written', len(out))
