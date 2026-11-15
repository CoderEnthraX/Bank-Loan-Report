"""Monthly Crooks E-J x profit ladder workbooks (asked 2026-11-15):
  Gold_Monthly_Crooks_EJ_Fractal_Grid.xlsx      the grid, all strategies on a gold M5 chart, then on an M15 chart
  Gold_Monthly_Crooks_EJ_Auction_Retest.xlsx    the Auction Retest M5 strategies, then the M15 strategies
from mcej/grid_money.pkl, ars_money.pkl, ars_targets.pkl (money.py, targets.py). Formulas for every total / count / year / balance."""
import sys, pickle, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.comments import Comment

S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
OUT = sys.argv[1] if len(sys.argv) > 1 else S + '/mcej'
F = 'Arial'
USD = '$#,##0;[Red]-$#,##0'; CNT = '0'; AVGC = '0.0'; PCT = '0%'; MONF = 'mmm yyyy'
f_norm = Font(name=F, size=10); f_bold = Font(name=F, size=10, bold=True); f_title = Font(name=F, size=13, bold=True)
f_hdr = Font(name=F, size=10, bold=True, color='FFFFFF'); f_small = Font(name=F, size=8, color='595959'); f_note = Font(name=F, size=9, italic=True, color='404040')
f_blue = Font(name=F, size=10, color='0000FF'); f_green = Font(name=F, size=10, color='008000'); f_greenb = Font(name=F, size=10, color='008000', bold=True)
f_block = Font(name=F, size=11, bold=True, color='1F3864')
fill_hdr = PatternFill('solid', fgColor='1F3864'); fill_hdr2 = PatternFill('solid', fgColor='2F5597')
fill_on = PatternFill('solid', fgColor='E2EFDA'); fill_guard = PatternFill('solid', fgColor='FCE4D6'); fill_stat = PatternFill('solid', fgColor='F2F2F2')
center = Alignment(horizontal='center', vertical='center', wrap_text=True); left = Alignment(horizontal='left', vertical='top', wrap_text=True)
thin = Side(style='thin', color='BFBFBF'); bleft = Border(left=Side(style='medium', color='1F3864'))
LEVELS = ('Off', 'Low', 'Medium', 'High', 'Extra high', 'Max')
RULES = ('Crooks E', 'Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')
CONFIGS = [('Crooks E', 'Off')] + [(r, l) for r in RULES[1:] for l in LEVELS]
C0 = 5                                                     # first rule / level column (E)
NC = len(CONFIGS); CL = C0 + NC - 1                         # last column (AI)
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
LADP = {'Low': (0.8, 0.10, 2.0, 0.25), 'Medium': (0.7, 0.15, 3.0, 0.30), 'High': (0.6, 0.20, 5.0, 0.35), 'Extra high': (0.5, 0.25, 8.0, 0.40), 'Max': (0.4, 0.30, 12.0, 0.50)}


def q(name): return "'" + name.replace("'", "''") + "'"
def mdate(m): return dt.date(int(m[:4]), int(m[5:]), 1)
def mtxt(m): return '%s %s' % (MON[int(m[5:]) - 1], m[:4])
def cfgname(c): return '%s %s' % (c[0], 'no ladder' if c[0] == 'Crooks E' else ('ladder Off' if c[1] == 'Off' else c[1]))
def usd(x): return ('-$%s' % format(-x, ',.0f')) if x < 0 else '+$%s' % format(x, ',.0f')


def header(ws, r, first_label='Month', cnt_labels=('Trades', 'Wins', 'Losses'), fullnames=False):
    """two header rows at r, r+1: A-D merged vertically, a rule name merged over its levels, the level names"""
    for j, t in enumerate((first_label,) + tuple(cnt_labels)):
        c = ws.cell(r, 1 + j, t); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
        ws.cell(r + 1, 1 + j).fill = fill_hdr
        ws.merge_cells(start_row=r, start_column=1 + j, end_row=r + 1, end_column=1 + j)
    j = 0
    for k, rule in enumerate(RULES):
        n = 1 if rule == 'Crooks E' else len(LEVELS); fl = fill_hdr if k % 2 == 0 else fill_hdr2
        c = ws.cell(r, C0 + j, rule + (' (no ladder)' if rule == 'Crooks E' else ' - profit ladder level')); c.font = f_hdr; c.fill = fl; c.alignment = center
        for t in range(n):
            ws.cell(r, C0 + j + t).fill = fl
            c2 = ws.cell(r + 1, C0 + j + t, 'Off' if rule == 'Crooks E' else LEVELS[t]); c2.font = f_hdr; c2.fill = fl; c2.alignment = center
        if n > 1: ws.merge_cells(start_row=r, start_column=C0 + j, end_row=r, end_column=C0 + j + n - 1)
        j += n
    if fullnames:
        for j, cfg in enumerate(CONFIGS):
            c = ws.cell(r + 2, C0 + j, cfgname(cfg)); c.font = f_small; c.alignment = center
    ws.row_dimensions[r].height = 27


def block_title(ws, r, text, note=None):
    c = ws.cell(r, 1, text); c.font = f_block
    if note: ws.cell(r + 1, 1, note).font = f_note; return r + 2
    return r + 1


STATS = [('Total', 'SUM', USD), ('Months in profit', 'PROF', CNT), ('Months in loss', 'LOSS', CNT), ('Worst month', 'MIN', USD), ('Best month', 'MAX', USD),
         ('Average month', 'AVERAGE', USD)]


def stat_formula(kind, rng):
    return {'SUM': '=SUM(%s)' % rng, 'PROF': '=COUNTIF(%s,">0")' % rng, 'LOSS': '=COUNTIF(%s,"<0")' % rng, 'MIN': '=MIN(%s)' % rng,
            'MAX': '=MAX(%s)' % rng, 'AVERAGE': '=AVERAGE(%s)' % rng}[kind]


def stat_rows(ws, r, first, last, stats=STATS, cnt_cols=(2, 3, 4)):
    """stats rows below a month block; returns {kind: row}"""
    pos = {}
    for lab, kind, fmt in stats:
        c = ws.cell(r, 1, lab + (' 2021-2026' if kind == 'SUM' else '')); c.font = f_bold; c.fill = fill_stat
        for col in list(cnt_cols) + list(range(C0, CL + 1)):
            if col in cnt_cols and kind != 'SUM':
                ws.cell(r, col).fill = fill_stat; continue
            cc = ws.cell(r, col, stat_formula(kind, '%s%d:%s%d' % (L(col), first, L(col), last)))
            cc.font = f_bold; cc.fill = fill_stat; cc.number_format = CNT if (col in cnt_cols or fmt == CNT) else fmt
        pos[kind] = r; r += 1
    return r, pos


