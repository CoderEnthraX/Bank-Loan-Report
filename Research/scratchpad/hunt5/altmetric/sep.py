import json,statistics as st,sys
D=json.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/altmetric/F.json'))
pos=[o for o in D if o['pos']]; neg=[o for o in D if not o['pos']]
lab=lambda o:o['sym'][:2]+o['t'][5:]
rows=[]
for k in D[0]['f']:
    for sgn in (1,-1):
        pv=sorted(sgn*o['f'][k] for o in pos); nv=[(sgn*o['f'][k],lab(o)) for o in neg]
        thr=pv[0]; rem=[x for x in nv if x[0]<thr]
        if not rem: continue
        sd=st.pstdev(pv) or 1
        gap=thr-max(x[0] for x in rem)
        # margin in units of positive sd, plus count of positives within gap below 2nd smallest
        rows.append((len(rem),gap/sd,k,sgn,thr,pv[1],[(round(a,3),b) for a,b in sorted(rem)],[(round(a,3),b) for a,b in nv if a>=thr]))
rows.sort(key=lambda r:(-r[0],-r[1]))
for r in rows[:int(sys.argv[1]) if len(sys.argv)>1 else 40]:
    print('%d/5 margin %.3f sd  %s%s  posMin %.4g pos2nd %.4g  removed %s  kept %s'%(r[0],r[1],'' if r[3]>0 else '-',r[2],r[4]*r[3],r[5]*r[3],r[6],r[7]))
