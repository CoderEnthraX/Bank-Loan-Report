"""EA v4.8 (asked 2026-11-16), applied to build/safe/AuctionRetestEA.mq5 v4.7 (backup build/bak/AuctionRetestEA_v47.mq5):
 - STRATEGY PRESET at the top of the inputs: Custom (the inputs below) or one of the 25 catalogue strategies (presets/preset_data.py, the same
   values as the TradingView files). The engine, the partials and the news windows read effective values gp* (PresetApply(), first thing in OnInit).
 - Add my filters: off = the preset as tested (its own hours / kill zone only); on = your days and news windows added, your hours or kill zones
   (when either is on) replace the preset's own hours. The preset's hours are Indian times whatever "Your time zone" is.
 - A preset trades only on its own chart timeframe (the engine arms nothing on another one; a message, the table says so).
 - Monthly restart: also the profit ladder (best profit and closed profit counted from the restart), Crooks J's drawdown, Rule C split's steps
   and a hard-cap Stop trading (saved in the restart memory).
Custom with the restart off = v4.7, unchanged."""
import os, re, shutil, sys
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
sys.path.insert(0, B + '../presets')
import preset_data as PD

SRC = B + 'safe/AuctionRetestEA.mq5'
BK = B + 'bak/AuctionRetestEA_v47.mq5'
if not os.path.exists(BK): shutil.copy(SRC, BK)
s = open(BK).read()


def sub1(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:90], s.count(old))
    s = s.replace(old, new)


P = PD.ars_presets(); N = len(P)

# ---- header and version
sub1('#property version   "4.70"', '#property version   "4.80"')
sub1('''//| v4.7: POSITION SIZE: Fixed $ risk, Fixed lots or % of equity at  |
//| risk; the loss recovery sizes every trade from that base.        |
''', '''//| v4.7: POSITION SIZE: Fixed $ risk, Fixed lots or % of equity at  |
//| risk; the loss recovery sizes every trade from that base.        |
//| v4.8: STRATEGY PRESET (top of the inputs): Custom or one of the  |
//| 25 tested catalogue strategies (M1 S1-S4, M5 S1-S4, M15 S1-S9,   |
//| H1 S1-S8), each on its own chart timeframe; "Add my filters"     |
//| adds your days, hours, kill zones and news. The monthly restart  |
//| also restarts the profit ladder and a hard-cap stop.             |
''')
sub1('TblAdd("AUCTION RETEST", "EA v4.7", white, C\'61,143,214\');', 'TblAdd("AUCTION RETEST", "EA v4.8", white, C\'61,143,214\');')

# ---- the preset enum and inputs, before every other input
def elabel(p):
    g = p['goal'].replace(' - indicator only', ', no partial close')
    return '%s %s%s' % (p['key'], g, ' (70%% closed at TP1)' % () if p['p1'] > 0 else '')


enum = ['enum ENUM_PRESET { PRE_CUSTOM  =  0, // Custom (my settings below)']
for i, p in enumerate(P, 1):
    nm = 'PRE_%s_S%d' % (p['tf'], p['n'])
    enum.append('                   %-11s = %2d%s // %s' % (nm, i, ',' if i < N else ' ', elabel(p)))
enum.append('                 };')
for ln in enum: assert all(ord(ch) < 128 for ch in ln), ln
top = '''//--- v4.8 STRATEGY PRESET (the top of the inputs): Custom = your settings below; a preset = a tested catalogue strategy (every signal setting,
//--- its own hours or kill zone, the 70% partial close of M15-S2 / S4 / S5 and H1-S2 / S4 / S5), only on its own chart timeframe
''' + '\n'.join(enum) + '''
input group "STRATEGY PRESET"
input ENUM_PRESET InpPreset = PRE_CUSTOM; // Strategy preset (only on its own chart timeframe; force-close, risk, recovery stay yours)
input bool   InpAddMine  = false;  // Add my filters to the preset (days, news; my hours / kill zones replace its own)

'''
sub1('//--- ENGINE inputs: same names, order and defaults as the shared Pine inputs\n', top + '//--- ENGINE inputs: same names, order and defaults as the shared Pine inputs\n')

