import sys, os
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from own_impl import *
from tightdata import TRADES
rng = np.random.default_rng(12345)
NET = 3
# per trade: first-impulse flag, session index, dist/A if tight, true label
rows = []
for t in TRADES:
    D = data(t['sym']); sg = impulses(D); net = sess_nets(D, sg); i = t['arm_i']; d = t['d']; k = D['sess'][i]
    first = not (sg[D['st'][k]:i] == d).any() and k > 0
    dA = stop_dist(D, i, d, t['entry'], True) / D['atr'][i]
    rows.append(dict(sym=t['sym'], k=k, d=d, first=first, tightDistOK=dA < 1.4, label=t['tight'], pn=net[k - 1] if k else 0, fill=t['fill']))
print('trades with first-impulse-of-session-in-direction:', sum(r['first'] for r in rows), 'of 80;  of those label tight:', sum(r['first'] and r['label'] for r in rows))
print('tight-labelled trades first-impulse:', [(r['sym'], r['fill'], r['first'], int(r['pn']), r['d']) for r in rows if r['label']])
print('first=True non-tight trades with d*pn<=-3 (false positives):', [(r['sym'], r['fill']) for r in rows if r['first'] and not r['label'] and r['d'] * r['pn'] <= -NET])
print('first=True non-tight trades: pn*d distribution', sorted([int(r['d'] * r['pn']) for r in rows if r['first'] and not r['label']]))
# session-level base rate
for s in SYMS:
    D = data(s); sg = impulses(D); net = sess_nets(D, sg)
    print(s, 'sessions', len(net), 'net:', net.tolist())
# 80-trade permutation: shuffle prevNet across sessions (k>=1) within each symbol
perms = 100000
sc = np.zeros(perms, int)
bysym = {}
for s in SYMS:
    D = data(s); sg = impulses(D); net = sess_nets(D, sg)
    bysym[s] = net
pnshuf = {}
for s in SYMS:
    net = bysym[s]; K = len(net)
    # session k uses net[k-1]; permute the vector net[0..K-2] (the prev-session values) across sessions 1..K-1
    pv = net[:K - 1]
    idx = np.argsort(rng.random((perms, K - 1)), axis=1)
    pnshuf[s] = pv[idx]  # perms x (K-1); column k-1 = prevNet of session k
correct = np.zeros(perms, int)
for r in rows:
    pn = pnshuf[r['sym']][:, r['k'] - 1] if r['k'] > 0 else np.zeros(perms, int)
    pred = r['first'] & (r['d'] * pn <= -NET) & r['tightDistOK']
    correct += (pred == r['label'])
obs = sum(((r['first'] and r['d'] * r['pn'] <= -NET and r['tightDistOK']) == r['label']) for r in rows)
print('observed', obs)
print('perm null (n=%d): mean %.2f  max %d  P(>=80)=%.5f  P(>=79)=%.5f  P(>=78)=%.5f  P(>=75)=%.5f' % (perms, correct.mean(), correct.max(), (correct >= 80).mean(), (correct >= 79).mean(), (correct >= 78).mean(), (correct >= 75).mean()))
print('first 1000 perms: P(>=79)=%.4f P(>=80)=%.4f max %d' % ((correct[:1000] >= 79).mean(), (correct[:1000] >= 80).mean(), correct[:1000].max()))
print('null score hist', np.bincount(correct).nonzero()[0].tolist()[-10:], np.bincount(correct)[np.bincount(correct).nonzero()[0]].tolist()[-10:])
# baseline "predict none tight": 72/80
print('constant "none tight" scores', sum(not r['label'] for r in rows), '/80')
# also count of the number of tight-eligible sessions per symbol (|pn|>=3 in either direction) 
