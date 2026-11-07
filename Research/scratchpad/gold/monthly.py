"""Month-by-month results of the 19 gold strategies (profitable at fixed $50, no partial close) with every loss-recovery rule (asked 2026-11-07).
Two setups (the strategies' own day / hour / kill-zone filters are replaced by the setup's):
  file1  every day the market is open (no day filter), no time window, no kill zones, no news window: as many trades as possible
  file2  Tue / Wed / Thu only (IST), kill zones Asia + London + New York (London Close off; they follow London / New York summer time),
         daily news window 17:45-18:15 IST that follows New York time (18:45-19:15 IST in US winter), no new trades from 60 minutes before it
         until it ends, and at its start an open trade is closed at market and a working entry is cancelled (the strategy's own rules)
Each month on its own (IST calendar month): the trades filled in that month, a fresh $10,000 account and a fresh recovery state on the 1st,
$50 base risk, the gold spread as the cost, the strategy's 1:100 leverage limit on the size (no lot rounding).
Usage: monthly.py collect | money | check   (collect: engine runs -> monthly_trades.pkl; money -> monthly.pkl)"""
import sys, os, pickle, datetime, math, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
import recovery as RC, crooks
LEV = 100.0; START = 10000.0; BASE = 50.0
TIMEKEYS = ('dayOn', 'days', 'hoursOn', 'hoursSess', 'kzOn', 'kz', 'kzShift', 'kzAuto')
SETUPS = {
    'file1': dict(title='Monday to Friday, no news, no time window', eng=dict(dayOn=False, hoursOn=False, kzOn=False), news=False,
                  counted=lambda d: d.weekday() < 5),
    'file2': dict(title='Tue / Wed / Thu, kill zones Asia + London + New York, news 17:45-18:15 IST', news=True,
                  eng=dict(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=False, kzOn=True, kz=(True, True, True, False), kzShift=0, kzAuto=True),
                  counted=lambda d: d.weekday() in (1, 2, 3)),
}
NEWS_S, NEWS_E, NEWS_PRE = 17 * 60 + 45, 18 * 60 + 15, 60
VARIANTS = [
    ('Fixed $50', 'no recovery: every trade risks $50', 'Off', {}),
    ('Crooks C', 'Crooks C as now, no cap', 'Crooks C', {}),
    ('C cap $500', 'Crooks C, hard cap $500, Start again', 'Crooks C', dict(cap=500.0, capAction='reset')),
    ('C cap $250', 'Crooks C, hard cap $250, Start again', 'Crooks C', dict(cap=250.0, capAction='reset')),
    ('C cap $150', 'Crooks C, hard cap $150, Start again', 'Crooks C', dict(cap=150.0, capAction='reset')),
    ('C over 2 wins', 'Crooks C, win the loss back over 2 wins, no cap', 'Crooks C', dict(cN=2)),
    ('Forget after 2', 'Crooks C rule: forget the loss after 2 losing recovery trades in a row', 'Crooks C', dict(crkPr='forget', crkPrN=2)),
    ('Forget after 3', 'Crooks C rule: forget the loss after 3 losing recovery trades in a row', 'Crooks C', dict(crkPr='forget', crkPrN=3)),
    ('50% forget 2', 'Crooks C rule: go for 50% of the loss, forget it after 2', 'Crooks C', dict(crkPr='pct', crkPrN=2, crkPrPct=50.0)),
    ('50% forget 3', 'Crooks C rule: go for 50% of the loss, forget it after 3', 'Crooks C', dict(crkPr='pct', crkPrN=3, crkPrPct=50.0)),
    ('Wait 2W after 2', 'Crooks C rule: after 2 losing recovery trades wait for 2 wins in a row, then a loss and a win', 'Crooks C', dict(crkPr='wait', crkPrN=2, crkPrM=2)),
    ('Wait 3W after 2', 'Crooks C rule: after 2 losing recovery trades wait for 3 wins in a row, then a loss and a win', 'Crooks C', dict(crkPr='wait', crkPrN=2, crkPrM=3)),
    ('Wait 2W after 3', 'Crooks C rule: after 3 losing recovery trades wait for 2 wins in a row, then a loss and a win', 'Crooks C', dict(crkPr='wait', crkPrN=3, crkPrM=2)),
    ('Skip 3d after 2', 'Crooks C rule: after 2 losing recovery trades skip 3 trading days, keep the loss', 'Crooks C', dict(crkPr='skip', crkPrN=2, crkPrD=3)),
    ('Skip 3d after 2 F', 'Crooks C rule: after 2 losing recovery trades skip 3 trading days, forget the loss', 'Crooks C', dict(crkPr='skip', crkPrN=2, crkPrD=3, crkPrForget=True)),
    ('Skip 2d after 3', 'Crooks C rule: after 3 losing recovery trades skip 2 trading days, keep the loss', 'Crooks C', dict(crkPr='skip', crkPrN=3, crkPrD=2)),
    ('Skip 2d after 3 F', 'Crooks C rule: after 3 losing recovery trades skip 2 trading days, forget the loss', 'Crooks C', dict(crkPr='skip', crkPrN=3, crkPrD=2, crkPrForget=True)),
]
def strategies():
    """the 19 strategies of the Crooks C single-win study (crooks_alt.py): profitable at fixed $50, no partial close"""
    out = []
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            seq0 = crooks.sequence(d['trades'], d['cfg'])
            if any(p for _, _, _, p in seq0): continue
            if RC.simulate([(r_, c) for _, r_, c, p in seq0], 'Off', exitR=crooks.exit_r(d['cfg']))['net'] <= 0: continue
            out.append(dict(key='%s-S%d' % (tf, i), tf=tf, idx=i, name=d['name'], cfg=dict(d['cfg']), exitR=crooks.exit_r(d['cfg']),
                            ref=[(x[0], x[1]) for x in d['trades']]))
    return out
