"""EA v4.3 review fix: the month's profit, its high and the lock state are saved too. A restored start goes on with the saved month (or a new
month starts, exactly like MonthTick at a month change), so a trade that closed while the EA was off is counted once, by BookClosed, like
after a disconnect. The deal-history rebuild (MonthFromHistory) stays for a start with nothing saved. Must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
REPS = [
    ('   IoI("mk", gMonKey); IoB("mr", monRestPend);\n',
     '   IoI("mk", gMonKey); IoB("mr", monRestPend); IoD("mp", monPnl); IoD("mq", monPeak); IoB("ms", monStop); IoB("ml", monLocked);\n'),
    ('''   int svMon = gMonKey;
   MonthFromHistory();       // this month's closed profit and the monthly locks (a restart in the middle of a month keeps them)
   if(gRestored && InpMRestart && svMon != -1 && svMon != gMonKey) monRestPend = true;   // a new month began while the EA was off
   if(gRestored) RestoreTrade();                         // the saved trade: still open, closed while the EA was off, or gone
''', '''   if(!gRestored) MonthFromHistory();                    // this month's closed profit and the monthly locks from the deal history
   else
   {
      datetime b1 = iTime(_Symbol, _Period, 1);
      MonthTick(UserTime(b1 > 0 ? b1 : TimeCurrent()));  // restored: the saved month goes on, or a new month began while the EA was off (locks start again)
      RestoreTrade();                                    // the saved trade: still open, closed while the EA was off, or gone
   }
'''),
]
for old, new in REPS:
    n = s.count(old); assert n == 1, (n, old[:100]); s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s); print(len(REPS), 'replacements; lines', s.count('\n'))
