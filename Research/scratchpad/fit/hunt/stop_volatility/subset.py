import sys, pickle
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from sig import raw
from engine2 import prepare
from tightdata import TRADES
D = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_volatility/'
r1 = pickle.load(open(D + 'feat.pkl', 'rb')); r2 = pickle.load(open(D + 'feat2.pkl', 'rb'))
out = []
for (t, f), (_, g) in zip(r1, r2):
    P = prepare(t['sym']); S = raw(P); i = t['arm_i']; d = t['d']; ds = i - P['sinceStart'][i]
    same = sum(1 for j in range(ds, i) if S[j] == d)
    h = dict(f); h.update(g); h['sameSigDay'] = same
    out.append((t, h))
pickle.dump(out, open(D + 'featall.pkl', 'wb'))
sub = [(t, h) for t, h in out if h['sameSigDay'] == 0]
print('subset', len(sub), 'tight', sum(t['tight'] for t, _ in sub))
pickle.dump(sub, open(D + 'featsub.pkl', 'wb'))
