"""align.py img x0 y0 x1 y1 xref index_ref s0  -> fits x-spacing and price scale from candle bodies"""
import sys, subprocess, numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); byi={r['i']:r for r in rows}
img=sys.argv[1]; box=sys.argv[2:6]; xref=float(sys.argv[6]); iref=int(sys.argv[7]); s0=float(sys.argv[8]); WMAX=int(sys.argv[9]) if len(sys.argv)>9 else 9
out=subprocess.run(['python3','-I','detect.py',img]+box,capture_output=True,text=True).stdout.split('\n')
C=[]
for l in out:
    if not l.strip(): continue
    p=l.split(); w=int(p[1][1:])
    if 4<=w<=WMAX: C.append((float(p[0]),int(p[3]),int(p[5]),p[6]))
xs=np.array([c[0] for c in C])
k=[0]
for i in range(1,len(xs)): k.append(k[-1]+round((xs[i]-xs[i-1])/s0))
k=np.array(k,float)
A=np.vstack([k,np.ones_like(k)]).T
(s,b),_,_,_=np.linalg.lstsq(A,xs,rcond=None)
kref=round((xref-b)/s)
idx=(k-kref+iref).astype(int)
print('spacing %.4f  x(index)= %.2f + %.4f*(index-%d)'%(s,b+kref*s,s,iref))
# price fit
P=[];Y=[];ok=[]
for (x,t,bt,col),i in zip(C,idx):
    r=byi.get(i)
    if r is None: continue
    hi=max(r['o'],r['c']); lo=min(r['o'],r['c'])
    if hi-lo<3: continue
    good=(col=='G')==(r['c']>r['o'])
    P+= [hi,lo]; Y+=[t,bt]; ok+=[good,good]
P=np.array(P);Y=np.array(Y);ok=np.array(ok)
import os
a0=-float(os.environ.get('PXPT','1.566'))
c0=np.median(Y[ok]-a0*P[ok])
m=ok&(abs(Y-(a0*P+c0))<4)
for it in range(6):
    A=np.vstack([P[m],np.ones(m.sum())]).T
    (a,c),_,_,_=np.linalg.lstsq(A,Y[m],rcond=None)
    res=Y-(a*P+c)
    m=ok&(abs(res)<3)
print('price fit: y = %.5f*price + %.2f  (px/pt %.4f) n=%d of %d, rms %.2f'%(a,c,-a,m.sum(),len(P),np.sqrt((res[m]**2).mean())))
print('colour mismatches:',[(round(x,1),i) for (x,t,bt,col),i in zip(C,idx) if i in byi and (col=='G')!=(byi[i]['c']>byi[i]['o']) and abs(byi[i]['c']-byi[i]['o'])>3])
print('first idx',idx.min(),byi.get(idx.min(),{}).get('t'),'last idx',idx.max(),byi.get(idx.max(),{}).get('t'))
np.save('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/z_nifty/fit_%s.npy'%img,np.array([b+kref*s,s,iref,a,c]))
if len(sys.argv)>10:
    for (x,t,bt,col),i in zip(C,idx):
        r=byi.get(i)
        if r is None: continue
        hi=max(r['o'],r['c']); lo=min(r['o'],r['c'])
        print('%7.1f %d %s top %d (%.1f) bot %d (%.1f) %s'%(x,i,r['t'],t,a*hi+c,bt,a*lo+c,col))
