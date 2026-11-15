"""Generator of FractalBreakoutGridEA.mq5 (MetaTrader 5 version of the TradingView Fractal Breakout Grid strategy).
The trade logic is the per-candle model of pine_twin2.Strat (the Python twin of the Pine code), run on 1-minute bars built from the
ticks: the first tick of a minute is the bar's open, every later tick is a move along the path. Usage: build_ea.py OUT.mq5"""
import sys, json

S12 = [  # (TF, right, left, offset %, SL %, TP %, BE %, salvage %): strategies 1-9 (the user's table), 10-12 (picked on gold)
    ('D1', 3, 25, -0.14, 3.00, 0.75, 0.45, 0.80), ('D1', 3, 15, -0.085, 0.50, 2.00, 0.25, 0.80), ('D1', 2, 7, -0.065, 0.30, 1.65, 0.20, 0.50),
    ('H4', 8, 12, -0.025, 0.44, 3.10, 0.33, 0.90), ('H1', 19, 30, -0.045, 2.00, 0.35, 0.10, 0.70), ('H1', 25, 25, -0.060, 4.20, 0.33, 0.15, 0.80),
    ('H1', 23, 25, -0.055, 0.87, 0.56, 0.13, 1.10), ('H1', 20, 25, -0.060, 0.68, 0.43, 0.10, 0.70), ('H1', 5, 5, -0.080, 2.00, 0.70, 0.10, 1.00),
    ('M5', 30, 65, -0.05, 1.0, 1.0, 0.2, 0.0), ('M15', 20, 40, -0.01, 1.0, 3.0, 0.2, 0.1), ('M1', 45, 200, -0.05, 0.75, 3.0, 0.2, 0.0)]
TFC = {'D1': 'PERIOD_D1', 'H4': 'PERIOD_H4', 'H1': 'PERIOD_H1', 'M15': 'PERIOD_M15', 'M5': 'PERIOD_M5', 'M1': 'PERIOD_M1'}

HEAD = r'''//+------------------------------------------------------------------+
//| FractalBreakoutGridEA.mq5                                        |
//| MetaTrader 5 version of the TradingView "Fractal Breakout Grid"  |
//| strategy: 12 long breakout strategies on swing highs.            |
//|                                                                  |
//| THE RULES (the same as the TradingView indicator and strategy):  |
//|  - Every strategy finds swing highs on its own timeframe (broker |
//|    candles): a candle whose high is strictly above the Left      |
//|    candles before it and the Right candles after it.             |
//|  - When the last Right candle closes, a buy stop waits at the    |
//|    swing high x (1 + offset %), replacing the older one.         |
//|  - A trade opens when the price (bid) rises through it; one      |
//|    trade at a time per strategy; either way that buy stop is     |
//|    used up.                                                      |
//|  - SL % and TP % from the fill. BE trigger: the SL moves to the  |
//|    entry. Salvage trigger: the TP moves to the entry. Only the   |
//|    first of the two happens; 0 = off.                            |
//|                                                                  |
//| ON EVERY TICK: the EA moves the SL / TP the moment the price     |
//| touches a trigger (TradingView's Strategy Tester can only act    |
//| at a candle close). The rules run on 1-minute bars of the ticks, |
//| as in the research, whatever the chart's timeframe: all 12       |
//| strategies run on any chart. The broker always holds the SL and  |
//| TP. Each strategy has its own magic number (base + its number)   |
//| and its own position: a HEDGING account is needed.              |
//|                                                                  |
//| MONEY: every strategy is its own account (start balance), sized  |
//| by the position size (Fixed $ risk / Fixed lots / % of equity)   |
//| and one of the 28 loss recovery rules, with the profit ladder,   |
//| the hard cap and the leverage limit. Each trade's real result    |
//| (its deals: profit, commission, swap) is booked.                 |
//|                                                                  |
//| RESTART MEMORY: the state is kept in MT5 global variables. After |
//| a restart the missed minutes are caught up: the buy stops follow |
//| the rules, no new trade opens for them, and an open trade is     |
//| managed as the rules say (a missed exit closes it at once).      |
//+------------------------------------------------------------------+
#property copyright "Fractal Breakout Grid"
#property version   "1.00"
#property description "12 long breakout strategies on swing highs (Fractal Breakout Grid), stops moved on every tick, money management."
#include <Trade/Trade.mqh>

enum ENUM_RUN { RUN_ALL = 0,     // All strategies
                RUN_TICKED = 1,  // Ticked strategies
                RUN_ONE = 2 };   // One strategy (the number below)
enum ENUM_ENTRY { ENT_STOP = 0,  // Buy stop: the price rises through it (as tested)
                  ENT_CLOSE = 1 }; // A 1-minute candle closes at or above it
enum ENUM_SIZE { PSZ_USD = 0,    // Fixed $ risk (Base risk per trade)
                 PSZ_LOT = 1,    // Fixed lots (Base lots)
                 PSZ_PCT = 2 };  // % of equity at risk (Risk % of equity)
enum ENUM_CAP { CAP_CLAMP = 0,   // Clamp risk to the cap
                CAP_STOP = 1,    // Stop trading
                CAP_RESET = 2 }; // Start again from the base risk
enum ENUM_REC { REC_OFF = 0,     // Off
                REC_ALL = 1,     // Recover all losses on the next trade
                REC_SPLIT = 2,   // Recover losses over N trades
                REC_PART = 3,    // Recover a % of losses per trade
                REC_MART = 4,    // Martingale (multiply after each loss)
                REC_EXACT = 5,   // Exact recovery at final TP
                REC_STEP = 6,    // Step-up (+$ per loss in a row)
                REC_FIB = 7,     // Fibonacci
                REC_DALE = 8,    // D'Alembert
                REC_C = 9,       // Rule C: carry the losses
                REC_CS = 10,     // Rule C split
                REC_LAB = 11,    // Labouchere
                REC_GMART = 12,  // Grand Martingale
                REC_PAR = 13,    // Paroli
                REC_RDALE = 14,  // Reverse D'Alembert
                REC_DELAY = 15,  // Delayed recovery
                REC_EQPCT = 16,  // % of equity
                REC_OSC = 17,    // Oscar's Grind
                REC_CRA = 18,    // Crooks A (base, base, then recovery every 2nd trade)
                REC_CRB = 19,    // Crooks B (Crooks A, the loss split over trades)
                REC_CRC = 20,    // Crooks C (base until a win, then one recovery trade)
                REC_CRD = 21,    // Crooks D (base, base, recovery: every 3rd trade)
                REC_CRE = 22,    // Crooks E (Crooks C, the small lot while a loss waits)
                REC_CRF = 23,    // Crooks F (Crooks C, recovery at most K x base)
                REC_CRG = 24,    // Crooks G (Crooks C, loss to win back at most X x base)
                REC_CRH = 25,    // Crooks H (Crooks C, recovery at most % of equity)
                REC_CRI = 26,    // Crooks I (Crooks E + F)
                REC_CRJ = 27 };  // Crooks J (Crooks C, recovery shrinks with the drawdown)
enum ENUM_CRK_PR { CPR_OFF = 0,   // Off (Crooks C as now)
                   CPR_FORGET = 1, // Forget the loss
                   CPR_PCT = 2,   // Each recovery trade goes for a % of the loss
                   CPR_WAIT = 3 }; // Wait for M wins in a row
enum ENUM_LADDER { LAD_OFF = 0,   // Off
                   LAD_LOW = 1,   // Low (keeps 80%, base up to 2x)
                   LAD_MED = 2,   // Medium (keeps 70%, base up to 3x)
                   LAD_HIGH = 3,  // High (keeps 60%, base up to 5x)
                   LAD_XHIGH = 4, // Extra high (keeps 50%, base up to 8x)
                   LAD_MAX = 5 }; // Max (keeps 40%, base up to 12x)
enum ENUM_SRV_TZ { SRV_NYCLOSE = 0, // GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED = 1,   // Fixed: the GMT offset below
                   SRV_EET = 2,     // GMT+2 winter / GMT+3 EU summer time (EET brokers, e.g. FxPro)
                   SRV_AUTO = 3 };  // Auto: read the broker's clock from MT5 (Strategy Tester: US summer time)
enum ENUM_TBL_POS { TBL_TOP_RIGHT = 0,    // Top right
                    TBL_TOP_LEFT = 1,     // Top left
                    TBL_BOTTOM_RIGHT = 2, // Bottom right
                    TBL_BOTTOM_LEFT = 3 }; // Bottom left

input group "GRID"
input ENUM_RUN InpRun     = RUN_ALL; // Run
input int    InpRunOne    = 11;      //   ...the one strategy (1-12)
input long   InpMagic     = 26110;   // Magic number base (strategy N uses base + N)
input double InpSpread    = 0.16;    // Spread for sizing (price; 0 = the live spread)
input double InpCommLot   = 7.0;     // Commission per lot, round trip (sizing)
'''

