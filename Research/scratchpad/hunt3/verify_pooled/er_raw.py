import csv,sys
def load(f):
    return [(r['time'][:16].replace('T',' '),float(r['close'])) for r in csv.DictReader(open(f))]
D='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/data/'
def er(f,t,d,n=10):
    rows=load(D+f); idx=[k for k,(tt,c) in enumerate(rows) if tt==t]
    # file times are IST-offset; try match directly
    return rows,idx
cases=[('MCX_CRUDEOIL1.csv','2026-10-15 18:30',1),('MCX_CRUDEOIL1.csv','2026-10-12 13:40',1),('MCX_CRUDEOIL1.csv','2026-10-16 11:40',1),('MCX_CRUDEOIL1.csv','2026-10-06 20:55',1),('MCX_CRUDEOIL1.csv','2026-10-15 18:50',1),('MCX_CRUDEOIL1.csv','2026-10-12 14:15',1),('MCX_CRUDEOIL1.csv','2026-10-16 11:45',1),('BITSTAMP_ETHUSD.csv','2026-10-11 00:05',1),('BITSTAMP_ETHUSD.csv','2026-10-11 00:15',1),('NSE_DLY_NIFTY.csv','2026-10-07 09:35',-1)]
for f,t,d in cases:
    rows,idx=er(f,t,d)
    if not idx: print(f,t,'notfound',rows[0][0]); continue
    i=idx[0]; C=[c for _,c in rows]
    for n in (10,):
        path=sum(abs(C[j]-C[j-1]) for j in range(i-n+1,i+1)); net=d*(C[i]-C[i-n])
        print(f[:8],t,'ER%d=%.3f'%(n,net/path),'net',net,'path',path)
