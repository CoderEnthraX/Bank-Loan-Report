import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
sym,cf,x0,i0,s,yref,pref,k=sys.argv[1],sys.argv[2],float(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7]),float(sys.argv[8])
step=int(sys.argv[9]) if len(sys.argv)>9 else 3
D={r['i']:r for r in load(sym)}
P=lambda y: pref-(y-yref)/k
out=[]; errs=[]
for l in open(cf).read().split('\n')[1:]:
  f=l.split()
  if len(f)<7: continue
  x=float(f[0]); i=round(i0+(x-x0)/s)
  if i not in D: continue
  r=D[i]; ph,pl=P(int(f[1])),P(int(f[2]))
  errs.append((round(ph-r['h']),round(pl-r['l'])))
  out.append('%s %s %s %.0f/%.0f vs %g/%g'%(f[0],r['t'][5:],f[5][0],ph,pl,r['h'],r['l']))
print(' | '.join(out[::step]))
