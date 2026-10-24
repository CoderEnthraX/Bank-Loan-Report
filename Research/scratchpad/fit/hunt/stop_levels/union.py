"""Union-of-levels test: for natural zones, which features have 0 (or <=1) normals in the zone, and the union of tight trades they cover."""
import sys, pickle; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels/feat.pkl','rb'))
keys = sorted({k for _, x in rows for k in x if not any(k.startswith(p) for p in ('since','srange','adr','datr'))})
zones = {'stop18': (-1.8, 0), 'stop18o': (-1.8, -0.9), 'stop09': (-0.9, 0), 'tgt36': (0, 3.6), 'tgt36o': (1.8, 3.6), 'tgt18': (0, 1.8), 'stop27':(-2.7,0), 'tgt54':(0,5.4)}
for zn, (a, b) in zones.items():
    clean = []
    for k in keys:
        tp = {j for j, (t, x) in enumerate(rows) if t['tight'] and x.get(k) is not None and a < x[k] < b}
        fp = sum(1 for t, x in rows if not t['tight'] and x.get(k) is not None and a < x[k] < b)
        if fp <= 1 and tp: clean.append((k, fp, tp))
    cov0 = set().union(*[c[2] for c in clean if c[1] == 0]) if clean else set()
    cov1 = set().union(*[c[2] for c in clean]) if clean else set()
    print(zn, (a, b), 'clean feats:', [(k, fp, len(tp)) for k, fp, tp in clean], '\n    union(fp=0) covers', len(cov0), '/8; union(fp<=1)', len(cov1), '/8')
