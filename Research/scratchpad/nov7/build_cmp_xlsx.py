"""TradingView (OANDA) vs EA (FxPro MT5) trades, 6 Oct - 6 Nov 2026: settings to change + trade by trade with the cause of each difference.
Usage: python3 -I build_cmp_xlsx.py TV.csv REPORT.xlsx OUT.xlsx"""
import sys, datetime as dt
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/tools/csvcheck')
from load import load
from cmp_ea_tv import ea_positions
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

tvp, rp, out = sys.argv[1], sys.argv[2], sys.argv[3]
EU_END = dt.datetime(2026, 10, 25, 4, 0)            # FxPro server time when EU summer time ends (01:00 UTC)
def srv_to_ist(t): return t - dt.timedelta(hours=3 if t < EU_END else 2) + dt.timedelta(hours=5, minutes=30)
tv = load(tvp)
ea, _ = ea_positions(rp)
for e in ea: e['ist'] = srv_to_ist(e['t'])
# match: same direction, EA fill within -1..+10 minutes of the TradingView fill, entry within $3 (as cmp_ea_tv.py)
used, pair = set(), {}
for t in tv:
    t0 = dt.datetime.strptime(t['entry_time'], '%Y-%m-%d %H:%M'); best = None
    for j, e in enumerate(ea):
        if j in used or e['dir'] != t['dir']: continue
        lag = (e['ist'] - t0).total_seconds() / 60.0
        if -1 <= lag < 10 and abs(e['px'] - t['entry_px']) < 3.0 and (best is None or abs(lag) < abs(best[1])): best = (j, lag)
    if best: used.add(best[0]); pair[t['n']] = best[0]

