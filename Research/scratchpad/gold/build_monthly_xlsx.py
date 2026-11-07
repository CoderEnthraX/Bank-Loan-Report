import pickle, json, re, os, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import ColorScaleRule

S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
D = pickle.load(open(f'{S}/gold/monthly.pkl', 'rb'))
R = json.load(open(f'{S}/gold/monthly_readme.json'))
variants = D['variants']; strategies = D['strategies']; months = D['months']
VN = [v[0] for v in variants]; labels = [R['labels'][n] for n in VN]
NV = 17
F = 'Arial'
f_norm = Font(name=F, size=10); f_bold = Font(name=F, size=10, bold=True)
f_title = Font(name=F, size=14, bold=True)
f_hdr = Font(name=F, size=10, bold=True, color='FFFFFF')
fill_hdr = PatternFill('solid', fgColor='1F3864')
fill_red = PatternFill('solid', fgColor='9C0006')
f_white = Font(name=F, size=10, bold=True, color='FFFFFF')
USD = '$#,##0;[Red]-$#,##0'; RF = '0.00'; PCT = '0%'; CNT = '0'
center = Alignment(horizontal='center', vertical='center', wrap_text=True)
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def mtxt(m): y, mo = m.split('-'); return f'{MON[int(mo)-1]} {y}'
def q(name): return "'" + name.replace("'", "''") + "'"
BLOCKS = [('Net result of the month ($)', 'net', USD), ('Biggest fall in the month ($)', 'maxDD', USD),
          ('Biggest single loss ($)', 'maxLoss', USD), ('Trades taken', 'trades', CNT)]
FIRST, LAST = 6, 75
TOT, AVG, PROF, LOSS, BEST, WORST, BLOWN = 77, 78, 79, 80, 81, 82, 83
SUMROWS = [(TOT,'Total'),(AVG,'Average month'),(PROF,'Months in profit'),(LOSS,'Months in loss'),(BEST,'Best month'),(WORST,'Worst month')]

def sumformula(row, col, first, last):
    rng = f'{col}{first}:{col}{last}'
    return {TOT: f'=SUM({rng})', AVG: f'=AVERAGE({rng})', PROF: f'=COUNTIF({rng},">0")',
            LOSS: f'=COUNTIF({rng},"<0")', BEST: f'=MAX({rng})', WORST: f'=MIN({rng})'}[row]

