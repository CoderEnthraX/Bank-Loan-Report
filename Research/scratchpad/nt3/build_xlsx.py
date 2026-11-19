"""Workbook of the over-N-trades monthly test (nt3/results.pkl): Summary (settings + formulas), Monthly, two trade lists, Notes."""
import sys, pickle
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter as CL
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
OUT = sys.argv[1]
R = pickle.load(open(S + '/nt3/results.pkl', 'rb'))
months = R['months']; res = R['res']
F = 'Arial'
def font(**k): return Font(name=F, size=k.pop('size', 10), **k)
BLUE = '0000FF'; HDR = PatternFill('solid', fgColor='1F3864'); SUB = PatternFill('solid', fgColor='D9E1F2'); INP = PatternFill('solid', fgColor='FFFF00')
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD = '$#,##0.00;($#,##0.00);-'; PCT = '0.0%;(0.0%);-'; INT = '#,##0;(#,##0);-'
wb = Workbook()

# ------------------------------------------------------------------ Summary
ws = wb.active; ws.title = 'Summary'
ws['A1'] = 'Gold: Recover losses over N trades (N = 3), final exit TP1 = 0.2R, $20 base, every month on its own (Jan 2021 – Sep 2026)'
ws['A1'].font = font(bold=True, size=13)
ws['A2'] = 'Each calendar month starts with a fresh account on the 1st (your time zone, IST) and is traded to the end of the month. All money numbers in USD.'
ws['A2'].font = font(italic=True)
settings = [('Start balance each month ($)', 1000.0, USD, 'Your last test: a fresh $1,000 every month.'),
            ('Base amount ($)', 20.0, USD, 'Risk mode: the stop-out loss of a base trade. Profit mode: the win of a base trade at TP1.'),
            ('N (Recover losses over N trades)', 3, INT, 'Every trade adds 1/N of the unrecovered losses to the base.'),
            ('Final exit TP1 (R)', 0.2, '0.0"R"', 'TP1 is the final exit (no partial).'),
            ('Leverage (1:x)', 100, INT, 'Lots never above equity x 100 / (price x 100 oz).'),
            ('Costs per oz ($)', 0.23, USD, 'Spread 0.16 + $7 commission per lot (0.07 per oz); the TP1 target is pushed by them (earn-back).')]
ws['A4'] = 'Settings of the test (inputs)'; ws['A4'].font = font(bold=True)
for i, (k, v, fmt, note) in enumerate(settings):
    r = 5 + i
    ws.cell(r, 1, k).font = font(); c = ws.cell(r, 3, v); c.font = font(color=BLUE); c.number_format = fmt; c.fill = INP
    ws.cell(r, 4, note).font = font(italic=True, color='595959')
ws['A12'] = 'Trading rules (your EA settings)'; ws['A12'].font = font(bold=True)
rules = ['Tuesday, Wednesday and Thursday only; new trades 06:00–23:00 IST (none after 2 AM).',
         'Kill zones Asia, London and New York (London / New York time, so they move 1 hour in winter).',
         'Daily news window 17:45 IST for 30 min (New York time), no new trades 30 min before it; an open trade is closed when it starts.',
         'Force-close 23:55 IST every day; close when Saturday starts. Lots in 0.01 steps, rounded down, at least 0.01.',
         'Signals: the Auction Retest engine on M5 (your settings); exits checked on M1 like the EA\'s broker stop loss and take profit.']
for i, t in enumerate(rules): ws.cell(13 + i, 1, '• ' + t).font = font()

COLS = [('Over N=3, Risk ($20 lost at the stop)', 'Monthly', 'F', 'D', 'C', 'I'), ('Over N=3, Profit ($20 won at TP1)', 'Monthly', 'Q', 'O', 'N', 'T'),
        ('Fixed $20 risk (no recovery)', 'Monthly', 'Y', None, None, None), ('Fixed $20 win (no recovery)', 'Monthly', 'AB', None, None, None)]
r0 = 19
ws.cell(r0, 1, 'Results over the 69 months (formulas on the Monthly sheet)').font = font(bold=True)
hdr = r0 + 1
ws.cell(hdr, 1, 'Measure').font = font(bold=True, color='FFFFFF'); ws.cell(hdr, 1).fill = HDR
for j, (name, *_ ) in enumerate(COLS):
    c = ws.cell(hdr, 3 + j, name); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(wrap_text=True, horizontal='center')
