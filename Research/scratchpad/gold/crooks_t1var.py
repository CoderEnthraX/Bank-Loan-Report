"""Crooks TP1-rule stop variants on gold (final exit TP1). Every variant keeps the TP1 rule's size, so the half closed at TP1 always banks
the whole recovery amount T and the rest runs to TP2 with its stop at the entry (from the next bar); only the stop before TP1 differs:
  tight   stop at TP1/2 - 1.5 x costs (0.3R): the current TP1 rule, a stop-out loses T
  k0.45   stop at 0.45R            k0.6  stop at 0.6R          wide  the normal stop (1R = the engine's stop)
  fill    normal stop on the fill bar, the tight stop from the next bar (a fill-bar close past it exits at the next open)
  user    normal stop until a bar closes in profit, then the tight stop (the user's idea)
  userBE  normal stop until a bar closes in profit, then the entry (breakeven)
  plain   no TP1 rule: whole position T / TP1 R, normal stop, the engine's TP1 exit (the strategy with the checkbox off)
Results in multiples of T per recovery trade, then the money rules (crooks_tp1.simulate, Crooks C keeps a leftover) per variant, each
half, and 200 random orders. TradingView fill rules as crooks_tp1.special. Output: crooks_t1var.pkl + crooks_t1var.txt."""
import sys, math, pickle, random, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import crooks_tp1 as K
TFS = K.TFS
VARS = ['tight', 'k0.45', 'k0.6', 'wide', 'fill', 'user', 'userBE']
def replay(P, x, tp1R, tp2R, var):
    """(pnl per $1 of T, exit bar, how it ended) of the TP1-rule trade with stop variant var, or None if the geometry is impossible"""
    O, H, L, C = P['O'], P['H'], P['L'], P['C']; mt = P['mt']; tol = mt * 0.001; n = len(O)
    d = x['dir']; E = x['entry']; R1 = d * (E - x['stop']); f = x['fill']; c = P['SP'][f] / R1
    dR0 = tp1R / 2.0 - 1.5 * c
    dpx = math.floor(dR0 * R1 / mt + 1e-9) * mt
    if dpx < mt - 1e-12 or tp1R - c <= 0: return None
    dR0 = dpx / R1; Pz = 1.0 / (dR0 + c); half = 0.5 * Pz
    t1 = E + d * tp1R * R1; t2 = E + d * tp2R * R1
    mv = lambda px: d * (px - E) / R1
    adv = lambda b: L[b] if d > 0 else H[b]
    fav = lambda b: H[b] if d > 0 else L[b]
    hits = lambda px, lvl: d * (px - lvl) >= -tol
    crosses = lambda px, lvl: d * (lvl - px) >= -tol
    favFirst = lambda b: (abs(H[b] - O[b]) < abs(O[b] - L[b])) == (d > 0)
    s = {'tight': dR0, 'k0.45': 0.45, 'k0.6': 0.6, 'wide': 1.0, 'fill': 1.0, 'user': 1.0, 'userBE': 1.0}[var]
    stp = lambda s: E - d * s * R1
    def after_close(b, s):
        """the stop for the next bar, decided at the close of bar b (the script runs on bar closes)"""
        if var == 'fill' and b == f: return min(s, dR0)
        if var == 'user' and mv(C[b]) > 0: return min(s, dR0)
        if var == 'userBE' and mv(C[b]) > 0: return min(s, 0.0)
        return s
    stop = stp(s)
    if crosses(adv(f), stop): return (-Pz * (s + c), f, 'stop on the fill bar')
    s = after_close(f, s); stop = stp(s)
    b = f + 1; got1 = None
    while b < n:
        if crosses(O[b], stop): return (Pz * (mv(O[b]) - c), b, 'stop (gap)')
        if hits(O[b], t1):
            p1 = half * (mv(O[b]) - c)
            if hits(O[b], t2): return (p1 + half * (mv(O[b]) - c), b, 'TP1 + TP2 (gap)')
            got1 = (p1, b); s_hit = crosses(adv(b), stop); t2_hit = hits(fav(b), t2)
            if t2_hit and (not s_hit or favFirst(b)): return (p1 + half * (tp2R - c), b, 'TP1 + TP2')
            if s_hit: return (p1 + half * (-s - c), b, 'TP1, rest stopped the same bar')
            break
        s_hit = crosses(adv(b), stop); t1_hit = hits(fav(b), t1)
        if s_hit and (not t1_hit or not favFirst(b)): return (-Pz * (s + c), b, 'stop')
        if t1_hit:
            p1 = half * (tp1R - c)
            if hits(fav(b), t2): return (p1 + half * (tp2R - c), b, 'TP1 + TP2')
            if s_hit: return (p1 + half * (-s - c), b, 'TP1, rest stopped the same bar')
            got1 = (p1, b); break
        s = after_close(b, s); stop = stp(s)
        b += 1
    if got1 is None: return (Pz * (mv(C[n - 1]) - c), n - 1, 'open at the end')
    p1, b1 = got1; b = b1 + 1
    while b < n:
        if crosses(O[b], E): return (p1 + half * (mv(O[b]) - c), b, 'TP1, rest at entry (gap)')
        if hits(O[b], t2): return (p1 + half * (mv(O[b]) - c), b, 'TP1 + TP2 (gap)')
        be = crosses(adv(b), E); tp = hits(fav(b), t2)
        if tp and (not be or favFirst(b)): return (p1 + half * (tp2R - c), b, 'TP1 + TP2')
        if be: return (p1 + half * (-c), b, 'TP1, rest at entry')
        b += 1
    return (p1 + half * (mv(C[n - 1]) - c), n - 1, 'open at the end')
