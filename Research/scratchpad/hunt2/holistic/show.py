import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0,'.')
from engine2 import prepare
from engine import rma
import m as M
sym=sys.argv[1]; days=sys.argv[2].split(','); inp=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
P=prepare(sym); T=P['T']; A=rma(P['tr'],14)
for t in M.run(sym,inp):
    if T[t['fill']][:10] in days:
        print(T[t['arm']], 'fill', T[t['fill']], 'L' if t['dir']>0 else 'S', f"e {t['entry']:.1f} s {t['stop']:.1f} ({abs(t['entry']-t['stop'])/A[t['arm']]:.2f}A)", 'exit', T[t['exit']] if t['exit'] is not None else None, t['res'], 'tight' if t['tight'] else '')
