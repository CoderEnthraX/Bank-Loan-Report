// fbg_harness DATA_DIR TFLIST [NAME=VALUE ...]: the EA's own rules (gSim) on the 1-minute bars of DATA_DIR: every bar = open, the nearer of
// high / low, the other, close (the research's path); before it, the candles of each strategy's timeframe (TFLIST: 12 names, e.g.
// D1,D1,D1,H4,H1,...) that closed by then, and (TREND=name) the trend timeframe's closes. Prints every closed trade:
// "T id entryTime entry exitTime exit reason risk" and at the end "E id equity net trades inTrade stopped".
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <map>
extern "C" {
int rt_SetInput(const char* name, double v);
void h_setup(); int h_ok(int i); void h_push(int i, double high, long long t, long long tNow); void h_trend(double c);
void h_barend(); void h_begin(long long T, double o); void h_move(double y); int h_logn(); void h_log(int k, double* o); void h_end(int i, double* o);
void h_restart(); void h_repush(int i, double high, long long t, long long tNow); void h_trend_reset();
}
struct Ser { std::vector<long long> t; std::vector<double> o, h, l, c; };
static bool load(const std::string& path, Ser& s, bool full)
{
   FILE* f = std::fopen(path.c_str(), "rb"); if(!f) return false;
   long long n = 0; if(std::fread(&n, 8, 1, f) != 1) return false;
   s.t.resize(n); s.o.resize(n); s.h.resize(n); s.l.resize(n); s.c.resize(n);
   bool ok = std::fread(s.t.data(), 8, n, f) == (size_t)n && std::fread(s.o.data(), 8, n, f) == (size_t)n && std::fread(s.h.data(), 8, n, f) == (size_t)n &&
             std::fread(s.l.data(), 8, n, f) == (size_t)n && std::fread(s.c.data(), 8, n, f) == (size_t)n;
   std::fclose(f); return ok;
}
int main(int argc, char** argv)
{
   if(argc < 3) { std::fprintf(stderr, "usage\n"); return 2; }
   std::string dir = argv[1];
   std::vector<std::string> tfs; { std::string a = argv[2]; size_t p = 0; while(p <= a.size()) { size_t q = a.find(',', p); if(q == std::string::npos) q = a.size(); tfs.push_back(a.substr(p, q - p)); p = q + 1; } }
   if(tfs.size() != 12) { std::fprintf(stderr, "12 timeframes needed\n"); return 2; }
   std::string trend;
   for(int i = 3; i < argc; i++)
   {
      std::string a = argv[i]; size_t p = a.find('=');
      if(p == std::string::npos) return 2;
      if(a.substr(0, p) == "TREND") { trend = a.substr(p + 1); continue; }
      if(!rt_SetInput(a.substr(0, p).c_str(), std::atof(a.c_str() + p + 1))) { std::fprintf(stderr, "bad input %s\n", argv[i]); return 2; }
   }
   h_setup();
   Ser m1; if(!load(dir + "/M1.bin", m1, true)) { std::fprintf(stderr, "no M1\n"); return 3; }
   std::map<std::string, Ser> ser; ser["M1"] = m1;
   for(auto& k : tfs) if(!ser.count(k)) { Ser s; if(!load(dir + "/" + k + ".bin", s, false)) { std::fprintf(stderr, "no %s\n", k.c_str()); return 3; } ser[k] = s; }
   if(!trend.empty() && !ser.count(trend)) { Ser s; if(!load(dir + "/" + trend + ".bin", s, false)) return 3; ser[trend] = s; }
   std::map<std::string, size_t> cur; for(auto& kv : ser) cur[kv.first] = 0;
   std::vector<size_t> pushed(12, 0); size_t pushedTr = 0;
   size_t n = m1.t.size();
   long long rsk = std::getenv("FBG_RESTART") ? std::atoll(std::getenv("FBG_RESTART")) : 0;   // a restart every rsk bars (0 = never)
   int nrs = 0;
   for(size_t i = 0; i < n; i++)
   {
      long long T = m1.t[i];
      for(auto& kv : ser) { size_t& c = cur[kv.first]; const Ser& s = kv.second; while(c + 1 < s.t.size() && s.t[c + 1] <= T) c++; }
      if(rsk > 0 && i > 0 && i % rsk == 0)
      {
         h_restart(); nrs++;
         for(int k = 0; k < 12; k++)
         {
            if(!h_ok(k)) continue;
            const Ser& s = ser[tfs[k]]; size_t c = cur[tfs[k]];
            for(size_t j = 0; j < pushed[k]; j++) h_repush(k, s.h[j], s.t[j], s.t[c]);
         }
         if(!trend.empty()) { h_trend_reset(); const Ser& s = ser[trend]; for(size_t j = 0; j < pushedTr; j++) h_trend(s.c[j]); }
      }
      h_barend();
      for(int k = 0; k < 12; k++)
      {
         if(!h_ok(k)) continue;
         const Ser& s = ser[tfs[k]]; size_t c = cur[tfs[k]];
         while(pushed[k] < c) { size_t j = pushed[k]; h_push(k, s.h[j], s.t[j], s.t[c]); pushed[k]++; }
      }
      if(!trend.empty()) { const Ser& s = ser[trend]; size_t c = cur[trend]; while(pushedTr < c) { h_trend(s.c[pushedTr]); pushedTr++; } }
      double o = m1.o[i], h = m1.h[i], l = m1.l[i], cl = m1.c[i];
      h_begin(T, o);
      bool hf = (h - o) < (o - l);
      h_move(hf ? h : l); h_move(hf ? l : h); h_move(cl);
   }
   double v[7];
   for(int k = 0; k < h_logn(); k++) { h_log(k, v); std::printf("T %d %lld %.10f %lld %.10f %d %.10f\n", (int)v[0], (long long)v[1], v[2], (long long)v[3], v[4], (int)v[5], v[6]); }
   for(int k = 0; k < 12; k++) { h_end(k, v); std::printf("E %d %.6f %.6f %d %d %d\n", k + 1, v[0], v[1], (int)v[2], (int)v[3], (int)v[4]); }
   if(rsk > 0) std::printf("R %d restarts\n", nrs);
   return 0;
}
