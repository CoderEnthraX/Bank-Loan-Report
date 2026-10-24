import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
from engine import rma
def sma(x,n): return [None if i<n-1 else sum(x[i-n+1:i+1])/n for i in range(len(x))]
for sym,t,want in [('CRUDE','2026-10-15 18:30','rej'),('CRUDE','2026-10-16 11:40','rej'),('GC','2026-10-09 20:50','acc'),('GC','2026-10-09 20:55','acc'),('CRUDE','2026-10-15 18:50','acc'),('CRUDE','2026-10-16 11:45','acc')]:
    P=prepare(sym); T=P['T']; i=T.index(t); C,O,H,L=P['C'],P['O'],P['H'],P['L']
    out=[]
    for nm,a in [('rma14',rma(P['tr'],14)),('rma14[1]',[None]+rma(P['tr'],14)[:-1]),('sma14',sma(P['tr'],14)),('rma10',rma(P['tr'],10)),('rma20',rma(P['tr'],20))]:
        d=1 if C[i]>O[i] else -1
        out.append(f"{nm}: mom {d*(C[i]-C[i-10])/a[i]:.3f} rng {(H[i]-L[i])/a[i]:.2f}")
    print(sym,t,want,'|', ' | '.join(out))
