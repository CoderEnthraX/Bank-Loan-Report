"""Strategy catalogue: for every timeframe, the profitable settings for each scenario (most profit, shortest losing streak, longest winning
streak, highest win rate, most trades, every year positive, smoothest, simplest, per session), re-run for full statistics.
Every pick passes the same rule as the main picks: profitable after spread in 2021-23 AND 2024-26, at least 4 of 6 years positive,
enough trades in both halves. Output: catalog_<TF>.pkl (checkpoint per timeframe). Usage: catalog.py [TF ...]"""
import sys, os, pickle, collections, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import pickcfg, labels, greedy, final, recovery as RC
SESS = {'Asia': ((True, False, False, False), (430, 1230)), 'London': ((False, True, False, False), (1230, 1630)),
        'New York': ((False, False, True, False), (1830, 2230)), 'London close': ((False, False, False, True), None)}
def nchg(c): return len(labels.rows(c))
def sessions(c):
    """sessions a setting can trade in: kill zones ticked and / or the trading-hours window; 'all' when neither is on"""
    out = None
    if c.get('kzOn'):
        out = {n for n, (m, _) in SESS.items() if any(a and b for a, b in zip(m, c.get('kz', (True,) * 4)))}
    if c.get('hoursOn'):
        h = {n for n, (_, w) in SESS.items() if w is not None and tuple(c.get('hoursSess', ())) == w}
        out = h if out is None else (out & h)
    return out or {'all'}
def unique(rows):
    """identical results (same trades, same net, same streak) counted once, keeping the version with the fewest changed settings"""
    u = {}
    for c, m in rows:
        k = (m['all']['n'], round(m['all']['net'], 6), m['all']['maxL'], m['all']['maxW'])
        if k not in u or nchg(c) < nchg(u[k][0]): u[k] = (c, m)
    return list(u.values())
def best(cands, key, simple=True):
    """highest key; among equal keys the best robust score; then (simple) the fewest changes within 10% of that score"""
    if not cands: return None
    top = max(key(r) for r in cands); q = [r for r in cands if key(r) == top]
    q.sort(key=lambda r: -pickcfg.robust(r[1]))
    if not simple: return q[0]
    b0 = pickcfg.robust(q[0][1]); near = [r for r in q if pickcfg.robust(r[1]) >= 0.9 * b0]
    return min(near, key=lambda r: (nchg(r[0]), -pickcfg.robust(r[1])))
def scenarios(tf):
    P, minA, minB = pickcfg.load(tf)
    U = unique([(c, m) for c, m in P.values() if pickcfg.ok(m, minA, minB)])
    if not U: return [], U
    prof = pickcfg.pick(tf, None, 1)[0][0]; floor = min(1.0, pickcfg.robust(prof[1]) / 3.0)
    F = [r for r in U if pickcfg.robust(r[1]) >= floor]
    rb = lambda r: pickcfg.robust(r[1])
    out = [('Most profit', 'Best R per trade after spread in both halves (ranked by the weaker half); the main recommendation.', prof),
           ('Shortest losing streak', 'The fewest losses in a row, keeping a fair profit. May use a partial close (strategy / EA only).', pickcfg.pick_streak(tf, 1)[0][0]),
           ('Shortest losing streak - indicator only', 'As above, without a partial close, so the indicator shows the same trades and results.',
            best([r for r in F if not r[0].get('p1')], lambda r: -r[1]['all']['maxL'])),
           ('Longest winning streak', 'The most wins in a row.', best(F, lambda r: r[1]['all']['maxW'])),
           ('Highest win rate', 'The largest share of profitable trades.', best(F, lambda r: round(r[1]['all']['win'], 4))),
           ('Most trades a day', 'The most trades while still profitable in both halves.', best(F, lambda r: r[1]['all']['n'])),
           ('Every year positive', 'Profitable in all 6 years (2021-2026), best score.', best([r for r in U if r[1]['ypos'] == 6], rb)),
           ('Simplest', 'The fewest settings to change.', best(U, lambda r: (-nchg(r[0]), round(rb(r), 6)), simple=False))]
    for name in SESS:
        q = [r for r in U if sessions(r[0]) == {name}]
        out.append(('%s session only' % name, 'Trades only in the %s session (Indian time); for traders who can only watch that session.' % name, best(q, rb)))
    return out, U
