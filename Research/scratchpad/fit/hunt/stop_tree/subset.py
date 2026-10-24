"""First-of-session subset of the 80 trades (sibling rule_firstday_prevday _event logic)."""
import sys, os, importlib.util
FIT = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from engine2 import prepare
from engine import rma
from tightdata import TRADES
spec = importlib.util.spec_from_file_location('rfp', FIT + '/hunt/stop_sequence/rule_firstday_prevday.py'); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
def first_flag(P, i, d, merge=True, extra=('vsl',)):
    R.MERGE = merge; R.EVENT_EXTRA = extra
    out, idx = R._daily(P); a = out[idx[i]][0]
    return not any(R._event(P, j, d) for j in range(a, i))
def subset(merge=True, extra=('vsl',)):
    S = []
    for t in TRADES:
        P = prepare(t['sym'])
        if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
        if first_flag(P, t['arm_i'], t['d'], merge, extra): S.append(t)
    return S
if __name__ == '__main__':
    for m in (True, False):
        S = subset(m)
        print('MERGE', m, len(S), 'trades', sum(t['tight'] for t in S), 'tight')
        for t in S: print('  ', t['sym'], t['fill'], t['arm'], t['d'], 'TIGHT' if t['tight'] else '')
