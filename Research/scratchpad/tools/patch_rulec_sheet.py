p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/build_final.py'; s=open(p).read()
a = """# ---------------------------------------------------------------- robustness (neighbourhood of each pick)"""
b = '''# ---------------------------------------------------------------- Rule C and Rule C split with the loss split over 1-5 trades
def rulec_sheet(wb):
    fn = S + '/gold/rulec.pkl'
    if not os.path.exists(fn): return
    D = pickle.load(open(fn, 'rb'))['rows']
    ws = wb.create_sheet('Rule C split test')
    title(ws, 'Rule C and Rule C split with the loss split over 1, 2, 3, 4 or 5 trades (2021-2026, after spread)',
          'Rule C: carried = how far closed equity is below its last high; next risk = max(base, carried / split). Rule C split: the same, and the base steps up with total profit '
          '(200 -> 200/3, 500 -> 500/5, 1000 -> 1000/8, then +1 part per +500). $10,000 start, $50 base, hard cap $500 with Clamp unless shown. Partial closes update the carried losses per part.')
    ws.merge_cells('A2:Q2'); ws['A2'].alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[2].height = 40
    notes = ['WHAT IT SHOWS',
             '1. With the best settings (profitable signals) and the hard cap on, Rule C split at split 2 or 3 made 5-9x the profit of fixed risk (Off), and per $ staked it lost about the same as Off.',
             '2. Without the hard cap, Rule C split at split 1-3 blew the $10,000 account on M1, M5 and M15. With the default settings every Rule C variant blew the account.',
             '3. Split 3 was the better choice than 2 on most cases: similar profit with a smaller drawdown (M15 best: 33% vs 46%). Drawdowns are still far larger than Off (16-70% vs 3-17%).',
             '4. The cap action matters: "Start again" (forget the carried losses when the risk would pass the cap) kept M5 alive where Clamp blew it, and gave M15 its best profit for the drawdown.',
             '5. Stress test (part 3): add 0.05-0.10 R of extra cost per trade (live slippage, weaker edge). H1 stays clearly profitable; M15 holds to about 0.05 R; M1 and M5 blow up - their edge is too thin.']
    r = 4
    for k, t in enumerate(notes): ws.cell(r + k, 1, t).font = font(bold=(k == 0), size=9)
    r += len(notes) + 1
    put(ws, r, 1, 'PART 1 - split 1 to 5, without and with the $500 hard cap (Clamp)', bold=True, fill=SUB); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10); r += 1
    cols = ['Timeframe', 'Settings', 'Rule', 'Split', 'Hard cap', 'Net profit ($)', 'Max drawdown ($)', 'Max drawdown %', 'Average stake ($)', 'Largest stake ($)', 'Account blown?',
            'Profit / max drawdown', 'vs Off (1 = same)', 'Profit per $ of average stake', 'Max drawdown per $ of average stake', '2021-23 alone: net ($)', '2024-26 alone: net ($)']
    hdr(ws, r, cols, height=54); r += 1
    for tf in TFS:
        for prof, _ in PROF:
            if (tf, prof) not in D: continue
            offrow = None
            for x in D[(tf, prof)]:
                a, A, B = x['all'], x['A'], x['B']; off = x['mode'] == 'Off'
                rule = 'Off (fixed $50)' if off else ('Rule C' if x['mode'].startswith('Rule C:') else 'Rule C split')
                if off: offrow = r
                fl = TOT if off else (BAD if a['ruined'] else None)
                vals = [tf, PNAME[prof], rule, '-' if off else x['split'], '-' if off else ('$500' if x['cap'] else 'none'), round(a['net'], 2), round(a['maxDD'], 2), round(a['maxDDpct'], 4),
                        round(a['avgRisk'], 2), round(a['maxRisk'], 2), ('YES, after %d trades' % a['ruinAt']) if a['ruined'] else 'no',
                        '=IF(G{0}=0,"",F{0}/G{0})', '=IF(OR(L{1}="",L{1}<=0,L{0}=""),"",L{0}/L{1})' if offrow and not off else ('1' if off else ''),
                        '=IF(I{0}=0,"",F{0}/I{0})', '=IF(I{0}=0,"",G{0}/I{0})',
                        'BLOWN' if A['ruined'] else round(A['net'], 2), 'BLOWN' if B['ruined'] else round(B['net'], 2)]
                for j, v in enumerate(vals, 1):
                    isf = isinstance(v, str) and v.startswith('=')
                    put(ws, r, j, v.format(r, offrow) if isf else (1 if v == '1' else v),
                        '#,##0;(#,##0);-' if j in (6, 7, 9, 10, 16, 17) else '0.0%' if j == 8 else '0.00' if j in (12, 13) else '0.0' if j in (14, 15) else None,
                        off, BLUE if (6 <= j <= 10 or j in (16, 17)) and not isf else None, fl)
                r += 1
            r += 1
    fc = S + '/gold/rulec_caps.pkl'
    if os.path.exists(fc):
        C = pickle.load(open(fc, 'rb'))
        r += 1; put(ws, r, 1, 'PART 2 - split 2 and 3: hard cap size and what happens when the risk would pass it (Clamp = trade at the cap, Start again = forget the carried losses)',
                     bold=True, fill=SUB); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12); r += 1
        hdr(ws, r, ['Timeframe', 'Settings', 'Rule', 'Split', 'Hard cap', 'If the risk would pass the cap', 'Net profit ($)', 'Max drawdown ($)', 'Max drawdown %', 'Account blown?',
                    'Profit / max drawdown'], height=42); r += 1
        for (tf, prof), rows in C.items():
            for x in rows:
                q = x['r']; fl = BAD if q['ruined'] else None
                vals = [tf, PNAME[prof], 'Rule C' if x['mode'].startswith('Rule C:') else 'Rule C split', x['split'], '$%d' % x['cap'], 'Clamp' if x['act'] == 'clamp' else 'Start again',
                        round(q['net'], 2), round(q['maxDD'], 2), round(q['maxDDpct'], 4), 'YES' if q['ruined'] else 'no', '=IF(H{0}=0,"",G{0}/H{0})']
                for j, v in enumerate(vals, 1):
                    isf = isinstance(v, str) and v.startswith('=')
                    put(ws, r, j, v.format(r) if isf else v, '#,##0;(#,##0);-' if j in (7, 8) else '0.0%' if j == 9 else '0.00' if j == 11 else None, False,
                        BLUE if 7 <= j <= 9 else None, fl)
                r += 1
            r += 1
    fs = S + '/gold/rulec_stress.pkl'
    if os.path.exists(fs):
        T = pickle.load(open(fs, 'rb'))
        r += 1; put(ws, r, 1, 'PART 3 - stress test on the best settings: the same runs with 0.05 R and 0.10 R of extra cost on every trade (slippage, a weaker live edge)',
                     bold=True, fill=SUB); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12); r += 1
        hdr(ws, r, ['Timeframe', 'Rule', 'Split', 'Hard cap / action', 'Net ($), as tested', 'Max DD %, as tested', 'Net ($), +0.05 R cost', 'Max DD %, +0.05 R', 'Net ($), +0.10 R cost',
                    'Max DD %, +0.10 R'], height=42); r += 1
        keys = sorted({k[2:] for k in T}, key=lambda k: (k[0] != 'Off', k[0], k[1], k[3]))
        for tf in TFS:
            for mode, split, cap, act in keys:
                if (tf, 0.0, mode, split, cap, act) not in T: continue
                vals = [tf, 'Off (fixed $50)' if mode == 'Off' else ('Rule C' if mode.startswith('Rule C:') else 'Rule C split'), '-' if mode == 'Off' else split,
                        '-' if not cap else '$%d %s' % (cap, 'Clamp' if act == 'clamp' else 'Start again')]
                for extra in (0.0, 0.05, 0.10):
                    q = T[(tf, extra, mode, split, cap, act)]
                    vals += ['BLOWN' if q['ruined'] else round(q['net'], 2), round(q['maxDDpct'], 4)]
                for j, v in enumerate(vals, 1):
                    put(ws, r, j, v, '#,##0;(#,##0);-' if j in (5, 7, 9) else '0.0%' if j in (6, 8, 10) else None, mode == 'Off', BLUE if j >= 5 else None,
                        TOT if mode == 'Off' else (BAD if v == 'BLOWN' else None))
                r += 1
            r += 1
    widths(ws, [9, 30, 14, 6, 9, 11, 11, 9, 9, 9, 16, 9, 9, 9, 10, 11, 11]); ws.freeze_panes = 'D11'
# ---------------------------------------------------------------- robustness (neighbourhood of each pick)'''
assert s.count(a) == 1; s = s.replace(a, b, 1)
a2 = "rbest = recovery_sheet(wb, FIN); robust_sheet(wb, FIN)"
b2 = "rbest = recovery_sheet(wb, FIN); rulec_sheet(wb); robust_sheet(wb, FIN)"
assert s.count(a2) == 1; s = s.replace(a2, b2)
a3 = "'Recovery rules', 'Robustness', 'Hours', 'Streak math']"
b3 = "'Recovery rules', 'Rule C split test', 'Robustness', 'Hours', 'Streak math']"
assert s.count(a3) == 1; s = s.replace(a3, b3)
a4 = "| Recovery rules | Robustness | Hours | Streak math']"
b4 = "| Recovery rules | Rule C split test | Robustness | Hours | Streak math']"
assert s.count(a4) == 1; s = s.replace(a4, b4)
open(p, 'w').write(s); print('ok')
