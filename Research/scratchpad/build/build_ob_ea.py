"""v6.0: the order block EA and the VWAP + order block grid EA from safe/AuctionRetestEA.mq5 (v5.40, not changed).
  ob   -> out/OrderBlockEA.mq5        (order block setup only, one engine)
  grid -> out/AuctionRetestGridEA.mq5 (setups input: VWAP / order block / both one at a time / both true grid = two legs, magic and magic + 1)
Run: python3 -I build_ob_ea.py"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ob_ea_parts as P
import classwrap as W

SRC = os.path.join(HERE, 'safe', 'AuctionRetestEA.mq5')
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)


def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:120])
    return s.replace(a, b)


def ob_patch(s, only_ob):
    s = rep(s, 'input group "SIGNAL MODEL (same as the indicator)"\n',
            P.INPUTS.replace('@@SETUPS@@', P.SETUPS_CONST if only_ob else P.SETUPS_INPUT) + 'input group "SIGNAL MODEL (same as the indicator)"\n')
    i = s.index('int      trSkip = 0;'); j = s.index('\n', i) + 1
    s = s[:j] + P.GLOBALS + s[j:]
    s = rep(s, '//=== ENGINE: one CLOSED bar', P.FUNCS + '//=== ENGINE: one CLOSED bar')
    s = rep(s, 'bool touched = gpEntryMode == ENTRY_MARKET ? true :', 'bool touched = gpEntryMode == ENTRY_MARKET || trMkt ? true :')
    s = rep(s, '   // 3. arm a new setup on the closed displacement candle\n',
            '   if(gSrcO) ObBar(s, t, o, h, l, c); else obSig = 0;   // v6.0: the order block engine on this bar\n   // 3. arm a new setup on the closed displacement candle\n')
    s = rep(s, '   if(canArm && (bullDisp || bearDisp) && !keepArm)\n', '   bool vArmed = false;\n   if(gSrcV && canArm && (bullDisp || bearDisp) && !keepArm)\n')
    s = rep(s, 'trRisk = risk; trHalf = half; trGhost = ghost;\n', 'trRisk = risk; trHalf = half; trGhost = ghost; trMkt = false; trSrc = 1; vArmed = true;\n')
    s = rep(s, '         if(!ghost) { evArm = true; evArmL = isL; }\n      }\n   }\n', '         if(!ghost) { evArm = true; evArmL = isL; }\n      }\n   }\n' + P.ARM)
    s = rep(s, 'trSkip = 0; lastRes = "-";', 'trSkip = 0; trMkt = false; trSrc = 0; ObReset(); lastRes = "-";')
    s = rep(s, '   PresetApply();                                        // v4.8: the preset\'s values (or the inputs) before anything uses them\n',
            '   PresetApply();                                        // v4.8: the preset\'s values (or the inputs) before anything uses them\n'
            '   gSrcV = InpSetups == SET_GRID ? gLeg == 0 : InpSetups != SET_OB;   // v6.0: the setups this engine arms\n'
            '   gSrcO = InpSetups == SET_GRID ? gLeg == 1 : InpSetups != SET_VWAP;\n')
    i = s.index('   if(InpSpread < 0 || InpCommLot < 0)'); j = s.index('\n', i) + 1
    s = s[:j] + P.CHECKS + s[j:]
    s = rep(s, '   else if(gpEntryMode == ENTRY_MARKET)\n', '   else if(gpEntryMode == ENTRY_MARKET || trMkt)        // v6.0: an order block setup enters at market\n')
    s = rep(s, '   if(gpEntryMode == ENTRY_MARKET) return HgMarket(v);', '   if(gpEntryMode == ENTRY_MARKET || trMkt) return HgMarket(v);')
    s = rep(s, '#property version   "5.40"', '#property version   "6.00"')
    h0 = '//| Drawdown cut, Cooling-off and the combinations C1 - C5.          |\n'
    h1 = ('//| v6.0: ORDER BLOCK setup: the last opposite candle of a higher   |\n'
          '//| timeframe (M3 - H4, built from the chart\'s bars) with a fair    |\n'
          '//| value gap within N candles; absorption in the zone (volume above |\n'
          '//| average, small body, long wick), then an aggression candle:      |\n'
          '//| market entry, stop beyond that candle or the last swing.        |\n'
          '//| SETUPS: VWAP only / order block only / both one trade at a time  |\n'
          '//| / both true grid (hedging account: each setup its own trade,     |\n'
          '//| money management and magic number; order block = magic + 1).    |\n')
    s = rep(s, h0, h0 + h1)
    if only_ob:
        s = rep(s, '#property description "VWAP displacement + retest EA (same engine as the TradingView indicator/strategy) with money management."',
                '#property description "Order block + absorption + aggression EA (same engine as the TradingView Order Block strategy) with the Auction Retest money management."')
    else:
        s = rep(s, '#property description "VWAP displacement + retest EA (same engine as the TradingView indicator/strategy) with money management."',
                '#property description "VWAP displacement + retest and order block EA: one trade at a time, or the true grid (each setup its own trade and magic, hedging account)."')
    s = rep(s, 'if(ChartSymbol(id) != _Symbol || StringFind(nm, "AuctionRetest") != 0) continue;',
            'if(ChartSymbol(id) != _Symbol || (StringFind(nm, "AuctionRetest") != 0 && StringFind(nm, "OrderBlockEA") != 0)) continue;')
    s = rep(s, '   TblAdd("STATE", gStateTxt, white,', '   TblAdd("STATE", gStateTxt + (has && trSrc == 2 ? " (order block)" : has && trSrc == 1 && gSrcO ? " (VWAP)" : ""), white,')
    if only_ob:
        s = rep(s, 'TblAdd("AUCTION RETEST", "EA v5.4", white,', 'TblAdd("ORDER BLOCK", "EA v6.0 | blocks " + ObTfText(), white,')
    else:
        s = rep(s, 'TblAdd("AUCTION RETEST", "EA v5.4", white,',
                'TblAdd(InpSetups == SET_GRID ? (gLeg == 0 ? "GRID LEG 1: VWAP" : "GRID LEG 2: ORDER BLOCK") : "AUCTION RETEST + ORDER BLOCK", "EA v6.0 | " + '
                '(InpSetups == SET_VWAP ? "VWAP only" : InpSetups == SET_OB ? "order block only" : InpSetups == SET_ONE ? "both, one trade at a time" : "true grid, magic " + IntegerToString(InpMagic)) + '
                '(gSrcO ? " | blocks " + ObTfText() : ""), white,')
    if not only_ob:                                      # a strategy preset trades the VWAP setup only (as tested)
        i = s.index(P.SETUPS_INPUT); j = s.index('\n', i) + 1
        s = s[:j] + s[j:].replace('InpSetups', 'SetupsUse()')
        s = s[:j] + 'ENUM_SETUPS SetupsUse() { return InpPreset == PRE_CUSTOM ? InpSetups : SET_VWAP; }   // a strategy preset trades the VWAP setup only\n' + s[j:]
    return s


def grid(s):
    s = rep(s, '   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;\n',
            '   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;\n'
            '   if(gLeg == 1) right = !right;                        // v6.0 true grid: the order block leg\'s table on the other side\n')
    s = rep(s, '   OtherEAs();\n', '   if(gLeg == 0) OtherEAs();\n')
    a = s.index('//--- globals ---')
    pre = s[:a]
    reg = W.leg_text(s[a:])
    w = W.wrap(pre + reg, '//--- globals ---')
    w = rep(w, 'int CLeg::Init()\n{\n', 'int CLeg::Init()\n{\n   gMagic = InpMagic + gLeg; gPfx = gLeg == 0 ? "ARM_" : "ARN_";   // v6.0: the leg\'s magic number and chart objects\n')
    for h in ('void CLeg::Deinit(const int reason)\n{\n', 'void CLeg::Tick()\n{\n',
              'void CLeg::ChartEvt(const int id, const long &lparam, const double &dparam, const string &sparam)\n{\n'):
        w = rep(w, h, h + '   trade.SetExpertMagicNumber(gMagic);                  // v6.0: every order of this call is the leg\'s\n')
    i = w.rindex('//+------------------------------------------------------------------+')
    return w[:i].rstrip() + '\n' + W.TAIL.replace('gGridOn = InpSetups == SET_GRID;', 'gGridOn = SetupsUse() == SET_GRID;')


def main():
    src = open(SRC, encoding='utf8').read()
    ob = ob_patch(src, True)
    ob = rep(ob, '//| AuctionRetestEA.mq5                                              |', '//| OrderBlockEA.mq5 (v6.0, built from AuctionRetestEA.mq5 v5.40)   |')
    open(os.path.join(OUT, 'OrderBlockEA.mq5'), 'w', encoding='utf8').write(ob)
    gr = ob_patch(src, False)
    gr = rep(gr, '//| AuctionRetestEA.mq5                                              |', '//| AuctionRetestGridEA.mq5 (v6.0, from AuctionRetestEA.mq5 v5.40)  |')
    open(os.path.join(OUT, 'AuctionRetestGridEA_flat.mq5'), 'w', encoding='utf8').write(gr)
    g2 = grid(gr)
    open(os.path.join(OUT, 'AuctionRetestGridEA.mq5'), 'w', encoding='utf8').write(g2)
    print('grid', len(g2.split('\n')))
    print('written', len(ob.split('\n')), len(gr.split('\n')))


if __name__ == '__main__':
    main()
