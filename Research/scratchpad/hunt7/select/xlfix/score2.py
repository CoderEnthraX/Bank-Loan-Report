"""Score a model against BOTH ground truths, separately:
  A = the 80 screenshot trades (gt/final, windows -> misses AND extras inside windows),
  B = the student's Excel log for SENSEX + CRUDE (trades only, the log is NOT complete -> only misses and wrong stops count).
Usage:  python3 -I score2.py [module.py] ['{"opt": value}'] [d]
  module.py must define run(sym, inp) -> list of trades dict(dir, arm, fill, entry, stop, exit, res) with bar indices
  (default: fit/pine_final.py, the current model = the published Pine strategy/indicator logic).
Excel times are the FILL bar; a model trade within +-1 bar with the same direction counts as a time match.
Stop match = |model stop - logged stop| <= 0.06 ATR (the log is rounded to whole points)."""
import sys, os, json, importlib.util, datetime as dt
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, F); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load_xl import load
from engine2 import prepare
from engine import rma
import gtscore
args = [a for a in sys.argv[1:]]
modp = next((a for a in args if a.endswith('.py')), os.path.join(F, 'pine_final.py'))
inp = next((json.loads(a) for a in args if a.startswith('{')), {})
det = 'd' in args
spec = importlib.util.spec_from_file_location('m', modp); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
# A: screenshot GT through gtscore with the module's run
def _r(P, cfg):
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    return M.run(P['sym'], inp)
gtscore.run = _r
tr, win = gtscore.load_gt(os.path.join(F, '..', 'gt', 'final'))
tr = [t for t in tr if not str(t.get('conf') or '').startswith('xl')]
ra, rowsA = gtscore.score({}, tr, [dict(w) for w in win], detail=True)
print('A screenshots (80):', {k: ra[k] for k in ('exact', 'near', 'miss', 'extra')})
if det: [print('   A', *x) for x in rowsA if x[0] != 'ok']
# B: Excel log
X = [x for x in load() if x['sym'] in ('SENSEX', 'CRUDE')]
SKIP = {66}   # #66: same prices as the 09:40 short, logged with a wrong time -> compare at 09:40
fixT = {66: '09:40'}
tm = st_ok = 0; rows = []
for sym in ('SENSEX', 'CRUDE'):
    P = prepare(sym); T = P['T']; A = rma(P['tr'], 14); idx = {t: i for i, t in enumerate(T)}
    trades = M.run(sym, inp)
    for x in [x for x in X if x['sym'] == sym]:
        f = idx.get(x['date'] + ' ' + fixT.get(x['n'], x['tin']))
        best = None
        for m in trades:
            if m['dir'] == x['d'] and f is not None and abs(m['fill'] - f) <= 1:
                if best is None or abs(m['fill'] - f) < abs(best['fill'] - f): best = m
        if best is None:
            rows.append(('MISS', sym, x['n'], x['date'], x['tin'], 'L' if x['d'] > 0 else 'S')); continue
        tm += 1
        a = A[best['arm']] or 1
        ok = abs(best['stop'] - x['stop']) <= 0.06 * a + 1.0
        st_ok += ok
        if not ok: rows.append(('STOP', sym, x['n'], x['date'], x['tin'], f"model {best['stop']:.6g} vs log {x['stop']} ({(best['stop']-x['stop'])/a:+.2f} ATR)"))
print(f'B student log SENSEX+CRUDE ({len(X)}): time-matched {tm}, missed {len(X) - tm}, stop correct {st_ok}/{tm}')
if det: [print('   B', *r) for r in rows]
