"""Best monthly settings, robust choice: the 400 best candidates of each family on the choice period (choose.py ranking 'fewest losing months,
then profit') are run again in two stress versions:
  mid    windows from the 15th to the 14th instead of calendar months (a fresh $1,000 on every 15th)
  cost   calendar months with costs 0.30 per oz instead of 0.23 (+0.07, e.g. a wider spread; the trades themselves unchanged)
Robust pick (choice period only): the fewest losing windows in the WORST of the three versions (calendar, mid, cost), then the most calendar
profit, then the smallest deepest drop inside a month. Its test-period results (2024-26) are reported, never used to choose.
Output: mcej3/robust.pkl + robust.txt"""
import sys, pickle, datetime as dt
import numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/mcej3'); sys.path.insert(0, S + '/gold')
import search as SE, choose as CH
D = pickle.load(open(S + '/mcej3/sets.pkl', 'rb')); MT = CH.M
COST2 = 0.30


def windows(kind):
    """(start, end, period) per window; period 'IN' (choice) / 'OUT' (test) / None (spans both)"""
    out = []; y, m = 2021, 1
    while (y, m) <= (2026, 10):
        a = dt.datetime(y, m, 1 if kind == 'cal' else 15); ny, nm = (y, m + 1) if m < 12 else (y + 1, 1)
        b = dt.datetime(ny, nm, 1 if kind == 'cal' else 15)
        per = 'IN' if b <= dt.datetime(2024, 1, 1) else 'OUT' if a >= dt.datetime(2024, 1, 1) else None
        if not (kind == 'mid' and (y, m) == (2026, 10)): out.append((a, b, per))
        y, m = ny, nm
    return out


WIN = {k: windows(k) for k in ('cal', 'mid')}


def split(trs, kind, cost):
    W = WIN[kind]; per = [[] for _ in W]; k = 0
    for x in trs:
        while k < len(W) and x['t'] >= W[k][1]: k += 1
        if k >= len(W): break
        if x['t'] >= W[k][0]:
            c = x['c'] if cost is None else cost / x['sd']
            rm = x['rmin'] if cost is None else x['sd'] + cost
            lv = x['levk'] if cost is None else x['levk'] * (x['sd'] + cost) / (x['sd'] + 0.23)
            per[k].append((x['R'], c, None, None, lv, rm))
    return per


def run_ars(s, run, lock, kind, cost):
    b, ri, ci = SE.RUNS[run]; _, mode, kw = SE.RULES[ri]; _, cap, act = SE.CAPS[ci]
    res = []
    for tup in split(s['trades'], kind, cost):
        net, dd, bl, n = SE.month_run(tup, mode, kw, b, SE.START, cap, act, s['exitR'], (SE.LOCKS[lock],))[0]
        res.append((net, dd, bl, n))
    return res


def split_x(trs, kind, cost):
    """like split, with each trade's exit time (to merge several strategies' trades into one balance path)"""
    W = WIN[kind]; per = [[] for _ in W]; k = 0
    for x in trs:
        while k < len(W) and x['t'] >= W[k][1]: k += 1
        if k >= len(W): break
        if x['t'] >= W[k][0]:
            c = x['c'] if cost is None else cost / x['sd']
            rm = x['rmin'] if cost is None else x['sd'] + cost
            lv = x['levk'] if cost is None else x['levk'] * (x['sd'] + cost) / (x['sd'] + 0.23)
            per[k].append(((x['R'], c, None, None, lv, rm), x['tx']))
    return per


def run_grid(subset, run, kind, cost):
    """every strategy its own account ($1,000 / k); the window's net = the sum; the deepest drop = on the summed balance, trades merged by exit"""
    import recovery as RC
    b, ri, ci = SE.RUNS[run]; _, mode, kw = SE.RULES[ri]; _, cap, act = SE.CAPS[ci]; k = len(subset); st = SE.START / k
    W = WIN[kind]; ev = [[] for _ in W]; bl = [False] * len(W); nt = [0] * len(W)
    for g in subset:
        s = D['grid'][g]
        for w, items in enumerate(split_x(s['trades'], kind, cost)):
            if not items: continue
            tup = [a for a, _ in items]; tr = []
            r = RC.simulate(tup, mode, base=b, start=st, cap=cap, capAction=act, exitR=s['exitR'], trace=tr, **kw)
            eq = 0.0
            for v, (t_, tx) in zip(tr, items):
                p = v * (t_[0] - t_[1]) / (1.0 + t_[1]); eq += p; ev[w].append((tx, p)); nt[w] += 1
                if st + eq <= 0: bl[w] = True
    out = []
    for w in range(len(W)):
        eq = pk = dd = 0.0
        for _, p in sorted(ev[w], key=lambda z: z[0]):
            eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
        out.append((eq, dd, bl[w], nt[w]))
    return out


