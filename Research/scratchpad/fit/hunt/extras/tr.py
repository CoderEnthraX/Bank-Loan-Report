import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/extras')
import json, pf
from lib import TR
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
inp = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
from engine import prepare
P = prepare(sym); T = [r['t'] for r in P['rows']]
trs = pf.run(sym, inp)
for x in pf.LOG:
    if a <= x[1] <= b: print(' ', *x)
print('MINE')
for m in trs:
    if a <= T[m['fill']] <= b: print('  ', 'L' if m['dir']>0 else 'S', 'arm', T[m['arm']], 'fill', T[m['fill']], 'exit', T[m['exit']] if m['exit'] is not None else None, m['res'], 'e %.6g s %.6g' % (m['entry'], m['stop']), 'tight' if m['tight'] else '')
print('GT')
for g in sorted([t for t in TR if t['sym']==sym], key=lambda t: t['fill']):
    if a <= g['fill'] <= b: print('  ', 'L' if g['d']>0 else 'S', 'fill', g['fill'], 'exit', g['exit'], g['out'], 'e', g['entry'], 's', g['stop'])
