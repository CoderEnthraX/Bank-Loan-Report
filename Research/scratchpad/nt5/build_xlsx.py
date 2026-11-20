"""2024 edge workbook: Summary, 2024 Months (one-year path and each month fresh), Every Year, Settings, Search (top settings), Notes."""
import sys, pickle
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter as CL
OUT = sys.argv[1]
D = pickle.load(open('edge_data.pkl', 'rb'))
F = 'Arial'
def font(**k): return Font(name=F, size=k.pop('size', 10), **k)
HDR = PatternFill('solid', fgColor='1F3864'); SUB = PatternFill('solid', fgColor='D9E1F2'); BLUE = '0000FF'
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD = '$#,##0;($#,##0);-'; PCT = '0%;(0%);-'
GREEN = PatternFill('solid', fgColor='C6EFCE'); RED = PatternFill('solid', fgColor='FFC7CE')
def hdr(ws, r, c, v, w=None):
    x = ws.cell(r, c, v); x.font = font(bold=True, color='FFFFFF'); x.fill = HDR; x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
def pick_name(d): return '%s + %s' % (d['name'].split(':')[0], d['rule'])
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
wb = Workbook()
# ---------------- Summary
ws = wb.active; ws.title = 'Summary'
ws['A1'] = 'Gold: searching for an edge in 2024 (M5 and M15) - Auction Retest with your EA rules'; ws['A1'].font = font(bold=True, size=13)
lines = ['2,275 different settings searched (M15 1,102, M5 1,173): final TP 0.1R - 2R, stop size, entry type, choppiness filter,',
         'trading hours, kill zones, days, VWAP anchor, momentum, breakeven moves and the trade direction; then every money rule (Risk and Profit) on the best.',
         'Each setting is your EA: news window, force-close 23:55 IST, weekend close, costs 0.23 per oz, exits on M1, 1:100 leverage; every year from $1,000, $20 base.',
         'Picked on 2024, so 2024 flatters them: the other years (Every Year sheet) are the honest test.']
for i, t in enumerate(lines): ws.cell(2 + i, 1, t).font = font(italic=True)
r0 = 7
heads = ['Pick (settings + money rule)', 'Timeframe', '2024 net ($)', '2024 max drawdown', '2024 months in profit (each month fresh from $1,000)', '2024 worst month (fresh)',
         '2021', '2022', '2023', '2025', '2026 (Jan-Sep)', 'Years in profit (2021-2026)', 'Years the account lost 80%+']
for j, h in enumerate(heads): hdr(ws, r0, 1 + j, h)
for i, d in enumerate(D):
    r = r0 + 1 + i; y = d['years']
    vals = [pick_name(d), d['tf'], y[2024]['net'], y[2024]['dd'], '%d / %d' % (y[2024]['pos'], y[2024]['months']), min(v for _, v, _ in d['m24fresh']),
            y[2021]['net'], y[2022]['net'], y[2023]['net'], y[2025]['net'], y[2026]['net'], None, sum(1 for k in y if y[k]['dd'] >= 0.8)]
    fm = [None, None, USD, PCT, None, USD, USD, USD, USD, USD, USD, None, '0']
    for j, (v, f) in enumerate(zip(vals, fm)):
        x = ws.cell(r, 1 + j, v); x.font = font(color=BLUE) if isinstance(v, (int, float)) else font(); x.border = BOX
        if f: x.number_format = f
    ws.cell(r, 12, '=COUNTIF(C%d,">0")+COUNTIF(G%d:K%d,">0")' % (r, r, r)).font = font(); ws.cell(r, 12).border = BOX
last = r0 + len(D)
for col in ('C', 'F', 'G', 'H', 'I', 'J', 'K'):
    ws.conditional_formatting.add('%s%d:%s%d' % (col, r0 + 1, col, last), CellIsRule(operator='greaterThan', formula=['0'], fill=GREEN))
    ws.conditional_formatting.add('%s%d:%s%d' % (col, r0 + 1, col, last), CellIsRule(operator='lessThan', formula=['0'], fill=RED))
k = last + 2
for t in ['What it shows',
          '- There is no edge at a 0.1R - 0.3R final target in 2024 on M5 or M15: the best of all settings lost (M5 -0.6R to -1.6R, M15 -2.0R to +0.3R for the year).',
          '- The edge in 2024 is LONG ONLY, a 1R - 2R target, a choppiness filter or a wide stop. Gold rose all year; buying the retests worked, selling them did not.',
          '- M5 D (long, 2R, stop 2.4 ATR, chop 8, 12:00-23:00 IST, your kill zones, Tue-Thu) made money in 11 of 12 months of 2024 with a fixed $20,',
          '  and in all 12 with Fibonacci / % of losses / Labouchere on top. Those recovery rules blew the account in 2026 (and some in 2021): see Every Year.',
          '- The safest pick is the fixed $20: smaller profit, never blown. Recovery rules only multiply an edge, and multiply the bad years too.']:
    ws.cell(k, 1, t).font = font(bold=t == 'What it shows'); k += 1
