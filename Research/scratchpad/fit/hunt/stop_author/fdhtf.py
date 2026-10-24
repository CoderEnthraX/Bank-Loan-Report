"""first-of-session-in-dir (sibling event def) AND HTF-against-d (various), on all 80."""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
import importlib.util
spec = importlib.util.spec_from_file_location('fdp', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/rule_firstday_prevday.py'); fdp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fdp)
from tightdata import TRADES
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/tfeat.pkl', 'rb'))
for r, t in zip(rows, TRADES):
    P = get(t['sym']); out, idx = fdp._daily(P); k = idx[t['arm_i']]; a = out[k][0]
    r['first'] = not any(fdp._event(P, j, t['d']) for j in range(a, t['arm_i']))
    po, pc = out[k-1][2], out[k-1][3]; r['pdb'] = t['d'] * (pc - po) / P[('atr', 14)][t['arm_i']]
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/tfeat.pkl', 'wb'))
F = [r for r in rows if r['first']]
print('first: n', len(F), 'tight', sum(r['tight'] for r in F))
keys = [k for k in rows[0] if k not in ('sym', 'fill', 'd', 'tight', 'pos', 'pos0', 'first')]
res = []
for k in keys:
    vals = [r[k] for r in F if r.get(k) is not None]
    for th in sorted(set(vals)):
        for side in (1, -1):
            tp = sum(1 for r in F if r.get(k) is not None and side * (r[k] - th) >= 0 and r['tight'])
            fp = sum(1 for r in F if r.get(k) is not None and side * (r[k] - th) >= 0 and not r['tight'])
            if tp == 8: res.append((fp, k, side, th))
best = {}
for fp, k, side, th in res:
    if k not in best or fp < best[k][0]: best[k] = (fp, side, th)
for k, v in sorted(best.items(), key=lambda x: x[1][0])[:25]:
    # margin: nearest normal beyond th
    fp, side, th = v
    nxt = sorted([side * (r[k] - th) for r in F if r.get(k) is not None and not r['tight'] and side * (r[k] - th) < 0], reverse=True)[:1]
    print(f"first & {k} {'>=' if side>0 else '<='} {th:.3f}: 8T {fp}FP  (nearest excluded normal at {nxt})")
