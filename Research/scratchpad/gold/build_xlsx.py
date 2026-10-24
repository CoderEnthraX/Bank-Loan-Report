"""Workbook: per-timeframe year x month tables (counts from the backtest, rates and totals as formulas) + summary + research."""
import sys, pickle, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); import geng
F = 'Arial'
HDR = PatternFill('solid', fgColor='1F3864'); YR = PatternFill('solid', fgColor='D9E1F2'); TOT = PatternFill('solid', fgColor='FFE699')
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
COLS = ['Year', 'Month', 'Trades', 'Wins (final target)', 'TP1 hits', 'TP2 hits', 'TP3 hits', 'TP4 hits', 'Breakeven exits', 'Total R',
        'Spread cost (R)', 'Total R after spread', 'Longest win streak', 'Longest losing streak',
        'Win %', 'TP1 %', 'TP2 %', 'TP3 %', 'TP4 %', 'R per trade', 'R per trade after spread']
def norm(tr):
    """accept full dicts (geng.run) or compact tuples (grid pickles)"""
    out = []
    for x in tr:
        if isinstance(x, dict): out.append((x['t'], x['res'], x['win'], tuple(x['hits']), x['sp'], x['risk'], x['be']))
        else: out.append(x)
    return out
def counts(tr):
    n = len(tr); res = [x[1] for x in tr]; mw, ml, _ = geng.streaks(res)
    return dict(n=n, w=sum(1 for x in tr if x[2]), h=[sum(1 for x in tr if x[3][k]) for k in range(4)], be=sum(1 for x in tr if x[6]),
                R=sum(res), cost=sum(x[4] / x[5] for x in tr), mw=mw, ml=ml)
def tf_sheet(wb, title, tr, note):
    tr = norm(tr); ws = wb.create_sheet(title)
    ws['A1'] = note; ws['A1'].font = Font(name=F, bold=True, size=11)
    ws['A2'] = ('Counts, R and streaks are backtest results (blue). Percentages, R per trade and all totals are formulas. Months = IST date of the fill. '
                'Streaks are counted inside each month / year (a streak running across a month boundary is split); the yearly and all-years streaks use the full sequence.')
    ws['A2'].font = Font(name=F, italic=True, size=9); ws.merge_cells('A2:U2'); ws['A2'].alignment = Alignment(wrap_text=True); ws.row_dimensions[2].height = 30
    r0 = 4
    for j, c in enumerate(COLS, 1):
        cell = ws.cell(r0, j, c); cell.font = Font(name=F, bold=True, color='FFFFFF', size=9); cell.fill = HDR
        cell.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); cell.border = BOX
    ws.row_dimensions[r0].height = 42
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for x in tr: by[x[0].year][x[0].month].append(x)
    r = r0 + 1; yrows = []
    def put(row, y, m, c, fill=None, bold=False, sumrange=None, streak=None):
        ws.cell(row, 1, y); ws.cell(row, 2, m)
        if sumrange is None:
            vals = [c['n'], c['w'], *c['h'], c['be'], round(c['R'], 4), round(c['cost'], 4)]
            for j, v in enumerate(vals, 3):
                ws.cell(row, j, v).font = Font(name=F, color='0000FF', size=9)
        else:
            for j in range(3, 12):
                L = get_column_letter(j); ws.cell(row, j, sumrange(L)).font = Font(name=F, bold=bold, size=9)
        ws.cell(row, 12, '=J%d-K%d' % (row, row))
        mw, ml = streak if streak else (c['mw'], c['ml'])
        ws.cell(row, 13, mw).font = Font(name=F, color='0000FF', size=9, bold=bold); ws.cell(row, 14, ml).font = Font(name=F, color='0000FF', size=9, bold=bold)
        for j, num in ((15, 'D'), (16, 'E'), (17, 'F'), (18, 'G'), (19, 'H')):
            ws.cell(row, j, '=IF($C%d=0,"",%s%d/$C%d)' % (row, num, row, row)).number_format = '0.0%'
        ws.cell(row, 20, '=IF($C%d=0,"",J%d/$C%d)' % (row, row, row)).number_format = '0.000'
        ws.cell(row, 21, '=IF($C%d=0,"",L%d/$C%d)' % (row, row, row)).number_format = '0.000'
        for j in range(1, 22):
            cell = ws.cell(row, j); cell.border = BOX
            if cell.font.name != F or (j in (1, 2, 12) or j >= 15): cell.font = Font(name=F, size=9, bold=bold, color=cell.font.color.rgb if (cell.font and cell.font.color and j in (13, 14)) else None)
            if fill: cell.fill = fill
        for j in (10, 11, 12): ws.cell(row, j).number_format = '0.00'
    for y in sorted(by):
        first = r
        for m in range(1, 13):
            if y == 2026 and m > 10: break
            put(r, y, MON[m - 1], counts(by[y].get(m, [])) if by[y].get(m) else dict(n=0, w=0, h=[0, 0, 0, 0], be=0, R=0, cost=0, mw=0, ml=0)); r += 1
        last = r - 1; yt = [x for m in sorted(by[y]) for x in by[y][m]]; c = counts(yt)
        put(r, '%d total' % y, 'All', c, fill=YR, bold=True, sumrange=lambda L, a=first, b=last: '=SUM(%s%d:%s%d)' % (L, a, L, b), streak=(c['mw'], c['ml']))
        yrows.append(r); r += 1
    ca = counts(tr)
    put(r, '2021-2026 total', 'All', ca, fill=TOT, bold=True, sumrange=lambda L: '=' + '+'.join('%s%d' % (L, k) for k in yrows), streak=(ca['mw'], ca['ml']))
    ws.cell(r, 14).comment = Comment('Longest losing streak over the whole 2021-2026 trade sequence (backtest result).', 'backtest')
    widths = [14, 7, 8, 9, 8, 8, 8, 8, 9, 9, 9, 10, 9, 9, 8, 8, 8, 8, 8, 9, 10]
    for j, wd in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = wd
    ws.freeze_panes = 'C5'
    return {y: row for y, row in zip(sorted(by), yrows)}, r
