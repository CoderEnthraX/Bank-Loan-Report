"""Let the gold scripts run from the slim checkpoint results (slim_*.pkl) when the big result pickles are not there."""
G = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/'
def patch(fn, pairs):
    s = open(G + fn).read()
    for a, b in pairs:
        assert s.count(a) == 1, (fn, a[:70])
        s = s.replace(a, b)
    open(G + fn, 'w').write(s); print('patched', fn)
patch('anaA.py', [
("import sys, pickle, collections, json\n", "import sys, os, pickle, collections, json\n"),
("def metrics(tr):", '''def sweep_metrics(tf):
    """(configs, {setting name: metrics}) of the stage-A sweep, from sweep_<tf>.pkl or the slim checkpoint copy slim_sweep_<tf>.pkl"""
    fn = S + '/gold/sweep_%s.pkl' % tf
    if os.path.exists(fn):
        D = pickle.load(open(fn, 'rb')); return D['configs'], {n: metrics(t) for n, t in D['res'].items() if t}
    D = pickle.load(open(S + '/gold/slim_sweep_%s.pkl' % tf, 'rb')); return D['configs'], D['metrics']
def metrics(tr):''')])
patch('pickcfg.py', [
("    d0 = anaA.metrics(pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb'))['res']['default'])",
 "    d0 = anaA.sweep_metrics(tf)[1]['default']")])
patch('greedy.py', [
("""        R = pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb'))['res']; d0 = anaA.metrics(R['default'])
        keep = []
        for n, o in mv:
            if n in R and R[n]:
                m = anaA.metrics(R[n])
                if m is None or m['EcA'] - d0['EcA'] < th: continue
            keep.append((n, o))""",
"""        M = anaA.sweep_metrics(tf)[1]; d0 = M['default']
        keep = []
        for n, o in mv:
            if n in M:
                m = M[n]
                if m is None or m['EcA'] - d0['EcA'] < th: continue
            keep.append((n, o))"""),
("    d0 = anaA.metrics(pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb'))['res']['default'])",
 "    d0 = anaA.sweep_metrics(tf)[1]['default']")])
patch('build_final.py', [
("""        fn = S + '/gold/sweep_%s.pkl' % tf
        if not os.path.exists(fn): continue
        D = pickle.load(open(fn, 'rb')); rows = [(n, anaA.metrics(D['res'][n])) for n, _ in D['configs'] if D['res'].get(n)]
        rows = [x for x in rows if x[1]]; rows.sort(key=lambda x: (x[0] != 'default', -x[1]['EcA']))""",
"""        if not (os.path.exists(S + '/gold/sweep_%s.pkl' % tf) or os.path.exists(S + '/gold/slim_sweep_%s.pkl' % tf)): continue
        C, M = anaA.sweep_metrics(tf); rows = [(n, M[n]) for n, _ in C if n in M]
        rows = [x for x in rows if x[1]]; rows.sort(key=lambda x: (x[0] != 'default', -x[1]['EcA']))"""),
("""        fn = S + '/gold/stageB_%s.pkl' % tf
        if not os.path.exists(fn): continue
        D = pickle.load(open(fn, 'rb')); d0 = anaA.metrics(pickle.load(open(S + '/gold/sweep_%s.pkl' % tf, 'rb'))['res']['default'])
        rows = [(n, anaA.metrics(t)) for n, t in D['res'].items() if t]; rows = [x for x in rows if x[1] and x[1]['nA'] >= 0.15 * d0['nA']]""",
"""        fn = S + '/gold/stageB_%s.pkl' % tf; fs = S + '/gold/slim_stageB_%s.pkl' % tf
        if os.path.exists(fn): D = pickle.load(open(fn, 'rb')); rows = [(n, anaA.metrics(t)) for n, t in D['res'].items() if t]
        elif os.path.exists(fs): rows = list(pickle.load(open(fs, 'rb'))['metrics'].items())
        else: continue
        d0 = anaA.sweep_metrics(tf)[1]['default']; rows = [x for x in rows if x[1] and x[1]['nA'] >= 0.15 * d0['nA']]"""),
("""            for mn, c, tr in FIN[tf]['neigh'][prof]:
                if not tr: continue
                m = greedy.metrics(greedy.pack(tr), {}); rows.append((mn, m))""",
"""            for mn, c, tr in FIN[tf]['neigh'][prof]:
                if not tr: continue
                m = tr if isinstance(tr, dict) else greedy.metrics(greedy.pack(tr), {}); rows.append((mn, m))"""),
])
s = open(G + 'build_final.py').read()
i = s.index('def exits_sheet(wb):'); j = s.index('# ----', i)
print(s[i:j])
