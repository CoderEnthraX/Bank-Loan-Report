"""v4.8 (asked 2026-11-16): STRATEGY PRESET at the top of the settings (Custom + the 25 catalogue strategies M1 S1-S4, M5 S1-S4, M15 S1-S9,
H1 S1-S8), "Add My Filters" (off = the preset exactly as tested), a preset trades only on its own chart timeframe, and the monthly restart
also restarts the profit ladder / Crooks J peak / Rule C split steps (closed profit counted from the restart) and the hard-cap stop.
Applied to the v4.7 sources (backups in build/bak/*_v47.pine), then assemble.py. Custom = the v4.7 engine and execution, unchanged."""
import os, re, shutil, sys
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
sys.path.insert(0, B + '../presets')
import preset_data as PD

FILES = ('shared_inputs.pine', 'shared_engine.pine', 'strategy_template.pine', 'indicator_template.pine')
for f in FILES:
    bk = B + 'bak/' + f.replace('.pine', '_v47.pine')
    if not os.path.exists(bk): shutil.copy(B + f, bk)
src = {f: open(B + 'bak/' + f.replace('.pine', '_v47.pine')).read() for f in FILES}


def sub1(s, old, new, cnt=1):
    assert s.count(old) == cnt, (old[:80], s.count(old))
    return s.replace(old, new)


P = PD.ars_presets()
N = len(P)


def lab(p):
    g = p['goal'].replace(' - indicator only', ', no partial close')
    return '%s · %s%s' % (p['key'], g, ' (70%% closed at TP1)' % () if p['p1'] > 0 else '')


def cond(ids):
    return ' or '.join('PI == %d' % i for i in ids)


def expr(vals, lit):
    """vals[i] = the value of preset i + 1: the most common value as the default, the others by preset index"""
    from collections import Counter
    cnt = Counter(vals); dflt = cnt.most_common(1)[0][0]
    out = lit(dflt)
    groups = {}
    for i, v in enumerate(vals, 1):
        if v != dflt: groups.setdefault(v, []).append(i)
    for v, ids in sorted(groups.items(), key=lambda kv: -kv[1][0]):
        out = '%s ? %s : %s' % (cond(ids), lit(v), out)
    return out


# ---------------------------------------------------------------- shared_inputs.pine
s = src['shared_inputs.pine']
head = s.split('\n', 1)
opts = ', '.join(['PS_CUSTOM'] + ['PS_%d' % i for i in range(1, N + 1)])
consts = '\n'.join('PS_%d = "%s"' % (i, lab(p)) for i, p in enumerate(P, 1))
TT_PRESET = ("Custom: your settings below. A preset sets every signal setting exactly as tested on gold 2021-2026 (stop, targets and final exit, "
             "entry price, filters, VWAP anchor, max fills, its own hours or kill zone; in the strategy also the 70% partial close at TP1 of M15-S2 / S4 / S5 "
             "and H1-S2 / S4 / S5). Your own values stay saved and come back with Custom.\\nA preset only trades on its own chart timeframe (the M1, M5, M15 "
             "or H1 in its name); on another chart it takes no trades and the table says so.\\nAlways yours, with any preset: force-close, the Saturday close, "
             "spread and commission, risk, loss recovery and the monthly settings.")
TT_ADD = ("Off (default): the preset trades exactly as tested: only in its own hours or kill zone (M5: 18:30-22:30 IST, M1: London Close 19:30-21:30 IST, "
          "M15-S9: Asia 05:30-09:30 IST, the others all day); your days, hours, kill zones and news windows are not used.\\nOn: your own filters below apply, each as "
          "you have it switched on or off: your days and news windows are added to the preset; your hours or kill zones, once either is switched on, replace "
          "the preset's own hours (both off: it keeps its own). A preset with your filters is no longer the tested strategy.")
top = '''// ── v4.8 STRATEGY PRESET (the top of the settings): Custom = your settings below; a preset = a tested catalogue strategy ──
GRP_PS    = "STRATEGY PRESET"
PS_CUSTOM = "Custom (my settings below)"
%s
presetIn  = input.string(PS_CUSTOM, "Strategy Preset", options = [%s], group = GRP_PS, tooltip = "%s")
addMine   = input.bool(false, "Add My Filters (days, hours, kill zones, news)", group = GRP_PS, tooltip = "%s")
''' % (consts, opts, TT_PRESET, TT_ADD)
s = head[0] + '\n' + top + head[1]

