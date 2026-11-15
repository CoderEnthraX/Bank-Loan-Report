"""The user's-settings monthly workbooks (asked 2026-11-15, second message): the Auction Retest strategy with the user's settings, gold M5
then M15, final exit TP1 (0.6R) and TP2 (1.0R), every month 2021 - 2 Oct 2026, No recovery + Crooks E + Crooks F - J x the 6 ladder levels:
  Gold_Monthly_YourSettings_1_AllFiltersOff.xlsx    days / hours / kill zones / news off
  Gold_Monthly_YourSettings_2_YourFilters.xlsx      Tue-Thu, 06:00-23:00, kill zones Asia + London + New York, news 17:45-18:15 (+60 min before)
Reuses the layout code of mcej/build_xlsx.py (monthly blocks, summary blocks, read me). Usage: build_user_xlsx.py OUTDIR"""
import sys, pickle, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter as L
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mcej')
import build_xlsx as BX
OUT = sys.argv[1] if len(sys.argv) > 1 else S + '/mcej2/out'

M = pickle.load(open(S + '/mcej2/user_money.pkl', 'rb')); MS = M['months']; RUNS = M['runs']
T = pickle.load(open(S + '/mcej2/user_trades.pkl', 'rb')); COSTS = pickle.load(open(S + '/mcej2/user_costs.pkl', 'rb'))
# the layout code works on module globals: one extra column (No recovery) before Crooks E
BX.CONFIGS = list(M['configs']); BX.RULES = ('Off',) + BX.RULES; BX.NC = len(BX.CONFIGS); BX.CL = BX.C0 + BX.NC - 1
C0, CL, CONFIGS, LEVELS = BX.C0, BX.CL, BX.CONFIGS, BX.LEVELS
GROUP_START = {C0, C0 + 1} | {C0 + 2 + 6 * k for k in range(5)}
fill_dead = PatternFill('solid', fgColor='D9D9D9')
f_norm, f_bold, f_note, f_hdr, f_blue = BX.f_norm, BX.f_bold, BX.f_note, BX.f_hdr, BX.f_blue
USD, CNT = BX.USD, BX.CNT


def cfgname(c):
    if c[0] == 'Off': return 'No recovery (fixed $50)'
    return '%s %s' % (c[0], 'no ladder' if c[0] == 'Crooks E' else ('ladder Off' if c[1] == 'Off' else c[1]))


def header(ws, r, first_label='Month', cnt_labels=('Trades', 'Wins', 'Losses'), fullnames=False):
    for j, t in enumerate((first_label,) + tuple(cnt_labels)):
        c = ws.cell(r, 1 + j, t); c.font = f_hdr; c.fill = BX.fill_hdr; c.alignment = BX.center
        ws.cell(r + 1, 1 + j).fill = BX.fill_hdr
        ws.merge_cells(start_row=r, start_column=1 + j, end_row=r + 1, end_column=1 + j)
    j = 0
    for k, rule in enumerate(BX.RULES):
        n = 1 if rule in ('Off', 'Crooks E') else len(LEVELS); fl = BX.fill_hdr if k % 2 == 0 else BX.fill_hdr2
        top = 'No recovery' if rule == 'Off' else rule + (' (no ladder)' if rule == 'Crooks E' else ' - profit ladder level')
        c = ws.cell(r, C0 + j, top); c.font = f_hdr; c.fill = fl; c.alignment = BX.center
        for t in range(n):
            ws.cell(r, C0 + j + t).fill = fl
            lab = 'Fixed $50' if rule == 'Off' else ('Off' if rule == 'Crooks E' else LEVELS[t])
            c2 = ws.cell(r + 1, C0 + j + t, lab); c2.font = f_hdr; c2.fill = fl; c2.alignment = BX.center
        if n > 1: ws.merge_cells(start_row=r, start_column=C0 + j, end_row=r, end_column=C0 + j + n - 1)
        j += n
    if fullnames:
        for j, cfg in enumerate(CONFIGS):
            c = ws.cell(r + 2, C0 + j, cfgname(cfg)); c.font = BX.f_small; c.alignment = BX.center
    ws.row_dimensions[r].height = 27


