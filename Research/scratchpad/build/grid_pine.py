"""v6.0 true grid for the Pine strategy (same direction only): the per-slot part of the engine (live trade, armed setup, arming), the
accuracy counters' update, the markings and the whole execution run in `for slot = 0 to (gridOn ? 1 : 0)`; slot 1's state lives in the Slot
object `sb` and is exchanged with the globals around its pass, so every line of the engine and the execution is the v5.4 one. Not in the
grid (one slot) the loop runs once and the script trades exactly like the single-slot file."""
import re

# per-slot state: engine, its events, its markings, the execution (trade, loss recovery, money rules, streaks, locks)
SLOT = ('st armBar fillBar lastExit lastFill lastDir lim stp stp0 trRisk t1 t2 t3 t4 tF tpHit trTrig trHalf trGhost trSkip bestPx trMkt trSrc '
        'dayFills dayW dayL dayR dayRiskR lossDirBlk '
        'evArm evArmL evFill evFillL evExit evWin evRes evMove evTp evSalv evTrig evCancel '
        'limLine gBox rBox eLine l1 l2 l3 drawOn '
        'exState exL exQty exRiskUsd exBase exBaseWin exCostPx exPnl exArm exPartDone skipWhy dayPnl lossRow winRow dayBlock pauseLeft paused '
        'recPool recLosses dUnits carried capStop labSeq parWins rdUnits oscU oscP crkL crkFx mmRa mmEqA mmS1326 mmLossRow mmCoolLeft exRisk0 '
        'crkN crkRec crkW crkP crkF crkWait crkWW crkNeedL crkSkip crkSkipLeft mNet0 rNet0 mPeak mStop pLocked mRestPend crkPk '
        'exT1 exT1Stop exT1Tight exT1Half exT1Tp1 exT1Tp2 exW exLn baseRisk slNet mPnl dayOpen crkPause').split()
EVENTS = 'evArm evArmL evFill evFillL evExit evWin evRes evMove evTp evSalv evTrig evCancel'.split()
TYPES = r'(?:float|int|bool|string|line|box|array<float>)'



def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:150])
    return s.replace(a, b)


def cut(s, a, b=None, keep_b=False):
    """the text from marker a (included) to marker b (excluded), and s without it"""
    i = s.index(a); assert s.count(a) == 1, a
    if b is None: return s[i:], s[:i]
    j = s.index(b, i); assert s.count(b) == 1, b
    return s[i:j], s[:i] + s[j:]


def decls(s):
    """name -> (type, init) of the slot variables, from their declarations"""
    out = {}
    for n in SLOT:
        m = re.findall(r'^(?:var\s+)?(' + TYPES + r')\s+' + n + r'\s*=\s*(.*?)\s*(?://.*)?$', s, re.M)
        assert len(m) == 1, (n, m)
        out[n] = m[0]
    return out


def indent(t, k):
    return ''.join((' ' * k + ln if ln.strip() else ln) for ln in t.splitlines(True))


