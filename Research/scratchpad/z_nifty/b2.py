import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
a,b=sys.argv[1],sys.argv[2]
for r in load('NIFTY'):
    if a<=r['t']<=b:
        mark=('MY-LONG-FILL' if r['lf'] else '')+('MY-SHORT-FILL' if r['sf'] else '')
        print(f"{r['i']} {r['t']} O {r['o']:.2f} H {r['h']:.2f} L {r['l']:.2f} C {r['c']:.2f} mid {(r['o']+r['c'])/2:.3f} vwap {r['vwap']:.2f} {mark}")
