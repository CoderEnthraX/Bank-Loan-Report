"""EA v4.6 (asked 2026-11-14): the PROFIT LADDER, a risk-appetite slider for Crooks F - J (Off / Low / Medium / High / Extra high / Max).
Before the profit target (InpLadT, $1,000) the rule trades as now. Once the highest closed profit (crkPk) has reached it:
  lock      L = lam x highest closed profit; cushion C = max(0, closed profit - L): the profit that may be put at extra risk
  base      B = base + min((most - 1) x base, share x C): the rule then works with B (its waiting trades, recovery, limits)
  limit     a trade risks at most the plain rule's risk + gam x C (its real stop-out loss): the extra risk is paid from the cushion only,
            and the ladder never risks less than the plain rule
  guard     while the closed profit is at or below 0 (back at the start), every trade is the 0.01 lot (no TP1 rule) until it is above 0
Levels (lock, share, most x, gam): Low 0.8 / 0.10 / 2 / 0.25, Medium 0.7 / 0.15 / 3 / 0.30, High 0.6 / 0.20 / 5 / 0.35, Extra high
0.5 / 0.25 / 8 / 0.40, Max 0.4 / 0.30 / 12 / 0.50. Crooks G's limit is X x the ladder base. No new saved state (totalNet, crkPk).
Gold study: gold/crooks_ladder.py (round 1, strict floor), crooks_ladder2.py, crooks_ladder3.py; reference gold/recovery.py, crooks_tp1.py.
Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''//| v4.5: Crooks E - J: Crooks C with smaller trades or a limit on   |
//| the recovery trade, so a long losing run costs less.             |
''', '''//| v4.5: Crooks E - J: Crooks C with smaller trades or a limit on   |
//| the recovery trade, so a long losing run costs less.             |
//| v4.6: PROFIT LADDER for Crooks F - J: after a first profit the   |
//| risk grows, paid only from the profit above a lock (5 levels).   |
''')
rep('''#property version   "4.50"''', '''#property version   "4.60"''')
rep('''input group "LOSS RECOVERY"
''', '''enum ENUM_LADDER { LAD_OFF   = 0,  // Off
                   LAD_LOW   = 1,  // Low (keeps 80% of the best profit, base up to 2x)
                   LAD_MED   = 2,  // Medium (keeps 70%, base up to 3x)
                   LAD_HIGH  = 3,  // High (keeps 60%, base up to 5x)
                   LAD_XHIGH = 4,  // Extra high (keeps 50%, base up to 8x)
                   LAD_MAX   = 5   // Max (keeps 40%, base up to 12x)
};
input group "LOSS RECOVERY"
''')
rep('''input double InpCrkJX    = 20.0;   // Crooks J: drawdown (x the base risk) at which a recovery trade is back to the base risk
''', '''input double InpCrkJX    = 20.0;   // Crooks J: drawdown (x the base risk) at which a recovery trade is back to the base risk
input ENUM_LADDER InpLadder = LAD_OFF; // Profit ladder (Crooks F-J): risk appetite once the profit target is reached
input double InpLadT     = 1000.0; //   ...profit target before the risk goes up ($, closed profit of this EA)
''')
rep('''//--- Crooks TP1 rule (exit at TP1, or any exit with InpCrkT1Any; recovery trades): the part p closed at TP1 banks the recovery amount, the rest runs to TP2.''',
    '''//--- v4.6 PROFIT LADDER (Crooks F - J): once the highest closed profit has reached InpLadT, the trades grow with the profit above a lock and the
//--- extra risk is paid from that profit only; back at the start (closed profit 0 or less) every trade is the 0.01 lot until it is in profit again
bool   LadFam()   { return InpRec >= REC_CRF && InpRec <= REC_CRJ; }
bool   LadOn()    { return InpLadder != LAD_OFF && LadFam() && InpLadT > 0 && crkPk >= InpLadT; }
bool   LadGuard() { return LadOn() && totalNet <= 0; }
//--- the level: lock (share of the best profit kept out of the extra risk), share of the cushion added to the base, most base (x), most extra loss
void   LadPar(double &lam, double &phi, double &bmax, double &gam)
{
   lam = 0.8; phi = 0.10; bmax = 2.0; gam = 0.25;
   if(InpLadder == LAD_MED)   { lam = 0.7; phi = 0.15; bmax = 3.0;  gam = 0.30; }
   if(InpLadder == LAD_HIGH)  { lam = 0.6; phi = 0.20; bmax = 5.0;  gam = 0.35; }
   if(InpLadder == LAD_XHIGH) { lam = 0.5; phi = 0.25; bmax = 8.0;  gam = 0.40; }
   if(InpLadder == LAD_MAX)   { lam = 0.4; phi = 0.30; bmax = 12.0; gam = 0.50; }
}
//--- the ladder's base (the plain base while it is off) and the cushion (the closed profit above the lock)
double LadBase(double &cush)
{
   cush = 0;
   if(!LadOn()) return InpBaseRisk;
   double lam, phi, bmax, gam; LadPar(lam, phi, bmax, gam);
   cush = MathMax(0.0, totalNet - lam * crkPk);
   return InpBaseRisk + MathMin((bmax - 1.0) * InpBaseRisk, phi * cush);
}
string LadTxt()
{
   string lv = InpLadder == LAD_LOW ? "Low" : InpLadder == LAD_MED ? "Medium" : InpLadder == LAD_HIGH ? "High" : InpLadder == LAD_XHIGH ? "Extra high" : "Max";
   if(!LadFam()) return lv + " | only with Crooks F, G, H, I or J";
   if(!LadOn()) return lv + " | best profit " + DoubleToString(MathMax(0.0, crkPk), 2) + " of " + DoubleToString(InpLadT, 0) + " to start";
   if(LadGuard()) return lv + " | back at the start: 0.01 lot until in profit";
   double cush, b = LadBase(cush), lam, phi, bmax, gam; LadPar(lam, phi, bmax, gam);
   return lv + " | lock " + DoubleToString(lam * crkPk, 2) + " | cushion " + DoubleToString(cush, 2) + " | base " + DoubleToString(b, 2);
}

//--- Crooks TP1 rule (exit at TP1, or any exit with InpCrkT1Any; recovery trades): the part p closed at TP1 banks the recovery amount, the rest runs to TP2.''')
rep('''   if(!InpCrkT1 || (InpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext() || CrkHedgeNow()) return 0;''',
    '''   if(!InpCrkT1 || (InpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext() || CrkHedgeNow() || LadGuard()) return 0;   // v4.6: not while the ladder's guard is on''')
rep('''//--- the $ risk of the next trade; minRisk: the stop-out loss of the Crooks E / I lot on this setup (0 = not known: the base is used)
double NextRisk(double exitR, bool canTake = true, double minRisk = 0)''', '''//--- the risk of a Crooks rule's next trade at this base (v4.6: also at the profit ladder's base)
double CrkRule(double base, double exitR, double minRisk)
{
   double x = crkL / (InpRec == REC_CRB ? InpCSplit : CrkCFam() ? CrkParts() : 1) * (CrkCFam() ? CrkPrPct() : 1.0);   // % rule: a part of the loss
   bool rn = CrkRecNext();
   double r = !rn ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
   if(rn) r = CrkRecLimit(r, base);                                  // v4.5 Crooks F / H / I / J
   else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI) && minRisk > 0) r = MathMin(base, minRisk);   // v4.5 Crooks E / I: the small lot while waiting
   return r;
}
//--- the $ risk of the next trade; minRisk: the stop-out loss of the 0.01 lot (Crooks E / I lot) on this setup (0 = not known: the base is used)
double NextRisk(double exitR, bool canTake = true, double minRisk = 0)''')
rep('''      {
         double x = crkL / (InpRec == REC_CRB ? InpCSplit : CrkCFam() ? CrkParts() : 1) * (CrkCFam() ? CrkPrPct() : 1.0);   // % rule: a part of the loss
         bool rn = CrkRecNext();
         r = !rn ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
         if(rn) r = CrkRecLimit(r, base);                                  // v4.5 Crooks F / H / I / J
         else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI) && minRisk > 0) r = MathMin(base, minRisk);   // v4.5 Crooks E / I: the small lot while waiting
         break;
      }''', '''      {
         r = CrkRule(base, exitR, minRisk);
         if(LadOn())                                                       // v4.6 profit ladder: the rule at the ladder's base, the extra paid from the cushion
         {
            double cush, lb = LadBase(cush), lam, phi, bmax, gam; LadPar(lam, phi, bmax, gam);
            r = LadGuard() ? (minRisk > 0 ? MathMin(base, minRisk) : base) : MathMin(CrkRule(lb, exitR, minRisk), r + gam * cush / CrkT1Mult());
         }
         break;
      }''')
rep('''   double minR = (InpRec == REC_CRE || InpRec == REC_CRI) ? MinLotRisk(trRisk) : 0;   // v4.5 Crooks E / I: the small lot on this setup''',
    '''   double minR = (InpRec == REC_CRE || InpRec == REC_CRI || LadOn()) ? MinLotRisk(trRisk) : 0;   // v4.5 Crooks E / I, v4.6 ladder guard: the 0.01 lot on this setup''')
rep('''   if(InpRec == REC_CRG && InpCrkGX > 0) crkL = MathMin(crkL, InpCrkGX * InpBaseRisk);   // v4.5 Crooks G: never more than X x base to win back
   crkPk = MathMax(crkPk, totalNet);                    // v4.5 Crooks J: the highest closed profit (whatever the rule, so a switch to J knows it)''',
    '''   crkPk = MathMax(crkPk, totalNet);                    // v4.5 Crooks J, v4.6 ladder: the highest closed profit (whatever the rule, so a switch knows it)
   double gCush;
   if(InpRec == REC_CRG && InpCrkGX > 0) crkL = MathMin(crkL, InpCrkGX * LadBase(gCush));   // v4.5 Crooks G: never more than X x base (v4.6: the ladder's base)''')
rep('''   TblAdd("AUCTION RETEST", "EA v4.5", white, C'61,143,214');''', '''   TblAdd("AUCTION RETEST", "EA v4.6", white, C'61,143,214');''')
rep('''   TblAdd("RISK | LOTS", exState != 0 ? DoubleToString(exRiskAmt, 2) + " | " + DoubleToString(exLots, 2) : "base " + DoubleToString(InpBaseRisk, 2), white, cell);''',
    '''   double lCu;
   TblAdd("RISK | LOTS", exState != 0 ? DoubleToString(exRiskAmt, 2) + " | " + DoubleToString(exLots, 2) : "base " + DoubleToString(LadBase(lCu), 2), white, cell);''')
rep('''   TblAdd(isC ? "LOSSES CARRIED" : isK ? "CROOKS: LOSS TO WIN BACK" : "RECOVERY POOL", rec, (isC ? carried : isK ? crkL : recPool) > 0 ? negC : white, cell);''',
    '''   TblAdd(isC ? "LOSSES CARRIED" : isK ? "CROOKS: LOSS TO WIN BACK" : "RECOVERY POOL", rec, (isC ? carried : isK ? crkL : recPool) > 0 ? negC : white, cell);
   if(InpLadder != LAD_OFF) TblAdd("PROFIT LADDER", LadTxt(), LadGuard() ? negC : LadOn() ? posC : white, cell);''')
rep('''   if(InpRec == REC_CRJ && InpCrkJX <= 0) { Print("Crooks J: the drawdown must be above 0."); return INIT_PARAMETERS_INCORRECT; }
''', '''   if(InpRec == REC_CRJ && InpCrkJX <= 0) { Print("Crooks J: the drawdown must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpLadder != LAD_OFF && InpLadT <= 0) { Print("Profit ladder: the profit target must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpLadder != LAD_OFF && !LadFam()) Print("Profit ladder: it works with Crooks F, G, H, I or J only; with this loss recovery it is off.");
''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
