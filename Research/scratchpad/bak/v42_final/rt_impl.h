// ---- runtime implementation section (appended to a copy of mql5shim.h by create_rt.py) ----
extern "C" int snprintf(char*, unsigned long, const char*, ...);

struct RtBar { long long t; double o, h, l, c; };
static RtBar* rt_bars = 0;
static int rt_n = 0;
static double rt_tick = 0.01;
extern "C" void rt_load(int n, const long long* t, const double* o, const double* h, const double* l, const double* c, double tick, int digits)
{
   rt_bars = new RtBar[n > 0 ? n : 1]; rt_n = n; rt_tick = tick; _Digits = digits; _Point = tick;
   for(int i = 0; i < n; i++) { rt_bars[i].t = t[i]; rt_bars[i].o = o[i]; rt_bars[i].h = h[i]; rt_bars[i].l = l[i]; rt_bars[i].c = c[i]; }
}

string _Symbol = "SYM";
ENUM_TIMEFRAMES _Period = PERIOD_M5;
int _Digits = 2;
double _Point = 0.01;
int _LastError = 0;
bool _StopFlag = false;
int _UninitReason = 0;
int _RandomSeed = 0;

// ---- strings ----
mqlstring& mqlstring::operator+=(const mqlstring& o) { *this = *this + o; return *this; }
mqlstring operator+(const mqlstring& a, const mqlstring& b)
{
   int n = a.n + b.n; char* buf = new char[n + 1];
   for(int i = 0; i < a.n; i++) buf[i] = a.s[i];
   for(int i = 0; i < b.n; i++) buf[a.n + i] = b.s[i];
   buf[n] = 0; mqlstring r(buf, (mq_size_t)n); delete[] buf; return r;
}
int rt_cmp(const mqlstring& a, const mqlstring& b)
{
   int m = a.n < b.n ? a.n : b.n;
   for(int i = 0; i < m; i++) if(a.s[i] != b.s[i]) return (uchar)a.s[i] < (uchar)b.s[i] ? -1 : 1;
   return a.n < b.n ? -1 : (a.n > b.n ? 1 : 0);
}
bool operator==(const mqlstring& a, const mqlstring& b) { return rt_cmp(a, b) == 0; }
bool operator!=(const mqlstring& a, const mqlstring& b) { return rt_cmp(a, b) != 0; }
bool operator<(const mqlstring& a, const mqlstring& b) { return rt_cmp(a, b) < 0; }
bool operator>(const mqlstring& a, const mqlstring& b) { return rt_cmp(a, b) > 0; }
bool operator<=(const mqlstring& a, const mqlstring& b) { return rt_cmp(a, b) <= 0; }
bool operator>=(const mqlstring& a, const mqlstring& b) { return rt_cmp(a, b) >= 0; }
mqlstring rt_n2s_d(double v) { char b[64]; snprintf(b, 64, "%.8g", v); return mqlstring(b); }
mqlstring rt_n2s_i(long long v) { char b[64]; snprintf(b, 64, "%lld", v); return mqlstring(b); }
int StringLen(const string& s) { return s.n; }
string StringSubstr(const string& s, int start, int len)
{
   if(start < 0) start = 0; if(start >= s.n) return string();
   if(len < 0 || start + len > s.n) len = s.n - start;
   return mqlstring(s.s + start, (mq_size_t)len);
}
int StringFind(const string& s, const string& m, int start)
{
   for(int i = start < 0 ? 0 : start; i + m.n <= s.n; i++) { int j = 0; while(j < m.n && s.s[i + j] == m.s[j]) j++; if(j == m.n) return i; }
   return -1;
}
int StringReplace(string& s, const string& f, const string& r)
{
   if(f.n == 0) return 0;
   int cnt = 0; string out; int i = 0;
   while(i < s.n) { if(i + f.n <= s.n && StringFind(StringSubstr(s, i, f.n), f) == 0) { out += r; i += f.n; cnt++; } else { out += StringSubstr(s, i, 1); i++; } }
   s = out; return cnt;
}
string DoubleToString(double v, int digits) { char b[400]; snprintf(b, 400, "%.*f", digits, v); return mqlstring(b); }
string IntegerToString(mql_long v, int len, ushort fill)
{
   char b[64]; snprintf(b, 64, "%lld", v); string r(b);
   while(r.n < len) r = mqlstring((const char*)&fill, 1) + r;
   return r;
}
struct RtArg { int k; double d; long long i; const mqlstring* s; };
inline RtArg rt_arg(const mqlstring& x) { RtArg a; a.k = 2; a.d = 0; a.i = 0; a.s = &x; return a; }
template<class T> RtArg rt_arg(const T& v)
{
   RtArg a; a.d = 0; a.i = 0; a.s = 0;
   if(mq_arith<typename mq_nocv<T>::type>::rank >= 9) { a.k = 1; a.d = (double)v; } else { a.k = 0; a.i = (long long)v; }
   return a;
}
string rt_format(const string& f, const RtArg* a, int na)
{
   string out; int ai = 0;
   for(int i = 0; i < f.n; i++)
   {
      if(f.s[i] != '%') { out += mqlstring(f.s + i, 1); continue; }
      if(i + 1 < f.n && f.s[i + 1] == '%') { out += mqlstring("%"); i++; continue; }
      char spec[40]; int sl = 0; spec[sl++] = '%'; i++;
      while(i < f.n && sl < 30 && (f.s[i] == '-' || f.s[i] == '+' || f.s[i] == ' ' || f.s[i] == '#' || f.s[i] == '0' || (f.s[i] >= '1' && f.s[i] <= '9') || f.s[i] == '.')) spec[sl++] = f.s[i++];
      while(i < f.n && (f.s[i] == 'l' || f.s[i] == 'h' || f.s[i] == 'I' || f.s[i] == '6' || f.s[i] == '4')) i++;
      char cv = i < f.n ? f.s[i] : 'd'; char buf[512];
      if(ai >= na) continue;
      const RtArg& A = a[ai++];
      if(cv == 's') { spec[sl++] = 's'; spec[sl] = 0; snprintf(buf, 512, spec, A.k == 2 && A.s->s ? A.s->s : ""); }
      else if(cv == 'f' || cv == 'e' || cv == 'g' || cv == 'E' || cv == 'G' || cv == 'F') { spec[sl++] = cv; spec[sl] = 0; snprintf(buf, 512, spec, A.k == 1 ? A.d : (double)A.i); }
      else if(cv == 'c') { spec[sl++] = 'c'; spec[sl] = 0; snprintf(buf, 512, spec, (int)A.i); }
      else { spec[sl++] = 'l'; spec[sl++] = 'l'; spec[sl++] = cv; spec[sl] = 0; snprintf(buf, 512, spec, A.k == 1 ? (long long)A.d : A.i); }
      out += mqlstring(buf);
   }
   return out;
}
template<class... A> string StringFormat(const string& fmt, const A&... a) { RtArg arr[] = { RtArg(), rt_arg(a)... }; return rt_format(fmt, arr + 1, (int)sizeof...(a)); }
template<class... A> void Print(const A&...) {}
template<class... A> void Alert(const A&...) {}
template<class... A> void Comment(const A&...) {}
template<class... A> void PrintFormat(const string&, const A&...) {}
template<class... A> bool SendNotification(const A&...) { return true; }

