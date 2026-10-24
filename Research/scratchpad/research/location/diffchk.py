import sys, json, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(D))
import lib
MOD = D + '/combo_loc.py'
bn, _ = lib.split(lib.run_all(MOD, {}))
def m(v): return sum(v)/len(v) if v else float('nan')
for o in json.loads(sys.argv[1]):
    tn, _ = lib.split(lib.run_all(MOD, o))
    kb = {(x['sym'], x['fill'], x['dir']) for x in bn}; kn = {(x['sym'], x['fill'], x['dir']) for x in tn}
    rem = [x for x in bn if (x['sym'], x['fill'], x['dir']) not in kn]; new = [x for x in tn if (x['sym'], x['fill'], x['dir']) not in kb]
    print(json.dumps(o), 'removed %d E2 %+.3f | new %d E2 %+.3f | common %d' % (len(rem), m([x['res'] for x in rem]), len(new), m([x['res'] for x in new]), len(tn)-len(new)))
