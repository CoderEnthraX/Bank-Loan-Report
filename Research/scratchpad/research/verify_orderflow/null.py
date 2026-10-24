import pickle, random, math
R='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'
rows=pickle.load(open(R+'/verify_orderflow/base_tab.pkl','rb'))
SPL='2026-10-01'
n=len(rows); res=[t['res'] for t in rows]; ist=[t['t']>=SPL for t in rows]
h1=[1 if t['hit1'] else -1 for t in rows]; h15=[1.5 if t['hit15'] else -1 for t in rows]
tri=[i for i in range(n) if not ist[i]]; tei=[i for i in range(n) if ist[i]]
def m(v,idx): return sum(v[i] for i in idx)/len(idx) if idx else 0
bTR=m(res,tri); bTE=m(res,tei)
def sel(keepmask,idx): return [i for i in idx if keepmask[i]]
# observed
z=[None if t['fx'] is None else t['fx']['z'] for t in rows]; cvd=[None if t['fx'] is None else t['fx']['cvd_clv'] for t in rows]
kz=[x is None or x<=2.4 for x in z]; kc=[x is None or x>=-0.006 for x in cvd]
for nm,k in (('z',kz),('cvd',kc),('both',[a and b for a,b in zip(kz,kc)])):
    print(nm,'keep',sum(k)/n,'dTR',m(res,sel(k,tri))-bTR,'dTE',m(res,sel(k,tei))-bTE)
# A: random veto
rnd=random.Random(7); N=3000
for keepfrac,obsTE,obsTR,nm in ((sum(kz)/n,m(res,sel(kz,tei))-bTE,m(res,sel(kz,tri))-bTR,'z'),(sum(kc)/n,m(res,sel(kc,tei))-bTE,m(res,sel(kc,tri))-bTR,'cvd')):
    dte=[];dtr=[];both=0
    for _ in range(N):
        k=[rnd.random()<keepfrac for _ in range(n)]
        a=m(res,sel(k,tei))-bTE; b=m(res,sel(k,tri))-bTR; dte.append(a); dtr.append(b)
        if a>=obsTE and b>=obsTR: both+=1
    dte.sort(); 
    print('A random veto keep %.2f: TEST dE2 null mean %+.3f sd %.3f p95 %+.3f p99 %+.3f | P(null TEST>=obs %.3f)=%.4f | P(TRAIN>=obs %.3f)=%.4f | P(both)=%.4f'%(keepfrac,sum(dte)/N,(sum((x-sum(dte)/N)**2 for x in dte)/N)**.5,dte[int(.95*N)],dte[int(.99*N)],obsTE,sum(1 for x in dte if x>=obsTE)/N,obsTR,sum(1 for x in dtr if x>=obsTR)/N,both/N))
# B: selection-adjusted: random features, TRAIN picks threshold (grid of keep fractions .70..95), report TEST dE2
fracs=[.70,.75,.80,.85,.90,.95]
def pick(f):
    # f: random vector; thresholds by quantile of feature over ALL trades: veto the top (1-frac) fraction (like 'le' threshold)
    order=sorted(range(n),key=lambda i:f[i]); best=None
    out=[]
    for fr in fracs:
        cut=int(fr*n); k=[False]*n
        for i in order[:cut]: k[i]=True
        trE=m(res,sel(k,tri)); teE=m(res,sel(k,tei)); out.append((trE,teE-bTE,trE-bTR))
    return out
B1=[];B2=[];B3=[]; reps=1000
rnd=random.Random(11)
for r in range(reps):
    fam=[]
    for fi in range(30):
        f=[rnd.random() for _ in range(n)]; o=pick(f); fam.append(o)
    # B1: single feature, TRAIN-best threshold
    o=fam[0]; B1.append(max(o,key=lambda x:x[0])[1])
    # B2: family, best TRAIN over feature x threshold, report TEST
    allv=[x for o in fam for x in o]; B2.append(max(allv,key=lambda x:x[0])[1])
    # B3: family max over TEST (oracle)
    B3.append(max(x[1] for x in allv))
for nm,B in (('B1 single feature, TRAIN-picked thr',B1),('B2 30-feature family, TRAIN-picked',B2),('B3 30-feature family, max TEST (oracle)',B3)):
    B=sorted(B); print(nm,'mean %+.3f p95 %+.3f p99 %+.3f ; P(>=+0.082)=%.3f P(>=+0.053)=%.3f'%(sum(B)/reps,B[int(.95*reps)],B[int(.99*reps)],sum(1 for x in B if x>=0.082)/reps,sum(1 for x in B if x>=0.053)/reps))
