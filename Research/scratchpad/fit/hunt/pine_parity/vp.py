import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, run
for sym in ['EURUSD','ETH']:
    P = prepare(sym); rows = P['rows']
    tr = run(P)
    mine = {(t['fill'], t['dir']): t for t in tr}
    csv = {(r['i'], 1 if r['lf'] else -1) for r in rows if r['lf'] or r['sf']}
    d = sorted([x for x in set(mine) ^ csv if x[0] >= 1500])
    for x in d:
        t = mine.get(x)
        print(sym, rows[x[0]]['t'], x, 'only_port' if x in mine else 'only_csv', (rows[t['arm']]['t'], t['entry'], t['stop']) if t else '')
