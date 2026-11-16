import json, math
from collections import defaultdict
D=json.load(open('../trades.json'))
months=[f"{y}-{m:02d}" for y in range(2021,2027) for m in range(1,13)][:70]

def by_month(trs):
    d=defaultdict(list)
    for t in trs: d[t['entry'][:7]].append(t)
    return d

def account(trs, exitR, start, rule, b, cap, lock):
    eq=start; rec=0.0; oscU=1; oscP=0.0; net=0.0
    for t in trs:
        if lock is not None and net>=lock: break
        if eq<=0: break
        if rule=='none': r=b
        elif rule=='exact': r=b+rec/exitR
        else:
            need=max(1,math.ceil((b-oscP)/(b*exitR)))
            r=b*min(oscU,need)
        if cap>0 and r>cap: r=cap
        if eq>0: r=min(r,eq*t['levk'])
        pnl=r*(t['R']-t['c'])/(1+t['c'])
        eq+=pnl; net+=pnl; win=pnl>0
        if rule=='exact':
            rec=max(0,rec-pnl) if win else rec+(-pnl)
        elif rule=='osc':
            oscP+=pnl
            if oscP>=b: oscU=1; oscP=0.0
            elif win: oscU+=1
    return net

def series(src, name, **kw):
    s=D[src][name]; bm=by_month(s['trades'])
    return [account(bm.get(m,[]), s['exitR'], **kw) for m in months]

def add(*ls): return [sum(x) for x in zip(*ls)]
ARS='M15-S3 fcOff'
res={}
res['ars_safe']=series('ars',ARS,start=1000,rule='osc',b=10,cap=0,lock=20)
res['ars_norec']=series('ars',ARS,start=1000,rule='none',b=20,cap=0,lock=20)
res['grid_bal']=add(*[series('grid',g,start=1000/3,rule='exact',b=10,cap=100,lock=None) for g in ['S7','S8','S10']])
res['grid_safe']=add(*[series('grid',g,start=1000/6,rule='exact',b=5,cap=50,lock=None) for g in ['S1','S2','S6','S7','S8','S10']])
res['combo safe + balanced']=add(series('ars',ARS,start=500,rule='osc',b=5,cap=0,lock=10),
  *[series('grid',g,start=500/3,rule='exact',b=5,cap=50,lock=None) for g in ['S7','S8','S10']])
json.dump(res,open('mine.json','w'))
print('computed')