def grid(s):
    # -- the helpers the grid needs, before the execution's functions ------------------------------------------------------------------
    s = rep(s, '// ══════════════════════════ EXECUTION (strategy only, follows the engine) ═════════════\n',
            '// ══════════════════════════ EXECUTION (strategy only, follows the engine) ═════════════\n' + HELPERS)
    s = rep(s, 'float mPnl = strategy.netprofit - mNet0\n', 'mPnl := strategy.netprofit - mNet0\n')
    s = rep(s, 'bool  dayOpen = dayStopR <= 0 or dayRiskR > -dayStopR\n', 'dayOpen := dayStopR <= 0 or dayRiskR > -dayStopR\n')
    s = rep(s, 'bool crkPause = crkPrOn and crkPr == CPR_SKIP and crkSkip ', 'crkPause := crkPrOn and crkPr == CPR_SKIP and crkSkip ')
    s = rep(s, '    mNet0   := nz(strategy.netprofit[1])\n', '    mNet0   := gridOn ? slNet : netPrev\n')
    s = rep(s, 'float mE   = strategy.initial_capital + strategy.netprofit', 'float mE   = strategy.initial_capital + strategy.@@NP@@')
    s = s.replace('strategy.netprofit', 'f_net()').replace('strategy.@@NP@@', 'strategy.netprofit')
    s = s.replace('strategy.position_avg_price', 'f_avgPx()')
    s = rep(s, 'f_avgPx() => gridOn ? slAvg : f_avgPx()', 'f_avgPx() => gridOn ? slAvg : strategy.position_avg_price')
    s = rep(s, 'f_net() => gridOn ? slNet : f_net()', 'f_net() => gridOn ? slNet : strategy.netprofit')
    s = rep(s, 'string eid = isL ? "L" : "S"', 'string eid = f_eid(isL)', 3)
    for k in (1, 2, 3, 4):
        s = s.replace('strategy.exit("X%d",' % k, 'strategy.exit(f_xid(%d),' % k)
    assert 'strategy.exit("' not in s
    s = s.replace('strategy.cancel_all()', 'f_cancelSlot()')
    s = re.sub(r'strategy\.close_all\(comment = (.*?)\)\n', r'f_closeSlot(\1)\n', s)
    # the helper itself keeps the real calls
    s = rep(s, '    else\n        f_cancelSlot()\n', '    else\n        strategy.cancel_all()\n')
    s = rep(s, '    else\n        f_closeSlot(c)\n', '    else\n        strategy.close_all(comment = c)\n')
    # execution step 1: this slot's closed trades and position
    s = rep(s, '''float newPnl    = 0.0
bool  closedNew = strategy.closedtrades > nClosed
if closedNew
    for k = nClosed to strategy.closedtrades - 1
        newPnl += strategy.closedtrades.profit(k)
    nClosed := strategy.closedtrades
exPnl += newPnl
''', '''float newPnl    = curSlot == 0 ? cpA : cpB
bool  closedNew = curSlot == 0 ? ccA : ccB
exPnl += newPnl
slNet += newPnl
''')
    s = rep(s, 'float pos = strategy.position_size\n', 'float pos = gridOn ? (curSlot == 0 ? posA : posB) : strategy.position_size\nslAvg := curSlot == 0 ? avgA : avgB\n')
    s = rep(s, 'if mRestPend and exState == 0 and strategy.position_size == 0\n', 'if mRestPend and exState == 0 and pos == 0\n')
    # same direction only: a setup against the other slot's trade (or working entry) is skipped
    s = rep(s, '    bool preSkip = exState != 0 or pos != 0 or newsBlock', '    float oPos   = curSlot == 0 ? posB : posA      // v6.0 true grid: one net position on TradingView: the other slot position now, or its working entry\n    bool oppSkip = gridOn and ((oPos != 0 and (oPos > 0) != isL) or (sb.exState == 1 and sb.exL != isL))\n    bool preSkip = exState != 0 or pos != 0 or oppSkip or newsBlock')
    s = rep(s, '    skipWhy := coolSkip ? "cooling-off" :', '    skipWhy := coolSkip ? "cooling-off" : oppSkip ? "opposite to the other setup\'s trade" :')

    D = decls(s)
    # -- cut the blocks ----------------------------------------------------------------------------------------------------------------
    eng, s = cut(s, '// ── 1. manage the live trade: stop first, then the final target, else stop moves (from the next bar) ──\n', '// <<< ENGINE END\n')
    sh, eng = cut(eng, 'int  dowUse = dayofweek(time, tzUse)\n', 'bool canArm  = ')
    kz = sh.index('bool kzOk'); kz = sh.index('\n', kz) + 1
    assert sh[kz:] == '', 'canArm must follow kzOk'
    stats_upd, s = cut(s, 'if evExit\n    float sd = lastDir == 1 ? 1.0 : -1.0\n', 'bool mvAny  = ')
    draw_upd, s = cut(s, 'if evCancel != "" or evFill\n    line.delete(limLine)\n', 'plot(showVwap ? vwap : na, "VWAP"')
    exa, s = cut(s, 'if newDay\n    dayPnl   := 0.0\n', 'f_tgtPx(bool isL, float lvl) =>')
    exb, s = cut(s, '// ── 1. what the broker emulator did on this bar ──\n', '// ═══════════════════════════════════════ TABLE ═══')
    shared_a = ''
    for ln in ('int   udKey = ', 'bool  udNew = ', 'int   udDow = ', 'int   mKey = ', 'bool  mNew = '):
        i = exa.index(ln); j = exa.index('\n', i) + 1
        shared_a += exa[i:j]; exa = exa[:i] + exa[j:]
    body = eng + stats_upd + draw_upd + exa + exb
    # -- the Slot object and the exchange -------------------------------------------------------------------------------------------------
    typ = ['// ── v6.0 true grid: slot 1 (order block) keeps its engine and execution state here between its passes ──', 'type Slot']
    for n in SLOT:
        t = D[n][0]
        dv = D[n][1]
        lit = re.fullmatch(r'-?\d+(\.\d+)?|true|false|""', dv)
        typ.append('    %s %s%s' % (t, n, (' = ' + dv) if lit else ''))
    args = ', '.join('%s = %s' % (n, D[n][1]) for n in SLOT if D[n][1] != 'na' and not re.fullmatch(r'-?\d+(\.\d+)?|true|false|""', D[n][1]))
    typ.append('var Slot sb = Slot.new(%s)' % args)
    ex = []
    for n in SLOT:
        ex += ['%s x_%s = %s' % (D[n][0], n, n), '%s := sb.%s' % (n, n), 'sb.%s := x_%s' % (n, n)]
    rs = ['%s := %s' % (n, D[n][1]) for n in EVENTS]
    pre = PRE + '\n'.join(typ) + '\n' + PRE2
    loop = ['// ── v6.0 the slots: 0 = the VWAP setup (or the only one), 1 = the order block setup (true grid) ──',
            'for slot = 0 to (gridOn ? 1 : 0)',
            '    for ph = 0 to 2',
            '        if ph != 1',
            '            if slot == 1',
            indent('\n'.join(ex), 16).rstrip('\n'),
            '                if ph == 0',
            indent('\n'.join(rs), 20).rstrip('\n'),
            '            curSlot := ph == 0 ? slot : 0',
            '        else']
    loop = '\n'.join(loop) + '\n' + indent(body, 12)
    plots, s = cut(s, 'plot(showVwap ? vwap : na, "VWAP"', '// <<< DRAW END\n')
    i = s.index('// <<< ENGINE END\n')
    s = s[:i] + sh + s[i:]
    i = s.index('// ═══════════════════════════════════════ TABLE ═══')
    s = s[:i] + shared_a + pre + loop + '\n' + plots + '\n' + s[i:]
    # the fill marks of both slots
    s = rep(s, 'plotshape(showMarks and evFill and evFillL, "Long Fill"', 'plotshape(showMarks and ((evFill and evFillL) or (gridOn and sb.evFill and sb.evFillL)), "Long Fill"')
    s = rep(s, 'plotshape(showMarks and evFill and not evFillL, "Short Fill"', 'plotshape(showMarks and ((evFill and not evFillL) or (gridOn and sb.evFill and not sb.evFillL)), "Short Fill"')
    # the table: one more row for the order block slot
    s = rep(s, '        mon := table.new(f_pos(tablePos), 2, 13 + (PC ? 0 : 1)', '        mon := table.new(f_pos(tablePos), 2, 13 + (gridOn ? 1 : 0) + (PC ? 0 : 1)')
    s = rep(s, '    string tz = tableTz == "Exchange" ? syminfo.timezone : tableTz\n', GRID_ROW + '    string tz = tableTz == "Exchange" ? syminfo.timezone : tableTz\n')
    return s


