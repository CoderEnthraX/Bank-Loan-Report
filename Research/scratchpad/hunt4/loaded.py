"""Compare model full-history W/L/R with the original's LOADED BARS readings (win%, total R at a known time)."""
import sys, json, importlib.util
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
spec=importlib.util.spec_from_file_location('m','/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt4/combo.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
READ = [('CRUDE','2026-10-09 13:40',35,24),('ETH','2026-10-12 06:00',37,34),('GC','2026-10-12 13:00',36,32),('NASDAQ','2026-10-09 13:40',38,52),
        ('NASDAQ','2026-10-12 12:45',38,51),('NIFTY','2026-10-12 12:40',35,22),('SENSEX','2026-10-12 12:40',34,13),('US30','2026-10-12 13:00',36,27)]
inp = json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
cache={}
for sym,t,wp,rr in READ:
    if sym not in cache:
        P=prepare(sym); cache[sym]=(P['T'], M.run(sym,inp))
    T,tr=cache[sym]
    end=next((i for i,x in enumerate(T) if x>=t), len(T)-1)
    done=[x for x in tr if x['exit'] is not None and x['exit']<=end]
    # best start: scan start bars, report the start whose (win%, R) is closest to the reading
    best=None
    for k in range(len(done)):
        sub=done[k:]; W=sum(1 for x in sub if x['res']>0); N=len(sub); R=sum(x['res'] for x in sub)
        err=abs(round(100*W/N)-wp)+abs(R-rr)
        if best is None or err<best[0]: best=(err,T[sub[0]['fill']],N,W,round(100*W/N),R)
    W=sum(1 for x in done if x['res']>0); N=len(done); R=sum(x['res'] for x in done)
    print(f"{sym:7s} @{t}  orig {wp}% {rr:+}R | model all-data from {T[0][:10]}: N={N} {round(100*W/N)}% {R:+.0f}R | closest start {best[1][:10]}: N={best[2]} {best[4]}% {best[5]:+.0f}R err={best[0]:.0f}")
