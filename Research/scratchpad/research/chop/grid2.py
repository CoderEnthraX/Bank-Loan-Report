"""TRAIN grid for chop-family features with the rule active only after m session bars (time-of-day control). -> grid2.jsonl"""
import sys, json, os
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research/chop'); sys.path.insert(0, S + '/research'); import ev, chopfeat, lib
k, K = int(sys.argv[1]), int(sys.argv[2])
tn, _ = lib.split(ev.BASE); cfgs = []
for nm, side in (('xR2', 'hi'), ('near05S', 'hi'), ('near1S', 'hi'), ('rngRel', 'lo'), ('rngRel5', 'lo'), ('rngS', 'lo'), ('near05_24', 'hi'), ('ov24', 'hi'), ('x24_2', 'hi'), ('bbwP', 'lo')):
    for m in (12, 24, 36):
        vals = sorted(v for v in (chopfeat.get(x['sym'], nm, x['arm'], x['dir']) for x in tn if chopfeat.get(x['sym'], 'vb', x['arm'], x['dir']) >= m) if v is not None)
        for pc in (10, 20, 30, 40):
            thr = vals[int(len(vals) * (1 - pc / 100))] if side == 'hi' else vals[int(len(vals) * pc / 100)]
            cfgs.append(dict(f=nm, side=side, m=m, pc=pc, rules=[[nm, 'le' if side == 'hi' else 'ge', thr]]))
out = S + f'/research/chop/grid2_{k}.jsonl'; done = set()
if os.path.exists(out): done = set(json.dumps([json.loads(l)['rules'], json.loads(l)['m']]) for l in open(out))
with open(out, 'a') as fo:
    for j, c in enumerate(cfgs):
        if j % K != k or json.dumps([c['rules'], c['m']]) in done: continue
        r = ev.summary(ev.run({'chopRules': c['rules'], 'chopMinBars': c['m']}), ci=False); c.update(r); fo.write(json.dumps(c) + '\n'); fo.flush()