N0, N1 = 3, 3 + len(months) - 1
rows = [('Total net profit ($)', lambda L: '=SUM(Monthly!%s%d:%s%d)' % (L, N0, L, N1), USD),
        ('Average month ($)', lambda L: '=AVERAGE(Monthly!%s%d:%s%d)' % (L, N0, L, N1), USD),
        ('Months tested', lambda L: '=COUNT(Monthly!%s%d:%s%d)' % (L, N0, L, N1), INT),
        ('Profitable months', lambda L: '=COUNTIF(Monthly!%s%d:%s%d,">0")' % (L, N0, L, N1), INT),
        ('Losing months', lambda L: '=COUNTIF(Monthly!%s%d:%s%d,"<0")' % (L, N0, L, N1), INT),
        ('Profitable months (%)', lambda L: None, PCT),
        ('Best month ($)', lambda L: '=MAX(Monthly!%s%d:%s%d)' % (L, N0, L, N1), USD),
        ('Worst month ($)', lambda L: '=MIN(Monthly!%s%d:%s%d)' % (L, N0, L, N1), USD),
        ('Months down more than $500', lambda L: '=COUNTIF(Monthly!%s%d:%s%d,"<-500")' % (L, N0, L, N1), INT)]
for i, (label, f, fmt) in enumerate(rows):
    r = hdr + 1 + i
    ws.cell(r, 1, label).font = font()
    for j, (name, sh, L, Lw, Lt, Lr) in enumerate(COLS):
        c = ws.cell(r, 3 + j)
        if label == 'Profitable months (%)':
            c.value = '=IF(%s%d>0,%s%d/%s%d,0)' % (CL(3 + j), hdr + 3, CL(3 + j), hdr + 4, CL(3 + j), hdr + 3)   # profitable / months tested
        else: c.value = f(L)
        c.number_format = fmt; c.font = font(); c.border = BOX
extra = hdr + 1 + len(rows)
for k, (label, kind) in enumerate([('Trades', 'trades'), ('Win rate (trades in profit)', 'win'), ('Biggest single-trade risk ($)', 'risk')]):
    r = extra + k; ws.cell(r, 1, label).font = font()
    for j, (name, sh, L, Lw, Lt, Lr) in enumerate(COLS):
        c = ws.cell(r, 3 + j)
        if Lt is None: c.value = 'same trades' if kind == 'trades' else '—'; c.font = font(color='808080'); c.alignment = Alignment(horizontal='center'); continue
        if kind == 'trades': c.value = '=SUM(Monthly!%s%d:%s%d)' % (Lt, N0, Lt, N1); c.number_format = INT
        elif kind == 'win': c.value = '=IF(SUM(Monthly!%s%d:%s%d)>0,SUM(Monthly!%s%d:%s%d)/SUM(Monthly!%s%d:%s%d),0)' % (Lt, N0, Lt, N1, Lw, N0, Lw, N1, Lt, N0, Lt, N1); c.number_format = PCT
        else: c.value = '=MAX(Monthly!%s%d:%s%d)' % (Lr, N0, Lr, N1); c.number_format = USD
        c.font = font(); c.border = BOX
yr0 = extra + 5
ws.cell(yr0, 1, 'Net profit and profitable months per year (each month on its own)').font = font(bold=True)
yh = yr0 + 1
heads = ['Year'] + sum([[n + ': net ($)', n + ': profitable months'] for n, *_ in COLS], [])
for j, h in enumerate(heads):
    c = ws.cell(yh, 1 + j if j == 0 else 2 + j, h); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(wrap_text=True, horizontal='center')
for i, y in enumerate(['2021', '2022', '2023', '2024', '2025', '2026']):
    r = yh + 1 + i; ws.cell(r, 1, y).font = font()
    for j, (name, sh, L, *_ ) in enumerate(COLS):
        c1 = ws.cell(r, 3 + 2 * j, '=SUMIFS(Monthly!%s%d:%s%d,Monthly!$B$%d:$B$%d,$A%d)' % (L, N0, L, N1, N0, N1, r)); c1.number_format = USD; c1.font = font(); c1.border = BOX
        c2 = ws.cell(r, 4 + 2 * j, '=COUNTIFS(Monthly!$B$%d:$B$%d,$A%d,Monthly!%s%d:%s%d,">0")' % (N0, N1, r, L, N0, L, N1)); c2.number_format = INT; c2.font = font(); c2.border = BOX
ws.cell(yh + 8, 1, '2026: January to September (the data end on 2 October 2026).').font = font(italic=True, color='595959')
ws.column_dimensions['A'].width = 34; ws.column_dimensions['B'].width = 2
for j in range(3, 12): ws.column_dimensions[CL(j)].width = 19
ws.column_dimensions['D'].width = 19
ws.row_dimensions[hdr].height = 30; ws.row_dimensions[yh].height = 44
ws.freeze_panes = 'A4'

