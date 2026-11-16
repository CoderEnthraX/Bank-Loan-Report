"""Gold_Best_Monthly_Settings_1000.xlsx: the best settings for each calendar month 2021 - 2 Oct 2026 with a fresh $1,000 every month, for the
Auction Retest strategy and the Fractal Breakout Grid (asked 2026-11-16). From mcej3/picks.pkl, combo.pkl, final.pkl, final_150.pkl.
Usage: build_best_xlsx.py OUT.xlsx"""
import sys, pickle, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
OUT = sys.argv[1]
P = pickle.load(open(S + '/mcej3/picks.pkl', 'rb')); C = pickle.load(open(S + '/mcej3/combo.pkl', 'rb'))
F3 = pickle.load(open(S + '/mcej3/final.pkl', 'rb')); F15 = pickle.load(open(S + '/mcej3/final_150.pkl', 'rb'))
M = pickle.load(open(S + '/mcej3/money_meta.pkl', 'rb')); MONTHS = M['months']
F = 'Arial'
fn = Font(name=F, size=10); fb = Font(name=F, size=10, bold=True); ft = Font(name=F, size=14, bold=True); fh = Font(name=F, size=10, bold=True, color='FFFFFF')
fnote = Font(name=F, size=9, italic=True, color='404040'); fblk = Font(name=F, size=11, bold=True, color='1F3864'); fblue = Font(name=F, size=10, color='0000FF')
fgreen = Font(name=F, size=10, color='008000')
H1 = PatternFill('solid', fgColor='1F3864'); H2 = PatternFill('solid', fgColor='2F5597'); REC = PatternFill('solid', fgColor='E2EFDA'); ALT = PatternFill('solid', fgColor='FCE4D6')
STAT = PatternFill('solid', fgColor='F2F2F2')
CEN = Alignment(horizontal='center', vertical='center', wrap_text=True); LEFT = Alignment(horizontal='left', vertical='top', wrap_text=True)
USD = '$#,##0;[Red]-$#,##0'; CNT = '0'


def mdate(m): return dt.date(int(m[:4]), int(m[5:]), 1)


# ------------------------------------------------------------------ the options shown (recommended first)
def full(c):
    sc = c['sc']; o = {}
    for v in ('cal', 'mid', 'cost'):
        a, b = sc[v]['IN'], sc[v]['OUT']
        o[v] = dict(lose=a['lose'] + b['lose'], prof=a['prof'] + b['prof'], total=a['total'] + b['total'], worst=min(a['worst'], b['worst']), dd=max(a['dd'], b['dd']))
    return o