# the engine inputs become <name>In; the engine reads the effective value <name> (below)
ren = [p[0] for p in PD.PARAMS] + ['dayOn', 'hoursOn', 'hoursSess', 'kzOn', 'kzAsia', 'kzLon', 'kzNy', 'kzLc', 'kzAuto', 'kzShift']
for v in ren:
    m = re.findall(r'^%s( *)= input\.' % v, s, re.M)
    assert len(m) == 1, (v, m)
    sp = m[0]
    s = re.sub(r'^%s%s= input\.' % (v, sp), '%sIn%s= input.' % (v, sp[2:] if len(sp) > 2 else ' '), s, count=1, flags=re.M)
# the targets check, exit level and exit R move below the effective values
old_t = '''if barstate.isfirst and (tp1R > tp2R or tp2R > tp3R or tp3R > tp4R)
    runtime.error("Targets must be in order: TP1 <= TP2 <= TP3 <= TP4.")
int   exitK = exitAt == "TP1" ? 1 : exitAt == "TP2" ? 2 : exitAt == "TP3" ? 3 : 4
float exitR = exitK == 1 ? tp1R : exitK == 2 ? tp2R : exitK == 3 ? tp3R : tp4R
'''
s = sub1(s, old_t, '')
# the effective values
TYPE = {'int': 'int', 'float': 'float', 'bool': 'bool', 'rearm': 'string', 'stopmode': 'string', 'anchor': 'string', 'src': 'float', 'entry': 'string',
        'exit': 'string', 'vwunit': 'string'}
lines = ['// ── v4.8 the values the engine uses: your inputs (Custom) or the preset\'s tested values (written by build/patch_pine_v48.py from presets/preset_data.py) ──',
         'int  PI = ' + ' : '.join('presetIn == PS_%d ? %d' % (i, i) for i in range(1, N + 1)) + ' : 0',
         'bool PC = PI == 0',
         'string presetTxt = PC ? "Custom" : presetIn']
for pv, key, kind, ea in PD.PARAMS:
    vals = [p['v'][key] for p in P]
    lines.append('%s %s = PC ? %sIn : %s' % (TYPE[kind], pv, pv, expr(vals, lambda x, k=kind: PD.pine_lit(k, x))))
ses = [PD.session(p) for p in P]
lines += [
    '// time filters: your days / news windows only for Custom or with Add My Filters; the preset\'s own hours or kill zone unless your hours or kill zones replace them',
    'bool   myF  = PC or addMine',
    'bool   ownS = not PC and not (addMine and (hoursOnIn or kzOnIn))',
    'bool   dayOn = myF and dayOnIn',
    'bool   hoursOn = ownS ? %s : hoursOnIn' % expr([x[0] for x in ses], lambda b: 'true' if b else 'false'),
    'string hoursSess = ownS ? %s : hoursSessIn' % expr([x[1] or '0000-0000' for x in ses], lambda t: '"%s"' % t),
    'string tzHr = ownS ? "Asia/Kolkata" : tzUse          // the preset hours are Indian times',
    'bool   kzOn = ownS ? %s : kzOnIn' % expr([x[2] for x in ses], lambda b: 'true' if b else 'false')]
for j, nm in enumerate(('kzAsia', 'kzLon', 'kzNy', 'kzLc')):
    lines.append('bool   %s = ownS ? %s : %sIn' % (nm, expr([x[3][j] for x in ses], lambda b: 'true' if b else 'false'), nm))
lines += ['bool   kzAuto = ownS ? %s : kzAutoIn' % expr([x[4] for x in ses], lambda b: 'true' if b else 'false'),
          'int    kzShift = ownS ? %s : kzShiftIn' % expr([x[5] for x in ses], str),
          '// a preset trades only on its own chart timeframe',
          'string presetTf = PC ? "" : %s' % expr([PD.TF_PINE[p['tf']] for p in P], lambda t: '"%s"' % t),
          'string presetTfTxt = presetTf == "1" ? "M1" : presetTf == "5" ? "M5" : presetTf == "15" ? "M15" : "H1"',
          'bool   presetTfOk = PC or timeframe.period == presetTf',
          old_t.rstrip('\n')]
eff = '\n'.join(lines) + '\n'
s = sub1(s, '// <<< ENGINE INPUTS END', eff + '// <<< ENGINE INPUTS END')
open(B + 'shared_inputs.pine', 'w').write(s)

# ---------------------------------------------------------------- shared_engine.pine
e = src['shared_engine.pine']
e = sub1(e, 'bool inHours = not na(time(timeframe.period, hoursSess, tzUse))', 'bool inHours = not na(time(timeframe.period, hoursSess, tzHr))')
e = sub1(e, 'bool canArm  = barstate.isconfirmed and warm and dayOk', 'bool canArm  = barstate.isconfirmed and warm and presetTfOk and dayOk')
open(B + 'shared_engine.pine', 'w').write(e)

