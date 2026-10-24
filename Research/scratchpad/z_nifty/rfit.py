import sys, statistics as st
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('NIFTY'); ts=[r['t'] for r in rows]
tr=[rows[0]['h']-rows[0]['l']]+[max(b['h']-b['l'],abs(b['h']-a['c']),abs(b['l']-a['c'])) for a,b in zip(rows,rows[1:])]
hl=[r['h']-r['l'] for r in rows]
def rma(x,n):
    o=[];s=None
    for i,v in enumerate(x):
        s=v if s is None else (s*(n-1)+v)/n; o.append(s)
    return o
def sma(x,n): return [sum(x[max(0,i-n+1):i+1])/len(x[max(0,i-n+1):i+1]) for i in range(len(x))]
def ema(x,n):
    o=[];s=None;k=2/(n+1)
    for v in x: s=v if s is None else s+k*(v-s); o.append(s)
    return o
# trades: displacement bar, measured R
T=[('2026-10-05 09:25',36.15),('2026-10-05 10:35',66.85),('2026-10-06 09:45',49.85),('2026-10-07 10:25',48.9),('2026-10-07 10:55',49.5),
('2026-10-08 10:35',49.8),('2026-10-08 13:15',48.7),('2026-10-09 10:05',31.15),('2026-10-09 13:40',32.4),('2026-10-12 09:50',60.6)]
cands={}
for n in (5,7,10,14,20,30,50):
    cands[f'rmaTR{n}']=rma(tr,n); cands[f'smaTR{n}']=sma(tr,n); cands[f'rmaHL{n}']=rma(hl,n); cands[f'smaHL{n}']=sma(hl,n); cands[f'emaTR{n}']=ema(tr,n)
res=[]
for k,X in cands.items():
    for off in (0,1):
        ratios=[R/X[ts.index(t)-off] for t,R in T]
        cv=st.pstdev(ratios)/st.mean(ratios)
        res.append((cv,k,off,[round(r,3) for r in ratios]))
res.sort()
for r in res[:12]: print('%.4f'%r[0],r[1],'off',r[2],r[3])
