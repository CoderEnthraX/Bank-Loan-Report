"""nt4 workbook: Recover losses over N trades (N = 3), TP1 0.2R, $20 base, every month on its own, M5 and M15, Risk and Profit, for one
start balance. Run: python3 -I nt4/build_xlsx.py START OUT.xlsx  (reads nt4/results_M5.pkl and nt4/results_M15.pkl)"""
import sys, pickle
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter as CL
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
START = float(sys.argv[1]); OUT = sys.argv[2]
RES = {tf: pickle.load(open(S + '/nt4/results_%s.pkl' % tf, 'rb')) for tf in ('M5', 'M15')}
months = RES['M5']['months']; assert months == RES['M15']['months']
F = 'Arial'
def font(**k): return Font(name=F, size=k.pop('size', 10), **k)
BLUE = '0000FF'; HDR = PatternFill('solid', fgColor='1F3864'); SUB = PatternFill('solid', fgColor='D9E1F2'); INP = PatternFill('solid', fgColor='FFFF00')
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD = '$#,##0.00;($#,##0.00);-'; PCT = '0.0%;(0.0%);-'; INT = '#,##0;(#,##0);-'
RUNS = [('M5 Risk', 'M5', 'risk', '$20 lost at the stop'), ('M5 Profit', 'M5', 'profit', '$20 won at TP1'),
        ('M15 Risk', 'M15', 'risk', '$20 lost at the stop'), ('M15 Profit', 'M15', 'profit', '$20 won at TP1')]
SUBH = ['Trades', 'Wins', 'Win %', 'Net ($)', 'Return %', 'Max drawdown ($)', 'Biggest risk ($)', 'Biggest lots', 'Worst trade ($)', 'Longest losing run', 'End balance ($)']
NS = len(SUBH)
def c0_of(i): return 3 + i * NS                                    # first column of run i on the Monthly sheet
FIX0 = 3 + len(RUNS) * NS                                           # the fixed-$20 (no recovery) nets after the four blocks
wb = Workbook()

# ------------------------------------------------------------------ Summary
ws = wb.active; ws.title = 'Summary'
ws['A1'] = 'Gold: Recover losses over N trades (N = 3), TP1 0.2R, $20 base, every month from $%s (Jan 2021 – Sep 2026), M5 and M15, Risk and Profit' % format(int(START), ',')
ws['A1'].font = font(bold=True, size=13)
ws['A2'] = 'Each calendar month starts with a fresh account on the 1st (IST) and is traded to the end of the month. All money numbers in USD.'
ws['A2'].font = font(italic=True)
settings = [('Start balance each month ($)', START, USD, 'The same fresh amount on the 1st of every month.'),
            ('Base amount ($)', 20.0, USD, 'Risk: the stop-out loss of a base trade. Profit: the win of a base trade at TP1 (costs included, v5.1).'),
            ('N (Recover losses over N trades)', 3, INT, 'Every trade adds 1/N of the unrecovered losses to the base.'),
            ('Final exit TP1 (R)', 0.2, '0.0"R"', 'TP1 is the final exit (no partial).'),
            ('Leverage (1:x)', 100, INT, 'Lots never above equity x 100 / (price x 100 oz).'),
            ('Costs per oz ($)', 0.23, USD, 'Spread 0.16 + $7 commission per lot (0.07 per oz); the TP1 target is pushed by them (earn-back).')]
ws['A4'] = 'Settings of the test (inputs; the numbers below were computed with them)'; ws['A4'].font = font(bold=True)
for i, (k, v, fmt, note) in enumerate(settings):
    r = 5 + i
    ws.cell(r, 1, k).font = font(); c = ws.cell(r, 3, v); c.font = font(color=BLUE); c.number_format = fmt; c.fill = INP
    ws.cell(r, 4, note).font = font(italic=True, color='595959')
