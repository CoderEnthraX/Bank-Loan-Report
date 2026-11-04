"""Crooks recovery trades with the final target at TP1 ("TP1 rule"), on bars, like the strategy in TradingView.
A recovery trade (trades 3, 5, 7 ... of a Crooks cycle) banks the recovery amount T at TP1 with HALF of a double-size position and runs the
other half to TP2; its stop is moved in so that a stop-out loses exactly T:
   T = max(base, loss to win back) (Crooks A) or max(base, loss / split) (Crooks B), after the hard cap
   stop distance (R) = TP1 / 2 - 1.5 x spread (R), rounded to the tick toward the entry; position = T / (stop distance + spread) per 1R
   after TP1 the rest's stop moves to the entry (from the next bar, when the script runs); the rest exits at TP2 or at the entry
   impossible geometry (spread >= TP1 / 3, or the stop closer than one tick) -> the normal Crooks trade (risk max(base, T / TP1 R), engine exit)
TradingView emulator rules (as build/emsim.py): orders act from the next bar, attached exits are live on the fill bar, the targets only after the
fill bar, limits fill on touch (gap -> at the open), stops when crossed (gap -> at the open), a bar touching both: O-H-L-C if the high is
closer to the open, else O-L-H-C. While a TP1-rule trade runs past the indicator's exit, the engine's next signals are skipped (one trade at a time).
Output: crooks_tp1.pkl + crooks_tp1.txt."""
import sys, math, pickle, random, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import greedy
TFS = ('M1', 'M5', 'M15', 'H1')
def special(P, x, tp1R, tp2R):
    """the TP1-rule trade of engine trade x on the bars: (pnl per $1 of T, exit bar, how it ended) or None if the geometry is impossible"""
    O, H, L, C = P['O'], P['H'], P['L'], P['C']; mt = P['mt']; tol = mt * 0.001; n = len(O)
    d = x['dir']; E = x['entry']; R1 = d * (E - x['stop']); f = x['fill']; c = P['SP'][f] / R1
    dR = tp1R / 2.0 - 1.5 * c
    dpx = math.floor(dR * R1 / mt + 1e-9) * mt
    if dpx < mt - 1e-12 or tp1R - c <= 0: return None
    dR = dpx / R1; Pz = 1.0 / (dR + c); half = 0.5 * Pz
    stop = E - d * dpx; t1 = E + d * tp1R * R1; t2 = E + d * tp2R * R1
    mv = lambda px: d * (px - E) / R1                                  # move from the entry in R
    adv = lambda b: L[b] if d > 0 else H[b]                            # adverse extreme of bar b
    fav = lambda b: H[b] if d > 0 else L[b]
    hits = lambda px, lvl: d * (px - lvl) >= -tol                      # favourable side reached lvl
    crosses = lambda px, lvl: d * (lvl - px) >= -tol                   # adverse side reached lvl
    favFirst = lambda b: (abs(H[b] - O[b]) < abs(O[b] - L[b])) == (d > 0)
    # fill bar: only the (attached) stop is live
    if crosses(adv(f), stop): return (-Pz * (dR + c), f, 'stop on the fill bar')
    b = f + 1; got1 = None
    while b < n:                                                       # stage 1: tight stop, TP1 (half) and TP2 (rest)
        if crosses(O[b], stop): return (Pz * (mv(O[b]) - c), b, 'stop (gap)')
        if hits(O[b], t1):
            p1 = half * (mv(O[b]) - c)
            if hits(O[b], t2): return (p1 + half * (mv(O[b]) - c), b, 'TP1 + TP2 (gap)')
            got1 = (p1, b); s_hit = crosses(adv(b), stop); t2_hit = hits(fav(b), t2)
            if t2_hit and (not s_hit or favFirst(b)): return (p1 + half * (tp2R - c), b, 'TP1 + TP2')
            if s_hit: return (p1 + half * (-dR - c), b, 'TP1, rest stopped the same bar')
            break
        s_hit = crosses(adv(b), stop); t1_hit = hits(fav(b), t1)
        if s_hit and (not t1_hit or not favFirst(b)): return (-Pz * (dR + c), b, 'stop')
        if t1_hit:
            p1 = half * (tp1R - c)
            if hits(fav(b), t2): return (p1 + half * (tp2R - c), b, 'TP1 + TP2')
            if s_hit: return (p1 + half * (-dR - c), b, 'TP1, rest stopped the same bar')
            got1 = (p1, b); break
        b += 1
    if got1 is None: return (Pz * (mv(C[n - 1]) - c), n - 1, 'open at the end')
    p1, b1 = got1; b = b1 + 1
    while b < n:                                                       # stage 2: the rest, stop at the entry, TP2
        if crosses(O[b], E): return (p1 + half * (mv(O[b]) - c), b, 'TP1, rest at entry (gap)')
        if hits(O[b], t2): return (p1 + half * (mv(O[b]) - c), b, 'TP1 + TP2 (gap)')
        be = crosses(adv(b), E); tp = hits(fav(b), t2)
        if tp and (not be or favFirst(b)): return (p1 + half * (tp2R - c), b, 'TP1 + TP2')
        if be: return (p1 + half * (-c), b, 'TP1, rest at entry')
        b += 1
    return (p1 + half * (mv(C[n - 1]) - c), n - 1, 'open at the end')
