import sys
src=open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/adxfit.py').read().split('cache={}')[0]
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
exec(src)
P=prepare('NIFTY'); rows=[dict(r) for r in P['rows']]
i=find(rows,'2026-10-12 12:40')
rows=rows[:i+1]; rows[i].update(o=22396.8,h=22402.2,l=22392.4,c=22400.1)
out=[]
for L in range(5,31):
    for S in sorted({L,5,7,10,14,20}):
        a=dmi(rows,L,S)[2][i]
        out.append((abs(a-39),L,S,round(a,1)))
out.sort(); print(out[:12])
