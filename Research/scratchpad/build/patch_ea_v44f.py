"""EA v4.4f (own read-through of the full diff):
1  The close report knows the last 8 positions this EA closed (CloseAll and partial closes), so both trades of a hedge pair closed together
   are reported as this EA's (before: the first one read "an EA with this magic number").
2  BrokerStart re-reads the account's margin mode once MT5 is connected (a start before the connection may not know it yet): hedging decides
   whether closes by hand / other EAs are matched by position id.
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


rep('''string   gCloseWhy = ""; long gCloseId = 0;                // why this EA closed a trade last, and that trade's position id
''', '''string   gCloseWhy = ""; long gCloseId = 0;                // why this EA closed a trade last, and that trade's position id
long     gClosedIds[8]; int gClosedN = 0;                 // the last positions this EA closed (fully or partly): their reports say "this EA"
''')
rep('''void CloseAll(string why)
{''', '''void NoteClose(long pid) { gCloseId = pid; gClosedIds[gClosedN % 8] = pid; gClosedN++; }   // a position this EA closes now (fully or partly)
bool ClosedByUs(long pid) { for(int q = 0; q < 8; q++) if(gClosedIds[q] == pid && pid > 0) return true; return false; }
void CloseAll(string why)
{''')
# CloseAll and the partial closes note the position id
rep('''   if(HasPosition(tk, v, op)) { gCloseWhy = why; gCloseId = PositionGetInteger(POSITION_IDENTIFIER); Print("Closing #", tk, " (", DoubleToString(v, 2), " lots): ", why); }
   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      gCloseId = PositionGetInteger(POSITION_IDENTIFIER);''', '''   if(HasPosition(tk, v, op)) { gCloseWhy = why; Print("Closing #", tk, " (", DoubleToString(v, 2), " lots): ", why); }
   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      NoteClose(PositionGetInteger(POSITION_IDENTIFIER));''')
rep('''      gCloseWhy = "Crooks TP1 rule: the TP1 part"; if(PositionSelectByTicket(tk)) gCloseId = PositionGetInteger(POSITION_IDENTIFIER);''',
    '''      gCloseWhy = "Crooks TP1 rule: the TP1 part"; if(PositionSelectByTicket(tk)) NoteClose(PositionGetInteger(POSITION_IDENTIFIER));''')
rep('''            gCloseWhy = "partial close at TP" + IntegerToString(k + 1); if(PositionSelectByTicket(tk)) gCloseId = PositionGetInteger(POSITION_IDENTIFIER);''',
    '''            gCloseWhy = "partial close at TP" + IntegerToString(k + 1); if(PositionSelectByTicket(tk)) NoteClose(PositionGetInteger(POSITION_IDENTIFIER));''')
# the report uses the list
rep('''             pid == gCloseId && gCloseWhy != "" ? "this EA: " + gCloseWhy : "an EA with this magic number (a second copy of this EA?)";''',
    '''             ClosedByUs(pid) && gCloseWhy != "" ? "this EA: " + gCloseWhy : "an EA with this magic number (a second copy of this EA?)";''')
rep('''   gLastCloseOut = !(rs == DEAL_REASON_SL || rs == DEAL_REASON_TP || (rs == DEAL_REASON_EXPERT && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && pid == gCloseId));''',
    '''   gLastCloseOut = !(rs == DEAL_REASON_SL || rs == DEAL_REASON_TP || (rs == DEAL_REASON_EXPERT && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && ClosedByUs(pid)));''')
# the margin mode once connected
rep('''   TzPick(false);                                        // the broker's clock, now that MT5 is connected''',
    '''   TzPick(false);                                        // the broker's clock, now that MT5 is connected
   gHedgeOk = (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;   // known for sure once connected''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