def trades_for(arg):
    """engine trades of one setting (exit at TP1) with bar indices, spread, result and the TP1-rule outcome"""
    tf, cfg = arg
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
        out.append(dict(t=P['T'][x['fill']], arm=x['arm'], fill=x['fill'], exit=x['exit'], res=x['res'], c=P['SP'][x['fill']] / R1, sp=special(P, x, tp1R, tp2R),
                        R1=R1, spx=P['SP'][x['fill']]))
    return tf, cfg, out, tp1R, tp2R
def simulate(tr, mode, base=50.0, cap=0.0, capAction='clamp', cSplit=3, tp1rule=True, exitR=0.6, start=10000.0, skips=True, trace=None):
    """Off / Crooks A / B / C / D on the trades of an exit-at-TP1 setting. tp1rule=False = the plain Crooks rule (risk max(base, T / TP1 R), engine exit)."""
    eq = start; peak = start; maxDD = maxDDp = 0.0; net = 0.0; gp = gl = 0.0; n = 0; nsk = 0; nsp = nfb = 0; sumRisk = maxRisk = 0.0
    crL = 0.0; crN = 0; crW = False; busy = -1; ruined = capStop = False; ruinAt = None; lossRun = worstRun = 0.0; kinds = {}
    for k, x in enumerate(tr):
        if skips and x['arm'] < busy: nsk += 1; continue                # still in a TP1-rule trade: this signal is skipped
        rec = ((mode in ('Crooks A', 'Crooks B') and crN >= 2 and crN % 2 == 0) or (mode == 'Crooks C' and crW and crL > 0)
               or (mode == 'Crooks D' and crN >= 2 and (crN - 2) % 3 == 0))
        X = crL / (cSplit if mode == 'Crooks B' else 1)
        sp = rec and tp1rule and x['sp'] is not None
        r = max(base, X) if sp else max(base, X / exitR) if rec else base
        if cap > 0 and r > cap:
            if capAction == 'stop':
                capStop = True
                if trace is not None: trace.append((x, r, None, sp))          # the signal that stopped trading
                break
            elif capAction == 'reset': crL = 0.0; crN = 0; crW = False; rec = sp = False; r = min(base, cap)
            else: r = cap
        if sp:
            pnl = r * x['sp'][0]; busy = x['sp'][1]; nsp += 1; kinds[x['sp'][2]] = kinds.get(x['sp'][2], 0) + 1
        else:
            pnl = r * (x['res'] - x['c']) / (1.0 + x['c']); busy = -1; nfb += 1 if (rec and tp1rule) else 0
        n += 1; sumRisk += r; maxRisk = max(maxRisk, r)
        if trace is not None: trace.append((x, r, pnl, sp))
        eq += pnl; net += pnl; gp += max(pnl, 0.0); gl += max(-pnl, 0.0)
        lossRun = lossRun + pnl if pnl < 0 else 0.0; worstRun = min(worstRun, lossRun)
        peak = max(peak, eq); dd = peak - eq; maxDD = max(maxDD, dd); maxDDp = max(maxDDp, dd / peak)
        if eq <= 0: ruined = True; ruinAt = k; break
        win = pnl > 0
        crL = max(0.0, crL - pnl)
        if crL < 0.01 or (mode in ('Crooks A', 'Crooks D') and win and rec): crL = 0.0; crN = 0      # C keeps a leftover
        else: crN += 1
        crW = win
    return dict(mode=mode, trades=n, skipped=nsk, tp1trades=nsp, fallback=nfb, kinds=kinds, avgRisk=sumRisk / n if n else 0.0, maxRisk=maxRisk, net=net, end=eq,
                maxDD=maxDD, maxDDpct=maxDDp, ruined=ruined, ruinAt=ruinAt, capStopped=capStop, pf=gp / gl if gl > 0 else float('inf'), worstRun=-worstRun,
                ratio=net / maxDD if maxDD > 0 else 0.0)
