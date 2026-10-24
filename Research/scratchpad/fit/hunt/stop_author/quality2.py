"""quality-score rules (2-3 components, count of components beyond threshold >= k) -> tight; static on 80 trades."""
import itertools, pickle
Q = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/quality.pkl', 'rb'))
G = dict(body=[60, 70, 80, 90], clos=[5, 10, 15, 20], rngA=[1.0, 1.2, 1.5, 2.0], brk=[0.1, 0.25, 0.5, 1.0], mom=[1.5, 2, 3, 4],
         cv=[0.5, 1, 1.5, 2, 3], cvs=[0.5, 1, 1.5, 2], vsl=[0.1, 0.25, 0.5], adx=[20, 25, 30, 40], vr=[1, 1.5, 2, 3], bodyA=[0.5, 0.75, 1.0, 1.5])
best = []
for r in (1, 2, 3):
    for cs in itertools.combinations(list(G), r):
        opts = [[(th, s) for th in G[c] for s in (1, -1)] for c in cs]
        for ths in itertools.product(*opts):
            sc = [sum(1 for c, (th, s) in zip(cs, ths) if s * (q[c] - th) >= 0) for q in Q]
            for k in range(1, r + 1):
                tp = fp = 0
                for v, q in zip(sc, Q):
                    if v >= k:
                        if q['tight']: tp += 1
                        else: fp += 1
                best.append((8 - tp + fp, tp, fp, cs, ths, k))
best.sort(key=lambda x: (x[0], len(x[3])))
for b in best[:12]: print(b)
