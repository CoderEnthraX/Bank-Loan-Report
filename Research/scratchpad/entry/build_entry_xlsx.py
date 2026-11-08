"""Gold_Entry_Accuracy_Research.xlsx from entry/report_data.json (numbers) + the research conclusions (texts)."""
import json, math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter as L
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
D = json.load(open(S + '/entry/report_data.json'))
F = 'Arial'
f_norm = Font(name=F, size=10); f_bold = Font(name=F, size=10, bold=True); f_title = Font(name=F, size=14, bold=True)
f_sub = Font(name=F, size=11, bold=True, color='1F3864'); f_head = Font(name=F, size=10, bold=True, color='FFFFFF')
fill_sec = PatternFill('solid', fgColor='DDEBF7'); fill_note = PatternFill('solid', fgColor='FFF7E0'); fill_head = PatternFill('solid', fgColor='1F3864')
fill_good = PatternFill('solid', fgColor='E2EFDA'); fill_bad = PatternFill('solid', fgColor='FCE4D6'); fill_key = PatternFill('solid', fgColor='FFF2CC')
wrap = Alignment(wrap_text=True, vertical='top'); center = Alignment(horizontal='center', vertical='top', wrap_text=True)
NOEDGE = [62.5, 50.0, 40.0, 100 / 3]
PER = {'train': '2021-2023', 'valid': '2024 - Jun 2025', 'test': 'TEST Jul 2025 - Oct 2026'}

def widths(ws, w):
    for k, x in enumerate(w, 1): ws.column_dimensions[L(k)].width = x
def wsum(ws, n): return sum(ws.column_dimensions[L(k)].width or 9 for k in range(1, n + 1))
def note(ws, r, text, n, font=None, fill=fill_note):
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=n)
    c = ws.cell(r, 1, text); c.font = font or f_norm; c.alignment = wrap
    for k in range(1, n + 1): ws.cell(r, k).fill = fill
    cpl = max(30, wsum(ws, n) * 1.05)
    lines = sum(max(1, math.ceil(len(p) / cpl)) for p in text.split('\n'))
    ws.row_dimensions[r].height = 14.5 * lines + 4
    return r + 1
def explain(ws, n, title, what, how):
    ws.cell(1, 1, title).font = f_title; r = 2
    r = note(ws, r, 'WHAT THIS SHEET IS', n, f_sub, fill_sec)
    for p in what: r = note(ws, r, p, n)
    r = note(ws, r, 'HOW TO READ IT', n, f_sub, fill_sec)
    for p in how: r = note(ws, r, '• ' + p, n)
    return r + 1
def header(ws, r, cols):
    for k, t in enumerate(cols, 1):
        c = ws.cell(r, k, t); c.font = f_head; c.fill = fill_head; c.alignment = center
    ws.row_dimensions[r].height = 30
    return r + 1
def put(ws, r, vals, bold=False, fmt=None, fill=None):
    for k, v in enumerate(vals, 1):
        c = ws.cell(r, k, v); c.font = f_bold if bold else f_norm; c.alignment = wrap if isinstance(v, str) else Alignment(vertical='top')
        if fmt and k in fmt and isinstance(v, (int, float)): c.number_format = fmt[k]
        if fill: c.fill = fill
    return r + 1

wb = Workbook()
# ======================================================================== Read me
ws = wb.active; ws.title = 'Read me'; widths(ws, [150])
ws['A1'] = 'Gold 2021-2026: can a better entry raise the TP1-TP4 accuracy of the Auction Retest indicator?'; ws['A1'].font = f_title
r = 3
def rm(t, font=f_norm, fill=None):
    global r
    c = ws.cell(r, 1, t); c.font = font; c.alignment = wrap
    if fill: c.fill = fill
    ws.row_dimensions[r].height = 14.5 * max(1, math.ceil(len(t) / 160)) + 4; r += 1
rm('WHAT THIS WORKBOOK IS', f_sub, fill_sec)
rm('The research you asked for after v4.2: rethink the entry (or the VWAP rules, or anything else) so that the hit rate of EVERY target TP1-TP4 goes up. '
   'Data: FxPro gold, every 1-minute candle from 4 January 2021 to 2 October 2026 (2.04 million minutes), also built into 5-minute, 15-minute and 1-hour candles. '
   'Accuracy = how often a trade reaches TP1 / TP2 / TP3 / TP4 (0.6 / 1 / 1.5 / 2 R) before its stop, measured on the 1-minute path.')
