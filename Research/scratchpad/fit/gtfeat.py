import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare
from gtscore import load_gt
from adxfit import dmi
EXTRA = [  # earlier exact/near-exact originals not in the json groups yet
 ('GC',1,'2026-10-09 04:40',4165.9,4161.75),('GC',1,'2026-10-09 07:30',None,None),('GC',1,'2026-10-09 11:20',4221.3,4214.85),
 ('GC',-1,'2026-10-09 18:25',None,4203.9),('GC',1,'2026-10-09 20:55',4214.3,4205.5),('GC',1,'2026-10-12 05:55',4234.3,4226.1),
 ('EURUSD',1,'2026-10-09 05:45',1.12148,1.12109),('EURUSD',1,'2026-10-09 07:05',None,1.12211),('EURUSD',1,'2026-10-09 12:55',1.1229,1.12224),
 ('EURUSD',-1,'2026-10-09 15:30',1.12174,1.12209),('EURUSD',-1,'2026-10-09 17:40',None,1.1213),
 ('SENSEX',-1,'2026-10-12 11:20',71977.95,72131.62),('NASDAQ',-1,'2026-10-12 11:15',30984.1,31014.2),('NASDAQ',1,'2026-10-09 12:55',31000.2,30963.8)]
def impulse(P, fi, d, entry):
    O,H,L,C=P['O'],P['H'],P['L'],P['C']; best=None
    for k in range(1,9):
        j=fi-k
        mid=(O[j]+C[j])/2
        for n in (6,10):
            lv = max(H[j-n:j]) if d>0 else min(L[j-n:j])
            cand = max(mid,lv) if d>0 else min(mid,lv)
            err = abs(cand-entry) if entry else (0 if ((C[j]>max(H[j-10:j])) if d>0 else (C[j]<min(L[j-10:j]))) else 9e9)
            if best is None or err < best[0]-1e-12: best=(err,j,n,cand,'mid' if cand==mid else f'lvl{n}')
    return best
def feats(sym, d, fill, entry, stop):
    P=prepare(sym); T=P['T']; idx={t:i for i,t in enumerate(T)}
    if fill not in idx: return None
    fi=idx[fill]; err,j,n,cand,src=impulse(P,fi,d,entry)
    A=P[('atr',14)][j] if ('atr',14) in P else None
    if A is None:
        from engine import rma; P[('atr',14)]=rma(P['tr'],14); A=P[('atr',14)][j]
    if 'dmi' not in P: P['dmi']=dmi(P['rows'],14,14)
    dip,dim,adx=P['dmi']
    e = entry if entry else cand
    rr = abs(e-stop)/A if stop else None
    return dict(sym=sym,d=d,fill=fill,imp=T[j],src=src,entry=e,err=err,R_atr=rr,adx=adx[j],dip=dip[j],dim=dim[j],
                adx_slope=adx[j]-adx[j-3], since=P['sinceStart'][j], cvwap=(P['C'][j]-P['V'][j])/A, rng=(P['H'][j]-P['L'][j])/A,
                body=abs(P['C'][j]-P['O'][j])/A, atr_rel=A/ (sum(P['tr'][j-100:j])/100))
if __name__=='__main__':
    tr,win=load_gt(os.path.join(os.path.dirname(__file__),'..','gt','final'))
    rows=[(t['sym'],t['d'],t['fill'],t['entry'],t['stop']) for t in tr]+EXTRA
    out=[]
    for r in rows:
        f=feats(*r)
        if f: out.append(f)
    out.sort(key=lambda f:(f['R_atr'] or 0))
    print(f"{'sym':7s} d fill             imp    src    R/ATR  ADX  dADX  DI+  DI-  since cVWAP  rng  body atrRel")
    for f in out:
        print(f"{f['sym']:7s} {'L' if f['d']>0 else 'S'} {f['fill']} {f['imp'][11:]} {f['src']:6s} {f['R_atr'] if f['R_atr'] is None else round(f['R_atr'],3)!s:6s} {f['adx']:4.0f} {f['adx_slope']:+5.1f} {f['dip']:4.0f} {f['dim']:4.0f} {f['since']:5d} {f['cvwap']:+5.2f} {f['rng']:4.2f} {f['body']:4.2f} {f['atr_rel']:5.2f}")
