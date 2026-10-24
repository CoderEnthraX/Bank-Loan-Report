"""TRAIN grid of 2-feature union vetoes (chop family), ghost mode -> grid3_k.jsonl"""
import sys, json, os, itertools
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research/chop'); sys.path.insert(0, S + '/research'); import ev, chopfeat, lib
k, K = int(sys.argv[1]), int(sys.argv[2]); tn, _ = lib.split(ev.BASE)
FS = {'xR2': 'hi', 'near1S': 'hi', 'rngRel': 'lo', 'rngS': 'lo'}
def thr(nm, pc):
    v = sorted(x for x in (chopfeat.get(t['sym'], nm, t['arm'], t['dir']) for t in tn) if x is not None)
    return [nm, 'le', v[int(len(v) * (1 - pc / 100))]] if FS[nm] == 'hi' else [nm, 'ge', v[int(len(v) * pc / 100)]]
cfgs = [dict(f=a + '+' + b, pc=(p, q), rules=[thr(a, p), thr(b, q)]) for a, b in itertools.combinations(FS, 2) for p in (10, 20, 30) for q in (10, 20, 30)]
out = S + f'/research/chop/grid3_{k}.jsonl'; done = set(json.dumps(json.loads(l)['rules']) for l in open(out)) if os.path.exists(out) else set()
with open(out, 'a') as fo:
    for j, c in enumerate(cfgs):
        if j % K != k or json.dumps(c['rules']) in done: continue
        r = ev.summary(ev.run({'chopRules': c['rules']}), ci=False); c.update(r); fo.write(json.dumps(c) + '\n'); fo.flush()
