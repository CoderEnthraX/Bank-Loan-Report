"""Exact engine re-runs of the finalists of bestmonth.py (their day / kill-zone filters inside the engine), then the same month-by-month money test.
Output: bestmonth_final.pkl + bestmonth_final.txt"""
import sys, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
import bestmonth as B
TIMEKEYS = ('dayOn', 'days', 'hoursOn', 'hoursSess', 'kzOn', 'kz', 'kzShift', 'kzAuto')
DD = lambda *d: tuple(i in d for i in range(7))
# name, strategy, keep own filters?, engine filters, window type, rule, cap, lock
FIN = [
    ('F1 calendar, lock +$250', 'M15-S9', False, dict(), 'cal', 'Labouchere', 'cap $500 clamp', 250.0),
    ('F2 calendar, lock +$150', 'M15-S7', True, dict(), 'cal', 'Martingale x2', 'cap $500 clamp', 150.0),
    ('F3 mid-month, lock +$150', 'M5-S3', False, dict(dayOn=True, days=DD(1, 2, 3), kzOn=True, kz=(False, False, True, True), kzAuto=True), 'mid', 'Martingale x2', 'cap $500 clamp', 150.0),
    ('F4 calendar, no lock', 'M5-S3', False, dict(dayOn=True, days=DD(1, 2, 3), kzOn=True, kz=(False, False, True, True), kzAuto=True), 'cal', 'Fibonacci', 'cap $500 clamp', None),
    ('F5 mid-month, no lock', 'M15-S1', True, dict(dayOn=True, days=DD(1, 2, 3)), 'mid', 'Rule C split 1', 'cap $500 clamp', None),
    ('F6 calendar, lock +$250 (chosen on 2021-23)', 'M15-S7', True, dict(dayOn=True, days=DD(2, 3, 4)), 'cal', 'Labouchere', 'cap $500 clamp', 250.0),
]
def engine(arg):
    name, sk, keep, flt, kind, rn, cn, lk = arg
    import geng, ref_gs, monthly as MO, datetime
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    st = [x for x in MO.strategies() if x['key'] == sk][0]
    o = {k: v for k, v in st['cfg'].items() if k != 'p1' and (keep or k not in TIMEKEYS)}
    if o.get('kzOn'): o['kzAuto'] = True
    o.update(flt)
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(st['tf'], vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    out = []
    for x in ref_gs.run(st['tf'], o):
        if x['exit'] is None or x['ghost']: continue
        d = x['dir']; R1 = d * (x['entry'] - x['stop']); c = P['SP'][x['fill']] / R1
        out.append(dict(t=P['T'][x['fill']], tx=P['T'][x['exit']], ta=P['T'][x['arm']], fill=x['fill'], exit=x['exit'], dir=d, entry=x['entry'], R1=R1, res=x['res'], c=c,
                        levk=B.LEV * R1 * (1.0 + c) / x['entry']))
    days = flt.get('days') or (o.get('days') if o.get('dayOn') else None)
    cnt = tuple(i for i in range(5) if days is None or days[i])
    return name, sk, kind, rn, cn, lk, st['exitR'], cnt, o, out
if __name__ == '__main__':
    with mp.Pool(4) as pool: E = pool.map(engine, FIN, chunksize=1)
    rules = {r[0]: r for r in B.RULES}; caps = dict(B.CAPS); L = []; out = []
    for name, sk, kind, rn, cn, lk, xr, cnt, o, trs in E:
        _, mode, rkw = rules[rn]; kw = dict(rkw); kw.update(caps[cn])
        W = B.WIN[kind]; per = B.split_windows(trs, kind)
        wins = [B.run_window(B.window_seq(Lw, cnt), mode, kw, xr)[lk] for Lw in per]
        labs = [w[0] for w in W]
        f = lambda I: dict(lose=sum(1 for i in I if wins[i][0] < -0.01), worst=min(wins[i][0] for i in I), net=sum(wins[i][0] for i in I), n=len(I),
                           drop=max(wins[i][1] for i in I), risk=max(wins[i][2] for i in I), blown=sum(1 for i in I if wins[i][3]))
        ins = [i for i, l in enumerate(labs) if B.is_in(l)]; oos = [i for i, l in enumerate(labs) if not B.is_in(l)]
        a, b, c_ = f(ins), f(oos), f(range(len(labs)))
        L.append('%s: %s, %s, %s, lock %s | engine trades %d (%.1f a window)\n   21-23 lose %d/%d worst %+.0f net %+.0f | 24-26 lose %d/%d worst %+.0f net %+.0f | all lose %d/%d worst %+.0f net %+.0f | max trade $%.0f, worst drop $%.0f, blown %d' % (
            name, sk, rn, cn, lk, len(trs), len(trs) / len(labs), a['lose'], a['n'], a['worst'], a['net'], b['lose'], b['n'], b['worst'], b['net'], c_['lose'], c_['n'], c_['worst'], c_['net'],
            c_['risk'], c_['drop'], c_['blown']))
        out.append(dict(name=name, sk=sk, kind=kind, rule=rn, cap=cn, lock=lk, exitR=xr, cfg=o, labels=labs, windows=wins, trades=trs, n=[len(x) for x in per]))
    pickle.dump(out, open(S + '/gold/bestmonth_final.pkl', 'wb'))
    open(S + '/gold/bestmonth_final.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
