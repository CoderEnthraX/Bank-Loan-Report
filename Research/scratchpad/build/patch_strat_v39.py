"""v3.9 strategy template patch: Crooks C rule after N losing recovery trades in a row (same logic as the EA and gold/recovery.py)."""
import sys
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/strategy_template.pine'
s = open(F).read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('count %d != %d for: %s' % (c, n, old[:100]))
    s = s.replace(old, new)

# inputs
anchor = 'parN     = input.int(3, "Wins Before Reset (Paroli)", minval = 1, group = GRP_L)\n'
rep(anchor, '''CPR_OFF    = "Off (Crooks C as now)"
CPR_FORGET = "Forget the loss"
CPR_PCT    = "Go for a % of the loss, forget it after N"
CPR_WAIT   = "Wait for M wins in a row, then a loss and a win"
CPR_SKIP   = "Skip D trading days"
crkPr     = input.string(CPR_OFF, "Crooks C: After N Losing Recovery Trades In A Row", options = [CPR_OFF, CPR_FORGET, CPR_PCT, CPR_WAIT, CPR_SKIP], group = GRP_L, tooltip = "Crooks C only. What happens after N recovery trades in a row have lost (recovery trades that lost with no winning recovery trade between them; base trades between them do not break the count). N, the % and M / D are set below.\\nForget the loss: a new cycle starts at the base risk (the money lost stays lost; it is just no longer chased).\\nGo for a % of the loss: every recovery trade goes for that % of the loss; when it wins, the rest is forgotten; after N losing recovery trades the loss is forgotten.\\nWait for M wins in a row: every trade risks the base until M trades win in a row; then, after the next loss and the win after it, the trade after that win is the recovery trade (the loss is kept).\\nSkip D trading days: no new trades for the rest of that day and D more trading days, then Crooks C goes on.\\nGold 2021-2026, 19 strategies profitable at fixed $50, no hard cap: as now +$225k, but the account blew in about 20% of shuffled trade orders; forget after 2 / 3: +$100k / +$108k, worst fall 26% / 27%, never blown; 50% + forget after 2: +$93k, worst fall 20%; wait for 2 wins after 2: +$182k, worst fall 95%, blown in 14%; skip 3 days after 2: +$176k keeping the loss (blown in 18%), +$89k forgetting it (worst fall 32%, never blown).")
crkPrN    = input.int(2, "Crooks C Rule: N Losing Recovery Trades In A Row", minval = 1, group = GRP_L, tooltip = "For every rule above: how many recovery trades in a row must lose before the rule acts.")
crkPrPct  = input.float(50.0, "Crooks C Rule: % Of The Loss Per Recovery Trade", minval = 10.0, maxval = 100.0, step = 5.0, group = GRP_L, tooltip = "Only for 'Go for a % of the loss'. Each recovery trade goes for this % of the loss to win back (with Crooks C over N wins: of each part); when its last part wins, the rest is forgotten and a new cycle starts.")
crkPrM    = input.int(2, "Crooks C Rule: M Wins In A Row To Wait For", minval = 1, group = GRP_L, tooltip = "Only for 'Wait for M wins in a row'. After N losing recovery trades every trade risks the base until this many trades win in a row; then, after the next loss and the win after it, the trade after that win is the recovery trade.")
crkPrD    = input.int(3, "Crooks C Rule: D Trading Days To Skip", minval = 1, group = GRP_L, tooltip = "Only for 'Skip D trading days'. No new trades for the rest of the day on which the N-th losing recovery trade closed, plus this many trading days (time zone of DAYS AND HOURS). Trading days: the ticked days when Trade Only On The Ticked Days is on, Monday to Friday when it is off.\\nExample: Tue / Wed / Thu ticked, D = 3, the trade closes on a Tuesday: the rest of Tuesday, Wednesday, Thursday and next Tuesday are skipped; trading starts again next Wednesday.")
crkPrForget = input.bool(false, "Crooks C Rule: Forget The Loss After The Skipped Days", group = GRP_L, tooltip = "Only for 'Skip D trading days'. Off: the loss is kept and Crooks C goes on after the pause (the trade after the next win is a recovery trade). On: the loss is forgotten; a new cycle starts at the base risk.")
crkPrAll  = input.bool(false, "Crooks C Rule: Count Every Day, Not Only The Trading Days", group = GRP_L, tooltip = "Only for 'Skip D trading days'. On: every day counts toward D, also days that are not ticked (e.g. Monday and Friday) and weekend days with candles.")
''' + anchor)

