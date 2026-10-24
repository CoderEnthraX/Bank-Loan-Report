"""TRAIN-only grid in the full model (no TEST output). usage: tgrid.py '<json list of opts>'"""
import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(D))
import lib
MOD = D + '/combo_loc.py'
bn, _ = lib.split(lib.run_all(MOD, {})); print('base TRAIN', lib.fmt(lib.stats(bn)))
def m(v): return sum(v)/len(v) if v else float('nan')
for o in json.loads(sys.argv[1]):
    tn, _ = lib.split(lib.run_all(MOD, o)); s = lib.stats(tn)
    k = sum(m([x['res'] for x in tn if x['sym']==y]) > m([x['res'] for x in bn if x['sym']==y]) for y in lib.SYMS[:8])
    print('%-70s' % json.dumps(o), lib.fmt(s), ' symsTR %d/8' % k)
    with open(D + '/progress.md', 'a') as f: f.write('- TRAINgrid %s | TRAIN n=%d E1 %+.3f E15 %+.3f E2 %+.3f symsTR %d/8\n' % (json.dumps(o), s['n'], s['E1'], s['E15'], s['E2'], k))
