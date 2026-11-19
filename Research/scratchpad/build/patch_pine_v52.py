"""Strategy v5.2 (2026-11-19, spec v50/SPEC_v50.md section 6): Crooks X = Crooks E with the loss to win back set after every close from the
levels (below the start: the gap to it; above it: the gap to the next step, at most the best; a win into another step: N parts again), and
an optional per-trade limit. Applied to build/bak/strategy_template_v51.pine, then assemble.py. The same as the MT5 EA v5.2."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
t = open(B + 'bak/strategy_template_v51.pine').read()


def sub1(a, b):
    global t
    assert t.count(a) == 1, (a[:100], t.count(a))
    t = t.replace(a, b)


sub1('''//  v5.1: with Profit a final-TP win is the amount INCLUDING the spread and commission (v5.0 came short by them). The same in the MT5 EA.
''', '''//  v5.1: with Profit a final-TP win is the amount INCLUDING the spread and commission (v5.0 came short by them). The same in the MT5 EA.
//  v5.2: Loss Recovery Crooks X: Crooks E where the loss to win back is the gap to the start (below it) or to the next step above it
//  ($1,000 by default, up to the best), won back over N trades; an optional per-trade limit. The same as in the MT5 EA.
''')
sub1('L_CRL   = "Crooks L (0.01 lot until a win, the loss split by the drawdown)"\n',
     'L_CRL   = "Crooks L (0.01 lot until a win, the loss split by the drawdown)"\n'
     'L_CRX   = "Crooks X (Crooks E, the loss = the gap to the start / the next step)"\n')
sub1('L_CRJ, L_CRK, L_CRL], group = GRP_L', 'L_CRJ, L_CRK, L_CRL, L_CRX], group = GRP_L')
sub1('at a new best the base grows by 10% of the profit (at most 4x). All settings below.\\n',
     'at a new best the base grows by 10% of the profit (at most 4x). All settings below.\\nX: Crooks E (0.01 lot after a loss until a win), but the loss to win back is taken from the balance: below the start it is the gap to the start; above it, the gap to the next step (every $1,000 above the start by default) up to the best balance; won back over N trades (Crooks C: Win The Loss Back Over N Wins); each new step starts N trades again.\\n')
sub1('''crkPrAll  = input.bool(false, "Crooks C Rule: Count Every Day''', '''cxStep    = input.float(1000.0, "Crooks X: Step Above The Start ($)", minval = 0.01, step = 100.0, group = GRP_L, tooltip = "Crooks X only. Above the start the loss to win back is the gap up to the next level, every this many $ above the start (e.g. start $1,000, best $5,000, balance $1,100 -> win back $900 up to $2,000, then $1,000 up to $3,000 ...), never above the best. Below the start it is the whole gap to the start. Each is won back over N trades (Crooks C: Win The Loss Back Over N Wins).")
CXL_CAP   = "Hard cap only"
CXL_TRADE = "Per-trade limit ($)"
cxLim     = input.string(CXL_CAP, "Crooks X: Limit Of A Recovery Trade", options = [CXL_CAP, CXL_TRADE], inline = "cx", group = GRP_L)
cxLimUsd  = input.float(500.0, "", minval = 0.01, step = 50.0, inline = "cx", group = GRP_L, tooltip = "Crooks X only. Hard cap only: a recovery trade is limited by the Hard Cap (if on), like every rule. Per-trade limit: also, a recovery trade risks at most this $ (the loss at its stop; never less than the base); the rest is won back by the next trades.")
crkPrAll  = input.bool(false, "Crooks C Rule: Count Every Day''')
sub1('or recMode == L_CRK or recMode == L_CRL   // v4.5: Crooks C and E - J (v5.0: K, L)', 'or recMode == L_CRK or recMode == L_CRL or recMode == L_CRX   // v4.5: Crooks C and E - J (v5.0: K, L; v5.2: X)')
sub1('''    else if not rn and crkL > 0 and (recMode == L_CRE or recMode == L_CRI or recMode == L_CRL)
''', '''    else if rn and recMode == L_CRX and cxLim == CXL_TRADE
        q := math.min(q, math.max(B, cxLimUsd) / mul)   // v5.2 Crooks X: the per-trade limit
    else if not rn and crkL > 0 and (recMode == L_CRE or recMode == L_CRI or recMode == L_CRL or recMode == L_CRX)
''')
sub1('''// v5.0 Crooks L: the parts of a loss just booked''', '''// v5.2 Crooks X: the step the closed profit v is in (-1 below the start), and the loss to win back from the levels: below the start the gap to
// it, above it the gap to the next cxStep level (at most the best crkPk); at the best nothing (0.005: a fraction of a cent under a level counts as at it)
f_xIdx(float v) => v < -0.005 ? -1 : int(math.floor((v + 0.005) / math.max(0.01, cxStep)))
f_xTarget(float v) =>
    float xs = math.max(0.01, cxStep)
    v < -0.005 ? -v : v >= crkPk - 0.005 ? 0.0 : math.max(0.0, math.min(crkPk, (math.floor((v + 0.005) / xs) + 1) * xs) - v)
// v5.0 Crooks L: the parts of a loss just booked''')
sub1('''    crkPk := math.max(crkPk, strategy.netprofit - rNet0) // v4.5 Crooks J, v4.6 ladder: the highest closed profit (v4.8: since the monthly restart)
''', '''    crkPk := math.max(crkPk, strategy.netprofit - rNet0) // v4.5 Crooks J, v4.6 ladder: the highest closed profit (v4.8: since the monthly restart)
    bool xNew = false                                    // v5.2 Crooks X: the loss is the gap to the level; a win into another step: N parts again
    if recMode == L_CRX
        float nrA = strategy.netprofit - rNet0
        crkL := f_xTarget(nrA)
        xNew := win and f_xIdx(nrA - exPnl) != f_xIdx(nrA)
''')
sub1('''        crkP := not win ? (recMode == L_CRL ? f_lParts() : crkNp) : crkRec ? math.max(1, crkP - 1) : crkP    // Crooks C over N wins: a loss starts the parts again after the next win (v5.0 L: from the drawdown)
''', '''        crkP := not win ? (recMode == L_CRL ? f_lParts() : crkNp) : crkRec ? math.max(1, crkP - 1) : crkP    // Crooks C over N wins: a loss starts the parts again after the next win (v5.0 L: from the drawdown)
        if xNew
            crkP := crkNp                                // v5.2 Crooks X: a new step is won back in N trades
''')
sub1('    string kWait = recMode == L_CRE or recMode == L_CRI or recMode == L_CRL ? " · "', '    string kWait = recMode == L_CRE or recMode == L_CRI or recMode == L_CRL or recMode == L_CRX ? " · "')
sub1(''' : " · at the best, base " + f_usd(f_lBase(baseRisk, sizeBy == SB_PROFIT ? f_pD(nz(trRisk)) : 1.0))) : ""''',
     ''' : " · at the best, base " + f_usd(f_lBase(baseRisk, sizeBy == SB_PROFIT ? f_pD(nz(trRisk)) : 1.0))) : recMode == L_CRX ? ((crkL <= 0 ? "" : nrT < -0.005 ? " · below the start: back to it" : " · up to " + f_usd(math.min(crkPk, (math.floor((nrT + 0.005) / math.max(0.01, cxStep)) + 1) * math.max(0.01, cxStep))) + " above the start") + (cxLim == CXL_TRADE ? ", at most " + f_usd(cxLimUsd) + " a trade" : "")) : ""''')
sub1('tooltip = "Crooks E, I and L (and Crooks K below the start)', 'tooltip = "Crooks E, I, L and X (and Crooks K below the start)')
open(B + 'strategy_template.pine', 'w').write(t)
print('strategy template v5.2 written', t.count('\n'), 'lines')
