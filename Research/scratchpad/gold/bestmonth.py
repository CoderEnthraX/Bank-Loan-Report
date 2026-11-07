"""Which settings give no losing month on gold 2021-2026 (asked 2026-11-07)? Each month (calendar month, or the 15th to the 14th) is run on its own:
a fresh $10,000 account and recovery state, $50 base, the gold spread, the 1:100 leverage limit (as monthly.py).
Stages:
  collect  the 19 strategies exactly as designed (their own time filters kept, kill zones follow summer time) -> bestmonth_design.pkl
  screen   trade sets: as designed / no filters (monthly file1) / the user's file2 setup, with day-of-week and kill-zone filters applied to the
           trades afterwards (approximate: in the engine a filter also frees time for other signals; the winners are re-run exactly later),
           scored at fixed $50 per window -> bestmonth_screen.pkl
  money    the best screened sets x ~25 recovery rules x hard caps x "stop for the window once it is up $X" (a new rule), per window type
           -> bestmonth_money.pkl
  report   choice on 2021-23 windows only, then 2024-26 and the whole period -> bestmonth.txt
Criteria (in this order): fewest losing windows, then the best worst window, then the most profit. A setting must trade in at least 90% of the
windows and average at least 3 trades per window; no window may blow the account."""
import sys, os, pickle, datetime, math, itertools, random, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
import recovery as RC
LEV = 100.0; START = 10000.0; BASE = 50.0
DAYSETS = {'all': (0, 1, 2, 3, 4, 5, 6), 'Mon-Thu': (0, 1, 2, 3), 'Tue-Fri': (1, 2, 3, 4), 'Tue-Thu': (1, 2, 3), 'Mon-Wed': (0, 1, 2), 'Wed-Fri': (2, 3, 4),
           'Mon/Wed/Fri': (0, 2, 4)}
KZN = ('Asia', 'London', 'NewYork', 'LonClose')
def kz_flags(t):
    """kill zones (IST, summer times; London / London Close +60 in UK winter, New York +60 in US winter) of a bar opening at t (IST)"""
    import ref
    u = t - datetime.timedelta(minutes=330); m = t.hour * 60 + t.minute
    lon = 0 if ref.uk_summer(u) else 60; ny = 0 if ref.ny_summer(u) else 60
    inz = lambda a, b: a <= m < b
    return (inz(330, 570), inz(690 + lon, 870 + lon), inz(990 + ny, 1170 + ny), inz(1170 + lon, 1290 + lon))
# ---------------------------------------------------------------- collect: the 19 as designed
def collect(sk):
    import geng, ref_gs, monthly as MO
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    st = [x for x in MO.strategies() if x['key'] == sk][0]
    o = {k: v for k, v in st['cfg'].items() if k != 'p1'}
    if o.get('kzOn'): o['kzAuto'] = True                     # the strategy's current default
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(st['tf'], vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    T = P['T']; out = []
    for x in ref_gs.run(st['tf'], o):
        if x['exit'] is None or x['ghost']: continue
        d = x['dir']; R1 = d * (x['entry'] - x['stop']); c = P['SP'][x['fill']] / R1
        out.append(dict(t=T[x['fill']], tx=T[x['exit']], ta=T[x['arm']], arm=x['arm'], fill=x['fill'], exit=x['exit'], dir=d, entry=x['entry'], R1=R1,
                        res=x['res'], c=c, how='engine', levk=LEV * R1 * (1.0 + c) / x['entry']))
    return sk, out
# ---------------------------------------------------------------- windows
def windows(kind):
    """(label, start date, end date inclusive) of the windows; only windows fully inside the data (4 Jan 2021 - 2 Oct 2026, at least 20 days)"""
    out = []; first = datetime.date(2021, 1, 4); last = datetime.date(2026, 10, 2)
    for y in range(2021, 2027):
        for m in range(1, 13):
            if kind == 'cal':
                a = datetime.date(y, m, 1); b = (datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1))
            else:
                a = datetime.date(y, m, 15); b = datetime.date(y + (m == 12), m % 12 + 1, 14)
            a2, b2 = max(a, first), min(b, last)
            if (b2 - a2).days >= 19: out.append(('%04d-%02d' % (y, m), a, b))
    return out
