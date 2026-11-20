"""File 2: the grid - the timeframes' best settings trading together (one account, $20 a trade on each), every month and year; every
combination of timeframes ranked. Run: python3 -I build_file2.py OUT.xlsx"""
import sys, pickle, collections, itertools
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as CL
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_xl import *
OUT = sys.argv[1]
P = pickle.load(open('picks.pkl', 'rb'))
TFS = [t for t in ('M1', 'M5', 'M15', 'H1', 'H4') if t in P]
TR = {tf: P[tf]['best']['trades'] for tf in TFS}
def mon(tfs):
    m = collections.defaultdict(float)
    for tf in tfs:
        for x in TR[tf]: m[(x['t'].year, x['t'].month)] += 20 * x['net']
    return m
def curve(tfs):                                      # the grid's closed balance trade by trade (by exit time), its biggest drawdown
    ev = sorted((x['tx'], 20 * x['net']) for tf in tfs for x in TR[tf])
    eq = pk = dd = 0.0
    for _, p in ev: eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
    return eq, dd
combos = []
for n in range(1, len(TFS) + 1):
    for cmb in itertools.combinations(TFS, n):
        m = mon(cmb); tot, dd = curve(cmb)
        combos.append((tot - 0.5 * dd, cmb, tot, dd, sum(m.get(k, 0) > 0 for k in MONTHS), min(m.get(k, 0.0) for k in MONTHS),
                       {y: sum(v for (yy, mm), v in m.items() if yy == y) for y in range(2021, 2027)}))
combos.sort(key=lambda c: -c[0])
best = combos[0][1]
wb = Workbook(); ws = wb.active; ws.title = 'Summary'
ws['A1'] = 'Gold, Auction Retest: the grid - every timeframe\'s best setting trading at the same time (one account, $20 a trade each)'; ws['A1'].font = font(bold=True, size=13)
ws['A2'] = 'Each timeframe runs its own EA copy (one trade at a time per timeframe); their trades add up in one account. Best grid = most profit minus half its biggest drawdown.'; ws['A2'].font = font(italic=True)
heads = ['Grid', 'Timeframes', 'Total profit 2021-2026 ($)', 'Biggest drawdown ($)', 'Months in profit', 'Worst month ($)'] + [str(y) for y in range(2021, 2027)]
for j, h in enumerate(heads): hdr(ws, 4, 1 + j, h)
alls = next(c for c in combos if c[1] == tuple(TFS))
for i, (lab, c) in enumerate((('All timeframes together', alls), ('Best grid (best combination)', combos[0]))):
    row = [lab, ' + '.join(c[1]), c[2], c[3], '%d / %d' % (c[4], len(MONTHS)), c[5]] + [c[6][y] for y in range(2021, 2027)]
    fm = [None, None, USD, USD, None, USD] + [USD] * 6
    for j, (v, f) in enumerate(zip(row, fm)): val(ws, 5 + i, 1 + j, v, f)
r = 8; hdr(ws, r, 1, 'Each timeframe alone')
for j, h in enumerate(heads[1:]): hdr(ws, r, 2 + j, h)
for i, tf in enumerate(TFS):
    c = next(x for x in combos if x[1] == (tf,))
    row = ['', tf, c[2], c[3], '%d / %d' % (c[4], len(MONTHS)), c[5]] + [c[6][y] for y in range(2021, 2027)]
    for j, (v, f) in enumerate(zip(row, [None, None, USD, USD, None, USD] + [USD] * 6)): val(ws, r + 1 + i, 1 + j, v, f)
