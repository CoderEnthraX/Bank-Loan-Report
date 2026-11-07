import sys, pickle, os, datetime, copy, collections
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
V = S + '/verify_monthly'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
DROP = ['dayOn', 'days', 'hoursOn', 'hoursSess', 'kzOn', 'kz', 'kzShift', 'kzAuto', 'p1']

def engine(tf, cfg, which):
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    c = {k: v for k, v in cfg.items() if k not in DROP}
    if which == 'file2':
        c.update(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=False, kzOn=True,
                 kz=(True, True, True, False), kzShift=0, kzAuto=True)
    else:
        c.update(dayOn=False, hoursOn=False, kzOn=False)
    o = dict(c); vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    trades = [x for x in ref_gs.run(tf, o) if x['exit'] is not None and not x['ghost']]
    keep = [dict(arm=x['arm'], fill=x['fill'], exit=x['exit'], dir=x['dir'], entry=x['entry'], stop=x['stop'], res=x['res']) for x in trades]
    return keep, dict(O=P['O'], T=P['T'], SP=P['SP'])

def nth_sunday(y, m, n):
    d = datetime.datetime(y, m, 1); off = (6 - d.weekday()) % 7
    return d + datetime.timedelta(days=off + 7 * (n - 1))

def us_dst(utc):
    y = utc.year
    a = nth_sunday(y, 3, 2) + datetime.timedelta(hours=7)
    b = nth_sunday(y, 11, 1) + datetime.timedelta(hours=6)
    return a <= utc < b

def news_arrays(T):
    n = len(T); inW = [False] * n; pre = [False] * n
    cache = {}
    for i, t in enumerate(T):
        utc = t - datetime.timedelta(hours=5, minutes=30)
        key = (utc.year, utc.month, utc.day, utc.hour)  # DST switch at whole UTC hours
        if key not in cache: cache[key] = us_dst(utc)
        # careful: key by hour OK since switches are at 07:00 / 06:00 UTC exactly
        sh = 0 if cache[key] else 60
        s = 17 * 60 + 45 + sh; e = 18 * 60 + 15 + sh
        m = t.hour * 60 + t.minute
        inW[i] = s <= m < e
        pre[i] = 0 < (s - m) % 1440 <= 60
    block = [a or b for a, b in zip(inW, pre)]
    start = [inW[i] and not (i > 0 and inW[i - 1]) for i in range(n)]
    return block, start

def apply_news(trades, B):
    O, T = B['O'], B['T']
    block, start = news_arrays(T)
    # prefix sums for fast any-queries
    n = len(T)
    pb = [0] * (n + 1); ps = [0] * (n + 1)
    for i in range(n): pb[i + 1] = pb[i] + block[i]; ps[i + 1] = ps[i] + start[i]
    out = []; st = collections.Counter()
    for x in trades:
        a, f, e = x['arm'], x['fill'], x['exit']
        if block[a]: st['nottaken'] += 1; continue
        if f - a > 1 and pb[f] - pb[a + 1] > 0: st['cancelled'] += 1; continue
        t = dict(x); t['how'] = 'engine'
        bs = [b for b in range(f, e) if start[b]]
        if bs:
            b = bs[0]
            if b + 1 < n:
                R1 = x['dir'] * (x['entry'] - x['stop'])
                t['res'] = x['dir'] * (O[b + 1] - x['entry']) / R1; t['exit'] = b + 1; t['how'] = 'news'; st['newsclosed'] += 1
        out.append(t)
    st['taken'] = len(out)
    return out, st

def days_list(d0, d1, counted):
    out = []; d = d0 + datetime.timedelta(days=1)
    while d <= d1:
        out.append(d.weekday() in counted); d += datetime.timedelta(days=1)
    return out

VARIANTS = [('Fixed $50', 'Off', {}), ('Crooks C', 'Crooks C', {}), ('Forget after 2', 'Crooks C', dict(crkPr='forget', crkPrN=2)),
            ('Skip 3d after 2', 'Crooks C', dict(crkPr='skip', crkPrN=2, crkPrD=3))]

