"""Workbook sheet 'Crooks A and B test' from crooks.pkl (backtest, halves, stress, cap sizes) and crooks_mc.pkl (500 random orders).
The findings text is built from those results. Called from build_final.py."""
import os, sys, pickle
from openpyxl.styles import Alignment
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
from build_final import put, hdr, title, font, widths, SUB, TOT, GOOD, BAD, BLUE, TFS
ACT = {'clamp': 'Clamp', 'reset': 'Start again', 'stop': 'Stop trading'}
USD = '#,##0;(#,##0);-'
def rule(m): return 'Off (fixed $50)' if m == 'Off' else m
def cap_txt(c, a): return 'none' if not c else '$%d, %s' % (c, ACT[a])
def split_txt(m, s): return s if m in ('Crooks B', 'Rule C split') else '-'
def sname(tf, i, d): return 'Default settings' if i == 0 else '%s-S%d: %s' % (tf, i, ' + '.join(d['scen']))
def sshort(tf, i, d): return 'Default settings' if i == 0 else '%s-S%d: %s%s' % (tf, i, d['scen'][0], ' (+%d more goals)' % (len(d['scen']) - 1) if len(d['scen']) > 1 else '')
def pct(x): return '%.0f%%' % (100 * x)
def usd(x): return ('-$' if x < 0 else '$') + format(round(abs(x)), ',')
def note_rows(ws, r, lines, width_cols=17, h=None):
    for k, t in enumerate(lines):
        c = ws.cell(r + k, 1, t); c.font = font(bold=(k == 0), size=9); c.alignment = Alignment(wrap_text=True, vertical='top')
        ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=width_cols)
        if h and k: ws.row_dimensions[r + k].height = max(15, 12.5 * -(-len(t) // 190) + 3)     # rows sized to the text (about 190 characters per line)
    return r + len(lines) + 1
def section(ws, r, text, cols=12):
    put(ws, r, 1, text, bold=True, fill=SUB); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=cols); return r + 1
def crooks_sheet(wb):
    fb, fm = S + '/gold/crooks.pkl', S + '/gold/crooks_mc.pkl'
    if not (os.path.exists(fb) and os.path.exists(fm)): return
    D = pickle.load(open(fb, 'rb')); M = pickle.load(open(fm, 'rb'))
    order = sorted(D, key=lambda k: (TFS.index(k[0]), k[1]))
    find = lambda tf, name: next((k for k in order if k[0] == tf and D[k]['name'] == name), None)
    row = lambda k, m, s, c, a: next(x for x in D[k]['rows'] if (x['mode'], x['split'], x['cap'], x['act']) == (m, s, c, a))
    ws = wb.create_sheet('Crooks A and B test')
    title(ws, 'Crooks A and Crooks B loss recovery (FxPro MT5 gold, 2021-2026, after spread)')
    r = note_rows(ws, 2, [
        'HOW THE RULES WORK',
        'Crooks A: trades 1 and 2 of a cycle risk the base ($50). From trade 3, every other trade (3, 5, 7 ...) is a RECOVERY trade and the trades between risk the base. '
        'Recovery risk = max(base, loss to win back / final target R): e.g. $250 to win back with TP4 (2R) as the final target -> $125; with TP2 (1R) -> $250; with TP1 (0.6R) -> $417. '
        'Losses add to the loss to win back, wins reduce it (never below 0). A winning recovery trade starts a new cycle (base, base, recovery ...), even if not everything is back; so does winning everything back.',
        'Crooks B: the same alternation, but recovery risk = max(base, loss to win back / split / final target R), with split = the Rule C split setting, and a new cycle starts only when the '
        'whole loss is won back (a recovery win that leaves some of the loss keeps alternating). Split 1 = Crooks A sizing with the Crooks B reset.',
        'Example, 5 losses in a row, base $50, final target TP2 (1R), Crooks A: risks $50, $50, $100, $50, $250. Same with TP4 (2R): $50, $50, $50, $50, $100. '
        'Hard cap: only when it is switched on; "Start again" = forget the loss to win back and trade 1 of a new cycle at the base risk.',
        'Test: $10,000 start, $50 base, every trade sized like the strategy and the EA (a stop-out loses the computed risk incl. spread), no leverage limit. '
        'The EA\'s own sizing code was run on these trades and gave the same risk on every trade (1.9 million trades compared, every rule except % of equity).'], h=40)
    r = note_rows(ws, r, [
        'HOW TO SET IT',
        'TradingView strategy, group LOSS RECOVERY (strategy only): Loss Recovery = "Crooks A (base, base, then recovery every 2nd trade)" or "Crooks B (Crooks A with the loss split over N trades)"; '
        'for Crooks B also "Split The Loss Over This Many Trades (Rule C, Crooks B)" = 2-5. Group RISK: tick "Hard Cap: Max Loss Per Trade ($)", 500, and '
        '"If The Risk Would Exceed The Cap" = "Start again from the base risk". The final target is "Exit At" (TP1-TP4).',
        'MT5 EA, group LOSS RECOVERY: Loss recovery (InpRec) = Crooks A / Crooks B; InpCSplit = the split (Crooks B). RISK: InpCapOn = true, InpHardCap = 500, '
        'InpCapAction = Start again from the base risk. The EA keeps the cycle in memory: after an EA restart it starts at trade 1 of a new cycle.',
        'Chart table row "CROOKS: LOSS TO WIN BACK": the $ still to win back, the number of the next (or open) trade in the cycle and whether it is a base or a recovery trade.'], h=30)
    # ---- findings, built from the results
    best = {tf: find(tf, 'Most profit') for tf in TFS}
    def mc(k, m, s, c, a): return M.get(k, {}).get('rules', {}).get((m, s, c, a))
    ed = [k for k in order if k in M]
    nocap_blow = {tf: max([100 * mc(k, 'Crooks A', 3, 0.0, 'clamp')['ruin'] for k in ed if k[0] == tf] + [0]) for tf in TFS}
    nocap_blow1 = {tf: max([100 * mc(k, 'Crooks B', 1, 0.0, 'clamp')['ruin'] for k in ed if k[0] == tf] + [0]) for tf in TFS}
    CRK = (('Crooks A', 3), ('Crooks B', 1), ('Crooks B', 2), ('Crooks B', 3), ('Crooks B', 4), ('Crooks B', 5))
    sa_blow = {tf: max([mc(k, m, s, 500.0, 'reset')['ruin'] for k in ed if k[0] == tf for m, s in CRK] + [0.0]) for tf in TFS}
    sa_txt = ', '.join('%s %s' % (tf, ('%.1f%%' % (100 * v)) if v else 'none') for tf, v in sa_blow.items())
    def ratio(x): return x['net'] / x['maxDD'] if x['maxDD'] > 0 else 0.0
    beatA = sum(1 for k in ed if ratio(row(k, 'Crooks A', 3, 500.0, 'reset')['all']) > ratio(row(k, 'Off', 3, 0.0, 'clamp')['all']))
    beatB = sum(1 for k in ed if ratio(row(k, 'Crooks B', 3, 500.0, 'reset')['all']) > ratio(row(k, 'Off', 3, 0.0, 'clamp')['all']))
    medA = sum(1 for k in ed if mc(k, 'Crooks A', 3, 500.0, 'reset')['med'] > mc(k, 'Off', 3, 0.0, 'clamp')['med'])
    dflt = [k for k in order if k[1] == 0]
    dblow = sum(1 for k in dflt for x in D[k]['rows'] if x['mode'].startswith('Crooks') and not x['cap'] and x['all']['ruined'])
    dall = sum(1 for k in dflt for x in D[k]['rows'] if x['mode'].startswith('Crooks') and not x['cap'])
    def line(tf):
        k = best[tf]; o = row(k, 'Off', 3, 0.0, 'clamp')['all']; a = row(k, 'Crooks A', 3, 500.0, 'reset')['all']; ma = mc(k, 'Crooks A', 3, 500.0, 'reset')
        b = row(k, 'Crooks B', 3, 500.0, 'reset')['all']; mb = mc(k, 'Crooks B', 3, 500.0, 'reset')
        return ('%s best settings (%s-S%d): Off %s, fall %s | Crooks A %s, fall %s (random orders: median %s, worst 5%% %s, 95%% of orders fall less than %s) | '
                'Crooks B split 3 %s, fall %s (median %s, 95%% fall < %s).' % (tf, tf, k[1], usd(o['net']), pct(o['maxDDpct']), usd(a['net']), pct(a['maxDDpct']), usd(ma['med']), usd(ma['p5']),
                                                                            pct(ma['dd95']), usd(b['net']), pct(b['maxDDpct']), usd(mb['med']), pct(mb['dd95'])))
    k15 = best['M15']
    h1 = [k for k in ed if k[0] == 'H1']
    h1base = sum(1 for k in h1 if all(row(k, 'Crooks B', s, 0.0, 'clamp')['all']['maxRisk'] <= 50.0 + 1e-9 for s in (4, 5)))
    r = note_rows(ws, r, [
        'WHAT IT SHOWS',
        '1. Gold trades do not win more often after losses (M15 best settings: %.1f%% of all trades profitable, %.1f%% right after two losses). So Crooks cannot make the signals better: '
        'it makes more money only because the recovery trades risk more than $50, and the account also falls deeper.' % tuple(100 * v for v in _after_losses(*k15)),
        '2. Always use the hard cap. Without it, Crooks A blew the $10,000 account in up to %s of the random orders (worst strategy per timeframe: M1 %s, M5 %s, M15 %s, H1 %s) '
        'and Crooks B split 1 in up to %s; with the default settings %d of %d uncapped Crooks runs blew the account. With the $500 cap and "Start again", the worst share of '
        'random orders that blew the account (any Crooks rule and split, worst strategy) was: %s.' % (
            pct(max(nocap_blow.values()) / 100), pct(nocap_blow['M1'] / 100), pct(nocap_blow['M5'] / 100), pct(nocap_blow['M15'] / 100), pct(nocap_blow['H1'] / 100),
            pct(max(nocap_blow1.values()) / 100), dblow, dall, sa_txt),
        '3. ' + line('H1'), '4. ' + line('M15'), '5. ' + line('M5'), '6. ' + line('M1'),
        '7. Luck of the order: when the real order "beats" 90%%+ of the random orders, the backtest is luckier than average - use the random-order median as the fair expectation (part 3). '
        'Example: M1 best settings, Crooks A with the cap made %s in the backtest, but the median of 500 random orders is %s.' % (
            usd(row(best['M1'], 'Crooks A', 3, 500.0, 'reset')['all']['net']), usd(mc(best['M1'], 'Crooks A', 3, 500.0, 'reset')['med'])),
        '8. Per $ of drawdown, fixed risk (Off) stays as good or better on most settings: Crooks A ($500 cap, Start again) had a better profit / drawdown than Off on %d of %d profitable strategies, '
        'Crooks B split 3 on %d of %d. More profit for the same fall is also possible by raising the fixed risk. Crooks A beat Off on the random-order median net on %d of %d.' % (
            beatA, len(ed), beatB, len(ed), medA, len(ed)),
        '9. A bigger split in Crooks B is the gentle version (less extra profit, less extra fall). On H1, Crooks B split 4-5 never risked more than the base on %d of %d strategies: '
        'the losses there never grow large enough, so it trades like Off.' % (h1base, len(h1)),
        '10. Partial close at TP1 (low-streak strategies marked "strategy and EA only"): the recovery size still divides by the final target R, so a recovery win pays back less than the loss.',
        _vs_all()], h=30)
    # ---- PART 1: quick answer
    r = section(ws, r, 'PART 1 - quick answer: the best settings per timeframe with the main Crooks choices ($500 cap, Start again) vs Off', 15)
    hdr(ws, r, ['Timeframe', 'Strategy', 'Final target R', 'Rule', 'Split', 'Hard cap', 'Backtest net ($)', 'Backtest deepest fall %', 'Average risk ($)', 'Largest risk ($)',
                'Random orders: median net ($)', 'Random orders: worst 5% net ($)', 'Random orders: 95% fall less than', 'Random orders: account blown', 'Random orders: fall > 40%'], height=54); r += 1
    QUICK = [('Off', 3, 0.0, 'clamp'), ('Crooks A', 3, 500.0, 'reset'), ('Crooks B', 2, 500.0, 'reset'), ('Crooks B', 3, 500.0, 'reset'), ('Crooks B', 5, 500.0, 'reset')]
    for tf in TFS:
        for name in ('Most profit', 'Shortest losing streak - indicator only'):
            k = next((q for q in order if q[0] == tf and name in D[q]['scen']), None)
            if k is None or k not in M: continue
            for m, s, c, a in QUICK:
                x = row(k, m, s, c, a)['all']; q = mc(k, m, s, c, a); off = m == 'Off'
                vals = [tf, sname(tf, k[1], D[k]), D[k]['exitR'], rule(m), split_txt(m, s), cap_txt(c, a), round(x['net'], 2), round(x['maxDDpct'], 4), round(x['avgRisk'], 2),
                        round(x['maxRisk'], 2), round(q['med'], 2), round(q['p5'], 2), round(q['dd95'], 4), round(q['ruin'], 4), round(q['dd40'], 4)]
                for j, v in enumerate(vals, 1):
                    put(ws, r, j, v, USD if j in (7, 9, 10, 11, 12) else '0.0%' if j in (8, 13, 14, 15) else '0.00' if j == 3 else None, off, BLUE if j >= 7 or j == 3 else None,
                        TOT if off else None, wrap=(j == 2))
                ws.row_dimensions[r].height = 12 * -(-len(sname(tf, k[1], D[k])) // 46) + 2; r += 1
            r += 1
    # ---- PART 2: every strategy, every variant
    r += 1; r = section(ws, r, 'PART 2 - backtest: every strategy x Crooks A / Crooks B split 1-5 x hard cap (none / $500 Clamp / $500 Start again / $500 Stop trading); each half from a fresh $10,000', 20)
    cols = ['Timeframe', 'Strategy', 'Final target R', 'Rule', 'Split', 'Hard cap', 'Net profit ($)', 'Max drawdown ($)', 'Max drawdown %', 'Average risk ($)', 'Largest risk ($)',
            'Worst run of losses ($)', 'Account', 'Profit / max drawdown', 'vs Off (1 = same)', '2021-23 net ($)', '2021-23 max drawdown %', '2024-26 net ($)', '2024-26 max drawdown %',
            'Eligible (whole run kept trading to the end, whole run and both halves profitable, risk <= $500, falls <= 40%)']
    hdr(ws, r, cols, height=66); r += 1; top = r
    for k in order:
        d = D[k]; offrow = None
        for x in d['rows']:
            a, A, B = x['all'], x['A'], x['B']; off = x['mode'] == 'Off'
            if off: offrow = r
            st = 'BLOWN after %d trades' % (a['ruinAt'] + 1) if a['ruined'] else ('stopped by the cap' if a['capStopped'] else 'survived')
            vals = [k[0], sshort(k[0], k[1], d), d['exitR'], rule(x['mode']), split_txt(x['mode'], x['split']), cap_txt(x['cap'], x['act']), round(a['net'], 2), round(a['maxDD'], 2),
                    round(a['maxDDpct'], 4), round(a['avgRisk'], 2), round(a['maxRisk'], 2), round(a['worstRun'], 2), st, '=IF(H{0}=0,"",G{0}/H{0})',
                    '1' if off else '=IF(OR(N{1}="",N{1}<=0,N{0}=""),"",N{0}/N{1})', 'BLOWN' if A['ruined'] else round(A['net'], 2), round(A['maxDDpct'], 4),
                    'BLOWN' if B['ruined'] else round(B['net'], 2), round(B['maxDDpct'], 4),
                    '=IF(AND(M{0}="survived",G{0}>0,K{0}<=500.005,I{0}<=0.4,ISNUMBER(P{0}),ISNUMBER(R{0}),P{0}>0,R{0}>0,Q{0}<=0.4,S{0}<=0.4),"yes","no")']
            for j, v in enumerate(vals, 1):
                isf = isinstance(v, str) and v.startswith('=')
                put(ws, r, j, v.format(r, offrow) if isf else (1 if v == '1' else v),
                    USD if j in (7, 8, 10, 11, 12, 16, 18) else '0.0%' if j in (9, 17, 19) else '0.00' if j in (3, 14, 15) else None,
                    off, BLUE if (j in (3, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19)) and not isf else None, TOT if off else (BAD if a['ruined'] else None))
            r += 1
        r += 1
    ws.auto_filter.ref = 'A%d:T%d' % (top - 1, r - 2)
    # ---- PART 3: random orders
    r += 1; r = section(ws, r, 'PART 3 - fair odds: the same trades of each profitable strategy replayed in 500 random orders (the order of wins and losses is luck; the trades themselves are the same)', 17)
    hdr(ws, r, ['Timeframe', 'Strategy', 'Final target R', 'Rule', 'Split', 'Hard cap', 'Backtest net ($)', 'Backtest beats this share of the random orders', 'Median net ($)', 'Worst 5% net ($)',
                'Best 5% net ($)', 'Median deepest fall %', '95% of orders fall less than', 'Account blown', 'Fall > 40%', 'Losing money', 'Median largest risk ($)'], height=66); r += 1
    for k in order:
        if k not in M: continue
        for (m, s, c, a), q in M[k]['rules'].items():
            off = m == 'Off'
            vals = [k[0], sshort(k[0], k[1], D[k]), D[k]['exitR'], rule(m), split_txt(m, s), cap_txt(c, a), round(q['real']['net'], 2), round(q['rank'], 4), round(q['med'], 2),
                    round(q['p5'], 2), round(q['p95'], 2), round(q['ddMed'], 4), round(q['dd95'], 4), round(q['ruin'], 4), round(q['dd40'], 4), round(q['loss'], 4), round(q['riskMed'], 2)]
            for j, v in enumerate(vals, 1):
                put(ws, r, j, v, USD if j in (7, 9, 10, 11, 17) else '0.0%' if j in (8, 12, 13, 14, 15, 16) else '0.00' if j == 3 else None, off, BLUE if j >= 7 or j == 3 else None,
                    TOT if off else (BAD if q['ruin'] >= 0.05 else None))
            r += 1
        r += 1
    # ---- PART 4: stress
    r += 1; r = section(ws, r, 'PART 4 - stress test: the same runs with 0.05 R and 0.10 R of extra cost on every trade (slippage, a weaker live edge)', 12)
    hdr(ws, r, ['Timeframe', 'Strategy', 'Final target R', 'Rule', 'Split', 'Hard cap', 'Net ($), as tested', 'Max DD %, as tested', 'Net ($), +0.05 R cost', 'Max DD %, +0.05 R', 'Net ($), +0.10 R cost',
                'Max DD %, +0.10 R'], height=42); r += 1
    SKEYS = [('Off', 3, 0.0, 'clamp'), ('Rule C split', 3, 500.0, 'reset'), ('Crooks A', 3, 0.0, 'clamp'), ('Crooks A', 3, 500.0, 'clamp'), ('Crooks A', 3, 500.0, 'reset')] + \
            [('Crooks B', s, c, a) for s in (1, 2, 3, 5) for c, a in ((0.0, 'clamp'), (500.0, 'reset'))]
    for k in order:
        if k[1] == 0: continue
        d = D[k]
        for m, s, c, a in SKEYS:
            x = row(k, m, s, c, a)['all']; vals = [k[0], sshort(k[0], k[1], d), d['exitR'], rule(m), split_txt(m, s), cap_txt(c, a)]
            for q in (x, d['stress'][(m, s, c, a, 0.05)], d['stress'][(m, s, c, a, 0.10)]): vals += ['BLOWN' if q['ruined'] else round(q['net'], 2), round(q['maxDDpct'], 4)]
            for j, v in enumerate(vals, 1):
                put(ws, r, j, v, USD if j in (7, 9, 11) else '0.0%' if j in (8, 10, 12) else '0.00' if j == 3 else None, m == 'Off', BLUE if j >= 7 or j == 3 else None,
                    TOT if m == 'Off' else (BAD if v == 'BLOWN' else None))
            r += 1
        r += 1
    # ---- PART 5: cap size
    r += 1; r = section(ws, r, 'PART 5 - hard cap size: $250 / $500 / $1,000 with Clamp or Start again (Crooks A, Crooks B split 1-3)', 12)
    hdr(ws, r, ['Timeframe', 'Strategy', 'Final target R', 'Rule', 'Split', 'Hard cap', 'Net profit ($)', 'Max drawdown ($)', 'Max drawdown %', 'Largest risk ($)', 'Account',
                'Profit / max drawdown'], height=42); r += 1
    for k in order:
        if k[1] == 0: continue
        d = D[k]; rows = []
        for m, s in [('Crooks A', 3)] + [('Crooks B', s) for s in (1, 2, 3)]:
            for c in (250.0, 500.0, 1000.0):
                for a in ('clamp', 'reset'): rows.append((m, s, c, a, d['caps'][(m, s, c, a)] if c != 500.0 else row(k, m, s, c, a)['all']))
        for m, s, c, a, q in rows:
            vals = [k[0], sshort(k[0], k[1], d), d['exitR'], rule(m), split_txt(m, s), cap_txt(c, a), round(q['net'], 2), round(q['maxDD'], 2), round(q['maxDDpct'], 4),
                    round(q['maxRisk'], 2), 'BLOWN' if q['ruined'] else 'survived', '=IF(H{0}=0,"",G{0}/H{0})']
            for j, v in enumerate(vals, 1):
                isf = isinstance(v, str) and v.startswith('=')
                put(ws, r, j, v.format(r) if isf else v, USD if j in (7, 8, 10) else '0.0%' if j == 9 else '0.00' if j in (3, 12) else None, False,
                    BLUE if 7 <= j <= 10 or j == 3 else None,
                    BAD if q['ruined'] else None)
            r += 1
        r += 1
    widths(ws, [9, 40, 9, 16, 7, 18, 11, 11, 10, 10, 10, 11, 18, 10, 10, 11, 10, 11, 10, 14])
    ws.freeze_panes = 'C1'
def _vs_all():
    """Crooks against all 19 rules on the 8 profitable best / low-streak settings, the same way as the summary of the Recovery rules sheet"""
    import collections
    from build_final import eligible, rkey
    agg = collections.defaultdict(list); cases = 0
    for tf in TFS:
        F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb'))
        for prof in ('profit', 'streak'):
            if F.get('passed', {}).get(prof) is False: continue
            rows = F['recovery'][prof]; cases += 1; off = [x for x in rows if x['mode'] == 'Off'][0]; el = {rkey(x) for x in eligible(rows)}
            for x in rows:
                if rkey(x) in el: agg[(x['mode'], x['cap'])].append(((x['net'] / x['maxDD']) / (off['net'] / off['maxDD']), x['net'] / off['net']))
    full = sorted([(k, v) for k, v in agg.items() if len(v) == cases and k[0] != 'Off'], key=lambda kv: -sum(q for q, _ in kv[1]) / len(kv[1]))
    if not full: return '11. No recovery rule stayed within the limits on all %d profitable settings.' % cases
    (m, c), v = full[0]
    others = ', '.join('%s%s (%.2f)' % (mm, ' + $500 cap' if cc else '', sum(q for q, _ in vv) / len(vv)) for (mm, cc), vv in full[1:4])
    return ('11. Against all 19 rules (sheet Recovery rules, $500 cap = Clamp): on the %d profitable best / low-streak settings, %s%s (split 3) is the best rule after Off that stayed within '
            'the limits in every case - %.2f x Off\'s profit per $ of drawdown with %.2f x its profit. Next: %s.' % (
                cases, m, ' + $500 cap' if c else '', sum(q for q, _ in v) / len(v), sum(g for _, g in v) / len(v), others))
def _after_losses(tf, i):
    """share of profitable trades overall and right after two losses, for one strategy (crooks.sources order)"""
    import crooks
    src = crooks.sources(tf)[i]
    seq = crooks.sequence(src['trades'], src['cfg']); w = [1 if (res - c) > 0 else 0 for _, res, c, _ in seq]
    a2 = [w[i] for i in range(2, len(w)) if w[i - 1] == 0 and w[i - 2] == 0]
    return sum(w) / len(w), sum(a2) / len(a2)