def summary_sheet(wb, refs, title='Summary', heading='Default settings: accuracy per timeframe and year'):
    ws = wb.create_sheet(title, 1)
    ws['A1'] = heading; ws['A1'].font = Font(name=F, bold=True, size=12)
    ws['A2'] = 'All values link to the year-total rows of each timeframe sheet.'; ws['A2'].font = Font(name=F, italic=True, size=9)
    hd = ['Timeframe', 'Year', 'Trades', 'Win %', 'TP1 %', 'TP2 %', 'TP3 %', 'TP4 %', 'Total R', 'Total R after spread', 'R per trade', 'R per trade after spread', 'Longest win streak', 'Longest losing streak']
    for j, c in enumerate(hd, 1):
        cell = ws.cell(4, j, c); cell.font = Font(name=F, bold=True, color='FFFFFF', size=9); cell.fill = HDR; cell.alignment = Alignment(wrap_text=True, horizontal='center'); cell.border = BOX
    ws.row_dimensions[4].height = 30; r = 5
    for sheet, (yrows, tot) in refs:
        for y, row in list(yrows.items()) + [('2021-2026', tot)]:
            q = "'%s'!" % sheet
            vals = [sheet, str(y), '=%sC%d' % (q, row), '=%sO%d' % (q, row), '=%sP%d' % (q, row), '=%sQ%d' % (q, row), '=%sR%d' % (q, row), '=%sS%d' % (q, row),
                    '=%sJ%d' % (q, row), '=%sL%d' % (q, row), '=%sT%d' % (q, row), '=%sU%d' % (q, row), '=%sM%d' % (q, row), '=%sN%d' % (q, row)]
            for j, v in enumerate(vals, 1):
                cell = ws.cell(r, j, v); cell.border = BOX
                cell.font = Font(name=F, size=9, bold=(y == '2021-2026'), color='008000' if j > 2 else None)
                if y == '2021-2026': cell.fill = TOT
                if 4 <= j <= 8: cell.number_format = '0.0%'
                elif j in (9, 10): cell.number_format = '0.0'
                elif j in (11, 12): cell.number_format = '0.000'
            r += 1
        r += 1
    for j, wd in enumerate([10, 11, 8, 8, 8, 8, 8, 8, 9, 11, 9, 11, 9, 10], 1): ws.column_dimensions[get_column_letter(j)].width = wd
    ws.freeze_panes = 'C5'
if __name__ == '__main__':
    base = pickle.load(open(S + '/gold/base_trades.pkl', 'rb'))
    wb = Workbook(); rd = wb.active; rd.title = 'Read me'
    lines = ['Auction Retest indicator on FxPro MT5 GOLD, 4 Jan 2021 - 2 Oct 2026 (user-supplied 1-minute data)', '',
             'Data: 2,037,975 one-minute bars from the MT5 export; 441 fake 00:00 "daily summary" bars removed. M5 / M15 / H1 built from M1 on the server clock.',
             'Broker clock: EET (UTC+2 winter, UTC+3 from the last Sunday of March to the last Sunday of October), found from the daily trading break.',
             'Engine: the same engine as the TradingView indicator / strategy and the MT5 EA (Python twin, verified trade-for-trade against the EA).',
             'Sessions / VWAP reset: broker server midnight (as in the EA). VWAP weights: tick volume (as in the EA).',
             'Default settings: displacement + 5-bar retest, 1.8 ATR stop (half stop rules on), TP1-TP4 = 0.6 / 1 / 1.5 / 2 R, final exit at TP4 (2R), max 5 fills a day.',
             'TPk hit: price reached that target after the fill bar and before the stop (a bar touching both counts as the stop). Win = closed at the final target.',
             'R = result in units of the stop distance. Spread cost = the bar spread from the MT5 data at the fill, divided by the stop distance.',
             'Longest win / losing streak: most consecutive wins / losses (a breakeven exit ends both).',
             'Blue = results from the backtest. Black = formulas. Green = links to another sheet.', '',
             'Sheets: Summary (default settings, per timeframe and year) | M1, M5, M15, H1 (default settings, year x month) | Research and best-settings sheets.']
    for i, t in enumerate(lines, 1):
        rd.cell(i, 1, t).font = Font(name=F, bold=(i == 1), size=11 if i == 1 else 10)
    rd.column_dimensions['A'].width = 150
    refs = []
    for tf in ('M1', 'M5', 'M15', 'H1'):
        yrows, tot = tf_sheet(wb, tf, base[tf], 'Default settings on %s - accuracy per year and month' % tf)
        refs.append((tf, (yrows, tot)))
    summary_sheet(wb, refs)
    out = sys.argv[1] if len(sys.argv) > 1 else S + '/gold/Gold_2021_2026_Auction_Retest.xlsx'
    wb.save(out); print('saved', out)
