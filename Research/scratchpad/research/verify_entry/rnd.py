import sys, pickle, random
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
res=pickle.load(open('grid.pkl','rb')); base=res['{}']; bn,be=lib.split(base)
rn=[x['res'] for x in bn]; re_=[x['res'] for x in be]; mn=sum(rn)/len(rn); me=sum(re_)/len(re_)
rnd=random.Random(11)
def q(v,p): v=sorted(v); return v[int(p*(len(v)-1))]
for keep in [1.0,0.95,0.8,0.6]:
    g=[]
    for _ in range(500):
        s=[r for r in re_ if rnd.random()<keep]; g.append(sum(s)/len(s)-me)
    print('random filter keep %.2f: TEST E2 gain sd %.3f  5%%..95%% [%+.3f,%+.3f]  frac>=+0.015: %.3f'%(keep,(sum(a*a for a in g)/len(g))**.5,q(g,.05),q(g,.95),sum(a>=0.015 for a in g)/len(g)))
# best-of-145 selected on TRAIN, test gain
for keep in [0.95,0.8]:
    gains=[];trg=[]
    for _ in range(300):
        best=None
        for v in range(145):
            m=[rnd.random()<keep for _ in rn]; s=[r for r,k in zip(rn,m) if k]; sc=sum(s)/len(s)-mn
            if best is None or sc>best[0]: best=(sc,)
            # test gain of this same variant with fresh mask (variant = rule applied to new data: independent noise)
        # test gain for the selected rule: independent random mask on TEST (random filter has no skill)
        s=[r for r in re_ if rnd.random()<keep]; gains.append(sum(s)/len(s)-me); trg.append(best[0])
    print('best-of-145 random filters keep %.2f: best TRAIN gain mean %.3f (analyst best TRAIN gain +0.037/+0.044); TEST gain of selected: sd %.3f, 95th pct %+.3f'%(keep,sum(trg)/len(trg),(sum(a*a for a in gains)/len(gains))**.5,q(gains,.95)))
# null for ALL-data trade-level: distribution of mean E2
import math
sd=(sum((r-me)**2 for r in re_)/(len(re_)-1))**.5; print('TEST per-trade sd %.3f SE of mean %.3f; ratio of BE+rb3 gain 0.015 to unpaired SE %.2f'%(sd,sd/len(re_)**.5,0.015/(sd/len(re_)**.5)))
