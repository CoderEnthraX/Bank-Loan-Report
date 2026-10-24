import json, sys, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit')
from engine2 import prepare
spec=importlib.util.spec_from_file_location('m',S+'/hunt5/stats/combo.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
CAND={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
SYMS=['CRUDE','GC','NASDAQ','NIFTY','US30','SENSEX','EURUSD','ETH']
def stat(tr):
    d=[x for x in tr if x['exit'] is not None]; W=sum(1 for x in d if x['res']>0); R=sum(x['res'] for x in d)
    return len(d),W,R
print('sym   bars | current: N win%  R   | CAND: N win%  R   | changes: common  removed(cur only)  added(cand only) | cur-only avg R, cand-only avg R')
T=[0]*3; Tc=[0]*3; tot=dict(c=0,r=0,a=0)
for s in SYMS:
    P=prepare(s); a=M.run(s,{}); b=M.run(s,CAND)
    used=set(); common=0; rem=[]
    for m in a:
        j=next((k for k,n in enumerate(b) if k not in used and n['dir']==m['dir'] and abs(n['fill']-m['fill'])<=1),None)
        if j is None: rem.append(m)
        else: used.add(j); common+=1
    add=[n for k,n in enumerate(b) if k not in used]
    na,wa,ra=stat(a); nb,wb,rb=stat(b)
    ar=lambda L:(sum(x['res'] for x in L if x['res'] is not None)/max(1,sum(1 for x in L if x['res'] is not None)))
    print(f"{s:7s}{len(P['T']):6d} | {na:4d} {100*wa/na:4.1f}% {ra:+6.0f} | {nb:4d} {100*wb/nb:4.1f}% {rb:+6.0f} | {common:4d} {len(rem):4d} {len(add):4d}  ({100*(len(rem)+len(add))/max(1,len(a)):.0f}% of cur trades differ) | {ar(rem):+.2f} {ar(add):+.2f}")
    for i,x in enumerate((na,wa,ra)): T[i]+=x
    for i,x in enumerate((nb,wb,rb)): Tc[i]+=x
    tot['c']+=common; tot['r']+=len(rem); tot['a']+=len(add)
print(f"ALL            | {T[0]:4d} {100*T[1]/T[0]:4.1f}% {T[2]:+6.0f} | {Tc[0]:4d} {100*Tc[1]/Tc[0]:4.1f}% {Tc[2]:+6.0f} | {tot}")