# ------------------------------------------------------------------ Monthly
wm = wb.create_sheet('Monthly')
blocks = [('Over N=3, Risk ($20 lost at the stop)', ('split', 'risk'), 3), ('Over N=3, Profit ($20 won at TP1)', ('split', 'profit'), 14)]
sub = ['Trades', 'Wins', 'Win %', 'Net ($)', 'Return %', 'Max drawdown ($)', 'Biggest risk ($)', 'Biggest lots', 'Worst trade ($)', 'Longest losing run', 'End balance ($)']
wm.cell(1, 1, 'Month').font = font(bold=True, color='FFFFFF'); wm.cell(1, 1).fill = HDR
wm.cell(1, 2, 'Year').font = font(bold=True, color='FFFFFF'); wm.cell(1, 2).fill = HDR
for name, key, c0 in blocks:
    wm.merge_cells(start_row=1, start_column=c0, end_row=1, end_column=c0 + len(sub) - 1)
    c = wm.cell(1, c0, name); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(horizontal='center')
    for j, h in enumerate(sub):
        c = wm.cell(2, c0 + j, h); c.font = font(bold=True); c.fill = SUB; c.alignment = Alignment(wrap_text=True, horizontal='center'); c.border = BOX
for name, key, c0 in (('Fixed $20 risk (no recovery)', ('fixed', 'risk'), 25), ('Fixed $20 win (no recovery)', ('fixed', 'profit'), 28)):
    wm.merge_cells(start_row=1, start_column=c0, end_row=1, end_column=c0 + 2)
    c = wm.cell(1, c0, name); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(horizontal='center')
    for j, h in enumerate(['Net ($)', 'Return %', 'Max drawdown ($)']):
        c = wm.cell(2, c0 + j, h); c.font = font(bold=True); c.fill = SUB; c.alignment = Alignment(wrap_text=True, horizontal='center'); c.border = BOX
for c in (1, 2):
    wm.cell(2, c).fill = SUB; wm.cell(2, c).border = BOX
for i, (y, m) in enumerate(months):
    r = 3 + i
    wm.cell(r, 1, '%04d-%02d' % (y, m)).font = font(); wm.cell(r, 2, str(y)).font = font()
    for name, key, c0 in blocks:
        st = res[key][(y, m)][1]
        vals = [(st['n'], INT), (st['wins'], INT), (None, PCT), (round(st['net'], 2), USD), (None, PCT), (round(st['mdd'], 2), USD),
                (round(st['maxRisk'], 2), USD), (st['maxLots'], '0.00'), (round(st['worst'], 2), USD), (st['lrun'], INT), (None, USD)]
        for j, (v, fmt) in enumerate(vals):
            c = wm.cell(r, c0 + j); c.number_format = fmt; c.border = BOX
            if j == 2: c.value = '=IF(%s%d>0,%s%d/%s%d,0)' % (CL(c0), r, CL(c0 + 1), r, CL(c0), r); c.font = font()
            elif j == 4: c.value = '=%s%d/Summary!$C$5' % (CL(c0 + 3), r); c.font = font()
            elif j == 10: c.value = '=Summary!$C$5+%s%d' % (CL(c0 + 3), r); c.font = font()
            else: c.value = v; c.font = font(color=BLUE)
    for name, key, c0 in (('f', ('fixed', 'risk'), 25), ('g', ('fixed', 'profit'), 28)):
        st = res[key][(y, m)][1]
        a = wm.cell(r, c0, round(st['net'], 2)); a.font = font(color=BLUE); a.number_format = USD; a.border = BOX
        b = wm.cell(r, c0 + 1, '=%s%d/Summary!$C$5' % (CL(c0), r)); b.font = font(); b.number_format = PCT; b.border = BOX
        d = wm.cell(r, c0 + 2, round(st['mdd'], 2)); d.font = font(color=BLUE); d.number_format = USD; d.border = BOX
last = 2 + len(months)
green = Font(name=F, size=10, color='006100'); red = Font(name=F, size=10, color='9C0006')
for col in ('F', 'Q', 'Y', 'AB'):
    rng = '%s3:%s%d' % (col, col, last)
    wm.conditional_formatting.add(rng, CellIsRule(operator='greaterThan', formula=['0'], fill=PatternFill('solid', fgColor='C6EFCE'), font=green))
    wm.conditional_formatting.add(rng, CellIsRule(operator='lessThan', formula=['0'], fill=PatternFill('solid', fgColor='FFC7CE'), font=red))
wm.column_dimensions['A'].width = 10; wm.column_dimensions['B'].width = 7
for j in range(3, 31): wm.column_dimensions[CL(j)].width = 12
wm.row_dimensions[2].height = 30
wm.freeze_panes = 'C3'

