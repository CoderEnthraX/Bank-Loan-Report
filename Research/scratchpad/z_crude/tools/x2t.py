# x2t.py anchor_x 'anchor time' s x1 x2 ...  -> bar time at each x (and fractional offset)
import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('CRUDE'); idx={r['t']:r['i'] for r in rows}
ax=float(sys.argv[1]); ai=idx[sys.argv[2]]; s=float(sys.argv[3])
for v in sys.argv[4:]:
    if ':' in v:
        print(v, 'x=%.1f'%(ax+(idx[v.replace('_',' ')]-ai)*s)); continue
    f=(float(v)-ax)/s; k=ai+round(f); r=rows[k]
    print(v, r['t'], 'frac %.2f'%(f-round(f)), 'O%g H%g L%g C%g'%(r['o'],r['h'],r['l'],r['c']))