cm = C['safe + balanced']
OPTS = [
    dict(key='combo', tier='RECOMMENDED', short='Both: 50 % Auction Retest + 50 % Grid', strat='Auction Retest M15-S3 ($500) + Grid S7+S8+S10 ($500)',
         money="ARS: Oscar's Grind, base $5, month lock +$10 | Grid: Exact recovery, base $5, cap $50 Clamp", monthly=cm['monthly'], dd=max(cm['dd']),
         mid=(cm['sum']['mid']['ALL']['lose'], cm['sum']['mid']['ALL']['worst']), cost=None, why='The steadiest months: the two strategies rarely lose in the same month.'),
    dict(key='grid_bal', tier='RECOMMENDED', short='Fractal Grid: S7 + S8 + S10', c=P['grid_bal'], strat='Grid strategies 7, 8, 10 (M1 model = the grid EA)',
         money='Exact recovery at final TP, base $10, hard cap $100 Clamp, $333 per strategy', why='Best grid setting with every drop inside a month under $300 in 2021-23.'),
    dict(key='grid_safe', tier='RECOMMENDED', short='Fractal Grid safe: 6 strategies', c=P['grid_safe'], strat='Grid strategies 1, 2, 6, 7, 8, 10',
         money='Exact recovery at final TP, base $5, hard cap $50 Clamp, $167 per strategy', why='Best grid setting with every drop under $150: the smallest losses.'),
    dict(key='ars_safe', tier='RECOMMENDED', short="Auction Retest: M15-S3, Oscar's Grind", c=P['ars_safe'], strat='Auction Retest M15-S3 (gold M15), force-close off',
         money="Oscar's Grind, base $10, no cap, stop for the month at +$20", why='Best Auction Retest setting with every drop under $150 in 2021-23.'),
    dict(key='ars_norec', tier='RECOMMENDED', short='Auction Retest: M15-S3, no recovery', c=P['ars_norec'], strat='Auction Retest M15-S3 (gold M15), force-close off',
         money='No recovery, $20 a trade, stop for the month at +$20', why='The simplest: no recovery at all.'),
    dict(key='grid_aggr', tier='higher risk', short='Grid aggressive: S8 + S10', c=P['grid_aggr'], strat='Grid strategies 8, 10', money='Exact recovery, base $20, no cap, $500 per strategy',
         why='Fewest losing calendar months, but a -$503 mid-month window: calendar luck.'),
    dict(key='grid_norec', tier='higher risk', short='Grid: all 12, no recovery', c=P['grid_norec'], strat='Grid strategies 1 - 12', money='No recovery, $10 a trade, $83 per strategy',
         why='Most profit with a fixed risk, but a third of the months lose (small losses).'),
    dict(key='ars_aggr', tier='higher risk', short='Auction Retest aggressive: M15-S6', c=P['ars_aggr'], strat='Auction Retest M15-S6, force-close off',
         money='Recover all on the next trade, base $20, no cap, lock +$50', why='Fewest losing months in 2021-23, but a -$972 month in the test period.'),
    dict(key='ars_bal', tier='higher risk', short='Auction Retest: M1-S2 Fibonacci', c=P['ars_bal'], strat='Auction Retest M1-S2 (gold M1), force-close off',
         money='Fibonacci, base $5, no cap, lock +$20', why='0 losing months in 2021-23 even under stress, then -$881 in one test month.'),
    dict(key='ars_you', tier='your settings', short='Your settings: best money', c=P['ars_you'], strat='Your Auction Retest settings, M15, your filters, TP1',
         money='Exact recovery, base $5, cap $100 Start again, lock +$20', why='The best money setting for your current settings: about break-even.'),
]
for o in OPTS:
    if 'c' in o:
        f_ = full(o['c']); o['monthly'] = o['c']['sc']['cal']['monthly']; o['dd'] = f_['cal']['dd']; o['mid'] = (f_['mid']['lose'], f_['mid']['worst'])
        o['cost'] = (f_['cost']['lose'], f_['cost']['total'])

wb = Workbook(); rd = wb.active; rd.title = 'Read me'
# ------------------------------------------------------------------ Monthly
mo = wb.create_sheet('Monthly'); mo.sheet_properties.tabColor = '2F5597'
mo['A1'] = 'Profit / loss of every month ($): each month starts again with $1,000 and a fresh money state (gold, IST calendar months)'; mo['A1'].font = ft
mo['A2'] = ('Green columns = recommended, orange = higher risk or your settings. Values from the simulation (each trade in the month it started); the rows '
            'under the months are formulas. Choice period = 2021-23 (the settings were chosen on these months only), test period = 2024-26.'); mo['A2'].font = fnote
HR = 4; FIRST = 6; LAST = FIRST + len(MONTHS) - 1; CH0, CH1, TE0 = FIRST, FIRST + 35, FIRST + 36
c = mo.cell(HR, 1, 'Month'); c.font = fh; c.fill = H1; c.alignment = CEN; mo.cell(HR + 1, 1).fill = H1
mo.merge_cells(start_row=HR, start_column=1, end_row=HR + 1, end_column=1)
mo.column_dimensions['A'].width = 12
for j, o in enumerate(OPTS):
    col = 2 + j; o['col'] = col
    c = mo.cell(HR, col, o['short']); c.font = fh; c.fill = H1 if o['tier'] == 'RECOMMENDED' else H2; c.alignment = CEN
    c = mo.cell(HR + 1, col, o['tier']); c.font = Font(name=F, size=8, bold=True, color='FFFFFF'); c.fill = H1 if o['tier'] == 'RECOMMENDED' else H2; c.alignment = CEN
    mo.column_dimensions[L(col)].width = 15
