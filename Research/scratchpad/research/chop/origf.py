"""How the causal chop filters treat the ORIGINAL indicator's trades (screenshots + student log), deduplicated."""
import sys, pickle, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); sys.path.insert(0, S + '/research/chop'); import lib, chopfeat, daytype
from engine2 import prepare
orig = pickle.load(open(S + '/research/chop/orig.pkl', 'rb')); base = pickle.load(open(S + '/research/chop/base.pkl', 'rb'))
FAM = {'NSE_NIFTY1': 'NIFTY'}
seen = {}; O = []
for o in orig:
    k = (FAM.get(o['sym'], o['sym']), o['t'], o['dir'])
    if k in seen:
        if seen[k]['res'] is None: seen[k]['res'] = o['res']
        continue
    seen[k] = o; O.append(o)
O = [o for o in O if o['res'] is not None]
nm = 0
for o in O:
    m = [x for x in base if x['sym'] == o['sym'] and x['dir'] == o['dir'] and abs(x['fill'] - o['i']) <= 1]
    o['sig'] = m[0]['arm'] if m else o['i'] - 1; nm += bool(m)
print('original trades with TP4/SL outcome after dedupe:', len(O), ' matched to a model signal bar:', nm, ' wins', sum(o['res'] > 0 for o in O))
RULES = {'F1 near1S<=0.525': [['near1S', 'le', 0.525]], 'F2 rngS>=6.97': [['rngS', 'ge', 6.97]], 'F4 xR2<=15.79&rngS>=5.99': [['xR2', 'le', 15.79], ['rngS', 'ge', 5.99]],
         'F5 xR2<=9.73': [['xR2', 'le', 9.73]], 'F5b xR2<=11.8': [['xR2', 'le', 11.8]], 'F6 xR2<=p10&rngRel>=p20': None}
import json, glob
G = [json.loads(l) for f in glob.glob(S + '/research/chop/grid3_*.jsonl') for l in open(f)]
RULES['F6 xR2<=p10&rngRel>=p20'] = [g for g in G if g['f'] == 'xR2+rngRel' and g['pc'] == [10, 20]][0]['rules']
def fails(o, rules):
    for n, op, t in rules:
        f = chopfeat.get(o['sym'], n, o['sig'], o['dir'])
        if f is not None and ((op == 'le' and f > t) or (op == 'ge' and f < t)): return True
    return False
W = [o for o in O if o['res'] > 0]; L = [o for o in O if o['res'] < 0]
print('rule                       winners vetoed   losers vetoed   E2 kept (n)    E2 vetoed (n)')
for name, r in RULES.items():
    vw = sum(fails(o, r) for o in W); vl = sum(fails(o, r) for o in L)
    k = [o for o in O if not fails(o, r)]; v = [o for o in O if fails(o, r)]
    E = lambda g: sum(o['res'] for o in g) / len(g) if g else float('nan')
    print(f"{name:26s} {vw:3d}/{len(W)} ({vw/len(W):.0%})    {vl:3d}/{len(L)} ({vl/len(L):.0%})    {E(k):+.3f} ({len(k)})   {E(v):+.3f} ({len(v)})")
print('all original', f"E2 {sum(o['res'] for o in O)/len(O):+.3f} TP4 rate {len(W)/len(O):.1%}")
# causal crossing-rate tercile (instrument terciles from the model's baseline trades) for originals
for nmf in ('xR2', 'near1S', 'rngS'):
    vals = sorted(chopfeat.get(x['sym'], nmf, x['arm'], x['dir']) for x in base); q1, q2 = vals[len(vals) // 3], vals[2 * len(vals) // 3]
    g = collections.defaultdict(list)
    for o in O:
        f = chopfeat.get(o['sym'], nmf, o['sig'], o['dir']); g['lo' if f < q1 else 'mid' if f < q2 else 'hi'].append(o['res'])
    print(f'original by causal {nmf} tercile (model cuts {q1:.3g}/{q2:.3g}):', ' '.join(f"{k}: n{len(v)} TP4 {sum(r>0 for r in v)/len(v):.0%} E2 {sum(v)/len(v):+.2f}" for k, v in sorted(g.items())))
# hindsight for the deduped set
g = collections.defaultdict(list)
for o in O:
    d = o['day']; ss = [x for x in daytype.sessions(o['sym'])[0] if x]; v = sorted(x['x2'] for x in ss); t = 'lo' if d['x2'] < v[len(v)//3] else 'mid' if d['x2'] < v[2*len(v)//3] else 'hi'
    g[t].append(o['res'])
print('original by HINDSIGHT day crossing tercile:', ' '.join(f"{k}: n{len(v)} TP4 {sum(r>0 for r in v)/len(v):.0%} E2 {sum(v)/len(v):+.2f}" for k, v in sorted(g.items())))
