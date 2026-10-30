"""Fair odds for Crooks A / B: the same trades of each strategy replayed in 500 random orders (the trades do not win more often after
losses, so the backtest's order is one draw of many). Per rule: median and 5% worst net, median and 95% worst drawdown %, share of orders
that blow the $10,000 account or fall more than 40% from a peak, and where the real order ranks. Output: crooks_mc.pkl + crooks_mc.txt."""
import sys, pickle, random, multiprocessing as mp
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/gold')
import recovery as RC, crooks
NSH = 500
RULES = [('Off', 3, 0.0, 'clamp'), ('Rule C split', 3, 500.0, 'reset'),
         ('Crooks A', 3, 0.0, 'clamp'), ('Crooks A', 3, 500.0, 'clamp'), ('Crooks A', 3, 500.0, 'reset')] + \
        [('Crooks B', s, c, a) for s in (1, 2, 3, 4, 5) for c, a in ((0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset'))]
def q(v, f): v = sorted(v); return v[min(len(v) - 1, int(f * len(v)))]
def job(arg):
    tf, i = arg
    d = crooks.sources(tf)[i]; seq = crooks.sequence(d['trades'], d['cfg']); xr = crooks.exit_r(d['cfg'])
    trs = [(res, c, parts) for _, res, c, parts in seq]
    rng = random.Random(1000 + 7 * i + {'M1': 1, 'M5': 2, 'M15': 3, 'H1': 4}[tf]); orders = []
    for _ in range(NSH):
        t = list(trs); rng.shuffle(t); orders.append(t)
    out = {}
    for m, s, c, a in RULES:
        real = RC.simulate(trs, m, cap=c, capAction=a, cSplit=s, exitR=xr)
        sims = [RC.simulate(t, m, cap=c, capAction=a, cSplit=s, exitR=xr) for t in orders]
        nets = [x['net'] for x in sims]; dds = [x['maxDDpct'] for x in sims]
        out[(m, s, c, a)] = dict(real=real, med=q(nets, 0.5), p5=q(nets, 0.05), p95=q(nets, 0.95), ddMed=q(dds, 0.5), dd95=q(dds, 0.95),
                                 ruin=sum(1 for x in sims if x['ruined']) / NSH, dd40=sum(1 for x in dds if x > 0.40) / NSH,
                                 loss=sum(1 for x in nets if x <= 0) / NSH, rank=sum(1 for x in nets if x < real['net']) / NSH,
                                 riskMed=q([x['maxRisk'] for x in sims], 0.5))
    return tf, i, dict(name=d['name'], scen=d['scen'], exitR=xr, n=len(trs), rules=out)
if __name__ == '__main__':
    jobs = []
    for tf in crooks.TFS:
        for i, d in enumerate(crooks.sources(tf)):
            seq = crooks.sequence(d['trades'], d['cfg'])
            if sum(res - c for _, res, c, _ in seq) > 0: jobs.append((tf, i))      # strategies with an edge after spread
    with mp.Pool(4) as pool: res = pool.map(job, jobs)
    out = {(tf, i): d for tf, i, d in res}
    pickle.dump(out, open(S + '/gold/crooks_mc.pkl', 'wb'))
    L = []
    for (tf, i), d in sorted(out.items(), key=lambda kv: (crooks.TFS.index(kv[0][0]), kv[0][1])):
        L.append('\n%s | %s (%s) | exit R %.2f | %d trades | %d random orders' % (tf, d['name'], ', '.join(d['scen']), d['exitR'], d['n'], NSH))
        for k, r in d['rules'].items():
            x = dict(mode=k[0], split=k[1], cap=k[2], act=k[3])
            L.append('   %-38s | real %+8.0f (beats %3.0f%%) | median %+8.0f  5%% worst %+8.0f | DD median %3.0f%%  95%% worst %3.0f%% | blown %4.1f%%  DD>40%% %4.1f%%  losing %4.1f%%' % (
                crooks.label(x), r['real']['net'], 100 * r['rank'], r['med'], r['p5'], 100 * r['ddMed'], 100 * r['dd95'], 100 * r['ruin'], 100 * r['dd40'], 100 * r['loss']))
    open(S + '/gold/crooks_mc.txt', 'w').write('\n'.join(L) + '\n')
    print('done', len(out))
