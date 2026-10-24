import sys, subprocess, numpy as np
img=sys.argv[1]; box=sys.argv[2:6]; xref=float(sys.argv[6]); s0=float(sys.argv[7])
out=subprocess.run(['python3','-I','detect.py',img]+box,capture_output=True,text=True).stdout.split('\n')
xs=[float(l.split()[0]) for l in out if l.strip() and 4<=int(l.split()[1][1:])<=9]
xs=np.array(xs)
k=[0]
for i in range(1,len(xs)):
    k.append(k[-1]+round((xs[i]-xs[i-1])/s0))
k=np.array(k,float)
A=np.vstack([k,np.ones_like(k)]).T
(s,b),_,_,_=np.linalg.lstsq(A,xs,rcond=None)
r=xs-(b+k*s)
kref=(xref-b)/s
print('spacing %.4f'%s,'k of xref %.3f'%kref,'resid max %.2f'%abs(r).max(),'n',len(xs),'krange',k.min(),k.max())
for x,kk,rr in zip(xs,k,r):
    if abs(rr)>1.5: print('bad',x,kk,round(rr,2))
