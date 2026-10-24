import pickle, random, collections
res=pickle.load(open('stab.pkl','rb'))
b=res[0]; 
def get(o):
    for r in res:
        if r['opts']==o: return r
sk=get({"skipLossDir":1000}); pd=get({"loc":[["pdRoom","ge",-3.4]]})
SPLIT='2026-10-01'
def day(t): return t[:10]
def bydays(r,part):
    d=collections.defaultdict(list)
    for s,f,t,res_,h1,h15 in r['tr']:
        if (t>=SPLIT)==(part=='TEST'): d[day(t)].append(res_)
    return d
for name,r in (('skipLossDir',sk),('pdRoom',pd)):
  for part in ('TRAIN','TEST'):
    A=bydays(b,part); B=bydays(r,part); days=sorted(set(A)|set(B)); rnd=random.Random(5); ds=[]
    for _ in range(4000):
        smp=[days[rnd.randrange(len(days))] for _ in days]
        sa=[x for d in smp for x in A.get(d,[])]; sb=[x for d in smp for x in B.get(d,[])]
        if sa and sb: ds.append(sum(sb)/len(sb)-sum(sa)/len(sa))
    ds.sort(); pt=sum(sum(v) for v in B.values())/sum(len(v) for v in B.values())-sum(sum(v) for v in A.values())/sum(len(v) for v in A.values())
    print(name,part,'days',len(days),'point %+.3f'%pt,'day-cluster 95%% CI [%+.3f, %+.3f]'%(ds[int(.025*len(ds))],ds[int(.975*len(ds))]),'P(diff<=0)=%.3f'%(sum(1 for x in ds if x<=0)/len(ds)))
# weekly breakdown of TEST+TRAIN total R diff
import datetime
def wk(t): d=datetime.date.fromisoformat(t[:10]); return d.isocalendar()[1]
for name,r in (('skipLossDir',sk),('pdRoom',pd)):
    w=collections.defaultdict(lambda:[0,0,0,0])
    for x,sgn in ((b,0),(r,1)):
        for s,f,t,res_,h1,h15 in x['tr']:
            w[wk(t)][sgn*2]+=res_; w[wk(t)][sgn*2+1]+=1
    print(name,'week: base totR(n) -> filt totR(n)')
    for k in sorted(w): v=w[k]; print('  wk',k,'%+.0f(%d) -> %+.0f(%d)  d%+.0f'%(v[0],v[1],v[2],v[3],v[2]-v[0]))
