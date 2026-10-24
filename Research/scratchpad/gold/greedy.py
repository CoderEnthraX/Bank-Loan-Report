"""Stage E: greedy search over every indicator setting in combination.
Start from a configuration; each round try every single change (the stage-A list plus extra levels, partial close at TP1,
and a reset-to-default for every setting already changed) on top of it; keep the change that most improves the 2021-23 score;
repeat until nothing improves. 2024-26 is never used to choose, only reported.
Score = sum of net R after spread in 2021-23 / sqrt(trades) (a t-like value: edge and sample size together).
Objectives: profit = best score; streak = best score among settings whose longest losing streak in 2021-23 is <= LMAX.
Usage: greedy.py TF lite|full maxRounds obj:start [obj:start ...]   (start = default | bestB | profit = the final profit config)
Checkpoint: greedy_<tf>.pkl holds every search's path; a restarted search continues from its last accepted step."""
import sys, os, math, pickle, collections, multiprocessing as mp
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
LMAX = 7
DEF = None
def defaults():
    global DEF
    if DEF is None:
        import ref_gs; DEF = dict(ref_gs.IN); DEF.update(vwAnchorG='session', vwSrcG='hlc3', p1=0.0)
    return DEF
def moves(tf, lite=False, th=0.0):
    import sweep
    mv = [(n, o) for n, o in sweep.C if n != 'default' and not n.startswith(('Days:', 'Longs only', 'Shorts only'))]
    add = lambda name, k, vals: mv.extend(('%s = %s' % (name, v), {k: v}) for v in vals)
    add('stopAtr', 'stopAtr', (2.0, 2.4, 2.8, 3.5, 4.0)); add('cooldownBars', 'cooldownBars', (8, 20, 30)); add('minOpenBars', 'minOpenBars', (9, 18))
    add('dispAtr', 'dispAtr', (0.4,)); add('tp1R', 'tp1R', (0.4, 0.5, 0.8)); add('tp2R', 'tp2R', (0.8, 1.2)); add('tp3R', 'tp3R', (1.2, 1.8))
    for s in (1.0, 1.25, 1.75, 2.2, 2.6): mv.append(("Don't Chase = %.2f sigma" % s, dict(noChase=True, noChaseSig=s)))
    for m in (6.0, 10.0): mv.append(('Choppy sessions max crosses = %d' % m, dict(chopOn=True, chopMax=m)))
    for m in (1.0, 1.4): mv.append(('1h EMA20 speed cap = %.2f' % m, dict(emaOn=True, emaMax=m)))
    for m in (0.25, 0.75): mv.append(('Min distance from VWAP = %.2f ATR' % m, dict(minVwOn=True, minVwAtr=m)))
    for p in (0.3, 0.5, 0.7): mv.append(('Close %d%% at TP1' % (100 * p), dict(p1=p)))
    if lite:
        import anaA
        M = anaA.sweep_metrics(tf)[1]; d0 = M['default']
        keep = []
        for n, o in mv:
            if n in M:
                m = M[n]
                if m is None or m['EcA'] - d0['EcA'] < th: continue
            keep.append((n, o))
        mv = keep
    return mv
def ekey(cfg):
    return tuple(sorted((k, v) for k, v in cfg.items() if k != 'p1'))
def valid(cfg):
    d = dict(defaults()); d.update(cfg)
    return d['tp1R'] < d['tp2R'] < d['tp3R'] < d['tp4R']
def norm(cfg):
    d = defaults(); c = {k: v for k, v in cfg.items() if d.get(k, object()) != v}
    if c.get('exitAt', 4) == 1: c.pop('p1', None)
    if not c.get('noChase'): c.pop('noChaseSig', None)
    for on, k in (('chopOn', 'chopMax'), ('emaOn', 'emaMax'), ('minVwOn', 'minVwAtr'), ('kzOn', 'kz'), ('kzOn', 'kzShift'), ('hoursOn', 'hoursSess'),
                  ('mv1On', 'mv1R'), ('mv2On', 'mv2R'), ('mv3On', 'mv3R'), ('dayOn', 'days')):
        if not c.get(on): c.pop(k, None)
    return c
def pack(rows):
    """rows of (fill time, R, TP1 reached, spread in R) -> compact arrays"""
    return (np.array([r[0].year for r in rows], dtype=np.int16), np.array([r[1] for r in rows], dtype=np.float64),
            np.array([bool(r[2]) for r in rows], dtype=bool), np.array([r[3] for r in rows], dtype=np.float64))