mo.row_dimensions[HR].height = 42
for i, m in enumerate(MONTHS):
    r = FIRST + i
    c = mo.cell(r, 1, mdate(m)); c.number_format = 'mmm yyyy'; c.font = fn; c.alignment = Alignment(horizontal='left')
    if m == '2026-10': c.comment = None
    for o in OPTS:
        c = mo.cell(r, o['col'], float(o['monthly'][i])); c.number_format = USD; c.font = fn
        c.fill = REC if o['tier'] == 'RECOMMENDED' else ALT
STATS = [('Months in profit (all 70)', 'COUNTIF({r},">0")', CNT, (FIRST, LAST)), ('Months in loss (all 70)', 'COUNTIF({r},"<0")', CNT, (FIRST, LAST)),
         ('Total 2021 - 2026', 'SUM({r})', USD, (FIRST, LAST)), ('Average month', 'AVERAGE({r})', USD, (FIRST, LAST)), ('Worst month', 'MIN({r})', USD, (FIRST, LAST)),
         ('Best month', 'MAX({r})', USD, (FIRST, LAST)),
         ('Choice 2021-23: months in loss', 'COUNTIF({r},"<0")', CNT, (CH0, CH1)), ('Choice 2021-23: total', 'SUM({r})', USD, (CH0, CH1)),
         ('Test 2024-26: months in loss', 'COUNTIF({r},"<0")', CNT, (TE0, LAST)), ('Test 2024-26: total', 'SUM({r})', USD, (TE0, LAST)),
         ('Test 2024-26: worst month', 'MIN({r})', USD, (TE0, LAST))]
SROW = {}
r = LAST + 2
for lab, fml, fm, (a, b) in STATS:
    c = mo.cell(r, 1, lab); c.font = fb; c.fill = STAT; c.alignment = Alignment(wrap_text=True)
    for o in OPTS:
        rng = '%s%d:%s%d' % (L(o['col']), a, L(o['col']), b)
        c = mo.cell(r, o['col'], '=' + fml.format(r=rng)); c.font = fb; c.fill = STAT; c.number_format = fm
    SROW[lab] = r; mo.row_dimensions[r].height = 26; r += 1
mo.freeze_panes = mo.cell(FIRST, 2)
mo.conditional_formatting.add('B%d:%s%d' % (FIRST, L(1 + len(OPTS)), LAST), CellIsRule(operator='lessThan', formula=['0'], font=Font(name=F, size=10, color='C00000', bold=True)))

# ------------------------------------------------------------------ Recommendations (summary, linked to Monthly)
rc = wb.create_sheet('Recommendations', 1); rc.sheet_properties.tabColor = '548235'
rc['A1'] = 'Best settings with a fresh $1,000 every month - how many months made money and how many lost (gold, Jan 2021 - 2 Oct 2026, 70 months)'; rc['A1'].font = ft
rc['A2'] = ('Green = recommended. Chosen on 2021-23 only, tested on 2024-26. Counts and totals are formulas linked to the "Monthly" sheet; the drop inside '
            'a month, the mid-month windows and the cost test are from the simulation.'); rc['A2'].font = fnote
hd = ['Option', 'Strategy', 'Money settings', 'Months in profit', 'Months in loss', 'Total 70 months ($)', 'Average month ($)', 'Worst month ($)',
      'Deepest drop inside a month ($)', 'Choice 2021-23: months in loss', 'Choice 2021-23: total ($)', 'Test 2024-26: months in loss', 'Test 2024-26: total ($)',
      'Test 2024-26: worst month ($)', 'Mid-month windows: losing (of 69)', 'Mid-month windows: worst ($)', 'Costs +0.07: months in loss', 'Costs +0.07: total ($)', 'Why']