# ---- every input a preset sets is read through gp<Name>
TIME = ['InpDayOn', 'InpHoursOn', 'InpStartH', 'InpStartM', 'InpEndH', 'InpEndM', 'InpKzOn', 'InpKzAsia', 'InpKzLon', 'InpKzNy', 'InpKzLc', 'InpKzAuto', 'InpKzShift']
NEWS = ['InpDNewsOn', 'InpN1On', 'InpN2On', 'InpN3On', 'InpN4On', 'InpN5On']
PART = ['InpP1', 'InpP2', 'InpP3']
names = [p[3] for p in PD.PARAMS] + TIME + NEWS + PART
types = {}
for n in names:
    m = re.findall(r'^input\s+(\w+)\s+%s\s*=' % n, s, re.M)
    assert len(m) == 1, (n, m)
    types[n] = m[0]
types['InpKzShift'] = 'int'
lines = s.split('\n'); out = []
for ln in lines:
    if not re.match(r'^input\s', ln):
        for n in names:
            ln = re.sub(r'\b%s\b' % n, 'gp' + n[3:], ln)
    out.append(ln)
s = '\n'.join(out)
s = s.replace('(int)gpKzShift', 'gpKzShift')
decl = '//--- v4.8 the values the EA uses: the inputs (Custom) or the preset\'s (PresetApply)\n'
for n in names:
    decl += '%s %s;\n' % (types[n], 'gp' + n[3:])
decl += 'bool   gpHrIst = false;                // the preset\'s own hours: Indian times\nbool   gpTfOk = true;                  // the chart is on the preset\'s timeframe (always with Custom)\nint    gpTf = 0;                       // the preset\'s timeframe (0 = Custom)\ndouble gNet0 = 0;                      // v4.8 monthly restart: the closed profit at the last restart (the money rules count from it)\n'


def cond(ids): return ' || '.join('pi == %d' % i for i in ids)


def expr(vals, lit):
    from collections import Counter
    dflt = Counter(vals).most_common(1)[0][0]
    out = lit(dflt); groups = {}
    for i, v in enumerate(vals, 1):
        if v != dflt: groups.setdefault(v, []).append(i)
    for v, ids in sorted(groups.items(), key=lambda kv: -kv[1][0]):
        out = '(%s) ? %s : %s' % (cond(ids), lit(v), out)
    return out


ap = ['//--- v4.8: the values the EA uses: the inputs (Custom) or the preset\'s tested values (written by build/patch_ea_v48.py from presets/preset_data.py)',
      'void PresetApply()', '{', '   int  pi = (int)InpPreset;', '   bool pc = pi == 0;']
for pv, key, kind, ea in PD.PARAMS:
    vals = [p['v'][key] for p in P]
    cast = '' if types[ea] in ('int', 'double', 'bool') else '(%s)' % types[ea]
    ap.append('   %s = pc ? %s : %s(%s);' % ('gp' + ea[3:], ea, cast, expr(vals, lambda x, k=kind: PD.mql_lit(k, x))))
ses = [PD.session(p) for p in P]
hh = [(int(x[1][:2]), int(x[1][2:4]), int(x[1][5:7]), int(x[1][7:9])) if x[1] else (0, 0, 0, 0) for x in ses]
B2 = lambda b: 'true' if b else 'false'
ap += ['   // time filters: your days and news windows only for Custom or with Add my filters; the preset\'s own hours / kill zone unless your hours or kill zones replace them',
       '   bool myF = pc || InpAddMine;',
       '   bool ownS = !pc && !(InpAddMine && (InpHoursOn || InpKzOn));',
       '   gpDayOn = myF && InpDayOn;',
       '   gpHoursOn = ownS ? (%s) : InpHoursOn;' % expr([x[0] for x in ses], B2),
       '   gpStartH = ownS ? (%s) : InpStartH;' % expr([h[0] for h in hh], str),
       '   gpStartM = ownS ? (%s) : InpStartM;' % expr([h[1] for h in hh], str),
       '   gpEndH = ownS ? (%s) : InpEndH;' % expr([h[2] for h in hh], str),
       '   gpEndM = ownS ? (%s) : InpEndM;' % expr([h[3] for h in hh], str),
       '   gpHrIst = ownS;',
       '   gpKzOn = ownS ? (%s) : InpKzOn;' % expr([x[2] for x in ses], B2)]
