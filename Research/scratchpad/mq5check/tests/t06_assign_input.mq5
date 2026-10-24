// EXPECT: error constant cannot be modified
input int InpLen = 5;
int OnInit() { InpLen = 7; return INIT_SUCCEEDED; }
