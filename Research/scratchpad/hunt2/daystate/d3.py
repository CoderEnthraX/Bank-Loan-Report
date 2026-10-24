import sys, os, importlib.util; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import gtscore; from engine2 import prepare
spec=importlib.util.spec_from_file_location('m','ds.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
tr,win=gtscore.load_gt('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/final')
for sym in sorted({w['sym'] for w in win}|{'SENSEX','CRUDE'}):
    P=prepare(sym); T=P['T']; ds=P['daystart']; day=[0]*len(T); k=0
    for i in range(len(T)):
        if ds[i]: k+=1
        day[i]=k
    cum={}
    for m in M.run(sym,{'dsMode':'none'}):
        if m['exit'] is None: continue
        d=day[m['exit']]; same = m['exit']==m['fill']
        if m['res']<0 and not same: cum[d]=cum.get(d,0)+1
        elif m['res']>0: cum[d]=cum.get(d,0)-2
        if m['res']<0 and not same and cum[d]>=3:
            j=m['exit']; end=max(x for x in range(len(T)) if day[x]==d)
            cov=sum(gtscore.covered(win,sym,T[x]) for x in range(j+1,end+1))
            print(sym, T[j], 'netLossR=%d'%cum[d], 'rest-of-day bars in A windows: %d/%d'%(cov,end-j))