// ---- math ----
double MathSqrt(double v) { return __builtin_sqrt(v); }
double MathFloor(double v) { return __builtin_floor(v); }
double MathCeil(double v) { return __builtin_ceil(v); }
double MathRound(double v) { return __builtin_round(v); }
double MathPow(double a, double b) { return __builtin_pow(a, b); }
double MathLog(double v) { return __builtin_log(v); }
double MathLog10(double v) { return __builtin_log10(v); }
double MathExp(double v) { return __builtin_exp(v); }
double MathSin(double v) { return __builtin_sin(v); }
double MathCos(double v) { return __builtin_cos(v); }
double MathTan(double v) { return __builtin_tan(v); }
double MathArcsin(double v) { return __builtin_asin(v); }
double MathArccos(double v) { return __builtin_acos(v); }
double MathArctan(double v) { return __builtin_atan(v); }
double MathMod(double a, double b) { return __builtin_fmod(a, b); }
bool MathIsValidNumber(double v) { return v == v && v - v == 0; }
double NormalizeDouble(double v, int digits) { double p = 1; for(int i = 0; i < digits; i++) p *= 10; return __builtin_round(v * p) / p; }

// ---- arrays ----
template<class T> MqlArr<T>* rt_dyn(MqlArr<T>& a) { return &a; }
template<class T> MqlArr<T>* rt_dyn(ArrayView<T>& a) { return a.dyn; }
template<class A, class V> int ArrayInitialize(A& a, V v) { int n = ArraySize(a); for(int i = 0; i < n; i++) a[i] = v; return n; }
template<class T> void ArrayFree(MqlArr<T>& a) { a.resize(0); }
template<class T> void ArrayFree(ArrayView<T> a) { if(a.dyn) a.dyn->resize(0); }
template<class A> bool ArrayRemove(A& a, int start, int count)
{
   auto* q = rt_dyn(a); int n = q->n;
   if(start < 0 || start >= n) return false;
   if(count < 0 || start + count > n) count = n - start;
   for(int i = start; i + count < n; i++) q->p[i] = q->p[i + count];
   q->resize(n - count); return true;
}
template<class T> void ZeroMemory(T& v) { __builtin_memset(&v, 0, sizeof(v)); }
template<class A> bool ArraySetAsSeries(A&, bool) { return true; }

