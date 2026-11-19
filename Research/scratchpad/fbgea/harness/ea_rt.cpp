#include "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/run/mql5rt.h"
#line 1 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fbgea/harness/EA_copy.mq5"
//+------------------------------------------------------------------+
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
//|                                                                  |
//| v1.1: PRESET at the top of the inputs: Custom or a tested        |
//| combination of strategies with its money (the $1,000-a-month     |
//| gold study); a monthly restart of every strategy's money.        |
//+------------------------------------------------------------------+





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

enum ENUM_GPRESET { GP_CUSTOM = 0,  // Custom (my settings below)
                    GP_1 = 1,     // Best monthly: S7, S8, S10 - $10 - exact recovery - cap $100
                    GP_2 = 2,     // Safest: S1, S2, S6, S7, S8, S10 - $5 - exact recovery - cap $50
                    GP_3 = 3,     // Steady, more profit: S1, S2, S6, S7, S8, S10 - $10 - exact recovery - cap $100 start again
                    GP_4 = 4,     // Small: S7, S8, S10 - $5 - exact recovery - cap $50
                    GP_5 = 5,     // No recovery: all 12 - $10 fixed risk
                    GP_6 = 6      // No recovery: 11 strategies (all but S4) - $10 fixed risk
                  };
  
 ENUM_GPRESET InpPreset = GP_CUSTOM; // Preset (its strategies, tested settings and money; weekend close, costs, balance stay yours)
 bool   InpAddMine  = false;  // Add my days and hours to the preset
 bool   InpMyMoney  = false;  // Use my money settings with the preset (base risk, recovery, cap, ladder, monthly restart)

  
 ENUM_RUN InpRun     = RUN_ALL; // Run
 int    InpRunOne    = 11;      //   ...the one strategy (1-12)
 mql_long   InpMagic     = 26110;   // Magic number base (strategy N uses base + N)
 double InpSpread    = 0.16;    // Spread for sizing (price; 0 = the live spread)
 double InpCommLot   = 7.0;     // Commission per lot, round trip (sizing)

  
 bool            InpS1On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS1Tf  = PERIOD_D1; // Swing-high timeframe
 int             InpS1R   = 3;  // Right candles
 int             InpS1L   = 25;  // Left candles
 double          InpS1Off = -0.14;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS1Sl  = 3.0;   // SL %
 double          InpS1Tp  = 0.75;   // TP %
 double          InpS1Be  = 0.45;   // BE trigger % (0 = off)
 double          InpS1Sv  = 0.8;   // Salvage trigger % (0 = off)

  
 bool            InpS2On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS2Tf  = PERIOD_D1; // Swing-high timeframe
 int             InpS2R   = 3;  // Right candles
 int             InpS2L   = 15;  // Left candles
 double          InpS2Off = -0.085;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS2Sl  = 0.5;   // SL %
 double          InpS2Tp  = 2.0;   // TP %
 double          InpS2Be  = 0.25;   // BE trigger % (0 = off)
 double          InpS2Sv  = 0.8;   // Salvage trigger % (0 = off)

  
 bool            InpS3On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS3Tf  = PERIOD_D1; // Swing-high timeframe
 int             InpS3R   = 2;  // Right candles
 int             InpS3L   = 7;  // Left candles
 double          InpS3Off = -0.065;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS3Sl  = 0.3;   // SL %
 double          InpS3Tp  = 1.65;   // TP %
 double          InpS3Be  = 0.2;   // BE trigger % (0 = off)
 double          InpS3Sv  = 0.5;   // Salvage trigger % (0 = off)

  
 bool            InpS4On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS4Tf  = PERIOD_H4; // Swing-high timeframe
 int             InpS4R   = 8;  // Right candles
 int             InpS4L   = 12;  // Left candles
 double          InpS4Off = -0.025;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS4Sl  = 0.44;   // SL %
 double          InpS4Tp  = 3.1;   // TP %
 double          InpS4Be  = 0.33;   // BE trigger % (0 = off)
 double          InpS4Sv  = 0.9;   // Salvage trigger % (0 = off)

  
 bool            InpS5On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS5Tf  = PERIOD_H1; // Swing-high timeframe
 int             InpS5R   = 19;  // Right candles
 int             InpS5L   = 30;  // Left candles
 double          InpS5Off = -0.045;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS5Sl  = 2.0;   // SL %
 double          InpS5Tp  = 0.35;   // TP %
 double          InpS5Be  = 0.1;   // BE trigger % (0 = off)
 double          InpS5Sv  = 0.7;   // Salvage trigger % (0 = off)

  
 bool            InpS6On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS6Tf  = PERIOD_H1; // Swing-high timeframe
 int             InpS6R   = 25;  // Right candles
 int             InpS6L   = 25;  // Left candles
 double          InpS6Off = -0.06;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS6Sl  = 4.2;   // SL %
 double          InpS6Tp  = 0.33;   // TP %
 double          InpS6Be  = 0.15;   // BE trigger % (0 = off)
 double          InpS6Sv  = 0.8;   // Salvage trigger % (0 = off)

  
 bool            InpS7On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS7Tf  = PERIOD_H1; // Swing-high timeframe
 int             InpS7R   = 23;  // Right candles
 int             InpS7L   = 25;  // Left candles
 double          InpS7Off = -0.055;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS7Sl  = 0.87;   // SL %
 double          InpS7Tp  = 0.56;   // TP %
 double          InpS7Be  = 0.13;   // BE trigger % (0 = off)
 double          InpS7Sv  = 1.1;   // Salvage trigger % (0 = off)

  
 bool            InpS8On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS8Tf  = PERIOD_H1; // Swing-high timeframe
 int             InpS8R   = 20;  // Right candles
 int             InpS8L   = 25;  // Left candles
 double          InpS8Off = -0.06;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS8Sl  = 0.68;   // SL %
 double          InpS8Tp  = 0.43;   // TP %
 double          InpS8Be  = 0.1;   // BE trigger % (0 = off)
 double          InpS8Sv  = 0.7;   // Salvage trigger % (0 = off)

  
 bool            InpS9On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS9Tf  = PERIOD_H1; // Swing-high timeframe
 int             InpS9R   = 5;  // Right candles
 int             InpS9L   = 5;  // Left candles
 double          InpS9Off = -0.08;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS9Sl  = 2.0;   // SL %
 double          InpS9Tp  = 0.7;   // TP %
 double          InpS9Be  = 0.1;   // BE trigger % (0 = off)
 double          InpS9Sv  = 1.0;   // Salvage trigger % (0 = off)

  
 bool            InpS10On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS10Tf  = PERIOD_M5; // Swing-high timeframe
 int             InpS10R   = 30;  // Right candles
 int             InpS10L   = 65;  // Left candles
 double          InpS10Off = -0.05;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS10Sl  = 1.0;   // SL %
 double          InpS10Tp  = 1.0;   // TP %
 double          InpS10Be  = 0.2;   // BE trigger % (0 = off)
 double          InpS10Sv  = 0.0;   // Salvage trigger % (0 = off)

  
 bool            InpS11On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS11Tf  = PERIOD_M15; // Swing-high timeframe
 int             InpS11R   = 20;  // Right candles
 int             InpS11L   = 40;  // Left candles
 double          InpS11Off = -0.01;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS11Sl  = 1.0;   // SL %
 double          InpS11Tp  = 3.0;   // TP %
 double          InpS11Be  = 0.2;   // BE trigger % (0 = off)
 double          InpS11Sv  = 0.1;   // Salvage trigger % (0 = off)

  
 bool            InpS12On  = true;      // On (Run = Ticked strategies)
 ENUM_TIMEFRAMES InpS12Tf  = PERIOD_M1; // Swing-high timeframe
 int             InpS12R   = 45;  // Right candles
 int             InpS12L   = 200;  // Left candles
 double          InpS12Off = -0.05;  // Buy entry offset % (from the swing high; -0.14 = 0.14 % below)
 double          InpS12Sl  = 0.75;   // SL %
 double          InpS12Tp  = 3.0;   // TP %
 double          InpS12Be  = 0.2;   // BE trigger % (0 = off)
 double          InpS12Sv  = 0.0;   // Salvage trigger % (0 = off)

  
 ENUM_ENTRY InpEntry = ENT_STOP; // Entry
 int    InpExpN    = 0;      // Buy stop expires after N swing-high candles (0 = never)
 int    InpMaxDay  = 0;      // Most entries per day, each strategy (0 = no limit)
 double InpTrA     = 0.0;    // Trailing stop: starts at +% from the fill
 double InpTrD     = 0.0;    // Trailing stop: distance % (0 = off)
 double InpTExitH  = 0.0;    // Close a trade after N hours (0 = off)
 bool   InpWkOn    = false;  // Close before the weekend (Friday, New York time)
 int    InpWkH     = 16;     //   ...from this hour (New York)
 bool   InpTrnOn   = false;  // Only buy above the EMA
 ENUM_TIMEFRAMES InpTrnTf = PERIOD_H4; //   ...EMA timeframe
 int    InpTrnLen  = 50;     //   ...EMA length

  
 ENUM_SRV_TZ InpServerTz = SRV_AUTO; // Broker server clock
 double InpServerGMT = 2.0;  // Broker server time zone if fixed (GMT +h)
 double InpUserGMT   = 5.5;  // Your time zone (GMT +h; India = 5.5)
 bool   InpDayOn   = false;  // Trade only on the ticked days
 bool   InpMon     = true;   //   Monday
 bool   InpTue     = true;   //   Tuesday
 bool   InpWed     = true;   //   Wednesday
 bool   InpThu     = true;   //   Thursday
 bool   InpFri     = true;   //   Friday
 bool   InpSat     = false;  //   Saturday
 bool   InpSun     = false;  //   Sunday
 bool   InpHoursOn = false;  // Trade only between
 int    InpHourFrom = 600;   //   ...from (HHMM, your time)
 int    InpHourTo   = 2300;  //   ...to (HHMM, not included; earlier than from = over midnight)

  
 double InpStartB   = 10000.0; // Start balance of each strategy
 ENUM_SIZE InpSizeMode = PSZ_USD; // Position size: the base trade (the loss recovery sizes every trade from it)
 double InpBaseRisk = 50.0;   // Base risk per trade (account currency; Fixed $ risk)
 double InpBaseLots = 0.01;   // Base lots (Fixed lots)
 double InpEqPct    = 1.0;    // Risk % of equity (% of equity at risk, and the % of equity rule)
 double InpLev      = 100.0;  // Leverage limit 1:N (a trade is never bigger than the balance x N)
 bool   InpCapOn    = true;   // Hard cap: max loss per trade
 double InpHardCap  = 500.0;  //   ...amount
 ENUM_CAP InpCapAction = CAP_CLAMP; //   ...if the risk would exceed the cap
 bool   InpMRestart = false;  // Restart every strategy's money on the 1st of each month (your time zone; the balance carries on)

  
 ENUM_REC InpRec    = REC_CRF; // Loss recovery
 int    InpRecN     = 3;      // Recover over N trades / Delayed recovery: N
 double InpRecPct   = 50.0;   // Recover a % of losses: the %
 double InpRecMult  = 2.0;    // Martingale / Grand Martingale multiplier
 double InpRecStep  = 25.0;   // Step-up: $ per loss in a row
 int    InpCSplit   = 3;      // Split (Rule C, Crooks B)
 int    InpParN     = 3;      // Paroli: wins before reset
 int    InpDelayN   = 2;      // Delayed recovery: losses before it starts
 int    InpCrkCn    = 1;      // Crooks C - J: win the loss back over N wins
 ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C - J: after N losing recovery trades in a row
 int    InpCrkPrN   = 2;      //   ...N
 double InpCrkPrPct = 50.0;   //   ...% of the loss each recovery trade goes for
 int    InpCrkPrM   = 2;      //   ...M wins in a row to wait for
 double InpCrkELot  = 0.01;   // Crooks E / I: lot while a loss waits for a win
 double InpCrkFK    = 3.0;    // Crooks F / I: a recovery trade risks at most x base
 double InpCrkGX    = 10.0;   // Crooks G: the loss to win back is at most x base
 double InpCrkHPct  = 1.0;    // Crooks H: a recovery trade risks at most % of equity
 double InpCrkJX    = 20.0;   // Crooks J: drawdown (x base) where recovery ends
 ENUM_LADDER InpLadder = LAD_MED; // Profit ladder (Crooks F - J): risk appetite
 double InpLadT     = 1000.0; //   ...profit target before the risk goes up ($ of the strategy)

  
 bool   InpTable    = true;   // Table
 ENUM_TBL_POS InpTablePos = TBL_TOP_RIGHT; //   ...position
 int    InpTableFont = 8;     //   ...font size
 bool   InpLines    = true;   // Lines: waiting buy stops, open trades' SL and TP
 bool   InpAlerts   = false;  // Alert on entries and exits
 bool   InpPush     = false;  // Push notification on entries and exits
 bool   InpRemember = true;   // Continue after a restart (restart memory)
 int    InpWarmDays = 60;     // Warm-up: days of 1-minute history read at a fresh start

