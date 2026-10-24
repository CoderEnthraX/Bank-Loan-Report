import json, itertools
D=json.load(open('feat.json'))
pos=[o for o in D if o['lab'] in('takenA','takenB','must')]; neg=[o for o in D if o['lab'].startswith('extra')]
keys=[k for k in D[0]['f'] if all(o['f'][k] is not None for o in D)]
import numpy as np
PV=np.array([[o['f'][k] for k in keys] for o in pos]); NV=np.array([[o['f'][k] for k in keys] for o in neg])
best=[]
# quadrant: reject if s1*f1 >= s1*t1 and s2*f2 >= s2*t2 ; thresholds at extra values
for a in range(len(keys)):
  for b in range(a+1,len(keys)):
    for s1 in (1,-1):
      for s2 in (1,-1):
        for t1 in set(NV[:,a]):
          ma=s1*PV[:,a]>=s1*t1; na=s1*NV[:,a]>=s1*t1
          if na.sum()<2: continue
          # need t2 such that no pos in ma passes: s2*f2 > max over pos(ma) of s2*f2
          lim=(s2*PV[ma,b]).max() if ma.any() else -1e18
          nr=na & (s2*NV[:,b]>lim)
          if nr.sum()>=3: best.append((int(nr.sum()),keys[a],s1,t1,keys[b],s2,lim,[neg[q]['sym'][:2]+neg[q]['t'][5:] for q in np.where(nr)[0]]))
best.sort(key=lambda r:-r[0]); print(len(best))
for r in best[:40]: print(r)