// ---- time ----
long long rt_days_from_civil(long long y, int m, int d)
{
   y -= m <= 2; long long era = (y >= 0 ? y : y - 399) / 400; long long yoe = y - era * 400;
   long long doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1; long long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
   return era * 146097 + doe - 719468;
}
bool TimeToStruct(datetime dt, MqlDateTime& o)
{
   long long days = dt / 86400, rem = dt % 86400; if(rem < 0) { rem += 86400; days--; }
   long long z = days + 719468; long long era = (z >= 0 ? z : z - 146096) / 146097; long long doe = z - era * 146097;
   long long yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365; long long y = yoe + era * 400;
   long long doy = doe - (365 * yoe + yoe / 4 - yoe / 100); long long mp = (5 * doy + 2) / 153;
   int d = (int)(doy - (153 * mp + 2) / 5 + 1); int m = (int)(mp < 10 ? mp + 3 : mp - 9); if(m <= 2) y++;
   o.year = (int)y; o.mon = m; o.day = d; o.hour = (int)(rem / 3600); o.min = (int)(rem % 3600 / 60); o.sec = (int)(rem % 60);
   long long wd = (days + 4) % 7; if(wd < 0) wd += 7; o.day_of_week = (int)wd;
   o.day_of_year = (int)(days - rt_days_from_civil(y, 1, 1));
   return true;
}
datetime StructToTime(MqlDateTime& d) { return rt_days_from_civil(d.year, d.mon, d.day) * 86400 + d.hour * 3600 + d.min * 60 + d.sec; }
string TimeToString(datetime v, int mode)
{
   MqlDateTime d; TimeToStruct(v, d); char b[64]; string r;
   if(mode & TIME_DATE) { snprintf(b, 64, "%04d.%02d.%02d", d.year, d.mon, d.day); r += mqlstring(b); }
   if(mode & TIME_MINUTES) { snprintf(b, 64, "%s%02d:%02d", r.n ? " " : "", d.hour, d.min); r += mqlstring(b); }
   if(mode & TIME_SECONDS) { snprintf(b, 64, "%s%02d:%02d:%02d", r.n ? " " : "", d.hour, d.min, d.sec); r += mqlstring(b); }
   return r;
}
datetime TimeCurrent() { return rt_n ? rt_bars[rt_n - 1].t : 0; }
datetime TimeCurrent(MqlDateTime& d) { TimeToStruct(TimeCurrent(), d); return TimeCurrent(); }
datetime TimeTradeServer() { return TimeCurrent(); }
datetime TimeLocal() { return TimeCurrent(); }
datetime TimeGMT() { return TimeCurrent(); }
int PeriodSeconds(ENUM_TIMEFRAMES p) { return 300; }

// ---- series (MT5 indexing: shift 0 = newest bar) ----
double iOpen(const string&, ENUM_TIMEFRAMES, int s) { return s < 0 || s >= rt_n ? 0 : rt_bars[rt_n - 1 - s].o; }
double iHigh(const string&, ENUM_TIMEFRAMES, int s) { return s < 0 || s >= rt_n ? 0 : rt_bars[rt_n - 1 - s].h; }
double iLow(const string&, ENUM_TIMEFRAMES, int s) { return s < 0 || s >= rt_n ? 0 : rt_bars[rt_n - 1 - s].l; }
double iClose(const string&, ENUM_TIMEFRAMES, int s) { return s < 0 || s >= rt_n ? 0 : rt_bars[rt_n - 1 - s].c; }
datetime iTime(const string&, ENUM_TIMEFRAMES, int s) { return s < 0 || s >= rt_n ? 0 : rt_bars[rt_n - 1 - s].t; }
mql_long iVolume(const string&, ENUM_TIMEFRAMES, int) { return 0; }
mql_long iTickVolume(const string&, ENUM_TIMEFRAMES, int) { return 0; }
mql_long iRealVolume(const string&, ENUM_TIMEFRAMES, int) { return 0; }
int Bars(const string&, ENUM_TIMEFRAMES) { return rt_n; }
int iBars(const string&, ENUM_TIMEFRAMES) { return rt_n; }
int iBarShift(const string&, ENUM_TIMEFRAMES, datetime t, bool exact)
{
   int lo = 0, hi = rt_n - 1, ans = -1;
   while(lo <= hi) { int mid = (lo + hi) / 2; if(rt_bars[mid].t <= t) { ans = mid; lo = mid + 1; } else hi = mid - 1; }
   if(ans < 0) return -1;
   if(exact && rt_bars[ans].t != t) return -1;
   return rt_n - 1 - ans;
}
double SymbolInfoDouble(const string&, ENUM_SYMBOL_INFO_DOUBLE id)
{
   if(id == SYMBOL_POINT || id == SYMBOL_TRADE_TICK_SIZE) return rt_tick;
   return 0;
}
bool SymbolInfoDouble(const string& n, ENUM_SYMBOL_INFO_DOUBLE id, double& v) { v = SymbolInfoDouble(n, id); return true; }
mql_long SymbolInfoInteger(const string&, ENUM_SYMBOL_INFO_INTEGER id) { return id == SYMBOL_DIGITS ? _Digits : 0; }
double AccountInfoDouble(ENUM_ACCOUNT_INFO_DOUBLE) { return 0; }
mql_long AccountInfoInteger(ENUM_ACCOUNT_INFO_INTEGER) { return 0; }
int MQLInfoInteger(ENUM_MQL_INFO_INTEGER) { return 0; }
int TerminalInfoInteger(ENUM_TERMINAL_INFO_INTEGER) { return 0; }
string Symbol() { return _Symbol; }
ENUM_TIMEFRAMES Period() { return _Period; }
int Digits() { return _Digits; }
double Point() { return _Point; }

