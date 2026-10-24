import json
D=json.load(open('featV.json'))
pos=[o for o in D if o['lab'] in('takenA','takenB','must')]; neg=[o for o in D if o['lab'].startswith('extra')]
for o in neg: print(o['sym'],o['t'],o['lab'])
keys=list(D[0]['f'])
res=[]
for k in keys:
    pv=[o['f'][k] for o in pos if o['f'][k] is not None]; nv=[(o['f'][k],o) for o in neg if o['f'][k] is not None]
    if not pv: continue
    lo,hi=min(pv),max(pv)
    below=[o for v,o in nv if v<lo]; above=[o for v,o in nv if v>hi]
    best=max(below,above,key=len)
    side='<'+format(lo,'.3g') if best is below else '>'+format(hi,'.3g')
    res.append((len(best),k,side,[o['t'][5:]+o['sym'][:2] for o in best],[round(v,3) for v,o in nv]))
res.sort(key=lambda r:-r[0])
for r in res[:45]: print(r)