//--- one strategy: settings, swing-high candles, the waiting buy stop, the trade, the money and the stats
//--- v1.1 the values the rules use: the inputs (Custom) or the preset's (PresetApply)
ENUM_RUN gpRun;
bool gpS1On;
ENUM_TIMEFRAMES gpS1Tf;
int gpS1R;
int gpS1L;
double gpS1Off;
double gpS1Sl;
double gpS1Tp;
double gpS1Be;
double gpS1Sv;
bool gpS2On;
ENUM_TIMEFRAMES gpS2Tf;
int gpS2R;
int gpS2L;
double gpS2Off;
double gpS2Sl;
double gpS2Tp;
double gpS2Be;
double gpS2Sv;
bool gpS3On;
ENUM_TIMEFRAMES gpS3Tf;
int gpS3R;
int gpS3L;
double gpS3Off;
double gpS3Sl;
double gpS3Tp;
double gpS3Be;
double gpS3Sv;
bool gpS4On;
ENUM_TIMEFRAMES gpS4Tf;
int gpS4R;
int gpS4L;
double gpS4Off;
double gpS4Sl;
double gpS4Tp;
double gpS4Be;
double gpS4Sv;
bool gpS5On;
ENUM_TIMEFRAMES gpS5Tf;
int gpS5R;
int gpS5L;
double gpS5Off;
double gpS5Sl;
double gpS5Tp;
double gpS5Be;
double gpS5Sv;
bool gpS6On;
ENUM_TIMEFRAMES gpS6Tf;
int gpS6R;
int gpS6L;
double gpS6Off;
double gpS6Sl;
double gpS6Tp;
double gpS6Be;
double gpS6Sv;
bool gpS7On;
ENUM_TIMEFRAMES gpS7Tf;
int gpS7R;
int gpS7L;
double gpS7Off;
double gpS7Sl;
double gpS7Tp;
double gpS7Be;
double gpS7Sv;
bool gpS8On;
ENUM_TIMEFRAMES gpS8Tf;
int gpS8R;
int gpS8L;
double gpS8Off;
double gpS8Sl;
double gpS8Tp;
double gpS8Be;
double gpS8Sv;
bool gpS9On;
ENUM_TIMEFRAMES gpS9Tf;
int gpS9R;
int gpS9L;
double gpS9Off;
double gpS9Sl;
double gpS9Tp;
double gpS9Be;
double gpS9Sv;
bool gpS10On;
ENUM_TIMEFRAMES gpS10Tf;
int gpS10R;
int gpS10L;
double gpS10Off;
double gpS10Sl;
double gpS10Tp;
double gpS10Be;
double gpS10Sv;
bool gpS11On;
ENUM_TIMEFRAMES gpS11Tf;
int gpS11R;
int gpS11L;
double gpS11Off;
double gpS11Sl;
double gpS11Tp;
double gpS11Be;
double gpS11Sv;
bool gpS12On;
ENUM_TIMEFRAMES gpS12Tf;
int gpS12R;
int gpS12L;
double gpS12Off;
double gpS12Sl;
double gpS12Tp;
double gpS12Be;
double gpS12Sv;
ENUM_ENTRY gpEntry;
int gpExpN;
int gpMaxDay;
double gpTrA;
double gpTrD;
double gpTExitH;
bool gpTrnOn;
bool gpDayOn;
bool gpHoursOn;
ENUM_SIZE gpSizeMode;
double gpBaseRisk;
bool gpCapOn;
double gpHardCap;
ENUM_CAP gpCapAction;
ENUM_REC gpRec;
ENUM_LADDER gpLadder;
bool gpMRestart;
string PresetName()
{
   switch(InpPreset)
   {
      case GP_1: return "G1 Best monthly: S7, S8, S10"_mq;
      case GP_2: return "G2 Safest: S1, S2, S6, S7, S8, S10"_mq;
      case GP_3: return "G3 Steady, more profit: S1, S2, S6, S7, S8, S10"_mq;
      case GP_4: return "G4 Small: S7, S8, S10"_mq;
      case GP_5: return "G5 No recovery: all 12"_mq;
      case GP_6: return "G6 No recovery: 11 strategies (all but S4)"_mq;
      default: break;
   }
   return "Custom"_mq;
}
struct Strat
{
   int      id;                  // 1 - 12
   bool     ok;                  // runs
   ENUM_TIMEFRAMES tf;
   int      r, l;
   double   off, sl, tp, be, sv;
   MqlArr<double>   hs;                // the last left + right + 1 highs of its timeframe (ring, by candle number)
   MqlArr<datetime> ht;                // their open times
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
   double   n0;                  // v1.1 monthly restart: the closed profit at the last restart (the money rules count from it)
   int      mKey, curM;          //   the month of the money (yyyymm), this candle's month
   bool     capStp;              //   stopped by the hard cap (ends with the month)
   // money (gold/recovery.py simulate, as the Pine code)
   double   eq, pkEq, ddU, ddP, net, peakNet, recPool, carried, oscP, crL, risk, units, bR;
   int      recLosses, dUnits, parWins, rdUnits, oscU, crN, crP, crF, crWW;
   bool     crW, crWait, crNeedL, crRecT;
   MqlArr<double>   lab;
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
bool   gReady = false;           // the start is done (history read, memory or warm-up): the rules run
datetime gStartAt = 0;
MqlArr<double> gSimLog; int gSimN = 0; // test harness only: the closed trades (strategy, entry time, entry, exit time, exit, reason, $ risk)
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
   mq_dot(s).id = id; mq_dot(s).ok = on; mq_dot(s).tf = tf; mq_dot(s).r = MathMax(1, r); mq_dot(s).l = MathMax(1, l); mq_dot(s).off = off; mq_dot(s).sl = sl; mq_dot(s).tp = tp; mq_dot(s).be = be; mq_dot(s).sv = sv;
   ArrayResize(mq_dot(s).hs, mq_dot(s).l + mq_dot(s).r + 1); ArrayResize(mq_dot(s).ht, mq_dot(s).l + mq_dot(s).r + 1); ArrayInitialize(mq_dot(s).hs, 0.0); ArrayInitialize(mq_dot(s).ht, 0);
   mq_dot(s).nC = 0; mq_dot(s).tfLast = 0;
   mq_dot(s).lvlOn = false; mq_dot(s).lvlH = 0; mq_dot(s).E = 0; mq_dot(s).lvlT = 0; mq_dot(s).kAct = 0; mq_dot(s).actT = 0; mq_dot(s).armed = false;
   mq_dot(s).pos = false; mq_dot(s).F = 0; mq_dot(s).SLp = 0; mq_dot(s).TPp = 0; mq_dot(s).BEl = 0; mq_dot(s).SVl = 0; mq_dot(s).hi = 0; mq_dot(s).beOn = false; mq_dot(s).svOn = false; mq_dot(s).trOn = false;
   mq_dot(s).eTime = 0; mq_dot(s).cnt = false; mq_dot(s).ticket = 0; mq_dot(s).lots = 0; mq_dot(s).dCnt = 0; mq_dot(s).dPrev = -1; mq_dot(s).stopped = false; mq_dot(s).stopWhy = ""_mq;
   mq_dot(s).n0 = 0; mq_dot(s).mKey = -1; mq_dot(s).curM = -1; mq_dot(s).capStp = false;
   mq_dot(s).eq = InpStartB; mq_dot(s).pkEq = InpStartB; mq_dot(s).ddU = 0; mq_dot(s).ddP = 0; mq_dot(s).net = 0; mq_dot(s).peakNet = 0; mq_dot(s).recPool = 0; mq_dot(s).carried = 0; mq_dot(s).oscP = 0; mq_dot(s).crL = 0;
   mq_dot(s).risk = 0; mq_dot(s).units = 0; mq_dot(s).bR = 0;
   mq_dot(s).recLosses = 0; mq_dot(s).dUnits = 1; mq_dot(s).parWins = 0; mq_dot(s).rdUnits = 1; mq_dot(s).oscU = 1; mq_dot(s).crN = 0; mq_dot(s).crP = MathMax(1, InpCrkCn); mq_dot(s).crF = 0; mq_dot(s).crWW = 0;
   mq_dot(s).crW = false; mq_dot(s).crWait = false; mq_dot(s).crNeedL = false; mq_dot(s).crRecT = false;
   ArrayResize(mq_dot(s).lab, 3); mq_dot(s).lab[0] = 1.0; mq_dot(s).lab[1] = 2.0; mq_dot(s).lab[2] = 3.0;
   mq_dot(s).n = 0; mq_dot(s).nW = 0; mq_dot(s).nTP = 0; mq_dot(s).nSL = 0; mq_dot(s).nBE = 0; mq_dot(s).nSV = 0; mq_dot(s).nOth = 0; mq_dot(s).st = 0; mq_dot(s).mst = 0;
   mq_dot(s).gw = 0; mq_dot(s).gl = 0; mq_dot(s).cum = 0; mq_dot(s).pk = 0; mq_dot(s).dd = 0; mq_dot(s).lastUsd = 0; mq_dot(s).lastRsn = 0; mq_dot(s).exitDue = 0; mq_dot(s).exitPx = 0;
}

//--- a completed candle of the strategy's timeframe (high, open time); tNow = the open time of the candle that starts now.
//--- detect: look for a swing high (off while the candles are rebuilt after a restart)
void PushTf(Strat &s, double high, datetime t, datetime tNow, bool detect)
{
   int w = mq_dot(s).l + mq_dot(s).r + 1, k = mq_dot(s).nC;
   mq_dot(s).hs[k % w] = high; mq_dot(s).ht[k % w] = t; mq_dot(s).nC++;
   if(!detect) return;
   int hb = mq_dot(s).nC;                                     // the number of the candle that starts now
   int p = k - mq_dot(s).r;                                   // the candidate: right candles after it have closed
   if(p - mq_dot(s).l >= 0)
   {
      double v = mq_dot(s).hs[p % w];
      bool ok = true;
      for(int i = 1; i <= mq_dot(s).l && ok; i++) if(mq_dot(s).hs[(p - i) % w] >= v) ok = false;
      for(int j = 1; j <= mq_dot(s).r && ok; j++) if(mq_dot(s).hs[(p + j) % w] >= v) ok = false;
      if(ok && mq_dot(s).ht[p % w] != mq_dot(s).lvlT)
      {
         mq_dot(s).lvlT = mq_dot(s).ht[p % w]; mq_dot(s).lvlOn = true; mq_dot(s).lvlH = v; mq_dot(s).E = v * (1.0 + mq_dot(s).off / 100.0); mq_dot(s).kAct = hb; mq_dot(s).actT = tNow; mq_dot(s).armed = false;
         Note(s, "BUY STOP "_mq + DoubleToString(mq_dot(s).E, _Digits) + " (swing high "_mq + DoubleToString(v, _Digits) + ")"_mq, false);
      }
   }
   if(mq_dot(s).lvlOn && gpExpN > 0 && hb - mq_dot(s).kAct >= gpExpN) mq_dot(s).lvlOn = false;
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
datetime UtcOf(datetime server) { return (datetime)((mql_long)server - (mql_long)MathRound(SrvGMT(server) * 3600.0)); }
datetime UserOf(datetime server) { return (datetime)((mql_long)UtcOf(server) + (mql_long)MathRound(InpUserGMT * 3600.0)); }
int NthSunday(int y, int mon, int k)
{
   MqlDateTime d; ZeroMemory(d); mq_dot(d).year = y; mq_dot(d).mon = mon; mq_dot(d).day = 1;
   MqlDateTime f; TimeToStruct(StructToTime(d), f);
   return 1 + (7 - mq_dot(f).day_of_week) % 7 + 7 * (k - 1);
}
int LastSunday(int y, int mon) { int d = NthSunday(y, mon, 1); while(d + 7 <= 31) d += 7; return d; }
datetime MkTime(int y, int mon, int day, int hr) { MqlDateTime d; ZeroMemory(d); mq_dot(d).year = y; mq_dot(d).mon = mon; mq_dot(d).day = day; mq_dot(d).hour = hr; return StructToTime(d); }
// New York daylight time at a UTC time: 07:00 UTC on the second Sunday of March to 06:00 UTC on the first Sunday of November
bool NySummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(mq_dot(d).year, 3, NthSunday(mq_dot(d).year, 3, 2), 7) && utc < MkTime(mq_dot(d).year, 11, NthSunday(mq_dot(d).year, 11, 1), 6); }
bool InSess(int mins)
{
   int a0 = (InpHourFrom / 100) * 60 + InpHourFrom % 100, a1 = (InpHourTo / 100) * 60 + InpHourTo % 100;
   return a0 < a1 ? (mins >= a0 && mins < a1) : (mins >= a0 || mins < a1);
}
void Filters(datetime T, bool &okb, bool &wk, int &dno)
{
   datetime utc = UtcOf(T), u = UserOf(T);
   MqlDateTime lz; TimeToStruct(u, lz);
   bool dOk = !gpDayOn || (mq_dot(lz).day_of_week == 1 ? InpMon : mq_dot(lz).day_of_week == 2 ? InpTue : mq_dot(lz).day_of_week == 3 ? InpWed : mq_dot(lz).day_of_week == 4 ? InpThu :
                            mq_dot(lz).day_of_week == 5 ? InpFri : mq_dot(lz).day_of_week == 6 ? InpSat : InpSun);
   bool hOk = !gpHoursOn || InSess(mq_dot(lz).hour * 60 + mq_dot(lz).min);
   bool tOk = !gpTrnOn || gTrUp;
   MqlDateTime ny; TimeToStruct((datetime)((mql_long)utc - (NySummer(utc) ? 4 : 5) * 3600), ny);
   wk = InpWkOn && mq_dot(ny).day_of_week == 5 && mq_dot(ny).hour >= InpWkH;
   okb = dOk && hOk && tOk && !wk;
   dno = mq_dot(lz).year * 10000 + mq_dot(lz).mon * 100 + mq_dot(lz).day;
}

