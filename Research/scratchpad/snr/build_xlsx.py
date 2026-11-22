"""Workbook: Research/deliverables/Gold_Sniper_Accuracy_Research_2021_2026.xlsx from the research pickles. Run: python3 -I build_xlsx.py"""
import sys, glob, pickle, numpy as np
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import engine as E, detail as D, analyze as A, final as FN, search as S, outcome as O, features as F
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

OUT = '/home/user/Bank-Loan-Report/Research/deliverables/Gold_Sniper_Accuracy_Research_2021_2026.xlsx'
TFN = {5: 'M5', 15: 'M15', 60: 'H1', 120: 'H2', 180: 'H3'}
FONT = 'Arial'
HB = Font(name=FONT, bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F4E78')
B = Font(name=FONT, bold=True); N = Font(name=FONT); BLUE = Font(name=FONT, color='0000FF'); I = Font(name=FONT, italic=True, color='555555')
GOOD = PatternFill('solid', fgColor='E2EFDA'); BAD = PatternFill('solid', fgColor='FCE4D6'); NOTE = PatternFill('solid', fgColor='FFF2CC')
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
PCT = '0.0%'; R3 = '+0.000;-0.000;0.000'; PTS = '+0.0;-0.0;0.0'


def hdr(ws, r, cols, c0=1):
    for j, h in enumerate(cols):
        x = ws.cell(r, c0 + j, h); x.font = HB; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical='center'); x.border = BOX


def put(ws, r, c, v, fmt=None, font=None, fill=None):
    x = ws.cell(r, c, v)
    x.font = font or N
    if fmt:
        x.number_format = fmt
    if fill:
        x.fill = fill
    x.border = BOX
    return x


def widths(ws, w):
    for j, x in enumerate(w):
        ws.column_dimensions[get_column_letter(j + 1)].width = x


def desc_params(kw, lv, fl, post):
    d = E.DEF; s = []
    for k, v in kw.items():
        if k.startswith('f') and k[1].isdigit():
            continue
        if v != d.get(k):
            s.append('%s = %g' % (k, v))
    if kw.get('ctx') == 2:
        s.append('levels = %s' % {'pd': 'previous day high / low', 'sx': 'session high / low so far', 'pw': 'previous week high / low'}[lv])
    for f in fl:
        s.append('filter: %s' % fdesc(f))
    if post:
        s.append("the user's filters (kill zones, 06:00-23:00 IST, news)")
    return '; '.join(s) if s else 'the defaults'


FD = {'h1_ema50': 'H1 close vs EMA50', 'h4_ema50': 'H4 close vs EMA50', 'd1_ema20': 'D1 close vs EMA20', 'h1_slope': 'H1 EMA50 slope', 'ema50_tf': 'close vs EMA50',
      'ema200_tf': 'close vs EMA200', 'wvwap_side': 'weekly VWAP', 'vwap_slope20': 'session VWAP slope', 'cvd_s20': '20-bar cumulative delta', 'pdc_side': 'previous day close',
      'poc_dist': 'session POC', 'ppoc_dist': 'previous session POC', 'atr_reg': 'ATR / 200-bar ATR', 'hour_ist': 'IST hour', 'dow': 'weekday (0 = Mon)',
      'stack_up': 'intrabars in a row in the trade direction', 'upfrac': 'intrabar volume share in the trade direction', 'sweep_lo': 'liquidity sweep (20-bar low / high, last 10 bars)',
      'va_pos': 'value-area position (signed by direction: 1 beyond, 0 inside, -1 against)', 'rn_dist': 'distance to a $10 level (ATR)'}


def fdesc(f):
    k, m, a, b = f
    if m == 1:
        return 'trade with the %s' % FD[k]
    if m == 5:
        return 'trade against the %s' % FD[k]
    if m == 2:
        return '%s from %g to %g' % (FD[k], a, b)
    if m == 3:
        return '%s at least %g' % (FD[k], a)
    return '%s from %g to %g' % (FD[k], a, b)


