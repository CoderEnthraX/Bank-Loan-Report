"""v6.1: the Auction Retest + VWAP Orderflow Sniper EA from safe/AuctionRetestEA.mq5 (v5.40, not changed) -> out/AuctionRetestSniperEA.mq5
(setups: VWAP retest / Sniper / both one at a time / both true grid = two legs, magic and magic + 1; classwrap.py). Run: python3 -I build_sn_ea.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sn_ea_parts as P
import classwrap as W
SRC = os.path.join(HERE, 'safe', 'AuctionRetestEA.mq5')
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)


def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:120])
    return s.replace(a, b)


def patch(s):
    s = rep(s, 'input group "SIGNAL MODEL (same as the indicator)"\n', P.INPUTS + 'input group "SIGNAL MODEL (same as the indicator)"\n')
    i = s.index('int      trSkip = 0;'); j = s.index('\n', i) + 1
    s = s[:j] + P.GLOBALS + s[j:]
    s = rep(s, '//=== ENGINE: one CLOSED bar', P.FUNCS + '//=== ENGINE: one CLOSED bar')
    s = rep(s, 'bool touched = gpEntryMode == ENTRY_MARKET ? true :', 'bool touched = gpEntryMode == ENTRY_MARKET || trMkt ? true :')
    s = rep(s, '   // 3. arm a new setup on the closed displacement candle\n',
            '   if(gSrcO) SnBar(s, t, o, h, l, c, vwap, vwSd, newAnchor); else snSig = 0;   // v6.1: the Sniper on this bar\n   // 3. arm a new setup on the closed displacement candle\n')
    s = rep(s, '   if(canArm && (bullDisp || bearDisp) && !keepArm)\n', '   bool vArmed = false;\n   if(gSrcV && canArm && (bullDisp || bearDisp) && !keepArm)\n')
    s = rep(s, 'trRisk = risk; trHalf = half; trGhost = ghost;\n', 'trRisk = risk; trHalf = half; trGhost = ghost; trMkt = false; trSrc = 1; vArmed = true;\n')
    s = rep(s, '         if(!ghost) { evArm = true; evArmL = isL; }\n      }\n   }\n', '         if(!ghost) { evArm = true; evArmL = isL; }\n      }\n   }\n' + P.ARM)
    s = rep(s, 'trSkip = 0; lastRes = "-";', 'trSkip = 0; trMkt = false; trSrc = 0; SnReset(); lastRes = "-";')
    s = rep(s, '   PresetApply();                                        // v4.8: the preset\'s values (or the inputs) before anything uses them\n',
            '   PresetApply();                                        // v4.8: the preset\'s values (or the inputs) before anything uses them\n'
            '   gSrcV = InpSetups == SET_GRID ? gLeg == 0 : InpSetups != SET_SN;   // v6.1: the setups this engine arms\n'
            '   gSrcO = InpSetups == SET_GRID ? gLeg == 1 : InpSetups != SET_VWAP;\n')
    i = s.index('   if(InpSpread < 0 || InpCommLot < 0)'); j = s.index('\n', i) + 1
    s = s[:j] + P.CHECKS + s[j:]
    s = rep(s, '   else if(gpEntryMode == ENTRY_MARKET)\n', '   else if(gpEntryMode == ENTRY_MARKET || trMkt)        // v6.1: a Sniper setup at its signal close enters at market\n')
    s = rep(s, '   if(gpEntryMode == ENTRY_MARKET) return HgMarket(v);', '   if(gpEntryMode == ENTRY_MARKET || trMkt) return HgMarket(v);')
    s = rep(s, '#property version   "5.40"', '#property version   "6.10"')
    h0 = '//| Drawdown cut, Cooling-off and the combinations C1 - C5.          |\n'
    h1 = ('//| v6.1: VWAP ORDERFLOW SNIPER setup: absorption (heavy volume that |\n'
          '//| fails to move the price) near the VWAP / band #1 arms a setup;   |\n'
          '//| the next aggressive candle (buy / sell volume ratio, full body)  |\n'
          '//| on the right side of the VWAP is the signal. Delta from the M1   |\n'
          '//| candles inside each bar (or a candle estimate).                  |\n'
          '//| SETUPS: VWAP retest / Sniper / both one trade at a time / both   |\n'
          '//| true grid (hedging account: each setup its own trade, money      |\n'
          '//| management and magic number; Sniper = magic + 1).                |\n')
    s = rep(s, h0, h0 + h1)
    s = rep(s, '#property description "VWAP displacement + retest EA (same engine as the TradingView indicator/strategy) with money management."',
            '#property description "VWAP retest and VWAP Orderflow Sniper EA: one trade at a time, or the true grid (each setup its own trade and magic, hedging account)."')
    s = rep(s, '//| AuctionRetestEA.mq5                                              |', '//| AuctionRetestSniperEA.mq5 (v6.1, from AuctionRetestEA.mq5 v5.40) |')
    s = rep(s, '   TblAdd("STATE", gStateTxt, white,', '   TblAdd("STATE", gStateTxt + (has && trSrc == 2 ? " (Sniper)" : has && trSrc == 1 && gSrcO ? " (VWAP retest)" : ""), white,')
    s = rep(s, 'TblAdd("AUCTION RETEST", "EA v5.4", white,',
            'TblAdd(InpSetups == SET_GRID ? (gLeg == 0 ? "GRID LEG 1: VWAP RETEST" : "GRID LEG 2: SNIPER") : "AUCTION RETEST + SNIPER", "EA v6.1 | " + '
            '(InpSetups == SET_VWAP ? "VWAP retest only" : InpSetups == SET_SN ? "Sniper only" : InpSetups == SET_ONE ? "both, one trade at a time" : "true grid, magic " + IntegerToString(InpMagic)), white,')
    return s


def grid(s):
    s = rep(s, '   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;\n',
            '   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;\n'
            '   if(gLeg == 1) right = !right;                        // v6.1 true grid: the Sniper leg\'s table on the other side\n')
    s = rep(s, '   OtherEAs();\n', '   if(gLeg == 0) OtherEAs();\n')
    a = s.index('//--- globals ---')
    w = W.wrap(s[:a] + W.leg_text(s[a:]), '//--- globals ---')
    w = rep(w, 'int CLeg::Init()\n{\n', 'int CLeg::Init()\n{\n   gMagic = InpMagic + gLeg; gPfx = gLeg == 0 ? "ARM_" : "ARN_";   // v6.1: the leg\'s magic number and chart objects\n')
    for h in ('void CLeg::Deinit(const int reason)\n{\n', 'void CLeg::Tick()\n{\n',
              'void CLeg::ChartEvt(const int id, const long &lparam, const double &dparam, const string &sparam)\n{\n'):
        w = rep(w, h, h + '   trade.SetExpertMagicNumber(gMagic);                  // v6.1: every order of this call is the leg\'s\n')
    i = w.rindex('//+------------------------------------------------------------------+')
    tail = W.TAIL.replace('the VWAP leg and the order block leg', 'the VWAP retest leg and the Sniper leg').replace('leg 1 (the order block setup, magic + 1)', 'leg 1 (the Sniper setup, magic + 1)')
    tail = tail.replace('"True grid: the VWAP leg trades with magic ", IntegerToString(gEA0.gMagic), ", the order block leg with magic "', '"True grid: the VWAP retest leg trades with magic ", IntegerToString(gEA0.gMagic), ", the Sniper leg with magic "')
    tail = tail.replace('v6.0 the event handlers', 'v6.1 the event handlers')
    w = w[:i].rstrip() + '\n' + tail
    w = w.replace('(the grid runs leg 0 = VWAP and leg 1 = order block)', '(the grid runs leg 0 = VWAP retest and leg 1 = Sniper)')
    assert 'order block' not in w.lower(), [l for l in w.split('\n') if 'order block' in l.lower()][:5]
    return w


if __name__ == '__main__':
    g = grid(patch(open(SRC, encoding='utf8').read()))
    open(os.path.join(OUT, 'AuctionRetestSniperEA.mq5'), 'w', encoding='utf8').write(g)
    print('written', len(g.split('\n')))
