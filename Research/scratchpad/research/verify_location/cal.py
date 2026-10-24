import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/verify_location")
from drv import *
if __name__=='__main__':
    o=[{"randRej":[q,s]} for q in (0.35,0.5,0.6,0.7) for s in (0,1)]
    for r in pmap(o): print(r['opts'],r['ALL']['n'],'%.3f'%r['TEST']['E2'])