rm('THE SHORT ANSWER', f_sub, fill_sec)
for t in ('1. Today the signals have no edge in direction. The indicator hits TP1-TP4 about 62 / 50 / 40 / 33 % of the time. Random entries with the same stop and '
          'targets hit the same: 62.5 / 50 / 40 / 33.3 % is simply the chance of reaching 0.6 / 1 / 1.5 / 2 R before -1 R when nothing predicts the direction '
          '(formula: 1 / (1 + target in R)). Your v4.0 settings: the same in 2021-2025 (sheet 1).',
          '2. About 1,100 entry rules were tested by three independent researchers (me and two research agents), plus 3,700 conditions found by a data search and '
          'machine-learning models on about 60 features. Some looked good on 2021-2025, but none beat random entries on the months kept aside for the final test '
          '(July 2025 - October 2026). An independent checker recomputed the test with its own code and got exactly the same numbers (sheets 2 and 3).',
          '3. So the indicator, the strategy and the EA were NOT changed. A rule that only looks good on past data would make your backtests look better while you '
          'keep trading the same coin flip, and it would cost you the trades it removes.',
          '4. The one real pattern found is the time of day in New York: gold tends to fall 07:00-10:00 and rise 13:00-17:00 New York time. It was strong in 2023-2025 '
          'but much weaker in the test months, so it cannot be relied on as a fixed rule (sheet 4).',
          '5. Why the pullback entry cannot add accuracy: the retest limit fills mostly on the moves that are already failing; the strong moves never come back to it '
          '(sheet 5). What really changes results is the cost per trade, not the entry (sheet 6).',
          '6. Order flow (sheet 7): POC / value area, LVN / HVN, delta, cumulative delta, absorption, exhaustion and pullback volume were tested by two more research '
          'agents (about 940 variants) as filters on the signals and as entries of their own. None finds the false signals or the winners: the best looked 2-5 points '
          'better than random on 2021-2025 and were at or below random in the test months. Gold has tick volume only (no real buy / sell volume), so delta is an '
          'estimate, the same as TradingView\'s order-flow tools show on XAUUSD.'):
    rm(t)
rm('HOW THE TEST WAS DONE', f_sub, fill_sec)
for t in ('• Periods: rules were found on 2021-2023, checked on January 2024 - June 2025, and the best ones were tested ONCE on July 2025 - October 2026, written '
          'down before the test (pre-registered), so the test could not be bent to fit.',
          '• Random reference: for every period, long and short trades on random candles with the same stop (1.8 ATR) and targets. Gold rose strongly in 2024-2025, '
          'so random longs hit more often then; comparing each rule with random trades of the same direction and period removes that.',
          '• Every signal was simulated on its own on the 1-minute candles (stop counted first when a minute touches both). Sheet 1 also shows the real indicator '
          '(one trade at a time) and your v4.0 settings.',
          '• Noise: with n trades a hit rate moves by about 50 / sqrt(n) points by luck (1,000 trades: +-1.6 points). After testing hundreds of rules, the best one '
          'looks 2-4 points better than random by luck alone.'):
    rm(t)
rm('THE SHEETS', f_sub, fill_sec)
for t in ('1 Accuracy vs random: the hit rates of random entries, the indicator\'s signals, the indicator as it trades and your v4.0 settings, per timeframe and period.',
          '2 What was tested: every family of ideas, how many variants, the best result before the test and the verdict.',
          '3 Finalists and test: the 4 best rules and 2 references on all three periods, longs and shorts, with the pass / fail rule written before the test.',
          '4 Time of day: which New York hours favoured longs or shorts in each year (the one real pattern) and how it faded in the test months.',
          '5 Why the retest limit: the same signals entered at the limit vs at market, split by whether the limit filled.',
          '6 What to do: practical conclusions for your trading and the two optional additions I can make.',
          '7 Order flow: volume profile, delta and the other order-flow ideas, as filters and as entries, with their final test.'):
    rm('• ' + t)