//--- money (gold/recovery.py simulate, the same as the Pine code)
bool CrkFam() { return gpRec == REC_CRC || gpRec == REC_CRE || gpRec == REC_CRF || gpRec == REC_CRG || gpRec == REC_CRH || gpRec == REC_CRI || gpRec == REC_CRJ; }
bool LadFam() { return gpRec == REC_CRF || gpRec == REC_CRG || gpRec == REC_CRH || gpRec == REC_CRI || gpRec == REC_CRJ; }
bool PrOn()   { return CrkFam() && InpCrkPr != CPR_OFF; }
void LadPar(double &lam, double &phi, double &bmx, double &gam)
{
   lam = 0.8; phi = 0.10; bmx = 2.0; gam = 0.25;
   if(gpLadder == LAD_MED)   { lam = 0.7; phi = 0.15; bmx = 3.0;  gam = 0.30; }
   if(gpLadder == LAD_HIGH)  { lam = 0.6; phi = 0.20; bmx = 5.0;  gam = 0.35; }
   if(gpLadder == LAD_XHIGH) { lam = 0.5; phi = 0.25; bmx = 8.0;  gam = 0.40; }
   if(gpLadder == LAD_MAX)   { lam = 0.4; phi = 0.30; bmx = 12.0; gam = 0.50; }
}
//--- units of the Crooks E / I lot (rounded up to the lot step)
double EUnits() { double st = LotStep(); return MathCeil(MathMax(InpCrkELot, st) / st - 1e-9) * st * Contract(); }
//--- the base trade's $ risk at a stop distance sd (price): Fixed $ risk, the Fixed lots' loss at that stop (costs included), or % of the account
double FBase(Strat &s, double sd)
{
   if(gpSizeMode == PSZ_LOT) return InpBaseLots * Contract() * (sd + Costs()) * Vpu();
   if(gpSizeMode == PSZ_PCT) return MathMax(0.0, mq_dot(s).eq) * InpEqPct / 100.0;
   return gpBaseRisk;
}
//--- the profit ladder at base B: on, the start guard (closed profit 0 or less), its base, the cushion above the lock
bool FLad(Strat &s, double B, bool &guard, double &lb, double &cush)
{
   bool on = gpLadder != LAD_OFF && LadFam() && mq_dot(s).peakNet >= InpLadT;
   double lam = 0, phi = 0, bmx = 0, gam = 0; LadPar(lam, phi, bmx, gam);
   cush = on ? MathMax(0.0, mq_dot(s).net - mq_dot(s).n0 - lam * mq_dot(s).peakNet) : 0.0;
   guard = on && mq_dot(s).net - mq_dot(s).n0 <= 0;
   lb = on ? B + MathMin((bmx - 1.0) * B, phi * cush) : B;
   return on;
}
//--- a Crooks C - J trade at base B (rec = a recovery trade)
double FCrk(Strat &s, double B, bool rec, double rmin, double pf, double xr)
{
   double x = rec ? MathMax(B, mq_dot(s).crL / mq_dot(s).crP * pf / xr) : B;
   if(rec)
   {
      if(gpRec == REC_CRF || gpRec == REC_CRI) x = MathMin(x, InpCrkFK * B);
      else if(gpRec == REC_CRH) x = MathMin(x, MathMax(B, mq_dot(s).eq * InpCrkHPct / 100.0));
      else if(gpRec == REC_CRJ) x = MathMax(B, x * MathMax(0.0, 1.0 - (mq_dot(s).peakNet - (mq_dot(s).net - mq_dot(s).n0)) / (InpCrkJX * B)));
   }
   else if(mq_dot(s).crL > 0 && (gpRec == REC_CRE || gpRec == REC_CRI)) x = MathMin(B, rmin);
   return x;
}
//--- the rule's risk for the next trade (before the cap and the leverage limit), whether it is a recovery trade, and Rule C split's base
double FRaw(Strat &s, double sd, bool &rec, double &baseC)
{
   double base = FBase(s, sd);
   double xr = mq_dot(s).tp / mq_dot(s).sl, rmin = EUnits() * (sd + Costs()) * Vpu();
   double add = gpRec == REC_ALL ? mq_dot(s).recPool : gpRec == REC_SPLIT ? mq_dot(s).recPool / MathMax(1, InpRecN) : gpRec == REC_PART ? mq_dot(s).recPool * InpRecPct / 100.0 :
                gpRec == REC_EXACT ? mq_dot(s).recPool / xr : gpRec == REC_STEP ? InpRecStep * mq_dot(s).recLosses : 0.0;
   double fa = 1.0, fb = 1.0;
   for(int k = 2; k <= MathMin(mq_dot(s).recLosses, 200); k++) { double t2 = fa + fb; fa = fb; fb = t2; }
   double stepBase = 0.0;
   double netR = mq_dot(s).net - mq_dot(s).n0;                     // v1.1: the closed profit since the monthly restart
   if(netR >= 1000) { int kk = (int)MathFloor((netR - 1000.0) / 500.0); stepBase = (1000.0 + 500.0 * kk) / (8.0 + kk); }
   else if(netR >= 500) stepBase = 500.0 / 5.0;
   else if(netR >= 200) stepBase = 200.0 / 3.0;
   baseC = gpRec == REC_CS ? MathMax(base, gpCapOn ? MathMin(stepBase, gpHardCap) : stepBase) : base;
   int nl = ArraySize(mq_dot(s).lab);
   double labU = nl > 1 ? mq_dot(s).lab[0] + mq_dot(s).lab[nl - 1] : (nl == 1 ? mq_dot(s).lab[0] : 1.0);
   int oscNd = base > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((base - mq_dot(s).oscP) / (base * xr) - 1e-9))) : 1;
   rec = ((gpRec == REC_CRA || gpRec == REC_CRB) && mq_dot(s).crN >= 2 && mq_dot(s).crN % 2 == 0) || (CrkFam() && mq_dot(s).crW && mq_dot(s).crL > 0) || (gpRec == REC_CRD && mq_dot(s).crN >= 2 && (mq_dot(s).crN - 2) % 3 == 0);
   if(rec && PrOn() && InpCrkPr == CPR_WAIT && (mq_dot(s).crWait || mq_dot(s).crNeedL)) rec = false;
   double pf = PrOn() && InpCrkPr == CPR_PCT ? InpCrkPrPct / 100.0 : 1.0;
   double r = base + add;
   switch(gpRec)
   {
      case REC_LAB:   r = base * labU; break;
      case REC_GMART: r = base * MathPow(InpRecMult, MathMin(mq_dot(s).recLosses, 200)) + base * mq_dot(s).recLosses; break;
      case REC_PAR:   r = base * MathPow(2.0, mq_dot(s).parWins); break;
      case REC_RDALE: r = base * mq_dot(s).rdUnits; break;
      case REC_DELAY: r = mq_dot(s).recLosses >= InpDelayN ? base + mq_dot(s).recPool / MathMax(1, InpRecN) : base; break;
      case REC_EQPCT: r = mq_dot(s).eq * InpEqPct / 100.0; break;
      case REC_OSC:   r = base * MathMin(mq_dot(s).oscU, oscNd); break;
      case REC_MART:  r = base * MathPow(InpRecMult, MathMin(mq_dot(s).recLosses, 200)); break;
      case REC_FIB:   r = base * (mq_dot(s).recLosses == 0 ? 1.0 : fb); break;
      case REC_DALE:  r = base * mq_dot(s).dUnits; break;
      case REC_C:
      case REC_CS:    r = MathMax(baseC, mq_dot(s).carried / MathMax(1, InpCSplit)); break;
      case REC_CRA:   r = rec ? MathMax(base, mq_dot(s).crL / xr) : base; break;
      case REC_CRB:   r = rec ? MathMax(base, mq_dot(s).crL / MathMax(1, InpCSplit) / xr) : base; break;
      case REC_CRC:   r = rec ? MathMax(base, mq_dot(s).crL / mq_dot(s).crP * pf / xr) : base; break;
      case REC_CRD:   r = rec ? MathMax(base, mq_dot(s).crL / xr) : base; break;
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
   double sd = F * mq_dot(s).sl / 100.0, baseC = 0; bool rec = false;
   if(FBase(s, sd) <= 0) return 0;
   double r = FRaw(s, sd, rec, baseC);
   if(gpCapOn && r > gpHardCap) r = gpCapAction == CAP_STOP ? -1 : gpCapAction == CAP_RESET ? MathMin(baseC, gpHardCap) : gpHardCap;
   if(r > 0 && mq_dot(s).eq > 0) r = MathMin(r, mq_dot(s).eq * InpLev * (sd + Costs()) / F);
   return r;
}
void RecReset(Strat &s)
{
   mq_dot(s).recPool = 0; mq_dot(s).recLosses = 0; mq_dot(s).dUnits = 1; mq_dot(s).carried = 0; ArrayResize(mq_dot(s).lab, 3); mq_dot(s).lab[0] = 1.0; mq_dot(s).lab[1] = 2.0; mq_dot(s).lab[2] = 3.0;
   mq_dot(s).parWins = 0; mq_dot(s).rdUnits = 1; mq_dot(s).oscU = 1; mq_dot(s).oscP = 0; mq_dot(s).crL = 0; mq_dot(s).crN = 0; mq_dot(s).crRecT = false; mq_dot(s).crW = false; mq_dot(s).crP = MathMax(1, InpCrkCn);
   mq_dot(s).crF = 0; mq_dot(s).crWait = false; mq_dot(s).crWW = 0; mq_dot(s).crNeedL = false;
}
//--- sizing at an entry (the cap's start again / stop change the state): false = no trade
//--- v1.1 monthly restart: the money starts again (the loss recovery; the closed profit the ladder / Crooks J / Rule C split count from)
void MmMonthReset(Strat &s) { RecReset(s); mq_dot(s).n0 = mq_dot(s).net; mq_dot(s).peakNet = 0; }
bool MmOpen(Strat &s, double F)
{
   if(gpMRestart && mq_dot(s).curM != mq_dot(s).mKey) { if(mq_dot(s).mKey >= 0) MmMonthReset(s); mq_dot(s).mKey = mq_dot(s).curM; }   // v1.1: the first trade of a new month: fresh money
   double sd = F * mq_dot(s).sl / 100.0;
   mq_dot(s).bR = FBase(s, sd);
   if(mq_dot(s).bR <= 0) { mq_dot(s).risk = 0; mq_dot(s).units = 0; return false; }   // no base (an empty account): no trade
   bool rec = false; double baseC = 0;
   double r = FRaw(s, sd, rec, baseC);
   bool take = true;
   mq_dot(s).crRecT = rec;
   if(gpCapOn && r > gpHardCap)
   {
      if(gpCapAction == CAP_STOP) { mq_dot(s).stopped = true; mq_dot(s).stopWhy = "stopped by the hard cap"_mq; mq_dot(s).capStp = true; take = false; }
      else if(gpCapAction == CAP_RESET) { RecReset(s); r = MathMin(baseC, gpHardCap); }
      else r = gpHardCap;
   }
   if(take && mq_dot(s).eq > 0) r = MathMin(r, mq_dot(s).eq * InpLev * (sd + Costs()) / F);
   mq_dot(s).risk = take ? r : 0;
   mq_dot(s).units = take ? r / ((sd + Costs()) * Vpu()) : 0;
   return take && mq_dot(s).units > 0;
}
//--- a closed trade's $ result: the rule's state after the trade
void MmBook(Strat &s, double pnl)
{
   mq_dot(s).eq += pnl; mq_dot(s).net += pnl; mq_dot(s).pkEq = MathMax(mq_dot(s).pkEq, mq_dot(s).eq); mq_dot(s).ddU = MathMax(mq_dot(s).ddU, mq_dot(s).pkEq - mq_dot(s).eq);
   if(mq_dot(s).pkEq > 0) mq_dot(s).ddP = MathMax(mq_dot(s).ddP, (mq_dot(s).pkEq - mq_dot(s).eq) / mq_dot(s).pkEq);
   mq_dot(s).peakNet = MathMax(mq_dot(s).peakNet, mq_dot(s).net - mq_dot(s).n0);
   if(mq_dot(s).eq <= 0) { mq_dot(s).stopped = true; mq_dot(s).stopWhy = "account blown"_mq; }
   bool win = pnl > 0;
   mq_dot(s).carried = MathMax(0.0, mq_dot(s).carried - pnl);
   int nl = ArraySize(mq_dot(s).lab);
   if(win)
   {
      mq_dot(s).recPool = MathMax(0.0, mq_dot(s).recPool - pnl); mq_dot(s).recLosses = mq_dot(s).recPool > 0 ? mq_dot(s).recLosses : 0;
      mq_dot(s).dUnits = MathMax(1, mq_dot(s).dUnits - 1); mq_dot(s).rdUnits++; mq_dot(s).parWins = mq_dot(s).parWins + 1 >= InpParN ? 0 : mq_dot(s).parWins + 1;
      if(nl <= 2) { ArrayResize(mq_dot(s).lab, 3); mq_dot(s).lab[0] = 1.0; mq_dot(s).lab[1] = 2.0; mq_dot(s).lab[2] = 3.0; }
      else { for(int q = 0; q < nl - 2; q++) mq_dot(s).lab[q] = mq_dot(s).lab[q + 1]; ArrayResize(mq_dot(s).lab, nl - 2); }
   }
   else
   {
      mq_dot(s).recPool += -pnl; mq_dot(s).recLosses++; mq_dot(s).dUnits++; mq_dot(s).rdUnits = MathMax(1, mq_dot(s).rdUnits - 1); mq_dot(s).parWins = 0;
      double used = nl > 1 ? mq_dot(s).lab[0] + mq_dot(s).lab[nl - 1] : (nl == 1 ? mq_dot(s).lab[0] : 1.0);
      ArrayResize(mq_dot(s).lab, nl + 1); mq_dot(s).lab[nl] = used;
   }
   mq_dot(s).oscP += pnl;
   if(mq_dot(s).oscP >= mq_dot(s).bR) { mq_dot(s).oscU = 1; mq_dot(s).oscP = 0; } else if(win) mq_dot(s).oscU++;
   bool lastPart = mq_dot(s).crP == 1;
   mq_dot(s).crL = MathMax(0.0, mq_dot(s).crL - pnl);
   if(gpRec == REC_CRG) { bool lg = false; double lb = 0, lc = 0; FLad(s, mq_dot(s).bR, lg, lb, lc); mq_dot(s).crL = MathMin(mq_dot(s).crL, InpCrkGX * lb); }
   if(mq_dot(s).crL < 0.01 || ((gpRec == REC_CRA || gpRec == REC_CRD) && win && mq_dot(s).crRecT))
   {
      mq_dot(s).crL = 0; mq_dot(s).crN = 0; mq_dot(s).crP = MathMax(1, InpCrkCn); mq_dot(s).crF = 0; mq_dot(s).crWait = false; mq_dot(s).crWW = 0; mq_dot(s).crNeedL = false;
   }
   else
   {
      mq_dot(s).crN++;
      mq_dot(s).crP = !win ? MathMax(1, InpCrkCn) : (mq_dot(s).crRecT ? MathMax(1, mq_dot(s).crP - 1) : mq_dot(s).crP);
      if(PrOn())
      {
         if(mq_dot(s).crWait)
         {
            mq_dot(s).crWW = win ? mq_dot(s).crWW + 1 : 0;
            if(mq_dot(s).crWW >= InpCrkPrM) { mq_dot(s).crWait = false; mq_dot(s).crWW = 0; mq_dot(s).crNeedL = true; }
         }
         else if(mq_dot(s).crNeedL && !win) mq_dot(s).crNeedL = false;
         if(mq_dot(s).crRecT && win)
         {
            mq_dot(s).crF = 0;
            if(InpCrkPr == CPR_PCT && lastPart) { mq_dot(s).crL = 0; mq_dot(s).crN = 0; mq_dot(s).crP = MathMax(1, InpCrkCn); }
         }
         else if(mq_dot(s).crRecT)
         {
            mq_dot(s).crF++;
            if(mq_dot(s).crF >= InpCrkPrN)
            {
               mq_dot(s).crF = 0;
               if(InpCrkPr == CPR_FORGET || InpCrkPr == CPR_PCT) { mq_dot(s).crL = 0; mq_dot(s).crN = 0; mq_dot(s).crP = MathMax(1, InpCrkCn); }
               else if(InpCrkPr == CPR_WAIT) { mq_dot(s).crWait = true; mq_dot(s).crWW = 0; mq_dot(s).crNeedL = false; }
            }
         }
      }
   }
   mq_dot(s).crW = win;
}

