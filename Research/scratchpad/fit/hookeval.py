"""Score a rule module against the 80 original trades.
Usage: python3 -I hookeval.py path/to/rule.py ['{"extra":"cfg"}'] [d]
The module may define:
  stop_fn(P, i, d, entry, stop, A, ctx) -> new stop price   (i = displacement bar index, d = +1 long / -1 short,
        stop = default entry - d*1.8*A, A = ATR14(RMA) at i, ctx = engine state: trades so far, dayFills, dayLoss, dayR,
        streak, lastExit, lastRes, st, armBar, lim)
  arm_fn(P, i, d, ctx) -> bool  (False = do not arm this displacement)
P has O,H,L,C,V (VWAP),T (IST 'YYYY-MM-DD HH:MM'),tr, daystart, sinceStart, sym, mt, ('atr',14), dowutc.
Prints the FULL-ENGINE score (exact/miss/extra vs the 80 original trades; current best 71/9/9) and, for stop_fn,
the classification of the 80 original stops (tight = 8 trades at ~0.9 ATR)."""
import sys, os, json, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt, score
from engine2 import prepare
from engine import rma
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
spec = importlib.util.spec_from_file_location('rule', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
cfg = dict(BEST)
if len(sys.argv) > 2 and sys.argv[2].strip().startswith('{'): cfg.update(json.loads(sys.argv[2]))
if hasattr(mod, 'stop_fn'): cfg['stopFn'] = mod.stop_fn
if hasattr(mod, 'arm_fn'): cfg['armFn'] = mod.arm_fn
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
r, rows = score(cfg, tr, [dict(w) for w in win], detail=True)
print('FULL ENGINE', {k: r[k] for k in ('exact', 'miss', 'extra')}, '(baseline 71/9/9; oracle-stops 74/6/6)')
if 'd' in sys.argv[2:]:
    [print('  ', *x) for x in rows if x[0] != 'ok']
if hasattr(mod, 'stop_fn'):
    from tightdata import TRADES
    ok = 0; bad = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr', 14)][i]
        ctx = dict(trades=[], dayFills=0, dayLoss=0, dayR=0.0, streak=0, lastExit=None, lastRes=0.0, st=0, armBar=None, lim=None)
        s = mod.stop_fn(P, i, t['d'], t['entry'], t['entry'] - t['d'] * 1.8 * A, A, ctx)
        predT = t['d'] * (t['entry'] - s) / A < 1.4
        if predT == t['tight']: ok += 1
        else: bad.append(f"{t['sym']} {t['fill']} {'TIGHT' if t['tight'] else 'normal'}")
    print(f'STOP CLASSIFICATION (ctx is empty here, so sequence rules show only in FULL ENGINE): {ok}/{len(TRADES)} wrong: {bad}')
