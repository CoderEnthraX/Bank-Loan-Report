"""look-ahead check: recompute every chop feature on data truncated at the signal bar and compare."""
import sys, pickle, random, math
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research/chop'); import chopfeat
from engine2 import prepare
base = pickle.load(open(S + '/research/chop/base.pkl', 'rb')); rnd = random.Random(3); bad = 0; cnt = 0
for x in rnd.sample(base, 40):
    full = chopfeat.feats(x['sym']); P = prepare(x['sym']); c = x['arm'] + 1
    T = {k: (v[:c] if isinstance(v, list) and len(v) == len(P['C']) else v) for k, v in P.items()}
    chopfeat.prepare = lambda s, T=T: T; chopfeat._F.pop('TRUNC', None)
    tr = chopfeat.feats.__wrapped__('TRUNC') if hasattr(chopfeat.feats, '__wrapped__') else None
    chopfeat._F.pop('TRUNC', None); F2 = chopfeat.feats('TRUNC'); chopfeat._F.pop('TRUNC', None); chopfeat.prepare = prepare
    for k in full:
        a, b = full[k][x['arm']], F2[k][x['arm']]; cnt += 1
        if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-9): bad += 1; print('MISMATCH', x['sym'], x['arm'], k, a, b)
print('compared', cnt, 'feature values, mismatches', bad)
