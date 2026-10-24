import subprocess,sys
img,day0,day1=sys.argv[1],sys.argv[2],sys.argv[3]
yref,pref,sc=map(float,sys.argv[4:7]); x0,y0,x1,y1=sys.argv[7:11]
c=subprocess.run(['python3','-I','fit/candles.py',img,x0,y0,x1,y1],capture_output=True,text=True).stdout.splitlines()[1:]
C=[(float(l.split()[0]),int(l.split()[1]),int(l.split()[2])) for l in c]
b=subprocess.run(['python3','-I','fit/bars.py','GC',day0,day1],capture_output=True,text=True).stdout.splitlines()
B=[(int(l.split()[0]),l.split()[2],float(l.split()[6]),float(l.split()[8])) for l in b]
f=lambda p:yref+(pref-p)*sc
res=[]
for sp in [float(s) for s in sys.argv[11].split(',')]:
  for k,(idx,t,h,l) in enumerate(B):
    # anchor bar idx at x xa: test each candle as anchor = first bar of B? use offset param
    pass
xa=float(sys.argv[12])
for sp in [float(s) for s in sys.argv[11].split(',')]:
  for idx0,t0,_,_ in B:
    err=[];n=0
    for (x,top,bot) in C:
        i=round((x-xa)/sp)
        j=[r for r in B if r[0]==idx0+i]
        if not j: continue
        err.append(abs(f(j[0][3])-bot)); n+=1
    if n>20:
        err.sort(); res.append((sum(err[:int(n*0.7)])/int(n*0.7),sp,t0,n))
res.sort(); print(res[:6])