// ---- no-ops: objects, chart, text, trade, account ----
bool ObjectCreate(mql_long, const string&, ENUM_OBJECT, int, datetime, double, datetime, double, datetime, double) { return true; }
bool ObjectDelete(mql_long, const string&) { return true; }
int ObjectsDeleteAll(mql_long, int, int) { return 0; }
int ObjectsDeleteAll(mql_long, const string&, int, int) { return 0; }
int ObjectFind(mql_long, const string&) { return -1; }
int ObjectsTotal(mql_long, int, int) { return 0; }
bool ObjectMove(mql_long, const string&, int, datetime, double) { return true; }
bool ObjectSetInteger(mql_long, const string&, ENUM_OBJECT_PROPERTY_INTEGER, mql_long) { return true; }
bool ObjectSetInteger(mql_long, const string&, ENUM_OBJECT_PROPERTY_INTEGER, int, mql_long) { return true; }
bool ObjectSetDouble(mql_long, const string&, ENUM_OBJECT_PROPERTY_DOUBLE, double) { return true; }
bool ObjectSetDouble(mql_long, const string&, ENUM_OBJECT_PROPERTY_DOUBLE, int, double) { return true; }
bool ObjectSetString(mql_long, const string&, ENUM_OBJECT_PROPERTY_STRING, const string&) { return true; }
bool ObjectSetString(mql_long, const string&, ENUM_OBJECT_PROPERTY_STRING, int, const string&) { return true; }
mql_long ObjectGetInteger(mql_long, const string&, ENUM_OBJECT_PROPERTY_INTEGER, int) { return 0; }
double ObjectGetDouble(mql_long, const string&, ENUM_OBJECT_PROPERTY_DOUBLE, int) { return 0; }
mql_long ChartID() { return 0; }
bool ChartRedraw(mql_long) { return true; }
mql_long ChartGetInteger(mql_long, ENUM_CHART_PROPERTY_INTEGER, int) { return 0; }
bool ChartGetInteger(mql_long, ENUM_CHART_PROPERTY_INTEGER, int, mql_long& v) { v = 0; return true; }
bool ChartSetInteger(mql_long, ENUM_CHART_PROPERTY_INTEGER, mql_long) { return true; }
bool TextSetFont(const string&, int, uint, int) { return true; }
bool TextGetSize(const string&, uint& w, uint& h) { w = 0; h = 0; return true; }
int PositionsTotal() { return 0; }
int OrdersTotal() { return 0; }
ulong PositionGetTicket(int) { return 0; }
ulong OrderGetTicket(int) { return 0; }
bool HistorySelect(datetime, datetime) { return true; }
int HistoryDealsTotal() { return 0; }
void ResetLastError() {}
int GetLastError() { return 0; }
CTrade::CTrade() {}
CTrade::~CTrade() {}
void CTrade::SetExpertMagicNumber(ulong) {}
void CTrade::SetDeviationInPoints(ulong) {}
bool CTrade::SetTypeFillingBySymbol(const string&) { return true; }
bool CTrade::Buy(double, const string&, double, double, double, const string&) { return false; }
bool CTrade::Sell(double, const string&, double, double, double, const string&) { return false; }
bool CTrade::BuyLimit(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }
bool CTrade::SellLimit(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }
bool CTrade::BuyStop(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }
bool CTrade::SellStop(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }
bool CTrade::OrderDelete(ulong) { return false; }
bool CTrade::PositionClose(ulong, ulong) { return false; }
bool CTrade::PositionModify(ulong, double, double) { return false; }
bool CTrade::PositionClosePartial(ulong, double, ulong) { return false; }
string CTrade::ResultRetcodeDescription() const { return string(); }
