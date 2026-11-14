import re,sys
D="/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal"
def load(p):
    rows=[]
    for ln in open(p).read().split("\n")[1:]:
        if not ln: continue
        a=ln.split(",")
        f=lambda s: float(re.sub(r"np\.float64\((.*)\)",r"\1",s))
        rows.append((int(a[0]),int(a[1]),f(a[2]),int(a[3]),f(a[4]),a[5]))
    return rows
for ch in ["M1","M5"]:
    m=load(f"{D}/indep/trades_{ch}.csv"); r=load(f"{D}/ref_trades_{ch}.csv")
    print(ch,"mine",len(m),"ref",len(r))
    ms={}; rs={}
    for x in m: ms.setdefault((x[0],x[1]),[]).append(x)
    for x in r: rs.setdefault((x[0],x[1]),[]).append(x)
    ok=lambda a,b: a[3]==b[3] and a[5]==b[5] and abs(a[2]-b[2])<=1e-9*abs(b[2]) and abs(a[4]-b[4])<=1e-9*abs(b[4])
    mism=0;ex=[]
    for k in sorted(set(ms)|set(rs)):
        a=ms.get(k);b=rs.get(k)
        if a and b and ok(a[0],b[0]): continue
        mism+=1; ex.append((k,a,b))
    print(" mismatches",mism)
    for e in ex[:8]: print("  ",e)