# ======================================================================== 1 Accuracy vs random
ws = wb.create_sheet('1 Accuracy vs random'); widths(ws, [10, 44, 26, 10, 10, 9, 9, 9, 9, 16]); N = 10
r = explain(ws, N, '1. Accuracy vs random entries', [
    'How often each kind of trade reached TP1 / TP2 / TP3 / TP4 (0.6 / 1 / 1.5 / 2 R) before its stop, per timeframe and period. The first row of each timeframe is '
    'the no-edge rate, the next two are random entries; the rest are the indicator.'],
    ['Compare every row with the random rows of the same timeframe and period: a real edge must be clearly above them at every target. Hit rates in %.',
     '"vs random" = the average over the 4 targets of (hit rate minus random), in percentage points; the random reference is the same direction mix where known '
     '(signals), otherwise the average of random longs and shorts.',
     '"Every signal on its own" counts every signal (as if each could be traded). "As the indicator trades" = one trade at a time, default settings, final exit '
     'TP4 so all 4 targets can be seen (chart rule: stop first when a candle touches both). Your v4.0 settings are shown the same way.'])
COLS = ['Timeframe', 'What', 'Period', 'Trades', 'Per month', 'TP1 %', 'TP2 %', 'TP3 %', 'TP4 %', 'vs random (pts)']
r = header(ws, r, COLS)
FMT = {4: '#,##0', 5: '0.0', 6: '0.0', 7: '0.0', 8: '0.0', 9: '0.0', 10: '+0.0;-0.0;0.0'}
MON = {'train': 36.0, 'valid': 18.0, 'test': 15.1}
for tf in ('M5', 'M15', 'H1', 'M1'):
    r = put(ws, r, [tf, 'No edge (any entry, 0.6 / 1 / 1.5 / 2 R vs a 1 R stop)', 'any', None, None] + NOEDGE + [0.0], True, FMT, fill_key)
    for sp in ('train', 'valid', 'test'):
        rl = D['random']['%s|%s|1' % (tf, sp)]; rs = D['random']['%s|%s|-1' % (tf, sp)]
        r = put(ws, r, [tf, 'Random entries: longs', PER[sp], rl['n'], None] + rl['hit'] + [sum(a - b for a, b in zip(rl['hit'], NOEDGE)) / 4], False, FMT)
        r = put(ws, r, [tf, 'Random entries: shorts', PER[sp], rs['n'], None] + rs['hit'] + [sum(a - b for a, b in zip(rs['hit'], NOEDGE)) / 4], False, FMT)
    for sp in ('train', 'valid', 'test'):
        x = D['raw'][tf]['%s|both' % sp]
        r = put(ws, r, [tf, 'Indicator: every signal on its own', PER[sp], x['n'], x['per_month']] + x['hit'] + [x['avg_excess']], False, FMT,
                fill_good if x['avg_excess'] > 2 else None)
    for nm, lab in (('default', 'Indicator as it trades (default settings)'), ('v4.0 settings', 'Your v4.0 settings (as it trades)')):
        for sp in ('train', 'valid', 'test'):
            k = '%s|%s|%s' % (tf, nm, sp)
            if k not in D['exact']: continue
            x = D['exact'][k]; rl = D['random']['%s|%s|1' % (tf, sp)]['hit']; rs = D['random']['%s|%s|-1' % (tf, sp)]['hit']
            ref = [(a + b) / 2 for a, b in zip(rl, rs)]
            ex = sum(a - b for a, b in zip(x['hit_chart'], ref)) / 4
            r = put(ws, r, [tf, lab, PER[sp], x['n'], x['per_month']] + x['hit_chart'] + [ex], nm != 'default', FMT, fill_good if ex > 2 else None)
    r += 1

# ======================================================================== 2 What was tested
ws = wb.create_sheet('2 What was tested'); widths(ws, [34, 52, 13, 12, 40, 30]); N = 6
r = explain(ws, N, '2. What was tested', [
    'Every family of ideas tried to raise the accuracy, who tested it, how many variants, the best result BEFORE the final test and the verdict. Three independent '
    'researchers: me, and two research agents working in parallel (one on new setups, one on the indicator\'s own entry).'],
    ['"Best before the test" = the best average gain over random in 2021-2023 / 2024-mid 2025 (points, average over TP1-TP4). With hundreds of variants, '
     '+2 to +4 points appear by luck alone, so a result counts only if it also holds in the test months (sheet 3).'])