def ny_summer(utc):
    import ref
    return ref.ny_summer(utc)
def news_flags(P):
    """per bar: in the news window, news block (window or the 60 minutes before it), first bar of a window; minute math in IST like the strategy"""
    T = P['T']; n = len(T); inW = [False] * n; blk = [False] * n; start = [False] * n
    for j in range(n):
        t = T[j]; sh = 0 if ny_summer(t - datetime.timedelta(minutes=330)) else 60
        s = (NEWS_S + sh) % 1440; e = (NEWS_E + sh) % 1440; cur = t.hour * 60 + t.minute
        inW[j] = (s <= cur < e) if s < e else (cur >= s or cur < e)
        diff = (s - cur + 1440) % 1440
        blk[j] = inW[j] or (0 < diff <= NEWS_PRE)
        start[j] = inW[j] and not (inW[j - 1] if j > 0 else False)
    return inW, blk, start
def collect(arg):
    """engine run of one strategy in one setup, then the strategy's execution (news window for file2): the trades the strategy takes"""
    sk, setup = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    st = [x for x in strategies() if x['key'] == sk][0]
    o = {k: v for k, v in st['cfg'].items() if k not in TIMEKEYS and k != 'p1'}
    o.update(SETUPS[setup]['eng'])
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(st['tf'], vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    T, O = P['T'], P['O']
    eng = [x for x in ref_gs.run(st['tf'], o) if x['exit'] is not None and not x['ghost']]
    if SETUPS[setup]['news']: inW, blk, start = news_flags(P)
    out = []; stats = dict(engine=len(eng), skipped_news=0, cancelled=0, closed_news=0)
    for x in eng:
        a, f, xb, d = x['arm'], x['fill'], x['exit'], x['dir']
        R1 = d * (x['entry'] - x['stop']); res = x['res']; exb = xb; how = 'engine'
        if SETUPS[setup]['news']:
            if blk[a]: stats['skipped_news'] += 1; continue                          # armed inside the news block: not taken
            if any(blk[j] for j in range(a + 1, f)): stats['cancelled'] += 1; continue   # the working entry is cancelled before the fill
            b = next((j for j in range(f, xb) if start[j]), None)                     # the window starts while the trade is open
            if b is not None and b + 1 < len(O):
                res = d * (O[b + 1] - x['entry']) / R1; exb = b + 1; how = 'news close'; stats['closed_news'] += 1
        out.append(dict(t=T[f], tx=T[exb], arm=a, fill=f, exit=exb, dir=d, entry=x['entry'], R1=R1, res=res, c=P['SP'][f] / R1, how=how,
                        levk=LEV * R1 * (1.0 + P['SP'][f] / R1) / x['entry']))
    return sk, setup, out, stats
def months():
    m = []; y, mo = 2021, 1
    while (y, mo) <= (2026, 10):
        m.append('%04d-%02d' % (y, mo)); mo += 1
        if mo == 13: y += 1; mo = 1
    return m
def dayev(prev_day, day, counted):
    ev = []; x = prev_day
    while x < day:
        x += datetime.timedelta(days=1); ev.append(counted(x))
    return ev
def money_month(trs, setup, exitR):
    """every rule on the trades of one month, each from a fresh $10,000 account"""
    cnt = SETUPS[setup]['counted']
    seq = []
    for k, x in enumerate(trs):
        if k == 0: ev = ([], [])
        else: ev = (dayev(trs[k - 1]['t'].date(), x['t'].date(), cnt), dayev(trs[k - 1]['tx'].date(), x['t'].date(), cnt))
        seq.append((x['res'], x['c'], None, ev, x['levk']))
    base = dict(trades=len(trs), wins=sum(1 for x in trs if x['res'] - x['c'] > 0), losses=sum(1 for x in trs if x['res'] - x['c'] <= 0),
                netR=sum((x['res'] - x['c']) / (1.0 + x['c']) for x in trs), newsClosed=sum(1 for x in trs if x['how'] == 'news close'))
    out = {}
    for nm, _, mode, kw in VARIANTS:
        tr = []; r = RC.simulate(seq, mode, base=BASE, start=START, exitR=exitR, trace=tr, **kw)
        taken = [v for v in tr if v != 'SKIP']
        # per-trade P&L again from the trace (the simulator returns totals): wins / losses / biggest loss of the trades taken
        pn = []; it = iter(seq)
        for v in tr:
            s_ = next(it)
            if v == 'SKIP': continue
            pn.append(v * (s_[0] - s_[1]) / (1.0 + s_[1]))
        out[nm] = dict(net=r['net'], trades=len(pn), skipped=len(tr) - len(taken), wins=sum(1 for p in pn if p > 0), losses=sum(1 for p in pn if p <= 0),
                       maxDD=r['maxDD'], maxDDpct=r['maxDDpct'], maxLoss=max([-p for p in pn] + [0.0]), maxRisk=r['maxRisk'], ruined=r['ruined'],
                       end=r['end'], capStopped=r['capStopped'])
    return base, out
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'collect'
    fn = S + '/gold/monthly_trades.pkl'
    if mode == 'collect':
        ST = strategies(); assert len(ST) == 19, len(ST)
        tfo = {'M1': 0, 'M5': 1, 'M15': 2, 'H1': 3}
        jobs = sorted([(s['key'], f) for s in ST for f in SETUPS], key=lambda j: tfo[j[0].split('-')[0]])    # M1 first (slowest)
        with mp.Pool(4) as pool: R = pool.map(collect, jobs, chunksize=1)
        D = {(sk, f): dict(trades=tr, stats=stt) for sk, f, tr, stt in R}
        pickle.dump(dict(strategies=[{k: v for k, v in s.items() if k != 'ref'} for s in ST], trades=D), open(fn, 'wb'))
        for (sk, f), d in sorted(D.items()): print(sk, f, len(d['trades']), d['stats'])
    elif mode == 'money':
        Dt = pickle.load(open(fn, 'rb')); ST = Dt['strategies']; M = months()
        res = {f: {} for f in SETUPS}
        for f in SETUPS:
            for s in ST:
                trs = Dt['trades'][(s['key'], f)]['trades']
                byM = {m: [] for m in M}
                for x in trs:
                    k = '%04d-%02d' % (x['t'].year, x['t'].month)
                    if k in byM: byM[k].append(x)
                res[f][s['key']] = {m: money_month(byM[m], f, s['exitR']) for m in M}
        out = dict(setups={f: dict(title=SETUPS[f]['title']) for f in SETUPS}, variants=[(nm, desc) for nm, desc, _, _ in VARIANTS], strategies=ST, months=M, res=res,
                   stats={k: v['stats'] for k, v in Dt['trades'].items()})
        pickle.dump(out, open(S + '/gold/monthly.pkl', 'wb')); print('saved monthly.pkl')
    elif mode == 'check':
        # file1 on the strategies without their own time filter must give the stored catalogue trades exactly; fixed $50 = 50 x net R per month
        Dt = pickle.load(open(fn, 'rb')); ST = strategies(); L = []
        for s in ST:
            own = any(s['cfg'].get(k) for k in ('dayOn', 'hoursOn', 'kzOn'))
            trs = Dt['trades'][(s['key'], 'file1')]['trades']
            if not own:
                a = [(x['t'], round(x['res'], 9)) for x in trs]; b = [(t, round(r_, 9)) for t, r_ in sorted(s['ref'])]
                L.append('%-8s file1 vs the stored trades: %d vs %d trades, identical %s' % (s['key'], len(a), len(b), a == b))
            else: L.append('%-8s has its own time filter (removed in file1): %d trades in file1 vs %d stored' % (s['key'], len(trs), len(s['ref'])))
        R = pickle.load(open(S + '/gold/monthly.pkl', 'rb'))
        worst = 0.0
        for f in SETUPS:
            for s in ST:
                for m, (b, v) in R['res'][f][s['key']].items():
                    worst = max(worst, abs(v['Fixed $50']['net'] - 50.0 * b['netR']))
        L.append('fixed $50 month net vs 50 x net R: worst difference %.2e' % worst)
        open(S + '/gold/monthly_check.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
