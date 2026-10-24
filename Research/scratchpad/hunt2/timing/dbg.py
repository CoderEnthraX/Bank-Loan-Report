import sys, importlib.util, json
spec = importlib.util.spec_from_file_location('m', sys.argv[1]); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sym, a, b = sys.argv[2], sys.argv[3], sys.argv[4]; inp = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
inp['dbg'] = True
tr = M.run(sym, inp)
from engine import prepare
for d in M.DBG:
    if a <= d['t'] <= b:
        print(f"{d['t'][5:]} {'up' if d['up'] else 'dn'} rng {d['rng']:.2f} body% {d['body']:3.0f} ext% {d['ext']:3.0f} brk10 L{d['brk10L']:+.2f} S{d['brk10S']:+.2f} brk L{d['brkL']:+.2f} S{d['brkS']:+.2f} mom {d['mom']:+.2f} slope {d['slope'] if d['slope'] is None else round(d['slope']/d['A'],3)} cv {d['cv']:+.2f} {'BULL' if d['bull'] else ''}{'BEAR' if d['bear'] else ''} st {d['st']} eL {d['entL']:.6g} eS {d['entS']:.6g} dR {d['dayRiskR']} A {d['A']:.4g}")
for t in tr:
    pass
