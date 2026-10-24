import sys, os, importlib.util
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; sys.path.insert(0,F); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl')
import gtscore
from engine2 import prepare
from engine import rma
from load_xl import load
spec = importlib.util.spec_from_file_location('m', 'kc.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
tr, win = gtscore.load_gt(os.path.join(F,'..','gt','final'))
tr = [t for t in tr if not str(t.get('conf') or '').startswith('xl')]
XL = load()
def ema(x, n):
    k = 2/(n+1); out=[]; e=x[0]
    for v in x: e = e + k*(v-e); out.append(e)
    return out
rows=[]
for s in sorted({t['sym'] for t in tr} | {'CRUDE','SENSEX'}):
    P=prepare(s); T=P['T']; A=rma(P['tr'],14); C=P['C']; idx={t:i for i,t in enumerate(T)}
    E={n:ema(C,n) for n in (50,100,200,300,600)}
    for m in M.run(s, {"dayStopR":0}):
        g=next((g for g in tr if g['sym']==s and g['fill']==T[m['fill']] and g['d']==m['dir']), None)
        r=None
        if g and g.get('stop') and g.get('entry'): r=abs(g['entry']-g['stop'])/A[m['arm']]; src='A'
        else:
            x=next((x for x in XL if x['sym']==s and x['d']==m['dir'] and idx.get(x['date']+' '+x['tin']) is not None and abs(idx[x['date']+' '+x['tin']]-m['fill'])<=1), None)
            if x: r=abs(x['entry']-x['stop'])/A[m['arm']]; src='B'
        if r is None: continue
        i=m['arm']; d=m['dir']
        rows.append((s, T[i], src, round(r,2), 'T' if r<1.3 else 'F', 'mT' if m.get('tight') else '', m['info'], ' '.join(f"{n}:{d*(C[i]-E[n][i])/A[i]:+.1f}" for n in E), P['sinceStart'][i]))
for r in rows:
    if r[4]=='T' or r[5]: print(*r)
print('--- full-stop trades: count with d*(C-EMA)<0 per n')
for n,k in ((50,0),(100,1),(200,2),(300,3),(600,4)):
    neg=[r for r in rows if r[4]=='F' and float(r[7].split()[k].split(':')[1])<0]
    print(n, len(neg), 'of', sum(r[4]=='F' for r in rows))