BX.header = header; BX.cfgname = cfgname
SETUPS = {'off': dict(file='Gold_Monthly_YourSettings_1_AllFiltersOff.xlsx', short='all filters off',
                      title='your Auction Retest settings with ALL FILTERS OFF (no day, hour, kill-zone or news filter)'),
          'on': dict(file='Gold_Monthly_YourSettings_2_YourFilters.xlsx', short='your filters',
                     title='your Auction Retest settings WITH YOUR FILTERS (Tue-Thu, 06:00-23:00, kill zones Asia + London + New York, news 17:45-18:15)')}
RUNKEYS = [('M5', 1), ('M5', 2), ('M15', 1), ('M15', 2)]


def sheetname(tf, ex): return '%s TP%d' % (tf, ex)
def wiped(w):
    for m in MS:
        if w['cont'][m]['end'] < 100.0: return m
    return None


def fix_borders(ws, r_last):
    for rr in range(5, r_last):
        for col in range(C0, CL + 1):
            ws.cell(rr, col).border = BX.bleft if col in GROUP_START else Border()


def year_netR(trs):
    y = collections.defaultdict(float)
    for x in trs: y[x['t'].year] += (x['R'] - x['c']) / (1 + x['c'])
    return y


def build(setup):
    info = SETUPS[setup]
    wb = Workbook(); rd = wb.active; rd.title = 'Read me'
    sm = wb.create_sheet('Summary'); sm.sheet_properties.tabColor = '1F3864'
    poss = {}
    for tf, ex in RUNKEYS:
        R = RUNS[(tf, setup, ex)]; res = R['res']
        data = {cfg: dict(cont=res[cfg]['cont'], fresh=res[cfg]['fresh']) for cfg in CONFIGS}
        title = 'Auction Retest, %s - gold %s, final exit TP%d (%.1fR) - IST calendar months, Jan 2021 - 2 Oct 2026' % (info['title'], tf, ex, 0.6 if ex == 1 else 1.0)
        settings = ('Base $50, $10,000 start, 1:100, no hard cap, costs 0.23 per oz (spread 0.16 + $7 per lot), earn-back targets, force-close 23:55, close at '
                    'Saturday start; %d trades, %d wins (%.1f%%), %+.1fR at a fixed risk.' % (R['n'], R['wins'], 100.0 * R['wins'] / R['n'], R['netR']))
        nd = sum(1 for cfg in CONFIGS if cfg[1] != 'Off' for m in MS if abs(res[cfg]['fresh'][m]['net'] - res[(cfg[0], 'Off')]['fresh'][m]['net']) > 1e-6)
        fn = ('The ladder needs $1,000 profit inside one month to switch on: %s, so here the Low - Max columns are %s Off.' % (
            'that never happened' if nd == 0 else 'that happened in %d rule-months' % nd, 'the same as' if nd == 0 else 'almost the same as'))
        ws, pos = BX.monthly_sheet(wb, sheetname(tf, ex), title, settings, 10000.0, MS, R['counts'], data, fresh_note=fn)
        poss[(tf, ex)] = pos
        # grey = the account is wiped out (balance under $100 at the month end): later months show tiny numbers
        for j, cfg in enumerate(CONFIGS):
            for i, m in enumerate(MS):
                if res[cfg]['cont'][m]['end'] < 100.0:
                    ws.cell(pos['FIRST'] + i, C0 + j).fill = fill_dead
        ws['H3'] = 'Account wiped out'; ws['H3'].fill = fill_dead; ws['H3'].font = f_norm; ws['H3'].alignment = BX.center
        ws['G3'] = None
        ws['I3'] = ('Shading in block 1: green = the profit ladder was on; orange = 0.01-lot start-guard trades; grey = the balance is under $100 at the month end '
                    '(the account is wiped out; the 1:100 leverage limit shrinks the trades, so it never quite reaches $0).')
        ws['I3'].font = f_note
        fix_borders(ws, ws.max_row + 1)
    # ---- summary
    sm['A1'] = 'Summary: Auction Retest, %s - gold M5 then M15, final exit TP1 and TP2, every rule x ladder level' % info['title']; sm['A1'].font = BX.f_title
    sm['A2'] = ('Green numbers are links to the four sheets (formulas); black ones are from the simulation. One account from January 2021 (the strategy left '
                'running). Colour scale per row: green = best of the row, red = worst. Columns AL / AM: the best setting of the row (formulas).'); sm['A2'].font = f_note
    sm.column_dimensions['A'].width = 12; sm.column_dimensions['B'].width = 26; sm.column_dimensions['C'].width = 8; sm.column_dimensions['D'].width = 2
    for col in range(C0, CL + 1): sm.column_dimensions[L(col)].width = 11.5
    sm.column_dimensions[L(CL + 2)].width = 26; sm.column_dimensions[L(CL + 3)].width = 12
    rows = [(sheetname(tf, ex), 'Final exit TP%d (%.1fR)' % (ex, 0.6 if ex == 1 else 1.0), RUNS[(tf, setup, ex)]['n'], sheetname(tf, ex), poss[(tf, ex)], (tf, ex))
            for tf, ex in RUNKEYS]
    get = lambda f: (lambda k, cfg: f(RUNS[(k[0], setup, k[1])]['res'][cfg]))
    blocks = [
        ('Total profit 2021 - 2026 ($), one account', 'm.SUM', USD, 'high', 'max'),
        ('Months in profit (of 70)', 'm.PROF', CNT, 'high', 'max'),
        ('Months in loss (of 70)', 'm.LOSS', CNT, 'low', 'min'),
        ('Worst month ($)', 'm.MIN', USD, 'high', 'max'),
        ('Best month ($)', 'm.MAX', USD, 'high', None),
        ('Balance on 2 Oct 2026 ($)', 'BAL_END', USD, 'high', None),
        ('Deepest drop inside one month ($)', 'DROP_MAX', USD, 'low', None),
        ('Deepest fall from a peak, whole period (% of that peak)', get(lambda w: round(w['whole']['maxDDpct'], 4)), '0.0%', 'low', None),
        ('Account wiped out from (first month ending under $100; - = never)', get(lambda w: BX.mtxt(wiped(w)) if wiped(w) else '-'), '@', None, None),
        ('Profit ladder switched on in (first month with the ladder on; - = never)', get(lambda w: BX.mtxt(w['whole']['ladFirst']) if w['whole']['ladFirst'] else '-'), '@', None, None),
        ('Each month on its own: total of the 70 months ($)', 'f.SUM', USD, 'high', 'max'),
        ('Each month on its own: months in profit (of 70)', 'f.PROF', CNT, 'high', 'max'),
        ('Each month on its own: months in loss (of 70)', 'f.LOSS', CNT, 'low', 'min'),
        ('Each month on its own: worst month ($)', 'f.MIN', USD, 'high', 'max'),
    ]
    r = 4
    for title, kind, fmt, scale, best in blocks:
        r_end, r0 = BX.summary_block(sm, r, title, rows, kind, fmt, scale=scale)
        if best:
            names = r0 - 1
            c = sm.cell(r0 - 3, CL + 2, 'Best setting (%s of the row)' % ('highest' if best == 'max' else 'lowest')); c.font = f_hdr; c.fill = BX.fill_hdr; c.alignment = BX.center
            c = sm.cell(r0 - 3, CL + 3, 'Value'); c.font = f_hdr; c.fill = BX.fill_hdr; c.alignment = BX.center
            for i in range(len(rows)):
                rr = r0 + i; rng = '$%s%d:$%s%d' % (L(C0), rr, L(CL), rr); nrng = '$%s$%d:$%s$%d' % (L(C0), names, L(CL), names); fnm = 'MAX' if best == 'max' else 'MIN'
                sm.cell(rr, CL + 2, '=INDEX(%s,MATCH(%s(%s),%s,0))' % (nrng, fnm, rng, rng)).font = f_norm
                c = sm.cell(rr, CL + 3, '=%s(%s)' % (fnm, rng)); c.font = f_norm; c.number_format = fmt
        r = r_end
    sm.freeze_panes = 'E1'
    # base-strategy table (fixed risk) on the summary, under the blocks
    r += 1
    sm.cell(r, 1, 'The strategy itself at a fixed $50 risk (no recovery): trades, win rate, net R after costs, and the same with other costs').font = BX.f_block; r += 1
    hd = ['Sheet', 'Final exit', 'Trades', None, 'Win %', 'Net R (0.23 per oz)', 'Net R, spread only (0.16)', 'Net R, no costs', 'Avg cost per trade (R)', 'Stop', 'Target', 'Force-close', 'News', '2021', '2022', '2023', '2024', '2025', '2026']
    for j, t in enumerate(hd):
        if t is None: continue                       # column D is the narrow spacer of the blocks above
        c = sm.cell(r, 1 + j, t); c.font = f_hdr; c.fill = BX.fill_hdr; c.alignment = BX.center
    sm.row_dimensions[r].height = 40; r += 1
    for tf, ex in RUNKEYS:
        R = RUNS[(tf, setup, ex)]; trs = T[(tf, setup, ex)]['trades']; yr = year_netR(trs); h = R['hows']
        vals = [sheetname(tf, ex), 'TP%d' % ex, R['n'], None, R['wins'] / R['n'], R['netR'], COSTS[(tf, setup, ex, 0.16)]['netR'], COSTS[(tf, setup, ex, 0.0)]['netR'],
                sum(x['c'] for x in trs) / len(trs), h.get('stop', 0), h.get('target', 0), h.get('force close', 0), h.get('news', 0)] + [yr.get(y, 0.0) for y in range(2021, 2027)]
        fm = ['@', '@', CNT, '@', '0.0%', '0.0', '0.0', '0.0', '0.000', CNT, CNT, CNT, CNT] + ['0.0'] * 6
        for j, (v, f) in enumerate(zip(vals, fm)):
            if v is None: continue
            c = sm.cell(r, 1 + j, v); c.font = f_norm; c.number_format = f
        r += 1
    sm.cell(r, 1, 'Net R = the sum over all trades of the result in R after costs, at the same $ risk per trade (multiply by $50 for dollars). '
                  'The year columns are the 0.23 per oz results by entry year.').font = f_note
    wb._sheets = [wb[n] for n in ['Read me', 'Summary'] + [sheetname(tf, ex) for tf, ex in RUNKEYS]]
    BX.readme(rd, readme_rows(setup))
    BX.levels_table(rd, rd.max_row + 2)
    fn = OUT + '/' + info['file']; wb.save(fn); print('saved', fn)