# state
rep('''var int   crkP      = crkNp  // Crooks C over N wins: parts of the loss still to win back (a recovery trade wins loss / parts)
''', '''var int   crkP      = crkNp  // Crooks C over N wins: parts of the loss still to win back (a recovery trade wins loss / parts)
var int   crkF      = 0      // Crooks C rule: losing recovery trades in a row in this cycle
var bool  crkWait   = false  // wait rule: waiting for M wins in a row
var int   crkWW     = 0      //   wins in a row while waiting
var bool  crkNeedL  = false  //   the M wins came: the next recovery trade waits for a loss, then a win
var bool  crkSkip   = false  // skip rule: trading is paused
var int   crkSkipLeft = 0    //   counted days still to skip
bool      crkPrOn   = recMode == L_CRC and crkPr != CPR_OFF
''')
rep('''f_crkRecNext() => ((recMode == L_CRA or recMode == L_CRB) and crkN >= 2 and crkN % 2 == 0) or (recMode == L_CRC and crkW and crkL > 0) or (recMode == L_CRD and crkN >= 2 and (crkN - 2) % 3 == 0)''',
    '''// (C with the wait rule: not while waiting for the M wins, nor before the loss that follows them)
f_crkRecNext() => ((recMode == L_CRA or recMode == L_CRB) and crkN >= 2 and crkN % 2 == 0) or (recMode == L_CRC and crkW and crkL > 0 and not (crkPrOn and crkPr == CPR_WAIT and (crkWait or crkNeedL))) or (recMode == L_CRD and crkN >= 2 and (crkN - 2) % 3 == 0)''')

# day counting of the skip rule
rep('''if newDay
    dayPnl   := 0.0
    dayBlock := false
    paused   := pauseLeft > 0
    if pauseLeft > 0
        pauseLeft -= 1
''', '''if newDay
    dayPnl   := 0.0
    dayBlock := false
    paused   := pauseLeft > 0
    if pauseLeft > 0
        pauseLeft -= 1
// Crooks C skip rule: a new day in the time zone of DAYS AND HOURS while trading is paused; counted days (the ticked days with Trade Only On The
// Ticked Days, else Monday-Friday, or every day) end the pause; the day the count reaches 0 is still skipped (counted before this bar's booking)
int   udKey = year(time, tzUse) * 10000 + month(time, tzUse) * 100 + dayofmonth(time, tzUse)
bool  udNew = udKey != nz(udKey[1], udKey)
int   udDow = dayofweek(time, tzUse)
if udNew and crkSkip
    if crkSkipLeft <= 0
        crkSkip := false
    else if crkPrAll or (dayOn ? dayOk : (udDow >= dayofweek.monday and udDow <= dayofweek.friday))
        crkSkipLeft -= 1
''')

