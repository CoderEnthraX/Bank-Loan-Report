"""v4.0 EA: the TradingView strategy's v4.0 defaults (the user's settings) + FxPro server clock + a Spread input for the costs
(sizing, earn-back, Crooks TP1-rule distances) so lots and target levels equal TradingView's. Every replacement must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
W = len('//| v3.9: Crooks C rule after N losing recovery trades in a row:     |')
def hl(t):
    line = '//| ' + t
    assert len(line) <= W - 1, t
    return line.ljust(W - 1) + '|'
hdr_old = ('//| v3.9: Crooks C rule after N losing recovery trades in a row:     |\n'
           '//| forget the loss, a % of it, wait for M wins, or skip D days.     |\n')
hdr_new = hdr_old + '\n'.join(hl(t) for t in (
    'v4.0: defaults = the TradingView strategy\'s v4.0 defaults (gold,',
    'FxPro): Tue-Thu 06:00-23:00 IST in the Asia / London / New York',
    'kill zones, exit TP1, Crooks C, news 17:45-18:15 IST, force-close',
    '23:55, server clock EU summer time, max 10 fills, half-stop cap.',
    'New Spread input: the costs (sizing, earn-back) use 0.16 like',
    'TradingView, so lots and target levels match it (0 = live).')) + '\n'
REPS = [
    (hdr_old, hdr_new),
    ('#property version   "3.90"', '#property version   "4.00"'),
    ('TblAdd("AUCTION RETEST", "EA v3.9"', 'TblAdd("AUCTION RETEST", "EA v4.0"'),
    # engine inputs (same defaults as the shared Pine inputs)
    ('input bool   InpHalfCap      = false;', 'input bool   InpHalfCap      = true; '),
    ('input int    InpMaxFills     = 5;     // Max fills per day', 'input int    InpMaxFills     = 10;    // Max fills per day'),
    ('input double InpEntryPct     = 50.0;', 'input double InpEntryPct     = 25.0;'),
    ('input ENUM_EXIT_AT InpExitAt = EXIT_TP4;', 'input ENUM_EXIT_AT InpExitAt = EXIT_TP1;'),
    ('input double InpMv3R  = 1.0;   //   ...to (R)', 'input double InpMv3R  = 0.0;   //   ...to (R)'),
    ('input double InpNoChaseSig = 2.4;', 'input double InpNoChaseSig = 2.0;'),
    ('input double InpChopMax    = 12.0;', 'input double InpChopMax    = 13.5;'),
    ('input ENUM_SRV_TZ InpServerTz = SRV_NYCLOSE; // Broker server clock', 'input ENUM_SRV_TZ InpServerTz = SRV_EET;     // Broker server clock'),
    ('input bool   InpDayOn     = false; // Trade only on the ticked days', 'input bool   InpDayOn     = true;  // Trade only on the ticked days'),
    ('input bool   InpMon       = true;  //   Monday', 'input bool   InpMon       = false; //   Monday'),
    ('input bool   InpFri       = true;  //   Friday', 'input bool   InpFri       = false; //   Friday'),
    ('input bool   InpSat       = true;  //   Saturday', 'input bool   InpSat       = false; //   Saturday'),
    ('input bool   InpSun       = true;  //   Sunday', 'input bool   InpSun       = false; //   Sunday'),
    ('input bool   InpHoursOn   = false; // Trade only between', 'input bool   InpHoursOn   = true;  // Trade only between'),
    ('input bool   InpKzOn      = false; // Trade only in kill zones', 'input bool   InpKzOn      = true;  // Trade only in kill zones'),
    ('input bool   InpKzLc      = true;  //   London close', 'input bool   InpKzLc      = false; //   London close'),
    # execution inputs (same defaults as the strategy)
    ('input double InpHardCap  = 500.0;  // Hard cap amount', 'input double InpHardCap  = 250.0;  // Hard cap amount'),
    ('input ENUM_CAP_ACTION InpCapAction = CAP_CLAMP;', 'input ENUM_CAP_ACTION InpCapAction = CAP_RESET;'),
    ('input ENUM_LOT_ROUND InpLotRound = LOTR_NEAR;', 'input ENUM_LOT_ROUND InpLotRound = LOTR_DOWN;'),
    ('input double InpCommLot  = 0.0;    // Commission per lot, round trip (sizing / earn-back)',
     'input double InpSpread   = 0.16;   // Spread for sizing and earn-back (price, like TradingView\'s Spread; 0 = the live spread)\n'
     'input double InpCommLot  = 7.0;    // Commission per lot, round trip (sizing / earn-back; FxPro gold: 7)'),
    ('input bool   InpEarnBack = false;', 'input bool   InpEarnBack = true; '),
    ('input int  InpLStopN  = 2;     //   N losses', 'input int  InpLStopN  = 23;    //   N losses'),
    ('input bool   InpFcOn      = false; // Force-close open trades daily at', 'input bool   InpFcOn      = true;  // Force-close open trades daily at'),
    ('input int    InpFcH       = 2;     //   hour', 'input int    InpFcH       = 23;    //   hour'),
    ('input int    InpFcM       = 0;     //   minute', 'input int    InpFcM       = 55;    //   minute'),
    ('input bool   InpWeekendOn = false;', 'input bool   InpWeekendOn = true; '),
    ('input bool   InpDNewsOn   = false; // Daily news window', 'input bool   InpDNewsOn   = true;  // Daily news window'),
    ('input int    InpDNewsH    = 18;    //   start hour', 'input int    InpDNewsH    = 17;    //   start hour'),
    ('input int    InpDNewsM    = 0;     //   start minute', 'input int    InpDNewsM    = 45;    //   start minute'),
    ('input int    InpDNewsDur  = 60;    //   length (minutes)', 'input int    InpDNewsDur  = 30;    //   length (minutes)'),
    ('input datetime InpN1T  = D\'2026.01.01 18:00\';', 'input datetime InpN1T  = D\'2026.01.01 23:30\';'),
    ('input datetime InpN2T  = D\'2026.01.01 18:00\';', 'input datetime InpN2T  = D\'2026.01.01 23:30\';'),
    ('input datetime InpN3T  = D\'2026.01.01 18:00\';', 'input datetime InpN3T  = D\'2026.01.01 23:30\';'),
    ('input datetime InpN4T  = D\'2026.01.01 18:00\';', 'input datetime InpN4T  = D\'2026.01.01 23:30\';'),
    ('input datetime InpN5T  = D\'2026.01.01 18:00\';', 'input datetime InpN5T  = D\'2026.01.01 23:30\';'),
    ('input ENUM_REC InpRec    = REC_OFF; // Loss recovery', 'input ENUM_REC InpRec    = REC_CRC; // Loss recovery'),
    ('input int    InpCSplit   = 3;', 'input int    InpCSplit   = 2;'),
    ('input bool   InpCrkT1    = true;', 'input bool   InpCrkT1    = false;'),
    ('input ENUM_T1_STOP InpCrkT1Stop = T1S_TIGHT;', 'input ENUM_T1_STOP InpCrkT1Stop = T1S_FULL;'),
    ('input int    InpCrkPrD   = 3;', 'input int    InpCrkPrD   = 4;'),
    # the cost spread: the Spread input like TradingView (0 = the live spread); the bid-chart order shift Spr() stays live
    ('double CeilTick(double p)  { double ts = TickSize(); return NormalizeDouble(MathCeil(p / ts - 1e-6) * ts, _Digits); }\n',
     'double CeilTick(double p)  { double ts = TickSize(); return NormalizeDouble(MathCeil(p / ts - 1e-6) * ts, _Digits); }\n'
     '// spread counted as a cost (lot size, earn-back, Crooks TP1-rule distance): the Spread input like TradingView, or the live spread when it is 0\n'
     'double CostSpr() { return InpSpread > 0 ? InpSpread : MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)); }\n'),
    ('   double spr = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)), p = CrkT1P();',
     '   double spr = CostSpr(), p = CrkT1P();'),
    ('   double spr = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));\n   double per = (d + spr)',
     '   double spr = CostSpr();\n   double per = (d + spr)'),
    ('   double spr = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);\n   double perLot',
     '   double spr = CostSpr();\n   double perLot'),
    ('   double sprNow = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));\n   exCostPx',
     '   double sprNow = CostSpr();\n   exCostPx'),
    ('   if(InpTp1R > InpTp2R || InpTp2R > InpTp3R || InpTp3R > InpTp4R)',
     '   if(InpSpread < 0 || InpCommLot < 0) { Print("Spread and commission must be 0 or more."); return INIT_PARAMETERS_INCORRECT; }\n'
     '   if(InpTp1R > InpTp2R || InpTp2R > InpTp3R || InpTp3R > InpTp4R)'),
]
for old, new in REPS:
    n = s.count(old)
    assert n == 1, (n, old[:100])
    s = s.replace(old, new)
assert s.count('SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)') == 2   # CostSpr (live fallback) and Spr (bid-chart shift)
open(P, 'w', encoding='utf8').write(s)
print(len(REPS), 'replacements; lines', s.count('\n'))