r = header(ws, r, ['Family', 'What was tried', 'Variants', 'By', 'Best before the test', 'Verdict'])
ROWS = [
    ('Filters on the indicator\'s signals', '~60 features: daily / weekly / monthly trend, VWAP distance, slope and sigma, session position, previous day high / low, '
     'candle size, body, close, break distance, momentum, efficiency, tick volume, compression, volatility regime, spread, time of day, half stop, entry depth', '180', 'me',
     'single features +1 to +3 points, not repeating in 2024-25', 'No edge'),
    ('Machine learning (LightGBM)', 'All features together on the signals, and on every candle (long and short)', '8 models', 'me',
     'signals: score 0.50-0.51 (0.50 = coin flip); every candle 0.53, mostly gold\'s trend regime', 'No edge'),
    ('Data search (rule mining)', 'Every feature fifth x New York 3-hour block, longs and shorts, day-clustered statistics', '3,694 cells', 'me',
     'only "longs in the New York afternoon" consistent', 'Time of day only (sheet 4)'),
    ('Entry mechanics', 'Retest confirmation (touch, then close back), fill window 1-5 candles, limit depth 0-100 %, market entry, market after no fill, '
     'second displacement, first pullback candle, stop entry beyond the signal candle', '~150', 'agent B + me', 'within +-2 points of random', 'No edge'),
    ('Stops', 'Structural (retest low, signal candle), tight and wide ATR stops', '~40', 'agent B', 'tighter stops worse (spread, 1-minute noise)', 'No edge'),
    ('Gates on the signal', 'Week / month VWAP side, daily trend, volatility regime, stronger CMO / body / close / range / break, New York hours', '~120', 'agent B',
     'train only', 'No edge'),
    ('Opposite trade (fade)', 'Fade every signal or by New York 3-hour block, with variants', '~100', 'agent B',
     '+4.5 / +5.4 (5-minute, New York 12:00-18:00)', 'Failed the test (sheet 3)'),
    ('Opening ranges', 'London, New York 08:30 / 09:30 / 10:00, Asia: breakout and fade', '~60', 'agent A', '+3.1 / +3.5 (15-minute, New York 09:30)',
     'Failed the test (sheet 3)'),
    ('Liquidity sweeps', 'Previous day high / low, day high / low, London range swept in New York; market and confirmation entries', '~40', 'agent A',
     '+3.8 / +7.3 (15-minute, previous day high / low)', 'Failed the test (sheet 3)'),
    ('VWAP rules', 'Reclaim / reject, pullback to VWAP or 1 sigma in a trend, 2-2.5 sigma fades, far-from-VWAP fades, first stretch of the session', '~60',
     'agent A + me', 'none positive in all four parts', 'No edge'),
    ('Other setups', 'News candles (08:30, 10:00 New York), intraday momentum, late-session drift, round numbers ($10 / $50), NR7 / inside candles, reopen gaps, '
     'runs of candles, volume climaxes, multi-timeframe signals, jobs-report Fridays', '~150', 'agents + me', 'noise', 'No edge'),
    ('Time of day alone', 'Longs New York 13:00-17:00, shorts 07:00-10:00, every candle; clock-shift placebo test', '24 hours x 6 periods', 'me',
     '+2 / +5.5 (15-minute), beats every shifted clock', 'Real, but faded in the test months'),
]
for row in ROWS:
    r = put(ws, r, list(row), False, None, fill_bad if row[5].startswith('Failed') else (fill_key if row[5].startswith(('Time', 'Real')) else None))
r = note(ws, r + 1, 'In total about 1,100 rules (agent A 357, agent B 522, me about 200) plus 3,694 mined conditions and 8 models. Agent A\'s conclusion before '
         'the test: none of its 357 variants was significant once the number of tries is counted.', N)

# ======================================================================== 3 Finalists and test
ws = wb.create_sheet('3 Finalists and test'); widths(ws, [36, 11, 26, 8, 8, 8, 8, 8, 8, 13, 10]); N = 11
r = explain(ws, N, '3. Finalists and the final test', [
    'The best rules found on 2021-2025 and two references, tested ONCE on July 2025 - October 2026. The list and the pass rule were written down before the test: '
    'pass = better than random for longs AND shorts in the test months, by at least one standard error overall, at 3 of the 4 targets.'],
    ['Look at the TEST rows: green = better than random, red = worse. A real edge would stay green there. Excess = hit rate minus random entries of the same '
     'direction in the same period, average over TP1-TP4 (points); se = its standard error (about 50 / sqrt(trades)).',
     'Result: no finalist passed. The independent checker recomputed these numbers with its own code (own ATR, New York time, 1-minute simulation and random '
     'reference) and got the same values to 0.01 points.'])
