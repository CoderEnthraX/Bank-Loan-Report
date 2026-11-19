"""EA v5.1 (2026-11-19, spec v50/SPEC_v50.md section 5): Size by Profit makes a final-TP win equal the amount INCLUDING the costs: every
amount-to-risk conversion divides by PDiv(exitR) = a final-TP win per $ of stop-out loss on this setup (v5.0 divided by the R alone, so a win
was short by the costs' share). Exact and the Crooks recovery use it too with Profit; Oscar's goal is the trade's own base win (exBaseWin,
saved as "xw"). Risk mode unchanged. Applied to build/bak/AuctionRetestEA_v50.mq5 -> build/safe/AuctionRetestEA.mq5."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
s = open(B + 'bak/AuctionRetestEA_v50.mq5').read()


def sub1(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:100], s.count(a))
    s = s.replace(a, b)


def box(lines):
    return ''.join('//| ' + x.ljust(64) + ' |\n' for x in lines)


sub1('#property version   "5.00"', '#property version   "5.10"')
sub1(box(['base grows with the profit.']),
     box(['base grows with the profit.']) + box([
         'v5.1: Size by Profit includes the costs: a final-TP win is the',
         'amount itself (v5.0 came short by the spread and commission).']))
sub1('TblAdd("AUCTION RETEST", "EA v5.0", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v5.1", white, C\'61,143,214\');')

# ---- state: the base win of the setup / the trade
sub1('double   exBase = 0;   // v4.7: the base risk of the EA\'s trade (its booking: Oscar\'s Grind, Crooks G)\n',
     'double   exBase = 0;   // v4.7: the base risk of the EA\'s trade (its booking: Oscar\'s Grind, Crooks G)\n'
     'double   gBaseWin = 0, exBaseWin = 0;   // v5.1: the base WIN at the final TP of the setup being sized / of the EA\'s trade (Profit: Oscar\'s goal)\n')

# ---- PDiv after SizeProfit
sub1('bool   SizeProfit() { return InpSizeBy == SZB_PROFIT; }\n',
     'bool   SizeProfit() { return InpSizeBy == SZB_PROFIT; }\n'
     '//--- v5.1 Size by Profit: what a final-TP win brings per $ of stop-out loss on this setup, costs included (with earn-back the target is\n'
     '//--- pushed by the costs, so a win nets the R x the stop distance); no tick value / stop distance, or a target inside the costs: the R alone\n'
     'double PDiv(double exitR)\n'
     '{\n'
     '   if(exitR <= 0) return 1.0;\n'
     '   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();\n'
     '   if(tv <= 0 || ts <= 0 || trRisk <= 0) return exitR;\n'
     '   double spr = MathMax(CostSpr(), 0), loss = (trRisk + spr) / ts * tv + InpCommLot;\n'
     '   double win = exitR * trRisk / ts * tv;\n'
     '   if(!InpEarnBack) win -= spr / ts * tv + InpCommLot;\n'
     '   return (loss > 0 && win > 0) ? win / loss : exitR;\n'
     '}\n')
sub1('double ShowBase() { double b = InpSizeMode == PSZ_USD ? InpBaseRisk : BaseRisk(trRisk); return SizeProfit() && InpSizeMode != PSZ_LOT && ExitR() > 0 ? b / ExitR() : b; }',
     'double ShowBase() { double b = InpSizeMode == PSZ_USD ? InpBaseRisk : BaseRisk(trRisk); return SizeProfit() && InpSizeMode != PSZ_LOT && ExitR() > 0 ? b / PDiv(ExitR()) : b; }')
sub1('" = win " + DoubleToString(b * ExitR(), 2) + " at TP"', '" = win " + DoubleToString(b * PDiv(ExitR()), 2) + " at TP"')

# ---- KCare / LBase take the divisor
sub1('double KCare(double base, double exitR, double kRisk)\n{\n   if(InpCrkKMode == CKM_USD) return SizeProfit() && exitR > 0 ? InpCrkKUsd / exitR : InpCrkKUsd;',
     'double KCare(double base, double dv, double kRisk)\n{\n   if(InpCrkKMode == CKM_USD) return SizeProfit() && dv > 0 ? InpCrkKUsd / dv : InpCrkKUsd;   // v5.1: dv = PDiv (Risk: 1)')
sub1('double LBase(double base, double exitR)\n{\n   double nr = totalNet - gNet0;\n   if(InpRec != REC_CRL || nr < crkPk) return base;\n'
     '   double g = InpCrkLGrow / 100.0 * nr / (SizeProfit() && exitR > 0 ? exitR : 1.0);',
     'double LBase(double base, double dv)\n{\n   double nr = totalNet - gNet0;\n   if(InpRec != REC_CRL || nr < crkPk) return base;\n'
     '   double g = InpCrkLGrow / 100.0 * nr / (SizeProfit() && dv > 0 ? dv : 1.0);   // v5.1: dv = PDiv (Risk: 1)')

# ---- NextRisk
sub1('''   double base = BaseRisk(trRisk);                    // v4.7: the base of this setup (Position size)
   if(SizeProfit() && InpSizeMode != PSZ_LOT && exitR > 0) base = base / exitR;   // v5.0: the base is the win at the final TP
   double r = base;
   gBase = base;
   if(base <= 0) return 0;                            // no base: size 0 (never a zero divide below)
   double dv = SizeProfit() && exitR > 0 ? exitR : 1.0;   // v5.0: the amounts a rule adds are wins at the final TP (Risk: 1)
''', '''   double base = BaseRisk(trRisk);                    // v4.7: the base of this setup (Position size)
   double dv = SizeProfit() ? PDiv(exitR) : 1.0;      // v5.1: Profit: a final-TP win per $ of stop-out loss here, costs included (Risk: 1)
   double xr = SizeProfit() ? dv : exitR;             //   Exact and the Crooks recovery divide by it (Risk: the final TP's R)
   if(SizeProfit() && InpSizeMode != PSZ_LOT && dv > 0) base = base / dv;   // v5.0: the base is the win at the final TP (v5.1: with costs)
   double r = base;
   gBase = base; gBaseWin = SizeProfit() ? base * dv : base;
   if(base <= 0) return 0;                            // no base: size 0 (never a zero divide below)
''')
sub1('''   double oscGoal = SizeProfit() ? base * exitR : base;   // v5.0: with Profit the cycle goal is one base win
   int oscNeed = exitR > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((oscGoal - oscP) / (base * exitR)))) : 1;   // v4.7: no int overflow''',
     '''   double oscGoal = SizeProfit() ? base * dv : base;   // v5.0: with Profit the cycle goal is one base win
   int oscNeed = xr > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((oscGoal - oscP) / (base * xr)))) : 1;   // v4.7: no int overflow''')
sub1('      case REC_EXACT: r = base + recPool / exitR; break;\n', '      case REC_EXACT: r = base + recPool / xr; break;\n')
sub1('         r = CrkRule(LBase(base, exitR), exitR, minRisk);   // v5.0 Crooks L: the base grows at a new best',
     '         r = CrkRule(LBase(base, dv), xr, minRisk);   // v5.0 Crooks L: the base grows at a new best (v5.1: Profit divides by dv)')
sub1('MathMin(CrkRule(lb, exitR, minRisk), r + gam * cush / CrkT1Mult());', 'MathMin(CrkRule(lb, xr, minRisk), r + gam * cush / CrkT1Mult());')
sub1('         if(KZone()) r = crkW ? KCare(base, exitR, kRisk) : (minRisk > 0 ? MathMin(base, minRisk) : base);   // v5.0 Crooks K below the start',
     '         if(KZone()) r = crkW ? KCare(base, dv, kRisk) : (minRisk > 0 ? MathMin(base, minRisk) : base);   // v5.0 Crooks K below the start')

# ---- table, take, booking, state
sub1('" | at the best, base " + DoubleToString(LBase(ShowBase(), ExitR()), 2)', '" | at the best, base " + DoubleToString(LBase(ShowBase(), SizeProfit() ? PDiv(ExitR()) : 1.0), 2)')
sub1('exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot); exBase = gBase;', 'exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot); exBase = gBase; exBaseWin = gBaseWin;')
sub1('   if(oscP >= (SizeProfit() ? BookBase() * ExitR() : BookBase())) { oscU = 1; oscP = 0; } else if(win) oscU++;   // v5.0: with Profit the goal is one base win\n',
     '   if(oscP >= (SizeProfit() ? (exBaseWin > 0 ? exBaseWin : BookBase() * ExitR()) : BookBase())) { oscU = 1; oscP = 0; } else if(win) oscU++;   // v5.0: with Profit the goal is one base win (v5.1: the trade\'s own)\n')
sub1('IoD("xb", exBase);', 'IoD("xb", exBase); IoD("xw", exBaseWin);')
assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(B + 'safe/AuctionRetestEA.mq5', 'w').write(s)
print('EA v5.1 written', s.count('\n'), 'lines')
