"""EA v4.7: Position Size (Fixed $ risk / Fixed lots / % of equity at risk), the same as Auction_Retest_Strategy.pine v4.7.
The loss recovery sizes every trade from the base of its setup; the trade's base is kept for its booking (Oscar's Grind, Crooks G) and in the
restart memory. Fixed $ risk (default) gives the same numbers as v4.6. A base of 0 (no equity, no tick value) is size 0, never a zero divide."""
import sys
p = sys.argv[1]; s = open(p, encoding='ascii').read()
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:90], s.count(old)); s = s.replace(old, new)
# header and version
rep('''//| v4.6: PROFIT LADDER for Crooks F - J: after a first profit the   |
//| risk grows, paid only from the profit above a lock (5 levels).   |
''', '''//| v4.6: PROFIT LADDER for Crooks F - J: after a first profit the   |
//| risk grows, paid only from the profit above a lock (5 levels).   |
//| v4.7: POSITION SIZE: Fixed $ risk, Fixed lots or % of equity at  |
//| risk; the loss recovery sizes every trade from that base.        |
''')
rep('#property version   "4.60"', '#property version   "4.70"')
rep('TblAdd("AUCTION RETEST", "EA v4.6", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v4.7", white, C\'61,143,214\');')
# the enum and the inputs
rep('''enum ENUM_SMALL_LOT { SMALLL_MIN  = 0,  // Trade the minimum lot (risks more)
                      SMALLL_SKIP = 1 };// Skip the trade
''', '''enum ENUM_SMALL_LOT { SMALLL_MIN  = 0,  // Trade the minimum lot (risks more)
                      SMALLL_SKIP = 1 };// Skip the trade
enum ENUM_SIZE_MODE { PSZ_USD = 0,     // Fixed $ risk (Base risk per trade)
                      PSZ_LOT = 1,     // Fixed lots (Base lots)
                      PSZ_PCT = 2 };   // % of equity at risk (Risk % of equity)
''')
rep('''input group "RISK AND POSITION SIZE"
input double InpBaseRisk = 50.0;   // Base risk per trade (account currency)
''', '''input group "RISK AND POSITION SIZE"
input ENUM_SIZE_MODE InpSizeMode = PSZ_USD; // Position size: the base trade (the loss recovery sizes every trade from it)
input double InpBaseRisk = 50.0;   // Base risk per trade (account currency; Fixed $ risk)
input double InpBaseLots = 0.01;   // Base lots (Fixed lots)
input double InpEqPct    = 1.0;    // Risk % of equity (% of equity at risk, and the % of equity rule)
''')
rep('input double InpEqPct    = 1.0;    // % of equity (% mode)\n', '')
# the trade's base
rep('double   exLots = 0, exRiskAmt = 0, exCostPx = 0, exPnl = 0;\n',
    'double   exLots = 0, exRiskAmt = 0, exCostPx = 0, exPnl = 0;\n'
    'double   gBase = 0;    // v4.7: the base risk of the setup being sized (NextRisk); the trade keeps it in exBase\n'
    'double   exBase = 0;   // v4.7: the base risk of the EA\'s trade (its booking: Oscar\'s Grind, Crooks G)\n')
