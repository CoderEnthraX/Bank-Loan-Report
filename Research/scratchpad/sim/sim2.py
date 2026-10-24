# Python port of the Pine state machine (same order of operations) to test invariants.
import random, math
random.seed(7)
N=40000; BARS_PER_DAY=276
o=[];h=[];l=[];c=[];v=[]
p=4200.0
for i in range(N):
    op=p; vol=abs(random.gauss(0,1.2))+0.3
    if random.random()<0.04: vol*=4
    cl=op+random.gauss(0,vol)
    hi=max(op,cl)+abs(random.gauss(0,vol*0.5)); lo=min(op,cl)-abs(random.gauss(0,vol*0.5))
    o.append(op);h.append(hi);l.append(lo);c.append(cl);v.append(random.randint(100,1000)); p=cl
P=dict(structLen=6,retest=5,dispAtr=0.8,bodyPct=60,closePct=30,stopAtr=1.8,cool=2,maxFills=5,atrLen=14,tp=[0.6,1,1.5,2])
tr=[h[0]-l[0]]+[max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])) for i in range(1,N)]
atr=[None]*N; a=None
for i in range(N):
    if i<P['atrLen']-1: continue
    a = sum(tr[:P['atrLen']])/P['atrLen'] if a is None else (a*(P['atrLen']-1)+tr[i])/P['atrLen']
    atr[i]=a
vw=[];cpv=cw=0
for i in range(N):
    if i%BARS_PER_DAY==0: cpv=cw=0
    tp=(h[i]+l[i]+c[i])/3; cpv+=tp*v[i]; cw+=v[i]; vw.append(cpv/cw)
st=0; armBar=fillBar=lastExit=None; lim=stp=t4=t1=None; tpHit=0
HZ=[12,18,24]; MODES=['profit','tp1','tp4']
hz={m:{'w':[0,0,0],'n':[0,0,0]} for m in MODES}; done={m:[True]*3 for m in MODES}
def rec(m,k,win):
    if not done[m][k]:
        done[m][k]=True; hz[m]['n'][k]+=1; hz[m]['w'][k]+=bool(win)

dayFills=0; totW=totL=0; totR=0.0; trades=[]; fillsPerDay={}
for i in range(N):
    if i%BARS_PER_DAY==0: dayFills=0
    day=i//BARS_PER_DAY
    # 1 manage live
    if abs(st)==2 and i>fillBar:
        isL=st==2
        sh = l[i]<=stp if isL else h[i]>=stp
        th = h[i]>=t4 if isL else l[i]<=t4
        if (h[i]>=t1 if isL else l[i]<=t1): tpHit=max(tpHit,1)
        el=i-fillBar; mv=(c[i]-lim) if isL else (lim-c[i])
        for m in MODES:
            for k in range(3):
                if sh or th: rec(m,k, (not sh) if m=='profit' else (tpHit>=1) if m=='tp1' else (th and not sh))
                elif el>=HZ[k]: rec(m,k, mv>0 if m=='profit' else (tpHit>=1) if m=='tp1' else False)
        if sh or th:
            win=not sh; res=P['tp'][3] if win else -1.0
            totR+=res; totW+=win; totL+=(not win); lastExit=i; st=0; trades[-1]['res']=res; trades[-1]['exit']=i
    # 2 armed
    if abs(st)==1 and i>armBar:
        isL=st==1
        touched = l[i]<=lim if isL else h[i]>=lim
        if touched and dayFills<P['maxFills']:
            st=2 if isL else -2; fillBar=i; dayFills+=1; fillsPerDay[day]=fillsPerDay.get(day,0)+1
            trades.append(dict(dir=1 if isL else -1,arm=armBar,fill=i,lim=lim,stp=stp,res=None)); tpHit=0
            for m in MODES: done[m]=[False]*3
            if (l[i]<=stp if isL else h[i]>=stp):
                totR-=1; totL+=1; lastExit=i; st=0; trades[-1]['res']=-1.0; trades[-1]['exit']=i
                for m in MODES:
                    for k in range(3): rec(m,k,False)
        elif i-armBar>=P['retest']:
            st=0
    # 3 arm
    if i<P['structLen']+1 or atr[i] is None: continue
    ph=max(h[i-P['structLen']:i]); pl=min(l[i-P['structLen']:i])
    rng=h[i]-l[i]; body=abs(c[i]-o[i]); mid=(o[i]+c[i])/2
    big = rng>0 and rng>=P['dispAtr']*atr[i] and body/rng*100>=P['bodyPct']
    bull = c[i]>o[i] and c[i]>ph and big and (h[i]-c[i])/rng*100<=P['closePct'] and c[i]>vw[i]
    bear = c[i]<o[i] and c[i]<pl and big and (c[i]-l[i])/rng*100<=P['closePct'] and c[i]<vw[i]
    cooled = lastExit is None or i-lastExit>=P['cool']
    if abs(st)!=2 and cooled and dayFills<P['maxFills'] and (bull or bear):
        isL=bull; d=1 if isL else -1
        e=max(mid,ph) if isL else min(mid,pl); s=e-d*P['stopAtr']*atr[i]; risk=d*(e-s)
        if risk>0:
            st=1 if isL else -1; armBar=i; lim=e; stp=s; t4=e+d*P['tp'][3]*risk; t1=e+d*P['tp'][0]*risk
# invariants
closed=[t for t in trades if t['res'] is not None]
assert all(t['fill']>t['arm'] and t['fill']-t['arm']<=P['retest'] for t in trades), "fill outside window"
assert max(fillsPerDay.values())<=P['maxFills'], "cap broken"
for a_,b_ in zip(trades,trades[1:]):
    assert a_.get('exit') is not None and b_['fill']>=a_['exit'], "overlapping trades"
    assert b_['arm']-a_['exit']>=P['cool'] or b_['arm']<a_['exit'], "cooldown broken"
assert abs(totR-sum(t['res'] for t in closed))<1e-9
lag=[t['fill']-t['arm'] for t in trades]
print(f"trades={len(trades)} closed={len(closed)} W={totW} L={totL} win%={100*totW/max(1,totW+totL):.1f} totR={totR:+.1f}")
print("fill delay histogram:",{k:lag.count(k) for k in sorted(set(lag))})
print("trades/day avg: %.2f, days at cap: %d of %d" % (len(trades)/(N/BARS_PER_DAY), sum(1 for x in fillsPerDay.values() if x==P['maxFills']), N//BARS_PER_DAY))
print("all invariants OK")

for m in MODES:
    print(m, ['%d%% %d/%d'%(round(100*w/n) if n else 0,w,n) for w,n in zip(hz[m]['w'],hz[m]['n'])])
    assert all(n<=len(trades) for n in hz[m]['n'])
    assert all(n>=len(closed)-1 for n in hz[m]['n']), 'a closed trade was not counted'
# TP4-within-horizon accuracy can only grow with a longer horizon
assert hz['tp4']['w'][0]<=hz['tp4']['w'][1]<=hz['tp4']['w'][2]
assert hz['tp1']['w'][0]<=hz['tp1']['w'][1]<=hz['tp1']['w'][2]
print('horizon invariants OK')
