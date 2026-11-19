"""EA v5.0 (asked 2026-11-19, spec v50/SPEC_v50.md): Size By (Risk / Profit at the final TP) for the base and every loss-recovery rule,
Crooks K and Crooks L. Applied to the v4.9 EA (build/bak/AuctionRetestEA_v49.mq5) -> build/safe/AuctionRetestEA.mq5. With Size By = Risk
and the old rules every number is the v4.9 one (division by 1.0 is exact; the rest is untouched)."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
s = open(B + 'bak/AuctionRetestEA_v49.mq5').read()


def sub1(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:100], s.count(a))
    s = s.replace(a, b)


def box(lines):
    return ''.join('//| ' + x.ljust(64) + ' |\n' for x in lines)


# ---- header, version, table title
sub1('#property version   "4.90"', '#property version   "5.00"')
sub1('//| off by default; they work with any preset (TradingView too).     |\n',
     '//| off by default; they work with any preset (TradingView too).     |\n' + box([
         'v5.0: SIZE BY: the base and every loss-recovery amount can be',
         'the PROFIT at the final TP (the stop-out loss follows from it).',
         'Crooks K: Crooks J above the start, below it a careful size',
         'after a win (lots, $ or % of base) and 0.01 lot after a loss.',
         'Crooks L: 0.01 lot until a win, then the loss is split by the',
         'drawdown (below the start / below the best); at a new best the',
         'base grows with the profit.']))
sub1('TblAdd("AUCTION RETEST", "EA v4.9", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v5.0", white, C\'61,143,214\');')

# ---- enums
sub1('                      PSZ_PCT = 2 };   // % of equity at risk (Risk % of equity)\n',
     '                      PSZ_PCT = 2 };   // % of equity at risk (Risk % of equity)\n'
     'enum ENUM_SIZE_BY   { SZB_RISK   = 0,  // Risk: the loss at the stop\n'
     '                      SZB_PROFIT = 1 };// Profit: the win at the final TP\n')
sub1('   REC_CRJ   = 27  // Crooks J (Crooks C, recovery shrinks in a drawdown)\n',
     '   REC_CRJ   = 27, // Crooks J (Crooks C, recovery shrinks in a drawdown)\n'
     '   REC_CRK   = 28, // Crooks K (Crooks J above the start, careful size below it)\n'
     '   REC_CRL   = 29  // Crooks L (0.01 lot until a win, the loss split by the drawdown)\n')
sub1('input group "LOSS RECOVERY"\n',
     'enum ENUM_CRK_K { CKM_LOTS = 0,  // Lots\n'
     '                  CKM_USD  = 1,  // Fixed amount (account currency)\n'
     '                  CKM_PCT  = 2 };// % of the base\n'
     'input group "LOSS RECOVERY"\n')

# ---- inputs
sub1('input ENUM_SIZE_MODE InpSizeMode = PSZ_USD; // Position size: the base trade (the loss recovery sizes every trade from it)\n',
     'input ENUM_SIZE_MODE InpSizeMode = PSZ_USD; // Position size: the base trade (the loss recovery sizes every trade from it)\n'
     'input ENUM_SIZE_BY InpSizeBy = SZB_RISK;     // Base and recovery amounts are (Risk: lost at the stop; Profit: won at the final TP)\n')
sub1('input double InpCrkELot  = 0.01;   // Crooks E / I: lot of the trades while a loss waits for a win (the normal size if smaller)\n',
     'input double InpCrkELot  = 0.01;   // Crooks E / I / K / L: lot of the trades while a loss waits for a win (the normal size if smaller)\n')
sub1('input double InpCrkJX    = 20.0;   // Crooks J: drawdown (x the base risk) at which a recovery trade is back to the base risk\n',
     'input double InpCrkJX    = 20.0;   // Crooks J / K: drawdown (x the base risk) at which a recovery trade is back to the base risk\n'
     'input ENUM_CRK_K InpCrkKMode = CKM_LOTS; // Crooks K: careful size below the start, after a win (after a loss: the E / I lot)\n'
     'input double InpCrkKLots = 0.02;   //   ...lots (Lots)\n'
     'input double InpCrkKUsd  = 25.0;   //   ...amount (Fixed amount; with Size by Profit: the win at the final TP)\n'
     'input double InpCrkKPct  = 50.0;   //   ...% of the base (% of the base)\n'
     'input double InpCrkLZ1   = 2.0;    // Crooks L: below the start, 1 part per this many x base of drawdown (from the start)\n'
     'input int    InpCrkLZ1N  = 6;      //   ...most parts below the start\n'
     'input double InpCrkLZ2   = 5.0;    // Crooks L: above the start, 1 part per this many x base below the best\n'
     'input int    InpCrkLZ2N  = 3;      //   ...most parts above the start\n'
     'input double InpCrkLGrow = 10.0;   // Crooks L: at a new best the base grows by this % of the profit\n'
     'input double InpCrkLGrowX = 4.0;   //   ...base at most this many x\n')
sub1('input ENUM_LADDER InpLadder = LAD_OFF; // Profit ladder (Crooks F-J): risk appetite once the profit target is reached\n',
     'input ENUM_LADDER InpLadder = LAD_OFF; // Profit ladder (Crooks F-K): risk appetite once the profit target is reached\n')

# ---- families, ladder guard
sub1('bool   CrkCFam()  { return InpRec == REC_CRC || (InpRec >= REC_CRE && InpRec <= REC_CRJ); }',
     'bool   CrkCFam()  { return InpRec == REC_CRC || (InpRec >= REC_CRE && InpRec <= REC_CRL); }   // v5.0: + K, L')
sub1('bool   LadFam()   { return InpRec >= REC_CRF && InpRec <= REC_CRJ; }',
     'bool   LadFam()   { return (InpRec >= REC_CRF && InpRec <= REC_CRJ) || InpRec == REC_CRK; }   // v5.0: + K')
sub1('bool   LadGuard() { return LadOn() && totalNet - gNet0 <= 0; }',
     'bool   LadGuard() { return LadOn() && InpRec != REC_CRK && totalNet - gNet0 <= 0; }   // v5.0: Crooks K has its own zone below the start instead')
sub1('   if(!LadFam()) return lv + " | only with Crooks F, G, H, I or J";',
     '   if(!LadFam()) return lv + " | only with Crooks F, G, H, I, J or K";')

# ---- base: Size By
sub1('double BookBase() { return InpSizeMode == PSZ_USD ? InpBaseRisk : (exBase > 0 ? exBase : InpBaseRisk); }',
     '//--- v5.0 SIZE BY: with Profit the base and the amounts a recovery rule adds are the win at the final TP (the risk = amount / its R)\n'
     'bool   SizeProfit() { return InpSizeBy == SZB_PROFIT; }\n'
     'double BookBase() { return InpSizeMode == PSZ_USD && !SizeProfit() ? InpBaseRisk : (exBase > 0 ? exBase : SizeProfit() && InpSizeMode != PSZ_LOT && ExitR() > 0 ? InpBaseRisk / ExitR() : InpBaseRisk); }')
sub1('double ShowBase() { return InpSizeMode == PSZ_USD ? InpBaseRisk : BaseRisk(trRisk); }\n',
     'double ShowBase() { double b = InpSizeMode == PSZ_USD ? InpBaseRisk : BaseRisk(trRisk); return SizeProfit() && InpSizeMode != PSZ_LOT && ExitR() > 0 ? b / ExitR() : b; }\n')
sub1('   return "base " + DoubleToString(LadBase(ShowBase(), cush), 2) + (InpSizeMode == PSZ_PCT ? " (" + DoubleToString(InpEqPct, 2) + "% of equity)" : "");\n',
     '   double b = LadBase(ShowBase(), cush);\n'
     '   string pct = InpSizeMode == PSZ_PCT ? " (" + DoubleToString(InpEqPct, 2) + "% of equity" + (SizeProfit() ? " as the win" : "") + ")" : "";\n'
     '   if(SizeProfit() && InpSizeMode != PSZ_LOT) return "base risk " + DoubleToString(b, 2) + " = win " + DoubleToString(b * ExitR(), 2) + " at TP" + IntegerToString((int)gpExitAt) + pct;   // v5.0\n'
     '   return "base " + DoubleToString(b, 2) + pct;\n')

# ---- v5.0 helpers (after LadTxt)
sub1('''   return lv + " | lock " + DoubleToString(lam * crkPk, 2) + " | cushion " + DoubleToString(cush, 2) + " | base " + DoubleToString(b, 2);
}
''', '''   return lv + " | lock " + DoubleToString(lam * crkPk, 2) + " | cushion " + DoubleToString(cush, 2) + " | base " + DoubleToString(b, 2);
}
//--- v5.0 Crooks K: below the start (the closed profit since the restart is under 0): after a win the careful size, after a loss the E / I lot
bool   KZone() { return InpRec == REC_CRK && totalNet - gNet0 < 0; }
double KCare(double base, double exitR, double kRisk)
{
   if(InpCrkKMode == CKM_USD) return SizeProfit() && exitR > 0 ? InpCrkKUsd / exitR : InpCrkKUsd;
   if(InpCrkKMode == CKM_PCT) return base * InpCrkKPct / 100.0;
   return kRisk > 0 ? kRisk : base;                     // the careful lots' stop-out loss on this setup (0 = not known: the base)
}
//--- v5.0 Crooks L: at a new best (the closed profit since the restart at its high; also at the start) the base grows with the profit
double LBase(double base, double exitR)
{
   double nr = totalNet - gNet0;
   if(InpRec != REC_CRL || nr < crkPk) return base;
   double g = InpCrkLGrow / 100.0 * nr / (SizeProfit() && exitR > 0 ? exitR : 1.0);
   return base + MathMin((MathMax(1.0, InpCrkLGrowX) - 1.0) * base, MathMax(0.0, g));
}
//--- v5.0 Crooks L: the parts of a loss just booked, from the drawdown after it (below the start: from the start; above it: from the best)
int LParts()
{
   double b = BookBase(), nr = totalNet - gNet0, dd = 0, step = 0; int mx = 1;
   if(nr < 0) { dd = -nr; step = InpCrkLZ1 * b; mx = InpCrkLZ1N > 1 ? InpCrkLZ1N : 1; }
   else if(nr < crkPk) { dd = crkPk - nr; step = InpCrkLZ2 * b; mx = InpCrkLZ2N > 1 ? InpCrkLZ2N : 1; }
   else return 1;
   if(step <= 0) return 1;
   double np = MathCeil(dd / step - 1e-9);
   if(np > mx) np = mx;
   if(np < 1) np = 1;
   return (int)np;
}
''')

# ---- TP1 rule off in the K zone; N / parts for L
sub1('   if(!InpCrkT1 || (gpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext() || CrkHedgeNow() || LadGuard()) return 0;   // v4.6: not while the ladder\'s guard is on',
     '   if(!InpCrkT1 || (gpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext() || CrkHedgeNow() || LadGuard() || KZone()) return 0;   // v4.6: not while the ladder\'s guard is on (v5.0: nor in the Crooks K zone)')
sub1('int CrkNp() { return InpCrkCnOn ? MathMax(1, InpCrkCn) : 1; }\n'
     'int CrkParts() { int np = CrkNp(); return (crkP < 1 || crkP > np) ? np : crkP; }\n',
     'int CrkNp() { return InpRec == REC_CRL ? 1 : InpCrkCnOn ? MathMax(1, InpCrkCn) : 1; }   // v5.0: Crooks L takes its parts from the drawdown\n'
     'int CrkParts()\n'
     '{\n'
     '   if(InpRec == REC_CRL) { int mx = InpCrkLZ1N > InpCrkLZ2N ? InpCrkLZ1N : InpCrkLZ2N; if(mx < 1) mx = 1; return crkP < 1 ? 1 : crkP > mx ? mx : crkP; }\n'
     '   int np = CrkNp(); return (crkP < 1 || crkP > np) ? np : crkP;\n'
     '}\n')

# ---- Crooks limits / waiting lot
sub1('   else if(InpRec == REC_CRJ && InpCrkJX > 0) r = MathMax(base, r * MathMax(0.0, 1.0 - MathMax(0.0, crkPk - (totalNet - gNet0)) / (InpCrkJX * base)));',
     '   else if((InpRec == REC_CRJ || InpRec == REC_CRK) && InpCrkJX > 0) r = MathMax(base, r * MathMax(0.0, 1.0 - MathMax(0.0, crkPk - (totalNet - gNet0)) / (InpCrkJX * base)));   // v5.0: K too')
sub1('   else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI) && minRisk > 0) r = MathMin(base, minRisk);   // v4.5 Crooks E / I: the small lot while waiting',
     '   else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL) && minRisk > 0) r = MathMin(base, minRisk);   // v4.5 Crooks E / I (v5.0: L): the small lot while waiting')

# ---- NextRisk
sub1('''//--- the $ risk of the next trade; minRisk: the stop-out loss of the 0.01 lot (Crooks E / I lot) on this setup (0 = not known: the base is used)
double NextRisk(double exitR, bool canTake = true, double minRisk = 0)
{
   double base = BaseRisk(trRisk), r = base;          // v4.7: the base of this setup (Position size)
   gBase = base;
   if(base <= 0) return 0;                            // no base: size 0 (never a zero divide below)
   double stepBase = 0;
''', '''//--- the $ risk of the next trade; minRisk: the stop-out loss of the 0.01 lot (Crooks E / I lot) on this setup (0 = not known: the base is used);
//--- kRisk: the stop-out loss of the Crooks K careful lots on this setup (0 = not known: the base)
double NextRisk(double exitR, bool canTake = true, double minRisk = 0, double kRisk = 0)
{
   double base = BaseRisk(trRisk);                    // v4.7: the base of this setup (Position size)
   if(SizeProfit() && InpSizeMode != PSZ_LOT && exitR > 0) base = base / exitR;   // v5.0: the base is the win at the final TP
   double r = base;
   gBase = base;
   if(base <= 0) return 0;                            // no base: size 0 (never a zero divide below)
   double dv = SizeProfit() && exitR > 0 ? exitR : 1.0;   // v5.0: the amounts a rule adds are wins at the final TP (Risk: 1)
   double stepBase = 0;
''')
sub1('''   else if(netR >= 200) stepBase = 200.0 / 3.0;
   double baseC = InpRec == REC_CS ? MathMax(base, InpCapOn ? MathMin(stepBase, InpHardCap) : stepBase) : base;''',
     '''   else if(netR >= 200) stepBase = 200.0 / 3.0;
   stepBase = stepBase / dv;                          // v5.0: a base amount
   double baseC = InpRec == REC_CS ? MathMax(base, InpCapOn ? MathMin(stepBase, InpHardCap) : stepBase) : base;''')
sub1('   int oscNeed = exitR > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((base - oscP) / (base * exitR)))) : 1;   // v4.7: no int overflow\n',
     '   double oscGoal = SizeProfit() ? base * exitR : base;   // v5.0: with Profit the cycle goal is one base win\n'
     '   int oscNeed = exitR > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((oscGoal - oscP) / (base * exitR)))) : 1;   // v4.7: no int overflow\n')
sub1('      case REC_ALL:   r = base + recPool; break;\n'
     '      case REC_SPLIT: r = base + recPool / InpRecN; break;\n'
     '      case REC_PART:  r = base + recPool * InpRecPct / 100.0; break;\n',
     '      case REC_ALL:   r = base + recPool / dv; break;\n'
     '      case REC_SPLIT: r = base + recPool / InpRecN / dv; break;\n'
     '      case REC_PART:  r = base + recPool * InpRecPct / 100.0 / dv; break;\n')
sub1('      case REC_STEP:  r = base + InpRecStep * recLosses; break;\n',
     '      case REC_STEP:  r = base + InpRecStep * recLosses / dv; break;\n')
sub1('      case REC_CS:    r = MathMax(baseC, carried / InpCSplit); break;\n',
     '      case REC_CS:    r = MathMax(baseC, carried / InpCSplit / dv); break;\n')
sub1('      case REC_DELAY: r = recLosses >= InpDelayN ? base + recPool / InpRecN : base; break;\n'
     '      case REC_EQPCT: r = AccountInfoDouble(ACCOUNT_EQUITY) * InpEqPct / 100.0; break;\n',
     '      case REC_DELAY: r = recLosses >= InpDelayN ? base + recPool / InpRecN / dv : base; break;\n'
     '      case REC_EQPCT: r = AccountInfoDouble(ACCOUNT_EQUITY) * InpEqPct / 100.0 / dv; break;\n')
sub1('''      case REC_CRJ:
      {
         r = CrkRule(base, exitR, minRisk);''', '''      case REC_CRJ:
      case REC_CRK:
      case REC_CRL:
      {
         r = CrkRule(LBase(base, exitR), exitR, minRisk);   // v5.0 Crooks L: the base grows at a new best''')
sub1('''            r = LadGuard() ? (minRisk > 0 ? MathMin(base, minRisk) : base) : MathMin(CrkRule(lb, exitR, minRisk), r + gam * cush / CrkT1Mult());
         }
''', '''            r = LadGuard() ? (minRisk > 0 ? MathMin(base, minRisk) : base) : MathMin(CrkRule(lb, exitR, minRisk), r + gam * cush / CrkT1Mult());
         }
         if(KZone()) r = crkW ? KCare(base, exitR, kRisk) : (minRisk > 0 ? MathMin(base, minRisk) : base);   // v5.0 Crooks K below the start
''')

# ---- LotRisk (MinLotRisk generalised; same arithmetic)
sub1('''double MinLotRisk(double stopDist)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(step <= 0) step = vmin > 0 ? vmin : 0.01;
   double lots = MathCeil(MathMax(InpCrkELot, vmin) / step - 1e-9) * step;
   return lots * ((stopDist + MathMax(CostSpr(), 0)) / ts * tv + InpCommLot);
}
''', '''double LotRisk(double lotsIn, double stopDist)        // v5.0: any lot (the E / I lot, the Crooks K careful lots)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(step <= 0) step = vmin > 0 ? vmin : 0.01;
   double lots = MathCeil(MathMax(lotsIn, vmin) / step - 1e-9) * step;
   return lots * ((stopDist + MathMax(CostSpr(), 0)) / ts * tv + InpCommLot);
}
double MinLotRisk(double stopDist) { return LotRisk(InpCrkELot, stopDist); }
''')

# ---- TakeSetup
sub1('''   double minR = (InpRec == REC_CRE || InpRec == REC_CRI || LadOn()) ? MinLotRisk(trRisk) : 0;   // v4.5 Crooks E / I, v4.6 ladder guard: the 0.01 lot on this setup
   double rAmt = NextRisk(ExitR(), canTake, minR);''',
     '''   double minR = (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL || LadOn()) ? MinLotRisk(trRisk) : 0;   // v4.5 Crooks E / I, v4.6 ladder guard, v5.0 K / L: the 0.01 lot on this setup
   double kR = InpRec == REC_CRK && InpCrkKMode == CKM_LOTS ? LotRisk(InpCrkKLots, trRisk) : 0;   // v5.0 Crooks K: the careful lots on this setup
   double rAmt = NextRisk(ExitR(), canTake, minR, kR);''')

# ---- BookClosed
sub1('   if(oscP >= BookBase()) { oscU = 1; oscP = 0; } else if(win) oscU++;\n',
     '   if(oscP >= (SizeProfit() ? BookBase() * ExitR() : BookBase())) { oscU = 1; oscP = 0; } else if(win) oscU++;   // v5.0: with Profit the goal is one base win\n')
sub1('      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = CrkNp(); }\n',
     '      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = InpRec == REC_CRL ? LParts() : CrkNp(); }\n')
sub1('      crkN++; crkP = !win ? CrkNp() : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts();   // Crooks C over N wins: a loss starts the parts again\n',
     '      crkN++; crkP = !win ? (InpRec == REC_CRL ? LParts() : CrkNp()) : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts();   // Crooks C over N wins: a loss starts the parts again (v5.0 L: from the drawdown)\n')

# ---- table
sub1('''                 InpRec == REC_CRJ ? ", drawdown " + DoubleToString(MathMax(0.0, crkPk - (totalNet - gNet0)), 2) : "";
   string kWait = InpRec == REC_CRE || InpRec == REC_CRI ? " | " + DoubleToString(InpCrkELot, 2) + " lot, waiting for a win" : " | base, waiting for a win";''',
     '''                 InpRec == REC_CRJ || InpRec == REC_CRK ? ", drawdown " + DoubleToString(MathMax(0.0, crkPk - (totalNet - gNet0)), 2) : "";
   string kWait = InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL ? " | " + DoubleToString(InpCrkELot, 2) + " lot, waiting for a win" : " | base, waiting for a win";
   double nrT = totalNet - gNet0;                       // v5.0 Crooks K / L: where the closed profit is (since the restart)
   string kCare = InpCrkKMode == CKM_USD ? DoubleToString(InpCrkKUsd, 2) + (SizeProfit() ? " win" : "") : InpCrkKMode == CKM_PCT ? DoubleToString(InpCrkKPct, 0) + "% of the base" : DoubleToString(InpCrkKLots, 2) + " lot";
   string kZn = InpRec == REC_CRK ? (KZone() ? " | below the start: " + (crkW ? "careful " + kCare + " after a win" : DoubleToString(InpCrkELot, 2) + " lot until a win") : " | above the start (Crooks J)") :
                InpRec == REC_CRL ? (nrT < 0 ? " | below the start" : nrT < crkPk ? " | below the best" : " | at the best, base " + DoubleToString(LBase(ShowBase(), ExitR()), 2)) : "";''')
sub1('''                 (CrkCFam() ? (kRec ? " | recovery trade" + (CrkNp() > 1 ? ", part " + IntegerToString(CrkNp() - CrkParts() + 1) + " of " + IntegerToString(CrkNp()) : "") + kLim : (crkL > 0 ? kWait : " | base")) : " | trade " + IntegerToString(crkN + 1) + (kRec ? " recovery" : " base")) + (InpRec == REC_CRB ? " | split " + IntegerToString(InpCSplit) : "")''',
     '''                 (CrkCFam() ? (kRec ? " | recovery trade" + (CrkNp() > 1 ? ", part " + IntegerToString(CrkNp() - CrkParts() + 1) + " of " + IntegerToString(CrkNp()) : "") +
                  (InpRec == REC_CRL ? ", " + IntegerToString(CrkParts()) + (CrkParts() == 1 ? " part" : " parts") + " to go" : "") + kLim : (crkL > 0 ? kWait : " | base")) + kZn : " | trade " + IntegerToString(crkN + 1) + (kRec ? " recovery" : " base")) + (InpRec == REC_CRB ? " | split " + IntegerToString(InpCSplit) : "")''')

# ---- input checks
sub1('''   if((InpRec == REC_CRE || InpRec == REC_CRI) && InpCrkELot <= 0) { Print("Crooks E / I: the lot while waiting for a win must be above 0."); return INIT_PARAMETERS_INCORRECT; }''',
     '''   if((InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL) && InpCrkELot <= 0) { Print("Crooks E / I / K / L: the lot while waiting for a win must be above 0."); return INIT_PARAMETERS_INCORRECT; }''')
sub1('''   if(InpRec == REC_CRJ && InpCrkJX <= 0) { Print("Crooks J: the drawdown must be above 0."); return INIT_PARAMETERS_INCORRECT; }''',
     '''   if((InpRec == REC_CRJ || InpRec == REC_CRK) && InpCrkJX <= 0) { Print("Crooks J / K: the drawdown must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRK && ((InpCrkKMode == CKM_LOTS && InpCrkKLots <= 0) || (InpCrkKMode == CKM_USD && InpCrkKUsd <= 0) || (InpCrkKMode == CKM_PCT && InpCrkKPct <= 0)))
   { Print("Crooks K: the careful size must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRL && (InpCrkLZ1 <= 0 || InpCrkLZ2 <= 0 || InpCrkLZ1N < 1 || InpCrkLZ2N < 1 || InpCrkLGrow < 0 || InpCrkLGrowX < 1))
   { Print("Crooks L: the part steps must be above 0, the most parts 1 or more, the growth 0 or more and its limit 1 x or more."); return INIT_PARAMETERS_INCORRECT; }
   if(SizeProfit() && ExitR() <= 0) { Print("Size by Profit: the final TP must be above 0 R."); return INIT_PARAMETERS_INCORRECT; }''')

assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(B + 'safe/AuctionRetestEA.mq5', 'w').write(s)
print('EA v5.0 written', s.count('\n'), 'lines')
