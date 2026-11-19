"""EA v5.3 (2026-11-19, spec v50/SPEC_v50.md section 7): "Recovery part size": Recalculate after each win (default, = v5.2) / Fixed when
recovery starts (the Crooks C family's part fixed at the first win and kept for the N trades; after the last part a leftover below the base
amount is forgotten, else one more trade for exactly it). Applied to build/bak/AuctionRetestEA_v52.mq5 -> build/safe/AuctionRetestEA.mq5."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
s = open(B + 'bak/AuctionRetestEA_v52.mq5').read()


def sub1(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:100], s.count(a))
    s = s.replace(a, b)


def box(lines):
    return ''.join('//| ' + x.ljust(64) + ' |\n' for x in lines)


sub1('#property version   "5.20"', '#property version   "5.30"')
sub1(box(['the next step ($1,000 by default) up to the best; N trades each.']),
     box(['the next step ($1,000 by default) up to the best; N trades each.']) + box([
         'v5.3: Recovery part size: recalculate after each win (as before)',
         'or fixed when recovery starts (the same amount for the N trades).']))
sub1('TblAdd("AUCTION RETEST", "EA v5.2", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v5.3", white, C\'61,143,214\');')
sub1('''enum ENUM_CRK_XLIM {''', '''enum ENUM_CRK_PART { CPS_RECALC = 0,   // Recalculate after each win
                     CPS_FIXED  = 1 }; // Fixed when recovery starts
enum ENUM_CRK_XLIM {''')
sub1('input int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)\n',
     'input int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)\n'
     'input ENUM_CRK_PART InpCrkPart = CPS_RECALC; // Crooks C (and E-X): recovery part size (fixed: set at the first win, the same for the N trades)\n')
sub1('double   crkL = 0; int crkN = 0; bool crkRec = false;', 'double   crkFx = 0;   // v5.3: the fixed recovery part ($ to win back; 0 = not set)\ndouble   crkL = 0; int crkN = 0; bool crkRec = false;')
sub1('void   CrkCycle() { crkL = 0; crkN = 0; crkP = CrkNp(); crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkHg = false; }',
     'void   CrkCycle() { crkL = 0; crkN = 0; crkP = CrkNp(); crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkHg = false; crkFx = 0; }')
sub1('   crkL = 0; crkN = 0; crkW = false; crkP = 0; crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false;',
     '   crkL = 0; crkN = 0; crkW = false; crkP = 0; crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; crkFx = 0;')
sub1('IoD("kl", crkL);', 'IoD("kl", crkL); IoD("kq", crkFx);')
# sizing: the part
sub1('   double x = crkL / (InpRec == REC_CRB ? InpCSplit : CrkCFam() ? CrkParts() : 1) * (CrkCFam() ? CrkPrPct() : 1.0);',
     '   double x = (CrkCFam() && InpCrkPart == CPS_FIXED && crkFx > 0 ? MathMin(crkFx, crkL) : crkL / (InpRec == REC_CRB ? InpCSplit : CrkCFam() ? CrkParts() : 1)) * (CrkCFam() ? CrkPrPct() : 1.0);   // v5.3: the fixed part')
# booking
sub1('      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = InpRec == REC_CRL ? LParts() : CrkNp(); }',
     '      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = InpRec == REC_CRL ? LParts() : CrkNp(); crkFx = 0; }')
sub1('''      if(xNew) crkP = CrkNp();                          // v5.2 Crooks X: a new step is won back in N trades
''', '''      if(xNew) crkP = CrkNp();                          // v5.2 Crooks X: a new step is won back in N trades
      if(InpCrkPart == CPS_FIXED && CrkCFam())          // v5.3: the recovery part fixed at the first win
      {
         if(!win) crkFx = 0;
         else
         {
            if(xNew) crkFx = 0;
            if(crkRec && lastPart && !xNew)              // the last part won: a leftover below the base amount is forgotten, else one more trade for it
            {
               double bAmt = SizeProfit() ? (exBaseWin > 0 ? exBaseWin : BookBase() * ExitR()) : BookBase();
               if(crkL < bAmt) CrkCycle(); else { crkFx = crkL; crkP = 1; }
            }
            else if(crkFx <= 0) crkFx = crkL / CrkParts();
         }
      }
''')
# table: show the fixed part
sub1('                 (CrkCFam() ? (kRec ? " | recovery trade"', '                 (CrkCFam() && InpCrkPart == CPS_FIXED && crkFx > 0 ? " | part fixed " + DoubleToString(crkFx, 2) : "") +\n                 (CrkCFam() ? (kRec ? " | recovery trade"')
assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(B + 'safe/AuctionRetestEA.mq5', 'w').write(s)
print('EA v5.3 written', s.count('\n'), 'lines')