//--- the trade rules on one strategy (pine_twin2.Strat: openAt / closeAt / doBE / doSV / trail / up / dn / onBar)
string RsnTxt(int r) { return r == 1 ? "TP"_mq : r == 2 ? "SL"_mq : r == 3 ? "BE"_mq : r == 4 ? "SALV"_mq : r == 5 ? "TRAIL"_mq : r == 6 ? "TIME"_mq : r == 7 ? "WKND"_mq : "OUT"_mq; }
void DoBE(Strat &s) { mq_dot(s).beOn = true; if(mq_dot(s).F > mq_dot(s).SLp) mq_dot(s).SLp = mq_dot(s).F; gDirty = true; }
void DoSV(Strat &s) { mq_dot(s).svOn = true; mq_dot(s).TPp = mq_dot(s).F; gDirty = true; }
void Trail(Strat &s)
{
   if(gpTrD > 0 && mq_dot(s).hi >= mq_dot(s).F * (1.0 + gpTrA / 100.0))
   {
      double tl = mq_dot(s).hi * (1.0 - gpTrD / 100.0);
      if(tl > mq_dot(s).SLp) { mq_dot(s).SLp = tl; mq_dot(s).trOn = true; gDirty = true; }
   }
}
bool CanEnter(Strat &s, bool okb) { return okb && !gNoEntry && !mq_dot(s).pos && !mq_dot(s).stopped && (gpMaxDay <= 0 || mq_dot(s).dCnt < gpMaxDay); }
void StatsAdd(Strat &s, int rsn, double usd)
{
   mq_dot(s).n++; if(usd > 0) { mq_dot(s).nW++; mq_dot(s).gw += usd; } else mq_dot(s).gl -= usd;
   if(rsn == 2) { mq_dot(s).st++; mq_dot(s).mst = MathMax(mq_dot(s).mst, mq_dot(s).st); } else if(rsn == 1) mq_dot(s).st = 0;
   mq_dot(s).cum += usd; mq_dot(s).pk = MathMax(mq_dot(s).pk, mq_dot(s).cum); mq_dot(s).dd = MathMax(mq_dot(s).dd, mq_dot(s).pk - mq_dot(s).cum);
   if(rsn == 1) mq_dot(s).nTP++; else if(rsn == 2) mq_dot(s).nSL++; else if(rsn == 3) mq_dot(s).nBE++; else if(rsn == 4) mq_dot(s).nSV++; else mq_dot(s).nOth++;
}
void OpenAt(Strat &s, double px, datetime T)
{
   if(!MmOpen(s, px)) return;
   mq_dot(s).pos = true; mq_dot(s).F = px; mq_dot(s).SLp = px * (1.0 - mq_dot(s).sl / 100.0); mq_dot(s).TPp = px * (1.0 + mq_dot(s).tp / 100.0);
   mq_dot(s).BEl = px * (1.0 + mq_dot(s).be / 100.0); mq_dot(s).SVl = px * (1.0 - mq_dot(s).sv / 100.0); mq_dot(s).beOn = false; mq_dot(s).svOn = false; mq_dot(s).trOn = false; mq_dot(s).hi = px;
   mq_dot(s).eTime = T; mq_dot(s).cnt = true; mq_dot(s).dCnt++;
   if(!BrokerOpen(s)) { mq_dot(s).pos = false; mq_dot(s).cnt = false; mq_dot(s).dCnt--; return; }
   Note(s, "BUY "_mq + DoubleToString(mq_dot(s).lots, 2) + " lot at "_mq + DoubleToString(px, _Digits) + " | SL "_mq + DoubleToString(mq_dot(s).SLp, _Digits) + " TP "_mq + DoubleToString(mq_dot(s).TPp, _Digits) +
        " | risk "_mq + DoubleToString(mq_dot(s).risk, 2), true);
}
void CloseAt(Strat &s, double px, int rsn, datetime T)
{
   double model = mq_dot(s).units * (px - mq_dot(s).F - Costs()) * Vpu(), usd = model;
   if(!gSim && !BrokerClose(s, model, usd)) { mq_dot(s).exitDue = rsn; mq_dot(s).exitPx = px; return; }   // refused: the trade stays, retried
   mq_dot(s).pos = false; mq_dot(s).exitDue = 0; gDirty = true;
   if(mq_dot(s).cnt) MmBook(s, usd);
   StatsAdd(s, rsn, usd);
   if(gSim)
   {
      int k = gSimN * 7; ArrayResize(gSimLog, k + 7, 70000);
      gSimLog[k] = mq_dot(s).id; gSimLog[k + 1] = (double)mq_dot(s).eTime; gSimLog[k + 2] = mq_dot(s).F; gSimLog[k + 3] = (double)T; gSimLog[k + 4] = px; gSimLog[k + 5] = rsn; gSimLog[k + 6] = mq_dot(s).risk;
      gSimN++;
   }
   mq_dot(s).cnt = false; mq_dot(s).ticket = 0; mq_dot(s).lastUsd = usd; mq_dot(s).lastRsn = rsn;
   Note(s, "EXIT "_mq + RsnTxt(rsn) + " at "_mq + DoubleToString(px, _Digits) + " | "_mq + (usd >= 0 ? "+"_mq : ""_mq) + DoubleToString(usd, 2), true);
}
void Up(Strat &s, double x, double y, bool okb, datetime T)
{
   for(int g = 0; g < 8; g++)
   {
      double best = 0; int ev = 0;
      if(mq_dot(s).pos && mq_dot(s).exitDue == 0)
      {
         if(x < mq_dot(s).TPp && mq_dot(s).TPp <= y) { best = mq_dot(s).TPp; ev = 1; }
         if(mq_dot(s).be > 0 && !mq_dot(s).beOn && !mq_dot(s).svOn && x < mq_dot(s).BEl && mq_dot(s).BEl <= y && (ev == 0 || mq_dot(s).BEl < best)) { best = mq_dot(s).BEl; ev = 2; }
      }
      if(gpEntry == ENT_STOP && mq_dot(s).lvlOn && x < mq_dot(s).E && mq_dot(s).E <= y && (ev == 0 || mq_dot(s).E < best)) { best = mq_dot(s).E; ev = 3; }
      if(ev == 0) break;
      if(ev == 1) CloseAt(s, mq_dot(s).TPp, mq_dot(s).svOn ? 4 : 1, T);
      else if(ev == 2) DoBE(s);
      else { if(CanEnter(s, okb)) OpenAt(s, mq_dot(s).E, T); mq_dot(s).lvlOn = false; }
   }
   if(mq_dot(s).pos && y > mq_dot(s).hi) mq_dot(s).hi = y;
}
void Dn(Strat &s, double x, double y, datetime T)
{
   if(mq_dot(s).pos && mq_dot(s).exitDue == 0) Trail(s);
   for(int g = 0; g < 8; g++)
   {
      double best = 0; int ev = 0;
      if(mq_dot(s).pos && mq_dot(s).exitDue == 0)
      {
         if(y <= mq_dot(s).SLp && mq_dot(s).SLp < x) { best = mq_dot(s).SLp; ev = 1; }
         if(mq_dot(s).sv > 0 && !mq_dot(s).svOn && !mq_dot(s).beOn && y <= mq_dot(s).SVl && mq_dot(s).SVl < x && (ev == 0 || mq_dot(s).SVl > best)) { best = mq_dot(s).SVl; ev = 2; }
      }
      if(ev == 0) break;
      if(ev == 1) CloseAt(s, mq_dot(s).SLp, mq_dot(s).trOn ? 5 : (mq_dot(s).beOn ? 3 : 2), T);
      else DoSV(s);
   }
}
void Seg(Strat &s, double x, double y, bool okb, datetime T) { if(y > x) Up(s, x, y, okb, T); else if(y < x) Dn(s, x, y, T); }
//--- the open of a 1-minute bar (a jump from the previous close): exits first, then BE / salvage, then a breakout at the open
void BarOpen(Strat &s, double o, double pc, bool okb, bool wk, int dno, datetime T)
{
   if(mq_dot(s).dPrev < 0 || dno != mq_dot(s).dPrev) { mq_dot(s).dCnt = 0; mq_dot(s).dPrev = dno; }
   mq_dot(s).curM = dno / 100;                                                    // v1.1: this candle's month (your time zone)
   if(gpMRestart && mq_dot(s).capStp && mq_dot(s).mKey >= 0 && mq_dot(s).curM != mq_dot(s).mKey) { mq_dot(s).stopped = false; mq_dot(s).capStp = false; mq_dot(s).stopWhy = ""_mq; }   // a hard-cap stop ends with the month
   if(gpMRestart && !mq_dot(s).pos && mq_dot(s).mKey >= 0 && mq_dot(s).curM != mq_dot(s).mKey) { MmMonthReset(s); mq_dot(s).mKey = mq_dot(s).curM; }   // flat at a new month: the money starts again now (the next lots shown are right)
   if(mq_dot(s).pos && mq_dot(s).exitDue == 0)
   {
      Trail(s);
      int xr = 0;
      if(o >= mq_dot(s).TPp) xr = mq_dot(s).svOn ? 4 : 1;
      else if(o <= mq_dot(s).SLp) xr = mq_dot(s).trOn ? 5 : (mq_dot(s).beOn ? 3 : 2);
      else if(gpTExitH > 0 && (mql_long)UtcOf(T) >= (mql_long)UtcOf(mq_dot(s).eTime) + (mql_long)MathRound(gpTExitH * 3600.0)) xr = 6;   // real hours (UTC): not shifted by the broker clock's summer time
      else if(wk) xr = 7;
      if(xr > 0) CloseAt(s, o, xr, T);
      else
      {
         if(mq_dot(s).be > 0 && !mq_dot(s).beOn && !mq_dot(s).svOn && o >= mq_dot(s).BEl) DoBE(s);
         else if(mq_dot(s).sv > 0 && !mq_dot(s).svOn && !mq_dot(s).beOn && o <= mq_dot(s).SVl) DoSV(s);
         if(o > mq_dot(s).hi) mq_dot(s).hi = o;
      }
   }
   if(gpEntry == ENT_STOP && mq_dot(s).lvlOn && pc > 0 && pc < mq_dot(s).E && o >= mq_dot(s).E)
   {
      if(CanEnter(s, okb)) OpenAt(s, o, T);
      mq_dot(s).lvlOn = false;
   }
}
//--- the close of a 1-minute bar: the candle-close entry
void BarClose(Strat &s, double c, bool okb, datetime T)
{
   if(gpEntry != ENT_CLOSE || !mq_dot(s).lvlOn) return;
   if(mq_dot(s).armed && c >= mq_dot(s).E) { if(CanEnter(s, okb)) OpenAt(s, c, T); mq_dot(s).lvlOn = false; }
   else if(c < mq_dot(s).E) mq_dot(s).armed = true;
}
//--- one 1-minute bar for one strategy, in three steps: BarEnd (the previous bar's close), the candles of its timeframe that closed
//--- (PushTf, done by the caller), BarBegin (the open), then Move for every later price
void BarEnd(Strat &s, BarCtx &c) { if(mq_dot(c).T > 0) BarClose(s, mq_dot(c).last, mq_dot(c).okb, mq_dot(c).T); }
void CtxBegin(BarCtx &c, datetime T, double o) { mq_dot(c).prevC = mq_dot(c).T > 0 ? mq_dot(c).last : 0; mq_dot(c).T = T; Filters(T, mq_dot(c).okb, mq_dot(c).wk, mq_dot(c).dno); mq_dot(c).last = o; }
void BarBegin(Strat &s, BarCtx &c, double o) { BarOpen(s, o, mq_dot(c).prevC, mq_dot(c).okb, mq_dot(c).wk, mq_dot(c).dno, mq_dot(c).T); }
void Move(Strat &s, BarCtx &c, double y) { Seg(s, mq_dot(c).last, y, mq_dot(c).okb, mq_dot(c).T); }

//--- notes ------------------------------------------------------------------------------------------------------------------------
void Note(Strat &s, string m, bool loud)
{
   if(gSim || (gNoEntry && !loud)) return;
   gDirty = true;
   string t = "FBG S"_mq + IntegerToString(mq_dot(s).id) + (gNoEntry ? " (catch-up) "_mq : " "_mq) + m;
   Print(t);
   if(loud && !gNoEntry && InpAlerts) Alert(_Symbol + " "_mq + t);
   if(loud && !gNoEntry && InpPush) SendNotification(_Symbol + " "_mq + t);
}

//--- broker -----------------------------------------------------------------------------------------------------------------------
double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
//--- lots for a number of units: to the nearest lot step, at least the minimum lot, at most the maximum
double LotsOf(double units)
{
   double st = LotStep(), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double v = MathRound(units / Contract() / st + 1e-9) * st;
   if(v < vmin) v = vmin;
   if(vmax > 0 && v > vmax) v = vmax;
   return NormalizeDouble(v, 8);
}
//--- the strategy's position at the broker (its magic number), newest first; 0 = none
ulong FindPos(Strat &s)
{
   ulong best = 0; datetime bt = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0 || PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic + mq_dot(s).id) continue;
      datetime t = (datetime)PositionGetInteger(POSITION_TIME);
      if(best == 0 || t > bt) { best = tk; bt = t; }
   }
   return best;
}
//--- a market buy for the strategy's new trade (the SL / TP are the rules' levels; one too close to the price waits, the EA watches it)
bool BrokerOpen(Strat &s)
{
   if(gSim) { mq_dot(s).ticket = 0; mq_dot(s).lots = mq_dot(s).units / Contract(); return true; }
   if(gNoEntry) return false;
   double v = LotsOf(mq_dot(s).units), st = LotStep(), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mg = 0;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double lossLot = (mq_dot(s).F - mq_dot(s).SLp + Costs()) * Vpu() * Contract();          // the stop-out loss of 1 lot
   if(gpCapOn && lossLot > 0 && v * lossLot > gpHardCap + 1e-9) v = MathFloor(gpHardCap / lossLot / st + 1e-9) * st;   // rounding never past the cap
   if(OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, 1.0, ask, mg) && mg > 0)
      v = MathMin(v, MathFloor(AccountInfoDouble(ACCOUNT_MARGIN_FREE) / mg / st + 1e-9) * st);           // what the free margin carries
   v = NormalizeDouble(v, 8);
   if(v < vmin) { Print("FBG S"_mq, mq_dot(s).id, ": the size is below the minimum lot (hard cap or free margin): trade skipped."_mq); return false; }
   double md = MinDist() + TickSize();
   double sl = NormP(mq_dot(s).SLp), tp = NormP(mq_dot(s).TPp);
   if(sl > bid - md) sl = 0;
   if(tp < bid + md) tp = 0;
   mq_dot(trade).SetExpertMagicNumber((ulong)(InpMagic + mq_dot(s).id));
   if(!mq_dot(trade).Buy(v, _Symbol, 0, sl, tp, "FBG S"_mq + IntegerToString(mq_dot(s).id)))
   {
      Print("FBG S"_mq, mq_dot(s).id, ": buy failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
      return false;
   }
   uint rc = mq_dot(trade).ResultRetcode();
   if(rc != TRADE_RETCODE_DONE && rc != TRADE_RETCODE_DONE_PARTIAL && rc != TRADE_RETCODE_PLACED)
   {
      Print("FBG S"_mq, mq_dot(s).id, ": buy not done: "_mq, mq_dot(trade).ResultRetcodeDescription());
      return false;
   }
   ulong tk = mq_dot(trade).ResultOrder();
   if(tk == 0 || !PositionSelectByTicket(tk)) tk = FindPos(s);
   if(tk == 0) { Print("FBG S"_mq, mq_dot(s).id, ": the position was not found after the buy."_mq); return false; }
   mq_dot(s).ticket = tk; mq_dot(s).lots = v; gDirty = true;
   return true;
}
//--- the real result of a closed position (all its deals: profit, commission, swap, fee); false = not closed yet / not found
bool PosResult(ulong pos, double &usd, double &px, int &why)
{
   usd = 0; px = 0; why = -1;
   if(pos == 0 || !HistorySelectByPosition(pos)) return false;
   bool out = false;
   for(int i = 0; i < HistoryDealsTotal(); i++)
   {
      ulong d = HistoryDealGetTicket(i);
      if(d == 0) continue;
      usd += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP) + HistoryDealGetDouble(d, DEAL_FEE);
      mql_long en = HistoryDealGetInteger(d, DEAL_ENTRY);
      if(en == DEAL_ENTRY_OUT || en == DEAL_ENTRY_OUT_BY) { out = true; px = HistoryDealGetDouble(d, DEAL_PRICE); why = (int)HistoryDealGetInteger(d, DEAL_REASON); }
   }
   return out;
}
//--- close the strategy's position (the rules exit) and read its real result (the model's result if its deals are not there yet).
//--- false: the broker refused the close (the trade stays open, retried on the next ticks)
bool BrokerClose(Strat &s, double model, double &usd)
{
   usd = model;
   if(mq_dot(s).ticket == 0) return true;
   if(PositionSelectByTicket(mq_dot(s).ticket))
   {
      mq_dot(trade).SetExpertMagicNumber((ulong)(InpMagic + mq_dot(s).id));
      bool sent = mq_dot(trade).PositionClose(mq_dot(s).ticket);
      uint rc = mq_dot(trade).ResultRetcode();
      bool done = sent && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL || rc == TRADE_RETCODE_PLACED);
      if(!done && PositionSelectByTicket(mq_dot(s).ticket))           // refused (requote, market closed, ...): the trade stays, retried
      {
         Print("FBG S"_mq, mq_dot(s).id, ": close refused ("_mq, mq_dot(trade).ResultRetcodeDescription(), "): retried in a few seconds."_mq);
         return false;
      }
   }
   double px = 0; int why = -1;
   bool got = PosResult(mq_dot(s).ticket, usd, px, why);
   for(int tries = 0; !got && tries < 3; tries++) { Sleep(50); got = PosResult(mq_dot(s).ticket, usd, px, why); }
   if(!got)
   {
      if(PositionSelectByTicket(mq_dot(s).ticket)) return false;      // still open (a partial close): the rest on the next try
      usd = model;                                            // gone, its deals not readable yet: the rules' result
   }
   return true;
}
//--- the broker closed a position itself (its SL / TP, a stop-out, by hand): book it as the rules' exit of that kind
datetime gExAt[12];
void Reconcile()
{
   if(gSim) return;
   for(int i = 0; i < 12; i++)
   {
      if(mq_dot(S[i]).pos && mq_dot(S[i]).exitDue > 0)                       // a refused close: again, every 5 seconds
      {
         if(TimeLocal() - gExAt[i] >= 5) { gExAt[i] = TimeLocal(); CloseAt(S[i], mq_dot(S[i]).exitPx, mq_dot(S[i]).exitDue, TimeCurrent()); }
         continue;
      }
      if(!mq_dot(S[i]).pos || mq_dot(S[i]).ticket == 0 || PositionSelectByTicket(mq_dot(S[i]).ticket)) continue;
      double usd = 0, px = 0; int why = -1;
      if(!PosResult(mq_dot(S[i]).ticket, usd, px, why)) continue;     // the deals are not in the history yet: next tick
      int rsn = why == DEAL_REASON_SL ? (mq_dot(S[i]).trOn ? 5 : (mq_dot(S[i]).beOn ? 3 : 2)) : why == DEAL_REASON_TP ? (mq_dot(S[i]).svOn ? 4 : 1) : 8;
      CloseAt(S[i], px > 0 ? px : SymbolInfoDouble(_Symbol, SYMBOL_BID), rsn, TimeCurrent());
      gDirty = true;
   }
}
//--- the broker's SL / TP follow the rules' levels (BE, salvage, trailing); a level too close to the price stays with the EA.
//--- A change the broker refused is tried again after 10 seconds (not on every tick)
double   gSyS[12], gSyT[12]; datetime gSyAt[12];
void Sync()
{
   if(gSim) return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ts = TickSize(), md = MinDist() + ts;
   for(int i = 0; i < 12; i++)
   {
      if(!mq_dot(S[i]).pos || mq_dot(S[i]).ticket == 0 || !PositionSelectByTicket(mq_dot(S[i]).ticket)) continue;
      double cs = PositionGetDouble(POSITION_SL), ct = PositionGetDouble(POSITION_TP);
      double ws = NormP(mq_dot(S[i]).SLp), wt = NormP(mq_dot(S[i]).TPp);
      double ns = MathAbs(ws - cs) > ts * 0.5 && ws <= bid - md ? ws : cs;
      double nt = MathAbs(wt - ct) > ts * 0.5 && wt >= bid + md ? wt : ct;
      if(MathAbs(ns - cs) <= ts * 0.5 && MathAbs(nt - ct) <= ts * 0.5) continue;
      if(ns == gSyS[i] && nt == gSyT[i] && TimeCurrent() - gSyAt[i] < 10) continue;
      gSyS[i] = ns; gSyT[i] = nt; gSyAt[i] = TimeCurrent();
      mq_dot(trade).SetExpertMagicNumber((ulong)(InpMagic + mq_dot(S[i]).id));
      if(!mq_dot(trade).PositionModify(mq_dot(S[i]).ticket, ns, nt)) Print("FBG S"_mq, mq_dot(S[i]).id, ": SL / TP change failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
   }
}

//--- the broker's clock -----------------------------------------------------------------------------------------------------------
int    gTzMode = SRV_NYCLOSE; double gTzFix = 2.0;
double RuleGMT(int md, datetime server)
{
   MqlDateTime d; TimeToStruct(server, d);
   if(md == SRV_EET)
   {
      int es = LastSunday(mq_dot(d).year, 3), ee = LastSunday(mq_dot(d).year, 10);
      bool sum = (mq_dot(d).mon > 3 && mq_dot(d).mon < 10) || (mq_dot(d).mon == 3 && mq_dot(d).day >= es) || (mq_dot(d).mon == 10 && mq_dot(d).day < ee);
      return sum ? 3.0 : 2.0;
   }
   int ds = NthSunday(mq_dot(d).year, 3, 2), de = NthSunday(mq_dot(d).year, 11, 1);
   bool dst = (mq_dot(d).mon > 3 && mq_dot(d).mon < 11) || (mq_dot(d).mon == 3 && mq_dot(d).day >= ds) || (mq_dot(d).mon == 11 && mq_dot(d).day < de);
   return dst ? 3.0 : 2.0;
}
double SrvGMT(datetime server)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;
   if(md == SRV_FIXED) return InpServerTz == SRV_AUTO ? gTzFix : InpServerGMT;
   return RuleGMT(md, server);
}
//--- Auto: the summer-time rule that gives the broker's offset now (US first, as most FX brokers; then EU), else that offset fixed
void TzPick()
{
   if(InpServerTz != SRV_AUTO || MQLInfoInteger(MQL_TESTER) != 0 || TerminalInfoInteger(TERMINAL_CONNECTED) == 0) return;
   datetime sv = TimeTradeServer(), g = TimeGMT();
   if(sv <= 0 || g <= 0) return;
   double d = MathRound((double)(sv - g) / 1800.0) / 2.0;
   if(MathAbs(d) > 14) return;
   if(RuleGMT(SRV_NYCLOSE, sv) == d) gTzMode = SRV_NYCLOSE;
   else if(RuleGMT(SRV_EET, sv) == d) gTzMode = SRV_EET;
   else { gTzMode = SRV_FIXED; gTzFix = d; }
}