widths = [30, 34, 46, 9, 9, 12, 11, 11, 12, 11, 12, 11, 12, 12, 12, 12, 11, 12, 60]
for j, (t, w) in enumerate(zip(hd, widths)):
    c = rc.cell(4, 1 + j, t); c.font = fh; c.fill = H1; c.alignment = CEN; rc.column_dimensions[L(1 + j)].width = w
rc.row_dimensions[4].height = 54
LINK = {4: 'Months in profit (all 70)', 5: 'Months in loss (all 70)', 6: 'Total 2021 - 2026', 7: 'Average month', 8: 'Worst month', 10: 'Choice 2021-23: months in loss',
        11: 'Choice 2021-23: total', 12: 'Test 2024-26: months in loss', 13: 'Test 2024-26: total', 14: 'Test 2024-26: worst month'}
for i, o in enumerate(OPTS):
    r = 5 + i; fill = REC if o['tier'] == 'RECOMMENDED' else ALT
    vals = {1: o['short'], 2: o['strat'], 3: o['money'], 9: round(o['dd'], 2), 15: o['mid'][0], 16: round(o['mid'][1], 2),
            17: o['cost'][0] if o['cost'] else '-', 18: round(o['cost'][1], 2) if o['cost'] else '-', 19: o['why']}
    for col in range(1, 20):
        if col in LINK:
            c = rc.cell(r, col, "='Monthly'!%s%d" % (L(o['col']), SROW[LINK[col]])); c.font = fgreen
            c.number_format = CNT if 'months' in LINK[col].lower() else USD
        else:
            c = rc.cell(r, col, vals[col]); c.font = fb if col == 1 else fn
            if col in (9, 16, 18): c.number_format = USD
            if col in (15, 17): c.number_format = CNT
        c.fill = fill; c.alignment = LEFT if col in (1, 2, 3, 19) else Alignment(horizontal='center', vertical='top')
    rc.row_dimensions[r].height = 40
rc.freeze_panes = 'B5'
r = 5 + len(OPTS) + 1
notes = [
    'How to read: "Months in profit / loss" counts the 70 months (each starting at $1,000). "Deepest drop inside a month" = how far the balance fell below the month\'s best '
    'point before the month ended: this is the risk the monthly totals hide.',
    'Mid-month windows (15th to 14th) and +0.07 costs are stress tests: a setting whose good calendar months are luck shows it there (e.g. the aggressive grid: '
    '4 losing calendar months but a -$503 mid-month window).',
    'Recovery rules with a monthly lock make most months small wins, but a bad streak inside a month can cost most of the $1,000 (see the orange options).',
]
for t in notes:
    c = rc.cell(r, 1, t); c.font = fnote; rc.merge_cells(start_row=r, start_column=1, end_row=r, end_column=19); c.alignment = LEFT; rc.row_dimensions[r].height = 26; r += 1

# ------------------------------------------------------------------ How to set
hs = wb.create_sheet('How to set', 2); hs.sheet_properties.tabColor = 'BF8F00'
hs['A1'] = 'How to set each recommended option (TradingView input title / EA input name / value)'; hs['A1'].font = ft
hs.column_dimensions['A'].width = 34; hs.column_dimensions['B'].width = 58; hs.column_dimensions['C'].width = 26; hs.column_dimensions['D'].width = 22
ARS_ENGINE = [('Chart', '-', 'gold M15'),
              ('Stop Distance (x ATR)', 'InpStopAtr', '4.0'), ('Half Stop (x ATR)', 'InpHalfStopAtr', '1.2'),
              ('Half Stop Never Wider Than The Normal Stop', 'InpHalfCap', 'off'),
              ('Skip When The 1h EMA20 Moved More Than (ATR In 3 Hours)', 'InpEmaOn / InpEmaMax', 'on, 1.2'), ('VWAP Slope Bars', 'InpSlopeBars', '0'),
              ('Max Fills Per Day', 'InpMaxFills', '5'), ('Final Exit At', 'InpExitAt', 'TP4 (2.0R)'), ('When TP3 Hits, Move Stop To (R)', 'InpMv3On / InpMv3R', 'on, 1.0'),
              ('Trade Only On The Ticked Days', 'InpDayOn', 'off'), ('Trade Only Between', 'InpHoursOn', 'off'), ('Trade Only In Kill Zones', 'InpKzOn', 'off'),
              ('Daily News Window', 'InpDNewsOn', 'off'), ('Force-Close Open Trades At', 'InpFcOn', 'off'), ('Close Open Trades When Saturday Starts', 'InpWeekendOn', 'on (default)')]
