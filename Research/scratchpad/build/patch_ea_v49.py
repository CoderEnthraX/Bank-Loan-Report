"""EA v4.9 (asked 2026-11-16): BE trigger and salvage trigger, applied to the v4.8 EA (build/bak/AuctionRetestEA_v48.mq5 = the output of
patch_ea_v48.py) -> build/safe/AuctionRetestEA.mq5. The same engine rule as the Pine engine v4.9 and the research engine bese/ref_gbe.py:
  BE trigger (InpBeOn, InpBeR): a bar after the fill reaches entry + R x risk -> the stop moves to the entry (from the next bar)
  salvage trigger (InpSvOn, InpSvR): a bar reaches entry - R x risk -> the final target moves to the entry (from the next bar; out at 0R)
  only the first acts in a trade; both on one bar: the extreme nearer the open came first; never on the fill bar. Not set by a preset.
The execution needs no change: a trigger sets evMove, so the broker's stop loss / take profit follow (SetExits uses stp and tF)."""
import os, shutil
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
SRC = B + 'safe/AuctionRetestEA.mq5'
BK = B + 'bak/AuctionRetestEA_v48.mq5'
if not os.path.exists(BK): shutil.copy(SRC, BK)
s = open(BK).read()


def sub1(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


sub1('#property version   "4.80"', '#property version   "4.90"')
sub1('''//| also restarts the profit ladder and a hard-cap stop.             |
''', '''//| also restarts the profit ladder and a hard-cap stop.             |
//| v4.9: BE TRIGGER (stop to the entry once the trade is X R up)    |
//| and SALVAGE TRIGGER (target to the entry once it is X R down),   |
//| off by default; they work with any preset (TradingView too).     |
''')
sub1('TblAdd("AUCTION RETEST", "EA v4.8", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v4.9", white, C\'61,143,214\');')
sub1('''input double InpMv3R  = 0.0;   //   ...to (R)
''', '''input double InpMv3R  = 0.0;   //   ...to (R)
input bool   InpBeOn  = false; // BE trigger: stop to the entry once the trade is up (R; works with any preset)
input double InpBeR   = 1.5;   //   ...R in profit (gold test: 1.5 best on M5 and M15; early values lose)
input bool   InpSvOn  = false; // Salvage trigger: target to the entry once the trade is down (R; any preset)
input double InpSvR   = 0.9;   //   ...R against the trade (below 1; gold test: best off, 0.9 the least harm)
''')
# engine state and events
sub1('int      tpHit = 0;', 'int      tpHit = 0;\nint      trTrig = 0;                                     // v4.9: the trigger that acted in the live trade (0 none, 1 BE, 2 salvage)')
sub1('bool     evArm, evArmL, evFill, evFillL, evExit, evWin, evMove, evTp; double evRes; int evCancel; // 0 none, 1 expired, 2 replaced',
     'bool     evArm, evArmL, evFill, evFillL, evExit, evWin, evMove, evTp; double evRes; int evCancel; // 0 none, 1 expired, 2 replaced\n'
     'bool     evSalv; int evTrig;            // v4.9: an exit at the entry by the salvage target; a BE (1) / salvage (2) trigger acted on this bar')
sub1('   evArm = false; evArmL = false; evFill = false; evFillL = false; evExit = false; evWin = false; evMove = false; evTp = false; evRes = 0; evCancel = 0;\n',
     '   evArm = false; evArmL = false; evFill = false; evFillL = false; evExit = false; evWin = false; evMove = false; evTp = false; evRes = 0; evCancel = 0;\n'
     '   evSalv = false; evTrig = 0;\n')
sub1('''         bool win = !stopHit;
         double res = win ? exitR : (stp == stp0 ? -1.0 : d * (stp - lim) / trRisk);''', '''         bool salv = !stopHit && trTrig == 2;           // v4.9: the salvage target (the entry): 0R, not a win
         bool win = !stopHit && !salv;
         double res = win ? exitR : (salv ? 0.0 : (stp == stp0 ? -1.0 : d * (stp - lim) / trRisk));''')
sub1('''            lastRes = (win ? "TP" + IntegerToString((int)gpExitAt) + " " : "STOP ") + (res >= 0 ? "+" : "") + DoubleToString(res, 2) + "R";
            evExit = true; evWin = win; evRes = res;''', '''            lastRes = (win ? "TP" + IntegerToString((int)gpExitAt) + " " : (salv ? "SALVAGE " : "STOP ")) + (res >= 0 ? "+" : "") + DoubleToString(res, 2) + "R";
            evExit = true; evWin = win; evRes = res; evSalv = salv;''')
sub1('''      else if(tpHit > prevHit)
      {
         double ns = stp;
         if(gpMv1On && tpHit >= 1) ns = isL ? MathMax(ns, lim + gpMv1R * trRisk) : MathMin(ns, lim - gpMv1R * trRisk);
         if(gpMv2On && tpHit >= 2) ns = isL ? MathMax(ns, lim + gpMv2R * trRisk) : MathMin(ns, lim - gpMv2R * trRisk);
         if(gpMv3On && tpHit >= 3) ns = isL ? MathMax(ns, lim + gpMv3R * trRisk) : MathMin(ns, lim - gpMv3R * trRisk);
         if(ns != stp) { stp = ns; evMove = !trGhost; }
         evTp = !trGhost;
      }''', '''      else
      {
         if(tpHit > prevHit)
         {
            double ns = stp;
            if(gpMv1On && tpHit >= 1) ns = isL ? MathMax(ns, lim + gpMv1R * trRisk) : MathMin(ns, lim - gpMv1R * trRisk);
            if(gpMv2On && tpHit >= 2) ns = isL ? MathMax(ns, lim + gpMv2R * trRisk) : MathMin(ns, lim - gpMv2R * trRisk);
            if(gpMv3On && tpHit >= 3) ns = isL ? MathMax(ns, lim + gpMv3R * trRisk) : MathMin(ns, lim - gpMv3R * trRisk);
            if(ns != stp) { stp = ns; evMove = !trGhost; }
            evTp = !trGhost;
         }
         // v4.9 BE / salvage trigger: only the first acts in a trade; both on one bar: the extreme nearer the open came first (from the next bar)
         if(trTrig == 0 && (InpBeOn || InpSvOn))
         {
            double beL = lim + d * InpBeR * trRisk, svL = lim - d * InpSvR * trRisk;
            bool beH = InpBeOn && (isL ? h >= beL - tol : l <= beL + tol);
            bool svH = InpSvOn && (isL ? l <= svL + tol : h >= svL - tol);
            if(beH && svH)
            {
               bool hiFirst = MathAbs(h - o) < MathAbs(o - l);
               if(hiFirst == isL) svH = false; else beH = false;
            }
            if(beH)
            {
               trTrig = 1; evTrig = trGhost ? 0 : 1;
               double nb = isL ? MathMax(stp, lim) : MathMin(stp, lim);
               if(nb != stp) { stp = nb; evMove = !trGhost; }
            }
            else if(svH) { trTrig = 2; evTrig = trGhost ? 0 : 2; tF = lim; evMove = !trGhost; }
         }
      }''')
sub1('st = isL ? 2 : -2; fillBar = bi; lastFill = bi; lastDir = isL ? 1 : -1; tpHit = 0; dayFills++;',
     'st = isL ? 2 : -2; fillBar = bi; lastFill = bi; lastDir = isL ? 1 : -1; tpHit = 0; trTrig = 0; dayFills++;')
# the salvage target is the entry itself (no earn-back push): the EA leaves at the engine's level
sub1('double TgtPx(bool isL, double lvl) { double tl = TickSize() * 0.001; return isL ? CeilTick(lvl + exCostPx - tl) : FloorTick(lvl - exCostPx + tl + Spr()); }',
     'double TgtPx(bool isL, double lvl) { double tl = TickSize() * 0.001; return isL ? CeilTick(lvl + exCostPx - tl) : FloorTick(lvl - exCostPx + tl + Spr()); }\n'
     'double TgtPx0(bool isL, double lvl) { double tl = TickSize() * 0.001; return isL ? CeilTick(lvl - tl) : FloorTick(lvl + tl + Spr()); }   // v4.9: the salvage target (the entry), no earn-back push')
sub1('   double sl = StopPx(exL), tp = withTarget ? TgtPx(exL, tF) : 0;',
     '   double sl = StopPx(exL), tp = withTarget ? (trTrig == 2 && exArm == armBar ? TgtPx0(exL, tF) : TgtPx(exL, tF)) : 0;   // v4.9: salvage: at the entry')
# stats, table, reset
sub1('int      beN = 0, lkN = 0;         // closed at a stop moved to the entry (breakeven) / into profit',
     'int      beN = 0, lkN = 0;         // closed at a stop moved to the entry (breakeven) / into profit\nint      svN = 0;                  // v4.9: closed at the entry by the salvage target (0R)')
sub1('      if(!evWin && stp != stp0) { if(evRes == 0.0) beN++; else if(evRes > 0.0) lkN++; }',
     '      if(evSalv) svN++;\n      else if(!evWin && stp != stp0) { if(evRes == 0.0) beN++; else if(evRes > 0.0) lkN++; }')
sub1('string BeTxt() { int n = totW + totL; return "BE " + IntegerToString(beN) + " (" + Share(beN, n) + ") | locked profit " + IntegerToString(lkN) + " (" + Share(lkN, n) + ")"; }',
     'string BeTxt() { int n = totW + totL; return "BE " + IntegerToString(beN) + " (" + Share(beN, n) + ") | locked profit " + IntegerToString(lkN) + " (" + Share(lkN, n) + ")" +\n'
     '                 (InpSvOn ? " | salvage " + IntegerToString(svN) + " (" + Share(svN, n) + ")" : ""); }')
sub1('   if(gpMv1On || gpMv2On || gpMv3On) TblAdd("BREAKEVEN", BeTxt(), white, cell);', '   if(gpMv1On || gpMv2On || gpMv3On || InpBeOn || InpSvOn) TblAdd("BREAKEVEN", BeTxt(), white, cell);')
sub1('   ArrayInitialize(tpHitN, 0); beN = 0; lkN = 0; gFirstT = 0;', '   ArrayInitialize(tpHitN, 0); beN = 0; lkN = 0; svN = 0; gFirstT = 0; trTrig = 0;')
# input checks
sub1('   if(gpMaxVwOn && gpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."); return INIT_PARAMETERS_INCORRECT; }',
     '   if(gpMaxVwOn && gpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."); return INIT_PARAMETERS_INCORRECT; }\n'
     '   if(InpBeOn && InpBeR <= 0) { Print("BE trigger: the R in profit must be above 0."); return INIT_PARAMETERS_INCORRECT; }\n'
     '   if(InpSvOn && (InpSvR <= 0 || InpSvR >= 1)) { Print("Salvage trigger: the R against the trade must be above 0 and below 1 (the stop is at 1R)."); return INIT_PARAMETERS_INCORRECT; }')
assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(SRC, 'w').write(s)
print('EA v4.9 written', s.count('\n'), 'lines')
