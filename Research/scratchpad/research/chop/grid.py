"""TRAIN-only threshold grid, ghost mode. usage: grid.py k K  (worker k of K). Appends to grid_k.jsonl, skips done configs."""
import sys, json, os, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research/chop'); sys.path.insert(0, S + '/research')
import ev, chopfeat, lib
k, K = int(sys.argv[1]), int(sys.argv[2]); mode = sys.argv[3] if len(sys.argv) > 3 else 'ghost'
tn, _ = lib.split(ev.BASE)
names = [nm for nm in chopfeat.feats('GC') if not nm.endswith('_S')] + ['dE']
cfgs = []
for nm in names:
    if nm == 'dE': vals = sorted(x['dir'] * (x['entry'] - lib.prepare(x['sym'])['V'][x['arm']]) / x['atr'] for x in tn)
    else: vals = sorted(v for v in (chopfeat.get(x['sym'], nm, x['arm'], x['dir']) for x in tn) if v is not None)
    for pc in (5, 10, 15, 20, 25, 30, 40):
        hi = vals[int(len(vals) * (1 - pc / 100))]; lo = vals[int(len(vals) * pc / 100)]
        cfgs.append(dict(f=nm, side='hi', pc=pc, rules=[[nm, 'le', hi]]))   # veto the top pc%
        cfgs.append(dict(f=nm, side='lo', pc=pc, rules=[[nm, 'ge', lo]]))   # veto the bottom pc%
out = S + f'/research/chop/grid_{mode}_{k}.jsonl'
done = set()
if os.path.exists(out):
    for l in open(out): done.add(json.dumps(json.loads(l)['rules']))
with open(out, 'a') as fo:
    for j, c in enumerate(cfgs):
        if j % K != k or json.dumps(c['rules']) in done: continue
        r = ev.summary(ev.run({'chopRules': c['rules'], 'chopMode': mode}), ci=False); c.update(r); fo.write(json.dumps(c) + '\n'); fo.flush()
