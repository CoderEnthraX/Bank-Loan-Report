"""Fractal Breakout Grid EA v1.1 (asked 2026-11-16): applied by build_ea.py to the generated v1.0 source.
 - PRESET at the top of the inputs: Custom or a grid preset (presets/preset_data.py GRID_PRESETS, the same as the TradingView files): its
   strategies with their tested settings, the entry / exit options as tested (the weekend close stays yours), its money unless "Use my money
   settings", your days and hours only with "Add my days and hours". The rules read gp<Name> (PresetApply(): OnInit and Setup()).
 - Monthly restart (MONEY): every strategy's money starts again at its first trade of a new month (your time zone): the loss recovery,
   the closed profit the profit ladder / Crooks J / Rule C split count from, a hard-cap stop. Saved in the restart memory.
Custom with the restart off = v1.0."""
import re, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/presets')
import preset_data as PD


def presetize(s, S12, TFC):
    def sub1(old, new, cnt=1):
        nonlocal s
        assert s.count(old) == cnt, (old[:90], s.count(old))
        s = s.replace(old, new)
    G = PD.GRID_PRESETS; NG = len(G)
    sub1('#property version   "1.00"', '#property version   "1.10"')
    sub1('''//| managed as the rules say (a missed exit closes it at once).      |
''', '''//| managed as the rules say (a missed exit closes it at once).      |
//|                                                                  |
//| v1.1: PRESET at the top of the inputs: Custom or a tested        |
//| combination of strategies with its money (the $1,000-a-month     |
//| gold study); a monthly restart of every strategy's money.        |
''')
    lab = lambda g: g['name'].replace(' · ', ' - ')
    en = ['enum ENUM_GPRESET { GP_CUSTOM = 0,  // Custom (my settings below)']
    for i, g in enumerate(G, 1):
        en.append('                    GP_%d = %d%s     // %s' % (i, i, ',' if i < NG else ' ', lab(g)))
    en.append('                  };')
    top = '\n'.join(en) + '''
input group "PRESET"
input ENUM_GPRESET InpPreset = GP_CUSTOM; // Preset (its strategies, tested settings and money; weekend close, costs, balance stay yours)
input bool   InpAddMine  = false;  // Add my days and hours to the preset
input bool   InpMyMoney  = false;  // Use my money settings with the preset (base risk, recovery, cap, ladder, monthly restart)

'''
    sub1('input group "GRID"\n', top + 'input group "GRID"\n')
    m = re.search(r'^input ENUM_CAP InpCapAction = CAP_CLAMP;.*$', s, re.M)
    s = s.replace(m.group(0), m.group(0) + '\ninput bool   InpMRestart = false;  // Restart every strategy\'s money on the 1st of each month (your time zone; the balance carries on)')
    names = ['InpRun'] + ['InpS%d%s' % (i, f) for i in range(1, 13) for f in ('On', 'Tf', 'R', 'L', 'Off', 'Sl', 'Tp', 'Be', 'Sv')] + \
            ['InpEntry', 'InpExpN', 'InpMaxDay', 'InpTrA', 'InpTrD', 'InpTExitH', 'InpTrnOn', 'InpDayOn', 'InpHoursOn',
             'InpSizeMode', 'InpBaseRisk', 'InpCapOn', 'InpHardCap', 'InpCapAction', 'InpRec', 'InpLadder', 'InpMRestart']
    types = {}
    for n in names:
        mm = re.findall(r'^input\s+(\w+)\s+%s\s*=' % n, s, re.M)
        assert len(mm) == 1, (n, mm)
        types[n] = mm[0]
    out = []
    for ln in s.split('\n'):
        if not re.match(r'^input\s', ln):
            for n in names: ln = re.sub(r'\b%s\b' % n, 'gp' + n[3:], ln)
        out.append(ln)
    s = '\n'.join(out)
    decl = '//--- v1.1 the values the rules use: the inputs (Custom) or the preset\'s (PresetApply)\n' + ''.join('%s gp%s;\n' % (types[n], n[3:]) for n in names)
    sub1('struct Strat\n{', decl + 'struct Strat\n{')

    def by(vals, lit):
        from collections import Counter
        dflt = Counter(vals).most_common(1)[0][0]; o = lit(dflt); grp = {}
        for i, v in enumerate(vals, 1):
            if v != dflt: grp.setdefault(v, []).append(i)
        for v, ids in sorted(grp.items(), key=lambda kv: -kv[1][0]):
            o = '(%s) ? %s : %s' % (' || '.join('gi == %d' % i for i in ids), lit(v), o)
        return o
    B = lambda b: 'true' if b else 'false'
    F = lambda x: PD.fnum(x)
    ap = ['//--- v1.1: the values the rules use: the inputs (Custom) or the preset\'s (written by fbgea/presetize.py from presets/preset_data.py)',
          'void PresetApply()', '{', '   int gi = (int)InpPreset; bool pc = gi == 0, pm = pc || InpMyMoney;', '   gpRun = pc ? InpRun : RUN_TICKED;']
    for i, p in enumerate(S12, 1):
        tf, r, l, off, sl, tp, be, sv = p
        ap.append('   gpS%dOn = pc ? InpS%dOn : (%s); gpS%dTf = pc ? InpS%dTf : %s; gpS%dR = pc ? InpS%dR : %d; gpS%dL = pc ? InpS%dL : %d;' % (
            i, i, by([i in g['strats'] for g in G], B), i, i, TFC[tf], i, i, r, i, i, l))
        ap.append('   gpS%dOff = pc ? InpS%dOff : %s; gpS%dSl = pc ? InpS%dSl : %s; gpS%dTp = pc ? InpS%dTp : %s; gpS%dBe = pc ? InpS%dBe : %s; gpS%dSv = pc ? InpS%dSv : %s;' % (
            i, i, F(off), i, i, F(sl), i, i, F(tp), i, i, F(be), i, i, F(sv)))
    ap += ['   gpEntry = pc ? InpEntry : ENT_STOP; gpExpN = pc ? InpExpN : 0; gpMaxDay = pc ? InpMaxDay : 0; gpTrA = pc ? InpTrA : 0.0; gpTrD = pc ? InpTrD : 0.0;',
           '   gpTExitH = pc ? InpTExitH : 0.0; gpTrnOn = pc ? InpTrnOn : false;',
           '   gpDayOn = (pc || InpAddMine) && InpDayOn; gpHoursOn = (pc || InpAddMine) && InpHoursOn;',
           '   gpSizeMode = pm ? InpSizeMode : PSZ_USD;',
           '   gpBaseRisk = pm ? InpBaseRisk : (%s);' % by([g['base'] for g in G], F),
           '   gpCapOn = pm ? InpCapOn : (%s);' % by([g['cap'] is not None for g in G], B),
           '   gpHardCap = pm ? InpHardCap : (%s);' % by([g['cap'] or 500.0 for g in G], F),
           '   gpCapAction = pm ? InpCapAction : (ENUM_CAP)(%s);' % by([g['act'] for g in G], lambda a: {'clamp': 'CAP_CLAMP', 'reset': 'CAP_RESET', 'stop': 'CAP_STOP'}[a]),
           '   gpRec = pm ? InpRec : (ENUM_REC)(%s);' % by([g['rec'] for g in G], lambda r: {'EXACT': 'REC_EXACT', 'OFF': 'REC_OFF'}[r]),
           '   gpLadder = pm ? InpLadder : LAD_OFF;',
           '   gpMRestart = pm ? InpMRestart : true;', '}', '']
    pn = ['string PresetName()', '{', '   switch(InpPreset)', '   {'] + \
         ['      case GP_%d: return "%s %s";' % (i, g['key'], lab(g).split(' - ')[0]) for i, g in enumerate(G, 1)] + ['      default: break;', '   }', '   return "Custom";', '}', '']
    sub1('struct Strat\n{', '\n'.join(pn) + 'struct Strat\n{')
    sub1('void Setup()\n{\n', '\n'.join(ap) + 'void Setup()\n{\n   PresetApply();\n')
    m = re.search(r'int OnInit\(\)\n\{\n', s); assert m
    s = s[:m.end()] + '   PresetApply();                                      // v1.1: the preset\'s values (or the inputs) before anything uses them\n' + s[m.end():]
    # ---- the monthly restart
    sub1('   string   stopWhy;\n', '   string   stopWhy;\n   double   n0;                  // v1.1 monthly restart: the closed profit at the last restart (the money rules count from it)\n   int      mKey, curM;          //   the month of the money (yyyymm), this candle\'s month\n   bool     capStp;              //   stopped by the hard cap (ends with the month)\n')
    sub1('s.stopped = false; s.stopWhy = "";\n', 's.stopped = false; s.stopWhy = "";\n   s.n0 = 0; s.mKey = -1; s.curM = -1; s.capStp = false;\n')
    sub1('   cush = on ? MathMax(0.0, s.net - lam * s.peakNet) : 0.0;\n   guard = on && s.net <= 0;', '   cush = on ? MathMax(0.0, s.net - s.n0 - lam * s.peakNet) : 0.0;\n   guard = on && s.net - s.n0 <= 0;')
    sub1('(s.peakNet - s.net) / (InpCrkJX * B)', '(s.peakNet - (s.net - s.n0)) / (InpCrkJX * B)')
    sub1('''   if(s.net >= 1000) { int kk = (int)MathFloor((s.net - 1000.0) / 500.0); stepBase = (1000.0 + 500.0 * kk) / (8.0 + kk); }
   else if(s.net >= 500) stepBase = 500.0 / 5.0;
   else if(s.net >= 200) stepBase = 200.0 / 3.0;''', '''   double netR = s.net - s.n0;                     // v1.1: the closed profit since the monthly restart
   if(netR >= 1000) { int kk = (int)MathFloor((netR - 1000.0) / 500.0); stepBase = (1000.0 + 500.0 * kk) / (8.0 + kk); }
   else if(netR >= 500) stepBase = 500.0 / 5.0;
   else if(netR >= 200) stepBase = 200.0 / 3.0;''')
    sub1('''bool MmOpen(Strat &s, double F)
{
''', '''//--- v1.1 monthly restart: the money starts again (the loss recovery; the closed profit the ladder / Crooks J / Rule C split count from)
void MmMonthReset(Strat &s) { RecReset(s); s.n0 = s.net; s.peakNet = 0; }
bool MmOpen(Strat &s, double F)
{
   if(gpMRestart && s.curM != s.mKey) { if(s.mKey >= 0) MmMonthReset(s); s.mKey = s.curM; }   // v1.1: the first trade of a new month: fresh money
''')
    sub1('{ s.stopped = true; s.stopWhy = "stopped by the hard cap"; take = false; }', '{ s.stopped = true; s.stopWhy = "stopped by the hard cap"; s.capStp = true; take = false; }')
    sub1('   s.peakNet = MathMax(s.peakNet, s.net);\n', '   s.peakNet = MathMax(s.peakNet, s.net - s.n0);\n')
    sub1('   if(s.dPrev < 0 || dno != s.dPrev) { s.dCnt = 0; s.dPrev = dno; }\n', '''   if(s.dPrev < 0 || dno != s.dPrev) { s.dCnt = 0; s.dPrev = dno; }
   s.curM = dno / 100;                                                    // v1.1: this candle's month (your time zone)
   if(gpMRestart && s.capStp && s.mKey >= 0 && s.curM != s.mKey) { s.stopped = false; s.capStp = false; s.stopWhy = ""; }   // a hard-cap stop ends with the month
   if(gpMRestart && !s.pos && s.mKey >= 0 && s.curM != s.mKey) { MmMonthReset(s); s.mKey = s.curM; }   // flat at a new month: the money starts again now (the next lots shown are right)
''')
    sub1('IoD(p + "pn", s.peakNet);', 'IoD(p + "pn", s.peakNet); IoD(p + "n0", s.n0); IoI(p + "mk", s.mKey); IoB(p + "cp", s.capStp);')
    sub1('Row("FRACTAL BREAKOUT GRID EA v1.0 | " + _Symbol', 'Row("FRACTAL BREAKOUT GRID EA v1.1 | " + (InpPreset != GP_CUSTOM ? PresetName() + " | " : "") + _Symbol')
    assert all(ord(ch) < 128 for ch in s), [ln for ln in s.split('\n') if any(ord(c) > 127 for c in ln)][:3]
    return s