def stats(res, kind, period):
    W = WIN[kind]; v = [r for r, w in zip(res, W) if w[2] == period]
    nets = [r[0] for r in v]
    return dict(lose=sum(1 for x in nets if x < -1e-9), prof=sum(1 for x in nets if x > 1e-9), total=sum(nets), worst=min(nets), n=len(nets),
                blown=sum(1 for r in v if r[2]), dd=max(r[1] for r in v), active=sum(1 for r in v if r[3] > 0))


def evaluate(c):
    out = {}
    for sc, kind, cost in (('cal', 'cal', None), ('mid', 'mid', None), ('cost', 'cal', COST2)):
        res = run_ars(D['ars'][c['set']], c['run'], c['lock'], kind, cost) if c['fam'] == 'ARS' else run_grid(c['subset'], c['run'], kind, cost)
        out[sc] = dict(IN=stats(res, kind, 'IN'), OUT=stats(res, kind, 'OUT'), monthly=[r[0] for r in res] if sc == 'cal' else None)
    c = dict(c); c['sc'] = out
    c['robust'] = (max(out[s]['IN']['lose'] + out[s]['IN']['blown'] for s in out), -out['cal']['IN']['total'], out['cal']['IN']['dd'])
    return c


if __name__ == '__main__':
    import multiprocessing as mp
    A, _ = CH.ars(); G = CH.grid()
    pools = {'ARS': CH.rank(A, 'steady')[:400], 'GRID': CH.rank(G, 'steady')[:400]}
    res = {}; L = []
    with mp.Pool(4) as pool:
        for fam, P in pools.items():
            R = pool.map(evaluate, P, chunksize=8)
            R.sort(key=lambda c: c['robust']); res[fam] = R
            L.append('\n=== %s: robust choice (2021-23 only: fewest losing windows in the worst of calendar / mid-month / +0.07 cost) ===' % fam)
            for c in R[:12]:
                sc = c['sc']
                L.append('%s\n   choice 2021-23 losing: cal %d, mid %d, cost %d | profit %+.0f, deepest drop in a month %.0f || TEST 2024-26: cal %d loss / %d profit %+.0f worst %+.0f | mid %d loss %+.0f | cost %d loss %+.0f' % (
                    c['name'], sc['cal']['IN']['lose'], sc['mid']['IN']['lose'], sc['cost']['IN']['lose'], sc['cal']['IN']['total'], sc['cal']['IN']['dd'],
                    sc['cal']['OUT']['lose'], sc['cal']['OUT']['prof'], sc['cal']['OUT']['total'], sc['cal']['OUT']['worst'], sc['mid']['OUT']['lose'],
                    sc['mid']['OUT']['total'], sc['cost']['OUT']['lose'], sc['cost']['OUT']['total']))
            top = R[:50]
            L.append('   robust top 50 in the TEST period (calendar): losing months median %d (min %d, max %d); total median %+.0f; %d of 50 positive; worst month median %+.0f' % (
                np.median([c['sc']['cal']['OUT']['lose'] for c in top]), min(c['sc']['cal']['OUT']['lose'] for c in top), max(c['sc']['cal']['OUT']['lose'] for c in top),
                np.median([c['sc']['cal']['OUT']['total'] for c in top]), sum(1 for c in top if c['sc']['cal']['OUT']['total'] > 0),
                np.median([c['sc']['cal']['OUT']['worst'] for c in top])))
    pickle.dump(res, open(S + '/mcej3/robust.pkl', 'wb'))
    open(S + '/mcej3/robust.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