ws['A12'] = 'Trading rules (your EA settings, the same on M5 and M15)'; ws['A12'].font = font(bold=True)
rules = ['Tuesday, Wednesday and Thursday only; new trades 06:00–23:00 IST (none after 2 AM).',
         'Kill zones Asia, London and New York (London / New York time, so they move 1 hour in winter).',
         'Daily news window 17:45 IST for 30 min (New York time), no new trades 30 min before it; an open trade is closed when it starts.',
         'Force-close 23:55 IST every day; close when Saturday starts. Lots in 0.01 steps, rounded down, at least 0.01.',
         'Signals: the Auction Retest engine on M5 or M15 (your settings); exits checked on M1 like the EA\'s broker stop loss and take profit.']
for i, t in enumerate(rules): ws.cell(13 + i, 1, '• ' + t).font = font()

r0 = 19
ws.cell(r0, 1, 'Results over the %d months: Recover losses over 3 trades (formulas on the Monthly sheet)' % len(months)).font = font(bold=True)
hdr = r0 + 1
ws.cell(hdr, 1, 'Measure').font = font(bold=True, color='FFFFFF'); ws.cell(hdr, 1).fill = HDR
for j, (name, tf, sb, what) in enumerate(RUNS):
    c = ws.cell(hdr, 3 + j, '%s\n(%s)' % (name, what)); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(wrap_text=True, horizontal='center')
N0, N1 = 3, 3 + len(months) - 1
def rng(col): return 'Monthly!%s%d:%s%d' % (col, N0, col, N1)
lines = [('Total net profit ($)', lambda L: '=SUM(%s)' % rng(L), USD),
         ('Average month ($)', lambda L: '=AVERAGE(%s)' % rng(L), USD),
         ('Months tested', lambda L: '=COUNT(%s)' % rng(L), INT),
         ('Profitable months', lambda L: '=COUNTIF(%s,">0")' % rng(L), INT),
         ('Losing months', lambda L: '=COUNTIF(%s,"<0")' % rng(L), INT),
         ('Profitable months (%)', None, PCT),
         ('Best month ($)', lambda L: '=MAX(%s)' % rng(L), USD),
         ('Worst month ($)', lambda L: '=MIN(%s)' % rng(L), USD),
         ('Worst month (% of the start)', None, PCT),
         ('Biggest drawdown in a month ($)', 'mdd', USD),
         ('Trades', 'trades', INT),
         ('Win rate (trades in profit)', 'win', PCT),
         ('Biggest single-trade risk ($)', 'risk', USD)]
for i, (label, f, fmt) in enumerate(lines):
    r = hdr + 1 + i
    ws.cell(r, 1, label).font = font()
    for j in range(len(RUNS)):
        c0 = c0_of(j); col = CL(3 + j); L = CL(c0 + 3)
        c = ws.cell(r, 3 + j)
        if label == 'Profitable months (%)': c.value = '=IF(%s%d>0,%s%d/%s%d,0)' % (col, hdr + 3, col, hdr + 4, col, hdr + 3)
        elif label == 'Worst month (% of the start)': c.value = '=%s%d/$C$5' % (col, hdr + 8)
        elif f == 'mdd': c.value = '=MAX(%s)' % rng(CL(c0 + 5))
        elif f == 'trades': c.value = '=SUM(%s)' % rng(CL(c0))
        elif f == 'win': c.value = '=IF(SUM(%s)>0,SUM(%s)/SUM(%s),0)' % (rng(CL(c0)), rng(CL(c0 + 1)), rng(CL(c0)))
        elif f == 'risk': c.value = '=MAX(%s)' % rng(CL(c0 + 6))
        else: c.value = f(L)
        c.number_format = fmt; c.font = font(); c.border = BOX
