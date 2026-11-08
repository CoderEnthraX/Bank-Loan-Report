import json, numpy as np, sys
rows = [json.loads(l) for l in open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB/rows.jsonl')]
seen = {}
for r in rows: seen[(r['name'], r['tf'])] = r
rows = list(seen.values())
def z(r):
    num = 0; den = 0
    for k in ('tl', 'ts', 'vl', 'vs'):
        n = r.get(k + '_n', 0)
        if n: num += r[k + '_avgex'] * n; den += n
    return (num / den) / (50 / np.sqrt(den)) if den else np.nan
a4 = [r for r in rows if all(r.get(k + '_n', 0) > 0 and r[k + '_avgex'] > 0 for k in ('tl', 'ts', 'vl', 'vs'))]
zs = np.array([z(r) for r in rows])
print('variants', len(rows), 'all4>0', len(a4), 'expected ~', round(len(rows) / 16, 1), 'pooled z mean %.2f sd %.2f max %.2f' % (np.nanmean(zs), np.nanstd(zs), np.nanmax(zs)))
mn = {'M15': 8, 'M5': 20, 'H1': 3, 'M1': 40}
for r in sorted(a4, key=z, reverse=True):
    pm = r.get('tl_pm', 0) + r.get('ts_pm', 0)
    pl = all(r.get(k + '_avgpl', -1) > 0 for k in ('tl', 'ts', 'vl', 'vs'))
    print('%-42s %-3s pm %6.1f%s z %.2f | %+5.1f %+5.1f %+5.1f %+5.1f | pl %+5.1f %+5.1f %+5.1f %+5.1f %s' % (r['name'][:42], r['tf'], pm, '' if pm >= mn[r['tf']] else '*', z(r),
          r['tl_avgex'], r['ts_avgex'], r['vl_avgex'], r['vs_avgex'], r['tl_avgpl'], r['ts_avgpl'], r['vl_avgpl'], r['vs_avgpl'], 'PL4' if pl else ''))
