import csv, sys, os
from datetime import datetime
D=sys.argv[1]
REF={ # symbol file -> (time IST, O,H,L,C) from the reference screenshots
 'COMEX_DL_GC1':[('2026-10-09T21:00',4213.6,4215.5,4212.3,4215.1)],
 'FX_IDC_EURUSD':[('2026-10-09T12:45',1.12261,1.12323,1.12257,1.12319),('2026-10-09T05:40',1.12123,1.12180,1.12121,1.12173)],
 'IG_NASDAQ':[('2026-10-09T12:10',30969.5,30972.8,30958.7,30969.9)],
 'MCX_CRUDEOIL1':[('2026-10-08T11:00',8734,8756,8734,8745),('2026-10-06T23:05',8641,8644,8622,8632)],
}
for f in sorted(os.listdir(D)):
    rows=list(csv.DictReader(open(os.path.join(D,f))))
    sym=f[:-4]
    t0,t1=rows[0]['time'],rows[-1]['time']
    days=sorted({r['time'][:10] for r in rows})
    fills=sum(1 for r in rows if r['Long Fill']=='1' or r['Short Fill']=='1')
    print(f"{sym:18s} bars={len(rows):5d}  {t0[:16]} -> {t1[:16]}  days={len(days)}  my-indicator fills in export={fills}")
    idx={r['time'][:16]:r for r in rows}
    for t,o,h,l,c in REF.get(sym,[]):
        r=idx.get(t)
        if not r: print(f"   {t}: NOT IN DATA"); continue
        got=tuple(float(r[k]) for k in ('open','high','low','close'))
        ok=all(abs(a-b)<1e-9 for a,b in zip(got,(o,h,l,c)))
        print(f"   check {t}: data O/H/L/C={got}  screenshot={(o,h,l,c)}  -> {'MATCH' if ok else 'DIFFERENT'}")