blocks = [
    ('Auction Retest: M15-S3, Oscar\'s Grind (recommended)', ARS_ENGINE + [
        ('Position Size', 'InpSizeMode', 'Fixed $ risk'), ('Base Risk Per Trade ($)', 'InpBaseRisk', '10'), ('Loss Recovery', 'InpRec', "Oscar's Grind"),
        ('Hard Cap', 'InpCapOn', 'off'), ('Stop For The Month Once It Is Up ($)', 'InpMLockOn / InpMLockAmt', 'on, 20'),
        ('Restart The Loss Recovery On The 1st Of Each Month', 'InpMRestart', 'on'), ('Everything else', '-', 'your current defaults (spread 0.16, commission 7, earn-back on, 1:100)')]),
    ('Auction Retest: M15-S3, no recovery (recommended, simplest)', [('Engine settings', '-', 'as above (M15-S3)'), ('Position Size / Base Risk', 'InpSizeMode / InpBaseRisk', 'Fixed $ risk, 20'),
        ('Loss Recovery', 'InpRec', 'Off'), ('Stop For The Month Once It Is Up ($)', 'InpMLockOn / InpMLockAmt', 'on, 20')]),
    ('Fractal Grid: S7 + S8 + S10 (recommended)', [
        ('Chart', '-', 'EA: any gold chart (it runs on 1-minute bars); TradingView: gold M1 chart'),
        ('Strategies on', 'InpS1On ... InpS12On', 'only 7, 8 and 10 on'), ('Strategy settings and options', '-', 'the defaults (unchanged)'),
        ('Start Balance ($) (each strategy)', 'InpStartB', '333.33 ($1,000 / 3)'), ('Position Size / Base Risk', 'InpSizeMode / InpBaseRisk', 'Fixed $ risk, 10'),
        ('Hard Cap', 'InpCapOn / InpHardCap / InpCapAction', 'on, 100, Clamp'), ('Loss Recovery', 'InpRec', 'Exact recovery at final TP'),
        ('Costs / leverage', 'InpCost... / InpLev', 'defaults (0.23 per oz, 1:100)')]),
    ('Fractal Grid safe: 6 strategies (recommended, smallest losses)', [('Strategies on', 'InpS1On ... InpS12On', 'only 1, 2, 6, 7, 8 and 10 on'),
        ('Start Balance ($) (each strategy)', 'InpStartB', '166.67 ($1,000 / 6)'), ('Base Risk', 'InpBaseRisk', '5'), ('Hard Cap', 'InpCapOn / InpHardCap / InpCapAction', 'on, 50, Clamp'),
        ('Loss Recovery', 'InpRec', 'Exact recovery at final TP')]),
    ('Both strategies: $500 + $500 (recommended, steadiest)', [('Auction Retest', 'as the Oscar\'s Grind option', 'Base Risk 5, month lock +$10, balance $500'),
        ('Fractal Grid', 'as the S7 + S8 + S10 option', 'Start Balance 166.67 each, Base Risk 5, Hard Cap 50 Clamp')]),
    ('Every month', [('Start again on the 1st', '-', 'Withdraw / top up to $1,000; Auction Retest: the monthly restart above does the money state; Grid EA: '
                     'remove and attach it again with "Continue after a restart" (InpRemember) off so its money state starts fresh (the grid has no monthly restart option yet)')]),
]
r = 3
for title, rows in blocks:
    c = hs.cell(r, 1, title); c.font = fblk; r += 1
    for j, t in enumerate(('Setting (TradingView)', 'EA input', 'Value')):
        c = hs.cell(r, 1 + j, t); c.font = fh; c.fill = H1; c.alignment = CEN
    r += 1
    for a, b, v in rows:
        hs.cell(r, 1, a).font = fn; hs.cell(r, 2, b).font = fn; c = hs.cell(r, 3, v); c.font = fblue
        for col in (1, 2, 3): hs.cell(r, col).alignment = LEFT
        hs.row_dimensions[r].height = 14 if len(v) < 40 else 40
        r += 1
    r += 1

