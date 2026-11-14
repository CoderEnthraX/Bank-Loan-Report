"""Builds TradingView/Fractal_Breakout_Grid.pine (the 11-strategy indicator) from the strategy table below.
Usage: build_fbg.py OUT.pine"""
import sys, json
# (fractal TF, right, left, offset %, SL %, TP %, BE %, salvage %); 10 and 11 from the gold search (search_pick.json)
STRATS = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else None
COLS = ['#2962FF', '#FF6D00', '#AA00FF', '#00BFA5', '#F50057', '#00B8D4', '#FFAB00', '#8D6E63', '#3D5AFE', '#C6FF00', '#FF3D00']
TFV = {'D1': 'D', 'H4': '240', 'H1': '60', 'M15': '15', 'M5': '5'}


def num(x):
    s = ('%.4f' % x).rstrip('0')
    return s + '0' if s.endswith('.') else s


def block(i, p):
    tf, r, l, off, sl, tp, be, sv = p
    g = 'GRP_%d' % i
    return '''{g} = "STRATEGY {i}"
s{i}On  = input.bool(true, "On", inline = "s{i}a", group = {g})
s{i}Col = input.color({col}, "", inline = "s{i}a", group = {g})
s{i}Tf  = input.timeframe("{tfv}", "Fractal TF / Buy Entry Offset %", inline = "s{i}b", group = {g})
s{i}Off = input.float({off}, "", minval = -5.0, maxval = 5.0, step = 0.005, inline = "s{i}b", group = {g}, tooltip = TT_TF)
s{i}R   = input.int({r}, "Right / Left Candles", minval = 1, maxval = 200, inline = "s{i}c", group = {g})
s{i}L   = input.int({l}, "", minval = 1, maxval = 200, inline = "s{i}c", group = {g}, tooltip = TT_RL)
s{i}Sl  = input.float({sl}, "SL % / TP %", minval = 0.001, step = 0.01, inline = "s{i}d", group = {g})
s{i}Tp  = input.float({tp}, "", minval = 0.001, step = 0.01, inline = "s{i}d", group = {g}, tooltip = TT_ST)
s{i}Be  = input.float({be}, "BE / Salvage Trigger %", minval = 0.0, step = 0.01, inline = "s{i}e", group = {g})
s{i}Sv  = input.float({sv}, "", minval = 0.0, step = 0.01, inline = "s{i}e", group = {g}, tooltip = TT_BS)
'''.format(g=g, i=i, col=COLS[i - 1], tfv=TFV[tf], off=num(off), r=r, l=l, sl=num(sl), tp=num(tp), be=num(be), sv=num(sv))