RULES = {
    'C1 fade NY 12-18 (PRIMARY)': '5-minute: when the indicator signals on a candle opening 12:00-17:59 New York time, take the OPPOSITE trade at market, stop 1.8 ATR',
    'C1L fade, longs only': 'The same, only the long side (buy after a bearish signal)',
    'ORB NY 09:30-10:00': '15-minute: range 09:30-10:00 New York; at 10:00 a buy stop above it and a sell stop below it until 13:00, stop 1.8 ATR',
    'SWEEP prev-day H/L': '15-minute: first candle that goes beyond the previous day\'s high (low) and closes back inside; stop entry on its other end, valid 3 candles',
    'ref: time-of-day bias': 'Reference: every candle, longs New York 13:00-16:59, shorts 07:00-09:59',
}
r = header(ws, r, ['Rule', 'Timeframe', 'Period', 'Side', 'Trades', 'TP1 %', 'TP2 %', 'TP3 %', 'TP4 %', 'Excess (pts)', 'se'])
for fz in D['finalists']:
    r = note(ws, r, '%s: %s' % (fz['name'].replace(' (PRIMARY)', ' (main candidate)'), RULES.get(fz['name'], '')), N, f_bold, fill_sec)
    sides = ('long',) if 'longs only' in fz['name'] else ('long', 'short', 'both')
    for sp in ('train', 'valid', 'test'):
        for sd in sides:
            x = fz['res'].get('%s|%s' % (sp, sd))
            if not x or not x.get('n'): continue
            fill = (fill_good if x['avg_excess'] > 0 else fill_bad) if sp == 'test' else None
            r = put(ws, r, ['', fz['tf'], PER[sp], sd, x['n']] + x['hit'] + [x['avg_excess'], x['se']], sp == 'test', {5: '#,##0', 6: '0.0', 7: '0.0', 8: '0.0', 9: '0.0', 10: '+0.00;-0.00', 11: '0.0'}, fill)
r = note(ws, r + 1, 'Verdict: C1 (main) failed: longs +2.3, shorts -3.2, overall -0.4 in the test (it was +4.5 and +5.4 before). Its long side held its sign in '
         'all three periods (+5.0 / +9.2 / +2.3) but the test value is below one standard error, so it is not confirmed. The opening-range and sweep rules failed '
         '(-1.3 and -0.4). The time-of-day reference stayed slightly positive (+0.7 on 15-minute) but far below its 2023-2025 size.', N, f_bold, fill_key)

# ======================================================================== 4 Time of day
ws = wb.create_sheet('4 Time of day'); widths(ws, [16, 11, 11, 11, 11, 11, 15, 30]); N = 8
r = explain(ws, N, '4. Time of day (New York time): the one real pattern', [
    'For every 15-minute candle, a long and a short at market with a 1.8 ATR stop. Number = how much better longs did than shorts at that New York hour, minus '
    'the average of that period (so gold\'s overall rise or fall is removed), in points (average over TP1-TP4).'],
    ['Green = longs did better at that hour, red = shorts did better. A real pattern shows the same colour in most years. New York time follows US summer '
     'time; gold is closed 17:00-18:00 New York.',
     'Longs were favoured 13:00-17:00 and shorts 07:00-10:00 in most years, strongest in 2023-2025; in the test months the pattern was much weaker.'])
PERS = ['2021', '2022', '2023', '2024', '2025 H1', 'test 25H2-26']
r = header(ws, r, ['New York hour', '2021', '2022', '2023', '2024', '2025 H1', 'TEST Jul 2025 - Oct 2026', 'Note'])
r0 = r
NOTES = {7: 'London morning / US premarket', 8: 'US data 08:30', 9: 'US stock open 09:30', 13: 'after the London close', 16: 'last hour before the close',
         17: 'market closed', 18: 'reopen (Asia evening)'}
for h in range(24):
    vals = [D['season'][p][h] for p in PERS]
    r = put(ws, r, ['%02d:00' % h] + [None if v is None else round(v, 1) for v in vals] + [NOTES.get(h, '')], False, {k: '+0.0;-0.0;0.0' for k in range(2, 8)})
rng = 'B%d:G%d' % (r0, r - 1)
ws.conditional_formatting.add(rng, CellIsRule(operator='greaterThan', formula=['1.5'], fill=fill_good))
ws.conditional_formatting.add(rng, CellIsRule(operator='lessThan', formula=['-1.5'], fill=fill_bad))

