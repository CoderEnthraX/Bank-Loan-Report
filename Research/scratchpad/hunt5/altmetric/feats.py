import json, math, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/altmetric')
from ind import *
D=json.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/pooled/featV.json'))
NEG={('CRUDE','2026-10-06 20:55'),('CRUDE','2026-10-12 13:40'),('CRUDE','2026-10-15 18:30'),('CRUDE','2026-10-16 11:40'),('ETH','2026-10-11 00:05')}
SIG=[dict(sym=o['sym'],i=o['i'],d=o['d'],t=o['t'],pos=o['lab'] in('takenA','takenB')) for o in D if o['lab'] in('takenA','takenB') or (o['sym'],o['t']) in NEG]
_s={}
def series(sym):
    if sym in _s: return _s[sym]
    B=base(sym); C,H,L,O=B['C'],B['H'],B['L'],B['O']; S={}
    for n in (7,10,14): S['rsi%d'%n]=rsi(C,n)
    for n in (10,14):
        p,m,a=dmi(B,n); S['dip%d'%n]=p; S['dim%d'%n]=m; S['adx%d'%n]=a
    for n in (9,20,21,50,200): S['ema%d'%n]=ema(C,n)
    for n,f in ((10,3),(10,2),(7,3),(14,2),(10,1.5)): S['st%d_%s'%(n,f)]=supertrend(B,f,n)
    mom=[None]*10+[C[i]-C[i-10] for i in range(10,len(C))]; S['mom10']=mom
    S['momsma20']=sma(mom,20); S['momsd20']=stdev(mom,20)
    hlc3=[(h+l+c)/3 for h,l,c in zip(H,L,C)]; S['hlc3']=hlc3
    for n in (10,14,20): S['hsma%d'%n]=sma(hlc3,n)
    dC=[0]+[C[i]-C[i-1] for i in range(1,len(C))]; S['dCsd20']=stdev(dC,20)
    _s[sym]=(B,S); return _s[sym]
