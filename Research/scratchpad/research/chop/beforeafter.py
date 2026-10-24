"""Is the loss on chop days caused by chop BEFORE the signal (knowable) or AFTER it (hindsight)? crosses rate per 100 bars before arm vs after exit/after arm."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); sys.path.insert(0, S + '/research/chop'); import lib, daytype, chopfeat
from engine2 import prepare
from engine import rma
tr = pickle.load(open(S + '/research/chop/base.pkl', 'rb'))
def xr(sym, a, b):
    P = prepare(sym); A = rma(P['tr'], 14); dev = [(P['C'][i] - P['V'][i]) / (A[i] or 1) for i in range(a, b + 1)]
    return daytype.crosses(dev, 0.2) / max(len(dev), 1) * 100
for x in tr:
    ss, sidx = daytype.sessions(x['sym']); d = ss[sidx[x['arm']]]
    x['vb'] = chopfeat.get(x['sym'], 'vb', x['arm'], x['dir'])
    x['before'] = chopfeat.get(x['sym'], 'xR2', x['arm'], x['dir'])
    x['after'] = xr(x['sym'], x['arm'] + 1, d['b']) if d and d['b'] > x['arm'] + 6 else None
def terc(g, k):
    g = [x for x in g if x[k] is not None]; g.sort(key=lambda x: x[k]); q = len(g) // 3
    return ' '.join(f"{n}:{sum(x['res'] for x in h)/len(h):+.3f}(n{len(h)})" for n, h in (('lo', g[:q]), ('mid', g[q:2*q]), ('hi', g[2*q:])))
for name, g in (('all trades', tr), ('trades from bar 24', [x for x in tr if x['vb'] >= 24])):
    print('==', name)
    print('  crossing rate BEFORE signal (causal) tercile  ', terc(g, 'before'))
    print('  crossing rate AFTER signal (hindsight) tercile', terc(g, 'after'))
    for part, h in zip(('TRAIN', 'TEST'), lib.split(g)): print('   ', part, 'before', terc(h, 'before'), '| after', terc(h, 'after'))
import statistics
g = [x for x in tr if x['after'] is not None and x['vb'] >= 24]
print('corr(before, after) crossing rate, trades from bar 24:', round(statistics.correlation([x['before'] for x in g], [x['after'] for x in g]), 3))
