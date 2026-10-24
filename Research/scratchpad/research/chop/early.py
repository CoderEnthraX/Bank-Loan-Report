"""Can a chop day be recognised at bar m of the session? AUC of causal session-so-far features vs the HINDSIGHT label
(label A: final VWAP-cross count (0.2 ATR hyst) in the top tercile of the instrument; label B: composite RANGE day from desc.py)."""
import sys
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); sys.path.insert(0, S + '/research/chop'); import lib, daytype, chopfeat
def auc(pos, neg):
    if not pos or not neg: return float('nan')
    s = 0.0
    for p in pos:
        for q in neg: s += 1 if p > q else 0.5 if p == q else 0
    return s / len(pos) / len(neg)
rows = []
for sym in lib.SYMS:
    ss, _ = daytype.sessions(sym); ds = [d for d in ss if d and not d['first']]
    v = sorted(d['x2'] for d in ds); q2 = v[2 * len(v) // 3]; v1 = v[len(v) // 3]
    for d in ds:
        d['labA'] = d['x2'] >= q2
        d['labB'] = d['eff'] < 0.35 and d['x2'] >= v1
        d['sym'] = sym; rows.append(d)
F = ['xR2', 'xS2', 'near05S', 'near1S', 'rngS', 'rngRel', 'rngRel5', 'effS', 'pX2r', 'pNear']
SIGN = {'rngS': -1, 'rngRel': -1, 'rngRel5': -1, 'effS': -1}     # low value = chop
print('sessions', len(rows), 'labelA share', round(sum(r['labA'] for r in rows) / len(rows), 2), 'labelB share', round(sum(r['labB'] for r in rows) / len(rows), 2))
for lab in ('labA', 'labB'):
    print('==', lab, 'AUC (0.5 = no skill) by session bar m (5-min bars)')
    ms = (6, 12, 24, 36, 48, 72, 96)
    print('feature   ' + ' '.join('m=%-4d' % m for m in ms))
    for f in F:
        out = []
        for m in ms:
            pos = []; neg = []
            for r in rows:
                if r['nb'] < m + 6: continue
                x = chopfeat.feats(r['sym'])[f][r['a'] + m - 1]
                if x is None: continue
                x *= SIGN.get(f, 1); (pos if r[lab] else neg).append(x)
            out.append(auc(pos, neg))
        print(f'{f:9s} ' + ' '.join('%.3f ' % a for a in out))
