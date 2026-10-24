import pickle, sys
R = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/dfeat.pkl', 'rb'))
feats = [k for k in R[0] if k[:2] in ('U_', 'M_')]
firsts = [k for k in R[0] if k.startswith('np')]
pre = sys.argv[1] if len(sys.argv) > 1 else ''
res = []
for fk in firsts:
    sub = [r for r in R if r[fk] == 0]
    if pre:  # extra conjunct like U_pdb<-1
        k, th = pre.split('<'); sub = [r for r in sub if r[k] < float(th)]
    T = [r for r in sub if r['tight']]
    if len(T) < 8: continue
    N = [r for r in sub if not r['tight']]
    for f in feats:
        tv = [r[f] for r in T]
        for side in ('le', 'ge'):
            th = max(tv) if side == 'le' else min(tv)
            fp = [r for r in N if (r[f] <= th if side == 'le' else r[f] >= th)]
            # margin: distance between th and nearest normal outside
            out = [r[f] for r in N if r not in fp]
            mg = (min(out) - th) if side == 'le' and out else (th - max(out)) if out else 99
            res.append((len(fp), -mg, fk, f, side, round(th, 3), round(mg, 3), [f"{r['sym']} {r['fill'][5:]}" for r in fp]))
res.sort(key=lambda x: (x[0], x[1]))
for x in res[:40]: print(x[0], x[2], x[3], x[4], x[5], 'margin', x[6], x[7])
