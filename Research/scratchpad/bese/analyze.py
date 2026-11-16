"""Summary of bese/sweep.jsonl: per strategy the base (both triggers off), the best BE / salvage pair chosen on 2021-23 (raw best and the
neighbour-smoothed best: the pair whose 3 x 3 neighbourhood in the grid has the best average, so a lucky single cell is not picked), and
their 2024-26 test result; per timeframe the pair with the largest total gain over the catalogue strategies in 2021-23, read on 2024-26.
Output: bese/analysis.pkl + text on stdout."""
import json, pickle, sys
from collections import defaultdict
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
R = [json.loads(l) for l in open(S + '/bese/sweep.jsonl')]
by = defaultdict(dict)
for r in R: by[r['key']][(r['be'], r['sv'])] = r
BEv = sorted({k[0] for d in by.values() for k in d if k[0] is not None})
SVv = sorted({k[1] for d in by.values() for k in d if k[1] is not None})


def tot(r, per): return r[per]['net']


def smooth(d, k, per='in'):
    """average of the pair and its grid neighbours (off counts as the step before the smallest value)"""
    bl = [None] + BEv; sl = [None] + SVv
    i, j = bl.index(k[0]), sl.index(k[1]); vals = []
    for a in (i - 1, i, i + 1):
        for b in (j - 1, j, j + 1):
            if 0 <= a < len(bl) and 0 <= b < len(sl) and (bl[a], sl[b]) in d: vals.append(tot(d[(bl[a], sl[b])], per))
    return sum(vals) / len(vals)


def lab(k): return 'BE %s / salvage %s' % ('off' if k[0] is None else '%gR' % k[0], 'off' if k[1] is None else '%gR' % k[1])


out = dict(per={}, tf={})
print('%-18s %-30s %8s %8s | %-30s %8s %8s | %-30s %8s %8s' % ('strategy', 'base (both off)', '21-23', '24-26', 'best on 2021-23', '21-23', '24-26', 'smoothed best', '21-23', '24-26'))
for key in sorted(by, key=lambda k: (('M1', 'M5', 'M15', 'H1').index(k.split('-')[0]), k)):
    d = by[key]
    if (None, None) not in d: continue
    b = d[(None, None)]
    kb = max(d, key=lambda k: tot(d[k], 'in'))
    ks = max(d, key=lambda k: smooth(d, k))
    out['per'][key] = dict(base=b, best=(kb, d[kb]), smooth=(ks, d[ks]), grid=d)
    print('%-18s %-30s %+8.1f %+8.1f | %-30s %+8.1f %+8.1f | %-30s %+8.1f %+8.1f' % (key, 'n %d/%d' % (b['in']['n'], b['out']['n']), tot(b, 'in'), tot(b, 'out'),
          lab(kb), tot(d[kb], 'in'), tot(d[kb], 'out'), lab(ks), tot(d[ks], 'in'), tot(d[ks], 'out')))
print()
for tf in ('M1', 'M5', 'M15', 'H1'):
    for kind in ('catalogue', 'your settings'):
        keys = [k for k in by if k.startswith(tf + '-') and next(iter(by[k].values()))['kind'] == kind and (None, None) in by[k]]
        if not keys: continue
        common = set.intersection(*[set(by[k]) for k in keys])
        gain = {c: (sum(tot(by[k][c], 'in') - tot(by[k][(None, None)], 'in') for k in keys), sum(tot(by[k][c], 'out') - tot(by[k][(None, None)], 'out') for k in keys),
                    sum(1 for k in keys if tot(by[k][c], 'in') > tot(by[k][(None, None)], 'in') and tot(by[k][c], 'out') > tot(by[k][(None, None)], 'out'))) for c in common}
        best = max(gain, key=lambda c: gain[c][0])
        sd = sorted(by[k][(None, None)]['sdPct'] for k in keys)[len(keys) // 2]
        out['tf'][(tf, kind)] = dict(keys=keys, gain=gain, best=best, sdPct=sd)
        top = sorted(gain, key=lambda c: -gain[c][0])[:5]
        print('%s %s (%d strategies, median stop %.2f%% of price): best pair on 2021-23 %s: gain %+.1fR, 2024-26 %+.1fR, better in both halves %d/%d' % (
            tf, kind, len(keys), sd, lab(best), gain[best][0], gain[best][1], gain[best][2], len(keys)))
        for c in top[1:]: print('      next: %-30s %+.1fR | %+.1fR | both %d' % (lab(c), gain[c][0], gain[c][1], gain[c][2]))
pickle.dump(out, open(S + '/bese/analysis.pkl', 'wb'))
