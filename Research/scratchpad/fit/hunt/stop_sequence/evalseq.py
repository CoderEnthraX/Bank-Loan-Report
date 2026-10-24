"""Usage: python3 -I evalseq.py rule.py -> teacher-forced stop classification (ctx = oracle-tight full-engine history at each GT arm)
and in-engine stop classification of the exactly-matched trades of the rule's own full-engine run."""
import sys, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from rec import *
spec = importlib.util.spec_from_file_location('rule', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
runall(True)
ok = 0; bad = []; n = 0
for t in TRADES:
    s = t['sym']; P = prepare(s); A = P[('atr', 14)][t['arm_i']]
    recs = [r for r in REC[s] if r[0] == t['arm_i'] and r[1] == t['d']]
    if not recs: continue
    n += 1; ctx = recs[-1][2]
    st = mod.stop_fn(P, t['arm_i'], t['d'], t['entry'], t['entry'] - t['d'] * 1.8 * A, A, ctx)
    pt = t['d'] * (t['entry'] - st) / A < 1.4
    if pt == t['tight']: ok += 1
    else: bad.append(f"{s} {t['fill']} {'TIGHT' if t['tight'] else 'normal'}")
print(f'TEACHER-FORCED {ok}/{n} wrong({len(bad)}): {bad}')
# in-engine: run rule, check matched trades' stop type
cfg = dict(BEST); cfg['stopFn'] = mod.stop_fn
ok2 = 0; n2 = 0; bad2 = []
for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P = prepare(s); tr = run(P, cfg); A = P[('atr', 14)]
    byfill = {(x['fill'], x['dir']): x for x in tr}
    for t in [t for t in TRADES if t['sym'] == s]:
        x = byfill.get((t['fill_i'], t['d']))
        if not x: continue
        n2 += 1; pt = x['dir'] * (x['entry'] - x['stop']) / A[x['arm']] < 1.4
        if pt == t['tight']: ok2 += 1
        else: bad2.append(f"{s} {t['fill']} {'TIGHT' if t['tight'] else 'normal'}")
print(f'IN-ENGINE (exact-fill matches) {ok2}/{n2} wrong({len(bad2)}): {bad2}')
