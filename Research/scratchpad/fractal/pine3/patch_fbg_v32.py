"""Fractal Breakout Grid v3.2 (asked 2026-11-16), applied to the v3.1 generator (backup pine3/build_fbg3_pre32.py) -> pine3/build_fbg3.py:
 - PRESET at the top of the settings: Custom (your settings) or one of the grid presets (presets/preset_data.py GRID_PRESETS): its strategies with
   their tested settings, the entry / exit options as tested (the weekend close stays yours), its money (fixed $ base, loss recovery, hard cap,
   profit ladder off, monthly restart on) unless "Use My Money Settings"; your days and hours only with "Add My Days And Hours".
 - Monthly restart (MONEY): every strategy's money starts again at its first trade of a new month (time zone of DAYS AND HOURS): the loss
   recovery, the profit ladder / Crooks J / Rule C split count the closed profit from there, a hard-cap stop ends. The balance carries on.
Custom with the restart off = v3.1."""
import os, re, shutil, sys
H = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal/pine3/'
sys.path.insert(0, H + '../../presets')
import preset_data as PD
if not os.path.exists(H + 'build_fbg3_pre32.py'): shutil.copy(H + 'build_fbg3.py', H + 'build_fbg3_pre32.py')
s = open(H + 'build_fbg3_pre32.py').read()


def sub1(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:90], s.count(old))
    s = s.replace(old, new)


G = PD.GRID_PRESETS; NG = len(G)
# ---- the strategy blocks: inputs <name>In (the effective values follow all blocks)
for a, b in (('s{i}On  = input.bool', 's{i}OnIn = input.bool'), ('s{i}Tf  = input.timeframe', 's{i}TfIn = input.timeframe'),
             ('s{i}Off = input.float', 's{i}OffIn = input.float'), ('s{i}R   = input.int', 's{i}RIn = input.int'), ('s{i}L   = input.int', 's{i}LIn = input.int'),
             ('s{i}Sl  = input.float', 's{i}SlIn = input.float'), ('s{i}Tp  = input.float', 's{i}TpIn = input.float'), ('s{i}Be  = input.float', 's{i}BeIn = input.float'),
             ('s{i}Sv  = input.float', 's{i}SvIn = input.float')):
    sub1(a, b)

# ---- header: version, the preset inputs first, renamed inputs, the monthly restart input
sub1('//  FRACTAL BREAKOUT GRID v3.1: 12 long', '//  FRACTAL BREAKOUT GRID v3.2: 12 long')
sub1('''//  from); a red note on the chart when a ticked strategy cannot run on the chart's timeframe.
''', '''//  from); a red note on the chart when a ticked strategy cannot run on the chart's timeframe.
//  v3.2: PRESET at the top of the settings: Custom or a tested combination of strategies with its money (the $1,000-a-month
//  study); a monthly restart of every strategy's money (the same in the MT5 EA).
''')
consts = '\n'.join('GP_%d = "%s"' % (i, g['name']) for i, g in enumerate(G, 1))
TT_P = ("Custom: your settings below. A preset runs its strategies with their tested settings (swing-high timeframe, candles, offset, SL, TP, BE, salvage), "
        "the entry and exit options as tested, and the money it was tested with in the $1,000-a-month gold study 2021-2026 (fixed $ base risk, loss recovery, hard cap, "
        "no profit ladder, monthly restart on). Your own settings stay saved and come back with Custom. The weekend close, costs, start balance, leverage, display "
        "and alerts stay yours. Use a 1 minute chart (as tested; a 5 minute chart runs all but S12).")
TT_A = "Off (default): the preset trades every day and hour, as tested. On: your Trade Only On The Ticked Days / Trade Only Between settings below apply too."
TT_M = "Off (default): the preset's money. On: your MONEY and LOSS RECOVERY settings below (base risk, loss recovery, hard cap, profit ladder, monthly restart) instead."
top = '''// ---------------------------------------------------------------- PRESET (v3.2: the top of the settings)
GRP_PS    = "PRESET"
GP_CUSTOM = "Custom (my settings below)"
%s
presetIn  = input.string(GP_CUSTOM, "Preset", options = [%s], group = GRP_PS, tooltip = "%s")
addMine   = input.bool(false, "Add My Days And Hours", group = GRP_PS, tooltip = "%s")
myMoney   = input.bool(false, "Use My Money Settings", group = GRP_PS, tooltip = "%s")

''' % (consts, ', '.join(['GP_CUSTOM'] + ['GP_%d' % i for i in range(1, NG + 1)]), TT_P, TT_A, TT_M)
sub1('// ---------------------------------------------------------------- GRID\nGRP_G   = "GRID"', top + '// ---------------------------------------------------------------- GRID\nGRP_G   = "GRID"')
head_end = s.index("BODY = r'''")
hs = s[:head_end]; rest = s[head_end:]
for v in ('runMode', 'entMode', 'expN', 'maxDay', 'trA', 'trD', 'tExitH', 'trnOn', 'dayOn', 'hoursOn', 'szMode', 'baseR', 'capOn', 'hardCap', 'capAction', 'recMode', 'ladMode'):
    m = re.findall(r'^%s( *)= input\.' % v, hs, re.M)
    assert len(m) == 1, (v, m)
    hs = re.sub(r'^%s%s= input\.' % (v, m[0]), '%sIn%s= input.' % (v, m[0][2:] if len(m[0]) > 2 else ' '), hs, count=1, flags=re.M)
