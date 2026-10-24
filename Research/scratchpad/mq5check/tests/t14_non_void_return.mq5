// EXPECT: warning not all control paths return a value
int f(int a) { if(a > 0) return 1; }
void OnTick() { Print(f(1)); }
