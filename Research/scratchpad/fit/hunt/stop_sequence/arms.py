import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from rec import *
out = runall(True)
for s in ['NIFTY','SENSEX']:
    P = prepare(s); fills = {t['arm']: t for t in out[s]}
    for (i, d, snap) in REC[s]:
        if '2026-10-04' < P['T'][i] < '2026-10-10':
            t = fills.get(i)
            print(s, P['T'][i], 'L' if d > 0 else 'S', 'st', snap['st'], '->', ('fill '+P['T'][t['fill']]+f" res {t['res']}") if t else 'unfilled')