def monthly_sheet(wb, name, title, settings, start, months, cnt, data, legend_guard=True, fresh_note=''):
    """data[cfg] = dict(cont={m: dict(net, drop, ladOn, guard)}, fresh={m: dict(net)}); cnt[m] = dict(n, w, l, nStart, wStart, lStart)"""
    ws = wb.create_sheet(name); ws.sheet_properties.tabColor = '2F5597'
    ws['A1'] = title; ws['A1'].font = f_title
    ws['A2'] = 'Start balance ($)'; ws['A2'].font = f_bold
    c = ws['B2']; c.value = start; c.font = f_blue; c.number_format = USD
    c.comment = Comment('The start balance the simulation used (each strategy: $10,000). The monthly results were computed with it: changing this cell only moves the '
                        'balances of block 3, it does not re-run the trades.', 'Claude')
    ws['E2'] = settings; ws['E2'].font = f_note
    ws['E3'] = 'Ladder on'; ws['E3'].fill = fill_on; ws['E3'].font = f_norm; ws['E3'].alignment = center
    ws['F3'] = 'Guard 0.01 lot'; ws['F3'].fill = fill_guard; ws['F3'].font = f_norm; ws['F3'].alignment = center
    ws['G3'] = ('Shading in blocks 1 and 4: green = the profit ladder was on for at least one trade closed that month; orange = at least one trade was the '
                "ladder's 0.01-lot start guard (the profit had fallen to $0 or below after reaching the $1,000 target).")
    ws['G3'].font = f_note
    ws.column_dimensions['A'].width = 24
    for col in (2, 3, 4): ws.column_dimensions[L(col)].width = 8
    for col in range(C0, CL + 1): ws.column_dimensions[L(col)].width = 11.5
    M = months; nM = len(M); pos = {}
    # 1. profit per month (one account)
    r = block_title(ws, 5, '1. Profit / loss of each month ($): ONE account from January 2021, every trade counted in the month it closed')
    header(ws, r); FIRST = r + 2; LAST = FIRST + nM - 1; pos['FIRST'], pos['LAST'] = FIRST, LAST
    for i, m in enumerate(M):
        rr = FIRST + i
        c = ws.cell(rr, 1, mdate(m)); c.number_format = MONF; c.font = f_norm; c.alignment = Alignment(horizontal='left')
        if i == nM - 1 and m == '2026-10': c.comment = Comment('The gold data ends on 2 Oct 2026: this month has only its first 2 days.', 'Claude')
        for j, k in enumerate(('n', 'w', 'l')):
            cc = ws.cell(rr, 2 + j, cnt[m][k]); cc.font = f_norm; cc.number_format = CNT
        for j, cfg in enumerate(CONFIGS):
            v = data[cfg]['cont'][m]
            cc = ws.cell(rr, C0 + j, float(v['net'])); cc.font = f_norm; cc.number_format = USD
            if v.get('guard'): cc.fill = fill_guard
            elif v.get('ladOn'): cc.fill = fill_on
    r, st1 = stat_rows(ws, LAST + 1, FIRST, LAST); pos['m'] = st1
    # 2. per year (formulas)
    r = block_title(ws, r + 1, '2. Profit / loss of each year ($): the months of block 1 added up (formulas)')
    header(ws, r, 'Year'); Y0 = r + 2; years = sorted({m[:4] for m in M}); pos['Y0'] = Y0
    for i, y in enumerate(years):
        rr = Y0 + i; lab = y + (' (to 2 Oct)' if y == '2026' else '')
        ws.cell(rr, 1, lab).font = f_norm
        crit = '$A$%d:$A$%d,">="&DATE(%s,1,1),$A$%d:$A$%d,"<"&DATE(%d,1,1)' % (FIRST, LAST, y, FIRST, LAST, int(y) + 1)
        for col in [2, 3, 4] + list(range(C0, CL + 1)):
            cc = ws.cell(rr, col, '=SUMIFS(%s$%d:%s$%d,%s)' % (L(col), FIRST, L(col), LAST, crit)); cc.font = f_norm
            cc.number_format = CNT if col < C0 else USD
    r = Y0 + len(years)
    rr = r; ws.cell(rr, 1, 'Years in loss').font = f_bold
    for col in range(C0, CL + 1):
        cc = ws.cell(rr, col, '=COUNTIF(%s%d:%s%d,"<0")' % (L(col), Y0, L(col), Y0 + len(years) - 1)); cc.font = f_bold; cc.fill = fill_stat; cc.number_format = CNT
    ws.cell(rr, 1).fill = fill_stat; pos['YLOSS'] = rr; r = rr + 1
    # 3. balance (formulas)
    r = block_title(ws, r + 1, '3. Balance at the end of each month ($): start balance (B2) + the months of block 1 so far (formulas)')
    header(ws, r); B0 = r + 2
    for i, m in enumerate(M):
        rr = B0 + i
        c = ws.cell(rr, 1, mdate(m)); c.number_format = MONF; c.font = f_norm; c.alignment = Alignment(horizontal='left')
        for col in range(C0, CL + 1):
            cc = ws.cell(rr, col, '=$B$2+SUM(%s$%d:%s%d)' % (L(col), FIRST, L(col), FIRST + i)); cc.font = f_norm; cc.number_format = USD
    BL = B0 + nM - 1; pos['BAL_END'] = BL; r = BL + 1
    for lab, fn in (('Lowest month-end balance', 'MIN'), ('Highest month-end balance', 'MAX')):
        ws.cell(r, 1, lab).font = f_bold; ws.cell(r, 1).fill = fill_stat
        for col in range(C0, CL + 1):
            cc = ws.cell(r, col, '=%s(%s%d:%s%d)' % (fn, L(col), B0, L(col), BL)); cc.font = f_bold; cc.fill = fill_stat; cc.number_format = USD
        pos['BAL_' + fn] = r; r += 1
    # 4. deepest drop inside the month (values)
    r = block_title(ws, r + 1, "4. Deepest drop inside each month ($): from the month's highest balance to the lowest balance after it (closed trades, one account)")
    header(ws, r); D0 = r + 2
    for i, m in enumerate(M):
        rr = D0 + i
        c = ws.cell(rr, 1, mdate(m)); c.number_format = MONF; c.font = f_norm; c.alignment = Alignment(horizontal='left')
        for j, cfg in enumerate(CONFIGS):
            v = data[cfg]['cont'][m]
            cc = ws.cell(rr, C0 + j, float(v['drop'])); cc.font = f_norm; cc.number_format = USD
            if v.get('guard'): cc.fill = fill_guard
            elif v.get('ladOn'): cc.fill = fill_on
    DL = D0 + nM - 1; r = DL + 1
    for lab, fn in (('Deepest month', 'MAX'), ('Average month', 'AVERAGE')):
        ws.cell(r, 1, lab).font = f_bold; ws.cell(r, 1).fill = fill_stat
        for col in range(C0, CL + 1):
            cc = ws.cell(r, col, '=%s(%s%d:%s%d)' % (fn, L(col), D0, L(col), DL)); cc.font = f_bold; cc.fill = fill_stat; cc.number_format = USD
        pos['DROP_' + fn] = r; r += 1
    # 5. each month on its own (values)
    r = block_title(ws, r + 1, '5. Each month ON ITS OWN ($): a fresh $10,000 account (per strategy) and a fresh recovery / ladder state on the 1st; '
                    'the trades that START in the month', fresh_note)
    header(ws, r, 'Month', ('Trades started', 'Wins', 'Losses')); E0 = r + 2
    for i, m in enumerate(M):
        rr = E0 + i
        c = ws.cell(rr, 1, mdate(m)); c.number_format = MONF; c.font = f_norm; c.alignment = Alignment(horizontal='left')
        for j, k in enumerate(('nStart', 'wStart', 'lStart')):
            cc = ws.cell(rr, 2 + j, cnt[m][k]); cc.font = f_norm; cc.number_format = CNT
        for j, cfg in enumerate(CONFIGS):
            cc = ws.cell(rr, C0 + j, float(data[cfg]['fresh'][m]['net'])); cc.font = f_norm; cc.number_format = USD
    EL = E0 + nM - 1
    r, st5 = stat_rows(ws, EL + 1, E0, EL); pos['f'] = st5
    ws.freeze_panes = ws.cell(FIRST, C0)
    for col in range(C0, CL + 1):
        if col in (C0, C0 + 1) or (col - C0 - 1) % 6 == 0:          # a line before each rule group
            for rr in range(5, r): ws.cell(rr, col).border = bleft
    return ws, pos