cap_line = re.search(r'^capActionIn = input\.string\(CAP_CLAMP, "If The Risk Would Exceed The Cap".*$', hs, re.M).group(0)
hs = hs.replace(cap_line, cap_line + '\nmRestartIn = input.bool(false, "Restart Every Strategy\'s Money On The 1st Of Each Month", group = GRP_M, tooltip = "Off (default): the money of each strategy runs on. On: at each strategy\'s first trade of a new month (time zone of DAYS AND HOURS) its loss recovery starts again from the base risk, the profit ladder, Crooks J and Rule C split count the closed profit from there, and a hard-cap Stop trading ends: every month starts like the $1,000-a-month test. The balance itself carries on.")')
s = hs + rest

# ---- the effective values, after the strategy blocks
EFF = r'''
def effective(strats):
    """v3.2: the values the grid uses: your settings (Custom) or the preset's (written from presets/preset_data.py)"""
    sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/presets')
    import preset_data as PD
    G = PD.GRID_PRESETS
    def by(vals, lit):
        from collections import Counter
        dflt = Counter(vals).most_common(1)[0][0]; out = lit(dflt); grp = {}
        for i, v in enumerate(vals, 1):
            if v != dflt: grp.setdefault(v, []).append(i)
        for v, ids in sorted(grp.items(), key=lambda kv: -kv[1][0]):
            out = '%s ? %s : %s' % (' or '.join('GI == %d' % i for i in ids), lit(v), out)
        return out
    B = lambda b: 'true' if b else 'false'
    L = ['// ---------------------------------------------------------------- v3.2: the values the grid uses (your settings, or the preset\'s)',
         'int    GI = ' + ' : '.join('presetIn == GP_%d ? %d' % (i, i) for i in range(1, len(G) + 1)) + ' : 0',
         'bool   PC = GI == 0',
         'bool   PM = PC or myMoney                  // your money settings',
         'string presetTxt = PC ? "Custom" : presetIn',
         'string runMode = PC ? runModeIn : RUN_TCK']
    for i, p in enumerate(strats, 1):
        tf, r, l, off, sl, tp, be, sv = p
        L += ['bool   s%dOn = PC ? s%dOnIn : %s' % (i, i, by([i in g['strats'] for g in G], B)),
              'string s%dTf = PC ? s%dTfIn : "%s"' % (i, i, TFV[tf]),
              'float  s%dOff = PC ? s%dOffIn : %s' % (i, i, num(off)),
              'int    s%dR = PC ? s%dRIn : %d' % (i, i, r),
              'int    s%dL = PC ? s%dLIn : %d' % (i, i, l),
              'float  s%dSl = PC ? s%dSlIn : %s' % (i, i, num(sl)),
              'float  s%dTp = PC ? s%dTpIn : %s' % (i, i, num(tp)),
              'float  s%dBe = PC ? s%dBeIn : %s' % (i, i, num(be)),
              'float  s%dSv = PC ? s%dSvIn : %s' % (i, i, num(sv))]
    L += ['string entMode = PC ? entModeIn : E_STOP', 'int    expN = PC ? expNIn : 0', 'int    maxDay = PC ? maxDayIn : 0', 'float  trA = PC ? trAIn : 0.0',
          'float  trD = PC ? trDIn : 0.0', 'float  tExitH = PC ? tExitHIn : 0.0', 'bool   trnOn = PC ? trnOnIn : false',
          'bool   dayOn = (PC or addMine) and dayOnIn', 'bool   hoursOn = (PC or addMine) and hoursOnIn',
          'string szMode = PM ? szModeIn : SZ_USD',
          'float  baseR = PM ? baseRIn : %s' % by([g['base'] for g in G], lambda x: num(x) if '.' in num(x) else num(x) + '.0'),
          'bool   capOn = PM ? capOnIn : %s' % by([g['cap'] is not None for g in G], B),
          'float  hardCap = PM ? hardCapIn : %s' % by([g['cap'] or 500.0 for g in G], lambda x: num(x) if '.' in num(x) else num(x) + '.0'),
          'string capAction = PM ? capActionIn : %s' % by([g['act'] for g in G], lambda a: {'clamp': 'CAP_CLAMP', 'reset': 'CAP_RESET', 'stop': 'CAP_STOP'}[a]),
          'string recMode = PM ? recModeIn : %s' % by([g['rec'] for g in G], lambda r: {'EXACT': 'L_EXACT', 'OFF': 'L_OFF'}[r]),
          'string ladMode = PM ? ladModeIn : "Off"',
          'bool   mRestart = PM ? mRestartIn : true']
    return '\n'.join(L) + '\n'

'''
sub1('\ndef build(strats, kind):', EFF + '\ndef build(strats, kind):')
sub1('    return head + blocks + body\n', '    return head + blocks + effective(strats) + body\n')

