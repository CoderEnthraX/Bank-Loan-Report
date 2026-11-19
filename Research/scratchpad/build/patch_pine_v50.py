"""Strategy v5.0 (asked 2026-11-19, spec v50/SPEC_v50.md): Base And Recovery Amounts Are (Risk / Profit at the final TP) for the base and
every loss-recovery rule, Crooks K and Crooks L, the same as the EA v5.0 and gold/recovery.py. Strategy template only (the money rules are
strategy-only; the shared blocks and the indicator are unchanged). Applied to build/bak/strategy_template_v49.pine, then assemble.py."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
t = open(B + 'bak/strategy_template_v49.pine').read()


def sub1(a, b):
    global t
    assert t.count(a) == 1, (a[:100], t.count(a))
    t = t.replace(a, b)


# ---- header
sub1('''//  TARGETS, EXIT AND STOP MOVES; off by default, they work with any preset (the same in the indicator and the MT5 EA).
''', '''//  TARGETS, EXIT AND STOP MOVES; off by default, they work with any preset (the same in the indicator and the MT5 EA).
//  v5.0: BASE AND RECOVERY AMOUNTS ARE (Risk and position size): Risk (as before) or Profit: the base and every loss-recovery amount
//  are what the trade WINS at the final TP (the stop-out loss follows from it). Loss Recovery: Crooks K (Crooks J above the start, a
//  careful size below it) and Crooks L (0.01 lot until a win, then the loss split by the drawdown; the base grows at a new best).
//  The same as in the MT5 EA.
''')

# ---- Size By
TT_SB = ("Risk (default): the Base Risk $ (or the % of equity) is what the base trade LOSES at its stop, as before.\\n"
         "Profit: it is what the base trade WINS at the final TP (Final Exit); the stop-out loss follows from it, e.g. $50 with the final TP at 0.1R "
         "-> the trade risks $500. Every loss-recovery rule then goes for its amounts as wins at the final TP: Recover all losses on the next trade "
         "wins all the losses plus the base win, Recover losses over N trades wins 1/N of them on each trade, % of losses that %, Step-up adds the "
         "step to the win, Rule C wins the carried losses / split, Oscar's Grind ends a cycle at +1 base win; Exact at final TP and the Crooks rules "
         "already size this way. Rules that multiply the base (Martingale, Fibonacci, D'Alembert ...) multiply the base trade.\\n"
         "The hard cap, the limits of Crooks F / G / H / J / K and the profit ladder stay on the loss at the stop. Fixed lots: the base trade stays "
         "the lots. With partial profits a full win brings a little less (the parts closed at the earlier TPs). Same as the MT5 EA.")
sub1('''baseRiskIn = input.float(50.0, "Base Risk Per Trade ($)", minval = 0.01, step = 5.0, group = GRP_R, tooltip = "Fixed $ risk: every base trade risks this amount, whatever the stop size: quantity = risk / (stop distance x point value + costs per unit), converted to the account currency.")
''', '''SB_RISK    = "Risk: the loss at the stop"
SB_PROFIT  = "Profit: the win at the final TP"
sizeBy     = input.string(SB_RISK, "Base And Recovery Amounts Are", options = [SB_RISK, SB_PROFIT], group = GRP_R, tooltip = "%s")
baseRiskIn = input.float(50.0, "Base Risk Per Trade ($)", minval = 0.01, step = 5.0, group = GRP_R, tooltip = "Fixed $ risk: every base trade risks this amount, whatever the stop size: quantity = risk / (stop distance x point value + costs per unit), converted to the account currency.\\nWith Base And Recovery Amounts Are = Profit: the amount the base trade wins at the final TP (it risks this / the final TP's R).")
''' % TT_SB)
sub1('var float baseRisk = baseRiskIn    // the base risk ($) of the trade being sized, set by the Position Size when a setup comes (Fixed $ risk: always the input)\n',
     'var float baseRisk = sizeBy == SB_PROFIT ? baseRiskIn / exitR : baseRiskIn    // the base risk ($) of the trade being sized, set by the Position Size when a setup comes (Fixed $ risk: always the input; v5.0 Profit: / the final TP R)\n')

# ---- Loss Recovery: K, L
sub1('L_CRJ   = "Crooks J (Crooks C, recovery shrinks in a drawdown)"\n',
     'L_CRJ   = "Crooks J (Crooks C, recovery shrinks in a drawdown)"\n'
     'L_CRK   = "Crooks K (Crooks J above the start, careful size below it)"\n'
     'L_CRL   = "Crooks L (0.01 lot until a win, the loss split by the drawdown)"\n')
sub1('L_CRA, L_CRB, L_CRC, L_CRD, L_CRE, L_CRF, L_CRG, L_CRH, L_CRI, L_CRJ], group = GRP_L, tooltip = ',
     'L_CRA, L_CRB, L_CRC, L_CRD, L_CRE, L_CRF, L_CRG, L_CRH, L_CRI, L_CRJ, L_CRK, L_CRL], group = GRP_L, tooltip = ')
sub1('J: the recovery trade shrinks with the drawdown.\\nLosses stay in the pool until profits pay them back, then sizing returns to the base risk. Use the Hard Cap to limit it.")',
     'J: the recovery trade shrinks with the drawdown.\\n'
     'K: Crooks J (and the profit ladder) while the closed profit is at or above the start (the monthly restart, if on, makes each month a new start); '
     'below it the trade after a win uses the careful size (lots, $ or % of base) and the trades after a loss the Crooks E / I lot.\\n'
     'L: after a loss the Crooks E / I lot until a win; then the loss is won back in parts set by the drawdown when the loss is booked: below the '
     'start 1 part per 2x base from the start (at most 6), above the start 1 part per 5x base below the best (at most 3); at a new best the base '
     'grows by 10% of the profit (at most 4x). All settings below.\\n'
     'Losses stay in the pool until profits pay them back, then sizing returns to the base risk. Use the Hard Cap to limit it. With Base And Recovery '
     'Amounts Are = Profit every amount above is a win at the final TP.")')
sub1('crkELot   = input.float(0.01, "Crooks E / I: Lot While Waiting For A Win", minval = 0.0001, step = 0.01, group = GRP_L, tooltip = "Crooks E and I only. While a loss is owed',
     'crkELot   = input.float(0.01, "Crooks E / I: Lot While Waiting For A Win", minval = 0.0001, step = 0.01, group = GRP_L, tooltip = "Crooks E, I and L (and Crooks K below the start). While a loss is owed')
sub1('crkJX     = input.float(20.0, "Crooks J: Drawdown (x Base) Where Recovery Ends", minval = 1.0, step = 1.0, group = GRP_L, tooltip = "Crooks J only.',
     'crkJX     = input.float(20.0, "Crooks J: Drawdown (x Base) Where Recovery Ends", minval = 1.0, step = 1.0, group = GRP_L, tooltip = "Crooks J and K (K above the start).')
sub1('''20 = with a $50 base, at a $500 drawdown a recovery trade risks half; at $1,000 only the base.")
''', '''20 = with a $50 base, at a $500 drawdown a recovery trade risks half; at $1,000 only the base.")
CK_LOTS = "Lots"
CK_USD  = "Fixed $"
CK_PCT  = "% of base"
ckMode  = input.string(CK_LOTS, "Crooks K: Careful Size Below The Start", options = [CK_LOTS, CK_USD, CK_PCT], group = GRP_L, tooltip = "Crooks K only. While the closed profit is below the start (since the monthly restart, if it is on), the trade after a win uses this size and the trades after a loss the Crooks E / I lot until the next win; the TP1 rule is off there. At or above the start Crooks K is Crooks J (with the profit ladder if it is on; no 0.01-lot start guard).\\nGold 2021-2026 ($10,000, $50 base, monthly restart): with 0.02-0.03 lot the worst month was about 3x smaller than with Crooks J, for 25-30% less profit.")
ckLots  = input.float(0.02, "Crooks K: Careful Lots · $ · % Of Base", minval = 0.0001, step = 0.01, inline = "ck", group = GRP_L)
ckUsd   = input.float(25.0, "", minval = 0.01, step = 5.0, inline = "ck", group = GRP_L)
ckPct   = input.float(50.0, "", minval = 1.0, step = 5.0, inline = "ck", group = GRP_L, tooltip = "The careful size of the mode chosen above. Lots: rounded up to the lot step (at least one step). $: the risk, or with Base And Recovery Amounts Are = Profit the win at the final TP. %: of the base risk.")
clZ1    = input.float(2.0, "Crooks L Below The Start: 1 Part Per x Base · Most Parts", minval = 0.1, step = 0.5, inline = "cl1", group = GRP_L)
clZ1N   = input.int(6, "", minval = 1, inline = "cl1", group = GRP_L, tooltip = "Crooks L only. A loss booked while the closed profit is below the start (since the monthly restart, if on) is won back in parts: 1 part per this many base risks of drawdown from the start (2 with a $50 base: 1 part per $100), at most this many. Each winning recovery trade wins one part back; a loss sets the parts again.")
clZ2    = input.float(5.0, "Crooks L Above The Start: 1 Part Per x Base Below The Best · Most Parts", minval = 0.1, step = 0.5, inline = "cl2", group = GRP_L)
clZ2N   = input.int(3, "", minval = 1, inline = "cl2", group = GRP_L, tooltip = "Crooks L only. A loss booked while the closed profit is above the start but below its best: 1 part per this many base risks below the best, at most this many parts (it is profit at risk, so fewer parts).")
clGrow  = input.float(10.0, "Crooks L At A New Best: Base + % Of The Profit · At Most x Base", minval = 0.0, step = 5.0, inline = "cl3", group = GRP_L)
clGrowX = input.float(4.0, "", minval = 1.0, step = 0.5, inline = "cl3", group = GRP_L, tooltip = "Crooks L only. While the closed profit is at its best (a new high, and at the start), the base grows by this % of the profit (with Profit: the base win grows), at most this many times the base. 0 = no growth.")
''')
sub1('''ladMode   = input.string(LAD_OFF, "Profit Ladder (Crooks F-J): Risk Appetite", options = [LAD_OFF, LAD_LOW, LAD_MED, LAD_HIGH, LAD_XH, LAD_MAX], group = GRP_L, tooltip = "Crooks F, G, H, I and J only.''',
     '''ladMode   = input.string(LAD_OFF, "Profit Ladder (Crooks F-J): Risk Appetite", options = [LAD_OFF, LAD_LOW, LAD_MED, LAD_HIGH, LAD_XH, LAD_MAX], group = GRP_L, tooltip = "Crooks F, G, H, I, J and K only.''')
sub1('If the profit falls back to the start, every trade is the Crooks E / I lot (0.01) until it is in profit again.\\n',
     'If the profit falls back to the start, every trade is the Crooks E / I lot (0.01) until it is in profit again (Crooks K: its careful size below the start instead).\\n')

# ---- execution state: families, ladder guard, N
sub1('bool      crkCFam   = recMode == L_CRC or recMode == L_CRE or recMode == L_CRF or recMode == L_CRG or recMode == L_CRH or recMode == L_CRI or recMode == L_CRJ   // v4.5: Crooks C and E - J\n',
     'bool      crkCFam   = recMode == L_CRC or recMode == L_CRE or recMode == L_CRF or recMode == L_CRG or recMode == L_CRH or recMode == L_CRI or recMode == L_CRJ or recMode == L_CRK or recMode == L_CRL   // v4.5: Crooks C and E - J (v5.0: K, L)\n')
sub1('bool      ladFam    = recMode == L_CRF or recMode == L_CRG or recMode == L_CRH or recMode == L_CRI or recMode == L_CRJ   // v4.6 profit ladder: Crooks F - J\n',
     'bool      ladFam    = recMode == L_CRF or recMode == L_CRG or recMode == L_CRH or recMode == L_CRI or recMode == L_CRJ or recMode == L_CRK   // v4.6 profit ladder: Crooks F - J (v5.0: K)\n')
sub1('    [on, on and strategy.netprofit - rNet0 <= 0, on ? B + math.min((ladBmax - 1.0) * B, ladPhi * C) : B, C]\n',
     '    [on, on and recMode != L_CRK and strategy.netprofit - rNet0 <= 0, on ? B + math.min((ladBmax - 1.0) * B, ladPhi * C) : B, C]   // v5.0: no start guard for Crooks K (its own zone)\n')
sub1('int       crkNp     = crkCnOn ? crkCn : 1\n',
     'int       crkNp     = recMode == L_CRL ? 1 : crkCnOn ? crkCn : 1   // v5.0: Crooks L takes its parts from the drawdown\n')
sub1('''    else if rn and recMode == L_CRJ
        q := math.max(B, q * math.max(0.0, 1.0 - math.max(0.0, crkPk - (strategy.netprofit - rNet0)) / (crkJX * B)))
    else if not rn and crkL > 0 and (recMode == L_CRE or recMode == L_CRI)
        q := math.min(B, eRisk)
    q
''', '''    else if rn and (recMode == L_CRJ or recMode == L_CRK)
        q := math.max(B, q * math.max(0.0, 1.0 - math.max(0.0, crkPk - (strategy.netprofit - rNet0)) / (crkJX * B)))
    else if not rn and crkL > 0 and (recMode == L_CRE or recMode == L_CRI or recMode == L_CRL)
        q := math.min(B, eRisk)
    q
// v5.0 Crooks L: the parts of a loss just booked, from the closed profit after it (below the start: the drawdown from the start; above it:
// the drawdown from the best), in steps of the booked trade's base
f_lParts() =>
    float nR = strategy.netprofit - rNet0
    float dd = nR < 0 ? -nR : crkPk - nR
    float lStep = nR < 0 ? clZ1 * exBase : clZ2 * exBase
    int   mx = nR < 0 ? clZ1N : clZ2N
    int   np = 1
    if nR < crkPk and lStep > 0
        np := math.max(1, math.min(mx, math.ceil(dd / lStep - 1e-9)))
    np
// v5.0 Crooks L: at a new best (the closed profit at its high since the start or the monthly restart, also at the start) the base grows with the profit
f_lBase(float B, float pD) =>
    float nR = strategy.netprofit - rNet0
    nR >= crkPk ? B + math.min((math.max(1.0, clGrowX) - 1.0) * B, math.max(0.0, clGrow / 100.0 * nR / pD)) : B
''')

# ---- booking
sub1('''    oscP += exPnl
    if oscP >= exBase
''', '''    oscP += exPnl
    if oscP >= (sizeBy == SB_PROFIT ? exBase * exitR : exBase)    // v5.0: with Profit the cycle goal is one base win
''')
sub1('        crkP := not win ? crkNp : crkRec ? math.max(1, crkP - 1) : crkP    // Crooks C over N wins: a loss starts the parts again after the next win\n',
     '        crkP := not win ? (recMode == L_CRL ? f_lParts() : crkNp) : crkRec ? math.max(1, crkP - 1) : crkP    // Crooks C over N wins: a loss starts the parts again after the next win (v5.0 L: from the drawdown)\n')

# ---- sizing
sub1('''    baseRisk := sizeMode == SZ_LOT ? baseLot * unitsPer * (rp * syminfo.pointvalue * fx + costUnit) : sizeMode == SZ_PCT ? math.max(0.0, strategy.equity) * eqPct / 100.0 : baseRiskIn
    // risk $ for this trade: base + loss recovery, capped
    float add = recMode == L_ALL ? recPool : recMode == L_SPLIT ? recPool / recN : recMode == L_PART ? recPool * recPct / 100.0 : recMode == L_EXACT ? recPool / exitR : recMode == L_STEP ? recStep * recLosses : 0.0
''', '''    // v5.0: with Profit the base and the amounts a rule adds are wins at the final TP (risk = amount / its R); Risk: / 1
    float pD  = sizeBy == SB_PROFIT ? exitR : 1.0
    baseRisk := sizeMode == SZ_LOT ? baseLot * unitsPer * (rp * syminfo.pointvalue * fx + costUnit) : sizeMode == SZ_PCT ? math.max(0.0, strategy.equity) * eqPct / 100.0 / pD : baseRiskIn / pD
    // risk $ for this trade: base + loss recovery, capped
    float add = recMode == L_ALL ? recPool / pD : recMode == L_SPLIT ? recPool / recN / pD : recMode == L_PART ? recPool * recPct / 100.0 / pD : recMode == L_EXACT ? recPool / exitR : recMode == L_STEP ? recStep * recLosses / pD : 0.0
''')
sub1('    float baseC = recMode == L_CS ? math.max(baseRisk, capOn ? math.min(stepBase, hardCap) : stepBase) : baseRisk\n',
     '    float baseC = recMode == L_CS ? math.max(baseRisk, capOn ? math.min(stepBase / pD, hardCap) : stepBase / pD) : baseRisk\n')
sub1('    int   oscNeed = int(math.max(1, math.ceil((baseRisk - oscP) / (baseRisk * exitR))))\n',
     '    int   oscNeed = int(math.max(1, math.ceil(((sizeBy == SB_PROFIT ? baseRisk * exitR : baseRisk) - oscP) / (baseRisk * exitR))))   // v5.0: Profit: the goal is one base win\n')
sub1('''    [ladOn, ladGuard, ladB, ladC] = f_lad(baseRisk)                // v4.6 profit ladder (the TP1 rule is off while the start guard acts)
    bool  t1Ok  = crkT1On and (exitK == 1 or crkT1Any) and f_crkRecNext() and t1D > 0 and not ladGuard and (isL ? eP - t1S : t1S - eP) >= syminfo.mintick * 0.5
''', '''    [ladOn, ladGuard, ladB, ladC] = f_lad(baseRisk)                // v4.6 profit ladder (the TP1 rule is off while the start guard acts)
    bool  kZone = recMode == L_CRK and strategy.netprofit - rNet0 < 0    // v5.0 Crooks K below the start (no TP1 rule there)
    bool  t1Ok  = crkT1On and (exitK == 1 or crkT1Any) and f_crkRecNext() and t1D > 0 and not ladGuard and not kZone and (isL ? eP - t1S : t1S - eP) >= syminfo.mintick * 0.5
''')
sub1('''    float eRisk = eLots * unitsPer * (rp * syminfo.pointvalue * fx + costUnit)
    float crkR  = f_crkRule(baseRisk, crkX, crkRn, t1Ok, t1Mul, eRisk)
''', '''    float eRisk = eLots * unitsPer * (rp * syminfo.pointvalue * fx + costUnit)
    float kLots = math.ceil(math.max(ckLots, stepLots) / stepLots - 1e-9) * stepLots      // v5.0 Crooks K: the careful lots and their stop-out loss
    float kRisk = kLots * unitsPer * (rp * syminfo.pointvalue * fx + costUnit)
    float crkR  = f_crkRule(recMode == L_CRL ? f_lBase(baseRisk, pD) : baseRisk, crkX, crkRn, t1Ok, t1Mul, eRisk)   // v5.0 Crooks L: the base grows at a new best
''')
sub1('''        crkR := ladGuard ? math.min(baseRisk, eRisk) : math.min(f_crkRule(ladB, crkX, crkRn, t1Ok, t1Mul, eRisk), crkR + ladGam * ladC / t1Mul)
''', '''        crkR := ladGuard ? math.min(baseRisk, eRisk) : math.min(f_crkRule(ladB, crkX, crkRn, t1Ok, t1Mul, eRisk), crkR + ladGam * ladC / t1Mul)
    // v5.0 Crooks K below the start: after a win the careful size, after a loss the Crooks E / I lot
    if kZone
        crkR := crkW ? (ckMode == CK_USD ? ckUsd / pD : ckMode == CK_PCT ? baseRisk * ckPct / 100.0 : kRisk) : math.min(baseRisk, eRisk)
''')
sub1('recMode == L_DELAY ? (recLosses >= delayN ? baseRisk + recPool / recN : baseRisk) : recMode == L_EQPCT ? strategy.equity * eqPct / 100.0 : ',
     'recMode == L_DELAY ? (recLosses >= delayN ? baseRisk + recPool / recN / pD : baseRisk) : recMode == L_EQPCT ? strategy.equity * eqPct / 100.0 / pD : ')
sub1('recMode == L_C or recMode == L_CS ? math.max(baseC, carried / cSplit) : ',
     'recMode == L_C or recMode == L_CS ? math.max(baseC, carried / cSplit / pD) : ')

# ---- table
sub1('''    f_row(mon, 4, "RISK · QTY · LOTS", exState != 0 ? f_usd(exRiskUsd) + " · " + str.tostring(exQty, "#,##0.##") + " · " + str.tostring(lots, "#,##0.##") : "base " + f_usd(lB), white)
''', '''    f_row(mon, 4, "RISK · QTY · LOTS", exState != 0 ? f_usd(exRiskUsd) + " · " + str.tostring(exQty, "#,##0.##") + " · " + str.tostring(lots, "#,##0.##") : sizeBy == SB_PROFIT and sizeMode != SZ_LOT ? "base risk " + f_usd(lB) + " = win " + f_usd(lB * exitR) + " at TP" + str.tostring(exitK) : "base " + f_usd(lB), white)
''')
sub1('''    string kLim = recMode == L_CRF or recMode == L_CRI ? ", at most " + str.tostring(crkFK) + "x base" : recMode == L_CRH ? ", at most " + str.tostring(crkHPct) + "% of equity" : recMode == L_CRJ ? ", drawdown " + f_usd(math.max(0.0, crkPk - (strategy.netprofit - rNet0))) : ""
    string kWait = recMode == L_CRE or recMode == L_CRI ? " · " + str.tostring(crkELot) + " lot, waiting for a win" : " · base, waiting for a win"
''', '''    string kLim = recMode == L_CRF or recMode == L_CRI ? ", at most " + str.tostring(crkFK) + "x base" : recMode == L_CRH ? ", at most " + str.tostring(crkHPct) + "% of equity" : recMode == L_CRJ or recMode == L_CRK ? ", drawdown " + f_usd(math.max(0.0, crkPk - (strategy.netprofit - rNet0))) : ""
    string kWait = recMode == L_CRE or recMode == L_CRI or recMode == L_CRL ? " · " + str.tostring(crkELot) + " lot, waiting for a win" : " · base, waiting for a win"
    float  nrT   = strategy.netprofit - rNet0      // v5.0 Crooks K / L: where the closed profit is (since the start or the monthly restart)
    string kCare = ckMode == CK_USD ? f_usd(ckUsd) + (sizeBy == SB_PROFIT ? " win" : "") : ckMode == CK_PCT ? str.tostring(ckPct) + "% of the base" : str.tostring(ckLots) + " lot"
    string kZn   = recMode == L_CRK ? (nrT < 0 ? " · below the start: " + (crkW ? "careful " + kCare + " after a win" : str.tostring(crkELot) + " lot until a win") : " · above the start (Crooks J)") : recMode == L_CRL ? (nrT < 0 ? " · below the start" : nrT < crkPk ? " · below the best" : " · at the best, base " + f_usd(f_lBase(baseRisk, sizeBy == SB_PROFIT ? exitR : 1.0))) : ""
''')
sub1('''(crkCFam ? (kRec ? " · recovery trade" + (crkNp > 1 ? ", part " + str.tostring(crkNp - crkP + 1) + " of " + str.tostring(crkNp) : "") + kLim : crkL > 0 ? kWait : " · base") : " · trade "''',
     '''(crkCFam ? (kRec ? " · recovery trade" + (crkNp > 1 ? ", part " + str.tostring(crkNp - crkP + 1) + " of " + str.tostring(crkNp) : "") + (recMode == L_CRL ? ", " + str.tostring(crkP) + (crkP == 1 ? " part" : " parts") + " to go" : "") + kLim : crkL > 0 ? kWait : " · base") + kZn : " · trade "''')
sub1('''f_row(mon, r, "PROFIT LADDER", not ladFam ? "only with Crooks F, G, H, I or J" : ''',
     '''f_row(mon, r, "PROFIT LADDER", not ladFam ? "only with Crooks F, G, H, I, J or K" : ''')
open(B + 'strategy_template.pine', 'w').write(t)
print('strategy template v5.0 written', t.count('\n'), 'lines')