//--- replay of the 1-minute history (warm-up at a fresh start, catch-up after a restart) ------------------------------------------------
//--- one strategy over the closed 1-minute bars [from, to): the candles of its timeframe that closed by each bar are pushed first
//--- (those closed by pushedTo were pushed before). No new trade opens (gNoEntry); an open trade follows the rules. Returns the bars replayed.
int ReplayStrat(Strat &s, datetime from, datetime to, datetime pushedTo, BarCtx &c, bool closePrev)
{
   MqlArr<MqlRates> m1, tf;
   if(to <= from) return 0;
   int n = CopyRates(_Symbol, PERIOD_M1, (datetime)(from - 7 * 86400), (datetime)(to - 1), m1);   // with the bar before the replay (its close)
   if(n <= 0) return 0;
   int i0 = 0;
   while(i0 < n && mq_dot(m1[i0]).time < from) i0++;
   if(i0 > 0)                                            // the bar before: its close is the previous close of the first bar replayed
   {
      mq_dot(c).T = mq_dot(m1[i0 - 1]).time; mq_dot(c).last = mq_dot(m1[i0 - 1]).close; Filters(mq_dot(c).T, mq_dot(c).okb, mq_dot(c).wk, mq_dot(c).dno);
   }
   bool skipEnd = !closePrev;                            // a fresh start: the bar before closed before the buy stop started
   int ps = PeriodSeconds(mq_dot(s).tf);
   int nt = CopyRates(_Symbol, mq_dot(s).tf, (datetime)(pushedTo - ps), (datetime)(to - 1), tf);
   int j = 0;
   while(j < nt && mq_dot(tf[j]).time + ps <= pushedTo) j++;    // closed before the replay: already pushed
   bool ne = gNoEntry; gNoEntry = true;
   for(int i = i0; i < n; i++)
   {
      datetime T = mq_dot(m1[i]).time;
      if(T >= to) break;
      if(!skipEnd) BarEnd(s, c);
      skipEnd = false;
      while(j < nt && mq_dot(tf[j]).time + ps <= T) { PushTf(s, mq_dot(tf[j]).high, mq_dot(tf[j]).time, T, true); j++; }
      CtxBegin(c, T, mq_dot(m1[i]).open);
      BarBegin(s, c, mq_dot(m1[i]).open);
      double o = mq_dot(m1[i]).open, h = mq_dot(m1[i]).high, lo = mq_dot(m1[i]).low, cl = mq_dot(m1[i]).close;
      bool hf = (h - o) < (o - lo);
      double a = hf ? h : lo, b = hf ? lo : h;
      Move(s, c, a); mq_dot(c).last = a; Move(s, c, b); mq_dot(c).last = b; Move(s, c, cl); mq_dot(c).last = cl;
   }
   gNoEntry = ne;
   return n;
}
//--- live: the candle of the strategy's timeframe that holds the last minute processed (PushLive pushes the ones after it as they close)
void TfMark(Strat &s, datetime lastT)
{
   int sh = lastT > 0 ? iBarShift(_Symbol, mq_dot(s).tf, lastT, false) : 0;
   datetime t = sh >= 0 ? iTime(_Symbol, mq_dot(s).tf, sh) : 0;
   mq_dot(s).tfLast = t > 0 ? t : iTime(_Symbol, mq_dot(s).tf, 0);
}
//--- a fresh start: the candles of the strategy's timeframe up to its latest swing high's start, then the 1-minute bars since (the buy
//--- stop is used up if the price went through it)
void WarmStrat(Strat &s, datetime now, BarCtx &c)
{
   MqlArr<MqlRates> tf;
   int ps = PeriodSeconds(mq_dot(s).tf);
   int nt = CopyRates(_Symbol, mq_dot(s).tf, 1, 3000, tf);      // closed candles, oldest first
   if(nt <= mq_dot(s).l + mq_dot(s).r + 1) { Print("FBG S"_mq, mq_dot(s).id, ": not enough "_mq, EnumToString(mq_dot(s).tf), " history yet ("_mq, nt, " candles)."_mq); mq_dot(s).tfLast = iTime(_Symbol, mq_dot(s).tf, 0); return; }
   // the latest swing high: pushed in a scratch copy, then again up to its start
   datetime act = 0;
   {
      int w = mq_dot(s).l + mq_dot(s).r + 1;
      for(int k = nt - 1; k >= w - 1; k--)                // newest first: candle k is the last right candle of the candidate k - r
      {
         int p = k - mq_dot(s).r; double v = mq_dot(tf[p]).high; bool ok = true;
         for(int i = 1; i <= mq_dot(s).l && ok; i++) if(mq_dot(tf[p - i]).high >= v) ok = false;
         for(int q = 1; q <= mq_dot(s).r && ok; q++) if(mq_dot(tf[p + q]).high >= v) ok = false;
         if(ok) { act = k + 1 < nt ? mq_dot(tf[k + 1]).time : mq_dot(tf[k]).time + (datetime)ps; break; }
      }
   }
   datetime from = MathMax(act, now - (datetime)(MathMax(1, InpWarmDays) * 86400));
   from = from - from % 60;
   int k0 = 0;
   bool ne = gNoEntry; gNoEntry = true;                  // quiet (no notes for old swing highs)
   for(; k0 < nt && mq_dot(tf[k0]).time + ps <= from; k0++) PushTf(s, mq_dot(tf[k0]).high, mq_dot(tf[k0]).time, mq_dot(tf[k0]).time + (datetime)ps, true);
   gNoEntry = ne;
   if(act > 0 && act < from && mq_dot(s).lvlOn)
   {
      double hm = 0;
      for(int k = 0; k < nt; k++) if(mq_dot(tf[k]).time >= act && mq_dot(tf[k]).time + ps <= from) hm = MathMax(hm, mq_dot(tf[k]).high);
      if(hm >= mq_dot(s).E) mq_dot(s).lvlOn = false;
      Print("FBG S"_mq, mq_dot(s).id, ": its buy stop started "_mq, TimeToString(act), ", before the 1-minute history read ("_mq, InpWarmDays, " days): "_mq,
            mq_dot(s).lvlOn ? "still waiting (the price stayed below it)."_mq : "used up (the price reached it)."_mq);
   }
   mq_dot(c).T = 0; mq_dot(c).last = 0; mq_dot(c).prevC = 0;
   ReplayStrat(s, from, now, from, c, false);
   TfMark(s, mq_dot(c).T);
}
//--- the trend timeframe's closed candles (EMA)
void TrendLoad()
{
   gTrSeed = false; gTrUp = false; gTrLast = 0;
   if(!gpTrnOn) return;
   MqlArr<MqlRates> r; int n = CopyRates(_Symbol, InpTrnTf, 1, 5000, r);
   for(int i = 0; i < n; i++) PushTrend(mq_dot(r[i]).close);
   gTrLast = iTime(_Symbol, InpTrnTf, 0);
}
void TrendLive()
{
   if(!gpTrnOn) return;
   datetime t0 = iTime(_Symbol, InpTrnTf, 0);
   if(t0 <= 0 || t0 <= gTrLast) return;
   if(gTrLast > 0)
   {
      MqlArr<MqlRates> r; int n = CopyRates(_Symbol, InpTrnTf, gTrLast, (datetime)(t0 - 1), r);
      if(n <= 0) return;
      for(int i = 0; i < n; i++) if(mq_dot(r[i]).time >= gTrLast && mq_dot(r[i]).time < t0) PushTrend(mq_dot(r[i]).close);
   }
   gTrLast = t0;
}
//--- live: the candles of the strategy's timeframe that closed since the last tick
void PushLive(Strat &s)
{
   datetime t0 = iTime(_Symbol, mq_dot(s).tf, 0);
   if(t0 <= 0 || t0 <= mq_dot(s).tfLast) return;
   if(mq_dot(s).tfLast > 0)
   {
      MqlArr<MqlRates> r; int n = CopyRates(_Symbol, mq_dot(s).tf, mq_dot(s).tfLast, (datetime)(t0 - 1), r);
      if(n <= 0) return;                                  // not read yet (history loading): again on the next tick
      for(int i = 0; i < n; i++) if(mq_dot(r[i]).time >= mq_dot(s).tfLast && mq_dot(r[i]).time < t0) PushTf(s, mq_dot(r[i]).high, mq_dot(r[i]).time, t0, true);
   }
   mq_dot(s).tfLast = t0;
   gDirty = true;
}

//--- restart memory -----------------------------------------------------------------------------------------------------------------
string   gSvBase = ""_mq;
bool     gIoSave = false;
MqlArr<string>   gIoN; MqlArr<double> gIoV; int gIoC = 0;
MqlArr<string>   gSvN; MqlArr<double> gSvV; int gSvC = 0;
datetime gSvT = 0;
double   gSvLast = 0;                      // the last price of the bar the EA was in when it stopped
bool     gRestored = false;
int SvVer() { return 1; }
void IoD(string n, double &x)
{
   if(gIoSave)
   {
      if(gIoC >= ArraySize(gIoN)) { ArrayResize(gIoN, gIoC + 64); ArrayResize(gIoV, gIoC + 64); }
      gIoN[gIoC] = n; gIoV[gIoC] = x; gIoC++;
   }
   else if(GlobalVariableCheck(gSvBase + n)) x = GlobalVariableGet(gSvBase + n);
}
void IoI(string n, int &x)      { double d = x; IoD(n, d); x = (int)MathRound(d); }
void IoB(string n, bool &x)     { double d = x ? 1.0 : 0.0; IoD(n, d); x = d != 0.0; }
void IoT(string n, datetime &x) { double d = (double)x; IoD(n, d); x = (datetime)(mql_long)MathRound(d); }
void IoU(string n, ulong &x)    { double hi = (double)(x >> 32), lo = (double)(x & 0xFFFFFFFF); IoD(n + "h"_mq, hi); IoD(n + "l"_mq, lo); x = ((ulong)MathRound(hi) << 32) | (ulong)MathRound(lo); }
//--- what identifies a strategy's swing highs: a change forgets its buy stop
double Fp(Strat &s) { return (double)mq_dot(s).tf * 1e6 + mq_dot(s).r * 1e3 + mq_dot(s).l + mq_dot(s).off * 1e-3; }
void StratIO(Strat &s)
{
   string p = "s"_mq + IntegerToString(mq_dot(s).id);
   double fp = Fp(s); IoD(p + "fp"_mq, fp);
   IoB(p + "lo"_mq, mq_dot(s).lvlOn); IoD(p + "lh"_mq, mq_dot(s).lvlH); IoD(p + "le"_mq, mq_dot(s).E); IoT(p + "lt"_mq, mq_dot(s).lvlT); IoT(p + "la"_mq, mq_dot(s).actT); IoB(p + "ar"_mq, mq_dot(s).armed);
   if(!gIoSave && MathAbs(fp - Fp(s)) > 1e-9) { mq_dot(s).lvlOn = false; mq_dot(s).lvlT = 0; }
   IoI(p + "xd"_mq, mq_dot(s).exitDue); IoD(p + "xp"_mq, mq_dot(s).exitPx);
   IoB(p + "ps"_mq, mq_dot(s).pos); IoD(p + "f"_mq, mq_dot(s).F); IoD(p + "sl"_mq, mq_dot(s).SLp); IoD(p + "tp"_mq, mq_dot(s).TPp); IoD(p + "be"_mq, mq_dot(s).BEl); IoD(p + "sv"_mq, mq_dot(s).SVl); IoD(p + "hi"_mq, mq_dot(s).hi);
   IoB(p + "bo"_mq, mq_dot(s).beOn); IoB(p + "so"_mq, mq_dot(s).svOn); IoB(p + "to"_mq, mq_dot(s).trOn); IoT(p + "et"_mq, mq_dot(s).eTime); IoB(p + "cn"_mq, mq_dot(s).cnt); IoU(p + "tk"_mq, mq_dot(s).ticket); IoD(p + "lv"_mq, mq_dot(s).lots);
   IoI(p + "dc"_mq, mq_dot(s).dCnt); IoI(p + "dp"_mq, mq_dot(s).dPrev); IoB(p + "st"_mq, mq_dot(s).stopped);
   int sw = mq_dot(s).stopWhy == "account blown"_mq ? 2 : mq_dot(s).stopWhy != ""_mq ? 1 : 0; IoI(p + "sw"_mq, sw);
   if(!gIoSave) mq_dot(s).stopWhy = sw == 2 ? "account blown"_mq : sw == 1 ? "stopped by the hard cap"_mq : ""_mq;
   IoD(p + "eq"_mq, mq_dot(s).eq); IoD(p + "pe"_mq, mq_dot(s).pkEq); IoD(p + "du"_mq, mq_dot(s).ddU); IoD(p + "dq"_mq, mq_dot(s).ddP); IoD(p + "nt"_mq, mq_dot(s).net); IoD(p + "pn"_mq, mq_dot(s).peakNet); IoD(p + "n0"_mq, mq_dot(s).n0); IoI(p + "mk"_mq, mq_dot(s).mKey); IoB(p + "cp"_mq, mq_dot(s).capStp);
   IoD(p + "rp"_mq, mq_dot(s).recPool); IoD(p + "ca"_mq, mq_dot(s).carried); IoD(p + "op"_mq, mq_dot(s).oscP); IoD(p + "kl"_mq, mq_dot(s).crL); IoD(p + "rk"_mq, mq_dot(s).risk); IoD(p + "un"_mq, mq_dot(s).units); IoD(p + "br"_mq, mq_dot(s).bR);
   IoI(p + "rl"_mq, mq_dot(s).recLosses); IoI(p + "dn"_mq, mq_dot(s).dUnits); IoI(p + "pw"_mq, mq_dot(s).parWins); IoI(p + "rd"_mq, mq_dot(s).rdUnits); IoI(p + "ou"_mq, mq_dot(s).oscU);
   IoI(p + "kn"_mq, mq_dot(s).crN); IoI(p + "kp"_mq, mq_dot(s).crP); IoI(p + "kf"_mq, mq_dot(s).crF); IoI(p + "kb"_mq, mq_dot(s).crWW);
   IoB(p + "kw"_mq, mq_dot(s).crW); IoB(p + "ka"_mq, mq_dot(s).crWait); IoB(p + "kc"_mq, mq_dot(s).crNeedL); IoB(p + "kr"_mq, mq_dot(s).crRecT);
   IoI(p + "n"_mq, mq_dot(s).n); IoI(p + "nw"_mq, mq_dot(s).nW); IoI(p + "n1"_mq, mq_dot(s).nTP); IoI(p + "n2"_mq, mq_dot(s).nSL); IoI(p + "n3"_mq, mq_dot(s).nBE); IoI(p + "n4"_mq, mq_dot(s).nSV); IoI(p + "n5"_mq, mq_dot(s).nOth);
   IoI(p + "ss"_mq, mq_dot(s).st); IoI(p + "sm"_mq, mq_dot(s).mst); IoD(p + "gw"_mq, mq_dot(s).gw); IoD(p + "gl"_mq, mq_dot(s).gl); IoD(p + "cu"_mq, mq_dot(s).cum); IoD(p + "pk"_mq, mq_dot(s).pk); IoD(p + "dd"_mq, mq_dot(s).dd);
   int ln = ArraySize(mq_dot(s).lab); IoI(p + "ln"_mq, ln);
   if(!gIoSave) { if(ln < 1 || ln > 2000) ln = 3; ArrayResize(mq_dot(s).lab, ln); }
   for(int q = 0; q < ln; q++) { double x = gIoSave ? mq_dot(s).lab[q] : (q < 3 ? q + 1.0 : 1.0); IoD(p + "L"_mq + IntegerToString(q), x); if(!gIoSave) mq_dot(s).lab[q] = x; }
   if(!gIoSave)
   {
      bool ok = ArraySize(mq_dot(s).lab) > 0;
      for(int q = 0; q < ArraySize(mq_dot(s).lab); q++) if(mq_dot(s).lab[q] <= 0) ok = false;
      if(!ok) { ArrayResize(mq_dot(s).lab, 3); mq_dot(s).lab[0] = 1.0; mq_dot(s).lab[1] = 2.0; mq_dot(s).lab[2] = 3.0; }
      if(mq_dot(s).crP < 1) mq_dot(s).crP = 1;
   }
}
void StateIO(bool save)
{
   gIoSave = save; gIoC = 0;
   int ver = SvVer(); IoI("ver"_mq, ver);
   datetime lt = mq_dot(gC).T, sv = TimeCurrent(); IoT("lt"_mq, lt); IoT("sv"_mq, sv);
   double cl = mq_dot(gC).last; IoD("cl"_mq, cl);
   if(!save) gSvLast = cl;
   double acc = (double)AccountInfoInteger(ACCOUNT_LOGIN); IoD("acc"_mq, acc);
   if(!save) { gSvT = lt; }
   for(int i = 0; i < 12; i++) StratIO(S[i]);
}
void StateSave(bool force)
{
   if(!InpRemember || gSim || MQLInfoInteger(MQL_TESTER) != 0 || mq_dot(gC).T <= 0) return;
   StateIO(true);
   bool ch = force || gIoC != gSvC;
   for(int q = 0; q < gIoC && !ch; q++) if(gIoN[q] != gSvN[q] || (gIoV[q] != gSvV[q] && gIoN[q] != "sv"_mq)) ch = true;
   if(!ch) return;
   for(int q = 0; q < gIoC; q++) if(force || q >= gSvC || gIoN[q] != gSvN[q] || gIoV[q] != gSvV[q]) GlobalVariableSet(gSvBase + gIoN[q], gIoV[q]);
   for(int q = gIoC; q < gSvC; q++) GlobalVariableDel(gSvBase + gSvN[q]);
   if(ArraySize(gSvN) < gIoC) { ArrayResize(gSvN, gIoC); ArrayResize(gSvV, gIoC); }
   for(int q = 0; q < gIoC; q++) { gSvN[q] = gIoN[q]; gSvV[q] = gIoV[q]; }
   gSvC = gIoC;
   GlobalVariablesFlush();
}
//--- the saved state of this symbol, magic number and account (false: none, or another account)
bool StateLoad()
{
   if(!InpRemember || MQLInfoInteger(MQL_TESTER) != 0) return false;
   if(!GlobalVariableCheck(gSvBase + "ver"_mq) || (int)MathRound(GlobalVariableGet(gSvBase + "ver"_mq)) != SvVer()) return false;
   if(!GlobalVariableCheck(gSvBase + "acc"_mq) || (mql_long)MathRound(GlobalVariableGet(gSvBase + "acc"_mq)) != AccountInfoInteger(ACCOUNT_LOGIN))
   {
      Print("Restart memory: saved for another account: starting fresh."_mq);
      return false;
   }
   StateIO(false);
   return gSvT > 0;
}
//--- after a restart: the candles up to the last minute processed, then the minutes missed (caught up)
void Restore(datetime now)
{
   for(int i = 0; i < 12; i++)
   {
      int ps = PeriodSeconds(mq_dot(S[i]).tf);
      MqlArr<MqlRates> tf; int nt = CopyRates(_Symbol, mq_dot(S[i]).tf, 1, 3000, tf);
      mq_dot(S[i]).nC = 0; int kA = 0;
      for(int k = 0; k < nt && mq_dot(tf[k]).time + ps <= gSvT; k++) { PushTf(S[i], mq_dot(tf[k]).high, mq_dot(tf[k]).time, mq_dot(tf[k]).time + (datetime)ps, false); if(mq_dot(tf[k]).time < mq_dot(S[i]).actT) kA = mq_dot(S[i]).nC; }
      mq_dot(S[i]).kAct = kA;
   }
   BarCtx c;
   MqlArr<MqlRates> b;
   double bc = CopyRates(_Symbol, PERIOD_M1, gSvT, 1, b) == 1 && mq_dot(b[0]).time == gSvT ? mq_dot(b[0]).close : 0;   // that bar's close
   for(int i = 0; i < 12; i++)
   {
      mq_dot(c).T = gSvT; mq_dot(c).last = gSvLast; mq_dot(c).prevC = 0; Filters(mq_dot(c).T, mq_dot(c).okb, mq_dot(c).wk, mq_dot(c).dno);   // the bar the EA was in when it stopped
      if(mq_dot(S[i]).ok)
      {
         if(bc > 0 && mq_dot(c).last > 0 && gSvT + 60 <= now)     // its rest: from the last price to its close (not its high / low: they may be older)
         {
            bool ne = gNoEntry; gNoEntry = true;
            Move(S[i], c, bc); mq_dot(c).last = bc;
            gNoEntry = ne;
         }
         ReplayStrat(S[i], gSvT + 60, now, gSvT, c, true);
      }
      TfMark(S[i], mq_dot(c).T > 0 ? mq_dot(c).T : gSvT);
      if(mq_dot(c).T > 0) gC = c;
   }
}

