import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
from sig import raw
rows, out = table(True)
for t, f in rows:
    if not f: continue
    s = t['sym']; i = t['arm_i']; d = t['d']; P = prepare(s); S = raw(P)
    cl = [x for x in out[s] if x['exit'] is not None and x['exit'] <= i]
    ss = [x for x in cl if x['dir'] == d]; oo = [x for x in cl if x['dir'] == -d]
    keep = {}
    keep['sRes'] = ss[-1]['res'] if ss else 0; keep['oRes'] = oo[-1]['res'] if oo else 0
    keep['sGap'] = i - ss[-1]['exit'] if ss else 9999; keep['oGap'] = i - oo[-1]['exit'] if oo else 9999
    keep['sRes2'] = sum(x['res'] for x in ss[-2:]); keep['oRes2'] = sum(x['res'] for x in oo[-2:])
    keep['sTight'] = int(bool(ss) and ss[-1]['dir'] * (ss[-1]['entry'] - ss[-1]['stop']) / P[('atr',14)][ss[-1]['arm']] < 1.4)
    ds = i - P['sinceStart'][i]
    keep['fd'] = int(not any(S[j] == d for j in range(ds, i)))
    keep['sToday'] = sum(1 for x in ss if x['fill'] >= ds); keep['oToday'] = sum(1 for x in oo if x['fill'] >= ds)
    f.clear(); f.update(keep)
res, n = sep(rows)
seen = set()
for r in res:
    if r[2] in seen: continue
    seen.add(r[2]); print(r)
# conjunction with fd
sub = [(t, f) for t, f in rows if f and f['fd']]
print('fd subset', len(sub))
res, n = sep(sub)
seen = set()
for r in res:
    if r[2] in seen: continue
    seen.add(r[2]); print(' fd&', r)