ws.column_dimensions['A'].width = 46
for j in range(2, 14): ws.column_dimensions[CL(j)].width = 13
ws.row_dimensions[r0].height = 58
# ---------------- 2024 Months
wm = wb.create_sheet('2024 Months')
hdr(wm, 1, 1, 'Pick'); hdr(wm, 1, 2, 'How')
for j, m in enumerate(MON): hdr(wm, 1, 3 + j, m)
hdr(wm, 1, 15, 'Year total'); hdr(wm, 1, 16, 'Months in profit')
r = 2
for d in D:
    for how, series in (('one year from $1,000: P&L in the month', [v for _, v in d['m24']]),
                        ('each month fresh from $1,000', [dict((m, v) for m, v, _ in d['m24fresh']).get(m, 0.0) for m in range(1, 13)])):
        wm.cell(r, 1, pick_name(d)).font = font(); wm.cell(r, 2, how).font = font(italic=True)
        for j, v in enumerate(series):
            x = wm.cell(r, 3 + j, round(v, 2)); x.font = font(color=BLUE); x.number_format = USD; x.border = BOX
        wm.cell(r, 15, '=SUM(C%d:N%d)' % (r, r)).number_format = USD; wm.cell(r, 15).font = font(bold=True)
        wm.cell(r, 16, '=COUNTIF(C%d:N%d,">0")' % (r, r)).font = font()
        r += 1
wm.conditional_formatting.add('C2:O%d' % (r - 1), CellIsRule(operator='greaterThan', formula=['0'], fill=GREEN))
wm.conditional_formatting.add('C2:O%d' % (r - 1), CellIsRule(operator='lessThan', formula=['0'], fill=RED))
wm.column_dimensions['A'].width = 46; wm.column_dimensions['B'].width = 34
for j in range(3, 17): wm.column_dimensions[CL(j)].width = 10
wm.freeze_panes = 'C2'
# ---------------- Every Year
wy = wb.create_sheet('Every Year')
hdr(wy, 1, 1, 'Pick')
for j, y in enumerate(range(2021, 2027)):
    hdr(wy, 1, 2 + 3 * j, '%d net ($)' % y); hdr(wy, 1, 3 + 3 * j, '%d max drawdown' % y); hdr(wy, 1, 4 + 3 * j, '%d months in profit' % y)
hdr(wy, 1, 20, 'All years net ($)')
for i, d in enumerate(D):
    r = 2 + i; wy.cell(r, 1, pick_name(d)).font = font()
    for j, y in enumerate(range(2021, 2027)):
        v = d['years'][y]
        a = wy.cell(r, 2 + 3 * j, round(v['net'], 2)); a.number_format = USD; a.font = font(color=BLUE)
        b = wy.cell(r, 3 + 3 * j, v['dd']); b.number_format = PCT; b.font = font(color=BLUE)
        wy.cell(r, 4 + 3 * j, '%d / %d' % (v['pos'], v['months'])).font = font()
    wy.cell(r, 20, '=' + '+'.join('%s%d' % (CL(2 + 3 * j), r) for j in range(6))).number_format = USD
wy.column_dimensions['A'].width = 46
for j in range(2, 21): wy.column_dimensions[CL(j)].width = 11
wy.row_dimensions[1].height = 44; wy.freeze_panes = 'B2'
# ---------------- Settings
st = wb.create_sheet('Settings')
rows = [('Setting (EA input / strategy input)', 'M5 D', 'M15 B', 'Your current'),
        ('Chart timeframe', 'M5', 'M15', 'M5 / M15'),
        ('Final exit at (InpExitAt) / TP1 (InpTp1R)', 'TP1, 2.0 R', 'TP1, 2.0 R', 'TP1, 0.2 R'),
        ('Longs / Shorts (InpAllowLong / InpAllowShort)', 'on / OFF', 'on / OFF', 'on / on'),
        ('Stop distance x ATR (InpStopAtr)', 2.4, 4.0, 1.8),
        ('Entry price (InpEntryMode)', 'Market', 'Model (25%)', 'Model (25%)'),
        ('Skip choppy sessions (InpChopOn / InpChopMax)', 'on, 8', 'off', 'off'),
        ('Trade only between (InpHoursOn, IST)', '12:00 - 23:00', '06:00 - 23:00', '06:00 - 23:00'),
        ('Kill zones (InpKzAsia / InpKzLon / InpKzNy)', 'Asia, London, New York', 'London, New York', 'Asia, London, New York'),
        ('Days (InpDayOn)', 'Tue, Wed, Thu', 'Mon - Fri', 'Tue, Wed, Thu'),
        ('VWAP anchor (InpVwapAnchor)', 'Session', 'Session', 'Session'),
        ('Min momentum x ATR (InpMomAtr)', 1.10, 0.60, 0.85),
        ('When TP2 hits, move stop (InpMv2On)', 'off', 'on', 'off'),
        ('Everything else', 'as your EA (news window, force-close, weekend close, max fills 10 ...)', 'as your EA', '')]
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        x = st.cell(1 + i, 1 + j, v)
        if i == 0: hdr(st, 1, 1 + j, v)
        else: x.font = font(); x.border = BOX
