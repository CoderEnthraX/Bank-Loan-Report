"""EA v4.5 (asked 2026-11-13): six new loss-recovery rules, each Crooks C with one change; everything of Crooks C applies to them (over N
wins, the rule after N losing recovery trades incl. the hedge rule, the Crooks TP1 rule, the hard cap):
  Crooks E  the user's rule: while a loss is owed, every trade that is not the recovery trade is 0.01 lot (InpCrkELot; the normal size if
            that is smaller); the recovery trade after a win goes for the loss as Crooks C, and a losing one goes back to 0.01 lot
  Crooks F  a recovery trade risks at most InpCrkFK x base (3): the rest is won back after the next wins (Crooks C keeps a leftover)
  Crooks G  the loss to win back is at most InpCrkGX x base (10): the rest is accepted as lost
  Crooks H  a recovery trade risks at most InpCrkHPct % of the equity (1%)
  Crooks I  Crooks E + Crooks F
  Crooks J  a recovery trade shrinks with the drawdown of the closed profit: x (1 - drawdown / (InpCrkJX x base)) (20), at least the base
The limits of F / H / I cover the real stop-out loss (a TP1-rule trade's wider stop). New state: crkPk (the highest closed profit, saved
as "pk"). Gold study: gold/crooks_e1.py, crooks_e2.py; reference gold/recovery.py. Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


# ---- header, version
rep('''//| default; DISPLAY inputs).                                        |
''', '''//| default; DISPLAY inputs).                                        |
//| v4.5: Crooks E - J: Crooks C with smaller trades or a limit on   |
//| the recovery trade, so a long losing run costs less.             |
''')
rep('''#property version   "4.40"''', '''#property version   "4.50"''')
# ---- the six rules
rep('''   REC_CRD   = 21  // Crooks D (base, base, recovery: every 3rd trade)''',
    '''   REC_CRD   = 21, // Crooks D (base, base, recovery: every 3rd trade)
   REC_CRE   = 22, // Crooks E (Crooks C, 0.01 lot while waiting for a win)
   REC_CRF   = 23, // Crooks F (Crooks C, recovery at most K x base)
   REC_CRG   = 24, // Crooks G (Crooks C, loss to win back at most X x base)
   REC_CRH   = 25, // Crooks H (Crooks C, recovery at most % of equity)
   REC_CRI   = 26, // Crooks I (Crooks E + recovery at most K x base)
   REC_CRJ   = 27  // Crooks J (Crooks C, recovery shrinks in a drawdown)''')
rep('''input bool   InpCrkCnOn  = false;  // Crooks C: win the loss back over N wins''',
    '''input bool   InpCrkCnOn  = false;  // Crooks C (and E-J): win the loss back over N wins''')
rep('''input ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C: after N losing recovery trades in a row''',
    '''input ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C (and E-J): after N losing recovery trades in a row''')
rep('''input bool   InpCrkHgForget = true; //   ...hedge rule: forget the loss after the pair (off: Crooks C goes on from the trade that closed last)
''', '''input bool   InpCrkHgForget = true; //   ...hedge rule: forget the loss after the pair (off: Crooks C goes on from the trade that closed last)
input double InpCrkELot  = 0.01;   // Crooks E / I: lot of the trades while a loss waits for a win (the normal size if smaller)
input double InpCrkFK    = 3.0;    // Crooks F / I: a recovery trade risks at most this many x the base risk
input double InpCrkGX    = 10.0;   // Crooks G: the loss to win back is at most this many x the base risk (the rest is accepted)
input double InpCrkHPct  = 1.0;    // Crooks H: a recovery trade risks at most this % of the equity
input double InpCrkJX    = 20.0;   // Crooks J: drawdown (x the base risk) at which a recovery trade is back to the base risk
''')
rep('''double   crkL = 0; int crkN = 0; bool crkRec = false;   // Crooks: $ loss to win back, closed trades in the cycle, the open trade is a recovery trade
''', '''double   crkL = 0; int crkN = 0; bool crkRec = false;   // Crooks: $ loss to win back, closed trades in the cycle, the open trade is a recovery trade
double   crkPk = 0;                                      // v4.5 Crooks J: the highest closed profit so far (its drawdown = crkPk - totalNet)
''')
rep('''//--- Crooks C rule after N losing recovery trades in a row (Crooks C only)
bool   CrkPrOn()  { return InpRec == REC_CRC && InpCrkPr != CPR_OFF; }''',
    '''//--- v4.5: Crooks C and the rules built on it (E - J): everything of Crooks C applies to them
bool   CrkCFam()  { return InpRec == REC_CRC || (InpRec >= REC_CRE && InpRec <= REC_CRJ); }
//--- Crooks C rule after N losing recovery trades in a row (Crooks C and E - J)
bool   CrkPrOn()  { return CrkCFam() && InpCrkPr != CPR_OFF; }''')
rep('''   if(InpRec == REC_CRC) return (crkW && crkL > 0 &&''', '''   if(CrkCFam()) return (crkW && crkL > 0 &&''')
# ---- the size: the limits of a recovery trade, the small lot while waiting
rep('''double NextRisk(double exitR, bool canTake = true)
{''', '''//--- v4.5 Crooks F / H / I / J: the most a recovery trade may risk (F / H / I: its real stop-out loss, a TP1-rule trade's wider stop included)
double CrkRecLimit(double r, double base)
{
   double mul = CrkT1Mult();
   if(InpRec == REC_CRF || InpRec == REC_CRI) r = MathMin(r, MathMax(1.0, InpCrkFK) * base / mul);
   else if(InpRec == REC_CRH) r = MathMin(r, MathMax(base, AccountInfoDouble(ACCOUNT_EQUITY) * InpCrkHPct / 100.0) / mul);
   else if(InpRec == REC_CRJ && InpCrkJX > 0) r = MathMax(base, r * MathMax(0.0, 1.0 - MathMax(0.0, crkPk - totalNet) / (InpCrkJX * base)));
   return r;
}
//--- the $ risk of the next trade; minRisk: the stop-out loss of the Crooks E / I lot on this setup (0 = not known: the base is used)
double NextRisk(double exitR, bool canTake = true, double minRisk = 0)
{''')
rep('''      case REC_CRA:
      case REC_CRB:
      case REC_CRC:
      case REC_CRD:
      {
         double x = crkL / (InpRec == REC_CRB ? InpCSplit : InpRec == REC_CRC ? CrkParts() : 1) * (InpRec == REC_CRC ? CrkPrPct() : 1.0);   // % rule: a part of the loss
         r = !CrkRecNext() ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
         break;
      }''', '''      case REC_CRA:
      case REC_CRB:
      case REC_CRC:
      case REC_CRD:
      case REC_CRE:
      case REC_CRF:
      case REC_CRG:
      case REC_CRH:
      case REC_CRI:
      case REC_CRJ:
      {
         double x = crkL / (InpRec == REC_CRB ? InpCSplit : CrkCFam() ? CrkParts() : 1) * (CrkCFam() ? CrkPrPct() : 1.0);   // % rule: a part of the loss
         bool rn = CrkRecNext();
         r = !rn ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
         if(rn) r = CrkRecLimit(r, base);                                  // v4.5 Crooks F / H / I / J
         else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI) && minRisk > 0) r = MathMin(base, minRisk);   // v4.5 Crooks E / I: the small lot while waiting
         break;
      }''')
rep('''   while(v >= vmin && OrderCalcMargin(ot, _Symbol, v, entry, margin) && margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v -= step;
   if(v < vmin) return 0;
   return NormalizeDouble(v, 8);
}
''', '''   while(v >= vmin && OrderCalcMargin(ot, _Symbol, v, entry, margin) && margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v -= step;
   if(v < vmin) return 0;
   return NormalizeDouble(v, 8);
}
//--- v4.5 Crooks E / I: the stop-out loss (spread and commission included, as LotsFor) of the lot used while a loss waits for a win:
//--- InpCrkELot, at least the broker's minimum, on its lot grid (LotsFor turns this amount back into exactly that lot)
double MinLotRisk(double stopDist)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(step <= 0) step = vmin > 0 ? vmin : 0.01;
   double lots = MathCeil(MathMax(InpCrkELot, vmin) / step - 1e-9) * step;
   return lots * ((stopDist + MathMax(CostSpr(), 0)) / ts * tv + InpCommLot);
}
''')
rep('''   double rAmt = NextRisk(ExitR(), canTake);''',
    '''   double minR = (InpRec == REC_CRE || InpRec == REC_CRI) ? MinLotRisk(trRisk) : 0;   // v4.5 Crooks E / I: the small lot on this setup
   double rAmt = NextRisk(ExitR(), canTake, minR);''')
# ---- booking: Crooks G's limit, Crooks J's peak
rep('''   crkL = MathMax(0.0, crkL - exPnl);
   if(exHg)''', '''   crkL = MathMax(0.0, crkL - exPnl);
   if(InpRec == REC_CRG && InpCrkGX > 0) crkL = MathMin(crkL, InpCrkGX * InpBaseRisk);   // v4.5 Crooks G: never more than X x base to win back
   crkPk = MathMax(crkPk, totalNet);                    // v4.5 Crooks J: the highest closed profit (whatever the rule, so a switch to J knows it)
   if(exHg)''')
# ---- restart memory
rep('''IoD("tn", totalNet);''', '''IoD("tn", totalNet); IoD("pk", crkPk);''')
rep('''   StateIO(false);
   gSvAcc = (long)MathRound(svAcc);''', '''   StateIO(false);
   crkPk = MathMax(crkPk, totalNet);                    // a state saved before v4.5 has no peak: the closed profit itself
   gSvAcc = (long)MathRound(svAcc);''')
rep('''totalNet = 0; exW = 0;''', '''totalNet = 0; crkPk = 0; exW = 0;''')
# ---- table and the restart line
rep('''isK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;
   bool   kRec''', '''isK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRD || CrkCFam();
   bool   kRec''')
rep('''   string kTxt = DoubleToString(crkL, 2) + (InpRec == REC_CRC ? (kRec ? " | recovery trade" + (CrkNp() > 1 ? ", part " + IntegerToString(CrkNp() - CrkParts() + 1) + " of " + IntegerToString(CrkNp()) : "") : (crkL > 0 ? " | base, waiting for a win" : " | base"))''',
    '''   string kLim = InpRec == REC_CRF || InpRec == REC_CRI ? ", at most " + DoubleToString(InpCrkFK, 1) + "x base" : InpRec == REC_CRH ? ", at most " + DoubleToString(InpCrkHPct, 1) + "% of equity" :
                 InpRec == REC_CRJ ? ", drawdown " + DoubleToString(MathMax(0.0, crkPk - totalNet), 2) : "";
   string kWait = InpRec == REC_CRE || InpRec == REC_CRI ? " | " + DoubleToString(InpCrkELot, 2) + " lot, waiting for a win" : " | base, waiting for a win";
   string kTxt = DoubleToString(crkL, 2) + (InpRec == REC_CRG ? " (at most " + DoubleToString(InpCrkGX * InpBaseRisk, 0) + ")" : "") +
                 (CrkCFam() ? (kRec ? " | recovery trade" + (CrkNp() > 1 ? ", part " + IntegerToString(CrkNp() - CrkParts() + 1) + " of " + IntegerToString(CrkNp()) : "") + kLim : (crkL > 0 ? kWait : " | base"))''')
rep('''   TblAdd("AUCTION RETEST", "EA v4.4", white, C'61,143,214');''', '''   TblAdd("AUCTION RETEST", "EA v4.5", white, C'61,143,214');''')
rep('''isKK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;''',
    '''isKK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRD || CrkCFam();''')
# ---- OnInit: the Crooks C checks apply to E - J; the new inputs
rep('''   if(gCrkPrPrev != (int)InpCrkPr || InpRec != REC_CRC) {''', '''   if(gCrkPrPrev != (int)InpCrkPr || !CrkCFam()) {''')
rep('''   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && !gHedgeOk) Print(''', '''   if(CrkCFam() && InpCrkPr == CPR_HEDGE && !gHedgeOk) Print(''')
rep('''   if(InpRec == REC_CRC && InpCrkPr != CPR_OFF && (InpCrkPrN < 1''', '''   if(CrkCFam() && InpCrkPr != CPR_OFF && (InpCrkPrN < 1''')
rep('''   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0''', '''   if(CrkCFam() && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0''')
rep('''   if(InpRec == REC_CRC && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100)) { Print("Crooks C rule: % of the loss must be 10 to 100."); return INIT_PARAMETERS_INCORRECT; }
''', '''   if(CrkCFam() && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100)) { Print("Crooks C rule: % of the loss must be 10 to 100."); return INIT_PARAMETERS_INCORRECT; }
   if((InpRec == REC_CRE || InpRec == REC_CRI) && InpCrkELot <= 0) { Print("Crooks E / I: the lot while waiting for a win must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if((InpRec == REC_CRF || InpRec == REC_CRI) && InpCrkFK < 1) { Print("Crooks F / I: the recovery limit must be 1 x the base risk or more."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRG && InpCrkGX <= 0) { Print("Crooks G: the limit of the loss to win back must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRH && InpCrkHPct <= 0) { Print("Crooks H: the % of the equity must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRJ && InpCrkJX <= 0) { Print("Crooks J: the drawdown must be above 0."); return INIT_PARAMETERS_INCORRECT; }
''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