cmp_r = hdr + 1 + len(lines) + 1
ws.cell(cmp_r, 1, 'For comparison: the same trades with a fixed $20 and no recovery').font = font(bold=True)
for k, (label, fn) in enumerate([('Total net profit ($)', 'SUM'), ('Profitable months', 'POS')]):
    r = cmp_r + 1 + k; ws.cell(r, 1, label).font = font()
    for j in range(len(RUNS)):
        L = CL(FIX0 + j); c = ws.cell(r, 3 + j)
        c.value = '=SUM(%s)' % rng(L) if fn == 'SUM' else '=COUNTIF(%s,">0")' % rng(L)
        c.number_format = USD if fn == 'SUM' else INT; c.font = font(); c.border = BOX

yr0 = cmp_r + 4
ws.cell(yr0, 1, 'Net profit and profitable months per year (Recover losses over 3 trades)').font = font(bold=True)
yh = yr0 + 1
c = ws.cell(yh, 1, 'Year'); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR
for j, (name, *_ ) in enumerate(RUNS):
    for k, h in enumerate((name + ': net ($)', name + ': profitable months')):
        c = ws.cell(yh, 3 + 2 * j + k, h); c.font = font(bold=True, color='FFFFFF'); c.fill = HDR; c.alignment = Alignment(wrap_text=True, horizontal='center')
for i, y in enumerate(['2021', '2022', '2023', '2024', '2025', '2026']):
    r = yh + 1 + i; ws.cell(r, 1, y).font = font()
    for j in range(len(RUNS)):
        L = CL(c0_of(j) + 3)
        c1 = ws.cell(r, 3 + 2 * j, '=SUMIFS(%s,Monthly!$B$%d:$B$%d,$A%d)' % (rng(L), N0, N1, r)); c1.number_format = USD; c1.font = font(); c1.border = BOX
        c2 = ws.cell(r, 4 + 2 * j, '=COUNTIFS(Monthly!$B$%d:$B$%d,$A%d,%s,">0")' % (N0, N1, r, rng(L))); c2.number_format = INT; c2.font = font(); c2.border = BOX
ws.cell(yh + 8, 1, '2026: January to September (the data end on 2 October 2026).').font = font(italic=True, color='595959')
ws.column_dimensions['A'].width = 36; ws.column_dimensions['B'].width = 2
for j in range(3, 12): ws.column_dimensions[CL(j)].width = 18
ws.row_dimensions[hdr].height = 32; ws.row_dimensions[yh].height = 44
ws.freeze_panes = 'A4'

# ------------------------------------------------------------------ Monthly
wm = wb.create_sheet('Monthly')
for c, h in ((1, 'Month'), (2, 'Year')):
    x = wm.cell(1, c, h); x.font = font(bold=True, color='FFFFFF'); x.fill = HDR
    wm.cell(2, c).fill = SUB; wm.cell(2, c).border = BOX
for j, (name, tf, sb, what) in enumerate(RUNS):
    c0 = c0_of(j)
    wm.merge_cells(start_row=1, start_column=c0, end_row=1, end_column=c0 + NS - 1)
    x = wm.cell(1, c0, '%s: Over N=3 (%s)' % (name, what)); x.font = font(bold=True, color='FFFFFF'); x.fill = HDR; x.alignment = Alignment(horizontal='center')
    for k, h in enumerate(SUBH):
        x = wm.cell(2, c0 + k, h); x.font = font(bold=True); x.fill = SUB; x.alignment = Alignment(wrap_text=True, horizontal='center'); x.border = BOX
wm.merge_cells(start_row=1, start_column=FIX0, end_row=1, end_column=FIX0 + len(RUNS) - 1)
x = wm.cell(1, FIX0, 'Fixed $20, no recovery: net ($)'); x.font = font(bold=True, color='FFFFFF'); x.fill = HDR; x.alignment = Alignment(horizontal='center')
for j, (name, *_ ) in enumerate(RUNS):
    x = wm.cell(2, FIX0 + j, name); x.font = font(bold=True); x.fill = SUB; x.alignment = Alignment(wrap_text=True, horizontal='center'); x.border = BOX