# ------------------------------------------------------------------ trades
for title, key in (('Trades Over N - Risk', ('split', 'risk')), ('Trades Over N - Profit', ('split', 'profit'))):
    wt = wb.create_sheet(title)
    hd = ['Month', 'Fill (IST)', 'Exit (IST)', 'Direction', 'Entry', 'Stop', 'Stop distance', 'Exit', 'Planned risk ($)', 'Lots', 'Risk ($)', 'P&L ($)', 'Balance ($)', 'Unrecovered losses after ($)']
    for j, h in enumerate(hd):
        c = wt.cell(1, 1 + j, h); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(wrap_text=True, horizontal='center')
    r = 2
    for (y, m) in months:
        for x in res[key][(y, m)][0]:
            vals = ['%04d-%02d' % (y, m), x['t'], x['tx'], 'long' if x['dir'] == 1 else 'short', x['entry'], round(x['stop'], 2), round(x['dist'], 2), x['kind'],
                    round(x['plan'], 2), x['lots'], round(x['risk'], 2), round(x['pnl'], 2), round(x['bal'], 2), round(x['pool'], 2)]
            fmts = [None, 'yyyy-mm-dd hh:mm', 'yyyy-mm-dd hh:mm', None, '0.00', '0.00', '0.00', None, USD, '0.00', USD, USD, USD, USD]
            for j, (v, fmt) in enumerate(zip(vals, fmts)):
                c = wt.cell(r, 1 + j, v); c.font = font(color=BLUE) if j >= 4 else font()
                if fmt: c.number_format = fmt
            r += 1
    for j, w in enumerate([9, 16, 16, 9, 10, 10, 10, 20, 13, 7, 11, 11, 12, 14]): wt.column_dimensions[CL(1 + j)].width = w
    wt.row_dimensions[1].height = 30; wt.freeze_panes = 'A2'; wt.auto_filter.ref = 'A1:N%d' % (r - 1)

# ------------------------------------------------------------------ Notes
wn = wb.create_sheet('Notes')
notes = [('How the rule sizes a trade', ''),
         ('', 'Recover losses over N trades (the EA / strategy rule): every trade risks the base plus 1/N of the losses not yet won back. A loss adds its $ to'),
         ('', 'the unrecovered losses; a win takes its profit off them. With N = 3 the next trade goes for a third of what is still unrecovered.'),
         ('', 'Risk mode: the base and the extra are the $ the trade LOSES at its stop ($20 + 1/3 of the losses).'),
         ('', 'Profit mode: they are the $ the trade WINS at TP1: risk = amount / (0.2 x stop / (stop + costs)), so a TP1 win is the amount before the lot rounding'),
         ('', '(about $100–110 of risk for the $20 base on M5 gold). This is how v5.1 of the EA and the strategy size it.'),
         ('Data and engine', ''),
         ('', 'FxPro gold, M5 candles for the signals and M1 candles for the exits, January 2021 to 2 October 2026; times in IST.'),
         ('', 'Signals: the Auction Retest engine with your settings (as in your EA). The EA places the limit order at the next candle; its stop loss and take'),
         ('', 'profit go to the broker with the order, so they are checked minute by minute from the fill (in the fill minute only the stop; a minute touching'),
         ('', 'both: the stop, the cautious choice). The TP1 target is pushed by the costs (earn-back), so a TP1 win nets 0.2 x the stop distance per oz.'),
         ('', 'An order is not placed (or is cancelled) in the news block; an open trade is closed at the candle open when the news window starts, at 23:55 or'),
         ('', 'when Saturday starts. One trade at a time.'),
         ('Money', ''),
         ('', 'Each month: a fresh $1,000 on the 1st, the recovery state starts again, nothing carries over. Lots in 0.01 steps, rounded down, at least 0.01;'),
         ('', 'never more than the 1:100 leverage allows (equity x 100 / (price x 100 oz)). Costs 0.23 per oz per trade (spread 0.16 + $7 per lot).'),
         ('', 'The leverage limit cuts recovery trades on a $1,000 account (e.g. a planned $294 trade risks $200): that trade then wins back only part.'),
         ('What the numbers say', ''),
         ('', 'At TP1 = 0.2R with these settings 77% of the trades win, but a win nets about 0.18R and a loss costs 1R, so the trades lose on average.'),
         ('', 'Recovering over 3 trades makes the trades after a loss bigger, so the losing months lose more; it cannot make a losing entry profitable.'),
         ('Limits of a backtest', ''),
         ('', 'Real spreads, slippage and the broker\'s fills differ; inside one minute the path is unknown. The result is one order of the trades.')]
for i, (h, t) in enumerate(notes):
    if h: c = wn.cell(1 + i, 1, h); c.font = font(bold=True)
    else: c = wn.cell(1 + i, 2, t); c.font = font()
wn.column_dimensions['A'].width = 26; wn.column_dimensions['B'].width = 150
wb.save(OUT)
print('saved', OUT)
