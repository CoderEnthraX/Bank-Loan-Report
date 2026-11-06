"""v3.8 Crooks TP1 rule on gold: the part p closed at TP1 (30 / 50 / 70 %) and the rule with any final exit (TP1, or TP2 with "works with any final exit").
The size is the one whose TP1 part alone banks the recovery amount T: stop distance d = p x TP1 - (1 + p) x costs (R, on the tick grid toward the entry),
position = T / (d + costs) per 1R; after TP1 the rest's stop moves to the entry (from the next bar) and the rest closes at TP2. Stop before TP1:
  tight  at d (a stop-out loses T)        wide  the normal stop (1R, the engine's stop): a stop-out loses (1 + c) / (d + c) x T
The settings are the 14 exit-TP1 settings of crooks_tp1.pkl, each also run with Final Exit TP2 (the engine's trades end at TP2; the TP1-rule trade is the
same path). Fill rules as crooks_tp1.special (TradingView emulator). Checks: p = 0.5 replays equal crooks_t1var.replay (tight, wide) and crooks_tp1.special.
Money: crooks_tp1.simulate (Crooks A / C, caps). Output: crooks_t1p.pkl (also the input of mq5check/rec/parity_tp1.py) + crooks_t1p.txt."""
import sys, math, pickle, random, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import crooks_tp1 as K
TFS = K.TFS
PTS = (0.3, 0.5, 0.7)
VARS = ('tight', 'wide')
def geom(P, x, tp1R, pt):
    """(d in R on the tick grid, cost c in R) of the TP1-rule trade, or None if the geometry is impossible"""
    mt = P['mt']; d = x['dir']; R1 = d * (x['entry'] - x['stop']); c = P['SP'][x['fill']] / R1
    dR = pt * tp1R - (1 + pt) * c
    dpx = math.floor(dR * R1 / mt + 1e-9) * mt
    if dpx < mt - 1e-12 or tp1R - c <= 0: return None
    return dpx / R1, c
def replay(P, x, tp1R, tp2R, var, pt):
    """(pnl per $1 of T, exit bar, how it ended) of the TP1-rule trade, or None if the geometry is impossible"""
    g = geom(P, x, tp1R, pt)
    if g is None: return None
    dR0, c = g
    O, H, L, C = P['O'], P['H'], P['L'], P['C']; mt = P['mt']; tol = mt * 0.001; n = len(O)
    d = x['dir']; E = x['entry']; R1 = d * (E - x['stop']); f = x['fill']
    Pz = 1.0 / (dR0 + c); a1 = pt * Pz; a2 = (1.0 - pt) * Pz          # the TP1 part and the rest
    t1 = E + d * tp1R * R1; t2 = E + d * tp2R * R1
    mv = lambda px: d * (px - E) / R1
    adv = lambda b: L[b] if d > 0 else H[b]
    fav = lambda b: H[b] if d > 0 else L[b]
    hits = lambda px, lvl: d * (px - lvl) >= -tol
    crosses = lambda px, lvl: d * (lvl - px) >= -tol
    favFirst = lambda b: (abs(H[b] - O[b]) < abs(O[b] - L[b])) == (d > 0)
    s = dR0 if var == 'tight' else 1.0
    stop = E - d * s * R1
    if crosses(adv(f), stop): return (-Pz * (s + c), f, 'stop on the fill bar')
    b = f + 1; got1 = None
    while b < n:
        if crosses(O[b], stop): return (Pz * (mv(O[b]) - c), b, 'stop (gap)')
        if hits(O[b], t1):
            p1 = a1 * (mv(O[b]) - c)
            if hits(O[b], t2): return (p1 + a2 * (mv(O[b]) - c), b, 'TP1 + TP2 (gap)')
            got1 = (p1, b); s_hit = crosses(adv(b), stop); t2_hit = hits(fav(b), t2)
            if t2_hit and (not s_hit or favFirst(b)): return (p1 + a2 * (tp2R - c), b, 'TP1 + TP2')
            if s_hit: return (p1 + a2 * (-s - c), b, 'TP1, rest stopped the same bar')
            break
        s_hit = crosses(adv(b), stop); t1_hit = hits(fav(b), t1)
        if s_hit and (not t1_hit or not favFirst(b)): return (-Pz * (s + c), b, 'stop')
        if t1_hit:
            p1 = a1 * (tp1R - c)
            if hits(fav(b), t2): return (p1 + a2 * (tp2R - c), b, 'TP1 + TP2')
            if s_hit: return (p1 + a2 * (-s - c), b, 'TP1, rest stopped the same bar')
            got1 = (p1, b); break
        b += 1
    if got1 is None: return (Pz * (mv(C[n - 1]) - c), n - 1, 'open at the end')
    p1, b1 = got1; b = b1 + 1
    while b < n:
        if crosses(O[b], E): return (p1 + a2 * (mv(O[b]) - c), b, 'TP1, rest at entry (gap)')
        if hits(O[b], t2): return (p1 + a2 * (mv(O[b]) - c), b, 'TP1 + TP2 (gap)')
        be = crosses(adv(b), E); tp = hits(fav(b), t2)
        if tp and (not be or favFirst(b)): return (p1 + a2 * (tp2R - c), b, 'TP1 + TP2')
        if be: return (p1 + a2 * (-c), b, 'TP1, rest at entry')
        b += 1
    return (p1 + a2 * (mv(C[n - 1]) - c), n - 1, 'open at the end')
