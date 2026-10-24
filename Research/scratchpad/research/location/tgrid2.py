"""TRAIN-only full-model sweep: every feature, cut 15%/30% of TRAIN baseline trades from either tail. Writes results to grid2.json."""
import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(D)); sys.path.insert(0, D)
import lib, feats
MOD = D + '/combo_loc.py'
base = lib.run_all(MOD, {}); bn, _ = lib.split(base)
for x in bn:
    F = feats.compute(x['sym'])
    for nm in feats.NAMES: x[nm] = feats.feature(F, nm, x['arm'], x['dir'])
def m(v): return sum(v)/len(v) if v else float('nan')
sb = lib.stats(bn); out = []
for nm in feats.NAMES:
    v = sorted(x[nm] for x in bn if x[nm] is not None)
    for p in (0.15, 0.3):
        for side in ('le', 'ge'):
            th = v[int(len(v) * (1 - p))] if side == 'le' else v[int(len(v) * p)]
            o = {"loc": [[nm, side, th]]}
            tn, _ = lib.split(lib.run_all(MOD, o)); s = lib.stats(tn)
            k = sum(m([x['res'] for x in tn if x['sym']==y]) > m([x['res'] for x in bn if x['sym']==y]) for y in lib.SYMS[:8])
            out.append(dict(o=o, p=p, n=s['n'], E1=s['E1'], E15=s['E15'], E2=s['E2'], tot=s['totR2'], k=k))
            print('%-9s %s cut%2d%% th %8.3f  n=%d E1 %+.3f E15 %+.3f E2 %+.3f (d %+.3f) tot %+.0f syms %d/8' % (nm, side, p*100, th, s['n'], s['E1'], s['E15'], s['E2'], s['E2']-sb['E2'], s['totR2'], k), flush=True)
            with open(D + '/progress.md', 'a') as f: f.write('- TRAINsweep %s | TRAIN n=%d E1 %+.3f E15 %+.3f E2 %+.3f symsTR %d/8\n' % (json.dumps(o), s['n'], s['E1'], s['E15'], s['E2'], k))
json.dump(out, open(D + '/grid2.json', 'w'))
