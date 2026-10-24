"""Fraction of tight trades in the full engine (all data and inside GT windows) for each rule module."""
import sys, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare, run
from rec import BEST
from tightdata import TRADES
for path in sys.argv[1:]:
    spec = importlib.util.spec_from_file_location('rule', path); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    cfg = dict(BEST); cfg['stopFn'] = mod.stop_fn; n = nt = 0; nw = ntw = 0
    ok = 0; tot = 0
    for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
        P = prepare(s); A = P[('atr', 14)]
        for x in run(P, cfg):
            tg = x['dir'] * (x['entry'] - x['stop']) / A[x['arm']] < 1.4
            n += 1; nt += tg
            if '2026-10-05' <= P['T'][x['fill']] < '2026-10-13': nw += 1; ntw += tg
        byf = {(x['fill'], x['dir']): x for x in run(P, cfg)}
        for t in [t for t in TRADES if t['sym'] == s]:
            x = byf.get((t['fill_i'], t['d']))
            if x: tot += 1; ok += ((x['dir'] * (x['entry'] - x['stop']) / A[x['arm']] < 1.4) == t['tight'])
    print(f"{path.split('/')[-1]:14s} all-data tight {nt}/{n} = {nt/n:.1%}; 10-05..10-12 {ntw}/{nw}; in-engine GT stop class {ok}/{tot}")
