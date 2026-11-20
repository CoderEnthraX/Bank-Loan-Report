"""EA v5.4 (2026-11-20, spec v50/SPEC_v50.md section 8): 10 money rules as Loss Recovery 31 - 40 (Kelly, 1-3-2-6, Equity-curve filter,
Drawdown cut, Cooling-off, Combos C1 - C5). Applied to build/bak/AuctionRetestEA_v53.mq5 -> build/safe/AuctionRetestEA.mq5."""
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
s = open(B + 'bak/AuctionRetestEA_v53.mq5').read()


def sub1(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:100], s.count(a))
    s = s.replace(a, b)


def box(lines):
    return ''.join('//| ' + x.ljust(64) + ' |\n' for x in lines)


sub1('#property version   "5.30"', '#property version   "5.40"')
sub1(box(['or fixed when recovery starts (the same amount for the N trades).']),
     box(['or fixed when recovery starts (the same amount for the N trades).']) + box([
         'v5.4: 10 money rules: Kelly, 1-3-2-6, Equity-curve filter,',
         'Drawdown cut, Cooling-off and the combinations C1 - C5.']))
sub1('TblAdd("AUCTION RETEST", "EA v5.3", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v5.4", white, C\'61,143,214\');')
sub1('   REC_CRX   = 30  // Crooks X (Crooks E, the loss = the gap to the start / the next step)\n', '''   REC_CRX   = 30, // Crooks X (Crooks E, the loss = the gap to the start / the next step)
   REC_KELLY = 31, // Kelly (learned from the last trades)
   REC_1326  = 32, // 1-3-2-6 (after each win)
   REC_EQF   = 33, // Equity-curve filter
   REC_DDCUT = 34, // Drawdown cut
   REC_COOL  = 35, // Cooling-off after losses in a row
   REC_C1    = 36, // Combo 1: Paroli up / brake down
   REC_C2    = 37, // Combo 2: 1-3-2-6 up / small lot down
   REC_C3    = 38, // Combo 3: % of equity + equity-curve filter
   REC_C4    = 39, // Combo 4: Kelly + brake
   REC_C5    = 40  // Combo 5: profit-paid recovery + brake
''')
sub1('input double InpCrkXLimUsd = 500.0; //   ...per-trade limit: a recovery trade risks at most this (account currency, the loss at the stop)\n',
     '''input double InpCrkXLimUsd = 500.0; //   ...per-trade limit: a recovery trade risks at most this (account currency, the loss at the stop)
input double InpMmKFrac  = 0.25;   // Kelly / Combo 4: fraction of the Kelly size (0.25 = quarter Kelly)
input int    InpMmKWin   = 100;    // Kelly / Combo 4: learn from the last this many trades (at most 200)
input int    InpMmKMin   = 30;     // Kelly / Combo 4: trades before Kelly starts (the base until then)
input int    InpMmEqN    = 20;     // Equity-curve filter / Combo 3: average of the last this many closed balances (at most 200)
input double InpMmEqLow  = 0.25;   //   ...size while the balance is under its average (x)
input double InpMmDd1    = 10.0;   // Drawdown cut / brakes: half size from this % below the best
input double InpMmDd2    = 20.0;   // Drawdown cut / brakes: quarter size from this % below the best
input int    InpMmCoolL  = 2;      // Cooling-off: after this many losses in a row ...
input int    InpMmCoolN  = 3;      //   ...skip this many signals
input double InpMmCap    = 3.0;    // Combos 1 - 5: a trade risks at most this % of the equity
input double InpMmC3Pct  = 1.5;    // Combo 3: % of the equity at risk
input double InpMmC5Share = 30.0;  // Combo 5: above the start, the recovery extra at most this % of the profit
''')
sub1('double   crkFx = 0;   // v5.3: the fixed recovery part ($ to win back; 0 = not set)\n', '''double   crkFx = 0;   // v5.3: the fixed recovery part ($ to win back; 0 = not set)
#define  MM_MAX 200
double   mmR[MM_MAX], mmEq[MM_MAX]; int mmRn = 0, mmEn = 0;   // v5.4: the R of the last trades; the closed profit after each trade (none = [0])
int      s1326 = 0, mmLossRow = 0, mmCoolLeft = 0;              // v5.4: 1-3-2-6 step; losses in a row and signals still to skip (Cooling-off)
double   gRisk = 0, exRisk0 = 0;                                // v5.4: the risk NextRisk planned; of the EA's trade (its R = P&L / this)
''')
sub1('''   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
   crkSkip = false; crkSkipLeft = 0;
}''', '''   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
   crkSkip = false; crkSkipLeft = 0; s1326 = 0; mmLossRow = 0; mmCoolLeft = 0;
}''')
sub1('   RecoveryRestart(); gNet0 = totalNet; crkPk = 0; capStop = false;\n', '   RecoveryRestart(); gNet0 = totalNet; crkPk = 0; capStop = false; mmEn = 0;   // v5.4: the balance average starts again\n')
sub1('   crkL = 0; crkN = 0; crkW = false; crkP = 0; crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; crkFx = 0;\n',
     '   crkL = 0; crkN = 0; crkW = false; crkP = 0; crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; crkFx = 0;\n'
     '   mmRn = 0; mmEn = 0; s1326 = 0; mmLossRow = 0; mmCoolLeft = 0; gRisk = 0; exRisk0 = 0;\n')