# booking
rep('''    crkL := math.max(0.0, crkL - exPnl)
    if crkL < 0.01 or ((recMode == L_CRA or recMode == L_CRD) and win and crkRec)
        crkL := 0.0
        crkN := 0
        crkP := crkNp
    else
        crkN += 1
        crkP := not win ? crkNp : crkRec ? math.max(1, crkP - 1) : crkP    // Crooks C over N wins: a loss starts the parts again after the next win
''', '''    bool crkLast = crkP == 1     // this recovery trade went for the last part of the loss (Crooks C over N wins)
    crkL := math.max(0.0, crkL - exPnl)
    bool crkNew = crkL < 0.01 or ((recMode == L_CRA or recMode == L_CRD) and win and crkRec)
    if not crkNew
        crkN += 1
        crkP := not win ? crkNp : crkRec ? math.max(1, crkP - 1) : crkP    // Crooks C over N wins: a loss starts the parts again after the next win
        // Crooks C rule after N losing recovery trades in a row
        if crkPrOn
            if crkWait
                crkWW := win ? crkWW + 1 : 0
                if crkWW >= crkPrM                // M wins in a row end the wait ...
                    crkWait  := false
                    crkWW    := 0
                    crkNeedL := true
            else if crkNeedL and not win          // ... then a loss: the trade after the next win is the recovery trade
                crkNeedL := false
            if crkRec and win
                crkF := 0
                if crkPr == CPR_PCT and crkLast   // the % went for is back, the rest is forgotten
                    crkNew := true
            else if crkRec
                crkF += 1
                if crkF >= crkPrN
                    crkF := 0
                    if crkPr == CPR_FORGET or crkPr == CPR_PCT
                        crkNew := true
                    else if crkPr == CPR_WAIT
                        crkWait  := true
                        crkWW    := 0
                        crkNeedL := false
                    else if crkPr == CPR_SKIP
                        crkSkip     := true
                        crkSkipLeft := crkPrD
                        crkNew      := crkPrForget
    if crkNew                    // a new cycle at the base risk
        crkL     := 0.0
        crkN     := 0
        crkP     := crkNp
        crkF     := 0
        crkWait  := false
        crkWW    := 0
        crkNeedL := false
''')

# cap restart
rep('''            crkL      := 0.0
            crkN      := 0
            crkW      := false
            crkP      := crkNp
''', '''            crkL      := 0.0
            crkN      := 0
            crkW      := false
            crkP      := crkNp
            crkF      := 0
            crkWait   := false
            crkWW     := 0
            crkNeedL  := false
''')

# sizing: the % rule
rep('''    float crkX  = crkL / (recMode == L_CRB ? cSplit : recMode == L_CRC ? crkP : 1)
''', '''    float crkX  = crkL / (recMode == L_CRB ? cSplit : recMode == L_CRC ? crkP : 1) * (crkPrOn and crkPr == CPR_PCT ? crkPrPct / 100.0 : 1.0)
''')

# taking a setup: the pause
rep('''// ── 5. take the engine's new setup ──
''', '''// ── 5. take the engine's new setup ──
bool crkPause = crkPrOn and crkPr == CPR_SKIP and crkSkip     // Crooks C skip rule: trading paused
''')
rep('''    bool preSkip = exState != 0 or pos != 0 or newsBlock or flatNow or capStop or paused or dayBlock
''', '''    bool preSkip = exState != 0 or pos != 0 or newsBlock or flatNow or capStop or paused or dayBlock or crkPause
''')
rep('''paused ? "paused" : dayBlock ? "streak stop" : q <= 0 ? "size 0" : ""''',
    '''paused ? "paused" : dayBlock ? "streak stop" : crkPause ? "Crooks C pause" : q <= 0 ? "size 0" : ""''')

# table
rep('''paused ? "PAUSED (" + str.tostring(pauseLeft) + "d left)" : dayBlock ? "STREAK STOP TODAY" :''',
    '''paused ? "PAUSED (" + str.tostring(pauseLeft) + "d left)" : crkPause ? "CROOKS C PAUSE (" + str.tostring(crkSkipLeft) + "d left)" : dayBlock ? "STREAK STOP TODAY" :''')
rep('''(exState != 0 and exT1 ? " · TP1 rule, stop " + f_px(exT1Half ? strategy.position_avg_price : exT1Stop) : "")
''', '''(exState != 0 and exT1 ? " · TP1 rule, stop " + f_px(exT1Half ? strategy.position_avg_price : exT1Stop) : "") + (not crkPrOn ? "" : crkPause ? " · paused, " + str.tostring(crkSkipLeft) + " days left" : crkWait ? " · waiting for " + str.tostring(crkPrM) + " wins in a row (" + str.tostring(crkWW) + ")" : crkNeedL ? " · waiting for a loss, then a win" : crkF > 0 ? " · lost recoveries in a row " + str.tostring(crkF) + "/" + str.tostring(crkPrN) : "")
''')
open(F, 'w').write(s)
print('patched', len(s))
