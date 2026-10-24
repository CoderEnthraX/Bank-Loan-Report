"""A-stop check on r3.py (copy of hunt8/astops8.py)."""
import sys, json, io, contextlib
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fit'); sys.path.insert(0, S + '/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tightdata
import r3 as M
from engine2 import prepare
from engine import rma
inp = json.loads(sys.argv[1] if len(sys.argv) > 1 else '{}')
cache = {}; bad = ok = 0
for t in tightdata.TRADES:
    sym = t['sym']
    if sym not in cache: P = prepare(sym); cache[sym] = (P, {(z['fill'], z['dir']): z for z in M.shown(sym, inp)}, rma(P['tr'], 14))
    P, tr, A = cache[sym]; m = tr.get((t['fill_i'], t['d']))
    if not m: print('NOMATCH', sym, t['fill']); continue
    a = A[m['arm']]; err = (m['stop'] - t['stop']) / a
    if abs(err) > 0.12: bad += 1; print(f"BADSTOP {sym} {t['fill']} {'L' if t['d']>0 else 'S'} gt {t['stopR']:.2f}ATR model {m['dir']*(m['entry']-m['stop'])/a:.2f}ATR {'TIGHT' if m['half'] else 'norm'} err {err:+.2f}")
    else: ok += 1
print('A stops ok', ok, 'bad', bad)
