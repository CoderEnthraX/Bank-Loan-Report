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
void rec_take();
void rec_part(double np);
void rec_close();
int rec_capstop();
void rec_init();
}
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
   FILE* f = std::fopen(argv[1], "r");
   if(!f) return 2;
   double res, c; int k;
   while(std::fscanf(f, "%lf %lf %d", &res, &c, &k) == 3)
   {
      std::vector<double> pr(k), pw(k);
      for(int j = 0; j < k; j++) if(std::fscanf(f, "%lf %lf", &pr[j], &pw[j]) != 2) return 3;
      double r = rec_next(exitR);
      if(rec_capstop()) { std::printf("STOP\n"); break; }
      rec_take();
      if(k == 0) rec_part(r * (res - c) / (1.0 + c));
      else for(int j = 0; j < k; j++) rec_part(r * (pr[j] - pw[j] * c) / (1.0 + c));
      rec_close();
      std::printf("R %.12g\n", r);
   }
   std::fclose(f);
   return 0;
}
