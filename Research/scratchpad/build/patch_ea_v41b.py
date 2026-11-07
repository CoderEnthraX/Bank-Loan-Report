"""EA v4.1 review fixes (hedge rule only): minimum SL / TP distance incl. the spread, market pair valid stops + no lone trade, margin for both
trades, a waiting leg cancelled at force-close / weekend / news, hard cap when both trades can lose. Every replacement must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
REPS = [
    # 1. a take profit / stop loss must clear the spread and the broker's stops level from the order price
    ('double HgDist(double x) { double ts = TickSize(); double d = InpCrkHgUnit == HGU_R ? x * trRisk : x; return MathMax(MathMax(ts, MinDist()), MathRound(d / ts) * ts); }',
     'double HgDist(double x)                                 // at least the stops level + the spread + 1 tick, or the broker rejects the order\n'
     '{\n'
     '   double ts = TickSize(), d = InpCrkHgUnit == HGU_R ? x * trRisk : x;\n'
     '   double sp = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));\n'
     '   return MathMax(MinDist() + sp + ts, MathRound(d / ts) * ts);\n'
     '}'),
    # 2. market pair: stops valid against the live price (a gap past a level), and never one trade alone
    ('bool   HgMarket(double v)                                // both trades at market (the level is reached, or Market entry)\n'
     '{\n'
     '   double slB, tpB, slS, tpS; HgLevels(true, slB, tpB); HgLevels(false, slS, tpS);\n'
     '   bool a = trade.Buy(v, _Symbol, 0, slB, tpB, "HEDGE");\n'
     '   if(!a) Print("Hedge buy failed: ", trade.ResultRetcodeDescription());\n'
     '   bool b = trade.Sell(v, _Symbol, 0, slS, tpS, "HEDGE");\n'
     '   if(!b) Print("Hedge sell failed: ", trade.ResultRetcodeDescription());\n'
     '   return a || b;\n'
     '}',
     'bool   HgMarket(double v)                                // both trades at market (the level is reached, or Market entry); one trade alone is closed again\n'
     '{\n'
     '   double slB, tpB, slS, tpS; HgLevels(true, slB, tpB); HgLevels(false, slS, tpS);\n'
     '   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), g = MinDist() + TickSize();\n'
     '   slB = MathMin(slB, FloorTick(bid - g)); tpB = MathMax(tpB, CeilTick(bid + g));   // the price already past a level (a gap): keep the order valid\n'
     '   slS = MathMax(slS, CeilTick(ask + g)); tpS = MathMin(tpS, FloorTick(ask - g));\n'
     '   bool a = trade.Buy(v, _Symbol, 0, slB, tpB, "HEDGE");\n'
     '   if(!a) Print("Hedge buy failed: ", trade.ResultRetcodeDescription());\n'
     '   bool b = trade.Sell(v, _Symbol, 0, slS, tpS, "HEDGE");\n'
     '   if(!b) Print("Hedge sell failed: ", trade.ResultRetcodeDescription());\n'
     '   if(a != b) { CloseAll(); Print("Hedge: only one of the two trades opened, so it was closed again."); return false; }\n'
     '   return a && b;\n'
     '}'),
    # 5. hard cap: with the take profit beyond the stop loss both trades can lose, so each risks at most half the cap
    ('   double hgS = hg ? HgDist(InpCrkHgSl) : 0, hgT = hg ? HgDist(InpCrkHgTp) : 0;\n',
     '   double hgS = hg ? HgDist(InpCrkHgSl) : 0, hgT = hg ? HgDist(InpCrkHgTp) : 0;\n'
     '   if(hg && InpCapOn && hgT > hgS) rAmt = MathMin(rAmt, InpHardCap / 2.0);   // both trades can lose: the pair stays inside the hard cap\n'),
    # 3. the free margin must carry both trades
    ('   double v = (capStop || crkPs) ? 0 : LotsFor(rAmt, sd, lim, isL, ld);\n',
     '   double v = (capStop || crkPs) ? 0 : LotsFor(rAmt, sd, lim, isL, ld);\n'
     '   if(hg && v > 0)                                   // hedge pair: the free margin must carry both trades\n'
     '   {\n'
     '      double vst = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mg;\n'
     '      if(vst <= 0) vst = vmn > 0 ? vmn : 0.01;\n'
     '      while(v >= vmn && OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, 2 * v, lim, mg) && mg > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v = NormalizeDouble(v - vst, 8);\n'
     '      if(v < vmn) v = 0;\n'
     '   }\n'),
    # 4. one trade of the pair open and the other still waiting: the waiting one is not opened after force-close / weekend / news
    ('   if(flatNow && pos) CloseAll();\n',
     '   if(flatNow && pos) CloseAll();\n'
     '   if(exHg && exState == 2 && (flatNow || newsBlk)) CancelPending();   // hedge pair: a trade still waiting is not opened after force-close, weekend or news\n'),
]
for old, new in REPS:
    n = s.count(old)
    assert n == 1, (n, old[:100])
    s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print(len(REPS), 'replacements; lines', s.count('\n'))
