import itertools, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
PARTS = dict(T={"slopeCross":True,"minOpenBars":0,"cooldownBars":1}, D={"dayStopR":0}, O={"tightOut":True},
             E={"erMin":0.2}, X={"legFrom":"exit"}, N={"netMin":2})
def one(keys):
    o={}; [o.update(PARTS[k]) for k in keys]
    a=subprocess.run(['python3','-I','score2.py',S+'/hunt4/combo.py',json.dumps(o)],cwd=S+'/xl',capture_output=True,text=True,timeout=900).stdout
    b=subprocess.run(['python3','-I','extrasB.py',S+'/hunt4/combo.py',json.dumps(o)],cwd=S+'/xl',capture_output=True,text=True,timeout=900).stdout
    A=eval(a.split('(80):')[1].split('\n')[0]); Bl=a.split('time-matched ')[1].split('\n')[0]
    bm=int(Bl.split(',')[0]); bs=int(Bl.split('stop correct ')[1].split('/')[0])
    px=b.count('PROVABLE-EXTRA')
    obj = bm + bs + 3*A['exact'] - 2*A['miss'] - 2*A['extra'] - 2*px
    return (''.join(keys) or '-', A['exact'],A['miss'],A['extra'], bm, bs, px, obj)
combos=[c for r in range(len(PARTS)+1) for c in itertools.combinations(PARTS,r)]
with ThreadPoolExecutor(6) as ex: res=list(ex.map(one,combos))
res.sort(key=lambda r:-r[-1])
print('combo  Aex Amiss Aext  Bmatch Bstop provB  obj')
for r in res: print('%-7s %3d %4d %4d   %4d %5d %5d  %4d'%r)
