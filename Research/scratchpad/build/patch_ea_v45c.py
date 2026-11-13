"""EA v4.5c (the restart parity found it: 48 runs, Crooks J only): StateLoad raised Crooks J's peak to the closed profit at every load, also
for a v4.5 state saved in the middle of a trade whose partial close was already counted, so the peak moved before the trade was booked.
Now only a state saved before v4.5 (no "pk") takes the closed profit as its peak. Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
old = '''   StateIO(false);
   crkPk = MathMax(crkPk, totalNet);                    // a state saved before v4.5 has no peak: the closed profit itself
'''
new = '''   bool pkSaved = GlobalVariableCheck(gSvBase + "pk");  // v4.5: Crooks J's peak (a state saved before v4.5 has none)
   StateIO(false);
   if(!pkSaved) crkPk = MathMax(crkPk, totalNet);      // ... then the closed profit itself is the peak
'''
assert s.count(old) == 1
s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print('1 edit; lines', s.count('\n'))