# the ladder at a given base, and the base helpers
rep('''double LadBase(double &cush)
{
   cush = 0;
   if(!LadOn()) return InpBaseRisk;
   double lam = 0, phi = 0, bmax = 0, gam = 0; LadPar(lam, phi, bmax, gam);
   cush = MathMax(0.0, totalNet - lam * crkPk);
   return InpBaseRisk + MathMin((bmax - 1.0) * InpBaseRisk, phi * cush);
}''', '''double LadBase(double base, double &cush)
{
   cush = 0;
   if(!LadOn()) return base;
   double lam = 0, phi = 0, bmax = 0, gam = 0; LadPar(lam, phi, bmax, gam);
   cush = MathMax(0.0, totalNet - lam * crkPk);
   return base + MathMin((bmax - 1.0) * base, phi * cush);
}
//--- v4.7 position size: the base trade's $ risk on a setup with this stop distance: Fixed $ risk, the Fixed lots' stop-out loss (spread and
//--- commission included, like LotsFor), or % of the equity. 0 = no base (no equity, no tick value): the setup gets size 0
double BaseRisk(double stopDist)
{
   if(InpSizeMode == PSZ_PCT) return MathMax(0.0, AccountInfoDouble(ACCOUNT_EQUITY)) * InpEqPct / 100.0;
   if(InpSizeMode == PSZ_LOT)
   {
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
      if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
      return InpBaseLots * ((stopDist + MathMax(CostSpr(), 0)) / ts * tv + InpCommLot);
   }
   return InpBaseRisk;
}
//--- the base of the EA's trade for its booking (Fixed $ risk: the input, as in v4.6)
double BookBase() { return InpSizeMode == PSZ_USD ? InpBaseRisk : (exBase > 0 ? exBase : InpBaseRisk); }
//--- the base shown in the table (Fixed lots: on the last setup's stop)
double ShowBase() { return InpSizeMode == PSZ_USD ? InpBaseRisk : BaseRisk(trRisk); }
string BaseTxt(double &cush)
{
   cush = 0;
   if(InpSizeMode == PSZ_LOT && !LadOn()) return "base " + DoubleToString(InpBaseLots, 2) + " lot";
   return "base " + DoubleToString(LadBase(ShowBase(), cush), 2) + (InpSizeMode == PSZ_PCT ? " (" + DoubleToString(InpEqPct, 2) + "% of equity)" : "");
}''')
rep('   double b = LadBase(cush); LadPar(lam, phi, bmax, gam);\n', '   double b = LadBase(ShowBase(), cush); LadPar(lam, phi, bmax, gam);\n')
# NextRisk: the base of this setup
rep('''double NextRisk(double exitR, bool canTake = true, double minRisk = 0)
{
   double base = InpBaseRisk, r = base;
''', '''double NextRisk(double exitR, bool canTake = true, double minRisk = 0)
{
   double base = BaseRisk(trRisk), r = base;          // v4.7: the base of this setup (Position size)
   gBase = base;
   if(base <= 0) return 0;                            // no base: size 0 (never a zero divide below)
''')
rep('            double lb = LadBase(cush); LadPar(lam, phi, bmax, gam);\n', '            double lb = LadBase(base, cush); LadPar(lam, phi, bmax, gam);\n')
# Oscar's Grind units: clamped before the int cast (a tiny base, e.g. % of equity on an almost empty account, would overflow a 32-bit int)
rep('   int oscNeed = exitR > 0 ? (int)MathMax(1, MathCeil((base - oscP) / (base * exitR))) : 1;\n',
    '   int oscNeed = exitR > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((base - oscP) / (base * exitR)))) : 1;   // v4.7: no int overflow\n')
# the table
rep('(InpRec == REC_CRG ? " (at most " + DoubleToString(InpCrkGX * InpBaseRisk, 0) + ")" : "")', '(InpRec == REC_CRG ? " (at most " + DoubleToString(InpCrkGX * ShowBase(), 0) + ")" : "")')
rep(': "base " + DoubleToString(LadBase(lCu), 2), white, cell);', ': BaseTxt(lCu), white, cell);')
# the trade keeps its base
rep('   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot);\n',
    '   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot); exBase = gBase;\n')
# booking
rep('   if(oscP >= InpBaseRisk) { oscU = 1; oscP = 0; } else if(win) oscU++;\n', '   if(oscP >= BookBase()) { oscU = 1; oscP = 0; } else if(win) oscU++;\n')
rep('crkL = MathMin(crkL, InpCrkGX * LadBase(gCush));', 'crkL = MathMin(crkL, InpCrkGX * LadBase(BookBase(), gCush));')
# restart memory
rep('IoD("xr", exRiskAmt);', 'IoD("xr", exRiskAmt); IoD("xb", exBase);')
# input checks
rep('''   if(InpSpread < 0 || InpCommLot < 0) { Print("Spread and commission must be 0 or more."); return INIT_PARAMETERS_INCORRECT; }
''', '''   if(InpSpread < 0 || InpCommLot < 0) { Print("Spread and commission must be 0 or more."); return INIT_PARAMETERS_INCORRECT; }
   if((InpSizeMode == PSZ_USD && InpBaseRisk <= 0) || (InpSizeMode == PSZ_LOT && InpBaseLots <= 0) || (InpSizeMode == PSZ_PCT && InpEqPct <= 0))
   { Print("Position size: the base risk, base lots or risk % of equity must be above 0."); return INIT_PARAMETERS_INCORRECT; }
''')
import re
left = [s.count('\n', 0, m.start()) + 1 for m in re.finditer(r'InpBaseRisk', s)]
print('InpBaseRisk now at lines', left)
open(p, 'w', encoding='ascii').write(s); print('patched', p)
