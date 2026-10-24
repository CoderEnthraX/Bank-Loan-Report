import json, subprocess, sys, importlib.util
from concurrent.futures import ThreadPoolExecutor
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; W=S+'/hunt5/altmetric'; MOD=W+'/combo_alt.py'
BASE={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True}
SYMS=['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']
def trades(o):
    spec=importlib.util.spec_from_file_location('m',MOD); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    return {(s,t['dir'],t['fill']) for s in SYMS for t in M.run(s,o)}
def one(arg):
    name,o=arg; o=dict(BASE,**o)
    a=subprocess.run(['python3','-I','score2.py',MOD,json.dumps(o),'d'],cwd=S+'/xl',capture_output=True,text=True,timeout=900).stdout
    b=subprocess.run(['python3','-I','extrasB.py',MOD,json.dumps(o)],cwd=S+'/xl',capture_output=True,text=True,timeout=900).stdout
    A=eval(a.split('(80):')[1].split('\n')[0]); Bl=a.split('time-matched ')[1].split('\n')[0]
    bm=int(Bl.split(',')[0]); bs=int(Bl.split('stop correct ')[1].split('/')[0]); px=b.count('PROVABLE-EXTRA')
    mm=[l.strip() for l in a.splitlines() if l.strip().startswith(('A ','B '))]
    t=trades(o); return name,A,bm,bs,px,t,mm
RUNS=[(n,json.loads(j)) for n,j in (x.split('|',1) for x in sys.argv[1:])]
ref=trades(dict(BASE,erMin=0.2))
with ThreadPoolExecutor(6) as ex: res=list(ex.map(one,RUNS))
for name,A,bm,bs,px,t,mm in res:
    print('%-22s A %d/%d/%d  B %d/42 stop %d/%d provB %d  | full data: %d trades, vs CANDIDATE -%d +%d'%(name,A['exact'],A['miss'],A['extra'],bm,bs,bm,px,len(t),len(ref-t),len(t-ref)))
    for l in mm: print('      ',l)
print('CANDIDATE full-data trades:',len(ref))
