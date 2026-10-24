import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/residual')
import rc
from engine import prepare
base = {"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
var = dict(base); var.update(json.loads(sys.argv[1]))
tot=[0,0,0,0.0,0.0]
for sym in sys.argv[2].split(','):
    T = [r['t'] for r in prepare(sym)['rows']]
    a = {(T[t['fill']], t['dir']): t['res'] for t in rc.run(sym, base)}
    b = {(T[t['fill']], t['dir']): t['res'] for t in rc.run(sym, var)}
    rem = sorted(set(a)-set(b)); add = sorted(set(b)-set(a))
    print(sym, 'n', len(a), '->', len(b), 'removed', len(rem), 'added', len(add), 'R', round(sum(v or 0 for v in a.values()),1), '->', round(sum(v or 0 for v in b.values()),1))
    if len(sys.argv) > 3: print('   -', rem[:12]); print('   +', add[:12])
