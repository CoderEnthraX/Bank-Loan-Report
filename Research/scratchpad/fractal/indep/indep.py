import numpy as np, numba as nb, sys, re
D="/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal"
STRATS={1:("D1",3,25,-0.14,3.00,0.75,0.45,0.80),2:("D1",3,15,-0.085,0.50,2.00,0.25,0.80),
3:("D1",2,7,-0.065,0.30,1.65,0.20,0.50),4:("H4",8,12,-0.025,0.44,3.10,0.33,0.90),
5:("H1",19,30,-0.045,2.00,0.35,0.10,0.70),6:("H1",25,25,-0.060,4.20,0.33,0.15,0.80),
7:("H1",23,25,-0.055,0.87,0.56,0.13,1.10),8:("H1",20,25,-0.060,0.68,0.43,0.10,0.70),
9:("H1",5,5,-0.080,2.00,0.70,0.10,1.00)}
# state s: 0 open,1 F,2 SL,3 TP,4 BE,5 SV,6 beDone,7 svDone,8 entry_bar,9 pending,10 E,11 ntr
# prm: 0 SLpct,1 TPpct,2 BEpct,3 SVpct
@nb.njit(cache=True)
def open_trade(s,prm,F,bar):
    s[0]=1; s[1]=F
    s[2]=F*(1-prm[0]/100); s[3]=F*(1+prm[1]/100)
    s[4]=F*(1+prm[2]/100); s[5]=F*(1-prm[3]/100)
    s[6]=0; s[7]=0; s[8]=bar
@nb.njit(cache=True)
def close_trade(s,out,bar,px,reason):
    n=int(s[11])
    out[n,0]=s[8]; out[n,1]=s[1]; out[n,2]=bar; out[n,3]=px; out[n,4]=reason
    s[11]=n+1; s[0]=0
@nb.njit(cache=True)
def up(s,prm,out,bar,x,y):
    while True:
        best=np.inf; kind=-1
        if s[0]==1:
            if s[3]>x and s[3]<=y:
                best=s[3]; kind=0
            if prm[2]>0 and s[6]==0 and s[7]==0 and s[4]>x and s[4]<=y:
                if s[4]<best: best=s[4]; kind=1
        if s[9]==1 and s[10]>x and s[10]<=y:
            if s[10]<best: best=s[10]; kind=2
        if kind<0: return
        if kind==0:
            close_trade(s,out,bar,s[3],3 if s[7]==1 else 0)
        elif kind==1:
            s[6]=1; s[2]=s[1]
        else:
            s[9]=0
            if s[0]==0: open_trade(s,prm,s[10],bar)
@nb.njit(cache=True)
def down(s,prm,out,bar,x,y):
    while True:
        best=-np.inf; kind=-1
        if s[0]==1:
            if s[2]<x and s[2]>=y:
                best=s[2]; kind=0
            if prm[3]>0 and s[6]==0 and s[7]==0 and s[5]<x and s[5]>=y:
                if s[5]>best: best=s[5]; kind=1
        if kind<0: return
        if kind==0:
            close_trade(s,out,bar,s[2],2 if s[6]==1 else 1)
        else:
            s[7]=1; s[3]=s[1]
@nb.njit(cache=True)
def run(O,H,L,C,cidx,swH,Right,offset,prm,maxn):
    n=len(O)
    s=np.zeros(12); out=np.zeros((maxn,5))
    for i in range(n):
        o=O[i];h=H[i];l=L[i];c=C[i]
        act=False
        if i==0 or cidx[i]!=cidx[i-1]:
            p=cidx[i]-Right-1
            if p>=0 and not np.isnan(swH[p]):
                s[9]=1; s[10]=swH[p]*(1+offset/100); act=True
        if s[0]==1:
            if o>=s[3]:
                close_trade(s,out,i,o,3 if s[7]==1 else 0)
            elif o<=s[2]:
                close_trade(s,out,i,o,2 if s[6]==1 else 1)
            else:
                if prm[2]>0 and s[6]==0 and s[7]==0 and o>=s[4]:
                    s[6]=1; s[2]=s[1]
                elif prm[3]>0 and s[6]==0 and s[7]==0 and o<=s[5]:
                    s[7]=1; s[3]=s[1]
        if s[9]==1 and (not act) and i>0 and C[i-1]<s[10] and o>=s[10]:
            s[9]=0
            if s[0]==0: open_trade(s,prm,o,i)
        if (h-o)<(o-l):
            a=h;b=l
        else:
            a=l;b=h
        for seg in range(3):
            if seg==0: x=o;y=a
            elif seg==1: x=a;y=b
            else: x=b;y=c
            if y>x: up(s,prm,out,i,x,y)
            elif y<x: down(s,prm,out,i,x,y)
    return out[:int(s[11])]

def swings(Hf,Left,Right):
    m=len(Hf); sw=np.full(m,np.nan)
    for p in range(Left,m-Right):
        ok=True
        for i in range(1,Left+1):
            if not Hf[p]>Hf[p-i]: ok=False;break
        if ok:
            for j in range(1,Right+1):
                if not Hf[p]>Hf[p+j]: ok=False;break
        if ok: sw[p]=Hf[p]
    return sw

REASON=["TP","SL","BE","SALV"]
def main():
    z=np.load(D+"/bars.npz")
    for chart in ["M1","M5"]:
        if chart=="M1": t,O,H,L,C=z["t"],z["O"],z["H"],z["L"],z["C"]
        else: t,O,H,L,C=[z["M5_"+k] for k in ["t","O","H","L","C"]]
        rows=[]
        for sid,(tf,R,Lf,off,sl,tp,be,sv) in STRATS.items():
            T=z[tf+"_t"];Hf=z[tf+"_H"]
            cidx=np.searchsorted(T,t,side="right")-1
            sw=swings(Hf,Lf,R)
            out=run(O,H,L,C,cidx,sw,R,off,np.array([sl,tp,be,sv]),len(T)+10)
            for r in out: rows.append((sid,int(r[0]),repr(float(r[1])),int(r[2]),repr(float(r[3])),REASON[int(r[4])]))
            print(chart,sid,len(out),flush=True)
        with open(f"{D}/indep/trades_{chart}.csv","w") as f:
            f.write("strategy,entry_bar,entry_price,exit_bar,exit_price,reason\n")
            for r in rows: f.write(",".join(map(str,r))+"\n")
if __name__=="__main__": main()
