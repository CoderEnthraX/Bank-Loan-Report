"""EA v4.1 (EA only): Crooks C hedge rule. After N losing recovery trades in a row (Crooks C rule = Hedge), the next signal opens a buy and a
sell at the engine's entry level (hedging account), both sized as the recovery trade, each with its own stop loss and take profit (inputs, in R or
price). They run to those levels (the engine's exits do not touch them; force-close / weekend / news close them). When both are closed: forget the
loss (default) or Crooks C goes on from the trade that closed last. A netting account forgets the loss instead. Every replacement must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
W = len('//| v3.9: Crooks C rule after N losing recovery trades in a row:     |')
def hl(t):
    line = '//| ' + t
    assert len(line) <= W - 2, t
    return line.ljust(W - 1) + '|'
hdr_old = '//| TradingView, so lots and target levels match it (0 = live).      |\n'
hdr_new = hdr_old + '\n'.join(hl(t) for t in (
    'v4.1 (EA only): Crooks C hedge rule: after N losing recovery',
    'trades in a row, the next signal opens a buy and a sell at the',
    'same entry (hedging account), with their own stop loss and take',
    'profit; then forget the loss, or go on from the last trade.')) + '\n'
REPS = [
    (hdr_old, hdr_new),
    ('#property version   "4.00"', '#property version   "4.10"'),
    ('TblAdd("AUCTION RETEST", "EA v4.0"', 'TblAdd("AUCTION RETEST", "EA v4.1"'),
    ('                   CPR_SKIP   = 4 }; // Skip D trading days',
     '                   CPR_SKIP   = 4,   // Skip D trading days\n'
     '                   CPR_HEDGE  = 5 }; // Hedge: a buy and a sell on the next signal (hedging account)\n'
     'enum ENUM_HG_UNIT { HGU_R     = 0,   // R (x the signal\'s stop distance)\n'
     '                    HGU_PRICE = 1 }; // Price (e.g. 5.0 = $5 on gold)'),
    ('input bool   InpCrkPrAll = false;  //   ...count every day, not only the trading days (the skip rule)\n',
     'input bool   InpCrkPrAll = false;  //   ...count every day, not only the trading days (the skip rule)\n'
     'input double InpCrkHgSl  = 1.0;    //   ...hedge rule: stop loss of the buy and the sell (R: 1 = the signal\'s own stop)\n'
     'input double InpCrkHgTp  = 0.6;    //   ...hedge rule: take profit of the buy and the sell (R: 0.6 = TP1)\n'
     'input ENUM_HG_UNIT InpCrkHgUnit = HGU_R; //   ...hedge rule: stop loss and take profit in R or in price\n'
     'input bool   InpCrkHgForget = true; //   ...hedge rule: forget the loss after the pair (off: Crooks C goes on from the trade that closed last)\n'),
    ('long     gPauseArm = -1; ',
     'bool     crkHg = false;                                   // hedge rule: the next signal opens a buy and a sell\n'
     'bool     exHg = false; double exHgS = 0, exHgT = 0;      // hedge rule: the working setup / open trades are the pair; its stop loss and take profit distances\n'
     'double   gLastOutProfit = 0;                              // profit of the last closing deal (hedge rule: did the trade that closed last win)\n'
     'bool     gHedgeOk = false;                                // the account can hold a buy and a sell at the same time (hedging)\n'
     'long     gPauseArm = -1; '),
    ('crkWW = 0; crkNeedL = false; }   // a new cycle at the base risk', 'crkWW = 0; crkNeedL = false; crkHg = false; }   // a new cycle at the base risk'),
    ('bool   CrkPause() { return CrkPrOn() && InpCrkPr == CPR_SKIP && crkSkip; }   // the skip rule pauses trading\n',
     'bool   CrkPause() { return CrkPrOn() && InpCrkPr == CPR_SKIP && crkSkip; }   // the skip rule pauses trading\n'
     'bool   CrkHedgeNow() { return CrkPrOn() && InpCrkPr == CPR_HEDGE && crkHg && crkL > 0; }   // hedge rule: this signal opens the pair\n'),
    ('   if(InpRec == REC_CRC) return crkW && crkL > 0 && !(CrkPrOn() && InpCrkPr == CPR_WAIT && (crkWait || crkNeedL));   // wait rule: not while waiting',
     '   if(InpRec == REC_CRC) return (crkW && crkL > 0 && !(CrkPrOn() && InpCrkPr == CPR_WAIT && (crkWait || crkNeedL))) || CrkHedgeNow();   // wait rule: not while waiting; the hedge pair is sized as a recovery trade'),
    ('|| !CrkRecNext()) return 0;', '|| !CrkRecNext() || CrkHedgeNow()) return 0;'),
    ('      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) closed = true;',
     '      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); }'),
    ('double MinDist() {', None),   # placeholder: insert the hedge helpers after the MinDist line (below)
    # TakeSetup
    ('   double t1d = CrkT1Dist();                         // after a cap restart this is 0: trade 1 of a new cycle\n'
     '   double sd = t1d > 0 ? t1d : trRisk;               // stop distance used for the size\n'
     '   double ld = t1d > 0 ? CrkT1Stop0Dist(t1d) : trRisk;   // the real stop-out distance (a wider TP1-rule stop)\n',
     '   bool   hg = CrkHedgeNow();                        // Crooks C hedge rule: a buy and a sell (after NextRisk: a hard-cap restart cancels it)\n'
     '   double hgS = hg ? HgDist(InpCrkHgSl) : 0, hgT = hg ? HgDist(InpCrkHgTp) : 0;\n'
     '   double t1d = CrkT1Dist();                         // after a cap restart this is 0: trade 1 of a new cycle\n'
     '   double sd = hg ? hgS : t1d > 0 ? t1d : trRisk;    // stop distance used for the size\n'
     '   double ld = hg ? hgS : t1d > 0 ? CrkT1Stop0Dist(t1d) : trRisk;   // the real stop-out distance (a wider TP1-rule stop)\n'),
    ('   exCostPx = InpEarnBack && tv > 0 ? InpCommLot / (tv / ts) + sprNow : 0;',
     '   exCostPx = InpEarnBack && tv > 0 && !hg ? InpCommLot / (tv / ts) + sprNow : 0;   // no earn-back on the hedge pair: its levels are the inputs'),
    ('   exT1Tp1 = t1; exT1Tp2 = t2; exKeepSl = 0;\n', '   exT1Tp1 = t1; exT1Tp2 = t2; exKeepSl = 0; exHg = false; exHgS = hgS; exHgT = hgT; gLastOutProfit = 0;\n'),
    ('   bool ok;\n   if(InpEntryMode == ENTRY_MARKET)', '   bool ok;\n   if(hg) ok = PlaceHedge(isL, v);\n   else if(InpEntryMode == ENTRY_MARKET)'),
    ('   if(ok) { exState = 1; exArm = armBar; exSynced = false; takenN++; crkRec = CrkRecNext(); }',
     '   if(ok) { exState = 1; exArm = armBar; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }'),
    # VirtualEntry
    ('   if(exState != 1) { gVirt = false; return; }\n   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);\n',
     '   if(exState != 1) { gVirt = false; return; }\n   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);\n'
     '   if(exHg)                                             // hedge pair: both trades at market when the level is reached\n'
     '   {\n'
     '      if(exL ? (ask <= EntryPx(true) || bid <= EntryPx(false)) : (bid >= EntryPx(false) || ask >= EntryPx(true))) { gVirt = false; HgMarket(exLots); }\n'
     '      return;\n'
     '   }\n'),
    # BookClosed
    ('   if(crkL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && crkRec)) CrkCycle();',
     '   if(exHg)                                             // the hedge pair closed (exPnl = both trades): forget the loss, or Crooks C goes on from the trade that closed last\n'
     '   {\n'
     '      crkF = 0; crkHg = false;\n'
     '      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = CrkNp(); }\n'
     '   }\n'
     '   else if(crkL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && crkRec)) CrkCycle();'),
    ('            else if(InpCrkPr == CPR_SKIP) { crkSkip = true; crkSkipLeft = MathMax(1, InpCrkPrD); if(InpCrkPrForget) CrkCycle(); }\n',
     '            else if(InpCrkPr == CPR_SKIP) { crkSkip = true; crkSkipLeft = MathMax(1, InpCrkPrD); if(InpCrkPrForget) CrkCycle(); }\n'
     '            else if(InpCrkPr == CPR_HEDGE) { if(gHedgeOk) crkHg = true; else CrkCycle(); }   // hedge rule: the next signal opens the pair (netting account: forget the loss)\n'),
    ('   crkW = win;\n', '   crkW = exHg ? gLastOutProfit > 0 : win;             // hedge pair: the trade that closed last decides (a win -> the next trade is a recovery trade)\n'),
    ('   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false;\n   CancelPending();\n}',
     '   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false; exHg = false;\n   CancelPending();\n}'),
    # OnNewBar: the hedge pair runs to its own stop loss and take profit
    ('      if(exMine && lastFill > exArm) missN++;          // engine filled, broker did not\n      exState = 0; exArm = -1; gVirt = false;\n',
     '      if(exMine && lastFill > exArm) missN++;          // engine filled, broker did not\n      exState = 0; exArm = -1; gVirt = false; exHg = false;\n'),
    ('   if(exState == 2 && exMine && (evFill || evMove)) SetExits(true);', '   if(exState == 2 && exMine && !exHg && (evFill || evMove)) SetExits(true);'),
    ('   if(evExit && exState == 2 && exMine && (!InpEarnBack || !evWin)', '   if(evExit && exState == 2 && exMine && !exHg && (!InpEarnBack || !evWin)'),
    ('   if(pos && !exClosed && !evExit && !engHolds && !(InpEarnBack && exSynced) && !(exT1 && exSynced))',
     '   if(pos && !exClosed && !evExit && !engHolds && !(InpEarnBack && exSynced) && !(exT1 && exSynced) && !exHg)'),
    ('   if(exState == 1 && (flatNow || newsBlk)) { CancelPending(); exState = 0; exArm = -1; gVirt = false; }',
     '   if(exState == 1 && (flatNow || newsBlk)) { CancelPending(); exState = 0; exArm = -1; gVirt = false; exHg = false; }'),
    ('      if(caught && exState == 2 && MathAbs(st) == 2 && exArm == armBar) SetExits(true);',
     '      if(caught && exState == 2 && MathAbs(st) == 2 && exArm == armBar && !exHg) SetExits(true);'),
    ('void ManagePartials()\n{\n   if(exState != 2) return;', 'void ManagePartials()\n{\n   if(exState != 2 || exHg) return;'),
    # ResetEngine
    ('exT1Tp1 = 0; exT1Tp2 = 0; exKeepSl = 0;\n   sigN = 0;', 'exT1Tp1 = 0; exT1Tp2 = 0; exKeepSl = 0; exHg = false; exHgS = 0; exHgT = 0; gLastOutProfit = 0;\n   sigN = 0;'),
    # OnInit
    ('crkSkip = false; crkSkipLeft = 0; }\n   gCrkPrPrev = (int)InpCrkPr;\n',
     'crkSkip = false; crkSkipLeft = 0; crkHg = false; }\n   gCrkPrPrev = (int)InpCrkPr;\n'
     '   gHedgeOk = (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;\n'
     '   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && !gHedgeOk) Print("Crooks C hedge rule: this account cannot hold a buy and a sell together (netting), so the rule forgets the loss instead.");\n'),
    ('   if(InpRec == REC_CRC && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100))',
     '   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0 || InpCrkHgTp <= 0)) { Print("Crooks C hedge rule: stop loss and take profit must be above 0."); return INIT_PARAMETERS_INCORRECT; }\n'
     '   if(InpRec == REC_CRC && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100))'),
    ('   if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))\n',
     '   if(HgOpen()) { exState = 2; exHg = true; Print("Hedge pair still open: its trades run to their own stop loss and take profit."); }\n'
     '   else if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))\n'),
    # state text and table
    ('!gKzOk ? "OUTSIDE KILL ZONES" : "SCANNING";', '!gKzOk ? "OUTSIDE KILL ZONES" : CrkHedgeNow() ? "SCANNING (HEDGE PAIR ON THE NEXT SIGNAL)" : "SCANNING";'),
    ('   string ex = exState == 2 ? " (in trade)" : (exState == 1 ? (gVirt ? " (waiting for the level)" : " (order working)") : "");',
     '   string ex = exState == 2 ? (exHg ? " (hedge pair open)" : " (in trade)") : (exState == 1 ? (gVirt ? " (waiting for the level)" : exHg ? " (hedge orders working)" : " (order working)") : "");'),
    ('crkNeedL ? " | waiting for a loss, then a win" : crkF > 0', 'crkNeedL ? " | waiting for a loss, then a win" : crkHg ? " | hedge pair on the next signal" : crkF > 0'),
]
HELPERS = r'''
//--- Crooks C hedge rule: a buy and a sell at the engine's entry level with the hedge stop loss and take profit
//--- (bid-chart levels: the buy-side prices are shifted by the spread, like the normal orders)
double HgDist(double x) { double ts = TickSize(); double d = InpCrkHgUnit == HGU_R ? x * trRisk : x; return MathMax(MathMax(ts, MinDist()), MathRound(d / ts) * ts); }
void   HgLevels(bool buy, double &sl, double &tp)
{
   double tl = TickSize() * 0.001;
   if(buy) { sl = FloorTick(lim - exHgS + tl); tp = CeilTick(lim + exHgT - tl); }
   else    { sl = CeilTick(lim + exHgS - tl + Spr()); tp = FloorTick(lim - exHgT + tl + Spr()); }
}
bool   HgMarket(double v)                                // both trades at market (the level is reached, or Market entry)
{
   double slB, tpB, slS, tpS; HgLevels(true, slB, tpB); HgLevels(false, slS, tpS);
   bool a = trade.Buy(v, _Symbol, 0, slB, tpB, "HEDGE");
   if(!a) Print("Hedge buy failed: ", trade.ResultRetcodeDescription());
   bool b = trade.Sell(v, _Symbol, 0, slS, tpS, "HEDGE");
   if(!b) Print("Hedge sell failed: ", trade.ResultRetcodeDescription());
   return a || b;
}
bool   PlaceHedge(bool isL, double v)                    // the pair's orders: a limit in the signal's direction and a stop the other way, both at the entry level
{
   if(InpEntryMode == ENTRY_MARKET) return HgMarket(v);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), gap = MathMax(MinDist(), TickSize());
   double pB = EntryPx(true), pS = EntryPx(false);       // the buy and the sell trigger when the bid reaches the entry level
   double slB, tpB, slS, tpS; HgLevels(true, slB, tpB); HgLevels(false, slS, tpS);
   if(isL ? (ask <= pB || bid <= pS) : (bid >= pS || ask >= pB)) return HgMarket(v);   // at / through the level: both now
   if(isL ? (ask - pB < gap || bid - pS < gap) : (pS - bid < gap || pB - ask < gap)) { gVirt = true; return true; }   // inside the stops distance: VirtualEntry opens both
   bool a = isL ? trade.BuyLimit(v, pB, _Symbol, slB, tpB, ORDER_TIME_GTC, 0, "HEDGE") : trade.SellLimit(v, pS, _Symbol, slS, tpS, ORDER_TIME_GTC, 0, "HEDGE");
   bool b = a && (isL ? trade.SellStop(v, pS, _Symbol, slS, tpS, ORDER_TIME_GTC, 0, "HEDGE") : trade.BuyStop(v, pB, _Symbol, slB, tpB, ORDER_TIME_GTC, 0, "HEDGE"));
   if(!b) { Print("Hedge orders failed: ", trade.ResultRetcodeDescription()); CancelPending(); return false; }
   return true;
}
bool   HgOpen()                                          // a hedge trade of this EA is open (e.g. after a restart)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic && PositionGetString(POSITION_COMMENT) == "HEDGE") return true;
   }
   return false;
}
'''
for old, new in REPS:
    n = s.count(old)
    assert n == 1, (n, old[:100])
    if new is None:                                       # insert the helpers after the whole MinDist line
        i = s.index(old); j = s.index('\n', i) + 1
        s = s[:j] + HELPERS.lstrip('\n') + s[j:]
    else:
        s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print(len(REPS), 'replacements; lines', s.count('\n'))
