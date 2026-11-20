"""Order block test workbook. Run: python3 -I ob_xlsx.py OUT.xlsx"""
import sys, os, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../nt6')
from openpyxl import Workbook
from openpyxl.utils import get_column_letter as CL
from common_xl import font, hdr, val, posneg, USD, PCT
import ob_summary as SM
OUT = sys.argv[1]; L = SM.L
R = pickle.load(open('ob_results.pkl', 'rb'))
wb = Workbook(); ws = wb.active; ws.title = 'Summary'
ws['A1'] = 'Gold 2026 (Jan - 2 Oct): order block + absorption + aggression, entry at market'; ws['A1'].font = font(bold=True, size=13)
ws['A2'] = ('Per row: how many entries, the share that reached each target (R = the stop distance) before the stop, and the net result per trade if you '
            'took profit there (costs 0.23 per oz included; a stop = -1R).'); ws['A2'].font = font(italic=True)
heads = ['Entry TF', 'Order block TF', 'Stop', 'Filters', 'Entries', 'Avg stop ($ per oz)'] + ['Reached %sR' % lv for lv in L] + ['Net R/trade at %sR' % lv for lv in L] + ['Best target', 'Best net R/trade', 'Total R at best']
for j, h in enumerate(heads): hdr(ws, 4, 1 + j, h)
r = 5
for ltf, htf, st, fl, xs, hit, net in SM.rows():
    b = net.index(max(net))
    row = [ltf, htf, 'below / above the aggression candle' if st == 'candle' else 'beyond the latest swing', 'kill zones + 06-23 + news' if fl else 'none',
           len(xs), sum(x['risk'] for x in xs) / len(xs)] + hit + net + ['%sR' % L[b], net[b], net[b] * len(xs)]
    fm = [None, None, None, None, '#,##0', '0.00'] + [PCT] * 9 + ['+0.00;-0.00;0.00'] * 9 + [None, '+0.000;-0.000;0', '+0.0;-0.0;0']
    for j, (v, f) in enumerate(zip(row, fm)): val(ws, r, 1 + j, v, f)
    r += 1
posneg(ws, 'P5:AA%d' % (r - 1))
ws.column_dimensions['C'].width = 30; ws.column_dimensions['D'].width = 22
for j in range(5, 28): ws.column_dimensions[CL(j)].width = 9
ws.row_dimensions[4].height = 44; ws.freeze_panes = 'E5'
k = r + 1
for t in ['What it shows:',
          '- M1 and M5 entries lose after costs at every target, with and without your filters: the entries win often at small targets (75-90% reach 0.1R)',
          '  but a small target pays far less than a stop costs, and at 1R+ the hit rate falls below what the costs need.',
          '- Only M15 entries on H4 order blocks are positive: +0.09R a trade at 1R (no filters, 75 trades) and +0.20R with your filters (36 trades).',
          '  That is a small sample in nine months - it needs more data (2021-2025) before trusting it.',
          '- The swing stop is wider (about 1.6x) and does not improve the results.']:
    ws.cell(k, 1, t).font = font(bold=t.endswith(':')); k += 1
# Monthly at 1R and at each row's best target
wm = wb.create_sheet('Months')
months = sorted({(x['t'].year, x['t'].month) for x in R})
hdr(wm, 1, 1, 'Setup'); hdr(wm, 1, 2, 'Target')
for j, (y, m) in enumerate(months): hdr(wm, 1, 3 + j, '%04d-%02d' % (y, m))
hdr(wm, 1, 3 + len(months), 'Total R'); hdr(wm, 1, 4 + len(months), 'Months in profit')
r = 2
for ltf, htf, st, fl, xs, hit, net in SM.rows():
    b = net.index(max(net))
    for lv in sorted({1.0, L[b]}):
        wm.cell(r, 1, '%s / %s OB / %s stop / %s' % (ltf, htf, st, 'filters' if fl else 'no filters')).font = font(); wm.cell(r, 2, '%sR' % lv).font = font()
        for j, ym in enumerate(months):
            v = sum(SM.netR(x, lv) for x in xs if (x['t'].year, x['t'].month) == ym)
            val(wm, r, 3 + j, round(v, 2), '+0.0;-0.0;0')
        c1, c2 = CL(3), CL(2 + len(months))
        wm.cell(r, 3 + len(months), '=SUM(%s%d:%s%d)' % (c1, r, c2, r)).number_format = '+0.0;-0.0;0'
        wm.cell(r, 4 + len(months), '=COUNTIF(%s%d:%s%d,">0")' % (c1, r, c2, r))
        r += 1
posneg(wm, 'C2:%s%d' % (CL(3 + len(months)), r - 1))
wm.column_dimensions['A'].width = 44
for j in range(3, 5 + len(months)): wm.column_dimensions[CL(j)].width = 9
wm.freeze_panes = 'C2'
# trades
wt = wb.create_sheet('Trades')
for j, h in enumerate(['Entry TF', 'OB TF', 'Stop', 'Direction', 'Entry time (IST)', 'Entry price', 'Stop distance', 'Best move before the stop (R)', 'Stopped', 'In your filters']):
    hdr(wt, 1, 1 + j, h)
for i, x in enumerate(sorted(R, key=lambda x: (x['ltf'], x['htf'], x['stop'], x['t']))):
    row = [x['ltf'], x['htf'], x['stop'], 'buy' if x['dir'] == 1 else 'sell', x['t'], x['entry'], round(x['risk'], 2), round(x['mfe'], 2), 'yes' if x['stopped'] else 'no', 'yes' if x['filt'] else 'no']
    for j, v in enumerate(row):
        c = wt.cell(2 + i, 1 + j, v); c.font = font()
        if j == 4: c.number_format = 'yyyy-mm-dd hh:mm'
wt.auto_filter.ref = 'A1:J%d' % (1 + len(R)); wt.freeze_panes = 'A2'
for j, w in enumerate([8, 8, 8, 8, 17, 11, 11, 14, 9, 11]): wt.column_dimensions[CL(1 + j)].width = w
nt = wb.create_sheet('Rules')
for i, t in enumerate(open('ob_test.py').read().split('"""')[1].split('\n')): nt.cell(1 + i, 1, t).font = font()
nt.column_dimensions['A'].width = 150
wb.save(OUT); print('saved', OUT)