# ------------------------------------------------------------------ Top lists
tl = wb.create_sheet('Top lists'); tl.sheet_properties.tabColor = '7F7F7F'
tl['A1'] = 'The best candidates of each rule, with their test-period results (how well the choice held up)'; tl['A1'].font = ft
tl['A2'] = ('Rule = in 2021-23, in calendar months, mid-month windows and +0.07 costs: no blown window and every drop inside a window under the limit; then the '
            'fewest losing windows, then the most profit. The test columns were never used to choose.'); tl['A2'].font = fnote
cols = ['Setting', 'Choice: losing (cal / mid / cost)', 'Choice: total ($)', 'Choice: deepest drop ($)', 'Test: months in loss', 'Test: total ($)', 'Test: worst month ($)',
        'Test: deepest drop ($)', 'All 70: months in profit', 'All 70: months in loss']
tl.column_dimensions['A'].width = 78
for j in range(1, len(cols)): tl.column_dimensions[L(1 + j)].width = 13
r = 4
for title, lst in (('Auction Retest, drop limit $150', F15['ARS']['good']), ('Auction Retest, drop limit $300', F3['ARS']['good']),
                   ('Fractal Grid, drop limit $150', F15['GRID']['good']), ('Fractal Grid, drop limit $300', F3['GRID']['good'])):
    c = tl.cell(r, 1, title); c.font = fblk; r += 1
    for j, t in enumerate(cols):
        c = tl.cell(r, 1 + j, t); c.font = fh; c.fill = H1; c.alignment = CEN
    tl.row_dimensions[r].height = 40; r += 1
    for cnd in lst[:20]:
        sc = cnd['sc']; o = full(cnd)
        vals = [cnd['name'], '%d / %d / %d' % (sc['cal']['IN']['lose'], sc['mid']['IN']['lose'], sc['cost']['IN']['lose']), sc['cal']['IN']['total'], sc['cal']['IN']['dd'],
                sc['cal']['OUT']['lose'], sc['cal']['OUT']['total'], sc['cal']['OUT']['worst'], sc['cal']['OUT']['dd'], o['cal']['prof'], o['cal']['lose']]
        for j, v in enumerate(vals):
            c = tl.cell(r, 1 + j, round(v, 2) if isinstance(v, float) else v); c.font = fn
            c.number_format = USD if j in (2, 3, 5, 6, 7) else CNT if j in (4, 8, 9) else '@'
            if j: c.alignment = Alignment(horizontal='center')
        r += 1
    r += 1
tl.freeze_panes = 'B4'

