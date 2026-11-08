// month_driver: the EA's own MonthTick / MonthCheck / RecoveryRestart through scripted months (v4.2 monthly profit lock)
#include <cstdio>
#include <cstdlib>
extern "C" {
int rt_SetInput(const char* name, double v);
double rec_next(double exitR); void rec_take(); void rec_part(double np); void rec_close(); void rec_init(); double rec_owed();
void rec_mtick(long long t); void rec_mpnl(double p); int rec_mcheck(); int rec_mrestart(); double rec_mpeak();
}
static const long long OCT = 1792022400LL, NOV = 1793577600LL;
static double tot = 0;
static void pnl(double p) { rec_mpnl(p); tot += p; int st = rec_mcheck(); std::printf("   trade %+8.2f  month %+8.2f  high %8.2f  -> %s\n", p, tot, rec_mpeak(), st ? "STOP for the month" : "keep trading"); }
int main()
{
   const char* in[][2] = {{"InpRec", "20"}, {"InpBaseRisk", "50"}, {"InpCommLot", "0"}, {"InpSpread", "0"}, {"InpCrkT1", "0"}, {"InpExitAt", "1"}, {"InpTp1R", "0.6"}};
   for(auto& kv : in) rt_SetInput(kv[0], std::atof(kv[1]));
   rec_init();
   std::printf("1) Stop for the month once it is up $150\n"); rt_SetInput("InpMLockOn", 1); rt_SetInput("InpMLockAmt", 150);
   rec_mtick(OCT); tot = 0; pnl(60); pnl(50); pnl(45);
   rec_mtick(NOV); tot = 0; std::printf("   new month -> %s\n", rec_mcheck() ? "STOP" : "trading again"); rt_SetInput("InpMLockOn", 0);
   std::printf("2) Lock profit once the month is up $500, lock 20%% of the high\n"); rt_SetInput("InpPLockOn", 1); rt_SetInput("InpPLockAt", 500); rt_SetInput("InpPLockPct", 20);
   rec_mtick(OCT); tot = 0; pnl(300); pnl(250); pnl(-200); pnl(300); pnl(-400); pnl(-119); pnl(-2);
   rec_mtick(NOV); tot = 0; std::printf("   new month -> %s\n", rec_mcheck() ? "STOP" : "trading again"); rt_SetInput("InpPLockOn", 0);
   std::printf("3) Restart the loss recovery on the 1st (Crooks C)\n"); rt_SetInput("InpMRestart", 1);
   rec_mtick(OCT);
   double r = rec_next(0.6); rec_take(); rec_part(-r); rec_close(); std::printf("   Oct: base trade risk %.2f lost, owed %.2f\n", r, rec_owed());
   r = rec_next(0.6); rec_take(); rec_part(0.6 * r); rec_close(); std::printf("   Oct: base trade risk %.2f won, owed %.2f, next risk %.2f (recovery)\n", r, rec_owed(), rec_next(0.6));
   rec_mtick(NOV); int did = rec_mrestart(); std::printf("   1 Nov: restart %s, owed %.2f, next risk %.2f\n", did ? "done" : "NOT done", rec_owed(), rec_next(0.6));
   rt_SetInput("InpMRestart", 0); rec_mtick(OCT + 86400LL * 40);
   r = rec_next(0.6); rec_take(); rec_part(-r); rec_close(); rec_mtick(OCT + 86400LL * 80); did = rec_mrestart();
   std::printf("   restart off: next month restart %s, owed %.2f (kept)\n", did ? "done" : "not done", rec_owed());
   std::printf("4) Trades booked by the EA (BookClosed) count in the month: lock \$150\n");
   rt_SetInput("InpMLockOn", 1); rt_SetInput("InpMLockAmt", 150); rt_SetInput("InpRec", 0); rec_mtick(NOV + 86400LL * 40);
   for(int k = 0; k < 2; k++) { double rr = rec_next(0.6); rec_take(); rec_part(80); rec_close(); int stp = rec_mcheck();
      std::printf("   trade closed +80.00 (risk %.2f) -> %s\n", rr, stp ? "STOP for the month" : "keep trading"); }
   return 0;
}