def trades(arg):
    tf, name, cfg = arg
    import geng, ref_gs
    ref_gs.eprep = geng.ref_g.eprep; geng.ref_g = ref_gs
    o = dict(cfg); o.pop('p1', None)
    vw = o.get('vwAnchorG', 'session'); src = o.get('vwSrcG', 'hlc3')
    P = geng.prepare(tf, vw, src); geng._CUR['vw'] = vw; geng._CUR['src'] = src
    o2 = {k: v for k, v in o.items() if k not in ('vwAnchorG', 'vwSrcG')}
    p = dict(ref_gs.IN); p.update(o2); assert p['exitAt'] == 1
    tp1R, tp2R = p['tp1R'], p['tp2R']
    out = []
    for x in ref_gs.run(tf, o2):
        if x['exit'] is None or x['ghost']: continue
        R1 = x['dir'] * (x['entry'] - x['stop'])
        y = dict(t=P['T'][x['fill']], arm=x['arm'], fill=x['fill'], exit=x['exit'], res=x['res'], c=P['SP'][x['fill']] / R1, R1=R1)
        y['v'] = {v: replay(P, x, tp1R, tp2R, v) for v in VARS}
        c = y['c']; d0 = tp1R / 2.0 - 1.5 * c                   # stop-out loss at the first stop, in T (the hard cap must cover it)
        y['m'] = {v: ((d0 if v == 'tight' else S0[v]) + c) / (d0 + c) for v in VARS}
        out.append(y)
    return tf, name, cfg, tp1R, tp2R, out
S0 = {'k0.45': 0.45, 'k0.6': 0.6, 'wide': 1.0, 'fill': 1.0, 'user': 1.0, 'userBE': 1.0}
def sim(tr, v, mode, tp1R, base=50.0, cap=0.0, act='clamp', start=10000.0, skips=True):
    """Off / Crooks A / Crooks C (C keeps a leftover) with variant v on the recovery trades; the hard cap limits the stop-out loss at the
    trade's first stop (T x loss multiple), like the strategy's cap (Start again = new cycle at the base, Clamp = smaller T)"""
    eq = start; peak = start; maxDD = maxDDp = 0.0; net = 0.0; crL = 0.0; crN = 0; crW = False; busy = -1; ruined = False; n = 0; maxLoss = 0.0
    for x in tr:
        if skips and x['arm'] < busy: continue
        rec = mode != 'Off' and ((mode == 'Crooks A' and crN >= 2 and crN % 2 == 0) or (mode == 'Crooks C' and crW and crL > 0))
        sp = x['v'][v] if (rec and v != 'plain') else None
        if sp is not None: r = max(base, crL); m = x['m'][v]
        elif rec: r = max(base, crL / tp1R); m = 1.0
        else: r = base; m = 1.0
        if cap > 0 and r * m > cap:
            if act == 'reset': crL = 0.0; crN = 0; crW = False; rec = False; sp = None; r = min(base, cap); m = 1.0
            else: r = cap / m
        if sp is not None: pnl = r * sp[0]; busy = sp[1]
        else: pnl = r * (x['res'] - x['c']) / (1.0 + x['c']); busy = -1
        maxLoss = max(maxLoss, r * m); n += 1
        eq += pnl; net += pnl; peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if crL < 0.01 or (mode == 'Crooks A' and win and rec): crL = 0.0; crN = 0
        else: crN += 1
        crW = win
    return dict(net=net, maxDD=maxDD, maxDDpct=maxDDp, ruined=ruined, trades=n, maxLoss=maxLoss)
