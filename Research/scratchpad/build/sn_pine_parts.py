"""v6.1: the VWAP Orderflow Sniper setup as Pine text pieces for build_sn_pine.py (the signal logic of Research/scratchpad/VWAP_Orderflow_Sniper.txt:
absorption arms a setup at the VWAP / band #1, aggression in the same direction fires it; its entry and stop; the targets, stop moves,
money management, news ... are the Auction Retest strategy's). The EA runs the same (sn_ea_parts.py)."""

INPUTS = r'''// ── v6.1 SETUPS AND VWAP ORDERFLOW SNIPER ──
GRP_SN = "SETUPS AND VWAP ORDERFLOW SNIPER"
S_VWAP = "VWAP retest only"
S_SN   = "Sniper only"
S_ONE  = "Both: one trade at a time"
S_GRID = "Both: true grid (same direction)"
setupIn    = input.string(S_ONE, "Setups", options = [S_VWAP, S_SN, S_ONE, S_GRID], group = GRP_SN, tooltip = "VWAP retest only: the Auction Retest setup. Sniper only: the VWAP Orderflow Sniper setup. Both, one trade at a time: whichever setup comes first is traded; a Sniper signal on the bar of a VWAP setup waits. Both, true grid: each setup has its own trade, loss recovery and money rules (on TradingView only in the same direction at one time: a strategy holds one net position; the EA trades both ways on a hedging account). A strategy preset (STRATEGY PRESET) trades the VWAP retest setup only, as it was tested.")
snAggRatio = input.float(2.2, "Aggression Ratio", minval = 1.0, step = 0.1, group = GRP_SN, tooltip = "Aggressive buy volume / aggressive sell volume (or the reverse) a candle needs to count as AGGRESSION.")
snAbsSens  = input.float(1.2, "Absorption Sensitivity (relative volume)", minval = 0.1, step = 0.1, group = GRP_SN, tooltip = "Volume / its average a candle needs before it can count as ABSORPTION (high effort, low result).")
DS_LTF = "Intrabar (lower timeframe)"
DS_EST = "Candle estimate"
snDeltaSrc = input.string(DS_LTF, "Delta Source", options = [DS_LTF, DS_EST], group = GRP_SN, tooltip = "Intrabar: each candle is split into lower-timeframe candles (auto: 1 minute up to H1 charts, 5 minutes up to H4, 15 minutes on D1): up candles = buying volume, down candles = selling volume (unchanged: by the previous close). The candle estimate (buy volume = volume x (close - low) / range) is used when there are fewer than 2 intrabars (an M1 chart, or history older than the intrabar data).")
snCustOn   = input.bool(false, "Custom Lower Timeframe", inline = "snltf", group = GRP_SN)
snCustLtf  = input.timeframe("1", "", inline = "snltf", group = GRP_SN, tooltip = "Used when it is below the chart's timeframe; else the automatic one.")
snVolLen   = input.int(20, "Volume Average Length", minval = 2, maxval = 200, group = GRP_SN)
snAtrLen   = input.int(14, "Sniper ATR Length", minval = 1, maxval = 200, group = GRP_SN)
snAbsLen   = input.int(5, "Absorption Lookback (bars)", minval = 2, maxval = 200, group = GRP_SN, tooltip = "Window of the delta-divergence absorption and of the local high / low (churn).")
snDivMin   = input.float(15.0, "Delta Divergence Min %", minval = 1.0, maxval = 100.0, step = 1.0, group = GRP_SN)
snWickPct  = input.float(40.0, "Rejection Wick Min %", minval = 10.0, maxval = 90.0, step = 5.0, group = GRP_SN)
snAggRelV  = input.float(1.0, "Aggression Min Relative Volume", minval = 0.0, step = 0.1, group = GRP_SN)
snAggBody  = input.float(50.0, "Aggression Min Body %", minval = 0.0, maxval = 100.0, step = 5.0, group = GRP_SN)
SM_SNIPER = "Sniper (absorption + aggression)"
SM_AGGR   = "Aggression only"
SM_BRK    = "Absorption breakout"
snMode     = input.string(SM_SNIPER, "Signal Mode", options = [SM_SNIPER, SM_AGGR, SM_BRK], group = GRP_SN, tooltip = "Sniper: absorption at the VWAP arms a setup, the next aggressive candle in the same direction fires the signal. Aggression only: every aggressive candle on the right side of the VWAP. Absorption breakout: an armed setup and a candle closing beyond the absorption zone.")
snExpiry   = input.int(10, "Setup Expiry (bars)", minval = 1, group = GRP_SN)
ZN_VWAP = "VWAP"
ZN_BAND = "VWAP or band #1"
ZN_ANY  = "Anywhere"
snZone     = input.string(ZN_BAND, "Absorption Location", options = [ZN_VWAP, ZN_BAND, ZN_ANY], group = GRP_SN, tooltip = "Where absorption must happen to arm a setup: longs at the VWAP / upper band #1, shorts at the VWAP / lower band #1 (the strategy's VWAP).")
BM_SD  = "Standard deviation"
BM_PCT = "Percentage"
snBandMode = input.string(BM_SD, "Band #1 (mode, x)", options = [BM_SD, BM_PCT], inline = "snband", group = GRP_SN)
snBandMult = input.float(1.0, "", minval = 0.0, step = 0.5, inline = "snband", group = GRP_SN, tooltip = "Band #1 = VWAP +- this x the VWAP's standard deviation (or x 1% of the VWAP).")
snZoneAtr  = input.float(0.75, "VWAP Zone Width (ATR)", minval = 0.05, step = 0.05, group = GRP_SN)
snMaxDist  = input.float(2.5, "Max Distance From VWAP (ATR)", minval = 0.0, step = 0.1, group = GRP_SN, tooltip = "0 = off.")
CV_OFF  = "Off"
CV_ROLL = "Rolling delta"
CV_SESS = "Session CVD"
snCvd      = input.string(CV_ROLL, "CVD Confirmation (mode, length)", options = [CV_OFF, CV_ROLL, CV_SESS], inline = "sncvd", group = GRP_SN)
snCvdLen   = input.int(3, "", minval = 1, maxval = 200, inline = "sncvd", group = GRP_SN, tooltip = "Rolling delta: the delta of the last Len bars must agree with the signal. Session CVD: the delta since the VWAP started.")
snSlopeOn  = input.bool(false, "VWAP Slope Filter (length)", inline = "snslope", group = GRP_SN)
snSlopeLen = input.int(5, "", minval = 1, maxval = 200, inline = "snslope", group = GRP_SN, tooltip = "Buys need a rising VWAP, sells a falling one over Len bars.")
snCool     = input.int(3, "Bars Between Sniper Signals", minval = 0, group = GRP_SN)
SE_CLOSE = "Signal close (market)"
SE_MID   = "Signal bar midpoint (limit)"
SE_VWAP  = "VWAP retest (limit)"
snEntry    = input.string(SE_CLOSE, "Sniper Entry", options = [SE_CLOSE, SE_MID, SE_VWAP], group = GRP_SN, tooltip = "A limit entry waits for the Retest Window of the ENTRY / SIGNAL settings.")
snOffset   = input.float(0.0, "Sniper Entry Offset (price)", minval = 0.0, step = 0.1, group = GRP_SN, tooltip = "A better price: longs lower, shorts higher. Above 0 the entry is a limit order.")
SL_STRUCT = "Absorption / swing"
SL_ATR    = "ATR"
SL_PTS    = "Fixed points"
SL_PCT    = "Percent"
snSlMode   = input.string(SL_STRUCT, "Sniper Stop", options = [SL_STRUCT, SL_ATR, SL_PTS, SL_PCT], group = GRP_SN, tooltip = "Absorption / swing: beyond the absorption zone (or the low / high of the last swing bars without a zone) plus a buffer, kept between the min and max risk. ATR: x the Sniper ATR. Fixed points: a price distance. Percent: of the price.")
snSlAtr    = input.float(1.5, "Stop ATR x", minval = 0.1, step = 0.1, group = GRP_SN)
snSlPts    = input.float(5.0, "Stop Fixed Points (price)", minval = 0.01, step = 0.5, group = GRP_SN)
snSlPct    = input.float(0.25, "Stop Percent %", minval = 0.01, step = 0.05, group = GRP_SN)
snSlBuf    = input.float(0.15, "Structure Stop Buffer (ATR)", minval = 0.0, step = 0.05, group = GRP_SN)
snSwingLen = input.int(5, "Swing Lookback (bars)", minval = 1, maxval = 200, group = GRP_SN)
snMinRisk  = input.float(0.3, "Structure Risk Min / Max (ATR)", minval = 0.0, step = 0.1, inline = "snrisk", group = GRP_SN)
snMaxRisk  = input.float(4.0, "", minval = 0.1, step = 0.1, inline = "snrisk", group = GRP_SN)
snShowZone = input.bool(true, "Draw The Absorption Zones", group = GRP_SN)

'''

