"""EA v4.6b: every local variable of the profit-ladder code starts with a value (split declarations), so MetaEditor cannot report
"possible use of uninitialized variable". No change in behaviour. Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''   if(!LadOn()) return InpBaseRisk;
   double lam, phi, bmax, gam; LadPar(lam, phi, bmax, gam);''', '''   if(!LadOn()) return InpBaseRisk;
   double lam = 0, phi = 0, bmax = 0, gam = 0; LadPar(lam, phi, bmax, gam);''')
rep('''   double cush, b = LadBase(cush), lam, phi, bmax, gam; LadPar(lam, phi, bmax, gam);
   return lv + " | lock "''', '''   double cush = 0, lam = 0, phi = 0, bmax = 0, gam = 0;
   double b = LadBase(cush); LadPar(lam, phi, bmax, gam);
   return lv + " | lock "''')
rep('''            double cush, lb = LadBase(cush), lam, phi, bmax, gam; LadPar(lam, phi, bmax, gam);''',
    '''            double cush = 0, lam = 0, phi = 0, bmax = 0, gam = 0;
            double lb = LadBase(cush); LadPar(lam, phi, bmax, gam);''')
rep('''   double lCu;
''', '''   double lCu = 0;
''')
rep('''   double gCush;
''', '''   double gCush = 0;
''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