def readme_rows(setup):
    info = SETUPS[setup]; other = 'on' if setup == 'off' else 'off'
    def w(k, cfg): return RUNS[(k[0], setup, k[1])]['res'][cfg]
    def fresh_stats(k, cfg):
        fr = w(k, cfg)['fresh']; v = [fr[m]['net'] for m in MS]
        return sum(v), sum(1 for x in v if x > 0), sum(1 for x in v if x < 0), min(v)
    surv = []
    for k in RUNKEYS:
        for cfg in CONFIGS:
            ww = w(k, cfg)
            if wiped(ww) is None: surv.append((ww['whole']['net'], k, cfg))
    surv.sort(reverse=True)
    nwiped = sum(1 for k in RUNKEYS for cfg in CONFIGS if wiped(w(k, cfg)) is not None)
    ladon = sum(1 for k in RUNKEYS for cfg in CONFIGS if w(k, cfg)['whole']['ladFirst'])
    bestfresh = max(((fresh_stats(k, cfg), k, cfg) for k in RUNKEYS for cfg in CONFIGS), key=lambda z: z[0][0])
    mostpos = max(((fresh_stats(k, cfg), k, cfg) for k in RUNKEYS for cfg in CONFIGS), key=lambda z: (z[0][1], z[0][0]))
    base = ['%s TP%d %+.0fR (no costs %+.0fR)' % (k[0], k[1], RUNS[(k[0], setup, k[1])]['netR'], COSTS[(k[0], setup, k[1], 0.0)]['netR']) for k in RUNKEYS]
    oth = ['%s TP%d %+.0fR' % (k[0], k[1], RUNS[(k[0], other, k[1])]['netR']) for k in RUNKEYS]
    trs = T[('M5', setup, 1)]['trades']; avgc = sum(x['c'] for x in trs) / len(trs)
    yr = year_netR(trs)
    rows = [
        ('#title', 'Gold month by month: %s - final exit TP1 and TP2, Crooks E - J and the profit-ladder levels' % (info['title'][0].upper() + info['title'][1:])),
        ('What', 'Your Auction Retest strategy settings on gold, first on M5 then on M15, once with the final exit at TP1 (0.6R) and once at TP2 (1.0R): every '
                 'month from January 2021 to 2 October 2026 (the end of the gold data) with No recovery (fixed $50), Crooks E and Crooks F - J at every '
                 'profit-ladder level (Off, Low, Medium, High, Extra high, Max). This file: %s. The other file has %s.' % (
                     info['short'], 'your filters' if setup == 'off' else 'all filters off')),
        ('Sheets', 'Summary: the key numbers of every rule / level for the 4 sheets, the best setting of each row, and the strategy at a fixed $50 with other costs.\n'
                   'M5 TP1, M5 TP2, M15 TP1, M15 TP2: block 1 profit or loss of each month, block 2 each year, block 3 the balance at each month end, block 4 '
                   'the deepest drop inside each month, block 5 each month on its own.'),
        ('Your settings', 'The strategy\'s current defaults, which are your TradingView settings (checked 160 of 160 against your screenshots): ATR stop 1.8 '
                          '(half stop on, never wider), entry Model, 10 fills a day, VWAP session, TP1 0.6 / TP2 1.0, spread 0.16 + commission $7 per lot with '
                          'earn-back targets, force-close 23:55, close when Saturday starts, $50 base risk.', 'blue'),
        ('This file\'s filters', ('All OFF: no day filter, no trading hours, no kill zones, no news window. The force-close at 23:55 and the close at the start of '
                                  'Saturday stay on (they manage open trades; they are not entry filters).') if setup == 'off' else
                                 ('ON: trade only Tuesday, Wednesday and Thursday; new setups only between 06:00 and 23:00 (IST); only inside the kill zones Asia '
                                  '05:30-09:30, London 11:30-14:30, New York 16:30-19:30 (London Close off; they follow London / New York summer time); daily news '
                                  'window 17:45-18:15 IST (it keeps its New York time: 18:45-19:15 IST while New York is on winter time) with no new trades from '
                                  '60 minutes before it until it ends, an open trade closed and a waiting entry cancelled when it starts. Force-close 23:55 and the '
                                  'Saturday close as in your settings.'), 'blue'),
        ('How the trades were made', 'The strategy\'s engine (the Python twin of the indicator / EA engine) gives every setup; a model of TradingView\'s strategy '
                                     'tester then executes the strategy\'s own order rules on each candle: the limit entry from the next candle (filled on touch, at '
                                     'the open on a gap), the stop at once and the earn-back target after the engine\'s fill, one trade at a time, close at the next '
                                     'open at the force-close time / Saturday start / news start, entries cancelled in the news block. TradingView\'s candle path: '
                                     'open, then the nearer of high / low, then the other, then close.'),
        ('Months', 'IST calendar months. Blocks 1 - 4: a trade counts in the month it closed. Block 5: a trade belongs to the month it started in.'),
        ('Two ways to read a month', 'ONE ACCOUNT (blocks 1 - 4, and the Summary): one account from January 2021, the recovery state and the ladder carry over, as '
                                     'when the strategy or EA is left running.\nEACH MONTH ON ITS OWN (block 5): a fresh $10,000 and a fresh recovery state every 1st.'),
        ('Money settings', 'Fixed $ risk, base $50; $10,000 start; 1:100 leverage limit; no hard cap (your setting); costs 0.23 per oz per trade (TradingView '
                           'commission 0.115 per contract per order = spread 0.16 + $7 per lot); Crooks E / I lot 0.01 = 1 oz; Crooks F x3, G x10, H 1 %, J x20; '
                           'ladder target $1,000; the recovery trade aims at TP1 = 0.6R (or TP2 = 1.0R). Sizes are not rounded to the 0.01-lot step.', 'blue'),
        ('The rules', 'No recovery: every trade risks $50.\nCrooks E: after a loss wait for a win, then the next trade wins the whole loss back; while the loss '
                      'waits every trade is 0.01 lot.\nCrooks F: a recovery trade risks at most 3 x the base ($150).\nCrooks G: the loss to win back is at most '
                      '10 x the base ($500).\nCrooks H: a recovery trade risks at most 1 % of the balance.\nCrooks I: Crooks E + Crooks F.\nCrooks J: a recovery '
                      'trade shrinks as the account falls from its peak.'),
        ('The profit ladder', 'Crooks F - J only. It switches on after the best closed profit reaches $1,000, then raises the base out of the profit above the '
                              'lock; back at $0 or below every trade is 0.01 lot (the start guard). The table at the bottom has each level\'s numbers.'),
        ('Shading', 'Block 1: green = ladder on, orange = 0.01-lot guard trades, grey = the account is wiped out (balance under $100 at the month end).'),
        ('#h', 'Findings'),
        ('1. The strategy itself loses', 'At a fixed $50 risk (no recovery) all four sheets lose after costs: %s. The trades win %.0f - %.0f %% of the time, but '
                                         'a TP1 win nets about +0.57R while a stop loses -1R.' % (
                                             '; '.join(base), 100 * min(RUNS[(k[0], setup, k[1])]['wins'] / RUNS[(k[0], setup, k[1])]['n'] for k in RUNKEYS),
                                             100 * max(RUNS[(k[0], setup, k[1])]['wins'] / RUNS[(k[0], setup, k[1])]['n'] for k in RUNKEYS))),
        ('2. Costs decide it', 'The M5 stops are small, so the 0.23 per oz cost is on average %.2fR per trade on M5 TP1 (the earn-back target is that much further '
                               'away, and a stop-out loses it too). Without costs the same trades are %s; with the spread only %s (Summary, bottom table).' % (
                                   avgc, ', '.join('%s TP%d %+.0fR' % (k[0], k[1], COSTS[(k[0], setup, k[1], 0.0)]['netR']) for k in RUNKEYS),
                                   ', '.join('%s TP%d %+.0fR' % (k[0], k[1], COSTS[(k[0], setup, k[1], 0.16)]['netR']) for k in RUNKEYS))
                               + (' Even without any costs these trades lose.' if all(COSTS[(k[0], setup, k[1], 0.0)]['netR'] < 0 for k in RUNKEYS) else
                                  ' Before costs the M5 runs are positive; the costs turn them negative.' if all(COSTS[('M5', setup, e, 0.0)]['netR'] > 0 for e in (1, 2)) else '')),
        ('3. By year', 'M5 TP1 at a fixed risk, net R by entry year: %s. %s' % (
            ', '.join('%d %+.0f' % (y, yr[y]) for y in sorted(yr)),
            'Every year loses, the recent ones less.' if all(v < 0 for v in yr.values()) else
            'The last two years are positive; 2021 - 2024 lose.' if yr.get(2025, 0) > 0 and yr.get(2026, 0) > 0 else 'Mixed years.')),
        ('4. Recovery on a losing strategy', 'With one account from January 2021, %d of the %d rule / level / sheet combinations end wiped out (grey). The recovery '
                                             'rules raise the risk after losses, which deepens the fall when the strategy itself loses. %s' % (
                                                 nwiped, len(RUNKEYS) * len(CONFIGS),
                                                 ('Still standing at the end: ' + '; '.join('%s TP%d %s %s' % (k[0], k[1], cfgname(cfg), BX.usd(v)) for v, k, cfg in surv[:6]) + '.')
                                                 if surv else 'None survives.')),
        ('5. The ladder', ('It needs the account to reach +$1,000 first: that never happened here, so the Low - Max columns are the same as Off in every '
                           'sheet.') if ladon == 0 else
                          ('It needs the account to reach +$1,000 first: that happened in %d of the %d combinations, so the Low - Max columns are mostly the same '
                           'as Off. Where it did switch on, its start guard (0.01 lot once the profit is back at $0) kept the account from being wiped out.' % (
                               ladon, len(RUNKEYS) * 25))),
        ('6. Each month on its own', 'Block 5 shows how a fresh account does inside one month. Most months in profit: %s %s (%d of 70 months, total %s, worst month '
                                     '%s). Best total: %s %s (%s, %d months in profit). Recovery rules win many small months and lose a few big ones.' % (
                                         '%s TP%d' % mostpos[1], cfgname(mostpos[2]), mostpos[0][1], BX.usd(mostpos[0][0]), BX.usd(mostpos[0][3]),
                                         '%s TP%d' % bestfresh[1], cfgname(bestfresh[2]), BX.usd(bestfresh[0][0]), bestfresh[0][1])),
        ('7. The other file', '%s, at a fixed risk: %s.' % ('With your filters (the other file)' if setup == 'off' else 'With all filters off (the other file)', '; '.join(oth))),
        ('#h', 'How it was computed and checked'),
        ('Engine', 'The engine with event recording (mcej2/ref_gse.py) gives exactly the same trades as the research engine in all 8 runs.'),
        ('Strategy model', 'With earn-back and the time closes off, the modelled strategy takes the same trades as the engine in all 8 runs (100 % same entry and '
                           'exit candles; 0.1 - 0.3 % differ in win / loss where one candle touches both stop and target, TradingView\'s candle path decides). '
                           'Against the EA\'s own code on the MT5 broker simulator (M5, your filters, TP1): 96.9 % of the EA\'s trades matched, 98.3 % of those '
                           'with the same exit candle, 99.2 % the same win / loss (TP2: 96.3 %, 99.1 %, 99.5 %). The simulator books +216R at TP1 only because it '
                           'charges no commission and its 4 ticks a minute fill entries and targets past their prices; priced at the EA\'s own order '
                           'levels (they include the real spread) with the $7 per lot commission the same trades make -264R at TP1 and -209R at TP2, '
                           'against -185R and -138R in this model.'),
        ('Money', 'gold/recovery.py, proven equal to the EA (parity suites, 0 differences) and to the TradingView strategy\'s money code. Workbook cells checked '
                  'against the simulation; an independent re-implementation recomputed sample months (see the final report).'),
        ('Caveats', 'One price history (FxPro gold); TradingView\'s OANDA data differs a little. No lot rounding (the strategy rounds down to 0.01 lot), no swaps. '
                    'Past results do not guarantee future ones.'),
        ('#h', 'Profit-ladder levels (the strategy\'s built-in numbers)'),
    ]
    return rows


if __name__ == '__main__':
    import os
    os.makedirs(OUT, exist_ok=True)
    for setup in ('off', 'on'): build(setup)