WIN = {k: windows(k) for k in ('cal', 'mid')}
def split_windows(trs, kind):
    """trades per window (by fill date)"""
    W = WIN[kind]; idx = {}
    for i, (lab, a, b) in enumerate(W):
        d = a
        while d <= b: idx[d] = i; d += datetime.timedelta(days=1)
    out = [[] for _ in W]
    for x in trs:
        i = idx.get(x['t'].date())
        if i is not None: out[i].append(x)
    return out
def is_in(lab): return int(lab[:4]) <= 2023                # 2021-23 = the choice period
# ---------------------------------------------------------------- trade sets with filters
def trade_sets():
    """(set name, strategy key, exitR, trades, counted-day function) for every trade set and filter"""
    D = pickle.load(open(S + '/gold/bestmonth_design.pkl', 'rb')); M = pickle.load(open(S + '/gold/monthly_trades.pkl', 'rb'))
    ST = {s['key']: s for s in M['strategies']}
    out = []
    for sk, s in ST.items():
        des = D[sk]; f1 = M['trades'][(sk, 'file1')]['trades']; f2 = M['trades'][(sk, 'file2')]['trades']
        if 'ta' not in f1[0]:
            import geng
            P = geng.prepare(s['tf'], s['cfg'].get('vwAnchorG', 'session'), 'hlc3')
            for x in f1 + f2: x['ta'] = P['T'][x['arm']]
        for dn, dd in DAYSETS.items():
            cnt = tuple(d for d in dd if d < 5)                      # the skip rule counts the ticked weekdays (Mon-Fri without a day filter)
            out.append(('design | days %s' % dn, sk, s['exitR'], [x for x in des if x['ta'].weekday() in dd], cnt))
            for kz in itertools.chain([None], itertools.product((False, True), repeat=4)):
                if kz is not None and not any(kz): continue
                sel = [x for x in f1 if x['ta'].weekday() in dd and (kz is None or any(a and b for a, b in zip(kz, x['kz'])))]
                kzt = 'no kill zones' if kz is None else 'kz ' + '+'.join(n for n, on in zip(KZN, kz) if on)
                out.append(('no filters | days %s | %s' % (dn, kzt), sk, s['exitR'], sel, cnt))
        out.append(('file2 (Tue-Thu, kz Asia+London+NY, news 17:45)', sk, s['exitR'], f2, (1, 2, 3)))
    return out
def screen_one(args):
    name, sk, exitR, trs, kind = args
    W = WIN[kind]; per = split_windows(trs, kind)
    nets = [sum((x['res'] - x['c']) / (1.0 + x['c']) for x in L) * BASE for L in per]
    n = [len(L) for L in per]
    ins = [i for i, w in enumerate(W) if is_in(w[0])]; oos = [i for i, w in enumerate(W) if not is_in(w[0])]
    f = lambda I: dict(lose=sum(1 for i in I if nets[i] < -0.01), zero=sum(1 for i in I if n[i] == 0), net=sum(nets[i] for i in I), worst=min(nets[i] for i in I),
                       trades=sum(n[i] for i in I), nwin=len(I))
    return dict(name=name, sk=sk, kind=kind, all=f(range(len(W))), ins=f(ins), oos=f(oos))
# ---------------------------------------------------------------- money rules
CAPS = [('no cap', {}), ('cap $500 start again', dict(cap=500.0, capAction='reset')), ('cap $250 start again', dict(cap=250.0, capAction='reset')),
        ('cap $500 clamp', dict(cap=500.0, capAction='clamp'))]
