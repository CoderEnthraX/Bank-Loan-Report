// EXPECT: warning hides global declaration
double gLevel = 1.0;
void OnTick() { double gLevel = 2.0; Print(gLevel); }
