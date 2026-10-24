// EXPECT: clean
#property copyright "x"
#property strict
#include <Trade/Trade.mqh>
enum ENUM_MODE { MODE_A = 0, MODE_B = 1 };
input group "Main"
input int      InpLen   = 5;       // length
input double   InpMul   = 1.5;
input string   InpName  = "tbl";
input color    InpClr   = C'10,20,30';
input datetime InpWhen  = D'2026.01.01 18:00';
input ENUM_MODE InpMode = MODE_A;
input long     InpMagic = 123;
CTrade trade;
double   gHist[];
int      gCount = 0;
struct SRow { string name; double val; double hist[]; };
SRow gRows[];
uint     gW = 0, gH = 0;

double Sum(const double &a[], int n) { double s = 0; for(int i = 0; i < n && i < ArraySize(a); i++) s += a[i]; return s; }
void Fill(double &a[]) { ArrayResize(a, 4); ArrayInitialize(a, 0.0); a[0] = 1; }
string Fmt(double v) { return "v=" + DoubleToString(v, 2) + " n=" + IntegerToString(gCount) + " " + TimeToString(TimeCurrent(), TIME_DATE | TIME_MINUTES); }

void Panel()
{
   string nm = InpName + "_p";
   ObjectDelete(0, nm);
   ObjectCreate(0, nm, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, 10);
   ObjectSetInteger(0, nm, OBJPROP_BGCOLOR, clrBlack);
   ObjectSetInteger(0, nm, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, InpClr);
   ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_DOT);
   ObjectSetInteger(0, nm, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
   ObjectSetDouble(0, nm, OBJPROP_PRICE, 0, 1.2345);
   ObjectSetInteger(0, nm, OBJPROP_TIME, 1, TimeCurrent());
   ObjectSetString(0, nm, OBJPROP_TEXT, Fmt(1.0));
   ObjectSetString(0, nm, OBJPROP_FONT, "Consolas");
   TextSetFont("Consolas", -100);
   TextGetSize("abc", gW, gH);
   long w = ChartGetInteger(0, CHART_WIDTH_IN_PIXELS);
   long h = ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS, 0);
   ObjectCreate(0, "tr", OBJ_TREND, 0, TimeCurrent(), 1.0, TimeCurrent() + PeriodSeconds(), 2.0);
   ObjectMove(0, "tr", 1, TimeCurrent(), 2.0);
   ObjectCreate(0, "ar", OBJ_ARROW_BUY, 0, TimeCurrent(), 1.0);
   ObjectsDeleteAll(0, "tr");
   if(ObjectFind(0, nm) < 0) Print("missing");
   if(MQLInfoInteger(MQL_TESTER) != 0 || MQLInfoInteger(MQL_VISUAL_MODE) != 0) Print("tester ", w, h);
   if(TerminalInfoInteger(TERMINAL_CONNECTED) == 0) Print("offline");
   string s = "abc"; StringReplace(s, "a", "b");
   int p = StringFind(s, "b"); int L = StringLen(s); string ss = StringSubstr(s, 0, 1);
   Print(p, L, ss);
   ChartRedraw();
}

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   Fill(gHist);
   ArrayResize(gRows, 2);
   gRows[0].name = "x"; ArrayResize(gRows[0].hist, 3);
   double loc[3]; loc[0] = Sum(loc, ArraySize(loc));
   EventSetTimer(1);
   Panel();
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason) { EventKillTimer(); ObjectsDeleteAll(0, InpName); }
void OnTimer() { Panel(); }
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id == CHARTEVENT_OBJECT_CLICK && sparam == InpName) gCount++;
}
void OnTick()
{
   double mx = MathMax(1, 2.5); double mn = MathMin(gCount, 3);
   int im = (int)MathMax(InpLen, 2);
   datetime t = iTime(_Symbol, _Period, 1);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(PositionsTotal() > 0 && trade.Buy(0.1, _Symbol, 0, 0, 0, "x")) gCount++;
   Print(mx, mn, im, t, bid);
}