# ======================================================================== 5 Why the retest limit
ws = wb.create_sheet('5 Why the retest limit'); widths(ws, [10, 58, 10, 10, 10, 10, 10]); N = 7
r = explain(ws, N, '5. Why the retest (pullback) entry cannot add accuracy', [
    'The same signals entered two ways: at the indicator\'s retest limit (as now) and at market at the signal close (same 1.8 ATR stop), all periods together. '
    'The market entries are then split by whether the limit would have filled.'],
    ['When the limit fills (the price came back), the move had already weakened: entered at the close those trades hit TP1 only about 50 % of the time. The '
     'signals whose limit never fills (the price ran away) would have hit TP1 about 95 % of the time, but the limit never gets them. Overall both ways end '
     'at the random level: the pullback entry picks the weaker half by design (adverse selection).'])
r = header(ws, r, ['Timeframe', 'Entry', 'Trades', 'TP1 %', 'TP2 %', 'TP3 %', 'TP4 %'])
for tf in ('M5', 'M15', 'H1'):
    a = D['adverse'][tf]
    for key, lab in (('limit_filled', 'At the retest limit (as the indicator), filled trades'), ('market_all', 'At market at the signal close, every signal'),
                     ('market_if_filled', '   ... of these: signals whose limit DID fill'), ('market_if_not_filled', '   ... of these: signals whose limit never filled')):
        h, n = a[key]
        r = put(ws, r, [tf, lab, n] + h, key == 'market_if_not_filled', {3: '#,##0', 4: '0.0', 5: '0.0', 6: '0.0', 7: '0.0'})
    r += 1

# ======================================================================== 6 What to do
ws = wb.create_sheet('6 What to do'); widths(ws, [150]); N = 1
r = explain(ws, N, '6. What to do with this', ['Practical conclusions from the research for trading the indicator, the strategy and the EA.'],
            ['Each point stands on its own; the numbers come from sheets 1-5 and the earlier gold workbooks.'])
for t in (
    '1. Judge any setting against random, not against 50 %. With these targets random entries hit 62.5 / 50 / 40 / 33.3 %. A setting is better only if its hit rates '
    'are above these by more than luck (about 50 / sqrt(trades) points: 400 trades +-2.5, 1,000 trades +-1.6). A 62 % TP1 is the coin-flip level, not an edge.',
    '2. Moving the targets closer or the stop wider raises the hit rate but not the edge: a 0.3 R target is hit 77 % of the time by random entries, and each win '
    'pays less. Only the hit rate ABOVE random at the same targets is an edge.',
    '3. What does change your results is the cost per trade. On 5-minute candles the spread costs about 0.07 R per trade with a 1.8 ATR stop, on 1-minute 0.17 R, '
    'plus $7 commission per lot. With a stop twice as wide the same spread and commission cost half as much in R. That is why the earlier gold settings that made '
    'money used 2.2-4 ATR stops and why 1-minute is the hardest timeframe.',
    '4. Money management cannot create an edge. Loss recovery rules (Crooks C and others) change the size of the trades, not the odds; gold wins do not cluster '
    '(earlier study), so recovery trades lose as often as any trade. The monthly lock and hard caps limit the damage; they do not raise the accuracy.',
    '5. The New York time pattern (weaker 07:00-10:00, stronger 13:00-17:00) is real but changed size from year to year and was weak in the latest 15 months. '
    'Use it as background knowledge, not as a fixed filter.',
    '6. Your v4.0 settings were at the random level in 2021-2025 and a few points above it in the latest 15 months (sheet 1, 625 trades on 5-minute): that is within '
    'normal luck for that many trades, so expect random-level accuracy in the future too.',
    '7. Order flow does not help on gold CFD data: tick-volume profile levels, estimated delta and cumulative delta, absorption, exhaustion and low-volume '
    'pullbacks did not separate the winning signals from the losing ones in the test months (sheet 7). Do not pay for or rely on order-flow add-ons for this.',
    '8. Optional, only if you want it (not done, because neither is a proven improvement): (a) an off-by-default experimental setting "buy after a bearish signal '
    '12:00-18:00 New York time" (the only idea whose direction held in all three periods: +5.0 / +9.2 / +2.3 points), to forward-test on a demo account for 3-6 '
    'months; (b) a "random" row in the TP table of the indicator and the EA, so every backtest shows the no-edge rate next to the hit rates.'):
    r = note(ws, r, t, N)

