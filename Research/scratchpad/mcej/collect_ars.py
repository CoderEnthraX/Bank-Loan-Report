"""Monthly Crooks E-J x profit ladder workbook (asked 2026-11-15), Auction Retest part: the trades of the M5 and M15 catalogue strategies
as designed (their own filters kept), from an engine re-run so that every trade has its fill time, exit time and entry price.
Checked against the stored catalogue trades (crooks.sources): same count, same R and cost per trade, same fill times.
Output: mcej/ars_trades.pkl  {key: dict(tf, idx, name, exitR, trades=[dict(t, tx, res, c, sd, px, dir)])}"""
import sys, pickle, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
import crooks, greedy, recovery as RC

SEL = {'M5': [1, 2, 3, 4], 'M15': [1, 3, 6, 7, 8, 9]}     # profitable at fixed $50, no partial close (the 19-strategy set of the earlier studies)


def collect(arg):
    tf, i = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    src = crooks.sources(tf)[i]
    o = {k: v for k, v in src['cfg'].items() if k != 'p1'}
    vw = o.pop('vwAnchorG', 'session'); vsrc = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, vsrc); geng._CUR['vw'] = vw; geng._CUR['src'] = vsrc
    T = P['T']
    eng = [x for x in ref_gs.run(tf, o) if x['exit'] is not None and not x['ghost']]
    out = []
    for x in eng:
        f, xb, d = x['fill'], x['exit'], x['dir']
        R1 = d * (x['entry'] - x['stop'])
        out.append(dict(t=T[f], tx=T[xb], res=x['res'], c=P['SP'][f] / R1, sd=R1, px=x['entry'], dir=d))
    # the stored catalogue trades: (time, R, ..., cost, stop distance, ...)
    ref = sorted(src['trades'], key=lambda z: z[0])
    same = len(ref) == len(out) and all(a['t'] == b[0] and abs(a['res'] - b[1]) < 1e-9 and abs(a['c'] - b[4] / b[5]) < 1e-9 for a, b in zip(out, ref))
    return '%s-S%d' % (tf, i), dict(tf=tf, idx=i, name=src['name'], exitR=crooks.exit_r(src['cfg']), cfg=dict(src['cfg']), trades=out,
                                    check=dict(engine=len(out), stored=len(ref), identical=same))


if __name__ == '__main__':
    jobs = [(tf, i) for tf in SEL for i in SEL[tf]]
    with mp.Pool(4) as pool: R = pool.map(collect, jobs, chunksize=1)
    D = dict(R)
    pickle.dump(D, open(S + '/mcej/ars_trades.pkl', 'wb'))
    for k, v in D.items():
        tr = v['trades']; cross = sum(1 for x in tr if (x['t'].year, x['t'].month) != (x['tx'].year, x['tx'].month))
        print('%-7s %-38s exitR %.2f | engine %d stored %d identical %s | first %s last exit %s | trades crossing a month end %d' % (
            k, v['name'], v['exitR'], v['check']['engine'], v['check']['stored'], v['check']['identical'], tr[0]['t'], tr[-1]['tx'], cross))
