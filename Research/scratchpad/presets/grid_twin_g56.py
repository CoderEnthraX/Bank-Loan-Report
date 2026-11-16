"""G5 / G6 (no recovery): the twin with a large start balance (no account can be blown) vs the study's trades at a fixed $10 (no ruin), per month."""
import sys, pickle, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/presets')
import grid_twin_months as GT, preset_data as PD
D = pickle.load(open(S + '/mcej3/sets.pkl', 'rb'))
for g in PD.GRID_PRESETS[4:]:
    tw = GT.months_twin(g, start_total=1e9 * len(g['strats']))
    rs = {}
    for sid in g['strats']:
        for x in D['grid'][sid - 1]['trades']:
            m = x['t'].strftime('%Y-%m'); rs[m] = rs.get(m, 0.0) + 10.0 * (x['R'] - x['c']) / (1.0 + x['c'])
    ms = sorted(set(tw) | set(rs)); d = max(abs(tw.get(m, 0) - rs.get(m, 0)) for m in ms if m <= '2026-10')
    a = sum(v for m, v in tw.items() if '2021' <= m < '2024'); b = sum(v for m, v in rs.items() if '2021' <= m < '2024')
    print(g['key'], 'months', len(ms), 'max month diff $%.4f' % d, '| 2021-23 twin %+.0f study-trades %+.0f' % (a, b), flush=True)