def stats(tr, cfg):
    """full statistics of one trade list (partial close already applied to R)"""
    d = dict(greedy.defaults()); d.update(cfg); n = len(tr)
    res = [x[1] for x in tr]; net = [x[1] - x[4] / x[5] for x in tr]
    A = [v for x, v in zip(tr, net) if x[0].year <= 2023]; B = [v for x, v in zip(tr, net) if x[0].year >= 2024]
    yrs = collections.defaultdict(list)
    for x, v in zip(tr, net): yrs[x[0].year].append((x[1], v))
    runs = []; cur = 0; sign = 0
    for r in res:
        s = 1 if r > 0 else -1 if r < 0 else 0
        if s != 0 and s == sign: cur += 1
        else:
            if sign != 0: runs.append((sign, cur))
            cur, sign = (1, s) if s != 0 else (0, 0)
    if sign != 0: runs.append((sign, cur))
    eq = pk = dd = 0.0
    for v in net: eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
    worstL = max((max([c for s, c in rr if s < 0] or [0]) for rr in [[(s, c) for s, c in _runs([a for a, _ in yrs[y]])] for y in yrs]), default=0)
    return dict(n=n, perday=n / 1485.0, win=sum(1 for x in tr if x[2]) / n, prof=sum(1 for r in res if r > 0) / n,
                tp=[sum(1 for x in tr if x[3][k]) / n for k in range(4)], be=sum(1 for x in tr if x[6]) / n,
                EA=sum(A) / len(A) if A else 0.0, EB=sum(B) / len(B) if B else 0.0, E=sum(net) / n, net=sum(net),
                years={y: sum(v for _, v in yrs[y]) for y in sorted(yrs)}, ypos=sum(1 for y in yrs if sum(v for _, v in yrs[y]) > 0),
                maxW=max([c for s, c in runs if s > 0] or [0]), maxL=max([c for s, c in runs if s < 0] or [0]), worstYearL=worstL,
                L5=sum(1 for s, c in runs if s < 0 and c >= 5), W5=sum(1 for s, c in runs if s > 0 and c >= 5), ddR=dd,
                tpR=(d['tp1R'], d['tp2R'], d['tp3R'], d['tp4R']), exitAt=d['exitAt'])
def _runs(seq):
    out = []; cur = 0; sign = 0
    for r in seq:
        s = 1 if r > 0 else -1 if r < 0 else 0
        if s != 0 and s == sign: cur += 1
        else:
            if sign != 0: out.append((sign, cur))
            cur, sign = (1, s) if s != 0 else (0, 0)
    if sign != 0: out.append((sign, cur))
    return out
def money(tr, cfg):
    """fixed $50 risk and the two Rule C split options on $10,000 (partial closes passed in parts)"""
    d = dict(greedy.defaults()); d.update(cfg); p = d['p1'] if d['exitAt'] > 1 else 0.0; t1 = d['tp1R']
    seq = [(x[1], x[4] / x[5], [(p * t1, p), (x[1] - p * t1, 1 - p)]) if (p and x[3][0]) else (x[1], x[4] / x[5]) for x in sorted(tr, key=lambda x: x[0])]
    return {'off': RC.simulate(seq, 'Off'), 'cs3_reset': RC.simulate(seq, 'Rule C split', cap=500.0, capAction='reset', cSplit=3),
            'cs3_clamp': RC.simulate(seq, 'Rule C split', cap=500.0, capAction='clamp', cSplit=3)}
if __name__ == '__main__':
    tfs = sys.argv[1:] or ['H1', 'M15', 'M5', 'M1']
    pool = mp.Pool(4)
    for tf in tfs:
        fn = S + '/gold/catalog_%s.pkl' % tf
        if os.path.exists(fn): print(tf, 'already done'); continue
        sc, U = scenarios(tf)
        picks = [(name, why, r[0]) for name, why, r in sc if r is not None]
        short = sorted(U, key=lambda r: -pickcfg.robust(r[1]))[:25]
        cfgs = []
        for c in [c for _, _, c in picks] + [r[0] for r in short]:
            if c not in cfgs: cfgs.append(c)
        runs = pool.map(final.full, [(tf, c) for c in cfgs]); T = {i: t for i, t in enumerate(runs)}
        ST = {i: stats(T[i], cfgs[i]) for i in T}
        smooth = max(range(len(cfgs)), key=lambda i: ST[i]['net'] / ST[i]['ddR'] if ST[i]['ddR'] > 0 else 0)
        picks.insert(7, ('Smoothest', 'The best profit for the deepest fall from a peak (total R / max drawdown in R), among the 25 strongest settings.', cfgs[smooth]))
        strat = []                                   # unique strategies, each with the scenarios it answers
        for name, why, c in picks:
            i = cfgs.index(c); hit = [s for s in strat if s['i'] == i]
            if hit: hit[0]['scen'].append((name, why))
            else: strat.append(dict(i=i, cfg=c, scen=[(name, why)], stats=ST[i], money=money(T[i], c), trades=T[i]))
        missing = [name for name, why, r in sc if r is None]
        pickle.dump(dict(strategies=strat, missing=missing, unique=[(c, m) for c, m in U]), open(fn, 'wb'))
        print(tf, 'strategies', len(strat), 'scenarios', len(picks), 'missing', missing, flush=True)
    pool.close()
