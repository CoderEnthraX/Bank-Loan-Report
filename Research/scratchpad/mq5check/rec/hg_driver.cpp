// hg_driver FORGET HEDGEOK: the EA's own NextRisk / CrkRecNext / BookClosed through a scripted Crooks C sequence that triggers the hedge rule
#include <cstdio>
#include <cstdlib>
extern "C" {
int rt_SetInput(const char* name, double v);
double rec_next(double exitR); void rec_take(); void rec_part(double np); void rec_close(); void rec_init();
void rec_hgok(int on); void rec_hgclose(double lastOut); int rec_hgnow(); double rec_owed();
}
static double X = 0.6;
static void trade(const char* what, double res) { double r = rec_next(X); rec_take(); double p = res * r; rec_part(p);
   rec_close(); std::printf("%-34s risk %8.2f  result %+8.2f  owed after %8.2f  hedge next %d\n", what, r, p, rec_owed(), rec_hgnow()); }
int main(int argc, char** argv)
{
   int forget = std::atoi(argv[1]), ok = std::atoi(argv[2]); double lastLeg = argc > 3 ? std::atof(argv[3]) : -1.0;
   const char* in[][2] = {{"InpRec", "20"}, {"InpCrkPr", "5"}, {"InpCrkPrN", "2"}, {"InpBaseRisk", "50"}, {"InpCommLot", "0"}, {"InpSpread", "0"},
                          {"InpCrkT1", "0"}, {"InpExitAt", "1"}, {"InpTp1R", "0.6"}, {"InpCapOn", "0"}};
   for(auto& kv : in) if(!rt_SetInput(kv[0], std::atof(kv[1]))) { std::printf("bad input %s\n", kv[0]); return 2; }
   rt_SetInput("InpCrkHgForget", forget);
   rec_init(); rec_hgok(ok);
   trade("1 base, loses", -1.0);
   trade("2 base, wins", 0.6);
   trade("3 recovery, loses (1 in a row)", -1.0);
   trade("4 base, wins", 0.6);
   trade("5 recovery, loses (2 in a row)", -1.0);
   double r = rec_next(X); int hg = rec_hgnow(); rec_take();
   double net = 0.6 * r - 1.0 * r;                       // pair: one take profit (+0.6R), one stop loss (-1R)
   rec_part(net); rec_hgclose(lastLeg * r);
   std::printf("%-34s risk %8.2f  result %+8.2f  owed after %8.2f  hedge next %d  (pair placed: %d)\n", "6 HEDGE PAIR, TP then SL", r, net, rec_owed(), rec_hgnow(), hg);
   trade("7 next trade, wins", 0.6);
   trade("8 next trade, wins", 0.6);
   return 0;
}
