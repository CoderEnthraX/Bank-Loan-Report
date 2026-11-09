"""EA v4.3 review fix: the saved state is named by symbol and magic number only (the account login can still be 0 when the EA starts with
MT5, before the connection); the account is saved as a value, and a state saved by another account is not loaded. Must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
REPS = [
    ('''string SvBaseName()                                     // ARS|symbol|magic|account| (a short hash when that is too long: names have at most 63 characters)
{
   string acc = IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
   string b = "ARS|" + _Symbol + "|" + IntegerToString(InpMagic) + "|" + acc + "|";
   if(StringLen(b) <= 57) return b;
   string k = _Symbol + "|" + IntegerToString(InpMagic) + "|" + acc;
''', '''string SvBaseName()                                     // ARS|symbol|magic| (a short hash when that is too long: names have at most 63 characters)
{
   string b = "ARS|" + _Symbol + "|" + IntegerToString(InpMagic) + "|";
   if(StringLen(b) <= 57) return b;
   string k = _Symbol + "|" + IntegerToString(InpMagic);
'''),
    ('variables (Tools -> Global Variables, F3; names ARS|symbol|magic|account|...) whenever they',
     'variables (Tools -> Global Variables, F3; names ARS|symbol|magic|...) whenever they'),
    ('''   IoT("lb", lb); IoT("sv", sv);
''', '''   IoT("lb", lb); IoT("sv", sv);
   double acc = (double)AccountInfoInteger(ACCOUNT_LOGIN); IoD("acc", acc);   // the account it belongs to (checked when loading)
'''),
    ('''   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer()) return false;
   StateIO(false);
''', '''   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer()) return false;
   double svAcc = GlobalVariableCheck(gSvBase + "acc") ? GlobalVariableGet(gSvBase + "acc") : 0, nowAcc = (double)AccountInfoInteger(ACCOUNT_LOGIN);
   if(svAcc != 0 && nowAcc != 0 && svAcc != nowAcc)    // saved by another account (same symbol and magic number): start fresh
   {
      Print("Restart memory: the saved state belongs to account ", (long)svAcc, ", not ", (long)nowAcc, ": starting fresh.");
      return false;
   }
   StateIO(false);
'''),
]
for old, new in REPS:
    n = s.count(old); assert n == 1, (n, old[:100]); s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s); print(len(REPS), 'replacements; lines', s.count('\n'))