RULES = [('Fixed $50', 'Off', {}), ('Crooks A', 'Crooks A', {}), ('Crooks B split 2', 'Crooks B', dict(cSplit=2)), ('Crooks C', 'Crooks C', {}),
         ('Crooks D', 'Crooks D', {}), ('Crooks C over 2 wins', 'Crooks C', dict(cN=2)), ('Crooks C forget after 2', 'Crooks C', dict(crkPr='forget', crkPrN=2)),
         ('Crooks C forget after 3', 'Crooks C', dict(crkPr='forget', crkPrN=3)), ('Crooks C 50% forget 2', 'Crooks C', dict(crkPr='pct', crkPrN=2, crkPrPct=50.0)),
         ('Crooks C wait 2 wins N2', 'Crooks C', dict(crkPr='wait', crkPrN=2, crkPrM=2)), ('Crooks C skip 3 days N2', 'Crooks C', dict(crkPr='skip', crkPrN=2, crkPrD=3)),
         ('Rule C split 1', 'Rule C: carry the losses', dict(cSplit=1)), ('Rule C split 3', 'Rule C: carry the losses', dict(cSplit=3)),
         ('Exact recovery at final TP', 'Exact recovery at final TP', {}), ('Recover all on the next trade', 'Recover all losses on the next trade', {}),
         ('Recover over 3 trades', 'Recover losses over N trades', dict(recN=3)), ('Recover 50% of losses', 'Recover a % of losses per trade', dict(recPct=50.0)),
         ('Martingale x2', 'Martingale (multiply after each loss)', dict(mult=2.0)), ('Fibonacci', 'Fibonacci', {}), ("D'Alembert", "D'Alembert", {}),
         ('Labouchere', 'Labouchere', {}), ("Oscar's Grind", "Oscar's Grind", {}), ('Paroli', 'Paroli', {}), ("Reverse D'Alembert", "Reverse D'Alembert", {}),
         ('Delayed recovery', 'Delayed recovery', {})]
LOCKS = [None, 50.0, 100.0, 150.0, 250.0, 500.0]
def dayev(prev, day, cnt):
    ev = []; x = prev
    while x < day:
        x += datetime.timedelta(days=1); ev.append(cnt(x))
    return ev
def window_seq(L, cntdays):
    cnt = lambda day: day.weekday() in cntdays
    seq = []
    for k, x in enumerate(L):
        ev = ([], []) if k == 0 else (dayev(L[k - 1]['t'].date(), x['t'].date(), cnt), dayev(L[k - 1]['tx'].date(), x['t'].date(), cnt))
        seq.append((x['res'], x['c'], None, ev, x['levk']))
    return seq
def run_window(seq, mode, kw, exitR):
    """the window's results for every lock target: (net, max drop inside the window, max trade risk, blown, trades taken) per target"""
    tr = []; r = RC.simulate(seq, mode, base=BASE, start=START, exitR=exitR, trace=tr, **kw)
    out = {}
    for lk in LOCKS:
        eq = 0.0; peak = 0.0; dd = 0.0; mr = 0.0; n = 0; it = iter(seq); blown = False
        for v in tr:
            s_ = next(it)
            if v == 'SKIP': continue
            if lk is not None and eq >= lk: break
            p = v * (s_[0] - s_[1]) / (1.0 + s_[1]); eq += p; n += 1; mr = max(mr, v); peak = max(peak, eq); dd = max(dd, peak - eq)
            if START + eq <= 0: blown = True; break
        if lk is None: blown = blown or r['ruined']
        out[lk] = (eq, dd, mr, blown, n)
    return out
def money_one(args):
    """one trade set and window type: every rule x cap -> per lock: per-window nets etc."""
    name, sk, exitR, trs, cnt, kind = args
    W = WIN[kind]; per = split_windows(trs, kind); seqs = [window_seq(L, cnt) for L in per]
    res = {}
    for (rn, mode, rkw), (cn, ckw) in itertools.product(RULES, CAPS):
        if rn == 'Fixed $50' and cn != 'no cap': continue
        kw = dict(rkw); kw.update(ckw)
        wins = [run_window(sq, mode, kw, exitR) for sq in seqs]
        for lk in LOCKS:
            res[(rn, cn, lk)] = [w[lk] for w in wins]
    return dict(name=name, sk=sk, kind=kind, labels=[w[0] for w in W], n=[len(L) for L in per], res=res)
