"""EA (read only) -> ea_rt.cpp (MQL5 translated to C++ with the executable runtime) + grid entry points -> fbg_harness. Usage: build.py EA.mq5"""
import sys, os, subprocess
OUT = sys.argv[2] if len(sys.argv) > 2 else 'fbg_harness'
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
RUN = S + '/mq5check/run'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN)
subprocess.run([sys.executable, '-I', RUN + '/create_rt.py'], check=True, capture_output=True)
import mq5rt


def wrapper():
    L = ['#line 1 "<fbg-wrapper>"', 'extern "C" int rt_SetInput(const char* name, double v)', '{']
    for ty, nm in mq5rt.INPUTS:
        if ty == 'string': continue
        if ty == 'bool': cast = '(v != 0)'
        elif ty in ('int', 'uint', 'long', 'ulong', 'datetime', 'color', 'double', 'float', 'short', 'ushort', 'char', 'uchar'): cast = '(%s)v' % ('mql_long' if ty == 'long' else ty)
        else: cast = '(%s)(int)v' % ty
        L.append('   if(__builtin_strcmp(name, "%s") == 0) { %s = %s; return 1; }' % (nm, nm, cast))
    L += ['   return 0;', '}', '''
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
''']
    return '\n'.join(L) + '\n'


mq5rt.rt_wrapper = wrapper
ea = os.path.abspath(sys.argv[1])
cp = HERE + '/EA_copy.mq5'
open(cp, 'w').write(open(ea).read())                     # the source is only read
mq5rt.MAIN_FILE[0] = cp
cpp, _ = mq5rt.build_cpp(cp)
open(HERE + '/ea_rt.cpp', 'w').write(cpp)
for cmd in (['clang++', '-std=c++17', '-O2', '-w', '-c', HERE + '/ea_rt.cpp', '-o', HERE + '/ea_rt.o'],
            ['clang++', '-std=c++17', '-O2', '-c', HERE + '/driver.cpp', '-o', HERE + '/driver.o'],
            ['clang++', '-O2', HERE + '/driver.o', HERE + '/ea_rt.o', '-o', HERE + '/' + OUT]):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[:4000]); sys.exit(1)
print('built %s (%d inputs)' % (OUT, len(mq5rt.INPUTS)))
