import json, sys, os, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/xl')
from engine2 import prepare
from engine import rma
import gtscore
from load_xl import load
spec=importlib.util.spec_from_file_location('m',S+'/hunt5/stats/combo.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
CAND={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
Dj=json.load(open(S+'/hunt3/pooled/featV.json'))
EX={('CRUDE','2026-10-06 20:55'),('CRUDE','2026-10-12 13:40'),('CRUDE','2026-10-15 18:30'),('CRUDE','2026-10-16 11:40'),('ETH','2026-10-11 00:05')}
items=[o for o in Dj if o['lab'] in('takenA','takenB') or (o['sym'],o['t']) in EX]
Pc={}
def er(o,n=10):
    P=Pc.setdefault(o['sym'],prepare(o['sym'])); C=P['C']; i=o['i']
    path=sum(abs(C[j]-C[j-1]) for j in range(i-n+1,i+1)); return o['d']*(C[i]-C[i-n])/path
for o in items: o['er']=er(o); o['ex']=(o['sym'],o['t']) in EX
tr,win=gtscore.load_gt(os.path.join(S,'gt','final')); tr=[t for t in tr if not str(t.get('conf') or '').startswith('xl')]
X=[x for x in load() if x['sym'] in ('SENSEX','CRUDE')]; fixT={66:'09:40'}
def evalA(thr):  # thr: dict sym->erMin
    gtscore.run=lambda P,cfg:(P.setdefault(('atr',14),rma(P['tr'],14)),M.run(P['sym'],{**CAND,'erMin':thr.get(P['sym'],0.0)}))[1]
    r,rows=gtscore.score({},tr,[dict(w) for w in win],detail=True)
    out={}
    for row in rows:
        s=row[1]; k='exact' if row[0]=='ok' else 'miss' if row[0]=='MISS' else 'extra' if row[0]=='EXTRA' else 'near'
        out.setdefault(s,dict(exact=0,miss=0,extra=0,near=0))[k]+=1
    return out
def evalB(thr,sym):
    P=prepare(sym); T=P['T']; idx={t:i for i,t in enumerate(T)}; trades=M.run(sym,{**CAND,'erMin':thr.get(sym,0.0)}); tm=0; n=0
    for x in [x for x in X if x['sym']==sym]:
        n+=1; f=idx.get(x['date']+' '+fixT.get(x['n'],x['tin']))
        if any(m['dir']==x['d'] and f is not None and abs(m['fill']-f)<=1 for m in trades): tm+=1
    return tm,n
SYMS=['CRUDE','GC','NASDAQ','NIFTY','US30','SENSEX','EURUSD','ETH']
base=evalA({s:0.2 for s in SYMS+[]}); none=evalA({})
print('per-symbol A, erMin 0.2 everywhere :',{s:tuple(base.get(s,{}).get(k,0) for k in('exact','miss','extra')) for s in SYMS})
print('per-symbol A, erMin 0 (dropped)    :',{s:tuple(none.get(s,{}).get(k,0) for k in('exact','miss','extra')) for s in SYMS})
for rule in ('mid','low'):
    print('=== rule',rule)
    tot=dict(exact=0,miss=0,extra=0); thrs={}
    for H in SYMS:
        oth=[o for o in items if o['sym']!=H]
        tmin=min(o['er'] for o in oth if not o['ex']); ex=[o['er'] for o in oth if o['ex'] and o['er']<tmin]
        lo=max(ex) if ex else 0.0; thr=(lo+tmin)/2 if rule=='mid' else lo+0.002
        # held-out symbol's own taken-min / extras
        hs=[o for o in items if o['sym']==H]; htm=min([o['er'] for o in hs if not o['ex']] or [9]); hex_=[round(o['er'],3) for o in hs if o['ex']]
        thrs[H]=thr
        a=evalA({H:thr}).get(H,{}); b=''
        if H in('CRUDE','SENSEX'): b=' B %d/%d'%evalB({H:thr},H)
        bb=base.get(H,{})
        print(f"{H:7s} others: taken-min {tmin:.3f} extras-below {sorted(round(e,3) for e in ex)} -> thr {thr:.4f} | held-out: taken-min {htm:.3f} extras {hex_} | A {a.get('exact',0)}/{a.get('miss',0)}/{a.get('extra',0)}{b}   (erMin .2: {bb.get('exact',0)}/{bb.get('miss',0)}/{bb.get('extra',0)}; none: {none.get(H,{}).get('exact',0)}/{none.get(H,{}).get('miss',0)}/{none.get(H,{}).get('extra',0)})")
        for k in tot: tot[k]+=a.get(k,0)
    print('  LOSO total A', tot)
print('B reference CRUDE/SENSEX at 0.2:',evalB({'CRUDE':.2},'CRUDE'),evalB({'SENSEX':.2},'SENSEX'),' at 0:',evalB({},'CRUDE'),evalB({},'SENSEX'))
