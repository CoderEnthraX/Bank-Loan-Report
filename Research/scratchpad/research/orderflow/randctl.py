import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/orderflow')
sys.argv=[sys.argv[0]]+sys.argv[1:]
import drive, lib
frac=float(sys.argv[1]); seeds=range(int(sys.argv[2]),int(sys.argv[3]))
for k in seeds:
    tr=lib.run_all(drive.M, {"of_phantom":True,"of_gate":[["rand%d"%k,"ge",frac]]}); tn,te=lib.split(tr)
    imp=sum((sum(t['res'] for t in tr if t['sym']==s)/max(1,len([t for t in tr if t['sym']==s]))) > (sum(t['res'] for t in drive.base if t['sym']==s)/len([t for t in drive.base if t['sym']==s])) for s in lib.SYMS)
    a,b,c=lib.stats(tr),lib.stats(tn),lib.stats(te)
    print(json.dumps(dict(frac=frac,seed=k,n=a['n'],tot=a['totR2'],trE2=b['E2'],teE2=c['E2'],teE1=c['E1'],teE15=c['E15'],imp=imp))); sys.stdout.flush()
