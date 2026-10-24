import sys,pickle
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
res=pickle.load(open('grid.pkl','rb')); base=res['{}']; PP={s:lib.prepare(s) for s in lib.SYMS}
def sim(x,pess,cost=0.0):
    P=PP[x['sym']];H,L=P['H'],P['L'];d=x['dir'];e=x['entry'];R=x['R'];stp=e-d*R;t=e+d*2*R;be=False;k=x['fill']
    if (L[k]<=stp if d>0 else H[k]>=stp): return -1.0
    k+=1
    while k<len(H):
        adv=(L[k]<=stp) if d>0 else (H[k]>=stp); tp=(H[k]>=t) if d>0 else (L[k]<=t)
        if adv: return (-cost if be else -1.0)
        if tp: return 2.0
        fav=d*((H[k] if d>0 else L[k])-e)/R
        if not be and fav>=1.0:
            be=True; stp=e
            if pess and ((L[k]<=e) if d>0 else (H[k]>=e)): return -cost
        k+=1
for pess,cost in [(0,0),(1,0),(0,0.05),(1,0.05),(0,0.1)]:
    tr=[];te=[]
    for x in base:
        r=sim(x,pess,cost)
        if r is None: continue
        (tr if x['t']<lib.SPLIT else te).append(r-x['res'])
    print('pess_triggerbar=%d scratch_cost=%.2fR: TRAIN diff %+.4f TEST diff %+.4f ALL %+.4f'%(pess,cost,sum(tr)/len(tr),sum(te)/len(te),(sum(tr)+sum(te))/(len(tr)+len(te))))