# ---------------------------------------------------------------- strategy_template.pine
t = src['strategy_template.pine']
t = sub1(t, '''//  v4.7: POSITION SIZE (Risk and position size): Fixed $ risk (as before), Fixed lots (e.g. 0.01 lot) or % of
//  equity at risk; the loss recovery rule sizes every trade from that base (strategy only; the EA keeps $ risk).
''', '''//  v4.7: POSITION SIZE (Risk and position size): Fixed $ risk (as before), Fixed lots (e.g. 0.01 lot) or % of
//  equity at risk; the loss recovery rule sizes every trade from that base (strategy only; the EA keeps $ risk).
//  v4.8: STRATEGY PRESET at the top of the settings: Custom (your settings) or one of the 25 tested catalogue strategies
//  (M1 S1-S4, M5 S1-S4, M15 S1-S9, H1 S1-S8), each on its own chart timeframe; Add My Filters adds your days, hours, kill
//  zones and news. The monthly restart now also restarts the profit ladder and a hard-cap stop (the same in the MT5 EA).
''')
for v in ('p1Pct', 'p2Pct', 'p3Pct'):
    t = sub1(t, '\n%s = input.float(' % v, '\n%sIn = input.float(' % v)
p1e = expr([round(p['p1'] * 100.0, 6) for p in P], PD.fnum)
t = sub1(t, 'float pp1 = exitK > 1 ? p1Pct : 0.0\n', '''// v4.8: a preset closes its own partial at TP1 (70%% on M15-S2 / S4 / S5 and H1-S2 / S4 / S5), nothing at TP2 / TP3
float p1Pct = PC ? p1PctIn : %s
float p2Pct = PC ? p2PctIn : 0.0
float p3Pct = PC ? p3PctIn : 0.0
float pp1 = exitK > 1 ? p1Pct : 0.0
''' % p1e)
for v in ('dNewsOn', 'n1On', 'n2On', 'n3On', 'n4On', 'n5On'):
    m = re.findall(r'^%s( *)= input\.bool' % v, t, re.M)
    assert len(m) == 1, v
    t = re.sub(r'^%s%s= input\.bool' % (v, m[0]), '%sIn%s= input.bool' % (v, m[0][2:] if len(m[0]) > 2 else ' '), t, count=1, flags=re.M)
t = sub1(t, '\nGRP_L = "LOSS RECOVERY (strategy only)"', '''
// v4.8: your news windows apply with Custom or with Add My Filters
bool dNewsOn = myF and dNewsOnIn
bool n1On    = myF and n1OnIn
bool n2On    = myF and n2OnIn
bool n3On    = myF and n3OnIn
bool n4On    = myF and n4OnIn
bool n5On    = myF and n5OnIn

GRP_L = "LOSS RECOVERY (strategy only)"''')
# the monthly restart: tooltip, the closed profit counted from the restart (profit ladder, Crooks J, Rule C split steps), the hard-cap stop
m = re.search(r'mRestart = input\.bool\(false, "Restart The Loss Recovery On The 1st Of Each Month", group = GRP_ML, tooltip = "([^"]*)"\)', t)
assert m
t = t.replace(m.group(1), m.group(1) + ' v4.8: it also restarts the profit ladder (its best profit and the closed profit count from the restart), the Crooks J drawdown, the Rule C split steps and a hard-cap Stop trading, so every month starts like a new account (the same as in the MT5 EA and the monthly tests).')
m = re.search(r'capAction  = input\.string\(CAP_RESET, "If The Risk Would Exceed The Cap", options = \[CAP_CLAMP, CAP_STOP, CAP_RESET\], group = GRP_R, tooltip = "([^"]*)"\)', t)
assert m and 'Stop trading: take no more trades for the rest of the back' in m.group(1), m and m.group(1)[:200]
t = t.replace(m.group(1), m.group(1).replace('Stop trading: take no more trades for the rest of the backtest.',
                                             'Stop trading: take no more trades for the rest of the backtest (with the monthly restart on: until the 1st of the next month).'))
t = sub1(t, 'var float mNet0     = 0.0    // monthly lock: closed profit before this month\n',
         'var float mNet0     = 0.0    // monthly lock: closed profit before this month\nvar float rNet0     = 0.0    // v4.8 monthly restart: closed profit at the last restart (the money rules count from it)\n')
t = sub1(t, '''    bool  on = ladMode != LAD_OFF and ladFam and ladT > 0 and crkPk >= ladT
    float C  = on ? math.max(0.0, strategy.netprofit - ladLam * crkPk) : 0.0
    [on, on and strategy.netprofit <= 0, on ? B + math.min((ladBmax - 1.0) * B, ladPhi * C) : B, C]''',
         '''    bool  on = ladMode != LAD_OFF and ladFam and ladT > 0 and crkPk >= ladT
    float C  = on ? math.max(0.0, strategy.netprofit - rNet0 - ladLam * crkPk) : 0.0
    [on, on and strategy.netprofit - rNet0 <= 0, on ? B + math.min((ladBmax - 1.0) * B, ladPhi * C) : B, C]''')
