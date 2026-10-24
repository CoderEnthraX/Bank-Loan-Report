"""setfit.py img x0 s iref  price:y price:y ... -> saves fit with LSQ price scale"""
import sys,numpy as np
img=sys.argv[1]; x0=float(sys.argv[2]); s=float(sys.argv[3]); iref=int(sys.argv[4])
P=[];Y=[]
for a in sys.argv[5:]:
    p,y=a.split(':'); P.append(float(p)); Y.append(float(y))
P=np.array(P);Y=np.array(Y)
A=np.vstack([P,np.ones_like(P)]).T
(a,c),_,_,_=np.linalg.lstsq(A,Y,rcond=None)
print('y = %.5f*p + %.2f ; resid'%(a,c), np.round(Y-(a*P+c),2))
np.save('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/z_nifty/fit_%s.npy'%img,np.array([x0,s,iref,a,c]))
