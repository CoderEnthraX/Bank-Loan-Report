"""is the 1h |EMA20 slope| cap just a price-momentum / volatility-regime proxy?"""
import sys, pickle, statistics as st
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev, feats
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab)
for x in tab:
    F=feats.compute(x['sym']); C=F['C']; A=F['A']; i=x['arm']
    for k in (12,24,36,48,72):
        x['f']['mv%d'%k]=abs(C[i]-C[i-k])/A[i] if i>=k else None
        x['f']['smv%d'%k]=x['dir']*(C[i]-C[i-k])/A[i] if i>=k else None
    # 3h ATR regime: mean TR over last 36 bars / ATR14
    P=feats.prepare(x['sym']); tr=P['tr']; x['f']['atrR']=(sum(tr[i-35:i+1])/36)/A[i]
def cap(nm,q):
    vals=sorted(x['f'][nm] for x in tn if x['f'][nm] is not None); th=vals[int(q*len(vals))]
    a=[x for x in tn if x['f'][nm] is None or x['f'][nm]<=th]; b=[x for x in te if x['f'][nm] is None or x['f'][nm]<=th]
    return th,len(a)/len(tn),ev.E(a)-ev.E(tn),len(b)/len(te),ev.E(b)-ev.E(te)
for nm in ['h60_asl_E20_3','mv12','mv24','mv36','mv48','mv72','smv36','atrR']:
    print('%-14s'%nm+' | '.join('q%.2f th %.2f TR %+.3f TE %+.3f'%(q,*[cap(nm,q)[i] for i in (0,2,4)]) for q in (0.7,0.8)))
# correlation of 1h slope with mv36
xs=[(x['f']['h60_asl_E20_3'],x['f']['mv36']) for x in tab if x['f']['h60_asl_E20_3'] is not None]
a=[u for u,_ in xs]; b=[v for _,v in xs]; ma,mb=st.mean(a),st.mean(b)
print('corr(h60_asl, mv36) %.2f'%(sum((u-ma)*(v-mb) for u,v in xs)/(sum((u-ma)**2 for u in a)*sum((v-mb)**2 for v in b))**.5))
# conditional: within mv36 kept by its own 72% cap, does the EMA cap still add?
th=cap('mv36',0.72)[0]
for part,nmT in ((tn,'TRAIN'),(te,'TEST')):
    k=[x for x in part if x['f']['mv36'] is None or x['f']['mv36']<=th]; kk=[x for x in k if x['f']['h60_asl_E20_3'] is None or x['f']['h60_asl_E20_3']<=1.652]
    print(nmT,'mv36 cap n=%d E %+.3f ; + EMA cap n=%d E %+.3f'%(len(k),ev.E(k),len(kk),ev.E(kk)))