def summary_block(ws, r, title, rows, kind, fmt, note=None, scale=None):
    """rows: [(label, name, trades, sheet, pos, extra)]; kind: a pos key path or a callable(row, j) -> value"""
    r = block_title(ws, r, title, note)
    header(ws, r, 'Strategy', ('Name', 'Trades', ''), fullnames=True); r0 = r + 3
    for i, (lab, nm, ntr, sheet, pos, ex) in enumerate(rows):
        rr = r0 + i
        ws.cell(rr, 1, lab).font = f_bold; ws.cell(rr, 2, nm).font = f_norm
        c = ws.cell(rr, 3, ntr); c.font = f_norm; c.number_format = CNT
        for j, cfg in enumerate(CONFIGS):
            col = C0 + j
            if callable(kind):
                v = kind(ex, cfg)
                cc = ws.cell(rr, col, v); cc.font = f_norm
            else:
                cc = ws.cell(rr, col, '=%s!%s%d' % (q(sheet), L(col), kind(pos) if callable(kind) else pos_get(pos, kind))); cc.font = f_green
            cc.number_format = fmt
        if scale:
            rng = '%s%d:%s%d' % (L(C0), rr, L(CL), rr)
            if scale == 'high':
                ws.conditional_formatting.add(rng, ColorScaleRule(start_type='min', start_color='F8696B', mid_type='percentile', mid_value=50, mid_color='FFEB84', end_type='max', end_color='63BE7B'))
            else:
                ws.conditional_formatting.add(rng, ColorScaleRule(start_type='min', start_color='63BE7B', mid_type='percentile', mid_value=50, mid_color='FFEB84', end_type='max', end_color='F8696B'))
    return r0 + len(rows) + 1, r0


def pos_get(pos, path):
    a, b = path.split('.') if '.' in path else (path, None)
    return pos[a][b] if b else pos[a]


def best_cols(ws, r_name_row, r0, n, ncol_best=2, labels=('Most', 'Least')):
    pass