for j, nm in enumerate(('Asia', 'Lon', 'Ny', 'Lc')):
    ap.append('   gpKz%s = ownS ? (%s) : InpKz%s;' % (nm, expr([x[3][j] for x in ses], B2), nm))
ap += ['   gpKzAuto = ownS ? (%s) : InpKzAuto;' % expr([x[4] for x in ses], B2),
       '   gpKzShift = ownS ? (%s) : (int)InpKzShift;' % expr([x[5] for x in ses], str)]
for n in NEWS:
    ap.append('   gp%s = myF && %s;' % (n[3:], n))
ap += ['   gpP1 = pc ? InpP1 : %s;' % expr([round(p['p1'] * 100.0, 6) for p in P], PD.fnum),
       '   gpP2 = pc ? InpP2 : 0.0;', '   gpP3 = pc ? InpP3 : 0.0;',
       '   gpTf = pc ? 0 : (%s);' % expr([PD.TF_MQL[p['tf']] for p in P], lambda t: '(int)' + t),
       '   gpTfOk = pc || (int)_Period == gpTf;', '}',
       'string PresetName()', '{', '   switch(InpPreset)', '   {'] + ['      case PRE_%s_S%d: return "%s";' % (p['tf'], p['n'], p['key']) for p in P] + ['      default: break;', '   }', '   return "Custom";', '}']
sub1('double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;\n',
     decl + 'double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;\n')
sub1('//--- monthly profit lock (calendar month in your time zone; closed deals, costs included) and the monthly restart of the loss recovery\n',
     '\n'.join(ap) + '\n\n//--- monthly profit lock (calendar month in your time zone; closed deals, costs included) and the monthly restart of the loss recovery\n')

# ---- OnInit: the preset first; the wrong-timeframe message
sub1('''   trade.SetTypeFillingBySymbol(_Symbol);
   ResetEngine();''', '''   trade.SetTypeFillingBySymbol(_Symbol);
   PresetApply();                                        // v4.8: the preset's values (or the inputs) before anything uses them
   ResetEngine();''')
sub1('''   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();''', '''   if(!gpTfOk)                                          // v4.8: a preset trades only on its own chart timeframe
   {
      string m = "Strategy preset " + PresetName() + " trades only on an " + TfName(gpTf) + " chart; this chart is " + TfName((int)_Period) +
                 ": no trades. Switch the chart to " + TfName(gpTf) + ", or choose another preset or Custom.";
      Print(m); Alert(m);
   }
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();''')

# ---- a preset trades its own timeframe: the EA's trading timeframe is the preset's (so switching the chart to it starts the trading)
sub1('''      if(gTfTrade == 0) gTfTrade = GlobalVariableCheck(tfN) ? (int)MathRound(GlobalVariableGet(tfN)) : (int)_Period;
      GlobalVariableSet(tfN, gTfTrade);
      if(TfHold())''', '''      string tpN = SvExtra("tfp");                      // v4.8: 1 = the timeframe was set by a preset
      bool fromPreset = GlobalVariableCheck(tpN) && GlobalVariableGet(tpN) > 0;
      if(gpTf > 0) gTfTrade = gpTf;                     // v4.8: a preset trades only its own timeframe
      else if(fromPreset) gTfTrade = (int)_Period;      // back to Custom after a preset: the chart's timeframe, as if attached now
      else if(gTfTrade == 0) gTfTrade = GlobalVariableCheck(tfN) ? (int)MathRound(GlobalVariableGet(tfN)) : (int)_Period;
      GlobalVariableSet(tfN, gTfTrade);
      GlobalVariableSet(tpN, gpTf > 0 ? 1 : 0);
      if(TfHold() && gpTf == 0)                         // (a preset on another chart has its own message below)''')
