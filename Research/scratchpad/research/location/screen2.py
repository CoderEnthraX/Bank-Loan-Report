import sys
sys.path.insert(0, '..'); sys.path.insert(0, '.')
import lib, feats
tr = lib.run_all(); tn, te = lib.split(tr)
for x in tr:
    F = feats.compute(x['sym'])
    for nm in feats.NAMES: x[nm] = feats.feature(F, nm, x['arm'], x['dir'])
def m(v): return sum(v)/len(v) if v else float('nan')
C = [('vwSig','le',1.7),('vwSig','le',2.0),('vwSig','le',2.15),('vwSig','le',2.4),('vwExtA','le',3.3),('vwExtA','le',4.0),('adx','le',30),('adx','le',34),
     ('consecC','le',3),('consec','le',3),('vwSlope','le',0.25),('rsi14','ge',55),('hour','ge',7)]
for nm, sd, th in C:
    rem = [x for x in tn if x[nm] is not None and (x[nm] > th if sd=='le' else x[nm] < th)]
    kept = [x for x in tn if x not in rem]
    per = []
    for s in lib.SYMS[:8]:
        a=[x['res'] for x in kept if x['sym']==s]; b=[x['res'] for x in rem if x['sym']==s]
        per.append('%s %+.2f/%+.2f(%d)'%(s[:3], m(a), m(b), len(b)))
    better = sum(1 for s in lib.SYMS[:8] if m([x['res'] for x in rem if x['sym']==s] or [9]) < m([x['res'] for x in kept if x['sym']==s]))
    print('%-8s %s %5.2f keep %d (%.0f%%) E2 kept %+.3f rem %+.3f  h1 kept %.3f rem %.3f  symsBetter %d/8' % (nm, sd, th, len(kept), 100*len(kept)/len(tn), m([x['res'] for x in kept]), m([x['res'] for x in rem]), m([x['hit1'] for x in kept]), m([x['hit1'] for x in rem]), better))
    print('    ', ' '.join(per))
