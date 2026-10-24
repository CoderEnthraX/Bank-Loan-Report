import sys, os, importlib.util
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; sys.path.insert(0,F); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl')
import gtscore
from engine2 import prepare
from engine import rma
from load_xl import load
spec = importlib.util.spec_from_file_location('m', 'kc.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
tr, win = gtscore.load_gt(os.path.join(F,'..','gt','final'))
tr = [t for t in tr if not str(t.get('conf') or '').startswith('xl')]
XL = load(); out=[]
for s in sorted({t['sym'] for t in tr} | {'CRUDE','SENSEX'}):
    P=prepare(s); T=P['T']; A=rma(P['tr'],14); C=P['C']; O=P['O']; H=P['H']; L=P['L']; V=P['V']; idx={t:i for i,t in enumerate(T)}; ds=P['daystart']
    # previous session stats per bar
    pv=[None]*len(T); pc=[None]*len(T); po=[None]*len(T); ph=[None]*len(T); pl=[None]*len(T); cur=None; prev=None; so=None
    for i in range(len(T)):
        if ds[i]:
            if i>0: prev=(V[i-1], C[i-1], so, hh, ll)
            so=O[i]; hh=H[i]; ll=L[i]
        else:
            hh=max(hh,H[i]) if so is not None else H[i]; ll=min(ll,L[i]) if so is not None else L[i]
        if prev: pv[i],pc[i],po[i],ph[i],pl[i]=prev
    for m in M.run(s, {"dayStopR":0,"legFrom":"exit","netMin":2}):
        g=next((g for g in tr if g['sym']==s and g['fill']==T[m['fill']] and g['d']==m['dir']), None)
        r=None
        if g and g.get('stop') and g.get('entry'): r=abs(g['entry']-g['stop'])/A[m['arm']]
        else:
            x=next((x for x in XL if x['sym']==s and x['d']==m['dir'] and idx.get(x['date']+' '+x['tin']) is not None and abs(idx[x['date']+' '+x['tin']]-m['fill'])<=1), None)
            if x: r=abs(x['entry']-x['stop'])/A[m['arm']]
        if r is None or pv[m['arm']] is None: continue
        i=m['arm']; d=m['dir']; a=A[i]
        out.append((('T' if r<1.3 else 'F'), 'mT' if m.get('tight') else '--', s, T[i], round(r,2), f"pV {d*(C[i]-pv[i])/a:+.1f} pC {d*(C[i]-pc[i])/a:+.1f} pDay {d*(pc[i]-po[i])/a:+.1f} open {d*(C[i]-O[i-P['sinceStart'][i]])/a:+.1f} gap {d*(O[i-P['sinceStart'][i]]-pc[i])/a:+.1f}", m['info']))
for o in sorted(out): print(*o)
