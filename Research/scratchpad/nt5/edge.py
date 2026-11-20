"""Edge search (asked 2026-11-20): the user's EA rules (nt4_test.trades: the engine + M1 exits, news / force-close / weekend, costs 0.23,
earn-back) with any timeframe, final TP (R) and filters. trades_for(tf, tp, on, eng) -> list of trades (t = fill IST, net = R incl. costs)."""
import sys, importlib
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/nt4'); sys.argv = sys.argv[:1]
import nt4_test as N
Q = N.Q


def trades_for(tf, tp, on=None, eng=None):
    N.TF = tf; N.BARMIN = {'M1': 1, 'M5': 5, 'M15': 15, 'H1': 60, 'H4': 240, 'D1': 1440}[tf]; N.TP = tp
    on0, eng0 = Q.USER_ON, Q.USER_ENG
    if on is not None: Q.USER_ON = on
    if eng is not None: Q.USER_ENG = eng
    try:
        tr, sk = N.trades()
    finally:
        Q.USER_ON, Q.USER_ENG = on0, eng0
    return tr


def stats(tr, year=None):
    xs = [x['net'] for x in tr if year is None or x['t'].year == year]
    if not xs: return dict(n=0, wr=0.0, exp=0.0, sumR=0.0)
    return dict(n=len(xs), wr=sum(v > 0 for v in xs) / len(xs), exp=sum(xs) / len(xs), sumR=sum(xs))
