"""Within the sibling's positive set (first-of-session & prev-session against), which of my features separate 8T from FPs?"""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from alib import *
import importlib.util
spec = importlib.util.spec_from_file_location('fdp', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence/rule_firstday_prevday.py'); fdp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fdp)
from tightdata import TRADES
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/tfeat.pkl', 'rb'))
for r, t in zip(rows, TRADES):
    P = get(t['sym']); r['pos'] = fdp.is_tight(P, t['arm_i'], t['d'])
fdp.PD_TH = 0.0
for r, t in zip(rows, TRADES):
    P = get(t['sym']); r['pos0'] = fdp.is_tight(P, t['arm_i'], t['d'])
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/tfeat.pkl', 'wb'))
for flag in ('pos', 'pos0'):
    S = [r for r in rows if r[flag]]
    print(flag, 'n', len(S), 'tight', sum(r['tight'] for r in S), 'FP', [f"{r['sym']} {r['fill'][5:]}" for r in S if not r['tight']])
    keys = [k for k in rows[0] if k not in ('sym', 'fill', 'd', 'tight', 'pos', 'pos0')]
    out = []
    for k in keys:
        T_ = [r[k] for r in S if r['tight'] and r.get(k) is not None]; N_ = [r[k] for r in S if not r['tight'] and r.get(k) is not None]
        if len(T_) < 8 or not N_: continue
        lo, hi = min(T_), max(T_)
        nin = sum(1 for v in N_ if lo <= v <= hi)
        # margin: distance of nearest FP outside
        out.append((nin, k, lo, hi, sorted(N_)))
    out.sort(key=lambda x: x[0])
    for nin, k, lo, hi, N_ in out[:25]:
        print(f"  {k:12s} FP inside {nin}  tight [{lo:.2f},{hi:.2f}]  FP vals {[round(v,2) for v in N_]}")
