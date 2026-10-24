import sys, os, importlib.util
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from gtscore import load_gt, score
from collections import defaultdict
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
spec = importlib.util.spec_from_file_location('rule', os.path.join(FIT, 'hunt/stop_author/rule_counter_net.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tr, win = load_gt(os.path.join(FIT, '..', 'gt', 'final'))
def persym(fn):
    cfg = dict(BEST)
    if fn: cfg['stopFn'] = fn
    r, rows = score(cfg, tr, [dict(w) for w in win], detail=True)
    d = defaultdict(lambda: [0, 0, 0])
    for x in rows:
        if x[0] == 'ok': d[x[1]][0] += 1
        elif x[0] == 'MISS': d[x[1]][1] += 1
        elif x[0] == 'EXTRA': d[x[1]][2] += 1
        elif x[0] == 'nodata': pass
        else: d[x[1]][0] += 0
    return d, r
b, rb = persym(None); mod.NET = 3; mod.WICK = True; a, ra = persym(mod.stop_fn)
mod.WICK = False; c, rc = persym(mod.stop_fn); mod.WICK = True
print('sym   baseline(no rule) e/m/x   rule e/m/x   rule(close-break) e/m/x')
for s in sorted(set(b) | set(a)): print(f'{s:7s}', b[s], a[s], c[s])
print('tot baseline', rb['exact'], rb['miss'], rb['extra'], '| rule', ra['exact'], ra['miss'], ra['extra'], '| close-break', rc['exact'], rc['miss'], rc['extra'])