# ---------------------------------------------------------------- main
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'collect'
    if mode == 'collect':
        import monthly as MO
        keys = [s['key'] for s in MO.strategies()]
        tfo = {'M1': 0, 'M5': 1, 'M15': 2, 'H1': 3}
        with mp.Pool(4) as pool: R = pool.map(collect, sorted(keys, key=lambda k: tfo[k.split('-')[0]]), chunksize=1)
        D = dict(R)
        for sk, trs in D.items():
            for x in trs: x['kz'] = kz_flags(x['ta'])
        pickle.dump(D, open(S + '/gold/bestmonth_design.pkl', 'wb')); print({k: len(v) for k, v in D.items()})
        M = pickle.load(open(S + '/gold/monthly_trades.pkl', 'rb'))          # arm times and kill-zone flags for the file1 / file2 trades
        import geng
        for s in M['strategies']:
            P = geng.prepare(s['tf'], s['cfg'].get('vwAnchorG', 'session'), 'hlc3')
            for f in ('file1', 'file2'):
                for x in M['trades'][(s['key'], f)]['trades']: x['ta'] = P['T'][x['arm']]; x['kz'] = kz_flags(x['ta'])
        pickle.dump(M, open(S + '/gold/monthly_trades.pkl', 'wb')); print('arm times and kill-zone flags added')
    elif mode == 'screen':
        TS = trade_sets(); R = [screen_one((n, sk, xr, trs, kind)) for n, sk, xr, trs, cnt in TS for kind in ('cal', 'mid')]
        pickle.dump(R, open(S + '/gold/bestmonth_screen.pkl', 'wb')); print('screened', len(R))
    elif mode == 'money':
        R = pickle.load(open(S + '/gold/bestmonth_screen.pkl', 'rb'))
        ok = lambda r: (r['all']['net'] > 0 and r['all']['zero'] <= 0.1 * r['all']['nwin'] and r['all']['trades'] >= 3 * r['all']['nwin'])
        top = {}
        for kind in ('cal', 'mid'):
            C = [r for r in R if r['kind'] == kind and ok(r)]
            a = sorted(C, key=lambda r: (r['ins']['lose'], -r['ins']['worst'], -r['ins']['net']))[:60]      # best on the choice period
            b = sorted(C, key=lambda r: (r['all']['lose'], -r['all']['worst'], -r['all']['net']))[:30]      # best over everything (for the report)
            c = sorted(C, key=lambda r: -r['ins']['net'])[:30]                                              # the most profitable (recovery has most to work with)
            for r in a + b + c: top[(r['name'], r['sk'], kind)] = r
        TS = {(n, sk): (xr, trs, cnt) for n, sk, xr, trs, cnt in trade_sets()}
        jobs = [(n, sk, TS[(n, sk)][0], TS[(n, sk)][1], TS[(n, sk)][2], kind) for (n, sk, kind) in top]
        print('money stage on', len(jobs), 'trade sets x window types', flush=True)
        with mp.Pool(4) as pool: M = pool.map(money_one, jobs, chunksize=1)
        pickle.dump(M, open(S + '/gold/bestmonth_money.pkl', 'wb')); print('saved', len(M))
# ---------------------------------------------------------------- report
def score_rows(M):
    """one row per (trade set, window type, rule, cap, lock) with the choice-period / later-period / whole-period figures"""
    rows = []
    for m in M:
        labs = m['labels']; ins = [i for i, l in enumerate(labs) if is_in(l)]; oos = [i for i, l in enumerate(labs) if not is_in(l)]
        for (rn, cn, lk), W in m['res'].items():
            def f(I):
                nets = [W[i][0] for i in I]
                return dict(lose=sum(1 for x in nets if x < -0.01), worst=min(nets), net=sum(nets), blown=sum(1 for i in I if W[i][3]),
                            drop=max(W[i][1] for i in I), risk=max(W[i][2] for i in I), nwin=len(I))
            rows.append(dict(set=m['name'], sk=m['sk'], kind=m['kind'], rule=rn, cap=cn, lock=lk, ins=f(ins), oos=f(oos), all=f(range(len(labs))),
                             trades=sum(m['n']) / len(labs), W=W, labels=labs))
    return rows
