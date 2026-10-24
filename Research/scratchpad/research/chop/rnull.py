"""random-gate null, ghost (or veto) mode: rnull.py k K mode keep1,keep2,..  seeds 0..249 -> rnull_<mode>_k.jsonl"""
import sys, json, os
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research/chop'); import ev
k, K, mode = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; keeps = [float(v) for v in sys.argv[4].split(',')]
out = S + f'/research/chop/rnull_{mode}_{k}.jsonl'; done = set()
if os.path.exists(out): done = set((json.loads(l)['keepP'], json.loads(l)['seed']) for l in open(out))
with open(out, 'a') as fo:
    j = 0
    for kp in keeps:
        for seed in range(250):
            j += 1
            if j % K != k or (kp, seed) in done: continue
            r = ev.summary(ev.run({'chopRand': [seed, kp], 'chopMode': mode}), ci=False); r.update(keepP=kp, seed=seed); fo.write(json.dumps(r) + '\n'); fo.flush()