def F(sig):
    B,S=series(sig['sym']); i=sig['i']; d=sig['d']; C,H,L,O,V=B['C'],B['H'],B['L'],B['O'],B['V']; A=B['atr'][i]; f={}
    def er(src,n,path='abs'):
        x=src; p=sum(abs(x[j]-x[j-1]) for j in range(i-n+1,i+1)); return d*(x[i]-x[i-n])/p if p else 0
    hl2=[(h+l)/2 for h,l in zip(H,L)]; o4=[(a+b+c+e)/4 for a,b,c,e in zip(O,H,L,C)]
    for n in (5,8,9,10,11,12,14,20):
        f['erC%d'%n]=er(C,n)
    for n in (10,14): f['erHL2_%d'%n]=er(hl2,n); f['erO4_%d'%n]=er(o4,n)
    for n in (10,14):
        ssum=sum(B['tr'][j] for j in range(i-n+1,i+1)); rngn=max(H[i-n+1:i+1])-min(L[i-n+1:i+1])
        f['chop%d'%n]=-100*math.log10(ssum/rngn)/math.log10(n)   # negated: higher=trendier
        f['diDiff%d'%n]=d*(S['dip%d'%n][i]-S['dim%d'%n][i]); f['adx%d'%n]=S['adx%d'%n][i]; f['diSame%d'%n]=(S['dip%d'%n][i] if d>0 else S['dim%d'%n][i])
        f['adxXdi%d'%n]=f['adx%d'%n]*(1 if f['diDiff%d'%n]>0 else -1)
    for n in (7,10,14): f['rsi%d'%n]=d*(S['rsi%d'%n][i]-50)
    for n in (5,10,14,20):
        sl,r=linreg_stats(C,n,i); f['lrSlope%d'%n]=d*sl/A; f['corr%d'%n]=d*r; f['r2s%d'%n]=r*r*(1 if d*r>0 else -1)
    for n in (5,10,14):
        sb=sum(C[j]-O[j] for j in range(i-n+1,i+1)); ab=sum(abs(C[j]-O[j]) for j in range(i-n+1,i+1)); f['bodyEff%d'%n]=d*sb/ab if ab else 0
        f['upCnt%d'%n]=sum(1 for j in range(i-n+1,i+1) if d*(C[j]-C[j-1])>0)
        f['upBody%d'%n]=sum(1 for j in range(i-n+1,i+1) if d*(C[j]-O[j])>0)
    for n in (10,14,25):
        w=n+1; hs=H[i-n:i+1]; ls=L[i-n:i+1]
        hi_age=n-max(k for k in range(w) if hs[k]==max(hs)); lo_age=n-max(k for k in range(w) if ls[k]==min(ls))
        au=100*(n-hi_age)/n; ad=100*(n-lo_age)/n; f['aroonOsc%d'%n]=d*(au-ad); f['aroonSame%d'%n]=au if d>0 else ad; f['aroonOpp%d'%n]=-(ad if d>0 else au)
    for n in (10,14,20):
        hs=S['hlc3']; m=S['hsma%d'%n][i]; md=sum(abs(hs[j]-m) for j in range(i-n+1,i+1))/n; f['cci%d'%n]=d*(hs[i]-m)/(0.015*md) if md else 0
        hh=max(H[i-n+1:i+1]); ll=min(L[i-n+1:i+1]); k=100*(C[i]-ll)/(hh-ll) if hh>ll else 50; f['stoch%d'%n]=d*(k-50)
        f['donch%d'%n]=d*(k-50)
        hhp=max(H[i-n:i]); llp=min(L[i-n:i]); f['donchPrev%d'%n]=d*(100*(C[i]-llp)/(hhp-llp)-50) if hhp>llp else 0
    # EMA alignment
    e=lambda n:S['ema%d'%n][i]
    f['emaAlign9_21_50']=sum(1 for a,b in ((C[i],e(9)),(e(9),e(21)),(e(21),e(50))) if d*(a-b)>0)
    f['ema9_21']=d*(e(9)-e(21))/A; f['ema20_50']=d*(e(20)-e(50))/A; f['c_ema20']=d*(C[i]-e(20))/A; f['c_ema50']=d*(C[i]-e(50))/A
    f['ema20slope']=d*(e(20)-S['ema20'][i-3])/A
    for k in S:
        if k.startswith('st'): f['super'+k[2:]]=d*S[k][i]; f['superPrev'+k[2:]]=d*S[k][i-1]
    m=S['mom10'][i]; f['momZ']=d*(m-S['momsma20'][i])/S['momsd20'][i] if S['momsd20'][i] else 0
    f['momZvol']=d*m/(S['dCsd20'][i]*math.sqrt(10)) if S['dCsd20'][i] else 0
    f['momAtr10']=d*m/A
    # volume-free proxies
    f['vwapDist']=d*(C[i]-V[i])/A; f['vwapSlope3']=d*(V[i]-V[i-3])/A if V[i-3] is not None else 0
    f['rngExp']=sum(H[j]-L[j] for j in range(i-4,i+1))/sum(H[j]-L[j] for j in range(i-14,i-4))*2
    f['trAtr']=B['tr'][i]/A
    for n in (9,10,11,14):  # Pine ta.cmo(close,n) (Chande), and Cutler (SMA) RSI = 50+cmo/2
        m1=sum(max(C[j]-C[j-1],0) for j in range(i-n+1,i+1)); m2=sum(max(C[j-1]-C[j],0) for j in range(i-n+1,i+1))
        f['cmo%d'%n]=d*100*(m1-m2)/(m1+m2) if m1+m2 else 0; f['rsiSma%d'%n]=50+f['cmo%d'%n]/2
    return f
if __name__=='__main__':
    out=[]
    for s in SIG:
        out.append(dict(s,f=F(s)))
    json.dump(out,open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/altmetric/F.json','w'))
    print(len(out),sum(o['pos'] for o in out))