def job(arg):
    tf, key = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    tr = geng.run(tf, dict(key))
    return key, pack([(x['t'], x['res'], x['hits'][0], x['sp'] / x['risk']) for x in tr])
def streaks(seq):
    mw = ml = cw = cl = 0
    for r in seq:
        if r > 0: cw += 1; cl = 0; mw = max(mw, cw)
        elif r < 0: cl += 1; cw = 0; ml = max(ml, cl)
        else: cw = cl = 0
    return mw, ml
def metrics(pk, cfg):
    d = dict(defaults()); d.update(cfg); p = d['p1'] if d['exitAt'] > 1 else 0.0
    yr, res, h, c = pk
    if p: res = np.where(h, p * d['tp1R'] + (1 - p) * res, res)
    net = res - c; out = {}
    for lab, msk in (('A', yr <= 2023), ('B', yr >= 2024), ('all', np.ones(len(yr), dtype=bool))):
        n = int(msk.sum()); s = float(net[msk].sum()); w, l = streaks(res[msk].tolist())
        out[lab] = dict(n=n, net=s, E=s / n if n else 0.0, t=s / math.sqrt(n) if n else -9.0, maxW=w, maxL=l, win=float((res[msk] > 0).mean()) if n else 0.0)
    ys = sorted(set(yr.tolist())); out['years'] = {y: float(net[yr == y].sum()) for y in ys}
    out['ypos'] = sum(1 for y in ys if out['years'][y] > 0)
    out['tp1'] = float(h.mean()) if len(h) else 0.0
    return out
def rank(m, obj, minN):
    a = m['A']
    if a['n'] < minN: return (0, -1e9 + a['n'])
    if obj == 'streak' and a['maxL'] > LMAX: return (0, -a['maxL'] + 0.01 * a['t'])
    return (1, a['t'] + 0.001 * a['maxW'])
def seed(tf, cache):
    """engine runs already done in stages A-C, keyed like job()"""
    for f, kind in (('sweep', 'A'), ('stageB', 'B'), ('stageC', 'C')):
        fn = S + '/gold/%s_%s.pkl' % (f, tf)
        if not os.path.exists(fn): continue
        D = pickle.load(open(fn, 'rb'))
        if kind == 'A': items = [(dict(D['configs'])[n], tr) for n, tr in D['res'].items()]
        elif kind == 'B': opts = dict(D['combos']); items = [(opts[n], tr) for n, tr in D['res'].items()]
        else:
            import stageC; co = dict(D['cands']); eo = dict(stageC.EXITS)
            items = [(dict(co[cn], **eo[en]), tr) for (cn, en), tr in D['res'].items() if en in eo]
        for o, tr in items:
            k = ekey(norm(o))
            if k not in cache: cache[k] = pack([(x[0], x[1], x[3][0], x[4] / x[5]) for x in tr])
def bestB(tf, minN):
    D = pickle.load(open(S + '/gold/stageB_%s.pkl' % tf, 'rb')); opts = dict(D['combos'])
    best = None
    for n, tr in D['res'].items():
        if not tr: continue
        m = metrics(pack([(x[0], x[1], x[3][0], x[4] / x[5]) for x in tr]), {})
        r = rank(m, 'profit', minN)
        if best is None or r > best[0]: best = (r, n)
    return norm(opts[best[1]]), best[1].split(' + ')