# ---- body: the monthly restart
sub1('''    bool   stopped = false
    string stopWhy = ""
''', '''    bool   stopped = false
    string stopWhy = ""
    float  n0     = 0.0       // v3.2 monthly restart: the closed profit at the last restart (the money rules count from it)
    int    mKey   = na        //   the month of the money (yyyymm)
    int    curM   = na        //   this candle's month
    bool   capStp = false     //   stopped by the hard cap (ends with the month)
''')
sub1('''    float C  = on ? math.max(0.0, s.net - ladLam * s.peakNet) : 0.0
    [on, on and s.net <= 0,''', '''    float C  = on ? math.max(0.0, s.net - s.n0 - ladLam * s.peakNet) : 0.0
    [on, on and s.net - s.n0 <= 0,''')
sub1('(s.peakNet - s.net) / (crkJX * B)', '(s.peakNet - (s.net - s.n0)) / (crkJX * B)')
sub1('''    float stepBase = 0.0
    if s.net >= 1000
        int kk = int(math.floor((s.net - 1000.0) / 500.0))
        stepBase := (1000.0 + 500.0 * kk) / (8.0 + kk)
    else if s.net >= 500
        stepBase := 500.0 / 5.0
    else if s.net >= 200
        stepBase := 200.0 / 3.0''', '''    float stepBase = 0.0
    float netR = s.net - s.n0
    if netR >= 1000
        int kk = int(math.floor((netR - 1000.0) / 500.0))
        stepBase := (1000.0 + 500.0 * kk) / (8.0 + kk)
    else if netR >= 500
        stepBase := 500.0 / 5.0
    else if netR >= 200
        stepBase := 200.0 / 3.0''')
sub1('''// sizing at an entry (the cap's reset / stop change the state): false = the cap stops the strategy, no trade
method mmOpen(Strat s, float F) =>
    float sd = F * s.sl / 100.0
''', '''// v3.2 monthly restart: the money starts again (the loss recovery, the closed profit the ladder / Crooks J / Rule C split count from)
method mReset(Strat s) =>
    s.recPool   := 0.0
    s.recLosses := 0
    s.dUnits    := 1
    s.carried   := 0.0
    s.lab.clear()
    s.lab.push(1.0)
    s.lab.push(2.0)
    s.lab.push(3.0)
    s.parWins   := 0
    s.rdUnits   := 1
    s.oscU      := 1
    s.oscP      := 0.0
    s.crL       := 0.0
    s.crN       := 0
    s.crRecT    := false
    s.crW       := false
    s.crP       := crkCn
    s.crF       := 0
    s.crWait    := false
    s.crWW      := 0
    s.crNeedL   := false
    s.n0        := s.net
    s.peakNet   := 0.0
    true

// sizing at an entry (the cap's reset / stop change the state): false = the cap stops the strategy, no trade
method mmOpen(Strat s, float F) =>
    if mRestart and (na(s.mKey) or s.curM != s.mKey)     // v3.2: the first trade of a new month starts with fresh money
        if not na(s.mKey)
            s.mReset()
        s.mKey := s.curM
    float sd = F * s.sl / 100.0
''')
sub1('''            s.stopped := true
            s.stopWhy := "stopped by the hard cap"
            take := false''', '''            s.stopped := true
            s.stopWhy := "stopped by the hard cap"
            s.capStp  := true
            take := false''')
sub1('    s.peakNet := math.max(s.peakNet, s.net)\n', '    s.peakNet := math.max(s.peakNet, s.net - s.n0)\n')
sub1('''method onBar(Strat s, float ph, int pt, int hb, float pc, bool okb, bool wk, int dno) =>
    s.msg := ""
''', '''method onBar(Strat s, float ph, int pt, int hb, float pc, bool okb, bool wk, int dno) =>
    s.msg := ""
    s.curM := int(math.floor(dno / 100))
    if mRestart and s.capStp and not na(s.mKey) and s.curM != s.mKey     // v3.2: a hard-cap stop ends with the month
        s.stopped := false
        s.capStp  := false
        s.stopWhy := ""
    if mRestart and not s.pos and not na(s.mKey) and s.curM != s.mKey    // v3.2: flat at a new month: the money starts again now (the next trade's lots shown are right)
        s.mReset()
        s.mKey := s.curM
''')
sub1('T.cell(0, 0, "FRACTAL BREAKOUT GRID v3.1 · " + syminfo.ticker', 'T.cell(0, 0, "FRACTAL BREAKOUT GRID v3.2 · " + (PC ? "" : presetTxt + " · ") + syminfo.ticker')
open(H + 'build_fbg3.py', 'w').write(s)
print('generator v3.2 written')
