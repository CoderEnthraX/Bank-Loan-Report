"""File 1: best setting per timeframe, each on its own, every month and year 2021 - 2 Oct 2026. Run: python3 -I build_file1.py OUT.xlsx"""
import sys, pickle, collections
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter as CL
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_xl import *
OUT = sys.argv[1]
P = pickle.load(open('picks.pkl', 'rb'))
TFS = [t for t in ('M1', 'M5', 'M15', 'H1', 'H4') if t in P]
def mR(tr):
    m = collections.defaultdict(float)
    for x in tr: m[(x['t'].year, x['t'].month)] += x['net']
    return m
wb = Workbook(); ws = wb.active; ws.title = 'Summary'
ws['A1'] = 'Gold, Auction Retest with your EA rules: the best setting for each timeframe, 2021 - 2 Oct 2026 (each timeframe on its own)'; ws['A1'].font = font(bold=True, size=13)
ws['A2'] = ('Searched per timeframe: final TP 0.1-2R, stop size, entry, choppiness filter, hours, kill zones, days, VWAP anchor, momentum, stop moves, direction. '
            'Best = most R over 2021-2026 minus half its biggest drawdown. Money: $20 a trade (fixed), $1,000 start.'); ws['A2'].font = font(italic=True)
heads = ['Timeframe', 'Settings searched', 'Best setting', 'Trades', 'Win rate', 'Total R 2021-2026', 'Total $ ($20 a trade)', 'Biggest drawdown (R)', 'Months in profit',
         'Worst month ($)', 'Years in profit', 'Honest check: picked on 2021-2023 only -> its 2024-2026 R']
for j, h in enumerate(heads): hdr(ws, 4, 1 + j, h)
for i, tf in enumerate(TFS):
    b = P[tf]['best']; r = b['stats']; mon = mR(b['trades']); e = P[tf]['early']
    early24 = sum(v for y, v in e['stats']['yr'].items() if y >= 2024)
    row = [tf, P[tf]['n_searched'], cfg_text(b['cfg']), r['n'], r['wr'], r['tot'], None, r['dd'], '%d / %d' % (sum(v > 0 for v in mon.values()), len(MONTHS)),
           20 * min(mon.get(k, 0.0) for k in MONTHS), '%d / 6' % sum(v > 0 for v in r['yr'].values()), early24]
    fm = [None, '#,##0', None, '#,##0', PCT, R1, USD, R1, None, USD, None, R1]
    for j, (v, f) in enumerate(zip(row, fm)): val(ws, 5 + i, 1 + j, v, f)
    ws.cell(5 + i, 7, '=F%d*20' % (5 + i)).number_format = USD
    ws.cell(5 + i, 3).alignment = Alignment(wrap_text=True)
k = 6 + len(TFS)
for t in ['Daily (D1): no trades with your EA rules - the 23:55 force-close and the cancel-before-fill rule cancel every daily setup.',
          'Each timeframe\'s best setting was chosen on all of 2021-2026, so the table flatters it; the last column is the honest test (chosen on 2021-2023, run on 2024-2026).',
          'Per month and per year: the Months and Years sheets. Money rules on each best setting: the Money Rules sheet. The best setting of each month in hindsight: the Hindsight sheet.']:
    ws.cell(k, 1, t).font = font(italic=True); k += 1
ws.column_dimensions['A'].width = 11; ws.column_dimensions['B'].width = 10; ws.column_dimensions['C'].width = 70
for j in range(4, 13): ws.column_dimensions[CL(j)].width = 13
ws.row_dimensions[4].height = 44
# Months
wm = wb.create_sheet('Months')
hdr(wm, 1, 1, 'Month'); hdr(wm, 1, 2, 'Year')
for j, tf in enumerate(TFS): hdr(wm, 1, 3 + j, '%s ($, $20 a trade)' % tf)
for i, (y, m) in enumerate(MONTHS):
    r = 2 + i; wm.cell(r, 1, '%04d-%02d' % (y, m)).font = font(); wm.cell(r, 2, str(y)).font = font()
    for j, tf in enumerate(TFS): val(wm, r, 3 + j, round(20 * mR(P[tf]['best']['trades']).get((y, m), 0.0), 2), USD)
n = 1 + len(MONTHS)
posneg(wm, 'C2:%s%d' % (CL(2 + len(TFS)), n))
wm.cell(n + 1, 1, 'Total').font = font(bold=True)
wm.cell(n + 2, 1, 'Months in profit').font = font(bold=True)
for j in range(len(TFS)):
    c = CL(3 + j)
    wm.cell(n + 1, 3 + j, '=SUM(%s2:%s%d)' % (c, c, n)).number_format = USD
    wm.cell(n + 2, 3 + j, '=COUNTIF(%s2:%s%d,">0")' % (c, c, n))
wm.freeze_panes = 'C2'; wm.column_dimensions['A'].width = 10
for j in range(3, 3 + len(TFS)): wm.column_dimensions[CL(j)].width = 16
# Years
wy = wb.create_sheet('Years')
hdr(wy, 1, 1, 'Year')
for j, tf in enumerate(TFS): hdr(wy, 1, 2 + j, '%s: whole year ($, $20 a trade)' % tf)
for i, y in enumerate(range(2021, 2027)):
    wy.cell(2 + i, 1, str(y)).font = font()
    for j, tf in enumerate(TFS):
        wy.cell(2 + i, 2 + j, '=SUMIFS(Months!%s$2:%s$%d,Months!$B$2:$B$%d,$A%d)' % (CL(3 + j), CL(3 + j), n, n, 2 + i)).number_format = USD
