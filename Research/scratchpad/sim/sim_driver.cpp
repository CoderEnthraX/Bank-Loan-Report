// Broker-simulator driver: sim M1.csv START END [KEY=VALUE ...] [InpX=value ...]
// Ticks: 4 per M1 bar (open, low/high in the bar's direction, close at :00 :15 :30 :45), spread = the bar's spread x (1 + JIT x u), u in [-1, 1].
// The EA starts at START (YYYY-MM-DD, server time) on M5 bars built from the ticks; the history before START warms it up.
// KEY: JIT, SEED, STOPS (points), COMM (per lot per side), RESTART=n (EA restart every n ticks: OnDeinit, a fresh program load, OnInit),
//      OFF=k (the EA stays off k ticks at each restart), REINIT=n (new inputs every n ticks: OnDeinit + OnInit, globals kept),
//      EXT=k (every k-th trade is closed by hand from the phone app HOLD ticks after it opened), HOLD, EXTMAGIC (close by another EA: its magic)
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
extern "C" {
int rt_SetInput(const char* name, double v);
void sim_load_cap(int n);
void sim_tick(long long t, double bid, double ask, int gmtoff);
int sim_init();
void sim_ontick();
void sim_deinit(int r);
void rec_fresh();
int sim_live();
int sim_ext_close(int reason, long long magic);
void sim_cfg(int stops, double comm);
int sim_bars();
void sim_set_tf(int m);
void sim_gv_set(const char* n, double v);
double sim_gv_get(const char* n);
void sim_set_chart(long long me, int n, const long long* ids, int withEa);
void sim_conn(int c);
void sim_vw_report(double vwapNow);
double sim_vwap();
}
static long long day(const char* s) { int y, m, d; std::sscanf(s, "%d-%d-%d", &y, &m, &d); y -= m <= 2; long long era = (y >= 0 ? y : y - 399) / 400; long long yoe = y - era * 400;
   long long doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1; long long doe = yoe * 365 + yoe / 4 - yoe / 100 + doy; return (era * 146097 + doe - 719468) * 86400; }
static unsigned long long rng = 88172645463325252ULL;
static double urand() { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return (double)(rng >> 11) / 9007199254740992.0; }