# ------------------------------------------------------------------ Read me
o1 = OPTS[0]; g = OPTS[1]; gs = OPTS[2]; a1 = OPTS[3]; a2 = OPTS[4]
def cnt(o): v = o['monthly']; return sum(1 for x in v if x > 1e-9), sum(1 for x in v if x < -1e-9), sum(v), min(v)
rows = [
    ('#title', 'Best monthly settings on gold with a fresh $1,000 every month: Auction Retest and Fractal Breakout Grid'),
    ('The question', 'Which settings give the most profit and the smallest losses in each calendar month (1st to the month end), every month from January 2021 to '
                     '2 October 2026 (70 months), starting every month with $1,000, for both strategies, including combinations; and how many months made money '
                     'and how many lost.'),
    ('Sheets', 'Recommendations: the options, their months in profit / in loss and the risk numbers. Monthly: every month of every option (counts as formulas). '
               'How to set: the exact inputs. Top lists: the best candidates of each rule and how they did in the test period.'),
    ('#h', 'The answer'),
    ('Steadiest: both together', 'Run both: $500 in the Auction Retest (M15-S3, Oscar\'s Grind) and $500 in the grid (strategies 7, 8, 10, exact recovery): %d months '
                                 'in profit, %d in loss, total %s, worst month %s.' % (*cnt(o1)[:2], '%+.0f' % cnt(o1)[2], '%+.0f' % cnt(o1)[3])),
    ('Fractal Grid', 'Strategies 7, 8 and 10, exact recovery at final TP, $10 base, hard cap $100 Clamp: %d in profit / %d in loss, total %+.0f, worst month %+.0f. '
                     'Smallest losses: strategies 1, 2, 6, 7, 8, 10 with $5: %d / %d, %+.0f, worst %+.0f.' % (*cnt(g), *cnt(gs))),
    ('Auction Retest', 'Catalogue strategy M15-S3 on gold M15 with the force-close off, Oscar\'s Grind, $10 base, stop for the month at +$20: %d / %d, %+.0f, worst '
                       '%+.0f. Without any recovery ($20 a trade, same lock): %d / %d, %+.0f, worst %+.0f.' % (*cnt(a1), *cnt(a2))),
    ('Your current settings', 'With your settings (TP1 0.6, your filters) even the best money setting is about break-even (%+.0f over 70 months): the costs eat the small '
                              'TP1 target (see the earlier workbooks).' % sum(OPTS[9]['monthly'])),
    ('#h', 'How it was done'),
    ('Trades', 'Auction Retest: the 19 catalogue strategies (with the force-close on and off) and your settings (M5 / M15 / H1, filters off / on, TP1 - TP4), each '
               'executed by the TradingView strategy model (your costs 0.16 + $7 per lot, earn-back targets, Saturday close; checked trade for trade against the '
               'engine). Grid: the 12 strategies on the M1 model (= the grid EA), costs 0.23.'),
    ('Money', 'Every month alone: $1,000, a fresh money state, the trades that start in the month. Searched: base $5 / $10 / $20; 38 loss-recovery rules (no recovery, '
              'Crooks C / E - J, the profit ladder with a $50 / $100 target, Exact recovery, Martingale, Labouchere, Fibonacci, D\'Alembert, Oscar\'s Grind, Rule C, ...); '
              'hard cap none / $50 / $100 (Clamp or Start again); Auction Retest also the monthly lock (none, +$20 ... +$150). Grid combinations: every subset of the '
              '12 strategies, each strategy its own share of the $1,000.'),
    ('Choosing', 'Only on 2021-23 (36 months); 2024-26 (34 months) is the test. A setting had to survive three versions of 2021-23 (calendar months, mid-month windows '
                 'from the 15th, costs +0.07) with no blown window and every drop inside a window below a limit ($150 or $300); then the fewest losing windows, then the '
                 'most profit. Without the drop limit, recovery rules with a monthly lock show almost no losing month, but lose most of the $1,000 in an unlucky month '
                 '(orange options).'),
    ('Checks', 'Trades: the strategy model takes exactly the engine\'s trades in all 62 Auction Retest sets (with earn-back and the time closes off). Money: '
               'gold/recovery.py (equal to the EA). The 5 recommended options were recomputed by an independent implementation from a written spec: all 70 months '
               'identical.'),
    ('Caveats', 'One price history (FxPro gold); the past does not guarantee the future; months in the test period are fewer and newer. No lot rounding. The grid has no '
                'monthly restart option yet (restart it by hand on the 1st, or ask for the option).'),
]
rd.column_dimensions['A'].width = 26; rd.column_dimensions['B'].width = 150
r = 1
for lab, txt in rows:
    if lab == '#title': c = rd.cell(r, 1, txt); c.font = ft; r += 1; continue
    if lab == '#h': r += 1; c = rd.cell(r, 1, txt); c.font = fblk; r += 1; continue
    a = rd.cell(r, 1, lab); a.font = fb; a.alignment = LEFT
    b = rd.cell(r, 2, txt); b.font = fn; b.alignment = LEFT
    rd.row_dimensions[r].height = 13 * (len(txt) // 150 + 1) + 2; r += 1
wb.save(OUT); print('saved', OUT)
