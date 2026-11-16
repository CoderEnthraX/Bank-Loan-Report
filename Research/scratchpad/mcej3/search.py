"""Best monthly settings, money search: every IST calendar month on its own, a fresh $1,000 account and a fresh money state on the 1st, the
trades that START in the month (mcej3/sets.pkl). Money = gold/recovery.py (proven equal to the EA and both strategies).
  base risk   $5 / $10 / $20 (fixed $)
  rule        No recovery, Crooks C / E / F / G / H / I / J, Crooks C forget after 2 / 50 % + forget 2, Exact recovery, Recover all, Martingale x2,
              Labouchere, D'Alembert, Fibonacci, Oscar's Grind, Rule C split 1, and Crooks F - J with the profit ladder (Medium / Max, target $50 / $100)
  hard cap    none, $50 / $100 Clamp, $50 / $100 Start again
  month lock  (Auction Retest only; the strategy / EA "Stop for the month once it is up $X") none, $20, $30, $50, $100, $150: the trades after the
              one that brings the month's closed profit to the lock are not taken
ARS: one $1,000 account per month. GRID: each strategy its own account (as the grid indicator / EA), $1,000 / k each for k strategies on
(k = 1..12), summed afterwards by select.py.
Output: mcej3/money_ars.npz + money_grid.npz (+ the run list in money_meta.pkl)"""
import sys, pickle, itertools, multiprocessing as mp
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC

START = 1000.0
BASES = (5.0, 10.0, 20.0)
RULES = [('No recovery', 'Off', {}), ('Crooks C', 'Crooks C', {}), ('Crooks E', 'Crooks E', {}), ('Crooks F', 'Crooks F', {}), ('Crooks G', 'Crooks G', {}),
         ('Crooks H', 'Crooks H', {}), ('Crooks I', 'Crooks I', {}), ('Crooks J', 'Crooks J', {}),
         ('Crooks C forget after 2', 'Crooks C', dict(crkPr='forget', crkPrN=2)), ('Crooks C 50% forget after 2', 'Crooks C', dict(crkPr='pct', crkPrN=2, crkPrPct=50.0)),
         ('Exact recovery at final TP', 'Exact recovery at final TP', {}), ('Recover all on the next trade', 'Recover all losses on the next trade', {}),
         ('Martingale x2', 'Martingale (multiply after each loss)', dict(mult=2.0)), ('Labouchere', 'Labouchere', {}), ("D'Alembert", "D'Alembert", {}),
         ('Fibonacci', 'Fibonacci', {}), ("Oscar's Grind", "Oscar's Grind", {}), ('Rule C split 1', 'Rule C: carry the losses', dict(cSplit=1))]
RULES += [('%s, ladder %s, target $%d' % (r, lv, T), r, dict(lad=lv, ladT=float(T))) for r in ('Crooks F', 'Crooks G', 'Crooks H', 'Crooks I', 'Crooks J')
          for lv in ('Medium', 'Max') for T in (50, 100)]
CAPS = [('no cap', 0.0, 'clamp'), ('cap $50 Clamp', 50.0, 'clamp'), ('cap $100 Clamp', 100.0, 'clamp'), ('cap $50 Start again', 50.0, 'reset'),
        ('cap $100 Start again', 100.0, 'reset')]
LOCKS = (None, 20.0, 30.0, 50.0, 100.0, 150.0)
RUNS = [(b, ri, ci) for b in BASES for ri, rr in enumerate(RULES) for ci, cc in enumerate(CAPS) if not (rr[1] == 'Off' and ci > 0)]


def months():
    out = []; y, m = 2021, 1
    while (y, m) <= (2026, 10):
        out.append('%04d-%02d' % (y, m)); m += 1
        if m == 13: y, m = y + 1, 1
    return out


MONTHS = months(); MI = {m: i for i, m in enumerate(MONTHS)}


def by_month(trs):
    per = [[] for _ in MONTHS]
    for x in trs:
        k = MI.get('%04d-%02d' % (x['t'].year, x['t'].month))
        if k is not None: per[k].append((x['R'], x['c'], None, None, x['levk'], x['rmin']))
    return per


