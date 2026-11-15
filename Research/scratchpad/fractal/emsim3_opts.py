"""The strategy's TradingView orders with random options (M15 chart): trade counts, identical share, $ vs the model."""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import emsim3 as EM, pine_twin2 as TW
from multiprocessing import Pool
def job(seed):
    rng = np.random.default_rng(1000 + seed); k = int(rng.integers(9)) if rng.random() < 0.7 else 10
    kw = EM.random_opts(seed); nm, nt, same, mU, tU, net = EM.run(sys.argv[3] if len(sys.argv) > 3 else 'M15', k, TW.P(**kw))
    return seed, k, kw, nm, nt, same, mU, tU
if __name__ == '__main__':
    with Pool(4) as pool: res = pool.map(job, range(int(sys.argv[1]), int(sys.argv[2])))
    for seed, k, kw, nm, nt, same, mU, tU in res:
        print('seed %d S%d model %4d TradingView %4d identical %5.1f%% | $ model %+8.0f TradingView %+8.0f | %s' % (seed, k + 1, nm, nt, 100.0 * same / max(1, nm), mU, tU, {a: kw[a] for a in kw if a not in ('days', 'sess')}))
    nm = sum(r[3] for r in res); same = sum(r[5] for r in res)
    print('random options: %d runs, model trades %d, TradingView trades %d, identical %.1f%%' % (len(res), nm, sum(r[4] for r in res), 100.0 * same / max(1, nm)))