def monthly_nets(trades, B, exitR, counted):
    import recovery as RC
    T, SP = B['T'], B['SP']
    by = collections.defaultdict(list)
    for t in trades: by[(T[t['fill']].year, T[t['fill']].month)].append(t)
    res = {}
    months = [(y, m) for y in range(2021, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]
    for ym in months:
        L = by.get(ym, [])
        seq = []; prev = None
        for k, t in enumerate(L):
            R1 = t['dir'] * (t['entry'] - t['stop']); c = SP[t['fill']] / R1; levk = 100 * R1 * (1 + c) / t['entry']
            if k == 0: ev = ([], [])
            else:
                fd = T[t['fill']].date()
                ev = (days_list(T[prev['fill']].date(), fd, counted), days_list(T[prev['exit']].date(), fd, counted))
            seq.append((t['res'], c, None, ev, levk)); prev = t
        r = {}
        for name, mode, kw in VARIANTS:
            tr = []
            if not seq: r[name] = 0.0; continue
            r[name] = RC.simulate(seq, mode, base=50.0, start=10000.0, exitR=exitR, trace=tr, **kw)['net']
        res[ym] = r
    return res

if __name__ == '__main__':
    stage = sys.argv[1]
    if stage == 'engine':
        key, which = sys.argv[2], sys.argv[3]
        d = pickle.load(open(S + '/gold/monthly_trades.pkl', 'rb'))
        s = [x for x in d['strategies'] if x['key'] == key][0]
        tr, B = engine(s['tf'], s['cfg'], which)
        pickle.dump((tr, B, s['exitR']), open('%s/eng_%s_%s.pkl' % (V, key, which), 'wb'))
        print(key, which, len(tr))

def compare():
    D = pickle.load(open(S + '/gold/monthly_trades.pkl', 'rb')); M = pickle.load(open(S + '/gold/monthly.pkl', 'rb'))
    names = {'Fixed $50': 'Fixed $50', 'Crooks C': 'Crooks C', 'Forget after 2': 'Forget after 2', 'Skip 3d after 2': 'Skip 3d after 2'}
    for key, which in [('M15-S8', 'file2'), ('M1-S4', 'file2'), ('M5-S4', 'file2'), ('H1-S8', 'file2'), ('M15-S8', 'file1')]:
        tr, B, exitR = pickle.load(open('%s/eng_%s_%s.pkl' % (V, key, which), 'rb'))
        if which == 'file2':
            mine, st = apply_news(tr, B); counted = {1, 2, 3}
        else:
            mine = [dict(t, how='engine') for t in tr]; st = collections.Counter(taken=len(tr)); counted = {0, 1, 2, 3, 4}
        ref = D['trades'][(key, which)]; rt = ref['trades']; rs = ref['stats']
        print('==', key, which, 'mine', len(mine), dict(st), 'ref', len(rt), rs)
        # (a)
        nd = 0; first = None
        if len(mine) != len(rt): print('  COUNT DIFF', len(mine), len(rt))
        fills_m = {t['fill'] for t in mine}; fills_r = {t['fill'] for t in rt}
        print('  fills only mine', sorted(fills_m - fills_r)[:5], 'only ref', sorted(fills_r - fills_m)[:5])
        for a, b in zip(mine, rt):
            if a['fill'] != b['fill'] or a['exit'] != b['exit'] or abs(a['res'] - b['res']) > 1e-9:
                nd += 1
                if first is None: first = (a['fill'], a['exit'], a['res'], a['how'], b['fill'], b['exit'], b['res'], b['how'])
        howm = collections.Counter(t['how'] for t in mine); howr = collections.Counter(t['how'] for t in rt)
        print('  (a) differing positional trades', nd, 'first', first, '| how mine', dict(howm), 'ref', dict(howr))
        if which == 'file2':
            print('  stats mine: engine %d not-taken %d cancelled %d news-closed %d | ref: engine %d skipped %d cancelled %d closed %d' % (
                len(tr), st['nottaken'], st['cancelled'], st['newsclosed'], rs['engine'], rs['skipped_news'], rs['cancelled'], rs['closed_news']))
        # (b)
        nets = monthly_nets(mine, B, exitR, counted)
        bad = collections.defaultdict(list); tot = 0
        for ym, r in nets.items():
            ms = '%d-%02d' % ym
            rr = M['res'][which][key].get(ms)
            if rr is None:
                bad['missing'].append(ms); continue
            v = rr[1]
            for nm in names:
                tot += 1
                if abs(r[nm] - v[nm]['net']) > 1e-6: bad[nm].append((ms, r[nm], v[nm]['net']))
        extra = set(M['res'][which][key]) - {'%d-%02d' % ym for ym in nets}
        print('  (b) cells compared', tot, 'mismatches', {k: len(v) for k, v in bad.items()}, 'extra months in ref', sorted(extra)[:3])
        for k, v in bad.items(): print('     first', k, v[:3])
if __name__ == '__main__' and sys.argv[1] == 'compare': compare()
