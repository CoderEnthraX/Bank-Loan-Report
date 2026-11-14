"""Strategy v4.6 (asked 2026-11-14): the PROFIT LADDER for Crooks F - J, the same rule as the EA (patch_ea_v46.py) and gold/recovery.py.
New inputs only (existing titles unchanged). Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/strategy_template.pine'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''//  long losing run costs less (the same rules as in the MT5 EA).
''', '''//  long losing run costs less (the same rules as in the MT5 EA).
//  v4.6: PROFIT LADDER for Crooks F - J (Off / Low / Medium / High / Extra high / Max): after a first profit the
//  risk grows, paid only from the profit above a lock; back at the start, 0.01 lot (the same as in the MT5 EA).
''')
rep('''crkJX     = input.float(20.0, "Crooks J: Drawdown (x Base) Where Recovery Ends",''', '''LAD_OFF   = "Off"
LAD_LOW   = "Low (keeps 80% of the best profit, base up to 2x)"
LAD_MED   = "Medium (keeps 70%, base up to 3x)"
LAD_HIGH  = "High (keeps 60%, base up to 5x)"
LAD_XH    = "Extra high (keeps 50%, base up to 8x)"
LAD_MAX   = "Max (keeps 40%, base up to 12x)"
ladMode   = input.string(LAD_OFF, "Profit Ladder (Crooks F-J): Risk Appetite", options = [LAD_OFF, LAD_LOW, LAD_MED, LAD_HIGH, LAD_XH, LAD_MAX], group = GRP_L, tooltip = "Crooks F, G, H, I and J only. Until the closed profit first reaches the profit target, the rule trades as usual. Then the trades grow with the profit above a lock (the share of the best profit that is kept), and the extra risk is paid only from that profit: a trade never risks less than the plain rule, and never more than the plain rule plus a share of that profit. If the profit falls back to the start, every trade is the Crooks E / I lot (0.01) until it is in profit again.\\nLow keeps 80% of the best profit and lets the base grow to 2x; Medium 70% / 3x; High 60% / 5x; Extra high 50% / 8x; Max 40% / 12x.")
ladT      = input.float(1000.0, "Profit Ladder: Profit Target Before The Risk Goes Up ($)", minval = 1.0, step = 100.0, group = GRP_L, tooltip = "The closed profit of the strategy that switches the profit ladder on. In the gold tests $1,000 worked better than $500: a $500 profit is gone in a normal losing run, so the 0.01-lot guard would act too often.")
crkJX     = input.float(20.0, "Crooks J: Drawdown (x Base) Where Recovery Ends",''')
rep('''var float crkPk     = 0.0    // v4.5 Crooks J: the highest closed profit (at each booked trade)
''', '''var float crkPk     = 0.0    // v4.5 Crooks J: the highest closed profit (at each booked trade)
bool      ladFam    = recMode == L_CRF or recMode == L_CRG or recMode == L_CRH or recMode == L_CRI or recMode == L_CRJ   // v4.6 profit ladder: Crooks F - J
float     ladLam    = ladMode == LAD_MED ? 0.7 : ladMode == LAD_HIGH ? 0.6 : ladMode == LAD_XH ? 0.5 : ladMode == LAD_MAX ? 0.4 : 0.8    //   lock: share of the best profit kept
float     ladPhi    = ladMode == LAD_MED ? 0.15 : ladMode == LAD_HIGH ? 0.2 : ladMode == LAD_XH ? 0.25 : ladMode == LAD_MAX ? 0.3 : 0.1   //   share of the cushion added to the base
float     ladBmax   = ladMode == LAD_MED ? 3.0 : ladMode == LAD_HIGH ? 5.0 : ladMode == LAD_XH ? 8.0 : ladMode == LAD_MAX ? 12.0 : 2.0   //   most base (x base)
float     ladGam    = ladMode == LAD_MED ? 0.3 : ladMode == LAD_HIGH ? 0.35 : ladMode == LAD_XH ? 0.4 : ladMode == LAD_MAX ? 0.5 : 0.25  //   most extra loss (share of the cushion)
// the profit ladder now: on, the start guard (closed profit 0 or less), its base, and the cushion (the closed profit above the lock)
f_lad() =>
    bool  on = ladMode != LAD_OFF and ladFam and ladT > 0 and crkPk >= ladT
    float C  = on ? math.max(0.0, strategy.netprofit - ladLam * crkPk) : 0.0
    [on, on and strategy.netprofit <= 0, on ? baseRisk + math.min((ladBmax - 1.0) * baseRisk, ladPhi * C) : baseRisk, C]
''')
rep('''f_crkRecNext() => ((recMode == L_CRA or recMode == L_CRB) and crkN >= 2 and crkN % 2 == 0) or (crkCFam and crkW and crkL > 0 and not (crkPrOn and crkPr == CPR_WAIT and (crkWait or crkNeedL))) or (recMode == L_CRD and crkN >= 2 and (crkN - 2) % 3 == 0)
''', '''f_crkRecNext() => ((recMode == L_CRA or recMode == L_CRB) and crkN >= 2 and crkN % 2 == 0) or (crkCFam and crkW and crkL > 0 and not (crkPrOn and crkPr == CPR_WAIT and (crkWait or crkNeedL))) or (recMode == L_CRD and crkN >= 2 and (crkN - 2) % 3 == 0)
// the risk of a Crooks rule's next trade at base B (v4.6: also at the profit ladder's base): x = the part of the loss it goes for, rn = a recovery
// trade, t1 = the TP1 rule, mul = its stop-out multiple, eRisk = the stop-out loss of the Crooks E / I lot (0.01)
f_crkRule(float B, float x, bool rn, bool t1, float mul, float eRisk) =>
    float q = rn ? (t1 ? math.max(B, x) : math.max(B, x / exitR)) : B
    if rn and (recMode == L_CRF or recMode == L_CRI)
        q := math.min(q, math.max(1.0, crkFK) * B / mul)
    else if rn and recMode == L_CRH
        q := math.min(q, math.max(B, strategy.equity * crkHPct / 100.0) / mul)
    else if rn and recMode == L_CRJ
        q := math.max(B, q * math.max(0.0, 1.0 - math.max(0.0, crkPk - strategy.netprofit) / (crkJX * B)))
    else if not rn and crkL > 0 and (recMode == L_CRE or recMode == L_CRI)
        q := math.min(B, eRisk)
    q
''')
rep('''    crkL := math.max(0.0, crkL - exPnl)
    if recMode == L_CRG                                  // v4.5 Crooks G: never more than X x base to win back
        crkL := math.min(crkL, crkGX * baseRisk)
    crkPk := math.max(crkPk, strategy.netprofit)         // v4.5 Crooks J: the highest closed profit
''', '''    crkL := math.max(0.0, crkL - exPnl)
    crkPk := math.max(crkPk, strategy.netprofit)         // v4.5 Crooks J, v4.6 ladder: the highest closed profit
    if recMode == L_CRG                                  // v4.5 Crooks G: never more than X x base to win back (v4.6: the ladder's base)
        [gOn, gGuard, gB, gC] = f_lad()
        crkL := math.min(crkL, crkGX * gB)
''')
rep('''    bool  t1Ok  = crkT1On and (exitK == 1 or crkT1Any) and f_crkRecNext() and t1D > 0 and''',
    '''    [ladOn, ladGuard, ladB, ladC] = f_lad()                // v4.6 profit ladder (the TP1 rule is off while the start guard acts)
    bool  t1Ok  = crkT1On and (exitK == 1 or crkT1Any) and f_crkRecNext() and t1D > 0 and not ladGuard and''')
rep('''    bool  crkRn = f_crkRecNext()
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
''', '''    bool  crkRn = f_crkRecNext()
    // v4.5 Crooks F / H / I / J: the most a recovery trade risks (F / H / I: its real stop-out loss, a wider TP1-rule stop included);
    // Crooks E / I: while a loss waits for a win, the small lot (its stop-out loss incl. costs), or the base if that is smaller
    float eLots = math.ceil(math.max(crkELot, stepLots) / stepLots - 1e-9) * stepLots
    float eRisk = eLots * unitsPer * (rp * syminfo.pointvalue * fx + costUnit)
    float crkR  = f_crkRule(baseRisk, crkX, crkRn, t1Ok, t1Mul, eRisk)
    // v4.6 profit ladder: the rule at the ladder's base, the extra risk paid only from the cushion; back at the start, the 0.01 lot
    if ladOn
        crkR := ladGuard ? math.min(baseRisk, eRisk) : math.min(f_crkRule(ladB, crkX, crkRn, t1Ok, t1Mul, eRisk), crkR + ladGam * ladC / t1Mul)
''')
rep('''        mon := table.new(f_pos(tablePos), 2, 13 + (mvAny ? 1 : 0) + (fltAny ? 1 : 0),''', '''        mon := table.new(f_pos(tablePos), 2, 13 + (mvAny ? 1 : 0) + (fltAny ? 1 : 0) + (ladMode != LAD_OFF ? 1 : 0),''')
rep('''    f_row(mon, 4, "RISK · QTY · LOTS", exState != 0 ? f_usd(exRiskUsd) + " · " + str.tostring(exQty, "#,##0.##") + " · " + str.tostring(lots, "#,##0.##") : "base " + f_usd(baseRisk), white)''',
    '''    [lOn, lGuard, lB, lC] = f_lad()
    f_row(mon, 4, "RISK · QTY · LOTS", exState != 0 ? f_usd(exRiskUsd) + " · " + str.tostring(exQty, "#,##0.##") + " · " + str.tostring(lots, "#,##0.##") : "base " + f_usd(lB), white)''')
rep('''    if fltAny
        f_row(mon, r, "SKIPPED BY FILTERS", f_fltTxt(), ghR <= 0 ? posC : negC)
        r += 1
''', '''    if fltAny
        f_row(mon, r, "SKIPPED BY FILTERS", f_fltTxt(), ghR <= 0 ? posC : negC)
        r += 1
    if ladMode != LAD_OFF
        f_row(mon, r, "PROFIT LADDER", not ladFam ? "only with Crooks F, G, H, I or J" : not lOn ? "best profit " + f_usd(math.max(0.0, crkPk)) + " of " + f_usd(ladT) + " to start" : lGuard ? "back at the start: 0.01 lot until in profit" : "lock " + f_usd(ladLam * crkPk) + " · cushion " + f_usd(lC) + " · base " + f_usd(lB), lGuard ? negC : lOn ? posC : white)
        r += 1
''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