//--- a strategy's position the EA does not know (a crash between the buy and the save, memory off): managed from now on with its
//--- own SL / TP (the rules' levels from its open price where it has none); booked with its real result when it closes
void Adopt(Strat &s)
{
   ulong tk = FindPos(s);
   if(tk == 0 || !PositionSelectByTicket(tk)) return;
   double op = PositionGetDouble(POSITION_PRICE_OPEN), psl = PositionGetDouble(POSITION_SL), ptp = PositionGetDouble(POSITION_TP);
   mq_dot(s).pos = true; mq_dot(s).F = op; mq_dot(s).SLp = psl > 0 ? psl : op * (1.0 - mq_dot(s).sl / 100.0); mq_dot(s).TPp = ptp > 0 ? ptp : op * (1.0 + mq_dot(s).tp / 100.0);
   mq_dot(s).BEl = op * (1.0 + mq_dot(s).be / 100.0); mq_dot(s).SVl = op * (1.0 - mq_dot(s).sv / 100.0);
   mq_dot(s).beOn = mq_dot(s).SLp >= op; mq_dot(s).svOn = mq_dot(s).TPp <= op; mq_dot(s).trOn = false; mq_dot(s).hi = MathMax(op, SymbolInfoDouble(_Symbol, SYMBOL_BID));
   mq_dot(s).eTime = (datetime)PositionGetInteger(POSITION_TIME); mq_dot(s).ticket = tk; mq_dot(s).lots = PositionGetDouble(POSITION_VOLUME);
   mq_dot(s).units = mq_dot(s).lots * Contract(); mq_dot(s).bR = FBase(s, op * mq_dot(s).sl / 100.0); mq_dot(s).risk = mq_dot(s).units * (op - mq_dot(s).SLp + Costs()) * Vpu(); mq_dot(s).cnt = true; mq_dot(s).exitDue = 0;
   Print("FBG S"_mq, mq_dot(s).id, ": adopted its open position #"_mq, tk, " ("_mq, DoubleToString(mq_dot(s).lots, 2), " lot at "_mq, DoubleToString(op, _Digits), ")."_mq);
   gDirty = true;
}
//--- table and lines -----------------------------------------------------------------------------------------------------------------
color  gCol[12] = { ((color)16736809), ((color)13941760), ((color)5287756), ((color)39167), ((color)11544476), ((color)6495977), ((color)8951296), ((color)3792077), ((color)4740473), ((color)9141600), ((color)5395199), ((color)3927039) };
MqlArr<string> gRows; MqlArr<color> gRowC;
datetime gDrawT = 0;
string TfTxt(ENUM_TIMEFRAMES t) { return t == PERIOD_M1 ? "M1"_mq : t == PERIOD_M5 ? "M5"_mq : t == PERIOD_M15 ? "M15"_mq : t == PERIOD_M30 ? "M30"_mq : t == PERIOD_H1 ? "H1"_mq : t == PERIOD_H4 ? "H4"_mq : t == PERIOD_D1 ? "D1"_mq : EnumToString(t); }
string RecTxt() { string e = EnumToString(gpRec); return StringSubstr(e, 4); }
string Usd(double v) { return (v < 0 ? "-"_mq : ""_mq) + DoubleToString(MathAbs(v), 2); }
string NowTxt(Strat &s)
{
   if(!mq_dot(s).ok) return "off"_mq;
   if(mq_dot(s).stopped) return mq_dot(s).stopWhy;
   if(mq_dot(s).pos)
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      return "LONG "_mq + DoubleToString(mq_dot(s).lots, 2) + " lot @ "_mq + DoubleToString(mq_dot(s).F, _Digits) + " "_mq + (bid >= mq_dot(s).F ? "+"_mq : ""_mq) + DoubleToString((bid - mq_dot(s).F) / mq_dot(s).F * 100.0, 2) + "% | SL "_mq +
             DoubleToString(mq_dot(s).SLp, _Digits) + (mq_dot(s).beOn ? " (BE)"_mq : mq_dot(s).trOn ? " (trail)"_mq : ""_mq) + " TP "_mq + DoubleToString(mq_dot(s).TPp, _Digits) + (mq_dot(s).svOn ? " (salvage)"_mq : ""_mq);
   }
   if(mq_dot(s).lvlOn)
   {
      double r = FNext(s, mq_dot(s).E);
      string nx = r > 0 ? " | next "_mq + DoubleToString(LotsOf(r / ((mq_dot(s).E * mq_dot(s).sl / 100.0 + Costs()) * Vpu())), 2) + " lot, risk "_mq + DoubleToString(r, 2) : r < 0 ? " | the hard cap would stop it"_mq : ""_mq;
      return "buy stop "_mq + DoubleToString(mq_dot(s).E, _Digits) + nx;
   }
   return "waiting for a swing high"_mq;
}
void Row(string t, color c) { int n = ArraySize(gRows); ArrayResize(gRows, n + 1); ArrayResize(gRowC, n + 1); gRows[n] = t; gRowC[n] = c; }
string Pad(string t, int w) { string r = t; while(StringLen(r) < w) r += " "_mq; return r; }
void HLine(string nm, double p, color c, ENUM_LINE_STYLE st)
{
   if(p <= 0) { ObjectDelete(0, nm); return; }
   if(ObjectFind(0, nm) < 0) { ObjectCreate(0, nm, OBJ_HLINE, 0, 0, p); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false); ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true); }
   ObjectSetDouble(0, nm, OBJPROP_PRICE, p); ObjectSetInteger(0, nm, OBJPROP_COLOR, c); ObjectSetInteger(0, nm, OBJPROP_STYLE, st);
}
void Draw(bool force)
{
   if(gSim || (MQLInfoInteger(MQL_TESTER) != 0 && MQLInfoInteger(MQL_VISUAL_MODE) == 0)) return;
   if(!force && TimeLocal() - gDrawT < 2) return;
   gDrawT = TimeLocal();
   for(int i = 0; i < 12; i++)
   {
      string id = IntegerToString(i + 1);
      bool on = InpLines && mq_dot(S[i]).ok;
      HLine("FBG_E"_mq + id, on && mq_dot(S[i]).lvlOn && !mq_dot(S[i]).pos ? mq_dot(S[i]).E : 0, gCol[i], STYLE_DOT);
      HLine("FBG_SL"_mq + id, on && mq_dot(S[i]).pos ? mq_dot(S[i]).SLp : 0, ((color)4536050), STYLE_DASH);
      HLine("FBG_TP"_mq + id, on && mq_dot(S[i]).pos ? mq_dot(S[i]).TPp : 0, ((color)5287756), STYLE_DASH);
   }
   ArrayResize(gRows, 0); ArrayResize(gRowC, 0);
   if(InpTable)
   {
      Row("FRACTAL BREAKOUT GRID EA v1.1 | "_mq + (InpPreset != GP_CUSTOM ? PresetName() + " | "_mq : ""_mq) + _Symbol + " | magic "_mq + IntegerToString(InpMagic) + " + N"_mq, ((color)14721833));
      string sz = gpSizeMode == PSZ_LOT ? DoubleToString(InpBaseLots, 2) + " lot"_mq : gpSizeMode == PSZ_PCT ? DoubleToString(InpEqPct, 2) + "% of equity"_mq : Usd(gpBaseRisk);
      Row("MONEY: "_mq + RecTxt() + (LadFam() && gpLadder != LAD_OFF ? " + ladder "_mq + StringSubstr(EnumToString(gpLadder), 4) : ""_mq) + " | base "_mq + sz + " | start "_mq + Usd(InpStartB) +
          " each"_mq + (gpCapOn ? " | cap "_mq + Usd(gpHardCap) : ""_mq), ((color)14472401));
      Row(Pad("#"_mq, 3) + Pad("TF"_mq, 4) + Pad("R/L"_mq, 8) + Pad("Trades"_mq, 7) + Pad("Win%"_mq, 6) + Pad("Net $"_mq, 11) + Pad("TP/SL/BE/SV"_mq, 16) + "Now"_mq, ((color)14472401));
      int tn = 0, tw = 0; double tnet = 0;
      for(int i = 0; i < 12; i++)
      {
         string rl = IntegerToString(mq_dot(S[i]).r) + "/"_mq + IntegerToString(mq_dot(S[i]).l);
         string wr = mq_dot(S[i]).n > 0 ? DoubleToString(100.0 * mq_dot(S[i]).nW / mq_dot(S[i]).n, 0) : "-"_mq;
         string cs = IntegerToString(mq_dot(S[i]).nTP) + "/"_mq + IntegerToString(mq_dot(S[i]).nSL) + "/"_mq + IntegerToString(mq_dot(S[i]).nBE) + "/"_mq + IntegerToString(mq_dot(S[i]).nSV);
         Row(Pad(IntegerToString(i + 1), 3) + Pad(TfTxt(mq_dot(S[i]).tf), 4) + Pad(rl, 8) + Pad(IntegerToString(mq_dot(S[i]).n), 7) + Pad(wr, 6) + Pad(Usd(mq_dot(S[i]).cum), 11) + Pad(cs, 16) + NowTxt(S[i]),
             !mq_dot(S[i]).ok ? ((color)8813432) : mq_dot(S[i]).pos ? (SymbolInfoDouble(_Symbol, SYMBOL_BID) >= mq_dot(S[i]).F ? ((color)5287756) : ((color)4536050)) : gCol[i]);
         tn += mq_dot(S[i]).n; tw += mq_dot(S[i]).nW; tnet += mq_dot(S[i]).cum;
      }
      Row("TOTAL: "_mq + IntegerToString(tn) + " trades | win "_mq + (tn > 0 ? DoubleToString(100.0 * tw / tn, 0) : "-"_mq) + "% | net "_mq + Usd(tnet) + (gRestored ? " | continued after a restart"_mq : ""_mq), ((color)14472401));
   }
   int fs = MathMax(6, InpTableFont), n = ArraySize(gRows), wmax = 0, th = 0;
   uint tw2 = 0, tht = 0;
   TextSetFont("Courier New"_mq, -fs * 10);
   for(int i = 0; i < n; i++) { TextGetSize(gRows[i], tw2, tht); wmax = MathMax(wmax, (int)tw2); th = MathMax(th, (int)tht); }
   int rowH = th + 4, cw = (int)ChartGetInteger(0, CHART_WIDTH_IN_PIXELS), chh = (int)ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);
   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;
   int x0 = right ? MathMax(0, cw - wmax - 16) : 6, y0 = bottom ? MathMax(0, chh - n * rowH - 10) : 20;
   string bg = "FBG_TBbg"_mq;
   if(n > 0)
   {
      if(ObjectFind(0, bg) < 0) { ObjectCreate(0, bg, OBJ_RECTANGLE_LABEL, 0, 0, 0); ObjectSetInteger(0, bg, OBJPROP_SELECTABLE, false); ObjectSetInteger(0, bg, OBJPROP_HIDDEN, true); }
      ObjectSetInteger(0, bg, OBJPROP_CORNER, CORNER_LEFT_UPPER); ObjectSetInteger(0, bg, OBJPROP_XDISTANCE, x0 - 4); ObjectSetInteger(0, bg, OBJPROP_YDISTANCE, y0 - 3);
      ObjectSetInteger(0, bg, OBJPROP_XSIZE, wmax + 10); ObjectSetInteger(0, bg, OBJPROP_YSIZE, n * rowH + 6);
      ObjectSetInteger(0, bg, OBJPROP_BGCOLOR, ((color)2234131)); ObjectSetInteger(0, bg, OBJPROP_BORDER_TYPE, BORDER_FLAT); ObjectSetInteger(0, bg, OBJPROP_COLOR, ((color)5326403));
   }
   else ObjectDelete(0, bg);
   for(int i = 0; i < 40; i++)
   {
      string nm = "FBG_TB"_mq + IntegerToString(i);
      if(i >= n) { ObjectDelete(0, nm); continue; }
      if(ObjectFind(0, nm) < 0) { ObjectCreate(0, nm, OBJ_LABEL, 0, 0, 0); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false); ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true); }
      ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER); ObjectSetInteger(0, nm, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
      ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x0); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y0 + i * rowH);
      ObjectSetString(0, nm, OBJPROP_TEXT, gRows[i]); ObjectSetString(0, nm, OBJPROP_FONT, "Courier New"_mq);
      ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, fs); ObjectSetInteger(0, nm, OBJPROP_COLOR, gRowC[i]);
   }
   ChartRedraw(0);
}