if __name__ == '__main__':
    tf, lite, maxR = sys.argv[1], sys.argv[2].startswith('lite'), int(sys.argv[3]); searches = [a.split(':') for a in sys.argv[4:]]
    th = float(sys.argv[2][4:]) if lite and len(sys.argv[2]) > 4 else 0.0
    ck = S + '/gold/greedy_%s.pkl' % tf
    paths = pickle.load(open(ck, 'rb')) if os.path.exists(ck) else {}
    cache = {}; seed(tf, cache); print(tf, 'seeded', len(cache), 'engine runs', flush=True)
    MV = moves(tf, lite, th); print(tf, len(MV), 'moves', flush=True)
    import anaA
    d0 = anaA.sweep_metrics(tf)[1]['default']
    minN = max(60, int(0.2 * d0['nA']))
    pool = mp.Pool(4)
    pfile = S + '/gold/greedy_pool_%s.pkl' % tf
    POOL = pickle.load(open(pfile, 'rb')) if os.path.exists(pfile) else {}
    def record(k):
        base = dict(k)
        for p in ((0.0,) if base.get('exitAt', 4) == 1 else (0.0, 0.3, 0.5, 0.7)):
            c = dict(base); c['p1'] = p; c = norm(c); pk = (ekey(c), c.get('p1', 0.0))
            if pk not in POOL: POOL[pk] = (c, metrics(cache[k], c))
    def save_pool():
        pickle.dump(POOL, open(pfile + '.tmp', 'wb')); os.replace(pfile + '.tmp', pfile)
    for k in list(cache): record(k)
    save_pool()
    def evaluate(cfgs):
        need = sorted({ekey(c) for c in cfgs if ekey(c) not in cache})
        for k, pk in pool.imap_unordered(job, [(tf, k) for k in need]): cache[k] = pk; record(k)
        return [metrics(cache[ekey(c)], c) for c in cfgs]
    for obj, start in searches:
        sid = '%s:%s' % (obj, start)
        if sid in paths and paths[sid][-1].get('done'): print(sid, 'already done', flush=True); continue
        if start == 'default': cur, names = {}, []
        elif start == 'bestB': cur, names = bestB(tf, minN)
        else: cur, names = paths['%s:default' % start][-1]['cfg'], list(paths['%s:default' % start][-1]['names'])
        path = paths.get(sid) or []
        if path: cur, names = path[-1]['cfg'], list(path[-1]['names'])
        curM = evaluate([cur])[0]
        if not path: path.append(dict(cfg=cur, names=list(names), m=curM, move='start'))
        paths[sid] = path
        print('\n%s %s start: %s | A %+.3f (n %d, L %d) B %+.3f' % (tf, sid, ' + '.join(names) or 'default', curM['A']['E'], curM['A']['n'], curM['A']['maxL'], curM['B']['E']), flush=True)
        for rnd in range(len(path) - 1, maxR):
            cands = []
            for n, o in MV:
                c = norm(dict(cur, **o))
                if c != cur and valid(c): cands.append((n, c))
            for k in list(cur):
                if k in ('noChaseSig', 'chopMax', 'emaMax', 'minVwAtr', 'kz', 'kzShift', 'hoursSess', 'mv1R', 'mv2R', 'mv3R', 'days'): continue
                c = dict(cur); c.pop(k); c = norm(c)
                if c != cur and valid(c): cands.append(('reset %s' % k, c))
            ms = evaluate([c for _, c in cands])
            best = max(range(len(cands)), key=lambda i: rank(ms[i], obj, minN))
            bn, bc = cands[best]; bm = ms[best]
            r0, r1 = rank(curM, obj, minN), rank(bm, obj, minN)
            if not (r1[0] > r0[0] or (r1[0] == r0[0] and r1[1] > r0[1] + (0.05 if r1[0] else 1e-9))):
                print('round %d: no improvement (best try %s)' % (rnd + 1, bn), flush=True); break
            cur, curM = bc, bm
            fam = bn.split(' = ')[0].split(': ')[0]
            if bn.startswith('reset '):
                names = [x for x in names if not x.lower().startswith(bn[6:].lower())]
            else:
                names = [x for x in names if not (x.split(' = ')[0].split(': ')[0] == fam)] + [bn]
            path.append(dict(cfg=cur, names=list(names), m=curM, move=bn))
            pickle.dump(paths, open(ck + '.tmp', 'wb')); os.replace(ck + '.tmp', ck); save_pool()
            print('round %d: %s | A %+.3f (n %d, win %.1f%%, W/L %d/%d) | B %+.3f (n %d, W/L %d/%d) | yrs+ %d | score %.2f' % (
                rnd + 1, bn, curM['A']['E'], curM['A']['n'], 100 * curM['A']['win'], curM['A']['maxW'], curM['A']['maxL'], curM['B']['E'], curM['B']['n'],
                curM['B']['maxW'], curM['B']['maxL'], curM['ypos'], r1[1]), flush=True)
        path[-1]['done'] = True
        pickle.dump(paths, open(ck + '.tmp', 'wb')); os.replace(ck + '.tmp', ck); save_pool()
        print('final %s: %s' % (sid, cur), flush=True)
    pool.close()
