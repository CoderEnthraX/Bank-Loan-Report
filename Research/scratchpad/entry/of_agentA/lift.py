"""hi-tercile minus lo-tercile excess per cell (train L, train S, valid L, valid S), for every feature, M5 and M15 side by side"""
import json, numpy as np, re
R = [json.loads(l) for l in open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA/rows.jsonl')]
R = [r for r in R if r['tag'] == 'terc']
K = ('train_long', 'train_short', 'valid_long', 'valid_short')
D = {}
for r in R:
    f = r['name'].split()[0]; side = 'hi' if '>=' in r['name'] else 'lo'
    D.setdefault((r['tf'], f), {})[side] = [r[k]['ex'] for k in K]
feats = sorted({f for (_, f) in D})
print('%-14s | %-30s | %-30s | same sign cells' % ('feature', 'M5 hi-lo trL trS vaL vaS', 'M15 hi-lo trL trS vaL vaS'))
for f in feats:
    row = []; allc = []
    for tf in ('M5', 'M15'):
        x = D.get((tf, f))
        if not x or 'hi' not in x or 'lo' not in x: row.append(' ' * 30); continue
        dd = np.array(x['hi']) - np.array(x['lo']); allc += list(dd); row.append(' '.join('%+6.2f' % v for v in dd) + '  ')
    a = np.array(allc); s = max((a > 0).sum(), (a < 0).sum())
    print('%-14s | %s | %s | %d/%d %s' % (f, row[0], row[1], s, len(a), '<==' if s == len(a) else ''))
