p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/greedy.py'; s=open(p).read()
A=("""    pool = mp.Pool(4)
    def evaluate(cfgs):
        need = sorted({ekey(c) for c in cfgs if ekey(c) not in cache})
        for k, pk in pool.imap_unordered(job, [(tf, k) for k in need]): cache[k] = pk
        return [metrics(cache[ekey(c)], c) for c in cfgs]
""","""    pool = mp.Pool(4)
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
""")
B=("""            path.append(dict(cfg=cur, names=list(names), m=curM, move=bn))
            pickle.dump(paths, open(ck + '.tmp', 'wb')); os.replace(ck + '.tmp', ck)""","""            path.append(dict(cfg=cur, names=list(names), m=curM, move=bn))
            pickle.dump(paths, open(ck + '.tmp', 'wb')); os.replace(ck + '.tmp', ck); save_pool()""")
C=("""        path[-1]['done'] = True
        pickle.dump(paths, open(ck + '.tmp', 'wb')); os.replace(ck + '.tmp', ck)""","""        path[-1]['done'] = True
        pickle.dump(paths, open(ck + '.tmp', 'wb')); os.replace(ck + '.tmp', ck); save_pool()""")
D=("""    out['ypos'] = sum(1 for y in set(yr.tolist()) if net[yr == y].sum() > 0)
    return out""","""    ys = sorted(set(yr.tolist())); out['years'] = {y: float(net[yr == y].sum()) for y in ys}
    out['ypos'] = sum(1 for y in ys if out['years'][y] > 0)
    out['tp1'] = float(h.mean()) if len(h) else 0.0
    return out""")
for a,b in (A,B,C,D):
    assert s.count(a)==1, a[:60]
    s=s.replace(a,b)
open(p,'w').write(s); print('patched')
