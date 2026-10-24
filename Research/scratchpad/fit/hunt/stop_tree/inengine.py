"""In-engine stop check for a rule module: run the full engine (best cfg + stop_fn), and for every engine trade that matches an
original trade exactly (same symbol/dir/fill bar) compare tight vs normal; also the tight share of all engine trades.
Usage: inengine.py rule.py"""
import sys, os, importlib.util
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare, run
from tightdata import TRADES
BEST = {"brkLen": 10, "entryLen": 6, "bodyPct": 55, "closePct": 25, "maxDayR": 3, "vsLag": 3, "noSunUTC": 1, "momMin": 0.85,
        "roundLevels": False, "rearm": "samedir", "minBars": 1}
spec = importlib.util.spec_from_file_location('rule', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
cfg = dict(BEST); cfg['stopFn'] = mod.stop_fn
ok = 0; bad = []; nm = 0; ntight = ntot = 0; nt_oct = nn_oct = 0
for sym in sorted({t['sym'] for t in TRADES}):
    P = prepare(sym); E = run(P, cfg); A = P[('atr', 14)]
    by = {(m['fill'], m['dir']): m for m in E}
    for m in E:
        r = m['dir'] * (m['entry'] - m['stop']) / A[m['arm']]
        ntot += 1; ntight += r < 1.4
        if P['T'][m['fill']] >= '2026-10-05': nn_oct += 1; nt_oct += r < 1.4
    for t in [t for t in TRADES if t['sym'] == sym]:
        m = by.get((t['fill_i'], t['d']))
        if m is None: continue
        nm += 1; r = m['dir'] * (m['entry'] - m['stop']) / A[m['arm']]
        if (r < 1.4) == t['tight']: ok += 1
        else: bad.append(f"{sym} {t['fill']} {'TIGHT' if t['tight'] else 'normal'} (engine {r:.2f})")
print(f'in-engine stop class on exact-matched trades: {ok}/{nm} wrong: {bad}')
print(f'tight share of engine trades: all {ntight}/{ntot} = {ntight / ntot:.1%}; from 10-05: {nt_oct}/{nn_oct} = {nt_oct / max(nn_oct, 1):.1%}')
