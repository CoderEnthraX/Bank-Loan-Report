p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/strategy_sheets.py'; s=open(p).read()
R = [("        put(ws, r, 2, lab, bold=True)\n        for k, s in enumerate(st): put(ws, r, k0 + k, fn(s), bold=(lab == 'Scenario'), wrap=True)",
      "        put(ws, r, 2, lab, bold=True, wrap=True)\n        for k, s in enumerate(st): put(ws, r, k0 + k, fn(s), bold=(lab == 'Scenario'), wrap=True)"),
     ("""    cols = ['Strategy', 'Timeframe', 'Goal(s)', 'Works in', 'Settings to change (indicator names)', 'Trades per day', 'Profitable trades %', 'TP1 reached %',
            'R per trade 2021-23', 'R per trade 2024-26', 'R per trade 2021-2026', 'Years positive', 'Longest winning streak', 'Longest losing streak',
            'Deepest fall (R)', 'Fixed $50: net ($)', 'Rule C split 3, $500 cap, Start again: net ($)', '... its deepest fall %']""",
      """    cols = ['Strategy', 'Timeframe', 'Goal(s)', 'Works in', 'Trades per day', 'Profitable trades %', 'TP1 reached %',
            'R per trade 2021-23', 'R per trade 2024-26', 'R per trade 2021-2026', 'Years positive', 'Longest winning streak', 'Longest losing streak',
            'Deepest fall (R)', 'Fixed $50: net ($)', 'Rule C split 3, $500 cap, Start again: net ($)', '... its deepest fall %', 'Settings to change (indicator names)']"""),
     ("""            vals = [sid(tf, k), tf, ' + '.join(n for n, _ in s['scen']), works(s['cfg']), labels.short(s['cfg']), round(x['perday'], 3), round(x['prof'], 4), round(x['tp'][0], 4),
                    round(x['EA'], 4), round(x['EB'], 4), round(x['E'], 4), x['ypos'], x['maxW'], x['maxL'], round(x['ddR'], 2), round(s['money']['off']['net'], 2),
                    'BLOWN' if rs['ruined'] else round(rs['net'], 2), round(rs['maxDDpct'], 4)]
            for j, v in enumerate(vals, 1):
                c = put(ws, r, j, v, '0.00' if j == 6 else '0.0%' if j in (7, 8, 18) else '0.000' if j in (9, 10, 11) else '0.0' if j == 15 else '#,##0;(#,##0);-' if j in (16, 17) else None,
                        j == 1, BLUE if j >= 6 else None, wrap=(j in (3, 5)))""",
      """            vals = [sid(tf, k), tf, ' + '.join(n for n, _ in s['scen']), works(s['cfg']), round(x['perday'], 3), round(x['prof'], 4), round(x['tp'][0], 4),
                    round(x['EA'], 4), round(x['EB'], 4), round(x['E'], 4), x['ypos'], x['maxW'], x['maxL'], round(x['ddR'], 2), round(s['money']['off']['net'], 2),
                    'BLOWN' if rs['ruined'] else round(rs['net'], 2), round(rs['maxDDpct'], 4), labels.short(s['cfg'])]
            for j, v in enumerate(vals, 1):
                c = put(ws, r, j, v, '0.00' if j == 5 else '0.0%' if j in (6, 7, 17) else '0.000' if j in (8, 9, 10) else '0.0' if j == 14 else '#,##0;(#,##0);-' if j in (15, 16) else None,
                        j == 1, BLUE if 5 <= j <= 17 else None, wrap=(j in (3, 4, 18)))"""),
     ("    widths(ws, [30, 30, 30, 30, 60, 8, 9, 8, 9, 9, 9, 8, 9, 9, 8, 10, 12, 9]); ws.freeze_panes = 'B6'",
      "    widths(ws, [34, 26, 26, 26, 26, 9, 8, 9, 9, 9, 8, 9, 9, 8, 10, 12, 9, 90]); ws.freeze_panes = 'B6'")]
for a, b in R:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w').write(s); print('ok')
