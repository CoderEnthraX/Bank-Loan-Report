p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/build_final.py'; s=open(p).read()
R = [
("""    L = ['Auction Retest indicator on FxPro MT5 GOLD, 4 Jan 2021 - 2 Oct 2026 (your 1-minute data): accuracy, TP1-TP4, streaks, best settings, recovery rules', '',""",
 """    L = ['Auction Retest indicator on FxPro MT5 GOLD, 4 Jan 2021 - 2 Oct 2026 (your 1-minute data): profitable settings per goal, accuracy, TP1-TP4, streaks, recovery rules', '',
         'HOW TO USE THIS FILE:',
         '  1. Strategy guide: pick your goal (most profit, shortest losing streak, longest winning streak, highest win rate, most trades, every year positive, smoothest, simplest,',
         '     one session only) and your timeframe. Click the strategy to jump to its column.',
         '  2. <TF> strategies (M1, M5, M15, H1): one column per strategy. Every indicator input is listed with its exact name; yellow = change it to that value, grey = keep the default.',
         '     Below the settings: what to expect - trades, win %, TP1-TP4 reached, R per trade in each half and each year, longest winning and losing streaks, deepest fall, $ results.',
         '  3. All profitable settings: every setting that passed the profit rule, with a filter on each column (e.g. longest losing streak <= 6).',
         '  4. Recovery rules and Rule C split test: money management. The rest of the sheets are the research detail.', '',"""),
("""         'SHEETS: Best settings | Summary | <TF> default / best / low-streak (year x month) | TP1-TP4 | Settings sweep | Combinations | Exits | Recovery rules | Rule C split test | Robustness | Hours | Streak math']""",
 """         'SHEETS: Strategy guide | M1 / M5 / M15 / H1 strategies | All profitable settings | Recovery rules | Rule C split test | Summary | <TF> default / best / low-streak (year x month;',
         '  best = strategy S1 "Most profit", low-streak = the "Shortest losing streak" strategy) | TP1-TP4 | Settings sweep | Combinations | Exits | Robustness | Hours | Streak math']"""),
("""    best_sheet(wb, FIN, refs, rbest)
    order = ['Read me', 'Best settings', 'Summary'] + [s for _, _, s, _ in refs] + ['TP1-TP4', 'Settings sweep', 'Combinations', 'Exits', 'Recovery rules', 'Rule C split test', 'Robustness', 'Hours', 'Streak math']""",
 """    import strategy_sheets as SS
    CAT = SS.load()
    for tf in CAT:                       # the month sheets 'best' / 'low-streak' are the catalogue's Most profit / Shortest losing streak strategies
        names = {n: s['cfg'] for s in CAT[tf]['strategies'] for n, _ in s['scen']}
        assert names.get('Most profit') == FIN[tf]['cfg']['profit'] and names.get('Shortest losing streak') == FIN[tf]['cfg']['streak'], tf
    links = {tf: SS.tf_sheet(wb, tf, CAT[tf]) for tf in TFS if tf in CAT}
    SS.guide(wb, CAT, links); SS.allprof(wb, CAT)
    order = (['Read me', 'Strategy guide'] + ['%s strategies' % tf for tf in TFS] + ['All profitable settings', 'Recovery rules', 'Rule C split test', 'Summary'] +
             [s for _, _, s, _ in refs] + ['TP1-TP4', 'Settings sweep', 'Combinations', 'Exits', 'Robustness', 'Hours', 'Streak math'])""")]
for a, b in R:
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
open(p, 'w').write(s); print('ok')