//--- MetaTrader events ---------------------------------------------------------------------------------------------------------------
bool Runs(int i, bool ticked) { return gpRun == RUN_ALL ? true : gpRun == RUN_TICKED ? ticked : InpRunOne == i; }
//--- v1.1: the values the rules use: the inputs (Custom) or the preset's (written by fbgea/presetize.py from presets/preset_data.py)
void PresetApply()
{
   int gi = (int)InpPreset; bool pc = gi == 0, pm = pc || InpMyMoney;
   gpRun = pc ? InpRun : RUN_TICKED;
   gpS1On = pc ? InpS1On : ((gi == 1 || gi == 4) ? false : true); gpS1Tf = pc ? InpS1Tf : PERIOD_D1; gpS1R = pc ? InpS1R : 3; gpS1L = pc ? InpS1L : 25;
   gpS1Off = pc ? InpS1Off : -0.14; gpS1Sl = pc ? InpS1Sl : 3.0; gpS1Tp = pc ? InpS1Tp : 0.75; gpS1Be = pc ? InpS1Be : 0.45; gpS1Sv = pc ? InpS1Sv : 0.8;
   gpS2On = pc ? InpS2On : ((gi == 1 || gi == 4) ? false : true); gpS2Tf = pc ? InpS2Tf : PERIOD_D1; gpS2R = pc ? InpS2R : 3; gpS2L = pc ? InpS2L : 15;
   gpS2Off = pc ? InpS2Off : -0.085; gpS2Sl = pc ? InpS2Sl : 0.5; gpS2Tp = pc ? InpS2Tp : 2.0; gpS2Be = pc ? InpS2Be : 0.25; gpS2Sv = pc ? InpS2Sv : 0.8;
   gpS3On = pc ? InpS3On : ((gi == 5 || gi == 6) ? true : false); gpS3Tf = pc ? InpS3Tf : PERIOD_D1; gpS3R = pc ? InpS3R : 2; gpS3L = pc ? InpS3L : 7;
   gpS3Off = pc ? InpS3Off : -0.065; gpS3Sl = pc ? InpS3Sl : 0.3; gpS3Tp = pc ? InpS3Tp : 1.65; gpS3Be = pc ? InpS3Be : 0.2; gpS3Sv = pc ? InpS3Sv : 0.5;
   gpS4On = pc ? InpS4On : ((gi == 5) ? true : false); gpS4Tf = pc ? InpS4Tf : PERIOD_H4; gpS4R = pc ? InpS4R : 8; gpS4L = pc ? InpS4L : 12;
   gpS4Off = pc ? InpS4Off : -0.025; gpS4Sl = pc ? InpS4Sl : 0.44; gpS4Tp = pc ? InpS4Tp : 3.1; gpS4Be = pc ? InpS4Be : 0.33; gpS4Sv = pc ? InpS4Sv : 0.9;
   gpS5On = pc ? InpS5On : ((gi == 5 || gi == 6) ? true : false); gpS5Tf = pc ? InpS5Tf : PERIOD_H1; gpS5R = pc ? InpS5R : 19; gpS5L = pc ? InpS5L : 30;
   gpS5Off = pc ? InpS5Off : -0.045; gpS5Sl = pc ? InpS5Sl : 2.0; gpS5Tp = pc ? InpS5Tp : 0.35; gpS5Be = pc ? InpS5Be : 0.1; gpS5Sv = pc ? InpS5Sv : 0.7;
   gpS6On = pc ? InpS6On : ((gi == 1 || gi == 4) ? false : true); gpS6Tf = pc ? InpS6Tf : PERIOD_H1; gpS6R = pc ? InpS6R : 25; gpS6L = pc ? InpS6L : 25;
   gpS6Off = pc ? InpS6Off : -0.06; gpS6Sl = pc ? InpS6Sl : 4.2; gpS6Tp = pc ? InpS6Tp : 0.33; gpS6Be = pc ? InpS6Be : 0.15; gpS6Sv = pc ? InpS6Sv : 0.8;
   gpS7On = pc ? InpS7On : (true); gpS7Tf = pc ? InpS7Tf : PERIOD_H1; gpS7R = pc ? InpS7R : 23; gpS7L = pc ? InpS7L : 25;
   gpS7Off = pc ? InpS7Off : -0.055; gpS7Sl = pc ? InpS7Sl : 0.87; gpS7Tp = pc ? InpS7Tp : 0.56; gpS7Be = pc ? InpS7Be : 0.13; gpS7Sv = pc ? InpS7Sv : 1.1;
   gpS8On = pc ? InpS8On : (true); gpS8Tf = pc ? InpS8Tf : PERIOD_H1; gpS8R = pc ? InpS8R : 20; gpS8L = pc ? InpS8L : 25;
   gpS8Off = pc ? InpS8Off : -0.06; gpS8Sl = pc ? InpS8Sl : 0.68; gpS8Tp = pc ? InpS8Tp : 0.43; gpS8Be = pc ? InpS8Be : 0.1; gpS8Sv = pc ? InpS8Sv : 0.7;
   gpS9On = pc ? InpS9On : ((gi == 5 || gi == 6) ? true : false); gpS9Tf = pc ? InpS9Tf : PERIOD_H1; gpS9R = pc ? InpS9R : 5; gpS9L = pc ? InpS9L : 5;
   gpS9Off = pc ? InpS9Off : -0.08; gpS9Sl = pc ? InpS9Sl : 2.0; gpS9Tp = pc ? InpS9Tp : 0.7; gpS9Be = pc ? InpS9Be : 0.1; gpS9Sv = pc ? InpS9Sv : 1.0;
   gpS10On = pc ? InpS10On : (true); gpS10Tf = pc ? InpS10Tf : PERIOD_M5; gpS10R = pc ? InpS10R : 30; gpS10L = pc ? InpS10L : 65;
   gpS10Off = pc ? InpS10Off : -0.05; gpS10Sl = pc ? InpS10Sl : 1.0; gpS10Tp = pc ? InpS10Tp : 1.0; gpS10Be = pc ? InpS10Be : 0.2; gpS10Sv = pc ? InpS10Sv : 0.0;
   gpS11On = pc ? InpS11On : ((gi == 5 || gi == 6) ? true : false); gpS11Tf = pc ? InpS11Tf : PERIOD_M15; gpS11R = pc ? InpS11R : 20; gpS11L = pc ? InpS11L : 40;
   gpS11Off = pc ? InpS11Off : -0.01; gpS11Sl = pc ? InpS11Sl : 1.0; gpS11Tp = pc ? InpS11Tp : 3.0; gpS11Be = pc ? InpS11Be : 0.2; gpS11Sv = pc ? InpS11Sv : 0.1;
   gpS12On = pc ? InpS12On : ((gi == 5 || gi == 6) ? true : false); gpS12Tf = pc ? InpS12Tf : PERIOD_M1; gpS12R = pc ? InpS12R : 45; gpS12L = pc ? InpS12L : 200;
   gpS12Off = pc ? InpS12Off : -0.05; gpS12Sl = pc ? InpS12Sl : 0.75; gpS12Tp = pc ? InpS12Tp : 3.0; gpS12Be = pc ? InpS12Be : 0.2; gpS12Sv = pc ? InpS12Sv : 0.0;
   gpEntry = pc ? InpEntry : ENT_STOP; gpExpN = pc ? InpExpN : 0; gpMaxDay = pc ? InpMaxDay : 0; gpTrA = pc ? InpTrA : 0.0; gpTrD = pc ? InpTrD : 0.0;
   gpTExitH = pc ? InpTExitH : 0.0; gpTrnOn = pc ? InpTrnOn : false;
   gpDayOn = (pc || InpAddMine) && InpDayOn; gpHoursOn = (pc || InpAddMine) && InpHoursOn;
   gpSizeMode = pm ? InpSizeMode : PSZ_USD;
   gpBaseRisk = pm ? InpBaseRisk : ((gi == 2 || gi == 4) ? 5.0 : 10.0);
   gpCapOn = pm ? InpCapOn : ((gi == 5 || gi == 6) ? false : true);
   gpHardCap = pm ? InpHardCap : ((gi == 2 || gi == 4) ? 50.0 : (gi == 5 || gi == 6) ? 500.0 : 100.0);
   gpCapAction = pm ? InpCapAction : (ENUM_CAP)((gi == 3) ? CAP_RESET : CAP_CLAMP);
   gpRec = pm ? InpRec : (ENUM_REC)((gi == 5 || gi == 6) ? REC_OFF : REC_EXACT);
   gpLadder = pm ? InpLadder : LAD_OFF;
   gpMRestart = pm ? InpMRestart : true;
}
void Setup()
{
   PresetApply();
   StratInit(S[0], 1, Runs(1, gpS1On), gpS1Tf, gpS1R, gpS1L, gpS1Off, gpS1Sl, gpS1Tp, gpS1Be, gpS1Sv);
   StratInit(S[1], 2, Runs(2, gpS2On), gpS2Tf, gpS2R, gpS2L, gpS2Off, gpS2Sl, gpS2Tp, gpS2Be, gpS2Sv);
   StratInit(S[2], 3, Runs(3, gpS3On), gpS3Tf, gpS3R, gpS3L, gpS3Off, gpS3Sl, gpS3Tp, gpS3Be, gpS3Sv);
   StratInit(S[3], 4, Runs(4, gpS4On), gpS4Tf, gpS4R, gpS4L, gpS4Off, gpS4Sl, gpS4Tp, gpS4Be, gpS4Sv);
   StratInit(S[4], 5, Runs(5, gpS5On), gpS5Tf, gpS5R, gpS5L, gpS5Off, gpS5Sl, gpS5Tp, gpS5Be, gpS5Sv);
   StratInit(S[5], 6, Runs(6, gpS6On), gpS6Tf, gpS6R, gpS6L, gpS6Off, gpS6Sl, gpS6Tp, gpS6Be, gpS6Sv);
   StratInit(S[6], 7, Runs(7, gpS7On), gpS7Tf, gpS7R, gpS7L, gpS7Off, gpS7Sl, gpS7Tp, gpS7Be, gpS7Sv);
   StratInit(S[7], 8, Runs(8, gpS8On), gpS8Tf, gpS8R, gpS8L, gpS8Off, gpS8Sl, gpS8Tp, gpS8Be, gpS8Sv);
   StratInit(S[8], 9, Runs(9, gpS9On), gpS9Tf, gpS9R, gpS9L, gpS9Off, gpS9Sl, gpS9Tp, gpS9Be, gpS9Sv);
   StratInit(S[9], 10, Runs(10, gpS10On), gpS10Tf, gpS10R, gpS10L, gpS10Off, gpS10Sl, gpS10Tp, gpS10Be, gpS10Sv);
   StratInit(S[10], 11, Runs(11, gpS11On), gpS11Tf, gpS11R, gpS11L, gpS11Off, gpS11Sl, gpS11Tp, gpS11Be, gpS11Sv);
   StratInit(S[11], 12, Runs(12, gpS12On), gpS12Tf, gpS12R, gpS12L, gpS12Off, gpS12Sl, gpS12Tp, gpS12Be, gpS12Sv);
}
//--- one copy per symbol + magic number: a temporary global variable holds the chart of the copy that runs
string gLockN = ""_mq; double gLockV = 0;
bool LockTake()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return true;
   gLockN = "FBGX|"_mq + _Symbol + "|"_mq + IntegerToString(InpMagic) + "|run"_mq;
   gLockV = (double)(ChartID() & 0xFFFFFFFFFFFF) + 1.0;
   if(!GlobalVariableCheck(gLockN)) GlobalVariableTemp(gLockN);
   if(GlobalVariableSetOnCondition(gLockN, gLockV, 0)) return true;
   double cur = GlobalVariableGet(gLockN);
   if(cur == gLockV) return true;
   for(mql_long id = ChartFirst(); id >= 0; id = ChartNext(id))
      if(id != ChartID() && (double)(id & 0xFFFFFFFFFFFF) + 1.0 == cur && ChartGetString(id, CHART_EXPERT_NAME) != ""_mq) return false;
   return GlobalVariableSetOnCondition(gLockN, gLockV, cur);
}
void LockFree() { if(gLockN != ""_mq && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableSetOnCondition(gLockN, 0, gLockV); }

void TryStart();
int OnInit()
{
   PresetApply();                                      // v1.1: the preset's values (or the inputs) before anything uses them
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
   {
      string m = "Fractal Breakout Grid EA needs a HEDGING account (every strategy holds its own position); this account nets positions."_mq;
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   if(gpRun == RUN_ONE && (InpRunOne < 1 || InpRunOne > 12)) { Print("Run one strategy: the number must be 1 to 12."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpSpread < 0 || InpCommLot < 0 || InpStartB <= 0 || InpLev <= 0) { Print("Spread, commission, start balance and leverage limit must be above 0 (spread / commission: 0 or more)."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((gpSizeMode == PSZ_USD && gpBaseRisk <= 0) || (gpSizeMode == PSZ_LOT && InpBaseLots <= 0) || (gpSizeMode == PSZ_PCT && InpEqPct <= 0))
   { Print("Position size: the base risk, base lots or risk % of equity must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpCapOn && gpHardCap <= 0) { Print("Hard cap: the amount must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpRec == REC_CRG && InpCrkGX <= 0) { Print("Crooks G: the limit of the loss to win back must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpRec == REC_CRH && InpCrkHPct <= 0) { Print("Crooks H: the % of the equity must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpRec == REC_CRJ && InpCrkJX <= 0) { Print("Crooks J: the drawdown must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((gpRec == REC_CRF || gpRec == REC_CRI) && InpCrkFK <= 0) { Print("Crooks F / I: the limit must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpLadder != LAD_OFF && InpLadT <= 0) { Print("Profit ladder: the profit target must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpCrkELot <= 0 || InpRecMult <= 0) { Print("Crooks E / I lot and the Martingale multiplier must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   Setup();
   for(int i = 0; i < 12; i++)
      if(mq_dot(S[i]).ok && (mq_dot(S[i]).sl <= 0 || mq_dot(S[i]).tp <= 0 || mq_dot(S[i]).be < 0 || mq_dot(S[i]).sv < 0))
      { Print("Strategy "_mq, i + 1, ": SL % and TP % must be above 0, BE and salvage triggers 0 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   gSvBase = "FBG|"_mq + _Symbol + "|"_mq + IntegerToString(InpMagic) + "|"_mq;
   if(StringLen(gSvBase) > 50) gSvBase = "FBG|"_mq + StringSubstr(_Symbol, 0, 20) + "|"_mq + IntegerToString(InpMagic) + "|"_mq;
   if(!LockTake())
   {
      string m = "Another copy of this EA runs on "_mq + _Symbol + " with magic number "_mq + IntegerToString(InpMagic) + ": remove one, or give each its own magic number."_mq;
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   mq_dot(trade).SetDeviationInPoints(50);
   mq_dot(trade).SetTypeFillingBySymbol(_Symbol);
   TzPick();
   gReady = false; gStartAt = TimeLocal();
   TryStart();
   EventSetTimer(2);
   return INIT_SUCCEEDED;
}
//--- MT5 has the history the start needs (1-minute bars, every strategy's timeframe, the trend timeframe)
bool SeriesOk()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return true;
   bool ok = SeriesInfoInteger(_Symbol, PERIOD_M1, SERIES_SYNCHRONIZED) != 0 && iTime(_Symbol, PERIOD_M1, 0) > 0;
   for(int i = 0; i < 12; i++) if(mq_dot(S[i]).ok && (SeriesInfoInteger(_Symbol, mq_dot(S[i]).tf, SERIES_SYNCHRONIZED) == 0 || iTime(_Symbol, mq_dot(S[i]).tf, 0) <= 0)) ok = false;
   if(gpTrnOn && (SeriesInfoInteger(_Symbol, InpTrnTf, SERIES_SYNCHRONIZED) == 0 || iTime(_Symbol, InpTrnTf, 0) <= 0)) ok = false;
   return ok;
}
//--- the start: the memory (restart) or the warm-up (fresh), positions closed while the EA was off, positions it does not know
void TryStart()
{
   if(gReady) return;
   if(!SeriesOk())
   {
      if(TimeLocal() - gStartAt < 60) return;           // again in 2 seconds (OnTimer)
      Print("Fractal Breakout Grid EA: MT5 has not loaded all the history after 60 seconds: starting with what it has."_mq);
   }
   TrendLoad();
   datetime now = TimeCurrent(); now = now - now % 60;
   mq_dot(gC).T = 0; mq_dot(gC).last = 0; mq_dot(gC).prevC = 0; mq_dot(gC).okb = false; mq_dot(gC).wk = false; mq_dot(gC).dno = 0;
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariablesDeleteAll(gSvBase);   // memory off: forget the saved state
   gRestored = StateLoad();
   if(gRestored) Restore(now);
   else
   {
      BarCtx c;
      for(int i = 0; i < 12; i++)
      {
         mq_dot(c).T = 0; mq_dot(c).last = 0; mq_dot(c).prevC = 0; mq_dot(c).okb = false; mq_dot(c).wk = false; mq_dot(c).dno = 0;
         if(mq_dot(S[i]).ok) { WarmStrat(S[i], now, c); if(mq_dot(c).T > 0) gC = c; }
      }
   }
   gReady = true;
   Reconcile();
   for(int i = 0; i < 12; i++) if(mq_dot(S[i]).ok && !mq_dot(S[i]).pos) Adopt(S[i]);
   for(int i = 0; i < 12; i++)
      if(mq_dot(S[i]).ok) Print("FBG S"_mq, i + 1, " "_mq, TfTxt(mq_dot(S[i]).tf), " "_mq, mq_dot(S[i]).r, "/"_mq, mq_dot(S[i]).l, ": "_mq, NowTxt(S[i]));
   gDirty = true;
   Draw(true);
}
void OnDeinit(const int reason)
{
   if(gReady) StateSave(true);
   EventKillTimer();
   ObjectsDeleteAll(0, "FBG_"_mq);
   LockFree();
}
void OnTick()
{
   if(!gReady) { TryStart(); if(!gReady) return; }
   MqlTick tk;
   if(!SymbolInfoTick(_Symbol, tk) || mq_dot(tk).bid <= 0) return;
   Reconcile();
   datetime m = mq_dot(tk).time - mq_dot(tk).time % 60;
   if(m > mq_dot(gC).T)
   {
      for(int i = 0; i < 12; i++) if(mq_dot(S[i]).ok) BarEnd(S[i], gC);
      for(int i = 0; i < 12; i++) if(mq_dot(S[i]).ok) PushLive(S[i]);
      TrendLive();
      CtxBegin(gC, m, mq_dot(tk).bid);
      for(int i = 0; i < 12; i++) if(mq_dot(S[i]).ok) BarBegin(S[i], gC, mq_dot(tk).bid);
      gDirty = true;
   }
   else if(mq_dot(tk).bid != mq_dot(gC).last)
   {
      for(int i = 0; i < 12; i++) if(mq_dot(S[i]).ok) Move(S[i], gC, mq_dot(tk).bid);
      mq_dot(gC).last = mq_dot(tk).bid;
   }
   Sync();
   if(gDirty) { StateSave(false); gDirty = false; }
   Draw(false);
}
void OnTimer()
{
   if(!gReady) { TryStart(); if(!gReady) return; }
   Reconcile();
   if(gDirty) { StateSave(false); gDirty = false; }
   Draw(false);
}

#line 1680 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fbgea/harness/EA_copy.mq5"
typedef void (*mq_t_OnTick)();
static mq_t_OnTick mq_chk_OnTick = &OnTick;
#line 1705 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fbgea/harness/EA_copy.mq5"
typedef void (*mq_t_OnTimer)();
static mq_t_OnTimer mq_chk_OnTimer = &OnTimer;
#line 1673 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fbgea/harness/EA_copy.mq5"
typedef void (*mq_t_OnDeinit)(const int);
static mq_t_OnDeinit mq_chk_OnDeinit = &OnDeinit;
#line 1 "<fbg-wrapper>"
extern "C" int rt_SetInput(const char* name, double v)
{
   if(__builtin_strcmp(name, "InpPreset") == 0) { InpPreset = (ENUM_GPRESET)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpAddMine") == 0) { InpAddMine = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMyMoney") == 0) { InpMyMoney = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpRun") == 0) { InpRun = (ENUM_RUN)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpRunOne") == 0) { InpRunOne = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMagic") == 0) { InpMagic = (mql_long)v; return 1; }
   if(__builtin_strcmp(name, "InpSpread") == 0) { InpSpread = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCommLot") == 0) { InpCommLot = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS1On") == 0) { InpS1On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS1Tf") == 0) { InpS1Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS1R") == 0) { InpS1R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS1L") == 0) { InpS1L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS1Off") == 0) { InpS1Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS1Sl") == 0) { InpS1Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS1Tp") == 0) { InpS1Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS1Be") == 0) { InpS1Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS1Sv") == 0) { InpS1Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS2On") == 0) { InpS2On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS2Tf") == 0) { InpS2Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS2R") == 0) { InpS2R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS2L") == 0) { InpS2L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS2Off") == 0) { InpS2Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS2Sl") == 0) { InpS2Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS2Tp") == 0) { InpS2Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS2Be") == 0) { InpS2Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS2Sv") == 0) { InpS2Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS3On") == 0) { InpS3On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS3Tf") == 0) { InpS3Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS3R") == 0) { InpS3R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS3L") == 0) { InpS3L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS3Off") == 0) { InpS3Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS3Sl") == 0) { InpS3Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS3Tp") == 0) { InpS3Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS3Be") == 0) { InpS3Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS3Sv") == 0) { InpS3Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS4On") == 0) { InpS4On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS4Tf") == 0) { InpS4Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS4R") == 0) { InpS4R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS4L") == 0) { InpS4L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS4Off") == 0) { InpS4Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS4Sl") == 0) { InpS4Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS4Tp") == 0) { InpS4Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS4Be") == 0) { InpS4Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS4Sv") == 0) { InpS4Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS5On") == 0) { InpS5On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS5Tf") == 0) { InpS5Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS5R") == 0) { InpS5R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS5L") == 0) { InpS5L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS5Off") == 0) { InpS5Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS5Sl") == 0) { InpS5Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS5Tp") == 0) { InpS5Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS5Be") == 0) { InpS5Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS5Sv") == 0) { InpS5Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS6On") == 0) { InpS6On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS6Tf") == 0) { InpS6Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS6R") == 0) { InpS6R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS6L") == 0) { InpS6L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS6Off") == 0) { InpS6Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS6Sl") == 0) { InpS6Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS6Tp") == 0) { InpS6Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS6Be") == 0) { InpS6Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS6Sv") == 0) { InpS6Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS7On") == 0) { InpS7On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS7Tf") == 0) { InpS7Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS7R") == 0) { InpS7R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS7L") == 0) { InpS7L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS7Off") == 0) { InpS7Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS7Sl") == 0) { InpS7Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS7Tp") == 0) { InpS7Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS7Be") == 0) { InpS7Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS7Sv") == 0) { InpS7Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS8On") == 0) { InpS8On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS8Tf") == 0) { InpS8Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS8R") == 0) { InpS8R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS8L") == 0) { InpS8L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS8Off") == 0) { InpS8Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS8Sl") == 0) { InpS8Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS8Tp") == 0) { InpS8Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS8Be") == 0) { InpS8Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS8Sv") == 0) { InpS8Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS9On") == 0) { InpS9On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS9Tf") == 0) { InpS9Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS9R") == 0) { InpS9R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS9L") == 0) { InpS9L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS9Off") == 0) { InpS9Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS9Sl") == 0) { InpS9Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS9Tp") == 0) { InpS9Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS9Be") == 0) { InpS9Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS9Sv") == 0) { InpS9Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS10On") == 0) { InpS10On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS10Tf") == 0) { InpS10Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS10R") == 0) { InpS10R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS10L") == 0) { InpS10L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS10Off") == 0) { InpS10Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS10Sl") == 0) { InpS10Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS10Tp") == 0) { InpS10Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS10Be") == 0) { InpS10Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS10Sv") == 0) { InpS10Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS11On") == 0) { InpS11On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS11Tf") == 0) { InpS11Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS11R") == 0) { InpS11R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS11L") == 0) { InpS11L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS11Off") == 0) { InpS11Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS11Sl") == 0) { InpS11Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS11Tp") == 0) { InpS11Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS11Be") == 0) { InpS11Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS11Sv") == 0) { InpS11Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS12On") == 0) { InpS12On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpS12Tf") == 0) { InpS12Tf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpS12R") == 0) { InpS12R = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS12L") == 0) { InpS12L = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpS12Off") == 0) { InpS12Off = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS12Sl") == 0) { InpS12Sl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS12Tp") == 0) { InpS12Tp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS12Be") == 0) { InpS12Be = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpS12Sv") == 0) { InpS12Sv = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpEntry") == 0) { InpEntry = (ENUM_ENTRY)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpExpN") == 0) { InpExpN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMaxDay") == 0) { InpMaxDay = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpTrA") == 0) { InpTrA = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTrD") == 0) { InpTrD = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTExitH") == 0) { InpTExitH = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpWkOn") == 0) { InpWkOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpWkH") == 0) { InpWkH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpTrnOn") == 0) { InpTrnOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTrnTf") == 0) { InpTrnTf = (ENUM_TIMEFRAMES)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpTrnLen") == 0) { InpTrnLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpServerTz") == 0) { InpServerTz = (ENUM_SRV_TZ)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpServerGMT") == 0) { InpServerGMT = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpUserGMT") == 0) { InpUserGMT = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpDayOn") == 0) { InpDayOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMon") == 0) { InpMon = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTue") == 0) { InpTue = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpWed") == 0) { InpWed = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpThu") == 0) { InpThu = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpFri") == 0) { InpFri = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpSat") == 0) { InpSat = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpSun") == 0) { InpSun = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHoursOn") == 0) { InpHoursOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHourFrom") == 0) { InpHourFrom = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpHourTo") == 0) { InpHourTo = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpStartB") == 0) { InpStartB = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpSizeMode") == 0) { InpSizeMode = (ENUM_SIZE)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpBaseRisk") == 0) { InpBaseRisk = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpBaseLots") == 0) { InpBaseLots = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpEqPct") == 0) { InpEqPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpLev") == 0) { InpLev = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCapOn") == 0) { InpCapOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHardCap") == 0) { InpHardCap = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCapAction") == 0) { InpCapAction = (ENUM_CAP)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpMRestart") == 0) { InpMRestart = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpRec") == 0) { InpRec = (ENUM_REC)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpRecN") == 0) { InpRecN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpRecPct") == 0) { InpRecPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpRecMult") == 0) { InpRecMult = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpRecStep") == 0) { InpRecStep = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCSplit") == 0) { InpCSplit = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpParN") == 0) { InpParN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDelayN") == 0) { InpDelayN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkCn") == 0) { InpCrkCn = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPr") == 0) { InpCrkPr = (ENUM_CRK_PR)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrN") == 0) { InpCrkPrN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrPct") == 0) { InpCrkPrPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrM") == 0) { InpCrkPrM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkELot") == 0) { InpCrkELot = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkFK") == 0) { InpCrkFK = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkGX") == 0) { InpCrkGX = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkHPct") == 0) { InpCrkHPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkJX") == 0) { InpCrkJX = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpLadder") == 0) { InpLadder = (ENUM_LADDER)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpLadT") == 0) { InpLadT = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTable") == 0) { InpTable = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTablePos") == 0) { InpTablePos = (ENUM_TBL_POS)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpTableFont") == 0) { InpTableFont = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpLines") == 0) { InpLines = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpAlerts") == 0) { InpAlerts = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpPush") == 0) { InpPush = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpRemember") == 0) { InpRemember = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpWarmDays") == 0) { InpWarmDays = (int)v; return 1; }
   return 0;
}