HEAD = '''//@version=6
// =======================================================================================================
//  FRACTAL BREAKOUT GRID: 11 long breakout strategies on swing highs (fractals)
// =======================================================================================================
//  Each strategy finds swing highs on its own timeframe: a candle whose high is strictly above the Left
//  candles before it and the Right candles after it. When the last Right candle closes, the swing high
//  sets a buy stop at high x (1 + offset / 100), replacing that strategy's older buy stop. A trade opens
//  when the price rises through it; one trade at a time per strategy (a breakout while a trade is open
//  is skipped); either way that buy stop is then used up.
//  Exits from the fill price: SL % and TP %. BE trigger: once the price is up this %, the SL moves to
//  the entry. Salvage trigger: once the price is down this %, the TP moves to the entry (out at
//  break-even if the price comes back). Only the first of the two happens in a trade; 0 = off.
//  Strategies 1-9: your table. 10 (5 min swing highs) and 11 (15 min): picked on gold 2021-2026.
//  The trades are worked out on the chart's candles, along open -> the nearer of high / low -> the other
//  -> close (gaps fill at the open). Use a chart timeframe at or below each strategy's timeframe (5 min
//  or 1 min runs all 11). Swing highs come from completed candles only, so nothing repaints.
//  Alerts: create one alert with "Any alert() function call" (sent at the candle close).
// =======================================================================================================
indicator("Fractal Breakout Grid", shorttitle = "FBG", overlay = true, max_lines_count = 500, max_labels_count = 500, max_bars_back = 500)

// ---------------------------------------------------------------- GRID
GRP_G   = "GRID"
RUN_ALL = "All strategies"
RUN_TCK = "Ticked strategies"
runMode = input.string(RUN_ALL, "Run", options = [RUN_ALL, RUN_TCK, "Strategy 1", "Strategy 2", "Strategy 3", "Strategy 4", "Strategy 5", "Strategy 6", "Strategy 7", "Strategy 8", "Strategy 9", "Strategy 10", "Strategy 11"], group = GRP_G, tooltip = "All strategies: all 11 run. Ticked strategies: only those with On ticked below. Strategy N: that one alone.")
costIn  = input.float(0.23, "Costs Per Trade (price units)", minval = 0.0, step = 0.01, group = GRP_G, tooltip = "Spread + commission of one trade in price units, taken off every trade in the table (the levels do not move). Gold: spread 0.16 + $7 per lot of 100 oz (0.07) = 0.23.")
statsFrom = input.time(timestamp("01 Jan 2021 00:00 +0000"), "Table Counts Trades From", group = GRP_G, tooltip = "The table counts the trades that opened at or after this time (and within the chart's loaded history).")

GRP_D   = "DISPLAY"
P_TR = "Top Right"
P_BR = "Bottom Right"
P_BL = "Bottom Left"
P_TL = "Top Left"
P_MR = "Middle Right"
T_TI = "Tiny"
T_SM = "Small"
T_NO = "Normal"
showLvl = input.bool(true, "Waiting Buy Stops", group = GRP_D, tooltip = "A dashed line at each strategy's waiting buy stop, from the candle it is set until it fills, is skipped or a newer swing high replaces it.")
showTr  = input.bool(true, "Trades: Entry, SL And TP Lines", group = GRP_D, tooltip = "Entry line in the strategy's colour, TP green, SL red. After the BE trigger the SL line continues at the entry (orange); after the salvage trigger the TP line continues at the entry (orange).")
showLbl = input.bool(true, "Entry And Exit Labels", group = GRP_D)
showTbl = input.bool(true, "Table", inline = "tb", group = GRP_D)
tblPos  = input.string(P_TR, "", options = [P_TR, P_BR, P_BL, P_TL, P_MR], inline = "tb", group = GRP_D)
tblTxt  = input.string(T_SM, "", options = [T_TI, T_SM, T_NO], inline = "tb", group = GRP_D)

GRP_A = "ALERTS (one alert: Any alert() function call)"
alLvl = input.bool(true, "New Buy Stop", group = GRP_A, tooltip = "When a swing high is confirmed: the strategy, the buy stop price, its SL and TP. Sent at the close of the candle where it is set.")
alEnt = input.bool(true, "Entry", group = GRP_A)
alExt = input.bool(true, "Exit", group = GRP_A)

TT_TF = "Fractal TF: the timeframe of the swing highs (D = daily, 240 = 4 hours, 60 = 1 hour, 15, 5); not below the chart's timeframe.\\nBuy entry offset %: the buy stop is at swing high x (1 + offset / 100); -0.14 = 0.14 % below the swing high."
TT_RL = "Right: candles after the swing high (it is confirmed when the last of them closes). Left: candles before it. The swing high must be strictly higher than all of them."
TT_ST = "SL % and TP % from the fill price."
TT_BS = "BE trigger %: once the price is up this % from the fill, the SL moves to the fill (break-even).\\nSalvage trigger %: once the price is down this % from the fill, the TP moves to the fill (out at break-even if the price comes back).\\nOnly the first of the two happens in a trade. 0 = off."

'''

