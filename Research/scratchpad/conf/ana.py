import pickle, sys
R = pickle.load(open('results.pkl', 'rb'))
def f(s): return '%5d %4.0f%% %+7.1f %+7.1f dd%5.1f run%3d d%.2f' % (s['all']['n'], 100 * s['all']['win'], s['in']['net'], s['out']['net'], s['all']['dd'], s['all']['lrun'], s['all']['medDist'])
def vn(r): return 'K%d %-7s stop@%-6s tgt %-4s min%.2f' % (r['K'], r['delta'], r['stop'], r['tgt'], r['minStop'])
for b in R:
    print('\n=== %s   normal: %s' % (b['key'], f(b['normal'])))
    print('   [n  win%  net21-23 net24-26 dd(R) lossrun medStop$]')
    rows = b['rows']
    # the user's literal rule: stop at entry, delta clv+vol, each target, K3, min 0 / 0.15 / 0.3
    print('  -- your rule (K3, delta clv+vol, stop at the entry), mode A = every setup:')
    for r in rows:
        if r['K'] == 3 and r['delta'] == 'clv+vol' and r['stop'] == 'entry': print('    ', vn(r), f(r['A']))
    best = sorted(rows, key=lambda r: -r['A']['in']['net'])[:3]
    print('  -- best mode A by 2021-23:'); [print('    ', vn(r), f(r['A'])) for r in best]
    best = sorted(rows, key=lambda r: -r['B']['in']['net'])[:3]
    print('  -- best mode B (normal, confirm after a loss) by 2021-23: whole B | its confirmation trades:')
    for r in best: print('    ', vn(r), f(r['B']), '|', f(r['Bc']))
    pos = sum(1 for r in rows if r['A']['in']['net'] > 0 and r['A']['out']['net'] > 0)
    print('  -- variants positive in both halves (mode A): %d of %d' % (pos, len(rows)))
