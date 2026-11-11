"""EA v4.4d (found with the broker simulator):
1  A setup the EA already traded is never placed again after a restart / new inputs / a timeframe switch. The engine can still show it armed
   (a market entry fills on the engine's next bar; a limit filled early at the broker); v4.3's re-place on the first tick (gRearm) then
   opened a second trade for the same signal. The arm bar time of the last placed setup is saved (gTakenT, "xt"); an order that was still
   waiting when the EA stopped is re-placed as before.
2  OrderExits: MT5 checks the stops of a pending order from its own price and those of a market order from the current price. v4.4 used the
   current price for a pending order too, which pushed the take profit of a buy / sell limit to the current price when the price had already
   run past the target before the retest. A market entry when the price is already past the target is skipped.
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


rep('''int      gTfTrade = 0;                                    // the timeframe the EA trades: the one it was attached to (0 = not known yet)
''', '''int      gTfTrade = 0;                                    // the timeframe the EA trades: the one it was attached to (0 = not known yet)
datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
''')
rep('''//--- an entry order's stop loss and take profit (v4.4: the target goes to the broker with the order): the engine's levels for this setup, kept
//--- outside the stops level from the order price (pending) and the price (market); SetExits re-sends the engine's levels once it has filled
void OrderExits(bool isL, double ep, double &sl, double &tp)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), minD = MinDist();
   sl = exT1 ? exT1Stop : StopPx(isL);
   tp = exT1 ? TgtPx(isL, exT1Tp2) : TgtPx(isL, tF);   // Crooks TP1 rule: the rest's TP2 (its TP1 part closes at market)
   if(isL) { sl = MathMin(sl, FloorTick(MathMin(ep, bid) - minD)); tp = MathMax(tp, CeilTick(MathMax(ep, bid) + minD)); }
   else    { sl = MathMax(sl, CeilTick(MathMax(ep, ask) + minD)); tp = MathMin(tp, FloorTick(MathMin(ep, ask) - minD)); }
}''', '''//--- an entry order's stop loss and take profit (v4.4: the target goes to the broker with the order): the engine's levels for this setup, kept
//--- outside the stops level from what MT5 checks them against: the order's price (pending) or the price that closes the trade (market).
//--- SetExits re-sends the engine's levels once it has filled. false: a market entry with the price already past the target (no entry)
bool OrderExits(bool isL, double ep, bool market, double &sl, double &tp)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), minD = MinDist();
   double ref = market ? (isL ? bid : ask) : ep;
   sl = exT1 ? exT1Stop : StopPx(isL);
   tp = exT1 ? TgtPx(isL, exT1Tp2) : TgtPx(isL, tF);   // Crooks TP1 rule: the rest's TP2 (its TP1 part closes at market)
   if(market && (isL ? ref >= tp : ref <= tp)) return false;
   if(isL) { sl = MathMin(sl, FloorTick(MathMin(ep, ref) - minD)); tp = MathMax(tp, CeilTick(ref + minD)); }
   else    { sl = MathMax(sl, CeilTick(MathMax(ep, ref) + minD)); tp = MathMin(tp, FloorTick(ref - minD)); }
   return true;
}''')
rep('''   double ep = EntryPx(isL), sl, tp;
   double minD = MinDist();
   OrderExits(isL, ep, sl, tp);                        // v4.4: the stop loss and the take profit go with the order
   bool ok;
   if(hg) ok = PlaceHedge(isL, v);
   else if(InpEntryMode == ENTRY_MARKET)
      ok = isL ? trade.Buy(v, _Symbol, 0, sl, tp, "ARM") : trade.Sell(v, _Symbol, 0, sl, tp, "ARM");
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) ok = trade.BuyLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM");
      else if(ask <= ep)                ok = trade.Buy(v, _Symbol, 0, sl, tp, "ARM");   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                  // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) ok = trade.SellLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM");
      else if(bid >= ep)                ok = trade.Sell(v, _Symbol, 0, sl, tp, "ARM");
      else { ok = true; gVirt = true; }
   }
   if(ok) { exState = 1; exArm = armBar; exArmT = BarTimeOf(armBar); exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }
   else { skipN++; skipWhy = "order rejected"; Print("ARM order failed: ", trade.ResultRetcodeDescription()); }''',
    '''   double ep = EntryPx(isL), sl = 0, tp = 0;           // v4.4: the stop loss and the take profit go with the order (OrderExits)
   double minD = MinDist();
   bool ok, past = false;
   if(hg) ok = PlaceHedge(isL, v);
   else if(InpEntryMode == ENTRY_MARKET)
   {
      past = !OrderExits(isL, ep, true, sl, tp);
      ok = !past && (isL ? trade.Buy(v, _Symbol, 0, sl, tp, "ARM") : trade.Sell(v, _Symbol, 0, sl, tp, "ARM"));
   }
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) { OrderExits(isL, ep, false, sl, tp); ok = trade.BuyLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM"); }
      else if(ask <= ep)                { past = !OrderExits(isL, ep, true, sl, tp); ok = !past && trade.Buy(v, _Symbol, 0, sl, tp, "ARM"); }   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                  // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) { OrderExits(isL, ep, false, sl, tp); ok = trade.SellLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM"); }
      else if(bid >= ep)                { past = !OrderExits(isL, ep, true, sl, tp); ok = !past && trade.Sell(v, _Symbol, 0, sl, tp, "ARM"); }
      else { ok = true; gVirt = true; }
   }
   if(ok) { exState = 1; exArm = armBar; exArmT = BarTimeOf(armBar); gTakenT = exArmT; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }
   else if(past) { skipN++; skipWhy = "price already past the target"; }
   else { skipN++; skipWhy = "order rejected"; Print("ARM order failed: ", trade.ResultRetcodeDescription()); }''')
rep('''   double ep = EntryPx(exL), sl, tp;
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      OrderExits(exL, ep, sl, tp);                     // v4.4: the take profit goes with the order
      if(!(exL ? trade.Buy(exLots, _Symbol, 0, sl, tp, "ARM") : trade.Sell(exLots, _Symbol, 0, sl, tp, "ARM")))''',
    '''   double ep = EntryPx(exL), sl = 0, tp = 0;
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      if(!OrderExits(exL, ep, true, sl, tp)) { Print("ARM entry skipped: the price is already past the target."); return; }   // v4.4: the take profit goes with the order
      if(!(exL ? trade.Buy(exLots, _Symbol, 0, sl, tp, "ARM") : trade.Sell(exLots, _Symbol, 0, sl, tp, "ARM")))''')
# the restart memory: the last placed setup
rep('''   IoT("xa", exArmT); IoD("xe", xe); IoD("x1", x1); IoD("x2", x2); IoD("x3", x3);''',
    '''   IoT("xa", exArmT); IoD("xe", xe); IoD("x1", x1); IoD("x2", x2); IoD("x3", x3); IoT("xt", gTakenT);''')
rep('''   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)''',
    '''   if(sx == 1) gTakenT = 0;                             // an order still waiting when the EA stopped: it is placed again (below)
   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)''')
rep('''   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm;   // re-place the engine's armed setup on the first tick (not one armed while paused)''',
    '''   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm && BarTimeOf(armBar) != gTakenT;   // re-place the engine's armed setup on the first tick (not one armed while paused, not one already traded)''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
