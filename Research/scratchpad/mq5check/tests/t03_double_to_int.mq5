// EXPECT: warning possible loss of data
void OnTick() { double y = 2.5; int x = 1.5 * y; Print(x); }