ENGINE = r'''// ── v6.1 VWAP Orderflow Sniper (the EA's SnBar): the buy / sell volume of each candle, absorption (heavy volume that fails to move the
// price: rejection wick, delta against the candle, churn at an extreme, delta divergence) arms a setup near the VWAP / band #1; the next
// aggressive candle (one side >= the ratio x the other, full body, volume) on the right side of the VWAP is the signal ──
string setupMode = PC ? setupIn : S_VWAP   // a strategy preset trades the VWAP retest setup only (as tested)
var bool trMkt = false       // v6.0: the setup enters at market
var int  trSrc = 0           // v6.0: the setup's source: 1 VWAP retest, 2 Sniper
var int  curSlot = 0         // v6.0: the slot the engine and the execution run for (true grid: 0 VWAP retest, 1 Sniper)
bool  gridOn  = setupMode == S_GRID
bool  snAny   = setupMode != S_VWAP
float snAtr   = ta.atr(snAtrLen)
float snAvgV  = ta.sma(volume, snVolLen)
float snRelV  = snAvgV > 0 ? volume / snAvgV : 0.0
float snRng   = high - low
float snBodyP = snRng > 0 ? math.abs(close - open) / snRng : 0.0
float snClPos = snRng > 0 ? (close - low) / snRng : 0.5
float snLoW   = math.min(open, close) - low
float snUpW   = high - math.max(open, close)
// intrabar volume split: up candle = buying, down candle = selling, unchanged = by the previous close (half each when that is equal too)
f_snSplit() =>
    float dr = close > open ? 1.0 : close < open ? -1.0 : math.sign(close - nz(close[1], close))
    float v  = nz(volume)
    [dr > 0 ? v : dr < 0 ? 0.0 : v * 0.5, dr < 0 ? v : dr > 0 ? 0.0 : v * 0.5]
int    snTfSec = timeframe.in_seconds()
string snAuto  = snTfSec <= 60 ? timeframe.period : snTfSec <= 3600 ? "1" : snTfSec <= 14400 ? "5" : snTfSec <= 86400 ? "15" : "60"
string snLtf   = snCustOn and timeframe.in_seconds(snCustLtf) < snTfSec ? snCustLtf : snAuto
[snBA, snSA] = request.security_lower_tf(syminfo.tickerid, snLtf, f_snSplit())
bool  snIntra = snDeltaSrc == DS_LTF and array.size(snBA) >= 2
float snV     = nz(volume)
float snBuyV  = snIntra ? nz(array.sum(snBA)) : snRng > 0 ? snV * (close - low) / snRng : snV * 0.5
float snSellV = snIntra ? nz(array.sum(snSA)) : snV - snBuyV
float snTotV  = snBuyV + snSellV
float snDelta = snBuyV - snSellV
float snBullR = snBuyV / math.max(snSellV, snTotV * 0.01, 0.000001)
float snBearR = snSellV / math.max(snBuyV, snTotV * 0.01, 0.000001)
var float snCvdS = 0.0
snCvdS := newAnchor ? snDelta : snCvdS + snDelta
float snRoll   = math.sum(snDelta, snCvdLen)
bool  snBullAg = close > open and snBullR >= snAggRatio and snRelV >= snAggRelV and snBodyP * 100.0 >= snAggBody
bool  snBearAg = close < open and snBearR >= snAggRatio and snRelV >= snAggRelV and snBodyP * 100.0 >= snAggBody
float snLoL    = ta.lowest(low, snAbsLen)
float snHiH    = ta.highest(high, snAbsLen)
float snWinD   = math.sum(snDelta, snAbsLen)
float snWinV   = math.sum(snTotV, snAbsLen)
float snWinRV  = math.sum(snV, snAbsLen)
float snWinDP  = snWinV > 0 ? 100.0 * snWinD / snWinV : 0.0
float snWinRel = snAvgV > 0 ? snWinRV / (snAvgV * snAbsLen) : 0.0
float snBack   = close[snAbsLen]
bool  snEffort = snRelV >= snAbsSens
bool  snBullAb = (snEffort and snLoW >= snRng * snWickPct / 100.0 and snClPos >= 0.5) or (snIntra and snEffort and snDelta < 0 and close >= open) or (snRelV >= snAbsSens * 1.5 and snRng <= snAtr * 0.7 and low <= snLoL) or (snWinDP <= -snDivMin and close >= snBack and snWinRel >= 1.0)
bool  snBearAb = (snEffort and snUpW >= snRng * snWickPct / 100.0 and snClPos <= 0.5) or (snIntra and snEffort and snDelta > 0 and close <= open) or (snRelV >= snAbsSens * 1.5 and snRng <= snAtr * 0.7 and high >= snHiH) or (snWinDP >= snDivMin and close <= snBack and snWinRel >= 1.0)
float snBasis  = snBandMode == BM_SD ? vwSd : vwap * 0.01
float snUp1    = vwap + snBasis * snBandMult
float snLo1    = vwap - snBasis * snBandMult
bool  snVwOk   = not na(vwap)
float snZoneW  = snZoneAtr * snAtr
f_snTouch(float level, float z) => not na(level) and low <= level + z and high >= level - z
bool  snBullCtx = snVwOk and close >= vwap - snZoneW and (snZone == ZN_ANY or f_snTouch(vwap, snZoneW) or (snZone == ZN_BAND and f_snTouch(snUp1, snZoneW)))
bool  snBearCtx = snVwOk and close <= vwap + snZoneW and (snZone == ZN_ANY or f_snTouch(vwap, snZoneW) or (snZone == ZN_BAND and f_snTouch(snLo1, snZoneW)))
float snDist   = snVwOk and snAtr > 0 ? math.abs(close - vwap) / snAtr : 0.0
bool  snDistOk = snMaxDist <= 0 or snDist <= snMaxDist
float snSlope  = vwap - vwap[snSlopeLen]
float snSwLo   = ta.lowest(low, snSwingLen)
float snSwHi   = ta.highest(high, snSwingLen)
var int   snBullArm = na
var float snBullLo  = na
var float snBullHi  = na
var box   snBullBox = na
var int   snBearArm = na
var float snBearLo  = na
var float snBearHi  = na
var box   snBearBox = na
var int   snLastSig = na
bool snBullArmed = not na(snBullArm) and bar_index - snBullArm <= snExpiry
bool snBearArmed = not na(snBearArm) and bar_index - snBearArm <= snExpiry
// a setup ends when the price loses the VWAP side or closes through the absorption zone
if snBullArmed and (close < vwap - snZoneW or close < snBullLo)
    snBullArm   := na
    snBullArmed := false
if snBearArmed and (close > vwap + snZoneW or close > snBearHi)
    snBearArm   := na
    snBearArmed := false
if snAny and snBullAb and snBullCtx
    if snBullArmed
        snBullLo := math.min(snBullLo, low)
        snBullHi := math.max(snBullHi, high)
        if not na(snBullBox)
            box.set_top(snBullBox, snBullHi)
            box.set_bottom(snBullBox, snBullLo)
    else
        snBullLo  := low
        snBullHi  := high
        snBullBox := na
        if snShowZone
            snBullBox := box.new(bar_index, high, bar_index + snExpiry, low, border_color = color.new(#2962FF, 40), border_width = 1, border_style = line.style_dotted, bgcolor = color.new(#2962FF, 88))
    snBullArm   := bar_index
    snBullArmed := true
if snAny and snBearAb and snBearCtx
    if snBearArmed
        snBearLo := math.min(snBearLo, low)
        snBearHi := math.max(snBearHi, high)
        if not na(snBearBox)
            box.set_top(snBearBox, snBearHi)
            box.set_bottom(snBearBox, snBearLo)
    else
        snBearLo  := low
        snBearHi  := high
        snBearBox := na
        if snShowZone
            snBearBox := box.new(bar_index, high, bar_index + snExpiry, low, border_color = color.new(#FF9800, 40), border_width = 1, border_style = line.style_dotted, bgcolor = color.new(#FF9800, 88))
    snBearArm   := bar_index
    snBearArmed := true
bool snCoolOk = na(snLastSig) or bar_index - snLastSig >= snCool
bool snBullF  = snVwOk and close > vwap and snDistOk and (not snSlopeOn or snSlope > 0) and (snCvd == CV_OFF or (snCvd == CV_ROLL ? snRoll > 0 : snCvdS > 0)) and snCoolOk
bool snBearF  = snVwOk and close < vwap and snDistOk and (not snSlopeOn or snSlope < 0) and (snCvd == CV_OFF or (snCvd == CV_ROLL ? snRoll < 0 : snCvdS < 0)) and snCoolOk
bool snBuy    = snAny and snBullF and (snMode == SM_AGGR ? snBullAg : snMode == SM_BRK ? (snBullArmed and close > snBullHi and close > open) : (snBullArmed and snBullAg))
bool snSell   = snAny and snBearF and not snBuy and (snMode == SM_AGGR ? snBearAg : snMode == SM_BRK ? (snBearArmed and close < snBearLo and close < open) : (snBearArmed and snBearAg))
int   snSig   = 0
float snEnt   = na
float snStp   = na
if snBuy or snSell
    int   sd   = snBuy ? 1 : -1
    bool  hasZ = sd == 1 ? snBullArmed : snBearArmed
    float zExt = sd == 1 ? snBullLo : snBearHi
    float sBase = snEntry == SE_MID ? hl2 : snEntry == SE_VWAP ? (sd == 1 ? math.min(close, vwap) : math.max(close, vwap)) : close
    float sEnt  = sBase - sd * snOffset
    float sStr  = sd == 1 ? (hasZ ? math.min(zExt, low) : snSwLo) - snSlBuf * snAtr : (hasZ ? math.max(zExt, high) : snSwHi) + snSlBuf * snAtr
    float sRisk = snSlMode == SL_ATR ? snAtr * snSlAtr : snSlMode == SL_PTS ? snSlPts : snSlMode == SL_PCT ? sEnt * snSlPct / 100.0 : sd * (sEnt - sStr)
    if snSlMode == SL_STRUCT
        sRisk := math.max(snMinRisk * snAtr, math.min(snMaxRisk * snAtr, nz(sRisk, snMinRisk * snAtr)))
    if not (sRisk > 0)
        sRisk := math.max(nz(snAtr) * 0.5, syminfo.mintick * 10)
    snSig     := sd
    snEnt     := sEnt
    snStp     := sEnt - sd * sRisk
    snLastSig := bar_index
    if sd == 1
        snBullArm := na
    else
        snBearArm := na

'''

ARM = r'''// v6.1 Sniper setup: the Sniper's entry (market at the signal close, or a limit) and stop; one trade at a time: a VWAP setup armed on this
// bar comes first
if srcO and not vArmed and canArm and snSig != 0
    bool  oIsL  = snSig == 1
    float oD    = oIsL ? 1.0 : -1.0
    float oRisk = oD * (snEnt - snStp)
    if oRisk >= syminfo.mintick and math.round_to_mintick(snStp) != math.round_to_mintick(snEnt)
        if math.abs(st) == 1 and not trGhost
            evCancel := "REPLACED"
        st      := oIsL ? 1 : -1
        armBar  := bar_index
        lim     := snEnt
        stp     := snStp
        stp0    := snStp
        trRisk  := oRisk
        trHalf  := false
        trGhost := false
        trSkip  := ""
        trMkt   := snEnt == close
        trSrc   := 2
        t1      := lim + oD * tp1R * oRisk
        t2      := lim + oD * tp2R * oRisk
        t3      := lim + oD * tp3R * oRisk
        t4      := lim + oD * tp4R * oRisk
        tF      := exitK == 1 ? t1 : exitK == 2 ? t2 : exitK == 3 ? t3 : t4
        evArm   := true
        evArmL  := oIsL
'''
