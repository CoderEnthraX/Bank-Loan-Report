// EXPECT: warning not initialized
void OnTick() { int x; double r = x * 2.0; Print(r); }
