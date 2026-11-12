"""EA v4.4i: a setup decided on while the chart shows another timeframe (no new trades then) is not remembered as decided: M5 bar times are
also M1 bar times, so a skipped M1 setup at 09:05 would otherwise keep the M5 setup armed at 09:05 from being placed back on M5."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
old = '''   gTakenT = BarTimeOf(armBar);                       // decided on now (taken, skipped or rejected): a restart does not take it again'''
new = '''   if(!TfHold()) gTakenT = BarTimeOf(armBar);         // decided on now (taken, skipped or rejected): a restart does not take it again (not on another timeframe)'''
assert s.count(old) == 1
s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print('1 edit; lines', s.count('\n'))