posneg(ws, 'C5:L%d' % (r + len(TFS)))
ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 26
for j in range(3, 13): ws.column_dimensions[CL(j)].width = 13
ws.row_dimensions[4].height = 30
# Months: each TF + the two grids
wm = wb.create_sheet('Months')
cols = TFS + ['ALL', 'BEST']
hdr(wm, 1, 1, 'Month'); hdr(wm, 1, 2, 'Year')
for j, c in enumerate(cols): hdr(wm, 1, 3 + j, {'ALL': 'Grid: all timeframes ($)', 'BEST': 'Grid: best combination %s ($)' % '+'.join(best)}.get(c, '%s ($)' % c))
M = {tf: mon((tf,)) for tf in TFS}
for i, ym in enumerate(MONTHS):
    r = 2 + i; wm.cell(r, 1, '%04d-%02d' % ym).font = font(); wm.cell(r, 2, str(ym[0])).font = font()
    for j, tf in enumerate(TFS): val(wm, r, 3 + j, round(M[tf].get(ym, 0.0), 2), USD)
    wm.cell(r, 3 + len(TFS), '=SUM(C%d:%s%d)' % (r, CL(2 + len(TFS)), r)).number_format = USD
    wm.cell(r, 4 + len(TFS), '=' + '+'.join('%s%d' % (CL(3 + TFS.index(tf)), r) for tf in best)).number_format = USD
n = 1 + len(MONTHS)
posneg(wm, 'C2:%s%d' % (CL(2 + len(cols)), n))
wm.cell(n + 1, 1, 'Total').font = font(bold=True); wm.cell(n + 2, 1, 'Months in profit').font = font(bold=True)
for j in range(len(cols)):
    c = CL(3 + j); wm.cell(n + 1, 3 + j, '=SUM(%s2:%s%d)' % (c, c, n)).number_format = USD; wm.cell(n + 2, 3 + j, '=COUNTIF(%s2:%s%d,">0")' % (c, c, n))
wm.freeze_panes = 'C2'
for j in range(3, 3 + len(cols)): wm.column_dimensions[CL(j)].width = 16
wm.row_dimensions[1].height = 44
# Years
wy = wb.create_sheet('Years')
hdr(wy, 1, 1, 'Year')
for j, c in enumerate(cols): hdr(wy, 1, 2 + j, wm.cell(1, 3 + j).value)
for i, y in enumerate(range(2021, 2027)):
    wy.cell(2 + i, 1, str(y)).font = font()
    for j in range(len(cols)):
        wy.cell(2 + i, 2 + j, '=SUMIFS(Months!%s$2:%s$%d,Months!$B$2:$B$%d,$A%d)' % (CL(3 + j), CL(3 + j), n, n, 2 + i)).number_format = USD
posneg(wy, 'B2:%s7' % CL(1 + len(cols)))
for j in range(1, 2 + len(cols)): wy.column_dimensions[CL(j)].width = 18
wy.row_dimensions[1].height = 44
# Combinations
cb = wb.create_sheet('All Combinations')
for j, h in enumerate(['Rank', 'Timeframes', 'Score (profit - half drawdown)', 'Total profit ($)', 'Biggest drawdown ($)', 'Months in profit', 'Worst month ($)'] + [str(y) for y in range(2021, 2027)]):
    hdr(cb, 1, 1 + j, h)
for i, c in enumerate(combos):
    row = [i + 1, ' + '.join(c[1]), c[0], c[2], c[3], c[4], c[5]] + [c[6][y] for y in range(2021, 2027)]
    for j, (v, f) in enumerate(zip(row, [None, None, USD, USD, USD, None, USD] + [USD] * 6)): val(cb, 2 + i, 1 + j, v, f)
posneg(cb, 'D2:D%d' % (1 + len(combos))); posneg(cb, 'H2:M%d' % (1 + len(combos)))
cb.column_dimensions['B'].width = 28
for j in range(3, 14): cb.column_dimensions[CL(j)].width = 13
cb.row_dimensions[1].height = 44
nt = wb.create_sheet('Notes')
for i, t in enumerate(['Grid = one EA copy per timeframe on the same account, each with its own best setting (File 1) and $20 a trade. Trades on different timeframes can be',
                       'open at the same time (more exposure); each copy takes one trade at a time. Drawdown measured on the combined closed balance, trade by trade.',
                       'Daily (D1) takes no trades with your EA rules. The settings were picked on 2021-2026, so these numbers are a best case.']):
    nt.cell(1 + i, 1, t).font = font()
nt.column_dimensions['A'].width = 150
wb.save(OUT); print('saved', OUT, 'best grid', best)
