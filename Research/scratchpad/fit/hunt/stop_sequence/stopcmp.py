import sys, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare, run
from rec import BEST
from tightdata import TRADES
spec = importlib.util.spec_from_file_location('rule', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
cfg = dict(BEST); cfg['stopFn'] = mod.stop_fn
for s in sorted({t['sym'] for t in TRADES}):
    P = prepare(s); A = P[('atr', 14)]; byf = {(x['fill'], x['dir']): x for x in run(P, cfg)}
    for t in [t for t in TRADES if t['sym'] == s and t['tight']]:
        x = byf.get((t['fill_i'], t['d']))
        if x: print(f"{s:6s} {t['fill']} GT stop {t['stop']:.6g} engine {x['stop']:.6g} err {(x['stop']-t['stop'])/A[x['arm']]:+.3f} ATR  engine exit {P['T'][x['exit']] if x['exit'] else None} res {x['res']} | GT exit {t['exit']} {t['out']}")
        else: print(s, t['fill'], 'NOT MATCHED')