def strat_inputs(i, p):
    tf, r, l, off, sl, tp, be, sv = p
    return '''
input group "STRATEGY %(i)d"
input bool            InpS%(i)dOn  = true;      // On (Run = Ticked strategies)
input ENUM_TIMEFRAMES InpS%(i)dTf  = %(tf)s; // Swing-high timeframe
input int             InpS%(i)dR   = %(r)d;  // Right candles
input int             InpS%(i)dL   = %(l)d;  // Left candles
input double          InpS%(i)dOff = %(off)r;  // Buy entry offset %% (from the swing high; -0.14 = 0.14 %% below)
input double          InpS%(i)dSl  = %(sl)r;   // SL %%
input double          InpS%(i)dTp  = %(tp)r;   // TP %%
input double          InpS%(i)dBe  = %(be)r;   // BE trigger %% (0 = off)
input double          InpS%(i)dSv  = %(sv)r;   // Salvage trigger %% (0 = off)
''' % dict(i=i, tf=TFC[tf], r=r, l=l, off=off, sl=sl, tp=tp, be=be, sv=sv)

OPTS = r'''
input group "ENTRY AND EXIT OPTIONS (all off = as tested)"
input ENUM_ENTRY InpEntry = ENT_STOP; // Entry
input int    InpExpN    = 0;      // Buy stop expires after N swing-high candles (0 = never)
input int    InpMaxDay  = 0;      // Most entries per day, each strategy (0 = no limit)
input double InpTrA     = 0.0;    // Trailing stop: starts at +% from the fill
input double InpTrD     = 0.0;    // Trailing stop: distance % (0 = off)
input double InpTExitH  = 0.0;    // Close a trade after N hours (0 = off)
input bool   InpWkOn    = false;  // Close before the weekend (Friday, New York time)
input int    InpWkH     = 16;     //   ...from this hour (New York)
input bool   InpTrnOn   = false;  // Only buy above the EMA
input ENUM_TIMEFRAMES InpTrnTf = PERIOD_H4; //   ...EMA timeframe
input int    InpTrnLen  = 50;     //   ...EMA length

input group "DAYS AND HOURS (all off = as tested; YOUR time zone)"
input ENUM_SRV_TZ InpServerTz = SRV_AUTO; // Broker server clock
input double InpServerGMT = 2.0;  // Broker server time zone if fixed (GMT +h)
input double InpUserGMT   = 5.5;  // Your time zone (GMT +h; India = 5.5)
input bool   InpDayOn   = false;  // Trade only on the ticked days
input bool   InpMon     = true;   //   Monday
input bool   InpTue     = true;   //   Tuesday
input bool   InpWed     = true;   //   Wednesday
input bool   InpThu     = true;   //   Thursday
input bool   InpFri     = true;   //   Friday
input bool   InpSat     = false;  //   Saturday
input bool   InpSun     = false;  //   Sunday
input bool   InpHoursOn = false;  // Trade only between
input int    InpHourFrom = 600;   //   ...from (HHMM, your time)
input int    InpHourTo   = 2300;  //   ...to (HHMM, not included; earlier than from = over midnight)

input group "MONEY (each strategy is its own account)"
input double InpStartB   = 10000.0; // Start balance of each strategy
input ENUM_SIZE InpSizeMode = PSZ_USD; // Position size: the base trade (the loss recovery sizes every trade from it)
input double InpBaseRisk = 50.0;   // Base risk per trade (account currency; Fixed $ risk)
input double InpBaseLots = 0.01;   // Base lots (Fixed lots)
input double InpEqPct    = 1.0;    // Risk % of equity (% of equity at risk, and the % of equity rule)
input double InpLev      = 100.0;  // Leverage limit 1:N (a trade is never bigger than the balance x N)
input bool   InpCapOn    = true;   // Hard cap: max loss per trade
input double InpHardCap  = 500.0;  //   ...amount
input ENUM_CAP InpCapAction = CAP_CLAMP; //   ...if the risk would exceed the cap

input group "LOSS RECOVERY"
input ENUM_REC InpRec    = REC_CRF; // Loss recovery
input int    InpRecN     = 3;      // Recover over N trades / Delayed recovery: N
input double InpRecPct   = 50.0;   // Recover a % of losses: the %
input double InpRecMult  = 2.0;    // Martingale / Grand Martingale multiplier
input double InpRecStep  = 25.0;   // Step-up: $ per loss in a row
input int    InpCSplit   = 3;      // Split (Rule C, Crooks B)
input int    InpParN     = 3;      // Paroli: wins before reset
input int    InpDelayN   = 2;      // Delayed recovery: losses before it starts
input int    InpCrkCn    = 1;      // Crooks C - J: win the loss back over N wins
input ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C - J: after N losing recovery trades in a row
input int    InpCrkPrN   = 2;      //   ...N
input double InpCrkPrPct = 50.0;   //   ...% of the loss each recovery trade goes for
input int    InpCrkPrM   = 2;      //   ...M wins in a row to wait for
input double InpCrkELot  = 0.01;   // Crooks E / I: lot while a loss waits for a win
input double InpCrkFK    = 3.0;    // Crooks F / I: a recovery trade risks at most x base
input double InpCrkGX    = 10.0;   // Crooks G: the loss to win back is at most x base
input double InpCrkHPct  = 1.0;    // Crooks H: a recovery trade risks at most % of equity
input double InpCrkJX    = 20.0;   // Crooks J: drawdown (x base) where recovery ends
input ENUM_LADDER InpLadder = LAD_MED; // Profit ladder (Crooks F - J): risk appetite
input double InpLadT     = 1000.0; //   ...profit target before the risk goes up ($ of the strategy)

input group "DISPLAY AND MEMORY"
input bool   InpTable    = true;   // Table
input ENUM_TBL_POS InpTablePos = TBL_TOP_RIGHT; //   ...position
input int    InpTableFont = 8;     //   ...font size
input bool   InpLines    = true;   // Lines: waiting buy stops, open trades' SL and TP
input bool   InpAlerts   = false;  // Alert on entries and exits
input bool   InpPush     = false;  // Push notification on entries and exits
input bool   InpRemember = true;   // Continue after a restart (restart memory)
input int    InpWarmDays = 60;     // Warm-up: days of 1-minute history read at a fresh start
'''

