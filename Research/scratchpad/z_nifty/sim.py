import sys, copy
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import engine
from engine import prepare, run
P=prepare('NIFTY'); rows=P['rows']
def show(tr,label):
    print('==',label)
    for t in tr:
        if '2026-10-01' <= rows[t['fill']]['t'] <= '2026-10-12 23:59':
            print('  %s %s arm %s fill %s entry %.2f stop %.2f R %.2f exit %s res %s'%(label,'L' if t['dir']>0 else 'S',rows[t['arm']]['t'][5:],rows[t['fill']]['t'][5:],t['entry'],t['stop'],t['risk'],rows[t['exit']]['t'][5:] if t['exit'] is not None else None,t['res']))
show(run(P),'base')
