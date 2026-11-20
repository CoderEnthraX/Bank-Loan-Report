// mrs_driver SEQ.txt EXITR [NAME=VALUE ...] (v4.8): the EA's own NextRisk() / BookClosed() and its monthly restart (MonthTick + MonthRestart)
// on a trade sequence with month marks. SEQ.txt lines: "M" = a new calendar month starts (the EA is flat); a trade "res c rmin k pr1 pw1 ...".
// Prints "R risk" per traded trade, "STOP" when the hard cap stops trading, "SKIP" for a trade after that in the same month.
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
extern "C" {
int rt_SetInput(const char* name, double v);
double rec_next_m(double exitR, double minRisk, double eq);
double rec_next_k(double exitR, double minRisk, double eq, double kRisk);
void rec_take(); void rec_part(double np); void rec_close(); int rec_capstop(); void rec_init();
void rec_mtick(long long t); int rec_mrestart(); void rec_restart();
void rec_setup(double risk, double spread);
int rec_cool();
}
static long rs_k = 0, rs_c = 0;
static void rp() { if(rs_k > 0 && ++rs_c % rs_k == 0) rec_restart(); }   // REC_RESTART=k: a restart (save, fresh load, reload) at every k-th point
int main(int argc, char** argv)
{
   if(argc < 3) return 2;
   double exitR = std::atof(argv[2]);
   for(int i = 3; i < argc; i++)
   {
      std::string a = argv[i]; size_t p = a.find('=');
      if(p == std::string::npos || !rt_SetInput(a.substr(0, p).c_str(), std::atof(a.c_str() + p + 1))) { std::fprintf(stderr, "bad input %s\n", argv[i]); return 2; }
   }
   rec_init();
   if(std::getenv("REC_RESTART")) rs_k = std::atol(std::getenv("REC_RESTART"));
   bool km_on = std::getenv("REC_KMIN") != nullptr;
   bool sd_on = std::getenv("REC_SD") != nullptr;
   long long t = 1609459200LL;                          // 1 Jan 2021 (any month start; only the change of month matters)
   rec_mtick(t);
   FILE* f = std::fopen(argv[1], "r");
   if(!f) return 2;
   char tok[64]; double eq0 = std::getenv("REC_START") ? std::atof(std::getenv("REC_START")) : 1e12, net = 0;
   while(std::fscanf(f, "%63s", tok) == 1)
   {
      if(tok[0] == 'M') { t += 32LL * 86400LL; rec_mtick(t); rp(); if(!rec_mrestart()) { std::printf("NORESTART\n"); return 4; } rp(); net = 0; continue; }
      double res = std::atof(tok), c, rmin, kr = 0; int k;
      if(std::fscanf(f, "%lf %lf", &c, &rmin) != 2) return 3;
      if(km_on && std::fscanf(f, "%lf", &kr) != 1) return 3;   // v5.0 REC_KMIN: the Crooks K careful lots' $ risk after the 0.01-lot risk
      double sdd = 0;
      if(sd_on && std::fscanf(f, "%lf", &sdd) != 1) return 3;   // v5.1 REC_SD: the setup's stop distance (Size by Profit sizes from it)
      if(std::fscanf(f, "%d", &k) != 1) return 3;
      std::vector<double> pr(k), pw(k);
      for(int j = 0; j < k; j++) if(std::fscanf(f, "%lf %lf", &pr[j], &pw[j]) != 2) return 3;
      if(rec_capstop()) { std::printf("SKIP\n"); continue; }
      if(rec_cool()) { std::printf("SKIP\n"); continue; }   // v5.4 Cooling-off
      if(sd_on) rec_setup(sdd, 0.0);
      double r = km_on ? rec_next_k(exitR, rmin, eq0 + net, kr) : rec_next_m(exitR, rmin, eq0 + net);
      if(rec_capstop()) { std::printf("STOP\n"); continue; }
      rp(); rec_take(); rp();
      if(k == 0) { double np = r * (res - c) / (1.0 + c); net += np; rec_part(np); rp(); }
      else for(int j = 0; j < k; j++) { double np = r * (pr[j] - pw[j] * c) / (1.0 + c); net += np; rec_part(np); rp(); }
      rec_close(); rp();
      std::printf("R %.12g\n", r);
   }
   std::fclose(f);
   return 0;
}