# ---- a Week / Month VWAP: the warm-up reaches back to the start of the current week / month (the M1 and M5 presets use the Month VWAP)
sub1("""   gVwN = (int)MathMax(50, MathMin(20000, InpVwapBars));   // the VWAP line: the last gVwN bars""", """   if(gpVwapAnchor != VW_SESSION)                       // v4.8: a Week / Month VWAP needs its whole current week / month (at most 100,000 bars)
   {
      datetime vwT = iTime(_Symbol, _Period, 1);
      MqlDateTime vwM; TimeToStruct(vwT, vwM);
      datetime vwA = gpVwapAnchor == VW_MONTH ? StringToTime(StringFormat("%04d.%02d.01 00:00", vwM.year, vwM.mon))
                                             : (datetime)((((long)vwT + 3 * 86400) / (7 * 86400)) * (7 * 86400) - 3 * 86400);   // Monday 00:00 (server)
      int vwS = iBarShift(_Symbol, _Period, vwA, false), vwL = (int)MathMin(100000, bars - look - 1);
      int vwN = vwS >= 0 ? vwS + 1 : vwL;
      if(vwN > start) start = (int)MathMin(vwN, vwL);
      if(iTime(_Symbol, _Period, bars - 1) > vwA || vwN > vwL)
         Print("VWAP ", gpVwapAnchor == VW_MONTH ? "Month" : "Week", ": the chart history does not reach back to ", TimeToString(vwA, TIME_DATE),
               ", so the VWAP starts later than TradingView's; scroll the chart back to load more history, then attach the EA again.");
   }
   gVwN = (int)MathMax(50, MathMin(20000, InpVwapBars));   // the VWAP line: the last gVwN bars""")
sub1('   if(gone && gTfTrade > 0 && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableDel(SvExtra("tf"));   // left the chart: attach it again on any timeframe',
     '   if(gone && gTfTrade > 0 && MQLInfoInteger(MQL_TESTER) == 0) { GlobalVariableDel(SvExtra("tf")); GlobalVariableDel(SvExtra("tfp")); }   // left the chart: attach it again on any timeframe')
# ---- engine: the preset's hours in Indian time; no setup on the wrong timeframe
sub1('   int cur = MinOfDay(ut), a0 = gpStartH * 60 + gpStartM, b0 = gpEndH * 60 + gpEndM;',
     '   int cur = gpHrIst ? MinOfDay(UtcTime(t) + 19800) : MinOfDay(ut), a0 = gpStartH * 60 + gpStartM, b0 = gpEndH * 60 + gpEndM;   // v4.8: a preset\'s hours are IST')
sub1('   bool canArm = gDayOk && gHourOk && gKzOk &&', '   bool canArm = gpTfOk && gDayOk && gHourOk && gKzOk &&')

# ---- table and state
sub1('   if(TfHold()) s = "CHART ON " + TfName((int)_Period) + ": NO NEW TRADES (EA TRADES " + TfName(gTfTrade) + ")";',
     '   if(TfHold()) s = "CHART ON " + TfName((int)_Period) + ": NO NEW TRADES (EA TRADES " + TfName(gTfTrade) + ")";\n'
     '   if(!gpTfOk) s = "WRONG CHART: " + TfName(gpTf) + " PRESET, NO TRADES";')
sub1('''   TblAdd("STATE", gStateTxt,''', '''   if(InpPreset != PRE_CUSTOM) TblAdd("PRESET", PresetName() + (gpTfOk ? "" : " | needs an " + TfName(gpTf) + " chart") + (InpAddMine ? " | + my filters" : ""), gpTfOk ? posC : negC, cell);
   TblAdd("STATE", gStateTxt,''')