# --------------------------------------------------------------------------------------------------------------------- read me helpers
def readme(ws, rows):
    ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 150
    r = 1
    for lab, txt, *sty in rows:
        if lab == '#title':
            c = ws.cell(r, 1, txt); c.font = Font(name=F, size=14, bold=True); r += 1; continue
        if lab == '#h':
            r += 1; c = ws.cell(r, 1, txt); c.font = f_block; r += 1; continue
        a = ws.cell(r, 1, lab); a.font = f_bold; a.alignment = left
        b = ws.cell(r, 2, txt); b.font = f_blue if (sty and sty[0] == 'blue') else f_norm; b.alignment = left
        lines = max(1, sum(len(x) // 150 + 1 for x in str(txt).split('\n')))
        ws.row_dimensions[r].height = 13 * lines + 2
        r += 1
    return r


def levels_table(ws, r):
    """the 5 levels' numbers (the strategies' built-in constants) in blue"""
    ws.cell(r, 1, 'Level').font = f_hdr; ws.cell(r, 1).fill = fill_hdr
    hd = ('Keeps (lock) of the best profit', 'Share of the cushion added to the base', 'Base at most (x $50)', 'Most extra risk per trade (share of the cushion)')
    for j, t in enumerate(hd):
        c = ws.cell(r, 2 + j, t); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
    ws.row_dimensions[r].height = 27
    for i, lv in enumerate(('Low', 'Medium', 'High', 'Extra high', 'Max')):
        rr = r + 1 + i; ws.cell(rr, 1, lv).font = f_bold
        for j, (v, fm) in enumerate(zip(LADP[lv], ('0%', '0%', '0"x"', '0%'))):
            c = ws.cell(rr, 2 + j, v); c.font = f_blue; c.number_format = fm; c.alignment = Alignment(horizontal='center')
    for col in (3, 4, 5): ws.column_dimensions[L(col)].width = 22
    return r + 7


# --------------------------------------------------------------------------------------------------------------------- the grid
def build_grid():
    D = pickle.load(open(S + '/mcej/grid_money.pkl', 'rb')); M = D['months']
    CH = D['charts']
    wb = Workbook(); rd = wb.active; rd.title = 'Read me'
    chart_info = {}
    for ctf in ('M5', 'M15'):
        C = CH[ctf]; ks = C['ks']
        fr_diff = sum(1 for k in ks for cfg in CONFIGS if cfg[1] != 'Off' for m in M
                      if abs(C['strategies'][k]['res'][cfg]['fresh'][m]['net'] - C['strategies'][k]['res'][(cfg[0], 'Off')]['fresh'][m]['net']) > 1e-6)
        chart_info[ctf] = dict(ks=ks, fr_diff=fr_diff)
    # summary first (placed after the read me), then the chart sheets
    sm = wb.create_sheet('Summary'); sm.sheet_properties.tabColor = '1F3864'
    poss = {}; sheets = {}
    for ctf in ('M5', 'M15'):
        C = CH[ctf]; ks = C['ks']
        lab = 'S' + ', S'.join(str(k) for k in ks)
        data = {cfg: dict(cont=C['combined'][cfg]['cont'], fresh=C['combined'][cfg]['fresh']) for cfg in CONFIGS}
        title = 'Fractal Breakout Grid on a gold %s chart: all %d strategies on (%s), each with its own $10,000 account - IST calendar months, Jan 2021 - 2 Oct 2026' % (
            ctf, len(ks), lab)
        settings = ('Settings = the grid defaults: $50 base risk, $10,000 per strategy, 1:100 leverage, hard cap $500 Clamp, costs 0.23 per trade, ladder target '
                    '$1,000, Crooks E / I lot 0.01, F x3, G x10, H 1%%, J x20. Numbers are the sum of the %d strategies.' % len(ks))
        fn = ('The ladder needs $1,000 profit inside one month to switch on; no strategy got there in any month (%d of %d strategy-rule-months differ from Off), '
              'so here the Low - Max columns are the same as Off.' % (chart_info[ctf]['fr_diff'], len(ks) * 25 * len(M)))
        ws, pos = monthly_sheet(wb, '%s chart' % ctf, title, settings, 10000.0 * len(ks), M, C['counts'], data, fresh_note=fn)
        poss[ctf] = pos; sheets[ctf] = ws
        build_grid_bystrat(wb, ctf, C, M, pos)
    # summary sheet
    sm['A1'] = 'Summary: Fractal Breakout Grid, gold, every Crooks E - J rule x profit ladder level - first the M5 chart, then the M15 chart'; sm['A1'].font = f_title
    sm['A2'] = ('Green numbers are links to the chart sheets (formulas). One account per strategy from January 2021 to 2 Oct 2026; the chart rows add the '
                'strategies up. Colour scale per row: green = best of the row, red = worst.'); sm['A2'].font = f_note
    rows = []
    for ctf in ('M5', 'M15'):
        ks = CH[ctf]['ks']; ntr = sum(CH[ctf]['strategies'][k]['n'] for k in ks)
        rows.append(('%s chart' % ctf, 'S' + ', S'.join(str(k) for k in ks), ntr, '%s chart' % ctf, poss[ctf], ctf))
    sm.column_dimensions['A'].width = 24; sm.column_dimensions['B'].width = 30; sm.column_dimensions['C'].width = 8; sm.column_dimensions['D'].width = 2
    for col in range(C0, CL + 1): sm.column_dimensions[L(col)].width = 11.5
    r = 4
    r, _ = summary_block(sm, r, 'Total profit 2021 - 2026 ($), one account per strategy', rows, 'm.SUM', USD, scale='high')
    r, _ = summary_block(sm, r, 'Months in profit (of 70)', rows, 'm.PROF', CNT, scale='high')
    r, _ = summary_block(sm, r, 'Months in loss (of 70)', rows, 'm.LOSS', CNT, scale='low')
    r, _ = summary_block(sm, r, 'Worst month ($)', rows, 'm.MIN', USD, scale='high')
    r, _ = summary_block(sm, r, 'Best month ($)', rows, 'm.MAX', USD, scale='high')
    r, _ = summary_block(sm, r, 'Average month ($)', rows, 'm.AVERAGE', USD, scale='high')
    r, _ = summary_block(sm, r, 'Years in loss (of 6)', rows, 'YLOSS', CNT, scale='low')
    r, _ = summary_block(sm, r, 'Balance on 2 Oct 2026 ($), all strategies together', rows, 'BAL_END', USD, scale='high')
    r, _ = summary_block(sm, r, 'Deepest drop inside one month ($)', rows, 'DROP_MAX', USD, scale='low')
    r, _ = summary_block(sm, r, 'Deepest fall from a peak, whole period ($): the summed balance of all strategies (closed trades)', rows,
                         lambda ctf, cfg: round(CH[ctf]['combined'][cfg]['whole']['maxDD'], 2), USD, scale='low')
    r, _ = summary_block(sm, r, 'Deepest fall from a peak, whole period (% of that peak, summed balance)', rows,
                         lambda ctf, cfg: round(CH[ctf]['combined'][cfg]['whole']['maxDDpct'], 4), '0.0%', scale='low')
    r, _ = summary_block(sm, r, 'Strategies whose profit ladder switched on (reached $1,000 profit)', rows,
                         lambda ctf, cfg: sum(1 for k in CH[ctf]['ks'] if CH[ctf]['strategies'][k]['res'][cfg]['whole']['ladFirst']), CNT)
    r, _ = summary_block(sm, r, 'Trades at the 0.01-lot start guard (profit back at $0 or below after the target)', rows,
                         lambda ctf, cfg: CH[ctf]['combined'][cfg]['whole']['guardTrades'], CNT)
    r, _ = summary_block(sm, r, 'Each month on its own: total of the 70 months ($)', rows, 'f.SUM', USD, scale='high')
    r, _ = summary_block(sm, r, 'Each month on its own: months in loss (of 70)', rows, 'f.LOSS', CNT, scale='low')
    sm.freeze_panes = 'E1'
    order = ['Read me', 'Summary', 'M5 chart', 'M5 by strategy', 'M15 chart', 'M15 by strategy']
    wb._sheets = [wb[n] for n in order]
    readme(rd, grid_readme(CH, M, chart_info))
    levels_table(rd, rd.max_row + 2)
    fn = OUT + '/Gold_Monthly_Crooks_EJ_Fractal_Grid.xlsx'; wb.save(fn); print('saved', fn)


def strat_label(p):
    return '%s R%d/L%d off %+.3f%% SL %.2f%% TP %.2f%% BE %.2f%% salv %.2f%%' % (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def build_grid_bystrat(wb, ctf, C, M, cpos):
    ws = wb.create_sheet('%s by strategy' % ctf); ws.sheet_properties.tabColor = '548235'
    ks = C['ks']
    ws['A1'] = 'Fractal Breakout Grid on a gold %s chart: each strategy on its own ($10,000 each, one account from January 2021)' % ctf; ws['A1'].font = f_title
    ws['A2'] = ('Values from the simulation (per strategy). The "All" row of the first table adds the strategies up with a formula and must equal the "%s chart" '
                'sheet total (row "Check"). Strategy settings: fractal TF, Right / Left candles, buy-stop offset, SL, TP, break-even and salvage triggers (%% of the fill).' % ctf)
    ws['A2'].font = f_note
    ws.column_dimensions['A'].width = 10; ws.column_dimensions['B'].width = 52; ws.column_dimensions['C'].width = 8; ws.column_dimensions['D'].width = 2
    for col in range(C0, CL + 1): ws.column_dimensions[L(col)].width = 11.5
    rows = [('S%d' % k, strat_label(C['strategies'][k]['prm']), C['strategies'][k]['n'], None, None, k) for k in ks]
    get = lambda f: (lambda k, cfg: f(C['strategies'][k]['res'][cfg]))
    r = 4
    r, r0 = summary_block(ws, r, 'Total profit 2021 - 2026 ($)', rows, get(lambda w: float(w['whole']['net'])), USD)
    # All + check rows
    rr = r - 1; ws.cell(rr, 1, 'All').font = f_bold; ws.cell(rr, 2, 'sum of the strategies (formula)').font = f_note
    c = ws.cell(rr, 3, '=SUM(C%d:C%d)' % (r0, r0 + len(ks) - 1)); c.font = f_bold; c.number_format = CNT
    for col in range(C0, CL + 1):
        c = ws.cell(rr, col, '=SUM(%s%d:%s%d)' % (L(col), r0, L(col), r0 + len(ks) - 1)); c.font = f_bold; c.number_format = USD; c.fill = fill_stat
    rr += 1; ws.cell(rr, 1, 'Check').font = f_bold; ws.cell(rr, 2, 'All minus the "%s chart" sheet total (0 = the same)' % ctf).font = f_note
    for col in range(C0, CL + 1):
        c = ws.cell(rr, col, "=ROUND(%s%d-%s!%s%d,2)" % (L(col), rr - 1, q('%s chart' % ctf), L(col), cpos['m']['SUM'])); c.font = f_norm; c.number_format = USD
    ws._grid_check_row = rr
    r = rr + 2
    r, _ = summary_block(ws, r, 'Months in loss (of 70), the strategy\'s own account', rows, get(lambda w: sum(1 for m in M if w['cont'][m]['net'] < 0)), CNT)
    r, _ = summary_block(ws, r, 'Worst month ($)', rows, get(lambda w: float(min(w['cont'][m]['net'] for m in M))), USD)
    r, _ = summary_block(ws, r, 'Biggest risk on one trade ($)', rows, get(lambda w: round(w['maxRisk'], 2)), USD)
    r, _ = summary_block(ws, r, 'Deepest fall from a peak, whole period (% of the strategy\'s peak balance)', rows, get(lambda w: round(w['whole']['maxDDpct'], 4)), '0.0%')
    r, _ = summary_block(ws, r, 'Profit ladder switched on in (first month with the ladder on; - = never reached $1,000)', rows,
                         get(lambda w: mtxt(w['whole']['ladFirst']) if w['whole']['ladFirst'] else '-'), '@')
    ws.freeze_panes = 'E1'
    return ws


def grid_readme(CH, M, info):
    a = CH['M5']['combined']; b = CH['M15']['combined']
    def tot(Cc, cfg): return Cc[cfg]['whole']['net']
    def loss(Cc, cfg): return sum(1 for m in M if Cc[cfg]['cont'][m]['net'] < 0)
    def worst(Cc, cfg): return min(Cc[cfg]['cont'][m]['net'] for m in M)
    F_ = ('Crooks F', 'Off'), ('Crooks F', 'Medium'), ('Crooks F', 'Max')
    s5 = CH['M5']['strategies']
    never = [k for k in CH['M5']['ks'] if not s5[k]['res'][('Crooks F', 'Medium')]['whole']['ladFirst']]
    best5 = max(CONFIGS, key=lambda c: tot(a, c)); best15 = max(CONFIGS, key=lambda c: tot(b, c))
    calm5 = min(CONFIGS, key=lambda c: (loss(a, c), -tot(a, c)))
    gain = sorted(CH['M5']['ks'], key=lambda k: -(s5[k]['res'][F_[2]]['whole']['net'] - s5[k]['res'][F_[0]]['whole']['net']))
    ddall = [CH[t]['combined'][c]['whole']['maxDDpct'] for t in ('M5', 'M15') for c in CONFIGS]; ddmin, ddmax = min(ddall), max(ddall)
    ddstrat = max(CH[t]['strategies'][k]['res'][c]['whole']['maxDDpct'] for t in ('M5', 'M15') for k in CH[t]['ks'] for c in CONFIGS)
    rows = [
        ('#title', 'Gold month by month: Fractal Breakout Grid with the Crooks E - J recovery rules and the 5 profit-ladder levels'),
        ('What', 'Every Crooks E - J rule with every profit-ladder level (Off, Low, Medium, High, Extra high, Max; Crooks E has no ladder), month by month '
                 'from January 2021 to 2 October 2026 (the end of the gold data), first with all strategies on a gold M5 chart, then on an M15 chart.'),
        ('Sheets', 'Summary: the key numbers of every rule / level for both charts (formulas linked to the chart sheets).\n'
                   'M5 chart / M15 chart: block 1 profit or loss of each month, block 2 each year, block 3 the balance at each month end, block 4 the deepest '
                   'drop inside each month, block 5 each month on its own.\n'
                   'M5 by strategy / M15 by strategy: the same rules and levels for each strategy alone (totals, losing months, worst month, biggest risk, deepest fall, '
                   'when the ladder switched on).'),
        ('Which trades', 'The grid model on the chart\'s candles (what the indicator and the strategy compute; engine = Pine twin, checked trade for trade here: '
                         '21 strategy / chart runs identical). M5 chart: strategies 1 - 11 (12 is an M1 strategy and is switched off on M5). M15 chart: 1 - 9 '
                         'and 11 (10 and 12 are below M15 and switched off). The TradingView strategy tester fills some trades at the next open instead '
                         '(about 5 - 10 % of trades, see the README audit), so its numbers differ a little.'),
        ('Months', 'IST calendar months (the grid\'s default time zone), from the 1st 00:00 to the last day 23:59. Blocks 1 - 4: a trade counts in the month it '
                   'closed (when the money is booked). Block 5: a trade belongs to the month it started in.'),
        ('Two ways to read a month', 'ONE ACCOUNT (blocks 1 - 4, and the Summary): one account per strategy runs from January 2021, as the strategy or EA does when it '
                                     'is left running. The recovery state and the profit ladder carry over from month to month. This is the only way the ladder '
                                     'levels can matter: the ladder switches on after the account\'s best closed profit reaches $1,000.\n'
                                     'EACH MONTH ON ITS OWN (block 5): every month starts again with $10,000 per strategy and a fresh recovery / ladder state, like the '
                                     'earlier monthly workbooks. No strategy reached $1,000 inside one month, so there the ladder never switched on and the Low - Max '
                                     'columns are the same as Off (%d and %d of %d / %d strategy-rule-months differ).' % (
                                         info['M5']['fr_diff'], info['M15']['fr_diff'], len(info['M5']['ks']) * 25 * len(M), len(info['M15']['ks']) * 25 * len(M))),
        ('Settings (the grid defaults)', 'Fixed $ risk, base $50 a trade; $10,000 start balance per strategy; 1:100 leverage limit; hard cap $500 per trade, Clamp; '
                                         'costs 0.23 (price units) per trade; Crooks E / I lot 0.01 (= 1 oz of gold); Crooks F x3; Crooks G x10; Crooks H 1 %; Crooks J '
                                         'x20; profit ladder target $1,000. Sizes are not rounded to the 0.01-lot step.', 'blue'),
        ('The rules', 'Crooks E: like Crooks C (after a loss, wait for a win, then the next trade wins the whole loss back), but while a loss waits for a win every trade is '
                      '0.01 lot.\nCrooks F: a recovery trade risks at most 3 x the base ($150).\nCrooks G: the loss to win back is at most 10 x the base ($500); the '
                      'rest is accepted.\nCrooks H: a recovery trade risks at most 1 % of the balance (at least the base).\nCrooks I: Crooks E + Crooks F.\n'
                      'Crooks J: a recovery trade shrinks as the account falls from its peak (x (1 - fall / (20 x base))), at least the base.'),
        ('The profit ladder', 'For Crooks F - J only. Until the best closed profit reaches $1,000 the rule trades as with Off. From then on: lock = keep-share x the '
                              'best profit; cushion = profit - lock; base = $50 + share x cushion (at most the level\'s multiple); a trade never risks more than the '
                              'plain rule + the extra share of the cushion. Start guard: whenever the profit is back at $0 or below, every trade is 0.01 lot until '
                              'it is above $0 again. The table at the bottom of this sheet has each level\'s numbers.'),
        ('Shading', 'Green cell = the ladder was on in that month; orange = at least one 0.01-lot start-guard trade in that month (none in this workbook).'),
        ('#h', 'Findings'),
        ('1. Every level adds profit', 'On both charts the ladder raised the profit at every level and the start guard never fired. M5 chart, Crooks F: Off %s, Medium '
                                       '(the default) %s, Max %s; worst month %s / %s / %s; months in loss %d / %d / %d of 70.' % (
                                           usd(tot(a, F_[0])), usd(tot(a, F_[1])), usd(tot(a, F_[2])), usd(worst(a, F_[0])), usd(worst(a, F_[1])), usd(worst(a, F_[2])),
                                           loss(a, F_[0]), loss(a, F_[1]), loss(a, F_[2]))),
        ('2. M15 chart', 'Crooks F: Off %s, Medium %s, Max %s; worst month %s / %s / %s; months in loss %d / %d / %d of 70. Fewer trades than on M5 (strategy 10 is '
                         'off) and bigger worst months at the high levels.' % (
                             usd(tot(b, F_[0])), usd(tot(b, F_[1])), usd(tot(b, F_[2])), usd(worst(b, F_[0])), usd(worst(b, F_[1])), usd(worst(b, F_[2])),
                             loss(b, F_[0]), loss(b, F_[1]), loss(b, F_[2]))),
        ('3. Best and calmest', 'Most profit: M5 %s %s, M15 %s %s. Fewest months in loss on M5: %s (%d of 70, %s). Crooks I is the most careful (smallest worst '
                                'months) but makes the least: M5 Off %s, Max %s. Crooks F, G, H and J end close to each other; Crooks E (no ladder) makes about half '
                                'of Crooks F Off.' % (
                                    cfgname(best5), usd(tot(a, best5)), cfgname(best15), usd(tot(b, best15)), cfgname(calm5), loss(a, calm5), usd(tot(a, calm5)),
                                    usd(tot(a, ('Crooks I', 'Off'))), usd(tot(a, ('Crooks I', 'Max'))))),
        ('4. Where the extra profit comes from', 'Strategies %s never reach $1,000 profit, so the ladder never switches on for them. Strategy %d gains the most '
                                                 '(M5, Crooks F: Off %s, Max %s), then %s (sheet "M5 by strategy").' % (
                                                     ', '.join(str(k) for k in never), gain[0], usd(s5[gain[0]]['res'][F_[0]]['whole']['net']),
                                                     usd(s5[gain[0]]['res'][F_[2]]['whole']['net']), ', '.join(str(k) for k in gain[1:4]))),
        ('5. Falls are small in %', 'The summed balance starts at $110,000 (M5) / $100,000 (M15), so its deepest fall is only %.1f - %.1f %%. Per strategy the falls '
                                     'are bigger: up to %.0f %% (sheet "by strategy").' % (100 * ddmin, 100 * ddmax, 100 * ddstrat)),
        ('6. Each month on its own', 'Starting each month from scratch, no strategy reaches the $1,000 target inside a month, so the levels make no difference there '
                                     '(block 5). The ladder pays off only when the account is left running across months.'),
        ('#h', 'How it was computed and checked'),
        ('Money', 'fractal/recovery_tol.py, the reference proven equal to the grid strategy\'s money code (earlier parity: 2,600 random settings, ~880k trades). '
                  'Here also checked against the Pine twin\'s own money for the default setting (Crooks F + Medium): every trade of all 21 strategy / chart runs, '
                  'largest relative difference 1.5e-7 (float rounding).'),
        ('Checks', 'Engine trades = Pine twin trades on both charts (21 runs identical). The default setting on the M5 chart totals %s, the number reported '
                   'for v2 (+$42,653).' % usd(tot(a, F_[1])) + ' The by-strategy sheets add up to the chart sheets (row "Check" = 0). An independent re-implementation of the money rules from their '
                   'definitions recomputed sample months (see the final report).'),
        ('Caveats', 'Past results, one price history. The results depend on the start date (when the $1,000 target is reached). No lot rounding, no swaps; '
                    'spread / commission as the 0.23 cost.'),
        ('#h', 'Profit-ladder levels (the strategy\'s built-in numbers)'),
    ]
    return rows


# --------------------------------------------------------------------------------------------------------------------- the Auction Retest strategies
def build_ars():
    D = pickle.load(open(S + '/mcej/ars_money.pkl', 'rb')); M = D['months']; ST = D['strategies']
    T = pickle.load(open(S + '/mcej/ars_targets.pkl', 'rb'))
    wb = Workbook(); rd = wb.active; rd.title = 'Read me'
    order = ['Read me']; poss = {}
    fr_diff_all = 0; fr_tot_all = 0
    for tf in ('M5', 'M15'):
        keys = [k for k in ST if ST[k]['tf'] == tf]
        sm = wb.create_sheet('Summary %s' % tf); sm.sheet_properties.tabColor = '1F3864'; order.append(sm.title)
        for key in keys:
            st = ST[key]; res = st['res']
            data = {cfg: dict(cont=res[cfg]['cont'], fresh=res[cfg]['fresh']) for cfg in CONFIGS}
            fr_diff = sum(1 for r_ in RULES[1:] for m in M if any(abs(res[(r_, l)]['fresh'][m]['net'] - res[(r_, 'Off')]['fresh'][m]['net']) > 1e-6 for l in LEVELS[1:]))
            fr_mon = len({m for r_ in RULES[1:] for m in M if any(abs(res[(r_, l)]['fresh'][m]['net'] - res[(r_, 'Off')]['fresh'][m]['net']) > 1e-6 for l in LEVELS[1:])})
            fr_diff_all += fr_diff; fr_tot_all += 5 * len(M)
            title = 'Auction Retest %s "%s" - gold, IST calendar months, Jan 2021 - 2 Oct 2026 - every Crooks E - J rule x profit ladder level' % (key, st['name'])
            settings = ('Settings = the strategy defaults: $50 base risk, $10,000 start, 1:100 leverage, no hard cap, gold spread as the cost, ladder target $1,000, '
                        'Crooks E / I lot 0.01, F x3, G x10, H 1%%, J x20; exit at %.1fR; %d trades. The strategy as designed (its own filters).' % (st['exitR'], st['n']))
            fn = ('The ladder needs $1,000 profit inside one month to switch on: that happened in %d of the %d months of this strategy (%d of %d rule-months), so '
                  'here the Low - Max columns are %s Off.' % (fr_mon, len(M), fr_diff, 5 * len(M), 'the same as' if fr_diff == 0 else 'almost the same as'))
            ws, pos = monthly_sheet(wb, key, title, settings, 10000.0, M, st['counts'], data, fresh_note=fn)
            poss[key] = pos; order.append(key)
        ars_summary(sm, tf, keys, ST, poss, M)
    tg = wb.create_sheet('Ladder target test'); tg.sheet_properties.tabColor = 'C65911'; order.append(tg.title)
    ars_targets_sheet(tg, T, ST)
    wb._sheets = [wb[n] for n in order]
    readme(rd, ars_readme(ST, M, T, fr_diff_all, fr_tot_all))
    levels_table(rd, rd.max_row + 2)
    fn = OUT + '/Gold_Monthly_Crooks_EJ_Auction_Retest.xlsx'; wb.save(fn); print('saved', fn)


def ars_summary(sm, tf, keys, ST, poss, M):
    sm['A1'] = 'Summary: Auction Retest %s strategies, gold Jan 2021 - 2 Oct 2026, every Crooks E - J rule x profit ladder level' % tf; sm['A1'].font = f_title
    sm['A2'] = ('Green numbers are links to the strategy sheets (formulas); black ones are from the simulation. One account per strategy from January 2021 '
                '(the strategy left running). Colour scale per row: green = best of the row, red = worst. Columns AK / AL: the best setting of the row (formulas).')
    sm['A2'].font = f_note
    sm.column_dimensions['A'].width = 10; sm.column_dimensions['B'].width = 34; sm.column_dimensions['C'].width = 8; sm.column_dimensions['D'].width = 2
    for col in range(C0, CL + 1): sm.column_dimensions[L(col)].width = 11.5
    sm.column_dimensions[L(CL + 2)].width = 26; sm.column_dimensions[L(CL + 3)].width = 12
    rows = [(k, ST[k]['name'], ST[k]['n'], k, poss[k], k) for k in keys]
    get = lambda f: (lambda k, cfg: f(ST[k]['res'][cfg]))
    r = 4
    blocks = [
        ('Total profit 2021 - 2026 ($), one account', 'm.SUM', USD, 'high', 'max'),
        ('Months in profit (of 70)', 'm.PROF', CNT, 'high', 'max'),
        ('Months in loss (of 70)', 'm.LOSS', CNT, 'low', 'min'),
        ('Worst month ($)', 'm.MIN', USD, 'high', 'max'),
        ('Best month ($)', 'm.MAX', USD, 'high', None),
        ('Average month ($)', 'm.AVERAGE', USD, 'high', None),
        ('Years in loss (of 6)', 'YLOSS', CNT, 'low', None),
        ('Balance on 2 Oct 2026 ($)', 'BAL_END', USD, 'high', None),
        ('Deepest drop inside one month ($)', 'DROP_MAX', USD, 'low', 'min'),
        ('Deepest fall from a peak, whole period ($), closed trades', get(lambda w: round(w['whole']['maxDD'], 2)), USD, 'low', 'min'),
        ('Deepest fall from a peak, whole period (% of that peak)', get(lambda w: round(w['whole']['maxDDpct'], 4)), '0.0%', 'low', None),
        ('Profit ladder switched on in (first month with the ladder on; - = never)', get(lambda w: mtxt(w['whole']['ladFirst']) if w['whole']['ladFirst'] else '-'), '@', None, None),
        ('Months with 0.01-lot start-guard trades (profit back at $0 or below after the target)', get(lambda w: w['whole']['guardMonths']), CNT, 'low', None),
        ('Each month on its own: total of the 70 months ($)', 'f.SUM', USD, 'high', None),
        ('Each month on its own: months in loss (of 70)', 'f.LOSS', CNT, 'low', None),
    ]
    for title, kind, fmt, scale, best in blocks:
        r_end, r0 = summary_block(sm, r, title, rows, kind, fmt, scale=scale)
        if best:
            hdr_names = r0 - 1                                      # the full-name row of this block's header
            c = sm.cell(r0 - 3, CL + 2, 'Best setting (%s of the row)' % ('highest' if best == 'max' else 'lowest')); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
            c = sm.cell(r0 - 3, CL + 3, 'Value'); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
            for i in range(len(rows)):
                rr = r0 + i; rng = '$%s%d:$%s%d' % (L(C0), rr, L(CL), rr); nrng = '$%s$%d:$%s$%d' % (L(C0), hdr_names, L(CL), hdr_names)
                fnm = 'MAX' if best == 'max' else 'MIN'
                c = sm.cell(rr, CL + 2, '=INDEX(%s,MATCH(%s(%s),%s,0))' % (nrng, fnm, rng, rng)); c.font = f_norm
                c = sm.cell(rr, CL + 3, '=%s(%s)' % (fnm, rng)); c.font = f_norm; c.number_format = fmt
        r = r_end
    sm.freeze_panes = 'E1'


def ars_targets_sheet(ws, T, ST):
    ws['A1'] = 'Profit ladder with other profit targets: total profit 2021 - 2026 ($), one account per strategy (Auction Retest M5 and M15 strategies)'; ws['A1'].font = f_title
    ws['A2'] = ('The workbook uses the default target ($1,000). Here the same runs with $2,000, $3,000 and $5,000. Orange = the run had 0.01-lot start-guard '
                'trades (the profit fell back to $0 or below after the target). Values from the simulation.'); ws['A2'].font = f_note
    TG = T['targets']; R = T['res']; LV = LEVELS[1:]
    ws.column_dimensions['A'].width = 10; ws.column_dimensions['B'].width = 30; ws.column_dimensions['C'].width = 10
    r = 4
    c = ws.cell(r, 1, 'Strategy'); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
    c = ws.cell(r, 2, 'Name'); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
    c = ws.cell(r, 3, 'Rule'); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
    c = ws.cell(r, 4, 'Ladder Off'); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
    for col in (1, 2, 3, 4): ws.cell(r + 1, col).fill = fill_hdr; ws.merge_cells(start_row=r, start_column=col, end_row=r + 1, end_column=col)
    ws.column_dimensions['D'].width = 11.5
    for t_i, Tv in enumerate(TG):
        c0 = 5 + t_i * len(LV); fl = fill_hdr if t_i % 2 == 0 else fill_hdr2
        c = ws.cell(r, c0, 'Target $%s%s' % (format(int(Tv), ','), ' (default)' if Tv == 1000 else '')); c.font = f_hdr; c.fill = fl; c.alignment = center
        ws.merge_cells(start_row=r, start_column=c0, end_row=r, end_column=c0 + len(LV) - 1)
        for j, lv in enumerate(LV):
            cc = ws.cell(r + 1, c0 + j, lv); cc.font = f_hdr; cc.fill = fl; cc.alignment = center; ws.column_dimensions[L(c0 + j)].width = 11.5
    rr = r + 2; first = rr
    for key in ST:
        for rule in RULES[1:]:
            ws.cell(rr, 1, key).font = f_bold; ws.cell(rr, 2, ST[key]['name']).font = f_norm; ws.cell(rr, 3, rule).font = f_norm
            c = ws.cell(rr, 4, float(R[(key, rule, 'Off', None)]['net'])); c.font = f_norm; c.number_format = USD
            for t_i, Tv in enumerate(TG):
                for j, lv in enumerate(LV):
                    v = R[(key, rule, lv, Tv)]
                    c = ws.cell(rr, 5 + t_i * len(LV) + j, float(v['net'])); c.font = f_norm; c.number_format = USD
                    if v['guard']: c.fill = fill_guard
            rr += 1
    last = rr - 1
    ws.cell(rr, 1, 'Total').font = f_bold; ws.cell(rr, 3, 'all rows').font = f_note
    for col in range(4, 5 + len(TG) * len(LV)):
        c = ws.cell(rr, col, '=SUM(%s%d:%s%d)' % (L(col), first, L(col), last)); c.font = f_bold; c.number_format = USD; c.fill = fill_stat
    rr += 1; ws.cell(rr, 1, 'Runs with guard trades').font = f_bold
    for t_i, Tv in enumerate(TG):
        for j, lv in enumerate(LV):
            n = sum(1 for key in ST for rule in RULES[1:] if R[(key, rule, lv, Tv)]['guard'])
            c = ws.cell(rr, 5 + t_i * len(LV) + j, n); c.font = f_bold; c.number_format = CNT; c.fill = fill_stat
    ws.freeze_panes = 'E6'


def ars_readme(ST, M, T, fr_diff, fr_tot):
    def w(k, cfg): return ST[k]['res'][cfg]['whole']
    def loss(k, cfg): return sum(1 for m in M if ST[k]['res'][cfg]['cont'][m]['net'] < 0)
    def worst(k, cfg): return min(ST[k]['res'][cfg]['cont'][m]['net'] for m in M)
    F0, FM, FX = ('Crooks F', 'Off'), ('Crooks F', 'Medium'), ('Crooks F', 'Max')
    trapped = [k for k in ST if all(ST[k]['res'][('Crooks F', l)]['whole']['guardMonths'] >= 24 for l in LEVELS[1:])]
    ntrap = {k: sum(1 for r_ in RULES[1:] for l in LEVELS[1:] if ST[k]['res'][(r_, l)]['whole']['guardMonths'] >= 24) for k in trapped}
    TG = T['targets']; R = T['res']
    gcount = {Tv: sum(1 for k in ST for r_ in RULES[1:] for l in LEVELS[1:] if R[(k, r_, l, Tv)]['guard']) for Tv in TG}
    ntot = len(ST) * 5 * 5
    best = {k: max(CONFIGS, key=lambda c: w(k, c)['net']) for k in ST}
    calm = {k: min(CONFIGS, key=lambda c: (loss(k, c), -w(k, c)['net'])) for k in ST}
    rows = [
        ('#title', 'Gold month by month: Auction Retest strategies with the Crooks E - J recovery rules and the 5 profit-ladder levels'),
        ('What', 'Every Crooks E - J rule with every profit-ladder level (Off, Low, Medium, High, Extra high, Max; Crooks E has no ladder), month by month '
                 'from January 2021 to 2 October 2026 (the end of the gold data): first the M5 strategies, then the M15 strategies.'),
        ('Sheets', 'Summary M5 / Summary M15: the key numbers of every strategy x rule x level, with the best setting of each row.\n'
                   'One sheet per strategy (M5-S1 ... M15-S9): block 1 profit or loss of each month, block 2 each year, block 3 the balance at each month end, '
                   'block 4 the deepest drop inside each month, block 5 each month on its own.\n'
                   'Ladder target test: the ladder with a $2,000 / $3,000 / $5,000 target instead of $1,000.'),
        ('Which strategies', 'The catalogue strategies on M5 (S1 Most profit, S2 Shortest losing streak, S3 Most trades a day, S4 Simplest) and M15 (S1 Most profit, '
                             'S3 Shortest losing streak - indicator only, S6 Most trades a day, S7 Every year positive, S8 Simplest, S9 Asia session only), as designed '
                             '(their own filters on): the gold strategies that are profitable at a fixed $50 without a partial close, the same set as the earlier '
                             'monthly workbooks. Trades from an engine re-run (checked: identical to the stored trades of all 10 strategies).'),
        ('Months', 'IST calendar months (the strategy\'s time zone), from the 1st 00:00 to the last day 23:59. Blocks 1 - 4: a trade counts in the month it closed. '
                   'Block 5: a trade belongs to the month it started in.'),
        ('Two ways to read a month', 'ONE ACCOUNT (blocks 1 - 4, and the summaries): the strategy runs from January 2021 without a restart, as the EA does when it is '
                                     'left running. The recovery state and the profit ladder carry over from month to month. This is the only way the ladder levels '
                                     'can matter: the ladder switches on after the account\'s best closed profit reaches $1,000.\n'
                                     'EACH MONTH ON ITS OWN (block 5): every month starts again with $10,000 and a fresh recovery / ladder state, like the earlier '
                                     'monthly workbooks. The $1,000 target was reached inside a month in only %d of %d strategy-rule-months, so there the Low - Max '
                                     'columns are (almost) the same as Off.' % (fr_diff, fr_tot)),
        ('Settings (the strategy defaults)', 'Fixed $ risk, base $50 a trade; $10,000 start balance; 1:100 leverage limit (entry price); no hard cap (the default); '
                                             'cost = the gold spread of each trade; Crooks E / I lot 0.01 (= 1 oz of gold); Crooks F x3; Crooks G x10; Crooks H 1 %; '
                                             'Crooks J x20; profit ladder target $1,000. Sizes are not rounded to the 0.01-lot step.', 'blue'),
        ('The rules', 'Crooks E: like Crooks C (after a loss, wait for a win, then the next trade wins the whole loss back), but while a loss waits for a win every trade is '
                      '0.01 lot.\nCrooks F: a recovery trade risks at most 3 x the base ($150).\nCrooks G: the loss to win back is at most 10 x the base ($500); the '
                      'rest is accepted.\nCrooks H: a recovery trade risks at most 1 % of the balance (at least the base).\nCrooks I: Crooks E + Crooks F.\n'
                      'Crooks J: a recovery trade shrinks as the account falls from its peak (x (1 - fall / (20 x base))), at least the base.'),
        ('The profit ladder', 'For Crooks F - J only. Until the best closed profit reaches $1,000 the rule trades as with Off. From then on: lock = keep-share x the '
                              'best profit; cushion = profit - lock; base = $50 + share x cushion (at most the level\'s multiple); a trade never risks more than the '
                              'plain rule + the extra share of the cushion. Start guard: whenever the profit is back at $0 or below, every trade is 0.01 lot until '
                              'it is above $0 again. The table at the bottom of this sheet has each level\'s numbers.'),
        ('Shading', 'Green cell = the ladder was on in that month; orange = at least one 0.01-lot start-guard trade in that month.'),
        ('#h', 'Findings'),
        ('1. The ladder can trap an account', 'On %s, Crooks F at every ladder level (even Low) spends 2+ years at the 0.01-lot start guard with the default '
                                              '$1,000 target (ladder settings of Crooks F - J with 2+ years of guard trades: %s, each of 25). These accounts reach +$1,000 early, fall back to $0, and from '
                                              'then on the start guard trades 0.01 lot (a few $ of risk), so the strategy\'s later profits are almost not earned (orange '
                                              'months on their sheets). Example M5-S2, Crooks F: Off %s, Low %s, Medium %s, Max %s; guard trades in %d of 70 months at Medium.' % (
                                                  ', '.join(trapped) if trapped else 'several strategies', ', '.join('%s %d' % (k, ntrap[k]) for k in trapped),
                                                  usd(w('M5-S2', F0)['net']),
                                                  usd(w('M5-S2', ('Crooks F', 'Low'))['net']), usd(w('M5-S2', FM)['net']), usd(w('M5-S2', FX)['net']),
                                                  w('M5-S2', FM)['guardMonths'])),
        ('2. ... and multiply another', 'On M15-S1 and M15-S7 the ladder multiplies the profit. M15-S7, Crooks F: Off %s, Medium %s, Max %s, but the worst month goes '
                                        'from %s to %s and the deepest fall from %.0f %% to %.0f %%. M15-S1: Off %s, Max %s (fall %.0f %% -> %.0f %%).' % (
                                            usd(w('M15-S7', F0)['net']), usd(w('M15-S7', FM)['net']), usd(w('M15-S7', FX)['net']), usd(worst('M15-S7', F0)),
                                            usd(worst('M15-S7', FX)), 100 * w('M15-S7', F0)['maxDDpct'], 100 * w('M15-S7', FX)['maxDDpct'],
                                            usd(w('M15-S1', F0)['net']), usd(w('M15-S1', FX)['net']), 100 * w('M15-S1', F0)['maxDDpct'], 100 * w('M15-S1', FX)['maxDDpct'])),
        ('3. A higher target helps', 'Sheet "Ladder target test": runs with start-guard trades fall from %d of %d at $1,000 to %d at $2,000, %d at $3,000 and %d at '
                                     '$5,000. Example M5-S2, Crooks F Medium: %s ($1,000), %s ($2,000), %s ($3,000), %s ($5,000). If you use the ladder on these '
                                     'strategies, a target of $2,000 - $3,000 is the safer choice; the results still depend a lot on the order of wins and losses.' % (
                                         gcount[1000.0], ntot, gcount[2000.0], gcount[3000.0], gcount[5000.0],
                                         usd(R[('M5-S2', 'Crooks F', 'Medium', 1000.0)]['net']), usd(R[('M5-S2', 'Crooks F', 'Medium', 2000.0)]['net']),
                                         usd(R[('M5-S2', 'Crooks F', 'Medium', 3000.0)]['net']), usd(R[('M5-S2', 'Crooks F', 'Medium', 5000.0)]['net']))),
        ('4. Crooks E', 'Crooks E (no ladder) has the fewest months in loss on %d of the %d strategies (e.g. M5-S3: %d, M15-S1: %d of 70) but can have the deepest '
                        'single months, because its recovery trade has no limit: worst month %s on M15-S7, deepest fall %.0f %% there.' % (
                            sum(1 for k in ST if calm[k] == ('Crooks E', 'Off')), len(ST), loss('M5-S3', ('Crooks E', 'Off')), loss('M15-S1', ('Crooks E', 'Off')),
                            usd(worst('M15-S7', ('Crooks E', 'Off'))), 100 * w('M15-S7', ('Crooks E', 'Off'))['maxDDpct'])),
        ('5. Best per strategy', 'Most profit, one account: ' + '; '.join('%s %s %s' % (k, cfgname(best[k]), usd(w(k, best[k])['net'])) for k in ST) + '.'),
        ('6. Fewest losing months', '; '.join('%s %s (%d, %s)' % (k, cfgname(calm[k]), loss(k, calm[k]), usd(w(k, calm[k])['net'])) for k in ST) + '.'),
        ('#h', 'How it was computed and checked'),
        ('Money', 'gold/recovery.py, the reference proven equal to the EA (parity suites: rec 7,728 runs / 11.4 M trades with the ladder, 0 differences) and to the '
                  'TradingView strategy\'s money code.'),
        ('Checks', 'Engine re-run = the stored catalogue trades (10 of 10 strategies identical: count, R, cost, time). An independent re-implementation of the money '
                   'rules from their definitions recomputed sample months (see the final report).'),
        ('Caveats', 'Past results, one price history. The results depend on the start date (when the $1,000 target is reached). No lot rounding (the EA rounds down to '
                    '0.01 lot); no commission or swaps; the spread as the cost.'),
        ('#h', 'Profit-ladder levels (the strategy\'s built-in numbers)'),
    ]
    return rows


if __name__ == '__main__':
    which = sys.argv[2] if len(sys.argv) > 2 else 'both'
    if which in ('both', 'grid'): build_grid()
    if which in ('both', 'ars'): build_ars()
