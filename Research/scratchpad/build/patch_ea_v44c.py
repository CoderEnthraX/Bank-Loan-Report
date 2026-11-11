"""EA v4.4c: the close report shows the trade's whole P&L (every deal of the position: both commissions, swaps), not only the closing deal's."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0
def rep(old, new):
    global s, n
    c = s.count(old); assert c == 1, (c, old[:100]); s = s.replace(old, new); n += 1
rep('''// one line in the log (Experts tab) and the table for every closing deal of this EA's trades
void CloseReport(ulong tk, double p)
{
   long rs = HistoryDealGetInteger(tk, DEAL_REASON), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   string who = CloseBy(tk);''', '''// one line in the log (Experts tab) and the table for every closing deal of this EA's trades: the trade's P&L from all its deals (n = deals)
void CloseReport(ulong tk, int n)
{
   long rs = HistoryDealGetInteger(tk, DEAL_REASON), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   string who = CloseBy(tk);
   double p = 0;
   for(int i = 0; i < n; i++)
   {
      ulong d = HistoryDealGetTicket(i);
      if(d != 0 && HistoryDealGetInteger(d, DEAL_POSITION_ID) == pid && HistoryDealGetString(d, DEAL_SYMBOL) == _Symbol)
         p += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP) + HistoryDealGetDouble(d, DEAL_FEE);
   }''')
rep('''   Print("Trade #", pid, " closed: ", DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at ", DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),
         ", ", (p >= 0 ? "+" : ""), DoubleToString(p, 2), " | closed by ", who);''',
    '''   Print("Trade #", pid, " closed: ", DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at ", DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),
         " | trade P&L ", (p >= 0 ? "+" : ""), DoubleToString(p, 2), " (costs included) | closed by ", who);''')
rep('''      if(IsExitDeal(tk)) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); if(!quiet) CloseReport(tk, p); }''',
    '''      if(IsExitDeal(tk)) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); if(!quiet) CloseReport(tk, n); }''')
open(P, 'w', encoding='utf8').write(s); print(n, 'edits; lines', s.count('\n'))