for i, (y, m) in enumerate(months):
    r = 3 + i
    wm.cell(r, 1, '%04d-%02d' % (y, m)).font = font(); wm.cell(r, 2, str(y)).font = font()
    for j, (name, tf, sb, what) in enumerate(RUNS):
        c0 = c0_of(j); st = RES[tf]['res'][(START, 'split', sb)][(y, m)][1]
        vals = [(st['n'], INT), (st['wins'], INT), (None, PCT), (round(st['net'], 2), USD), (None, PCT), (round(st['mdd'], 2), USD),
                (round(st['maxRisk'], 2), USD), (st['maxLots'], '0.00'), (round(st['worst'], 2), USD), (st['lrun'], INT), (None, USD)]
        for k, (v, fmt) in enumerate(vals):
            x = wm.cell(r, c0 + k); x.number_format = fmt; x.border = BOX
            if k == 2: x.value = '=IF(%s%d>0,%s%d/%s%d,0)' % (CL(c0), r, CL(c0 + 1), r, CL(c0), r); x.font = font()
            elif k == 4: x.value = '=%s%d/Summary!$C$5' % (CL(c0 + 3), r); x.font = font()
            elif k == 10: x.value = '=Summary!$C$5+%s%d' % (CL(c0 + 3), r); x.font = font()
            else: x.value = v; x.font = font(color=BLUE)
        fx = RES[tf]['res'][(START, 'fixed', sb)][(y, m)][1]
        x = wm.cell(r, FIX0 + j, round(fx['net'], 2)); x.font = font(color=BLUE); x.number_format = USD; x.border = BOX
last = 2 + len(months)
green = Font(name=F, size=10, color='006100'); red = Font(name=F, size=10, color='9C0006')
for col in [CL(c0_of(j) + 3) for j in range(len(RUNS))] + [CL(FIX0 + j) for j in range(len(RUNS))]:
    rg = '%s3:%s%d' % (col, col, last)
    wm.conditional_formatting.add(rg, CellIsRule(operator='greaterThan', formula=['0'], fill=PatternFill('solid', fgColor='C6EFCE'), font=green))
    wm.conditional_formatting.add(rg, CellIsRule(operator='lessThan', formula=['0'], fill=PatternFill('solid', fgColor='FFC7CE'), font=red))
wm.column_dimensions['A'].width = 10; wm.column_dimensions['B'].width = 7
for j in range(3, FIX0 + len(RUNS)): wm.column_dimensions[CL(j)].width = 12
wm.row_dimensions[2].height = 30
wm.freeze_panes = 'C3'

# ------------------------------------------------------------------ trades, one sheet per run
for name, tf, sb, what in RUNS:
    wt = wb.create_sheet('Trades %s' % name)
    hd = ['Month', 'Fill (IST)', 'Exit (IST)', 'Direction', 'Entry', 'Stop', 'Stop distance', 'Exit', 'Planned risk ($)', 'Lots', 'Risk ($)', 'P&L ($)', 'Balance ($)', 'Unrecovered losses after ($)']
    for j, h in enumerate(hd):
        x = wt.cell(1, 1 + j, h); x.font = font(bold=True, color='FFFFFF'); x.fill = HDR; x.alignment = Alignment(wrap_text=True, horizontal='center')
    r = 2
    for (y, m) in months:
        for t in RES[tf]['res'][(START, 'split', sb)][(y, m)][0]:
            vals = ['%04d-%02d' % (y, m), t['t'], t['tx'], 'long' if t['dir'] == 1 else 'short', t['entry'], round(t['stop'], 2), round(t['dist'], 2), t['kind'],
                    round(t['plan'], 2), t['lots'], round(t['risk'], 2), round(t['pnl'], 2), round(t['bal'], 2), round(t['pool'], 2)]
            fmts = [None, 'yyyy-mm-dd hh:mm', 'yyyy-mm-dd hh:mm', None, '0.00', '0.00', '0.00', None, USD, '0.00', USD, USD, USD, USD]
            for j, (v, fmt) in enumerate(zip(vals, fmts)):
                x = wt.cell(r, 1 + j, v); x.font = font(color=BLUE) if j >= 4 else font()
                if fmt: x.number_format = fmt
            r += 1
    for j, w in enumerate([9, 16, 16, 9, 10, 10, 10, 20, 13, 7, 11, 11, 12, 14]): wt.column_dimensions[CL(1 + j)].width = w
    wt.row_dimensions[1].height = 30; wt.freeze_panes = 'A2'; wt.auto_filter.ref = 'A1:N%d' % (r - 1)

