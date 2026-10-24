import sys, json, importlib.util
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
spec=importlib.util.spec_from_file_location('m', next((a for a in sys.argv[1:] if a.endswith('.py')), '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt4/combo.py')); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
# (sym, reading time, W, L, R, fills, active (dir, entry, stop) or None)
READ=[('CRUDE','2026-10-09 13:40',0,2,-2,2,None),('NASDAQ','2026-10-09 13:40',2,2,2,5,(1,31000.2,30963.8)),
      ('NASDAQ','2026-10-12 12:45',1,0,2,2,(-1,30984.1,31014.2)),('NIFTY','2026-10-12 12:40',2,0,4,1,None),
      ('SENSEX','2026-10-12 12:40',2,0,4,2,(-1,71977.95,72131.62)),('GC','2026-10-12 13:00',2,1,3,2,None)]
inp=next((json.loads(a) for a in sys.argv[1:] if a.startswith('{')), {})
ok=0
for sym,t,W,Lc,Rr,F,act in READ:
    P=prepare(sym); T=P['T']; ds=P['daystart']; tr=M.run(sym,inp)
    end=next(i for i,x in enumerate(T) if x>=t)
    st=max(i for i in range(end+1) if ds[i])
    ex=[x for x in tr if x['exit'] is not None and st<=x['exit']<=end]
    w=sum(1 for x in ex if x['res']>0); l=len(ex)-w; r=sum(x['res'] for x in ex)
    f=sum(1 for x in tr if st<=x['fill']<=end)
    a=[x for x in tr if x['fill']<=end and (x['exit'] is None or x['exit']>end)]
    am=(a[0]['dir'],round(a[0]['entry'],2),round(a[0]['stop'],2)) if a else None
    good=(w,l,r,f)==(W,Lc,Rr,F) and ((act is None and am is None) or (act and am and am[0]==act[0] and abs(am[1]-act[1])<0.05*abs(act[1]-act[2]) ))
    ok+=good
    print(f"{'OK ' if good else 'BAD'} {sym:7s} {t}: orig {W}W/{Lc}L {Rr:+}R fills {F} active {act} | model {w}W/{l}L {r:+.0f}R fills {f} active {am}")
print('MODEL DAY readings matched', ok, '/', len(READ))
