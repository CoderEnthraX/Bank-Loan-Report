import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
import r3
from engine2 import prepare
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
r3.IMPS = []; tr = r3.run(sym, {}); P = prepare(sym); T = P['T']
fills = {x['arm']: x for x in tr}
for i, d, bn, sn, pn in r3.IMPS:
    if a <= T[i] <= b:
        x = fills.get(i)
        print(T[i], 'BULL' if d > 0 else 'bear', 'before: bull', bn, 'bear', sn, 'prevNet', pn, ('ARM->fill %s %s stop %.2f half %s' % (T[x['fill']], 'L' if x['dir']>0 else 'S', x['stop'], x['half'])) if x else '')
for x in tr:
    if a <= T[x['arm']] <= b: print('TRADE arm', T[x['arm']], 'fill', T[x['fill']], 'L' if x['dir'] > 0 else 'S', 'exit', T[x['exit']] if x['exit'] is not None else None, 'half', x['half'], 'ghost', x['ghost'])
