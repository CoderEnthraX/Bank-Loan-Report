"""Loss-recovery rules (gold/recovery.py, the strategy / EA reference) on the 11 fractal strategies' gold trades (M1 execution).
Trade -> (gross R, cost in R, None, None, leverage limit 1:100, 0.01-lot risk); exitR = TP / SL; base $50, start $10,000.
Per strategy and mode: the real order + 200 shuffled orders (median net, ruin %, 95th percentile max drawdown %).
Output rec11.pkl + rec11.txt."""
import sys, pickle, random, numpy as np
from multiprocessing import Pool
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/fractal'); sys.path.insert(0, S + '/gold')
import engine as EN, recovery as RC
from final11 import ALL
COST = 0.23; LEV = 100.0
CAPS = [(0.0, 'clamp'), (500.0, 'clamp'), (500.0, 'reset')]
EXTRA = [('Crooks F', dict(fK=2.0)), ('Crooks F', dict(fK=5.0)), ('Crooks G', dict(gX=5.0)), ('Crooks G', dict(gX=20.0)), ('Crooks J', dict(jX=10.0)), ('Crooks J', dict(jX=40.0))] + \
        [(m, dict(lad=lv)) for m in ('Crooks F', 'Crooks J') for lv in ('Low', 'Medium', 'Max')]


def trades_of(p):
    B = EN.load(); tr = EN.run(B, 'M1', *p); sl = p[4]
    F = tr[:, 1]; X = tr[:, 3]; sd = F * sl / 100.0
    res = (X - F) / sd; c = COST / sd
    return [(float(a), float(b), None, None, LEV * float(d) * (1.0 + float(b)) / float(f), 1.0 * (float(d) + COST)) for a, b, d, f in zip(res, c, sd, F)]


def job(k):
    p = ALL[k]; trs = trades_of(p); xr = p[5] / p[4]
    rng = random.Random(77 + k); orders = []
    for _ in range(200):
        q = list(trs); rng.shuffle(q); orders.append(q)
    ways = [(m, {}) for m in RC.MODES] + EXTRA
    out = {}
    for m, kw in ways:
        for cap, act in CAPS:
            key = (m, tuple(sorted(kw.items())), cap, act)
            r = RC.simulate(trs, m, cap=cap, capAction=act, exitR=xr, **kw)
            sims = [RC.simulate(q, m, cap=cap, capAction=act, exitR=xr, **kw) for q in orders]
            out[key] = dict(net=r['net'], dd=r['maxDD'], ddp=r['maxDDpct'], pf=r['pf'], ruined=r['ruined'], maxRisk=r['maxRisk'], stop=r['capStopped'],
                            med=float(np.median([z['net'] for z in sims])), ruin=float(np.mean([z['ruined'] for z in sims])),
                            dd95=float(np.percentile([z['maxDDpct'] for z in sims], 95)), q05=float(np.percentile([z['net'] for z in sims], 5)))
    return k, out


if __name__ == '__main__':
    with Pool(4) as pool: res = dict(pool.map(job, range(len(ALL))))
    pickle.dump(res, open('rec11.pkl', 'wb'))
    keys = list(res[0].keys()); L = []
    for key in keys:
        m, kw, cap, act = key
        rows = [res[k][key] for k in range(len(ALL))]
        L.append('%-40s %-22s cap %4.0f %-5s | total net %+9.0f | sum med %+9.0f | worst 5%% %+8.0f | max DD%% avg %5.1f worst %5.1f | 95%% DD%% avg %5.1f | blown %d, shuffled ruin avg %4.1f%% | net by strategy %s' % (
            m[:40], ','.join('%s=%s' % x for x in kw)[:22], cap, act, sum(r['net'] for r in rows), sum(r['med'] for r in rows), sum(r['q05'] for r in rows),
            100 * np.mean([r['ddp'] for r in rows]), 100 * max(r['ddp'] for r in rows), 100 * np.mean([r['dd95'] for r in rows]), sum(r['ruined'] for r in rows),
            100 * np.mean([r['ruin'] for r in rows]), ' '.join('%+.0f' % r['net'] for r in rows)))
    open('rec11.txt', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
