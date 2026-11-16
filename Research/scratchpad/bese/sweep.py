"""BE trigger x salvage trigger sweep on the Auction Retest research engine (bese/ref_gbe.py), gold FxPro 2021-2026, every catalogue strategy
without a partial close (M1 S1-S4, M5 S1-S4, M15 S1/S3/S6/S7/S8/S9, H1 S1/S3/S6/S7/S8) and the user's settings on M5 (filters off / on x final
exit TP1-TP4). Costs 0.23 per oz (spread 0.16 + $7 a lot): net R of a trade = (R - c) / (1 + c), c = 0.23 / stop distance.
Per job (base, BE, salvage): trades, net R in 2021-23 (choice) and 2024-26 (test), stop-outs, 0R exits, longest losing run, deepest fall (R),
median stop distance (% of price). Resumable: one JSON line per finished job in bese/sweep.jsonl. Run: python3 sweep.py [workers]"""
import sys, os, json, multiprocessing as mp, datetime as dt
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/bese'); sys.path.insert(0, S + '/gold'); sys.path.insert(0, S + '/build')
OUT = S + '/bese/sweep.jsonl'
COST = 0.23
BE = (None, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5)
SV = (None, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
BE_M1 = (None, 0.3, 0.5, 0.8, 1.25)
SV_M1 = (None, 0.4, 0.6, 0.8)
USER_ENG = dict(halfCap=True, maxFills=10, entryPct=25.0, mv3R=0.0, noChaseSig=2.0, chopMax=13.5, kzShift=0, kzAuto=True)
USER_ON = dict(dayOn=True, days=(False, True, True, True, False, False, False), hoursOn=True, hoursSess=(600, 2300), kzOn=True, kz=(True, True, True, False))
SPLIT = dt.datetime(2024, 1, 1)


def bases():
    import crooks
    out = []
    for tf in ('M1', 'M5', 'M15', 'H1'):
        for i, d in enumerate(crooks.sources(tf)):
            if i == 0 or d['cfg'].get('p1'): continue
            out.append(dict(key='%s-S%d' % (tf, i), tf=tf, kind='catalogue', cfg=dict(d['cfg'])))
    for su in ('off', 'on'):
        for ex in (1, 2, 3, 4):
            out.append(dict(key='M5-you-%s-TP%d' % (su, ex), tf='M5', kind='your settings', cfg=dict(USER_ENG, exitAt=ex, **(USER_ON if su == 'on' else {}))))
    return out


def jobs():
    import greedy
    J = []
    for b in bases():
        p = dict(greedy.defaults()); p.update(b['cfg'])
        exitR = (p['tp1R'], p['tp2R'], p['tp3R'], p['tp4R'])[p['exitAt'] - 1]
        BEs, SVs = (BE_M1, SV_M1) if b['tf'] == 'M1' else (BE, SV)
        for be in BEs:
            if be is not None and be >= exitR: continue            # the trade is out at the target before the trigger
            for sv in SVs:
                J.append(dict(b, be=be, sv=sv, exitR=exitR))
    order = {'M1': 0, 'M5': 1, 'M15': 2, 'H1': 3}
    return sorted(J, key=lambda j: order[j['tf']])


def jid(j): return '%s|%s|%s' % (j['key'], j['be'], j['sv'])


def work(j):
    import geng, ref_gbe
    ref_gbe.eprep = geng.ref_g.eprep
    o = {k: v for k, v in j['cfg'].items() if k != 'p1'}
    vw = o.pop('vwAnchorG', 'session'); src = o.pop('vwSrcG', 'hlc3')
    P = geng.prepare(j['tf'], vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    if j['be'] is not None: o.update(beOn=True, beR=j['be'])
    if j['sv'] is not None: o.update(svOn=True, svR=j['sv'])
    tr = [x for x in ref_gbe.run(j['tf'], o) if not x['ghost'] and x['exit'] is not None]
    T = P['T']; r = dict(id=jid(j), key=j['key'], tf=j['tf'], kind=j['kind'], be=j['be'], sv=j['sv'], exitR=j['exitR'])
    for per in ('in', 'out'): r[per] = dict(n=0, net=0.0, win=0, sl=0, zero=0, be=0, sv=0)
    eq = pk = dd = 0.0; run = mrun = 0; sd = []
    for x in tr:
        risk = x['dir'] * (x['entry'] - x['stop']); c = COST / risk; net = (x['res'] - c) / (1.0 + c)
        a = r['in' if T[x['fill']] < SPLIT else 'out']
        a['n'] += 1; a['net'] += net; a['win'] += net > 0; a['sl'] += x['res'] <= -0.999; a['zero'] += abs(x['res']) < 1e-9
        a['be'] += x.get('trig') == 'be'; a['sv'] += x.get('trig') == 'sv'
        eq += net; pk = max(pk, eq); dd = max(dd, pk - eq)
        run = run + 1 if net < 0 else 0; mrun = max(mrun, run)
        sd.append(100.0 * risk / x['entry'])
    sd.sort()
    r.update(dd=dd, lrun=mrun, sdPct=sd[len(sd) // 2] if sd else None)
    return r


if __name__ == '__main__':
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    done = set()
    if os.path.exists(OUT):
        for ln in open(OUT): done.add(json.loads(ln)['id'])
    todo = [j for j in jobs() if jid(j) not in done]
    print('jobs', len(todo), 'to run,', len(done), 'done', flush=True)
    with mp.Pool(W, maxtasksperchild=40) as pool, open(OUT, 'a') as f:
        for k, r in enumerate(pool.imap_unordered(work, todo, chunksize=1), 1):
            f.write(json.dumps(r) + '\n'); f.flush()
            if k % 50 == 0: print(k, 'of', len(todo), flush=True)
    print('finished', flush=True)
