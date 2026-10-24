// EXPECT: warning implicit conversion from 'number' to 'string'
void OnTick() { string s = "a" + 5; Print(s); }