HELPERS = r'''// v6.0 true grid helpers: the slot's closed profit, position, entry / exit names, and closing / cancelling only the slot's orders
var float slNet = 0.0        // the slot's closed profit (true grid; one slot: the strategy's)
float slAvg = na             // the slot's average entry price (true grid)
float mPnl  = 0.0            // this month's closed profit of the slot
bool  dayOpen  = true         // the slot's daily R stop not hit (the engine's dayOpen; shown in the table)
bool  crkPause = false        // the slot's Crooks C skip pause
f_net() => gridOn ? slNet : strategy.netprofit
f_avgPx() => gridOn ? slAvg : strategy.position_avg_price
f_eid(bool isL) => curSlot == 0 ? (isL ? "L" : "S") : (isL ? "L2" : "S2")
f_xid(int k) => (curSlot == 0 ? "X" : "Y") + str.tostring(k)
f_cancelSlot() =>
    if gridOn
        strategy.cancel(f_eid(true))
        strategy.cancel(f_eid(false))
        for k = 1 to 4
            strategy.cancel(f_xid(k))
    else
        strategy.cancel_all()
f_closeSlot(string c) =>
    if gridOn
        strategy.close(f_eid(true), comment = c)
        strategy.close(f_eid(false), comment = c)
    else
        strategy.close_all(comment = c)
'''