int main(int argc, char** argv)
{
   if(argc < 4) { std::fprintf(stderr, "usage: %s m1.csv START END [KEY=VALUE ...]\n", argv[0]); return 2; }
   long long t0 = day(argv[2]), t1 = day(argv[3]);
   std::string altName; double altVal = 0;              // ALT=InpName:value -> that input changes at every REINIT (new inputs that change the engine)
   double jit = 0, comm = 0; int stops = 0; long long restart = 0, off = 0, reinit = 0, ext = 0, hold = 40, extMagic = -1, tfsw = 0, tflen = 60, tfAt = -1, lockTest = 0, disc = 0, discLeft = 0; double gmtFix = -99;
   std::vector<std::pair<std::string, double>> inp;
   inp.push_back({"InpDraw", 0}); inp.push_back({"InpShowTable", 0});
   for(int i = 4; i < argc; i++)
   {
      std::string a = argv[i]; size_t p = a.find('=');
      if(p == std::string::npos) { std::fprintf(stderr, "bad arg %s\n", argv[i]); return 2; }
      std::string k = a.substr(0, p); double v = std::atof(a.c_str() + p + 1);
      if(k == "JIT") jit = v; else if(k == "SEED") rng = 88172645463325252ULL + (unsigned long long)(v * 7919); else if(k == "STOPS") stops = (int)v;
      else if(k == "COMM") comm = v; else if(k == "RESTART") restart = (long long)v; else if(k == "OFF") off = (long long)v;
      else if(k == "REINIT") reinit = (long long)v; else if(k == "EXT") ext = (long long)v; else if(k == "HOLD") hold = (long long)v;
      else if(k == "EXTMAGIC") extMagic = (long long)v; else if(k == "TFSW") tfsw = (long long)v; else if(k == "TFLEN") tflen = (long long)v; else if(k == "LOCKTEST") lockTest = (long long)v; else if(k == "GMTOFF") gmtFix = v; else if(k == "DISC") disc = (long long)v;
      else if(k == "ALT") { size_t c = a.find(':'); altName = a.substr(p + 1, c - p - 1); altVal = std::atof(a.c_str() + c + 1); }
      else inp.push_back({k, v});
   }
   FILE* f = std::fopen(argv[1], "r");
   if(!f) { std::fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
   std::vector<long long> T; std::vector<int> G; std::vector<double> O, H, L, C, SP;
   char line[256];
   while(std::fgets(line, sizeof line, f))
   {
      long long s; int g; double o, h, l, c, sp;
      if(std::sscanf(line, "%lld,%d,%lf,%lf,%lf,%lf,%lf", &s, &g, &o, &h, &l, &c, &sp) == 7 && s < t1) { T.push_back(s); G.push_back(g); O.push_back(o); H.push_back(h); L.push_back(l); C.push_back(c); SP.push_back(sp); }
   }
   std::fclose(f);
   sim_load_cap((int)T.size() + 10);
   sim_cfg(stops, comm);
   for(auto& kv : inp) if(!rt_SetInput(kv.first.c_str(), kv.second)) { std::fprintf(stderr, "unknown input %s\n", kv.first.c_str()); return 2; }
   bool on = false; long long nTick = 0, offLeft = 0, nOpen = 0, openAt = -1, inits = 0; int prevLive = 0;
   for(size_t i = 0; i < T.size(); i++)
   {
      bool up = C[i] >= O[i];
      double px[4] = {O[i], up ? L[i] : H[i], up ? H[i] : L[i], C[i]};
      for(int k = 0; k < 4; k++)
      {
         long long t = T[i] + 15 * k;
         double sp = SP[i] * (1.0 + jit * (2.0 * urand() - 1.0)); if(sp < 0.05) sp = 0.05;
         sp = (double)(long long)(sp * 100.0 + 0.5) / 100.0;
         sim_tick(t, px[k], px[k] + sp, gmtFix > -90 ? (int)(gmtFix * 3600) : G[i]);
         if(t < t0) continue;
         if(!on && offLeft == 0)
         {
            if(lockTest)                                           // another chart (202) runs this EA and holds the lock of this symbol + magic number
            {
               long long ids[2] = {101, 202}; sim_set_chart(101, 2, ids, 1);
               if(lockTest == 2) { long long one[1] = {101}; sim_set_chart(101, 1, one, 1); }   // 2: that chart is gone (a stale lock)
               sim_gv_set("ARX|SYM|240611|run", (double)(202 & 0xFFFFFFFFFFFFLL) + 1.0);
               int r = sim_init(); std::printf("LOCKTEST %lld: OnInit returned %d, lock now %.0f\n", lockTest, r, sim_gv_get("ARX|SYM|240611|run")); return 0;
            }
            if(sim_init() != 0) { std::printf("INIT FAILED\n"); return 1; } on = true; inits++; continue;
         }
         if(discLeft > 0) { if(--discLeft == 0) { sim_conn(1); std::printf("DRIVER connected at tick %lld\n", nTick); } continue; }   // MT5 started offline: no ticks reach the EA
         if(offLeft > 0) { if(--offLeft == 0) { rec_fresh(); if(sim_init() != 0) { std::printf("INIT FAILED (restart)\n"); return 1; } on = true; inits++; } continue; }
         nTick++;
         int live = sim_live();
         if(live > 0 && prevLive == 0) { nOpen++; openAt = nTick; }
         prevLive = live;
         if(ext > 0 && live > 0 && openAt > 0 && nTick == openAt + hold && nOpen % ext == 0)
         {
            std::printf("DRIVER close by %s at tick %lld\n", extMagic >= 0 ? "another EA" : "hand (phone)", nTick);
            sim_ext_close(extMagic >= 0 ? 3 : 1, extMagic >= 0 ? extMagic : 0); prevLive = sim_live();
         }
         if(restart > 0 && nTick % restart == 0)
         {
            std::printf("DRIVER restart at tick %lld (off %lld ticks)\n", nTick, off);
            sim_deinit(9); on = false;
            if(disc) { rec_fresh(); sim_conn(0); if(sim_init() != 0) { std::printf("INIT FAILED (offline start)\n"); return 1; } on = true; inits++; discLeft = off > 0 ? off : 1; continue; }   // MT5 starts before it connects: old history, then the missed bars
            if(off > 0) { offLeft = off; continue; }
            rec_fresh(); if(sim_init() != 0) { std::printf("INIT FAILED (restart)\n"); return 1; } on = true; inits++;
            continue;
         }
         if(tfsw > 0 && (nTick % tfsw == 0 || nTick == tfAt))      // the chart switched to M1 and, TFLEN ticks later, back to M5 (globals kept)
         {
            bool toM1 = nTick % tfsw == 0; if(toM1) tfAt = nTick + tflen;
            std::printf("DRIVER timeframe switch to %s at tick %lld\n", toM1 ? "M1" : "M5", nTick);
            sim_deinit(3); sim_set_tf(toM1 ? 1 : 5); if(sim_init() != 0) { std::printf("INIT FAILED (timeframe)\n"); return 1; } inits++;
            continue;
         }
         if(reinit > 0 && nTick % reinit == 0)
         {
            std::printf("DRIVER new inputs at tick %lld\n", nTick);
            sim_deinit(5);
            if(!altName.empty()) { static bool alt = false; static double orig = 0; static bool got = false;
               if(!got) { for(auto& kv : inp) if(kv.first == altName) orig = kv.second; got = true; }
               alt = !alt; rt_SetInput(altName.c_str(), alt ? altVal : orig); std::printf("DRIVER %s = %g\n", altName.c_str(), alt ? altVal : orig); }
            if(sim_init() != 0) { std::printf("INIT FAILED (new inputs)\n"); return 1; } inits++;
            continue;
         }
         sim_ontick();
      }
   }
   sim_vw_report(sim_vwap());
   std::printf("END ticks %lld bars %d inits %lld trades opened %lld\n", nTick, sim_bars(), inits, nOpen);
   return 0;
}
