"""Final runs per timeframe: default, profit pick, streak pick (full trade records, partial close applied), the four pure TP exits of each pick,
the neighbourhood check of each pick (every single change on top of it), and the recovery rules on each sequence.
Usage: final.py TF [TF ...]   -> final_<TF>.pkl  (checkpointed per step)"""
import sys, os, pickle, math, collections, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import greedy, pickcfg, recovery as RC
def full(arg):
    tf, cfg = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    c = dict(cfg); p = c.pop('p1', 0.0); d = dict(greedy.defaults()); d.update(c)
    tr = geng.run(tf, c); out = []
    for x in tr:
        r = x['res']
        if p and d['exitAt'] > 1 and x['hits'][0]: r = p * d['tp1R'] + (1 - p) * r
        out.append((x['t'], r, x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be'], x['dir']))
    return out
def winR(cfg):
    d = dict(greedy.defaults()); d.update(cfg); R = (d['tp1R'], d['tp2R'], d['tp3R'], d['tp4R'])[d['exitAt'] - 1]
    p = d['p1'] if d['exitAt'] > 1 else 0.0
    return p * d['tp1R'] + (1 - p) * R
def recov(tr, exitR, cfg=None):
    """all rules on a trade sequence; with a partial close at TP1 each trade is passed in its two parts (Rule C updates its carried losses per part)"""
    d = dict(greedy.defaults()); d.update(cfg or {}); p = d['p1'] if d['exitAt'] > 1 else 0.0; t1 = d['tp1R']
    seq = [(x[1], x[4] / x[5], [(p * t1, p), (x[1] - p * t1, 1 - p)]) if (p and x[3][0]) else (x[1], x[4] / x[5]) for x in sorted(tr, key=lambda x: x[0])]
    out = []
    for mode in RC.MODES:
        for cap in (0.0, 500.0):
            r = RC.simulate(seq, mode, cap=cap, exitR=exitR); r['cap'] = cap; out.append(r)
    return out
if __name__ == '__main__':
    for tf in sys.argv[1:]:
        fn = S + '/gold/final_%s.pkl' % tf
        F = pickle.load(open(fn, 'rb')) if os.path.exists(fn) else {}
        save = lambda: (pickle.dump(F, open(fn + '.tmp', 'wb')), os.replace(fn + '.tmp', fn))
        if 'cfg' not in F:
            ch = pickcfg.choose(tf)
            F['cfg'] = {'default': {}, 'profit': ch['profit'][0], 'streak': ch['streak'][0]}
            F['passed'] = {'profit': ch['profit'][2], 'streak': ch['streak'][2]}; save()
        pool = mp.Pool(4)
        if 'trades' not in F:
            names = list(F['cfg']); res = pool.map(full, [(tf, F['cfg'][n]) for n in names])
            F['trades'] = dict(zip(names, res)); save(); print(tf, 'trades done', flush=True)
        if 'exits' not in F:
            tasks = []
            for n in ('default', 'profit', 'streak'):
                base = {k: v for k, v in F['cfg'][n].items() if k not in ('p1', 'mv1On', 'mv1R', 'mv2On', 'mv2R', 'mv3On', 'mv3R', 'exitAt')}
                for k in (1, 2, 3, 4): tasks.append(((n, k), greedy.norm(dict(base, exitAt=k))))
            res = pool.map(full, [(tf, c) for _, c in tasks])
            F['exits'] = {key: (c, r) for (key, c), r in zip(tasks, res)}; save(); print(tf, 'exits done', flush=True)
        if 'recovery' not in F:
            F['recovery'] = {n: recov(F['trades'][n], winR(F['cfg'][n]), F['cfg'][n]) for n in F['trades']}; save(); print(tf, 'recovery done', flush=True)
        if 'neigh' not in F:
            MV = greedy.moves(tf, lite=tf in ('M5', 'M1'), th=0.05 if tf == 'M1' else 0.0); F['neigh'] = {}
            for n in ('profit', 'streak'):
                cur = F['cfg'][n]; cands = []
                for mn, o in MV:
                    c = greedy.norm(dict(cur, **o))
                    if c != cur and greedy.valid(c): cands.append((mn, c))
                res = pool.map(full, [(tf, c) for _, c in cands])
                F['neigh'][n] = [(mn, c, [(x[0], x[1], x[3][0], x[4] / x[5]) for x in r]) for (mn, c), r in zip(cands, res)]
                save(); print(tf, n, 'neighbourhood done', len(cands), flush=True)
        pool.close()
