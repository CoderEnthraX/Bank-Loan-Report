"""Strategy v4.5 (asked 2026-11-13): Crooks E - J, the same rules as the EA (patch_ea_v45.py) and gold/recovery.py. Each is Crooks C with one
change; everything of Crooks C applies to them (over N wins, the rule after N losing recovery trades, the TP1 rule, the hard cap). Existing input
titles are kept (TradingView keeps the saved values); only tooltips say that the Crooks C settings also act for E - J.
Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/strategy_template.pine'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''//  restart the loss recovery on the 1st); all off by default, the same settings as in the MT5 EA.
''', '''//  restart the loss recovery on the 1st); all off by default, the same settings as in the MT5 EA.
//  v4.5: Crooks E - J in Loss Recovery: Crooks C with smaller trades or a limit on the recovery trade, so a
//  long losing run costs less (the same rules as in the MT5 EA).
''')
rep('''L_CRD   = "Crooks D (base, base, recovery: every 3rd trade)"
''', '''L_CRD   = "Crooks D (base, base, recovery: every 3rd trade)"
L_CRE   = "Crooks E (Crooks C, 0.01 lot while waiting for a win)"
L_CRF   = "Crooks F (Crooks C, recovery at most K x base)"
L_CRG   = "Crooks G (Crooks C, loss to win back at most X x base)"
L_CRH   = "Crooks H (Crooks C, recovery at most % of equity)"
L_CRI   = "Crooks I (Crooks E + recovery at most K x base)"
L_CRJ   = "Crooks J (Crooks C, recovery shrinks in a drawdown)"
''')
rep('''L_CRA, L_CRB, L_CRC, L_CRD], group = GRP_L, tooltip = "All:''', '''L_CRA, L_CRB, L_CRC, L_CRD, L_CRE, L_CRF, L_CRG, L_CRH, L_CRI, L_CRJ], group = GRP_L, tooltip = "All:''')
rep('''base, recovery, base, base, recovery (trades 3, 6, 9 ...).\\nLosses stay in the pool''',
    '''base, recovery, base, base, recovery (trades 3, 6, 9 ...).\\nCrooks E - J are Crooks C with one change each (every Crooks C setting also acts for them):\\nCrooks E: while a loss is owed, every trade that is not the recovery trade is 0.01 lot (Crooks E / I lot), or the normal size if that is smaller; the recovery trade after a win goes for the loss as in Crooks C, and if it loses the trades go back to 0.01 lot until the next win.\\nCrooks F: a recovery trade risks at most K x base (default 3); the rest of the loss is won back after the next wins.\\nCrooks G: the loss to win back is never more than X x base (default 10); the rest is accepted as lost.\\nCrooks H: a recovery trade risks at most this % of the equity (default 1%).\\nCrooks I: Crooks E with the Crooks F limit.\\nCrooks J: the deeper the closed-profit drawdown, the smaller the recovery trade: x (1 - drawdown / (X x base)), never below the base (default X 20).\\nLosses stay in the pool''')
rep('''inline = "ccn", group = GRP_L, tooltip = "Crooks C only. 1 = the trade after a win''', '''inline = "ccn", group = GRP_L, tooltip = "Crooks C and E - J. 1 = the trade after a win''')
rep('''group = GRP_L, tooltip = "Crooks C only. What happens after N recovery trades''', '''group = GRP_L, tooltip = "Crooks C and E - J. What happens after N recovery trades''')
rep('''crkPrAll  = input.bool(false, "Crooks C Rule: Count Every Day, Not Only The Trading Days",''', '''crkELot   = input.float(0.01, "Crooks E / I: Lot While Waiting For A Win", minval = 0.0001, step = 0.01, group = GRP_L, tooltip = "Crooks E and I only. While a loss is owed, every trade that is not the recovery trade uses this many lots (rounded up to the lot step, at least one step), or the normal size if that is smaller. Gold: 0.01 lot = 1 oz.")
crkFK     = input.float(3.0, "Crooks F / I: Recovery Trade At Most x Base", minval = 1.0, step = 0.5, group = GRP_L, tooltip = "Crooks F and I only. The most a recovery trade may lose at its stop, in base risks (3 = $150 with a $50 base). A bigger loss to win back is won back over the next wins: after each win the next trade is a recovery trade again.")
crkGX     = input.float(10.0, "Crooks G: Loss To Win Back At Most x Base", minval = 0.5, step = 1.0, group = GRP_L, tooltip = "Crooks G only. The loss to win back is never more than this many base risks (10 = $500 with a $50 base); anything above is accepted as lost.")
crkHPct   = input.float(1.0, "Crooks H: Recovery Trade At Most % Of Equity", minval = 0.1, step = 0.1, group = GRP_L, tooltip = "Crooks H only. The most a recovery trade may lose at its stop, in % of the equity (never less than the base risk).")
crkJX     = input.float(20.0, "Crooks J: Drawdown (x Base) Where Recovery Ends", minval = 1.0, step = 1.0, group = GRP_L, tooltip = "Crooks J only. A recovery trade's risk is multiplied by 1 - drawdown / (this x base), never below the base risk. Drawdown = the highest closed profit minus the closed profit now. 20 = with a $50 base, at a $500 drawdown a recovery trade risks half; at $1,000 only the base.")
crkPrAll  = input.bool(false, "Crooks C Rule: Count Every Day, Not Only The Trading Days",''')
rep('''bool      crkPrOn   = recMode == L_CRC and crkPr != CPR_OFF
''', '''bool      crkCFam   = recMode == L_CRC or recMode == L_CRE or recMode == L_CRF or recMode == L_CRG or recMode == L_CRH or recMode == L_CRI or recMode == L_CRJ   // v4.5: Crooks C and E - J
bool      crkPrOn   = crkCFam and crkPr != CPR_OFF
var float crkPk     = 0.0    // v4.5 Crooks J: the highest closed profit (at each booked trade)
''')
rep('''(recMode == L_CRC and crkW and crkL > 0 and not (crkPrOn''', '''(crkCFam and crkW and crkL > 0 and not (crkPrOn''')
rep('''    crkL := math.max(0.0, crkL - exPnl)
    bool crkNew''', '''    crkL := math.max(0.0, crkL - exPnl)
    if recMode == L_CRG                                  // v4.5 Crooks G: never more than X x base to win back
        crkL := math.min(crkL, crkGX * baseRisk)
    crkPk := math.max(crkPk, strategy.netprofit)         // v4.5 Crooks J: the highest closed profit
    bool crkNew''')
rep('''    float crkX  = crkL / (recMode == L_CRB ? cSplit : recMode == L_CRC ? crkP : 1) * (crkPrOn and crkPr == CPR_PCT ? crkPrPct / 100.0 : 1.0)
    float crkR  = f_crkRecNext() ? (t1Ok ? math.max(baseRisk, crkX) : math.max(baseRisk, crkX / exitR)) : baseRisk
''', '''    float crkX  = crkL / (recMode == L_CRB ? cSplit : crkCFam ? crkP : 1) * (crkPrOn and crkPr == CPR_PCT ? crkPrPct / 100.0 : 1.0)
    bool  crkRn = f_crkRecNext()
    float crkR  = crkRn ? (t1Ok ? math.max(baseRisk, crkX) : math.max(baseRisk, crkX / exitR)) : baseRisk
    // v4.5 Crooks F / H / I / J: the most a recovery trade risks (F / H / I: its real stop-out loss, a wider TP1-rule stop included);
    // Crooks E / I: while a loss waits for a win, the small lot (its stop-out loss incl. costs), or the base if that is smaller
    if crkRn and (recMode == L_CRF or recMode == L_CRI)
        crkR := math.min(crkR, math.max(1.0, crkFK) * baseRisk / t1Mul)
    else if crkRn and recMode == L_CRH
        crkR := math.min(crkR, math.max(baseRisk, strategy.equity * crkHPct / 100.0) / t1Mul)
    else if crkRn and recMode == L_CRJ
        crkR := math.max(baseRisk, crkR * math.max(0.0, 1.0 - math.max(0.0, crkPk - strategy.netprofit) / (crkJX * baseRisk)))
    else if not crkRn and crkL > 0 and (recMode == L_CRE or recMode == L_CRI)
        float eLots = math.ceil(math.max(crkELot, stepLots) / stepLots - 1e-9) * stepLots
        crkR := math.min(baseRisk, eLots * unitsPer * (rp * syminfo.pointvalue * fx + costUnit))
''')
rep('''recMode == L_CRA or recMode == L_CRB or recMode == L_CRC or recMode == L_CRD ? crkR : baseRisk + add''',
    '''recMode == L_CRA or recMode == L_CRB or recMode == L_CRD or crkCFam ? crkR : baseRisk + add''')
rep('''    bool   isK = recMode == L_CRA or recMode == L_CRB or recMode == L_CRC or recMode == L_CRD
''', '''    bool   isK = recMode == L_CRA or recMode == L_CRB or recMode == L_CRD or crkCFam
''')
rep('''    string kTxt = f_usd(crkL) + (recMode == L_CRC ? (kRec ? " · recovery trade" + (crkNp > 1 ? ", part " + str.tostring(crkNp - crkP + 1) + " of " + str.tostring(crkNp) : "") : crkL > 0 ? " · base, waiting for a win" : " · base")''',
    '''    string kLim = recMode == L_CRF or recMode == L_CRI ? ", at most " + str.tostring(crkFK) + "x base" : recMode == L_CRH ? ", at most " + str.tostring(crkHPct) + "% of equity" : recMode == L_CRJ ? ", drawdown " + f_usd(math.max(0.0, crkPk - strategy.netprofit)) : ""
    string kWait = recMode == L_CRE or recMode == L_CRI ? " · " + str.tostring(crkELot) + " lot, waiting for a win" : " · base, waiting for a win"
    string kTxt = f_usd(crkL) + (recMode == L_CRG ? " (at most " + f_usd(crkGX * baseRisk) + ")" : "") + (crkCFam ? (kRec ? " · recovery trade" + (crkNp > 1 ? ", part " + str.tostring(crkNp - crkP + 1) + " of " + str.tostring(crkNp) : "") + kLim : crkL > 0 ? kWait : " · base")''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