t = sub1(t, 'q := math.max(B, q * math.max(0.0, 1.0 - math.max(0.0, crkPk - strategy.netprofit) / (crkJX * B)))',
         'q := math.max(B, q * math.max(0.0, 1.0 - math.max(0.0, crkPk - (strategy.netprofit - rNet0)) / (crkJX * B)))')
t = sub1(t, '    crkPk := math.max(crkPk, strategy.netprofit)         // v4.5 Crooks J, v4.6 ladder: the highest closed profit',
         '    crkPk := math.max(crkPk, strategy.netprofit - rNet0) // v4.5 Crooks J, v4.6 ladder: the highest closed profit (v4.8: since the monthly restart)')
t = sub1(t, '    float prof     = strategy.netprofit\n', '    float prof     = strategy.netprofit - rNet0     // v4.8: since the monthly restart\n')
t = sub1(t, '''    crkSkip     := false
    crkSkipLeft := 0
// this month's closed profit''', '''    crkSkip     := false
    crkSkipLeft := 0
    rNet0       := strategy.netprofit   // v4.8: the profit ladder, Crooks J and Rule C split count from here; a hard-cap stop ends
    crkPk       := 0.0
    capStop     := false
// this month's closed profit''')
t = sub1(t, 'kTxt = f_usd(crkL)', 'kTxt = f_usd(crkL)')
t = sub1(t, '", drawdown " + f_usd(math.max(0.0, crkPk - strategy.netprofit))', '", drawdown " + f_usd(math.max(0.0, crkPk - (strategy.netprofit - rNet0)))')
# table: a PRESET row when a preset is selected, and the wrong-chart state
t = sub1(t, 'mon := table.new(f_pos(tablePos), 2, 13 + ', 'mon := table.new(f_pos(tablePos), 2, 13 + (PC ? 0 : 1) + ')
t = sub1(t, '    string stTxt = st != 0 and trGhost ?', '    string stTxt = not presetTfOk ? "WRONG CHART: " + presetTfTxt + " PRESET, NO TRADES" : st != 0 and trGhost ?')
t = sub1(t, '''    if ladMode != LAD_OFF
        f_row(mon, r, "PROFIT LADDER",''', '''    if not PC
        f_row(mon, r, "PRESET", presetTxt + (presetTfOk ? "" : " · needs a " + presetTfTxt + " chart") + (addMine ? " · + my filters" : ""), presetTfOk ? posC : negC)
        r += 1
    if ladMode != LAD_OFF
        f_row(mon, r, "PROFIT LADDER",''')
open(B + 'strategy_template.pine', 'w').write(t)

# ---------------------------------------------------------------- indicator_template.pine
d = src['indicator_template.pine']
d = sub1(d, '''//  The engine below is byte-identical in Auction_Retest_Strategy.pine, so both show the same trades.
''', '''//  v4.8: STRATEGY PRESET at the top of the settings: Custom (your settings) or one of the 25 tested catalogue strategies
//  (M1 S1-S4, M5 S1-S4, M15 S1-S9, H1 S1-S8), each on its own chart timeframe; Add My Filters adds your days, hours and
//  kill zones (the same presets as the strategy and the MT5 EA).
//  The engine below is byte-identical in Auction_Retest_Strategy.pine, so both show the same trades.
''')
d = sub1(d, 'mon := table.new(f_pos(tablePos), 2, 10 + ', 'mon := table.new(f_pos(tablePos), 2, 10 + (PC ? 0 : 1) + ')
d = sub1(d, '    string stTxt  = timeframe.isdwm and vwapAnchor == "Session" ?', '    string stTxt  = not presetTfOk ? "WRONG CHART: " + presetTfTxt + " PRESET" : timeframe.isdwm and vwapAnchor == "Session" ?')
d = sub1(d, '''    int r = 9
    if mvAny''', '''    int r = 9
    if not PC
        f_row(mon, r, "PRESET", presetTxt + (presetTfOk ? "" : " · needs a " + presetTfTxt + " chart") + (addMine ? " · + my filters" : ""), presetTfOk ? posC : negC, cellBg, sz, "The strategy preset in use (STRATEGY PRESET at the top of the settings). A preset only shows signals on its own chart timeframe.")
        r += 1
    if mvAny''')
open(B + 'indicator_template.pine', 'w').write(d)
print('patched', N, 'presets')
