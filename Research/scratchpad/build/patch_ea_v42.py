"""EA v4.2: the same MONTHLY PROFIT LOCK settings as the TradingView strategy v4.2: stop for the month once it is up $X, lock P% of the month's
highest closed profit once it is up $Y (stop when it falls back there), restart the loss recovery on the 1st (once no trade of the old month is
left). Calendar month in your time zone, closed deals incl. costs; rebuilt from the deal history after a restart. Every replacement must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
W = len('//| v3.9: Crooks C rule after N losing recovery trades in a row:     |')
def hl(t):
    line = '//| ' + t
    assert len(line) <= W - 2, t
    return line.ljust(W - 1) + '|'
hdr_old = '//| profit; then forget the loss, or go on from the last trade.      |\n'
hdr_new = hdr_old + '\n'.join(hl(t) for t in (
    'v4.2: MONTHLY PROFIT LOCK (same as the TradingView strategy):',
    'stop for the month once it is up $X; lock a % of the month\'s',
    'profit once it is up $Y; restart the loss recovery on the 1st.')) + '\n'
FUNCS = r'''//--- monthly profit lock (calendar month in your time zone; closed deals, costs included) and the monthly restart of the loss recovery
void RecoveryRestart()                                // like the hard cap's Start again: the loss recovery starts again from the base risk
{
   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
   crkSkip = false; crkSkipLeft = 0;
}
void MonthTick(datetime ut)                           // a new month: the locks start again; the recovery restart waits until no trade of the old month is left
{
   MqlDateTime d; TimeToStruct(ut, d);
   int k = d.year * 100 + d.mon;
   if(gMonKey != -1 && k != gMonKey) { monPnl = 0; monPeak = 0; monStop = false; monLocked = false; if(InpMRestart) monRestPend = true; }
   gMonKey = k;
}
void MonthCheck()                                     // stop for the month at the lock amount, or when the profit falls back to the locked part of its high
{
   if(InpMLockOn && monPnl >= InpMLockAmt) monStop = true;
   if(InpPLockOn)
   {
      monPeak = MathMax(monPeak, monPnl);
      if(monPnl >= InpPLockAt) monLocked = true;
      if(monLocked && monPnl <= InpPLockPct / 100.0 * monPeak) monStop = true;
   }
}
void MonthFromHistory()                               // after a restart: this month's closed profit, its high and the locks from the deal history
{
   datetime now = TimeCurrent(); MqlDateTime d; TimeToStruct(UserTime(now), d);
   gMonKey = d.year * 100 + d.mon; d.day = 1; d.hour = 0; d.min = 0; d.sec = 0;
   datetime from = StructToTime(d) - (datetime)(InpUserGMT * 3600) + (datetime)(SrvGMT(now) * 3600);
   monPnl = 0; monPeak = 0; monLocked = false; monStop = false;
   if(!HistorySelect(from, now + 86400)) return;
   int n = HistoryDealsTotal();
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      monPnl += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      long e = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY) MonthCheck();
   }
}

'''
REPS = [
    (hdr_old, hdr_new),
    ('#property version   "4.10"', '#property version   "4.20"'),
    ('TblAdd("AUCTION RETEST", "EA v4.1"', 'TblAdd("AUCTION RETEST", "EA v4.2"'),
    ('input int  InpPauseDays = 1;   //   Days to pause (1-3)\n',
     'input int  InpPauseDays = 1;   //   Days to pause (1-3)\n\n'
     'input group "MONTHLY PROFIT LOCK"\n'
     'input bool   InpMLockOn  = false;  // Stop for the month once it is up (closed profit this month, your time zone)\n'
     'input double InpMLockAmt = 150.0;  //   amount (account currency)\n'
     'input bool   InpPLockOn  = false;  // Lock profit once the month is up (stop when it falls back to the locked part)\n'
     'input double InpPLockAt  = 500.0;  //   amount (account currency)\n'
     'input double InpPLockPct = 20.0;   //   lock % of the month\'s highest profit (rises with new highs)\n'
     'input bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (after a trade still open closes)\n'),
    ('bool     gHedgeOk = false; ',
     'int      gMonKey = -1;                                    // monthly lock: the month (your time zone) of the last processed bar\n'
     'double   monPnl = 0, monPeak = 0;                         //   this month\'s closed profit (costs included) and its high\n'
     'bool     monStop = false, monLocked = false, monRestPend = false;   //   no new trades until next month; profit lock armed; restart the recovery once flat\n'
     'bool     gHedgeOk = false; '),
    ('//--- risk $ for the next trade (loss recovery + hard cap) -------------------\n', FUNCS + '//--- risk $ for the next trade (loss recovery + hard cap) -------------------\n'),
    ('dayBlock || crkPs);   // the hard cap acts only on a sig', 'dayBlock || crkPs || monStop);   // the hard cap acts only on a sig'),
    ('crkPs ? "Crooks C pause" : v <= 0 ? "size 0" : ""', 'crkPs ? "Crooks C pause" : monStop ? "monthly lock" : v <= 0 ? "size 0" : ""'),
    ('CrkPause() ? "CROOKS C PAUSE (" + IntegerToString(crkSkipLeft) + "d left)" : dayBlock',
     'CrkPause() ? "CROOKS C PAUSE (" + IntegerToString(crkSkipLeft) + "d left)" : monStop ? "MONTHLY LOCK (until the 1st)" : dayBlock'),
    ('TblAdd("DAY P&L | FILLS", DoubleToString(dayPnl, 2) + " | " + IntegerToString(dayFills) + "/" + IntegerToString(InpMaxFills), dayPnl >= 0',
     'TblAdd("DAY P&L | FILLS", DoubleToString(dayPnl, 2) + " | " + IntegerToString(dayFills) + "/" + IntegerToString(InpMaxFills) + (InpMLockOn || InpPLockOn ? " | month " + DoubleToString(monPnl, 2) + (monLocked ? " (locked " + DoubleToString(InpPLockPct / 100.0 * monPeak, 2) + ")" : "") : ""), dayPnl >= 0'),
    ('   datetime ut = UserTime(bt), utPrev = UserTime(gPrevT > 0 ? gPrevT : iTime(_Symbol, _Period, 2));\n',
     '   datetime ut = UserTime(bt), utPrev = UserTime(gPrevT > 0 ? gPrevT : iTime(_Symbol, _Period, 2));\n'
     '   MonthTick(ut);                                     // a new month (your time zone): its closed deals count from this bar on\n'),
    ('   exPnl += newPnl; totalNet += newPnl;\n', '   exPnl += newPnl; totalNet += newPnl; monPnl += newPnl;\n'),
    ('   if(exClosed) BookClosed();\n',
     '   if(exClosed) BookClosed();\n'
     '   if(monRestPend && exState == 0 && !pos) { monRestPend = false; RecoveryRestart(); }   // monthly restart, once no trade of the old month is left\n'
     '   MonthCheck();\n'),
    ('   bool c; NewDealsPnl(c);   // do not count old history\n',
     '   bool c; NewDealsPnl(c);   // do not count old history\n'
     '   MonthFromHistory();       // this month\'s closed profit and the monthly locks (a restart in the middle of a month keeps them)\n'),
    ('   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0 || InpCrkHgTp <= 0))',
     '   if((InpMLockOn && InpMLockAmt <= 0) || (InpPLockOn && (InpPLockAt <= 0 || InpPLockPct <= 0 || InpPLockPct > 100))) { Print("Monthly profit lock: the amounts must be above 0 and the lock % 1 to 100."); return INIT_PARAMETERS_INCORRECT; }\n'
     '   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0 || InpCrkHgTp <= 0))'),
]
for old, new in REPS:
    n = s.count(old)
    assert n == 1, (n, old[:100])
    s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print(len(REPS), 'replacements; lines', s.count('\n'))
