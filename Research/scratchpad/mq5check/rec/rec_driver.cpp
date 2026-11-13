// rec_driver SEQ.txt EXITR [NAME=VALUE ...]: runs the EA's own NextRisk() / BookClosed() on a trade sequence and prints the $ risk of each trade.
// SEQ.txt: one trade per line "res c k pr1 pw1 ... prk pwk" (R result, spread cost in R, parts of a partial close). "STOP" = the hard cap stopped trading.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
extern "C" {
int rt_SetInput(const char* name, double v);
double rec_next(double exitR);
double rec_next_m(double exitR, double minRisk, double eq);
double rec_next_t1(double exitR, double eq);
void rec_take();
void rec_part(double np);
void rec_close();
int rec_capstop();
void rec_init();
void rec_setup(double risk, double spread);
int rec_t1();
void rec_day(int counted);
int rec_paused();
void rec_restart();
}
// v4.5 REC_MIN=1: every trade line has the Crooks E / I small-lot $ risk right after the cost ("res c rmin k ..."); REC_START=x: the equity the
// EA sees (Crooks H) is x + the P&L so far (default 1e12, like the simulator's start in the parity scripts)
static bool rm_on = false; static double eq0 = 1e12, net = 0.0;
// REC_RESTART=k: a restart (save, fresh load, reload) at every k-th point between the steps of the trades (0 / unset = never)
static long rs_k = 0, rs_c = 0;
static void rp() { if(rs_k > 0 && ++rs_c % rs_k == 0) rec_restart(); }
int main(int argc, char** argv)
{
   if(argc < 3) { std::fprintf(stderr, "usage: %s seq.txt exitR [NAME=VALUE ...]\n", argv[0]); return 2; }
   double exitR = std::atof(argv[2]);
   for(int i = 3; i < argc; i++)
   {
      std::string a = argv[i]; size_t p = a.find('=');
      if(p == std::string::npos || !rt_SetInput(a.substr(0, p).c_str(), std::atof(a.c_str() + p + 1))) { std::fprintf(stderr, "bad input %s\n", argv[i]); return 2; }
   }
   rec_init();
   if(std::getenv("REC_RESTART")) rs_k = std::atol(std::getenv("REC_RESTART"));
   rm_on = std::getenv("REC_MIN") != nullptr; if(std::getenv("REC_START")) eq0 = std::atof(std::getenv("REC_START"));
   FILE* f = std::fopen(argv[1], "r");
   if(!f) return 2;
   if(std::getenv("REC_DAYS"))
   {
      // Crooks C rule mode: "nd d1 .. dnd res c k pr1 pw1 ..." per signal: the new days before it (1 = counted), then the trade; a signal the
      // skip rule pauses prints SKIP and is not traded
      int nd;
      while(std::fscanf(f, "%d", &nd) == 1)
      {
         for(int j = 0; j < nd; j++) { int dv; if(std::fscanf(f, "%d", &dv) != 1) return 3; rec_day(dv); rp(); }
         double res, c, rmin = 0; int k;
         if(std::fscanf(f, "%lf %lf", &res, &c) != 2) return 3;
         if(rm_on && std::fscanf(f, "%lf", &rmin) != 1) return 3;
         if(std::fscanf(f, "%d", &k) != 1) return 3;
         std::vector<double> pr(k), pw(k);
         for(int j = 0; j < k; j++) if(std::fscanf(f, "%lf %lf", &pr[j], &pw[j]) != 2) return 3;
         if(rec_paused()) { std::printf("SKIP\n"); continue; }
         double r = rec_next_m(exitR, rmin, eq0 + net);
         if(rec_capstop()) { std::printf("STOP\n"); break; }
         rp(); rec_take(); rp();
         if(k == 0) { double np = r * (res - c) / (1.0 + c); net += np; rec_part(np); rp(); }
         else for(int j = 0; j < k; j++) { double np = r * (pr[j] - pw[j] * c) / (1.0 + c); net += np; rec_part(np); rp(); }
         rec_close(); rp();
         std::printf("R %.12g\n", r);
      }
      std::fclose(f);
      return 0;
   }
   if(std::getenv("REC_T1"))
   {
      // TP1 mode: "risk spread u" per taken trade; prints the $ risk and whether the TP1 rule was used
      double risk, spr, u;
      while(std::fscanf(f, "%lf %lf %lf", &risk, &spr, &u) == 3)
      {
         rec_setup(risk, spr);
         double r = rec_next_t1(exitR, eq0 + net);
         if(rec_capstop()) { std::printf("STOP\n"); break; }
         int t1 = rec_t1();
         rec_take(); rp();
         net += r * u; rec_part(r * u); rp();
         rec_close(); rp();
         std::printf("R %.12g %d\n", r, t1);
      }
      std::fclose(f);
      return 0;
   }
   double res, c; int k;
   while(std::fscanf(f, "%lf %lf", &res, &c) == 2)
   {
      double rmin = 0;
      if(rm_on && std::fscanf(f, "%lf", &rmin) != 1) return 3;
      if(std::fscanf(f, "%d", &k) != 1) return 3;
      std::vector<double> pr(k), pw(k);
      for(int j = 0; j < k; j++) if(std::fscanf(f, "%lf %lf", &pr[j], &pw[j]) != 2) return 3;
      double r = rec_next_m(exitR, rmin, eq0 + net);
      if(rec_capstop()) { std::printf("STOP\n"); break; }
      rp(); rec_take(); rp();
      if(k == 0) { double np = r * (res - c) / (1.0 + c); net += np; rec_part(np); rp(); }
      else for(int j = 0; j < k; j++) { double np = r * (pr[j] - pw[j] * c) / (1.0 + c); net += np; rec_part(np); rp(); }
      rec_close(); rp();
      std::printf("R %.12g\n", r);
   }
   std::fclose(f);
   return 0;
}