RULES = [('Crooks C', 0.0, 'clamp'), ('Crooks C', 500.0, 'reset'), ('Crooks C', 500.0, 'clamp'), ('Crooks A', 0.0, 'clamp'), ('Crooks A', 500.0, 'reset')]
def money(arg):
    tf, name, cfg, tp1R, tp2R, tr = arg
    res = {}
    rng = random.Random(11 + TFS.index(tf)); orders = []
    idx = list(range(len(tr)))
    for _ in range(200):
        q = list(idx); rng.shuffle(q); orders.append(q)
    off = dict(all=sim(tr, 'plain', 'Off', tp1R))
    # check: the tight variant and plain equal crooks_tp1.simulate (the tight stop-out loses exactly T, so both caps act the same)
    for m, c, a in RULES:
        for v in ('tight', 'plain'):
            mine = sim(tr, v, m, tp1R, cap=c, act=a)['net']
            ref = K.simulate([dict(x, sp=(x['v']['tight'] if v == 'tight' else None)) for x in tr], m, cap=c, capAction=a, tp1rule=(v == 'tight'), exitR=tp1R)['net']
            assert abs(mine - ref) <= 1e-6 * max(1.0, abs(ref)), (tf, name, m, c, a, v, mine, ref)
    A = [x for x in tr if x['t'].year <= 2023]; B = [x for x in tr if x['t'].year >= 2024]
    for v in ['plain'] + VARS:
        for m, c, a in RULES:
            kw = dict(mode=m, tp1R=tp1R, cap=c, act=a)
            r = dict(all=sim(tr, v, **kw), A=sim(A, v, **kw), B=sim(B, v, **kw))
            if (m, c, a) in (('Crooks C', 500.0, 'reset'), ('Crooks C', 0.0, 'clamp'), ('Crooks A', 500.0, 'reset')):
                sims = [sim([tr[i] for i in q], v, skips=False, **kw) for q in orders]
                nets = sorted(z['net'] for z in sims); dds = sorted(z['maxDDpct'] for z in sims)
                r['mc'] = dict(med=nets[len(nets) // 2], p5=nets[int(0.05 * len(nets))], dd95=dds[int(0.95 * len(dds))], ruin=sum(1 for z in sims if z['ruined']) / len(sims))
            res[(v, m, c, a)] = r
    # per-trade outcomes in T (every trade as if it were a recovery trade)
    stats = {}
    for v in ['plain'] + VARS:
        if v == 'plain': o = [(x['res'] - x['c']) / ((1.0 + x['c']) * tp1R) for x in tr]; kinds = None
        else: o = [x['v'][v][0] for x in tr if x['v'][v] is not None]; kinds = [x['v'][v][2] for x in tr if x['v'][v] is not None]
        n = len(o)
        stats[v] = dict(n=n, E=sum(o) / n, loss=sum(1 for z in o if z < 0) / n, avgLoss=sum(z for z in o if z < 0) / max(1, sum(1 for z in o if z < 0)), worst=min(o),
                        tp1=(sum(1 for k in kinds if 'TP1' in k) / n) if kinds else sum(1 for z in o if z > 0) / n,
                        tp2=(sum(1 for k in kinds if 'TP2' in k) / n) if kinds else 0.0)
    return tf, name, dict(cfg=cfg, tp1R=tp1R, tp2R=tp2R, n=len(tr), off=off, res=res, stats=stats)
if __name__ == '__main__':
    D = pickle.load(open(S + '/gold/crooks_tp1.pkl', 'rb'))
    jobs = sorted([(tf, nm, d['cfg']) for (tf, nm), d in D.items()], key=lambda j: TFS.index(j[0]))
    with mp.Pool(4) as pool:
        T = pool.map(trades, jobs)
        R = pool.map(money, T)
    out = {(tf, nm): d for tf, nm, d in R}
    pickle.dump(out, open(S + '/gold/crooks_t1var.pkl', 'wb'))
    L = []
    for (tf, nm), d in out.items():
        L.append('\n%s | %s | %d trades | fixed $50: net %+.0f' % (tf, nm, d['n'], d['off']['all']['net']))
        for v in ['plain'] + VARS:
            s = d['stats'][v]; r = d['res'][(v, 'Crooks C', 500.0, 'reset')]; u = d['res'][(v, 'Crooks C', 0.0, 'clamp')]
            L.append('   %-7s per recovery trade: %+.3f T | loss %4.1f%% (avg %+.2f T, worst %+.2f T) TP1 %4.1f%% TP2 %4.1f%% | C $500 start again: net %+8.0f DD %3.0f%% 21-23 %+7.0f 24-26 %+7.0f median %+7.0f | C no cap: net %+8.0f %s blown %3.0f%% of orders' % (
                v, s['E'], 100 * s['loss'], s['avgLoss'], s['worst'], 100 * s['tp1'], 100 * s['tp2'], r['all']['net'], 100 * r['all']['maxDDpct'], r['A']['net'], r['B']['net'], r['mc']['med'],
                u['all']['net'], 'BLOWN' if u['all']['ruined'] else 'ok', 100 * u['mc']['ruin']))
    open(S + '/gold/crooks_t1var.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
