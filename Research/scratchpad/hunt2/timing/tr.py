import sys, importlib.util, json
spec = importlib.util.spec_from_file_location('m', sys.argv[1]); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sym, a, b = sys.argv[2], sys.argv[3], sys.argv[4]; inp = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
from engine2 import prepare
T = prepare(sym)['T']
for t in M.run(sym, inp):
    if a <= T[t['fill']] <= b:
        print(f"{'L' if t['dir']>0 else 'S'} arm {T[t['arm']]} fill {T[t['fill']][5:]} e {t['entry']:.6g} s {t['stop']:.6g} exit {T[t['exit']][5:] if t['exit'] is not None else None} {t['res']} tight {t.get('tight')}")