VARIANTS = ([('Off', 3, 0.0, 'clamp', False)] +
            [(m, s, c, a, rule) for rule in (True, False) for m, s in (('Crooks A', 3), ('Crooks B', 2), ('Crooks B', 3), ('Crooks B', 5))
             for c, a in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'))])
def study(arg):
    tf, name, cfg, tr, tp1R, tp2R = arg
    A = [x for x in tr if x['t'].year <= 2023]; B = [x for x in tr if x['t'].year >= 2024]
    rows = []
    for m, s, c, a, rule in VARIANTS:
        kw = dict(mode=m, cap=c, capAction=a, cSplit=s, tp1rule=rule, exitR=tp1R)
        rows.append(dict(mode=m, split=s, cap=c, act=a, tp1rule=rule, all=simulate(tr, **kw), A=simulate(A, **kw), B=simulate(B, **kw)))
    rng = random.Random(7 + TFS.index(tf)); mc = {}
    orders = []
    for _ in range(300):
        t = list(tr); rng.shuffle(t); orders.append(t)
    for m, s, c, a, rule in VARIANTS:
        if c and a == 'clamp' and m != 'Off': continue
        sims = [simulate(t, m, cap=c, capAction=a, cSplit=s, tp1rule=rule, exitR=tp1R, skips=False) for t in orders]
        nets = sorted(q['net'] for q in sims); dds = sorted(q['maxDDpct'] for q in sims)
        mc[(m, s, c, a, rule)] = dict(med=nets[len(nets) // 2], p5=nets[int(0.05 * len(nets))], dd95=dds[int(0.95 * len(dds))],
                                     ruin=sum(1 for q in sims if q['ruined']) / len(sims), dd40=sum(1 for q in dds if q > 0.40) / len(sims))
    nsp = [x for x in tr if x['sp'] is not None]
    geo = dict(n=len(tr), possible=len(nsp) / len(tr) if tr else 0.0, avgPnlT=sum(x['sp'][0] for x in nsp) / len(nsp) if nsp else 0.0,
               win=sum(1 for x in nsp if x['sp'][0] > 0) / len(nsp) if nsp else 0.0, E=sum(x['res'] - x['c'] for x in tr) / len(tr) if tr else 0.0)
    kinds = {}
    for x in nsp: kinds[x['sp'][2]] = kinds.get(x['sp'][2], 0) + 1
    geo['kinds'] = kinds
    return tf, name, dict(cfg=cfg, tp1R=tp1R, tp2R=tp2R, geo=geo, rows=rows, mc=mc, trades=tr)
def label(x):
    return '%-9s%s%s%s' % (x['mode'], ' split %d' % x['split'] if x['mode'] == 'Crooks B' else '', ' cap $%d %s' % (x['cap'], 'start again' if x['act'] == 'reset' else x['act']) if x['cap'] else '',
                           '' if x['mode'] == 'Off' else (' | TP1 rule' if x['tp1rule'] else ' | plain'))
if __name__ == '__main__':
    import pickcfg
    jobs = []
    for tf in TFS:
        F = pickle.load(open(S + '/gold/final_%s.pkl' % tf, 'rb'))
        for prof, nm in (('default', 'Default settings'), ('profit', 'Best settings, exit TP1'), ('streak', 'Low-streak settings, exit TP1')):
            jobs.append((tf, nm, F['exits'][(prof, 1)][0]))
        Pp, minA, minB = pickcfg.load(tf)
        ok = sorted([(c, m) for c, m in Pp.values() if c.get('exitAt', 4) == 1 and pickcfg.ok(m, minA, minB)], key=lambda r: -pickcfg.robust(r[1]))
        for k, (c, m) in enumerate(ok[:2]): jobs.append((tf, 'Best TP1-exit settings found #%d' % (k + 1), greedy.norm(dict(c))))
    with mp.Pool(4) as pool:
        T = pool.map(trades_for, [(tf, cfg) for tf, nm, cfg in jobs])
        res = pool.map(study, [(tf, nm, cfg, tr, a, b) for (tf, nm, _), (_, cfg, tr, a, b) in zip(jobs, T)])
    out = {(tf, nm): d for tf, nm, d in res}
    pickle.dump(out, open(S + '/gold/crooks_tp1.pkl', 'wb'))
    L = []
    for (tf, nm), d in out.items():
        g = d['geo']
        L.append('\n%s | %s | %d trades, R/trade after spread %+.3f | TP1 rule possible on %.0f%% of trades; as a TP1-rule trade: %.0f%% end in profit, average %+.2f T | %s' % (
            tf, nm, g['n'], g['E'], 100 * g['possible'], 100 * g['win'], g['avgPnlT'], ', '.join('%s %d' % kv for kv in sorted(g['kinds'].items(), key=lambda kv: -kv[1]))))
        for x in d['rows']:
            a, A, B = x['all'], x['A'], x['B']; q = d['mc'].get((x['mode'], x['split'], x['cap'], x['act'], x['tp1rule']))
            L.append('   %-46s | net %+9.0f DD %3.0f%% maxRisk $%5.0f ratio %5.2f %s | trades %4d, TP1-rule %3d, fallback %3d, skipped %3d | 21-23 %+7.0f | 24-26 %+7.0f%s' % (
                label(x), a['net'], 100 * a['maxDDpct'], a['maxRisk'], a['ratio'], 'BLOWN' if a['ruined'] else 'ok   ', a['trades'], a['tp1trades'], a['fallback'], a['skipped'],
                A['net'], B['net'], (' | random: median %+7.0f, 95%% fall < %3.0f%%, blown %4.1f%%' % (q['med'], 100 * q['dd95'], 100 * q['ruin'])) if q else ''))
    open(S + '/gold/crooks_tp1.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