posneg(wy, 'B2:%s7' % CL(1 + len(TFS)))
wy.cell(8, 1, '2026 = January to 2 October.').font = font(italic=True)
for j in range(1, 2 + len(TFS)): wy.column_dimensions[CL(j)].width = 18
wy.row_dimensions[1].height = 30
# Money rules
mr = wb.create_sheet('Money Rules')
heads = ['Timeframe', 'Money rule', 'Whole period from $1,000 ($)', 'Biggest drawdown', 'Blown?'] + ['%d (fresh $1,000)' % y for y in range(2021, 2027)] + ['Worst year drawdown', 'Months in profit (each fresh)']
for j, h in enumerate(heads): hdr(mr, 1, 1 + j, h)
r = 2
for tf in TFS:
    M = P[tf]['best']['money']
    for lab, d in sorted(M.items(), key=lambda kv: -kv[1]['all']['net']):
        row = [tf, lab, d['all']['net'], d['all']['dd'], 'yes' if d['all']['ruined'] else 'no'] + [d['years'][y]['net'] for y in range(2021, 2027)] + \
              [max(d['years'][y]['dd'] for y in range(2021, 2027)), '%d / %d' % (sum(v > 0 for v in d['months'].values()), len(d['months']))]
        fm = [None, None, USD, PCT, None] + [USD] * 6 + [PCT, None]
        for j, (v, f) in enumerate(zip(row, fm)): val(mr, r, 1 + j, v, f)
        r += 1
posneg(mr, 'C2:C%d' % (r - 1)); posneg(mr, 'F2:K%d' % (r - 1))
mr.column_dimensions['B'].width = 24
for j in range(3, 14): mr.column_dimensions[CL(j)].width = 13
mr.row_dimensions[1].height = 44; mr.freeze_panes = 'C2'; mr.auto_filter.ref = 'A1:M%d' % (r - 1)
# Hindsight
hs = wb.create_sheet('Hindsight')
hdr(hs, 1, 1, 'Month')
for j, tf in enumerate(TFS): hdr(hs, 1, 2 + 2 * j, '%s: best setting that month (R)' % tf); hdr(hs, 1, 3 + 2 * j, '%s: that setting' % tf)
for i, ym in enumerate(MONTHS):
    hs.cell(2 + i, 1, '%04d-%02d' % ym).font = font()
    for j, tf in enumerate(TFS):
        v, c = P[tf]['hindsight'].get(ym, (0.0, None))
        val(hs, 2 + i, 2 + 2 * j, round(v, 2), R1); hs.cell(2 + i, 3 + 2 * j, cfg_text(c) if c else '-').font = font(size=8)
hs.cell(3 + len(MONTHS), 1, 'Hindsight only: the setting that did best in that one month, found after the fact. It is a different setting almost every month - nobody can know it in advance.').font = font(italic=True)
for j in range(len(TFS)): hs.column_dimensions[CL(2 + 2 * j)].width = 11; hs.column_dimensions[CL(3 + 2 * j)].width = 40
hs.row_dimensions[1].height = 44; hs.freeze_panes = 'B2'
# Settings
st = wb.create_sheet('EA Settings')
hdr(st, 1, 1, 'EA input')
for j, tf in enumerate(TFS): hdr(st, 1, 2 + j, tf)
rows = None
for j, tf in enumerate(TFS):
    rows = ea_inputs(P[tf]['best']['cfg'])
    for i, (a, b) in enumerate(rows):
        st.cell(2 + i, 1, a).font = font(); val(st, 2 + i, 2 + j, b)
st.cell(3 + len(rows), 1, 'Everything else as your EA (news window, force-close 23:55, weekend close, max fills 10, half cap ...).').font = font(italic=True)
st.column_dimensions['A'].width = 38
for j in range(2, 2 + len(TFS)): st.column_dimensions[CL(j)].width = 24
nt = wb.create_sheet('Notes')
for i, t in enumerate(['Data: FxPro gold, Jan 2021 - 2 Oct 2026. H4 bars built from the H1 bars (4-hour blocks of the server day). Exits checked on M1 candles.',
                       'Your EA rules on every timeframe: the limit order at the next bar, news window 17:45 IST, force-close 23:55 IST, Saturday close, one trade at a time,',
                       'costs 0.23 per oz, targets pushed by the costs. Fixed $20 a trade unless a money rule is named; 1:100 leverage in the money-rule runs.',
                       'R = a trade\'s result as a multiple of its risk. Best settings are picked on the same years they are shown on - the honest check column shows what',
                       'happens when the pick is made on 2021-2023 only. Test any setting in the MT5 Strategy Tester on your broker before trading it.']):
    nt.cell(1 + i, 1, t).font = font()
nt.column_dimensions['A'].width = 150
wb.save(OUT); print('saved', OUT)