def fmt(r):
    lk = 'none' if r['lock'] is None else '+$%d' % r['lock']
    g = lambda p: '%2d/%d lose, worst %+6.0f, net %+7.0f%s' % (r[p]['lose'], r[p]['nwin'], r[p]['worst'], r[p]['net'], ', BLOWN %d' % r[p]['blown'] if r[p]['blown'] else '')
    return ('%-7s %-52s | %-26s %-21s lock %-5s | 21-23: %s | 24-26: %s | all: %s | max trade risk $%.0f, worst drop in a window $%.0f, %.1f trades/window' % (
        r['sk'], r['set'][:52], r['rule'][:26], r['cap'], lk, g('ins'), g('oos'), g('all'), r['all']['risk'], r['all']['drop'], r['trades']))
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'report':
    M = pickle.load(open(S + '/gold/bestmonth_money.pkl', 'rb')); rows = score_rows(M); L = []
    for kind, kname in (('cal', 'CALENDAR MONTHS (1st to last day)'), ('mid', 'MID-MONTH WINDOWS (15th to 14th)')):
        R = [r for r in rows if r['kind'] == kind and r['ins']['blown'] == 0]
        for cat, cond in (('existing settings (no monthly lock), biggest trade risk <= $500', lambda r: r['lock'] is None and r['all']['risk'] <= 500.0001),
                          ('existing settings (no monthly lock), any size', lambda r: r['lock'] is None),
                          ('with the new rule "stop for the window once it is up $X", biggest trade risk <= $500', lambda r: r['lock'] is not None and r['all']['risk'] <= 500.0001),
                          ('with the new rule, any size', lambda r: r['lock'] is not None)):
            C = [r for r in R if cond(r)]
            L.append('\n%s - %s: %d candidates' % (kname, cat, len(C)))
            L.append('  chosen on 2021-23 only (fewest losing windows, then the best worst window, then the most profit):')
            for r in sorted(C, key=lambda r: (r['ins']['lose'], -r['ins']['worst'], -r['ins']['net']))[:6]: L.append('    ' + fmt(r))
            L.append('  looking back at the whole period (most fitted to the past):')
            for r in sorted(C, key=lambda r: (r['all']['lose'], -r['all']['worst'], -r['all']['net']))[:4]: L.append('    ' + fmt(r))
    open(S + '/gold/bestmonth.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
    pickle.dump(rows, open(S + '/gold/bestmonth_rows.pkl', 'wb'))
# ---------------------------------------------------------------- exact sets only (no filter applied afterwards): the 19 as designed, no filters, file2
EXACT = ('design | days all', 'no filters | days all | no kill zones', 'file2 (Tue-Thu, kz Asia+London+NY, news 17:45)')
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'exact':
    TS = [t for t in trade_sets() if t[0] in EXACT]
    jobs = [(n, sk, xr, trs, cnt, kind) for n, sk, xr, trs, cnt in TS for kind in ('cal', 'mid')]
    with mp.Pool(4) as pool: M = pool.map(money_one, jobs, chunksize=1)
    pickle.dump(M, open(S + '/gold/bestmonth_exact.pkl', 'wb'))
    rows = score_rows(M); L = []
    for kind, kname in (('cal', 'CALENDAR MONTHS'), ('mid', 'MID-MONTH WINDOWS (15th to 14th)')):
        R = [r for r in rows if r['kind'] == kind and r['ins']['blown'] == 0 and r['trades'] >= 3]
        for cat, cond in (('existing settings, biggest trade <= $500', lambda r: r['lock'] is None and r['all']['risk'] <= 500.0001),
                          ('existing settings, any size', lambda r: r['lock'] is None),
                          ('new monthly lock, biggest trade <= $500', lambda r: r['lock'] is not None and r['all']['risk'] <= 500.0001),
                          ('new monthly lock, any size', lambda r: r['lock'] is not None)):
            C = [r for r in R if cond(r)]
            z = [r for r in C if r['ins']['lose'] == 0]
            L.append('\n%s - %s: %d candidates; %d with no losing window in 2021-23, of which %d also none in 2024-26 (%.0f%%), %d with 1, %d with 2+' % (
                kname, cat, len(C), len(z), sum(1 for r in z if r['oos']['lose'] == 0), 100.0 * sum(1 for r in z if r['oos']['lose'] == 0) / max(1, len(z)),
                sum(1 for r in z if r['oos']['lose'] == 1), sum(1 for r in z if r['oos']['lose'] >= 2)))
            L.append('  chosen on 2021-23 only:')
            for r in sorted(C, key=lambda r: (r['ins']['lose'], -r['ins']['worst'], -r['ins']['net']))[:5]: L.append('    ' + fmt(r))
            L.append('  whole period:')
            for r in sorted(C, key=lambda r: (r['all']['lose'], -r['all']['worst'], -r['all']['net']))[:5]: L.append('    ' + fmt(r))
    open(S + '/gold/bestmonth_exact.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
    pickle.dump(rows, open(S + '/gold/bestmonth_exact_rows.pkl', 'wb'))