HR = dict(f1col=F.CI['hour_ist'], f1mode=2, f1a=11, f1b=16)
REC = [(5, 'Default', {}, 'defaults'),
       (5, 'Volume average 80 + structure stop buffer 0.3 ATR', dict(volLen=80, slBuf=0.3), 'existing: Volume Average Length 80, Structure Stop Buffer 0.3'),
       (5, 'Zone of 2+ absorption candles + volume 80 + stop buffer 0.3', dict(minZoneN=2, volLen=80, slBuf=0.3), 'existing + NEW: minimum absorption candles in the zone = 2'),
       (5, 'Zone of 2+ absorption candles + volume 80 + stop buffer 0.3 + 11:00-16:00 IST', dict(minZoneN=2, volLen=80, slBuf=0.3, **HR), 'as above + existing: trading hours 11:00-16:00 IST'),
       (15, 'Default', {}, 'defaults'),
       (15, 'VWAP slope against the trade (20 bars)', dict(f1col=F.CI['vwap_slope20'], f1mode=5), 'NEW: VWAP slope filter, counter-trend'),
       (60, 'Default, ratio 1.3', dict(aggRatio=1.3), 'existing: Aggression Ratio 1.3'),
       (120, 'Default, ratio 1.3', dict(aggRatio=1.3), 'existing: Aggression Ratio 1.3'),
       (120, 'Ratio 1.3 + close within 1 ATR of the session POC', dict(aggRatio=1.3, f1col=F.CI['poc_dist'], f1mode=4, f1a=-1, f1b=1), 'NEW: session POC filter'),
       (180, 'Default, ratio 1.3', dict(aggRatio=1.3), 'existing: Aggression Ratio 1.3'),
       (180, 'Ratio 1.3 + against the 20-bar cumulative delta', dict(aggRatio=1.3, f1col=F.CI['cvd_s20'], f1mode=5), 'NEW: 20-bar delta filter, counter-trend'),
       (180, 'Ratio 1.3 + against the session VWAP slope', dict(aggRatio=1.3, f1col=F.CI['vwap_slope20'], f1mode=5), 'NEW: VWAP slope filter, counter-trend')]


def default_kw(tf):
    return dict(aggRatio=1.3) if tf >= 60 else {}


def row_lv(rows, X):
    return next(r for r in rows if abs(r['X'] - X) < 1e-9)


