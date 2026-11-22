"""v6.1 TradingView: Auction Retest + VWAP Orderflow Sniper strategy from TradingView/Auction_Retest_Strategy.pine (v5.4, not changed).
  out/Auction_Retest_Sniper_Strategy.pine  setups: VWAP retest only / Sniper only / both one at a time / both true grid (same direction only)
The grid is grid_pine.py (slot 0 = VWAP retest, slot 1 = Sniper). Run: python3 -I build_sn_pine.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sn_pine_parts as P
import grid_pine as G
SRC = '/home/user/Bank-Loan-Report/TradingView/Auction_Retest_Strategy.pine'
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)


def rep(s, a, b, n=1):
    c = s.count(a)
    assert c == n, (c, a[:150])
    return s.replace(a, b)


def base():
    s = open(SRC, encoding='utf8').read()
    s = rep(s, 'GRP_M = "SIGNAL MODEL"\n', P.INPUTS + 'GRP_M = "SIGNAL MODEL"\n')
    s = rep(s, '// ── 1. manage the live trade: stop first, then the final target, else stop moves (from the next bar) ──\n',
            P.ENGINE + '// ── 1. manage the live trade: stop first, then the final target, else stop moves (from the next bar) ──\n')
    s = rep(s, '    bool touched = entryMode == E_MARKET ? true :', '    bool touched = (trSrc != 2 and entryMode == E_MARKET) or trMkt ? true :')
    s = rep(s, 'bool keepArm = rearmMode == REARM_KEEP and ((st == 1 and bullDisp) or (st == -1 and bearDisp))\nif canArm and (bullDisp or bearDisp) and not keepArm\n',
            'bool keepArm = rearmMode == REARM_KEEP and ((st == 1 and bullDisp) or (st == -1 and bearDisp))\n'
            'bool srcV    = gridOn ? curSlot == 0 : setupMode != S_SN     // v6.1: the setups this pass arms (srcO = the Sniper)\n'
            'bool srcO    = gridOn ? curSlot == 1 : setupMode != S_VWAP\n'
            'bool vArmed  = false\n'
            'if srcV and canArm and (bullDisp or bearDisp) and not keepArm\n')
    s = rep(s, '        trGhost := ghost\n', '        trGhost := ghost\n        trMkt   := false\n        trSrc   := 1\n        vArmed  := true\n')
    s = rep(s, '        if not ghost\n            evArm  := true\n            evArmL := isL\n// <<< ENGINE END\n',
            '        if not ghost\n            evArm  := true\n            evArmL := isL\n' + P.ARM + '// <<< ENGINE END\n')
    s = rep(s, 'st == 1 ? "BUY LIMIT ARMED" : st == -1 ? "SELL LIMIT ARMED"', 'st == 1 ? (trMkt ? "BUY AT MARKET (NEXT BAR)" : "BUY LIMIT ARMED") : st == -1 ? (trMkt ? "SELL AT MARKET (NEXT BAR)" : "SELL LIMIT ARMED")')
    s = rep(s, '        if entryMode == E_MARKET\n            strategy.entry(', '        if (trSrc != 2 and entryMode == E_MARKET) or trMkt      // v6.1: Entry Price = Market is for the VWAP setup; a Sniper setup at its signal close enters at market\n            strategy.entry(')
    s = rep(s, 'strategy("Auction Retest Strategy [VWAP Displacement + Retest]", shorttitle = "ARS",',
            'strategy("Auction Retest + VWAP Orderflow Sniper Strategy [Grid]", shorttitle = "ARSN",')
    s = rep(s, 'pyramiding = 0,', 'pyramiding = 2, close_entries_rule = "ANY",')
    s = rep(s, 'f_row(mon, 1, "STATE", stTxt + exTxt, white)', 'f_row(mon, 1, "STATE", stTxt + exTxt + (st != 0 and not trGhost and setupMode == S_ONE ? (trSrc == 2 ? " (Sniper)" : " (VWAP retest)") : ""), white)')
    s = rep(s, '    table.cell(mon, 0, 0, "AUCTION RETEST",', '    table.cell(mon, 0, 0, setupMode == S_VWAP ? "AUCTION RETEST" : setupMode == S_SN ? "VWAP ORDERFLOW SNIPER" : gridOn ? "GRID: VWAP RETEST + SNIPER" : "VWAP RETEST + SNIPER",')
    return s


if __name__ == '__main__':
    g = G.grid(base())
    g = rep(g, '"ORDER BLOCK SLOT"', '"SNIPER SLOT"')
    g = g.replace('// ── v6.0 true grid: slot 1 (order block) keeps', '// ── v6.1 true grid: slot 1 (Sniper) keeps').replace('1 = the order block setup (true grid)', '1 = the Sniper setup (true grid)')
    g = g.replace("this bar's closed trades and open position of each slot (true grid: slot 1's entries are L2 / S2)", "this bar's closed trades and open position of each slot (true grid: slot 1 = the Sniper, entries L2 / S2)")
    assert 'order block' not in g.lower(), [l for l in g.split('\n') if 'order block' in l.lower()][:5]
    open(os.path.join(OUT, 'Auction_Retest_Sniper_Strategy.pine'), 'w', encoding='utf8').write(g)
    print('written', len(g.split('\n')))
