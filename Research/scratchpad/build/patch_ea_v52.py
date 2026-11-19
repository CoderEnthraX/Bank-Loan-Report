"""EA v5.2 (2026-11-19, spec v50/SPEC_v50.md section 6): Crooks X = Crooks E with the loss to win back set after every close from the levels
(below the start: the gap to it; above it: the gap to the next InpCrkXStep level, at most the best; a win into another step: N parts again),
and an optional per-trade limit. Applied to build/bak/AuctionRetestEA_v51.mq5 -> build/safe/AuctionRetestEA.mq5."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
s = open(B + 'bak/AuctionRetestEA_v51.mq5').read()


def sub1(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:100], s.count(a))
    s = s.replace(a, b)


def box(lines):
    return ''.join('//| ' + x.ljust(64) + ' |\n' for x in lines)


sub1('#property version   "5.10"', '#property version   "5.20"')
sub1(box(['amount itself (v5.0 came short by the spread and commission).']),
     box(['amount itself (v5.0 came short by the spread and commission).']) + box([
         'v5.2: Crooks X: Crooks E with the loss to win back taken from',
         'the levels: below the start the gap to it, above it the gap to',
         'the next step ($1,000 by default) up to the best; N trades each.']))
sub1('TblAdd("AUCTION RETEST", "EA v5.1", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v5.2", white, C\'61,143,214\');')
sub1('   REC_CRL   = 29  // Crooks L (0.01 lot until a win, the loss split by the drawdown)\n',
     '   REC_CRL   = 29, // Crooks L (0.01 lot until a win, the loss split by the drawdown)\n'
     '   REC_CRX   = 30  // Crooks X (Crooks E, the loss = the gap to the start / the next step)\n')
sub1('''enum ENUM_CRK_K { CKM_LOTS = 0,  // Lots''', '''enum ENUM_CRK_XLIM { CXL_CAP   = 0,   // Hard cap only
                     CXL_TRADE = 1 }; // Per-trade limit ($)
enum ENUM_CRK_K { CKM_LOTS = 0,  // Lots''')
sub1('input double InpCrkLGrowX = 4.0;   //   ...base at most this many x\n',
     'input double InpCrkLGrowX = 4.0;   //   ...base at most this many x\n'
     'input double InpCrkXStep  = 1000.0; // Crooks X: above the start, win back up to the next level every this much (account currency)\n'
     'input ENUM_CRK_XLIM InpCrkXLim = CXL_CAP; // Crooks X: limit of a recovery trade\n'
     'input double InpCrkXLimUsd = 500.0; //   ...per-trade limit: a recovery trade risks at most this (account currency, the loss at the stop)\n')
sub1('bool   CrkCFam()  { return InpRec == REC_CRC || (InpRec >= REC_CRE && InpRec <= REC_CRL); }   // v5.0: + K, L',
     'bool   CrkCFam()  { return InpRec == REC_CRC || (InpRec >= REC_CRE && InpRec <= REC_CRX); }   // v5.0: + K, L; v5.2: + X')
# the per-trade limit (with the Crooks F limits)
sub1('   if(InpRec == REC_CRF || InpRec == REC_CRI) r = MathMin(r, MathMax(1.0, InpCrkFK) * base / mul);\n',
     '   if(InpRec == REC_CRF || InpRec == REC_CRI) r = MathMin(r, MathMax(1.0, InpCrkFK) * base / mul);\n'
     '   else if(InpRec == REC_CRX && InpCrkXLim == CXL_TRADE) r = MathMin(r, MathMax(base, InpCrkXLimUsd) / mul);   // v5.2 Crooks X: the per-trade limit\n')
sub1('   else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL) && minRisk > 0) r = MathMin(base, minRisk);',
     '   else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL || InpRec == REC_CRX) && minRisk > 0) r = MathMin(base, minRisk);')
sub1('      case REC_CRL:\n      {\n', '      case REC_CRL:\n      case REC_CRX:\n      {\n')
# the levels
sub1('//--- v5.0 Crooks L: the parts of a loss just booked', '''//--- v5.2 Crooks X: the step the closed profit nr is in (-1 below the start), and the loss to win back from the levels: below the start the gap to it,
//--- above it the gap to the next InpCrkXStep level (at most the best crkPk); at the best nothing (0.005: a fraction of a cent under a level counts as at it)
int    XIdx(double nr) { return nr < -0.005 ? -1 : (int)MathFloor((nr + 0.005) / MathMax(0.01, InpCrkXStep)); }
double XTarget(double nr)
{
   if(nr < -0.005) return -nr;
   if(nr >= crkPk - 0.005) return 0;
   double xs = MathMax(0.01, InpCrkXStep);
   return MathMax(0.0, MathMin(crkPk, (MathFloor((nr + 0.005) / xs) + 1) * xs) - nr);
}
//--- v5.0 Crooks L: the parts of a loss just booked''')
sub1('''   double gCush = 0;
   if(InpRec == REC_CRG && InpCrkGX > 0)''', '''   bool xNew = false;                                  // v5.2 Crooks X: the loss is the gap to the level; a win into another step: N parts again
   if(InpRec == REC_CRX) { double nrA = totalNet - gNet0; crkL = XTarget(nrA); xNew = win && XIdx(nrA - exPnl) != XIdx(nrA); }
   double gCush = 0;
   if(InpRec == REC_CRG && InpCrkGX > 0)''')
sub1('''      crkN++; crkP = !win ? (InpRec == REC_CRL ? LParts() : CrkNp()) : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts();   // Crooks C over N wins: a loss starts the parts again (v5.0 L: from the drawdown)
''', '''      crkN++; crkP = !win ? (InpRec == REC_CRL ? LParts() : CrkNp()) : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts();   // Crooks C over N wins: a loss starts the parts again (v5.0 L: from the drawdown)
      if(xNew) crkP = CrkNp();                          // v5.2 Crooks X: a new step is won back in N trades
''')
# table
sub1('   string kWait = InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL ? " | "',
     '   string kWait = InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL || InpRec == REC_CRX ? " | "')
sub1('''                InpRec == REC_CRL ? (nrT < 0 ? " | below the start" : nrT < crkPk ? " | below the best" : " | at the best, base " + DoubleToString(LBase(ShowBase(), SizeProfit() ? PDiv(ExitR()) : 1.0), 2)) : "";''',
     '''                InpRec == REC_CRL ? (nrT < 0 ? " | below the start" : nrT < crkPk ? " | below the best" : " | at the best, base " + DoubleToString(LBase(ShowBase(), SizeProfit() ? PDiv(ExitR()) : 1.0), 2)) :
                InpRec == REC_CRX ? (crkL <= 0 ? "" : nrT < -0.005 ? " | below the start: back to it" : " | up to " + DoubleToString(MathMin(crkPk, (MathFloor((nrT + 0.005) / MathMax(0.01, InpCrkXStep)) + 1) * MathMax(0.01, InpCrkXStep)), 0) + " above the start") +
                                    (InpCrkXLim == CXL_TRADE ? ", at most " + DoubleToString(InpCrkXLimUsd, 0) + " a trade" : "") : "";''')
# setup + checks
sub1('   double minR = (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL || LadOn()) ? MinLotRisk(trRisk) : 0;',
     '   double minR = (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL || InpRec == REC_CRX || LadOn()) ? MinLotRisk(trRisk) : 0;')
sub1('   if((InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL) && InpCrkELot <= 0) { Print("Crooks E / I / K / L: the lot',
     '   if(InpRec == REC_CRX && (InpCrkXStep <= 0 || (InpCrkXLim == CXL_TRADE && InpCrkXLimUsd <= 0))) { Print("Crooks X: the step and the per-trade limit must be above 0."); return INIT_PARAMETERS_INCORRECT; }\n'
     '   if((InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL || InpRec == REC_CRX) && InpCrkELot <= 0) { Print("Crooks E / I / K / L / X: the lot')
assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(B + 'safe/AuctionRetestEA.mq5', 'w').write(s)
print('EA v5.2 written', s.count('\n'), 'lines')
