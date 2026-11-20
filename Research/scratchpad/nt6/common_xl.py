"""Shared helpers for the two workbooks."""
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule
F = 'Arial'
def font(**k): return Font(name=F, size=k.pop('size', 10), **k)
HDR = PatternFill('solid', fgColor='1F3864'); BLUE = '0000FF'
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD = '$#,##0;($#,##0);-'; PCT = '0%;(0%);-'; R1 = '+0.0"R";-0.0"R";-'
GREEN = PatternFill('solid', fgColor='C6EFCE'); RED = PatternFill('solid', fgColor='FFC7CE')
MONTHS = [(y, m) for y in range(2021, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]   # the data end on 2 Oct 2026
def hdr(ws, r, c, v):
    x = ws.cell(r, c, v); x.font = font(bold=True, color='FFFFFF'); x.fill = HDR; x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); return x
def val(ws, r, c, v, fmt=None, inp=True, bold=False):
    x = ws.cell(r, c, v); x.font = font(color=BLUE if inp and isinstance(v, (int, float)) else '000000', bold=bold); x.border = BOX
    if fmt: x.number_format = fmt
    return x
def posneg(ws, rng):
    ws.conditional_formatting.add(rng, CellIsRule(operator='greaterThan', formula=['0'], fill=GREEN))
    ws.conditional_formatting.add(rng, CellIsRule(operator='lessThan', formula=['0'], fill=RED))
def cfg_text(c):
    return '%s, final TP %.1fR, stop %.1f ATR, %s entry%s, chop %s, hours %s, kill zones %s, days %s, VWAP %s, momentum %.2f, stop move %s' % (
        {'both': 'long + short', 'long': 'LONG only', 'short': 'SHORT only'}[c.get('dirn', 'both')], c['tp'], c['stopAtr'], c['entryMode'],
        ' %d%%' % c['entryPct'] if c['entryMode'] == 'model' else '', c['chop'] or 'off', '%02d:%02d-%02d:%02d IST' % (c['hours'][0] // 100, c['hours'][0] % 100, c['hours'][1] // 100, c['hours'][1] % 100) if c['hours'] else 'any',
        {'user': 'Asia + London + New York', 'LNY': 'London + New York', None: 'off'}[c['kz']], 'Tue-Thu' if c['days'] == 'TWT' else 'Mon-Fri', c['vw'], c['momAtr'], c['mv'] or 'off')
def ea_inputs(c):
    rows = [('InpExitAt / InpTp1R', 'TP1, %.1f' % c['tp']), ('InpAllowLong / InpAllowShort', {'both': 'true / true', 'long': 'true / false', 'short': 'false / true'}[c.get('dirn', 'both')]),
            ('InpStopAtr', c['stopAtr']), ('InpEntryMode / InpEntryPct', '%s / %d' % ('ENTRY_MARKET' if c['entryMode'] == 'market' else 'ENTRY_MODEL', c['entryPct'])),
            ('InpChopOn / InpChopMax', 'true / %.1f' % c['chop'] if c['chop'] else 'false'), ('InpHoursOn', ('true, %04d-%04d IST' % c['hours']) if c['hours'] else 'false'),
            ('InpKzOn / Asia / London / New York', {'user': 'true / true / true / true', 'LNY': 'true / false / true / true', None: 'false'}[c['kz']]),
            ('InpDayOn (days)', 'Tue, Wed, Thu' if c['days'] == 'TWT' else 'Mon - Fri'), ('InpVwapAnchor', 'VW_SESSION' if c['vw'] == 'session' else 'VW_MONTH'),
            ('InpMomAtr', c['momAtr']), ('InpMv2On / InpMv3On', {'mv2': 'true / false', 'mv3': 'false / true (to 0R)', None: 'false / false'}[c['mv']])]
    return rows
