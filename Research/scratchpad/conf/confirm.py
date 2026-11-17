"""Confirmation entry study (asked 2026-11-17). For every setup the Auction Retest engine fills (the price retests the entry), instead of the
limit fill: wait up to K candles (the touch candle included) for a candle that CLOSES beyond the entry in the trade direction (green for a long,
red for a short), optionally with "aggressive delta" (no real delta on gold CFDs: close in the outer 40% of the candle, and also tick volume
above its 20-candle mean), and with the new stop distance >= m x the original risk. Enter at that close; stop at the entry (or the candle's
low / high); target = close + k x the new stop distance (or the original TP1). A close beyond the original stop before confirming cancels it.
Exits from the next candle: stop first if both are touched. Costs 0.23 per oz: net R = (R - c) / (1 + c), c = 0.23 / stop distance.
Modes: A = every setup taken this way; B = normal trades, after a losing trade the confirmation trades until one wins, then normal again.
Output: conf/results.pkl (rows per base x variant x mode, and the trade lists for the money test)."""
import sys, os, pickle, itertools, multiprocessing as mp, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/bese'); sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
COST = 0.23
SPLIT = dt.datetime(2024, 1, 1)
USER_ENG = dict(halfCap=True, maxFills=10, entryPct=25.0, mv3R=0.0, noChaseSig=2.0, chopMax=13.5, kzShift=0, kzAuto=True)
USER_ON = dict(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, hoursSess=(600, 2300), kzOn=True, kz=(True, True, True, False))
KS = (1, 3, 6); DELTA = ('off', 'clv', 'clv+vol'); STOPS = ('entry', 'candle'); TGT = ('tp1', 1.0, 1.5, 2.0); MINS = (0.0, 0.15, 0.3)


def bases():
    import crooks
    out = [dict(key='M5-your settings (TP1)', tf='M5', cfg=dict(USER_ENG, exitAt=1, **USER_ON))]
    for tf, keep in (('M5', (1, 2, 3, 4)), ('M15', (1, 3, 6, 7, 8, 9))):
        src = crooks.sources(tf)
        for i in keep: out.append(dict(key='%s-S%d' % (tf, i), tf=tf, cfg=dict(src[i]['cfg'])))
    return out


def engine(b):
    import geng, ref_gbe, greedy
    ref_gbe.eprep = geng.ref_g.eprep
    o = {k: v for k, v in b['cfg'].items() if k != 'p1'}
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(b['tf'], vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    p = dict(greedy.defaults()); p.update(o)
    tr = [x for x in ref_gbe.run(b['tf'], o) if not x['ghost'] and x['exit'] is not None]
    return P, p, tr


def net(res, dist): c = COST / dist; return (res - c) / (1.0 + c)


def confirm(P, x, p, K, delta, stopM, tgt, m):
    """the confirmation trade of setup x, or None: dict(fill, exit, dist, res)"""
    O, H, L, C, TV = P['O'], P['H'], P['L'], P['C'], P['W']; n = len(O); tol = 0.00001
    d = x['dir']; E = x['entry']; S0 = x['stop']; R0 = d * (E - S0); f = x['fill']
    for j in range(f, min(f + K, n)):
        if d * (C[j] - S0) <= 0: return None                                  # closed beyond the original stop: the setup failed
        rng = H[j] - L[j]
        ok = d * (C[j] - O[j]) > 0 and d * (C[j] - E) > 0 and rng > 0
        if ok and delta != 'off':
            clv = (C[j] - L[j]) / rng if d == 1 else (H[j] - C[j]) / rng
            ok = clv >= 0.6
            if ok and delta == 'clv+vol':
                a = max(0, j - 20); mv = sum(TV[a:j]) / max(1, j - a); ok = TV[j] > mv
        if not ok: continue
        stp = E if stopM == 'entry' else (L[j] if d == 1 else H[j])
        dist = d * (C[j] - stp)
        if dist < max(m * R0, 0.05): continue                                  # too small a stop (0.05 = 5 ticks at least)
        tF = (E + d * p['tp1R'] * R0) if tgt == 'tp1' else C[j] + d * tgt * dist
        if d * (tF - C[j]) <= 0: continue                                       # already past the target
        for i in range(j + 1, n):
            if (L[i] <= stp + tol) if d == 1 else (H[i] >= stp - tol): return dict(fill=j, exit=i, dist=dist, res=-1.0)
            if (H[i] >= tF - tol) if d == 1 else (L[i] <= tF + tol): return dict(fill=j, exit=i, dist=dist, res=d * (tF - C[j]) / dist)
        return None
    return None


def stats(rows, T):
    out = {}
    for per in ('in', 'out', 'all'):
        rr = [r for r in rows if per == 'all' or (T[r['fill']] < SPLIT) == (per == 'in')]
        nn = [net(r['res'], r['dist']) for r in rr]
        eq = pk = dd = 0.0; run = mrun = 0
        for v in nn:
            eq += v; pk = max(pk, eq); dd = max(dd, pk - eq); run = run + 1 if v < 0 else 0; mrun = max(mrun, run)
        out[per] = dict(n=len(nn), win=sum(v > 0 for v in nn) / len(nn) if nn else 0, net=sum(nn), avgW=(sum(v for v in nn if v > 0) / max(1, sum(v > 0 for v in nn))),
                        dd=dd, lrun=mrun, medDist=sorted(r['dist'] for r in rr)[len(rr) // 2] if rr else 0)
    return out


def work(b):
    P, p, tr = engine(b); T = P['T']
    normal = [dict(fill=x['fill'], exit=x['exit'], dist=x['dir'] * (x['entry'] - x['stop']), res=x['res']) for x in tr]
    out = dict(key=b['key'], tf=b['tf'], normal=stats(normal, T), normalSeq=[(T[r['fill']], r['res'], COST / r['dist']) for r in normal], rows=[])
    for K, dl, sm, tg, m in itertools.product(KS, DELTA, STOPS, TGT, MINS):
        cf = [confirm(P, x, p, K, dl, sm, tg, m) for x in tr]
        A = []; last = -1
        for c in cf:                                                            # mode A: every setup, one trade at a time
            if c and c['fill'] > last: A.append(c); last = c['exit']
        B = []; seqB = []; last = -1; rec = False
        for x, c, nr in zip(tr, cf, normal):                                    # mode B: after a loss, confirmation trades until one wins
            if not rec:
                if nr['fill'] <= last: continue
                B.append(nr); seqB.append((T[nr['fill']], nr['res'], COST / nr['dist'], 'n')); last = nr['exit']
                if net(nr['res'], nr['dist']) < 0: rec = True
            else:
                if not c or c['fill'] <= last: continue
                B.append(c); seqB.append((T[c['fill']], c['res'], COST / c['dist'], 'c')); last = c['exit']
                if net(c['res'], c['dist']) > 0: rec = False
        v = dict(K=K, delta=dl, stop=sm, tgt=tg, minStop=m)
        out['rows'].append(dict(v, A=stats(A, T), B=stats(B, T), Bc=stats([r for r, s in zip(B, seqB) if s[3] == 'c'], T), seqB=seqB))
    return out


if __name__ == '__main__':
    with mp.Pool(min(11, os.cpu_count() or 2)) as pool: res = pool.map(work, bases())
    pickle.dump(res, open(S + '/conf/results.pkl', 'wb'))
    print('done', len(res))
