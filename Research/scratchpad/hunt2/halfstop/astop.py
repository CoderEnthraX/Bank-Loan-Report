"""A-set stop check: for each of the 80 screenshot trades matched (same dir, fill +-2), stop error in ATR; prints mismatches > 0.12 ATR.
Usage: python3 -I astop.py module.py '{opts}'"""
import sys, io, contextlib, json, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit')
with contextlib.redirect_stdout(io.StringIO()):
    import tightdata
from engine2 import prepare
from engine import rma
modp = sys.argv[1]; inp = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
spec = importlib.util.spec_from_file_location('mm', modp); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
cache = {}; bad = 0; n = 0; tt = 0
for t in tightdata.TRADES:
    s = t['sym']
    if s not in cache: cache[s] = M.run(s, inp)
    P = prepare(s); A = rma(P['tr'], 14)
    c = [m for m in cache[s] if m['dir'] == t['d'] and abs(m['fill'] - t['fill_i']) <= 2]
    if not c: continue
    m = min(c, key=lambda m: abs(m['fill'] - t['fill_i'])); n += 1
    err = (m['stop'] - t['stop']) / A[m['arm']]
    mt = abs(m['entry'] - m['stop']) / A[m['arm']] < 1.4
    tt += mt
    if abs(err) > 0.12 or mt != t['tight']:
        bad += 1; print(f"  A STOP {s} {t['fill']} {'L' if t['d']>0 else 'S'} model {m['stop']:.6g} gt {t['stop']} err {err:+.2f} ATR model_tight {mt} gt_tight {t['tight']}")
print(f'A stops: matched {n}, wrong {bad}, model tight {tt}')