CORE = r'''
//--- one strategy: settings, swing-high candles, the waiting buy stop, the trade, the money and the stats
struct Strat
{
   int      id;                  // 1 - 12
   bool     ok;                  // runs
   ENUM_TIMEFRAMES tf;
   int      r, l;
   double   off, sl, tp, be, sv;
   double   hs[];                // the last left + right + 1 highs of its timeframe (ring, by candle number)
   datetime ht[];                // their open times
   int      nC;                  // completed candles pushed (the current candle's number)
   datetime tfLast;              // live: open time of the current candle of its timeframe
   bool     lvlOn;               // a buy stop waits
   double   lvlH, E;             // the swing high, the buy stop
   datetime lvlT;                // the swing-high candle's open time (a new swing high = another time)
   int      kAct;                // the candle number where the buy stop started (expiry)
   datetime actT;                // its open time (restart memory)
   bool     armed;               // candle-close entry: a close below the buy stop came first
   bool     pos;                 // in a trade
   double   F, SLp, TPp, BEl, SVl, hi;
   bool     beOn, svOn, trOn;
   datetime eTime;
   bool     cnt;                 // booked in the money
   ulong    ticket;              // the broker position
   double   lots;
   int      dCnt, dPrev;         // entries today, the day
   bool     stopped;
   string   stopWhy;
   // money (gold/recovery.py simulate, as the Pine code)
   double   eq, pkEq, ddU, ddP, net, peakNet, recPool, carried, oscP, crL, risk, units, bR;
   int      recLosses, dUnits, parWins, rdUnits, oscU, crN, crP, crF, crWW;
   bool     crW, crWait, crNeedL, crRecT;
   double   lab[];
   // stats (real $ results)
   int      n, nW, nTP, nSL, nBE, nSV, nOth, st, mst;
   double   gw, gl, cum, pk, dd;
   double   lastUsd;
   int      lastRsn;
   int      exitDue;             // the rules exited but the broker refused the close: retried (the reason)
   double   exitPx;
};
Strat S[12];

//--- the 1-minute bar the ticks are building (live) or a replayed one
struct BarCtx
{
   datetime T;                   // open time (server)
   double   last;                // the last price (bid) of the bar so far
   double   prevC;               // the previous bar's close (0 = none)
   bool     okb, wk;             // a breakout may open a trade; the weekend close is due
   int      dno;                 // the day (your time zone)
};
BarCtx gC;
bool   gSim = false;             // test harness: no broker, the model's result is booked
bool   gNoEntry = false;         // replay (warm-up, catch-up): buy stops and exits only, no new trade
bool   gDirty = false;           // something to save in the restart memory
double gSimLog[]; int gSimN = 0; // test harness only: the closed trades (strategy, entry time, entry, exit time, exit, reason, $ risk)
double gSimContract = 100.0;     // test harness only: units per lot
CTrade trade;
// trend filter: the EMA of the trend timeframe's closes and whether the last closed candle closed above it
double   gTrE = 0; bool gTrSeed = false, gTrUp = false; datetime gTrLast = 0;

bool BrokerOpen(Strat &s);
bool BrokerClose(Strat &s, double model, double &usd);
void Note(Strat &s, string m, bool loud);
double Pt()       { return SymbolInfoDouble(_Symbol, SYMBOL_POINT); }
double TickSize() { double t = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE); return t > 0 ? t : Pt(); }
double Contract() { if(gSim) return gSimContract; double c = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE); return c > 0 ? c : 1.0; }
double LotStep()  { double s = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP); return s > 0 ? s : 0.01; }
//--- account currency per 1 unit for a price move of 1.0 (gold in a USD account: 1)
double Vpu()
{
   if(gSim) return 1.0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   return tv > 0 && ts > 0 ? tv / ts / Contract() : 1.0;
}
//--- costs of one unit, round trip, in price units: spread + commission (gold: 0.16 + 7 / 100 = 0.23, as TradingView's Costs input)
double Costs()
{
   double spr = InpSpread > 0 ? InpSpread : MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
   return spr + InpCommLot / Contract() / Vpu();
}
double NormP(double p) { double ts = TickSize(); return NormalizeDouble(MathRound(p / ts) * ts, _Digits); }

//--- settings of a strategy and a fresh account
void StratInit(Strat &s, int id, bool on, ENUM_TIMEFRAMES tf, int r, int l, double off, double sl, double tp, double be, double sv)
{
   s.id = id; s.ok = on; s.tf = tf; s.r = MathMax(1, r); s.l = MathMax(1, l); s.off = off; s.sl = sl; s.tp = tp; s.be = be; s.sv = sv;
   ArrayResize(s.hs, s.l + s.r + 1); ArrayResize(s.ht, s.l + s.r + 1); ArrayInitialize(s.hs, 0.0); ArrayInitialize(s.ht, 0);
   s.nC = 0; s.tfLast = 0;
   s.lvlOn = false; s.lvlH = 0; s.E = 0; s.lvlT = 0; s.kAct = 0; s.actT = 0; s.armed = false;
   s.pos = false; s.F = 0; s.SLp = 0; s.TPp = 0; s.BEl = 0; s.SVl = 0; s.hi = 0; s.beOn = false; s.svOn = false; s.trOn = false;
   s.eTime = 0; s.cnt = false; s.ticket = 0; s.lots = 0; s.dCnt = 0; s.dPrev = -1; s.stopped = false; s.stopWhy = "";
   s.eq = InpStartB; s.pkEq = InpStartB; s.ddU = 0; s.ddP = 0; s.net = 0; s.peakNet = 0; s.recPool = 0; s.carried = 0; s.oscP = 0; s.crL = 0;
   s.risk = 0; s.units = 0; s.bR = 0;
   s.recLosses = 0; s.dUnits = 1; s.parWins = 0; s.rdUnits = 1; s.oscU = 1; s.crN = 0; s.crP = MathMax(1, InpCrkCn); s.crF = 0; s.crWW = 0;
   s.crW = false; s.crWait = false; s.crNeedL = false; s.crRecT = false;
   ArrayResize(s.lab, 3); s.lab[0] = 1.0; s.lab[1] = 2.0; s.lab[2] = 3.0;
   s.n = 0; s.nW = 0; s.nTP = 0; s.nSL = 0; s.nBE = 0; s.nSV = 0; s.nOth = 0; s.st = 0; s.mst = 0;
   s.gw = 0; s.gl = 0; s.cum = 0; s.pk = 0; s.dd = 0; s.lastUsd = 0; s.lastRsn = 0; s.exitDue = 0; s.exitPx = 0;
}

//--- a completed candle of the strategy's timeframe (high, open time); tNow = the open time of the candle that starts now.
//--- detect: look for a swing high (off while the candles are rebuilt after a restart)
void PushTf(Strat &s, double high, datetime t, datetime tNow, bool detect)
{
   int w = s.l + s.r + 1, k = s.nC;
   s.hs[k % w] = high; s.ht[k % w] = t; s.nC++;
   if(!detect) return;
   int hb = s.nC;                                     // the number of the candle that starts now
   int p = k - s.r;                                   // the candidate: right candles after it have closed
   if(p - s.l >= 0)
   {
      double v = s.hs[p % w];
      bool ok = true;
      for(int i = 1; i <= s.l && ok; i++) if(s.hs[(p - i) % w] >= v) ok = false;
      for(int j = 1; j <= s.r && ok; j++) if(s.hs[(p + j) % w] >= v) ok = false;
      if(ok && s.ht[p % w] != s.lvlT)
      {
         s.lvlT = s.ht[p % w]; s.lvlOn = true; s.lvlH = v; s.E = v * (1.0 + s.off / 100.0); s.kAct = hb; s.actT = tNow; s.armed = false;
         Note(s, "BUY STOP " + DoubleToString(s.E, _Digits) + " (swing high " + DoubleToString(v, _Digits) + ")", false);
      }
   }
   if(s.lvlOn && InpExpN > 0 && hb - s.kAct >= InpExpN) s.lvlOn = false;
}
//--- a completed candle of the trend timeframe: its EMA (seeded with the first close) and whether it closed above it
void PushTrend(double c)
{
   double a = 2.0 / (MathMax(1, InpTrnLen) + 1.0);
   if(!gTrSeed) { gTrE = c; gTrSeed = true; } else gTrE = a * c + (1.0 - a) * gTrE;
   gTrUp = c > gTrE;
}

//--- your time and the filters of a 1-minute bar
double RuleGMT(int md, datetime server);
double SrvGMT(datetime server);
datetime UtcOf(datetime server) { return server - (datetime)MathRound(SrvGMT(server) * 3600.0); }
datetime UserOf(datetime server) { return UtcOf(server) + (datetime)MathRound(InpUserGMT * 3600.0); }
int NthSunday(int y, int mon, int k)
{
   MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = 1;
   MqlDateTime f; TimeToStruct(StructToTime(d), f);
   return 1 + (7 - f.day_of_week) % 7 + 7 * (k - 1);
}
int LastSunday(int y, int mon) { int d = NthSunday(y, mon, 1); while(d + 7 <= 31) d += 7; return d; }
datetime MkTime(int y, int mon, int day, int hr) { MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = day; d.hour = hr; return StructToTime(d); }
// New York daylight time at a UTC time: 07:00 UTC on the second Sunday of March to 06:00 UTC on the first Sunday of November
bool NySummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(d.year, 3, NthSunday(d.year, 3, 2), 7) && utc < MkTime(d.year, 11, NthSunday(d.year, 11, 1), 6); }
bool InSess(int mins)
{
   int a0 = (InpHourFrom / 100) * 60 + InpHourFrom % 100, a1 = (InpHourTo / 100) * 60 + InpHourTo % 100;
   return a0 < a1 ? (mins >= a0 && mins < a1) : (mins >= a0 || mins < a1);
}
void Filters(datetime T, bool &okb, bool &wk, int &dno)
{
   datetime utc = UtcOf(T), u = utc + (datetime)MathRound(InpUserGMT * 3600.0);
   MqlDateTime lz; TimeToStruct(u, lz);
   bool dOk = !InpDayOn || (lz.day_of_week == 1 ? InpMon : lz.day_of_week == 2 ? InpTue : lz.day_of_week == 3 ? InpWed : lz.day_of_week == 4 ? InpThu :
                            lz.day_of_week == 5 ? InpFri : lz.day_of_week == 6 ? InpSat : InpSun);
   bool hOk = !InpHoursOn || InSess(lz.hour * 60 + lz.min);
   bool tOk = !InpTrnOn || gTrUp;
   MqlDateTime ny; TimeToStruct(utc - (datetime)((NySummer(utc) ? 4 : 5) * 3600), ny);
   wk = InpWkOn && ny.day_of_week == 5 && ny.hour >= InpWkH;
   okb = dOk && hOk && tOk && !wk;
   dno = lz.year * 10000 + lz.mon * 100 + lz.day;
}

//--- money (gold/recovery.py simulate, the same as the Pine code)
bool CrkFam() { return InpRec == REC_CRC || InpRec == REC_CRE || InpRec == REC_CRF || InpRec == REC_CRG || InpRec == REC_CRH || InpRec == REC_CRI || InpRec == REC_CRJ; }
bool LadFam() { return InpRec == REC_CRF || InpRec == REC_CRG || InpRec == REC_CRH || InpRec == REC_CRI || InpRec == REC_CRJ; }
bool PrOn()   { return CrkFam() && InpCrkPr != CPR_OFF; }
void LadPar(double &lam, double &phi, double &bmx, double &gam)
{
   lam = 0.8; phi = 0.10; bmx = 2.0; gam = 0.25;
   if(InpLadder == LAD_MED)   { lam = 0.7; phi = 0.15; bmx = 3.0;  gam = 0.30; }
   if(InpLadder == LAD_HIGH)  { lam = 0.6; phi = 0.20; bmx = 5.0;  gam = 0.35; }
   if(InpLadder == LAD_XHIGH) { lam = 0.5; phi = 0.25; bmx = 8.0;  gam = 0.40; }
   if(InpLadder == LAD_MAX)   { lam = 0.4; phi = 0.30; bmx = 12.0; gam = 0.50; }
}
//--- units of the Crooks E / I lot (rounded up to the lot step)
double EUnits() { double st = LotStep(); return MathCeil(MathMax(InpCrkELot, st) / st - 1e-9) * st * Contract(); }
//--- the base trade's $ risk at a stop distance sd (price): Fixed $ risk, the Fixed lots' loss at that stop (costs included), or % of the account
double FBase(Strat &s, double sd)
{
   if(InpSizeMode == PSZ_LOT) return InpBaseLots * Contract() * (sd + Costs()) * Vpu();
   if(InpSizeMode == PSZ_PCT) return MathMax(0.0, s.eq) * InpEqPct / 100.0;
   return InpBaseRisk;
}
//--- the profit ladder at base B: on, the start guard (closed profit 0 or less), its base, the cushion above the lock
bool FLad(Strat &s, double B, bool &guard, double &lb, double &cush)
{
   bool on = InpLadder != LAD_OFF && LadFam() && s.peakNet >= InpLadT;
   double lam = 0, phi = 0, bmx = 0, gam = 0; LadPar(lam, phi, bmx, gam);
   cush = on ? MathMax(0.0, s.net - lam * s.peakNet) : 0.0;
   guard = on && s.net <= 0;
   lb = on ? B + MathMin((bmx - 1.0) * B, phi * cush) : B;
   return on;
}
//--- a Crooks C - J trade at base B (rec = a recovery trade)
double FCrk(Strat &s, double B, bool rec, double rmin, double pf, double xr)
{
   double x = rec ? MathMax(B, s.crL / s.crP * pf / xr) : B;
   if(rec)
   {
      if(InpRec == REC_CRF || InpRec == REC_CRI) x = MathMin(x, InpCrkFK * B);
      else if(InpRec == REC_CRH) x = MathMin(x, MathMax(B, s.eq * InpCrkHPct / 100.0));
      else if(InpRec == REC_CRJ) x = MathMax(B, x * MathMax(0.0, 1.0 - (s.peakNet - s.net) / (InpCrkJX * B)));
   }
   else if(s.crL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI)) x = MathMin(B, rmin);
   return x;
}
//--- the rule's risk for the next trade (before the cap and the leverage limit), whether it is a recovery trade, and Rule C split's base
double FRaw(Strat &s, double sd, bool &rec, double &baseC)
{
   double base = FBase(s, sd);
   double xr = s.tp / s.sl, rmin = EUnits() * (sd + Costs()) * Vpu();
   double add = InpRec == REC_ALL ? s.recPool : InpRec == REC_SPLIT ? s.recPool / MathMax(1, InpRecN) : InpRec == REC_PART ? s.recPool * InpRecPct / 100.0 :
                InpRec == REC_EXACT ? s.recPool / xr : InpRec == REC_STEP ? InpRecStep * s.recLosses : 0.0;
   double fa = 1.0, fb = 1.0;
   for(int k = 2; k <= MathMin(s.recLosses, 200); k++) { double t2 = fa + fb; fa = fb; fb = t2; }
   double stepBase = 0.0;
   if(s.net >= 1000) { int kk = (int)MathFloor((s.net - 1000.0) / 500.0); stepBase = (1000.0 + 500.0 * kk) / (8.0 + kk); }
   else if(s.net >= 500) stepBase = 500.0 / 5.0;
   else if(s.net >= 200) stepBase = 200.0 / 3.0;
   baseC = InpRec == REC_CS ? MathMax(base, InpCapOn ? MathMin(stepBase, InpHardCap) : stepBase) : base;
   int nl = ArraySize(s.lab);
   double labU = nl > 1 ? s.lab[0] + s.lab[nl - 1] : (nl == 1 ? s.lab[0] : 1.0);
   int oscNd = base > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((base - s.oscP) / (base * xr) - 1e-9))) : 1;
   rec = ((InpRec == REC_CRA || InpRec == REC_CRB) && s.crN >= 2 && s.crN % 2 == 0) || (CrkFam() && s.crW && s.crL > 0) || (InpRec == REC_CRD && s.crN >= 2 && (s.crN - 2) % 3 == 0);
   if(rec && PrOn() && InpCrkPr == CPR_WAIT && (s.crWait || s.crNeedL)) rec = false;
   double pf = PrOn() && InpCrkPr == CPR_PCT ? InpCrkPrPct / 100.0 : 1.0;
   double r = base + add;
   switch(InpRec)
   {
      case REC_LAB:   r = base * labU; break;
      case REC_GMART: r = base * MathPow(InpRecMult, MathMin(s.recLosses, 200)) + base * s.recLosses; break;
      case REC_PAR:   r = base * MathPow(2.0, s.parWins); break;
      case REC_RDALE: r = base * s.rdUnits; break;
      case REC_DELAY: r = s.recLosses >= InpDelayN ? base + s.recPool / MathMax(1, InpRecN) : base; break;
      case REC_EQPCT: r = s.eq * InpEqPct / 100.0; break;
      case REC_OSC:   r = base * MathMin(s.oscU, oscNd); break;
      case REC_MART:  r = base * MathPow(InpRecMult, MathMin(s.recLosses, 200)); break;
      case REC_FIB:   r = base * (s.recLosses == 0 ? 1.0 : fb); break;
      case REC_DALE:  r = base * s.dUnits; break;
      case REC_C:
      case REC_CS:    r = MathMax(baseC, s.carried / MathMax(1, InpCSplit)); break;
      case REC_CRA:   r = rec ? MathMax(base, s.crL / xr) : base; break;
      case REC_CRB:   r = rec ? MathMax(base, s.crL / MathMax(1, InpCSplit) / xr) : base; break;
      case REC_CRC:   r = rec ? MathMax(base, s.crL / s.crP * pf / xr) : base; break;
      case REC_CRD:   r = rec ? MathMax(base, s.crL / xr) : base; break;
      default:        break;
   }
   if(CrkFam())
   {
      r = FCrk(s, base, rec, rmin, pf, xr);
      bool lg = false; double lb = 0, lc = 0;
      if(FLad(s, base, lg, lb, lc))
      {
         double lam = 0, phi = 0, bmx = 0, gam = 0; LadPar(lam, phi, bmx, gam);
         r = MathMin(FCrk(s, lb, rec, rmin, pf, xr), r + gam * lc);
         if(lg) r = MathMin(base, rmin);
      }
   }
   return r;
}
//--- the next trade's $ risk at fill F, shown before it happens (no state change); -1 = the cap would stop the strategy
double FNext(Strat &s, double F)
{
   double sd = F * s.sl / 100.0, baseC = 0; bool rec = false;
   if(FBase(s, sd) <= 0) return 0;
   double r = FRaw(s, sd, rec, baseC);
   if(InpCapOn && r > InpHardCap) r = InpCapAction == CAP_STOP ? -1 : InpCapAction == CAP_RESET ? MathMin(baseC, InpHardCap) : InpHardCap;
   if(r > 0 && s.eq > 0) r = MathMin(r, s.eq * InpLev * (sd + Costs()) / F);
   return r;
}
void RecReset(Strat &s)
{
   s.recPool = 0; s.recLosses = 0; s.dUnits = 1; s.carried = 0; ArrayResize(s.lab, 3); s.lab[0] = 1.0; s.lab[1] = 2.0; s.lab[2] = 3.0;
   s.parWins = 0; s.rdUnits = 1; s.oscU = 1; s.oscP = 0; s.crL = 0; s.crN = 0; s.crRecT = false; s.crW = false; s.crP = MathMax(1, InpCrkCn);
   s.crF = 0; s.crWait = false; s.crWW = 0; s.crNeedL = false;
}
//--- sizing at an entry (the cap's start again / stop change the state): false = no trade
bool MmOpen(Strat &s, double F)
{
   double sd = F * s.sl / 100.0;
   s.bR = FBase(s, sd);
   if(s.bR <= 0) { s.risk = 0; s.units = 0; return false; }   // no base (an empty account): no trade
   bool rec = false; double baseC = 0;
   double r = FRaw(s, sd, rec, baseC);
   bool take = true;
   s.crRecT = rec;
   if(InpCapOn && r > InpHardCap)
   {
      if(InpCapAction == CAP_STOP) { s.stopped = true; s.stopWhy = "stopped by the hard cap"; take = false; }
      else if(InpCapAction == CAP_RESET) { RecReset(s); r = MathMin(baseC, InpHardCap); }
      else r = InpHardCap;
   }
   if(take && s.eq > 0) r = MathMin(r, s.eq * InpLev * (sd + Costs()) / F);
   s.risk = take ? r : 0;
   s.units = take ? r / ((sd + Costs()) * Vpu()) : 0;
   return take && s.units > 0;
}
//--- a closed trade's $ result: the rule's state after the trade
void MmBook(Strat &s, double pnl)
{
   s.eq += pnl; s.net += pnl; s.pkEq = MathMax(s.pkEq, s.eq); s.ddU = MathMax(s.ddU, s.pkEq - s.eq);
   if(s.pkEq > 0) s.ddP = MathMax(s.ddP, (s.pkEq - s.eq) / s.pkEq);
   s.peakNet = MathMax(s.peakNet, s.net);
   if(s.eq <= 0) { s.stopped = true; s.stopWhy = "account blown"; }
   bool win = pnl > 0;
   s.carried = MathMax(0.0, s.carried - pnl);
   int nl = ArraySize(s.lab);
   if(win)
   {
      s.recPool = MathMax(0.0, s.recPool - pnl); s.recLosses = s.recPool > 0 ? s.recLosses : 0;
      s.dUnits = MathMax(1, s.dUnits - 1); s.rdUnits++; s.parWins = s.parWins + 1 >= InpParN ? 0 : s.parWins + 1;
      if(nl <= 2) { ArrayResize(s.lab, 3); s.lab[0] = 1.0; s.lab[1] = 2.0; s.lab[2] = 3.0; }
      else { for(int q = 0; q < nl - 2; q++) s.lab[q] = s.lab[q + 1]; ArrayResize(s.lab, nl - 2); }
   }
   else
   {
      s.recPool += -pnl; s.recLosses++; s.dUnits++; s.rdUnits = MathMax(1, s.rdUnits - 1); s.parWins = 0;
      double used = nl > 1 ? s.lab[0] + s.lab[nl - 1] : (nl == 1 ? s.lab[0] : 1.0);
      ArrayResize(s.lab, nl + 1); s.lab[nl] = used;
   }
   s.oscP += pnl;
   if(s.oscP >= s.bR) { s.oscU = 1; s.oscP = 0; } else if(win) s.oscU++;
   bool lastPart = s.crP == 1;
   s.crL = MathMax(0.0, s.crL - pnl);
   if(InpRec == REC_CRG) { bool lg = false; double lb = 0, lc = 0; FLad(s, s.bR, lg, lb, lc); s.crL = MathMin(s.crL, InpCrkGX * lb); }
   if(s.crL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && s.crRecT))
   {
      s.crL = 0; s.crN = 0; s.crP = MathMax(1, InpCrkCn); s.crF = 0; s.crWait = false; s.crWW = 0; s.crNeedL = false;
   }
   else
   {
      s.crN++;
      s.crP = !win ? MathMax(1, InpCrkCn) : (s.crRecT ? MathMax(1, s.crP - 1) : s.crP);
      if(PrOn())
      {
         if(s.crWait)
         {
            s.crWW = win ? s.crWW + 1 : 0;
            if(s.crWW >= InpCrkPrM) { s.crWait = false; s.crWW = 0; s.crNeedL = true; }
         }
         else if(s.crNeedL && !win) s.crNeedL = false;
         if(s.crRecT && win)
         {
            s.crF = 0;
            if(InpCrkPr == CPR_PCT && lastPart) { s.crL = 0; s.crN = 0; s.crP = MathMax(1, InpCrkCn); }
         }
         else if(s.crRecT)
         {
            s.crF++;
            if(s.crF >= InpCrkPrN)
            {
               s.crF = 0;
               if(InpCrkPr == CPR_FORGET || InpCrkPr == CPR_PCT) { s.crL = 0; s.crN = 0; s.crP = MathMax(1, InpCrkCn); }
               else if(InpCrkPr == CPR_WAIT) { s.crWait = true; s.crWW = 0; s.crNeedL = false; }
            }
         }
      }
   }
   s.crW = win;
}

//--- the trade rules on one strategy (pine_twin2.Strat: openAt / closeAt / doBE / doSV / trail / up / dn / onBar)
string RsnTxt(int r) { return r == 1 ? "TP" : r == 2 ? "SL" : r == 3 ? "BE" : r == 4 ? "SALV" : r == 5 ? "TRAIL" : r == 6 ? "TIME" : r == 7 ? "WKND" : "OUT"; }
void DoBE(Strat &s) { s.beOn = true; if(s.F > s.SLp) s.SLp = s.F; gDirty = true; }
void DoSV(Strat &s) { s.svOn = true; s.TPp = s.F; gDirty = true; }
void Trail(Strat &s)
{
   if(InpTrD > 0 && s.hi >= s.F * (1.0 + InpTrA / 100.0))
   {
      double tl = s.hi * (1.0 - InpTrD / 100.0);
      if(tl > s.SLp) { s.SLp = tl; s.trOn = true; gDirty = true; }
   }
}
bool CanEnter(Strat &s, bool okb) { return okb && !gNoEntry && !s.pos && !s.stopped && (InpMaxDay <= 0 || s.dCnt < InpMaxDay); }
void StatsAdd(Strat &s, int rsn, double usd)
{
   s.n++; if(usd > 0) { s.nW++; s.gw += usd; } else s.gl -= usd;
   if(rsn == 2) { s.st++; s.mst = MathMax(s.mst, s.st); } else if(rsn == 1) s.st = 0;
   s.cum += usd; s.pk = MathMax(s.pk, s.cum); s.dd = MathMax(s.dd, s.pk - s.cum);
   if(rsn == 1) s.nTP++; else if(rsn == 2) s.nSL++; else if(rsn == 3) s.nBE++; else if(rsn == 4) s.nSV++; else s.nOth++;
}
void OpenAt(Strat &s, double px, datetime T)
{
   if(!MmOpen(s, px)) return;
   s.pos = true; s.F = px; s.SLp = px * (1.0 - s.sl / 100.0); s.TPp = px * (1.0 + s.tp / 100.0);
   s.BEl = px * (1.0 + s.be / 100.0); s.SVl = px * (1.0 - s.sv / 100.0); s.beOn = false; s.svOn = false; s.trOn = false; s.hi = px;
   s.eTime = T; s.cnt = true; s.dCnt++;
   if(!BrokerOpen(s)) { s.pos = false; s.cnt = false; s.dCnt--; return; }
   Note(s, "BUY " + DoubleToString(s.lots, 2) + " lot at " + DoubleToString(px, _Digits) + " | SL " + DoubleToString(s.SLp, _Digits) + " TP " + DoubleToString(s.TPp, _Digits) +
        " | risk " + DoubleToString(s.risk, 2), true);
}
void CloseAt(Strat &s, double px, int rsn, datetime T)
{
   double model = s.units * (px - s.F - Costs()) * Vpu(), usd = model;
   if(!gSim && !BrokerClose(s, model, usd)) { s.exitDue = rsn; s.exitPx = px; return; }   // refused: the trade stays, retried
   s.pos = false; s.exitDue = 0; gDirty = true;
   if(s.cnt) MmBook(s, usd);
   StatsAdd(s, rsn, usd);
   if(gSim)
   {
      int k = gSimN * 7; ArrayResize(gSimLog, k + 7, 70000);
      gSimLog[k] = s.id; gSimLog[k + 1] = (double)s.eTime; gSimLog[k + 2] = s.F; gSimLog[k + 3] = (double)T; gSimLog[k + 4] = px; gSimLog[k + 5] = rsn; gSimLog[k + 6] = s.risk;
      gSimN++;
   }
   s.cnt = false; s.ticket = 0; s.lastUsd = usd; s.lastRsn = rsn;
   Note(s, "EXIT " + RsnTxt(rsn) + " at " + DoubleToString(px, _Digits) + " | " + (usd >= 0 ? "+" : "") + DoubleToString(usd, 2), true);
}
void Up(Strat &s, double x, double y, bool okb, datetime T)
{
   for(int g = 0; g < 8; g++)
   {
      double best = 0; int ev = 0;
      if(s.pos && s.exitDue == 0)
      {
         if(x < s.TPp && s.TPp <= y) { best = s.TPp; ev = 1; }
         if(s.be > 0 && !s.beOn && !s.svOn && x < s.BEl && s.BEl <= y && (ev == 0 || s.BEl < best)) { best = s.BEl; ev = 2; }
      }
      if(InpEntry == ENT_STOP && s.lvlOn && x < s.E && s.E <= y && (ev == 0 || s.E < best)) { best = s.E; ev = 3; }
      if(ev == 0) break;
      if(ev == 1) CloseAt(s, s.TPp, s.svOn ? 4 : 1, T);
      else if(ev == 2) DoBE(s);
      else { if(CanEnter(s, okb)) OpenAt(s, s.E, T); s.lvlOn = false; }
   }
   if(s.pos && y > s.hi) s.hi = y;
}
void Dn(Strat &s, double x, double y, datetime T)
{
   if(s.pos && s.exitDue == 0) Trail(s);
   for(int g = 0; g < 8; g++)
   {
      double best = 0; int ev = 0;
      if(s.pos && s.exitDue == 0)
      {
         if(y <= s.SLp && s.SLp < x) { best = s.SLp; ev = 1; }
         if(s.sv > 0 && !s.svOn && !s.beOn && y <= s.SVl && s.SVl < x && (ev == 0 || s.SVl > best)) { best = s.SVl; ev = 2; }
      }
      if(ev == 0) break;
      if(ev == 1) CloseAt(s, s.SLp, s.trOn ? 5 : (s.beOn ? 3 : 2), T);
      else DoSV(s);
   }
}
void Seg(Strat &s, double x, double y, bool okb, datetime T) { if(y > x) Up(s, x, y, okb, T); else if(y < x) Dn(s, x, y, T); }
//--- the open of a 1-minute bar (a jump from the previous close): exits first, then BE / salvage, then a breakout at the open
void BarOpen(Strat &s, double o, double pc, bool okb, bool wk, int dno, datetime T)
{
   if(s.dPrev < 0 || dno != s.dPrev) { s.dCnt = 0; s.dPrev = dno; }
   if(s.pos && s.exitDue == 0)
   {
      Trail(s);
      int xr = 0;
      if(o >= s.TPp) xr = s.svOn ? 4 : 1;
      else if(o <= s.SLp) xr = s.trOn ? 5 : (s.beOn ? 3 : 2);
      else if(InpTExitH > 0 && T >= s.eTime + (datetime)MathRound(InpTExitH * 3600.0)) xr = 6;
      else if(wk) xr = 7;
      if(xr > 0) CloseAt(s, o, xr, T);
      else
      {
         if(s.be > 0 && !s.beOn && !s.svOn && o >= s.BEl) DoBE(s);
         else if(s.sv > 0 && !s.svOn && !s.beOn && o <= s.SVl) DoSV(s);
         if(o > s.hi) s.hi = o;
      }
   }
   if(InpEntry == ENT_STOP && s.lvlOn && pc > 0 && pc < s.E && o >= s.E)
   {
      if(CanEnter(s, okb)) OpenAt(s, o, T);
      s.lvlOn = false;
   }
}
//--- the close of a 1-minute bar: the candle-close entry
void BarClose(Strat &s, double c, bool okb, datetime T)
{
   if(InpEntry != ENT_CLOSE || !s.lvlOn) return;
   if(s.armed && c >= s.E) { if(CanEnter(s, okb)) OpenAt(s, c, T); s.lvlOn = false; }
   else if(c < s.E) s.armed = true;
}
//--- one 1-minute bar for one strategy, in three steps: BarEnd (the previous bar's close), the candles of its timeframe that closed
//--- (PushTf, done by the caller), BarBegin (the open), then Move for every later price
void BarEnd(Strat &s, BarCtx &c) { if(c.T > 0) BarClose(s, c.last, c.okb, c.T); }
void CtxBegin(BarCtx &c, datetime T, double o) { c.prevC = c.T > 0 ? c.last : 0; c.T = T; Filters(T, c.okb, c.wk, c.dno); c.last = o; }
void BarBegin(Strat &s, BarCtx &c, double o) { BarOpen(s, o, c.prevC, c.okb, c.wk, c.dno, c.T); }
void Move(Strat &s, BarCtx &c, double y) { Seg(s, c.last, y, c.okb, c.T); }
'''

