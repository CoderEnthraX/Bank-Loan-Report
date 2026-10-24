// EXPECT: warning possible loss of data
void OnTick() { long someLong = 5; int k = someLong; Print(k); }
