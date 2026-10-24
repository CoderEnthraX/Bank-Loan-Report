import csv,sys
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/data/NSE_DLY_NIFTY.csv'
a,b=sys.argv[1],sys.argv[2]
for i,r in enumerate(csv.DictReader(open(F))):
    t=r['time'][:16].replace('T',' ')
    if a<=t<=b:
        o,h,l,c=(float(r[k]) for k in ('open','high','low','close'))
        m=('LF ' if r['Long Fill']=='1' else '')+('SF ' if r['Short Fill']=='1' else '')+('LE ' if r['Long Event']=='1' else '')+('SE ' if r['Short Event']=='1' else '')
        print(f"{i:5d} {t[5:]} O {o:9.2f} H {h:9.2f} L {l:9.2f} C {c:9.2f} mid {(o+c)/2:9.3f} rng {h-l:6.2f} body {c-o:7.2f} vw {float(r['VWAP']):9.2f} {m}")