TAIL = r'''void Setup()
{
{SETUP}
}
//--- one copy per symbol + magic number: a temporary global variable holds the chart of the copy that runs
string gLockN = ""; double gLockV = 0;
bool LockTake()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return true;
   gLockN = "FBGX|" + _Symbol + "|" + IntegerToString(InpMagic) + "|run";
   gLockV = (double)(ChartID() & 0xFFFFFFFFFFFF) + 1.0;
   if(!GlobalVariableCheck(gLockN)) GlobalVariableTemp(gLockN);
   if(GlobalVariableSetOnCondition(gLockN, gLockV, 0)) return true;
   double cur = GlobalVariableGet(gLockN);
   if(cur == gLockV) return true;
   for(long id = ChartFirst(); id >= 0; id = ChartNext(id))
      if(id != ChartID() && (double)(id & 0xFFFFFFFFFFFF) + 1.0 == cur && ChartGetString(id, CHART_EXPERT_NAME) != "") return false;
   return GlobalVariableSetOnCondition(gLockN, gLockV, cur);
}
void LockFree() { if(gLockN != "" && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableSetOnCondition(gLockN, 0, gLockV); }

int OnInit()
{
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
   {
      string m = "Fractal Breakout Grid EA needs a HEDGING account (every strategy holds its own position); this account nets positions.";
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   if(InpRun == RUN_ONE && (InpRunOne < 1 || InpRunOne > 12)) { Print("Run one strategy: the number must be 1 to 12."); return INIT_PARAMETERS_INCORRECT; }
   if(InpSpread < 0 || InpCommLot < 0 || InpStartB <= 0 || InpLev <= 0) { Print("Spread, commission, start balance and leverage limit must be above 0 (spread / commission: 0 or more)."); return INIT_PARAMETERS_INCORRECT; }
   if((InpSizeMode == PSZ_USD && InpBaseRisk <= 0) || (InpSizeMode == PSZ_LOT && InpBaseLots <= 0) || (InpSizeMode == PSZ_PCT && InpEqPct <= 0))
   { Print("Position size: the base risk, base lots or risk % of equity must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpCapOn && InpHardCap <= 0) { Print("Hard cap: the amount must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRG && InpCrkGX <= 0) { Print("Crooks G: the limit of the loss to win back must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRH && InpCrkHPct <= 0) { Print("Crooks H: the % of the equity must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRJ && InpCrkJX <= 0) { Print("Crooks J: the drawdown must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if((InpRec == REC_CRF || InpRec == REC_CRI) && InpCrkFK <= 0) { Print("Crooks F / I: the limit must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpLadder != LAD_OFF && InpLadT <= 0) { Print("Profit ladder: the profit target must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpCrkELot <= 0 || InpRecMult <= 0) { Print("Crooks E / I lot and the Martingale multiplier must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   Setup();
   for(int i = 0; i < 12; i++)
      if(S[i].ok && (S[i].sl <= 0 || S[i].tp <= 0 || S[i].be < 0 || S[i].sv < 0))
      { Print("Strategy ", i + 1, ": SL % and TP % must be above 0, BE and salvage triggers 0 or more."); return INIT_PARAMETERS_INCORRECT; }
   gSvBase = "FBG|" + _Symbol + "|" + IntegerToString(InpMagic) + "|";
   if(StringLen(gSvBase) > 50) gSvBase = "FBG|" + StringSubstr(_Symbol, 0, 20) + "|" + IntegerToString(InpMagic) + "|";
   if(!LockTake())
   {
      string m = "Another copy of this EA runs on " + _Symbol + " with magic number " + IntegerToString(InpMagic) + ": remove one, or give each its own magic number.";
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   trade.SetDeviationInPoints(50);
   trade.SetTypeFillingBySymbol(_Symbol);
   TzPick();
   TrendLoad();
   datetime now = TimeCurrent(); now = now - now % 60;
   gC.T = 0; gC.last = 0; gC.prevC = 0; gC.okb = false; gC.wk = false; gC.dno = 0;
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariablesDeleteAll(gSvBase);   // memory off: forget the saved state
   gRestored = StateLoad();
   if(gRestored) Restore(now);
   else
   {
      BarCtx c;
      for(int i = 0; i < 12; i++)
      {
         c.T = 0; c.last = 0; c.prevC = 0; c.okb = false; c.wk = false; c.dno = 0;
         if(S[i].ok) { WarmStrat(S[i], now, c); if(c.T > 0) gC = c; }
      }
   }
   for(int i = 0; i < 12; i++)
      if(S[i].ok) Print("FBG S", i + 1, " ", TfTxt(S[i].tf), " ", S[i].r, "/", S[i].l, ": ", NowTxt(S[i]));
   Reconcile();
   gDirty = true;
   EventSetTimer(2);
   Draw(true);
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason)
{
   StateSave(true);
   EventKillTimer();
   ObjectsDeleteAll(0, "FBG_");
   LockFree();
}
void OnTick()
{
   MqlTick tk;
   if(!SymbolInfoTick(_Symbol, tk) || tk.bid <= 0) return;
   Reconcile();
   datetime m = tk.time - tk.time % 60;
   if(m != gC.T)
   {
      for(int i = 0; i < 12; i++) if(S[i].ok) BarEnd(S[i], gC);
      for(int i = 0; i < 12; i++) if(S[i].ok) PushLive(S[i]);
      TrendLive();
      CtxBegin(gC, m, tk.bid);
      for(int i = 0; i < 12; i++) if(S[i].ok) BarBegin(S[i], gC, tk.bid);
      gDirty = true;
   }
   else if(tk.bid != gC.last)
   {
      for(int i = 0; i < 12; i++) if(S[i].ok) Move(S[i], gC, tk.bid);
      gC.last = tk.bid;
   }
   Sync();
   if(gDirty) { StateSave(false); gDirty = false; }
   Draw(false);
}
void OnTimer()
{
   Reconcile();
   if(gDirty) { StateSave(false); gDirty = false; }
   Draw(false);
}
'''


def tail():
    st = '\n'.join('   StratInit(S[%d], %d, Runs(%d, InpS%dOn), InpS%dTf, InpS%dR, InpS%dL, InpS%dOff, InpS%dSl, InpS%dTp, InpS%dBe, InpS%dSv);' % ((i, i + 1) + (i + 1,) * 10) for i in range(12))
    return TAIL.replace('{SETUP}', st)


def build(out):
    src = HEAD + ''.join(strat_inputs(i + 1, p) for i, p in enumerate(S12)) + OPTS + CORE
    import os
    rest = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ea_rest.mq5')
    if os.path.exists(rest): src += open(rest).read()
    src += tail()
    open(out, 'w', encoding='ascii').write(src)
    print('wrote', out, src.count('\n'), 'lines')


if __name__ == '__main__':
    build(sys.argv[1])
