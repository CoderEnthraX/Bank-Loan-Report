import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import prepare, rma
from arp_data import find
# (symbol, last bar shown when the table was read, ADX shown)
OBS = [('GC','2026-10-09 21:05',13),('GC','2026-10-10 01:05',15),('GC','2026-10-12 06:40',30),('GC','2026-10-09 14:00',20),
       ('EURUSD','2026-10-09 12:50',21),('EURUSD','2026-10-09 13:40',15),('EURUSD','2026-10-12 06:40',41)]
def dmi(rows, L, S):
    n=len(rows); up=[0.0]*n; dn=[0.0]*n; tr=[rows[0]['h']-rows[0]['l']]+[0.0]*(n-1)
    for i in range(1,n):
        u=rows[i]['h']-rows[i-1]['h']; d=rows[i-1]['l']-rows[i]['l']
        up[i]=u if (u>d and u>0) else 0.0; dn[i]=d if (d>u and d>0) else 0.0
        tr[i]=max(rows[i]['h']-rows[i]['l'],abs(rows[i]['h']-rows[i-1]['c']),abs(rows[i]['l']-rows[i-1]['c']))
    trr=rma(tr,L); pu=rma(up,L); pd=rma(dn,L)
    dx=[]; dip=[]; dim=[]
    for i in range(n):
        if trr[i] is None or trr[i]==0: dx.append(0.0); dip.append(None); dim.append(None); continue
        p=100*pu[i]/trr[i]; m=100*pd[i]/trr[i]; dip.append(p); dim.append(m)
        dx.append(abs(p-m)/(p+m if p+m else 1)*100)
    first=next(i for i in range(n) if trr[i] is not None)
    adx=[None]*n; ax=rma(dx[first:],S)
    for k,v in enumerate(ax): adx[first+k]=v
    return dip,dim,adx
if __name__ == '__main__':
  cache={}
  res=[]
  for L in range(5,31):
      for S in sorted({L,7,10,14,20}):
          err=0; vals=[]
          for sym,t,v in OBS:
              P=cache.setdefault(sym,prepare(sym)); i=find(P['rows'],t)
              key=(sym,L,S)
              if key not in cache: cache[key]=dmi(P['rows'],L,S)
              a=cache[key][2][i]; vals.append(round(a)); err+=abs(round(a)-v)
          res.append((err,L,S,vals))
  res.sort()
  print('target', [v for *_,v in OBS])
  for r in res[:8]: print(r)