def trades(arg):
    tf, name, cfg, exitAt = arg
    import geng, ref_gs, crooks_t1var as V
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    o = dict(cfg); o.pop('p1', None); o['exitAt'] = exitAt
    vw = o.get('vwAnchorG', 'session'); src = o.get('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    o2 = {k: v for k, v in o.items() if k not in ('vwAnchorG', 'vwSrcG')}
    p = dict(ref_gs.IN); p.update(o2)
    tp1R, tp2R = p['tp1R'], p['tp2R']; exitR = (tp1R, tp2R, p['tp3R'], p['tp4R'])[exitAt - 1]
    out = []; chk = 0
    for x in ref_gs.run(tf, o2):
        if x['exit'] is None or x['ghost']: continue
        R1 = x['dir'] * (x['entry'] - x['stop'])
        y = dict(t=P['T'][x['fill']], arm=x['arm'], fill=x['fill'], exit=x['exit'], res=x['res'], c=P['SP'][x['fill']] / R1, R1=R1, spx=P['SP'][x['fill']], v={}, m={})
        for pt in PTS:
            g = geom(P, x, tp1R, pt)
            for var in VARS:
                y['v'][(pt, var)] = replay(P, x, tp1R, tp2R, var, pt)
                y['m'][(pt, var)] = 1.0 if g is None else ((g[0] if var == 'tight' else 1.0) + g[1]) / (g[0] + g[1])   # stop-out loss at the first stop / T
        # the generalised replay at p = 0.5 is the old one
        assert y['v'][(0.5, 'tight')] == V.replay(P, x, tp1R, tp2R, 'tight') == K.special(P, x, tp1R, tp2R), (tf, name, x['arm'])
        assert y['v'][(0.5, 'wide')] == V.replay(P, x, tp1R, tp2R, 'wide'), (tf, name, x['arm'])
        chk += 1
        out.append(y)
    return tf, name, exitAt, dict(cfg=cfg, tp1R=tp1R, tp2R=tp2R, exitR=exitR, trades=out, checked=chk)
RULES = [('Crooks C', 0.0, 'clamp'), ('Crooks C', 500.0, 'reset'), ('Crooks C', 500.0, 'clamp'), ('Crooks A', 500.0, 'reset')]
def with_var(tr, key): return [dict(x, sp=x['v'][key], m=x['m'][key]) for x in tr]
def money(arg):
    tf, name, exitAt, d = arg
    tr = d['trades']; exitR = d['exitR']
    A = [x for x in tr if x['t'].year <= 2023]; B = [x for x in tr if x['t'].year >= 2024]
    rng = random.Random(23 + TFS.index(tf) + 7 * exitAt); idx = list(range(len(tr))); orders = []
    for _ in range(100):
        q = list(idx); rng.shuffle(q); orders.append(q)
    res = {}
    keys = [('plain', None)] + [(var, pt) for var in VARS for pt in PTS]
    for var, pt in keys:
        rule = var != 'plain'
        T = with_var(tr, (pt, var)) if rule else [dict(x, sp=None) for x in tr]
        TA = [x for x in T if x['t'].year <= 2023]; TB = [x for x in T if x['t'].year >= 2024]
        for m, c, a in RULES:
            kw = dict(mode=m, cap=c, capAction=a, tp1rule=rule, exitR=exitR)
            r = dict(all=K.simulate(T, **kw), A=K.simulate(TA, **kw), B=K.simulate(TB, **kw))
            if (m, c, a) == ('Crooks C', 500.0, 'reset'):
                sims = [K.simulate([T[i] for i in q], skips=False, **kw) for q in orders]
                nets = sorted(z['net'] for z in sims); dds = sorted(z['maxDDpct'] for z in sims)
                r['mc'] = dict(med=nets[len(nets) // 2], p5=nets[int(0.05 * len(nets))], dd95=dds[int(0.95 * len(dds))], ruin=sum(1 for z in sims if z['ruined']) / len(sims))
            res[(var, pt, m, c, a)] = r
    stats = {}
    for var, pt in keys:
        if var == 'plain': o = [(x['res'] - x['c']) / ((1.0 + x['c']) * exitR) for x in tr]; kinds = None
        else: o = [x['v'][(pt, var)][0] for x in tr if x['v'][(pt, var)] is not None]; kinds = [x['v'][(pt, var)][2] for x in tr if x['v'][(pt, var)] is not None]
        n = len(o)
        stats[(var, pt)] = dict(n=n, E=sum(o) / n, loss=sum(1 for z in o if z < 0) / n, avgLoss=sum(z for z in o if z < 0) / max(1, sum(1 for z in o if z < 0)), worst=min(o),
                                tp1=(sum(1 for k in kinds if 'TP1' in k) / n) if kinds else sum(1 for z in o if z > 0) / n,
                                tp2=(sum(1 for k in kinds if 'TP2' in k) / n) if kinds else 0.0)
    return tf, name, exitAt, dict(cfg=d['cfg'], n=len(tr), exitR=exitR, res=res, stats=stats)
if __name__ == '__main__':
    D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb'))
    jobs = sorted([(tf, nm, d['cfg'], ex) for (tf, nm), d in D.items() for ex in (1, 2)], key=lambda j: (-TFS.index(j[0]), j[3]))   # M1 last
    with mp.Pool(4) as pool:
        T = pool.map(trades, jobs, chunksize=1)
        pickle.dump({(tf, nm, ex): d for tf, nm, ex, d in T}, open(S + '/gold/crooks_t1p.pkl', 'wb'))
        print('replays checked against crooks_t1var / crooks_tp1 at p = 0.5:', sum(d['checked'] for _, _, _, d in T), 'trades', flush=True)
        R = pool.map(money, T, chunksize=1)
    out = {(tf, nm, ex): d for tf, nm, ex, d in R}
    pickle.dump(out, open(S + '/gold/crooks_t1p_money.pkl', 'wb'))
    L = []
    for (tf, nm, ex), d in sorted(out.items(), key=lambda kv: (TFS.index(kv[0][0]), kv[0][1], kv[0][2])):
        L.append('\n%s | %s | Final Exit TP%d%s | %d trades' % (tf, nm, ex, ' (TP1 rule: works with any final exit)' if ex != 1 else '', d['n']))
        for var, pt in [('plain', None)] + [(v, p) for v in VARS for p in PTS]:
            s = d['stats'][(var, pt)]; r = d['res'][(var, pt, 'Crooks C', 500.0, 'reset')]; u = d['res'][(var, pt, 'Crooks C', 0.0, 'clamp')]
            a = d['res'][(var, pt, 'Crooks A', 500.0, 'reset')]
            L.append('   %-11s per recovery trade %+.3f T | loss %4.1f%% (avg %+.2f T, worst %+.2f T) TP1 %4.1f%% TP2 %4.1f%% | C $500 start again: net %+8.0f DD %3.0f%% 21-23 %+7.0f 24-26 %+7.0f median %+7.0f (5%% %+7.0f, blown %2.0f%%) | C no cap: net %+9.0f %s | A $500 start again %+8.0f' % (
                'plain' if var == 'plain' else '%s %d%%' % (var, round(100 * pt)), s['E'], 100 * s['loss'], s['avgLoss'], s['worst'], 100 * s['tp1'], 100 * s['tp2'],
                r['all']['net'], 100 * r['all']['maxDDpct'], r['A']['net'], r['B']['net'], r['mc']['med'], r['mc']['p5'], 100 * r['mc']['ruin'], u['all']['net'], 'BLOWN' if u['all']['ruined'] else 'ok   ', a['all']['net']))
    open(S + '/gold/crooks_t1p.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
