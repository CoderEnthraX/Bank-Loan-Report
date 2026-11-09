"""EA v4.3 review fix: nothing is saved before the engine processed a bar (OnDeinit after a failed OnInit would store an empty last-bar time),
and the day replay needs a saved last-bar time. Must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
REPS = [
    ('void StateSave(bool force)\n{\n   if(!gPersist) return;\n',
     'void StateSave(bool force)\n{\n   if(!gPersist || gLastDone <= 0) return;                // not before the engine processed a bar (e.g. OnDeinit after a failed start)\n'),
    ('      if(gRestored && iTime(_Symbol, _Period, s) > gSvLast)   // the bars since the saved state count like bars missed in a disconnect',
     '      if(gRestored && gSvLast > 0 && iTime(_Symbol, _Period, s) > gSvLast)   // the bars since the saved state count like bars missed in a disconnect'),
]
for old, new in REPS:
    n = s.count(old); assert n == 1, (n, old[:100]); s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s); print(len(REPS), 'replacements; lines', s.count('\n'))