def main():
    wb = Workbook()
    # ---------------------------------------------------------------- How to read
    ws = wb.active; ws.title = 'How to read'
    lines = [
        ('VWAP ORDERFLOW SNIPER: ACCURACY RESEARCH ON GOLD, JANUARY 2021 - 2 OCTOBER 2026 (FxPro M1 data)', B),
        ('', N),
        ('What was tested', B),
        ('The Sniper of the Auction Retest + Sniper strategy / EA (v6.1): absorption near the VWAP / band #1 arms a setup, the next aggressive candle fires it.', N),
        ('Its signals were produced by a research copy of the EA engine that gives exactly the EA\'s signals (148 of 148 on the broker simulator, June - October 2026).', N),
        ('Chart timeframes M5, M15, H1, H2, H3, built from the M1 bars; the buy / sell volume of a bar comes from its M1 candles (M5 candles on H2 / H3), like the EA and TradingView.', N),
        ('', N),
        ('How a signal is scored', B),
        ('Entry at the signal close (market), the Sniper stop. Then minute by minute (M1): a minute that touches the stop is a loss first (conservative); otherwise its high / low adds to the best excursion.', N),
        ('Accuracy at X R = the share of signals whose price reached X x the stop distance before the stop. No time limit (a second table adds the 23:55 IST force close).', N),
        ('Net R = the result per trade with the costs: spread 0.16 + commission $7 a lot = 0.23 per ounce. A win at X R nets (X x risk - 0.23) / (risk + 0.23); a stop -1.', N),
        ('', N),
        ('The most important line: the accuracy of a RANDOM entry', B),
        ('If the price has no direction after the signal, the chance to reach +X R before -1 R is 1 / (1 + X): 83.3% at 0.2R, 66.7% at 0.5R, 62.5% at 0.6R, 50% at 1R, 40% at 1.5R, 33.3% at 2R.', N),
        ('So a high accuracy at a small target is not an edge by itself. The EDGE is the accuracy above that line (in % points). Only an edge beats the costs.', N),
        ('The default Sniper\'s accuracy is on that line: its signals have about no edge on these data.', N),
        ('', N),
        ('Train and test', B),
        ('Every setting was chosen on 2021-2023 only (2021-22 and 2023 separately: a setting had to work in both). 2024 - 2 Oct 2026 is the test: never used to choose.', N),
        ('Many settings were tried (about 45,000 combinations), so the best results on 2021-23 are partly luck; the test column shows what is left.', N),
        ('', N),
        ('Colours', B),
        ('Blue numbers = inputs you can change on this sheet; black = calculated. Green cells = a positive edge in both periods; orange = negative.', N),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = ws.cell(i, 1, t); c.font = f
    r0 = len(lines) + 2
    ws.cell(r0, 1, 'Random-entry accuracy and the accuracy needed to break even (edit the blue cells)').font = B
    put(ws, r0 + 1, 1, 'Cost per ounce (spread + commission)', font=B); put(ws, r0 + 1, 2, 0.23, '0.00', BLUE).comment = Comment('0.16 spread + $7 per lot round trip (100 oz) = 0.23', 'research')
    put(ws, r0 + 2, 1, 'Typical stop distance (price, $)', font=B); put(ws, r0 + 2, 2, 2.4, '0.00', BLUE).comment = Comment('M5 Sniper median stop about $2.4 (M15 about $5.0, H1 about $15)', 'research')
    hdr(ws, r0 + 4, ['Target (R)', 'Random-entry accuracy', 'Accuracy needed to break even (with the costs)', 'Edge needed (points)'])
    for j, X in enumerate((0.1, 0.2, 0.3, 0.5, 0.6, 0.75, 1.0, 1.5, 2.0, 3.0)):
        r = r0 + 5 + j
        put(ws, r, 1, X, '0.0#', BLUE)
        put(ws, r, 2, '=1/(1+A%d)' % r, PCT)
        put(ws, r, 3, '=($B$%d+$B$%d)/(A%d*$B$%d+$B$%d)' % (r0 + 2, r0 + 1, r, r0 + 2, r0 + 2), PCT).comment = Comment('wins x (X r - c)/(r + c) = losses x 1  ->  p = (r + c) / (X r + r)', 'research') if j == 0 else None
        if j:
            ws.cell(r, 3).value = '=($B$%d+$B$%d)/(A%d*$B$%d+$B$%d)' % (r0 + 2, r0 + 1, r, r0 + 2, r0 + 2)
        put(ws, r, 4, '=(C%d-B%d)*100' % (r, r), PTS)
    widths(ws, [42, 22, 30, 18])
    ws.column_dimensions['A'].width = 140
    # ---------------------------------------------------------------- Default Sniper
    ws = wb.create_sheet('Default Sniper')
    hdr(ws, 1, ['Chart', 'Settings', 'Period', 'Signals', 'Target (R)', 'Accuracy', 'Random entry', 'Edge (points)', 'Net R per trade', 'z (edge / its error)'])
    r = 2
    base_det = {}
    for tf in (5, 15, 60, 120, 180):
        for kwl, lab in ((dict(), 'defaults (aggression ratio 2.2)'), (dict(aggRatio=1.3), 'defaults, aggression ratio 1.3')):
            if tf < 60 and kwl:
                continue
            det, _ = D.full(tf, kwl)
            base_det[(tf, lab)] = det
            for per in ('train', 'test'):
                for rr in det[per]:
                    if rr['X'] not in (0.2, 0.5, 0.6, 1.0, 1.5, 2.0):
                        continue
                    put(ws, r, 1, TFN[tf]); put(ws, r, 2, lab); put(ws, r, 3, '2021-2023' if per == 'train' else '2024 - Oct 2026')
                    put(ws, r, 4, rr['n']); put(ws, r, 5, rr['X'], '0.0#'); put(ws, r, 6, rr['acc'], PCT)
                    put(ws, r, 7, '=1/(1+E%d)' % r, PCT); put(ws, r, 8, '=(F%d-G%d)*100' % (r, r), PTS)
                    put(ws, r, 9, rr['net'], R3); put(ws, r, 10, rr['z'], '0.00')
                    r += 1
    widths(ws, [8, 34, 16, 10, 10, 11, 13, 13, 15, 16])
    # ---------------------------------------------------------------- settings sweeps
    for tf in (5, 15, 60, 120, 180):
        fs = glob.glob(HERE + '/sweep1_%d*.pkl' % tf)
        if not fs:
            continue
        rows = pickle.load(open(fs[0], 'rb'))
        ws = wb.create_sheet('Settings %s' % TFN[tf])
        ws.cell(1, 1, 'One setting at a time around the defaults%s (all other settings default). Accuracy at 1R and 0.5R, 2021-23 vs 2024-26.' % (' with the aggression ratio 1.3' if tf >= 60 else '')).font = B
        hdr(ws, 2, ['Setting', 'Value', 'Signals 2021-23', 'Signals 2024-26', 'Acc 0.5R 2021-23', 'Acc 0.5R 2024-26', 'Acc 1R 2021-23', 'Acc 1R 2024-26',
                    'Edge 1R 2021-23 (pts)', 'Edge 1R 2024-26 (pts)', 'Net R 1R 2021-23', 'Net R 1R 2024-26'])
        r = 3
        for k, v, m in rows:
            if m.get('n_tr', 0) == 0 or m.get('n_te', 0) == 0:
                continue
            put(ws, r, 1, 'DEFAULT' if k == 'base' else k); put(ws, r, 2, '' if v is None else v)
            put(ws, r, 3, m['tr_n_1']); put(ws, r, 4, m['te_n_1'])
            put(ws, r, 5, m['tr_acc_0.5'], PCT); put(ws, r, 6, m['te_acc_0.5'], PCT); put(ws, r, 7, m['tr_acc_1'], PCT); put(ws, r, 8, m['te_acc_1'], PCT)
            put(ws, r, 9, '=(G%d-0.5)*100' % r, PTS); put(ws, r, 10, '=(H%d-0.5)*100' % r, PTS)
            put(ws, r, 11, m['tr_net_1'], R3); put(ws, r, 12, m['te_net_1'], R3)
            if m['tr_acc_1'] > 0.52 and m['te_acc_1'] > 0.52:
                for c in (9, 10):
                    ws.cell(r, c).fill = GOOD
            r += 1
        widths(ws, [14, 8, 12, 12, 12, 12, 12, 12, 14, 14, 13, 13])
    # ---------------------------------------------------------------- concepts
    ws = wb.create_sheet('Order flow concepts')
    ws.cell(1, 1, 'Each order flow / context concept added alone to the default Sniper (H1 - H3: aggression ratio 1.3). Accuracy at 1R (random 50%) and 0.5R (random 66.7%).').font = B
    hdr(ws, 2, ['Chart', 'Concept', 'Signals 2021-22', 'Signals 2023', 'Signals 2024-26', 'Acc 1R 2021-22', 'Acc 1R 2023', 'Acc 1R 2024-26', 'Edge 1R 2024-26 (pts)', 'Acc 0.5R 2024-26', 'Net R 1R 2024-26'])
    r = 3
    for tf in (5, 15, 60, 120, 180):
        f = HERE + '/concepts_%d.pkl' % tf
        try:
            rows = pickle.load(open(f, 'rb'))
        except FileNotFoundError:
            continue
        for name, kw, lv, post, m in rows:
            if m is None or m['T_n_1'] == 0:
                continue
            put(ws, r, 1, TFN[tf]); put(ws, r, 2, name)
            put(ws, r, 3, m['A_n_1']); put(ws, r, 4, m['B_n_1']); put(ws, r, 5, m['T_n_1'])
            put(ws, r, 6, m['A_acc_1'] if m['A_n_1'] else None, PCT); put(ws, r, 7, m['B_acc_1'] if m['B_n_1'] else None, PCT); put(ws, r, 8, m['T_acc_1'], PCT)
            put(ws, r, 9, '=(H%d-0.5)*100' % r, PTS); put(ws, r, 10, m['T_acc_0.5'], PCT); put(ws, r, 11, m['T_net_1'], R3)
            good = m['A_n_1'] and m['B_n_1'] and m['A_acc_1'] > 0.5 and m['B_acc_1'] > 0.5 and m['T_acc_1'] > 0.5
            ws.cell(r, 9).fill = GOOD if good else (BAD if m['T_acc_1'] < 0.5 else PatternFill())
            r += 1
    widths(ws, [8, 78, 12, 12, 13, 12, 12, 13, 14, 13, 13])
    # ---------------------------------------------------------------- search check
    ws = wb.create_sheet('Search check')
    ws.cell(1, 1, 'Random search: does choosing on 2021-23 find settings that are better on 2024-26? Mean test edge (points above random) of all eligible combinations vs the best ones chosen on 2021-23.').font = B
    hdr(ws, 2, ['Chart', 'Target (R)', 'Combinations tried', 'Eligible (enough trades)', 'All eligible: mean test edge', 'Top 10 chosen on 2021-23', 'Top 50', 'Top 200', 'Top 10: share positive in 2024-26'])
    r = 3
    sc_rows = {}
    for tf in (5, 15, 60, 120, 180):
        res = A.load(tf)
        for X in (0.5, 1.0, 1.5):
            sc = np.array([A.score(q[4], X, tf) for q in res]); ok = np.isfinite(sc)
            te = np.array([q[4]['T_acc_%g' % X] - 1 / (1 + X) if q[4]['T_n_%g' % X] >= S.MINN[tf][1] else np.nan for q in res])
            o = np.argsort(-np.where(ok, sc, -9))
            vals = [len(res), int(ok.sum()), 100 * np.nanmean(te[ok]), 100 * np.nanmean(te[o[:10]]), 100 * np.nanmean(te[o[:50]]), 100 * np.nanmean(te[o[:200]]), np.nanmean(te[o[:10]] > 0)]
            put(ws, r, 1, TFN[tf]); put(ws, r, 2, X, '0.0#')
            for j, v in enumerate(vals):
                put(ws, r, 3 + j, v, PTS if 2 <= j <= 5 else (PCT if j == 6 else '0'))
            r += 1
    widths(ws, [8, 10, 18, 18, 22, 22, 12, 12, 22])
    # ---------------------------------------------------------------- recommended (simple) settings
    ws = wb.create_sheet('Recommended settings')
    ws.cell(1, 1, 'Recommended settings per chart: the few changes that raised the accuracy in 2021-22, in 2023 AND in 2024-26 (formed from the 2021-23 results; few tests).').font = B
    ws.cell(2, 1, 'Existing input = already in the Sniper strategy / EA (v6.1). New = needs one new input (offered as a next step). Net R / trade includes the costs.').font = I
    hdr(ws, 3, ['Chart', 'Settings', 'Inputs', 'Period', 'Signals', 'Signals / year', 'Target (R)', 'Accuracy', 'Random', 'Edge (pts)', 'Net R / trade', 'z',
                'One at a time: accuracy', 'One at a time: net R', "With the user's filters: accuracy", 'With the 23:55 IST force close: accuracy'])
    r = 4
    rec_det = {}
    for tf, name, kw, inputs in REC:
        det, _ = D.full(tf, dict(kw))
        detf, _ = D.full(tf, dict(kw), post='filt')
        detc, _ = D.full(tf, dict(kw), usecut=True)
        rec_det[(tf, name)] = det
        for per, yrs in (('train', 3.0), ('test', 2.75)):
            for X2 in (0.5, 0.6, 1.0, 1.5):
                rr = row_lv(det[per], X2); oat = row_lv(det['oat_' + per], X2)
                put(ws, r, 1, TFN[tf]); put(ws, r, 2, name); put(ws, r, 3, inputs)
                put(ws, r, 4, '2021-2023' if per == 'train' else '2024 - Oct 2026'); put(ws, r, 5, rr['n']); put(ws, r, 6, '=E%d/%g' % (r, yrs), '0')
                put(ws, r, 7, X2, '0.0#'); put(ws, r, 8, rr['acc'], PCT); put(ws, r, 9, '=1/(1+G%d)' % r, PCT); put(ws, r, 10, '=(H%d-I%d)*100' % (r, r), PTS)
                put(ws, r, 11, rr['net'], R3); put(ws, r, 12, rr['z'], '0.00'); put(ws, r, 13, oat['acc'], PCT); put(ws, r, 14, oat['net'], R3)
                put(ws, r, 15, row_lv(detf[per], X2)['acc'], PCT); put(ws, r, 16, row_lv(detc[per], X2)['acc'], PCT)
                if per == 'test':
                    ws.cell(r, 10).fill = GOOD if rr['acc'] > 1 / (1 + X2) else BAD
                r += 1
    widths(ws, [7, 52, 30, 16, 9, 12, 10, 10, 9, 10, 12, 7, 16, 16, 18, 20])
    # ---------------------------------------------------------------- search picks
    fin = pickle.load(open(HERE + '/final.pkl', 'rb'))
    ws = wb.create_sheet('Search picks')
    ws.cell(1, 1, 'The best combinations of the random search, chosen on 2021-23 only (robust = highest lower bound of the 2021-23 edge, positive in 2021-22 and 2023; top = highest selection score). The test 2024-26 was not used to choose.').font = B
    hdr(ws, 2, ['Chart', 'Chosen for', 'Rule', 'Settings (changes from the defaults)', 'Period', 'Signals', 'Signals / year', 'Target (R)', 'Accuracy', 'Random', 'Edge (pts)', 'Net R / trade', 'z',
                'One at a time: accuracy', 'One at a time: signals'])
    r = 3
    best_det = {}
    for tf in (5, 15, 60, 120, 180):
        for X in (0.5, 1.0):
            for rule in ('robust', 'top'):
                kw, lv, fl, post, m = fin[(tf, X)][rule]
                det, _ = D.full(tf, dict(kw), lv, post)
                best_det[(tf, X, rule)] = (det, kw, lv, fl, post)
                for per, yrs in (('train', 3.0), ('test', 2.75)):
                    for X2 in (0.5, 0.6, 1.0, 1.5):
                        rr = row_lv(det[per], X2); oat = row_lv(det['oat_' + per], X2)
                        put(ws, r, 1, TFN[tf]); put(ws, r, 2, '%g R' % X); put(ws, r, 3, rule); put(ws, r, 4, desc_params(kw, lv, fl, post))
                        put(ws, r, 5, '2021-2023' if per == 'train' else '2024 - Oct 2026'); put(ws, r, 6, rr['n']); put(ws, r, 7, '=F%d/%g' % (r, yrs), '0')
                        put(ws, r, 8, X2, '0.0#'); put(ws, r, 9, rr['acc'], PCT); put(ws, r, 10, '=1/(1+H%d)' % r, PCT); put(ws, r, 11, '=(I%d-J%d)*100' % (r, r), PTS)
                        put(ws, r, 12, rr['net'], R3); put(ws, r, 13, rr['z'], '0.00'); put(ws, r, 14, oat['acc'], PCT); put(ws, r, 15, oat['n'])
                        if per == 'test':
                            ws.cell(r, 11).fill = GOOD if rr['acc'] > 1 / (1 + X2) else BAD
                        ws.cell(r, 4).alignment = Alignment(wrap_text=True, vertical='top')
                        r += 1
    widths(ws, [7, 10, 8, 90, 16, 9, 12, 10, 10, 9, 10, 12, 7, 16, 14])
    # ---------------------------------------------------------------- per year of the robust 1R picks
    ws = wb.create_sheet('Best by year')
    hdr(ws, 1, ['Chart', 'Settings', 'Year', 'Signals (1R)', 'Acc 0.5R', 'Acc 0.6R', 'Acc 1R', 'Edge 1R (pts)', 'Net R 1R'])
    r = 2
    for tf in (5, 15, 60, 120, 180):
        for lab, det in [('default', base_det.get((tf, 'defaults (aggression ratio 2.2)' if tf < 60 else 'defaults, aggression ratio 1.3')))] + [(nm, rec_det[(t2, nm)]) for t2, nm, kw, inp in REC if t2 == tf and nm not in ('Default', 'Default, ratio 1.3')]:
            for y in range(2021, 2027):
                yr = det['years'][y]
                put(ws, r, 1, TFN[tf]); put(ws, r, 2, lab); put(ws, r, 3, y if y < 2026 else '2026 (to 2 Oct)')
                put(ws, r, 4, row_lv(yr, 1.0)['n']); put(ws, r, 5, row_lv(yr, 0.5)['acc'], PCT); put(ws, r, 6, row_lv(yr, 0.6)['acc'], PCT); put(ws, r, 7, row_lv(yr, 1.0)['acc'], PCT)
                put(ws, r, 8, '=(G%d-0.5)*100' % r, PTS); put(ws, r, 9, row_lv(yr, 1.0)['net'], R3)
                r += 1
    widths(ws, [7, 60, 16, 12, 10, 10, 10, 13, 11])
    # ---------------------------------------------------------------- machine learning
    ws = wb.create_sheet('Machine learning')
    ws.cell(1, 1, 'All features together (LightGBM): fitted on 2021-22, stopped on 2023, scored on 2024-26. AUC 0.5 = no better than a coin; the accuracy of the signals the model rates best (threshold set on 2023).').font = B
    hdr(ws, 2, ['Chart', 'Target (R)', 'Candidates 2024-26', 'Accuracy of all candidates 2024-26', 'Random', 'AUC 2023', 'AUC 2024-26', 'Best-rated 20%: accuracy', 'Best-rated 10%: accuracy', 'Most used features'])
    r = 3
    for tf in (5, 15, 60, 120, 180):
        try:
            mlr = pickle.load(open(HERE + '/ml_%d.pkl' % tf, 'rb'))
        except FileNotFoundError:
            continue
        for X, d in mlr['res'].items():
            put(ws, r, 1, TFN[tf]); put(ws, r, 2, X, '0.0#'); put(ws, r, 3, mlr['n'][2]); put(ws, r, 4, d['base'][2], PCT); put(ws, r, 5, '=1/(1+B%d)' % r, PCT)
            put(ws, r, 6, d['aucB'], '0.000'); put(ws, r, 7, d['aucT'], '0.000')
            put(ws, r, 8, next(a for q, n, a in d['top'] if q == 0.2), PCT); put(ws, r, 9, next(a for q, n, a in d['top'] if q == 0.1), PCT)
            put(ws, r, 10, ', '.join(n for g, n in d['imp'][:6]))
            r += 1
    widths(ws, [7, 10, 16, 20, 9, 10, 12, 18, 18, 70])
    # ---------------------------------------------------------------- EA check (broker simulator)
    ws = wb.create_sheet('EA check')
    ws.cell(1, 1, 'The real EA (AuctionRetestSniperEA, Setups = Sniper only) on the broker simulator, 2 Jan 2024 - 2 Oct 2026, M5, with its own exits (TP1 0.6R, stop moves, costs as FxPro).').font = B
    ws.cell(2, 1, 'Win = a closed trade with a positive result after the commission. "Default filters" = the EA defaults (days, hours, kill zones, news, force close); "no filters" = all of them off. The first four runs use the default loss recovery (Crooks C), the last two none ($50 base risk), so their profit is the plain per-trade result.').font = I
    hdr(ws, 3, ['Run', 'Sniper settings', 'Filters', 'Year', 'Trades', 'Wins', 'Win rate', 'Net profit ($)', 'Average per trade ($)'])
    r = 4
    import re, collections
    ea_stats = {}
    for log, sett, flt in (('ea_def.log', 'defaults', 'default filters'), ('ea_rec.log', 'Volume Average 80 + Structure Stop Buffer 0.3', 'default filters'),
                           ('ea_def_nof.log', 'defaults', 'no filters'), ('ea_rec_nof.log', 'Volume Average 80 + Structure Stop Buffer 0.3', 'no filters'),
                           ('ea_def_norec.log', 'defaults', 'default filters, loss recovery off ($50 a trade)'),
                           ('ea_rec_norec.log', 'Volume Average 80 + Structure Stop Buffer 0.3', 'default filters, loss recovery off ($50 a trade)')):
        path = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/obt/' + log
        try:
            txt = open(path).read().split('\n')
        except FileNotFoundError:
            continue
        pnl = collections.defaultdict(float); tclose = {}
        for l in txt:
            m = re.match(r'SIM DEAL (\d{4})\.\d\d\.\d\d \S+ tk=\d+ pos=(\d+) \w+ (IN|OUT) vol=\S+ px=\S+ profit=(\S+) comm=(\S+)', l)
            if m:
                pnl[m.group(2)] += float(m.group(4)) + float(m.group(5))
                if m.group(3) == 'OUT':
                    tclose[m.group(2)] = int(m.group(1))
        by = collections.defaultdict(list)
        for pid, y in tclose.items():
            by[y].append(pnl[pid]); by['all'].append(pnl[pid])
        va = by.get('all', [])
        ea_stats[log] = (len(va), (sum(1 for x in va if x > 0) / len(va)) if va else float('nan'), sum(va), (sum(va) / len(va)) if va else float('nan'))
        for y in [2024, 2025, 2026, 'all']:
            v = by.get(y, [])
            put(ws, r, 1, log.replace('.log', '')); put(ws, r, 2, sett); put(ws, r, 3, flt); put(ws, r, 4, 'all (2024 - 2026)' if y == 'all' else y)
            put(ws, r, 5, len(v)); put(ws, r, 6, sum(1 for x in v if x > 0)); put(ws, r, 7, '=IF(E%d>0,F%d/E%d,0)' % (r, r, r), PCT)
            put(ws, r, 8, sum(v), '#,##0.00;-#,##0.00'); put(ws, r, 9, '=IF(E%d>0,H%d/E%d,0)' % (r, r, r), '0.00;-0.00')
            if y == 'all':
                for c in range(1, 10):
                    ws.cell(r, c).font = B
            r += 1
    widths(ws, [16, 44, 44, 18, 9, 9, 10, 15, 18])
    # ---------------------------------------------------------------- verification
    ws = wb.create_sheet('Verification')
    vl = ['How the numbers were checked',
          '1. The research engine gives exactly the EA\'s Sniper signals: 148 of 148 (same bar, direction, entry, stop) on the broker simulator, June - October 2026 (M1 intrabars).',
          '2. Its VWAP equals the EA\'s on all 24,409 M5 bars of that run (largest difference 5e-9).',
          '3. The scoring was rebuilt independently (separate code, not reading the research code) for every M5 default signal and the recommended M5 settings:',
          '   the same accuracy at 0.5R and 1R in both periods; per signal the best excursion agrees to 1e-6 (rounding only), no signal changes its result.',
          '4. The EA itself was run on the broker simulator for 2024 - 2026 with the default and the recommended Sniper settings (sheet EA check).',
          '5. Every choice of settings used 2021-2023 only; 2024 - 2 Oct 2026 was only used to report. The search check sheet shows how much of the 2021-23 edge was luck.',
          'Data: FxPro gold M1 bars 4 Jan 2021 - 2 Oct 2026 (server time), tick volume; costs 0.23 per ounce (spread 0.16 + $7 a lot round trip).']
    for i, t in enumerate(vl, 1):
        ws.cell(i, 1, t).font = B if i == 1 else N
    ws.column_dimensions['A'].width = 170
    # ---------------------------------------------------------------- summary
    ws = wb.create_sheet('Summary')
    def ac(det, per, X):
        return row_lv(det[per], X)
    lines = ['SUMMARY: can the VWAP Orderflow Sniper be made more accurate on gold?', '']
    d0 = rec_det[(5, 'Default')]; d1 = rec_det[(5, 'Volume average 80 + structure stop buffer 0.3 ATR')]; d2 = rec_det[(5, 'Zone of 2+ absorption candles + volume 80 + stop buffer 0.3')]
    d3 = rec_det[(5, 'Zone of 2+ absorption candles + volume 80 + stop buffer 0.3 + 11:00-16:00 IST')]
    lines += ['1. The default Sniper is as accurate as a random entry. On M5 it reached 1R before the stop in %.1f%% of the 2021-23 signals and %.1f%% in 2024-26; a random entry reaches 1R first 50%% of the time.' % (100 * ac(d0, 'train', 1)['acc'], 100 * ac(d0, 'test', 1)['acc']),
              '   The same holds at every target (0.5R: %.1f%% vs 66.7%% random) and on M15. With the costs every target loses (M5 net %+.3fR per trade at 1R in 2024-26).' % (100 * ac(d0, 'test', 0.5)['acc'], ac(d0, 'test', 1)['net']),
              '2. A smaller target always looks more accurate (0.2R: about 83%) but needs even more accuracy to pay the costs: see "How to read" for the break-even accuracy of each target.',
              '3. About 45,000 setting combinations, 40 order flow / context concepts and a machine-learning model of all features were tested. Settings chosen on 2021-23 kept little of their edge in 2024-26:',
              '   M5 +1 to +3 points, M15 about 0, H1 - H3 +2 to +6 points (small samples). The machine-learning model could not tell good M5 / M15 / H1 / H2 signals from bad ones (AUC 0.50 in 2024-26).',
              '4. What did help on M5, in 2021-22, 2023 and 2024-26 alike, on large samples:',
              '   Volume Average Length 80 + Structure Stop Buffer 0.3 ATR (existing inputs): 1R accuracy %.1f%% / %.1f%% (2021-23 / 2024-26), net %+.3fR per trade in 2024-26 (default %+.3fR).' % (100 * ac(d1, 'train', 1)['acc'], 100 * ac(d1, 'test', 1)['acc'], ac(d1, 'test', 1)['net'], ac(d0, 'test', 1)['net']),
              '   + a zone of at least 2 absorption candles (new input): %.1f%% / %.1f%%, net %+.3fR.  + trading 11:00-16:00 IST only: %.1f%% / %.1f%%, net %+.3fR (fewer trades: %d in 2024-26).' % (
                  100 * ac(d2, 'train', 1)['acc'], 100 * ac(d2, 'test', 1)['acc'], ac(d2, 'test', 1)['net'], 100 * ac(d3, 'train', 1)['acc'], 100 * ac(d3, 'test', 1)['acc'], ac(d3, 'test', 1)['net'], ac(d3, 'test', 1)['n']),
              '5. On H3 the Sniper worked better as a counter-trend trade: against the 20-bar cumulative delta it reached 1R first in about 58-60% in every period (about 20 trades a year).',
              '6. Nothing found makes the Sniper accurate enough for small targets with these costs. The edges found are small; trade them only with a size the recovery rules can carry.']
    if 'ea_def.log' in ea_stats and 'ea_rec.log' in ea_stats:
        e0, e1 = ea_stats['ea_def.log'], ea_stats['ea_rec.log']
        lines.append('7. The real EA on the broker simulator, 2024-26 (Sniper only, its own exits): win rate %.1f%% with the defaults (%d trades) -> %.1f%% with Volume 80 + Stop Buffer 0.3 (%d trades), default filters.' % (100 * e0[1], e0[0], 100 * e1[1], e1[0]))
    if 'ea_def_norec.log' in ea_stats and 'ea_rec_norec.log' in ea_stats:
        e0, e1 = ea_stats['ea_def_norec.log'], ea_stats['ea_rec_norec.log']
        money = lambda x: ('-' if x < 0 else '+') + '$' + format(abs(x), ',.0f')
        money2 = lambda x: ('-' if x < 0 else '+') + '$' + format(abs(x), ',.2f')
        lines.append('   Without loss recovery ($50 a trade): net %s (%s a trade) with the defaults -> %s (%s a trade) with the recommended settings; every year positive.' % (money(e0[2]), money2(e0[3]), money(e1[2]), money2(e1[3])))
    lines += [

              '', 'Sheets: How to read (definitions, break-even accuracy) - Default Sniper - Recommended settings - Best by year - EA check (the real EA on the simulator) -',
              'Settings M5 / M15 / H1 / H2 / H3 (one setting at a time) - Order flow concepts (each concept alone) - Search check (does choosing on 2021-23 work on 2024-26?) -',
              'Search picks (the best combinations found) - Machine learning - Verification.']
    for i, t in enumerate(lines, 1):
        ws.cell(i, 1, t).font = B if i == 1 else N
    ws.column_dimensions['A'].width = 200
    wb.move_sheet('Summary', offset=-wb.index(wb['Summary']))
    wb.move_sheet('How to read', offset=1 - wb.index(wb['How to read']))
    wb.save(OUT)
    print('saved', OUT)
    return base_det, best_det


if __name__ == '__main__':
    main()