# helpers before NextRisk
sub1('double NextRisk(double exitR, bool canTake = true, double minRisk = 0, double kRisk = 0)\n{\n', '''//--- v5.4 money rules: the kept R values and closed balances (oldest first), Kelly learned from them, the average closed profit
void   MmPushR(double v)  { if(mmRn >= MM_MAX) { for(int q = 1; q < MM_MAX; q++) mmR[q - 1] = mmR[q]; mmRn = MM_MAX - 1; } mmR[mmRn++] = v; }
void   MmPushEq(double v)
{
   if(mmEn <= 0) { mmEq[0] = 0; mmEn = 1; }
   if(mmEn >= MM_MAX) { for(int q = 1; q < MM_MAX; q++) mmEq[q - 1] = mmEq[q]; mmEn = MM_MAX - 1; }
   mmEq[mmEn++] = v;
}
double MmMA()
{
   if(mmEn <= 0) return 0;
   int n = MathMax(1, MathMin(MathMin(InpMmEqN, MM_MAX), mmEn)); double sm = 0;
   for(int q = mmEn - n; q < mmEn; q++) sm += mmEq[q];
   return sm / n;
}
double MmKelly(double base, double eq, double ml)
{
   if(mmRn < MathMax(1, InpMmKMin)) return base;
   int w0 = MathMax(0, mmRn - MathMax(1, MathMin(InpMmKWin, MM_MAX))), n = mmRn - w0, nw = 0, nl = 0; double sw = 0, sl = 0;
   for(int q = w0; q < mmRn; q++) { if(mmR[q] > 0) { nw++; sw += mmR[q]; } else { nl++; sl += mmR[q]; } }
   double p = (double)nw / n, rw = nw > 0 ? sw / nw : 0, lw = nl > 0 ? -sl / nl : 1.0;
   double f = (rw > 0 && lw > 0) ? MathMax(0.0, (p * rw - (1 - p) * lw) / (rw * lw)) * InpMmKFrac : 0;
   return f > 0 ? f * eq * lw : ml;
}
bool   MmRule() { return InpRec >= REC_KELLY && InpRec <= REC_C5; }
double NextRisk(double exitR, bool canTake = true, double minRisk = 0, double kRisk = 0)
{
   gRisk = 0;
''')
sub1('''      default:        r = base;
   }
   double mul = CrkT1Mult();''', '''      case REC_KELLY:
      case REC_1326:
      case REC_EQF:
      case REC_DDCUT:
      case REC_COOL:
      case REC_C1:
      case REC_C2:
      case REC_C3:
      case REC_C4:
      case REC_C5:
      {
         double eq = AccountInfoDouble(ACCOUNT_EQUITY), nr = totalNet - gNet0, st0 = eq - nr;
         double dd = (crkPk > nr && st0 + crkPk > 0) ? (crkPk - nr) / (st0 + crkPk) : 0;
         double ml = minRisk > 0 ? minRisk : base, ma = MmMA(), u[4] = {1, 3, 2, 6};
         double brake = base * MathMin(1.0, st0 > 0 ? eq / st0 : 1.0) * (dd < InpMmDd2 / 100.0 ? 0.5 : 0.25);
         int k = s1326 < 0 ? 0 : s1326 > 3 ? 3 : s1326;
         if(InpRec == REC_KELLY) r = MmKelly(base, eq, ml);
         else if(InpRec == REC_1326) r = base * u[k];
         else if(InpRec == REC_EQF) r = base * (nr >= ma - 1e-9 ? 1.0 : InpMmEqLow);
         else if(InpRec == REC_DDCUT) r = base * (dd < InpMmDd1 / 100.0 ? 1.0 : dd < InpMmDd2 / 100.0 ? 0.5 : 0.25);
         else if(InpRec == REC_COOL) r = base;
         else if(InpRec == REC_C1) r = nr >= 0 && dd < InpMmDd1 / 100.0 ? base * MathPow(2, parWins) : brake;
         else if(InpRec == REC_C2) r = nr >= 0 ? base * u[k] : MathMin(base, ml);
         else if(InpRec == REC_C3) r = eq * InpMmC3Pct / 100.0 / dv * (nr >= ma - 1e-9 ? 1.0 : InpMmEqLow);
         else if(InpRec == REC_C4) r = MmKelly(base, eq, ml) * (dd >= InpMmDd1 / 100.0 ? 0.5 : 1.0);
         else r = nr >= 0 ? base + MathMin(recPool / MathMax(1, InpRecN) / dv, InpMmC5Share / 100.0 * nr) : brake;
         if(InpRec >= REC_C1) r = MathMin(r, InpMmCap / 100.0 * eq);   // the combinations: never more than Cap % of the equity
         break;
      }
      default:        r = base;
   }
   double mul = CrkT1Mult();''')