SET, LIKELY, NO = 'Yes', 'Likely', 'No'
TV_ONLY = {
    15: ('Daily news window', SET, "The EA's news window is 17:55 for 75 minutes, so it blocks new trades until 19:10. TradingView's is 17:45-18:15, so 18:50 is allowed."),
    17: ('Bid-chart matching', LIKELY, "The EA had the same buy order (4150.66, placed 08:25) but it expired unfilled at 08:50. With 'Match bid-chart levels' OFF, the EA's buy orders wait for the ASK price, so price has to fall one more spread (about $0.16). TradingView filled on the last allowed candle."),
    18: ('Knock-on', NO, "Follows from #17. After a trade the engine re-anchors the breakout ('Re-anchor breakout after a trade'). TradingView had #17, the EA did not, so only TradingView got this short."),
    21: ('Price data', NO, "On FxPro candles the EA had no long signal at 07:40. This starts a chain of differences on 20 Oct (#21 to #24)."),
    22: ('Bid-chart matching + price data', LIKELY, "Same setup in the EA (buy limit 4140.26 at 08:35), but it expired unfilled. TradingView's price dipped only $0.11 below its entry, so a buy order waiting for the ask could not fill. FxPro's candles also gave a tight half stop (3.81) where TradingView used the normal stop (7.76)."),
    23: ('Knock-on', NO, "Follows from #21 and #22: the two engines were in different states for the rest of 20 Oct."),
    24: ('Knock-on', NO, "TradingView was still in #23 until 13:00, so its short came at 13:15. The EA was flat and took a short at 13:05 instead (EA-only row)."),
    26: ('Price data', NO, "On FxPro candles this short came 15 minutes later (11:55 at 4114.07) and lost (EA-only row)."),
    33: ('Max fills per day', SET, "The EA had already filled 5 trades on 22 Oct and its limit is 5. TradingView's limit is 10, and this was its 6th fill."),
    35: ('Server clock + max fills', SET, "From 25 Oct to 1 Nov the EA's clock is 1 hour behind (its server-clock setting uses the US rule; FxPro uses the EU rule). The EA thought it was 18:15, inside its news window. It had also used its 5 fills that day."),
    37: ('Clock-change week', NO, "From 25 Oct to 1 Nov, FxPro's day (and the EA's VWAP) starts at 18:00 New York time instead of 17:00, so the VWAP and the signals differ all week. The EA took a long at 13:51 instead."),
    38: ('Server clock', SET, "The EA's clock said 05:05 (1 hour behind that week): before the 06:00 start and before the Asia kill zone."),
    39: ('Knock-on', NO, "Follows from #38 (re-anchor after a trade) in the clock-change week."),
    49: ('Price data', NO, "On FxPro candles the EA had no long at 07:40. It then took a long at 08:40, which TradingView could not take because it was still in #49."),
    50: ('Daily news window', SET, "New York winter time: TradingView blocks 17:45-19:15 and the EA blocks 17:55-20:10, so 19:30 is allowed only in TradingView."),
    51: ('Daily news window', SET, "Same as #50: 20:05 is inside the EA's window."),
    52: ('Price data', NO, "The EA was allowed to trade at 20:15, but on FxPro candles it had no short signal there."),
}
EA_ONLY = {
    '10-06 16:54': ('Daily news window', SET, "Signal candle 16:45. TradingView stops new trades from 16:45 (60 minutes before 17:45); the EA only from 16:55 (60 minutes before 17:55)."),
    '10-14 07:10': ('Price data', NO, "On OANDA candles TradingView had no short here."),
    '10-15 20:12': ('London Close kill zone', SET, "20:10 is in the London Close zone (19:30-21:30), which is ON in the EA and OFF in TradingView."),
    '10-20 13:05': ('Knock-on', NO, "TradingView was in #23 (a long) until 13:00, so it could not take this short (see #24)."),
    '10-20 13:28': ('Knock-on', NO, "Follows from the 13:05 short. In the EA this was a 0.18-lot Crooks C recovery trade."),
    '10-21 11:55': ('Price data', NO, "TradingView took this short 15 minutes earlier (#26 at 11:40) and won. On FxPro candles it came at 11:55 and lost."),
    '10-27 08:35': ('Clock-change week', NO, "FxPro's day and VWAP start 1 hour later than OANDA's this week. TradingView had no signal."),
    '10-27 09:19': ('Clock-change week', NO, "Same as above."),
    '10-27 09:54': ('Server clock', SET, "The real time was 09:50, after the Asia zone ends (09:30), but the EA's clock said 08:50."),
    '10-27 17:41': ('Server clock', SET, "The real time was 17:35, inside the news block, but the EA's clock said 16:35. With the right clock, even the EA's own window would block it."),
    '10-28 07:31': ('Clock-change week', NO, "A second short after #36. On OANDA candles there was no second signal."),
    '10-28 13:51': ('Clock-change week', NO, "Different VWAP this week. TradingView took a long at 14:25 instead (#37)."),
    '11-04 11:54': ('Kill zones follow summer time', SET, "UK winter time: TradingView moves its London zone to 12:30-15:30, while the EA keeps 11:30-14:30."),
    '11-04 21:47': ('London Close kill zone', SET, "Signal at 21:20, inside London Close (19:30-21:30), which is ON in the EA and OFF in TradingView."),
    '11-05 08:40': ('Knock-on', NO, "TradingView was still in #49 (07:40-09:25), so it could not take this long."),
}
SAME_NOTE = {25: ('Bid-chart matching', LIKELY, "Same entry, different result. TradingView's target was only just touched. With 'Match bid-chart levels' OFF, the EA's short target is a buy order that waits for the ASK, so it needed one more spread. Price then turned and hit the EA's stop.")}
CROOKS = {20, 29, 40, 46, 47}

