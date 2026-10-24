"""Pine-style standard indicators, full series per symbol. All return lists (None where undefined)."""
import math, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare as eprep, rma
_c={}
def base(sym):
    if sym in _c: return _c[sym]
    P=eprep(sym); R=P['rows']
    B=dict(O=[r['o'] for r in R],H=[r['h'] for r in R],L=[r['l'] for r in R],C=[r['c'] for r in R],V=[r['vwap'] for r in R],tr=P['tr'],ds=P['daystart'],T=[r['t'] for r in R])
    B['atr']=rma(P['tr'],14); _c[sym]=B; return B
def sma(x,n):
    o=[None]*len(x)
    for i in range(n-1,len(x)):
        w=x[i-n+1:i+1]
        if None in w: continue
        o[i]=sum(w)/n
    return o
def ema(x,n):
    a=2/(n+1); o=[None]*len(x); v=None
    for i,xi in enumerate(x):
        if xi is None: continue
        v=xi if v is None else a*xi+(1-a)*v; o[i]=v
    return o
def rmaN(x,n):
    o=[None]*len(x); v=None; buf=[]
    for i,xi in enumerate(x):
        if xi is None: continue
        if v is None:
            buf.append(xi)
            if len(buf)==n: v=sum(buf)/n; o[i]=v
        else: v=(v*(n-1)+xi)/n; o[i]=v
    return o
def stdev(x,n):
    o=[None]*len(x)
    for i in range(n-1,len(x)):
        w=x[i-n+1:i+1]
        if None in w: continue
        m=sum(w)/n; o[i]=math.sqrt(sum((a-m)**2 for a in w)/n)
    return o
def rsi(C,n):
    up=[None]+[max(C[i]-C[i-1],0) for i in range(1,len(C))]; dn=[None]+[max(C[i-1]-C[i],0) for i in range(1,len(C))]
    u=rmaN(up,n); d=rmaN(dn,n); o=[None]*len(C)
    for i in range(len(C)):
        if u[i] is None: continue
        o[i]=100 if d[i]==0 else (0 if u[i]==0 else 100-100/(1+u[i]/d[i]))
    return o
def dmi(B,n):
    H,L=B['H'],B['L']; N=len(H)
    pdm=[None]+[ (H[i]-H[i-1]) if (H[i]-H[i-1])>(L[i-1]-L[i]) and (H[i]-H[i-1])>0 else 0 for i in range(1,N)]
    mdm=[None]+[ (L[i-1]-L[i]) if (L[i-1]-L[i])>(H[i]-H[i-1]) and (L[i-1]-L[i])>0 else 0 for i in range(1,N)]
    tr=[None]+list(B['tr'][1:])
    t=rmaN(tr,n); p=rmaN(pdm,n); m=rmaN(mdm,n)
    dip=[None]*N; dim=[None]*N; dx=[None]*N
    for i in range(N):
        if t[i]: dip[i]=100*p[i]/t[i]; dim[i]=100*m[i]/t[i]; s=dip[i]+dim[i]; dx[i]=100*abs(dip[i]-dim[i])/(s if s else 1)
    adx=rmaN(dx,n); return dip,dim,adx
def linreg_stats(C,n,i):
    if i<n-1: return None
    y=C[i-n+1:i+1]; x=list(range(n)); mx=(n-1)/2; my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); sxx=sum((a-mx)**2 for a in x); syy=sum((b-my)**2 for b in y)
    slope=sxy/sxx; r=sxy/math.sqrt(sxx*syy) if syy>0 else 0
    return slope,r
def supertrend(B,f,n):
    H,L,C=B['H'],B['L'],B['C']; at=rmaN([None]+list(B['tr'][1:]),n) if False else rma(B['tr'],n)
    N=len(C); d=[None]*N; up=dn=None; dirv=1; prevST=None
    for i in range(N):
        if at[i] is None: continue
        src=(H[i]+L[i])/2; u=src+f*at[i]; l=src-f*at[i]
        if dn is not None: l = l if (l>dn or C[i-1]<dn) else dn
        if up is not None: u = u if (u<up or C[i-1]>up) else up
        if prevST is None: dirv=1
        elif prevST==up: dirv = -1 if C[i]>u else 1
        else: dirv = 1 if C[i]<l else -1
        st = l if dirv==-1 else u
        up,dn,prevST=u,l,st
        d[i]= -dirv  # +1 = uptrend (Pine: dir<0 is up)
    return d