def build(fk):
    info = R['files'][fk]; res = D['res'][fk]; news = fk == 'file2'
    wb = Workbook(); ws = wb.active; ws.title = 'Read me'
    # --- Read me
    ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 120
    r = 1
    def put(r, text, font=f_norm):
        c = ws.cell(r, 1, text); c.font = font; c.alignment = Alignment(wrap_text=True, vertical='top')
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        ws.row_dimensions[r].height = max(15, 14 * (len(text) // 140 + 1))
    put(r, info['title'], f_title); ws.row_dimensions[r].height = 24; r += 2
    for t in info['setup'] + [''] + R['common'] + [''] + R['columns']:
        if t: put(r, t)
        r += 1
    r += 1
    for j, h in enumerate(['Rule (column header)', 'What it does']):
        c = ws.cell(r, 1 + j, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
    r += 1
    for (n, desc), lab in zip(variants, labels):
        a = ws.cell(r, 1, lab); b = ws.cell(r, 2, desc)
        for c in (a, b): c.font = f_norm; c.alignment = Alignment(wrap_text=True, vertical='top')
        r += 1
    # --- Summary placeholder (filled after sheet names known)
    sm = wb.create_sheet('Summary')
    snames = [R['names'][s['key']] for s in strategies]
    base = 7 if news else 6          # blocks start after this many columns
    bstart = [base + 1 + i * NV for i in range(4)]   # 1-based col index of block i first column
    # --- Strategy sheets
    for s, nm in zip(strategies, snames):
        w = wb.create_sheet(nm); key = s['key']
        w['A1'] = f"{nm} - {info['title']}"; w['A1'].font = Font(name=F, size=12, bold=True)
        note = R['notes'].get(key, '')
        w['A2'] = f"Settings: {R['settings'][key]}, final target {s['exitR']:g} R. {note}".rstrip()
        w['A2'].font = f_norm
        fixed = ['Month','Trades','Wins','Losses','Win %','Net R'] + (['Closed by news'] if news else [])
        for j, h in enumerate(fixed, 1):
            w.cell(5, j, h); w.cell(4, j, '')
        w.cell(4, 1, 'Whole account-free totals' if False else 'Month and trades')
        for (gt, _, _), c0 in zip(BLOCKS, bstart):
            w.cell(4, c0, gt)
            w.merge_cells(start_row=4, start_column=c0, end_row=4, end_column=c0 + NV - 1)
            for k, lab in enumerate(labels): w.cell(5, c0 + k, lab)
        w.merge_cells(start_row=4, start_column=1, end_row=4, end_column=base)
        for row in (4, 5):
            for c in range(1, bstart[-1] + NV):
                cell = w.cell(row, c); cell.font = f_hdr; cell.fill = fill_hdr; cell.alignment = center
        w.row_dimensions[5].height = 42
        for i, m in enumerate(months):
            rr = FIRST + i
            b, v = res[key].get(m, (None, None)) if m in res[key] else (None, None)
            b = b or dict(trades=0, wins=0, losses=0, netR=0.0, newsClosed=0)
            w.cell(rr, 1, mtxt(m))
            w.cell(rr, 2, b['trades']); w.cell(rr, 3, b['wins']); w.cell(rr, 4, b['losses'])
            w.cell(rr, 5, f'=IF(B{rr}>0,C{rr}/B{rr},"")'); w.cell(rr, 6, float(b['netR']))
            if news: w.cell(rr, 7, b['newsClosed'])
            for (gt, fld, fmt), c0 in zip(BLOCKS, bstart):
                for k, vn in enumerate(VN):
                    d = v.get(vn) if v else None
                    val = d[fld] if d else 0
                    cell = w.cell(rr, c0 + k, float(val) if fld != 'trades' else int(val))
                    if fld == 'net' and d and d['ruined']:
                        cell.fill = fill_red; cell.font = f_white
            for c in range(1, bstart[-1] + NV):
                cell = w.cell(rr, c)
                if cell.font != f_white: cell.font = f_norm
        # summary rows
        cols = list(range(2, bstart[-1] + NV))
        def kind(c):
            """net R / Net $: every row; Win %: total and average; counts: total and average; falls and single losses: average, best = smallest, worst = largest"""
            if c < bstart[0]: return 'r' if c == 6 else ('pct' if c == 5 else 'cnt')
            b = max(i for i, s0 in enumerate(bstart) if c >= s0)
            return ('net', 'fall', 'fall', 'cnt')[b]
        for row, lab in SUMROWS:
            w.cell(row, 1, lab).font = f_bold
            for c in cols:
                col = L(c); kd = kind(c)
                if kd in ('net', 'r'): f = sumformula(row, col, FIRST, LAST)
                elif kd == 'pct':
                    if row == TOT: f = f'=IF(B{TOT}>0,C{TOT}/B{TOT},"")'
                    elif row == AVG: f = sumformula(row, col, FIRST, LAST)
                    else: continue
                elif kd == 'cnt':
                    if row in (TOT, AVG): f = sumformula(row, col, FIRST, LAST)
                    else: continue
                else:
                    if row == AVG: f = sumformula(row, col, FIRST, LAST)
                    elif row == BEST: f = f'=MIN({col}{FIRST}:{col}{LAST})'
                    elif row == WORST: f = f'=MAX({col}{FIRST}:{col}{LAST})'
                    else: continue
                w.cell(row, c, f)
        w.cell(BLOWN, 1, 'Months blown').font = f_bold
        for k, vn in enumerate(VN):
            n = sum(1 for m in months if m in res[key] and res[key][m][1] and res[key][m][1].get(vn) and res[key][m][1][vn]['ruined'])
            w.cell(BLOWN, bstart[0] + k, n)
        # formats
        fm = {2: CNT, 3: CNT, 4: CNT, 5: PCT, 6: RF, 7: CNT}
        for rr in list(range(FIRST, LAST + 1)) + [r for r, _ in SUMROWS] + [BLOWN]:
            for c in cols:
                cell = w.cell(rr, c)
                if cell.font.name != F or cell.font.color is None or cell.font.color.rgb != 'FFFFFFFF':
                    cell.font = f_bold if rr >= TOT else f_norm
                if c < bstart[0]: fmt = fm[c]
                else: fmt = BLOCKS[(c - bstart[0]) // NV][2]
                if rr in (PROF, LOSS, BLOWN): fmt = CNT
                if rr == AVG and c in (2, 3, 4, 7): fmt = '0.0'
                if rr == AVG and fm.get(c) == CNT and c >= bstart[3]: fmt = '0.0'
                if rr == AVG and c >= bstart[3]: fmt = '0.0'
                cell.number_format = fmt
        w.column_dimensions['A'].width = 10
        for c in range(2, bstart[-1] + NV): w.column_dimensions[L(c)].width = 11
        w.freeze_panes = 'B6'
    # --- Summary
    sm.column_dimensions['A'].width = 26; sm.column_dimensions['B'].width = 10
    for c in range(3, 3 + NV): sm.column_dimensions[L(c)].width = 13
    sblocks = [('Total of the 70 monthly results ($)', TOT, USD), ('Months in profit', PROF, CNT),
               ('Worst month ($)', WORST, USD), ('Months the $10,000 account was blown', BLOWN, CNT)]
    r = 1; ranges = []
    for title, trow, fmt in sblocks:
        sm.cell(r, 1, title).font = Font(name=F, size=11, bold=True); r += 1
        for j, h in enumerate(['Strategy', 'Timeframe'] + labels, 1):
            c = sm.cell(r, j, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
        sm.row_dimensions[r].height = 30; r += 1; r0 = r
        for s, nm in zip(strategies, snames):
            sm.cell(r, 1, nm).font = f_norm; sm.cell(r, 2, s['tf']).font = f_norm
            for k in range(NV):
                c = sm.cell(r, 3 + k, f"={q(nm)}!{L(bstart[0] + k)}{trow}")
                c.font = f_norm; c.number_format = fmt
            r += 1
        ranges.append((title, f'C{r0}:{L(2 + NV)}{r - 1}')); r += 1
    for title, rng in ranges:
        if title.startswith('Total') or title.startswith('Worst'):
            sm.conditional_formatting.add(rng, ColorScaleRule(start_type='min', start_color='F8696B', mid_type='num', mid_value=0, mid_color='FFFFFF', end_type='max', end_color='63BE7B'))
    sm.freeze_panes = 'C1'
    # --- By month sheets
    used = set()
    for k, (lab, vn) in enumerate(zip(labels, VN)):
        nm = ('By month - ' + re.sub(r'[/\\?*\[\]:]', '-', lab))[:31]
        assert nm not in used; used.add(nm)
        w = wb.create_sheet(nm)
        w['A1'] = f"{lab} - net result per month ($) - {info['title']}"; w['A1'].font = Font(name=F, size=12, bold=True)
        hdr = ['Month'] + snames + ['All 19']
        for j, h in enumerate(hdr, 1):
            c = w.cell(3, j, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center
        w.row_dimensions[3].height = 42
        nc = len(hdr)
        for i, m in enumerate(months):
            rr = 4 + i; w.cell(rr, 1, mtxt(m)).font = f_norm
            for j, nmS in enumerate(snames):
                c = w.cell(rr, 2 + j, f"={q(nmS)}!{L(bstart[0] + k)}{FIRST + i}"); c.font = f_norm; c.number_format = USD
            c = w.cell(rr, nc, f'=SUM(B{rr}:{L(nc-1)}{rr})'); c.font = f_bold; c.number_format = USD
        a, z = 4, 3 + len(months)
        for n, (row, lb) in enumerate(SUMROWS):
            rr = z + 2 + n; w.cell(rr, 1, lb).font = f_bold
            for c in range(2, nc + 1):
                f = sumformula(row, L(c), a, z)
                cell = w.cell(rr, c, f); cell.font = f_bold
                cell.number_format = CNT if row in (PROF, LOSS) else USD
        w.column_dimensions['A'].width = 18
        for c in range(2, nc + 1): w.column_dimensions[L(c)].width = 13
        w.freeze_panes = 'B4'
    out = f"{S}/{info['filename']}"
    wb.save(out); return out

if __name__ == '__main__':
    for fk in ('file1', 'file2'): print(build(fk))
