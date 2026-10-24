import sys; sys.path.insert(0,"/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research")
import lib, math, random
base=lib.run_all()
from engine2 import prepare
sess={}
for s in lib.SYMS:
    P=prepare(s); c=0; a=[]
    for d in P['daystart']: c+= 1 if d else 0; a.append(c)
    sess[s]=a
rows=[]
for s in lib.SYMS:
    tr=sorted([x for x in base if x['sym']==s],key=lambda x:x['fill'])
    last=None; ls=None  # (dir) of active block, session
    for x in tr:
        ss=sess[s][x['arm']]
        if ls!=ss: blk=0; ls=ss
        flag = (blk==x['dir'])           # same-direction after unresolved loss
        flagOpp = (blk==-x['dir'])
        rows.append((s,x['t'],x['res'],flag,flagOpp, blk!=0))
        # state update at exit
        blk = 0 if x['res']>0 else x['dir']
import statistics as st
def rep(name,sel):
    for per,f in (('ALL',lambda r:True),('TRAIN',lambda r:r[1]<lib.SPLIT),('TEST',lambda r:r[1]>=lib.SPLIT)):
        v=[r[2] for r in rows if sel(r) and f(r)]
        o=[r[2] for r in rows if not sel(r) and f(r)]
        if len(v)>1:
            se=math.sqrt(st.pvariance(v)/len(v)+st.pvariance(o)/len(o))
            print(f'{name:14s}{per:6s} flagged n={len(v):4d} mean {sum(v)/len(v):+.3f} | rest n={len(o):4d} mean {sum(o)/len(o):+.3f} | diff {sum(v)/len(v)-sum(o)/len(o):+.3f} se {se:.3f}')
rep('sameDirAfterLoss',lambda r:r[3]); rep('oppDirAfterLoss',lambda r:r[4]); rep('anyAfterLoss',lambda r:r[5])
# per-symbol sameDir flagged
for s in lib.SYMS:
    v=[r[2] for r in rows if r[0]==s and r[3]]; print(s,len(v),'%+.3f'%(sum(v)/len(v)) if v else '')
# by test week
