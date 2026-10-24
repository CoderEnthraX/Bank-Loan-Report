import sys, pickle, random, math
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
res=pickle.load(open('grid.pkl','rb')); base=res['{}']
PP={s:lib.prepare(s) for s in lib.SYMS}
def sim(x,beR,rb=None):
    P=PP[x['sym']]; H,L=P['H'],P['L']; d=x['dir']; e=x['entry']; R=x['R']; stp=e-d*R; t=e+d*2*R; be=False; n=len(H)
    # fill bar: stop only (as engine)
    k=x['fill']
    if (L[k]<=stp if d>0 else H[k]>=stp): return -1.0
    k+=1
    while k<n:
        lo,hi=(L[k],H[k]) if d>0 else (-H[k],-L[k])
        # d>0: adverse=L ; d<0: adverse=H -> use signed
        adv = (L[k]<=stp) if d>0 else (H[k]>=stp)
        tp = (H[k]>=t) if d>0 else (L[k]<=t)
        if adv: return (0.0 if be else -1.0)
        if tp: return 2.0
        fav=d*((H[k] if d>0 else L[k])-e)/R
        if not be and fav>=beR: be=True; stp=e
        k+=1
    return None
for beR in [1.0]:
    diffs={'ALL':[], 'TRAIN':[], 'TEST':[]}; mism=0
    for x in base:
        r=sim(x,beR)
        if r is None: continue
        d=r-x['res']; diffs['ALL'].append(d); diffs['TRAIN' if x['t']<lib.SPLIT else 'TEST'].append(d)
    for k,v in diffs.items():
        m=sum(v)/len(v); sd=(sum((a-m)**2 for a in v)/(len(v)-1))**.5; se=sd/len(v)**.5
        rnd=random.Random(3); bs=sorted(sum(v[rnd.randrange(len(v))] for _ in v)/len(v) for _ in range(2000))
        print('static paired BE%.2f %s n=%d mean diff %+.4f SE %.4f boot95 [%+.3f,%+.3f] changed %d'%(beR,k,len(v),m,se,bs[50],bs[1950],sum(1 for a in v if a!=0)))
    # decomposition
    import collections
    c=collections.Counter((x['res'],sim(x,beR)) for x in base if sim(x,beR) is not None)
    print(c)
# static for beR grid on TEST and TRAIN
for beR in [0.5,0.8,1.0,1.25,1.5,1.75]:
    tr=[];te=[]
    for x in base:
        r=sim(x,beR)
        if r is None: continue
        (tr if x['t']<lib.SPLIT else te).append(r-x['res'])
    print('static beR %.2f TRAIN diff %+.4f TEST diff %+.4f'%(beR,sum(tr)/len(tr),sum(te)/len(te)))