sub1('''         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
         r = MathMin(baseC, InpHardCap);''', '''         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
         s1326 = 0; mmLossRow = 0; mmCoolLeft = 0;   // v5.4
         r = MathMin(baseC, InpHardCap);''')
sub1('''      else r = InpHardCap / mul;
   }
   return r;
}''', '''      else r = InpHardCap / mul;
   }
   gRisk = r;                                      // v5.4: the planned risk (a trade's R = its P&L / this)
   return r;
}''')
# take: the small lot for Kelly / C2 / C4, the cooling-off skip, the planned risk
sub1('|| InpRec == REC_CRL || InpRec == REC_CRX || LadOn()) ? MinLotRisk(trRisk) : 0;',
     '|| InpRec == REC_CRL || InpRec == REC_CRX || InpRec == REC_KELLY || InpRec == REC_C2 || InpRec == REC_C4 || LadOn()) ? MinLotRisk(trRisk) : 0;')
sub1('   double kR = InpRec == REC_CRK && InpCrkKMode == CKM_LOTS ? LotRisk(InpCrkKLots, trRisk) : 0;   // v5.0 Crooks K: the careful lots on this setup\n',
     '   if(canTake && InpRec == REC_COOL && mmCoolLeft > 0) { mmCoolLeft--; skipN++; skipWhy = "cooling-off"; return; }   // v5.4: a signal skipped by the cooling-off\n'
     '   double kR = InpRec == REC_CRK && InpCrkKMode == CKM_LOTS ? LotRisk(InpCrkKLots, trRisk) : 0;   // v5.0 Crooks K: the careful lots on this setup\n')
sub1('exBase = gBase; exBaseWin = gBaseWin;\n', 'exBase = gBase; exBaseWin = gBaseWin; exRisk0 = gRisk;\n')
# booking
sub1('   crkW = exHg ? gLastOutProfit > 0 : win;             // hedge pair: the trade that closed last decides (a win -> the next trade is a recovery trade)\n',
     '   crkW = exHg ? gLastOutProfit > 0 : win;             // hedge pair: the trade that closed last decides (a win -> the next trade is a recovery trade)\n'
     '   if(exRisk0 > 0) MmPushR(exPnl / exRisk0);           // v5.4: the trade\'s R, the closed profit after it, 1-3-2-6, Cooling-off\n'
     '   MmPushEq(totalNet - gNet0); s1326 = win ? (s1326 + 1) % 4 : 0;\n'
     '   if(win) mmLossRow = 0; else if(++mmLossRow >= MathMax(1, InpMmCoolL)) { mmCoolLeft = MathMax(0, InpMmCoolN); mmLossRow = 0; }\n')
# memory
sub1('IoD("kl", crkL); IoD("kq", crkFx);', 'IoD("kl", crkL); IoD("kq", crkFx); MmIo();')
sub1('void IoD(string n, double &x)\n', '''void MmIo();
void IoD(string n, double &x)
''')
i = s.index('void IoI(string n, int &x)')
j = s.index('\n', i) + 1
j = s.index('\n', s.index('void IoB(string n, bool &x)')) + 1
s = s[:j] + '''void MmIo()                                             // v5.4: the money rules' state (saved: the counts first, then the values)
{
   IoI("zrn", mmRn); mmRn = mmRn < 0 ? 0 : mmRn > MM_MAX ? MM_MAX : mmRn;
   for(int q = 0; q < mmRn; q++) IoD("zr" + IntegerToString(q), mmR[q]);
   IoI("zen", mmEn); mmEn = mmEn < 0 ? 0 : mmEn > MM_MAX ? MM_MAX : mmEn;
   for(int q = 0; q < mmEn; q++) IoD("ze" + IntegerToString(q), mmEq[q]);
   IoI("z6", s1326); IoI("zlr", mmLossRow); IoI("zcl", mmCoolLeft); IoD("zx0", exRisk0);
}
''' + s[j:]
# checks
sub1('   if(InpRec == REC_CRX && (InpCrkXStep <= 0', '''   if(MmRule() && (InpMmKFrac <= 0 || InpMmKWin < 2 || InpMmKWin > MM_MAX || InpMmKMin < 2 || InpMmEqN < 1 || InpMmEqN > MM_MAX || InpMmEqLow < 0 || InpMmEqLow > 1 ||
      InpMmDd1 <= 0 || InpMmDd2 < InpMmDd1 || InpMmCoolL < 1 || InpMmCoolN < 0 || InpMmCap <= 0 || InpMmC3Pct <= 0 || InpMmC5Share < 0))
   { Print("Money rules: Kelly fraction > 0, learn from 2 - 200 trades, at least 2 to start, average of 1 - 200 balances, reduced size 0 - 1, drawdown steps > 0 (the second not below the first), losses before cooling-off 1 or more, cap and % above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRX && (InpCrkXStep <= 0''')
assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(B + 'safe/AuctionRetestEA.mq5', 'w').write(s)
print('EA v5.4 written', s.count('\n'), 'lines')
