import sys
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/presets'); sys.path.insert(0, S + '/mcej3'); sys.path.insert(0, S + '/gold')
import preset_data as PD, robust as RB, search as SE
print('| Preset | Strategies | Money | 2021-23: losing / profitable months | total | worst month | deepest drop | 2024-26: losing / profitable months | total | worst month | deepest drop |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for g in PD.GRID_PRESETS:
    ri = [r[0] for r in SE.RULES].index('Exact recovery at final TP' if g['rec'] == 'EXACT' else 'No recovery')
    cap = 0.0 if g['cap'] is None else g['cap']
    ci = [i for i, c in enumerate(SE.CAPS) if c[1] == cap and (cap == 0 or c[2] == g['act'])][0]
    res = RB.run_grid([sid - 1 for sid in g['strats']], SE.RUNS.index((g['base'], ri, ci)), 'cal', None)
    row = []
    for per in ('IN', 'OUT'):
        v = [r for r, w in zip(res, RB.WIN['cal']) if w[2] == per]
        nets = [r[0] for r in v]
        row += ['%d / %d' % (sum(x < -1e-9 for x in nets), sum(x > 1e-9 for x in nets)), '%+.0f' % sum(nets), '%+.0f' % min(nets), '%.0f' % max(r[1] for r in v)]
    money = '$%g fixed, %s%s' % (g['base'], 'exact recovery' if g['rec'] == 'EXACT' else 'no recovery', ', cap $%g %s' % (g['cap'], 'Clamp' if g['act'] == 'clamp' else 'Start again') if g['cap'] else '')
    print('| %s | %s | %s | %s |' % (g['name'].split(':')[0] + ' (' + g['key'] + ')', ', '.join('S%d' % i for i in g['strats']) if len(g['strats']) < 12 else 'all 12', money, ' | '.join(row)))
