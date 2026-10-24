import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
P = prepare('CRUDE'); rows = P['rows']
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
dip,dim,adx=dmi(rows,14,14)
idx={r['t']:r['i'] for r in rows}
for t in sys.argv[1:]:
    i=idx[t]; print(t, 'ADX %.1f +DI %.1f -DI %.1f' % (adx[i], dip[i], dim[i]))