extern "C" void h_setup() { gSim = true; gNoEntry = false; Setup(); gC.T = 0; gC.last = 0; gC.prevC = 0; gC.okb = false; gC.wk = false; gC.dno = 0;
                            ArrayResize(gSimLog, 0); gSimN = 0; gTrSeed = false; gTrUp = false; gTrE = 0; }
extern "C" int h_ok(int i) { return S[i].ok ? 1 : 0; }
extern "C" void h_push(int i, double high, long long t, long long tNow) { PushTf(S[i], high, (datetime)t, (datetime)tNow, true); }
extern "C" void h_trend(double c) { PushTrend(c); }
extern "C" void h_barend() { for(int i = 0; i < 12; i++) if(S[i].ok) BarEnd(S[i], gC); }
extern "C" void h_begin(long long T, double o) { CtxBegin(gC, (datetime)T, o); for(int i = 0; i < 12; i++) if(S[i].ok) BarBegin(S[i], gC, o); }
extern "C" void h_move(double y) { for(int i = 0; i < 12; i++) if(S[i].ok) Move(S[i], gC, y); gC.last = y; }
extern "C" int h_logn() { return gSimN; }
extern "C" void h_log(int k, double* o) { for(int q = 0; q < 7; q++) o[q] = gSimLog[k * 7 + q]; }
// runtime functions the rules never call in the harness (gSim): stubs so it links
int CopyRates(const string&, ENUM_TIMEFRAMES, int, int, ArrayView<MqlRates>) { return 0; }
int CopyRates(const string&, ENUM_TIMEFRAMES, datetime, datetime, ArrayView<MqlRates>) { return 0; }
int CopyRates(const string&, ENUM_TIMEFRAMES, datetime, int, ArrayView<MqlRates>) { return 0; }
void EventKillTimer() {}
bool HistorySelectByPosition(mql_long) { return false; }
bool OrderCalcMargin(ENUM_ORDER_TYPE, const string&, double, double, double& m) { m = 0; return true; }
void Sleep(int) {}
bool SymbolInfoTick(const string&, MqlTick&) { return false; }
mql_long SeriesInfoInteger(const string&, ENUM_TIMEFRAMES, ENUM_SERIES_INFO_INTEGER) { return 1; }
// restart memory test: save every strategy (StateIO, as StateSave), a fresh program (Setup), load it back (StateIO); the driver then
// rebuilds the candles (no swing-high search, kAct from the buy stop's start) and the trend EMA, as Restore / TrendLoad do
extern "C" void h_restart()
{
   gIoSave = true; gIoC = 0; StateIO(true);
   for(int q = 0; q < gIoC; q++) GlobalVariableSet(gSvBase + gIoN[q], gIoV[q]);
   BarCtx keep = gC;
   Setup();
   StateIO(false);
   gC = keep;
}
extern "C" void h_repush(int i, double high, long long t, long long tNow) { PushTf(S[i], high, (datetime)t, (datetime)tNow, false); if((datetime)t < S[i].actT) S[i].kAct = S[i].nC; }
extern "C" void h_trend_reset() { gTrSeed = false; gTrUp = false; gTrE = 0; }
extern "C" void h_end(int i, double* o) { o[0] = S[i].eq; o[1] = S[i].net; o[2] = S[i].n; o[3] = S[i].pos ? 1 : 0; o[4] = S[i].stopped ? 1 : 0; }

