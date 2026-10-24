"""diffcfg.py module.py '{optsA}' '{optsB}' -> trades that differ between two configs on all symbols, flagged by A-window coverage and B log."""
import sys, os, json, importlib.util
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; sys.path.insert(0,F); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl')
import gtscore; from engine2 import prepare; from load_xl import load
spec=importlib.util.spec_from_file_location('m',sys.argv[1]); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
oa=json.loads(sys.argv[2]); ob=json.loads(sys.argv[3])
tr,win=gtscore.load_gt(os.path.join(F,'..','gt','final'))
X=load()
for sym in ['BTC' if 0 else s for s in sorted({w['sym'] for w in win}|{'SENSEX','CRUDE'})]:
    P=prepare(sym); T=P['T']
    def key(m): return (m['dir'],m['fill'])
    a={key(m):m for m in M.run(sym,oa)}; b={key(m):m for m in M.run(sym,ob)}
    for k in sorted(set(a)^set(b), key=lambda k:k[1]):
        m=a.get(k) or b.get(k); t=T[m['fill']]
        cov=gtscore.covered(win,sym,t); gt=any(g['sym']==sym and g['fill']==t and g['d']==m['dir'] for g in tr)
        xl=[x['n'] for x in X if x['sym']==sym and x['d']==m['dir'] and (x['date']+' '+x['tin'])==t]
        print('A-only' if k in a else 'B-only', sym, t, 'L' if m['dir']>0 else 'S', 'res=%s'%m['res'], 'inWin' if cov else '', 'GT' if gt else '', ('XL#%s'%xl) if xl else '')