st.column_dimensions['A'].width = 48
for c in 'BCD': st.column_dimensions[c].width = 30
# ---------------- Search
sr = wb.create_sheet('Search')
hdr(sr, 1, 1, 'Timeframe')
for j, h in enumerate(['Direction', 'Final TP (R)', 'Stop x ATR', 'Entry', 'Chop filter', 'Hours (IST)', 'Kill zones', 'Days', 'VWAP', 'Momentum', 'Stop move',
                       '2024 R', '2024 R per trade', '2024 trades', '2024 months in profit', '2021 R', '2022 R', '2023 R', '2025 R', '2026 R']):
    hdr(sr, 1, 2 + j, h)
r = 2
for tf in ('M5', 'M15'):
    S = [x for x in pickle.load(open('stage2_%s.pkl' % tf, 'rb')) if x[1] and x[1]['years'][2024]['n'] >= 40]
    for c, res, e in sorted(S, key=lambda x: -x[1]['years'][2024]['sumR'])[:40]:
        y = res['years']
        vals = [tf, c.get('dirn', 'both'), c['tp'], c['stopAtr'], c['entryMode'], c['chop'] or 'off', '%04d-%04d' % c['hours'] if c['hours'] else 'any', c['kz'] or 'off',
                c['days'], c['vw'], c['momAtr'], c['mv'] or 'off', round(y[2024]['sumR'], 2), round(y[2024]['exp'], 3), y[2024]['n'], sum(v > 0 for v in res['m24'].values()),
                round(y[2021]['sumR'], 2), round(y[2022]['sumR'], 2), round(y[2023]['sumR'], 2), round(y[2025]['sumR'], 2), round(y[2026]['sumR'], 2)]
        for j, v in enumerate(vals): sr.cell(r, 1 + j, v).font = font()
        r += 1
sr.conditional_formatting.add('M2:U%d' % (r - 1), CellIsRule(operator='greaterThan', formula=['0'], fill=GREEN))
sr.conditional_formatting.add('M2:U%d' % (r - 1), CellIsRule(operator='lessThan', formula=['0'], fill=RED))
for j in range(1, 22): sr.column_dimensions[CL(j)].width = 11
sr.row_dimensions[1].height = 44; sr.freeze_panes = 'B2'; sr.auto_filter.ref = 'A1:U%d' % (r - 1)
# ---------------- Notes
nt = wb.create_sheet('Notes')
notes = ['Every number: your EA rules on FxPro gold 2021 - Sep 2026 (the engine on M5 / M15 candles, exits on M1 candles: stop first when a minute touches both),',
         'news window 17:45 IST + 30 min before, force-close 23:55 IST, Saturday close, one trade at a time, costs 0.23 per oz (spread 0.16 + $7 a lot),',
         'targets pushed by the costs (earn-back). Money: $1,000 start, $20 base, the 1:100 leverage limit, fractional lots (the EA rounds down to 0.01).',
         'R = the result as a multiple of the trade\'s risk. "Months in profit (fresh)": each month started again from $1,000.',
         'The settings were chosen BECAUSE they did well in 2024, so 2024 is the best case. A real edge should also show in years it was not picked on:',
         'the long-only settings made money in 2022, 2023 and 2025 with a fixed $20 but lost in 2021, when gold went sideways to down.',
         'Recovery rules (Martingale, Fibonacci, Labouchere, % of losses ...) bet more after losses: they turn a small edge into big 2024 numbers and empty',
         'the account in a bad stretch (2021, 2026). Test any pick in the MT5 Strategy Tester on your broker before using it.']
for i, t in enumerate(notes): nt.cell(1 + i, 1, t).font = font()
nt.column_dimensions['A'].width = 150
wb.save(OUT); print('saved', OUT)
