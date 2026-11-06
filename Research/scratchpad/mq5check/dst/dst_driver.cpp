#include <cstdio>
extern "C" { int dst_uk(long long t); int dst_ny(long long t); }
// prints every UTC hour (and the minutes around the switch hours) 2019-2036 with the EA's London / New York summer flags
int main() { for(long long t = 1546300800LL; t < 2082758400LL; t += 900) std::printf("%lld %d %d\n", t, dst_uk(t), dst_ny(t)); return 0; }