# ======================================================================== 7 Order flow
ws = wb.create_sheet('7 Order flow'); widths(ws, [40, 11, 26, 8, 8, 8, 8, 8, 8, 13, 10]); N = 11
r = explain(ws, N, '7. Order flow: does it find the false signals and the winners?', [
    'Your question: do order-flow concepts (POC, value area, LVN / HVN, delta, cumulative delta, absorption, exhaustion ...) combined with the signals tell the '
    'losing signals from the winning ones, or give better entries? Two research agents tested it in parallel (about 940 variants), with the same rules as '
    'sheets 1-3: found on 2021 - June 2025, the best written down, then tested once on July 2025 - October 2026.',
    'Data limit: gold CFD (FxPro, OANDA) has TICK volume only, no real buy / sell (bid / ask) volume. Delta and cumulative delta were estimated from the '
    '1-minute candles (up-minute volume minus down-minute volume, and a close-location version); the volume profile spreads each minute\'s tick volume over '
    'its range ($0.50 rows, per session). This is also what TradingView\'s order-flow tools show on XAUUSD.'],
    ['What failed (every timeframe, both periods or the test): signal-candle delta and delta %, cumulative delta trend and divergence, absorption (big volume, '
     'small range), exhaustion / climax volume, low-volume ("no supply") pullbacks and pullback delta as cancel rules, entry / stop / targets inside or outside '
     'the previous value area, near the POC, at an LVN or HVN, LVN or HVN on the way to TP1-TP4, failed auctions and the 80 % rule, LVN breakouts and '
     'rejections, POC reversion and migration, delta flips after sweeps, initial-balance breakouts with delta. Machine learning with 40 order-flow features '
     'added: score 0.50-0.51 (coin flip), the same as without them.',
     'The table: the 4 finalists on all three periods; TEST rows green = above random, red = below. Pass rule (written before the test): above random for longs '
     'AND shorts, by at least one standard error overall, at 3 of the 4 targets. None passed.'])
OFRULES = {
    'OFA-C1 narrow prior value area': 'Filter on the signals (5-minute): take a signal only if the previous session\'s value area was narrow (VAH - VAL <= 7.5 ATR)',
    'OFA-C1b narrow prior range (no volume)': 'The same with the previous session\'s high - low <= 16.8 ATR: no volume needed (control)',
    'OFB-C3 fade extension from POC': 'Entry (5-minute): the signal points away from the developing POC while price is >= 5.8 ATR from it -> take the OPPOSITE trade at market',
    'OFB-C1L long far below POC': 'Entry (5-minute): price >= 8.6 ATR below the developing POC -> buy at market (long only)',
}
r = header(ws, r, ['Rule', 'Timeframe', 'Period', 'Side', 'Trades', 'TP1 %', 'TP2 %', 'TP3 %', 'TP4 %', 'Excess (pts)', 'se'])
for fz in D['of_finalists']:
    r = note(ws, r, OFRULES.get(fz['name'], fz['name']), N, f_bold, fill_sec)
    sides = ('long',) if 'long far' in fz['name'] else ('long', 'short', 'both')
    for sp in ('train', 'valid', 'test'):
        for sd in sides:
            x = fz['res'].get('%s|%s' % (sp, sd))
            if not x or not x.get('n'): continue
            fill = (fill_good if x['avg_excess'] > 0 else fill_bad) if sp == 'test' else None
            r = put(ws, r, ['', fz['tf'], PER[sp], sd, x['n']] + x['hit'] + [x['avg_excess'], x['se']], sp == 'test',
                    {5: '#,##0', 6: '0.0', 7: '0.0', 8: '0.0', 9: '0.0', 10: '+0.00;-0.00', 11: '0.0'}, fill)
r = note(ws, r + 1, 'Verdict: order flow built from tick volume does not find the false signals or the winners. The two order-flow entries fell to -1.8 and -2.1 '
         'below random in the test. The only effect whose sign held is not order flow: signals after a NARROW previous session were about +0.8 points better '
         'in the test (+1 to +4 before), the same with or without volume, too small to matter after costs.', N, f_bold, fill_key)

for w in wb.worksheets:
    w.sheet_view.showGridLines = False
    w.freeze_panes = None
out = S + '/Gold_Entry_Accuracy_Research.xlsx'; wb.save(out); print('saved', out, wb.sheetnames)
