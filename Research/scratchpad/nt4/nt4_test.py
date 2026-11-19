"""nt4 (asked 2026-11-19): the nt3 test on M5 and M15, each month starting at $1,000 / $2,000 / $10,000; Risk and Profit.
Run: python3 -I nt4/nt4_test.py TF  (M5 | M15) -> nt4/results_TF.pkl
Recover losses over N trades (N = 3), final exit TP1 = 0.2R, $20 base, every calendar month on its own (fresh $1,000 on the 1st), gold
2021-01 .. 2026-09 (asked 2026-11-19). The user's EA settings: Tue-Thu, new trades 06:00-23:00 IST, kill zones Asia / London / New York (New
York / London time), daily news 17:45 IST 30 min + 30 min before (New York time), force-close 23:55 IST, weekend close, 1:100, 0.01-lot steps
(rounded down, at least 0.01), costs 0.23 per oz (spread 0.16 + $7 a lot), earn-back target. Signals: the engine on M5 (FxPro gold).
EXITS ON M1 like the EA's broker orders: the stop and the take profit go with the order, so from the fill minute on they are checked on the
1-minute candles (fill minute: only the stop; a minute touching both: the stop); news / 23:55 / Saturday closes at the bar open.
Money: the EA's Recover losses over N trades: risk = base + pool / N; Size By Profit (as v5.1): (base + pool / N) / (TP x stop / (stop + costs)),
so a TP1 win is exactly that amount before the lot rounding; a loss adds to the pool, a win takes its profit off it. Baselines: fixed base (no recovery). Output: nt3/results.pkl"""
import sys, math, pickle, bisect, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/conf'); sys.path.insert(0, S + '/bese')
import confirm as Q
from ref_gbe import ny_summer
COST = 0.23; LEV = 100.0; TP = 0.2; BASE = 20.0; N = 3; STARTS = (1000.0, 2000.0, 10000.0)
TF = sys.argv[1] if len(sys.argv) > 1 else 'M5'; BARMIN = {'M5': 5, 'M15': 15}[TF]
DAYS = (False, True, True, True, False, False, False); PRE = 30


def mins(t): return t.hour * 60 + t.minute
def nshift(t): return 0 if ny_summer(t - dt.timedelta(minutes=330)) else 60
def block(t):
    s0 = (17 * 60 + 45 + nshift(t)) % 1440; cur = mins(t); diff = (s0 - cur) % 1440
    return (s0 <= cur < s0 + 30) or (0 < diff <= PRE)
def flat(t, u):
    s0 = (17 * 60 + 45 + nshift(t)) % 1440
    nS = (s0 <= mins(t) < s0 + 30) and not (s0 <= mins(u) < s0 + 30)
    fc = (mins(u) < 1435 <= mins(t)) or (t.date() != u.date() and mins(u) < 1435)
    return nS or fc or (t.weekday() == 5 and u.weekday() != 5)


def trades():
    cfg = dict(Q.USER_ENG, exitAt=1, tp1R=TP, **dict(Q.USER_ON, days=DAYS))
    P, p, tr = Q.engine(dict(key='user', tf=TF, cfg=cfg))
    T = P['T']
    m1 = pickle.load(open(S + '/gold/data/M1.pkl', 'rb'))
    T1 = [u + dt.timedelta(hours=5, minutes=30) for u in m1['utc']]
    O1, H1, L1 = m1['O'], m1['H'], m1['L']; n1 = len(T1)
    out = []; busyT = None; sk = dict(busy=0, news=0, cancel=0, nodata=0)
    for x in tr:
        a, f, d, E, stp = x['arm'], x['fill'], x['dir'], x['entry'], x['stop']; risk = d * (E - stp)
        tOrd = T[a + 1]                                              # the EA places the order at the open of the bar after the arm bar
        if busyT is not None and busyT > tOrd: sk['busy'] += 1; continue   # still in the previous position
        if block(tOrd): sk['news'] += 1; continue
        if any(block(T[j]) or flat(T[j], T[j - 1]) for j in range(a + 1, f + 1)): sk['cancel'] += 1; continue
        tgt = E + d * (TP * risk + COST); tol = 0.00001
        j0 = bisect.bisect_left(T1, T[f]); j1 = bisect.bisect_left(T1, T[f] + dt.timedelta(minutes=BARMIN))
        jf = next((j for j in range(j0, j1) if (L1[j] <= E + tol if d == 1 else H1[j] >= E - tol)), None)
        if jf is None: sk['nodata'] += 1; continue
        ex = None
        if (L1[jf] <= stp + tol if d == 1 else H1[jf] >= stp - tol): ex = (jf, -1.0, 'stop')
        k = jf + 1
        while ex is None and k < n1:
            if flat(T1[k], T1[k - 1]): ex = (k, (d * (O1[k] - E) - COST) / (risk + COST), 'news / 23:55 / weekend')
            elif (L1[k] <= stp + tol if d == 1 else H1[k] >= stp - tol): ex = (k, -1.0, 'stop')
            elif (H1[k] >= tgt - tol if d == 1 else L1[k] <= tgt + tol): ex = (k, TP * risk / (risk + COST), 'TP1')
            k += 1
        if ex is None: break
        ke, net, kind = ex
        out.append(dict(t=T1[jf], tx=T1[ke], dir=d, entry=E, stop=stp, dist=risk, px=E, net=net, kind=kind))
        busyT = T1[ke]
    return out, sk