rows = []   # (sort time, cells...)
for t in tv:
    t0 = dt.datetime.strptime(t['entry_time'], '%Y-%m-%d %H:%M')
    d = 'Long' if t['dir'] > 0 else 'Short'
    if t['n'] in pair:
        e = ea[pair[t['n']]]; ln = round(e['lots'] * 100); q = round(t['qty'])
        if t['n'] in SAME_NOTE: st = 'Same trade, different result'; cause, fix, why = SAME_NOTE[t['n']]
        elif t['n'] in CROOKS: st = 'Same trade'; cause, fix, why = 'Crooks C sizing', NO, 'Different earlier wins and losses, so Crooks C made the recovery trade at a different point.'
        elif ln == q + 1: st = 'Same trade'; cause, fix, why = 'Lot rounding', SET, 'The EA is 0.01 lot bigger because it rounds to the nearest lot step; TradingView rounds down.'
        elif ln == q: st = 'Same trade'; cause, fix, why = '', '', ''
        else: st = 'Same trade'; cause, fix, why = 'Size', '', 'Size differs.'
        rows.append((t0, [t0, d, st, t['n'], t['entry_px'], t['qty'], t['pnl'], e['ist'].replace(second=0), e['px'], e['lots'], round(e['net'], 2), cause, fix, why]))
    else:
        cause, fix, why = TV_ONLY[t['n']]
        rows.append((t0, [t0, d, 'TradingView only', t['n'], t['entry_px'], t['qty'], t['pnl'], None, None, None, None, cause, fix, why]))
for j, e in enumerate(ea):
    if j in used: continue
    k = e['ist'].strftime('%m-%d %H:%M'); cause, fix, why = EA_ONLY[k]
    rows.append((e['ist'], [e['ist'].replace(second=0), 'Long' if e['dir'] > 0 else 'Short', 'EA only', None, None, None, None, e['ist'].replace(second=0), e['px'], e['lots'], round(e['net'], 2), cause, fix, why]))
rows.sort(key=lambda r: r[0])

F = 'Arial'; fn = Font(name=F, size=10); fb = Font(name=F, size=10, bold=True); fh = Font(name=F, size=10, bold=True, color='FFFFFF')
fill_h = PatternFill('solid', fgColor='1F3864'); wrap = Alignment(wrap_text=True, vertical='top'); hw = Alignment(wrap_text=True, vertical='center', horizontal='center')
FILL = {'Same trade': PatternFill('solid', fgColor='E2EFDA'), 'Same trade, different result': PatternFill('solid', fgColor='FFF2CC'),
        'TradingView only': PatternFill('solid', fgColor='DDEBF7'), 'EA only': PatternFill('solid', fgColor='FCE4D6')}
USD = '$#,##0.00;[Red]-$#,##0.00'
wb = Workbook()

# ---- Read me
ws = wb.active; ws.title = 'Read me'; ws.column_dimensions['A'].width = 130
ws['A1'] = 'TradingView (OANDA) vs EA (FxPro MT5), gold M5, 6 Oct - 6 Nov 2026'; ws['A1'].font = Font(name=F, size=14, bold=True)
n_same = sum(1 for r in rows if r[1][2].startswith('Same')); n_tv = sum(1 for r in rows if r[1][2] == 'TradingView only'); n_ea = sum(1 for r in rows if r[1][2] == 'EA only')
fix_yes = sum(1 for r in rows if r[1][2] != 'Same trade' and r[1][12] == SET); fix_lk = sum(1 for r in rows if r[1][2] != 'Same trade' and r[1][12] == LIKELY)
txt = [
    'Answer: the two files are NOT taking the same trades. %d of TradingView\'s %d trades are the same trade in the EA (same direction, same candle, same price within $3). '
    'TradingView has %d trades the EA does not; the EA has %d trades TradingView does not.' % (n_same, len(tv), n_tv, n_ea),
    'Why: 9 settings differ between the two files (sheet "Settings"). They directly caused %d of the differences, and probably %d more. '
    'Most of the rest follow from those: one different trade changes the next signals (re-anchor after a trade, cooldown, max fills) '
    'and moves the Crooks C recovery trades.' % (fix_yes, fix_lk),
    'What no setting can fix: (1) different price data. OANDA and FxPro candles differ by a few cents, and their volumes (which weight the VWAP) are completely different. '
    '(2) The clock-change weeks. From 25 Oct to 1 Nov, FxPro\'s day starts at 18:00 New York time instead of 17:00, so the EA\'s VWAP starts 1 hour later than TradingView\'s. '
    'This happens every year between the European and the US clock changes (about 1 week in autumn and 2 weeks in March).',
    'Times are India time. EA times are converted from FxPro server time (UTC+3 until 25 Oct, then UTC+2). Sizes: TradingView in oz (8 = 0.08 lot), EA in lots.',
    'Checked from the files: FxPro charged $3.50 per lot per side ($7 round trip). TradingView charged $0.07 per oz per trade (also $7 per lot). '
    'FxPro\'s gold spread in this test was 0.15-0.20 (median 0.16), worked out from the EA\'s target prices.',
    'TradingView\'s loss recovery is Crooks C, confirmed by replaying its trade sizes: the recovery trades fall exactly where Crooks C puts them.',
]
for i, p in enumerate(txt):
    c = ws.cell(3 + i, 1, p); c.font = fn; c.alignment = wrap

