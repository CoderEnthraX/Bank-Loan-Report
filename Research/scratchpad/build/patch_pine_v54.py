"""Strategy v5.4 (2026-11-20, spec v50/SPEC_v50.md section 8): 10 money rules (Kelly, 1-3-2-6, Equity-curve filter, Drawdown cut, Cooling-off,
Combos C1 - C5). Applied to build/bak/strategy_template_v53.pine, then assemble.py. The same as the MT5 EA v5.4."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
t = open(B + 'bak/strategy_template_v53.pine').read()


def sub1(a, b):
    global t
    assert t.count(a) == 1, (a[:100], t.count(a))
    t = t.replace(a, b)


sub1('''//  v5.3: Recovery Part Size: recalculate after each win (as before) or fixed when recovery starts (the same amount for the N trades).
''', '''//  v5.3: Recovery Part Size: recalculate after each win (as before) or fixed when recovery starts (the same amount for the N trades).
//  v5.4: 10 money rules in Loss Recovery: Kelly, 1-3-2-6, Equity-Curve Filter, Drawdown Cut, Cooling-Off and Combos 1 - 5. The same as in the MT5 EA.
''')
sub1('L_CRX   = "Crooks X (Crooks E, the loss = the gap to the start / the next step)"\n', '''L_CRX   = "Crooks X (Crooks E, the loss = the gap to the start / the next step)"
L_KELLY = "Kelly (learned from the last trades)"
L_1326  = "1-3-2-6 (after each win)"
L_EQF   = "Equity-curve filter"
L_DDCUT = "Drawdown cut"
L_COOL  = "Cooling-off after losses in a row"
L_C1    = "Combo 1: Paroli up / brake down"
L_C2    = "Combo 2: 1-3-2-6 up / small lot down"
L_C3    = "Combo 3: % of equity + equity-curve filter"
L_C4    = "Combo 4: Kelly + brake"
L_C5    = "Combo 5: profit-paid recovery + brake"
''')
sub1('L_CRL, L_CRX], group = GRP_L', 'L_CRL, L_CRX, L_KELLY, L_1326, L_EQF, L_DDCUT, L_COOL, L_C1, L_C2, L_C3, L_C4, L_C5], group = GRP_L')
sub1('each new step starts N trades again.\\n', 'each new step starts N trades again.\\nMoney rules (Money Rules settings below): Kelly: risk = Kelly fraction x the Kelly size learned from the last trades (the small lot when the trades show no edge). 1-3-2-6: base x 1, 3, 2, 6 after each win, back to 1 after a loss. Equity-curve filter: base, a smaller size while the closed balance is under its average. Drawdown cut: base, half from 10% below the best balance, a quarter from 20%. Cooling-off: base; after 2 losses in a row the next 3 signals are skipped. Combo 1: Paroli at or above the start, a brake below it. Combo 2: 1-3-2-6 at or above the start, the small lot below. Combo 3: 1.5% of equity, a quarter under the balance average. Combo 4: quarter Kelly, half from 10% below the best. Combo 5: Over N recovery paid only from the profit above the start, a brake below. The combos never risk more than 3% of the equity on a trade.\\n')
sub1('''parN     = input.int(3, "Wins Before Reset (Paroli)"''', '''GRP_MM    = "MONEY RULES (Kelly, 1-3-2-6, filters, Combos 1 - 5)"
mmKFrac   = input.float(0.25, "Kelly: Fraction Of The Kelly Size", minval = 0.01, maxval = 1.0, step = 0.05, group = GRP_MM, tooltip = "Kelly and Combo 4. 0.25 = a quarter of the full Kelly size (the full size swings far too much).")
mmKWin    = input.int(100, "Kelly: Learn From The Last N Trades", minval = 2, maxval = 200, group = GRP_MM)
mmKMin    = input.int(30, "Kelly: Trades Before It Starts (The Base Until Then)", minval = 2, maxval = 200, group = GRP_MM)
mmEqN     = input.int(20, "Equity Filter: Average Of The Last N Closed Balances", minval = 1, maxval = 200, group = GRP_MM, tooltip = "Equity-curve filter and Combo 3.")
mmEqLow   = input.float(0.25, "Equity Filter: Size While Under The Average (x)", minval = 0.0, maxval = 1.0, step = 0.05, group = GRP_MM)
mmDd1     = input.float(10.0, "Drawdown: Half Size From This % Below The Best", minval = 0.1, step = 1.0, group = GRP_MM, tooltip = "Drawdown cut and the brakes of the combos.")
mmDd2     = input.float(20.0, "Drawdown: Quarter Size From This % Below The Best", minval = 0.1, step = 1.0, group = GRP_MM, tooltip = "Not below the half-size step.")
mmCoolL   = input.int(2, "Cooling-Off: After This Many Losses In A Row", minval = 1, group = GRP_MM)
mmCoolN   = input.int(3, "Cooling-Off: Skip This Many Signals", minval = 0, group = GRP_MM)
mmCap     = input.float(3.0, "Combos: A Trade Risks At Most This % Of The Equity", minval = 0.01, step = 0.5, group = GRP_MM)
mmC3Pct   = input.float(1.5, "Combo 3: % Of The Equity At Risk", minval = 0.01, step = 0.1, group = GRP_MM)
mmC5Share = input.float(30.0, "Combo 5: Recovery Extra At Most This % Of The Profit", minval = 0.0, step = 5.0, group = GRP_MM)
parN     = input.int(3, "Wins Before Reset (Paroli)"''')
sub1('var float crkFx     = 0.0    // v5.3: the fixed recovery part ($ to win back; 0 = not set)\n', '''var float crkFx     = 0.0    // v5.3: the fixed recovery part ($ to win back; 0 = not set)
var array<float> mmRa  = array.new_float(0)   // v5.4: the R of the last trades (oldest first, at most 200)
var array<float> mmEqA = array.new_float(0)   // v5.4: the closed profit after each trade (none = [0]; cleared at the monthly restart)
var int   mmS1326   = 0      // v5.4: 1-3-2-6 step
var int   mmLossRow = 0      // v5.4: losses in a row (Cooling-off)
var int   mmCoolLeft = 0     // v5.4: signals still to skip (Cooling-off)
var float exRisk0   = 0.0    // v5.4: the planned risk of the open trade (its R = P&L / this)
''')
sub1('// v5.0 Crooks L: the parts of a loss just booked', '''// v5.4 money rules: the average closed profit and Kelly learned from the kept R values
f_mmMA() =>
    int n0 = array.size(mmEqA)
    float out = 0.0
    if n0 > 0
        int n = math.max(1, math.min(math.min(mmEqN, 200), n0))
        float sm = 0.0
        for q = n0 - n to n0 - 1
            sm += array.get(mmEqA, q)
        out := sm / n
    out
f_mmKelly(float B, float E, float ml) =>
    int n0 = array.size(mmRa)
    float out = B
    if n0 >= math.max(1, mmKMin)
        int w0 = math.max(0, n0 - math.max(1, math.min(mmKWin, 200)))
        int nw = 0
        int nl = 0
        float sw = 0.0
        float sl = 0.0
        for q = w0 to n0 - 1
            float v = array.get(mmRa, q)
            if v > 0
                nw += 1
                sw += v
            else
                nl += 1
                sl += v
        float p  = float(nw) / float(n0 - w0)
        float rw = nw > 0 ? sw / nw : 0.0
        float lw = nl > 0 ? -sl / nl : 1.0
        float f  = rw > 0 and lw > 0 ? math.max(0.0, (p * rw - (1 - p) * lw) / (rw * lw)) * mmKFrac : 0.0
        out := f > 0 ? f * E * lw : ml
    out
// v5.0 Crooks L: the parts of a loss just booked''')
sub1('''    crkW   := win
''', '''    crkW   := win
    if exRisk0 > 0                                       // v5.4: the trade's R, the closed profit after it, 1-3-2-6, Cooling-off
        array.push(mmRa, exPnl / exRisk0)
        if array.size(mmRa) > 200
            array.shift(mmRa)
    if array.size(mmEqA) == 0
        array.push(mmEqA, 0.0)
    array.push(mmEqA, strategy.netprofit - rNet0)
    if array.size(mmEqA) > 200
        array.shift(mmEqA)
    mmS1326 := win ? (mmS1326 + 1) % 4 : 0
    if win
        mmLossRow := 0
    else
        mmLossRow += 1
        if mmLossRow >= math.max(1, mmCoolL)
            mmCoolLeft := math.max(0, mmCoolN)
            mmLossRow  := 0
''')
sub1('''    crkSkipLeft := 0
    rNet0       := strategy.netprofit''', '''    crkSkipLeft := 0
    mmS1326     := 0
    mmLossRow   := 0
    mmCoolLeft  := 0
    array.clear(mmEqA)                  // v5.4: the balance average starts again
    rNet0       := strategy.netprofit''')
# sizing
i = t.index('    float rUsd = recMode == L_LAB')
j = t.index('\n', i) + 1
t = t[:j] + '''    // v5.4 money rules (closed balance E, the closed profit since the start nR, the best crkPk, the drawdown from the best)
    bool  mmOn = recMode == L_KELLY or recMode == L_1326 or recMode == L_EQF or recMode == L_DDCUT or recMode == L_COOL or recMode == L_C1 or recMode == L_C2 or recMode == L_C3 or recMode == L_C4 or recMode == L_C5
    if mmOn
        float mE   = strategy.initial_capital + strategy.netprofit
        float mNr  = strategy.netprofit - rNet0
        float mSt0 = mE - mNr
        float mDd  = crkPk > mNr and mSt0 + crkPk > 0 ? (crkPk - mNr) / (mSt0 + crkPk) : 0.0
        float mMl  = eRisk > 0 ? eRisk : baseRisk
        float mMa  = f_mmMA()
        float mU   = mmS1326 == 0 ? 1.0 : mmS1326 == 1 ? 3.0 : mmS1326 == 2 ? 2.0 : 6.0
        float mBrk = baseRisk * math.min(1.0, mSt0 > 0 ? mE / mSt0 : 1.0) * (mDd < mmDd2 / 100.0 ? 0.5 : 0.25)
        rUsd := recMode == L_KELLY ? f_mmKelly(baseRisk, mE, mMl) : recMode == L_1326 ? baseRisk * mU : recMode == L_EQF ? baseRisk * (mNr >= mMa - 1e-9 ? 1.0 : mmEqLow) :
                 recMode == L_DDCUT ? baseRisk * (mDd < mmDd1 / 100.0 ? 1.0 : mDd < mmDd2 / 100.0 ? 0.5 : 0.25) : recMode == L_COOL ? baseRisk :
                 recMode == L_C1 ? (mNr >= 0 and mDd < mmDd1 / 100.0 ? baseRisk * math.pow(2, parWins) : mBrk) : recMode == L_C2 ? (mNr >= 0 ? baseRisk * mU : math.min(baseRisk, mMl)) :
                 recMode == L_C3 ? mE * mmC3Pct / 100.0 / pD * (mNr >= mMa - 1e-9 ? 1.0 : mmEqLow) : recMode == L_C4 ? f_mmKelly(baseRisk, mE, mMl) * (mDd >= mmDd1 / 100.0 ? 0.5 : 1.0) :
                 mNr >= 0 ? baseRisk + math.min(recPool / math.max(1, recN) / pD, mmC5Share / 100.0 * mNr) : mBrk
        if recMode == L_C1 or recMode == L_C2 or recMode == L_C3 or recMode == L_C4 or recMode == L_C5
            rUsd := math.min(rUsd, mmCap / 100.0 * mE)   // the combinations: never more than Cap % of the equity
''' + t[j:]
sub1('''    bool preSkip = exState != 0 or pos != 0 or newsBlock or flatNow or capStop or paused or dayBlock or crkPause or mStop
''', '''    bool preSkip = exState != 0 or pos != 0 or newsBlock or flatNow or capStop or paused or dayBlock or crkPause or mStop
    bool coolSkip = recMode == L_COOL and mmCoolLeft > 0 and not preSkip   // v5.4: a signal skipped by the cooling-off
    if coolSkip
        mmCoolLeft -= 1
        preSkip := true
''')
sub1('''            crkNeedL  := false
            rUsd      := math.min(baseC, hardCap)''', '''            crkNeedL  := false
            mmS1326   := 0
            mmLossRow := 0
            mmCoolLeft := 0
            rUsd      := math.min(baseC, hardCap)''')
i = t.index('    skipWhy := exState != 0 or pos != 0 ? "still in a trade"')
t = t[:i] + '    skipWhy := coolSkip ? "cooling-off" : ' + t[i + len('    skipWhy := '):]
sub1('''        exBaseWin := sizeBy == SB_PROFIT ? baseRisk * pD : baseRisk
''', '''        exBaseWin := sizeBy == SB_PROFIT ? baseRisk * pD : baseRisk
        exRisk0   := rUsd
''')
open(B + 'strategy_template.pine', 'w').write(t)
print('strategy template v5.4 written', t.count(chr(10)), 'lines')
