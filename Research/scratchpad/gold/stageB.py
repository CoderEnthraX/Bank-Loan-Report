"""Stage B: combinations (size 1-4) of the settings that improved 2021-23 after spread in the sweep (one value per setting family)."""
import sys, pickle, itertools, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
EXCL = ('Final exit', 'TP4 =', 'Stop to', 'BE at', 'Days:', 'Longs only', 'Shorts only', 'default')
def family(name):
    for sep in (' = ', ': '):
        if sep in name: return name.split(sep)[0]
    return name
def ingredients(tf, k=8, minDelta=0.015, minShare=0.15):
    import anaA
    D = pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb')); C = dict(D['configs']); R = D['res']
    rows = [(n, anaA.metrics(R[n])) for n in R if R[n]]; d0 = dict(rows)['default']
    cand = []
    for n, m in rows:
        if any(n.startswith(e) for e in EXCL) or m is None: continue
        if m['nA'] < minShare * d0['nA']: continue
        if m['EcA'] - d0['EcA'] >= minDelta: cand.append((m['EcA'] - d0['EcA'], n))
    cand.sort(reverse=True); picked = []; fams = set()
    for dlt, n in cand:
        f = family(n)
        if f.startswith('Kill zones') or f.startswith('Hours'): f = 'session'
        if f in fams: continue
        fams.add(f); picked.append((n, C[n]))
        if len(picked) >= k: break
    return picked
def job(arg):
    tf, name, o = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    tr = geng.run(tf, o)
    return tf, name, [(x['t'], x['res'], x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be']) for x in tr]
if __name__ == '__main__':
    tf = sys.argv[1]
    ing = ingredients(tf)
    print(tf, 'ingredients:', [n for n, _ in ing], flush=True)
    combos = []
    for r in range(1, 5):
        for sub in itertools.combinations(ing, r):
            o = {}
            for _, d in sub: o.update(d)
            combos.append((' + '.join(n for n, _ in sub), o))
    out = {}
    with mp.Pool(4) as pool:
        for t, name, tr in pool.imap_unordered(job, [(tf, n, o) for n, o in combos]): out[name] = tr
    pickle.dump(dict(ingredients=ing, combos=combos, res=out), open(S + '/gold/stageB_%s.pkl' % tf, 'wb'))
    print(tf, 'combos done', len(out), flush=True)
