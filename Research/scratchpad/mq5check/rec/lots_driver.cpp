// lots_driver NAME=VALUE ... -- risk sd entry isL ld tv spread vstep vmin equity: prints the EA's LotsFor() result
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
extern "C" {
int rt_SetInput(const char* name, double v);
double rec_lots(double risk, double sd, double entry, int isL, double ld, double tv, double spread, double vstep, double vmin, double eq);
}
int main(int argc, char** argv)
{
   int i = 1;
   for(; i < argc && std::strcmp(argv[i], "--") != 0; i++)
   {
      std::string a = argv[i]; size_t p = a.find('=');
      if(p == std::string::npos || !rt_SetInput(a.substr(0, p).c_str(), std::atof(a.c_str() + p + 1))) { std::fprintf(stderr, "bad input %s\n", argv[i]); return 2; }
   }
   if(argc - i - 1 != 10) { std::fprintf(stderr, "need 10 numbers after --\n"); return 2; }
   double v[10]; for(int k = 0; k < 10; k++) v[k] = std::atof(argv[i + 1 + k]);
   std::printf("%.8f\n", rec_lots(v[0], v[1], v[2], (int)v[3], v[4], v[5], v[6], v[7], v[8], v[9]));
   return 0;
}