def month_run(tup, mode, kw, base, start, cap, act, exitR, locks):
    """one month: per lock (net, deepest drop from the month's high, blown, trades taken)"""
    if not tup: return [(0.0, 0.0, False, 0)] * len(locks)
    tr = []; r = RC.simulate(tup, mode, base=base, start=start, cap=cap, capAction=act, exitR=exitR, trace=tr, **kw)
    pn = [v * (t[0] - t[1]) / (1.0 + t[1]) for v, t in zip(tr, tup)]
    out = []
    for lk in locks:
        eq = 0.0; pk = 0.0; dd = 0.0; n = 0; blown = False
        for p in pn:
            if lk is not None and eq >= lk: break
            eq += p; n += 1; pk = max(pk, eq); dd = max(dd, pk - eq)
            if start + eq <= 0: blown = True; break
        out.append((eq, dd, blown, n))
    return out


def ars_job(args):
    i, s = args
    per = by_month(s['trades']); nR = len(RUNS); nL = len(LOCKS); nM = len(MONTHS)
    net = np.zeros((nR, nL, nM), np.float32); dd = np.zeros((nR, nL, nM), np.float32); bl = np.zeros((nR, nL, nM), bool); nt = np.zeros((nR, nL, nM), np.int16)
    for j, (b, ri, ci) in enumerate(RUNS):
        _, mode, kw = RULES[ri]; _, cap, act = CAPS[ci]
        for m, tup in enumerate(per):
            for li, (a, d_, bb, n) in enumerate(month_run(tup, mode, kw, b, START, cap, act, s['exitR'], LOCKS)):
                net[j, li, m] = a; dd[j, li, m] = d_; bl[j, li, m] = bb; nt[j, li, m] = n
    return i, net, dd, bl, nt


def grid_job(args):
    g, k, s = args
    per = by_month(s['trades']); nR = len(RUNS); nM = len(MONTHS); st = START / k
    net = np.zeros((nR, nM), np.float32); bl = np.zeros((nR, nM), bool); nt = np.zeros((nR, nM), np.int16)
    for j, (b, ri, ci) in enumerate(RUNS):
        _, mode, kw = RULES[ri]; _, cap, act = CAPS[ci]
        for m, tup in enumerate(per):
            a, d_, bb, n = month_run(tup, mode, kw, b, st, cap, act, s['exitR'], (None,))[0]
            net[j, m] = a; bl[j, m] = bb; nt[j, m] = n
    return g, k, net, bl, nt


if __name__ == '__main__':
    D = pickle.load(open(S + '/mcej3/sets.pkl', 'rb')); A = D['ars']; G = D['grid']
    pickle.dump(dict(months=MONTHS, runs=RUNS, rules=[r[0] for r in RULES], caps=[c[0] for c in CAPS], locks=LOCKS, bases=BASES,
                     ars=[{k: v for k, v in s.items() if k != 'trades'} for s in A], grid=[{k: v for k, v in s.items() if k != 'trades'} for s in G]),
                open(S + '/mcej3/money_meta.pkl', 'wb'))
    print('runs per set', len(RUNS), '| ARS sets', len(A), '| grid strategies', len(G), flush=True)
    jobs = sorted(enumerate(A), key=lambda js: -len(js[1]['trades']))
    nR, nL, nM = len(RUNS), len(LOCKS), len(MONTHS)
    NET = np.zeros((len(A), nR, nL, nM), np.float32); DD = np.zeros_like(NET); BL = np.zeros(NET.shape, bool); NT = np.zeros(NET.shape, np.int16)
    with mp.Pool(4) as pool:
        for i, net, dd, bl, nt in pool.imap_unordered(ars_job, jobs):
            NET[i], DD[i], BL[i], NT[i] = net, dd, bl, nt; print('ARS', A[i]['key'], flush=True)
    np.savez_compressed(S + '/mcej3/money_ars.npz', net=NET, dd=DD, blown=BL, n=NT)
    GN = np.zeros((len(G), 12, nR, nM), np.float32); GB = np.zeros(GN.shape, bool); GT = np.zeros(GN.shape, np.int16)
    gj = [(g, k, G[g]) for g in range(len(G)) for k in range(1, 13)]
    with mp.Pool(4) as pool:
        for g, k, net, bl, nt in pool.imap_unordered(grid_job, gj, chunksize=2):
            GN[g, k - 1], GB[g, k - 1], GT[g, k - 1] = net, bl, nt
    np.savez_compressed(S + '/mcej3/money_grid.npz', net=GN, blown=GB, n=GT)
    print('saved', flush=True)
