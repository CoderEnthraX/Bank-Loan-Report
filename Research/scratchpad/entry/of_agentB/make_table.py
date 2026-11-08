import json, numpy as np
D = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB'
rows = [json.loads(l) for l in open(D + '/rows.jsonl')]
seen = {}
for r in rows: seen[(r['name'], r['tf'])] = r
rows = list(seen.values())
MN = {'M15': 8, 'M5': 20, 'H1': 3, 'M1': 40}
def z(r):
    num = den = 0
    for k in ('tl', 'ts', 'vl', 'vs'):
        n = r.get(k + '_n', 0)
        if n: num += r[k + '_avgex'] * n; den += n
    return (num / den) / (50 / np.sqrt(den)) if den else np.nan
out = ['| # | family | variant | TF | n/mo (train) | train L | train S | valid L | valid S | placebo-adj train L/S | placebo-adj valid L/S | verdict |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
na = 0
for q, r in enumerate(rows, 1):
    g = lambda k, f: r.get(k + '_' + f, float('nan'))
    pm = g('tl', 'pm') + g('ts', 'pm')
    a4 = all(r.get(k + '_n', 0) > 0 and r[k + '_avgex'] > 0 for k in ('tl', 'ts', 'vl', 'vs'))
    na += a4
    v = ('all 4 > 0, pooled z %.1f' % z(r)) if a4 else 'FAIL'
    if pm < MN[r['tf']]: v += ' ; few trades'
    if (r['name'], r['tf']) in {('C3 p80 declust12 mkt', 'M5'), ('C3gen impulse bar 0.8ATR away p80 OPP mkt', 'M5'), ('C3gen impulse bar 0.8ATR away p80 OPP mkt', 'M15')} and a4: v = '**' + v + ' (candidate)**'
    out.append('| %d | %s | %s | %s | %.1f | %+.1f | %+.1f | %+.1f | %+.1f | %+.1f / %+.1f | %+.1f / %+.1f | %s |' % (
        q, r['family'], r['name'], r['tf'], pm, g('tl', 'avgex'), g('ts', 'avgex'), g('vl', 'avgex'), g('vs', 'avgex'),
        g('tl', 'avgpl'), g('ts', 'avgpl'), g('vl', 'avgpl'), g('vs', 'avgpl'), v))
zs = np.array([z(r) for r in rows])
open(D + '/table.md', 'w').write('\n'.join(out) + '\n')
print(len(rows), 'variants; all4>0', na, 'expected', len(rows) / 16, 'z mean %.2f sd %.2f max %.2f; z>3: %d' % (np.nanmean(zs), np.nanstd(zs), np.nanmax(zs), (zs > 3).sum()))
print([ (r['name'], r['tf'], round(z(r),1)) for r in rows if z(r) > 3])
