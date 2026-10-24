import sys, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare
from tightdata import TRADES
from nearsig import conds
from bias import daily, dayidx
CORE = ('dir', 'rng', 'body', 'clos', 'brk')
OPT = ('vw', 'mom', 'vsl', 'first', 'sun')
cache = {}
def ev_ok(P, j, d, inc):
    key = (P['sym'], j, d)
    if key not in cache: cache[key] = conds(P, j, d)
    r = cache[key]
    if not r: return False
    for k in CORE:
        if not r[k]: return False
    for k in ('vw', 'mom', 'vsl', 'first'):
        if k in inc and not r[k]: return False
    if 'sun' in inc and P['dowutc'][j] == 6: return False
    return True
if __name__ == '__main__':
    res = []
    for n in range(len(OPT) + 1):
        for inc in itertools.combinations(OPT, n):
            for pdk in ('body', 'pd2'):
                tp = fp = 0; fps = []
                for t in TRADES:
                    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; ds = i - P['sinceStart'][i]
                    Dd = daily(P); k = dayidx(P, i); pd = Dd[k - 1]
                    pv = (pd['c'] - pd['o']) if pdk == 'body' else (pd['c'] - Dd[k - 2]['c'])
                    if d * pv >= 0: continue
                    if any(ev_ok(P, j, d, inc) for j in range(ds, i)): continue
                    if t['tight']: tp += 1
                    else: fp += 1; fps.append(f"{t['sym']} {t['fill'][5:]}")
                res.append((8 - tp + fp, tp, fp, inc, pdk, fps))
    res.sort(key=lambda x: (x[0], len(x[3])))
    for r in res[:25]: print(r)