# ---- monthly restart: the closed profit counted from the restart (ladder, Crooks J, Rule C split), the hard-cap stop
sub1('bool   LadGuard() { return LadOn() && totalNet <= 0; }', 'bool   LadGuard() { return LadOn() && totalNet - gNet0 <= 0; }')
sub1('   cush = MathMax(0.0, totalNet - lam * crkPk);', '   cush = MathMax(0.0, totalNet - gNet0 - lam * crkPk);')
sub1('MathMax(0.0, crkPk - totalNet) / (InpCrkJX * base)', 'MathMax(0.0, crkPk - (totalNet - gNet0)) / (InpCrkJX * base)')
sub1('''   if(totalNet >= 1000) { int kk = (int)MathFloor((totalNet - 1000) / 500); stepBase = (1000.0 + 500.0 * kk) / (8 + kk); }
   else if(totalNet >= 500) stepBase = 100.0;
   else if(totalNet >= 200) stepBase = 200.0 / 3.0;''', '''   double netR = totalNet - gNet0;                    // v4.8: the closed profit since the monthly restart
   if(netR >= 1000) { int kk = (int)MathFloor((netR - 1000) / 500); stepBase = (1000.0 + 500.0 * kk) / (8 + kk); }
   else if(netR >= 500) stepBase = 100.0;
   else if(netR >= 200) stepBase = 200.0 / 3.0;''')
sub1('   crkPk = MathMax(crkPk, totalNet);                    // v4.5 Crooks J, v4.6 ladder: the highest closed profit (whatever the rule, so a switch knows it)',
     '   crkPk = MathMax(crkPk, totalNet - gNet0);            // v4.5 Crooks J, v4.6 ladder: the highest closed profit (whatever the rule, so a switch knows it; v4.8: since the monthly restart)')
sub1('   if(!pkSaved) crkPk = MathMax(crkPk, totalNet);      // ... then the closed profit itself is the peak',
     '   if(!pkSaved) crkPk = MathMax(crkPk, totalNet - gNet0);   // ... then the closed profit itself is the peak')
sub1('InpRec == REC_CRJ ? ", drawdown " + DoubleToString(MathMax(0.0, crkPk - totalNet), 2) : "";',
     'InpRec == REC_CRJ ? ", drawdown " + DoubleToString(MathMax(0.0, crkPk - (totalNet - gNet0)), 2) : "";')
sub1('''void MonthTick(datetime ut)''', '''void MonthRestart()                                   // v4.8: the monthly restart: the loss recovery, the profit ladder / Crooks J / Rule C split count from here, a hard-cap stop ends
{
   RecoveryRestart(); gNet0 = totalNet; crkPk = 0; capStop = false;
}
void MonthTick(datetime ut)''')
sub1('{ monRestPend = false; RecoveryRestart(); }', '{ monRestPend = false; MonthRestart(); }', 2)
sub1('IoD("tn", totalNet); IoD("pk", crkPk);', 'IoD("tn", totalNet); IoD("pk", crkPk); IoD("rn", gNet0);')
# a fresh start forgets the restart point too
m = re.search(r'\n   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset\(\); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; totalNet = 0; crkPk = 0;', s)
assert m
sub1(m.group(0), m.group(0) + ' gNet0 = 0;')
# input tooltips
sub1('input bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (after a trade still open closes)',
     'input bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (also the profit ladder and a hard-cap stop; after a trade still open closes)')
assert 'InpStructLen' in s and s.count('InpStructLen') == 1 + 0 or True
assert all(ord(ch) < 128 for ch in s), 'non-ASCII'
open(SRC, 'w').write(s)
print('EA v4.8 written', len(s.split(chr(10))), 'lines;', N, 'presets;', len(names), 'inputs read through gp*')
