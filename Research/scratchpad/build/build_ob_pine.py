"""v6.0 TradingView: the order block strategy and the VWAP + order block strategy, from TradingView/Auction_Retest_Strategy.pine (v5.4, not changed).
  out/OrderBlock_Strategy.pine        order block setup only (one trade at a time; the v5.4 money management, news, targets ...)
  out/Auction_Retest_OB_Strategy.pine setups: VWAP only / order block only / both one at a time / both true grid (same direction only: a Pine
                                      strategy holds one net position). The grid runs the engine and the execution twice per bar: slot 0 =
                                      VWAP, slot 1 = order block; slot 1's state is kept in a Slot object and swapped in for its pass.
The order block engine is the one of the EA (ObBar) and ob/ob_stream.py. Run: python3 -I build_ob_pine.py"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/user/Bank-Loan-Report'
SRC = REPO + '/TradingView/Auction_Retest_Strategy.pine'
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)


def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:150])
    return s.replace(a, b)


OB_INPUTS = r'''// ── v6.0 SETUPS AND ORDER BLOCK ──
GRP_OB = "SETUPS AND ORDER BLOCK"
S_VWAP = "VWAP only"
S_OB   = "Order block only"
S_ONE  = "Both: one trade at a time"
S_GRID = "Both: true grid (same direction)"
@@SETUP@@
OBT_AUTO = "Auto"
OBT_OFF  = "Off"
obTf1In   = input.string(OBT_AUTO, "Order Block Timeframe 1", options = [OBT_AUTO, OBT_OFF, "M3", "M5", "M15", "M30", "H1", "H4"], group = GRP_OB, tooltip = "The higher timeframe whose candles make the order blocks (built from this chart's own candles). Auto: M1 chart -> M3 and M5 · M5 -> M15, M30 and H1 · M15 -> H1 and H4 · M3 -> M15 and M30 · M30 / H1 -> H4. A timeframe must be above the chart's and a whole multiple of it; others are ignored.")
obTf2In   = input.string(OBT_AUTO, "Order Block Timeframe 2", options = [OBT_AUTO, OBT_OFF, "M3", "M5", "M15", "M30", "H1", "H4"], group = GRP_OB)
obTf3In   = input.string(OBT_AUTO, "Order Block Timeframe 3", options = [OBT_AUTO, OBT_OFF, "M3", "M5", "M15", "M30", "H1", "H4"], group = GRP_OB)
OBZ_EET = "Broker server (EU summer time, e.g. FxPro)"
OBZ_NY7 = "Broker server (New York + 7 h)"
OBZ_UTC = "UTC"
OBZ_U2  = "UTC + 2"
OBZ_U3  = "UTC + 3"
obTzIn    = input.string(OBZ_EET, "Higher-Timeframe Candles In", options = [OBZ_EET, OBZ_NY7, OBZ_UTC, OBZ_U2, OBZ_U3], group = GRP_OB, tooltip = "The clock the higher-timeframe candles start on, as on the broker's MetaTrader chart (it matters for H4 only). EU summer time: UTC+2 in winter, UTC+3 from the last Sunday of March to the last Sunday of October (FxPro and other EET brokers). New York + 7 h: the same, but switching on the US dates (most other FX brokers). The EA always uses the broker's own clock.")
obFvgN    = input.int(3, "Fair Value Gap Within (candles)", minval = 2, maxval = 5, group = GRP_OB, tooltip = "Order block: the last opposite candle before a move that leaves a fair value gap (candles k-2 and k do not overlap) within this many candles, and closes beyond the block.")
obEpi     = input.int(30, "Episode (candles from the first touch)", minval = 1, group = GRP_OB, tooltip = "From the first touch of the zone, the absorption and the aggression must come within this many candles; one trade per block.")
obDays    = input.int(20, "A Block Waits For Its First Touch (days)", minval = 1, group = GRP_OB)
obVolN    = input.int(20, "Absorption: Volume Average (candles)", minval = 1, maxval = 500, group = GRP_OB)
obVolMult = input.float(1.0, "Absorption: Volume Above The Average x", minval = 0.01, step = 0.1, group = GRP_OB)
obAbsBody = input.float(40.0, "Absorption: Body Below (% of range)", minval = 1.0, maxval = 100.0, step = 1.0, group = GRP_OB)
obAbsWick = input.float(50.0, "Absorption: Wick Into The Zone (% of range)", minval = 1.0, maxval = 100.0, step = 1.0, group = GRP_OB)
obAggBody = input.float(55.0, "Aggression: Body At Least (% of range)", minval = 1.0, maxval = 100.0, step = 1.0, group = GRP_OB, tooltip = "After an absorption candle in the zone, a candle in the trade's direction with at least this body: market entry at its close (the next candle's open).")
OBS_CANDLE = "Beyond the aggression candle"
OBS_SWING  = "Beyond the last swing (pivot 2 / 2)"
obStopIn  = input.string(OBS_CANDLE, "Order Block Stop", options = [OBS_CANDLE, OBS_SWING], group = GRP_OB)
obBufTk   = input.int(1, "Stop Buffer (ticks)", minval = 0, group = GRP_OB)
obMinTk   = input.int(5, "Smallest Stop Distance (ticks)", minval = 1, group = GRP_OB)
obShow    = input.bool(true, "Draw The Order Block Zones", group = GRP_OB)

'''

SETUP_INPUT = 'setupMode = input.string(S_ONE, "Setups", options = [S_VWAP, S_OB, S_ONE, S_GRID], group = GRP_OB, tooltip = "VWAP only: the Auction Retest setup. Order block only: the order block setup. Both, one trade at a time: whichever setup comes first is traded; a setup on the bar of a VWAP setup waits. Both, true grid: each setup has its own trade, loss recovery and money rules (on TradingView only in the same direction at one time: a strategy holds one net position; the EA trades both ways on a hedging account).")'
SETUP_CONST = 'string setupMode = S_OB   // this strategy trades the order block setup only'

OB_ENGINE = r'''// ── v6.0 order block engine (the EA's ObBar): higher-timeframe candles built from the chart's own candles; a block acts from the bar after
// its candle closed; the first touch starts an episode: absorption (volume above the average, small body, long wick into the zone), then an
// aggression candle = the signal (one per block); a close beyond the block's far side ends it ──
var bool trMkt = false       // v6.0: the setup enters at market (order block)
var int  trSrc = 0           // v6.0: the setup's source: 1 VWAP, 2 order block
var int  curSlot = 0         // v6.0: the slot the engine and the execution run for (true grid: 0 VWAP, 1 order block)
bool gridOn = setupMode == S_GRID
bool obAny  = setupMode != S_VWAP
int  obCm   = int(timeframe.in_seconds(timeframe.period) / 60)
int  obTfMs = timeframe.in_seconds(timeframe.period) * 1000
f_obPick(int q, string v) =>
    int a = obCm == 1 ? (q == 0 ? 3 : q == 1 ? 5 : 0) : obCm == 3 ? (q == 0 ? 15 : q == 1 ? 30 : 0) : obCm == 5 ? (q == 0 ? 15 : q == 1 ? 30 : 60) : obCm == 15 ? (q == 0 ? 60 : q == 1 ? 240 : 0) : obCm == 30 or obCm == 60 ? (q == 0 ? 240 : 0) : 0
    int m = v == OBT_OFF ? 0 : v == "M3" ? 3 : v == "M5" ? 5 : v == "M15" ? 15 : v == "M30" ? 30 : v == "H1" ? 60 : v == "H4" ? 240 : a
    m > obCm and obCm > 0 and m % obCm == 0 and 1440 % m == 0 ? m : 0
f_obList() =>
    array<int> a = array.new_int(0)
    for q = 0 to 2
        int m = f_obPick(q, q == 0 ? obTf1In : q == 1 ? obTf2In : obTf3In)
        if m > 0 and not array.includes(a, m)
            array.push(a, m)
    a
var array<int>   obTfA   = f_obList()
int obTfN = array.size(obTfA)
f_obTfTxt() =>
    string s = ""
    if obTfN > 0
        for q = 0 to obTfN - 1
            int m = array.get(obTfA, q)
            s := s + (q > 0 ? " + " : "") + (m < 60 ? "M" + str.tostring(m) : "H" + str.tostring(int(m / 60)))
    s == "" ? "none" : s
var array<bool>  obCurOn = array.new_bool(3, false)
var array<int>   obCurK  = array.new_int(3, 0)
var array<float> obCurO  = array.new_float(3, 0.0)
var array<float> obCurH  = array.new_float(3, 0.0)
var array<float> obCurL  = array.new_float(3, 0.0)
var array<float> obCurC  = array.new_float(3, 0.0)
var array<int>   obDN    = array.new_int(3, 0)
var array<float> obDO    = array.new_float(18, 0.0)
var array<float> obDH    = array.new_float(18, 0.0)
var array<float> obDL    = array.new_float(18, 0.0)
var array<float> obDC    = array.new_float(18, 0.0)
var array<int>   obZD    = array.new_int(0)
var array<float> obZLo   = array.new_float(0)
var array<float> obZHi   = array.new_float(0)
var array<int>   obZT0   = array.new_int(0)
var array<int>   obZSt   = array.new_int(0)
var array<int>   obZTb   = array.new_int(0)
var array<bool>  obZAb   = array.new_bool(0)
var array<box>   obZBx   = array.new<box>()
var array<float> obPL    = array.new_float(0)
var array<float> obPH    = array.new_float(0)
f_obDel(int k) =>
    box.delete(array.get(obZBx, k))
    array.remove(obZD, k)
    array.remove(obZLo, k)
    array.remove(obZHi, k)
    array.remove(obZT0, k)
    array.remove(obZSt, k)
    array.remove(obZTb, k)
    array.remove(obZAb, k)
    array.remove(obZBx, k)
f_obAdd(int dir, float lo, float hi, int t0) =>
    if array.size(obZD) >= 100
        f_obDel(0)
    box bx = na
    if obShow
        bx := box.new(t0, hi, t0 + obTfMs, lo, xloc = xloc.bar_time, border_color = dir == 1 ? color.new(#26A69A, 0) : color.new(#EF5350, 0), border_style = line.style_dotted, border_width = 1, bgcolor = color.new(#000000, 100))
    array.push(obZD, dir)
    array.push(obZLo, lo)
    array.push(obZHi, hi)
    array.push(obZT0, t0)
    array.push(obZSt, 0)
    array.push(obZTb, -1)
    array.push(obZAb, false)
    array.push(obZBx, bx)
// the fair value gap (kk - 2, kk) of closed candle kk and its close beyond block candle i (slot q's candles start at q * 6)
f_obFvg(int q, int dir, int i, int kk) =>
    int b = q * 6
    dir == 1 ? array.get(obDL, b + kk) > array.get(obDH, b + kk - 2) and array.get(obDC, b + kk) > array.get(obDH, b + i) : array.get(obDH, b + kk) < array.get(obDL, b + kk - 2) and array.get(obDC, b + kk) < array.get(obDL, b + i)
// a higher-timeframe candle closed: keep it (the last 6), then the blocks it completes, acting from t0
f_obClose(int q, int t0) =>
    int b = q * 6
    int n = array.get(obDN, q)
    if n == 6
        for j = 0 to 4
            array.set(obDO, b + j, array.get(obDO, b + j + 1))
            array.set(obDH, b + j, array.get(obDH, b + j + 1))
            array.set(obDL, b + j, array.get(obDL, b + j + 1))
            array.set(obDC, b + j, array.get(obDC, b + j + 1))
        n := 5
    array.set(obDO, b + n, array.get(obCurO, q))
    array.set(obDH, b + n, array.get(obCurH, q))
    array.set(obDL, b + n, array.get(obCurL, q))
    array.set(obDC, b + n, array.get(obCurC, q))
    n += 1
    array.set(obDN, q, n)
    array.set(obCurOn, q, false)
    int k = n - 1
    for dd = 0 to 1
        int dir = dd == 0 ? 1 : -1
        for i = k - obFvgN to k - 2
            if i >= 0
                bool opp = dir == 1 ? array.get(obDC, b + i) < array.get(obDO, b + i) : array.get(obDC, b + i) > array.get(obDO, b + i)
                if opp and f_obFvg(q, dir, i, k)
                    bool early = false
                    if i + 2 <= k - 1
                        for kk = i + 2 to k - 1
                            if f_obFvg(q, dir, i, kk)
                                early := true
                    if not early
                        f_obAdd(dir, array.get(obDL, b + i), array.get(obDH, b + i), t0)
// the clock of the higher-timeframe candles: minutes ahead of UTC
f_obOff(int t) => obTzIn == OBZ_UTC ? 0 : obTzIn == OBZ_U2 ? 120 : obTzIn == OBZ_U3 ? 180 : obTzIn == OBZ_EET ? ((hour(t, "Europe/Athens") - hour(t, "UTC") + 24) % 24) * 60 : ((hour(t, "America/New_York") - hour(t, "UTC") + 24) % 24 - 24) * 60 + 420
f_obKey(int t, int off, int m) => int(math.floor((t + off * 60000) / (m * 60000.0)))
float obV     = na(volume) or volume <= 0 ? 1.0 : volume
float obVa    = ta.sma(obV, obVolN)[1]
bool  obHaveV = bar_index >= obVolN and not na(obVa)
int   obSig   = 0
float obStopC = na
float obStopS = na
if obAny and obTfN > 0
    int obOffM = f_obOff(time)
    for q = 0 to obTfN - 1
        int m  = array.get(obTfA, q)
        int kq = f_obKey(time, obOffM, m)
        if array.get(obCurOn, q) and array.get(obCurK, q) != kq
            f_obClose(q, time)       // the previous candle ended without a bar at its end (a gap): it acts from this bar
        if not array.get(obCurOn, q)
            array.set(obCurOn, q, true)
            array.set(obCurK, q, kq)
            array.set(obCurO, q, open)
            array.set(obCurH, q, high)
            array.set(obCurL, q, low)
            array.set(obCurC, q, close)
        else
            array.set(obCurH, q, math.max(array.get(obCurH, q), high))
            array.set(obCurL, q, math.min(array.get(obCurL, q), low))
            array.set(obCurC, q, close)
    if bar_index >= 4                // the swing 2 bars back is confirmed now
        if low[2] <= low and low[2] <= low[1] and low[2] <= low[3] and low[2] <= low[4]
            if array.size(obPL) == 200
                array.shift(obPL)
            array.push(obPL, low[2])
        if high[2] >= high and high[2] >= high[1] and high[2] >= high[3] and high[2] >= high[4]
            if array.size(obPH) == 200
                array.shift(obPH)
            array.push(obPH, high[2])
    float obRng  = high - low
    float obBody = math.abs(close - open)
    int   obS    = 0
    int   zk     = 0
    while zk < array.size(obZD)
        int zt0 = array.get(obZT0, zk)
        if zt0 > time
            zk += 1                  // its candle closed on this bar: from the next bar
        else
            int   zd    = array.get(obZD, zk)
            float zlo   = array.get(obZLo, zk)
            float zhi   = array.get(obZHi, zk)
            bool  zdead = zd == 1 ? close < zlo : close > zhi
            bool  zgone = false
            bool  zgo   = true
            if array.get(obZSt, zk) == 0
                if time - zt0 > obDays * 86400000 or zdead
                    zgone := true
                else if low <= zhi and high >= zlo
                    array.set(obZSt, zk, 1)  // the first touch starts the episode
                    array.set(obZTb, zk, bar_index)
                else
                    zgo := false
            if not zgone and zgo
                if bar_index - array.get(obZTb, zk) >= obEpi or zdead
                    zgone := true
                else if obRng > 0
                    if array.get(obZAb, zk) and (zd == 1 ? close > open : close < open) and obBody >= obAggBody / 100.0 * obRng
                        obS   := zd          // aggression: traded once
                        zgone := true
                    else if obHaveV and low <= zhi and high >= zlo
                        float zwk = zd == 1 ? math.min(open, close) - low : high - math.max(open, close)
                        if obV > obVolMult * obVa and obBody < obAbsBody / 100.0 * obRng and zwk >= obAbsWick / 100.0 * obRng
                            array.set(obZAb, zk, true)   // absorption
            if zgone
                f_obDel(zk)
            else
                zk += 1
    int obTc = time + obTfMs
    for q = 0 to obTfN - 1
        if array.get(obCurOn, q) and f_obKey(obTc, obOffM, array.get(obTfA, q)) != array.get(obCurK, q)
            f_obClose(q, obTc)       // this bar ends the candle
    if obShow and array.size(obZBx) > 0
        for z = 0 to array.size(obZBx) - 1
            box.set_right(array.get(obZBx, z), obTc)
    if obS != 0
        float obBuf = obBufTk * syminfo.mintick
        obSig   := obS
        obStopC := obS == 1 ? low - obBuf : high + obBuf
        if obS == 1 and array.size(obPL) > 0
            for j = array.size(obPL) - 1 to 0
                if array.get(obPL, j) < close
                    obStopS := array.get(obPL, j) - obBuf
                    break
        if obS == -1 and array.size(obPH) > 0
            for j = array.size(obPH) - 1 to 0
                if array.get(obPH, j) > close
                    obStopS := array.get(obPH, j) + obBuf
                    break

'''

OB_ARM = r'''// v6.0 order block setup: at the aggression candle's close, a market entry on the next bar (one trade at a time: a VWAP setup armed on
// this bar comes first)
if srcO and not vArmed and canArm and obSig != 0
    bool  oIsL  = obSig == 1
    float oD    = oIsL ? 1.0 : -1.0
    float oStop = obStopIn == OBS_CANDLE ? obStopC : obStopS
    float oRisk = na(oStop) ? na : oD * (close - oStop)
    if not na(oStop) and oRisk >= math.max(syminfo.mintick, obMinTk * syminfo.mintick) and math.round_to_mintick(oStop) != math.round_to_mintick(close)
        if math.abs(st) == 1 and not trGhost
            evCancel := "REPLACED"
        st      := oIsL ? 1 : -1
        armBar  := bar_index
        lim     := close
        stp     := oStop
        stp0    := oStop
        trRisk  := oRisk
        trHalf  := false
        trGhost := false
        trSkip  := ""
        trMkt   := true
        trSrc   := 2
        t1      := lim + oD * tp1R * oRisk
        t2      := lim + oD * tp2R * oRisk
        t3      := lim + oD * tp3R * oRisk
        t4      := lim + oD * tp4R * oRisk
        tF      := exitK == 1 ? t1 : exitK == 2 ? t2 : exitK == 3 ? t3 : t4
        evArm   := true
        evArmL  := oIsL
'''


def base(only_ob):
    s = open(SRC, encoding='utf8').read()
    s = rep(s, 'GRP_M = "SIGNAL MODEL"\n', OB_INPUTS.replace('@@SETUP@@', SETUP_CONST if only_ob else SETUP_INPUT) + 'GRP_M = "SIGNAL MODEL"\n')
    s = rep(s, '// ── 1. manage the live trade: stop first, then the final target, else stop moves (from the next bar) ──\n',
            OB_ENGINE + '// ── 1. manage the live trade: stop first, then the final target, else stop moves (from the next bar) ──\n')
    s = rep(s, '    bool touched = entryMode == E_MARKET ? true :', '    bool touched = entryMode == E_MARKET or trMkt ? true :')
    s = rep(s, 'bool keepArm = rearmMode == REARM_KEEP and ((st == 1 and bullDisp) or (st == -1 and bearDisp))\nif canArm and (bullDisp or bearDisp) and not keepArm\n',
            'bool keepArm = rearmMode == REARM_KEEP and ((st == 1 and bullDisp) or (st == -1 and bearDisp))\n'
            'bool srcV    = gridOn ? curSlot == 0 : setupMode != S_OB     // v6.0: the setups this pass arms\n'
            'bool srcO    = gridOn ? curSlot == 1 : setupMode != S_VWAP\n'
            'bool vArmed  = false\n'
            'if srcV and canArm and (bullDisp or bearDisp) and not keepArm\n')
    s = rep(s, '        trGhost := ghost\n', '        trGhost := ghost\n        trMkt   := false\n        trSrc   := 1\n        vArmed  := true\n')
    s = rep(s, '        if not ghost\n            evArm  := true\n            evArmL := isL\n// <<< ENGINE END\n',
            '        if not ghost\n            evArm  := true\n            evArmL := isL\n' + OB_ARM + '// <<< ENGINE END\n')
    s = rep(s, 'st == 1 ? "BUY LIMIT ARMED" : st == -1 ? "SELL LIMIT ARMED"', 'st == 1 ? (trMkt ? "BUY AT MARKET (NEXT BAR)" : "BUY LIMIT ARMED") : st == -1 ? (trMkt ? "SELL AT MARKET (NEXT BAR)" : "SELL LIMIT ARMED")')
    s = rep(s, '        if entryMode == E_MARKET\n            strategy.entry(', '        if entryMode == E_MARKET or trMkt      // v6.0: an order block setup enters at market\n            strategy.entry(')
    if only_ob:
        s = rep(s, 'strategy("Auction Retest Strategy [VWAP Displacement + Retest]", shorttitle = "ARS",',
                'strategy("Order Block Strategy [Absorption + Aggression]", shorttitle = "OBS",')
        s = rep(s, '    table.cell(mon, 0, 0, "AUCTION RETEST",', '    table.cell(mon, 0, 0, "ORDER BLOCK · " + f_obTfTxt(),')
        for g, t in (('GRP_M = "SIGNAL MODEL"', 'GRP_M = "VWAP SIGNAL MODEL (VWAP setup only: not used here)"'), ('GRP_V = "VWAP"', 'GRP_V = "VWAP (VWAP setup only: not used here)"'),
                     ('GRP_E = "ENTRY PRICE"', 'GRP_E = "ENTRY PRICE (VWAP setup only: an order block enters at market)"'),
                     ('GRP_F = "ACCURACY FILTERS (research, off = original)"', 'GRP_F = "ACCURACY FILTERS (VWAP setup only: not used here)"')):
            s = rep(s, g + '\n', t + '\n')
    else:
        s = rep(s, 'strategy("Auction Retest Strategy [VWAP Displacement + Retest]", shorttitle = "ARS",',
                'strategy("Auction Retest + Order Block Strategy [VWAP + Order Block, Grid]", shorttitle = "AROB",')
        s = rep(s, 'pyramiding = 0,', 'pyramiding = 2, close_entries_rule = "ANY",')
        s = rep(s, 'f_row(mon, 1, "STATE", stTxt + exTxt, white)', 'f_row(mon, 1, "STATE", stTxt + exTxt + (st != 0 and not trGhost and setupMode == S_ONE ? (trSrc == 2 ? " (order block)" : " (VWAP)") : ""), white)')
        s = rep(s, '    table.cell(mon, 0, 0, "AUCTION RETEST",', '    table.cell(mon, 0, 0, setupMode == S_VWAP ? "AUCTION RETEST" : setupMode == S_OB ? "ORDER BLOCK · " + f_obTfTxt() : (gridOn ? "GRID: VWAP + OB · " : "VWAP + OB · ") + f_obTfTxt(),')
    return s


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    import grid_pine as G
    ob = base(True)
    open(os.path.join(OUT, 'OrderBlock_Strategy.pine'), 'w', encoding='utf8').write(ob)
    one = base(False)
    gr = G.grid(one)
    open(os.path.join(OUT, 'Auction_Retest_OB_Strategy.pine'), 'w', encoding='utf8').write(gr)
    print('written', len(ob.split('\n')), len(gr.split('\n')))