BODY = '''
// ---------------------------------------------------------------- swing highs (completed candles only)
// on fractal candle k: the swing high of candle p = k - 1 - right, confirmed when candle k - 1 (= p + right) closed:
// high[p] above the highest of the left candles before it and of the right candles after it
f_piv(int lft, int rgt) =>
    float lh = ta.highest(high, lft)[rgt + 2]
    float rh = ta.highest(high, rgt)[1]
    float p  = high[rgt + 1]
    bool  ok = not na(lh) and not na(rh) and not na(p) and p > lh and p > rh
    [ok ? p : na, ok ? time[rgt + 1] : na]

// a strategy runs only when its timeframe is not below the chart's; otherwise it requests the chart's own timeframe (unused)
f_fits(string tf) =>
    timeframe.in_seconds(tf) >= timeframe.in_seconds(timeframe.period)

{SEC}
// ---------------------------------------------------------------- one strategy
C_TP   = color.new(#26A69A, 0)
C_SL   = color.new(#EF5350, 0)
C_MOVE = color.new(#FF9800, 0)
C_WIN  = color.new(#26A69A, 10)
C_LOSS = color.new(#EF5350, 10)

type Strat
    int    id
    bool   sel
    bool   ok
    string tf
    int    r
    int    l
    float  off
    float  sl
    float  tp
    float  be
    float  sv
    color  col
    bool   lvlOn  = false
    float  lvlH   = na
    float  E      = na
    int    lvlT   = na
    bool   pos    = false
    float  F      = na
    float  SLp    = na
    float  TPp    = na
    float  BEl    = na
    float  SVl    = na
    bool   beOn   = false
    bool   svOn   = false
    int    eTime  = na
    int    n      = 0
    int    nW     = 0
    int    nTP    = 0
    int    nSL    = 0
    int    nBE    = 0
    int    nSV    = 0
    float  sumPct = 0.0
    float  sumR   = 0.0
    float  gw     = 0.0
    float  gl     = 0.0
    float  cum    = 0.0
    float  pk     = 0.0
    float  dd     = 0.0
    int    st     = 0
    int    mst    = 0
    line   lnLvl  = na
    line   lnE    = na
    line   lnSL   = na
    line   lnTP   = na
    string msg    = ""

f_px(float x) =>
    str.tostring(x, format.mintick)

f_num(float x, string f) =>
    str.tostring(x, f)

f_sgn(float x, string f) =>
    (x >= 0 ? "+" : "") + str.tostring(x, f)

method openAt(Strat s, float px, bool gap) =>
    s.pos   := true
    s.F     := px
    s.SLp   := px * (1.0 - s.sl / 100.0)
    s.TPp   := px * (1.0 + s.tp / 100.0)
    s.BEl   := px * (1.0 + s.be / 100.0)
    s.SVl   := px * (1.0 - s.sv / 100.0)
    s.beOn  := false
    s.svOn  := false
    s.eTime := time
    if showTr
        s.lnE  := line.new(bar_index, px, bar_index, px, color = s.col, width = 2)
        s.lnTP := line.new(bar_index, s.TPp, bar_index, s.TPp, color = C_TP)
        s.lnSL := line.new(bar_index, s.SLp, bar_index, s.SLp, color = C_SL)
    if showLbl
        label.new(bar_index, px, str.tostring(s.id) + (gap ? " BUY (gap)" : " BUY"), color = s.col, textcolor = color.white, style = label.style_label_up, size = size.tiny)
    if alEnt
        s.msg += "FBG S" + str.tostring(s.id) + " BUY " + f_px(px) + (gap ? " (gap open)" : "") + " | SL " + f_px(s.SLp) + " | TP " + f_px(s.TPp) + "\\n"
    true

method closeAt(Strat s, float px, int rsn) =>
    float pnl = px - s.F - costIn
    float pct = pnl / s.F * 100.0
    float rr  = pnl / (s.F * s.sl / 100.0)
    if s.eTime >= statsFrom
        s.n      += 1
        s.sumPct += pct
        s.sumR   += rr
        if pnl > 0
            s.nW += 1
            s.gw += rr
        else
            s.gl -= rr
        if rsn == 2
            s.st  += 1
            s.mst := math.max(s.mst, s.st)
        else if rsn == 1
            s.st := 0
        s.cum += rr
        s.pk  := math.max(s.pk, s.cum)
        s.dd  := math.max(s.dd, s.pk - s.cum)
        if rsn == 1
            s.nTP += 1
        else if rsn == 2
            s.nSL += 1
        else if rsn == 3
            s.nBE += 1
        else
            s.nSV += 1
    string rs = rsn == 1 ? "TP" : rsn == 2 ? "SL" : rsn == 3 ? "BE" : "SALV"
    if not na(s.lnE)
        s.lnE.set_x2(bar_index)
    if not na(s.lnSL)
        s.lnSL.set_x2(bar_index)
    if not na(s.lnTP)
        s.lnTP.set_x2(bar_index)
    s.lnE  := na
    s.lnSL := na
    s.lnTP := na
    if showLbl
        label.new(bar_index, px, str.tostring(s.id) + " " + rs + " " + f_sgn(pct, "0.00") + "%", color = pnl > 0 ? C_WIN : C_LOSS, textcolor = color.white, style = label.style_label_down, size = size.tiny)
    if alExt
        s.msg += "FBG S" + str.tostring(s.id) + " EXIT " + rs + " " + f_px(px) + " (" + f_sgn(pct, "0.00") + "% after costs, " + f_sgn(rr, "0.00") + "R)\\n"
    s.pos := false
    true

// BE trigger reached: the SL moves to the entry
method doBE(Strat s) =>
    s.beOn := true
    s.SLp  := s.F
    if not na(s.lnSL)
        s.lnSL.set_x2(bar_index)
        s.lnSL := line.new(bar_index, s.F, bar_index, s.F, color = C_MOVE, style = line.style_dotted, width = 2)
    true

// salvage trigger reached: the TP moves to the entry
method doSV(Strat s) =>
    s.svOn := true
    s.TPp  := s.F
    if not na(s.lnTP)
        s.lnTP.set_x2(bar_index)
        s.lnTP := line.new(bar_index, s.F, bar_index, s.F, color = C_MOVE, style = line.style_dotted, width = 2)
    true

// the waiting buy stop is used up (filled, or skipped while a trade is open)
method useLvl(Strat s) =>
    s.lvlOn := false
    if not na(s.lnLvl)
        s.lnLvl.set_x2(bar_index)
    s.lnLvl := na
    true

// the price moves up from x to y: TP, BE trigger and the buy stop, lowest first (equal: TP, BE, buy stop)
method up(Strat s, float x, float y) =>
    for _i = 0 to 7
        float best = na
        int   ev   = 0
        if s.pos
            if x < s.TPp and s.TPp <= y
                best := s.TPp
                ev   := 1
            if s.be > 0 and not s.beOn and not s.svOn and x < s.BEl and s.BEl <= y and (na(best) or s.BEl < best)
                best := s.BEl
                ev   := 2
        if s.lvlOn and x < s.E and s.E <= y and (na(best) or s.E < best)
            best := s.E
            ev   := 3
        if ev == 0
            break
        if ev == 1
            s.closeAt(s.TPp, s.svOn ? 4 : 1)
        else if ev == 2
            s.doBE()
        else
            if not s.pos
                s.openAt(s.E, false)
            s.useLvl()
    true

// the price moves down from x to y: SL and salvage trigger, highest first (equal: SL)
method dn(Strat s, float x, float y) =>
    for _i = 0 to 7
        float best = na
        int   ev   = 0
        if s.pos
            if y <= s.SLp and s.SLp < x
                best := s.SLp
                ev   := 1
            if s.sv > 0 and not s.svOn and not s.beOn and y <= s.SVl and s.SVl < x and (na(best) or s.SVl > best)
                best := s.SVl
                ev   := 2
        if ev == 0
            break
        if ev == 1
            s.closeAt(s.SLp, s.beOn ? 3 : 2)
        else
            s.doSV()
    true

method seg(Strat s, float x, float y) =>
    if y > x
        s.up(x, y)
    else if y < x
        s.dn(x, y)
    true

// one chart candle: a new swing high, the open (exits, then a gap fill), then open -> a -> b -> close
method onBar(Strat s, float ph, int pt, float pc) =>
    s.msg := ""
    bool lvlNew = false
    if not na(ph) and not na(pt) and (na(s.lvlT) or pt != s.lvlT)
        if not na(s.lnLvl)
            s.lnLvl.set_x2(bar_index)
        s.lvlT  := pt
        s.lvlOn := true
        s.lvlH  := ph
        s.E     := ph * (1.0 + s.off / 100.0)
        lvlNew  := true
        s.lnLvl := showLvl ? line.new(bar_index, s.E, bar_index, s.E, color = s.col, style = line.style_dashed) : na
        if alLvl
            s.msg += "FBG S" + str.tostring(s.id) + " BUY STOP " + f_px(s.E) + " (swing high " + f_px(ph) + ", " + s.tf + " " + str.tostring(s.r) + "/" + str.tostring(s.l) + ") | SL " + f_num(s.sl, "0.0##") + "% | TP " + f_num(s.tp, "0.0##") + "%\\n"
    if s.pos
        if open >= s.TPp
            s.closeAt(open, s.svOn ? 4 : 1)
        else if open <= s.SLp
            s.closeAt(open, s.beOn ? 3 : 2)
        else if s.be > 0 and not s.beOn and not s.svOn and open >= s.BEl
            s.doBE()
        else if s.sv > 0 and not s.svOn and not s.beOn and open <= s.SVl
            s.doSV()
    if s.lvlOn and not lvlNew and not na(pc) and pc < s.E and open >= s.E
        if not s.pos
            s.openAt(open, true)
        s.useLvl()
    bool  hf = (high - open) < (open - low)
    float a  = hf ? high : low
    float b  = hf ? low : high
    s.seg(open, a)
    s.seg(a, b)
    s.seg(b, close)
    if s.lvlOn and not na(s.lnLvl)
        s.lnLvl.set_x2(bar_index)
    if s.pos
        if not na(s.lnE)
            s.lnE.set_x2(bar_index)
        if not na(s.lnSL)
            s.lnSL.set_x2(bar_index)
        if not na(s.lnTP)
            s.lnTP.set_x2(bar_index)
    true

f_run(int i, bool ticked) =>
    runMode == RUN_ALL ? true : runMode == RUN_TCK ? ticked : runMode == "Strategy " + str.tostring(i)

var array<Strat> S = array.new<Strat>()
if barstate.isfirst
{NEW}
// ---------------------------------------------------------------- every candle
array<float> PH = array.from({PHS})
array<int>   PT = array.from({PTS})
string alertMsg = ""
for [i, s] in S
    if s.ok
        s.onBar(PH.get(i), PT.get(i), close[1])
        alertMsg += s.msg
if alertMsg != ""
    alert(alertMsg, alert.freq_once_per_bar_close)

// ---------------------------------------------------------------- table
var int firstT = time
f_tsz() =>
    tblTxt == T_TI ? size.tiny : tblTxt == T_NO ? size.normal : size.small

f_tpos() =>
    tblPos == P_BR ? position.bottom_right : tblPos == P_BL ? position.bottom_left : tblPos == P_TL ? position.top_left : tblPos == P_MR ? position.middle_right : position.top_right

f_tfs(string tf) =>
    tf == "D" or tf == "1D" ? "D1" : tf == "240" ? "H4" : tf == "60" ? "H1" : tf == "15" ? "M15" : tf == "5" ? "M5" : tf == "1" ? "M1" : tf

var table T = na
if barstate.islast and showTbl
    if not na(T)
        T.delete()
    int nRow = 0
    for s in S
        if s.sel
            nRow += 1
    T := table.new(f_tpos(), 12, nRow + 3, bgcolor = color.new(#131722, 10), border_color = color.new(#434651, 0), border_width = 1, frame_color = color.new(#434651, 0), frame_width = 1)
    color hd = color.new(#2A2E39, 0)
    color tx = color.new(#D1D4DC, 0)
    T.cell(0, 0, "FRACTAL BREAKOUT GRID · " + syminfo.ticker + " · chart " + timeframe.period + " · trades since " + str.format_time(math.max(statsFrom, firstT), "yyyy-MM-dd", syminfo.timezone) + " · costs " + str.tostring(costIn) + " per trade", text_color = tx, bgcolor = hd, text_size = f_tsz(), text_halign = text.align_left)
    T.merge_cells(0, 0, 11, 0)
    array<string> H  = array.from("#", "TF", "R / L", "Trades", "Win %", "Net %", "Net R", "PF", "Max DD R", "SL in a row", "TP · SL · BE · SALV", "Now")
    array<string> HT = array.from("Strategy number (its colour on the chart).", "Fractal timeframe of the swing highs.", "Right / Left candles of the swing high.", "Closed trades counted (opened at or after the start date, within the loaded history).", "Trades that closed with a profit after costs. BE and salvage exits close at the entry, so the costs make them small losses.", "Sum of the trades' % results after costs (the same money in every trade).", "Sum of the trades' results in R after costs (R = 1 x the trade's SL: the same risk in every trade).", "Profit factor: R won / R lost.", "Largest fall of the running R total from its high.", "Most stop-loss exits in a row (BE and salvage exits are not counted; a TP resets it).", "Exits by reason: take profit, stop loss, break-even stop after the BE trigger, break-even exit after the salvage trigger.", "Now: open trade (entry, % from the entry), waiting buy stop, or waiting for the next swing high.")
    for [c, h] in H
        T.cell(c, 1, h, text_color = tx, bgcolor = hd, text_size = f_tsz(), tooltip = HT.get(c))
    int   row  = 2
    int   tN   = 0
    float tPct = 0.0
    float tR   = 0.0
    for s in S
        if s.sel
            string now = not s.ok ? "needs a chart of " + f_tfs(s.tf) + " or lower" : s.pos ? "LONG " + f_px(s.F) + " · " + f_sgn((close - s.F) / s.F * 100.0, "0.00") + "%" : s.lvlOn ? "BUY STOP " + f_px(s.E) : "waiting for a swing high"
            color  nc  = not s.ok ? color.new(#787B86, 0) : s.pos ? (close >= s.F ? C_TP : C_SL) : tx
            float  pf  = s.gl > 0 ? s.gw / s.gl : na
            T.cell(0, row, str.tostring(s.id), text_color = color.white, bgcolor = s.col, text_size = f_tsz())
            T.cell(1, row, f_tfs(s.tf), text_color = tx, text_size = f_tsz())
            T.cell(2, row, str.tostring(s.r) + " / " + str.tostring(s.l), text_color = tx, text_size = f_tsz())
            T.cell(3, row, str.tostring(s.n), text_color = tx, text_size = f_tsz())
            T.cell(4, row, s.n > 0 ? f_num(s.nW * 100.0 / s.n, "0.0") : "-", text_color = tx, text_size = f_tsz())
            T.cell(5, row, f_sgn(s.sumPct, "0.00"), text_color = s.sumPct >= 0 ? C_TP : C_SL, text_size = f_tsz())
            T.cell(6, row, f_sgn(s.sumR, "0.0"), text_color = s.sumR >= 0 ? C_TP : C_SL, text_size = f_tsz())
            T.cell(7, row, na(pf) ? (s.n > 0 ? "all wins" : "-") : f_num(pf, "0.00"), text_color = tx, text_size = f_tsz())
            T.cell(8, row, f_num(s.dd, "0.0"), text_color = tx, text_size = f_tsz())
            T.cell(9, row, str.tostring(s.mst), text_color = tx, text_size = f_tsz())
            T.cell(10, row, str.tostring(s.nTP) + " · " + str.tostring(s.nSL) + " · " + str.tostring(s.nBE) + " · " + str.tostring(s.nSV), text_color = tx, text_size = f_tsz())
            T.cell(11, row, now, text_color = nc, text_size = f_tsz(), text_halign = text.align_left)
            tN   += s.n
            tPct += s.sumPct
            tR   += s.sumR
            row  += 1
    T.cell(0, row, "ALL", text_color = tx, bgcolor = hd, text_size = f_tsz())
    T.cell(3, row, str.tostring(tN), text_color = tx, bgcolor = hd, text_size = f_tsz())
    T.cell(5, row, f_sgn(tPct, "0.00"), text_color = tPct >= 0 ? C_TP : C_SL, bgcolor = hd, text_size = f_tsz())
    T.cell(6, row, f_sgn(tR, "0.0"), text_color = tR >= 0 ? C_TP : C_SL, bgcolor = hd, text_size = f_tsz())
    T.cell(11, row, "Net % and R after costs; R = 1 x the trade's SL", text_color = tx, bgcolor = hd, text_size = f_tsz(), text_halign = text.align_left)
'''