# ---- Settings
ws = wb.create_sheet('Settings')
hdr = ['#', 'Setting', 'TradingView (screenshots)', 'EA now (report)', 'Change to match', 'Trades it changed this month', 'Why it matters']
S_ROWS = [
    (1, 'Daily news window', '17:45 - 18:15 (30 min), 60 min before, follows New York time',
     'InpDNewsH = 17, InpDNewsM = 55, InpDNewsDur = 75 (17:55 - 19:10)', 'EA: InpDNewsM = 45, InpDNewsDur = 30',
     'TV #15, #50, #51 missing in the EA; EA-only 6 Oct 16:54',
     'With 60 minutes before, TradingView blocks new trades 16:45-18:15 and the EA blocks 16:55-19:10 (New York winter time: both 1 hour later).'),
    (2, 'Broker server clock (EA only)', '- (TradingView uses the chart time zone)', 'InpServerTz = 0 (Auto: US summer time)',
     'EA: InpServerTz = 2 (Auto: EU summer time, EET brokers e.g. FxPro)', 'TV #35, #38 missing in the EA; EA-only 27 Oct 09:54 and 17:41',
     "FxPro's server changes clock with Europe (25 Oct), not the US (1 Nov). Until 1 Nov, the EA's hours, kill zones, news window and force-close were 1 hour early."),
    (3, 'London Close kill zone (19:30 - 21:30)', 'OFF', 'InpKzLc = true', 'EA: InpKzLc = false',
     'EA-only 15 Oct 20:12 and 4 Nov 21:47 (and an unfilled order on 29 Oct)', 'The EA traded in a zone TradingView does not use.'),
    (4, 'Kill zones follow London / New York summer time', 'ON', 'InpKzAuto = false', 'EA: InpKzAuto = true',
     'EA-only 4 Nov 11:54 (and an unfilled order on 5 Nov 16:45)', 'After the UK (25 Oct) and US (1 Nov) clock changes, TradingView moves the London and New York zones 1 hour later. The EA did not.'),
    (5, 'Max fills per day', '10', 'InpMaxFills = 5', 'EA: InpMaxFills = 10', 'TV #33 and #35 missing in the EA',
     'The EA used up its 5 fills on 22 Oct and 27 Oct. This limit is inside the signal engine, so it also changes later signals.'),
    (6, "Match bid-chart levels (EA only)", '- (TradingView fills at the chart price, the bid)', 'InpBidChart = false', 'EA: InpBidChart = true (the default)',
     'TV #17 and #22: the EA had the same buy orders but they expired unfilled. #25: a TradingView win but an EA loss.',
     "OFF: the EA's buy orders (long entries, short stops, short targets) trigger on the ASK. Long entries then need one more spread to fill, short stops are hit one spread early, and short targets need one more spread."),
    (7, 'Lot rounding', 'Down', 'InpLotRound = 1 (to the nearest step)', 'EA: InpLotRound = 0 (Down), or set both to nearest',
     '15 of the 35 shared trades are 0.01 lot bigger in the EA', 'Bigger lots mean different $ results, and so different Crooks C recovery amounts.'),
    (8, 'Commission ($ per lot, round trip)', "0 (but Properties charges $0.07 per oz = $7 per lot)", 'InpCommLot = 0.16',
     'Both: 7. (In the EA the spread is read live, so do not enter it there.)',
     'Sizes and earn-back targets (small)', "FxPro charges $3.50 per lot per side ($7 round trip). InpCommLot is dollars per lot, so 0.16 there means 16 cents per lot, not the 0.16 spread."),
    (9, 'Half stop never wider than the normal stop', 'ON', 'InpHalfCap = false', 'EA: InpHalfCap = true', 'None seen this month',
     'Only changes the stop after a very tall signal candle, but it changes that trade and the signals after it.'),
    (10, 'TradingView Properties -> Commission', '$0.035 per oz per order ($7 per lot round trip)', '- (FxPro charges the real spread + $7 per lot)',
     "TradingView: after step 8, enter the value the strategy's table shows (0.115 per contract = $7 commission + 0.16 spread)",
     'P&L only', "TradingView fills at chart (bid) prices, so it never pays the spread unless the commission includes it. The EA pays the real spread on every trade."),
]
for j, h in enumerate(hdr, 1):
    c = ws.cell(1, j, h); c.font = fh; c.fill = fill_h; c.alignment = hw
