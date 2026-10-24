import sys, pickle, math
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab)
nm='h60_asl_E20_3'
print('threshold stability (ghost exact)', nm)
for th in (1.2,1.4,1.5,1.652,1.8,2.0,2.2,2.5,3.0):
    a=[x for x in tn if x['f'][nm] is None or x['f'][nm]<=th]; b=[x for x in te if x['f'][nm] is None or x['f'][nm]<=th]
    print(' <=%.2f TRAIN keep %.0f%% dE %+.3f | TEST keep %.0f%% dE %+.3f | tot %+.0f'%(th,100*len(a)/len(tn),ev.E(a)-ev.E(tn),100*len(b)/len(te),ev.E(b)-ev.E(te),sum(x['res'] for x in a+b)))
rem=[x for x in tab if x['f'][nm] is not None and x['f'][nm]>1.652]
w=[x for x in rem if x['f']['h60_sl_E20_3']>0]; c=[x for x in rem if x['f']['h60_sl_E20_3']<=0]
print('removed n=%d E %+.3f | with-1h-trend n=%d E %+.3f | counter n=%d E %+.3f'%(len(rem),ev.E(rem),len(w),ev.E(w),len(c),ev.E(c)))
for nm2 in ('h60_sl_E20_3',):
  for th in (1.0,1.3,1.652,2.0):
    a=[x for x in tn if x['f'][nm2] is None or x['f'][nm2]<=th]; b=[x for x in te if x['f'][nm2] is None or x['f'][nm2]<=th]
    print(' signed %s<=%.2f TRAIN keep %.0f%% dE %+.3f | TEST keep %.0f%% dE %+.3f'%(nm2,th,100*len(a)/len(tn),ev.E(a)-ev.E(tn),100*len(b)/len(te),ev.E(b)-ev.E(te)))
# by month / symbol
for mo in ('2026-09','2026-10'):
    s=[x for x in tab if x['t'][:7]==mo]; k=[x for x in s if x['f'][nm] is None or x['f'][nm]<=1.652]
    print(mo,'base n=%d E %+.3f  kept n=%d E %+.3f'%(len(s),ev.E(s),len(k),ev.E(k)))
for sy in ev.SYMS:
    s=[x for x in tab if x['sym']==sy]; k=[x for x in s if x['f'][nm] is None or x['f'][nm]<=1.652]; r=[x for x in s if x not in k]
    print(' %-15s base n=%3d E %+.3f kept n=%3d E %+.3f removed E %+.3f'%(sy,len(s),ev.E(s),len(k),ev.E(k),ev.E(r) if r else float('nan')))
# orig fisher
o=pickle.load(open('orig.pkl','rb')); 
rm=[x for x in o if x['f'][nm] is not None and x['f'][nm]>1.652]; kp=[x for x in o if x not in rm]
a,b,c_,d=sum(not x['win'] for x in rm),sum(x['win'] for x in rm),sum(not x['win'] for x in kp),sum(x['win'] for x in kp)
from math import comb
N=a+b+c_+d; K=a+c_; n=a+b
p=sum(comb(K,i)*comb(N-K,n-i) for i in range(a,min(K,n)+1))/comb(N,n)
print('orig: removed %dL/%dW kept %dL/%dW one-sided Fisher p=%.3f'%(a,b,c_,d,p))
