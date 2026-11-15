import json, datetime
START=10000.0; B0=50.0
LEV={'Low':(0.8,0.10,2,0.25),'Medium':(0.7,0.15,3,0.30),'High':(0.6,0.20,5,0.35),
     'Extra high':(0.5,0.25,8,0.40),'Max':(0.4,0.30,12,0.50)}
LEVELS=['Off','Low','Medium','High','Extra high','Max']
# 31 settings in order E..AI
SETTINGS=[('E',None)]+[(r,l) for r in 'FGHIJ' for l in LEVELS]

def sim(trades, exitR, cap, rule, level, T=1000.0, J_in_recovery_only=True, ret_pnls=True):
    b=B0; eq=START; net=0.0; peak=0.0; crL=0.0; crW=False; ruined=False
    lad = LEV.get(level) if (rule!='E' and level and level!='Off') else None
    out=[]
    for t in trades:
        if ruined:
            out.append(0.0); continue
        R=t['R']; c=t['c']; sd=t['sd']; price=t['price']
        levk=100*sd*(1+c)/price; rmin=sd*(1+c)
        rec = crW and crL>0
        def plain(B):
            if rec:
                x=max(B, crL/exitR)
                if rule in 'FI': x=min(x,3*B)
                elif rule=='H': x=min(x,max(B,0.01*eq))
                elif rule=='J': x=max(B, x*max(0.0,1-(peak-net)/(20*B)))
                return x
            elif crL>0 and rule in 'EI':
                return min(B,rmin)
            return B
        r=plain(b)
        if lad and peak>=T:
            lam,phi,bmax,gam=lad
            C=max(0.0,net-lam*peak)
            B=b+min((bmax-1)*b, phi*C)
            r=min(plain(B), r+gam*C)
            if net<=0: r=min(b,rmin)
        if cap>0 and r>cap: r=cap
        if eq>0: r=min(r, eq*levk)
        pnl=r*(R-c)/(1+c)
        eq+=pnl; net+=pnl; peak=max(peak,net)
        if eq<=0: ruined=True
        crL=max(0.0,crL-pnl)
        if rule=='G':
            if lad and peak>=T:
                lam,phi,bmax,gam=lad
                B2=b+min((bmax-1)*b, phi*max(0.0,net-lam*peak))
            else: B2=b
            crL=min(crL,10*B2)
        if crL<0.01: crL=0.0
        crW = pnl>0
        out.append(pnl)
    return out

def months():
    return [(2021+(i//12), i%12+1) for i in range(70)]
def mkey(s): return (int(s[:4]),int(s[5:7]))

def block1(acc, rule, level, T=1000.0):
    p=sim(acc['trades'],acc['exitR'],acc['cap'],rule,level,T)
    d={}
    for t,x in zip(acc['trades'],p):
        d[mkey(t['exit'])]=d.get(mkey(t['exit']),0.0)+x
    return [d.get(m,0.0) for m in months()]

def block5(acc, rule, level, T=1000.0):
    by={}
    for t in acc['trades']: by.setdefault(mkey(t['entry']),[]).append(t)
    res=[]
    for m in months():
        tr=by.get(m,[])
        res.append(sum(sim(tr,acc['exitR'],acc['cap'],rule,level,T)) if tr else 0.0)
    return res
def total(acc,rule,level,T): return sum(sim(acc['trades'],acc['exitR'],acc['cap'],rule,level,T))