# ------------------------------------------------------------------ Notes
wn = wb.create_sheet('Notes')
notes = [('How the rule sizes a trade', ''),
         ('', 'Recover losses over N trades: every trade goes for the base plus 1/N of the losses not yet won back. A loss adds its $ to the unrecovered'),
         ('', 'losses; a win takes its profit off them. With N = 3 the next trade goes for a third of what is still unrecovered.'),
         ('', 'Risk: the base and the extra are the $ the trade LOSES at its stop ($20 + 1/3 of the losses).'),
         ('', 'Profit: they are the $ the trade WINS at TP1: risk = amount / (0.2 x stop / (stop + costs)), so a TP1 win is the amount before the lot'),
         ('', 'rounding: the median $20 base trade risks about $109 on M5 (median stop $2.51) and $106 on M15 (median stop $4.15).'),
         ('', 'This is how v5.1 of the EA and the strategy size it.'),
         ('Why the start balance changes the result', ''),
         ('', 'Lots can never be more than the 1:100 leverage allows (equity x 100 / (price x 100 oz)). On a small account this cuts the big recovery trades,'),
         ('', 'so they win back only part of the loss but also lose less. A bigger account lets them run at full size: the same trades, bigger amounts.'),
         ('', 'With a fixed $20 RISK and no recovery the leverage never binds, so that result is the same for every start balance; a fixed $20 WIN needs about $105-110 of risk, which the leverage still cuts on a $1,000 account.'),
         ('Data and engine', ''),
         ('', 'FxPro gold, M5 / M15 candles for the signals and M1 candles for the exits, January 2021 to 2 October 2026; times in IST.'),
         ('', 'Signals: the Auction Retest engine with your settings. The EA places the limit order at the next candle; its stop loss and take profit go to the'),
         ('', 'broker with the order, so they are checked minute by minute from the fill (in the fill minute only the stop; a minute touching both: the stop).'),
         ('', 'The TP1 target is pushed by the costs (earn-back), so a TP1 win nets 0.2 x the stop distance per oz. Orders are not placed (or are cancelled)'),
         ('', 'in the news block; an open trade is closed at the candle open when the news window starts, at 23:55 or when Saturday starts. One trade at a time.'),
         ('Money', ''),
         ('', 'Each month: the fresh start balance on the 1st, the recovery state starts again, nothing carries over. Lots in 0.01 steps, rounded down, at'),
         ('', 'least 0.01. Costs 0.23 per oz per trade (spread 0.16 + $7 per lot).'),
         ('What the numbers say', ''),
         ('', 'At TP1 = 0.2R most trades win, but a win nets about 0.18R and a loss costs 1R, so the trades lose on average. Recovering over 3 trades makes'),
         ('', 'the trades after a loss bigger, so the losing months lose more; it cannot make a losing entry profitable.'),
         ('Limits of a backtest', ''),
         ('', 'Real spreads, slippage and the broker\'s fills differ; inside one minute the path is unknown. The result is one order of the trades.')]
for i, (h, t) in enumerate(notes):
    if h: x = wn.cell(1 + i, 1, h); x.font = font(bold=True)
    else: x = wn.cell(1 + i, 2, t); x.font = font()
wn.column_dimensions['A'].width = 30; wn.column_dimensions['B'].width = 150
wb.save(OUT)
print('saved', OUT)