def month_run(trs, rule, size_by, START):
    """one month, fresh account: rule 'split' (over N trades) or 'fixed'; size_by 'risk' / 'profit'. -> per-trade rows and the month's stats"""
    eq = START; peak = START; mdd = 0.0; pool = 0.0; rows = []; blown = False; lrun = 0; mlrun = 0
    for x in trs:
        rmin = x['dist'] + COST                                     # $ stop-out loss of 0.01 lot (1 oz)
        ulev = math.floor(eq * LEV / (x['px'] * 100) / 0.01 + 1e-9)  # 1:100: lots <= equity x 100 / (price x 100 oz)
        if ulev < 1: blown = True; break
        # Size By Profit (v5.1): the amount is the WIN at TP1, costs included: a TP1 win per $ of stop-out loss = TP x stop / (stop + costs)
        dv = TP * x['dist'] / (x['dist'] + COST) if size_by == 'profit' else 1.0
        r = (BASE + (pool / N if rule == 'split' else 0.0)) / dv
        u = math.floor(r / rmin + 1e-9)
        u = max(1, u); u = min(u, ulev)                              # at least 0.01 lot (the EA's "trade the minimum"); the leverage limit
        risk = u * rmin; pnl = risk * x['net']
        eq += pnl; peak = max(peak, eq); mdd = max(mdd, peak - eq)
        if pnl > 0: pool = max(0.0, pool - pnl); lrun = 0
        else: pool += -pnl; lrun += 1; mlrun = max(mlrun, lrun)
        rows.append(dict(x, plan=r, lots=u / 100.0, risk=risk, pnl=pnl, bal=eq, pool=pool))
    wins = sum(1 for r_ in rows if r_['pnl'] > 0)
    return rows, dict(n=len(rows), wins=wins, losses=len(rows) - wins, net=eq - START, end=eq, mdd=mdd, mddp=mdd / peak if peak else 0.0,
                      maxRisk=max([r_['risk'] for r_ in rows] or [0.0]), maxLots=max([r_['lots'] for r_ in rows] or [0.0]),
                      worst=min([r_['pnl'] for r_ in rows] or [0.0]), best=max([r_['pnl'] for r_ in rows] or [0.0]), lrun=mlrun, blown=blown,
                      minBal=min([START] + [r_['bal'] for r_ in rows]), poolEnd=pool)


if __name__ == '__main__':
    trs, sk = trades()
    print(len(trs), 'trades', sk, 'TP1 %d stop %d closed by news / 23:55 / weekend %d' % (
        sum(x['kind'] == 'TP1' for x in trs), sum(x['kind'] == 'stop' for x in trs), sum(x['kind'].startswith('news') for x in trs)))
    months = [(y, m) for y in range(2021, 2027) for m in range(1, 13) if (y, m) <= (2026, 9)]
    by = {k: [x for x in trs if (x['t'].year, x['t'].month) == k] for k in months}
    res = {}
    for st in STARTS:
        for rule in ('split', 'fixed'):
            for sb in ('risk', 'profit'):
                res[(st, rule, sb)] = {k: month_run(by[k], rule, sb, st) for k in months}
    pickle.dump(dict(tf=TF, trades=trs, skipped=sk, months=months, res=res), open(S + '/nt4/results_%s.pkl' % TF, 'wb'))
    for (st, rule, sb), R in res.items():
        nets = [R[k][1]['net'] for k in months]
        print('%s $%-6d %-6s %-6s total %+9.2f | profitable months %2d / %d | best %+8.2f worst %+8.2f | blown months %d' % (
            TF, st, rule, sb, sum(nets), sum(v > 0 for v in nets), len(nets), max(nets), min(nets), sum(R[k][1]['blown'] for k in months)))
