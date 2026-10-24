"""static classification of r_pdx variants on the 80 trades (fast, no engine)."""
import os, json, sys, itertools, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from tightdata import TRADES
from engine2 import prepare
spec = importlib.util.spec_from_file_location('rpdx', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/r_pdx.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
grid = json.loads(sys.argv[1])
keys = list(grid)
for vals in itertools.product(*[grid[k] for k in keys]):
    c = dict(zip(keys, vals)); m.CFG.update(c)
    bad = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr', 14)][i]
        s = m.stop_fn(P, i, t['d'], t['entry'], t['entry'] - t['d'] * 1.8 * A, A, {})
        pt = t['d'] * (t['entry'] - s) / A < 1.4
        if pt != t['tight']: bad.append(f"{'FN' if t['tight'] else 'FP'} {t['sym']} {t['fill'][5:]}")
    print(80 - len(bad), c, bad)