PRE = r'''// ── v6.0 this bar's closed trades and open position of each slot (true grid: slot 1's entries are L2 / S2) ──
float netPrev = nz(strategy.netprofit[1])
float cpA = 0.0
float cpB = 0.0
bool  ccA = false
bool  ccB = false
if strategy.closedtrades > nClosed
    for k = nClosed to strategy.closedtrades - 1
        string cid = strategy.closedtrades.entry_id(k)
        if gridOn and (cid == "L2" or cid == "S2")
            cpB += strategy.closedtrades.profit(k)
            ccB := true
        else
            cpA += strategy.closedtrades.profit(k)
            ccA := true
    nClosed := strategy.closedtrades
float posA = 0.0
float posB = 0.0
float avgA = na
float avgB = na
if gridOn and strategy.opentrades > 0
    float vA = 0.0
    float vB = 0.0
    for k = 0 to strategy.opentrades - 1
        string oid = strategy.opentrades.entry_id(k)
        float  osz = strategy.opentrades.size(k)
        if oid == "L2" or oid == "S2"
            posB += osz
            vB   += math.abs(osz) * strategy.opentrades.entry_price(k)
        else
            posA += osz
            vA   += math.abs(osz) * strategy.opentrades.entry_price(k)
    avgA := posA != 0 ? vA / math.abs(posA) : na
    avgB := posB != 0 ? vB / math.abs(posB) : na
'''

PRE2 = r'''if newDay and gridOn           // the engine's day counters of slot 1 (slot 0's are reset by the engine above)
    sb.dayFills   := 0
    sb.dayW       := 0
    sb.dayL       := 0
    sb.dayR       := 0.0
    sb.dayRiskR   := 0.0
    sb.lossDirBlk := 0
'''

GRID_ROW = r'''    if gridOn
        string sbSt = sb.st == 2 ? "LONG ACTIVE" : sb.st == -2 ? "SHORT ACTIVE" : sb.st == 1 ? "BUY ARMED" : sb.st == -1 ? "SELL ARMED" : "SCANNING"
        f_row(mon, r, "ORDER BLOCK SLOT", sbSt + (sb.exState == 2 ? " · in trade " + str.tostring(sb.exQty / unitsPer, "#,##0.##") + " lots" : sb.exState == 1 ? " · order working" : "") + " · net " + f_usd(sb.slNet) + " · " + str.tostring(sb.exW) + "W/" + str.tostring(sb.exLn) + "L", white)
        r += 1
'''
