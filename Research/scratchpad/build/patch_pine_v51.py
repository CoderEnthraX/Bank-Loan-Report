"""Strategy v5.1 (2026-11-19, spec v50/SPEC_v50.md section 5): with Base And Recovery Amounts Are = Profit a final-TP win is the amount
including the costs: f_pD(rp) = a final-TP win per $ of stop-out loss for this stop (earn-back: exitR x stop / (stop + costs)); used for the
base, the add-ons, Exact and the Crooks recovery (f_crkRule takes the divisor), L's growth, K's careful $, Oscar (goal = the trade's base win,
exBaseWin). Risk mode unchanged. Applied to build/bak/strategy_template_v50.pine, then assemble.py."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
t = open(B + 'bak/strategy_template_v50.pine').read()


def sub1(a, b):
    global t
    assert t.count(a) == 1, (a[:100], t.count(a))
    t = t.replace(a, b)


sub1('''//  careful size below it) and Crooks L (0.01 lot until a win, then the loss split by the drawdown; the base grows at a new best).
//  The same as in the MT5 EA.
''', '''//  careful size below it) and Crooks L (0.01 lot until a win, then the loss split by the drawdown; the base grows at a new best).
//  The same as in the MT5 EA.
//  v5.1: with Profit a final-TP win is the amount INCLUDING the spread and commission (v5.0 came short by them). The same in the MT5 EA.
''')
sub1('e.g. $50 with the final TP at 0.1R -> the trade risks $500. ',
     'e.g. $50 with the final TP at 0.1R -> the trade risks about $500 plus the costs (with a $2.50 gold stop $546) and wins $50. ')
sub1("var float exBase    = baseRiskIn   // the base risk of the open trade (for its booking)\n",
     "var float exBase    = baseRiskIn   // the base risk of the open trade (for its booking)\n"
     "var float exBaseWin = 0.0          // v5.1: the base win at the final TP of the open trade (Profit: Oscar's goal)\n")
sub1('''f_crkRule(float B, float x, bool rn, bool useT1, float mul, float eRisk) =>
    float q = rn ? (useT1 ? math.max(B, x) : math.max(B, x / exitR)) : B
''', '''f_crkRule(float B, float x, bool rn, bool useT1, float mul, float eRisk, float xr) =>
    float q = rn ? (useT1 ? math.max(B, x) : math.max(B, x / xr)) : B
''')
sub1('''// v5.0 Crooks L: the parts of a loss just booked''', '''// v5.1 Size By Profit: what a final-TP win brings per $ of stop-out loss for a stop of rp, costs included (earn-back pushes the target by
// them, so a win nets exitR x rp); a stop of 0 or a target inside the costs: the R alone
f_pD(float rp) =>
    float lu = rp * syminfo.pointvalue * fx + costUnit
    float wn = earnBack ? exitR * rp * syminfo.pointvalue * fx : exitR * rp * syminfo.pointvalue * fx - costUnit
    lu > 0 and wn > 0 ? wn / lu : exitR
// v5.0 Crooks L: the parts of a loss just booked''')
sub1('''    // v5.0: with Profit the base and the amounts a rule adds are wins at the final TP (risk = amount / its R); Risk: / 1
    float pD  = sizeBy == SB_PROFIT ? exitR : 1.0
''', '''    // v5.0: with Profit the base and the amounts a rule adds are wins at the final TP; Risk: / 1. v5.1: a win per $ of risk WITH the costs
    float pD  = sizeBy == SB_PROFIT ? f_pD(rp) : 1.0
    float pXR = sizeBy == SB_PROFIT ? pD : exitR      // Exact and the Crooks recovery divide by it (Risk: the final TP's R)
''')
sub1('recMode == L_EXACT ? recPool / exitR : recMode == L_STEP', 'recMode == L_EXACT ? recPool / pXR : recMode == L_STEP')
sub1('    int   oscNeed = int(math.max(1, math.ceil(((sizeBy == SB_PROFIT ? baseRisk * exitR : baseRisk) - oscP) / (baseRisk * exitR))))   // v5.0: Profit: the goal is one base win\n',
     '    int   oscNeed = int(math.max(1, math.ceil(((sizeBy == SB_PROFIT ? baseRisk * pD : baseRisk) - oscP) / (baseRisk * pXR))))   // v5.0: Profit: the goal is one base win\n')
sub1('crkX, crkRn, t1Ok, t1Mul, eRisk)   // v5.0 Crooks L: the base grows at a new best', 'crkX, crkRn, t1Ok, t1Mul, eRisk, pXR)   // v5.0 Crooks L: the base grows at a new best')
sub1('math.min(f_crkRule(ladB, crkX, crkRn, t1Ok, t1Mul, eRisk), crkR + ladGam * ladC / t1Mul)', 'math.min(f_crkRule(ladB, crkX, crkRn, t1Ok, t1Mul, eRisk, pXR), crkR + ladGam * ladC / t1Mul)')
sub1('        exBase    := baseRisk\n', '        exBase    := baseRisk\n        exBaseWin := sizeBy == SB_PROFIT ? baseRisk * pD : baseRisk\n')
sub1('    if oscP >= (sizeBy == SB_PROFIT ? exBase * exitR : exBase)    // v5.0: with Profit the cycle goal is one base win\n',
     '    if oscP >= (sizeBy == SB_PROFIT ? exBaseWin : exBase)    // v5.0: with Profit the cycle goal is one base win (v5.1: the trade\'s own)\n')
sub1('" = win " + f_usd(lB * exitR) + " at TP"', '" = win " + f_usd(lB * f_pD(nz(trRisk))) + " at TP"')
sub1('" · at the best, base " + f_usd(f_lBase(baseRisk, sizeBy == SB_PROFIT ? exitR : 1.0))', '" · at the best, base " + f_usd(f_lBase(baseRisk, sizeBy == SB_PROFIT ? f_pD(nz(trRisk)) : 1.0))')
open(B + 'strategy_template.pine', 'w').write(t)
print('strategy template v5.1 written', t.count('\n'), 'lines')
