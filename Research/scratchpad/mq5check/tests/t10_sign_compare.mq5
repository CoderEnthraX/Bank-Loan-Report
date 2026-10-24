// EXPECT: warning signed/unsigned mismatch
void OnTick() { int a = -1; uint b = 3; if(a < b) Print("x"); }
