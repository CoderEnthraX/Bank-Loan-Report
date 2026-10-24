import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from gtscore import load_gt
from engine2 import prepare
import os
tr,win=load_gt('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/final')
for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P=prepare(s); print(s,P['T'][0],P['T'][-1],len(P['T']))
    for w in sorted([w for w in win if w['sym']==s],key=lambda w:w['a']): print('   win',w['a'],w['b'],w['img'])
