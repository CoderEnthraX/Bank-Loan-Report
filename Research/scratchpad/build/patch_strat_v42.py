"""v4.2 strategy: monthly profit lock ("stop for the month once it is up $X"), profit lock (once the month is up $Y, lock P% of its highest
closed profit; stop for the month when it falls back there) and the monthly restart of the loss recovery (on the 1st, once no trade of the old
month is left). Calendar month in the DAYS AND HOURS time zone, closed trades incl. costs. All off by default. Every replacement must match once."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/strategy_template.pine'
s = open(B, encoding='utf8').read()
INPUTS = '''
GRP_ML = "MONTHLY PROFIT LOCK (strategy only)"
mLockOn  = input.bool(false, "Stop For The Month Once It Is Up ($)", inline = "ml", group = GRP_ML)
mLockAmt = input.float(150.0, "", minval = 0.01, step = 10.0, inline = "ml", group = GRP_ML, tooltip = "When this calendar month's closed profit (costs included; time zone of DAYS AND HOURS) reaches this amount, no new trades until the 1st of next month. A trade already open runs to its exit.\\nGold research (workbook Gold_No_Losing_Month): +$50 to +$250 worked with the right settings, +$500 was too ambitious.")
pLockOn  = input.bool(false, "Lock Profit Once The Month Is Up ($) · Lock %", inline = "pl", group = GRP_ML)
pLockAt  = input.float(500.0, "", minval = 0.01, step = 50.0, inline = "pl", group = GRP_ML)
pLockPct = input.float(20.0, "", minval = 1.0, maxval = 100.0, step = 5.0, inline = "pl", group = GRP_ML, tooltip = "When this month's closed profit reaches the amount, this % of the month's highest closed profit is locked, e.g. up $500 with 20% -> $100 locked; the locked part rises with every new high (up $800 -> $160). If the month's closed profit falls back to the locked level, no new trades until the 1st of next month. It is checked when a trade closes, so one big losing trade can still end below the locked level.")
mRestart = input.bool(false, "Restart The Loss Recovery On The 1st Of Each Month", group = GRP_ML, tooltip = "On the 1st of each month (time zone of DAYS AND HOURS) the loss recovery starts again from the base risk, like the hard cap's Start again: the loss to win back, the losing runs, the Labouchere list, Rule C's carried losses and the Crooks C rule state (incl. a skip pause) are forgotten. With a trade or entry order of the old month still open, right after it closes.\\nThe gold research tested every month this way (a fresh start on the 1st).")
'''
STATE = '''var float mNet0     = 0.0    // monthly lock: closed profit before this month
var float mPeak     = 0.0    //   this month's highest closed profit
var bool  mStop     = false  //   no new trades until next month (monthly lock or profit lock)
var bool  pLocked   = false  //   profit lock: the month reached the lock amount
var bool  mRestPend = false  //   monthly restart of the loss recovery, once no trade of the old month is left
'''
MONTH = '''
// monthly profit lock: a new calendar month in the time zone of DAYS AND HOURS (its closed trades count from this bar on)
int   mKey = year(time, tzUse) * 100 + month(time, tzUse)
bool  mNew = mKey != nz(mKey[1], mKey)
if mNew
    mNet0   := nz(strategy.netprofit[1])
    mPeak   := 0.0
    mStop   := false
    pLocked := false
    if mRestart
        mRestPend := true
'''
LOCK = '''// ── monthly restart of the loss recovery (once no trade or entry order of the old month is left) and the monthly locks ──
if mRestPend and exState == 0 and strategy.position_size == 0
    mRestPend   := false
    recPool     := 0.0
    recLosses   := 0
    dUnits      := 1
    carried     := 0.0
    labSeq      := array.from(1.0, 2.0, 3.0)
    parWins     := 0
    rdUnits     := 1
    oscU        := 1
    oscP        := 0.0
    crkL        := 0.0
    crkN        := 0
    crkW        := false
    crkP        := crkNp
    crkF        := 0
    crkWait     := false
    crkWW       := 0
    crkNeedL    := false
    crkSkip     := false
    crkSkipLeft := 0
// this month's closed profit (costs included): stop for the month at the lock amount, or when it falls back to the locked part of its high
float mPnl = strategy.netprofit - mNet0
if mLockOn and mPnl >= mLockAmt
    mStop := true
if pLockOn
    mPeak := math.max(mPeak, mPnl)
    if mPnl >= pLockAt
        pLocked := true
    if pLocked and mPnl <= pLockPct / 100.0 * mPeak
        mStop := true

'''
REPS = [
    ('//  risk with Crooks C, news window 17:45-18:15 IST, force-close 23:55, spread 0.16 + $7 commission per lot.\n',
     '//  risk with Crooks C, news window 17:45-18:15 IST, force-close 23:55, spread 0.16 + $7 commission per lot.\n'
     '//  v4.2: MONTHLY PROFIT LOCK group (stop for the month once it is up $X, lock a % of the month\'s profit,\n'
     '//  restart the loss recovery on the 1st); all off by default, the same settings as in the MT5 EA.\n'),
    (None, 'pauseDays = input.int(1, "", minval = 1, maxval = 3, inline = "ps", group = GRP_K, tooltip = "Stops trading for the rest of today plus this many full trading days, then the streak count restarts.")\n'),
    ('var int   crkSkipLeft = 0    //   counted days still to skip\n', 'var int   crkSkipLeft = 0    //   counted days still to skip\n' + STATE),
    ('        crkSkipLeft -= 1\n\nf_tgtPx(bool isL, float lvl)', '        crkSkipLeft -= 1\n' + MONTH + '\nf_tgtPx(bool isL, float lvl)'),
    ('\n// ── 3. follow the engine (only the setup the strategy took) ──', '\n' + LOCK + '// ── 3. follow the engine (only the setup the strategy took) ──'),
    ('    bool preSkip = exState != 0 or pos != 0 or newsBlock or flatNow or capStop or paused or dayBlock or crkPause\n',
     '    bool preSkip = exState != 0 or pos != 0 or newsBlock or flatNow or capStop or paused or dayBlock or crkPause or mStop\n'),
    ('crkPause ? "Crooks C pause" : q <= 0 ? "size 0" : ""', 'crkPause ? "Crooks C pause" : mStop ? "monthly lock" : q <= 0 ? "size 0" : ""'),
    ('crkPause ? "CROOKS C PAUSE (" + str.tostring(crkSkipLeft) + "d left)" : dayBlock ? "STREAK STOP TODAY"',
     'crkPause ? "CROOKS C PAUSE (" + str.tostring(crkSkipLeft) + "d left)" : mStop ? "MONTHLY LOCK (until the 1st)" : dayBlock ? "STREAK STOP TODAY"'),
    ('f_row(mon, 7, "DAY P&L · FILLS", f_usd(dayPnl) + " · " + str.tostring(dayFills) + "/" + str.tostring(maxFills), dayPnl >= 0 ? posC : negC)',
     'f_row(mon, 7, "DAY P&L · FILLS", f_usd(dayPnl) + " · " + str.tostring(dayFills) + "/" + str.tostring(maxFills) + (mLockOn or pLockOn ? " · month " + f_usd(mPnl) + (pLocked ? " (locked " + f_usd(pLockPct / 100.0 * mPeak) + ")" : "") : ""), dayPnl >= 0 ? posC : negC)'),
]
for old, new in REPS:
    if old is None:                                   # insert the new input group after the pauseDays line
        assert s.count(new) == 1
        s = s.replace(new, new + INPUTS)
        continue
    n = s.count(old)
    assert n == 1, (n, old[:100])
    s = s.replace(old, new)
open(B, 'w', encoding='utf8').write(s)
print(len(REPS), 'edits; lines', s.count('\n'))
