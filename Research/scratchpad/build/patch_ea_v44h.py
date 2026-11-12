"""EA v4.4h: CloseAll prints one 'Closing #...' line for every position it closes (a hedge pair: both trades), with the reason."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
old = '''   if(HasPosition(tk, v, op)) { gCloseWhy = why; Print("Closing #", tk, " (", DoubleToString(v, 2), " lots): ", why); }
   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      NoteClose(PositionGetInteger(POSITION_IDENTIFIER));'''
new = '''   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      gCloseWhy = why; NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
      Print("Closing #", tk, " (", DoubleToString(v, 2), " lots): ", why);'''
assert s.count(old) == 1
s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print('1 edit; lines', s.count('\n'))
