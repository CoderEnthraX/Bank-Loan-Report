import sys, os, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/residual')
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import rc
base={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}; base.update(json.loads(sys.argv[1]))
r, rows = rc.score(base, True)
n=ok=0; bad=[]
from engine import prepare, rma
for x in rows:
    if x[0]!='ok' or len(x)<6: continue
    m, g = x[5].split()[1].split('/')
    if g in ('None',''): continue
    m=float(m); g=float(g); P=prepare(x[1]); 
    n+=1
    # tolerance 0.06 ATR approx via relative to entry/stop distance unavailable; use 0.06*|risk|/1.8
    e = float(x[4].split()[1].split('/')[0]); a = abs(e-m)/1.8 if abs(e-m)>0 else 1
    if abs(m-g) <= 0.06*a*1.8/1.8*1.0 + 0.06*a: ok+=1
    else: bad.append((x[1],x[2],round(m,2),g))
print({k:r[k] for k in ('exact','miss','extra')}, 'A stops ok', ok, '/', n, bad[:8])