ws.row_dimensions[1].height = 32
for i, r in enumerate(S_ROWS, 2):
    for j, v in enumerate(r, 1):
        c = ws.cell(i, j, v); c.font = fb if j == 2 else fn; c.alignment = wrap
r0 = len(S_ROWS) + 3
ws.cell(r0, 2, 'Different but not used with your settings (tidy them so both files read the same)').font = fb
TIDY = [('Split the loss (Rule C / Crooks B)', '2', 'InpCSplit = 3', 'Not used by Crooks C'),
        ('Crooks C rule: D trading days to skip', '4', 'InpCrkPrD = 3', 'The rule is Off'),
        ('Custom entry %', '25', 'InpEntryPct = 50', 'Not used with Entry = Model'),
        ("Don't chase (sigma)", '2', 'InpNoChaseSig = 2.4', 'Filter off'),
        ('Skip choppy sessions: max crosses', '13.5', 'InpChopMax = 12', 'Filter off'),
        ('When TP3 hits, move stop to (R)', '0', 'InpMv3R = 1.0', 'Off'),
        ('Crooks TP1 rule: stop before TP1', 'Normal stop', 'InpCrkT1Stop = 0 (Tight)', 'The rule is off'),
        ('Stop for the day after N losses', '23', 'InpLStopN = 2', 'Off')]
for i, r in enumerate(TIDY, r0 + 1):
    for j, v in enumerate(r, 2):
        c = ws.cell(i, j, v); c.font = fn; c.alignment = wrap
r1 = r0 + len(TIDY) + 2
ws.cell(r1, 2, 'Same in both').font = fb
c = ws.cell(r1 + 1, 2, 'All signal-model values (10 / 6 / 6 / 5, 0.8, 55, 25, 10 / 0.85, CMO 20, keep first, ATR stop 1.8, swing 6 / 0.22, half stop 0.9 / 3, impulse body 50, '
            'half stop when the session opens outside, cooldown 1, daily stop 0, re-anchor after a trade, ATR 14, VWAP filter, slope 3 across the session start, '
            'skip Sunday open), VWAP session hlc3, entry Model, targets 0.6 / 1 / 1.5 / 2, exit at TP1, no stop moves, all accuracy filters off, '
            'Tue / Wed / Thu, 06:00-23:00, Asia + London + New York kill zones, India time, no partials, base $50, hard cap off (250, start again), '
            'leverage 100, lot step auto, trade the minimum lot, earn-back on, streaks off, force-close 23:55, close at the weekend, 60 minutes before news, '
            'news window follows New York time, Crooks C with N 3 / 50% / x2 / $25 / Paroli 3 / Delayed 2 / 1%, Crooks TP1 rule off, Crooks C over N wins off, Crooks C rule Off.')