def build(strats):
    blocks = '\n'.join(block(i + 1, p) for i, p in enumerate(strats))
    sec = '\n'.join('[ph%d, pt%d] = request.security(syminfo.tickerid, f_fits(s%dTf) ? s%dTf : timeframe.period, f_piv(s%dL, s%dR), lookahead = barmerge.lookahead_on)' % (i, i, i, i, i, i) for i in range(1, 12))
    new = '\n'.join('    S.push(Strat.new(%d, f_run(%d, s%dOn), f_run(%d, s%dOn) and f_fits(s%dTf), s%dTf, s%dR, s%dL, s%dOff, s%dSl, s%dTp, s%dBe, s%dSv, s%dCol))' % ((i,) * 15) for i in range(1, 12))
    body = BODY.replace('{SEC}', sec).replace('{NEW}', new).replace('{PHS}', ', '.join('ph%d' % i for i in range(1, 12))).replace('{PTS}', ', '.join('pt%d' % i for i in range(1, 12)))
    return HEAD + blocks + body


if __name__ == '__main__':
    T9 = [('D1', 3, 25, -0.14, 3.00, 0.75, 0.45, 0.80), ('D1', 3, 15, -0.085, 0.50, 2.00, 0.25, 0.80), ('D1', 2, 7, -0.065, 0.30, 1.65, 0.20, 0.50),
          ('H4', 8, 12, -0.025, 0.44, 3.10, 0.33, 0.90), ('H1', 19, 30, -0.045, 2.00, 0.35, 0.10, 0.70), ('H1', 25, 25, -0.060, 4.20, 0.33, 0.15, 0.80),
          ('H1', 23, 25, -0.055, 0.87, 0.56, 0.13, 1.10), ('H1', 20, 25, -0.060, 0.68, 0.43, 0.10, 0.70), ('H1', 5, 5, -0.080, 2.00, 0.70, 0.10, 1.00)]
    st = T9 + [tuple(x) for x in STRATS] if STRATS else T9 + [('M5', 3, 12, -0.03, 0.3, 0.3, 0.1, 0.0), ('M15', 3, 12, -0.03, 0.3, 0.3, 0.1, 0.0)]
    open(sys.argv[1], 'w', encoding='utf8').write(build(st))
    print('wrote', sys.argv[1], 'strategies', len(st))
