p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/build_final.py'; s=open(p).read()
a='''# ---------------------------------------------------------------- streak math'''
b='''# ---------------------------------------------------------------- robustness (neighbourhood of each pick)
def robust_sheet(wb, FIN):
    ws = wb.create_sheet('Robustness')
    title(ws, 'How fragile are the recommended settings? Every single setting changed once more on top of them',
          'A setting that only works at one exact value is probably luck. Shown: how many one-step changes stay profitable after spread in both halves, and the changes that hurt most.')
    ws.merge_cells('A2:J2'); r = 4
    cols = ['Timeframe', 'Settings', 'One-step changes tested', 'Still profitable in 2021-23 and 2024-26', 'Share', 'Median R per trade after spread (all changes)',
            'R per trade of the pick itself', 'Most damaging change', 'R per trade after it', '2nd most damaging', 'R per trade after it', '3rd most damaging', 'R per trade after it']
    hdr(ws, r, cols, height=54); r += 1
    for tf in TFS:
        if tf not in FIN or 'neigh' not in FIN[tf]: continue
        for prof in ('profit', 'streak'):
            if prof not in FIN[tf]['neigh']: continue
            rows = []
            for mn, c, tr in FIN[tf]['neigh'][prof]:
                if not tr: continue
                m = greedy.metrics(greedy.pack(tr), {}); rows.append((mn, m))
            if not rows: continue
            both = sum(1 for _, m in rows if m['A']['E'] > 0 and m['B']['E'] > 0)
            med = statistics.median(m['all']['E'] for _, m in rows)
            own = [x[1] - x[4] / x[5] for x in FIN[tf]['trades'][prof]]
            worst = sorted(rows, key=lambda x: x[1]['all']['E'])[:3]
            vals = [tf, PNAME[prof], len(rows), both, '=IF(C{0}=0,"",D{0}/C{0})', round(med, 4), round(sum(own) / len(own), 4) if own else 0]
            for mn, m in worst: vals += [mn, round(m['all']['E'], 4)]
            for j, v in enumerate(vals, 1):
                isf = isinstance(v, str) and v.startswith('=')
                put(ws, r, j, v.format(r) if isf else v, '0.0%' if j == 5 else '0.000' if j in (6, 7, 9, 11, 13) else None, False,
                    None if (isf or j in (1, 2, 8, 10, 12)) else BLUE, wrap=j in (8, 10, 12))
            r += 1
        r += 1
    widths(ws, [9, 30, 9, 11, 7, 11, 9, 30, 9, 30, 9, 30, 9]); ws.freeze_panes = 'C5'
# ---------------------------------------------------------------- streak math'''
assert s.count(a)==1; s=s.replace(a,b,1)
a2="""rbest = recovery_sheet(wb, FIN); math_sheet(wb)"""
b2="""rbest = recovery_sheet(wb, FIN); robust_sheet(wb, FIN); math_sheet(wb)"""
assert s.count(a2)==1; s=s.replace(a2,b2)
a3="""'Exits', 'Recovery rules', 'Streak math']"""
b3="""'Exits', 'Recovery rules', 'Robustness', 'Streak math']"""
assert s.count(a3)==1; s=s.replace(a3,b3)
open(p,'w').write(s); print('ok')