c.font = fn; c.alignment = wrap; ws.merge_cells(start_row=r1 + 1, start_column=2, end_row=r1 + 1, end_column=7); ws.row_dimensions[r1 + 1].height = 75
for col, w in zip('ABCDEFG', (4, 30, 30, 30, 34, 34, 60)): ws.column_dimensions[col].width = w
ws.freeze_panes = 'A2'

# ---- Trade by trade
ws = wb.create_sheet('Trade by trade')
hdr = ['Time (India)', 'Direction', 'Status', 'TV #', 'TV entry', 'TV size (oz)', 'TV P&L', 'EA fill (India)', 'EA entry', 'EA lots', 'EA P&L',
       'Cause', 'Fixable by a setting?', 'Explanation']
for j, h in enumerate(hdr, 1):
    c = ws.cell(1, j, h); c.font = fh; c.fill = fill_h; c.alignment = hw
ws.row_dimensions[1].height = 32
FMT = ['dd mmm hh:mm', None, None, '0', '0.00', '0', USD, 'dd mmm hh:mm', '0.00', '0.00', USD, None, None, None]
for i, (_, r) in enumerate(rows, 2):
    for j, v in enumerate(r, 1):
        c = ws.cell(i, j, v if v != '' else None); c.font = fn; c.fill = FILL[r[2]]
        if FMT[j - 1]: c.number_format = FMT[j - 1]
        if j == 14: c.alignment = wrap
last = len(rows) + 1
s = last + 2
summ = [('TradingView total', '=SUM(G2:G%d)' % last, 7), ('EA total', '=SUM(K2:K%d)' % last, 11)]
for k, (lab, f, col) in enumerate(summ):
    ws.cell(s + k, 3, lab).font = fb; c = ws.cell(s + k, col, f); c.font = fb; c.number_format = USD
cnt = [('Same trade', '=COUNTIF(C2:C%d,"Same trade*")' % last), ('Same trade, different result', '=COUNTIF(C2:C%d,"Same trade, different result")' % last),
       ('TradingView only', '=COUNTIF(C2:C%d,"TradingView only")' % last), ('EA only', '=COUNTIF(C2:C%d,"EA only")' % last),
       ('Differences fixable by a setting (Yes)', '=COUNTIFS(C2:C%d,"<>Same trade",M2:M%d,"Yes")' % (last, last)),
       ('Differences probably fixable (Likely)', '=COUNTIFS(C2:C%d,"<>Same trade",M2:M%d,"Likely")' % (last, last))]
for k, (lab, f) in enumerate(cnt):
    ws.cell(s + 3 + k, 3, lab).font = fb; c = ws.cell(s + 3 + k, 4, f); c.font = fb; c.number_format = '0'
for col, w in zip('ABCDEFGHIJKLMN', (14, 8, 24, 6, 10, 8, 11, 14, 10, 7, 11, 28, 11, 90)): ws.column_dimensions[col].width = w
ws.freeze_panes = 'D2'; ws.auto_filter.ref = 'A1:N%d' % last
wb.move_sheet('Trade by trade', offset=-1)
wb.save(out)
print('rows', len(rows), '| same', n_same, '| TV only', n_tv, '| EA only', n_ea, '| set', fix_yes, 'likely', fix_lk)
print('TV net %.2f, EA net %.2f' % (sum(t['pnl'] for t in tv), sum(e['net'] for e in ea)))
