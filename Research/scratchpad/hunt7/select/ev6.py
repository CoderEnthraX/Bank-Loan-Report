"""stateless count of displacement events that break the 6-bar but not the 10-bar extreme; in/out of A windows; traded by alt?"""
import sys, os, json, importlib.util
F=S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; sys.path.insert(0,F)
import gtscore
d=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('m',os.path.join(d,'sel.py')); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
base=json.loads(sys.argv[1]); L=int(sys.argv[2]) if len(sys.argv)>2 else 6
tr,win=gtscore.load_gt(os.path.join(F,'..','gt','final'))
wsyms=sorted({w['sym'] for w in win}); print('window syms',wsyms)
for sym in ('NSE_NIFTY1','MCX_NATURALGAS','CRUDE','SENSEX','NIFTY','GC','EURUSD','NASDAQ','US30','ETH'):
    out=[]
    for bl in (0,L):
        M.DBG.clear(); q=dict(base); q.update(brkLen=bl,dbg=True); t=M.run(sym,q); out.append(({r['i']:r for r in M.DBG},{(x['arm']) for x in t}))
    (d0,a0),(d6,a6)=out
    ev=[i for i in d6 if (d6[i]['bullDisp'] and not d0[i]['bullDisp']) or (d6[i]['bearDisp'] and not d0[i]['bearDisp'])]
    gs=gtscore.norm(sym) if hasattr(gtscore,'norm') else sym
    inw=[i for i in ev if gtscore.covered(win,gs,d6[i]['t'])]
    print(f"{sym:15s} events {len(ev)} inA {len(inw)} armedAlt {sum(1 for i in ev if i in a6)} | inA: "+', '.join(f"{d6[i]['t']}{'*' if i in a6 else ''}" for i in inw))
