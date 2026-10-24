import sys, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare, run
from rec import BEST
spec = importlib.util.spec_from_file_location('rule', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
cfg = dict(BEST); cfg['stopFn'] = mod.stop_fn
P = prepare('US30'); A = P[('atr', 14)]
for x in run(P, cfg):
    if '2026-10-06 20:00' <= P['T'][x['fill']] <= '2026-10-08 02:00':
        print(P['T'][x['arm']], P['T'][x['fill']], x['dir'], round(x['dir'] * (x['entry'] - x['stop']) / A[x['arm']], 2), x['res'], P['T'][x['exit']] if x['exit'] else None)
