// EXPECT: error 
void OnTick() { double a[]; ArrayResize(a, 3); a = 5; }
